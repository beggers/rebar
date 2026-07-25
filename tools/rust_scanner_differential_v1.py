#!/usr/bin/env python3
"""Frozen, independent, untimed public ``re.Scanner`` differential oracle."""

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
from typing import Any, Callable, Mapping
import types
import warnings


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/rust_scanner_differential_v1.py"
PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14",
)
PINNED_STDLIB_RE = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
    "lib/python3.14/re/__init__.py",
)
SCHEMA = "rebar-independent-rust-scanner-differential-v1"
PUBLISHED_SEED = 0x5343_414E_4E45_5231
VARIANTS_PER_FAMILY = 32
MATRIX_SHA256 = (
    "83a8ad125b36846c1790ca01564305b2ab9714185f972efa838740b7bbf4b55c"
)
BASELINE_SHA256 = (
    "37de08e1991adf28990e35b72c2130ebafa78c72b04750d28550cce08555666d"
)
MAX_WORKER_BYTES = 32 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024
IGNORECASE = 2
LOCALE = 4
MULTILINE = 8
DOTALL = 16
UNICODE = 32
VERBOSE = 64
ASCII = 256
FAMILIES = (
    "one-branch",
    "two-branches",
    "three-branches",
    "four-branches",
    "leftmost-action-priority",
    "nested-captures",
    "numbered-captures",
    "named-captures",
    "duplicate-named-captures-invalid",
    "phrase-local-backreference",
    "phrase-local-conditional",
    "overflow-invalid-compiled-scanner",
    "inline-global-flags",
    "inline-scoped-flags",
    "default-unicode",
    "explicit-ascii",
    "bytes-locale",
    "invalid-flag-combinations",
    "mixed-lexicon-invalid",
    "bytes-subject",
    "bytearray-subject",
    "readonly-memoryview-subject",
    "writable-memoryview-subject",
    "mixed-subject-invalid",
    "zero-width",
    "callback-success",
    "callback-error",
    "tuple-action-value",
    "list-lexicon-identity",
    "tuple-lexicon-identity",
    "post-construction-lexicon-mutation",
    "character-class-warning",
)
CASE_COUNT = len(FAMILIES) * VARIANTS_PER_FAMILY

if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))


