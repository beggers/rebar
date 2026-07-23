#!/usr/bin/env python3
"""Render only the independently proved Rust capture-initialization run."""

from __future__ import annotations

import argparse
import contextlib
import copy
import io
import json
from pathlib import Path

from tools import rust_v7_multi_candidate_practice_charts as original


ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "performance" / "v7" / "evidence"
PREFIX = EVIDENCE / "three-qualified-engines-public-practice-v8"
SUMMARY = EVIDENCE / "three-qualified-engines-public-practice-v8-summary.json"
RAW = EVIDENCE / "three-qualified-engines-public-practice-v8-raw.jsonl.gz"
INTEGRITY = EVIDENCE / "three-qualified-engines-public-practice-v8-integrity.json"
V8_AUDITOR = ROOT / "tools" / "rust_v7_multi_candidate_practice_v8_audit.py"
ROLE_CONFUSION_INCIDENT = EVIDENCE / "ZIG-STAGE-13-VERIFIER-INCIDENTS.md"
C_STAGE20_INCIDENT = EVIDENCE / "C-STAGE-20-INDEPENDENCE-AUDIT-RETRY.md"

HISTORIES = (
    {
        "version": 1,
        "renderer": "rust_v7_multi_candidate_practice_charts.py",
        "renderer_sha256": "5674fecff2b2555b725fd154cfdb1f7ee9ce7b951895c7a38f0f124f5304dddf",
        "summary_sha256": "20c33badfc08d98566c5476452370f042cd8ff544ecc5ed98f6d1111550328f0",
        "integrity_sha256": "8739803b6cd020b8b4f663223435fd1e39ef5603e90195b2a268a9fa7fbc0340",
        "slot": "three-qualified-engines-public-practice-v1",
        "schema": "rebar-v7-multi-candidate-practice-integrity-v1",
        "regressions": 426,
    },
    {
        "version": 2,
        "renderer": "rust_v7_multi_candidate_practice_v2_charts.py",
        "renderer_sha256": "3f81638918886de725500c23059b383e2773d493cbbfc5bb296f29721afd618d",
        "summary_sha256": "db3cc7f4704df7b0a6b1283818d0dfdf96947d83d44752bf633a640a3e721cab",
        "integrity_sha256": "82ef917ca82ba124af6311f3bf10398a2a040286ed06430919bbdd26dd61e057",
        "slot": "three-qualified-engines-fused-vectorcall-v2",
        "schema": "rebar-v7-multi-candidate-practice-integrity-v2",
        "regressions": 401,
    },
    {
        "version": 3,
        "renderer": "rust_v7_multi_candidate_practice_v3_charts.py",
        "renderer_sha256": "8e28587474b20fbd39af9a3df12bc5590b731864afac5b41a26310f55e6822be",
        "summary_sha256": "33ebdff8ecb061e3544b9cd4bc687040b8278aa037f3c993abe654daa665d155",
        "integrity_sha256": "aa1921230845a01aa03d607bd8609b3475dc659cacda5e6135d8b7064ed60c22",
        "slot": "three-qualified-engines-findall-capacity-16-v3",
        "schema": "rebar-v7-multi-candidate-practice-integrity-v3",
        "regressions": 387,
    },
    {
        "version": 4,
        "renderer": "rust_v7_multi_candidate_practice_v4_charts.py",
        "renderer_sha256": "bb0415c0a2a0da43c362535e3c0c8ffdab04686912510e0875eaf71678edf5b4",
        "summary_sha256": "e23164b077b2bfa1abccaf8cce93a068bc7ea9b7ef444ef55905cc2fbd573e0c",
        "integrity_sha256": "7bfb360fa570510d585c923345f00162da92a3a7cd6379528ad981b1ec003174",
        "slot": "three-qualified-engines-zig-span-256-v4",
        "schema": "rebar-v7-multi-candidate-practice-integrity-v4",
        "regressions": 402,
    },
    {
        "version": 5,
        "renderer": "rust_v7_multi_candidate_practice_v5_charts.py",
        "renderer_sha256": "d67869da13132b6b00f6478d794846363b7beac36ed36d02c9d6be955f23ad1d",
        "summary_sha256": "98c611410895f831d0b97a1677723186cc1e06d438d3437bfec9519743b1ad69",
        "integrity_sha256": "015a2f9e3ceebd3792c4de62828c2d63fbafd7a5f866c9513b60b964a974712e",
        "slot": "three-qualified-engines-rust-owned-common-prefix-v5",
        "schema": "rebar-v7-multi-candidate-practice-integrity-v5",
        "regressions": 407,
    },
    {
        "version": 6,
        "renderer": "rust_v7_multi_candidate_practice_v6_charts.py",
        "renderer_sha256": "b39cc0f565bca708ad8cfc7e29d842d20b3e97de2c73f83be61c60b282f12bb8",
        "summary_sha256": "22689cf92175274f935df81f51b07b4f2a0a90bafad3ae1bd2b0e9f905579fce",
        "integrity_sha256": "8804136b49d7203854bda098b4c224e1b62ae9ecc3d050e81378d1b9b9515134",
        "slot": "three-qualified-engines-c-stage-20-native-scanner-cmethod-v6",
        "schema": "rebar-v7-multi-candidate-practice-integrity-v6",
        "regressions": 407,
    },
    {
        "version": 7,
        "renderer": "rust_v7_multi_candidate_practice_v7_charts.py",
        "renderer_sha256": "ff7938dab6636a0cf37c02c6a5a66bcd2d7b8922bb89fc7601b64aa2066c3f0b",
        "summary_sha256": "89cf98bee40bb8e3ecc95861e07f302eff6c5f6288130854ea806578e8b76d79",
        "integrity_sha256": "d7c51632e9e9419b1e309897eed0f60b1d0af5ffc1cecd66413874a8d487212d",
        "slot": "three-qualified-engines-zig-stage-13-interned-dispatch-v7",
        "schema": "rebar-v7-multi-candidate-practice-integrity-v7",
        "regressions": 259,
    },
)

