#!/usr/bin/env python3
"""Correctness-gate and measure the from-scratch Zig mini-regex experiment."""

import argparse
import ctypes
import json
import random
import re
import statistics
import time
from html import escape
from pathlib import Path

from candidates import _zig_bridge


SEED = 20260724
TRIALS = 13
LIBRARY = Path("candidates/_zig_probe.so")
ATOMS = ("a", "b", ".", r"\d", r"\w", "[ab]", "[^x]", "[A-Za-z0-9_-]")
WORDS = ("amber", "birch", "cedar", "delta", "ember", "frost", "gold", "hazel", "iris", "jade")
BENCHMARKS = (
    ("literal-hit", "needle", "prefix needle suffix", 0),
    ("literal-miss", "needle", "ordinary text without a hit", 0),
    ("alternatives-miss", "(?:cedar|birch|maple|willow|spruce|poplar|walnut|aspen|cherry|olive)_[0-9]{2}", "regular prose without tree names or identifiers", 0),
    ("structured-match", "[A-Z]+(?:-[0-9]+)?(?:\\.[A-Z]+(?:-[0-9]+)?)*", "ALPHA-1.BETA.GAMMA-22.DELTA", 2),
    ("url-search", "(?:https?|ftp)://[A-Za-z0-9.-]+(?::[0-9]+)?(?:/[^ ?#]*)?", "link ftp://files.example.net:2121/releases/v4.2.tar?q=no", 0),
    ("multiline-comment", r"//[^\n]*$", "let x = 1; // first\nlet y = 2; // end", 0),
)
TARGETS = (
    (r"[^\n]+", "\nfirst line\nsecond", 0),
    (r"[\n\t]+", "value\n\t\nnext", 0),
    (r"^//[^\n]*$", "code\n// first\n// second", re.MULTILINE),
    (r"(?:|amber)_[0-9]+", "amber_12", 0),
    (r"(?:ab|a)b", "ab abb", 0),
    (r"a.*?b", "a one b a two b", re.DOTALL),
    (r"^[A-Z_-]+$", "Alpha_VALUE", re.IGNORECASE),
    (r"\A\w+(?:-\d+)?\Z", "name-42", re.ASCII),
    (r"\b[A-Za-z_][A-Za-z0-9_]*\b", "skip_one ready item_3", re.ASCII),
    (r"\B(?:ab|xy)+\B", "zababq xxyy", re.ASCII),
)


class Zig:
    def __init__(self, library):
        self.lib = ctypes.CDLL(str(library))
        self.lib.rebar_zig_compile.argtypes = (ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32)
        self.lib.rebar_zig_compile.restype = ctypes.c_void_p
        self.lib.rebar_zig_free.argtypes = (ctypes.c_void_p,)
        match_args = (ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_uint8, ctypes.POINTER(ctypes.c_ssize_t), ctypes.POINTER(ctypes.c_ssize_t))
        self.lib.rebar_zig_match.argtypes = match_args
        self.lib.rebar_zig_match.restype = ctypes.c_int
        self.lib.rebar_zig_match_tree.argtypes = match_args
        self.lib.rebar_zig_match_tree.restype = ctypes.c_int
        self.lib.rebar_zig_batch.argtypes = (*match_args[:6], ctypes.c_size_t, *match_args[6:])
        self.lib.rebar_zig_batch.restype = ctypes.c_int
        self.lib.rebar_zig_program_size.argtypes = ()
        self.lib.rebar_zig_program_size.restype = ctypes.c_size_t

    def compile(self, pattern, flags):
        raw = pattern if isinstance(pattern, bytes) else pattern.encode("ascii")
        handle = self.lib.rebar_zig_compile(raw, len(raw), int(flags))
        if not handle:
            raise ValueError("unsupported or invalid Zig probe pattern")
        return handle

    def span(self, handle, text, pos, end, mode, backend="bytecode"):
        if backend == "native":
            return _zig_bridge.span(handle, text, pos, end, mode)
        raw = text if isinstance(text, bytes) else text.encode("ascii")
        begin, finish = ctypes.c_ssize_t(-1), ctypes.c_ssize_t(-1)
        function = self.lib.rebar_zig_match if backend == "bytecode" else self.lib.rebar_zig_match_tree
        result = function(handle, raw, len(raw), pos, end, mode, ctypes.byref(begin), ctypes.byref(finish))
        if result < 0:
            raise RuntimeError("Zig probe match failed")
        return (begin.value, finish.value) if result else None

    def batch(self, handle, text, pos, end, mode, operations):
        raw = text if isinstance(text, bytes) else text.encode("ascii")
        begin, finish = ctypes.c_ssize_t(-1), ctypes.c_ssize_t(-1)
        result = self.lib.rebar_zig_batch(handle, raw, len(raw), pos, end, mode, operations, ctypes.byref(begin), ctypes.byref(finish))
        if result < 0:
            raise RuntimeError("Zig bytecode batch failed")
        return (begin.value, finish.value) if result else None


