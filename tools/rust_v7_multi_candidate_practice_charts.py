#!/usr/bin/env python3
"""Render audited, same-run public practice results; never open a holdout."""

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
from typing import Iterable
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "performance" / "v7" / "evidence"
DEFAULT_PREFIX = EVIDENCE / "three-qualified-engines-public-practice-v1"
DEFAULT_SUMMARY = EVIDENCE / "three-qualified-engines-public-practice-v1-summary.json"
DEFAULT_RAW = EVIDENCE / "three-qualified-engines-public-practice-v1-raw.jsonl.gz"
DEFAULT_INTEGRITY = EVIDENCE / "three-qualified-engines-public-practice-v1-integrity.json"
AUDIT_PATH = ROOT / "candidates" / "audits" / "FROM-SCRATCH-AUDIT.json"

SUMMARY_SCHEMA = "rebar-rust-balanced-calibration-pilot-v7"
RAW_SCHEMA = "rebar-rust-balanced-calibration-row-v7"
INTEGRITY_SCHEMA = "rebar-v7-multi-candidate-practice-integrity-v1"
PRACTICE_SHA256 = "2e6c098bd3a4757620461363106a9795f8defa98fe8bc9c13c0ebbf7ed58b598"
ORACLE_SOURCE_SHA256 = "fe6a263a48f243ea02faaa78fc3bbd051233a2b2221967a5f76dd1bb79d242ca"
ORACLE_ANSWERS_SHA256 = "b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526"
SLOT = "three-qualified-engines-public-practice-v1"
CASES = 624
TRIALS = 7
BOOTSTRAPS = 499
RAW_ROWS = 17_472
CORRECTNESS_CHECKS = 52_416
EXPECTED_REGRESSIONS = 426
EDGE_CHECKS = 223_198
BASELINE = "re"
RUST = "candidates.rust_candidate"
C_ENGINE = "candidates.vm_candidate"
ZIG = "candidates.zig_candidate"
MODULES = (BASELINE, RUST, C_ENGINE, ZIG)
CANDIDATES = MODULES[1:]
DISPLAY = {BASELINE: "Standard Python", C_ENGINE: "C", RUST: "Rust", ZIG: "Zig"}
COLOURS = {
    BASELINE: "#64748b",
    C_ENGINE: "#2563eb",
    RUST: "#c2410c",
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
    "compile": "Prepare a pattern",
    "escape": "Escape special characters",
    "findall": "Find all matches",
    "finditer": "Stream all matches",
    "fullmatch": "Match the whole input",
    "match": "Match at the beginning",
    "match-surface": "Read match information",
    "scanner": "Scan repeated matches",
    "search": "Search for a match",
    "split": "Split around matches",
    "sub": "Replace matches",
    "subn": "Replace and count",
}
NATIVE_PATHS = {
    f"{RUST}:module": ROOT / "candidates" / "rust_candidate.py",
    f"{RUST}:native-bridge": ROOT / "candidates" / "_rust_bridge.cpython-314-x86_64-linux-gnu.so",
    f"{RUST}:native-engine": ROOT / "candidates" / "_rust_engine.so",
    f"{RUST}:native-source": ROOT / "candidates" / "rust" / "src" / "lib.rs",
    f"{RUST}:bridge-source": ROOT / "candidates" / "rust" / "py_bridge.c",
    f"{C_ENGINE}:module": ROOT / "candidates" / "vm_candidate.py",
    f"{C_ENGINE}:native-engine": ROOT / "candidates" / "_vm_native.cpython-314-x86_64-linux-gnu.so",
    f"{ZIG}:module": ROOT / "candidates" / "zig_candidate.py",
    f"{ZIG}:native-bridge": ROOT / "candidates" / "_zig_bridge.cpython-314-x86_64-linux-gnu.so",
    f"{ZIG}:native-engine": ROOT / "candidates" / "_zig_probe.so",
}
CHART_SUFFIXES = ("overall", "outcomes", "api", "regressions", "memory", "rankings")


@dataclass(frozen=True)
class EngineResult:
    module: str
    ranking: dict
    rows: tuple[dict, ...]


@dataclass(frozen=True)
class PracticeResults:
    summary: dict
    integrity: dict
    results: tuple[EngineResult, ...]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def finite(value: object, label: str, *, allow_zero: bool = False) -> float:
    require(isinstance(value, (int, float)) and not isinstance(value, bool), f"invalid {label}")
    number = float(value)
    require(math.isfinite(number), f"non-finite {label}")
    require(number >= 0 if allow_zero else number > 0, f"out-of-range {label}")
    return number


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as source:
            for block in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as error:
        raise ValueError(f"cannot verify input: {path}") from error
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read audited practice input: {path}") from error
    require(isinstance(value, dict), f"practice input is not an object: {path}")
    return value


def geometric(rows: Iterable[dict]) -> float:
    values = tuple(rows)
    require(bool(values), "a practice group was dropped")
    return math.exp(math.fsum(math.log(finite(row["speedup"], "case speed")) for row in values) / len(values))


def same_float(actual: float, expected: float, label: str) -> None:
    require(math.isclose(actual, expected, rel_tol=1e-11, abs_tol=1e-12), label)


