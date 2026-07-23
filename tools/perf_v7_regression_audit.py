#!/usr/bin/env python3
"""Explain and preserve every strictly measured frozen-v7 slowdown."""

from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import json
import math
import statistics
from pathlib import Path

from tools.perf_v5 import source_kind
from tools.perf_v7 import (
    COHORTS,
    REGRESSION_SPEEDUP_THRESHOLD,
    ROOT,
    SUMMARY_SCHEMA,
    frozen,
    is_runtime_regression,
    verify_regression_boundaries,
)


SCHEMA = "rebar-performance-regression-audit-v7"
INTEGRITY_SCHEMA = "rebar-performance-result-integrity-v7"
NAMES = {
    "candidates.ast_candidate": "Python engine",
    "candidates.vm_candidate": "C engine",
    "candidates.rust_candidate": "Rust engine",
    "candidates.zig_candidate": "Zig engine",
}
ZIG = "candidates.zig_candidate"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def display_path(path: Path) -> str:
    """Keep repository paths readable without rejecting external outputs."""
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT.resolve()))
    except ValueError:
        return str(resolved)


def positive_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value > 0
    )


def load_json(path: Path, label: str) -> tuple[dict, str]:
    if path.suffix == ".gz":
        with gzip.open(path, "rb") as compressed:
            payload = compressed.read()
    else:
        payload = path.read_bytes()
    try:
        value = json.loads(payload)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"invalid {label}: {path}") from error
    require(isinstance(value, dict), f"invalid {label} object: {path}")
    return value, hashlib.sha256(payload).hexdigest()


def check_strict_regressions(
    case_results: object, recorded_regressions: object
) -> dict[tuple[str, str], dict]:
    """Reject every missing, extra, changed, or duplicate strict slowdown."""
    require(isinstance(case_results, list), "candidate case results are missing")
    require(isinstance(recorded_regressions, list), "complete slowdown records are missing")
    results: dict[tuple[str, str], dict] = {}
    expected: dict[tuple[str, str], dict] = {}
    for row in case_results:
        require(isinstance(row, dict), "a candidate case result is not an object")
        case = row.get("case")
        candidate = row.get("candidate")
        require(isinstance(case, str) and case, "a candidate result has no case")
        require(isinstance(candidate, str) and candidate, "a candidate result has no engine")
        key = (case, candidate)
        require(key not in results, f"duplicate candidate case result: {key}")
        speedup = row.get("speedup")
        require(positive_number(speedup), f"invalid measured speed: {key}")
        slowdown = is_runtime_regression(speedup)
        require(
            row.get("regression_gt_20pct") is slowdown,
            f"incorrect strictly-more-than-20% flag: {key}",
        )
        results[key] = row
        if slowdown:
            expected[key] = row

    require(
        len(recorded_regressions) == len(expected),
        "a measured slowdown was omitted or an extra slowdown was inserted",
    )
    seen: set[tuple[str, str]] = set()
    for row in recorded_regressions:
        require(isinstance(row, dict), "a recorded slowdown is not an object")
        key = (row.get("case"), row.get("candidate"))
        require(key in expected, f"unmeasured or below-threshold slowdown: {key}")
        require(key not in seen, f"duplicate recorded slowdown: {key}")
        require(row == expected[key], f"changed measured slowdown: {key}")
        seen.add(key)
    require(seen == set(expected), "a measured slowdown is absent")
    return expected


