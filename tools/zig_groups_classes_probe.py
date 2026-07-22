#!/usr/bin/env python3
"""Differential checks for many captures, Unicode group names, and large character sets."""

from __future__ import annotations

import argparse
import json
import random
import re
import signal
from pathlib import Path

from candidates import zig_candidate as zig


SEED = 2026073107
APIS = ("search", "match", "fullmatch", "findall", "finditer", "split", "subn", "scanner")


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
        raise TimeoutError("groups/classes case exceeded 500 ms")

    previous = signal.signal(signal.SIGALRM, timed_out)
    signal.setitimer(signal.ITIMER_REAL, .5)
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
            result = value(compiled.split(subject, 4))
        elif api == "subn":
            reference = min(compiled.groups, 200)
            replacement = f"<\\g<{reference}>>" if compiled.groups else "<x>"
            if isinstance(pattern, bytes):
                replacement = replacement.encode("ascii")
            result = value(compiled.subn(replacement, subject, 4))
        else:
            scanner = compiled.scanner(subject)
            result = [matched(scanner.search()) for _ in range(5)]
        return {"metadata": [int(compiled.flags), compiled.groups, dict(compiled.groupindex)], "result": result}
    except Exception as exc:
        return {"error": type(exc).__name__, "message": getattr(exc, "msg", str(exc)), "position": getattr(exc, "pos", None), "display": str(exc)}
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def named_alternatives(count):
    body = "|".join(f"x(?P<a{item}>{item:x})y" for item in range(1, count + 1))
    return f"(?:{body})(?({count})z|t)"


def large_set(count, negative=False):
    marks = "".join(chr(256 + item * 255) for item in range(count))
    return "[^" + marks + "]" if negative else "[" + marks + "]"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--seeded-cases", type=int, default=8192)
    args = parser.parse_args()
    if args.seeded_cases < 0:
        raise ValueError("invalid control size")

    manual = []
    valid_names = ("µ", "𝔘𝔫𝔦𝔠𝔬𝔡𝔢", "雪", "é_٣", "a\u0301", "名前2")
    for name in valid_names:
        manual.append((f"(?P<{name}>x)(?P={name})(?({name})y|z)", "-xxy-xxz-", 0))
    for name in ("😀", "¹", "a-b", " a", "a b"):
        manual.append((f"(?P<{name}>x)", "x", 0))
    for count in (1, 63, 127, 128, 129, 160, 200, 255):
        manual.append(("".join("(x)" for _ in range(count)), "x" * count, 0))
    for count in (129, 160, 200):
        target = count
        subject = f"x{target:x}yz"
        manual.append((named_alternatives(count), subject, 0))
    for count in (1, 63, 64, 65, 128, 255, 256):
        target = chr(256 + (count - 1) * 255)
        manual.append((large_set(count), "-" + target + "-", 0))
        manual.append((large_set(count, True), target + "A", 0))
    manual.extend((
        ("(" + large_set(256) + ")", "\uff01", 0),
        ("(?P<µ>" + large_set(256) + ")(?P=µ)", "\uff01\uff01", 0),
        (br"(?P<a200>x)(?P=a200)(?(a200)y|z)", b"-xxy-xxz-", 0),
    ))

    failures = []
    checks = 0

    def check(kind, index, api, pattern, subject, flags):
        nonlocal checks
        expected = outcome(re, api, pattern, subject, flags)
        actual = outcome(zig, api, pattern, subject, flags)
        checks += 1
        if actual != expected:
            failures.append({"kind": kind, "index": index, "api": api, "pattern": repr(pattern)[:360], "pattern_length": len(pattern), "subject": repr(subject)[:240], "flags": int(flags), "expected": expected, "actual": actual})

    for index, (pattern, subject, flags) in enumerate(manual):
        print(f"checking manual {index + 1}/{len(manual)}", flush=True)
        for api in APIS:
            check("manual", index, api, pattern, subject, flags)

    membership_checks = 0
    for count in (65, 128, 256):
        pattern = large_set(count)
        compiled_expected = re.compile(pattern)
        compiled_actual = zig.compile(pattern) if outcome(zig, "search", pattern, "", 0).get("error") is None else None
        for item in range(count):
            subject = chr(256 + item * 255)
            expected = bool(compiled_expected.fullmatch(subject))
            actual = bool(compiled_actual.fullmatch(subject)) if compiled_actual is not None else None
            checks += 1
            membership_checks += 1
            if actual != expected:
                failures.append({"kind": "membership", "index": item, "api": "fullmatch", "pattern": f"large-set-{count}", "pattern_length": len(pattern), "subject": repr(subject), "flags": 0, "expected": expected, "actual": actual})

    rng = random.Random(SEED)
    counts = (1, 8, 32, 63, 64, 65, 96, 128, 129, 160, 200, 255, 256)
    flags = (0, re.IGNORECASE, re.ASCII, re.MULTILINE)
    for index in range(args.seeded_cases):
        if index % 512 == 0:
            print(f"checking seeded {index}/{args.seeded_cases}", flush=True)
        count = rng.choice(counts)
        if index % 3 == 0:
            pattern = large_set(count, index % 2 == 0)
            target = chr(256 + rng.randrange(count) * 255)
            subject = target + rng.choice(("", "A", "雪"))
        elif index % 3 == 1:
            groups = min(count, 255)
            pattern = "".join("(x)" for _ in range(groups))
            subject = "x" * groups
        else:
            name = rng.choice(valid_names)
            pattern = f"(?P<{name}>[A-Za-z]+)(?P={name})"
            word = rng.choice(("a", "ab", "XY", "Maple"))
            subject = word + word
        check("seeded", index, APIS[index % len(APIS)], pattern, subject, rng.choice(flags))

    result = {"schema": "rebar-zig-groups-classes-v1", "seed": SEED, "manual_cases": len(manual), "membership_checks": membership_checks, "seeded_cases": args.seeded_cases, "correctness_checks": checks, "failed": len(failures), "failures": failures}
    Path(args.output).write_text(json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: item for key, item in result.items() if key != "failures"}, sort_keys=True))
    for failure in failures[:40]:
        print(failure["kind"], failure["index"], failure["api"], failure["pattern"][:120], failure.get("actual", {}).get("message", "value mismatch") if isinstance(failure.get("actual"), dict) else "value mismatch")
    raise SystemExit(bool(failures))


if __name__ == "__main__":
    main()
