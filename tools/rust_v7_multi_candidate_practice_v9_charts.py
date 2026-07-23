#!/usr/bin/env python3
"""Render only source-bound C Stage 21 public practice under performance/v7."""

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
PREFIX = EVIDENCE / "three-qualified-engines-public-practice-v9"
SUMMARY = EVIDENCE / "three-qualified-engines-public-practice-v9-summary.json"
RAW = EVIDENCE / "three-qualified-engines-public-practice-v9-raw.jsonl.gz"
INTEGRITY = EVIDENCE / "three-qualified-engines-public-practice-v9-integrity.json"
V9_PRACTICE_AUDITOR = ROOT / "tools" / "rust_v7_multi_candidate_practice_v9_audit.py"
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
    {
        "version": 8,
        "renderer": "rust_v7_multi_candidate_practice_v8_charts.py",
        "renderer_sha256": "d8dc3d0a30d9106c7ec5a1892396838989b93f70c4e3d95448c19e3fbe93ebfd",
        "summary_sha256": "77d3aa8ac970e126d11c9e9aad832f480670aceda1778966d16a4a768ca5a4c3",
        "integrity_sha256": "b2c9aa305abe0436c3566ed3ccf18b4947bff81b3dc3e898b2a1e1545ab10459",
        "slot": "three-qualified-engines-rust-capture-initialization-v8",
        "schema": "rebar-v7-multi-candidate-practice-integrity-v8",
        "regressions": 261,
    },
)

V9_PRACTICE_SLOT = "three-qualified-engines-c-stage-21-singleton-split-memchr-v9"
V9_PRACTICE_SCHEMA = "rebar-v7-multi-candidate-practice-integrity-v9"

# Pin only the genuine completed one-shot public-practice result.
V9_PRACTICE_SUMMARY_SHA256: str | None = "e0140380d6b3026e6195f27d3188e87e6d646b08d0e632c5e9eda38674e616ed"
V9_PRACTICE_COMPRESSED_RAW_SHA256: str | None = "004ef3e8ddb1bd81f88c6742843e3d5bc7c29ed4bfea120d40d3d28fdae4a651"
V9_PRACTICE_RAW_SHA256: str | None = "493f3d8ec3c0a030891306b71353714e7165d60a5ec12e629fa0bfcfd5558200"
V9_PRACTICE_REGRESSIONS: int | None = 256
V9_C_EDGE_REPORT_SHA256: str | None = "c843dccc2d0b8eb1dcada2af282679ca05a1be2de98afc39bad95e7f448f4d7a"
V9_C_SOURCE_SHA256: str | None = "2253ddd8608a19a06f25ed41251729365ecb1e25f6829f710cdcb858b10c4e0c"
V9_C_NATIVE_ENGINE_SHA256: str | None = "f6458cb4bf190f042e7d417a40020d2d58cebcb39671fda7352aab9725a7f633"
V9_C_CAMPAIGN_SHA256: str | None = "a29b540e01fc9f565e01e5cc62af14db30b38d9bacbaf55e4950e95b17c7ea40"
V9_PRACTICE_SOURCE_AUDIT_SHA256: str | None = "a790fe1a75c8748df7f8bb6f1e39d0be841636055358aaee94db0aa35523f326"
V9_C_DEEP_CONTRACT_SHA256: str | None = "907d6c684cd5e7161ef27b167f1d3bdd18243dff61bad4d5586ff3ef5b2d13cd"
V9_C_OBSERVABILITY_SHA256: str | None = "0a975f63d3a5e20e317e3dc08c1324ce95a8ed371923b53c18e65f49c6414b8a"

RUST_CAPTURE_CAMPAIGN_SHA256 = "9ddbab81b16f0440ca19bffb8a539ea08d4a7ff33606ee3019eaf85977c2249a"
ZIG_STAGE13_CAMPAIGN_SHA256 = "4ba7cb9c45a70b747cc0a6eb721f6bb51081157f527d1bf5e578e603715ae5dc"
INITIAL_AUDIT_FAILURE_SHA256 = "ccaf3813b29badcf80c552dc0d850f83a2ca122cc3cc3057576dd519aed4f088"
ROLE_CONFUSION_INCIDENT_SHA256 = "84efcdbd0059ab430c84322695bf472f66fdc1cc05efd74e383b62114efcedff"
C_STAGE20_INCIDENT_SHA256 = "0ee24eabfe369328c3dcd03c2dabab80f46a3851e82b6dbf4b390a72667149c4"
REFERENCE_MODULES = (original.BASELINE, original.RUST, original.ZIG)
SUFFIXES = ("overall", "outcomes", "api", "regressions", "memory", "rankings")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def actual_digest(value: str | None, label: str) -> str:
    require(
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value),
        f"the genuine C Stage 21 public-practice {label} is NOT MEASURED or unqualified",
    )
    return value


