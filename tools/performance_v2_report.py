#!/usr/bin/env python3
"""Generate a plain-language, all-results performance report."""

import argparse
import json
from pathlib import Path

NAMES = {"candidates.ast_candidate": "Python engine", "candidates.vm_candidate": "Native C engine", "candidates.rust_candidate": "Rust engine", "rebar": "rebar"}


def name(value):
    return NAMES.get(value, value.rsplit(".", 1)[-1].replace("_candidate", ""))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--title", required=True)
    args = parser.parse_args()
    data = json.loads(Path(args.summary).read_text(encoding="utf-8"))
    holdout = sorted((row for row in data["rankings"] if row["cohort"] == "holdout"), key=lambda row: row["geomean_speedup"], reverse=True)
    lines = [f"# {args.title}", "", f"All {data['rows']} raw timing rows, {len(data['case_results'])} engine/task results, and {len(data['regressions'])} large slowdowns are retained. Raw SHA-256: `{data['raw_sha256']}`.", "", "## At a glance", "", "The holdout tasks were kept separate from tuning. **1× means the same speed as Python `re`; higher is faster.** A result is clearly faster only when its measured range stays above 1×. A large slowdown means more than 20% slower.", "", "| Engine | Overall speed | Measured range | Clearly faster | Large slowdowns |", "| --- | ---: | ---: | ---: | ---: |"]
    for row in holdout:
        lines.append(f"| {name(row['candidate'])} | **{row['geomean_speedup']:.4f}×** | {row['ci95_low']:.4f}–{row['ci95_high']:.4f}× | {row['statistically_faster_cases']}/{row['cases']} | {row['regressions_gt_20pct']}/{row['cases']} |")
    lines.extend(["", "## Overall results", "", "| Task set | Engine | Overall speed | Measured range | Clearly faster | Large slowdowns |", "| --- | --- | ---: | ---: | ---: | ---: |"])
    cohorts = {"calibration": "Practice", "holdout": "Holdout", "all": "All"}
    for row in data["rankings"]:
        lines.append(f"| {cohorts[row['cohort']]} | {name(row['candidate'])} | {row['geomean_speedup']:.4f}× | {row['ci95_low']:.4f}–{row['ci95_high']:.4f}× | {row['statistically_faster_cases']}/{row['cases']} | {row['regressions_gt_20pct']} |")
    lines.extend(["", "## Every task", "", "`FASTER` means the measured range stays above 1×. `SLOWER` means more than 20% slower. Memory compares median traced Python memory with Python `re`.", "", "| Task set | Task | Engine | Speed | Measured range | Memory | Result |", "| --- | --- | --- | ---: | ---: | ---: | --- |"])
    for row in data["case_results"]:
        result = "SLOWER" if row["regression_gt_20pct"] else ("FASTER" if row["statistically_faster"] else "—")
        lines.append(f"| {cohorts[row['cohort']]} | `{row['case']}` | {name(row['candidate'])} | {row['speedup']:.4f}× | {row['ci95_low']:.4f}–{row['ci95_high']:.4f}× | {row['peak_traced_ratio']:.2f}× | {result} |")
    lines.extend(["", "## Large slowdowns", ""])
    if not data["regressions"]:
        lines.append("None were measured.")
    else:
        for candidate in sorted({row["candidate"] for row in data["regressions"]}):
            values = [row for row in data["regressions"] if row["candidate"] == candidate]
            cases = ", ".join(f"`{row['case']}` ({row['speedup']:.3f}×)" for row in values)
            lines.append(f"- {name(candidate)}: {cases}.")
        native = [row for row in data["regressions"] if row["candidate"] == "candidates.vm_candidate"]
        lines.extend(["", "The Python engine performs matching work in Python, and the Rust engine repeatedly prepares data and crosses the Python/Rust boundary; both costs dominate short tasks. Native-C losses expose specific boundary and general-path costs:"])
        if any("findall.tokens" in row["case"] or "unicode.words" in row["case"] for row in native):
            lines.append("- Repeated text/Unicode matching needs character-category and word-boundary checks that cannot use the simplest one-pass scan.")
        if any("empty.finditer" in row["case"] or "atomic.search" in row["case"] for row in native):
            lines.append("- Empty matches and controlled branches use the general backtracking/iterator path and construct more match state.")
        if any("escape." in row["case"] for row in native):
            lines.append("- Escaping currently loops over every character in Python, explaining both the time and extra traced-memory cost.")
        if any("scanner.search" in row["case"] for row in native):
            lines.append("- Scanning repeatedly returns through a small Python wrapper, so per-match boundary and object costs accumulate.")
        if any("match.surface" in row["case"] for row in native):
            lines.append("- Reading many groups and expanding a template makes several Python/C and Python-template calls for one match.")
        if any("real." in row["case"] for row in native):
            lines.append("- Everyday log, address, path, comment, markup, quote, and comma-separated-field tasks combine repeated classes, captures, or lookarounds; they take the general native backtracking path instead of its compact single-pass path.")
        if any("branch." in row["case"] for row in native):
            lines.append("- Searches across many alternative words still test the remaining branches when a possible prefix survives; the native one/two-character start filter removes impossible positions but does not build a full shared-prefix trie.")
        if any("repeat.nested" in row["case"] or "block.dotall" in row["case"] or "pattern.verbose" in row["case"] for row in native):
            lines.append("- Structured repeated paths, multi-line blocks, and readable formatted fields require general repeat/capture backtracking, which carries more state than the simple literal and single-character fast paths.")
        if any("look.negative-" in row["case"] for row in native):
            lines.append("- Excluded-prefix and tagged-word searches evaluate a negative lookaround for each possible match, so the native executor repeats assertion work while scanning.")
        if any("bytes.scan" in row["case"] or "window.scanner" in row["case"] for row in native):
            lines.append("- Byte and windowed scanning also return through the per-match Python scanner wrapper, so repeated boundary/object costs dominate these short inputs.")
        if any("zero.boundary" in row["case"] or "split.limited" in row["case"] for row in native):
            lines.append("- Word/separator-position iteration and limited mixed-separator splits repeatedly use the general iterator or whitespace-backtracking path; each small match pays state and result-construction costs.")
        lines.extend(["", "No loss is removed from the denominator or hidden from the charts."])
    lines.append("")
    Path(args.output).write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
