#!/usr/bin/env python3
"""Independent, frozen PUBLIC DEVELOPMENT PRACTICE ONLY; never a final holdout.

Every case originates in literals and a published seed in this source.  Source
verification imports no matching engine, starts no subprocess, reads no case or
benchmark file, samples no clock, and writes nothing.  The standard-library
oracle and the named Rust candidate are imported only in explicitly requested,
separate pinned-CPython worker processes.  No external regex package is used.
"""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import importlib
from importlib.machinery import EXTENSION_SUFFIXES, ExtensionFileLoader
import inspect
import json
import math
import os
from pathlib import Path, PurePosixPath
import random
import stat
import statistics
import subprocess
import sys
import types
from typing import Any, Callable, Mapping
import warnings


ROOT = Path("/home/dev-user/src/rebar")
if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))

PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14",
)
PINNED_STDLIB_RE = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
    "lib/python3.14/re/__init__.py",
)
SOURCE_RELATIVE = "tools/rust_public_practice_benchmark_v2.py"
OUTPUT_PREFIX = "experiments/rust_public_practice_v2"
SCHEMA = "rebar-rust-independent-public-practice-v2"
PRACTICE_LABEL = (
    "PUBLIC DEVELOPMENT/PRACTICE ONLY; NOT A SEALED, HIDDEN, OR FINAL HOLDOUT"
)
PUBLISHED_SEED = 0x5245_4241_525F_5032
MATRIX_SHA256 = "0c88d1ec7066ede05466c1a91126086cd52256548eda13a31778ff284439d97d"
DEFAULT_PAIRED_TRIALS = 8
DEFAULT_BATCH_ITERATIONS = 4
DEFAULT_WARMUP_ITERATIONS = 1
BOOTSTRAP_RESAMPLES = 400
MAX_PROCESS_BYTES = 64 * 1024 * 1024
MAX_OUTPUT_BYTES = 256 * 1024 * 1024
WORKER_TIMEOUT_SECONDS = 300

# Public CPython flag integers, intentionally defined without importing ``re``.
IGNORECASE = 2
MULTILINE = 8
DOTALL = 16
VERBOSE = 64
ASCII = 256

OPERATIONS = (
    "module.compile",
    "module.compile.flags_keyword",
    "module.compile.identity",
    "module.cache.repeated_identity",
    "module.cache.purge_compile",
    "module.cache.alternating_compile",
    "module.search",
    "module.search.flags_keyword",
    "module.match",
    "module.fullmatch",
    "module.findall",
    "module.finditer",
    "module.split",
    "module.split.positional",
    "module.split.unlimited",
    "module.sub.literal",
    "module.sub.positional",
    "module.sub.unlimited",
    "module.sub.template_named",
    "module.sub.callback",
    "module.sub.callback_error",
    "module.sub.buffer_exporter",
    "module.sub.buffer_changing_subject",
    "module.sub.invalid_replacement_precedence",
    "module.subn.literal",
    "module.subn.positional",
    "module.subn.template_named",
    "module.subn.callback",
    "module.subn.callback_error",
    "module.escape.pattern",
    "module.escape.subject",
    "module.flags.constants",
    "pattern.search",
    "pattern.search.pos_endpos",
    "pattern.search.negative_bounds",
    "pattern.match",
    "pattern.match.pos_endpos",
    "pattern.fullmatch",
    "pattern.fullmatch.pos_endpos",
    "pattern.findall",
    "pattern.findall.pos_endpos",
    "pattern.finditer",
    "pattern.finditer.pos_endpos",
    "pattern.split",
    "pattern.split.unlimited",
    "pattern.sub.literal",
    "pattern.sub.template_named",
    "pattern.sub.template_numeric",
    "pattern.sub.callback",
    "pattern.sub.callback_error",
    "pattern.sub.buffer_exporter",
    "pattern.sub.buffer_changing_subject",
    "pattern.sub.invalid_replacement_precedence",
    "pattern.subn.literal",
    "pattern.subn.template_named",
    "pattern.subn.callback",
    "pattern.subn.callback_error",
    "pattern.scanner.search",
    "pattern.scanner.match",
    "pattern.scanner.loop",
    "pattern.scanner.bounded",
    "pattern.scanner.reduce_ex.negative",
    "pattern.scanner.reduce_ex.zero",
    "pattern.scanner.reduce_ex.one",
    "pattern.scanner.reduce_ex.two",
    "pattern.scanner.reduce_ex.five",
    "pattern.scanner.reduce_ex.string",
    "pattern.scanner.reduce_ex.overflow",
    "pattern.properties",
    "pattern.groupindex",
    "pattern.flags",
    "pattern.copy",
    "pattern.deepcopy",
    "pattern.method_signature.search",
    "pattern.method_signature.match",
    "pattern.method_signature.fullmatch",
    "pattern.method_signature.findall",
    "pattern.method_signature.finditer",
    "pattern.method_signature.split",
    "pattern.method_signature.sub",
    "pattern.method_signature.subn",
    "pattern.method_signature.scanner",
    "match.group.default",
    "match.group.zero",
    "match.group.named",
    "match.group.multiple",
    "match.group.index_error",
    "match.groups.default",
    "match.groupdict.default",
    "match.start_end_span",
    "match.span.named",
    "match.expand.named",
    "match.expand.numeric",
    "match.getitem.zero",
    "match.getitem.named",
    "match.getitem.index_error",
    "match.properties",
    "match.regs",
    "scanner.scan",
    "scanner.scan.callback_error",
    "scanner.scan.skipping",
    "scanner.scan.no_action",
    "scanner.scan.empty_remainder",
    "lifecycle.compile_fresh.search",
    "lifecycle.compile_fresh.fullmatch",
    "lifecycle.cache_hot.search",
    "lifecycle.cache_hot.compile",
    "lifecycle.cache_churn.search",
    "lifecycle.precompiled.reuse",
    "lifecycle.scanner_recreate.search",
    "lifecycle.module_repeated.search",
)


