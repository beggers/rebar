#!/usr/bin/env python3
"""Deterministic CPython oracle for the public Rust regex and FFI surface."""

from __future__ import annotations

import argparse
import collections
import copy
import importlib
import json
import pickle
import weakref
from pathlib import Path


class Index:
    def __init__(self, value):
        self.value = value

    def __index__(self):
        return self.value

    def __repr__(self):
        return f"Index({self.value!r})"


class RaisingIndex:
    def __index__(self):
        raise RuntimeError("intentional __index__ failure")

    def __repr__(self):
        return "RaisingIndex()"


class NonintegerIndex:
    def __index__(self):
        return "1"

    def __repr__(self):
        return "NonintegerIndex()"


class Text(str):
    pass


class Blob(bytes):
    pass


class HashText(str):
    def __hash__(self):
        raise RuntimeError("intentional text __hash__ failure")


class HashBlob(bytes):
    def __hash__(self):
        raise RuntimeError("intentional bytes __hash__ failure")


def normalized(value):
    if isinstance(value, bytes):
        return {"bytes_hex": bytes(value).hex(), "type": type(value).__name__}
    if isinstance(value, str):
        return {"text": str(value), "type": type(value).__name__}
    if isinstance(value, memoryview):
        return {
            "bytes_hex": value.tobytes().hex(),
            "shape": list(value.shape),
            "contiguous": value.c_contiguous,
        }
    if isinstance(value, tuple):
        return {"tuple": [normalized(item) for item in value]}
    if isinstance(value, list):
        return [normalized(item) for item in value]
    if isinstance(value, dict):
        return {str(key): normalized(item) for key, item in value.items()}
    if hasattr(value, "span") and hasattr(value, "group"):
        return {
            "span": normalized(value.span()),
            "group": normalized(value.group()),
            "groups": normalized(value.groups()),
            "groupdict": normalized(value.groupdict()),
            "regs": normalized(value.regs),
            "lastindex": value.lastindex,
            "lastgroup": value.lastgroup,
            "pos": value.pos,
            "endpos": value.endpos,
            "subject_type": type(value.string).__name__,
            "pattern_type": type(value.re.pattern).__name__,
        }
    return value


def observed(action):
    try:
        return {"value": normalized(action())}
    except Exception as error:
        result = {"error": type(error).__name__, "message": str(error)}
        if all(hasattr(error, name) for name in ("msg", "pattern", "pos")):
            result["pattern_error"] = {
                name: normalized(getattr(error, name, None))
                for name in ("msg", "pattern", "pos", "lineno", "colno")
            }
        return result


def equivalent(expected, actual):
    if "error" in expected or "error" in actual:
        if expected.get("error") != actual.get("error"):
            return False
        if "pattern_error" in expected or "pattern_error" in actual:
            return expected.get("pattern_error") == actual.get("pattern_error")
        return True
    return expected == actual


def describe(value):
    if isinstance(value, memoryview):
        return f"memoryview(shape={value.shape}, contiguous={value.c_contiguous})"
    return repr(value)


def check(records, family, operation, details, standard, candidate):
    expected = observed(standard)
    actual = observed(candidate)
    records.append(
        {
            "family": family,
            "operation": operation,
            "details": details,
            "expected": expected,
            "actual": actual,
            "passed": equivalent(expected, actual),
        }
    )


def scanner_values(pattern, subject, pos, endpos, operation):
    scanner = pattern.scanner(subject, pos, endpos)
    output = []
    for _ in range(128):
        match = getattr(scanner, operation)()
        output.append(normalized(match))
        if match is None:
            return output
    raise RuntimeError("scanner failed to terminate")


def index_protocol(records, standard, candidate):
    patterns = (
        ("literal-text", "aba", "xxaba aba"),
        ("capture-text", r"(?P<word>[A-Za-z]+)", "xxaba aba"),
        ("nullable-text", r"(?P<word>[A-Za-z]*)", "xx aba"),
        ("literal-bytes", b"aba", b"xxaba aba"),
        ("capture-bytes", rb"(?P<word>[A-Za-z]+)", b"xxaba aba"),
    )
    windows = (
        (Index(0), Index(9)),
        (Index(1), Index(8)),
        (Index(-3), Index(7)),
        (Index(4), Index(2)),
        (Index(2**90), Index(2**91)),
        (True, False),
        (RaisingIndex(), Index(2)),
        (Index(0), RaisingIndex()),
        (NonintegerIndex(), Index(2)),
        (Index(0), NonintegerIndex()),
    )
    for label, expression, subject in patterns:
        left, right = standard.compile(expression), candidate.compile(expression)
        for start, end in windows:
            details = {"input": label, "pos": describe(start), "endpos": describe(end)}
            for operation in ("search", "match", "fullmatch", "findall"):
                check(records, "index-protocol", operation, details,
                      lambda p=left, op=operation: getattr(p, op)(subject, start, end),
                      lambda p=right, op=operation: getattr(p, op)(subject, start, end))
            check(records, "index-protocol", "finditer", details,
                  lambda p=left: [normalized(item) for item in p.finditer(subject, start, end)],
                  lambda p=right: [normalized(item) for item in p.finditer(subject, start, end)])
            for operation in ("search", "match"):
                check(records, "index-protocol", "scanner." + operation, details,
                      lambda p=left, op=operation: scanner_values(p, subject, start, end, op),
                      lambda p=right, op=operation: scanner_values(p, subject, start, end, op))


