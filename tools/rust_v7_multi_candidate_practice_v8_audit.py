#!/usr/bin/env python3
"""Independently replay one fully qualified Rust capture-hoist practice run.

The seven earlier public experiments, both genuine verifier incidents, and
the frozen Python correctness and practice plans are immutable.  No future
campaign, observation, measurement, or candidate is inferred.  Verification
fails before writing anything while even one required real result is missing.
"""

from __future__ import annotations

import argparse
import copy
import gzip
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


ROOT = original.ROOT
EVIDENCE = original.EVIDENCE
SCHEMA = "rebar-v7-multi-candidate-practice-integrity-v8"
PREFIX = "three-qualified-engines-public-practice-v8"
EXPECTED_EXCLUSIVE_SLOT = "three-qualified-engines-rust-capture-initialization-v8"
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
V1_INTEGRITY_SHA256 = "8739803b6cd020b8b4f663223435fd1e39ef5603e90195b2a268a9fa7fbc0340"
V2_INTEGRITY_SHA256 = "82ef917ca82ba124af6311f3bf10398a2a040286ed06430919bbdd26dd61e057"
V3_INTEGRITY_SHA256 = "aa1921230845a01aa03d607bd8609b3475dc659cacda5e6135d8b7064ed60c22"
V4_INTEGRITY_SHA256 = "7bfb360fa570510d585c923345f00162da92a3a7cd6379528ad981b1ec003174"
V5_INTEGRITY_SHA256 = "015a2f9e3ceebd3792c4de62828c2d63fbafd7a5f866c9513b60b964a974712e"
V6_INTEGRITY_SHA256 = "8804136b49d7203854bda098b4c224e1b62ae9ecc3d050e81378d1b9b9515134"
V7_INTEGRITY_SHA256 = "d7c51632e9e9419b1e309897eed0f60b1d0af5ffc1cecd66413874a8d487212d"

HISTORICAL_V7_AUDIT_SHA256 = "5ce9df468d136b47c435456e59d372aed74d89f80fe1f877988dd7dba784b737"
HISTORICAL_V7_REGRESSIONS = 259
PREVIOUS_RUST_SOURCE_SHA256 = "d6e0cd31b06cd4edb1af7f8fb7409c23027289818934b35a03d5b3cc17444784"
PREVIOUS_RUST_ENGINE_SHA256 = "37ab3d8598bdbbe9097810a35b54f3558fd0473db903d0a0c6b6527068dbf7cb"
UNCHANGED_RUST_BRIDGE_SOURCE_SHA256 = "83afb5a709a6d0ea1701dfd64db30644edbf2cb0276c2db731a8119cfd52d8ed"
UNCHANGED_RUST_BRIDGE_SHA256 = "1f072e81ba9339a8b2e52a7e93b7bcde791c4d518620b6bd760af67c7c89af34"
UNCHANGED_C_ENGINE_SHA256 = "0e4d194fc14a2e307dd765ec5632acbe7b4192a0b2a74833a1126fbd0e5b5b91"
UNCHANGED_ZIG_BRIDGE_SOURCE_SHA256 = "92d4039e1db2e01757edfd4edf56006c4735c3bc64352b6ce9c5d1f69decafcf"
UNCHANGED_ZIG_BRIDGE_SHA256 = "80d7dab57cbee317ee1727862e27cd7dcf4cb22e1a944f4b29f2e4e983f940ed"
UNCHANGED_ZIG_ENGINE_SHA256 = "70bafca56a3f48477b2011f016a81b625e5f40a772af6a986d32b9098269f614"
HISTORICAL_RUST_CAMPAIGN_SHA256 = "9543fbbb39bbf42f5329a051b8441e69c756a495287a06c2f877c757b3ec5688"
C_CAMPAIGN_SHA256 = "c211d826032fed60c30024beb6de66c3e20b08fdcb936b53393d0a5fdba09721"
ZIG_CAMPAIGN_SHA256 = "4ba7cb9c45a70b747cc0a6eb721f6bb51081157f527d1bf5e578e603715ae5dc"
INITIAL_FAILURE_SHA256 = "ccaf3813b29badcf80c552dc0d850f83a2ca122cc3cc3057576dd519aed4f088"
ROLE_CONFUSION_INCIDENT_PATH = EVIDENCE / "ZIG-STAGE-13-VERIFIER-INCIDENTS.md"
ROLE_CONFUSION_INCIDENT_SHA256 = "84efcdbd0059ab430c84322695bf472f66fdc1cc05efd74e383b62114efcedff"
C_STAGE20_VERIFIER_INCIDENT_PATH = EVIDENCE / "C-STAGE-20-INDEPENDENCE-AUDIT-RETRY.md"
C_STAGE20_VERIFIER_INCIDENT_SHA256 = "0ee24eabfe369328c3dcd03c2dabab80f46a3851e82b6dbf4b390a72667149c4"
UNCHANGED_REFERENCE_CANDIDATES = [
    "re", "candidates.vm_candidate", "candidates.zig_candidate",
]

# Freeze only facts actually produced by the reviewed, built, source-audited
# Rust change and its real independently run edge, deep, and observability
# correctness gates.  The complete campaign and public timing remain unset.
V8_SLOT: str | None = "three-qualified-engines-rust-capture-initialization-v8"
V8_AUDIT_SHA256: str | None = "55ab21dfa78193c96551f5d3d95a51251f30e535cdb37c24df3d2e6044166854"
V8_SUMMARY_SHA256: str | None = "77d3aa8ac970e126d11c9e9aad832f480670aceda1778966d16a4a768ca5a4c3"
V8_COMPRESSED_RAW_SHA256: str | None = "f67cd7ddc0dff0cd256b156e23bfc8efc39546df8a4aec909cd9034261c91289"
V8_RAW_SHA256: str | None = "32a265fa68ce82e76572c33696f41a605c2ea1b572d31411badbe78ff3cff8d4"
RUST_CAPTURE_CAMPAIGN_PATH: Path | None = ROOT / "candidates/evidence/rust-v8-rust-owned-capture-init-hoist-sealed-campaign.json"
RUST_CAPTURE_CAMPAIGN_SHA256: str | None = "9ddbab81b16f0440ca19bffb8a539ea08d4a7ff33606ee3019eaf85977c2249a"
RUST_CAPTURE_EDGE_PATH: Path | None = ROOT / "candidates/evidence/rust-v7-edge-oracle-rust-owned-capture-init-hoist.json.gz"
RUST_CAPTURE_EDGE_COMPRESSED_SHA256: str | None = "397f8940b7b98c454241cd00290ec67dbf2592c6f95096e811de0771b98eebbd"
RUST_CAPTURE_EDGE_PAYLOAD_SHA256: str | None = "c3e67b08ac34540dbbd248b5ffb07161ae7e9b815a6f6bcbc757ef178f7585b1"
RUST_CAPTURE_DEEP_PATH: Path | None = ROOT / "candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-OWNED-CAPTURE-INIT-HOIST.json.gz"
RUST_CAPTURE_DEEP_COMPRESSED_SHA256: str | None = "6a04536315e0f2af9ca129179b539b629614dcdd707f62ac61c5f24fe05a5a33"
RUST_CAPTURE_OBSERVABILITY_PATH: Path | None = ROOT / "candidates/evidence/rust-v8-observability-rust-qualified-owned-capture-init-hoist.json.gz"
RUST_CAPTURE_OBSERVABILITY_COMPRESSED_SHA256: str | None = "6a2d4ec435109e0f96092d65c27092c9e6b1c3eea21b21f4962aae10a0a9cb8e"
RUST_CAPTURE_SOURCE_SHA256: str | None = "4b89d916e4c33e2b516be570ff3e75694f03dcea5eccf9320cedf07471b07dac"
RUST_CAPTURE_ENGINE_SHA256: str | None = "e7177c97070b2d0073a721044c4d23bb93e0d0883c1f2ccaa07c41eda8b96255"
EXPECTED_REGRESSIONS: int | None = 261

