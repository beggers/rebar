#!/usr/bin/env python3
"""Freeze Python Scanner comment and VERBOSE correctness, without benchmarks.

The 2,854 cases include the independently reproduced 2,560 comment/scope
combinations and all 294 escaped-newline/tokenizer combinations.  A synthetic
``--self-test`` cannot open files, import a candidate, start a process or
thread, sample a clock, or run a regular-expression engine.  ``--baseline`` is
a separately and explicitly pinned operation: it starts exactly two isolated
standard-CPython workers and preserves their complete, exact observations.
There is deliberately no candidate-running or performance-measurement mode.
Future candidate recorders must use the frozen V5 native ownership guard.
"""

from __future__ import annotations

import argparse
import base64
import builtins
import gc
import hashlib
import importlib
import io
import json
import os
import random
import stat
import subprocess
import sys
import threading
import time
import types
import warnings
from collections.abc import Callable, Mapping
from typing import Any


ROOT = "/home/dev-user/src/rebar"
SOURCE_RELATIVE = "tools/independent_scanner_verbose_comments_v1.py"
SOURCE_ABSOLUTE = ROOT + "/" + SOURCE_RELATIVE
SCHEMA = "rebar-independent-scanner-verbose-comments-v1"
PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
PINNED_STDLIB_DIRECTORY = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/lib/python3.14/re/"
)
PINNED_STDLIB_SOURCES = types.MappingProxyType({
    "re": (
        "__init__.py",
        "741a9de729ed8207bfa19db990f8826f1bf3661f33d0970a80c08cd1338ebc35",
    ),
    "re._compiler": (
        "_compiler.py",
        "d49f30cf9a1dbae33b200ed8befd9d0ce3ac612783a10ac35196536f98923e91",
    ),
    "re._parser": (
        "_parser.py",
        "e57bd194a2d42398355ae7c1ccc2ddfb78421dd431eb81e3809dbe8ca9057dc4",
    ),
    "re._constants": (
        "_constants.py",
        "42253b3181b81aad6c46392f44a0ab26dcfa31feea411296f43ba16616a1ab0b",
    ),
})
V5_GUARD_RELATIVE = "tools/independent_original_cpython_suite_v5.py"
V5_GUARD_SHA256 = (
    "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce"
)
OWNERSHIP_AUDIT_RELATIVE = "tools/independent_from_scratch_audit_v3.py"
OWNERSHIP_AUDIT_SHA256 = (
    "377c63eecccea021562694e00d624d54f61adfb0d3a4700586a29ed424f389ee"
)
PUBLISHED_SEED = 0x5343_4E56_4552_5631
VERBOSE = 64
SEMANTIC_CASE_COUNT = 2_560
TOKENIZER_CASE_COUNT = 294
CASE_COUNT = SEMANTIC_CASE_COUNT + TOKENIZER_CASE_COUNT
MATRIX_SHA256 = (
    "01bca287cd481a5e4ae134b910911e2e2f8f1501eebb7ffd2947092ab170d17b"
)
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
MAX_PROCESS_BYTES = 64 * 1024 * 1024
COMMENT_PAYLOADS = (
    "(((",
    "(?P<phantom>q)",
    "\\8",
    "(?(99)a|b)",
    "(?P=missing)",
    "(?x:",
    "(?-x:",
    "[unclosed(",
    ") ((( ???",
    "\\",
    "# another comment",
    "(?<=(",
    "(?<!(",
    "(?>(",
    "(?P<_phantom>(",
    "(?#not-really",
)
SEMANTIC_TAILS = (
    ("literal", "a", "a"),
    ("plain_capture", "(a)", "a"),
    ("named_capture", "(?P<real>a)", "a"),
    ("conditional_yes", "(a)?(?(1)b|c)", "ab"),
    ("conditional_no", "(a)?(?(1)b|c)", "c"),
    ("numeric_backreference", "(a)\\1", "aa"),
    ("named_backreference", "(?P<real>a)(?P=real)", "aa"),
    ("inner_verbose_scope", "(?x:a b)", "ab"),
)
SEMANTIC_ENDINGS = (("lf", "\n"), ("crlf", "\r\n"))
SEMANTIC_CONTEXTS = (
    "root_verbose",
    "global_verbose",
    "scoped_verbose",
    "nested_enable",
    "nested_disable",
)
TOKENIZER_ENDINGS = (
    ("none", ""),
    ("lf", "\n"),
    ("cr", "\r"),
    ("crlf", "\r\n"),
    ("lfcr", "\n\r"),
    ("double_lf", "\n\n"),
    ("latin1_nel", "\x85"),
)
TOKENIZER_CONTEXTS = ("root", "global", "scoped")
EXPECTED_KINDS = frozenset({
    "full-match",
    "continued-comment-empty",
    "prefix-then-fallback",
    "continued-comment-unterminated",
})
EXPECTED_COUNTS = types.MappingProxyType({
    "full-match": 2_612,
    "continued-comment-empty": 32,
    "prefix-then-fallback": 108,
    "continued-comment-unterminated": 102,
})
EXPECTED_NEGATIVE_COUNTS = types.MappingProxyType({
    "semantic": 48,
    "tokenizer": 54,
})
FORBIDDEN_ENGINE_ROOTS = frozenset({
    "_regex", "candidates", "fancy_regex", "google_re2", "hyperscan",
    "onig", "oniguruma", "pcre", "pcre2", "re2", "regex",
    "rust_regex", "sre_compile", "sre_constants", "sre_parse", "vectorscan",
})


class ScannerCommentOracleError(Exception):
    """The frozen matrix, Python provenance, or full observation was forged."""


class SourceOnlyError(ScannerCommentOracleError):
    """A synthetic control attempted a real external effect."""


class ReferenceWorkerFailure(ScannerCommentOracleError):
    """A genuine worker failed; retain its complete unmodified evidence."""

    def __init__(self, message: str, evidence: Mapping[str, Any]) -> None:
        super().__init__(message)
        self.evidence = dict(evidence)


def require(condition: Any, message: str) -> None:
    if not condition:
        raise ScannerCommentOracleError(message)


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii") + b"\n"
    except (TypeError, ValueError, UnicodeError, OverflowError) as error:
        raise ScannerCommentOracleError(
            "a scanner-comment observation is not canonical JSON"
        ) from error


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def valid_digest(value: Any) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and len(set(value)) > 1
        and all(letter in "0123456789abcdef" for letter in value)
    )


def checked_digest(value: Any, label: str) -> str:
    require(valid_digest(value), "an exact SHA-256 is mandatory: " + label)
    return value


def unique_json_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        require(type(key) is str and key not in result,
                "a complete scanner-comment JSON field was duplicated")
        result[key] = value
    return result


def decode_canonical(raw: Any, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_PROCESS_BYTES,
            "complete bounded worker evidence is mandatory: " + label)

    def reject_constant(_: str) -> Any:
        raise ScannerCommentOracleError("nonfinite JSON is forbidden")

    try:
        value = json.loads(
            raw,
            object_pairs_hook=unique_json_object,
            parse_constant=reject_constant,
        )
    except (
        ScannerCommentOracleError, TypeError, ValueError, UnicodeError,
        json.JSONDecodeError,
    ) as error:
        raise ScannerCommentOracleError(
            "an isolated scanner-comment worker emitted invalid JSON: " + label
        ) from error
    require(type(value) is dict and canonical(value) == raw,
            "a complete canonical worker was truncated or substituted: " + label)
    return value


def encode_subject(value: str | bytes) -> dict[str, str]:
    if type(value) is str:
        return {"kind": "str", "value": value}
    if type(value) is bytes:
        return {"kind": "bytes", "hex": value.hex()}
    raise ScannerCommentOracleError("an exact text or bytes carrier is required")


def validate_subject(value: Any, *, domain: str) -> dict[str, str]:
    require(domain in {"str", "bytes"} and type(value) is dict,
            "an exact scanner phrase and subject domain is mandatory")
    if domain == "str":
        require(set(value) == {"kind", "value"}
                and value.get("kind") == "str"
                and type(value.get("value")) is str,
                "a complete original Unicode carrier was substituted")
    else:
        require(set(value) == {"kind", "hex"}
                and value.get("kind") == "bytes"
                and type(value.get("hex")) is str,
                "a complete original bytes carrier was substituted")
        try:
            raw = bytes.fromhex(value["hex"])
        except ValueError as error:
            raise ScannerCommentOracleError(
                "a scanner bytes carrier is not canonical lowercase hex"
            ) from error
        require(raw.hex() == value["hex"],
                "a scanner bytes carrier is not canonical lowercase hex")
    return value


def decode_subject(value: Mapping[str, Any]) -> str | bytes:
    kind = value.get("kind")
    validate_subject(value, domain=kind)
    return value["value"] if kind == "str" else bytes.fromhex(value["hex"])


def semantic_contexts(
    payload: str, ending: str, tail: str, subject: str,
) -> tuple[tuple[str, str, int, str], ...]:
    return (
        ("root_verbose", "# " + payload + ending + tail, VERBOSE, subject),
        ("global_verbose", "(?x)# " + payload + ending + tail, 0, subject),
        ("scoped_verbose", "(?x:# " + payload + ending + tail + ")", 0,
         subject),
        ("nested_enable",
         "(?-x:\\#(?x:# " + payload + ending + tail + "))",
         VERBOSE, "#" + subject),
        ("nested_disable",
         "(?x:# " + payload + ending + "(?-x:\\#)(?x:" + tail + "))",
         0, "#" + subject),
    )


