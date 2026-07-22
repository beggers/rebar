#!/usr/bin/env python3
"""Differentially check and measure the from-scratch capture-aware Zig executor."""

import argparse
import ctypes
import json
import math
import random
import re
import statistics
import time
from html import escape
from pathlib import Path

from candidates import _zig_bridge


SEED = 20260728
LIBRARY = Path("candidates/_zig_probe.so")
ATOMS = ("a", "b", ".", r"\d", r"\w", "[ab]", "[^x]", "[A-Za-z0-9_-]")
TARGETS = (
    (r"(a(b)?)+", "aba", 0),
    (r"((ab)|a)b", "ab abb", 0),
    (r"(a)?(b+)", "xx bbb", 0),
    (r"((?:a|b){1,3})(x)?", "abx", 0),
    (r"^([A-Z]+)_([0-9]{2,4})$", "skip\nTAG_2048", re.MULTILINE),
    (r"(a.*?b)(c)?", "a one b a two bc", re.DOTALL),
    (r"((a)|(b))+", "abba", 0),
    (r"(a(b(c)?){0,2})+", "abcbcabc", 0),
    (r"\b([A-Za-z_][A-Za-z0-9_]*)\b", "skip_one ready item_3", re.ASCII),
    (r"\B((ab|xy)+)\B", "zababq xxyy", re.ASCII),
)
BENCHMARKS = (
    ("literal-capture", r"(needle)", "prefix needle suffix", 0, 0),
    ("optional-capture", r"([A-Z]+)(?:_([0-9]+))?", "prefix ITEM_730 suffix", 0, 0),
    ("alternatives-capture", r"(cedar|birch|maple|willow|spruce|poplar|walnut|aspen|cherry|olive)_([0-9]{2})", "regular prose without tree names or identifiers", 0, 0),
    ("structured-capture", r"([A-Z]+)(?:-([0-9]+))?(?:\.([A-Z]+)(?:-([0-9]+))?)*", "ALPHA-1.BETA.GAMMA-22.DELTA", 2, 0),
    ("url-capture", r"(https?|ftp)://([A-Za-z0-9.-]+)(?::([0-9]+))?(/[^ ?#]*)?", "link ftp://files.example.net:2121/releases/v4.2.tar?q=no", 0, 0),
    ("line-capture", r"^([A-Z]+)\s+([A-Z]{3}[0-9]{2})\s+([^\n]+)$", "TRACE NET01 connected\nDEBUG CFG20 loaded", 0, re.MULTILINE),
)


class Zig:
    def __init__(self, library):
        self.lib = ctypes.CDLL(str(library))
        self.lib.rebar_zig_compile.argtypes = (ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32)
        self.lib.rebar_zig_compile.restype = ctypes.c_void_p
        self.lib.rebar_zig_free.argtypes = (ctypes.c_void_p,)
        self.lib.rebar_zig_groups.argtypes = (ctypes.c_void_p,)
        self.lib.rebar_zig_groups.restype = ctypes.c_size_t

    def compile(self, pattern, flags):
        raw = pattern if isinstance(pattern, bytes) else pattern.encode("ascii")
        handle = self.lib.rebar_zig_compile(raw, len(raw), int(flags))
        if not handle:
            raise ValueError("unsupported or invalid Zig capture pattern")
        return handle

    def run(self, handle, text, pos, end, mode):
        return _zig_bridge.match(handle, text, pos, end, mode)


def expected_value(compiled, text, pos, end, mode):
    found = (compiled.search, compiled.match, compiled.fullmatch)[mode](text, pos, end)
    if found is None:
        return None
    spans = tuple(None if found.start(index) < 0 else found.span(index) for index in range(compiled.groups + 1))
    return spans, found.lastindex


