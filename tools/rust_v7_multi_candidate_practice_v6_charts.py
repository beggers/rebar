#!/usr/bin/env python3
"""Render only the verified, independently implemented C Stage 20 run."""

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
PREFIX = EVIDENCE / "three-qualified-engines-public-practice-v6"
SUMMARY = EVIDENCE / "three-qualified-engines-public-practice-v6-summary.json"
RAW = EVIDENCE / "three-qualified-engines-public-practice-v6-raw.jsonl.gz"
INTEGRITY = EVIDENCE / "three-qualified-engines-public-practice-v6-integrity.json"
V6_AUDITOR = ROOT / "tools" / "rust_v7_multi_candidate_practice_v6_audit.py"

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
)

V6_SLOT = "three-qualified-engines-c-stage-20-native-scanner-cmethod-v6"
V6_SCHEMA = "rebar-v7-multi-candidate-practice-integrity-v6"
V6_SUMMARY_SHA256 = "22689cf92175274f935df81f51b07b4f2a0a90bafad3ae1bd2b0e9f905579fce"
V6_COMPRESSED_RAW_SHA256 = "9e38b7a20435d1479d88e0456ffb2849337983c7957ddad238c021d69c4913ee"
V6_RAW_SHA256 = "8098869ed442741e132567516341c73d78bef59db0e901280a940af40e25521e"
V6_REGRESSIONS = 407
V6_C_EDGE_REPORT_SHA256 = "2f80bc9b0a12959455b9422d89f047903b8073d5d75e5e1a814c0922049d336f"
V6_AUDIT_SHA256 = "f875068b829482d0c5dd28290a5706dd0a5c0ed91018b857cee82b6defe40f0a"
V6_C_CAMPAIGN_SHA256 = "c211d826032fed60c30024beb6de66c3e20b08fdcb936b53393d0a5fdba09721"
V5_RUST_CAMPAIGN_SHA256 = "9543fbbb39bbf42f5329a051b8441e69c756a495287a06c2f877c757b3ec5688"
V4_ZIG_CAMPAIGN_SHA256 = "f89fe9081421d28a291feab1b664c21a7c372762a548569856c6572e4a23eba6"
INITIAL_AUDIT_FAILURE_SHA256 = "ccaf3813b29badcf80c552dc0d850f83a2ca122cc3cc3057576dd519aed4f088"
V6_C_SOURCE_SHA256 = "696925d94c63fed442d547e9a0fbcce9dda271eae633130d01cdb4e68ea4af2f"
V6_C_NATIVE_ENGINE_SHA256 = "0e4d194fc14a2e307dd765ec5632acbe7b4192a0b2a74833a1126fbd0e5b5b91"
REFERENCE_MODULES = (original.BASELINE, original.RUST, original.ZIG)
SUFFIXES = ("overall", "outcomes", "api", "regressions", "memory", "rankings")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def check_renderers() -> None:
    for history in HISTORIES:
        source = ROOT / "tools" / history["renderer"]
        require(original.sha256_file(source) == history["renderer_sha256"], f"the immutable v{history['version']} renderer changed")
    require(
        Path(original.__file__).resolve()
        == (ROOT / "tools" / "rust_v7_multi_candidate_practice_charts.py").resolve(),
        "the frozen pure original SVG renderer was substituted",
    )
    first = HISTORIES[0]
    require(original.SLOT == first["slot"], "frozen original public-practice slot controls changed")
    require(original.INTEGRITY_SCHEMA == first["schema"], "frozen original integrity-schema controls changed")
    require(original.EXPECTED_REGRESSIONS == first["regressions"], "frozen original slowdown controls changed")
    require(original.CHART_SUFFIXES == SUFFIXES, "a separately required graph renderer was dropped")
    require(original.CASES == 624, "the frozen case denominator changed")
    require(original.TRIALS == 7, "the frozen paired-trial denominator changed")
    require(original.BOOTSTRAPS == 499, "the frozen confidence protocol changed")
    require(original.RAW_ROWS == 17_472, "the frozen raw-row denominator changed")
    require(original.CORRECTNESS_CHECKS == 52_416, "a frozen correctness gate was omitted")
    require(
        original.MODULES == (
            "re",
            "candidates.rust_candidate",
            "candidates.vm_candidate",
            "candidates.zig_candidate",
        ),
        "the baseline or an independently implemented candidate was replaced",
    )
    require(len(original.API_COUNTS) == 12, "a frozen public operation was omitted")


