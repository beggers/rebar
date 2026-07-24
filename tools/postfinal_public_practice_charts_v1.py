#!/usr/bin/env python3
"""Render only the frozen expanded public practice; never open a final test."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import statistics
from collections import Counter
from dataclasses import dataclass
from html import escape
from pathlib import Path
from xml.etree import ElementTree

from tools import render_postfinal_rust_split as previous


ROOT = Path(__file__).resolve().parent.parent
PUBLIC_ROOT = ROOT / "performance" / "postfinal-public-v1"
EVIDENCE = PUBLIC_ROOT / "evidence"
MANIFEST = PUBLIC_ROOT / "manifest.json"
MANIFEST_SHA256 = "4b541eaa1602855aeb67655c8732635d4c951a61ca2fae37f395a1b080a78d1e"
PREFIX = "postfinal-public-practice-v1"
SUMMARY = EVIDENCE / f"{PREFIX}-summary.json"
INTEGRITY = EVIDENCE / f"{PREFIX}-integrity.json"
PLAN_SCHEMA = "rebar-rust-balanced-calibration-plan-v7"
PLAN_POSTFINAL_SCHEMA = "rebar-postfinal-public-practice-plan-v1"
SUMMARY_SCHEMA = "rebar-rust-balanced-calibration-pilot-v7"
SUMMARY_POSTFINAL_SCHEMA = "rebar-postfinal-public-practice-report-v1"
INTEGRITY_SCHEMA = "rebar-postfinal-public-practice-integrity-v1"
CASES = 4096
TRIALS = 13
BOOTSTRAPS = 2000
CATEGORY_COUNT = 260
RAW_ROWS = 212_992
CORRECTNESS_GATES = 638_976
CONFIDENCE_INTERVALS = 12_291
MODULES = previous.MODULES
CANDIDATES = previous.CANDIDATES
BASELINE = previous.BASELINE
DISPLAY = previous.DISPLAY
COLOURS = previous.COLOURS
API_LABELS = previous.API_LABELS
API_COUNTS = {
    "compile": 210,
    "escape": 161,
    "findall": 414,
    "finditer": 414,
    "fullmatch": 358,
    "match": 229,
    "match-surface": 241,
    "scanner": 413,
    "search": 414,
    "split": 414,
    "sub": 414,
    "subn": 414,
}
SUFFIXES = ("overall", "outcomes", "api", "regressions", "memory", "rankings")
BANNER = previous.BANNER
FINAL_STATUS = previous.FINAL_STATUS
SVG_NAMESPACE = previous.SVG_NAMESPACE


@dataclass(frozen=True)
class Candidate:
    module: str
    ranking: dict
    rows: tuple[dict, ...]


@dataclass(frozen=True)
class Results:
    summary: dict
    candidates: tuple[Candidate, ...]
    summary_sha256: str
    manifest_sha256: str


require = previous.require
finite = previous.finite
same_float = previous.same_float
valid_sha256 = previous.valid_sha256
fmt = previous.fmt


def geometric(rows: tuple[dict, ...]) -> float:
    require(bool(rows), "a public workload group is NOT MEASURED")
    return math.exp(math.fsum(math.log(finite(row.get("speedup"), "public speed")) for row in rows) / len(rows))


def canonical_sha256(document: dict) -> str:
    return hashlib.sha256(
        json.dumps(document, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def check_manifest(document: object, *, manifest_sha256: str) -> None:
    require(isinstance(document, dict), "the frozen public manifest is not a JSON object")
    require(valid_sha256(manifest_sha256), "the frozen public manifest fingerprint is invalid")
    require(document.get("schema") == PLAN_SCHEMA, "the frozen public plan schema changed")
    require(document.get("postfinal_schema") == PLAN_POSTFINAL_SCHEMA, "the expanded public plan schema changed")
    for key in ("protocol", "protocol_name", "exclusive_slot"):
        if key in document:
            require(document[key] == PREFIX, "the frozen public practice protocol changed")
    checks = {
        "modules": list(MODULES),
        "module_order": list(MODULES),
        "cases": CASES,
        "cases_per_candidate": CASES,
        "trials": TRIALS,
        "trials_per_module_case": TRIALS,
        "bootstrap_samples": BOOTSTRAPS,
        "bootstrap_draws": BOOTSTRAPS,
        "all_bounded_workload_categories": CATEGORY_COUNT,
        "category_count": CATEGORY_COUNT,
        "public_operations": API_COUNTS,
        "api_counts": API_COUNTS,
    }
    for key, expected in checks.items():
        if key in document:
            require(document[key] == expected, f"the frozen public manifest {key} changed")


def check_summary(
    summary: object, *, summary_sha256: str, manifest_sha256: str
) -> Results:
    require(isinstance(summary, dict), "the expanded public summary is not a JSON object")
    require(valid_sha256(summary_sha256), "the expanded public summary fingerprint is invalid")
    require(valid_sha256(manifest_sha256), "the expanded public manifest fingerprint is invalid")
    required = {
        "schema": SUMMARY_SCHEMA,
        "postfinal_schema": SUMMARY_POSTFINAL_SCHEMA,
        "cohort": "calibration",
        "holdout_accessed": False,
        "failed": 0,
        "modules": list(MODULES),
        "cases": CASES,
        "trials": TRIALS,
        "bootstrap_samples": BOOTSTRAPS,
        "paired_raw_rows": RAW_ROWS,
        "correctness_checks": CORRECTNESS_GATES,
        "all_bounded_workload_categories": CATEGORY_COUNT,
        "public_operations": API_COUNTS,
    }
    for key, expected in required.items():
        require(
            summary.get(key) == expected and type(summary.get(key)) is type(expected),
            f"the frozen expanded public {key} changed or is NOT MEASURED",
        )
    for key in ("protocol", "exclusive_slot"):
        if key in summary:
            require(summary[key] == PREFIX, "the expanded public practice slot changed")
    for key in ("manifest_sha256", "plan_sha256"):
        if key in summary:
            require(summary[key] == manifest_sha256, "the expanded summary is not bound to its frozen public plan")
    threshold = finite(summary.get("strict_regression_speedup_threshold"), "public slowdown threshold")
    same_float(threshold, 5 / 6, "the more-than-20%-slower rule changed")

    before = summary.get("candidate_binary_sha256_before")
    after = summary.get("candidate_binary_sha256_after")
    require(isinstance(before, dict) and before == after, "a public candidate changed during measurement")
    require(set(before) == previous.ARTIFACT_ROLES, "a four-way public engine fingerprint is missing")
    require(all(valid_sha256(value) for value in before.values()), "an expanded public engine fingerprint is invalid")

    proofs = summary.get("verified_edge_oracles")
    require(isinstance(proofs, list) and len(proofs) == len(CANDIDATES), "an original public correctness gate is missing")
    proof_modules: set[str] = set()
    for proof in proofs:
        require(isinstance(proof, dict), "invalid expanded public correctness gate")
        module = proof.get("module")
        require(module in CANDIDATES and module not in proof_modules, "a public candidate correctness gate is duplicated")
        require(proof.get("correctness_checks") == previous.EDGE_CHECKS, "an original edge-correctness gate changed")
        require(proof.get("script_sha256") == previous.ORACLE_SOURCE_SHA256, "the original correctness oracle changed")
        require(proof.get("actual_sha256") == previous.ORACLE_ANSWER_SHA256, "the original correctness answers changed")
        proof_modules.add(module)

    ranking_rows = summary.get("rankings")
    case_rows = summary.get("case_results")
    require(isinstance(ranking_rows, list) and len(ranking_rows) == len(CANDIDATES), "a candidate public ranking is NOT MEASURED")
    require(
        isinstance(case_rows, list) and len(case_rows) == CASES * len(CANDIDATES),
        "an expanded public candidate case was omitted or duplicated",
    )
    rankings: dict[str, dict] = {}
    for ranking in ranking_rows:
        require(isinstance(ranking, dict), "invalid expanded public candidate ranking")
        module = ranking.get("candidate")
        require(module in CANDIDATES and module not in rankings, "a public candidate ranking is missing or duplicated")
        require(ranking.get("cohort") == "calibration", "a ranking is not public calibration")
        require(ranking.get("cases") == CASES and ranking.get("weight") == CASES, "a ranking changes the 4,096-case denominator")
        low = finite(ranking.get("ci95_low"), "public confidence lower bound")
        speed = finite(ranking.get("geomean_speedup"), "public geometric mean")
        high = finite(ranking.get("ci95_high"), "public confidence upper bound")
        require(low <= speed <= high, "a public confidence interval excludes its measured estimate")
        rankings[module] = ranking

    by_module: dict[str, list[dict]] = {module: [] for module in CANDIDATES}
    seen: set[tuple[str, str]] = set()
    baseline_by_case: dict[str, float] = {}
    categories: dict[str, str] = {}
    for row in case_rows:
        require(isinstance(row, dict), "invalid expanded public case")
        module, case = row.get("candidate"), row.get("case")
        require(module in by_module, "an unapproved candidate entered public practice")
        require(isinstance(case, str) and case.startswith("cal."), "a non-calibration case entered public practice")
        require((module, case) not in seen, "an expanded public case was duplicated")
        seen.add((module, case))
        require(row.get("cohort") == "calibration", "a non-public case entered the comparison")
        require(row.get("api") in API_COUNTS, "an original public operation was substituted")
        require(type(row.get("weight")) is int and row["weight"] == 1, "an expanded public case was reweighted")
        category = row.get("category")
        require(isinstance(category, str) and bool(category), "a public workload category is missing")
        speed = finite(row.get("speedup"), f"{case} speed")
        low = finite(row.get("ci95_low"), f"{case} confidence lower bound")
        high = finite(row.get("ci95_high"), f"{case} confidence upper bound")
        require(low <= speed <= high, f"{case} has an invalid confidence interval")
        baseline_ns = finite(row.get("baseline_ns"), f"{case} CPython timing")
        finite(row.get("candidate_ns"), f"{case} candidate timing")
        finite(row.get("peak_traced_ratio"), f"{case} Python-traced memory", allow_zero=True)
        faster, slowdown = row.get("statistically_faster"), row.get("regression_gt_20pct")
        require(isinstance(faster, bool) and faster == (low > 1), f"{case} invents a confidence-supported win")
        require(isinstance(slowdown, bool) and slowdown == (speed < threshold), f"{case} hides a substantial slowdown")
        if case in baseline_by_case:
            same_float(baseline_ns, baseline_by_case[case], f"{case} changed its shared CPython baseline")
            require(categories[case] == category, f"{case} changed its shared public category")
        else:
            baseline_by_case[case] = baseline_ns
            categories[case] = category
        by_module[module].append(row)

    require(len(baseline_by_case) == CASES, "the engines did not share all 4,096 public cases")
    require(len(set(categories.values())) == CATEGORY_COUNT, "one of the 260 public workload categories was removed")
    case_names = frozenset(baseline_by_case)
    measured_losses: list[dict] = []
    candidates: list[Candidate] = []
    for module in CANDIDATES:
        rows = tuple(by_module[module])
        label = DISPLAY[module]
        require(len(rows) == CASES and frozenset(row["case"] for row in rows) == case_names, f"{label} omitted a shared public case")
        require(dict(Counter(row["api"] for row in rows)) == API_COUNTS, f"{label} altered an original operation denominator")
        ranking = rankings[module]
        same_float(geometric(rows), ranking["geomean_speedup"], f"{label} omitted or reweighted a public timing")
        wins = sum(row["statistically_faster"] for row in rows)
        losses = [row for row in rows if row["regression_gt_20pct"]]
        require(type(ranking.get("statistically_faster_cases")) is int and ranking["statistically_faster_cases"] == wins, f"{label} fabricated a clear-win count")
        require(type(ranking.get("regressions_gt_20pct")) is int and ranking["regressions_gt_20pct"] == len(losses), f"{label} concealed a substantial slowdown")
        measured_losses.extend(losses)
        candidates.append(Candidate(module, ranking, rows))

    reported = summary.get("regressions")
    require(isinstance(reported, list) and all(isinstance(row, dict) for row in reported), "the expanded public slowdown records are NOT MEASURED")
    key = lambda row: (row.get("candidate", ""), row.get("case", ""))
    require(sorted(reported, key=key) == sorted(measured_losses, key=key), "an individual expanded public slowdown was concealed or changed")
    ordered = tuple(sorted(candidates, key=lambda item: (-item.ranking["geomean_speedup"], DISPLAY[item.module])))
    return Results(summary, ordered, summary_sha256, manifest_sha256)


def read_json(path: Path, *, allowed: Path, label: str, digest: str | None = None) -> tuple[dict, str]:
    require(path.resolve() == allowed.resolve(), f"only the exact frozen public {label} may be read")
    try:
        payload = allowed.read_bytes()
        document = json.loads(payload.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"the frozen public {label} is NOT MEASURED") from error
    actual = hashlib.sha256(payload).hexdigest()
    if digest is not None:
        require(valid_sha256(digest) and actual == digest, f"the frozen public {label} SHA-256 changed")
    require(isinstance(document, dict), f"the frozen public {label} is not a JSON object")
    return document, actual


def check_integrity(document: object, results: Results, *, integrity_sha256: str) -> None:
    require(isinstance(document, dict), "the public integrity report is not a JSON object")
    require(valid_sha256(integrity_sha256), "the public integrity fingerprint is invalid")
    require(document.get("schema") == INTEGRITY_SCHEMA, "the expanded public integrity schema changed")
    require(document.get("result", document.get("status")) == "PASS", "the independent expanded public audit did not pass")
    require(document.get("summary_sha256") == results.summary_sha256, "the expanded audit does not bind its exact measured summary")
    require(document.get("manifest_sha256", document.get("plan_sha256")) == results.manifest_sha256, "the expanded audit does not bind its frozen public manifest")
    if "holdout_accessed" in document:
        require(document["holdout_accessed"] is False, "the public audit does not establish final-test isolation")
    expected = {
        "module_order": list(MODULES),
        "cases_per_candidate": CASES,
        "candidate_case_count": CASES * len(CANDIDATES),
        "trials_per_module_case": TRIALS,
        "raw_rows": RAW_ROWS,
        "correctness_checks": CORRECTNESS_GATES,
        "bootstrap_draws": BOOTSTRAPS,
        "bootstrap_samples": BOOTSTRAPS,
        "confidence_intervals": CONFIDENCE_INTERVALS,
        "strict_regressions": len(results.summary["regressions"]),
        "exclusive_slot": PREFIX,
        "source_audit_checks": 76,
        "from_scratch_checks": 76,
        "native_library_count": 5,
    }
    for key, value in expected.items():
        if key in document:
            require(document[key] == value, f"the expanded public integrity report changed {key}")
    for key in ("from_scratch_audit_sha256", "source_audit_sha256", "runner_sha256"):
        if key in document:
            require(valid_sha256(document[key]), f"the expanded public {key} is missing or invalid")
    if "native_elf_fingerprints" in document:
        expected_native = {
            key: value
            for key, value in results.summary["candidate_binary_sha256_before"].items()
            if key.endswith(":native-engine") or key.endswith(":native-bridge")
        }
        require(len(expected_native) == 5, "the public comparison does not contain five actual native libraries")
        require(document["native_elf_fingerprints"] == expected_native, "the public audit does not bind all five native libraries")


def svg_open(title: str, subtitle: str, results: Results, *, height: int, width: int = 1640) -> list[str]:
    description = (
        f"{BANNER}. CPython, C, Rust, and Zig ran the same {CASES} calibration-only "
        f"public cases, {TRIALS} paired trials, and {BOOTSTRAPS} bootstrap draws. "
        f"{subtitle}. Public manifest SHA-256 {results.manifest_sha256}; public "
        f"summary SHA-256 {results.summary_sha256}. {FINAL_STATUS}"
    )
    return [
        f'<svg xmlns="{SVG_NAMESPACE}" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="public-chart-title public-chart-description">',
        f'<title id="public-chart-title">{escape(title)}</title>',
        f'<desc id="public-chart-description">{escape(description)}</desc>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;fill:#172033}.title{font-size:31px;font-weight:760}.subtitle{font-size:16px;fill:#475569}.heading{font-size:19px;font-weight:730}.label{font-size:14px}.value{font-size:15px;font-weight:720}.note{font-size:13.5px;fill:#475569}.tick{font-size:13px;fill:#475569}.banner{font-size:16px;font-weight:740;fill:#7f1d1d}.status{font-size:14px;font-weight:680;fill:#7f1d1d}.grid{stroke:#e2e8f0;stroke-width:1}.baseline{stroke:#64748b;stroke-width:2}.panel{fill:#f8fafc;stroke:#d9e2ee;stroke-width:1}</style>',
        f'<text x="30" y="46" class="title">{escape(title)}</text>',
        f'<text x="31" y="77" class="subtitle">{escape(subtitle)}</text>',
        f'<rect x="23" y="93" width="{width - 46}" height="45" rx="8" fill="#fef2f2" stroke="#fca5a5"/>',
        f'<text x="37" y="123" class="banner">{escape(BANNER)}</text>',
        f'<text x="31" y="163" class="status">{escape(FINAL_STATUS)}</text>',
        f'<text x="31" y="186" class="note">Public plan SHA-256: {escape(results.manifest_sha256)}</text>',
        f'<text x="31" y="208" class="note">Public measurement SHA-256: {escape(results.summary_sha256)}</text>',
    ]


def svg_close(body: list[str]) -> str:
    return "\n".join((*body, "</svg>", ""))


def legend(body: list[str], results: Results, *, x: int = 380, y: int = 235) -> None:
    position = x
    for module in (BASELINE, *(candidate.module for candidate in results.candidates)):
        body.append(f'<circle cx="{position}" cy="{y - 5}" r="5.5" fill="{COLOURS[module]}"/>')
        body.append(f'<text x="{position + 12}" y="{y}" class="label">{escape(DISPLAY[module])}</text>')
        position += 255 if module == BASELINE else 105


def log_x(value: float, *, left: int, right: int, low: float, high: float) -> float:
    require(0 < low <= value <= high and low < high, "a measured public speed falls outside the chart axis")
    return left + (right - left) * (math.log(value) - math.log(low)) / (math.log(high) - math.log(low))


def speed_axis(body: list[str], *, left: int, right: int, top: int, bottom: int, low: float, high: float) -> None:
    for value, label in ((0.25, "0.25×"), (0.5, "0.5×"), (0.75, "0.75×"), (1.0, "1× CPython"), (1.25, "1.25×"), (1.5, "1.5×"), (2.0, "2×"), (3.0, "3×"), (4.0, "4×"), (8.0, "8×")):
        if low <= value <= high:
            x = log_x(value, left=left, right=right, low=low, high=high)
            style = "baseline" if value == 1 else "grid"
            body.append(f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{bottom}" class="{style}"/>')
            body.append(f'<text x="{x:.2f}" y="{top - 8}" text-anchor="middle" class="tick">{escape(label)}</text>')


def groups(candidate: Candidate) -> dict[str, tuple[dict, ...]]:
    grouped = {api: tuple(row for row in candidate.rows if row["api"] == api) for api in API_COUNTS}
    for api, rows in grouped.items():
        require(len(rows) == API_COUNTS[api], "a public operation was removed from a chart")
    return grouped


def overall_chart(results: Results) -> str:
    height, left, right = 625, 351, 933
    values = [1.0, *(number for candidate in results.candidates for number in (candidate.ranking["ci95_low"], candidate.ranking["ci95_high"]))]
    low, high = min(0.70, min(values) * 0.94), max(1.65, max(values) * 1.08)
    body = svg_open("Expanded public development speed compared with CPython", f"All four engines; {CASES:,} shared public cases; measured 95% confidence ranges", results, height=height)
    speed_axis(body, left=left, right=right, top=261, bottom=535, low=low, high=high)
    y = 283
    x = log_x(1.0, left=left, right=right, low=low, high=high)
    body.extend((f'<text x="31" y="{y + 5}" class="heading">{escape(DISPLAY[BASELINE])}</text>', f'<circle cx="{x:.2f}" cy="{y}" r="7" fill="{COLOURS[BASELINE]}"/>', f'<text x="954" y="{y + 5}" class="value">Exactly 1.000×; neutral baseline; {CASES:,}/{CASES:,} cases</text>'))
    for index, candidate in enumerate(results.candidates):
        y = 350 + index * 82
        rank = candidate.ranking
        lower, point, upper = rank["ci95_low"], rank["geomean_speedup"], rank["ci95_high"]
        colour = COLOURS[candidate.module]
        body.extend((
            f'<text x="31" y="{y + 5}" class="heading">{escape(DISPLAY[candidate.module])}</text>',
            f'<line x1="{log_x(lower, left=left, right=right, low=low, high=high):.2f}" y1="{y}" x2="{log_x(upper, left=left, right=right, low=low, high=high):.2f}" y2="{y}" stroke="{colour}" stroke-width="7" stroke-linecap="round"/>',
            f'<circle cx="{log_x(point, left=left, right=right, low=low, high=high):.2f}" cy="{y}" r="7" fill="{colour}" stroke="#ffffff" stroke-width="1.5"/>',
            f'<text x="954" y="{y - 9}" class="value">{fmt(point)}; 95% range {fmt(lower)} to {fmt(upper)}</text>',
            f'<text x="954" y="{y + 16}" class="note">{rank["statistically_faster_cases"]:,}/{CASES:,} clear wins; {rank["regressions_gt_20pct"]:,}/{CASES:,} substantial slowdowns</text>',
        ))
    body.append(f'<text x="31" y="{height - 21}" class="note">Confidence intervals compare each candidate only with CPython; no final or candidate-to-candidate performance claim is made.</text>')
    return svg_close(body)


def stack(body: list[str], *, y: int, parts: tuple[tuple[int, str], ...], left: int = 390, right: int = 1300) -> None:
    require(sum(count for count, _ in parts) == CASES, "a public outcomes chart changed the full denominator")
    x = float(left)
    for count, colour in parts:
        width = (right - left) * count / CASES
        if count:
            body.append(f'<rect x="{x:.2f}" y="{y}" width="{width:.2f}" height="22" fill="{colour}"/>')
            if width >= 43:
                body.append(f'<text x="{x + width / 2:.2f}" y="{y + 16}" text-anchor="middle" style="font-size:12px;font-weight:730;fill:#ffffff">{count:,}</text>')
        x += width


def outcomes_chart(results: Results) -> str:
    panel, height = 204, 254 + 204 * len(results.candidates) + 40
    body = svg_open("Every expanded public win, uncertain case, and slowdown", f"All {CASES:,} cases per candidate; measured and confidence-supported outcomes remain separate", results, height=height)
    legend(body, results)
    for index, candidate in enumerate(results.candidates):
        top = 257 + index * panel
        rows = candidate.rows
        faster, slower = sum(row["speedup"] > 1 for row in rows), sum(row["speedup"] < 1 for row in rows)
        equal = CASES - faster - slower
        clear_faster, clear_slower = sum(row["ci95_low"] > 1 for row in rows), sum(row["ci95_high"] < 1 for row in rows)
        uncertain = CASES - clear_faster - clear_slower
        losses = candidate.ranking["regressions_gt_20pct"]
        body.append(f'<rect x="22" y="{top - 14}" width="1596" height="{panel - 9}" rx="9" class="panel"/>')
        body.append(f'<text x="36" y="{top + 12}" class="heading">{escape(DISPLAY[candidate.module])}; {CASES:,}/{CASES:,} cases</text>')
        body.append(f'<text x="36" y="{top + 49}" class="label">Measured outcomes</text>')
        stack(body, y=top + 31, parts=((faster, "#047857"), (equal, "#64748b"), (slower, "#dc2626")))
        body.append(f'<text x="1320" y="{top + 48}" class="value">{CASES:,}/{CASES:,}</text>')
        body.append(f'<text x="390" y="{top + 70}" class="note">{faster:,} faster; {equal:,} equal; {slower:,} slower</text>')
        body.append(f'<text x="36" y="{top + 103}" class="label">95%-confidence outcomes</text>')
        stack(body, y=top + 85, parts=((clear_faster, "#047857"), (uncertain, "#64748b"), (clear_slower, "#dc2626")))
        body.append(f'<text x="1320" y="{top + 102}" class="value">{CASES:,}/{CASES:,}</text>')
        body.append(f'<text x="390" y="{top + 124}" class="note">{clear_faster:,} clearly faster; {uncertain:,} uncertain; {clear_slower:,} clearly slower</text>')
        body.append(f'<text x="36" y="{top + 163}" class="label">More than 20% longer</text>')
        body.append(f'<rect x="390" y="{top + 145}" width="910" height="22" fill="#fee2e2"/>')
        body.append(f'<rect x="390" y="{top + 145}" width="{910 * losses / CASES:.2f}" height="22" fill="#dc2626"/>')
        body.append(f'<text x="1320" y="{top + 162}" class="value">{losses:,}/{CASES:,}</text>')
    body.append(f'<text x="31" y="{height - 16}" class="note">All {len(results.summary["regressions"]):,} observed substantial public slowdowns remain visible; final outcomes are NOT MEASURED.</text>')
    return svg_close(body)


def api_chart(results: Results) -> str:
    family_top, family_row, category_row = 268, 42, 25
    category_top = family_top + len(API_COUNTS) * family_row + 66
    height = category_top + CATEGORY_COUNT * category_row + 62
    body = svg_open("All 12 public operations and all 260 workload categories", "Every frozen operation and category; geometric means only, not category confidence intervals", results, height=height)
    legend(body, results)
    all_groups = {candidate.module: groups(candidate) for candidate in results.candidates}
    points = [geometric(all_groups[candidate.module][api]) for candidate in results.candidates for api in API_COUNTS]
    low, high = min(0.45, min(points) * 0.92), max(2.1, max(points) * 1.09)
    speed_axis(body, left=435, right=1010, top=family_top, bottom=family_top + len(API_COUNTS) * family_row, low=low, high=high)
    for index, (api, count) in enumerate(API_COUNTS.items()):
        y = family_top + 22 + index * family_row
        body.append(f'<text x="31" y="{y + 4}" class="label">{escape(API_LABELS[api])} ({escape(api)}); {count}/{count}</text>')
        for offset, candidate in enumerate(results.candidates):
            value = geometric(all_groups[candidate.module][api])
            cy = y + (offset - 1) * 8
            x = log_x(value, left=435, right=1010, low=low, high=high)
            body.append(f'<circle cx="{x:.2f}" cy="{cy}" r="4.8" fill="{COLOURS[candidate.module]}"/>')
            body.append(f'<text x="{1031 + offset * 170}" y="{y + 4}" class="label">{escape(DISPLAY[candidate.module])} {fmt(value)}</text>')

    categories = sorted({row["category"] for row in results.candidates[0].rows})
    require(len(categories) == CATEGORY_COUNT, "the operation graph omits a public category")
    category_groups = {
        candidate.module: {
            category: tuple(row for row in candidate.rows if row["category"] == category)
            for category in categories
        }
        for candidate in results.candidates
    }
    body.append(f'<text x="31" y="{category_top - 24}" class="heading">Every one of the {CATEGORY_COUNT} observed public workload categories</text>')
    for index, category in enumerate(categories):
        y = category_top + index * category_row
        count = len(category_groups[results.candidates[0].module][category])
        require(count > 0, "a public workload category is empty")
        body.append(f'<text x="34" y="{y + 15}" class="label">{escape(category)}; {count}/{count} cases</text>')
        for offset, candidate in enumerate(results.candidates):
            family = category_groups[candidate.module][category]
            require(len(family) == count, "a candidate omitted a shared public category")
            body.append(f'<text x="{840 + offset * 245}" y="{y + 15}" class="label">{escape(DISPLAY[candidate.module])} {fmt(geometric(family))}</text>')
    body.append(f'<text x="31" y="{height - 19}" class="note">All 12 original operations and all 260 measured categories retain their full denominators; group values do not establish confidence or final results.</text>')
    return svg_close(body)


def regressions_chart(results: Results) -> str:
    losses = len(results.summary["regressions"])
    family_height, individual_height = 28, 24
    panels = [54 + len(API_COUNTS) * family_height + candidate.ranking["regressions_gt_20pct"] * individual_height + 14 for candidate in results.candidates]
    height = 258 + sum(panels) + 18 * (len(panels) - 1) + 44
    body = svg_open("Every individual expanded public slowdown over 20%", f"Every one of the {losses:,} observed substantial slowdowns; no case is hidden", results, height=height)
    legend(body, results)
    all_losses = [row for candidate in results.candidates for row in candidate.rows if row["regression_gt_20pct"]]
    require(len(all_losses) == losses, "the individual slowdown chart conceals a measured case")
    maximum = max(((1 / row["speedup"] - 1) * 100 for row in all_losses), default=20.0)
    shown: set[tuple[str, str]] = set()
    y = 259
    for candidate, panel_height in zip(results.candidates, panels, strict=True):
        body.append(f'<rect x="22" y="{y - 13}" width="1596" height="{panel_height}" rx="9" class="panel"/>')
        total = candidate.ranking["regressions_gt_20pct"]
        body.append(f'<text x="37" y="{y + 14}" class="heading">{escape(DISPLAY[candidate.module])}: {total:,}/{CASES:,} cases more than 20% slower than CPython</text>')
        cursor = y + 42
        grouped = groups(candidate)
        for api, count in API_COUNTS.items():
            family_losses = tuple(sorted((row for row in grouped[api] if row["regression_gt_20pct"]), key=lambda row: row["case"]))
            body.append(f'<text x="38" y="{cursor + 15}" class="value">{escape(API_LABELS[api])} ({escape(api)}): {len(family_losses)}/{count}</text>')
            cursor += family_height
            for row in family_losses:
                identity = (candidate.module, row["case"])
                require(identity not in shown, "an expanded public slowdown was duplicated")
                shown.add(identity)
                percent = (1 / row["speedup"] - 1) * 100
                require(percent > 20, "a displayed slowdown is not more than 20%")
                bar = 245 * math.log1p(percent) / math.log1p(maximum)
                body.extend((
                    f'<text x="52" y="{cursor + 15}" class="label">{escape(row["case"])}</text>',
                    f'<text x="884" y="{cursor + 15}" class="value">{fmt(row["speedup"])}</text>',
                    f'<text x="1005" y="{cursor + 15}" class="label">{percent:.1f}% longer</text>',
                    f'<rect x="1320" y="{cursor + 3}" width="245" height="15" rx="3" fill="#fee2e2"/>',
                    f'<rect x="1320" y="{cursor + 3}" width="{bar:.2f}" height="15" rx="3" fill="#dc2626"/>',
                ))
                cursor += individual_height
        y += panel_height + 18
    expected = {(row["candidate"], row["case"]) for row in results.summary["regressions"]}
    require(shown == expected and len(shown) == losses, "the graph omits an original measured public slowdown")
    body.append(f'<text x="31" y="{height - 18}" class="note">Every measured substantial loss is named individually; bars use a zero-preserving logarithmic visual scale. Final regressions: NOT MEASURED.</text>')
    return svg_close(body)


def memory_chart(results: Results) -> str:
    left, right, row_height, panel = 425, 1040, 33, 474
    height = 258 + panel * len(results.candidates) + 65
    by_module = {candidate.module: groups(candidate) for candidate in results.candidates}
    medians = [float(statistics.median(row["peak_traced_ratio"] for row in by_module[candidate.module][api])) for candidate in results.candidates for api in API_COUNTS]
    upper = max(1.75, max(medians, default=1.0) * 1.1)
    body = svg_open("Measured Python-traced expanded public allocations", "Python-traced temporary allocations only; final, native, and whole-process memory are NOT MEASURED", results, height=height)
    legend(body, results)
    for index, candidate in enumerate(results.candidates):
        top = 259 + index * panel
        median = float(statistics.median(row["peak_traced_ratio"] for row in candidate.rows))
        zeros = sum(row["peak_traced_ratio"] == 0 for row in candidate.rows)
        body.append(f'<rect x="22" y="{top - 13}" width="1596" height="{panel - 9}" rx="9" class="panel"/>')
        body.append(f'<text x="37" y="{top + 15}" class="heading">{escape(DISPLAY[candidate.module])}: {fmt(median)} median traced ratio; {zeros:,}/{CASES:,} zero-traced cases</text>')
        for tick, label in ((0.0, "0×"), (0.25, "0.25×"), (0.5, "0.5×"), (0.75, "0.75×"), (1.0, "1× CPython"), (1.5, "1.5×"), (2.0, "2×"), (3.0, "3×"), (4.0, "4×")):
            if tick <= upper:
                x = left + (right - left) * tick / upper
                style = "baseline" if tick == 1 else "grid"
                body.append(f'<line x1="{x:.2f}" y1="{top + 48}" x2="{x:.2f}" y2="{top + 64 + len(API_COUNTS) * row_height}" class="{style}"/>')
                body.append(f'<text x="{x:.2f}" y="{top + 40}" text-anchor="middle" class="tick">{escape(label)}</text>')
        for offset, (api, count) in enumerate(API_COUNTS.items()):
            rows = by_module[candidate.module][api]
            value = float(statistics.median(row["peak_traced_ratio"] for row in rows))
            require(0 <= value <= upper, "a public Python-traced measurement was clipped")
            y = top + 72 + offset * row_height
            x = left + (right - left) * value / upper
            zero_count = sum(row["peak_traced_ratio"] == 0 for row in rows)
            body.extend((
                f'<text x="37" y="{y + 4}" class="label">{escape(API_LABELS[api])} ({escape(api)})</text>',
                f'<circle cx="{x:.2f}" cy="{y}" r="5.5" fill="{COLOURS[candidate.module]}"/>',
                f'<text x="{right + 17}" y="{y + 4}" class="value">{fmt(value)}</text>',
                f'<text x="{right + 107}" y="{y + 4}" class="label">{count}/{count} cases; {zero_count} zero-traced</text>',
            ))
    body.append(f'<text x="31" y="{height - 40}" class="note">Python-traced allocations do not measure isolated native, whole-process, or final-benchmark memory: NOT MEASURED.</text>')
    body.append(f'<text x="31" y="{height - 17}" class="note">The linear axis preserves genuine zero-traced results; zero Python-traced allocations do not mean zero native memory.</text>')
    return svg_close(body)


def rankings_chart(results: Results) -> str:
    top, row_height, left, right = 272, 72, 323, 856
    height = top + len(MODULES) * row_height + 79
    points = [1.0, *(point for candidate in results.candidates for point in (candidate.ranking["ci95_low"], candidate.ranking["ci95_high"]))]
    low, high = min(0.70, min(points) * 0.94), max(1.65, max(points) * 1.08)
    body = svg_open("Expanded public ordering only — not a final ranking", f"Four-way public development estimates on all {CASES:,} shared cases; no final winner", results, height=height)
    speed_axis(body, left=left, right=right, top=top + 17, bottom=top + len(MODULES) * row_height - 8, low=low, high=high)
    body.append(f'<text x="876" y="{top + 4}" class="label">Public speed and 95% interval</text>')
    body.append(f'<text x="1280" y="{top + 4}" class="label">Clear wins</text>')
    body.append(f'<text x="1430" y="{top + 4}" class="label">&gt;20% slower</text>')
    ordered = [(candidate.ranking["geomean_speedup"], candidate.module, candidate) for candidate in results.candidates]
    ordered.append((1.0, BASELINE, None))
    ordered.sort(key=lambda item: (-item[0], DISPLAY[item[1]]))
    for index, (_, module, candidate) in enumerate(ordered):
        y = top + 46 + index * row_height
        colour = COLOURS[module]
        body.append(f'<text x="30" y="{y + 5}" class="heading">{index + 1}. {escape(DISPLAY[module])}</text>')
        if candidate is None:
            x = log_x(1.0, left=left, right=right, low=low, high=high)
            body.extend((f'<circle cx="{x:.2f}" cy="{y}" r="6" fill="{colour}"/>', f'<text x="876" y="{y + 4}" class="value">Exactly 1.000×; neutral baseline</text>', f'<text x="1280" y="{y + 4}" class="label">Baseline</text>', f'<text x="1430" y="{y + 4}" class="label">Baseline</text>'))
            continue
        rank = candidate.ranking
        lower, point, upper = rank["ci95_low"], rank["geomean_speedup"], rank["ci95_high"]
        body.extend((
            f'<line x1="{log_x(lower, left=left, right=right, low=low, high=high):.2f}" y1="{y}" x2="{log_x(upper, left=left, right=right, low=low, high=high):.2f}" y2="{y}" stroke="{colour}" stroke-width="7" stroke-linecap="round"/>',
            f'<circle cx="{log_x(point, left=left, right=right, low=low, high=high):.2f}" cy="{y}" r="6" fill="{colour}"/>',
            f'<text x="876" y="{y + 4}" class="value">{fmt(point)} [{fmt(lower)} to {fmt(upper)}]</text>',
            f'<text x="1280" y="{y + 4}" class="value">{rank["statistically_faster_cases"]:,}/{CASES:,}</text>',
            f'<text x="1430" y="{y + 4}" class="value">{rank["regressions_gt_20pct"]:,}/{CASES:,}</text>',
        ))
    body.append(f'<text x="30" y="{height - 18}" class="note">Public point-estimate ordering does not establish candidate-to-candidate significance. Final ranking: NOT MEASURED; final winner: NONE.</text>')
    return svg_close(body)


def validate_svg(svg: str, *, suffix: str, results: Results) -> None:
    try:
        root = ElementTree.fromstring(svg)
    except ElementTree.ParseError as error:
        raise ValueError(f"the {suffix} chart is not valid SVG") from error
    require(root.tag == f"{{{SVG_NAMESPACE}}}svg" and root.get("role") == "img", f"the {suffix} chart is not accessible SVG")
    require(root.get("aria-labelledby") == "public-chart-title public-chart-description", f"the {suffix} chart lacks accessible labels")
    require(root.find(f"{{{SVG_NAMESPACE}}}title") is not None and root.find(f"{{{SVG_NAMESPACE}}}desc") is not None, f"the {suffix} chart lacks its title or description")
    visible = " ".join(text for text in root.itertext() if text)
    for required in (BANNER, FINAL_STATUS, "CPython", "Rust", "Zig", "NOT MEASURED", results.manifest_sha256, results.summary_sha256):
        require(required in visible, f"the {suffix} chart omitted {required}")
    require(any((node.text or "").strip() == "C" or (node.text or "").strip().startswith(("C ", "C:", "1. C", "2. C", "3. C", "4. C")) for node in root.iter()), f"the {suffix} chart omitted the C engine")
    require(root.find(f".//{{{SVG_NAMESPACE}}}script") is None, f"the {suffix} chart contains executable content")
    if suffix == "api":
        for api in API_COUNTS:
            require(f"({api})" in visible, "the operation graph omits an original public API")
        for category in {row["category"] for row in results.candidates[0].rows}:
            require(category in visible, "the operation graph omits a public workload category")
    elif suffix == "regressions":
        for row in results.summary["regressions"]:
            require(row["case"] in visible, "the slowdown graph omits an individual measured loss")
    elif suffix == "memory":
        require("Python-traced" in visible and "native" in visible and "0×" in visible, "the public memory graph misrepresents its measurement scope")


def build_charts(results: Results) -> dict[str, str]:
    charts = {
        "overall": overall_chart(results),
        "outcomes": outcomes_chart(results),
        "api": api_chart(results),
        "regressions": regressions_chart(results),
        "memory": memory_chart(results),
        "rankings": rankings_chart(results),
    }
    require(tuple(charts) == SUFFIXES, "a required expanded public chart was removed")
    for suffix, svg in charts.items():
        validate_svg(svg, suffix=suffix, results=results)
    return charts


def synthetic_documents() -> tuple[dict, dict, dict]:
    manifest = {
        "schema": PLAN_SCHEMA,
        "postfinal_schema": PLAN_POSTFINAL_SCHEMA,
        "protocol": PREFIX,
        "modules": list(MODULES),
        "cases": CASES,
        "trials": TRIALS,
        "bootstrap_samples": BOOTSTRAPS,
        "all_bounded_workload_categories": CATEGORY_COUNT,
        "public_operations": dict(API_COUNTS),
    }
    manifest_digest = canonical_sha256(manifest)
    fingerprints = {role: hashlib.sha256(role.encode("utf-8")).hexdigest() for role in sorted(previous.ARTIFACT_ROLES)}
    summary: dict = {
        "schema": SUMMARY_SCHEMA,
        "postfinal_schema": SUMMARY_POSTFINAL_SCHEMA,
        "cohort": "calibration",
        "holdout_accessed": False,
        "failed": 0,
        "modules": list(MODULES),
        "cases": CASES,
        "trials": TRIALS,
        "bootstrap_samples": BOOTSTRAPS,
        "paired_raw_rows": RAW_ROWS,
        "correctness_checks": CORRECTNESS_GATES,
        "all_bounded_workload_categories": CATEGORY_COUNT,
        "public_operations": dict(API_COUNTS),
        "manifest_sha256": manifest_digest,
        "exclusive_slot": PREFIX,
        "strict_regression_speedup_threshold": 5 / 6,
        "candidate_binary_sha256_before": dict(fingerprints),
        "candidate_binary_sha256_after": dict(fingerprints),
        "verified_edge_oracles": [{"module": module, "correctness_checks": previous.EDGE_CHECKS, "script_sha256": previous.ORACLE_SOURCE_SHA256, "actual_sha256": previous.ORACLE_ANSWER_SHA256} for module in CANDIDATES],
        "case_results": [],
        "rankings": [],
        "regressions": [],
    }
    specs: list[tuple[str, str, str]] = []
    index = 0
    for api, count in API_COUNTS.items():
        for _ in range(count):
            specs.append((f"cal.{api}.synthetic.{index:04d}", api, f"synthetic-public-category-{index % CATEGORY_COUNT:03d}"))
            index += 1
    require(len(specs) == CASES, "the synthetic expanded public API counts changed")
    for module_index, module in enumerate(CANDIDATES):
        rows: list[dict] = []
        for index, (case, api, category) in enumerate(specs):
            band = (index * 37 + module_index * 83) % CASES
            if band < 75 + module_index * 19:
                speed = 0.60 + (index % 9) * 0.018
            elif band < 490 + module_index * 23:
                speed = 0.86 + (index % 6) * 0.01
            elif band < 940 + module_index * 31:
                speed = 0.98 + (index % 5) * 0.01
            else:
                speed = 1.10 + (index % 13) * 0.017 + module_index * 0.003
            low, high = speed * 0.96, speed * 1.04
            baseline_ns = float(1_000 + index % 97)
            row = {
                "api": api,
                "baseline_ns": baseline_ns,
                "candidate": module,
                "candidate_ns": baseline_ns / speed,
                "case": case,
                "category": category,
                "ci95_high": high,
                "ci95_low": low,
                "cohort": "calibration",
                "input": "text",
                "lifecycle": "compiled",
                "peak_traced_ratio": (0.0, 0.35, 0.61, 0.89, 1.0, 1.33)[(index + module_index) % 6],
                "regression_gt_20pct": speed < 5 / 6,
                "result_density": "one",
                "speedup": speed,
                "statistically_faster": low > 1,
                "weight": 1,
            }
            rows.append(row)
            summary["case_results"].append(row)
            if row["regression_gt_20pct"]:
                summary["regressions"].append(dict(row))
        speed = geometric(tuple(rows))
        summary["rankings"].append({"candidate": module, "cases": CASES, "ci95_high": speed * 1.04, "ci95_low": speed * 0.96, "cohort": "calibration", "geomean_speedup": speed, "regressions_gt_20pct": sum(row["regression_gt_20pct"] for row in rows), "statistically_faster_cases": sum(row["statistically_faster"] for row in rows), "weight": CASES})
    summary_digest = canonical_sha256(summary)
    integrity = {
        "schema": INTEGRITY_SCHEMA,
        "result": "PASS",
        "holdout_accessed": False,
        "manifest_sha256": manifest_digest,
        "summary_sha256": summary_digest,
        "module_order": list(MODULES),
        "cases_per_candidate": CASES,
        "candidate_case_count": CASES * len(CANDIDATES),
        "trials_per_module_case": TRIALS,
        "raw_rows": RAW_ROWS,
        "correctness_checks": CORRECTNESS_GATES,
        "bootstrap_draws": BOOTSTRAPS,
        "confidence_intervals": CONFIDENCE_INTERVALS,
        "strict_regressions": len(summary["regressions"]),
        "source_audit_checks": 76,
        "native_library_count": 5,
        "native_elf_fingerprints": {role: digest for role, digest in fingerprints.items() if role.endswith(":native-engine") or role.endswith(":native-bridge")},
    }
    return manifest, summary, integrity


def self_test() -> dict:
    manifest, summary, integrity = synthetic_documents()
    manifest_digest, summary_digest = canonical_sha256(manifest), canonical_sha256(summary)
    check_manifest(manifest, manifest_sha256=manifest_digest)
    results = check_summary(summary, summary_sha256=summary_digest, manifest_sha256=manifest_digest)
    check_integrity(integrity, results, integrity_sha256=canonical_sha256(integrity))
    charts = build_charts(results)
    require(charts == build_charts(results), "expanded public charts are not deterministic")
    mutations = (
        ("final-test access", lambda value: value.__setitem__("holdout_accessed", True)),
        ("changed summary schema", lambda value: value.__setitem__("postfinal_schema", "substituted")),
        ("changed public denominator", lambda value: value.__setitem__("cases", CASES - 1)),
        ("changed bootstrap count", lambda value: value.__setitem__("bootstrap_samples", BOOTSTRAPS - 1)),
        ("substituted CPython", lambda value: value["modules"].__setitem__(0, "substituted")),
        ("dropped public case", lambda value: value["case_results"].pop()),
        ("non-public case", lambda value: value["case_results"][0].__setitem__("case", "not-calibration")),
        ("changed shared baseline", lambda value: value["case_results"][CASES].__setitem__("baseline_ns", 777_777.0)),
        ("missing Python-traced memory", lambda value: value["case_results"][0].__setitem__("peak_traced_ratio", None)),
        ("concealed individual slowdown", lambda value: value["regressions"].pop()),
        ("invented clear win", lambda value: value["rankings"][0].__setitem__("statistically_faster_cases", -1)),
        ("hidden ranking slowdown", lambda value: value["rankings"][0].__setitem__("regressions_gt_20pct", -1)),
        ("changed original operation", lambda value: value["public_operations"].__setitem__("split", 413)),
        ("dropped correctness proof", lambda value: value["verified_edge_oracles"].pop()),
        ("changed measured engine", lambda value: value["candidate_binary_sha256_after"].__setitem__(f"{previous.RUST}:native-engine", "0" * 64)),
        ("changed frozen manifest binding", lambda value: value.__setitem__("manifest_sha256", "0" * 64)),
    )
    for label, mutate in mutations:
        changed = copy.deepcopy(summary)
        mutate(changed)
        try:
            check_summary(changed, summary_sha256=canonical_sha256(changed), manifest_sha256=manifest_digest)
        except (ValueError, TypeError):
            continue
        raise ValueError(f"the isolated synthetic test accepted {label}")
    changed_integrity = copy.deepcopy(integrity)
    changed_integrity["strict_regressions"] += 1
    try:
        check_integrity(changed_integrity, results, integrity_sha256=canonical_sha256(changed_integrity))
    except ValueError:
        pass
    else:
        raise ValueError("the isolated synthetic test accepted a concealed audited slowdown")
    return {
        "result": "PASS",
        "mode": "candidate-free in-memory synthetic only; no benchmark files read or written",
        "charts": len(charts),
        "public_modules": len(MODULES),
        "synthetic_cases_per_module": CASES,
        "synthetic_workload_categories": CATEGORY_COUNT,
        "synthetic_individually_visible_slowdowns": len(summary["regressions"]),
        "adversarial_rejections": len(mutations) + 1,
        "genuine_expanded_public_result": "NOT MEASURED",
        "historical_final_benchmark": "FAILED; no final winner",
    }


def render(*, summary: Path, integrity: Path, manifest: Path, output_dir: Path) -> dict:
    previous.verify_final_failure()
    public_manifest, manifest_digest = read_json(manifest, allowed=MANIFEST, label="expanded practice manifest", digest=MANIFEST_SHA256)
    check_manifest(public_manifest, manifest_sha256=manifest_digest)
    public_summary, summary_digest = read_json(summary, allowed=SUMMARY, label="expanded practice summary")
    results = check_summary(public_summary, summary_sha256=summary_digest, manifest_sha256=manifest_digest)
    public_integrity, integrity_digest = read_json(integrity, allowed=INTEGRITY, label="expanded practice integrity report")
    check_integrity(public_integrity, results, integrity_sha256=integrity_digest)
    charts = build_charts(results)
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        outputs = []
        for suffix in SUFFIXES:
            destination = output_dir / f"{PREFIX}-{suffix}.svg"
            svg = charts[suffix]
            destination.write_text(svg, encoding="utf-8", newline="\n")
            outputs.append({"chart": suffix, "path": str(destination.resolve()), "sha256": hashlib.sha256(svg.encode("utf-8")).hexdigest()})
    except OSError as error:
        raise ValueError("cannot write the explicitly selected public chart directory") from error
    return {
        "result": "PASS",
        "measurement": "expanded public development only; not the failed final benchmark",
        "manifest_sha256": manifest_digest,
        "summary_sha256": summary_digest,
        "integrity_sha256": integrity_digest,
        "public_cases_per_module": CASES,
        "individually_visible_public_slowdowns": len(results.summary["regressions"]),
        "final_failure_report_sha256": previous.FINAL_FAILURE_REPORT_SHA256,
        "final_failure_certificate_sha256": previous.FINAL_FAILURE_CERTIFICATE_SHA256,
        "final_benchmark": "FAILED; final speed, final memory, and final ranking NOT MEASURED; no final winner",
        "charts": outputs,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render six independently audited expanded public-practice SVGs; never read hidden final-test evidence.")
    parser.add_argument("--self-test", action="store_true", help="run candidate-free synthetic checks without file access")
    parser.add_argument("--summary", type=Path, help="exact expanded public practice summary")
    parser.add_argument("--integrity", type=Path, help="exact independent expanded public integrity report")
    parser.add_argument("--manifest", type=Path, help="exact SHA-256-frozen expanded public manifest")
    parser.add_argument("--output-dir", type=Path, help="explicit destination for exactly six SVG charts")
    args = parser.parse_args(argv)
    values = (args.summary, args.integrity, args.manifest, args.output_dir)
    if args.self_test:
        if any(value is not None for value in values):
            parser.error("--self-test cannot access benchmark inputs or write chart outputs")
    elif any(value is None for value in values):
        parser.error("rendering requires explicit --summary, --integrity, --manifest, and --output-dir")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = self_test() if args.self_test else render(summary=args.summary, integrity=args.integrity, manifest=args.manifest, output_dir=args.output_dir)
    except (OSError, ValueError, TypeError) as error:
        print(f"expanded public practice chart rendering rejected: {error}")
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