AuditError = original.AuditError
require = original.require


def required_digest(value: str | None, label: str) -> str:
    require(
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value),
        f"the actual source-bound Rust capture-hoist {label} has not been frozen",
    )
    return value


def required_path(value: Path | None, label: str) -> Path:
    require(
        isinstance(value, Path),
        f"the actual source-bound Rust capture-hoist {label} path has not been frozen",
    )
    path = value.resolve()
    require(path.is_relative_to(ROOT.resolve()), f"the {label} path escaped this project")
    return path


def required_slot(value: str | None) -> str:
    require(
        isinstance(value, str)
        and value == EXPECTED_EXCLUSIVE_SLOT
        and value != PREFIX
        and value not in {
            original.EXPECTED_SLOT, second.SLOT, third.SLOT,
            fourth.SLOT, fifth.SLOT, sixth.SLOT, seventh.V7_SLOT,
        },
        "the genuine unique Rust capture-hoist public-practice slot has not been frozen",
    )
    return value


def validate_preserved_incident(actual: str, expected: str, label: str) -> None:
    require(actual == expected, f"the genuine preserved {label} incident was concealed or changed")


def validate_version_identity(
    summary: dict, plan: dict, profile: original.Profile,
    raw_path: Path, expected_slot: str,
) -> None:
    original.validate_header(summary, plan, profile, None)
    require(summary.get("exclusive_slot") == expected_slot, "v8 substituted a historical or unauthorized practice slot")
    require(summary.get("raw_path") == str(raw_path.resolve()), "v8 substituted the recorded public-practice raw path")
    require(
        summary.get("measurement")
        == "balanced practice diagnostic only; not a holdout result or final speed claim",
        "the Rust practice result was misrepresented as held-out or final performance",
    )


