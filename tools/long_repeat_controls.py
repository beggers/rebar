#!/usr/bin/env python3
"""Deterministic differential controls for repeated groups and lookbehind."""

import argparse
import importlib
import json
import random
import re
from pathlib import Path


SEED = 20260721
MODULES = ("rebar", "candidates.ast_candidate", "candidates.rust_candidate")
ATOMS = ("a", "A", ".", r"\d", r"\w", "[ab]", "[aA0-3]", "(?:a|b)", "(?:a|.)")
TAILS = ("", "a", "b", "0", "(?:a|b)")
QUANTIFIERS = ("*", "+", "?", "{0,3}", "{1,4}", "{2,5}", "{3}")
MODES = ("", "?", "+")
FLAGS = (0, re.IGNORECASE, re.DOTALL, re.IGNORECASE | re.DOTALL)


def match_value(value):
    if value is None:
        return None
    return (
        value.span(),
        value.groups(),
        value.groupdict(),
        value.lastindex,
        value.lastgroup,
        value.pos,
        value.endpos,
        value.regs,
    )


def snapshot(module, pattern, text, flags, pos, end):
    compiled = module.compile(pattern, flags)
    replacement = r"<\1>" if compiled.groups else "<>"
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
        compiled.subn(lambda value: "<" + value.group(0) + ">", text, 2),
    )


def cases():
    rng = random.Random(SEED)
    for index in range(960):
        atom = rng.choice(ATOMS)
        inner_count = rng.randint(1, 4)
        outer_count = rng.randint(1, 3)
        forms = (
            atom,
            f"({atom})",
            f"(({atom}){{{inner_count}}})",
            f"((({atom}){{{inner_count}}}){{{outer_count}}})",
        )
        child = rng.choice(forms)
        quantifier = rng.choice(QUANTIFIERS)
        mode = rng.choice(MODES)
        prefix = rng.choice(("", "a", "(?:a|b)"))
        tail = rng.choice(TAILS)
        pattern = prefix + child + quantifier + mode + tail
        text = "".join(rng.choice("abAB0123x\n") for _ in range(rng.randint(0, 28)))
        pos = rng.randint(0, len(text))
        end = rng.randint(pos, len(text))
        yield index, pattern, text, rng.choice(FLAGS), pos, end

    lookbehinds = (
        r"(?<=x{3})",
        r"(?<=x{3})x",
        r"(?<=((x{2}){2}){2})",
        r"(?<=((x{2}){2}){2})x",
        r"(?<!((x{2}){2}){2})",
    )
    index = 960
    for pattern in lookbehinds:
        for text in ("x" * 10, "ax" * 8, "x\nx" * 4):
            for pos in (0, 1, 2, 5):
                end = len(text) - (pos % 2)
                yield index, pattern, text, 0, min(pos, end), end
                index += 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    modules = {name: importlib.import_module(name) for name in MODULES}
    failures = []
    checked = 0
    total_cases = 0
    for index, pattern, text, flags, pos, end in cases():
        total_cases += 1
        expected = snapshot(re, pattern, text, flags, pos, end)
        for name, module in modules.items():
            checked += 1
            actual = snapshot(module, pattern, text, flags, pos, end)
            if actual != expected:
                failures.append(
                    {
                        "case": index,
                        "module": name,
                        "pattern": pattern,
                        "text": text,
                        "flags": int(flags),
                        "pos": pos,
                        "endpos": end,
                        "expected": repr(expected),
                        "actual": repr(actual),
                    }
                )
    result = {
        "schema": "rebar-long-repeat-controls-v1",
        "seed": SEED,
        "cases_per_module": total_cases,
        "checks": checked,
        "modules": list(MODULES),
        "failed": len(failures),
        "failures": failures,
    }
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "failures"}, sort_keys=True))
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
