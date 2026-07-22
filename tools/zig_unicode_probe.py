#!/usr/bin/env python3
"""Deterministic, differential Unicode checks for the from-scratch Zig engine."""

from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path

from candidates import zig_candidate as zig


SEED = 2026073101
CHUNK = 4096


def match_value(value):
    if value is None:
        return None
    return {
        "span": value.span(),
        "groups": value.groups(),
        "groupdict": value.groupdict(),
        "lastindex": value.lastindex,
        "lastgroup": value.lastgroup,
    }


def call(module, api, pattern, subject, flags):
    compiled = module.compile(pattern, flags)
    if api == "search":
        return match_value(compiled.search(subject))
    if api == "match":
        return match_value(compiled.match(subject))
    if api == "fullmatch":
        return match_value(compiled.fullmatch(subject))
    if api == "findall":
        return compiled.findall(subject)
    if api == "finditer":
        return [match_value(value) for value in compiled.finditer(subject)]
    if api == "split":
        return compiled.split(subject, 7)
    if api == "subn":
        replacement = "<x>" if compiled.groups == 0 else r"<\g<1>>"
        return compiled.subn(replacement, subject, 7)
    scanner = compiled.scanner(subject)
    return [match_value(scanner.search()) for _ in range(8)]


def outcome(module, api, pattern, subject, flags):
    try:
        return {"value": call(module, api, pattern, subject, flags)}
    except Exception as exc:  # differential evidence retains exact failures
        return {"error": type(exc).__name__, "message": str(exc)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--seeded-cases", type=int, default=4096)
    parser.add_argument("--membership-stride", type=int, default=1)
    args = parser.parse_args()
    if args.seeded_cases < 0 or args.membership_stride < 1:
        raise ValueError("invalid seeded case count or membership stride")

    failures = []
    checks = 0
    membership_patterns = [
        (r"\d", 0),
        (r"\D", 0),
        (r"\s", 0),
        (r"\S", 0),
        (r"\w", 0),
        (r"\W", 0),
        (r"\w", re.ASCII),
        (r"\W", re.ASCII),
        (r"[a-z]", re.IGNORECASE),
        (r"[A-Z]", re.IGNORECASE),
        (r"[^a-z]", re.IGNORECASE),
        (r"[\xc0-\xde]", re.IGNORECASE),
        (r"[\xe0-\xfe]", re.IGNORECASE),
        (r"[\u0400-\u042f]", re.IGNORECASE),
        (r"[\U00010400-\U00010427]", re.IGNORECASE),
        (r"[😀-🙏]", 0),
    ]
    for pattern, flags in membership_patterns:
        expected_pattern = re.compile(pattern, flags)
        actual_pattern = zig.compile(pattern, flags)
        for begin in range(0, 0x110000, CHUNK * args.membership_stride):
            subject = "".join(map(chr, range(begin, min(begin + CHUNK, 0x110000))))
            expected = expected_pattern.findall(subject)
            try:
                actual = actual_pattern.findall(subject)
            except Exception as exc:
                actual = {"error": type(exc).__name__, "message": str(exc)}
            checks += 1
            if actual != expected:
                failures.append({
                    "kind": "membership",
                    "pattern": pattern,
                    "flags": int(flags),
                    "begin": begin,
                    "expected_size": len(expected),
                    "actual_size": len(actual) if isinstance(actual, list) else None,
                    "actual": actual if not isinstance(actual, list) else actual[:20],
                    "expected": expected[:20],
                })

    rng = random.Random(SEED)
    alphabet = list("aAZ09_,-. \t\n") + ["é", "ß", "雪", "٣", "İ", "ı", "ſ", "K", "\u0301", "\u2003", "☃", "★", "😀", "🙏", "\ud800"]
    patterns = [
        r"café\+雪",
        r"\d+|\w+",
        r"\b\w+\b",
        r"\B\w+\B",
        r"\S{1,5}",
        r"[😀-🙏]+|\w+",
        r"[\u0100-\u024f]+",
        r"[\U0001f600-\U0001f64f]+",
        r"\N{SNOWMAN}+",
        r"(雪.)\1",
        r"(?P<word>\w+)[-](?P=word)",
        r"(?<!雪)\w+(?=★)",
        r"(?:é|ß|雪){0,3}?\w",
        r"[a-z]{1,6}",
        r"[^,\n]{1,8},",
        r"^.*$",
    ]
    apis = ("search", "match", "fullmatch", "findall", "finditer", "split", "subn", "scanner")
    modes = (0, re.ASCII, re.IGNORECASE, re.ASCII | re.IGNORECASE, re.MULTILINE, re.DOTALL)
    for index in range(args.seeded_cases):
        pattern = patterns[rng.randrange(len(patterns))]
        flags = modes[rng.randrange(len(modes))]
        api = apis[index % len(apis)]
        subject = "".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 97)))
        expected = outcome(re, api, pattern, subject, flags)
        actual = outcome(zig, api, pattern, subject, flags)
        checks += 1
        if actual != expected:
            failures.append({
                "kind": "seeded",
                "index": index,
                "api": api,
                "pattern": pattern,
                "flags": int(flags),
                "subject": subject,
                "expected": expected,
                "actual": actual,
            })

    case_groups = [
        (0x0069, 0x0131, 0x0130),
        (0x0073, 0x017f),
        (0x00b5, 0x03bc),
        (0x0345, 0x03b9, 0x1fbe),
        (0x0390, 0x1fd3),
        (0x03b0, 0x1fe3),
        (0x03b2, 0x03d0),
        (0x03b5, 0x03f5),
        (0x03b8, 0x03d1),
        (0x03ba, 0x03f0),
        (0x03c0, 0x03d6),
        (0x03c1, 0x03f1),
        (0x03c2, 0x03c3),
        (0x03c6, 0x03d5),
        (0x0432, 0x1c80),
        (0x0434, 0x1c81),
        (0x043e, 0x1c82),
        (0x0441, 0x1c83),
        (0x0442, 0x1c84, 0x1c85),
        (0x044a, 0x1c86),
        (0x0463, 0x1c87),
        (0xa64b, 0x1c88),
        (0x1e61, 0x1e9b),
        (0xfb05, 0xfb06),
    ]
    casefix_checks = 0
    for group in case_groups:
        for left in group:
            escaped = rf"\u{left:04x}" if left <= 0xffff else rf"\U{left:08x}"
            patterns = (escaped, f"[19{escaped}]", f"[{escaped}-{escaped}]")
            for right in group:
                for pattern in patterns:
                    subject = chr(right)
                    expected = outcome(re, "match", pattern, subject, re.IGNORECASE)
                    actual = outcome(zig, "match", pattern, subject, re.IGNORECASE)
                    checks += 1
                    casefix_checks += 1
                    if actual != expected:
                        failures.append({"kind": "case-equivalence", "pattern": pattern, "subject": subject, "expected": expected, "actual": actual})

    result = {
        "schema": "rebar-zig-unicode-probe-v1",
        "seed": SEED,
        "unicode_version": "16.0.0",
        "membership_patterns": len(membership_patterns),
        "codepoints": 0x110000,
        "chunk": CHUNK,
        "membership_stride": args.membership_stride,
        "seeded_cases": args.seeded_cases,
        "case_equivalence_checks": casefix_checks,
        "correctness_checks": checks,
        "failed": len(failures),
        "failures": failures,
    }
    Path(args.output).write_text(json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "failures"}, sort_keys=True))
    for failure in failures[:20]:
        print(failure["kind"], failure.get("pattern"), failure.get("index", failure.get("begin")))
    raise SystemExit(bool(failures))


if __name__ == "__main__":
    main()