def validate_historical_continuity(
    v1: dict, v2: dict, v3: dict, v4: dict, v5: dict, v6: dict, v7: dict,
    sources: dict[str, str], native: dict[str, str], measured: dict[str, str],
    rust_source_sha256: str, rust_engine_sha256: str,
) -> None:
    require(v7.get("schema") == seventh.SCHEMA, "the frozen Zig Stage-13 experiment was replaced")
    require(v7.get("result") == "PASS" and v7.get("failed") == 0, "the frozen Zig Stage-13 experiment did not pass")
    require(v7.get("holdout_accessed") is False and v7.get("timing_performed") is False, "the historical Zig replay accessed or timed hidden performance")
    require(v7.get("module_order") == list(original.MODULES), "historical v7 changed independent candidate families")
    require(v7.get("cases_per_candidate") == original.EXPECTED_CASES, "historical v7 changed the frozen practice denominator")
    require(v7.get("trials_per_module_case") == original.EXPECTED_TRIALS, "historical v7 changed paired trials")
    require(v7.get("bootstrap_draws") == original.EXPECTED_BOOTSTRAPS, "historical v7 changed confidence draws")
    require(v7.get("frozen_plan_sha256") == original.EXPECTED_PLAN_SHA256, "historical v7 changed the frozen public practice plan")
    require(v7.get("source_sha256") == V7_AUDITOR_SHA256, "the immutable Stage-13 practice verifier changed")
    for key, expected in (
        ("historical_v1_integrity_sha256", V1_INTEGRITY_SHA256),
        ("historical_v2_integrity_sha256", V2_INTEGRITY_SHA256),
        ("historical_v3_integrity_sha256", V3_INTEGRITY_SHA256),
        ("historical_v4_integrity_sha256", V4_INTEGRITY_SHA256),
        ("historical_v5_integrity_sha256", V5_INTEGRITY_SHA256),
        ("historical_v6_integrity_sha256", V6_INTEGRITY_SHA256),
    ):
        require(v7.get(key) == expected, f"historical v7 substituted immutable evidence: {key}")
    require(v7.get("from_scratch_audit_sha256") == HISTORICAL_V7_AUDIT_SHA256, "historical v7 substituted its source-independent audit")
    require(v7.get("strict_regressions") == HISTORICAL_V7_REGRESSIONS, "historical v7 concealed its actual 259 slowdowns")
    require(v7.get("full_correctness_campaign_sha256") == ZIG_CAMPAIGN_SHA256, "historical v7 changed its complete Zig Stage-13 campaign")
    require(v7.get("full_correctness_campaign_steps") == 22, "historical v7 omitted Zig correctness stages")
    require(v7.get("c_full_correctness_campaign_sha256") == C_CAMPAIGN_SHA256, "historical v7 changed the complete Stage-20 C campaign")
    require(v7.get("c_full_correctness_campaign_steps") == 22, "historical v7 omitted C correctness stages")
    require(v7.get("rust_full_correctness_campaign_sha256") == HISTORICAL_RUST_CAMPAIGN_SHA256, "historical v7 changed the former complete Rust campaign")
    require(v7.get("rust_full_correctness_campaign_steps") == 22, "historical v7 omitted former Rust correctness stages")
    require(v7.get("initial_audit_failure_sha256") == INITIAL_FAILURE_SHA256, "historical v7 concealed the genuine initial Rust failure")
    require(v7.get("role_confusion_incident_sha256") == ROLE_CONFUSION_INCIDENT_SHA256, "historical v7 concealed the genuine Zig verifier incident")
    require(v7.get("role_confusion_incident_path") == str(ROLE_CONFUSION_INCIDENT_PATH.resolve()), "historical v7 substituted the genuine Zig verifier incident path")
    historical_controls = v7.get("self_test")
    require(
        isinstance(historical_controls, dict)
        and historical_controls.get("result") == "PASS"
        and isinstance(historical_controls.get("poisoned_control_count"), int)
        and historical_controls["poisoned_control_count"] >= 187
        and historical_controls.get("role_confusion_incident_control_verified") is True,
        "historical v7 concealed frozen source-isolation or incident controls",
    )
    for flag in (
        "rust_optimization_verified", "capacity16_optimization_verified",
        "mandatory_prefix_optimization_verified", "unchanged_rust_bridge_verified",
        "c_optimization_verified", "zig_optimization_verified",
        "zig_interned_attributes_optimization_verified",
    ):
        require(v7.get(flag) is True, f"historical v7 dropped a qualified-source optimization: {flag}")

    old_sources = v7.get("qualified_source_fingerprints")
    old_native = v7.get("native_elf_fingerprints")
    old_measured = v7.get("candidate_binary_sha256_before")
    require(isinstance(old_sources, dict), "historical v7 omitted production source fingerprints")
    require(isinstance(old_native, dict), "historical v7 omitted mapped native fingerprints")
    require(isinstance(old_measured, dict), "historical v7 omitted timed native fingerprints")
    require(v7.get("candidate_binary_sha256_after") == old_measured, "historical v7 altered an engine during timing")
    seventh.validate_historical_continuity(
        v1, v2, v3, v4, v5, v6, old_sources, old_native, old_measured,
        UNCHANGED_ZIG_BRIDGE_SOURCE_SHA256, UNCHANGED_ZIG_BRIDGE_SHA256,
    )

    changed_source = "candidates/rust/src/lib.rs"
    changed_native = "candidates.rust_candidate:native-engine"
    changed_source_role = "candidates.rust_candidate:native-source"
    require(set(sources) == set(old_sources), "the Rust-only experiment added or omitted a production source")
    require(set(native) == set(old_native), "the Rust-only experiment added or omitted a mapped native library")
    require(set(measured) == set(old_measured), "the Rust-only experiment added or omitted a timed artifact")
    for path, digest in old_sources.items():
        if path != changed_source:
            require(sources.get(path) == digest, f"the Rust-only experiment changed another source: {path}")
    for role, digest in old_native.items():
        if role != changed_native:
            require(native.get(role) == digest, f"the Rust-only experiment changed another mapped library: {role}")
    for role, digest in old_measured.items():
        if role not in {changed_native, changed_source_role}:
            require(measured.get(role) == digest, f"the Rust-only experiment changed another timed artifact: {role}")
    require(old_sources.get(changed_source) == PREVIOUS_RUST_SOURCE_SHA256, "historical v7 omitted the previously qualified owned Rust source")
    require(old_native.get(changed_native) == PREVIOUS_RUST_ENGINE_SHA256, "historical v7 omitted the previously qualified owned Rust engine")
    require(old_measured.get(changed_source_role) == PREVIOUS_RUST_SOURCE_SHA256, "historical v7 did not time the genuine previously qualified Rust source")
    require(sources.get(changed_source) == rust_source_sha256, "the Rust capture-hoist source differs from its full qualification")
    require(native.get(changed_native) == rust_engine_sha256, "the Rust capture-hoist library differs from its full qualification")
    require(measured.get(changed_native) == rust_engine_sha256, "the timed Rust library is not the actual mapped Rust engine")
    require(measured.get(changed_source_role) == rust_source_sha256, "the timed Rust source does not match its owned engine")
    require(rust_source_sha256 != PREVIOUS_RUST_SOURCE_SHA256, "the alleged Rust capture-hoist did not change its owned source")
    require(rust_engine_sha256 != PREVIOUS_RUST_ENGINE_SHA256, "the alleged Rust capture-hoist did not change its owned engine")
    require(sources.get("candidates/rust/py_bridge.c") == UNCHANGED_RUST_BRIDGE_SOURCE_SHA256, "the Rust capture-hoist replaced its Python bridge source")
    require(native.get("candidates.rust_candidate:native-bridge") == UNCHANGED_RUST_BRIDGE_SHA256, "the Rust capture-hoist replaced its mapped bridge")
    require(native.get("candidates.vm_candidate:native-engine") == UNCHANGED_C_ENGINE_SHA256, "the Rust-only experiment changed the C engine")
    require(native.get("candidates.zig_candidate:native-bridge") == UNCHANGED_ZIG_BRIDGE_SHA256, "the Rust-only experiment changed the Zig bridge")
    require(native.get("candidates.zig_candidate:native-engine") == UNCHANGED_ZIG_ENGINE_SHA256, "the Rust-only experiment changed the Zig engine")


