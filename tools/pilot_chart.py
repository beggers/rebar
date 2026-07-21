#!/usr/bin/env python3
"""Generate a compact log-scale pilot chart from every raw pilot row."""

import argparse
import json
import math
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    rows = [json.loads(line) for line in Path(args.input).read_text(encoding="utf-8").splitlines()]
    cases = sorted({row["case"] for row in rows})
    names = ["candidates.ast_candidate", "candidates.vm_candidate", "candidates.rust_candidate"]
    values = {(row["case"], row["module"]): row["elapsed_ns"] for row in rows}
    width, left, plot, row_height = 940, 244, 650, 20
    height = 82 + len(cases) * row_height
    colors = {names[0]: "#7c3aed", names[1]: "#0284c7", names[2]: "#d97706"}
    body = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Pilot candidate speed ratios for all cases">', '<rect width="100%" height="100%" fill="#fff"/>', '<text x="24" y="30" font-family="sans-serif" font-size="20" font-weight="700" fill="#172033">Pilot speed ratios — all 32 cases</text>', '<text x="24" y="51" font-family="sans-serif" font-size="12" fill="#42526e">One correctness-gated operation; log10(stdlib / candidate). Formal confidence is NOT MEASURED.</text>']
    for tick in range(-7, 2):
        x = left + round(plot * (tick + 7) / 8)
        body.append(f'<line x1="{x}" y1="62" x2="{x}" y2="{height-8}" stroke="#e5e7eb"/>')
        body.append(f'<text x="{x}" y="73" text-anchor="middle" font-family="monospace" font-size="9" fill="#6b7280">1e{tick}</text>')
    for index, case in enumerate(cases):
        y = 90 + index * row_height
        body.append(f'<text x="24" y="{y+3}" font-family="monospace" font-size="10" fill="#172033">{case}</text>')
        base = values[(case, "re")]
        for offset, name in enumerate(names):
            ratio = base / values[(case, name)]
            value = max(-7, min(1, math.log10(ratio)))
            x = left + round(plot * (value + 7) / 8)
            body.append(f'<circle cx="{x}" cy="{y-5+offset*5}" r="2.5" fill="{colors[name]}"/>')
    body.append(f'<text x="{left}" y="{height-5}" font-family="sans-serif" font-size="10" fill="#42526e">purple: AST · blue: native VM · orange: Rust/FFI · right of 1e0 is faster than stdlib</text>')
    body.append("</svg>\n")
    Path(args.output).write_text("\n".join(body), encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