def actual_regressions() -> int:
    require(
        isinstance(V9_PRACTICE_REGRESSIONS, int)
        and not isinstance(V9_PRACTICE_REGRESSIONS, bool)
        and 0 <= V9_PRACTICE_REGRESSIONS <= 624 * 3,
        "the genuine C Stage 21 public-practice loss count is NOT MEASURED or invalid",
    )
    return V9_PRACTICE_REGRESSIONS


def check_renderers() -> None:
    for entry in HISTORIES:
        source = ROOT / "tools" / entry["renderer"]
        require(original.sha256_file(source) == entry["renderer_sha256"], f"the preserved v{entry['version']} practice renderer changed")
    require(
        Path(original.__file__).resolve()
        == (ROOT / "tools" / "rust_v7_multi_candidate_practice_charts.py").resolve(),
        "the pure original public-practice chart renderer was substituted",
    )
    first = HISTORIES[0]
    require(original.SLOT == first["slot"], "the original public-practice slot changed")
    require(original.INTEGRITY_SCHEMA == first["schema"], "the original public-practice replay schema changed")
    require(original.EXPECTED_REGRESSIONS == first["regressions"], "the original slowdown controls changed")
    require(original.CHART_SUFFIXES == SUFFIXES, "a separately required public-practice graph was omitted")
    require(original.CASES == 624, "the frozen public-practice case denominator changed")
    require(original.TRIALS == 7, "the frozen public-practice paired-trial denominator changed")
    require(original.BOOTSTRAPS == 499, "the frozen public-practice confidence protocol changed")
    require(original.RAW_ROWS == 17_472, "the frozen public-practice raw-observation count changed")
    require(original.CORRECTNESS_CHECKS == 52_416, "a public-practice timing correctness check was dropped")
    require(
        original.MODULES == (
            "re",
            "candidates.rust_candidate",
            "candidates.vm_candidate",
            "candidates.zig_candidate",
        ),
        "the standard Python baseline or an independent replacement changed",
    )
    require(len(original.API_COUNTS) == 12, "a frozen public-practice operation was omitted")


@contextlib.contextmanager
def v9_practice_renderer(*, synthetic: bool = False):
    """Scope only public-practice constants and always restore v1 state."""

    check_renderers()
    saved = (original.SLOT, original.INTEGRITY_SCHEMA, original.EXPECTED_REGRESSIONS)
    original.SLOT = V9_PRACTICE_SLOT
    original.INTEGRITY_SCHEMA = V9_PRACTICE_SCHEMA
    original.EXPECTED_REGRESSIONS = HISTORIES[0]["regressions"] if synthetic else actual_regressions()
    try:
        yield
    finally:
        original.SLOT, original.INTEGRITY_SCHEMA, original.EXPECTED_REGRESSIONS = saved
        check_renderers()


def check_history() -> tuple[tuple[dict, dict], ...]:
    histories: list[tuple[dict, dict]] = []
    for entry in HISTORIES:
        version = entry["version"]
        prefix = f"three-qualified-engines-public-practice-v{version}"
        summary_path = EVIDENCE / f"{prefix}-summary.json"
        integrity_path = EVIDENCE / f"{prefix}-integrity.json"
        require(original.sha256_file(summary_path) == entry["summary_sha256"], f"the immutable public-practice v{version} summary changed")
        require(original.sha256_file(integrity_path) == entry["integrity_sha256"], f"the immutable public-practice v{version} integrity report changed")
        summary = original.read_json(summary_path)
        integrity = original.read_json(integrity_path)
        require(summary.get("exclusive_slot") == entry["slot"], f"public-practice v{version} was relabeled")
        require(integrity.get("schema") == entry["schema"], f"the public-practice v{version} audit schema changed")
        require(integrity.get("result") == "PASS", f"the original public-practice v{version} replay failed")
        require(integrity.get("summary_sha256") == entry["summary_sha256"], f"public-practice v{version} lost its historical identity")
        require(integrity.get("strict_regressions") == entry["regressions"], f"public-practice v{version} historical losses changed")
        for previous in HISTORIES[: version - 1]:
            key = f"historical_v{previous['version']}_integrity_sha256"
            require(integrity.get(key) == previous["integrity_sha256"], f"public-practice v{previous['version']}-to-v{version} continuity was lost")
        histories.append((summary, integrity))
    return tuple(histories)


