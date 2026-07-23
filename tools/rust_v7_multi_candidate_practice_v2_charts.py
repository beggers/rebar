#!/usr/bin/env python3
"""Render only the audited, fused-vectorcall four-way public-practice run."""

from __future__ import annotations

import argparse
import contextlib
import copy
import io
import json
from pathlib import Path

from tools import rust_v7_multi_candidate_practice_charts as v1


ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "performance" / "v7" / "evidence"
PREFIX = EVIDENCE / "three-qualified-engines-public-practice-v2"
SUMMARY = EVIDENCE / "three-qualified-engines-public-practice-v2-summary.json"
RAW = EVIDENCE / "three-qualified-engines-public-practice-v2-raw.jsonl.gz"
INTEGRITY = EVIDENCE / "three-qualified-engines-public-practice-v2-integrity.json"
V2_AUDITOR = ROOT / "tools" / "rust_v7_multi_candidate_practice_v2_audit.py"

V1_RENDERER_SHA256 = "5674fecff2b2555b725fd154cfdb1f7ee9ce7b951895c7a38f0f124f5304dddf"
V1_SUMMARY_SHA256 = "20c33badfc08d98566c5476452370f042cd8ff544ecc5ed98f6d1111550328f0"
V1_INTEGRITY_SHA256 = "8739803b6cd020b8b4f663223435fd1e39ef5603e90195b2a268a9fa7fbc0340"
V1_SLOT = "three-qualified-engines-public-practice-v1"
V1_SCHEMA = "rebar-v7-multi-candidate-practice-integrity-v1"
V1_REGRESSIONS = 426

V2_SLOT = "three-qualified-engines-fused-vectorcall-v2"
V2_SCHEMA = "rebar-v7-multi-candidate-practice-integrity-v2"
V2_SUMMARY_SHA256 = "db3cc7f4704df7b0a6b1283818d0dfdf96947d83d44752bf633a640a3e721cab"
V2_COMPRESSED_RAW_SHA256 = "81b1a8c99f8f460539d9b212127d2ba9c76720987d4dde49c5c0186f31c05e76"
V2_RAW_SHA256 = "3fd49183c18e31c3319c7f8df31ea1cf829a0e70d8be593ee89b349ffdd36718"
V2_AUDIT_SHA256 = "ee98f2098223585e4cc3d484d97d36a33c358ccdfd133e6db78c8dad89d1a355"
V2_CAMPAIGN_SHA256 = "d54d11835e6fd1d4b6bf81d6bdd9f72d219265fbd48142cb923274bf5b6f681e"
V2_RUST_BRIDGE_SOURCE_SHA256 = "88a8a6b086061da69022a978eba3a0f0317a378f0a758c44ec84fb9c1c0b3c65"
V2_RUST_EDGE_REPORT_SHA256 = "90fbd41d862cba6b926929dc99c53c4e981ed4da7a73d4652b20d3013d544ad4"
V2_REGRESSIONS = 401
REFERENCE_MODULES = (v1.BASELINE, v1.C_ENGINE, v1.ZIG)
V2_SUFFIXES = ("overall", "outcomes", "api", "regressions", "memory", "rankings")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def check_renderer() -> None:
    require(
        Path(v1.__file__).resolve()
        == (ROOT / "tools" / "rust_v7_multi_candidate_practice_charts.py").resolve(),
        "the immutable historical chart renderer was substituted",
    )
    require(
        v1.sha256_file(Path(v1.__file__).resolve()) == V1_RENDERER_SHA256,
        "the immutable historical practice renderer changed",
    )
    require(v1.SLOT == V1_SLOT, "historical practice-slot controls were modified")
    require(v1.INTEGRITY_SCHEMA == V1_SCHEMA, "historical integrity-schema controls were modified")
    require(v1.EXPECTED_REGRESSIONS == V1_REGRESSIONS, "historical slowdown controls were modified")
    require(v1.CHART_SUFFIXES == V2_SUFFIXES, "a required historical chart renderer is missing")
    require(v1.CASES == 624, "the frozen per-engine practice denominator changed")
    require(v1.TRIALS == 7, "the frozen paired-trial denominator changed")
    require(v1.BOOTSTRAPS == 499, "the frozen confidence protocol changed")
    require(v1.RAW_ROWS == 17_472, "the frozen paired-row denominator changed")
    require(v1.CORRECTNESS_CHECKS == 52_416, "a frozen correctness gate was omitted")
    require(
        v1.MODULES
        == (
            "re",
            "candidates.rust_candidate",
            "candidates.vm_candidate",
            "candidates.zig_candidate",
        ),
        "the four independently audited practice engines changed",
    )
    require(len(v1.API_COUNTS) == 12, "a frozen public operation was dropped")