def add_case(
    records: list[dict[str, Any]],
    *,
    seed: int,
    cohort: str,
    domain: str,
    context: str,
    phrase: str,
    flags: int,
    subject: str,
    ending: str,
    tail: str | None,
    payload_index: int | None,
    slash_count: int | None,
    expected: str,
) -> None:
    require(domain in {"str", "bytes"} and expected in EXPECTED_KINDS,
            "an unfrozen scanner case was injected")
    if domain == "bytes":
        native_phrase: str | bytes = phrase.encode("latin1")
        native_subject: str | bytes = subject.encode("latin1")
    else:
        native_phrase, native_subject = phrase, subject
    parts = [cohort, domain, context, ending]
    if payload_index is not None:
        parts.extend((str(payload_index), str(tail)))
    if slash_count is not None:
        parts.append(str(slash_count))
    records.append({
        "case": "/".join(parts),
        "cohort": cohort,
        "context": context,
        "domain": domain,
        "flags": flags,
        "phrase": encode_subject(native_phrase),
        "subject": encode_subject(native_subject),
        "line_ending": ending,
        "tail": tail,
        "payload_index": payload_index,
        "slash_count": slash_count,
        "expected_kind": expected,
        "seed": seed,
    })


def build_matrix(seed: int = PUBLISHED_SEED) -> list[dict[str, Any]]:
    require(type(seed) is int and seed >= 0,
            "an exact nonnegative published scanner seed is mandatory")
    records: list[dict[str, Any]] = []
    for domain in ("str", "bytes"):
        for payload_index, payload in enumerate(COMMENT_PAYLOADS):
            for ending_name, ending in SEMANTIC_ENDINGS:
                for tail_name, tail, subject in SEMANTIC_TAILS:
                    for context, phrase, flags, value in semantic_contexts(
                        payload, ending, tail, subject
                    ):
                        slash_count = len(payload) - len(payload.rstrip("\\"))
                        continued = ending_name == "lf" and slash_count % 2 == 1
                        expected = (
                            "continued-comment-empty"
                            if continued and context in {
                                "root_verbose", "global_verbose"
                            }
                            else "continued-comment-unterminated"
                            if continued
                            else "full-match"
                        )
                        add_case(
                            records,
                            seed=seed,
                            cohort="semantic",
                            domain=domain,
                            context=context,
                            phrase=phrase,
                            flags=flags,
                            subject=value,
                            ending=ending_name,
                            tail=tail_name,
                            payload_index=payload_index,
                            slash_count=None,
                            expected=expected,
                        )

        for slash_count in range(7):
            for ending_name, ending in TOKENIZER_ENDINGS:
                body = "a # " + "\\" * slash_count + ending + "b"
                terminated = (
                    ending_name in {"crlf", "double_lf"}
                    or ending_name in {"lf", "lfcr"} and slash_count % 2 == 0
                )
                for context in TOKENIZER_CONTEXTS:
                    phrase = (
                        body if context == "root"
                        else "(?x)" + body if context == "global"
                        else "(?x:" + body + ")"
                    )
                    expected = (
                        "full-match" if terminated
                        else "continued-comment-unterminated"
                        if context == "scoped"
                        else "prefix-then-fallback"
                    )
                    add_case(
                        records,
                        seed=seed,
                        cohort="tokenizer",
                        domain=domain,
                        context=context,
                        phrase=phrase,
                        flags=VERBOSE if context == "root" else 0,
                        subject="ab",
                        ending=ending_name,
                        tail=None,
                        payload_index=None,
                        slash_count=slash_count,
                        expected=expected,
                    )
    require(len(records) == CASE_COUNT,
            "a complete deterministic scanner-comment case was omitted")
    random.Random(seed).shuffle(records)
    return records


def validate_matrix(
    records: Any, expected_sha256: str | None = None,
) -> str:
    require(type(records) is list and len(records) == CASE_COUNT,
            "all 2,854 exact scanner-comment cases are mandatory")
    required = {
        "case", "cohort", "context", "domain", "flags", "phrase",
        "subject", "line_ending", "tail", "payload_index", "slash_count",
        "expected_kind", "seed",
    }
    seen: set[str] = set()
    counts = {name: 0 for name in EXPECTED_COUNTS}
    negative = {"semantic": 0, "tokenizer": 0}
    cohort_counts = {"semantic": 0, "tokenizer": 0}
    for row in records:
        require(type(row) is dict and set(row) == required,
                "a complete seeded scanner case was added, removed, or hidden")
        identifier = row.get("case")
        domain = row.get("domain")
        cohort = row.get("cohort")
        expected = row.get("expected_kind")
        require(type(identifier) is str and identifier not in seen
                and domain in {"str", "bytes"}
                and cohort in cohort_counts
                and expected in counts
                and type(row.get("flags")) is int
                and row["flags"] in {0, VERBOSE}
                and row.get("seed") == PUBLISHED_SEED,
                "a unique original scanner case, flag, domain, or seed changed")
        seen.add(identifier)
        validate_subject(row.get("phrase"), domain=domain)
        validate_subject(row.get("subject"), domain=domain)
        counts[expected] += 1
        cohort_counts[cohort] += 1
        if expected == "continued-comment-unterminated":
            negative[cohort] += 1
        if cohort == "semantic":
            require(row.get("context") in SEMANTIC_CONTEXTS
                    and row.get("line_ending") in {"lf", "crlf"}
                    and row.get("tail") in {
                        name for name, _, _ in SEMANTIC_TAILS
                    }
                    and type(row.get("payload_index")) is int
                    and 0 <= row["payload_index"] < len(COMMENT_PAYLOADS)
                    and row.get("slash_count") is None,
                    "an original comment, capture, scope, or escape was hidden")
        else:
            require(row.get("context") in TOKENIZER_CONTEXTS
                    and row.get("line_ending") in {
                        name for name, _ in TOKENIZER_ENDINGS
                    }
                    and row.get("tail") is None
                    and row.get("payload_index") is None
                    and type(row.get("slash_count")) is int
                    and 0 <= row["slash_count"] <= 6,
                    "an escaped newline or original tokenizer case was hidden")
    require(cohort_counts == {
        "semantic": SEMANTIC_CASE_COUNT,
        "tokenizer": TOKENIZER_CASE_COUNT,
    }, "the complete 2,560 and 294 case denominators were changed")
    require(counts == dict(EXPECTED_COUNTS),
            "a genuine full match, empty scan, fallback, or error was hidden")
    require(negative == dict(EXPECTED_NEGATIVE_COUNTS),
            "the genuine 48 or 54 Python PatternErrors were hidden")
    actual = digest(records)
    if expected_sha256 is None:
        expected_sha256 = MATRIX_SHA256
    checked_digest(expected_sha256, "prospectively frozen scanner case matrix")
    require(actual == expected_sha256,
            "the exact deterministic scanner matrix or its order changed")
    return actual


def normalize_value(value: Any) -> dict[str, Any]:
    if value is None:
        return {"kind": "none"}
    if type(value) is bool:
        return {"kind": "bool", "value": value}
    if type(value) is int:
        return {"kind": "int", "value": value}
    if type(value) is str:
        return {"kind": "str", "value": value}
    if type(value) is bytes:
        return {"kind": "bytes", "hex": value.hex()}
    if type(value) is bytearray:
        return {"kind": "bytearray", "hex": bytes(value).hex()}
    if type(value) is memoryview:
        return {
            "kind": "memoryview",
            "readonly": value.readonly,
            "format": value.format,
            "itemsize": value.itemsize,
            "ndim": value.ndim,
            "shape": list(value.shape) if value.shape is not None else None,
            "strides": list(value.strides) if value.strides is not None else None,
            "contiguous": value.contiguous,
            "hex": value.tobytes().hex(),
        }
    if type(value) in {tuple, list}:
        return {
            "kind": "tuple" if type(value) is tuple else "list",
            "items": [normalize_value(item) for item in value],
        }
    if isinstance(value, Mapping):
        pairs = [
            [normalize_value(key), normalize_value(item)]
            for key, item in value.items()
        ]
        pairs.sort(key=lambda item: canonical(item[0]))
        return {"kind": "mapping", "items": pairs}
    raise ScannerCommentOracleError(
        "a complete scanner carrier was hidden: " + type(value).__qualname__
    )


