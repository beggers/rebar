#!/usr/bin/env python3
"""Independently frozen, untimed CPython Match.expand buffer oracle."""

from __future__ import annotations

import argparse
import hashlib
import importlib
from importlib.machinery import EXTENSION_SUFFIXES, ExtensionFileLoader
import json
import os
from pathlib import Path
import random
import stat
import subprocess
import sys
from typing import Any, Mapping
import types
import warnings


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/rust_memoryview_expand_differential_v1.py"
PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14",
)
PINNED_STDLIB_RE = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
    "lib/python3.14/re/__init__.py",
)
SCHEMA = "rebar-independent-rust-memoryview-expand-differential-v1"
PUBLISHED_SEED = 0x4D45_5850_414E_4431
VARIANTS_PER_FAMILY = 32
MATRIX_SHA256 = (
    "b40fb92f42c7019a73eec72800077f262f1a6be516886a6ddda372e24807eb60"
)
BASELINE_SHA256 = (
    "8312263785cd49f7283ab8c6fac13443befe9c5a3d739b2e068aebdcf3f59b75"
)
MAX_WORKER_BYTES = 32 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
IGNORECASE = 2
ASCII = 256
FAMILIES = (
    "measured-mutable-memoryview",
    "measured-readonly-memoryview",
    "sliced-mutable-memoryview",
    "sliced-readonly-memoryview",
    "strided-mutable-memoryview",
    "strided-readonly-memoryview",
    "released-before-search",
    "released-after-match",
    "bytearray-control",
    "bytes-control",
    "empty-mutable-memoryview",
    "empty-readonly-memoryview",
    "named-capture-template",
    "numbered-capture-template",
    "octal-escape-template",
    "escaped-backslash-template",
    "unmatched-optional-capture",
    "missing-numbered-capture",
    "missing-named-capture",
    "malformed-escape-template",
    "wrong-template-type",
    "unicode-text-separation",
    "mutable-source-after-match",
    "buffer-exporter-error",
)
CASE_COUNT = len(FAMILIES) * VARIANTS_PER_FAMILY

if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))


class ExpandOracleError(Exception):
    """Reject omitted, forged, timed, or non-isolated expand observations."""


class ExplodingBuffer:
    def __buffer__(self, flags: int) -> memoryview:
        raise BufferError("frozen public expand buffer exporter failure")

    def __release_buffer__(self, view: memoryview) -> None:
        return None


def require(condition: Any, message: str) -> None:
    if not condition:
        raise ExpandOracleError(message)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii") + b"\n"


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def valid_digest(value: Any) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and len(set(value)) > 1
        and all(letter in "0123456789abcdef" for letter in value)
    )


def unique_json_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    actual: dict[str, Any] = {}
    for key, value in items:
        require(
            type(key) is str and key not in actual,
            "duplicate genuine Match.expand evidence is forbidden",
        )
        actual[key] = value
    return actual


def decode_canonical(raw: Any, label: str) -> dict[str, Any]:
    require(
        type(raw) is bytes and 0 < len(raw) <= MAX_WORKER_BYTES,
        "complete bounded original Match.expand worker output is required: "
        + label,
    )
    try:
        actual = json.loads(
            raw,
            object_pairs_hook=unique_json_object,
            parse_constant=lambda value: (_ for _ in ()).throw(
                ExpandOracleError("nonfinite Match.expand evidence is forbidden"),
            ),
        )
    except (TypeError, ValueError, UnicodeError, json.JSONDecodeError) as error:
        raise ExpandOracleError(
            "invalid genuine Match.expand worker evidence: " + label,
        ) from error
    require(
        type(actual) is dict and canonical(actual) == raw,
        "complete original Match.expand worker evidence was substituted",
    )
    return actual


def encode_bytes(value: bytes) -> dict[str, str]:
    require(type(value) is bytes, "an exact original bytes payload is mandatory")
    return {"kind": "bytes", "hex": value.hex()}


def encode_text(value: str) -> dict[str, str]:
    require(type(value) is str, "an exact original text payload is mandatory")
    return {"kind": "str", "value": value}


def encode_carrier(
    kind: str,
    payload: bytes,
    *,
    start: int = 0,
    stop: int | None = None,
    step: int = 1,
) -> dict[str, Any]:
    require(
        kind
        in (
            "bytes",
            "bytearray",
            "readonly-memoryview",
            "mutable-memoryview",
            "exploding-buffer",
        ),
        "an unfrozen expand carrier was injected",
    )
    require(type(payload) is bytes, "the original carrier bytes were substituted")
    return {
        "kind": kind,
        "hex": payload.hex(),
        "start": start,
        "stop": len(payload) if stop is None else stop,
        "step": step,
    }


