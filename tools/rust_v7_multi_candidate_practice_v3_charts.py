#!/usr/bin/env python3
"""Render only the independently verified capacity-16 public-practice run."""

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
PREFIX = EVIDENCE / "three-qualified-engines-public-practice-v3"
SUMMARY = EVIDENCE / "three-qualified-engines-public-practice-v3-summary.json"
RAW = EVIDENCE / "three-qualified-engines-public-practice-v3-raw.jsonl.gz"
INTEGRITY = EVIDENCE / "three-qualified-engines-public-practice-v3-integrity.json"
V3_AUDITOR = ROOT / "tools" / "rust_v7_multi_candidate_practice_v3_audit.py"

V1_RENDERER_SHA256 = "5674fecff2b2555b725fd154cfdb1f7ee9ce7b951895c7a38f0f124f5304dddf"
V2_RENDERER_SHA256 = "3f81638918886de725500c23059b383e2773d493cbbfc5bb296f29721afd618d"
V1_SUMMARY_SHA256 = "20c33badfc08d98566c5476452370f042cd8ff544ecc5ed98f6d1111550328f0"
V1_INTEGRITY_SHA256 = "8739803b6cd020b8b4f663223435fd1e39ef5603e90195b2a268a9fa7fbc0340"
V2_SUMMARY_SHA256 = "db3cc7f4704df7b0a6b1283818d0dfdf96947d83d44752bf633a640a3e721cab"
V2_INTEGRITY_SHA256 = "82ef917ca82ba124af6311f3bf10398a2a040286ed06430919bbdd26dd61e057"
V1_SLOT = "three-qualified-engines-public-practice-v1"
V2_SLOT = "three-qualified-engines-fused-vectorcall-v2"
V3_SLOT = "three-qualified-engines-findall-capacity-16-v3"
V1_SCHEMA = "rebar-v7-multi-candidate-practice-integrity-v1"
V2_SCHEMA = "rebar-v7-multi-candidate-practice-integrity-v2"
V3_SCHEMA = "rebar-v7-multi-candidate-practice-integrity-v3"
V1_REGRESSIONS = 426
V2_REGRESSIONS = 401

# Freeze only the actual, complete, one-shot four-way public-practice result.
V3_SUMMARY_SHA256: str | None = "33ebdff8ecb061e3544b9cd4bc687040b8278aa037f3c993abe654daa665d155"
V3_COMPRESSED_RAW_SHA256: str | None = "d17ae80c1a2d8adddf2ddeecd3ff84377e72f293d8ca8add2ad1c533bcf562b1"
V3_RAW_SHA256: str | None = "225c3c83e4a8170f5851586f70aed0c58cc056778a8c718b7799abc896bf169c"
V3_REGRESSIONS: int | None = 387

V3_AUDIT_SHA256 = "af69f41966a26d9ec1892e34b16f1bc02eb095c41767899d0a3deb612591d8fc"
V3_CAMPAIGN_SHA256 = "89793a597ac74551742d05bdf1c5af61f1121d89466e00ac2902c8942aaeef4d"
V3_RUST_BRIDGE_SOURCE_SHA256 = "83afb5a709a6d0ea1701dfd64db30644edbf2cb0276c2db731a8119cfd52d8ed"
V3_RUST_NATIVE_BRIDGE_SHA256 = "1f072e81ba9339a8b2e52a7e93b7bcde791c4d518620b6bd760af67c7c89af34"
V3_RUST_EDGE_REPORT_SHA256 = "cec324450b93abaf3b1727d06e8334658a6996f150648bf97733303bce0f201b"
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
        isinstance(V3_REGRESSIONS, int)
        and not isinstance(V3_REGRESSIONS, bool)
        and 0 <= V3_REGRESSIONS <= 624 * 3,
        "the actual capacity-16 slowdown count is NOT MEASURED or invalid",
    )
    return V3_REGRESSIONS