class PublicPracticeError(Exception):
    """Reject an altered public matrix, observation, worker, or output path."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise PublicPracticeError(message)


FORBIDDEN_REGEX_PACKAGE_ROOTS = frozenset({
    "regex", "_regex", "re2", "google_re2", "rure", "pcre", "pcre2",
    "oniguruma", "onigurumacffi", "hyperscan",
})


def stdlib_regex_modules() -> dict[str, Any]:
    """Record incidental harness imports without treating them as oracle calls."""
    return {
        name: module for name, module in sys.modules.items()
        if name in ("re", "_sre")
        or name.startswith("re.") or name.startswith("_sre.")
    }


def reject_external_regex_packages() -> None:
    foreign = sorted(
        name for name in sys.modules
        if name.partition(".")[0] in FORBIDDEN_REGEX_PACKAGE_ROOTS
    )
    require(not foreign,
            "an external matching package entered first-party public practice: "
            + ", ".join(foreign))


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, allow_nan=False, ensure_ascii=True,
        separators=(",", ":"), sort_keys=True,
    ).encode("ascii") + b"\n"


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    actual: dict[str, Any] = {}
    for key, value in pairs:
        require(type(key) is str and key not in actual,
                "duplicate canonical public-process keys are forbidden")
        actual[key] = value
    return actual


def decode_canonical(payload: bytes, label: str) -> dict[str, Any]:
    require(type(payload) is bytes and 0 < len(payload) <= MAX_PROCESS_BYTES,
            "one complete bounded public-process document is required: " + label)
    try:
        actual = json.loads(
            payload, object_pairs_hook=_unique_object,
            parse_constant=lambda value: (_ for _ in ()).throw(
                PublicPracticeError("nonfinite public evidence is forbidden"),
            ),
        )
    except (ValueError, TypeError, UnicodeError, json.JSONDecodeError) as error:
        raise PublicPracticeError(
            "invalid, incomplete, or noncanonical public evidence: " + label,
        ) from error
    require(type(actual) is dict and canonical(actual) == payload,
            "truncated, concatenated, or noncanonical public evidence: " + label)
    return actual


def typed_text(value: str) -> dict[str, str]:
    require(type(value) is str, "a genuine public text literal is mandatory")
    return {"type": "str", "value": value}


def typed_bytes(value: bytes) -> dict[str, str]:
    require(type(value) is bytes, "a genuine public bytes literal is mandatory")
    return {"type": "bytes", "hex": value.hex()}


def encode_subject(value: Any) -> dict[str, Any]:
    if type(value) is str:
        return typed_text(value)
    if type(value) is bytes:
        return typed_bytes(value)
    if type(value) is bytearray:
        return {"type": "bytearray", "hex": bytes(value).hex()}
    if type(value) is memoryview:
        require(value.format == "B" and value.ndim == 1 and value.contiguous,
                "only an authentic public byte memoryview is permitted")
        return {
            "type": "memoryview", "hex": value.tobytes().hex(),
            "readonly": value.readonly, "format": value.format,
            "shape": list(value.shape) if value.shape is not None else None,
        }
    raise PublicPracticeError("a public str/bytes/buffer subject was substituted")


def materialize_typed(value: Any) -> str | bytes | bytearray | memoryview:
    require(type(value) is dict, "an exact original typed public value is required")
    if set(value) == {"type", "value"} and value.get("type") == "str":
        require(type(value["value"]) is str,
                "a genuine original public text value was replaced")
        return value["value"]
    if set(value) == {"type", "hex"} \
            and value.get("type") in ("bytes", "bytearray"):
        require(type(value["hex"]) is str,
                "a genuine original public byte encoding was replaced")
        try:
            actual = bytes.fromhex(value["hex"])
        except ValueError as error:
            raise PublicPracticeError("invalid original public byte encoding") from error
        require(actual.hex() == value["hex"],
                "the original public byte encoding must be canonical")
        return actual if value["type"] == "bytes" else bytearray(actual)
    if set(value) == {"type", "hex", "readonly", "format", "shape"} \
            and value.get("type") == "memoryview":
        require(type(value.get("hex")) is str
                and type(value.get("readonly")) is bool
                and value.get("format") == "B"
                and type(value.get("shape")) is list
                and len(value["shape"]) == 1,
                "a public memoryview's exact metadata was substituted")
        try:
            actual = bytes.fromhex(value["hex"])
        except ValueError as error:
            raise PublicPracticeError("invalid public memoryview bytes") from error
        require(actual.hex() == value["hex"]
                and value["shape"] == [len(actual)],
                "a public memoryview's canonical bytes or shape changed")
        return memoryview(actual if value["readonly"] else bytearray(actual))
    raise PublicPracticeError("an exact original public value was injected or removed")


def public_datasets() -> tuple[
    tuple[tuple[str, str, str, int, str], ...],
    tuple[tuple[str, bytes, Any, int, str], ...],
]:
    """Return independent, newly authored public literals; read no data files."""
    text = (
        ("text.literal.short", r"(?P<word>[A-Za-z]+)(?P<number>\d*)",
         "alpha12 beta7 gamma003", 0, "short-mixed"),
        ("text.ascii.ignorecase", r"(?P<word>[a-z]+)(?P<number>\d*)",
         "alpha42 BETA7 Gamma003 delta", IGNORECASE, "ascii-casefold"),
        ("text.unicode.words", r"(?P<word>\w+)(?P<number>\d*)",
         "café Δelta_9 naïve 東京42", 0, "unicode-word"),
        ("text.unicode.ascii_boundary", r"\b(?P<word>\w+)(?P<number>\d*)\b",
         "café naïve ASCII_42 mañana", ASCII, "ascii-unicode-boundary"),
        ("text.unicode.combining", r"(?P<word>\w+)(?P<number>\d*)",
         "e\u0301clair9 Ångström7 a\u0308ffin3", 0, "combining-marks"),
        ("text.unicode.astral", r"(?P<word>[\U00010400-\U0001044f]+)(?P<number>\d*)",
         "\U00010400\U00010428 𝔘nicode7 \U00010437\U0001044f19", 0,
         "astral-codepoints"),
        ("text.unicode.kelvin", r"(?P<word>[a-z]+)(?P<number>\d*)",
         "Kelvin4 kelvin7 KELVIN8", IGNORECASE, "unicode-special-casefold"),
        ("text.unicode.long_s", r"(?P<word>[a-z]+)(?P<number>\d*)",
         "ſample12 sample7 SAMPLE3", IGNORECASE, "unicode-special-casefold"),
        ("text.unicode.turkish", r"(?P<word>[i]+)(?P<number>\d*)",
         "İ9 ı8 I7 i6", IGNORECASE, "unicode-turkish-casefold"),
        ("text.unicode.greek", r"(?P<word>[σ]+)(?P<number>\d*)",
         "Σ12 σ7 ς3", IGNORECASE, "unicode-greek-casefold"),
        ("text.unicode.digits", r"(?P<word>[^\W\d_]+)(?P<number>\d+)",
         "item٣٢ other१२ final42", 0, "unicode-decimal-digits"),
        ("text.unicode.spaces", r"(?P<word>\w+)\s+(?P<number>\d+)",
         "alpha\u00a012 beta\u20037 gamma\t003", 0, "unicode-whitespace"),
        ("text.multiline.anchors", r"^(?P<word>[a-z]+)(?P<number>\d*)$",
         "alpha1\nBETA\ngamma22\ndelta9", MULTILINE | IGNORECASE,
         "line-anchors"),
        ("text.dotall.lazy", r"(?P<word>a.+?z)(?P<number>\d*)",
         "a first\nsecond z12 then a final z7", DOTALL, "dotall-lazy"),
        ("text.verbose.groups", r"(?P<word> [a-z]+ ) \s* (?P<number> \d* )",
         "alpha 12 BETA7 gamma 003", VERBOSE | IGNORECASE, "verbose-groups"),
        ("text.lookbehind.fixed", r"(?<=ID:)(?P<word>[A-Z]+)(?P<number>\d+)",
         "ID:AB12 none ID:XY90 ID:CD34", 0, "fixed-lookbehind"),
        ("text.lookahead.negative", r"(?P<word>(?!skip)[a-z]+)(?P<number>\d*)",
         "skip1 keep2 skit3 token4", 0, "negative-lookahead"),
        ("text.alternation.prefix", r"(?P<word>ab|a|abc)(?P<number>\d*)",
         "ab12 a7 abc99 aba3", 0, "alternation-priority"),
        ("text.backreference", r"(?P<word>[a-z]+)-(?P=word)(?P<number>\d*)",
         "echo-echo12 bad-good7 aa-aa3", 0, "named-backreference"),
        ("text.conditional.group", r"(?P<word>[A-Z]+)(?P<number>\d+)?(?(number)!|\?)",
         "AB12! CD? EF7! GH!", 0, "conditional-capture"),
        ("text.atomic.group", r"(?P<word>(?>ab|a))(?P<number>\d*)",
         "ab12 a7 aba99", 0, "atomic-group"),
        ("text.possessive.repeat", r"(?P<word>a++)(?P<number>\d*)",
         "aaaa12 aa7 bbb", 0, "possessive-repeat"),
        ("text.flags.scoped", r"(?P<word>(?i:[a-z]+))(?P<number>\d*)",
         "alpha12 BETA7 Gamma3", 0, "scoped-inline-flags"),
        ("text.absolute.anchors", r"\A(?P<word>[A-Za-z]+)-(?P<number>\d+)\Z",
         "alpha-123", 0, "absolute-full-string"),
        ("text.boundary.repeated", r"\b(?P<word>[A-Za-z_]+)(?P<number>\d*)\b",
         "prefix_42 middle7 suffix_003 " * 6, ASCII, "repeated-word-boundaries"),
        ("text.nested.repeats", r"(?P<word>(?:ab){1,4})(?P<number>\d*)",
         "abab12 ab7 ababab3 none", 0, "bounded-nested-repeats"),
        ("text.email.like", r"(?P<word>[A-Za-z._+-]+)@(?:example|test)\.(?P<number>\d*)",
         "alice@example.42 bob+tag@test.7 bad@other.9", 0, "email-shaped"),
        ("text.path.like", r"/(?P<word>[A-Za-z_-]+)/(?P<number>\d+)",
         "/users/42 /teams/7 /misc/003", 0, "route-shaped"),
        ("text.json.like", r'"(?P<word>[A-Za-z_]+)"\s*:\s*(?P<number>\d+)',
         '{"alpha": 12, "beta":7, "gamma": 003}', 0, "structured-log"),
        ("text.scanner.remainder", r"(?P<word>[A-Za-z]+)(?P<number>\d*)",
         "alpha12 beta7 !unconsumed tail9", 0, "scanner-remainder"),
        ("text.no.match", r"(?P<word>QZX_NEVER_PRESENT)(?P<number>\d+)",
         "alpha12 ordinary words gamma003", 0, "complete-miss"),
        ("text.long.repeated", r"(?P<word>[A-Za-z]+)(?P<number>\d+)",
         "noise alpha42 BETA7 " * 9, IGNORECASE, "long-repeated-haystack"),
        ("text.scanner.scoped_i_enable", r"(?P<word>(?i:a))(?P<number>\d*)",
         "A7 a3", ASCII, "scanner-scoped-ignorecase-enable"),
        ("text.scanner.scoped_i_disable", r"(?P<word>(?-i:a))(?P<number>\d*)",
         "A7 a3", IGNORECASE, "scanner-scoped-ignorecase-disable"),
        ("text.scanner.scoped_s_enable", r"(?P<word>(?s:a.b))(?P<number>\d*)",
         "a\nb7 aXb3", ASCII, "scanner-scoped-dotall-enable"),
        ("text.scanner.scoped_s_disable", r"(?P<word>(?-s:a.b))(?P<number>\d*)",
         "a\nb7 aXb3", DOTALL, "scanner-scoped-dotall-disable"),
        ("text.scanner.scoped_m_enable", r"(?P<word>(?m:^a$))(?P<number>\d*)",
         "a\nx", ASCII, "scanner-scoped-multiline-enable"),
        ("text.scanner.scoped_m_disable", r"(?P<word>(?-m:^a$))(?P<number>\d*)",
         "a\nx", MULTILINE, "scanner-scoped-multiline-disable"),
        ("text.scanner.scoped_a_enable", r"(?P<word>(?a:\w+))(?P<number>\d*)",
         "café42", 0, "scanner-scoped-ascii-enable"),
        ("text.scanner.scoped_u_override", r"(?P<word>(?u:\w+))(?P<number>\d*)",
         "café42", ASCII, "scanner-scoped-unicode-override"),
        ("text.comment.inline_unknown_named_unicode",
         r"(?# \N{NO SUCH PUBLIC CHARACTER})(?P<word>a)(?P<number>\d*)",
         "a12", 0, "ignored-inline-comment-named-unicode"),
        ("text.comment.global_verbose_unknown_named_unicode",
         r"# \N{NO SUCH PUBLIC CHARACTER}" + "\n"
         + r"(?P<word>a)(?P<number>\d*)",
         "a12", VERBOSE, "ignored-global-verbose-comment-named-unicode"),
        ("text.comment.scoped_verbose_unknown_named_unicode",
         r"(?x:# \N{NO SUCH PUBLIC CHARACTER}" + "\n"
         + r"(?P<word>a)(?P<number>\d*))",
         "a12", 0, "ignored-scoped-verbose-comment-named-unicode"),
        ("text.named_unicode.valid",
         r"(?P<word>\N{LATIN SMALL LETTER A})(?P<number>\d*)",
         "a12 b7", 0, "active-valid-named-unicode"),
        ("text.prefilter.dense_first_sparse_last",
         r"(?P<word>aaaaab)(?=\d)(?P<number>\d)",
         "a" * 2_048 + "b7", 0, "prefilter-dense-first-sparse-last"),
        ("text.prefilter.sparse_first_dense_last",
         r"(?P<word>bcaaaa)(?P<number>\d?)",
         "b" + "d" + "a" * 2_048, 0, "prefilter-sparse-first-dense-last"),
        ("text.buffer.changing_exporter",
         r"(?P<word>[a-z]+)(?P<number>\d+)",
         "az12 bz34", 0, "changing-pep688-subject-buffer"),
    )
    binary = (
        ("bytes.literal.short", rb"(?P<word>[A-Za-z]+)(?P<number>\d*)",
         b"alpha12 beta7 gamma003", 0, "short-mixed"),
        ("bytes.ascii.ignorecase", rb"(?P<word>[a-z]+)(?P<number>\d*)",
         b"alpha42 BETA7 Gamma003 delta", IGNORECASE, "ascii-casefold"),
        ("bytes.high.bit.words", rb"(?P<word>\w+)(?P<number>\d*)",
         b"caf\xe9 delta_9 ASCII_2 \xff tail7", 0, "high-bit-word-boundary"),
        ("bytes.null.embedded", rb"(?P<word>[A-Za-z]+)\x00(?P<number>\d+)",
         b"alpha\x0012 beta\x007 tail", 0, "embedded-nul"),
        ("bytes.hex.escapes", rb"(?P<word>[\x41-\x5a]+)(?P<number>\d*)",
         b"AB12 xy CD7 EF003", 0, "hexadecimal-character-class"),
        ("bytes.octal.escapes", rb"(?P<word>\101+)(?P<number>\d*)",
         b"AAA12 BBB7 A003", 0, "octal-escapes"),
        ("bytes.multiline.anchors", rb"^(?P<word>[a-z]+)(?P<number>\d*)$",
         b"alpha1\nBETA\ngamma22\ndelta9", MULTILINE | IGNORECASE,
         "line-anchors"),
        ("bytes.dotall.lazy", rb"(?P<word>a.+?z)(?P<number>\d*)",
         b"a first\nsecond z12 then a final z7", DOTALL, "dotall-lazy"),
        ("bytes.verbose.groups", rb"(?P<word> [a-z]+ ) \s* (?P<number> \d* )",
         b"alpha 12 BETA7 gamma 003", VERBOSE | IGNORECASE, "verbose-groups"),
        ("bytes.lookbehind.fixed", rb"(?<=ID:)(?P<word>[A-Z]+)(?P<number>\d+)",
         b"ID:AB12 none ID:XY90 ID:CD34", 0, "fixed-lookbehind"),
        ("bytes.lookahead.negative", rb"(?P<word>(?!skip)[a-z]+)(?P<number>\d*)",
         b"skip1 keep2 skit3 token4", 0, "negative-lookahead"),
        ("bytes.alternation.prefix", rb"(?P<word>ab|a|abc)(?P<number>\d*)",
         b"ab12 a7 abc99 aba3", 0, "alternation-priority"),
        ("bytes.backreference", rb"(?P<word>[a-z]+)-(?P=word)(?P<number>\d*)",
         b"echo-echo12 bad-good7 aa-aa3", 0, "named-backreference"),
        ("bytes.conditional.group", rb"(?P<word>[A-Z]+)(?P<number>\d+)?(?(number)!|\?)",
         b"AB12! CD? EF7! GH!", 0, "conditional-capture"),
        ("bytes.atomic.group", rb"(?P<word>(?>ab|a))(?P<number>\d*)",
         b"ab12 a7 aba99", 0, "atomic-group"),
        ("bytes.possessive.repeat", rb"(?P<word>a++)(?P<number>\d*)",
         b"aaaa12 aa7 bbb", 0, "possessive-repeat"),
        ("bytes.flags.scoped", rb"(?P<word>(?i:[a-z]+))(?P<number>\d*)",
         b"alpha12 BETA7 Gamma3", 0, "scoped-inline-flags"),
        ("bytes.absolute.anchors", rb"\A(?P<word>[A-Za-z]+)-(?P<number>\d+)\Z",
         b"alpha-123", 0, "absolute-full-string"),
        ("bytes.boundary.repeated", rb"\b(?P<word>[A-Za-z_]+)(?P<number>\d*)\b",
         b"prefix_42 middle7 suffix_003 " * 6, ASCII,
         "repeated-word-boundaries"),
        ("bytes.nested.repeats", rb"(?P<word>(?:ab){1,4})(?P<number>\d*)",
         b"abab12 ab7 ababab3 none", 0, "bounded-nested-repeats"),
        ("bytes.email.like", rb"(?P<word>[A-Za-z._+-]+)@(?:example|test)\.(?P<number>\d*)",
         b"alice@example.42 bob+tag@test.7 bad@other.9", 0, "email-shaped"),
        ("bytes.path.like", rb"/(?P<word>[A-Za-z_-]+)/(?P<number>\d+)",
         b"/users/42 /teams/7 /misc/003", 0, "route-shaped"),
        ("bytes.json.like", rb'"(?P<word>[A-Za-z_]+)"\s*:\s*(?P<number>\d+)',
         b'{"alpha": 12, "beta":7, "gamma": 003}', 0, "structured-log"),
        ("bytes.no.match", rb"(?P<word>QZX_NEVER_PRESENT)(?P<number>\d+)",
         b"alpha12 ordinary words gamma003", 0, "complete-miss"),
        ("bytes.long.repeated", rb"(?P<word>[A-Za-z]+)(?P<number>\d+)",
         b"noise alpha42 BETA7 " * 9, IGNORECASE, "long-repeated-haystack"),
        ("bytes.bytearray.scanner_remainder",
         rb"(?P<word>[A-Za-z]+)(?P<number>\d*)",
         bytearray(b"alpha12 beta7 !unconsumed tail9"), 0, "mutable-bytearray"),
        ("bytes.bytearray.high_bit", rb"(?P<word>[a-z]+)(?P<number>\d*)",
         bytearray(b"caf\xe9 alpha12 \xff beta7"), IGNORECASE,
         "mutable-high-bit-buffer"),
        ("bytes.memoryview.mutable.scanner_remainder",
         rb"(?P<word>[A-Za-z]+)(?P<number>\d*)",
         memoryview(bytearray(b"alpha12 beta7 !unconsumed tail9")), 0,
         "mutable-memoryview"),
        ("bytes.memoryview.readonly.scanner_remainder",
         rb"(?P<word>[A-Za-z]+)(?P<number>\d*)",
         memoryview(b"alpha12 beta7 !unconsumed tail9"), 0,
         "readonly-memoryview"),
        ("bytes.memoryview.mutable.nul", rb"(?P<word>[A-Z]+)\x00(?P<number>\d+)",
         memoryview(bytearray(b"AB\x0012 CD\x007")), 0,
         "mutable-memoryview-nul"),
        ("bytes.memoryview.readonly.high_bit",
         rb"(?P<word>[a-z]+)(?P<number>\d*)",
         memoryview(b"\xff alpha12 \xe9 beta7"), 0,
         "readonly-memoryview-high-bit"),
        ("bytes.whitespace.binary", rb"(?P<word>[A-Za-z]+)\s+(?P<number>\d+)",
         b"alpha\t12 beta\n7 gamma\v003", 0, "binary-whitespace"),
        ("bytes.scanner.scoped_i_enable", rb"(?P<word>(?i:a))(?P<number>\d*)",
         b"A7 a3", ASCII, "scanner-scoped-ignorecase-enable"),
        ("bytes.scanner.scoped_i_disable", rb"(?P<word>(?-i:a))(?P<number>\d*)",
         b"A7 a3", IGNORECASE, "scanner-scoped-ignorecase-disable"),
        ("bytes.scanner.scoped_s_enable", rb"(?P<word>(?s:a.b))(?P<number>\d*)",
         b"a\nb7 aXb3", ASCII, "scanner-scoped-dotall-enable"),
        ("bytes.scanner.scoped_s_disable", rb"(?P<word>(?-s:a.b))(?P<number>\d*)",
         b"a\nb7 aXb3", DOTALL, "scanner-scoped-dotall-disable"),
        ("bytes.scanner.scoped_m_enable", rb"(?P<word>(?m:^a$))(?P<number>\d*)",
         b"a\nx", ASCII, "scanner-scoped-multiline-enable"),
        ("bytes.scanner.scoped_m_disable", rb"(?P<word>(?-m:^a$))(?P<number>\d*)",
         b"a\nx", MULTILINE, "scanner-scoped-multiline-disable"),
        ("bytes.scanner.scoped_a_enable", rb"(?P<word>(?a:\w+))(?P<number>\d*)",
         b"caf\xe942", 0, "scanner-scoped-ascii-enable"),
        ("bytes.scanner.scoped_a_highbit", rb"(?P<word>(?a:\w+))(?P<number>\d*)",
         memoryview(b"\xff caf\xe942"), ASCII,
         "scanner-scoped-ascii-high-bit-buffer"),
        ("bytes.comment.inline_unknown_named_unicode",
         rb"(?# \N{NO SUCH PUBLIC CHARACTER})(?P<word>a)(?P<number>\d*)",
         b"a12", 0, "ignored-inline-comment-named-unicode"),
        ("bytes.comment.global_verbose_unknown_named_unicode",
         rb"# \N{NO SUCH PUBLIC CHARACTER}" + b"\n"
         + rb"(?P<word>a)(?P<number>\d*)",
         b"a12", VERBOSE, "ignored-global-verbose-comment-named-unicode"),
        ("bytes.comment.scoped_verbose_unknown_named_unicode",
         rb"(?x:# \N{NO SUCH PUBLIC CHARACTER}" + b"\n"
         + rb"(?P<word>a)(?P<number>\d*))",
         b"a12", 0, "ignored-scoped-verbose-comment-named-unicode"),
        ("bytes.comment.inline_known_named_unicode",
         rb"(?# \N{LATIN SMALL LETTER A})(?P<word>a)(?P<number>\d*)",
         b"a12", 0, "ignored-inline-comment-known-named-unicode"),
        ("bytes.prefilter.dense_first_sparse_last",
         rb"(?P<word>aaaaab)(?=\d)(?P<number>\d)",
         b"a" * 2_048 + b"b7", 0, "prefilter-dense-first-sparse-last"),
        ("bytes.prefilter.sparse_first_dense_last",
         rb"(?P<word>bcaaaa)(?P<number>\d?)",
         b"b" + b"d" + b"a" * 2_048, 0,
         "prefilter-sparse-first-dense-last"),
        ("bytes.buffer.changing_exporter",
         rb"(?P<word>[a-z]+)(?P<number>\d+)",
         b"az12 bz34", 0, "changing-pep688-subject-buffer"),
    )
    return text, binary


def classify_lifecycle(operation: str) -> str:
    if operation.startswith("module.cache."):
        return "module-compile-cache"
    if operation.startswith("module.compile"):
        return "module-compile"
    if operation.startswith("module."):
        return "module-call"
    if operation.startswith("pattern.scanner."):
        return "compiled-pattern-scanner"
    if operation.startswith("pattern."):
        return "reused-precompiled-pattern"
    if operation.startswith("match."):
        return "live-match-object"
    if operation.startswith("scanner."):
        return "public-scanner-callback"
    if operation.startswith("lifecycle.compile_fresh"):
        return "fresh-cache-miss-compile-and-match"
    if operation.startswith("lifecycle.cache_"):
        return "explicit-hot-or-churned-compile-cache"
    return "repeated-operation-lifecycle"


def build_public_matrix() -> list[dict[str, Any]]:
    text, binary = public_datasets()
    seeded = random.Random(PUBLISHED_SEED)
    datasets: list[tuple[str, str, dict[str, Any], dict[str, Any], int, str]] = []
    for name, expression, subject, flags, workload in text:
        datasets.append((name, "text", typed_text(expression),
                         encode_subject(subject), flags, workload))
    for name, expression, subject, flags, workload in binary:
        datasets.append((name, "bytes", typed_bytes(expression),
                         encode_subject(subject), flags, workload))

    cases: list[dict[str, Any]] = []
    for dataset, domain, expression, subject, flags, workload in datasets:
        materialized_subject = materialize_typed(subject)
        subject_length = len(materialized_subject)
        replacement = (
            typed_text(r"<\g<word>>") if domain == "text"
            else typed_bytes(rb"<\g<word>>")
        )
        for operation in OPERATIONS:
            start = min(seeded.randrange(0, 4), subject_length)
            end = max(start, subject_length - seeded.randrange(0, 3))
            cases.append({
                "case": "rust-public-practice.v2." + format(len(cases), "05d"),
                "dataset": dataset, "workload": workload, "domain": domain,
                "operation": operation,
                "lifecycle": classify_lifecycle(operation),
                "pattern": expression, "subject": subject,
                "replacement": replacement, "flags": flags,
                "limit": seeded.randrange(1, 5), "pos": start,
                "endpos": end, "repetitions": seeded.randrange(2, 5),
                "subject_length": subject_length, "weight_numerator": 1,
            })
    return cases


def validate_public_matrix(cases: Any) -> str:
    text, binary = public_datasets()
    expected_count = (len(text) + len(binary)) * len(OPERATIONS)
    require(type(cases) is list and len(cases) == expected_count
            and cases == build_public_matrix()
            and len({case["case"] for case in cases}) == expected_count
            and digest(cases) == MATRIX_SHA256,
            "the exact frozen public seed, operation, case, or weight was changed")
    require(len(text) == len(binary)
            and sum(case["domain"] == "text" for case in cases)
            == sum(case["domain"] == "bytes" for case in cases)
            == len(text) * len(OPERATIONS),
            "text and bytes must preserve exactly equal public case weights")
    for operation in OPERATIONS:
        require(sum(case["operation"] == operation for case in cases)
                == len(text) + len(binary),
                "a complete frozen public API operation was omitted: " + operation)
    for case in cases:
        require(case["lifecycle"] == classify_lifecycle(case["operation"])
                and case["weight_numerator"] == 1
                and case["subject_length"] == len(materialize_typed(case["subject"]))
                and 0 <= case["pos"] <= case["endpos"] <= case["subject_length"],
                "a public lifecycle, buffer, bounds, or equal weight was changed")
    return MATRIX_SHA256


def verify_pinned_runtime(*, permit_candidate: bool = False) -> None:
    expected_root = str(ROOT)
    expected_source = str(ROOT / SOURCE_RELATIVE)
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and bool(sys.path) and sys.path[0] == expected_root
            and os.path.realpath(expected_root) == expected_root
            and os.path.abspath(sys.executable) == str(PINNED_PYTHON)
            and os.path.realpath(sys.executable) == str(PINNED_PYTHON)
            and os.path.abspath(__file__) == expected_source
            and os.path.realpath(__file__) == expected_source,
            "use only the frozen real source/root and isolated pinned CPython 3.14.6")
    if not permit_candidate:
        require(not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
                "a candidate escaped into a source-only or standard-library process")


def owned_origin(module: Any, *, description: str) -> str:
    origin = getattr(module, "__file__", None)
    require(type(origin) is str and os.path.isabs(origin)
            and os.path.abspath(origin) == origin
            and os.path.realpath(origin) == origin
            and os.path.commonpath((str(ROOT), origin)) == str(ROOT),
            "an exact owned " + description + " module origin was substituted")
    return origin


def authenticate_rust_candidate(engine: Any) -> None:
    expected_adapter = str(ROOT / "candidates" / "rust_candidate.py")
    require(engine.__name__ == "candidates.rust_candidate"
            and owned_origin(engine, description="Rust adapter") == expected_adapter,
            "the named owned from-scratch Rust adapter was substituted")
    bridge = sys.modules.get("candidates._rust_bridge")
    require(isinstance(bridge, types.ModuleType)
            and bridge.__name__ == "candidates._rust_bridge",
            "the genuine owned compiled Rust extension was omitted")
    origin = owned_origin(bridge, description="compiled Rust extension")
    candidate_root = str(ROOT / "candidates")
    require(os.path.commonpath((candidate_root, origin)) == candidate_root
            and any(origin.endswith(suffix) for suffix in EXTENSION_SUFFIXES),
            "the Rust bridge is not an owned real CPython extension")
    specification = getattr(bridge, "__spec__", None)
    loader = getattr(specification, "loader", None)
    require(specification is not None
            and getattr(specification, "name", None) == "candidates._rust_bridge"
            and getattr(specification, "origin", None) == origin
            and isinstance(loader, ExtensionFileLoader)
            and getattr(loader, "name", None) == "candidates._rust_bridge"
            and getattr(loader, "path", None) == origin,
            "the authentic owned native-extension loader or identity was forged")
    package = sys.modules.get("candidates")
    if package is not None and getattr(package, "__file__", None) is not None:
        require(owned_origin(package, description="Rust candidate package")
                == str(ROOT / "candidates" / "__init__.py"),
                "the owned candidate package was substituted")
    for name in (
        "compile", "search", "match", "fullmatch", "findall", "finditer",
        "split", "sub", "subn", "escape", "purge", "Scanner",
    ):
        function = getattr(engine, name, None)
        if function is None:
            continue
        module_name = getattr(function, "__module__", None)
        require(module_name not in ("re", "_sre", "sre_compile"),
                "a Rust public operation directly aliases CPython: " + name)
        if type(module_name) is str and module_name.startswith("candidates."):
            module = sys.modules.get(module_name)
            if module is not None:
                owned_origin(module, description="Rust operation " + name)


def audit_candidate_runtime(
    engine: Any, harness_regex: Mapping[str, Any], *, phase: str,
) -> None:
    """Keep incidental harness ``re`` distinct from candidate-owned imports."""
    reject_external_regex_packages()
    actual_regex = stdlib_regex_modules()
    newly_imported = sorted(set(actual_regex) - set(harness_regex))
    replaced = sorted(
        name for name, module in harness_regex.items()
        if actual_regex.get(name) is not module
    )
    require(not newly_imported and not replaced,
            "candidate-owned matching imported or replaced stdlib re/_sre at "
            + phase + ": " + ", ".join(newly_imported + replaced))
    owned_root = str(ROOT / "candidates")
    for name, module in tuple(sys.modules.items()):
        if name == "candidates" or name.startswith("candidates."):
            require(isinstance(module, types.ModuleType),
                    "a candidate runtime module identity was forged: " + name)
            origin = owned_origin(module, description="first-party runtime " + name)
            require(os.path.commonpath((owned_root, origin)) == owned_root,
                    "a first-party candidate runtime escaped the owned module root")
    for name, value in vars(engine).items():
        if isinstance(value, types.ModuleType):
            module_name = value.__name__
            require(module_name not in ("re", "_sre")
                    and not module_name.startswith(("re.", "_sre."))
                    and module_name.partition(".")[0]
                    not in FORBIDDEN_REGEX_PACKAGE_ROOTS,
                    "a candidate-owned runtime directly retained a matching module: "
                    + name)
            if module_name.startswith("candidates."):
                origin = owned_origin(
                    value, description="first-party adapter runtime " + module_name,
                )
                require(os.path.commonpath((owned_root, origin)) == owned_root,
                        "a candidate-owned adapter module is not first-party")


def normalize_pattern(pattern: Any) -> dict[str, Any]:
    groups = getattr(pattern, "groups")
    flags = getattr(pattern, "flags")
    require(type(groups) is int and groups >= 0 and type(flags) is int,
            "a genuine compiled pattern concealed exact groups or flags")
    groupindex = dict(getattr(pattern, "groupindex"))
    return {
        "kind": "compiled-pattern", "pattern": normalize_value(pattern.pattern),
        "flags": flags, "groups": groups,
        "groupindex": [[key, value] for key, value in sorted(groupindex.items())],
    }


def normalize_match(match: Any) -> dict[str, Any]:
    expression = match.re
    groups = expression.groups
    require(type(groups) is int and groups >= 0,
            "a live public match concealed its exact capture-group denominator")
    return {
        "kind": "match", "pattern": normalize_pattern(expression),
        "string": normalize_value(match.string),
        "group": normalize_value(match.group(0)),
        "span": list(match.span(0)),
        "groups": [normalize_value(item) for item in match.groups()],
        "spans": [list(match.span(index)) for index in range(groups + 1)],
        "groupdict": [[name, normalize_value(item)]
                      for name, item in sorted(match.groupdict().items())],
        "lastindex": match.lastindex, "lastgroup": match.lastgroup,
        "pos": match.pos, "endpos": match.endpos,
    }


def normalize_value(value: Any) -> Any:
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is bytes:
        return {"kind": "bytes", "hex": value.hex()}
    if type(value) is bytearray:
        return {"kind": "bytearray", "hex": bytes(value).hex()}
    if type(value) is memoryview:
        return {
            "kind": "memoryview", "hex": value.tobytes().hex(),
            "readonly": value.readonly, "format": value.format,
            "itemsize": value.itemsize, "ndim": value.ndim,
            "shape": list(value.shape) if value.shape is not None else None,
            "strides": list(value.strides) if value.strides is not None else None,
            "contiguous": value.contiguous,
        }
    if type(value) in (list, tuple):
        return {"kind": "list" if type(value) is list else "tuple",
                "items": [normalize_value(item) for item in value]}
    if isinstance(value, Mapping):
        return {"kind": "mapping", "items": [
            [normalize_value(key), normalize_value(item)]
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        ]}
    if hasattr(value, "group") and hasattr(value, "span") and hasattr(value, "re"):
        return normalize_match(value)
    if hasattr(value, "pattern") and hasattr(value, "groups") \
            and hasattr(value, "groupindex") and hasattr(value, "flags"):
        return normalize_pattern(value)
    raise PublicPracticeError(
        "an unsupported public API observable escaped normalization: "
        + type(value).__qualname__,
    )


def normalize_exception(error: Exception, engine: Any = None) -> dict[str, Any]:
    public_error = getattr(engine, "error", None) if engine is not None else None
    if isinstance(public_error, type) and isinstance(error, public_error):
        return {
            "kind": "public-regex-pattern-error", "type": type(error).__qualname__,
            "is_engine_error": True, "args": normalize_value(error.args),
            "message": getattr(error, "msg", None),
            "pattern": normalize_value(getattr(error, "pattern", None)),
            "position": getattr(error, "pos", None),
            "line": getattr(error, "lineno", None),
            "column": getattr(error, "colno", None),
        }
    return {
        "kind": "ordinary-python-exception", "module": type(error).__module__,
        "type": type(error).__qualname__, "args": normalize_value(error.args),
    }


def normalize_warnings(records: Any) -> list[dict[str, Any]]:
    require(type(records) is list,
            "every genuine recorded public warning must be preserved")
    actual: list[dict[str, Any]] = []
    for item in records:
        require(isinstance(item.category, type)
                and isinstance(item.message, Warning)
                and isinstance(item.message, item.category),
                "a genuine public warning category or message was substituted")
        actual.append({
            "category_module": item.category.__module__,
            "category": item.category.__qualname__,
            "message": str(item.message),
        })
    return actual


def project_fresh_match(match: Any) -> Any:
    if match is None:
        return None
    return {
        "group": match.group(0), "span": tuple(match.span(0)),
        "groups": tuple(match.groups()), "groupdict": dict(match.groupdict()),
    }


def prepare_case(engine: Any, case: Mapping[str, Any]) -> Callable[[], dict[str, Any]]:
    expression = materialize_typed(case["pattern"])
    subject = materialize_typed(case["subject"])
    replacement = materialize_typed(case["replacement"])
    operation = case["operation"]
    flags, limit = case["flags"], case["limit"]
    start, end = case["pos"], case["endpos"]
    repetitions = case["repetitions"]
    require(operation in OPERATIONS and type(flags) is int
            and type(limit) is int and 1 <= limit <= 4
            and type(start) is int and type(end) is int
            and 0 <= start <= end <= len(subject)
            and type(repetitions) is int and 2 <= repetitions <= 4
            and ((type(expression) is str and type(subject) is str
                  and type(replacement) is str)
                 or (type(expression) is bytes
                     and type(subject) in (bytes, bytearray, memoryview)
                     and type(replacement) is bytes)),
            "a frozen original public operation, matching domain, or bounds changed")
    compiled: Any = None
    if operation.startswith(("pattern.", "match.")) \
            or operation in ("lifecycle.precompiled.reuse",
                             "lifecycle.scanner_recreate.search"):
        compiled = engine.compile(expression, flags)
    serial = 0

    def without_warnings() -> dict[str, Any]:
        nonlocal serial
        callbacks: list[dict[str, Any]] = []
        buffer_events: list[str] = []

        class PublicBufferExporter:
            """A first-party PEP 688 probe with exact acquire/release evidence."""

            def __init__(self, name: str, backing: bytes) -> None:
                self.name = name
                self.backing = backing

            def __buffer__(self, flags: int) -> memoryview:
                buffer_events.append(self.name + "+")
                return memoryview(self.backing)

            def __release_buffer__(self, view: memoryview) -> None:
                buffer_events.append(self.name + "-")

        class ChangingPublicBufferExporter:
            """First acquisition is original bytes; later acquisitions are ``X``."""

            def __init__(self, backing: bytes) -> None:
                self.backing = backing
                self.acquisitions = 0

            def __buffer__(self, flags: int) -> memoryview:
                buffer_events.append("S+")
                self.acquisitions += 1
                return memoryview(
                    self.backing if self.acquisitions == 1 else b"X",
                )

            def __release_buffer__(self, view: memoryview) -> None:
                buffer_events.append("S-")

        class ForbiddenSubjectExporter:
            """Expose invalid-template precedence without opening the subject."""

            def __buffer__(self, flags: int) -> memoryview:
                buffer_events.append("BAD+")
                raise RuntimeError("public invalid-template subject must remain unopened")

            def __release_buffer__(self, view: memoryview) -> None:
                buffer_events.append("BAD-")

        def buffer_exporters() -> tuple[PublicBufferExporter, PublicBufferExporter]:
            replacement_bytes = (
                replacement.encode("utf-8") if type(replacement) is str
                else replacement
            )
            subject_bytes = (
                subject.encode("utf-8") if type(subject) is str
                else bytes(subject)
            )
            return (PublicBufferExporter("R", replacement_bytes),
                    PublicBufferExporter("S", subject_bytes))

        def callback(match: Any) -> str | bytes:
            callbacks.append(normalize_match(match))
            token = match.group(0)
            if type(token) is bytes:
                return b"<" + token.upper() + b">"
            require(type(token) is str,
                    "a real public replacement callback changed matching domains")
            return "<" + token.upper() + ">"

        def failing_callback(match: Any) -> str | bytes:
            callbacks.append(normalize_match(match))
            raise ValueError("independent public practice replacement callback failure")

        def scanner_callback(scanner: Any, token: Any) -> str | bytes:
            actual_match = scanner.match
            combined = scanner.scanner
            callbacks.append({
                "kind": "scanner-token", "token": normalize_value(token),
                "match": normalize_match(actual_match),
                "combined_pattern": normalize_pattern(combined),
                "match_uses_combined_pattern": actual_match.re is combined,
            })
            if type(token) is bytes:
                return b"<" + token.upper() + b">"
            require(type(token) is str,
                    "a real Scanner callback changed its exact public token type")
            return "<" + token.upper() + ">"

        def failing_scanner_callback(scanner: Any, token: Any) -> str | bytes:
            actual_match = scanner.match
            combined = scanner.scanner
            callbacks.append({
                "kind": "scanner-token", "token": normalize_value(token),
                "match": normalize_match(actual_match),
                "combined_pattern": normalize_pattern(combined),
                "match_uses_combined_pattern": actual_match.re is combined,
            })
            raise ValueError("independent public practice scanner callback failure")

        def fresh_pattern() -> str | bytes:
            nonlocal serial
            comment = "(?#independent-public-v2-" + str(serial) + ")"
            serial += 1
            return expression + (
                comment if type(expression) is str else comment.encode("ascii")
            )

        try:
            if operation == "module.compile":
                result = engine.compile(expression, flags)
            elif operation == "module.compile.flags_keyword":
                result = engine.compile(expression, flags=flags)
            elif operation in ("module.compile.identity",
                               "module.cache.repeated_identity"):
                first = engine.compile(expression, flags)
                second = engine.compile(expression, flags)
                result = {"same_object": first is second, "pattern": second}
            elif operation == "module.cache.purge_compile":
                purged = engine.purge()
                result = {"purge_return": purged,
                          "pattern": engine.compile(expression, flags)}
            elif operation == "module.cache.alternating_compile":
                alternate = expression + (
                    "(?#public-v2-cache-alternate)" if type(expression) is str
                    else b"(?#public-v2-cache-alternate)"
                )
                primary = engine.compile(expression, flags)
                other = engine.compile(alternate, flags)
                repeated = engine.compile(expression, flags)
                result = {"primary_retained": primary is repeated,
                          "distinct_alternate": primary is not other,
                          "pattern": repeated}
            elif operation in (
                "module.search", "module.match", "module.fullmatch",
                "module.findall", "module.finditer",
            ):
                name = operation.split(".", 1)[1]
                result = getattr(engine, name)(expression, subject, flags)
                if name == "finditer":
                    result = list(result)
            elif operation == "module.search.flags_keyword":
                result = engine.search(expression, subject, flags=flags)
            elif operation == "module.split":
                result = engine.split(expression, subject, maxsplit=limit, flags=flags)
            elif operation == "module.split.positional":
                result = engine.split(expression, subject, limit, flags)
            elif operation == "module.split.unlimited":
                result = engine.split(expression, subject, maxsplit=0, flags=flags)
            elif operation == "module.sub.buffer_exporter":
                exported_replacement, exported_subject = buffer_exporters()
                observed = engine.sub(
                    expression, exported_replacement, exported_subject,
                    count=limit, flags=flags,
                )
                result = {"result": observed, "buffer_events": tuple(buffer_events)}
            elif operation == "module.sub.buffer_changing_subject":
                backing = (
                    subject.encode("utf-8") if type(subject) is str else bytes(subject)
                )
                changing = ChangingPublicBufferExporter(backing)
                template = r"\g<word>" if type(expression) is str else rb"\g<word>"
                observed = engine.sub(
                    expression, template, changing, count=0, flags=flags,
                )
                result = {
                    "result": observed, "buffer_events": tuple(buffer_events),
                    "subject_acquisitions": changing.acquisitions,
                }
            elif operation == "module.sub.invalid_replacement_precedence":
                invalid = "\\" if type(expression) is str else b"\\"
                result = engine.sub(
                    expression, invalid, ForbiddenSubjectExporter(),
                    count=limit, flags=flags,
                )
            elif operation in (
                "module.sub.literal", "module.sub.positional", "module.sub.unlimited",
                "module.sub.template_named", "module.sub.callback",
                "module.sub.callback_error", "module.subn.literal",
                "module.subn.positional", "module.subn.template_named",
                "module.subn.callback", "module.subn.callback_error",
            ):
                name = "subn" if operation.startswith("module.subn.") else "sub"
                actual_replacement: Any
                if operation.endswith("callback_error"):
                    actual_replacement = failing_callback
                elif operation.endswith("callback"):
                    actual_replacement = callback
                else:
                    actual_replacement = replacement
                if operation.endswith("positional"):
                    result = getattr(engine, name)(
                        expression, actual_replacement, subject, limit, flags,
                    )
                else:
                    count = 0 if operation.endswith("unlimited") else limit
                    result = getattr(engine, name)(
                        expression, actual_replacement, subject,
                        count=count, flags=flags,
                    )
            elif operation == "module.escape.pattern":
                result = engine.escape(expression)
            elif operation == "module.escape.subject":
                result = engine.escape(subject)
            elif operation == "module.flags.constants":
                result = {
                    name: int(getattr(engine, name))
                    for name in (
                        "ASCII", "DOTALL", "IGNORECASE", "MULTILINE",
                        "NOFLAG", "VERBOSE",
                    )
                }
            elif operation in (
                "pattern.search", "pattern.match", "pattern.fullmatch",
                "pattern.findall", "pattern.finditer",
            ):
                name = operation.split(".", 1)[1]
                result = getattr(compiled, name)(subject)
                if name == "finditer":
                    result = list(result)
            elif operation in (
                "pattern.search.pos_endpos", "pattern.match.pos_endpos",
                "pattern.fullmatch.pos_endpos", "pattern.findall.pos_endpos",
                "pattern.finditer.pos_endpos",
            ):
                name = operation.split(".")[1]
                result = getattr(compiled, name)(subject, start, end)
                if name == "finditer":
                    result = list(result)
            elif operation == "pattern.search.negative_bounds":
                result = compiled.search(subject, -len(subject) - 5,
                                         len(subject) + 5)
            elif operation in ("pattern.split", "pattern.split.unlimited"):
                result = compiled.split(
                    subject, maxsplit=0 if operation.endswith("unlimited") else limit,
                )
            elif operation == "pattern.sub.buffer_exporter":
                exported_replacement, exported_subject = buffer_exporters()
                observed = compiled.sub(
                    exported_replacement, exported_subject, count=limit,
                )
                result = {"result": observed, "buffer_events": tuple(buffer_events)}
            elif operation == "pattern.sub.buffer_changing_subject":
                backing = (
                    subject.encode("utf-8") if type(subject) is str else bytes(subject)
                )
                changing = ChangingPublicBufferExporter(backing)
                template = r"\g<word>" if type(expression) is str else rb"\g<word>"
                observed = compiled.sub(template, changing, count=0)
                result = {
                    "result": observed, "buffer_events": tuple(buffer_events),
                    "subject_acquisitions": changing.acquisitions,
                }
            elif operation == "pattern.sub.invalid_replacement_precedence":
                invalid = "\\" if type(expression) is str else b"\\"
                result = compiled.sub(invalid, ForbiddenSubjectExporter(), count=limit)
            elif operation in (
                "pattern.sub.literal", "pattern.sub.template_named",
                "pattern.sub.template_numeric", "pattern.sub.callback",
                "pattern.sub.callback_error", "pattern.subn.literal",
                "pattern.subn.template_named", "pattern.subn.callback",
                "pattern.subn.callback_error",
            ):
                name = "subn" if operation.startswith("pattern.subn.") else "sub"
                if operation.endswith("callback_error"):
                    actual_replacement = failing_callback
                elif operation.endswith("callback"):
                    actual_replacement = callback
                elif operation.endswith("template_numeric"):
                    actual_replacement = (
                        r"[\1]" if type(expression) is str else rb"[\1]"
                    )
                else:
                    actual_replacement = replacement
                result = getattr(compiled, name)(
                    actual_replacement, subject, count=limit,
                )
            elif operation in ("pattern.scanner.search", "pattern.scanner.match"):
                scanner = compiled.scanner(subject)
                result = getattr(scanner, operation.rsplit(".", 1)[1])()
            elif operation in ("pattern.scanner.loop", "pattern.scanner.bounded"):
                scanner = (
                    compiled.scanner(subject, start, end)
                    if operation.endswith("bounded") else compiled.scanner(subject)
                )
                result = []
                while True:
                    matched = scanner.search()
                    if matched is None:
                        break
                    result.append(matched)
                    require(len(result) <= 1_024,
                            "an authentic public pattern scanner failed to progress")
            elif operation.startswith("pattern.scanner.reduce_ex."):
                scanner = compiled.scanner(subject)
                protocol = {
                    "negative": -1, "zero": 0, "one": 1, "two": 2,
                    "five": 5, "string": "0", "overflow": 2 ** 40,
                }[operation.rsplit(".", 1)[1]]
                reduction = scanner.__reduce_ex__(protocol)
                require(type(reduction) is tuple and len(reduction) == 2
                        and callable(reduction[0])
                        and type(reduction[1]) is tuple,
                        "an authentic scanner reduction did not retain its exact tuple")
                arguments = reduction[1]
                result = {
                    "protocol": protocol,
                    "reconstructor_module": getattr(reduction[0], "__module__", None),
                    "reconstructor_qualname": getattr(
                        reduction[0], "__qualname__", None,
                    ),
                    "argument_count": len(arguments),
                    "argument_zero_is_actual_scanner_type": (
                        len(arguments) > 0 and arguments[0] is type(scanner)
                    ),
                    "argument_one_is_object": (
                        len(arguments) > 1 and arguments[1] is object
                    ),
                    "argument_two_is_none": (
                        len(arguments) > 2 and arguments[2] is None
                    ),
                }
            elif operation == "pattern.properties":
                result = {
                    "pattern": compiled.pattern, "flags": compiled.flags,
                    "groups": compiled.groups,
                    "groupindex": dict(compiled.groupindex),
                }
            elif operation == "pattern.groupindex":
                result = dict(compiled.groupindex)
            elif operation == "pattern.flags":
                result = {"flags": compiled.flags, "groups": compiled.groups}
            elif operation == "pattern.copy":
                copied = copy.copy(compiled)
                result = {"pattern": copied, "same_object": copied is compiled}
            elif operation == "pattern.deepcopy":
                copied = copy.deepcopy(compiled)
                result = {"pattern": copied, "same_object": copied is compiled}
            elif operation.startswith("pattern.method_signature."):
                method_name = operation.rsplit(".", 1)[1]
                method = getattr(compiled, method_name)
                result = {
                    "method": method_name,
                    "bound_to_pattern": getattr(method, "__self__", None) is compiled,
                    "signature": str(inspect.signature(method)),
                    "text_signature": getattr(method, "__text_signature__", None),
                    "qualname": getattr(method, "__qualname__", None),
                    "callable_kind": type(method).__name__,
                }
            elif operation.startswith("match."):
                matched = compiled.search(subject)
                if matched is None:
                    result = None
                elif operation == "match.group.default":
                    result = matched.group()
                elif operation == "match.group.zero":
                    result = matched.group(0)
                elif operation == "match.group.named":
                    result = matched.group("word")
                elif operation == "match.group.multiple":
                    result = matched.group(0, "word", "number")
                elif operation == "match.group.index_error":
                    result = matched.group(99_999)
                elif operation == "match.groups.default":
                    missing = "MISSING" if type(expression) is str else b"MISSING"
                    result = matched.groups(missing)
                elif operation == "match.groupdict.default":
                    missing = "MISSING" if type(expression) is str else b"MISSING"
                    result = matched.groupdict(missing)
                elif operation == "match.start_end_span":
                    result = {
                        "start": matched.start(), "end": matched.end(),
                        "span": matched.span(),
                    }
                elif operation == "match.span.named":
                    result = matched.span("word")
                elif operation == "match.expand.named":
                    result = matched.expand(replacement)
                elif operation == "match.expand.numeric":
                    template = r"[\1]" if type(expression) is str else rb"[\1]"
                    result = matched.expand(template)
                elif operation == "match.getitem.zero":
                    result = matched[0]
                elif operation == "match.getitem.named":
                    result = matched["word"]
                elif operation == "match.getitem.index_error":
                    result = matched[99_999]
                elif operation == "match.properties":
                    result = {
                        "re": matched.re, "string": matched.string,
                        "pos": matched.pos, "endpos": matched.endpos,
                        "lastindex": matched.lastindex,
                        "lastgroup": matched.lastgroup,
                    }
                elif operation == "match.regs":
                    result = matched.regs
                else:
                    raise PublicPracticeError("an unfrozen live match API was injected")
            elif operation.startswith("scanner.scan"):
                whitespace = r"\s+" if type(expression) is str else rb"\s+"
                wildcard = r"(?s:.)" if type(expression) is str else rb"(?s:.)"
                action: Any = (
                    failing_scanner_callback if operation.endswith("callback_error")
                    else None if operation.endswith("no_action")
                    else scanner_callback
                )
                lexicon: list[tuple[Any, Any]] = [
                    (expression, action), (whitespace, None),
                ]
                if operation.endswith(("skipping", "empty_remainder")):
                    lexicon.append((wildcard, None))
                scanner = engine.Scanner(lexicon, flags=flags)
                result = scanner.scan(subject)
            elif operation in (
                "lifecycle.compile_fresh.search", "lifecycle.compile_fresh.fullmatch",
            ):
                fresh = engine.compile(fresh_pattern(), flags)
                method = "fullmatch" if operation.endswith("fullmatch") else "search"
                result = project_fresh_match(getattr(fresh, method)(subject))
            elif operation == "lifecycle.cache_hot.search":
                engine.compile(expression, flags)
                result = project_fresh_match(engine.search(expression, subject, flags))
            elif operation == "lifecycle.cache_hot.compile":
                engine.compile(expression, flags)
                result = normalize_pattern(engine.compile(expression, flags))
            elif operation == "lifecycle.cache_churn.search":
                for _ in range(repetitions):
                    engine.compile(fresh_pattern(), flags)
                result = project_fresh_match(engine.search(expression, subject, flags))
            elif operation == "lifecycle.precompiled.reuse":
                observed = None
                for _ in range(repetitions):
                    observed = compiled.search(subject)
                result = project_fresh_match(observed)
            elif operation == "lifecycle.scanner_recreate.search":
                observed = None
                for _ in range(repetitions):
                    observed = compiled.scanner(subject).search()
                result = project_fresh_match(observed)
            elif operation == "lifecycle.module_repeated.search":
                observed = None
                for _ in range(repetitions):
                    observed = engine.search(expression, subject, flags)
                result = project_fresh_match(observed)
            else:
                raise PublicPracticeError("an unfrozen public operation was injected")
            return {
                "status": "return", "value": normalize_value(result),
                "callbacks": callbacks, "buffer_events": buffer_events,
            }
        except PublicPracticeError:
            raise
        except Exception as error:
            return {
                "status": "raise", "exception": normalize_exception(error, engine),
                "callbacks": callbacks, "buffer_events": buffer_events,
            }

    def perform() -> dict[str, Any]:
        with warnings.catch_warnings(record=True) as observed:
            warnings.simplefilter("always")
            result = without_warnings()
            result["warnings"] = normalize_warnings(observed)
            return result

    return perform


def load_engine(name: str, harness_regex: Mapping[str, Any]) -> Any:
    require(name in ("stdlib", "rust"),
            "only pinned isolated CPython or the named Rust candidate is allowed")
    verify_pinned_runtime()
    reject_external_regex_packages()
    if name == "stdlib":
        engine = importlib.import_module("re")
        require(engine.__name__ == "re" and type(engine.__file__) is str
                and os.path.abspath(engine.__file__) == str(PINNED_STDLIB_RE)
                and os.path.realpath(engine.__file__) == str(PINNED_STDLIB_RE),
                "the exact real pinned CPython standard-library oracle changed")
        require(not any(item == "candidates" or item.startswith("candidates.")
                        for item in sys.modules),
                "the isolated standard-library oracle imported a candidate")
        return engine
    engine = importlib.import_module("candidates.rust_candidate")
    authenticate_rust_candidate(engine)
    audit_candidate_runtime(engine, harness_regex, phase="candidate import")
    return engine


def observe_worker(role: str, engine_name: str) -> dict[str, Any]:
    matrix = build_public_matrix()
    validate_public_matrix(matrix)
    harness_regex = stdlib_regex_modules()
    engine = load_engine(engine_name, harness_regex)
    records: list[dict[str, Any]] = []
    for case in matrix:
        try:
            outcome = prepare_case(engine, case)()
        except PublicPracticeError:
            raise
        except Exception as error:
            outcome = {
                "status": "raise", "exception": normalize_exception(error, engine),
                "callbacks": [], "buffer_events": [], "warnings": [],
            }
        records.append({"case": case["case"], "outcome": outcome})
    require(len(records) == len(matrix),
            "a complete public standard-library/Rust observation was removed")
    if engine_name == "rust":
        audit_candidate_runtime(engine, harness_regex, phase="candidate matching")
    else:
        reject_external_regex_packages()
    return {
        "schema": SCHEMA + "-isolated-observations", "status": "PASS",
        "label": PRACTICE_LABEL, "role": role, "engine": engine_name,
        "pid": os.getpid(), "python": "3.14.6", "published_seed": PUBLISHED_SEED,
        "matrix_sha256": MATRIX_SHA256, "case_count": len(matrix),
        "records_sha256": digest(records), "records": records,
        "candidate_import_count": sum(
            item == "candidates" or item.startswith("candidates.")
            for item in sys.modules
        ),
        "harness_preexisting_stdlib_regex_modules": sorted(harness_regex),
        "candidate_new_stdlib_regex_module_count": (
            len(set(stdlib_regex_modules()) - set(harness_regex))
            if engine_name == "rust" else None
        ),
        "candidate_runtime_provenance_checked": engine_name == "rust",
        "oracle_is_stdlib_only": engine_name == "stdlib",
        "external_regex_package_count": 0,
        "benchmark_files_read": 0, "fixture_files_read": 0,
        "sealed_cases_read": 0, "hidden_cases_read": 0,
        "archive_files_read": 0, "files_written": 0,
    }


def validate_expected_records(
    records: Any, matrix: list[dict[str, Any]], expected_hash: Any,
) -> dict[str, dict[str, Any]]:
    require(type(records) is list and len(records) == len(matrix)
            and type(expected_hash) is str and digest(records) == expected_hash,
            "the full source-ordered standard-library outcome vector changed")
    by_case: dict[str, dict[str, Any]] = {}
    for case, record in zip(matrix, records, strict=True):
        require(type(record) is dict and set(record) == {"case", "outcome"}
                and record.get("case") == case["case"]
                and type(record.get("outcome")) is dict
                and record["outcome"].get("status") in ("return", "raise")
                and type(record["outcome"].get("callbacks")) is list
                and type(record["outcome"].get("buffer_events")) is list
                and type(record["outcome"].get("warnings")) is list,
                "a complete source-ordered public oracle outcome was omitted")
        by_case[case["case"]] = record["outcome"]
    return by_case


def timing_worker(role: str, engine_name: str) -> dict[str, Any]:
    matrix = build_public_matrix()
    validate_public_matrix(matrix)
    request = decode_canonical(
        sys.stdin.buffer.read(MAX_PROCESS_BYTES + 1),
        role + " complete public timing request",
    )
    for key, expected in (
        ("schema", SCHEMA + "-timing-request"),
        ("published_seed", PUBLISHED_SEED),
        ("matrix_sha256", MATRIX_SHA256),
    ):
        require(request.get(key) == expected,
                "a frozen source-only public timing protocol changed: " + key)
    trial, iterations, warmups = (
        request.get("trial"), request.get("iterations"), request.get("warmups")
    )
    require(type(trial) is int and 0 <= trial < 1_000
            and type(iterations) is int and 1 <= iterations <= 1_000
            and type(warmups) is int and 0 <= warmups <= 100,
            "an actual paired public trial, iteration, or warmup was substituted")
    expected = validate_expected_records(
        request.get("expected_records"), matrix, request.get("expected_sha256"),
    )
    case_by_id = {case["case"]: case for case in matrix}
    order = request.get("case_order")
    require(type(order) is list and len(order) == len(matrix)
            and all(type(case_id) is str for case_id in order)
            and len(set(order)) == len(matrix)
            and set(order) == set(case_by_id),
            "a paired public timing case was omitted, duplicated, or substituted")
    harness_regex = stdlib_regex_modules()
    engine = load_engine(engine_name, harness_regex)
    rows: list[dict[str, Any]] = []
    for position, case_id in enumerate(order):
        try:
            executor = prepare_case(engine, case_by_id[case_id])
            outcome = expected[case_id]
            for _ in range(warmups):
                require(executor() == outcome,
                        "a public warmup failed exact correctness: " + case_id)
            before = __import__("time").perf_counter_ns()
            for _ in range(iterations):
                require(executor() == outcome,
                        "a public timed operation failed exact correctness: " + case_id)
            after = __import__("time").perf_counter_ns()
            require(executor() == outcome,
                    "a public post-timing operation failed correctness: " + case_id)
        except Exception as error:
            raise PublicPracticeError(
                "an exact correctness-gated public timing failed at " + case_id
                + ": " + type(error).__qualname__ + ": " + str(error),
            ) from error
        elapsed = after - before
        require(type(elapsed) is int and elapsed > 0,
                "a genuine bounded monotonic public timing interval was not observed")
        rows.append({
            "case": case_id, "trial": trial, "position": position,
            "elapsed_ns": elapsed, "batch_iterations": iterations,
            "correctness_checks": warmups + iterations + 1,
            "expected_outcome_sha256": digest(outcome),
        })
    if engine_name == "rust":
        audit_candidate_runtime(engine, harness_regex, phase="timed candidate matching")
    else:
        reject_external_regex_packages()
    return {
        "schema": SCHEMA + "-isolated-timing", "status": "PASS",
        "label": PRACTICE_LABEL, "role": role, "engine": engine_name,
        "pid": os.getpid(), "python": "3.14.6", "trial": trial,
        "published_seed": PUBLISHED_SEED, "matrix_sha256": MATRIX_SHA256,
        "expected_sha256": request["expected_sha256"],
        "case_count": len(matrix), "rows_sha256": digest(rows), "rows": rows,
        "candidate_import_count": sum(
            item == "candidates" or item.startswith("candidates.")
            for item in sys.modules
        ),
        "harness_preexisting_stdlib_regex_modules": sorted(harness_regex),
        "candidate_new_stdlib_regex_module_count": (
            len(set(stdlib_regex_modules()) - set(harness_regex))
            if engine_name == "rust" else None
        ),
        "candidate_runtime_provenance_checked": engine_name == "rust",
        "oracle_is_stdlib_only": engine_name == "stdlib",
        "external_regex_package_count": 0,
        "benchmark_files_read": 0, "fixture_files_read": 0,
        "sealed_cases_read": 0, "hidden_cases_read": 0,
        "archive_files_read": 0, "files_written": 0,
    }


def run_isolated_worker(
    role: str, engine: str, mode: str, *, request: dict[str, Any] | None = None,
) -> dict[str, Any]:
    require(type(role) is str and bool(role)
            and engine in ("stdlib", "rust") and mode in ("observe", "timing")
            and ((mode == "observe" and request is None)
                 or (mode == "timing" and type(request) is dict)),
            "only an explicitly named isolated public oracle/candidate is permitted")
    command = [
        str(PINNED_PYTHON), "-I", "-B", str(ROOT / SOURCE_RELATIVE),
        "--internal-worker", "--engine", engine,
        "--worker-mode", mode, "--role", role,
    ]
    payload = None if request is None else canonical(request)
    require(payload is None or len(payload) <= MAX_PROCESS_BYTES,
            "a complete bounded isolated public timing request was not retained")
    process = subprocess.Popen(
        command, stdin=subprocess.PIPE if payload is not None else subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(ROOT), shell=False,
        env={
            "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
            "LC_ALL": "C", "PATH": "/usr/bin:/bin",
        },
    )
    if mode == "observe":
        # Correctness observation is genuinely untimed, including timeout clocks.
        stdout, stderr = process.communicate(input=payload)
    else:
        try:
            stdout, stderr = process.communicate(
                input=payload, timeout=WORKER_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as error:
            process.kill()
            process.communicate()
            raise PublicPracticeError(
                "an isolated correctness-gated public timing worker timed out: " + role,
            ) from error
    require(process.returncode == 0 and stderr == b"",
            "an isolated public oracle/candidate worker failed: " + role
            + "; exit=" + str(process.returncode)
            + "; stderr=" + stderr[-2_000:].decode("utf-8", "replace"))
    document = decode_canonical(stdout, role + " complete isolated worker stdout")
    require(document.get("status") == "PASS"
            and document.get("label") == PRACTICE_LABEL
            and document.get("role") == role and document.get("engine") == engine
            and type(document.get("pid")) is int and document["pid"] == process.pid
            and document.get("python") == "3.14.6"
            and document.get("published_seed") == PUBLISHED_SEED
            and document.get("matrix_sha256") == MATRIX_SHA256
            and all(document.get(key) == 0 for key in (
                "benchmark_files_read", "fixture_files_read", "sealed_cases_read",
                "hidden_cases_read", "archive_files_read", "files_written",
            )),
            "an authentic isolated public worker, purity counter, or protocol changed")
    if engine == "stdlib":
        require(document.get("candidate_import_count") == 0,
                "the isolated standard-library-only oracle imported a candidate")
        require(document.get("oracle_is_stdlib_only") is True
                and document.get("candidate_runtime_provenance_checked") is False
                and document.get("candidate_new_stdlib_regex_module_count") is None
                and document.get("external_regex_package_count") == 0,
                "a stdlib-only public oracle worker claimed candidate provenance")
    else:
        require(type(document.get("candidate_import_count")) is int
                and document["candidate_import_count"] > 0,
                "the explicit isolated Rust worker omitted its named candidate")
        require(document.get("oracle_is_stdlib_only") is False
                and document.get("candidate_runtime_provenance_checked") is True
                and document.get("candidate_new_stdlib_regex_module_count") == 0
                and document.get("external_regex_package_count") == 0,
                "the isolated Rust runtime loaded an unauthorized regex dependency")
    require(type(document.get("harness_preexisting_stdlib_regex_modules")) is list
            and all(type(name) is str
                    for name in document["harness_preexisting_stdlib_regex_modules"]),
            "the isolated worker concealed incidental harness regex-module provenance")
    matrix = build_public_matrix()
    if mode == "observe":
        require(document.get("schema") == SCHEMA + "-isolated-observations"
                and document.get("case_count") == len(matrix),
                "a full source-only public correctness worker was substituted")
        validate_expected_records(
            document.get("records"), matrix, document.get("records_sha256"),
        )
    else:
        require(request is not None
                and document.get("schema") == SCHEMA + "-isolated-timing"
                and document.get("case_count") == len(matrix)
                and document.get("trial") == request["trial"]
                and document.get("expected_sha256") == request["expected_sha256"]
                and type(document.get("rows")) is list
                and len(document["rows"]) == len(matrix)
                and document.get("rows_sha256") == digest(document["rows"]),
                "an actual complete paired public timing worker was substituted")
        for position, (case_id, row) in enumerate(zip(
            request["case_order"], document["rows"], strict=True,
        )):
            require(type(row) is dict and row.get("case") == case_id
                    and row.get("trial") == request["trial"]
                    and row.get("position") == position
                    and type(row.get("elapsed_ns")) is int
                    and row["elapsed_ns"] > 0
                    and row.get("batch_iterations") == request["iterations"]
                    and row.get("correctness_checks")
                    == request["warmups"] + request["iterations"] + 1,
                    "an actual pair, trial, timing, or correctness gate was forged")
    return document


def geometric_mean(values: list[float]) -> float:
    require(type(values) is list and bool(values)
            and all(type(item) in (int, float)
                    and math.isfinite(item) and item > 0 for item in values),
            "every genuine positive finite paired public ratio is required")
    return math.exp(math.fsum(math.log(item) for item in values) / len(values))


def bootstrap_case_interval(
    pairs: list[tuple[int, int]], seed: int,
) -> dict[str, float | int | str]:
    require(type(pairs) is list and bool(pairs)
            and all(type(pair) is tuple and len(pair) == 2
                    and all(type(item) is int and item > 0 for item in pair)
                    for pair in pairs),
            "every exact paired public trial is mandatory for its confidence bound")
    generator = random.Random(seed)
    count = len(pairs)
    estimates: list[float] = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        sample = [pairs[generator.randrange(count)] for _ in range(count)]
        estimates.append(geometric_mean([
            baseline / candidate for baseline, candidate in sample
        ]))
    estimates.sort()
    return {
        "method": "published-seed paired percentile bootstrap",
        "confidence_level": 0.95, "resamples": BOOTSTRAP_RESAMPLES,
        "lower": estimates[int((BOOTSTRAP_RESAMPLES - 1) * 0.025)],
        "upper": estimates[int((BOOTSTRAP_RESAMPLES - 1) * 0.975)],
    }


def bootstrap_overall_interval(
    all_pairs: list[list[tuple[int, int]]], seed: int,
) -> dict[str, float | int | str]:
    require(type(all_pairs) is list and bool(all_pairs)
            and all(type(pairs) is list and bool(pairs) for pairs in all_pairs),
            "all equally weighted public cases are mandatory for overall confidence")
    generator = random.Random(seed)
    count = len(all_pairs)
    estimates: list[float] = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        case_ratios: list[float] = []
        for _ in range(count):
            pairs = all_pairs[generator.randrange(count)]
            sampled: list[float] = []
            for _ in range(len(pairs)):
                baseline, candidate = pairs[generator.randrange(len(pairs))]
                require(type(baseline) is int and baseline > 0
                        and type(candidate) is int and candidate > 0,
                        "an invalid overall paired public trial was injected")
                sampled.append(baseline / candidate)
            case_ratios.append(geometric_mean(sampled))
        estimates.append(geometric_mean(case_ratios))
    estimates.sort()
    return {
        "method": (
            "published-seed equally weighted case-and-paired-trial "
            "geometric-mean bootstrap"
        ),
        "confidence_level": 0.95, "resamples": BOOTSTRAP_RESAMPLES,
        "lower": estimates[int((BOOTSTRAP_RESAMPLES - 1) * 0.025)],
        "upper": estimates[int((BOOTSTRAP_RESAMPLES - 1) * 0.975)],
    }


def summarize_paired_trials(
    matrix: list[dict[str, Any]], raw_rows: list[dict[str, Any]],
    *, trial_count: int,
) -> dict[str, Any]:
    validate_public_matrix(matrix)
    require(type(trial_count) is int and trial_count > 0
            and type(raw_rows) is list
            and len(raw_rows) == len(matrix) * trial_count,
            "every original case and paired public trial belongs in the denominator")
    by_case: dict[str, list[dict[str, Any]]] = {
        case["case"]: [] for case in matrix
    }
    for row in raw_rows:
        require(type(row) is dict and row.get("case") in by_case
                and type(row.get("trial")) is int
                and 0 <= row["trial"] < trial_count
                and type(row.get("baseline_elapsed_ns")) is int
                and row["baseline_elapsed_ns"] > 0
                and type(row.get("rust_elapsed_ns")) is int
                and row["rust_elapsed_ns"] > 0,
                "an exact paired public trial timing was substituted")
        by_case[row["case"]].append(row)
    summaries: list[dict[str, Any]] = []
    all_pairs: list[list[tuple[int, int]]] = []
    for index, case in enumerate(matrix):
        rows = sorted(by_case[case["case"]], key=lambda row: row["trial"])
        require(len(rows) == trial_count
                and [row["trial"] for row in rows] == list(range(trial_count)),
                "an actual source-ordered paired public trial was omitted")
        pairs = [
            (row["baseline_elapsed_ns"], row["rust_elapsed_ns"])
            for row in rows
        ]
        all_pairs.append(pairs)
        baseline_median = statistics.median([pair[0] for pair in pairs])
        candidate_median = statistics.median([pair[1] for pair in pairs])
        ratio = geometric_mean([
            baseline / candidate for baseline, candidate in pairs
        ])
        interval = bootstrap_case_interval(
            pairs, PUBLISHED_SEED ^ ((index + 1) * 0x9E37_79B9),
        )
        summaries.append({
            "case": case["case"], "dataset": case["dataset"],
            "workload": case["workload"], "domain": case["domain"],
            "operation": case["operation"], "lifecycle": case["lifecycle"],
            "subject_length": case["subject_length"], "flags": case["flags"],
            "weight_numerator": 1, "weight_denominator": len(matrix),
            "paired_trial_count": trial_count,
            "baseline_median_batch_ns_descriptive": baseline_median,
            "rust_median_batch_ns_descriptive": candidate_median,
            "median_batch_ratio_descriptive": baseline_median / candidate_median,
            "point_estimator": "geometric mean of every paired trial ratio",
            "speedup_vs_baseline": ratio,
            "rust_change_percent": (1.0 / ratio - 1.0) * 100.0,
            "speedup_confidence_interval": interval,
            "statistically_faster": interval["lower"] > 1.0,
            "statistically_slower": interval["upper"] < 1.0,
            "regression_exceeds_20_percent": (1.0 / ratio) > 1.2,
        })
    overall = geometric_mean([item["speedup_vs_baseline"] for item in summaries])
    interval = bootstrap_overall_interval(all_pairs, PUBLISHED_SEED ^ 0xA110_CAF2)
    regressions = [
        item for item in summaries if item["regression_exceeds_20_percent"]
    ]
    workloads = sorted({case["workload"] for case in matrix})
    lifecycles = sorted({case["lifecycle"] for case in matrix})
    return {
        "label": PRACTICE_LABEL,
        "weight_policy": "every frozen original public case has identical weight",
        "point_estimator": (
            "equally weighted geometric mean of each public case's "
            "geometric mean of every original paired trial ratio"
        ),
        "timed_interval": (
            "complete public API invocation, operation/result materialization, "
            "callback/warning normalization, and exact per-call stdlib correctness "
            "comparison; never native-only timing"
        ),
        "case_denominator": len(matrix), "paired_trials_per_case": trial_count,
        "baseline_first_paired_rounds": (trial_count + 1) // 2,
        "rust_first_paired_rounds": trial_count // 2,
        "pair_order_is_exactly_balanced": trial_count % 2 == 0,
        "total_complete_paired_rows": len(raw_rows),
        "text_case_count": sum(case["domain"] == "text" for case in matrix),
        "bytes_case_count": sum(case["domain"] == "bytes" for case in matrix),
        "operation_count": len(OPERATIONS),
        "workload_count": len(workloads), "workloads": workloads,
        "lifecycle_count": len(lifecycles), "lifecycles": lifecycles,
        "weighted_geomean_speedup_vs_baseline": overall,
        "overall_speedup_confidence_interval": interval,
        "statistically_faster_case_count": sum(
            item["statistically_faster"] for item in summaries
        ),
        "statistically_faster_fraction": sum(
            item["statistically_faster"] for item in summaries
        ) / len(matrix),
        "statistically_slower_case_count": sum(
            item["statistically_slower"] for item in summaries
        ),
        "regression_over_20_percent_count": len(regressions),
        "all_regressions_over_20_percent": regressions,
        "all_case_results": summaries,
        "candidate_qualified_for_sealed_final_holdout": False,
        "sealed_final_holdout_opened": False,
        "final_winner_selected": False,
    }


def run_correctness_only() -> dict[str, Any]:
    verify_pinned_runtime()
    matrix = build_public_matrix()
    validate_public_matrix(matrix)
    baseline = run_isolated_worker("public_v2_untimed_stdlib", "stdlib", "observe")
    candidate = run_isolated_worker("public_v2_untimed_rust", "rust", "observe")
    require(baseline["pid"] != candidate["pid"],
            "the public standard-library oracle and Rust were not isolated")
    mismatches: list[dict[str, Any]] = []
    for case, reference, actual in zip(
        matrix, baseline["records"], candidate["records"], strict=True,
    ):
        require(reference["case"] == actual["case"] == case["case"],
                "a complete source-ordered public correctness case changed")
        if reference["outcome"] != actual["outcome"]:
            mismatches.append({
                "case": case["case"], "dataset": case["dataset"],
                "workload": case["workload"], "domain": case["domain"],
                "operation": case["operation"], "lifecycle": case["lifecycle"],
                "flags": case["flags"], "pattern": case["pattern"],
                "subject": case["subject"], "replacement": case["replacement"],
                "limit": case["limit"], "pos": case["pos"],
                "endpos": case["endpos"],
                "baseline_outcome": reference["outcome"],
                "rust_outcome": actual["outcome"],
            })
    return {
        "schema": SCHEMA + "-actual-untimed-correctness",
        "status": "PASS" if not mismatches else "FAIL", "label": PRACTICE_LABEL,
        "python": "3.14.6", "published_seed": PUBLISHED_SEED,
        "matrix_sha256": MATRIX_SHA256, "case_denominator": len(matrix),
        "actual_baseline_cases": len(baseline["records"]),
        "actual_rust_cases": len(candidate["records"]),
        "baseline_records_sha256": baseline["records_sha256"],
        "rust_records_sha256": candidate["records_sha256"],
        "baseline_pid": baseline["pid"], "rust_pid": candidate["pid"],
        "mismatch_count": len(mismatches),
        "first_mismatch": mismatches[0] if mismatches else None,
        "all_mismatches": mismatches, "actual_candidate_workers": 1,
        "timing_trials_run": 0, "clock_samples": 0,
        "benchmark_files_read": 0, "fixture_files_read": 0,
        "sealed_cases_read": 0, "hidden_cases_read": 0,
        "archive_files_read": 0, "files_written": 0,
        "performance": "NOT MEASURED",
        "candidate_qualified_for_sealed_final_holdout": False,
        "sealed_final_holdout_opened": False,
        "final_winner_selected": False,
    }


def run_public_practice(
    *, trials: int, iterations: int, warmups: int,
) -> dict[str, Any]:
    verify_pinned_runtime()
    require(type(trials) is int and 2 <= trials <= 100
            and type(iterations) is int and 1 <= iterations <= 1_000
            and type(warmups) is int and 0 <= warmups <= 100,
            "exact bounded paired public trials, batches, and warmups are required")
    matrix = build_public_matrix()
    validate_public_matrix(matrix)
    baseline = run_isolated_worker("public_v2_stdlib_correctness", "stdlib", "observe")
    candidate = run_isolated_worker("public_v2_rust_correctness", "rust", "observe")
    require(baseline["pid"] != candidate["pid"],
            "the original standard-library and candidate correctness were not isolated")
    require(baseline["records"] == candidate["records"]
            and baseline["records_sha256"] == candidate["records_sha256"],
            "Rust failed the complete frozen public correctness gate; no timing allowed")
    raw_rows: list[dict[str, Any]] = []
    process_provenance: list[dict[str, Any]] = []
    for trial in range(trials):
        case_order = [case["case"] for case in matrix]
        random.Random(PUBLISHED_SEED ^ (trial + 1)).shuffle(case_order)
        request = {
            "schema": SCHEMA + "-timing-request",
            "published_seed": PUBLISHED_SEED, "matrix_sha256": MATRIX_SHA256,
            "trial": trial, "iterations": iterations, "warmups": warmups,
            "expected_sha256": baseline["records_sha256"],
            "expected_records": baseline["records"], "case_order": case_order,
        }
        pair_order = ("stdlib", "rust") if trial % 2 == 0 else ("rust", "stdlib")
        actual: dict[str, dict[str, Any]] = {}
        for position, engine in enumerate(pair_order):
            role = "public_v2_trial_" + format(trial, "03d") + "_" + engine
            observed = run_isolated_worker(role, engine, "timing", request=request)
            actual[engine] = observed
            process_provenance.append({
                "trial": trial, "engine": engine,
                "pair_execution_position": position,
                "pid": observed["pid"], "rows_sha256": observed["rows_sha256"],
            })
        require(actual["stdlib"]["pid"] != actual["rust"]["pid"],
                "an actual public paired trial reused its oracle process")
        for reference, observed in zip(
            actual["stdlib"]["rows"], actual["rust"]["rows"], strict=True,
        ):
            require(reference["case"] == observed["case"]
                    and reference["trial"] == observed["trial"] == trial
                    and reference["position"] == observed["position"]
                    and reference["expected_outcome_sha256"]
                    == observed["expected_outcome_sha256"],
                    "an actual paired public trial lost its exact common oracle case")
            raw_rows.append({
                "case": reference["case"], "trial": trial,
                "case_order_position": reference["position"],
                "pair_order": list(pair_order),
                "baseline_pid": actual["stdlib"]["pid"],
                "rust_pid": actual["rust"]["pid"],
                "batch_iterations": iterations,
                "correctness_checks_per_engine": reference["correctness_checks"],
                "expected_outcome_sha256": reference["expected_outcome_sha256"],
                "baseline_elapsed_ns": reference["elapsed_ns"],
                "rust_elapsed_ns": observed["elapsed_ns"],
            })
    require(len(raw_rows) == len(matrix) * trials,
            "a complete public practice case or actual paired trial was omitted")
    return {
        "schema": SCHEMA + "-actual-public-practice-report", "status": "PASS",
        "label": PRACTICE_LABEL, "python": "3.14.6",
        "published_seed": PUBLISHED_SEED, "matrix_sha256": MATRIX_SHA256,
        "case_count": len(matrix), "matrix": matrix,
        "correctness_reference_records_sha256": baseline["records_sha256"],
        "correctness_reference_records": baseline["records"],
        "baseline_correctness_pid": baseline["pid"],
        "rust_correctness_pid": candidate["pid"],
        "paired_trials": trials, "batch_iterations": iterations,
        "warmup_iterations": warmups,
        "trial_process_provenance": process_provenance,
        "raw_paired_rows_sha256": digest(raw_rows), "raw_paired_rows": raw_rows,
        "results": summarize_paired_trials(matrix, raw_rows, trial_count=trials),
        "benchmark_files_read": 0, "fixture_files_read": 0,
        "sealed_cases_read": 0, "hidden_cases_read": 0,
        "archive_files_read": 0,
        "candidate_production_reference_delegation": "NOT AUDITED BY PUBLIC PRACTICE",
        "candidate_qualified_for_sealed_final_holdout": False,
        "sealed_final_holdout_opened": False,
        "final_winner_selected": False,
    }


def approved_output_parts(value: Any) -> tuple[str, ...]:
    require(type(value) is str and bool(value)
            and "\x00" not in value and "\\" not in value,
            "an exact approved named public-practice JSON path is mandatory")
    if os.path.isabs(value):
        prefix = str(ROOT) + os.sep
        require(value.startswith(prefix),
                "an explicit output outside the owned repository is forbidden")
        relative = value[len(prefix):]
    else:
        relative = value
    path = PurePosixPath(relative)
    require(not path.is_absolute() and ".." not in path.parts
            and path.as_posix() == relative
            and len(path.parts) >= 3
            and path.parts[:2] == ("experiments", "rust_public_practice_v2")
            and path.parts[-1].endswith(".json")
            and path.parts[-1] != ".json",
            "write only an explicitly named JSON beneath " + OUTPUT_PREFIX)
    return path.parts


def write_approved_output(value: str, document: Mapping[str, Any]) -> dict[str, Any]:
    parts = approved_output_parts(value)
    payload = canonical(dict(document))
    require(0 < len(payload) <= MAX_OUTPUT_BYTES,
            "a complete bounded public-practice report is mandatory")
    directory_flags = (
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    opened: list[int] = []
    writer: int | None = None
    directory: int | None = None
    writer_info: Any = None
    durable = False
    try:
        current = os.open(str(ROOT), directory_flags)
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode),
                "the exact original public output root is not a real directory")
        for component in parts[:-1]:
            try:
                following = os.open(component, directory_flags, dir_fd=current)
            except FileNotFoundError:
                os.mkdir(component, mode=0o755, dir_fd=current)
                following = os.open(component, directory_flags, dir_fd=current)
            opened.append(following)
            require(stat.S_ISDIR(os.fstat(following).st_mode),
                    "an approved output component is not a no-follow directory")
            current = following
        directory = current
        writer = os.open(
            parts[-1], os.O_WRONLY | os.O_CREAT | os.O_EXCL
            | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
            0o644, dir_fd=directory,
        )
        writer_info = os.fstat(writer)
        require(stat.S_ISREG(writer_info.st_mode),
                "the exclusively created public report is not a regular file")
        written = os.write(writer, payload)
        require(type(written) is int and written == len(payload),
                "the approved exclusive public report write was short or forged")
        os.fsync(writer)
        os.fsync(directory)
        durable = True
        return {
            "path": "/".join(parts), "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload), "actual_write_calls": 1,
            "file_fsync_completed": True, "directory_fsync_completed": True,
        }
    finally:
        if writer is not None and not durable and writer_info is not None \
                and directory is not None:
            try:
                actual = os.stat(parts[-1], dir_fd=directory, follow_symlinks=False)
                if stat.S_ISREG(actual.st_mode) \
                        and actual.st_dev == writer_info.st_dev \
                        and actual.st_ino == writer_info.st_ino:
                    os.unlink(parts[-1], dir_fd=directory)
                    os.fsync(directory)
            except OSError:
                pass
        if writer is not None:
            os.close(writer)
        for descriptor in reversed(opened):
            os.close(descriptor)


def source_self_test(mode: str) -> dict[str, Any]:
    """Pure source validation: no engine, process, clock, case file, or write."""
    verify_pinned_runtime()
    require(mode in ("self-test", "verify-source"),
            "only explicitly source-only v2 verification is permitted")
    harness_regex = stdlib_regex_modules()
    reject_external_regex_packages()
    require(not any(item == "candidates" or item.startswith("candidates.")
                    for item in sys.modules),
            "source-only public verification imported a candidate")
    matrix = build_public_matrix()
    validate_public_matrix(matrix)
    text, binary = public_datasets()
    require(len(text) == len(binary) == 47
            and len({item[0] for item in text + binary}) == 94
            and len(set(OPERATIONS)) == len(OPERATIONS)
            and len(matrix) == 94 * len(OPERATIONS)
            and sum(case["domain"] == "text" for case in matrix)
            == sum(case["domain"] == "bytes" for case in matrix),
            "the frozen enlarged equal-domain public denominator changed")

    rejected_documents: list[str] = []
    for label, payload in (
        ("duplicate-keys", b'{"a":1,"a":2}\n'),
        ("nonfinite", b'{"a":NaN}\n'),
        ("truncated", b'{"a":1'),
        ("concatenated", b'{"a":1}\n{"b":2}\n'),
        ("noncanonical-spacing", b'{"a": 1}\n'),
        ("noncanonical-key-order", b'{"z":1,"a":2}\n'),
        ("empty", b""),
    ):
        try:
            decode_canonical(payload, label)
        except PublicPracticeError:
            rejected_documents.append(label)
        else:
            raise PublicPracticeError("an adversarial process document was accepted")
    require(decode_canonical(canonical({"a": 1}), "valid") == {"a": 1}
            and len(rejected_documents) == 7,
            "strict canonical process decoding failed its adversarial controls")

    rejected_values: list[str] = []
    for label, value in (
        ("uppercase-hex", {"type": "bytes", "hex": "AB"}),
        ("spaced-hex", {"type": "bytes", "hex": "61 62"}),
        ("extra-field", {"type": "bytes", "hex": "61", "extra": 1}),
        ("memoryview-shape", {
            "type": "memoryview", "hex": "6162", "readonly": True,
            "format": "B", "shape": [1],
        }),
        ("memoryview-mutability", {
            "type": "memoryview", "hex": "61", "readonly": 1,
            "format": "B", "shape": [1],
        }),
        ("foreign-type", {"type": "foreign", "hex": "61"}),
    ):
        try:
            materialize_typed(value)
        except PublicPracticeError:
            rejected_values.append(label)
        else:
            raise PublicPracticeError("an adversarial typed public value was accepted")
    require(len(rejected_values) == 6,
            "source-only canonical buffer rejection controls were bypassed")

    rejected_matrices: list[str] = []
    omitted = matrix[:-1]
    duplicate = list(matrix)
    duplicate[-1] = dict(duplicate[0])
    reweighted = list(matrix)
    reweighted[0] = dict(reweighted[0], weight_numerator=2)
    renamed = list(matrix)
    renamed[0] = dict(renamed[0], operation="module.injected")
    changed_bounds = list(matrix)
    changed_bounds[0] = dict(changed_bounds[0], endpos=-1)
    for label, actual in (
        ("omitted-case", omitted), ("duplicate-case", duplicate),
        ("reweighted-case", reweighted), ("injected-operation", renamed),
        ("changed-bounds", changed_bounds),
    ):
        try:
            validate_public_matrix(actual)
        except PublicPracticeError:
            rejected_matrices.append(label)
        else:
            raise PublicPracticeError("an adversarial public matrix was accepted")
    require(len(rejected_matrices) == 5,
            "source-only denominator/case/weight controls were bypassed")

    rejected_paths: list[str] = []
    for forbidden in (
        "/tmp/foreign-v2-practice.json",
        "../foreign-v2-practice.json",
        "experiments/foreign-v2-practice.json",
        "experiments/rust_public_practice_v2/../foreign.json",
        "experiments/rust_public_practice_v2/not-json.txt",
        "oracle/phase3/forbidden.json",
        "experiments/rust_public_practice_v2/.json",
        "experiments\\rust_public_practice_v2\\foreign.json",
    ):
        try:
            approved_output_parts(forbidden)
        except PublicPracticeError:
            rejected_paths.append(forbidden)
        else:
            raise PublicPracticeError("an unauthorized public output path was accepted")
    require(len(rejected_paths) == 8,
            "source-only public path traversal or restricted-path control failed")

    pairs = [(100, 100), (103, 103), (107, 107), (109, 109)]
    confidence = bootstrap_case_interval(pairs, PUBLISHED_SEED)
    require(confidence == bootstrap_case_interval(pairs, PUBLISHED_SEED)
            and confidence["lower"] == confidence["upper"] == 1.0,
            "the source-only published-seed paired bootstrap is not deterministic")
    overall = bootstrap_overall_interval(
        [pairs, list(reversed(pairs))], PUBLISHED_SEED,
    )
    require(overall["lower"] == overall["upper"] == 1.0,
            "the source-only equally weighted oracle self-comparison was altered")
    require(stdlib_regex_modules() == harness_regex
            and not any(item == "candidates" or item.startswith("candidates.")
                        for item in sys.modules),
            "source-only verification altered harness regex imports or loaded Rust")
    return {
        "schema": SCHEMA + "-source-only-" + mode, "status": "PASS",
        "label": PRACTICE_LABEL, "python": "3.14.6",
        "published_seed": PUBLISHED_SEED, "matrix_sha256": MATRIX_SHA256,
        "case_count": len(matrix), "operation_count": len(OPERATIONS),
        "dataset_count": len(text) + len(binary),
        "text_dataset_count": len(text), "bytes_dataset_count": len(binary),
        "text_case_count": len(text) * len(OPERATIONS),
        "bytes_case_count": len(binary) * len(OPERATIONS),
        "workload_count": len({case["workload"] for case in matrix}),
        "lifecycle_count": len({case["lifecycle"] for case in matrix}),
        "mutable_bytearray_dataset_count": sum(
            type(item[2]) is bytearray for item in binary
        ),
        "mutable_memoryview_dataset_count": sum(
            type(item[2]) is memoryview and not item[2].readonly
            for item in binary
        ),
        "readonly_memoryview_dataset_count": sum(
            type(item[2]) is memoryview and item[2].readonly
            for item in binary
        ),
        "weight_policy": "all frozen original public cases have identical weight",
        "rejected_adversarial_process_documents": rejected_documents,
        "rejected_adversarial_typed_values": rejected_values,
        "rejected_adversarial_matrices": rejected_matrices,
        "rejected_unapproved_output_count": len(rejected_paths),
        "seeded_bootstrap_baseline_speedup": 1.0,
        "seeded_bootstrap_baseline_confidence_interval": confidence,
        "seeded_overall_baseline_confidence_interval": overall,
        "default_paired_rounds": DEFAULT_PAIRED_TRIALS,
        "default_pair_order_exactly_balanced": DEFAULT_PAIRED_TRIALS % 2 == 0,
        "actual_candidate_workers": 0, "actual_oracle_workers": 0,
        "subprocesses_started": 0, "candidate_import_count": 0,
        "harness_preexisting_stdlib_regex_modules": sorted(harness_regex),
        "new_stdlib_regex_modules": [],
        "stdlib_oracle_matching_calls": 0,
        "external_regex_package_count": 0, "timing_trials_run": 0,
        "clock_samples": 0, "benchmark_files_read": 0,
        "fixture_files_read": 0, "sealed_cases_read": 0,
        "hidden_cases_read": 0, "archive_files_read": 0,
        "files_written": 0, "performance": "NOT MEASURED",
        "candidate_qualified_for_sealed_final_holdout": False,
        "sealed_final_holdout_opened": False,
        "final_winner_selected": False,
    }


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Frozen independent PUBLIC DEVELOPMENT/PRACTICE ONLY; "
            "never a sealed, hidden, or final holdout"
        ),
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-source", action="store_true")
    modes.add_argument("--correctness-only", action="store_true")
    modes.add_argument("--run", action="store_true")
    modes.add_argument("--internal-worker", action="store_true",
                       help=argparse.SUPPRESS)
    parser.add_argument("--output")
    parser.add_argument("--trials", type=int, default=DEFAULT_PAIRED_TRIALS)
    parser.add_argument("--iterations", type=int, default=DEFAULT_BATCH_ITERATIONS)
    parser.add_argument("--warmups", type=int, default=DEFAULT_WARMUP_ITERATIONS)
    parser.add_argument("--engine", choices=("stdlib", "rust"), help=argparse.SUPPRESS)
    parser.add_argument("--worker-mode", choices=("observe", "timing"),
                        help=argparse.SUPPRESS)
    parser.add_argument("--role", help=argparse.SUPPRESS)
    return parser.parse_args(arguments)


def reject_nondefault_timing(options: argparse.Namespace) -> None:
    require(options.trials == DEFAULT_PAIRED_TRIALS
            and options.iterations == DEFAULT_BATCH_ITERATIONS
            and options.warmups == DEFAULT_WARMUP_ITERATIONS,
            "source-only/untimed correctness cannot accept timing parameters")


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    if options.self_test or options.verify_source:
        require(options.output is None and options.engine is None
                and options.worker_mode is None and options.role is None,
                "source-only verification cannot create workers, read cases, or write")
        reject_nondefault_timing(options)
        document = source_self_test(
            "self-test" if options.self_test else "verify-source",
        )
    elif options.correctness_only:
        require(options.output is None and options.engine is None
                and options.worker_mode is None and options.role is None,
                "untimed public correctness cannot write or inject worker arguments")
        reject_nondefault_timing(options)
        document = run_correctness_only()
    elif options.run:
        require(options.engine is None and options.worker_mode is None
                and options.role is None,
                "explicit paired public practice cannot inject worker arguments")
        if options.output is not None:
            approved_output_parts(options.output)
        document = run_public_practice(
            trials=options.trials, iterations=options.iterations,
            warmups=options.warmups,
        )
        if options.output is not None:
            publication = write_approved_output(options.output, document)
            document = {
                "schema": SCHEMA + "-published-public-practice-summary",
                "status": "PASS", "label": PRACTICE_LABEL,
                "matrix_sha256": MATRIX_SHA256,
                "case_count": document["case_count"],
                "raw_paired_rows_sha256": document["raw_paired_rows_sha256"],
                "results": document["results"], "publication": publication,
                "benchmark_files_read": 0, "fixture_files_read": 0,
                "sealed_cases_read": 0, "hidden_cases_read": 0,
                "archive_files_read": 0,
                "sealed_final_holdout_opened": False,
                "final_winner_selected": False,
            }
    else:
        require(options.output is None and options.engine in ("stdlib", "rust")
                and options.worker_mode in ("observe", "timing")
                and type(options.role) is str and bool(options.role),
                "an isolated internal worker requires exact explicit provenance")
        reject_nondefault_timing(options)
        document = (
            observe_worker(options.role, options.engine)
            if options.worker_mode == "observe"
            else timing_worker(options.role, options.engine)
        )
    sys.stdout.buffer.write(canonical(document))
    sys.stdout.buffer.flush()
    return 0 if document.get("status") == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PublicPracticeError as error:
        print("independent public practice failed closed: " + str(error),
              file=sys.stderr)
        raise SystemExit(1) from error
