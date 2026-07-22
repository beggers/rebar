#!/usr/bin/env python3
"""Differential checks for compact lookaround and zero-width native paths."""

import argparse
import json
import random
import re
from pathlib import Path

import rebar


SEED = 20260725
PATTERNS = (
    r"(?=;)|\b",
    r"(?=\s)|\B",
    r"\b(?!skip_)[A-Za-z_][A-Za-z0-9_]*\b",
    r"(?<!\\)#[A-Za-z_]+",
    r"(?<=ID:)[A-Z]{2}[0-9]+",
    r"(?=(?P<word>[A-Za-z]+):)[A-Za-z]+",
    r",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)",
    r"(?:(?=ab)a|b)+",
    r"(?:^|(?<=;))(?P<key>[A-Za-z]+)(?=[:=])",
    r"(?!bad)(?P<value>[A-Za-z]+)(?<!x)",
)


def snapshot(value):
    if value is None:
        return None
    if hasattr(value, "span"):
        return {"span": list(value.span()), "groups": list(value.groups()), "lastindex": value.lastindex}
    if isinstance(value, tuple):
        return [snapshot(item) for item in value]
    if isinstance(value, list):
        return [snapshot(item) for item in value]
    if isinstance(value, bytes):
        return {"bytes_hex": value.hex()}
    return value


def result(function):
    try:
        return {"ok": True, "value": snapshot(function())}
    except Exception as error:
        return {"ok": False, "type": type(error).__name__, "message": str(error)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    rng = random.Random(SEED)
    words = ("ready", "skip_one", "item_3", "bad", "value", "ID:AB42", "#tag", r"\#skip", '"blue,green"', "x", "ab")
    failures = []
    checks = 0
    for index in range(900):
        pattern = PATTERNS[index % len(PATTERNS)]
        pieces = [rng.choice(words) for _ in range(rng.randint(0, 9))]
        text = rng.choice((" ", ";", ",", "\n")).join(pieces)
        flags = rng.choice((0, re.MULTILINE, re.DOTALL, re.ASCII, re.IGNORECASE | re.ASCII))
        if rng.randrange(2):
            pattern, text = pattern.encode("ascii"), text.encode("ascii")
        pos = rng.randint(0, len(text))
        endpos = rng.randint(pos, len(text))
        baseline = re.compile(pattern, flags)
        candidate = rebar.compile(pattern, flags)
        calls = (
            ("search", lambda module: module.search(text, pos, endpos)),
            ("match", lambda module: module.match(text, pos, endpos)),
            ("fullmatch", lambda module: module.fullmatch(text, pos, endpos)),
            ("findall", lambda module: module.findall(text, pos, endpos)),
            ("finditer", lambda module: list(module.finditer(text, pos, endpos))),
            ("split", lambda module: module.split(text)),
            ("subn", lambda module: module.subn(b"X" if isinstance(text, bytes) else "X", text)),
        )
        for name, call in calls:
            checks += 1
            expected, actual = result(lambda: call(baseline)), result(lambda: call(candidate))
            if actual != expected:
                failures.append({"case": index, "api": name, "pattern": repr(pattern), "text": repr(text), "flags": int(flags), "pos": pos, "endpos": endpos, "expected": expected, "actual": actual})
    output = {"schema": "rebar-look-path-controls-v1", "seed": SEED, "cases": 900, "checks": checks, "failed": len(failures), "failures": failures}
    Path(args.output).write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in output.items() if key != "failures"}, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
