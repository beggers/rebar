#!/usr/bin/env python3
"""Independently replay the one-off, fully qualified C Stage-20 run.

The first five practice experiments remain immutable.  Their candidate-free
raw, bootstrap, provenance, and synthetic helpers are reused without importing
an engine, executing a benchmark, or accessing the final holdout.
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


ROOT = original.ROOT
EVIDENCE = original.EVIDENCE
SCHEMA = "rebar-v7-multi-candidate-practice-integrity-v6"
SLOT = "three-qualified-engines-c-stage-20-native-scanner-cmethod-v6"
PREFIX = "three-qualified-engines-public-practice-v6"
RAW_PATH = EVIDENCE / f"{PREFIX}-raw.jsonl.gz"
SUMMARY_PATH = EVIDENCE / f"{PREFIX}-summary.json"
OUTPUT_PATH = EVIDENCE / f"{PREFIX}-integrity.json"
CAMPAIGN_PATH = ROOT / "candidates/evidence/rust-v8-vm-stage-20-native-scanner-cmethod-sealed-campaign.json"
C_EDGE_PATH = ROOT / "candidates/evidence/rust-v8-edge-oracle-vm-deep-stage-20-native-scanner-cmethod.json.gz"

V1_AUDITOR_SHA256 = "bc093f114fe15833cab8f7c8d59bd1970345b6ddb47bc33349854be1af7f0ded"
V2_AUDITOR_SHA256 = "4dee19924cb0e4312ff9b62c70dd105f1f49aa4a7f3eeedaa650d9f9f5d853d4"
V3_AUDITOR_SHA256 = "1bd6a03a0d8e25b3041a31e095f97647f7d2e0b317e8ae3b8adf9b25113aefd4"
V4_AUDITOR_SHA256 = "6b6cb39cdab33e5b6ce2c88568925885514590f26f27c1990b24b598ac555dc0"
V5_AUDITOR_SHA256 = "7236508d80094d5c7a4fd3e33725b6e9485b73b7cdacd33b6a72d2ccc4cf6590"
V1_INTEGRITY_SHA256 = "8739803b6cd020b8b4f663223435fd1e39ef5603e90195b2a268a9fa7fbc0340"
V2_INTEGRITY_SHA256 = "82ef917ca82ba124af6311f3bf10398a2a040286ed06430919bbdd26dd61e057"
V3_INTEGRITY_SHA256 = "aa1921230845a01aa03d607bd8609b3475dc659cacda5e6135d8b7064ed60c22"
V4_INTEGRITY_SHA256 = "7bfb360fa570510d585c923345f00162da92a3a7cd6379528ad981b1ec003174"
V5_INTEGRITY_SHA256 = "015a2f9e3ceebd3792c4de62828c2d63fbafd7a5f866c9513b60b964a974712e"
V6_AUDIT_SHA256 = "f875068b829482d0c5dd28290a5706dd0a5c0ed91018b857cee82b6defe40f0a"
V6_SUMMARY_SHA256 = "22689cf92175274f935df81f51b07b4f2a0a90bafad3ae1bd2b0e9f905579fce"
V6_COMPRESSED_RAW_SHA256 = "9e38b7a20435d1479d88e0456ffb2849337983c7957ddad238c021d69c4913ee"
V6_RAW_SHA256 = "8098869ed442741e132567516341c73d78bef59db0e901280a940af40e25521e"
C_CAMPAIGN_SHA256 = "c211d826032fed60c30024beb6de66c3e20b08fdcb936b53393d0a5fdba09721"
RUST_CAMPAIGN_SHA256 = "9543fbbb39bbf42f5329a051b8441e69c756a495287a06c2f877c757b3ec5688"
ZIG_CAMPAIGN_SHA256 = "f89fe9081421d28a291feab1b664c21a7c372762a548569856c6572e4a23eba6"
C_EDGE_COMPRESSED_SHA256 = "829c39f4ea838b229f4c7465e239e70509d9187de75a7d2f236da959c82f1343"
C_EDGE_PAYLOAD_SHA256 = "2f80bc9b0a12959455b9422d89f047903b8073d5d75e5e1a814c0922049d336f"
STAGE20_C_SOURCE_SHA256 = "696925d94c63fed442d547e9a0fbcce9dda271eae633130d01cdb4e68ea4af2f"
STAGE20_C_NATIVE_SHA256 = "0e4d194fc14a2e307dd765ec5632acbe7b4192a0b2a74833a1126fbd0e5b5b91"
STAGE19_C_SOURCE_SHA256 = "bb4df5960e169c24e772d9fa0a193fcc6a9e8d31ab60d20aabb48ab07e5fe06d"
STAGE19_C_NATIVE_SHA256 = "d3ec19d66161f789056f2146c3abadccb98fa7bfd979fd66e1fb68540ad0f078"
INITIAL_FAILURE_SHA256 = "ccaf3813b29badcf80c552dc0d850f83a2ca122cc3cc3057576dd519aed4f088"
EXPECTED_REGRESSIONS = 407
UNCHANGED_REFERENCE_CANDIDATES = [
    "re", "candidates.rust_candidate", "candidates.zig_candidate"
]


AuditError = original.AuditError
require = original.require


def validate_version_identity(summary: dict, plan: dict, profile: original.Profile, raw_path: Path) -> None:
    original.validate_header(summary, plan, profile, None)
    require(summary.get("exclusive_slot") == SLOT, "C Stage-20 did not use its one authorized four-engine practice slot")
    require(summary.get("raw_path") == str(raw_path.resolve()), "C Stage-20 substituted public raw observations")
    require(
        summary.get("measurement") == "balanced practice diagnostic only; not a holdout result or final speed claim",
        "C Stage-20 public practice was misrepresented as final speed",
    )


def validate_historical_continuity(
    v1: dict, v2: dict, v3: dict, v4: dict, v5: dict,
    sources: dict[str, str], native: dict[str, str], measured: dict[str, str],
) -> None:
    require(v5.get("schema") == fifth.SCHEMA, "the historical owned-prefix Rust result was substituted")
    require(v5.get("result") == "PASS" and v5.get("failed") == 0, "historical v5 evidence did not pass independent verification")
    require(v5.get("holdout_accessed") is False and v5.get("timing_performed") is False, "historical v5 verifier accessed or timed final performance")
    require(v5.get("module_order") == list(original.MODULES), "historical v5 changed independent candidate families")
    require(v5.get("cases_per_candidate") == original.EXPECTED_CASES, "historical v5 changed the practice denominator")
    require(v5.get("trials_per_module_case") == original.EXPECTED_TRIALS, "historical v5 changed paired trials")
    require(v5.get("bootstrap_draws") == original.EXPECTED_BOOTSTRAPS, "historical v5 changed confidence draws")
    require(v5.get("frozen_plan_sha256") == original.EXPECTED_PLAN_SHA256, "historical v5 changed its frozen public cases")
    require(v5.get("source_sha256") == V5_AUDITOR_SHA256, "the immutable v5 verifier changed")
    for key, expected in (
        ("historical_v1_integrity_sha256", V1_INTEGRITY_SHA256),
        ("historical_v2_integrity_sha256", V2_INTEGRITY_SHA256),
        ("historical_v3_integrity_sha256", V3_INTEGRITY_SHA256),
        ("historical_v4_integrity_sha256", V4_INTEGRITY_SHA256),
    ):
        require(v5.get(key) == expected, f"historical v5 changed frozen previous evidence: {key}")
    require(v5.get("from_scratch_audit_sha256") == fifth.V5_AUDIT_SHA256, "historical v5 changed its source-independent canonical audit")
    require(v5.get("strict_regressions") == fifth.EXPECTED_REGRESSIONS, "historical v5 concealed its actual 407 slowdowns")
    require(v5.get("full_correctness_campaign_sha256") == RUST_CAMPAIGN_SHA256, "the preserved owned-prefix Rust full campaign changed")
    require(v5.get("full_correctness_campaign_steps") == 22, "preserved owned-prefix Rust omitted a correctness stage")
    require(v5.get("zig_full_correctness_campaign_sha256") == ZIG_CAMPAIGN_SHA256, "the preserved Stage-12 Zig full campaign changed")
    require(v5.get("zig_full_correctness_campaign_steps") == 22, "preserved Stage-12 Zig omitted a correctness stage")
    require(v5.get("initial_audit_failure_sha256") == INITIAL_FAILURE_SHA256, "the preserved real initial Rust audit failure was concealed")
    for flag in (
        "rust_optimization_verified", "capacity16_optimization_verified",
        "zig_optimization_verified", "mandatory_prefix_optimization_verified",
        "unchanged_rust_bridge_verified",
    ):
        require(v5.get(flag) is True, f"historical v5 dropped a qualified-source proof: {flag}")
    old_sources = v5.get("qualified_source_fingerprints")
    old_native = v5.get("native_elf_fingerprints")
    old_measured = v5.get("candidate_binary_sha256_before")
    require(isinstance(old_sources, dict), "historical v5 production-source fingerprints are missing")
    require(isinstance(old_native, dict), "historical v5 mapped-native fingerprints are missing")
    require(isinstance(old_measured, dict), "historical v5 timed-engine fingerprints are missing")
    require(v5.get("candidate_binary_sha256_after") == old_measured, "historical v5 changed a binary while timing")
    fifth.validate_historical_continuity(v1, v2, v3, v4, old_sources, old_native, old_measured)

    changed_source = "candidates/_vm_native.c"
    changed_native = "candidates.vm_candidate:native-engine"
    require(set(sources) == set(old_sources), "C Stage-20 added or omitted a production source")
    require(set(native) == set(old_native), "C Stage-20 added or omitted a mapped native regex library")
    require(set(measured) == set(old_measured), "C Stage-20 added or omitted a timed artifact")
    for path, digest in old_sources.items():
        if path != changed_source:
            require(sources.get(path) == digest, f"the C-only experiment changed another production source: {path}")
    for role, digest in old_native.items():
        if role != changed_native:
            require(native.get(role) == digest, f"the C-only experiment changed another mapped native engine: {role}")
    for role, digest in old_measured.items():
        if role != changed_native:
            require(measured.get(role) == digest, f"the C-only experiment changed another measured engine: {role}")
    require(old_sources.get(changed_source) == STAGE19_C_SOURCE_SHA256, "historical v5 did not include the genuine Stage-19 C source")
    require(old_native.get(changed_native) == STAGE19_C_NATIVE_SHA256, "historical v5 did not include the genuine Stage-19 C binary")
    require(sources.get(changed_source) == STAGE20_C_SOURCE_SHA256, "the optimized C source differs from its qualified Stage-20 source")
    require(native.get(changed_native) == STAGE20_C_NATIVE_SHA256, "the optimized C library differs from its qualified Stage-20 binary")
    require(measured.get(changed_native) == STAGE20_C_NATIVE_SHA256, "the measured C library differs from its verified loaded mapping")
    require(STAGE20_C_SOURCE_SHA256 != STAGE19_C_SOURCE_SHA256, "the proposed C source did not actually change")
    require(STAGE20_C_NATIVE_SHA256 != STAGE19_C_NATIVE_SHA256, "the proposed C native library did not actually change")


def validate_v6_edges(summary: dict, measured: dict[str, str]) -> list[dict]:
    require(original.sha256_file(original.EDGE_SOURCE_PATH) == original.EXPECTED_EDGE_SOURCE_SHA256, "the frozen four-candidate correctness oracle changed")
    baseline, baseline_digest = original.read_edge(original.STDLIB_EDGE_PATH, "frozen pinned Python edge report")
    original.validate_edge_document(baseline, "re")
    require(baseline_digest == original.EXPECTED_STDLIB_EDGE_SHA256, "the frozen Python matching baseline changed")
    require(original.sha256_file(C_EDGE_PATH) == C_EDGE_COMPRESSED_SHA256, "the exact new Stage-20 C correctness proof changed")
    require(original.sha256_file(fifth.RUST_EDGE_PATH) == fifth.RUST_EDGE_COMPRESSED_SHA256, "the unchanged owned-prefix Rust proof changed")
    require(original.sha256_file(fourth.ZIG_EDGE_PATH) == fourth.ZIG_EDGE_COMPRESSED_SHA256, "the unchanged Stage-12 Zig proof changed")
    proofs = summary.get("verified_edge_oracles")
    require(isinstance(proofs, list) and len(proofs) == len(original.MODULES) - 1, "the Stage-20 comparison omitted an independently qualified engine")
    paths = {
        "candidates.rust_candidate": fifth.RUST_EDGE_PATH,
        "candidates.vm_candidate": C_EDGE_PATH,
        "candidates.zig_candidate": fourth.ZIG_EDGE_PATH,
    }
    for module, proof in zip(original.MODULES[1:], proofs, strict=True):
        require(isinstance(proof, dict) and proof.get("module") == module, "Stage-20 edge proofs are missing, reordered, or cross-contaminated")
        path = paths[module]
        require(proof.get("path") == str(path.resolve()), f"{module} points at a substituted frozen edge proof")
        require(proof.get("correctness_checks") == 223_198, f"{module} dropped an independently frozen matching obligation")
        require(proof.get("actual_sha256") == original.EXPECTED_EDGE_ANSWER_SHA256, f"{module} failed to reproduce the frozen Python matching answers")
        require(proof.get("script_sha256") == original.EXPECTED_EDGE_SOURCE_SHA256, f"{module} substituted the matching-oracle source")
        require(proof.get("stdlib_baseline_sha256") == baseline_digest, f"{module} substituted the pinned Python baseline")
        report, digest = original.read_edge(path, f"{module} Stage-20 matching proof")
        original.validate_edge_document(report, module)
        require(proof.get("report_sha256") == digest, f"{module} changed its edge evidence after the one-shot timing")
        if module == "candidates.vm_candidate":
            require(digest == C_EDGE_PAYLOAD_SHA256, "the C edge report is not the exact qualified Stage-20 experiment")
        if module == "candidates.rust_candidate":
            require(digest == fifth.RUST_EDGE_PAYLOAD_SHA256, "the unchanged Rust candidate used a different owned-prefix proof")
        if module == "candidates.zig_candidate":
            require(digest == fourth.ZIG_EDGE_PAYLOAD_SHA256, "the unchanged Zig candidate used a different Stage-12 proof")
        artifacts = second.artifact_fingerprints(report.get("candidate_artifacts"), module)
        require(proof.get("candidate_artifacts") == artifacts, f"{module} measured artifacts that differ from its correctness qualification")
        for role, item in artifacts.items():
            if role == "public-python":
                key = f"{module}:module"
            elif module == "candidates.vm_candidate" and role == "native-bridge":
                key = f"{module}:native-engine"
            else:
                key = f"{module}:{role}"
            require(measured.get(key) == item["sha256"], f"{module} substituted its source, native binary, or engine family")
    return proofs


def validate_c_campaign(campaign: dict, sources: dict[str, str], measured: dict[str, str]) -> None:
    require(campaign.get("schema") == "rebar-rust-campaign-gate-v1", "the complete C Stage-20 campaign format changed")
    require(campaign.get("candidate") == "candidates.vm_candidate", "the C Stage-20 campaign qualified a different engine")
    require(campaign.get("passed") is True, "the complete C Stage-20 campaign did not pass")
    require(campaign.get("holdout_accessed") is False, "the complete C Stage-20 campaign accessed the final holdout")
    require(campaign.get("timing_performed") is False and campaign.get("performance") == "NOT MEASURED", "the C Stage-20 campaign timed an engine")
    require(campaign.get("required_correctness_step_count") == 22, "C Stage-20 changed the frozen complete correctness denominator")
    stages = campaign.get("steps")
    require(isinstance(stages, list) and len(stages) == 22, "C Stage-20 omitted a required correctness stage")
    require(all(isinstance(stage, dict) and stage.get("passed") is True for stage in stages), "C Stage-20 contains an unexplained failure or native crash")
    require(campaign.get("pinned_cpython") == "3.14.6", "C Stage-20 used a different Python correctness baseline")
    require(campaign.get("python_executable") == str(original.PINNED_PYTHON), "C Stage-20 used a different baseline executable")
    require(campaign.get("mode") == "sealed-practice-only", "C Stage-20 weakened its isolated campaign mode")
    edge = campaign.get("edge_oracle")
    require(isinstance(edge, dict), "C Stage-20 omitted its independent edge evidence")
    require(edge.get("archive_sha256") == C_EDGE_COMPRESSED_SHA256, "C Stage-20 changed its edge archive")
    require(edge.get("path") == str(C_EDGE_PATH.resolve()), "C Stage-20 used a different edge-report path")
    require(edge.get("checks") == 223_198 and edge.get("failed") == 0, "C Stage-20 dropped or failed frozen edge cases")
    require(edge.get("module") == "candidates.vm_candidate", "the C Stage-20 edge belongs to another candidate")
    all_artifacts = second.artifact_fingerprints(campaign.get("native_artifacts"), "candidates.vm_candidate")
    production = second.artifact_fingerprints(edge.get("production_artifacts"), "candidates.vm_candidate")
    matching = second.artifact_fingerprints(edge.get("candidate_artifacts"), "candidates.vm_candidate")
    require(all_artifacts == production, "the complete C campaign and qualified production source differ")
    for role, item in matching.items():
        require(all_artifacts.get(role) == item, "the complete C campaign and edge matching artifacts differ")
    for role, item in all_artifacts.items():
        if role == "native-source":
            require(sources.get(item["path"]) == item["sha256"], "the complete C campaign used an unverified native source")
        elif role == "public-python":
            require(measured.get("candidates.vm_candidate:module") == item["sha256"], "the complete C campaign used a substituted public wrapper")
        elif role == "native-bridge":
            require(measured.get("candidates.vm_candidate:native-engine") == item["sha256"], "the complete C campaign and actual mapped C library differ")
        else:
            raise AuditError("the complete C campaign introduced an unexpected artifact role")


def synthetic_histories() -> tuple[dict, dict, dict, dict, dict, dict[str, str], dict[str, str], dict[str, str]]:
    v1, v2, v3, v4, old_sources, old_native, old_measured = fifth.synthetic_histories()
    c_path = "candidates/_vm_native.c"
    c_role = "candidates.vm_candidate:native-engine"
    for historical in (v1, v2, v3, v4):
        historical["qualified_source_fingerprints"][c_path] = STAGE19_C_SOURCE_SHA256
        historical["native_elf_fingerprints"][c_role] = STAGE19_C_NATIVE_SHA256
        historical["candidate_binary_sha256_before"][c_role] = STAGE19_C_NATIVE_SHA256
        historical["candidate_binary_sha256_after"][c_role] = STAGE19_C_NATIVE_SHA256
    old_sources[c_path] = STAGE19_C_SOURCE_SHA256
    old_native[c_role] = STAGE19_C_NATIVE_SHA256
    old_measured[c_role] = STAGE19_C_NATIVE_SHA256
    v5 = {
        "schema": fifth.SCHEMA, "result": "PASS", "failed": 0,
        "holdout_accessed": False, "timing_performed": False,
        "module_order": list(original.MODULES),
        "cases_per_candidate": original.EXPECTED_CASES,
        "trials_per_module_case": original.EXPECTED_TRIALS,
        "bootstrap_draws": original.EXPECTED_BOOTSTRAPS,
        "frozen_plan_sha256": original.EXPECTED_PLAN_SHA256,
        "source_sha256": V5_AUDITOR_SHA256,
        "historical_v1_integrity_sha256": V1_INTEGRITY_SHA256,
        "historical_v2_integrity_sha256": V2_INTEGRITY_SHA256,
        "historical_v3_integrity_sha256": V3_INTEGRITY_SHA256,
        "historical_v4_integrity_sha256": V4_INTEGRITY_SHA256,
        "from_scratch_audit_sha256": fifth.V5_AUDIT_SHA256,
        "strict_regressions": fifth.EXPECTED_REGRESSIONS,
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
        "qualified_source_fingerprints": dict(old_sources),
        "native_elf_fingerprints": dict(old_native),
        "candidate_binary_sha256_before": dict(old_measured),
        "candidate_binary_sha256_after": dict(old_measured),
    }
    sources = {**old_sources, c_path: STAGE20_C_SOURCE_SHA256}
    native = {**old_native, c_role: STAGE20_C_NATIVE_SHA256}
    measured = {**old_measured, c_role: STAGE20_C_NATIVE_SHA256}
    return v1, v2, v3, v4, v5, sources, native, measured


def self_test() -> dict:
    inherited = fifth.self_test()
    require(inherited.get("result") == "PASS", "the preserved v5 synthetic replay failed")
    earlier = inherited.get("poisoned_controls")
    require(isinstance(earlier, list) and len(earlier) >= 119, "C Stage-20 omitted its 119 inherited poison controls")
    plan, sample, _compressed, profile = original.synthetic_evidence()
    sample["exclusive_slot"] = SLOT
    sample["raw_path"] = str(RAW_PATH.resolve())
    sample["measurement"] = "balanced practice diagnostic only; not a holdout result or final speed claim"
    validate_version_identity(sample, plan, profile, RAW_PATH)
    v1, v2, v3, v4, v5, sources, native, measured = synthetic_histories()
    validate_historical_continuity(v1, v2, v3, v4, v5, sources, native, measured)
    controls = [*earlier]

    def reject(name: str, action: object) -> None:
        try:
            action()  # type: ignore[operator]
        except (AuditError, KeyError, ValueError, TypeError, OverflowError):
            controls.append({"name": name, "passed": True})
            return
        raise AuditError(f"C Stage-20 synthetic control accepted corrupted evidence: {name}")

    def poison_version(key: str, value: object) -> None:
        value_copy = copy.deepcopy(sample)
        value_copy[key] = value
        validate_version_identity(value_copy, plan, profile, RAW_PATH)

    def poison_history(which: str, key: str, value: object) -> None:
        first = copy.deepcopy(v1)
        second_doc = copy.deepcopy(v2)
        third_doc = copy.deepcopy(v3)
        fourth_doc = copy.deepcopy(v4)
        fifth_doc = copy.deepcopy(v5)
        current_sources = dict(sources)
        current_native = dict(native)
        current_measured = dict(measured)
        mappings = {
            "v1": first, "v2": second_doc, "v3": third_doc,
            "v4": fourth_doc, "v5": fifth_doc,
            "v5-sources": fifth_doc["qualified_source_fingerprints"],
            "v5-native": fifth_doc["native_elf_fingerprints"],
            "sources": current_sources, "native": current_native,
            "measured": current_measured,
        }
        mappings[which][key] = value
        validate_historical_continuity(
            first, second_doc, third_doc, fourth_doc, fifth_doc,
            current_sources, current_native, current_measured,
        )

    for label, bad_slot in (
        ("v1-slot-cross-contamination", original.EXPECTED_SLOT),
        ("v2-slot-cross-contamination", second.SLOT),
        ("v3-slot-cross-contamination", third.SLOT),
        ("v4-slot-cross-contamination", fourth.SLOT),
        ("v5-slot-cross-contamination", fifth.SLOT),
        ("v6-filename-incorrectly-used-as-slot", PREFIX),
    ):
        reject(label, lambda value=bad_slot: poison_version("exclusive_slot", value))
    for label, path in (
        ("v1-raw-cross-contamination", original.RAW_PATH),
        ("v2-raw-cross-contamination", second.RAW_PATH),
        ("v3-raw-cross-contamination", third.RAW_PATH),
        ("v4-raw-cross-contamination", fourth.RAW_PATH),
        ("v5-raw-cross-contamination", fifth.RAW_PATH),
    ):
        reject(label, lambda value=path: poison_version("raw_path", str(value.resolve())))
    reject("practice-falsely-claimed-final", lambda: poison_version("measurement", "final held-out performance"))
    for label, history in (
        ("v1-history-substituted", "v1"), ("v2-history-substituted", "v2"),
        ("v3-history-substituted", "v3"), ("v4-history-substituted", "v4"),
        ("v5-history-substituted", "v5"),
    ):
        reject(label, lambda value=history: poison_history(value, "schema", SCHEMA))
    reject("historical-v5-407-losses-concealed", lambda: poison_history("v5", "strict_regressions", fifth.EXPECTED_REGRESSIONS - 1))
    reject("historical-rust-full-campaign-substituted", lambda: poison_history("v5", "full_correctness_campaign_sha256", "0" * 64))
    reject("historical-zig-full-campaign-substituted", lambda: poison_history("v5", "zig_full_correctness_campaign_sha256", "0" * 64))
    reject("historical-first-rust-failure-concealed", lambda: poison_history("v5", "initial_audit_failure_sha256", "0" * 64))
    reject("historical-c-source-replaced", lambda: poison_history("v5-sources", "candidates/_vm_native.c", STAGE20_C_SOURCE_SHA256))
    reject("historical-c-native-replaced", lambda: poison_history("v5-native", "candidates.vm_candidate:native-engine", STAGE20_C_NATIVE_SHA256))
    reject("stage20-c-source-not-new", lambda: poison_history("sources", "candidates/_vm_native.c", STAGE19_C_SOURCE_SHA256))
    reject("stage20-c-native-not-new", lambda: poison_history("native", "candidates.vm_candidate:native-engine", STAGE19_C_NATIVE_SHA256))
    reject("unchanged-rust-owned-source-substituted", lambda: poison_history("sources", "candidates/rust/src/lib.rs", "0" * 64))
    reject("unchanged-rust-engine-substituted", lambda: poison_history("native", "candidates.rust_candidate:native-engine", "0" * 64))
    reject("unchanged-rust-bridge-substituted", lambda: poison_history("native", "candidates.rust_candidate:native-bridge", "0" * 64))
    reject("unchanged-zig12-source-substituted", lambda: poison_history("sources", "candidates/zig/py_bridge.c", "0" * 64))
    reject("unchanged-zig12-bridge-substituted", lambda: poison_history("native", "candidates.zig_candidate:native-bridge", "0" * 64))
    reject("unchanged-zig12-engine-substituted", lambda: poison_history("native", "candidates.zig_candidate:native-engine", "0" * 64))
    reject("unchanged-python-baseline-substituted", lambda: poison_history("measured", "re:module", "0" * 64))
    require(len(controls) >= 151, "C Stage-20 omitted inherited candidate-isolation poison controls")
    return {
        "schema": SCHEMA + "-self-test", "result": "PASS", "synthetic_only": True,
        "holdout_accessed": False, "timing_performed": False,
        "historical_v1_auditor_sha256": V1_AUDITOR_SHA256,
        "historical_v2_auditor_sha256": V2_AUDITOR_SHA256,
        "historical_v3_auditor_sha256": V3_AUDITOR_SHA256,
        "historical_v4_auditor_sha256": V4_AUDITOR_SHA256,
        "historical_v5_auditor_sha256": V5_AUDITOR_SHA256,
        "inherited_poisoned_control_count": len(earlier),
        "poisoned_control_count": len(controls), "poisoned_controls": controls,
        "unchanged_reference_candidates": list(UNCHANGED_REFERENCE_CANDIDATES),
        "failed": 0,
    }


def verify(raw_path: Path, summary_path: Path, audit_path: Path, output_path: Path) -> dict:
    require(platform.python_implementation() == "CPython" and tuple(sys.version_info[:3]) == (3, 14, 6), "C Stage-20 requires pinned stable CPython 3.14.6")
    require(Path(sys.executable).resolve() == original.PINNED_PYTHON.resolve(), "C Stage-20 requires the exact frozen Python executable")
    require(raw_path.resolve() == RAW_PATH.resolve(), "v6 may not replace or overwrite preserved practice observations")
    require(summary_path.resolve() == SUMMARY_PATH.resolve(), "v6 may not replace or overwrite preserved practice summaries")
    require(audit_path.resolve() == original.AUDIT_PATH.resolve(), "v6 may not substitute the actual current native audit")
    require(output_path.resolve() == OUTPUT_PATH.resolve(), "v6 may not overwrite or redirect any historical integrity result")
    require(not output_path.exists(), "the unique Stage-20 C integrity result already exists")
    require(not any(name in sys.modules for name in original.MODULES[1:]), "the independent C Stage-20 verifier imported a candidate")
    for module, digest in (
        (original, V1_AUDITOR_SHA256), (second, V2_AUDITOR_SHA256),
        (third, V3_AUDITOR_SHA256), (fourth, V4_AUDITOR_SHA256),
        (fifth, V5_AUDITOR_SHA256),
    ):
        require(original.sha256_file(Path(module.__file__).resolve()) == digest, "a frozen previous independent verifier changed")
    require(original.sha256_file(third.INITIAL_FAILURE_PATH) == INITIAL_FAILURE_SHA256, "the genuine preserved Rust first-failure report changed")

    profile = original.Profile()
    plan = original.read_json(original.PLAN_PATH, "frozen 624-case public practice plan", original.EXPECTED_PLAN_SHA256)
    require(plan.get("expected_sha256") == original.EXPECTED_FROZEN_ANSWER_SHA256, "the C experiment changed frozen expected Python answers")
    original.validate_plan(plan, profile)
    summary = original.read_json(summary_path, "actual one-shot Stage-20 C public practice summary", V6_SUMMARY_SHA256)
    validate_version_identity(summary, plan, profile, raw_path)
    require(summary.get("compressed_raw_sha256") == V6_COMPRESSED_RAW_SHA256, "the actual Stage-20 gzip observations changed")
    require(summary.get("raw_sha256") == V6_RAW_SHA256, "the actual Stage-20 decompressed observations changed")
    require(original.sha256_file(raw_path) == V6_COMPRESSED_RAW_SHA256, "the one-shot Stage-20 raw gzip file changed")

    audit = original.read_json(audit_path, "actual five-library Stage-20 independence audit", V6_AUDIT_SHA256)
    sources, native = original.validate_independence(audit)
    measured = original.validate_measured_fingerprints(summary, sources, native)
    v1 = original.read_json(original.OUTPUT_PATH, "frozen original four-way result", V1_INTEGRITY_SHA256)
    v2 = original.read_json(second.OUTPUT_PATH, "frozen v2 four-way result", V2_INTEGRITY_SHA256)
    v3 = original.read_json(third.OUTPUT_PATH, "frozen v3 four-way result", V3_INTEGRITY_SHA256)
    v4 = original.read_json(fourth.OUTPUT_PATH, "frozen v4 four-way result", V4_INTEGRITY_SHA256)
    v5 = original.read_json(fifth.OUTPUT_PATH, "frozen v5 four-way result", V5_INTEGRITY_SHA256)
    validate_historical_continuity(v1, v2, v3, v4, v5, sources, native, measured)
    edges = validate_v6_edges(summary, measured)
    c_campaign = original.read_json(CAMPAIGN_PATH, "passing original complete Stage-20 C campaign", C_CAMPAIGN_SHA256)
    validate_c_campaign(c_campaign, sources, measured)
    rust_campaign = original.read_json(fifth.CAMPAIGN_PATH, "preserved passing complete Rust owned-prefix campaign", RUST_CAMPAIGN_SHA256)
    fifth.validate_rust_campaign(rust_campaign, measured)
    zig_campaign = original.read_json(fourth.CAMPAIGN_PATH, "preserved passing complete Zig Stage-12 campaign", ZIG_CAMPAIGN_SHA256)
    fourth.validate_zig_campaign(zig_campaign, sources, measured)

    try:
        with raw_path.open("rb") as source:
            observations = original.read_observations(source, V6_COMPRESSED_RAW_SHA256, summary, plan, profile)
    except OSError as error:
        raise AuditError("cannot open the unique Stage-20 C public-practice observations") from error
    results, rankings = original.recompute_results(plan, observations, profile)
    regressions = original.validate_results(summary, results, rankings, profile)
    require(len(regressions) == EXPECTED_REGRESSIONS, "the Stage-20 C comparison omitted or changed its 407 actual losses")
    controls = self_test()
    require(not any(name in sys.modules for name in original.MODULES[1:]), "the independent C results verifier imported an engine")

    document = {
        "schema": SCHEMA, "result": "PASS", "holdout_accessed": False,
        "timing_performed": False,
        "measurement": "independent replay of one Stage-20 C four-way public practice run; not final or held-out performance",
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
        "summary_sha256": V6_SUMMARY_SHA256,
        "compressed_raw_sha256": V6_COMPRESSED_RAW_SHA256,
        "raw_sha256": V6_RAW_SHA256,
        "frozen_plan_sha256": original.EXPECTED_PLAN_SHA256,
        "source_sha256": original.sha256_file(Path(__file__).resolve()),
        "historical_v1_auditor_sha256": V1_AUDITOR_SHA256,
        "historical_v2_auditor_sha256": V2_AUDITOR_SHA256,
        "historical_v3_auditor_sha256": V3_AUDITOR_SHA256,
        "historical_v4_auditor_sha256": V4_AUDITOR_SHA256,
        "historical_v5_auditor_sha256": V5_AUDITOR_SHA256,
        "historical_v1_integrity_sha256": V1_INTEGRITY_SHA256,
        "historical_v2_integrity_sha256": V2_INTEGRITY_SHA256,
        "historical_v3_integrity_sha256": V3_INTEGRITY_SHA256,
        "historical_v4_integrity_sha256": V4_INTEGRITY_SHA256,
        "historical_v5_integrity_sha256": V5_INTEGRITY_SHA256,
        "from_scratch_audit_sha256": V6_AUDIT_SHA256,
        "from_scratch_control_count": 76,
        "verified_independent_engine_count": len(original.MODULES) - 1,
        "verified_native_library_count": len(native),
        "full_correctness_campaign_sha256": C_CAMPAIGN_SHA256,
        "full_correctness_campaign_steps": 22,
        "rust_full_correctness_campaign_sha256": RUST_CAMPAIGN_SHA256,
        "rust_full_correctness_campaign_steps": 22,
        "zig_full_correctness_campaign_sha256": ZIG_CAMPAIGN_SHA256,
        "zig_full_correctness_campaign_steps": 22,
        "initial_audit_failure_sha256": INITIAL_FAILURE_SHA256,
        "rust_optimization_verified": True,
        "capacity16_optimization_verified": True,
        "zig_optimization_verified": True,
        "mandatory_prefix_optimization_verified": True,
        "unchanged_rust_bridge_verified": True,
        "c_optimization_verified": True,
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
        raise AuditError("the unique Stage-20 C integrity output already exists") from error
    except OSError as error:
        raise AuditError("cannot persist the unique Stage-20 C integrity output") from error
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
        "poisoned_control_count": controls["poisoned_control_count"],
        "rust_optimization_verified": True,
        "capacity16_optimization_verified": True,
        "zig_optimization_verified": True,
        "mandatory_prefix_optimization_verified": True,
        "unchanged_rust_bridge_verified": True,
        "c_optimization_verified": True,
        "unchanged_reference_candidates": list(UNCHANGED_REFERENCE_CANDIDATES),
        "output": original.display_path(output_path),
        "sha256": hashlib.sha256(encoded).hexdigest(), "failed": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("self-test", help="run only pure inherited corruption and C-only source isolation controls")
    check = commands.add_parser("verify", help="independently replay the exact fully qualified C Stage-20 practice run")
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