V8_SLOT = "three-qualified-engines-rust-capture-initialization-v8"
V8_SCHEMA = "rebar-v7-multi-candidate-practice-integrity-v8"

# Pin only the genuine, complete, one-shot four-way public-practice result.
V8_SUMMARY_SHA256: str | None = "77d3aa8ac970e126d11c9e9aad832f480670aceda1778966d16a4a768ca5a4c3"
V8_COMPRESSED_RAW_SHA256: str | None = "f67cd7ddc0dff0cd256b156e23bfc8efc39546df8a4aec909cd9034261c91289"
V8_RAW_SHA256: str | None = "32a265fa68ce82e76572c33696f41a605c2ea1b572d31411badbe78ff3cff8d4"
V8_REGRESSIONS: int | None = 261
V8_RUST_EDGE_REPORT_SHA256: str | None = "c3e67b08ac34540dbbd248b5ffb07161ae7e9b815a6f6bcbc757ef178f7585b1"
V8_RUST_CAMPAIGN_SHA256: str | None = "9ddbab81b16f0440ca19bffb8a539ea08d4a7ff33606ee3019eaf85977c2249a"

V8_AUDIT_SHA256 = "55ab21dfa78193c96551f5d3d95a51251f30e535cdb37c24df3d2e6044166854"
V8_RUST_ENGINE_SOURCE_SHA256 = "4b89d916e4c33e2b516be570ff3e75694f03dcea5eccf9320cedf07471b07dac"
V8_RUST_NATIVE_ENGINE_SHA256 = "e7177c97070b2d0073a721044c4d23bb93e0d0883c1f2ccaa07c41eda8b96255"
V8_RUST_DEEP_CONTRACT_SHA256 = "6a04536315e0f2af9ca129179b539b629614dcdd707f62ac61c5f24fe05a5a33"
V8_RUST_OBSERVABILITY_SHA256 = "6a2d4ec435109e0f96092d65c27092c9e6b1c3eea21b21f4962aae10a0a9cb8e"
UNCHANGED_RUST_BRIDGE_SOURCE_SHA256 = "83afb5a709a6d0ea1701dfd64db30644edbf2cb0276c2db731a8119cfd52d8ed"
UNCHANGED_RUST_NATIVE_BRIDGE_SHA256 = "1f072e81ba9339a8b2e52a7e93b7bcde791c4d518620b6bd760af67c7c89af34"
C_CAMPAIGN_SHA256 = "c211d826032fed60c30024beb6de66c3e20b08fdcb936b53393d0a5fdba09721"
ZIG_CAMPAIGN_SHA256 = "4ba7cb9c45a70b747cc0a6eb721f6bb51081157f527d1bf5e578e603715ae5dc"
INITIAL_AUDIT_FAILURE_SHA256 = "ccaf3813b29badcf80c552dc0d850f83a2ca122cc3cc3057576dd519aed4f088"
ROLE_CONFUSION_INCIDENT_SHA256 = "84efcdbd0059ab430c84322695bf472f66fdc1cc05efd74e383b62114efcedff"
C_STAGE20_INCIDENT_SHA256 = "0ee24eabfe369328c3dcd03c2dabab80f46a3851e82b6dbf4b390a72667149c4"
REFERENCE_MODULES = (original.BASELINE, original.C_ENGINE, original.ZIG)
SUFFIXES = ("overall", "outcomes", "api", "regressions", "memory", "rankings")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def actual_digest(value: str | None, label: str) -> str:
    require(
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value),
        f"the genuine capture-initialization {label} is NOT MEASURED or unqualified",
    )
    return value