def check_summary(summary: dict) -> tuple[EngineResult, ...]:
    require(summary.get("schema") == SUMMARY_SCHEMA, "the public practice format changed")
    require(summary.get("cohort") == "calibration", "only public practice cases may be charted")
    require(summary.get("holdout_accessed") is False, "the unseen test was accessed")
    require(summary.get("exclusive_slot") == SLOT, "the results are not from the frozen shared run")
    require(summary.get("failed") == 0, "a correctness check failed")
    require(summary.get("expected_sha256") == PRACTICE_SHA256, "the frozen practice answers changed")
    require(summary.get("modules") == list(MODULES), "the four engines or their paired order changed")
    require(summary.get("cases") == CASES, "the per-engine denominator changed")
    require(summary.get("trials") == TRIALS, "the paired-trial denominator changed")
    require(summary.get("warmups") == 4, "the warmup protocol changed")
    require(summary.get("bootstrap_samples") == BOOTSTRAPS, "the confidence protocol changed")
    require(summary.get("paired_raw_rows") == RAW_ROWS, "raw paired measurements were dropped")
    require(summary.get("correctness_checks") == CORRECTNESS_CHECKS, "a timing correctness gate was dropped")
    require(summary.get("all_bounded_workload_categories") == 260, "a practice category was dropped")
    require(summary.get("public_operations") == API_COUNTS, "an operation or its true denominator changed")
    threshold = finite(summary.get("strict_regression_speedup_threshold"), "slowdown threshold")
    same_float(threshold, 5 / 6, "the more-than-20%-slower rule changed")

    case_rows = summary.get("case_results")
    require(isinstance(case_rows, list) and len(case_rows) == CASES * len(CANDIDATES), "a candidate practice case was dropped or duplicated")
    rankings = summary.get("rankings")
    require(isinstance(rankings, list) and len(rankings) == len(CANDIDATES), "a candidate ranking was dropped")
    ranking_by_module: dict[str, dict] = {}
    for ranking in rankings:
        require(isinstance(ranking, dict), "invalid candidate ranking")
        module = ranking.get("candidate")
        require(module in CANDIDATES and module not in ranking_by_module, "an engine ranking is missing or duplicated")
        require(ranking.get("cohort") == "calibration", "a ranking is not public practice")
        require(ranking.get("cases") == CASES and ranking.get("weight") == CASES, "a ranking silently changed its denominator")
        point = finite(ranking.get("geomean_speedup"), "overall practice speed")
        low = finite(ranking.get("ci95_low"), "overall confidence lower bound")
        high = finite(ranking.get("ci95_high"), "overall confidence upper bound")
        require(low <= point <= high, "an overall confidence range excludes its estimate")
        ranking_by_module[module] = ranking

    by_module: dict[str, list[dict]] = {module: [] for module in CANDIDATES}
    seen: set[tuple[str, str]] = set()
    baseline_values: dict[str, float] = {}
    for row in case_rows:
        require(isinstance(row, dict), "invalid public case record")
        module = row.get("candidate")
        case = row.get("case")
        require(module in by_module, "an unapproved candidate entered the chart")
        require(isinstance(case, str) and case.startswith("cal."), "a hidden or invalid case entered the chart")
        require((module, case) not in seen, "a candidate case was duplicated")
        seen.add((module, case))
        require(row.get("cohort") == "calibration", "a hidden cohort entered the chart")
        require(row.get("api") in API_COUNTS, "an unknown public operation entered the chart")
        require(row.get("weight") == 1, "a case was silently reweighted")
        speed = finite(row.get("speedup"), f"{case} speed")
        low = finite(row.get("ci95_low"), f"{case} confidence lower bound")
        high = finite(row.get("ci95_high"), f"{case} confidence upper bound")
        require(low <= speed <= high, f"{case} has an invalid confidence range")
        baseline_ns = finite(row.get("baseline_ns"), f"{case} Python time")
        finite(row.get("candidate_ns"), f"{case} candidate time")
        if case in baseline_values:
            same_float(baseline_ns, baseline_values[case], f"{case} did not use the shared Python baseline")
        baseline_values[case] = baseline_ns
        finite(row.get("peak_traced_ratio"), f"{case} Python-traced allocation", allow_zero=True)
        faster = row.get("statistically_faster")
        slower = row.get("regression_gt_20pct")
        require(isinstance(faster, bool) and faster == (low > 1), f"{case} invented a clearly faster result")
        require(isinstance(slower, bool) and slower == (speed < threshold), f"{case} hid or invented a large slowdown")
        by_module[module].append(row)

    require(len(baseline_values) == CASES, "the engines were not tested on the same 624 cases")
    expected_ids = frozenset(baseline_values)
    results: list[EngineResult] = []
    regressions: list[dict] = []
    for module in CANDIDATES:
        rows = tuple(by_module[module])
        require(len(rows) == CASES, f"{DISPLAY[module]} lost a practice case")
        require(frozenset(row["case"] for row in rows) == expected_ids, f"{DISPLAY[module]} used different practice cases")
        require(dict(Counter(row["api"] for row in rows)) == API_COUNTS, f"{DISPLAY[module]} changed operation denominators")
        ranking = ranking_by_module[module]
        same_float(geometric(rows), finite(ranking["geomean_speedup"], "ranking speed"), f"{DISPLAY[module]} omitted or reweighted an overall case")
        faster_count = sum(row["statistically_faster"] for row in rows)
        large_losses = [row for row in rows if row["regression_gt_20pct"]]
        require(ranking.get("statistically_faster_cases") == faster_count, f"{DISPLAY[module]} invented a faster-case count")
        require(ranking.get("regressions_gt_20pct") == len(large_losses), f"{DISPLAY[module]} hid a more-than-20% slowdown")
        regressions.extend(large_losses)
        results.append(EngineResult(module, ranking, rows))

    reported_losses = summary.get("regressions")
    require(isinstance(reported_losses, list) and len(reported_losses) == EXPECTED_REGRESSIONS, "the complete set of 426 slowdowns is missing")
    order = lambda item: (item.get("candidate", ""), item.get("case", ""))
    require(sorted(reported_losses, key=order) == sorted(regressions, key=order), "a more-than-20% slowdown was removed or changed")
    require(sum(result.ranking["regressions_gt_20pct"] for result in results) == EXPECTED_REGRESSIONS, "the slowdown denominator changed")

    proofs = summary.get("verified_edge_oracles")
    require(isinstance(proofs, list) and len(proofs) == len(CANDIDATES), "an independent correctness proof was dropped")
    proof_modules: set[str] = set()
    for proof in proofs:
        require(isinstance(proof, dict), "invalid independent correctness proof")
        module = proof.get("module")
        require(module in CANDIDATES and module not in proof_modules, "candidate correctness proofs are incomplete")
        require(proof.get("correctness_checks") == EDGE_CHECKS, "an edge correctness obligation was omitted")
        require(proof.get("script_sha256") == ORACLE_SOURCE_SHA256, "the frozen correctness oracle changed")
        require(proof.get("actual_sha256") == ORACLE_ANSWERS_SHA256, "frozen correctness answers changed")
        proof_modules.add(module)

    before = summary.get("candidate_binary_sha256_before")
    after = summary.get("candidate_binary_sha256_after")
    require(isinstance(before, dict) and before == after, "the measured engines changed during practice")
    require(set(before) == set(NATIVE_PATHS) | {f"{BASELINE}:module"}, "a measured Python or native artifact is missing")
    require(all(isinstance(value, str) and len(value) == 64 for value in before.values()), "an engine fingerprint is invalid")
    return tuple(results)


def check_integrity(summary: dict, integrity: dict, *, summary_digest: str, compressed_digest: str, raw_digest: str) -> None:
    require(integrity.get("schema") == INTEGRITY_SCHEMA, "the independent practice audit has the wrong schema")
    require(integrity.get("result") == "PASS", "the independent practice audit did not pass")
    require(integrity.get("holdout_accessed") is False, "the independent audit does not prove hidden-test isolation")
    expected = {
        "module_order": list(MODULES),
        "cases_per_candidate": CASES,
        "candidate_case_count": CASES * len(CANDIDATES),
        "trials_per_module_case": TRIALS,
        "raw_rows": RAW_ROWS,
        "correctness_checks": CORRECTNESS_CHECKS,
        "bootstrap_draws": BOOTSTRAPS,
        "strict_regressions": EXPECTED_REGRESSIONS,
        "summary_sha256": summary_digest,
        "compressed_raw_sha256": compressed_digest,
        "raw_sha256": raw_digest,
    }
    for key, value in expected.items():
        require(integrity.get(key) == value, f"independent practice evidence does not verify {key}")
    require(summary.get("compressed_raw_sha256") == compressed_digest, "compressed public measurements changed")
    require(summary.get("raw_sha256") == raw_digest, "uncompressed public measurements changed")
    for key in ("candidate_binary_sha256_before", "candidate_binary_sha256_after", "rankings", "regressions", "verified_edge_oracles"):
        require(integrity.get(key) == summary.get(key), f"independent practice evidence does not bind {key}")
    require(integrity.get("timing_performed") is False, "the independent audit must not run a new timing experiment")


