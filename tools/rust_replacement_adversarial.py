#!/usr/bin/env python3
"""Deterministically compare Python and Rust replacement side effects."""

from __future__ import annotations

import argparse
import array
import collections
import gc
import gzip
import hashlib
import importlib
import importlib.util
import inspect
import json
import re
import sys
import weakref
from pathlib import Path


SCHEMA = "rebar-rust-native-replacement-adversarial-v1"


class TextSubclass(str):
    pass


class BytesSubclass(bytes):
    pass


class UnhashableText(str):
    __hash__ = None


class UnhashableBytes(bytes):
    __hash__ = None


class ExplodingHashText(str):
    def __new__(cls, value, trace):
        result = super().__new__(cls, value)
        result.trace = trace
        return result

    def __hash__(self):
        self.trace.append(("replacement-hash", "text", "exploding"))
        raise AssertionError("replacement-hash-sentinel")


class ExplodingHashBytes(bytes):
    def __new__(cls, value, trace):
        result = super().__new__(cls, value)
        result.trace = trace
        return result

    def __hash__(self):
        self.trace.append(("replacement-hash", "bytes", "exploding"))
        raise AssertionError("replacement-hash-sentinel")


class CountingHashText(str):
    def __new__(cls, value, trace):
        result = super().__new__(cls, value)
        result.trace = trace
        return result

    def __hash__(self):
        self.trace.append(("replacement-hash", "text", "counted"))
        return hash(str(self))


class CountingHashBytes(bytes):
    def __new__(cls, value, trace):
        result = super().__new__(cls, value)
        result.trace = trace
        return result

    def __hash__(self):
        self.trace.append(("replacement-hash", "bytes", "counted"))
        return hash(bytes(self))


class NonIntegerHashText(str):
    def __new__(cls, value, trace):
        result = super().__new__(cls, value)
        result.trace = trace
        return result

    def __hash__(self):
        self.trace.append(("replacement-hash", "text", "non-integer"))
        return "invalid-hash"


class NonIntegerHashBytes(bytes):
    def __new__(cls, value, trace):
        result = super().__new__(cls, value)
        result.trace = trace
        return result

    def __hash__(self):
        self.trace.append(("replacement-hash", "bytes", "non-integer"))
        return "invalid-hash"


class BytearraySubclass(bytearray):
    pass


class PythonBuffer:
    def __init__(self, data, trace, label):
        self.data = bytearray(data)
        self.trace = trace
        self.label = label

    def __buffer__(self, flags):
        self.trace.append(("buffer-export", self.label, flags))
        return memoryview(self.data)

    def __release_buffer__(self, view):
        self.trace.append(("buffer-release", self.label))

    def __repr__(self):
        return f"PythonBuffer({bytes(self.data)!r}, {self.label!r})"


class MatchCycle:
    __slots__ = ("match", "cycle", "__weakref__")

    def __init__(self, match):
        self.match = match
        self.cycle = self


class IndexValue:
    def __init__(self, value, trace):
        self.value = value
        self.trace = trace

    def __index__(self):
        self.trace.append(("index", self.value))
        return self.value


def normalise(value):
    if value is None or isinstance(value, (bool, int, float)):
        return [type(value).__name__, value]
    if isinstance(value, str):
        return [type(value).__name__, str(value)]
    if isinstance(value, bytes):
        return [type(value).__name__, bytes(value).hex()]
    if isinstance(value, (bytearray, memoryview)):
        return [type(value).__name__, bytes(value).hex()]
    if isinstance(value, array.array):
        return ["array:" + value.typecode, value.tobytes().hex()]
    if isinstance(value, (list, tuple)):
        return [type(value).__name__, [normalise(item) for item in value]]
    if isinstance(value, dict):
        return [
            "dict",
            [
                [normalise(key), normalise(item)]
                for key, item in sorted(value.items(), key=lambda pair: repr(pair[0]))
            ],
        ]
    return [type(value).__name__, repr(value)]


def observed(module, action):
    trace = []
    try:
        result, subject = action(module, trace)
        identity = result[0] is subject if isinstance(result, tuple) else result is subject
        return {
            "status": "ok",
            "value": normalise(result),
            "source_identity": identity,
            "trace": normalise(trace),
        }
    except BaseException as error:
        return {
            "status": "error",
            "type": type(error).__name__,
            "message": str(error),
            "args": normalise(error.args),
            "trace": normalise(trace),
        }


