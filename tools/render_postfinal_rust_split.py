#!/usr/bin/env python3
"""Render only the four-way, source-bound, post-final public comparison.

The final independent benchmark failed. These charts cannot establish final
speed, final memory, a final ranking, or a winning replacement. This renderer
never opens a final artifact, a raw archive, a protocol, or a seal: its sole
permitted inputs are the exact public development summary, its optional public
integrity report, and the SHA-256-pinned published final failure certificates.
"""

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
from typing import Iterable
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parent.parent
PUBLIC_SUMMARY = (
    ROOT
    / "performance"
    / "v7"
    / "evidence"
    / "postfinal-rust-batched-split-01-summary.json"
)
PUBLIC_INTEGRITY = (
    ROOT
    / "performance"
    / "v7"
    / "evidence"
    / "postfinal-rust-batched-split-01-integrity.json"
)
FINAL_FAILURE_REPORT = (
    ROOT / "performance" / "v9" / "evidence" / "FINAL-HOLDOUT-FAILURE.md"
)
FINAL_FAILURE_REPORT_SHA256 = (
    "39ca5011c4fe2d965b39d1cd9d062a7a300ef8aa51631e84b5afffaf932270ba"
)
FINAL_FAILURE_CERTIFICATE = (
    ROOT
    / "performance"
    / "v9"
    / "evidence"
    / "V9-FINAL-HOLDOUT-24576-FAILURE.json"
)
FINAL_FAILURE_CERTIFICATE_SHA256 = (
    "b3c9ac416d0a748a9fbe4f80f97efefb56ae7f598eea425c614aa278cb177069"
)
PUBLIC_ANSWER_SHA256 = (
    "2e6c098bd3a4757620461363106a9795f8defa98fe8bc9c13c0ebbf7ed58b598"
)
ORACLE_SOURCE_SHA256 = (
    "fe6a263a48f243ea02faaa78fc3bbd051233a2b2221967a5f76dd1bb79d242ca"
)
ORACLE_ANSWER_SHA256 = (
    "b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526"
)
SUMMARY_SCHEMA = "rebar-rust-balanced-calibration-pilot-v7"
PUBLIC_SLOT = "postfinal-rust-batched-split-01"

CASES = 624
TRIALS = 7
WARMUPS = 4
BOOTSTRAPS = 499
PAIRED_ROWS = 17_472
CORRECTNESS_CHECKS = 52_416
PUBLIC_CATEGORIES = 260
EDGE_CHECKS = 223_198
REGRESSION_THRESHOLD = 5 / 6

BASELINE = "re"
RUST = "candidates.rust_candidate"
C_ENGINE = "candidates.vm_candidate"
ZIG = "candidates.zig_candidate"
MODULES = (BASELINE, RUST, C_ENGINE, ZIG)
CANDIDATES = MODULES[1:]

DISPLAY = {
    BASELINE: "CPython (standard Python)",
    RUST: "Rust",
    C_ENGINE: "C",
    ZIG: "Zig",
}
COLOURS = {
    BASELINE: "#64748b",
    RUST: "#c2410c",
    C_ENGINE: "#2563eb",
    ZIG: "#7c3aed",
}

API_COUNTS = {
    "compile": 48,
    "escape": 48,
    "findall": 80,
    "finditer": 67,
    "fullmatch": 47,
    "match": 48,
    "match-surface": 48,
    "scanner": 48,
    "search": 48,
    "split": 47,
    "sub": 48,
    "subn": 47,
}
API_LABELS = {
    "compile": "Prepare a regular expression",
    "escape": "Escape special characters",
    "findall": "Find all matching results",
    "finditer": "Stream matching results",
    "fullmatch": "Match the entire input",
    "match": "Match at the beginning",
    "match-surface": "Read match information",
    "scanner": "Scan repeated matches",
    "search": "Search for a match",
    "split": "Split around matches",
    "sub": "Replace matching text",
    "subn": "Replace and count matches",
}
API_LIFETIMES = {
    "compile / cold": 48,
    "escape / module": 48,
    "findall / compiled": 78,
    "findall / module": 2,
    "finditer / compiled": 65,
    "finditer / module": 2,
    "fullmatch / compiled": 47,
    "match / compiled": 48,
    "match-surface / compiled": 48,
    "scanner / compiled": 48,
    "search / cold": 6,
    "search / compiled": 35,
    "search / module": 7,
    "split / compiled": 47,
    "sub / cold": 4,
    "sub / compiled": 33,
    "sub / module": 11,
    "subn / compiled": 37,
    "subn / module": 10,
}
INPUT_COUNTS = {"bytearray": 27, "bytes": 51, "memoryview": 17, "text": 529}
LIFETIME_COUNTS = {"cold": 58, "compiled": 486, "module": 80}
DENSITY_COUNTS = {"few": 181, "many": 113, "none": 71, "one": 259}
ARTIFACT_ROLES = frozenset(
    (
        f"{BASELINE}:module",
        f"{RUST}:module",
        f"{RUST}:native-bridge",
        f"{RUST}:native-engine",
        f"{RUST}:native-source",
        f"{RUST}:bridge-source",
        f"{C_ENGINE}:module",
        f"{C_ENGINE}:native-engine",
        f"{ZIG}:module",
        f"{ZIG}:native-bridge",
        f"{ZIG}:native-engine",
    )
)

BANNER = "Public development only; final independent benchmark failed; no final winner"
FINAL_STATUS = (
    "Final speed, final memory, and final candidate ranking: NOT MEASURED. "
    "Final winner: NONE."
)
CHART_SUFFIXES = ("overall", "outcomes", "api", "regressions", "memory", "rankings")
OUTPUT_PREFIX = "postfinal-rust-batched-split-01"
SVG_NAMESPACE = "http://www.w3.org/2000/svg"


@dataclass(frozen=True)
class CandidateResult:
    module: str
    ranking: dict
    rows: tuple[dict, ...]


@dataclass(frozen=True)
class PublicResults:
    summary: dict
    candidates: tuple[CandidateResult, ...]
    summary_sha256: str


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def finite(value: object, label: str, *, allow_zero: bool = False) -> float:
    require(
        isinstance(value, (int, float)) and not isinstance(value, bool),
        f"{label} is NOT MEASURED or is not a number",
    )
    number = float(value)
    require(math.isfinite(number), f"{label} is NOT MEASURED or is not finite")
    require(number >= 0 if allow_zero else number > 0, f"{label} is out of range")
    return number


def same_float(actual: float, expected: float, label: str) -> None:
    require(math.isclose(actual, expected, rel_tol=1e-11, abs_tol=1e-12), label)


def geometric(rows: Iterable[dict]) -> float:
    values = tuple(rows)
    require(bool(values), "a public workload family has no measured cases")
    return math.exp(
        math.fsum(math.log(finite(row.get("speedup"), "public case speed")) for row in values)
        / len(values)
    )