def validate_normalized_value(value: Any) -> None:
    require(type(value) is dict and type(value.get("kind")) is str,
            "an exact typed scanner value is mandatory")
    kind = value["kind"]
    if kind == "none":
        require(set(value) == {"kind"}, "a genuine None was forged")
    elif kind in {"bool", "int", "str"}:
        expected = {"bool": bool, "int": int, "str": str}[kind]
        require(set(value) == {"kind", "value"}
                and type(value.get("value")) is expected,
                "a genuine scalar carrier was forged: " + kind)
    elif kind in {"bytes", "bytearray"}:
        require(set(value) == {"kind", "hex"}
                and type(value.get("hex")) is str,
                "a genuine binary carrier was forged: " + kind)
        try:
            raw = bytes.fromhex(value["hex"])
        except ValueError as error:
            raise ScannerCommentOracleError(
                "a scanner binary observation is not canonical hex"
            ) from error
        require(raw.hex() == value["hex"],
                "a scanner binary observation is not canonical hex")
    elif kind == "memoryview":
        require(set(value) == {
            "kind", "readonly", "format", "itemsize", "ndim", "shape",
            "strides", "contiguous", "hex",
        } and type(value.get("readonly")) is bool
          and type(value.get("format")) is str
          and type(value.get("itemsize")) is int
          and value["itemsize"] > 0
          and type(value.get("ndim")) is int
          and value["ndim"] >= 0
          and type(value.get("contiguous")) is bool
          and type(value.get("hex")) is str,
          "a complete memory carrier and its layout are mandatory")
        try:
            raw = bytes.fromhex(value["hex"])
        except ValueError as error:
            raise ScannerCommentOracleError(
                "a scanner memory carrier is not canonical hex"
            ) from error
        require(raw.hex() == value["hex"],
                "a scanner memory carrier is not canonical hex")
        for field in ("shape", "strides"):
            actual = value[field]
            require(actual is None or type(actual) is list
                    and len(actual) == value["ndim"]
                    and all(type(item) is int for item in actual),
                    "a genuine scanner memory layout was hidden: " + field)
    elif kind in {"tuple", "list"}:
        require(set(value) == {"kind", "items"}
                and type(value.get("items")) is list,
                "an ordered scanner return was forged: " + kind)
        for item in value["items"]:
            validate_normalized_value(item)
    elif kind == "mapping":
        require(set(value) == {"kind", "items"}
                and type(value.get("items")) is list,
                "a complete scanner mapping is mandatory")
        previous: bytes | None = None
        for pair in value["items"]:
            require(type(pair) is list and len(pair) == 2,
                    "a complete scanner mapping entry was omitted")
            validate_normalized_value(pair[0])
            validate_normalized_value(pair[1])
            current = canonical(pair[0])
            require(previous is None or previous < current,
                    "scanner mapping entries were reordered or duplicated")
            previous = current
    else:
        raise ScannerCommentOracleError(
            "an unknown scanner carrier was injected: " + kind
        )


def normalize_pattern(value: Any) -> dict[str, Any]:
    groups = value.groups
    flags = value.flags
    require(type(groups) is int and groups >= 0 and type(flags) is int,
            "the genuine combined scanner flags or group count was hidden")
    return {
        "kind": "compiled-pattern",
        "pattern": normalize_value(value.pattern),
        "flags": flags,
        "groups": groups,
        "groupindex": normalize_value(dict(value.groupindex)),
    }


def normalize_match(value: Any) -> dict[str, Any]:
    expression = value.re
    count = expression.groups
    require(type(count) is int and count >= 0,
            "a genuine scanner match concealed its native group count")
    return {
        "kind": "match",
        "pattern": normalize_pattern(expression),
        "string": normalize_value(value.string),
        "group": normalize_value(value.group(0)),
        "groups": [normalize_value(item) for item in value.groups()],
        "spans": [list(value.span(index)) for index in range(count + 1)],
        "groupdict": normalize_value(value.groupdict()),
        "lastindex": value.lastindex,
        "lastgroup": value.lastgroup,
        "pos": value.pos,
        "endpos": value.endpos,
    }


def validate_pattern(value: Any) -> None:
    require(type(value) is dict and set(value) == {
        "kind", "pattern", "flags", "groups", "groupindex",
    } and value.get("kind") == "compiled-pattern"
      and type(value.get("flags")) is int
      and type(value.get("groups")) is int and value["groups"] >= 0,
      "a complete genuine scanner combined pattern was forged")
    validate_normalized_value(value["pattern"])
    validate_normalized_value(value["groupindex"])


def validate_match(value: Any) -> None:
    require(type(value) is dict and set(value) == {
        "kind", "pattern", "string", "group", "groups", "spans",
        "groupdict", "lastindex", "lastgroup", "pos", "endpos",
    } and value.get("kind") == "match",
      "a complete scanner callback match was forged")
    validate_pattern(value["pattern"])
    groups = value["pattern"]["groups"]
    require(type(value.get("groups")) is list
            and len(value["groups"]) == groups
            and type(value.get("spans")) is list
            and len(value["spans"]) == groups + 1
            and type(value.get("pos")) is int
            and type(value.get("endpos")) is int
            and (value.get("lastindex") is None
                 or type(value["lastindex"]) is int)
            and (value.get("lastgroup") is None
                 or type(value["lastgroup"]) is str),
            "complete scanner groups, positions, or last capture were hidden")
    for field in ("string", "group", "groupdict"):
        validate_normalized_value(value[field])
    for item in value["groups"]:
        validate_normalized_value(item)
    for span in value["spans"]:
        require(type(span) is list and len(span) == 2
                and all(type(item) is int for item in span),
                "a complete scanner capture span was omitted")


def normalize_error(error: Exception, engine: Any) -> dict[str, Any]:
    engine_error = getattr(engine, "error", None)
    if isinstance(engine_error, type) and isinstance(error, engine_error):
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


def validate_error(value: Any) -> None:
    require(type(value) is dict and type(value.get("kind")) is str,
            "a complete genuine Python scanner error is mandatory")
    if value["kind"] == "public-regex-error":
        require(set(value) == {
            "kind", "type", "args", "message", "pattern", "position",
            "line", "column",
        } and type(value.get("type")) is str
          and (value.get("message") is None
               or type(value["message"]) is str),
          "a genuine Python PatternError was approximated")
        validate_normalized_value(value["args"])
        validate_normalized_value(value["pattern"])
        for field in ("position", "line", "column"):
            require(value[field] is None or type(value[field]) is int,
                    "a genuine PatternError position was hidden: " + field)
    else:
        require(value["kind"] == "ordinary-python-error"
                and set(value) == {"kind", "module", "type", "args"}
                and type(value.get("module")) is str
                and type(value.get("type")) is str,
                "a genuine scanner Python exception was approximated")
        validate_normalized_value(value["args"])


def normalize_warnings(observed: list[Any]) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for item in observed:
        require(isinstance(item.category, type)
                and isinstance(item.message, Warning)
                and isinstance(item.message, item.category),
                "a genuine scanner warning was substituted")
        records.append({
            "category_module": item.category.__module__,
            "category": item.category.__qualname__,
            "message": str(item.message),
        })
    return records


def make_action(
    branch: int, events: list[dict[str, Any]],
) -> Callable[[Any, Any], Any]:
    def action(scanner: Any, token: Any) -> Any:
        match = scanner.match
        combined = scanner.scanner
        events.append({
            "branch": branch,
            "token": normalize_value(token),
            "match": normalize_match(match),
            "combined_pattern": normalize_pattern(combined),
            "match_uses_combined_pattern": match.re is combined,
        })
        require(len(events) <= 2,
                "a frozen scanner case failed to make forward progress")
        return (branch, token)

    return action


def execute_case(case: Mapping[str, Any], engine: Any) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    combined: dict[str, Any] | None = None
    with warnings.catch_warnings(record=True) as observed:
        warnings.simplefilter("always")
        try:
            phrase = decode_subject(case["phrase"])
            subject = decode_subject(case["subject"])
            fallback = "." if case["domain"] == "str" else b"."
            lexicon = [
                (phrase, make_action(0, events)),
                (fallback, make_action(1, events)),
            ]
            scanner = engine.Scanner(lexicon, flags=case["flags"])
            require(scanner.lexicon is lexicon,
                    "the original Scanner lexicon identity was substituted")
            combined = normalize_pattern(scanner.scanner)
            require(scanner.scanner.pattern is None
                    and scanner.scanner.groups == 2
                    and scanner.scanner.flags == case["flags"]
                    and dict(scanner.scanner.groupindex) == {},
                    "a native combined scanner pattern was approximated")
            scanned, remainder = scanner.scan(subject)
            outcome = {
                "status": "return",
                "value": normalize_value((scanned, remainder)),
                "callbacks": events,
                "warnings": normalize_warnings(observed),
                "combined_pattern": combined,
            }
        except ScannerCommentOracleError:
            raise
        except Exception as error:
            outcome = {
                "status": "raise",
                "exception": normalize_error(error, engine),
                "callbacks": events,
                "warnings": normalize_warnings(observed),
                "combined_pattern": combined,
            }
    validate_outcome(outcome)
    verify_expected_outcome(case, outcome)
    return outcome


def validate_outcome(value: Any) -> None:
    require(type(value) is dict and value.get("status") in {"return", "raise"},
            "an exact scanner return or exception is mandatory")
    required = {"status", "callbacks", "warnings", "combined_pattern"}
    required.add("value" if value["status"] == "return" else "exception")
    require(set(value) == required,
            "a scanner callback, warning, return, or exception was hidden")
    require(type(value.get("callbacks")) is list
            and len(value["callbacks"]) <= 2
            and type(value.get("warnings")) is list,
            "all actual scanner callbacks and warnings are mandatory")
    if value["combined_pattern"] is not None:
        validate_pattern(value["combined_pattern"])
    for event in value["callbacks"]:
        require(type(event) is dict and set(event) == {
            "branch", "token", "match", "combined_pattern",
            "match_uses_combined_pattern",
        } and type(event.get("branch")) is int
          and event["branch"] in {0, 1}
          and type(event.get("match_uses_combined_pattern")) is bool,
          "a complete scanner callback was omitted")
        validate_normalized_value(event["token"])
        validate_match(event["match"])
        validate_pattern(event["combined_pattern"])
    for warning in value["warnings"]:
        require(type(warning) is dict and set(warning) == {
            "category_module", "category", "message",
        } and all(type(warning[name]) is str for name in warning),
          "a genuine scanner warning was hidden")
    if value["status"] == "return":
        validate_normalized_value(value["value"])
    else:
        validate_error(value["exception"])