def capture_match(trace, match):
    trace.append(
        (
            "match",
            match.span(),
            normalise(match.group(0)),
            normalise(match.groups()),
            normalise(match.groupdict()),
        )
    )


def build_cases(*, deep=False):
    cases = []

    def add(cohort, category, name, action):
        cases.append((cohort, category, name, action))

    counts = (
        ("zero", lambda state: 0),
        ("one", lambda state: 1),
        ("two", lambda state: 2),
        ("negative", lambda state: -1),
        ("index-zero", lambda state: IndexValue(0, state)),
        ("index-one", lambda state: IndexValue(1, state)),
        ("index-negative", lambda state: IndexValue(-1, state)),
        ("none", lambda state: None),
        ("float", lambda state: 1.5),
    )
    returns = (
        ("text", lambda: "X"),
        ("text-subclass", lambda: TextSubclass("X")),
        ("bytes", lambda: b"X"),
        ("bytes-subclass", lambda: BytesSubclass(b"X")),
        ("bytearray", lambda: bytearray(b"X")),
        ("memoryview", lambda: memoryview(b"X")),
        ("array", lambda: array.array("B", [88])),
        ("none", lambda: None),
        ("int", lambda: 7),
        ("bool", lambda: True),
        ("list", lambda: ["X"]),
        ("tuple", lambda: ("X",)),
    )
    sources = (
        ("text", lambda: "aba"),
        ("text-subclass", lambda: TextSubclass("aba")),
        ("bytes", lambda: b"aba"),
        ("bytes-subclass", lambda: BytesSubclass(b"aba")),
        ("bytearray", lambda: bytearray(b"aba")),
        ("memoryview", lambda: memoryview(b"aba")),
        ("array", lambda: array.array("B", [97, 98, 97])),
    )
    for source_name, source_factory in sources:
        pattern = "a" if source_name.startswith("text") else b"a"
        for return_name, return_factory in returns:
            for count_name, count_factory in counts:
                for method in ("sub", "subn"):

                    def action(
                        module, state, sf=source_factory, rf=return_factory,
                        cf=count_factory, p=pattern, name=method
                    ):
                        subject = sf()

                        def callback(match):
                            capture_match(state, match)
                            return rf()

                        return (
                            getattr(module.compile(p), name)(
                                callback, subject, cf(state)
                            ),
                            subject,
                        )

                    add(
                        "canonical-8264", "callback-types",
                        f"{source_name}/{return_name}/{count_name}/{method}", action,
                    )

    wrong = (
        ("none", lambda: None),
        ("int", lambda: 3),
        ("bool", lambda: True),
        ("bytearray", lambda: bytearray(b"X")),
        ("memoryview", lambda: memoryview(b"X")),
        ("array", lambda: array.array("B", [88])),
        ("text", lambda: "X"),
        ("bytes", lambda: b"X"),
        ("bad-text-template", lambda: r"\g<missing>"),
        ("bad-bytes-template", lambda: rb"\g<missing>"),
        ("invalid-text-template", lambda: r"\x"),
        ("invalid-bytes-template", lambda: rb"\x"),
    )
    for is_text in (True, False):
        pattern = "a" if is_text else b"a"
        source_cases = (
            (
                ("nomatch-text", lambda: "zzz"),
                ("match-text", lambda: "aza"),
                ("nomatch-text-sub", lambda: TextSubclass("zzz")),
                ("match-text-sub", lambda: TextSubclass("aza")),
            )
            if is_text
            else (
                ("nomatch-bytes", lambda: b"zzz"),
                ("match-bytes", lambda: b"aza"),
                ("nomatch-bytes-sub", lambda: BytesSubclass(b"zzz")),
                ("match-bytes-sub", lambda: BytesSubclass(b"aza")),
                ("nomatch-bytearray", lambda: bytearray(b"zzz")),
                ("match-bytearray", lambda: bytearray(b"aza")),
                ("nomatch-memoryview", lambda: memoryview(b"zzz")),
                ("match-memoryview", lambda: memoryview(b"aza")),
            )
        )
        for source_name, source_factory in source_cases:
            for replacement_name, replacement_factory in wrong:
                for count_name, count_factory in counts:
                    for method in ("sub", "subn"):

                        def action(
                            module, state, sf=source_factory, rf=replacement_factory,
                            cf=count_factory, p=pattern, name=method
                        ):
                            subject = sf()
                            return (
                                getattr(module.compile(p), name)(
                                    rf(), subject, cf(state)
                                ),
                                subject,
                            )

                        add(
                            "canonical-8264", "validation",
                            f"{source_name}/{replacement_name}/{count_name}/{method}",
                            action,
                        )

    patterns = (
        ("empty", r"", ""),
        ("empty-text", r"", "ab"),
        ("nullable-star", r"a*", "baac"),
        ("empty-alternative", r"|a", "aba"),
        ("lookahead", r"(?=.)", "abc"),
        ("optional-named", r"(?P<left>a)?(?P<right>b)", "bb ab b"),
        ("optional-alt", r"(a)|(b)", "abba"),
        ("nested-optionals", r"((a)?b)?", "abxb"),
    )
    templates = (
        ("plain", lambda text: "X" if text else b"X"),
        ("empty", lambda text: "" if text else b""),
        ("number-one", lambda text: r"<\1>" if text else rb"<\1>"),
        ("number-two", lambda text: r"<\2>" if text else rb"<\2>"),
        ("group-left", lambda text: r"<\g<left>>" if text else rb"<\g<left>>"),
        ("missing", lambda text: r"\g<missing>" if text else rb"\g<missing>"),
        ("bad-escape", lambda text: r"\x" if text else rb"\x"),
    )
    for is_text in (True, False):
        for pattern_name, raw_pattern, raw_subject in patterns:
            pattern = raw_pattern if is_text else raw_pattern.encode()
            for subclass in (False, True):

                def source_factory(
                    raw=raw_subject, text=is_text, use_subclass=subclass
                ):
                    if text:
                        return TextSubclass(raw) if use_subclass else raw
                    encoded = raw.encode()
                    return BytesSubclass(encoded) if use_subclass else encoded

                for template_name, template_factory in templates:
                    for count_name, count_factory in counts:
                        for method in ("sub", "subn"):

                            def action(
                                module, state, sf=source_factory, tf=template_factory,
                                cf=count_factory, p=pattern, text=is_text, name=method
                            ):
                                subject = sf()
                                return (
                                    getattr(module.compile(p), name)(
                                        tf(text), subject, cf(state)
                                    ),
                                    subject,
                                )

                            add(
                                "canonical-8264", "nullable-and-groups",
                                f"{pattern_name}/{is_text}/{subclass}/"
                                f"{template_name}/{count_name}/{method}",
                                action,
                            )

    for is_text in (True, False):
        pattern = r"(a)|(b)" if is_text else rb"(a)|(b)"
        subject = "abba" if is_text else b"abba"
        exceptions = (
            ("runtime", RuntimeError), ("value", ValueError),
            ("overflow", OverflowError), ("memory", MemoryError),
            ("recursion", RecursionError), ("interrupt", KeyboardInterrupt),
        )
        for exception_name, exception_type in exceptions:
            for fail_at in (1, 2, 3):
                for method in ("sub", "subn"):

                    def action(
                        module, state, p=pattern, source=subject,
                        error_type=exception_type, failure=fail_at, name=method
                    ):

                        def callback(match):
                            state.append(
                                ("callback", match.span(), normalise(match.groups()))
                            )
                            if len(state) == failure:
                                raise error_type("rust-native-callback-sentinel")
                            return "X" if isinstance(source, str) else b"X"

                        return (
                            getattr(module.compile(p), name)(callback, source),
                            source,
                        )

                    add(
                        "canonical-8264", "callback-exceptions",
                        f"{is_text}/{exception_name}/{fail_at}/{method}", action,
                    )

    for is_text in (True, False):
        pattern = "a" if is_text else b"a"
        subject = "aba" if is_text else b"aba"
        replacement = "X" if is_text else b"X"
        for method in ("sub", "subn"):
            calls = (
                ("positional", lambda f: f(replacement, subject)),
                ("keyword-both", lambda f: f(repl=replacement, string=subject)),
                ("keyword-count", lambda f: f(replacement, subject, count=1)),
                (
                    "all-keyword",
                    lambda f: f(repl=replacement, string=subject, count=1),
                ),
                ("missing-repl", lambda f: f(string=subject)),
                ("missing-string", lambda f: f(replacement)),
                ("unknown", lambda f: f(replacement, subject, other=1)),
                (
                    "duplicate-repl",
                    lambda f: f(replacement, subject, repl=replacement),
                ),
                (
                    "duplicate-string",
                    lambda f: f(replacement, subject, string=subject),
                ),
                (
                    "duplicate-count",
                    lambda f: f(replacement, subject, 1, count=1),
                ),
                ("too-many", lambda f: f(replacement, subject, 1, 2)),
                ("unknown-invalid", lambda f: f(3, subject, other=1)),
                ("signature", lambda f: str(inspect.signature(f))),
            )
            for call_name, caller in calls:

                def action(
                    module, state, p=pattern, source=subject, name=method,
                    invoke=caller
                ):
                    return invoke(getattr(module.compile(p), name)), source

                add(
                    "canonical-8264", "method-binding",
                    f"{is_text}/{method}/{call_name}", action,
                )

            def identity_action(
                module, state, p=pattern, source=subject, name=method
            ):
                compiled = module.compile(p)
                first = getattr(compiled, name)
                second = getattr(compiled, name)
                return (
                    (
                        first is second,
                        first.__self__ is compiled,
                        second.__self__ is compiled,
                        str(inspect.signature(first)),
                    ),
                    source,
                )

            add(
                "canonical-8264", "method-binding",
                f"identity/{is_text}/{method}", identity_action,
            )

    if sum(item[0] == "canonical-8264" for item in cases) != 8264:
        raise RuntimeError("canonical 8,264-case replacement cohort drifted")

    for storage_kind in ("bytearray", "memoryview", "array"):
        for count_name, count_factory in counts:
            for method in ("sub", "subn"):

                def action(
                    module, state, kind=storage_kind, cf=count_factory, name=method
                ):
                    storage = (
                        array.array("B", [48])
                        if kind == "array"
                        else bytearray(b"0")
                    )
                    replacement = memoryview(storage) if kind == "memoryview" else storage
                    subject = b"a-a-a-a"
                    calls_seen = 0

                    def callback(match):
                        nonlocal calls_seen
                        capture_match(state, match)
                        calls_seen += 1
                        storage[0] = 48 + calls_seen
                        state.append(("mutable-return", bytes(storage)))
                        return replacement

                    return (
                        getattr(module.compile(b"a"), name)(
                            callback, subject, cf(state)
                        ),
                        subject,
                    )

                add(
                    "extended", "shared-mutable-return",
                    f"{storage_kind}/{count_name}/{method}", action,
                )

    buffers = (
        ("bytes", lambda value: value),
        ("bytearray", lambda value: bytearray(value)),
        ("memoryview", lambda value: memoryview(value)),
        ("array", lambda value: array.array("B", value)),
    )
    contents = (
        ("plain", b"X"),
        ("unknown-name", rb"\g<missing>"),
        ("invalid-group", rb"\g<1>"),
        ("invalid-escape", rb"\q"),
    )
    for is_text in (True, False):
        pattern = "a" if is_text else b"a"
        for matching in (False, True):
            subject = (
                ("aza" if matching else "zzz")
                if is_text
                else (b"aza" if matching else b"zzz")
            )
            for buffer_name, make_buffer in buffers:
                for content_name, content in contents:
                    for count in (-1, 0, 1):
                        for method in ("sub", "subn"):

                            def action(
                                module, state, p=pattern, source=subject,
                                factory=make_buffer, data=content, limit=count,
                                name=method
                            ):
                                return (
                                    getattr(module.compile(p), name)(
                                        factory(data), source, limit
                                    ),
                                    source,
                                )

                            add(
                                "extended", "template-validation-timing",
                                f"{is_text}/match-{matching}/{buffer_name}/"
                                f"{content_name}/{count}/{method}",
                                action,
                            )

    for is_text in (True, False):
        pattern = "a" if is_text else b"a"
        subject = "za-a-a-a" if is_text else b"za-a-a-a"
        valid = "X" if is_text else b"X"
        wrong_value = b"X" if is_text else "X"
        for invalid_at in range(4):
            for late_raise in (False, True):
                for count in (-1, 0, 1, 2, 4):
                    for method in ("sub", "subn"):

                        def action(
                            module, state, p=pattern, source=subject, good=valid,
                            bad=wrong_value, bad_at=invalid_at, raise_late=late_raise,
                            limit=count, name=method
                        ):
                            callbacks = 0

                            def callback(match):
                                nonlocal callbacks
                                capture_match(state, match)
                                position = callbacks
                                callbacks += 1
                                if raise_late and position == bad_at + 1:
                                    raise ValueError("late callback")
                                return bad if position == bad_at else good

                            return (
                                getattr(module.compile(p), name)(
                                    callback, source, limit
                                ),
                                source,
                            )

                        add(
                            "extended", "deferred-join-order",
                            f"{is_text}/at-{invalid_at}/late-{late_raise}/"
                            f"{count}/{method}",
                            action,
                        )
    if deep:
        add_deep_cases(cases)
    return cases


