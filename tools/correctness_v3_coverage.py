#!/usr/bin/env python3
"""Generate a compact, readable chart for the large correctness holdout."""

import argparse
import json
from pathlib import Path


NAMES = {
    "parent": "Earlier frozen cases",
    "deep-text": "Deep text patterns",
    "deep-bytes": "Deep bytes and buffers",
    "real-text": "Everyday text patterns",
    "real-bytes": "Everyday bytes patterns",
    "scanner": "Scanner sequences and mutation",
    "properties": "Cross-API properties",
    "invalid-pattern": "Invalid patterns",
    "invalid-template": "Invalid replacements",
}
MODULES = {"re": "Python re (self-check)", "rebar": "Native C / rebar", "candidates.ast_candidate": "Python engine", "candidates.rust_candidate": "Rust engine"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="oracle/v3/manifest.json")
    parser.add_argument("--result", action="append", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    results = [json.loads(Path(value).read_text(encoding="utf-8")) for value in args.result]
    families = [(name, manifest["families"][name]) for name in NAMES]
    max_cases = max(value for _, value in families)
    width = 1000
    top = 126
    row = 31
    status_top = top + len(families) * row + 47
    height = status_top + len(results) * 34 + 42
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Large correctness holdout coverage and results">',
        '<rect width="100%" height="100%" fill="#fff"/>',
        '<style>text{font-family:system-ui,-apple-system,Segoe UI,sans-serif;fill:#172033}.title{font-size:23px;font-weight:700}.sub{font-size:13px;fill:#536179}.section{font-size:15px;font-weight:700}.label{font-size:13px}.value{font-size:12px;text-anchor:end;font-weight:700}.note{font-size:12px;fill:#536179}.track{fill:#e8edf4}</style>',
        '<text x="26" y="38" class="title">Large Python re correctness holdout</text>',
        f'<text x="26" y="61" class="sub">{manifest["cases"]:,} total cases · {manifest["cohorts"]["holdout"]:,} new holdout cases · {manifest["mapped_obligations"]}/{manifest["obligations"]} obligations mapped · CPython {manifest["python"]}</text>',
        '<text x="26" y="98" class="section">What is covered?</text>',
    ]
    for index, (name, count) in enumerate(families):
        y = top + index * row
        bar = round(500 * count / max_cases)
        color = "#8d99a8" if name == "parent" else "#477db7"
        lines.extend((f'<text x="26" y="{y+15}" class="label">{NAMES[name]}</text>', f'<rect x="342" y="{y}" width="500" height="21" rx="3" class="track"/>', f'<rect x="342" y="{y}" width="{bar}" height="21" rx="3" fill="{color}"/>', f'<text x="{width-28}" y="{y+15}" class="value">{count:,} cases</text>'))
    lines.extend((f'<text x="26" y="{status_top-17}" class="section">Current correctness results</text>', f'<text x="26" y="{status_top+4}" class="note">Every result is compared with the frozen CPython fixture; failures and timeouts remain visible.</text>'))
    for index, result in enumerate(results):
        y = status_top + 20 + index * 34
        passed = result["passed"]
        cases = result["cases"]
        failed = result["failed"]
        bar = round(500 * passed / cases) if cases else 0
        color = "#238b64" if failed == 0 else "#c84c4c"
        label = MODULES.get(result["module"], result["module"])
        lines.extend((f'<text x="26" y="{y+15}" class="label">{label}</text>', f'<rect x="342" y="{y}" width="500" height="21" rx="3" class="track"/>', f'<rect x="342" y="{y}" width="{bar}" height="21" rx="3" fill="{color}"/>', f'<text x="{width-28}" y="{y+15}" class="value">{passed:,}/{cases:,} passed · {failed:,} failed</text>'))
    lines.append("</svg>\n")
    Path(args.output).write_text("".join(lines), encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