def bound_calls(records, standard, candidate):
    patterns = (
        ("text", "a", "aba"),
        ("capture-text", r"(?P<word>[a-z]+)", "aba def"),
        ("bytes", b"a", b"aba"),
        ("capture-bytes", rb"(?P<word>[a-z]+)", b"aba def"),
    )

    def invoke(pattern, operation, args, kwargs):
        result = getattr(pattern, operation)(*args, **kwargs)
        if operation == "finditer":
            return [normalized(item) for item in result]
        if operation == "scanner":
            values = []
            for _ in range(64):
                item = result.search()
                values.append(normalized(item))
                if item is None:
                    return values
            raise RuntimeError("scanner failed to terminate")
        return result

    for label, expression, subject in patterns:
        left, right = standard.compile(expression), candidate.compile(expression)
        calls = (
            ("pos-none", (subject, None), {}),
            ("endpos-none", (subject, 0, None), {}),
            ("both-none", (subject, None, None), {}),
            ("keyword-pos-none", (subject,), {"pos": None}),
            ("keyword-endpos-none", (subject,), {"endpos": None}),
            ("keyword-both-none", (subject,), {"pos": None, "endpos": None}),
            ("string-keyword", (), {"string": subject}),
            ("duplicate-string", (subject,), {"string": subject}),
            ("duplicate-pos", (subject, 1), {"pos": 2}),
            ("unknown-keyword", (), {"value": subject}),
            ("float-pos", (subject, 1.0), {}),
            ("float-endpos", (subject, 0, 2.0), {}),
            ("string-pos", (subject, "1"), {}),
            ("string-endpos", (subject, 0, "2"), {}),
            ("raising-pos", (subject, RaisingIndex()), {}),
            ("raising-endpos", (subject, 0, RaisingIndex()), {}),
            ("noninteger-pos", (subject, NonintegerIndex()), {}),
            ("noninteger-endpos", (subject, 0, NonintegerIndex()), {}),
            ("missing-string", (), {}),
            ("too-many", (subject, 0, 2, 3), {}),
        )
        for operation in ("search", "match", "fullmatch", "findall", "finditer", "scanner"):
            for name, args, kwargs in calls:
                details = {"input": label, "call": name}
                check(records, "bound-keywords", operation, details,
                      lambda p=left, op=operation, a=args, kw=kwargs: invoke(p, op, a, kw),
                      lambda p=right, op=operation, a=args, kw=kwargs: invoke(p, op, a, kw))


def count_protocol(records, standard, candidate):
    patterns = (("text", "a", "aba", "!"), ("bytes", b"a", b"aba", b"!"))
    counts = (Index(0), Index(1), Index(2), Index(-1), True, False, None, 1.0,
              RaisingIndex(), NonintegerIndex(), Index(2**90), Index(-(2**90)))
    for label, expression, subject, replacement in patterns:
        left, right = standard.compile(expression), candidate.compile(expression)
        for count in counts:
            details = {"input": label, "count": describe(count)}
            for operation in ("sub", "subn"):
                check(records, "replacement-count", operation, details,
                      lambda p=left, op=operation: getattr(p, op)(replacement, subject, count),
                      lambda p=right, op=operation: getattr(p, op)(replacement, subject, count))
            check(records, "replacement-count", "split", details,
                  lambda p=left: p.split(subject, count),
                  lambda p=right: p.split(subject, count))


