#!/usr/bin/env python3
"""Additive, benchmark-blind CPython 3.14.6 public-contract differential.

The reference and native candidate run in separate Python processes.  Native
workers poison every CPython regular-expression entry point before executing
any case.  Implementation-specific garbage-collector graph topology is recorded
and compared separately; it is never counted as documented public equality.
"""

from __future__ import annotations

import array
import collections
import copy
import gc
import gzip
import hashlib
import importlib
import inspect
import json
import os
import pickle
import random
import subprocess
import sys
import types
import warnings
import weakref
from pathlib import Path
from typing import Any


SCHEMA = "rebar-rust-v8-deep-public-contract-v1"
PINNED = (3, 14, 6)
PINNED_EXECUTABLE = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
SEED = 2026072347
SEEDED_CASES = 64
ROOT = Path(__file__).resolve().parent.parent
SCRIPT = Path(__file__).resolve()
EVIDENCE = ROOT / "candidates/audits/RUST-V8-DEEP-CONTRACT.json.gz"
CANONICAL_ARTIFACTS = {
    "public-python": (
        "candidates/rust_candidate.py",
        "1111a419d65d44775d1f4b0cb6a728dea8de44a592597341596533351c16018e",
    ),
    "native-source": (
        "candidates/rust/src/lib.rs",
        "a2fa04912bb1f6957f833560446f4d3d1c5d13df8b5efac992fa63e28803668b",
    ),
    "bridge-source": (
        "candidates/rust/py_bridge.c",
        "8900b120ddb85a74aedf584b960ff878aa47020c910c0ce749dae51eb304f3c2",
    ),
    "native-engine": (
        "candidates/_rust_engine.so",
        "890f9e34e966244067a3dc173c2276043ae15d4830a05228fb37ec2571aa17cd",
    ),
    "native-bridge": (
        "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "eedcd253ab9ec6bab9a9ac9242d04d3fc6c808bf1b8de342bb5a5b9fd8528272",
    ),
}
HEX_DIGITS = frozenset("0123456789abcdefABCDEF")
MISSING = object()


class CallbackSignal(Exception):
    """Deterministic exception raised by user replacement callbacks."""


class ConverterSignal(Exception):
    """Deterministic exception raised by user conversion protocols."""


class OuterSignal(Exception):
    """Deterministic exception used to preserve active exception state."""


class GuardSignal(AssertionError):
    """Raised if a production worker reaches a CPython regex entry point."""


class TextSubclass(str):
    pass


class BytesSubclass(bytes):
    pass


class FinalizedText(str):
    def __new__(cls, value: str, events: list[Any], label: str):
        item = str.__new__(cls, value)
        item.events = events
        item.label = label
        return item

    def __del__(self):
        self.events.append(("__del__", self.label))


class EventIndex:
    def __init__(self, events: list[Any], mode: str, label: str):
        self.events = events
        self.mode = mode
        self.label = label

    def __index__(self):
        self.events.append(("__index__", self.label, self.mode))
        if self.mode == "raise":
            raise ConverterSignal("deep-contract __index__ sentinel")
        if self.mode == "noninteger":
            return "not an integer"
        if self.mode == "overflow":
            return 1 << 100
        if self.mode == "negative":
            return -1
        return 1

    def __int__(self):
        self.events.append(("__int__", self.label, self.mode))
        return 1


class EventName(str):
    def __new__(cls, value: str, events: list[Any], mode: str):
        item = str.__new__(cls, value)
        item.events = events
        item.mode = mode
        return item

    def __hash__(self):
        self.events.append(("__hash__", str(self), self.mode))
        if self.mode == "raise":
            raise ConverterSignal("deep-contract group-name hash sentinel")
        return str.__hash__(self)

    def __eq__(self, other):
        self.events.append(("__eq__", str(self), stable_text(other)))
        if self.mode == "eq-raise":
            raise ConverterSignal("deep-contract group-name equality sentinel")
        return str.__eq__(self, other)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=True,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("ascii")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def file_digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def stable_text(value: Any) -> str:
    text = str(value)
    parts: list[str] = []
    cursor = 0
    while True:
        marker = text.find("0x", cursor)
        if marker < 0:
            parts.append(text[cursor:])
            return "".join(parts)
        end = marker + 2
        while end < len(text) and text[end] in HEX_DIGITS:
            end += 1
        if end == marker + 2:
            parts.append(text[cursor:end])
        else:
            parts.extend((text[cursor:marker], "0x<address>"))
        cursor = end


def normalize(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int)):
        return value
    if isinstance(value, str):
        text = stable_text(value)
        if any(0xD800 <= ord(char) <= 0xDFFF for char in text):
            return {
                "kind": type(value).__name__,
                "surrogatepass_utf8_hex": text.encode(
                    "utf-8", "surrogatepass"
                ).hex(),
            }
        if type(value) is str:
            return text
        return {"kind": type(value).__name__, "text": text}
    if isinstance(value, (bytes, bytearray)):
        return {"kind": type(value).__name__, "hex": bytes(value).hex()}
    if isinstance(value, array.array):
        return {
            "kind": "array",
            "typecode": value.typecode,
            "hex": value.tobytes().hex(),
        }
    if isinstance(value, memoryview):
        return {
            "kind": "memoryview",
            "hex": value.tobytes().hex(),
            "format": value.format,
            "shape": list(value.shape),
            "c_contiguous": value.c_contiguous,
        }
    if isinstance(value, (tuple, list)):
        return [normalize(item) for item in value]
    if isinstance(value, dict):
        return {
            stable_text(key): normalize(item)
            for key, item in sorted(
                value.items(), key=lambda entry: stable_text(entry[0])
            )
        }
    if isinstance(value, types.MappingProxyType):
        return {"kind": "mappingproxy", "value": normalize(dict(value))}
    if isinstance(value, type):
        return {
            "kind": "type",
            "module": value.__module__,
            "name": value.__qualname__,
        }
    return {
        "kind": type(value).__name__,
        "repr": stable_text(repr(value)),
    }


def traceback_snapshot(traceback: Any) -> list[dict[str, Any]]:
    result = []
    while traceback is not None:
        frame = traceback.tb_frame
        if Path(frame.f_code.co_filename).resolve() == SCRIPT:
            result.append(
                {
                    "function": frame.f_code.co_name,
                    "line": traceback.tb_lineno,
                }
            )
        traceback = traceback.tb_next
    return result


