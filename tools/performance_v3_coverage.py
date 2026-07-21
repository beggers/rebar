#!/usr/bin/env python3
"""Generate a compact, plain-language coverage/status chart for performance v3."""

import argparse
import html
import json
from pathlib import Path


def esc(value):
    return html.escape(str(value), quote=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="performance/v3/manifest.json")
    parser.add_argument("--correctness", default="performance/v3/evidence/initial-correctness.json")
    parser.add_argument("--output", default="performance/v3/evidence/coverage.svg")
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    correctness = json.loads(Path(args.correctness).read_text(encoding="utf-8"))
    groups = [
        ("Earlier tasks, preserved", 28, "#0ea5e9"),
        ("Everyday examples", 15, "#10b981"),
        ("Pattern and matching shapes", 11, "#6366f1"),
        ("API and input shapes", 10, "#f59e0b"),
        ("Boundary and short calls", 8, "#ec4899"),
    ]
    total = sum(count for _, count, _ in groups)
    if manifest["cohorts"]["holdout"] != total or manifest["cohorts"]["calibration"] != total:
        raise RuntimeError("coverage totals no longer match frozen cohorts")
    width, height = 1120, 390
    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Broader performance coverage and current status">',
        '<rect width="100%" height="100%" fill="#f8fafc"/>',
        '<text x="28" y="36" font-family="Arial, sans-serif" font-size="23" font-weight="700" fill="#0f172a">A broader check for building a faster Python re</text>',
        '<text x="28" y="61" font-family="Arial, sans-serif" font-size="14" fill="#475569">72 separate holdout tasks, matched by 72 practice tasks. Earlier coverage is preserved; new tasks add realistic inputs and API boundaries.</text>',
    ]
    cards = [
        ("72", "holdout tasks", "#0369a1"),
        ("144", "tasks total", "#047857"),
        (str(manifest["trials"]), "paired trials", "#4338ca"),
        (str(correctness["failed"]), "checks to fix", "#b91c1c"),
    ]
    for index, (value, label, color) in enumerate(cards):
        x = 28 + index * 270
        body.extend([
            f'<rect x="{x}" y="82" width="250" height="70" rx="9" fill="#fff" stroke="#cbd5e1"/>',
            f'<text x="{x+16}" y="114" font-family="Arial, sans-serif" font-size="25" font-weight="700" fill="{color}">{esc(value)}</text>',
            f'<text x="{x+16}" y="138" font-family="Arial, sans-serif" font-size="13" fill="#475569">{esc(label)}</text>',
        ])
    body.append('<text x="28" y="183" font-family="Arial, sans-serif" font-size="15" font-weight="700" fill="#0f172a">What is in the holdout</text>')
    left, bar_width = 28, 1060
    offset = left
    for _, count, color in groups:
        segment = round(bar_width * count / total)
        body.append(f'<rect x="{offset}" y="196" width="{segment}" height="22" fill="{color}"/>')
        offset += segment
    for index, (label, count, color) in enumerate(groups):
        y = 245 + index * 22
        body.extend([
            f'<rect x="30" y="{y-11}" width="12" height="12" rx="2" fill="{color}"/>',
            f'<text x="52" y="{y}" font-family="Arial, sans-serif" font-size="13" fill="#334155">{esc(label)}: {count}</text>',
        ])
    checks = correctness["checks"]
    passed = checks - correctness["failed"]
    status_line = "Current status: NOT MEASURED"
    details = [
        f"The pre-timing check passes {passed}/{checks} comparisons.",
        "Windowed scanners need support in all engines; native C also misses",
        "the first line of two multiline configuration examples.",
    ]
    if correctness["failed"] == 0:
        details = [
            f"All {passed}/{checks} pre-timing comparisons now pass.",
            "Windowed scanners and multiline first-line matching are fixed.",
            "The official CPython compatibility suite still needs work before timing.",
        ]
    body.extend([
        f'<text x="590" y="248" font-family="Arial, sans-serif" font-size="15" font-weight="700" fill="#0f172a">{esc(status_line)}</text>',
        f'<text x="590" y="273" font-family="Arial, sans-serif" font-size="13" fill="#475569">{esc(details[0])}</text>',
        f'<text x="590" y="297" font-family="Arial, sans-serif" font-size="13" fill="#475569">{esc(details[1])}</text>',
        f'<text x="590" y="319" font-family="Arial, sans-serif" font-size="13" fill="#475569">{esc(details[2])}</text>',
        '<text x="28" y="376" font-family="Arial, sans-serif" font-size="12" fill="#64748b">Incorrect cases are never timed. Once correctness is clean, the same frozen holdout will provide clearer overall and task-by-task speed evidence.</text>',
        '</svg>\n',
    ])
    Path(args.output).write_text("\n".join(body), encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