def check_renderers() -> None:
    historical_path = ROOT / "tools" / "rust_v7_multi_candidate_practice_charts.py"
    v2_path = ROOT / "tools" / "rust_v7_multi_candidate_practice_v2_charts.py"
    require(Path(original.__file__).resolve() == historical_path.resolve(), "the original pure chart renderer was substituted")
    require(original.sha256_file(historical_path) == V1_RENDERER_SHA256, "the immutable v1 practice renderer changed")
    require(original.sha256_file(v2_path) == V2_RENDERER_SHA256, "the immutable v2 practice renderer changed")
    require(original.SLOT == V1_SLOT, "original practice-slot controls were modified")
    require(original.INTEGRITY_SCHEMA == V1_SCHEMA, "original integrity-schema controls were modified")
    require(original.EXPECTED_REGRESSIONS == V1_REGRESSIONS, "original slowdown controls were modified")
    require(original.CHART_SUFFIXES == SUFFIXES, "a separately required graph renderer was dropped")
    require(original.CASES == 624, "the frozen case denominator changed")
    require(original.TRIALS == 7, "the frozen paired-trial denominator changed")
    require(original.BOOTSTRAPS == 499, "the frozen confidence protocol changed")
    require(original.RAW_ROWS == 17_472, "the frozen raw-row denominator changed")
    require(original.CORRECTNESS_CHECKS == 52_416, "a correctness gate was dropped")
    require(
        original.MODULES == (
            "re",
            "candidates.rust_candidate",
            "candidates.vm_candidate",
            "candidates.zig_candidate",
        ),
        "the Python baseline or an independent candidate changed",
    )
    require(len(original.API_COUNTS) == 12, "a public operation group was omitted")


@contextlib.contextmanager
def v3_renderer(*, synthetic: bool = False):
    """Temporarily scope exact v3 controls; always restore the v1 renderer."""

    check_renderers()
    previous = (original.SLOT, original.INTEGRITY_SCHEMA, original.EXPECTED_REGRESSIONS)
    original.SLOT = V3_SLOT
    original.INTEGRITY_SCHEMA = V3_SCHEMA
    original.EXPECTED_REGRESSIONS = V1_REGRESSIONS if synthetic else measured_regressions()
    try:
        yield
    finally:
        original.SLOT, original.INTEGRITY_SCHEMA, original.EXPECTED_REGRESSIONS = previous
        check_renderers()


def check_history() -> tuple[dict, dict, dict, dict]:
    v1_summary_path = original.DEFAULT_SUMMARY
    v1_integrity_path = original.DEFAULT_INTEGRITY
    v2_summary_path = EVIDENCE / "three-qualified-engines-public-practice-v2-summary.json"
    v2_integrity_path = EVIDENCE / "three-qualified-engines-public-practice-v2-integrity.json"
    for path, digest, label in (
        (v1_summary_path, V1_SUMMARY_SHA256, "original public practice summary"),
        (v1_integrity_path, V1_INTEGRITY_SHA256, "original public practice audit"),
        (v2_summary_path, V2_SUMMARY_SHA256, "fused-vectorcall public practice summary"),
        (v2_integrity_path, V2_INTEGRITY_SHA256, "fused-vectorcall public practice audit"),
    ):
        require(original.sha256_file(path) == digest, f"the immutable {label} changed")

    v1_summary = original.read_json(v1_summary_path)
    v1_integrity = original.read_json(v1_integrity_path)
    v2_summary = original.read_json(v2_summary_path)
    v2_integrity = original.read_json(v2_integrity_path)
    for summary, integrity, slot, schema, digest, regressions in (
        (v1_summary, v1_integrity, V1_SLOT, V1_SCHEMA, V1_SUMMARY_SHA256, V1_REGRESSIONS),
        (v2_summary, v2_integrity, V2_SLOT, V2_SCHEMA, V2_SUMMARY_SHA256, V2_REGRESSIONS),
    ):
        require(summary.get("exclusive_slot") == slot, "a historical practice run was relabeled")
        require(integrity.get("schema") == schema, "a historical practice audit was relabeled")
        require(integrity.get("result") == "PASS", "a preserved historical practice audit failed")
        require(integrity.get("summary_sha256") == digest, "historical integrity does not bind its original measured results")
        require(integrity.get("strict_regressions") == regressions, "historical substantial slowdowns were rewritten")
    require(v2_integrity.get("historical_v1_integrity_sha256") == V1_INTEGRITY_SHA256, "the historical v1-to-v2 chain changed")
    return v1_summary, v1_integrity, v2_summary, v2_integrity


