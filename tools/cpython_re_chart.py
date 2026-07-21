#!/usr/bin/env python3
"""Draw the vendored CPython re compatibility results."""

import argparse
import html
import json
from pathlib import Path

NAMES = {"re": "Python re (self-check)", "rebar": "Native C / rebar", "candidates.ast_candidate": "Python engine", "candidates.rust_candidate": "Rust engine"}
COLORS = {"re": "#15803d", "rebar": "#0284c7", "candidates.ast_candidate": "#7c3aed", "candidates.rust_candidate": "#d97706"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", action="append", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    rows = [json.loads(Path(value).read_text(encoding="utf-8")) for value in args.input]
    width, left, bar, row_height = 1110, 256, 550, 70
    height = 126 + row_height * len(rows)
    body = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="CPython re compatibility check">', '<rect width="100%" height="100%" fill="#f8fafc"/>', '<text x="28" y="35" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#0f172a">CPython re compatibility check</text>', '<text x="28" y="60" font-family="Arial, sans-serif" font-size="13" fill="#475569">Official public test methods. Green is passing; red shows failures, crashes, or timeouts. Locale-dependent skips are shown separately.</text>']
    for index, row in enumerate(rows):
        y = 100 + index * row_height
        usable = row["methods"] - row["skipped"]
        passed = row["passed"]
        good = round(bar * passed / max(usable, 1))
        name = html.escape(NAMES.get(row["module"], row["module"]), quote=True)
        color = COLORS.get(row["module"], "#475569")
        body.extend([f'<text x="28" y="{y+19}" font-family="Arial, sans-serif" font-size="14" font-weight="700" fill="{color}">{name}</text>', f'<rect x="{left}" y="{y}" width="{bar}" height="24" rx="5" fill="#fee2e2"/>', f'<rect x="{left}" y="{y}" width="{good}" height="24" rx="5" fill="#15803d"/>', f'<text x="{left+bar+20}" y="{y+17}" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#0f172a">{passed}/{usable} passed · {row["failed"]} failed</text>', f'<text x="{left+bar+20}" y="{y+36}" font-family="Arial, sans-serif" font-size="11" fill="#475569">{row["crashes"]} crashes · {row["timeouts"]} timeouts · {row["skipped"]} locale skips</text>'])
    body.append("</svg>\n")
    Path(args.output).write_text("\n".join(body), encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