def validate_v8_edges(
    summary: dict, measured: dict[str, str], rust_path: Path,
    rust_compressed_sha256: str, rust_payload_sha256: str,
) -> list[dict]:
    require(original.sha256_file(original.EDGE_SOURCE_PATH) == original.EXPECTED_EDGE_SOURCE_SHA256, "the frozen independent Python matching-oracle source changed")
    baseline, baseline_digest = original.read_edge(original.STDLIB_EDGE_PATH, "frozen pinned Python matching baseline")
    original.validate_edge_document(baseline, "re")
    require(baseline_digest == original.EXPECTED_STDLIB_EDGE_SHA256, "the immutable Python baseline matching payload changed")
    require(original.sha256_file(rust_path) == rust_compressed_sha256, "the fresh Rust capture-hoist compressed matching proof changed")
    require(original.sha256_file(sixth.C_EDGE_PATH) == sixth.C_EDGE_COMPRESSED_SHA256, "the preserved Stage-20 C matching proof changed")
    zig_path = required_path(seventh.ZIG13_EDGE_PATH, "preserved Zig Stage-13 matching proof")
    zig_compressed = required_digest(seventh.ZIG13_EDGE_COMPRESSED_SHA256, "preserved Zig Stage-13 compressed matching proof")
    zig_payload = required_digest(seventh.ZIG13_EDGE_PAYLOAD_SHA256, "preserved Zig Stage-13 matching payload")
    require(original.sha256_file(zig_path) == zig_compressed, "the preserved Stage-13 Zig matching proof changed")
    entries = summary.get("verified_edge_oracles")
    require(isinstance(entries, list) and len(entries) == len(original.MODULES) - 1, "v8 omitted an independently qualified candidate")
    paths = {
        "candidates.rust_candidate": rust_path,
        "candidates.vm_candidate": sixth.C_EDGE_PATH,
        "candidates.zig_candidate": zig_path,
    }
    for module, proof in zip(original.MODULES[1:], entries, strict=True):
        require(isinstance(proof, dict) and proof.get("module") == module, "v8 reordered or cross-contaminated independent candidate proofs")
        path = paths[module]
        require(proof.get("path") == str(path.resolve()), f"{module} substituted its independent matching-proof path")
        require(proof.get("correctness_checks") == 223_198, f"{module} omitted frozen Python matching cases")
        require(proof.get("actual_sha256") == original.EXPECTED_EDGE_ANSWER_SHA256, f"{module} failed exact frozen Python matching answers")
        require(proof.get("script_sha256") == original.EXPECTED_EDGE_SOURCE_SHA256, f"{module} substituted the frozen Python matching oracle")
        require(proof.get("stdlib_baseline_sha256") == baseline_digest, f"{module} substituted the pinned stable Python baseline")
        report, payload_digest = original.read_edge(path, f"{module} independently frozen v8 matching proof")
        original.validate_edge_document(report, module)
        require(proof.get("report_sha256") == payload_digest, f"{module} substituted its decompressed matching-proof identity")
        if module == "candidates.rust_candidate":
            require(payload_digest == rust_payload_sha256, "the Rust matching proof does not certify the actual fresh owned engine")
        elif module == "candidates.vm_candidate":
            require(payload_digest == sixth.C_EDGE_PAYLOAD_SHA256, "the C matching proof does not certify the preserved Stage-20 engine")
        else:
            require(payload_digest == zig_payload, "the Zig matching proof does not certify the preserved Stage-13 engine")
        artifacts = second.artifact_fingerprints(report.get("candidate_artifacts"), module)
        require(proof.get("candidate_artifacts") == artifacts, f"{module} timed artifacts not source-bound to its matching proof")
        for role, item in artifacts.items():
            if role == "public-python":
                key = f"{module}:module"
            elif module == "candidates.vm_candidate" and role == "native-bridge":
                key = f"{module}:native-engine"
            else:
                key = f"{module}:{role}"
            require(measured.get(key) == item["sha256"], f"{module} substituted a timed source, engine, bridge, or family")
    return entries


def read_compressed_json(path: Path, compressed_sha256: str, label: str) -> dict:
    require(original.sha256_file(path) == compressed_sha256, f"the exact compressed {label} changed")
    try:
        with gzip.open(path, "rt", encoding="utf-8") as source:
            document = json.load(source)
    except (OSError, EOFError, UnicodeError, json.JSONDecodeError) as error:
        raise AuditError(f"cannot read the complete source-bound {label}") from error
    require(isinstance(document, dict), f"the source-bound {label} is not an object")
    return document


def validate_rust_artifacts(
    document: dict, sources: dict[str, str], measured: dict[str, str], label: str,
) -> dict[str, dict]:
    artifacts = second.artifact_fingerprints(
        document.get("native_artifacts"), "candidates.rust_candidate",
    )
    require(
        set(artifacts) == {
            "bridge-source", "native-bridge", "native-engine",
            "native-source", "public-python",
        },
        f"{label} omitted or replaced a Rust production artifact",
    )
    for role, item in artifacts.items():
        if role in {"bridge-source", "native-source"}:
            require(sources.get(item["path"]) == item["sha256"], f"{label} used an unaudited Rust production source")
        key = "candidates.rust_candidate:module" if role == "public-python" else f"candidates.rust_candidate:{role}"
        require(measured.get(key) == item["sha256"], f"{label} differs from its actual timed Rust production artifact")
    return artifacts


def validate_rust_edge_reference(
    document: dict, edge_path: Path, edge_compressed_sha256: str, label: str,
) -> dict:
    edge = document.get("edge_oracle")
    require(isinstance(edge, dict), f"{label} omitted the frozen Rust matching proof")
    require(edge.get("archive_sha256") == edge_compressed_sha256, f"{label} substituted the Rust edge archive")
    require(edge.get("path") == str(edge_path.resolve()), f"{label} substituted the Rust edge path")
    require(edge.get("module") == "candidates.rust_candidate", f"{label} bound another candidate family")
    require(edge.get("checks") == 223_198 and edge.get("failed") == 0, f"{label} omitted or failed frozen Python matching cases")
    return edge


def validate_rust_deep_contract(
    deep: dict, sources: dict[str, str], measured: dict[str, str],
    edge_path: Path, edge_compressed_sha256: str,
) -> dict[str, dict]:
    label = "fresh Rust 393-case deep public-contract proof"
    require(deep.get("schema") == "rebar-rust-v8-deep-public-contract-v1", f"{label} substituted the immutable schema")
    require(deep.get("status") == "PASS", f"{label} did not pass")
    require(deep.get("candidate_module") == "candidates.rust_candidate", f"{label} qualified another candidate")
    require(deep.get("checks") == 393, f"{label} changed the frozen public obligation count")
    require(deep.get("public_mismatch_count") == 0, f"{label} concealed a documented public mismatch")
    require(deep.get("stdlib_vs_stdlib_mismatches") == [], f"{label} contains an unexplained Python self-oracle failure")
    require(deep.get("holdout") == "NOT ACCESSED", f"{label} accessed hidden benchmark material")
    require(deep.get("performance") == "NOT MEASURED", f"{label} performed benchmark timing")
    require(isinstance(deep.get("cross_engine_guard_count"), int) and deep["cross_engine_guard_count"] >= 10, f"{label} omitted independent-engine delegation guards")
    validate_rust_edge_reference(deep, edge_path, edge_compressed_sha256, label)
    return validate_rust_artifacts(deep, sources, measured, label)