@contextlib.contextmanager
def v2_renderer(*, synthetic: bool = False):
    """Apply exact v2 bounds only inside this isolated, reversible process."""

    check_renderer()
    saved = (v1.SLOT, v1.INTEGRITY_SCHEMA, v1.EXPECTED_REGRESSIONS)
    v1.SLOT = V2_SLOT
    v1.INTEGRITY_SCHEMA = V2_SCHEMA
    v1.EXPECTED_REGRESSIONS = V1_REGRESSIONS if synthetic else V2_REGRESSIONS
    try:
        yield
    finally:
        v1.SLOT, v1.INTEGRITY_SCHEMA, v1.EXPECTED_REGRESSIONS = saved
        check_renderer()


def check_history() -> tuple[dict, dict]:
    require(
        v1.sha256_file(v1.DEFAULT_SUMMARY) == V1_SUMMARY_SHA256,
        "the preserved original four-way practice summary changed",
    )
    require(
        v1.sha256_file(v1.DEFAULT_INTEGRITY) == V1_INTEGRITY_SHA256,
        "the preserved original four-way practice integrity evidence changed",
    )
    historical_summary = v1.read_json(v1.DEFAULT_SUMMARY)
    historical_integrity = v1.read_json(v1.DEFAULT_INTEGRITY)
    require(historical_summary.get("exclusive_slot") == V1_SLOT, "historical practice was relabeled")
    require(historical_integrity.get("schema") == V1_SCHEMA, "historical practice evidence was relabeled")
    require(historical_integrity.get("result") == "PASS", "the preserved historical practice audit failed")
    require(
        historical_integrity.get("summary_sha256") == V1_SUMMARY_SHA256,
        "historical integrity does not bind its original measured result",
    )
    require(
        historical_integrity.get("strict_regressions") == V1_REGRESSIONS,
        "historical practice slowdowns were rewritten",
    )
    return historical_summary, historical_integrity


def check_v2_metadata(summary: dict, integrity: dict) -> None:
    exact = {
        "schema": V2_SCHEMA,
        "result": "PASS",
        "holdout_accessed": False,
        "timing_performed": False,
        "module_order": list(v1.MODULES),
        "cases_per_candidate": 624,
        "candidate_case_count": 1_872,
        "trials_per_module_case": 7,
        "raw_rows": 17_472,
        "correctness_checks": 52_416,
        "bootstrap_draws": 499,
        "strict_regressions": V2_REGRESSIONS,
        "summary_sha256": V2_SUMMARY_SHA256,
        "compressed_raw_sha256": V2_COMPRESSED_RAW_SHA256,
        "raw_sha256": V2_RAW_SHA256,
        "from_scratch_audit_sha256": V2_AUDIT_SHA256,
        "historical_v1_integrity_sha256": V1_INTEGRITY_SHA256,
        "unchanged_reference_candidates": list(REFERENCE_MODULES),
        "rust_optimization_verified": True,
        "full_correctness_campaign_sha256": V2_CAMPAIGN_SHA256,
    }
    for key, expected in exact.items():
        require(integrity.get(key) == expected, f"the fused-vectorcall results audit does not verify {key}")
    require(summary.get("exclusive_slot") == V2_SLOT, "the experiment used a different timing slot")
    require(summary.get("cohort") == "calibration", "only public practice can be displayed")
    require(summary.get("holdout_accessed") is False, "unseen final cases were accessed")
    require(summary.get("failed") == 0, "a public-practice correctness gate failed")
    require(summary.get("compressed_raw_sha256") == V2_COMPRESSED_RAW_SHA256, "the actual compressed v2 observations changed")
    require(summary.get("raw_sha256") == V2_RAW_SHA256, "the actual uncompressed v2 observations changed")
    require(v1.sha256_file(V2_AUDITOR) == integrity.get("source_sha256"), "the independent v2 audit source was substituted")