def encode_template(value: Any) -> dict[str, Any]:
    if type(value) is bytes:
        return encode_bytes(value)
    if type(value) is str:
        return encode_text(value)
    if type(value) is int:
        return {"kind": "int", "value": value}
    if type(value) is list:
        return {"kind": "list", "items": [encode_template(item) for item in value]}
    if type(value) is bytearray:
        return {"kind": "bytearray", "hex": bytes(value).hex()}
    if type(value) is memoryview:
        return {
            "kind": "template-memoryview",
            "hex": value.tobytes().hex(),
            "readonly": value.readonly,
        }
    if type(value) is ExplodingBuffer:
        return {"kind": "exploding-buffer"}
    raise ExpandOracleError("an original Match.expand template was substituted")


def decode_bytes(value: Any) -> bytes:
    require(
        type(value) is dict
        and set(value) == {"kind", "hex"}
        and value.get("kind") == "bytes"
        and type(value.get("hex")) is str,
        "an original Match.expand bytes payload was forged",
    )
    try:
        actual = bytes.fromhex(value["hex"])
    except ValueError as error:
        raise ExpandOracleError("a frozen Match.expand bytes payload is invalid") from error
    require(
        actual.hex() == value["hex"],
        "a noncanonical Match.expand bytes payload was injected",
    )
    return actual


def decode_pattern(value: Any) -> str | bytes:
    require(type(value) is dict, "a frozen Match.expand pattern is mandatory")
    if value.get("kind") == "str":
        require(
            set(value) == {"kind", "value"} and type(value.get("value")) is str,
            "an original Match.expand Unicode pattern was substituted",
        )
        return value["value"]
    return decode_bytes(value)


def decode_carrier(value: Any) -> tuple[Any, bytearray | None]:
    require(
        type(value) is dict
        and set(value) == {"kind", "hex", "start", "stop", "step"},
        "the complete original Match.expand carrier is mandatory",
    )
    kind = value["kind"]
    require(
        kind
        in (
            "bytes",
            "bytearray",
            "readonly-memoryview",
            "mutable-memoryview",
            "exploding-buffer",
        )
        and type(value["hex"]) is str
        and type(value["start"]) is int
        and type(value["stop"]) is int
        and type(value["step"]) is int
        and value["step"] in (1, 2),
        "the actual memoryview shape or mutability was substituted",
    )
    try:
        payload = bytes.fromhex(value["hex"])
    except ValueError as error:
        raise ExpandOracleError("an original Match.expand carrier is invalid") from error
    require(
        payload.hex() == value["hex"]
        and 0 <= value["start"] <= value["stop"] <= len(payload),
        "the original Match.expand carrier bounds were corrupted",
    )
    if kind == "exploding-buffer":
        return ExplodingBuffer(), None
    if kind == "bytes":
        return payload[value["start"] : value["stop"] : value["step"]], None
    if kind == "bytearray":
        actual = bytearray(payload)
        return actual[value["start"] : value["stop"] : value["step"]], None
    if kind == "readonly-memoryview":
        return (
            memoryview(payload)[value["start"] : value["stop"] : value["step"]],
            None,
        )
    backing = bytearray(payload)
    return (
        memoryview(backing)[value["start"] : value["stop"] : value["step"]],
        backing,
    )


def decode_template(value: Any) -> Any:
    require(type(value) is dict, "the original Match.expand template is mandatory")
    kind = value.get("kind")
    if kind == "bytes":
        return decode_bytes(value)
    if kind == "str":
        require(
            set(value) == {"kind", "value"} and type(value.get("value")) is str,
            "an original Unicode Match.expand template was substituted",
        )
        return value["value"]
    if kind == "int":
        require(
            set(value) == {"kind", "value"} and type(value.get("value")) is int,
            "an original wrong-type template was substituted",
        )
        return value["value"]
    if kind == "list":
        require(
            set(value) == {"kind", "items"} and type(value.get("items")) is list,
            "an original unhashable template was substituted",
        )
        return [decode_template(item) for item in value["items"]]
    if kind in ("bytearray", "template-memoryview"):
        require(
            type(value.get("hex")) is str,
            "an original bytes-like replacement was substituted",
        )
        try:
            actual = bytes.fromhex(value["hex"])
        except ValueError as error:
            raise ExpandOracleError("an original replacement buffer is invalid") from error
        require(
            actual.hex() == value["hex"],
            "a noncanonical original replacement buffer was injected",
        )
        if kind == "bytearray":
            require(set(value) == {"kind", "hex"}, "a bytearray template changed")
            return bytearray(actual)
        require(
            set(value) == {"kind", "hex", "readonly"}
            and type(value.get("readonly")) is bool,
            "a replacement memoryview lost its readonly state",
        )
        return memoryview(actual if value["readonly"] else bytearray(actual))
    if kind == "exploding-buffer":
        require(set(value) == {"kind"}, "a public failing buffer was substituted")
        return ExplodingBuffer()
    raise ExpandOracleError("an unfrozen Match.expand replacement was injected")