def actual_regressions() -> int:
    require(
        isinstance(V8_REGRESSIONS, int)
        and not isinstance(V8_REGRESSIONS, bool)
        and 0 <= V8_REGRESSIONS <= 624 * 3,
        "the genuine capture-initialization slowdown count is NOT MEASURED or invalid",
    )
    return V8_REGRESSIONS


def check_renderers() -> None:
    for entry in HISTORIES:
        path = ROOT / "tools" / entry["renderer"]
        require(original.sha256_file(path) == entry["renderer_sha256"], f"the preserved v{entry['version']} graph renderer changed")
    require(
        Path(original.__file__).resolve()
        == (ROOT / "tools" / "rust_v7_multi_candidate_practice_charts.py").resolve(),
        "the frozen pure original graph renderer was substituted",
    )
    first = HISTORIES[0]
    require(original.SLOT == first["slot"], "the frozen original practice slot changed")
    require(original.INTEGRITY_SCHEMA == first["schema"], "the original replay schema changed")
    require(original.EXPECTED_REGRESSIONS == first["regressions"], "the original slowdown boundary changed")
    require(original.CHART_SUFFIXES == SUFFIXES, "a separately required historical graph was dropped")
    require(original.CASES == 624, "the frozen practice denominator changed")
    require(original.TRIALS == 7, "the frozen paired-trial denominator changed")
    require(original.BOOTSTRAPS == 499, "the frozen confidence protocol changed")
    require(original.RAW_ROWS == 17_472, "the frozen raw-observation denominator changed")
    require(original.CORRECTNESS_CHECKS == 52_416, "a frozen timing correctness check was dropped")
    require(
        original.MODULES == (
            "re",
            "candidates.rust_candidate",
            "candidates.vm_candidate",
            "candidates.zig_candidate",
        ),
        "the Python baseline or an independently implemented replacement changed",
    )
    require(len(original.API_COUNTS) == 12, "a public operation was excluded")


@contextlib.contextmanager
def v8_renderer(*, synthetic: bool = False):
    """Temporarily install exact v8 controls and restore all v1 controls."""

    check_renderers()
    previous = (original.SLOT, original.INTEGRITY_SCHEMA, original.EXPECTED_REGRESSIONS)
    original.SLOT = V8_SLOT
    original.INTEGRITY_SCHEMA = V8_SCHEMA
    original.EXPECTED_REGRESSIONS = HISTORIES[0]["regressions"] if synthetic else actual_regressions()
    try:
        yield
    finally:
        original.SLOT, original.INTEGRITY_SCHEMA, original.EXPECTED_REGRESSIONS = previous
        check_renderers()


