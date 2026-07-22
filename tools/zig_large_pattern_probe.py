#!/usr/bin/env python3
"""Differential checks for large patterns, compact repeats, and wide lookbehind."""

from __future__ import annotations

import argparse
import json
import random
import re
import signal
from pathlib import Path

from candidates import zig_candidate as zig


SEED = 2026073108
APIS = ("search", "match", "fullmatch", "findall", "finditer", "split", "subn", "scanner")
CASE_TIMEOUT = 1.5


def matched(value):
    if value is None:
        return None
    return {"span": value.span(), "groups": value.groups(), "lastindex": value.lastindex, "lastgroup": value.lastgroup}


def outcome(module, api, pattern, subject, flags):
    def timed_out(signum, frame):
        raise TimeoutError(f"large-pattern case exceeded {CASE_TIMEOUT:g} seconds")

    previous = signal.signal(signal.SIGALRM, timed_out)
    signal.setitimer(signal.ITIMER_REAL, CASE_TIMEOUT)
    try:
        compiled = module.compile(pattern, flags)
        if api == "compile":
            shown = repr(compiled)
            result = {"repr_under_300": len(shown) < 300, "repr_prefix": shown[:30], "repr_suffix": shown[-24:]}
        elif api == "search":
            result = matched(compiled.search(subject))
        elif api == "match":
            result = matched(compiled.match(subject))
        elif api == "fullmatch":
            result = matched(compiled.fullmatch(subject))
        elif api == "findall":
            result = compiled.findall(subject)
        elif api == "finditer":
            result = [matched(item) for item in compiled.finditer(subject)]
        elif api == "split":
            result = compiled.split(subject, 4)
        elif api == "subn":
            result = compiled.subn(r"<\1>" if compiled.groups else "<x>", subject, 4)
        else:
            scanner = compiled.scanner(subject)
            result = [matched(scanner.search()) for _ in range(5)]
        return {"metadata": [int(compiled.flags), compiled.groups, dict(compiled.groupindex)], "result": result}
    except Exception as exc:
        return {"error": type(exc).__name__, "message": getattr(exc, "msg", str(exc)), "position": getattr(exc, "pos", None)}
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def manual_cases():
    long_pattern = "Very " + "long " * 1000 + "pattern"
    for flags in (0, re.IGNORECASE):
        yield "long-repr", "compile", long_pattern, "", flags
    yield "long-match", "fullmatch", long_pattern, long_pattern, 0
    yield "long-miss", "search", long_pattern, long_pattern[:-1] + "!", 0
    alternatives = "|".join(str(item) for item in range(10000))
    yield "large-alternatives", "match", alternatives, "1000", 0
    yield "large-alternatives-miss", "search", alternatives, "letters-only", 0

    subject = "x" * 100000
    for count in (129, 187, 255, 512, 4096, 65535, 65536):
        yield f"dot-exact-{count}", "match", f".{{{count}}}", subject, 0
        yield f"dot-upper-{count}", "match", f".{{,{count}}}", subject, 0
        yield f"dot-lazy-{count}", "match", f".{{{count},}}?", subject, 0
    for atom in ("x", "[xy]", r"\w", "(?:x|y)"):
        yield f"atom-exact-{atom}", "match", f"{atom}{{4096}}", subject, 0
        yield f"atom-upper-{atom}", "fullmatch", f"{atom}{{,4096}}", "x" * 2048, 0
        yield f"atom-tail-{atom}", "search", f"{atom}{{129,255}}y", "-" + "x" * 187 + "y", 0

    for outer in ("{0,}", "*", "+", "{1,187}"):
        for inner in ("{0,}", "*", "?"):
            yield "nullable-captures", "match", f"^((x|y){inner}){outer}", "xyyzy", 0

    look_subject = "x" * 2500000
    yield "wide-positive-lookbehind", "search", r"(?<=((.{128}){128}){128})", look_subject, 0
    yield "wide-negative-lookbehind", "search", r"(?<!((.{128}){128}){128})", look_subject, 0
    for count in (2**7, 2**12, 2**16, 2**22):
        for shape in ((count, 1, 1), (1, count, 1), (1, 1, count)):
            for mark in ("=", "!"):
                yield f"lookbehind-compile-{count}", "compile", r"(?<%s((.{%d}){%d}){%d})" % (mark, *shape), "", 0
    for pattern in (
        r".{%d}" % 2**128,
        r".{,%d}" % 2**128,
        r".{%d,}?" % 2**128,
        r".{%d,%d}" % (2**129, 2**128),
        r"(?<=((.{%d}){%d}){%d})" % (2**22, 2**22, 2**22),
        r"(?<!((.{%d}){%d}){%d})" % (2**22, 2**22, 2**22),
    ):
        yield "oversized-error", "compile", pattern, "", 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--seeded-cases", type=int, default=8192)
    parser.add_argument("--case-timeout", type=float, default=1.5)
    args = parser.parse_args()
    if args.seeded_cases < 0 or args.case_timeout <= 0:
        raise ValueError("invalid control size or timeout")
    global CASE_TIMEOUT
    CASE_TIMEOUT = args.case_timeout

    failures = []
    checks = 0

    def check(kind, index, api, pattern, subject, flags):
        nonlocal checks
        expected = outcome(re, api, pattern, subject, flags)
        actual = outcome(zig, api, pattern, subject, flags)
        checks += 1
        if actual != expected:
            failures.append({"kind": kind, "index": index, "api": api, "pattern": pattern[:360], "pattern_length": len(pattern), "subject_length": len(subject), "flags": int(flags), "expected": expected, "actual": actual})

    manual = list(manual_cases())
    for index, (kind, api, pattern, subject, flags) in enumerate(manual):
        print(f"checking manual {index + 1}/{len(manual)} {kind}", flush=True)
        check(kind, index, api, pattern, subject, flags)

    rng = random.Random(SEED)
    atoms = ("x", ".", "[xy]", r"\w", "(?:x|y)")
    counts = (0, 1, 2, 3, 7, 31, 63, 64, 127, 128, 129, 160, 187, 255, 256, 511, 512)
    tails = ("",)
    flags = (0, re.IGNORECASE, re.DOTALL, re.MULTILINE)
    for index in range(args.seeded_cases):
        if index % 32 == 0:
            print(f"checking seeded {index}/{args.seeded_cases}", flush=True)
        atom = rng.choice(atoms)
        minimum = rng.choice(counts)
        maximum = max(minimum, rng.choice(counts))
        if index % 5 == 0:
            quantifier = f"{{{minimum}}}"
        elif index % 5 == 1:
            quantifier = f"{{,{maximum}}}"
        elif index % 5 == 2:
            quantifier = f"{{{minimum},{maximum}}}"
        elif index % 5 == 3:
            quantifier = f"{{{minimum},}}?"
        else:
            quantifier = f"{{{minimum},{maximum}}}+"
        child = atom if index % 4 else f"({atom})"
        pattern = child + quantifier + rng.choice(tails)
        api = APIS[index % len(APIS)]
        length = rng.choice((0, 1, 2, 7, 32, 128, 256, 512))
        if api == "fullmatch":
            length = max(minimum, length)
            if index % 5 in (1, 2, 4):
                length = min(maximum, length)
        subject = "x" * length
        check("seeded", index, api, pattern, subject, rng.choice(flags))

    result = {"schema": "rebar-zig-large-pattern-v1", "seed": SEED, "manual_cases": len(manual), "seeded_cases": args.seeded_cases, "correctness_checks": checks, "failed": len(failures), "failures": failures}
    Path(args.output).write_text(json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "failures"}, sort_keys=True))
    for failure in failures[:40]:
        actual = failure["actual"]
        print(failure["kind"], failure["index"], failure["api"], failure["pattern"][:100], actual.get("error", "value mismatch"), actual.get("message", ""))
    raise SystemExit(bool(failures))


if __name__ == "__main__":
    main()
