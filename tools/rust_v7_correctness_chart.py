#!/usr/bin/env python3
"""Draw the frozen compatibility results without reading performance data."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "candidates" / "evidence"
SCHEMA = "rebar-v7-independent-edge-oracle-v1"
EXPECTED_SHA256 = "b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526"
ORACLE_SHA256 = "fe6a263a48f243ea02faaa78fc3bbd051233a2b2221967a5f76dd1bb79d242ca"
CHECKS = 223_198
CASES = (
    ("Python re (reference)", "re", "rust-v7-edge-oracle-stdlib-baseline.json.gz", "#64748b"),
    ("Corrected Rust", "candidates.rust_candidate", "rust-v7-edge-oracle-rust-corrected-v4.json.gz", "#059669"),
    ("Original Zig", "candidates.zig_candidate", "rust-v7-edge-oracle-zig-baseline.json.gz", "#7c3aed"),
    ("Original Rust", "candidates.rust_candidate", "rust-v7-edge-oracle-rust-baseline.json.gz", "#2563eb"),
    ("Original C", "candidates.vm_candidate", "rust-v7-edge-oracle-c-baseline.json.gz", "#d97706"),
    ("Original Python engine", "candidates.ast_candidate", "rust-v7-edge-oracle-python-baseline.json.gz", "#db2777"),
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def read_reports() -> list[dict]:
    reports = []
    for label, module, filename, color in CASES:
        path = EVIDENCE / filename
        with gzip.open(path, "rb") as source:
            report = json.load(source)
        reports.append({"label": label, "module": module, "color": color, "path": path, "report": report})
    return reports


def validated(reports: list[dict]) -> list[dict]:
    require(len(reports) == len(CASES), "a compatibility candidate was removed")
    rows = []
    for index, item in enumerate(reports):
        label, module, filename, color = CASES[index]
        require(item["label"] == label and item["module"] == module, "compatibility candidate order changed")
        require(item["color"] == color and item["path"] == EVIDENCE / filename, "compatibility provenance changed")
        report = item["report"]
        require(report.get("schema") == SCHEMA, f"invalid compatibility evidence: {label}")
        require(report.get("module") == module, f"incorrect candidate: {label}")
        require(report.get("script_sha256") == ORACLE_SHA256, f"compatibility oracle changed: {label}")
        require(report.get("correctness_checks") == CHECKS, f"compatibility denominator changed: {label}")
        require(report.get("expected_sha256") == EXPECTED_SHA256, f"Python reference answers changed: {label}")
        failed = report.get("failed")
        require(isinstance(failed, int) and not isinstance(failed, bool), f"invalid failure count: {label}")
        require(0 <= failed <= CHECKS, f"failure count outside frozen denominator: {label}")
        require(len(report.get("failures", [])) == failed, f"hidden compatibility failures: {label}")
        require(report.get("performance") == "NOT MEASURED", f"performance entered compatibility data: {label}")
        require(report.get("holdout") == "NOT ACCESSED", f"held-back data entered compatibility results: {label}")
        if failed == 0:
            require(report.get("actual_sha256") == EXPECTED_SHA256, f"incorrect passing answer digest: {label}")
        if label == "Corrected Rust":
            artifacts = report.get("candidate_artifacts")
            require(isinstance(artifacts, list) and len(artifacts) == 5, "corrected Rust artifact roles changed")
            require(
                {artifact.get("role") for artifact in artifacts}
                == {"public-python", "native-bridge", "native-engine", "native-source", "bridge-source"},
                "corrected Rust source or native artifact is missing",
            )
            for artifact in artifacts:
                path = (ROOT / artifact["path"]).resolve()
                require(path.is_file() and path.is_relative_to(ROOT), "corrected Rust artifact escaped the project")
                with path.open("rb") as source:
                    actual = hashlib.file_digest(source, "sha256").hexdigest()
                require(actual == artifact["sha256"], f"corrected Rust artifact changed: {artifact['role']}")
        rows.append({"label": label, "color": color, "passed": CHECKS - failed, "failed": failed})
    require(rows[0]["failed"] == 0, "Python reference has unexplained compatibility failures")
    require(rows[1]["failed"] == 0, "corrected Rust has unexplained compatibility failures")
    return rows


def chart(rows: list[dict]) -> str:
    width, height = 1220, 472
    left, bar_width, first, stride = 268, 555, 139, 52
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" '
        'aria-label="How closely do the from-scratch replacements match Python?">',
        '<rect width="100%" height="100%" fill="#fff"/>',
        '<style>text{font-family:system-ui,-apple-system,Segoe UI,sans-serif;fill:#172033}'
        '.title{font-size:24px;font-weight:700}.sub{font-size:13px;fill:#52627a}'
        '.label{font-size:15px;font-weight:650}.value{font-size:14px;font-weight:650}'
        '.note{font-size:12px;fill:#52627a}.tick{font-size:11px;fill:#64748b}'
        '.grid{stroke:#e2e8f0;stroke-width:1}</style>',
        '<text x="24" y="38" class="title">Which engines really behave like Python re?</text>',
        '<text x="24" y="61" class="sub">All 223,198 independently frozen checks. '
        'A full bar means zero differences; red shows every mismatch.</text>',
    ]
    for fraction in (0.0, 0.25, 0.50, 0.75, 1.0):
        x = left + round(bar_width * fraction, 2)
        lines.append(f'<line x1="{x}" y1="100" x2="{x}" y2="{first + stride * 5 + 22}" class="grid"/>')
        lines.append(f'<text x="{x}" y="94" class="tick" text-anchor="middle">{fraction:.0%}</text>')
    for index, row in enumerate(rows):
        y = first + index * stride
        passed_width = round(bar_width * row["passed"] / CHECKS, 2)
        failed_width = round(bar_width - passed_width, 2)
        if row["label"] == "Corrected Rust":
            lines.append(f'<rect x="12" y="{y-25}" width="1196" height="47" rx="8" fill="#ecfdf5"/>')
        lines.append(f'<text x="24" y="{y+5}" class="label">{escape(row["label"])}</text>')
        lines.append(f'<rect x="{left}" y="{y-10}" width="{bar_width}" height="19" rx="5" fill="#f1f5f9"/>')
        if passed_width:
            lines.append(f'<rect x="{left}" y="{y-10}" width="{passed_width}" height="19" rx="5" fill="{row["color"]}"/>')
        if failed_width:
            lines.append(
                f'<rect x="{left+passed_width}" y="{y-10}" width="{failed_width}" height="19" fill="#ef4444"/>'
            )
        detail = (
            f'{row["passed"]:,} / {CHECKS:,} correct · zero mismatches'
            if not row["failed"]
            else f'{row["passed"]:,} / {CHECKS:,} correct · {row["failed"]:,} mismatches'
        )
        lines.append(f'<text x="850" y="{y+5}" class="value">{escape(detail)}</text>')
    lines.append('<text x="24" y="450" class="note">Speed is measured separately; '
                 'the corrected Rust engine has not seen the final performance test.</text>')
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def self_test() -> dict:
    reports = read_reports()
    rows = validated(reports)
    rejected = 0
    for mutate in (
        lambda value: value.pop(),
        lambda value: value[1]["report"].update(correctness_checks=CHECKS - 1),
        lambda value: value[1]["report"].update(expected_sha256="0" * 64),
        lambda value: value[1]["report"].update(failed=1),
        lambda value: value[1]["report"].update(holdout="ACCESSED"),
        lambda value: value[1]["report"].update(candidate_artifacts=[]),
    ):
        corrupted = [
            {**item, "report": dict(item["report"])}
            for item in reports
        ]
        mutate(corrupted)
        try:
            validated(corrupted)
        except (KeyError, RuntimeError, TypeError, ValueError):
            rejected += 1
        else:
            raise RuntimeError("a corrupted compatibility result was accepted")
    svg = chart(rows)
    require(svg.startswith("<svg ") and svg.endswith("</svg>\n"), "invalid generated compatibility chart")
    return {
        "schema": "rebar-rust-v7-correctness-chart-self-test-v1",
        "candidates": len(rows),
        "checks_per_candidate": CHECKS,
        "rejected_corruptions": rejected,
        "holdout_accessed": False,
        "performance": "NOT MEASURED",
        "failed": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=EVIDENCE / "rust-v7-correctness.svg")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    require(tuple(sys.version_info[:3]) == (3, 14, 6), "requires pinned CPython 3.14.6")
    if args.self_test:
        print(json.dumps(self_test(), sort_keys=True))
        return
    destination = args.output.resolve()
    require(destination.is_relative_to(EVIDENCE), "correctness chart must remain in candidates/evidence")
    rows = validated(read_reports())
    content = chart(rows)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")
    print(json.dumps({
        "schema": "rebar-rust-v7-correctness-chart-v1",
        "candidates": len(rows),
        "checks_per_candidate": CHECKS,
        "holdout_accessed": False,
        "performance": "NOT MEASURED",
        "output": str(destination.relative_to(ROOT)),
        "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "failed": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
