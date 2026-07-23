#!/usr/bin/env python3
"""Render only a genuinely qualified, source-bound Zig Stage 13 practice run."""

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
PREFIX = EVIDENCE / "three-qualified-engines-public-practice-v7"
SUMMARY = EVIDENCE / "three-qualified-engines-public-practice-v7-summary.json"
RAW = EVIDENCE / "three-qualified-engines-public-practice-v7-raw.jsonl.gz"
INTEGRITY = EVIDENCE / "three-qualified-engines-public-practice-v7-integrity.json"
V7_AUDITOR = ROOT / "tools" / "rust_v7_multi_candidate_practice_v7_audit.py"
ROLE_CONFUSION_INCIDENT = EVIDENCE / "ZIG-STAGE-13-VERIFIER-INCIDENTS.md"

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
)

V7_SCHEMA = "rebar-v7-multi-candidate-practice-integrity-v7"

# Pin only the genuine completed full campaign and one-shot public practice.
V7_SLOT: str | None = "three-qualified-engines-zig-stage-13-interned-dispatch-v7"
V7_SUMMARY_SHA256: str | None = "89cf98bee40bb8e3ecc95861e07f302eff6c5f6288130854ea806578e8b76d79"
V7_COMPRESSED_RAW_SHA256: str | None = "574f62be23725529decaa7bbab67a575faae040470ccef9f528213c50866385c"
V7_RAW_SHA256: str | None = "59a04863d5cc2f0727222ac8d4388255411803793c741975d4c8abb3bfc3a696"
V7_REGRESSIONS: int | None = 259
V7_ZIG_EDGE_REPORT_SHA256: str | None = "a4c8b75811b5304ab115fb387f821127a20ed2615e7948ab4b96443dbe1ebe5c"
V7_AUDIT_SHA256: str | None = "5ce9df468d136b47c435456e59d372aed74d89f80fe1f877988dd7dba784b737"
V7_ZIG_CAMPAIGN_SHA256: str | None = "4ba7cb9c45a70b747cc0a6eb721f6bb51081157f527d1bf5e578e603715ae5dc"
V7_ZIG_BRIDGE_SOURCE_SHA256: str | None = "92d4039e1db2e01757edfd4edf56006c4735c3bc64352b6ce9c5d1f69decafcf"
V7_ZIG_NATIVE_BRIDGE_SHA256: str | None = "80d7dab57cbee317ee1727862e27cd7dcf4cb22e1a944f4b29f2e4e983f940ed"
UNCHANGED_ZIG_ENGINE_SOURCE_SHA256 = "4deca5a442cccd02bebfcecd4ceeb73de62a68837c5a3bdadee4dcaf84cf0ee3"
UNCHANGED_ZIG_NATIVE_ENGINE_SHA256 = "70bafca56a3f48477b2011f016a81b625e5f40a772af6a986d32b9098269f614"

RUST_CAMPAIGN_SHA256 = "9543fbbb39bbf42f5329a051b8441e69c756a495287a06c2f877c757b3ec5688"
C_CAMPAIGN_SHA256 = "c211d826032fed60c30024beb6de66c3e20b08fdcb936b53393d0a5fdba09721"
INITIAL_AUDIT_FAILURE_SHA256 = "ccaf3813b29badcf80c552dc0d850f83a2ca122cc3cc3057576dd519aed4f088"
ROLE_CONFUSION_INCIDENT_SHA256 = "84efcdbd0059ab430c84322695bf472f66fdc1cc05efd74e383b62114efcedff"
REFERENCE_MODULES = (original.BASELINE, original.RUST, original.C_ENGINE)
SUFFIXES = ("overall", "outcomes", "api", "regressions", "memory", "rankings")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def actual_digest(value: str | None, label: str) -> str:
    require(
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value),
        f"the genuine Zig Stage 13 {label} is NOT MEASURED or not qualified",
    )
    return value


def actual_slot() -> str:
    require(
        isinstance(V7_SLOT, str)
        and V7_SLOT.startswith("three-qualified-engines-")
        and V7_SLOT.endswith("-v7")
        and "/" not in V7_SLOT,
        "the genuine Zig Stage 13 exclusive slot is NOT MEASURED or invalid",
    )
    return V7_SLOT


