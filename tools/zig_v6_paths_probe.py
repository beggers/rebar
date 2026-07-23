#!/usr/bin/env python3
"""Differential checks for Zig's literal, prefix-choice, class, and line paths."""

from __future__ import annotations

import argparse
import importlib
import json
import random
import re
from pathlib import Path


SEED = 2026072301


def match_value(value):
    if value is None:
        return None
    return value.span(), value.groups(), value.lastindex, value.lastgroup


def check(module, pattern, subject, flags, label, failures):
    expected = re.compile(pattern, flags)
    candidate = module.compile(pattern, flags)
    length = len(subject)
    windows = ((0, length), (min(1, length), length), (0, max(0, length - 1)), (min(3, length), max(0, length - 2)))
    checks = 0
    for pos, endpos in windows:
        calls = (
            ("search", lambda item: match_value(item.search(subject, pos, endpos))),
            ("match", lambda item: match_value(item.match(subject, pos, endpos))),
            ("fullmatch", lambda item: match_value(item.fullmatch(subject, pos, endpos))),
            ("findall", lambda item: item.findall(subject, pos, endpos)),
            ("findall-keywords", lambda item: item.findall(string=subject, pos=pos, endpos=endpos)),
            ("finditer", lambda item: [match_value(value) for value in item.finditer(subject, pos, endpos)]),
        )
        for operation, action in calls:
            want = action(expected)
            got = action(candidate)
            checks += 1
            if got != want:
                failures.append({"label": label, "operation": operation, "pattern": repr(pattern), "subject": repr(subject), "flags": flags, "pos": pos, "endpos": endpos, "expected": repr(want), "actual": repr(got)})
    replacement = b"<\\g<0>>" if isinstance(pattern, bytes) else r"<\g<0>>"
    for operation, action in (
        ("split", lambda item: item.split(subject)),
        ("split-limited", lambda item: item.split(subject, 2)),
        ("sub", lambda item: item.sub(replacement, subject)),
        ("subn-limited", lambda item: item.subn(replacement, subject, 2)),
    ):
        want = action(expected)
        got = action(candidate)
        checks += 1
        if got != want:
            failures.append({"label": label, "operation": operation, "pattern": repr(pattern), "subject": repr(subject), "flags": flags, "expected": repr(want), "actual": repr(got)})
    return checks


