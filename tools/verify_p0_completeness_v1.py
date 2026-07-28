#!/usr/bin/env python3
"""Verify the frozen Phase-1 Python regex crosswalk without running an engine.

The source-only self-test uses exclusively synthetic in-memory documents.
The real verifier is read-only, explicitly hash-pinned, fail-closed, and
rejects a pending reference, undocumented denominator, or unmapped behavior.
Actual V19 evidence is decoded only by its independently frozen V27/V19
producer-owned reference authenticator.
"""

from __future__ import annotations

import builtins
import contextlib
import copy
import gc
import hashlib
import importlib
import io
import json
import math
import os
from pathlib import Path
import stat
import subprocess
import sys
import threading
import time
from typing import Any, Callable, Iterator, Mapping
import zlib


ROOT = Path(os.path.abspath(__file__)).parent.parent
SOURCE_RELATIVE = "tools/verify_p0_completeness_v1.py"
DOCUMENT_RELATIVE = "oracle/phase1/p0-completeness-v1.json"
EXPLANATION_RELATIVE = "oracle/phase1/P0-COMPLETENESS-V1.md"
SCHEMA = "rebar-cpython-re-p0-completeness-v1"
GOAL_SHA256 = (
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
)
PINNED_PYTHON = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
PINNED_RUNTIME_SOURCES: tuple[tuple[str, str], ...] = (
    (
        "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
        "lib/python3.14/re/__init__.py",
        "741a9de729ed8207bfa19db990f8826f1bf3661f33d0970a80c08cd1338ebc35",
    ),
    (
        "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
        "lib/python3.14/re/_compiler.py",
        "d49f30cf9a1dbae33b200ed8befd9d0ce3ac612783a10ac35196536f98923e91",
    ),
    (
        "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
        "lib/python3.14/re/_parser.py",
        "e57bd194a2d42398355ae7c1ccc2ddfb78421dd431eb81e3809dbe8ca9057dc4",
    ),
    (
        "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
        "lib/python3.14/re/_constants.py",
        "42253b3181b81aad6c46392f44a0ab26dcfa31feea411296f43ba16616a1ab0b",
    ),
    (
        "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
        "lib/python3.14/concurrent/interpreters/__init__.py",
        "040e47f07bdfb28c67798fa7764fac1d79e13fd0fc0db9c85ee5dae8e1edf249",
    ),
)
V19_VALIDATOR_RELATIVE = "tools/python_re_public_surface_oracle_stage27.py"
V19_VALIDATOR_SHA256 = (
    "fd0ef1babdb5943d74ef443486805ef6586e46b06eb9d46e4f5b7b650045032b"
)
V19_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-SURFACE-V27.md"
V19_PROTOCOL_SHA256 = (
    "c8cc917b52affbce8d61ae1ad217835c7c890fe1e1369d211475a7aaf443cd3f"
)
MAX_SOURCE_BYTES = 4 * 1024 * 1024
MAX_DOCUMENT_BYTES = 4 * 1024 * 1024
MAX_RECEIPT_BYTES = 4 * 1024 * 1024
MAX_COMPRESSED_BYTES = 32 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 256 * 1024 * 1024
MAX_CAPTURED_REFERENCE_BYTES = 32 * 1024 * 1024
MINIMUM_SYNTHETIC_REJECTIONS = 100
UPSTREAM_ACCOUNTING_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/UPSTREAM-ACCOUNTING-V5.md"
)
UPSTREAM_ACCOUNTING_PROTOCOL_SHA256 = (
    "21e77143bbec1f54faa6fc8a74a842808e32bd36815802a0df3ddfef11c597e1"
)
UPSTREAM_ACCOUNTING_MANIFEST_RELATIVE = (
    "oracle/cpython-3.14.6/manifest-v5.json"
)
UPSTREAM_ACCOUNTING_MANIFEST_SHA256 = (
    "41b598475a6f756bf63dcd71141d602da05ebb7a810525c45b6c07635b78c0d7"
)
UPSTREAM_ACCOUNTING_VERIFIER_RELATIVE = (
    "tools/verify_original_cpython_accounting_v1.py"
)
UPSTREAM_ACCOUNTING_VERIFIER_SHA256 = (
    "f562ab8c998197880590487fa6e78f511db5c01596ab35731185ca8caead454c"
)

INHERITED_OBLIGATIONS = (
    "API-EXPORTS", "API-FLAGS", "API-COMPILE", "API-SEARCH",
    "API-MATCH", "API-FULLMATCH", "API-FINDALL", "API-FINDITER",
    "API-SPLIT", "API-SUB", "API-SUBN", "API-ESCAPE", "API-PATTERN",
    "API-MATCH-OBJECT", "API-SCANNER", "S-LITERAL", "S-DOT-CLASS",
    "S-ANCHOR", "S-QUANTIFIER", "S-POSSESSIVE", "S-ALTERNATION",
    "S-GROUP", "S-BACKREF", "S-CONDITIONAL", "S-LOOKAROUND",
    "S-ATOMIC", "S-INLINE", "S-VERBOSE", "S-UNICODE", "S-ASCII",
    "S-LOCALE", "S-EMPTY", "S-WINDOW", "E-PATTERN", "E-TYPE",
    "E-TEMPLATE", "E-WARNING", "E-DEBUG", "API-GENERIC",
    "API-BYTESLIKE", "API-REPRESENTATION", "API-MATCH-COPY",
    "E-DEPRECATION", "S-LOOKBEHIND-REF", "S-DEEP-FUZZ",
)
ADDITIONAL_OBLIGATIONS = (
    "API-UPSTREAM-ALL-165", "API-UPSTREAM-403-CORPUS",
    "API-UPSTREAM-11-EXTERNAL-ASSERTIONS", "API-MODULE-SCANNER",
    "API-SCANNER-CALLBACK-ORDER", "API-SCANNER-LEXICON-IDENTITY",
    "API-VERBOSE-ESCAPED-COMMENTS", "API-PUBLIC-TYPE-IDENTITY",
    "API-GENERIC-ALIASES", "API-WEAKREF-COPY-ATOMICITY",
    "API-PICKLE-PROTOCOLS-0-5", "API-PUBLIC-CACHE-PURGE",
    "API-PEP688-DIRECT-EXPORTER", "API-PEP688-NESTED-EXPORTER",
    "API-BUFFER-ACQUIRE-RELEASE-ORDER",
    "API-SCANNER-GC-RETAINED-CYCLE", "API-SHAPE-CHANGING-EXPORTER",
    "API-CALLBACK-EXCEPTION-IDENTITY", "API-LOCALE-CROSS-TRANSITION",
    "API-SUBINTERPRETER-ISOLATION", "API-SUBINTERPRETER-TEARDOWN",
    "S-UNICODE-ESCAPED-LONE-SURROGATES",
    "E-EXACT-PATTERN-ATTRIBUTES",
    "E-WARNING-CATEGORY-MESSAGE-LOCATION", "E-64BIT-INDEX-OVERFLOW",
    "E-FIXTURE-VERSUS-USER-EXCEPTION",
    "API-THREAD-SHARED-PATTERN-REENTRANCY",
    "API-MODULE-VERSION-METADATA",
)
PRIVATE_WAIVERS = (
    "DebugTests.test_debug_flag",
    "DebugTests.test_atomic_group",
    "DebugTests.test_possesive_repeat_one",
    "DebugTests.test_possesive_repeat",
    "ImplementationTest.test_immutable",
    "ImplementationTest.test_overlap_table",
    "ImplementationTest.test_signedness",
    "ImplementationTest.test_disallow_instantiation",
    "ImplementationTest.test_deprecated_modules",
    "ImplementationTest.test_case_helpers",
    "ImplementationTest.test_dealloc",
    "ImplementationTest.test_repeat_minmax_overflow_maxrepeat",
    "ImplementationTest.test_sre_template_invalid_group_index",
)
FROZEN_SUITES: dict[str, tuple[int, str | None, str, str | None]] = {
    "original_bounded_v5": (
        151, None,
        "93f0fe07cf6cc0fbe0332b748ca61768f3b966bd5c0fdd81d024520a7deff240",
        "b6f23860b340ff326347bdd103505c04bb2b84c21fc874758bd278bc90390276",
    ),
    "public_v3": (
        864, "5928217332825411633",
        "367d30517874745b11d6facf43685a906784dc94c0246dc6a6381c17afcc776e",
        "0ae84d65f16976e046a267704585306c3968703194d26bbc3c5223b746304f7c",
    ),
    "scanner_v3": (
        1024, "5999710933164053041",
        "83a8ad125b36846c1790ca01564305b2ab9714185f972efa838740b7bbf4b55c",
        "37de08e1991adf28990e35b72c2130ebafa78c72b04750d28550cce08555666d",
    ),
    "buffer_v3": (
        768, "5567953616029762609",
        "b40fb92f42c7019a73eec72800077f262f1a6be516886a6ddda372e24807eb60",
        "8312263785cd49f7283ab8c6fac13443befe9c5a3d739b2e068aebdcf3f59b75",
    ),
    "managed_v1": (
        1024, "5567095966978627121",
        "28ef84b6989542ba8865c98e5296639c780c786078e2a99c7c0a95bfcb4b0976",
        "80293f5332300220f38c3f017d38611a5514b1b686918e692a53491945b196df",
    ),
    "scanner_verbose_v1": (
        2854, "5999725261024810545",
        "01bca287cd481a5e4ae134b910911e2e2f8f1501eebb7ffd2947092ab170d17b",
        "d7e2d499eb4dbe6ae0f8743d8b152e4835898656daa8b3167598636ef7be6012",
    ),
    "public_types_v1": (
        6912, "6077977430793212465",
        "c315e37dfa2e79ab62519ea84c710d4e3ca41d63d34873894bf7415278b56123",
        "0b78702279b7ae2eb8be493bbf04df75719f36c2943f26c9df3e950f32d68e21",
    ),
    "substitution_v2": (
        5120, "6004778603531028017",
        "26f46fe7f1abc5135d1265a7882ccd4a2e2b45cdec80ba293520fda510235b54",
        "2bc65461b9ac60fd19a3c66856bd33ee48db038ab6a5de62193837800840f61b",
    ),
    "shape_v2": (
        10240, "6001118316486346290",
        "10fe3e3fd4b4650bff1da6a745b5b883f01033ed14df3f9795aa2f7a30c6d8d8",
        "58bbc78828ba2d4cde6b99cbebea815ce9381cda24d0acec03f6cc095b8b643c",
    ),
    "public_surface_v19": (
        1376, "2026072483",
        "7885a9ac0b2e22db88db7dc4ab9c33c4ba229ddb6d15fcdd4bfe9b0d6f10e8aa",
        "c002fc9e82bb73e592ffa3b5ba73731070004eb892cf85cfcf288fe7693b0aef",
    ),
    "subinterpreter_v2": (
        128, "2026072501",
        "edda77658c5eef9746c6d4769734c69e40db4c9d986171fa63799093f4cb62d3",
        "450fccc859099ca78aec725911b6195695cd932ad281af931ca7945cec8c51e8",
    ),
    "pep688_v4": (
        264, None,
        "2d9eb4e637387bc89020d2f883f59ff03dd98cbebd2f2aaa2a30dc55d0836891",
        "7827586e0c7d4f43ac1fbd288f6b28f6a44b810b46274830d3803505c76692a8",
    ),
}
FROZEN_SOURCE_PINS: dict[str, tuple[str, str]] = {
    "original_bounded_v5": (
        "tools/independent_original_cpython_suite_v5.py",
        "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce",
    ),
    "public_v3": (
        "tools/rust_public_practice_benchmark_v1.py",
        "d74932c13bdda64e1340c958cbea48d65db36531b849e202dfc16170de150b37",
    ),
    "scanner_v3": (
        "tools/rust_scanner_differential_v1.py",
        "fcc82a76e7bcaaa25d92a8482d4dc611b643d887d7fd983db0906c7340b91fd7",
    ),
    "buffer_v3": (
        "tools/rust_memoryview_expand_differential_v1.py",
        "226f129f0e90b060c977e599e6e8369f5a5285890089c69108b718cfcb2980e6",
    ),
    "managed_v1": (
        "tools/independent_managed_buffer_lifetime_v1.py",
        "cedbab1227ea58a97d407cb339d2959a9f9be58a2085ce3106b65bb3385de489",
    ),
    "scanner_verbose_v1": (
        "tools/independent_scanner_verbose_comments_v1.py",
        "5508910eae3f5e59d2013bc9fa4f1a8948a823e27de09bf416de2fffc8e91c9d",
    ),
    "public_types_v1": (
        "tools/independent_public_type_identity_serialization_v1.py",
        "7ce0606da0d830ef8e9cf9b8e9b952a9836bf705254a23a65551832bf1d92e20",
    ),
    "substitution_v2": (
        "tools/independent_substitution_buffer_semantics_v2.py",
        "e7cc951b4fbb90b2826c3730bbb3b3e81b50e8a5eac8a3d758962358d9414573",
    ),
    "shape_v2": (
        "tools/independent_shape_changing_buffer_semantics_v2.py",
        "0262807f793a818307f2c8c6ecfd84bf970264a6ef5d656acf30c9d3606f0e2c",
    ),
    "public_surface_v19": (
        "tools/python_re_public_surface_oracle_stage19.py",
        "fda386f3c00be660a41e92d8005fc287706d9dc050967cf2b708cb6f8aba113e",
    ),
    "subinterpreter_v2": (
        "tools/python_re_subinterpreter_oracle_v2.py",
        "54735efb77a099feb2dd076723d3a93d81415226b9b9213307c32cc0f38c52c8",
    ),
    "pep688_v4": (
        "tools/python_re_buffer_exporter_oracle_v4.py",
        "8da0b8e5c5519e7335cd1b53ceb7042f1da1f902c486ad8ac35ddf53d8a04490",
    ),
}
PURE_CORE_RECORDER_RELATIVE = (
    "tools/record_independent_public_contract_baselines_v1.py"
)
PURE_CORE_RECORDER_SHA256 = (
    "7ede1a1c81d624664561f89bcc7214ae7232cb742b9a4ebd4628d3d4914c7135"
)
PURE_CORE_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/PUBLIC-CONTRACT-BASELINES-V1.md"
)
PURE_CORE_PROTOCOL_SHA256 = (
    "f3b9094f03067c0afe818f85f2c9e7c6b8764db0e84e0a896ba0063258859cf0"
)
THREADED_SOURCE_RELATIVE = "tools/python_re_threaded_pattern_oracle_v1.py"
THREADED_SOURCE_SHA256 = (
    "05226e59736d8721a975eda8afa10247213999690c2766a7b3235c567b9f8276"
)
THREADED_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/PUBLIC-THREADED-PATTERN-V1.md"
)
THREADED_PROTOCOL_SHA256 = (
    "df0a6ef32b805f8ccac6c98c505eec7e5aadc13efcad66ee1f5daf86cc823aaf"
)
THREADED_MATRIX_SHA256 = (
    "a7d467e3e529204946fe00ddb819e734421e7087ea909af9ec24b757e42afa0b"
)
THREADED_CASE_COUNT = 512
THREADED_METADATA_CASE_COUNT = 32
THREADED_PUBLISHED_SEED = "2026072701"
FROZEN_RECORDER_PINS: dict[str, tuple[str, str]] = {
    "original_bounded_v5": (
        "tools/record_independent_original_cpython_v5.py",
        "72f5717b5e5909f5d6e521b83018797bf1abab8392c70fd95ef26d64a039c367",
    ),
    "public_v3": (PURE_CORE_RECORDER_RELATIVE, PURE_CORE_RECORDER_SHA256),
    "scanner_v3": (PURE_CORE_RECORDER_RELATIVE, PURE_CORE_RECORDER_SHA256),
    "buffer_v3": (PURE_CORE_RECORDER_RELATIVE, PURE_CORE_RECORDER_SHA256),
    "managed_v1": (
        "tools/record_independent_managed_buffer_lifetime_v1.py",
        "dddc90f3b6449deeb31098d062af9077e3bea558645b3f2d71de2cd4e6488abd",
    ),
    "scanner_verbose_v1": (
        "tools/record_independent_scanner_verbose_comments_v1.py",
        "d75934bef992e01ad5c1131a8abef997d3b540f8b150518822ad7e55c39c9191",
    ),
    "public_types_v1": (
        "tools/record_independent_public_type_identity_serialization_v1.py",
        "ee3e6fc00991758fee93b710a63dad9094f881f1ea57777cae2415397f752eae",
    ),
    "substitution_v2": (
        "tools/record_independent_substitution_buffer_semantics_v3.py",
        "1e6bd77cea22c511ca3ee0ccdd4c02b12b4aa22c4fb79cb0df74d2894280807c",
    ),
    "shape_v2": (
        "tools/record_independent_shape_changing_buffer_semantics_v2.py",
        "0ddcb154378807ce6d3b8c5726f37e72ed9fcf921fe348d7640e1a6f1a898cc9",
    ),
}
MANAGED_ARCHIVE_INDEX_RELATIVE = (
    "docs/evidence/managed-buffer-lifetime-baseline-v1.archive.json"
)
MANAGED_ARCHIVE_INDEX_SHA256 = (
    "514a22347d62340cf6a122ff14415cf6acbac8fc16039f25109911b840680c69"
)
MANAGED_RESTORER_RELATIVE = (
    "tools/restore_managed_buffer_lifetime_baseline_v1.py"
)
MANAGED_RESTORER_SHA256 = (
    "775247b55a494b8bbe3a0c4cb42bc443f586a35fb7f3420c861498d207fa2b0d"
)
LEGACY_RECEIPT_SCHEMAS: dict[str, str] = {
    "scanner_verbose_v1": (
        "rebar-independent-scanner-verbose-comments-recorder-v1-"
        "durable-baseline-publication-receipt"
    ),
    "public_types_v1": (
        "rebar-independent-public-type-identity-serialization-recorder-v1-"
        "durable-baseline-publication-receipt"
    ),
    "substitution_v2": (
        "rebar-independent-substitution-buffer-semantics-recorder-v3-"
        "durable-baseline-publication-receipt"
    ),
    "shape_v2": (
        "rebar-independent-shape-changing-buffer-semantics-recorder-v2-"
        "durable-baseline-publication-receipt"
    ),
}


