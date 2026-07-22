#!/usr/bin/env python3
"""Focused differential controls for behaviors discovered by the large correctness holdout."""

import argparse
import json
import random
import re
from pathlib import Path


SEED = 2026072909
MODULES = ("rebar", "candidates.ast_candidate", "candidates.rust_candidate")
SEPARATORS = (
    r"[^,\n]{1,2},",
    r"[^,\n]{1,8},",
    r"[^,\n]{8},",
    r"(?:[^,\n]{1,8},)+?",
    r"(?:[^,\n]{1,8},){1,4}",
    r"(?:[^,\n]{1,8},).*",
)
LOCALE_CLASSES = (
    rb"[^x]", rb"[^x\n]", rb"[^xy]", rb"[^x!]", rb"[^x0]", rb"[^a-z]", rb"[^a-z\n]", rb"[^\n]", rb"[^\n!]",
    rb"[^\d]", rb"[^\d\n]", rb"[^A-Z_]", rb"[^\x80x]", rb"[^xX]", rb"[^a-zA-Z]", rb"[^a-zA-Z_]",
)
CONFIG = r"^(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>[^#\n]*?)\s*(?:#.*)?$"


def snapshot(value):
    if hasattr(value, "span") and hasattr(value, "groups"):
        return (value.span(), value.groups(), value.lastindex, value.lastgroup, value.pos, value.endpos)
    if isinstance(value, (tuple, list)):
        return tuple(snapshot(item) for item in value)
    if isinstance(value, (bytes, str, int)) or value is None:
        return value
    if hasattr(value, "__next__"):
        return tuple(snapshot(item) for item in value)
    return repr(value)


def materialize(value, kind):
    if kind in {"text", "bytes"}:
        return value
    if kind == "bytearray":
        return bytearray(value)
    if kind == "memoryview":
        return memoryview(bytearray(value))
    raise RuntimeError(f"unknown input kind: {kind}")


def action(module, pattern, value, flags, api, surface):
    target = module if surface == "module" else module.compile(pattern, flags)
    function = getattr(target, api)
    kwargs = {"flags": flags} if surface == "module" else {}
    if api == "search":
        return snapshot(function(pattern, value, **kwargs) if surface == "module" else function(value))
    if api == "findall":
        return snapshot(function(pattern, value, **kwargs) if surface == "module" else function(value))
    if api == "split":
        return snapshot(function(pattern, value, maxsplit=0, **kwargs) if surface == "module" else function(value, maxsplit=0))
    repl = b"<\\g<0>>" if isinstance(pattern, bytes) else r"<\g<0>>"
    return snapshot(function(pattern, repl, value, count=0, **kwargs) if surface == "module" else function(repl, value, count=0))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    modules = {name: __import__(name, fromlist=["*"]) for name in MODULES}
    rng = random.Random(SEED)
    failures = []
    checks = 0
    totals = {"bounded-separator": 0, "locale-negated-set": 0, "final-newline-config": 0}

    subjects = ["", "a,", "123456789,", "x12345678,", "ZX91/0-cbX0,YcZ", "a,b,c,", "1234,5678,", "one,two\nthree,four,"]
    alphabet = "abcXYZ019 _,-.!:/=\n"
    for _ in range(40):
        run = "".join(rng.choice(alphabet.replace(",", "").replace("\n", "")) for _ in range(rng.randrange(0, 24)))
        subjects.append(rng.choice((run + ",", "prefix," + run + ",", run + ",tail", run + "\nnext,")))
    for byte_mode in (False, True):
        kinds = ("bytes", "bytearray", "memoryview") if byte_mode else ("text",)
        flags_list = (0, int(re.M), int(re.I | re.M))
        for pattern_text in SEPARATORS:
            pattern = pattern_text.encode("ascii") if byte_mode else pattern_text
            for text in subjects:
                source = text.encode("ascii") if byte_mode else text
                for kind in kinds:
                    value = materialize(source, kind)
                    for flags in flags_list:
                        for api in ("search", "findall", "split", "subn"):
                            for surface in ("module", "compiled"):
                                expected = action(re, pattern, value, flags, api, surface)
                                for name, module in modules.items():
                                    actual = action(module, pattern, value, flags, api, surface)
                                    checks += 1
                                    totals["bounded-separator"] += 1
                                    if actual != expected:
                                        failures.append({"family": "bounded-separator", "module": name, "pattern": repr(pattern), "subject": repr(source), "kind": kind, "flags": flags, "api": api, "surface": surface, "expected": repr(expected), "actual": repr(actual)})

    locale_subjects = (bytes(range(256)), b"xXyYzZ09!_\n\x80\xff", b"ccX X\nX", b"aA_bB-1", b"\x80\xffXYZxyz")
    for pattern in LOCALE_CLASSES:
        for source in locale_subjects:
            for kind in ("bytes", "bytearray", "memoryview"):
                value = materialize(source, kind)
                for api in ("search", "findall", "split", "subn"):
                    for surface in ("module", "compiled"):
                        expected = action(re, pattern, value, int(re.I | re.L), api, surface)
                        for name, module in modules.items():
                            actual = action(module, pattern, value, int(re.I | re.L), api, surface)
                            checks += 1
                            totals["locale-negated-set"] += 1
                            if actual != expected:
                                failures.append({"family": "locale-negated-set", "module": name, "pattern": repr(pattern), "subject": repr(source), "kind": kind, "api": api, "surface": surface, "expected": repr(expected), "actual": repr(actual)})

    config_subjects = (
        "PORT = 8080 # service\n", "\nPORT = 8080 # service\n", "NAME=alpha beta\nNEXT = value\n", "# comment\nDEBUG = false # note\n",
        "EMPTY = \n", "VALUE = x\n\n", "BAD-LINE\nGOOD = yes\n", "KEY = value",
    )
    for byte_mode in (False, True):
        pattern = CONFIG.encode("ascii") if byte_mode else CONFIG
        kinds = ("bytes", "bytearray", "memoryview") if byte_mode else ("text",)
        for text in config_subjects:
            source = text.encode("ascii") if byte_mode else text
            for kind in kinds:
                value = materialize(source, kind)
                for api in ("search", "findall", "subn"):
                    for surface in ("module", "compiled"):
                        expected = action(re, pattern, value, int(re.M), api, surface)
                        for name, module in modules.items():
                            actual = action(module, pattern, value, int(re.M), api, surface)
                            checks += 1
                            totals["final-newline-config"] += 1
                            if actual != expected:
                                failures.append({"family": "final-newline-config", "module": name, "pattern": repr(pattern), "subject": repr(source), "kind": kind, "api": api, "surface": surface, "expected": repr(expected), "actual": repr(actual)})

    result = {"schema": "rebar-large-holdout-controls-v1", "seed": SEED, "modules": list(MODULES), "checks": checks, "families": totals, "failed": len(failures), "failures": failures}
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "failures"}, sort_keys=True))
    if failures:
        for failure in failures[:25]:
            print(failure, flush=True)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
