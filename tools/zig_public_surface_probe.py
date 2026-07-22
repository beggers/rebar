#!/usr/bin/env python3
"""Differential checks for the native-bound public Pattern and Match surface."""

from __future__ import annotations

import argparse
import copy
import importlib
import inspect
import json
import pickle
import re
import weakref
from pathlib import Path


METHODS = ("search", "match", "fullmatch", "findall", "finditer", "split", "sub", "subn", "scanner")


def match_value(value):
    if value is None:
        return None
    return {"span": list(value.span()), "groups": list(value.groups()), "groupdict": value.groupdict(), "lastindex": value.lastindex, "lastgroup": value.lastgroup}


def result_value(method, value):
    if method in ("search", "match", "fullmatch"):
        return match_value(value)
    if method == "finditer":
        return [match_value(item) for item in value]
    if method == "scanner":
        return [match_value(value.search()), match_value(value.search()), match_value(value.search())]
    return value


def observed(function):
    try:
        return {"value": function()}
    except BaseException as error:
        return {"error": type(error).__name__, "message": str(error)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--module", default="rebar")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    candidate = importlib.import_module(args.module)
    failures = []
    checks = 0

    def check(name, oracle, actual):
        nonlocal checks
        checks += 1
        expected = observed(oracle)
        got = observed(actual)
        if expected != got:
            failures.append({"case": name, "expected": expected, "actual": got})

    for byte_mode in (False, True):
        tag = "bytes" if byte_mode else "text"
        pattern = rb"(a)(?P<n>b)?" if byte_mode else r"(a)(?P<n>b)?"
        subject = b"ab a ab" if byte_mode else "ab a ab"
        replacement = rb"\g<n>-\1" if byte_mode else r"\g<n>-\1"
        oracle_pattern = re.compile(pattern)
        actual_pattern = candidate.compile(pattern)
        positional = {name: (subject,) for name in METHODS}
        positional["sub"] = positional["subn"] = (replacement, subject)
        keyword = {name: {"string": subject} for name in METHODS}
        keyword["sub"] = keyword["subn"] = {"repl": replacement, "string": subject}
        for method in METHODS:
            check(f"{tag}.class.{method}.positional", lambda method=method: result_value(method, getattr(re.Pattern, method)(oracle_pattern, *positional[method])), lambda method=method: result_value(method, getattr(candidate.Pattern, method)(actual_pattern, *positional[method])))
            check(f"{tag}.class.{method}.keyword", lambda method=method: result_value(method, getattr(re.Pattern, method)(oracle_pattern, **keyword[method])), lambda method=method: result_value(method, getattr(candidate.Pattern, method)(actual_pattern, **keyword[method])))
            check(f"{tag}.bound-self.{method}", lambda method=method: getattr(oracle_pattern, method).__self__ is oracle_pattern, lambda method=method: getattr(actual_pattern, method).__self__ is actual_pattern)
            check(f"{tag}.wrong-self.{method}", lambda method=method: getattr(re.Pattern, method)(object()), lambda method=method: getattr(candidate.Pattern, method)(object()))
            check(f"{tag}.bound-signature.{method}", lambda method=method: str(inspect.signature(getattr(oracle_pattern, method))), lambda method=method: str(inspect.signature(getattr(actual_pattern, method))))
            check(f"{tag}.class-signature.{method}", lambda method=method: str(inspect.signature(getattr(re.Pattern, method))), lambda method=method: str(inspect.signature(getattr(candidate.Pattern, method))))
        for attribute, value in (("pattern", b"x" if byte_mode else "x"), ("flags", 0), ("groups", 0), ("groupindex", {}), *((method, None) for method in METHODS)):
            check(f"{tag}.readonly.{attribute}", lambda attribute=attribute, value=value: setattr(oracle_pattern, attribute, value), lambda attribute=attribute, value=value: setattr(actual_pattern, attribute, value))
        check(f"{tag}.copy", lambda: copy.copy(oracle_pattern) is oracle_pattern, lambda: copy.copy(actual_pattern) is actual_pattern)
        check(f"{tag}.deepcopy", lambda: copy.deepcopy(oracle_pattern) is oracle_pattern, lambda: copy.deepcopy(actual_pattern) is actual_pattern)
        check(f"{tag}.pickle", lambda: match_value(pickle.loads(pickle.dumps(oracle_pattern)).search(subject)), lambda: match_value(pickle.loads(pickle.dumps(actual_pattern)).search(subject)))
        check(f"{tag}.weakref", lambda: weakref.ref(oracle_pattern)() is oracle_pattern, lambda: weakref.ref(actual_pattern)() is actual_pattern)

        oracle_match = oracle_pattern.search(subject)
        actual_match = actual_pattern.search(subject)
        match_calls = (
            ("group0", lambda item: item.group()), ("group-name", lambda item: item.group("n")), ("group-many", lambda item: item.group(0, "n", 1)),
            ("groups", lambda item: item.groups()), ("groups-default", lambda item: item.groups(default=b"x" if byte_mode else "x")),
            ("groupdict", lambda item: item.groupdict()), ("groupdict-default", lambda item: item.groupdict(default=b"x" if byte_mode else "x")),
            ("start", lambda item: item.start()), ("end", lambda item: item.end()), ("span", lambda item: item.span()), ("span-name", lambda item: item.span("n")),
            ("regs", lambda item: item.regs), ("regs-identity", lambda item: item.regs is item.regs),
            ("group-keyword", lambda item: item.group(group=1)), ("groups-extra", lambda item: item.groups("a", "b")), ("groups-keywords", lambda item: item.groups(default="a", other="b")),
            ("groupdict-extra", lambda item: item.groupdict("a", "b")), ("groupdict-keywords", lambda item: item.groupdict(default="a", other="b")),
            ("start-extra", lambda item: item.start(1, 2)), ("end-extra", lambda item: item.end(1, 2)), ("span-extra", lambda item: item.span(1, 2)),
            ("start-keyword", lambda item: item.start(group=1)), ("end-keyword", lambda item: item.end(group=1)), ("span-keyword", lambda item: item.span(group=1)),
        )
        for name, function in match_calls:
            check(f"{tag}.match.{name}", lambda function=function: function(oracle_match), lambda function=function: function(actual_match))

    report = {"schema": "rebar-zig-public-surface-v1", "module": args.module, "correctness_checks": checks, "failed": len(failures), "failures": failures}
    Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True, default=repr) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "failures"}, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