def subclass_surface(records, standard, candidate):
    inputs = (
        ("text-subject", "aba", Text("xxaba aba")),
        ("text-pattern", Text("aba"), "xxaba aba"),
        ("text-both", Text("aba"), Text("xxaba aba")),
        ("bytes-subject", b"aba", Blob(b"xxaba aba")),
        ("bytes-pattern", Blob(b"aba"), b"xxaba aba"),
        ("bytes-both", Blob(b"aba"), Blob(b"xxaba aba")),
        ("named-text", Text(r"(?P<word>[A-Za-z]+)"), Text("xx aba")),
        ("named-bytes", Blob(rb"(?P<word>[A-Za-z]+)"), Blob(b"xx aba")),
    )
    for label, expression, subject in inputs:
        left, right = standard.compile(expression), candidate.compile(expression)
        details = {"input": label, "pattern_type": type(expression).__name__, "subject_type": type(subject).__name__}
        for operation in ("search", "match", "fullmatch", "findall", "split"):
            check(records, "subclass-identity", operation, details,
                  lambda p=left, op=operation: getattr(p, op)(subject),
                  lambda p=right, op=operation: getattr(p, op)(subject))
        check(records, "subclass-identity", "finditer", details,
              lambda p=left: [normalized(match) for match in p.finditer(subject)],
              lambda p=right: [normalized(match) for match in p.finditer(subject)])
        check(records, "subclass-identity", "subject-identity", details,
              lambda p=left: p.search(subject).string is subject,
              lambda p=right: p.search(subject).string is subject)
        check(records, "subclass-identity", "pattern-identity", details,
              lambda p=left: p.search(subject).re.pattern is expression,
              lambda p=right: p.search(subject).re.pattern is expression)


def buffer_surface(records, standard, candidate):
    inputs = (
        ("contiguous", memoryview(b"xxaba aba")),
        ("noncontiguous", memoryview(b"x_x_a_b_a_ _a_b_a_")[::2]),
        ("multidimensional", memoryview(b"xxabaaba").cast("B", (2, 4))),
        ("wide-elements", memoryview(b"x\x00a\x00b\x00a\x00").cast("H")),
        ("bytearray", bytearray(b"xxaba aba")),
    )
    for label, subject in inputs:
        left, right = standard.compile(b"aba"), candidate.compile(b"aba")
        details = {"input": label, "subject": describe(subject)}
        for operation in ("search", "match", "fullmatch", "findall", "split"):
            check(records, "buffer-lifetime", operation, details,
                  lambda p=left, op=operation: getattr(p, op)(subject),
                  lambda p=right, op=operation: getattr(p, op)(subject))
        check(records, "buffer-lifetime", "finditer", details,
              lambda p=left: [normalized(match) for match in p.finditer(subject)],
              lambda p=right: [normalized(match) for match in p.finditer(subject)])

    def lock_outcome(engine, operation):
        source = bytearray(b"aba aba")
        compiled = engine.compile(b"aba")
        owner = compiled.finditer(source) if operation == "iterator" else compiled.scanner(source)
        try:
            source.append(33)
            changed = True
        except BufferError:
            changed = False
        if operation == "iterator":
            first = next(owner, None)
        else:
            first = owner.search()
        return {"append_succeeded": changed, "first": normalized(first), "length": len(source)}

    for operation in ("iterator", "scanner"):
        check(records, "buffer-lifetime", "mutable-lock." + operation, {},
              lambda op=operation: lock_outcome(standard, op),
              lambda op=operation: lock_outcome(candidate, op))


def match_surface(records, standard, candidate):
    inputs = (
        ("text", r"(?P<first>[a-z]+)(?P<sep>[-_])(?P<num>[0-9]+)?", "xx alpha-123 beta_"),
        ("bytes", rb"(?P<first>[a-z]+)(?P<sep>[-_])(?P<num>[0-9]+)?", b"xx alpha-123 beta_"),
    )
    for label, expression, subject in inputs:
        left, right = standard.compile(expression), candidate.compile(expression)
        default = b"missing" if isinstance(subject, bytes) else "missing"
        template = rb"<\g<num>: \g<first>>" if isinstance(subject, bytes) else r"<\g<num>: \g<first>>"
        actions = (
            ("group", lambda match: match.group()),
            ("group-zero", lambda match: match.group(0)),
            ("group-first", lambda match: match.group(1)),
            ("group-named", lambda match: match.group("first")),
            ("group-many", lambda match: match.group(0, 1, 2, 3)),
            ("group-mixed", lambda match: match.group("first", 2, "num")),
            ("group-true", lambda match: match.group(True)),
            ("group-false", lambda match: match.group(False)),
            ("group-index", lambda match: match.group(Index(1))),
            ("group-raising-index", lambda match: match.group(RaisingIndex())),
            ("group-noninteger-index", lambda match: match.group(NonintegerIndex())),
            ("group-bad-negative", lambda match: match.group(-1)),
            ("group-bad-large", lambda match: match.group(20)),
            ("group-bad-name", lambda match: match.group("missing")),
            ("group-bad-float", lambda match: match.group(1.0)),
            ("groups", lambda match: match.groups()),
            ("groups-default", lambda match: match.groups(default)),
            ("groups-keyword", lambda match: match.groups(default=default)),
            ("groupdict", lambda match: match.groupdict()),
            ("groupdict-default", lambda match: match.groupdict(default)),
            ("groupdict-keyword", lambda match: match.groupdict(default=default)),
            ("regs", lambda match: match.regs),
            ("regs-cached", lambda match: match.regs is match.regs),
            ("start", lambda match: match.start()),
            ("start-name", lambda match: match.start("first")),
            ("start-raising", lambda match: match.start(RaisingIndex())),
            ("end", lambda match: match.end()),
            ("end-name", lambda match: match.end("num")),
            ("span", lambda match: match.span()),
            ("span-name", lambda match: match.span("num")),
            ("getitem-index", lambda match: match[Index(1)]),
            ("getitem-name", lambda match: match["first"]),
            ("expand", lambda match: match.expand(template)),
            ("copy-identity", lambda match: copy.copy(match) is match),
            ("deepcopy-identity", lambda match: copy.deepcopy(match) is match),
            ("lastindex", lambda match: match.lastindex),
            ("lastgroup", lambda match: match.lastgroup),
            ("readonly-pos", lambda match: setattr(match, "pos", 3)),
            ("readonly-string", lambda match: setattr(match, "string", "changed")),
            ("type-name", lambda match: type(match).__name__),
            ("type-module", lambda match: type(match).__module__),
        )
        for number in (0, 1):
            for name, action in actions:
                details = {"input": label, "match": number}
                check(records, "match-surface", name, details,
                      lambda p=left, n=number, fn=action: fn(list(p.finditer(subject))[n]),
                      lambda p=right, n=number, fn=action: fn(list(p.finditer(subject))[n]))