def validate_rust_observability(
    observation: dict, sources: dict[str, str], measured: dict[str, str],
    edge_path: Path, edge_compressed_sha256: str,
    deep_path: Path, deep_compressed_sha256: str,
    deep_artifacts: dict[str, dict],
) -> None:
    label = "fresh Rust 479-case public observability proof"
    require(observation.get("schema") == "rebar-v8-multi-candidate-observability-v1", f"{label} substituted the immutable schema")
    require(observation.get("status") == "PASS", f"{label} did not pass")
    require(observation.get("candidate_module") == "candidates.rust_candidate", f"{label} qualified another candidate")
    require(observation.get("checks") == 479 and observation.get("candidate_checks") == 479, f"{label} changed the frozen public obligation count")
    require(observation.get("failures") == [] and observation.get("candidate_failures") == 0, f"{label} concealed a public observation failure")
    require(observation.get("private_binder_checks") == 34, f"{label} changed frozen native-boundary checks")
    require(observation.get("private_binder_failures") == [], f"{label} concealed a native binder failure")
    require(observation.get("holdout") == "NOT ACCESSED", f"{label} accessed hidden benchmark material")
    require(observation.get("performance") == "NOT MEASURED", f"{label} performed benchmark timing")
    validate_rust_edge_reference(observation, edge_path, edge_compressed_sha256, label)
    proof = observation.get("deep_proof")
    require(isinstance(proof, dict), f"{label} omitted its frozen deep-contract chain")
    require(proof.get("archive_sha256") == deep_compressed_sha256, f"{label} substituted the deep-contract archive")
    require(proof.get("path") == str(deep_path.resolve()), f"{label} substituted the deep-contract path")
    require(proof.get("candidate_module") == "candidates.rust_candidate", f"{label} bound another family's deep proof")
    require(proof.get("checks") == 393 and proof.get("status") == "PASS", f"{label} dropped or failed the frozen deep proof")
    require(proof.get("edge_archive_sha256") == edge_compressed_sha256, f"{label} substituted the matching proof in its deep chain")
    artifacts = validate_rust_artifacts(observation, sources, measured, label)
    require(artifacts == deep_artifacts, f"{label} qualified a different Rust engine from its deep proof")


def validate_rust_capture_campaign(
    campaign: dict, sources: dict[str, str], measured: dict[str, str],
    edge_path: Path, edge_compressed_sha256: str,
    deep_artifacts: dict[str, dict],
) -> None:
    label = "complete Rust capture-hoist 22-stage correctness campaign"
    require(campaign.get("schema") == "rebar-rust-campaign-gate-v1", f"{label} substituted its immutable schema")
    require(campaign.get("candidate") == "candidates.rust_candidate", f"{label} qualified another family")
    require(campaign.get("passed") is True, f"{label} did not pass")
    require(campaign.get("holdout_accessed") is False, f"{label} accessed hidden cases")
    require(campaign.get("timing_performed") is False and campaign.get("performance") == "NOT MEASURED", f"{label} performed benchmark timing")
    require(campaign.get("required_correctness_step_count") == 22, f"{label} changed the frozen stage denominator")
    stages = campaign.get("steps")
    require(isinstance(stages, list) and len(stages) == 22, f"{label} omitted a required correctness stage")
    require(all(isinstance(stage, dict) and stage.get("passed") is True for stage in stages), f"{label} contains an unexplained mismatch, crash, or failed obligation")
    require(campaign.get("pinned_cpython") == "3.14.6", f"{label} changed the stable Python correctness baseline")
    require(campaign.get("python_executable") == str(original.PINNED_PYTHON), f"{label} changed the frozen Python executable")
    require(campaign.get("mode") == "sealed-practice-only", f"{label} weakened sealed practice isolation")
    edge = validate_rust_edge_reference(campaign, edge_path, edge_compressed_sha256, label)
    artifacts = validate_rust_artifacts(campaign, sources, measured, label)
    matching = second.artifact_fingerprints(edge.get("candidate_artifacts"), "candidates.rust_candidate")
    require(artifacts == matching, f"{label} differs from the complete independent matching proof")
    require(artifacts == deep_artifacts, f"{label} differs from the complete independent deep and observability proofs")


def synthetic_histories() -> tuple[
    dict, dict, dict, dict, dict, dict, dict,
    dict[str, str], dict[str, str], dict[str, str], str, str,
]:
    (
        v1, v2, v3, v4, v5, v6, previous_sources, previous_native,
        previous_measured, _synthetic_zig_source, _synthetic_zig_bridge,
    ) = seventh.synthetic_histories()
    zig_path = "candidates/zig/py_bridge.c"
    zig_role = "candidates.zig_candidate:native-bridge"
    previous_sources[zig_path] = UNCHANGED_ZIG_BRIDGE_SOURCE_SHA256
    previous_native[zig_role] = UNCHANGED_ZIG_BRIDGE_SHA256
    previous_measured[zig_role] = UNCHANGED_ZIG_BRIDGE_SHA256
    v7 = {
        "schema": seventh.SCHEMA, "result": "PASS", "failed": 0,
        "holdout_accessed": False, "timing_performed": False,
        "module_order": list(original.MODULES),
        "cases_per_candidate": original.EXPECTED_CASES,
        "trials_per_module_case": original.EXPECTED_TRIALS,
        "bootstrap_draws": original.EXPECTED_BOOTSTRAPS,
        "frozen_plan_sha256": original.EXPECTED_PLAN_SHA256,
        "source_sha256": V7_AUDITOR_SHA256,
        "historical_v1_integrity_sha256": V1_INTEGRITY_SHA256,
        "historical_v2_integrity_sha256": V2_INTEGRITY_SHA256,
        "historical_v3_integrity_sha256": V3_INTEGRITY_SHA256,
        "historical_v4_integrity_sha256": V4_INTEGRITY_SHA256,
        "historical_v5_integrity_sha256": V5_INTEGRITY_SHA256,
        "historical_v6_integrity_sha256": V6_INTEGRITY_SHA256,
        "from_scratch_audit_sha256": HISTORICAL_V7_AUDIT_SHA256,
        "strict_regressions": HISTORICAL_V7_REGRESSIONS,
        "full_correctness_campaign_sha256": ZIG_CAMPAIGN_SHA256,
        "full_correctness_campaign_steps": 22,
        "c_full_correctness_campaign_sha256": C_CAMPAIGN_SHA256,
        "c_full_correctness_campaign_steps": 22,
        "rust_full_correctness_campaign_sha256": HISTORICAL_RUST_CAMPAIGN_SHA256,
        "rust_full_correctness_campaign_steps": 22,
        "initial_audit_failure_sha256": INITIAL_FAILURE_SHA256,
        "role_confusion_incident_sha256": ROLE_CONFUSION_INCIDENT_SHA256,
        "role_confusion_incident_path": str(ROLE_CONFUSION_INCIDENT_PATH.resolve()),
        "self_test": {
            "result": "PASS", "poisoned_control_count": 187,
            "role_confusion_incident_control_verified": True,
        },
        "rust_optimization_verified": True,
        "capacity16_optimization_verified": True,
        "mandatory_prefix_optimization_verified": True,
        "unchanged_rust_bridge_verified": True,
        "c_optimization_verified": True,
        "zig_optimization_verified": True,
        "zig_interned_attributes_optimization_verified": True,
        "qualified_source_fingerprints": dict(previous_sources),
        "native_elf_fingerprints": dict(previous_native),
        "candidate_binary_sha256_before": dict(previous_measured),
        "candidate_binary_sha256_after": dict(previous_measured),
    }
    rust_path = "candidates/rust/src/lib.rs"
    rust_role = "candidates.rust_candidate:native-engine"
    rust_source_role = "candidates.rust_candidate:native-source"
    synthetic_rust_source = hashlib.sha256(b"synthetic-rust-capture-initialization-source").hexdigest()
    synthetic_rust_engine = hashlib.sha256(b"synthetic-rust-capture-initialization-native").hexdigest()
    sources = {**previous_sources, rust_path: synthetic_rust_source}
    native = {**previous_native, rust_role: synthetic_rust_engine}
    measured = {
        **previous_measured,
        rust_role: synthetic_rust_engine,
        rust_source_role: synthetic_rust_source,
    }
    return (
        v1, v2, v3, v4, v5, v6, v7, sources, native, measured,
        synthetic_rust_source, synthetic_rust_engine,
    )


