#!/usr/bin/env python3
"""Differential fixed-width lookbehind/reference checks for the Zig candidate."""

from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path

from candidates import zig_candidate as zig


SEED = 2026073104


def json_value(value):
    if isinstance(value, bytes):
        return {"bytes_hex": value.hex()}
    if isinstance(value, tuple):
        return [json_value(item) for item in value]
    if isinstance(value, list):
        return [json_value(item) for item in value]
    if isinstance(value, dict):
        return {key: json_value(item) for key, item in value.items()}
    return value


def match_value(value):
    if value is None:
        return None
    return {"span": value.span(), "groups": value.groups(), "groupdict": value.groupdict(), "lastindex": value.lastindex, "lastgroup": value.lastgroup}


def outcome(module, api, pattern, subject, flags):
    try:
        compiled = module.compile(pattern, flags)
        metadata = (int(compiled.flags), compiled.groups, dict(compiled.groupindex))
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
            replacement = br"<\g<1>>" if isinstance(pattern, bytes) else r"<\g<1>>"
            value = compiled.subn(replacement, subject, 6)
        else:
            scanner = compiled.scanner(subject)
            value = [match_value(scanner.search()) for _ in range(7)]
        return {"metadata": json_value(metadata), "value": json_value(value)}
    except Exception as exc:
        return {"error": type(exc).__name__, "message": getattr(exc, "msg", str(exc)), "position": getattr(exc, "pos", None), "pattern": repr(getattr(exc, "pattern", None)), "display": str(exc)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--seeded-cases", type=int, default=16384)
    args = parser.parse_args()
    if args.seeded_cases < 0:
        raise ValueError("invalid seeded case count")

    apis = ("search", "match", "fullmatch", "findall", "finditer", "split", "subn", "scanner")
    manual = [
        (r"(a)(?<=\1)b", "ab", 0),
        (r"(a)(?<!\1)b", "ab", 0),
        (r"(?P<x>ab)(?<=(?P=x))c", "abc abc", 0),
        (r"(a)a(?<=\1)c", "aac", 0),
        (r"(a)b(?<=\1)a", "abaa", 0),
        (r"(a)a(?<!\1)c", "aac", 0),
        (r"(a)b(?<!\1)a", "abaa", 0),
        (r"(ab|cd)(?<=\1)x", "abx cdx", 0),
        (r"([a-z]{2})(?<=\1)!", "ab! zz!", re.IGNORECASE),
        (r"(雪😀)(?<=\1)!", "雪😀!", 0),
        (r"(?P<x>é{2})(?<=(?P=x))!", "éé!", re.IGNORECASE),
        (r"(?:(a)|(x))b(?<=(?(2)x|b))c", "abc xbc", 0),
        (br"(a)(?<=\1)b", b"ab", 0),
        (br"(a)(?<!\1)b", b"ab", 0),
        (br"(?P<x>ab)(?<=(?P=x))c", b"abc abc", 0),
        (br"([a-z]{2})(?<=\1)!", b"ab! zz!", re.IGNORECASE),
    ]
    errors = [
        r"(a+)(?<=\1)b",
        r"(?P<x>a+)(?<=(?P=x))b",
        r"(ab|c)(?<=\1)x",
        r"(a)b(?<=(?(2)b|x))(c)",
        r"(a)b(?<=(.)\2)(c)",
        r"(a)b(?<=(?P<a>.)(?P=a))(c)",
        r"(a)b(?<=(a)(?(2)b|x))(c)",
        r"(a)b(?<=(.)(?<=\2))(c)",
    ]
    failures = []
    checks = 0
    for index, (pattern, subject, flags) in enumerate(manual):
        for api in apis:
            expected = outcome(re, api, pattern, subject, flags)
            actual = outcome(zig, api, pattern, subject, flags)
            checks += 1
            if actual != expected:
                failures.append({"kind": "manual", "index": index, "api": api, "pattern": repr(pattern), "subject": repr(subject), "flags": int(flags), "expected": expected, "actual": actual})
    for index, pattern in enumerate(errors):
        for value in (pattern, pattern.encode("ascii")):
            expected = outcome(re, "search", value, b"x" if isinstance(value, bytes) else "x", 0)
            actual = outcome(zig, "search", value, b"x" if isinstance(value, bytes) else "x", 0)
            checks += 1
            if actual != expected:
                failures.append({"kind": "error", "index": index, "api": "search", "pattern": repr(value), "subject": "x", "flags": 0, "expected": expected, "actual": actual})

    rng = random.Random(SEED)
    bodies = ("a", "ab", "a{2}", "[ab]{2}", "(?:ab|cd)", "(?:a|b){2}", "é", "雪", "😀", "(?:雪|é){2}", "(?i:ab)")
    fillers = ("", "a", "x", "-", " ", "\\n")
    tails = ("b", "x", "!", "[ab]", "(?:x|y)")
    modes = (0, re.IGNORECASE, re.ASCII, re.MULTILINE, re.DOTALL)
    alphabet = list("abABcdxy!-_ \\n") + ["é", "雪", "😀"]
    for index in range(args.seeded_cases):
        body = rng.choice(bodies)
        named = bool(index & 1)
        capture = f"(?P<x>{body})" if named else f"({body})"
        ref = "(?P=x)" if named else r"\1"
        look = "<=" if index & 2 else "<!"
        pattern = capture + rng.choice(fillers) + "(?" + look + ref + ")" + rng.choice(tails)
        subject = "".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 65)))
        if index % 4 == 0 and pattern.isascii() and subject.isascii():
            pattern, subject = pattern.encode("ascii"), subject.encode("ascii")
        flags = rng.choice(modes)
        api = apis[index % len(apis)]
        expected = outcome(re, api, pattern, subject, flags)
        actual = outcome(zig, api, pattern, subject, flags)
        checks += 1
        if actual != expected:
            failures.append({"kind": "seeded", "index": index, "api": api, "pattern": repr(pattern), "subject": repr(subject), "flags": int(flags), "expected": expected, "actual": actual})

    result = {"schema": "rebar-zig-lookbehind-refs-v1", "seed": SEED, "manual_cases": len(manual), "error_cases": len(errors) * 2, "seeded_cases": args.seeded_cases, "correctness_checks": checks, "failed": len(failures), "failures": failures}
    Path(args.output).write_text(json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "failures"}, sort_keys=True))
    for failure in failures[:30]:
        print(failure["kind"], failure["index"], failure["api"], failure["pattern"], failure["expected"].get("message"), failure["actual"].get("message"))
    raise SystemExit(bool(failures))


if __name__ == "__main__":
    main()
