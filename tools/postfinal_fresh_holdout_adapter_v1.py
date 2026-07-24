#!/usr/bin/env python3
"""A source-bound, four-channel adapter for the unopened fresh holdout.

Importing this module, or running ``--self-test``, never opens a holdout,
starts a process, draws entropy, reads an evidence file, or imports a candidate.
The future holdout controller must explicitly supply already verified public
provenance before asking this adapter to start an isolated worker.
"""

from __future__ import annotations

import argparse
from array import array
import base64
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import subprocess
import sys
from typing import Any, Mapping


ADAPTER_SCHEMA = "rebar-postfinal-fresh-holdout-adapter-v1"
AUDIT_SCHEMA = "rebar-postfinal-fresh-holdout-adapter-audit-v1"
CASE_SCHEMA = "rebar-postfinal-fresh-holdout-v1-case"
WORKER_MODE = "fresh_holdout_v1"
CHANNELS = (
    "compiled-pattern-metadata",
    "return-values-match-spans-and-buffer-representation",
    "exception-class-arguments-and-public-pattern-error-fields",
    "documented-converter-callback-warning-and-scanner-traces",
)
FAMILIES = ("re", "rust", "vm", "zig")
CANDIDATE_FAMILIES = FAMILIES[1:]
TRIALS = 19
BOOTSTRAP_DRAWS = 2_000
CASES = 65_536
MAX_PATTERN_BYTES = 512
MAX_SUBJECT_BYTES = 4_096
MAX_MATCHES = 64
MAX_OPERATIONS = 1_024
MAX_WARMUPS = 64
MAX_FRAME_BYTES = 256 * 1_024
MAX_ERROR_DEPTH = 4
MAX_NORMALIZATION_DEPTH = 16
LANE_DOMAIN = b"rebar/fresh-holdout/v1/observable-lane\x00"
BOOTSTRAP_DOMAIN = b"rebar/fresh-holdout/v1/bootstrap\x00"
PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
ROOT = Path(__file__).resolve().parent.parent
GUARDED_AUDIT_SOURCE = ROOT / "tools" / "postfinal_no_delegation_audit_v1.py"
GUARDED_AUDIT_SOURCE_SHA256 = (
    "e505e17f4849242d990ee8e184794962327335d807000d1a8a0e65a0cb10c0ed"
)

REQUEST_MAGIC = b"RBHBOOT1"
RESPONSE_MAGIC = b"RBHRES01"
BOOTSTRAP_VERSION = 1
CASE_BOOTSTRAP = 1
AGGREGATE_BOOTSTRAP = 2
BOOTSTRAP_HEADER = struct.Struct("<8sHHIII32sQ")
BOOTSTRAP_RESPONSE = struct.Struct("<8sHHIII32sQddd")
BOOTSTRAP_CASE_PAYLOAD = struct.Struct("<38Q")
BOOTSTRAP_AGGREGATE_PAYLOAD = struct.Struct("<19d")
AGGREGATE_CASE_INDEX = (1 << 64) - 1

CASE_FIELDS = frozenset(
    {
        "schema",
        "id",
        "family",
        "family_index",
        "stratum",
        "variant",
        "pattern",
        "subject",
        "flags",
        "pos",
        "endpos",
        "lifecycle",
        "operation",
        "replacement",
        "maxsplit",
        "replacement_count",
        "max_matches",
    }
)