@contextlib.contextmanager
def v6_renderer(*, synthetic: bool = False):
    """Restore the byte-pinned v1 renderer even when a v6 check fails."""

    check_renderers()
    saved = (original.SLOT, original.INTEGRITY_SCHEMA, original.EXPECTED_REGRESSIONS)
    original.SLOT = V6_SLOT
    original.INTEGRITY_SCHEMA = V6_SCHEMA
    original.EXPECTED_REGRESSIONS = HISTORIES[0]["regressions"] if synthetic else V6_REGRESSIONS
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
        require(original.sha256_file(summary_path) == history["summary_sha256"], f"the preserved v{version} summary changed")
        require(original.sha256_file(integrity_path) == history["integrity_sha256"], f"the preserved v{version} results audit changed")
        summary = original.read_json(summary_path)
        integrity = original.read_json(integrity_path)
        require(summary.get("exclusive_slot") == history["slot"], f"historical practice v{version} was relabeled")
        require(integrity.get("schema") == history["schema"], f"the historical v{version} integrity schema changed")
        require(integrity.get("result") == "PASS", f"the historical v{version} results audit failed")
        require(integrity.get("summary_sha256") == history["summary_sha256"], f"historical v{version} results lost their source fingerprint")
        require(integrity.get("strict_regressions") == history["regressions"], f"historical v{version} substantial slowdowns were dropped")
        for previous in HISTORIES[: version - 1]:
            key = f"historical_v{previous['version']}_integrity_sha256"
            require(integrity.get(key) == previous["integrity_sha256"], f"the immutable v{previous['version']}-to-v{version} continuity broke")
        records.append((summary, integrity))
    return tuple(records)


def check_v6_metadata(summary: dict, integrity: dict) -> None:
    expected = {
        "schema": V6_SCHEMA,
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
        "strict_regressions": V6_REGRESSIONS,
        "summary_sha256": V6_SUMMARY_SHA256,
        "compressed_raw_sha256": V6_COMPRESSED_RAW_SHA256,
        "raw_sha256": V6_RAW_SHA256,
        "from_scratch_audit_sha256": V6_AUDIT_SHA256,
        "full_correctness_campaign_sha256": V6_C_CAMPAIGN_SHA256,
        "rust_full_correctness_campaign_sha256": V5_RUST_CAMPAIGN_SHA256,
        "zig_full_correctness_campaign_sha256": V4_ZIG_CAMPAIGN_SHA256,
        "initial_audit_failure_sha256": INITIAL_AUDIT_FAILURE_SHA256,
        "unchanged_reference_candidates": list(REFERENCE_MODULES),
        "rust_optimization_verified": True,
        "capacity16_optimization_verified": True,
        "zig_optimization_verified": True,
        "mandatory_prefix_optimization_verified": True,
        "unchanged_rust_bridge_verified": True,
        "c_optimization_verified": True,
    }
    for history in HISTORIES:
        expected[f"historical_v{history['version']}_integrity_sha256"] = history["integrity_sha256"]
    for key, expected_value in expected.items():
        require(integrity.get(key) == expected_value, f"the independent C Stage 20 audit does not verify {key}")
    require(summary.get("exclusive_slot") == V6_SLOT, "the single actual C Stage 20 practice slot changed")
    require(summary.get("cohort") == "calibration", "a non-public case entered the diagnostic")
    require(summary.get("holdout_accessed") is False, "unseen final cases entered public practice")
    require(summary.get("failed") == 0, "a C Stage 20 timing correctness gate failed")
    require(summary.get("compressed_raw_sha256") == V6_COMPRESSED_RAW_SHA256, "the actual compressed v6 observations changed")
    require(summary.get("raw_sha256") == V6_RAW_SHA256, "the actual uncompressed v6 observations changed")
    require(original.sha256_file(V6_AUDITOR) == integrity.get("source_sha256"), "the independent v6 source-bound results auditor was substituted")