def build_matrix() -> list[dict[str, Any]]:
    seeded = random.Random(PUBLISHED_SEED)
    cases: list[dict[str, Any]] = []
    for family in FAMILIES:
        for variant in range(VARIANTS_PER_FAMILY):
            noise = "".join(
                seeded.choice("abcdef0123456789") for _ in range(8)
            ).encode("ascii")
            payload = b"alpha42 beta7 !" + noise
            pattern: str | bytes = rb"(?P<word>[A-Za-z]+)(?P<number>\d*)"
            template: Any = rb"<\g<word>>"
            flags = (0, IGNORECASE, ASCII, 0)[variant % 4]
            carrier = encode_carrier("readonly-memoryview", payload)
            mutation = "none"

            if family == "measured-mutable-memoryview":
                carrier = encode_carrier("mutable-memoryview", payload)
            elif family == "measured-readonly-memoryview":
                carrier = encode_carrier("readonly-memoryview", payload)
            elif family in (
                "sliced-mutable-memoryview",
                "sliced-readonly-memoryview",
            ):
                padded = b"<<" + payload + b">>"
                kind = (
                    "mutable-memoryview"
                    if family == "sliced-mutable-memoryview"
                    else "readonly-memoryview"
                )
                carrier = encode_carrier(
                    kind, padded, start=2, stop=len(padded) - 2,
                )
            elif family in (
                "strided-mutable-memoryview",
                "strided-readonly-memoryview",
            ):
                kind = (
                    "mutable-memoryview"
                    if family == "strided-mutable-memoryview"
                    else "readonly-memoryview"
                )
                carrier = encode_carrier(kind, payload, step=2)
            elif family == "released-before-search":
                carrier = encode_carrier(
                    "mutable-memoryview" if variant % 2 else "readonly-memoryview",
                    payload,
                )
                mutation = "release-before-search"
            elif family == "released-after-match":
                carrier = encode_carrier(
                    "mutable-memoryview" if variant % 2 else "readonly-memoryview",
                    payload,
                )
                mutation = "release-after-match"
            elif family == "bytearray-control":
                carrier = encode_carrier("bytearray", payload)
            elif family == "bytes-control":
                carrier = encode_carrier("bytes", payload)
            elif family in (
                "empty-mutable-memoryview",
                "empty-readonly-memoryview",
            ):
                kind = (
                    "mutable-memoryview"
                    if family == "empty-mutable-memoryview"
                    else "readonly-memoryview"
                )
                carrier = encode_carrier(kind, b"")
                pattern = rb"(?P<word>)(?P<number>\d*)"
            elif family == "named-capture-template":
                carrier = encode_carrier(
                    "mutable-memoryview" if variant % 2 else "readonly-memoryview",
                    payload,
                )
                template = (
                    rb"<\g<word>>:\g<number>"
                    if variant % 2
                    else rb"\g<0>|\g<word>|\g<number>"
                )
            elif family == "numbered-capture-template":
                carrier = encode_carrier(
                    "mutable-memoryview" if variant % 2 else "readonly-memoryview",
                    payload,
                )
                template = (rb"<\1>:\2", rb"\g<1>|\g<2>", rb"\g<0>")[variant % 3]
            elif family == "octal-escape-template":
                carrier = encode_carrier(
                    "mutable-memoryview" if variant % 2 else "readonly-memoryview",
                    payload,
                )
                template = (rb"\101-\060-\0", rb"\007\011", rb"\077\100")[variant % 3]
            elif family == "escaped-backslash-template":
                carrier = encode_carrier(
                    "mutable-memoryview" if variant % 2 else "readonly-memoryview",
                    payload,
                )
                template = (rb"\\\g<word>", rb"\t\n\r", rb"\\literal\\")[variant % 3]
            elif family == "unmatched-optional-capture":
                carrier = encode_carrier(
                    "mutable-memoryview" if variant % 2 else "readonly-memoryview",
                    payload,
                )
                pattern = rb"(?P<word>[A-Za-z]+)(?P<number>\d*)(?P<optional>z+)?"
                template = (
                    rb"[\g<optional>]-\g<word>",
                    rb"<\3>-\1",
                )[variant % 2]
            elif family == "missing-numbered-capture":
                carrier = encode_carrier(
                    "mutable-memoryview" if variant % 2 else "readonly-memoryview",
                    payload,
                )
                template = (rb"\9", rb"\g<42>", rb"\3")[variant % 3]
            elif family == "missing-named-capture":
                carrier = encode_carrier(
                    "mutable-memoryview" if variant % 2 else "readonly-memoryview",
                    payload,
                )
                template = (rb"\g<missing>", rb"\g<not_a_group>")[variant % 2]
            elif family == "malformed-escape-template":
                carrier = encode_carrier(
                    "mutable-memoryview" if variant % 2 else "readonly-memoryview",
                    payload,
                )
                template = (b"\\", rb"\g<", rb"\g<>", rb"\x", rb"\400")[
                    variant % 5
                ]
            elif family == "wrong-template-type":
                carrier = encode_carrier(
                    "mutable-memoryview" if variant % 2 else "readonly-memoryview",
                    payload,
                )
                wrong: tuple[Any, ...] = (
                    r"<\g<word>>",
                    17,
                    [b"group"],
                    bytearray(rb"<\g<word>>"),
                    memoryview(rb"<\g<word>>"),
                    memoryview(bytearray(rb"<\g<word>>")),
                )
                template = wrong[variant % len(wrong)]
            elif family == "unicode-text-separation":
                pattern = r"(?P<word>[\w]+)(?P<number>\d*)"
                carrier = encode_text("café42 Δelta7 " + noise.decode("ascii"))
                flags = (0, IGNORECASE, ASCII, 0)[variant % 4]
                template = (
                    r"<\g<word>>",
                    rb"<\g<word>>",
                    r"\1-\g<number>",
                    r"\g<missing>",
                )[variant % 4]
            elif family == "mutable-source-after-match":
                carrier = encode_carrier("mutable-memoryview", payload)
                mutation = (
                    "mutate-captured-byte",
                    "mutate-uncaptured-byte",
                    "resize-exporter",
                )[variant % 3]
                template = (rb"<\g<word>>", rb"\1-\2")[variant % 2]
            elif family == "buffer-exporter-error":
                if variant % 2:
                    carrier = encode_carrier("readonly-memoryview", payload)
                    template = ExplodingBuffer()
                else:
                    carrier = encode_carrier("exploding-buffer", payload)

            encoded_pattern = (
                encode_text(pattern) if type(pattern) is str else encode_bytes(pattern)
            )
            cases.append(
                {
                    "case": "memoryview-expand.v1." + format(len(cases), "04d"),
                    "family": family,
                    "variant": variant,
                    "flags": flags,
                    "pattern": encoded_pattern,
                    "subject": carrier,
                    "template": encode_template(template),
                    "mutation": mutation,
                }
            )
    return cases


