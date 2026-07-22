#!/usr/bin/env python3
"""Differential checks for structured native search and collection paths."""

import argparse
import json
import random
import re
from pathlib import Path

import rebar


SEED = 20260726
PATTERNS = (
    (r"START\n(?P<body>.*?)\nSTOP", re.DOTALL),
    (r"BEGIN:(?P<body>.*?):END", re.DOTALL),
    (r"<(?P<body>.*?)>", 0),
    (r"([\"'])(.*?)\1", 0),
    (r"([/:])(.*?)\1", re.DOTALL),
    (r"//[^\n]*$", re.MULTILINE),
    (r"##[^\n]*$", re.MULTILINE),
    (r"<(?P<tag>[A-Za-z][A-Za-z0-9]*)\b[^>]*>", 0),
    (r"\[(?P<tag>[A-Za-z][A-Za-z0-9]*)\b[^\]]*\]", 0),
    (r"(?:cedar|birch|maple|willow|spruce|poplar|walnut|aspen|cherry|olive)_[0-9]{2}", 0),
    (r"(?:amber|azure|apricot|apple|arch|atom)-[A-Z]{2}", re.IGNORECASE),
    (r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?P<num>[0-9]+)", 0),
    (r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<num>[0-9]+)", 0),
)


def snapshot(value):
    if value is None:
        return None
    if hasattr(value, "span"):
        return {"span": list(value.span()), "groups": list(value.groups()), "lastindex": value.lastindex}
    if isinstance(value, list):
        return [snapshot(item) for item in value]
    if isinstance(value, tuple):
        return [snapshot(item) for item in value]
    if isinstance(value, bytes):
        return {"bytes_hex": value.hex()}
    return value


def outcome(function):
    try:
        return {"ok": True, "value": snapshot(function())}
    except Exception as error:
        return {"ok": False, "type": type(error).__name__, "message": str(error)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    rng = random.Random(SEED)
    pieces = ("alpha", "item_7", "730", " : ", " = ", "// note", "## tag", "START\nrow\nSTOP", "BEGIN:value:END", "'quoted value'", '"two words"', "/path/", "<markup>", "\n", ";")
    failures = []
    checks = 0
    for index in range(990):
        pattern, flags = PATTERNS[index % len(PATTERNS)]
        text = "".join(rng.choice(pieces) for _ in range(rng.randint(0, 12)))
        if rng.randrange(3) == 0:
            text = rng.choice(("START\nfirst\nSTOP", "BEGIN:a:END", "key_2 : 47", "// line\n", "'one' \"two\"")) + text
        if rng.randrange(2):
            pattern, text = pattern.encode("ascii"), text.encode("ascii")
        pos = rng.randint(0, len(text))
        endpos = rng.randint(pos, len(text))
        expected, actual = re.compile(pattern, flags), rebar.compile(pattern, flags)
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
            left, right = outcome(lambda: call(expected)), outcome(lambda: call(actual))
            if left != right:
                failures.append({"case": index, "api": name, "pattern": repr(pattern), "text": repr(text), "flags": int(flags), "pos": pos, "endpos": endpos, "expected": left, "actual": right})
    result = {"schema": "rebar-structured-path-controls-v1", "seed": SEED, "cases": 990, "checks": checks, "failed": len(failures), "failures": failures}
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "failures"}, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
