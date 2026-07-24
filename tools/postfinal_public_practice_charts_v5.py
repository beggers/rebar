#!/usr/bin/env python3
"""Render only source-bound, independently replayed V5 public-practice charts."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from tools import postfinal_public_practice_charts_v4 as previous


ROOT = Path(__file__).resolve().parent.parent
PREFIX = "postfinal-public-practice-v5"
PUBLIC_ROOT = ROOT / "performance" / "postfinal-public-v5"
EVIDENCE = PUBLIC_ROOT / "evidence"
MANIFEST = PUBLIC_ROOT / "manifest.json"
SUMMARY = EVIDENCE / f"{PREFIX}-summary.json"
INTEGRITY = EVIDENCE / f"{PREFIX}-integrity.json"
PUBLIC_RAW = EVIDENCE / f"{PREFIX}-raw.jsonl.gz"

PLAN_SCHEMA = "rebar-rust-balanced-calibration-plan-v7"
PLAN_POSTFINAL_SCHEMA = "rebar-postfinal-public-practice-plan-v5"
SUMMARY_SCHEMA = "rebar-rust-balanced-calibration-pilot-v7"
SUMMARY_POSTFINAL_SCHEMA = "rebar-postfinal-public-practice-report-v5"
INTEGRITY_SCHEMA = "rebar-postfinal-public-practice-integrity-v5"

V4_RENDERER_PATH = ROOT / "tools" / "postfinal_public_practice_charts_v4.py"
V4_RENDERER_SHA256 = (
    "85ea57956381d67b76517c04a7d99777c72f1ea9bbd52670637b52376d913e79"
)
V4_PREFIX = "postfinal-public-practice-v4"
V4_PUBLIC_ROOT = ROOT / "performance" / "postfinal-public-v4"
V4_EVIDENCE = V4_PUBLIC_ROOT / "evidence"
V4_MANIFEST = V4_PUBLIC_ROOT / "manifest.json"
V4_SUMMARY = V4_EVIDENCE / f"{V4_PREFIX}-summary.json"
V4_INTEGRITY = V4_EVIDENCE / f"{V4_PREFIX}-integrity.json"
V4_PUBLIC_RAW = V4_EVIDENCE / f"{V4_PREFIX}-raw.jsonl.gz"

require = previous.require
valid_sha256 = previous.valid_sha256


def require_v4_source_binding(source_path: Path, source_sha256: str) -> None:
    """Reject a substituted source path or any change to the committed V4."""

    require(
        source_path.resolve() == V4_RENDERER_PATH.resolve(),
        "the committed V4 public chart renderer source was substituted",
    )
    require(
        valid_sha256(source_sha256) and source_sha256 == V4_RENDERER_SHA256,
        "the committed V4 public chart renderer SHA-256 changed",
    )


def verify_v4_renderer_source() -> None:
    """Read exclusively the exact explicitly authorized inherited chart source."""

    source_path = Path(previous.__file__).resolve()
    require(
        source_path == V4_RENDERER_PATH.resolve(),
        "the imported V4 public chart renderer source was substituted",
    )
    source_sha256 = hashlib.sha256(source_path.read_bytes()).hexdigest()
    require_v4_source_binding(source_path, source_sha256)


@contextmanager
def v5_renderer() -> Iterator[None]:
    """Temporarily bind the verified immutable V4 renderer solely to V5."""

    previous.original.require_candidate_free()
    verify_v4_renderer_source()
    updates = {
        "__file__": str(Path(__file__).resolve()),
        "PUBLIC_ROOT": PUBLIC_ROOT,
        "EVIDENCE": EVIDENCE,
        "MANIFEST": MANIFEST,
        "PREFIX": PREFIX,
        "SUMMARY": SUMMARY,
        "INTEGRITY": INTEGRITY,
        "PUBLIC_RAW": PUBLIC_RAW,
        "PLAN_SCHEMA": PLAN_SCHEMA,
        "PLAN_POSTFINAL_SCHEMA": PLAN_POSTFINAL_SCHEMA,
        "SUMMARY_SCHEMA": SUMMARY_SCHEMA,
        "SUMMARY_POSTFINAL_SCHEMA": SUMMARY_POSTFINAL_SCHEMA,
        "INTEGRITY_SCHEMA": INTEGRITY_SCHEMA,
    }
    saved = {name: getattr(previous, name) for name in updates}
    try:
        for name, value in updates.items():
            setattr(previous, name, value)
        yield
    finally:
        for name, value in saved.items():
            setattr(previous, name, value)
        previous.original.require_candidate_free()


def require_v5_render_inputs(
    *,
    summary: Path,
    integrity: Path,
    manifest: Path,
    manifest_sha256: str,
    runner_sha256: str,
    output_dir: Path,
) -> None:
    """Require every exact V5 path and both externally supplied fingerprints."""

    for label, supplied, expected in (
        ("summary", summary, SUMMARY),
        ("integrity", integrity, INTEGRITY),
        ("manifest", manifest, MANIFEST),
        ("output evidence directory", output_dir, EVIDENCE),
    ):
        require(
            isinstance(supplied, Path)
            and supplied.resolve() == expected.resolve(),
            f"the public V5 {label} escaped its exact V5 path",
        )
    require(
        valid_sha256(manifest_sha256),
        "an externally supplied genuine V5 --manifest-sha256 is required",
    )
    require(
        valid_sha256(runner_sha256),
        "an externally supplied genuine V5 --runner-sha256 is required",
    )


def reject_synthetic(label: str, action) -> None:
    """Require one candidate-free, exclusively in-memory poison to fail."""

    try:
        action()
    except (KeyError, OSError, TypeError, ValueError):
        return
    raise ValueError(f"the public V5 synthetic controls accepted {label}")


def self_test() -> dict:
    """Retain all V4 poison controls and reject stale V4 evidence bindings."""

    previous.original.require_candidate_free()
    additional_rejections = 0
    with v5_renderer():
        inherited = previous.self_test()
        require(
            inherited.get("result") == "PASS",
            "the source-bound V4 public chart synthetic controls failed",
        )
        require(
            inherited.get("protocol_version") == PREFIX,
            "the source-bound V4 charts retained a stale public protocol",
        )
        require(
            inherited.get("charts") == len(previous.SUFFIXES) == 6,
            "the source-bound public renderer omitted a required graph",
        )
        require(
            inherited.get("synthetic_cases_per_module") == 8_192
            and inherited.get("synthetic_workload_categories") == 260,
            "the source-bound public denominator or category coverage changed",
        )
        require(
            inherited.get("stage05_independent_correctness_artifacts") == 12,
            "the source-bound public renderer omitted a stage-05 proof",
        )
        require(
            type(inherited.get("adversarial_rejections")) is int
            and inherited["adversarial_rejections"] >= 70,
            "an inherited V4 public chart poison control was removed",
        )

        fake_manifest_sha256 = hashlib.sha256(
            b"synthetic-only-v5-public-chart-manifest-pin"
        ).hexdigest()
        fake_runner_sha256 = hashlib.sha256(
            b"synthetic-only-v5-public-chart-runner-pin"
        ).hexdigest()
        quotas = previous.synthetic_quotas()
        with previous.v4_renderer(
            manifest_sha256=fake_manifest_sha256,
            runner_sha256=fake_runner_sha256,
            public_operations=quotas,
        ):
            manifest, summary, integrity = previous.synthetic_documents()
            manifest_sha256 = previous.base.canonical_sha256(manifest)
            summary_sha256 = previous.base.canonical_sha256(summary)
            selected = previous.check_v4_manifest(
                manifest,
                manifest_sha256=manifest_sha256,
            )
            results = previous.check_v4_summary(
                summary,
                manifest=manifest,
                selected_cases=selected,
                summary_sha256=summary_sha256,
                manifest_sha256=manifest_sha256,
            )
            previous.check_v4_integrity(
                integrity,
                results,
                manifest=manifest,
                integrity_sha256=previous.base.canonical_sha256(integrity),
            )
            require(
                tuple(previous.build_v4_charts(results)) == previous.SUFFIXES,
                "the exact six source-bound public V5 graphs changed",
            )

            document_poisons = (
                ("stale V4 plan protocol", "manifest", "protocol_version", V4_PREFIX),
                ("stale V4 exclusive slot", "manifest", "exclusive_slot", V4_PREFIX),
                (
                    "stale V4 plan schema",
                    "manifest",
                    "postfinal_schema",
                    "rebar-postfinal-public-practice-plan-v4",
                ),
                ("substituted V5 runner", "manifest", "runner_sha256", "0" * 64),
                ("stale V4 summary protocol", "summary", "protocol_version", V4_PREFIX),
                ("stale V4 summary slot", "summary", "exclusive_slot", V4_PREFIX),
                (
                    "stale V4 summary schema",
                    "summary",
                    "postfinal_schema",
                    "rebar-postfinal-public-practice-report-v4",
                ),
                ("stale V4 frozen manifest", "summary", "manifest_path", str(V4_MANIFEST)),
                ("stale V4 raw observations", "summary", "raw_path", str(V4_PUBLIC_RAW)),
                ("changed V5 summary runner", "summary", "runner_sha256", "0" * 64),
                ("changed V5 manifest pin", "summary", "manifest_sha256", "0" * 64),
                (
                    "stale V4 replay protocol",
                    "integrity",
                    "protocol_version",
                    V4_PREFIX,
                ),
                (
                    "stale V4 replay schema",
                    "integrity",
                    "schema",
                    "rebar-postfinal-public-practice-integrity-v4",
                ),
                ("changed V5 replay runner", "integrity", "runner_sha256", "0" * 64),
                ("changed V5 replay manifest", "integrity", "manifest_sha256", "0" * 64),
                ("changed V5 replay summary", "integrity", "summary_sha256", "0" * 64),
            )
            for label, kind, key, value in document_poisons:
                changed = copy.deepcopy(
                    {"manifest": manifest, "summary": summary, "integrity": integrity}[
                        kind
                    ]
                )
                changed[key] = value
                if kind == "manifest":
                    action = lambda changed=changed: previous.check_v4_manifest(
                        changed,
                        manifest_sha256=previous.base.canonical_sha256(changed),
                    )
                elif kind == "summary":
                    action = lambda changed=changed: previous.check_v4_summary(
                        changed,
                        manifest=manifest,
                        selected_cases=selected,
                        summary_sha256=previous.base.canonical_sha256(changed),
                        manifest_sha256=manifest_sha256,
                    )
                else:
                    action = lambda changed=changed: previous.check_v4_integrity(
                        changed,
                        results,
                        manifest=manifest,
                        integrity_sha256=previous.base.canonical_sha256(changed),
                    )
                reject_synthetic(label, action)
                additional_rejections += 1

        genuine_inputs = {
            "summary": SUMMARY,
            "integrity": INTEGRITY,
            "manifest": MANIFEST,
            "manifest_sha256": fake_manifest_sha256,
            "runner_sha256": fake_runner_sha256,
            "output_dir": EVIDENCE,
        }
        require_v5_render_inputs(**genuine_inputs)
        input_poisons = (
            ("stale V4 summary evidence", "summary", V4_SUMMARY),
            ("stale V4 integrity evidence", "integrity", V4_INTEGRITY),
            ("stale V4 manifest evidence", "manifest", V4_MANIFEST),
            ("stale V4 output evidence", "output_dir", V4_EVIDENCE),
            ("missing external V5 manifest fingerprint", "manifest_sha256", ""),
            ("missing external V5 runner fingerprint", "runner_sha256", ""),
        )
        for label, key, value in input_poisons:
            changed = {**genuine_inputs, key: value}
            reject_synthetic(
                label,
                lambda changed=changed: require_v5_render_inputs(**changed),
            )
            additional_rejections += 1

        source_poisons = (
            (
                "substituted inherited renderer path",
                ROOT / "tools" / "postfinal_public_practice_charts_v3.py",
                V4_RENDERER_SHA256,
            ),
            (
                "substituted inherited renderer fingerprint",
                V4_RENDERER_PATH,
                "0" * 64,
            ),
        )
        for label, source_path, source_sha256 in source_poisons:
            reject_synthetic(
                label,
                lambda source_path=source_path, source_sha256=source_sha256: (
                    require_v4_source_binding(source_path, source_sha256)
                ),
            )
            additional_rejections += 1

    previous.original.require_candidate_free()
    return {
        **inherited,
        "mode": (
            "candidate-free in-memory synthetic controls; "
            "only the immutable inherited V4 chart source is verified; "
            "no benchmark evidence read or outputs written"
        ),
        "protocol_version": PREFIX,
        "inherited_renderer_source_path": str(V4_RENDERER_PATH),
        "inherited_renderer_source_sha256": V4_RENDERER_SHA256,
        "inherited_adversarial_rejections": inherited["adversarial_rejections"],
        "v5_adversarial_rejections": additional_rejections,
        "adversarial_rejections": (
            inherited["adversarial_rejections"] + additional_rejections
        ),
        "manifest_binding": (
            "explicit --manifest-sha256 and --runner-sha256 required; never guessed"
        ),
    }


def render(
    *,
    summary: Path,
    integrity: Path,
    manifest: Path,
    manifest_sha256: str,
    runner_sha256: str,
    output_dir: Path,
) -> dict:
    """Render only explicit, fully replayed V5 evidence after both SHA pins."""

    previous.original.require_candidate_free()
    require_v5_render_inputs(
        summary=summary,
        integrity=integrity,
        manifest=manifest,
        manifest_sha256=manifest_sha256,
        runner_sha256=runner_sha256,
        output_dir=output_dir,
    )
    with v5_renderer():
        report = previous.render(
            summary=summary,
            integrity=integrity,
            manifest=manifest,
            manifest_sha256=manifest_sha256,
            runner_sha256=runner_sha256,
            output_dir=output_dir,
        )
    previous.original.require_candidate_free()
    require(
        report.get("result") == "PASS"
        and report.get("protocol_version") == PREFIX
        and report.get("manifest_sha256") == manifest_sha256
        and report.get("runner_sha256") == runner_sha256,
        "the measured public V5 graphs changed an externally pinned provenance",
    )
    require(
        isinstance(report.get("charts"), list)
        and len(report["charts"]) == len(previous.SUFFIXES) == 6,
        "the measured public V5 evidence omitted a required graph",
    )
    return {
        **report,
        "inherited_renderer_source_path": str(V4_RENDERER_PATH),
        "inherited_renderer_source_sha256": V4_RENDERER_SHA256,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Render six source-bound, independently replayed public V5 charts "
            "without importing candidates or accessing held-out benchmarks."
        )
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run exclusively candidate-free, synthetic V5 poison controls",
    )
    parser.add_argument("--summary", type=Path, help="exact V5 public summary")
    parser.add_argument(
        "--integrity", type=Path, help="exact independently replayed V5 integrity"
    )
    parser.add_argument("--manifest", type=Path, help="exact frozen V5 manifest")
    parser.add_argument(
        "--manifest-sha256",
        help="required independently supplied genuine V5 frozen manifest SHA-256",
    )
    parser.add_argument(
        "--runner-sha256",
        help="required independently supplied genuine V5 frozen runner SHA-256",
    )
    parser.add_argument(
        "--output-dir", type=Path, help="exact additive public-V5 evidence directory"
    )
    args = parser.parse_args(argv)
    values = (
        args.summary,
        args.integrity,
        args.manifest,
        args.manifest_sha256,
        args.runner_sha256,
        args.output_dir,
    )
    if args.self_test:
        if any(value is not None for value in values):
            parser.error(
                "synthetic controls cannot read benchmark evidence or write outputs"
            )
    elif any(value is None for value in values):
        parser.error(
            "rendering requires explicit --summary, --integrity, --manifest, "
            "--manifest-sha256, --runner-sha256, and --output-dir"
        )
    elif not valid_sha256(args.manifest_sha256):
        parser.error("--manifest-sha256 must be a lowercase 64-character SHA-256")
    elif not valid_sha256(args.runner_sha256):
        parser.error("--runner-sha256 must be a lowercase 64-character SHA-256")
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
                manifest_sha256=args.manifest_sha256,
                runner_sha256=args.runner_sha256,
                output_dir=args.output_dir,
            )
        )
    except (KeyError, OSError, TypeError, ValueError) as error:
        print(f"source-bound public V5 chart rendering rejected: {error}")
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