def check_unchanged_references(summary: dict, integrity: dict, historical_summary: dict, historical_integrity: dict) -> None:
    old_artifacts = historical_summary.get("candidate_binary_sha256_before")
    artifacts = summary.get("candidate_binary_sha256_before")
    require(isinstance(old_artifacts, dict) and isinstance(artifacts, dict), "measured engine identities are missing")
    require(summary.get("candidate_binary_sha256_after") == artifacts, "a measured v2 candidate changed during paired practice")
    for module in REFERENCE_MODULES:
        prefix = f"{module}:"
        old = {role: value for role, value in old_artifacts.items() if role.startswith(prefix)}
        new = {role: value for role, value in artifacts.items() if role.startswith(prefix)}
        require(bool(old) and new == old, f"the standard Python, C, or Zig reference changed: {module}")

    old_sources = historical_integrity.get("qualified_source_fingerprints")
    new_sources = integrity.get("qualified_source_fingerprints")
    require(isinstance(old_sources, dict) and isinstance(new_sources, dict), "independent source identity is missing")
    reference_paths = (
        "candidates/vm_candidate.py",
        "candidates/_vm_native.c",
        "candidates/zig_candidate.py",
        "candidates/zig/mini_regex.zig",
        "candidates/zig/py_bridge.c",
    )
    for path in reference_paths:
        require(path in old_sources and new_sources.get(path) == old_sources[path], f"a C or Zig from-scratch reference source changed: {path}")

    bridge_path = "candidates/rust/py_bridge.c"
    require(new_sources.get(bridge_path) == V2_RUST_BRIDGE_SOURCE_SHA256, "the actually qualified fused-vectorcall bridge was substituted")
    require(old_sources.get(bridge_path) != new_sources[bridge_path], "the v2 result did not measure the new fused-vectorcall bridge")
    for path, digest in old_sources.items():
        if path == "candidates/rust_candidate.py" or path.startswith("candidates/rust/"):
            if path != bridge_path:
                require(new_sources.get(path) == digest, f"the experiment changed an unrelated Rust source: {path}")

    old_bridge = old_artifacts.get(f"{v1.RUST}:native-bridge")
    new_bridge = artifacts.get(f"{v1.RUST}:native-bridge")
    require(isinstance(new_bridge, str) and len(new_bridge) == 64, "the measured fused-vectorcall bridge is missing")
    require(old_bridge != new_bridge, "the measured native Rust bridge did not change")
    for role, digest in old_artifacts.items():
        if role.startswith(f"{v1.RUST}:") and role not in {
            f"{v1.RUST}:bridge-source",
            f"{v1.RUST}:native-bridge",
        }:
            require(artifacts.get(role) == digest, f"the experiment changed an unrelated Rust artifact: {role}")


def check_fused_edge(summary: dict) -> None:
    proofs = summary.get("verified_edge_oracles")
    require(isinstance(proofs, list), "fresh correctness proofs are missing")
    rust_proofs = [proof for proof in proofs if isinstance(proof, dict) and proof.get("module") == v1.RUST]
    require(len(rust_proofs) == 1, "the fused-vectorcall correctness proof is missing or duplicated")
    require(
        rust_proofs[0].get("report_sha256") == V2_RUST_EDGE_REPORT_SHA256,
        "practice did not use the exact passing fused-vectorcall Rust correctness report",
    )