class HoldoutAdapterError(RuntimeError):
    """A prospective adapter, private frame, or public snapshot was unsafe."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise HoldoutAdapterError(message)


def canonical(value: Any) -> bytes:
    """Canonical ASCII JSON preserves even lone Python Unicode surrogates."""

    try:
        return json.dumps(
            value,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    except (OverflowError, TypeError, UnicodeError, ValueError) as error:
        raise HoldoutAdapterError("a private observable has no canonical ASCII representation") from error


def normalize(value: Any, depth: int = 0) -> Any:
    """Independently encode only documented, bounded Python regex surfaces."""

    require(depth <= MAX_NORMALIZATION_DEPTH, "observable nesting exceeds its safe bound")
    if value is None or isinstance(value, (bool, int)):
        return value
    if isinstance(value, float):
        require(math.isfinite(value), "a nonfinite public observable was rejected")
        return value
    if isinstance(value, str):
        if type(value) is str:
            return value
        return {"kind": type(value).__name__, "text": str(value)}
    if isinstance(value, (bytes, bytearray)):
        return {"kind": type(value).__name__, "hex": bytes(value).hex()}
    if isinstance(value, memoryview):
        try:
            return {
                "kind": "memoryview",
                "hex": value.tobytes().hex(),
                "format": value.format,
                "shape": normalize(value.shape, depth + 1),
                "strides": normalize(value.strides, depth + 1),
                "readonly": value.readonly,
                "c_contiguous": value.c_contiguous,
            }
        except ValueError:
            return {"kind": "memoryview", "released": True}
    if isinstance(value, tuple):
        return {"tuple": [normalize(item, depth + 1) for item in value]}
    if isinstance(value, list):
        require(len(value) <= 4 * MAX_MATCHES, "a public result list exceeded its safe bound")
        return [normalize(item, depth + 1) for item in value]
    if isinstance(value, Mapping):
        require(len(value) <= 4 * MAX_MATCHES, "a public result mapping exceeded its safe bound")
        result: dict[str, Any] = {}
        for key, item in sorted(value.items(), key=lambda pair: str(pair[0])):
            text = str(key)
            require(text not in result, "canonicalization would merge distinct public keys")
            result[text] = normalize(item, depth + 1)
        return result
    raise HoldoutAdapterError(
        f"the public observable has an unsupported type: {type(value).__name__}"
    )


def lane_digests(channels: Mapping[str, Any]) -> dict[str, str]:
    """Hash four distinct labeled snapshots; never repeat one shared digest."""

    require(isinstance(channels, Mapping), "observable channels must be a mapping")
    require(set(channels) == set(CHANNELS), "the four independently named channels changed")
    return {
        name: hashlib.sha256(
            LANE_DOMAIN + name.encode("ascii") + b"\x00" + canonical(channels[name])
        ).hexdigest()
        for name in CHANNELS
    }


def ensure_candidate_free() -> None:
    loaded = sorted(
        name
        for name in sys.modules
        if name.startswith("candidates.")
        and (
            name.endswith("_candidate")
            or name.rsplit(".", 1)[-1]
            in {"_vm_native", "_rust_bridge", "_zig_bridge"}
        )
    )
    require(not loaded, f"the fresh controller imported a candidate: {loaded!r}")


def _bounded_wire(value: Mapping[str, Any], *, pattern: bool = False) -> dict[str, str]:
    require(isinstance(value, Mapping), "a fresh private wire value is not a mapping")
    kind = value.get("kind")
    maximum = MAX_PATTERN_BYTES if pattern else MAX_SUBJECT_BYTES
    if kind == "str":
        require(set(value) == {"kind", "text"}, "a text wire contains an unexpected field")
        text = value.get("text")
        require(isinstance(text, str), "a text wire does not contain Python text")
        require(
            len(text.encode("utf-8", "surrogatepass")) <= maximum,
            "a private text wire exceeded its frozen bound",
        )
        return {"kind": "str", "text": text}
    require(kind in {"bytes", "bytearray", "memoryview"}, "unknown fresh buffer representation")
    require(set(value) == {"kind", "base64"}, "a bytes wire contains an unexpected field")
    encoded = value.get("base64")
    require(isinstance(encoded, str) and encoded.isascii(), "a private bytes wire is not ASCII")
    try:
        raw = base64.b64decode(encoded, validate=True)
    except (TypeError, ValueError) as error:
        raise HoldoutAdapterError("a private bytes wire is not valid base64") from error
    require(len(raw) <= maximum, "a private buffer exceeded its frozen bound")
    return {"kind": kind, "hex": raw.hex()}


def private_case_descriptor(case: Mapping[str, Any]) -> dict[str, Any]:
    """Transmit one fresh case, never a production key or baseline answer."""

    require(isinstance(case, Mapping), "the fresh case is not a mapping")
    require(set(case) == CASE_FIELDS, "the fresh case contains an absent or unapproved field")
    require(case.get("schema") == CASE_SCHEMA, "the fresh case has the wrong public schema")
    identifier = case.get("id")
    require(
        isinstance(identifier, str)
        and identifier.startswith("fresh.")
        and len(identifier.encode("utf-8", "surrogatepass")) <= 512,
        "the fresh case identifier is invalid",
    )
    stratum = case.get("stratum")
    require(isinstance(stratum, Mapping), "the fresh case stratum is not a mapping")
    require(
        set(stratum) == {"index", "input_domain", "flag_tier", "window", "lifecycle"},
        "the fresh case stratum changed its frozen fields",
    )
    family_index = case.get("family_index")
    variant = case.get("variant")
    require(
        type(family_index) is int and 0 <= family_index < 16,
        "the fresh case family index is invalid",
    )
    require(type(variant) is int and 0 <= variant < 256, "the fresh case variant is invalid")
    require(
        type(stratum.get("index")) is int and 0 <= stratum["index"] < 16,
        "the fresh case stratum index is invalid",
    )
    lifecycle = case.get("lifecycle")
    require(
        lifecycle in {"module", "compiled"} and stratum.get("lifecycle") == lifecycle,
        "the fresh case lifecycle is inconsistent",
    )
    operation = case.get("operation")
    require(
        operation in {
            "search", "match", "fullmatch", "findall", "finditer", "scanner",
            "split", "sub", "subn",
        }
        and (operation != "scanner" or lifecycle == "compiled"),
        "the fresh case selected an unsupported public operation",
    )
    for field, maximum in (("maxsplit", 4), ("replacement_count", 4)):
        require(type(case.get(field)) is int and 0 <= case[field] <= maximum, f"invalid {field}")
    require(case.get("max_matches") == MAX_MATCHES, "the bounded fresh match limit changed")
    for field in ("pos", "endpos"):
        item = case.get(field)
        require(item is None or type(item) is int, f"the fresh {field} is not a Python integer")
    flags = case.get("flags")
    require(type(flags) is int and 0 <= flags <= 511, "the fresh public flags are invalid")
    family_name = case.get("family")
    require(isinstance(family_name, str) and 0 < len(family_name) <= 64, "invalid family name")
    descriptor: dict[str, Any] = {
        "schema": CASE_SCHEMA,
        "id": identifier,
        "family": family_name,
        "family_index": family_index,
        "stratum": normalize(dict(stratum)),
        "variant": variant,
        "pattern": _bounded_wire(case["pattern"], pattern=True),
        "subject": _bounded_wire(case["subject"]),
        "flags": flags,
        "pos": case["pos"],
        "endpos": case["endpos"],
        "lifecycle": lifecycle,
        "operation": operation,
        "replacement": _bounded_wire(case["replacement"]),
        "maxsplit": case["maxsplit"],
        "replacement_count": case["replacement_count"],
        "max_matches": MAX_MATCHES,
    }
    require(len(canonical(descriptor)) < MAX_FRAME_BYTES, "the bounded fresh case frame is oversized")
    return descriptor


# Inserted inside the original, independently audited worker after all of its
# import, native-loader, registry, subprocess, and evidence guards are active.
# This literal never imports the stdlib regex or any other regex implementation.
WORKER_EXTENSION = r'''
FRESH_ADAPTER_SCHEMA = "rebar-postfinal-fresh-holdout-adapter-v1"
FRESH_CASE_SCHEMA = "rebar-postfinal-fresh-holdout-v1-case"
FRESH_CHANNELS = (
    "compiled-pattern-metadata",
    "return-values-match-spans-and-buffer-representation",
    "exception-class-arguments-and-public-pattern-error-fields",
    "documented-converter-callback-warning-and-scanner-traces",
)
FRESH_LANE_DOMAIN = b"rebar/fresh-holdout/v1/observable-lane\x00"
FRESH_MAX_MATCHES = 64
FRESH_MAX_DEPTH = 16
fresh_prepared = None


def fresh_require(condition, message):
    if not condition:
        raise RuntimeError("fresh four-channel worker: " + message)


def fresh_canonical(value):
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def fresh_normalize(value, depth=0):
    fresh_require(depth <= FRESH_MAX_DEPTH, "observable nesting exceeded its bound")
    if value is None or isinstance(value, (bool, int)):
        return value
    if isinstance(value, str):
        if type(value) is str:
            return value
        return {"kind": type(value).__name__, "text": str(value)}
    if isinstance(value, (bytes, bytearray)):
        return {"kind": type(value).__name__, "hex": bytes(value).hex()}
    if isinstance(value, memoryview):
        try:
            return {
                "kind": "memoryview",
                "hex": value.tobytes().hex(),
                "format": value.format,
                "shape": fresh_normalize(value.shape, depth + 1),
                "strides": fresh_normalize(value.strides, depth + 1),
                "readonly": value.readonly,
                "c_contiguous": value.c_contiguous,
            }
        except ValueError:
            return {"kind": "memoryview", "released": True}
    if isinstance(value, tuple):
        return {"tuple": [fresh_normalize(item, depth + 1) for item in value]}
    if isinstance(value, list):
        fresh_require(len(value) <= 4 * FRESH_MAX_MATCHES, "result list exceeded its bound")
        return [fresh_normalize(item, depth + 1) for item in value]
    if isinstance(value, dict):
        fresh_require(len(value) <= 4 * FRESH_MAX_MATCHES, "result map exceeded its bound")
        result = {}
        for key, item in sorted(value.items(), key=lambda pair: str(pair[0])):
            text = str(key)
            fresh_require(text not in result, "distinct public keys collide")
            result[text] = fresh_normalize(item, depth + 1)
        return result
    raise RuntimeError("unsupported fresh observable: " + type(value).__name__)


def fresh_error(error, depth=0):
    fresh_require(depth <= 4, "public exception chain exceeded its bound")
    result = {
        "class": type(error).__name__,
        "args": fresh_normalize(error.args),
        "notes": fresh_normalize(getattr(error, "__notes__", [])),
        "cause": fresh_error(error.__cause__, depth + 1) if error.__cause__ is not None else None,
        "context": fresh_error(error.__context__, depth + 1) if error.__context__ is not None else None,
        "suppress_context": bool(error.__suppress_context__),
    }
    if hasattr(error, "msg") and hasattr(error, "pos"):
        result["pattern_error"] = {
            key: fresh_normalize(getattr(error, key, None))
            for key in ("msg", "pattern", "pos", "lineno", "colno")
        }
    return result


def fresh_attempt(action):
    try:
        return {"status": "ok", "value": fresh_normalize(action())}
    except Exception as error:
        return {"status": "error", "error": fresh_error(error)}


def fresh_wire(value):
    fresh_require(isinstance(value, dict), "private wire is not an object")
    kind = value.get("kind")
    if kind == "str":
        fresh_require(set(value) == {"kind", "text"}, "invalid text wire fields")
        text = value.get("text")
        fresh_require(isinstance(text, str), "invalid private text")
        return text
    fresh_require(kind in {"bytes", "bytearray", "memoryview"}, "unknown buffer wire")
    fresh_require(set(value) == {"kind", "hex"}, "invalid bytes wire fields")
    encoded = value.get("hex")
    fresh_require(isinstance(encoded, str) and len(encoded) <= 8192, "oversized bytes wire")
    try:
        payload = bytes.fromhex(encoded)
    except ValueError as error:
        raise RuntimeError("invalid hexadecimal fresh wire") from error
    fresh_require(payload.hex() == encoded, "noncanonical hexadecimal fresh wire")
    if kind == "bytearray":
        return bytearray(payload)
    if kind == "memoryview":
        return memoryview(payload)
    return payload


def fresh_pattern_surface(compiled):
    return {
        "pattern": fresh_normalize(compiled.pattern),
        "flags": int(compiled.flags),
        "groups": compiled.groups,
        "groupindex": fresh_normalize(dict(compiled.groupindex)),
    }


def fresh_match_surface(match, subject):
    if match is None:
        return None
    default = "!" if isinstance(match.string, str) else b"!"
    groups = []
    for index in range(match.re.groups + 1):
        groups.append({
            "index": index,
            "group": fresh_normalize(match.group(index)),
            "getitem": fresh_normalize(match[index]),
            "start": match.start(index),
            "end": match.end(index),
            "span": fresh_normalize(match.span(index)),
        })
    named = {}
    for name in sorted(match.re.groupindex):
        named[name] = {
            "group": fresh_normalize(match.group(name)),
            "getitem": fresh_normalize(match[name]),
            "start": match.start(name),
            "end": match.end(name),
            "span": fresh_normalize(match.span(name)),
        }
    return {
        "span": fresh_normalize(match.span()),
        "regs": fresh_normalize(match.regs),
        "regs_cached": match.regs is match.regs,
        "groups": fresh_normalize(match.groups()),
        "groups_default": fresh_normalize(match.groups(default)),
        "groupdict": fresh_normalize(match.groupdict()),
        "groupdict_default": fresh_normalize(match.groupdict(default)),
        "lastindex": match.lastindex,
        "lastgroup": match.lastgroup,
        "pos": match.pos,
        "endpos": match.endpos,
        "same_subject": match.string is subject,
        "string": fresh_normalize(match.string),
        "captures": groups,
        "named": named,
    }


def fresh_bounded_iterator(iterator, subject):
    result = []
    for _ in range(FRESH_MAX_MATCHES):
        item = next(iterator, None)
        if item is None:
            return {
                "matches": result,
                "iterator_is_self": iter(iterator) is iterator,
                "exhausted_once": next(iterator, None) is None,
                "exhausted_twice": next(iterator, None) is None,
            }
        result.append(fresh_match_surface(item, subject))
    raise RuntimeError("fresh iterator exceeded its fixed result bound")


def fresh_scanner_trace(compiled, subject, pos, endpos):
    if pos is None:
        scanner = compiled.scanner(subject)
    elif endpos is None:
        scanner = compiled.scanner(subject, pos)
    else:
        scanner = compiled.scanner(subject, pos, endpos)
    records = []
    for index in range(FRESH_MAX_MATCHES):
        method = "match" if index % 5 == 1 else "search"
        item = getattr(scanner, method)()
        records.append({"method": method, "match": fresh_match_surface(item, subject)})
        if item is None:
            records.append({"method": method, "match": fresh_match_surface(getattr(scanner, method)(), subject)})
            records.append({"method": "search", "match": fresh_match_surface(scanner.search(), subject)})
            return records
    raise RuntimeError("fresh scanner exceeded its fixed result bound")


class FreshIndex:
    def __init__(self, events, value, fail=False):
        self.events = events
        self.value = value
        self.fail = fail

    def __index__(self):
        self.events.append({"event": "__index__", "value": self.value, "fail": self.fail})
        if self.fail:
            raise ValueError("fresh public index sentinel")
        return self.value


def fresh_action(module, compiled, case, subject, replacement):
    operation = case["operation"]
    flags = case["flags"]
    pos = case["pos"]
    endpos = case["endpos"]
    lifecycle = case["lifecycle"]
    pattern = compiled.pattern
    if lifecycle == "compiled":
        if operation in {"search", "match", "fullmatch", "findall", "finditer"}:
            method = getattr(compiled, operation)
            if operation == "finditer":
                if pos is None:
                    return lambda: fresh_bounded_iterator(method(subject), subject)
                if endpos is None:
                    return lambda: fresh_bounded_iterator(method(subject, pos), subject)
                return lambda: fresh_bounded_iterator(method(subject, pos, endpos), subject)
            if pos is None:
                return lambda: method(subject)
            if endpos is None:
                return lambda: method(subject, pos)
            return lambda: method(subject, pos, endpos)
        if operation == "scanner":
            return lambda: fresh_scanner_trace(compiled, subject, pos, endpos)
        if operation == "split":
            return lambda: compiled.split(subject, maxsplit=case["maxsplit"])
        if operation in {"sub", "subn"}:
            method = getattr(compiled, operation)
            return lambda: method(replacement, subject, count=case["replacement_count"])
    else:
        if operation in {"search", "match", "fullmatch", "findall", "finditer"}:
            method = getattr(module, operation)
            if operation == "finditer":
                return lambda: fresh_bounded_iterator(method(pattern, subject, flags), subject)
            return lambda: method(pattern, subject, flags)
        if operation == "split":
            return lambda: module.split(pattern, subject, maxsplit=case["maxsplit"], flags=flags)
        if operation in {"sub", "subn"}:
            method = getattr(module, operation)
            return lambda: method(
                pattern,
                replacement,
                subject,
                count=case["replacement_count"],
                flags=flags,
            )
    raise RuntimeError("unsupported fresh public operation")


def fresh_result(action, case, subject):
    def observed():
        result = action()
        operation = case["operation"]
        if operation in {"search", "match", "fullmatch"}:
            return fresh_match_surface(result, subject)
        return result
    return fresh_attempt(observed)


def fresh_traces(module, compiled, case, subject):
    events = []
    pos = case["pos"] if case["pos"] is not None else 0
    index = FreshIndex(events, pos, fail=bool(case["variant"] % 7 == 0))
    indexed = fresh_attempt(lambda: fresh_match_surface(compiled.search(subject, index), subject))

    callback_events = []
    def replacement(match):
        callback_events.append({
            "event": "replacement",
            "index": len(callback_events),
            "match": fresh_match_surface(match, subject),
        })
        return match.group(0)
    callback = fresh_attempt(lambda: compiled.subn(replacement, subject, count=2))

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        warning_result = fresh_attempt(
            lambda: module.split(compiled.pattern, subject, 1, case["flags"])
        )
        warning_events = [
            {"category": item.category.__name__, "message": str(item.message)}
            for item in caught
        ]

    scanner = fresh_attempt(
        lambda: fresh_scanner_trace(compiled, subject, case["pos"], case["endpos"])
    )
    return {
        "converter": {"result": indexed, "events": fresh_normalize(events)},
        "callback": {"result": callback, "events": fresh_normalize(callback_events)},
        "warnings": {"result": warning_result, "events": fresh_normalize(warning_events)},
        "scanner": scanner,
    }


def fresh_channel_snapshots(module, prepared_case):
    case, pattern, subject, replacement, compiled, action = prepared_case
    metadata = fresh_attempt(lambda: fresh_pattern_surface(compiled))
    values = fresh_result(action, case, subject)
    exception = {
        "compile": metadata.get("error") if metadata["status"] == "error" else None,
        "operation": values.get("error") if values["status"] == "error" else None,
    }
    traces = fresh_traces(module, compiled, case, subject)
    return {
        FRESH_CHANNELS[0]: metadata,
        FRESH_CHANNELS[1]: values,
        FRESH_CHANNELS[2]: exception,
        FRESH_CHANNELS[3]: traces,
    }


def fresh_channel_digests(channels):
    fresh_require(isinstance(channels, dict) and set(channels) == set(FRESH_CHANNELS), "four distinct public channels are required")
    return {
        name: hashlib.sha256(
            FRESH_LANE_DOMAIN + name.encode("ascii") + b"\x00" + fresh_canonical(channels[name])
        ).hexdigest()
        for name in FRESH_CHANNELS
    }


def fresh_prepare(candidate, request):
    global fresh_prepared
    fresh_require(mode == "fresh_holdout_v1", "fresh case reached a non-holdout worker")
    before = verify_runtime()
    case = request.get("case")
    fresh_require(isinstance(case, dict), "fresh private case is not an object")
    fresh_require(case.get("schema") == FRESH_CASE_SCHEMA, "fresh private case schema changed")
    fresh_require(isinstance(case.get("id"), str) and case["id"].startswith("fresh."), "fresh private case identifier changed")
    fresh_require(case.get("max_matches") == FRESH_MAX_MATCHES, "fresh match bound changed")
    pattern = fresh_wire(case["pattern"])
    subject = fresh_wire(case["subject"])
    replacement = fresh_wire(case["replacement"])
    fresh_require(isinstance(pattern, (str, bytes)), "fresh pattern domain is invalid")
    compiled = candidate.compile(pattern, case["flags"])
    action = fresh_action(candidate, compiled, case, subject, replacement)
    fresh_require(callable(action), "fresh action is not callable")
    fresh_prepared = (case, pattern, subject, replacement, compiled, action)
    return {
        "op": "fresh_prepare",
        "passed": True,
        "family": family,
        "module": module_name,
        "case": case["id"],
        "guard_persistent": True,
        "registry_provenance": before["registry_provenance"],
        "native_mapping_provenance": before["native_mapping_provenance"],
    }


def fresh_snapshot(candidate, request, reveal=False):
    fresh_require(mode == "fresh_holdout_v1" and fresh_prepared is not None, "no guarded fresh case is prepared")
    case = fresh_prepared[0]
    fresh_require(request.get("case") == case["id"], "fresh snapshot case was substituted")
    registry = verify_registry()
    channels = fresh_channel_snapshots(candidate, fresh_prepared)
    result = {
        "op": "fresh_reveal" if reveal else "fresh_snapshot",
        "passed": True,
        "family": family,
        "module": module_name,
        "case": case["id"],
        "channel_digests": fresh_channel_digests(channels),
        "channel_count": len(FRESH_CHANNELS),
        "guard_persistent": True,
        "registry_provenance": registry,
    }
    if reveal:
        result["channels"] = channels
    return result


def fresh_proc_memory():
    rss = None
    high = None
    with open("/proc/self/status", "r", encoding="utf-8") as stream:
        data = stream.read(256 * 1024 + 1)
    fresh_require(len(data) <= 256 * 1024, "process memory status exceeds its bound")
    for line in data.splitlines():
        if line.startswith("VmRSS:"):
            rss = int(line.split()[1])
        elif line.startswith("VmHWM:"):
            high = int(line.split()[1])
    fresh_require(isinstance(rss, int) and rss >= 0, "worker RSS is unavailable")
    fresh_require(isinstance(high, int) and high >= 0, "worker RSS high-water is unavailable")
    return {"rss_kb": rss, "hwm_kb": high}


def fresh_observe(candidate, request):
    fresh_require(mode == "fresh_holdout_v1" and fresh_prepared is not None, "no guarded fresh observation is prepared")
    case, _pattern, subject, _replacement, _compiled, action = fresh_prepared
    fresh_require(request.get("case") == case["id"], "fresh observation case was substituted")
    operations = request.get("operations")
    warmups = request.get("warmups")
    trial = request.get("trial")
    fresh_require(type(operations) is int and 1 <= operations <= 1024, "invalid fresh operation bound")
    fresh_require(type(warmups) is int and 0 <= warmups <= 64, "invalid fresh warmup bound")
    fresh_require(type(trial) is int and 0 <= trial < 19, "invalid fresh paired trial")
    verify_registry()
    for _ in range(warmups):
        action()
    tracemalloc.start()
    try:
        sample = action()
        _current, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    if case["operation"] in {"search", "match", "fullmatch"}:
        fresh_match_surface(sample, subject)
    before = fresh_proc_memory()
    was_enabled = gc.isenabled()
    if was_enabled:
        gc.disable()
    try:
        started = time.perf_counter_ns()
        for _ in range(operations):
            action()
        elapsed = time.perf_counter_ns() - started
    finally:
        if was_enabled:
            gc.enable()
    fresh_require(type(elapsed) is int and 0 < elapsed < (1 << 64), "invalid fresh elapsed interval")
    after = fresh_proc_memory()
    channels = fresh_channel_snapshots(candidate, fresh_prepared)
    registry = verify_registry()
    return {
        "op": "fresh_observe",
        "passed": True,
        "family": family,
        "module": module_name,
        "case": case["id"],
        "trial": trial,
        "operations": operations,
        "warmups": warmups,
        "elapsed_ns": elapsed,
        "ns_per_op": elapsed / operations,
        "peak_traced_bytes": peak,
        "rss_before_kb": before["rss_kb"],
        "rss_after_kb": after["rss_kb"],
        "hwm_kb": after["hwm_kb"],
        "channel_digests": fresh_channel_digests(channels),
        "channel_count": len(FRESH_CHANNELS),
        "guard_persistent": True,
        "registry_provenance": registry,
    }
'''

MODE_ANCHOR = 'if mode not in {"smoke", "persistent"}:'
PREPARE_ANCHOR = "prepared = None\n\n\ndef prepare_case"
DISPATCH_ANCHOR = '            elif operation == "quit":'
MODE_REPLACEMENT = 'if mode not in {"smoke", "persistent", "fresh_holdout_v1"}:'
DISPATCH_EXTENSION = '''            elif operation == "fresh_prepare":
                result = fresh_prepare(candidate, request)
            elif operation == "fresh_snapshot":
                result = fresh_snapshot(candidate, request)
            elif operation == "fresh_observe":
                result = fresh_observe(candidate, request)
            elif operation == "fresh_reveal":
                result = fresh_snapshot(candidate, request, reveal=True)
'''


def derive_guarded_worker_source(base_source: str) -> tuple[str, dict[str, Any]]:
    """Add exactly three reviewable sites to the immutable original guard."""

    require(isinstance(base_source, str), "the original guarded worker is not source text")
    require(0 < len(base_source.encode("utf-8")) <= 16 * 1024 * 1024, "unsafe guard source size")
    anchors = (
        ("frozen-worker-mode", MODE_ANCHOR),
        ("guarded-fresh-functions", PREPARE_ANCHOR),
        ("guarded-fresh-dispatch", DISPATCH_ANCHOR),
    )
    for name, anchor in anchors:
        require(base_source.count(anchor) == 1, f"immutable guarded worker anchor is not unique: {name}")
    require(
        WORKER_MODE not in base_source and "fresh_channel_snapshots" not in base_source,
        "the immutable guard was already extended or substituted",
    )
    source = base_source.replace(MODE_ANCHOR, MODE_REPLACEMENT, 1)
    source = source.replace(
        PREPARE_ANCHOR,
        "prepared = None\n" + WORKER_EXTENSION + "\n\ndef prepare_case",
        1,
    )
    source = source.replace(DISPATCH_ANCHOR, DISPATCH_EXTENSION + DISPATCH_ANCHOR, 1)
    for name, marker in (
        ("fresh-worker-mode", MODE_REPLACEMENT),
        ("fresh-worker-source", WORKER_EXTENSION),
        ("fresh-worker-dispatch", DISPATCH_EXTENSION),
    ):
        require(source.count(marker) == 1, f"the guarded fresh insertion is not unique: {name}")
    restored = source.replace(DISPATCH_EXTENSION + DISPATCH_ANCHOR, DISPATCH_ANCHOR, 1)
    restored = restored.replace(
        "prepared = None\n" + WORKER_EXTENSION + "\n\ndef prepare_case",
        PREPARE_ANCHOR,
        1,
    )
    restored = restored.replace(MODE_REPLACEMENT, MODE_ANCHOR, 1)
    require(restored == base_source, "fresh worker derivation changed an original guard byte")
    manifest = {
        "schema": ADAPTER_SCHEMA + "-guarded-source",
        "base_source_sha256": hashlib.sha256(base_source.encode("utf-8")).hexdigest(),
        "derived_source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "extension_sha256": hashlib.sha256(WORKER_EXTENSION.encode("utf-8")).hexdigest(),
        "mode": WORKER_MODE,
        "anchor_names": [name for name, _anchor in anchors],
        "anchor_counts": {name: 1 for name, _anchor in anchors},
        "unchanged_original_guard_restores_exactly": True,
        "channel_names": list(CHANNELS),
        "private_wire_format": "canonical-ascii-json-utf8",
        "descriptor_wire": "bounded-text-or-hex; no key or reference answer",
    }
    return source, manifest


def guarded_holdout_worker_command(
    audit_module: Any,
    family: str,
    native_fingerprints: Mapping[str, str],
) -> tuple[list[str], dict[str, Any]]:
    """Derive one exact pinned audited worker command without launching it."""

    ensure_candidate_free()
    require(family in FAMILIES, "an unapproved family requested a fresh worker")
    require(isinstance(native_fingerprints, Mapping), "missing frozen native fingerprints")
    raw_source_path = getattr(audit_module, "__file__", None)
    require(isinstance(raw_source_path, (str, os.PathLike)), "the frozen guard module has no public source")
    source_path = Path(raw_source_path)
    require(
        not source_path.is_symlink()
        and source_path.resolve() == GUARDED_AUDIT_SOURCE.resolve(),
        "the immutable original no-delegation guard source was substituted",
    )
    source_digest = hashlib.sha256()
    source_size = 0
    try:
        with source_path.open("rb") as source_stream:
            while block := source_stream.read(1024 * 1024):
                source_size += len(block)
                require(source_size <= 16 * 1024 * 1024, "the frozen original guard source exceeds its bound")
                source_digest.update(block)
    except OSError as error:
        raise HoldoutAdapterError("the frozen original guard source cannot be verified") from error
    require(
        source_digest.hexdigest() == GUARDED_AUDIT_SOURCE_SHA256,
        "the immutable original no-delegation guard source fingerprint changed",
    )
    make_command = getattr(audit_module, "guarded_worker_command", None)
    validate = getattr(audit_module, "validate_guarded_worker_response", None)
    base_source = getattr(audit_module, "GUARDED_WORKER_SOURCE", None)
    require(callable(make_command) and callable(validate), "the frozen audit does not expose its guarded protocol")
    require(isinstance(base_source, str), "the frozen audit does not expose its exact worker")
    base = make_command(family, native_fingerprints, persistent=True)
    require(
        isinstance(base, list)
        and len(base) == 10
        and all(isinstance(item, str) for item in base)
        and Path(base[0]).resolve() == PINNED_PYTHON.resolve()
        and base[1:4] == ["-I", "-B", "-c"]
        and base[4] == base_source
        and Path(base[5]).resolve() == ROOT.resolve()
        and base[6] == family
        and base[9] == "persistent",
        "the exact pinned original guarded-worker command was substituted",
    )
    try:
        hashes = json.loads(base[8])
    except (TypeError, ValueError) as error:
        raise HoldoutAdapterError("the guarded native fingerprint frame is invalid") from error
    require(isinstance(hashes, dict), "the guarded native fingerprint frame is not an object")
    source, evidence = derive_guarded_worker_source(base_source)
    evidence["audit_source_path"] = "tools/postfinal_no_delegation_audit_v1.py"
    evidence["audit_source_sha256"] = GUARDED_AUDIT_SOURCE_SHA256
    command = list(base)
    command[4] = source
    command[9] = WORKER_MODE
    require(command[:4] == base[:4] and command[5:9] == base[5:9], "fresh worker changed its audited process capabilities")
    return command, evidence


class PersistentFreshHoldoutWorker:
    """One future, separately guarded engine; no controller candidate import."""

    def __init__(
        self,
        audit_module: Any,
        family: str,
        native_fingerprints: Mapping[str, str],
    ) -> None:
        ensure_candidate_free()
        self.audit_module = audit_module
        self.family = family
        self.native_fingerprints = native_fingerprints
        command, self.source_provenance = guarded_holdout_worker_command(
            audit_module,
            family,
            native_fingerprints,
        )
        self.process = subprocess.Popen(
            command,
            cwd=ROOT,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="strict",
            bufsize=1,
        )
        try:
            ready = self._read_response()
            require(
                ready.get("op") == "ready"
                and ready.get("passed") is True
                and ready.get("family") == family,
                "the isolated fresh worker did not verify its audited startup",
            )
            self._validate_runtime(ready, force_hash=True)
        except BaseException:
            self.close()
            raise
        ensure_candidate_free()

    def _read_response(self) -> dict[str, Any]:
        require(self.process.stdout is not None, "the guarded fresh worker has no private output")
        try:
            encoded = self.process.stdout.readline(MAX_FRAME_BYTES + 1)
        except (OSError, UnicodeError) as error:
            raise HoldoutAdapterError("the guarded fresh worker response is unreadable") from error
        require(
            bool(encoded)
            and len(encoded.encode("utf-8")) <= MAX_FRAME_BYTES
            and encoded.endswith("\n"),
            "the guarded fresh worker response is not one bounded line",
        )
        try:
            value = json.loads(encoded)
        except (UnicodeError, ValueError) as error:
            raise HoldoutAdapterError("the guarded fresh worker returned invalid JSON") from error
        require(isinstance(value, dict), "the guarded fresh worker response is not an object")
        return value

    def _validate_runtime(self, response: Mapping[str, Any], *, force_hash: bool | None = None) -> None:
        validated = self.audit_module.validate_guarded_worker_response(
            self.family,
            response,
            self.native_fingerprints,
        )
        require(isinstance(validated, dict), "the frozen original audit rejected the fresh worker")
        if force_hash is not None:
            mapping = validated.get("native_mapping_provenance")
            require(
                isinstance(mapping, dict)
                and mapping.get("force_hash") is force_hash
                and mapping.get("digest_cache_key")
                == "device,inode,size,mtime_ns,ctime_ns",
                "fresh worker changed the actual native fingerprint policy",
            )
            if force_hash:
                entries = mapping.get("observed_owned_mappings")
                require(
                    isinstance(entries, list)
                    and all(
                        isinstance(entry, dict)
                        and entry.get("content_sha256_recomputed") is True
                        for entry in entries
                    ),
                    "fresh worker did not independently rehash its native mappings",
                )

    def request(self, value: Mapping[str, Any]) -> dict[str, Any]:
        ensure_candidate_free()
        require(self.process.poll() is None, "the guarded fresh worker exited")
        require(self.process.stdin is not None, "the guarded fresh worker lost its input")
        require(isinstance(value, Mapping), "the guarded fresh worker request is not an object")
        encoded = canonical(dict(value))
        require(len(encoded) < MAX_FRAME_BYTES, "the guarded fresh request exceeds its bound")
        try:
            self.process.stdin.write(encoded.decode("ascii") + "\n")
            self.process.stdin.flush()
        except (BrokenPipeError, OSError, UnicodeError) as error:
            raise HoldoutAdapterError("the guarded fresh worker rejected its private request") from error
        response = self._read_response()
        require(
            response.get("passed") is True
            and response.get("family") == self.family
            and response.get("op") == value.get("op"),
            "the guarded fresh worker returned a substituted or failing response",
        )
        self._validate_runtime(response)
        ensure_candidate_free()
        return response

    def verify(self, *, force_hash: bool = False) -> dict[str, Any]:
        require(type(force_hash) is bool, "the fresh force-hash request is not boolean")
        response = self.request({"op": "verify", "force_hash": force_hash})
        self._validate_runtime(response, force_hash=force_hash)
        return response

    def prepare(self, case: Mapping[str, Any]) -> dict[str, Any]:
        descriptor = private_case_descriptor(case)
        response = self.request({"op": "fresh_prepare", "case": descriptor})
        require(
            response.get("case") == descriptor["id"]
            and response.get("guard_persistent") is True,
            "fresh case preparation lost its isolated provenance",
        )
        return response

    def snapshot(self, case_id: str, *, reveal: bool = False) -> dict[str, Any]:
        require(type(reveal) is bool, "fresh reveal selector is not boolean")
        operation = "fresh_reveal" if reveal else "fresh_snapshot"
        response = self.request({"op": operation, "case": case_id})
        validate_channel_digests(response.get("channel_digests"))
        require(
            response.get("case") == case_id
            and response.get("channel_count") == len(CHANNELS),
            "fresh snapshot omitted a separately reconstructed public channel",
        )
        if reveal:
            channels = response.get("channels")
            require(lane_digests(channels) == response["channel_digests"], "revealed fresh channels do not match their independently labeled hashes")
        return response

    def observe(
        self,
        case_id: str,
        *,
        trial: int,
        operations: int,
        warmups: int,
    ) -> dict[str, Any]:
        require(type(trial) is int and 0 <= trial < TRIALS, "invalid fresh paired trial")
        require(type(operations) is int and 1 <= operations <= MAX_OPERATIONS, "invalid fresh operations")
        require(type(warmups) is int and 0 <= warmups <= MAX_WARMUPS, "invalid fresh warmups")
        response = self.request(
            {
                "op": "fresh_observe",
                "case": case_id,
                "trial": trial,
                "operations": operations,
                "warmups": warmups,
            }
        )
        validate_channel_digests(response.get("channel_digests"))
        elapsed = response.get("elapsed_ns")
        require(
            response.get("case") == case_id
            and response.get("trial") == trial
            and response.get("operations") == operations
            and response.get("warmups") == warmups
            and response.get("channel_count") == len(CHANNELS)
            and type(elapsed) is int
            and 0 < elapsed < 1 << 64
            and response.get("ns_per_op") == elapsed / operations,
            "the guarded fresh observation changed its fixed timing denominator",
        )
        for key in ("peak_traced_bytes", "rss_before_kb", "rss_after_kb", "hwm_kb"):
            require(type(response.get(key)) is int and response[key] >= 0, f"invalid fresh process-memory observation: {key}")
        return response

    def close(self) -> None:
        process = getattr(self, "process", None)
        if process is None:
            return
        if process.poll() is None:
            try:
                self.request({"op": "quit"})
            except (HoldoutAdapterError, OSError, subprocess.SubprocessError):
                process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
        for stream in (process.stdin, process.stdout, process.stderr):
            if stream is not None:
                stream.close()


def validate_channel_digests(value: Any) -> dict[str, str]:
    require(isinstance(value, dict) and set(value) == set(CHANNELS), "exactly four independently labeled correctness digests are required")
    for name in CHANNELS:
        digest = value[name]
        require(
            isinstance(digest, str)
            and len(digest) == 64
            and all(letter in "0123456789abcdef" for letter in digest),
            f"invalid independent correctness digest: {name}",
        )
    return value


class CaseTrialBuffer:
    """Exactly one case's 19 paired observations; no global timing matrix."""

    def __init__(self) -> None:
        self.values = array("Q", [0]) * (TRIALS * len(FAMILIES))
        require(self.values.itemsize == 8, "the pinned platform has no uint64 case buffer")
        self.completed = 0

    @staticmethod
    def offset(trial: int, family: str) -> int:
        require(type(trial) is int and 0 <= trial < TRIALS, "case-buffer trial is out of bounds")
        require(family in FAMILIES, "case-buffer family is not independently approved")
        return trial * len(FAMILIES) + FAMILIES.index(family)

    def record(self, trial: int, family: str, elapsed_ns: int) -> None:
        require(type(elapsed_ns) is int and 0 < elapsed_ns < 1 << 64, "invalid uint64 observation")
        index = self.offset(trial, family)
        require(self.values[index] == 0, "duplicate paired observation in the current fresh case")
        self.values[index] = elapsed_ns
        self.completed += 1

    def paired(self, candidate: str) -> tuple[int, ...]:
        require(candidate in CANDIDATE_FAMILIES, "baseline cannot be ranked against itself")
        require(self.completed == TRIALS * len(FAMILIES), "a fresh case omitted paired observations")
        result: list[int] = []
        for trial in range(TRIALS):
            result.extend(
                (
                    self.values[self.offset(trial, "re")],
                    self.values[self.offset(trial, candidate)],
                )
            )
        require(len(result) == 2 * TRIALS and all(result), "paired fresh case timings are incomplete")
        return tuple(result)

    @property
    def storage_bytes(self) -> int:
        return len(self.values) * self.values.itemsize