def verify_expected_outcome(
    case: Mapping[str, Any], outcome: Mapping[str, Any],
) -> None:
    expected = case["expected_kind"]
    callbacks = outcome["callbacks"]
    if expected == "continued-comment-unterminated":
        require(outcome["status"] == "raise"
                and outcome["exception"]["kind"] == "public-regex-error"
                and outcome["exception"]["type"] in {"PatternError", "error"}
                and callbacks == [] and outcome["combined_pattern"] is None,
                "a genuine unterminated Python PatternError was hidden")
        return
    require(outcome["status"] == "return"
            and outcome["combined_pattern"] is not None,
            "a valid original scanner unexpectedly raised")
    returned = outcome["value"]
    require(returned["kind"] == "tuple" and len(returned["items"]) == 2
            and returned["items"][0]["kind"] == "list",
            "the genuine scanner tokens and remainder were approximated")
    tokens = returned["items"][0]["items"]
    remainder = returned["items"][1]
    subject = decode_subject(case["subject"])
    empty = normalize_value(subject[:0])
    if expected == "continued-comment-empty":
        require(tokens == [] and callbacks == []
                and remainder == normalize_value(subject),
                "an escaped newline must preserve a stopped zero-width scan")
    elif expected == "full-match":
        require(len(tokens) == len(callbacks) == 1
                and callbacks[0]["branch"] == 0
                and callbacks[0]["token"] == normalize_value(subject)
                and callbacks[0]["match_uses_combined_pattern"] is True
                and remainder == empty,
                "a complete verbose scanner match or its native callback changed")
    else:
        require(expected == "prefix-then-fallback"
                and len(tokens) == len(callbacks) == 2
                and [item["branch"] for item in callbacks] == [0, 1]
                and callbacks[0]["token"] == normalize_value(subject[:1])
                and callbacks[1]["token"] == normalize_value(subject[1:])
                and all(item["match_uses_combined_pattern"] is True
                        for item in callbacks)
                and remainder == empty,
                "an unterminated comment changed the real fallback branch")


def validate_future_candidate_pins(value: Any) -> dict[str, str]:
    require(type(value) is dict and set(value) == {
        "family", "adapter_relative", "adapter_sha256", "engine_relative",
        "engine_sha256", "bridge_relative", "bridge_sha256",
        "v5_guard_relative", "v5_guard_sha256", "ownership_audit_relative",
        "ownership_audit_sha256",
    }, "an independently authenticated V5-owned source closure is mandatory")
    family = value.get("family")
    require(family in {"rust", "c", "zig"},
            "an independent Rust, C, or Zig owner is mandatory")
    adapters = {
        "rust": "candidates/rust_candidate.py",
        "c": "candidates/vm_candidate.py",
        "zig": "candidates/zig_candidate.py",
    }
    engines = {
        "rust": "candidates/_rust_engine.so",
        "c": "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
        "zig": "candidates/_zig_probe.so",
    }
    bridges = {
        "rust": "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "c": "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
        "zig": "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
    }
    require(value["adapter_relative"] == adapters[family]
            and value["engine_relative"] == engines[family]
            and value["bridge_relative"] == bridges[family]
            and value["v5_guard_relative"] == V5_GUARD_RELATIVE
            and value["v5_guard_sha256"] == V5_GUARD_SHA256
            and value["ownership_audit_relative"] == OWNERSHIP_AUDIT_RELATIVE
            and value["ownership_audit_sha256"] == OWNERSHIP_AUDIT_SHA256,
            "a sibling engine, external package, or ownership guard was used")
    for name in ("adapter_sha256", "engine_sha256", "bridge_sha256"):
        checked_digest(value[name], "future native candidate " + name)
    require((value["engine_relative"] == value["bridge_relative"])
            == (family == "c")
            and (value["engine_sha256"] == value["bridge_sha256"])
            == (family == "c"),
            "a native engine was delegated to another candidate")
    return dict(value)


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True
            and os.path.abspath(sys.executable) == PINNED_PYTHON
            and os.path.realpath(sys.executable) == PINNED_PYTHON
            and os.path.abspath(__file__) == SOURCE_ABSOLUTE
            and os.path.realpath(__file__) == SOURCE_ABSOLUTE,
            "use only the exact isolated pinned CPython and frozen source")


def read_pinned_file(
    absolute: str, expected_sha256: str, *, label: str,
) -> dict[str, Any]:
    checked_digest(expected_sha256, label)
    require(type(absolute) is str and os.path.isabs(absolute)
            and os.path.abspath(absolute) == absolute
            and os.path.realpath(absolute) == absolute,
            "an exact pinned regular file is mandatory: " + label)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(absolute, flags)
    except OSError as error:
        raise ScannerCommentOracleError(
            "an exact pinned standard source could not be opened: " + label
        ) from error
    try:
        before = os.fstat(descriptor)
        maximum = MAX_BINARY_BYTES if absolute == PINNED_PYTHON else MAX_SOURCE_BYTES
        require(stat.S_ISREG(before.st_mode) and 0 < before.st_size <= maximum,
                "a pinned owner is not a bounded regular file: " + label)
        observed = hashlib.sha256()
        remaining = before.st_size
        while remaining:
            part = os.read(descriptor, min(remaining, 1_048_576))
            require(bool(part), "a pinned source was truncated: " + label)
            observed.update(part)
            remaining -= len(part)
        require(os.read(descriptor, 1) == b"",
                "a pinned source grew during authentication: " + label)
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_size)
                == (after.st_dev, after.st_ino, after.st_size)
                and observed.hexdigest() == expected_sha256,
                "an exact standard source owner was substituted: " + label)
        return {
            "path": absolute,
            "sha256": expected_sha256,
            "bytes": before.st_size,
            "device": before.st_dev,
            "inode": before.st_ino,
        }
    finally:
        os.close(descriptor)


def verify_standard_modules(modules: Mapping[str, Any] | None = None) -> None:
    actual = sys.modules if modules is None else modules
    require(isinstance(actual, Mapping),
            "the complete reference module table is mandatory")
    for name in actual:
        require(type(name) is str
                and name.partition(".")[0] not in FORBIDDEN_ENGINE_ROOTS,
                "a candidate or external matcher entered the standard worker")


def authenticate_standard_reference(
    source_pin: str,
) -> tuple[Any, dict[str, dict[str, Any]]]:
    verify_runtime()
    owners = {
        "oracle": read_pinned_file(
            SOURCE_ABSOLUTE, source_pin, label="frozen scanner-comment oracle"
        ),
        "python": read_pinned_file(
            PINNED_PYTHON, PINNED_PYTHON_SHA256,
            label="pinned stable CPython executable",
        ),
    }
    engine = importlib.import_module("re")
    for name, (filename, source_hash) in PINNED_STDLIB_SOURCES.items():
        absolute = PINNED_STDLIB_DIRECTORY + filename
        module = importlib.import_module(name)
        require(isinstance(module, types.ModuleType)
                and module.__name__ == name
                and getattr(module, "__file__", None) == absolute
                and os.path.realpath(absolute) == absolute,
                "a genuine pinned standard regex module was substituted: "
                + name)
        owners[name] = read_pinned_file(absolute, source_hash, label=name)
    builtin = sys.modules.get("_sre")
    require(isinstance(builtin, types.ModuleType)
            and getattr(getattr(builtin, "__spec__", None), "origin", None)
            == "built-in"
            and engine.__name__ == "re"
            and getattr(engine.compile, "__module__", None) == "re"
            and getattr(engine.Scanner, "__module__", None) == "re",
            "the genuine standard CPython regex oracle was substituted")
    verify_standard_modules()
    return engine, owners


def validate_source_owners(
    value: Any, source_pin: str,
) -> dict[str, dict[str, Any]]:
    require(type(value) is dict
            and set(value) == {"oracle", "python", *PINNED_STDLIB_SOURCES},
            "the complete pinned CPython and parser closure is mandatory")
    expected = {
        "oracle": (SOURCE_ABSOLUTE, source_pin),
        "python": (PINNED_PYTHON, PINNED_PYTHON_SHA256),
    }
    expected.update({
        name: (PINNED_STDLIB_DIRECTORY + filename, source_hash)
        for name, (filename, source_hash) in PINNED_STDLIB_SOURCES.items()
    })
    for name, (path, source_hash) in expected.items():
        owner = value.get(name)
        require(type(owner) is dict and set(owner) == {
            "path", "sha256", "bytes", "device", "inode",
        } and owner.get("path") == path
          and owner.get("sha256") == source_hash
          and type(owner.get("bytes")) is int and owner["bytes"] > 0
          and type(owner.get("device")) is int and owner["device"] >= 0
          and type(owner.get("inode")) is int and owner["inode"] > 0,
          "a pinned source owner was forged: " + name)
    return value


def make_reference_guard(checks: int) -> dict[str, Any]:
    return {
        "candidate_import_count": 0,
        "external_regex_import_count": 0,
        "actual_method_guard_checks": checks,
        "required_method_guard_checks": 2 * CASE_COUNT,
        "future_candidate_guard_relative": V5_GUARD_RELATIVE,
        "future_candidate_guard_sha256": V5_GUARD_SHA256,
        "future_ownership_audit_relative": OWNERSHIP_AUDIT_RELATIVE,
        "future_ownership_audit_sha256": OWNERSHIP_AUDIT_SHA256,
        "future_candidate_guard_installed": False,
    }


def validate_reference_guard(value: Any) -> dict[str, Any]:
    expected = make_reference_guard(2 * CASE_COUNT)
    require(type(value) is dict and value == expected,
            "a complete scanner ownership or standard-reference guard was forged")
    return value