def self_test() -> dict:
    inherited = seventh.self_test()
    require(inherited.get("result") == "PASS", "the immutable Stage-13 candidate-free synthetic replay failed")
    previous = inherited.get("poisoned_controls")
    require(isinstance(previous, list) and len(previous) >= 187, "v8 omitted its 187 frozen historical corruption controls")
    plan, sample, _payload, profile = original.synthetic_evidence()
    sample_slot = "synthetic-rust-capture-initialization-candidate-free-v8"
    sample["exclusive_slot"] = sample_slot
    sample["raw_path"] = str(RAW_PATH.resolve())
    sample["measurement"] = "balanced practice diagnostic only; not a holdout result or final speed claim"
    validate_version_identity(sample, plan, profile, RAW_PATH, sample_slot)
    (
        v1, v2, v3, v4, v5, v6, v7, sources, native, measured,
        source_digest, engine_digest,
    ) = synthetic_histories()
    validate_historical_continuity(
        v1, v2, v3, v4, v5, v6, v7, sources, native, measured,
        source_digest, engine_digest,
    )
    controls = [*previous]

    def reject(name: str, action: object) -> None:
        try:
            action()  # type: ignore[operator]
        except (AuditError, KeyError, ValueError, TypeError, OverflowError):
            controls.append({"name": name, "passed": True})
            return
        raise AuditError(f"Rust capture-hoist synthetic controls accepted corruption: {name}")

    def poison_version(key: str, value: object) -> None:
        document = copy.deepcopy(sample)
        document[key] = value
        validate_version_identity(document, plan, profile, RAW_PATH, sample_slot)

    def poison_history(which: str, key: str, value: object) -> None:
        first, second_doc, third_doc, fourth_doc = (
            copy.deepcopy(v1), copy.deepcopy(v2),
            copy.deepcopy(v3), copy.deepcopy(v4),
        )
        fifth_doc, sixth_doc, seventh_doc = (
            copy.deepcopy(v5), copy.deepcopy(v6), copy.deepcopy(v7),
        )
        current_sources, current_native, current_measured = (
            dict(sources), dict(native), dict(measured),
        )
        groups = {
            "v1": first, "v2": second_doc, "v3": third_doc,
            "v4": fourth_doc, "v5": fifth_doc, "v6": sixth_doc,
            "v7": seventh_doc,
            "v7-sources": seventh_doc["qualified_source_fingerprints"],
            "v7-native": seventh_doc["native_elf_fingerprints"],
            "v7-measured": seventh_doc["candidate_binary_sha256_before"],
            "sources": current_sources, "native": current_native,
            "measured": current_measured,
        }
        groups[which][key] = value
        validate_historical_continuity(
            first, second_doc, third_doc, fourth_doc, fifth_doc, sixth_doc,
            seventh_doc, current_sources, current_native, current_measured,
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
        ("v8-filename-incorrectly-treated-as-slot", PREFIX),
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
    ):
        reject(label, lambda value=path: poison_version("raw_path", str(value.resolve())))
    reject("practice-falsely-claimed-final", lambda: poison_version("measurement", "final hidden benchmark"))
    for label, historical in (
        ("v1-history-substitution", "v1"),
        ("v2-history-substitution", "v2"),
        ("v3-history-substitution", "v3"),
        ("v4-history-substitution", "v4"),
        ("v5-history-substitution", "v5"),
        ("v6-history-substitution", "v6"),
        ("v7-history-substitution", "v7"),
    ):
        reject(label, lambda value=historical: poison_history(value, "schema", SCHEMA))
    reject("historical-v7-259-losses-concealed", lambda: poison_history("v7", "strict_regressions", HISTORICAL_V7_REGRESSIONS - 1))
    reject("preserved-zig13-full-campaign-substituted", lambda: poison_history("v7", "full_correctness_campaign_sha256", "0" * 64))
    reject("preserved-c20-full-campaign-substituted", lambda: poison_history("v7", "c_full_correctness_campaign_sha256", "0" * 64))
    reject("historical-owned-rust-campaign-substituted", lambda: poison_history("v7", "rust_full_correctness_campaign_sha256", "0" * 64))
    reject("genuine-initial-rust-failure-concealed", lambda: poison_history("v7", "initial_audit_failure_sha256", "0" * 64))
    reject("historical-zig-incident-concealed", lambda: poison_history("v7", "role_confusion_incident_sha256", "0" * 64))
    reject("historical-187-corruption-controls-concealed", lambda: poison_history("v7", "self_test", {"result": "PASS", "poisoned_control_count": 186, "role_confusion_incident_control_verified": True}))
    reject("historical-rust-owned-source-replaced", lambda: poison_history("v7-sources", "candidates/rust/src/lib.rs", source_digest))
    reject("historical-rust-owned-engine-replaced", lambda: poison_history("v7-native", "candidates.rust_candidate:native-engine", engine_digest))
    reject("capture-rust-source-not-new", lambda: poison_history("sources", "candidates/rust/src/lib.rs", PREVIOUS_RUST_SOURCE_SHA256))
    reject("capture-rust-native-not-new", lambda: poison_history("native", "candidates.rust_candidate:native-engine", PREVIOUS_RUST_ENGINE_SHA256))
    reject("capture-rust-measured-source-substituted", lambda: poison_history("measured", "candidates.rust_candidate:native-source", "0" * 64))
    reject("capture-rust-measured-native-substituted", lambda: poison_history("measured", "candidates.rust_candidate:native-engine", "0" * 64))
    reject("unchanged-rust-bridge-source-substituted", lambda: poison_history("sources", "candidates/rust/py_bridge.c", "0" * 64))
    reject("unchanged-rust-mapped-bridge-substituted", lambda: poison_history("native", "candidates.rust_candidate:native-bridge", "0" * 64))
    reject("unchanged-c-stage20-source-substituted", lambda: poison_history("sources", "candidates/_vm_native.c", "0" * 64))
    reject("unchanged-c-stage20-engine-substituted", lambda: poison_history("native", "candidates.vm_candidate:native-engine", "0" * 64))
    reject("unchanged-zig13-source-substituted", lambda: poison_history("sources", "candidates/zig/py_bridge.c", "0" * 64))
    reject("unchanged-zig13-bridge-substituted", lambda: poison_history("native", "candidates.zig_candidate:native-bridge", "0" * 64))
    reject("unchanged-zig13-engine-substituted", lambda: poison_history("native", "candidates.zig_candidate:native-engine", "0" * 64))
    reject("unchanged-python-baseline-substituted", lambda: poison_history("measured", "re:module", "0" * 64))
    for label, synthetic_value in (
        ("preserved-stage20-c-incident-concealed", b"synthetic-honest-c-stage20-incident"),
        ("preserved-stage13-zig-incident-concealed", b"synthetic-honest-zig-stage13-incident"),
    ):
        digest = hashlib.sha256(synthetic_value).hexdigest()
        validate_preserved_incident(digest, digest, label)
        reject(
            label,
            lambda expected=digest, name=label: validate_preserved_incident(
                "0" * 64, expected, name,
            ),
        )
    require(len(controls) >= 225, "v8 omitted frozen history, unchanged-family, or genuine-incident corruption controls")
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
        "inherited_poisoned_control_count": len(previous),
        "poisoned_control_count": len(controls),
        "poisoned_controls": controls,
        "role_confusion_incident_control_verified": True,
        "c_stage20_verifier_incident_control_verified": True,
        "unchanged_reference_candidates": list(UNCHANGED_REFERENCE_CANDIDATES),
        "failed": 0,
    }