def error_snapshot(error: BaseException, depth: int = 0) -> dict[str, Any]:
    if depth > 5:
        raise AssertionError("exception chaining exceeded the fixed audit depth")
    return {
        "type": type(error).__name__,
        "args": normalize(error.args),
        "notes": normalize(getattr(error, "__notes__", [])),
        "cause": (
            error_snapshot(error.__cause__, depth + 1)
            if error.__cause__ is not None
            else None
        ),
        "context": (
            error_snapshot(error.__context__, depth + 1)
            if error.__context__ is not None
            else None
        ),
        "suppress_context": error.__suppress_context__,
        "public_traceback": traceback_snapshot(error.__traceback__),
    }


def attempted(action: Any) -> dict[str, Any]:
    try:
        return {"status": "value", "value": normalize(action())}
    except BaseException as error:
        return {"status": "error", "error": error_snapshot(error)}


def active_exception() -> Any:
    current = sys.exception()
    if current is None:
        return None
    return {"type": type(current).__name__, "args": normalize(current.args)}


def match_snapshot(match: Any, subject: Any = MISSING) -> Any:
    if match is None:
        return None
    return {
        "span": normalize(match.span()),
        "regs": normalize(match.regs),
        "regs_cached": match.regs is match.regs,
        "group0": normalize(match.group(0)),
        "groups": normalize(match.groups()),
        "groupdict": normalize(match.groupdict()),
        "lastindex": match.lastindex,
        "lastgroup": match.lastgroup,
        "pos": match.pos,
        "endpos": match.endpos,
        "same_subject": (
            match.string is subject if subject is not MISSING else None
        ),
    }


def case(family: str, label: str, **settings: Any) -> dict[str, Any]:
    return {"family": family, "id": f"{family}/{label}", **settings}


def build_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for holder in ("match", "iterator", "scanner"):
        for cyclic in (False, True):
            cases.append(
                case(
                    "gc-lifetime-finalization",
                    f"{holder}/cyclic={int(cyclic)}",
                    holder=holder,
                    cyclic=cyclic,
                )
            )
    for subject in (
        "bytearray",
        "memoryview",
        "cast-memoryview",
        "noncontiguous-memoryview",
        "released-memoryview",
        "array",
    ):
        for holder in ("match", "iterator", "scanner", "findall", "sub"):
            cases.append(
                case(
                    "buffer-export-mutation",
                    f"{subject}/{holder}",
                    subject=subject,
                    holder=holder,
                )
            )
    for holder in ("iterator", "scanner"):
        for expression in ("a", "a*", "(?P<letter>a)(b)?", "(?=a)"):
            for action in (
                "copy",
                "deepcopy",
                "pickle",
                "reduce",
                "reduce-ex",
                "weakref",
            ):
                cases.append(
                    case(
                        "stateful-scanner-copy",
                        f"{holder}/{expression}/{action}",
                        holder=holder,
                        expression=expression,
                        action=action,
                    )
                )
    for operation in ("sub", "subn"):
        for bound in (False, True):
            for byte_mode in (False, True):
                for mode in (
                    "value",
                    "subclass",
                    "none",
                    "wrong-domain",
                    "raise-first",
                    "raise-second",
                    "raise-chained",
                    "stop-iteration",
                    "recursive",
                ):
                    cases.append(
                        case(
                            "callback-reentry-exception-state",
                            (
                                f"{operation}/bound={int(bound)}"
                                f"/bytes={int(byte_mode)}/{mode}"
                            ),
                            operation=operation,
                            bound=bound,
                            byte_mode=byte_mode,
                            mode=mode,
                        )
                    )
    for method in (
        "search",
        "match",
        "fullmatch",
        "findall",
        "finditer",
        "scanner",
    ):
        for mode in ("value", "negative", "raise", "noninteger", "overflow"):
            for position in ("pos", "endpos"):
                cases.append(
                    case(
                        "malicious-window-converter",
                        f"{method}/{position}/{mode}",
                        method=method,
                        position=position,
                        mode=mode,
                    )
                )
    for method in ("split", "sub", "subn"):
        for mode in ("value", "negative", "raise", "noninteger", "overflow"):
            cases.append(
                case(
                    "malicious-count-converter",
                    f"{method}/{mode}",
                    method=method,
                    mode=mode,
                )
            )
    for method in ("group", "start", "end", "span", "getitem"):
        for mode in ("value", "raise", "eq-raise", "missing"):
            cases.append(
                case(
                    "malicious-group-converter",
                    f"{method}/{mode}",
                    method=method,
                    mode=mode,
                )
            )
    for instrument in ("trace", "profile", "monitoring"):
        for operation in ("sub", "subn"):
            for bound in (False, True):
                for failure in (False, True):
                    cases.append(
                        case(
                            "callback-public-instrumentation",
                            (
                                f"{instrument}/{operation}"
                                f"/bound={int(bound)}/failure={int(failure)}"
                            ),
                            instrument=instrument,
                            operation=operation,
                            bound=bound,
                            failure=failure,
                        )
                    )
    for owner in ("pattern-class", "pattern-bound", "match-class", "match-bound"):
        names = (
            ("search", "match", "fullmatch", "findall", "finditer", "scanner", "split", "sub", "subn")
            if owner.startswith("pattern")
            else ("group", "groups", "groupdict", "start", "end", "span", "expand")
        )
        for name in names:
            cases.append(
                case(
                    "public-method-introspection",
                    f"{owner}/{name}",
                    owner=owner,
                    name=name,
                )
            )
    for owner in ("pattern", "match", "scanner", "iterator"):
        cases.append(case("public-object-introspection", owner, owner=owner))
    for byte_mode in (False, True):
        for operation in (
            "nested-set",
            "intersection",
            "difference",
            "split-positional",
            "split-flags-positional",
            "sub-positional",
            "sub-flags-positional",
            "subn-positional",
            "subn-flags-positional",
        ):
            cases.append(
                case(
                    "warning-call-site",
                    f"bytes={int(byte_mode)}/{operation}",
                    byte_mode=byte_mode,
                    operation=operation,
                )
            )
    frozen = tuple(cases)
    generator = random.Random(SEED)
    for number in range(SEEDED_CASES):
        original = generator.choice(frozen)
        cases.append(
            {
                **original,
                "family": f"seeded/{original['family']}",
                "id": f"seeded/{number:03d}/{original['id']}",
                "original_id": original["id"],
            }
        )
    identifiers = [item["id"] for item in cases]
    if len(identifiers) != len(set(identifiers)):
        raise AssertionError("deep-contract case identifiers are not unique")
    if len(frozen) != 329 or len(cases) != 393:
        raise AssertionError("deep-contract case denominator changed")
    return cases