def bootstrap_seed(mode: int, case_index: int, candidate_index: int) -> bytes:
    require(mode in {CASE_BOOTSTRAP, AGGREGATE_BOOTSTRAP}, "invalid prospective bootstrap operation")
    require(type(candidate_index) is int and 0 <= candidate_index < len(CANDIDATE_FAMILIES), "invalid bootstrap candidate")
    if mode == CASE_BOOTSTRAP:
        require(type(case_index) is int and 0 <= case_index < CASES, "invalid bootstrap case index")
    else:
        require(case_index == AGGREGATE_CASE_INDEX, "aggregate bootstrap requires its fixed sentinel")
    seed = hashlib.sha256(
        BOOTSTRAP_DOMAIN
        + bytes((mode,))
        + struct.pack("<Q", case_index)
        + CANDIDATE_FAMILIES[candidate_index].encode("ascii")
    ).digest()
    require(seed != bytes(32), "a zero-state deterministic bootstrap seed was rejected")
    return seed


def bootstrap_request(
    mode: int,
    case_index: int,
    candidate_index: int,
    values: tuple[int, ...] | tuple[float, ...],
) -> bytes:
    seed = bootstrap_seed(mode, case_index, candidate_index)
    header = BOOTSTRAP_HEADER.pack(
        REQUEST_MAGIC,
        BOOTSTRAP_VERSION,
        mode,
        TRIALS,
        BOOTSTRAP_DRAWS,
        candidate_index,
        seed,
        case_index,
    )
    require(len(values) == (2 * TRIALS if mode == CASE_BOOTSTRAP else TRIALS), "the native bootstrap changed its paired denominator")
    if mode == CASE_BOOTSTRAP:
        require(all(type(value) is int and 0 < value < 1 << 64 for value in values), "the native bootstrap received invalid uint64 timings")
        payload = BOOTSTRAP_CASE_PAYLOAD.pack(*values)
    else:
        require(all(type(value) is float and math.isfinite(value) for value in values), "the native bootstrap received nonfinite aggregate logarithms")
        payload = BOOTSTRAP_AGGREGATE_PAYLOAD.pack(*values)
    return header + payload