def controls(zig):
    rng = random.Random(SEED)
    failures = []
    cases = []
    for _ in range(960):
        branches = rng.sample(WORDS, rng.randint(2, 6))
        atom = rng.choice(ATOMS)
        pattern = rng.choice((
            atom + rng.choice(("*", "+", "?", "{1,3}", "{0,4}?")),
            "(?:" + "|".join(branches) + ")" + rng.choice(("", "_[0-9]{2}", "[A-Za-z]*")),
            "(" + atom + ")" + rng.choice(("*", "+", "{1,3}")) + rng.choice(("", "x", "[0-9]+")),
            "^" + atom + "+(?:_" + atom + "+)*$",
        ))
        flags = rng.choice((0, re.IGNORECASE, re.DOTALL, re.MULTILINE, re.IGNORECASE | re.ASCII))
        text = "".join(rng.choice("abxyzAB0123_ .,-\n") for _ in range(rng.randint(0, 30)))
        if rng.randrange(3) == 0:
            text += rng.choice(branches) + rng.choice(("", "_12", "x"))
        if rng.randrange(2):
            pattern, text = pattern.encode("ascii"), text.encode("ascii")
        pos = rng.randint(0, len(text))
        end = rng.randint(pos, len(text))
        cases.append((pattern, text, flags, pos, end))
    for pattern, text, flags in TARGETS:
        cases.append((pattern, text, flags, 0, len(text)))
        cases.append((pattern.encode("ascii"), text.encode("ascii"), flags | re.ASCII, 0, len(text)))
    checks = 0
    for index, (pattern, text, flags, pos, end) in enumerate(cases):
        try:
            handle = zig.compile(pattern, flags)
        except Exception as error:
            failures.append({"case": index, "stage": "compile", "pattern": repr(pattern), "error": str(error)})
            continue
        try:
            baseline = re.compile(pattern, flags)
            for mode, name in ((0, "search"), (1, "match"), (2, "fullmatch")):
                expected_match = getattr(baseline, name)(text, pos, end)
                expected = expected_match.span() if expected_match else None
                for backend in ("bytecode", "tree", "native"):
                    checks += 1
                    actual = zig.span(handle, text, pos, end, mode, backend)
                    if actual != expected:
                        failures.append({"case": index, "backend": backend, "stage": name, "pattern": repr(pattern), "text": repr(text), "flags": int(flags), "pos": pos, "endpos": end, "expected": expected, "actual": actual})
        finally:
            zig.lib.rebar_zig_free(handle)
    return len(cases), checks, failures


def measure(zig, trials, operations):
    results = []
    raw = []
    for name, pattern, text, mode in BENCHMARKS:
        flags = re.MULTILINE if name == "multiline-comment" else 0
        handle = zig.compile(pattern, flags)
        baseline = re.compile(pattern, flags)
        expected_match = (baseline.search if mode == 0 else baseline.fullmatch)(text)
        expected = expected_match.span() if expected_match else None
        for backend in ("bytecode", "tree", "native"):
            actual = zig.span(handle, text, 0, len(text), mode, backend)
            if actual != expected:
                zig.lib.rebar_zig_free(handle)
                raise RuntimeError(f"benchmark correctness mismatch: {name} {backend}: {actual} != {expected}")
        pairs = []
        for trial in range(trials):
            values = {}
            engines = ("re", "zig-bytecode", "zig-native", "zig-tree", "zig-batched")
            shift = trial % len(engines)
            order = engines[shift:] + engines[:shift]
            if trial % 2:
                order = tuple(reversed(order))
            for engine in order:
                started = time.perf_counter_ns()
                if engine == "re":
                    for _ in range(operations):
                        item = (baseline.search if mode == 0 else baseline.fullmatch)(text)
                        span = item.span() if item else None
                elif engine == "zig-batched":
                    span = zig.batch(handle, text, 0, len(text), mode, operations)
                else:
                    backend = "tree" if engine == "zig-tree" else "native" if engine == "zig-native" else "bytecode"
                    for _ in range(operations):
                        span = zig.span(handle, text, 0, len(text), mode, backend)
                elapsed = time.perf_counter_ns() - started
                if span != expected:
                    raise RuntimeError(f"timed result changed: {name} {engine}")
                values[engine] = elapsed / operations
                raw.append({"case": name, "trial": trial, "engine": engine, "operations": operations, "ns_per_op": values[engine]})
            pairs.append({engine: values["re"] / values[engine] for engine in engines[1:]})
        baseline = statistics.median(row["ns_per_op"] for row in raw if row["case"] == name and row["engine"] == "re")
        for engine in engines[1:]:
            values = [item[engine] for item in pairs]
            rng = random.Random(SEED + sum(map(ord, name + engine)))
            samples = sorted(statistics.geometric_mean(rng.choices(values, k=len(values))) for _ in range(5000))
            results.append({"case": name, "engine": engine, "speedup": statistics.geometric_mean(values), "ci95_low": samples[124], "ci95_high": samples[4874], "baseline_ns_median": baseline, "engine_ns_median": statistics.median(row["ns_per_op"] for row in raw if row["case"] == name and row["engine"] == engine)})
        zig.lib.rebar_zig_free(handle)
    return results, raw


