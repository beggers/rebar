#!/usr/bin/env python3
"""Generate a compact, plain-language Zig coverage and speed summary from raw results."""

import argparse
import json
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def ranking(path, cohort="holdout"):
    return next(item for item in load(path)["rankings"] if item["cohort"] == cohort)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--p0-initial", required=True)
    parser.add_argument("--p0-current", required=True)
    parser.add_argument("--performance-initial", required=True)
    parser.add_argument("--performance-current", required=True)
    parser.add_argument("--upstream", required=True)
    parser.add_argument("--initial", required=True)
    parser.add_argument("--batched", required=True)
    parser.add_argument("--output-build", required=True)
    parser.add_argument("--iterator", required=True)
    parser.add_argument("--final", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    p0_initial = load(args.p0_initial)
    p0_current = load(args.p0_current)
    perf_initial = load(args.performance_initial)
    perf_current = load(args.performance_current)
    upstream = load(args.upstream)
    coverage = (
        ("Initial compatibility check", p0_initial["passed"], p0_initial["cases"]),
        ("Current compatibility check", p0_current["passed"], p0_current["cases"]),
        ("Initial broader task check", perf_initial["checks"] - perf_initial["failed"], perf_initial["checks"]),
        ("Current broader task check", perf_current["checks"] - perf_current["failed"], perf_current["checks"]),
        ("Official CPython re tests", upstream["passed"], upstream["methods"] - upstream["skipped"]),
    )
    short = (
        ("Initial public API", ranking(args.initial)["geomean_speedup"]),
        ("Batch matching", ranking(args.batched)["geomean_speedup"]),
        ("Build results natively", ranking(args.output_build)["geomean_speedup"]),
        ("Batch iterators", ranking(args.iterator)["geomean_speedup"]),
    )
    final = ranking(args.final)

    width = 1000
    height = 570
    bar_left = 340
    bar_width = 480
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Zig compatibility and speed progress">',
        '<rect width="100%" height="100%" fill="#fff"/>',
        '<style>text{font-family:system-ui,-apple-system,Segoe UI,sans-serif;fill:#172033}.title{font-size:23px;font-weight:700}.sub{font-size:13px;fill:#536179}.section{font-size:15px;font-weight:700}.label{font-size:13px}.value{font-size:12px;text-anchor:end;font-weight:700}.note{font-size:12px;fill:#536179}.track{fill:#e9edf3}</style>',
        '<text x="26" y="38" class="title">Zig: compatibility and speed so far</text>',
        '<text x="26" y="61" class="sub">The engine is written from scratch. It is improving, but it is not yet a drop-in replacement for Python re.</text>',
        '<text x="26" y="99" class="section">How much works?</text>',
    ]
    for index, (label, passed, total) in enumerate(coverage):
        y = 120 + index * 35
        value = round(bar_width * passed / total)
        color = "#238b64" if passed == total else "#d48a2b" if passed * 2 >= total else "#c84c4c"
        lines.extend((f'<text x="26" y="{y+15}" class="label">{label}</text>', f'<rect x="{bar_left}" y="{y}" width="{bar_width}" height="22" rx="3" class="track"/>', f'<rect x="{bar_left}" y="{y}" width="{value}" height="22" rx="3" fill="{color}"/>', f'<text x="{width-28}" y="{y+15}" class="value">{passed:,}/{total:,} passed</text>'))
    lines.extend(('<text x="26" y="326" class="section">How fast is the public API?</text>', '<text x="26" y="347" class="note">Short tuning check: the same 67 supported holdout tasks, five paired trials, up to eight calls each. 1× is Python re.</text>'))
    for index, (label, speed) in enumerate(short):
        y = 366 + index * 31
        value = min(bar_width, round(bar_width * speed))
        lines.extend((f'<text x="26" y="{y+14}" class="label">{label}</text>', f'<rect x="{bar_left}" y="{y}" width="{bar_width}" height="20" rx="3" class="track"/>', f'<rect x="{bar_left}" y="{y}" width="{value}" height="20" rx="3" fill="#477db7"/>', f'<text x="{width-28}" y="{y+14}" class="value">{speed:.3f}× of Python re</text>'))
    lines.extend((f'<text x="26" y="522" class="section">Full holdout check: {final["geomean_speedup"]:.3f}× ({final["ci95_low"]:.3f}–{final["ci95_high"]:.3f}×)</text>', f'<text x="26" y="544" class="note">13 paired trials at full call counts · {final["qualified"]}/{final["total"]} tasks supported · {final["faster_cases"]} clearly faster · {final["slowdowns_gt_20pct"]} more than 20% slower.</text>', '</svg>\n'))
    Path(args.output).write_text("".join(lines), encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
