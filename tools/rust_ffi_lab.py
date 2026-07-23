#!/usr/bin/env python3
"""Audit and measure the from-scratch Rust/Python boundary in isolation.

This laboratory intentionally does not read either performance holdout.  Its
locally generated cases are diagnostic, not an end-to-end ranking.  CPython's
unmodified public ``re`` implementation is the semantic and timing baseline.
The third measured implementation, ``rust-direct``, invokes this project's own
native Rust bridge and is an experimental boundary strategy, not another regex
engine or a change to the public implementation.
"""

from __future__ import annotations

import argparse
import array
import gc
import gzip
import hashlib
import importlib
import importlib.util
import inspect
import json
import math
import random
import statistics
import sys
import time
import tracemalloc
import warnings
import weakref
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


SCHEMA = "rebar-rust-ffi-lab-v1"
PYTHON_VERSION = (3, 14, 6)
ORDER_SEED = 1_985_072_311
BOOTSTRAP_SEED = 1_985_072_312
RUNTIME_REGRESSION_THRESHOLD = 1.2
SPEEDUP_REGRESSION_THRESHOLD = 1.0 / RUNTIME_REGRESSION_THRESHOLD
ENGINES = ("stdlib", "rust-public", "rust-direct")
ROOT = Path(__file__).resolve().parent.parent


class Text(str):
    """A real, mutable-attribute Unicode subclass for ownership checks."""


class Blob(bytes):
    """A bytes subclass for exact result and unchanged-object checks."""


class ExplodingHashText(Text):
    """A Unicode subclass whose hash produces a user-visible exception."""

    def __hash__(self) -> int:
        raise RuntimeError("intentional FFI text-subclass hash failure")


class ExplodingHashBlob(Blob):
    """A bytes subclass whose hash produces a user-visible exception."""

    def __hash__(self) -> int:
        raise RuntimeError("intentional FFI bytes-subclass hash failure")


class ExplodingHashBuffer(bytearray):
    """A buffer whose hash must not be consulted by replacement parsing."""

    def __hash__(self) -> int:
        raise RuntimeError("the replacement buffer must not be hashed")


class Index:
    """An ordinary object implementing Python's indexing protocol."""

    def __init__(self, value: int) -> None:
        self.value = value

    def __index__(self) -> int:
        return self.value


class ExplodingIndex:
    """Verify that user-defined index exceptions survive the boundary."""

    def __index__(self) -> int:
        raise RuntimeError("intentional FFI index failure")


class CallbackFailure(RuntimeError):
    """Recognizable callback failure for exact exception propagation."""


@dataclass(frozen=True, slots=True)
class TimingCase:
    identifier: str
    family: str
    operation: str
    pattern: str | bytes
    subject: str | bytes | bytearray
    replacement: str | bytes | None = None
    flags: int = 0
    count: int = 0
    pos: int = 0
    endpos: int = sys.maxsize


@dataclass(frozen=True, slots=True)
class SemanticCase:
    identifier: str
    family: str
    action: Callable[[Any], Any]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def require_pinned_python() -> None:
    require(sys.implementation.name == "cpython", "the oracle must use CPython")
    require(
        sys.version_info[:3] == PYTHON_VERSION,
        "the FFI laboratory requires pinned CPython 3.14.6",
    )


def canonical(
    value: Any,
    *,
    subject: Any = None,
    compiled: Any = None,
) -> Any:
    """Preserve observable types, captures, ownership, and Python values."""
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        return {"integer": int(value), "type": type(value).__name__}
    if isinstance(value, str):
        return {"text": str(value), "type": type(value).__name__}
    if isinstance(value, bytes):
        return {"hex": bytes(value).hex(), "type": type(value).__name__}
    if isinstance(value, bytearray):
        return {"hex": bytes(value).hex(), "type": type(value).__name__}
    if isinstance(value, memoryview):
        return {
            "hex": value.tobytes().hex(),
            "type": "memoryview",
            "contiguous": value.c_contiguous,
        }
    if isinstance(value, array.array):
        return {
            "hex": value.tobytes().hex(),
            "type": "array",
            "typecode": value.typecode,
        }
    if isinstance(value, tuple):
        return {
            "tuple": [
                canonical(item, subject=subject, compiled=compiled)
                for item in value
            ]
        }
    if isinstance(value, list):
        return [
            canonical(item, subject=subject, compiled=compiled)
            for item in value
        ]
    if isinstance(value, dict):
        return {
            str(key): canonical(item, subject=subject, compiled=compiled)
            for key, item in value.items()
        }
    if all(hasattr(value, name) for name in ("span", "groups", "groupdict", "re", "string")):
        return {
            "match": {
                "span": canonical(value.span()),
                "group": canonical(value.group()),
                "groups": canonical(value.groups()),
                "groupdict": canonical(value.groupdict()),
                "regs": canonical(value.regs),
                "lastindex": canonical(value.lastindex),
                "lastgroup": canonical(value.lastgroup),
                "pos": canonical(value.pos),
                "endpos": canonical(value.endpos),
                "subject_type": type(value.string).__name__,
                "subject_identity": value.string is subject,
                "pattern_identity": compiled is None or value.re is compiled,
            }
        }
    if hasattr(value, "pattern") and hasattr(value, "groupindex"):
        return {
            "pattern": canonical(value.pattern),
            "groups": canonical(value.groups),
            "groupindex": canonical(dict(value.groupindex)),
            "flags": canonical(int(value.flags)),
        }
    return {"type": type(value).__name__, "representation": repr(value)}


def observe(
    action: Callable[[], Any],
    *,
    subject: Any = None,
    compiled: Any = None,
) -> dict[str, Any]:
    """Record exact exception text, warnings, and normalized return values."""
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        try:
            result = {
                "value": canonical(action(), subject=subject, compiled=compiled)
            }
        except BaseException as error:
            if isinstance(error, (KeyboardInterrupt, SystemExit)):
                raise
            result = {
                "error": type(error).__name__,
                "message": str(error),
            }
            if all(hasattr(error, key) for key in ("msg", "pattern", "pos")):
                result["pattern_error"] = {
                    key: canonical(getattr(error, key, None))
                    for key in ("msg", "pattern", "pos", "lineno", "colno")
                }
        result["warnings"] = [
            {"category": item.category.__name__, "message": str(item.message)}
            for item in recorded
        ]
        return result


def scanner_snapshot(scanner: Any, *, mode: str = "search") -> list[Any]:
    output = []
    for _ in range(2048):
        match = getattr(scanner, mode)()
        if match is None:
            return output
        output.append(match)
    raise RuntimeError("scanner failed to terminate after 2,048 results")


def timing_cases() -> tuple[TimingCase, ...]:
    """Generate independent diagnostic cases without opening a holdout."""
    rows: list[TimingCase] = []

    def add(
        family: str,
        variant: int,
        operation: str,
        pattern: str | bytes,
        subject: str | bytes | bytearray,
        *,
        replacement: str | bytes | None = None,
        flags: int = 0,
        count: int = 0,
        pos: int = 0,
        endpos: int = sys.maxsize,
    ) -> None:
        rows.append(
            TimingCase(
                f"ffi.calibration.{family}.{variant:02d}",
                family,
                operation,
                pattern,
                subject,
                replacement,
                flags,
                count,
                pos,
                endpos,
            )
        )

    for index in range(8):
        number = 17 + index
        plain = f"item{index} alpha={number} beta={number + 3} omega"
        dense = " ".join(
            f"field{column}={number + column}"
            for column in range(4 + index)
        )
        raw = dense.encode("ascii")
        glyph = ("é", "Ā", "😀", "\ud800")[index % 4]
        wide = f"{glyph} {plain} {glyph} {dense}"
        add("module-search", index, "module-search", r"alpha=\d+", plain)
        add("cached-bound-search", index, "search", r"alpha=\d+", plain)
        add("fresh-bound-search", index, "fresh-search", r"alpha=\d+", plain)
        add("fresh-method-binding", index, "binding-only", r"alpha=\d+", plain)
        add("bound-search-miss", index, "search", r"absent_\d+", plain)
        add("bound-match", index, "match", r"item\d+", plain)
        add("bound-fullmatch", index, "fullmatch", r"item\d+.*omega", plain)
        add("literal-findall", index, "findall", "field", dense)
        add("captured-findall", index, "findall", r"(field\d+)=(\d+)", dense)
        add("dense-iterator", index, "finditer", r"(field\d+)=(\d+)", dense)
        add("dense-scanner", index, "scanner", r"(field\d+)=(\d+)", dense)
        add("zero-width-iterator", index, "finditer", r"(?=field)|(?=$)", dense)
        add("captured-split", index, "split", r"(\s+)", dense, count=2 + index % 3)
        add("literal-replacement", index, "sub", r"field\d+", dense, replacement="name")
        add(
            "captured-replacement",
            index,
            "sub",
            r"(field\d+)=(\d+)",
            dense,
            replacement=r"\2:\1",
        )
        add(
            "counted-replacement",
            index,
            "subn",
            r"(field\d+)=(\d+)",
            dense,
            replacement=r"\2:\1",
            count=1 + index % 3,
        )
        add("callback-replacement", index, "callback-sub", r"field\d+", dense)
        add("full-match-surface", index, "match-surface", r"(?P<name>alpha)=(?P<number>\d+)", plain)
        add("bytes-search", index, "search", rb"field\d+=\d+", raw)
        add("mutable-buffer-search", index, "search", rb"field\d+=\d+", bytearray(raw))
        add("wide-unicode-search", index, "search", r"alpha=\d+", wide)
        add("cold-compilation", index, "cold-compile", rf"ffi_probe_{index}_(\d+)", plain)
        add("module-replacement", index, "module-sub", r"field\d+", dense, replacement="name")
        add(
            "windowed-search",
            index,
            "search",
            r"field\d+",
            dense,
            pos=3 + index,
            endpos=max(3 + index, len(dense) - index),
        )

    identifiers = [case.identifier for case in rows]
    require(len(identifiers) == len(set(identifiers)), "duplicate FFI case identifiers")
    require(all("holdout" not in case.identifier for case in rows), "holdout leaked into the FFI laboratory")
    return tuple(rows)


