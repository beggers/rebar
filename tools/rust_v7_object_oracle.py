#!/usr/bin/env python3
"""Reproduce frozen CPython 3.14.6 regular-expression object contracts.

This correctness-only oracle never imports a benchmark, holdout, or external
regular-expression engine. It compares every independently generated case with
the pinned standard library, first verifies the reference against itself, and
writes complete, deterministic gzip evidence for all four local candidates.
"""

from __future__ import annotations

import argparse
import array
import collections
import copy
import gc
import gzip
import hashlib
import importlib
import inspect
import json
import operator
import pickle
import random
import re
import sys
import types
import unicodedata
import warnings
import weakref
from dataclasses import dataclass
from pathlib import Path


SEED = 0x52454241525F4F42
SCHEMA = "rebar-rust-v7-object-oracle-v1"
PINNED = (3, 14, 6)
MODULES = (
    ("ast", "candidates.ast_candidate"),
    ("vm", "candidates.vm_candidate"),
    ("rust", "candidates.rust_candidate"),
    ("zig", "candidates.zig_candidate"),
)


class Text(str):
    pass


class Blob(bytes):
    pass


class Index:
    def __init__(self, value, trace=None, label="index", behavior="normal"):
        self.value = value
        self.trace = trace
        self.label = label
        self.behavior = behavior

    def __index__(self):
        if self.trace is not None:
            self.trace.append(("index", self.label, self.behavior))
        if self.behavior == "raise":
            raise RuntimeError("independent object-contract index sentinel")
        if self.behavior == "noninteger":
            return "not-an-integer"
        return self.value


class HashText(str):
    def __new__(cls, value, trace, behavior="normal"):
        item = str.__new__(cls, value)
        item.trace = trace
        item.behavior = behavior
        return item

    def __hash__(self):
        self.trace.append(("pattern-hash", "text", self.behavior))
        if self.behavior == "raise":
            raise RuntimeError("independent object-contract text hash sentinel")
        return str.__hash__(self)


class HashBlob(bytes):
    def __new__(cls, value, trace, behavior="normal"):
        item = bytes.__new__(cls, value)
        item.trace = trace
        item.behavior = behavior
        return item

    def __hash__(self):
        self.trace.append(("pattern-hash", "bytes", self.behavior))
        if self.behavior == "raise":
            raise RuntimeError("independent object-contract bytes hash sentinel")
        return bytes.__hash__(self)



_HEX_DIGITS = frozenset("0123456789abcdefABCDEF")


def stable_text(value):
    """Remove ephemeral object addresses while preserving actual text."""
    value = str(value)
    chunks = []
    cursor = 0
    while True:
        marker = value.find("0x", cursor)
        if marker < 0:
            chunks.append(value[cursor:])
            return "".join(chunks)
        end = marker + 2
        while end < len(value) and value[end] in _HEX_DIGITS:
            end += 1
        if end == marker + 2:
            chunks.append(value[cursor:marker + 2])
            cursor = marker + 2
            continue
        chunks.append(value[cursor:marker])
        chunks.append("0x<address>")
        cursor = end