def actual_regressions() -> int:
    require(
        isinstance(V7_REGRESSIONS, int)
        and not isinstance(V7_REGRESSIONS, bool)
        and 0 <= V7_REGRESSIONS <= 624 * 3,
        "the genuine Zig Stage 13 slowdown count is NOT MEASURED or invalid",
    )
    return V7_REGRESSIONS


def check_renderers() -> None:
    for history in HISTORIES:
        path = ROOT / "tools" / history["renderer"]
        require(original.sha256_file(path) == history["renderer_sha256"], f"the immutable v{history['version']} graph renderer changed")
    require(
        Path(original.__file__).resolve()
        == (ROOT / "tools" / "rust_v7_multi_candidate_practice_charts.py").resolve(),
        "the original pure SVG renderer was substituted",
    )
    initial = HISTORIES[0]
    require(original.SLOT == initial["slot"], "the original practice-slot controls changed")
    require(original.INTEGRITY_SCHEMA == initial["schema"], "the original practice-audit schema changed")
    require(original.EXPECTED_REGRESSIONS == initial["regressions"], "the original slowdown controls changed")
    require(original.CHART_SUFFIXES == SUFFIXES, "a separate original graph was omitted")
    require(original.CASES == 624, "the frozen public case denominator changed")
    require(original.TRIALS == 7, "the frozen paired-trial denominator changed")
    require(original.BOOTSTRAPS == 499, "the frozen confidence protocol changed")
    require(original.RAW_ROWS == 17_472, "the frozen paired-row denominator changed")
    require(original.CORRECTNESS_CHECKS == 52_416, "a frozen correctness gate was omitted")
    require(
        original.MODULES == (
            "re",
            "candidates.rust_candidate",
            "candidates.vm_candidate",
            "candidates.zig_candidate",
        ),
        "the standard Python baseline or independently implemented candidates changed",
    )
    require(len(original.API_COUNTS) == 12, "a frozen public operation was dropped")


@contextlib.contextmanager
def v7_renderer(*, synthetic: bool = False):
    """Use only version-scoped controls and always restore the v1 renderer."""

    check_renderers()
    saved = (original.SLOT, original.INTEGRITY_SCHEMA, original.EXPECTED_REGRESSIONS)
    original.SLOT = "three-qualified-engines-zig-stage13-synthetic-v7" if synthetic else actual_slot()
    original.INTEGRITY_SCHEMA = V7_SCHEMA
    original.EXPECTED_REGRESSIONS = HISTORIES[0]["regressions"] if synthetic else actual_regressions()
    try:
        yield
    finally:
        original.SLOT, original.INTEGRITY_SCHEMA, original.EXPECTED_REGRESSIONS = saved
        check_renderers()


def check_history() -> tuple[tuple[dict, dict], ...]:
    records: list[tuple[dict, dict]] = []
    for history in HISTORIES:
        version = history["version"]
        prefix = f"three-qualified-engines-public-practice-v{version}"
        summary_path = EVIDENCE / f"{prefix}-summary.json"
        integrity_path = EVIDENCE / f"{prefix}-integrity.json"
        require(original.sha256_file(summary_path) == history["summary_sha256"], f"the preserved v{version} public summary changed")
        require(original.sha256_file(integrity_path) == history["integrity_sha256"], f"the preserved v{version} independent replay changed")
        summary = original.read_json(summary_path)
        integrity = original.read_json(integrity_path)
        require(summary.get("exclusive_slot") == history["slot"], f"historical v{version} practice was relabeled")
        require(integrity.get("schema") == history["schema"], f"the historical v{version} replay schema changed")
        require(integrity.get("result") == "PASS", f"the original v{version} independent practice audit failed")
        require(integrity.get("summary_sha256") == history["summary_sha256"], f"historical v{version} practice lost its source binding")
        require(integrity.get("strict_regressions") == history["regressions"], f"historical v{version} slowdowns were altered")
        for previous in HISTORIES[: version - 1]:
            key = f"historical_v{previous['version']}_integrity_sha256"
            require(integrity.get(key) == previous["integrity_sha256"], f"historical v{previous['version']}-to-v{version} continuity changed")
        records.append((summary, integrity))
    return tuple(records)