def manual_cases():
    rows = [
        (r"(?:read|reader|reading|ready|reason|record|recover|reduce|remove|remote|render|repair|repeat|report|request|reset)(?:[-_][0-9]{1,6})?", "read-1 reader-2 reading-3 ready-4 reason-5 reset-6", 0),
        (r"(?i)(?:read|reader|reading|ready|reason|record|recover|reduce|remove|remote|render|repair|repeat|report|request|reset)(?:[-_][0-9]{1,6})?", "READ-1 Reader-2 ReAdInG-3 READY-4 REASON-5 RESET-6", re.I),
        (r"(?:ab|abc|abcd)c", "abc abcc abcdc xabc", 0),
        (r"(?:prefix|prefixes|prefixing|prefixed)(?:es|ing|ed)?!", "prefix! prefixes! prefixing! prefixed!", 0),
        (r"(?:aa|aaa|aaaa)b", "aab aaab aaaab aaaaab", 0),
        (r"(?i)(?:ki|kin|kind|kilo|kiss|kite|skip|skin)", "KI Kind KILO KI ſkin İi", re.I),
        (r"(?i)(?<![A-Za-z0-9_.-])(?:README|LICENSE|[A-Za-z0-9_.-]+\.(?:py|rs|zig|c|h|json|ya?ml|md|txt))(?![A-Za-z0-9_.-])", "README LICENSE readme.md alpha_4.ZIG beta-7.Json no/file", re.I),
        (r"(?<![A-Za-z0-9_])(?:[$€£][0-9]+(?:,[0-9]{3})*(?:\.[0-9]{2})?|[-+]?[0-9]+(?:\.[0-9]+)?(?:ms|s|KB|MB|GiB|%))(?![A-Za-z0-9_])", "$1,234.00 €88.01 £7 1.5MS 9kb 2GiB 30% x9MB", re.I),
        (r"(?m)^\s*(?P<word>\w+(?:[’\'-]\w+)*)\s+(?P<num>\d+)\s*$", "alpha café Straße العربية 雪_1 11\nready 22\nO’Neill ٣٣\ncan't 44", re.M),
        (r"(?m)^\s*(?:alpha|alphabet|alpine|alps)\s*$", "x\nalphabet\n  alpine  \ny\nalps", re.M),
        (r"^abc", "xabc\nabc", 0),
        (r"(?m)^abc", "xabc\nabc\nabc", re.M),
        ("café", "café caféine café 雪café", 0),
        ("雪山", "雪山 x雪山 雪山雪山", 0),
        ("\x00x", "a\x00x b\x00x", 0),
        ("a a", "a a a a a  a", re.M),
        (r"[A-Z]+", "ABC xyz KİſK", re.I),
        (r"(?a:[A-Z]+)|(?u:[A-Z]+)", "ABC İſK xyz", re.I),
        (r"(?i:[a-z]+)(?-i:[A-Z]+)", "abCD ABcd xyZZ", 0),
    ]
    encoded = []
    for pattern, subject, flags in rows:
        try:
            byte_pattern = pattern.encode("ascii")
            byte_subject = subject.encode("utf-8")
            byte_flags = flags & ~re.UNICODE
            re.compile(byte_pattern, byte_flags)
            encoded.append((byte_pattern, byte_subject, byte_flags))
        except (UnicodeEncodeError, re.error):
            continue
    many = "(?:" + "|".join(f"prefix{index:03d}" for index in range(300)) + ")!"
    rows.append((many, "prefix000! prefix128! prefix299! prefix300!", 0))
    return rows + encoded


def generated(rng, index):
    family = index % 5
    flags = rng.choice((0, re.I, re.A, re.I | re.A, re.M, re.I | re.M))
    if family == 0:
        prefix = rng.choice(("pre", "read", "alpha", "ki", "ss"))
        count = rng.randrange(2, 30)
        endings = ["".join(rng.choice("abcdeinorst012") for _ in range(rng.randrange(0, 7))) for _ in range(count)]
        words = [prefix + ending for ending in endings]
        tail = rng.choice(("", "!", "[0-9]", "(?:x|xy)", "(?:[-_][0-9]{1,3})?"))
        pattern = "(?:" + "|".join(map(re.escape, words)) + ")" + tail
        subject = " ".join(rng.choice(words).swapcase() + rng.choice(("", "!", "x", "xy", "-12")) for _ in range(rng.randrange(1, 24)))
    elif family == 1:
        atom = rng.choice((r"[A-Za-z0-9_.-]", r"[A-Z]", r"[0-9]", r"[^,;\s]", r"[a-z_]", r"[\u0100-\u04ff]"))
        prefix = rng.choice(("", r"(?<![A-Za-z0-9_])", r"\b"))
        suffix = rng.choice(("", r"(?![A-Za-z0-9_])", r"\b"))
        pattern = prefix + atom + rng.choice(("+", "{1,8}", "*")) + suffix
        alphabet = " abcXYZ019_.,;-İıſKßΩ雪"
        subject = "".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 100)))
    elif family == 2:
        flags |= re.M
        atom = rng.choice((r"[A-Za-z]+", r"\w+", r"[^\n]+", r"(?:cat|catalog|cater)", r"(?P<word>\w+(?:[-']\w+)*)"))
        pattern = "(?m)^" + rng.choice(("", r"\s*")) + atom + rng.choice(("", r"\s+[0-9]+", r"\s+(?P<num>\d+)")) + rng.choice(("$", r"\s*$"))
        lines = ["".join(rng.choice(" abcXYZ019_-'.İſK雪") for _ in range(rng.randrange(0, 45))) for _ in range(rng.randrange(1, 18))]
        subject = "\n".join(lines)
    elif family == 3:
        alphabet = "abcXYZ019 _-café雪😀\x00"
        literal = "".join(rng.choice(alphabet) for _ in range(rng.randrange(1, 9)))
        pattern = literal
        subject = rng.choice((" ", "|", "")).join(literal if rng.randrange(4) else "".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 14))) for _ in range(rng.randrange(0, 48)))
        flags &= ~(re.I | re.X)
    else:
        pattern = rng.choice((r"(?i)[a-z]+", r"(?i)(?:ki|kin|kind|skip|skin)", r"(?i)[A-Z]{1,8}", r"(?i)[^A-Z\s]+"))
        subject = " ".join(rng.choice(("KELVIN", "Kelvin", "ſignal", "İSTANBUL", "ıota", "Straße", "ABC", "xyz")) for _ in range(rng.randrange(1, 30)))
    if index % 4 == 1 and "\\u" not in pattern and "(?u:" not in pattern:
        try:
            pattern = pattern.encode("ascii")
            subject = subject.encode("utf-8")
            flags &= ~re.UNICODE
        except UnicodeEncodeError:
            pass
    if isinstance(pattern, bytes) and index % 8 in (1, 5):
        subject = bytearray(subject) if index % 8 == 1 else memoryview(subject)
    return pattern, subject, flags


