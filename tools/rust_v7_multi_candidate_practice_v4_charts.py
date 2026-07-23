#!/usr/bin/env python3
"""Render only the independently verified Zig Stage 12 practice experiment."""

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
PREFIX = EVIDENCE / "three-qualified-engines-public-practice-v4"
SUMMARY = EVIDENCE / "three-qualified-engines-public-practice-v4-summary.json"
RAW = EVIDENCE / "three-qualified-engines-public-practice-v4-raw.jsonl.gz"
INTEGRITY = EVIDENCE / "three-qualified-engines-public-practice-v4-integrity.json"
V4_AUDITOR = ROOT / "tools" / "rust_v7_multi_candidate_practice_v4_audit.py"

V1_RENDERER_SHA256 = "5674fecff2b2555b725fd154cfdb1f7ee9ce7b951895c7a38f0f124f5304dddf"
V2_RENDERER_SHA256 = "3f81638918886de725500c23059b383e2773d493cbbfc5bb296f29721afd618d"
V3_RENDERER_SHA256 = "8e28587474b20fbd39af9a3df12bc5590b731864afac5b41a26310f55e6822be"
V1_SUMMARY_SHA256 = "20c33badfc08d98566c5476452370f042cd8ff544ecc5ed98f6d1111550328f0"
V2_SUMMARY_SHA256 = "db3cc7f4704df7b0a6b1283818d0dfdf96947d83d44752bf633a640a3e721cab"
V3_SUMMARY_SHA256 = "33ebdff8ecb061e3544b9cd4bc687040b8278aa037f3c993abe654daa665d155"
V1_INTEGRITY_SHA256 = "8739803b6cd020b8b4f663223435fd1e39ef5603e90195b2a268a9fa7fbc0340"
V2_INTEGRITY_SHA256 = "82ef917ca82ba124af6311f3bf10398a2a040286ed06430919bbdd26dd61e057"
V3_INTEGRITY_SHA256 = "aa1921230845a01aa03d607bd8609b3475dc659cacda5e6135d8b7064ed60c22"
V1_SLOT = "three-qualified-engines-public-practice-v1"
V2_SLOT = "three-qualified-engines-fused-vectorcall-v2"
V3_SLOT = "three-qualified-engines-findall-capacity-16-v3"
V4_SLOT = "three-qualified-engines-zig-span-256-v4"
V1_SCHEMA = "rebar-v7-multi-candidate-practice-integrity-v1"
V2_SCHEMA = "rebar-v7-multi-candidate-practice-integrity-v2"
V3_SCHEMA = "rebar-v7-multi-candidate-practice-integrity-v3"
V4_SCHEMA = "rebar-v7-multi-candidate-practice-integrity-v4"
V1_REGRESSIONS = 426
V2_REGRESSIONS = 401
V3_REGRESSIONS = 387

# Pin only the genuine, complete, one-shot four-way Zig Stage 12 result.
V4_SUMMARY_SHA256: str | None = "e23164b077b2bfa1abccaf8cce93a068bc7ea9b7ef444ef55905cc2fbd573e0c"
V4_COMPRESSED_RAW_SHA256: str | None = "628b23d7797312fce35436a4709bb278995f1513b381c9cc302ee6caf5bda6fe"
V4_RAW_SHA256: str | None = "1639451c8167062e0b7d847c969c6a1c4d613e784d86c7ca09044e9786085da0"
V4_REGRESSIONS: int | None = 402
V4_ZIG_EDGE_REPORT_SHA256: str | None = "3abc55fe1722defb478f32a571c7eb0d00fa9bd93b7ac6ddc7a9227bdde3b2b8"

