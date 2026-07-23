#!/usr/bin/env python3
"""Frozen public-observability oracle for the from-scratch Rust re engine."""

from __future__ import annotations

import argparse
import array
import collections
import gc
import gzip
import hashlib
import importlib
import json
import os
import random
import subprocess
import sys
import types
import weakref
from pathlib import Path
from typing import Any


SCHEMA = "rebar-rust-v7-public-observability-v2"
PINNED = (3, 14, 6)
SEED = 2026072343
FROZEN_FIXTURE_SHA256 = (
    "1d5a84b9fe2213289d96126dab740d103958bd593b811b262238bfc57a4a5403"
)
EDGE_SCHEMA = "rebar-v7-independent-edge-oracle-v1"
EDGE_SEED = 2026072329
EDGE_CHECKS = 223198
EDGE_CATEGORIES = 49
EDGE_SCRIPT_SHA256 = (
    "fe6a263a48f243ea02faaa78fc3bbd051233a2b2221967a5f76dd1bb79d242ca"
)
EDGE_REFERENCE_SHA256 = (
    "b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526"
)
EDGE_BASELINE_SHA256 = (
    "392cda0f0e17a2ec020d445a594958e46f2521ff951b4341c99f6fb5af5e722f"
)
EDGE_FROZEN_CANDIDATE_SHA256 = (
    "4ad0a2516ede95751a8f2bc6b4d907f12048b2556311ff3bd71c4e4a7664bb2b"
)
ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "candidates" / "evidence"
EDGE_SCRIPT = ROOT / "tools" / "rust_v7_edge_oracle.py"
EDGE_BASELINE = EVIDENCE / "rust-v7-edge-oracle-stdlib-baseline.json.gz"
EDGE_FROZEN_CANDIDATE = (
    EVIDENCE / "rust-v7-edge-oracle-rust-corrected-v4.json.gz"
)
ARCHIVE_NAMES = {
    "manifest": "rust-v7-observability-manifest.json.gz",
    "stdlib-a": "rust-v7-observability-stdlib-a.json.gz",
    "stdlib-b": "rust-v7-observability-stdlib-b.json.gz",
    "candidate": "rust-v7-observability-candidate.json.gz",
    "private-binders": "rust-v7-observability-private-binders.json.gz",
    "rejected-iterator-control": (
        "rust-v7-observability-rejected-iterator-control.json.gz"
    ),
}
PRODUCTION_ARTIFACTS = {
    "public-python": (
        ROOT / "candidates/rust_candidate.py",
        "1111a419d65d44775d1f4b0cb6a728dea8de44a592597341596533351c16018e",
    ),
    "native-source": (
        ROOT / "candidates/rust/src/lib.rs",
        "a2fa04912bb1f6957f833560446f4d3d1c5d13df8b5efac992fa63e28803668b",
    ),
    "bridge-source": (
        ROOT / "candidates/rust/py_bridge.c",
        "8900b120ddb85a74aedf584b960ff878aa47020c910c0ce749dae51eb304f3c2",
    ),
    "native-engine": (
        ROOT / "candidates/_rust_engine.so",
        "890f9e34e966244067a3dc173c2276043ae15d4830a05228fb37ec2571aa17cd",
    ),
    "native-bridge": (
        ROOT / "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "eedcd253ab9ec6bab9a9ac9242d04d3fc6c808bf1b8de342bb5a5b9fd8528272",
    ),
}


class CallbackFailure(Exception):
    """Deterministic replacement callback exception."""


class MaliciousFailure(Exception):
    """Deterministic user-supplied protocol exception."""


class TrackedText(str):
    pass


class TrackedReplacement(str):
    pass