def error_surface(module):
    expected_text = re.compile("abc")
    actual_text = module.compile("abc")
    expected_bytes = re.compile(b"abc")
    actual_bytes = module.compile(b"abc")
    calls = (
        ("missing", lambda item: item.findall()),
        ("too-many", lambda item: item.findall("abc", 0, 3, 4)),
        ("unknown-keyword", lambda item: item.findall("abc", other=1)),
        ("duplicate-string", lambda item: item.findall("abc", string="abc")),
        ("duplicate-pos", lambda item: item.findall("abc", 0, pos=0)),
        ("bad-pos", lambda item: item.findall("abc", "0")),
        ("wrong-subject", lambda item: item.findall(b"abc")),
    )
    rows = []
    for label, action in calls:
        results = []
        for value in (expected_text, actual_text):
            try:
                action(value)
                results.append((None, None))
            except BaseException as error:
                results.append((type(error).__name__, str(error)))
        rows.append({"label": label, "expected": results[0], "actual": results[1], "passed": results[0][0] == results[1][0]})
    for label, action in (("bytes-wrong-subject", lambda item: item.findall("abc")), ("bytes-noncontiguous", lambda item: item.findall(memoryview(b"aabbcc")[::2]))):
        results = []
        for value in (expected_bytes, actual_bytes):
            try:
                action(value)
                results.append((None, None))
            except BaseException as error:
                results.append((type(error).__name__, str(error)))
        rows.append({"label": label, "expected": results[0], "actual": results[1], "passed": results[0][0] == results[1][0]})
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--module", default="rebar")
    parser.add_argument("--output", required=True)
    parser.add_argument("--seeded-cases", type=int, default=8192)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    module = importlib.import_module(args.module)
    failures = []
    checks = 0
    manual = manual_cases()
    for index, case in enumerate(manual):
        checks += check(module, *case, f"manual-{index}", failures)
    rng = random.Random(args.seed)
    for index in range(args.seeded_cases):
        checks += check(module, *generated(rng, index), f"seeded-{index}", failures)
        if index and index % 1024 == 0:
            print(f"checked seeded {index}/{args.seeded_cases}", flush=True)
    errors = error_surface(module)
    failures.extend({"label": "error-" + row["label"], "expected": row["expected"], "actual": row["actual"]} for row in errors if not row["passed"])
    result = {"schema": "rebar-zig-v6-paths-probe-v1", "module": args.module, "seed": args.seed, "manual_cases": len(manual), "seeded_cases": args.seeded_cases, "correctness_checks": checks + len(errors), "error_surface": errors, "failed": len(failures), "failures": failures}
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key not in {"failures", "error_surface"}}, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
