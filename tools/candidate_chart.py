#!/usr/bin/env python3
"""Generate the committed candidate-correctness chart from raw oracle results."""

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--title", default="Candidate correctness — raw discovery")
    parser.add_argument("--subtitle", default="All cases and failures retained; no compatibility adapter applied.")
    parser.add_argument("results", nargs="+")
    args = parser.parse_args()
    rows = []
    for value in args.results:
        result = json.loads(Path(value).read_text(encoding="utf-8"))
        rows.append((result["module"], result["passed"], result["failed"], result["cases"]))
    width = 800
    height = 104 + 62 * len(rows)
    body = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Candidate correctness results">', '<rect width="100%" height="100%" fill="#fff"/>', f'<text x="28" y="36" font-family="sans-serif" font-size="22" font-weight="700" fill="#172033">{args.title}</text>', f'<text x="28" y="59" font-family="sans-serif" font-size="13" fill="#42526e">{args.subtitle}</text>']
    for index, (name, passed, failed, cases) in enumerate(rows):
        y = 82 + index * 62
        total_width = 520
        pass_width = round(total_width * passed / cases) if cases else 0
        body.extend([f'<text x="28" y="{y + 17}" font-family="monospace" font-size="14" fill="#172033">{name}</text>', f'<rect x="140" y="{y}" width="{total_width}" height="24" rx="3" fill="#b91c1c"/>', f'<rect x="140" y="{y}" width="{pass_width}" height="24" rx="3" fill="#15803d"/>', f'<text x="674" y="{y + 17}" font-family="monospace" font-size="13" fill="#172033">{passed}/{cases}</text>', f'<text x="140" y="{y + 43}" font-family="sans-serif" font-size="12" fill="#6b7280">{failed} failed</text>'])
    body.append("</svg>\n")
    Path(args.output).write_text("\n".join(body), encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