def public_runner(module: Any, case: TimingCase) -> Callable[[], Any]:
    """Create a normal public Python ``re`` action."""
    pattern = module.compile(case.pattern, case.flags)
    subject = case.subject
    operation = case.operation
    window = (case.pos, case.endpos)
    if operation == "module-search":
        return lambda: module.search(case.pattern, subject, case.flags)
    if operation == "module-sub":
        return lambda: module.sub(case.pattern, case.replacement, subject, flags=case.flags)
    if operation == "cold-compile":
        def compile_cold() -> Any:
            module.purge()
            return module.compile(case.pattern, case.flags)

        return compile_cold
    if operation == "binding-only":
        return lambda: pattern.search.__self__ is pattern
    if operation == "fresh-search":
        return lambda: pattern.search(subject)
    if operation in ("search", "match", "fullmatch"):
        method = getattr(pattern, operation)
        if window == (0, sys.maxsize):
            return lambda: method(subject)
        return lambda: method(subject, *window)
    if operation == "findall":
        return lambda: pattern.findall(subject)
    if operation == "finditer":
        return lambda: list(pattern.finditer(subject))
    if operation == "scanner":
        return lambda: scanner_snapshot(pattern.scanner(subject))
    if operation == "split":
        return lambda: pattern.split(subject, case.count)
    if operation in ("sub", "subn"):
        method = getattr(pattern, operation)
        return lambda: method(case.replacement, subject, case.count)
    if operation == "callback-sub":
        def callback(match: Any) -> str:
            return match.group(0).upper()

        return lambda: pattern.sub(callback, subject)
    if operation == "match-surface":
        def match_surface() -> Any:
            found = pattern.search(subject)
            if found is None:
                return None
            return (
                found.group(),
                found.group(1, 2),
                found.groups(),
                found.groupdict(),
                found.span(),
                found.span("number"),
                found.regs,
                found.lastindex,
                found.lastgroup,
            )

        return match_surface
    raise ValueError(f"unknown FFI operation: {operation}")


def direct_runner(module: Any, case: TimingCase) -> Callable[[], Any]:
    """Exercise the project's own direct native bridge, never another engine."""
    bridge = importlib.import_module("candidates._rust_bridge")
    operation = case.operation
    if operation == "cold-compile":
        return public_runner(module, case)

    def prepare_pattern() -> Any:
        return module.compile(case.pattern, case.flags)

    pattern = prepare_pattern()
    subject = case.subject
    handle = pattern._handle
    groupindex = pattern._groupindex
    expression = pattern.pattern
    literal = pattern._literal
    groups = pattern.groups

    if operation in ("search", "match", "fullmatch", "fresh-search"):
        if operation == "match":
            function = bridge.bound_match
        elif operation == "fullmatch":
            function = bridge.bound_fullmatch
        else:
            function = bridge.bound_search
        if (case.pos, case.endpos) == (0, sys.maxsize):
            return lambda: function(
                pattern,
                handle,
                groupindex,
                expression,
                literal,
                subject,
            )
        return lambda: function(
            pattern,
            handle,
            groupindex,
            expression,
            literal,
            subject,
            case.pos,
            case.endpos,
        )
    if operation == "binding-only":
        return lambda: pattern.search.__self__ is pattern
    if operation == "module-search":
        function = bridge.bound_search

        def module_search() -> Any:
            compiled = prepare_pattern()
            return function(
                compiled,
                compiled._handle,
                compiled._groupindex,
                compiled.pattern,
                compiled._literal,
                subject,
            )

        return module_search
    if operation == "findall":
        function = bridge.bound_findall
        return lambda: function(handle, expression, groups, subject)
    if operation == "finditer":
        function = bridge.bound_finditer
        return lambda: list(
            function(
                pattern,
                handle,
                groupindex,
                expression,
                groups,
                subject,
            )
        )
    if operation == "scanner":
        function = bridge.bound_scanner
        return lambda: scanner_snapshot(
            function(
                pattern,
                handle,
                groupindex,
                expression,
                groups,
                subject,
            )
        )
    if operation == "split":
        function = bridge.bound_split
        return lambda: function(handle, expression, groups, subject, case.count)
    if operation in ("sub", "subn"):
        templates = pattern._templates
        if templates is None:
            templates = {}
            object.__setattr__(pattern, "_templates", templates)
        function = bridge.bound_subn if operation == "subn" else bridge.bound_sub
        return lambda: function(
            pattern,
            handle,
            groupindex,
            expression,
            literal,
            templates,
            groups,
            case.replacement,
            subject,
            case.count,
        )
    if operation == "module-sub":
        function = bridge.bound_sub

        def module_sub() -> Any:
            compiled = prepare_pattern()
            templates = compiled._templates
            if templates is None:
                templates = {}
                object.__setattr__(compiled, "_templates", templates)
            return function(
                compiled,
                compiled._handle,
                compiled._groupindex,
                compiled.pattern,
                compiled._literal,
                templates,
                compiled.groups,
                case.replacement,
                subject,
                case.count,
            )

        return module_sub
    if operation == "callback-sub":
        def callback(match: Any) -> str:
            return match.group(0).upper()

        templates = pattern._templates
        if templates is None:
            templates = {}
            object.__setattr__(pattern, "_templates", templates)
        function = bridge.bound_sub
        return lambda: function(
            pattern,
            handle,
            groupindex,
            expression,
            literal,
            templates,
            groups,
            callback,
            subject,
            case.count,
        )
    if operation == "match-surface":
        function = bridge.bound_search

        def match_surface() -> Any:
            found = function(
                pattern,
                handle,
                groupindex,
                expression,
                literal,
                subject,
            )
            if found is None:
                return None
            return (
                found.group(),
                found.group(1, 2),
                found.groups(),
                found.groupdict(),
                found.span(),
                found.span("number"),
                found.regs,
                found.lastindex,
                found.lastgroup,
            )

        return match_surface
    raise ValueError(f"unknown direct FFI operation: {operation}")


def binding_action(module: Any, method_name: str) -> Any:
    pattern = module.compile(r"(?P<word>[A-Za-z]+)(?:=(?P<number>\d+))?")
    first = getattr(pattern, method_name)
    second = getattr(pattern, method_name)
    return {
        "fresh_each_access": first is not second,
        "bound_to_pattern": first.__self__ is pattern,
        "name": first.__name__,
        "qualname": first.__qualname__,
        "signature": str(inspect.signature(first)),
        "callable": callable(first),
    }


