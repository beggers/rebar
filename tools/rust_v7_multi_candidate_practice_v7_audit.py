#!/usr/bin/env python3
"""Fail-closed replay of a future, fully qualified Zig Stage-13 practice run.

The six earlier experiments and their source-bound integrity proofs remain
immutable.  All Stage-13 identity and measurement constants intentionally stay
unset until an actual complete correctness campaign and a single authorized
public-practice run exist.  No verifier invocation can certify guessed data.
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


ROOT = original.ROOT
EVIDENCE = original.EVIDENCE
SCHEMA = "rebar-v7-multi-candidate-practice-integrity-v7"
PREFIX = "three-qualified-engines-public-practice-v7"
RAW_PATH = EVIDENCE / f"{PREFIX}-raw.jsonl.gz"
SUMMARY_PATH = EVIDENCE / f"{PREFIX}-summary.json"
OUTPUT_PATH = EVIDENCE / f"{PREFIX}-integrity.json"

V1_AUDITOR_SHA256 = "bc093f114fe15833cab8f7c8d59bd1970345b6ddb47bc33349854be1af7f0ded"
V2_AUDITOR_SHA256 = "4dee19924cb0e4312ff9b62c70dd105f1f49aa4a7f3eeedaa650d9f9f5d853d4"
V3_AUDITOR_SHA256 = "1bd6a03a0d8e25b3041a31e095f97647f7d2e0b317e8ae3b8adf9b25113aefd4"
V4_AUDITOR_SHA256 = "6b6cb39cdab33e5b6ce2c88568925885514590f26f27c1990b24b598ac555dc0"
V5_AUDITOR_SHA256 = "7236508d80094d5c7a4fd3e33725b6e9485b73b7cdacd33b6a72d2ccc4cf6590"
V6_AUDITOR_SHA256 = "e8885263620f0a9c40dcb3f095dcc5ce1aa7741da57acb5a1b10749ea81acce9"
V1_INTEGRITY_SHA256 = "8739803b6cd020b8b4f663223435fd1e39ef5603e90195b2a268a9fa7fbc0340"
V2_INTEGRITY_SHA256 = "82ef917ca82ba124af6311f3bf10398a2a040286ed06430919bbdd26dd61e057"
V3_INTEGRITY_SHA256 = "aa1921230845a01aa03d607bd8609b3475dc659cacda5e6135d8b7064ed60c22"
V4_INTEGRITY_SHA256 = "7bfb360fa570510d585c923345f00162da92a3a7cd6379528ad981b1ec003174"
V5_INTEGRITY_SHA256 = "015a2f9e3ceebd3792c4de62828c2d63fbafd7a5f866c9513b60b964a974712e"
V6_INTEGRITY_SHA256 = "8804136b49d7203854bda098b4c224e1b62ae9ecc3d050e81378d1b9b9515134"
C_CAMPAIGN_SHA256 = "c211d826032fed60c30024beb6de66c3e20b08fdcb936b53393d0a5fdba09721"
RUST_CAMPAIGN_SHA256 = "9543fbbb39bbf42f5329a051b8441e69c756a495287a06c2f877c757b3ec5688"
INITIAL_FAILURE_SHA256 = "ccaf3813b29badcf80c552dc0d850f83a2ca122cc3cc3057576dd519aed4f088"
STAGE12_ZIG_SOURCE_SHA256 = "cb14210092d9ec92a2ac8c458d7b713342c8662bcf3318f954e0c520bc7b1589"
STAGE12_ZIG_BRIDGE_SHA256 = "4d1eb307eabc8b254ac0724aeb8ba106105d9879b7d46054b2355621fb330a92"
UNCHANGED_ZIG_ENGINE_SHA256 = "70bafca56a3f48477b2011f016a81b625e5f40a772af6a986d32b9098269f614"
UNCHANGED_REFERENCE_CANDIDATES = [
    "re", "candidates.rust_candidate", "candidates.vm_candidate"
]

# Deliberate fail-closed placeholders.  Populate only from the actual passing
# Stage-13 campaign, the genuine current independence audit, and the exact
# single public-practice run.  A missing value is never interpreted as success.
V7_SLOT: str | None = "three-qualified-engines-zig-stage-13-interned-dispatch-v7"
V7_AUDIT_SHA256: str | None = "5ce9df468d136b47c435456e59d372aed74d89f80fe1f877988dd7dba784b737"
V7_SUMMARY_SHA256: str | None = "89cf98bee40bb8e3ecc95861e07f302eff6c5f6288130854ea806578e8b76d79"
V7_COMPRESSED_RAW_SHA256: str | None = "574f62be23725529decaa7bbab67a575faae040470ccef9f528213c50866385c"
V7_RAW_SHA256: str | None = "59a04863d5cc2f0727222ac8d4388255411803793c741975d4c8abb3bfc3a696"
ZIG13_CAMPAIGN_PATH: Path | None = ROOT / "candidates/evidence/rust-v8-zig-stage-13-sealed-campaign.json"
ZIG13_CAMPAIGN_SHA256: str | None = "4ba7cb9c45a70b747cc0a6eb721f6bb51081157f527d1bf5e578e603715ae5dc"
ZIG13_EDGE_PATH: Path | None = ROOT / "candidates/evidence/rust-v8-edge-oracle-zig-deep-stage-13.json.gz"
ZIG13_EDGE_COMPRESSED_SHA256: str | None = "b31af0559e865b93a506e0915073cef141a805b4462e7e4d4a692e11aff393fc"
ZIG13_EDGE_PAYLOAD_SHA256: str | None = "a4c8b75811b5304ab115fb387f821127a20ed2615e7948ab4b96443dbe1ebe5c"
ZIG13_SOURCE_SHA256: str | None = "92d4039e1db2e01757edfd4edf56006c4735c3bc64352b6ce9c5d1f69decafcf"
ZIG13_BRIDGE_SHA256: str | None = "80d7dab57cbee317ee1727862e27cd7dcf4cb22e1a944f4b29f2e4e983f940ed"
STAGE13_ROLE_CONFUSION_INCIDENT_PATH = EVIDENCE / "ZIG-STAGE-13-VERIFIER-INCIDENTS.md"
STAGE13_ROLE_CONFUSION_INCIDENT_SHA256: str | None = "84efcdbd0059ab430c84322695bf472f66fdc1cc05efd74e383b62114efcedff"
EXPECTED_REGRESSIONS: int | None = 259


AuditError = original.AuditError
require = original.require


def required_digest(value: str | None, label: str) -> str:
    require(
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value),
        f"the actual source-bound Stage-13 {label} has not been frozen",
    )
    return value


def required_path(value: Path | None, label: str) -> Path:
    require(isinstance(value, Path), f"the actual source-bound Stage-13 {label} path has not been frozen")
    path = value.resolve()
    require(path.is_relative_to(ROOT.resolve()), f"the Stage-13 {label} path escaped this project")
    return path


def required_slot(value: str | None) -> str:
    require(
        isinstance(value, str)
        and bool(value)
        and value != PREFIX
        and value not in {
            original.EXPECTED_SLOT, second.SLOT, third.SLOT,
            fourth.SLOT, fifth.SLOT, sixth.SLOT,
        },
        "the actual unique Stage-13 public-practice slot has not been frozen",
    )
    return value


def validate_role_confusion_incident(actual_sha256: str, expected_sha256: str) -> None:
    require(
        actual_sha256 == expected_sha256,
        "the honest Stage-13 verifier role-confusion incident was concealed or changed",
    )


def validate_version_identity(
    summary: dict, plan: dict, profile: original.Profile,
    raw_path: Path, expected_slot: str,
) -> None:
    original.validate_header(summary, plan, profile, None)
    require(summary.get("exclusive_slot") == expected_slot, "Stage-13 used a different or historical public-practice slot")
    require(summary.get("raw_path") == str(raw_path.resolve()), "Stage-13 substituted recorded public-practice observations")
    require(
        summary.get("measurement")
        == "balanced practice diagnostic only; not a holdout result or final speed claim",
        "Stage-13 practice was misrepresented as final or held-out performance",
    )


def validate_historical_continuity(
    v1: dict, v2: dict, v3: dict, v4: dict, v5: dict, v6: dict,
    sources: dict[str, str], native: dict[str, str], measured: dict[str, str],
    zig_source_sha256: str, zig_bridge_sha256: str,
) -> None:
    require(v6.get("schema") == sixth.SCHEMA, "the historical C Stage-20 result was replaced")
    require(v6.get("result") == "PASS" and v6.get("failed") == 0, "historical Stage-20 C did not pass independent verification")
    require(v6.get("holdout_accessed") is False and v6.get("timing_performed") is False, "historical C verification accessed or timed hidden performance")
    require(v6.get("module_order") == list(original.MODULES), "historical Stage-20 changed independent candidate families")
    require(v6.get("cases_per_candidate") == original.EXPECTED_CASES, "historical Stage-20 changed public case weights")
    require(v6.get("trials_per_module_case") == original.EXPECTED_TRIALS, "historical Stage-20 changed paired trials")
    require(v6.get("bootstrap_draws") == original.EXPECTED_BOOTSTRAPS, "historical Stage-20 changed confidence draws")
    require(v6.get("frozen_plan_sha256") == original.EXPECTED_PLAN_SHA256, "historical Stage-20 changed the frozen practice plan")
    require(v6.get("source_sha256") == V6_AUDITOR_SHA256, "the frozen C Stage-20 verifier changed")
    for key, expected in (
        ("historical_v1_integrity_sha256", V1_INTEGRITY_SHA256),
        ("historical_v2_integrity_sha256", V2_INTEGRITY_SHA256),
        ("historical_v3_integrity_sha256", V3_INTEGRITY_SHA256),
        ("historical_v4_integrity_sha256", V4_INTEGRITY_SHA256),
        ("historical_v5_integrity_sha256", V5_INTEGRITY_SHA256),
    ):
        require(v6.get(key) == expected, f"historical Stage-20 changed an earlier frozen experiment: {key}")
    require(v6.get("from_scratch_audit_sha256") == sixth.V6_AUDIT_SHA256, "historical Stage-20 changed its source-independent audit")
    require(v6.get("strict_regressions") == sixth.EXPECTED_REGRESSIONS, "historical Stage-20 concealed its actual 407 losses")
    require(v6.get("full_correctness_campaign_sha256") == C_CAMPAIGN_SHA256, "the unchanged C Stage-20 full campaign changed")
    require(v6.get("full_correctness_campaign_steps") == 22, "the unchanged C Stage-20 campaign omitted correctness stages")
    require(v6.get("rust_full_correctness_campaign_sha256") == RUST_CAMPAIGN_SHA256, "the unchanged owned-prefix Rust full campaign changed")
    require(v6.get("rust_full_correctness_campaign_steps") == 22, "the unchanged Rust full campaign omitted correctness stages")
    require(v6.get("initial_audit_failure_sha256") == INITIAL_FAILURE_SHA256, "the genuine historical Rust failure was removed")
    for flag in (
        "rust_optimization_verified", "capacity16_optimization_verified",
        "zig_optimization_verified", "mandatory_prefix_optimization_verified",
        "unchanged_rust_bridge_verified", "c_optimization_verified",
    ):
        require(v6.get(flag) is True, f"historical Stage-20 omitted a source qualification: {flag}")
    old_sources = v6.get("qualified_source_fingerprints")
    old_native = v6.get("native_elf_fingerprints")
    old_measured = v6.get("candidate_binary_sha256_before")
    require(isinstance(old_sources, dict), "historical Stage-20 source fingerprints are missing")
    require(isinstance(old_native, dict), "historical Stage-20 native fingerprints are missing")
    require(isinstance(old_measured, dict), "historical Stage-20 timed fingerprints are missing")
    require(v6.get("candidate_binary_sha256_after") == old_measured, "historical Stage-20 changed an engine while timing")
    sixth.validate_historical_continuity(v1, v2, v3, v4, v5, old_sources, old_native, old_measured)

    changed_source = "candidates/zig/py_bridge.c"
    changed_native = "candidates.zig_candidate:native-bridge"
    require(set(sources) == set(old_sources), "Stage-13 added or removed a production source")
    require(set(native) == set(old_native), "Stage-13 added or removed a mapped native engine")
    require(set(measured) == set(old_measured), "Stage-13 added or removed a timed production artifact")
    for path, digest in old_sources.items():
        if path != changed_source:
            require(sources.get(path) == digest, f"the Zig-only experiment changed another production source: {path}")
    for role, digest in old_native.items():
        if role != changed_native:
            require(native.get(role) == digest, f"the Zig-only experiment changed another mapped engine: {role}")
    for role, digest in old_measured.items():
        if role != changed_native:
            require(measured.get(role) == digest, f"the Zig-only experiment changed another timed candidate: {role}")
    require(old_sources.get(changed_source) == STAGE12_ZIG_SOURCE_SHA256, "historical v6 does not contain its genuine Stage-12 Zig bridge source")
    require(old_native.get(changed_native) == STAGE12_ZIG_BRIDGE_SHA256, "historical v6 does not contain its genuine Stage-12 Zig bridge")
    require(sources.get(changed_source) == zig_source_sha256, "the new Stage-13 Zig source does not match its full qualification")
    require(native.get(changed_native) == zig_bridge_sha256, "the new Stage-13 Zig bridge does not match its full qualification")
    require(measured.get(changed_native) == zig_bridge_sha256, "the new Stage-13 Zig timed bridge is not its mapped native library")
    require(native.get("candidates.zig_candidate:native-engine") == UNCHANGED_ZIG_ENGINE_SHA256, "the supposedly unchanged Zig owned engine changed")
    require(zig_source_sha256 != STAGE12_ZIG_SOURCE_SHA256, "the alleged Stage-13 Zig bridge source did not actually change")
    require(zig_bridge_sha256 != STAGE12_ZIG_BRIDGE_SHA256, "the alleged Stage-13 Zig bridge did not actually change")


def validate_v7_edges(
    summary: dict, measured: dict[str, str],
    zig_path: Path, zig_compressed_sha256: str, zig_payload_sha256: str,
) -> list[dict]:
    require(original.sha256_file(original.EDGE_SOURCE_PATH) == original.EXPECTED_EDGE_SOURCE_SHA256, "the immutable independent matching-oracle source changed")
    baseline, baseline_digest = original.read_edge(original.STDLIB_EDGE_PATH, "frozen Python baseline edge report")
    original.validate_edge_document(baseline, "re")
    require(baseline_digest == original.EXPECTED_STDLIB_EDGE_SHA256, "the frozen Python baseline edge payload changed")
    require(original.sha256_file(fifth.RUST_EDGE_PATH) == fifth.RUST_EDGE_COMPRESSED_SHA256, "the unchanged owned-prefix Rust edge proof changed")
    require(original.sha256_file(sixth.C_EDGE_PATH) == sixth.C_EDGE_COMPRESSED_SHA256, "the unchanged Stage-20 C edge proof changed")
    require(original.sha256_file(zig_path) == zig_compressed_sha256, "the new Stage-13 Zig compressed correctness proof changed")
    entries = summary.get("verified_edge_oracles")
    require(isinstance(entries, list) and len(entries) == len(original.MODULES) - 1, "Stage-13 omitted a measured engine's complete correctness proof")
    paths = {
        "candidates.rust_candidate": fifth.RUST_EDGE_PATH,
        "candidates.vm_candidate": sixth.C_EDGE_PATH,
        "candidates.zig_candidate": zig_path,
    }
    for module, proof in zip(original.MODULES[1:], entries, strict=True):
        require(isinstance(proof, dict) and proof.get("module") == module, "Stage-13 correctness proofs are missing, reordered, or cross-contaminated")
        path = paths[module]
        require(proof.get("path") == str(path.resolve()), f"{module} names a different frozen correctness report")
        require(proof.get("correctness_checks") == 223_198, f"{module} omitted frozen matching cases")
        require(proof.get("actual_sha256") == original.EXPECTED_EDGE_ANSWER_SHA256, f"{module} failed to reproduce exact Python matching answers")
        require(proof.get("script_sha256") == original.EXPECTED_EDGE_SOURCE_SHA256, f"{module} changed the frozen matching-oracle source")
        require(proof.get("stdlib_baseline_sha256") == baseline_digest, f"{module} used a different pinned Python baseline")
        report, digest = original.read_edge(path, f"{module} Stage-13 qualified matching proof")
        original.validate_edge_document(report, module)
        require(proof.get("report_sha256") == digest, f"{module} changed matching evidence after the one-shot run")
        if module == "candidates.rust_candidate":
            require(digest == fifth.RUST_EDGE_PAYLOAD_SHA256, "the unchanged Rust proof does not certify the owned-prefix implementation")
        elif module == "candidates.vm_candidate":
            require(digest == sixth.C_EDGE_PAYLOAD_SHA256, "the unchanged C proof does not certify the Stage-20 implementation")
        else:
            require(digest == zig_payload_sha256, "the Zig proof does not certify the actual Stage-13 implementation")
        artifacts = second.artifact_fingerprints(report.get("candidate_artifacts"), module)
        require(proof.get("candidate_artifacts") == artifacts, f"{module} timed artifacts not bound to its frozen correctness proof")
        for role, item in artifacts.items():
            if role == "public-python":
                key = f"{module}:module"
            elif module == "candidates.vm_candidate" and role == "native-bridge":
                key = f"{module}:native-engine"
            else:
                key = f"{module}:{role}"
            require(measured.get(key) == item["sha256"], f"{module} substituted its timed source, native library, or family")
    return entries


def validate_zig_campaign(
    campaign: dict, sources: dict[str, str], measured: dict[str, str],
    zig_path: Path, zig_compressed_sha256: str,
) -> None:
    require(campaign.get("schema") == "rebar-rust-campaign-gate-v1", "the future Stage-13 campaign does not use the frozen complete correctness format")
    require(campaign.get("candidate") == "candidates.zig_candidate", "the Stage-13 full campaign qualified another engine")
    require(campaign.get("passed") is True, "the complete Stage-13 Zig correctness campaign did not pass")
    require(campaign.get("holdout_accessed") is False, "the Stage-13 full campaign accessed a hidden case")
    require(campaign.get("timing_performed") is False and campaign.get("performance") == "NOT MEASURED", "the Stage-13 full correctness campaign performed timing")
    require(campaign.get("required_correctness_step_count") == 22, "Stage-13 changed the required frozen correctness denominator")
    stages = campaign.get("steps")
    require(isinstance(stages, list) and len(stages) == 22, "Stage-13 omitted a correctness stage")
    require(all(isinstance(stage, dict) and stage.get("passed") is True for stage in stages), "Stage-13 contains an unexplained mismatch or native crash")
    require(campaign.get("pinned_cpython") == "3.14.6", "Stage-13 changed its stable CPython correctness baseline")
    require(campaign.get("python_executable") == str(original.PINNED_PYTHON), "Stage-13 used another Python executable")
    require(campaign.get("mode") == "sealed-practice-only", "Stage-13 weakened complete campaign isolation")
    edge = campaign.get("edge_oracle")
    require(isinstance(edge, dict), "Stage-13 omitted its source-bound matching proof")
    require(edge.get("archive_sha256") == zig_compressed_sha256, "Stage-13 referenced a different compressed Zig matching proof")
    require(edge.get("path") == str(zig_path.resolve()), "Stage-13 referenced a different edge-report path")
    require(edge.get("checks") == 223_198 and edge.get("failed") == 0, "Stage-13 dropped or failed frozen matching cases")
    require(edge.get("module") == "candidates.zig_candidate", "Stage-13 bound another candidate's matching proof")
    complete = second.artifact_fingerprints(campaign.get("native_artifacts"), "candidates.zig_candidate")
    production = second.artifact_fingerprints(edge.get("production_artifacts"), "candidates.zig_candidate")
    matching = second.artifact_fingerprints(edge.get("candidate_artifacts"), "candidates.zig_candidate")
    require(complete == production, "the Stage-13 campaign differs from its actual production parser and native bridge")
    for role, item in matching.items():
        require(complete.get(role) == item, "the Stage-13 edge proof differs from the fully qualified Zig engine")
    for role, item in complete.items():
        if role in {"native-source", "bridge-source"}:
            require(sources.get(item["path"]) == item["sha256"], "the Stage-13 campaign used an unaudited source")
        else:
            key = "candidates.zig_candidate:module" if role == "public-python" else f"candidates.zig_candidate:{role}"
            require(measured.get(key) == item["sha256"], "the Stage-13 timed binary differs from its complete correctness campaign")


def synthetic_histories() -> tuple[dict, dict, dict, dict, dict, dict, dict[str, str], dict[str, str], dict[str, str], str, str]:
    v1, v2, v3, v4, v5, old_sources, old_native, old_measured = sixth.synthetic_histories()
    zig_path = "candidates/zig/py_bridge.c"
    zig_role = "candidates.zig_candidate:native-bridge"
    for historical in (v1, v2, v3, v4, v5):
        if historical.get("schema") in {fourth.SCHEMA, fifth.SCHEMA}:
            historical["qualified_source_fingerprints"][zig_path] = STAGE12_ZIG_SOURCE_SHA256
            historical["native_elf_fingerprints"][zig_role] = STAGE12_ZIG_BRIDGE_SHA256
            historical["candidate_binary_sha256_before"][zig_role] = STAGE12_ZIG_BRIDGE_SHA256
            historical["candidate_binary_sha256_after"][zig_role] = STAGE12_ZIG_BRIDGE_SHA256
    old_sources[zig_path] = STAGE12_ZIG_SOURCE_SHA256
    old_native[zig_role] = STAGE12_ZIG_BRIDGE_SHA256
    old_measured[zig_role] = STAGE12_ZIG_BRIDGE_SHA256
    v6 = {
        "schema": sixth.SCHEMA, "result": "PASS", "failed": 0,
        "holdout_accessed": False, "timing_performed": False,
        "module_order": list(original.MODULES),
        "cases_per_candidate": original.EXPECTED_CASES,
        "trials_per_module_case": original.EXPECTED_TRIALS,
        "bootstrap_draws": original.EXPECTED_BOOTSTRAPS,
        "frozen_plan_sha256": original.EXPECTED_PLAN_SHA256,
        "source_sha256": V6_AUDITOR_SHA256,
        "historical_v1_integrity_sha256": V1_INTEGRITY_SHA256,
        "historical_v2_integrity_sha256": V2_INTEGRITY_SHA256,
        "historical_v3_integrity_sha256": V3_INTEGRITY_SHA256,
        "historical_v4_integrity_sha256": V4_INTEGRITY_SHA256,
        "historical_v5_integrity_sha256": V5_INTEGRITY_SHA256,
        "from_scratch_audit_sha256": sixth.V6_AUDIT_SHA256,
        "strict_regressions": sixth.EXPECTED_REGRESSIONS,
        "full_correctness_campaign_sha256": C_CAMPAIGN_SHA256,
        "full_correctness_campaign_steps": 22,
        "rust_full_correctness_campaign_sha256": RUST_CAMPAIGN_SHA256,
        "rust_full_correctness_campaign_steps": 22,
        "zig_full_correctness_campaign_sha256": fourth.ZIG_CAMPAIGN_SHA256,
        "zig_full_correctness_campaign_steps": 22,
        "initial_audit_failure_sha256": INITIAL_FAILURE_SHA256,
        "rust_optimization_verified": True,
        "capacity16_optimization_verified": True,
        "zig_optimization_verified": True,
        "mandatory_prefix_optimization_verified": True,
        "unchanged_rust_bridge_verified": True,
        "c_optimization_verified": True,
        "qualified_source_fingerprints": dict(old_sources),
        "native_elf_fingerprints": dict(old_native),
        "candidate_binary_sha256_before": dict(old_measured),
        "candidate_binary_sha256_after": dict(old_measured),
    }
    new_source = hashlib.sha256(b"synthetic-zig-stage13-interned-source").hexdigest()
    new_bridge = hashlib.sha256(b"synthetic-zig-stage13-interned-native").hexdigest()
    sources = {**old_sources, zig_path: new_source}
    native = {**old_native, zig_role: new_bridge}
    measured = {**old_measured, zig_role: new_bridge}
    return v1, v2, v3, v4, v5, v6, sources, native, measured, new_source, new_bridge


def self_test() -> dict:
    inherited = sixth.self_test()
    require(inherited.get("result") == "PASS", "the immutable C Stage-20 synthetic replay failed")
    existing = inherited.get("poisoned_controls")
    require(isinstance(existing, list) and len(existing) >= 151, "the Stage-13 verifier omitted its 151 inherited corruption controls")
    plan, sample, _payload, profile = original.synthetic_evidence()
    sample_slot = "synthetic-stage13-candidate-free-v7"
    sample["exclusive_slot"] = sample_slot
    sample["raw_path"] = str(RAW_PATH.resolve())
    sample["measurement"] = "balanced practice diagnostic only; not a holdout result or final speed claim"
    validate_version_identity(sample, plan, profile, RAW_PATH, sample_slot)
    v1, v2, v3, v4, v5, v6, sources, native, measured, source_digest, bridge_digest = synthetic_histories()
    validate_historical_continuity(
        v1, v2, v3, v4, v5, v6, sources, native, measured,
        source_digest, bridge_digest,
    )
    controls = [*existing]

    def reject(name: str, action: object) -> None:
        try:
            action()  # type: ignore[operator]
        except (AuditError, KeyError, ValueError, TypeError, OverflowError):
            controls.append({"name": name, "passed": True})
            return
        raise AuditError(f"Stage-13 synthetic controls accepted corrupted evidence: {name}")

    def poison_version(key: str, value: object) -> None:
        document = copy.deepcopy(sample)
        document[key] = value
        validate_version_identity(document, plan, profile, RAW_PATH, sample_slot)

    def poison_history(which: str, key: str, value: object) -> None:
        first = copy.deepcopy(v1)
        second_doc = copy.deepcopy(v2)
        third_doc = copy.deepcopy(v3)
        fourth_doc = copy.deepcopy(v4)
        fifth_doc = copy.deepcopy(v5)
        sixth_doc = copy.deepcopy(v6)
        current_sources = dict(sources)
        current_native = dict(native)
        current_measured = dict(measured)
        groups = {
            "v1": first, "v2": second_doc, "v3": third_doc,
            "v4": fourth_doc, "v5": fifth_doc, "v6": sixth_doc,
            "v6-sources": sixth_doc["qualified_source_fingerprints"],
            "v6-native": sixth_doc["native_elf_fingerprints"],
            "sources": current_sources, "native": current_native,
            "measured": current_measured,
        }
        groups[which][key] = value
        validate_historical_continuity(
            first, second_doc, third_doc, fourth_doc, fifth_doc, sixth_doc,
            current_sources, current_native, current_measured,
            source_digest, bridge_digest,
        )

    for label, slot in (
        ("v1-slot-contamination", original.EXPECTED_SLOT),
        ("v2-slot-contamination", second.SLOT),
        ("v3-slot-contamination", third.SLOT),
        ("v4-slot-contamination", fourth.SLOT),
        ("v5-slot-contamination", fifth.SLOT),
        ("v6-slot-contamination", sixth.SLOT),
        ("v7-filename-incorrectly-treated-as-slot", PREFIX),
    ):
        reject(label, lambda value=slot: poison_version("exclusive_slot", value))
    for label, path in (
        ("v1-raw-contamination", original.RAW_PATH),
        ("v2-raw-contamination", second.RAW_PATH),
        ("v3-raw-contamination", third.RAW_PATH),
        ("v4-raw-contamination", fourth.RAW_PATH),
        ("v5-raw-contamination", fifth.RAW_PATH),
        ("v6-raw-contamination", sixth.RAW_PATH),
    ):
        reject(label, lambda value=path: poison_version("raw_path", str(value.resolve())))
    reject("practice-falsely-claimed-final", lambda: poison_version("measurement", "final hidden benchmark"))
    for label, version in (
        ("v1-history-substitution", "v1"), ("v2-history-substitution", "v2"),
        ("v3-history-substitution", "v3"), ("v4-history-substitution", "v4"),
        ("v5-history-substitution", "v5"), ("v6-history-substitution", "v6"),
    ):
        reject(label, lambda value=version: poison_history(value, "schema", SCHEMA))
    reject("v6-historical-407-losses-concealed", lambda: poison_history("v6", "strict_regressions", sixth.EXPECTED_REGRESSIONS - 1))
    reject("preserved-stage20-c-campaign-substituted", lambda: poison_history("v6", "full_correctness_campaign_sha256", "0" * 64))
    reject("preserved-rust-owned-campaign-substituted", lambda: poison_history("v6", "rust_full_correctness_campaign_sha256", "0" * 64))
    reject("preserved-initial-rust-failure-concealed", lambda: poison_history("v6", "initial_audit_failure_sha256", "0" * 64))
    reject("historical-zig12-source-replaced", lambda: poison_history("v6-sources", "candidates/zig/py_bridge.c", source_digest))
    reject("historical-zig12-native-replaced", lambda: poison_history("v6-native", "candidates.zig_candidate:native-bridge", bridge_digest))
    reject("stage13-zig-source-not-new", lambda: poison_history("sources", "candidates/zig/py_bridge.c", STAGE12_ZIG_SOURCE_SHA256))
    reject("stage13-zig-bridge-not-new", lambda: poison_history("native", "candidates.zig_candidate:native-bridge", STAGE12_ZIG_BRIDGE_SHA256))
    reject("unchanged-zig-owned-engine-substituted", lambda: poison_history("native", "candidates.zig_candidate:native-engine", "0" * 64))
    reject("unchanged-c-stage20-source-substituted", lambda: poison_history("sources", "candidates/_vm_native.c", "0" * 64))
    reject("unchanged-c-stage20-native-substituted", lambda: poison_history("native", "candidates.vm_candidate:native-engine", "0" * 64))
    reject("unchanged-rust-owned-source-substituted", lambda: poison_history("sources", "candidates/rust/src/lib.rs", "0" * 64))
    reject("unchanged-rust-owned-engine-substituted", lambda: poison_history("native", "candidates.rust_candidate:native-engine", "0" * 64))
    reject("unchanged-rust-bridge-substituted", lambda: poison_history("native", "candidates.rust_candidate:native-bridge", "0" * 64))
    reject("unchanged-python-baseline-substituted", lambda: poison_history("measured", "re:module", "0" * 64))
    synthetic_incident_sha256 = hashlib.sha256(
        b"synthetic-stage13-honest-role-confusion-incident"
    ).hexdigest()
    validate_role_confusion_incident(
        synthetic_incident_sha256, synthetic_incident_sha256,
    )
    reject(
        "stage13-role-confusion-incident-concealed",
        lambda: validate_role_confusion_incident(
            "0" * 64, synthetic_incident_sha256,
        ),
    )
    require(len(controls) >= 185, "Stage-13 omitted frozen, incident-preservation, or Zig-only source-isolation poison controls")
    return {
        "schema": SCHEMA + "-self-test", "result": "PASS", "synthetic_only": True,
        "holdout_accessed": False, "timing_performed": False,
        "historical_v1_auditor_sha256": V1_AUDITOR_SHA256,
        "historical_v2_auditor_sha256": V2_AUDITOR_SHA256,
        "historical_v3_auditor_sha256": V3_AUDITOR_SHA256,
        "historical_v4_auditor_sha256": V4_AUDITOR_SHA256,
        "historical_v5_auditor_sha256": V5_AUDITOR_SHA256,
        "historical_v6_auditor_sha256": V6_AUDITOR_SHA256,
        "inherited_poisoned_control_count": len(existing),
        "poisoned_control_count": len(controls), "poisoned_controls": controls,
        "role_confusion_incident_control_verified": True,
        "unchanged_reference_candidates": list(UNCHANGED_REFERENCE_CANDIDATES),
        "failed": 0,
    }


def verify(raw_path: Path, summary_path: Path, audit_path: Path, output_path: Path) -> dict:
    slot = required_slot(V7_SLOT)
    audit_digest = required_digest(V7_AUDIT_SHA256, "canonical five-library independence audit")
    summary_digest = required_digest(V7_SUMMARY_SHA256, "one-shot public summary")
    compressed_digest = required_digest(V7_COMPRESSED_RAW_SHA256, "compressed public raw record")
    raw_digest = required_digest(V7_RAW_SHA256, "uncompressed public raw record")
    campaign_path = required_path(ZIG13_CAMPAIGN_PATH, "complete 22-stage campaign")
    campaign_digest = required_digest(ZIG13_CAMPAIGN_SHA256, "complete passing campaign")
    edge_path = required_path(ZIG13_EDGE_PATH, "independent edge-oracle")
    edge_digest = required_digest(ZIG13_EDGE_COMPRESSED_SHA256, "compressed edge proof")
    edge_payload = required_digest(ZIG13_EDGE_PAYLOAD_SHA256, "uncompressed edge proof")
    source_digest = required_digest(ZIG13_SOURCE_SHA256, "Zig bridge source")
    bridge_digest = required_digest(ZIG13_BRIDGE_SHA256, "actual mapped Zig bridge")
    incident_digest = required_digest(
        STAGE13_ROLE_CONFUSION_INCIDENT_SHA256,
        "honestly preserved verifier role-confusion incident",
    )
    losses = EXPECTED_REGRESSIONS
    require(isinstance(losses, int) and not isinstance(losses, bool) and losses >= 0, "the actual one-shot Stage-13 slowdown denominator has not been frozen")
    require(platform.python_implementation() == "CPython" and tuple(sys.version_info[:3]) == (3, 14, 6), "Stage-13 replay requires stable CPython 3.14.6")
    require(Path(sys.executable).resolve() == original.PINNED_PYTHON.resolve(), "Stage-13 replay requires its exact frozen Python baseline")
    require(raw_path.resolve() == RAW_PATH.resolve(), "v7 may not substitute or overwrite earlier public observations")
    require(summary_path.resolve() == SUMMARY_PATH.resolve(), "v7 may not substitute or overwrite earlier public summaries")
    require(audit_path.resolve() == original.AUDIT_PATH.resolve(), "v7 may not substitute the actual source-independence audit")
    require(output_path.resolve() == OUTPUT_PATH.resolve(), "v7 may not redirect or overwrite historical integrity proofs")
    require(not output_path.exists(), "the unique Stage-13 practice-integrity report already exists")
    require(not any(name in sys.modules for name in original.MODULES[1:]), "the Stage-13 results verifier imported a candidate")
    validate_role_confusion_incident(
        original.sha256_file(STAGE13_ROLE_CONFUSION_INCIDENT_PATH),
        incident_digest,
    )
    for module, expected in (
        (original, V1_AUDITOR_SHA256), (second, V2_AUDITOR_SHA256),
        (third, V3_AUDITOR_SHA256), (fourth, V4_AUDITOR_SHA256),
        (fifth, V5_AUDITOR_SHA256), (sixth, V6_AUDITOR_SHA256),
    ):
        require(original.sha256_file(Path(module.__file__).resolve()) == expected, "an immutable prior practice verifier source changed")
    require(original.sha256_file(third.INITIAL_FAILURE_PATH) == INITIAL_FAILURE_SHA256, "the genuine first Rust audit failure was deleted or rewritten")

    profile = original.Profile()
    plan = original.read_json(original.PLAN_PATH, "frozen 624-case public plan", original.EXPECTED_PLAN_SHA256)
    require(plan.get("expected_sha256") == original.EXPECTED_FROZEN_ANSWER_SHA256, "Stage-13 changed frozen Python practice answers")
    original.validate_plan(plan, profile)
    summary = original.read_json(summary_path, "actual one-shot Stage-13 public-practice summary", summary_digest)
    validate_version_identity(summary, plan, profile, raw_path, slot)
    require(summary.get("compressed_raw_sha256") == compressed_digest, "Stage-13 changed its recorded compressed raw observations")
    require(summary.get("raw_sha256") == raw_digest, "Stage-13 changed its recorded decompressed raw observations")
    require(original.sha256_file(raw_path) == compressed_digest, "Stage-13 changed the exact raw gzip file")

    audit = original.read_json(audit_path, "Stage-13 source-bound five-library provenance audit", audit_digest)
    sources, native = original.validate_independence(audit)
    measured = original.validate_measured_fingerprints(summary, sources, native)
    v1 = original.read_json(original.OUTPUT_PATH, "frozen original public result", V1_INTEGRITY_SHA256)
    v2 = original.read_json(second.OUTPUT_PATH, "frozen v2 public result", V2_INTEGRITY_SHA256)
    v3 = original.read_json(third.OUTPUT_PATH, "frozen v3 public result", V3_INTEGRITY_SHA256)
    v4 = original.read_json(fourth.OUTPUT_PATH, "frozen v4 public result", V4_INTEGRITY_SHA256)
    v5 = original.read_json(fifth.OUTPUT_PATH, "frozen v5 public result", V5_INTEGRITY_SHA256)
    v6 = original.read_json(sixth.OUTPUT_PATH, "frozen v6 public result", V6_INTEGRITY_SHA256)
    validate_historical_continuity(
        v1, v2, v3, v4, v5, v6, sources, native, measured,
        source_digest, bridge_digest,
    )
    edge_proofs = validate_v7_edges(summary, measured, edge_path, edge_digest, edge_payload)
    zig_campaign = original.read_json(campaign_path, "passing complete Stage-13 Zig campaign", campaign_digest)
    validate_zig_campaign(zig_campaign, sources, measured, edge_path, edge_digest)
    c_campaign = original.read_json(sixth.CAMPAIGN_PATH, "preserved complete Stage-20 C campaign", C_CAMPAIGN_SHA256)
    sixth.validate_c_campaign(c_campaign, sources, measured)
    rust_campaign = original.read_json(fifth.CAMPAIGN_PATH, "preserved complete owned-prefix Rust campaign", RUST_CAMPAIGN_SHA256)
    fifth.validate_rust_campaign(rust_campaign, measured)

    try:
        with raw_path.open("rb") as source:
            observations = original.read_observations(source, compressed_digest, summary, plan, profile)
    except OSError as error:
        raise AuditError("cannot open the complete Stage-13 public practice observations") from error
    results, rankings = original.recompute_results(plan, observations, profile)
    regressions = original.validate_results(summary, results, rankings, profile)
    require(len(regressions) == losses, "Stage-13 concealed or altered an actual substantial slowdown")
    controls = self_test()
    require(not any(name in sys.modules for name in original.MODULES[1:]), "the Stage-13 independent replay imported a candidate")

    document = {
        "schema": SCHEMA, "result": "PASS", "holdout_accessed": False,
        "timing_performed": False,
        "measurement": "independent replay of one Stage-13 Zig four-way public practice run; not final or held-out performance",
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
        "historical_v1_integrity_sha256": V1_INTEGRITY_SHA256,
        "historical_v2_integrity_sha256": V2_INTEGRITY_SHA256,
        "historical_v3_integrity_sha256": V3_INTEGRITY_SHA256,
        "historical_v4_integrity_sha256": V4_INTEGRITY_SHA256,
        "historical_v5_integrity_sha256": V5_INTEGRITY_SHA256,
        "historical_v6_integrity_sha256": V6_INTEGRITY_SHA256,
        "from_scratch_audit_sha256": audit_digest,
        "role_confusion_incident_sha256": incident_digest,
        "role_confusion_incident_path": str(
            STAGE13_ROLE_CONFUSION_INCIDENT_PATH.resolve()
        ),
        "from_scratch_control_count": 76,
        "verified_independent_engine_count": len(original.MODULES) - 1,
        "verified_native_library_count": len(native),
        "full_correctness_campaign_sha256": campaign_digest,
        "full_correctness_campaign_steps": 22,
        "c_full_correctness_campaign_sha256": C_CAMPAIGN_SHA256,
        "c_full_correctness_campaign_steps": 22,
        "rust_full_correctness_campaign_sha256": RUST_CAMPAIGN_SHA256,
        "rust_full_correctness_campaign_steps": 22,
        "initial_audit_failure_sha256": INITIAL_FAILURE_SHA256,
        "rust_optimization_verified": True,
        "capacity16_optimization_verified": True,
        "mandatory_prefix_optimization_verified": True,
        "unchanged_rust_bridge_verified": True,
        "c_optimization_verified": True,
        "zig_optimization_verified": True,
        "zig_interned_attributes_optimization_verified": True,
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
        raise AuditError("the unique Stage-13 public-practice integrity output already exists") from error
    except OSError as error:
        raise AuditError("cannot persist the unique Stage-13 practice integrity result") from error
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
        "rust_full_correctness_campaign_steps": 22,
        "poisoned_control_count": controls["poisoned_control_count"],
        "role_confusion_incident_sha256": incident_digest,
        "role_confusion_incident_path": str(
            STAGE13_ROLE_CONFUSION_INCIDENT_PATH.resolve()
        ),
        "rust_optimization_verified": True,
        "capacity16_optimization_verified": True,
        "mandatory_prefix_optimization_verified": True,
        "unchanged_rust_bridge_verified": True,
        "c_optimization_verified": True,
        "zig_optimization_verified": True,
        "zig_interned_attributes_optimization_verified": True,
        "unchanged_reference_candidates": list(UNCHANGED_REFERENCE_CANDIDATES),
        "output": original.display_path(output_path),
        "sha256": hashlib.sha256(encoded).hexdigest(), "failed": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("self-test", help="run only frozen, candidate-free synthetic and historical isolation controls")
    check = commands.add_parser("verify", help="replay the exact future, fully qualified Stage-13 Zig public practice run")
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
