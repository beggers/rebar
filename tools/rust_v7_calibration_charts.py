#!/usr/bin/env python3
"""Draw honest, reproducible charts from sealed Rust practice results only."""

from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import json
import math
import statistics
from collections import Counter
from dataclasses import dataclass
from html import escape
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "performance" / "v7" / "evidence"
DEFAULT_SUMMARY = EVIDENCE / "rust-v7-calibration-corrected-v4-baseline-summary.json"
SUMMARY_SCHEMA = "rebar-rust-balanced-calibration-pilot-v7"
ORACLE_SCHEMA = "rebar-v7-independent-edge-oracle-v1"
PRACTICE_SHA256 = "2e6c098bd3a4757620461363106a9795f8defa98fe8bc9c13c0ebbf7ed58b598"
ORACLE_SCRIPT_SHA256 = "fe6a263a48f243ea02faaa78fc3bbd051233a2b2221967a5f76dd1bb79d242ca"
ORACLE_EXPECTED_SHA256 = "b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526"
CASES = 624
TRIALS = 7
ORACLE_CHECKS = 223_198
RUST_MODULE = "candidates.rust_candidate"
ROLE_KEYS = {
    "public-python": "module",
    "native-bridge": "native-bridge",
    "native-engine": "native-engine",
    "native-source": "native-source",
    "bridge-source": "bridge-source",
}
API_LABELS = {
    "compile": "Prepare a pattern",
    "escape": "Escape special characters",
    "findall": "Find every match",
    "finditer": "Stream each match",
    "fullmatch": "Match the entire input",
    "match": "Match at the beginning",
    "match-surface": "Read the match details",
    "scanner": "Scan repeated matches",
    "search": "Search for a match",
    "split": "Split around matches",
    "sub": "Replace matches",
    "subn": "Replace and count matches",
}
PURPLE = "#7c3aed"
GREEN = "#047857"
RED = "#dc2626"
AMBER = "#b45309"
GREY = "#64748b"
GRID = "#e2e8f0"


@dataclass(frozen=True)
class PracticeResult:
    path: Path
    payload: dict
    ranking: dict
    rows: tuple[dict, ...]
    label: str


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def finite(value: object, label: str, *, positive: bool = True) -> float:
    require(isinstance(value, (int, float)) and not isinstance(value, bool), f"invalid {label}")
    number = float(value)
    require(math.isfinite(number), f"non-finite {label}")
    require(number > 0 if positive else number >= 0, f"out-of-range {label}")
    return number


def geometric(rows: tuple[dict, ...] | list[dict], key: str = "speedup") -> float:
    require(bool(rows), "cannot omit a practice group")
    return math.exp(math.fsum(math.log(finite(row[key], key)) for row in rows) / len(rows))


def architecture_name(path: Path) -> str:
    slug = path.name
    prefix = "rust-v7-calibration-"
    suffix = "-summary.json"
    require(slug.startswith(prefix) and slug.endswith(suffix), "unfrozen practice summary filename")
    slug = slug[len(prefix) : -len(suffix)]
    if slug == "corrected-v4-baseline":
        return "Corrected Rust baseline"
    words = slug.replace("-", " ").strip()
    require(bool(words), "practice architecture has no name")
    return f"Rust: {words}"