def private_referents(holder: Any, subject: Any, pattern: Any) -> dict[str, Any]:
    entries = []
    for item in gc.get_referents(holder):
        entries.append(
            {
                "type_module": type(item).__module__,
                "type_name": type(item).__qualname__,
                "is_subject": item is subject,
                "is_pattern": item is pattern,
            }
        )
    return {
        "classification": "implementation-private-gc-referent-topology",
        "documented_public_equality": False,
        "holder_type_module": type(holder).__module__,
        "holder_type_name": type(holder).__qualname__,
        "holder_gc_tracked": gc.is_tracked(holder),
        "direct_referents": sorted(
            entries,
            key=lambda item: (
                item["type_module"],
                item["type_name"],
                item["is_subject"],
                item["is_pattern"],
            ),
        ),
    }


def lifetime_case(module: Any, spec: dict[str, Any]) -> tuple[Any, Any]:
    events: list[Any] = []
    module.purge()
    subject = FinalizedText("aba", events, "subject")
    subject_ref = weakref.ref(
        subject, lambda unused: events.append(("weakref", "subject"))
    )
    pattern = module.compile("a")
    pattern_ref = weakref.ref(
        pattern, lambda unused: events.append(("weakref", "pattern"))
    )
    module.purge()
    holder_kind = spec["holder"]
    if holder_kind == "match":
        holder = pattern.search(subject)
    elif holder_kind == "iterator":
        holder = pattern.finditer(subject)
    elif holder_kind == "scanner":
        holder = pattern.scanner(subject)
    else:
        raise AssertionError("unrecognized lifetime holder")
    if spec["cyclic"]:
        subject.backlink = holder
    diagnostic = private_referents(holder, subject, pattern)
    initial = {
        "subject_alive": subject_ref() is not None,
        "pattern_alive": pattern_ref() is not None,
        "holder_gc_tracked": gc.is_tracked(holder),
    }
    del subject
    del pattern
    gc.collect()
    retained = {
        "subject_alive": subject_ref() is not None,
        "pattern_alive": pattern_ref() is not None,
        "events": normalize(list(events)),
    }
    if holder_kind == "match":
        observed = attempted(lambda: match_snapshot(holder))
    elif holder_kind == "iterator":
        observed = attempted(
            lambda: [match_snapshot(next(holder, None)) for unused in range(4)]
        )
    else:
        observed = attempted(
            lambda: [match_snapshot(holder.search()) for unused in range(4)]
        )
    gc.collect()
    exhausted = {
        "subject_alive": subject_ref() is not None,
        "pattern_alive": pattern_ref() is not None,
        "events": normalize(list(events)),
    }
    del holder
    gc.collect()
    gc.collect()
    released = {
        "subject_alive": subject_ref() is not None,
        "pattern_alive": pattern_ref() is not None,
        "events": normalize(list(events)),
    }
    return {
        "initial": initial,
        "retained": retained,
        "observed": observed,
        "exhausted": exhausted,
        "released": released,
        "recovery": match_snapshot(module.fullmatch("a", "a")),
    }, diagnostic


def resize_probe(storage: Any) -> str:
    storage.append(33)
    storage.pop()
    return "append-and-pop"


def make_buffer_subject(kind: str) -> tuple[Any, Any, Any]:
    if kind == "array":
        storage = array.array("B", b"aba")
        return storage, storage, None
    storage = bytearray(b"aba")
    if kind == "bytearray":
        return storage, storage, None
    view = memoryview(storage)
    if kind == "cast-memoryview":
        view = view.cast("c").cast("B")
    elif kind == "noncontiguous-memoryview":
        view = view[::2]
    elif kind == "released-memoryview":
        view.release()
    elif kind != "memoryview":
        raise AssertionError("unrecognized buffer subject")
    return storage, view, view


def buffer_case(module: Any, spec: dict[str, Any]) -> tuple[Any, Any]:
    storage, subject, view = make_buffer_subject(spec["subject"])
    pattern = module.compile(rb"(?P<letter>a)(b)?")
    kind = spec["holder"]
    box: list[Any] = []

    def open_holder():
        if kind == "match":
            value = pattern.search(subject)
            summary = match_snapshot(value, subject)
        elif kind == "iterator":
            value = pattern.finditer(subject)
            summary = {"iterator_is_self": iter(value) is value}
        elif kind == "scanner":
            value = pattern.scanner(subject)
            summary = {"has_search": callable(value.search)}
        elif kind == "findall":
            value = pattern.findall(subject)
            summary = normalize(value)
        elif kind == "sub":
            value = pattern.sub(b"x", subject)
            summary = normalize(value)
        else:
            raise AssertionError("unrecognized buffer holder")
        box.append(value)
        return summary

    opened = attempted(open_holder)
    output: dict[str, Any] = {
        "subject_kind": spec["subject"],
        "opened": opened,
        "storage_before": bytes(storage).hex(),
    }
    if not box:
        output["resize_after_rejection"] = attempted(
            lambda: resize_probe(storage)
        )
        if view is not None:
            output["release_after_rejection"] = attempted(view.release)
            output["resize_after_release"] = attempted(
                lambda: resize_probe(storage)
            )
        return output, {}

    holder = box.pop()
    output["resize_while_live"] = attempted(lambda: resize_probe(storage))

    def mutate():
        storage[0] = ord("z")
        return bytes(storage)

    output["mutation"] = attempted(mutate)
    if kind == "match":
        output["after_mutation"] = attempted(
            lambda: match_snapshot(holder, subject)
        )
    elif kind == "iterator":
        output["after_mutation"] = attempted(
            lambda: [
                match_snapshot(next(holder, None), subject)
                for unused in range(4)
            ]
        )
        output["exhaustion_exception"] = attempted(lambda: next(holder))
    elif kind == "scanner":
        output["after_mutation"] = attempted(
            lambda: [
                match_snapshot(holder.search(), subject)
                for unused in range(4)
            ]
        )
        output["exhaustion_repeat"] = attempted(
            lambda: match_snapshot(holder.search(), subject)
        )
    else:
        output["after_mutation"] = normalize(holder)
    output["resize_after_exhaustion"] = attempted(
        lambda: resize_probe(storage)
    )
    if view is not None:
        output["release_while_holder_live"] = attempted(view.release)
    del holder
    gc.collect()
    if view is not None:
        output["release_after_holder"] = attempted(view.release)
    output["resize_after_holder"] = attempted(lambda: resize_probe(storage))
    output["storage_final"] = bytes(storage).hex()
    return output, {}


