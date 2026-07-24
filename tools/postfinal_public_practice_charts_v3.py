#!/usr/bin/env python3
"""Render only exact, independently replayed stage-03 public practice."""

from __future__ import annotations

import argparse
import json
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from tools import postfinal_public_practice_charts_v2 as original


ROOT = Path(__file__).resolve().parent.parent
PUBLIC_ROOT = ROOT / "performance" / "postfinal-public-v3"
EVIDENCE = PUBLIC_ROOT / "evidence"
MANIFEST = PUBLIC_ROOT / "manifest.json"
MANIFEST_SHA256 = (
    "5f49f255271b8f71786e7fa67a61827b53c1330e1ad7afe29c8750991df4b90f"
)
RUNNER_SHA256 = (
    "aa2b22de82894dc41622378d1bd782636358fa360454be37f3b8fedbc6e4989a"
)
PREFIX = "postfinal-public-practice-v3"
SUMMARY = EVIDENCE / f"{PREFIX}-summary.json"
INTEGRITY = EVIDENCE / f"{PREFIX}-integrity.json"
PUBLIC_RAW = EVIDENCE / f"{PREFIX}-raw.jsonl.gz"
PLAN_SCHEMA = "rebar-rust-balanced-calibration-plan-v7"
PLAN_POSTFINAL_SCHEMA = "rebar-postfinal-public-practice-plan-v3"
SUMMARY_SCHEMA = "rebar-rust-balanced-calibration-pilot-v7"
SUMMARY_POSTFINAL_SCHEMA = "rebar-postfinal-public-practice-report-v3"
INTEGRITY_SCHEMA = "rebar-postfinal-public-practice-integrity-v3"

MODULES = (
    "re",
    "candidates.rust_candidate",
    "candidates.vm_candidate",
    "candidates.zig_candidate",
)
CANDIDATES = MODULES[1:]
EDGE_PROOF_PATHS = {
    "candidates.rust_candidate": str(
        ROOT
        / "candidates"
        / "evidence"
        / "rust-v7-edge-oracle-rust-post-final-stage-03-slot-batch.json.gz"
    ),
    "candidates.vm_candidate": str(
        ROOT
        / "candidates"
        / "evidence"
        / "rust-v8-edge-oracle-vm-deep-stage-21-singleton-split-memchr.json.gz"
    ),
    "candidates.zig_candidate": str(
        ROOT
        / "candidates"
        / "evidence"
        / "rust-v8-edge-oracle-zig-deep-stage-13.json.gz"
    ),
}
SUFFIXES = (
    "overall",
    "outcomes",
    "api",
    "regressions",
    "memory",
    "rankings",
)

require = original.require


@contextmanager
def v3_renderer() -> Iterator[None]:
    """Reuse exact committed graphs and checks without retaining mutations."""

    original.require_candidate_free()
    require(original.MODULES == MODULES, "the frozen public module order changed")
    require(original.CANDIDATES == CANDIDATES, "the native candidate order changed")
    require(original.SUFFIXES == SUFFIXES, "a required public chart was omitted")
    require(
        sum(original.API_COUNTS.values()) == original.CASES == 4_096,
        "the selected stage-03 public API quotas changed",
    )
    require(
        sum(original.BOUNDED_API_CAPACITIES.values())
        == original.ELIGIBLE_PUBLIC_CASES
        == 9_731,
        "the eligible public API capacities changed",
    )
    updates = {
        "PUBLIC_ROOT": PUBLIC_ROOT,
        "EVIDENCE": EVIDENCE,
        "MANIFEST": MANIFEST,
        "MANIFEST_SHA256": MANIFEST_SHA256,
        "RUNNER_SHA256": RUNNER_SHA256,
        "PREFIX": PREFIX,
        "SUMMARY": SUMMARY,
        "INTEGRITY": INTEGRITY,
        "PUBLIC_RAW": PUBLIC_RAW,
        "PLAN_SCHEMA": PLAN_SCHEMA,
        "PLAN_POSTFINAL_SCHEMA": PLAN_POSTFINAL_SCHEMA,
        "SUMMARY_SCHEMA": SUMMARY_SCHEMA,
        "SUMMARY_POSTFINAL_SCHEMA": SUMMARY_POSTFINAL_SCHEMA,
        "INTEGRITY_SCHEMA": INTEGRITY_SCHEMA,
        "EDGE_PROOF_PATHS": EDGE_PROOF_PATHS,
    }
    saved = {name: getattr(original, name) for name in updates}
    try:
        for name, value in updates.items():
            setattr(original, name, value)
        with original.v2_renderer():
            yield
    finally:
        for name, value in saved.items():
            setattr(original, name, value)