def add_deep_cases(cases):
    def add(category, name, action):
        cases.append(("deep", category, name, action))

    windows = (
        ("default", lambda trace: (0, sys.maxsize)),
        ("inside", lambda trace: (1, 9)),
        ("negative", lambda trace: (-50, 50)),
        (
            "index",
            lambda trace: (IndexValue(0, trace), IndexValue(9, trace)),
        ),
    )
    literal_fixtures = (
        ("one-byte", "x", "x-x-x"),
        ("multi-byte", "xy", "xy-xy-xy"),
        ("whole-subject", "xy", "xy"),
        ("latin-one", "é", "é-é-é"),
        ("latin-multi", "éé", "éé-éé-éé"),
        ("wide-one", "🙂", "🙂-🙂-🙂"),
        ("wide-multi", "🙂🙂", "🙂🙂-🙂🙂-🙂🙂"),
        ("captured", "(xy)", "xy-xy-xy"),
        ("empty", "", "xy"),
    )
    for is_text in (True, False):
        for fixture_name, raw_pattern, raw_subject in literal_fixtures:
            if not is_text and not raw_pattern.isascii():
                continue
            pattern = raw_pattern if is_text else raw_pattern.encode()
            for subject_subclass in (False, True):
                subject = (
                    (TextSubclass(raw_subject) if subject_subclass else raw_subject)
                    if is_text
                    else (
                        BytesSubclass(raw_subject.encode())
                        if subject_subclass
                        else raw_subject.encode()
                    )
                )
                for window_name, make_window in windows:

                    def action(
                        module, trace, p=pattern, source=subject,
                        window=make_window
                    ):
                        start, end = window(trace)
                        compiled = module.compile(p)
                        values = compiled.findall(source, start, end)
                        details = (
                            tuple(
                                (
                                    normalise(value),
                                    value is source,
                                    value is p,
                                )
                                for value in values
                            ),
                            tuple(
                                (left, right, values[left] is values[right])
                                for left in range(len(values))
                                for right in range(left + 1, len(values))
                            ),
                            compiled.pattern is p,
                        )
                        return details, source

                    add(
                        "literal-result-identity",
                        f"{is_text}/{fixture_name}/subclass-{subject_subclass}/"
                        f"{window_name}",
                        action,
                    )

    def strided(data):
        interleaved = bytearray()
        for value in data:
            interleaved.extend((value, 95))
        return memoryview(interleaved)[::2]

    replacements = (
        ("unhashable-text-plain", lambda trace: UnhashableText("X")),
        (
            "unhashable-text-template",
            lambda trace: UnhashableText(r"\g<0>"),
        ),
        ("unhashable-bytes-plain", lambda trace: UnhashableBytes(b"X")),
        (
            "unhashable-bytes-template",
            lambda trace: UnhashableBytes(rb"\g<0>"),
        ),
        (
            "exploding-text-plain",
            lambda trace: ExplodingHashText("X", trace),
        ),
        (
            "exploding-text-template",
            lambda trace: ExplodingHashText(r"\g<0>", trace),
        ),
        (
            "exploding-bytes-plain",
            lambda trace: ExplodingHashBytes(b"X", trace),
        ),
        (
            "exploding-bytes-template",
            lambda trace: ExplodingHashBytes(rb"\g<0>", trace),
        ),
        (
            "counted-text-plain",
            lambda trace: CountingHashText("X", trace),
        ),
        (
            "counted-text-template",
            lambda trace: CountingHashText(r"\g<0>", trace),
        ),
        (
            "counted-bytes-plain",
            lambda trace: CountingHashBytes(b"X", trace),
        ),
        (
            "counted-bytes-template",
            lambda trace: CountingHashBytes(rb"\g<0>", trace),
        ),
        (
            "non-integer-text-plain",
            lambda trace: NonIntegerHashText("X", trace),
        ),
        (
            "non-integer-text-template",
            lambda trace: NonIntegerHashText(r"\g<0>", trace),
        ),
        (
            "non-integer-bytes-plain",
            lambda trace: NonIntegerHashBytes(b"X", trace),
        ),
        (
            "non-integer-bytes-template",
            lambda trace: NonIntegerHashBytes(rb"\g<0>", trace),
        ),
        ("bytearray-subclass", lambda trace: BytearraySubclass(b"X")),
        (
            "bytearray-subclass-template",
            lambda trace: BytearraySubclass(rb"\g<0>"),
        ),
        ("strided-memoryview", lambda trace: memoryview(b"XYZ")[::2]),
        (
            "strided-template",
            lambda trace: strided(rb"\g<0>"),
        ),
        (
            "strided-invalid-template",
            lambda trace: strided(rb"\g<missing>"),
        ),
        ("wide-array", lambda trace: array.array("H", [88, 89])),
        ("wide-int-array", lambda trace: array.array("I", [88, 89])),
        ("python-buffer", lambda trace: PythonBuffer(b"X", trace, "plain")),
        (
            "python-buffer-template",
            lambda trace: PythonBuffer(rb"\g<0>", trace, "template"),
        ),
        (
            "python-buffer-invalid-template",
            lambda trace: PythonBuffer(
                rb"\g<missing>", trace, "invalid-template"
            ),
        ),
    )
    deep_counts = (
        ("negative", lambda trace: -1),
        ("zero", lambda trace: 0),
        ("one", lambda trace: 1),
        ("index-zero", lambda trace: IndexValue(0, trace)),
    )
    for is_text in (True, False):
        pattern = "a" if is_text else b"a"
        for matching in (False, True):
            raw_subject = "aza" if matching else "zzz"
            subject = raw_subject if is_text else raw_subject.encode()
            for replacement_name, make_replacement in replacements:
                for count_name, make_count in deep_counts:
                    for method in ("sub", "subn"):
                        for module_level in (False, True):

                            def action(
                                module, trace, p=pattern, source=subject,
                                factory=make_replacement, count=make_count,
                                name=method, use_module=module_level
                            ):
                                replacement = factory(trace)
                                limit = count(trace)
                                if use_module:
                                    value = getattr(module, name)(
                                        p, replacement, source, count=limit
                                    )
                                else:
                                    value = getattr(module.compile(p), name)(
                                        replacement, source, limit
                                    )
                                return value, source

                            add(
                                "unhashable-and-buffer-replacements",
                                f"{is_text}/match-{matching}/"
                                f"{replacement_name}/{count_name}/{method}/"
                                f"module-{module_level}",
                                action,
                            )

    escaped = (
        ("unknown-name", rb"\g<missing>"),
        ("invalid-group", rb"\g<1>"),
        ("invalid-escape", rb"\q"),
    )
    buffer_types = (
        ("bytes", lambda data: data),
        ("bytes-subclass", lambda data: BytesSubclass(data)),
        ("unhashable-bytes", lambda data: UnhashableBytes(data)),
        ("bytearray", lambda data: bytearray(data)),
        ("bytearray-subclass", lambda data: BytearraySubclass(data)),
        ("memoryview", lambda data: memoryview(data)),
        ("strided", strided),
        ("array", lambda data: array.array("B", data)),
    )
    for is_text in (True, False):
        pattern = "a" if is_text else b"a"
        for matching in (False, True):
            raw_subject = "aza" if matching else "zzz"
            subject = raw_subject if is_text else raw_subject.encode()
            for escape_name, content in escaped:
                for buffer_name, make_buffer in buffer_types:
                    for count in (-1, 0):
                        for method in ("sub", "subn"):

                            def action(
                                module, trace, p=pattern, source=subject,
                                data=content, factory=make_buffer, limit=count,
                                name=method
                            ):
                                try:
                                    value = getattr(module.compile(p), name)(
                                        factory(data), source, limit
                                    )
                                except BaseException as error:
                                    value = (
                                        "captured-error",
                                        type(error).__name__,
                                        str(error),
                                        normalise(error.args),
                                        normalise(
                                            getattr(error, "pattern", None)
                                        ),
                                        getattr(error, "pos", None),
                                        getattr(error, "lineno", None),
                                        getattr(error, "colno", None),
                                    )
                                return value, source

                            add(
                                "template-error-metadata",
                                f"{is_text}/match-{matching}/{escape_name}/"
                                f"{buffer_name}/{count}/{method}",
                                action,
                            )

    for source_kind in ("bytearray", "bytearray-subclass", "memoryview", "array"):
        for mutation in (
            "current",
            "next-match",
            "unmatched-prefix",
            "same-length-slice",
            "resize",
        ):
            for count in (-1, 0, 1, 2):
                for method in ("sub", "subn"):

                    def action(
                        module, trace, kind=source_kind, operation=mutation,
                        limit=count, name=method
                    ):
                        if kind == "array":
                            owner = array.array("B", b"a-a-a-a")
                            subject = owner
                        elif kind == "bytearray-subclass":
                            owner = BytearraySubclass(b"a-a-a-a")
                            subject = owner
                        else:
                            owner = bytearray(b"a-a-a-a")
                            subject = (
                                memoryview(owner)
                                if kind == "memoryview"
                                else owner
                            )

                        def callback(match):
                            capture_match(trace, match)
                            start, end = match.span()
                            if operation == "current":
                                owner[start] = ord("b")
                            elif operation == "next-match":
                                owner[min(end + 1, len(owner) - 1)] = ord("b")
                            elif operation == "unmatched-prefix":
                                owner[1] = ord("+")
                            elif operation == "same-length-slice":
                                owner[1:2] = (
                                    array.array("B", b"+")
                                    if isinstance(owner, array.array)
                                    else b"+"
                                )
                            else:
                                owner.append(ord("z"))
                            trace.append(("subject-mutated", bytes(owner)))
                            return b"X"

                        return (
                            getattr(module.compile(b"a"), name)(
                                callback, subject, limit
                            ),
                            subject,
                        )

                    add(
                        "mutable-subject",
                        f"{source_kind}/{mutation}/{count}/{method}",
                        action,
                    )

    for is_text in (True, False):
        pattern = "a" if is_text else b"a"
        subject = "aza" if is_text else b"aza"
        replacement = "X" if is_text else b"X"
        for operation in (
            "nested-search",
            "nested-sub",
            "purge",
            "global-mutation",
            "none",
            "recursive-three",
        ):
            for count in (-1, 0, 1):
                for method in ("sub", "subn"):

                    def action(
                        module, trace, p=pattern, source=subject,
                        output=replacement, task=operation, limit=count,
                        name=method, text=is_text
                    ):
                        compiled = module.compile(p)
                        calls = 0

                        def callback(match):
                            nonlocal calls
                            capture_match(trace, match)
                            calls += 1
                            if task == "nested-search":
                                inner = compiled.search(source)
                                trace.append(
                                    ("nested-search", inner.span() if inner else None)
                                )
                            elif task == "nested-sub":
                                trace.append(
                                    (
                                        "nested-sub",
                                        normalise(
                                            compiled.sub(output, source, 1)
                                        ),
                                    )
                                )
                            elif task == "purge":
                                module.purge()
                                trace.append(("purge", calls))
                            elif task == "global-mutation":
                                trace.append(("global", calls))
                            elif task == "none":
                                return None
                            elif task == "recursive-three":
                                inner_subject = "a" if text else b"a"

                                def nested(inner_match):
                                    trace.append(
                                        (
                                            "nested-callback",
                                            inner_match.span(),
                                        )
                                    )
                                    return output

                                for _ in range(3):
                                    compiled.sub(nested, inner_subject)
                            return output

                        return (
                            getattr(compiled, name)(
                                callback, source, limit
                            ),
                            source,
                        )

                    add(
                        "reentrant-callbacks",
                        f"{is_text}/{operation}/{count}/{method}",
                        action,
                    )

    for is_text in (True, False):
        pattern = "a" if is_text else b"a"
        subject = "aza" if is_text else b"aza"
        replacement = "X" if is_text else b"X"
        for count in (-1, 0, 1):
            for method in ("sub", "subn"):

                def action(
                    module, trace, p=pattern, source=subject,
                    output=replacement, limit=count, name=method
                ):
                    references = []

                    def callback(match):
                        capture_match(trace, match)
                        cycle = MatchCycle(match)
                        references.append(weakref.ref(cycle))
                        return output

                    result = getattr(module.compile(p), name)(
                        callback, source, limit
                    )
                    gc.collect()
                    trace.append(
                        (
                            "match-cycles-collected",
                            tuple(reference() is None for reference in references),
                        )
                    )
                    return result, source

                add(
                    "callback-match-garbage-collection",
                    f"{is_text}/{count}/{method}",
                    action,
                )