V4_AUDIT_SHA256 = "d68a14b5a2c4f181871afbc23c2d6e90150e7eb4752e9d636f035a8ad9cdf796"
V4_ZIG_CAMPAIGN_SHA256 = "f89fe9081421d28a291feab1b664c21a7c372762a548569856c6572e4a23eba6"
V3_RUST_CAMPAIGN_SHA256 = "89793a597ac74551742d05bdf1c5af61f1121d89466e00ac2902c8942aaeef4d"
V3_INITIAL_AUDIT_FAILURE_SHA256 = "ccaf3813b29badcf80c552dc0d850f83a2ca122cc3cc3057576dd519aed4f088"
V4_ZIG_BRIDGE_SOURCE_SHA256 = "cb14210092d9ec92a2ac8c458d7b713342c8662bcf3318f954e0c520bc7b1589"
V4_ZIG_NATIVE_BRIDGE_SHA256 = "4d1eb307eabc8b254ac0724aeb8ba106105d9879b7d46054b2355621fb330a92"
REFERENCE_MODULES = (original.BASELINE, original.RUST, original.C_ENGINE)
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
        isinstance(V4_REGRESSIONS, int)
        and not isinstance(V4_REGRESSIONS, bool)
        and 0 <= V4_REGRESSIONS <= 624 * 3,
        "the actual Zig Stage 12 slowdown count is NOT MEASURED or invalid",
    )
    return V4_REGRESSIONS


def check_renderers() -> None:
    frozen = (
        ("rust_v7_multi_candidate_practice_charts.py", V1_RENDERER_SHA256),
        ("rust_v7_multi_candidate_practice_v2_charts.py", V2_RENDERER_SHA256),
        ("rust_v7_multi_candidate_practice_v3_charts.py", V3_RENDERER_SHA256),
    )
    for name, digest in frozen:
        path = ROOT / "tools" / name
        require(original.sha256_file(path) == digest, f"the immutable historical renderer changed: {name}")
    require(
        Path(original.__file__).resolve()
        == (ROOT / "tools" / "rust_v7_multi_candidate_practice_charts.py").resolve(),
        "the original pure graph renderer was substituted",
    )
    require(original.SLOT == V1_SLOT, "original practice-slot controls were changed")
    require(original.INTEGRITY_SCHEMA == V1_SCHEMA, "original integrity-schema controls were changed")
    require(original.EXPECTED_REGRESSIONS == V1_REGRESSIONS, "original slowdown controls were changed")
    require(original.CHART_SUFFIXES == SUFFIXES, "a separately required historical graph is missing")
    require(original.CASES == 624, "the frozen case denominator changed")
    require(original.TRIALS == 7, "the frozen paired-trial denominator changed")
    require(original.BOOTSTRAPS == 499, "the confidence protocol changed")
    require(original.RAW_ROWS == 17_472, "the raw timing denominator changed")
    require(original.CORRECTNESS_CHECKS == 52_416, "a correctness gate was omitted")
    require(
        original.MODULES == (
            "re",
            "candidates.rust_candidate",
            "candidates.vm_candidate",
            "candidates.zig_candidate",
        ),
        "the baseline or an independently implemented candidate changed",
    )
    require(len(original.API_COUNTS) == 12, "a public operation group was omitted")


@contextlib.contextmanager
def v4_renderer(*, synthetic: bool = False):
    """Use exact v4-only bounds; restore all immutable v1 renderer controls."""

    check_renderers()
    saved = (original.SLOT, original.INTEGRITY_SCHEMA, original.EXPECTED_REGRESSIONS)
    original.SLOT = V4_SLOT
    original.INTEGRITY_SCHEMA = V4_SCHEMA
    original.EXPECTED_REGRESSIONS = V1_REGRESSIONS if synthetic else measured_regressions()
    try:
        yield
    finally:
        original.SLOT, original.INTEGRITY_SCHEMA, original.EXPECTED_REGRESSIONS = saved
        check_renderers()