def check_history() -> tuple[tuple[dict, dict], ...]:
    checked: list[tuple[dict, dict]] = []
    for entry in HISTORIES:
        version = entry["version"]
        name = f"three-qualified-engines-public-practice-v{version}"
        summary_path = EVIDENCE / f"{name}-summary.json"
        integrity_path = EVIDENCE / f"{name}-integrity.json"
        require(original.sha256_file(summary_path) == entry["summary_sha256"], f"the historical v{version} practice summary changed")
        require(original.sha256_file(integrity_path) == entry["integrity_sha256"], f"the historical v{version} standalone replay changed")
        summary = original.read_json(summary_path)
        integrity = original.read_json(integrity_path)
        require(summary.get("exclusive_slot") == entry["slot"], f"historical practice v{version} was relabeled")
        require(integrity.get("schema") == entry["schema"], f"historical v{version} replay provenance changed")
        require(integrity.get("result") == "PASS", f"the preserved v{version} independent practice audit failed")
        require(integrity.get("summary_sha256") == entry["summary_sha256"], f"historical v{version} results lost their source identity")
        require(integrity.get("strict_regressions") == entry["regressions"], f"historical v{version} slowdowns were changed")
        for earlier in HISTORIES[: version - 1]:
            key = f"historical_v{earlier['version']}_integrity_sha256"
            require(integrity.get(key) == earlier["integrity_sha256"], f"historical v{earlier['version']}-to-v{version} continuity was lost")
        checked.append((summary, integrity))
    return tuple(checked)


def check_v8_metadata(summary: dict, integrity: dict) -> None:
    expected = {
        "schema": V8_SCHEMA,
        "result": "PASS",
        "holdout_accessed": False,
        "timing_performed": False,
        "module_order": list(original.MODULES),
        "cases_per_candidate": 624,
        "candidate_case_count": 1_872,
        "trials_per_module_case": 7,
        "raw_rows": 17_472,
        "correctness_checks": 52_416,
        "bootstrap_draws": 499,
        "strict_regressions": actual_regressions(),
        "summary_sha256": actual_digest(V8_SUMMARY_SHA256, "actual one-shot practice summary"),
        "compressed_raw_sha256": actual_digest(V8_COMPRESSED_RAW_SHA256, "actual compressed paired observations"),
        "raw_sha256": actual_digest(V8_RAW_SHA256, "actual uncompressed paired observations"),
        "from_scratch_audit_sha256": V8_AUDIT_SHA256,
        "full_correctness_campaign_sha256": actual_digest(V8_RUST_CAMPAIGN_SHA256, "passing complete Rust 22-stage campaign"),
        "rust_deep_contract_sha256": V8_RUST_DEEP_CONTRACT_SHA256,
        "rust_deep_contract_checks": 393,
        "rust_observability_sha256": V8_RUST_OBSERVABILITY_SHA256,
        "rust_observability_checks": 479,
        "rust_observability_binder_checks": 34,
        "c_full_correctness_campaign_sha256": C_CAMPAIGN_SHA256,
        "zig_full_correctness_campaign_sha256": ZIG_CAMPAIGN_SHA256,
        "initial_audit_failure_sha256": INITIAL_AUDIT_FAILURE_SHA256,
        "role_confusion_incident_sha256": ROLE_CONFUSION_INCIDENT_SHA256,
        "role_confusion_incident_path": str(ROLE_CONFUSION_INCIDENT.resolve()),
        "c_stage20_verifier_incident_sha256": C_STAGE20_INCIDENT_SHA256,
        "c_stage20_verifier_incident_path": str(C_STAGE20_INCIDENT.resolve()),
        "unchanged_reference_candidates": list(REFERENCE_MODULES),
        "rust_optimization_verified": True,
        "capacity16_optimization_verified": True,
        "zig_optimization_verified": True,
        "mandatory_prefix_optimization_verified": True,
        "unchanged_rust_bridge_verified": True,
        "c_optimization_verified": True,
        "zig_interned_attributes_optimization_verified": True,
        "rust_capture_initialization_optimization_verified": True,
    }
    for entry in HISTORIES:
        expected[f"historical_v{entry['version']}_integrity_sha256"] = entry["integrity_sha256"]
    for key, value in expected.items():
        require(integrity.get(key) == value, f"the independent capture-initialization results audit does not verify {key}")
    require(summary.get("exclusive_slot") == V8_SLOT, "the genuine capture-initialization exclusive timing slot changed")
    require(summary.get("cohort") == "calibration", "a non-public case entered practice")
    require(summary.get("holdout_accessed") is False, "unseen final-test data entered practice")
    require(summary.get("failed") == 0, "a capture-initialization timing correctness gate failed")
    require(summary.get("compressed_raw_sha256") == actual_digest(V8_COMPRESSED_RAW_SHA256, "compressed observations"), "complete compressed practice observations changed")
    require(summary.get("raw_sha256") == actual_digest(V8_RAW_SHA256, "uncompressed observations"), "complete uncompressed practice observations changed")
    require(original.sha256_file(V8_AUDITOR) == integrity.get("source_sha256"), "the independent v8 source-bound results auditor was substituted")
    require(original.sha256_file(ROLE_CONFUSION_INCIDENT) == ROLE_CONFUSION_INCIDENT_SHA256, "the preserved Zig verifier incident changed")
    require(original.sha256_file(C_STAGE20_INCIDENT) == C_STAGE20_INCIDENT_SHA256, "the preserved C Stage 20 verifier incident changed")