def controls(zig):
    rng = random.Random(SEED)
    cases = []
    for _ in range(1200):
        left, right = rng.choice(ATOMS), rng.choice(ATOMS)
        quantifier = rng.choice(("*", "+", "?", "{1,3}", "{0,4}?"))
        pattern = rng.choice((
            f"({left}){quantifier}({right})?",
            f"(({left})|({right})){quantifier}",
            f"(({left})(?:{right})?){{1,3}}(x)?",
            f"^({left}+)(?:_({right}+))*$",
        ))
        flags = rng.choice((0, re.IGNORECASE, re.DOTALL, re.MULTILINE, re.IGNORECASE | re.ASCII))
        text = "".join(rng.choice("abxyzAB0123_ .,-\n") for _ in range(rng.randint(0, 28)))
        if rng.randrange(3) == 0:
            text += rng.choice(("ab", "aabx", "TAG_42", "bbb", "a12x"))
        if rng.randrange(2):
            pattern, text = pattern.encode("ascii"), text.encode("ascii")
        pos = rng.randint(0, len(text))
        end = rng.randint(pos, len(text))
        cases.append((pattern, text, flags, pos, end))
    for pattern, text, flags in TARGETS:
        cases.append((pattern, text, flags, 0, len(text)))
        cases.append((pattern.encode("ascii"), text.encode("ascii"), flags | re.ASCII, 0, len(text)))
    failures = []
    checks = 0
    for index, (pattern, text, flags, pos, end) in enumerate(cases):
        try:
            baseline = re.compile(pattern, flags)
            handle = zig.compile(pattern, flags)
        except BaseException as error:
            failures.append({"case": index, "stage": "compile", "pattern": repr(pattern), "type": type(error).__name__, "message": str(error)})
            continue
        try:
            if zig.lib.rebar_zig_groups(handle) != baseline.groups:
                failures.append({"case": index, "stage": "groups", "pattern": repr(pattern), "expected": baseline.groups, "actual": zig.lib.rebar_zig_groups(handle)})
            for mode, name in enumerate(("search", "match", "fullmatch")):
                checks += 1
                expected = expected_value(baseline, text, pos, end, mode)
                actual = zig.run(handle, text, pos, end, mode)
                if actual != expected:
                    failures.append({"case": index, "stage": name, "pattern": repr(pattern), "text": repr(text), "flags": int(flags), "pos": pos, "endpos": end, "expected": expected, "actual": actual})
        finally:
            zig.lib.rebar_zig_free(handle)
    return len(cases), checks, failures


def measure(zig, trials, operations):
    results = []
    rows = []
    for name, pattern, text, mode, flags in BENCHMARKS:
        compiled = re.compile(pattern, flags)
        handle = zig.compile(pattern, flags)
        expected = expected_value(compiled, text, 0, len(text), mode)
        actual = zig.run(handle, text, 0, len(text), mode)
        if actual != expected:
            zig.lib.rebar_zig_free(handle)
            raise RuntimeError(f"pre-timing Zig capture mismatch: {name}")
        paired = []
        for trial in range(trials):
            order = ("re", "zig") if trial % 2 == 0 else ("zig", "re")
            values = {}
            for order_index, engine in enumerate(order):
                started = time.perf_counter_ns()
                if engine == "re":
                    for _ in range(operations):
                        value = expected_value(compiled, text, 0, len(text), mode)
                else:
                    for _ in range(operations):
                        value = zig.run(handle, text, 0, len(text), mode)
                elapsed = time.perf_counter_ns() - started
                if value != expected:
                    raise RuntimeError(f"post-timing Zig capture mismatch: {name} {engine}")
                values[engine] = elapsed / operations
                rows.append({"case": name, "trial": trial, "engine": engine, "order": order_index, "operations": operations, "ns_per_op": values[engine]})
            paired.append(values["re"] / values["zig"])
        rng = random.Random(SEED + sum(map(ord, name)))
        bootstrap = sorted(statistics.geometric_mean(rng.choices(paired, k=len(paired))) for _ in range(5000))
        results.append({"case": name, "speedup": statistics.geometric_mean(paired), "ci95_low": bootstrap[124], "ci95_high": bootstrap[4874], "baseline_ns_median": statistics.median(row["ns_per_op"] for row in rows if row["case"] == name and row["engine"] == "re"), "zig_ns_median": statistics.median(row["ns_per_op"] for row in rows if row["case"] == name and row["engine"] == "zig")})
        zig.lib.rebar_zig_free(handle)
    return results, rows