def check_v3_metadata(summary: dict, integrity: dict) -> None:
    summary_digest = measured_digest(V3_SUMMARY_SHA256, "v3 summary fingerprint")
    compressed_digest = measured_digest(V3_COMPRESSED_RAW_SHA256, "compressed v3 observations")
    raw_digest = measured_digest(V3_RAW_SHA256, "uncompressed v3 observations")
    loss_count = measured_regressions()
    expected = {
        "schema": V3_SCHEMA,
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
        "strict_regressions": loss_count,
        "summary_sha256": summary_digest,
        "compressed_raw_sha256": compressed_digest,
        "raw_sha256": raw_digest,
        "from_scratch_audit_sha256": V3_AUDIT_SHA256,
        "historical_v1_integrity_sha256": V1_INTEGRITY_SHA256,
        "historical_v2_integrity_sha256": V2_INTEGRITY_SHA256,
        "full_correctness_campaign_sha256": V3_CAMPAIGN_SHA256,
        "unchanged_reference_candidates": list(REFERENCE_MODULES),
        "capacity16_optimization_verified": True,
        "rust_optimization_verified": True,
    }
    for key, value in expected.items():
        require(integrity.get(key) == value, f"the independently replayed v3 evidence does not prove {key}")
    require(summary.get("exclusive_slot") == V3_SLOT, "the four-way capacity-16 practice slot changed")
    require(summary.get("cohort") == "calibration", "a non-public practice cohort entered the graph")
    require(summary.get("holdout_accessed") is False, "unseen final cases entered public practice")
    require(summary.get("failed") == 0, "a v3 practice correctness gate failed")
    require(summary.get("compressed_raw_sha256") == compressed_digest, "the measured v3 compressed observations changed")
    require(summary.get("raw_sha256") == raw_digest, "the measured v3 uncompressed observations changed")
    require(original.sha256_file(V3_AUDITOR) == integrity.get("source_sha256"), "the independent v3 replay auditor was substituted")


def check_unchanged_references(summary: dict, integrity: dict, v2_summary: dict, v2_integrity: dict) -> None:
    historical = v2_summary.get("candidate_binary_sha256_before")
    measured = summary.get("candidate_binary_sha256_before")
    require(isinstance(historical, dict) and isinstance(measured, dict), "source-bound candidate identities are missing")
    require(summary.get("candidate_binary_sha256_after") == measured, "a candidate changed during the actual four-way run")
    for module in REFERENCE_MODULES:
        prefix = f"{module}:"
        old = {key: value for key, value in historical.items() if key.startswith(prefix)}
        new = {key: value for key, value in measured.items() if key.startswith(prefix)}
        require(bool(old) and new == old, f"an unchanged Python, C, or Zig reference was replaced: {module}")

    old_sources = v2_integrity.get("qualified_source_fingerprints")
    new_sources = integrity.get("qualified_source_fingerprints")
    require(isinstance(old_sources, dict) and isinstance(new_sources, dict), "historical or capacity-16 source evidence is missing")
    for path in (
        "candidates/vm_candidate.py",
        "candidates/_vm_native.c",
        "candidates/zig_candidate.py",
        "candidates/zig/mini_regex.zig",
        "candidates/zig/py_bridge.c",
    ):
        require(path in old_sources and new_sources.get(path) == old_sources[path], f"a C or Zig source changed: {path}")

    bridge = "candidates/rust/py_bridge.c"
    require(new_sources.get(bridge) == V3_RUST_BRIDGE_SOURCE_SHA256, "the real capacity-16 Rust bridge source was substituted")
    require(new_sources.get(bridge) != old_sources.get(bridge), "the new Rust capacity-16 bridge was not measured")
    for path, digest in old_sources.items():
        if path == "candidates/rust_candidate.py" or path.startswith("candidates/rust/"):
            if path != bridge:
                require(new_sources.get(path) == digest, f"an unrelated Rust source changed: {path}")

    new_bridge = measured.get(f"{original.RUST}:native-bridge")
    require(new_bridge == V3_RUST_NATIVE_BRIDGE_SHA256, "the actual capacity-16 Rust native bridge was substituted")
    require(new_bridge != historical.get(f"{original.RUST}:native-bridge"), "the historical Rust bridge was reused")
    for key, digest in historical.items():
        if key.startswith(f"{original.RUST}:") and key not in {
            f"{original.RUST}:native-bridge",
            f"{original.RUST}:bridge-source",
        }:
            require(measured.get(key) == digest, f"an unrelated Rust artifact changed: {key}")