def check_unchanged_references(summary: dict, integrity: dict, v5_summary: dict, v5_integrity: dict) -> None:
    previous = v5_summary.get("candidate_binary_sha256_before")
    measured = summary.get("candidate_binary_sha256_before")
    require(isinstance(previous, dict) and isinstance(measured, dict), "historical or measured candidate fingerprints are missing")
    require(summary.get("candidate_binary_sha256_after") == measured, "a production engine changed during paired practice")
    for module in REFERENCE_MODULES:
        prefix = f"{module}:"
        old = {key: digest for key, digest in previous.items() if key.startswith(prefix)}
        new = {key: digest for key, digest in measured.items() if key.startswith(prefix)}
        require(bool(old) and new == old, f"an unchanged standard Python, Rust, or Zig reference changed: {module}")

    old_sources = v5_integrity.get("qualified_source_fingerprints")
    current_sources = integrity.get("qualified_source_fingerprints")
    require(isinstance(old_sources, dict) and isinstance(current_sources, dict), "current or historical qualified source fingerprints are missing")
    changed_source = "candidates/_vm_native.c"
    require(current_sources.get(changed_source) == V6_C_SOURCE_SHA256, "the passing C Stage 20 native source was substituted")
    require(old_sources.get(changed_source) != V6_C_SOURCE_SHA256, "practice did not use the optimized native C source")
    for path, digest in old_sources.items():
        if path != changed_source:
            require(current_sources.get(path) == digest, f"an unrelated Python, Rust, Zig, or C surface changed: {path}")

    changed_engine = f"{original.C_ENGINE}:native-engine"
    require(measured.get(changed_engine) == V6_C_NATIVE_ENGINE_SHA256, "the current verified C native engine was substituted")
    require(previous.get(changed_engine) != V6_C_NATIVE_ENGINE_SHA256, "practice reused the historical C native engine")
    for role, digest in previous.items():
        if role.startswith(f"{original.C_ENGINE}:") and role != changed_engine:
            require(measured.get(role) == digest, f"the unchanged public C surface changed: {role}")


def check_current_edge(summary: dict) -> None:
    proofs = summary.get("verified_edge_oracles")
    require(isinstance(proofs, list), "the complete fresh correctness proofs are missing")
    matching = [item for item in proofs if isinstance(item, dict) and item.get("module") == original.C_ENGINE]
    require(len(matching) == 1, "the currently passing C Stage 20 correctness proof is missing or duplicated")
    require(matching[0].get("report_sha256") == V6_C_EDGE_REPORT_SHA256, "the measured C engine does not match its passing frozen correctness proof")


def load_results(summary_path: Path, raw_path: Path, integrity_path: Path):
    require(summary_path.resolve() == SUMMARY.resolve(), "refusing a substituted C Stage 20 summary")
    require(raw_path.resolve() == RAW.resolve(), "refusing substituted C Stage 20 paired observations")
    require(integrity_path.resolve() == INTEGRITY.resolve(), "refusing substituted C Stage 20 independent evidence")
    require(original.sha256_file(summary_path) == V6_SUMMARY_SHA256, "the complete one-shot C Stage 20 summary changed")
    require(original.sha256_file(raw_path) == V6_COMPRESSED_RAW_SHA256, "the complete one-shot C Stage 20 raw measurements changed")
    history = check_history()
    v5_summary, v5_integrity = history[-1]
    summary = original.read_json(summary_path)
    integrity = original.read_json(integrity_path)
    check_v6_metadata(summary, integrity)
    check_unchanged_references(summary, integrity, v5_summary, v5_integrity)
    check_current_edge(summary)
    with v6_renderer():
        result = original.load_results(summary_path, raw_path, integrity_path)
        charts = original.build_charts(result)
    require(tuple(charts) == SUFFIXES, "a separately required C Stage 20 graph was removed")
    for suffix, graph in charts.items():
        require("PRACTICE ONLY" in graph, f"the {suffix} graph omitted its practice-only disclosure")
        require("final speed NOT MEASURED" in graph, f"the {suffix} graph invented unseen final performance")
    return result, charts