def check_raw_lines(lines: Iterable[bytes], summary: dict, *, expected_digest: str) -> None:
    digest = hashlib.sha256()
    case_rows = {row["case"]: row for row in summary["case_results"] if row["candidate"] == RUST}
    case_answers: dict[str, str] = {}
    seen: set[tuple[str, int, str]] = set()
    count = 0
    for line in lines:
        require(isinstance(line, bytes), "a raw practice row is not encoded bytes")
        digest.update(line)
        try:
            row = json.loads(line)
        except (UnicodeError, json.JSONDecodeError) as error:
            raise ValueError("invalid paired public practice measurement") from error
        require(isinstance(row, dict), "a raw measurement is not an object")
        require(row.get("schema") == RAW_SCHEMA, "a raw practice format changed")
        require(row.get("cohort") == "calibration", "a hidden case entered the raw measurements")
        case = row.get("case")
        module = row.get("module")
        trial = row.get("trial")
        require(case in case_rows and module in MODULES, "a raw practice case or candidate changed")
        require(isinstance(trial, int) and not isinstance(trial, bool) and 0 <= trial < TRIALS, "a paired trial changed")
        key = (case, trial, module)
        require(key not in seen, "a paired candidate measurement was duplicated")
        seen.add(key)
        answer = row.get("expected_sha256")
        require(
            isinstance(answer, str)
            and len(answer) == 64
            and all(character in "0123456789abcdef" for character in answer),
            "a raw per-case correctness answer is invalid",
        )
        if case in case_answers:
            require(answer == case_answers[case], "paired engines did not use the same per-case correctness answer")
        else:
            case_answers[case] = answer
        reference = case_rows[case]
        for name in ("api", "category", "input", "lifecycle", "result_density"):
            require(row.get(name) == reference.get(name), f"a raw practice {name} changed")
        finite(row.get("elapsed_ns"), "raw elapsed time")
        finite(row.get("ns_per_op"), "raw time per operation")
        operations = row.get("operations")
        require(isinstance(operations, int) and not isinstance(operations, bool) and operations > 0, "raw operation counts changed")
        finite(row.get("peak_traced_bytes"), "raw Python-traced allocation", allow_zero=True)
        count += 1
        require(count <= RAW_ROWS, "unexpected extra practice measurements")
    require(count == RAW_ROWS, "paired public practice measurements are missing")
    require(len(seen) == CASES * TRIALS * len(MODULES), "practice engines did not share every case and trial")
    require(len(case_answers) == CASES, "per-case practice correctness answers were dropped")
    require(digest.hexdigest() == expected_digest, "uncompressed public practice measurements changed")


def check_current_sources(summary: dict, integrity: dict) -> None:
    require(sha256_file(AUDIT_PATH) == integrity.get("from_scratch_audit_sha256"), "the qualifying from-scratch audit changed")
    audit = read_json(AUDIT_PATH)
    require(audit.get("schema_version") == 1, "the from-scratch audit format changed")
    require(audit.get("passed") is True and audit.get("result") == "PASS", "the candidates failed the from-scratch audit")
    require(audit.get("verified_core_family_count", 0) >= 3, "fewer than three independent core families were audited")
    require(audit.get("verified_distinct_pipeline_count", 0) >= 4, "the Python baseline and three independent pipelines were not audited")
    require(audit.get("runtime_native_mapping_provenance", {}).get("passed") is True, "loaded native-engine provenance is not verified")
    require(audit.get("native_elf_provenance", {}).get("passed") is True, "native binary provenance is not verified")
    require(audit.get("self_test", {}).get("passed") is True, "the independence audit did not pass its self-test")
    families = audit.get("families")
    require(isinstance(families, dict), "the independence audit omitted engine families")
    source_fingerprints = integrity.get("qualified_source_fingerprints")
    require(isinstance(source_fingerprints, dict) and bool(source_fingerprints), "the results audit omitted current source fingerprints")
    verified_sources: dict[str, str] = {}
    for family, module in (("rust", RUST), ("vm", C_ENGINE), ("zig", ZIG)):
        result = families.get(family)
        require(isinstance(result, dict) and result.get("passed") is True, f"{DISPLAY[module]} is not independently qualified")
        python_source = result.get("python_source")
        require(isinstance(python_source, dict) and python_source.get("passed") is True, f"{DISPLAY[module]} Python source was not audited")
        entries = [python_source]
        native_sources = result.get("native_sources")
        require(isinstance(native_sources, list) and bool(native_sources), f"{DISPLAY[module]} from-scratch native sources are missing")
        entries.extend(native_sources)
        for entry in entries:
            require(isinstance(entry, dict) and entry.get("passed") is True, f"{DISPLAY[module]} source failed the independence audit")
            relative = entry.get("file")
            recorded = entry.get("sha256")
            require(isinstance(relative, str) and isinstance(recorded, str), "invalid audited source fingerprint")
            actual = (ROOT / relative).resolve()
            require(actual.is_relative_to(ROOT.resolve()), "an audited source escaped the project")
            require(sha256_file(actual) == recorded, f"the audited {DISPLAY[module]} source changed: {relative}")
            verified_sources[relative] = recorded
    require(source_fingerprints == verified_sources, "the independent results audit does not bind all current from-scratch sources")
    before = summary["candidate_binary_sha256_before"]
    for role, path in NATIVE_PATHS.items():
        require(sha256_file(path) == before.get(role), f"the measured native engine changed: {role}")
    binaries = integrity.get("native_elf_fingerprints")
    require(isinstance(binaries, dict), "the results audit omitted native-engine fingerprints")
    expected = {role: before[role] for role in NATIVE_PATHS if role.endswith(":native-engine") or role.endswith(":native-bridge")}
    require(binaries == expected, "the results audit does not bind all five measured native binaries")


def load_results(summary_path: Path, raw_path: Path, integrity_path: Path) -> PracticeResults:
    summary = read_json(summary_path)
    integrity = read_json(integrity_path)
    results = check_summary(summary)
    summary_digest = sha256_file(summary_path)
    compressed_digest = sha256_file(raw_path)
    raw_digest = summary.get("raw_sha256")
    require(isinstance(raw_digest, str) and len(raw_digest) == 64, "the raw public practice digest is missing")
    check_integrity(summary, integrity, summary_digest=summary_digest, compressed_digest=compressed_digest, raw_digest=raw_digest)
    require(summary.get("raw_path") == str(raw_path.resolve()), "the summary identifies different raw practice measurements")
    try:
        with gzip.open(raw_path, "rb") as source:
            check_raw_lines(source, summary, expected_digest=raw_digest)
    except (OSError, EOFError, gzip.BadGzipFile) as error:
        raise ValueError("cannot read the complete compressed public practice measurements") from error
    check_current_sources(summary, integrity)
    return PracticeResults(summary, integrity, tuple(sorted(results, key=lambda item: (-item.ranking["geomean_speedup"], DISPLAY[item.module]))))


def fmt(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}×"


