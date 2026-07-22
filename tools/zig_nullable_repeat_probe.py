#!/usr/bin/env python3
"""Differential nullable/nested-repeat and long-repeat checks for Zig."""

from __future__ import annotations

import argparse
import json
import random
import re
import signal
from pathlib import Path

from candidates import zig_candidate as zig


SEED = 2026073105


def value(item):
    if isinstance(item, bytes):
        return {"bytes_hex": item.hex()}
    if isinstance(item, tuple):
        return [value(part) for part in item]
    if isinstance(item, list):
        return [value(part) for part in item]
    if isinstance(item, dict):
        return {key: value(part) for key, part in item.items()}
    return item


def matched(item):
    if item is None:
        return None
    return {"span": item.span(), "groups": value(item.groups()), "lastindex": item.lastindex, "lastgroup": item.lastgroup}


def outcome(module, api, pattern, subject, flags):
    def timed_out(signum, frame):
        raise TimeoutError("nullable-repeat case exceeded 250 ms")

    previous = signal.signal(signal.SIGALRM, timed_out)
    signal.setitimer(signal.ITIMER_REAL, .25)
    try:
        compiled = module.compile(pattern, flags)
        if api == "search":
            result = matched(compiled.search(subject))
        elif api == "match":
            result = matched(compiled.match(subject))
        elif api == "fullmatch":
            result = matched(compiled.fullmatch(subject))
        elif api == "findall":
            result = value(compiled.findall(subject))
        elif api == "finditer":
            result = [matched(item) for item in compiled.finditer(subject)]
        elif api == "split":
            result = value(compiled.split(subject, 8))
        elif api == "subn":
            replacement = br"<\g<1>>" if compiled.groups and isinstance(pattern, bytes) else r"<\g<1>>" if compiled.groups else b"<x>" if isinstance(pattern, bytes) else "<x>"
            result = value(compiled.subn(replacement, subject, 8))
        else:
            scanner = compiled.scanner(subject)
            result = [matched(scanner.search()) for _ in range(9)]
        return {"metadata": [int(compiled.flags), compiled.groups, dict(compiled.groupindex)], "result": result}
    except Exception as exc:
        return {"error": type(exc).__name__, "message": getattr(exc, "msg", str(exc)), "position": getattr(exc, "pos", None), "display": str(exc)}
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--seeded-cases", type=int, default=16384)
    parser.add_argument("--long-length", type=int, default=50000)
    args = parser.parse_args()
    if args.seeded_cases < 0 or args.long_length < 1:
        raise ValueError("invalid control size")

    apis = ("search", "match", "fullmatch", "findall", "finditer", "split", "subn", "scanner")
    manual = [
        (r"(?:|a)*b", "aaab", 0), (r"(?:|a)*?b", "aaab", 0), (r"(?:|a)+b", "aaab", 0), (r"(?:|a)+?b", "aaab", 0),
        (r"(?:|a)*+b", "aaab", 0), (r"(?:|a)++b", "aaab", 0), (r"(?:|a)*z", "aaab", 0), (r"(?:a?)*b", "aaab", 0),
        (r"(?:a?)+b", "aaab", 0), (r"(?:a?)*?b", "aaab", 0), (r"(a?)*b", "aaab", 0), (r"(a?)*?b", "aaab", 0),
        (r"((?:|a)*)b", "aaab", 0), (r"(?:|a)*(?<!z)c", "aaac", 0), (r"(?:|a)*(?<=a)b", "aaab", 0),
        (r"(?:|a)*(?:|b)*c", "aaabbc", 0), (r"(?:(?:|a)*)*b", "aaab", 0), (r"(?:(a)?)*b", "aaab", 0),
        (r"(?:|é)*雪", "éé雪", 0), (r"(?:|雪)*?(?<!x)c", "雪雪c", 0),
        (br"(?:|a)*b", b"aaab", 0), (br"(?:|a)*?b", b"aaab", 0), (br"(a?)*b", b"aaab", 0), (br"(?:|a)*(?<!z)c", b"aaac", 0),
        (br"0*+(a)?(?(1)b|c)*+(?<!z)c|[^x\n]", b"X x0c\nZabc", re.IGNORECASE | re.LOCALE),
    ]
    failures = []
    checks = 0

    def check(kind, index, api, pattern, subject, flags):
        nonlocal checks
        expected = outcome(re, api, pattern, subject, flags)
        actual = outcome(zig, api, pattern, subject, flags)
        checks += 1
        if actual != expected:
            failures.append({"kind": kind, "index": index, "api": api, "pattern": repr(pattern), "subject": repr(subject)[:240], "flags": int(flags), "expected": expected, "actual": actual})

    for index, (pattern, subject, flags) in enumerate(manual):
        print(f"checking manual {index + 1}/{len(manual)}", flush=True)
        for api in apis:
            check("manual", index, api, pattern, subject, flags)

    long_subject = "x" * args.long_length
    long_cases = [
        (r"(x)*", long_subject, "match"), (r"(x)*y", long_subject + "y", "match"), (r"(x)*?y", long_subject + "y", "match"),
        (r".*?c", "ab" * (args.long_length // 2) + "cd", "match"), (r"(?:|x)*y", long_subject + "y", "match"),
    ]
    for index, (pattern, subject, api) in enumerate(long_cases):
        print(f"checking long {index + 1}/{len(long_cases)}", flush=True)
        check("long", index, api, pattern, subject, 0)

    rng = random.Random(SEED)
    nullable = (r"(?:|a)", r"(?:a?)", r"(?:|b)", r"(?:[ab]?)", r"(?:|é)", r"(?:|雪)", r"(a?)", r"(?:(a)?)")
    quantifiers = ("*", "*?", "*+", "+", "+?", "++", "{0,2}", "{0,2}?", "{0,2}+", "{1,3}", "{1,3}?")
    suffixes = ("b", "c", "[ab]", r"(?<!z)c", r"(?<=a)b", r"\b", "(?:x|y)")
    alphabet = list("aAbBcCxyz _-\\n") + ["é", "雪"]
    modes = (0, re.IGNORECASE, re.ASCII, re.MULTILINE, re.DOTALL)
    for index in range(args.seeded_cases):
        if index % 512 == 0:
            print(f"checking seeded {index}/{args.seeded_cases}", flush=True)
        pieces = []
        for _ in range(1):
            pieces.append(rng.choice(nullable))
            pieces.append(rng.choice(quantifiers))
        pieces.append(rng.choice(suffixes))
        pattern = "".join(pieces)
        subject = "".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 9)))
        if index % 4 == 0 and pattern.isascii() and subject.isascii():
            pattern, subject = pattern.encode("ascii"), subject.encode("ascii")
        check("seeded", index, apis[index % len(apis)], pattern, subject, rng.choice(modes))

    result = {"schema": "rebar-zig-nullable-repeat-v1", "seed": SEED, "manual_cases": len(manual), "long_cases": len(long_cases), "long_length": args.long_length, "seeded_cases": args.seeded_cases, "correctness_checks": checks, "failed": len(failures), "failures": failures}
    Path(args.output).write_text(json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "failures"}, sort_keys=True))
    for failure in failures[:30]:
        print(failure["kind"], failure["index"], failure["api"], failure["pattern"], failure["actual"].get("message", "value mismatch"))
    raise SystemExit(bool(failures))


if __name__ == "__main__":
    main()
