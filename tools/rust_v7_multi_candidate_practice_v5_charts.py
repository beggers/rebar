#!/usr/bin/env python3
"""Render only the source-bound, owned Rust common-prefix practice run."""

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
PREFIX = EVIDENCE / "three-qualified-engines-public-practice-v5"
SUMMARY = EVIDENCE / "three-qualified-engines-public-practice-v5-summary.json"
RAW = EVIDENCE / "three-qualified-engines-public-practice-v5-raw.jsonl.gz"
INTEGRITY = EVIDENCE / "three-qualified-engines-public-practice-v5-integrity.json"
V5_AUDITOR = ROOT / "tools" / "rust_v7_multi_candidate_practice_v5_audit.py"

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
)

V5_SLOT = "three-qualified-engines-rust-owned-common-prefix-v5"
V5_SCHEMA = "rebar-v7-multi-candidate-practice-integrity-v5"

# Pin only the actual, complete, one-shot owned-engine public-practice result.
V5_SUMMARY_SHA256: str | None = "98c611410895f831d0b97a1677723186cc1e06d438d3437bfec9519743b1ad69"
V5_COMPRESSED_RAW_SHA256: str | None = "bfb82c4ac326163db2d3ae463817e2a56821e0c5f1b72ee693c26690c23e4a7d"
V5_RAW_SHA256: str | None = "8a1b998c140046ac3b795cf912c5ccb958ac182d44b1a49b7f055aed25f80eb2"
V5_REGRESSIONS: int | None = 407
V5_RUST_ENGINE_SOURCE_SHA256: str | None = "d6e0cd31b06cd4edb1af7f8fb7409c23027289818934b35a03d5b3cc17444784"
V5_RUST_NATIVE_ENGINE_SHA256: str | None = "37ab3d8598bdbbe9097810a35b54f3558fd0473db903d0a0c6b6527068dbf7cb"
V5_RUST_EDGE_REPORT_SHA256: str | None = "13e3aaa028a8ebd5e7b345db333afbe082e5b6ac7bd6d72709f9071af3430628"

V5_AUDIT_SHA256 = "4856f38bac3f54a1c0758e4c32c8d738a55128f932ecbc451025ea170108709d"
V5_RUST_CAMPAIGN_SHA256 = "9543fbbb39bbf42f5329a051b8441e69c756a495287a06c2f877c757b3ec5688"
V4_ZIG_CAMPAIGN_SHA256 = "f89fe9081421d28a291feab1b664c21a7c372762a548569856c6572e4a23eba6"
INITIAL_AUDIT_FAILURE_SHA256 = "ccaf3813b29badcf80c552dc0d850f83a2ca122cc3cc3057576dd519aed4f088"
UNCHANGED_RUST_BRIDGE_SOURCE_SHA256 = "83afb5a709a6d0ea1701dfd64db30644edbf2cb0276c2db731a8119cfd52d8ed"
UNCHANGED_RUST_NATIVE_BRIDGE_SHA256 = "1f072e81ba9339a8b2e52a7e93b7bcde791c4d518620b6bd760af67c7c89af34"
REFERENCE_MODULES = (original.BASELINE, original.C_ENGINE, original.ZIG)
SUFFIXES = ("overall", "outcomes", "api", "regressions", "memory", "rankings")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def measured_digest(value: str | None, label: str) -> str:
    require(
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value),
        f"the actual {label} is NOT MEASURED or invalid",
    )
    return value


def measured_regressions() -> int:
    require(
        isinstance(V5_REGRESSIONS, int)
        and not isinstance(V5_REGRESSIONS, bool)
        and 0 <= V5_REGRESSIONS <= 624 * 3,
        "the actual owned-engine practice slowdown count is NOT MEASURED or invalid",
    )
    return V5_REGRESSIONS