def normal(value):
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        return int(value)
    if isinstance(value, str):
        text = stable_text(value)
        if any(0xD800 <= ord(character) <= 0xDFFF for character in text):
            return {
                "kind": type(value).__name__,
                "surrogatepass_utf8_hex": text.encode("utf-8", "surrogatepass").hex(),
            }
        return {"kind": type(value).__name__, "text": text}
    if isinstance(value, (bytes, bytearray)):
        return {"kind": type(value).__name__, "hex": bytes(value).hex()}
    if isinstance(value, memoryview):
        return {
            "kind": "memoryview",
            "hex": value.tobytes().hex(),
            "format": value.format,
            "shape": list(value.shape),
            "contiguous": value.c_contiguous,
        }
    if isinstance(value, tuple):
        return {"tuple": [normal(item) for item in value]}
    if isinstance(value, list):
        return [normal(item) for item in value]
    if isinstance(value, dict):
        return {
            stable_text(str(key)): normal(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, types.MappingProxyType):
        return {"kind": "mappingproxy", "value": normal(dict(value))}
    if isinstance(value, type):
        return {"kind": "type", "name": value.__name__}
    return {"kind": type(value).__name__, "repr": stable_text(repr(value))}


def attempted(action):
    try:
        return {"status": "ok", "value": normal(action())}
    except Exception as exc:
        result = {
            "status": "error",
            "type": type(exc).__name__,
            "args": normal(exc.args),
        }
        if hasattr(exc, "msg") and hasattr(exc, "pos"):
            result["pattern_error"] = {
                key: normal(getattr(exc, key, None))
                for key in ("msg", "pattern", "pos", "lineno", "colno")
            }
        return result


def match_snapshot(match, subject=None):
    if match is None:
        return None
    groups = match.groups()
    named = match.groupdict()
    return {
        "span": normal(match.span()),
        "regs": normal(match.regs),
        "regs_cached": match.regs is match.regs,
        "group0": normal(match.group(0)),
        "group0_same_subject": match.group(0) is subject,
        "getitem0_same_subject": match[0] is subject,
        "groups": normal(groups),
        "group_same_subject": [value is subject for value in groups],
        "groupdict": normal(named),
        "named_same_subject": {
            name: value is subject for name, value in sorted(named.items())
        },
        "pos": match.pos,
        "endpos": match.endpos,
        "lastindex": match.lastindex,
        "lastgroup": match.lastgroup,
        "subject_same": match.string is subject,
        "subject_kind": type(match.string).__name__,
        "pattern_kind": type(match.re.pattern).__name__,
    }


@dataclass(frozen=True, slots=True)
class Case:
    family: str
    label: str
    action: object


def byte_subject(kind, payload):
    if kind == "bytes":
        return payload
    if kind == "bytes-subclass":
        return Blob(payload)
    if kind == "bytearray":
        return bytearray(payload)
    if kind == "memoryview":
        return memoryview(payload)
    if kind == "mutable-memoryview":
        return memoryview(bytearray(payload))
    if kind == "array":
        return array.array("B", payload)
    raise ValueError(kind)


def collect_rows(rows, subject):
    output = []
    for row in rows:
        if isinstance(row, tuple):
            output.append({
                "value": normal(row),
                "same_subject": [part is subject for part in row],
            })
        else:
            output.append({
                "value": normal(row),
                "same_subject": row is subject,
            })
    return {
        "rows": output,
        "adjacent_same": [left is right for left, right in zip(rows, rows[1:])],
    }


def bytes_action(module, expression, payload, kind, operation, pos, endpos):
    subject = byte_subject(kind, payload)
    pattern = module.compile(expression)
    if operation == "findall":
        return collect_rows(pattern.findall(subject, pos, endpos), subject)
    if operation == "finditer":
        return [
            match_snapshot(match, subject)
            for match in pattern.finditer(subject, pos, endpos)
        ]
    if operation == "scanner-search":
        scanner = pattern.scanner(subject, pos, endpos)
        result = []
        for _ in range(len(payload) + 3):
            match = scanner.search()
            result.append(match_snapshot(match, subject))
            if match is None:
                break
        else:
            raise AssertionError("scanner did not terminate")
        return result
    if operation == "scanner-match":
        scanner = pattern.scanner(subject, pos, endpos)
        result = []
        for _ in range(len(payload) + 3):
            match = scanner.match()
            result.append(match_snapshot(match, subject))
            if match is None:
                break
        else:
            raise AssertionError("scanner did not terminate")
        return result
    return match_snapshot(getattr(pattern, operation)(subject, pos, endpos), subject)


def text_action(module, expression, payload, subclass, operation, pos, endpos):
    subject = Text(payload) if subclass else payload
    pattern = module.compile(expression)
    if operation == "findall":
        return collect_rows(pattern.findall(subject, pos, endpos), subject)
    if operation == "finditer":
        return [
            match_snapshot(match, subject)
            for match in pattern.finditer(subject, pos, endpos)
        ]
    return match_snapshot(getattr(pattern, operation)(subject, pos, endpos), subject)


def pattern_contract(module, expression, flags, operation):
    module.purge()
    source = expression
    pattern = module.compile(source, flags)
    subject = b"abc abc" if isinstance(source, bytes) else "abc abc"
    if operation == "repr":
        return repr(pattern)
    if operation == "source-kind":
        return {"kind": type(pattern.pattern).__name__, "same": pattern.pattern is source}
    if operation == "flags":
        return pattern.flags
    if operation == "groups":
        return pattern.groups
    if operation == "groupindex":
        return {"kind": type(pattern.groupindex).__name__, "value": dict(pattern.groupindex)}
    if operation == "groupindex-identity":
        return pattern.groupindex is pattern.groupindex
    if operation == "cache-identity":
        return module.compile(source, flags) is pattern
    if operation == "copy":
        return copy.copy(pattern) is pattern
    if operation == "deepcopy":
        return copy.deepcopy(pattern) is pattern
    if operation == "weakref":
        return weakref.ref(pattern)() is pattern
    if operation == "pickle":
        restored = pickle.loads(pickle.dumps(pattern))
        return {
            "pattern": normal(restored.pattern),
            "flags": restored.flags,
            "groups": restored.groups,
            "groupindex": dict(restored.groupindex),
            "search": match_snapshot(restored.search(subject), subject),
        }
    if operation == "equal-compiled":
        module.purge()
        other = module.compile(source, flags)
        return {"equal": pattern == other, "same_hash": hash(pattern) == hash(other)}
    if operation.startswith("readonly-"):
        name = operation.removeprefix("readonly-")
        return setattr(pattern, name, None)
    if operation == "generic":
        alias = module.Pattern[str]
        return {
            "origin_name": alias.__origin__.__name__,
            "args": [item.__name__ for item in alias.__args__],
        }
    raise ValueError(operation)


def match_contract(module, expression, subject, operation, key_kind):
    match = module.compile(expression).search(subject)
    if match is None:
        raise AssertionError("independent object-contract expected a match")
    trace = []
    keys = {
        "zero": 0,
        "one": 1,
        "minus-one": -1,
        "true": True,
        "false": False,
        "float": 1.0,
        "string": "name",
        "bytes": b"name",
        "index": Index(1, trace, "group"),
        "negative-index": Index(-1, trace, "group"),
        "raising-index": Index(1, trace, "group", "raise"),
        "noninteger-index": Index(1, trace, "group", "noninteger"),
        "huge-index": Index(1 << 100, trace, "group"),
        "none": None,
        "object": object(),
    }
    key = keys[key_kind]

    def action():
        if operation == "group":
            return match.group(key)
        if operation == "getitem":
            return match[key]
        if operation == "start":
            return match.start(key)
        if operation == "end":
            return match.end(key)
        if operation == "span":
            return match.span(key)
        raise ValueError(operation)

    result = attempted(action)
    result["trace"] = normal(trace)
    return result


def window_contract(module, expression, subject, operation, start_kind, end_kind):
    trace = []

    def make(kind, label):
        options = {
            "zero": 0,
            "one": 1,
            "negative": -5,
            "huge": 1 << 100,
            "true": True,
            "false": False,
            "float": 1.0,
            "none": None,
            "normal-index": Index(1, trace, label),
            "raising-index": Index(1, trace, label, "raise"),
            "bad-index": Index(1, trace, label, "noninteger"),
        }
        return options[kind]

    start = make(start_kind, "pos")
    end = make(end_kind, "endpos")
    pattern = module.compile(expression)

    def action():
        if operation == "finditer":
            return [match_snapshot(item, subject) for item in pattern.finditer(subject, start, end)]
        if operation == "scanner":
            scanner = pattern.scanner(subject, start, end)
            return [match_snapshot(scanner.search(), subject) for _ in range(3)]
        result = getattr(pattern, operation)(subject, start, end)
        if operation == "findall":
            return collect_rows(result, subject)
        return match_snapshot(result, subject)

    result = attempted(action)
    result["trace"] = normal(trace)
    return result


def signature_contract(module, owner, name):
    if owner == "module":
        value = getattr(module, name)
    elif owner == "pattern-class":
        value = getattr(module.Pattern, name)
    elif owner == "pattern-bound":
        value = getattr(module.compile("(?P<name>a)"), name)
    elif owner == "match-class":
        value = getattr(module.Match, name)
    elif owner == "match-bound":
        value = getattr(module.search("(?P<name>a)", "a"), name)
    else:
        raise ValueError(owner)
    return str(inspect.signature(value))


def warning_contract(module, action, text, byte_mode):
    expression = text.encode("ascii") if byte_mode else text
    subject = b"aaa" if byte_mode else "aaa"
    replacement = b"x" if byte_mode else "x"
    module.purge()
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        if action == "compile":
            result = attempted(lambda: module.compile(expression))
        elif action == "split-positional":
            result = attempted(lambda: module.split(expression, subject, 1))
        elif action == "split-flags-positional":
            result = attempted(lambda: module.split(expression, subject, 1, 0))
        elif action == "sub-positional":
            result = attempted(lambda: module.sub(expression, replacement, subject, 1))
        elif action == "sub-flags-positional":
            result = attempted(lambda: module.sub(expression, replacement, subject, 1, 0))
        elif action == "subn-positional":
            result = attempted(lambda: module.subn(expression, replacement, subject, 1))
        elif action == "subn-flags-positional":
            result = attempted(lambda: module.subn(expression, replacement, subject, 1, 0))
        else:
            raise ValueError(action)
    return {
        "result": result,
        "warnings": [
            {
                "category": item.category.__name__,
                "message": str(item.message),
                "at_probe": Path(item.filename).name == Path(__file__).name,
            }
            for item in captured
        ],
    }


def mutable_contract(module, operation, kind, expression):
    backing = bytearray(b"a1 b2 c3")
    subject = backing if kind == "bytearray" else memoryview(backing)
    pattern = module.compile(expression)
    if operation == "match-mutation":
        found = pattern.search(subject)
        before = match_snapshot(found, subject)
        backing[0] = ord("z")
        after = match_snapshot(found, subject)
        resize = attempted(lambda: backing.append(ord("!")))
        return {
            "before": before,
            "after": after,
            "resize": resize,
            "final": normal(backing),
        }
    if operation == "iterator-mutation":
        iterator = pattern.finditer(subject)
        first = next(iterator, None)
        backing[3] = ord("y")
        remaining = [match_snapshot(value, subject) for value in iterator]
        return {
            "first": match_snapshot(first, subject),
            "remaining": remaining,
            "final": normal(backing),
        }
    if operation == "scanner-mutation":
        scanner = pattern.scanner(subject)
        first = scanner.search()
        backing[3] = ord("y")
        values = []
        for _ in range(5):
            value = scanner.search()
            values.append(match_snapshot(value, subject))
            if value is None:
                break
        return {
            "first": match_snapshot(first, subject),
            "remaining": values,
            "final": normal(backing),
        }
    raise ValueError(operation)


def hash_contract(module, byte_mode, behavior, operation):
    trace = []
    module.purge()
    pattern = (
        HashBlob(b"a", trace, behavior)
        if byte_mode else HashText("a", trace, behavior)
    )
    subject = b"aba" if byte_mode else "aba"

    def invoke():
        if operation == "compile":
            return {"source_kind": type(module.compile(pattern).pattern).__name__}
        result = getattr(module, operation)(pattern, subject)
        if operation == "finditer":
            return [match_snapshot(item, subject) for item in result]
        if operation == "findall":
            return collect_rows(result, subject)
        return match_snapshot(result, subject)

    result = attempted(invoke)
    result["trace"] = normal(trace)
    return result


def group_capture_contract(module, expression, subject, operation):
    match = module.compile(expression).search(subject)
    if match is None:
        return None
    if operation == "copy":
        return copy.copy(match) is match
    if operation == "deepcopy":
        return copy.deepcopy(match) is match
    if operation == "pickle":
        return pickle.dumps(match)
    if operation == "weakref":
        return weakref.ref(match)() is match
    if operation == "repr":
        return repr(match)
    if operation == "regs-cache":
        return match.regs is match.regs
    if operation == "re-same":
        return match.re is module.compile(expression)
    if operation == "string-same":
        return match.string is subject
    if operation.startswith("readonly-"):
        return setattr(match, operation.removeprefix("readonly-"), None)
    if operation == "generic":
        alias = module.Match[str]
        return {
            "origin_name": alias.__origin__.__name__,
            "args": [item.__name__ for item in alias.__args__],
        }
    if operation == "tracked":
        return gc.is_tracked(match)
    raise ValueError(operation)


def build_cases():
    cases = []

    def add(family, label, action):
        cases.append(Case(family, label, action))

    byte_patterns = (
        rb"a*", rb"(a*)", rb"(?P<all>a*)", rb".*",
        rb"(?P<all>.*)", rb"(a*)(a?)", rb"(?:a|)*",
        rb"(?P<x>a)(?P<y>a)?", rb"a|", rb"[a-z]+",
    )
    lengths = (0, 1, 2, 3, 7, 31, 63, 64, 65, 127, 128, 129)
    for pattern_index, expression in enumerate(byte_patterns):
        for length in lengths:
            payload = b"a" * length
            windows = dict.fromkeys(((0, length), (0, max(length - 1, 0)), (min(1, length), length)))
            for kind in ("bytes", "bytes-subclass", "bytearray", "memoryview", "mutable-memoryview", "array"):
                for pos, endpos in windows:
                    for operation in ("search", "match", "fullmatch", "findall", "finditer"):
                        label = f"p{pattern_index}:{kind}:len{length}:{operation}:{pos}:{endpos}"
                        add(
                            "whole-bytes-and-capture-identity", label,
                            lambda module, e=expression, p=payload, k=kind, op=operation, a=pos, b=endpos:
                                bytes_action(module, e, p, k, op, a, b),
                        )

    text_patterns = (r"a*", r"(a*)", r"(?P<all>a*)", r".*", r"(?P<all>.*)", r"(a*)(a?)", r"a|")
    text_values = ("", "a", "aa", "aaa", "é", "éé", "😀", "a😀a", "a\x00a", "a" * 63, "a" * 64, "a" * 65, "\ud800")
    for pattern_index, expression in enumerate(text_patterns):
        for value_index, payload in enumerate(text_values):
            windows = dict.fromkeys(((0, len(payload)), (0, max(len(payload) - 1, 0)), (min(1, len(payload)), len(payload))))
            for subclass in (False, True):
                for pos, endpos in windows:
                    for operation in ("search", "match", "fullmatch", "findall", "finditer"):
                        label = f"p{pattern_index}:v{value_index}:subclass{int(subclass)}:{operation}:{pos}:{endpos}"
                        add(
                            "whole-text-and-capture-identity", label,
                            lambda module, e=expression, p=payload, s=subclass, op=operation, a=pos, b=endpos:
                                text_action(module, e, p, s, op, a, b),
                        )

    expressions = (
        ("plain-text", "abc", 0),
        ("named-text", r"(?P<name>abc)", 0),
        ("subclass-text", Text("abc"), 0),
        ("plain-bytes", b"abc", 0),
        ("named-bytes", rb"(?P<name>abc)", 0),
        ("subclass-bytes", Blob(b"abc"), 0),
        ("ignorecase", "abc", int(re.IGNORECASE)),
        ("ascii", "abc", int(re.ASCII)),
        ("multiline", "abc", int(re.MULTILINE)),
        ("dotall", "abc", int(re.DOTALL)),
        ("combined", "abc", int(re.IGNORECASE | re.MULTILINE)),
        ("repr-199", "a" * 199, 0),
        ("repr-200", "a" * 200, 0),
        ("repr-201", "a" * 201, 0),
        ("repr-wide", "é" * 100, 0),
    )
    pattern_ops = (
        "repr", "source-kind", "flags", "groups", "groupindex",
        "groupindex-identity", "cache-identity", "copy", "deepcopy",
        "weakref", "pickle", "equal-compiled", "generic",
        "readonly-pattern", "readonly-flags", "readonly-groups", "readonly-groupindex",
        "readonly-search", "readonly-match", "readonly-fullmatch", "readonly-findall",
        "readonly-finditer", "readonly-scanner", "readonly-split", "readonly-sub", "readonly-subn",
    )
    for tag, expression, flags in expressions:
        for operation in pattern_ops:
            add(
                "compiled-pattern-contract", f"{tag}:{operation}",
                lambda module, e=expression, f=flags, op=operation: pattern_contract(module, e, f, op),
            )

    keys = (
        "zero", "one", "minus-one", "true", "false", "float", "string",
        "bytes", "index", "negative-index", "raising-index", "noninteger-index",
        "huge-index", "none", "object",
    )
    for byte_mode in (False, True):
        expression = rb"(?P<name>a)(b)?" if byte_mode else r"(?P<name>a)(b)?"
        subject = b"a" if byte_mode else "a"
        for operation in ("group", "getitem", "start", "end", "span"):
            for key in keys:
                add(
                    "match-group-index-errors-and-side-effects",
                    f"{'bytes' if byte_mode else 'text'}:{operation}:{key}",
                    lambda module, e=expression, s=subject, op=operation, k=key:
                        match_contract(module, e, s, op, k),
                )

    window_pairs = (
        ("zero", "zero"), ("zero", "one"), ("one", "one"),
        ("negative", "one"), ("true", "false"), ("normal-index", "normal-index"),
        ("normal-index", "raising-index"), ("raising-index", "normal-index"),
        ("normal-index", "bad-index"), ("bad-index", "normal-index"),
        ("huge", "normal-index"), ("normal-index", "huge"),
        ("none", "one"), ("zero", "none"), ("float", "one"), ("zero", "float"),
    )
    for byte_mode in (False, True):
        expression = rb"(?P<name>a)" if byte_mode else r"(?P<name>a)"
        subject = b"a a" if byte_mode else "a a"
        for operation in ("search", "match", "fullmatch", "findall", "finditer", "scanner"):
            for start, end in window_pairs:
                add(
                    "window-index-order-and-exact-errors",
                    f"{'bytes' if byte_mode else 'text'}:{operation}:{start}:{end}",
                    lambda module, e=expression, s=subject, op=operation, a=start, b=end:
                        window_contract(module, e, s, op, a, b),
                )

    module_names = (
        "compile", "search", "match", "fullmatch", "findall", "finditer",
        "split", "sub", "subn", "escape", "purge",
    )
    pattern_names = (
        "search", "match", "fullmatch", "findall", "finditer", "scanner",
        "split", "sub", "subn",
    )
    match_names = ("group", "groups", "groupdict", "start", "end", "span", "expand")
    for owner, names in (
        ("module", module_names),
        ("pattern-class", pattern_names),
        ("pattern-bound", pattern_names),
        ("match-class", match_names),
        ("match-bound", match_names),
    ):
        for name in names:
            add(
                "inspectable-public-signatures", f"{owner}:{name}",
                lambda module, o=owner, n=name: signature_contract(module, o, n),
            )

    warning_patterns = ("[[a]", "[a&&b]", "[a~~b]", "[a||b]", "[a--b]")
    for byte_mode in (False, True):
        for expression in warning_patterns:
            add(
                "warning-messages-and-call-site", f"{'bytes' if byte_mode else 'text'}:compile:{expression}",
                lambda module, e=expression, b=byte_mode: warning_contract(module, "compile", e, b),
            )
        for operation in (
            "split-positional", "split-flags-positional", "sub-positional",
            "sub-flags-positional", "subn-positional", "subn-flags-positional",
        ):
            add(
                "warning-messages-and-call-site", f"{'bytes' if byte_mode else 'text'}:{operation}",
                lambda module, op=operation, b=byte_mode: warning_contract(module, op, "a", b),
            )

    for kind in ("bytearray", "memoryview"):
        for expression in (rb"(?P<letter>[a-z])(?P<digit>\d)", rb"[a-z]\d", rb"(?:[a-z]\d)*"):
            for operation in ("match-mutation", "iterator-mutation", "scanner-mutation"):
                add(
                    "mutable-buffer-and-scanner-lifetime",
                    f"{kind}:{expression!r}:{operation}",
                    lambda module, k=kind, e=expression, op=operation:
                        mutable_contract(module, op, k, e),
                )

    for byte_mode in (False, True):
        for behavior in ("normal", "raise"):
            for operation in ("compile", "search", "match", "fullmatch", "findall", "finditer"):
                add(
                    "pattern-hash-call-count-and-exact-errors",
                    f"{'bytes' if byte_mode else 'text'}:{behavior}:{operation}",
                    lambda module, b=byte_mode, h=behavior, op=operation:
                        hash_contract(module, b, h, op),
                )

    for byte_mode in (False, True):
        expression = rb"(?P<name>a)(b)?" if byte_mode else r"(?P<name>a)(b)?"
        subject = b"a" if byte_mode else "a"
        for operation in (
            "copy", "deepcopy", "pickle", "weakref", "repr", "regs-cache",
            "re-same", "string-same", "generic", "tracked", "readonly-re",
            "readonly-string", "readonly-pos", "readonly-endpos",
            "readonly-lastindex", "readonly-lastgroup", "readonly-regs",
        ):
            add(
                "match-copy-pickle-gc-and-readonly", f"{'bytes' if byte_mode else 'text'}:{operation}",
                lambda module, e=expression, s=subject, op=operation:
                    group_capture_contract(module, e, s, op),
            )

    randomizer = random.Random(SEED)
    seeded_patterns = (
        rb"a*", rb"(a*)", rb"(?P<x>a*)", rb"[ab]+",
        rb"(a?)(b?)", rb"(?:ab|a|)", rb"(?P<x>a)(?P<y>b)?",
        rb"(?:a|b)*", rb"a{0,3}", rb"(?=a)a",
    )
    for index in range(160):
        length = randomizer.randrange(0, 48)
        payload = bytes(randomizer.choice(b"abxy\x00\n") for _ in range(length))
        expression = randomizer.choice(seeded_patterns)
        kind = randomizer.choice(("bytes", "bytes-subclass", "bytearray", "memoryview", "array"))
        start = randomizer.randrange(0, length + 1)
        end = randomizer.randrange(start, length + 1)
        for operation in ("search", "match", "fullmatch", "findall", "finditer", "scanner-search", "scanner-match"):
            add(
                "independent-seeded-object-fuzz",
                f"seed{SEED:x}:case{index}:{kind}:{operation}:{start}:{end}",
                lambda module, e=expression, p=payload, k=kind, op=operation, a=start, b=end:
                    bytes_action(module, e, p, k, op, a, b),
            )

    return tuple(cases)


def evaluate(cases, module):
    records = []
    for case in cases:
        records.append({
            "family": case.family,
            "case": case.label,
            "observation": attempted(lambda c=case: c.action(module)),
        })
    return records


def summarize(records, expected):
    counts = collections.Counter()
    failed_counts = collections.Counter()
    failures = []
    for actual, oracle in zip(records, expected, strict=True):
        if actual["family"] != oracle["family"] or actual["case"] != oracle["case"]:
            raise AssertionError("independent oracle case identity drift")
        counts[actual["family"]] += 1
        if actual["observation"] != oracle["observation"]:
            failed_counts[actual["family"]] += 1
            failures.append({
                "family": actual["family"],
                "case": actual["case"],
                "expected": oracle["observation"],
                "actual": actual["observation"],
            })
    return {
        "checks": len(records),
        "failed": len(failures),
        "families": [
            {"family": family, "checks": checks, "failed": failed_counts[family]}
            for family, checks in sorted(counts.items())
        ],
        "failures": failures,
    }



ROOT = Path(__file__).resolve().parents[1]
OUTPUT_NAMES = {
    "stdlib": "rust-v7-object-stdlib.json.gz",
    "ast": "rust-v7-object-ast.json.gz",
    "vm": "rust-v7-object-vm.json.gz",
    "rust": "rust-v7-object-rust.json.gz",
    "zig": "rust-v7-object-zig.json.gz",
}
CANDIDATE_SOURCES = {
    "ast": ("candidates/ast_candidate.py",),
    "vm": ("candidates/vm_candidate.py", "candidates/_vm_native.c"),
    "rust": (
        "candidates/rust_candidate.py",
        "candidates/rust/py_bridge.c",
        "candidates/rust/Cargo.toml",
        "candidates/rust/Cargo.lock",
        "candidates/rust/src/lib.rs",
        "candidates/rust/src/newline.rs",
        "candidates/rust/src/search.rs",
        "candidates/rust/src/stack.rs",
        "candidates/rust/src/unicode_tables.rs",
    ),
    "zig": (
        "candidates/zig_candidate.py",
        "candidates/zig/mini_regex.zig",
        "candidates/zig/py_bridge.c",
    ),
}
NATIVE_MODULES = {
    "vm": ("candidates._vm_native",),
    "rust": ("candidates._rust_bridge",),
    "zig": ("candidates._zig_bridge",),
}


def sha256_file(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def common_provenance():
    return {
        "python_implementation": sys.implementation.name,
        "python_version": ".".join(str(part) for part in sys.version_info[:3]),
        "python_cache_tag": sys.implementation.cache_tag,
        "unicode_version": unicodedata.unidata_version,
        "python_executable_sha256": sha256_file(Path(sys.executable)),
        "stdlib_re_sha256": sha256_file(Path(re.__file__)),
        "suite_path": "tools/rust_v7_object_oracle.py",
        "suite_sha256": sha256_file(Path(__file__)),
        "seed": SEED,
        "seed_hex": f"0x{SEED:016x}",
        "normalization": {
            "ephemeral_object_addresses": "0x<address>",
            "lone_surrogates": "surrogatepass_utf8_hex",
        },
    }


def candidate_provenance(label):
    if label == "stdlib":
        return {}
    result = {
        relative: sha256_file(ROOT / relative)
        for relative in CANDIDATE_SOURCES[label]
    }
    for name in NATIVE_MODULES.get(label, ()):
        native = importlib.import_module(name)
        path = Path(native.__file__).resolve()
        try:
            key = path.relative_to(ROOT).as_posix()
        except ValueError:
            key = f"loaded-native/{path.name}"
        result[key] = sha256_file(path)
    if label == "zig":
        native = ROOT / "candidates" / "_zig_probe.so"
        if native.is_file():
            result["candidates/_zig_probe.so"] = sha256_file(native)
    return result


def write_deterministic_gzip(path, report):
    payload = (
        json.dumps(
            report,
            sort_keys=True,
            ensure_ascii=True,
            allow_nan=False,
            separators=(",", ":"),
        ).encode("ascii")
        + b"\n"
    )
    with path.open("wb") as raw:
        with gzip.GzipFile(
            filename="",
            mode="wb",
            compresslevel=9,
            fileobj=raw,
            mtime=0,
        ) as compressed:
            compressed.write(payload)


def read_deterministic_gzip(path):
    with gzip.open(path, "rt", encoding="ascii") as stream:
        return json.load(stream)


def validate_report(report, label, expected_cases, provenance):
    if report.get("schema") != SCHEMA:
        raise AssertionError(f"{label}: unexpected object-oracle schema")
    if report.get("module_label") != label:
        raise AssertionError(f"{label}: object-oracle module drift")
    if report.get("provenance") != provenance:
        raise AssertionError(f"{label}: pinned interpreter or suite drift")
    if report.get("checks") != expected_cases:
        raise AssertionError(f"{label}: object-oracle denominator drift")
    if len(report.get("records", ())) != expected_cases:
        raise AssertionError(f"{label}: incomplete object-oracle records")
    if report.get("failed") != len(report.get("failures", ())):
        raise AssertionError(f"{label}: incomplete object-oracle failures")
    if sum(item["checks"] for item in report["families"]) != expected_cases:
        raise AssertionError(f"{label}: object-oracle family denominator drift")
    if sum(item["failed"] for item in report["families"]) != report["failed"]:
        raise AssertionError(f"{label}: object-oracle family failure drift")
    if label == "stdlib" and report["failed"] != 0:
        raise AssertionError("pinned stdlib self-oracle has unexplained failures")


def archive_report(output, label, module_name, records, expected, provenance):
    summary = summarize(records, expected)
    report = {
        "schema": SCHEMA,
        "module_label": label,
        "module": module_name,
        "oracle": "CPython 3.14.6 standard-library re",
        "provenance": provenance,
        "candidate_source_sha256": candidate_provenance(label),
        "checks": summary["checks"],
        "failed": summary["failed"],
        "families": summary["families"],
        "failures": summary["failures"],
        "records": records,
    }
    validate_report(report, label, len(expected), provenance)
    destination = output / OUTPUT_NAMES[label]
    write_deterministic_gzip(destination, report)
    reloaded = read_deterministic_gzip(destination)
    if reloaded != report:
        raise AssertionError(f"{label}: evidence does not exactly round-trip")
    validate_report(reloaded, label, len(expected), provenance)
    print(
        json.dumps(
            {
                "module": label,
                "checks": report["checks"],
                "failed": report["failed"],
                "archive": destination.as_posix(),
                "archive_sha256": sha256_file(destination),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return report


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "candidates" / "evidence",
        help="directory for the five complete deterministic evidence archives",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate the existing five archives without changing them",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if tuple(sys.version_info[:3]) != PINNED:
        raise SystemExit(f"requires exact pinned CPython {PINNED!r}")
    output = args.output_dir.resolve()
    if not output.is_dir():
        raise SystemExit("the evidence output directory must already exist")
    cases = build_cases()
    if len(cases) != 14_783:
        raise SystemExit(f"frozen object-oracle denominator drift: {len(cases)}")
    provenance = common_provenance()

    if args.check:
        for label in OUTPUT_NAMES:
            path = output / OUTPUT_NAMES[label]
            report = read_deterministic_gzip(path)
            validate_report(report, label, len(cases), provenance)
            if label != "stdlib":
                current = candidate_provenance(label)
                if report["candidate_source_sha256"] != current:
                    raise AssertionError(f"{label}: production source or native-binary drift")
            print(
                json.dumps(
                    {
                        "module": label,
                        "checks": report["checks"],
                        "failed": report["failed"],
                        "archive_sha256": sha256_file(path),
                        "verified": True,
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
        return

    reference = evaluate(cases, re)
    repeated_reference = evaluate(cases, re)
    self_check = summarize(repeated_reference, reference)
    if self_check["failed"]:
        raise SystemExit(
            f"pinned stdlib self-oracle failed {self_check['failed']} "
            f"of {self_check['checks']} object-contract cases"
        )
    archive_report(
        output, "stdlib", "re", repeated_reference, reference, provenance
    )
    for label, name in MODULES:
        module = importlib.import_module(name)
        records = evaluate(cases, module)
        archive_report(output, label, name, records, reference, provenance)


if __name__ == "__main__":
    main()