def check_history() -> tuple[dict, dict, dict, dict, dict, dict]:
    histories = (
        (
            original.DEFAULT_SUMMARY,
            original.DEFAULT_INTEGRITY,
            V1_SUMMARY_SHA256,
            V1_INTEGRITY_SHA256,
            V1_SLOT,
            V1_SCHEMA,
            V1_REGRESSIONS,
        ),
        (
            EVIDENCE / "three-qualified-engines-public-practice-v2-summary.json",
            EVIDENCE / "three-qualified-engines-public-practice-v2-integrity.json",
            V2_SUMMARY_SHA256,
            V2_INTEGRITY_SHA256,
            V2_SLOT,
            V2_SCHEMA,
            V2_REGRESSIONS,
        ),
        (
            EVIDENCE / "three-qualified-engines-public-practice-v3-summary.json",
            EVIDENCE / "three-qualified-engines-public-practice-v3-integrity.json",
            V3_SUMMARY_SHA256,
            V3_INTEGRITY_SHA256,
            V3_SLOT,
            V3_SCHEMA,
            V3_REGRESSIONS,
        ),
    )
    documents: list[dict] = []
    for summary_path, integrity_path, summary_hash, integrity_hash, slot, schema, regressions in histories:
        require(original.sha256_file(summary_path) == summary_hash, f"a historical practice summary changed: {slot}")
        require(original.sha256_file(integrity_path) == integrity_hash, f"a historical practice verification changed: {slot}")
        summary = original.read_json(summary_path)
        integrity = original.read_json(integrity_path)
        require(summary.get("exclusive_slot") == slot, f"a historical practice run was relabeled: {slot}")
        require(integrity.get("schema") == schema, f"a historical practice verifier was relabeled: {slot}")
        require(integrity.get("result") == "PASS", f"a historical practice verifier failed: {slot}")
        require(integrity.get("summary_sha256") == summary_hash, f"historical results are not source bound: {slot}")
        require(integrity.get("strict_regressions") == regressions, f"historical substantial slowdowns changed: {slot}")
        documents.extend((summary, integrity))
    require(documents[3].get("historical_v1_integrity_sha256") == V1_INTEGRITY_SHA256, "historical v1-to-v2 continuity changed")
    require(documents[5].get("historical_v1_integrity_sha256") == V1_INTEGRITY_SHA256, "historical v1-to-v3 continuity changed")
    require(documents[5].get("historical_v2_integrity_sha256") == V2_INTEGRITY_SHA256, "historical v2-to-v3 continuity changed")
    return tuple(documents)  # type: ignore[return-value]


def check_v4_metadata(summary: dict, integrity: dict) -> None:
    summary_hash = measured_digest(V4_SUMMARY_SHA256, "v4 one-shot practice summary")
    compressed_hash = measured_digest(V4_COMPRESSED_RAW_SHA256, "compressed v4 paired observations")
    raw_hash = measured_digest(V4_RAW_SHA256, "uncompressed v4 paired observations")
    expected = {
        "schema": V4_SCHEMA,
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
        "summary_sha256": summary_hash,
        "compressed_raw_sha256": compressed_hash,
        "raw_sha256": raw_hash,
        "from_scratch_audit_sha256": V4_AUDIT_SHA256,
        "historical_v1_integrity_sha256": V1_INTEGRITY_SHA256,
        "historical_v2_integrity_sha256": V2_INTEGRITY_SHA256,
        "historical_v3_integrity_sha256": V3_INTEGRITY_SHA256,
        "full_correctness_campaign_sha256": V4_ZIG_CAMPAIGN_SHA256,
        "rust_full_correctness_campaign_sha256": V3_RUST_CAMPAIGN_SHA256,
        "initial_audit_failure_sha256": V3_INITIAL_AUDIT_FAILURE_SHA256,
        "unchanged_reference_candidates": list(REFERENCE_MODULES),
        "rust_optimization_verified": True,
        "capacity16_optimization_verified": True,
        "zig_optimization_verified": True,
    }
    for key, value in expected.items():
        require(integrity.get(key) == value, f"the independent Zig Stage 12 audit does not prove {key}")
    require(summary.get("exclusive_slot") == V4_SLOT, "the actual Zig Stage 12 measurement slot changed")
    require(summary.get("cohort") == "calibration", "a non-public case entered practice")
    require(summary.get("holdout_accessed") is False, "unseen final cases entered practice")
    require(summary.get("failed") == 0, "a public-practice correctness gate failed")
    require(summary.get("compressed_raw_sha256") == compressed_hash, "actual compressed v4 results changed")
    require(summary.get("raw_sha256") == raw_hash, "actual uncompressed v4 results changed")
    require(original.sha256_file(V4_AUDITOR) == integrity.get("source_sha256"), "the independent Zig Stage 12 results auditor was substituted")


