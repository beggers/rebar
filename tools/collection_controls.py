#!/usr/bin/env python3
"""Differential checks for structured line, path, and separator collection."""

import argparse
import json
import random
import re
from pathlib import Path

import rebar


SEED = 20260727
PATTERNS = (
    (r"\s*[:|/]\s*", 0),
    (r"\s*[,;]\s*", 0),
    (r"(?:^|\s)(?:\.\./|/)?[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+", 0),
    (r"(?:^|\s)(?:\.\./|/)?[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+", re.ASCII),
    (r"^(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?P<value>[^#\n]*?)\s*(?:#.*)?$", re.MULTILINE),
    (r"^(?:TRACE|DEBUG|FATAL)\s+(?P<code>[A-Z]{3}[0-9]{2})\s+(?P<text>.+)$", re.MULTILINE),
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
    pieces = ("alpha", "item_7", "730", " : ", " | ", " / ", " , ", " ; ", "../tests/data.json", "/opt/app/bin", "host: api.local", "max_items : 250 # cap", "enabled: true", "TRACE NET01 connected", "DEBUG CFG20 loaded", "FATAL APP99 stopped", "\n", "  ")
    failures = []
    checks = 0
    for index in range(960):
        pattern, flags = PATTERNS[index % len(PATTERNS)]
        text = "".join(rng.choice(pieces) for _ in range(rng.randint(0, 13)))
        if rng.randrange(3) == 0:
            text = rng.choice(("host: value\nnext: two", "TRACE NET01 ready\nDEBUG CFG20 done", "read ../a/b and /opt/c/d", "a : b | c / d")) + text
        if rng.randrange(2):
            pattern, text = pattern.encode("ascii"), text.encode("ascii")
        pos = rng.randint(0, len(text))
        endpos = rng.randint(pos, len(text))
        expected, actual = re.compile(pattern, flags), rebar.compile(pattern, flags)
        replacement = b"X" if isinstance(text, bytes) else "X"
        calls = (
            ("search", lambda module: module.search(text, pos, endpos)),
            ("match", lambda module: module.match(text, pos, endpos)),
            ("fullmatch", lambda module: module.fullmatch(text, pos, endpos)),
            ("findall", lambda module: module.findall(text, pos, endpos)),
            ("finditer", lambda module: list(module.finditer(text, pos, endpos))),
            ("split", lambda module: module.split(text, rng.randrange(4))),
            ("subn", lambda module: module.subn(replacement, text, rng.randrange(4))),
        )
        for name, call in calls:
            checks += 1
            state = rng.getstate()
            left = outcome(lambda: call(expected))
            rng.setstate(state)
            right = outcome(lambda: call(actual))
            if left != right:
                failures.append({"case": index, "api": name, "pattern": repr(pattern), "text": repr(text), "flags": int(flags), "pos": pos, "endpos": endpos, "expected": left, "actual": right})
    result = {"schema": "rebar-collection-controls-v1", "seed": SEED, "cases": 960, "checks": checks, "failed": len(failures), "failures": failures}
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "failures"}, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