def path_digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def value_digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def normalize(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int)):
        return value
    if isinstance(value, str):
        if any(0xD800 <= ord(character) <= 0xDFFF for character in value):
            return {
                "kind": "str",
                "surrogatepass_utf8_hex": value.encode(
                    "utf-8", "surrogatepass"
                ).hex(),
            }
        return str(value)
    if isinstance(value, (bytes, bytearray, memoryview)):
        return {"kind": type(value).__name__, "hex": bytes(value).hex()}
    if isinstance(value, array.array):
        return {
            "kind": "array",
            "typecode": value.typecode,
            "hex": value.tobytes().hex(),
        }
    if isinstance(value, BaseException):
        return {
            "type": type(value).__name__,
            "args": normalize(value.args),
        }
    if isinstance(value, (list, tuple)):
        return [normalize(item) for item in value]
    if isinstance(value, dict):
        return {
            str(key): normalize(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, types.MappingProxyType):
        return normalize(dict(value))
    if hasattr(value, "span") and hasattr(value, "groups"):
        return {
            "span": normalize(value.span()),
            "group0": normalize(value.group(0)),
            "groups": normalize(value.groups()),
            "groupdict": normalize(value.groupdict()),
            "lastindex": value.lastindex,
            "lastgroup": value.lastgroup,
            "pos": value.pos,
            "endpos": value.endpos,
        }
    return {"kind": type(value).__name__}


def attempted(action) -> dict[str, Any]:
    try:
        return {"status": "value", "value": normalize(action())}
    except BaseException as error:
        return {"status": "error", "error": normalize(error)}


def domain_values(byte_mode: bool):
    if byte_mode:
        return rb"(?P<letter>a)(b)?", b"aba", b"!"
    return r"(?P<letter>a)(b)?", "aba", "!"


def invoke_substitution(
    module,
    operation: str,
    bound: bool,
    pattern,
    replacement,
    subject,
    count,
):
    if bound:
        return getattr(module.compile(pattern), operation)(
            replacement,
            subject,
            count,
        )
    return getattr(module, operation)(
        pattern,
        replacement,
        subject,
        count=count,
    )


def profiled_callback_case(module, case):
    pattern, subject, marker = domain_values(case["bytes"])
    callback_events = []
    builtin_events = []
    internal_events = collections.Counter()
    effects = []

    def replacement(match):
        piece = match.group("letter")
        length = len(piece)
        effects.append(("callback", piece, length))
        if case["failure"] and len(effects) == 2:
            raise CallbackFailure("profile replacement sentinel")
        return piece + marker

    callback_code = replacement.__code__

    def profile(frame, event, argument):
        if frame.f_code is callback_code:
            if event in ("call", "return"):
                callback_events.append(
                    (event, normalize(argument) if event == "return" else None)
                )
            elif event in ("c_call", "c_return", "c_exception"):
                if argument is len:
                    builtin_events.append((event, "builtins.len"))
                else:
                    owner = getattr(argument, "__module__", None)
                    name = getattr(argument, "__qualname__", None)
                    internal_events[(event, str(owner), str(name))] += 1
        return profile

    before = sys.getprofile()
    sys.setprofile(profile)
    try:
        result = attempted(
            lambda: invoke_substitution(
                module,
                case["operation"],
                case["bound"],
                pattern,
                replacement,
                subject,
                case["count"],
            )
        )
    finally:
        sys.setprofile(before)
    observation = {
        "result": result,
        "callback_events": normalize(callback_events),
        "builtin_c_events": normalize(builtin_events),
        "callback_effects": normalize(effects),
        "profile_restored": sys.getprofile() is before,
        "recovery": normalize(module.fullmatch("a", "a")),
    }
    diagnostic = {
        "engine_specific_c_events": [
            {"event": key[0], "module": key[1], "name": key[2], "count": count}
            for key, count in sorted(internal_events.items())
        ],
    }
    return observation, diagnostic


def monitoring_callback_case(module, case):
    monitor = getattr(sys, "monitoring", None)
    if monitor is None:
        return {"monitoring": "NOT AVAILABLE"}, {}
    tool_id = next(
        (number for number in (4, 3) if monitor.get_tool(number) is None),
        None,
    )
    if tool_id is None:
        return {"monitoring": "NO FREE TOOL"}, {}
    pattern, subject, marker = domain_values(case["bytes"])
    effects = []
    public_events = []
    internal_events = collections.Counter()

    def replacement(match):
        value = match.group("letter")
        effects.append((value, len(value)))
        if case["failure"] and len(effects) == 2:
            raise CallbackFailure("monitoring replacement sentinel")
        return value + marker

    code = replacement.__code__

    def receiver(event_name):
        def receive(*arguments):
            if not arguments or arguments[0] is not code:
                return None
            if event_name in ("PY_START", "PY_RETURN"):
                result = (
                    normalize(arguments[-1])
                    if event_name == "PY_RETURN" and len(arguments) > 2
                    else None
                )
                public_events.append((event_name, result))
                return None
            if event_name in ("CALL", "C_RETURN", "C_RAISE"):
                callable_object = arguments[2] if len(arguments) > 2 else None
                if callable_object is len:
                    public_events.append((event_name, "builtins.len"))
                else:
                    owner = getattr(callable_object, "__module__", None)
                    name = getattr(callable_object, "__qualname__", None)
                    internal_events[(event_name, str(owner), str(name))] += 1
            return None

        return receive

    registered = []
    monitor.use_tool_id(tool_id, "rebar-rust-v7-observability")
    try:
        for name in ("PY_START", "PY_RETURN", "CALL", "C_RETURN", "C_RAISE"):
            event = getattr(monitor.events, name, None)
            if event is not None:
                monitor.register_callback(tool_id, event, receiver(name))
                registered.append(event)
        mask = (
            monitor.events.PY_START
            | monitor.events.PY_RETURN
            | monitor.events.CALL
        )
        monitor.set_events(tool_id, mask)
        try:
            result = attempted(
                lambda: invoke_substitution(
                    module,
                    case["operation"],
                    case["bound"],
                    pattern,
                    replacement,
                    subject,
                    case["count"],
                )
            )
        finally:
            monitor.set_events(tool_id, monitor.events.NO_EVENTS)
    finally:
        for event in registered:
            monitor.register_callback(tool_id, event, None)
        monitor.free_tool_id(tool_id)
    observation = {
        "monitoring": "AVAILABLE",
        "result": result,
        "public_events": normalize(public_events),
        "callback_effects": normalize(effects),
        "tool_released": monitor.get_tool(tool_id) is None,
        "recovery": normalize(module.fullmatch("a", "a")),
    }
    diagnostic = {
        "engine_specific_monitoring_events": [
            {"event": key[0], "module": key[1], "name": key[2], "count": count}
            for key, count in sorted(internal_events.items())
        ],
    }
    return observation, diagnostic


def recursion_case(module, case):
    old_limit = sys.getrecursionlimit()
    requested = case["depth"]
    calls = [0]
    operation = case["operation"]

    def replacement(match):
        calls[0] += 1
        if case["overflow"] or calls[0] < requested:
            nested = getattr(module, operation)(
                "a",
                replacement,
                "a",
                count=1,
            )
            return nested[0] if operation == "subn" else nested
        return "x"

    if case["overflow"]:
        sys.setrecursionlimit(96)
    try:
        captured = attempted(
            lambda: getattr(module, operation)(
                "a",
                replacement,
                "a",
                count=1,
            )
        )
    finally:
        sys.setrecursionlimit(old_limit)
    if case["overflow"]:
        error = captured.get("error", {})
        observation = {
            "overflow": True,
            "raised_recursion_error": error.get("type") == "RecursionError",
            "recursion_limit_restored": (
                sys.getrecursionlimit() == old_limit
            ),
            "recovery": normalize(module.fullmatch("a", "a")),
        }
        diagnostic = {
            "engine_specific_callback_depth": calls[0],
            "engine_specific_recursion_error": captured,
        }
    else:
        observation = {
            "overflow": False,
            "result": captured,
            "callback_count": calls[0],
            "recursion_limit_restored": (
                sys.getrecursionlimit() == old_limit
            ),
            "recovery": normalize(module.fullmatch("a", "a")),
        }
        diagnostic = {}
    return observation, diagnostic


def callback_case(module, case):
    pattern, subject, marker = domain_values(case["bytes"])
    effects = []
    mode = case["mode"]

    def replacement(match):
        effects.append(
            (
                match.span(),
                match.group("letter"),
                match.groupdict(),
                match.string is subject,
            )
        )
        if mode == "value":
            return match.group("letter") + marker
        if mode == "subclass" and not case["bytes"]:
            return TrackedReplacement(match.group("letter") + marker)
        if mode == "none":
            return None
        if mode == "integer":
            return 7
        if mode == "opposite-domain":
            return "wrong" if case["bytes"] else b"wrong"
        if mode == "raise-first":
            raise CallbackFailure("replacement sentinel")
        if mode == "raise-second" and len(effects) == 2:
            raise CallbackFailure("replacement sentinel")
        if mode == "stop-iteration":
            raise StopIteration("replacement sentinel")
        return match.group("letter") + marker

    result = attempted(
        lambda: invoke_substitution(
            module,
            case["operation"],
            case["bound"],
            pattern,
            replacement,
            subject,
            case["count"],
        )
    )
    observation = {
        "result": result,
        "effects": normalize(effects),
        "recovery": normalize(module.fullmatch("a", "a")),
    }
    return observation, {}


class MaliciousIndex:
    def __init__(self, trace, mode):
        self.trace = trace
        self.mode = mode

    def __index__(self):
        self.trace.append(("index", self.mode))
        if self.mode == "raise":
            raise MaliciousFailure("index sentinel")
        if self.mode == "noninteger":
            return "not-an-index"
        if self.mode == "overflow":
            return 1 << 100
        return 1


def public_binder_case(module, case):
    pattern = module.compile(r"(?P<letter>a)(b)?")
    method = getattr(pattern, case["method"])
    trace = []
    bomb = MaliciousIndex(trace, case["mode"])
    shape = case["shape"]
    if case["method"] in ("search", "match", "fullmatch", "findall", "finditer", "scanner"):
        if shape == "missing":
            action = lambda: method()
        elif shape == "unexpected":
            action = lambda: method("aba", invalid=1)
        elif shape == "duplicate":
            action = lambda: method("aba", string="aba")
        elif shape == "index":
            action = lambda: method("aba", bomb)
        elif shape == "end-index":
            action = lambda: method("aba", 0, bomb)
        else:
            raise AssertionError("unknown matching binder shape")
    elif case["method"] == "split":
        if shape == "missing":
            action = lambda: method()
        elif shape == "unexpected":
            action = lambda: method("aba", invalid=1)
        elif shape == "duplicate":
            action = lambda: method("aba", string="aba")
        elif shape in ("index", "end-index"):
            action = lambda: method("aba", bomb)
        else:
            raise AssertionError("unknown split binder shape")
    else:
        if shape == "missing":
            action = lambda: method("x")
        elif shape == "unexpected":
            action = lambda: method("x", "aba", invalid=1)
        elif shape == "duplicate":
            action = lambda: method("x", "aba", repl="y")
        elif shape in ("index", "end-index"):
            action = lambda: method("x", "aba", bomb)
        else:
            raise AssertionError("unknown replacement binder shape")
    if case["method"] == "finditer":
        iterator_action = action

        def observe_public_iterator():
            iterator = iterator_action()
            return {
                "iterator_is_its_own_iterator": iter(iterator) is iterator,
                "matches": [normalize(match) for match in iterator],
                "exhausted_after_consumption": next(iterator, None) is None,
            }

        action = observe_public_iterator
    observed = attempted(action)
    if observed.get("status") == "value":
        value = observed.get("value")
        if isinstance(value, dict) and value.get("kind") == "SRE_Scanner":
            observed["value"] = {"kind": "iterator"}
    return {
        "result": observed,
        "trace": normalize(trace),
        "recovery": normalize(module.fullmatch("a", "a")),
    }, {}


def lifetime_case(module, case):
    events = []

    class Subject(TrackedText):
        def __del__(self):
            events.append("subject-finalized")

    subject = Subject("aba")
    reference = weakref.ref(subject)
    pattern = module.compile("a")
    kind = case["kind"]
    if kind == "match":
        holder = pattern.search(subject)
    elif kind == "iterator":
        holder = pattern.finditer(subject)
    elif kind == "scanner":
        holder = pattern.scanner(subject)
    else:
        raise AssertionError("unknown subject lifetime")
    del subject
    gc.collect()
    retained = reference() is not None
    if kind == "match":
        observed = normalize(holder)
    elif kind == "iterator":
        match = next(holder)
        observed = normalize(match)
        del match
    else:
        match = holder.search()
        observed = normalize(match)
        del match
    del holder
    gc.collect()
    return {
        "retained_while_live": retained,
        "observed": observed,
        "released_after_use": reference() is None,
        "events": normalize(events),
        "recovery": normalize(module.fullmatch("a", "a")),
    }, {}


def build_cases():
    cases = []

    def add(family, label, **settings):
        cases.append({"family": family, "id": f"{family}/{label}", **settings})

    for operation in ("sub", "subn"):
        for bound in (False, True):
            for byte_mode in (False, True):
                for failure in (False, True):
                    label = (
                        f"{operation}/bound={int(bound)}/bytes={int(byte_mode)}"
                        f"/failure={int(failure)}"
                    )
                    add(
                        "profile-public-callback",
                        label,
                        operation=operation,
                        bound=bound,
                        bytes=byte_mode,
                        failure=failure,
                        count=0,
                    )
                    add(
                        "monitoring-public-callback",
                        label,
                        operation=operation,
                        bound=bound,
                        bytes=byte_mode,
                        failure=failure,
                        count=0,
                    )
    for operation in ("sub", "subn"):
        for depth in (1, 2, 8):
            add(
                "recursive-substitution",
                f"{operation}/depth={depth}",
                operation=operation,
                depth=depth,
                overflow=False,
            )
        add(
            "recursive-substitution",
            f"{operation}/overflow",
            operation=operation,
            depth=512,
            overflow=True,
        )
    for operation in ("sub", "subn"):
        for bound in (False, True):
            for byte_mode in (False, True):
                for mode in (
                    "value",
                    "subclass",
                    "none",
                    "integer",
                    "opposite-domain",
                    "raise-first",
                    "raise-second",
                    "stop-iteration",
                ):
                    for count in (0, 1, 2):
                        add(
                            "replacement-callback",
                            (
                                f"{operation}/bound={int(bound)}"
                                f"/bytes={int(byte_mode)}/mode={mode}/count={count}"
                            ),
                            operation=operation,
                            bound=bound,
                            bytes=byte_mode,
                            mode=mode,
                            count=count,
                        )
    for method in (
        "search",
        "match",
        "fullmatch",
        "findall",
        "finditer",
        "scanner",
        "split",
        "sub",
        "subn",
    ):
        for shape in ("missing", "unexpected", "duplicate", "index", "end-index"):
            for mode in ("value", "raise", "noninteger", "overflow"):
                add(
                    "malicious-public-binder",
                    f"{method}/shape={shape}/mode={mode}",
                    method=method,
                    shape=shape,
                    mode=mode,
                )
    for kind in ("match", "iterator", "scanner"):
        add("object-lifetime", kind, kind=kind)

    generator = random.Random(SEED)
    frozen = tuple(cases)
    for number in range(64):
        original = generator.choice(frozen)
        cases.append(
            {
                **original,
                "id": f"seeded/{number:03d}/{original['id']}",
                "family": "seeded-" + original["family"],
            }
        )
    identities = [case["id"] for case in cases]
    if len(identities) != len(set(identities)):
        raise AssertionError("observability case identity drift")
    return cases


def read_edge_archive(path):
    requested = Path(path)
    if requested.is_symlink():
        raise AssertionError("an edge correctness report must not be a symlink")
    resolved = requested.resolve()
    if not resolved.is_file() or resolved.suffix != ".gz":
        raise AssertionError("the specified frozen edge correctness report is missing")
    try:
        compressed = resolved.read_bytes()
        if len(compressed) < 10 or compressed[:2] != b"\x1f\x8b":
            raise AssertionError("the edge correctness report is not gzip evidence")
        if compressed[3] & 0x08 or compressed[4:8] != b"\x00\x00\x00\x00":
            raise AssertionError("the edge correctness gzip is not deterministic")
        report = json.loads(gzip.decompress(compressed))
    except (OSError, EOFError, gzip.BadGzipFile, ValueError, json.JSONDecodeError) as error:
        raise AssertionError("the edge correctness evidence is unreadable") from error
    if not isinstance(report, dict):
        raise AssertionError("the edge correctness report is not an object")
    return resolved, report


def frozen_edge_baseline():
    if path_digest(EDGE_SCRIPT) != EDGE_SCRIPT_SHA256:
        raise AssertionError("the immutable edge oracle source hash changed")
    if path_digest(EDGE_BASELINE) != EDGE_BASELINE_SHA256:
        raise AssertionError("the immutable edge standard-library baseline changed")
    _, baseline = read_edge_archive(EDGE_BASELINE)
    categories = baseline.get("categories")
    if not isinstance(categories, dict):
        raise AssertionError("the edge standard-library categories are missing")
    if len(categories) != EDGE_CATEGORIES:
        raise AssertionError("the edge standard-library category denominator changed")
    if any(not isinstance(count, int) or count <= 0 for count in categories.values()):
        raise AssertionError("the edge standard-library category counts are invalid")
    if sum(categories.values()) != EDGE_CHECKS:
        raise AssertionError("the edge standard-library case denominator changed")
    expected = {
        "schema": EDGE_SCHEMA,
        "python": "3.14.6",
        "seed": EDGE_SEED,
        "correctness_checks": EDGE_CHECKS,
        "failed": 0,
        "expected_sha256": EDGE_REFERENCE_SHA256,
        "actual_sha256": EDGE_REFERENCE_SHA256,
        "script_sha256": EDGE_SCRIPT_SHA256,
        "oracle": "CPython standard-library re",
        "module": "re",
    }
    for name, value in expected.items():
        if baseline.get(name) != value:
            raise AssertionError(f"the frozen edge baseline changed: {name}")
    if baseline.get("failures") != []:
        raise AssertionError("the frozen edge baseline has unexplained failures")
    return baseline


def validate_edge_document(
    report,
    baseline,
    *,
    check_live_files=True,
    expected_artifacts=None,
):
    expected = {
        "schema": EDGE_SCHEMA,
        "python": "3.14.6",
        "seed": EDGE_SEED,
        "correctness_checks": EDGE_CHECKS,
        "failed": 0,
        "expected_sha256": EDGE_REFERENCE_SHA256,
        "actual_sha256": EDGE_REFERENCE_SHA256,
        "script_sha256": EDGE_SCRIPT_SHA256,
        "oracle": "CPython standard-library re",
        "module": "candidates.rust_candidate",
        "holdout": "NOT ACCESSED",
        "performance": "NOT MEASURED",
    }
    for name, value in expected.items():
        if report.get(name) != value:
            raise AssertionError(f"the canonical edge report is invalid: {name}")
    if report.get("failures") != []:
        raise AssertionError("the canonical edge report contains mismatches")
    for name in (
        "categories",
        "embedded_frozen_oracles",
        "independent_source_seeds",
        "json_normalization",
        "locale",
        "membership_partitions",
        "seeded_cases",
        "unicode",
        "unicode_stride",
    ):
        if report.get(name) != baseline.get(name):
            raise AssertionError(f"the canonical edge suite differs from baseline: {name}")
    categories = report["categories"]
    if len(categories) != EDGE_CATEGORIES or sum(categories.values()) != EDGE_CHECKS:
        raise AssertionError("the canonical edge case or category denominator changed")

    reported = report.get("candidate_artifacts")
    if not isinstance(reported, list) or len(reported) != len(PRODUCTION_ARTIFACTS):
        raise AssertionError("the canonical edge report must contain five artifacts")
    by_role = {}
    for artifact in reported:
        if not isinstance(artifact, dict):
            raise AssertionError("a canonical edge artifact is not an object")
        role = artifact.get("role")
        if role not in PRODUCTION_ARTIFACTS:
            raise AssertionError("an unknown canonical edge artifact was supplied")
        if role in by_role:
            raise AssertionError("a canonical edge artifact role is duplicated")
        canonical_path = PRODUCTION_ARTIFACTS[role][0].resolve()
        canonical_name = canonical_path.relative_to(ROOT).as_posix()
        if artifact.get("path") != canonical_name:
            raise AssertionError(f"a canonical edge artifact path was swapped: {role}")
        fingerprint = artifact.get("sha256")
        if (
            not isinstance(fingerprint, str)
            or len(fingerprint) != 64
            or any(character not in "0123456789abcdef" for character in fingerprint)
        ):
            raise AssertionError(f"a canonical edge artifact hash is invalid: {role}")
        if expected_artifacts is not None:
            original = expected_artifacts[role][1]
            if fingerprint != original:
                raise AssertionError(f"a frozen baseline artifact is stale: {role}")
        if check_live_files and path_digest(canonical_path) != fingerprint:
            raise AssertionError(f"a canonical edge artifact is stale: {role}")
        by_role[role] = (canonical_path, fingerprint)
    if set(by_role) != set(PRODUCTION_ARTIFACTS):
        raise AssertionError("the canonical edge report omitted an artifact role")
    return by_role


def validate_edge_oracle(path):
    baseline = frozen_edge_baseline()
    resolved, report = read_edge_archive(path)
    artifacts = validate_edge_document(report, baseline)
    label = (
        resolved.relative_to(ROOT).as_posix()
        if resolved.is_relative_to(ROOT)
        else str(resolved)
    )
    return {
        "path": label,
        "sha256": path_digest(resolved),
        "schema": report["schema"],
        "script_sha256": report["script_sha256"],
        "baseline_archive_sha256": EDGE_BASELINE_SHA256,
        "reference_sha256": report["expected_sha256"],
        "checks": report["correctness_checks"],
        "categories": len(report["categories"]),
        "failed": report["failed"],
        "artifacts": [
            {
                "role": role,
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": fingerprint,
            }
            for role, (path, fingerprint) in sorted(artifacts.items())
        ],
    }, artifacts


def mapped_files() -> set[Path]:
    result = set()
    for line in Path("/proc/self/maps").read_text(encoding="ascii").splitlines():
        fields = line.split(maxsplit=5)
        if len(fields) == 6 and fields[5].startswith("/"):
            path = Path(fields[5])
            if path.is_file():
                result.add(path.resolve())
    return result


def production_provenance(module, expected_artifacts=None):
    artifacts = (
        PRODUCTION_ARTIFACTS
        if expected_artifacts is None
        else expected_artifacts
    )
    if set(artifacts) != set(PRODUCTION_ARTIFACTS):
        raise AssertionError("the canonical production artifact roles changed")
    bridge = importlib.import_module("candidates._rust_bridge")
    if Path(module.__file__).resolve() != (
        artifacts["public-python"][0].resolve()
    ):
        raise AssertionError("the public production Rust module is not loaded")
    if Path(bridge.__file__).resolve() != (
        artifacts["native-bridge"][0].resolve()
    ):
        raise AssertionError("the production native bridge is not loaded")
    mappings = mapped_files()
    for role in ("native-bridge", "native-engine"):
        if artifacts[role][0].resolve() not in mappings:
            raise AssertionError(f"production {role} is not mapped")
    output = []
    for role, (path, expected) in artifacts.items():
        if path.resolve() != PRODUCTION_ARTIFACTS[role][0].resolve():
            raise AssertionError(f"noncanonical production artifact path: {role}")
        actual = path_digest(path)
        if actual != expected:
            raise AssertionError(f"production artifact changed: {role}")
        output.append(
            {
                "role": role,
                "path": path.resolve().relative_to(ROOT).as_posix(),
                "sha256": actual,
            }
        )
    return sorted(output, key=lambda item: item["role"])


def install_regex_guards():
    standard = importlib.import_module("re")
    sre = importlib.import_module("_sre")
    compiler = importlib.import_module("re._compiler")
    parser = importlib.import_module("re._parser")

    def forbidden(*args, **kwargs):
        raise AssertionError("Rust production delegated to CPython re")

    guards = []
    for name in (
        "compile",
        "search",
        "match",
        "fullmatch",
        "findall",
        "finditer",
        "split",
        "sub",
        "subn",
        "_compile",
    ):
        if hasattr(standard, name):
            setattr(standard, name, forbidden)
            guards.append((standard, name))
    for owner, name in ((sre, "compile"), (compiler, "compile"), (parser, "parse")):
        if not hasattr(owner, name):
            raise AssertionError("missing CPython regex delegation guard")
        setattr(owner, name, forbidden)
        guards.append((owner, name))
    if any(getattr(owner, name) is not forbidden for owner, name in guards):
        raise AssertionError("a regex-delegation guard was not installed")
    return guards


def dispatch_case(module, case):
    family = case["family"]
    if family.startswith("seeded-"):
        family = family.removeprefix("seeded-")
    if family == "profile-public-callback":
        return profiled_callback_case(module, case)
    if family == "monitoring-public-callback":
        return monitoring_callback_case(module, case)
    if family == "recursive-substitution":
        return recursion_case(module, case)
    if family == "replacement-callback":
        return callback_case(module, case)
    if family == "malicious-public-binder":
        return public_binder_case(module, case)
    if family == "object-lifetime":
        return lifetime_case(module, case)
    raise AssertionError(f"unknown observability obligation: {family}")


def rejected_iterator_controls(module):
    """Reproduce and reject the historical private-iterator-name comparison."""
    observations = []
    for shape in ("end-index", "index"):
        trace = []
        bomb = MaliciousIndex(trace, "value")
        pattern = module.compile(r"(?P<letter>a)(b)?")
        if shape == "end-index":
            iterator = pattern.finditer("aba", 0, bomb)
        else:
            iterator = pattern.finditer("aba", bomb)
        private_type = type(iterator).__name__
        legacy_value = {"kind": private_type}
        if private_type in ("callable_iterator", "SRE_Scanner", "RustIterator"):
            legacy_value = {"kind": "iterator"}
        recovery = normalize(module.fullmatch("a", "a"))
        result = {
            "iterator_is_its_own_iterator": iter(iterator) is iterator,
            "matches": [normalize(match) for match in iterator],
            "exhausted_after_consumption": next(iterator, None) is None,
        }
        observations.append(
            {
                "id": (
                    "malicious-public-binder/finditer/shape="
                    f"{shape}/mode=value"
                ),
                "legacy_private_type_observation": {
                    "result": {"status": "value", "value": legacy_value},
                    "trace": normalize(trace),
                    "recovery": recovery,
                },
                "correct_public_observation": {
                    "result": {"status": "value", "value": result},
                    "trace": normalize(trace),
                    "recovery": recovery,
                },
                "diagnostic_private_iterator_type": private_type,
            }
        )
    return observations


def audit_regex_guards(guards):
    """Prove that every forbidden standard-library entry point is poisoned."""
    observations = []
    for owner, name in guards:
        target = getattr(owner, name)
        result = attempted(lambda function=target: function("guard-probe"))
        passed = result == {
            "status": "error",
            "error": {
                "type": "AssertionError",
                "args": ["Rust production delegated to CPython re"],
            },
        }
        observation = {
            "id": f"{owner.__name__}.{name}",
            "passed": passed,
            "result": result,
        }
        observations.append(observation)
        if not passed:
            raise AssertionError(f"regex delegation guard is ineffective: {name}")
    return observations


def private_binder_safety(module):
    bridge = importlib.import_module("candidates._rust_bridge")
    observations = []
    failures = []
    names = (
        "bound_search",
        "bound_match",
        "bound_fullmatch",
        "bound_findall",
        "bound_literal_findall",
        "bound_finditer",
        "bound_scanner",
        "bound_split",
        "bound_sub",
        "bound_subn",
    )
    for name in names:
        function = getattr(bridge, name)
        for shape, action in (
            ("no-arguments", lambda f=function: f()),
            ("one-argument", lambda f=function: f(None)),
            ("unexpected-keyword", lambda f=function: f(unknown=1)),
        ):
            result = attempted(action)
            safe = (
                result.get("status") == "error"
                and result.get("error", {}).get("type") == "TypeError"
            )
            recovery = attempted(lambda: module.fullmatch("a", "a"))
            safe = safe and recovery.get("status") == "value"
            entry = {
                "id": f"private-native-binder/{name}/{shape}",
                "passed": safe,
                "result": result,
                "recovery": recovery,
            }
            observations.append(entry)
            if not safe:
                failures.append(entry)
    for shape, action in (
        ("missing", lambda: bridge.bind()),
        ("one-argument", lambda: bridge.bind(len)),
        ("noncallable", lambda: bridge.bind(None, object())),
    ):
        result = attempted(action)
        safe = (
            result.get("status") == "error"
            and result.get("error", {}).get("type") == "TypeError"
        )
        entry = {
            "id": f"private-native-binder/bind/{shape}",
            "passed": safe,
            "result": result,
            "recovery": attempted(lambda: module.fullmatch("a", "a")),
        }
        observations.append(entry)
        if not safe:
            failures.append(entry)
    compiled = module.compile("a")
    binding = bridge.bind(len, compiled, ())
    valid = attempted(lambda: binding("abc"))
    entry = {
        "id": "private-native-binder/bind/vectorcall-success",
        "passed": valid == {"status": "value", "value": 3},
        "result": valid,
        "recovery": attempted(lambda: module.fullmatch("a", "a")),
    }
    observations.append(entry)
    if not entry["passed"]:
        failures.append(entry)
    return observations, failures


def worker(role, requested_case, edge_oracle=None):
    if tuple(sys.version_info[:3]) != PINNED:
        raise AssertionError("requires pinned CPython 3.14.6")
    if edge_oracle is not None and role != "candidate":
        raise AssertionError("edge provenance can authorize only the canonical candidate")
    cases = build_cases()
    fixture = value_digest(cases)
    if fixture != FROZEN_FIXTURE_SHA256:
        raise AssertionError("frozen observability fixture changed")
    if requested_case is not None:
        cases = [case for case in cases if case["id"] == requested_case]
        if len(cases) != 1:
            raise AssertionError("reproduction did not select exactly one case")
    artifacts = []
    guards = []
    edge_provenance = None
    expected_artifacts = None
    if role in ("stdlib-a", "stdlib-b"):
        module = importlib.import_module("re")
        if "cpython-3.14.6" not in str(Path(module.__file__).resolve()):
            raise AssertionError("reference re is not the pinned standard library")
    elif role == "candidate":
        if edge_oracle is not None:
            edge_provenance, expected_artifacts = validate_edge_oracle(edge_oracle)
        module = importlib.import_module("candidates.rust_candidate")
        artifacts = production_provenance(module, expected_artifacts)
        guards = install_regex_guards()
    else:
        raise AssertionError("unknown isolated observability worker")
    observations = []
    diagnostics = []
    family_counts = collections.Counter()
    for case in cases:
        observation, diagnostic = dispatch_case(module, case)
        normalized = normalize(observation)
        observations.append(
            {
                "id": case["id"],
                "family": case["family"],
                "sha256": value_digest(normalized),
                "observation": normalized,
            }
        )
        if diagnostic:
            diagnostics.append(
                {
                    "id": case["id"],
                    "family": case["family"],
                    "diagnostic": normalize(diagnostic),
                }
            )
        family_counts[case["family"]] += 1
    private_observations = []
    private_failures = []
    guard_observations = []
    rejected_controls = []
    if role == "candidate" and requested_case is None:
        private_observations, private_failures = private_binder_safety(module)
        rejected_controls = rejected_iterator_controls(module)
        guard_observations = audit_regex_guards(guards)
        artifacts = production_provenance(module, expected_artifacts)
        if any(
            getattr(owner, name).__name__ != "forbidden"
            for owner, name in guards
        ):
            raise AssertionError("a standard-library regex guard was removed")
    elif requested_case is None:
        rejected_controls = rejected_iterator_controls(module)
    return {
        "schema": SCHEMA,
        "role": role,
        "python": "3.14.6",
        "seed": SEED,
        "fixture_sha256": fixture,
        "checks": len(observations),
        "family_counts": dict(sorted(family_counts.items())),
        "observations": observations,
        "observation_sha256": value_digest(observations),
        "acceptable_engine_specific_diagnostics": diagnostics,
        "private_binder_checks": len(private_observations),
        "private_binder_failures": private_failures,
        "private_binder_observations": private_observations,
        "forbidden_regex_guards": len(guards),
        "forbidden_regex_guard_observations": guard_observations,
        "rejected_iterator_controls": rejected_controls,
        "native_artifacts": artifacts,
        **({"edge_oracle": edge_provenance} if edge_provenance is not None else {}),
        "monitoring_available": getattr(sys, "monitoring", None) is not None,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def mismatch_records(left, right):
    expected = {item["id"]: item for item in left}
    actual = {item["id"]: item for item in right}
    failures = []
    for identity in sorted(expected.keys() | actual.keys()):
        one = expected.get(identity)
        two = actual.get(identity)
        if one is None or two is None or one["sha256"] != two["sha256"]:
            failures.append(
                {
                    "id": identity,
                    "family": (
                        one["family"] if one is not None else two["family"]
                    ),
                    "expected_sha256": (
                        one["sha256"] if one is not None else None
                    ),
                    "actual_sha256": (
                        two["sha256"] if two is not None else None
                    ),
                }
            )
    return failures


def write_report(path, value):
    path = path.resolve()
    if path.parent != EVIDENCE.resolve():
        raise AssertionError("observability evidence must remain in candidates/evidence")
    if path.name not in ARCHIVE_NAMES.values():
        raise AssertionError("unrecognized frozen observability evidence name")
    with path.open("wb") as raw:
        with gzip.GzipFile(
            filename="",
            fileobj=raw,
            mode="wb",
            compresslevel=9,
            mtime=0,
        ) as output:
            output.write(canonical(value))
    return path_digest(path)


def read_report(path):
    path = path.resolve()
    if path.parent != EVIDENCE.resolve():
        raise AssertionError("observability evidence escaped candidates/evidence")
    if path.name not in ARCHIVE_NAMES.values():
        raise AssertionError("unrecognized observability archive")
    raw = path.read_bytes()
    if len(raw) < 10 or raw[:2] != b"\x1f\x8b":
        raise AssertionError(f"invalid gzip evidence: {path.name}")
    if raw[3] & 0x08 or raw[4:8] != b"\x00\x00\x00\x00":
        raise AssertionError(f"nondeterministic gzip evidence: {path.name}")
    payload = gzip.decompress(raw)
    report = json.loads(payload)
    if canonical(report) != payload:
        raise AssertionError(f"noncanonical JSON evidence: {path.name}")
    if report.get("schema") != SCHEMA:
        raise AssertionError(f"unexpected evidence schema: {path.name}")
    return report


def run_worker(role, case_id=None, edge_oracle=None):
    if edge_oracle is not None and role != "candidate":
        raise AssertionError("edge provenance cannot authorize a standard-library worker")
    command = [
        sys.executable,
        "-B",
        str(Path(__file__).resolve()),
        "--role",
        role,
    ]
    if case_id is not None:
        command.extend(("--case-id", case_id))
    if edge_oracle is not None:
        command.extend(("--edge-oracle", str(Path(edge_oracle).resolve())))
    environment = os.environ.copy()
    old_pythonpath = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = (
        str(ROOT)
        if not old_pythonpath
        else str(ROOT) + os.pathsep + old_pythonpath
    )
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
        env=environment,
    )
    if result.returncode:
        raise RuntimeError(
            f"{role} worker exited {result.returncode}: {result.stderr[-6000:]}"
        )
    report = json.loads(result.stdout)
    if report["schema"] != SCHEMA or report["role"] != role:
        raise AssertionError("observability worker provenance changed")
    if value_digest(report["observations"]) != report["observation_sha256"]:
        raise AssertionError("observability worker observations changed")
    if report["fixture_sha256"] != FROZEN_FIXTURE_SHA256:
        raise AssertionError("observability worker changed the frozen fixture")
    expected_checks = 1 if case_id is not None else 479
    if report["checks"] != expected_checks:
        raise AssertionError("observability worker changed the frozen denominator")
    if any(
        row["sha256"] != value_digest(row["observation"])
        for row in report["observations"]
    ):
        raise AssertionError("observability worker produced inconsistent public rows")
    if edge_oracle is not None:
        expected_edge, _ = validate_edge_oracle(edge_oracle)
        if report.get("edge_oracle") != expected_edge:
            raise AssertionError("the isolated candidate changed its proven edge build")
    elif "edge_oracle" in report:
        raise AssertionError("unexpected edge authorization changed the frozen baseline")
    return report


def archive_reference(role, report):
    path = EVIDENCE / ARCHIVE_NAMES[role]
    fingerprint = write_report(path, report)
    if read_report(path) != report:
        raise AssertionError(f"observability evidence did not round-trip: {role}")
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": fingerprint,
    }