def verify(raw_path: Path, summary_path: Path, audit_path: Path, output_path: Path) -> dict:
    slot = required_slot(V8_SLOT)
    audit_digest = required_digest(V8_AUDIT_SHA256, "canonical source-bound five-library independence audit")
    summary_digest = required_digest(V8_SUMMARY_SHA256, "single authorized public-practice summary")
    compressed_digest = required_digest(V8_COMPRESSED_RAW_SHA256, "compressed public-practice raw observation")
    raw_digest = required_digest(V8_RAW_SHA256, "decompressed public-practice raw observation")
    campaign_path = required_path(RUST_CAPTURE_CAMPAIGN_PATH, "complete passing 22-stage Rust correctness campaign")
    campaign_digest = required_digest(RUST_CAPTURE_CAMPAIGN_SHA256, "complete passing 22-stage Rust correctness campaign")
    edge_path = required_path(RUST_CAPTURE_EDGE_PATH, "fresh independent Rust matching proof")
    edge_digest = required_digest(RUST_CAPTURE_EDGE_COMPRESSED_SHA256, "fresh compressed Rust matching proof")
    edge_payload = required_digest(RUST_CAPTURE_EDGE_PAYLOAD_SHA256, "fresh decompressed Rust matching proof")
    deep_path = required_path(RUST_CAPTURE_DEEP_PATH, "fresh 393-case Rust public-contract proof")
    deep_digest = required_digest(RUST_CAPTURE_DEEP_COMPRESSED_SHA256, "fresh compressed Rust public-contract proof")
    observability_path = required_path(RUST_CAPTURE_OBSERVABILITY_PATH, "fresh 479-case Rust observability proof")
    observability_digest = required_digest(RUST_CAPTURE_OBSERVABILITY_COMPRESSED_SHA256, "fresh compressed Rust observability proof")
    source_digest = required_digest(RUST_CAPTURE_SOURCE_SHA256, "qualified owned Rust capture-hoist source")
    engine_digest = required_digest(RUST_CAPTURE_ENGINE_SHA256, "qualified mapped Rust capture-hoist engine")
    losses = EXPECTED_REGRESSIONS
    require(isinstance(losses, int) and not isinstance(losses, bool) and losses >= 0, "the actual one-shot Rust slowdown count has not been frozen")
    require(platform.python_implementation() == "CPython" and tuple(sys.version_info[:3]) == (3, 14, 6), "v8 requires the pinned stable CPython 3.14.6 baseline")
    require(Path(sys.executable).resolve() == original.PINNED_PYTHON.resolve(), "v8 requires the exact frozen Python executable")
    require(raw_path.resolve() == RAW_PATH.resolve(), "v8 may not substitute historical public observations")
    require(summary_path.resolve() == SUMMARY_PATH.resolve(), "v8 may not substitute historical public summaries")
    require(audit_path.resolve() == original.AUDIT_PATH.resolve(), "v8 may not replace the canonical source-independence audit")
    require(output_path.resolve() == OUTPUT_PATH.resolve(), "v8 may not replace historical integrity reports")
    require(not output_path.exists(), "the unique v8 public-practice integrity report already exists")
    require(not any(name in sys.modules for name in original.MODULES[1:]), "the independent v8 verifier imported a candidate")

    validate_preserved_incident(
        original.sha256_file(ROLE_CONFUSION_INCIDENT_PATH),
        ROLE_CONFUSION_INCIDENT_SHA256, "Zig Stage-13 verifier role-confusion",
    )
    validate_preserved_incident(
        original.sha256_file(C_STAGE20_VERIFIER_INCIDENT_PATH),
        C_STAGE20_VERIFIER_INCIDENT_SHA256, "C Stage-20 independence-audit retry",
    )
    for module, expected in (
        (original, V1_AUDITOR_SHA256), (second, V2_AUDITOR_SHA256),
        (third, V3_AUDITOR_SHA256), (fourth, V4_AUDITOR_SHA256),
        (fifth, V5_AUDITOR_SHA256), (sixth, V6_AUDITOR_SHA256),
        (seventh, V7_AUDITOR_SHA256),
    ):
        require(original.sha256_file(Path(module.__file__).resolve()) == expected, "an immutable historical public-practice verifier changed")
    require(original.sha256_file(third.INITIAL_FAILURE_PATH) == INITIAL_FAILURE_SHA256, "the genuine preserved first Rust failure was concealed or rewritten")

    profile = original.Profile()
    plan = original.read_json(original.PLAN_PATH, "immutable frozen 624-case public practice plan", original.EXPECTED_PLAN_SHA256)
    require(plan.get("expected_sha256") == original.EXPECTED_FROZEN_ANSWER_SHA256, "v8 changed frozen Python public-practice answers")
    original.validate_plan(plan, profile)
    summary = original.read_json(summary_path, "actual single authorized v8 Rust public-practice summary", summary_digest)
    validate_version_identity(summary, plan, profile, raw_path, slot)
    require(summary.get("compressed_raw_sha256") == compressed_digest, "v8 substituted the recorded compressed public observations")
    require(summary.get("raw_sha256") == raw_digest, "v8 substituted the recorded decompressed public observations")
    require(original.sha256_file(raw_path) == compressed_digest, "v8 changed the exact public raw gzip")

    audit = original.read_json(audit_path, "actual Rust capture-hoist source-bound independence audit", audit_digest)
    sources, native = original.validate_independence(audit)
    measured = original.validate_measured_fingerprints(summary, sources, native)
    v1 = original.read_json(original.OUTPUT_PATH, "frozen v1 independent public result", V1_INTEGRITY_SHA256)
    v2 = original.read_json(second.OUTPUT_PATH, "frozen v2 independent public result", V2_INTEGRITY_SHA256)
    v3 = original.read_json(third.OUTPUT_PATH, "frozen v3 independent public result", V3_INTEGRITY_SHA256)
    v4 = original.read_json(fourth.OUTPUT_PATH, "frozen v4 independent public result", V4_INTEGRITY_SHA256)
    v5 = original.read_json(fifth.OUTPUT_PATH, "frozen v5 independent public result", V5_INTEGRITY_SHA256)
    v6 = original.read_json(sixth.OUTPUT_PATH, "frozen v6 independent public result", V6_INTEGRITY_SHA256)
    v7 = original.read_json(seventh.OUTPUT_PATH, "frozen v7 independent public result", V7_INTEGRITY_SHA256)
    validate_historical_continuity(
        v1, v2, v3, v4, v5, v6, v7, sources, native, measured,
        source_digest, engine_digest,
    )
    edge_proofs = validate_v8_edges(summary, measured, edge_path, edge_digest, edge_payload)

    deep = read_compressed_json(deep_path, deep_digest, "fresh 393-case Rust public-contract evidence")
    deep_artifacts = validate_rust_deep_contract(
        deep, sources, measured, edge_path, edge_digest,
    )
    observation = read_compressed_json(
        observability_path, observability_digest,
        "fresh 479-case Rust public-observability evidence",
    )
    validate_rust_observability(
        observation, sources, measured, edge_path, edge_digest,
        deep_path, deep_digest, deep_artifacts,
    )
    campaign = original.read_json(campaign_path, "genuine complete 22-stage Rust capture-hoist campaign", campaign_digest)
    validate_rust_capture_campaign(
        campaign, sources, measured, edge_path, edge_digest, deep_artifacts,
    )
    c_campaign = original.read_json(sixth.CAMPAIGN_PATH, "preserved complete C Stage-20 correctness campaign", C_CAMPAIGN_SHA256)
    sixth.validate_c_campaign(c_campaign, sources, measured)
    zig_campaign_path = required_path(seventh.ZIG13_CAMPAIGN_PATH, "preserved complete Zig Stage-13 correctness campaign")
    zig_campaign = original.read_json(zig_campaign_path, "preserved complete Zig Stage-13 correctness campaign", ZIG_CAMPAIGN_SHA256)
    zig_edge_path = required_path(seventh.ZIG13_EDGE_PATH, "preserved Zig Stage-13 matching proof")
    zig_edge_digest = required_digest(seventh.ZIG13_EDGE_COMPRESSED_SHA256, "preserved Zig Stage-13 compressed matching proof")
    seventh.validate_zig_campaign(zig_campaign, sources, measured, zig_edge_path, zig_edge_digest)

    try:
        with raw_path.open("rb") as source:
            observations = original.read_observations(
                source, compressed_digest, summary, plan, profile,
            )
    except OSError as error:
        raise AuditError("cannot open the exact complete v8 public practice observations") from error
    results, rankings = original.recompute_results(plan, observations, profile)
    regressions = original.validate_results(summary, results, rankings, profile)
    require(len(regressions) == losses, "v8 concealed or altered actual substantial public-practice losses")
    controls = self_test()
    require(not any(name in sys.modules for name in original.MODULES[1:]), "the independent v8 replay imported a production candidate")

    document = {
        "schema": SCHEMA, "result": "PASS", "holdout_accessed": False,
        "timing_performed": False,
        "measurement": "independent replay of one Rust capture-initialization four-way public practice run; not final or held-out performance",
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
        "historical_v1_integrity_sha256": V1_INTEGRITY_SHA256,
        "historical_v2_integrity_sha256": V2_INTEGRITY_SHA256,
        "historical_v3_integrity_sha256": V3_INTEGRITY_SHA256,
        "historical_v4_integrity_sha256": V4_INTEGRITY_SHA256,
        "historical_v5_integrity_sha256": V5_INTEGRITY_SHA256,
        "historical_v6_integrity_sha256": V6_INTEGRITY_SHA256,
        "historical_v7_integrity_sha256": V7_INTEGRITY_SHA256,
        "from_scratch_audit_sha256": audit_digest,
        "from_scratch_control_count": 76,
        "verified_independent_engine_count": len(original.MODULES) - 1,
        "verified_native_library_count": len(native),
        "full_correctness_campaign_sha256": campaign_digest,
        "full_correctness_campaign_steps": 22,
        "c_full_correctness_campaign_sha256": C_CAMPAIGN_SHA256,
        "c_full_correctness_campaign_steps": 22,
        "zig_full_correctness_campaign_sha256": ZIG_CAMPAIGN_SHA256,
        "zig_full_correctness_campaign_steps": 22,
        "rust_deep_contract_sha256": deep_digest,
        "rust_deep_contract_checks": 393,
        "rust_observability_sha256": observability_digest,
        "rust_observability_checks": 479,
        "rust_observability_binder_checks": 34,
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
        raise AuditError("the unique v8 public-practice integrity output already exists") from error
    except OSError as error:
        raise AuditError("cannot persist the unique v8 public-practice integrity output") from error
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
        "c_full_correctness_campaign_steps": 22,
        "zig_full_correctness_campaign_steps": 22,
        "rust_deep_contract_sha256": deep_digest,
        "rust_deep_contract_checks": 393,
        "rust_observability_sha256": observability_digest,
        "rust_observability_checks": 479,
        "rust_observability_binder_checks": 34,
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
        "unchanged_reference_candidates": list(UNCHANGED_REFERENCE_CANDIDATES),
        "output": original.display_path(output_path),
        "sha256": hashlib.sha256(encoded).hexdigest(), "failed": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("self-test", help="run only frozen candidate-free synthetic and historical corruption controls")
    check = commands.add_parser("verify", help="replay the sole actually qualified Rust capture-hoist public practice run")
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