def check_capacity16_edge(summary: dict) -> None:
    proofs = summary.get("verified_edge_oracles")
    require(isinstance(proofs, list), "independent candidate correctness proofs are missing")
    rust = [row for row in proofs if isinstance(row, dict) and row.get("module") == original.RUST]
    require(len(rust) == 1, "the current capacity-16 Rust proof is missing or duplicated")
    require(rust[0].get("report_sha256") == V3_RUST_EDGE_REPORT_SHA256, "the practice run did not use the actual passing capacity-16 Rust proof")


def load_results(summary_path: Path, raw_path: Path, integrity_path: Path):
    require(summary_path.resolve() == SUMMARY.resolve(), "refusing a substituted v3 practice summary")
    require(raw_path.resolve() == RAW.resolve(), "refusing substituted v3 paired measurements")
    require(integrity_path.resolve() == INTEGRITY.resolve(), "refusing substituted v3 independent evidence")
    summary_digest = measured_digest(V3_SUMMARY_SHA256, "v3 summary fingerprint")
    compressed_digest = measured_digest(V3_COMPRESSED_RAW_SHA256, "compressed v3 observations")
    require(original.sha256_file(summary_path) == summary_digest, "the exact one-shot v3 summary was replaced")
    require(original.sha256_file(raw_path) == compressed_digest, "the exact one-shot v3 raw observations were replaced")

    _v1_summary, _v1_integrity, v2_summary, v2_integrity = check_history()
    summary = original.read_json(summary_path)
    integrity = original.read_json(integrity_path)
    check_v3_metadata(summary, integrity)
    check_unchanged_references(summary, integrity, v2_summary, v2_integrity)
    check_capacity16_edge(summary)
    with v3_renderer():
        result = original.load_results(summary_path, raw_path, integrity_path)
        charts = original.build_charts(result)
    require(tuple(charts) == SUFFIXES, "a required v3 graph was dropped or substituted")
    for suffix, content in charts.items():
        require("PRACTICE ONLY" in content, f"the {suffix} graph omitted its public-only scope")
        require("final speed NOT MEASURED" in content, f"the {suffix} graph invented a final result")
    return result, charts


def expect_rejection(action, label: str) -> None:
    try:
        action()
    except (ValueError, TypeError, KeyError, OverflowError):
        return
    raise ValueError(f"synthetic capacity-16 version-control evidence was accepted: {label}")