def check_unchanged_references(summary: dict, integrity: dict, v7_summary: dict, v7_integrity: dict) -> None:
    old = v7_summary.get("candidate_binary_sha256_before")
    measured = summary.get("candidate_binary_sha256_before")
    require(isinstance(old, dict) and isinstance(measured, dict), "historical or actual candidate fingerprints are missing")
    require(summary.get("candidate_binary_sha256_after") == measured, "a candidate changed during paired timing")
    for module in REFERENCE_MODULES:
        prefix = f"{module}:"
        historical = {role: digest for role, digest in old.items() if role.startswith(prefix)}
        current = {role: digest for role, digest in measured.items() if role.startswith(prefix)}
        require(bool(historical) and current == historical, f"a fixed standard Python, C, or Zig reference changed: {module}")

    historical_sources = v7_integrity.get("qualified_source_fingerprints")
    current_sources = integrity.get("qualified_source_fingerprints")
    require(isinstance(historical_sources, dict) and isinstance(current_sources, dict), "current or historical production source identity is missing")
    changed = "candidates/rust/src/lib.rs"
    require(current_sources.get(changed) == V8_RUST_ENGINE_SOURCE_SHA256, "the qualifying capture-initialization Rust source was substituted")
    require(historical_sources.get(changed) != V8_RUST_ENGINE_SOURCE_SHA256, "practice reused the historical Rust engine source")
    for path, digest in historical_sources.items():
        if path != changed:
            require(current_sources.get(path) == digest, f"an unrelated Python, C, Zig, or Rust bridge/helper source changed: {path}")

    engine_key = f"{original.RUST}:native-engine"
    engine_source_key = f"{original.RUST}:native-source"
    bridge_key = f"{original.RUST}:native-bridge"
    bridge_source_key = f"{original.RUST}:bridge-source"
    require(measured.get(engine_key) == V8_RUST_NATIVE_ENGINE_SHA256, "the qualifying capture-initialization Rust engine was substituted")
    require(old.get(engine_key) != V8_RUST_NATIVE_ENGINE_SHA256, "practice reused the historical Rust engine")
    require(measured.get(engine_source_key) == V8_RUST_ENGINE_SOURCE_SHA256, "the measured Rust engine source identity is missing")
    require(measured.get(bridge_key) == old.get(bridge_key) == UNCHANGED_RUST_NATIVE_BRIDGE_SHA256, "the fixed native Rust bridge changed")
    require(measured.get(bridge_source_key) == old.get(bridge_source_key) == UNCHANGED_RUST_BRIDGE_SOURCE_SHA256, "the fixed Rust bridge source changed")
    for key, digest in old.items():
        if key.startswith(f"{original.RUST}:") and key not in {engine_key, engine_source_key}:
            require(measured.get(key) == digest, f"an unrelated public Rust surface or bridge changed: {key}")


