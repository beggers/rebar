#!/usr/bin/env python3
"""Generate a readable all-cases performance report from the committed summary."""

import argparse
import json
from pathlib import Path


def short(value):
    return value.rsplit(".", 1)[-1].replace("_candidate", "")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--title", required=True)
    args = parser.parse_args()
    data = json.loads(Path(args.summary).read_text(encoding="utf-8"))
    lines = [f"# {args.title}", "", f"Raw SHA-256: `{data['raw_sha256']}`. Rows: {data['rows']}. All {len(data['case_results'])} candidate/case results and all {len(data['regressions'])} regressions are shown below.", "", "## Rankings", "", "| Cohort | Candidate | Geomean | 95% CI | Faster cases | >20% regressions |", "| --- | --- | ---: | ---: | ---: | ---: |"]
    for row in data["rankings"]:
        lines.append(f"| {row['cohort']} | {short(row['candidate'])} | {row['geomean_speedup']:.4f}x | {row['ci95_low']:.4f}–{row['ci95_high']:.4f}x | {row['statistically_faster_cases']}/{row['cases']} | {row['regressions_gt_20pct']} |")
    lines.extend(["", "## Every case", "", "`REGRESSION` means speedup below 0.8; `FASTER` means the lower confidence bound exceeds 1. Memory is median traced-peak candidate/baseline ratio.", "", "| Cohort | Case | Candidate | Speedup | 95% CI | Memory | Result |", "| --- | --- | --- | ---: | ---: | ---: | --- |"])
    for row in data["case_results"]:
        result = "REGRESSION" if row["regression_gt_20pct"] else "FASTER" if row["statistically_faster"] else "—"
        lines.append(f"| {row['cohort']} | `{row['case']}` | {short(row['candidate'])} | {row['speedup']:.4f}x | {row['ci95_low']:.4f}–{row['ci95_high']:.4f}x | {row['peak_traced_ratio']:.2f}x | {result} |")
    lines.extend(["", "## Regression explanation", "", "All listed regressions are retained. The AST family pays Python generator/state-allocation and per-position scanning costs. The native VM improves cold compilation but pays state cloning, Python result construction, and wrapper/template costs. Rust pays per-call FFI conversion plus eager continuation allocation. Long misses amplify scanning/boundary work; `findall`, `finditer`, `split`, and substitutions amplify repeated match/result construction. These mechanisms explain the >20% losses shown above; the raw RSS/HWM and traced peaks remain available for inspection.", ""])
    Path(args.output).write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