def check_v9_practice_metadata(summary: dict, integrity: dict) -> None:
    expected = {
        "schema": V9_PRACTICE_SCHEMA,
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
        "summary_sha256": actual_digest(V9_PRACTICE_SUMMARY_SHA256, "complete one-shot practice summary"),
        "compressed_raw_sha256": actual_digest(V9_PRACTICE_COMPRESSED_RAW_SHA256, "complete compressed practice observations"),
        "raw_sha256": actual_digest(V9_PRACTICE_RAW_SHA256, "complete uncompressed practice observations"),
        "from_scratch_audit_sha256": actual_digest(V9_PRACTICE_SOURCE_AUDIT_SHA256, "passing all-five-native source audit"),
        "full_correctness_campaign_sha256": actual_digest(V9_C_CAMPAIGN_SHA256, "passing complete 22-stage C campaign"),
        "c_deep_contract_sha256": actual_digest(V9_C_DEEP_CONTRACT_SHA256, "passing 393-check C contract proof"),
        "c_deep_contract_checks": 393,
        "c_observability_sha256": actual_digest(V9_C_OBSERVABILITY_SHA256, "passing 479-check C observability proof"),
        "c_observability_checks": 479,
        "c_observability_binder_checks": 34,
        "rust_full_correctness_campaign_sha256": RUST_CAPTURE_CAMPAIGN_SHA256,
        "zig_full_correctness_campaign_sha256": ZIG_STAGE13_CAMPAIGN_SHA256,
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
        "c_singleton_split_memchr_optimization_verified": True,
    }
    for entry in HISTORIES:
        expected[f"historical_v{entry['version']}_integrity_sha256"] = entry["integrity_sha256"]
    for key, value in expected.items():
        require(integrity.get(key) == value, f"the independent C Stage 21 public-practice audit does not prove {key}")
    require(summary.get("exclusive_slot") == V9_PRACTICE_SLOT, "the exact C Stage 21 public-practice slot changed")
    require(summary.get("cohort") == "calibration", "a non-public workload entered practice")
    require(summary.get("holdout_accessed") is False, "hidden cases entered the public practice report")
    require(summary.get("failed") == 0, "a Stage 21 public-practice correctness gate failed")
    require(summary.get("compressed_raw_sha256") == actual_digest(V9_PRACTICE_COMPRESSED_RAW_SHA256, "compressed practice observations"), "compressed public observations changed")
    require(summary.get("raw_sha256") == actual_digest(V9_PRACTICE_RAW_SHA256, "uncompressed practice observations"), "uncompressed public observations changed")
    require(original.sha256_file(V9_PRACTICE_AUDITOR) == integrity.get("source_sha256"), "the standalone public-practice replay auditor was substituted")
    require(original.sha256_file(ROLE_CONFUSION_INCIDENT) == ROLE_CONFUSION_INCIDENT_SHA256, "the preserved Zig verifier incident changed")
    require(original.sha256_file(C_STAGE20_INCIDENT) == C_STAGE20_INCIDENT_SHA256, "the preserved C Stage 20 verifier incident changed")


def check_unchanged_references(summary: dict, integrity: dict, previous_summary: dict, previous_integrity: dict) -> None:
    before = previous_summary.get("candidate_binary_sha256_before")
    current = summary.get("candidate_binary_sha256_before")
    require(isinstance(before, dict) and isinstance(current, dict), "historical or actual public candidate fingerprints are missing")
    require(summary.get("candidate_binary_sha256_after") == current, "a candidate changed during paired public practice")
    for module in REFERENCE_MODULES:
        prefix = f"{module}:"
        old = {role: digest for role, digest in before.items() if role.startswith(prefix)}
        new = {role: digest for role, digest in current.items() if role.startswith(prefix)}
        require(bool(old) and old == new, f"the fixed Python, Rust, or Zig reference changed: {module}")

    old_sources = previous_integrity.get("qualified_source_fingerprints")
    new_sources = integrity.get("qualified_source_fingerprints")
    require(isinstance(old_sources, dict) and isinstance(new_sources, dict), "current or historical candidate source provenance is absent")
    changed = "candidates/_vm_native.c"
    actual_source = actual_digest(V9_C_SOURCE_SHA256, "actual Stage 21 C native source")
    require(new_sources.get(changed) == actual_source, "the qualified C Stage 21 source was substituted")
    require(old_sources.get(changed) != actual_source, "the experiment reused the historical C source")
    for path, digest in old_sources.items():
        if path != changed:
            require(new_sources.get(path) == digest, f"an unrelated Python, Rust, Zig, or C surface changed: {path}")

    changed_role = f"{original.C_ENGINE}:native-engine"
    actual_native = actual_digest(V9_C_NATIVE_ENGINE_SHA256, "actual Stage 21 mapped C engine")
    require(current.get(changed_role) == actual_native, "the passing mapped Stage 21 C engine was substituted")
    require(before.get(changed_role) != actual_native, "the experiment reused the historical mapped C engine")
    for role, digest in before.items():
        if role.startswith(f"{original.C_ENGINE}:") and role != changed_role:
            require(current.get(role) == digest, f"an unrelated public C surface changed: {role}")