def svg_open(width: int, height: int, title: str, subtitle: str) -> list[str]:
    description = (
        f"PRACTICE ONLY. Every replacement and standard Python ran the same {CASES} public practice tasks "
        f"in the same {TRIALS} paired trials. The unseen final test remains sealed. {subtitle}"
    )
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title, quote=True)}">',
        f"<title>{escape(title)}</title>",
        f"<desc>{escape(description)}</desc>",
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;fill:#172033}.title{font-size:25px;font-weight:750}.sub{font-size:13px;fill:#52627a}.head{font-size:15px;font-weight:700}.label{font-size:12px}.small{font-size:11px;fill:#52627a}.value{font-size:12px;font-weight:700}.tick{font-size:10.5px;fill:#64748b}.banner{font-size:12px;font-weight:700;fill:#92400e}.grid{stroke:#e2e8f0;stroke-width:1}.base{stroke:#475569;stroke-width:1.7}.panel{fill:#f8fafc;stroke:#e2e8f0;stroke-width:1}</style>',
        f'<text x="26" y="39" class="title">{escape(title)}</text>',
        f'<text x="26" y="63" class="sub">{escape(subtitle)}</text>',
        f'<rect x="20" y="78" width="{width - 40}" height="34" rx="7" fill="#fffbeb" stroke="#fcd34d"/>',
        '<text x="33" y="100" class="banner">PRACTICE ONLY — the unseen final test remains sealed; final speed NOT MEASURED</text>',
    ]


def log_x(value: float, left: int, right: int, lower: float, upper: float) -> float:
    require(0 < lower < upper, "invalid logarithmic chart bounds")
    clamped = min(upper, max(lower, value))
    return left + (math.log(clamped) - math.log(lower)) / (math.log(upper) - math.log(lower)) * (right - left)