def scanner_case(module: Any, spec: dict[str, Any]) -> tuple[Any, Any]:
    subject = "aba"
    pattern = module.compile(spec["expression"])
    if spec["holder"] == "iterator":
        holder = pattern.finditer(subject)

        def advance():
            return match_snapshot(next(holder, None), subject)

    else:
        holder = pattern.scanner(subject)

        def advance():
            return match_snapshot(holder.search(), subject)

    first = attempted(advance)
    operation = spec["action"]
    if operation == "copy":
        action = lambda: describe_copy(copy.copy(holder), holder)
    elif operation == "deepcopy":
        action = lambda: describe_copy(copy.deepcopy(holder), holder)
    elif operation == "pickle":
        action = lambda: pickle.dumps(holder, protocol=pickle.HIGHEST_PROTOCOL)
    elif operation == "reduce":
        action = lambda: holder.__reduce__()
    elif operation == "reduce-ex":
        action = lambda: holder.__reduce_ex__(pickle.HIGHEST_PROTOCOL)
    elif operation == "weakref":
        action = lambda: weakref.ref(holder)() is holder
    else:
        raise AssertionError("unrecognized stateful copy operation")
    intervention = attempted(action)
    remaining = [attempted(advance) for unused in range(5)]
    return {
        "first": first,
        "intervention": intervention,
        "remaining": remaining,
        "recovery": match_snapshot(module.fullmatch("a", "a")),
    }, private_referents(holder, subject, pattern)


def describe_copy(result: Any, original: Any) -> dict[str, Any]:
    return {
        "same_object": result is original,
        "type_module": type(result).__module__,
        "type_name": type(result).__qualname__,
    }


def callback_case(module: Any, spec: dict[str, Any]) -> tuple[Any, Any]:
    events: list[Any] = []
    byte_mode = spec["byte_mode"]
    expression = rb"(?P<letter>a)(b)?" if byte_mode else r"(?P<letter>a)(b)?"
    subject = bytearray(b"aba") if byte_mode else TextSubclass("aba")
    marker = b"!" if byte_mode else "!"
    pattern = module.compile(expression)
    operation = spec["operation"]
    outer_reference: list[Any] = []

    def replacement(match):
        index = len(events)
        piece = match.group("letter")
        events.append(
            {
                "event": "callback",
                "index": index,
                "match": match_snapshot(match, subject),
                "same_pattern": match.re is pattern,
                "active_exception": active_exception(),
                "builtin_len": len(piece),
            }
        )
        mode = spec["mode"]
        if mode == "raise-first":
            raise CallbackSignal("deep-contract callback sentinel")
        if mode == "raise-second" and index == 1:
            raise CallbackSignal("deep-contract callback sentinel")
        if mode == "raise-chained":
            raise CallbackSignal("deep-contract chained callback") from outer_reference[0]
        if mode == "stop-iteration":
            raise StopIteration("deep-contract callback sentinel")
        if mode == "none":
            return None
        if mode == "wrong-domain":
            return "wrong" if byte_mode else b"wrong"
        if mode == "recursive":
            nested = pattern.search(subject)
            events.append(
                {
                    "event": "recursive-search",
                    "match": match_snapshot(nested, subject),
                    "active_exception": active_exception(),
                }
            )
        result = piece + marker
        if mode == "subclass":
            return BytesSubclass(result) if byte_mode else TextSubclass(result)
        return result

    if spec["bound"]:
        invoke = lambda: getattr(pattern, operation)(replacement, subject, 0)
    else:
        invoke = lambda: getattr(module, operation)(
            expression, replacement, subject, count=0
        )
    try:
        raise OuterSignal("deep-contract active exception")
    except OuterSignal as outer:
        outer_reference.append(outer)
        before = active_exception()
        result = attempted(invoke)
        after = active_exception()
    resize = attempted(lambda: resize_probe(subject)) if byte_mode else None
    return {
        "active_before": before,
        "result": result,
        "active_after": after,
        "events": normalize(events),
        "resize_after_callback": resize,
        "recovery": match_snapshot(module.fullmatch("a", "a")),
    }, {}


def window_case(module: Any, spec: dict[str, Any]) -> tuple[Any, Any]:
    events: list[Any] = []
    bomb = EventIndex(events, spec["mode"], spec["position"])
    pattern = module.compile(r"(?P<letter>a)(b)?")
    method = getattr(pattern, spec["method"])
    if spec["position"] == "pos":
        action = lambda: describe_window(method("aba", bomb), spec["method"])
    else:
        action = lambda: describe_window(method("aba", 0, bomb), spec["method"])
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        result = attempted(action)
    return {
        "result": result,
        "conversion_events": normalize(events),
        "warnings": normalize(
            [
                {"category": item.category.__name__, "message": str(item.message)}
                for item in captured
            ]
        ),
        "active_exception_after": active_exception(),
        "recovery": match_snapshot(module.fullmatch("a", "a")),
    }, {}


def describe_window(value: Any, method: str) -> Any:
    if method in ("search", "match", "fullmatch"):
        return match_snapshot(value, "aba")
    if method == "findall":
        return normalize(value)
    if method == "finditer":
        return {
            "iterator_is_self": iter(value) is value,
            "matches": [match_snapshot(item, "aba") for item in value],
            "exhausted": next(value, None) is None,
        }
    if method == "scanner":
        return [match_snapshot(value.search(), "aba") for unused in range(4)]
    raise AssertionError("unrecognized window result")


def count_case(module: Any, spec: dict[str, Any]) -> tuple[Any, Any]:
    events: list[Any] = []
    bomb = EventIndex(events, spec["mode"], "count")
    pattern = module.compile("a")
    if spec["method"] == "split":
        action = lambda: pattern.split("aba", bomb)
    else:
        action = lambda: getattr(pattern, spec["method"])("x", "aba", bomb)
    return {
        "result": attempted(action),
        "conversion_events": normalize(events),
        "active_exception_after": active_exception(),
        "recovery": match_snapshot(module.fullmatch("a", "a")),
    }, {}


def group_case(module: Any, spec: dict[str, Any]) -> tuple[Any, Any]:
    events: list[Any] = []
    match = module.search(r"(?P<letter>a)(b)?", "a")
    value = "missing" if spec["mode"] == "missing" else "letter"
    name = EventName(value, events, spec["mode"])
    if spec["method"] == "getitem":
        action = lambda: match[name]
    else:
        action = lambda: getattr(match, spec["method"])(name)
    return {
        "result": attempted(action),
        "conversion_events": normalize(events),
        "recovery": match_snapshot(module.fullmatch("a", "a")),
    }, {}