def check_v7_metadata(summary: dict, integrity: dict) -> None:
    expected = {
        "schema": V7_SCHEMA,
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
        "summary_sha256": actual_digest(V7_SUMMARY_SHA256, "one-shot practice summary"),
        "compressed_raw_sha256": actual_digest(V7_COMPRESSED_RAW_SHA256, "compressed paired observations"),
        "raw_sha256": actual_digest(V7_RAW_SHA256, "uncompressed paired observations"),
        "from_scratch_audit_sha256": actual_digest(V7_AUDIT_SHA256, "passing all-five-mapped native-source audit"),
        "full_correctness_campaign_sha256": actual_digest(V7_ZIG_CAMPAIGN_SHA256, "passing complete 22-stage Zig campaign"),
        "rust_full_correctness_campaign_sha256": RUST_CAMPAIGN_SHA256,
        "c_full_correctness_campaign_sha256": C_CAMPAIGN_SHA256,
        "initial_audit_failure_sha256": INITIAL_AUDIT_FAILURE_SHA256,
        "role_confusion_incident_sha256": ROLE_CONFUSION_INCIDENT_SHA256,
        "role_confusion_incident_path": str(ROLE_CONFUSION_INCIDENT.resolve()),
        "unchanged_reference_candidates": list(REFERENCE_MODULES),
        "rust_optimization_verified": True,
        "capacity16_optimization_verified": True,
        "zig_optimization_verified": True,
        "mandatory_prefix_optimization_verified": True,
        "unchanged_rust_bridge_verified": True,
        "c_optimization_verified": True,
        "zig_interned_attributes_optimization_verified": True,
    }
    for history in HISTORIES:
        expected[f"historical_v{history['version']}_integrity_sha256"] = history["integrity_sha256"]
    for key, value in expected.items():
        require(integrity.get(key) == value, f"the independent Stage 13 results audit does not prove {key}")
    require(summary.get("exclusive_slot") == actual_slot(), "the actual Stage 13 exclusive timing slot changed")
    require(summary.get("cohort") == "calibration", "a non-public practice case entered the report")
    require(summary.get("holdout_accessed") is False, "the unseen final test entered practice")
    require(summary.get("failed") == 0, "a real Stage 13 timing correctness gate failed")
    require(summary.get("compressed_raw_sha256") == actual_digest(V7_COMPRESSED_RAW_SHA256, "compressed observations"), "the actual compressed observations changed")
    require(summary.get("raw_sha256") == actual_digest(V7_RAW_SHA256, "uncompressed observations"), "the actual uncompressed observations changed")
    require(original.sha256_file(V7_AUDITOR) == integrity.get("source_sha256"), "the independent Stage 13 replay verifier was substituted")
    require(
        original.sha256_file(ROLE_CONFUSION_INCIDENT) == ROLE_CONFUSION_INCIDENT_SHA256,
        "the preserved, openly disclosed Stage 13 verifier incident was altered",
    )


def check_unchanged_references(summary: dict, integrity: dict, v6_summary: dict, v6_integrity: dict) -> None:
    old_artifacts = v6_summary.get("candidate_binary_sha256_before")
    new_artifacts = summary.get("candidate_binary_sha256_before")
    require(isinstance(old_artifacts, dict) and isinstance(new_artifacts, dict), "actual or historical candidate fingerprints are missing")
    require(summary.get("candidate_binary_sha256_after") == new_artifacts, "a candidate changed during the actual four-way run")
    for module in REFERENCE_MODULES:
        prefix = f"{module}:"
        old = {role: digest for role, digest in old_artifacts.items() if role.startswith(prefix)}
        new = {role: digest for role, digest in new_artifacts.items() if role.startswith(prefix)}
        require(bool(old) and new == old, f"an unchanged Python, Rust, or C reference changed: {module}")

    old_sources = v6_integrity.get("qualified_source_fingerprints")
    new_sources = integrity.get("qualified_source_fingerprints")
    require(isinstance(old_sources, dict) and isinstance(new_sources, dict), "passing production-source provenance is missing")
    changed_source = "candidates/zig/py_bridge.c"
    actual_source = actual_digest(V7_ZIG_BRIDGE_SOURCE_SHA256, "qualified Stage 13 Zig bridge source")
    require(new_sources.get(changed_source) == actual_source, "the fresh Stage 13 Zig bridge source was substituted")
    require(old_sources.get(changed_source) != actual_source, "practice reused the historical Zig bridge source")
    require(
        old_sources.get("candidates/zig/mini_regex.zig")
        == new_sources.get("candidates/zig/mini_regex.zig")
        == UNCHANGED_ZIG_ENGINE_SOURCE_SHA256,
        "the unchanged, from-scratch Stage 12 Zig engine source was substituted",
    )
    for path, digest in old_sources.items():
        if path != changed_source:
            require(new_sources.get(path) == digest, f"an unrelated standard-Python, Rust, C, or Zig-engine source changed: {path}")

    changed_role = f"{original.ZIG}:native-bridge"
    actual_native = actual_digest(V7_ZIG_NATIVE_BRIDGE_SHA256, "qualified Stage 13 Zig native bridge")
    require(new_artifacts.get(changed_role) == actual_native, "the real Stage 13 Zig native bridge was substituted")
    require(old_artifacts.get(changed_role) != actual_native, "practice reused the historical mapped Zig bridge")
    require(
        old_artifacts.get(f"{original.ZIG}:native-engine")
        == new_artifacts.get(f"{original.ZIG}:native-engine")
        == UNCHANGED_ZIG_NATIVE_ENGINE_SHA256,
        "the unchanged, from-scratch mapped Zig engine was substituted",
    )
    for role, digest in old_artifacts.items():
        if role.startswith(f"{original.ZIG}:") and role != changed_role:
            require(new_artifacts.get(role) == digest, f"an unchanged Zig Python surface or owned engine changed: {role}")