def self_test() -> dict:
    """Use only inherited in-memory controls; never read benchmark evidence."""

    original.require_candidate_free()
    with v3_renderer():
        report = original.self_test()
        require(report.get("result") == "PASS", "stage-03 synthetic controls failed")
        require(
            report.get("protocol_version") == PREFIX,
            "synthetic controls used an earlier public-practice version",
        )
        require(
            report.get("frozen_public_manifest_sha256") == MANIFEST_SHA256,
            "synthetic controls substituted the frozen stage-03 manifest",
        )
        require(
            report.get("frozen_public_runner_sha256") == RUNNER_SHA256,
            "synthetic controls substituted the frozen stage-03 runner",
        )
        require(
            report.get("synthetic_cases_per_module") == 4_096,
            "synthetic controls changed the stage-03 case denominator",
        )
        require(
            report.get("synthetic_workload_categories") == 260,
            "synthetic controls concealed a public workload category",
        )
        require(
            report.get("charts") == len(SUFFIXES),
            "synthetic controls omitted an independently generated chart",
        )
        require(
            type(report.get("adversarial_rejections")) is int
            and report["adversarial_rejections"] >= 30,
            "a stage-03 synthetic adversarial control was removed",
        )
        slowdowns = report.get("synthetic_individually_visible_slowdowns")
        require(
            type(slowdowns) is int and slowdowns >= 0,
            "a synthetic public slowdown was concealed",
        )
    original.require_candidate_free()
    return {
        "result": "PASS",
        "mode": (
            "candidate-free in-memory synthetic only; "
            "no evidence files read or written"
        ),
        "protocol_version": PREFIX,
        "charts": len(SUFFIXES),
        "synthetic_cases_per_module": 4_096,
        "synthetic_workload_categories": 260,
        "synthetic_individually_visible_slowdowns": slowdowns,
        "adversarial_rejections": report["adversarial_rejections"],
        "frozen_public_manifest_sha256": MANIFEST_SHA256,
        "frozen_public_runner_sha256": RUNNER_SHA256,
        "genuine_stage_03_public_results": "NOT MEASURED",
        "historical_final_benchmark": "FAILED; no final winner",
    }


def render(
    *,
    summary: Path,
    integrity: Path,
    manifest: Path,
    output_dir: Path,
) -> dict:
    original.require_candidate_free()
    require(
        output_dir.resolve() == EVIDENCE.resolve(),
        "stage-03 charts must use the exact additive public-v3 evidence directory",
    )
    with v3_renderer():
        report = original.render(
            summary=summary,
            integrity=integrity,
            manifest=manifest,
            output_dir=output_dir,
        )
        require(report.get("result") == "PASS", "independent stage-03 replay failed")
        require(
            report.get("protocol_version") == PREFIX,
            "the chart renderer substituted the stage-03 protocol",
        )
        require(
            report.get("manifest_sha256") == MANIFEST_SHA256,
            "the chart renderer substituted the frozen stage-03 manifest",
        )
        require(
            report.get("runner_sha256") == RUNNER_SHA256,
            "the chart renderer substituted the frozen stage-03 runner",
        )
        charts = report.get("charts")
        require(
            isinstance(charts, list) and len(charts) == len(SUFFIXES),
            "a required stage-03 public chart is missing",
        )
        for item, suffix in zip(charts, SUFFIXES, strict=True):
            require(isinstance(item, dict), "invalid stage-03 public chart evidence")
            require(item.get("chart") == suffix, "a stage-03 chart was reordered")
            expected = EVIDENCE / f"{PREFIX}-{suffix}.svg"
            require(
                item.get("path") == str(expected),
                "a stage-03 chart escaped the exact public evidence path",
            )
            require(
                original.valid_sha256(item.get("sha256")),
                "a stage-03 public chart has no valid fingerprint",
            )
        original.require_candidate_free()
    original.require_candidate_free()
    report["measurement"] = (
        "independently replayed stage-03 public development only"
    )
    return report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Render six frozen, independently replayed stage-03 public "
            "practice charts without importing production candidates."
        )
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run only inherited candidate-free, in-memory synthetic controls",
    )
    parser.add_argument("--summary", type=Path, help="exact stage-03 public summary")
    parser.add_argument(
        "--integrity",
        type=Path,
        help="exact stage-03 independently replayed public evidence",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        help="exact SHA-256-pinned stage-03 public plan",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="exact additive public-v3 evidence directory",
    )
    args = parser.parse_args(argv)
    inputs = (args.summary, args.integrity, args.manifest, args.output_dir)
    if args.self_test:
        if any(value is not None for value in inputs):
            parser.error(
                "synthetic controls cannot access public evidence or chart outputs"
            )
    elif any(value is None for value in inputs):
        parser.error(
            "rendering requires explicit --summary, --integrity, "
            "--manifest, and --output-dir"
        )
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = (
            self_test()
            if args.self_test
            else render(
                summary=args.summary,
                integrity=args.integrity,
                manifest=args.manifest,
                output_dir=args.output_dir,
            )
        )
    except (KeyError, OSError, TypeError, ValueError) as error:
        print(f"stage-03 public chart rendering rejected: {error}")
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
