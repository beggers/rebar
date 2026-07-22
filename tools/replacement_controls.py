#!/usr/bin/env python3
"""Differential checks for replacement validation, expansion, and output types."""

import argparse
import importlib
import json
import re
from pathlib import Path


MODULES = ("rebar", "candidates.ast_candidate", "candidates.rust_candidate")
TEXT_SUBJECTS = ("", "bbb", "a", "ba", "aba")
BYTE_SUBJECTS = (b"", b"bbb", b"a", b"ba", b"aba")
REPLACEMENTS = (
    ("text-empty", lambda: ""),
    ("text-literal", lambda: "X"),
    ("text-group", lambda: r"<\g<0>>"),
    ("text-number", lambda: r"<\1>"),
    ("text-bad-escape", lambda: r"\q"),
    ("text-bad-group", lambda: r"\g<4>"),
    ("bytes-empty", lambda: b""),
    ("bytes-literal", lambda: b"X"),
    ("bytes-group", lambda: b"<\\g<0>>"),
    ("bytes-number", lambda: b"<\\1>"),
    ("bytes-bad-escape", lambda: b"\\q"),
    ("bytes-bad-group", lambda: b"\\g<4>"),
    ("bytearray-literal", lambda: bytearray(b"X")),
    ("bytearray-group", lambda: bytearray(b"<\\g<0>>")),
    ("memoryview-literal", lambda: memoryview(b"X")),
    ("memoryview-group", lambda: memoryview(b"<\\g<0>>")),
    ("none", lambda: None),
    ("integer", lambda: 7),
    ("tuple", lambda: ("X",)),
    ("list", lambda: ["X"]),
    ("object", lambda: object()),
    ("call-text", lambda: lambda match: "X"),
    ("call-bytes", lambda: lambda match: b"X"),
    ("call-bytearray", lambda: lambda match: bytearray(b"X")),
    ("call-memoryview", lambda: lambda match: memoryview(b"X")),
)


def normalize(value):
    if isinstance(value, tuple):
        return {"type": "tuple", "value": [normalize(item) for item in value]}
    if isinstance(value, bytes):
        return {"type": type(value).__name__, "value": value.hex()}
    return {"type": type(value).__name__, "value": value}


def outcome(function):
    try:
        return {"ok": True, "result": normalize(function())}
    except Exception as error:
        return {"ok": False, "type": type(error).__name__, "message": str(error)}


def subject_value(kind, value):
    if kind == "text" or kind == "bytes":
        return value
    if kind == "bytearray":
        return bytearray(value)
    return memoryview(value)


def invoke(module, record):
    pattern = record["pattern"]
    subject = subject_value(record["subject_kind"], record["subject"])
    replacement = record["replacement_factory"]()
    if record["api"] == "expand":
        match = module.compile(pattern).search(subject)
        if match is None:
            return {"ok": True, "result": {"type": "no-match", "value": None}}
        return outcome(lambda: match.expand(replacement))
    if record["surface"] == "compiled":
        function = getattr(module.compile(pattern), record["api"])
        return outcome(lambda: function(replacement, subject, record["count"]))
    function = getattr(module, record["api"])
    return outcome(lambda: function(pattern, replacement, subject, count=record["count"]))


def records():
    result = []
    for subject_kind, subjects in (("text", TEXT_SUBJECTS), ("bytes", BYTE_SUBJECTS), ("bytearray", BYTE_SUBJECTS), ("memoryview", BYTE_SUBJECTS)):
        byte_mode = subject_kind != "text"
        patterns = ((b"(a)" if byte_mode else "(a)"), (b"(?P<word>a+)" if byte_mode else "(?P<word>a+)"))
        for pattern in patterns:
            for subject in subjects:
                for replacement_name, replacement_factory in REPLACEMENTS:
                    for api in ("sub", "subn"):
                        for surface in ("module", "compiled"):
                            for count in (0, 1, -1):
                                result.append({"subject_kind": subject_kind, "subject": subject, "pattern": pattern, "replacement": replacement_name, "replacement_factory": replacement_factory, "api": api, "surface": surface, "count": count})
                    result.append({"subject_kind": subject_kind, "subject": subject, "pattern": pattern, "replacement": replacement_name, "replacement_factory": replacement_factory, "api": "expand", "surface": "compiled", "count": 0})
    return result


def shown(record):
    return {key: (repr(value) if key in {"subject", "pattern"} else value) for key, value in record.items() if key != "replacement_factory"}


def chart(initial, final, output):
    labels = {"rebar": "Native C", "candidates.ast_candidate": "Python", "candidates.rust_candidate": "Rust"}
    width, left, right, top, row = 920, 132, 100, 82, 72
    plot = width - left - right
    height = top + len(MODULES) * row + 54
    maximum = final["cases_per_module"]
    body = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">', '<rect width="100%" height="100%" fill="#ffffff"/>', '<style>text{font-family:ui-sans-serif,system-ui,sans-serif;fill:#1f2937}.title{font-size:20px;font-weight:700}.small{font-size:12px}.label{font-size:15px;font-weight:600}</style>', '<text x="24" y="32" class="title">Replacement compatibility: before and after the fix</text>', f'<text x="24" y="54" class="small">Each engine is checked on {maximum:,} text, bytes, buffer, callback, empty, and error cases. Green means the result matches Python re.</text>']
    for index, module in enumerate(MODULES):
        y = top + index * row
        body.append(f'<text x="{left-14}" y="{y+28}" text-anchor="end" class="label">{labels[module]}</text>')
        for offset, (name, value, color) in enumerate((("Before", initial["passed"][module], "#dc2626"), ("After", final["passed"][module], "#16a34a"))):
            bar_y = y + offset * 23
            bar_width = plot * value / maximum
            body.append(f'<rect x="{left}" y="{bar_y}" width="{plot}" height="16" rx="3" fill="#f3f4f6"/>')
            body.append(f'<rect x="{left}" y="{bar_y}" width="{bar_width:.1f}" height="16" rx="3" fill="{color}" opacity="0.85"/>')
            body.append(f'<text x="{left+6}" y="{bar_y+12}" class="small" fill="#ffffff">{name}</text>')
            body.append(f'<text x="{width-right+8}" y="{bar_y+12}" class="small">{value:,}/{maximum:,}</text>')
    body.append(f'<text x="24" y="{height-16}" class="small">Initial mismatches: {initial["failed"]:,}. Final mismatches: {final["failed"]:,}.</text>')
    body.append('</svg>')
    Path(output).write_text("\n".join(body) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--initial")
    parser.add_argument("--chart")
    args = parser.parse_args()
    cases = records()
    expected = [invoke(re, record) for record in cases]
    failures = []
    passed = {name: 0 for name in MODULES}
    for name in MODULES:
        module = importlib.import_module(name)
        for index, record in enumerate(cases):
            actual = invoke(module, record)
            if actual == expected[index]:
                passed[name] += 1
            else:
                failures.append({"case": index, "module": name, "record": shown(record), "expected": expected[index], "actual": actual})
    result = {"schema": "rebar-replacement-controls-v1", "cases_per_module": len(cases), "checks": len(cases) * len(MODULES), "modules": list(MODULES), "passed": passed, "failed": len(failures), "failures": failures}
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.chart:
        if not args.initial:
            raise ValueError("--chart requires --initial")
        initial = json.loads(Path(args.initial).read_text(encoding="utf-8"))
        chart(initial, result, args.chart)
    print(json.dumps({key: value for key, value in result.items() if key != "failures"}, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