def check_current_edge(summary: dict) -> None:
    expected = actual_digest(V9_C_EDGE_REPORT_SHA256, "fresh passing Stage 21 C edge proof")
    edge_oracles = summary.get("verified_edge_oracles")
    require(isinstance(edge_oracles, list), "actual public-practice correctness proofs are missing")
    matching = [proof for proof in edge_oracles if isinstance(proof, dict) and proof.get("module") == original.C_ENGINE]
    require(len(matching) == 1, "the fresh Stage 21 C edge proof is missing or duplicated")
    require(matching[0].get("report_sha256") == expected, "the measured Stage 21 C engine differs from the passing edge proof")


def load_results(summary_path: Path, raw_path: Path, integrity_path: Path):
    require(summary_path.resolve() == SUMMARY.resolve(), "refusing an unrelated public-practice version-9 summary")
    require(raw_path.resolve() == RAW.resolve(), "refusing unrelated public-practice version-9 observations")
    require(integrity_path.resolve() == INTEGRITY.resolve(), "refusing unrelated public-practice version-9 integrity evidence")
    require(original.sha256_file(summary_path) == actual_digest(V9_PRACTICE_SUMMARY_SHA256, "actual public-practice summary"), "the actual one-shot C Stage 21 summary changed")
    require(original.sha256_file(raw_path) == actual_digest(V9_PRACTICE_COMPRESSED_RAW_SHA256, "actual public-practice compressed observations"), "the actual one-shot C Stage 21 rows changed")
    histories = check_history()
    previous_summary, previous_integrity = histories[-1]
    summary = original.read_json(summary_path)
    integrity = original.read_json(integrity_path)
    check_v9_practice_metadata(summary, integrity)
    check_unchanged_references(summary, integrity, previous_summary, previous_integrity)
    check_current_edge(summary)
    with v9_practice_renderer():
        results = original.load_results(summary_path, raw_path, integrity_path)
        charts = original.build_charts(results)
    require(tuple(charts) == SUFFIXES, "a separately required public-practice graph is missing")
    for suffix, chart in charts.items():
        require("PRACTICE ONLY" in chart, f"the {suffix} graph omitted its public-practice scope")
        require("final speed NOT MEASURED" in chart, f"the {suffix} graph invented unseen final-test results")
    return results, charts


def expect_rejection(action, label: str) -> None:
    try:
        action()
    except (ValueError, TypeError, KeyError, OverflowError):
        return
    raise ValueError(f"synthetic public-practice version-9 isolation evidence was accepted: {label}")