def check_unchanged_references(summary: dict, integrity: dict, v3_summary: dict, v3_integrity: dict) -> None:
    old = v3_summary.get("candidate_binary_sha256_before")
    current = summary.get("candidate_binary_sha256_before")
    require(isinstance(old, dict) and isinstance(current, dict), "historical or current candidate identities are missing")
    require(summary.get("candidate_binary_sha256_after") == current, "a candidate changed during v4 practice")
    for module in REFERENCE_MODULES:
        role_prefix = f"{module}:"
        historical = {role: digest for role, digest in old.items() if role.startswith(role_prefix)}
        measured = {role: digest for role, digest in current.items() if role.startswith(role_prefix)}
        require(bool(historical) and measured == historical, f"a fixed Python, Rust, or C reference changed: {module}")

    old_sources = v3_integrity.get("qualified_source_fingerprints")
    new_sources = integrity.get("qualified_source_fingerprints")
    require(isinstance(old_sources, dict) and isinstance(new_sources, dict), "qualified source continuity is missing")
    zig_bridge = "candidates/zig/py_bridge.c"
    require(new_sources.get(zig_bridge) == V4_ZIG_BRIDGE_SOURCE_SHA256, "the passing Stage 12 Zig bridge source was substituted")
    require(old_sources.get(zig_bridge) != new_sources[zig_bridge], "practice did not measure the new Zig bridge")
    for path, digest in old_sources.items():
        if path != zig_bridge:
            require(new_sources.get(path) == digest, f"an unrelated Python, Rust, C, or Zig-engine source changed: {path}")

    zig_bridge_role = f"{original.ZIG}:native-bridge"
    require(current.get(zig_bridge_role) == V4_ZIG_NATIVE_BRIDGE_SHA256, "the passing Zig native bridge was substituted")
    require(old.get(zig_bridge_role) != current[zig_bridge_role], "practice reused the historical Zig bridge")
    for role, digest in old.items():
        if role.startswith(f"{original.ZIG}:") and role != zig_bridge_role:
            require(current.get(role) == digest, f"an unrelated Zig artifact changed: {role}")


def check_stage12_edge(summary: dict) -> None:
    report_hash = measured_digest(V4_ZIG_EDGE_REPORT_SHA256, "passing Zig Stage 12 correctness report")
    proofs = summary.get("verified_edge_oracles")
    require(isinstance(proofs, list), "independent current candidate correctness proofs are missing")
    matches = [proof for proof in proofs if isinstance(proof, dict) and proof.get("module") == original.ZIG]
    require(len(matches) == 1, "the current Zig Stage 12 correctness proof is missing or duplicated")
    require(matches[0].get("report_sha256") == report_hash, "practice did not measure the genuine passing Stage 12 Zig engine")