def chart(results, output):
    labels = {"literal-hit": "Find a word (present)", "literal-miss": "Find a word (absent)", "alternatives-miss": "Find one of many words (absent)", "structured-match": "Check a structured value", "url-search": "Find an address", "multiline-comment": "Find a line comment"}
    colors = {"zig-tree": "#d97706", "zig-bytecode": "#2563eb", "zig-native": "#7c3aed", "zig-batched": "#059669"}
    names = {"zig-tree": "Zig tree executor", "zig-bytecode": "Zig compiled / ctypes", "zig-native": "Zig compiled / native bridge", "zig-batched": "Zig compiled, one Python call"}
    width, left, right, top, row = 1120, 260, 110, 94, 102
    height = top + len(BENCHMARKS) * row + 40
    min_log, max_log = -3.0, 1.0
    plot_width = width - left - right
    def x(value):
        import math
        return left + (max(min_log, min(max_log, math.log10(value))) - min_log) / (max_log - min_log) * plot_width
    body = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">', '<rect width="100%" height="100%" fill="#ffffff"/>', '<style>text{font-family:ui-sans-serif,system-ui,sans-serif;fill:#1f2937}.small{font-size:12px}.label{font-size:14px}.title{font-size:20px;font-weight:700}</style>', '<text x="24" y="32" class="title">Zig design probe: speed compared with Python re</text>', '<text x="24" y="54" class="small">Values above 1× are faster. The green rows show matching cost when repeated calls cross the Python boundary once.</text>']
    for value, label in ((0.001, "0.001×"), (0.01, "0.01×"), (0.1, "0.1×"), (1, "1× baseline"), (10, "10×")):
        px = x(value)
        stroke = "#111827" if value == 1 else "#e5e7eb"
        body.append(f'<line x1="{px:.1f}" y1="{top-12}" x2="{px:.1f}" y2="{height-32}" stroke="{stroke}" stroke-width="{2 if value == 1 else 1}"/>')
        body.append(f'<text x="{px:.1f}" y="{top-20}" text-anchor="middle" class="small">{label}</text>')
    order = ("zig-tree", "zig-bytecode", "zig-native", "zig-batched")
    for index, (case, _, _, _) in enumerate(BENCHMARKS):
        base_y = top + index * row
        body.append(f'<text x="{left-14}" y="{base_y+30}" text-anchor="end" class="label">{escape(labels[case])}</text>')
        for offset, engine in enumerate(order):
            result = next(item for item in results if item["case"] == case and item["engine"] == engine)
            speed = result["speedup"]
            px = x(speed)
            y = base_y + offset * 20
            start, bar_width = min(x(0.001), px), abs(px - x(0.001))
            body.append(f'<rect x="{start:.1f}" y="{y}" width="{bar_width:.1f}" height="14" rx="3" fill="{colors[engine]}" opacity="0.88"/>')
            body.append(f'<text x="{min(px+7,width-right+18):.1f}" y="{y+11}" class="small">{speed:.3f}×</text>')
    legend_y = height - 10
    for index, engine in enumerate(order):
        lx = 24 + index * 270
        body.append(f'<rect x="{lx}" y="{legend_y-11}" width="15" height="11" rx="2" fill="{colors[engine]}"/><text x="{lx+21}" y="{legend_y-1}" class="small">{escape(names[engine])}</text>')
    body.append('</svg>')
    Path(output).write_text("\n".join(body) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--library", default=str(LIBRARY))
    parser.add_argument("--chart")
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--trials", type=int, default=TRIALS)
    parser.add_argument("--operations", type=int, default=8000)
    args = parser.parse_args()
    zig = Zig(args.library)
    case_count, checks, failures = controls(zig)
    if failures:
        result = {"schema": "rebar-zig-probe-v3", "seed": SEED, "correctness_cases": case_count, "correctness_checks": checks, "failed": len(failures), "failures": failures}
        Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({key: value for key, value in result.items() if key != "failures"}, sort_keys=True))
        return 1
    if args.verify_only:
        result = {"schema": "rebar-zig-probe-v3", "seed": SEED, "correctness_cases": case_count, "correctness_checks": checks, "failed": 0, "program_bytes": zig.lib.rebar_zig_program_size()}
        Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, sort_keys=True))
        return 0
    if args.trials < 1 or args.operations < 1:
        raise ValueError("--trials and --operations must be positive")
    results, raw = measure(zig, args.trials, args.operations)
    overall = {engine: statistics.geometric_mean(item["speedup"] for item in results if item["engine"] == engine) for engine in ("zig-tree", "zig-bytecode", "zig-native", "zig-batched")}
    result = {"schema": "rebar-zig-probe-v3", "seed": SEED, "correctness_cases": case_count, "correctness_checks": checks, "failed": 0, "trials": args.trials, "operations": args.operations, "program_bytes": zig.lib.rebar_zig_program_size(), "overall": overall, "results": results, "raw": raw}
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.chart:
        chart(results, args.chart)
    print(json.dumps({"correctness_checks": checks, "failed": 0, "overall": overall, "program_bytes": result["program_bytes"], "results": results, "trials": args.trials}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
