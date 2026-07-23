#!/usr/bin/env python3
"""Report the broader performance result and every Zig holdout slowdown."""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path


NAMES = {
    "candidates.ast_candidate": "Python engine",
    "candidates.vm_candidate": "Native C engine",
    "candidates.rust_candidate": "Rust engine",
    "candidates.zig_candidate": "Zig / rebar",
}
CAUSES = {
    "deeper-file-names": "case-insensitive alternatives, filename-boundary checks, and repeated suffix choices keep the general matcher busy",
    "deeper-shared-prefix-alternatives": "sixteen words share the same opening letters, so the general matcher repeatedly retries alternatives, especially with case-insensitive matching",
    "deeper-dense-literal-findall": "hundreds of short literal results make repeated matching and Python string/list construction dominate",
    "deeper-unicode-word-lines": "line starts, Unicode word checks, apostrophe/hyphen repeats, and two captures are repeated for every line",
    "deeper-money-units": "case-insensitive units, currency/number alternatives, and both boundary checks add repeated branch and backtracking work",
    "expanded-backreference": "restoring captures and comparing previously matched text adds work on some inputs",
    "expanded-branch-alternatives": "many alternatives add repeated branch checks on a small number of inputs",
    "expanded-ip-version": "these six/seven-character version strings return four captures; at this size, building the result and crossing the Python/native boundary costs more than the match itself",
}


def geometric(values):
    values = list(values)
    return math.exp(sum(map(math.log, values)) / len(values))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    data = json.loads(Path(args.summary).read_text(encoding="utf-8"))
    rankings = sorted(data["rankings"], key=lambda row: (("calibration", "holdout", "all").index(row["cohort"]), -row["geomean_speedup"]))
    holdout = [row for row in data["case_results"] if row["cohort"] == "holdout"]
    zig = [row for row in holdout if row["candidate"] == "candidates.zig_candidate"]
    losses = [row for row in zig if row["regression_gt_20pct"]]
    grouped = defaultdict(list)
    for row in losses:
        grouped[row["category"]].append(row)
    families = defaultdict(list)
    for row in holdout:
        families[(row["category"], row["candidate"])].append(row)
    categories = sorted({key[0] for key in families})
    candidates = [row["candidate"] for row in rankings if row["cohort"] == "holdout"]

    lines = [
        "# Broader performance result",
        "",
        f"This run retains **{data['rows']:,}** paired timing rows, all **{len(data['case_results']):,}** engine/task results, and all **{len(data['regressions']):,}** large slowdowns across practice and holdout. Raw SHA-256: `{data['raw_sha256']}`.",
        "",
        "## Overall results",
        "",
        "| Test set | Engine | Overall speed | 95% range | Clearly faster | Large slowdowns |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in rankings:
        lines.append(f"| {row['cohort']} | {NAMES[row['candidate']]} | {row['geomean_speedup']:.4f}× | {row['ci95_low']:.4f}–{row['ci95_high']:.4f}× | {row['statistically_faster_cases']:,}/{row['cases']:,} | {row['regressions_gt_20pct']:,} |")
    lines.extend((
        "",
        "## Every Zig / rebar holdout slowdown",
        "",
        f"There are **{len(losses):,}** holdout tasks below 0.8×. Every task is listed with its stable ID and measured range; no slowdown is removed or reclassified.",
        "",
        "### Why they are slower",
        "",
    ))
    for category, rows in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])):
        speeds = [row["speedup"] for row in rows]
        lines.append(f"- **{category.removeprefix('deeper-').removeprefix('expanded-').replace('-', ' ')} ({len(rows)}):** {CAUSES.get(category, 'matching, result construction, or the Python/native boundary dominates this task')}. Observed range: {min(speeds):.3f}–{max(speeds):.3f}×.")
    lines.extend(("", "### Every slower task", "", "| Task | Kind of task | Speed | 95% range | Memory |", "| --- | --- | ---: | ---: | ---: |"))
    for row in sorted(losses, key=lambda item: (item["category"], item["case"])):
        lines.append(f"| `{row['case']}` | {row['category'].replace('-', ' ')} | {row['speedup']:.3f}× | {row['ci95_low']:.3f}–{row['ci95_high']:.3f}× | {row['peak_traced_ratio']:.2f}× |")
    lines.extend(("", "## All holdout workload families", "", "Every family and engine is shown. `faster` counts tasks whose measured range is entirely above 1×; `slow` counts tasks below 0.8×.", "", "| Workload family | Engine | Speed | Memory | Faster | Slow |", "| --- | --- | ---: | ---: | ---: | ---: |"))
    for category in categories:
        for candidate in candidates:
            rows = families[(category, candidate)]
            lines.append(f"| {category.replace('-', ' ')} | {NAMES[candidate]} | {geometric(row['speedup'] for row in rows):.3f}× | {geometric(max(row['peak_traced_ratio'], 1e-12) for row in rows):.2f}× | {sum(row['statistically_faster'] for row in rows)}/{len(rows)} | {sum(row['regression_gt_20pct'] for row in rows)} |")
    lines.extend(("", "The compressed summary contains every individual practice/holdout result and every candidate slowdown; the compressed raw file contains all paired rows, order, operation count, correctness digest, and memory observations.", ""))
    Path(args.output).write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {args.output} ({len(losses)} Zig holdout slowdowns; {len(categories)} families)")


if __name__ == "__main__":
    main()