def validate_records(
    matrix: list[dict[str, Any]], records: Any, expected_sha256: str,
) -> list[dict[str, Any]]:
    checked_digest(expected_sha256, "complete scanner-comment observations")
    require(type(records) is list and len(records) == CASE_COUNT,
            "all 2,854 scanner observations must be preserved")
    for case, record in zip(matrix, records, strict=True):
        require(type(record) is dict and set(record) == {
            "case", "cohort", "expected_kind", "outcome",
        } and record.get("case") == case["case"]
          and record.get("cohort") == case["cohort"]
          and record.get("expected_kind") == case["expected_kind"],
          "a scanner observation was omitted, reordered, or relabeled")
        validate_outcome(record["outcome"])
        verify_expected_outcome(case, record["outcome"])
    require(digest(records) == expected_sha256,
            "the complete scanner observation vector was substituted")
    return records


def observe_reference_worker(role: str, source_pin: str) -> dict[str, Any]:
    require(role in {"reference_a", "reference_b"},
            "only an isolated standard-reference worker is permitted")
    checked_digest(source_pin, "frozen scanner-comment source")
    matrix = build_matrix()
    validate_matrix(matrix)
    engine, owners_before = authenticate_standard_reference(source_pin)
    records: list[dict[str, Any]] = []
    checks = 0
    for case in matrix:
        verify_standard_modules()
        checks += 1
        try:
            outcome = execute_case(case, engine)
        finally:
            verify_standard_modules()
            checks += 1
        records.append({
            "case": case["case"],
            "cohort": case["cohort"],
            "expected_kind": case["expected_kind"],
            "outcome": outcome,
        })
    records_sha256 = digest(records)
    validate_records(matrix, records, records_sha256)
    owners_after = authenticate_standard_reference(source_pin)[1]
    require(owners_before == owners_after,
            "a genuine standard owner changed during observation")
    result = {
        "schema": SCHEMA + "-isolated-reference-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": role,
        "pid": os.getpid(),
        "oracle_source_sha256": source_pin,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "semantic_case_count": SEMANTIC_CASE_COUNT,
        "tokenizer_case_count": TOKENIZER_CASE_COUNT,
        "expected_kind_counts": dict(EXPECTED_COUNTS),
        "expected_pattern_error_counts": dict(EXPECTED_NEGATIVE_COUNTS),
        "records_sha256": records_sha256,
        "records": records,
        "source_owners": owners_before,
        "reference_guard": make_reference_guard(checks),
        "actual_reference_workers": 1,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    return validate_reference_worker(
        result, role=role, source_pin=source_pin, matrix=matrix,
        expected_pid=result["pid"],
    )


def validate_reference_worker(
    value: Any,
    *,
    role: str,
    source_pin: str,
    matrix: list[dict[str, Any]],
    expected_pid: int,
) -> dict[str, Any]:
    require(role in {"reference_a", "reference_b"}
            and type(expected_pid) is int and expected_pid > 0,
            "an exact genuine worker role and independent PID are mandatory")
    expected = {
        "schema": SCHEMA + "-isolated-reference-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": role,
        "pid": expected_pid,
        "oracle_source_sha256": source_pin,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "semantic_case_count": SEMANTIC_CASE_COUNT,
        "tokenizer_case_count": TOKENIZER_CASE_COUNT,
        "expected_kind_counts": dict(EXPECTED_COUNTS),
        "expected_pattern_error_counts": dict(EXPECTED_NEGATIVE_COUNTS),
        "actual_reference_workers": 1,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }
    require(type(value) is dict and set(value) == set(expected) | {
        "records_sha256", "records", "source_owners", "reference_guard",
    }, "a complete genuine reference worker was forged")
    for name, original in expected.items():
        require(value.get(name) == original,
                "a genuine frozen reference field was altered: " + name)
    validate_source_owners(value["source_owners"], source_pin)
    validate_reference_guard(value["reference_guard"])
    validate_records(matrix, value["records"], value["records_sha256"])
    return value


def encode_stream(value: bytes) -> dict[str, Any]:
    require(type(value) is bytes and len(value) <= MAX_PROCESS_BYTES,
            "a complete bounded isolated worker stream is mandatory")
    return {
        "base64": base64.b64encode(value).decode("ascii"),
        "bytes": len(value),
        "sha256": hashlib.sha256(value).hexdigest(),
        "complete": True,
    }


def decode_stream(value: Any, label: str) -> bytes:
    require(type(value) is dict and set(value) == {
        "base64", "bytes", "sha256", "complete",
    } and type(value.get("base64")) is str
      and type(value.get("bytes")) is int
      and 0 <= value["bytes"] <= MAX_PROCESS_BYTES
      and valid_digest(value.get("sha256"))
      and value.get("complete") is True,
      "a complete reversible reference stream was hidden: " + label)
    try:
        actual = base64.b64decode(value["base64"].encode("ascii"), validate=True)
    except (ValueError, UnicodeError) as error:
        raise ScannerCommentOracleError(
            "an isolated worker stream is not canonical base64: " + label
        ) from error
    require(len(actual) == value["bytes"]
            and hashlib.sha256(actual).hexdigest() == value["sha256"]
            and base64.b64encode(actual).decode("ascii") == value["base64"],
            "a complete isolated worker stream was altered: " + label)
    return actual


def validate_process_evidence(
    evidence: Any, worker: Mapping[str, Any], *, role: str,
) -> dict[str, Any]:
    require(type(evidence) is dict and set(evidence) == {
        "role", "pid", "returncode", "stdout", "stderr",
    } and evidence.get("role") == role
      and type(evidence.get("pid")) is int
      and evidence["pid"] > 0
      and evidence["pid"] == worker.get("pid")
      and evidence.get("returncode") == 0,
      "an independent genuine reference process was substituted")
    stdout = decode_stream(evidence["stdout"], role + " stdout")
    stderr = decode_stream(evidence["stderr"], role + " stderr")
    require(stderr == b"" and stdout == canonical(dict(worker)),
            "a complete worker stream differs from its exact observation")
    return evidence


def run_isolated_reference(
    role: str, source_pin: str, matrix: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    require(role in {"reference_a", "reference_b"},
            "a candidate cannot enter the reference-only baseline phase")
    arguments = [
        PINNED_PYTHON, "-I", "-B", SOURCE_ABSOLUTE,
        "--internal-reference-worker", "--role", role,
        "--oracle-source-sha256", source_pin,
        "--matrix-sha256", MATRIX_SHA256,
    ]
    try:
        process = subprocess.Popen(
            arguments,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            cwd=ROOT,
            env={
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONHASHSEED": "0",
                "LC_ALL": "C",
                "PATH": "/usr/bin:/bin",
            },
        )
        stdout, stderr = process.communicate()
    except (OSError, subprocess.SubprocessError) as error:
        raise ReferenceWorkerFailure(
            "an isolated pinned CPython reference could not start",
            {"role": role, "error_type": type(error).__qualname__,
             "error": str(error)},
        ) from error
    evidence = {
        "role": role,
        "pid": process.pid,
        "returncode": process.returncode,
        "stdout": encode_stream(stdout),
        "stderr": encode_stream(stderr),
    }
    if process.returncode != 0 or stderr:
        raise ReferenceWorkerFailure(
            "an isolated genuine standard reference failed", evidence
        )
    try:
        worker = validate_reference_worker(
            decode_canonical(stdout, role),
            role=role,
            source_pin=source_pin,
            matrix=matrix,
            expected_pid=process.pid,
        )
        validate_process_evidence(evidence, worker, role=role)
    except (ScannerCommentOracleError, ValueError, TypeError, KeyError) as error:
        evidence["validation_error"] = {
            "type": type(error).__qualname__, "message": str(error),
        }
        raise ReferenceWorkerFailure(
            "the complete genuine reference evidence was rejected", evidence
        ) from error
    return worker, evidence


def validate_reference_pair(
    first: Mapping[str, Any],
    second: Mapping[str, Any],
    first_process: Mapping[str, Any],
    second_process: Mapping[str, Any],
    *,
    source_pin: str,
    matrix: list[dict[str, Any]],
) -> str:
    validate_reference_worker(
        first, role="reference_a", source_pin=source_pin,
        matrix=matrix, expected_pid=first.get("pid"),
    )
    validate_reference_worker(
        second, role="reference_b", source_pin=source_pin,
        matrix=matrix, expected_pid=second.get("pid"),
    )
    validate_process_evidence(first_process, first, role="reference_a")
    validate_process_evidence(second_process, second, role="reference_b")
    require(first["pid"] != second["pid"]
            and first["source_owners"] == second["source_owners"]
            and first["records_sha256"] == second["records_sha256"]
            and first["records"] == second["records"],
            "two independently isolated standard references disagree")
    return first["records_sha256"]


def run_baseline(source_pin: str, matrix_pin: str) -> dict[str, Any]:
    verify_runtime()
    checked_digest(source_pin, "explicitly frozen scanner-comment source")
    checked_digest(matrix_pin, "explicitly frozen scanner-comment matrix")
    require(matrix_pin == MATRIX_SHA256,
            "the prospectively frozen scanner matrix was substituted")
    matrix = build_matrix()
    validate_matrix(matrix, matrix_pin)
    _, owners_before = authenticate_standard_reference(source_pin)
    first, first_process = run_isolated_reference(
        "reference_a", source_pin, matrix
    )
    second, second_process = run_isolated_reference(
        "reference_b", source_pin, matrix
    )
    records_sha256 = validate_reference_pair(
        first, second, first_process, second_process,
        source_pin=source_pin, matrix=matrix,
    )
    owners_after = authenticate_standard_reference(source_pin)[1]
    require(owners_before == owners_after == first["source_owners"],
            "a pinned standard source changed around baseline observation")
    return {
        "schema": SCHEMA + "-two-reference-baseline",
        "status": "PASS",
        "python": "3.14.6",
        "oracle_source_sha256": source_pin,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "semantic_case_count": SEMANTIC_CASE_COUNT,
        "tokenizer_case_count": TOKENIZER_CASE_COUNT,
        "expected_kind_counts": dict(EXPECTED_COUNTS),
        "expected_pattern_error_counts": dict(EXPECTED_NEGATIVE_COUNTS),
        "baseline_records_sha256": records_sha256,
        "source_owners": owners_before,
        "reference_a": dict(first),
        "reference_b": dict(second),
        "reference_a_process": dict(first_process),
        "reference_b_process": dict(second_process),
        "actual_reference_workers": 2,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


class SourceOnlyBoundary:
    """Deny actual files, candidate imports, clocks, processes and threads."""

    def __init__(self) -> None:
        self.originals: list[tuple[Any, str, Any]] = []
        self.blocked = {
            "file_reads": 0,
            "file_writes": 0,
            "processes": 0,
            "candidate_imports": 0,
            "dynamic_imports": 0,
            "clock_samples": 0,
            "threads": 0,
            "garbage_collections": 0,
            "randomness": 0,
        }

    def install(self, owner: Any, name: str, category: str) -> None:
        if not hasattr(owner, name):
            return
        original = getattr(owner, name)
        self.originals.append((owner, name, original))

        def denied(*args: Any, **kwargs: Any) -> Any:
            selected = category
            if category == "file_reads":
                mode = args[1] if len(args) > 1 else kwargs.get("mode", "r")
                if type(mode) is str and any(x in mode for x in "wax+"):
                    selected = "file_writes"
                elif type(mode) is int and mode & (
                    os.O_WRONLY | os.O_RDWR | os.O_CREAT
                    | os.O_TRUNC | os.O_APPEND
                ):
                    selected = "file_writes"
            elif category == "dynamic_imports" and args:
                target = args[0]
                if type(target) is str and (
                    target == "candidates" or target.startswith("candidates.")
                    or target.partition(".")[0] in FORBIDDEN_ENGINE_ROOTS
                ):
                    selected = "candidate_imports"
            self.blocked[selected] += 1
            raise SourceOnlyError(
                "synthetic scanner-comment controls cannot perform " + selected
            )

        setattr(owner, name, denied)

    def __enter__(self) -> SourceOnlyBoundary:
        protections = (
            (builtins, "open", "file_reads"),
            (io, "open", "file_reads"),
            (os, "open", "file_reads"),
            (os, "stat", "file_reads"),
            (os, "lstat", "file_reads"),
            (os, "scandir", "file_reads"),
            (os, "listdir", "file_reads"),
            (os, "readlink", "file_reads"),
            (os, "replace", "file_writes"),
            (os, "rename", "file_writes"),
            (os, "remove", "file_writes"),
            (os, "unlink", "file_writes"),
            (os, "mkdir", "file_writes"),
            (os, "makedirs", "file_writes"),
            (subprocess, "Popen", "processes"),
            (subprocess, "run", "processes"),
            (os, "system", "processes"),
            (os, "fork", "processes"),
            (os, "posix_spawn", "processes"),
            (threading.Thread, "start", "threads"),
            (time, "time", "clock_samples"),
            (time, "time_ns", "clock_samples"),
            (time, "monotonic", "clock_samples"),
            (time, "monotonic_ns", "clock_samples"),
            (time, "perf_counter", "clock_samples"),
            (time, "perf_counter_ns", "clock_samples"),
            (gc, "collect", "garbage_collections"),
            (os, "urandom", "randomness"),
            (importlib, "import_module", "dynamic_imports"),
            (builtins, "__import__", "dynamic_imports"),
        )
        for owner, name, category in protections:
            self.install(owner, name, category)
        return self

    def __exit__(self, error_type: Any, error: Any, trace: Any) -> bool:
        del error_type, error, trace
        for owner, name, original in reversed(self.originals):
            setattr(owner, name, original)
        self.originals.clear()
        return False


def synthetic_source_owners(source_pin: str) -> dict[str, dict[str, Any]]:
    values = {
        "oracle": (SOURCE_ABSOLUTE, source_pin),
        "python": (PINNED_PYTHON, PINNED_PYTHON_SHA256),
    }
    values.update({
        name: (PINNED_STDLIB_DIRECTORY + filename, source_hash)
        for name, (filename, source_hash) in PINNED_STDLIB_SOURCES.items()
    })
    return {
        name: {
            "path": path,
            "sha256": source_hash,
            "bytes": 4096 + index,
            "device": 7,
            "inode": 1000 + index,
        }
        for index, (name, (path, source_hash)) in enumerate(values.items())
    }


def synthetic_pattern(flags: int) -> dict[str, Any]:
    return {
        "kind": "compiled-pattern",
        "pattern": normalize_value(None),
        "flags": flags,
        "groups": 2,
        "groupindex": normalize_value({}),
    }


def synthetic_event(
    branch: int, token: str | bytes, subject: str | bytes, flags: int,
) -> dict[str, Any]:
    pattern = synthetic_pattern(flags)
    start = 0 if branch == 0 else 1
    end = start + len(token)
    missing = normalize_value(None)
    groups = [missing, missing]
    groups[branch] = normalize_value(token)
    return {
        "branch": branch,
        "token": normalize_value(token),
        "combined_pattern": pattern,
        "match_uses_combined_pattern": True,
        "match": {
            "kind": "match",
            "pattern": pattern,
            "string": normalize_value(subject),
            "group": normalize_value(token),
            "groups": groups,
            "spans": [[start, end]] + [
                [start, end] if index == branch else [-1, -1]
                for index in range(2)
            ],
            "groupdict": normalize_value({}),
            "lastindex": branch + 1,
            "lastgroup": None,
            "pos": 0,
            "endpos": len(subject),
        },
    }


def synthetic_outcome(case: Mapping[str, Any]) -> dict[str, Any]:
    subject = decode_subject(case["subject"])
    expected = case["expected_kind"]
    if expected == "continued-comment-unterminated":
        return {
            "status": "raise",
            "exception": {
                "kind": "public-regex-error",
                "type": "PatternError",
                "args": normalize_value(("synthetic unterminated subpattern",)),
                "message": "synthetic unterminated subpattern",
                "pattern": normalize_value(decode_subject(case["phrase"])),
                "position": 0,
                "line": 1,
                "column": 1,
            },
            "callbacks": [],
            "warnings": [],
            "combined_pattern": None,
        }
    callbacks = (
        [] if expected == "continued-comment-empty"
        else [synthetic_event(0, subject, subject, case["flags"])]
        if expected == "full-match"
        else [
            synthetic_event(0, subject[:1], subject, case["flags"]),
            synthetic_event(1, subject[1:], subject, case["flags"]),
        ]
    )
    tokens = [
        (event["branch"], subject if len(callbacks) == 1
         else subject[event["branch"]:event["branch"] + 1])
        for event in callbacks
    ]
    remainder = subject if not callbacks else subject[:0]
    return {
        "status": "return",
        "value": normalize_value((tokens, remainder)),
        "callbacks": callbacks,
        "warnings": [],
        "combined_pattern": synthetic_pattern(case["flags"]),
    }


def synthetic_records(matrix: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{
        "case": case["case"],
        "cohort": case["cohort"],
        "expected_kind": case["expected_kind"],
        "outcome": synthetic_outcome(case),
    } for case in matrix]


def synthetic_reference(
    role: str,
    pid: int,
    source_pin: str,
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-isolated-reference-worker",
        "status": "OBSERVED",
        "python": "3.14.6",
        "role": role,
        "pid": pid,
        "oracle_source_sha256": source_pin,
        "matrix_sha256": MATRIX_SHA256,
        "published_seed": PUBLISHED_SEED,
        "case_count": CASE_COUNT,
        "semantic_case_count": SEMANTIC_CASE_COUNT,
        "tokenizer_case_count": TOKENIZER_CASE_COUNT,
        "expected_kind_counts": dict(EXPECTED_COUNTS),
        "expected_pattern_error_counts": dict(EXPECTED_NEGATIVE_COUNTS),
        "records_sha256": digest(records),
        "records": records,
        "source_owners": synthetic_source_owners(source_pin),
        "reference_guard": make_reference_guard(2 * CASE_COUNT),
        "actual_reference_workers": 1,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def synthetic_process(worker: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "role": worker["role"],
        "pid": worker["pid"],
        "returncode": 0,
        "stdout": encode_stream(canonical(dict(worker))),
        "stderr": encode_stream(b""),
    }


def synthetic_candidate_pins(family: str) -> dict[str, str]:
    require(family in {"rust", "c", "zig"},
            "a real independent synthetic family is mandatory")
    adapters = {
        "rust": "candidates/rust_candidate.py",
        "c": "candidates/vm_candidate.py",
        "zig": "candidates/zig_candidate.py",
    }
    engines = {
        "rust": "candidates/_rust_engine.so",
        "c": "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
        "zig": "candidates/_zig_probe.so",
    }
    bridges = {
        "rust": "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "c": "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
        "zig": "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
    }
    return {
        "family": family,
        "adapter_relative": adapters[family],
        "adapter_sha256": "12" * 32,
        "engine_relative": engines[family],
        "engine_sha256": "34" * 32,
        "bridge_relative": bridges[family],
        "bridge_sha256": "34" * 32 if family == "c" else "56" * 32,
        "v5_guard_relative": V5_GUARD_RELATIVE,
        "v5_guard_sha256": V5_GUARD_SHA256,
        "ownership_audit_relative": OWNERSHIP_AUDIT_RELATIVE,
        "ownership_audit_sha256": OWNERSHIP_AUDIT_SHA256,
    }


def source_self_test() -> dict[str, Any]:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True
            and os.path.abspath(sys.executable) == PINNED_PYTHON
            and os.path.abspath(__file__) == SOURCE_ABSOLUTE,
            "run source-only controls on exact isolated pinned CPython 3.14.6")
    require(not any(
        name.partition(".")[0] in FORBIDDEN_ENGINE_ROOTS
        for name in sys.modules
    ), "a candidate or external regex entered a source-only process")
    accepted: list[str] = []
    rejected: list[str] = []

    def accept(name: str, condition: Any) -> None:
        require(type(name) is str and name not in accepted and bool(condition),
                "a source-only scanner positive control failed: " + name)
        accepted.append(name)

    def reject(name: str, action: Callable[[], Any]) -> None:
        require(type(name) is str and name not in rejected and callable(action),
                "a source-only scanner rejection control was duplicated")
        try:
            action()
        except (
            ScannerCommentOracleError, TypeError, ValueError, KeyError,
            OSError, OverflowError,
        ):
            rejected.append(name)
            return
        raise ScannerCommentOracleError(
            "a forged source-only scanner control was accepted: " + name
        )

    with SourceOnlyBoundary() as boundary:
        matrix = build_matrix()
        observed_matrix = digest(matrix)
        if not valid_digest(MATRIX_SHA256):
            return {
                "schema": SCHEMA + "-synthetic-self-test",
                "status": "UNFROZEN",
                "python": "3.14.6",
                "published_seed": PUBLISHED_SEED,
                "case_count": CASE_COUNT,
                "semantic_case_count": SEMANTIC_CASE_COUNT,
                "tokenizer_case_count": TOKENIZER_CASE_COUNT,
                "observed_matrix_sha256": observed_matrix,
                "actual_reference_workers": 0,
                "actual_candidate_workers": 0,
                "actual_candidate_imports": 0,
                "clock_samples": 0,
                "timing_trials_run": 0,
                "workspace_files_written": 0,
                "evidence_files_created": 0,
                "benchmark_files_read": 0,
                "hidden_cases_read": 0,
                "performance": "NOT MEASURED",
            }

        accept("freeze-every-original-2560-comment-and-294-tokenizer-case",
               validate_matrix(matrix) == MATRIX_SHA256)
        accept("freeze-the-exact-independent-public-seed",
               PUBLISHED_SEED == 0x5343_4E56_4552_5631)
        accept("retain-all-2612-complete-original-matches",
               sum(row["expected_kind"] == "full-match" for row in matrix)
               == 2_612)
        accept("retain-all-32-real-escaped-newline-zero-width-scans",
               sum(row["expected_kind"] == "continued-comment-empty"
                   for row in matrix) == 32)
        accept("retain-all-108-real-prefix-and-fallback-scans",
               sum(row["expected_kind"] == "prefix-then-fallback"
                   for row in matrix) == 108)
        for cohort, expected in EXPECTED_NEGATIVE_COUNTS.items():
            accept("preserve-every-genuine-" + cohort + "-pattern-error",
                   sum(row["cohort"] == cohort
                       and row["expected_kind"]
                       == "continued-comment-unterminated"
                       for row in matrix) == expected)
        accept("preserve-both-text-and-bytes-equally",
               sum(row["domain"] == "str" for row in matrix)
               == sum(row["domain"] == "bytes" for row in matrix)
               == CASE_COUNT // 2)
        accept("preserve-all-five-root-global-scoped-and-nested-flag-states",
               {row["context"] for row in matrix
                if row["cohort"] == "semantic"} == set(SEMANTIC_CONTEXTS))
        accept("preserve-all-seven-python-tokenizer-line-endings",
               {row["line_ending"] for row in matrix
                if row["cohort"] == "tokenizer"}
               == {name for name, _ in TOKENIZER_ENDINGS})
        accept("preserve-all-seven-exact-backslash-parities",
               {row["slash_count"] for row in matrix
                if row["cohort"] == "tokenizer"} == set(range(7)))
        accept("preserve-every-original-capture-backreference-and-conditional",
               {row["tail"] for row in matrix
                if row["cohort"] == "semantic"}
               == {name for name, _, _ in SEMANTIC_TAILS})
        accept("preserve-every-adversarial-verbatim-comment-payload",
               {row["payload_index"] for row in matrix
                if row["cohort"] == "semantic"}
               == set(range(len(COMMENT_PAYLOADS))))
        accept("distinguish-original-bytes-and-bytearray",
               normalize_value(b"a") != normalize_value(bytearray(b"a")))
        accept("distinguish-readonly-and-writable-memory-carriers",
               normalize_value(memoryview(b"a"))
               != normalize_value(memoryview(bytearray(b"a"))))
        accept("preserve-strided-memory-shape-and-layout",
               normalize_value(memoryview(b"abcd")[::2])["strides"] == [2]
               and normalize_value(memoryview(b"abcd")[::2])["hex"] == "6163")
        accept("distinguish-boolean-and-integer-observations",
               normalize_value(True) != normalize_value(1))
        accept("distinguish-tuple-and-list-observations",
               normalize_value((1,)) != normalize_value([1]))
        accept("preserve-lone-unicode-surrogates",
               b"\\ud800" in canonical(normalize_value("\ud800")))
        accept("preserve-canonically-distinct-unicode-spellings",
               normalize_value("e\u0301") != normalize_value("\u00e9"))

        source_pin = "12" * 32
        records = synthetic_records(matrix)
        records_pin = digest(records)
        accept("validate-all-complete-synthetic-observations-without-an-engine",
               validate_records(matrix, records, records_pin) is records)
        first = synthetic_reference("reference_a", 41001, source_pin, records)
        second = synthetic_reference("reference_b", 41002, source_pin, records)
        first_process = synthetic_process(first)
        second_process = synthetic_process(second)
        accept("require-two-distinct-reference-process-identities",
               validate_reference_pair(
                   first, second, first_process, second_process,
                   source_pin=source_pin, matrix=matrix,
               ) == records_pin)
        accept("retain-full-reversible-synthetic-reference-stdout",
               decode_stream(first_process["stdout"], "synthetic reference")
               == canonical(first))
        accept("retain-an-empty-exact-standard-reference-stderr",
               decode_stream(first_process["stderr"], "synthetic stderr")
               == b"")
        accept("require-continuous-standard-method-ownership-checks",
               validate_reference_guard(
                   make_reference_guard(2 * CASE_COUNT)
               )["actual_method_guard_checks"] == 2 * CASE_COUNT)

        for family in ("rust", "c", "zig"):
            pins = synthetic_candidate_pins(family)
            accept("preserve-an-independent-future-" + family + "-native-owner",
                   validate_future_candidate_pins(pins) == pins)
            for field, forged in (
                ("adapter_relative", "candidates/foreign_candidate.py"),
                ("adapter_sha256", "f" * 64),
                ("engine_relative", "candidates/foreign_engine.so"),
                ("engine_sha256", "invalid"),
                ("bridge_relative", "candidates/foreign_bridge.so"),
                ("bridge_sha256", "invalid"),
                ("v5_guard_relative", "tools/foreign_guard.py"),
                ("v5_guard_sha256", "a" * 64),
                ("ownership_audit_relative", "tools/foreign_audit.py"),
                ("ownership_audit_sha256", "b" * 64),
            ):
                changed = dict(pins)
                changed[field] = forged
                reject("reject-" + family + "-foreign-" + field,
                       lambda changed=changed:
                       validate_future_candidate_pins(changed))

        reject("reject-an-altered-public-scanner-seed",
               lambda: validate_matrix(build_matrix(PUBLISHED_SEED + 1)))
        reject("reject-a-missing-original-scanner-case",
               lambda: validate_matrix(matrix[:-1]))
        reject("reject-an-added-original-scanner-case",
               lambda: validate_matrix(matrix + [matrix[0]]))
        reject("reject-a-reordered-frozen-original-scanner-case",
               lambda: validate_matrix(matrix[1:] + matrix[:1]))
        reject("reject-a-duplicate-frozen-original-scanner-case",
               lambda: validate_matrix([matrix[0], *matrix[2:], matrix[0]]))
        original = matrix[0]
        for field, changed in (
            ("case", original["case"] + "/forged"),
            ("cohort", "hidden"),
            ("context", "hidden"),
            ("domain", "memoryview"),
            ("flags", original["flags"] | 2),
            ("phrase", {"kind": "bytes", "hex": "0A"}),
            ("subject", {"kind": "bytes", "hex": "0A"}),
            ("line_ending", "hidden"),
            ("tail", "hidden"),
            ("payload_index", 99),
            ("slash_count", 99),
            ("expected_kind", "hidden"),
            ("seed", PUBLISHED_SEED + 1),
        ):
            forged_case = dict(original)
            forged_case[field] = changed
            reject("reject-a-forged-frozen-scanner-case-" + field,
                   lambda forged_case=forged_case:
                   validate_matrix([forged_case, *matrix[1:]]))

        reject("reject-truncated-original-scanner-outcomes",
               lambda: validate_records(matrix, records[:-1], records_pin))
        reject("reject-reordered-original-scanner-outcomes",
               lambda: validate_records(
                   matrix, records[1:] + records[:1], records_pin
               ))
        reject("reject-a-substituted-complete-outcome-digest",
               lambda: validate_records(matrix, records, "98" * 32))
        for field, changed in (
            ("role", "reference_b"),
            ("pid", 41002),
            ("oracle_source_sha256", "98" * 32),
            ("matrix_sha256", "98" * 32),
            ("published_seed", PUBLISHED_SEED + 1),
            ("case_count", CASE_COUNT - 1),
            ("semantic_case_count", SEMANTIC_CASE_COUNT - 1),
            ("tokenizer_case_count", TOKENIZER_CASE_COUNT - 1),
            ("actual_reference_workers", 0),
            ("actual_candidate_workers", 1),
            ("actual_candidate_imports", 1),
            ("clock_samples", 1),
            ("timing_trials_run", 1),
            ("workspace_files_written", 1),
            ("evidence_files_created", 1),
            ("benchmark_files_read", 1),
            ("hidden_cases_read", 1),
            ("performance", "MEASURED"),
            ("candidate_qualified_for_hidden_benchmark", True),
            ("final_winner_selected", True),
            ("records_sha256", "98" * 32),
        ):
            changed_worker = dict(first)
            changed_worker[field] = changed
            reject("reject-a-forged-standard-worker-" + field,
                   lambda changed_worker=changed_worker:
                   validate_reference_worker(
                       changed_worker, role="reference_a",
                       source_pin=source_pin, matrix=matrix,
                       expected_pid=41001,
                   ))

        for field, changed in (
            ("candidate_import_count", 1),
            ("external_regex_import_count", 1),
            ("actual_method_guard_checks", 2 * CASE_COUNT - 1),
            ("required_method_guard_checks", 2 * CASE_COUNT - 1),
            ("future_candidate_guard_relative", "tools/foreign_guard.py"),
            ("future_candidate_guard_sha256", "98" * 32),
            ("future_ownership_audit_relative", "tools/foreign_audit.py"),
            ("future_ownership_audit_sha256", "98" * 32),
            ("future_candidate_guard_installed", True),
        ):
            forged_guard = make_reference_guard(2 * CASE_COUNT)
            forged_guard[field] = changed
            reject("reject-a-forged-native-ownership-guard-" + field,
                   lambda forged_guard=forged_guard:
                   validate_reference_guard(forged_guard))

        reject("reject-duplicate-canonical-worker-fields",
               lambda: decode_canonical(b'{"value":1,"value":2}\n',
                                        "duplicate synthetic field"))
        reject("reject-noncanonical-worker-whitespace",
               lambda: decode_canonical(b'{ "value":1}\n',
                                        "noncanonical synthetic field"))
        reject("reject-nonfinite-worker-numbers",
               lambda: decode_canonical(b'{"value":NaN}\n',
                                        "nonfinite synthetic field"))
        reject("reject-an-incomplete-reference-stream",
               lambda: decode_stream(
                   {**first_process["stdout"], "complete": False},
                   "incomplete synthetic stream",
               ))
        reject("reject-a-truncated-reference-stream",
               lambda: decode_stream(
                   {**first_process["stdout"],
                    "bytes": first_process["stdout"]["bytes"] - 1},
                   "truncated synthetic stream",
               ))
        reject("reject-the-same-pid-for-both-references",
               lambda: validate_reference_pair(
                   first, {**second, "pid": first["pid"]},
                   first_process, second_process,
                   source_pin=source_pin, matrix=matrix,
               ))
        reject("reject-a-substituted-reference-output-stream",
               lambda: validate_process_evidence(
                   {**first_process, "stdout": second_process["stdout"]},
                   first, role="reference_a",
               ))

        reject("block-real-workspace-file-reads",
               lambda: builtins.open(SOURCE_ABSOLUTE, "rb"))
        reject("block-all-workspace-file-writes",
               lambda: builtins.open(SOURCE_ABSOLUTE, "wb"))
        reject("block-real-filesystem-stat", lambda: os.stat(SOURCE_ABSOLUTE))
        reject("block-all-native-candidate-imports",
               lambda: importlib.import_module("candidates.zig_candidate"))
        reject("block-external-regex-package-imports",
               lambda: importlib.import_module("regex"))
        reject("block-stdlib-imports-during-synthetic-controls",
               lambda: importlib.import_module("re"))
        reject("block-all-genuine-reference-workers",
               lambda: subprocess.Popen([PINNED_PYTHON, "-I", "-B"]))
        reject("block-background-worker-threads",
               lambda: threading.Thread(target=lambda: None).start())
        reject("block-wall-clock-sampling", lambda: time.time())
        reject("block-monotonic-clock-sampling", lambda: time.monotonic())
        reject("block-performance-clock-sampling", lambda: time.perf_counter())
        reject("block-operating-system-randomness", lambda: os.urandom(1))
        reject("block-garbage-collection-side-effects", lambda: gc.collect())

        blocked = dict(boundary.blocked)
        accept("exercise-every-real-source-only-effects-protection",
               all(blocked[name] > 0 for name in (
                   "file_reads", "file_writes", "processes",
                   "candidate_imports", "dynamic_imports", "clock_samples",
                   "threads", "garbage_collections", "randomness",
               )))
        accept("load-no-candidate-or-external-regex-module",
               not any(name.partition(".")[0] in FORBIDDEN_ENGINE_ROOTS
                       for name in sys.modules))

    return {
        "schema": SCHEMA + "-synthetic-self-test",
        "status": "PASS",
        "python": "3.14.6",
        "published_seed": PUBLISHED_SEED,
        "matrix_sha256": MATRIX_SHA256,
        "case_count": CASE_COUNT,
        "semantic_case_count": SEMANTIC_CASE_COUNT,
        "tokenizer_case_count": TOKENIZER_CASE_COUNT,
        "expected_kind_counts": dict(EXPECTED_COUNTS),
        "expected_pattern_error_counts": dict(EXPECTED_NEGATIVE_COUNTS),
        "positive_control_count": len(accepted),
        "negative_control_count": len(rejected),
        "positive_controls": accepted,
        "negative_controls": rejected,
        "source_only_blocked_operations": blocked,
        "future_candidate_guard_relative": V5_GUARD_RELATIVE,
        "future_candidate_guard_sha256": V5_GUARD_SHA256,
        "future_ownership_audit_relative": OWNERSHIP_AUDIT_RELATIVE,
        "future_ownership_audit_sha256": OWNERSHIP_AUDIT_SHA256,
        "actual_reference_workers": 0,
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_files_written": 0,
        "evidence_files_created": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_hidden_benchmark": False,
        "final_winner_selected": False,
    }


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Frozen scanner comments and escaped-newline correctness",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true",
                       help="run only effect-blocked in-memory controls")
    modes.add_argument("--baseline", action="store_true",
                       help="explicitly run exactly two standard references")
    modes.add_argument("--internal-reference-worker", action="store_true",
                       help=argparse.SUPPRESS)
    parser.add_argument("--role", choices=("reference_a", "reference_b"))
    parser.add_argument("--oracle-source-sha256")
    parser.add_argument("--matrix-sha256")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    try:
        if options.self_test:
            require(options.role is None
                    and options.oracle_source_sha256 is None
                    and options.matrix_sha256 is None,
                    "source-only controls cannot select a worker or engine")
            result = source_self_test()
            sys.stdout.buffer.write(canonical(result))
            return 0 if result["status"] == "PASS" else 2

        checked_digest(options.oracle_source_sha256,
                       "explicitly pinned scanner-comment oracle source")
        checked_digest(options.matrix_sha256,
                       "explicitly pinned scanner-comment case matrix")
        require(options.matrix_sha256 == MATRIX_SHA256,
                "the frozen original scanner-comment matrix was substituted")
        if options.internal_reference_worker:
            require(options.role in {"reference_a", "reference_b"},
                    "an isolated standard-reference worker role is mandatory")
            result = observe_reference_worker(
                options.role, options.oracle_source_sha256
            )
        else:
            require(options.baseline and options.role is None,
                    "only exactly two genuine baseline workers are permitted")
            result = run_baseline(
                options.oracle_source_sha256, options.matrix_sha256
            )
        sys.stdout.buffer.write(canonical(result))
        return 0
    except ReferenceWorkerFailure as error:
        sys.stdout.buffer.write(canonical({
            "schema": SCHEMA + "-failure",
            "status": "FAIL",
            "error_type": type(error).__qualname__,
            "error": str(error),
            "complete_reference_worker_failure": error.evidence,
            "actual_candidate_workers": 0,
            "actual_candidate_imports": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "workspace_files_written": 0,
            "evidence_files_created": 0,
            "benchmark_files_read": 0,
            "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
        }))
        return 1
    except (ScannerCommentOracleError, OSError, ValueError, TypeError) as error:
        sys.stdout.buffer.write(canonical({
            "schema": SCHEMA + "-failure",
            "status": "FAIL",
            "error_type": type(error).__qualname__,
            "error": str(error),
            "actual_candidate_workers": 0,
            "actual_candidate_imports": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "workspace_files_written": 0,
            "evidence_files_created": 0,
            "benchmark_files_read": 0,
            "hidden_cases_read": 0,
            "performance": "NOT MEASURED",
        }))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
