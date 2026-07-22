#!/usr/bin/env python3
"""Differential checks for Zig's compact and direct-scanning executor paths."""

from __future__ import annotations

import argparse
import importlib
import json
import random
import re
from pathlib import Path


SEED = 2026072203


def match_value(match):
    if match is None:
        return None
    return (match.span(), match.groups(), match.lastindex, match.lastgroup)


def check(module, pattern, subject, flags, failures, label):
    expected = re.compile(pattern, flags)
    candidate = module.compile(pattern, flags)
    checks = 0
    windows = ((0, len(subject)), (min(1, len(subject)), len(subject)), (0, max(0, len(subject) - 1)))
    replacement = b"<\\g<0>>" if isinstance(subject, bytes) else r"<\g<0>>"
    for pos, endpos in windows:
        actions = (
            ("search", lambda value: match_value(value.search(subject, pos, endpos))),
            ("match", lambda value: match_value(value.match(subject, pos, endpos))),
            ("fullmatch", lambda value: match_value(value.fullmatch(subject, pos, endpos))),
            ("findall", lambda value: value.findall(subject, pos, endpos)),
            ("finditer", lambda value: [match_value(item) for item in value.finditer(subject, pos, endpos)]),
        )
        for operation, action in actions:
            want = action(expected)
            got = action(candidate)
            checks += 1
            if want != got:
                failures.append({"label": label, "operation": operation, "pattern": repr(pattern), "subject": repr(subject), "flags": flags, "pos": pos, "endpos": endpos, "expected": repr(want), "actual": repr(got)})
    for operation, action in (
        ("split", lambda value: value.split(subject)),
        ("split-limited", lambda value: value.split(subject, 2)),
        ("sub", lambda value: value.sub(replacement, subject)),
        ("subn-limited", lambda value: value.subn(replacement, subject, 2)),
    ):
        want = action(expected)
        got = action(candidate)
        checks += 1
        if want != got:
            failures.append({"label": label, "operation": operation, "pattern": repr(pattern), "subject": repr(subject), "flags": flags, "expected": repr(want), "actual": repr(got)})
    return checks


def manual_cases():
    rows = [
        (r"(?:|[A-Za-z])*?(?=[:;])|\b|(?=,)", "alpha,beta: end", 0),
        (r"(?i)(?:|[a-z])*?(?=[:;])|\B|(?=[A-Z])", "α,aBc; Z", re.I),
        (r"(?=;)|\b", "a;b café", 0),
        (r"(?<!x)|\B", "xx,a", 0),
        (r"\b(?!skip_)[A-Za-z_][A-Za-z0-9_]*\b", "skip_one ready skip_two item_3 final", 0),
        (r"(?i)\b(?!no_)[a-z_][a-z0-9_]*\b", "NO_item good No_more READY", re.I),
        (r"([\"'])(.*?)\1", "first='one two' second=\"three\" bare=four", 0),
        (r"([ab])(.*?)\1", "a--a b-b a\n-a", 0),
        (r"(?i)([A-Z])(.*?)\1", "A..a K..k", re.I),
        (r"([\"'])(.*?)\1", "\"one\ntwo\" 'three'", re.S),
        (r"(?P<key>[A-Z]+):(?P<num>[0-9]+)", "DELTA:781 DELTA:782", 0),
        (r"([a-z]{1,5})=([0-9]{1,4})", "alpha=12 beta=002", 0),
        (r"([A-Za-z_]+)_(\d+?)", "item_123 other_4", 0),
        (r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?P<num>[0-9]+)", "prefix item_total : 730 suffix", 0),
        (r"([A-Z][A-Z0-9]*)\s*=\s*(\d+)", "AB2 = 901 C3=4", 0),
        (r"[A-Z]{2,8}_[0-9]+", "prefix DELTA_997 suffix", 0),
        (r"[A-Z]+?_[0-9]+?", "ABCDE_123 Z_4", 0),
        (r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "owner=x_2@demo.io; reply=help+us@mail.example.co", 0),
        (r"[a-z]+@[a-z.]+?\.[a-z]{1,3}?", "a@one.two.three b@x.io", 0),
        (r",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", "alpha,\"one,two\",bravo,\"three,four\",charlie", 0),
        (r",(?!(?:[^\"]*\"[^\"]*\")*[^\"]*$)", "alpha,\"one,two\",bravo,\"three,four\",charlie", 0),
        (r";(?=(?:[^']*'[^']*')*[^']*$)", "one;'two;three';four", 0),
    ]
    return rows + [(pattern.encode("ascii"), subject.encode("utf-8"), flags & ~re.UNICODE) for pattern, subject, flags in rows]


def generated(rng, index):
    family = index % 8
    flags = rng.choice((0, re.I, re.A, re.I | re.A))
    prefix = rng.choice(("skip_", "no_", "omit_"))
    separator = rng.choice((":", "=", "_"))
    quote = rng.choice(("\"", "'"))
    if family == 0:
        pattern = rf"\b(?!{prefix})[A-Za-z_][A-Za-z0-9_]*\b"
    elif family == 1:
        pattern = r"([\"'])(.*?)\1"
        flags |= rng.choice((0, re.S))
    elif family == 2:
        pattern = rf"(?P<key>[A-Z]+){separator}(?P<num>[0-9]+)"
    elif family == 3:
        pattern = rf"(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*{separator}\s*(?P<num>[0-9]+)"
    elif family == 4:
        pattern = rf"[A-Z]{{1,{rng.randrange(3, 9)}}}{separator}[0-9]+"
    elif family == 5:
        pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    elif family == 6:
        escaped = re.escape(quote)
        pattern = rf"{re.escape(separator)}(?=(?:[^{escaped}]*{escaped}[^{escaped}]*{escaped})*[^{escaped}]*$)"
    else:
        pattern = rf"(?:|[A-Za-z])*?(?=[{re.escape(separator)},])|\b|(?={re.escape(quote)})"
    alphabet = " abcXYZskip_NO0123_:@=,;.-+%'\"\nα雪"
    subject = "".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 100)))
    subject += rng.choice(("", f" {prefix}one ready", f" KEY{separator}128", " x_2@demo.io", f" {quote}one,two{quote}"))
    if index % 2:
        return pattern.encode("ascii"), subject.encode("utf-8"), flags
    return pattern, subject, flags


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
    for index, (pattern, subject, flags) in enumerate(manual):
        checks += check(module, pattern, subject, flags, failures, f"manual-{index}")
    rng = random.Random(args.seed)
    for index in range(args.seeded_cases):
        checks += check(module, *generated(rng, index), failures, f"seeded-{index}")
        if index and index % 1024 == 0:
            print(f"checked seeded {index}/{args.seeded_cases}", flush=True)
    result = {"schema": "rebar-zig-executor-probe-v1", "module": args.module, "seed": args.seed, "manual_cases": len(manual), "seeded_cases": args.seeded_cases, "correctness_checks": checks, "failed": len(failures), "failures": failures}
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "failures"}, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