def self_test() -> dict:
    boundary = verify_regression_boundaries()
    require(REGRESSION_SPEEDUP_THRESHOLD == 5.0 / 6.0, "strict slowdown rule changed")
    require(
        display_path(ROOT / "performance" / "v7") == "performance/v7",
        "a repository output lost its reproducible relative path",
    )
    require(
        Path(display_path(Path("/tmp/rebar-v7-regression-audit-self-test.json.gz"))).is_absolute(),
        "an external evidence output was incorrectly rejected or relativized",
    )
    expectations = (
        (0.80, True),
        (0.81, True),
        (0.833, True),
        (5.0 / 6.0, False),
        (0.84, False),
        (1.0, False),
    )
    results = [
        {
            "case": f"boundary-{index}",
            "candidate": "self-test-engine",
            "speedup": speedup,
            "regression_gt_20pct": expected,
        }
        for index, (speedup, expected) in enumerate(expectations)
    ]
    recorded = [row.copy() for row in results if row["regression_gt_20pct"]]
    checked = check_strict_regressions(results, recorded)
    require(len(checked) == 3, "strict threshold missed a boundary slowdown")
    require(
        sum(row["speedup"] < 0.8 for row in results) == 0,
        "the historical 0.8 rule unexpectedly captures strict boundary examples",
    )

    rejected = 0
    mutations = (
        (results, recorded[:-1]),
        (results, [*recorded, recorded[0]]),
        ([*results, results[0]], recorded),
        (
            [
                {**row, "regression_gt_20pct": not row["regression_gt_20pct"]}
                if index == 1
                else row
                for index, row in enumerate(results)
            ],
            recorded,
        ),
        (results, [{**recorded[0], "speedup": 0.79}, *recorded[1:]]),
    )
    for changed_results, changed_recorded in mutations:
        try:
            check_strict_regressions(changed_results, changed_recorded)
        except RuntimeError:
            rejected += 1
        else:
            raise RuntimeError("regression audit accepted corrupted slowdown evidence")

    return {
        "schema": f"{SCHEMA}-self-test",
        **boundary,
        "boundary_examples": len(expectations),
        "strict_boundary_regressions": len(checked),
        "rejected_corruptions": rejected,
        "failed": 0,
    }


def observed_explanation(case: dict) -> str:
    """Describe timed work, without pretending component costs were profiled."""
    api = case["api"]
    lifecycle = case["lifecycle"]
    input_kind = source_kind(case)

    if api == "compile":
        work = "Cold compilation includes clearing the cache and parsing and compiling the pattern"
    elif api == "escape":
        work = "Module-level escaping includes constructing the escaped Python result"
    elif lifecycle == "cold":
        work = f"Cold {api} includes clearing the cache, compiling the pattern and running the operation"
    elif api == "scanner":
        work = "Precompiled scanning includes creating the scanner, repeated search calls and collecting match objects"
    elif api == "match-surface":
        work = "Match access includes the search, groups, named groups, spans and template expansion"
    elif api == "finditer":
        work = f"{lifecycle.capitalize()} finditer includes collecting all match objects into a Python list"
    elif api == "findall":
        work = f"{lifecycle.capitalize()} findall includes constructing the complete Python result"
    elif api == "split":
        work = f"{lifecycle.capitalize()} split includes constructing every returned text and capture"
    elif api in {"sub", "subn"}:
        replacement = case.get("repl")
        if isinstance(replacement, dict) and "callable" in replacement:
            work = (
                f"{lifecycle.capitalize()} {api} includes invoking the Python replacement "
                "callback and constructing the output"
            )
        else:
            work = f"{lifecycle.capitalize()} {api} includes replacement expansion and constructing the output"
    else:
        work = f"{lifecycle.capitalize()} {api} includes performing the match and returning the Python result"

    if input_kind != "text":
        work += f" on {input_kind} input"
    return f"{work}; separate engine, boundary and allocation costs NOT MEASURED."


def enriched(row: dict, case: dict) -> dict:
    speedup = row["speedup"]
    require(
        is_runtime_regression(speedup),
        f"non-regression cannot enter complete slowdown evidence: {row['case']}",
    )
    return {
        **row,
        "api": case["api"],
        "lifecycle": case["lifecycle"],
        "input_kind": source_kind(case),
        "operations": case["ops"],
        "runtime_increase_fraction": 1.0 / speedup - 1.0,
        "explanation": observed_explanation(case),
    }


def grouped(rows: list[dict], field: str) -> list[dict]:
    groups: dict[str, list[dict]] = collections.defaultdict(list)
    for row in rows:
        groups[row[field]].append(row)
    result = []
    for label, values in groups.items():
        speedups = [row["speedup"] for row in values]
        result.append(
            {
                "name": label,
                "cases": len(values),
                "median_speedup": statistics.median(speedups),
                "slowest_speedup": min(speedups),
                "largest_runtime_increase_fraction": max(
                    row["runtime_increase_fraction"] for row in values
                ),
            }
        )
    result.sort(key=lambda item: (-item["cases"], item["name"]))
    require(sum(item["cases"] for item in result) == len(rows), f"incomplete {field} grouping")
    return result