def load_candidate(module_name, bridge_path):
    if bridge_path:
        package_name, _, _ = module_name.rpartition(".")
        if not package_name:
            raise ValueError("--bridge-path requires a package-qualified module")
        package = importlib.import_module(package_name)
        bridge_name = package_name + "._rust_bridge"
        spec = importlib.util.spec_from_file_location(bridge_name, bridge_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load native bridge {bridge_path!r}")
        bridge = importlib.util.module_from_spec(spec)
        sys.modules[bridge_name] = bridge
        spec.loader.exec_module(bridge)
        setattr(package, "_rust_bridge", bridge)
    return importlib.import_module(module_name)


def kind(expected, actual):
    if (
        expected.get("status") == actual.get("status") == "error"
        and expected.get("type") == actual.get("type")
        and expected.get("message") == actual.get("message")
        and expected.get("args") == actual.get("args")
        and expected.get("trace") != actual.get("trace")
    ):
        return "callback-side-effects"
    if (
        expected.get("status") == actual.get("status") == "error"
        and expected.get("type") == actual.get("type")
    ):
        return "exception-message-or-state"
    return "result-or-exception"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest() if path else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", default="candidates.rust_candidate")
    parser.add_argument("--bridge-path")
    parser.add_argument(
        "--engine-path",
        help="record the exact native Rust engine used by an isolated bridge",
    )
    parser.add_argument(
        "--deep",
        action="store_true",
        help="add frozen identity, buffer, mutation, recursion, and GC controls",
    )
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    candidate = load_candidate(args.module, args.bridge_path)
    cases = build_cases(deep=args.deep)
    checks = collections.Counter()
    failures = []
    self_failures = []
    for cohort, category, name, action in cases:
        checks[cohort, category] += 1
        expected = observed(re, action)
        repeated = observed(re, action)
        if expected != repeated:
            self_failures.append(
                {
                    "cohort": cohort,
                    "category": category,
                    "case": name,
                    "first": expected,
                    "second": repeated,
                }
            )
            continue
        actual = observed(candidate, action)
        if expected != actual:
            failures.append(
                {
                    "cohort": cohort,
                    "category": category,
                    "case": name,
                    "kind": kind(expected, actual),
                    "expected": expected,
                    "actual": actual,
                }
            )
    failure_counts = collections.Counter(
        (failure["cohort"], failure["category"]) for failure in failures
    )
    kind_counts = collections.Counter(
        (failure["cohort"], failure["category"], failure["kind"])
        for failure in failures
    )
    categories = [
        {
            "cohort": cohort,
            "category": category,
            "checks": total,
            "failed": failure_counts[cohort, category],
            "failure_kinds": {
                reason: number
                for (kind_cohort, kind_category, reason), number
                in sorted(kind_counts.items())
                if (kind_cohort, kind_category) == (cohort, category)
            },
        }
        for (cohort, category), total in sorted(checks.items())
    ]
    canonical_failed = sum(
        item["failed"] for item in categories if item["cohort"] == "canonical-8264"
    )
    report = {
        "schema": SCHEMA,
        "python_version": sys.version,
        "python_executable": sys.executable,
        "oracle": "stdlib re",
        "module": args.module,
        "module_sha256": sha256(getattr(candidate, "__file__", None)),
        "bridge_path": args.bridge_path,
        "bridge_sha256": sha256(args.bridge_path),
        "engine_path": args.engine_path,
        "engine_sha256": sha256(args.engine_path),
        "runner_sha256": sha256(Path(__file__)),
        "deep": args.deep,
        "self_oracle_passes": 2,
        "self_oracle_failures": self_failures,
        "checks": len(cases),
        "failed": len(failures),
        "canonical_checks": 8264,
        "canonical_failed": canonical_failed,
        "categories": categories,
        "failures": failures,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = (
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")
    if output.suffix == ".gz":
        output.write_bytes(gzip.compress(payload, compresslevel=9, mtime=0))
    else:
        output.write_bytes(payload)
    print(
        json.dumps(
            {
                "schema": SCHEMA,
                "checks": len(cases),
                "failed": len(failures),
                "self_oracle_failures": len(self_failures),
                "canonical_checks": 8264,
                "canonical_failed": canonical_failed,
                "categories": categories,
                "bridge_path": args.bridge_path,
                "deep": args.deep,
                "output": str(output),
            },
            sort_keys=True,
        )
    )
    if failures or self_failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