def load_results(summary_path: Path, raw_path: Path, integrity_path: Path):
    require(summary_path.resolve() == SUMMARY.resolve(), "refusing a substituted Zig Stage 12 summary")
    require(raw_path.resolve() == RAW.resolve(), "refusing substituted Zig Stage 12 paired observations")
    require(integrity_path.resolve() == INTEGRITY.resolve(), "refusing substituted Zig Stage 12 replay evidence")
    require(
        original.sha256_file(summary_path) == measured_digest(V4_SUMMARY_SHA256, "actual v4 summary fingerprint"),
        "the actual one-shot Zig Stage 12 summary changed",
    )
    require(
        original.sha256_file(raw_path) == measured_digest(V4_COMPRESSED_RAW_SHA256, "actual compressed v4 fingerprint"),
        "the actual one-shot Zig Stage 12 observations changed",
    )
    _v1_summary, _v1_integrity, _v2_summary, _v2_integrity, v3_summary, v3_integrity = check_history()
    summary = original.read_json(summary_path)
    integrity = original.read_json(integrity_path)
    check_v4_metadata(summary, integrity)
    check_unchanged_references(summary, integrity, v3_summary, v3_integrity)
    check_stage12_edge(summary)
    with v4_renderer():
        result = original.load_results(summary_path, raw_path, integrity_path)
        charts = original.build_charts(result)
    require(tuple(charts) == SUFFIXES, "a separately required Zig Stage 12 graph was dropped")
    for suffix, content in charts.items():
        require("PRACTICE ONLY" in content, f"the {suffix} graph omitted its public-practice limitation")
        require("final speed NOT MEASURED" in content, f"the {suffix} graph invented final performance")
    return result, charts


def expect_rejection(action, label: str) -> None:
    try:
        action()
    except (ValueError, TypeError, KeyError, OverflowError):
        return
    raise ValueError(f"synthetic Zig Stage 12 evidence was accepted: {label}")


