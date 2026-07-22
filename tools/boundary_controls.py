#!/usr/bin/env python3
"""Deterministic differential controls for scanner, escaping, and expansion."""

import argparse
import importlib
import json
import random
import re
from pathlib import Path


SEED = 20260722
MODULES = ("rebar", "candidates.ast_candidate", "candidates.rust_candidate")
SCANNER_PATTERNS = (r"|x", r"x*", r"(?:ab|a)", r"(?=x)", r"(?=,)|\b", r"[a-z]+", r"(?:x|,)*?")
TEMPLATES = (r"\2:\g<a>", r"\g<a>-\2", r"x\\y", r"\g<9>", r"\q")


def match_value(value):
    if value is None:
        return None
    return (value.span(), value.groups(), value.lastindex, value.lastgroup, value.pos, value.endpos)


def outcome(call):
    try:
        value = call()
        return ("ok", type(value).__name__, value)
    except BaseException as error:
        return (type(error).__name__, str(error), getattr(error, "msg", None), getattr(error, "pos", None))


def scanner_value(module, pattern, text, pos, end, sequence):
    scanner = module.compile(pattern).scanner(text, pos, end)
    public = tuple(sorted(name for name in dir(scanner) if not name.startswith("_")))
    return (public, scanner.pattern.pattern, tuple(match_value(getattr(scanner, name)()) for name in sequence))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    rng = random.Random(SEED)
    modules = {name: importlib.import_module(name) for name in MODULES}
    failures = []
    checks = 0
    cases = 0

    for index in range(720):
        text = "".join(rng.choice("abx, ") for _ in range(rng.randint(0, 24)))
        pattern = rng.choice(SCANNER_PATTERNS)
        if rng.randrange(2):
            text = text.encode("ascii")
            pattern = pattern.encode("ascii")
        pos = rng.randint(0, len(text))
        end = rng.randint(pos, len(text))
        sequence = tuple(rng.choice(("search", "match")) for _ in range(rng.randint(1, 9)))
        want = scanner_value(re, pattern, text, pos, end, sequence)
        for name, module in modules.items():
            checks += 1
            got = scanner_value(module, pattern, text, pos, end, sequence)
            if got != want:
                failures.append({"case": f"scanner-{index}", "module": name, "pattern": repr(pattern), "text": repr(text), "pos": pos, "endpos": end, "sequence": list(sequence), "expected": repr(want), "actual": repr(got)})
        cases += 1

    values = ("a+b", "\u2603 + [x]", b"a+b", bytes(range(256)), bytearray(b"a+b"), memoryview(b"a+b"), 3, None, [1])
    for index, value in enumerate(values):
        want = outcome(lambda: re.escape(value))
        for name, module in modules.items():
            checks += 1
            got = outcome(lambda module=module: module.escape(value))
            if got != want:
                failures.append({"case": f"escape-{index}", "module": name, "value": repr(value), "expected": repr(want), "actual": repr(got)})
        cases += 1

    for index, byte_mode in enumerate((False, True)):
        pattern = rb"(?P<a>a)?(b)" if byte_mode else r"(?P<a>a)?(b)"
        text = b"b" if byte_mode else "b"
        templates = tuple(value.encode("ascii") for value in TEMPLATES) if byte_mode else TEMPLATES
        if byte_mode:
            templates += (bytearray(rb"\2"), memoryview(rb"\2"))
        baseline = re.compile(pattern).search(text)
        for template_index, template in enumerate(templates):
            want = outcome(lambda: baseline.expand(template))
            for name, module in modules.items():
                match = module.compile(pattern).search(text)
                checks += 1
                got = outcome(lambda match=match: match.expand(template))
                if got != want:
                    failures.append({"case": f"expand-{index}-{template_index}", "module": name, "template": repr(template), "expected": repr(want), "actual": repr(got)})
            cases += 1

    result = {"schema": "rebar-boundary-controls-v1", "seed": SEED, "cases_per_module": cases, "checks": checks, "modules": list(MODULES), "failed": len(failures), "failures": failures}
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "failures"}, sort_keys=True))
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
