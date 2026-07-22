#!/usr/bin/env python3
"""Regenerate readable Zig speed, memory, and win/loss charts from committed results."""

from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

from tools.zig_perf_v5_pilot import chart, memory_chart, regression_chart


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    parser.add_argument("--speed-chart", required=True)
    parser.add_argument("--memory-chart", required=True)
    parser.add_argument("--regression-chart", required=True)
    args = parser.parse_args()
    summary = json.loads(Path(args.input).read_text(encoding="utf-8"))
    results = summary["case_results"]
    for family in summary["families"]:
        members = [
            value for value in results
            if value["category"] == family["category"]
            and (family["cohort"] == "all" or value["cohort"] == family["cohort"])
        ]
        if len(members) != family["cases"]:
            raise RuntimeError(f"family count drift: {family['cohort']} {family['category']}")
        logs = [math.log((value["zig_peak_bytes"] + 1) / (value["baseline_peak_bytes"] + 1)) for value in members]
        family["memory_ratio"] = math.exp(statistics.fmean(logs))
        family["baseline_peak_bytes"] = round(statistics.median(value["baseline_peak_bytes"] for value in members))
        family["zig_peak_bytes"] = round(statistics.median(value["zig_peak_bytes"] for value in members))
    if args.output:
        Path(args.output).write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    chart(summary, args.speed_chart)
    memory_chart(summary, args.memory_chart)
    regression_chart(summary, args.regression_chart)
    print(json.dumps({"schema": summary["schema"], "cases": summary["cases"], "rows": summary["rows"], "charts": [args.speed_chart, args.memory_chart, args.regression_chart]}, sort_keys=True))


if __name__ == "__main__":
    main()