def valid_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def validate_public_summary(
    summary: object, *, summary_sha256: str | None = None
) -> PublicResults:
    require(isinstance(summary, dict), "the public development summary is not a JSON object")
    if summary_sha256 is None:
        canonical = json.dumps(
            summary, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        summary_sha256 = hashlib.sha256(canonical).hexdigest()
    require(valid_sha256(summary_sha256), "the public development summary fingerprint is invalid")
    expected_metadata = {
        "schema": SUMMARY_SCHEMA,
        "cohort": "calibration",
        "holdout_accessed": False,
        "exclusive_slot": PUBLIC_SLOT,
        "failed": 0,
        "expected_sha256": PUBLIC_ANSWER_SHA256,
        "modules": list(MODULES),
        "cases": CASES,
        "trials": TRIALS,
        "warmups": WARMUPS,
        "bootstrap_samples": BOOTSTRAPS,
        "paired_raw_rows": PAIRED_ROWS,
        "correctness_checks": CORRECTNESS_CHECKS,
        "all_bounded_workload_categories": PUBLIC_CATEGORIES,
        "public_operations": API_COUNTS,
        "api_lifetimes": API_LIFETIMES,
        "inputs": INPUT_COUNTS,
        "lifetimes": LIFETIME_COUNTS,
        "result_densities": DENSITY_COUNTS,
    }
    for key, expected in expected_metadata.items():
        require(
            summary.get(key) == expected and type(summary.get(key)) is type(expected),
            f"the frozen public development {key} changed or is NOT MEASURED",
        )

    for seed_name in ("bootstrap_seed", "order_seed", "selection_seed"):
        seed = summary.get(seed_name)
        require(
            type(seed) is int and seed >= 0,
            f"the post-final public {seed_name} is NOT MEASURED or invalid",
        )
    measurement = summary.get("measurement")
    require(
        isinstance(measurement, str)
        and ("practice" in measurement.casefold() or "development" in measurement.casefold()),
        "the post-final measurement is not explicitly public development",
    )

    threshold = finite(summary.get("strict_regression_speedup_threshold"), "slowdown threshold")
    same_float(threshold, REGRESSION_THRESHOLD, "the more-than-20%-slower rule changed")

    before = summary.get("candidate_binary_sha256_before")
    after = summary.get("candidate_binary_sha256_after")
    require(isinstance(before, dict) and before == after, "a measured development engine changed")
    require(set(before) == ARTIFACT_ROLES, "a four-way public engine fingerprint is missing")
    require(all(valid_sha256(digest) for digest in before.values()), "invalid public engine fingerprint")

    proofs = summary.get("verified_edge_oracles")
    require(isinstance(proofs, list) and len(proofs) == len(CANDIDATES), "a public qualification is missing")
    proof_modules: set[str] = set()
    for proof in proofs:
        require(isinstance(proof, dict), "invalid public correctness qualification")
        module = proof.get("module")
        require(module in CANDIDATES and module not in proof_modules, "a public candidate proof is duplicated or missing")
        require(proof.get("correctness_checks") == EDGE_CHECKS, "a public correctness check was omitted")
        require(proof.get("script_sha256") == ORACLE_SOURCE_SHA256, "the public correctness oracle changed")
        require(proof.get("actual_sha256") == ORACLE_ANSWER_SHA256, "the public correctness answers changed")
        proof_modules.add(module)

    rankings = summary.get("rankings")
    require(isinstance(rankings, list) and len(rankings) == len(CANDIDATES), "a public candidate ranking is missing")
    ranking_by_module: dict[str, dict] = {}
    for ranking in rankings:
        require(isinstance(ranking, dict), "invalid public candidate ranking")
        module = ranking.get("candidate")
        require(module in CANDIDATES and module not in ranking_by_module, "a public candidate ranking was substituted")
        require(ranking.get("cohort") == "calibration", "a ranking is not public development")
        require(ranking.get("cases") == CASES and ranking.get("weight") == CASES, "a ranking changed the 624-case denominator")
        point = finite(ranking.get("geomean_speedup"), "overall public development speed")
        low = finite(ranking.get("ci95_low"), "public confidence lower bound")
        high = finite(ranking.get("ci95_high"), "public confidence upper bound")
        require(low <= point <= high, "a public confidence range excludes its measured estimate")
        ranking_by_module[module] = ranking

    case_rows = summary.get("case_results")
    require(
        isinstance(case_rows, list) and len(case_rows) == CASES * len(CANDIDATES),
        "a candidate's public 624-case workload was omitted or duplicated",
    )
    by_module: dict[str, list[dict]] = {module: [] for module in CANDIDATES}
    seen: set[tuple[str, str]] = set()
    baseline_by_case: dict[str, float] = {}
    category_by_case: dict[str, str] = {}

    for row in case_rows:
        require(isinstance(row, dict), "invalid public development case")
        module = row.get("candidate")
        case = row.get("case")
        category = row.get("category")
        require(module in by_module, "a non-public candidate entered the comparison")
        require(isinstance(case, str) and case.startswith("cal."), "a non-public case entered the comparison")
        require(isinstance(category, str) and bool(category), "a public workload category is missing")
        require((module, case) not in seen, "a public candidate case was duplicated")
        seen.add((module, case))
        require(row.get("cohort") == "calibration", "a non-public workload entered the chart")
        require(row.get("api") in API_COUNTS, "an unrecognized public workload family entered the chart")
        require(row.get("lifecycle") in LIFETIME_COUNTS, "a public pattern lifetime was substituted")
        require(row.get("input") in INPUT_COUNTS, "a public input family was substituted")
        require(row.get("result_density") in DENSITY_COUNTS, "a public result family was substituted")
        require(type(row.get("weight")) is int and row.get("weight") == 1, "a public case was reweighted")

        speed = finite(row.get("speedup"), f"{case} speed")
        low = finite(row.get("ci95_low"), f"{case} confidence lower bound")
        high = finite(row.get("ci95_high"), f"{case} confidence upper bound")
        require(low <= speed <= high, f"{case} has an invalid confidence range")
        baseline_ns = finite(row.get("baseline_ns"), f"{case} CPython time")
        finite(row.get("candidate_ns"), f"{case} candidate time")
        finite(row.get("peak_traced_ratio"), f"{case} Python-traced allocation", allow_zero=True)

        faster = row.get("statistically_faster")
        slower = row.get("regression_gt_20pct")
        require(isinstance(faster, bool) and faster == (low > 1), f"{case} invents a confidence-supported win")
        require(isinstance(slower, bool) and slower == (speed < threshold), f"{case} hides or invents a substantial slowdown")

        if case in baseline_by_case:
            same_float(baseline_ns, baseline_by_case[case], f"{case} does not use the shared CPython baseline")
            require(category_by_case[case] == category, f"{case} changes its shared workload category")
        else:
            baseline_by_case[case] = baseline_ns
            category_by_case[case] = category
        by_module[module].append(row)

    require(len(baseline_by_case) == CASES, "the four engines did not share all 624 public cases")
    require(
        len(set(category_by_case.values())) == PUBLIC_CATEGORIES,
        "one or more of the 260 public workload categories was removed",
    )
    expected_cases = frozenset(baseline_by_case)
    measured_losses: list[dict] = []
    results: list[CandidateResult] = []

    for module in CANDIDATES:
        rows = tuple(by_module[module])
        label = DISPLAY[module]
        require(len(rows) == CASES, f"{label} is not represented on all 624 cases")
        require(frozenset(row["case"] for row in rows) == expected_cases, f"{label} used a different public workload")
        require(dict(Counter(row["api"] for row in rows)) == API_COUNTS, f"{label} changed a workload-family denominator")
        require(
            dict(Counter(f"{row['api']} / {row['lifecycle']}" for row in rows)) == API_LIFETIMES,
            f"{label} changed a public operation or pattern lifetime",
        )
        require(dict(Counter(row["input"] for row in rows)) == INPUT_COUNTS, f"{label} changed an input denominator")
        require(dict(Counter(row["lifecycle"] for row in rows)) == LIFETIME_COUNTS, f"{label} changed a pattern-lifetime denominator")
        require(dict(Counter(row["result_density"] for row in rows)) == DENSITY_COUNTS, f"{label} changed a result-density denominator")

        ranking = ranking_by_module[module]
        same_float(
            geometric(rows),
            finite(ranking.get("geomean_speedup"), f"{label} overall development speed"),
            f"{label} omits or reweights a public case",
        )
        clearly_faster = sum(row["statistically_faster"] for row in rows)
        losses = [row for row in rows if row["regression_gt_20pct"]]
        require(
            type(ranking.get("statistically_faster_cases")) is int
            and ranking.get("statistically_faster_cases") == clearly_faster,
            f"{label} invents or drops a confidence-supported development win",
        )
        require(
            type(ranking.get("regressions_gt_20pct")) is int
            and ranking.get("regressions_gt_20pct") == len(losses),
            f"{label} hides a more-than-20% public slowdown",
        )
        measured_losses.extend(losses)
        results.append(CandidateResult(module=module, ranking=ranking, rows=rows))

    reported_losses = summary.get("regressions")
    require(
        isinstance(reported_losses, list),
        "the complete set of post-final public slowdowns is NOT MEASURED",
    )
    require(all(isinstance(row, dict) for row in reported_losses), "a public slowdown record is invalid")
    loss_key = lambda row: (row.get("candidate", ""), row.get("case", ""))
    require(
        sorted(reported_losses, key=loss_key) == sorted(measured_losses, key=loss_key),
        "a substantial public slowdown was omitted, duplicated, or altered",
    )
    require(
        len(measured_losses) == len(reported_losses),
        "the post-final public slowdown denominator changed",
    )

    ordered = tuple(
        sorted(
            results,
            key=lambda result: (-result.ranking["geomean_speedup"], DISPLAY[result.module]),
        )
    )
    return PublicResults(
        summary=summary,
        candidates=ordered,
        summary_sha256=summary_sha256,
    )


def decode_public_summary(
    payload: bytes, *, expected_sha256: str | None = None
) -> PublicResults:
    actual_sha256 = hashlib.sha256(payload).hexdigest()
    if expected_sha256 is not None:
        require(valid_sha256(expected_sha256), "the supplied public summary fingerprint is invalid")
        require(
            actual_sha256 == expected_sha256,
            "the post-final public summary does not match its supplied SHA-256",
        )
    try:
        document = json.loads(payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("the frozen public development summary is not valid UTF-8 JSON") from error
    return validate_public_summary(document, summary_sha256=actual_sha256)


def load_public_summary(
    path: Path, *, expected_sha256: str | None = None
) -> PublicResults:
    require(
        path.resolve() == PUBLIC_SUMMARY.resolve(),
        "only the exact postfinal-rust-batched-split-01 public summary may be read",
    )
    try:
        payload = PUBLIC_SUMMARY.read_bytes()
    except OSError as error:
        raise ValueError("the post-final public development summary is NOT MEASURED") from error
    return decode_public_summary(payload, expected_sha256=expected_sha256)


def verify_final_failure() -> None:
    for path, expected, label in (
        (FINAL_FAILURE_REPORT, FINAL_FAILURE_REPORT_SHA256, "published final failure report"),
        (
            FINAL_FAILURE_CERTIFICATE,
            FINAL_FAILURE_CERTIFICATE_SHA256,
            "published independent final failure certificate",
        ),
    ):
        try:
            payload = path.read_bytes()
        except OSError as error:
            raise ValueError(f"the {label} is missing; final success cannot be claimed") from error
        require(
            hashlib.sha256(payload).hexdigest() == expected,
            f"the SHA-256-pinned {label} changed; final success cannot be claimed",
        )


def load_public_integrity(
    path: Path,
    results: PublicResults,
    *,
    expected_sha256: str | None = None,
) -> str:
    require(
        path.resolve() == PUBLIC_INTEGRITY.resolve(),
        "only the exact postfinal-rust-batched-split-01 public integrity report may be read",
    )
    try:
        payload = PUBLIC_INTEGRITY.read_bytes()
        document = json.loads(payload.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("the post-final public integrity report is NOT MEASURED") from error
    actual_sha256 = hashlib.sha256(payload).hexdigest()
    if expected_sha256 is not None:
        require(valid_sha256(expected_sha256), "the supplied public integrity fingerprint is invalid")
        require(actual_sha256 == expected_sha256, "the public integrity report SHA-256 changed")
    require(isinstance(document, dict), "the public integrity report is not a JSON object")
    require(
        document.get("result", document.get("status")) == "PASS",
        "the independent post-final public results audit did not pass",
    )
    require(
        document.get("summary_sha256") == results.summary_sha256,
        "the public results audit does not bind the exact rendered post-final summary",
    )
    if "holdout_accessed" in document:
        require(
            document["holdout_accessed"] is False,
            "the public results audit does not establish final-test isolation",
        )
    observed_losses = sum(
        result.ranking["regressions_gt_20pct"] for result in results.candidates
    )
    optional_checks = {
        "module_order": list(MODULES),
        "cases_per_candidate": CASES,
        "candidate_case_count": CASES * len(CANDIDATES),
        "trials_per_module_case": TRIALS,
        "raw_rows": PAIRED_ROWS,
        "correctness_checks": CORRECTNESS_CHECKS,
        "bootstrap_draws": BOOTSTRAPS,
        "strict_regressions": observed_losses,
        "exclusive_slot": PUBLIC_SLOT,
    }
    for key, expected in optional_checks.items():
        if key in document:
            require(
                document[key] == expected and type(document[key]) is type(expected),
                f"the public results audit changes the measured {key}",
            )
    if "native_elf_fingerprints" in document:
        measured = results.summary["candidate_binary_sha256_before"]
        expected_native = {
            role: digest
            for role, digest in measured.items()
            if role.endswith(":native-engine") or role.endswith(":native-bridge")
        }
        require(
            document["native_elf_fingerprints"] == expected_native,
            "the public results audit does not bind the measured native candidates",
        )
    return actual_sha256


def fmt(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}×"


def svg_open(
    width: int,
    height: int,
    title: str,
    subtitle: str,
    *,
    source_sha256: str,
) -> list[str]:
    require(valid_sha256(source_sha256), "the chart has no verified public summary fingerprint")
    description = (
        f"{BANNER}. CPython (standard Python), C, Rust, and Zig share the same "
        f"{CASES} public development cases and {TRIALS} paired measurements. "
        f"{subtitle}. Source: {PUBLIC_SUMMARY.name}; SHA-256 {source_sha256}. "
        f"{FINAL_STATUS}"
    )
    return [
        (
            f'<svg xmlns="{SVG_NAMESPACE}" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" '
            'aria-labelledby="postfinal-chart-title postfinal-chart-description">'
        ),
        f'<title id="postfinal-chart-title">{escape(title)}</title>',
        f'<desc id="postfinal-chart-description">{escape(description)}</desc>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        (
            '<style>'
            'text{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;'
            'fill:#172033}'
            '.title{font-size:32px;font-weight:760}'
            '.subtitle{font-size:17px;fill:#475569}'
            '.heading{font-size:20px;font-weight:720}'
            '.label{font-size:15px;fill:#263449}'
            '.value{font-size:16px;font-weight:720}'
            '.note{font-size:15px;fill:#475569}'
            '.tick{font-size:14px;fill:#475569}'
            '.banner{font-size:17px;font-weight:740;fill:#7f1d1d}'
            '.status{font-size:15px;font-weight:680;fill:#7f1d1d}'
            '.grid{stroke:#e2e8f0;stroke-width:1}'
            '.baseline{stroke:#64748b;stroke-width:2.2}'
            '.panel{fill:#f8fafc;stroke:#d9e2ee;stroke-width:1}'
            '</style>'
        ),
        f'<text x="30" y="49" class="title">{escape(title)}</text>',
        f'<text x="31" y="83" class="subtitle">{escape(subtitle)}</text>',
        f'<rect x="23" y="103" width="{width - 46}" height="49" rx="9" fill="#fef2f2" stroke="#fca5a5"/>',
        f'<text x="38" y="135" class="banner">{escape(BANNER)}</text>',
        f'<text x="32" y="181" class="status">{escape(FINAL_STATUS)}</text>',
        (
            f'<text x="32" y="207" class="note">Source: {escape(PUBLIC_SUMMARY.name)}; '
            f'SHA-256 {escape(source_sha256)}</text>'
        ),
    ]


def svg_close(body: list[str]) -> str:
    return "\n".join((*body, "</svg>", ""))


def log_x(value: float, left: int, right: int, lower: float, upper: float) -> float:
    require(0 < lower <= value <= upper, "a measured speed falls outside its chart axis")
    require(left < right and lower < upper, "invalid public speed chart axis")
    return left + (math.log(value) - math.log(lower)) / (math.log(upper) - math.log(lower)) * (right - left)


def speed_axis(
    body: list[str],
    *,
    left: int,
    right: int,
    top: int,
    bottom: int,
    lower: float,
    upper: float,
) -> None:
    ticks = (
        (0.25, "0.25×"),
        (0.5, "0.5×"),
        (0.75, "0.75×"),
        (1.0, "1× CPython"),
        (1.25, "1.25×"),
        (1.5, "1.5×"),
        (2.0, "2×"),
        (3.0, "3×"),
        (4.0, "4×"),
        (8.0, "8×"),
    )
    for value, label in ticks:
        if lower <= value <= upper:
            x = log_x(value, left, right, lower, upper)
            style = "baseline" if value == 1 else "grid"
            body.append(f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{bottom}" class="{style}"/>')
            body.append(f'<text x="{x:.2f}" y="{top - 10}" text-anchor="middle" class="tick">{escape(label)}</text>')


def legend(body: list[str], results: PublicResults, *, x: int, y: int) -> None:
    position = x
    modules = (BASELINE, *(result.module for result in results.candidates))
    for module in modules:
        label = DISPLAY[module]
        body.append(f'<circle cx="{position}" cy="{y - 5}" r="6" fill="{COLOURS[module]}"/>')
        body.append(f'<text x="{position + 13}" y="{y}" class="label">{escape(label)}</text>')
        position += 278 if module == BASELINE else 108


def grouped(result: CandidateResult) -> dict[str, tuple[dict, ...]]:
    groups = {
        api: tuple(row for row in result.rows if row["api"] == api)
        for api in API_COUNTS
    }
    for api, rows in groups.items():
        require(len(rows) == API_COUNTS[api], "a graph omitted a public workload-family case")
    return groups


def overall_chart(results: PublicResults) -> str:
    width, height = 1560, 638
    left, right = 344, 914
    values = [1.0]
    for result in results.candidates:
        values.extend((result.ranking["ci95_low"], result.ranking["ci95_high"]))
    lower = min(0.70, min(values) * 0.94)
    upper = max(1.65, max(values) * 1.08)
    body = svg_open(
        width,
        height,
        "Public development speed compared with CPython",
        f"All four engines; the same {CASES} public cases; {TRIALS} paired runs; measured 95% confidence ranges",
        source_sha256=results.summary_sha256,
    )
    speed_axis(body, left=left, right=right, top=252, bottom=543, lower=lower, upper=upper)
    baseline_x = log_x(1.0, left, right, lower, upper)
    baseline_y = 277
    body.extend(
        (
            f'<text x="31" y="{baseline_y + 6}" class="heading">{escape(DISPLAY[BASELINE])}</text>',
            f'<circle cx="{baseline_x:.2f}" cy="{baseline_y}" r="8" fill="{COLOURS[BASELINE]}" stroke="#ffffff" stroke-width="2"/>',
            f'<text x="938" y="{baseline_y + 5}" class="value">Exactly 1.000×; neutral baseline; {CASES}/{CASES} cases</text>',
        )
    )
    for index, result in enumerate(results.candidates):
        y = 350 + index * 86
        ranking = result.ranking
        low = ranking["ci95_low"]
        point = ranking["geomean_speedup"]
        high = ranking["ci95_high"]
        colour = COLOURS[result.module]
        interpretation = (
            "Clearly faster than CPython in public development"
            if low > 1
            else "Clearly slower than CPython in public development"
            if high < 1
            else "No clear overall difference from CPython in public development"
        )
        body.extend(
            (
                f'<text x="31" y="{y + 6}" class="heading">{escape(DISPLAY[result.module])}</text>',
                f'<line x1="{log_x(low, left, right, lower, upper):.2f}" y1="{y}" x2="{log_x(high, left, right, lower, upper):.2f}" y2="{y}" stroke="{colour}" stroke-width="8" stroke-linecap="round"/>',
                f'<circle cx="{log_x(point, left, right, lower, upper):.2f}" cy="{y}" r="8" fill="{colour}" stroke="#ffffff" stroke-width="2"/>',
                f'<text x="938" y="{y - 13}" class="value">{fmt(point)}; 95% range {fmt(low)} to {fmt(high)}</text>',
                f'<text x="938" y="{y + 10}" class="note">{escape(interpretation)}</text>',
                f'<text x="938" y="{y + 32}" class="note">{ranking["statistically_faster_cases"]}/{CASES} clear case wins; {ranking["regressions_gt_20pct"]}/{CASES} substantial slowdowns</text>',
            )
        )
    body.append(
        '<text x="31" y="603" class="note">Each confidence range compares one engine with CPython only; it does not prove a difference between candidate engines.</text>'
    )
    return svg_close(body)


def stacked_bar(
    body: list[str],
    *,
    left: int,
    right: int,
    y: int,
    parts: tuple[tuple[int, str], ...],
) -> None:
    require(sum(count for count, _ in parts) == CASES, "an outcome chart changed the 624-case denominator")
    position = float(left)
    for count, colour in parts:
        bar_width = (right - left) * count / CASES
        if count:
            body.append(f'<rect x="{position:.2f}" y="{y}" width="{bar_width:.2f}" height="25" fill="{colour}"/>')
            if bar_width >= 42:
                body.append(
                    f'<text x="{position + bar_width / 2:.2f}" y="{y + 18}" text-anchor="middle" '
                    f'style="font-size:14px;font-weight:740;fill:#ffffff">{count}</text>'
                )
        position += bar_width


def outcomes_chart(results: PublicResults) -> str:
    width, left, right = 1560, 391, 1263
    panel_height = 228
    height = 250 + panel_height * len(results.candidates) + 54
    body = svg_open(
        width,
        height,
        "Every public development win, uncertainty, and loss",
        f"Every engine keeps all {CASES} public cases; measured outcomes and confidence-supported outcomes are shown separately",
        source_sha256=results.summary_sha256,
    )
    legend(body, results, x=391, y=223)
    for index, result in enumerate(results.candidates):
        top = 251 + index * panel_height
        rows = result.rows
        raw_faster = sum(row["speedup"] > 1 for row in rows)
        raw_slower = sum(row["speedup"] < 1 for row in rows)
        raw_equal = CASES - raw_faster - raw_slower
        faster = sum(row["ci95_low"] > 1 for row in rows)
        slower = sum(row["ci95_high"] < 1 for row in rows)
        uncertain = CASES - faster - slower
        losses = result.ranking["regressions_gt_20pct"]
        body.append(f'<rect x="22" y="{top - 17}" width="{width - 44}" height="{panel_height - 13}" rx="10" class="panel"/>')
        body.append(f'<text x="37" y="{top + 12}" class="heading">{escape(DISPLAY[result.module])}: all {CASES}/{CASES} public cases</text>')

        body.append(f'<text x="37" y="{top + 55}" class="label">Measured case outcomes</text>')
        stacked_bar(
            body,
            left=left,
            right=right,
            y=top + 35,
            parts=((raw_faster, "#047857"), (raw_equal, "#64748b"), (raw_slower, "#dc2626")),
        )
        body.append(f'<text x="{right + 15}" y="{top + 54}" class="value">{CASES}/{CASES}</text>')
        body.append(
            f'<text x="{left}" y="{top + 82}" class="note">{raw_faster}/{CASES} faster; '
            f'{raw_equal}/{CASES} equal; {raw_slower}/{CASES} slower</text>'
        )

        body.append(f'<text x="37" y="{top + 113}" class="label">95%-confidence outcomes</text>')
        stacked_bar(
            body,
            left=left,
            right=right,
            y=top + 93,
            parts=((faster, "#047857"), (uncertain, "#64748b"), (slower, "#dc2626")),
        )
        body.append(f'<text x="{right + 15}" y="{top + 112}" class="value">{CASES}/{CASES}</text>')
        body.append(
            f'<text x="{left}" y="{top + 139}" class="note">{faster}/{CASES} clearly faster; '
            f'{uncertain}/{CASES} uncertain; {slower}/{CASES} clearly slower</text>'
        )

        body.append(f'<text x="37" y="{top + 174}" class="label">More than 20% longer</text>')
        body.append(f'<rect x="{left}" y="{top + 154}" width="{right - left}" height="25" fill="#fee2e2"/>')
        body.append(f'<rect x="{left}" y="{top + 154}" width="{(right - left) * losses / CASES:.2f}" height="25" fill="#dc2626"/>')
        body.append(f'<text x="{right + 15}" y="{top + 173}" class="value">{losses}/{CASES}</text>')
        body.append(
            f'<text x="{left}" y="{top + 202}" class="note">Substantial slowdowns are a separate timing rule and are never removed from the confidence outcomes.</text>'
        )
    body.append(
        f'<text x="31" y="{height - 20}" class="note">All {len(results.summary["regressions"])} recorded substantial public-development slowdowns remain visible; final outcomes are NOT MEASURED.</text>'
    )
    return svg_close(body)


def api_chart(results: PublicResults) -> str:
    width, left, right = 1560, 454, 1007
    top, row_height = 275, 53
    height = top + len(API_COUNTS) * row_height + 90
    grouped_results = {result.module: grouped(result) for result in results.candidates}
    points = [
        geometric(grouped_results[result.module][api])
        for result in results.candidates
        for api in API_COUNTS
    ]
    lower = min(0.48, min(points) * 0.91)
    upper = max(2.05, max(points) * 1.09)
    body = svg_open(
        width,
        height,
        "All public regular-expression workload families",
        "All 12 measured public operations; family averages are not confidence intervals",
        source_sha256=results.summary_sha256,
    )
    legend(body, results, x=454, y=224)
    speed_axis(
        body,
        left=left,
        right=right,
        top=top,
        bottom=top + len(API_COUNTS) * row_height,
        lower=lower,
        upper=upper,
    )
    for index, (api, count) in enumerate(API_COUNTS.items()):
        y = top + 28 + index * row_height
        body.append(
            f'<text x="31" y="{y + 5}" class="label">{escape(API_LABELS[api])} '
            f'({escape(api)}); {count}/{count} cases</text>'
        )
        for offset, result in enumerate(results.candidates):
            speed = geometric(grouped_results[result.module][api])
            cy = y + (offset - 1) * 11
            colour = COLOURS[result.module]
            body.append(
                f'<circle cx="{log_x(speed, left, right, lower, upper):.2f}" cy="{cy}" '
                f'r="5.6" fill="{colour}" stroke="#ffffff" stroke-width="1.2"/>'
            )
            body.append(
                f'<text x="{1031 + offset * 165}" y="{y + 5}" class="label">'
                f'{escape(DISPLAY[result.module])} {fmt(speed)}</text>'
            )
    body.append(
        f'<text x="31" y="{height - 47}" class="note">Each family uses its full frozen case count for CPython, C, Rust, and Zig; all {CASES} public cases are retained.</text>'
    )
    body.append(
        '<text x="31" y="' + str(height - 22) + '" class="note">Dots show public geometric means only; no workload-family confidence interval or candidate-to-candidate significance is claimed.</text>'
    )
    return svg_close(body)


def regressions_chart(results: PublicResults) -> str:
    width = 1560
    observed_loss_count = len(results.summary["regressions"])
    individual_height, family_height = 26, 30
    panel_gap, panel_header = 20, 57
    panel_heights = [
        panel_header
        + len(API_COUNTS) * family_height
        + result.ranking["regressions_gt_20pct"] * individual_height
        + 15
        for result in results.candidates
    ]
    height = 248 + sum(panel_heights) + panel_gap * (len(panel_heights) - 1) + 54
    body = svg_open(
        width,
        height,
        "Every individual public slowdown of more than 20%",
        f"All {observed_loss_count} measured public slowdowns; every case name and all 12 workload-family denominators",
        source_sha256=results.summary_sha256,
    )
    legend(body, results, x=424, y=225)
    losses = [row for result in results.candidates for row in result.rows if row["regression_gt_20pct"]]
    require(len(losses) == observed_loss_count, "the individual slowdown graph omitted a public loss")
    maximum_percent = max(
        ((1 / row["speedup"] - 1) * 100 for row in losses),
        default=20.0,
    )
    require(
        not losses or maximum_percent > 20,
        "the individual slowdown graph has no measured substantial loss",
    )

    y = 249
    shown: set[tuple[str, str]] = set()
    for result, panel_height in zip(results.candidates, panel_heights, strict=True):
        groups = grouped(result)
        body.append(f'<rect x="22" y="{y - 15}" width="{width - 44}" height="{panel_height}" rx="10" class="panel"/>')
        total = result.ranking["regressions_gt_20pct"]
        body.append(
            f'<text x="38" y="{y + 15}" class="heading">{escape(DISPLAY[result.module])}: '
            f'{total}/{CASES} public cases took more than 20% longer than CPython</text>'
        )
        cursor = y + 46
        for api, denominator in API_COUNTS.items():
            family_losses = tuple(
                sorted(
                    (row for row in groups[api] if row["regression_gt_20pct"]),
                    key=lambda row: row["case"],
                )
            )
            body.append(
                f'<text x="40" y="{cursor + 15}" class="value">{escape(API_LABELS[api])} '
                f'({escape(api)}): {len(family_losses)}/{denominator}</text>'
            )
            cursor += family_height
            for row in family_losses:
                identity = (result.module, row["case"])
                require(identity not in shown, "an individual public slowdown was duplicated")
                shown.add(identity)
                percent = (1 / row["speedup"] - 1) * 100
                require(percent > 20, "the slowdown chart includes a case that is not more than 20% slower")
                bar_width = 254 * math.log1p(percent) / math.log1p(maximum_percent)
                body.extend(
                    (
                        f'<text x="56" y="{cursor + 16}" class="label">{escape(row["case"])}</text>',
                        f'<text x="846" y="{cursor + 16}" class="value">{fmt(row["speedup"])}</text>',
                        f'<text x="972" y="{cursor + 16}" class="label">{percent:.1f}% longer</text>',
                        f'<rect x="1219" y="{cursor + 3}" width="254" height="17" rx="4" fill="#fee2e2"/>',
                        f'<rect x="1219" y="{cursor + 3}" width="{bar_width:.2f}" height="17" rx="4" fill="#dc2626"/>',
                    )
                )
                cursor += individual_height
        require(
            cursor == y + 46 + len(API_COUNTS) * family_height + total * individual_height,
            "an individual public slowdown panel silently changed its denominator",
        )
        y += panel_height + panel_gap

    require(
        len(shown) == observed_loss_count,
        "the graph does not show every measured individual post-final public slowdown",
    )
    expected = {(row["candidate"], row["case"]) for row in results.summary["regressions"]}
    require(shown == expected, "an original public slowdown is absent from the individual graph")
    body.append(
        f'<text x="31" y="{height - 22}" class="note">All {observed_loss_count} measured post-final public case records are shown; the bars use a zero-preserving logarithmic visual scale.</text>'
    )
    return svg_close(body)


def linear_memory_x(value: float, left: int, right: int, upper: float) -> float:
    require(0 <= value <= upper and upper > 0, "a Python-traced measurement is missing or clipped")
    return left + (right - left) * value / upper


def memory_axis(body: list[str], *, left: int, right: int, top: int, bottom: int, upper: float) -> None:
    for value, label in (
        (0.0, "0×"),
        (0.25, "0.25×"),
        (0.5, "0.5×"),
        (0.75, "0.75×"),
        (1.0, "1× CPython"),
        (1.5, "1.5×"),
        (2.0, "2×"),
        (3.0, "3×"),
        (4.0, "4×"),
        (6.0, "6×"),
    ):
        if value <= upper:
            x = linear_memory_x(value, left, right, upper)
            style = "baseline" if value == 1 else "grid"
            body.append(f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{bottom}" class="{style}"/>')
            body.append(f'<text x="{x:.2f}" y="{top - 9}" text-anchor="middle" class="tick">{escape(label)}</text>')


def memory_chart(results: PublicResults) -> str:
    width, left, right = 1560, 426, 1029
    row_height, panel_height = 35, 509
    height = 260 + panel_height * len(results.candidates) + 74
    all_groups = {result.module: grouped(result) for result in results.candidates}
    medians = [
        float(statistics.median(row["peak_traced_ratio"] for row in all_groups[result.module][api]))
        for result in results.candidates
        for api in API_COUNTS
    ]
    upper = max(1.75, max(medians, default=1.0) * 1.11)
    body = svg_open(
        width,
        height,
        "Measured Python-traced public-practice allocations",
        "Python-traced temporary allocations only; lower is better; zero remains visible; final and native memory are NOT MEASURED",
        source_sha256=results.summary_sha256,
    )
    legend(body, results, x=426, y=226)
    for index, result in enumerate(results.candidates):
        top = 261 + index * panel_height
        overall = float(statistics.median(row["peak_traced_ratio"] for row in result.rows))
        zero_total = sum(row["peak_traced_ratio"] == 0 for row in result.rows)
        body.append(f'<rect x="22" y="{top - 17}" width="{width - 44}" height="{panel_height - 12}" rx="10" class="panel"/>')
        body.append(
            f'<text x="38" y="{top + 13}" class="heading">{escape(DISPLAY[result.module])}: '
            f'{fmt(overall)} median Python-traced ratio; {zero_total}/{CASES} measured zero-traced cases</text>'
        )
        axis_top = top + 50
        memory_axis(
            body,
            left=left,
            right=right,
            top=axis_top,
            bottom=top + 66 + len(API_COUNTS) * row_height,
            upper=upper,
        )
        for offset, (api, denominator) in enumerate(API_COUNTS.items()):
            family = all_groups[result.module][api]
            y = top + 77 + offset * row_height
            median = float(statistics.median(row["peak_traced_ratio"] for row in family))
            zeros = sum(row["peak_traced_ratio"] == 0 for row in family)
            body.extend(
                (
                    f'<text x="38" y="{y + 5}" class="label">{escape(API_LABELS[api])} ({escape(api)})</text>',
                    f'<circle cx="{linear_memory_x(median, left, right, upper):.2f}" cy="{y}" r="6" '
                    f'fill="{COLOURS[result.module]}" stroke="#ffffff" stroke-width="1.3"/>',
                    f'<text x="{right + 18}" y="{y + 5}" class="value">{fmt(median)}</text>',
                    f'<text x="{right + 114}" y="{y + 5}" class="label">{denominator}/{denominator} cases; {zeros} zero-traced</text>',
                )
            )
    body.append(
        f'<text x="31" y="{height - 48}" class="note">Only Python-visible temporary allocations were measured in a shared development process; isolated native, total, and whole-process memory: NOT MEASURED.</text>'
    )
    body.append(
        f'<text x="31" y="{height - 22}" class="note">Zero Python-traced allocations do not mean zero native or total memory. Complete final-benchmark memory: NOT MEASURED.</text>'
    )
    return svg_close(body)


def rankings_chart(results: PublicResults) -> str:
    width, left, right = 1560, 318, 852
    top, row_height = 265, 76
    height = top + len(MODULES) * row_height + 104
    values = [1.0]
    for result in results.candidates:
        values.extend((result.ranking["ci95_low"], result.ranking["ci95_high"]))
    lower = min(0.70, min(values) * 0.94)
    upper = max(1.65, max(values) * 1.08)
    body = svg_open(
        width,
        height,
        "Public development ordering only — not a final ranking",
        f"Four-way public comparison on the same {CASES} cases; no final winner and no candidate-to-candidate confidence claim",
        source_sha256=results.summary_sha256,
    )
    speed_axis(
        body,
        left=left,
        right=right,
        top=top + 22,
        bottom=top + len(MODULES) * row_height - 8,
        lower=lower,
        upper=upper,
    )
    body.append(f'<text x="876" y="{top + 8}" class="label">Public speed and 95% range</text>')
    body.append(f'<text x="1252" y="{top + 8}" class="label">Clear wins</text>')
    body.append(f'<text x="1390" y="{top + 8}" class="label">&gt;20% slower</text>')

    ordered: list[tuple[float, str, CandidateResult | None]] = [
        (result.ranking["geomean_speedup"], result.module, result)
        for result in results.candidates
    ]
    ordered.append((1.0, BASELINE, None))
    ordered.sort(key=lambda item: (-item[0], DISPLAY[item[1]]))
    require(len(ordered) == len(MODULES), "the four-way public development ranking is incomplete")

    for index, (_, module, result) in enumerate(ordered):
        y = top + 52 + index * row_height
        colour = COLOURS[module]
        body.append(f'<text x="31" y="{y + 6}" class="heading">{index + 1}. {escape(DISPLAY[module])}</text>')
        if result is None:
            x = log_x(1.0, left, right, lower, upper)
            body.extend(
                (
                    f'<circle cx="{x:.2f}" cy="{y}" r="7" fill="{colour}" stroke="#ffffff" stroke-width="1.5"/>',
                    f'<text x="876" y="{y + 5}" class="value">Exactly 1.000×; neutral baseline</text>',
                    f'<text x="1252" y="{y + 5}" class="label">Baseline</text>',
                    f'<text x="1390" y="{y + 5}" class="label">Baseline</text>',
                )
            )
            continue

        ranking = result.ranking
        low, point, high = (
            ranking["ci95_low"],
            ranking["geomean_speedup"],
            ranking["ci95_high"],
        )
        body.extend(
            (
                f'<line x1="{log_x(low, left, right, lower, upper):.2f}" y1="{y}" x2="{log_x(high, left, right, lower, upper):.2f}" y2="{y}" stroke="{colour}" stroke-width="7" stroke-linecap="round"/>',
                f'<circle cx="{log_x(point, left, right, lower, upper):.2f}" cy="{y}" r="7" fill="{colour}" stroke="#ffffff" stroke-width="1.5"/>',
                f'<text x="876" y="{y + 5}" class="value">{fmt(point)} [{fmt(low)} to {fmt(high)}]</text>',
                f'<text x="1252" y="{y + 5}" class="value">{ranking["statistically_faster_cases"]}/{CASES}</text>',
                f'<text x="1390" y="{y + 5}" class="value">{ranking["regressions_gt_20pct"]}/{CASES}</text>',
            )
        )
    body.append(
        f'<text x="31" y="{height - 48}" class="note">Ordering describes public-development point estimates only; overlapping ranges do not establish candidate-to-candidate significance.</text>'
    )
    body.append(
        f'<text x="31" y="{height - 22}" class="note">The independent final benchmark failed. A complete final ranking is NOT MEASURED; no candidate is the final winner.</text>'
    )
    return svg_close(body)


def validate_svg(svg: str, *, suffix: str, results: PublicResults) -> None:
    try:
        root = ElementTree.fromstring(svg)
    except ElementTree.ParseError as error:
        raise ValueError(f"the public {suffix} chart is not valid self-contained SVG") from error
    require(root.tag == f"{{{SVG_NAMESPACE}}}svg", f"the public {suffix} chart is not SVG")
    require(root.get("role") == "img", f"the public {suffix} chart has no accessible image role")
    require(
        root.get("aria-labelledby") == "postfinal-chart-title postfinal-chart-description",
        f"the public {suffix} chart has no accessible title and description",
    )
    title = root.find(f"{{{SVG_NAMESPACE}}}title")
    description = root.find(f"{{{SVG_NAMESPACE}}}desc")
    require(title is not None and bool(title.text), f"the public {suffix} chart has no accessible title")
    require(description is not None and bool(description.text), f"the public {suffix} chart has no accessible description")
    visible = " ".join(text for text in root.itertext() if text)
    require(BANNER in visible, f"the public {suffix} chart hides the final benchmark failure")
    require(FINAL_STATUS in visible, f"the public {suffix} chart invents a final result")
    require("CPython" in visible, f"the public {suffix} chart hides the neutral Python baseline")
    require("Rust" in visible and "Zig" in visible, f"the public {suffix} chart hides a native candidate")
    require(
        any(
            (node.text or "").strip() in ("C", "1. C", "2. C", "3. C", "4. C")
            or (node.text or "").strip().startswith("C:")
            or (node.text or "").strip().startswith("C ")
            for node in root.iter()
        ),
        f"the public {suffix} chart hides the C candidate",
    )
    require(str(CASES) in visible, f"the public {suffix} chart hides the fixed case denominator")
    require("NOT MEASURED" in visible, f"the public {suffix} chart hides an unavailable final measurement")
    require(root.find(f".//{{{SVG_NAMESPACE}}}script") is None, f"the public {suffix} chart contains an executable script")
    if suffix == "regressions":
        for result in results.candidates:
            for row in result.rows:
                if row["regression_gt_20pct"]:
                    require(row["case"] in visible, "an individual public slowdown is not visible")
    if suffix == "memory":
        require("Python-traced" in visible, "the memory graph does not identify Python tracing")
        require("native" in visible, "the memory graph does not identify unavailable native memory")
        require("0×" in visible, "the memory graph hides true zero Python-traced allocations")


def build_charts(results: PublicResults) -> dict[str, str]:
    charts = {
        "overall": overall_chart(results),
        "outcomes": outcomes_chart(results),
        "api": api_chart(results),
        "regressions": regressions_chart(results),
        "memory": memory_chart(results),
        "rankings": rankings_chart(results),
    }
    require(tuple(charts) == CHART_SUFFIXES, "a required four-way public development chart was removed")
    for suffix, svg in charts.items():
        validate_svg(svg, suffix=suffix, results=results)
    return charts


def expanded_counts(counts: dict[str, int]) -> tuple[str, ...]:
    values = tuple(value for value, count in counts.items() for _ in range(count))
    require(len(values) == CASES, "the synthetic public case denominator changed")
    return values


def synthetic_summary() -> dict:
    synthetic_clear_wins = {RUST: 310, C_ENGINE: 360, ZIG: 330}
    synthetic_large_losses = {RUST: 39, C_ENGINE: 27, ZIG: 33}
    synthetic_clearly_slower = {RUST: 180, C_ENGINE: 150, ZIG: 160}
    inputs = expanded_counts(INPUT_COUNTS)
    densities = expanded_counts(DENSITY_COUNTS)
    cases: list[tuple[str, str, str, str, str, str]] = []
    case_index = 0
    for api, count in API_COUNTS.items():
        lifetimes = tuple(
            lifetime
            for label, lifetime_count in API_LIFETIMES.items()
            for lifetime in [label.partition(" / ")[2]]
            if label.partition(" / ")[0] == api
            for _ in range(lifetime_count)
        )
        require(len(lifetimes) == count, "the synthetic public pattern-lifetime denominator changed")
        for lifetime in lifetimes:
            cases.append(
                (
                    f"cal.{api}.public.{case_index:03d}",
                    api,
                    lifetime,
                    inputs[case_index],
                    densities[case_index],
                    f"public-family-{case_index % PUBLIC_CATEGORIES:03d}",
                )
            )
            case_index += 1
    require(len(cases) == CASES, "the synthetic public workload does not contain 624 cases")

    fingerprints = {
        role: hashlib.sha256(role.encode("utf-8")).hexdigest()
        for role in sorted(ARTIFACT_ROLES)
    }
    summary: dict = {
        "schema": SUMMARY_SCHEMA,
        "cohort": "calibration",
        "holdout_accessed": False,
        "exclusive_slot": PUBLIC_SLOT,
        "failed": 0,
        "expected_sha256": PUBLIC_ANSWER_SHA256,
        "modules": list(MODULES),
        "cases": CASES,
        "trials": TRIALS,
        "warmups": WARMUPS,
        "bootstrap_samples": BOOTSTRAPS,
        "bootstrap_seed": 1_986_072_302,
        "order_seed": 1_986_072_301,
        "selection_seed": 1_986_072_311,
        "paired_raw_rows": PAIRED_ROWS,
        "correctness_checks": CORRECTNESS_CHECKS,
        "all_bounded_workload_categories": PUBLIC_CATEGORIES,
        "public_operations": dict(API_COUNTS),
        "api_lifetimes": dict(API_LIFETIMES),
        "inputs": dict(INPUT_COUNTS),
        "lifetimes": dict(LIFETIME_COUNTS),
        "result_densities": dict(DENSITY_COUNTS),
        "measurement": "synthetic public development practice only; no final measurement",
        "strict_regression_speedup_threshold": REGRESSION_THRESHOLD,
        "candidate_binary_sha256_before": dict(fingerprints),
        "candidate_binary_sha256_after": dict(fingerprints),
        "verified_edge_oracles": [
            {
                "module": module,
                "correctness_checks": EDGE_CHECKS,
                "script_sha256": ORACLE_SOURCE_SHA256,
                "actual_sha256": ORACLE_ANSWER_SHA256,
            }
            for module in CANDIDATES
        ],
        "case_results": [],
        "rankings": [],
        "regressions": [],
    }
    for module_index, module in enumerate(CANDIDATES):
        candidate_rows: list[dict] = []
        uncertain_count = (
            CASES - synthetic_clear_wins[module] - synthetic_clearly_slower[module]
        )
        for index, (case, api, lifetime, input_kind, density, category) in enumerate(cases):
            band = (index * 37 + module_index * 83) % CASES
            if band < synthetic_large_losses[module]:
                speed = 0.57 + (index % 11) * 0.018
            elif band < synthetic_clearly_slower[module]:
                speed = 0.855 + (index % 7) * 0.009
            elif band < synthetic_clearly_slower[module] + uncertain_count:
                speed = 0.98 + (index % 5) * 0.01
            else:
                speed = 1.10 + (index % 17) * 0.019 + module_index * 0.004
            low = speed * 0.96
            high = speed * 1.04
            baseline_ns = float(1_000 + index % 101)
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
                "input": input_kind,
                "lifecycle": lifetime,
                "peak_traced_ratio": (0.0, 0.32, 0.58, 0.83, 1.0, 1.37)[(index + module_index) % 6],
                "regression_gt_20pct": speed < REGRESSION_THRESHOLD,
                "result_density": density,
                "speedup": speed,
                "statistically_faster": low > 1,
                "weight": 1,
            }
            candidate_rows.append(row)
            summary["case_results"].append(row)
            if row["regression_gt_20pct"]:
                summary["regressions"].append(dict(row))

        point = geometric(candidate_rows)
        summary["rankings"].append(
            {
                "candidate": module,
                "cases": CASES,
                "ci95_high": point * 1.04,
                "ci95_low": point * 0.96,
                "cohort": "calibration",
                "geomean_speedup": point,
                "regressions_gt_20pct": sum(row["regression_gt_20pct"] for row in candidate_rows),
                "statistically_faster_cases": sum(row["statistically_faster"] for row in candidate_rows),
                "weight": CASES,
            }
        )
    return summary


def expect_rejection(summary: dict, mutation, label: str) -> None:
    altered = copy.deepcopy(summary)
    mutation(altered)
    try:
        validate_public_summary(altered)
    except (ValueError, TypeError):
        return
    raise ValueError(f"the isolated synthetic self-test accepted {label}")


def self_test() -> dict:
    summary = synthetic_summary()
    results = validate_public_summary(summary)
    charts = build_charts(results)
    second_charts = build_charts(results)
    require(charts == second_charts, "public chart generation is not deterministic")
    require(len(charts) == 6, "the isolated synthetic test did not generate all six charts")

    payload = json.dumps(summary, sort_keys=True, separators=(",", ":")).encode("utf-8")
    synthetic_digest = hashlib.sha256(payload).hexdigest()
    decoded = decode_public_summary(payload, expected_sha256=synthetic_digest)
    require(build_charts(decoded) == charts, "validated synthetic JSON changes the generated charts")
    try:
        decode_public_summary(payload + b" ", expected_sha256=synthetic_digest)
    except ValueError:
        pass
    else:
        raise ValueError("the isolated synthetic test accepted a changed public-summary fingerprint")

    mutations = (
        ("an accessed independent test", lambda value: value.__setitem__("holdout_accessed", True)),
        ("a failed public correctness check", lambda value: value.__setitem__("failed", 1)),
        ("a substituted development slot", lambda value: value.__setitem__("exclusive_slot", "substituted-public-slot")),
        ("a changed CPython baseline", lambda value: value["modules"].__setitem__(0, "substituted.baseline")),
        ("a changed 624-case denominator", lambda value: value.__setitem__("cases", CASES - 1)),
        ("a changed paired-trial denominator", lambda value: value.__setitem__("trials", TRIALS - 1)),
        ("a changed confidence protocol", lambda value: value.__setitem__("bootstrap_samples", BOOTSTRAPS - 1)),
        ("an invented final measurement", lambda value: value.__setitem__("measurement", "final speed result")),
        ("an invalid confidence seed", lambda value: value.__setitem__("bootstrap_seed", -1)),
        ("a changed substantial-slowdown threshold", lambda value: value.__setitem__("strict_regression_speedup_threshold", 0.8)),
        ("a dropped native-engine fingerprint", lambda value: value["candidate_binary_sha256_before"].pop(f"{RUST}:native-engine")),
        ("a changed measured engine", lambda value: value["candidate_binary_sha256_after"].__setitem__(f"{RUST}:native-engine", "0" * 64)),
        ("a dropped public correctness qualification", lambda value: value["verified_edge_oracles"].pop()),
        ("a substituted public correctness oracle", lambda value: value["verified_edge_oracles"][0].__setitem__("actual_sha256", "0" * 64)),
        ("a dropped public candidate case", lambda value: value["case_results"].pop()),
        ("a non-public case", lambda value: value["case_results"][0].__setitem__("case", "not-public.synthetic")),
        ("a duplicated public case", lambda value: value["case_results"][1].__setitem__("case", value["case_results"][0]["case"])),
        ("a changed shared CPython time", lambda value: value["case_results"][CASES].__setitem__("baseline_ns", 999_999.0)),
        ("a concealed workload family", lambda value: value["public_operations"].__setitem__("split", 46)),
        ("a changed pattern lifetime", lambda value: value["case_results"][0].__setitem__("lifecycle", "module")),
        ("a reweighted public case", lambda value: value["case_results"][0].__setitem__("weight", 2)),
        ("an invented clearly-faster case", lambda value: value["case_results"][0].__setitem__("statistically_faster", not value["case_results"][0]["statistically_faster"])),
        ("a concealed substantial slowdown", lambda value: value["case_results"][0].__setitem__("regression_gt_20pct", not value["case_results"][0]["regression_gt_20pct"])),
        ("an unavailable Python-traced measurement", lambda value: value["case_results"][0].__setitem__("peak_traced_ratio", None)),
        ("an invented negative Python-traced measurement", lambda value: value["case_results"][0].__setitem__("peak_traced_ratio", -1.0)),
        ("a dropped candidate ranking", lambda value: value["rankings"].pop()),
        ("an invalid confidence interval", lambda value: value["rankings"][0].__setitem__("ci95_low", value["rankings"][0]["ci95_high"] + 1)),
        ("an invented clear-win count", lambda value: value["rankings"][0].__setitem__("statistically_faster_cases", value["rankings"][0]["statistically_faster_cases"] + 1)),
        ("a hidden ranking slowdown", lambda value: value["rankings"][0].__setitem__("regressions_gt_20pct", value["rankings"][0]["regressions_gt_20pct"] - 1)),
        ("an omitted individual public slowdown", lambda value: value["regressions"].pop()),
        ("an altered individual public slowdown", lambda value: value["regressions"][0].__setitem__("speedup", 0.01)),
    )
    for label, mutation in mutations:
        expect_rejection(summary, mutation, label)

    try:
        load_public_summary(PUBLIC_SUMMARY.with_name("substituted-public-summary.json"))
    except ValueError:
        pass
    else:
        raise ValueError("the isolated synthetic test allowed an unapproved input path")

    return {
        "result": "PASS",
        "mode": "isolated public synthetic only; no on-disk benchmark input read",
        "charts": len(charts),
        "public_cases_per_engine": CASES,
        "public_candidates_including_cpython": len(MODULES),
        "individually_visible_synthetic_slowdowns": len(summary["regressions"]),
        "adversarial_rejections": len(mutations) + 2,
        "final_benchmark": "FAILED; final speed, final memory, and final ranking NOT MEASURED; no final winner",
    }


def render(
    summary: Path,
    output_dir: Path,
    *,
    summary_sha256: str | None = None,
    integrity: Path | None = None,
    integrity_sha256: str | None = None,
) -> dict:
    verify_final_failure()
    results = load_public_summary(summary, expected_sha256=summary_sha256)
    selected_integrity = integrity
    if selected_integrity is None and PUBLIC_INTEGRITY.is_file():
        selected_integrity = PUBLIC_INTEGRITY
    observed_integrity_sha256: str | None = None
    if selected_integrity is not None:
        observed_integrity_sha256 = load_public_integrity(
            selected_integrity,
            results,
            expected_sha256=integrity_sha256,
        )
    charts = build_charts(results)
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        written: list[dict[str, str]] = []
        for suffix in CHART_SUFFIXES:
            svg = charts[suffix]
            destination = output_dir / f"{OUTPUT_PREFIX}-{suffix}.svg"
            destination.write_text(svg, encoding="utf-8", newline="\n")
            written.append(
                {
                    "chart": suffix,
                    "path": str(destination.resolve()),
                    "sha256": hashlib.sha256(svg.encode("utf-8")).hexdigest(),
                }
            )
    except OSError as error:
        raise ValueError(f"cannot write the explicitly selected public chart output directory: {output_dir}") from error
    return {
        "result": "PASS",
        "measurement": "four-way public development only",
        "summary_sha256": results.summary_sha256,
        "public_integrity_sha256": observed_integrity_sha256,
        "final_failure_report_sha256": FINAL_FAILURE_REPORT_SHA256,
        "final_failure_certificate_sha256": FINAL_FAILURE_CERTIFICATE_SHA256,
        "public_cases_per_engine": CASES,
        "individually_visible_public_slowdowns": len(results.summary["regressions"]),
        "final_benchmark": "FAILED; final speed, final memory, and final ranking NOT MEASURED; no final winner",
        "charts": written,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Render six accessible four-way public-development charts after the "
            "failed independent final benchmark. No final benchmark artifact is read."
        )
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run a deterministic, in-memory, public-synthetic-only self-test",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        help="the exact postfinal-rust-batched-split-01 public development summary",
    )
    parser.add_argument(
        "--summary-sha256",
        help="optional independent SHA-256 binding for the completed public summary",
    )
    parser.add_argument(
        "--integrity",
        type=Path,
        help="the exact source-bound postfinal-rust-batched-split-01 public integrity report",
    )
    parser.add_argument(
        "--integrity-sha256",
        help="optional independent SHA-256 binding for the public integrity report",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="explicit destination directory for the six public-development SVG files",
    )
    args = parser.parse_args(argv)
    if args.self_test:
        if (
            args.summary is not None
            or args.output_dir is not None
            or args.summary_sha256 is not None
            or args.integrity is not None
            or args.integrity_sha256 is not None
        ):
            parser.error("--self-test is isolated and cannot be combined with on-disk inputs or outputs")
    elif args.summary is None or args.output_dir is None:
        parser.error("rendering requires both an explicit --summary and an explicit --output-dir")
    elif args.integrity_sha256 is not None and args.integrity is None:
        parser.error("--integrity-sha256 requires an explicit --integrity")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = (
            self_test()
            if args.self_test
            else render(
                args.summary,
                args.output_dir,
                summary_sha256=args.summary_sha256,
                integrity=args.integrity,
                integrity_sha256=args.integrity_sha256,
            )
        )
    except (OSError, ValueError, TypeError) as error:
        print(f"public-development chart rendering rejected: {error}")
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