def match_surface_action(module: Any, *, width: str, zero: bool) -> Any:
    prefix = {"ascii": "", "latin1": "é", "bmp": "Ā", "astral": "😀", "surrogate": "\ud800"}[width]
    subject = prefix + " alpha=17 omega"
    pattern = module.compile(r"alpha=\d+" if zero else r"(?P<word>alpha)=(?P<number>\d+)")
    found = pattern.search(subject)
    require(found is not None, "the diagnostic match unexpectedly failed")
    payload = canonical(found, subject=subject, compiled=pattern)
    payload["match"]["regs_are_cached"] = found.regs is found.regs
    payload["match"]["group_zero_by_index"] = canonical(found[0])
    payload["match"]["zero_groups"] = canonical(found.groups())
    if not zero:
        payload["match"]["named_word"] = canonical(found["word"])
        payload["match"]["missing_default"] = canonical(found.groups(default="missing"))
    return payload


def unchanged_identity_action(module: Any, *, source_type: str, operation: str) -> Any:
    if source_type == "text":
        subject: Any = "unchanged text"
        pattern_value: Any = "missing"
        replacement: Any = "replacement"
    elif source_type == "text-subclass":
        subject = Text("unchanged text")
        pattern_value = "missing"
        replacement = "replacement"
    elif source_type == "bytes":
        subject = b"unchanged bytes"
        pattern_value = b"missing"
        replacement = b"replacement"
    elif source_type == "bytes-subclass":
        subject = Blob(b"unchanged bytes")
        pattern_value = b"missing"
        replacement = b"replacement"
    elif source_type == "bytearray":
        subject = bytearray(b"unchanged bytes")
        pattern_value = b"missing"
        replacement = b"replacement"
    elif source_type == "memoryview":
        subject = memoryview(b"unchanged bytes")
        pattern_value = b"missing"
        replacement = b"replacement"
    else:
        raise ValueError(source_type)
    pattern = module.compile(pattern_value)
    result = getattr(pattern, operation)(replacement, subject)
    output = result[0] if operation == "subn" else result
    return {
        "result": canonical(result, subject=subject, compiled=pattern),
        "output_is_subject": output is subject,
        "output_type": type(output).__name__,
    }


def findall_identity_action(module: Any, *, source_type: str, width: int) -> Any:
    require(width in (1, 2, 5), "unsupported literal identity width")
    text = "TOKEN"[:width]
    if source_type == "text":
        pattern_value: Any = text
        subject: Any = f"{text} {text} {text}"
    elif source_type == "text-subclass":
        pattern_value = Text(text)
        subject = Text(f"{text} {text} {text}")
    elif source_type == "bytes":
        pattern_value = text.encode("ascii")
        subject = f"{text} {text} {text}".encode("ascii")
    elif source_type == "bytes-subclass":
        pattern_value = Blob(text.encode("ascii"))
        subject = Blob(f"{text} {text} {text}".encode("ascii"))
    else:
        raise ValueError(source_type)
    pattern = module.compile(pattern_value)
    values = pattern.findall(subject)
    require(len(values) == 3, "the literal identity probe expected three results")
    return {
        "values": canonical(values, subject=subject, compiled=pattern),
        "first_is_second": values[0] is values[1],
        "second_is_third": values[1] is values[2],
        "first_is_pattern": values[0] is pattern.pattern,
        "first_is_subject": values[0] is subject,
    }


def missing_capture_action(module: Any, *, byte_mode: bool, operation: str) -> Any:
    pattern_value: str | bytes = rb"(a)?b" if byte_mode else r"(a)?b"
    subject: str | bytes = b"b ab b" if byte_mode else "b ab b"
    pattern = module.compile(pattern_value)
    if operation == "findall":
        return pattern.findall(subject)
    if operation == "split":
        return pattern.split(subject)
    if operation == "finditer":
        return list(pattern.finditer(subject))
    raise ValueError(operation)


def replacement_buffer_action(
    module: Any,
    *,
    source_type: str,
    template: bytes,
    matched: bool,
    count: int,
) -> Any:
    if source_type == "bytearray":
        replacement: Any = bytearray(template)
    elif source_type == "memoryview":
        replacement = memoryview(bytearray(template))
    elif source_type == "array":
        replacement = array.array("B", template)
    elif source_type == "exploding-hash":
        replacement = ExplodingHashBuffer(template)
    else:
        raise ValueError(source_type)
    subject = b"a1 a2" if matched else b"zz zz"
    pattern = module.compile(rb"a(\d)")
    before = canonical(replacement)
    result = observe(
        lambda: pattern.subn(replacement, subject, count),
        subject=subject,
        compiled=pattern,
    )
    return {"outcome": result, "replacement_before": before, "replacement_after": canonical(replacement)}


def replacement_subclass_action(
    module: Any,
    *,
    byte_mode: bool,
    template: str,
    matched: bool,
    count: int,
) -> Any:
    if byte_mode:
        replacement: str | bytes = ExplodingHashBlob(template.encode("ascii"))
        pattern = module.compile(rb"(a)")
        subject: str | bytes = b"a a" if matched else b"z z"
    else:
        replacement = ExplodingHashText(template)
        pattern = module.compile(r"(a)")
        subject = "a a" if matched else "z z"
    return {
        "replacement": canonical(replacement),
        "outcome": observe(
            lambda: pattern.subn(replacement, subject, count),
            subject=subject,
            compiled=pattern,
        ),
    }


def pattern_subclass_hash_action(module: Any, *, byte_mode: bool, operation: str) -> Any:
    if byte_mode:
        expression: str | bytes = ExplodingHashBlob(b"a")
        subject: str | bytes = b"aba"
        replacement: str | bytes = b"x"
    else:
        expression = ExplodingHashText("a")
        subject = "aba"
        replacement = "x"

    if operation == "compile":
        return module.compile(expression)
    if operation == "finditer":
        return list(module.finditer(expression, subject))
    if operation == "sub":
        return module.sub(expression, replacement, subject)
    if operation == "subn":
        return module.subn(expression, replacement, subject)
    if operation == "split":
        return module.split(expression, subject)
    return getattr(module, operation)(expression, subject)


def module_surface_action(module: Any, *, operation: str, variant: str) -> Any:
    expression: Any = r"(a)"
    subject: Any = "a a"
    replacement: Any = "X"
    flags = 0
    if variant == "compiled" or variant == "bad-compiled-flags":
        expression = module.compile(expression)
    if variant in ("ignorecase", "bad-compiled-flags"):
        flags = int(module.IGNORECASE)
    if variant == "ignorecase":
        expression = r"(A)"
    if variant == "wrong-subject":
        subject = b"a a"
    function = getattr(module, operation)

    if variant == "deprecated-positional":
        if operation == "split":
            return function(expression, subject, 1, flags)
        if operation in ("sub", "subn"):
            return function(expression, replacement, subject, 1, flags)
        raise ValueError(f"unsupported deprecated-position operation {operation}")

    if variant == "duplicate-count":
        if operation == "split":
            return function(expression, subject, 1, maxsplit=2)
        if operation in ("sub", "subn"):
            return function(expression, replacement, subject, 1, count=2)
        raise ValueError(f"unsupported duplicate-count operation {operation}")

    keywords: dict[str, Any] = {}
    if flags:
        keywords["flags"] = flags
    if variant == "unexpected-keyword":
        keywords["unexpected"] = 1
    if operation == "split":
        if variant == "index-count":
            keywords["maxsplit"] = Index(1)
        return function(expression, subject, **keywords)
    if operation in ("sub", "subn"):
        if variant == "index-count":
            keywords["count"] = Index(1)
        return function(expression, replacement, subject, **keywords)
    value = function(expression, subject, **keywords)
    if operation == "finditer":
        return list(value)
    return value


def module_cache_action(module: Any, *, operation: str) -> Any:
    module.purge()
    expression = r"(a)"
    subject = "a a"
    replacement = "X"
    first = module.compile(expression)
    before = module.compile(expression) is first
    function = getattr(module, operation)
    if operation == "split":
        value = function(expression, subject)
    elif operation in ("sub", "subn"):
        value = function(expression, replacement, subject)
    elif operation == "finditer":
        value = list(function(expression, subject))
    else:
        value = function(expression, subject)
    retained = module.compile(expression) is first
    module.purge()
    cleared = module.compile(expression) is not first
    return {
        "cache_hit_before_call": before,
        "call": canonical(value, subject=subject, compiled=first),
        "cache_hit_after_call": retained,
        "purge_recompiled": cleared,
    }


