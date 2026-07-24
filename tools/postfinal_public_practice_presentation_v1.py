#!/usr/bin/env python3
"""Present the independently verified V5 public results as six clear SVGs."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import sys
import xml.etree.ElementTree as ElementTree
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent.parent
VERSION = "postfinal-public-practice-v5"
PUBLIC_ROOT = ROOT / "performance" / "postfinal-public-v5"
EVIDENCE = PUBLIC_ROOT / "evidence"
MANIFEST = PUBLIC_ROOT / "manifest.json"
SUMMARY = EVIDENCE / f"{VERSION}-summary.json"
INTEGRITY = EVIDENCE / f"{VERSION}-integrity.json"
RAW = EVIDENCE / f"{VERSION}-raw.jsonl.gz"
MANIFEST_SHA256 = (
    "c9950c87079ccc1909ba4470ed573b08afe1f275b85a8932cbfe83b547b24f96"
)
SUMMARY_SHA256 = (
    "d9dd1e712a97d0d1716308e1e468e0c9d2b6d6058e501bccd871492bc66a6b4c"
)
INTEGRITY_SHA256 = (
    "ff86c9421747373df9f5cf640f8a081331661c7d79e8b12969cb0952c86d9246"
)
RUNNER_SHA256 = (
    "f4294a3b5434f43a92970635a958cf3b39db0eb926adef50e242ac0f6b9a1d22"
)

CASES = 8_192
CATEGORIES = 260
TRIALS = 13
WARMUPS = 4
BOOTSTRAPS = 2_000
RAW_ROWS = 425_984
CORRECTNESS_CHECKS = 1_277_952
CONFIDENCE_INTERVALS = 24_579
REGRESSIONS = 5_173
RUNTIME_GUARDS = 65_544
MODULES = (
    "re",
    "candidates.rust_candidate",
    "candidates.vm_candidate",
    "candidates.zig_candidate",
)
CANDIDATES = MODULES[1:]
OPERATIONS = {
    "compile": 210,
    "escape": 161,
    "findall": 2_040,
    "finditer": 2_041,
    "fullmatch": 358,
    "match": 229,
    "match-surface": 241,
    "scanner": 427,
    "search": 1_057,
    "split": 451,
    "sub": 447,
    "subn": 530,
}
SUFFIXES = ("overall", "outcomes", "api", "regressions", "memory", "rankings")
LABELS = {
    "candidates.rust_candidate": "Rust",
    "candidates.vm_candidate": "C",
    "candidates.zig_candidate": "Zig",
}
COLORS = {
    "candidates.rust_candidate": "#d17852",
    "candidates.vm_candidate": "#238b86",
    "candidates.zig_candidate": "#7766c9",
}
MEMORY_LIMITATION = (
    "Tracemalloc reports Python-visible temporary allocations. "
    "RSS and high-water marks are process-level observations in "
    "separate dedicated engine workers; they do not establish exact "
    "per-allocation native-engine memory."
)
UNIVERSAL_FIELDS = (
    "python_re_universal_oracle_source_path",
    "python_re_universal_oracle_source_sha256",
    "python_re_universal_oracle_report_path",
    "python_re_universal_oracle_report_sha256",
    "python_re_universal_oracle_schema",
    "python_re_universal_oracle_status",
    "python_re_universal_oracle_selected",
    "python_re_universal_oracle_candidates",
    "python_re_universal_oracle_cases",
    "python_re_universal_oracle_comparisons_per_case",
    "python_re_universal_oracle_comparisons_per_candidate",
    "python_re_universal_oracle_total_comparisons",
    "python_re_universal_oracle_mismatches",
    "python_re_universal_oracle_seed",
    "python_re_universal_oracle_seed_domain",
    "python_re_universal_oracle_case_sha256",
    "python_re_universal_oracle_grammar_family_count",
    "python_re_universal_oracle_input_stratum_count",
    "python_re_universal_oracle_examples_per_stratum",
    "python_re_universal_oracle_original_audit_sha256",
    "python_re_universal_oracle_postfinal_no_delegation_audit_sha256",
    "python_re_universal_oracle_frozen_source_path",
    "python_re_universal_oracle_frozen_source_sha256",
)
FOOTER = "Public test only; final holdout not run. No final winner."
SVG_NAMESPACE = "http://www.w3.org/2000/svg"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def valid_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def require_candidate_free() -> None:
    loaded = [
        name
        for name in sys.modules
        if any(name == candidate or name.startswith(candidate + ".") for candidate in CANDIDATES)
    ]
    require(not loaded, "the public presenter imported a production candidate")


def finite(value: object, label: str, *, zero: bool = False) -> float:
    require(
        isinstance(value, (int, float)) and not isinstance(value, bool),
        f"the verified public {label} is not a number",
    )
    number = float(value)
    require(math.isfinite(number), f"the verified public {label} is not finite")
    require(number >= 0 if zero else number > 0, f"the verified public {label} is invalid")
    return number


def same_float(actual: float, expected: float, label: str) -> None:
    require(
        math.isclose(actual, expected, rel_tol=1e-11, abs_tol=1e-12),
        f"the independently verified public {label} changed",
    )


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in result, "a verified public JSON key was duplicated")
        result[key] = value
    return result


def reject_json_constant(value: str) -> None:
    raise ValueError(f"a verified public JSON number is nonfinite: {value}")


def read_verified_json(path: Path, *, expected: Path, digest: str) -> dict[str, Any]:
    require(path.resolve() == expected.resolve(), "a public evidence path escaped the exact V5 root")
    require(valid_sha256(digest), "an expected public evidence SHA-256 is invalid")
    payload = path.read_bytes()
    require(
        hashlib.sha256(payload).hexdigest() == digest,
        "the exact independently verified public evidence SHA-256 changed",
    )
    result = json.loads(
        payload.decode("utf-8"),
        object_pairs_hook=unique_object,
        parse_constant=reject_json_constant,
    )
    require(isinstance(result, dict), "verified public evidence is not a JSON object")
    return result


@dataclass(frozen=True)
class PublicResults:
    manifest: dict[str, Any]
    summary: dict[str, Any]
    integrity: dict[str, Any]
    rankings: tuple[dict[str, Any], ...]
    rows_by_candidate: dict[str, tuple[dict[str, Any], ...]]
    losses_by_candidate: dict[str, tuple[dict[str, Any], ...]]
    operations: dict[str, int]


def require_stage05(document: dict[str, Any], reference: list[dict[str, Any]]) -> None:
    artifacts = document.get("stage05_correctness_artifacts")
    require(artifacts == reference and len(reference) == 12, "a verified stage-05 correctness proof changed")
    expected_roles = {
        f"{family}-{role}"
        for family in ("rust", "vm", "zig")
        for role in ("edge", "deep-public-contract", "observability", "complete-correctness-campaign")
    }
    require(
        {artifact.get("role") for artifact in artifacts if isinstance(artifact, dict)} == expected_roles,
        "one of the 12 verified stage-05 correctness roles is missing",
    )
    for artifact in artifacts:
        require(valid_sha256(artifact.get("sha256")), "a stage-05 correctness fingerprint is invalid")
        if artifact["role"] == "vm-deep-public-contract":
            require(
                artifact.get("path")
                == "candidates/audits/RUST-V8-DEEP-CONTRACT-C-POST-FINAL-STAGE-05-UNIVERSAL-PARITY.json.gz",
                "the independently verified C-family deep proof was substituted",
            )


def require_universal(document: dict[str, Any], reference: dict[str, Any]) -> None:
    require(len(UNIVERSAL_FIELDS) == 23, "the full universal compatibility proof is incomplete")
    for field in UNIVERSAL_FIELDS:
        require(field in document and document[field] == reference.get(field), f"the verified public {field} changed")
    expected = {
        "python_re_universal_oracle_status": "PASS",
        "python_re_universal_oracle_selected": "all",
        "python_re_universal_oracle_candidates": ["rust", "vm", "zig"],
        "python_re_universal_oracle_cases": CASES,
        "python_re_universal_oracle_comparisons_per_case": 48,
        "python_re_universal_oracle_comparisons_per_candidate": 393_216,
        "python_re_universal_oracle_total_comparisons": 1_179_648,
        "python_re_universal_oracle_mismatches": 0,
        "python_re_universal_oracle_grammar_family_count": 16,
        "python_re_universal_oracle_input_stratum_count": 16,
        "python_re_universal_oracle_examples_per_stratum": 32,
    }
    for field, value in expected.items():
        require(document.get(field) == value, f"the verified complete Python compatibility {field} changed")
    for field in UNIVERSAL_FIELDS:
        if field.endswith("sha256"):
            require(valid_sha256(document.get(field)), f"the verified compatibility {field} is invalid")


def validate_documents(
    manifest: dict[str, Any],
    summary: dict[str, Any],
    integrity: dict[str, Any],
    *,
    manifest_sha256: str,
    summary_sha256: str,
    integrity_sha256: str,
    runner_sha256: str,
) -> PublicResults:
    """Reconcile the exact independent replay with every public case and loss."""

    require_candidate_free()
    require(manifest_sha256 == MANIFEST_SHA256, "the externally pinned V5 manifest was substituted")
    require(summary_sha256 == SUMMARY_SHA256, "the independently replayed V5 summary was substituted")
    require(integrity_sha256 == INTEGRITY_SHA256, "the independently replayed V5 integrity was substituted")
    require(runner_sha256 == RUNNER_SHA256, "the externally pinned V5 runner was substituted")
    require(
        manifest.get("schema") == "rebar-rust-balanced-calibration-plan-v7"
        and manifest.get("postfinal_schema") == "rebar-postfinal-public-practice-plan-v5",
        "the frozen public V5 manifest schema changed",
    )
    require(
        summary.get("schema") == "rebar-rust-balanced-calibration-pilot-v7"
        and summary.get("postfinal_schema") == "rebar-postfinal-public-practice-report-v5",
        "the measured public V5 summary schema changed",
    )
    require(
        integrity.get("schema") == "rebar-postfinal-public-practice-integrity-v5"
        and integrity.get("result") == "PASS",
        "the independent public V5 integrity replay did not pass",
    )
    for name, document in (("manifest", manifest), ("summary", summary), ("integrity", integrity)):
        require(document.get("protocol_version") == VERSION, f"the verified public {name} uses another protocol")
        require(document.get("cohort") == "calibration", f"the verified public {name} is not calibration only")
        require(document.get("holdout_accessed") is False, f"the verified public {name} claims holdout access")
        require(
            document.get("held_out_cases_generated") == 0
            and document.get("held_out_records_deserialized") == 0,
            f"the verified public {name} contains nonpublic cases",
        )
        require(document.get("runner_sha256") == runner_sha256, f"the verified public {name} changed the runner")
        require(document.get("failed") == 0, f"the verified public {name} contains a failed check")

    require(manifest.get("exclusive_slot") == VERSION, "the frozen public slot changed")
    require(summary.get("exclusive_slot") == VERSION, "the measured public slot changed")
    require(manifest.get("modules") == list(MODULES), "the frozen public engines changed")
    require(summary.get("modules") == list(MODULES), "the measured public engines changed")
    require(integrity.get("module_order") == list(MODULES), "the replayed public engines changed")
    require(manifest.get("cases") == CASES and summary.get("cases") == CASES, "the public denominator is not 8,192")
    require(
        manifest.get("all_bounded_workload_categories") == CATEGORIES
        and summary.get("all_bounded_workload_categories") == CATEGORIES,
        "one of the 260 frozen public categories is missing",
    )
    require(
        manifest.get("public_operations") == OPERATIONS
        and summary.get("public_operations") == OPERATIONS,
        "one of the exact 12 frozen public operation quotas changed",
    )
    require(sum(OPERATIONS.values()) == CASES, "the frozen operation quotas changed the public denominator")
    require(
        manifest.get("frozen_trials") == TRIALS
        and manifest.get("frozen_warmups") == WARMUPS
        and manifest.get("frozen_bootstrap_samples") == BOOTSTRAPS
        and summary.get("trials") == TRIALS
        and summary.get("warmups") == WARMUPS
        and summary.get("bootstrap_samples") == BOOTSTRAPS,
        "the frozen public trials, warmups, or bootstrap denominator changed",
    )
    require(
        summary.get("manifest_path") == str(MANIFEST)
        and summary.get("manifest_sha256") == manifest_sha256
        and summary.get("raw_path") == str(RAW),
        "the measured public summary escaped its frozen V5 evidence",
    )
    require(
        integrity.get("manifest_sha256") == manifest_sha256
        and integrity.get("summary_sha256") == summary_sha256,
        "the independent replay does not authenticate the exact frozen summary",
    )
    for field in ("raw_sha256", "compressed_raw_sha256"):
        require(
            valid_sha256(summary.get(field)) and integrity.get(field) == summary[field],
            f"the independently replayed public {field} changed",
        )
    require(
        summary.get("paired_raw_rows") == RAW_ROWS
        and integrity.get("raw_rows") == RAW_ROWS
        and RAW_ROWS == CASES * len(MODULES) * TRIALS,
        "the complete 425,984-row public timing stream is incomplete",
    )
    require(
        summary.get("correctness_checks") == CORRECTNESS_CHECKS
        and integrity.get("correctness_checks") == CORRECTNESS_CHECKS
        and CORRECTNESS_CHECKS == RAW_ROWS * 3,
        "the complete 1,277,952-check public correctness gates are incomplete",
    )
    require(
        integrity.get("cases_per_candidate") == CASES
        and integrity.get("candidate_case_count") == CASES * len(CANDIDATES)
        and integrity.get("trials_per_module_case") == TRIALS
        and integrity.get("bootstrap_draws") == BOOTSTRAPS
        and integrity.get("confidence_intervals_recomputed") == CONFIDENCE_INTERVALS
        and CONFIDENCE_INTERVALS == CASES * len(CANDIDATES) + len(CANDIDATES),
        "the independent replay omitted a public case or confidence interval",
    )
    require(
        integrity.get("strict_regressions") == REGRESSIONS,
        "the independently verified 5,173 public losses changed",
    )
    require(
        summary.get("persistent_isolated_worker_count") == len(MODULES)
        and integrity.get("persistent_isolated_worker_count") == len(MODULES)
        and summary.get("per_case_runtime_guard_checks") == RUNTIME_GUARDS
        and integrity.get("per_case_runtime_guard_checks") == RUNTIME_GUARDS,
        "the four isolated public workers or their runtime guards changed",
    )
    require(
        summary.get("controller_candidate_imported") is False
        and integrity.get("controller_candidate_imported") is False
        and integrity.get("candidate_imported") is False
        and integrity.get("timing_performed") is False,
        "the independent replay imported a candidate or performed new timing",
    )
    require(
        integrity.get("memory_limitation") == MEMORY_LIMITATION,
        "the replay overclaims native, process-level, or final memory",
    )
    require(
        integrity.get("from_scratch_control_count") == 76
        and integrity.get("verified_independent_engine_count") == len(CANDIDATES)
        and integrity.get("verified_native_library_count") == 5,
        "the original independent source or native-library audit is incomplete",
    )
    require(
        all(document.get("postfinal_no_delegation_control_count") == 32 for document in (manifest, summary, integrity)),
        "the 32-control no-delegation proof changed",
    )
    for field in ("from_scratch_audit_sha256", "from_scratch_audit_source_sha256", "postfinal_no_delegation_audit_sha256"):
        require(
            valid_sha256(manifest.get(field))
            and summary.get(field) == manifest[field]
            and integrity.get(field) == manifest[field],
            f"the independently authenticated public {field} changed",
        )
    native = manifest.get("native_elf_fingerprints")
    sources = manifest.get("qualified_source_fingerprints")
    require(isinstance(native, dict) and len(native) == 5, "an independently verified native engine is missing")
    require(isinstance(sources, dict) and bool(sources), "the qualified engine source fingerprints are missing")
    require(
        integrity.get("native_elf_fingerprints") == native
        and integrity.get("qualified_source_fingerprints") == sources,
        "the independently replayed source or native fingerprints changed",
    )
    before = summary.get("candidate_binary_sha256_before")
    require(
        isinstance(before, dict)
        and bool(before)
        and before == summary.get("candidate_binary_sha256_after")
        and before == integrity.get("candidate_binary_sha256_before")
        and before == integrity.get("candidate_binary_sha256_after"),
        "a loaded public candidate artifact changed before independent replay",
    )
    controls = integrity.get("self_test")
    require(isinstance(controls, dict) and controls.get("result") == "PASS", "the independent replay controls did not pass")
    require_universal(manifest, manifest)
    require_universal(summary, manifest)
    require_universal(integrity, manifest)
    artifacts = manifest.get("stage05_correctness_artifacts")
    require(isinstance(artifacts, list), "all 12 independent stage-05 proofs are missing")
    require_stage05(manifest, artifacts)
    require_stage05(summary, artifacts)
    require_stage05(integrity, artifacts)

    selected = manifest.get("selected_cases")
    require(isinstance(selected, list) and len(selected) == CASES, "the exact frozen 8,192-case public selection is incomplete")
    frozen: dict[str, dict[str, Any]] = {}
    for item in selected:
        require(isinstance(item, dict), "a frozen public case is invalid")
        case = item.get("case")
        require(isinstance(case, str) and case.startswith("cal.") and case not in frozen, "a frozen public case is duplicated or nonpublic")
        require(item.get("cohort") == "calibration", "a frozen case escaped the calibration cohort")
        require(item.get("api") in OPERATIONS, "a frozen public operation was substituted")
        require(isinstance(item.get("category"), str), "a frozen public category is missing")
        frozen[case] = item
    categories = manifest.get("categories")
    require(isinstance(categories, dict) and len(categories) == CATEGORIES, "the manifest omitted a frozen workload category")
    require(Counter(item["api"] for item in selected) == Counter(OPERATIONS), "the exact frozen operation weights changed")
    require(Counter(item["category"] for item in selected) == categories, "the frozen category counts were substituted")

    rows = summary.get("case_results")
    require(
        isinstance(rows, list) and len(rows) == CASES * len(CANDIDATES),
        "the summary omitted one of its 24,576 measured candidate cases",
    )
    rows_by_candidate: dict[str, list[dict[str, Any]]] = {candidate: [] for candidate in CANDIDATES}
    losses_by_candidate: dict[str, list[dict[str, Any]]] = {candidate: [] for candidate in CANDIDATES}
    identities: set[tuple[str, str]] = set()
    for row in rows:
        require(isinstance(row, dict), "an independently replayed case is invalid")
        candidate = row.get("candidate")
        case = row.get("case")
        require(candidate in CANDIDATES and isinstance(case, str), "a candidate or public case was omitted")
        identity = (candidate, case)
        require(identity not in identities, "an independently replayed candidate case was duplicated")
        identities.add(identity)
        reference = frozen.get(case)
        require(reference is not None, "an unfrozen public case entered the measured summary")
        for field in ("api", "category", "cohort"):
            require(row.get(field) == reference.get(field), f"a measured public case changed its frozen {field}")
        require(row.get("weight") == 1, "a public candidate case is not equally weighted")
        speedup = finite(row.get("speedup"), "case speedup")
        lower = finite(row.get("ci95_low"), "case confidence lower bound")
        upper = finite(row.get("ci95_high"), "case confidence upper bound")
        require(lower <= upper, "a measured public confidence interval is inverted")
        finite(row.get("baseline_ns"), "Python baseline observation")
        finite(row.get("candidate_ns"), "candidate observation")
        finite(row.get("peak_traced_ratio"), "Python-visible traced allocation ratio", zero=True)
        require(type(row.get("statistically_faster")) is bool, "a public case concealed its significance")
        require(
            type(row.get("regression_gt_20pct")) is bool
            and row["regression_gt_20pct"] == (speedup < 5 / 6),
            "a public slowdown exceeding 20% was omitted or invented",
        )
        rows_by_candidate[candidate].append(row)
        if row["regression_gt_20pct"]:
            losses_by_candidate[candidate].append(row)
    for candidate, candidate_rows in rows_by_candidate.items():
        require(len(candidate_rows) == CASES, f"{LABELS[candidate]} omitted an 8,192-case denominator")
        require({row["case"] for row in candidate_rows} == set(frozen), "a candidate did not cover every frozen public case")
        require(Counter(row["api"] for row in candidate_rows) == Counter(OPERATIONS), "a candidate omitted a frozen operation")
        require(Counter(row["category"] for row in candidate_rows) == categories, "a candidate omitted a frozen workload category")

    loss_rows = summary.get("regressions")
    require(isinstance(loss_rows, list) and len(loss_rows) == REGRESSIONS, "one of the 5,173 genuine public losses is missing")
    expected_losses = [row for row in rows if row["regression_gt_20pct"]]
    require(loss_rows == expected_losses, "an individual measured public loss was removed, changed, or reordered")
    replayed_losses = integrity.get("regressions")
    require(isinstance(replayed_losses, list) and len(replayed_losses) == REGRESSIONS, "the independent replay omitted a measured public loss")
    key = lambda row: (row.get("candidate", ""), row.get("case", ""))
    require(sorted(replayed_losses, key=key) == sorted(loss_rows, key=key), "the independent replay altered an individual public loss")

    rankings = summary.get("rankings")
    require(isinstance(rankings, list) and len(rankings) == len(CANDIDATES), "a measured public candidate ranking is missing")
    require(integrity.get("rankings") == rankings, "the independently replayed public rankings changed")
    seen: set[str] = set()
    for ranking in rankings:
        require(isinstance(ranking, dict), "a measured public ranking is invalid")
        candidate = ranking.get("candidate")
        require(candidate in CANDIDATES and candidate not in seen, "a measured candidate ranking is missing or duplicated")
        seen.add(candidate)
        candidate_rows = rows_by_candidate[candidate]
        require(ranking.get("cases") == CASES and ranking.get("weight") == CASES, "a public ranking changed its 8,192-case weight")
        require(ranking.get("cohort") == "calibration", "a public ranking claims a final cohort")
        mean = math.exp(math.fsum(math.log(finite(row["speedup"], "case speedup")) for row in candidate_rows) / CASES)
        same_float(finite(ranking.get("geomean_speedup"), "overall speedup"), mean, "geometric-mean ranking")
        lower = finite(ranking.get("ci95_low"), "overall confidence lower bound")
        upper = finite(ranking.get("ci95_high"), "overall confidence upper bound")
        require(lower <= ranking["geomean_speedup"] <= upper, "a candidate's overall confidence interval is invalid")
        require(
            ranking.get("statistically_faster_cases") == sum(row["statistically_faster"] for row in candidate_rows),
            "a public candidate concealed a clearly faster case",
        )
        require(
            ranking.get("regressions_gt_20pct") == len(losses_by_candidate[candidate]),
            "a public candidate concealed a slowdown exceeding 20%",
        )
    require(
        rankings == sorted(rankings, key=lambda row: row["geomean_speedup"], reverse=True),
        "the displayed public rankings are not the measured order",
    )
    require(sum(len(values) for values in losses_by_candidate.values()) == REGRESSIONS, "a public loss was hidden")
    return PublicResults(
        manifest=manifest,
        summary=summary,
        integrity=integrity,
        rankings=tuple(rankings),
        rows_by_candidate={candidate: tuple(values) for candidate, values in rows_by_candidate.items()},
        losses_by_candidate={candidate: tuple(values) for candidate, values in losses_by_candidate.items()},
        operations=dict(OPERATIONS),
    )


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def text(x: float, y: float, value: object, cls: str = "body", **attributes: object) -> str:
    extra = "".join(f' {key.replace("_", "-")}="{esc(value)}"' for key, value in attributes.items())
    return f'<text x="{x:.2f}" y="{y:.2f}" class="{cls}"{extra}>{esc(value)}</text>'


def rect(x: float, y: float, width: float, height: float, *, fill: str, radius: float = 0, **attributes: object) -> str:
    extra = "".join(f' {key.replace("_", "-")}="{esc(value)}"' for key, value in attributes.items())
    return (
        f'<rect x="{x:.2f}" y="{y:.2f}" width="{width:.2f}" height="{height:.2f}" '
        f'rx="{radius:.2f}" fill="{esc(fill)}"{extra}/>'
    )


def line(x1: float, y1: float, x2: float, y2: float, *, stroke: str, width: float = 1, **attributes: object) -> str:
    extra = "".join(f' {key.replace("_", "-")}="{esc(value)}"' for key, value in attributes.items())
    return (
        f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
        f'stroke="{esc(stroke)}" stroke-width="{width:.2f}"{extra}/>'
    )


STYLE = (
    "text{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"
    "'Segoe UI',sans-serif;fill:#17263b}"
    ".eyebrow{font-size:12px;font-weight:720;letter-spacing:1.7px;fill:#58718c}"
    ".title{font-size:32px;font-weight:760;letter-spacing:-.8px}"
    ".subtitle{font-size:14px;fill:#607087}"
    ".heading{font-size:17px;font-weight:720}"
    ".body{font-size:13px;fill:#46586d}"
    ".label{font-size:15px;font-weight:690}"
    ".value{font-size:15px;font-weight:730}"
    ".big{font-size:32px;font-weight:760;letter-spacing:-.6px}"
    ".small{font-size:11.5px;fill:#65768a}"
    ".tick{font-size:11px;fill:#718299}"
    ".footer{font-size:12px;font-weight:620;fill:#58718c}"
)


def begin_svg(suffix: str, *, title: str, description: str, height: int, subtitle: str) -> list[str]:
    title_id = f"clear-v5-{suffix}-title"
    desc_id = f"clear-v5-{suffix}-description"
    return [
        f'<svg xmlns="{SVG_NAMESPACE}" width="1120" height="{height}" '
        f'viewBox="0 0 1120 {height}" role="img" '
        f'aria-labelledby="{title_id} {desc_id}">',
        f'<title id="{title_id}">{esc(title)}</title>',
        f'<desc id="{desc_id}">{esc(description + " " + FOOTER)}</desc>',
        f"<style>{STYLE}</style>",
        rect(0, 0, 1120, height, fill="#f5f7fb"),
        rect(24, 20, 1072, height - 40, fill="#ffffff", radius=20),
        text(56, 57, "INDEPENDENTLY VERIFIED · PUBLIC CALIBRATION", "eyebrow"),
        text(54, 101, title, "title"),
        text(56, 126, subtitle, "subtitle"),
    ]


def finish_svg(parts: list[str], *, height: int) -> str:
    parts.extend(
        (
            line(56, height - 66, 1064, height - 66, stroke="#e6ebf2"),
            text(56, height - 39, FOOTER, "footer"),
            text(1064, height - 39, "8,192 public cases · 13 paired trials", "small", text_anchor="end"),
            "</svg>\n",
        )
    )
    return "\n".join(parts)


def pill(parts: list[str], x: float, y: float, width: float, label: str, value: str) -> None:
    parts.append(rect(x, y, width, 62, fill="#f5f8fc", radius=12))
    parts.append(text(x + 14, y + 23, label, "small"))
    parts.append(text(x + 14, y + 47, value, "value"))


def speed_bounds(values: list[float]) -> tuple[float, float]:
    return min(0.72, min(values) * 0.94), max(1.64, max(values) * 1.06)


def speed_x(value: float, *, left: float, right: float, bounds: tuple[float, float]) -> float:
    low, high = bounds
    return left + (math.log(value) - math.log(low)) / (math.log(high) - math.log(low)) * (right - left)


def speed_axis(
    parts: list[str],
    *,
    left: float,
    right: float,
    top: float,
    bottom: float,
    bounds: tuple[float, float],
) -> None:
    for value in (0.75, 1.0, 1.25, 1.5, 2.0, 3.0, 5.0, 10.0):
        if bounds[0] <= value <= bounds[1]:
            x = speed_x(value, left=left, right=right, bounds=bounds)
            is_baseline = value == 1.0
            is_target = value == 1.5
            parts.append(
                line(
                    x,
                    top,
                    x,
                    bottom,
                    stroke="#7d8fa3" if is_baseline else "#8a72bb" if is_target else "#e9edf3",
                    width=1.6 if is_baseline or is_target else 1,
                    stroke_dasharray="5 5" if is_target else "0",
                )
            )
            parts.append(text(x, bottom + 17, f"{value:g}×", "tick", text_anchor="middle"))
    baseline = speed_x(1.0, left=left, right=right, bounds=bounds)
    target = speed_x(1.5, left=left, right=right, bounds=bounds)
    parts.append(text(baseline, top - 10, "Python · 1×", "small", text_anchor="middle"))
    parts.append(text(target, top - 10, "1.5× target", "small", text_anchor="middle"))


def confidence_mark(
    parts: list[str],
    ranking: dict[str, Any],
    y: float,
    *,
    left: float,
    right: float,
    bounds: tuple[float, float],
) -> None:
    candidate = ranking["candidate"]
    color = COLORS[candidate]
    low = speed_x(ranking["ci95_low"], left=left, right=right, bounds=bounds)
    high = speed_x(ranking["ci95_high"], left=left, right=right, bounds=bounds)
    center = speed_x(ranking["geomean_speedup"], left=left, right=right, bounds=bounds)
    parts.extend(
        (
            line(low, y, high, y, stroke=color, width=5, stroke_linecap="round"),
            line(low, y - 8, low, y + 8, stroke=color, width=2),
            line(high, y - 8, high, y + 8, stroke=color, width=2),
            f'<circle cx="{center:.2f}" cy="{y:.2f}" r="7" fill="{color}" stroke="#ffffff" stroke-width="2"/>',
        )
    )


def build_overall(results: PublicResults) -> str:
    height = 650
    parts = begin_svg(
        "overall",
        title="How fast were the three regex engines?",
        description="Geometric-mean public speed versus Python with genuine 95% confidence intervals for Zig, C, and Rust.",
        height=height,
        subtitle="Higher is faster. Confidence bars show independently verified uncertainty, not final-test results.",
    )
    pill(parts, 56, 151, 174, "Shared public cases", "8,192 per engine")
    pill(parts, 242, 151, 174, "Workload coverage", "12 APIs · 260 groups")
    pill(parts, 428, 151, 190, "Uncertainty", "95% bootstrap interval")
    values = [bound for row in results.rankings for bound in (row["ci95_low"], row["ci95_high"])]
    bounds = speed_bounds(values)
    left, right, top, bottom = 255.0, 824.0, 279.0, 486.0
    speed_axis(parts, left=left, right=right, top=top, bottom=bottom, bounds=bounds)
    for index, ranking in enumerate(results.rankings):
        y = 319 + index * 68
        candidate = ranking["candidate"]
        parts.append(text(66, y + 5, LABELS[candidate], "label"))
        confidence_mark(parts, ranking, y, left=left, right=right, bounds=bounds)
        parts.append(text(851, y - 3, f'{ranking["geomean_speedup"]:.3f}×', "value"))
        parts.append(
            text(851, y + 17, f'{ranking["ci95_low"]:.3f}–{ranking["ci95_high"]:.3f}× · 95% CI', "small")
        )
    parts.append(text(58, 553, "No engine reaches the 1.5× public target.", "heading"))
    parts.append(text(58, 574, "These are measured public-development comparisons, not final qualification.", "body"))
    return finish_svg(parts, height=height)


def build_outcomes(results: PublicResults) -> str:
    height = 650
    parts = begin_svg(
        "outcomes",
        title="What happened across all 8,192 cases?",
        description="Every verified candidate case is classified as clearly faster, more than 20% slower, or remaining uncertain.",
        height=height,
        subtitle="Each bar includes every public case. A faster result must be supported by its case-level confidence interval.",
    )
    green, neutral, amber = "#238b75", "#e4eaf2", "#d59a60"
    for x, color, label in ((64, green, "Clearly faster"), (225, neutral, "Remaining / uncertain"), (445, amber, "More than 20% slower")):
        parts.append(rect(x, 167, 12, 12, fill=color, radius=3))
        parts.append(text(x + 20, 178, label, "body"))
    left, width = 222.0, 666.0
    for index, ranking in enumerate(results.rankings):
        y = 237 + index * 101
        wins = ranking["statistically_faster_cases"]
        losses = ranking["regressions_gt_20pct"]
        remaining = CASES - wins - losses
        require(remaining >= 0, "verified public outcomes overlap or omit a case")
        parts.append(text(65, y + 21, LABELS[ranking["candidate"]], "label"))
        offset = left
        for count, color in ((wins, green), (remaining, neutral), (losses, amber)):
            segment = width * count / CASES
            if segment:
                parts.append(rect(offset, y, segment, 29, fill=color, radius=3))
            offset += segment
        parts.append(text(901, y + 19, f"{CASES:,}/{CASES:,}", "value"))
        parts.append(
            text(
                left,
                y + 51,
                f"{wins:,} clearly faster · {remaining:,} remaining · {losses:,} over 20% slower",
                "small",
            )
        )
    target_x = left + width * 0.60
    parts.append(line(target_x, 222, target_x, 473, stroke="#8a72bb", width=1.5, stroke_dasharray="5 5"))
    parts.append(text(target_x + 7, 222, "60% clearly-faster target", "small"))
    parts.append(text(59, 531, "The 60% target requires 4,916 clearly faster cases; no engine reaches it.", "body"))
    return finish_svg(parts, height=height)


def operation_means(results: PublicResults) -> dict[tuple[str, str], float]:
    values: dict[tuple[str, str], float] = {}
    for candidate, rows in results.rows_by_candidate.items():
        grouped: dict[str, list[float]] = {operation: [] for operation in OPERATIONS}
        for row in rows:
            grouped[row["api"]].append(row["speedup"])
        for operation, speeds in grouped.items():
            require(len(speeds) == OPERATIONS[operation], "a displayed operation omitted a genuine public case")
            values[(candidate, operation)] = math.exp(math.fsum(math.log(speed) for speed in speeds) / len(speeds))
    require(len(values) == len(CANDIDATES) * len(OPERATIONS), "a displayed candidate-operation result is missing")
    return values


def build_api(results: PublicResults) -> str:
    height = 1_110
    parts = begin_svg(
        "api",
        title="Which Python operations were fast?",
        description="All 12 frozen Python operations are shown separately for all three engines using every verified case.",
        height=height,
        subtitle="Dots are per-operation geometric means. Per-operation confidence intervals were not measured or invented.",
    )
    means = operation_means(results)
    bounds = speed_bounds(list(means.values()))
    left, right, top, bottom = 281.0, 830.0, 174.0, 1_008.0
    speed_axis(parts, left=left, right=right, top=top, bottom=bottom, bounds=bounds)
    candidate_order = tuple(row["candidate"] for row in results.rankings)
    for index, (operation, count) in enumerate(OPERATIONS.items()):
        group = 195 + index * 67
        if index:
            parts.append(line(57, group - 12, 1_059, group - 12, stroke="#edf0f5"))
        parts.append(text(63, group + 11, operation, "label"))
        parts.append(text(63, group + 29, f"{count:,} cases per engine", "small"))
        for candidate_index, candidate in enumerate(candidate_order):
            y = group + candidate_index * 17
            value = means[(candidate, operation)]
            x = speed_x(value, left=left, right=right, bounds=bounds)
            parts.append(
                f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4.5" fill="{COLORS[candidate]}">'
                f"<title>{esc(LABELS[candidate])}: {esc(operation)}, {value:.6f}×, {count:,} public cases</title></circle>"
            )
            parts.append(text(849, y + 4, f"{LABELS[candidate]} · {value:.2f}×", "small"))
    return finish_svg(parts, height=height)


def build_regressions(results: PublicResults) -> str:
    columns = 112
    step = 6.65
    order = tuple(row["candidate"] for row in results.rankings)
    band_heights = {
        candidate: 47 + math.ceil(len(results.losses_by_candidate[candidate]) / columns) * step
        for candidate in order
    }
    height = max(610, math.ceil(277 + sum(band_heights.values()) + 89))
    parts = begin_svg(
        "regressions",
        title="Every measured slowdown, shown once",
        description="Each of the 5,173 independently verified public slowdowns is one individually titled, visible dot.",
        height=height,
        subtitle="One dot is one real candidate–case more than 20% slower than Python. Hover a dot for its exact case.",
    )
    pill(parts, 57, 150, 205, "Individually visible losses", "5,173 / 24,576")
    pill(parts, 275, 150, 205, "Threshold", "more than 20% slower")
    pill(parts, 493, 150, 205, "Missing or merged cases", "0")
    y = 241.0
    shown = 0
    for candidate in order:
        losses = sorted(
            results.losses_by_candidate[candidate],
            key=lambda row: (row["api"], row["case"]),
        )
        parts.append(text(62, y + 8, LABELS[candidate], "label"))
        parts.append(text(62, y + 27, f"{len(losses):,}/{CASES:,} cases", "small"))
        base_y = y + 4
        for index, row in enumerate(losses):
            x = 296 + (index % columns) * step
            dot_y = base_y + (index // columns) * step
            title = (
                f'{LABELS[candidate]} · {row["api"]} · {row["case"]} · '
                f'{row["speedup"]:.6f}× Python speed'
            )
            parts.append(
                f'<circle class="loss-mark" cx="{x:.2f}" cy="{dot_y:.2f}" '
                f'r="2.45" fill="{COLORS[candidate]}"><title>{esc(title)}</title></circle>'
            )
            shown += 1
        y += band_heights[candidate]
        if candidate != order[-1]:
            parts.append(line(58, y - 16, 1_056, y - 16, stroke="#edf0f5"))
    require(shown == REGRESSIONS, "a visibly displayed public slowdown was omitted")
    parts.append(text(59, height - 92, "Dots are genuine measured cases, not a sample or a generated workload.", "body"))
    return finish_svg(parts, height=height)


def quantile(values: tuple[float, ...], fraction: float) -> float:
    require(bool(values) and 0 <= fraction <= 1, "a traced-allocation percentile is invalid")
    index = (len(values) - 1) * fraction
    lower = math.floor(index)
    upper = math.ceil(index)
    return values[lower] + (values[upper] - values[lower]) * (index - lower)


def build_memory(results: PublicResults) -> str:
    height = 680
    parts = begin_svg(
        "memory",
        title="What memory was actually measured?",
        description="Python-visible temporary allocation ratios only; native allocations, process attribution, and final memory are not measured.",
        height=height,
        subtitle="Points are median Python-traced temporary-allocation ratios; bars span the 10th to 90th observed percentiles.",
    )
    samples: dict[str, tuple[float, ...]] = {
        candidate: tuple(sorted(finite(row["peak_traced_ratio"], "traced allocation", zero=True) for row in rows))
        for candidate, rows in results.rows_by_candidate.items()
    }
    summaries = {
        candidate: (quantile(values, 0.1), quantile(values, 0.5), quantile(values, 0.9))
        for candidate, values in samples.items()
    }
    left, right = 271.0, 800.0
    high = max(1.15, max(values[2] for values in summaries.values()) * 1.10)
    axis_x = lambda value: left + value / high * (right - left)
    for tick in (0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0):
        if tick <= high:
            x = axis_x(tick)
            parts.append(line(x, 203, x, 439, stroke="#8d9caf" if tick == 1.0 else "#e9edf3", width=1.5 if tick == 1.0 else 1))
            parts.append(text(x, 457, f"{tick:g}×", "tick", text_anchor="middle"))
    if high >= 1.0:
        parts.append(text(axis_x(1.0), 194, "Python traced allocation · 1×", "small", text_anchor="middle"))
    for index, ranking in enumerate(results.rankings):
        candidate = ranking["candidate"]
        y = 245 + index * 69
        low, median, upper = summaries[candidate]
        color = COLORS[candidate]
        parts.append(text(66, y + 4, LABELS[candidate], "label"))
        parts.append(line(axis_x(low), y, axis_x(upper), y, stroke=color, width=5, stroke_linecap="round"))
        parts.append(f'<circle cx="{axis_x(median):.2f}" cy="{y:.2f}" r="6.5" fill="{color}" stroke="#ffffff" stroke-width="2"/>')
        parts.append(text(823, y + 3, f"{median:.2f}× median", "value"))
        parts.append(text(823, y + 20, f"{CASES:,} Python-traced cases", "small"))
    parts.append(rect(57, 481, 1_003, 82, fill="#f3f6fb", radius=12))
    parts.append(text(74, 510, "Native-engine allocations and final memory: NOT MEASURED", "heading"))
    parts.append(text(74, 535, "Worker RSS and high-water marks are process-level only; they cannot identify per-case native allocations.", "body"))
    return finish_svg(parts, height=height)


def build_rankings(results: PublicResults) -> str:
    height = 670
    parts = begin_svg(
        "rankings",
        title="The public ranking, without overstating it",
        description="The independently verified public ranking lists Zig, C, and Rust with every overall confidence interval and case denominator.",
        height=height,
        subtitle="This is a ranking of one 8,192-case public development test. It is not a final qualification.",
    )
    values = [value for row in results.rankings for value in (row["ci95_low"], row["ci95_high"])]
    bounds = speed_bounds(values)
    left, right, top, bottom = 314.0, 788.0, 213.0, 456.0
    speed_axis(parts, left=left, right=right, top=top, bottom=bottom, bounds=bounds)
    for index, ranking in enumerate(results.rankings):
        y = 254 + index * 78
        candidate = ranking["candidate"]
        parts.append(text(64, y + 5, f"{index + 1:02d}", "small"))
        parts.append(text(105, y + 4, LABELS[candidate], "label"))
        parts.append(text(105, y + 22, f'{ranking["statistically_faster_cases"]:,}/{CASES:,} clearly faster', "small"))
        confidence_mark(parts, ranking, y, left=left, right=right, bounds=bounds)
        parts.append(text(813, y - 2, f'{ranking["geomean_speedup"]:.3f}×', "value"))
        parts.append(text(813, y + 17, f'{ranking["ci95_low"]:.3f}–{ranking["ci95_high"]:.3f}×', "small"))
        parts.append(text(955, y + 4, f'{ranking["regressions_gt_20pct"]:,} losses', "small"))
    parts.append(rect(58, 501, 1_001, 66, fill="#f4f6fb", radius=12))
    parts.append(text(75, 528, "Neither public target was met.", "heading"))
    parts.append(text(75, 550, "No 1.5× geometric mean; no 4,916/8,192 clearly-faster cases.", "body"))
    return finish_svg(parts, height=height)


BUILDERS: dict[str, Callable[[PublicResults], str]] = {
    "overall": build_overall,
    "outcomes": build_outcomes,
    "api": build_api,
    "regressions": build_regressions,
    "memory": build_memory,
    "rankings": build_rankings,
}


def validate_svg(svg: str, *, suffix: str) -> None:
    require(isinstance(svg, str) and svg.endswith("</svg>\n"), "a clear public graph is not a complete SVG")
    root = ElementTree.fromstring(svg)
    require(root.tag == f"{{{SVG_NAMESPACE}}}svg", "a clear public graph is not namespaced SVG")
    require(root.get("role") == "img", "a clear public graph has no accessible image role")
    require(root.get("aria-labelledby") == f"clear-v5-{suffix}-title clear-v5-{suffix}-description", "a clear public graph omitted accessible title or description")
    namespace = f"{{{SVG_NAMESPACE}}}"
    title = root.find(f"{namespace}title")
    description = root.find(f"{namespace}desc")
    require(title is not None and bool(title.text), "a clear public graph omitted its title")
    require(description is not None and FOOTER in (description.text or ""), "a clear public graph misrepresented final holdout status")
    visible_text = " ".join(node.text or "" for node in root.iter(f"{namespace}text"))
    require(FOOTER in visible_text, "a clear public graph concealed its public-only footer")
    require(MANIFEST_SHA256 not in svg and RUNNER_SHA256 not in svg, "a readable public graph contains fingerprint clutter")
    if suffix in ("overall", "api", "rankings"):
        require("Python · 1×" in visible_text and "1.5× target" in visible_text, "a public speed graph omitted its baseline or target")
    if suffix == "regressions":
        marks = [node for node in root.iter(f"{namespace}circle") if node.get("class") == "loss-mark"]
        require(len(marks) == REGRESSIONS, "one of the 5,173 individual public loss dots is missing")
        require(
            all((mark.find(f"{namespace}title") is not None) for mark in marks),
            "an individual public loss has no accessible case description",
        )
    if suffix == "memory":
        require(
            "Native-engine allocations and final memory: NOT MEASURED" in visible_text,
            "a public graph overclaims native or final memory",
        )


def build_charts(results: PublicResults) -> dict[str, str]:
    require_candidate_free()
    require(tuple(BUILDERS) == SUFFIXES, "a clear public presentation graph was removed")
    charts = {suffix: BUILDERS[suffix](results) for suffix in SUFFIXES}
    for suffix, svg in charts.items():
        validate_svg(svg, suffix=suffix)
    require_candidate_free()
    return charts


def plan_clear_outputs(
    charts: dict[str, str],
    states: dict[str, tuple[str, bytes | None]],
) -> dict[str, bool]:
    """Plan all six outputs before permitting any exclusive file creation."""

    require(
        tuple(charts) == SUFFIXES and tuple(states) == SUFFIXES,
        "the reproducible presentation omitted or substituted an exact output",
    )
    create: dict[str, bool] = {}
    for suffix in SUFFIXES:
        state = states[suffix]
        require(
            isinstance(state, tuple) and len(state) == 2,
            "an exact public presentation destination has an invalid state",
        )
        kind, existing = state
        if kind == "missing":
            require(existing is None, "a missing public graph contains unexpected existing bytes")
            create[suffix] = True
            continue
        require(
            kind == "regular",
            "a public graph destination is a symlink or is not a regular file",
        )
        require(
            isinstance(existing, bytes)
            and existing == charts[suffix].encode("utf-8"),
            "an existing public graph does not reproduce the exact verified SVG",
        )
        create[suffix] = False
    return create


def synthetic_sha(label: str) -> str:
    return hashlib.sha256(f"synthetic-public-presentation-only:{label}".encode("utf-8")).hexdigest()


def synthetic_documents() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Generate all 8,192 synthetic public cases without opening any file."""

    selected: list[dict[str, Any]] = []
    for operation, count in OPERATIONS.items():
        for index in range(count):
            global_index = len(selected)
            selected.append(
                {
                    "case": f"cal.synthetic.{operation}.{index:05d}",
                    "api": operation,
                    "category": f"synthetic-public-category-{global_index % CATEGORIES:03d}",
                    "cohort": "calibration",
                }
            )
    categories = dict(Counter(item["category"] for item in selected))
    targets = {
        "candidates.rust_candidate": (2_516, 2_866, 1.42),
        "candidates.vm_candidate": (1_282, 4_709, 1.66),
        "candidates.zig_candidate": (1_375, 4_689, 1.82),
    }
    rows: list[dict[str, Any]] = []
    rankings: list[dict[str, Any]] = []
    for candidate_index, candidate in enumerate(CANDIDATES):
        loss_count, wins, winning_speed = targets[candidate]
        candidate_rows: list[dict[str, Any]] = []
        for index, item in enumerate(selected):
            is_loss = index < loss_count
            is_win = loss_count <= index < loss_count + wins
            speedup = 0.72 if is_loss else winning_speed if is_win else 1.01
            lower = speedup * (0.985 if is_win else 0.91)
            upper = speedup * (1.015 if is_win else 1.09)
            row = {
                **item,
                "candidate": candidate,
                "weight": 1,
                "baseline_ns": 100.0,
                "candidate_ns": 100.0 / speedup,
                "speedup": speedup,
                "ci95_low": lower,
                "ci95_high": upper,
                "peak_traced_ratio": (index % 31) / 20 + candidate_index * 0.04,
                "statistically_faster": is_win,
                "regression_gt_20pct": is_loss,
            }
            candidate_rows.append(row)
        rows.extend(candidate_rows)
        average = math.exp(math.fsum(math.log(row["speedup"]) for row in candidate_rows) / CASES)
        rankings.append(
            {
                "candidate": candidate,
                "cases": CASES,
                "weight": CASES,
                "cohort": "calibration",
                "geomean_speedup": average,
                "ci95_low": average * 0.985,
                "ci95_high": average * 1.015,
                "statistically_faster_cases": wins,
                "regressions_gt_20pct": loss_count,
            }
        )
    rankings.sort(key=lambda row: row["geomean_speedup"], reverse=True)
    losses = [row for row in rows if row["regression_gt_20pct"]]
    native = {f"synthetic-native-{index}": synthetic_sha(f"native-{index}") for index in range(5)}
    sources = {f"synthetic-source-{index}": synthetic_sha(f"source-{index}") for index in range(12)}
    binaries = {f"synthetic-binary-{index}": synthetic_sha(f"binary-{index}") for index in range(11)}
    artifacts: list[dict[str, str]] = []
    for family in ("rust", "vm", "zig"):
        paths = {
            "edge": f"candidates/evidence/rust-v7-edge-oracle-{family}-post-final-stage-05-universal-parity.json.gz",
            "deep-public-contract": (
                "candidates/audits/RUST-V8-DEEP-CONTRACT-"
                f"{'C' if family == 'vm' else family.upper()}-POST-FINAL-STAGE-05-UNIVERSAL-PARITY.json.gz"
            ),
            "observability": f"candidates/evidence/rust-v8-observability-{family}-qualified-post-final-stage-05-universal-parity.json.gz",
            "complete-correctness-campaign": f"candidates/evidence/rust-v8-{family}-post-final-stage-05-universal-parity-sealed-campaign.json",
        }
        for role, path in paths.items():
            artifacts.append({"role": f"{family}-{role}", "path": path, "sha256": synthetic_sha(f"artifact-{family}-{role}")})
    proof: dict[str, Any] = {
        "python_re_universal_oracle_source_path": "tools/synthetic-public-universal-oracle.py",
        "python_re_universal_oracle_source_sha256": synthetic_sha("universal-source"),
        "python_re_universal_oracle_report_path": "synthetic-only-public-oracle-report.json",
        "python_re_universal_oracle_report_sha256": synthetic_sha("universal-report"),
        "python_re_universal_oracle_schema": "rebar-python-re-universal-public-oracle-v1",
        "python_re_universal_oracle_status": "PASS",
        "python_re_universal_oracle_selected": "all",
        "python_re_universal_oracle_candidates": ["rust", "vm", "zig"],
        "python_re_universal_oracle_cases": CASES,
        "python_re_universal_oracle_comparisons_per_case": 48,
        "python_re_universal_oracle_comparisons_per_candidate": 393_216,
        "python_re_universal_oracle_total_comparisons": 1_179_648,
        "python_re_universal_oracle_mismatches": 0,
        "python_re_universal_oracle_seed": 2_026_072_417,
        "python_re_universal_oracle_seed_domain": "rebar/python-re/universal-public/v1",
        "python_re_universal_oracle_case_sha256": synthetic_sha("universal-cases"),
        "python_re_universal_oracle_grammar_family_count": 16,
        "python_re_universal_oracle_input_stratum_count": 16,
        "python_re_universal_oracle_examples_per_stratum": 32,
        "python_re_universal_oracle_original_audit_sha256": synthetic_sha("original-audit"),
        "python_re_universal_oracle_postfinal_no_delegation_audit_sha256": synthetic_sha("isolation-audit"),
        "python_re_universal_oracle_frozen_source_path": "tools/synthetic-public-immutable-oracle.py",
        "python_re_universal_oracle_frozen_source_sha256": synthetic_sha("frozen-universal-source"),
    }
    common = {
        "protocol_version": VERSION,
        "cohort": "calibration",
        "holdout_accessed": False,
        "held_out_cases_generated": 0,
        "held_out_records_deserialized": 0,
        "runner_sha256": RUNNER_SHA256,
        "from_scratch_audit_sha256": synthetic_sha("original-audit"),
        "from_scratch_audit_source_sha256": synthetic_sha("original-audit-source"),
        "postfinal_no_delegation_audit_sha256": synthetic_sha("isolation-audit"),
        "postfinal_no_delegation_control_count": 32,
        "stage05_correctness_artifacts": artifacts,
        "failed": 0,
        **proof,
    }
    manifest = {
        **common,
        "schema": "rebar-rust-balanced-calibration-plan-v7",
        "postfinal_schema": "rebar-postfinal-public-practice-plan-v5",
        "exclusive_slot": VERSION,
        "modules": list(MODULES),
        "cases": CASES,
        "all_bounded_workload_categories": CATEGORIES,
        "public_operations": dict(OPERATIONS),
        "categories": categories,
        "selected_cases": selected,
        "frozen_trials": TRIALS,
        "frozen_warmups": WARMUPS,
        "frozen_bootstrap_samples": BOOTSTRAPS,
        "native_elf_fingerprints": native,
        "qualified_source_fingerprints": sources,
    }
    summary = {
        **common,
        "schema": "rebar-rust-balanced-calibration-pilot-v7",
        "postfinal_schema": "rebar-postfinal-public-practice-report-v5",
        "exclusive_slot": VERSION,
        "modules": list(MODULES),
        "cases": CASES,
        "all_bounded_workload_categories": CATEGORIES,
        "public_operations": dict(OPERATIONS),
        "trials": TRIALS,
        "warmups": WARMUPS,
        "bootstrap_samples": BOOTSTRAPS,
        "manifest_path": str(MANIFEST),
        "manifest_sha256": MANIFEST_SHA256,
        "raw_path": str(RAW),
        "raw_sha256": synthetic_sha("uncompressed-raw"),
        "compressed_raw_sha256": synthetic_sha("compressed-raw"),
        "paired_raw_rows": RAW_ROWS,
        "correctness_checks": CORRECTNESS_CHECKS,
        "persistent_isolated_worker_count": len(MODULES),
        "per_case_runtime_guard_checks": RUNTIME_GUARDS,
        "controller_candidate_imported": False,
        "candidate_binary_sha256_before": binaries,
        "candidate_binary_sha256_after": binaries,
        "case_results": rows,
        "regressions": losses,
        "rankings": rankings,
    }
    integrity = {
        **common,
        "schema": "rebar-postfinal-public-practice-integrity-v5",
        "result": "PASS",
        "module_order": list(MODULES),
        "cases_per_candidate": CASES,
        "candidate_case_count": CASES * len(CANDIDATES),
        "trials_per_module_case": TRIALS,
        "bootstrap_draws": BOOTSTRAPS,
        "raw_rows": RAW_ROWS,
        "correctness_checks": CORRECTNESS_CHECKS,
        "confidence_intervals_recomputed": CONFIDENCE_INTERVALS,
        "strict_regressions": REGRESSIONS,
        "manifest_sha256": MANIFEST_SHA256,
        "summary_sha256": SUMMARY_SHA256,
        "raw_sha256": summary["raw_sha256"],
        "compressed_raw_sha256": summary["compressed_raw_sha256"],
        "persistent_isolated_worker_count": len(MODULES),
        "per_case_runtime_guard_checks": RUNTIME_GUARDS,
        "controller_candidate_imported": False,
        "candidate_imported": False,
        "timing_performed": False,
        "memory_limitation": MEMORY_LIMITATION,
        "from_scratch_control_count": 76,
        "verified_independent_engine_count": len(CANDIDATES),
        "verified_native_library_count": 5,
        "native_elf_fingerprints": native,
        "qualified_source_fingerprints": sources,
        "candidate_binary_sha256_before": binaries,
        "candidate_binary_sha256_after": binaries,
        "rankings": rankings,
        "regressions": losses,
        "self_test": {"result": "PASS", "synthetic_only": True},
    }
    return manifest, summary, integrity


