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
        lines.extend(["", "The Python engine performs matching work in Python, and the Rust engine repeatedly prepares data and crosses the Python/Rust boundary; both costs dominate short tasks. Native-C slowdowns, if present, remain explicit targets for profiling. No loss is removed from the denominator or hidden from the charts."])
    lines.append("")
    Path(args.output).write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