def archive_json(document: dict, destination: Path) -> dict:
    payload = (
        json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")
    expected_sha256 = hashlib.sha256(payload).hexdigest()
    if destination.exists():
        require(destination.is_file(), f"regression archive is not a file: {destination}")
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as target:
            with gzip.GzipFile(
                filename="", fileobj=target, mode="wb", compresslevel=9, mtime=0
            ) as compressed:
                compressed.write(payload)
    with gzip.open(destination, "rb") as compressed:
        restored = compressed.read()
    require(restored == payload, f"regression archive omitted or changed evidence: {destination}")
    with destination.open("rb") as compressed:
        header = compressed.read(10)
    require(len(header) == 10 and header[:2] == b"\x1f\x8b", "invalid regression gzip")
    require(header[3] & 0x08 == 0, "regression gzip contains a non-deterministic filename")
    require(header[4:8] == b"\0\0\0\0", "regression gzip contains a non-deterministic timestamp")
    archive_digest = hashlib.sha256()
    with destination.open("rb") as compressed:
        for chunk in iter(lambda: compressed.read(1024 * 1024), b""):
            archive_digest.update(chunk)
    return {
        "path": display_path(destination),
        "sha256": archive_digest.hexdigest(),
        "bytes": destination.stat().st_size,
        "restored_sha256": expected_sha256,
        "restored_bytes": len(payload),
        "gzip_mtime": 0,
        "gzip_filename": "",
    }


def percent(value: float) -> str:
    return f"{100.0 * value:.1f}%"


def speed(value: float) -> str:
    return f"{value:.3f}×"


def group_table(title: str, rows: list[dict]) -> list[str]:
    lines = [
        f"### {title}",
        "",
        "| Group | Slower cases | Median speed versus Python | Slowest case | Largest extra time |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        label = row["name"].removeprefix("broader-").removeprefix("deeper-")
        label = label.replace("-", " ")
        lines.append(
            f"| {label} | {row['cases']} | {speed(row['median_speedup'])} | "
            f"{speed(row['slowest_speedup'])} | "
            f"{percent(row['largest_runtime_increase_fraction'])} |"
        )
    lines.append("")
    return lines


def markdown_report(document: dict, archive: dict) -> str:
    lines = [
        "# Measured slowdowns against Python",
        "",
        "This report accounts for every case in which a replacement took more than "
        "20% longer than the unchanged Python 3.14.6 `re` module. "
        "Nothing is removed when a result is inconvenient.",
        "",
        f"- Total benchmark: **{document['cases']:,}** different workloads, "
        f"**{document['cases_per_cohort']:,}** of them independently held back.",
        f"- Competitors: **{document['candidate_count']}** independent implementations, "
        "each measured against the same Python baseline and workloads.",
        f"- Complete strict slowdowns across every competitor and workload: "
        f"**{document['total_regressions']:,}**.",
        "- A speed above `1×` is faster than Python. A slowdown is counted only "
        "when `Python time / replacement time < 5/6`; exactly `5/6` is not "
        "more than 20% slower.",
        "- Confidence intervals come from the original frozen, paired benchmark. "
        "The audit performs no new timing and does not change the held-back tests.",
        "",
        "## Overall results",
        "",
        "| Engine | Cases | Overall speed versus Python | 95% confidence interval | "
        "Reliably faster cases | More-than-20% slowdowns |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in document["all_rankings"]:
        lines.append(
            f"| {NAMES[row['candidate']]} | {row['cases']:,} | "
            f"{speed(row['geomean_speedup'])} | "
            f"{speed(row['ci95_low'])}–{speed(row['ci95_high'])} | "
            f"{row['statistically_faster_cases']:,}/{row['cases']:,} | "
            f"{row['regressions_gt_20pct']:,} |"
        )
    lines.extend(
        [
            "",
            "## Independently held-back results",
            "",
            "| Engine | Held-back cases | Overall speed versus Python | "
            "95% confidence interval | Reliably faster cases | More-than-20% slowdowns |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in document["holdout_rankings"]:
        lines.append(
            f"| {NAMES[row['candidate']]} | {row['cases']:,} | "
            f"{speed(row['geomean_speedup'])} | "
            f"{speed(row['ci95_low'])}–{speed(row['ci95_high'])} | "
            f"{row['statistically_faster_cases']:,}/{row['cases']:,} | "
            f"{row['regressions_gt_20pct']:,} |"
        )

    zig = document["zig_holdout_regressions"]
    lines.extend(
        [
            "",
            "## Every held-back Zig slowdown",
            "",
            f"The Zig engine has **{len(zig)}** more-than-20% slowdowns among "
            f"**{document['cases_per_cohort']:,}** held-back workloads and "
            f"**{document['zig_total_regressions']}** across all "
            f"**{document['cases']:,}** workloads. Every held-back case appears below.",
            "",
            "The explanations describe what the frozen benchmark actually timed. "
            "They are not claims that a particular parser, matcher, Python/native "
            "call, memory allocation, or conversion was independently responsible: "
            "individual component costs were **NOT MEASURED**.",
            "",
        ]
    )
    lines.extend(group_table("By kind of workload", document["zig_holdout_groups"]["category"]))
    lines.extend(group_table("By Python operation", document["zig_holdout_groups"]["api"]))
    lines.extend(group_table("By pattern lifetime", document["zig_holdout_groups"]["lifecycle"]))
    lines.extend(group_table("By text or binary input", document["zig_holdout_groups"]["input_kind"]))
    lines.extend(
        [
            "### All individual held-back cases",
            "",
            "| Frozen case | Workload | Python operation | Pattern lifetime | "
            "Input | Speed versus Python | Extra time | 95% confidence interval | "
            "Operations per trial | What was actually measured |",
            "| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in zig:
        workload = (
            row["category"].removeprefix("broader-").removeprefix("deeper-")
            .replace("-", " ")
        )
        lines.append(
            f"| `{row['case']}` | {workload} | `{row['api']}` | "
            f"{row['lifecycle']} | {row['input_kind']} | {speed(row['speedup'])} | "
            f"{percent(row['runtime_increase_fraction'])} | "
            f"{speed(row['ci95_low'])}–{speed(row['ci95_high'])} | "
            f"{row['operations']} | {row['explanation']} |"
        )
    lines.extend(
        [
            "",
            "## Complete machine-readable evidence",
            "",
            f"[`initial-regressions.json.gz`](initial-regressions.json.gz) "
            f"contains all **{document['total_regressions']:,}** measured "
            "slowdowns, for all four candidates and both cohorts, including their "
            "original measured results, confidence intervals, traced-memory ratios, "
            "frozen workload metadata, and honest descriptions of timed work.",
            "",
            f"- Frozen correctness and workload digest: `{document['expected_sha256']}`.",
            f"- Complete raw measurement digest: `{document['raw_sha256']}`.",
            f"- Complete original analysis digest: `{document['summary_sha256']}`.",
            f"- Independently audited integrity report digest: `{document['integrity_sha256']}`.",
            f"- Compressed complete-slowdown archive digest: `{archive['sha256']}`.",
            f"- Restored complete-slowdown evidence digest: `{archive['restored_sha256']}`.",
            "",
            "Reproduce this report without running or changing the benchmark:",
            "",
            "```sh",
            "PYTHONPATH=. /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 "
            "tools/perf_v7_regression_audit.py --self-test",
            "PYTHONPATH=. /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 "
            "tools/perf_v7_regression_audit.py "
            "--integrity performance/v7/evidence/initial-integrity.json "
            "--summary performance/v7/evidence/initial-summary.json.gz "
            "--output performance/v7/evidence/REGRESSION-AUDIT.md "
            "--json-output performance/v7/evidence/initial-regressions.json.gz",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def audit(integrity_path: Path, summary_path: Path) -> dict:
    boundary = self_test()
    suite, cases, _expected, manifest = frozen()
    modules = tuple(suite.MODULES)
    candidates = modules[1:]
    require(modules[0] == "re", "the unchanged Python baseline changed")
    require(set(candidates) == set(NAMES), "an independent competitor was dropped")
    require(len(cases) == 20_624, "the full workload denominator changed")
    require(suite.CASES_PER_COHORT == 10_312, "the held-back denominator changed")

    integrity, integrity_sha256 = load_json(integrity_path, "integrity report")
    summary, summary_sha256 = load_json(summary_path, "original benchmark summary")
    require(integrity.get("schema") == INTEGRITY_SCHEMA, "incorrect integrity-report schema")
    require(integrity.get("failed") == 0, "the independently audited benchmark has failures")
    require(summary.get("schema") == SUMMARY_SCHEMA, "incorrect frozen benchmark-summary schema")
    require(
        integrity.get("summary_sha256") == summary_sha256,
        "the audited original performance summary changed",
    )
    require(
        summary.get("raw_sha256") == integrity.get("raw_sha256"),
        "the raw timing evidence does not match the independent integrity audit",
    )
    require(
        summary.get("expected_sha256")
        == integrity.get("expected_sha256")
        == manifest["expected_sha256"],
        "the frozen correctness/workload fixture changed",
    )
    require(integrity.get("cases") == len(cases), "the integrity case denominator changed")
    require(
        integrity.get("cases_per_cohort") == suite.CASES_PER_COHORT,
        "the independently held-back case denominator changed",
    )
    require(
        integrity.get("paired_raw_rows") == len(cases) * len(modules) * suite.TRIALS,
        "paired baseline/candidate/trial data are missing",
    )
    archives = integrity.get("archives")
    require(isinstance(archives, dict), "complete raw and summary evidence archives are missing")
    for archive_name, digest in (
        ("raw", integrity["raw_sha256"]),
        ("summary", summary_sha256),
    ):
        archive = archives.get(archive_name)
        require(isinstance(archive, dict), f"missing complete {archive_name} archive")
        require(
            archive.get("restored_sha256") == digest,
            f"complete {archive_name} archive does not restore the audited evidence",
        )

    case_by_id = {case["id"]: case for case in cases}
    require(len(case_by_id) == len(cases), "duplicate frozen workload identifier")
    regressions = check_strict_regressions(summary.get("case_results"), summary.get("regressions"))
    require(
        len(summary["case_results"]) == len(cases) * len(candidates),
        "a candidate or case was excluded from the benchmark results",
    )
    results_seen: set[tuple[str, str]] = set()
    for row in summary["case_results"]:
        key = (row["case"], row["candidate"])
        case = case_by_id.get(row["case"])
        require(case is not None, f"unfrozen benchmark result: {row['case']}")
        require(row["candidate"] in candidates, f"unknown candidate: {row['candidate']}")
        require(row.get("cohort") == case["cohort"], f"changed cohort: {row['case']}")
        require(row.get("category") == case["category"], f"changed workload: {row['case']}")
        require(row.get("weight") == case["weight"], f"changed case weight: {row['case']}")
        for field in ("ci95_low", "ci95_high"):
            require(positive_number(row.get(field)), f"invalid confidence interval: {key}")
        require(row["ci95_low"] <= row["ci95_high"], f"inverted confidence interval: {key}")
        require(
            row.get("statistically_faster") is (row["ci95_low"] > 1.0),
            f"changed reliably-faster flag: {key}",
        )
        results_seen.add(key)
    require(
        len(results_seen) == len(cases) * len(candidates),
        "a frozen case or independent candidate is missing",
    )
    require(
        integrity.get("candidate_case_results") == len(results_seen),
        "the integrity audit and candidate-case denominator disagree",
    )
    require(
        len(regressions) == integrity.get("strict_regressions"),
        "the independent raw audit and recorded slowdown denominator disagree",
    )

    rankings = summary.get("rankings")
    require(isinstance(rankings, list), "candidate rankings are missing")
    require(rankings == integrity.get("rankings"), "independently audited rankings changed")
    indexed_rankings: dict[tuple[str, str], dict] = {}
    for row in rankings:
        require(isinstance(row, dict), "invalid candidate ranking")
        key = (row.get("cohort"), row.get("candidate"))
        require(key not in indexed_rankings, f"duplicate ranking: {key}")
        indexed_rankings[key] = row
    require(
        set(indexed_rankings)
        == {(cohort, candidate) for cohort in (*COHORTS, "all") for candidate in candidates},
        "a whole-cohort candidate ranking is missing",
    )

    rows = [
        enriched(row, case_by_id[case_id])
        for (case_id, _candidate), row in sorted(
            regressions.items(), key=lambda item: (item[1]["cohort"], item[1]["candidate"], item[0][0])
        )
    ]
    slowdown_counts = collections.Counter((row["cohort"], row["candidate"]) for row in rows)
    for cohort in (*COHORTS, "all"):
        for candidate in candidates:
            expected_count = (
                sum(slowdown_counts[item, candidate] for item in COHORTS)
                if cohort == "all"
                else slowdown_counts[cohort, candidate]
            )
            require(
                indexed_rankings[cohort, candidate]["regressions_gt_20pct"] == expected_count,
                f"whole-cohort slowdown ranking hides measured rows: {(cohort, candidate)}",
            )

    zig_holdout = [
        row for row in rows if row["cohort"] == "holdout" and row["candidate"] == ZIG
    ]
    require(
        len(zig_holdout) == indexed_rankings["holdout", ZIG]["regressions_gt_20pct"],
        "a held-back Zig slowdown was omitted",
    )
    groups = {
        field: grouped(zig_holdout, field)
        for field in ("category", "api", "lifecycle", "input_kind")
    }
    sort_ranking = lambda row: (-row["geomean_speedup"], row["candidate"])
    return {
        "schema": SCHEMA,
        "python": integrity["python"],
        "expected_sha256": manifest["expected_sha256"],
        "raw_sha256": integrity["raw_sha256"],
        "summary_sha256": summary_sha256,
        "integrity_sha256": integrity_sha256,
        "cases": len(cases),
        "cases_per_cohort": suite.CASES_PER_COHORT,
        "candidate_count": len(candidates),
        "candidate_case_results": len(results_seen),
        "total_regressions": len(rows),
        "regression_speedup_threshold": REGRESSION_SPEEDUP_THRESHOLD,
        "regression_boundary_checks": boundary["boundary_examples"],
        "rejected_self_test_corruptions": boundary["rejected_corruptions"],
        "holdout_rankings": sorted(
            (indexed_rankings["holdout", candidate] for candidate in candidates),
            key=sort_ranking,
        ),
        "all_rankings": sorted(
            (indexed_rankings["all", candidate] for candidate in candidates),
            key=sort_ranking,
        ),
        "zig_total_regressions": indexed_rankings["all", ZIG]["regressions_gt_20pct"],
        "zig_holdout_regressions": zig_holdout,
        "zig_holdout_groups": groups,
        "regressions": rows,
        "failed": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--integrity", type=Path)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    if args.self_test:
        require(
            all(value is None for value in (args.integrity, args.summary, args.output, args.json_output)),
            "self-test does not accept or mutate evidence paths",
        )
        print(json.dumps(self_test(), sort_keys=True))
        return
    require(
        all(value is not None for value in (args.integrity, args.summary, args.output, args.json_output)),
        "--integrity, --summary, --output and --json-output are all required",
    )
    document = audit(args.integrity, args.summary)
    archive = archive_json(document, args.json_output)
    report = markdown_report(document, archive)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(
        json.dumps(
            {
                "schema": SCHEMA,
                "cases": document["cases"],
                "cases_per_cohort": document["cases_per_cohort"],
                "candidate_case_results": document["candidate_case_results"],
                "strict_regressions": document["total_regressions"],
                "zig_holdout_regressions": len(document["zig_holdout_regressions"]),
                "zig_all_regressions": document["zig_total_regressions"],
                "regression_speedup_threshold": REGRESSION_SPEEDUP_THRESHOLD,
                "regression_boundary_checks": document["regression_boundary_checks"],
                "rejected_self_test_corruptions": document["rejected_self_test_corruptions"],
                "archive": archive,
                "report": display_path(args.output),
                "failed": 0,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