def check_renderers() -> None:
    for history in HISTORIES:
        path = ROOT / "tools" / history["renderer"]
        require(original.sha256_file(path) == history["renderer_sha256"], f"an immutable historical graph renderer changed: v{history['version']}")
    require(
        Path(original.__file__).resolve()
        == (ROOT / "tools" / "rust_v7_multi_candidate_practice_charts.py").resolve(),
        "the original pure graph renderer was substituted",
    )
    first = HISTORIES[0]
    require(original.SLOT == first["slot"], "original public-practice slot controls changed")
    require(original.INTEGRITY_SCHEMA == first["schema"], "original integrity-schema controls changed")
    require(original.EXPECTED_REGRESSIONS == first["regressions"], "original substantial-slowdown controls changed")
    require(original.CHART_SUFFIXES == SUFFIXES, "a separately required graph was omitted")
    require(original.CASES == 624, "the frozen per-candidate case count changed")
    require(original.TRIALS == 7, "the frozen paired-trial count changed")
    require(original.BOOTSTRAPS == 499, "the frozen confidence protocol changed")
    require(original.RAW_ROWS == 17_472, "the frozen raw timing denominator changed")
    require(original.CORRECTNESS_CHECKS == 52_416, "a frozen correctness gate was dropped")
    require(
        original.MODULES == (
            "re",
            "candidates.rust_candidate",
            "candidates.vm_candidate",
            "candidates.zig_candidate",
        ),
        "the unchanged Python baseline or a production candidate was replaced",
    )
    require(len(original.API_COUNTS) == 12, "a public operation group was omitted")


@contextlib.contextmanager
def v5_renderer(*, synthetic: bool = False):
    """Scope exact v5 controls locally and always restore historical state."""

    check_renderers()
    previous = (original.SLOT, original.INTEGRITY_SCHEMA, original.EXPECTED_REGRESSIONS)
    original.SLOT = V5_SLOT
    original.INTEGRITY_SCHEMA = V5_SCHEMA
    original.EXPECTED_REGRESSIONS = HISTORIES[0]["regressions"] if synthetic else measured_regressions()
    try:
        yield
    finally:
        original.SLOT, original.INTEGRITY_SCHEMA, original.EXPECTED_REGRESSIONS = previous
        check_renderers()


def check_history() -> tuple[tuple[dict, dict], ...]:
    results: list[tuple[dict, dict]] = []
    for history in HISTORIES:
        version = history["version"]
        name = f"three-qualified-engines-public-practice-v{version}"
        summary_path = EVIDENCE / f"{name}-summary.json"
        integrity_path = EVIDENCE / f"{name}-integrity.json"
        require(original.sha256_file(summary_path) == history["summary_sha256"], f"the complete v{version} practice summary changed")
        require(original.sha256_file(integrity_path) == history["integrity_sha256"], f"the independently verified v{version} practice evidence changed")
        summary = original.read_json(summary_path)
        integrity = original.read_json(integrity_path)
        require(summary.get("exclusive_slot") == history["slot"], f"historical practice v{version} was relabeled")
        require(integrity.get("schema") == history["schema"], f"the historical v{version} verifier was substituted")
        require(integrity.get("result") == "PASS", f"the preserved v{version} practice verifier failed")
        require(integrity.get("summary_sha256") == history["summary_sha256"], f"the v{version} result lost its original source binding")
        require(integrity.get("strict_regressions") == history["regressions"], f"historical v{version} slowdowns were removed")
        for previous in HISTORIES[: version - 1]:
            key = f"historical_v{previous['version']}_integrity_sha256"
            require(integrity.get(key) == previous["integrity_sha256"], f"historical v{previous['version']}-to-v{version} continuity changed")
        results.append((summary, integrity))
    return tuple(results)


