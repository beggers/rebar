#!/usr/bin/env python3
"""Independently replay the one-off, capacity-16 public practice experiment.

The frozen v1 and v2 experiments remain historical, byte-identified evidence.
Only their pure, candidate-free replay and synthetic-control helpers are reused.
This verifier neither times nor imports a regex candidate and never opens or
generates final benchmark cases.
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
from tools import rust_v7_multi_candidate_practice_v2_audit as previous


ROOT = original.ROOT
EVIDENCE = original.EVIDENCE
SCHEMA = "rebar-v7-multi-candidate-practice-integrity-v3"
SLOT = "three-qualified-engines-findall-capacity-16-v3"
PREFIX = "three-qualified-engines-public-practice-v3"
RAW_PATH = EVIDENCE / f"{PREFIX}-raw.jsonl.gz"
SUMMARY_PATH = EVIDENCE / f"{PREFIX}-summary.json"
OUTPUT_PATH = EVIDENCE / f"{PREFIX}-integrity.json"
CAMPAIGN_PATH = ROOT / "candidates/evidence/rust-v8-rust-findall-capacity-16-sealed-campaign.json"
RUST_EDGE_PATH = ROOT / "candidates/evidence/rust-v7-edge-oracle-rust-findall-capacity-16.json.gz"
INITIAL_FAILURE_PATH = ROOT / "candidates/evidence/RUST-FINDALL-CAPACITY-16-INITIAL-AUDIT-FAILURE.md"

V1_AUDITOR_SHA256 = "bc093f114fe15833cab8f7c8d59bd1970345b6ddb47bc33349854be1af7f0ded"
V2_AUDITOR_SHA256 = "4dee19924cb0e4312ff9b62c70dd105f1f49aa4a7f3eeedaa650d9f9f5d853d4"
V1_INTEGRITY_SHA256 = "8739803b6cd020b8b4f663223435fd1e39ef5603e90195b2a268a9fa7fbc0340"
V2_INTEGRITY_SHA256 = "82ef917ca82ba124af6311f3bf10398a2a040286ed06430919bbdd26dd61e057"
V3_AUDIT_SHA256 = "af69f41966a26d9ec1892e34b16f1bc02eb095c41767899d0a3deb612591d8fc"
V3_SUMMARY_SHA256 = "33ebdff8ecb061e3544b9cd4bc687040b8278aa037f3c993abe654daa665d155"
V3_COMPRESSED_RAW_SHA256 = "d17ae80c1a2d8adddf2ddeecd3ff84377e72f293d8ca8add2ad1c533bcf562b1"
V3_RAW_SHA256 = "225c3c83e4a8170f5851586f70aed0c58cc056778a8c718b7799abc896bf169c"
V3_CAMPAIGN_SHA256 = "89793a597ac74551742d05bdf1c5af61f1121d89466e00ac2902c8942aaeef4d"
V3_EDGE_COMPRESSED_SHA256 = "e089482ae716693e109b357b30b898d4699c77b36ad2575d745fdb9c0f8c1577"
V3_EDGE_PAYLOAD_SHA256 = "cec324450b93abaf3b1727d06e8334658a6996f150648bf97733303bce0f201b"
INITIAL_FAILURE_SHA256 = "ccaf3813b29badcf80c552dc0d850f83a2ca122cc3cc3057576dd519aed4f088"
CAPACITY16_SOURCE_SHA256 = "83afb5a709a6d0ea1701dfd64db30644edbf2cb0276c2db731a8119cfd52d8ed"
CAPACITY16_BRIDGE_SHA256 = "1f072e81ba9339a8b2e52a7e93b7bcde791c4d518620b6bd760af67c7c89af34"
EXPECTED_REGRESSIONS = 387
UNCHANGED_REFERENCE_CANDIDATES = [
    "re", "candidates.vm_candidate", "candidates.zig_candidate"
]


AuditError = original.AuditError
require = original.require


def validate_version_identity(
    summary: dict,
    plan: dict,
    profile: original.Profile,
    raw_path: Path,
) -> None:
    original.validate_header(summary, plan, profile, None)
    require(summary.get("exclusive_slot") == SLOT, "the capacity-16 run changed its one authorized v3 timing slot")
    require(summary.get("raw_path") == str(raw_path.resolve()), "the capacity-16 summary names different raw observations")
    require(
        summary.get("measurement")
        == "balanced practice diagnostic only; not a holdout result or final speed claim",
        "the capacity-16 public result was misrepresented as final performance",
    )


def validate_historical_continuity(
    first: dict,
    second: dict,
    current_sources: dict[str, str],
    current_native: dict[str, str],
    current_measured: dict[str, str],
) -> None:
    require(second.get("schema") == previous.SCHEMA, "the historical v2 experiment was replaced by another version")
    require(second.get("result") == "PASS" and second.get("failed") == 0, "the historical v2 practice evidence does not pass")
    require(second.get("holdout_accessed") is False and second.get("timing_performed") is False, "the historical v2 verifier accessed or timed final workloads")
    require(second.get("module_order") == list(original.MODULES), "the historical v2 comparison changed its independent engine families")
    require(second.get("cases_per_candidate") == original.EXPECTED_CASES, "the historical v2 comparison changed its case denominator")
    require(second.get("trials_per_module_case") == original.EXPECTED_TRIALS, "the historical v2 comparison changed its trial denominator")
    require(second.get("bootstrap_draws") == original.EXPECTED_BOOTSTRAPS, "the historical v2 comparison changed its bootstrap protocol")
    require(second.get("frozen_plan_sha256") == original.EXPECTED_PLAN_SHA256, "the historical v2 comparison changed its frozen cases")
    require(second.get("source_sha256") == V2_AUDITOR_SHA256, "the immutable v2 auditor source changed")
    require(second.get("historical_v1_integrity_sha256") == V1_INTEGRITY_SHA256, "the historical v2 result does not bind its actual v1 predecessor")
    require(second.get("from_scratch_audit_sha256") == previous.V2_AUDIT_SHA256, "the historical v2 canonical audit was substituted")
    require(second.get("strict_regressions") == previous.EXPECTED_REGRESSIONS, "the actual historical v2 slowdown denominator changed")
    require(second.get("full_correctness_campaign_sha256") == previous.FUSED_CAMPAIGN_SHA256, "the actual historical v2 full correctness campaign changed")
    require(second.get("full_correctness_campaign_steps") == 22, "historical v2 Rust was not fully qualified")
    require(second.get("rust_optimization_verified") is True, "the historical v2 Rust change was not independently verified")
    require(second.get("unchanged_reference_candidates") == UNCHANGED_REFERENCE_CANDIDATES, "the historical v2 reference engines changed")

    old_sources = second.get("qualified_source_fingerprints")
    old_native = second.get("native_elf_fingerprints")
    old_measured = second.get("candidate_binary_sha256_before")
    require(isinstance(old_sources, dict), "the historical v2 audited source fingerprints are missing")
    require(isinstance(old_native, dict), "the historical v2 five-library fingerprints are missing")
    require(isinstance(old_measured, dict), "the historical v2 measured production fingerprints are missing")
    require(second.get("candidate_binary_sha256_after") == old_measured, "the historical v2 production artifacts changed during timing")

    # Independently prove that the exact frozen v1 and v2 experiments agree on
    # their baseline, C, and Zig references and differ only in audited Rust.
    previous.validate_historical_continuity(first, old_sources, old_native, old_measured)

    unchanged_sources = (
        "candidates/_vm_native.c",
        "candidates/vm_candidate.py",
        "candidates/zig/mini_regex.zig",
        "candidates/zig/py_bridge.c",
        "candidates/zig_candidate.py",
    )
    for path in unchanged_sources:
        require(current_sources.get(path) == old_sources.get(path), f"a C or Zig reference source changed since v2: {path}")
    unchanged_roles = (
        "re:module",
        "candidates.vm_candidate:module",
        "candidates.vm_candidate:native-engine",
        "candidates.zig_candidate:module",
        "candidates.zig_candidate:native-bridge",
        "candidates.zig_candidate:native-engine",
    )
    for role in unchanged_roles:
        require(current_measured.get(role) == old_measured.get(role), f"a baseline, C, or Zig control changed since v2: {role}")
        if role in old_native:
            require(current_native.get(role) == old_native.get(role), f"a control native mapping changed since v2: {role}")

    rust_source_path = "candidates/rust/py_bridge.c"
    rust_native_role = "candidates.rust_candidate:native-bridge"
    require(old_sources.get(rust_source_path) == previous.FUSED_RUST_SOURCE_SHA256, "the historical v2 Rust source is not the fused-vectorcall experiment")
    require(old_native.get(rust_native_role) == previous.FUSED_RUST_BRIDGE_SHA256, "the historical v2 Rust binary is not the fused-vectorcall experiment")
    require(current_sources.get(rust_source_path) == CAPACITY16_SOURCE_SHA256, "the capacity-16 Rust source differs from its independently audited change")
    require(current_native.get(rust_native_role) == CAPACITY16_BRIDGE_SHA256, "the capacity-16 Rust native bridge differs from its independently audited change")
    require(CAPACITY16_SOURCE_SHA256 != previous.FUSED_RUST_SOURCE_SHA256, "the alleged capacity-16 Rust source did not actually change")
    require(CAPACITY16_BRIDGE_SHA256 != previous.FUSED_RUST_BRIDGE_SHA256, "the alleged capacity-16 Rust native bridge did not actually change")


def validate_v3_edges(summary: dict, measured: dict[str, str]) -> list[dict]:
    require(
        original.sha256_file(original.EDGE_SOURCE_PATH) == original.EXPECTED_EDGE_SOURCE_SHA256,
        "the frozen independent matching oracle changed",
    )
    stdlib, stdlib_digest = original.read_edge(original.STDLIB_EDGE_PATH, "pinned Python edge correctness proof")
    original.validate_edge_document(stdlib, "re")
    require(stdlib_digest == original.EXPECTED_STDLIB_EDGE_SHA256, "the frozen Python edge correctness proof changed")
    require(original.sha256_file(RUST_EDGE_PATH) == V3_EDGE_COMPRESSED_SHA256, "the capacity-16 Rust edge proof was substituted")
    references = summary.get("verified_edge_oracles")
    require(isinstance(references, list) and len(references) == len(original.MODULES) - 1, "the capacity-16 comparison omitted an independent correctness-qualified candidate")
    paths = {
        "candidates.rust_candidate": RUST_EDGE_PATH,
        "candidates.vm_candidate": previous.C_EDGE_PATH,
        "candidates.zig_candidate": previous.ZIG_EDGE_PATH,
    }
    for module, reference in zip(original.MODULES[1:], references, strict=True):
        require(isinstance(reference, dict) and reference.get("module") == module, "capacity-16 candidate correctness proofs are missing or reordered")
        path = paths[module]
        require(reference.get("path") == str(path.resolve()), f"{module} used a different qualification proof")
        require(reference.get("correctness_checks") == 223_198, f"{module} dropped an independent frozen matching obligation")
        require(reference.get("actual_sha256") == original.EXPECTED_EDGE_ANSWER_SHA256, f"{module} does not reproduce Python's exact matching results")
        require(reference.get("script_sha256") == original.EXPECTED_EDGE_SOURCE_SHA256, f"{module} used an altered correctness oracle")
        require(reference.get("stdlib_baseline_sha256") == stdlib_digest, f"{module} changed the pinned Python correctness baseline")
        report, payload_digest = original.read_edge(path, f"{module} capacity-16 correctness proof")
        original.validate_edge_document(report, module)
        require(reference.get("report_sha256") == payload_digest, f"{module} qualification evidence changed after measurement")
        if module == "candidates.rust_candidate":
            require(payload_digest == V3_EDGE_PAYLOAD_SHA256, "the Rust correctness report is not the exact capacity-16 qualification")
        artifacts = previous.artifact_fingerprints(report.get("candidate_artifacts"), module)
        require(reference.get("candidate_artifacts") == artifacts, f"{module} used substituted production artifacts")
        for role, item in artifacts.items():
            if role == "public-python":
                key = f"{module}:module"
            elif module == "candidates.vm_candidate" and role == "native-bridge":
                key = f"{module}:native-engine"
            else:
                key = f"{module}:{role}"
            require(measured.get(key) == item["sha256"], f"{module} was not timed using its actually qualified source and binary")
    return references


def validate_full_campaign(campaign: dict, measured: dict[str, str]) -> None:
    require(campaign.get("schema") == "rebar-rust-campaign-gate-v1", "the capacity-16 full campaign schema changed")
    require(campaign.get("candidate") == "candidates.rust_candidate", "the full campaign qualified a different candidate")
    require(campaign.get("passed") is True, "the complete capacity-16 Rust correctness campaign failed")
    require(campaign.get("holdout_accessed") is False, "the capacity-16 correctness campaign accessed a final case")
    require(campaign.get("timing_performed") is False and campaign.get("performance") == "NOT MEASURED", "the capacity-16 correctness campaign contained performance timing")
    require(campaign.get("required_correctness_step_count") == 22, "the frozen 22-stage correctness denominator changed")
    steps = campaign.get("steps")
    require(isinstance(steps, list) and len(steps) == 22, "the capacity-16 campaign dropped a correctness stage")
    require(all(isinstance(step, dict) and step.get("passed") is True for step in steps), "the capacity-16 campaign contains an unexplained failing stage")
    require(campaign.get("pinned_cpython") == "3.14.6", "the capacity-16 campaign used a different Python baseline")
    require(campaign.get("python_executable") == str(original.PINNED_PYTHON), "the capacity-16 campaign used a different Python executable")
    require(campaign.get("mode") == "sealed-practice-only", "the capacity-16 campaign changed its correctness isolation")
    edge = campaign.get("edge_oracle")
    require(isinstance(edge, dict), "the full capacity-16 campaign omitted its independent edge oracle")
    require(edge.get("archive_sha256") == V3_EDGE_COMPRESSED_SHA256, "the full capacity-16 campaign used a different matching proof")
    require(edge.get("path") == str(RUST_EDGE_PATH.resolve()), "the full capacity-16 campaign used a different Rust edge report")
    require(edge.get("checks") == 223_198 and edge.get("failed") == 0, "the full capacity-16 matching stage dropped or failed checks")
    require(edge.get("module") == "candidates.rust_candidate", "the full capacity-16 campaign qualified the wrong matching engine")
    native = previous.artifact_fingerprints(campaign.get("native_artifacts"), "candidates.rust_candidate")
    edge_native = previous.artifact_fingerprints(edge.get("candidate_artifacts"), "candidates.rust_candidate")
    require(native == edge_native, "the full capacity-16 campaign and edge proof disagree on production artifacts")
    for role, item in native.items():
        key = "candidates.rust_candidate:module" if role == "public-python" else f"candidates.rust_candidate:{role}"
        require(measured.get(key) == item["sha256"], "the timed capacity-16 engine differs from the engine that passed all 22 stages")


def synthetic_histories() -> tuple[dict, dict, dict[str, str], dict[str, str], dict[str, str]]:
    first, v2_sources, v2_native, v2_measured = previous.synthetic_history()
    second = {
        "schema": previous.SCHEMA, "result": "PASS", "failed": 0,
        "holdout_accessed": False, "timing_performed": False,
        "module_order": list(original.MODULES),
        "cases_per_candidate": original.EXPECTED_CASES,
        "trials_per_module_case": original.EXPECTED_TRIALS,
        "bootstrap_draws": original.EXPECTED_BOOTSTRAPS,
        "frozen_plan_sha256": original.EXPECTED_PLAN_SHA256,
        "source_sha256": V2_AUDITOR_SHA256,
        "historical_v1_integrity_sha256": V1_INTEGRITY_SHA256,
        "from_scratch_audit_sha256": previous.V2_AUDIT_SHA256,
        "strict_regressions": previous.EXPECTED_REGRESSIONS,
        "full_correctness_campaign_sha256": previous.FUSED_CAMPAIGN_SHA256,
        "full_correctness_campaign_steps": 22,
        "rust_optimization_verified": True,
        "unchanged_reference_candidates": list(UNCHANGED_REFERENCE_CANDIDATES),
        "qualified_source_fingerprints": dict(v2_sources),
        "native_elf_fingerprints": dict(v2_native),
        "candidate_binary_sha256_before": dict(v2_measured),
        "candidate_binary_sha256_after": dict(v2_measured),
    }
    sources = {**v2_sources, "candidates/rust/py_bridge.c": CAPACITY16_SOURCE_SHA256}
    native = {
        **v2_native,
        "candidates.rust_candidate:native-bridge": CAPACITY16_BRIDGE_SHA256,
    }
    measured = {
        **v2_measured,
        "candidates.rust_candidate:native-bridge": CAPACITY16_BRIDGE_SHA256,
    }
    return first, second, sources, native, measured


def self_test() -> dict:
    parent = previous.self_test()
    require(parent.get("result") == "PASS", "the immutable v2 synthetic controls no longer pass")
    inherited = parent.get("poisoned_controls")
    require(isinstance(inherited, list) and len(inherited) >= 44, "the capacity-16 verifier omitted the 44 original corruption controls")
    plan, summary, _encoded, profile = original.synthetic_evidence()
    summary["exclusive_slot"] = SLOT
    summary["raw_path"] = str(RAW_PATH.resolve())
    summary["measurement"] = "balanced practice diagnostic only; not a holdout result or final speed claim"
    validate_version_identity(summary, plan, profile, RAW_PATH)
    first, second, sources, native, measured = synthetic_histories()
    validate_historical_continuity(first, second, sources, native, measured)
    controls = [*inherited]

    def reject(name: str, action: object) -> None:
        try:
            action()  # type: ignore[operator]
        except (AuditError, KeyError, ValueError, TypeError, OverflowError):
            controls.append({"name": name, "passed": True})
            return
        raise AuditError(f"the capacity-16 synthetic verifier accepted poisoned evidence: {name}")

    def poison_version(key: str, value: object) -> None:
        poisoned = copy.deepcopy(summary)
        poisoned[key] = value
        validate_version_identity(poisoned, plan, profile, RAW_PATH)

    def poison_history(which: str, key: str, value: object) -> None:
        frozen_v1 = copy.deepcopy(first)
        frozen_v2 = copy.deepcopy(second)
        current_sources = dict(sources)
        current_native = dict(native)
        current_measured = dict(measured)
        mappings = {
            "v1": frozen_v1,
            "v2": frozen_v2,
            "v1-sources": frozen_v1["qualified_source_fingerprints"],
            "v2-sources": frozen_v2["qualified_source_fingerprints"],
            "v2-native": frozen_v2["native_elf_fingerprints"],
            "sources": current_sources,
            "native": current_native,
            "measured": current_measured,
        }
        mappings[which][key] = value
        validate_historical_continuity(
            frozen_v1, frozen_v2, current_sources, current_native, current_measured
        )

    reject("v1-exclusive-slot-cross-contamination", lambda: poison_version("exclusive_slot", original.EXPECTED_SLOT))
    reject("v2-exclusive-slot-cross-contamination", lambda: poison_version("exclusive_slot", previous.SLOT))
    reject("v3-filename-incorrectly-treated-as-slot", lambda: poison_version("exclusive_slot", PREFIX))
    reject("v1-raw-observation-cross-contamination", lambda: poison_version("raw_path", str(original.RAW_PATH.resolve())))
    reject("v2-raw-observation-cross-contamination", lambda: poison_version("raw_path", str(previous.RAW_PATH.resolve())))
    reject("public-practice-falsely-claimed-final", lambda: poison_version("measurement", "final holdout benchmark"))
    reject("substituted-v1-historical-schema", lambda: poison_history("v1", "schema", SCHEMA))
    reject("substituted-v2-historical-schema", lambda: poison_history("v2", "schema", SCHEMA))
    reject("substituted-v2-historical-auditor", lambda: poison_history("v2", "source_sha256", "0" * 64))
    reject("substituted-v2-historical-independence-audit", lambda: poison_history("v2", "from_scratch_audit_sha256", "0" * 64))
    reject("hidden-v2-substantial-slowdown", lambda: poison_history("v2", "strict_regressions", previous.EXPECTED_REGRESSIONS - 1))
    reject("v2-correctness-stage-omitted", lambda: poison_history("v2", "full_correctness_campaign_steps", 21))
    reject("v2-fused-rust-source-substituted", lambda: poison_history("v2-sources", "candidates/rust/py_bridge.c", CAPACITY16_SOURCE_SHA256))
    reject("v2-fused-rust-native-substituted", lambda: poison_history("v2-native", "candidates.rust_candidate:native-bridge", CAPACITY16_BRIDGE_SHA256))
    reject("capacity16-source-not-actually-new", lambda: poison_history("sources", "candidates/rust/py_bridge.c", previous.FUSED_RUST_SOURCE_SHA256))
    reject("capacity16-native-not-actually-new", lambda: poison_history("native", "candidates.rust_candidate:native-bridge", previous.FUSED_RUST_BRIDGE_SHA256))
    reject("unchanged-python-baseline-substituted", lambda: poison_history("measured", "re:module", "0" * 64))
    reject("unchanged-c-reference-source-substituted", lambda: poison_history("sources", "candidates/_vm_native.c", "0" * 64))
    reject("unchanged-c-reference-native-substituted", lambda: poison_history("native", "candidates.vm_candidate:native-engine", "0" * 64))
    reject("unchanged-zig-reference-source-substituted", lambda: poison_history("sources", "candidates/zig/mini_regex.zig", "0" * 64))
    reject("unchanged-zig-reference-native-substituted", lambda: poison_history("native", "candidates.zig_candidate:native-engine", "0" * 64))
    require(len(controls) >= 65, "the capacity-16 verifier omitted frozen or historical-isolation poison controls")
    return {
        "schema": SCHEMA + "-self-test", "result": "PASS", "synthetic_only": True,
        "holdout_accessed": False, "timing_performed": False,
        "historical_v1_auditor_sha256": V1_AUDITOR_SHA256,
        "historical_v2_auditor_sha256": V2_AUDITOR_SHA256,
        "inherited_poisoned_control_count": len(inherited),
        "poisoned_control_count": len(controls), "poisoned_controls": controls,
        "unchanged_reference_candidates": list(UNCHANGED_REFERENCE_CANDIDATES),
        "failed": 0,
    }


def verify(raw_path: Path, summary_path: Path, audit_path: Path, output_path: Path) -> dict:
    require(platform.python_implementation() == "CPython" and tuple(sys.version_info[:3]) == (3, 14, 6), "the v3 verifier requires frozen CPython 3.14.6")
    require(Path(sys.executable).resolve() == original.PINNED_PYTHON.resolve(), "the v3 verifier requires the exact frozen CPython executable")
    require(raw_path.resolve() == RAW_PATH.resolve(), "v3 may not substitute or overwrite historical raw observations")
    require(summary_path.resolve() == SUMMARY_PATH.resolve(), "v3 may not substitute or overwrite a historical summary")
    require(audit_path.resolve() == original.AUDIT_PATH.resolve(), "v3 may not substitute its actual from-scratch audit")
    require(output_path.resolve() == OUTPUT_PATH.resolve(), "v3 may not overwrite or redirect historical integrity evidence")
    require(not output_path.exists(), "the source-bound v3 integrity result already exists")
    require(not any(name in sys.modules for name in original.MODULES[1:]), "the v3 verifier unexpectedly imported a measured candidate")
    require(original.sha256_file(Path(original.__file__).resolve()) == V1_AUDITOR_SHA256, "the immutable v1 pure replay auditor changed")
    require(original.sha256_file(Path(previous.__file__).resolve()) == V2_AUDITOR_SHA256, "the immutable v2 pure historical-control auditor changed")
    require(original.sha256_file(INITIAL_FAILURE_PATH) == INITIAL_FAILURE_SHA256, "the genuine initial capacity-16 audit failure was removed or changed")

    profile = original.Profile()
    plan = original.read_json(
        original.PLAN_PATH, "immutable 624-case public practice plan", original.EXPECTED_PLAN_SHA256
    )
    require(plan.get("expected_sha256") == original.EXPECTED_FROZEN_ANSWER_SHA256, "v3 changed the frozen Python practice answers")
    original.validate_plan(plan, profile)
    summary = original.read_json(
        summary_path, "exact one-shot capacity-16 public practice summary", V3_SUMMARY_SHA256
    )
    validate_version_identity(summary, plan, profile, raw_path)
    require(summary.get("compressed_raw_sha256") == V3_COMPRESSED_RAW_SHA256, "the v3 compressed raw observations changed")
    require(summary.get("raw_sha256") == V3_RAW_SHA256, "the v3 decompressed raw observations changed")
    require(original.sha256_file(raw_path) == V3_COMPRESSED_RAW_SHA256, "the actual one-shot v3 gzip observations changed")

    audit = original.read_json(
        audit_path, "capacity-16 all-engine from-scratch provenance audit", V3_AUDIT_SHA256
    )
    sources, native = original.validate_independence(audit)
    measured = original.validate_measured_fingerprints(summary, sources, native)
    historical_v1 = original.read_json(
        original.OUTPUT_PATH, "immutable historical v1 four-engine result", V1_INTEGRITY_SHA256
    )
    historical_v2 = original.read_json(
        previous.OUTPUT_PATH, "immutable historical v2 four-engine result", V2_INTEGRITY_SHA256
    )
    validate_historical_continuity(historical_v1, historical_v2, sources, native, measured)
    edge_proofs = validate_v3_edges(summary, measured)
    campaign = original.read_json(
        CAMPAIGN_PATH, "passing untouched 22-stage capacity-16 correctness campaign", V3_CAMPAIGN_SHA256
    )
    validate_full_campaign(campaign, measured)

    try:
        with raw_path.open("rb") as source:
            observations = original.read_observations(
                source, V3_COMPRESSED_RAW_SHA256, summary, plan, profile
            )
    except OSError as error:
        raise AuditError("cannot open the actual capacity-16 public practice observations") from error
    results, rankings = original.recompute_results(plan, observations, profile)
    regressions = original.validate_results(summary, results, rankings, profile)
    require(len(regressions) == EXPECTED_REGRESSIONS, "the capacity-16 comparison concealed or altered its 387 actual losses")
    controls = self_test()
    require(not any(name in sys.modules for name in original.MODULES[1:]), "the v3 verifier imported a production candidate")

    document = {
        "schema": SCHEMA, "result": "PASS", "holdout_accessed": False,
        "timing_performed": False,
        "measurement": "independent replay of one recorded capacity-16 four-way public practice run; not final or held-out performance",
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
        "summary_sha256": V3_SUMMARY_SHA256,
        "compressed_raw_sha256": V3_COMPRESSED_RAW_SHA256,
        "raw_sha256": V3_RAW_SHA256,
        "frozen_plan_sha256": original.EXPECTED_PLAN_SHA256,
        "source_sha256": original.sha256_file(Path(__file__).resolve()),
        "historical_v1_auditor_sha256": V1_AUDITOR_SHA256,
        "historical_v2_auditor_sha256": V2_AUDITOR_SHA256,
        "historical_v1_integrity_sha256": V1_INTEGRITY_SHA256,
        "historical_v2_integrity_sha256": V2_INTEGRITY_SHA256,
        "from_scratch_audit_sha256": V3_AUDIT_SHA256,
        "from_scratch_control_count": 76,
        "verified_independent_engine_count": len(original.MODULES) - 1,
        "verified_native_library_count": len(native),
        "full_correctness_campaign_sha256": V3_CAMPAIGN_SHA256,
        "full_correctness_campaign_steps": 22,
        "initial_audit_failure_sha256": INITIAL_FAILURE_SHA256,
        "rust_optimization_verified": True,
        "capacity16_optimization_verified": True,
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
        raise AuditError("the unique capacity-16 integrity result already exists") from error
    except OSError as error:
        raise AuditError("cannot persist the unique capacity-16 practice integrity result") from error
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
        "capacity16_optimization_verified": True,
        "unchanged_reference_candidates": list(UNCHANGED_REFERENCE_CANDIDATES),
        "output": original.display_path(output_path),
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "failed": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("self-test", help="run only candidate-free synthetic historical and corruption controls")
    check = commands.add_parser("verify", help="independently replay the exact four-way capacity-16 public practice run")
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