def read_json(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read frozen practice summary: {path}") from error
    require(isinstance(payload, dict), "practice summary is not an object")
    return payload


def resolve_oracle(value: object) -> Path:
    require(isinstance(value, str) and bool(value), "missing independent correctness proof")
    supplied = Path(value)
    marker = ("candidates", "evidence")
    parts = supplied.parts
    positions = [i for i in range(len(parts) - 1) if tuple(parts[i : i + 2]) == marker]
    require(len(positions) == 1, "correctness proof is outside candidates/evidence")
    result = (ROOT / Path(*parts[positions[0] :])).resolve()
    evidence = (ROOT / "candidates" / "evidence").resolve()
    require(result.is_relative_to(evidence), "correctness proof escaped candidates/evidence")
    return result


def verify_oracle(payload: dict, ranking: dict) -> None:
    proofs = payload.get("verified_edge_oracles")
    require(isinstance(proofs, list) and len(proofs) == 1, "expected one complete Rust correctness proof")
    proof = proofs[0]
    require(isinstance(proof, dict), "invalid Rust correctness proof")
    require(proof.get("module") == ranking["candidate"], "proof does not cover the measured Rust engine")
    require(proof.get("correctness_checks") == ORACLE_CHECKS, "correctness proof lost a frozen obligation")
    require(proof.get("script_sha256") == ORACLE_SCRIPT_SHA256, "correctness oracle was replaced")
    require(proof.get("actual_sha256") == ORACLE_EXPECTED_SHA256, "correctness answers were replaced")

    path = resolve_oracle(proof.get("path"))
    try:
        compressed = path.read_bytes()
        uncompressed = gzip.decompress(compressed)
        actual = json.loads(uncompressed)
    except (OSError, EOFError, gzip.BadGzipFile, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot verify independent Rust correctness proof: {path}") from error
    require(hashlib.sha256(uncompressed).hexdigest() == proof.get("report_sha256"), "correctness proof bytes do not match")
    require(isinstance(actual, dict) and actual.get("schema") == ORACLE_SCHEMA, "incorrect correctness proof format")
    require(actual.get("python") == "3.14.6", "correctness Python version changed")
    require(actual.get("module") == ranking["candidate"], "proof tested a different engine")
    require(actual.get("correctness_checks") == ORACLE_CHECKS, "proof did not run all correctness checks")
    require(actual.get("failed") == 0 and actual.get("failures") == [], "Rust did not pass every correctness check")
    require(actual.get("holdout") == "NOT ACCESSED", "correctness proof accessed a performance holdout")
    require(actual.get("performance") == "NOT MEASURED", "correctness proof included performance")
    require(actual.get("actual_sha256") == ORACLE_EXPECTED_SHA256, "incorrect actual oracle answers")
    require(actual.get("expected_sha256") == ORACLE_EXPECTED_SHA256, "incorrect expected oracle answers")
    require(actual.get("script_sha256") == ORACLE_SCRIPT_SHA256, "incorrect oracle implementation")

    proof_roles = proof.get("candidate_artifacts")
    actual_roles = actual.get("candidate_artifacts")
    require(isinstance(proof_roles, dict) and set(proof_roles) == set(ROLE_KEYS), "proof omitted an engine artifact")
    require(isinstance(actual_roles, list) and len(actual_roles) == len(ROLE_KEYS), "oracle omitted an engine artifact")
    indexed = {entry.get("role"): entry for entry in actual_roles if isinstance(entry, dict)}
    require(set(indexed) == set(ROLE_KEYS), "oracle duplicated or omitted an engine artifact")
    before = payload.get("candidate_binary_sha256_before")
    after = payload.get("candidate_binary_sha256_after")
    require(isinstance(before, dict) and before == after, "measured code changed during the practice test")
    for role, measured_role in ROLE_KEYS.items():
        recorded = proof_roles[role]
        actual_role = indexed[role]
        require(isinstance(recorded, dict), f"invalid recorded {role}")
        require(recorded.get("path") == actual_role.get("path"), f"incorrect {role} path")
        require(recorded.get("sha256") == actual_role.get("sha256"), f"incorrect {role} correctness fingerprint")
        key = f"{ranking['candidate']}:{measured_role}"
        require(before.get(key) == recorded.get("sha256"), f"measured {role} differs from the correctness proof")


def validate_payload(payload: dict, path: Path, *, verify_proof: bool = True) -> PracticeResult:
    require(payload.get("schema") == SUMMARY_SCHEMA, "incorrect frozen practice format")
    require(payload.get("cohort") == "calibration", "only the practice cohort may be charted")
    require(payload.get("holdout_accessed") is False, "hidden performance test was accessed")
    require(payload.get("expected_sha256") == PRACTICE_SHA256, "practice answers or workload changed")
    require(payload.get("cases") == CASES, "practice denominator changed")
    require(payload.get("trials") == TRIALS, "paired-trial denominator changed")
    require(payload.get("paired_raw_rows") == CASES * TRIALS * 2, "paired measurement rows are missing")
    require(payload.get("failed") == 0, "a practice correctness check failed")
    require(payload.get("correctness_checks") == CASES * TRIALS * 6, "a practice correctness check was omitted")
    threshold = finite(payload.get("strict_regression_speedup_threshold"), "slowdown threshold")
    require(math.isclose(threshold, 5 / 6, rel_tol=0, abs_tol=1e-15), "the more-than-20% slowdown threshold changed")
    require(payload.get("modules") == ["re", RUST_MODULE], "practice comparison must contain Python and Rust")

    rankings = payload.get("rankings")
    require(isinstance(rankings, list) and len(rankings) == 1, "expected one baseline-relative Rust ranking")
    ranking = rankings[0]
    require(isinstance(ranking, dict) and ranking.get("candidate") == RUST_MODULE, "practice ranking is not the Rust engine")
    require(ranking.get("cohort") == "calibration", "ranking includes hidden results")
    require(ranking.get("cases") == CASES and ranking.get("weight") == CASES, "ranking changed the denominator")
    point = finite(ranking.get("geomean_speedup"), "overall speed")
    low = finite(ranking.get("ci95_low"), "overall confidence lower bound")
    high = finite(ranking.get("ci95_high"), "overall confidence upper bound")
    require(low <= point <= high, "overall confidence range excludes the measured speed")

    values = payload.get("case_results")
    require(isinstance(values, list) and len(values) == CASES, "a practice case was dropped or duplicated")
    rows: list[dict] = []
    ids: set[str] = set()
    for value in values:
        require(isinstance(value, dict), "invalid practice case")
        identifier = value.get("case")
        require(isinstance(identifier, str) and identifier.startswith("cal."), "case is not a sealed practice example")
        require(identifier not in ids, "duplicate practice case")
        ids.add(identifier)
        require(value.get("cohort") == "calibration", "hidden case found in practice chart")
        require(value.get("candidate") == RUST_MODULE, "case belongs to a different engine")
        require(value.get("api") in API_LABELS, "unknown or omitted public operation")
        require(value.get("weight") == 1, "case weighting or denominator changed")
        speed = finite(value.get("speedup"), f"{identifier} speed")
        case_low = finite(value.get("ci95_low"), f"{identifier} confidence lower bound")
        case_high = finite(value.get("ci95_high"), f"{identifier} confidence upper bound")
        require(case_low <= speed <= case_high, f"{identifier} has an invalid confidence range")
        finite(value.get("baseline_ns"), f"{identifier} Python time")
        finite(value.get("candidate_ns"), f"{identifier} Rust time")
        finite(value.get("peak_traced_ratio"), f"{identifier} Python-traced memory", positive=False)
        faster = value.get("statistically_faster")
        regression = value.get("regression_gt_20pct")
        require(isinstance(faster, bool) and faster == (case_low > 1), f"{identifier} changes the faster-case rule")
        require(isinstance(regression, bool) and regression == (speed < threshold), f"{identifier} hides a large slowdown")
        rows.append(value)

    frozen_rows = tuple(rows)
    require(math.isclose(geometric(frozen_rows), point, rel_tol=1e-12, abs_tol=1e-12), "overall speed omits or reweights a case")
    faster_count = sum(row["statistically_faster"] for row in frozen_rows)
    regressions = [row for row in frozen_rows if row["regression_gt_20pct"]]
    require(ranking.get("statistically_faster_cases") == faster_count, "ranking hides statistically faster cases")
    require(ranking.get("regressions_gt_20pct") == len(regressions), "ranking hides a large slowdown")
    saved_regressions = payload.get("regressions")
    require(isinstance(saved_regressions, list), "complete slowdown evidence is missing")
    require(sorted(saved_regressions, key=lambda row: row.get("case", "")) == sorted(regressions, key=lambda row: row["case"]), "a more-than-20% slowdown was dropped or modified")

    distributions = (
        ("public_operations", Counter(row["api"] for row in frozen_rows)),
        ("lifetimes", Counter(row["lifecycle"] for row in frozen_rows)),
        ("inputs", Counter(row["input"] for row in frozen_rows)),
        ("result_densities", Counter(row["result_density"] for row in frozen_rows)),
        ("api_lifetimes", Counter(f"{row['api']} / {row['lifecycle']}" for row in frozen_rows)),
    )
    for name, actual in distributions:
        require(payload.get(name) == dict(actual), f"practice {name} dropped or relabeled a case")
        require(sum(actual.values()) == CASES, f"practice {name} has the wrong denominator")
    require(set(payload["public_operations"]) == set(API_LABELS), "a public API group was omitted")

    if verify_proof:
        verify_oracle(payload, ranking)
    return PracticeResult(path, payload, ranking, frozen_rows, architecture_name(path))


def load_results(paths: list[Path]) -> list[PracticeResult]:
    require(bool(paths), "at least one frozen Rust practice report is required")
    resolved = [path.resolve() for path in paths]
    require(len(set(resolved)) == len(resolved), "a Rust architecture was charted twice")
    results = [validate_payload(read_json(path), path) for path in resolved]
    expected = {(item.payload["expected_sha256"], item.payload["cases"], item.payload["trials"]) for item in results}
    require(len(expected) == 1, "Rust architectures did not run the same frozen practice test")
    return sorted(results, key=lambda item: (-item.ranking["geomean_speedup"], item.label, str(item.path)))


def fmt(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}×"


def opening(width: int, height: int, title: str, subtitle: str) -> list[str]:
    description = f"PRACTICE ONLY. {CASES} practice tasks and {TRIALS} paired runs. The unseen test has not been opened. {subtitle}"
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">',
        f"<title>{escape(title)}</title>",
        f"<desc>{escape(description)}</desc>",
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;fill:#172033}.title{font-size:25px;font-weight:750}.sub{font-size:13px;fill:#52627a}.head{font-size:15px;font-weight:700}.label{font-size:12px}.small{font-size:11px;fill:#52627a}.value{font-size:12px;font-weight:700}.tick{font-size:10.5px;fill:#64748b}.banner{font-size:12px;font-weight:700;fill:#92400e}.grid{stroke:#e2e8f0;stroke-width:1}.base{stroke:#475569;stroke-width:1.7}.panel{fill:#f8fafc;stroke:#e2e8f0;stroke-width:1}</style>',
        f'<text x="26" y="39" class="title">{escape(title)}</text>',
        f'<text x="26" y="63" class="sub">{escape(subtitle)}</text>',
        f'<rect x="20" y="78" width="{width - 40}" height="34" rx="7" fill="#fffbeb" stroke="#fcd34d"/>',
        '<text x="33" y="100" class="banner">PRACTICE ONLY — the final unseen test has not been opened</text>',
    ]


def log_x(value: float, left: int, right: int, lower: float, upper: float) -> float:
    clipped = min(upper, max(lower, value))
    fraction = (math.log(clipped) - math.log(lower)) / (math.log(upper) - math.log(lower))
    return left + fraction * (right - left)


def speed_grid(body: list[str], left: int, right: int, top: int, bottom: int, *, lower: float = 0.2, upper: float = 5) -> None:
    ticks = ((0.2, "0.2×"), (0.3, "0.3×"), (0.5, "0.5×"), (0.75, "0.75×"), (1, "1× Python"), (1.5, "1.5×"), (2, "2×"), (3, "3×"), (5, "5×"), (8, "8×"), (10, "10×"))
    for value, label in ticks:
        if not lower <= value <= upper:
            continue
        position = log_x(value, left, right, lower, upper)
        style = "base" if value == 1 else "grid"
        body.append(f'<line x1="{position:.2f}" y1="{top}" x2="{position:.2f}" y2="{bottom}" class="{style}"/>')
        body.append(f'<text x="{position:.2f}" y="{top - 8}" text-anchor="middle" class="tick">{escape(label)}</text>')


def speed_bounds(results: list[PracticeResult], *, groups: bool = False) -> tuple[float, float]:
    values = [1.0]
    for item in results:
        if groups:
            for api in API_LABELS:
                rows = tuple(row for row in item.rows if row["api"] == api)
                values.append(geometric(rows))
        else:
            values.extend((item.ranking["ci95_low"], item.ranking["ci95_high"]))
    lower = min(0.2, min(values) * 0.85)
    upper = max(2.0, max(values) * 1.15)
    return max(lower, 0.01), min(max(upper, 2), 50)


def overall_chart(results: list[PracticeResult]) -> str:
    width = 1320
    height = 250 + 76 * len(results)
    left, right = 310, 842
    lower, upper = speed_bounds(results)
    body = opening(width, height, "How fast is Rust compared with Python?", f"{CASES} practice tasks · {TRIALS} paired runs · lines show the full 95% measured range")
    speed_grid(body, left, right, 154, height - 48, lower=lower, upper=upper)
    baseline_y = 183
    baseline_x = log_x(1, left, right, lower, upper)
    body.extend((
        f'<text x="28" y="{baseline_y + 5}" class="head">Python re</text>',
        f'<circle cx="{baseline_x:.2f}" cy="{baseline_y}" r="6" fill="{GREY}" stroke="#ffffff" stroke-width="1.5"/>',
        f'<text x="868" y="{baseline_y - 3}" class="value">Python baseline: exactly 1.000×</text>',
        f'<text x="868" y="{baseline_y + 16}" class="small">The same Python installation and the same {CASES} tasks.</text>',
    ))
    for index, item in enumerate(results):
        ranking = item.ranking
        y = 259 + 76 * index
        low, point, high = (ranking["ci95_low"], ranking["geomean_speedup"], ranking["ci95_high"])
        if low > 1:
            color, interpretation = GREEN, "Clearly faster overall"
        elif high < 1:
            color, interpretation = RED, "Clearly slower overall"
        else:
            color, interpretation = AMBER, "No clear overall speed difference; range crosses 1×"
        body.extend((
            f'<text x="28" y="{y + 5}" class="head">{escape(item.label)}</text>',
            f'<line x1="{log_x(low, left, right, lower, upper):.2f}" y1="{y}" x2="{log_x(high, left, right, lower, upper):.2f}" y2="{y}" stroke="{color}" stroke-width="7" stroke-linecap="round"/>',
            f'<circle cx="{log_x(point, left, right, lower, upper):.2f}" cy="{y}" r="6" fill="{color}" stroke="#ffffff" stroke-width="1.5"/>',
            f'<text x="868" y="{y - 10}" class="value">{fmt(point)} as fast · 95% range {fmt(low)}–{fmt(high)}</text>',
            f'<text x="868" y="{y + 9}" class="small">{escape(interpretation)}</text>',
            f'<text x="868" y="{y + 26}" class="small">{ranking["statistically_faster_cases"]}/{CASES} clearly faster · {ranking["regressions_gt_20pct"]}/{CASES} more than 20% slower</text>',
        ))
    body.append(f'<text x="27" y="{height - 15}" class="small">Every architecture shown passed all {ORACLE_CHECKS:,} frozen correctness checks. Practice results are not final unseen-test results.</text>')
    return "\n".join((*body, "</svg>", ""))


def api_rows(item: PracticeResult) -> dict[str, tuple[dict, ...]]:
    return {api: tuple(row for row in item.rows if row["api"] == api) for api in API_LABELS}


def api_chart(results: list[PracticeResult]) -> str:
    width = 1320
    row_height = 32
    panel_height = 62 + len(API_LABELS) * row_height
    height = 153 + len(results) * panel_height + 35
    left, right = 327, 861
    lower, upper = speed_bounds(results, groups=True)
    body = opening(width, height, "Where Rust is faster or slower", f"All {len(API_LABELS)} kinds of Python re operation · all {CASES} practice tasks · dots are group averages, not group confidence intervals")
    for index, item in enumerate(results):
        top = 151 + index * panel_height
        body.append(f'<rect x="18" y="{top - 22}" width="{width - 36}" height="{panel_height - 8}" rx="9" class="panel"/>')
        body.append(f'<text x="29" y="{top - 2}" class="head">{escape(item.label)}</text>')
        speed_grid(body, left, right, top + 31, top + 38 + len(API_LABELS) * row_height, lower=lower, upper=upper)
        for offset, (api, rows) in enumerate(api_rows(item).items()):
            y = top + 57 + offset * row_height
            point = geometric(rows)
            faster = sum(row["statistically_faster"] for row in rows)
            regressions = sum(row["regression_gt_20pct"] for row in rows)
            color = RED if regressions else GREEN if point > 1 else PURPLE
            body.extend((
                f'<text x="29" y="{y + 4}" class="label">{escape(API_LABELS[api])} ({escape(api)})</text>',
                f'<circle cx="{log_x(point, left, right, lower, upper):.2f}" cy="{y}" r="5" fill="{color}" stroke="#ffffff" stroke-width="1.2"/>',
                f'<text x="878" y="{y + 4}" class="value">{fmt(point)}</text>',
                f'<text x="958" y="{y + 4}" class="small">{faster}/{len(rows)} clearly faster · {regressions}/{len(rows)} &gt;20% slower</text>',
            ))
    body.append(f'<text x="26" y="{height - 14}" class="small">Every group includes every one of its practice cases. Group-average dots must not be mistaken for confidence intervals.</text>')
    return "\n".join((*body, "</svg>", ""))


def win_loss_chart(results: list[PracticeResult]) -> str:
    width = 1250
    panel_height = 155
    height = 148 + len(results) * panel_height + 45
    left, right = 300, 1060
    scale = (right - left) / CASES
    body = opening(width, height, "How often does Rust win or lose?", f"All {CASES} practice tasks; confidence-based outcomes and all more-than-20% slowdowns are shown separately")
    for index, item in enumerate(results):
        top = 147 + index * panel_height
        faster = sum(row["ci95_low"] > 1 for row in item.rows)
        slower = sum(row["ci95_high"] < 1 for row in item.rows)
        uncertain = CASES - faster - slower
        regressions = item.ranking["regressions_gt_20pct"]
        require(faster + uncertain + slower == CASES, "win/loss chart changed the denominator")
        body.append(f'<rect x="18" y="{top - 16}" width="{width - 36}" height="{panel_height - 10}" rx="9" class="panel"/>')
        body.append(f'<text x="29" y="{top + 7}" class="head">{escape(item.label)}</text>')
        body.append(f'<text x="29" y="{top + 47}" class="label">Confidence-based outcome</text>')
        position = float(left)
        for count, color in ((faster, GREEN), (uncertain, GREY), (slower, RED)):
            section = count * scale
            if count:
                body.append(f'<rect x="{position:.2f}" y="{top + 30}" width="{section:.2f}" height="22" fill="{color}"/>')
                if section >= 45:
                    body.append(f'<text x="{position + section / 2:.2f}" y="{top + 45}" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#ffffff">{count}</text>')
            position += section
        body.append(f'<text x="{right + 12}" y="{top + 46}" class="value">{CASES}/{CASES}</text>')
        body.append(f'<text x="{left}" y="{top + 72}" class="small">{faster}/{CASES} clearly faster · {uncertain}/{CASES} no clear difference · {slower}/{CASES} clearly slower</text>')
        body.append(f'<text x="29" y="{top + 105}" class="label">Took &gt;20% longer</text>')
        body.append(f'<rect x="{left}" y="{top + 89}" width="{right - left}" height="19" fill="#fee2e2"/>')
        body.append(f'<rect x="{left}" y="{top + 89}" width="{regressions * scale:.2f}" height="19" fill="{RED}"/>')
        body.append(f'<text x="{right + 12}" y="{top + 104}" class="value">{regressions}/{CASES}</text>')
        body.append(f'<text x="{left}" y="{top + 127}" class="small">A separate timing rule: all {regressions} large slowdowns are retained, even if an individual confidence range crosses 1×.</text>')
    body.append(f'<text x="26" y="{height - 15}" class="small">Green, grey, and red outcomes add to all {CASES} tasks. The slowdown bar uses the same {CASES}-task denominator.</text>')
    return "\n".join((*body, "</svg>", ""))


def regression_chart(results: list[PracticeResult]) -> str:
    width = 1210
    row_height = 30
    panel_height = 65 + len(API_LABELS) * row_height
    height = 149 + len(results) * panel_height + 37
    left, right = 333, 906
    body = opening(width, height, "Every slowdown of more than 20%", f"All {CASES} practice tasks · all {len(API_LABELS)} kinds of operation · zero-count groups are retained")
    for index, item in enumerate(results):
        top = 146 + index * panel_height
        grouped = api_rows(item)
        counts = {api: sum(row["regression_gt_20pct"] for row in rows) for api, rows in grouped.items()}
        require(sum(counts.values()) == item.ranking["regressions_gt_20pct"], "regression chart omitted a slowdown")
        maximum = max(1, max(counts.values()))
        body.append(f'<rect x="18" y="{top - 17}" width="{width - 36}" height="{panel_height - 8}" rx="9" class="panel"/>')
        body.append(f'<text x="29" y="{top + 3}" class="head">{escape(item.label)} · {sum(counts.values())}/{CASES} large slowdowns</text>')
        for offset, (api, rows) in enumerate(grouped.items()):
            y = top + 33 + offset * row_height
            count = counts[api]
            bar_width = (right - left) * count / maximum
            body.extend((
                f'<text x="29" y="{y + 13}" class="label">{escape(API_LABELS[api])} ({escape(api)})</text>',
                f'<rect x="{left}" y="{y}" width="{right - left}" height="17" rx="3" fill="#f1f5f9"/>',
                f'<rect x="{left}" y="{y}" width="{bar_width:.2f}" height="17" rx="3" fill="{RED}"/>',
                f'<text x="{right + 15}" y="{y + 13}" class="value">{count}/{len(rows)}</text>',
                f'<text x="{right + 85}" y="{y + 13}" class="small">{100 * count / len(rows):.1f}% of this group</text>',
            ))
    body.append(f'<text x="26" y="{height - 15}" class="small">A slowdown is counted when Rust takes more than 20% longer than Python; no operation or loss is excluded.</text>')
    return "\n".join((*body, "</svg>", ""))


def memory_chart(results: list[PracticeResult]) -> str:
    width = 1320
    row_height = 32
    panel_height = 63 + len(API_LABELS) * row_height
    height = 151 + len(results) * panel_height + 47
    left, right = 337, 845
    medians = [statistics.median(row["peak_traced_ratio"] for row in rows) for item in results for rows in api_rows(item).values()]
    lower = 0.0625
    upper = max(4.0, max(medians, default=1.0) * 1.2)
    body = opening(width, height, "Temporary memory used while matching", f"Python-traced temporary memory only · median of all {CASES} practice cases · lower is better")
    for index, item in enumerate(results):
        top = 147 + index * panel_height
        body.append(f'<rect x="18" y="{top - 18}" width="{width - 36}" height="{panel_height - 8}" rx="9" class="panel"/>')
        body.append(f'<text x="29" y="{top + 2}" class="head">{escape(item.label)} · Python-traced temporary memory</text>')
        ticks = ((0.0625, "0.06×"), (0.125, "0.125×"), (0.25, "0.25×"), (0.5, "0.5×"), (1, "1× Python"), (2, "2×"), (4, "4×"), (8, "8×"), (16, "16×"))
        for value, label in ticks:
            if not lower <= value <= upper:
                continue
            x = log_x(value, left, right, lower, upper)
            body.append(f'<line x1="{x:.2f}" y1="{top + 33}" x2="{x:.2f}" y2="{top + 38 + len(API_LABELS) * row_height}" class="{"base" if value == 1 else "grid"}"/>')
            body.append(f'<text x="{x:.2f}" y="{top + 25}" text-anchor="middle" class="tick">{escape(label)}</text>')
        for offset, (api, rows) in enumerate(api_rows(item).items()):
            y = top + 57 + offset * row_height
            median = float(statistics.median(row["peak_traced_ratio"] for row in rows))
            zero_count = sum(row["peak_traced_ratio"] == 0 for row in rows)
            color = GREEN if median < 1 else RED if median > 1 else GREY
            body.extend((
                f'<text x="29" y="{y + 4}" class="label">{escape(API_LABELS[api])} ({escape(api)})</text>',
                f'<circle cx="{log_x(max(median, lower), left, right, lower, upper):.2f}" cy="{y}" r="5" fill="{color}" stroke="#ffffff" stroke-width="1.2"/>',
                f'<text x="{right + 17}" y="{y + 4}" class="value">{fmt(median)}</text>',
                f'<text x="{right + 100}" y="{y + 4}" class="small">{len(rows)} cases · {zero_count} with no traced temporary memory</text>',
            ))
    body.append(f'<text x="26" y="{height - 24}" class="small">These values describe Python-traced temporary allocations only. They do not measure process memory, RSS, Rust allocator use, or total memory.</text>')
    body.append(f'<text x="26" y="{height - 9}" class="small">A 0.000× median means no Python-traced temporary allocation; its dot is shown at the left edge, without dropping any zero.</text>')
    return "\n".join((*body, "</svg>", ""))


def build_charts(results: list[PracticeResult]) -> dict[str, str]:
    charts = {
        "rust-v7-calibration-overall.svg": overall_chart(results),
        "rust-v7-calibration-api.svg": api_chart(results),
        "rust-v7-calibration-win-loss.svg": win_loss_chart(results),
        "rust-v7-calibration-regressions.svg": regression_chart(results),
        "rust-v7-calibration-memory.svg": memory_chart(results),
    }
    for name, content in charts.items():
        require(name.startswith("rust-v7-calibration-") and name.endswith(".svg"), "refusing an unrelated chart path")
        require("PRACTICE ONLY" in content and "unseen test has not been opened" in content, "practice-only disclosure is missing")
        require(str(CASES) in content, "chart omitted the complete case denominator")
        try:
            ElementTree.fromstring(content)
        except ElementTree.ParseError as error:
            raise ValueError(f"generated invalid chart: {name}") from error
    return charts


def expect_rejection(payload: dict, path: Path, change, label: str) -> None:
    poisoned = copy.deepcopy(payload)
    change(poisoned)
    try:
        validate_payload(poisoned, path)
    except (ValueError, TypeError, KeyError):
        return
    raise ValueError(f"self-test accepted {label}")


def self_test(paths: list[Path]) -> None:
    results = load_results(paths)
    first = results[0]
    mutations = (
        ("a hidden-test access", lambda value: value.__setitem__("holdout_accessed", True)),
        ("the hidden cohort", lambda value: value.__setitem__("cohort", "holdout")),
        ("a changed case denominator", lambda value: value.__setitem__("cases", CASES - 1)),
        ("a missing practice case", lambda value: value["case_results"].pop()),
        ("a duplicated practice case", lambda value: value["case_results"].__setitem__(1, copy.deepcopy(value["case_results"][0]))),
        ("a hidden case", lambda value: value["case_results"][0].__setitem__("cohort", "holdout")),
        ("a removed regression", lambda value: value["regressions"].pop()),
        ("a weakened slowdown threshold", lambda value: value.__setitem__("strict_regression_speedup_threshold", 0.8)),
        ("a removed faster case", lambda value: value["rankings"][0].__setitem__("statistically_faster_cases", value["rankings"][0]["statistically_faster_cases"] - 1)),
        ("a hidden ranking slowdown", lambda value: value["rankings"][0].__setitem__("regressions_gt_20pct", value["rankings"][0]["regressions_gt_20pct"] - 1)),
        ("an altered overall confidence range", lambda value: value["rankings"][0].__setitem__("ci95_low", value["rankings"][0]["geomean_speedup"] + 0.01)),
        ("a dropped operation group", lambda value: value["public_operations"].pop("scanner")),
        ("a dropped memory observation", lambda value: value["case_results"][0].__setitem__("peak_traced_ratio", None)),
        ("a negative memory observation", lambda value: value["case_results"][0].__setitem__("peak_traced_ratio", -1)),
        ("changed frozen practice answers", lambda value: value.__setitem__("expected_sha256", "0" * 64)),
        ("an unqualified correctness oracle", lambda value: value["verified_edge_oracles"][0].__setitem__("correctness_checks", ORACLE_CHECKS - 1)),
        ("a replaced correctness proof", lambda value: value["verified_edge_oracles"][0].__setitem__("report_sha256", "0" * 64)),
        ("a changed engine artifact", lambda value: value["candidate_binary_sha256_after"].__setitem__(f"{RUST_MODULE}:native-engine", "0" * 64)),
        ("an unpaired benchmark", lambda value: value.__setitem__("paired_raw_rows", value["paired_raw_rows"] - 1)),
        ("a different Python baseline", lambda value: value.__setitem__("modules", ["another_baseline", RUST_MODULE])),
    )
    for label, mutation in mutations:
        expect_rejection(first.payload, first.path, mutation, label)

    charts = build_charts(results)
    overall = charts["rust-v7-calibration-overall.svg"]
    for item in results:
        rank = item.ranking
        required = (
            item.label,
            fmt(rank["geomean_speedup"]),
            fmt(rank["ci95_low"]),
            fmt(rank["ci95_high"]),
            f'{rank["statistically_faster_cases"]}/{CASES}',
            f'{rank["regressions_gt_20pct"]}/{CASES}',
        )
        for label in required:
            require(escape(label) in overall, f"overall chart omitted the exact result: {label}")
        if rank["ci95_low"] <= 1 <= rank["ci95_high"]:
            require("range crosses 1×" in overall, "overall chart hid an inconclusive confidence range")
        for name in ("rust-v7-calibration-api.svg", "rust-v7-calibration-regressions.svg", "rust-v7-calibration-memory.svg"):
            for api in API_LABELS:
                require(f"({escape(api)})" in charts[name], f"{name} omitted operation {api}")
        outcomes = charts["rust-v7-calibration-win-loss.svg"]
        faster = sum(row["ci95_low"] > 1 for row in item.rows)
        slower = sum(row["ci95_high"] < 1 for row in item.rows)
        uncertain = CASES - faster - slower
        for count in (faster, uncertain, slower, rank["regressions_gt_20pct"]):
            require(f"{count}/{CASES}" in outcomes, "win/loss chart omitted a measured outcome")
        require("Python-traced temporary memory" in charts["rust-v7-calibration-memory.svg"], "memory chart omitted its measurement scope")
        require("do not measure process memory" in charts["rust-v7-calibration-memory.svg"], "memory chart could be mistaken for process memory")

    repeated = build_charts(results)
    require(charts == repeated, "practice charts are not deterministic")
    print(f"PASS: {len(results)} correctness-qualified Rust architecture(s); {len(mutations)} corruption checks; {len(charts)} valid deterministic practice-only charts; all {CASES} cases and all losses retained; hidden test untouched")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate transparent charts from sealed Rust practice data only.")
    parser.add_argument("--summary", action="append", type=Path, default=[], help="repeat for each frozen 624-case Rust practice summary")
    parser.add_argument("--self-test", action="store_true", help="validate hidden-test isolation, complete losses, correctness proofs and deterministic SVG")
    args = parser.parse_args()
    paths = args.summary or [DEFAULT_SUMMARY]
    if args.self_test:
        self_test(paths)
        return
    results = load_results(paths)
    for name, content in build_charts(results).items():
        destination = EVIDENCE / name
        destination.write_text(content, encoding="utf-8")
        print(f"wrote {destination.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
