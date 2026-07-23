#!/usr/bin/env python3
"""Independently replay the one-off Rust-owned-prefix public practice run.

All four prior experiments are immutable.  Only their candidate-free raw,
bootstrap, history, and synthetic-control helpers are reused.  This program
does not import a candidate, time an engine, or access a held-out benchmark.
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


ROOT = original.ROOT
EVIDENCE = original.EVIDENCE
SCHEMA = "rebar-v7-multi-candidate-practice-integrity-v5"
SLOT = "three-qualified-engines-rust-owned-common-prefix-v5"
PREFIX = "three-qualified-engines-public-practice-v5"
RAW_PATH = EVIDENCE / f"{PREFIX}-raw.jsonl.gz"
SUMMARY_PATH = EVIDENCE / f"{PREFIX}-summary.json"
OUTPUT_PATH = EVIDENCE / f"{PREFIX}-integrity.json"
CAMPAIGN_PATH = ROOT / "candidates/evidence/rust-v8-rust-owned-mandatory-common-prefix-sealed-campaign.json"
RUST_EDGE_PATH = ROOT / "candidates/evidence/rust-v7-edge-oracle-rust-owned-mandatory-common-prefix.json.gz"

V1_AUDITOR_SHA256 = "bc093f114fe15833cab8f7c8d59bd1970345b6ddb47bc33349854be1af7f0ded"
V2_AUDITOR_SHA256 = "4dee19924cb0e4312ff9b62c70dd105f1f49aa4a7f3eeedaa650d9f9f5d853d4"
V3_AUDITOR_SHA256 = "1bd6a03a0d8e25b3041a31e095f97647f7d2e0b317e8ae3b8adf9b25113aefd4"
V4_AUDITOR_SHA256 = "6b6cb39cdab33e5b6ce2c88568925885514590f26f27c1990b24b598ac555dc0"
V1_INTEGRITY_SHA256 = "8739803b6cd020b8b4f663223435fd1e39ef5603e90195b2a268a9fa7fbc0340"
V2_INTEGRITY_SHA256 = "82ef917ca82ba124af6311f3bf10398a2a040286ed06430919bbdd26dd61e057"
V3_INTEGRITY_SHA256 = "aa1921230845a01aa03d607bd8609b3475dc659cacda5e6135d8b7064ed60c22"
V4_INTEGRITY_SHA256 = "7bfb360fa570510d585c923345f00162da92a3a7cd6379528ad981b1ec003174"
V5_AUDIT_SHA256 = "4856f38bac3f54a1c0758e4c32c8d738a55128f932ecbc451025ea170108709d"
V5_SUMMARY_SHA256 = "98c611410895f831d0b97a1677723186cc1e06d438d3437bfec9519743b1ad69"
V5_COMPRESSED_RAW_SHA256 = "bfb82c4ac326163db2d3ae463817e2a56821e0c5f1b72ee693c26690c23e4a7d"
V5_RAW_SHA256 = "8a1b998c140046ac3b795cf912c5ccb958ac182d44b1a49b7f055aed25f80eb2"
RUST_CAMPAIGN_SHA256 = "9543fbbb39bbf42f5329a051b8441e69c756a495287a06c2f877c757b3ec5688"
ZIG_CAMPAIGN_SHA256 = "f89fe9081421d28a291feab1b664c21a7c372762a548569856c6572e4a23eba6"
RUST_EDGE_COMPRESSED_SHA256 = "21d664fdb3d7b9575f3ae82029b88e17947be704316f1263e7106b2164cc8efe"
RUST_EDGE_PAYLOAD_SHA256 = "13e3aaa028a8ebd5e7b345db333afbe082e5b6ac7bd6d72709f9071af3430628"
OWNED_RUST_SOURCE_SHA256 = "d6e0cd31b06cd4edb1af7f8fb7409c23027289818934b35a03d5b3cc17444784"
OWNED_RUST_ENGINE_SHA256 = "37ab3d8598bdbbe9097810a35b54f3558fd0473db903d0a0c6b6527068dbf7cb"
PREVIOUS_RUST_SOURCE_SHA256 = "ef845cf6bbe3897224dbc4809ffeaea98f671f01b6d7c5d17eaf43c65f0ae54f"
PREVIOUS_RUST_ENGINE_SHA256 = "d1a0983b09ec3fe848b91f0df82be6b5d65cda77c37d2870b4dba0bb37527b5e"
UNCHANGED_RUST_BRIDGE_SOURCE_SHA256 = "83afb5a709a6d0ea1701dfd64db30644edbf2cb0276c2db731a8119cfd52d8ed"
UNCHANGED_RUST_BRIDGE_SHA256 = "1f072e81ba9339a8b2e52a7e93b7bcde791c4d518620b6bd760af67c7c89af34"
INITIAL_FAILURE_SHA256 = "ccaf3813b29badcf80c552dc0d850f83a2ca122cc3cc3057576dd519aed4f088"
EXPECTED_REGRESSIONS = 407
UNCHANGED_REFERENCE_CANDIDATES = [
    "re", "candidates.vm_candidate", "candidates.zig_candidate"
]


AuditError = original.AuditError
require = original.require


def validate_version_identity(summary: dict, plan: dict, profile: original.Profile, raw_path: Path) -> None:
    original.validate_header(summary, plan, profile, None)
    require(summary.get("exclusive_slot") == SLOT, "owned-prefix Rust was not measured in its one authorized practice slot")
    require(summary.get("raw_path") == str(raw_path.resolve()), "owned-prefix Rust names substituted public observations")
    require(
        summary.get("measurement") == "balanced practice diagnostic only; not a holdout result or final speed claim",
        "owned-prefix practice was misrepresented as final or held-out performance",
    )


def validate_historical_continuity(
    v1: dict, v2: dict, v3: dict, v4: dict,
    sources: dict[str, str], native: dict[str, str], measured: dict[str, str],
) -> None:
    require(v4.get("schema") == fourth.SCHEMA, "the historical Zig Stage-12 comparison was substituted")
    require(v4.get("result") == "PASS" and v4.get("failed") == 0, "the historical v4 experiment did not independently pass")
    require(v4.get("holdout_accessed") is False and v4.get("timing_performed") is False, "historical v4 results accessed or timed final workloads")
    require(v4.get("module_order") == list(original.MODULES), "historical v4 changed independent candidate families")
    require(v4.get("cases_per_candidate") == original.EXPECTED_CASES, "historical v4 changed the practice denominator")
    require(v4.get("trials_per_module_case") == original.EXPECTED_TRIALS, "historical v4 changed the paired trial denominator")
    require(v4.get("bootstrap_draws") == original.EXPECTED_BOOTSTRAPS, "historical v4 changed its bootstrap protocol")
    require(v4.get("frozen_plan_sha256") == original.EXPECTED_PLAN_SHA256, "historical v4 changed frozen public practice cases")
    require(v4.get("source_sha256") == V4_AUDITOR_SHA256, "the immutable v4 audit source changed")
    require(v4.get("historical_v1_integrity_sha256") == V1_INTEGRITY_SHA256, "historical v4 changed the v1 experiment")
    require(v4.get("historical_v2_integrity_sha256") == V2_INTEGRITY_SHA256, "historical v4 changed the v2 experiment")
    require(v4.get("historical_v3_integrity_sha256") == V3_INTEGRITY_SHA256, "historical v4 changed the v3 experiment")
    require(v4.get("from_scratch_audit_sha256") == fourth.V4_AUDIT_SHA256, "historical v4 changed the qualifying Zig12 canonical audit")
    require(v4.get("strict_regressions") == fourth.EXPECTED_REGRESSIONS, "historical v4 concealed its 402 actual substantial slowdowns")
    require(v4.get("full_correctness_campaign_sha256") == ZIG_CAMPAIGN_SHA256, "the unchanged Zig12 full correctness campaign changed")
    require(v4.get("full_correctness_campaign_steps") == 22, "the unchanged Zig12 engine did not pass all 22 stages")
    require(v4.get("initial_audit_failure_sha256") == INITIAL_FAILURE_SHA256, "the genuine historical Rust audit failure was removed")
    require(v4.get("rust_optimization_verified") is True, "the historical Rust qualification was omitted")
    require(v4.get("capacity16_optimization_verified") is True, "historical capacity-16 Rust was not independently qualified")
    require(v4.get("zig_optimization_verified") is True, "historical Zig12 was not independently qualified")

    old_sources = v4.get("qualified_source_fingerprints")
    old_native = v4.get("native_elf_fingerprints")
    old_measured = v4.get("candidate_binary_sha256_before")
    require(isinstance(old_sources, dict), "historical v4 qualified source fingerprints are missing")
    require(isinstance(old_native, dict), "historical v4 mapped native fingerprints are missing")
    require(isinstance(old_measured, dict), "historical v4 measured fingerprints are missing")
    require(v4.get("candidate_binary_sha256_after") == old_measured, "historical v4 production artifacts changed during timing")
    fourth.validate_historical_continuity(v1, v2, v3, old_sources, old_native, old_measured)

    changed_source = "candidates/rust/src/lib.rs"
    changed_engine = "candidates.rust_candidate:native-engine"
    changed_measured = {changed_engine, "candidates.rust_candidate:native-source"}
    require(set(sources) == set(old_sources), "owned-prefix Rust added or removed an independently audited source")
    require(set(native) == set(old_native), "owned-prefix Rust added or removed a mapped native binary")
    require(set(measured) == set(old_measured), "owned-prefix Rust added or removed a measured production role")
    for path, digest in old_sources.items():
        if path != changed_source:
            require(sources.get(path) == digest, f"the owned-engine experiment changed another production source: {path}")
    for role, digest in old_native.items():
        if role != changed_engine:
            require(native.get(role) == digest, f"the owned-engine experiment changed another native library: {role}")
    for role, digest in old_measured.items():
        if role not in changed_measured:
            require(measured.get(role) == digest, f"the owned-engine experiment changed another measured production role: {role}")

    require(old_sources.get(changed_source) == PREVIOUS_RUST_SOURCE_SHA256, "historical v4 did not contain the original owned Rust source")
    require(old_native.get(changed_engine) == PREVIOUS_RUST_ENGINE_SHA256, "historical v4 did not contain the original owned Rust engine")
    require(sources.get(changed_source) == OWNED_RUST_SOURCE_SHA256, "the current mandatory-prefix Rust source does not match its audited change")
    require(native.get(changed_engine) == OWNED_RUST_ENGINE_SHA256, "the current mandatory-prefix Rust engine does not match its audited change")
    require(measured.get(changed_engine) == OWNED_RUST_ENGINE_SHA256, "the measured Rust engine differs from the mapped owned engine")
    require(measured.get("candidates.rust_candidate:native-source") == OWNED_RUST_SOURCE_SHA256, "the measured Rust source differs from its qualified owned source")
    require(sources.get("candidates/rust/py_bridge.c") == UNCHANGED_RUST_BRIDGE_SOURCE_SHA256, "the supposedly unchanged Rust bridge source changed")
    require(native.get("candidates.rust_candidate:native-bridge") == UNCHANGED_RUST_BRIDGE_SHA256, "the supposedly unchanged Rust bridge binary changed")
    require(measured.get("candidates.rust_candidate:native-bridge") == UNCHANGED_RUST_BRIDGE_SHA256, "the supposedly unchanged measured Rust bridge changed")
    require(OWNED_RUST_SOURCE_SHA256 != PREVIOUS_RUST_SOURCE_SHA256, "the claimed owned Rust source did not actually change")
    require(OWNED_RUST_ENGINE_SHA256 != PREVIOUS_RUST_ENGINE_SHA256, "the claimed owned Rust engine did not actually change")


def validate_v5_edges(summary: dict, measured: dict[str, str]) -> list[dict]:
    require(original.sha256_file(original.EDGE_SOURCE_PATH) == original.EXPECTED_EDGE_SOURCE_SHA256, "the frozen four-engine matching oracle changed")
    stdlib, stdlib_digest = original.read_edge(original.STDLIB_EDGE_PATH, "frozen Python matching reference")
    original.validate_edge_document(stdlib, "re")
    require(stdlib_digest == original.EXPECTED_STDLIB_EDGE_SHA256, "the frozen Python matching reference changed")
    require(original.sha256_file(RUST_EDGE_PATH) == RUST_EDGE_COMPRESSED_SHA256, "the new owned Rust matching proof was substituted")
    require(original.sha256_file(fourth.ZIG_EDGE_PATH) == fourth.ZIG_EDGE_COMPRESSED_SHA256, "the preserved Zig12 matching proof was substituted")
    proofs = summary.get("verified_edge_oracles")
    require(isinstance(proofs, list) and len(proofs) == len(original.MODULES) - 1, "owned-prefix practice omitted an independent correctness proof")
    paths = {
        "candidates.rust_candidate": RUST_EDGE_PATH,
        "candidates.vm_candidate": second.C_EDGE_PATH,
        "candidates.zig_candidate": fourth.ZIG_EDGE_PATH,
    }
    for module, proof in zip(original.MODULES[1:], proofs, strict=True):
        require(isinstance(proof, dict) and proof.get("module") == module, "v5 matching proofs are missing, reordered, or substituted")
        path = paths[module]
        require(proof.get("path") == str(path.resolve()), f"{module} used an unexpected matching report")
        require(proof.get("correctness_checks") == 223_198, f"{module} dropped frozen Python matching checks")
        require(proof.get("actual_sha256") == original.EXPECTED_EDGE_ANSWER_SHA256, f"{module} disagrees with the frozen Python answers")
        require(proof.get("script_sha256") == original.EXPECTED_EDGE_SOURCE_SHA256, f"{module} altered the matching-oracle source")
        require(proof.get("stdlib_baseline_sha256") == stdlib_digest, f"{module} changed the pinned Python baseline")
        report, digest = original.read_edge(path, f"{module} owned-prefix practice matching proof")
        original.validate_edge_document(report, module)
        require(proof.get("report_sha256") == digest, f"{module} changed its exact correctness evidence after timing")
        if module == "candidates.rust_candidate":
            require(digest == RUST_EDGE_PAYLOAD_SHA256, "Rust did not use the exact owned-prefix matching qualification")
        if module == "candidates.zig_candidate":
            require(digest == fourth.ZIG_EDGE_PAYLOAD_SHA256, "the unchanged Zig12 candidate used another matching proof")
        artifacts = second.artifact_fingerprints(report.get("candidate_artifacts"), module)
        require(proof.get("candidate_artifacts") == artifacts, f"{module} timed an implementation not bound to its edge proof")
        for role, artifact in artifacts.items():
            if role == "public-python":
                key = f"{module}:module"
            elif module == "candidates.vm_candidate" and role == "native-bridge":
                key = f"{module}:native-engine"
            else:
                key = f"{module}:{role}"
            require(measured.get(key) == artifact["sha256"], f"{module} substituted a measured source or native engine")
    return proofs


def validate_rust_campaign(campaign: dict, measured: dict[str, str]) -> None:
    require(campaign.get("schema") == "rebar-rust-campaign-gate-v1", "the owned-prefix correctness campaign changed schema")
    require(campaign.get("candidate") == "candidates.rust_candidate", "the owned-prefix campaign qualified another candidate")
    require(campaign.get("passed") is True, "the owned-prefix Rust full correctness campaign did not pass")
    require(campaign.get("holdout_accessed") is False, "the owned-prefix correctness campaign accessed held-out cases")
    require(campaign.get("timing_performed") is False and campaign.get("performance") == "NOT MEASURED", "the owned-prefix correctness campaign performed benchmark timing")
    require(campaign.get("required_correctness_step_count") == 22, "the owned-prefix Rust campaign changed its required stages")
    stages = campaign.get("steps")
    require(isinstance(stages, list) and len(stages) == 22, "the owned-prefix campaign omitted a correctness stage")
    require(all(isinstance(stage, dict) and stage.get("passed") is True for stage in stages), "the owned-prefix campaign contains an unexplained mismatch or crash")
    require(campaign.get("pinned_cpython") == "3.14.6", "the owned-prefix campaign changed its Python baseline")
    require(campaign.get("python_executable") == str(original.PINNED_PYTHON), "the owned-prefix campaign changed its Python executable")
    require(campaign.get("mode") == "sealed-practice-only", "the owned-prefix campaign weakened its isolated correctness mode")
    edge = campaign.get("edge_oracle")
    require(isinstance(edge, dict), "the owned-prefix full campaign omitted its independent edge proof")
    require(edge.get("archive_sha256") == RUST_EDGE_COMPRESSED_SHA256, "the owned-prefix campaign referenced a different compressed correctness proof")
    require(edge.get("path") == str(RUST_EDGE_PATH.resolve()), "the owned-prefix campaign referenced another candidate proof")
    require(edge.get("checks") == 223_198 and edge.get("failed") == 0, "the owned-prefix campaign dropped or failed frozen edge checks")
    require(edge.get("module") == "candidates.rust_candidate", "the owned-prefix campaign edge belongs to another candidate")
    complete = second.artifact_fingerprints(campaign.get("native_artifacts"), "candidates.rust_candidate")
    qualified = second.artifact_fingerprints(edge.get("candidate_artifacts"), "candidates.rust_candidate")
    require(complete == qualified, "the owned-prefix full campaign and independent edge qualified different production artifacts")
    for role, artifact in complete.items():
        key = "candidates.rust_candidate:module" if role == "public-python" else f"candidates.rust_candidate:{role}"
        require(measured.get(key) == artifact["sha256"], "the timed Rust differs from the engine that passed all 22 stages")


def synthetic_histories() -> tuple[dict, dict, dict, dict, dict[str, str], dict[str, str], dict[str, str]]:
    v1, v2, v3, old_sources, old_native, old_measured = fourth.synthetic_histories()
    rust_path = "candidates/rust/src/lib.rs"
    rust_role = "candidates.rust_candidate:native-engine"
    rust_source_role = "candidates.rust_candidate:native-source"
    bridge_path = "candidates/rust/py_bridge.c"
    bridge_role = "candidates.rust_candidate:native-bridge"
    for document in (v1, v2, v3):
        document["qualified_source_fingerprints"][rust_path] = PREVIOUS_RUST_SOURCE_SHA256
        document["native_elf_fingerprints"][rust_role] = PREVIOUS_RUST_ENGINE_SHA256
        document["candidate_binary_sha256_before"][rust_role] = PREVIOUS_RUST_ENGINE_SHA256
        document["candidate_binary_sha256_after"][rust_role] = PREVIOUS_RUST_ENGINE_SHA256
        document["candidate_binary_sha256_before"][rust_source_role] = PREVIOUS_RUST_SOURCE_SHA256
        document["candidate_binary_sha256_after"][rust_source_role] = PREVIOUS_RUST_SOURCE_SHA256
    old_sources[rust_path] = PREVIOUS_RUST_SOURCE_SHA256
    old_sources[bridge_path] = UNCHANGED_RUST_BRIDGE_SOURCE_SHA256
    old_native[rust_role] = PREVIOUS_RUST_ENGINE_SHA256
    old_native[bridge_role] = UNCHANGED_RUST_BRIDGE_SHA256
    old_measured[rust_role] = PREVIOUS_RUST_ENGINE_SHA256
    old_measured[rust_source_role] = PREVIOUS_RUST_SOURCE_SHA256
    old_measured[bridge_role] = UNCHANGED_RUST_BRIDGE_SHA256
    v4 = {
        "schema": fourth.SCHEMA, "result": "PASS", "failed": 0,
        "holdout_accessed": False, "timing_performed": False,
        "module_order": list(original.MODULES),
        "cases_per_candidate": original.EXPECTED_CASES,
        "trials_per_module_case": original.EXPECTED_TRIALS,
        "bootstrap_draws": original.EXPECTED_BOOTSTRAPS,
        "frozen_plan_sha256": original.EXPECTED_PLAN_SHA256,
        "source_sha256": V4_AUDITOR_SHA256,
        "historical_v1_integrity_sha256": V1_INTEGRITY_SHA256,
        "historical_v2_integrity_sha256": V2_INTEGRITY_SHA256,
        "historical_v3_integrity_sha256": V3_INTEGRITY_SHA256,
        "from_scratch_audit_sha256": fourth.V4_AUDIT_SHA256,
        "strict_regressions": fourth.EXPECTED_REGRESSIONS,
        "full_correctness_campaign_sha256": ZIG_CAMPAIGN_SHA256,
        "full_correctness_campaign_steps": 22,
        "initial_audit_failure_sha256": INITIAL_FAILURE_SHA256,
        "rust_optimization_verified": True,
        "capacity16_optimization_verified": True,
        "zig_optimization_verified": True,
        "qualified_source_fingerprints": dict(old_sources),
        "native_elf_fingerprints": dict(old_native),
        "candidate_binary_sha256_before": dict(old_measured),
        "candidate_binary_sha256_after": dict(old_measured),
    }
    sources = {**old_sources, rust_path: OWNED_RUST_SOURCE_SHA256}
    native = {**old_native, rust_role: OWNED_RUST_ENGINE_SHA256}
    measured = {
        **old_measured,
        rust_role: OWNED_RUST_ENGINE_SHA256,
        rust_source_role: OWNED_RUST_SOURCE_SHA256,
    }
    return v1, v2, v3, v4, sources, native, measured


def self_test() -> dict:
    inherited = fourth.self_test()
    require(inherited.get("result") == "PASS", "the immutable v4 replay synthetic controls failed")
    earlier = inherited.get("poisoned_controls")
    require(isinstance(earlier, list) and len(earlier) >= 89, "the owned-prefix replay dropped its 89 inherited poison controls")
    plan, sample, _compressed, profile = original.synthetic_evidence()
    sample["exclusive_slot"] = SLOT
    sample["raw_path"] = str(RAW_PATH.resolve())
    sample["measurement"] = "balanced practice diagnostic only; not a holdout result or final speed claim"
    validate_version_identity(sample, plan, profile, RAW_PATH)
    v1, v2, v3, v4, sources, native, measured = synthetic_histories()
    validate_historical_continuity(v1, v2, v3, v4, sources, native, measured)
    controls = [*earlier]

    def reject(name: str, action: object) -> None:
        try:
            action()  # type: ignore[operator]
        except (AuditError, KeyError, ValueError, TypeError, OverflowError):
            controls.append({"name": name, "passed": True})
            return
        raise AuditError(f"the owned-prefix synthetic replay accepted corrupted evidence: {name}")

    def poison_version(key: str, value: object) -> None:
        poisoned = copy.deepcopy(sample)
        poisoned[key] = value
        validate_version_identity(poisoned, plan, profile, RAW_PATH)

    def poison_history(which: str, key: str, value: object) -> None:
        first = copy.deepcopy(v1)
        second_doc = copy.deepcopy(v2)
        third_doc = copy.deepcopy(v3)
        fourth_doc = copy.deepcopy(v4)
        current_sources = dict(sources)
        current_native = dict(native)
        current_measured = dict(measured)
        mappings = {
            "v1": first, "v2": second_doc, "v3": third_doc, "v4": fourth_doc,
            "v4-sources": fourth_doc["qualified_source_fingerprints"],
            "v4-native": fourth_doc["native_elf_fingerprints"],
            "sources": current_sources, "native": current_native,
            "measured": current_measured,
        }
        mappings[which][key] = value
        validate_historical_continuity(
            first, second_doc, third_doc, fourth_doc,
            current_sources, current_native, current_measured,
        )

    reject("v1-slot-cross-contamination", lambda: poison_version("exclusive_slot", original.EXPECTED_SLOT))
    reject("v2-slot-cross-contamination", lambda: poison_version("exclusive_slot", second.SLOT))
    reject("v3-slot-cross-contamination", lambda: poison_version("exclusive_slot", third.SLOT))
    reject("v4-slot-cross-contamination", lambda: poison_version("exclusive_slot", fourth.SLOT))
    reject("v5-filename-incorrectly-treated-as-slot", lambda: poison_version("exclusive_slot", PREFIX))
    reject("v1-raw-cross-contamination", lambda: poison_version("raw_path", str(original.RAW_PATH.resolve())))
    reject("v2-raw-cross-contamination", lambda: poison_version("raw_path", str(second.RAW_PATH.resolve())))
    reject("v3-raw-cross-contamination", lambda: poison_version("raw_path", str(third.RAW_PATH.resolve())))
    reject("v4-raw-cross-contamination", lambda: poison_version("raw_path", str(fourth.RAW_PATH.resolve())))
    reject("practice-falsely-reported-as-final", lambda: poison_version("measurement", "final holdout benchmark"))
    reject("v1-history-replaced-with-v5", lambda: poison_history("v1", "schema", SCHEMA))
    reject("v2-history-replaced-with-v5", lambda: poison_history("v2", "schema", SCHEMA))
    reject("v3-history-replaced-with-v5", lambda: poison_history("v3", "schema", SCHEMA))
    reject("v4-history-replaced-with-v5", lambda: poison_history("v4", "schema", SCHEMA))
    reject("v4-actual-402-regressions-hidden", lambda: poison_history("v4", "strict_regressions", fourth.EXPECTED_REGRESSIONS - 1))
    reject("preserved-zig12-campaign-substituted", lambda: poison_history("v4", "full_correctness_campaign_sha256", "0" * 64))
    reject("preserved-rust-first-failure-concealed", lambda: poison_history("v4", "initial_audit_failure_sha256", "0" * 64))
    reject("previous-rust-owned-source-substituted", lambda: poison_history("v4-sources", "candidates/rust/src/lib.rs", OWNED_RUST_SOURCE_SHA256))
    reject("previous-rust-engine-substituted", lambda: poison_history("v4-native", "candidates.rust_candidate:native-engine", OWNED_RUST_ENGINE_SHA256))
    reject("owned-prefix-rust-source-not-new", lambda: poison_history("sources", "candidates/rust/src/lib.rs", PREVIOUS_RUST_SOURCE_SHA256))
    reject("owned-prefix-rust-engine-not-new", lambda: poison_history("native", "candidates.rust_candidate:native-engine", PREVIOUS_RUST_ENGINE_SHA256))
    reject("owned-prefix-measured-source-not-new", lambda: poison_history("measured", "candidates.rust_candidate:native-source", PREVIOUS_RUST_SOURCE_SHA256))
    reject("unchanged-rust-bridge-source-substituted", lambda: poison_history("sources", "candidates/rust/py_bridge.c", "0" * 64))
    reject("unchanged-rust-bridge-binary-substituted", lambda: poison_history("native", "candidates.rust_candidate:native-bridge", "0" * 64))
    reject("unchanged-stage12-zig-source-substituted", lambda: poison_history("sources", "candidates/zig/py_bridge.c", "0" * 64))
    reject("unchanged-stage12-zig-bridge-substituted", lambda: poison_history("native", "candidates.zig_candidate:native-bridge", "0" * 64))
    reject("unchanged-stage12-zig-engine-substituted", lambda: poison_history("native", "candidates.zig_candidate:native-engine", "0" * 64))
    reject("unchanged-c-source-substituted", lambda: poison_history("sources", "candidates/_vm_native.c", "0" * 64))
    reject("unchanged-c-native-substituted", lambda: poison_history("native", "candidates.vm_candidate:native-engine", "0" * 64))
    reject("unchanged-python-baseline-substituted", lambda: poison_history("measured", "re:module", "0" * 64))
    require(len(controls) >= 119, "owned-prefix verification omitted inherited or changed-engine isolation controls")
    return {
        "schema": SCHEMA + "-self-test", "result": "PASS", "synthetic_only": True,
        "holdout_accessed": False, "timing_performed": False,
        "historical_v1_auditor_sha256": V1_AUDITOR_SHA256,
        "historical_v2_auditor_sha256": V2_AUDITOR_SHA256,
        "historical_v3_auditor_sha256": V3_AUDITOR_SHA256,
        "historical_v4_auditor_sha256": V4_AUDITOR_SHA256,
        "inherited_poisoned_control_count": len(earlier),
        "poisoned_control_count": len(controls), "poisoned_controls": controls,
        "unchanged_reference_candidates": list(UNCHANGED_REFERENCE_CANDIDATES),
        "failed": 0,
    }


def verify(raw_path: Path, summary_path: Path, audit_path: Path, output_path: Path) -> dict:
    require(platform.python_implementation() == "CPython" and tuple(sys.version_info[:3]) == (3, 14, 6), "owned-prefix replay requires exact stable CPython 3.14.6")
    require(Path(sys.executable).resolve() == original.PINNED_PYTHON.resolve(), "owned-prefix replay requires its exact pinned baseline executable")
    require(raw_path.resolve() == RAW_PATH.resolve(), "v5 may not replace or overwrite historical raw practice observations")
    require(summary_path.resolve() == SUMMARY_PATH.resolve(), "v5 may not replace or overwrite historical practice summaries")
    require(audit_path.resolve() == original.AUDIT_PATH.resolve(), "v5 may not substitute its actual native-independence audit")
    require(output_path.resolve() == OUTPUT_PATH.resolve(), "v5 may not overwrite or redirect historical integrity reports")
    require(not output_path.exists(), "the unique owned-prefix practice integrity report already exists")
    require(not any(name in sys.modules for name in original.MODULES[1:]), "owned-prefix independent verification imported a candidate")
    for module, expected in (
        (original, V1_AUDITOR_SHA256),
        (second, V2_AUDITOR_SHA256),
        (third, V3_AUDITOR_SHA256),
        (fourth, V4_AUDITOR_SHA256),
    ):
        require(original.sha256_file(Path(module.__file__).resolve()) == expected, "an immutable previous public-practice verifier source changed")
    require(original.sha256_file(third.INITIAL_FAILURE_PATH) == INITIAL_FAILURE_SHA256, "the preserved initial Rust correctness failure was removed or changed")

    profile = original.Profile()
    plan = original.read_json(original.PLAN_PATH, "immutable 624-case public practice plan", original.EXPECTED_PLAN_SHA256)
    require(plan.get("expected_sha256") == original.EXPECTED_FROZEN_ANSWER_SHA256, "owned-prefix Rust changed the frozen practice correctness answers")
    original.validate_plan(plan, profile)
    summary = original.read_json(summary_path, "one-shot owned-prefix Rust practice summary", V5_SUMMARY_SHA256)
    validate_version_identity(summary, plan, profile, raw_path)
    require(summary.get("compressed_raw_sha256") == V5_COMPRESSED_RAW_SHA256, "the one-off v5 gzip observations changed")
    require(summary.get("raw_sha256") == V5_RAW_SHA256, "the one-off v5 decompressed observations changed")
    require(original.sha256_file(raw_path) == V5_COMPRESSED_RAW_SHA256, "the exact compressed v5 raw observation bytes changed")

    audit = original.read_json(audit_path, "owned-prefix five-library from-scratch audit", V5_AUDIT_SHA256)
    sources, native = original.validate_independence(audit)
    measured = original.validate_measured_fingerprints(summary, sources, native)
    v1 = original.read_json(original.OUTPUT_PATH, "immutable original four-way experiment", V1_INTEGRITY_SHA256)
    v2 = original.read_json(second.OUTPUT_PATH, "immutable historical v2 experiment", V2_INTEGRITY_SHA256)
    v3 = original.read_json(third.OUTPUT_PATH, "immutable historical v3 experiment", V3_INTEGRITY_SHA256)
    v4 = original.read_json(fourth.OUTPUT_PATH, "immutable historical v4 Zig12 experiment", V4_INTEGRITY_SHA256)
    validate_historical_continuity(v1, v2, v3, v4, sources, native, measured)
    edges = validate_v5_edges(summary, measured)
    rust_campaign = original.read_json(CAMPAIGN_PATH, "passing complete owned-prefix Rust correctness campaign", RUST_CAMPAIGN_SHA256)
    validate_rust_campaign(rust_campaign, measured)
    zig_campaign = original.read_json(fourth.CAMPAIGN_PATH, "unchanged complete Zig Stage-12 correctness campaign", ZIG_CAMPAIGN_SHA256)
    fourth.validate_zig_campaign(zig_campaign, sources, measured)

    try:
        with raw_path.open("rb") as source:
            observations = original.read_observations(source, V5_COMPRESSED_RAW_SHA256, summary, plan, profile)
    except OSError as error:
        raise AuditError("cannot open the exact one-off owned-prefix practice observations") from error
    results, rankings = original.recompute_results(plan, observations, profile)
    regressions = original.validate_results(summary, results, rankings, profile)
    require(len(regressions) == EXPECTED_REGRESSIONS, "the owned-prefix experiment concealed or changed its 407 actual substantial losses")
    controls = self_test()
    require(not any(name in sys.modules for name in original.MODULES[1:]), "the owned-prefix independent replay imported a candidate")

    document = {
        "schema": SCHEMA, "result": "PASS", "holdout_accessed": False,
        "timing_performed": False,
        "measurement": "independent replay of one owned-Rust-prefix four-way public practice run; not final or held-out performance",
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
        "summary_sha256": V5_SUMMARY_SHA256,
        "compressed_raw_sha256": V5_COMPRESSED_RAW_SHA256,
        "raw_sha256": V5_RAW_SHA256,
        "frozen_plan_sha256": original.EXPECTED_PLAN_SHA256,
        "source_sha256": original.sha256_file(Path(__file__).resolve()),
        "historical_v1_auditor_sha256": V1_AUDITOR_SHA256,
        "historical_v2_auditor_sha256": V2_AUDITOR_SHA256,
        "historical_v3_auditor_sha256": V3_AUDITOR_SHA256,
        "historical_v4_auditor_sha256": V4_AUDITOR_SHA256,
        "historical_v1_integrity_sha256": V1_INTEGRITY_SHA256,
        "historical_v2_integrity_sha256": V2_INTEGRITY_SHA256,
        "historical_v3_integrity_sha256": V3_INTEGRITY_SHA256,
        "historical_v4_integrity_sha256": V4_INTEGRITY_SHA256,
        "from_scratch_audit_sha256": V5_AUDIT_SHA256,
        "from_scratch_control_count": 76,
        "verified_independent_engine_count": len(original.MODULES) - 1,
        "verified_native_library_count": len(native),
        "full_correctness_campaign_sha256": RUST_CAMPAIGN_SHA256,
        "full_correctness_campaign_steps": 22,
        "zig_full_correctness_campaign_sha256": ZIG_CAMPAIGN_SHA256,
        "zig_full_correctness_campaign_steps": 22,
        "initial_audit_failure_sha256": INITIAL_FAILURE_SHA256,
        "rust_optimization_verified": True,
        "capacity16_optimization_verified": True,
        "zig_optimization_verified": True,
        "mandatory_prefix_optimization_verified": True,
        "unchanged_rust_bridge_verified": True,
        "unchanged_reference_candidates": list(UNCHANGED_REFERENCE_CANDIDATES),
        "qualified_source_fingerprints": sources,
        "native_elf_fingerprints": native,
        "candidate_binary_sha256_before": summary["candidate_binary_sha256_before"],
        "candidate_binary_sha256_after": summary["candidate_binary_sha256_after"],
        "verified_edge_oracles": edges,
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
        raise AuditError("the unique owned-prefix integrity result already exists") from error
    except OSError as error:
        raise AuditError("cannot persist the unique owned-prefix integrity result") from error
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
        "zig_full_correctness_campaign_steps": 22,
        "poisoned_control_count": controls["poisoned_control_count"],
        "rust_optimization_verified": True,
        "capacity16_optimization_verified": True,
        "zig_optimization_verified": True,
        "mandatory_prefix_optimization_verified": True,
        "unchanged_rust_bridge_verified": True,
        "unchanged_reference_candidates": list(UNCHANGED_REFERENCE_CANDIDATES),
        "output": original.display_path(output_path),
        "sha256": hashlib.sha256(encoded).hexdigest(), "failed": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("self-test", help="run only candidate-free synthetic version and changed-engine controls")
    check = commands.add_parser("verify", help="replay the exact source-bound Rust owned-prefix practice experiment")
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