def instrumentation_case(module: Any, spec: dict[str, Any]) -> tuple[Any, Any]:
    events: list[Any] = []
    effects: list[Any] = []
    pattern = module.compile(r"(?P<letter>a)(b)?")

    def replacement(match):
        piece = match.group("letter")
        size = len(piece)
        effects.append((match.span(), piece, size, active_exception()))
        if spec["failure"] and len(effects) == 2:
            raise CallbackSignal("deep-contract instrumentation sentinel")
        return piece + "!"

    code = replacement.__code__
    if spec["bound"]:
        invoke = lambda: getattr(pattern, spec["operation"])(
            replacement, "aba", 0
        )
    else:
        invoke = lambda: getattr(module, spec["operation"])(
            r"(?P<letter>a)(b)?", replacement, "aba", count=0
        )
    instrument = spec["instrument"]
    if instrument == "trace":
        before = sys.gettrace()

        def tracer(frame, event, argument):
            if frame.f_code is code:
                item: dict[str, Any] = {"event": event}
                if event == "line":
                    item["line_offset"] = frame.f_lineno - code.co_firstlineno
                elif event == "return":
                    item["value"] = normalize(argument)
                elif event == "exception":
                    item["error_type"] = argument[0].__name__
                    item["error_args"] = normalize(argument[1].args)
                events.append(item)
                return tracer
            return tracer

        sys.settrace(tracer)
        try:
            result = attempted(invoke)
        finally:
            sys.settrace(before)
        restored = sys.gettrace() is before
    elif instrument == "profile":
        before = sys.getprofile()

        def profiler(frame, event, argument):
            if frame.f_code is code:
                if event in ("call", "return"):
                    events.append(
                        {
                            "event": event,
                            "value": normalize(argument)
                            if event == "return"
                            else None,
                        }
                    )
                elif event in ("c_call", "c_return", "c_exception") and argument is len:
                    events.append({"event": event, "callable": "builtins.len"})
            return profiler

        sys.setprofile(profiler)
        try:
            result = attempted(invoke)
        finally:
            sys.setprofile(before)
        restored = sys.getprofile() is before
    elif instrument == "monitoring":
        monitor = getattr(sys, "monitoring", None)
        if monitor is None:
            raise AssertionError("pinned CPython is missing sys.monitoring")
        tool_id = next(
            (number for number in (4, 3) if monitor.get_tool(number) is None),
            None,
        )
        if tool_id is None:
            raise AssertionError("no isolated sys.monitoring tool is available")
        registered = []

        def receiver(name):
            def receive(*arguments):
                if not arguments or arguments[0] is not code:
                    return None
                if name in ("PY_START", "PY_RETURN", "PY_UNWIND"):
                    item: dict[str, Any] = {"event": name}
                    if name == "PY_RETURN" and len(arguments) > 2:
                        item["value"] = normalize(arguments[-1])
                    events.append(item)
                elif name in ("CALL", "C_RETURN", "C_RAISE"):
                    called = arguments[2] if len(arguments) > 2 else None
                    if called is len:
                        events.append({"event": name, "callable": "builtins.len"})
                return None

            return receive

        monitor.use_tool_id(tool_id, "rebar-rust-v8-deep-public-contract")
        try:
            for name in (
                "PY_START", "PY_RETURN", "PY_UNWIND", "CALL", "C_RETURN", "C_RAISE"
            ):
                event = getattr(monitor.events, name, None)
                if event is not None:
                    monitor.register_callback(tool_id, event, receiver(name))
                    registered.append(event)
            mask = (
                monitor.events.PY_START
                | monitor.events.PY_RETURN
                | monitor.events.PY_UNWIND
                | monitor.events.CALL
            )
            monitor.set_events(tool_id, mask)
            try:
                result = attempted(invoke)
            finally:
                monitor.set_events(tool_id, monitor.events.NO_EVENTS)
        finally:
            for event in registered:
                monitor.register_callback(tool_id, event, None)
            monitor.free_tool_id(tool_id)
        restored = monitor.get_tool(tool_id) is None
    else:
        raise AssertionError("unrecognized public instrumentation")
    return {
        "instrument": instrument,
        "result": result,
        "public_events": normalize(events),
        "callback_effects": normalize(effects),
        "instrument_restored": restored,
        "recovery": match_snapshot(module.fullmatch("a", "a")),
    }, {}


def method_case(module: Any, spec: dict[str, Any]) -> tuple[Any, Any]:
    pattern = module.compile(r"(?P<letter>a)(b)?")
    match = pattern.search("a")
    owner = spec["owner"]
    name = spec["name"]
    if owner == "pattern-class":
        value = getattr(module.Pattern, name)
        expected_self = None
    elif owner == "pattern-bound":
        value = getattr(pattern, name)
        expected_self = pattern
    elif owner == "match-class":
        value = getattr(module.Match, name)
        expected_self = None
    elif owner == "match-bound":
        value = getattr(match, name)
        expected_self = match
    else:
        raise AssertionError("unrecognized public method owner")
    return {
        "signature": attempted(lambda: str(inspect.signature(value))),
        "name": attempted(lambda: value.__name__),
        "qualname": attempted(lambda: value.__qualname__),
        "text_signature": attempted(lambda: value.__text_signature__),
        "documentation": attempted(lambda: value.__doc__),
        "inspect_isbuiltin": inspect.isbuiltin(value),
        "inspect_ismethoddescriptor": inspect.ismethoddescriptor(value),
        "callable": callable(value),
        "bound_self": (
            attempted(lambda: value.__self__ is expected_self)
            if expected_self is not None
            else attempted(lambda: hasattr(value, "__self__"))
        ),
        "fresh_bound_method": (
            getattr(expected_self, name) is value
            if expected_self is not None
            else None
        ),
        "repr": attempted(lambda: stable_text(repr(value))),
    }, {}


def object_case(module: Any, spec: dict[str, Any]) -> tuple[Any, Any]:
    subject = TextSubclass("aba")
    pattern = module.compile(r"(?P<letter>a)(b)?")
    owner = spec["owner"]
    if owner == "pattern":
        value = pattern
    elif owner == "match":
        value = pattern.search(subject)
    elif owner == "scanner":
        value = pattern.scanner(subject)
    elif owner == "iterator":
        value = pattern.finditer(subject)
    else:
        raise AssertionError("unrecognized public object")
    result = {
        "type_module": type(value).__module__,
        "type_name": type(value).__name__,
        "type_qualname": type(value).__qualname__,
        "repr": attempted(lambda: stable_text(repr(value))),
        "public_directory": [name for name in dir(value) if not name.startswith("_")],
        "gc_tracked": gc.is_tracked(value),
        "weakref": attempted(lambda: weakref.ref(value)() is value),
        "copy": attempted(lambda: describe_copy(copy.copy(value), value)),
        "deepcopy": attempted(lambda: describe_copy(copy.deepcopy(value), value)),
    }
    if owner == "match":
        result["snapshot"] = match_snapshot(value, subject)
    return result, private_referents(value, subject, pattern)