def parse_bootstrap_response(
    frame: bytes,
    *,
    mode: int,
    case_index: int,
    candidate_index: int,
) -> dict[str, Any]:
    require(isinstance(frame, bytes) and len(frame) == BOOTSTRAP_RESPONSE.size, "the native bootstrap omitted its exact fixed-size response")
    (
        magic,
        version,
        actual_mode,
        trials,
        draws,
        actual_candidate,
        seed,
        actual_case,
        estimate,
        lower,
        upper,
    ) = BOOTSTRAP_RESPONSE.unpack(frame)
    require(
        magic == RESPONSE_MAGIC
        and version == BOOTSTRAP_VERSION
        and actual_mode == mode
        and trials == TRIALS
        and draws == BOOTSTRAP_DRAWS
        and actual_candidate == candidate_index
        and actual_case == case_index
        and seed == bootstrap_seed(mode, case_index, candidate_index),
        "the native bootstrap response was substituted or used a different seed",
    )
    require(
        all(math.isfinite(value) and value > 0 for value in (estimate, lower, upper))
        and lower <= upper,
        "the native bootstrap returned a nonfinite or inverted paired interval",
    )
    return {
        "candidate": CANDIDATE_FAMILIES[candidate_index],
        "case_index": case_index,
        "paired_trials": TRIALS,
        "bootstrap_samples": BOOTSTRAP_DRAWS,
        "geometric_mean_speedup": estimate,
        "confidence_interval": {"level": 0.95, "lower": lower, "upper": upper},
    }