def callback_action(module: Any, *, behavior: str, byte_mode: bool, count: int) -> Any:
    subject: str | bytes
    if byte_mode:
        subject = b"a b c d"
        pattern = module.compile(rb"[a-d]")
    else:
        subject = "a b c d"
        pattern = module.compile(r"[a-d]")
    events: list[Any] = []
    shared = bytearray(b"0")
    retained: list[Any] = []

    def callback(match: Any) -> Any:
        events.append(canonical(match, subject=subject, compiled=pattern))
        step = len(events)
        if behavior == "raise" and step == 2:
            raise CallbackFailure("intentional second replacement failure")
        if behavior == "none":
            return None
        if behavior == "wrong-type":
            return "wrong" if byte_mode else b"wrong"
        if behavior == "shared-buffer":
            shared[0] = ord("0") + step
            return shared
        if behavior == "shared-view":
            shared[0] = ord("0") + step
            return memoryview(shared)
        if behavior == "retained-match":
            retained.append(match)
        piece = match.group(0)
        return piece.upper()

    result = observe(
        lambda: pattern.subn(callback, subject, count),
        subject=subject,
        compiled=pattern,
    )
    return {
        "outcome": result,
        "events": events,
        "shared_final": canonical(shared),
        "retained": [
            canonical(item, subject=subject, compiled=pattern)
            for item in retained
        ],
    }


def gc_cycle_action(module: Any, owner: str) -> Any:
    source = Text("alpha beta alpha")
    pattern = module.compile("alpha")
    if owner == "match":
        value = pattern.search(source)
    elif owner == "iterator":
        value = pattern.finditer(source)
    elif owner == "scanner":
        value = pattern.scanner(source)
    else:
        raise ValueError(owner)
    source.owner = value
    reference = weakref.ref(source)
    del value
    del source
    gc.collect()
    return {"subject_cycle_collected": reference() is None}


def gc_owner_diagnostics(module: Any, *, owner: str) -> dict[str, Any]:
    """Expose tracked-state and traversal, not merely a weakref outcome."""
    source = Text("alpha beta alpha")
    pattern = module.compile("alpha")
    if owner == "match":
        value = pattern.search(source)
    elif owner == "iterator":
        value = pattern.finditer(source)
    elif owner == "scanner":
        value = pattern.scanner(source)
    else:
        raise ValueError(owner)

    details: dict[str, Any] = {
        "owner": owner,
        "owner_type": type(value).__name__,
        "owner_tracked": gc.is_tracked(value),
        "source_type": type(source).__name__,
        "source_tracked": gc.is_tracked(source),
        "owner_referent_types": sorted(
            type(item).__name__ for item in gc.get_referents(value)
        ),
        "source_refcount_before_cycle": sys.getrefcount(source) - 1,
    }
    source.owner = value
    details["source_refcount_in_cycle"] = sys.getrefcount(source) - 1
    details["owner_refcount_in_cycle"] = sys.getrefcount(value) - 1
    reference = weakref.ref(source)
    del value
    del source
    details["objects_collected"] = gc.collect()
    details["source_alive_after_collection"] = reference() is not None
    survivor = reference()
    if survivor is not None:
        details["surviving_owner_tracked"] = gc.is_tracked(survivor.owner)
        details["surviving_source_referrer_types"] = sorted(
            type(item).__name__ for item in gc.get_referrers(survivor)
        )
    return details


def mutable_subject_action(module: Any, *, owner: str) -> Any:
    source = bytearray(b"a1 b2 c3")
    pattern = module.compile(rb"([a-z])(\d)")
    if owner == "iterator":
        iterator = pattern.finditer(source)
        source[0] = ord("x")
        first = next(iterator)
        resize = observe(lambda: source.append(ord("!")))
        remaining = list(iterator)
    elif owner == "scanner":
        scanner = pattern.scanner(source)
        source[0] = ord("x")
        first = scanner.search()
        resize = observe(lambda: source.append(ord("!")))
        remaining = scanner_snapshot(scanner)
    else:
        raise ValueError(owner)
    return {
        "first": canonical(first, subject=source, compiled=pattern),
        "resize_while_borrowed": resize,
        "remaining": canonical(remaining, subject=source, compiled=pattern),
        "final_source": canonical(source),
    }


def post_match_mutation_action(module: Any, *, source_type: str, operation: str) -> Any:
    backing = bytearray(b"a1 b2")
    if source_type == "bytearray":
        subject: Any = backing
    elif source_type == "memoryview":
        subject = memoryview(backing)
    else:
        raise ValueError(source_type)
    pattern = module.compile(rb"([a-z])(\d)")
    if operation == "search":
        found = pattern.search(subject)
    elif operation == "iterator":
        iterator = pattern.finditer(subject)
        found = next(iterator)
        del iterator
    else:
        raise ValueError(operation)
    require(found is not None, "post-match buffer probe unexpectedly missed")
    before = canonical(found, subject=subject, compiled=pattern)
    backing[0] = ord("x")
    after_mutation = canonical(found, subject=subject, compiled=pattern)
    resized = observe(lambda: backing.append(ord("!")))
    after_resize = canonical(found, subject=subject, compiled=pattern)
    return {
        "before": before,
        "after_mutation": after_mutation,
        "resize_after_matching": resized,
        "after_resize": after_resize,
        "backing": canonical(backing),
    }


def buffer_boundary_action(module: Any, *, kind: str, operation: str) -> Any:
    if kind == "noncontiguous":
        subject: Any = memoryview(bytearray(b"ax1xbx2x"))[::2]
    elif kind == "multidimensional":
        subject = memoryview(bytearray(b"a1b2c3")).cast("B", shape=[3, 2])
    elif kind == "wide-elements":
        subject = memoryview(array.array("H", [0x3161, 0x3262]))
    elif kind == "readonly-view":
        subject = memoryview(b"a1 b2")
    elif kind == "mutable-view":
        subject = memoryview(bytearray(b"a1 b2"))
    else:
        raise ValueError(kind)
    pattern = module.compile(rb"([a-z])(\d)")

    def action() -> Any:
        if operation == "finditer":
            return list(pattern.finditer(subject))
        if operation == "scanner":
            return scanner_snapshot(pattern.scanner(subject))
        if operation == "split":
            return pattern.split(subject)
        if operation in ("sub", "subn"):
            return getattr(pattern, operation)(b"X", subject)
        return getattr(pattern, operation)(subject)

    return {
        "source": {
            "contiguous": subject.c_contiguous,
            "dimensions": subject.ndim,
            "format": subject.format,
            "itemsize": subject.itemsize,
            "readonly": subject.readonly,
        },
        "outcome": observe(action, subject=subject, compiled=pattern),
    }


def window_action(module: Any, *, method: str, kind: str) -> Any:
    pattern = module.compile(r"a")
    subject = "a a a"
    if kind == "index":
        pos: Any = Index(2)
        end: Any = Index(5)
    elif kind == "negative":
        pos, end = -99, 99
    elif kind == "reversed":
        pos, end = 5, 2
    elif kind == "exploding":
        pos, end = ExplodingIndex(), 5
    else:
        raise ValueError(kind)
    if method == "scanner":
        return scanner_snapshot(pattern.scanner(subject, pos, end))
    if method == "finditer":
        return list(pattern.finditer(subject, pos, end))
    return getattr(pattern, method)(subject, pos, end)