def self_test() -> dict[str, Any]:
    """Validate synthetic evidence and six SVGs entirely in memory."""

    require_candidate_free()
    manifest, summary, integrity = synthetic_documents()
    pins = {
        "manifest_sha256": MANIFEST_SHA256,
        "summary_sha256": SUMMARY_SHA256,
        "integrity_sha256": INTEGRITY_SHA256,
        "runner_sha256": RUNNER_SHA256,
    }
    results = validate_documents(manifest, summary, integrity, **pins)
    charts = build_charts(results)
    require(charts == build_charts(results), "the clear public SVG presentation is not deterministic")

    missing_outputs: dict[str, tuple[str, bytes | None]] = {
        suffix: ("missing", None) for suffix in SUFFIXES
    }
    existing_outputs: dict[str, tuple[str, bytes | None]] = {
        suffix: ("regular", charts[suffix].encode("utf-8"))
        for suffix in SUFFIXES
    }
    require(
        all(plan_clear_outputs(charts, missing_outputs).values()),
        "a genuinely missing synthetic public graph is not exclusively creatable",
    )
    require(
        not any(plan_clear_outputs(charts, existing_outputs).values()),
        "byte-identical committed public graphs are not reproducible",
    )
    mixed_outputs = {
        **existing_outputs,
        "overall": ("missing", None),
    }
    require(
        plan_clear_outputs(charts, mixed_outputs)
        == {suffix: suffix == "overall" for suffix in SUFFIXES},
        "the public presenter does not exclusively recreate its one missing graph",
    )

    poison_controls: tuple[tuple[str, Callable[[], None]], ...] = (
        ("substituted manifest fingerprint", lambda: validate_documents(manifest, summary, integrity, **{**pins, "manifest_sha256": "0" * 64})),
        ("substituted summary fingerprint", lambda: validate_documents(manifest, summary, integrity, **{**pins, "summary_sha256": "0" * 64})),
        ("substituted replay fingerprint", lambda: validate_documents(manifest, summary, integrity, **{**pins, "integrity_sha256": "0" * 64})),
        ("substituted runner fingerprint", lambda: validate_documents(manifest, summary, integrity, **{**pins, "runner_sha256": "0" * 64})),
        ("nonpublic manifest", lambda: validate_documents({**manifest, "holdout_accessed": True}, summary, integrity, **pins)),
        ("nonpublic summary", lambda: validate_documents(manifest, {**summary, "holdout_accessed": True}, integrity, **pins)),
        ("nonpublic replay", lambda: validate_documents(manifest, summary, {**integrity, "holdout_accessed": True}, **pins)),
        ("wrong public denominator", lambda: validate_documents(manifest, {**summary, "cases": CASES - 1}, integrity, **pins)),
        ("omitted frozen operation", lambda: validate_documents({**manifest, "public_operations": {key: value for key, value in OPERATIONS.items() if key != "split"}}, summary, integrity, **pins)),
        ("omitted workload category", lambda: validate_documents({**manifest, "categories": {key: value for index, (key, value) in enumerate(manifest["categories"].items()) if index}}, summary, integrity, **pins)),
        ("omitted frozen public case", lambda: validate_documents({**manifest, "selected_cases": manifest["selected_cases"][:-1]}, summary, integrity, **pins)),
        ("omitted measured candidate case", lambda: validate_documents(manifest, {**summary, "case_results": summary["case_results"][:-1]}, integrity, **pins)),
        ("omitted public candidate", lambda: validate_documents(manifest, {**summary, "rankings": summary["rankings"][:-1]}, integrity, **pins)),
        ("omitted individual slowdown", lambda: validate_documents(manifest, {**summary, "regressions": summary["regressions"][:-1]}, integrity, **pins)),
        ("omitted replayed slowdown", lambda: validate_documents(manifest, summary, {**integrity, "regressions": integrity["regressions"][:-1]}, **pins)),
        ("concealed total losses", lambda: validate_documents(manifest, summary, {**integrity, "strict_regressions": REGRESSIONS - 1}, **pins)),
        ("omitted timing observation", lambda: validate_documents(manifest, {**summary, "paired_raw_rows": RAW_ROWS - 1}, integrity, **pins)),
        ("omitted correctness gate", lambda: validate_documents(manifest, summary, {**integrity, "correctness_checks": CORRECTNESS_CHECKS - 1}, **pins)),
        ("omitted confidence interval", lambda: validate_documents(manifest, summary, {**integrity, "confidence_intervals_recomputed": CONFIDENCE_INTERVALS - 1}, **pins)),
        ("replayed public timing", lambda: validate_documents(manifest, summary, {**integrity, "timing_performed": True}, **pins)),
        ("imported production candidate", lambda: validate_documents(manifest, summary, {**integrity, "candidate_imported": True}, **pins)),
        ("substituted replayed summary", lambda: validate_documents(manifest, summary, {**integrity, "summary_sha256": "0" * 64}, **pins)),
        ("substituted raw stream", lambda: validate_documents(manifest, summary, {**integrity, "raw_sha256": "0" * 64}, **pins)),
        ("overclaimed native memory", lambda: validate_documents(manifest, summary, {**integrity, "memory_limitation": "all native allocations and final memory measured"}, **pins)),
        ("omitted stage-05 proof", lambda: validate_documents({**manifest, "stage05_correctness_artifacts": manifest["stage05_correctness_artifacts"][:-1]}, summary, integrity, **pins)),
        ("substituted universal oracle", lambda: validate_documents(manifest, {**summary, "python_re_universal_oracle_mismatches": 1}, integrity, **pins)),
        ("omitted isolation control", lambda: validate_documents(manifest, summary, {**integrity, "postfinal_no_delegation_control_count": 31}, **pins)),
        ("omitted native library", lambda: validate_documents(manifest, summary, {**integrity, "verified_native_library_count": 4}, **pins)),
        ("unverified integrity replay", lambda: validate_documents(manifest, summary, {**integrity, "result": "FAIL"}, **pins)),
    )
    output_poison_controls: tuple[tuple[str, Callable[[], None]], ...] = (
        (
            "substituted committed SVG bytes",
            lambda: plan_clear_outputs(
                charts,
                {**existing_outputs, "overall": ("regular", b"substituted public SVG")},
            ),
        ),
        (
            "symbolic-link output destination",
            lambda: plan_clear_outputs(
                charts,
                {**existing_outputs, "overall": ("symlink", None)},
            ),
        ),
        (
            "nonregular output destination",
            lambda: plan_clear_outputs(
                charts,
                {**existing_outputs, "overall": ("nonregular", None)},
            ),
        ),
        (
            "omitted exact output destination",
            lambda: plan_clear_outputs(
                charts,
                {suffix: existing_outputs[suffix] for suffix in SUFFIXES[:-1]},
            ),
        ),
        (
            "additional unowned output destination",
            lambda: plan_clear_outputs(
                charts,
                {**existing_outputs, "unowned": ("missing", None)},
            ),
        ),
        (
            "unexpected bytes at a missing output",
            lambda: plan_clear_outputs(
                charts,
                {**existing_outputs, "overall": ("missing", b"unexpected")},
            ),
        ),
        (
            "non-byte committed output",
            lambda: plan_clear_outputs(
                charts,
                {**existing_outputs, "overall": ("regular", None)},
            ),
        ),
        (
            "changed deterministic output source",
            lambda: plan_clear_outputs(
                {**charts, "overall": charts["overall"] + "substituted"},
                existing_outputs,
            ),
        ),
    )
    for label, action in (*poison_controls, *output_poison_controls):
        try:
            action()
        except (KeyError, TypeError, ValueError):
            continue
        raise ValueError(f"a synthetic clear-presentation control accepted {label}")
    require_candidate_free()
    return {
        "result": "PASS",
        "protocol_version": VERSION,
        "presentation_version": "postfinal-public-practice-presentation-v1",
        "mode": "candidate-free in-memory synthetic only; no files, subprocesses, timing, or holdout access",
        "synthetic_public_cases_per_candidate": CASES,
        "synthetic_workload_categories": CATEGORIES,
        "synthetic_operations": len(OPERATIONS),
        "synthetic_timing_rows": RAW_ROWS,
        "synthetic_correctness_checks": CORRECTNESS_CHECKS,
        "synthetic_confidence_intervals": CONFIDENCE_INTERVALS,
        "synthetic_individually_visible_losses": REGRESSIONS,
        "synthetic_stage05_proofs": 12,
        "synthetic_universal_proof_fields": len(UNIVERSAL_FIELDS),
        "candidate_free": True,
        "charts": len(charts),
        "deterministic": True,
        "reproducible_existing_outputs": True,
        "exclusive_missing_output_creation": True,
        "output_plan_adversarial_rejections": len(output_poison_controls),
        "adversarial_rejections": len(poison_controls) + len(output_poison_controls),
        "final_holdout": "NOT RUN",
        "native_final_memory": "NOT MEASURED",
    }