def check_current_edge(summary: dict) -> None:
    expected = actual_digest(V8_RUST_EDGE_REPORT_SHA256, "passing capture-initialization edge-correctness proof")
    proofs = summary.get("verified_edge_oracles")
    require(isinstance(proofs, list), "fresh standalone correctness proofs are missing")
    rust = [row for row in proofs if isinstance(row, dict) and row.get("module") == original.RUST]
    require(len(rust) == 1, "the actual passing Rust proof is absent or duplicated")
    require(rust[0].get("report_sha256") == expected, "practice used a different Rust engine than the passing edge proof")


def load_results(summary_path: Path, raw_path: Path, integrity_path: Path):
    require(summary_path.resolve() == SUMMARY.resolve(), "refusing an unrelated capture-initialization summary")
    require(raw_path.resolve() == RAW.resolve(), "refusing unrelated capture-initialization timing rows")
    require(integrity_path.resolve() == INTEGRITY.resolve(), "refusing unrelated capture-initialization integrity evidence")
    require(original.sha256_file(summary_path) == actual_digest(V8_SUMMARY_SHA256, "actual one-shot practice summary"), "the actual one-shot Rust summary changed")
    require(original.sha256_file(raw_path) == actual_digest(V8_COMPRESSED_RAW_SHA256, "actual one-shot compressed observations"), "the actual one-shot Rust observations changed")
    histories = check_history()
    v7_summary, v7_integrity = histories[-1]
    summary = original.read_json(summary_path)
    integrity = original.read_json(integrity_path)
    check_v8_metadata(summary, integrity)
    check_unchanged_references(summary, integrity, v7_summary, v7_integrity)
    check_current_edge(summary)
    with v8_renderer():
        results = original.load_results(summary_path, raw_path, integrity_path)
        charts = original.build_charts(results)
    require(tuple(charts) == SUFFIXES, "a separately required Rust practice graph was omitted")
    for suffix, chart in charts.items():
        require("PRACTICE ONLY" in chart, f"the {suffix} graph omitted its public-only disclosure")
        require("final speed NOT MEASURED" in chart, f"the {suffix} graph invented a final performance result")
    return results, charts


def expect_rejection(action, label: str) -> None:
    try:
        action()
    except (ValueError, TypeError, KeyError, OverflowError):
        return
    raise ValueError(f"synthetic capture-initialization version-isolation evidence was accepted: {label}")