class ScannerOracleError(Exception):
    """Reject an incomplete, forged, hidden, or timed Scanner observation."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise ScannerOracleError(message)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, allow_nan=False,
        sort_keys=True, separators=(",", ":"),
    ).encode("ascii") + b"\n"


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def valid_digest(value: Any) -> bool:
    return type(value) is str and len(value) == 64 \
        and len(set(value)) > 1 \
        and all(letter in "0123456789abcdef" for letter in value)


def unique_json_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    actual: dict[str, Any] = {}
    for name, value in items:
        require(type(name) is str and name not in actual,
                "duplicate actual Scanner worker evidence is forbidden")
        actual[name] = value
    return actual


def decode_canonical(raw: Any, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_WORKER_BYTES,
            "complete bounded actual Scanner worker output is required: " + label)
    try:
        actual = json.loads(
            raw, object_pairs_hook=unique_json_object,
            parse_constant=lambda value: (_ for _ in ()).throw(
                ScannerOracleError("nonfinite Scanner evidence is forbidden"),
            ),
        )
    except (TypeError, ValueError, UnicodeError, json.JSONDecodeError) as error:
        raise ScannerOracleError(
            "invalid complete genuine Scanner worker evidence: " + label,
        ) from error
    require(type(actual) is dict and canonical(actual) == raw,
            "the complete canonical Scanner worker output was substituted")
    return actual


def encode_subject(value: Any) -> dict[str, Any]:
    if type(value) is str:
        return {"type": "str", "value": value}
    if type(value) is bytes:
        return {"type": "bytes", "hex": value.hex()}
    if type(value) is bytearray:
        return {"type": "bytearray", "hex": bytes(value).hex()}
    if type(value) is memoryview:
        require(value.format == "B" and value.ndim == 1 and value.contiguous,
                "only original contiguous public byte carriers are allowed")
        return {
            "type": "memoryview", "hex": value.tobytes().hex(),
            "readonly": value.readonly,
            "format": value.format,
            "shape": list(value.shape),
        }
    raise ScannerOracleError("an unfrozen Scanner subject type was injected")


def decode_subject(value: Any) -> str | bytes | bytearray | memoryview:
    require(type(value) is dict,
            "an original typed Scanner subject or phrase is mandatory")
    kind = value.get("type")
    if kind == "str":
        require(set(value) == {"type", "value"}
                and type(value.get("value")) is str,
                "an original Scanner text subject was forged")
        return value["value"]
    require(kind in ("bytes", "bytearray", "memoryview")
            and type(value.get("hex")) is str,
            "an original Scanner bytes-like carrier was substituted")
    try:
        actual = bytes.fromhex(value["hex"])
    except ValueError as error:
        raise ScannerOracleError("a Scanner bytes payload was corrupted") from error
    require(actual.hex() == value["hex"],
            "noncanonical original Scanner bytes are forbidden")
    if kind == "bytes":
        require(set(value) == {"type", "hex"},
                "the exact public bytes carrier was substituted")
        return actual
    if kind == "bytearray":
        require(set(value) == {"type", "hex"},
                "the exact mutable bytearray carrier was substituted")
        return bytearray(actual)
    require(set(value) == {"type", "hex", "readonly", "format", "shape"}
            and type(value.get("readonly")) is bool
            and value.get("format") == "B"
            and value.get("shape") == [len(actual)],
            "an original memoryview's readonly state or shape was forged")
    return memoryview(actual if value["readonly"] else bytearray(actual))


def encode_phrase(value: str | bytes) -> dict[str, Any]:
    return encode_subject(value)


def _typed_phrase(value: str, domain: str) -> dict[str, Any]:
    require(domain in ("str", "bytes"),
            "an original Scanner lexicon domain is mandatory")
    return encode_phrase(value if domain == "str" else value.encode("ascii"))


def build_matrix() -> list[dict[str, Any]]:
    seeded = random.Random(PUBLISHED_SEED)
    records: list[dict[str, Any]] = []
    for family_index, family in enumerate(FAMILIES):
        for variant in range(VARIANTS_PER_FAMILY):
            domain = "str" if (family_index + variant) % 2 == 0 else "bytes"
            if family in (
                "bytes-locale", "bytes-subject", "bytearray-subject",
                "readonly-memoryview-subject", "writable-memoryview-subject",
            ):
                domain = "bytes"
            if family in ("default-unicode", "inline-global-flags",
                          "inline-scoped-flags"):
                domain = "str"

            branch_count = {
                "one-branch": 1,
                "two-branches": 2,
                "three-branches": 3,
                "four-branches": 4,
            }.get(family, 2 + variant % 2)
            expressions = [
                r"(?P<word>[A-Za-z]+)",
                r"\d+",
                r"\s+",
                r".",
            ][:branch_count]
            flags = (0, IGNORECASE, MULTILINE, DOTALL)[variant % 4]
            mutation = "none"
            lexicon_type = "list"
            action_mode = "identity"

            if family == "leftmost-action-priority":
                expressions = [r"a+", r"a", r"\s+"]
            elif family == "nested-captures":
                expressions[0] = r"((a)(b(c)?))"
            elif family == "numbered-captures":
                expressions[0] = r"(a)(b)(c)?"
            elif family == "named-captures":
                expressions[0] = r"(?P<first>a)(?P<second>b)(?P<third>c)?"
            elif family == "duplicate-named-captures-invalid":
                expressions = [r"(?P<duplicate>a)", r"(?P<duplicate>b)"]
            elif family == "phrase-local-backreference":
                expressions[0] = r"(a)(b)\2"
            elif family == "phrase-local-conditional":
                expressions[0] = r"(a)?(?(1)b|c)"
            elif family == "overflow-invalid-compiled-scanner":
                expressions[0] = r"(?(4294967296)a|b)"
            elif family == "inline-global-flags":
                expressions[0] = (r"(?i)[a-z]+", r"(?a)\w+")[variant % 2]
                flags = 0
            elif family == "inline-scoped-flags":
                expressions[0] = (
                    r"(?i:[a-z]+)", r"(?a:\w+)", r"(?s:a.b)",
                    r"(?x: a [ ] b )",
                )[variant % 4]
            elif family == "default-unicode":
                expressions[0] = r"\w+"
                flags = 0
            elif family == "explicit-ascii":
                expressions[0] = r"\w+"
                flags = ASCII
            elif family == "bytes-locale":
                expressions[0] = r"\w+"
                flags = LOCALE
            elif family == "invalid-flag-combinations":
                flags = (
                    ASCII | UNICODE,
                    UNICODE if domain == "bytes" else LOCALE,
                    LOCALE | ASCII,
                    LOCALE | UNICODE,
                )[variant % 4]
            elif family == "mixed-lexicon-invalid":
                expressions = [r"(?P<word>[A-Za-z]+)", r"\d+"]
            elif family == "zero-width":
                expressions = [r"(?=a)", r"a+", r"\s+"]
            elif family == "callback-success":
                action_mode = ("identity", "upper")[variant % 2]
            elif family == "callback-error":
                action_mode = "raise"
            elif family == "tuple-action-value":
                action_mode = "tuple"
            elif family == "tuple-lexicon-identity":
                lexicon_type = "tuple"
            elif family == "post-construction-lexicon-mutation":
                mutation = ("replace-action", "append", "swap", "delete")[
                    variant % 4
                ]
            elif family == "character-class-warning":
                expressions[0] = (
                    r"[a&&b]", r"[a~~b]", r"[a||b]", r"[[]",
                )[variant % 4]

            noise = "".join(seeded.choice("abcdef0123456789") for _ in range(5))
            tail = " !tail-" + format(variant, "02d") + "-" + noise
            text = (
                "abc abb aaaa ABC 123 café\nabc" + tail
                if domain == "str"
                else "abc abb aaaa ABC 123 xyz\nabc" + tail
            )
            payload: Any = text if domain == "str" else text.encode("ascii")
            if family == "bytearray-subject":
                payload = bytearray(payload)
            elif family == "readonly-memoryview-subject":
                payload = memoryview(payload)
            elif family == "writable-memoryview-subject":
                payload = memoryview(bytearray(payload))
            elif family == "mixed-subject-invalid":
                payload = (
                    text.encode("utf-8") if domain == "str" else text
                )

            phrases: list[dict[str, Any]] = []
            for branch, expression in enumerate(expressions):
                actual_domain = domain
                if family == "mixed-lexicon-invalid" and branch == 1:
                    actual_domain = "bytes" if domain == "str" else "str"
                phrase = _typed_phrase(expression, actual_domain)
                if expression == r"\s+":
                    action = "skip"
                elif branch == 0:
                    action = action_mode
                else:
                    action = ("identity", "upper", "tuple")[
                        (variant + branch) % 3
                    ]
                phrases.append({"phrase": phrase, "action": action})

            records.append({
                "case": "scanner-differential.v1." + format(len(records), "04d"),
                "family": family,
                "variant": variant,
                "domain": domain,
                "flags": flags,
                "lexicon_type": lexicon_type,
                "mutation": mutation,
                "lexicon": phrases,
                "subject": encode_subject(payload),
            })
    return records


def validate_matrix(records: Any) -> str:
    require(type(records) is list and len(records) == CASE_COUNT
            and records == build_matrix()
            and digest(records) == MATRIX_SHA256
            and len({case["case"] for case in records}) == CASE_COUNT,
            "every original seeded Scanner differential case is mandatory")
    require(CASE_COUNT == 1024 and len(FAMILIES) == 32,
            "the independent Scanner denominator silently changed")
    for family in FAMILIES:
        require(sum(case["family"] == family for case in records)
                == VARIANTS_PER_FAMILY,
                "an original Scanner edge family was omitted: " + family)
    return MATRIX_SHA256


def verify_runtime(*, candidate_loaded: bool = False) -> None:
    expected_source = str(ROOT / SOURCE_RELATIVE)
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and bool(sys.path) and sys.path[0] == str(ROOT)
            and os.path.realpath(str(ROOT)) == str(ROOT)
            and os.path.abspath(__file__) == expected_source
            and os.path.realpath(__file__) == expected_source
            and os.path.abspath(sys.executable) == str(PINNED_PYTHON)
            and os.path.realpath(sys.executable) == str(PINNED_PYTHON),
            "use only the independently frozen root, source, and CPython 3.14.6")
    if not candidate_loaded:
        require(not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
                "a candidate escaped into original-only Scanner authentication")


def normalize_value(value: Any) -> Any:
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is bytes:
        return {"kind": "bytes", "hex": value.hex()}
    if type(value) is bytearray:
        return {"kind": "bytearray", "hex": bytes(value).hex()}
    if type(value) is memoryview:
        return {
            "kind": "memoryview", "readonly": value.readonly,
            "format": value.format, "itemsize": value.itemsize,
            "ndim": value.ndim,
            "shape": list(value.shape) if value.shape is not None else None,
            "strides": list(value.strides) if value.strides is not None else None,
            "contiguous": value.contiguous, "hex": value.tobytes().hex(),
        }
    if type(value) in (tuple, list):
        return {
            "kind": "tuple" if type(value) is tuple else "list",
            "items": [normalize_value(item) for item in value],
        }
    if isinstance(value, Mapping):
        return {
            "kind": "mapping",
            "items": [[normalize_value(name), normalize_value(item)]
                      for name, item in sorted(
                          value.items(), key=lambda pair: str(pair[0]),
                      )],
        }
    if hasattr(value, "group") and hasattr(value, "span") and hasattr(value, "re"):
        return normalize_match(value)
    if hasattr(value, "pattern") and hasattr(value, "groups") \
            and hasattr(value, "groupindex") and hasattr(value, "flags"):
        return normalize_pattern(value)
    raise ScannerOracleError(
        "a genuine public Scanner observable was hidden: "
        + type(value).__qualname__,
    )


def normalize_pattern(value: Any) -> dict[str, Any]:
    count = value.groups
    flags = value.flags
    require(type(count) is int and count >= 0 and type(flags) is int,
            "the genuine combined scanner group count or flags was forged")
    return {
        "kind": "compiled-pattern",
        "pattern": normalize_value(value.pattern),
        "flags": flags,
        "groups": count,
        "groupindex": [
            [name, index] for name, index in sorted(dict(value.groupindex).items())
        ],
    }


def normalize_match(value: Any) -> dict[str, Any]:
    expression = value.re
    count = expression.groups
    require(type(count) is int and count >= 0,
            "a genuine callback match concealed its complete group count")
    return {
        "kind": "match",
        "pattern": normalize_pattern(expression),
        "string": normalize_value(value.string),
        "group": normalize_value(value.group(0)),
        "groups": [normalize_value(item) for item in value.groups()],
        "span": list(value.span(0)),
        "spans": [list(value.span(index)) for index in range(count + 1)],
        "groupdict": [
            [name, normalize_value(item)]
            for name, item in sorted(value.groupdict().items())
        ],
        "lastindex": value.lastindex,
        "lastgroup": value.lastgroup,
        "pos": value.pos,
        "endpos": value.endpos,
    }


def normalize_error(error: Exception, engine: Any) -> dict[str, Any]:
    expected = getattr(engine, "error", None)
    if isinstance(expected, type) and isinstance(error, expected):
        return {
            "kind": "public-regex-error",
            "type": type(error).__qualname__,
            "is_engine_error": True,
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


def normalize_warnings(observed: Any) -> list[dict[str, Any]]:
    require(type(observed) is list,
            "the complete genuine warning sequence is mandatory")
    records: list[dict[str, Any]] = []
    for item in observed:
        category = item.category
        message = item.message
        require(isinstance(category, type)
                and isinstance(message, Warning)
                and isinstance(message, category),
                "a genuine Scanner warning category was substituted")
        records.append({
            "category_module": category.__module__,
            "category": category.__qualname__,
            "message": str(message),
        })
    return records


def make_action(
    action: str, branch: int, events: list[dict[str, Any]],
) -> Callable[[Any, Any], Any] | None:
    require(action in ("skip", "identity", "upper", "tuple", "raise"),
            "an unfrozen original Scanner callback was injected")
    if action == "skip":
        return None

    def callback(scanner: Any, token: Any) -> Any:
        combined = scanner.scanner
        actual_match = scanner.match
        events.append({
            "branch": branch,
            "action": action,
            "token": normalize_value(token),
            "match": normalize_match(actual_match),
            "combined_pattern": normalize_pattern(combined),
            "match_uses_combined_pattern": actual_match.re is combined,
        })
        require(len(events) <= 1_024,
                "an actual Scanner callback failed to make forward progress")
        if action == "raise":
            raise ValueError("original scanner callback failure: " + str(branch))
        if action == "upper":
            return token.upper()
        if action == "tuple":
            return (branch, token, actual_match.span())
        return token

    return callback


def execute_case(case: Mapping[str, Any], engine: Any) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    scanner: Any = None
    mutation: dict[str, Any] | None = None
    combined_before: dict[str, Any] | None = None
    lexicon_identity_before: bool | None = None
    lexicon_identity_after: bool | None = None
    with warnings.catch_warnings(record=True) as actual_warnings:
        warnings.simplefilter("always")
        try:
            entries = [
                (
                    decode_subject(entry["phrase"]),
                    make_action(entry["action"], branch, events),
                )
                for branch, entry in enumerate(case["lexicon"])
            ]
            original_lexicon: Any = (
                tuple(entries) if case["lexicon_type"] == "tuple" else entries
            )
            subject = decode_subject(case["subject"])
            scanner = engine.Scanner(original_lexicon, flags=case["flags"])
            lexicon_identity_before = scanner.lexicon is original_lexicon
            combined_before = normalize_pattern(scanner.scanner)
            change = case["mutation"]
            if change == "replace-action":
                phrase = original_lexicon[0][0]
                original_lexicon[0] = (
                    phrase, make_action("tuple", 0, events),
                )
            elif change == "append":
                expression = r"z+" if case["domain"] == "str" else rb"z+"
                original_lexicon.append((
                    expression, make_action("identity", len(original_lexicon), events),
                ))
            elif change == "swap":
                original_lexicon[0], original_lexicon[1] = (
                    original_lexicon[1], original_lexicon[0],
                )
            elif change == "delete":
                original_lexicon.pop(0)
            else:
                require(change == "none", "an unfrozen lexicon mutation was used")
            lexicon_identity_after = scanner.lexicon is original_lexicon
            mutation = {
                "kind": change,
                "lexicon_type": type(original_lexicon).__name__,
                "length_after": len(original_lexicon),
                "identity_before": lexicon_identity_before,
                "identity_after": lexicon_identity_after,
            }
            result = scanner.scan(subject)
            return {
                "status": "return",
                "value": normalize_value(result),
                "callbacks": events,
                "warnings": normalize_warnings(actual_warnings),
                "combined_pattern": combined_before,
                "lexicon": mutation,
            }
        except ScannerOracleError:
            raise
        except Exception as error:
            return {
                "status": "raise",
                "exception": normalize_error(error, engine),
                "callbacks": events,
                "warnings": normalize_warnings(actual_warnings),
                "combined_pattern": combined_before,
                "lexicon": mutation,
            }


def authenticate_owned_module(value: Any, *, label: str) -> str:
    origin = getattr(value, "__file__", None)
    require(type(origin) is str and os.path.isabs(origin)
            and os.path.abspath(origin) == origin
            and os.path.realpath(origin) == origin
            and os.path.commonpath((str(ROOT), origin)) == str(ROOT),
            "the actual owned Scanner " + label + " origin was substituted")
    return origin


def authenticate_native_engine() -> dict[str, Any]:
    expected = str(ROOT / "candidates" / "_rust_engine.so")
    require(os.path.realpath(expected) == expected,
            "the exact actual native Rust engine is not owned")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) \
        | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(expected, flags)
    try:
        info = os.fstat(descriptor)
        require(stat.S_ISREG(info.st_mode)
                and 0 < info.st_size <= MAX_BINARY_BYTES,
                "the actual Rust semantic scanner is not a bounded owned binary")
        hasher = hashlib.sha256()
        remaining = info.st_size
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1_048_576))
            require(type(chunk) is bytes and bool(chunk),
                    "the actual owned semantic Rust scanner was truncated")
            hasher.update(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"",
                "the actual semantic Rust scanner grew while authenticated")
        final_info = os.fstat(descriptor)
        require(final_info.st_dev == info.st_dev
                and final_info.st_ino == info.st_ino
                and final_info.st_size == info.st_size,
                "the authentic native Rust scanner inode changed")
        return {
            "relative": "candidates/_rust_engine.so",
            "sha256": hasher.hexdigest(),
            "bytes": info.st_size,
            "device": info.st_dev,
            "inode": info.st_ino,
        }
    finally:
        os.close(descriptor)


def load_engine(name: str) -> tuple[Any, dict[str, Any] | None]:
    require(name in ("stdlib", "rust"),
            "only an exact original or isolated owned Rust engine may be loaded")
    verify_runtime()
    if name == "stdlib":
        engine = importlib.import_module("re")
        require(engine.__name__ == "re" and type(engine.__file__) is str
                and os.path.abspath(engine.__file__) == str(PINNED_STDLIB_RE)
                and os.path.realpath(engine.__file__) == str(PINNED_STDLIB_RE),
                "the exact pinned CPython Scanner oracle was substituted")
        return engine, None
    native = authenticate_native_engine()
    engine = importlib.import_module("candidates.rust_candidate")
    require(engine.__name__ == "candidates.rust_candidate"
            and authenticate_owned_module(engine, label="Rust adapter")
            == str(ROOT / "candidates" / "rust_candidate.py"),
            "the exact owned Rust Scanner adapter was substituted")
    bridge = sys.modules.get("candidates._rust_bridge")
    require(isinstance(bridge, types.ModuleType)
            and bridge.__name__ == "candidates._rust_bridge",
            "the actual owned Rust native scanner bridge was omitted")
    bridge_origin = authenticate_owned_module(bridge, label="native Rust bridge")
    bridge_spec = getattr(bridge, "__spec__", None)
    bridge_loader = getattr(bridge_spec, "loader", None)
    require(os.path.commonpath((str(ROOT / "candidates"), bridge_origin))
            == str(ROOT / "candidates")
            and any(bridge_origin.endswith(suffix)
                    for suffix in EXTENSION_SUFFIXES)
            and bridge_spec is not None
            and getattr(bridge_spec, "name", None) == "candidates._rust_bridge"
            and getattr(bridge_spec, "origin", None) == bridge_origin
            and isinstance(bridge_loader, ExtensionFileLoader)
            and getattr(bridge_loader, "name", None) == "candidates._rust_bridge"
            and getattr(bridge_loader, "path", None) == bridge_origin,
            "the exact owned compiled Scanner bridge or loader was substituted")
    return engine, native


def observe_worker(role: str, engine_name: str) -> dict[str, Any]:
    matrix = build_matrix()
    validate_matrix(matrix)
    engine, native = load_engine(engine_name)
    records: list[dict[str, Any]] = []
    for case in matrix:
        observed = execute_case(case, engine)
        records.append({
            "case": case["case"], "family": case["family"],
            "outcome": observed,
        })
    require(len(records) == CASE_COUNT,
            "an original Scanner differential observation was silently dropped")
    return {
        "schema": SCHEMA + "-isolated-worker",
        "status": "PASS", "python": "3.14.6",
        "role": role, "engine": engine_name, "pid": os.getpid(),
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
    require(type(role) is str and bool(role)
            and engine in ("stdlib", "rust"),
            "only an explicitly isolated Scanner reference is permitted")
    process = subprocess.Popen(
        [str(PINNED_PYTHON), "-I", "-B", str(ROOT / SOURCE_RELATIVE),
         "--internal-worker", "--engine", engine, "--role", role],
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, cwd=str(ROOT), shell=False,
        env={
            "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
            "LC_ALL": "C", "PATH": "/usr/bin:/bin",
        },
    )
    # An actual timeout samples a clock. The untimed oracle uses no timeout.
    stdout, stderr = process.communicate()
    require(process.returncode == 0 and stderr == b"",
            "an actual isolated Scanner reference failed: " + role
            + "; exit=" + str(process.returncode)
            + "; stderr=" + stderr[-1_200:].decode("utf-8", "replace"))
    document = decode_canonical(stdout, role)
    checks: dict[str, Any] = {
        "schema": SCHEMA + "-isolated-worker",
        "status": "PASS", "python": "3.14.6",
        "role": role, "engine": engine, "pid": process.pid,
        "published_seed": PUBLISHED_SEED,
        "matrix_sha256": MATRIX_SHA256,
        "case_count": CASE_COUNT,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "files_written": 0,
        "benchmark_files_read": 0,
        "hidden_cases_read": 0,
    }
    for name, expected in checks.items():
        require(document.get(name) == expected,
                "an actual complete Scanner reference changed: " + name)
    if engine == "stdlib":
        require(document.get("candidate_import_count") == 0
                and document.get("native_engine") is None,
                "a standard-library Scanner reference imported Rust")
    else:
        require(type(document.get("candidate_import_count")) is int
                and document["candidate_import_count"] > 0
                and type(document.get("native_engine")) is dict,
                "the genuine owned native Rust scanner was not authenticated")
    records = document.get("records")
    matrix = build_matrix()
    require(type(records) is list and len(records) == CASE_COUNT
            and document.get("records_sha256") == digest(records),
            "an original Scanner reference record was omitted or forged")
    for case, record in zip(matrix, records, strict=True):
        require(type(record) is dict
                and set(record) == {"case", "family", "outcome"}
                and record.get("case") == case["case"]
                and record.get("family") == case["family"]
                and type(record.get("outcome")) is dict
                and record["outcome"].get("status") in ("return", "raise")
                and type(record["outcome"].get("callbacks")) is list
                and type(record["outcome"].get("warnings")) is list,
                "a complete source-ordered Scanner outcome was concealed")
    return document


def source_self_test() -> dict[str, Any]:
    verify_runtime()
    matrix = build_matrix()
    validate_matrix(matrix)
    first = run_worker("scanner_original_reference_a", "stdlib")
    second = run_worker("scanner_original_reference_b", "stdlib")
    require(first["pid"] != second["pid"]
            and first["records"] == second["records"]
            and first["records_sha256"] == second["records_sha256"]
            and first["records_sha256"] == BASELINE_SHA256,
            "the two actual complete CPython Scanner references disagree")
    by_family: dict[str, int] = {family: 0 for family in FAMILIES}
    warning_count = 0
    callback_count = 0
    for record in first["records"]:
        by_family[record["family"]] += 1
        warning_count += len(record["outcome"]["warnings"])
        for callback in record["outcome"]["callbacks"]:
            callback_count += 1
            require(callback.get("match_uses_combined_pattern") is True
                    and type(callback.get("match")) is dict
                    and type(callback.get("combined_pattern")) is dict,
                    "the genuine callback combined-pattern identity was hidden")
    require(all(amount == VARIANTS_PER_FAMILY
                for amount in by_family.values()),
            "an entire genuine Scanner family lost its exact denominator")
    require(warning_count > 0 and callback_count > 0,
            "actual scanner warnings or callback behavior were never observed")
    rejected = 0
    for index in range(24):
        omitted = list(matrix)
        omitted.pop(index)
        try:
            validate_matrix(omitted)
        except ScannerOracleError:
            rejected += 1
        else:
            raise ScannerOracleError("an omitted actual Scanner case was accepted")
    for index in range(12):
        forged = list(matrix)
        altered = dict(forged[index])
        altered["family"] = "substituted-foreign-scanner-family"
        forged[index] = altered
        try:
            validate_matrix(forged)
        except ScannerOracleError:
            rejected += 1
        else:
            raise ScannerOracleError("a substituted Scanner case was accepted")
    for invalid in (None, "", "0" * 64, "G" * 64, MATRIX_SHA256.upper()):
        require(not valid_digest(invalid),
                "a forged frozen Scanner digest was accepted")
        rejected += 1
    verify_runtime()
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS", "python": "3.14.6",
        "published_seed": PUBLISHED_SEED,
        "matrix_sha256": MATRIX_SHA256,
        "baseline_records_sha256": BASELINE_SHA256,
        "case_count": CASE_COUNT,
        "family_count": len(FAMILIES),
        "variants_per_family": VARIANTS_PER_FAMILY,
        "actual_reference_workers": 2,
        "actual_candidate_workers": 0,
        "candidate_import_count": 0,
        "observed_warning_count": warning_count,
        "observed_callback_count": callback_count,
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
    baseline = run_worker("scanner_original_candidate_reference", "stdlib")
    require(baseline["records_sha256"] == BASELINE_SHA256,
            "the actual complete pinned Scanner baseline vector changed")
    candidate = run_worker("scanner_owned_native_rust_candidate", "rust")
    require(baseline["pid"] != candidate["pid"],
            "the actual Scanner engines were not independently isolated")
    counts = {family: 0 for family in FAMILIES}
    first: dict[str, Any] | None = None
    mismatch_count = 0
    for case, original, rust in zip(
        matrix, baseline["records"], candidate["records"], strict=True,
    ):
        require(original["case"] == rust["case"] == case["case"]
                and original["family"] == rust["family"] == case["family"],
                "the entire Scanner differential case order was substituted")
        if original["outcome"] != rust["outcome"]:
            mismatch_count += 1
            counts[case["family"]] += 1
            if first is None:
                first = {
                    "case": case["case"], "family": case["family"],
                    "input": case,
                    "baseline_outcome": original["outcome"],
                    "rust_outcome": rust["outcome"],
                }
    return {
        "schema": SCHEMA + "-compact-candidate-result",
        "status": "PASS" if mismatch_count == 0 else "FAIL",
        "python": "3.14.6",
        "published_seed": PUBLISHED_SEED,
        "matrix_sha256": MATRIX_SHA256,
        "baseline_records_sha256": BASELINE_SHA256,
        "candidate_records_sha256": candidate["records_sha256"],
        "case_denominator": CASE_COUNT,
        "actual_baseline_cases": len(baseline["records"]),
        "actual_candidate_cases": len(candidate["records"]),
        "mismatch_count": mismatch_count,
        "mismatches_by_family": counts,
        "first_mismatch": first,
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
            "Independent, deterministic, untimed original Python Scanner oracle"
        ),
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--candidate", action="store_true")
    modes.add_argument("--internal-worker", action="store_true",
                       help=argparse.SUPPRESS)
    parser.add_argument("--engine", choices=("stdlib", "rust"),
                        help=argparse.SUPPRESS)
    parser.add_argument("--role", help=argparse.SUPPRESS)
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    if options.self_test:
        require(options.engine is None and options.role is None,
                "a Scanner source self-test cannot import a candidate")
        result = source_self_test()
    elif options.candidate:
        require(options.engine is None and options.role is None,
                "a Scanner comparison cannot inject a worker role")
        result = run_candidate()
    else:
        require(options.engine in ("stdlib", "rust")
                and type(options.role) is str and bool(options.role),
                "an exact isolated Scanner worker role is mandatory")
        result = observe_worker(options.role, options.engine)
    sys.stdout.buffer.write(canonical(result))
    sys.stdout.buffer.flush()
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ScannerOracleError as error:
        print("independent Scanner differential failed closed: " + str(error),
              file=sys.stderr)
        raise SystemExit(1) from error