def axis(body: list[str], left: int, right: int, top: int, bottom: int, lower: float, upper: float, *, memory: bool = False) -> None:
    ticks = ((0.0625, "0.0625×"), (0.125, "0.125×"), (0.25, "0.25×"), (0.5, "0.5×"), (0.75, "0.75×"), (1.0, "1× Python"), (1.5, "1.5×"), (2.0, "2×"), (3.0, "3×"), (4.0, "4×"), (8.0, "8×"), (16.0, "16×"), (32.0, "32×"), (64.0, "64×"), (128.0, "128×"), (256.0, "256×"))
    for value, label in ticks:
        if lower <= value <= upper and (memory or value >= 0.25):
            x = log_x(value, left, right, lower, upper)
            body.append(f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{bottom}" class="{"base" if value == 1 else "grid"}"/>')
            body.append(f'<text x="{x:.2f}" y="{top - 8}" text-anchor="middle" class="tick">{escape(label)}</text>')


def linear_memory_x(value: float, left: int, right: int, upper: float) -> float:
    require(upper > 0 and value >= 0, "invalid zero-preserving allocation axis")
    require(value <= upper, "a measured allocation was silently clipped")
    return left + value / upper * (right - left)


def linear_memory_axis(body: list[str], left: int, right: int, top: int, bottom: int, upper: float) -> None:
    ticks = ((0.0, "0×"), (0.25, "0.25×"), (0.5, "0.5×"), (0.75, "0.75×"), (1.0, "1× Python"), (1.5, "1.5×"), (2.0, "2×"), (3.0, "3×"), (4.0, "4×"), (8.0, "8×"), (16.0, "16×"), (32.0, "32×"), (64.0, "64×"), (128.0, "128×"), (256.0, "256×"))
    for value, label in ticks:
        if value <= upper:
            x = linear_memory_x(value, left, right, upper)
            style = "base" if value == 1 else "grid"
            body.append(f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{bottom}" class="{style}"/>')
            body.append(f'<text x="{x:.2f}" y="{top - 8}" text-anchor="middle" class="tick">{escape(label)}</text>')


def legend(body: list[str], *, x: int, y: int, results: tuple[EngineResult, ...]) -> None:
    position = x
    for result in results:
        label = DISPLAY[result.module]
        body.append(f'<circle cx="{position}" cy="{y - 4}" r="5" fill="{COLOURS[result.module]}"/>')
        body.append(f'<text x="{position + 11}" y="{y}" class="small">{escape(label)}</text>')
        position += 85


def grouped(result: EngineResult) -> dict[str, tuple[dict, ...]]:
    output = {api: tuple(row for row in result.rows if row["api"] == api) for api in API_COUNTS}
    for api, rows in output.items():
        require(len(rows) == API_COUNTS[api], "a graph omitted an operation case")
    return output


def overall_chart(data: PracticeResults) -> str:
    width, height = 1320, 526
    left, right = 298, 780
    points = [1.0] + [number for result in data.results for number in (result.ranking["ci95_low"], result.ranking["ci95_high"])]
    lower, upper = min(0.75, min(points) * 0.94), max(1.5, max(points) * 1.08)
    body = svg_open(width, height, "How fast are the replacements compared with Python?", f"The same {CASES} practice tasks · {TRIALS} paired runs · lines show each measured 95% confidence range")
    axis(body, left, right, 152, 424, lower, upper)
    y = 182
    x = log_x(1.0, left, right, lower, upper)
    body.extend((
        f'<text x="28" y="{y + 5}" class="head">Standard Python</text>',
        f'<circle cx="{x:.2f}" cy="{y}" r="6" fill="{COLOURS[BASELINE]}" stroke="#ffffff" stroke-width="1.5"/>',
        f'<text x="800" y="{y + 4}" class="value">Baseline: exactly 1.000× · the same {CASES} tasks</text>',
    ))
    for index, result in enumerate(data.results):
        y = 252 + index * 76
        ranking = result.ranking
        low, point, high = (ranking["ci95_low"], ranking["geomean_speedup"], ranking["ci95_high"])
        if low > 1:
            interpretation = "Clearly faster overall in practice"
        elif high < 1:
            interpretation = "Clearly slower overall in practice"
        else:
            interpretation = "No clear overall speed difference; range crosses 1×"
        colour = COLOURS[result.module]
        body.extend((
            f'<text x="28" y="{y + 5}" class="head">{escape(DISPLAY[result.module])}</text>',
            f'<line x1="{log_x(low, left, right, lower, upper):.2f}" y1="{y}" x2="{log_x(high, left, right, lower, upper):.2f}" y2="{y}" stroke="{colour}" stroke-width="7" stroke-linecap="round"/>',
            f'<circle cx="{log_x(point, left, right, lower, upper):.2f}" cy="{y}" r="6" fill="{colour}" stroke="#ffffff" stroke-width="1.5"/>',
            f'<text x="800" y="{y - 12}" class="value">{fmt(point)} as fast · 95% range {fmt(low)}–{fmt(high)}</text>',
            f'<text x="800" y="{y + 7}" class="small">{escape(interpretation)}</text>',
            f'<text x="800" y="{y + 24}" class="small">{ranking["statistically_faster_cases"]}/{CASES} clearly faster · {ranking["regressions_gt_20pct"]}/{CASES} more than 20% slower</text>',
        ))
    body.append('<text x="26" y="486" class="small">Each range compares one replacement with standard Python; it does not establish a confidence range between replacements.</text>')
    body.append(f'<text x="26" y="505" class="small">All {CORRECTNESS_CHECKS:,} timing correctness checks passed. Public practice is not the unseen final benchmark.</text>')
    return "\n".join((*body, "</svg>", ""))


def outcomes_chart(data: PracticeResults) -> str:
    width, left, right = 1320, 305, 1080
    panel = 191
    height = 177 + panel * len(data.results) + 28
    body = svg_open(width, height, "How often does each replacement win or lose?", f"Measured outcomes and confidence-supported outcomes use the same {CASES} tasks; large slowdowns are counted separately")
    for index, result in enumerate(data.results):
        top = 147 + index * panel
        raw_faster = sum(row["speedup"] > 1 for row in result.rows)
        raw_slower = sum(row["speedup"] < 1 for row in result.rows)
        raw_equal = CASES - raw_faster - raw_slower
        faster = sum(row["ci95_low"] > 1 for row in result.rows)
        slower = sum(row["ci95_high"] < 1 for row in result.rows)
        unclear = CASES - faster - slower
        losses = result.ranking["regressions_gt_20pct"]
        require(raw_faster + raw_equal + raw_slower == CASES, "a measured-outcome graph changed the denominator")
        require(faster + unclear + slower == CASES, "an outcome graph changed the denominator")
        body.append(f'<rect x="18" y="{top - 16}" width="{width - 36}" height="{panel - 9}" rx="9" class="panel"/>')
        body.append(f'<text x="29" y="{top + 6}" class="head">{escape(DISPLAY[result.module])} · all {CASES} cases</text>')
        body.append(f'<text x="29" y="{top + 43}" class="label">Measured result</text>')
        position = float(left)
        for count, colour in ((raw_faster, "#047857"), (raw_equal, "#94a3b8"), (raw_slower, "#dc2626")):
            bar = (right - left) * count / CASES
            if count:
                body.append(f'<rect x="{position:.2f}" y="{top + 26}" width="{bar:.2f}" height="19" fill="{colour}"/>')
                if bar >= 36:
                    body.append(f'<text x="{position + bar / 2:.2f}" y="{top + 40}" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#ffffff">{count}</text>')
            position += bar
        body.append(f'<text x="{right + 12}" y="{top + 42}" class="value">{CASES}/{CASES}</text>')
        body.append(f'<text x="{left}" y="{top + 60}" class="small">{raw_faster}/{CASES} measured faster · {raw_equal}/{CASES} equal · {raw_slower}/{CASES} measured slower</text>')
        body.append(f'<text x="29" y="{top + 88}" class="label">Confidence-based result</text>')
        position = float(left)
        for count, colour in ((faster, "#047857"), (unclear, "#94a3b8"), (slower, "#dc2626")):
            bar = (right - left) * count / CASES
            if count:
                body.append(f'<rect x="{position:.2f}" y="{top + 71}" width="{bar:.2f}" height="19" fill="{colour}"/>')
                if bar >= 36:
                    body.append(f'<text x="{position + bar / 2:.2f}" y="{top + 85}" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#ffffff">{count}</text>')
            position += bar
        body.append(f'<text x="{right + 12}" y="{top + 87}" class="value">{CASES}/{CASES}</text>')
        body.append(f'<text x="{left}" y="{top + 105}" class="small">{faster}/{CASES} clearly faster · {unclear}/{CASES} no clear difference · {slower}/{CASES} clearly slower</text>')
        body.append(f'<text x="29" y="{top + 137}" class="label">Took more than 20% longer</text>')
        body.append(f'<rect x="{left}" y="{top + 120}" width="{right - left}" height="19" fill="#fee2e2"/>')
        body.append(f'<rect x="{left}" y="{top + 120}" width="{(right - left) * losses / CASES:.2f}" height="19" fill="#dc2626"/>')
        body.append(f'<text x="{right + 12}" y="{top + 135}" class="value">{losses}/{CASES}</text>')
        body.append(f'<text x="{left}" y="{top + 157}" class="small">A separate timing rule; every large slowdown remains visible even when its confidence range crosses 1×.</text>')
    body.append(f'<text x="26" y="{height - 12}" class="small">All {EXPECTED_REGRESSIONS} recorded large slowdowns are retained. Practice results are not final results.</text>')
    return "\n".join((*body, "</svg>", ""))


def api_chart(data: PracticeResults) -> str:
    width, left, right = 1320, 331, 860
    row_height = 39
    top = 173
    height = top + len(API_COUNTS) * row_height + 74
    all_points = [geometric(rows) for result in data.results for rows in grouped(result).values()]
    lower, upper = max(0.2, min(0.5, min(all_points) * 0.86)), max(2.0, max(all_points) * 1.12)
    body = svg_open(width, height, "Which everyday matching tasks are faster or slower?", "All 12 public operations; dots are measured group averages, not group confidence ranges")
    legend(body, x=334, y=139, results=data.results)
    axis(body, left, right, top, top + len(API_COUNTS) * row_height, lower, upper)
    per_engine = {result.module: grouped(result) for result in data.results}
    for index, api in enumerate(API_COUNTS):
        y = top + 23 + index * row_height
        count = API_COUNTS[api]
        body.append(f'<text x="28" y="{y + 4}" class="label">{escape(API_LABELS[api])} ({escape(api)}) · n={count}</text>')
        for offset, result in enumerate(data.results):
            value = geometric(per_engine[result.module][api])
            cy = y + (offset - 1) * 8
            body.append(f'<circle cx="{log_x(value, left, right, lower, upper):.2f}" cy="{cy}" r="4.2" fill="{COLOURS[result.module]}" stroke="#ffffff" stroke-width="0.9"/>')
            body.append(f'<text x="{883 + offset * 140}" y="{y + 4}" class="small">{escape(DISPLAY[result.module])} {fmt(value)}</text>')
    body.append(f'<text x="26" y="{height - 35}" class="small">Each operation uses its actual case count; the same cases are retained for C, Rust, Zig, and standard Python.</text>')
    body.append(f'<text x="26" y="{height - 16}" class="small">Dots are per-operation geometric averages only. No per-operation confidence range or candidate-to-candidate significance is claimed.</text>')
    return "\n".join((*body, "</svg>", ""))


def regressions_chart(data: PracticeResults) -> str:
    width, left, right = 1320, 344, 873
    row_height, panel = 27, 382
    height = 163 + panel * len(data.results) + 29
    body = svg_open(width, height, "Every case that took more than 20% longer", f"All {EXPECTED_REGRESSIONS} recorded slowdowns · all 12 operations · zero-count groups remain visible")
    shown = 0
    for index, result in enumerate(data.results):
        top = 150 + index * panel
        cases = grouped(result)
        counts = {api: sum(row["regression_gt_20pct"] for row in rows) for api, rows in cases.items()}
        require(sum(counts.values()) == result.ranking["regressions_gt_20pct"], "a slowdown graph omitted a loss")
        shown += sum(counts.values())
        maximum = max(1, max(counts.values()))
        body.append(f'<rect x="18" y="{top - 18}" width="{width - 36}" height="{panel - 11}" rx="9" class="panel"/>')
        body.append(f'<text x="29" y="{top + 3}" class="head">{escape(DISPLAY[result.module])} · {sum(counts.values())}/{CASES} tasks more than 20% slower</text>')
        for offset, api in enumerate(API_COUNTS):
            y = top + 27 + offset * row_height
            count = counts[api]
            body.extend((
                f'<text x="29" y="{y + 13}" class="label">{escape(API_LABELS[api])} ({escape(api)})</text>',
                f'<rect x="{left}" y="{y}" width="{right - left}" height="17" rx="3" fill="#f1f5f9"/>',
                f'<rect x="{left}" y="{y}" width="{(right - left) * count / maximum:.2f}" height="17" rx="3" fill="#dc2626"/>',
                f'<text x="{right + 13}" y="{y + 13}" class="value">{count}/{API_COUNTS[api]}</text>',
                f'<text x="{right + 95}" y="{y + 13}" class="small">{100 * count / API_COUNTS[api]:.1f}% of this operation</text>',
            ))
    require(shown == EXPECTED_REGRESSIONS, "the chart did not display all 426 slowdowns")
    body.append(f'<text x="26" y="{height - 12}" class="small">A loss is counted only when the replacement takes strictly more than 20% longer than standard Python.</text>')
    return "\n".join((*body, "</svg>", ""))


def memory_chart(data: PracticeResults) -> str:
    width, left, right = 1320, 340, 850
    row_height, panel = 29, 409
    height = 173 + panel * len(data.results) + 54
    medians = [statistics.median(row["peak_traced_ratio"] for row in rows) for result in data.results for rows in grouped(result).values()]
    upper = max(2.0, max(medians, default=1.0) * 1.12)
    body = svg_open(width, height, "Python-visible temporary allocations", f"Median Python-traced temporary allocation versus Python · all {CASES} tasks per engine · lower is better")
    for index, result in enumerate(data.results):
        top = 151 + index * panel
        groups = grouped(result)
        overall = float(statistics.median(row["peak_traced_ratio"] for row in result.rows))
        body.append(f'<rect x="18" y="{top - 18}" width="{width - 36}" height="{panel - 10}" rx="9" class="panel"/>')
        body.append(f'<text x="29" y="{top + 3}" class="head">{escape(DISPLAY[result.module])} · {fmt(overall)} median Python-traced allocations · {CASES} cases</text>')
        linear_memory_axis(body, left, right, top + 35, top + 42 + len(API_COUNTS) * row_height, upper)
        for offset, api in enumerate(API_COUNTS):
            rows = groups[api]
            y = top + 59 + offset * row_height
            median = float(statistics.median(row["peak_traced_ratio"] for row in rows))
            zeros = sum(row["peak_traced_ratio"] == 0 for row in rows)
            body.extend((
                f'<text x="29" y="{y + 4}" class="label">{escape(API_LABELS[api])} ({escape(api)})</text>',
                f'<circle cx="{linear_memory_x(median, left, right, upper):.2f}" cy="{y}" r="4.8" fill="{COLOURS[result.module]}" stroke="#ffffff" stroke-width="1"/>',
                f'<text x="{right + 15}" y="{y + 4}" class="value">{fmt(median)}</text>',
                f'<text x="{right + 96}" y="{y + 4}" class="small">n={len(rows)} · {zeros} zero Python-traced observations</text>',
            ))
    body.append(f'<text x="26" y="{height - 36}" class="small">Measures Python-traced temporary allocations only in a shared process; it does not measure native, total, peak-process, or exclusive-engine memory.</text>')
    body.append(f'<text x="26" y="{height - 17}" class="small">The linear axis preserves every true zero; zero traced allocation does not mean zero native or total memory.</text>')
    return "\n".join((*body, "</svg>", ""))


def rankings_chart(data: PracticeResults) -> str:
    width, left, right = 1320, 250, 746
    row_height, top = 71, 171
    height = top + (len(data.results) + 1) * row_height + 93
    values = [1.0] + [number for result in data.results for number in (result.ranking["ci95_low"], result.ranking["ci95_high"])]
    lower, upper = min(0.75, min(values) * 0.94), max(1.5, max(values) * 1.08)
    body = svg_open(width, height, "Overall practice results at a glance", f"Ordered by the measured {CASES}-case average; each confidence range compares only with Python")
    axis(body, left, right, top + 12, top + (len(data.results) + 1) * row_height - 8, lower, upper)
    body.append(f'<text x="768" y="{top + 3}" class="small">Overall speed and 95% range</text>')
    body.append(f'<text x="1062" y="{top + 3}" class="small">Clear wins</text>')
    body.append(f'<text x="1176" y="{top + 3}" class="small">&gt;20% slower</text>')
    for index, result in enumerate(data.results):
        y = top + 44 + index * row_height
        ranking = result.ranking
        low, point, high = ranking["ci95_low"], ranking["geomean_speedup"], ranking["ci95_high"]
        colour = COLOURS[result.module]
        body.extend((
            f'<text x="28" y="{y + 4}" class="head">{index + 1}. {escape(DISPLAY[result.module])}</text>',
            f'<line x1="{log_x(low, left, right, lower, upper):.2f}" y1="{y}" x2="{log_x(high, left, right, lower, upper):.2f}" y2="{y}" stroke="{colour}" stroke-width="6" stroke-linecap="round"/>',
            f'<circle cx="{log_x(point, left, right, lower, upper):.2f}" cy="{y}" r="5.5" fill="{colour}" stroke="#ffffff" stroke-width="1"/>',
            f'<text x="768" y="{y + 4}" class="value">{fmt(point)} [{fmt(low)}–{fmt(high)}]</text>',
            f'<text x="1062" y="{y + 4}" class="value">{ranking["statistically_faster_cases"]}/{CASES}</text>',
            f'<text x="1176" y="{y + 4}" class="value">{ranking["regressions_gt_20pct"]}/{CASES}</text>',
        ))
        if low <= 1 <= high:
            body.append(f'<text x="768" y="{y + 20}" class="small">Range crosses 1×: no clear overall advantage.</text>')
    y = top + 44 + len(data.results) * row_height
    body.append(f'<text x="28" y="{y + 4}" class="head">Standard Python</text>')
    body.append(f'<circle cx="{log_x(1, left, right, lower, upper):.2f}" cy="{y}" r="5.5" fill="{COLOURS[BASELINE]}"/>')
    body.append(f'<text x="768" y="{y + 4}" class="value">Exactly 1.000× baseline · {CASES} identical tasks</text>')
    body.append(f'<text x="26" y="{height - 34}" class="small">Ordering describes practice estimates only; it does not prove a statistically significant difference between replacements.</text>')
    body.append(f'<text x="26" y="{height - 15}" class="small">The unseen final test remains sealed. Final speed and the final winner: NOT MEASURED.</text>')
    return "\n".join((*body, "</svg>", ""))


def build_charts(data: PracticeResults) -> dict[str, str]:
    charts = {
        "overall": overall_chart(data),
        "outcomes": outcomes_chart(data),
        "api": api_chart(data),
        "regressions": regressions_chart(data),
        "memory": memory_chart(data),
        "rankings": rankings_chart(data),
    }
    require(tuple(charts) == CHART_SUFFIXES, "a required practice graph was omitted or replaced")
    for suffix, content in charts.items():
        require("PRACTICE ONLY" in content, f"{suffix} omitted its practice-only disclosure")
        require("final speed NOT MEASURED" in content, f"{suffix} invented a final performance result")
        require(str(CASES) in content, f"{suffix} omitted the shared 624-case denominator")
        for result in data.results:
            require(escape(DISPLAY[result.module]) in content, f"{suffix} omitted {DISPLAY[result.module]}")
        try:
            ElementTree.fromstring(content)
        except ElementTree.ParseError as error:
            raise ValueError(f"generated invalid practice SVG: {suffix}") from error
    return charts


def synthetic_documents() -> tuple[dict, dict, tuple[bytes, ...], str, str, str]:
    source_hash = "a" * 64
    fingerprints = {role: source_hash for role in set(NATIVE_PATHS) | {f"{BASELINE}:module"}}
    api_sequence = [api for api, count in API_COUNTS.items() for _ in range(count)]
    require(len(api_sequence) == CASES, "invalid synthetic public practice denominator")
    case_results: list[dict] = []
    rankings: list[dict] = []
    losses = {C_ENGINE: 49, RUST: 139, ZIG: 238}
    wins = {C_ENGINE: 426, RUST: 247, ZIG: 229}
    fast_speed = {C_ENGINE: 1.45, RUST: 1.28, ZIG: 1.16}
    for module in CANDIDATES:
        rows: list[dict] = []
        for index, api in enumerate(api_sequence):
            if index < losses[module]:
                speed, low, high = 0.70, 0.65, 0.75
            elif index < losses[module] + wins[module]:
                speed = fast_speed[module]
                low, high = speed - 0.04, speed + 0.04
            else:
                speed, low, high = 0.99, 0.94, 1.04
            baseline_ns = float(1_000 + index)
            rows.append({
                "api": api,
                "baseline_ns": baseline_ns,
                "candidate": module,
                "candidate_ns": baseline_ns / (speed * 1.013),
                "case": f"cal.synthetic.{index:04d}",
                "category": f"synthetic-category-{index % 260:03d}",
                "ci95_high": high,
                "ci95_low": low,
                "cohort": "calibration",
                "input": "text",
                "lifecycle": "compiled",
                "peak_traced_ratio": float(index % 9) / 4,
                "regression_gt_20pct": speed < 5 / 6,
                "result_density": "one",
                "speedup": speed,
                "statistically_faster": low > 1,
                "weight": 1,
            })
        point = geometric(rows)
        rankings.append({
            "candidate": module,
            "cases": CASES,
            "ci95_high": point * 1.08,
            "ci95_low": point * 0.92,
            "cohort": "calibration",
            "geomean_speedup": point,
            "regressions_gt_20pct": losses[module],
            "statistically_faster_cases": wins[module],
            "weight": CASES,
        })
        case_results.extend(rows)

    raw_lines: list[bytes] = []
    for index, api in enumerate(api_sequence):
        for trial in range(TRIALS):
            for module in MODULES:
                line = {
                    "api": api,
                    "case": f"cal.synthetic.{index:04d}",
                    "category": f"synthetic-category-{index % 260:03d}",
                    "cohort": "calibration",
                    "elapsed_ns": 1000 + index + trial,
                    "expected_sha256": hashlib.sha256(f"synthetic-case-{index:04d}".encode("ascii")).hexdigest(),
                    "frozen_operations": 1,
                    "input": "text",
                    "lifecycle": "compiled",
                    "module": module,
                    "ns_per_op": float(1000 + index + trial),
                    "operations": 1,
                    "peak_traced_bytes": index % 7,
                    "result_density": "one",
                    "schema": RAW_SCHEMA,
                    "trial": trial,
                }
                raw_lines.append((json.dumps(line, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii"))
    raw_bytes = b"".join(raw_lines)
    raw_digest = hashlib.sha256(raw_bytes).hexdigest()
    compressed_digest = hashlib.sha256(gzip.compress(raw_bytes, mtime=0)).hexdigest()
    regressions = [row for row in case_results if row["regression_gt_20pct"]]
    proofs = [{
        "module": module,
        "correctness_checks": EDGE_CHECKS,
        "script_sha256": ORACLE_SOURCE_SHA256,
        "actual_sha256": ORACLE_ANSWERS_SHA256,
    } for module in CANDIDATES]
    summary = {
        "all_bounded_workload_categories": 260,
        "bootstrap_samples": BOOTSTRAPS,
        "candidate_binary_sha256_after": fingerprints,
        "candidate_binary_sha256_before": copy.deepcopy(fingerprints),
        "case_results": case_results,
        "cases": CASES,
        "cohort": "calibration",
        "compressed_raw_sha256": compressed_digest,
        "correctness_checks": CORRECTNESS_CHECKS,
        "exclusive_slot": SLOT,
        "expected_sha256": PRACTICE_SHA256,
        "failed": 0,
        "holdout_accessed": False,
        "modules": list(MODULES),
        "paired_raw_rows": RAW_ROWS,
        "public_operations": copy.deepcopy(API_COUNTS),
        "rankings": rankings,
        "raw_sha256": raw_digest,
        "regressions": regressions,
        "schema": SUMMARY_SCHEMA,
        "strict_regression_speedup_threshold": 5 / 6,
        "trials": TRIALS,
        "verified_edge_oracles": proofs,
        "warmups": 4,
    }
    summary_digest = hashlib.sha256(json.dumps(summary, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
    integrity = {
        "bootstrap_draws": BOOTSTRAPS,
        "candidate_binary_sha256_after": copy.deepcopy(fingerprints),
        "candidate_binary_sha256_before": copy.deepcopy(fingerprints),
        "candidate_case_count": CASES * len(CANDIDATES),
        "cases_per_candidate": CASES,
        "compressed_raw_sha256": compressed_digest,
        "correctness_checks": CORRECTNESS_CHECKS,
        "holdout_accessed": False,
        "module_order": list(MODULES),
        "rankings": copy.deepcopy(rankings),
        "raw_rows": RAW_ROWS,
        "raw_sha256": raw_digest,
        "regressions": copy.deepcopy(regressions),
        "result": "PASS",
        "schema": INTEGRITY_SCHEMA,
        "strict_regressions": EXPECTED_REGRESSIONS,
        "summary_sha256": summary_digest,
        "timing_performed": False,
        "trials_per_module_case": TRIALS,
        "verified_edge_oracles": copy.deepcopy(proofs),
    }
    return summary, integrity, tuple(raw_lines), summary_digest, compressed_digest, raw_digest


def expect_rejection(check, label: str) -> None:
    try:
        check()
    except (ValueError, TypeError, KeyError, OverflowError):
        return
    raise ValueError(f"synthetic safety test accepted {label}")


def self_test() -> None:
    summary, integrity, raw_lines, summary_digest, compressed_digest, raw_digest = synthetic_documents()
    results = check_summary(summary)
    check_integrity(summary, integrity, summary_digest=summary_digest, compressed_digest=compressed_digest, raw_digest=raw_digest)
    check_raw_lines(raw_lines, summary, expected_digest=raw_digest)
    data = PracticeResults(summary, integrity, tuple(sorted(results, key=lambda item: (-item.ranking["geomean_speedup"], DISPLAY[item.module]))))
    charts = build_charts(data)

    def reject_summary(change, label: str) -> None:
        poisoned = copy.deepcopy(summary)
        change(poisoned)
        expect_rejection(lambda: check_summary(poisoned), label)

    tests = (
        (lambda value: value.__setitem__("holdout_accessed", True), "hidden-test access"),
        (lambda value: value.__setitem__("cohort", "holdout"), "a hidden cohort"),
        (lambda value: value.__setitem__("cases", CASES - 1), "a changed case denominator"),
        (lambda value: value.__setitem__("trials", TRIALS - 1), "a dropped paired trial"),
        (lambda value: value.__setitem__("bootstrap_samples", BOOTSTRAPS - 1), "a changed confidence protocol"),
        (lambda value: value.__setitem__("paired_raw_rows", RAW_ROWS - 1), "a dropped raw measurement"),
        (lambda value: value.__setitem__("correctness_checks", CORRECTNESS_CHECKS - 1), "a dropped timing correctness gate"),
        (lambda value: value.__setitem__("modules", list(reversed(MODULES))), "a changed paired-engine order"),
        (lambda value: value.__setitem__("strict_regression_speedup_threshold", 0.8), "a weakened slowdown rule"),
        (lambda value: value["case_results"].pop(), "a dropped candidate case"),
        (lambda value: value["case_results"].__setitem__(1, copy.deepcopy(value["case_results"][0])), "a duplicated candidate case"),
        (lambda value: value["case_results"][0].__setitem__("cohort", "holdout"), "a hidden candidate case"),
        (lambda value: value["case_results"][0].__setitem__("weight", 2), "a silently reweighted case"),
        (lambda value: value["case_results"][0].__setitem__("statistically_faster", True), "an invented statistically faster case"),
        (lambda value: value["case_results"][0].__setitem__("regression_gt_20pct", False), "a hidden large slowdown"),
        (lambda value: value["case_results"][0].__setitem__("peak_traced_ratio", -1), "negative Python-traced allocations"),
        (lambda value: value["rankings"][0].__setitem__("statistically_faster_cases", value["rankings"][0]["statistically_faster_cases"] + 1), "an invented faster-case ranking"),
        (lambda value: value["rankings"][0].__setitem__("regressions_gt_20pct", value["rankings"][0]["regressions_gt_20pct"] - 1), "a hidden slowdown ranking"),
        (lambda value: value["rankings"][0].__setitem__("ci95_low", value["rankings"][0]["geomean_speedup"] + 1), "an invalid overall confidence range"),
        (lambda value: value["regressions"].pop(), "an omitted one of the 426 slowdowns"),
        (lambda value: value["public_operations"].pop("scanner"), "an omitted operation group"),
        (lambda value: value["verified_edge_oracles"].pop(), "an unqualified independent candidate"),
        (lambda value: value["candidate_binary_sha256_after"].__setitem__(f"{ZIG}:native-engine", "b" * 64), "a changed measured native engine"),
    )
    for change, label in tests:
        reject_summary(change, label)

    integrity_tests = (
        ("summary_sha256", "0" * 64),
        ("compressed_raw_sha256", "0" * 64),
        ("raw_sha256", "0" * 64),
        ("result", "FAIL"),
        ("strict_regressions", EXPECTED_REGRESSIONS - 1),
        ("candidate_case_count", CASES * len(CANDIDATES) - 1),
        ("timing_performed", True),
    )
    for key, replacement in integrity_tests:
        poisoned = copy.deepcopy(integrity)
        poisoned[key] = replacement
        expect_rejection(lambda value=poisoned: check_integrity(summary, value, summary_digest=summary_digest, compressed_digest=compressed_digest, raw_digest=raw_digest), f"an unbound or invalid integrity field: {key}")
    expect_rejection(lambda: check_raw_lines(raw_lines[:-1], summary, expected_digest=raw_digest), "a missing raw paired measurement")
    expect_rejection(lambda: check_raw_lines(raw_lines, summary, expected_digest="0" * 64), "a fake raw measurement digest")
    switched = json.loads(raw_lines[1])
    switched["expected_sha256"] = "0" * 64
    poisoned_raw = (raw_lines[0], (json.dumps(switched, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii"), *raw_lines[2:])
    expect_rejection(lambda: check_raw_lines(poisoned_raw, summary, expected_digest=raw_digest), "a switched per-case correctness answer")

    require(build_charts(data) == charts, "the practice-only SVG charts are not deterministic")
    for result in data.results:
        rank = result.ranking
        for text in (DISPLAY[result.module], fmt(rank["geomean_speedup"]), fmt(rank["ci95_low"]), fmt(rank["ci95_high"]), f'{rank["statistically_faster_cases"]}/{CASES}', f'{rank["regressions_gt_20pct"]}/{CASES}'):
            require(escape(text) in charts["overall"], f"the headline graph omitted {text}")
        for suffix in ("api", "regressions", "memory"):
            for api in API_COUNTS:
                require(f"({escape(api)})" in charts[suffix], f"the {suffix} graph omitted {api}")
    require("shared process" in charts["memory"] and "does not measure native" in charts["memory"], "the memory graph omitted its actual limitations")
    require(str(EXPECTED_REGRESSIONS) in charts["regressions"], "the regression graph omitted the full slowdown count")
    print(json.dumps({
        "result": "PASS",
        "schema": f"{INTEGRITY_SCHEMA}-charts-self-test",
        "synthetic_only": True,
        "holdout_accessed": False,
        "timing_performed": False,
        "modules": list(MODULES),
        "cases_per_candidate": CASES,
        "candidate_case_count": CASES * len(CANDIDATES),
        "raw_rows": RAW_ROWS,
        "correctness_checks": CORRECTNESS_CHECKS,
        "strict_regressions": EXPECTED_REGRESSIONS,
        "corruption_checks": len(tests) + len(integrity_tests) + 3,
        "chart_count": len(charts),
        "charts_deterministic": True,
        "unseen_final_result": "NOT MEASURED",
    }, sort_keys=True))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render six independently audited, practice-only C/Rust/Zig comparisons with standard Python.")
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY, help="the complete same-run public-practice summary")
    parser.add_argument("--raw", type=Path, default=DEFAULT_RAW, help="the complete compressed public-practice trial log")
    parser.add_argument("--integrity", type=Path, default=DEFAULT_INTEGRITY, help="the independently verified passing practice-integrity report")
    parser.add_argument("--prefix", type=Path, default=DEFAULT_PREFIX, help="output prefix for exactly six practice-only SVG charts")
    parser.add_argument("--self-test", action="store_true", help="run deterministic synthetic-only corruption and SVG checks; never read real results")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.self_test:
        self_test()
        return
    prefix = args.prefix.resolve()
    require(prefix.parent == EVIDENCE.resolve(), "practice graphs may only be written to performance/v7/evidence")
    require(prefix.name == DEFAULT_PREFIX.name, "refusing to overwrite unrelated practice evidence")
    data = load_results(args.summary.resolve(), args.raw.resolve(), args.integrity.resolve())
    charts = build_charts(data)
    for suffix in CHART_SUFFIXES:
        path = prefix.parent / f"{prefix.name}-{suffix}.svg"
        path.write_text(charts[suffix], encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
