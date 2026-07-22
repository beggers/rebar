#!/usr/bin/env python3
"""Differential pattern-error and valid-control checks for the Zig candidate."""

from __future__ import annotations

import argparse
import json
import random
import re
import importlib.util
from pathlib import Path

from candidates import zig_candidate as zig
from oracle.v2 import suite as v2
from oracle.v3 import suite as v3


SEED = 2026073103


def outcome(module, pattern, flags=0):
    try:
        compiled = module.compile(pattern, flags)
    except Exception as exc:
        return {
            "error": type(exc).__name__,
            "message": getattr(exc, "msg", str(exc)),
            "position": getattr(exc, "pos", None),
            "line": getattr(exc, "lineno", None),
            "column": getattr(exc, "colno", None),
            "pattern": repr(getattr(exc, "pattern", None)),
            "display": str(exc),
        }
    return {"compiled": True, "flags": int(compiled.flags), "groups": compiled.groups, "groupindex": dict(compiled.groupindex)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--seeded-cases", type=int, default=16384)
    args = parser.parse_args()
    if args.seeded_cases < 0:
        raise ValueError("invalid seeded case count")

    failures = []
    counts = {"frozen": 0, "official": 0, "seeded": 0, "valid": 0}

    def check(kind, index, pattern, flags=0):
        expected = outcome(re, pattern, flags)
        actual = outcome(zig, pattern, flags)
        counts[kind] += 1
        if actual != expected:
            failures.append({"kind": kind, "index": index, "pattern": repr(pattern), "flags": int(flags), "expected": expected, "actual": actual})

    frozen = [case for case in v2.cases() if case["id"].startswith(("error.pattern", "fuzz.invalid-pattern"))]
    frozen += [case for case in v3.cases() if case["id"].startswith("v3.hold.invalid-pattern")]
    for case in frozen:
        check("frozen", case["id"], case["pattern"])

    official = [
        "\\", r"\q", r"\X", r"\u123", r"\U0001234", r"\U00110000", r"\x1z", r"\567", r"\911",
        r"\N", r"\N{", r"\N{}", r"\N{not a character}",
        "[", "[^", "[a", "[a-", r"[\w-b]", r"[a-\w]", "[b-a]", r"[\567]", r"[\911]", r"[\x1z]",
        "(", ")", "(?:", "(?", "(?P", "(?Pxy)", "(?<", "(?<>)", "(?z)", "(?iz)",
        "(?P<bad-name>a)", "(?P<x>a)(?P<x>b)", "(?P=x)", r"(a)\2", r"(abc\1)",
        "()(?(0)a|b)", "()(?(-1)a|b)", "()(?(+1)a|b)", "()(?( 1 )a|b)", "()(?(1", "()(?(1)a", "()(?(1)a|b|c", "()(?(2)a)",
        "(?i-i:a)", "(?a-u:a)", "(?au:a)", "(?-", "(?-+", "(?-z", "(?-i", "(?-i)", "(?-i+", "(?-iz", "(?i:", "(?i", "(?i+", "(?iz", "a(?i)b",
        "*", "+", "?", "{1,2}", "(?:*)", "a**", "a+?*", "a{3,1}", "(?<=a+)b",
    ]
    official += ["\\" + code for code in "ceghijklmopqyCEFGHIJKLMNOPQRTVXY"]
    official += ["[\\" + code + "]" for code in "ceghijklmopqyzABCEFGHIJKLMNOPQRTVXYZ"]
    for outer_reps in ("*", "+", "?", "{1,2}"):
        for outer_mod in ("", "?", "+"):
            for inner_reps in ("*", "+", "?", "{1,2}"):
                for inner_mod in ("", "?", "+"):
                    if inner_mod + outer_reps not in ("?", "+"):
                        official.append("x" + inner_reps + inner_mod + outer_reps + outer_mod)
    source = Path(__file__).resolve().parents[1] / "oracle" / "cpython-3.14.6" / "re_tests.py"
    spec = importlib.util.spec_from_file_location("rebar_official_re_tests", source)
    historical = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(historical)
    official += [item[0] for item in historical.tests if len(item) >= 3 and item[2] == historical.SYNTAX_ERROR]
    for index, pattern in enumerate(official):
        check("official", index, pattern)
        if pattern.isascii():
            check("official", f"{index}.bytes", pattern.encode("ascii"))

    valid = [
        "", "a", "a|b", "(?:ab){0,2}", r"(?P<x>a)(?P=x)", r"(a)\1", r"(?<=ab)c", r"(?<!a)b",
        r"[a-z]", r"[9-a]", r"[\xc0-\xde]", r"[\u0430-\u045f]", r"[\U00010428-\U0001044f]", r"\N{SNOWMAN}",
        r"\0", r"\08", r"\01", r"\018", r"[\1]", r"[\08]", r"[\177]", r"[\377]",
        r"(?i:a)(?-i:b)", "(?x: a # comment\n b)", r"(?a:\w)(?u:\w)",
    ]
    for index, pattern in enumerate(valid):
        check("valid", index, pattern, re.IGNORECASE if index % 3 == 0 else 0)
        if pattern.isascii() and "\\u" not in pattern and "\\U" not in pattern and "\\N" not in pattern and "(?u:" not in pattern:
            check("valid", f"{index}.bytes", pattern.encode("ascii"), re.IGNORECASE if index % 3 == 0 else 0)

    rng = random.Random(SEED)
    forms = (
        lambda tail: r"\q" + tail,
        lambda tail: "[abc" + tail.replace("]", ""),
        lambda tail: "(" + tail,
        lambda tail: "a**" + tail,
        lambda tail: "a{3,1}" + tail,
        lambda tail: "(?P<x>a)(?P<x>b)" + tail,
        lambda tail: r"(a)\2" + tail,
        lambda tail: "(?<=a+)b" + tail,
        lambda tail: "a(?i)b" + tail,
        lambda tail: "(?P<bad-name>a)" + tail,
        lambda tail: "(?P=x)" + tail,
        lambda tail: "(?(99)a|b)" + tail,
        lambda tail: "(?i-i:a)" + tail,
        lambda tail: "(?a-u:a)" + tail,
        lambda tail: r"[\x1]" + tail,
        lambda tail: tail + r"\x1",
        lambda tail: "()(?(1)a|b|c" + tail,
        lambda tail: r"(abc\1)" + tail,
    )
    tails = ("", "x", "|z", "(?:ab)", "\nxy", "\n# note\nq", r"\t", "[0-9]")
    prefixes = ("", "", "\n", "ab\n", "(?:x)\n")
    for index in range(args.seeded_cases):
        pattern = rng.choice(prefixes) + rng.choice(forms)(rng.choice(tails))
        if index % 4 == 0:
            pattern = pattern.encode("ascii")
        check("seeded", index, pattern)

    result = {"schema": "rebar-zig-pattern-errors-v1", "seed": SEED, "seeded_cases": args.seeded_cases, "correctness_checks": sum(counts.values()), "counts": counts, "failed": len(failures), "failures": failures}
    Path(args.output).write_text(json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "failures"}, sort_keys=True))
    for failure in failures[:30]:
        print(failure["kind"], failure["index"], failure["pattern"], failure["expected"].get("message"), failure["actual"].get("message"))
    raise SystemExit(bool(failures))


if __name__ == "__main__":
    main()