def validate_matrix(matrix: Any) -> str:
    require(
        CASE_COUNT == 768
        and len(FAMILIES) == 24
        and VARIANTS_PER_FAMILY == 32,
        "the original Match.expand family denominator silently changed",
    )
    require(
        type(matrix) is list
        and len(matrix) == CASE_COUNT
        and matrix == build_matrix()
        and len({case["case"] for case in matrix}) == CASE_COUNT
        and digest(matrix) == MATRIX_SHA256,
        "every independently seeded Match.expand case is mandatory",
    )
    for family in FAMILIES:
        require(
            sum(case["family"] == family for case in matrix)
            == VARIANTS_PER_FAMILY,
            "an entire Match.expand carrier or template family was omitted: "
            + family,
        )
    return MATRIX_SHA256


def verify_runtime(*, candidate_loaded: bool = False) -> None:
    expected_source = str(ROOT / SOURCE_RELATIVE)
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and bool(sys.path)
        and sys.path[0] == str(ROOT)
        and os.path.realpath(str(ROOT)) == str(ROOT)
        and os.path.abspath(__file__) == expected_source
        and os.path.realpath(__file__) == expected_source
        and os.path.abspath(sys.executable) == str(PINNED_PYTHON)
        and os.path.realpath(sys.executable) == str(PINNED_PYTHON),
        "use only the frozen Match.expand source, root, and CPython 3.14.6",
    )
    if not candidate_loaded:
        require(
            not any(
                name == "candidates" or name.startswith("candidates.")
                for name in sys.modules
            ),
            "a candidate escaped into original-only Match.expand authentication",
        )


def normalize_value(value: Any) -> Any:
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is bytes:
        return {"kind": "bytes", "hex": value.hex()}
    if type(value) is bytearray:
        return {"kind": "bytearray", "hex": bytes(value).hex()}
    if type(value) is memoryview:
        try:
            return {
                "kind": "memoryview",
                "hex": value.tobytes().hex(),
                "readonly": value.readonly,
                "format": value.format,
                "itemsize": value.itemsize,
                "ndim": value.ndim,
                "shape": list(value.shape) if value.shape is not None else None,
                "strides": list(value.strides)
                if value.strides is not None
                else None,
                "contiguous": value.contiguous,
            }
        except ValueError as error:
            return {
                "kind": "released-memoryview",
                "exception": type(error).__qualname__,
                "args": [normalize_value(item) for item in error.args],
            }
    if type(value) in (tuple, list):
        return {
            "kind": "tuple" if type(value) is tuple else "list",
            "items": [normalize_value(item) for item in value],
        }
    if isinstance(value, Mapping):
        return {
            "kind": "mapping",
            "items": [
                [normalize_value(key), normalize_value(item)]
                for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
            ],
        }
    raise ExpandOracleError(
        "an actual public Match.expand observable was hidden: "
        + type(value).__qualname__,
    )