def check_v5_metadata(summary: dict, integrity: dict) -> None:
    summary_digest = measured_digest(V5_SUMMARY_SHA256, "owned-engine practice summary")
    compressed_digest = measured_digest(V5_COMPRESSED_RAW_SHA256, "compressed owned-engine paired observations")
    raw_digest = measured_digest(V5_RAW_SHA256, "uncompressed owned-engine paired observations")
    expected = {
        "schema": V5_SCHEMA,
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
        "strict_regressions": measured_regressions(),
        "summary_sha256": summary_digest,
        "compressed_raw_sha256": compressed_digest,
        "raw_sha256": raw_digest,
        "from_scratch_audit_sha256": V5_AUDIT_SHA256,
        "full_correctness_campaign_sha256": V5_RUST_CAMPAIGN_SHA256,
        "zig_full_correctness_campaign_sha256": V4_ZIG_CAMPAIGN_SHA256,
        "initial_audit_failure_sha256": INITIAL_AUDIT_FAILURE_SHA256,
        "unchanged_reference_candidates": list(REFERENCE_MODULES),
        "rust_optimization_verified": True,
        "capacity16_optimization_verified": True,
        "zig_optimization_verified": True,
        "mandatory_prefix_optimization_verified": True,
        "unchanged_rust_bridge_verified": True,
    }
    for history in HISTORIES:
        expected[f"historical_v{history['version']}_integrity_sha256"] = history["integrity_sha256"]
    for key, value in expected.items():
        require(integrity.get(key) == value, f"the independent owned-engine results audit does not prove {key}")
    require(summary.get("exclusive_slot") == V5_SLOT, "the exact owned-engine practice slot changed")
    require(summary.get("cohort") == "calibration", "a non-public case entered practice")
    require(summary.get("holdout_accessed") is False, "unseen final cases entered practice")
    require(summary.get("failed") == 0, "an owned-engine timing correctness gate failed")
    require(summary.get("compressed_raw_sha256") == compressed_digest, "the complete compressed v5 observations changed")
    require(summary.get("raw_sha256") == raw_digest, "the complete uncompressed v5 observations changed")
    require(original.sha256_file(V5_AUDITOR) == integrity.get("source_sha256"), "the independent v5 replay verifier was substituted")


def check_unchanged_references(summary: dict, integrity: dict, v4_summary: dict, v4_integrity: dict) -> None:
    historical = v4_summary.get("candidate_binary_sha256_before")
    current = summary.get("candidate_binary_sha256_before")
    require(isinstance(historical, dict) and isinstance(current, dict), "source-bound current or historical production fingerprints are missing")
    require(summary.get("candidate_binary_sha256_after") == current, "a production candidate changed during the measured paired run")
    for module in REFERENCE_MODULES:
        prefix = f"{module}:"
        old = {role: digest for role, digest in historical.items() if role.startswith(prefix)}
        new = {role: digest for role, digest in current.items() if role.startswith(prefix)}
        require(bool(old) and new == old, f"an unchanged standard Python, C, or Zig engine was substituted: {module}")

    old_sources = v4_integrity.get("qualified_source_fingerprints")
    new_sources = integrity.get("qualified_source_fingerprints")
    require(isinstance(old_sources, dict) and isinstance(new_sources, dict), "independently qualified source fingerprints are missing")
    changed_source = "candidates/rust/src/lib.rs"
    expected_engine_source = measured_digest(V5_RUST_ENGINE_SOURCE_SHA256, "actual owned Rust engine source")
    require(new_sources.get(changed_source) == expected_engine_source, "the actually qualified owned Rust source was substituted")
    require(old_sources.get(changed_source) != expected_engine_source, "practice did not measure the new owned Rust source")
    for path, digest in old_sources.items():
        if path != changed_source:
            require(new_sources.get(path) == digest, f"an unrelated Python, C, Zig, Rust bridge, or Rust helper changed: {path}")

    engine_key = f"{original.RUST}:native-engine"
    bridge_key = f"{original.RUST}:native-bridge"
    engine_source_key = f"{original.RUST}:native-source"
    bridge_source_key = f"{original.RUST}:bridge-source"
    engine = measured_digest(V5_RUST_NATIVE_ENGINE_SHA256, "actual owned Rust native engine")
    require(current.get(engine_key) == engine, "the actual owned Rust native engine was substituted")
    require(historical.get(engine_key) != engine, "practice reused the historical Rust engine")
    require(current.get(bridge_key) == historical.get(bridge_key) == UNCHANGED_RUST_NATIVE_BRIDGE_SHA256, "the preserved Rust native bridge was changed")
    require(current.get(bridge_source_key) == historical.get(bridge_source_key) == UNCHANGED_RUST_BRIDGE_SOURCE_SHA256, "the preserved Rust bridge source was changed")
    require(current.get(engine_source_key) == expected_engine_source, "the measured owned Rust source identity is missing")
    for role, digest in historical.items():
        if role.startswith(f"{original.RUST}:") and role not in {engine_key, engine_source_key}:
            require(current.get(role) == digest, f"an unrelated Rust Python surface or native bridge changed: {role}")