def load_results(summary_path: Path, raw_path: Path, integrity_path: Path):
    require(summary_path.resolve() == SUMMARY.resolve(), "refusing a substituted v2 practice summary")
    require(raw_path.resolve() == RAW.resolve(), "refusing substituted v2 practice observations")
    require(integrity_path.resolve() == INTEGRITY.resolve(), "refusing substituted v2 practice integrity evidence")
    require(v1.sha256_file(summary_path) == V2_SUMMARY_SHA256, "the actual frozen v2 summary bytes changed")
    require(v1.sha256_file(raw_path) == V2_COMPRESSED_RAW_SHA256, "the actual frozen v2 observation bytes changed")

    historical_summary, historical_integrity = check_history()
    summary = v1.read_json(summary_path)
    integrity = v1.read_json(integrity_path)
    check_v2_metadata(summary, integrity)
    check_unchanged_references(summary, integrity, historical_summary, historical_integrity)
    check_fused_edge(summary)
    with v2_renderer():
        data = v1.load_results(summary_path, raw_path, integrity_path)
        charts = v1.build_charts(data)
    require(tuple(charts) == V2_SUFFIXES, "a separately required v2 graph is missing")
    for suffix, content in charts.items():
        require("PRACTICE ONLY" in content, f"the {suffix} graph omits its practice-only scope")
        require("final speed NOT MEASURED" in content, f"the {suffix} graph invents a final result")
    return data, charts


def expect_rejection(action, label: str) -> None:
    try:
        action()
    except (ValueError, TypeError, KeyError, OverflowError):
        return
    raise ValueError(f"synthetic v2 version-control evidence was accepted: {label}")