def normalize_pattern(pattern: Any) -> dict[str, Any]:
    groups = pattern.groups
    flags = pattern.flags
    require(
        type(groups) is int
        and groups >= 0
        and type(flags) is int,
        "the original Match.expand compiled-pattern metadata was forged",
    )
    return {
        "pattern": normalize_value(pattern.pattern),
        "flags": flags,
        "groups": groups,
        "groupindex": [
            [name, number]
            for name, number in sorted(dict(pattern.groupindex).items())
        ],
    }


def normalize_match(match: Any) -> dict[str, Any]:
    pattern = match.re
    return {
        "pattern": normalize_pattern(pattern),
        "string": normalize_value(match.string),
        "group": normalize_value(match.group(0)),
        "groups": [normalize_value(item) for item in match.groups()],
        "spans": [
            list(match.span(number)) for number in range(pattern.groups + 1)
        ],
        "lastindex": match.lastindex,
        "lastgroup": match.lastgroup,
        "pos": match.pos,
        "endpos": match.endpos,
    }


def normalize_error(error: Exception, engine: Any) -> dict[str, Any]:
    expected = getattr(engine, "error", None)
    if isinstance(expected, type) and isinstance(error, expected):
        return {
            "kind": "public-regex-error",
            "type": type(error).__qualname__,
            "args": normalize_value(error.args),
            "message": getattr(error, "msg", None),
            "pattern": normalize_value(getattr(error, "pattern", None)),
            "position": getattr(error, "pos", None),
            "line": getattr(error, "lineno", None),
            "column": getattr(error, "colno", None),
        }
    return {
        "kind": "ordinary-python-error",
        "module": type(error).__module__,
        "type": type(error).__qualname__,
        "args": normalize_value(error.args),
    }


def normalize_warnings(observed: Any) -> list[dict[str, str]]:
    require(
        type(observed) is list,
        "the original Match.expand warning sequence is mandatory",
    )
    result: list[dict[str, str]] = []
    for item in observed:
        require(
            isinstance(item.category, type)
            and isinstance(item.message, item.category),
            "an original Match.expand warning was substituted",
        )
        result.append(
            {
                "category_module": item.category.__module__,
                "category": item.category.__qualname__,
                "message": str(item.message),
            }
        )
    return result


def execute_case(case: Mapping[str, Any], engine: Any) -> dict[str, Any]:
    stage = "materialize"
    before: dict[str, Any] | None = None
    source_after: Any = None
    mutation: dict[str, Any] | None = None
    with warnings.catch_warnings(record=True) as actual_warnings:
        warnings.simplefilter("always")
        try:
            pattern = decode_pattern(case["pattern"])
            if case["subject"].get("kind") == "str":
                subject = decode_pattern(case["subject"])
                backing = None
            else:
                subject, backing = decode_carrier(case["subject"])
            template = decode_template(case["template"])
            action = case["mutation"]
            if action == "release-before-search":
                require(
                    type(subject) is memoryview,
                    "only a real memoryview may be released",
                )
                subject.release()
            stage = "compile"
            compiled = engine.compile(pattern, case["flags"])
            stage = "search"
            match = compiled.search(subject)
            if match is None:
                return {
                    "status": "return",
                    "stage": "search",
                    "value": None,
                    "match_before": None,
                    "source_after": normalize_value(subject),
                    "mutation": mutation,
                    "warnings": normalize_warnings(actual_warnings),
                }
            before = normalize_match(match)
            stage = "mutate"
            if action == "release-after-match":
                require(
                    type(subject) is memoryview,
                    "only an original memoryview may be released",
                )
                subject.release()
                mutation = {"kind": action, "released": True}
            elif action == "mutate-captured-byte":
                require(backing is not None, "a real mutable exporter is mandatory")
                start = case["subject"]["start"] + match.start("word")
                previous = backing[start]
                backing[start] = ord("Z") if previous != ord("Z") else ord("Q")
                mutation = {
                    "kind": action,
                    "offset": start,
                    "previous": previous,
                    "current": backing[start],
                }
            elif action == "mutate-uncaptured-byte":
                require(backing is not None, "a real mutable exporter is mandatory")
                start = len(backing) - 1
                previous = backing[start]
                backing[start] = ord("Z") if previous != ord("Z") else ord("Q")
                mutation = {
                    "kind": action,
                    "offset": start,
                    "previous": previous,
                    "current": backing[start],
                }
            elif action == "resize-exporter":
                require(backing is not None, "a real mutable exporter is mandatory")
                try:
                    backing.append(ord("!"))
                except Exception as error:
                    mutation = {
                        "kind": action,
                        "exception": normalize_error(error, engine),
                    }
                else:
                    mutation = {"kind": action, "resized": True}
            else:
                require(action == "none", "an unfrozen source mutation was injected")
            source_after = normalize_value(subject)
            stage = "expand"
            result = match.expand(template)
            return {
                "status": "return",
                "stage": stage,
                "value": normalize_value(result),
                "match_before": before,
                "source_after": source_after,
                "mutation": mutation,
                "warnings": normalize_warnings(actual_warnings),
            }
        except ExpandOracleError:
            raise
        except Exception as error:
            return {
                "status": "raise",
                "stage": stage,
                "exception": normalize_error(error, engine),
                "match_before": before,
                "source_after": source_after,
                "mutation": mutation,
                "warnings": normalize_warnings(actual_warnings),
            }


