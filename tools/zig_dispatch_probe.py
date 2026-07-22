#!/usr/bin/env python3
"""Differential checks for Zig start dispatch, leading runs, and lazy delimiters."""

import argparse
import importlib
import json
import random
import re
from pathlib import Path


SEED = 2026080101
MANUAL = (
    (r"(cedar|birch|maple|willow|spruce|poplar|walnut|aspen|cherry|olive)_([0-9]{2})", "ordinary prose without a tree name", 0, 0, None),
    (r"(?i)(istanbul|sierra|kelvin|[A-Z]+)-([0-9]+)", "x \u0130STANBUL-7 y \u017fIERRA-8 z \u212aELVIN-9", 0, 0, None),
    (r"([A-F][0-9]+|[g-z][0-9]+|_[0-9]+)", "F12 g34 _56", 0, 0, None),
    (r"(?P<word>[A-Za-z_]+)-(?P<num>[0-9]+)", "prefix orbit_0-304 suffix", 0, 0, None),
    (r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?P<num>[0-9]+)", "prefix orbit_0 : 304 suffix", 0, 0, None),
    (r"START\n(?P<body>.*?)\nSTOP", "header\nSTART\none\ntwo\nSTOP\nfooter", re.DOTALL, 0, None),
    (r"(?s)(.*?)(?:END)Z", "x ENDq y ENDZ", 0, 0, None),
    (r"(?s)(.{1,20}?)END", "aa END xx", 0, 0, None),
    (r"(?s)(.*?)(\u96ea\u6b62)", "x\u96eax\u96ea\u6b62", 0, 0, None),
    (rb"(?s)(.*?)END", b"aa ENx bb END", 0, 0, None),
    (rb"(?P<word>[A-Za-z_]+)-(?P<num>[0-9]+)", bytearray(b"prefix orbit_0-304 suffix"), 0, 1, 22),
    (rb"(?s)(.*?)END", memoryview(b"xx aa ENx bb END yy"), 0, 3, 16),
)


def snapshot(value):
    if value is None:
        return None
    if hasattr(value, "span") and hasattr(value, "groups"):
        return {
            "span": value.span(),
            "groups": value.groups(),
            "groupdict": value.groupdict(),
            "lastindex": value.lastindex,
            "lastgroup": value.lastgroup,
            "regs": value.regs,
        }
    if isinstance(value, tuple):
        return tuple(snapshot(item) for item in value)
    if isinstance(value, list):
        return [snapshot(item) for item in value]
    return value


def captured(function):
    try:
        return ("ok", snapshot(function()))
    except Exception as exc:  # exact exception behavior is part of the comparison
        return ("error", type(exc).__name__, str(exc))


def generated(rng, index):
    token = rng.choice(("orbit", "cedar", "maple", "sierra", "kelvin", "fjord"))
    other = rng.choice(("direct", "quiet", "amber", "north", "plain"))
    number = rng.randrange(1, 9999)
    shape = index % 6
    if shape == 0:
        words = rng.sample(("cedar", "birch", "maple", "willow", "spruce", "poplar", "walnut", "aspen", "cherry", "olive"), 6)
        pattern = "(" + "|".join(words) + r")_([0-9]{1,4})"
        subject = f"{other} {token}_{number} ordinary {other}"
        flags = re.IGNORECASE if index % 4 == 0 else 0
    elif shape == 1:
        pattern = r"([A-F][0-9]+|[g-z][0-9]+|_[0-9]+|[\u0100-\u0108][0-9]+)"
        starter = rng.choice(("A", "F", "g", "z", "_", "\u0102"))
        subject = f"{other} {starter}{number} {token}"
        flags = re.IGNORECASE if index % 5 == 0 else 0
    elif shape == 2:
        pattern = r"(?P<word>[A-Za-z_]+)-(?P<num>[0-9]+)"
        interrupt = str(index % 10) if index % 2 else ""
        subject = f"prefix {token}_{interrupt}-{number} {other}"
        flags = 0
    elif shape == 3:
        pattern = r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?P<num>[0-9]+)"
        subject = f"prefix {token}_{index % 100} : {number} {other}"
        flags = re.VERBOSE if index % 5 == 0 else 0
    elif shape == 4:
        marker = rng.choice(("STOP", "END", "DONE"))
        pattern = r"START\n(?P<body>.*?)\n" + marker
        lines = "\n".join(f"{token} {other} {number + item}" for item in range(1 + index % 7))
        suffix = marker if index % 3 else marker[:-1] + "X"
        subject = "header\nSTART\n" + lines + "\n" + suffix + "\nfooter"
        flags = re.DOTALL
    else:
        marker = rng.choice((b"END", b"STOP", b"DONE"))
        pattern = rb"(?s)(.*?)" + marker
        body = (token + " " + other + " ").encode("ascii") * (1 + index % 6)
        suffix = marker if index % 4 else marker[:-1] + b"X"
        raw = b"xx " + body + suffix + b" yy"
        subject = (bytes, bytearray, memoryview)[index % 3](raw)
        flags = 0
    end = len(subject) - (1 if index % 11 == 0 and len(subject) else 0)
    pos = 1 if index % 13 == 0 and end else 0
    return pattern, subject, flags, pos, end