class CompletenessError(Exception):
    """The independently frozen compatibility gate must fail closed."""


class SyntheticEffectError(CompletenessError):
    """A forbidden real-world effect escaped a source-only control."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise CompletenessError(message)


def canonical(value: Any) -> bytes:
    try:
        return (
            json.dumps(
                value, ensure_ascii=True, allow_nan=False,
                sort_keys=True, separators=(",", ":"),
            ).encode("ascii") + b"\n"
        )
    except (TypeError, ValueError, UnicodeError) as error:
        raise CompletenessError("noncanonical completeness evidence") from error


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    actual: dict[str, Any] = {}
    for name, value in pairs:
        require(type(name) is str and name not in actual,
                "duplicate completeness evidence keys are forbidden")
        actual[name] = value
    return actual


def decode_complete_json(raw: bytes, label: str) -> dict[str, Any]:
    """Decode genuine, hash-pinned JSON without inventing compact formatting."""
    require(type(raw) is bytes and 0 < len(raw) <= MAX_UNCOMPRESSED_BYTES,
            "complete bounded JSON evidence is required: " + label)
    try:
        result = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_unique_pairs,
            parse_constant=lambda value: (_ for _ in ()).throw(
                CompletenessError("a nonfinite JSON value was hidden: " + value),
            ),
        )
    except (ValueError, UnicodeError, json.JSONDecodeError) as error:
        raise CompletenessError(
            "invalid complete unique-key JSON evidence: " + label,
        ) from error
    require(type(result) is dict,
            "a complete JSON evidence object is required: " + label)
    return result


def decode_canonical(raw: bytes, label: str) -> dict[str, Any]:
    result = decode_complete_json(raw, label)
    require(type(result) is dict and canonical(result) == raw,
            "incomplete, reordered, or noncanonical evidence: " + label)
    return result


def valid_sha256(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(letter in "0123456789abcdef" for letter in value),
            "an exact independently frozen SHA-256 is required: " + label)
    return value


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1
            and sys.dont_write_bytecode is True
            and os.path.abspath(sys.executable) == PINNED_PYTHON
            and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE)
            and bool(sys.path) and sys.path[0] == str(ROOT),
            "use only isolated pinned no-bytecode CPython 3.14.6")
    require(not any(
        name == "candidates" or name.startswith("candidates.")
        for name in sys.modules
    ), "a completeness verifier may never import a candidate")


def safe_relative(relative: Any, allowed: frozenset[str]) -> tuple[str, ...]:
    require(type(relative) is str and relative in allowed,
            "an evidence path was not explicitly pinned in the manifest")
    require("\\" not in relative and "\x00" not in relative
            and not relative.startswith("/"),
            "an evidence path escaped the literal repository root")
    parts = tuple(relative.split("/"))
    require(bool(parts) and all(part not in ("", ".", "..") for part in parts),
            "a completeness path was noncanonical")
    require("performance" not in parts and "candidates" not in parts
            and "holdout" not in parts and "hidden" not in parts,
            "candidate, performance, holdout, and hidden paths are forbidden")
    return parts


@contextlib.contextmanager
def owned_descriptor(
    relative: str, allowed: frozenset[str], maximum: int,
) -> Iterator[tuple[int, os.stat_result]]:
    parts = safe_relative(relative, allowed)
    require(type(maximum) is int and 0 < maximum <= MAX_UNCOMPRESSED_BYTES,
            "a bounded authenticated regular file is mandatory")
    flags = (
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    directory_flags = flags | getattr(os, "O_DIRECTORY", 0)
    opened: list[int] = []
    try:
        current = os.open(str(ROOT), directory_flags)
        opened.append(current)
        require(stat.S_ISDIR(os.fstat(current).st_mode),
                "the literal repository root is not an owned directory")
        for component in parts[:-1]:
            following = os.open(component, directory_flags, dir_fd=current)
            opened.append(following)
            require(stat.S_ISDIR(os.fstat(following).st_mode),
                    "an evidence parent was replaced or symlinked")
            current = following
        descriptor = os.open(parts[-1], flags, dir_fd=current)
        opened.append(descriptor)
        first = os.fstat(descriptor)
        named = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        require(stat.S_ISREG(first.st_mode) and stat.S_ISREG(named.st_mode)
                and (first.st_dev, first.st_ino)
                == (named.st_dev, named.st_ino)
                and 0 < first.st_size <= maximum,
                "evidence must be the exact bounded no-follow regular inode")
        yield descriptor, first
        final = os.fstat(descriptor)
        named_final = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        require(
            (first.st_dev, first.st_ino, first.st_size)
            == (final.st_dev, final.st_ino, final.st_size)
            == (named_final.st_dev, named_final.st_ino, named_final.st_size),
            "a frozen owned evidence inode changed during verification",
        )
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def read_owned(
    relative: str, expected: str, maximum: int,
    allowed: frozenset[str],
) -> bytes:
    valid_sha256(expected, relative)
    with owned_descriptor(relative, allowed, maximum) as (descriptor, info):
        remaining = info.st_size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1_048_576))
            require(type(chunk) is bytes and bool(chunk),
                    "an authenticated original evidence file was truncated")
            chunks.append(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"",
                "an authenticated original file gained a hidden suffix")
    result = b"".join(chunks)
    require(hashlib.sha256(result).hexdigest() == expected,
            "an actual independently pinned evidence fingerprint changed")
    return result


def validate_artifact(value: Any, *, nullable: bool = False) -> dict[str, Any] | None:
    if value is None and nullable:
        return None
    require(type(value) is dict and set(value) >= {"path", "sha256"},
            "an actual pinned artifact path and hash are required")
    require(type(value["path"]) is str and bool(value["path"]),
            "an independently frozen artifact path is required")
    valid_sha256(value["sha256"], value["path"])
    return value


def _validate_case_results(results: Any, label: str) -> None:
    require(type(results) is dict
            and set(results) == {"c", "rust", "zig"}
            and all(value == "NOT MEASURED" for value in results.values()),
            "a Phase-1 candidate result was forged: " + label)


def _validate_original(original: Any) -> None:
    require(type(original) is dict
            and original.get("source_method_count") == 165
            and original.get("public_method_count") == 152
            and original.get("runnable_public_method_count") == 151
            and original.get("private_waiver_count") == len(PRIVATE_WAIVERS),
            "the original 165-method public/private denominator changed")
    for field, relative, fingerprint in (
        (
            "accounting_protocol",
            UPSTREAM_ACCOUNTING_PROTOCOL_RELATIVE,
            UPSTREAM_ACCOUNTING_PROTOCOL_SHA256,
        ),
        (
            "accounting_manifest",
            UPSTREAM_ACCOUNTING_MANIFEST_RELATIVE,
            UPSTREAM_ACCOUNTING_MANIFEST_SHA256,
        ),
        (
            "accounting_verifier",
            UPSTREAM_ACCOUNTING_VERIFIER_RELATIVE,
            UPSTREAM_ACCOUNTING_VERIFIER_SHA256,
        ),
    ):
        actual = validate_artifact(original.get(field))
        require(actual is not None and actual["path"] == relative
                and actual["sha256"] == fingerprint,
                "an actual complete upstream accounting artifact changed")
    waivers = original.get("private_waivers")
    require(type(waivers) is list
            and tuple(item.get("method") for item in waivers)
            == PRIVATE_WAIVERS,
            "a named private waiver was omitted, invented, or reordered")
    skipped = original.get("public_debug_skip")
    require(type(skipped) is dict
            and skipped.get("method") == "ReTests.test_memory_leaks"
            and skipped.get("source_order_index") == 138
            and skipped.get("row_sha256")
            == "840264aaf4bf27c06d29ac78664767327a8f4b90008c5db994c88542c692b389"
            and skipped.get("private_waiver") is False
            and skipped.get("counted_as_runnable_case") is False,
            "the actual public debug-only skip was changed or privately waived")
    require(original.get("original_method_matrix_sha256")
            == FROZEN_SUITES["original_bounded_v5"][2]
            and original.get("original_record_vector_sha256")
            == FROZEN_SUITES["original_bounded_v5"][3],
            "the complete source-ordered original public vector was changed")
    corpus = original.get("external_corpus")
    require(type(corpus) is dict and corpus.get("case_count") == 403
            and corpus.get("literal_case_count") == 400
            and corpus.get("extended_case_count") == 3
            and corpus.get("succeed_count") == 289
            and corpus.get("fail_count") == 74
            and corpus.get("syntax_error_count") == 40
            and corpus.get("external_pattern_fixture_count") == 11
            and corpus.get("performance") == "NOT MEASURED",
            "the complete 403-case upstream correctness corpus was forged")
    lineages = original.get("lineages")
    require(type(lineages) is list
            and {row.get("id") for row in lineages}
            == {"original_full_v5", "original_full_v6",
                "original_bounded_v5"},
            "the three distinct original-suite lineages were conflated")
    by_id = {row["id"]: row for row in lineages}
    full = by_id["original_full_v5"]
    require(full.get("requested_and_delivered_big_memory_bytes") == 2**31
            and full.get("actual_max_memory_bytes") == 42_949_672_960
            and full.get("big_memory_dry_run") is False
            and full.get("candidate_big_memory_status") == "NOT MEASURED"
            and full.get("distinct_reference_process_ids") == "NOT CAPTURED",
            "the genuine full 2-GiB Python reference was misrepresented")
    require(by_id["original_full_v6"].get("full_resource_parent")
            == "original_full_v5"
            and by_id["original_full_v6"].get(
                "distinct_reference_process_ids",
            ) == "NOT CAPTURED",
            "the independent full-resource V6 parent was substituted")
    bounded = by_id["original_bounded_v5"]
    require(bounded.get("big_memory_dry_run") is True
            and bounded.get("big_memory_maximum_bytes") == 5_147,
            "the bounded original run was represented as a 2-GiB allocation")


def _validate_suites(document: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    rows = document.get("suites")
    require(type(rows) is list and len(rows) == len(FROZEN_SUITES) + 1,
            "an independent compatibility suite was removed or duplicated")
    result: dict[str, dict[str, Any]] = {}
    for item in rows:
        require(type(item) is dict and type(item.get("id")) is str
                and item["id"] not in result,
                "a frozen compatibility suite was omitted or duplicated")
        result[item["id"]] = item
        _validate_case_results(item.get("candidate_results"), item["id"])
        require(item.get("performance") == "NOT MEASURED",
                "timing evidence cannot qualify a Phase-1 correctness suite")
    require(set(result) == {*FROZEN_SUITES, "threaded_pattern_v1"},
            "the exact independent suite identities changed")
    for name, (count, seed, matrix, records) in FROZEN_SUITES.items():
        actual = result[name]
        require(type(actual.get("case_execution_count")) is int
                and actual["case_execution_count"] == count
                and actual.get("published_seed_decimal") == seed
                and actual.get("matrix_sha256") == matrix,
                "a complete original case count, matrix, or seed changed: " + name)
        if records is not None:
            require(actual.get("baseline_records_sha256") == records,
                    "an original Python reference vector changed: " + name)
        source = validate_artifact(actual.get("source"))
        require(source is not None
                and (source["path"], source["sha256"])
                == FROZEN_SOURCE_PINS[name],
                "an independently frozen category source was substituted: " + name)
        recorder = validate_artifact(actual.get("recorder"), nullable=True)
        expected_recorder = FROZEN_RECORDER_PINS.get(name)
        require(
            (recorder is None and expected_recorder is None)
            or (recorder is not None and expected_recorder is not None
                and (recorder["path"], recorder["sha256"]) == expected_recorder),
            "an independently frozen category recorder was substituted: " + name,
        )
        if name in ("public_v3", "scanner_v3", "buffer_v3"):
            protocol = validate_artifact(actual.get("protocol"))
            require(protocol is not None
                    and protocol["path"] == PURE_CORE_PROTOCOL_RELATIVE
                    and protocol["sha256"] == PURE_CORE_PROTOCOL_SHA256,
                    "the pure two-reference contract protocol was substituted")
        baseline = actual.get("baseline")
        require(type(baseline) is dict,
                "a separately recorded Python baseline is mandatory: " + name)
        require(baseline.get("candidate_process_count") == 0
                and baseline.get("hidden_cases_read") == 0
                and baseline.get("timing_trials_run") == 0,
                "a pure correctness baseline started a candidate or timer: " + name)
    pep = result["pep688_v4"]
    require(pep.get("published_seed_decimal") is None
            and pep.get("public_operation_count") == 19
            and pep.get("carrier_count") == 4,
            "the actual seed-free 264-case PEP 688 matrix was changed")
    pep_protocol = validate_artifact(pep.get("protocol"))
    require(
        pep_protocol is not None
        and pep_protocol["path"]
        == "oracle/cpython-3.14.6/PUBLIC-BUFFER-EXPORTER-V4.md"
        and pep_protocol["sha256"]
        == "7f7a4a274c7b59e8f0148f2eae25c5a577fea8886dedbdff27b2fa66fe742905",
        "the independently frozen PEP 688 V4 protocol was substituted",
    )
    threaded = result["threaded_pattern_v1"]
    threaded_source = validate_artifact(threaded.get("source"))
    threaded_protocol = validate_artifact(threaded.get("protocol"))
    require(
        threaded_source is not None
        and threaded_source["path"] == THREADED_SOURCE_RELATIVE
        and threaded_source["sha256"] == THREADED_SOURCE_SHA256
        and threaded_protocol is not None
        and threaded_protocol["path"] == THREADED_PROTOCOL_RELATIVE
        and threaded_protocol["sha256"] == THREADED_PROTOCOL_SHA256
        and threaded.get("case_execution_count") == THREADED_CASE_COUNT
        and threaded.get("published_seed_decimal") == THREADED_PUBLISHED_SEED
        and threaded.get("matrix_sha256") == THREADED_MATRIX_SHA256
        and threaded.get("metadata_overlap_case_count")
        == THREADED_METADATA_CASE_COUNT,
        "the genuine frozen shared-thread and overlapping metadata source changed",
    )
    version = threaded.get("version_metadata")
    require(type(version) is dict
            and version.get("attribute") == "__version__"
            and version.get("type") == "str"
            and version.get("value") == "2.2.1"
            and version.get("candidate_module_name_asserted") is False,
            "Python version metadata or the public import alias was falsified")
    broad = result["public_surface_v19"]
    require(broad.get("full_resource_parent") == "original_full_v5"
            and broad.get("real_locale_case_count") == 64
            and broad.get("locale_transition_count") == 192
            and broad["baseline"].get("reference_role_count") == 2
            and broad["baseline"].get("distinct_reference_process_ids")
            == "NOT CAPTURED",
            "broad V19 provenance, true locale cases, or unrecorded PIDs changed")
    real_interpreters = result["subinterpreter_v2"]["baseline"]
    require(real_interpreters.get("reference_process_ids") == [81, 82]
            and real_interpreters.get("actual_interpreters_created") == 22
            and real_interpreters.get("actual_interpreters_closed") == 22
            and real_interpreters.get("actual_regex_match_operations") == 788
            and real_interpreters.get("actual_case_triples") == 256
            and real_interpreters.get("actual_phase_records") == 768,
            "genuine concurrently isolated Python-interpreter evidence changed")
    return result


def _validate_obligations(
    obligations: Any, suite_ids: frozenset[str],
) -> None:
    require(type(obligations) is dict
            and obligations.get("inherited_count") == len(INHERITED_OBLIGATIONS)
            and obligations.get("additional_named_count")
            == len(ADDITIONAL_OBLIGATIONS)
            and type(obligations.get("crosswalk_count")) is int
            and obligations["crosswalk_count"] >= 34,
            "an independently frozen public-obligation denominator changed")
    for key, expected in (
        ("inherited", INHERITED_OBLIGATIONS),
        ("additional", ADDITIONAL_OBLIGATIONS),
    ):
        rows = obligations.get(key)
        require(type(rows) is list and len(rows) == len(expected)
                and tuple(row.get("id") for row in rows) == expected,
                "an inherited or discovered public obligation was omitted: " + key)
        for row in rows:
            coverage = row.get("covered_by")
            require(type(coverage) is list and bool(coverage)
                    and len(coverage) == len(set(coverage))
                    and set(coverage).issubset(suite_ids),
                    "a public obligation has no exact independent case mapping")
    crosswalk = obligations.get("crosswalk")
    require(type(crosswalk) is list
            and len(crosswalk) == obligations["crosswalk_count"],
            "a complete original many-to-one obligation map is mandatory")
    found: set[str] = set()
    valid = set(suite_ids) | {"original_full_v5", "original_full_v6"}
    for row in crosswalk:
        require(type(row) is dict and type(row.get("id")) is str
                and row["id"].startswith("P0-") and row["id"] not in found
                and type(row.get("description")) is str
                and bool(row["description"]),
                "a stable public completeness obligation was substituted")
        found.add(row["id"])
        coverage = row.get("covered_by")
        require(type(coverage) is list and bool(coverage)
                and len(coverage) == len(set(coverage))
                and set(coverage).issubset(valid),
                "a complete public crosswalk edge was omitted")


def validate_document(
    document: Mapping[str, Any], *, require_ready: bool,
) -> dict[str, dict[str, Any]]:
    fields = {
        "schema", "version", "goal", "runtime",
        "predecessor_obligation_matrices", "original_upstream",
        "denominator", "suites", "obligations", "historical_evidence",
        "candidate_results", "audit_boundaries", "phase_gate",
    }
    require(type(document) is dict and set(document) == fields
            and document.get("schema") == SCHEMA
            and document.get("version") == 1,
            "the complete independently frozen Phase-1 schema changed")
    goal = document.get("goal")
    require(type(goal) is dict and goal.get("path") == "GOAL.md"
            and goal.get("sha256") == GOAL_SHA256,
            "the immutable user objective was changed or detached")
    runtime = document.get("runtime")
    require(type(runtime) is dict and runtime.get("python_version") == "3.14.6"
            and runtime.get("python_implementation") == "CPython",
            "the pinned CPython correctness baseline was substituted")
    executable = validate_artifact(runtime.get("executable"))
    require(executable is not None
            and executable["path"] == PINNED_PYTHON
            and executable["sha256"] == PINNED_PYTHON_SHA256,
            "the exact stable CPython executable was substituted")
    runtime_sources = runtime.get("stdlib_sources")
    require(
        type(runtime_sources) is list
        and len(runtime_sources) == len(PINNED_RUNTIME_SOURCES)
        and tuple(
            (item.get("path"), item.get("sha256"))
            for item in runtime_sources if type(item) is dict
        ) == PINNED_RUNTIME_SOURCES,
        "a pinned original CPython regex or interpreter source changed",
    )
    predecessors = document.get("predecessor_obligation_matrices")
    require(type(predecessors) is list and len(predecessors) == 2
            and predecessors[0].get("path") == "oracle/v1/P0.md"
            and predecessors[0].get("sha256")
            == "30dc3dd121c8e2d7a080884923109164b4bbdf37103f56c2bac84727acbd4424"
            and predecessors[0].get("obligation_count") == 38
            and predecessors[1].get("path") == "oracle/v2/P0.md"
            and predecessors[1].get("sha256")
            == "50fe34edd81ae22f3a2b8fb836a615fe625dc2b7c32ce0f045275554bf3b9e44"
            and predecessors[1].get("obligation_count") == 45
            and predecessors[1].get("includes_entire_version_1") is True,
            "the complete immutable 38-to-45 obligation ancestry changed")
    _validate_original(document.get("original_upstream"))
    suites = _validate_suites(document)
    _validate_obligations(document.get("obligations"), frozenset(suites))
    _validate_case_results(document.get("candidate_results"), "global")
    guards = document.get("audit_boundaries")
    require(type(guards) is dict
            and guards.get("candidate_processes_started") == 0
            and guards.get("reference_processes_started_by_ledger") == 0
            and guards.get("timing_trials_run") == 0
            and guards.get("clock_samples") == 0
            and guards.get("hidden_cases_read") == 0
            and guards.get("final_cases_read") == 0
            and guards.get("external_regex_packages_used") == 0
            and guards.get("performance") == "NOT MEASURED"
            and guards.get("native_memory") == "NOT MEASURED"
            and guards.get("candidate_qualified") is False
            and guards.get("winner_selected") is False,
            "correctness verification ran hidden, timed, or candidate work")
    denominator = document.get("denominator")
    observed_case_execution_count = sum(
        item["case_execution_count"] for item in suites.values()
    )
    require(type(denominator) is dict
            and observed_case_execution_count == 31_237
            and denominator.get("available_frozen_vector_case_executions")
            == observed_case_execution_count
            and denominator.get("frozen_planned_case_execution_denominator")
            == observed_case_execution_count
            and denominator.get(
                "known_minimum_if_frozen_264_case_pep688_baseline_passes",
            ) == 30_725
            and denominator.get("pep688_case_executions_awaiting_two_reference_baseline")
            == 0
            and denominator.get("threaded_pattern_case_execution_count")
            == THREADED_CASE_COUNT
            and denominator.get("public_original_skip_cases_outside_runnable_denominator")
            == 1
            and denominator.get("private_upstream_methods_outside_public_denominator")
            == 13
            and denominator.get("historical_subinterpreter_versions_double_counted")
            is False
            and denominator.get("full_resource_original_versions_double_counted")
            is False
            and denominator.get("not_semantically_deduplicated") is True
            and denominator.get("counted_suite_ids") == list(suites),
            "a public case denominator was omitted, inflated, or double-counted")
    phase = document.get("phase_gate")
    require(type(phase) is dict
            and phase.get("phase") == "CORRECTNESS ORACLE"
            and phase.get("all_obligations_mapped") is True
            and phase.get("candidate_evaluation_authorized") is False
            and phase.get("final_holdout_authorized") is False,
            "an unopened candidate or final test was silently authorized")
    if require_ready:
        require(phase.get("status") == "PASS"
                and phase.get("all_obligations_mapped") is True
                and phase.get("blockers") == [],
                "BLOCKED: publish every independently frozen pure reference")
        threaded = suites["threaded_pattern_v1"]
        require(type(threaded.get("case_execution_count")) is int
                and threaded["case_execution_count"] > 0
                and type(threaded.get("published_seed_decimal")) is str
                and threaded["published_seed_decimal"].isdecimal(),
                "BLOCKED: actual threaded reference matrix has not been frozen")
        valid_sha256(threaded.get("matrix_sha256"),
                     "actual threaded public-pattern matrix")
        valid_sha256(threaded.get("baseline_records_sha256"),
                     "actual threaded two-reference vector")
        valid_sha256(suites["pep688_v4"].get("baseline_records_sha256"),
                     "actual zero-candidate PEP 688 reference vector")
        require(denominator.get("threaded_pattern_case_execution_count")
                == threaded["case_execution_count"]
                and denominator.get("final_required_case_execution_denominator")
                == observed_case_execution_count,
                "BLOCKED: the final independently observed denominator is unknown")
        for name, item in suites.items():
            baseline = item["baseline"]
            require(baseline.get("status") == "PASS",
                    "BLOCKED: an actual Python reference is not passing: " + name)
            if name not in ("original_bounded_v5", "public_surface_v19"):
                validate_artifact(baseline.get("publication_receipt"))
        for key in ("inherited", "additional", "crosswalk"):
            require(all(row.get("status") not in {
                "FROZEN_SOURCE_AND_PYTHON_BASELINE_PENDING", "PENDING",
            } for row in document["obligations"][key]),
                    "BLOCKED: an actual public compatibility obligation is pending")
    else:
        require(phase.get("status") == "NOT COMPLETE"
                and type(phase.get("blockers")) is list
                and bool(phase["blockers"])
                and denominator.get("final_required_case_execution_denominator")
                == "NOT ESTABLISHED",
                "a pending public obligation was falsely marked complete")
    return suites


def verify_gzip(
    compressed: bytes, *, expected_sha256: str, expected_bytes: int,
    capture_plain: bool = False,
) -> dict[str, Any]:
    require(type(compressed) is bytes
            and 10 <= len(compressed) <= MAX_COMPRESSED_BYTES
            and compressed[:3] == b"\x1f\x8b\x08"
            and compressed[3] == 0
            and int.from_bytes(compressed[4:8], "little") == 0,
            "a complete single deterministic mtime-zero gzip is required")
    valid_sha256(expected_sha256, "complete uncompressed evidence")
    require(type(expected_bytes) is int
            and 0 < expected_bytes <= MAX_UNCOMPRESSED_BYTES,
            "a frozen exact original uncompressed size is required")
    decoder = zlib.decompressobj(wbits=16 + zlib.MAX_WBITS)
    digest = hashlib.sha256()
    total = 0
    cursor = 0
    captured: list[bytes] = []
    require(type(capture_plain) is bool
            and (
                not capture_plain
                or expected_bytes <= MAX_CAPTURED_REFERENCE_BYTES
            ),
            "refusing to retain an unbounded decompressed evidence document")
    while cursor < len(compressed):
        chunk = compressed[cursor:cursor + 65_536]
        cursor += len(chunk)
        try:
            output = decoder.decompress(
                chunk, min(1_048_576, expected_bytes + 1 - total),
            )
        except zlib.error as error:
            raise CompletenessError("a signed gzip member is malformed") from error
        while decoder.unconsumed_tail:
            total += len(output)
            digest.update(output)
            if capture_plain:
                captured.append(output)
            require(total <= expected_bytes,
                    "a signed gzip exceeded its complete original denominator")
            try:
                output = decoder.decompress(
                    decoder.unconsumed_tail,
                    min(1_048_576, expected_bytes + 1 - total),
                )
            except zlib.error as error:
                raise CompletenessError("a signed gzip stream was truncated") from error
        total += len(output)
        digest.update(output)
        if capture_plain:
            captured.append(output)
        require(total <= expected_bytes,
                "a signed gzip concealed extra original evidence bytes")
        require(not decoder.unused_data,
                "extra or concatenated gzip members are forbidden")
    try:
        tail = decoder.flush()
    except zlib.error as error:
        raise CompletenessError("a signed gzip trailer is invalid") from error
    total += len(tail)
    digest.update(tail)
    if capture_plain:
        captured.append(tail)
    require(decoder.eof and not decoder.unused_data
            and not decoder.unconsumed_tail
            and total == expected_bytes
            and digest.hexdigest() == expected_sha256,
            "the complete original gzip records, CRC, length, or hash changed")
    result: dict[str, Any] = {
        "bytes": total, "sha256": digest.hexdigest(), "complete": True,
    }
    if capture_plain:
        result["plain"] = b"".join(captured)
    return result


@contextlib.contextmanager
def source_only_boundary() -> Iterator[dict[str, int]]:
    effects = {
        "actual_file_reads": 0, "actual_file_writes": 0,
        "actual_candidate_imports": 0, "actual_reference_imports": 0,
        "actual_workers_started": 0, "actual_threads_started": 0,
        "actual_clock_samples": 0, "actual_garbage_collections": 0,
        "hidden_cases_read": 0, "performance_files_read": 0,
        "blocked_reads": 0, "blocked_writes": 0,
        "blocked_imports": 0, "blocked_workers": 0,
        "blocked_threads": 0, "blocked_clocks": 0,
        "blocked_garbage_collections": 0,
    }
    installed: list[tuple[Any, str, Any]] = []

    def install(owner: Any, name: str, replacement: Any) -> None:
        if hasattr(owner, name):
            installed.append((owner, name, getattr(owner, name)))
            setattr(owner, name, replacement)

    def denied(counter: str, message: str) -> Callable[..., Any]:
        def reject(*args: Any, **keywords: Any) -> Any:
            effects[counter] += 1
            raise SyntheticEffectError(message)
        return reject

    try:
        for owner, name in (
            (builtins, "open"), (io, "open"), (os, "open"),
            (os, "read"), (os, "stat"), (os, "lstat"),
            (Path, "open"), (Path, "read_bytes"), (Path, "read_text"),
        ):
            install(owner, name, denied(
                "blocked_reads", "source-only controls cannot read evidence",
            ))
        for owner, name in (
            (os, "write"), (os, "unlink"), (os, "remove"),
            (os, "rename"), (os, "replace"), (os, "mkdir"),
            (os, "rmdir"), (os, "fsync"), (Path, "write_bytes"),
            (Path, "write_text"), (Path, "unlink"), (Path, "mkdir"),
        ):
            install(owner, name, denied(
                "blocked_writes", "source-only controls cannot modify files",
            ))
        install(importlib, "import_module", denied(
            "blocked_imports", "source-only controls cannot import matchers",
        ))
        install(builtins, "__import__", denied(
            "blocked_imports", "source-only controls cannot import candidates",
        ))
        for name in ("Popen", "run", "call", "check_call", "check_output"):
            install(subprocess, name, denied(
                "blocked_workers", "source-only controls cannot run a worker",
            ))
        install(threading.Thread, "start", denied(
            "blocked_threads", "source-only controls cannot start a thread",
        ))
        for name in (
            "time", "time_ns", "monotonic", "monotonic_ns",
            "perf_counter", "perf_counter_ns", "process_time",
            "process_time_ns",
        ):
            install(time, name, denied(
                "blocked_clocks", "source-only controls cannot sample a clock",
            ))
        install(gc, "collect", denied(
            "blocked_garbage_collections",
            "source-only controls cannot collect garbage",
        ))
        yield effects
    finally:
        for owner, name, previous in reversed(installed):
            setattr(owner, name, previous)


def _synthetic_digest(label: str) -> str:
    return hashlib.sha256(("synthetic-only:" + label).encode("ascii")).hexdigest()


def _synthetic_artifact(label: str) -> dict[str, str]:
    return {
        "path": "oracle/phase1/synthetic-" + label + ".json",
        "sha256": _synthetic_digest(label),
    }


def synthetic_ready_document() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for name, (count, seed, matrix, records) in FROZEN_SUITES.items():
        baseline: dict[str, Any] = {
            "status": "PASS", "candidate_process_count": 0,
            "hidden_cases_read": 0, "timing_trials_run": 0,
            "publication_receipt": _synthetic_artifact(name + "-receipt"),
        }
        if name == "public_surface_v19":
            baseline["reference_role_count"] = 2
            baseline["distinct_reference_process_ids"] = "NOT CAPTURED"
        if name == "subinterpreter_v2":
            baseline.update({
                "reference_process_ids": [81, 82],
                "actual_interpreters_created": 22,
                "actual_interpreters_closed": 22,
                "actual_regex_match_operations": 788,
                "actual_case_triples": 256,
                "actual_phase_records": 768,
            })
        row: dict[str, Any] = {
            "id": name, "case_execution_count": count,
            "published_seed_decimal": seed,
            "matrix_sha256": matrix,
            "baseline_records_sha256": records or _synthetic_digest(name + "-records"),
            "source": {
                "path": FROZEN_SOURCE_PINS[name][0],
                "sha256": FROZEN_SOURCE_PINS[name][1],
            },
            "recorder": (
                {
                    "path": FROZEN_RECORDER_PINS[name][0],
                    "sha256": FROZEN_RECORDER_PINS[name][1],
                }
                if name in FROZEN_RECORDER_PINS else None
            ),
            "case_namespace": "synthetic-only/" + name,
            "baseline": baseline,
            "candidate_results": {
                "c": "NOT MEASURED",
                "rust": "NOT MEASURED",
                "zig": "NOT MEASURED",
            },
            "performance": "NOT MEASURED",
        }
        if name == "pep688_v4":
            row["public_operation_count"] = 19
            row["carrier_count"] = 4
            row["protocol"] = {
                "path": "oracle/cpython-3.14.6/PUBLIC-BUFFER-EXPORTER-V4.md",
                "sha256": (
                    "7f7a4a274c7b59e8f0148f2eae25c5a577fea8886dedbdff27b2fa66fe742905"
                ),
            }
        if name in ("public_v3", "scanner_v3", "buffer_v3"):
            row["protocol"] = {
                "path": PURE_CORE_PROTOCOL_RELATIVE,
                "sha256": PURE_CORE_PROTOCOL_SHA256,
            }
        if name == "public_surface_v19":
            row["real_locale_case_count"] = 64
            row["locale_transition_count"] = 192
            row["full_resource_parent"] = "original_full_v5"
        rows.append(row)
    rows.append({
        "id": "threaded_pattern_v1",
        "case_execution_count": THREADED_CASE_COUNT,
        "published_seed_decimal": THREADED_PUBLISHED_SEED,
        "matrix_sha256": THREADED_MATRIX_SHA256,
        "baseline_records_sha256": _synthetic_digest("threaded-records"),
        "source": {
            "path": THREADED_SOURCE_RELATIVE,
            "sha256": THREADED_SOURCE_SHA256,
        },
        "protocol": {
            "path": THREADED_PROTOCOL_RELATIVE,
            "sha256": THREADED_PROTOCOL_SHA256,
        },
        "recorder": _synthetic_artifact("threaded-recorder"),
        "case_namespace": "synthetic-only/threaded",
        "metadata_overlap_case_count": THREADED_METADATA_CASE_COUNT,
        "baseline": {
            "status": "PASS", "candidate_process_count": 0,
            "hidden_cases_read": 0, "timing_trials_run": 0,
            "publication_receipt": _synthetic_artifact("threaded-receipt"),
        },
        "candidate_results": {
            "c": "NOT MEASURED", "rust": "NOT MEASURED",
            "zig": "NOT MEASURED",
        },
        "performance": "NOT MEASURED",
        "version_metadata": {
            "attribute": "__version__", "type": "str", "value": "2.2.1",
            "candidate_module_name_asserted": False,
        },
    })
    original = {
        "source_method_count": 165, "public_method_count": 152,
        "runnable_public_method_count": 151,
        "private_waiver_count": len(PRIVATE_WAIVERS),
        "accounting_protocol": {
            "path": UPSTREAM_ACCOUNTING_PROTOCOL_RELATIVE,
            "sha256": UPSTREAM_ACCOUNTING_PROTOCOL_SHA256,
        },
        "accounting_manifest": {
            "path": UPSTREAM_ACCOUNTING_MANIFEST_RELATIVE,
            "sha256": UPSTREAM_ACCOUNTING_MANIFEST_SHA256,
        },
        "accounting_verifier": {
            "path": UPSTREAM_ACCOUNTING_VERIFIER_RELATIVE,
            "sha256": UPSTREAM_ACCOUNTING_VERIFIER_SHA256,
        },
        "private_waivers": [
            {"method": name, "reason": "synthetic private-only control"}
            for name in PRIVATE_WAIVERS
        ],
        "public_debug_skip": {
            "method": "ReTests.test_memory_leaks",
            "source_order_index": 138,
            "row_sha256": (
                "840264aaf4bf27c06d29ac78664767327a8f4b90008c5db994c88542c692b389"
            ),
            "private_waiver": False, "counted_as_runnable_case": False,
        },
        "original_method_matrix_sha256":
            FROZEN_SUITES["original_bounded_v5"][2],
        "original_record_vector_sha256":
            FROZEN_SUITES["original_bounded_v5"][3],
        "external_corpus": {
            "case_count": 403, "literal_case_count": 400,
            "extended_case_count": 3, "succeed_count": 289,
            "fail_count": 74, "syntax_error_count": 40,
            "external_pattern_fixture_count": 11,
            "performance": "NOT MEASURED",
        },
        "lineages": [
            {
                "id": "original_full_v5",
                "requested_and_delivered_big_memory_bytes": 2**31,
                "actual_max_memory_bytes": 42_949_672_960,
                "big_memory_dry_run": False,
                "candidate_big_memory_status": "NOT MEASURED",
                "distinct_reference_process_ids": "NOT CAPTURED",
            },
            {
                "id": "original_full_v6",
                "full_resource_parent": "original_full_v5",
                "distinct_reference_process_ids": "NOT CAPTURED",
            },
            {
                "id": "original_bounded_v5",
                "big_memory_dry_run": True,
                "big_memory_maximum_bytes": 5_147,
            },
        ],
    }
    all_names = [row["id"] for row in rows]
    crosswalk = [
        {
            "id": "P0-" + format(index + 1, "02d"),
            "description": "synthetic-only fully mapped obligation",
            "covered_by": [all_names[index % len(all_names)]],
        }
        for index in range(34)
    ]
    return {
        "schema": SCHEMA, "version": 1,
        "goal": {"path": "GOAL.md", "sha256": GOAL_SHA256},
        "runtime": {
            "python_version": "3.14.6", "python_implementation": "CPython",
            "executable": {
                "path": PINNED_PYTHON, "sha256": PINNED_PYTHON_SHA256,
            },
            "stdlib_sources": [
                {"path": relative, "sha256": fingerprint}
                for relative, fingerprint in PINNED_RUNTIME_SOURCES
            ],
        },
        "predecessor_obligation_matrices": [
            {
                "path": "oracle/v1/P0.md",
                "sha256": (
                    "30dc3dd121c8e2d7a080884923109164b4bbdf37103f56c2bac84727acbd4424"
                ),
                "obligation_count": 38,
            },
            {
                "path": "oracle/v2/P0.md",
                "sha256": (
                    "50fe34edd81ae22f3a2b8fb836a615fe625dc2b7c32ce0f045275554bf3b9e44"
                ),
                "obligation_count": 45, "includes_entire_version_1": True,
            },
        ],
        "original_upstream": original,
        "denominator": {
            "available_frozen_vector_case_executions": 31_237,
            "frozen_planned_case_execution_denominator": 31_237,
            "known_minimum_if_frozen_264_case_pep688_baseline_passes": 30_725,
            "pep688_case_executions_awaiting_two_reference_baseline": 0,
            "threaded_pattern_case_execution_count": 512,
            "final_required_case_execution_denominator": 30_725 + 512,
            "public_original_skip_cases_outside_runnable_denominator": 1,
            "private_upstream_methods_outside_public_denominator": 13,
            "historical_subinterpreter_versions_double_counted": False,
            "full_resource_original_versions_double_counted": False,
            "counted_suite_ids": all_names,
            "not_semantically_deduplicated": True,
        },
        "suites": rows,
        "obligations": {
            "inherited_count": len(INHERITED_OBLIGATIONS),
            "additional_named_count": len(ADDITIONAL_OBLIGATIONS),
            "crosswalk_count": len(crosswalk),
            "inherited": [
                {"id": name, "covered_by": ["original_bounded_v5"]}
                for name in INHERITED_OBLIGATIONS
            ],
            "additional": [
                {
                    "id": name,
                    "covered_by": (
                        ["threaded_pattern_v1"]
                        if name in (
                            "API-THREAD-SHARED-PATTERN-REENTRANCY",
                            "API-MODULE-VERSION-METADATA",
                        )
                        else ["public_surface_v19"]
                    ),
                }
                for name in ADDITIONAL_OBLIGATIONS
            ],
            "crosswalk": crosswalk,
        },
        "historical_evidence": {"synthetic": True},
        "candidate_results": {
            "c": "NOT MEASURED", "rust": "NOT MEASURED",
            "zig": "NOT MEASURED",
        },
        "audit_boundaries": {
            "candidate_processes_started": 0,
            "reference_processes_started_by_ledger": 0,
            "timing_trials_run": 0, "clock_samples": 0,
            "hidden_cases_read": 0, "final_cases_read": 0,
            "external_regex_packages_used": 0,
            "performance": "NOT MEASURED",
            "native_memory": "NOT MEASURED",
            "candidate_qualified": False, "winner_selected": False,
        },
        "phase_gate": {
            "phase": "CORRECTNESS ORACLE", "status": "PASS",
            "blockers": [], "all_obligations_mapped": True,
            "candidate_evaluation_authorized": False,
            "final_holdout_authorized": False,
        },
    }


def source_self_test() -> dict[str, Any]:
    verify_runtime()
    passed: list[str] = []
    rejected: list[str] = []

    def accept(name: str, condition: Any) -> None:
        require(type(name) is str and name not in passed and bool(condition),
                "a genuine source-only completeness control failed: " + name)
        passed.append(name)

    def reject(name: str, action: Callable[[], Any]) -> None:
        require(type(name) is str and name not in rejected,
                "a synthetic completeness poison was duplicated")
        try:
            action()
        except (
            CompletenessError, KeyError, TypeError, ValueError, OSError,
            UnicodeError, zlib.error,
        ):
            rejected.append(name)
            return
        raise CompletenessError("a falsified completeness ledger passed: " + name)

    with source_only_boundary() as effects:
        document = synthetic_ready_document()
        suites = validate_document(document, require_ready=True)
        accept("all-45-immutable-inherited-obligations-are-mapped",
               len(INHERITED_OBLIGATIONS) == 45)
        accept("all-28-independently-discovered-obligations-are-mapped",
               len(ADDITIONAL_OBLIGATIONS) == 28)
        accept("thirteen-named-private-waivers-and-one-public-debug-skip",
               len(PRIVATE_WAIVERS) == 13)
        accept("all-thirteen-separate-source-only-suites-remain-visible",
               len(suites) == 13)
        accept("thread-metadata-cohort-never-requires-module-name-re",
               suites["threaded_pattern_v1"]["version_metadata"][
                   "candidate_module_name_asserted"
               ] is False)
        accept("retain-valid-canonical-escaped-lone-surrogate",
               decode_canonical(b'{"text":"\\ud800"}\n', "synthetic surrogate")
               == {"text": "\ud800"})
        accept("synthetic-document-is-canonical-and-complete",
               decode_canonical(canonical(document), "synthetic complete ledger")
               == document)
        accept("preserve-real-full-resource-and-bounded-original-separately",
               document["original_upstream"]["lineages"][0][
                   "requested_and_delivered_big_memory_bytes"
               ] == 2**31)
        accept("do-not-invent-broad-reference-process-identifiers",
               suites["public_surface_v19"]["baseline"][
                   "distinct_reference_process_ids"
               ] == "NOT CAPTURED")
        synthetic_plain = canonical({
            "kind": "synthetic-only-complete-gzip",
            "valid_escaped_surrogate": "\ud800",
        })
        synthetic_encoder = zlib.compressobj(
            level=9, wbits=16 + zlib.MAX_WBITS,
        )
        synthetic_archive = (
            synthetic_encoder.compress(synthetic_plain)
            + synthetic_encoder.flush()
        )
        synthetic_plain_sha256 = hashlib.sha256(synthetic_plain).hexdigest()
        synthetic_restored = verify_gzip(
            synthetic_archive,
            expected_sha256=synthetic_plain_sha256,
            expected_bytes=len(synthetic_plain),
            capture_plain=True,
        )
        accept(
            "verify-complete-single-member-mtime-zero-synthetic-gzip",
            synthetic_restored["plain"] == synthetic_plain
            and synthetic_restored["complete"] is True,
        )
        for name, payload, expected_hash, expected_length in (
            (
                "reject-truncated-synthetic-gzip",
                synthetic_archive[:-1], synthetic_plain_sha256,
                len(synthetic_plain),
            ),
            (
                "reject-hidden-second-synthetic-gzip-member",
                synthetic_archive + synthetic_archive,
                synthetic_plain_sha256, len(synthetic_plain),
            ),
            (
                "reject-extra-trailing-synthetic-gzip-data",
                synthetic_archive + b"hidden",
                synthetic_plain_sha256, len(synthetic_plain),
            ),
            (
                "reject-wrong-synthetic-gzip-plaintext-hash",
                synthetic_archive, _synthetic_digest("forged-gzip"),
                len(synthetic_plain),
            ),
            (
                "reject-missing-synthetic-gzip-plaintext-byte",
                synthetic_archive, synthetic_plain_sha256,
                len(synthetic_plain) - 1,
            ),
            (
                "reject-invented-synthetic-gzip-plaintext-byte",
                synthetic_archive, synthetic_plain_sha256,
                len(synthetic_plain) + 1,
            ),
            (
                "reject-nonzero-synthetic-gzip-modification-time",
                synthetic_archive[:4] + b"\x01\x00\x00\x00"
                + synthetic_archive[8:],
                synthetic_plain_sha256, len(synthetic_plain),
            ),
            (
                "reject-forged-synthetic-gzip-checksum",
                synthetic_archive[:-8]
                + bytes([synthetic_archive[-8] ^ 1])
                + synthetic_archive[-7:],
                synthetic_plain_sha256, len(synthetic_plain),
            ),
        ):
            reject(
                name,
                lambda payload=payload, expected_hash=expected_hash,
                expected_length=expected_length: verify_gzip(
                    payload, expected_sha256=expected_hash,
                    expected_bytes=expected_length,
                    capture_plain=True,
                ),
            )

        for field in tuple(document):
            altered = copy.deepcopy(document)
            altered.pop(field)
            reject(
                "reject-missing-root-field-" + field,
                lambda altered=altered: validate_document(
                    altered, require_ready=True,
                ),
            )
        for index, name in enumerate(INHERITED_OBLIGATIONS):
            altered = copy.deepcopy(document)
            altered["obligations"]["inherited"].pop(index)
            reject(
                "reject-missing-inherited-obligation-" + name,
                lambda altered=altered: validate_document(
                    altered, require_ready=True,
                ),
            )
        for index, name in enumerate(ADDITIONAL_OBLIGATIONS):
            altered = copy.deepcopy(document)
            altered["obligations"]["additional"].pop(index)
            reject(
                "reject-missing-additional-obligation-" + name,
                lambda altered=altered: validate_document(
                    altered, require_ready=True,
                ),
            )
        for index, original in enumerate(document["suites"]):
            for field in ("case_execution_count", "matrix_sha256"):
                altered = copy.deepcopy(document)
                actual = altered["suites"][index]
                actual[field] = (
                    0 if field == "case_execution_count"
                    else (
                        "g" * 64
                        if original["id"] == "threaded_pattern_v1"
                        else _synthetic_digest("forged-" + original["id"])
                    )
                )
                reject(
                    "reject-forged-" + original["id"] + "-" + field,
                    lambda altered=altered: validate_document(
                        altered, require_ready=True,
                    ),
                )
        for index, name in enumerate(PRIVATE_WAIVERS):
            altered = copy.deepcopy(document)
            altered["original_upstream"]["private_waivers"].pop(index)
            reject(
                "reject-omitted-exact-private-waiver-" + name,
                lambda altered=altered: validate_document(
                    altered, require_ready=True,
                ),
            )
        for index in range(len(document["obligations"]["crosswalk"])):
            altered = copy.deepcopy(document)
            altered["obligations"]["crosswalk"][index]["covered_by"] = []
            reject(
                "reject-unmapped-public-crosswalk-" + format(index, "02d"),
                lambda altered=altered: validate_document(
                    altered, require_ready=True,
                ),
            )
        for name, changed in (
            ("forged-global-candidate-pass", ("candidate_results", "rust", "PASS")),
            ("forged-global-candidate-speed", ("candidate_results", "zig", "1.5x")),
        ):
            altered = copy.deepcopy(document)
            outer, inner, value = changed
            altered[outer][inner] = value
            reject(name, lambda altered=altered: validate_document(
                altered, require_ready=True,
            ))
        for key, value in (
            ("hidden_cases_read", 1),
            ("final_cases_read", 1),
            ("clock_samples", 1),
            ("timing_trials_run", 1),
            ("candidate_processes_started", 1),
            ("external_regex_packages_used", 1),
            ("winner_selected", True),
        ):
            altered = copy.deepcopy(document)
            altered["audit_boundaries"][key] = value
            reject(
                "reject-hidden-candidate-timing-or-winner-" + key,
                lambda altered=altered: validate_document(
                    altered, require_ready=True,
                ),
            )
        for name, payload in (
            ("duplicate-json-key", b'{"x":1,"x":2}\n'),
            ("nonfinite-json-nan", b'{"x":NaN}\n'),
            ("nonfinite-json-infinity", b'{"x":Infinity}\n'),
            ("nonfinite-json-negative-infinity", b'{"x":-Infinity}\n'),
            ("truncated-json-document", b'{"x":1'),
            ("noncanonical-json-spacing", b'{ "x": 1 }\n'),
            ("noncanonical-json-key-order", b'{"z":1,"a":2}\n'),
            ("uncanonical-utf8-lone-surrogate", b'{"x":"\xed\xa0\x80"}\n'),
        ):
            reject(
                "reject-" + name,
                lambda payload=payload: decode_canonical(
                    payload, "synthetic-only poison",
                ),
            )
        allowed = frozenset({DOCUMENT_RELATIVE})
        for name, path in (
            ("performance-root", "performance/forbidden.json"),
            ("candidate-root", "candidates/forbidden.json"),
            ("hidden-root", "hidden/forbidden.json"),
            ("holdout-root", "holdout/forbidden.json"),
            ("absolute-root", "/tmp/forbidden.json"),
            ("parent-escape", "oracle/phase1/../forbidden.json"),
            ("backslash-escape", "oracle\\phase1\\forbidden.json"),
            ("foreign-evidence", "oracle/phase1/foreign.json"),
        ):
            reject(
                "reject-unapproved-" + name,
                lambda path=path: safe_relative(path, allowed),
            )
        for name, action in (
            ("intercept-real-source-only-file-read",
             lambda: builtins.open(DOCUMENT_RELATIVE, "rb")),
            ("intercept-real-source-only-descriptor-read",
             lambda: os.open(DOCUMENT_RELATIVE, os.O_RDONLY)),
            ("intercept-real-source-only-file-write",
             lambda: os.write(1, b"forbidden")),
            ("intercept-real-source-only-candidate-import",
             lambda: importlib.import_module("candidates.rust_candidate")),
            ("intercept-real-source-only-reference-worker",
             lambda: subprocess.Popen([PINNED_PYTHON])),
            ("intercept-real-source-only-thread",
             lambda: threading.Thread(target=lambda: None).start()),
            ("intercept-real-source-only-performance-clock",
             lambda: time.perf_counter()),
            ("intercept-real-source-only-wall-clock",
             lambda: time.time()),
            ("intercept-real-source-only-garbage-collector",
             lambda: gc.collect()),
        ):
            reject(name, action)
        accept(
            "all-real-world-source-only-effects-are-zero",
            all(effects[name] == 0 for name in (
                "actual_file_reads", "actual_file_writes",
                "actual_candidate_imports", "actual_reference_imports",
                "actual_workers_started", "actual_threads_started",
                "actual_clock_samples", "actual_garbage_collections",
                "hidden_cases_read", "performance_files_read",
            )),
        )
        accept(
            "all-seven-independent-real-effect-families-are-intercepted",
            all(effects[name] > 0 for name in (
                "blocked_reads", "blocked_writes", "blocked_imports",
                "blocked_workers", "blocked_threads", "blocked_clocks",
                "blocked_garbage_collections",
            )),
        )
        require(len(rejected) >= MINIMUM_SYNTHETIC_REJECTIONS
                and len(rejected) == len(set(rejected)),
                "at least 100 genuine distinct hostile controls must fail closed")
    verify_runtime()
    return {
        "schema": SCHEMA + "-verifier-source-self-test",
        "status": "PASS",
        "python": "3.14.6",
        "synthetic": True,
        "inherited_obligation_count": len(INHERITED_OBLIGATIONS),
        "additional_obligation_count": len(ADDITIONAL_OBLIGATIONS),
        "private_waiver_count": len(PRIVATE_WAIVERS),
        "accepted_control_count": len(passed),
        "rejected_control_count": len(rejected),
        "accepted_controls": passed,
        "rejected_controls": rejected,
        "effects": effects,
        "actual_files_read": 0,
        "actual_files_written": 0,
        "actual_candidate_workers": 0,
        "actual_reference_workers": 0,
        "actual_clock_samples": 0,
        "hidden_cases_read": 0,
        "performance_files_read": 0,
        "performance": "NOT MEASURED",
        "final_winner_selected": False,
    }


def _collect_artifacts(value: Any, result: set[str]) -> None:
    if type(value) is dict:
        if (type(value.get("path")) is str
                and type(value.get("sha256")) is str
                and len(value["sha256"]) == 64
                and not value["path"].startswith("/")):
            result.add(value["path"])
        for child in value.values():
            _collect_artifacts(child, result)
    elif type(value) is list:
        for child in value:
            _collect_artifacts(child, result)


def _authenticate_pure_core_reference(
    suite: Mapping[str, Any],
    receipt: Mapping[str, Any],
    archive: Mapping[str, Any],
    archive_bytes: bytes,
    actual: Mapping[str, Any],
) -> None:
    expected_category = {
        "public_v3": "public",
        "scanner_v3": "scanner",
        "buffer_v3": "buffer",
    }[suite["id"]]
    count = suite["case_execution_count"]
    records = suite["baseline_records_sha256"]
    roles = receipt.get("reference_pids")
    require(
        receipt.get("schema")
        == "rebar-independent-public-contract-v3-pure-baselines-v1-"
        "durable-publication-receipt"
        and receipt.get("phase") == "correctness-oracle-baseline"
        and receipt.get("category") == expected_category
        and receipt.get("label") == "phase1-v1"
        and receipt.get("python") == "3.14.6"
        and receipt.get("recorder_relative") == PURE_CORE_RECORDER_RELATIVE
        and receipt.get("recorder_source_sha256") == PURE_CORE_RECORDER_SHA256
        and receipt.get("contract_relative")
        == "tools/independent_public_contract_v3.py"
        and receipt.get("contract_source_sha256")
        == "9a831571c81e542d7d43ae56aea271f8e6c69550173d97ae1c9f8213eef40bf3"
        and receipt.get("category_source_relative")
        == FROZEN_SOURCE_PINS[suite["id"]][0]
        and receipt.get("category_source_sha256")
        == FROZEN_SOURCE_PINS[suite["id"]][1]
        and receipt.get("published_seed")
        == int(suite["published_seed_decimal"])
        and receipt.get("matrix_sha256") == suite["matrix_sha256"]
        and receipt.get("frozen_baseline_records_sha256") == records
        and receipt.get("case_count") == count
        and type(roles) is dict
        and set(roles) == {"reference_a", "reference_b"}
        and all(type(pid) is int and pid > 0 for pid in roles.values())
        and len(set(roles.values())) == 2
        and receipt.get("distinct_reference_pids") is True
        and receipt.get("actual_reference_workers") == 2
        and receipt.get("observed_reference_case_counts")
        == {"reference_a": count, "reference_b": count}
        and receipt.get("reference_records_sha256")
        == {"reference_a": records, "reference_b": records}
        and receipt.get("reference_mismatch_count") == 0
        and receipt.get("reference_failure_count") == 0
        and receipt.get("complete_reference_worker_failures") == []
        and receipt.get("source_closure_unchanged") is True
        and receipt.get("archive_relative") == archive["path"]
        and receipt.get("archive_sha256") == archive["sha256"]
        and receipt.get("archive_bytes") == len(archive_bytes)
        and receipt.get("approved_fresh_path_count") == 2
        and receipt.get("fresh_paths_checked_before_references") is True
        and receipt.get("actual_candidate_workers") == 0
        and receipt.get("actual_candidate_imports") == 0
        and receipt.get("clock_samples") == 0
        and receipt.get("timing_trials_run") == 0
        and receipt.get("benchmark_files_read") == 0
        and receipt.get("hidden_cases_read") == 0
        and receipt.get("holdout") == "NOT ACCESSED"
        and receipt.get("performance") == "NOT MEASURED",
        "the actual zero-candidate V3 two-reference category was falsified",
    )
    publication = receipt.get("archive_publication")
    require(
        type(publication) is dict
        and publication.get("status") == "PASS"
        and publication.get("kind") == "archive"
        and publication.get("path") == archive["path"]
        and publication.get("sha256") == archive["sha256"]
        and publication.get("bytes") == len(archive_bytes)
        and publication.get("actual_bytes_written") == len(archive_bytes)
        and publication.get("actual_write_calls") == 1
        and publication.get("file_fsync_completed") is True
        and publication.get("directory_fsync_completed") is True
        and publication.get("complete_readback_verified") is True
        and publication.get("atomic_no_overwrite_link") is True
        and publication.get("owned_temporary_removed") is True,
        "the actual pure-reference archive was not durably published",
    )
    owner = importlib.import_module(
        "tools.record_independent_public_contract_baselines_v1",
    )
    require(
        os.path.abspath(owner.__file__)
        == str(ROOT / PURE_CORE_RECORDER_RELATIVE)
        and os.path.realpath(owner.__file__)
        == str(ROOT / PURE_CORE_RECORDER_RELATIVE),
        "the original source-pinned pure-reference owner was substituted",
    )
    selected = owner.CATEGORIES[expected_category]
    context = owner.authenticate_contract(PURE_CORE_RECORDER_SHA256, selected)
    original = owner.decode_canonical(
        actual["plain"], archive["path"] + ":complete-original",
        owner.MAX_REPORT_BYTES,
    )
    workers = original.get("reference_workers")
    processes = original.get("isolated_reference_process_evidence")
    matrix = original.get("source_ordered_complete_stimuli")
    groups = original.get("source_ordered_groups")
    require(
        original.get("schema")
        == "rebar-independent-public-contract-v3-pure-baselines-v1"
        and original.get("status") == "PASS"
        and original.get("phase") == "correctness-oracle-baseline"
        and original.get("python") == "3.14.6"
        and original.get("label") == "phase1-v1"
        and original.get("category") == expected_category
        and original.get("recorder_relative") == PURE_CORE_RECORDER_RELATIVE
        and original.get("recorder_source_sha256") == PURE_CORE_RECORDER_SHA256
        and original.get("contract_relative")
        == "tools/independent_public_contract_v3.py"
        and original.get("contract_source_sha256")
        == "9a831571c81e542d7d43ae56aea271f8e6c69550173d97ae1c9f8213eef40bf3"
        and original.get("category_source_relative")
        == FROZEN_SOURCE_PINS[suite["id"]][0]
        and original.get("category_source_sha256")
        == FROZEN_SOURCE_PINS[suite["id"]][1]
        and original.get("published_seed")
        == int(suite["published_seed_decimal"])
        and original.get("matrix_sha256") == suite["matrix_sha256"]
        and original.get("frozen_baseline_records_sha256") == records
        and original.get("case_count") == count
        and original.get("group_count") == selected.group_count
        and original.get("cases_per_group") == selected.cases_per_group
        and type(workers) is dict
        and set(workers) == {"reference_a", "reference_b"}
        and type(processes) is dict
        and set(processes) == {"reference_a", "reference_b"}
        and type(matrix) is list and len(matrix) == count
        and type(groups) is list and len(groups) == selected.group_count
        and original.get("reference_pids") == roles
        and original.get("distinct_reference_pids") is True
        and original.get("actual_reference_workers") == 2
        and original.get("observed_reference_case_counts")
        == {"reference_a": count, "reference_b": count}
        and original.get("reference_records_sha256")
        == {"reference_a": records, "reference_b": records}
        and original.get("reference_mismatch_count") == 0
        and original.get("all_reference_mismatches") == []
        and original.get("reference_failure_count") == 0
        and original.get("complete_reference_worker_failures") == []
        and original.get("source_provenance_before")
        == context["source_provenance"]
        and original.get("source_provenance_after")
        == context["source_provenance"]
        and original.get("source_closure_unchanged") is True
        and original.get("actual_candidate_workers") == 0
        and original.get("actual_candidate_imports") == 0
        and original.get("candidate_family") is None
        and original.get("candidate_records") is None
        and original.get("clock_samples") == 0
        and original.get("timing_trials_run") == 0
        and original.get("benchmark_files_read") == 0
        and original.get("hidden_cases_read") == 0
        and original.get("holdout") == "NOT ACCESSED"
        and original.get("performance") == "NOT MEASURED",
        "the complete genuine pure-reference archive was falsified",
    )
    owner.validate_matrix_rows(
        selected, matrix, tuple(groups), suite["matrix_sha256"],
    )
    require(matrix == context["matrix"] and tuple(groups) == context["groups"],
            "an actual pure-reference source-ordered matrix was substituted")
    actual_pids: list[int] = []
    for role in ("reference_a", "reference_b"):
        report, process = owner.validate_reference(
            context, role, workers[role], processes[role],
        )
        require(
            report == workers[role]
            and process == processes[role]
            and process.get("pid") == roles[role],
            "an original complete pure-reference worker was substituted",
        )
        actual_pids.append(process["pid"])
    require(
        len(set(actual_pids)) == 2
        and sorted(actual_pids)
        == suite["baseline"]["reference_process_ids"]
        and owner.verify_source_closure(context)
        == context["source_provenance"],
        "a genuine pure-reference process or frozen source owner changed",
    )


def _authenticate_managed_archive_index(
    suite: Mapping[str, Any],
    receipt: Mapping[str, Any],
    raw_receipt: bytes,
    archive: Mapping[str, Any],
    archive_bytes: bytes,
    actual: Mapping[str, Any],
    allowed: frozenset[str],
) -> None:
    baseline = suite["baseline"]
    index = validate_artifact(baseline.get("archive_index"))
    require(
        index is not None
        and index["path"] == MANAGED_ARCHIVE_INDEX_RELATIVE
        and index["sha256"] == MANAGED_ARCHIVE_INDEX_SHA256,
        "the genuine managed original-report archive bridge was substituted",
    )
    restorer = validate_artifact(baseline.get("archive_restorer"))
    require(
        restorer is not None
        and restorer["path"] == MANAGED_RESTORER_RELATIVE
        and restorer["sha256"] == MANAGED_RESTORER_SHA256,
        "the independently frozen managed archive restorer was substituted",
    )
    bridge_raw = read_owned(
        index["path"], index["sha256"], MAX_DOCUMENT_BYTES, allowed,
    )
    bridge = decode_complete_json(bridge_raw, index["path"])
    compressed = bridge.get("archive")
    original = bridge.get("report")
    original_receipt = bridge.get("receipt")
    require(
        bridge.get("schema")
        == "rebar-managed-buffer-lifetime-baseline-v1-lossless-archive"
        and bridge.get("status") == "PASS"
        and bridge.get("case_count") == suite["case_execution_count"]
        and bridge.get("published_seed")
        == int(suite["published_seed_decimal"])
        and bridge.get("matrix_sha256") == suite["matrix_sha256"]
        and bridge.get("baseline_records_sha256")
        == suite["baseline_records_sha256"]
        and bridge.get("actual_reference_workers") == 2
        and bridge.get("actual_candidate_workers") == 0
        and bridge.get("benchmark_files_read") == 0
        and bridge.get("hidden_cases_read") == 0
        and bridge.get("clock_samples") == 0
        and bridge.get("timing_trials_run") == 0
        and bridge.get("performance") == "NOT MEASURED"
        and bridge.get("winner_selected") is False
        and type(compressed) is dict
        and compressed.get("relative") == archive["path"]
        and compressed.get("sha256") == archive["sha256"]
        and compressed.get("bytes") == len(archive_bytes)
        and compressed.get("format") == "gzip"
        and compressed.get("member_count") == 1
        and compressed.get("trailing_bytes") == 0
        and compressed.get("deterministic_command") == "gzip -n -9 -k"
        and type(original) is dict
        and original.get("bytes") == actual["bytes"]
        and original.get("sha256") == actual["sha256"]
        and original.get("complete_case_count")
        == suite["case_execution_count"]
        and type(original_receipt) is dict
        and original_receipt.get("relative")
        == baseline["publication_receipt"]["path"]
        and original_receipt.get("sha256")
        == baseline["publication_receipt"]["sha256"]
        and original_receipt.get("bytes") == len(raw_receipt),
        "the exact genuine original-report managed archive bridge changed",
    )
    for key, expected in (
        ("oracle", FROZEN_SOURCE_PINS["managed_v1"]),
        ("recorder", FROZEN_RECORDER_PINS["managed_v1"]),
        ("restorer", (MANAGED_RESTORER_RELATIVE, MANAGED_RESTORER_SHA256)),
    ):
        owner_record = bridge.get(key)
        require(
            type(owner_record) is dict
            and owner_record.get("relative") == expected[0]
            and owner_record.get("sha256") == expected[1],
            "a genuine managed archive owner was substituted: " + key,
        )
    read_owned(
        MANAGED_RESTORER_RELATIVE, MANAGED_RESTORER_SHA256,
        MAX_SOURCE_BYTES, allowed,
    )
    owner = importlib.import_module(
        "tools.restore_managed_buffer_lifetime_baseline_v1",
    )
    require(
        os.path.abspath(owner.__file__)
        == str(ROOT / MANAGED_RESTORER_RELATIVE)
        and os.path.realpath(owner.__file__)
        == str(ROOT / MANAGED_RESTORER_RELATIVE),
        "the original source-pinned managed receipt decoder was substituted",
    )
    genuine_receipt = owner.decode_receipt(raw_receipt)
    owner.validate_receipt(genuine_receipt)
    require(
        genuine_receipt == receipt
        and receipt.get("schema")
        == "rebar-independent-managed-buffer-lifetime-v1-recorder-"
        "durable-publication-receipt"
        and receipt.get("report_relative") == original["relative"]
        and receipt.get("report_sha256") == original["sha256"]
        and receipt.get("report_bytes") == original["bytes"]
        and receipt.get("report_actual_write_calls") == 1
        and receipt.get("report_atomic_no_overwrite_link") is True
        and receipt.get("report_complete_readback_verified") is True
        and receipt.get("report_file_fsync_completed") is True
        and receipt.get("report_directory_fsync_completed") is True
        and receipt.get("baseline_reference_pids")
        == baseline["reference_process_ids"],
        "the genuine producer-owned original managed publication was forged",
    )


def _authenticate_baseline_receipt(
    suite: Mapping[str, Any], allowed: frozenset[str],
) -> None:
    baseline = suite["baseline"]
    evidence = validate_artifact(baseline.get("publication_receipt"))
    require(evidence is not None, "an actual independently signed receipt is mandatory")
    raw = read_owned(
        evidence["path"], evidence["sha256"],
        MAX_RECEIPT_BYTES, allowed,
    )
    receipt = decode_canonical(raw, evidence["path"])
    require(receipt.get("status") == "PASS",
            "a genuine complete baseline receipt reports a failure")
    compressed = baseline.get("compressed_report")
    uncompressed = baseline.get("uncompressed_report")
    archive = validate_artifact(compressed)
    require(archive is not None and type(uncompressed) is dict,
            "a complete frozen compressed and uncompressed pair is mandatory")
    archive_bytes = read_owned(
        archive["path"], archive["sha256"],
        MAX_COMPRESSED_BYTES, allowed,
    )
    actual = verify_gzip(
        archive_bytes,
        expected_sha256=uncompressed["sha256"],
        expected_bytes=uncompressed["bytes"],
        capture_plain=suite["id"] in {
            "public_v3", "scanner_v3", "buffer_v3", "pep688_v4",
        },
    )
    if suite["id"] in ("public_v3", "scanner_v3", "buffer_v3"):
        _authenticate_pure_core_reference(
            suite, receipt, archive, archive_bytes, actual,
        )
        return
    if suite["id"] == "managed_v1":
        _authenticate_managed_archive_index(
            suite, receipt, raw, archive, archive_bytes, actual, allowed,
        )
        return
    if suite["id"] == "pep688_v4":
        require(
            receipt.get("schema")
            == "rebar-python-re-pep688-buffer-exporter-v4-actual-exclusive-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("path") == archive["path"]
            and receipt.get("sha256") == archive["sha256"]
            and receipt.get("bytes") == len(archive_bytes)
            and receipt.get("uncompressed_sha256") == actual["sha256"]
            and receipt.get("uncompressed_bytes") == actual["bytes"]
            and receipt.get("matrix_sha256") == suite["matrix_sha256"]
            and receipt.get("case_count") == suite["case_execution_count"]
            and receipt.get("protocol_sha256")
            == "7f7a4a274c7b59e8f0148f2eae25c5a577fea8886dedbdff27b2fa66fe742905"
            and receipt.get("file_fsync_completed") is True
            and receipt.get("directory_fsync_completed") is True
            and receipt.get("exact_same_inode_readback_verified") is True
            and receipt.get("complete_bounded_decompression_verified") is True
            and receipt.get("single_gzip_member") is True
            and receipt.get("gzip_mtime") == 0
            and receipt.get("performance") == "NOT MEASURED"
            and receipt.get("holdout") == "NOT ACCESSED"
            and receipt.get("synthetic") is False,
            "the actual corrected PEP 688 exclusive receipt was falsified",
        )
        owner = importlib.import_module(
            "tools.python_re_buffer_exporter_oracle_v4",
        )
        require(os.path.abspath(owner.__file__)
                == str(ROOT / FROZEN_SOURCE_PINS["pep688_v4"][0]),
                "the genuine original PEP 688 evidence decoder was substituted")
        original = owner.decode_canonical(
            actual["plain"], archive["path"] + ":complete-original",
        )
        require(
            original.get("schema")
            == "rebar-python-re-pep688-buffer-exporter-v4-self-oracle"
            and original.get("status") == "PASS"
            and original.get("source_sha256")
            == FROZEN_SOURCE_PINS["pep688_v4"][1]
            and original.get("matrix_sha256") == suite["matrix_sha256"]
            and original.get("case_count") == suite["case_execution_count"]
            and original.get("reference_vector_sha256")
            == suite["baseline_records_sha256"]
            and original.get("actual_independent_reference_count") == 2
            and original.get("actual_reference_process_count") == 2
            and original.get("actual_case_executions")
            == 2 * suite["case_execution_count"]
            and original.get("actual_candidate_workers") == 0
            and original.get("candidate_imports") == 0
            and original.get("holdout_cases_read") == 0
            and original.get("performance_fixtures_read") == 0
            and original.get("performance") == "NOT MEASURED",
            "the complete real two-reference PEP 688 report was falsified",
        )
        workers = original.get("reference_worker_reports")
        processes = original.get("reference_worker_processes")
        require(
            type(workers) is dict
            and type(processes) is dict
            and set(workers) == {"reference_a", "reference_b"}
            and set(processes) == {"reference_a", "reference_b"}
            and all(
                type(workers[role]) is dict
                and workers[role].get("records_sha256")
                == suite["baseline_records_sha256"]
                and type(workers[role].get("records")) is list
                and len(workers[role]["records"])
                == suite["case_execution_count"]
                and type(processes[role]) is dict
                and type(processes[role].get("pid")) is int
                and processes[role]["pid"] > 0
                for role in ("reference_a", "reference_b")
            )
            and processes["reference_a"]["pid"]
            != processes["reference_b"]["pid"]
            and sorted([
                processes["reference_a"]["pid"],
                processes["reference_b"]["pid"],
            ]) == baseline["reference_process_ids"],
            "the real complete PEP 688 role vectors or exact PIDs disappeared",
        )
        for role in ("reference_a", "reference_b"):
            genuine_worker = owner.validate_worker_document(
                workers[role], role=role,
                pins={"source": FROZEN_SOURCE_PINS["pep688_v4"][1]},
            )
            owner.validate_worker_process(
                processes[role], role=role, expected=genuine_worker,
            )
        return
    if suite["id"] == "threaded_pattern_v1":
        owner = importlib.import_module(
            "tools.python_re_threaded_pattern_oracle_v1",
        )
        require(os.path.abspath(owner.__file__)
                == str(ROOT / THREADED_SOURCE_RELATIVE),
                "the corrected original threaded evidence decoder changed")
        original = owner.restore_publication_document(
            archive["path"], archive_bytes,
        )
        genuine_receipt = owner.restore_publication_document(
            evidence["path"], raw,
        )
        require(genuine_receipt == receipt,
                "a producer-owned complete threaded receipt was substituted")
        owner.validate_publication_receipt(
            genuine_receipt, relative=archive["path"], document=original,
        )
        require(
            original.get("schema")
            == "rebar-python-re-genuine-threaded-pattern-v1-self-oracle"
            and original.get("status") == "PASS"
            and original.get("python") == "3.14.6"
            and original.get("source_path") == THREADED_SOURCE_RELATIVE
            and original.get("source_sha256") == THREADED_SOURCE_SHA256
            and original.get("protocol_path") == THREADED_PROTOCOL_RELATIVE
            and original.get("protocol_sha256") == THREADED_PROTOCOL_SHA256
            and original.get("matrix_sha256") == THREADED_MATRIX_SHA256
            and original.get("case_count") == THREADED_CASE_COUNT
            and original.get("threaded_case_count") == THREADED_CASE_COUNT
            and original.get("metadata_case_count")
            == THREADED_METADATA_CASE_COUNT
            and original.get("metadata_cases_are_threaded_subset") is True
            and original.get("module_version") == "2.2.1"
            and original.get("module_version_type") == "str"
            and original.get("actual_independent_reference_count") == 2
            and original.get("distinct_reference_processes") is True
            and original.get("reference_records_sha256")
            == suite["baseline_records_sha256"]
            and original.get("actual_thread_starts") == 64
            and original.get("actual_thread_joins") == 64
            and original.get("actual_thread_case_executions") == 2_048
            and original.get("actual_regex_api_calls") == 4_352
            and original.get("all_barriers_verified") is True
            and original.get("all_thread_joins_verified") is True
            and original.get("orphan_threads") == 0
            and original.get("candidate_status") == "NOT RUN"
            and original.get("candidate_imports") == 0
            and original.get("native_owner_workers") == 0
            and original.get("benchmark_or_timing_executed") is False
            and original.get("performance") == "NOT MEASURED"
            and original.get("holdout") == "NOT ACCESSED",
            "an actual complete genuine 512-case threaded reference changed",
        )
        roles = original.get("reference_roles")
        require(type(roles) is dict
                and set(roles) == {"reference_a", "reference_b"},
                "a genuinely independent threaded reference role was omitted")
        actual_pids: list[int] = []
        for role in ("reference_a", "reference_b"):
            process = roles[role]
            require(type(process) is dict
                    and process.get("status") == "PASS"
                    and process.get("role") == role
                    and process.get("returncode") == 0
                    and process.get("signal") is None
                    and process.get("timed_out") is False
                    and process.get("stdout_complete") is True
                    and process.get("stderr_complete") is True
                    and type(process.get("pid")) is int
                    and process["pid"] > 0,
                    "an actual complete threaded reference process was forged")
            stdout = owner.restore_complete_stream(
                process.get("stdout"), label=role + " complete original stdout",
            )
            stderr = owner.restore_complete_stream(
                process.get("stderr"), label=role + " complete original stderr",
            )
            require(stderr == b"", "a passing thread reference concealed stderr")
            report = owner.strict_canonical(
                stdout, label=role + " original producer-canonical report",
            )
            require(report == process.get("report"),
                    "a genuine complete threaded reference stream changed")
            owner.validate_worker_document(
                report, role, expected_pid=process["pid"],
            )
            actual_pids.append(process["pid"])
        require(
            len(set(actual_pids)) == 2
            and sorted(actual_pids) == baseline["reference_process_ids"],
            "the two genuine threaded reference PIDs were invented or reused",
        )
        return
    if suite["id"] == "subinterpreter_v2":
        require(receipt.get("schema")
                == "rebar-python-re-genuine-subinterpreter-v2-exclusive-publication-receipt"
                and receipt.get("path") == archive["path"]
                and receipt.get("expected_sha256") == archive["sha256"]
                and receipt.get("uncompressed_sha256") == actual["sha256"]
                and receipt.get("uncompressed_bytes") == actual["bytes"]
                and receipt.get("file_fsync") is True
                and receipt.get("directory_fsync") is True
                and receipt.get("safe_parent_component_walk") is True,
                "the actual no-follow V2 interpreter receipt was falsified")
        owner = importlib.import_module(
            "tools.python_re_subinterpreter_oracle_v2",
        )
        require(
            os.path.abspath(owner.__file__)
            == str(ROOT / FROZEN_SOURCE_PINS["subinterpreter_v2"][0])
            and os.path.realpath(owner.__file__)
            == str(ROOT / FROZEN_SOURCE_PINS["subinterpreter_v2"][0]),
            "the genuine source-pinned subinterpreter decoder was substituted",
        )
        original = owner.restore_publication_document(
            archive["path"], archive_bytes,
        )
        genuine_receipt = owner.restore_publication_document(
            evidence["path"], raw,
        )
        require(genuine_receipt == receipt,
                "a genuine producer-owned interpreter receipt was substituted")
        owner.validate_publication_receipt(
            genuine_receipt, relative=archive["path"], document=original,
        )
        require(
            original.get("schema")
            == "rebar-python-re-genuine-subinterpreter-v2-self-oracle"
            and original.get("status") == "PASS"
            and original.get("python") == "3.14.6"
            and original.get("source_path")
            == FROZEN_SOURCE_PINS["subinterpreter_v2"][0]
            and original.get("source_sha256")
            == FROZEN_SOURCE_PINS["subinterpreter_v2"][1]
            and original.get("protocol_path")
            == suite["protocol"]["path"]
            and original.get("protocol_sha256")
            == suite["protocol"]["sha256"]
            and original.get("matrix_sha256") == suite["matrix_sha256"]
            and original.get("case_count") == suite["case_execution_count"]
            and original.get("reference_records_sha256")
            == suite["baseline_records_sha256"]
            and original.get("actual_independent_reference_count") == 2
            and original.get("distinct_reference_processes") is True
            and original.get("actual_interpreters_created")
            == baseline["actual_interpreters_created"]
            and original.get("actual_interpreters_destroyed")
            == baseline["actual_interpreters_closed"]
            and original.get("actual_matching_interpreter_exec_calls")
            == baseline["actual_regex_match_operations"]
            and original.get("actual_aba_case_triples")
            == baseline["actual_case_triples"]
            and original.get("actual_aba_phase_records")
            == baseline["actual_phase_records"]
            and original.get("all_interpreter_teardowns_verified") is True
            and original.get("candidate_status") == "NOT RUN"
            and original.get("candidate_imports") == 0
            and original.get("native_owner_workers") == 0
            and original.get("benchmark_or_timing_executed") is False
            and original.get("performance") == "NOT MEASURED"
            and original.get("holdout") == "NOT ACCESSED",
            "the complete genuine simultaneous-interpreter reference changed",
        )
        require(
            original.get("original_reference") == {
                "independent_reference_count": 2,
                "original_methods": 165,
                "pinned_public_interpreters": owner.PINNED_INTERPRETERS,
                "pinned_public_interpreters_sha256": (
                    owner.PINNED_INTERPRETERS_SHA256
                ),
                "pinned_python": owner.PINNED_PYTHON,
                "pinned_stdlib_re": owner.PINNED_STDLIB_RE,
                "pinned_stdlib_re_sha256": owner.PINNED_STDLIB_RE_SHA256,
                "private_methods": 13,
                "private_waivers": owner.PRIVATE_WAIVERS,
                "public_cases": owner.PUBLIC_CASES,
                "public_cohorts": owner.PUBLIC_COHORTS,
                "public_matrix_sha256": owner.PUBLIC_MATRIX_SHA256,
                "public_method_waivers": [],
                "public_methods": 152,
                "public_protocol_sha256": owner.PUBLIC_PROTOCOL_SHA256,
                "public_real_locale_cases": owner.PUBLIC_REAL_LOCALE_CASES,
                "public_real_locale_transitions": (
                    owner.PUBLIC_REAL_LOCALE_TRANSITIONS
                ),
                "public_reference_independent_roles": 2,
                "public_reference_record_sha256": (
                    owner.PUBLIC_REFERENCE_RECORD_SHA256
                ),
                "public_reference_sha256": owner.PUBLIC_REFERENCE_SHA256,
                "public_source_sha256": owner.PUBLIC_SOURCE_SHA256,
                "public_stimulus_sha256": owner.PUBLIC_STIMULUS_SHA256,
                "reference_sha256": owner.V6_REFERENCE_SHA256,
                "reference_status_vector_sha256": (
                    owner.ORIGINAL_STATUS_VECTOR_SHA256
                ),
            },
            "the exact genuine interpreter V6 and public-reference ancestry changed",
        )
        roles = original.get("reference_roles")
        require(type(roles) is dict
                and set(roles) == {"reference_a", "reference_b"},
                "a genuine simultaneous-interpreter role was omitted")
        actual_pids: list[int] = []
        actual_streams: list[str] = []
        for role in ("reference_a", "reference_b"):
            process = roles[role]
            require(
                type(process) is dict
                and process.get("status") == "PASS"
                and process.get("role") == role
                and process.get("returncode") == 0
                and process.get("signal") is None
                and process.get("timed_out") is False
                and process.get("stdout_complete") is True
                and process.get("stderr_complete") is True
                and type(process.get("pid")) is int
                and process["pid"] > 0,
                "a genuine simultaneous-interpreter process was forged",
            )
            stdout = owner.restore_complete_stream(
                process.get("stdout"),
                label=role + " complete original interpreter stdout",
            )
            stderr = owner.restore_complete_stream(
                process.get("stderr"),
                label=role + " complete original interpreter stderr",
            )
            require(stderr == b"",
                    "a genuine simultaneous-interpreter worker concealed stderr")
            worker = owner.strict_canonical(
                stdout, label=role + " original subinterpreter worker",
            )
            require(worker == process.get("report"),
                    "a complete subinterpreter worker stream was substituted")
            owner.validate_worker_document(
                worker, role, expected_pid=process["pid"],
            )
            actual_pids.append(process["pid"])
            actual_streams.append(hashlib.sha256(stdout).hexdigest())
        require(
            len(set(actual_pids)) == 2
            and sorted(actual_pids) == baseline["reference_process_ids"]
            and actual_streams == baseline["reference_role_stream_sha256"],
            "the genuine subinterpreter process IDs or full streams changed",
        )
        return
    require(receipt.get("schema") == LEGACY_RECEIPT_SCHEMAS.get(suite["id"])
            and receipt.get("baseline_result_status") == "PASS"
            and receipt.get("case_count") == suite["case_execution_count"]
            and receipt.get("matrix_sha256") == suite["matrix_sha256"]
            and receipt.get("baseline_records_sha256")
            == suite["baseline_records_sha256"]
            and receipt.get("baseline_reference_pids") == [82, 83]
            and receipt.get("actual_reference_workers") == 2
            and receipt.get("actual_candidate_workers") == 0
            and receipt.get("actual_candidate_imports") == 0
            and receipt.get("hidden_cases_read") == 0
            and receipt.get("benchmark_files_read") == 0
            and receipt.get("clock_samples") == 0
            and receipt.get("timing_trials_run") == 0
            and receipt.get("report_relative") == archive["path"]
            and receipt.get("report_sha256") == archive["sha256"]
            and receipt.get("report_uncompressed_bytes") == actual["bytes"]
            and receipt.get("report_uncompressed_sha256") == actual["sha256"]
            and receipt.get("report_file_fsync_completed") is True
            and receipt.get("report_directory_fsync_completed") is True,
            "a complete actual pure two-reference baseline receipt changed")


def verify_actual(
    *, source_sha256: str, document_sha256: str,
    explanation_sha256: str,
) -> dict[str, Any]:
    verify_runtime()
    for name, value in (
        ("verifier source", source_sha256),
        ("canonical phase document", document_sha256),
        ("human-readable crosswalk", explanation_sha256),
    ):
        valid_sha256(value, name)
    initial = frozenset({
        SOURCE_RELATIVE, DOCUMENT_RELATIVE, EXPLANATION_RELATIVE,
    })
    source = read_owned(
        SOURCE_RELATIVE, source_sha256, MAX_SOURCE_BYTES, initial,
    )
    explanation = read_owned(
        EXPLANATION_RELATIVE, explanation_sha256,
        MAX_DOCUMENT_BYTES, initial,
    )
    raw = read_owned(
        DOCUMENT_RELATIVE, document_sha256, MAX_DOCUMENT_BYTES, initial,
    )
    document = decode_canonical(raw, DOCUMENT_RELATIVE)
    suites = validate_document(document, require_ready=True)
    actual_paths: set[str] = set(initial)
    _collect_artifacts(document, actual_paths)
    allowed = frozenset(actual_paths)
    source_count = 0
    for suite in suites.values():
        for key in ("source", "recorder", "protocol"):
            item = validate_artifact(suite.get(key), nullable=True)
            if item is not None:
                read_owned(
                    item["path"], item["sha256"],
                    MAX_SOURCE_BYTES, allowed,
                )
                source_count += 1
    for item in document["predecessor_obligation_matrices"]:
        actual = validate_artifact(item)
        require(actual is not None, "a frozen predecessor matrix is mandatory")
        read_owned(actual["path"], actual["sha256"], MAX_SOURCE_BYTES, allowed)
        source_count += 1
    for field in (
        "accounting_protocol", "accounting_manifest", "accounting_verifier",
    ):
        item = validate_artifact(document["original_upstream"].get(field))
        require(item is not None,
                "an independently signed upstream accounting artifact is missing")
        read_owned(
            item["path"], item["sha256"],
            MAX_DOCUMENT_BYTES if field == "accounting_manifest"
            else MAX_SOURCE_BYTES, allowed,
        )
        source_count += 1
    upstream_owner = importlib.import_module(
        "tools.verify_original_cpython_accounting_v1",
    )
    require(os.path.abspath(upstream_owner.__file__)
            == str(ROOT / UPSTREAM_ACCOUNTING_VERIFIER_RELATIVE),
            "the independent complete CPython accounting owner was replaced")
    upstream = upstream_owner.verify(
        UPSTREAM_ACCOUNTING_VERIFIER_SHA256,
        UPSTREAM_ACCOUNTING_MANIFEST_SHA256,
    )
    require(
        type(upstream) is dict
        and upstream.get("status") == "PASS"
        and upstream.get("python") == "3.14.6"
        and upstream.get("all_original_methods") == 165
        and upstream.get("public_methods") == 152
        and upstream.get("private_method_waivers") == 13
        and upstream.get("public_method_waivers") == 0
        and upstream.get("full_method_matrix_sha256")
        == FROZEN_SUITES["original_bounded_v5"][2]
        and upstream.get("public_method_matrix_sha256")
        == "5802606619ee4aad65a1d031259740b003c891de8674a5321d0bf6dbce2b590a"
        and upstream.get("full_resource_v5_reference_sha256")
        == "3a5c300640b4d5207694d474eb231ce6ff7cb11ce6f3a17da0edd2e48fea3916"
        and upstream.get("separate_v6_reference_sha256")
        == "1c0445780b747680ff75ced694a61b43949dc1f7eb81a8e4a8c45cfa9376cebf"
        and upstream.get("v19_reference_sha256")
        == "a2ac2853a6551b9eb95564ee74731c9e7d44998f5ec32ad5aac2259b5b313ad8"
        and upstream.get("v19_record_sha256")
        == FROZEN_SUITES["public_surface_v19"][3]
        and upstream.get("historical_selected_methods") == 146
        and upstream.get("historical_passed") == 144
        and upstream.get("historical_locale_skips") == 2,
        "complete original upstream CPython accounting was forged or conflated",
    )
    for lineage in document["original_upstream"]["lineages"]:
        for key in ("source", "protocol", "reference_report"):
            item = validate_artifact(lineage.get(key), nullable=True)
            if item is not None:
                read_owned(
                    item["path"], item["sha256"],
                    MAX_UNCOMPRESSED_BYTES
                    if key == "reference_report" else MAX_SOURCE_BYTES,
                    allowed,
                )
    for name, suite in suites.items():
        if name not in ("original_bounded_v5", "public_surface_v19"):
            _authenticate_baseline_receipt(suite, allowed)
    broad = suites["public_surface_v19"]
    validator = validate_artifact(broad.get("independent_verifier"))
    protocol = validate_artifact(broad.get("independent_verifier_protocol"))
    require(validator is not None and protocol is not None
            and validator["path"] == V19_VALIDATOR_RELATIVE
            and validator["sha256"] == V19_VALIDATOR_SHA256
            and protocol["path"] == V19_PROTOCOL_RELATIVE
            and protocol["sha256"] == V19_PROTOCOL_SHA256,
            "only the independently frozen V27 producer verifier can decode V19")
    read_owned(validator["path"], validator["sha256"],
               MAX_SOURCE_BYTES, allowed)
    read_owned(protocol["path"], protocol["sha256"],
               MAX_SOURCE_BYTES, allowed)
    require(not any(
        name == "candidates" or name.startswith("candidates.")
        for name in sys.modules
    ), "a candidate imported before the genuine V19 Python reference")
    owner = importlib.import_module(
        "tools.python_re_public_surface_oracle_stage27",
    )
    require(os.path.abspath(owner.__file__)
            == str(ROOT / V19_VALIDATOR_RELATIVE),
            "the genuine producer-owned V19 decoder was substituted")
    read_owned(validator["path"], validator["sha256"],
               MAX_SOURCE_BYTES, allowed)
    reference = owner.authenticate_reference(
        V19_VALIDATOR_SHA256, V19_PROTOCOL_SHA256,
    )
    require(type(reference) is dict
            and reference.get("v19_reference_sha256")
            == broad["baseline"]["report"]["sha256"]
            and reference.get("v19_reference_record_sha256")
            == broad["baseline_records_sha256"]
            and reference.get("cases") == broad["case_execution_count"]
            and reference.get("actual_independent_reference_count") == 2
            and reference.get("fresh_reference_workers_started") == 0
            and reference.get("candidate_imports") == 0
            and reference.get("candidate_audits_read") == 0
            and reference.get("candidate_proofs_read") == 0
            and reference.get("holdout_cases_read") == 0
            and reference.get("performance_fixtures_read") == 0
            and reference.get("benchmark_or_timing_executed") is False,
            "the complete actual strict producer-owned V19 reference changed")
    verify_runtime()
    return {
        "schema": SCHEMA + "-actual-read-only-verification",
        "status": "PASS",
        "python": "3.14.6",
        "goal_sha256": GOAL_SHA256,
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "document_sha256": hashlib.sha256(raw).hexdigest(),
        "explanation_sha256": hashlib.sha256(explanation).hexdigest(),
        "frozen_sources_verified": source_count,
        "suite_count": len(suites),
        "case_execution_denominator": document["denominator"][
            "final_required_case_execution_denominator"
        ],
        "inherited_obligation_count": len(INHERITED_OBLIGATIONS),
        "additional_obligation_count": len(ADDITIONAL_OBLIGATIONS),
        "private_waiver_count": len(PRIVATE_WAIVERS),
        "public_debug_skip_count": 1,
        "broad_v19_decoder": "actual independently frozen stage-27/stage-19 owner",
        "new_candidate_workers": 0,
        "new_reference_workers": 0,
        "clock_samples": 0,
        "hidden_cases_read": 0,
        "performance_files_read": 0,
        "performance": "NOT MEASURED",
        "final_winner_selected": False,
    }


def main(arguments: list[str] | None = None) -> int:
    values = list(sys.argv[1:] if arguments is None else arguments)
    if values == ["--self-test"]:
        document = source_self_test()
    else:
        require(len(values) == 7 and values[0] == "--verify",
                "use --self-test or explicitly pinned read-only --verify")
        pins: dict[str, str] = {}
        for index in (1, 3, 5):
            key = values[index]
            require(key in {
                "--source-sha256", "--document-sha256",
                "--explanation-sha256",
            } and key not in pins,
                    "supply each externally frozen verifier/document hash once")
            pins[key] = values[index + 1]
        require(set(pins) == {
            "--source-sha256", "--document-sha256",
            "--explanation-sha256",
        }, "all three independently frozen completeness hashes are required")
        document = verify_actual(
            source_sha256=pins["--source-sha256"],
            document_sha256=pins["--document-sha256"],
            explanation_sha256=pins["--explanation-sha256"],
        )
    sys.stdout.buffer.write(canonical(document))
    sys.stdout.buffer.flush()
    return 0


if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
