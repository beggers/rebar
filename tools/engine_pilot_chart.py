#!/usr/bin/env python3
"""Render a plain-language before/after chart from correctness-gated engine pilots."""

import argparse
import html
import json
import math
import statistics
from pathlib import Path


def medians(data, module):
    rows = data["rows"]
    cases = sorted({row["case"] for row in rows})
    return {case: statistics.median(row["per_operation_ns"] for row in rows if row["case"] == case and row["module"] == module) for case in cases}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    parser.add_argument("--module", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    before = json.loads(Path(args.before).read_text(encoding="utf-8"))
    after = json.loads(Path(args.after).read_text(encoding="utf-8"))
    old = medians(before, args.module)
    new = medians(after, args.module)
    baseline = medians(after, "re")
    if set(old) != set(new) or set(new) != set(baseline):
        raise ValueError("pilot cases differ")
    cases = sorted(new, key=lambda case: old[case] / new[case], reverse=True)
    improvement = math.exp(statistics.fmean(math.log(old[case] / new[case]) for case in cases))
    relative = math.exp(statistics.fmean(math.log(baseline[case] / new[case]) for case in cases))
    width = 1040
    row_height = 22
    top = 142
    height = top + len(cases) * row_height + 38
    center = 785
    half = 185
    max_log = max(1.0, max(abs(math.log2(old[case] / new[case])) for case in cases))
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:system-ui,-apple-system,Segoe UI,sans-serif;fill:#172033}.title{font-size:23px;font-weight:700}.sub{font-size:14px;fill:#526079}.head{font-size:12px;font-weight:700;fill:#41506a}.label{font-size:12px}.num{font-size:12px;text-anchor:end;font-variant-numeric:tabular-nums}.gain{font-size:12px;font-weight:700;text-anchor:end;font-variant-numeric:tabular-nums}.grid{stroke:#d7deea;stroke-width:1}.axis{stroke:#8290a6;stroke-width:1.2}</style>',
        f'<text x="26" y="36" class="title">{html.escape(args.module.rsplit(".", 1)[-1].replace("_candidate", "").title())} engine: before and after</text>',
        f'<text x="26" y="60" class="sub">{len(cases)} holdout tasks · lower time is better · {improvement:.2f}× faster overall than before · {relative:.3f}× of Python re</text>',
        '<text x="26" y="88" class="sub">Green bars show an improvement; red bars show a slowdown. Every timed result was checked for correctness.</text>',
        '<text x="26" y="122" class="head">TASK</text><text x="516" y="122" class="head" text-anchor="end">BEFORE (µs)</text><text x="624" y="122" class="head" text-anchor="end">AFTER (µs)</text><text x="770" y="122" class="head" text-anchor="end">CHANGE</text><text x="785" y="122" class="head">SLOWER ← · → FASTER</text>',
        f'<line x1="{center}" y1="{top - 8}" x2="{center}" y2="{height - 20}" class="axis"/>',
    ]
    for index, case in enumerate(cases):
        y = top + index * row_height
        ratio = old[case] / new[case]
        delta = math.log2(ratio) / max_log * half
        x = center if delta >= 0 else center + delta
        color = "#238b64" if delta >= 0 else "#c84c4c"
        label = case.removeprefix("hold.").replace(".", " / ").replace("-", " ")
        if index % 2 == 0:
            lines.append(f'<rect x="18" y="{y - 15}" width="{width - 36}" height="{row_height}" fill="#f5f7fb"/>')
        lines.extend((
            f'<line x1="18" y1="{y + 7}" x2="{width - 18}" y2="{y + 7}" class="grid"/>',
            f'<text x="26" y="{y}" class="label">{html.escape(label)}</text>',
            f'<text x="516" y="{y}" class="num">{old[case] / 1000:.2f}</text>',
            f'<text x="624" y="{y}" class="num">{new[case] / 1000:.2f}</text>',
            f'<text x="770" y="{y}" class="gain" fill="{color}">{ratio:.2f}×</text>',
            f'<rect x="{x:.1f}" y="{y - 10}" width="{abs(delta):.1f}" height="11" rx="2" fill="{color}"/>',
        ))
    lines.append("</svg>\n")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("".join(lines), encoding="utf-8")
    print(json.dumps({"cases": len(cases), "module": args.module, "overall_improvement": improvement, "relative_to_re": relative, "output": str(output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