def semantic_cases() -> tuple[SemanticCase, ...]:
    cases: list[SemanticCase] = []

    def add(family: str, suffix: str, action: Callable[[Any], Any]) -> None:
        cases.append(SemanticCase(f"ffi.semantic.{family}.{suffix}", family, action))

    for method in (
        "search", "match", "fullmatch", "findall", "finditer", "scanner", "split", "sub", "subn"
    ):
        add("fresh-vectorcall-binding", method, lambda module, name=method: binding_action(module, name))

    for width in ("ascii", "latin1", "bmp", "astral", "surrogate"):
        for zero in (False, True):
            suffix = f"{width}.{'zero-groups' if zero else 'named-groups'}"
            add(
                "borrowed-unicode-match",
                suffix,
                lambda module, w=width, z=zero: match_surface_action(module, width=w, zero=z),
            )

    for source_type in (
        "text", "text-subclass", "bytes", "bytes-subclass", "bytearray", "memoryview"
    ):
        for operation in ("sub", "subn"):
            add(
                "unchanged-object-identity",
                f"{source_type}.{operation}",
                lambda module, s=source_type, op=operation:
                unchanged_identity_action(module, source_type=s, operation=op),
            )

    for source_type in ("text", "text-subclass", "bytes", "bytes-subclass"):
        for width in (1, 2, 5):
            add(
                "literal-result-identity",
                f"{source_type}.width-{width}",
                lambda module, s=source_type, w=width:
                findall_identity_action(module, source_type=s, width=w),
            )

    for byte_mode in (False, True):
        for operation in ("findall", "split", "finditer"):
            add(
                "missing-capture-boundary",
                f"{'bytes' if byte_mode else 'text'}.{operation}",
                lambda module, b=byte_mode, op=operation:
                missing_capture_action(module, byte_mode=b, operation=op),
            )

    for source_type in ("bytearray", "memoryview", "array", "exploding-hash"):
        for label, template in (
            ("literal", b"X"),
            ("escaped-valid", b"<\\g<1>>"),
            ("escaped-invalid", b"\\g<9>"),
        ):
            for matched in (False, True):
                for count in (-1, 0, 1):
                    suffix = f"{source_type}.{label}.{'hit' if matched else 'miss'}.{count}"
                    add(
                        "eager-buffer-template",
                        suffix,
                        lambda module, s=source_type, t=template, m=matched, c=count:
                        replacement_buffer_action(module, source_type=s, template=t, matched=m, count=c),
                    )

    for byte_mode in (False, True):
        for label, template in (
            ("literal", "X"),
            ("escaped-valid", r"<\g<1>>"),
            ("escaped-invalid", r"\g<9>"),
        ):
            for matched in (False, True):
                for count in (-1, 0, 1):
                    suffix = f"{'bytes' if byte_mode else 'text'}.{label}.{'hit' if matched else 'miss'}.{count}"
                    add(
                        "malicious-replacement-subclass",
                        suffix,
                        lambda module, b=byte_mode, t=template, m=matched, c=count:
                        replacement_subclass_action(module, byte_mode=b, template=t, matched=m, count=c),
                    )

    for byte_mode in (False, True):
        for operation in (
            "compile", "search", "match", "fullmatch", "findall", "finditer", "split", "sub", "subn"
        ):
            add(
                "malicious-pattern-subclass",
                f"{'bytes' if byte_mode else 'text'}.{operation}",
                lambda module, b=byte_mode, op=operation:
                pattern_subclass_hash_action(module, byte_mode=b, operation=op),
            )

    module_operations = (
        "search", "match", "fullmatch", "findall", "finditer", "split", "sub", "subn"
    )
    for operation in module_operations:
        for variant in (
            "default", "compiled", "ignorecase", "bad-compiled-flags", "wrong-subject", "unexpected-keyword"
        ):
            add(
                "module-vectorcall-surface",
                f"{operation}.{variant}",
                lambda module, op=operation, kind=variant:
                module_surface_action(module, operation=op, variant=kind),
            )
        add(
            "module-cache-lifecycle",
            operation,
            lambda module, op=operation: module_cache_action(module, operation=op),
        )

    for operation in ("split", "sub", "subn"):
        for variant in ("index-count", "duplicate-count", "deprecated-positional"):
            add(
                "module-vectorcall-errors-and-warnings",
                f"{operation}.{variant}",
                lambda module, op=operation, kind=variant:
                module_surface_action(module, operation=op, variant=kind),
            )

    for byte_mode in (False, True):
        for behavior in ("normal", "none", "wrong-type", "raise", "retained-match", "shared-buffer", "shared-view"):
            if behavior in ("shared-buffer", "shared-view") and not byte_mode:
                continue
            for count in (0, 1, 2):
                suffix = f"{'bytes' if byte_mode else 'text'}.{behavior}.{count}"
                add(
                    "deferred-callback-side-effects",
                    suffix,
                    lambda module, b=byte_mode, action=behavior, c=count:
                    callback_action(module, behavior=action, byte_mode=b, count=c),
                )

    for owner in ("match", "iterator", "scanner"):
        add("garbage-collected-ownership", owner, lambda module, o=owner: gc_cycle_action(module, o))

    for owner in ("iterator", "scanner"):
        add("borrowed-mutable-subject", owner, lambda module, o=owner: mutable_subject_action(module, owner=o))

    for source_type in ("bytearray", "memoryview"):
        for operation in ("search", "iterator"):
            add(
                "post-match-mutable-buffer",
                f"{source_type}.{operation}",
                lambda module, s=source_type, op=operation:
                post_match_mutation_action(module, source_type=s, operation=op),
            )

    for kind in (
        "noncontiguous", "multidimensional", "wide-elements", "readonly-view", "mutable-view"
    ):
        for operation in (
            "search", "match", "fullmatch", "findall", "finditer", "scanner", "split", "sub", "subn"
        ):
            add(
                "strided-and-wide-buffer",
                f"{kind}.{operation}",
                lambda module, source=kind, op=operation:
                buffer_boundary_action(module, kind=source, operation=op),
            )

    for method in ("search", "match", "fullmatch", "findall", "finditer", "scanner"):
        for kind in ("index", "negative", "reversed", "exploding"):
            add(
                "native-window-and-errors",
                f"{method}.{kind}",
                lambda module, name=method, item=kind: window_action(module, method=name, kind=item),
            )

    identifiers = [case.identifier for case in cases]
    require(len(identifiers) == len(set(identifiers)), "duplicate FFI semantic cases")
    return tuple(cases)