def operations(compiled, subject, pos, end):
    replacement = (lambda match: b"<" + match.group(0) + b">") if isinstance(compiled.pattern, bytes) else (lambda match: "<" + match.group(0) + ">")

    def scan():
        scanner = compiled.scanner(subject, pos, end)
        result = []
        while True:
            item = scanner.search()
            if item is None:
                return result
            result.append(item)

    return (
        ("search", lambda: compiled.search(subject, pos, end)),
        ("match", lambda: compiled.match(subject, pos, end)),
        ("fullmatch", lambda: compiled.fullmatch(subject, pos, end)),
        ("findall", lambda: compiled.findall(subject, pos, end)),
        ("finditer", lambda: list(compiled.finditer(subject, pos, end))),
        ("scanner", scan),
        ("split", lambda: compiled.split(subject, 2)),
        ("subn", lambda: compiled.subn(replacement, subject, 3)),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--module", default="rebar")
    parser.add_argument("--output", required=True)
    parser.add_argument("--seeded-cases", type=int, default=8192)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    candidate = importlib.import_module(args.module)
    rng = random.Random(args.seed)
    cases = list(MANUAL) + [generated(rng, index) for index in range(args.seeded_cases)]
    failures = []
    checks = 0
    for index, (pattern, subject, flags, pos, end) in enumerate(cases):
        actual_compile = captured(lambda: candidate.compile(pattern, flags))
        expected_compile = captured(lambda: re.compile(pattern, flags))
        checks += 1
        if actual_compile[0] != expected_compile[0]:
            failures.append({"case": index, "operation": "compile", "expected": repr(expected_compile), "actual": repr(actual_compile)})
            continue
        if actual_compile[0] == "error":
            if actual_compile != expected_compile:
                failures.append({"case": index, "operation": "compile-error", "expected": repr(expected_compile), "actual": repr(actual_compile)})
            continue
        actual = candidate.compile(pattern, flags)
        expected = re.compile(pattern, flags)
        metadata = (actual.pattern, actual.flags, actual.groups, dict(actual.groupindex))
        expected_metadata = (expected.pattern, expected.flags, expected.groups, dict(expected.groupindex))
        checks += 1
        if metadata != expected_metadata:
            failures.append({"case": index, "operation": "metadata", "expected": repr(expected_metadata), "actual": repr(metadata)})
        actual_operations = operations(actual, subject, pos, len(subject) if end is None else end)
        expected_operations = operations(expected, subject, pos, len(subject) if end is None else end)
        for (name, actual_call), (_, expected_call) in zip(actual_operations, expected_operations):
            got = captured(actual_call)
            want = captured(expected_call)
            checks += 1
            if got != want and len(failures) < 100:
                failures.append({"case": index, "operation": name, "expected": repr(want), "actual": repr(got), "pattern": repr(pattern), "subject": repr(subject)})
    result = {"schema": "rebar-zig-dispatch-probe-v1", "module": args.module, "seed": args.seed, "manual_cases": len(MANUAL), "seeded_cases": args.seeded_cases, "correctness_checks": checks, "failed": len(failures), "failures": failures}
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "failures"}, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
