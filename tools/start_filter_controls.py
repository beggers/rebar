#!/usr/bin/env python3
"""Deterministic differential controls for native start/class/repeat filters."""

import argparse
import json
import random
import re
from pathlib import Path

import rebar


SEED = 20260723
BRANCHES = ("amber", "birch", "cedar", "delta", "ember", "frost", "gold", "hazel", "iris", "jade")
ATOMS = ("a", "A", ".", r"\d", r"\w", "[ab]", "[aA0-3]", "[^x]", "[\u0130a]", "[\u0400-\u04ff]")
TAILS = ("", "x", "_", "[0-9]{2}", "(?:xy|z)", r"\b")
FLAGS = (0, re.IGNORECASE, re.ASCII, re.IGNORECASE | re.ASCII, re.DOTALL, re.MULTILINE)


def match_value(value):
    if value is None:
        return None
    return (value.span(), value.groups(), value.groupdict(), value.lastindex, value.lastgroup, value.pos, value.endpos)


def snapshot(module, pattern, text, flags, pos, end):
    compiled = module.compile(pattern, flags)
    replacement = r"<\1>" if compiled.groups else "<>"
    if isinstance(pattern, bytes):
        replacement = replacement.encode("ascii")
    return (
        compiled.groups,
        dict(compiled.groupindex),
        match_value(compiled.search(text, pos, end)),
        match_value(compiled.match(text, pos, end)),
        match_value(compiled.fullmatch(text, pos, end)),
        compiled.findall(text, pos, end),
        tuple(match_value(value) for value in compiled.finditer(text, pos, end)),
        compiled.split(text, 2),
        compiled.subn(replacement, text, 2),
    )


def outcome(call):
    try:
        return ("ok", snapshot(*call))
    except BaseException as error:
        return (type(error).__name__, str(error), getattr(error, "msg", None), getattr(error, "pos", None))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    rng = random.Random(SEED)
    failures = []
    cases = 0
    for index in range(1800):
        branches = rng.sample(BRANCHES, rng.randint(2, 7))
        first = rng.choice((
            "(?:" + "|".join(branches) + ")",
            "(" + "|".join(branches) + ")",
            "(?:" + rng.choice(ATOMS) + "?" + "|".join(branches) + ")",
            "(?:" + "|".join(value[: rng.randint(1, len(value))] for value in branches) + ")",
            "(?=" + branches[0][:2] + ")" + rng.choice(ATOMS) + "+",
            "(?:" + rng.choice(ATOMS) + "+|" + rng.choice(ATOMS) + "{1,3})",
        ))
        prefix = rng.choice(("", "^", r"\b", "(?:x)?", "(?<!x)"))
        tail = rng.choice(TAILS)
        pattern = prefix + first + tail
        alphabet = "abcedfghijlmnoprstuvxyzABCD0123_ \n\u0130\u0401\U0001f600"
        text = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 36)))
        if rng.randrange(4) == 0:
            text = text + rng.choice(branches) + rng.choice(("", "x", "_12"))
        byte_mode = rng.randrange(3) == 0
        if byte_mode:
            pattern = pattern.encode("ascii", "backslashreplace")
            text = text.encode("ascii", "ignore")
        flags = rng.choice(FLAGS)
        if byte_mode and flags & re.ASCII:
            flags ^= re.ASCII
        pos = rng.randint(0, len(text))
        end = rng.randint(pos, len(text))
        want = outcome((re, pattern, text, flags, pos, end))
        got = outcome((rebar, pattern, text, flags, pos, end))
        if got != want:
            failures.append({"case": index, "pattern": repr(pattern), "text": repr(text), "flags": int(flags), "pos": pos, "endpos": end, "expected": repr(want), "actual": repr(got)})
        cases += 1
    result = {"schema": "rebar-start-filter-controls-v1", "seed": SEED, "cases": cases, "checks": cases, "module": "rebar", "failed": len(failures), "failures": failures}
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "failures"}, sort_keys=True))
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