def expect_rejection(action, label: str) -> None:
    try:
        action()
    except (ValueError, TypeError, KeyError, OverflowError):
        return
    raise ValueError(f"synthetic C Stage 20 version-isolation evidence was accepted: {label}")


def self_test() -> None:
    check_renderers()
    captured = io.StringIO()
    with v6_renderer(synthetic=True):
        with contextlib.redirect_stdout(captured):
            original.self_test()
        summary, integrity, _raw, summary_digest, compressed_digest, raw_digest = original.synthetic_documents()
        base = json.loads(captured.getvalue())
        require(isinstance(base, dict) and base.get("result") == "PASS", "the original pure SVG corruption controls failed")
        require(base.get("synthetic_only") is True, "a synthetic control inspected an actual practice result")
        require(base.get("holdout_accessed") is False, "a synthetic control accessed a held-out workload")
        require(base.get("timing_performed") is False, "a synthetic control timed a production engine")
        require(base.get("corruption_checks", 0) >= 33, "the original poisoned-evidence controls were weakened")
        require(base.get("chart_count") == len(SUFFIXES), "a synthetic graph was omitted")
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
            reject_integrity("schema", history["schema"], f"historical-v{version}-integrity-substitution")
        reject_summary("exclusive_slot", "three-qualified-engines-public-practice-v6", "invented-c-stage20-measurement-slot")
        reject_summary("holdout_accessed", True, "unseen-final-workload-access")
        reject_summary("paired_raw_rows", original.RAW_ROWS - 1, "omitted-paired-practice-observation")
        reject_summary("correctness_checks", original.CORRECTNESS_CHECKS - 1, "omitted-practice-correctness-gate")
        reject_summary("modules", list(reversed(original.MODULES)), "substituted-baseline-or-paired-candidates")
        reject_summary("bootstrap_samples", original.BOOTSTRAPS - 1, "changed-confidence-protocol")
        reject_summary("trials", original.TRIALS - 1, "missing-frozen-paired-trial")
        reject_integrity("summary_sha256", "0" * 64, "substituted-c-stage20-summary")
        reject_integrity("compressed_raw_sha256", "0" * 64, "substituted-compressed-practice-observations")
        reject_integrity("raw_sha256", "0" * 64, "substituted-uncompressed-practice-observations")
        reject_integrity("strict_regressions", HISTORIES[0]["regressions"] - 1, "concealed-synthetic-substantial-slowdown")
        reject_integrity("timing_performed", True, "independent-replay-performs-timing")

        data = original.PracticeResults(
            summary,
            integrity,
            tuple(sorted(original.check_summary(summary), key=lambda row: (-row.ranking["geomean_speedup"], original.DISPLAY[row.module]))),
        )
        charts = original.build_charts(data)
        require(tuple(charts) == SUFFIXES, "a separately required synthetic graph was omitted")
        require("shared process" in charts["memory"], "the graph concealed its shared-process memory scope")
        require("does not measure native" in charts["memory"], "the graph invented native-memory measurements")
        require(original.build_charts(data) == charts, "source-bound practice graphs are not deterministic")

    check_renderers()
    poisoned = base["corruption_checks"] + len(extras)
    require(poisoned >= 53, "fewer than 53 deterministic poison controls were preserved")
    print(json.dumps({
        "schema": f"{V6_SCHEMA}-charts-self-test",
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
    parser = argparse.ArgumentParser(description="Generate exactly six independently verified C Stage 20 public-practice graphs.")
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
    require(prefix == PREFIX.resolve(), "refusing to overwrite a historical or unrelated practice graph")
    require(prefix.parent == EVIDENCE.resolve(), "refusing to write outside frozen public practice evidence")
    _result, charts = load_results(args.summary.resolve(), args.raw.resolve(), args.integrity.resolve())
    for suffix in SUFFIXES:
        path = prefix.parent / f"{prefix.name}-{suffix}.svg"
        path.write_text(charts[suffix], encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
