#!/usr/bin/env python3
"""Draw a plain-language, correctness-gated picture of the larger re benchmark."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from html import escape
from pathlib import Path

from tools.perf_v7 import frozen


DOMAIN_LABELS = {
    "protocols": "Web, network, and logs",
    "source": "Source code and data",
    "unicode": "Languages and Unicode",
    "lookaround": "Boundaries and captures",
    "backtracking": "Difficult match rules",
    "buffers": "Bytes and input buffers",
    "lifecycle": "Compilation and reuse",
    "density": "Few and many results",
}


def text(x, y, value, css, *, anchor=None):
    suffix = f' text-anchor="{anchor}"' if anchor else ""
    return f'<text x="{x}" y="{y}" class="{css}"{suffix}>{escape(str(value))}</text>'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    suite, cases, _expected, manifest = frozen()
    result = json.loads(Path(args.result).read_text(encoding="utf-8"))
    if (
        result.get("schema") != "rebar-performance-correctness-v7"
        or result.get("expected_sha256") != manifest["expected_sha256"]
        or result.get("cases_per_module") != len(cases)
        or result.get("checks") != len(cases) * len(suite.MODULES)
        or set(result.get("modules", ())) != set(suite.MODULES)
        or len(result.get("modules", ())) != len(suite.MODULES)
    ):
        raise RuntimeError("the larger coverage chart requires every frozen candidate check")
    if result.get("failed") != len(result.get("failures", ())):
        raise RuntimeError("the larger coverage chart has inconsistent failures")

    specs = suite.SPECS
    domains = Counter(item["domain"] for item in specs)
    if domains != {name: 8 for name in DOMAIN_LABELS}:
        raise RuntimeError("the larger coverage chart lost its eight balanced categories")

    width = 1260
    header = 128
    card_top = 148
    card_height = 52
    family_top = 298
    family_row = 21
    family_bottom = family_top + 32 * family_row
    api_top = family_bottom + 62
    api_row = 23
    footer_top = api_top + len(manifest["api_counts"]) * api_row + 41
    height = footer_top + 104
    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}" '
        'role="img" aria-label="Larger independently checked Python re benchmark">',
        '<rect width="100%" height="100%" fill="#f8fafc"/>',
        '<style>text{font-family:system-ui,-apple-system,Segoe UI,sans-serif;'
        'fill:#172033}.title{font-size:25px;font-weight:750}.sub{font-size:13px;'
        'fill:#526076}.head{font-size:16px;font-weight:700}.label{font-size:12px}'
        '.value{font-size:12px;font-weight:700}.note{font-size:12px;fill:#526076}'
        '.card{fill:#fff;stroke:#dbe5ef}.track{fill:#e2e8f0}</style>',
        text(28, 42, "How thoroughly are the faster Python re replacements tested?", "title"),
        text(
            28,
            67,
            f"{manifest['cohorts']['holdout']:,} unseen tasks · "
            f"{manifest['cohorts']['calibration']:,} separate practice tasks · "
            f"CPython {manifest['python']} baseline",
            "sub",
        ),
        text(
            28,
            91,
            f"All {manifest['parent_cases']:,} earlier tasks are preserved exactly. "
            "The larger test adds 64 balanced kinds of real work.",
            "sub",
        ),
        text(28, header, "Eight equally represented kinds of work", "head"),
    ]

    for index, (domain, label) in enumerate(DOMAIN_LABELS.items()):
        column, row = index % 4, index // 4
        x = 28 + column * 308
        y = card_top + row * (card_height + 9)
        body.extend(
            (
                f'<rect x="{x}" y="{y}" width="296" height="{card_height}" '
                'rx="8" class="card"/>',
                text(x + 12, y + 21, label, "value"),
                text(x + 12, y + 39, "8 workload families · 512 unseen examples", "note"),
            )
        )

    body.append(text(28, family_top - 19, "All 64 additional workload families", "head"))
    for index, item in enumerate(specs):
        column, line = index % 2, index // 2
        x = 28 + column * 615
        y = family_top + line * family_row
        name = item["name"].replace("-", " ")
        body.extend(
            (
                text(x, y + 13, name, "label"),
                f'<rect x="{x + 393}" y="{y + 1}" width="122" '
                'height="14" rx="3" class="track"/>',
                f'<rect x="{x + 393}" y="{y + 1}" width="122" '
                'height="14" rx="3" fill="#4f7fb8"/>',
                text(x + 587, y + 13, "64 unseen", "value", anchor="end"),
            )
        )

    body.extend(
        (
            text(28, api_top - 31, "Which normal Python re calls are exercised?", "head"),
            text(
                28,
                api_top - 10,
                "Counts include every preserved and new task. Text, bytes, "
                "mutable buffers, compiled calls, module calls, and fresh compilation are included.",
                "note",
            ),
        )
    )
    largest = max(manifest["api_counts"].values())
    for index, (api, count) in enumerate(manifest["api_counts"].items()):
        y = api_top + index * api_row
        bar = round(680 * count / largest)
        label = "match details" if api == "match-surface" else api
        body.extend(
            (
                text(28, y + 14, label, "label"),
                f'<rect x="220" y="{y + 1}" width="680" '
                'height="16" rx="3" class="track"/>',
                f'<rect x="220" y="{y + 1}" width="{bar}" '
                'height="16" rx="3" fill="#60966f"/>',
                text(940, y + 14, f"{count:,} tasks", "value"),
            )
        )

    failed = result["failed"]
    passed = result["checks"] - failed
    buffers = sum(
        manifest["input_counts"].get(kind, 0)
        for kind in ("bytes", "bytearray", "memoryview")
    )
    color = "#238b64" if failed == 0 else "#c84c4c"
    body.extend(
        (
            f'<rect x="24" y="{footer_top}" width="1212" height="81" '
            'rx="8" fill="#fff" stroke="#cbd5e1"/>',
            text(42, footer_top + 23, "All engines must match Python before any timing", "head"),
            text(
                42,
                footer_top + 45,
                f"{passed:,}/{result['checks']:,} frozen checks agree · "
                f"{failed:,} failures · {buffers:,} byte and buffer tasks · "
                f"{manifest['surrogate_subject_cases']:,} lone-surrogate tasks",
                "value",
            ),
            text(
                42,
                footer_top + 65,
                f"{manifest['trials']} paired trials · {manifest['warmups']} warmups · "
                f"{manifest['bootstraps']:,} confidence samples · every task counts equally",
                "note",
            ),
            f'<circle cx="1207" cy="{footer_top + 39}" r="10" fill="{color}"/>',
            "</svg>\n",
        )
    )
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("".join(body), encoding="utf-8")
    print(f"wrote {destination}")


if __name__ == "__main__":
    main()
