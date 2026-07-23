#!/usr/bin/env python3
"""Recompute historical slowdown counts from immutable version-6 summaries.

This audit never runs, profiles, times, or changes a benchmark. A replacement
that takes more than 120% of Python's time has baseline/candidate speed below
5/6. Earlier version-6 reports incorrectly used a cutoff of 4/5.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path

from tools import performance_v6_charts as charts


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "performance" / "v6" / "manifest.json"
GOAL = ROOT / "GOAL.md"
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
CASES_PER_COHORT = 6216
CORRECT_THRESHOLD = Decimal(5) / Decimal(6)
HISTORICAL_THRESHOLD = Decimal(4) / Decimal(5)
BASELINE = "re"
ZIG = "candidates.zig_candidate"
CANDIDATES = (
    "candidates.ast_candidate",
    "candidates.vm_candidate",
    "candidates.rust_candidate",
    "candidates.zig_candidate",
)
COHORTS = ("calibration", "holdout")
SOURCES = {
    "initial_five_engine": ROOT / "performance" / "v6" / "evidence" / "initial-summary.json.gz",
    "optimized_zig": ROOT / "candidates" / "evidence" / "zig-v6-final-summary.json.gz",
    "combined_final": ROOT / "candidates" / "evidence" / "zig-v6-combined-summary.json.gz",
    "first_zig_rerun": ROOT / "candidates" / "evidence" / "zig-v6-first-rerun-summary.json.gz",
}
BUG_SOURCES = (
    ROOT / "tools" / "perf_v5.py",
    ROOT / "tools" / "perf_v6.py",
    ROOT / "tools" / "zig_perf_v6.py",
    ROOT / "tools" / "rust_perf_v6.py",
    ROOT / "tools" / "rust_merge_v6.py",
)


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_summary(path: Path) -> tuple[dict, dict]:
    compressed = path.read_bytes()
    payload = gzip.decompress(compressed) if path.suffix == ".gz" else compressed
    result = json.loads(payload)
    if not isinstance(result, dict):
        raise RuntimeError(f"historical summary is not an object: {path}")
    return result, {
        "path": str(path.relative_to(ROOT)),
        "compressed_sha256": sha256(compressed),
        "expanded_sha256": sha256(payload),
        "compressed_bytes": len(compressed),
        "expanded_bytes": len(payload),
        "schema": result.get("schema"),
        "raw_sha256": result.get("raw_sha256"),
        "raw_rows": result.get("rows"),
    }


def candidate_keys(summary: dict, source: str) -> dict[tuple[str, str, str], dict]:
    rows = summary.get("case_results")
    if not isinstance(rows, list):
        raise RuntimeError(f"{source} omits historical per-case speedups")
    result = {}
    for row in rows:
        if not isinstance(row, dict):
            raise RuntimeError(f"{source} contains a malformed case result")
        key = (row.get("candidate"), row.get("cohort"), row.get("case"))
        if key in result:
            raise RuntimeError(f"{source} repeats a benchmark decision: {key}")
        candidate, cohort, case = key
        if candidate not in CANDIDATES or cohort not in COHORTS:
            raise RuntimeError(f"{source} changes a candidate or cohort: {key}")
        if not isinstance(case, str) or not case:
            raise RuntimeError(f"{source} contains an invalid case: {key}")
        speed = row.get("speedup")
        if (
            not isinstance(speed, (int, float))
            or isinstance(speed, bool)
            or not math.isfinite(speed)
            or speed <= 0
        ):
            raise RuntimeError(f"{source} contains an invalid speedup: {key}")
        expected_old = Decimal(str(speed)) < HISTORICAL_THRESHOLD
        if row.get("regression_gt_20pct") is not expected_old:
            raise RuntimeError(f"{source} does not use its recorded legacy cutoff: {key}")
        result[key] = row
    return result


def validate_summary(
    summary: dict,
    source: str,
    manifest: dict,
    wanted_candidates: tuple[str, ...],
) -> dict[tuple[str, str, str], dict]:
    if summary.get("expected_sha256") != manifest.get("expected_sha256"):
        raise RuntimeError(f"{source} does not use the frozen v6 correctness fixture")
    rows = candidate_keys(summary, source)
    if {key[0] for key in rows} != set(wanted_candidates):
        raise RuntimeError(f"{source} omits or changes an independent candidate")
    for candidate in wanted_candidates:
        for cohort in COHORTS:
            selected = [
                row for (engine, actual_cohort, _), row in rows.items()
                if engine == candidate and actual_cohort == cohort
            ]
            if len(selected) != CASES_PER_COHORT:
                raise RuntimeError(
                    f"{source} changed the {cohort} denominator for {candidate}: "
                    f"{len(selected)} != {CASES_PER_COHORT}"
                )
    rankings = summary.get("rankings")
    if not isinstance(rankings, list):
        raise RuntimeError(f"{source} omits its frozen ranking")
    expected_rankings = {
        (cohort, candidate)
        for cohort in (*COHORTS, "all")
        for candidate in wanted_candidates
    }
    actual_rankings = {(row.get("cohort"), row.get("candidate")) for row in rankings}
    if actual_rankings != expected_rankings or len(rankings) != len(expected_rankings):
        raise RuntimeError(f"{source} ranking candidate/cohort balance changed")
    for rank in rankings:
        candidate = rank["candidate"]
        cohort = rank["cohort"]
        selected = [
            row
            for (engine, actual_cohort, _), row in rows.items()
            if engine == candidate and (cohort == "all" or actual_cohort == cohort)
        ]
        if rank.get("cases") != len(selected):
            raise RuntimeError(f"{source} changes ranking task count: {cohort} {candidate}")
        old = sum(bool(row["regression_gt_20pct"]) for row in selected)
        if rank.get("regressions_gt_20pct") != old:
            raise RuntimeError(f"{source} historical ranking loss count is inconsistent")
    expected_regressions = {
        key for key, row in rows.items() if row["regression_gt_20pct"]
    }
    old_regressions = summary.get("regressions")
    if not isinstance(old_regressions, list):
        raise RuntimeError(f"{source} omits its historical regressions")
    reported_regressions = {
        (row.get("candidate"), row.get("cohort"), row.get("case"))
        for row in old_regressions
    }
    if reported_regressions != expected_regressions:
        raise RuntimeError(f"{source} historical regression records changed")
    return rows


def corrected_flag(row: dict) -> bool:
    return Decimal(str(row["speedup"])) < CORRECT_THRESHOLD


def fixture_explanation(row: dict) -> str:
    category = row["category"]
    if category == "expanded-ip-version":
        return (
            "Frozen version-5 compiled findall on one short semantic-version "
            "string. The expression returns four captures; the archived Zig "
            "report attributes this workload to Python/native call and "
            "capture-result construction dominating a tiny match. No new "
            "profiling was performed."
        )
    if category == "deeper-negative-class":
        return (
            "Frozen version-6 compiled findall on one short key=value field. "
            "The expression evaluates two bounded negated character classes, "
            "two captures, and a delimiter lookahead. The recorded extra "
            "elapsed time is real; a more specific implementation-level "
            "cause is NOT MEASURED."
        )
    return (
        "The immutable category identifies the measured workload. A more "
        "specific implementation-level cause is NOT MEASURED."
    )


def loss_record(row: dict) -> dict:
    speed = Decimal(str(row["speedup"]))
    slower_percent = (Decimal(1) / speed - Decimal(1)) * Decimal(100)
    return {
        "case": row["case"],
        "cohort": row["cohort"],
        "category": row["category"],
        "candidate": row["candidate"],
        "speedup": row["speedup"],
        "candidate_slower_percent": float(slower_percent),
        "ci95_low": row.get("ci95_low"),
        "ci95_high": row.get("ci95_high"),
        "previously_reported": bool(row["regression_gt_20pct"]),
        "fixture_explanation": fixture_explanation(row),
    }


def count_candidate(rows: list[dict]) -> dict:
    old = [row for row in rows if row["regression_gt_20pct"]]
    corrected = [row for row in rows if corrected_flag(row)]
    newly_visible = [
        row for row in corrected if not row["regression_gt_20pct"]
    ]
    return {
        "cases": len(rows),
        "historically_reported_regressions": len(old),
        "corrected_regressions": len(corrected),
        "previously_hidden_regressions": len(newly_visible),
        "corrected_category_counts": dict(
            sorted(Counter(row["category"] for row in corrected).items())
        ),
        "hidden_category_counts": dict(
            sorted(Counter(row["category"] for row in newly_visible).items())
        ),
        "hidden_cases": [
            loss_record(row)
            for row in sorted(newly_visible, key=lambda item: item["case"])
        ],
    }


def cohort_counts(
    lookup: dict[tuple[str, str, str], dict],
    candidates: tuple[str, ...],
) -> dict:
    result = {}
    for cohort in (*COHORTS, "all"):
        groups = {}
        baseline_cases = CASES_PER_COHORT * (2 if cohort == "all" else 1)
        groups[BASELINE] = {
            "cases": baseline_cases,
            "historically_reported_regressions": 0,
            "corrected_regressions": 0,
            "previously_hidden_regressions": 0,
            "corrected_category_counts": {},
            "hidden_category_counts": {},
            "hidden_cases": [],
            "basis": "Python baseline is 1× against itself by definition.",
        }
        for candidate in candidates:
            selected = [
                row
                for (engine, actual_cohort, _), row in lookup.items()
                if engine == candidate and (cohort == "all" or actual_cohort == cohort)
            ]
            groups[candidate] = count_candidate(selected)
        result[cohort] = groups
    return result


def source_evidence() -> list[dict]:
    evidence = []
    for path in BUG_SOURCES:
        payload = path.read_bytes()
        lines = payload.decode("utf-8").splitlines()
        findings = [
            {"line": number, "source": line.strip()}
            for number, line in enumerate(lines, 1)
            if (
                "regression_gt_20pct" in line
                and ("0.8" in line or "< .8" in line or "<.8" in line)
            )
        ]
        if not findings:
            raise RuntimeError(f"legacy threshold source marker not found: {path}")
        evidence.append(
            {
                "path": str(path.relative_to(ROOT)),
                "sha256": sha256(payload),
                "findings": findings,
            }
        )
    return evidence


def validate_combination(
    initial: dict[tuple[str, str, str], dict],
    final: dict[tuple[str, str, str], dict],
    combined: dict[tuple[str, str, str], dict],
) -> None:
    expected = {
        **{key: row for key, row in initial.items() if key[0] != ZIG},
        **final,
    }
    if combined != expected:
        missing = sorted(set(expected) ^ set(combined))[:5]
        changed = next(
            (key for key in expected.keys() & combined.keys() if expected[key] != combined[key]),
            None,
        )
        raise RuntimeError(
            f"combined summary does not preserve initial engines and final Zig: "
            f"missing={missing}, changed={changed}"
        )


def corrected_summary(summary: dict) -> dict:
    result = {key: value for key, value in summary.items()}
    results = []
    for row in summary["case_results"]:
        updated = dict(row)
        updated["regression_gt_20pct"] = corrected_flag(row)
        results.append(updated)
    rankings = []
    for row in summary["rankings"]:
        updated = dict(row)
        updated["regressions_gt_20pct"] = sum(
            item["regression_gt_20pct"]
            for item in results
            if item["candidate"] == row["candidate"]
            and (row["cohort"] == "all" or item["cohort"] == row["cohort"])
        )
        rankings.append(updated)
    result["case_results"] = results
    result["rankings"] = rankings
    result["regressions"] = [
        row for row in results if row["regression_gt_20pct"]
    ]
    return result


def write_charts(summary: dict, prefix: Path) -> list[str]:
    prefix.parent.mkdir(parents=True, exist_ok=True)
    operations = (
        ("overall", charts.overall),
        ("zig-speed", charts.zig_speed),
        ("family-speed", charts.family_speed),
        ("memory", charts.memory),
        ("win-loss", charts.win_loss),
        ("rankings", charts.rankings),
    )
    written = []
    for name, action in operations:
        destination = Path(f"{prefix}-{name}.svg")
        action(summary, str(destination))
        written.append(str(destination.relative_to(ROOT)))
    return written


def display_name(candidate: str) -> str:
    return {
        BASELINE: "Python `re` baseline",
        "candidates.ast_candidate": "Python engine",
        "candidates.vm_candidate": "Native C engine",
        "candidates.rust_candidate": "Rust engine",
        ZIG: "Zig / `rebar`",
    }[candidate]


def markdown(report: dict) -> str:
    initial = report["initial_five_engine"]["holdout"]
    final = report["combined_final"]["holdout"]
    zig = report["optimized_zig"]["holdout"][ZIG]
    lines = [
        "# Correcting the historical slowdown threshold",
        "",
        "A result is **more than 20% slower** when a replacement takes more "
        "than `1.2 ×` Python's time. Because reported speed is "
        "`Python time / replacement time`, the correct cutoff is "
        "`speed < 1 / 1.2`, or `speed < 5 / 6`.",
        "",
        "The earlier version-6 code instead used `speed < 0.8`. That flags "
        "replacements only when they are more than **25% slower**. It therefore "
        "omitted the more-than-20%-through-25% interval. The frozen inputs, "
        "original timings, official summaries, and confidence ranges have "
        "**not** been changed or rerun.",
        "",
        "## Original five-engine test",
        "",
        f"All counts use the complete **{CASES_PER_COHORT:,}-case unseen "
        "holdout**. Python `re` is the unchanged reference.",
        "",
        "| Engine | Original reported slowdowns | Corrected more-than-20% slowdowns | Previously omitted |",
        "| --- | ---: | ---: | ---: |",
    ]
    for candidate in (BASELINE, *CANDIDATES):
        values = initial[candidate]
        lines.append(
            f"| {display_name(candidate)} | "
            f"{values['historically_reported_regressions']:,}/{values['cases']:,} | "
            f"{values['corrected_regressions']:,}/{values['cases']:,} | "
            f"{values['previously_hidden_regressions']:,} |"
        )
    lines += [
        "",
        "## Optimized Zig and preserved final comparison",
        "",
        f"The optimized Zig rerun originally reported "
        f"**{zig['historically_reported_regressions']:,}** large holdout "
        f"slowdowns. Applying the correct threshold to its existing "
        f"{zig['cases']:,} measured speedups gives "
        f"**{zig['corrected_regressions']:,}**, including "
        f"**{zig['previously_hidden_regressions']:,}** previously omitted cases.",
        "",
        "| Engine in final comparison | Corrected holdout slowdowns | Previously omitted |",
        "| --- | ---: | ---: |",
    ]
    for candidate in (BASELINE, *CANDIDATES):
        values = final[candidate]
        lines.append(
            f"| {display_name(candidate)} | "
            f"{values['corrected_regressions']:,}/{values['cases']:,} | "
            f"{values['previously_hidden_regressions']:,} |"
        )
    lines += [
        "",
        "### Every corrected optimized-Zig holdout slowdown",
        "",
        "- **Six short version strings:** each frozen `findall` case matches "
        "one short semantic version and returns four captures. The earlier "
        "Zig report attributes this already-profiled family to Python/native "
        "call and capture-result construction exceeding the small matching "
        "cost. Four of these six cases were previously omitted.",
        "- **One short negated-class field:** the frozen `findall` case "
        "checks one `key=value` record with two bounded negated classes, "
        "two captures, and a delimiter lookahead. Its measured 20.25% "
        "slowdown was previously omitted. A more specific "
        "implementation-level explanation is **NOT MEASURED**; this audit "
        "does not re-profile the holdout.",
        "",
        "| Frozen task | Workload | Speed relative to Python | Extra time | Omitted before? |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for row in report["optimized_zig_corrected_holdout_losses"]:
        lines.append(
            f"| `{row['case']}` | `{row['category']}` | "
            f"{row['speedup']:.4f}× | "
            f"{row['candidate_slower_percent']:.2f}% | "
            f"{'No' if row['previously_reported'] else 'Yes'} |"
        )
    if not report["optimized_zig_corrected_holdout_losses"]:
        lines.append("| None | — | — | — | — |")
    lines += [
        "",
        "The frozen task names identify the exact kind of work. Category "
        "counts and every previously omitted case for every engine and test "
        "set are retained in "
        "[regression-threshold-audit.json](regression-threshold-audit.json). "
        "This audit does not infer an unmeasured implementation cause or "
        "claim a new speed measurement.",
        "",
        "## Evidence and reproduction",
        "",
        "The audit verifies the version-6 expected-result hash, every "
        "candidate and holdout denominator, each historical flag and ranking, "
        "and that the final combined comparison exactly preserves all original "
        "non-Zig results plus the optimized Zig run. Compressed and expanded "
        "source hashes are recorded in the JSON evidence.",
        "",
        "```sh",
        "PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14",
        'PYTHONPATH=. "$PY" tools/perf_regression_audit.py',
        "```",
        "",
        "The command reads already-recorded summaries and regenerates the "
        "audit and newly named corrected charts. It never executes a regex "
        "candidate, times an operation, changes the frozen fixture, or "
        "rewrites a historical result.",
        "",
    ]
    return "\n".join(lines)


def self_test() -> int:
    vectors = (
        (0.79, True, True),
        (0.8, False, True),
        (0.82, False, True),
        (0.8333333333333333, False, True),
        (0.8333333333333334, False, False),
        (0.84, False, False),
        (1.0, False, False),
    )
    for speed, old, corrected in vectors:
        observed_old = Decimal(str(speed)) < HISTORICAL_THRESHOLD
        observed_corrected = corrected_flag({"speedup": speed})
        if (observed_old, observed_corrected) != (old, corrected):
            raise RuntimeError(
                f"slowdown boundary check failed at {speed}: "
                f"{(observed_old, observed_corrected)} != {(old, corrected)}"
            )
    print(
        json.dumps(
            {
                "schema": "rebar-performance-v6-regression-threshold-self-test-v1",
                "boundary_cases": len(vectors),
                "historical_threshold": "speedup < 4/5",
                "correct_threshold": "speedup < 5/6",
                "passed": len(vectors),
                "failed": 0,
                "timing": "NOT MEASURED",
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-json",
        type=Path,
        default=ROOT / "performance" / "v6" / "evidence" / "regression-threshold-audit.json",
    )
    parser.add_argument(
        "--output-markdown",
        type=Path,
        default=ROOT / "performance" / "v6" / "evidence" / "REGRESSION-THRESHOLD-AUDIT.md",
    )
    parser.add_argument(
        "--chart-prefix",
        type=Path,
        default=ROOT / "candidates" / "evidence" / "zig-v6-threshold-corrected",
    )
    parser.add_argument("--no-charts", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    if sys.implementation.name != "cpython" or sys.version_info[:3] != (3, 14, 6):
        raise RuntimeError("historical audit requires frozen CPython 3.14.6")
    if sha256(GOAL.read_bytes()) != GOAL_SHA256:
        raise RuntimeError("the immutable objective changed")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if (
        manifest.get("schema") != "rebar-performance-v6"
        or manifest.get("cases") != 12432
        or manifest.get("python") != "3.14.6"
        or manifest.get("goal_sha256") != GOAL_SHA256
    ):
        raise RuntimeError("the frozen version-6 performance manifest changed")

    summaries = {}
    provenance = {}
    for name, path in SOURCES.items():
        summaries[name], provenance[name] = load_summary(path)

    initial = validate_summary(
        summaries["initial_five_engine"], "initial_five_engine", manifest, CANDIDATES
    )
    optimized = validate_summary(
        summaries["optimized_zig"], "optimized_zig", manifest, (ZIG,)
    )
    combined = validate_summary(
        summaries["combined_final"], "combined_final", manifest, CANDIDATES
    )
    rerun = validate_summary(
        summaries["first_zig_rerun"], "first_zig_rerun", manifest, (ZIG,)
    )
    validate_combination(initial, optimized, combined)

    optimized_holdout = [
        row
        for (candidate, cohort, _), row in optimized.items()
        if candidate == ZIG and cohort == "holdout" and corrected_flag(row)
    ]
    cause_groups = {}
    for category in sorted({row["category"] for row in optimized_holdout}):
        entries = sorted(
            (row for row in optimized_holdout if row["category"] == category),
            key=lambda row: row["case"],
        )
        cause_groups[category] = {
            "cases": len(entries),
            "previously_hidden": sum(
                not row["regression_gt_20pct"] for row in entries
            ),
            "case_ids": [row["case"] for row in entries],
            "fixture_explanation": fixture_explanation(entries[0]),
        }
    report = {
        "schema": "rebar-performance-v6-regression-threshold-audit-v1",
        "status": "CORRECTED HISTORICAL REPORTING; NO RETIMING",
        "measurement": (
            "Derived exclusively from complete already-recorded frozen v6 "
            "per-case speedups; no benchmark execution or holdout profiling."
        ),
        "python": "3.14.6",
        "goal_sha256": GOAL_SHA256,
        "expected_sha256": manifest["expected_sha256"],
        "cohort_cases": CASES_PER_COHORT,
        "baseline_and_candidates": [BASELINE, *CANDIDATES],
        "speedup_definition": "pinned Python re elapsed time / candidate elapsed time",
        "correct_slowdown_definition": "candidate elapsed time > 1.2 * Python elapsed time",
        "correct_speedup_threshold": "speedup < 5/6",
        "incorrect_historical_threshold": "speedup < 4/5",
        "hidden_slowdown_interval": "20% < candidate extra elapsed time <= 25%",
        "source_summaries": provenance,
        "historical_source_findings": source_evidence(),
        "initial_five_engine": cohort_counts(initial, CANDIDATES),
        "optimized_zig": cohort_counts(optimized, (ZIG,)),
        "combined_final": cohort_counts(combined, CANDIDATES),
        "first_zig_rerun": cohort_counts(rerun, (ZIG,)),
        "optimized_zig_corrected_holdout_losses": [
            loss_record(row)
            for row in sorted(optimized_holdout, key=lambda item: item["case"])
        ],
        "optimized_zig_holdout_cause_groups": cause_groups,
        "historical_raw_timings_changed": False,
        "historical_summaries_changed": False,
        "holdout_retimed": False,
        "holdout_profiled": False,
        "timing": "NOT MEASURED; existing complete speedups only",
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    if not args.no_charts:
        report["corrected_charts"] = write_charts(
            corrected_summary(summaries["combined_final"]), args.chart_prefix
        )
    else:
        report["corrected_charts"] = []
    args.output_json.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.output_markdown.write_text(markdown(report), encoding="utf-8")

    def compact(cohort):
        return {
            display_name(candidate): {
                "old": values["historically_reported_regressions"],
                "correct": values["corrected_regressions"],
                "hidden": values["previously_hidden_regressions"],
            }
            for candidate, values in cohort.items()
        }

    print(
        json.dumps(
            {
                "schema": report["schema"],
                "cases_per_holdout": CASES_PER_COHORT,
                "initial_holdout": compact(report["initial_five_engine"]["holdout"]),
                "optimized_zig_holdout": compact(report["optimized_zig"]["holdout"]),
                "combined_final_holdout": compact(report["combined_final"]["holdout"]),
                "zig_corrected_holdout_cases": report[
                    "optimized_zig_corrected_holdout_losses"
                ],
                "charts": report["corrected_charts"],
                "json": str(args.output_json),
                "markdown": str(args.output_markdown),
            },
            ensure_ascii=False,
            sort_keys=True,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