class BootstrapStream:
    """A future, separately pinned native statistics helper; never an engine."""

    def __init__(self, executable: Path, *, expected_sha256: str) -> None:
        ensure_candidate_free()
        require(
            isinstance(expected_sha256, str)
            and len(expected_sha256) == 64
            and all(item in "0123456789abcdef" for item in expected_sha256),
            "the native statistics artifact lacks a frozen SHA-256",
        )
        path = Path(executable)
        require(not path.is_symlink() and path.is_file(), "the native statistics artifact is not a regular file")
        require(path.parent.resolve() == (ROOT / "tools").resolve(), "the native statistics artifact escaped its owned tools directory")
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            while block := stream.read(1024 * 1024):
                digest.update(block)
        require(digest.hexdigest() == expected_sha256, "the frozen native statistics artifact changed")
        self.process = subprocess.Popen(
            [str(path), "--stream-v1"],
            cwd=ROOT,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def interval(
        self,
        mode: int,
        case_index: int,
        candidate_index: int,
        values: tuple[int, ...] | tuple[float, ...],
    ) -> dict[str, Any]:
        ensure_candidate_free()
        require(self.process.poll() is None, "the native paired-bootstrap helper exited")
        require(self.process.stdin is not None and self.process.stdout is not None, "the native bootstrap lost its bounded binary protocol")
        request = bootstrap_request(mode, case_index, candidate_index, values)
        try:
            self.process.stdin.write(request)
            self.process.stdin.flush()
            response = self.process.stdout.read(BOOTSTRAP_RESPONSE.size)
        except (BrokenPipeError, OSError) as error:
            raise HoldoutAdapterError("the native bootstrap rejected its exact paired frame") from error
        require(isinstance(response, bytes), "the native bootstrap returned a nonbinary response")
        return parse_bootstrap_response(
            response,
            mode=mode,
            case_index=case_index,
            candidate_index=candidate_index,
        )

    def close(self) -> None:
        if self.process.stdin is not None:
            self.process.stdin.close()
        try:
            result = self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=10)
            raise HoldoutAdapterError("native paired-bootstrap helper did not stop cleanly")
        require(result == 0, "native paired-bootstrap helper reported an invalid or incomplete frame")
        for stream in (self.process.stdout, self.process.stderr):
            if stream is not None:
                stream.close()