def self_test() -> None:
    check_renderer()
    captured = io.StringIO()
    with v2_renderer(synthetic=True):
        with contextlib.redirect_stdout(captured):
            v1.self_test()
        summary, integrity, raw_lines, summary_digest, compressed_digest, raw_digest = v1.synthetic_documents()
        controls = json.loads(captured.getvalue())
        require(isinstance(controls, dict) and controls.get("result") == "PASS", "the original synthetic graph safety controls failed")
        require(controls.get("synthetic_only") is True, "synthetic controls inspected actual practice results")
        require(controls.get("holdout_accessed") is False, "synthetic controls accessed hidden workloads")
        require(controls.get("timing_performed") is False, "synthetic controls performed timing")
        require(controls.get("corruption_checks", 0) >= 33, "the original 33 deterministic corruption controls were weakened")
        require(controls.get("chart_count") == len(V2_SUFFIXES), "a required synthetic graph is missing")

        extra_controls: list[str] = []

        def reject_summary(key: str, value: object, label: str) -> None:
            changed = copy.deepcopy(summary)
            changed[key] = value
            expect_rejection(lambda: v1.check_summary(changed), label)
            extra_controls.append(label)

        def reject_integrity(key: str, value: object, label: str) -> None:
            changed = copy.deepcopy(integrity)
            changed[key] = value
            expect_rejection(
                lambda: v1.check_integrity(
                    summary,
                    changed,
                    summary_digest=summary_digest,
                    compressed_digest=compressed_digest,
                    raw_digest=raw_digest,
                ),
                label,
            )
            extra_controls.append(label)

        reject_summary("exclusive_slot", V1_SLOT, "historical-v1-slot-substitution")
        reject_summary("exclusive_slot", "three-qualified-engines-public-practice-v2", "wrong-v2-slot-substitution")
        reject_summary("holdout_accessed", True, "unseen-test-access")
        reject_summary("paired_raw_rows", v1.RAW_ROWS - 1, "missing-paired-public-observation")
        reject_summary("correctness_checks", v1.CORRECTNESS_CHECKS - 1, "missing-public-correctness-gate")
        reject_summary("modules", list(reversed(v1.MODULES)), "substituted-paired-candidate-order")
        reject_integrity("schema", V1_SCHEMA, "historical-v1-integrity-substitution")
        reject_integrity("summary_sha256", "0" * 64, "substituted-v2-summary-digest")
        reject_integrity("compressed_raw_sha256", "0" * 64, "substituted-v2-compressed-observations")
        reject_integrity("raw_sha256", "0" * 64, "substituted-v2-uncompressed-observations")
        reject_integrity("strict_regressions", V1_REGRESSIONS - 1, "concealed-synthetic-slowdown")
        reject_integrity("timing_performed", True, "audit-performs-timing")

        charts = v1.build_charts(
            v1.PracticeResults(
                summary,
                integrity,
                tuple(
                    sorted(
                        v1.check_summary(summary),
                        key=lambda item: (
                            -item.ranking["geomean_speedup"],
                            v1.DISPLAY[item.module],
                        ),
                    )
                ),
            )
        )
        require(tuple(charts) == V2_SUFFIXES, "synthetic v2 dropped a required graph")
        require("shared process" in charts["memory"], "synthetic v2 hid its shared-process memory limitation")
        require("does not measure native" in charts["memory"], "synthetic v2 invented native memory measurements")
        require(v1.build_charts(v1.PracticeResults(
            summary,
            integrity,
            tuple(sorted(v1.check_summary(summary), key=lambda item: (-item.ranking["geomean_speedup"], v1.DISPLAY[item.module]))),
        )) == charts, "synthetic v2 SVG generation is not deterministic")

    check_renderer()
    print(
        json.dumps(
            {
                "schema": f"{V2_SCHEMA}-charts-self-test",
                "result": "PASS",
                "synthetic_only": True,
                "holdout_accessed": False,
                "timing_performed": False,
                "historical_renderer_sha256": V1_RENDERER_SHA256,
                "historical_renderer_restored": True,
                "cases_per_candidate": v1.CASES,
                "candidate_case_count": v1.CASES * len(v1.CANDIDATES),
                "trials_per_module_case": v1.TRIALS,
                "raw_rows": v1.RAW_ROWS,
                "correctness_checks": v1.CORRECTNESS_CHECKS,
                "bootstrap_draws": v1.BOOTSTRAPS,
                "original_poison_controls": controls["corruption_checks"],
                "additional_version_poison_controls": extra_controls,
                "poisoned_control_count": controls["corruption_checks"] + len(extra_controls),
                "chart_count": len(V2_SUFFIXES),
                "charts_deterministic": True,
                "final_speed": "NOT MEASURED",
            },
            sort_keys=True,
        )
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate exactly six source-bound, fused-vectorcall, public-practice-only graphs."
    )
    parser.add_argument("--summary", type=Path, default=SUMMARY)
    parser.add_argument("--raw", type=Path, default=RAW)
    parser.add_argument("--integrity", type=Path, default=INTEGRITY)
    parser.add_argument("--prefix", type=Path, default=PREFIX)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run only synthetic v2 version-isolation and deterministic graph controls",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.self_test:
        self_test()
        return

    check_renderer()
    prefix = args.prefix.resolve()
    require(prefix == PREFIX.resolve(), "refusing to redirect or overwrite historical practice graphs")
    require(prefix.parent == EVIDENCE.resolve(), "refusing to write outside public practice evidence")
    _data, charts = load_results(args.summary.resolve(), args.raw.resolve(), args.integrity.resolve())
    for suffix in V2_SUFFIXES:
        destination = prefix.parent / f"{prefix.name}-{suffix}.svg"
        destination.write_text(charts[suffix], encoding="utf-8")
        print(f"wrote {destination.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