def self_test() -> None:
    check_renderers()
    captured = io.StringIO()
    with v3_renderer(synthetic=True):
        with contextlib.redirect_stdout(captured):
            original.self_test()
        summary, integrity, raw_lines, summary_digest, compressed_digest, raw_digest = original.synthetic_documents()
        controls = json.loads(captured.getvalue())
        require(isinstance(controls, dict) and controls.get("result") == "PASS", "original synthetic graph corruption controls failed")
        require(controls.get("synthetic_only") is True, "a synthetic check inspected actual results")
        require(controls.get("holdout_accessed") is False, "a synthetic check accessed hidden workloads")
        require(controls.get("timing_performed") is False, "a synthetic check timed an engine")
        require(controls.get("corruption_checks", 0) >= 33, "the original deterministic corruption controls were weakened")
        require(controls.get("chart_count") == len(SUFFIXES), "synthetic verification omitted a required graph")

        extra: list[str] = []

        def reject_summary(key: str, value: object, label: str) -> None:
            poisoned = copy.deepcopy(summary)
            poisoned[key] = value
            expect_rejection(lambda: original.check_summary(poisoned), label)
            extra.append(label)

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
            extra.append(label)

        reject_summary("exclusive_slot", V1_SLOT, "historical-v1-slot-substitution")
        reject_summary("exclusive_slot", V2_SLOT, "historical-v2-slot-substitution")
        reject_summary("exclusive_slot", "three-qualified-engines-public-practice-v3", "invented-v3-slot-substitution")
        reject_summary("holdout_accessed", True, "unseen-test-access")
        reject_summary("paired_raw_rows", original.RAW_ROWS - 1, "missing-paired-public-observation")
        reject_summary("correctness_checks", original.CORRECTNESS_CHECKS - 1, "missing-public-correctness-gate")
        reject_summary("modules", list(reversed(original.MODULES)), "substituted-paired-candidate-order")
        reject_summary("bootstrap_samples", original.BOOTSTRAPS - 1, "weakened-confidence-protocol")
        reject_integrity("schema", V1_SCHEMA, "historical-v1-integrity-substitution")
        reject_integrity("schema", V2_SCHEMA, "historical-v2-integrity-substitution")
        reject_integrity("summary_sha256", "0" * 64, "substituted-capacity16-summary")
        reject_integrity("compressed_raw_sha256", "0" * 64, "substituted-compressed-paired-observations")
        reject_integrity("raw_sha256", "0" * 64, "substituted-uncompressed-paired-observations")
        reject_integrity("strict_regressions", V1_REGRESSIONS - 1, "concealed-synthetic-slowdown")
        reject_integrity("timing_performed", True, "independent-audit-performs-timing")

        synthetic_result = original.PracticeResults(
            summary,
            integrity,
            tuple(
                sorted(
                    original.check_summary(summary),
                    key=lambda item: (-item.ranking["geomean_speedup"], original.DISPLAY[item.module]),
                )
            ),
        )
        charts = original.build_charts(synthetic_result)
        require(tuple(charts) == SUFFIXES, "synthetic capacity-16 verification lost a graph")
        require("shared process" in charts["memory"], "the graph concealed shared-process memory limitations")
        require("does not measure native" in charts["memory"], "the graph invented native memory observations")
        require(original.build_charts(synthetic_result) == charts, "capacity-16 graph generation is not deterministic")

    check_renderers()
    require(controls["corruption_checks"] + len(extra) >= 45, "fewer than 45 poisoning controls were preserved")
    print(
        json.dumps(
            {
                "schema": f"{V3_SCHEMA}-charts-self-test",
                "result": "PASS",
                "synthetic_only": True,
                "holdout_accessed": False,
                "timing_performed": False,
                "historical_v1_renderer_sha256": V1_RENDERER_SHA256,
                "historical_v2_renderer_sha256": V2_RENDERER_SHA256,
                "historical_renderers_restored": True,
                "cases_per_candidate": original.CASES,
                "candidate_case_count": original.CASES * len(original.CANDIDATES),
                "trials_per_module_case": original.TRIALS,
                "raw_rows": original.RAW_ROWS,
                "correctness_checks": original.CORRECTNESS_CHECKS,
                "bootstrap_draws": original.BOOTSTRAPS,
                "original_poison_controls": controls["corruption_checks"],
                "additional_version_poison_controls": extra,
                "poisoned_control_count": controls["corruption_checks"] + len(extra),
                "chart_count": len(SUFFIXES),
                "charts_deterministic": True,
                "final_speed": "NOT MEASURED",
            },
            sort_keys=True,
        )
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate six independently audited capacity-16 public-practice graphs."
    )
    parser.add_argument("--summary", type=Path, default=SUMMARY)
    parser.add_argument("--raw", type=Path, default=RAW)
    parser.add_argument("--integrity", type=Path, default=INTEGRITY)
    parser.add_argument("--prefix", type=Path, default=PREFIX)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run only synthetic version-isolation and deterministic graph controls",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.self_test:
        self_test()
        return

    check_renderers()
    prefix = args.prefix.resolve()
    require(prefix == PREFIX.resolve(), "refusing to overwrite a historical or unrelated graph")
    require(prefix.parent == EVIDENCE.resolve(), "refusing to write outside frozen public practice evidence")
    _result, charts = load_results(args.summary.resolve(), args.raw.resolve(), args.integrity.resolve())
    for suffix in SUFFIXES:
        path = prefix.parent / f"{prefix.name}-{suffix}.svg"
        path.write_text(charts[suffix], encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
