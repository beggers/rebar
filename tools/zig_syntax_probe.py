#!/usr/bin/env python3
"""Differential checks for Zig comments, braces, octal escapes, and forward references."""

from __future__ import annotations

import argparse
import json
import random
import re
import signal
from pathlib import Path

from candidates import zig_candidate as zig


SEED = 2026073106
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
        raise TimeoutError("syntax case exceeded 250 ms")

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
    args = parser.parse_args()
    if args.seeded_cases < 0:
        raise ValueError("invalid control size")

    manual = [
        (r"w(?# comment 1)xy(?# comment 2)z", "-wxyz-", 0),
        (r"a(?#x)y", "ayay", re.IGNORECASE),
        (r"(a)(?# comment)(b)", "abxab", 0),
        (br"w(?# comment 1)xy(?# comment 2)z", b"-wxyz-", 0),
        (r"a(?#x", "a", 0),
        (br"a(?#x", b"a", 0),
        (r"x{}", "xx{} x{}", 0),
        (r"x{}+", "x{} x{}}", 0),
        (r"^x{}+$", "x{}", 0),
        (r"x{a}", "x{a} xx", 0),
        (r"x{2,a}", "x{2,a}", 0),
        (r"x{,a}", "x{,a}", 0),
        (r"x{2,}", "x xx xxx", 0),
        (r"x{,2}?", "xxx", 0),
        (r"x{2,1}", "xxx", 0),
        (r"^{a}", "{a}", 0),
        (r"\141", "zaaz", 0),
        (r"\1410", "za0z", 0),
        (r"\377", "\xff", 0),
        (r"\400", "", 0),
        (r"\567", "", 0),
        (r"\119", "", 0),
        (r"(a)(b)(c)(d)(e)(f)(g)(h)(i)(j)(k)(l)\119", "abcdefghijklk9", 0),
        (br"\141", b"zaaz", 0),
        (br"\1410", b"za0z", 0),
        (br"\377", b"\xff", 0),
        (br"\400", b"", 0),
        (r"(a)b(?=(?(2)x|c))(c)", "abc abcc", 0),
        (r"(a)b(?=(?(2)b|x))(c)", "abc abcc", 0),
        (r"(?(1)a|b)(a)?", "ba aa", 0),
        (r"(?(2)a|b)(a)?", "ba aa", 0),
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
        for api in APIS:
            check("manual", index, api, pattern, subject, flags)

    octal_checks = 0
    for number in range(256):
        for byte_mode in (False, True):
            escaped = f"\\{number:03o}"
            literal = chr(number)
            for suffix in ("", "0", "8"):
                pattern = escaped + suffix
                subject = "!" + literal + suffix + "!"
                if byte_mode:
                    pattern, subject = pattern.encode("ascii"), subject.encode("latin1")
                api = APIS[(number + len(suffix) + byte_mode) % len(APIS)]
                check("octal", octal_checks, api, pattern, subject, 0)
                octal_checks += 1

    rng = random.Random(SEED)
    brace_forms = ("{}", "{}+", "{a}", "{,a}", "{2,a}", "{2}", "{,2}", "{1,3}", "{0,3}?", "{1,3}+", "{2,1}")
    comments = ("", "(?#x)", "(?# space and 123)")
    endings = ("", "b", "[ab]", "(?=b)b", "(?:(?(2)b|c))(b)?")
    modes = (0, re.IGNORECASE, re.ASCII, re.MULTILINE, re.DOTALL)
    for index in range(args.seeded_cases):
        if index % 1024 == 0:
            print(f"checking seeded {index}/{args.seeded_cases}", flush=True)
        atom = rng.choice(("a", "b", "[ab]", "(?:a|b)", "(a)"))
        pattern = atom + rng.choice(brace_forms) + rng.choice(comments) + rng.choice(endings)
        subject = "".join(rng.choice("aAbB{} ,012x-") for _ in range(rng.randrange(0, 12)))
        flags = rng.choice(modes)
        if index % 4 == 0 and pattern.isascii() and subject.isascii():
            pattern, subject = pattern.encode("ascii"), subject.encode("ascii")
        check("seeded", index, APIS[index % len(APIS)], pattern, subject, flags)

    result = {"schema": "rebar-zig-syntax-v1", "seed": SEED, "manual_cases": len(manual), "octal_checks": octal_checks, "seeded_cases": args.seeded_cases, "correctness_checks": checks, "failed": len(failures), "failures": failures}
    Path(args.output).write_text(json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: item for key, item in result.items() if key != "failures"}, sort_keys=True))
    for failure in failures[:40]:
        print(failure["kind"], failure["index"], failure["api"], failure["pattern"], failure["actual"].get("message", "value mismatch"))
    raise SystemExit(bool(failures))


if __name__ == "__main__":
    main()
