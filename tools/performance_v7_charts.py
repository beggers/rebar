#!/usr/bin/env python3
"""Generate readable, complete, baseline-relative frozen-v7 evidence charts."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from html import escape
from pathlib import Path

from tools.perf_v7 import frozen
from tools.performance_v6_charts import (
    COLORS,
    NAMES,
    fmt,
    geometric,
    grid,
    overall,
    page,
    rankings,
    save,
    xlog,
)
from tools.rust_merge_v7 import validate_summary


def name(category):
    if category == "Earlier workloads":
        return category
    return category.removeprefix("broader-").replace("-", " ").title()


def ordered(summary):
    return sorted(
        (
            row for row in summary["rankings"]
            if row["cohort"] == "holdout"
        ),
        key=lambda row: row["geomean_speedup"],
        reverse=True,
    )


def groups(summary, *, include_earlier):
    values = defaultdict(list)
    for row in summary["case_results"]:
        if row["cohort"] != "holdout":
            continue
        category = row["category"]
        if not category.startswith("broader-"):
            if not include_earlier:
                continue
            category = "Earlier workloads"
        values[(category, row["candidate"])].append(row)
    categories = sorted(
        {category for category, _candidate in values},
        key=lambda category: (category != "Earlier workloads", category),
    )
    candidates = [row["candidate"] for row in ordered(summary)]
    return values, categories, candidates


def family_speed(summary, destination):
    values, categories, candidates = groups(summary, include_earlier=False)
    row_height = 23
    panel = len(categories) * row_height + 66
    width = 1320
    height = 88 + len(candidates) * panel + 22
    left = 283
    right = 979
    body = page(
        width,
        height,
        "Where each replacement is fast or slow",
        "64 new kinds of work, with 64 unseen examples each. "
        "1× is Python re; farther right is faster.",
    )
    for candidate_index, candidate in enumerate(candidates):
        top = 102 + candidate_index * panel
        bottom = top + 16 + len(categories) * row_height
        color = COLORS[candidate]
        body.extend(
            (
                f'<rect x="15" y="{top - 28}" width="1290" '
                f'height="{panel - 9}" rx="9" fill="#f8fafc" '
                'stroke="#e2e8f0"/>',
                f'<text x="29" y="{top - 8}" class="head">'
                f"{escape(NAMES[candidate])}</text>",
            )
        )
        grid(
            body,
            left,
            right,
            top + 8,
            bottom,
            -3,
            2,
            ((0.001, ".001×"), (0.01, ".01×"), (0.1, ".1×"),
             (1, "1× Python re"), (10, "10×"), (100, "100×")),
        )
        for index, category in enumerate(categories):
            rows = values[(category, candidate)]
            if len(rows) != 64:
                raise RuntimeError(f"the v7 family chart changed a 64-task denominator: {category}")
            point = geometric(row["speedup"] for row in rows)
            low = geometric(row["ci95_low"] for row in rows)
            high = geometric(row["ci95_high"] for row in rows)
            wins = sum(row["statistically_faster"] for row in rows)
            losses = sum(row["regression_gt_20pct"] for row in rows)
            y = top + 24 + index * row_height
            body.extend(
                (
                    f'<text x="28" y="{y + 4}" class="label">'
                    f"{escape(name(category))}</text>",
                    f'<line x1="{xlog(low, left, right - left, -3, 2):.1f}" '
                    f'y1="{y}" x2="{xlog(high, left, right - left, -3, 2):.1f}" '
                    f'y2="{y}" stroke="{color}" stroke-width="3" '
                    'stroke-linecap="round"/>',
                    f'<circle cx="{xlog(point, left, right - left, -3, 2):.1f}" '
                    f'cy="{y}" r="3.5" fill="{color}"/>',
                    f'<text x="998" y="{y + 4}" class="value">{fmt(point)}</text>',
                    f'<text x="1080" y="{y + 4}" class="small">'
                    f"{wins}/64 faster · {losses} slow</text>",
                )
            )
    save(destination, body)


def candidate_speed(summary, candidate, destination):
    values, categories, _candidates = groups(summary, include_earlier=True)
    row_height = 24
    width = 1270
    height = 120 + len(categories) * row_height
    left = 283
    right = 905
    body = page(
        width,
        height,
        f"Where the {NAMES[candidate]} is fast or slow",
        "Every earlier task remains in the first row; the other rows show all "
        "64 new workloads. 1× is Python re.",
    )
    grid(
        body,
        left,
        right,
        99,
        height - 15,
        -2,
        2,
        ((0.01, ".01×"), (0.1, ".1×"), (0.3, ".3×"),
         (1, "1× Python re"), (3, "3×"), (10, "10×"), (100, "100×")),
    )
    for index, category in enumerate(categories):
        rows = values[(category, candidate)]
        if not rows:
            raise RuntimeError(f"the candidate chart omitted {category}")
        point = geometric(row["speedup"] for row in rows)
        low = geometric(row["ci95_low"] for row in rows)
        high = geometric(row["ci95_high"] for row in rows)
        wins = sum(row["statistically_faster"] for row in rows)
        losses = sum(row["regression_gt_20pct"] for row in rows)
        color = "#dc2626" if losses else COLORS[candidate]
        y = 123 + index * row_height
        body.extend(
            (
                f'<text x="24" y="{y + 4}" class="label">'
                f"{escape(name(category))}</text>",
                f'<line x1="{xlog(low, left, right - left, -2, 2):.1f}" '
                f'y1="{y}" x2="{xlog(high, left, right - left, -2, 2):.1f}" '
                f'y2="{y}" stroke="{color}" stroke-width="3" '
                'stroke-linecap="round"/>',
                f'<circle cx="{xlog(point, left, right - left, -2, 2):.1f}" '
                f'cy="{y}" r="3.5" fill="{color}"/>',
                f'<text x="925" y="{y + 4}" class="value">{fmt(point)}</text>',
                f'<text x="1002" y="{y + 4}" class="small">'
                f"{wins}/{len(rows)} faster · {losses} slow</text>",
            )
        )
    save(destination, body)


def memory(summary, destination):
    values, categories, candidates = groups(summary, include_earlier=False)
    row_height = 23
    panel = len(categories) * row_height + 66
    width = 1280
    height = 88 + len(candidates) * panel + 22
    left = 283
    right = 986
    body = page(
        width,
        height,
        "How much temporary Python memory each replacement uses",
        "64 unseen examples per workload. 1× is Python re; farther left "
        "uses less Python-traced memory. Process memory is retained in raw data.",
    )
    for candidate_index, candidate in enumerate(candidates):
        top = 102 + candidate_index * panel
        bottom = top + 16 + len(categories) * row_height
        color = COLORS[candidate]
        body.extend(
            (
                f'<rect x="15" y="{top - 28}" width="1250" '
                f'height="{panel - 9}" rx="9" fill="#f8fafc" '
                'stroke="#e2e8f0"/>',
                f'<text x="29" y="{top - 8}" class="head">'
                f"{escape(NAMES[candidate])}</text>",
            )
        )
        grid(
            body,
            left,
            right,
            top + 8,
            bottom,
            -2,
            4,
            ((0.01, ".01×"), (0.1, ".1×"), (1, "1× Python re"),
             (10, "10×"), (100, "100×"), (1000, "1,000×"),
             (10000, "10,000×")),
        )
        for index, category in enumerate(categories):
            rows = values[(category, candidate)]
            if len(rows) != 64:
                raise RuntimeError(f"the memory chart changed a 64-task denominator: {category}")
            ratio = geometric(max(row["peak_traced_ratio"], 1e-12) for row in rows)
            y = top + 24 + index * row_height
            body.extend(
                (
                    f'<text x="28" y="{y + 4}" class="label">'
                    f"{escape(name(category))}</text>",
                    f'<circle cx="{xlog(ratio, left, right - left, -2, 4):.1f}" '
                    f'cy="{y}" r="3.5" fill="{color}"/>',
                    f'<text x="1006" y="{y + 4}" class="value">{fmt(ratio)}</text>',
                )
            )
    save(destination, body)


def win_loss(summary, destination):
    values, categories, candidates = groups(summary, include_earlier=True)
    row_height = 24
    cell = 251
    width = 1330
    height = 120 + len(categories) * row_height
    left = 293
    body = page(
        width,
        height,
        "Which tasks are clearly faster or more than 20% slower?",
        "1× is Python re; below 0.833× takes over 20% more time. "
        "Every unseen task is counted; green marks wins and red marks slowdowns.",
    )
    for index, candidate in enumerate(candidates):
        body.append(
            f'<text x="{left + index * cell + 7}" y="96" class="head">'
            f"{escape(NAMES[candidate])}</text>"
        )
    for index, category in enumerate(categories):
        y = 107 + index * row_height
        body.append(
            f'<text x="24" y="{y + 15}" class="label">'
            f"{escape(name(category))}</text>"
        )
        for candidate_index, candidate in enumerate(candidates):
            rows = values[(category, candidate)]
            wins = sum(row["statistically_faster"] for row in rows)
            losses = sum(row["regression_gt_20pct"] for row in rows)
            fill = (
                "#b91c1c" if losses
                else "#15803d" if wins > len(rows) / 2
                else "#64748b"
            )
            x = left + candidate_index * cell
            body.extend(
                (
                    f'<rect x="{x}" y="{y}" width="{cell - 7}" '
                    f'height="20" rx="4" fill="{fill}"/>',
                    f'<text x="{x + 7}" y="{y + 14}" class="value" '
                    'style="fill:#fff">'
                    f"{fmt(geometric(row['speedup'] for row in rows))} · "
                    f"{wins}/{len(rows)} faster · {losses} slow</text>",
                )
            )
    save(destination, body)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--prefix", required=True)
    args = parser.parse_args()
    suite, cases, _expected, manifest = frozen()
    summary = json.loads(Path(args.summary).read_text(encoding="utf-8"))
    validate_summary(
        summary,
        label="complete frozen v7 chart measurements",
        suite=suite,
        cases=cases,
        manifest=manifest,
        candidates=tuple(suite.MODULES[1:]),
    )
    destination = Path(args.prefix)
    destination.parent.mkdir(parents=True, exist_ok=True)
    prefix = str(destination)
    overall(summary, prefix + "-overall.svg")
    candidate_speed(summary, "candidates.rust_candidate", prefix + "-rust-speed.svg")
    candidate_speed(summary, "candidates.zig_candidate", prefix + "-zig-speed.svg")
    family_speed(summary, prefix + "-family-speed.svg")
    memory(summary, prefix + "-memory.svg")
    win_loss(summary, prefix + "-win-loss.svg")
    rankings(summary, prefix + "-rankings.svg")


if __name__ == "__main__":
    main()