def self_test() -> None:
    check_renderers()
    output = io.StringIO()
    with v9_practice_renderer(synthetic=True):
        with contextlib.redirect_stdout(output):
            original.self_test()
        summary, integrity, _raw, summary_digest, compressed_digest, raw_digest = original.synthetic_documents()
        controls = json.loads(output.getvalue())
        require(isinstance(controls, dict) and controls.get("result") == "PASS", "original synthetic public-practice SVG controls failed")
        require(controls.get("synthetic_only") is True, "synthetic controls accessed actual practice measurements")
        require(controls.get("holdout_accessed") is False, "synthetic controls accessed unseen cases")
        require(controls.get("timing_performed") is False, "synthetic controls performed timing")
        require(controls.get("corruption_checks", 0) >= 33, "the original synthetic corruption controls were weakened")
        require(controls.get("chart_count") == len(SUFFIXES), "a synthetic public-practice graph was omitted")
        extra: list[str] = []

        def reject_summary(key: str, value: object, label: str) -> None:
            corrupted = copy.deepcopy(summary)
            corrupted[key] = value
            expect_rejection(lambda: original.check_summary(corrupted), label)
            extra.append(label)

        def reject_integrity(key: str, value: object, label: str) -> None:
            corrupted = copy.deepcopy(integrity)
            corrupted[key] = value
            expect_rejection(
                lambda: original.check_integrity(
                    summary,
                    corrupted,
                    summary_digest=summary_digest,
                    compressed_digest=compressed_digest,
                    raw_digest=raw_digest,
                ),
                label,
            )
            extra.append(label)

        for entry in HISTORIES:
            version = entry["version"]
            reject_summary("exclusive_slot", entry["slot"], f"historical-practice-v{version}-slot-substitution")
            reject_integrity("schema", entry["schema"], f"historical-practice-v{version}-audit-substitution")
        reject_summary("exclusive_slot", "three-qualified-engines-public-practice-v9", "invented-public-practice-timing-slot")
        reject_summary("holdout_accessed", True, "unseen-final-workload-access")
        reject_summary("paired_raw_rows", original.RAW_ROWS - 1, "omitted-public-practice-timing-row")
        reject_summary("correctness_checks", original.CORRECTNESS_CHECKS - 1, "omitted-public-practice-correctness-gate")
        reject_summary("modules", list(reversed(original.MODULES)), "substituted-python-baseline-or-candidates")
        reject_summary("bootstrap_samples", original.BOOTSTRAPS - 1, "changed-public-bootstrap-confidence-protocol")
        reject_summary("trials", original.TRIALS - 1, "omitted-public-practice-paired-trial")
        reject_integrity("summary_sha256", "0" * 64, "substituted-public-practice-summary")
        reject_integrity("compressed_raw_sha256", "0" * 64, "substituted-public-practice-compressed-observations")
        reject_integrity("raw_sha256", "0" * 64, "substituted-public-practice-uncompressed-observations")
        reject_integrity("strict_regressions", HISTORIES[0]["regressions"] - 1, "concealed-public-practice-slowdown")
        reject_integrity("timing_performed", True, "independent-replay-performs-candidate-timing")

        synthetic = original.PracticeResults(
            summary,
            integrity,
            tuple(sorted(original.check_summary(summary), key=lambda row: (-row.ranking["geomean_speedup"], original.DISPLAY[row.module]))),
        )
        charts = original.build_charts(synthetic)
        require(tuple(charts) == SUFFIXES, "a separately required synthetic practice graph is missing")
        require("shared process" in charts["memory"], "synthetic graphs conceal shared-process memory limits")
        require("does not measure native" in charts["memory"], "synthetic graphs invent native-memory results")
        require(original.build_charts(synthetic) == charts, "public-practice version-9 SVG graphs are not deterministic")

    check_renderers()
    poisoned = controls["corruption_checks"] + len(extra)
    require(poisoned >= 59, "historical public-practice poisoning controls were weakened")
    print(json.dumps({
        "schema": f"{V9_PRACTICE_SCHEMA}-charts-self-test",
        "result": "PASS",
        "synthetic_only": True,
        "holdout_accessed": False,
        "timing_performed": False,
        "historical_practice_renderer_sha256": {f"v{entry['version']}": entry["renderer_sha256"] for entry in HISTORIES},
        "historical_practice_renderers_restored": True,
        "cases_per_candidate": original.CASES,
        "candidate_case_count": original.CASES * len(original.CANDIDATES),
        "trials_per_module_case": original.TRIALS,
        "raw_rows": original.RAW_ROWS,
        "correctness_checks": original.CORRECTNESS_CHECKS,
        "bootstrap_draws": original.BOOTSTRAPS,
        "original_poison_controls": controls["corruption_checks"],
        "additional_version_poison_controls": extra,
        "poisoned_control_count": poisoned,
        "chart_count": len(SUFFIXES),
        "charts_deterministic": True,
        "final_speed": "NOT MEASURED",
    }, sort_keys=True))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate exactly six source-bound C Stage 21 public-practice graphs.")
    parser.add_argument("--summary", type=Path, default=SUMMARY)
    parser.add_argument("--raw", type=Path, default=RAW)
    parser.add_argument("--integrity", type=Path, default=INTEGRITY)
    parser.add_argument("--prefix", type=Path, default=PREFIX)
    parser.add_argument("--self-test", action="store_true", help="run synthetic-only public-practice historical-isolation and deterministic SVG controls")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.self_test:
        self_test()
        return

    check_renderers()
    prefix = args.prefix.resolve()
    require(prefix == PREFIX.resolve(), "refusing to overwrite historical or unrelated public-practice graphs")
    require(prefix.parent == EVIDENCE.resolve(), "refusing to write outside public practice evidence")
    _results, charts = load_results(args.summary.resolve(), args.raw.resolve(), args.integrity.resolve())
    for suffix in SUFFIXES:
        destination = prefix.parent / f"{prefix.name}-{suffix}.svg"
        destination.write_text(charts[suffix], encoding="utf-8")
        print(f"wrote {destination.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
