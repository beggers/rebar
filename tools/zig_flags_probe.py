#!/usr/bin/env python3
"""Deterministic, differential checks for valid scoped regex flags in Zig."""

from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path

from candidates import zig_candidate as zig


SEED = 2026073102


def match_value(value):
    if value is None:
        return None
    return {"span": value.span(), "groups": value.groups(), "groupdict": value.groupdict(), "lastindex": value.lastindex, "lastgroup": value.lastgroup}


def operation(module, api, pattern, subject, flags):
    compiled = module.compile(pattern, flags)
    metadata = (compiled.flags, compiled.groups, dict(compiled.groupindex))
    if api == "search":
        value = match_value(compiled.search(subject))
    elif api == "match":
        value = match_value(compiled.match(subject))
    elif api == "fullmatch":
        value = match_value(compiled.fullmatch(subject))
    elif api == "findall":
        value = compiled.findall(subject)
    elif api == "finditer":
        value = [match_value(item) for item in compiled.finditer(subject)]
    elif api == "split":
        value = compiled.split(subject, 6)
    elif api == "subn":
        replacement = b"<x>" if isinstance(pattern, bytes) else "<x>"
        if compiled.groups:
            replacement = br"<\g<1>>" if isinstance(pattern, bytes) else r"<\g<1>>"
        value = compiled.subn(replacement, subject, 6)
    else:
        scanner = compiled.scanner(subject)
        value = [match_value(scanner.search()) for _ in range(8)]
    return metadata, value


def outcome(module, api, pattern, subject, flags):
    try:
        return {"value": operation(module, api, pattern, subject, flags)}
    except Exception as exc:
        return {"error": type(exc).__name__, "message": str(exc)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--seeded-cases", type=int, default=8192)
    args = parser.parse_args()
    if args.seeded_cases < 0:
        raise ValueError("invalid seeded case count")

    manual = [
        (r"(?s:a.b)", "a\nb", 0),
        (r"(?i:ab)(?-i:cd)", "ABcd", 0),
        (r"(?i:ab)(?-i:cd)", "ABCD", 0),
        (r"(?i:a)(?-i:b)(?i:c)", "AbC", 0),
        (r"(?-i:a)B", "aB", re.IGNORECASE),
        (r"(?-i:a)B", "AB", re.IGNORECASE),
        (r"(?i:(?-i:a)b)", "aB", 0),
        (r"(?m:^b$)", "a\nb\nc", 0),
        ("(?x: a # comment\n b )", "ab", 0),
        (r" a(?x: b) c", " ab c", 0),
        (r" a(?-x: b) c", "a bc", re.VERBOSE),
        (r"\w(?a:\W)\w", "ààà", 0),
        (r"(?a:\W(?u:\w)\W)", "ààà", 0),
        (r"\W(?u:\w)\W", "ààà", re.ASCII),
        (r"(?i:[a-z]+)(?-i:[A-Z]+)", "İıſKABC", 0),
        (r"(?s:(?=a.)a.)", "a\n", 0),
        (br"(?i:ab)(?-i:cd)", b"ABcd", 0),
        (br"(?s:a.b)", b"a\nb", 0),
        (br"(?m:^b$)", b"a\nb\nc", 0),
        (br"(?a:\w+)", b"\xffword_2", 0),
        (br"(?L:\w+)", b"word_2", 0),
    ]
    apis = ("search", "match", "fullmatch", "findall", "finditer", "split", "subn", "scanner")
    failures = []
    checks = 0
    for index, (pattern, subject, flags) in enumerate(manual):
        for api in apis:
            expected = outcome(re, api, pattern, subject, flags)
            actual = outcome(zig, api, pattern, subject, flags)
            checks += 1
            if actual != expected:
                failures.append({"kind": "manual", "index": index, "api": api, "pattern": repr(pattern), "subject": repr(subject), "flags": int(flags), "expected": expected, "actual": actual})

    rng = random.Random(SEED)
    atoms = (
        r"(?i:aB)",
        r"(?-i:aB)",
        r"(?s:.)",
        r"(?-s:.)",
        r"(?m:^a$)",
        r"(?-m:^a$)",
        r"(?x:a b)",
        r"(?-x:a b)",
        r"(?a:\w)",
        r"(?a:\W)",
        r"(?u:\w)",
        r"(?i:[a-z])",
        r"(?-i:[A-Z])",
        r"(?i:(?-i:a)b)",
        r"(?s:(?=a.)a.)",
        r"(?i:(a)b)\1",
    )
    quantifiers = ("", "?", "+", "{0,2}", "*?", "?+")
    joins = ("", "", "|", r"\b")
    modes = (0, re.IGNORECASE, re.ASCII, re.VERBOSE, re.DOTALL, re.MULTILINE, re.IGNORECASE | re.ASCII, re.IGNORECASE | re.VERBOSE)
    alphabet = list("aAbBcC09_,-. \t\n") + ["é", "ß", "雪", "٣", "İ", "ı", "ſ", "K", "\u0301", "\u2003", "☃", "😀"]
    for index in range(args.seeded_cases):
        pieces = []
        for _ in range(rng.randrange(1, 5)):
            pieces.append(rng.choice(atoms))
            pieces.append(rng.choice(quantifiers))
            pieces.append(rng.choice(joins))
        pattern = "".join(pieces)
        if pattern.endswith("|"):
            pattern += "a"
        subject = "".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 81)))
        flags = rng.choice(modes)
        api = apis[index % len(apis)]
        expected = outcome(re, api, pattern, subject, flags)
        actual = outcome(zig, api, pattern, subject, flags)
        checks += 1
        if actual != expected:
            failures.append({"kind": "seeded", "index": index, "api": api, "pattern": pattern, "subject": subject, "flags": int(flags), "expected": expected, "actual": actual})

    result = {"schema": "rebar-zig-flags-probe-v1", "seed": SEED, "manual_cases": len(manual), "seeded_cases": args.seeded_cases, "correctness_checks": checks, "failed": len(failures), "failures": failures}
    Path(args.output).write_text(json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "failures"}, sort_keys=True))
    for failure in failures[:20]:
        print(failure["kind"], failure["index"], failure["api"], failure["pattern"])
    raise SystemExit(bool(failures))


if __name__ == "__main__":
    main()