def render(
    *,
    summary: Path,
    integrity: Path,
    manifest: Path,
    manifest_sha256: str,
    runner_sha256: str,
    output_dir: Path,
) -> dict[str, Any]:
    """Write only six new clear SVGs after authenticating all V5 evidence."""

    require_candidate_free()
    require(manifest_sha256 == MANIFEST_SHA256, "--manifest-sha256 must be the exact frozen public V5 manifest")
    require(runner_sha256 == RUNNER_SHA256, "--runner-sha256 must be the exact frozen public V5 runner")
    require(output_dir.resolve() == EVIDENCE.resolve(), "clear public SVGs must use the exact V5 evidence directory")
    require(EVIDENCE.is_dir(), "the independently verified public V5 evidence directory is missing")
    verified_manifest = read_verified_json(manifest, expected=MANIFEST, digest=manifest_sha256)
    verified_summary = read_verified_json(summary, expected=SUMMARY, digest=SUMMARY_SHA256)
    verified_integrity = read_verified_json(integrity, expected=INTEGRITY, digest=INTEGRITY_SHA256)
    results = validate_documents(
        verified_manifest,
        verified_summary,
        verified_integrity,
        manifest_sha256=manifest_sha256,
        summary_sha256=SUMMARY_SHA256,
        integrity_sha256=INTEGRITY_SHA256,
        runner_sha256=runner_sha256,
    )
    charts = build_charts(results)
    destinations = {
        suffix: EVIDENCE / f"{VERSION}-clear-{suffix}.svg"
        for suffix in SUFFIXES
    }
    states: dict[str, tuple[str, bytes | None]] = {}
    for suffix, destination in destinations.items():
        if destination.is_symlink():
            states[suffix] = ("symlink", None)
        elif not destination.exists():
            states[suffix] = ("missing", None)
        elif not destination.is_file():
            states[suffix] = ("nonregular", None)
        else:
            states[suffix] = ("regular", destination.read_bytes())
    create = plan_clear_outputs(charts, states)
    outputs = []
    for suffix in SUFFIXES:
        destination = destinations[suffix]
        svg = charts[suffix]
        if create[suffix]:
            with destination.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write(svg)
        outputs.append(
            {
                "chart": suffix,
                "path": str(destination),
                "sha256": hashlib.sha256(svg.encode("utf-8")).hexdigest(),
            }
        )
    require_candidate_free()
    return {
        "result": "PASS",
        "protocol_version": VERSION,
        "presentation_version": "postfinal-public-practice-presentation-v1",
        "manifest_sha256": manifest_sha256,
        "summary_sha256": SUMMARY_SHA256,
        "integrity_sha256": INTEGRITY_SHA256,
        "runner_sha256": runner_sha256,
        "public_cases_per_candidate": CASES,
        "public_operations": len(OPERATIONS),
        "public_workload_categories": CATEGORIES,
        "public_raw_rows": RAW_ROWS,
        "public_correctness_checks": CORRECTNESS_CHECKS,
        "public_confidence_intervals": CONFIDENCE_INTERVALS,
        "individually_visible_public_losses": REGRESSIONS,
        "final_holdout": "NOT RUN",
        "native_final_memory": "NOT MEASURED",
        "charts": outputs,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Present independently verified V5 public regex results as six additional readable SVGs."
    )
    parser.add_argument("--self-test", action="store_true", help="run only candidate-free synthetic controls without reading or writing files")
    parser.add_argument("--summary", type=Path, help="exact independently replayed V5 public summary")
    parser.add_argument("--integrity", type=Path, help="exact passing V5 independent integrity report")
    parser.add_argument("--manifest", type=Path, help="exact frozen V5 public manifest")
    parser.add_argument("--manifest-sha256", help="required externally supplied frozen V5 manifest SHA-256")
    parser.add_argument("--runner-sha256", help="required externally supplied frozen V5 runner SHA-256")
    parser.add_argument("--output-dir", type=Path, help="exact existing V5 public evidence directory")
    args = parser.parse_args(argv)
    values = (args.summary, args.integrity, args.manifest, args.manifest_sha256, args.runner_sha256, args.output_dir)
    if args.self_test:
        if any(value is not None for value in values):
            parser.error("the synthetic self-test cannot read evidence or create SVGs")
    elif any(value is None for value in values):
        parser.error("presentation requires --summary, --integrity, --manifest, --manifest-sha256, --runner-sha256, and --output-dir")
    elif args.manifest_sha256 != MANIFEST_SHA256:
        parser.error("--manifest-sha256 must exactly match the committed V5 public manifest")
    elif args.runner_sha256 != RUNNER_SHA256:
        parser.error("--runner-sha256 must exactly match the committed V5 public runner")
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
    except (KeyError, OSError, TypeError, ValueError, ElementTree.ParseError) as error:
        print(f"independently verified public presentation rejected: {error}")
        return 2
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
