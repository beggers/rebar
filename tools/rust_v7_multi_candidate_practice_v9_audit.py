#!/usr/bin/env python3
"""Replay one C Stage-21 public-practice experiment, never final performance.

This is practice evidence version 9 under ``performance/v7/evidence`` only.
It does not read, infer, open, or time any final benchmark or held-out case.
Every actual Stage-21 source, correctness gate, slot, and measured result must
be independently frozen before an exclusive evidence file can be written.
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
from tools import rust_v7_multi_candidate_practice_v4_audit as fourth
from tools import rust_v7_multi_candidate_practice_v5_audit as fifth
from tools import rust_v7_multi_candidate_practice_v6_audit as sixth
from tools import rust_v7_multi_candidate_practice_v7_audit as seventh
from tools import rust_v7_multi_candidate_practice_v8_audit as eighth


ROOT = original.ROOT
EVIDENCE = original.EVIDENCE
SCHEMA = "rebar-v7-multi-candidate-practice-integrity-v9"
PREFIX = "three-qualified-engines-public-practice-v9"
EXPECTED_EXCLUSIVE_SLOT = "three-qualified-engines-c-stage-21-singleton-split-memchr-v9"
RAW_PATH = EVIDENCE / f"{PREFIX}-raw.jsonl.gz"
SUMMARY_PATH = EVIDENCE / f"{PREFIX}-summary.json"
OUTPUT_PATH = EVIDENCE / f"{PREFIX}-integrity.json"

V1_AUDITOR_SHA256 = "bc093f114fe15833cab8f7c8d59bd1970345b6ddb47bc33349854be1af7f0ded"
V2_AUDITOR_SHA256 = "4dee19924cb0e4312ff9b62c70dd105f1f49aa4a7f3eeedaa650d9f9f5d853d4"
V3_AUDITOR_SHA256 = "1bd6a03a0d8e25b3041a31e095f97647f7d2e0b317e8ae3b8adf9b25113aefd4"
V4_AUDITOR_SHA256 = "6b6cb39cdab33e5b6ce2c88568925885514590f26f27c1990b24b598ac555dc0"
V5_AUDITOR_SHA256 = "7236508d80094d5c7a4fd3e33725b6e9485b73b7cdacd33b6a72d2ccc4cf6590"
V6_AUDITOR_SHA256 = "e8885263620f0a9c40dcb3f095dcc5ce1aa7741da57acb5a1b10749ea81acce9"
V7_AUDITOR_SHA256 = "31709b558736716bd95001ef07d613dbfe33e1e19fc9fc9a8da562ce98e2ce2e"
V8_AUDITOR_SHA256 = "e1d0dc1ddbbc9d47b98c8eb3fcf1b7cec10ee5d1c2960b163e3e62ee73ac50d7"
V1_INTEGRITY_SHA256 = "8739803b6cd020b8b4f663223435fd1e39ef5603e90195b2a268a9fa7fbc0340"
V2_INTEGRITY_SHA256 = "82ef917ca82ba124af6311f3bf10398a2a040286ed06430919bbdd26dd61e057"
V3_INTEGRITY_SHA256 = "aa1921230845a01aa03d607bd8609b3475dc659cacda5e6135d8b7064ed60c22"
V4_INTEGRITY_SHA256 = "7bfb360fa570510d585c923345f00162da92a3a7cd6379528ad981b1ec003174"
V5_INTEGRITY_SHA256 = "015a2f9e3ceebd3792c4de62828c2d63fbafd7a5f866c9513b60b964a974712e"
V6_INTEGRITY_SHA256 = "8804136b49d7203854bda098b4c224e1b62ae9ecc3d050e81378d1b9b9515134"
V7_INTEGRITY_SHA256 = "d7c51632e9e9419b1e309897eed0f60b1d0af5ffc1cecd66413874a8d487212d"
V8_INTEGRITY_SHA256 = "b2c9aa305abe0436c3566ed3ccf18b4947bff81b3dc3e898b2a1e1545ab10459"

HISTORICAL_V8_AUDIT_SHA256 = "55ab21dfa78193c96551f5d3d95a51251f30e535cdb37c24df3d2e6044166854"
HISTORICAL_V8_REGRESSIONS = 261
PREVIOUS_C_SOURCE_SHA256 = "696925d94c63fed442d547e9a0fbcce9dda271eae633130d01cdb4e68ea4af2f"
PREVIOUS_C_ENGINE_SHA256 = "0e4d194fc14a2e307dd765ec5632acbe7b4192a0b2a74833a1126fbd0e5b5b91"
UNCHANGED_RUST_SOURCE_SHA256 = "4b89d916e4c33e2b516be570ff3e75694f03dcea5eccf9320cedf07471b07dac"
UNCHANGED_RUST_ENGINE_SHA256 = "e7177c97070b2d0073a721044c4d23bb93e0d0883c1f2ccaa07c41eda8b96255"
UNCHANGED_RUST_BRIDGE_SOURCE_SHA256 = "83afb5a709a6d0ea1701dfd64db30644edbf2cb0276c2db731a8119cfd52d8ed"
UNCHANGED_RUST_BRIDGE_SHA256 = "1f072e81ba9339a8b2e52a7e93b7bcde791c4d518620b6bd760af67c7c89af34"
UNCHANGED_ZIG_BRIDGE_SOURCE_SHA256 = "92d4039e1db2e01757edfd4edf56006c4735c3bc64352b6ce9c5d1f69decafcf"
UNCHANGED_ZIG_BRIDGE_SHA256 = "80d7dab57cbee317ee1727862e27cd7dcf4cb22e1a944f4b29f2e4e983f940ed"
UNCHANGED_ZIG_ENGINE_SHA256 = "70bafca56a3f48477b2011f016a81b625e5f40a772af6a986d32b9098269f614"
HISTORICAL_C_CAMPAIGN_SHA256 = "c211d826032fed60c30024beb6de66c3e20b08fdcb936b53393d0a5fdba09721"
RUST_CAMPAIGN_SHA256 = "9ddbab81b16f0440ca19bffb8a539ea08d4a7ff33606ee3019eaf85977c2249a"
ZIG_CAMPAIGN_SHA256 = "4ba7cb9c45a70b747cc0a6eb721f6bb51081157f527d1bf5e578e603715ae5dc"
INITIAL_FAILURE_SHA256 = "ccaf3813b29badcf80c552dc0d850f83a2ca122cc3cc3057576dd519aed4f088"
ROLE_CONFUSION_INCIDENT_PATH = EVIDENCE / "ZIG-STAGE-13-VERIFIER-INCIDENTS.md"
ROLE_CONFUSION_INCIDENT_SHA256 = "84efcdbd0059ab430c84322695bf472f66fdc1cc05efd74e383b62114efcedff"
C_STAGE20_VERIFIER_INCIDENT_PATH = EVIDENCE / "C-STAGE-20-INDEPENDENCE-AUDIT-RETRY.md"
C_STAGE20_VERIFIER_INCIDENT_SHA256 = "0ee24eabfe369328c3dcd03c2dabab80f46a3851e82b6dbf4b390a72667149c4"
UNCHANGED_REFERENCE_CANDIDATES = [
    "re", "candidates.rust_candidate", "candidates.zig_candidate",
]

# Facts not yet produced by the independently approved Stage-21 experiment
# are deliberately None.  No verification, timing claim, or output is possible
# until the root supplies the actual complete correctness and practice facts.
V9_SLOT: str | None = "three-qualified-engines-c-stage-21-singleton-split-memchr-v9"
V9_AUDIT_SHA256: str | None = "a790fe1a75c8748df7f8bb6f1e39d0be841636055358aaee94db0aa35523f326"
V9_SUMMARY_SHA256: str | None = "e0140380d6b3026e6195f27d3188e87e6d646b08d0e632c5e9eda38674e616ed"
V9_COMPRESSED_RAW_SHA256: str | None = "004ef3e8ddb1bd81f88c6742843e3d5bc7c29ed4bfea120d40d3d28fdae4a651"
V9_RAW_SHA256: str | None = "493f3d8ec3c0a030891306b71353714e7165d60a5ec12e629fa0bfcfd5558200"
C_STAGE21_CAMPAIGN_PATH: Path | None = ROOT / "candidates/evidence/rust-v8-vm-stage-21-singleton-split-memchr-sealed-campaign.json"
C_STAGE21_CAMPAIGN_SHA256: str | None = "a29b540e01fc9f565e01e5cc62af14db30b38d9bacbaf55e4950e95b17c7ea40"
C_STAGE21_EDGE_PATH: Path | None = ROOT / "candidates/evidence/rust-v8-edge-oracle-vm-deep-stage-21-singleton-split-memchr.json.gz"
C_STAGE21_EDGE_COMPRESSED_SHA256: str | None = "a5214e9f0144b4549f8134d7df9bec21975f5debe9b6a392f47dd1097baec314"
C_STAGE21_EDGE_PAYLOAD_SHA256: str | None = "c843dccc2d0b8eb1dcada2af282679ca05a1be2de98afc39bad95e7f448f4d7a"
C_STAGE21_DEEP_PATH: Path | None = ROOT / "candidates/audits/RUST-V8-DEEP-CONTRACT-C-STAGE-21-SINGLETON-SPLIT-MEMCHR.json.gz"
C_STAGE21_DEEP_COMPRESSED_SHA256: str | None = "907d6c684cd5e7161ef27b167f1d3bdd18243dff61bad4d5586ff3ef5b2d13cd"
C_STAGE21_OBSERVABILITY_PATH: Path | None = ROOT / "candidates/evidence/rust-v8-observability-vm-qualified-stage-21-singleton-split-memchr.json.gz"
C_STAGE21_OBSERVABILITY_COMPRESSED_SHA256: str | None = "0a975f63d3a5e20e317e3dc08c1324ce95a8ed371923b53c18e65f49c6414b8a"
C_STAGE21_SOURCE_SHA256: str | None = "2253ddd8608a19a06f25ed41251729365ecb1e25f6829f710cdcb858b10c4e0c"
C_STAGE21_ENGINE_SHA256: str | None = "f6458cb4bf190f042e7d417a40020d2d58cebcb39671fda7352aab9725a7f633"
EXPECTED_REGRESSIONS: int | None = 256

AuditError = original.AuditError
require = original.require


def required_digest(value: str | None, label: str) -> str:
    require(
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value),
        f"the actual public-practice C Stage-21 {label} has not been frozen",
    )
    return value


def required_path(value: Path | None, label: str) -> Path:
    require(isinstance(value, Path), f"the actual public-practice C Stage-21 {label} path has not been frozen")
    path = value.resolve()
    require(path.is_relative_to(ROOT.resolve()), f"the public-practice {label} path escaped this project")
    return path


def required_slot(value: str | None) -> str:
    require(
        isinstance(value, str)
        and value == EXPECTED_EXCLUSIVE_SLOT
        and value != PREFIX
        and value not in {
            original.EXPECTED_SLOT, second.SLOT, third.SLOT,
            fourth.SLOT, fifth.SLOT, sixth.SLOT, seventh.V7_SLOT,
            eighth.V8_SLOT,
        },
        "the genuine unique C Stage-21 public-practice slot has not been frozen",
    )
    return value


def validate_preserved_incident(actual: str, expected: str, label: str) -> None:
    require(actual == expected, f"the genuine preserved {label} incident was concealed or changed")


def validate_version_identity(
    summary: dict, plan: dict, profile: original.Profile,
    raw_path: Path, expected_slot: str,
) -> None:
    original.validate_header(summary, plan, profile, None)
    require(summary.get("exclusive_slot") == expected_slot, "practice v9 substituted a historical or unauthorized slot")
    require(summary.get("raw_path") == str(raw_path.resolve()), "practice v9 substituted the recorded public raw path")
    require(
        summary.get("measurement")
        == "balanced practice diagnostic only; not a holdout result or final speed claim",
        "practice v9 was falsely represented as a final or held-out performance result",
    )


def validate_historical_continuity(
    v1: dict, v2: dict, v3: dict, v4: dict, v5: dict, v6: dict,
    v7: dict, v8: dict,
    sources: dict[str, str], native: dict[str, str], measured: dict[str, str],
    c_source_sha256: str, c_engine_sha256: str,
) -> None:
    require(v8.get("schema") == eighth.SCHEMA, "the immutable Rust capture-hoist practice experiment was replaced")
    require(v8.get("result") == "PASS" and v8.get("failed") == 0, "the immutable Rust capture-hoist practice did not pass")
    require(v8.get("holdout_accessed") is False and v8.get("timing_performed") is False, "historical v8 accessed or timed hidden final material")
    require(v8.get("module_order") == list(original.MODULES), "historical v8 changed independent candidate families")
    require(v8.get("cases_per_candidate") == original.EXPECTED_CASES, "historical v8 changed frozen public case weights")
    require(v8.get("trials_per_module_case") == original.EXPECTED_TRIALS, "historical v8 changed frozen paired trials")
    require(v8.get("bootstrap_draws") == original.EXPECTED_BOOTSTRAPS, "historical v8 changed frozen confidence draws")
    require(v8.get("frozen_plan_sha256") == original.EXPECTED_PLAN_SHA256, "historical v8 changed the immutable public-practice plan")
    require(v8.get("source_sha256") == V8_AUDITOR_SHA256, "the immutable Rust capture-hoist verifier changed")
    for key, expected in (
        ("historical_v1_integrity_sha256", V1_INTEGRITY_SHA256),
        ("historical_v2_integrity_sha256", V2_INTEGRITY_SHA256),
        ("historical_v3_integrity_sha256", V3_INTEGRITY_SHA256),
        ("historical_v4_integrity_sha256", V4_INTEGRITY_SHA256),
        ("historical_v5_integrity_sha256", V5_INTEGRITY_SHA256),
        ("historical_v6_integrity_sha256", V6_INTEGRITY_SHA256),
        ("historical_v7_integrity_sha256", V7_INTEGRITY_SHA256),
    ):
        require(v8.get(key) == expected, f"historical v8 substituted immutable public evidence: {key}")
    require(v8.get("from_scratch_audit_sha256") == HISTORICAL_V8_AUDIT_SHA256, "historical v8 changed its original source-bound audit")
    require(v8.get("strict_regressions") == HISTORICAL_V8_REGRESSIONS, "historical v8 concealed its actual 261 substantial losses")
    require(v8.get("full_correctness_campaign_sha256") == RUST_CAMPAIGN_SHA256, "historical v8 changed the full Rust capture-hoist campaign")
    require(v8.get("full_correctness_campaign_steps") == 22, "historical v8 omitted a Rust correctness stage")
    require(v8.get("c_full_correctness_campaign_sha256") == HISTORICAL_C_CAMPAIGN_SHA256, "historical v8 changed the previous C Stage-20 campaign")
    require(v8.get("c_full_correctness_campaign_steps") == 22, "historical v8 omitted a previous C correctness stage")
    require(v8.get("zig_full_correctness_campaign_sha256") == ZIG_CAMPAIGN_SHA256, "historical v8 changed the complete Zig Stage-13 campaign")
    require(v8.get("zig_full_correctness_campaign_steps") == 22, "historical v8 omitted a Zig correctness stage")
    require(v8.get("rust_deep_contract_sha256") == eighth.RUST_CAPTURE_DEEP_COMPRESSED_SHA256, "historical v8 changed its actual Rust deep proof")
    require(v8.get("rust_deep_contract_checks") == 393, "historical v8 omitted frozen Rust deep obligations")
    require(v8.get("rust_observability_sha256") == eighth.RUST_CAPTURE_OBSERVABILITY_COMPRESSED_SHA256, "historical v8 changed its actual Rust observability proof")
    require(v8.get("rust_observability_checks") == 479, "historical v8 omitted frozen Rust observability obligations")
    require(v8.get("rust_observability_binder_checks") == 34, "historical v8 omitted frozen Rust native-boundary obligations")
    require(v8.get("initial_audit_failure_sha256") == INITIAL_FAILURE_SHA256, "historical v8 concealed the genuine initial Rust failure")
    require(v8.get("role_confusion_incident_sha256") == ROLE_CONFUSION_INCIDENT_SHA256, "historical v8 concealed the genuine Zig verifier incident")
    require(v8.get("role_confusion_incident_path") == str(ROLE_CONFUSION_INCIDENT_PATH.resolve()), "historical v8 substituted the genuine Zig verifier incident path")
    require(v8.get("c_stage20_verifier_incident_sha256") == C_STAGE20_VERIFIER_INCIDENT_SHA256, "historical v8 concealed the genuine C independence-audit failure")
    require(v8.get("c_stage20_verifier_incident_path") == str(C_STAGE20_VERIFIER_INCIDENT_PATH.resolve()), "historical v8 substituted the genuine C failure-evidence path")
    historical_controls = v8.get("self_test")
    require(
        isinstance(historical_controls, dict)
        and historical_controls.get("result") == "PASS"
        and isinstance(historical_controls.get("poisoned_control_count"), int)
        and historical_controls["poisoned_control_count"] >= 233
        and historical_controls.get("role_confusion_incident_control_verified") is True
        and historical_controls.get("c_stage20_verifier_incident_control_verified") is True,
        "historical v8 concealed its 233 frozen family-isolation and incident controls",
    )
    for flag in (
        "rust_optimization_verified", "capacity16_optimization_verified",
        "mandatory_prefix_optimization_verified", "unchanged_rust_bridge_verified",
        "c_optimization_verified", "zig_optimization_verified",
        "zig_interned_attributes_optimization_verified",
        "rust_capture_initialization_optimization_verified",
    ):
        require(v8.get(flag) is True, f"historical v8 dropped a fully qualified optimization: {flag}")

    previous_sources = v8.get("qualified_source_fingerprints")
    previous_native = v8.get("native_elf_fingerprints")
    previous_measured = v8.get("candidate_binary_sha256_before")
    require(isinstance(previous_sources, dict), "historical v8 omitted qualified production sources")
    require(isinstance(previous_native, dict), "historical v8 omitted mapped native libraries")
    require(isinstance(previous_measured, dict), "historical v8 omitted timed native fingerprints")
    require(v8.get("candidate_binary_sha256_after") == previous_measured, "historical v8 changed an actual library while timing")
    eighth.validate_historical_continuity(
        v1, v2, v3, v4, v5, v6, v7,
        previous_sources, previous_native, previous_measured,
        UNCHANGED_RUST_SOURCE_SHA256, UNCHANGED_RUST_ENGINE_SHA256,
    )

    changed_source = "candidates/_vm_native.c"
    changed_native = "candidates.vm_candidate:native-engine"
    require(set(sources) == set(previous_sources), "the C-only experiment added or omitted a production source")
    require(set(native) == set(previous_native), "the C-only experiment added or omitted a mapped native library")
    require(set(measured) == set(previous_measured), "the C-only experiment added or omitted a timed artifact")
    for path, digest in previous_sources.items():
        if path != changed_source:
            require(sources.get(path) == digest, f"the C-only experiment changed another production source: {path}")
    for role, digest in previous_native.items():
        if role != changed_native:
            require(native.get(role) == digest, f"the C-only experiment changed another mapped native library: {role}")
    for role, digest in previous_measured.items():
        if role != changed_native:
            require(measured.get(role) == digest, f"the C-only experiment changed another timed candidate: {role}")
    require(previous_sources.get(changed_source) == PREVIOUS_C_SOURCE_SHA256, "historical v8 omitted the real Stage-20 C source")
    require(previous_native.get(changed_native) == PREVIOUS_C_ENGINE_SHA256, "historical v8 omitted the real Stage-20 C library")
    require(sources.get(changed_source) == c_source_sha256, "the C Stage-21 source differs from its full qualification")
    require(native.get(changed_native) == c_engine_sha256, "the C Stage-21 mapped library differs from its full qualification")
    require(measured.get(changed_native) == c_engine_sha256, "the measured C Stage-21 library differs from its actual mapping")
    require(c_source_sha256 != PREVIOUS_C_SOURCE_SHA256, "the claimed Stage-21 singleton splitter did not change its owned C source")
    require(c_engine_sha256 != PREVIOUS_C_ENGINE_SHA256, "the claimed Stage-21 singleton splitter did not change its mapped C library")
    require(sources.get("candidates/rust/src/lib.rs") == UNCHANGED_RUST_SOURCE_SHA256, "the C-only experiment changed the fully qualified Rust source")
    require(native.get("candidates.rust_candidate:native-engine") == UNCHANGED_RUST_ENGINE_SHA256, "the C-only experiment changed the fully qualified Rust engine")
    require(native.get("candidates.rust_candidate:native-bridge") == UNCHANGED_RUST_BRIDGE_SHA256, "the C-only experiment changed the Rust bridge")
    require(native.get("candidates.zig_candidate:native-bridge") == UNCHANGED_ZIG_BRIDGE_SHA256, "the C-only experiment changed the Zig bridge")
    require(native.get("candidates.zig_candidate:native-engine") == UNCHANGED_ZIG_ENGINE_SHA256, "the C-only experiment changed the Zig engine")


def validate_v9_edges(
    summary: dict, measured: dict[str, str], c_path: Path,
    c_compressed_sha256: str, c_payload_sha256: str,
) -> list[dict]:
    require(original.sha256_file(original.EDGE_SOURCE_PATH) == original.EXPECTED_EDGE_SOURCE_SHA256, "the frozen independent matching-oracle source changed")
    baseline, baseline_digest = original.read_edge(original.STDLIB_EDGE_PATH, "immutable pinned Python baseline matching evidence")
    original.validate_edge_document(baseline, "re")
    require(baseline_digest == original.EXPECTED_STDLIB_EDGE_SHA256, "the immutable Python matching baseline changed")
    require(original.sha256_file(c_path) == c_compressed_sha256, "the fresh Stage-21 C compressed matching evidence changed")
    rust_path = required_path(eighth.RUST_CAPTURE_EDGE_PATH, "preserved Rust capture-hoist edge proof")
    rust_compressed = required_digest(eighth.RUST_CAPTURE_EDGE_COMPRESSED_SHA256, "preserved compressed Rust capture-hoist edge proof")
    rust_payload = required_digest(eighth.RUST_CAPTURE_EDGE_PAYLOAD_SHA256, "preserved decompressed Rust capture-hoist edge proof")
    require(original.sha256_file(rust_path) == rust_compressed, "the preserved actual Rust capture-hoist edge changed")
    zig_path = required_path(seventh.ZIG13_EDGE_PATH, "preserved Zig Stage-13 edge proof")
    zig_compressed = required_digest(seventh.ZIG13_EDGE_COMPRESSED_SHA256, "preserved compressed Zig Stage-13 edge proof")
    zig_payload = required_digest(seventh.ZIG13_EDGE_PAYLOAD_SHA256, "preserved decompressed Zig Stage-13 edge proof")
    require(original.sha256_file(zig_path) == zig_compressed, "the preserved actual Zig Stage-13 edge changed")
    entries = summary.get("verified_edge_oracles")
    require(isinstance(entries, list) and len(entries) == len(original.MODULES) - 1, "public practice v9 omitted an independently qualified candidate")
    paths = {
        "candidates.rust_candidate": rust_path,
        "candidates.vm_candidate": c_path,
        "candidates.zig_candidate": zig_path,
    }
    for module, proof in zip(original.MODULES[1:], entries, strict=True):
        require(isinstance(proof, dict) and proof.get("module") == module, "public practice v9 reordered or cross-contaminated independent candidates")
        path = paths[module]
        require(proof.get("path") == str(path.resolve()), f"{module} substituted its source-bound matching-proof path")
        require(proof.get("correctness_checks") == 223_198, f"{module} dropped frozen Python matching cases")
        require(proof.get("actual_sha256") == original.EXPECTED_EDGE_ANSWER_SHA256, f"{module} failed exact frozen Python matching answers")
        require(proof.get("script_sha256") == original.EXPECTED_EDGE_SOURCE_SHA256, f"{module} substituted the immutable matching oracle")
        require(proof.get("stdlib_baseline_sha256") == baseline_digest, f"{module} changed the frozen stable Python baseline")
        report, payload_digest = original.read_edge(path, f"{module} fully qualified public practice-v9 matching proof")
        original.validate_edge_document(report, module)
        require(proof.get("report_sha256") == payload_digest, f"{module} substituted its decompressed matching evidence")
        if module == "candidates.rust_candidate":
            require(payload_digest == rust_payload, "the unchanged Rust edge does not certify the genuine capture-hoist engine")
        elif module == "candidates.vm_candidate":
            require(payload_digest == c_payload_sha256, "the fresh C edge does not certify the genuine Stage-21 library")
        else:
            require(payload_digest == zig_payload, "the unchanged Zig edge does not certify the genuine Stage-13 engine")
        artifacts = second.artifact_fingerprints(report.get("candidate_artifacts"), module)
        require(proof.get("candidate_artifacts") == artifacts, f"{module} timed artifacts differ from frozen matching evidence")
        for role, item in artifacts.items():
            if role == "public-python":
                key = f"{module}:module"
            elif module == "candidates.vm_candidate" and role == "native-bridge":
                key = f"{module}:native-engine"
            else:
                key = f"{module}:{role}"
            require(measured.get(key) == item["sha256"], f"{module} substituted its timed native engine, source, bridge, or family")
    return entries


def validate_c_artifacts(
    document: dict, sources: dict[str, str], measured: dict[str, str], label: str,
) -> dict[str, dict]:
    artifacts = second.artifact_fingerprints(
        document.get("native_artifacts"), "candidates.vm_candidate",
    )
    require(
        set(artifacts) == {"native-source", "native-bridge", "public-python"},
        f"{label} omitted or substituted the owned C production pipeline",
    )
    for role, item in artifacts.items():
        if role == "native-source":
            require(sources.get(item["path"]) == item["sha256"], f"{label} differs from its audited Stage-21 C source")
        elif role == "public-python":
            require(measured.get("candidates.vm_candidate:module") == item["sha256"], f"{label} substituted the public C wrapper")
        elif role == "native-bridge":
            require(measured.get("candidates.vm_candidate:native-engine") == item["sha256"], f"{label} substituted the actual mapped Stage-21 C engine")
    return artifacts


def validate_c_edge_reference(
    document: dict, edge_path: Path, edge_compressed_sha256: str, label: str,
) -> dict:
    edge = document.get("edge_oracle")
    require(isinstance(edge, dict), f"{label} omitted its frozen Python matching proof")
    require(edge.get("archive_sha256") == edge_compressed_sha256, f"{label} substituted the Stage-21 edge archive")
    require(edge.get("path") == str(edge_path.resolve()), f"{label} substituted the Stage-21 edge path")
    require(edge.get("module") == "candidates.vm_candidate", f"{label} bound another independent family")
    require(edge.get("checks") == 223_198 and edge.get("failed") == 0, f"{label} omitted or failed frozen matching checks")
    return edge


def validate_c_deep_contract(
    deep: dict, sources: dict[str, str], measured: dict[str, str],
    edge_path: Path, edge_compressed_sha256: str,
) -> dict[str, dict]:
    label = "fresh Stage-21 C 393-case public-contract proof"
    require(deep.get("schema") == "rebar-rust-v8-deep-public-contract-v1", f"{label} substituted the immutable contract schema")
    require(deep.get("status") == "PASS", f"{label} did not pass")
    require(deep.get("candidate_module") == "candidates.vm_candidate", f"{label} qualified another candidate")
    require(deep.get("checks") == 393, f"{label} changed the frozen public obligation count")
    require(deep.get("public_mismatch_count") == 0, f"{label} concealed a public behavioral mismatch")
    require(deep.get("stdlib_vs_stdlib_mismatches") == [], f"{label} concealed a Python self-oracle failure")
    require(deep.get("holdout") == "NOT ACCESSED", f"{label} accessed held-out benchmark material")
    require(deep.get("performance") == "NOT MEASURED", f"{label} performed performance timing")
    require(isinstance(deep.get("cross_engine_guard_count"), int) and deep["cross_engine_guard_count"] >= 10, f"{label} omitted cross-family delegation guards")
    validate_c_edge_reference(deep, edge_path, edge_compressed_sha256, label)
    return validate_c_artifacts(deep, sources, measured, label)


def validate_c_observability(
    observation: dict, sources: dict[str, str], measured: dict[str, str],
    edge_path: Path, edge_compressed_sha256: str,
    deep_path: Path, deep_compressed_sha256: str,
    deep_artifacts: dict[str, dict],
) -> None:
    label = "fresh Stage-21 C 479-case observability proof"
    require(observation.get("schema") == "rebar-v8-multi-candidate-observability-v1", f"{label} substituted its immutable schema")
    require(observation.get("status") == "PASS", f"{label} did not pass")
    require(observation.get("candidate_module") == "candidates.vm_candidate", f"{label} qualified another independent family")
    require(observation.get("checks") == 479 and observation.get("candidate_checks") == 479, f"{label} changed the frozen public obligation count")
    require(observation.get("failures") == [] and observation.get("candidate_failures") == 0, f"{label} concealed a frozen public observation failure")
    require(observation.get("private_binder_checks") == 34, f"{label} changed frozen native-boundary checks")
    require(observation.get("private_binder_failures") == [], f"{label} concealed a native-boundary failure")
    require(observation.get("holdout") == "NOT ACCESSED", f"{label} accessed a held-out benchmark")
    require(observation.get("performance") == "NOT MEASURED", f"{label} performed performance timing")
    validate_c_edge_reference(observation, edge_path, edge_compressed_sha256, label)
    deep_proof = observation.get("deep_proof")
    require(isinstance(deep_proof, dict), f"{label} omitted its frozen deep-contract chain")
    require(deep_proof.get("archive_sha256") == deep_compressed_sha256, f"{label} substituted its compressed deep evidence")
    require(deep_proof.get("path") == str(deep_path.resolve()), f"{label} substituted its deep-evidence path")
    require(deep_proof.get("candidate_module") == "candidates.vm_candidate", f"{label} bound another candidate's deep proof")
    require(deep_proof.get("checks") == 393 and deep_proof.get("status") == "PASS", f"{label} changed or failed frozen deep obligations")
    require(deep_proof.get("edge_archive_sha256") == edge_compressed_sha256, f"{label} substituted the matching proof in its deep chain")
    artifacts = validate_c_artifacts(observation, sources, measured, label)
    require(artifacts == deep_artifacts, f"{label} qualified a different C pipeline from its deep proof")


def validate_c_stage21_campaign(
    campaign: dict, sources: dict[str, str], measured: dict[str, str],
    edge_path: Path, edge_compressed_sha256: str,
    deep_artifacts: dict[str, dict],
) -> None:
    label = "complete Stage-21 C singleton-split 22-stage correctness campaign"
    require(campaign.get("schema") == "rebar-rust-campaign-gate-v1", f"{label} substituted its frozen campaign schema")
    require(campaign.get("candidate") == "candidates.vm_candidate", f"{label} qualified another independent family")
    require(campaign.get("passed") is True, f"{label} did not pass")
    require(campaign.get("holdout_accessed") is False, f"{label} accessed held-out cases")
    require(campaign.get("timing_performed") is False and campaign.get("performance") == "NOT MEASURED", f"{label} performed performance timing")
    require(campaign.get("required_correctness_step_count") == 22, f"{label} changed the immutable correctness denominator")
    stages = campaign.get("steps")
    require(isinstance(stages, list) and len(stages) == 22, f"{label} omitted a required correctness stage")
    require(all(isinstance(stage, dict) and stage.get("passed") is True for stage in stages), f"{label} concealed a mismatch, crash, or failed obligation")
    require(campaign.get("pinned_cpython") == "3.14.6", f"{label} changed the pinned Python correctness oracle")
    require(campaign.get("python_executable") == str(original.PINNED_PYTHON), f"{label} changed the frozen Python executable")
    require(campaign.get("mode") == "sealed-practice-only", f"{label} weakened practice-only campaign isolation")
    edge = validate_c_edge_reference(campaign, edge_path, edge_compressed_sha256, label)
    artifacts = validate_c_artifacts(campaign, sources, measured, label)
    production = second.artifact_fingerprints(edge.get("production_artifacts"), "candidates.vm_candidate")
    matching = second.artifact_fingerprints(edge.get("candidate_artifacts"), "candidates.vm_candidate")
    require(artifacts == production, f"{label} differs from its actual complete C production pipeline")
    for role, item in matching.items():
        require(artifacts.get(role) == item, f"{label} differs from its frozen C edge artifacts")
    require(artifacts == deep_artifacts, f"{label} differs from its frozen C deep and observability proofs")


def synthetic_histories() -> tuple[
    dict, dict, dict, dict, dict, dict, dict, dict,
    dict[str, str], dict[str, str], dict[str, str], str, str,
]:
    (
        v1, v2, v3, v4, v5, v6, v7, previous_sources,
        previous_native, previous_measured,
        _synthetic_rust_source, _synthetic_rust_engine,
    ) = eighth.synthetic_histories()
    rust_path = "candidates/rust/src/lib.rs"
    rust_role = "candidates.rust_candidate:native-engine"
    rust_source_role = "candidates.rust_candidate:native-source"
    previous_sources[rust_path] = UNCHANGED_RUST_SOURCE_SHA256
    previous_native[rust_role] = UNCHANGED_RUST_ENGINE_SHA256
    previous_measured[rust_role] = UNCHANGED_RUST_ENGINE_SHA256
    previous_measured[rust_source_role] = UNCHANGED_RUST_SOURCE_SHA256
    v8 = {
        "schema": eighth.SCHEMA, "result": "PASS", "failed": 0,
        "holdout_accessed": False, "timing_performed": False,
        "module_order": list(original.MODULES),
        "cases_per_candidate": original.EXPECTED_CASES,
        "trials_per_module_case": original.EXPECTED_TRIALS,
        "bootstrap_draws": original.EXPECTED_BOOTSTRAPS,
        "frozen_plan_sha256": original.EXPECTED_PLAN_SHA256,
        "source_sha256": V8_AUDITOR_SHA256,
        "historical_v1_integrity_sha256": V1_INTEGRITY_SHA256,
        "historical_v2_integrity_sha256": V2_INTEGRITY_SHA256,
        "historical_v3_integrity_sha256": V3_INTEGRITY_SHA256,
        "historical_v4_integrity_sha256": V4_INTEGRITY_SHA256,
        "historical_v5_integrity_sha256": V5_INTEGRITY_SHA256,
        "historical_v6_integrity_sha256": V6_INTEGRITY_SHA256,
        "historical_v7_integrity_sha256": V7_INTEGRITY_SHA256,
        "from_scratch_audit_sha256": HISTORICAL_V8_AUDIT_SHA256,
        "strict_regressions": HISTORICAL_V8_REGRESSIONS,
        "full_correctness_campaign_sha256": RUST_CAMPAIGN_SHA256,
        "full_correctness_campaign_steps": 22,
        "c_full_correctness_campaign_sha256": HISTORICAL_C_CAMPAIGN_SHA256,
        "c_full_correctness_campaign_steps": 22,
        "zig_full_correctness_campaign_sha256": ZIG_CAMPAIGN_SHA256,
        "zig_full_correctness_campaign_steps": 22,
        "rust_deep_contract_sha256": eighth.RUST_CAPTURE_DEEP_COMPRESSED_SHA256,
        "rust_deep_contract_checks": 393,
        "rust_observability_sha256": eighth.RUST_CAPTURE_OBSERVABILITY_COMPRESSED_SHA256,
        "rust_observability_checks": 479,
        "rust_observability_binder_checks": 34,
        "initial_audit_failure_sha256": INITIAL_FAILURE_SHA256,
        "role_confusion_incident_sha256": ROLE_CONFUSION_INCIDENT_SHA256,
        "role_confusion_incident_path": str(ROLE_CONFUSION_INCIDENT_PATH.resolve()),
        "c_stage20_verifier_incident_sha256": C_STAGE20_VERIFIER_INCIDENT_SHA256,
        "c_stage20_verifier_incident_path": str(C_STAGE20_VERIFIER_INCIDENT_PATH.resolve()),
        "self_test": {
            "result": "PASS", "poisoned_control_count": 233,
            "role_confusion_incident_control_verified": True,
            "c_stage20_verifier_incident_control_verified": True,
        },
        "rust_optimization_verified": True,
        "capacity16_optimization_verified": True,
        "mandatory_prefix_optimization_verified": True,
        "unchanged_rust_bridge_verified": True,
        "c_optimization_verified": True,
        "zig_optimization_verified": True,
        "zig_interned_attributes_optimization_verified": True,
        "rust_capture_initialization_optimization_verified": True,
        "qualified_source_fingerprints": dict(previous_sources),
        "native_elf_fingerprints": dict(previous_native),
        "candidate_binary_sha256_before": dict(previous_measured),
        "candidate_binary_sha256_after": dict(previous_measured),
    }
    c_path = "candidates/_vm_native.c"
    c_role = "candidates.vm_candidate:native-engine"
    synthetic_c_source = hashlib.sha256(b"synthetic-c-stage21-singleton-split-memchr-source").hexdigest()
    synthetic_c_engine = hashlib.sha256(b"synthetic-c-stage21-singleton-split-memchr-engine").hexdigest()
    sources = {**previous_sources, c_path: synthetic_c_source}
    native = {**previous_native, c_role: synthetic_c_engine}
    measured = {**previous_measured, c_role: synthetic_c_engine}
    return (
        v1, v2, v3, v4, v5, v6, v7, v8,
        sources, native, measured, synthetic_c_source, synthetic_c_engine,
    )


def self_test() -> dict:
    inherited = eighth.self_test()
    require(inherited.get("result") == "PASS", "the immutable Rust capture-hoist candidate-free replay failed")
    previous = inherited.get("poisoned_controls")
    require(isinstance(previous, list) and len(previous) >= 233, "practice v9 omitted its 233 inherited frozen corruption controls")
    plan, sample, _payload, profile = original.synthetic_evidence()
    sample_slot = "synthetic-c-stage21-singleton-split-memchr-candidate-free-practice-v9"
    sample["exclusive_slot"] = sample_slot
    sample["raw_path"] = str(RAW_PATH.resolve())
    sample["measurement"] = "balanced practice diagnostic only; not a holdout result or final speed claim"
    validate_version_identity(sample, plan, profile, RAW_PATH, sample_slot)
    (
        v1, v2, v3, v4, v5, v6, v7, v8,
        sources, native, measured, source_digest, engine_digest,
    ) = synthetic_histories()
    validate_historical_continuity(
        v1, v2, v3, v4, v5, v6, v7, v8,
        sources, native, measured, source_digest, engine_digest,
    )
    controls = [*previous]

    def reject(name: str, action: object) -> None:
        try:
            action()  # type: ignore[operator]
        except (AuditError, KeyError, ValueError, TypeError, OverflowError):
            controls.append({"name": name, "passed": True})
            return
        raise AuditError(f"practice-v9 C Stage-21 synthetic controls accepted corruption: {name}")

    def poison_version(key: str, value: object) -> None:
        document = copy.deepcopy(sample)
        document[key] = value
        validate_version_identity(document, plan, profile, RAW_PATH, sample_slot)

    def poison_history(which: str, key: str, value: object) -> None:
        first, second_doc, third_doc, fourth_doc = (
            copy.deepcopy(v1), copy.deepcopy(v2),
            copy.deepcopy(v3), copy.deepcopy(v4),
        )
        fifth_doc, sixth_doc, seventh_doc, eighth_doc = (
            copy.deepcopy(v5), copy.deepcopy(v6),
            copy.deepcopy(v7), copy.deepcopy(v8),
        )
        current_sources, current_native, current_measured = (
            dict(sources), dict(native), dict(measured),
        )
        groups = {
            "v1": first, "v2": second_doc, "v3": third_doc,
            "v4": fourth_doc, "v5": fifth_doc, "v6": sixth_doc,
            "v7": seventh_doc, "v8": eighth_doc,
            "v8-sources": eighth_doc["qualified_source_fingerprints"],
            "v8-native": eighth_doc["native_elf_fingerprints"],
            "v8-measured": eighth_doc["candidate_binary_sha256_before"],
            "sources": current_sources, "native": current_native,
            "measured": current_measured,
        }
        groups[which][key] = value
        validate_historical_continuity(
            first, second_doc, third_doc, fourth_doc, fifth_doc,
            sixth_doc, seventh_doc, eighth_doc,
            current_sources, current_native, current_measured,
            source_digest, engine_digest,
        )

    for label, slot in (
        ("v1-slot-contamination", original.EXPECTED_SLOT),
        ("v2-slot-contamination", second.SLOT),
        ("v3-slot-contamination", third.SLOT),
        ("v4-slot-contamination", fourth.SLOT),
        ("v5-slot-contamination", fifth.SLOT),
        ("v6-slot-contamination", sixth.SLOT),
        ("v7-slot-contamination", seventh.V7_SLOT),
        ("v8-slot-contamination", eighth.V8_SLOT),
        ("v9-practice-filename-incorrectly-treated-as-slot", PREFIX),
    ):
        reject(label, lambda value=slot: poison_version("exclusive_slot", value))
    for label, path in (
        ("v1-raw-contamination", original.RAW_PATH),
        ("v2-raw-contamination", second.RAW_PATH),
        ("v3-raw-contamination", third.RAW_PATH),
        ("v4-raw-contamination", fourth.RAW_PATH),
        ("v5-raw-contamination", fifth.RAW_PATH),
        ("v6-raw-contamination", sixth.RAW_PATH),
        ("v7-raw-contamination", seventh.RAW_PATH),
        ("v8-raw-contamination", eighth.RAW_PATH),
    ):
        reject(label, lambda value=path: poison_version("raw_path", str(value.resolve())))
    reject("practice-v9-falsely-claimed-final", lambda: poison_version("measurement", "final held-out performance-v9 benchmark"))
    for label, historical in (
        ("v1-history-substitution", "v1"),
        ("v2-history-substitution", "v2"),
        ("v3-history-substitution", "v3"),
        ("v4-history-substitution", "v4"),
        ("v5-history-substitution", "v5"),
        ("v6-history-substitution", "v6"),
        ("v7-history-substitution", "v7"),
        ("v8-history-substitution", "v8"),
    ):
        reject(label, lambda value=historical: poison_history(value, "schema", SCHEMA))
    reject("historical-v8-261-losses-concealed", lambda: poison_history("v8", "strict_regressions", HISTORICAL_V8_REGRESSIONS - 1))
    reject("preserved-rust-capture-full-campaign-substituted", lambda: poison_history("v8", "full_correctness_campaign_sha256", "0" * 64))
    reject("historical-c20-full-campaign-substituted", lambda: poison_history("v8", "c_full_correctness_campaign_sha256", "0" * 64))
    reject("preserved-zig13-full-campaign-substituted", lambda: poison_history("v8", "zig_full_correctness_campaign_sha256", "0" * 64))
    reject("historical-rust-deep-proof-substituted", lambda: poison_history("v8", "rust_deep_contract_sha256", "0" * 64))
    reject("historical-rust-observability-substituted", lambda: poison_history("v8", "rust_observability_sha256", "0" * 64))
    reject("genuine-initial-rust-failure-concealed", lambda: poison_history("v8", "initial_audit_failure_sha256", "0" * 64))
    reject("historical-zig-verifier-incident-concealed", lambda: poison_history("v8", "role_confusion_incident_sha256", "0" * 64))
    reject("historical-c20-verifier-incident-concealed", lambda: poison_history("v8", "c_stage20_verifier_incident_sha256", "0" * 64))
    reject(
        "historical-233-corruption-controls-concealed",
        lambda: poison_history("v8", "self_test", {
            "result": "PASS", "poisoned_control_count": 232,
            "role_confusion_incident_control_verified": True,
            "c_stage20_verifier_incident_control_verified": True,
        }),
    )
    reject("historical-c20-source-replaced", lambda: poison_history("v8-sources", "candidates/_vm_native.c", source_digest))
    reject("historical-c20-mapped-engine-replaced", lambda: poison_history("v8-native", "candidates.vm_candidate:native-engine", engine_digest))
    reject("stage21-c-source-not-new", lambda: poison_history("sources", "candidates/_vm_native.c", PREVIOUS_C_SOURCE_SHA256))
    reject("stage21-c-engine-not-new", lambda: poison_history("native", "candidates.vm_candidate:native-engine", PREVIOUS_C_ENGINE_SHA256))
    reject("stage21-c-timed-engine-substituted", lambda: poison_history("measured", "candidates.vm_candidate:native-engine", "0" * 64))
    reject("unchanged-rust-capture-source-substituted", lambda: poison_history("sources", "candidates/rust/src/lib.rs", "0" * 64))
    reject("unchanged-rust-capture-engine-substituted", lambda: poison_history("native", "candidates.rust_candidate:native-engine", "0" * 64))
    reject("unchanged-rust-bridge-source-substituted", lambda: poison_history("sources", "candidates/rust/py_bridge.c", "0" * 64))
    reject("unchanged-rust-bridge-substituted", lambda: poison_history("native", "candidates.rust_candidate:native-bridge", "0" * 64))
    reject("unchanged-zig13-bridge-source-substituted", lambda: poison_history("sources", "candidates/zig/py_bridge.c", "0" * 64))
    reject("unchanged-zig13-bridge-substituted", lambda: poison_history("native", "candidates.zig_candidate:native-bridge", "0" * 64))
    reject("unchanged-zig13-engine-substituted", lambda: poison_history("native", "candidates.zig_candidate:native-engine", "0" * 64))
    reject("unchanged-python-baseline-substituted", lambda: poison_history("measured", "re:module", "0" * 64))
    for label, synthetic_value in (
        ("preserved-c-stage20-incident-concealed", b"synthetic-public-v9-honest-c-stage20-incident"),
        ("preserved-zig-stage13-incident-concealed", b"synthetic-public-v9-honest-zig-stage13-incident"),
    ):
        digest = hashlib.sha256(synthetic_value).hexdigest()
        validate_preserved_incident(digest, digest, label)
        reject(
            label,
            lambda expected=digest, name=label: validate_preserved_incident(
                "0" * 64, expected, name,
            ),
        )
    require(len(controls) >= 275, "practice v9 omitted frozen history, unchanged-family, no-final, or incident-isolation controls")
    return {
        "schema": SCHEMA + "-self-test", "result": "PASS",
        "synthetic_only": True, "holdout_accessed": False,
        "timing_performed": False,
        "historical_v1_auditor_sha256": V1_AUDITOR_SHA256,
        "historical_v2_auditor_sha256": V2_AUDITOR_SHA256,
        "historical_v3_auditor_sha256": V3_AUDITOR_SHA256,
        "historical_v4_auditor_sha256": V4_AUDITOR_SHA256,
        "historical_v5_auditor_sha256": V5_AUDITOR_SHA256,
        "historical_v6_auditor_sha256": V6_AUDITOR_SHA256,
        "historical_v7_auditor_sha256": V7_AUDITOR_SHA256,
        "historical_v8_auditor_sha256": V8_AUDITOR_SHA256,
        "inherited_poisoned_control_count": len(previous),
        "poisoned_control_count": len(controls),
        "poisoned_controls": controls,
        "role_confusion_incident_control_verified": True,
        "c_stage20_verifier_incident_control_verified": True,
        "final_holdout_isolation_control_verified": True,
        "unchanged_reference_candidates": list(UNCHANGED_REFERENCE_CANDIDATES),
        "failed": 0,
    }


def verify(raw_path: Path, summary_path: Path, audit_path: Path, output_path: Path) -> dict:
    slot = required_slot(V9_SLOT)
    audit_digest = required_digest(V9_AUDIT_SHA256, "canonical five-library independence audit")
    summary_digest = required_digest(V9_SUMMARY_SHA256, "single authorized public-practice summary")
    compressed_digest = required_digest(V9_COMPRESSED_RAW_SHA256, "compressed public-practice raw observations")
    raw_digest = required_digest(V9_RAW_SHA256, "decompressed public-practice raw observations")
    campaign_path = required_path(C_STAGE21_CAMPAIGN_PATH, "complete 22-stage C Stage-21 correctness campaign")
    campaign_digest = required_digest(C_STAGE21_CAMPAIGN_SHA256, "complete 22-stage C Stage-21 correctness campaign")
    edge_path = required_path(C_STAGE21_EDGE_PATH, "fresh C Stage-21 frozen matching proof")
    edge_digest = required_digest(C_STAGE21_EDGE_COMPRESSED_SHA256, "fresh compressed C Stage-21 matching proof")
    edge_payload = required_digest(C_STAGE21_EDGE_PAYLOAD_SHA256, "fresh decompressed C Stage-21 matching proof")
    deep_path = required_path(C_STAGE21_DEEP_PATH, "fresh C Stage-21 393-case deep proof")
    deep_digest = required_digest(C_STAGE21_DEEP_COMPRESSED_SHA256, "fresh compressed C Stage-21 deep proof")
    observability_path = required_path(C_STAGE21_OBSERVABILITY_PATH, "fresh C Stage-21 479-case observability proof")
    observability_digest = required_digest(C_STAGE21_OBSERVABILITY_COMPRESSED_SHA256, "fresh compressed C Stage-21 observability proof")
    source_digest = required_digest(C_STAGE21_SOURCE_SHA256, "fresh owned C Stage-21 production source")
    engine_digest = required_digest(C_STAGE21_ENGINE_SHA256, "fresh mapped C Stage-21 native engine")
    losses = EXPECTED_REGRESSIONS
    require(isinstance(losses, int) and not isinstance(losses, bool) and losses >= 0, "the actual practice-v9 one-shot slowdown count has not been frozen")
    require(platform.python_implementation() == "CPython" and tuple(sys.version_info[:3]) == (3, 14, 6), "practice v9 requires frozen stable CPython 3.14.6")
    require(Path(sys.executable).resolve() == original.PINNED_PYTHON.resolve(), "practice v9 requires its exact frozen Python executable")
    require(raw_path.resolve() == RAW_PATH.resolve(), "practice v9 may not substitute frozen historical observations")
    require(summary_path.resolve() == SUMMARY_PATH.resolve(), "practice v9 may not substitute frozen historical summaries")
    require(audit_path.resolve() == original.AUDIT_PATH.resolve(), "practice v9 may not replace the canonical from-scratch audit")
    require(output_path.resolve() == OUTPUT_PATH.resolve(), "practice v9 may not redirect or overwrite prior integrity evidence")
    require(not output_path.exists(), "the unique practice-v9 integrity result already exists")
    require(not any(name in sys.modules for name in original.MODULES[1:]), "the practice-v9 independent verifier imported a candidate")
    validate_preserved_incident(
        original.sha256_file(ROLE_CONFUSION_INCIDENT_PATH),
        ROLE_CONFUSION_INCIDENT_SHA256, "Zig Stage-13 role confusion",
    )
    validate_preserved_incident(
        original.sha256_file(C_STAGE20_VERIFIER_INCIDENT_PATH),
        C_STAGE20_VERIFIER_INCIDENT_SHA256, "C Stage-20 independence-audit retry",
    )
    for module, expected in (
        (original, V1_AUDITOR_SHA256), (second, V2_AUDITOR_SHA256),
        (third, V3_AUDITOR_SHA256), (fourth, V4_AUDITOR_SHA256),
        (fifth, V5_AUDITOR_SHA256), (sixth, V6_AUDITOR_SHA256),
        (seventh, V7_AUDITOR_SHA256), (eighth, V8_AUDITOR_SHA256),
    ):
        require(original.sha256_file(Path(module.__file__).resolve()) == expected, "an immutable public-practice history verifier changed")
    require(original.sha256_file(third.INITIAL_FAILURE_PATH) == INITIAL_FAILURE_SHA256, "the real preserved first Rust audit failure was removed or rewritten")

    profile = original.Profile()
    plan = original.read_json(original.PLAN_PATH, "immutable 624-case public-practice plan", original.EXPECTED_PLAN_SHA256)
    require(plan.get("expected_sha256") == original.EXPECTED_FROZEN_ANSWER_SHA256, "practice v9 changed frozen Python baseline answers")
    original.validate_plan(plan, profile)
    summary = original.read_json(summary_path, "sole actual practice-v9 Stage-21 public summary", summary_digest)
    validate_version_identity(summary, plan, profile, raw_path, slot)
    require(summary.get("compressed_raw_sha256") == compressed_digest, "practice v9 changed compressed observed data")
    require(summary.get("raw_sha256") == raw_digest, "practice v9 changed decompressed observed data")
    require(original.sha256_file(raw_path) == compressed_digest, "practice v9 substituted the public gzip file")

    audit = original.read_json(audit_path, "actual C Stage-21 source-bound native provenance audit", audit_digest)
    sources, native = original.validate_independence(audit)
    measured = original.validate_measured_fingerprints(summary, sources, native)
    v1 = original.read_json(original.OUTPUT_PATH, "frozen v1 public-practice integrity", V1_INTEGRITY_SHA256)
    v2 = original.read_json(second.OUTPUT_PATH, "frozen v2 public-practice integrity", V2_INTEGRITY_SHA256)
    v3 = original.read_json(third.OUTPUT_PATH, "frozen v3 public-practice integrity", V3_INTEGRITY_SHA256)
    v4 = original.read_json(fourth.OUTPUT_PATH, "frozen v4 public-practice integrity", V4_INTEGRITY_SHA256)
    v5 = original.read_json(fifth.OUTPUT_PATH, "frozen v5 public-practice integrity", V5_INTEGRITY_SHA256)
    v6 = original.read_json(sixth.OUTPUT_PATH, "frozen v6 public-practice integrity", V6_INTEGRITY_SHA256)
    v7 = original.read_json(seventh.OUTPUT_PATH, "frozen v7 public-practice integrity", V7_INTEGRITY_SHA256)
    v8 = original.read_json(eighth.OUTPUT_PATH, "frozen v8 public-practice integrity", V8_INTEGRITY_SHA256)
    validate_historical_continuity(
        v1, v2, v3, v4, v5, v6, v7, v8,
        sources, native, measured, source_digest, engine_digest,
    )
    edge_proofs = validate_v9_edges(summary, measured, edge_path, edge_digest, edge_payload)

    deep = eighth.read_compressed_json(deep_path, deep_digest, "fresh Stage-21 C 393-case public deep proof")
    deep_artifacts = validate_c_deep_contract(
        deep, sources, measured, edge_path, edge_digest,
    )
    observation = eighth.read_compressed_json(
        observability_path, observability_digest,
        "fresh Stage-21 C 479-case public observability proof",
    )
    validate_c_observability(
        observation, sources, measured, edge_path, edge_digest,
        deep_path, deep_digest, deep_artifacts,
    )
    campaign = original.read_json(campaign_path, "actual full 22-stage C singleton-split correctness campaign", campaign_digest)
    validate_c_stage21_campaign(
        campaign, sources, measured, edge_path, edge_digest, deep_artifacts,
    )
    rust_campaign_path = required_path(eighth.RUST_CAPTURE_CAMPAIGN_PATH, "unchanged Rust capture-hoist complete campaign")
    rust_campaign = original.read_json(rust_campaign_path, "preserved complete 22-stage Rust capture-hoist campaign", RUST_CAMPAIGN_SHA256)
    rust_edge_path = required_path(eighth.RUST_CAPTURE_EDGE_PATH, "unchanged Rust capture-hoist edge")
    rust_edge_digest = required_digest(eighth.RUST_CAPTURE_EDGE_COMPRESSED_SHA256, "unchanged Rust capture-hoist compressed edge")
    rust_deep_path = required_path(eighth.RUST_CAPTURE_DEEP_PATH, "unchanged Rust capture-hoist deep proof")
    rust_deep_digest = required_digest(eighth.RUST_CAPTURE_DEEP_COMPRESSED_SHA256, "unchanged Rust capture-hoist compressed deep proof")
    rust_deep = eighth.read_compressed_json(rust_deep_path, rust_deep_digest, "preserved 393-case Rust capture-hoist proof")
    rust_artifacts = eighth.validate_rust_deep_contract(
        rust_deep, sources, measured, rust_edge_path, rust_edge_digest,
    )
    eighth.validate_rust_capture_campaign(
        rust_campaign, sources, measured,
        rust_edge_path, rust_edge_digest, rust_artifacts,
    )
    zig_campaign_path = required_path(seventh.ZIG13_CAMPAIGN_PATH, "unchanged full Zig Stage-13 campaign")
    zig_campaign = original.read_json(zig_campaign_path, "preserved complete 22-stage Zig Stage-13 campaign", ZIG_CAMPAIGN_SHA256)
    zig_edge_path = required_path(seventh.ZIG13_EDGE_PATH, "unchanged Zig Stage-13 edge")
    zig_edge_digest = required_digest(seventh.ZIG13_EDGE_COMPRESSED_SHA256, "unchanged Zig Stage-13 compressed edge")
    seventh.validate_zig_campaign(zig_campaign, sources, measured, zig_edge_path, zig_edge_digest)

    try:
        with raw_path.open("rb") as source:
            observations = original.read_observations(
                source, compressed_digest, summary, plan, profile,
            )
    except OSError as error:
        raise AuditError("cannot read the complete practice-v9 public raw observations") from error
    results, rankings = original.recompute_results(plan, observations, profile)
    regressions = original.validate_results(summary, results, rankings, profile)
    require(len(regressions) == losses, "practice v9 concealed or altered its actual substantial public slowdowns")
    controls = self_test()
    require(not any(name in sys.modules for name in original.MODULES[1:]), "the practice-v9 replay imported a production candidate")

    document = {
        "schema": SCHEMA, "result": "PASS", "holdout_accessed": False,
        "timing_performed": False,
        "measurement": "independent replay of one Stage-21 C four-way public practice run; not final or held-out performance",
        "exclusive_slot": slot,
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
        "summary_sha256": summary_digest,
        "compressed_raw_sha256": compressed_digest,
        "raw_sha256": raw_digest,
        "frozen_plan_sha256": original.EXPECTED_PLAN_SHA256,
        "source_sha256": original.sha256_file(Path(__file__).resolve()),
        "historical_v1_auditor_sha256": V1_AUDITOR_SHA256,
        "historical_v2_auditor_sha256": V2_AUDITOR_SHA256,
        "historical_v3_auditor_sha256": V3_AUDITOR_SHA256,
        "historical_v4_auditor_sha256": V4_AUDITOR_SHA256,
        "historical_v5_auditor_sha256": V5_AUDITOR_SHA256,
        "historical_v6_auditor_sha256": V6_AUDITOR_SHA256,
        "historical_v7_auditor_sha256": V7_AUDITOR_SHA256,
        "historical_v8_auditor_sha256": V8_AUDITOR_SHA256,
        "historical_v1_integrity_sha256": V1_INTEGRITY_SHA256,
        "historical_v2_integrity_sha256": V2_INTEGRITY_SHA256,
        "historical_v3_integrity_sha256": V3_INTEGRITY_SHA256,
        "historical_v4_integrity_sha256": V4_INTEGRITY_SHA256,
        "historical_v5_integrity_sha256": V5_INTEGRITY_SHA256,
        "historical_v6_integrity_sha256": V6_INTEGRITY_SHA256,
        "historical_v7_integrity_sha256": V7_INTEGRITY_SHA256,
        "historical_v8_integrity_sha256": V8_INTEGRITY_SHA256,
        "from_scratch_audit_sha256": audit_digest,
        "from_scratch_control_count": 76,
        "verified_independent_engine_count": len(original.MODULES) - 1,
        "verified_native_library_count": len(native),
        "full_correctness_campaign_sha256": campaign_digest,
        "full_correctness_campaign_steps": 22,
        "rust_full_correctness_campaign_sha256": RUST_CAMPAIGN_SHA256,
        "rust_full_correctness_campaign_steps": 22,
        "zig_full_correctness_campaign_sha256": ZIG_CAMPAIGN_SHA256,
        "zig_full_correctness_campaign_steps": 22,
        "c_deep_contract_sha256": deep_digest,
        "c_deep_contract_checks": 393,
        "c_observability_sha256": observability_digest,
        "c_observability_checks": 479,
        "c_observability_binder_checks": 34,
        "initial_audit_failure_sha256": INITIAL_FAILURE_SHA256,
        "role_confusion_incident_sha256": ROLE_CONFUSION_INCIDENT_SHA256,
        "role_confusion_incident_path": str(ROLE_CONFUSION_INCIDENT_PATH.resolve()),
        "c_stage20_verifier_incident_sha256": C_STAGE20_VERIFIER_INCIDENT_SHA256,
        "c_stage20_verifier_incident_path": str(C_STAGE20_VERIFIER_INCIDENT_PATH.resolve()),
        "rust_optimization_verified": True,
        "capacity16_optimization_verified": True,
        "mandatory_prefix_optimization_verified": True,
        "unchanged_rust_bridge_verified": True,
        "c_optimization_verified": True,
        "zig_optimization_verified": True,
        "zig_interned_attributes_optimization_verified": True,
        "rust_capture_initialization_optimization_verified": True,
        "c_singleton_split_memchr_optimization_verified": True,
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
        json.dumps(document, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
        + "\n"
    ).encode("ascii")
    try:
        with output_path.open("xb") as destination:
            destination.write(encoded)
            destination.flush()
            os.fsync(destination.fileno())
    except FileExistsError as error:
        raise AuditError("the exclusive public-practice v9 integrity output already exists") from error
    except OSError as error:
        raise AuditError("cannot persist the exclusive public-practice v9 integrity output") from error
    return {
        "schema": SCHEMA, "result": "PASS", "holdout_accessed": False,
        "timing_performed": False,
        "cases_per_candidate": original.EXPECTED_CASES,
        "candidate_case_count": len(results),
        "trials_per_module_case": original.EXPECTED_TRIALS,
        "raw_rows": len(observations),
        "correctness_checks": original.EXPECTED_CORRECTNESS_CHECKS,
        "bootstrap_draws": original.EXPECTED_BOOTSTRAPS,
        "confidence_intervals_recomputed": len(results) + len(rankings),
        "strict_regressions": len(regressions),
        "verified_native_library_count": len(native),
        "full_correctness_campaign_steps": 22,
        "rust_full_correctness_campaign_steps": 22,
        "zig_full_correctness_campaign_steps": 22,
        "c_deep_contract_sha256": deep_digest,
        "c_deep_contract_checks": 393,
        "c_observability_sha256": observability_digest,
        "c_observability_checks": 479,
        "c_observability_binder_checks": 34,
        "poisoned_control_count": controls["poisoned_control_count"],
        "role_confusion_incident_sha256": ROLE_CONFUSION_INCIDENT_SHA256,
        "role_confusion_incident_path": str(ROLE_CONFUSION_INCIDENT_PATH.resolve()),
        "c_stage20_verifier_incident_sha256": C_STAGE20_VERIFIER_INCIDENT_SHA256,
        "c_stage20_verifier_incident_path": str(C_STAGE20_VERIFIER_INCIDENT_PATH.resolve()),
        "rust_optimization_verified": True,
        "capacity16_optimization_verified": True,
        "mandatory_prefix_optimization_verified": True,
        "unchanged_rust_bridge_verified": True,
        "c_optimization_verified": True,
        "zig_optimization_verified": True,
        "zig_interned_attributes_optimization_verified": True,
        "rust_capture_initialization_optimization_verified": True,
        "c_singleton_split_memchr_optimization_verified": True,
        "unchanged_reference_candidates": list(UNCHANGED_REFERENCE_CANDIDATES),
        "output": original.display_path(output_path),
        "sha256": hashlib.sha256(encoded).hexdigest(), "failed": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("self-test", help="run only frozen candidate-free synthetic public-practice isolation controls")
    check = commands.add_parser("verify", help="replay the sole fully qualified C Stage-21 practice-only comparison")
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
    except (
        AuditError, KeyError, ValueError, TypeError, OverflowError,
        RecursionError, json.JSONDecodeError, UnicodeError,
    ) as error:
        print(json.dumps({
            "schema": SCHEMA, "result": "FAIL", "holdout_accessed": False,
            "timing_performed": False, "error": str(error), "failed": 1,
        }, sort_keys=True))
        raise SystemExit(1) from error
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