def check_owned_engine_edge(summary: dict) -> None:
    expected = measured_digest(V5_RUST_EDGE_REPORT_SHA256, "fresh passing owned Rust correctness proof")
    proofs = summary.get("verified_edge_oracles")
    require(isinstance(proofs, list), "fresh independent correctness proofs are missing")
    rust = [entry for entry in proofs if isinstance(entry, dict) and entry.get("module") == original.RUST]
    require(len(rust) == 1, "the current owned Rust correctness proof is missing or duplicated")
    require(rust[0].get("report_sha256") == expected, "the measured Rust does not match its complete passing correctness proof")


def load_results(summary_path: Path, raw_path: Path, integrity_path: Path):
    require(summary_path.resolve() == SUMMARY.resolve(), "refusing an unrelated owned-engine practice summary")
    require(raw_path.resolve() == RAW.resolve(), "refusing unrelated owned-engine paired observations")
    require(integrity_path.resolve() == INTEGRITY.resolve(), "refusing unrelated owned-engine integrity evidence")
    require(original.sha256_file(summary_path) == measured_digest(V5_SUMMARY_SHA256, "actual v5 summary fingerprint"), "the actual one-shot owned-engine summary changed")
    require(original.sha256_file(raw_path) == measured_digest(V5_COMPRESSED_RAW_SHA256, "actual v5 compressed observations"), "the actual one-shot owned-engine observations changed")

    history = check_history()
    v4_summary, v4_integrity = history[-1]
    summary = original.read_json(summary_path)
    integrity = original.read_json(integrity_path)
    check_v5_metadata(summary, integrity)
    check_unchanged_references(summary, integrity, v4_summary, v4_integrity)
    check_owned_engine_edge(summary)
    with v5_renderer():
        result = original.load_results(summary_path, raw_path, integrity_path)
        charts = original.build_charts(result)
    require(tuple(charts) == SUFFIXES, "a required separate owned-engine practice graph is missing")
    for suffix, content in charts.items():
        require("PRACTICE ONLY" in content, f"the {suffix} graph omitted its public-practice disclosure")
        require("final speed NOT MEASURED" in content, f"the {suffix} graph invented final performance")
    return result, charts


def expect_rejection(action, label: str) -> None:
    try:
        action()
    except (ValueError, TypeError, KeyError, OverflowError):
        return
    raise ValueError(f"synthetic owned-engine version-isolation evidence was accepted: {label}")