def malicious_hash(records, standard, candidate):
    factories = (
        ("text-pattern", lambda: HashText("a"), "aba"),
        ("bytes-pattern", lambda: HashBlob(b"a"), b"aba"),
    )
    for label, factory, subject in factories:
        details = {"input": label}
        for operation in ("compile", "search", "match", "fullmatch", "findall", "finditer"):
            def run(engine, op=operation, make=factory, source=subject):
                pattern = make()
                if op == "compile":
                    result = engine.compile(pattern)
                    return result.pattern
                value = getattr(engine, op)(pattern, source)
                if op == "finditer":
                    return [normalized(match) for match in value]
                return value

            check(records, "malicious-hash", operation, details,
                  lambda: run(standard), lambda: run(candidate))


def pattern_surface(records, standard, candidate):
    patterns = (("text", r"(?P<word>[a-z]+)", "word"),
                ("bytes", rb"(?P<word>[a-z]+)", b"word"))
    for label, expression, subject in patterns:
        left, right = standard.compile(expression), candidate.compile(expression)
        actions = (
            ("pattern", lambda pattern: pattern.pattern),
            ("flags", lambda pattern: pattern.flags),
            ("groups", lambda pattern: pattern.groups),
            ("groupindex", lambda pattern: dict(pattern.groupindex)),
            ("copy-identity", lambda pattern: copy.copy(pattern) is pattern),
            ("deepcopy-identity", lambda pattern: copy.deepcopy(pattern) is pattern),
            ("weakref", lambda pattern: weakref.ref(pattern)() is pattern),
            ("pickle-result", lambda pattern: normalized(pickle.loads(pickle.dumps(pattern)).search(subject))),
            ("readonly-pattern", lambda pattern: setattr(pattern, "pattern", expression)),
            ("readonly-flags", lambda pattern: setattr(pattern, "flags", 0)),
            ("readonly-groups", lambda pattern: setattr(pattern, "groups", 0)),
            ("readonly-groupindex", lambda pattern: setattr(pattern, "groupindex", {})),
        )
        for name, action in actions:
            check(records, "pattern-surface", name, {"input": label},
                  lambda p=left, fn=action: fn(p),
                  lambda p=right, fn=action: fn(p))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", default="candidates.rust_candidate")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    standard = importlib.import_module("re")
    candidate = importlib.import_module(args.module)
    records = []
    for runner in (index_protocol, bound_calls, count_protocol, subclass_surface,
                   buffer_surface, match_surface, malicious_hash, pattern_surface):
        runner(records, standard, candidate)

    failures = [record for record in records if not record["passed"]]
    families = collections.Counter(record["family"] for record in records)
    failed_families = collections.Counter(record["family"] for record in failures)
    report = {
        "schema": "rebar-rust-public-surface-v1",
        "module": args.module,
        "oracle": "CPython stdlib re",
        "correctness_checks": len(records),
        "failed": len(failures),
        "families": [
            {"family": family, "checks": count, "failed": failed_families[family]}
            for family, count in sorted(families.items())
        ],
        "failures": failures,
        "records": records,
    }
    Path(args.output).write_text(
        json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({key: value for key, value in report.items()
                      if key not in {"failures", "records"}}, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