def check_current_edge(summary: dict) -> None:
    expected = actual_digest(V7_ZIG_EDGE_REPORT_SHA256, "passing frozen Stage 13 edge-correctness proof")
    proofs = summary.get("verified_edge_oracles")
    require(isinstance(proofs, list), "current independent candidate correctness proofs are missing")
    matches = [item for item in proofs if isinstance(item, dict) and item.get("module") == original.ZIG]
    require(len(matches) == 1, "the passing Stage 13 Zig edge proof is missing or duplicated")
    require(matches[0].get("report_sha256") == expected, "the measured Zig engine differs from its actual passing edge proof")


def load_results(summary_path: Path, raw_path: Path, integrity_path: Path):
    require(summary_path.resolve() == SUMMARY.resolve(), "refusing a substituted Stage 13 practice summary")
    require(raw_path.resolve() == RAW.resolve(), "refusing substituted Stage 13 paired measurements")
    require(integrity_path.resolve() == INTEGRITY.resolve(), "refusing substituted Stage 13 replay evidence")
    require(original.sha256_file(summary_path) == actual_digest(V7_SUMMARY_SHA256, "complete v7 summary"), "the genuine one-shot Stage 13 summary changed")
    require(original.sha256_file(raw_path) == actual_digest(V7_COMPRESSED_RAW_SHA256, "complete v7 observations"), "the genuine one-shot Stage 13 observations changed")
    histories = check_history()
    v6_summary, v6_integrity = histories[-1]
    summary = original.read_json(summary_path)
    integrity = original.read_json(integrity_path)
    check_v7_metadata(summary, integrity)
    check_unchanged_references(summary, integrity, v6_summary, v6_integrity)
    check_current_edge(summary)
    with v7_renderer():
        results = original.load_results(summary_path, raw_path, integrity_path)
        charts = original.build_charts(results)
    require(tuple(charts) == SUFFIXES, "a separately required Stage 13 practice graph is missing")
    for name, graph in charts.items():
        require("PRACTICE ONLY" in graph, f"the {name} graph omitted its public-practice limitation")
        require("final speed NOT MEASURED" in graph, f"the {name} graph invented final-test performance")
    return results, charts


def expect_rejection(action, label: str) -> None:
    try:
        action()
    except (ValueError, TypeError, KeyError, OverflowError):
        return
    raise ValueError(f"synthetic Zig Stage 13 version-isolation evidence was accepted: {label}")