def candidate_free_self_test() -> dict[str, Any]:
    """Run deterministic, exclusively in-memory adapter poison controls."""

    ensure_candidate_free()
    checks: list[dict[str, Any]] = []

    def check(name: str, value: bool) -> None:
        checks.append({"name": name, "passed": bool(value)})

    def rejected(name: str, action: Any) -> None:
        try:
            action()
        except (HoldoutAdapterError, OverflowError, TypeError, ValueError):
            check(name, True)
        else:
            check(name, False)

    check("four-distinct-public-channel-names", len(CHANNELS) == 4 and len(set(CHANNELS)) == 4)
    check("exact-independent-worker-families", FAMILIES == ("re", "rust", "vm", "zig"))
    check("exact-65536-case-population", CASES == 16 * 16 * 256)
    check("exact-4980736-paired-observations", CASES * TRIALS * len(FAMILIES) == 4_980_736)
    check("exact-14942208-four-channel-gates", CASES * TRIALS * len(CANDIDATE_FAMILIES) * len(CHANNELS) == 14_942_208)
    check("exact-196611-confidence-intervals", CASES * len(CANDIDATE_FAMILIES) + len(CANDIDATE_FAMILIES) == 196_611)
    check("exact-2000-bootstrap-draws", BOOTSTRAP_DRAWS == 2_000)
    check("exact-64-byte-native-request-header", BOOTSTRAP_HEADER.size == 64)
    check("exact-88-byte-native-response", BOOTSTRAP_RESPONSE.size == 88)
    check("exact-304-byte-paired-bootstrap-payload", BOOTSTRAP_CASE_PAYLOAD.size == 304)
    check("exact-152-byte-aggregate-bootstrap-payload", BOOTSTRAP_AGGREGATE_PAYLOAD.size == 152)

    surrogate = "\ud800\n\udfff"
    encoded = canonical({"surrogate": surrogate})
    check("canonical-wire-is-ascii", encoded.isascii())
    check("canonical-wire-roundtrips-lone-surrogates", json.loads(encoded)["surrogate"] == surrogate)
    check("canonical-wire-has-no-embedded-frame-newline", b"\n" not in encoded)
    rejected("reject-nonfinite-wire-observables", lambda: canonical({"poison": float("nan")}))
    check("preserve-exact-bytes-representation", normalize(b"a\xff") == {"kind": "bytes", "hex": "61ff"})
    check("preserve-exact-bytearray-representation", normalize(bytearray(b"a\xff")) == {"kind": "bytearray", "hex": "61ff"})
    view = memoryview(b"a\xff")
    check("preserve-buffer-kind-and-readonly-state", normalize(view)["kind"] == "memoryview" and normalize(view)["readonly"] is True)
    view.release()
    check("preserve-released-memoryview-state", normalize(view) == {"kind": "memoryview", "released": True})
    check("preserve-tuple-identity", normalize((1, "a")) == {"tuple": [1, "a"]})
    rejected("reject-colliding-normalized-mapping-keys", lambda: normalize({1: "a", "1": "b"}))

    synthetic = {name: {"lane": name, "surrogate": surrogate} for name in CHANNELS}
    first = lane_digests(synthetic)
    second = lane_digests(dict(synthetic))
    check("all-four-observation-digests-are-deterministic", first == second)
    check("all-four-observation-digests-are-independent", len(set(first.values())) == 4)
    check("all-four-observation-digests-are-exact-sha256", validate_channel_digests(first) == first)
    for index, name in enumerate(CHANNELS):
        poisoned = dict(synthetic)
        poisoned[name] = {"lane": name, "surrogate": surrogate, "poison": index}
        updated = lane_digests(poisoned)
        check(
            "detect-independent-channel-poison:" + name,
            updated[name] != first[name]
            and all(updated[other] == first[other] for other in CHANNELS if other != name),
        )
    rejected("reject-omitted-correctness-channel", lambda: lane_digests({name: synthetic[name] for name in CHANNELS[:-1]}))
    rejected("reject-extra-correctness-channel", lambda: lane_digests({**synthetic, "poison": {}}))
    rejected("reject-malformed-channel-digest", lambda: validate_channel_digests({**first, CHANNELS[0]: "0"}))

    fake_guard = (
        'if mode not in {"smoke", "persistent"}:\n'
        '    raise RuntimeError("invalid guarded worker mode")\n'
        "prepared = None\n\n\ndef prepare_case(candidate, request):\n"
        "    return request\n"
        '            elif operation == "quit":\n'
    )
    derived, evidence = derive_guarded_worker_source(fake_guard)
    check("exactly-three-unique-immutable-guard-anchors", evidence["anchor_counts"] == {"frozen-worker-mode": 1, "guarded-fresh-functions": 1, "guarded-fresh-dispatch": 1})
    check("restore-original-guard-byte-for-byte", evidence["unchanged_original_guard_restores_exactly"] is True)
    check("one-exact-embedded-four-channel-extension", derived.count(WORKER_EXTENSION) == 1)
    check("one-exact-fresh-worker-mode", derived.count(MODE_REPLACEMENT) == 1)
    check("one-exact-fresh-worker-dispatch", derived.count(DISPATCH_EXTENSION) == 1)
    check("derived-guard-has-source-bound-sha256", evidence["derived_source_sha256"] == hashlib.sha256(derived.encode("utf-8")).hexdigest())
    for name, anchor in (("mode", MODE_ANCHOR), ("prepare", PREPARE_ANCHOR), ("dispatch", DISPATCH_ANCHOR)):
        rejected("reject-missing-immutable-anchor:" + name, lambda needle=anchor: derive_guarded_worker_source(fake_guard.replace(needle, "", 1)))
        rejected("reject-duplicate-immutable-anchor:" + name, lambda needle=anchor: derive_guarded_worker_source(fake_guard + "\n" + needle))
    rejected("reject-previously-extended-guard", lambda: derive_guarded_worker_source(derived))

    case = {
        "schema": CASE_SCHEMA,
        "id": "fresh.literal.00.000",
        "family": "literal",
        "family_index": 0,
        "stratum": {
            "index": 0,
            "input_domain": "text",
            "flag_tier": "default",
            "window": "default",
            "lifecycle": "module",
        },
        "variant": 0,
        "pattern": {"kind": "str", "text": surrogate},
        "subject": {"kind": "str", "text": "x" + surrogate},
        "flags": 0,
        "pos": None,
        "endpos": None,
        "lifecycle": "module",
        "operation": "search",
        "replacement": {"kind": "str", "text": "R"},
        "maxsplit": 0,
        "replacement_count": 0,
        "max_matches": MAX_MATCHES,
    }
    descriptor = private_case_descriptor(case)
    check("one-way-descriptor-preserves-lone-surrogates", json.loads(canonical(descriptor))["pattern"]["text"] == surrogate)
    check("one-way-descriptor-has-only-allowed-fields", set(descriptor) == CASE_FIELDS)
    rejected("reject-secret-or-oracle-answer-in-descriptor", lambda: private_case_descriptor({**case, "private_key": "poison"}))
    rejected("reject-missing-fresh-descriptor-field", lambda: private_case_descriptor({name: value for name, value in case.items() if name != "pattern"}))
    rejected("reject-unfrozen-fresh-case-schema", lambda: private_case_descriptor({**case, "schema": "poison"}))
    rejected("reject-scanner-on-module-lifecycle", lambda: private_case_descriptor({**case, "operation": "scanner"}))
    rejected("reject-unbounded-fresh-pattern", lambda: private_case_descriptor({**case, "pattern": {"kind": "str", "text": "p" * (MAX_PATTERN_BYTES + 1)}}))
    rejected("reject-unbounded-fresh-subject", lambda: private_case_descriptor({**case, "subject": {"kind": "str", "text": "s" * (MAX_SUBJECT_BYTES + 1)}}))

    raw = b"a\x00\xff"
    for kind in ("bytes", "bytearray", "memoryview"):
        transmitted = _bounded_wire({"kind": kind, "base64": base64.b64encode(raw).decode("ascii")})
        check("lossless-hex-wire:" + kind, transmitted == {"kind": kind, "hex": raw.hex()})
    rejected("reject-malformed-base64-wire", lambda: _bounded_wire({"kind": "bytes", "base64": "%%%"}))

    trial_buffer = CaseTrialBuffer()
    check("exactly-76-uint64-timing-cells", len(trial_buffer.values) == 76)
    check("exactly-608-bytes-of-case-timing-state", trial_buffer.storage_bytes == 608)
    for trial in range(TRIALS):
        for index, family in enumerate(FAMILIES):
            trial_buffer.record(trial, family, 1_000 + trial * 10 + index)
    check("all-76-paired-observations-accounted", trial_buffer.completed == 76)
    for index, family in enumerate(CANDIDATE_FAMILIES, start=1):
        pairs = trial_buffer.paired(family)
        check("exact-38-paired-values:" + family, len(pairs) == 38 and pairs[0] == 1_000 and pairs[1] == 1_000 + index)
    rejected("reject-duplicate-paired-case-observation", lambda: trial_buffer.record(0, "re", 1))
    rejected("reject-baseline-self-comparison", lambda: trial_buffer.paired("re"))
    rejected("reject-out-of-range-paired-trial", lambda: trial_buffer.record(TRIALS, "re", 1))

    values = trial_buffer.paired("rust")
    request = bootstrap_request(CASE_BOOTSTRAP, 0, 0, values)
    check("exact-368-byte-case-bootstrap-request", len(request) == BOOTSTRAP_HEADER.size + BOOTSTRAP_CASE_PAYLOAD.size)
    seed = bootstrap_seed(CASE_BOOTSTRAP, 0, 0)
    check("reproducible-domain-separated-bootstrap-seed", seed == bootstrap_seed(CASE_BOOTSTRAP, 0, 0))
    check("distinct-candidate-bootstrap-seeds", seed != bootstrap_seed(CASE_BOOTSTRAP, 0, 1))
    check("distinct-case-bootstrap-seeds", seed != bootstrap_seed(CASE_BOOTSTRAP, 1, 0))
    aggregate_values = tuple(float(index) / 100 for index in range(TRIALS))
    aggregate_request = bootstrap_request(AGGREGATE_BOOTSTRAP, AGGREGATE_CASE_INDEX, 0, aggregate_values)
    check("exact-216-byte-aggregate-bootstrap-request", len(aggregate_request) == BOOTSTRAP_HEADER.size + BOOTSTRAP_AGGREGATE_PAYLOAD.size)
    check("distinct-case-and-aggregate-bootstrap-seeds", seed != bootstrap_seed(AGGREGATE_BOOTSTRAP, AGGREGATE_CASE_INDEX, 0))
    rejected("reject-omitted-bootstrap-pair", lambda: bootstrap_request(CASE_BOOTSTRAP, 0, 0, values[:-1]))
    rejected("reject-zero-bootstrap-observation", lambda: bootstrap_request(CASE_BOOTSTRAP, 0, 0, (0,) + values[1:]))
    rejected("reject-nonfinite-aggregate-bootstrap", lambda: bootstrap_request(AGGREGATE_BOOTSTRAP, AGGREGATE_CASE_INDEX, 0, (float("nan"),) + aggregate_values[1:]))
    rejected("reject-aggregate-with-real-case-index", lambda: bootstrap_request(AGGREGATE_BOOTSTRAP, 0, 0, aggregate_values))

    response = BOOTSTRAP_RESPONSE.pack(
        RESPONSE_MAGIC,
        BOOTSTRAP_VERSION,
        CASE_BOOTSTRAP,
        TRIALS,
        BOOTSTRAP_DRAWS,
        0,
        seed,
        0,
        1.25,
        1.1,
        1.4,
    )
    parsed = parse_bootstrap_response(response, mode=CASE_BOOTSTRAP, case_index=0, candidate_index=0)
    check("validate-exact-native-bootstrap-response", parsed["geometric_mean_speedup"] == 1.25 and parsed["confidence_interval"] == {"level": 0.95, "lower": 1.1, "upper": 1.4})
    rejected("reject-short-native-bootstrap-response", lambda: parse_bootstrap_response(response[:-1], mode=CASE_BOOTSTRAP, case_index=0, candidate_index=0))
    rejected("reject-substituted-native-bootstrap-candidate", lambda: parse_bootstrap_response(response, mode=CASE_BOOTSTRAP, case_index=0, candidate_index=1))
    poisoned_response = BOOTSTRAP_RESPONSE.pack(RESPONSE_MAGIC, BOOTSTRAP_VERSION, CASE_BOOTSTRAP, TRIALS, BOOTSTRAP_DRAWS, 0, seed, 0, 1.25, 1.4, 1.1)
    rejected("reject-inverted-native-bootstrap-interval", lambda: parse_bootstrap_response(poisoned_response, mode=CASE_BOOTSTRAP, case_index=0, candidate_index=0))

    ensure_candidate_free()
    failed = [item["name"] for item in checks if not item["passed"]]
    return {
        "schema": ADAPTER_SCHEMA + "-self-test",
        "status": "PASS" if not failed else "FAIL",
        "passed": not failed,
        "checks": checks,
        "check_count": len(checks),
        "failed": failed,
        "case_population": CASES,
        "paired_trials": TRIALS,
        "participant_count": len(FAMILIES),
        "raw_observations": CASES * TRIALS * len(FAMILIES),
        "correctness_channels": list(CHANNELS),
        "correctness_gates": CASES * TRIALS * len(CANDIDATE_FAMILIES) * len(CHANNELS),
        "confidence_intervals": CASES * len(CANDIDATE_FAMILIES) + len(CANDIDATE_FAMILIES),
        "bootstrap_samples": BOOTSTRAP_DRAWS,
        "maximum_case_timing_bytes": trial_buffer.storage_bytes,
        "private_wire_format": "canonical-ascii-json-utf8",
        "candidate_imports": 0,
        "subprocesses": 0,
        "production_entropy_drawn": False,
        "file_reads": 0,
        "file_writes": 0,
        "guard_created": False,
        "guard_read": False,
        "production_cases_materialized": 0,
        "historical_holdout_accessed": False,
        "benchmark_or_timing_executed": False,
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run only deterministic in-memory, candidate-free poison controls",
    )
    args = parser.parse_args(arguments)
    if not args.self_test:
        parser.error("only the candidate-free --self-test is available before an explicit frozen opening")
    try:
        result = candidate_free_self_test()
    except (HoldoutAdapterError, OverflowError, TypeError, ValueError) as error:
        sys.stdout.buffer.write(
            canonical(
                {
                    "schema": ADAPTER_SCHEMA + "-self-test",
                    "status": "FAIL",
                    "passed": False,
                    "error": str(error),
                    "candidate_imports": 0,
                    "production_entropy_drawn": False,
                    "historical_holdout_accessed": False,
                    "benchmark_or_timing_executed": False,
                }
            )
            + b"\n"
        )
        return 1
    sys.stdout.buffer.write(canonical(result) + b"\n")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