def private_binder_report(candidate):
    observations = candidate["private_binder_observations"]
    failures = candidate["private_binder_failures"]
    guards = candidate["forbidden_regex_guard_observations"]
    if len(observations) != 34:
        raise AssertionError("private native-binder denominator changed")
    if len(guards) != 13 or any(not item["passed"] for item in guards):
        raise AssertionError("standard-library regex poison controls failed")
    return {
        "schema": SCHEMA,
        "role": "private-binders",
        "status": "PASS" if not failures else "FAIL",
        "python": "3.14.6",
        "seed": SEED,
        "fixture_sha256": FROZEN_FIXTURE_SHA256,
        "checks": len(observations),
        "failures": failures,
        "observations": observations,
        "observation_sha256": value_digest(observations),
        "forbidden_regex_guards": len(guards),
        "forbidden_regex_guard_observations": guards,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def rejected_iterator_report(expected, actual):
    standard = expected["rejected_iterator_controls"]
    candidate = actual["rejected_iterator_controls"]
    if len(standard) != 2 or len(candidate) != 2:
        raise AssertionError("historical iterator-control denominator changed")
    records = []
    for left, right in zip(standard, candidate, strict=True):
        if left["id"] != right["id"]:
            raise AssertionError("historical iterator control identity changed")
        if left["correct_public_observation"] != right["correct_public_observation"]:
            raise AssertionError("historical iterator control exposed a real failure")
        if (
            left["legacy_private_type_observation"]
            == right["legacy_private_type_observation"]
        ):
            raise AssertionError("historical iterator false positive was not reproduced")
        records.append(
            {
                "id": left["id"],
                "classification": "REJECTED: private implementation type",
                "standard_private_type": left[
                    "diagnostic_private_iterator_type"
                ],
                "candidate_private_type": right[
                    "diagnostic_private_iterator_type"
                ],
                "legacy_standard_observation": left[
                    "legacy_private_type_observation"
                ],
                "legacy_candidate_observation": right[
                    "legacy_private_type_observation"
                ],
                "standard_public_observation": left[
                    "correct_public_observation"
                ],
                "candidate_public_observation": right[
                    "correct_public_observation"
                ],
            }
        )
    return {
        "schema": SCHEMA,
        "role": "rejected-iterator-control",
        "status": "PASS: explained and rejected",
        "python": "3.14.6",
        "seed": SEED,
        "fixture_sha256": FROZEN_FIXTURE_SHA256,
        "checks": len(records),
        "genuine_public_mismatches": 0,
        "historical_private_control": {
            "schema": "rebar-private-cpython-ffi-observability-v1",
            "script_sha256": (
                "4ece0328780bd81d27bb25a1b7bea26d"
                "440a4d7b758816078e54d8021048a02a"
            ),
            "report_sha256": (
                "d6c2c44cd0768429f8a4066cc6a52f44"
                "00fa0ac2c88c7d64ed41751c67e630c3"
            ),
            "reported_false_positives": 2,
        },
        "observations": records,
        "observation_sha256": value_digest(records),
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def announce(value):
    print(json.dumps(value, ensure_ascii=True, sort_keys=True), flush=True)


def edge_provenance_self_test():
    baseline = frozen_edge_baseline()
    if path_digest(EDGE_FROZEN_CANDIDATE) != EDGE_FROZEN_CANDIDATE_SHA256:
        raise AssertionError("the frozen canonical Rust edge control changed")
    _, original = read_edge_archive(EDGE_FROZEN_CANDIDATE)
    validate_edge_document(
        original,
        baseline,
        check_live_files=False,
        expected_artifacts=PRODUCTION_ARTIFACTS,
    )

    def duplicate_role(report):
        report["candidate_artifacts"][1] = dict(report["candidate_artifacts"][0])

    def missing_role(report):
        report["candidate_artifacts"].pop()

    def stale_hash(report):
        report["candidate_artifacts"][0]["sha256"] = "0" * 64

    def swapped_path(report):
        first = report["candidate_artifacts"][0]
        second = report["candidate_artifacts"][1]
        first["path"], second["path"] = second["path"], first["path"]

    def wrong_reference(report):
        report["expected_sha256"] = "0" * 64

    def wrong_source(report):
        report["script_sha256"] = "0" * 64

    def wrong_candidate(report):
        report["module"] = "candidates.zig_candidate"

    def weakened_categories(report):
        identity = next(iter(report["categories"]))
        report["categories"][identity] -= 1

    mutations = (
        ("missing-artifact-role", missing_role),
        ("duplicate-artifact-role", duplicate_role),
        ("stale-artifact-hash", stale_hash),
        ("swapped-artifact-path", swapped_path),
        ("wrong-reference-digest", wrong_reference),
        ("wrong-edge-source", wrong_source),
        ("wrong-candidate-module", wrong_candidate),
        ("weakened-edge-categories", weakened_categories),
    )
    observations = []
    for label, mutate in mutations:
        corrupted = json.loads(json.dumps(original, ensure_ascii=True))
        mutate(corrupted)
        try:
            validate_edge_document(
                corrupted,
                baseline,
                check_live_files=False,
                expected_artifacts=PRODUCTION_ARTIFACTS,
            )
        except AssertionError as error:
            observations.append(
                {"id": label, "passed": True, "rejection": str(error)}
            )
        else:
            raise AssertionError(f"invalid edge evidence was accepted: {label}")

    missing = EVIDENCE / "rust-v7-edge-oracle-missing-observability-control.json.gz"
    try:
        validate_edge_oracle(missing)
    except AssertionError as error:
        observations.append(
            {"id": "missing-edge-report", "passed": True, "rejection": str(error)}
        )
    else:
        raise AssertionError("a missing edge correctness report was accepted")

    rejected = read_report(EVIDENCE / ARCHIVE_NAMES["rejected-iterator-control"])
    expected_ids = {
        "malicious-public-binder/finditer/shape=end-index/mode=value",
        "malicious-public-binder/finditer/shape=index/mode=value",
    }
    rows = rejected.get("observations", [])
    if (
        rejected.get("checks") != 2
        or rejected.get("genuine_public_mismatches") != 0
        or {row.get("id") for row in rows} != expected_ids
    ):
        raise AssertionError("the frozen iterator false-positive controls changed")
    if any(
        row["standard_public_observation"] != row["candidate_public_observation"]
        or row["legacy_standard_observation"]
        == row["legacy_candidate_observation"]
        for row in rows
    ):
        raise AssertionError("a frozen iterator false positive was misclassified")
    observations.append(
        {
            "id": "frozen-iterator-private-class-false-positives",
            "passed": True,
            "replayed": 2,
        }
    )
    return observations


def run_self_test():
    standard_a = run_worker("stdlib-a")
    standard_b = run_worker("stdlib-b")
    failures = mismatch_records(
        standard_a["observations"], standard_b["observations"]
    )
    provenance_controls = edge_provenance_self_test()
    summary = {
        "schema": SCHEMA,
        "phase": "self-test",
        "status": "PASS" if not failures else "FAIL",
        "python": "3.14.6",
        "seed": SEED,
        "fixture_sha256": FROZEN_FIXTURE_SHA256,
        "independent_standard_library_controls": 2,
        "checks_per_control": standard_a["checks"],
        "failures": failures,
        "observation_sha256": standard_a["observation_sha256"],
        "monitoring_available": standard_a["monitoring_available"],
        "edge_provenance_controls": provenance_controls,
        "edge_provenance_control_failures": 0,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    announce(summary)
    return int(bool(failures))


def run_candidate_gate(edge_oracle=None):
    edge_provenance = None
    if edge_oracle is not None:
        edge_provenance, _ = validate_edge_oracle(edge_oracle)
    expected = run_worker("stdlib-a")
    actual = run_worker("candidate", edge_oracle=edge_oracle)
    failures = mismatch_records(expected["observations"], actual["observations"])
    private_failures = actual["private_binder_failures"]
    guards = actual["forbidden_regex_guard_observations"]
    if len(guards) != 13 or any(not item["passed"] for item in guards):
        raise AssertionError("candidate did not pass every regex-delegation poison")
    rejected = rejected_iterator_report(expected, actual)
    summary = {
        "schema": SCHEMA,
        "phase": "candidate-gate",
        "status": "PASS" if not failures and not private_failures else "FAIL",
        "python": "3.14.6",
        "seed": SEED,
        "fixture_sha256": FROZEN_FIXTURE_SHA256,
        "checks": actual["checks"],
        "failures": failures,
        "private_binder_checks": actual["private_binder_checks"],
        "private_binder_failures": private_failures,
        "forbidden_regex_guards": len(guards),
        "reproduced_rejected_iterator_controls": rejected["checks"],
        "expected_observation_sha256": expected["observation_sha256"],
        "actual_observation_sha256": actual["observation_sha256"],
        "native_artifacts": actual["native_artifacts"],
        **({"edge_oracle": edge_provenance} if edge_provenance is not None else {}),
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    announce(summary)
    return int(bool(failures or private_failures))


def orchestrate():
    if tuple(sys.version_info[:3]) != PINNED:
        raise AssertionError("requires pinned CPython 3.14.6")
    if not EVIDENCE.is_dir():
        raise AssertionError("candidates/evidence must already exist")
    print(
        json.dumps(
            {
                "phase": "start",
                "schema": SCHEMA,
                "seed": SEED,
                "cases": len(build_cases()),
                "fixture_sha256": FROZEN_FIXTURE_SHA256,
                "performance": "NOT MEASURED",
                "holdout": "NOT ACCESSED",
            },
            sort_keys=True,
        ),
        flush=True,
    )
    reports = {}
    archives = {}
    for role in ("stdlib-a", "stdlib-b", "candidate"):
        print(json.dumps({"phase": f"{role}-start"}), flush=True)
        report = run_worker(role)
        archives[role] = archive_reference(role, report)
        reports[role] = report
        print(
            json.dumps(
                {
                    "phase": f"{role}-complete",
                    "checks": report["checks"],
                    "observation_sha256": report["observation_sha256"],
                    "private_binder_checks": report["private_binder_checks"],
                    "private_binder_failures": len(
                        report["private_binder_failures"]
                    ),
                    "forbidden_regex_guards": report["forbidden_regex_guards"],
                },
                sort_keys=True,
            ),
            flush=True,
        )
        if role == "stdlib-b":
            failures = mismatch_records(
                reports["stdlib-a"]["observations"],
                reports["stdlib-b"]["observations"],
            )
            if failures:
                announce(
                    {
                        "phase": "self-oracle-failed",
                        "failed": len(failures),
                        "failures": failures,
                    }
                )
                return 2
            print(
                json.dumps(
                    {
                        "phase": "self-oracle",
                        "checks": reports["stdlib-a"]["checks"],
                        "failures": 0,
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
    expected = reports["stdlib-a"]
    actual = reports["candidate"]
    failures = mismatch_records(
        expected["observations"],
        actual["observations"],
    )
    print(
        json.dumps(
            {
                "phase": "public-differential",
                "checks": actual["checks"],
                "failed": len(failures),
                "first_failure": failures[0] if failures else None,
                "private_binder_checks": actual["private_binder_checks"],
                "private_binder_failures": len(actual["private_binder_failures"]),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    reproduced = []
    for failure in failures[:16]:
        reproduced.append(
            {
                "id": failure["id"],
                "expected": run_worker("stdlib-a", failure["id"]),
                "actual": run_worker("candidate", failure["id"]),
            }
        )
    private = private_binder_report(actual)
    rejected = rejected_iterator_report(expected, actual)
    archives["private-binders"] = archive_reference("private-binders", private)
    archives["rejected-iterator-control"] = archive_reference(
        "rejected-iterator-control", rejected
    )
    summary = {
        "schema": SCHEMA,
        "role": "manifest",
        "status": (
            "PASS"
            if not failures and not actual["private_binder_failures"]
            else "FAIL"
        ),
        "python": "3.14.6",
        "seed": SEED,
        "fixture_sha256": expected["fixture_sha256"],
        "checks": expected["checks"],
        "self_oracle_checks": expected["checks"],
        "self_oracle_failures": 0,
        "candidate_checks": actual["checks"],
        "candidate_failures": len(failures),
        "candidate_failures_by_family": dict(
            sorted(collections.Counter(item["family"] for item in failures).items())
        ),
        "failures": failures,
        "failure_reproductions": reproduced,
        "family_counts": expected["family_counts"],
        "seeded_cases": sum(
            count
            for family, count in expected["family_counts"].items()
            if family.startswith("seeded-")
        ),
        "monitoring_available": expected["monitoring_available"],
        "private_binder_checks": actual["private_binder_checks"],
        "private_binder_failures": actual["private_binder_failures"],
        "forbidden_regex_guards": actual["forbidden_regex_guards"],
        "expected_observation_sha256": expected["observation_sha256"],
        "actual_observation_sha256": actual["observation_sha256"],
        "acceptable_engine_specific_diagnostic_counts": {
            "stdlib": len(expected["acceptable_engine_specific_diagnostics"]),
            "candidate": len(actual["acceptable_engine_specific_diagnostics"]),
        },
        "classification": {
            "public_profile_callbacks": "compared",
            "public_builtin_c_events": "compared",
            "public_monitoring_callbacks": "compared",
            "callback_recursion_outcome_and_recovery": "compared",
            "public_finditer_matches_protocol_and_exhaustion": "compared",
            "private_finditer_iterator_class_name": "diagnostic-only",
            "internal_sre_and_rust_bridge_c_frames": "diagnostic-only",
            "recursion_depth_in_internal_engine_frames": "diagnostic-only",
            "private_rust_binder": "candidate-only safety obligation",
        },
        "preserved_rejected_control": {
            "archive": archives["rejected-iterator-control"],
            "checks": rejected["checks"],
            "genuine_public_mismatches": rejected[
                "genuine_public_mismatches"
            ],
            "historical_private_control": rejected[
                "historical_private_control"
            ],
            "classification": (
                "rejected harness control: implementation-private iterator "
                "class names are not a public re compatibility requirement"
            ),
        },
        "native_artifacts": actual["native_artifacts"],
        "forbidden_regex_guard_observations": actual[
            "forbidden_regex_guard_observations"
        ],
        "isolated_worker_archives": archives,
        "script": {
            "path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
            "sha256": path_digest(Path(__file__).resolve()),
        },
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    fingerprint = write_report(EVIDENCE / ARCHIVE_NAMES["manifest"], summary)
    if read_report(EVIDENCE / ARCHIVE_NAMES["manifest"]) != summary:
        raise AssertionError("observability manifest did not exactly round-trip")
    print(
        json.dumps(
            {
                "phase": "complete",
                "status": summary["status"],
                "checks": summary["checks"],
                "candidate_failures": summary["candidate_failures"],
                "candidate_failures_by_family": (
                    summary["candidate_failures_by_family"]
                ),
                "self_oracle_failures": 0,
                "private_binder_checks": summary["private_binder_checks"],
                "private_binder_failures": len(
                    summary["private_binder_failures"]
                ),
                "monitoring_available": summary["monitoring_available"],
                "forbidden_regex_guards": summary["forbidden_regex_guards"],
                "expected_observation_sha256": (
                    summary["expected_observation_sha256"]
                ),
                "actual_observation_sha256": summary["actual_observation_sha256"],
                "report": (
                    (EVIDENCE / ARCHIVE_NAMES["manifest"])
                    .relative_to(ROOT)
                    .as_posix()
                ),
                "report_sha256": fingerprint,
                "holdout": "NOT ACCESSED",
                "performance": "NOT MEASURED",
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return int(
        bool(failures or actual["private_binder_failures"])
    )


def verify_evidence():
    if tuple(sys.version_info[:3]) != PINNED:
        raise AssertionError("requires pinned CPython 3.14.6")
    if value_digest(build_cases()) != FROZEN_FIXTURE_SHA256:
        raise AssertionError("frozen public-observability cases changed")
    manifest_path = EVIDENCE / ARCHIVE_NAMES["manifest"]
    manifest = read_report(manifest_path)
    if manifest.get("role") != "manifest" or manifest.get("status") != "PASS":
        raise AssertionError("observability manifest is not a passing gate")
    if manifest.get("seed") != SEED:
        raise AssertionError("observability manifest seed drifted")
    if manifest.get("fixture_sha256") != FROZEN_FIXTURE_SHA256:
        raise AssertionError("observability manifest fixture drifted")
    if manifest.get("checks") != 479 or manifest.get("candidate_checks") != 479:
        raise AssertionError("observability manifest denominator changed")
    if manifest.get("self_oracle_checks") != 479:
        raise AssertionError("observability self-oracle denominator changed")
    if manifest.get("self_oracle_failures") or manifest.get("candidate_failures"):
        raise AssertionError("observability manifest contains compatibility failures")
    source = manifest.get("script", {})
    if source.get("path") != "tools/rust_v7_observability_oracle.py":
        raise AssertionError("observability source provenance changed")
    if source.get("sha256") != path_digest(Path(__file__).resolve()):
        raise AssertionError("observability source hash changed")

    archives = {}
    expected_roles = {
        "stdlib-a",
        "stdlib-b",
        "candidate",
        "private-binders",
        "rejected-iterator-control",
    }
    references = manifest.get("isolated_worker_archives", {})
    if set(references) != expected_roles:
        raise AssertionError("observability evidence archive set changed")
    for role in sorted(expected_roles):
        path = EVIDENCE / ARCHIVE_NAMES[role]
        reference = references[role]
        if reference.get("path") != path.relative_to(ROOT).as_posix():
            raise AssertionError(f"observability archive path drifted: {role}")
        if reference.get("sha256") != path_digest(path):
            raise AssertionError(f"observability archive digest drifted: {role}")
        report = read_report(path)
        if report.get("role") != role:
            raise AssertionError(f"observability archive role drifted: {role}")
        if report.get("seed") != SEED:
            raise AssertionError(f"observability archive seed drifted: {role}")
        if report.get("fixture_sha256") != FROZEN_FIXTURE_SHA256:
            raise AssertionError(f"observability archive fixture drifted: {role}")
        archives[role] = report

    cases = build_cases()
    expected_ids = [case["id"] for case in cases]
    for role in ("stdlib-a", "stdlib-b", "candidate"):
        report = archives[role]
        rows = report["observations"]
        if report.get("checks") != 479 or len(rows) != 479:
            raise AssertionError(f"observability rows incomplete: {role}")
        if [row["id"] for row in rows] != expected_ids:
            raise AssertionError(f"observability case identity changed: {role}")
        if any(
            row["sha256"] != value_digest(row["observation"])
            for row in rows
        ):
            raise AssertionError(f"observability row digest changed: {role}")
        if value_digest(rows) != report.get("observation_sha256"):
            raise AssertionError(f"observability full archive digest changed: {role}")

    standard_a = archives["stdlib-a"]
    standard_b = archives["stdlib-b"]
    candidate = archives["candidate"]
    if mismatch_records(standard_a["observations"], standard_b["observations"]):
        raise AssertionError("independent standard-library controls disagree")
    if mismatch_records(standard_a["observations"], candidate["observations"]):
        raise AssertionError("candidate does not match the public baseline")
    if manifest["expected_observation_sha256"] != standard_a[
        "observation_sha256"
    ]:
        raise AssertionError("manifest expected observation digest changed")
    if manifest["actual_observation_sha256"] != candidate[
        "observation_sha256"
    ]:
        raise AssertionError("manifest candidate observation digest changed")

    private = archives["private-binders"]
    if private.get("status") != "PASS" or private.get("checks") != 34:
        raise AssertionError("private native-binder controls do not pass")
    if private.get("failures") or candidate.get("private_binder_failures"):
        raise AssertionError("private native-binder failure was hidden")
    if private["observations"] != candidate["private_binder_observations"]:
        raise AssertionError("private native-binder archive does not match candidate")
    if value_digest(private["observations"]) != private["observation_sha256"]:
        raise AssertionError("private native-binder evidence digest changed")
    guards = candidate["forbidden_regex_guard_observations"]
    if len(guards) != 13 or any(not row["passed"] for row in guards):
        raise AssertionError("a regex-delegation poison control failed")
    if private["forbidden_regex_guard_observations"] != guards:
        raise AssertionError("regex-delegation poison archive changed")

    rejected = archives["rejected-iterator-control"]
    if rejected != rejected_iterator_report(standard_a, candidate):
        raise AssertionError("rejected iterator control is incomplete or changed")
    if rejected["genuine_public_mismatches"] != 0:
        raise AssertionError("a genuine public iterator mismatch was hidden")

    if len(candidate["native_artifacts"]) != 5:
        raise AssertionError("production native-artifact denominator changed")
    baseline = frozen_edge_baseline()
    if path_digest(EDGE_FROZEN_CANDIDATE) != EDGE_FROZEN_CANDIDATE_SHA256:
        raise AssertionError("the immutable canonical baseline edge report changed")
    _, edge_candidate = read_edge_archive(EDGE_FROZEN_CANDIDATE)
    frozen_artifacts = validate_edge_document(
        edge_candidate,
        baseline,
        check_live_files=False,
        expected_artifacts=PRODUCTION_ARTIFACTS,
    )
    expected_artifact_rows = [
        {
            "role": role,
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": fingerprint,
        }
        for role, (path, fingerprint) in sorted(frozen_artifacts.items())
    ]
    if candidate["native_artifacts"] != expected_artifact_rows:
        raise AssertionError("archived production provenance differs from frozen baseline")
    if candidate["native_artifacts"] != manifest["native_artifacts"]:
        raise AssertionError("manifest native provenance does not match candidate")

    announce(
        {
            "schema": SCHEMA,
            "phase": "verify",
            "status": "PASS",
            "python": "3.14.6",
            "seed": SEED,
            "fixture_sha256": FROZEN_FIXTURE_SHA256,
            "independent_standard_library_controls": 2,
            "checks": 479,
            "self_oracle_failures": 0,
            "candidate_failures": 0,
            "private_binder_checks": 34,
            "private_binder_failures": 0,
            "forbidden_regex_guards": 13,
            "rejected_iterator_false_positives": 2,
            "genuine_public_iterator_mismatches": 0,
            "observation_sha256": candidate["observation_sha256"],
            "manifest_sha256": path_digest(manifest_path),
            "baseline_edge_oracle_sha256": EDGE_FROZEN_CANDIDATE_SHA256,
            "baseline_native_provenance": "verified from immutable archived evidence",
            "performance": "NOT MEASURED",
            "holdout": "NOT ACCESSED",
        }
    )
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        nargs="?",
        choices=("write", "verify", "candidate"),
        default="write",
        help="write deterministic evidence, verify it, or run the live candidate gate",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="compare two independently isolated pinned standard-library controls",
    )
    parser.add_argument(
        "--candidate",
        action="store_true",
        help="run the complete isolated live candidate compatibility gate",
    )
    parser.add_argument(
        "--edge-oracle",
        type=Path,
        help=(
            "authorize the actual canonical candidate using an independently "
            "passing frozen 223,198-case Rust edge-correctness report"
        ),
    )
    parser.add_argument(
        "--role",
        choices=("stdlib-a", "stdlib-b", "candidate"),
        help=argparse.SUPPRESS,
    )
    parser.add_argument("--case-id", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.role is not None:
        if args.self_test or args.candidate or args.command != "write":
            parser.error("an isolated worker cannot select another gate")
        if args.edge_oracle is not None and args.role != "candidate":
            parser.error("--edge-oracle can authorize only the canonical candidate")
        report = worker(args.role, args.case_id, args.edge_oracle)
        sys.stdout.write(json.dumps(report, ensure_ascii=True, sort_keys=True))
        sys.stdout.write("\n")
        return 0
    if args.case_id is not None:
        parser.error("--case-id requires an isolated worker")
    if args.self_test:
        if args.candidate or args.command != "write" or args.edge_oracle is not None:
            parser.error("--self-test cannot be combined with another gate")
        return run_self_test()
    if args.candidate:
        if args.command != "write":
            parser.error("--candidate cannot be combined with another gate")
        return run_candidate_gate(args.edge_oracle)
    if args.command == "verify":
        if args.edge_oracle is not None:
            parser.error("--edge-oracle must not change immutable baseline verification")
        return verify_evidence()
    if args.command == "candidate":
        return run_candidate_gate(args.edge_oracle)
    if args.edge_oracle is not None:
        parser.error("--edge-oracle requires the canonical candidate gate")
    return orchestrate()


if __name__ == "__main__":
    raise SystemExit(main())