def warning_case(module: Any, spec: dict[str, Any]) -> tuple[Any, Any]:
    byte_mode = spec["byte_mode"]
    operation = spec["operation"]
    subject = b"aaa" if byte_mode else "aaa"
    replacement = b"x" if byte_mode else "x"
    module.purge()

    def invoke():
        if operation == "nested-set":
            expression = b"[[]" if byte_mode else "[[]"
            value = module.compile(expression)
            return {"compiled": True, "flags": value.flags}
        if operation == "intersection":
            expression = b"[a&&b]" if byte_mode else "[a&&b]"
            value = module.compile(expression)
            return {"compiled": True, "flags": value.flags}
        if operation == "difference":
            expression = b"[a--b]" if byte_mode else "[a--b]"
            value = module.compile(expression)
            return {"compiled": True, "flags": value.flags}
        expression = b"a" if byte_mode else "a"
        if operation == "split-positional":
            return module.split(expression, subject, 1)
        if operation == "split-flags-positional":
            return module.split(expression, subject, 1, 0)
        if operation == "sub-positional":
            return module.sub(expression, replacement, subject, 1)
        if operation == "sub-flags-positional":
            return module.sub(expression, replacement, subject, 1, 0)
        if operation == "subn-positional":
            return module.subn(expression, replacement, subject, 1)
        if operation == "subn-flags-positional":
            return module.subn(expression, replacement, subject, 1, 0)
        raise AssertionError("unrecognized public warning case")

    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        result = attempted(invoke)
    recorded = []
    for item in captured:
        location = Path(item.filename).resolve()
        recorded.append(
            {
                "category": item.category.__name__,
                "message": stable_text(item.message),
                "at_public_call_site": location == SCRIPT,
                "filename": location.name,
                "line_offset": item.lineno - invoke.__code__.co_firstlineno,
            }
        )
    return {"result": result, "warnings": recorded}, {}


DISPATCH = {
    "gc-lifetime-finalization": lifetime_case,
    "buffer-export-mutation": buffer_case,
    "stateful-scanner-copy": scanner_case,
    "callback-reentry-exception-state": callback_case,
    "malicious-window-converter": window_case,
    "malicious-count-converter": count_case,
    "malicious-group-converter": group_case,
    "callback-public-instrumentation": instrumentation_case,
    "public-method-introspection": method_case,
    "public-object-introspection": object_case,
    "warning-call-site": warning_case,
}


def verify_runtime() -> None:
    if tuple(sys.version_info[:3]) != PINNED:
        raise AssertionError("deep-contract oracle requires CPython 3.14.6")
    if sys.implementation.name != "cpython":
        raise AssertionError("deep-contract oracle requires CPython")
    if Path(sys.executable).resolve() != PINNED_EXECUTABLE.resolve():
        raise AssertionError("deep-contract oracle requires the pinned executable")
    if os.environ.get("PYTHONDONTWRITEBYTECODE") != "1":
        raise AssertionError("PYTHONDONTWRITEBYTECODE=1 is mandatory")
    path_entries = os.environ.get("PYTHONPATH", "").split(os.pathsep)
    if "." not in path_entries and str(ROOT) not in path_entries:
        raise AssertionError("PYTHONPATH=. or the canonical root is mandatory")


def production_provenance(module: Any) -> list[dict[str, str]]:
    bridge = importlib.import_module("candidates._rust_bridge")
    public_path = ROOT / CANONICAL_ARTIFACTS["public-python"][0]
    bridge_path = ROOT / CANONICAL_ARTIFACTS["native-bridge"][0]
    if Path(module.__file__).resolve() != public_path.resolve():
        raise AssertionError("the canonical production Rust module is not loaded")
    if Path(bridge.__file__).resolve() != bridge_path.resolve():
        raise AssertionError("the canonical production native bridge is not loaded")
    mapped = set()
    for line in Path("/proc/self/maps").read_text(encoding="ascii").splitlines():
        fields = line.split(maxsplit=5)
        if len(fields) == 6:
            mapped.add(fields[5].removesuffix(" (deleted)"))
    for role in ("native-bridge", "native-engine"):
        expected_path = str((ROOT / CANONICAL_ARTIFACTS[role][0]).resolve())
        if expected_path not in mapped:
            raise AssertionError(f"canonical production {role} is not mapped")
    result = []
    for role, (relative, expected) in sorted(CANONICAL_ARTIFACTS.items()):
        actual = file_digest(ROOT / relative)
        if actual != expected:
            raise AssertionError(
                f"canonical production artifact changed: {role}: "
                f"expected {expected}, observed {actual}"
            )
        result.append({"role": role, "path": relative, "sha256": actual})
    return result


def install_regex_guards() -> list[tuple[Any, str, Any]]:
    standard = importlib.import_module("re")
    sre = importlib.import_module("_sre")
    compiler = importlib.import_module("re._compiler")
    parser = importlib.import_module("re._parser")

    def forbidden(*args: Any, **kwargs: Any) -> Any:
        raise GuardSignal("production reached a forbidden CPython regex entry point")

    guards = []
    for name in (
        "compile", "search", "match", "fullmatch", "findall", "finditer",
        "split", "sub", "subn", "_compile",
    ):
        if not hasattr(standard, name):
            raise AssertionError(f"missing CPython regex guard: re.{name}")
        setattr(standard, name, forbidden)
        guards.append((standard, name, forbidden))
    for owner, name in ((sre, "compile"), (compiler, "compile"), (parser, "parse")):
        if not hasattr(owner, name):
            raise AssertionError(f"missing CPython regex delegation guard: {name}")
        setattr(owner, name, forbidden)
        guards.append((owner, name, forbidden))
    if len(guards) != 13:
        raise AssertionError("the CPython regex-poison denominator changed")
    if any(getattr(owner, name) is not poison for owner, name, poison in guards):
        raise AssertionError("a CPython regex guard could not be installed")
    return guards


def audit_regex_guards(guards: list[tuple[Any, str, Any]]) -> list[dict[str, Any]]:
    observations = []
    for owner, name, forbidden in guards:
        installed = getattr(owner, name)
        if installed is not forbidden:
            raise AssertionError(f"CPython regex guard was removed: {name}")
        try:
            installed()
        except GuardSignal as error:
            observations.append(
                {
                    "module": owner.__name__,
                    "name": name,
                    "type": type(error).__name__,
                    "args": normalize(error.args),
                }
            )
        else:
            raise AssertionError(f"CPython regex guard did not fail closed: {name}")
    return observations