def self_test() -> None:
    check_renderers()
    captured = io.StringIO()
    with v5_renderer(synthetic=True):
        with contextlib.redirect_stdout(captured):
            original.self_test()
        summary, integrity, _raw, summary_digest, compressed_digest, raw_digest = original.synthetic_documents()
        controls = json.loads(captured.getvalue())
        require(isinstance(controls, dict) and controls.get("result") == "PASS", "the original synthetic graph controls failed")
        require(controls.get("synthetic_only") is True, "synthetic controls inspected real candidate measurements")
        require(controls.get("holdout_accessed") is False, "synthetic controls accessed unseen workloads")
        require(controls.get("timing_performed") is False, "synthetic controls performed timing")
        require(controls.get("corruption_checks", 0) >= 33, "the original poisoned-evidence controls were weakened")
        require(controls.get("chart_count") == len(SUFFIXES), "synthetic controls omitted a practice graph")
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
        reject_summary("exclusive_slot", "three-qualified-engines-public-practice-v5", "invented-v5-slot-substitution")
        reject_summary("holdout_accessed", True, "unseen-final-workload-access")
        reject_summary("paired_raw_rows", original.RAW_ROWS - 1, "omitted-paired-practice-observation")
        reject_summary("correctness_checks", original.CORRECTNESS_CHECKS - 1, "omitted-practice-correctness-gate")
        reject_summary("modules", list(reversed(original.MODULES)), "substituted-paired-candidate-order")
        reject_summary("bootstrap_samples", original.BOOTSTRAPS - 1, "changed-frozen-confidence-protocol")
        reject_summary("trials", original.TRIALS - 1, "omitted-frozen-paired-trial")
        reject_integrity("summary_sha256", "0" * 64, "substituted-owned-engine-summary")
        reject_integrity("compressed_raw_sha256", "0" * 64, "substituted-compressed-paired-observations")
        reject_integrity("raw_sha256", "0" * 64, "substituted-uncompressed-paired-observations")
        reject_integrity("strict_regressions", HISTORIES[0]["regressions"] - 1, "concealed-synthetic-substantial-slowdown")
        reject_integrity("timing_performed", True, "independent-replay-performs-benchmark-timing")

        data = original.PracticeResults(
            summary,
            integrity,
            tuple(sorted(
                original.check_summary(summary),
                key=lambda value: (-value.ranking["geomean_speedup"], original.DISPLAY[value.module]),
            )),
        )
        charts = original.build_charts(data)
        require(tuple(charts) == SUFFIXES, "synthetic evidence omitted a separate graph")
        require("shared process" in charts["memory"], "Python-traced shared-process memory limitations were omitted")
        require("does not measure native" in charts["memory"], "synthetic evidence invented native memory measurements")
        require(original.build_charts(data) == charts, "owned-engine graph generation is not deterministic")

    check_renderers()
    poisoned = controls["corruption_checks"] + len(extras)
    require(poisoned >= 50, "fewer than 50 synthetic poisoning controls were preserved")
    print(json.dumps({
        "schema": f"{V5_SCHEMA}-charts-self-test",
        "result": "PASS",
        "synthetic_only": True,
        "holdout_accessed": False,
        "timing_performed": False,
        "historical_renderer_sha256": {
            f"v{entry['version']}": entry["renderer_sha256"] for entry in HISTORIES
        },
        "historical_renderers_restored": True,
        "cases_per_candidate": original.CASES,
        "candidate_case_count": original.CASES * len(original.CANDIDATES),
        "trials_per_module_case": original.TRIALS,
        "raw_rows": original.RAW_ROWS,
        "correctness_checks": original.CORRECTNESS_CHECKS,
        "bootstrap_draws": original.BOOTSTRAPS,
        "original_poison_controls": controls["corruption_checks"],
        "additional_version_poison_controls": extras,
        "poisoned_control_count": poisoned,
        "chart_count": len(SUFFIXES),
        "charts_deterministic": True,
        "final_speed": "NOT MEASURED",
    }, sort_keys=True))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate exactly six independently verified owned-engine Rust public-practice graphs.")
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
    require(prefix.parent == EVIDENCE.resolve(), "refusing to write outside public practice evidence")
    _result, charts = load_results(args.summary.resolve(), args.raw.resolve(), args.integrity.resolve())
    for suffix in SUFFIXES:
        destination = prefix.parent / f"{prefix.name}-{suffix}.svg"
        destination.write_text(charts[suffix], encoding="utf-8")
        print(f"wrote {destination.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