def chart(results, output):
    labels = {"literal-capture": "Find a captured word", "optional-capture": "Find optional captured fields", "alternatives-capture": "Search captured alternatives (absent)", "structured-capture": "Check repeated captured fields", "url-capture": "Find a captured address", "line-capture": "Find captured line fields"}
    width, height, left, top, row = 960, 460, 290, 100, 55
    plot = 520
    minimum, maximum = .05, 5
    def x(value):
        return left + (math.log10(max(minimum, min(maximum, value))) - math.log10(minimum)) / (math.log10(maximum) - math.log10(minimum)) * plot
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="#fff"/>', '<style>text{font-family:system-ui,-apple-system,Segoe UI,sans-serif;fill:#172033}.title{font-size:22px;font-weight:700}.sub{font-size:13px;fill:#526079}.label{font-size:13px}.num{font-size:12px;font-weight:700}</style>', '<text x="24" y="36" class="title">Zig capture-aware engine: speed compared with Python re</text>', '<text x="24" y="60" class="sub">Values above 1× are faster. Each call returns all capture spans and lastindex; every timed result is checked.</text>']
    for value in (.05, .1, .25, .5, 1, 2, 5):
        point = x(value)
        lines.append(f'<line x1="{point:.1f}" y1="{top-16}" x2="{point:.1f}" y2="{height-28}" stroke="{"#111827" if value == 1 else "#e1e6ef"}" stroke-width="{2 if value == 1 else 1}"/>')
        lines.append(f'<text x="{point:.1f}" y="{top-24}" text-anchor="middle" class="sub">{value:g}×</text>')
    for index, result in enumerate(results):
        y = top + index * row
        low, high, speed = x(result["ci95_low"]), x(result["ci95_high"]), x(result["speedup"])
        color = "#238b64" if result["ci95_low"] > 1 else "#c84c4c" if result["ci95_high"] < .8 else "#7c3aed"
        lines.extend((f'<text x="{left-15}" y="{y+8}" text-anchor="end" class="label">{escape(labels[result["case"]])}</text>', f'<line x1="{low:.1f}" y1="{y+3}" x2="{high:.1f}" y2="{y+3}" stroke="{color}" stroke-width="5" stroke-linecap="round"/>', f'<circle cx="{speed:.1f}" cy="{y+3}" r="7" fill="{color}"/>', f'<text x="{left+plot+18}" y="{y+8}" class="num">{result["speedup"]:.3f}× ({result["ci95_low"]:.3f}–{result["ci95_high"]:.3f})</text>'))
    lines.append("</svg>\n")
    Path(output).write_text("".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--library", default=str(LIBRARY))
    parser.add_argument("--chart")
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--trials", type=int, default=13)
    parser.add_argument("--operations", type=int, default=8000)
    args = parser.parse_args()
    zig = Zig(args.library)
    cases, checks, failures = controls(zig)
    if failures or args.verify_only:
        result = {"schema": "rebar-zig-capture-v1", "seed": SEED, "correctness_cases": cases, "correctness_checks": checks, "failed": len(failures), "failures": failures}
        Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({key: value for key, value in result.items() if key != "failures"}, sort_keys=True))
        return int(bool(failures))
    results, rows = measure(zig, args.trials, args.operations)
    overall = statistics.geometric_mean(item["speedup"] for item in results)
    result = {"schema": "rebar-zig-capture-v1", "seed": SEED, "correctness_cases": cases, "correctness_checks": checks, "failed": 0, "trials": args.trials, "operations": args.operations, "overall": overall, "results": results, "raw": rows}
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.chart:
        chart(results, args.chart)
    print(json.dumps({key: value for key, value in result.items() if key != "raw"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