def self_test() -> None:
    check_renderers()
    captured = io.StringIO()
    with v8_renderer(synthetic=True):
        with contextlib.redirect_stdout(captured):
            original.self_test()
        summary, integrity, _raw, summary_digest, compressed_digest, raw_digest = original.synthetic_documents()
        original_controls = json.loads(captured.getvalue())
        require(isinstance(original_controls, dict) and original_controls.get("result") == "PASS", "the original deterministic SVG corruption controls failed")
        require(original_controls.get("synthetic_only") is True, "synthetic controls inspected actual practice data")
        require(original_controls.get("holdout_accessed") is False, "synthetic controls accessed hidden cases")
        require(original_controls.get("timing_performed") is False, "synthetic controls timed a production candidate")
        require(original_controls.get("corruption_checks", 0) >= 33, "original evidence-poisoning controls were weakened")
        require(original_controls.get("chart_count") == len(SUFFIXES), "synthetic controls omitted a required graph")
        extras: list[str] = []

        def reject_summary(key: str, value: object, label: str) -> None:
            poisoned = copy.deepcopy(summary)
            poisoned[key] = value
            expect_rejection(lambda: original.check_summary(poisoned), label)
            extras.append(label)

        def reject_integrity(key: str, value: object, label: str) -> None:
            poisoned = copy.deepcopy(integrity)
            poisoned[key] = value
            expect_rejection(
                lambda: original.check_integrity(
                    summary,
                    poisoned,
                    summary_digest=summary_digest,
                    compressed_digest=compressed_digest,
                    raw_digest=raw_digest,
                ),
                label,
            )
            extras.append(label)

        for entry in HISTORIES:
            version = entry["version"]
            reject_summary("exclusive_slot", entry["slot"], f"historical-v{version}-slot-substitution")
            reject_integrity("schema", entry["schema"], f"historical-v{version}-replay-substitution")
        reject_summary("exclusive_slot", "three-qualified-engines-public-practice-v8", "invented-rust-capture-timing-slot")
        reject_summary("holdout_accessed", True, "unseen-final-case-access")
        reject_summary("paired_raw_rows", original.RAW_ROWS - 1, "missing-paired-practice-observation")
        reject_summary("correctness_checks", original.CORRECTNESS_CHECKS - 1, "missing-public-practice-correctness-gate")
        reject_summary("modules", list(reversed(original.MODULES)), "substituted-python-baseline-or-independent-candidates")
        reject_summary("bootstrap_samples", original.BOOTSTRAPS - 1, "changed-bootstrap-confidence-draws")
        reject_summary("trials", original.TRIALS - 1, "omitted-paired-timing-trial")
        reject_integrity("summary_sha256", "0" * 64, "substituted-rust-capture-summary")
        reject_integrity("compressed_raw_sha256", "0" * 64, "substituted-compressed-capture-observations")
        reject_integrity("raw_sha256", "0" * 64, "substituted-uncompressed-capture-observations")
        reject_integrity("strict_regressions", HISTORIES[0]["regressions"] - 1, "concealed-synthetic-substantial-slowdown")
        reject_integrity("timing_performed", True, "independent-replay-performs-benchmark-timing")

        data = original.PracticeResults(
            summary,
            integrity,
            tuple(sorted(original.check_summary(summary), key=lambda item: (-item.ranking["geomean_speedup"], original.DISPLAY[item.module]))),
        )
        charts = original.build_charts(data)
        require(tuple(charts) == SUFFIXES, "a separate synthetic capture graph was omitted")
        require("shared process" in charts["memory"], "a graph concealed shared-process memory limitations")
        require("does not measure native" in charts["memory"], "a graph invented native-memory observations")
        require(original.build_charts(data) == charts, "capture-initialization graphs are not deterministic")

    check_renderers()
    poisoned = original_controls["corruption_checks"] + len(extras)
    require(poisoned >= 57, "historical synthetic corruption controls were weakened")
    print(json.dumps({
        "schema": f"{V8_SCHEMA}-charts-self-test",
        "result": "PASS",
        "synthetic_only": True,
        "holdout_accessed": False,
        "timing_performed": False,
        "historical_renderer_sha256": {f"v{row['version']}": row["renderer_sha256"] for row in HISTORIES},
        "historical_renderers_restored": True,
        "cases_per_candidate": original.CASES,
        "candidate_case_count": original.CASES * len(original.CANDIDATES),
        "trials_per_module_case": original.TRIALS,
        "raw_rows": original.RAW_ROWS,
        "correctness_checks": original.CORRECTNESS_CHECKS,
        "bootstrap_draws": original.BOOTSTRAPS,
        "original_poison_controls": original_controls["corruption_checks"],
        "additional_version_poison_controls": extras,
        "poisoned_control_count": poisoned,
        "chart_count": len(SUFFIXES),
        "charts_deterministic": True,
        "final_speed": "NOT MEASURED",
    }, sort_keys=True))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate six independently verified Rust capture-initialization public-practice graphs.")
    parser.add_argument("--summary", type=Path, default=SUMMARY)
    parser.add_argument("--raw", type=Path, default=RAW)
    parser.add_argument("--integrity", type=Path, default=INTEGRITY)
    parser.add_argument("--prefix", type=Path, default=PREFIX)
    parser.add_argument("--self-test", action="store_true", help="run synthetic-only historical-isolation and deterministic SVG controls")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.self_test:
        self_test()
        return

    check_renderers()
    prefix = args.prefix.resolve()
    require(prefix == PREFIX.resolve(), "refusing to overwrite a historical or unrelated public practice graph")
    require(prefix.parent == EVIDENCE.resolve(), "refusing to write outside public practice evidence")
    _results, charts = load_results(args.summary.resolve(), args.raw.resolve(), args.integrity.resolve())
    for suffix in SUFFIXES:
        destination = prefix.parent / f"{prefix.name}-{suffix}.svg"
        destination.write_text(charts[suffix], encoding="utf-8")
        print(f"wrote {destination.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