def sha256_json(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def native_fingerprints() -> dict[str, str]:
    bridge = importlib.import_module("candidates._rust_bridge")
    paths = {
        "native_bridge": Path(bridge.__file__),
        "rust_engine": ROOT / "candidates" / "_rust_engine.so",
    }
    fingerprints = {}
    for name, path in paths.items():
        with path.open("rb") as stream:
            fingerprints[name] = hashlib.file_digest(stream, "sha256").hexdigest()
    return fingerprints


def load_candidate(module_name: str, bridge_path: Path | None = None) -> Any:
    """Optionally inject an isolated extension without changing production."""
    if bridge_path is None:
        return importlib.import_module(module_name)
    path = bridge_path.resolve(strict=True)
    require(
        module_name not in sys.modules,
        "the candidate was imported before isolated bridge injection",
    )
    package = importlib.import_module("candidates")
    require(
        "candidates._rust_bridge" not in sys.modules,
        "the production bridge was imported before isolated bridge injection",
    )
    specification = importlib.util.spec_from_file_location(
        "candidates._rust_bridge",
        path,
    )
    require(
        specification is not None and specification.loader is not None,
        "unable to load the isolated native Rust bridge",
    )
    bridge = importlib.util.module_from_spec(specification)
    sys.modules["candidates._rust_bridge"] = bridge
    specification.loader.exec_module(bridge)
    setattr(package, "_rust_bridge", bridge)
    return importlib.import_module(module_name)


def build_runners(
    baseline: Any,
    candidate: Any,
    case: TimingCase,
) -> dict[str, Callable[[], Any]]:
    return {
        "stdlib": public_runner(baseline, case),
        "rust-public": public_runner(candidate, case),
        "rust-direct": direct_runner(candidate, case),
    }


def case_observation(action: Callable[[], Any], case: TimingCase) -> dict[str, Any]:
    return observe(action, subject=case.subject)


def verify(args: argparse.Namespace) -> dict[str, Any]:
    require_pinned_python()
    baseline = importlib.import_module("re")
    candidate = load_candidate(args.module, args.bridge_path)
    native_before = native_fingerprints()
    rows: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []

    for case in semantic_cases():
        expected = observe(lambda item=case: item.action(baseline))
        actual = observe(lambda item=case: item.action(candidate))
        row = {
            "case": case.identifier,
            "family": case.family,
            "expected": expected,
            "actual": actual,
            "equal": expected == actual,
        }
        rows.append(row)
        if not row["equal"]:
            mismatches.append(row)

    for case in timing_cases():
        runners = build_runners(baseline, candidate, case)
        expected = case_observation(runners["stdlib"], case)
        for name in ("rust-public", "rust-direct"):
            actual = case_observation(runners[name], case)
            row = {
                "case": case.identifier,
                "family": case.family,
                "engine": name,
                "expected": expected,
                "actual": actual,
                "equal": expected == actual,
            }
            rows.append(row)
            if not row["equal"]:
                mismatches.append(row)

    native_after = native_fingerprints()
    require(native_before == native_after, "Rust native code changed during the FFI verification")
    report = {
        "schema": SCHEMA,
        "kind": "semantic-verification",
        "python": list(sys.version_info[:3]),
        "module": args.module,
        "native_bridge_override": (
            str(args.bridge_path.resolve()) if args.bridge_path is not None else None
        ),
        "holdout_accessed": False,
        "native_fingerprints": native_after,
        "semantic_cases": len(semantic_cases()),
        "timing_cases": len(timing_cases()),
        "checks": len(rows),
        "mismatches": len(mismatches),
        "families": dict(sorted(defaultdict_counts(row["family"] for row in rows).items())),
        "rows": rows,
        "result_sha256": sha256_json(rows),
    }
    write_report(Path(args.output), report)
    if mismatches:
        examples = ", ".join(row["case"] for row in mismatches[:8])
        raise SystemExit(f"FFI boundary mismatch: {len(mismatches)}/{len(rows)}; {examples}")
    return report


def oracle_self(args: argparse.Namespace) -> dict[str, Any]:
    """Prove the isolated CPython boundary oracle agrees with itself."""
    require_pinned_python()
    baseline = importlib.import_module("re")
    rows: list[dict[str, Any]] = []

    for case in semantic_cases():
        expected = observe(lambda item=case: item.action(baseline))
        actual = observe(lambda item=case: item.action(baseline))
        rows.append(
            {
                "case": case.identifier,
                "family": case.family,
                "expected": expected,
                "actual": actual,
                "equal": expected == actual,
            }
        )

    for case in timing_cases():
        first = public_runner(baseline, case)
        second = public_runner(baseline, case)
        expected = case_observation(first, case)
        actual = case_observation(second, case)
        rows.append(
            {
                "case": case.identifier,
                "family": case.family,
                "expected": expected,
                "actual": actual,
                "equal": expected == actual,
            }
        )

    failures = [row for row in rows if not row["equal"]]
    report = {
        "schema": SCHEMA,
        "kind": "stdlib-vs-stdlib-boundary-oracle",
        "python": list(sys.version_info[:3]),
        "holdout_accessed": False,
        "semantic_cases": len(semantic_cases()),
        "timing_cases": len(timing_cases()),
        "checks": len(rows),
        "mismatches": len(failures),
        "rows": rows,
        "result_sha256": sha256_json(rows),
    }
    write_report(Path(args.output), report)
    if failures:
        examples = ", ".join(row["case"] for row in failures[:8])
        raise SystemExit(f"self-oracle mismatch: {len(failures)}/{len(rows)}; {examples}")
    return report


def defaultdict_counts(values: Any) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for value in values:
        counts[value] += 1
    return dict(counts)


def percentile(sorted_values: list[float], fraction: float) -> float:
    require(bool(sorted_values), "cannot take a percentile of an empty sample")
    index = fraction * (len(sorted_values) - 1)
    lower = math.floor(index)
    upper = math.ceil(index)
    weight = index - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def is_material_regression(speedup: float) -> bool:
    """Report candidate runtime exceeding 120% of baseline runtime."""
    require(math.isfinite(speedup) and speedup > 0, "non-positive FFI speedup")
    return speedup < SPEEDUP_REGRESSION_THRESHOLD


def bootstrap_interval(logs: list[float], *, seed: int, samples: int) -> tuple[float, float]:
    require(bool(logs), "no paired observations available")
    require(samples > 0, "bootstrap samples must be positive")
    generator = random.Random(seed)
    count = len(logs)
    values = sorted(
        math.exp(sum(logs[generator.randrange(count)] for _ in range(count)) / count)
        for _ in range(samples)
    )
    return percentile(values, 0.025), percentile(values, 0.975)


def paired_rows(
    raw: list[dict[str, Any]],
    cases: tuple[TimingCase, ...],
    trials: int,
) -> dict[str, dict[str, list[float]]]:
    grouped: dict[str, dict[str, list[float]]] = {
        case.identifier: {name: [] for name in ENGINES}
        for case in cases
    }
    seen: set[tuple[str, str, int]] = set()
    for row in raw:
        key = (row["case"], row["engine"], row["trial"])
        require(key not in seen, f"duplicate paired timing: {key!r}")
        seen.add(key)
        require(row["case"] in grouped, f"unknown timing case: {row['case']}")
        require(row["engine"] in ENGINES, f"unknown engine: {row['engine']}")
        require(0 <= row["trial"] < trials, "timing trial is outside the frozen denominator")
        require(row["operations"] > 0, "timing operation count must be positive")
        require(row["elapsed_ns"] > 0, "timing elapsed duration must be positive")
        require(row["correctness_before"] and row["correctness_after"], "ungated timing observation")
        grouped[row["case"]][row["engine"]].append(row["elapsed_ns"] / row["operations"])
    expected = len(cases) * len(ENGINES) * trials
    require(len(seen) == expected, f"incomplete paired timing: {len(seen)}/{expected}")
    for identifier, engines in grouped.items():
        for name in ENGINES:
            require(len(engines[name]) == trials, f"missing {name} trial for {identifier}")
    return grouped


def measure(args: argparse.Namespace) -> dict[str, Any]:
    require_pinned_python()
    require(args.trials > 0, "trials must be positive")
    require(args.max_ops > 0, "max-ops must be positive")
    require(args.bootstraps > 0, "bootstraps must be positive")
    require(args.warmups >= 0, "warmups cannot be negative")
    baseline = importlib.import_module("re")
    candidate = importlib.import_module(args.module)
    cases = timing_cases()
    frozen = native_fingerprints()
    raw: list[dict[str, Any]] = []
    memory: list[dict[str, Any]] = []

    for index, case in enumerate(cases):
        runners = build_runners(baseline, candidate, case)
        expected = case_observation(runners["stdlib"], case)
        expected_hash = sha256_json(expected)
        for name in ENGINES:
            result = case_observation(runners[name], case)
            require(result == expected, f"{case.identifier}: {name} disagrees with CPython before warmup")
            for _ in range(args.warmups):
                runners[name]()

        for trial in range(args.trials):
            names = list(ENGINES)
            random.Random(ORDER_SEED + index * 65_537 + trial).shuffle(names)
            for order, name in enumerate(names):
                action = runners[name]
                before = case_observation(action, case)
                require(before == expected, f"{case.identifier}: {name} failed before timed trial {trial}")
                start = time.perf_counter_ns()
                for _ in range(args.max_ops):
                    action()
                elapsed = time.perf_counter_ns() - start
                after = case_observation(action, case)
                require(after == expected, f"{case.identifier}: {name} failed after timed trial {trial}")
                raw.append(
                    {
                        "case": case.identifier,
                        "family": case.family,
                        "engine": name,
                        "trial": trial,
                        "order": order,
                        "operations": args.max_ops,
                        "elapsed_ns": elapsed,
                        "expected_sha256": expected_hash,
                        "correctness_before": True,
                        "correctness_after": True,
                    }
                )

        for name in ENGINES:
            tracemalloc.start(1)
            try:
                before_current, _ = tracemalloc.get_traced_memory()
                result = runners[name]()
                current, peak = tracemalloc.get_traced_memory()
                require(
                    canonical(result, subject=case.subject)
                    == expected.get("value"),
                    f"{case.identifier}: {name} failed its memory correctness gate",
                )
                memory.append(
                    {
                        "case": case.identifier,
                        "family": case.family,
                        "engine": name,
                        "traced_peak_bytes": max(0, peak - before_current),
                        "traced_retained_bytes": max(0, current - before_current),
                        "includes_native_allocator": False,
                    }
                )
            finally:
                tracemalloc.stop()

    require(frozen == native_fingerprints(), "Rust native code changed during paired FFI timing")
    grouped = paired_rows(raw, cases, args.trials)
    results: dict[str, Any] = {}
    for engine_index, name in enumerate(("rust-public", "rust-direct")):
        family_logs: dict[str, list[float]] = defaultdict(list)
        case_rows: list[dict[str, Any]] = []
        logs: list[float] = []
        faster = 0
        losses = 0
        for index, case in enumerate(cases):
            observations = grouped[case.identifier]
            per_trial = [
                math.log(observations["stdlib"][trial] / observations[name][trial])
                for trial in range(args.trials)
            ]
            speed = math.exp(statistics.fmean(per_trial))
            low, high = bootstrap_interval(
                per_trial,
                seed=BOOTSTRAP_SEED + engine_index * 1_000_003 + index,
                samples=args.bootstraps,
            )
            log_speed = math.log(speed)
            logs.append(log_speed)
            family_logs[case.family].append(log_speed)
            statistically_faster = low > 1.0
            regressed = is_material_regression(speed)
            faster += statistically_faster
            losses += regressed
            case_rows.append(
                {
                    "case": case.identifier,
                    "family": case.family,
                    "speedup": speed,
                    "confidence_low": low,
                    "confidence_high": high,
                    "statistically_faster": statistically_faster,
                    "regression_over_20_percent": regressed,
                    "stdlib_median_ns": statistics.median(observations["stdlib"]),
                    "candidate_median_ns": statistics.median(observations[name]),
                }
            )
        low, high = bootstrap_interval(
            logs,
            seed=BOOTSTRAP_SEED + engine_index * 1_000_003,
            samples=args.bootstraps,
        )
        results[name] = {
            "cases": len(cases),
            "geometric_speedup": math.exp(statistics.fmean(logs)),
            "confidence_low": low,
            "confidence_high": high,
            "statistically_faster_cases": faster,
            "regressions_over_20_percent": losses,
            "families": {
                family: {
                    "cases": len(values),
                    "geometric_speedup": math.exp(statistics.fmean(values)),
                }
                for family, values in sorted(family_logs.items())
            },
            "all_cases": case_rows,
        }

    report = {
        "schema": SCHEMA,
        "kind": "paired-calibration-only",
        "python": list(sys.version_info[:3]),
        "module": args.module,
        "holdout_accessed": False,
        "end_to_end_ranking": "NOT MEASURED",
        "cases": len(cases),
        "families": len({case.family for case in cases}),
        "trials": args.trials,
        "warmups": args.warmups,
        "operations_per_trial": args.max_ops,
        "bootstrap_samples": args.bootstraps,
        "order_seed": ORDER_SEED,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "runtime_regression_threshold": RUNTIME_REGRESSION_THRESHOLD,
        "speedup_regression_threshold": SPEEDUP_REGRESSION_THRESHOLD,
        "expected_raw_rows": len(cases) * len(ENGINES) * args.trials,
        "observed_raw_rows": len(raw),
        "correctness_gates": len(cases) * (len(ENGINES) + 2 * len(ENGINES) * args.trials + len(ENGINES)),
        "native_fingerprints": frozen,
        "engines": results,
        "memory": memory,
        "raw_sha256": sha256_json(raw),
    }
    raw_path = Path(args.raw)
    write_raw(raw_path, raw)
    with raw_path.open("rb") as stream:
        report["raw_file_sha256"] = hashlib.file_digest(stream, "sha256").hexdigest()
    write_report(Path(args.output), report)
    return report


def write_raw(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".gz":
        with path.open("wb") as output:
            with gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as compressed:
                for row in rows:
                    compressed.write(
                        (json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii")
                    )
        return
    with path.open("w", encoding="ascii", newline="\n") as output:
        for row in rows:
            output.write(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n")


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("ascii")
    if path.suffix == ".gz":
        with path.open("wb") as output:
            with gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as compressed:
                compressed.write(payload)
    else:
        path.write_bytes(payload)


def read_json_report(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if path.suffix == ".gz":
        data = gzip.decompress(data)
    value = json.loads(data)
    require(isinstance(value, dict), f"{path}: expected a JSON object")
    require(value.get("schema") == SCHEMA, f"{path}: changed FFI schema")
    return value


def read_raw(path: Path) -> list[dict[str, Any]]:
    data = path.read_bytes()
    if path.suffix == ".gz":
        data = gzip.decompress(data)
    rows = [json.loads(line) for line in data.decode("ascii").splitlines() if line]
    require(all(isinstance(row, dict) for row in rows), "invalid raw FFI observation")
    return rows


def bundle(args: argparse.Namespace) -> dict[str, Any]:
    """Preserve self-oracle, all semantic checks, and every raw timing."""
    require_pinned_python()
    control = read_json_report(Path(args.self_test))
    self_oracle = read_json_report(Path(args.self_oracle))
    semantic = read_json_report(Path(args.verify))
    timing = read_json_report(Path(args.summary))
    raw_path = Path(args.raw)
    raw = read_raw(raw_path)

    require(control.get("kind") == "self-test", "missing FFI integrity self-test")
    require(control.get("result") == "PASS", "FFI integrity self-test failed")
    require(self_oracle.get("kind") == "stdlib-vs-stdlib-boundary-oracle", "missing CPython self oracle")
    require(self_oracle.get("mismatches") == 0, "CPython FFI self-oracle did not pass")
    require(semantic.get("kind") == "semantic-verification", "missing Rust FFI semantic verification")
    require(semantic.get("mismatches") == 0, "Rust FFI semantic verification did not pass")
    require(timing.get("kind") == "paired-calibration-only", "missing paired FFI diagnostic")
    require(timing.get("raw_sha256") == sha256_json(raw), "FFI raw timing evidence changed")
    with raw_path.open("rb") as stream:
        raw_file_sha256 = hashlib.file_digest(stream, "sha256").hexdigest()
    require(
        timing.get("raw_file_sha256") == raw_file_sha256,
        "the exact FFI raw-observation artifact changed",
    )
    require(timing.get("observed_raw_rows") == len(raw), "FFI raw timing denominator changed")
    require(timing.get("cases") == len(timing_cases()), "FFI timing fixture changed")
    require(
        semantic.get("native_fingerprints") == timing.get("native_fingerprints"),
        "different Rust binaries were used for FFI semantics and timing",
    )
    for component in (control, self_oracle, semantic, timing):
        require(component.get("holdout_accessed") is False, "holdout leaked into FFI diagnostic")

    paired_rows(raw, timing_cases(), timing["trials"])
    report = {
        "schema": SCHEMA,
        "kind": "complete-falsifiable-ffi-laboratory",
        "python": list(sys.version_info[:3]),
        "holdout_accessed": False,
        "end_to_end_ranking": "NOT MEASURED",
        "self_test": control,
        "stdlib_self_oracle": self_oracle,
        "rust_semantic_verification": semantic,
        "paired_calibration": timing,
        "paired_raw_observations": raw,
    }
    write_report(Path(args.output), report)
    return report


def capture(args: argparse.Namespace) -> dict[str, Any]:
    """Preserve failed correctness evidence without running any timing."""
    require_pinned_python()
    control = read_json_report(Path(args.self_test))
    self_oracle = read_json_report(Path(args.self_oracle))
    semantic = read_json_report(Path(args.verify))

    require(control.get("kind") == "self-test", "missing FFI integrity self-test")
    require(control.get("result") == "PASS", "FFI integrity self-test failed")
    require(self_oracle.get("kind") == "stdlib-vs-stdlib-boundary-oracle", "missing CPython self oracle")
    require(self_oracle.get("mismatches") == 0, "CPython FFI self-oracle did not pass")
    require(semantic.get("kind") == "semantic-verification", "missing Rust FFI semantic verification")
    require(control.get("timing_cases") == len(timing_cases()), "FFI timing denominator changed")
    require(control.get("semantic_cases") == len(semantic_cases()), "FFI semantic denominator changed")
    require(self_oracle.get("checks") == len(semantic_cases()) + len(timing_cases()), "self-oracle denominator changed")
    require(
        semantic.get("checks") == len(semantic_cases()) + 2 * len(timing_cases()),
        "candidate FFI denominator changed",
    )
    require(
        semantic.get("mismatches")
        == sum(not row["equal"] for row in semantic["rows"]),
        "candidate FFI mismatches were omitted",
    )
    frozen = native_fingerprints()
    require(
        semantic.get("native_fingerprints") == frozen,
        "the Rust binary changed after FFI verification",
    )
    for component in (control, self_oracle, semantic):
        require(component.get("holdout_accessed") is False, "holdout leaked into FFI evidence")

    standard = importlib.import_module("re")
    candidate = importlib.import_module(args.module)
    diagnostics = [
        {
            "engine": name,
            **gc_owner_diagnostics(module, owner=owner),
        }
        for name, module in (("stdlib", standard), ("rust", candidate))
        for owner in ("match", "iterator", "scanner")
    ]
    require(frozen == native_fingerprints(), "Rust native binary changed during GC diagnosis")
    report = {
        "schema": SCHEMA,
        "kind": "correctness-only-ffi-laboratory",
        "python": list(sys.version_info[:3]),
        "module": args.module,
        "holdout_accessed": False,
        "timing": "NOT MEASURED",
        "end_to_end_ranking": "NOT MEASURED",
        "waivers": [],
        "self_oracle_checks": self_oracle["checks"],
        "self_oracle_mismatches": self_oracle["mismatches"],
        "candidate_checks": semantic["checks"],
        "candidate_mismatches": semantic["mismatches"],
        "native_fingerprints": frozen,
        "self_test": control,
        "stdlib_self_oracle": self_oracle,
        "rust_semantic_verification": semantic,
        "gc_traversal_diagnostics": diagnostics,
    }
    write_report(Path(args.output), report)
    return report


def amend_capture(args: argparse.Namespace) -> dict[str, Any]:
    """Append a verified correction without hiding the historical failure."""
    require_pinned_python()
    report = read_json_report(Path(args.evidence))
    corrected = read_json_report(Path(args.verification))
    require(
        report.get("kind") == "correctness-only-ffi-laboratory",
        "the historical FFI evidence is missing",
    )
    require(
        corrected.get("kind") == "semantic-verification",
        "the corrected FFI verification is missing",
    )
    require(corrected.get("mismatches") == 0, "corrected FFI still has mismatches")
    require(
        corrected.get("checks") == report.get("candidate_checks"),
        "corrected FFI changed the historical denominator",
    )
    require(
        corrected.get("semantic_cases") == len(semantic_cases()),
        "corrected FFI changed the semantic cases",
    )
    require(
        corrected.get("timing_cases") == len(timing_cases()),
        "corrected FFI changed the calibration controls",
    )
    require(corrected.get("holdout_accessed") is False, "corrected FFI accessed holdout")
    original_engine = report["native_fingerprints"]["rust_engine"]
    same_engine = corrected["native_fingerprints"]["rust_engine"] == original_engine

    if args.label == "isolated":
        require(
            same_engine,
            "the isolated correction did not use the same Rust execution engine",
        )
        require(
            corrected.get("native_bridge_override") is not None,
            "the isolated correction must fingerprint its private bridge",
        )
        report["isolated_corrected_verification"] = corrected
        report["isolated_corrected_mismatches"] = corrected["mismatches"]
    else:
        require(
            corrected.get("native_bridge_override") is None,
            "the production correction must use the real public bridge",
        )
        require(
            corrected["native_fingerprints"] == native_fingerprints(),
            "the corrected production bridge changed after verification",
        )
        report["production_corrected_verification"] = corrected
        report["production_corrected_mismatches"] = corrected["mismatches"]
        report["production_engine_changed_since_original"] = not same_engine
        report["final_result"] = "PASS"
        standard = importlib.import_module("re")
        candidate = importlib.import_module(args.module)
        report["production_gc_traversal_diagnostics"] = [
            {"engine": name, **gc_owner_diagnostics(module, owner=owner)}
            for name, module in (("stdlib", standard), ("rust", candidate))
            for owner in ("match", "iterator", "scanner")
        ]
    write_report(Path(args.output), report)
    return report


def self_test(args: argparse.Namespace) -> dict[str, Any]:
    require_pinned_python()
    cases = timing_cases()
    semantic = semantic_cases()
    require(len(cases) == 192, "the FFI calibration denominator changed")
    require(len({case.family for case in cases}) == 24, "the FFI family denominator changed")
    require(len(semantic) == 354, "the FFI semantic denominator changed")
    require(cases == timing_cases(), "FFI calibration generation is nondeterministic")
    require(
        [case.identifier for case in semantic]
        == [case.identifier for case in semantic_cases()],
        "FFI semantic case generation is nondeterministic",
    )
    require(bootstrap_interval([0.0] * 5, seed=BOOTSTRAP_SEED, samples=31) == (1.0, 1.0), "self comparison must be exactly 1x")
    require(percentile([1.0, 3.0], 0.5) == 2.0, "percentile interpolation is incorrect")
    require(is_material_regression(0.82), "0.82x must be counted as over 20% slower")
    require(is_material_regression(0.833333), "0.833333x must be counted as over 20% slower")
    require(not is_material_regression(5.0 / 6.0), "exactly 20% slower is not over 20% slower")
    require(not is_material_regression(0.834), "0.834x must not be counted as over 20% slower")

    synthetic = [
        {
            "case": cases[0].identifier,
            "family": cases[0].family,
            "engine": engine,
            "trial": trial,
            "operations": 4,
            "elapsed_ns": 40,
            "correctness_before": True,
            "correctness_after": True,
        }
        for trial in range(2)
        for engine in ENGINES
    ]
    paired_rows(synthetic, (cases[0],), 2)
    rejected = 0
    for corrupted in (
        synthetic[:-1],
        synthetic + [dict(synthetic[0])],
        [{**row, "correctness_after": False} if i == 0 else dict(row) for i, row in enumerate(synthetic)],
        [{**row, "operations": 0} if i == 0 else dict(row) for i, row in enumerate(synthetic)],
        [{**row, "elapsed_ns": 0} if i == 0 else dict(row) for i, row in enumerate(synthetic)],
    ):
        try:
            paired_rows(corrupted, (cases[0],), 2)
        except ValueError:
            rejected += 1
    require(rejected == 5, "paired-row integrity controls failed")
    report = {
        "schema": SCHEMA,
        "kind": "self-test",
        "python": list(sys.version_info[:3]),
        "holdout_accessed": False,
        "timing_cases": len(cases),
        "timing_families": len({case.family for case in cases}),
        "semantic_cases": len(semantic),
        "runtime_regression_threshold": RUNTIME_REGRESSION_THRESHOLD,
        "speedup_regression_threshold": SPEEDUP_REGRESSION_THRESHOLD,
        "rejected_corrupt_observations": rejected,
        "result": "PASS",
    }
    write_report(Path(args.output), report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    check = commands.add_parser("self-test", help="validate case generation and paired-data rejection")
    check.add_argument("--output", required=True)

    self_oracle = commands.add_parser("oracle-self", help="verify every boundary case against unmodified CPython twice")
    self_oracle.add_argument("--output", required=True)

    correctness = commands.add_parser("verify", help="compare every boundary and side effect against CPython")
    correctness.add_argument("--module", default="candidates.rust_candidate")
    correctness.add_argument("--bridge-path", type=Path)
    correctness.add_argument("--output", required=True)

    timing = commands.add_parser("measure", help="run an independent, correctness-gated boundary pilot")
    timing.add_argument("--module", default="candidates.rust_candidate")
    timing.add_argument("--trials", type=int, default=7)
    timing.add_argument("--warmups", type=int, default=3)
    timing.add_argument("--max-ops", type=int, default=16)
    timing.add_argument("--bootstraps", type=int, default=401)
    timing.add_argument("--raw", required=True)
    timing.add_argument("--output", required=True)

    archive = commands.add_parser("bundle", help="preserve self-oracles, exact traces, and every paired raw observation")
    archive.add_argument("--self-test", required=True)
    archive.add_argument("--self-oracle", required=True)
    archive.add_argument("--verify", required=True)
    archive.add_argument("--summary", required=True)
    archive.add_argument("--raw", required=True)
    archive.add_argument("--output", required=True)

    correctness_archive = commands.add_parser("capture", help="preserve correctness failures, self-oracle, and lifetime diagnostics without timing")
    correctness_archive.add_argument("--module", default="candidates.rust_candidate")
    correctness_archive.add_argument("--self-test", required=True)
    correctness_archive.add_argument("--self-oracle", required=True)
    correctness_archive.add_argument("--verify", required=True)
    correctness_archive.add_argument("--output", required=True)

    corrected_archive = commands.add_parser("amend", help="append corrected exact traces without hiding historical failures")
    corrected_archive.add_argument("--module", default="candidates.rust_candidate")
    corrected_archive.add_argument("--evidence", required=True)
    corrected_archive.add_argument("--verification", required=True)
    corrected_archive.add_argument("--label", choices=("isolated", "production"), required=True)
    corrected_archive.add_argument("--output", required=True)

    args = parser.parse_args()
    if args.command == "self-test":
        report = self_test(args)
    elif args.command == "oracle-self":
        report = oracle_self(args)
    elif args.command == "verify":
        report = verify(args)
    elif args.command == "capture":
        report = capture(args)
    elif args.command == "amend":
        report = amend_capture(args)
    elif args.command == "bundle":
        report = bundle(args)
    else:
        report = measure(args)
    mismatches = report.get(
        "mismatches",
        report.get(
            "production_corrected_mismatches",
            report.get("candidate_mismatches", 0),
        ),
    )
    result = report.get(
        "result",
        report.get("final_result", "PASS" if mismatches == 0 else "FAIL"),
    )
    cases = report.get(
        "cases",
        report.get(
            "checks",
            report.get("candidate_checks", report.get("timing_cases")),
        ),
    )
    print(
        json.dumps(
            {
                "schema": report["schema"],
                "kind": report["kind"],
                "result": result,
                "cases": cases,
                "mismatches": mismatches,
                "holdout_accessed": report["holdout_accessed"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