def self_test() -> None:
    check_renderers()
    captured = io.StringIO()
    with v7_renderer(synthetic=True):
        with contextlib.redirect_stdout(captured):
            original.self_test()
        summary, integrity, _rows, summary_digest, compressed_digest, raw_digest = original.synthetic_documents()
        base = json.loads(captured.getvalue())
        require(isinstance(base, dict) and base.get("result") == "PASS", "the original standalone synthetic chart controls failed")
        require(base.get("synthetic_only") is True, "a synthetic chart control used real measurement data")
        require(base.get("holdout_accessed") is False, "a synthetic chart control accessed unseen final cases")
        require(base.get("timing_performed") is False, "a synthetic chart control timed a production engine")
        require(base.get("corruption_checks", 0) >= 33, "original poisoned-evidence controls were removed")
        require(base.get("chart_count") == len(SUFFIXES), "a required synthetic SVG was removed")
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

        for history in HISTORIES:
            version = history["version"]
            reject_summary("exclusive_slot", history["slot"], f"historical-v{version}-slot-substitution")
            reject_integrity("schema", history["schema"], f"historical-v{version}-replay-substitution")
        reject_summary("exclusive_slot", "three-qualified-engines-public-practice-v7", "invented-stage13-timing-slot")
        reject_summary("holdout_accessed", True, "unseen-final-workload-access")
        reject_summary("paired_raw_rows", original.RAW_ROWS - 1, "missing-paired-practice-observation")
        reject_summary("correctness_checks", original.CORRECTNESS_CHECKS - 1, "missing-practice-correctness-gate")
        reject_summary("modules", list(reversed(original.MODULES)), "substituted-standard-python-or-candidates")
        reject_summary("bootstrap_samples", original.BOOTSTRAPS - 1, "changed-confidence-draw-count")
        reject_summary("trials", original.TRIALS - 1, "missing-frozen-paired-trial")
        reject_integrity("summary_sha256", "0" * 64, "substituted-stage13-summary")
        reject_integrity("compressed_raw_sha256", "0" * 64, "substituted-compressed-stage13-observations")
        reject_integrity("raw_sha256", "0" * 64, "substituted-uncompressed-stage13-observations")
        reject_integrity("strict_regressions", HISTORIES[0]["regressions"] - 1, "concealed-substantial-slowdown")
        reject_integrity("timing_performed", True, "independent-replay-performs-timing")

        data = original.PracticeResults(
            summary,
            integrity,
            tuple(sorted(original.check_summary(summary), key=lambda row: (-row.ranking["geomean_speedup"], original.DISPLAY[row.module]))),
        )
        charts = original.build_charts(data)
        require(tuple(charts) == SUFFIXES, "a separate synthetic Stage 13 graph was omitted")
        require("shared process" in charts["memory"], "a graph concealed shared-process memory limitations")
        require("does not measure native" in charts["memory"], "a graph invented native memory measurements")
        require(original.build_charts(data) == charts, "Stage 13 public-practice graphs are not deterministic")

    check_renderers()
    poisoned = base["corruption_checks"] + len(extras)
    require(poisoned >= 55, "historical and synthetic poisoned-evidence controls were weakened")
    print(json.dumps({
        "schema": f"{V7_SCHEMA}-charts-self-test",
        "result": "PASS",
        "synthetic_only": True,
        "holdout_accessed": False,
        "timing_performed": False,
        "historical_renderer_sha256": {f"v{entry['version']}": entry["renderer_sha256"] for entry in HISTORIES},
        "historical_renderers_restored": True,
        "cases_per_candidate": original.CASES,
        "candidate_case_count": original.CASES * len(original.CANDIDATES),
        "trials_per_module_case": original.TRIALS,
        "raw_rows": original.RAW_ROWS,
        "correctness_checks": original.CORRECTNESS_CHECKS,
        "bootstrap_draws": original.BOOTSTRAPS,
        "original_poison_controls": base["corruption_checks"],
        "additional_version_poison_controls": extras,
        "poisoned_control_count": poisoned,
        "chart_count": len(SUFFIXES),
        "charts_deterministic": True,
        "final_speed": "NOT MEASURED",
    }, sort_keys=True))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate six independently verified Zig Stage 13 public-practice graphs.")
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
    require(prefix == PREFIX.resolve(), "refusing to replace a historical or unrelated graph")
    require(prefix.parent == EVIDENCE.resolve(), "refusing to write outside frozen public practice evidence")
    _data, charts = load_results(args.summary.resolve(), args.raw.resolve(), args.integrity.resolve())
    for suffix in SUFFIXES:
        destination = prefix.parent / f"{prefix.name}-{suffix}.svg"
        destination.write_text(charts[suffix], encoding="utf-8")
        print(f"wrote {destination.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