def self_test() -> None:
    check_renderers()
    output = io.StringIO()
    with v4_renderer(synthetic=True):
        with contextlib.redirect_stdout(output):
            original.self_test()
        summary, integrity, _raw_rows, summary_hash, compressed_hash, raw_hash = original.synthetic_documents()
        base_controls = json.loads(output.getvalue())
        require(isinstance(base_controls, dict) and base_controls.get("result") == "PASS", "immutable synthetic rendering controls failed")
        require(base_controls.get("synthetic_only") is True, "synthetic controls inspected actual practice results")
        require(base_controls.get("holdout_accessed") is False, "synthetic controls accessed the unseen benchmark")
        require(base_controls.get("timing_performed") is False, "synthetic controls performed timing")
        require(base_controls.get("corruption_checks", 0) >= 33, "original poisoned-evidence controls were weakened")
        require(base_controls.get("chart_count") == len(SUFFIXES), "synthetic verification omitted a graph")

        extra: list[str] = []

        def reject_summary(key: str, value: object, label: str) -> None:
            changed = copy.deepcopy(summary)
            changed[key] = value
            expect_rejection(lambda: original.check_summary(changed), label)
            extra.append(label)

        def reject_integrity(key: str, value: object, label: str) -> None:
            changed = copy.deepcopy(integrity)
            changed[key] = value
            expect_rejection(
                lambda: original.check_integrity(
                    summary,
                    changed,
                    summary_digest=summary_hash,
                    compressed_digest=compressed_hash,
                    raw_digest=raw_hash,
                ),
                label,
            )
            extra.append(label)

        reject_summary("exclusive_slot", V1_SLOT, "historical-v1-slot-substitution")
        reject_summary("exclusive_slot", V2_SLOT, "historical-v2-slot-substitution")
        reject_summary("exclusive_slot", V3_SLOT, "historical-v3-slot-substitution")
        reject_summary("exclusive_slot", "three-qualified-engines-public-practice-v4", "invented-v4-slot-substitution")
        reject_summary("holdout_accessed", True, "unseen-final-case-access")
        reject_summary("paired_raw_rows", original.RAW_ROWS - 1, "missing-paired-practice-measurement")
        reject_summary("correctness_checks", original.CORRECTNESS_CHECKS - 1, "missing-practice-correctness-gate")
        reject_summary("modules", list(reversed(original.MODULES)), "substituted-baseline-or-candidate-order")
        reject_summary("bootstrap_samples", original.BOOTSTRAPS - 1, "weakened-confidence-protocol")
        reject_integrity("schema", V1_SCHEMA, "historical-v1-replay-substitution")
        reject_integrity("schema", V2_SCHEMA, "historical-v2-replay-substitution")
        reject_integrity("schema", V3_SCHEMA, "historical-v3-replay-substitution")
        reject_integrity("summary_sha256", "0" * 64, "substituted-zig-stage12-summary")
        reject_integrity("compressed_raw_sha256", "0" * 64, "substituted-compressed-paired-observations")
        reject_integrity("raw_sha256", "0" * 64, "substituted-uncompressed-paired-observations")
        reject_integrity("strict_regressions", V1_REGRESSIONS - 1, "concealed-synthetic-substantial-slowdown")
        reject_integrity("timing_performed", True, "independent-replay-performs-timing")

        data = original.PracticeResults(
            summary,
            integrity,
            tuple(
                sorted(
                    original.check_summary(summary),
                    key=lambda row: (-row.ranking["geomean_speedup"], original.DISPLAY[row.module]),
                )
            ),
        )
        charts = original.build_charts(data)
        require(tuple(charts) == SUFFIXES, "synthetic Zig Stage 12 omitted a graph")
        require("shared process" in charts["memory"], "synthetic graphs concealed shared-process memory limitations")
        require("does not measure native" in charts["memory"], "synthetic graphs invented native memory results")
        require(original.build_charts(data) == charts, "Zig Stage 12 graph generation is not deterministic")

    check_renderers()
    poisoned_count = base_controls["corruption_checks"] + len(extra)
    require(poisoned_count >= 48, "fewer than 48 synthetic evidence-poisoning controls were retained")
    print(
        json.dumps(
            {
                "schema": f"{V4_SCHEMA}-charts-self-test",
                "result": "PASS",
                "synthetic_only": True,
                "holdout_accessed": False,
                "timing_performed": False,
                "historical_v1_renderer_sha256": V1_RENDERER_SHA256,
                "historical_v2_renderer_sha256": V2_RENDERER_SHA256,
                "historical_v3_renderer_sha256": V3_RENDERER_SHA256,
                "historical_renderers_restored": True,
                "cases_per_candidate": original.CASES,
                "candidate_case_count": original.CASES * len(original.CANDIDATES),
                "trials_per_module_case": original.TRIALS,
                "raw_rows": original.RAW_ROWS,
                "correctness_checks": original.CORRECTNESS_CHECKS,
                "bootstrap_draws": original.BOOTSTRAPS,
                "original_poison_controls": base_controls["corruption_checks"],
                "additional_version_poison_controls": extra,
                "poisoned_control_count": poisoned_count,
                "chart_count": len(SUFFIXES),
                "charts_deterministic": True,
                "final_speed": "NOT MEASURED",
            },
            sort_keys=True,
        )
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate exactly six independently audited Zig Stage 12 public-practice graphs."
    )
    parser.add_argument("--summary", type=Path, default=SUMMARY)
    parser.add_argument("--raw", type=Path, default=RAW)
    parser.add_argument("--integrity", type=Path, default=INTEGRITY)
    parser.add_argument("--prefix", type=Path, default=PREFIX)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run synthetic-only historical-isolation and deterministic graph controls",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.self_test:
        self_test()
        return

    check_renderers()
    prefix = args.prefix.resolve()
    require(prefix == PREFIX.resolve(), "refusing to overwrite historical or unrelated practice graphs")
    require(prefix.parent == EVIDENCE.resolve(), "refusing to write outside public practice evidence")
    _data, charts = load_results(args.summary.resolve(), args.raw.resolve(), args.integrity.resolve())
    for suffix in SUFFIXES:
        destination = prefix.parent / f"{prefix.name}-{suffix}.svg"
        destination.write_text(charts[suffix], encoding="utf-8")
        print(f"wrote {destination.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
