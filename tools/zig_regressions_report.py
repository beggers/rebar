#!/usr/bin/env python3
"""List and explain every large Zig slowdown in the expanded holdout."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from tools.performance_v5_report import CAUSES


EXTRA = {
    "search-hit": "very short successful searches are dominated by the Python/native call and match-object setup",
    "search-miss": "very short misses still pay the Python/native call cost",
    "empty": "many empty results require safe progress and repeated iterator/result construction",
    "real-email": "several repeated character classes and returned values amplify collection work",
    "real-csv": "quoted-field lookahead requires repeated scans and backtracking",
    "branch-prefix": "controlled alternatives add branch and state work to a short search",
    "branch-miss": "an absent choice requires checking many alternatives at every plausible start",
    "block-dotall": "lazy multi-line matching repeatedly retries the closing text",
    "pattern-verbose": "short verbose expressions expose capture and native-boundary setup",
    "look-negative-ahead": "negative lookahead and word-boundary checks repeat across the input",
    "literal-replace": "a very short replacement is dominated by argument handling and result construction",
    "match-miss": "very short anchored misses are dominated by call/setup cost",
    "expanded-match-surface": "these generated inputs never match: a digit interrupts the leading text run before the dash, so the matcher retries the run at many starts; the result-building path is not reached",
}


def cause(category):
    family = category.removeprefix("expanded-").removeprefix("large-")
    return EXTRA.get(category, EXTRA.get(family, CAUSES.get(family, "matching, collection, or native-boundary work dominates this task")))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    data = json.loads(Path(args.summary).read_text(encoding="utf-8"))
    rows = [value for value in data["case_results"] if value["cohort"] == "holdout" and value["regression_gt_20pct"]]
    groups = defaultdict(list)
    for row in rows:
        groups[row["category"]].append(row)
    if not rows:
        lines = [
            "# Every large Zig slowdown",
            "",
            "The final expanded holdout has **0** tasks below 0.8×. There are no large slowdowns to explain or omit.",
            "",
        ]
        Path(args.output).write_text("\n".join(lines), encoding="utf-8")
        print(f"wrote {args.output} (0 slowdowns)")
        return
    lines = [
        "# Every large Zig slowdown",
        "",
        f"The final expanded holdout has **{len(rows):,}** tasks below 0.8×. Every task is listed here with its measured range, median time, and the workload-specific reason; no result is omitted or reclassified.",
        "",
        "## Causes by kind of task",
        "",
    ]
    for category, members in sorted(groups.items(), key=lambda item: (-len(item[1]), item[0])):
        speeds = [row["speedup"] for row in members]
        lines.append(f"- **{category.replace('-', ' ')} ({len(members)}):** {cause(category)}. Observed range: {min(speeds):.3f}–{max(speeds):.3f}×.")
    lines.extend((
        "",
        "## Every task",
        "",
        "| Task | Kind of task | Speed | 95% range | Python re | Zig |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ))
    for row in sorted(rows, key=lambda item: (item["category"], item["case"])):
        lines.append(f"| `{row['case']}` | {row['category'].replace('-', ' ')} | {row['speedup']:.3f}× | {row['ci95_low']:.3f}–{row['ci95_high']:.3f}× | {row['baseline_ns']:.0f} ns | {row['zig_ns']:.0f} ns |")
    Path(args.output).write_text("\n".join([*lines, ""]), encoding="utf-8")
    print(f"wrote {args.output} ({len(rows)} slowdowns)")


if __name__ == "__main__":
    main()