def evaluate_worker(role: str) -> dict[str, Any]:
    verify_runtime()
    cases = build_cases()
    if canonical(cases) != canonical(build_cases()):
        raise AssertionError("deep-contract fixture generation is nondeterministic")
    guards: list[tuple[Any, str, Any]] = []
    artifacts: list[dict[str, str]] = []
    if role in ("stdlib-a", "stdlib-b"):
        module = importlib.import_module("re")
        if "cpython-3.14.6" not in str(Path(module.__file__).resolve()):
            raise AssertionError("reference is not the pinned CPython standard library")
    elif role in ("candidate", "poison"):
        module = importlib.import_module("candidates.rust_candidate")
        artifacts = production_provenance(module)
        guards = install_regex_guards()
    else:
        raise AssertionError(f"unknown isolated deep-contract worker: {role}")
    if role == "poison":
        before = audit_regex_guards(guards)
        native = {
            "search": match_snapshot(module.search("(?P<letter>a)", "a"), "a"),
            "sub": attempted(lambda: module.sub("a", "x", "aba")),
        }
        after = audit_regex_guards(guards)
        if before != after:
            raise AssertionError("native execution altered a CPython regex poison")
        return {
            "schema": SCHEMA,
            "role": role,
            "seed": SEED,
            "fixture_sha256": digest(cases),
            "checks": len(cases),
            "guards": before,
            "guard_count": len(before),
            "native_under_poison": native,
            "native_artifacts": artifacts,
        }

    observations = []
    diagnostics = []
    counts: collections.Counter[str] = collections.Counter()
    for item in cases:
        family = item["family"]
        dispatch_family = family.removeprefix("seeded/")
        handler = DISPATCH.get(dispatch_family)
        if handler is None:
            raise AssertionError(f"unhandled deep-contract case family: {family}")
        observation, diagnostic = handler(module, item)
        normalized = normalize(observation)
        observations.append(
            {
                "id": item["id"],
                "family": family,
                "sha256": digest(normalized),
                "observation": normalized,
            }
        )
        if diagnostic:
            diagnostics.append(
                {
                    "id": item["id"],
                    "family": family,
                    "classification": (
                        "recorded implementation-private GC topology; "
                        "not asserted as documented public equality"
                    ),
                    "diagnostic": normalize(diagnostic),
                }
            )
        counts[family] += 1
    guard_observations = audit_regex_guards(guards) if guards else []
    if guards:
        if len(guard_observations) != 13:
            raise AssertionError("a production regex-poison guard disappeared")
        artifacts = production_provenance(module)
    return {
        "schema": SCHEMA,
        "role": role,
        "python": "3.14.6",
        "seed": SEED,
        "checks": len(observations),
        "fixture_sha256": digest(cases),
        "family_counts": dict(sorted(counts.items())),
        "observations": observations,
        "observation_sha256": digest(observations),
        "implementation_private_gc_diagnostics": diagnostics,
        "guard_count": len(guard_observations),
        "guard_observations": guard_observations,
        "native_artifacts": artifacts,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def run_worker(role: str) -> dict[str, Any]:
    verify_runtime()
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPATH"] = str(ROOT)
    command = [str(PINNED_EXECUTABLE), "-B", str(SCRIPT), "--worker", role]
    result = subprocess.run(
        command,
        cwd=str(ROOT),
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(
            f"isolated {role} worker failed with exit {result.returncode}: "
            f"{result.stderr[-10000:]} {result.stdout[-4000:]}"
        )
    try:
        report = json.loads(result.stdout)
    except (TypeError, ValueError) as error:
        raise AssertionError(f"isolated {role} worker returned invalid JSON") from error
    if report.get("schema") != SCHEMA or report.get("role") != role:
        raise AssertionError(f"isolated {role} worker has invalid provenance")
    if report.get("seed") != SEED or report.get("checks") != len(build_cases()):
        raise AssertionError(f"isolated {role} worker changed the seed or denominator")
    if report.get("fixture_sha256") != digest(build_cases()):
        raise AssertionError(f"isolated {role} worker changed the frozen fixture")
    if role == "poison":
        if report.get("guard_count") != 13:
            raise AssertionError("isolated poison self-test did not audit all guards")
        return report
    rows = report.get("observations")
    if not isinstance(rows, list) or digest(rows) != report.get("observation_sha256"):
        raise AssertionError(f"isolated {role} observations fail integrity checking")
    if len(rows) != len(build_cases()):
        raise AssertionError(f"isolated {role} observations changed the denominator")
    for row in rows:
        if row.get("sha256") != digest(row.get("observation")):
            raise AssertionError(f"isolated {role} produced an invalid case digest")
    return report


def mismatches(expected: list[Any], actual: list[Any]) -> list[dict[str, Any]]:
    left = {row["id"]: row for row in expected}
    right = {row["id"]: row for row in actual}
    result = []
    for identity in sorted(set(left) | set(right)):
        reference = left.get(identity)
        candidate = right.get(identity)
        if reference is None or candidate is None:
            result.append(
                {"id": identity, "expected": reference, "actual": candidate}
            )
        elif reference["observation"] != candidate["observation"]:
            result.append(
                {
                    "id": identity,
                    "family": reference["family"],
                    "expected": reference["observation"],
                    "actual": candidate["observation"],
                    "expected_sha256": reference["sha256"],
                    "actual_sha256": candidate["sha256"],
                }
            )
    return result


def diagnostic_differences(reference: list[Any], candidate: list[Any]) -> list[Any]:
    expected = {item["id"]: item for item in reference}
    actual = {item["id"]: item for item in candidate}
    result = []
    for identity in sorted(set(expected) | set(actual)):
        left = expected.get(identity)
        right = actual.get(identity)
        if left != right:
            result.append(
                {
                    "id": identity,
                    "classification": "implementation-private-gc-referent-topology",
                    "counted_as_public_contract": False,
                    "reference": left,
                    "candidate": right,
                }
            )
    return result


def verify_differential_self_test() -> dict[str, Any]:
    baseline = [
        {
            "id": "self-test/control",
            "family": "self-test",
            "sha256": digest({"value": 1}),
            "observation": {"value": 1},
        }
    ]
    poisoned = [
        {
            "id": "self-test/control",
            "family": "self-test",
            "sha256": digest({"value": 2}),
            "observation": {"value": 2},
        }
    ]
    missing = []
    if mismatches(baseline, baseline):
        raise AssertionError("differential self-test rejected an identical reference")
    changed = mismatches(baseline, poisoned)
    absent = mismatches(baseline, missing)
    if len(changed) != 1 or len(absent) != 1:
        raise AssertionError("differential self-test failed to detect poisoned data")
    return {
        "identical_reference": "PASS",
        "changed_observation_poison": "PASS",
        "missing_observation_poison": "PASS",
    }


def self_test() -> dict[str, Any]:
    verify_runtime()
    reference_a = run_worker("stdlib-a")
    reference_b = run_worker("stdlib-b")
    reference_failures = mismatches(
        reference_a["observations"], reference_b["observations"]
    )
    if reference_failures:
        raise AssertionError(
            "pinned standard-library references are nondeterministic: "
            + canonical(reference_failures[:3]).decode("ascii")
        )
    poison = run_worker("poison")
    differential = verify_differential_self_test()
    return {
        "schema": SCHEMA,
        "status": "PASS",
        "mode": "self-test",
        "python": "3.14.6",
        "seed": SEED,
        "checks": reference_a["checks"],
        "fixture_sha256": reference_a["fixture_sha256"],
        "reference_a_sha256": reference_a["observation_sha256"],
        "reference_b_sha256": reference_b["observation_sha256"],
        "stdlib_vs_stdlib_mismatches": 0,
        "differential_poison_self_tests": differential,
        "forbidden_regex_guards": poison["guard_count"],
        "native_under_poison": poison["native_under_poison"],
        "native_artifacts": poison["native_artifacts"],
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def write_evidence(report: dict[str, Any]) -> str:
    if EVIDENCE != ROOT / "candidates/audits/RUST-V8-DEEP-CONTRACT.json.gz":
        raise AssertionError("deep-contract evidence escaped its authorized path")
    if not EVIDENCE.parent.is_dir():
        raise AssertionError("the authorized candidates/audits directory is absent")
    payload = canonical(report)
    with EVIDENCE.open("wb") as raw:
        with gzip.GzipFile(
            filename="",
            fileobj=raw,
            mode="wb",
            compresslevel=9,
            mtime=0,
        ) as compressed:
            compressed.write(payload)
    raw = EVIDENCE.read_bytes()
    if len(raw) < 10 or raw[:2] != b"\x1f\x8b":
        raise AssertionError("deep-contract evidence is not a gzip archive")
    if raw[3] & 0x08 or raw[4:8] != b"\x00\x00\x00\x00":
        raise AssertionError("deep-contract gzip metadata is nondeterministic")
    if gzip.decompress(raw) != payload:
        raise AssertionError("deep-contract evidence failed its round-trip check")
    return hashlib.sha256(raw).hexdigest()


def candidate_gate() -> tuple[dict[str, Any], int]:
    verify_runtime()
    reference_a = run_worker("stdlib-a")
    reference_b = run_worker("stdlib-b")
    reference_failures = mismatches(
        reference_a["observations"], reference_b["observations"]
    )
    if reference_failures:
        raise AssertionError(
            "candidate gate refused a nondeterministic pinned reference: "
            + canonical(reference_failures[:3]).decode("ascii")
        )
    poison = run_worker("poison")
    differential = verify_differential_self_test()
    candidate = run_worker("candidate")
    failures = mismatches(reference_a["observations"], candidate["observations"])
    topology = diagnostic_differences(
        reference_a["implementation_private_gc_diagnostics"],
        candidate["implementation_private_gc_diagnostics"],
    )
    failure_counts = collections.Counter(item.get("family", "missing") for item in failures)
    report = {
        "schema": SCHEMA,
        "status": "FAIL" if failures else "PASS",
        "python": "3.14.6",
        "seed": SEED,
        "seeded_case_count": SEEDED_CASES,
        "checks": reference_a["checks"],
        "fixture_sha256": reference_a["fixture_sha256"],
        "suite_path": "tools/rust_v8_deep_contract_oracle.py",
        "suite_sha256": file_digest(SCRIPT),
        "reference_a_sha256": reference_a["observation_sha256"],
        "reference_b_sha256": reference_b["observation_sha256"],
        "candidate_sha256": candidate["observation_sha256"],
        "stdlib_vs_stdlib_mismatches": reference_failures,
        "public_mismatch_count": len(failures),
        "public_mismatch_family_counts": dict(sorted(failure_counts.items())),
        "public_mismatches": failures,
        "implementation_private_gc_topology_difference_count": len(topology),
        "implementation_private_gc_topology_differences": topology,
        "implementation_private_gc_topology_policy": (
            "fully recorded and separately compared; explicitly not represented "
            "as documented public lifetime or collectability equality"
        ),
        "differential_poison_self_tests": differential,
        "forbidden_regex_guards": poison["guard_count"],
        "guard_observations": candidate["guard_observations"],
        "native_under_poison": poison["native_under_poison"],
        "native_artifacts": candidate["native_artifacts"],
        "reference": reference_a,
        "reference_independent_repeat": reference_b,
        "candidate": candidate,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    summary = {
        key: report[key]
        for key in (
            "schema", "status", "python", "seed", "seeded_case_count", "checks",
            "fixture_sha256", "suite_sha256", "reference_a_sha256",
            "reference_b_sha256", "candidate_sha256", "public_mismatch_count",
            "public_mismatch_family_counts",
            "implementation_private_gc_topology_difference_count",
            "forbidden_regex_guards", "native_artifacts", "performance", "holdout",
        )
    }
    summary["stdlib_vs_stdlib_mismatches"] = len(reference_failures)
    summary["differential_poison_self_tests"] = differential
    summary["evidence_path"] = "candidates/audits/RUST-V8-DEEP-CONTRACT.json.gz"
    summary["evidence_sha256"] = write_evidence(report)
    if failures:
        summary["first_public_mismatches"] = failures[:8]
        return summary, 1
    return summary, 0


def main(arguments: list[str]) -> int:
    if arguments == ["--self-test"]:
        print(canonical(self_test()).decode("ascii"))
        return 0
    if arguments in (["--gate"], ["--candidate-gate"]):
        report, status = candidate_gate()
        print(canonical(report).decode("ascii"))
        return status
    if len(arguments) == 2 and arguments[0] == "--worker":
        print(canonical(evaluate_worker(arguments[1])).decode("ascii"))
        return 0
    raise SystemExit(
        "usage: rust_v8_deep_contract_oracle.py "
        "--self-test | --gate | --worker ROLE"
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