def authenticate_owned_module(module: Any, *, label: str) -> str:
    origin = getattr(module, "__file__", None)
    require(
        type(origin) is str
        and os.path.isabs(origin)
        and os.path.abspath(origin) == origin
        and os.path.realpath(origin) == origin
        and os.path.commonpath((str(ROOT), origin)) == str(ROOT),
        "the genuine owned Match.expand " + label + " was substituted",
    )
    return origin


def authenticate_native_engine() -> dict[str, Any]:
    expected = str(ROOT / "candidates" / "_rust_engine.so")
    require(
        os.path.realpath(expected) == expected,
        "the actual owned Match.expand native engine was substituted",
    )
    descriptor = os.open(
        expected,
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        original = os.fstat(descriptor)
        require(
            stat.S_ISREG(original.st_mode)
            and 0 < original.st_size <= MAX_BINARY_BYTES,
            "the actual Rust Match.expand engine is not a bounded owned binary",
        )
        hasher = hashlib.sha256()
        remaining = original.st_size
        while remaining:
            block = os.read(descriptor, min(remaining, 1_048_576))
            require(bool(block), "the actual Rust native engine was truncated")
            hasher.update(block)
            remaining -= len(block)
        require(
            os.read(descriptor, 1) == b"",
            "the actual Rust engine changed while being authenticated",
        )
        final = os.fstat(descriptor)
        require(
            (final.st_dev, final.st_ino, final.st_size)
            == (original.st_dev, original.st_ino, original.st_size),
            "the actual owned Rust Match.expand engine inode changed",
        )
        return {
            "relative": "candidates/_rust_engine.so",
            "sha256": hasher.hexdigest(),
            "bytes": original.st_size,
            "device": original.st_dev,
            "inode": original.st_ino,
        }
    finally:
        os.close(descriptor)


def load_engine(name: str) -> tuple[Any, dict[str, Any] | None]:
    require(
        name in ("stdlib", "rust"),
        "only the genuine pinned or owned Match.expand engine may be loaded",
    )
    verify_runtime()
    if name == "stdlib":
        engine = importlib.import_module("re")
        require(
            engine.__name__ == "re"
            and type(engine.__file__) is str
            and os.path.abspath(engine.__file__) == str(PINNED_STDLIB_RE)
            and os.path.realpath(engine.__file__) == str(PINNED_STDLIB_RE),
            "the original CPython Match.expand reference was substituted",
        )
        return engine, None

    native = authenticate_native_engine()
    engine = importlib.import_module("candidates.rust_candidate")
    require(
        engine.__name__ == "candidates.rust_candidate"
        and authenticate_owned_module(engine, label="Rust adapter")
        == str(ROOT / "candidates" / "rust_candidate.py"),
        "the genuine owned Rust Match.expand adapter was substituted",
    )
    bridge = sys.modules.get("candidates._rust_bridge")
    require(
        isinstance(bridge, types.ModuleType)
        and bridge.__name__ == "candidates._rust_bridge",
        "the genuine compiled Rust Match.expand bridge was omitted",
    )
    bridge_origin = authenticate_owned_module(bridge, label="native bridge")
    bridge_spec = getattr(bridge, "__spec__", None)
    bridge_loader = getattr(bridge_spec, "loader", None)
    require(
        os.path.commonpath((str(ROOT / "candidates"), bridge_origin))
        == str(ROOT / "candidates")
        and any(bridge_origin.endswith(suffix) for suffix in EXTENSION_SUFFIXES)
        and bridge_spec is not None
        and getattr(bridge_spec, "name", None) == "candidates._rust_bridge"
        and getattr(bridge_spec, "origin", None) == bridge_origin
        and isinstance(bridge_loader, ExtensionFileLoader)
        and getattr(bridge_loader, "name", None) == "candidates._rust_bridge"
        and getattr(bridge_loader, "path", None) == bridge_origin,
        "the actual owned Rust extension or its loader was substituted",
    )
    require(
        getattr(engine, "Match", None) is getattr(bridge, "Match", None),
        "the genuine owned native Rust Match type was substituted",
    )
    for public in ("compile", "search", "match", "Scanner"):
        value = getattr(engine, public, None)
        require(
            value is not None
            and getattr(value, "__module__", None)
            not in ("re", "_sre", "sre_compile"),
            "a Rust Match.expand public operation delegates to CPython: " + public,
        )
    for value in vars(engine).values():
        require(
            not (
                isinstance(value, types.ModuleType)
                and value.__name__ in ("re", "_sre", "sre_compile")
            ),
            "the owned Rust adapter directly imported a CPython regex engine",
        )
    return engine, native


def observe_worker(role: str, engine_name: str) -> dict[str, Any]:
    matrix = build_matrix()
    validate_matrix(matrix)
    engine, native = load_engine(engine_name)
    records: list[dict[str, Any]] = []
    for case in matrix:
        records.append(
            {
                "case": case["case"],
                "family": case["family"],
                "outcome": execute_case(case, engine),
            }
        )
    require(
        len(records) == CASE_COUNT,
        "an original Match.expand differential observation was omitted",
    )
    return {
        "schema": SCHEMA + "-isolated-worker",
        "status": "PASS",
        "python": "3.14.6",
        "role": role,
        "engine": engine_name,
        "pid": os.getpid(),
        "published_seed": PUBLISHED_SEED,
        "matrix_sha256": MATRIX_SHA256,
        "case_count": CASE_COUNT,
        "records_sha256": digest(records),
        "records": records,
        "native_engine": native,
        "candidate_import_count": sum(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ),
        "clock_samples": 0,
        "timing_trials_run": 0,
        "files_written": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
    }


def run_worker(role: str, engine: str) -> dict[str, Any]:
    require(
        type(role) is str and bool(role) and engine in ("stdlib", "rust"),
        "an explicitly isolated original Match.expand worker is mandatory",
    )
    process = subprocess.Popen(
        [
            str(PINNED_PYTHON),
            "-I",
            "-B",
            str(ROOT / SOURCE_RELATIVE),
            "--internal-worker",
            "--engine",
            engine,
            "--role",
            role,
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(ROOT),
        shell=False,
        env={
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONHASHSEED": "0",
            "LC_ALL": "C",
            "PATH": "/usr/bin:/bin",
        },
    )
    stdout, stderr = process.communicate()
    require(
        process.returncode == 0 and stderr == b"",
        "an actual isolated Match.expand worker failed: "
        + role
        + "; exit="
        + str(process.returncode)
        + "; stderr="
        + stderr[-1200:].decode("utf-8", "replace"),
    )
    document = decode_canonical(stdout, role)
    expected = {
        "schema": SCHEMA + "-isolated-worker",
        "status": "PASS",
        "python": "3.14.6",
        "role": role,
        "engine": engine,
        "pid": process.pid,
        "published_seed": PUBLISHED_SEED,
        "matrix_sha256": MATRIX_SHA256,
        "case_count": CASE_COUNT,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "files_written": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
    }
    for key, value in expected.items():
        require(
            document.get(key) == value,
            "an actual complete Match.expand worker changed: " + key,
        )
    if engine == "stdlib":
        require(
            document.get("candidate_import_count") == 0
            and document.get("native_engine") is None,
            "a standard-library Match.expand worker imported a candidate",
        )
    else:
        require(
            type(document.get("candidate_import_count")) is int
            and document["candidate_import_count"] > 0
            and type(document.get("native_engine")) is dict,
            "the owned native Rust Match.expand worker was not authenticated",
        )
    records = document.get("records")
    require(
        type(records) is list
        and len(records) == CASE_COUNT
        and document.get("records_sha256") == digest(records),
        "an actual complete Match.expand vector was hidden or forged",
    )
    for case, record in zip(build_matrix(), records, strict=True):
        require(
            type(record) is dict
            and set(record) == {"case", "family", "outcome"}
            and record.get("case") == case["case"]
            and record.get("family") == case["family"]
            and type(record.get("outcome")) is dict
            and record["outcome"].get("status") in ("return", "raise")
            and type(record["outcome"].get("warnings")) is list,
            "a complete source-ordered Match.expand observation was concealed",
        )
    return document


def source_self_test() -> dict[str, Any]:
    verify_runtime()
    matrix = build_matrix()
    validate_matrix(matrix)
    first = run_worker("expand_original_reference_a", "stdlib")
    second = run_worker("expand_original_reference_b", "stdlib")
    require(
        first["pid"] != second["pid"]
        and first["records"] == second["records"]
        and first["records_sha256"] == second["records_sha256"]
        and first["records_sha256"] == BASELINE_SHA256,
        "the two actual complete pinned Match.expand references disagree",
    )
    counts = {family: 0 for family in FAMILIES}
    statuses = {"return": 0, "raise": 0}
    measured_memoryview_cases = 0
    for record in first["records"]:
        counts[record["family"]] += 1
        statuses[record["outcome"]["status"]] += 1
        if record["family"] in (
            "measured-mutable-memoryview",
            "measured-readonly-memoryview",
        ):
            measured_memoryview_cases += 1
    require(
        all(count == VARIANTS_PER_FAMILY for count in counts.values())
        and measured_memoryview_cases == 2 * VARIANTS_PER_FAMILY
        and statuses["return"] > 0
        and statuses["raise"] > 0,
        "a genuine original Match.expand family or error domain was hidden",
    )
    rejected = 0
    for index in range(24):
        omitted = list(matrix)
        omitted.pop(index)
        try:
            validate_matrix(omitted)
        except ExpandOracleError:
            rejected += 1
        else:
            raise ExpandOracleError("an omitted Match.expand case was accepted")
    for index in range(12):
        forged = list(matrix)
        altered = dict(forged[index])
        altered["family"] = "substituted-foreign-expand-family"
        forged[index] = altered
        try:
            validate_matrix(forged)
        except ExpandOracleError:
            rejected += 1
        else:
            raise ExpandOracleError("a substituted Match.expand case was accepted")
    for value in (
        None,
        "",
        "0" * 64,
        "G" * 64,
        MATRIX_SHA256.upper(),
        BASELINE_SHA256.upper(),
    ):
        require(
            not valid_digest(value),
            "a forged frozen Match.expand digest was accepted",
        )
        rejected += 1
    require(
        rejected >= 40,
        "the required original Match.expand poison controls were omitted",
    )
    verify_runtime()
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "python": "3.14.6",
        "published_seed": PUBLISHED_SEED,
        "matrix_sha256": MATRIX_SHA256,
        "baseline_records_sha256": BASELINE_SHA256,
        "case_count": CASE_COUNT,
        "family_count": len(FAMILIES),
        "variants_per_family": VARIANTS_PER_FAMILY,
        "actual_reference_workers": 2,
        "actual_candidate_workers": 0,
        "candidate_import_count": 0,
        "measured_memoryview_cases": measured_memoryview_cases,
        "outcome_counts": statuses,
        "rejected_control_count": rejected,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "files_written": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def run_candidate() -> dict[str, Any]:
    verify_runtime()
    matrix = build_matrix()
    validate_matrix(matrix)
    baseline = run_worker("expand_original_candidate_reference", "stdlib")
    require(
        baseline["records_sha256"] == BASELINE_SHA256,
        "the genuine complete pinned Match.expand baseline changed",
    )
    candidate = run_worker("expand_owned_native_rust_candidate", "rust")
    require(
        baseline["pid"] != candidate["pid"],
        "the two Match.expand engines were not independently isolated",
    )
    by_family = {family: 0 for family in FAMILIES}
    mismatches: list[dict[str, Any]] = []
    for case, original, actual in zip(
        matrix,
        baseline["records"],
        candidate["records"],
        strict=True,
    ):
        require(
            original["case"] == actual["case"] == case["case"]
            and original["family"] == actual["family"] == case["family"],
            "a complete original Match.expand case order was substituted",
        )
        if original["outcome"] != actual["outcome"]:
            by_family[case["family"]] += 1
            mismatches.append(
                {
                    "case": case["case"],
                    "family": case["family"],
                    "input": case,
                    "baseline_outcome": original["outcome"],
                    "rust_outcome": actual["outcome"],
                }
            )
    return {
        "schema": SCHEMA + "-candidate-result",
        "status": "PASS" if not mismatches else "FAIL",
        "python": "3.14.6",
        "published_seed": PUBLISHED_SEED,
        "matrix_sha256": MATRIX_SHA256,
        "baseline_records_sha256": BASELINE_SHA256,
        "candidate_records_sha256": candidate["records_sha256"],
        "case_denominator": CASE_COUNT,
        "actual_baseline_cases": len(baseline["records"]),
        "actual_candidate_cases": len(candidate["records"]),
        "mismatch_count": len(mismatches),
        "mismatches_by_family": by_family,
        "all_mismatches": mismatches,
        "first_mismatch": mismatches[0] if mismatches else None,
        "baseline_pid": baseline["pid"],
        "candidate_pid": candidate["pid"],
        "native_engine": candidate["native_engine"],
        "actual_candidate_workers": 1,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "files_written": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Independent, deterministic, untimed original Match.expand "
            "memoryview differential oracle"
        ),
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--candidate", action="store_true")
    modes.add_argument(
        "--internal-worker",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--engine",
        choices=("stdlib", "rust"),
        help=argparse.SUPPRESS,
    )
    parser.add_argument("--role", help=argparse.SUPPRESS)
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    if options.self_test:
        require(
            options.engine is None and options.role is None,
            "a Match.expand source self-test cannot inject a candidate",
        )
        result = source_self_test()
    elif options.candidate:
        require(
            options.engine is None and options.role is None,
            "a Match.expand comparison cannot inject a worker role",
        )
        result = run_candidate()
    else:
        require(
            options.engine in ("stdlib", "rust")
            and type(options.role) is str
            and bool(options.role),
            "an exact isolated Match.expand worker role is mandatory",
        )
        result = observe_worker(options.role, options.engine)
    sys.stdout.buffer.write(canonical(result))
    sys.stdout.buffer.flush()
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ExpandOracleError as error:
        print(
            "independent Match.expand differential failed closed: " + str(error),
            file=sys.stderr,
        )
        raise SystemExit(1) from error
