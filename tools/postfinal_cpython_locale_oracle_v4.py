#!/usr/bin/env python3
"""Freeze every genuine public CPython regex test without inventing a pass."""

from __future__ import annotations

import argparse
import ast
import builtins
import contextlib
import copy
import hashlib
import importlib
import importlib.util
import io
import json
import locale
import multiprocessing
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import time
import types
import unittest
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent.parent
PINNED_CPYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
SCHEMA = "rebar-postfinal-cpython-full-public-locale-v4"
SOURCE_RELATIVE = "tools/postfinal_cpython_locale_oracle_v4.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-LOCALE-V4.md"
REPORT_RELATIVE = "oracle/cpython-3.14.6/evidence/postfinal-locale-v4-all.json"
SELF_ORACLE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v4-self-oracle.json"
)
SELF_ORACLE_FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v4-self-oracle-failures.json"
)
FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v4-failures.json"
)
ROLE_REPORT_RELATIVES = {
    role: "oracle/cpython-3.14.6/evidence/postfinal-locale-v4-"
    + role + ".json"
    for role in ("rust", "vm", "zig")
}

TEST_SOURCE_RELATIVE = "oracle/cpython-3.14.6/test_re.py"
TEST_SOURCE_SHA256 = (
    "879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2"
)
CORPUS_SOURCE_RELATIVE = "oracle/cpython-3.14.6/re_tests.py"
CORPUS_SOURCE_SHA256 = (
    "ec04a2b2a77338d20b37d931693c7e588a2896d3c73c7b4b47973e24c13b5aab"
)

# The source distribution and complete extracted support tree were actually
# authenticated independently; neither a generated support shim nor the
# presence of a package in sys.modules can stand in for these real bytes.
UPSTREAM_ARCHIVE = Path("/tmp/rebar-cpython/Python-3.14.6.tar.xz")
UPSTREAM_ARCHIVE_SHA256 = (
    "143b1dddefaec3bd2e21e3b839b34a2b7fb9842272883c576420d605e9f30c63"
)
UPSTREAM_LIB = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-upstream-source/"
    "Python-3.14.6/Lib"
)
UPSTREAM_TEST_INIT_SHA256 = (
    "836cdb388117cf81e78d9fa2a141cca1b14b0179733322e710067749a1b16fe9"
)
UPSTREAM_SUPPORT_INIT_SHA256 = (
    "519f9d36eccf2fda59f78c3480bb4b6e35b2ecb51551f11e0ac03ecbfa503159"
)
UPSTREAM_WARNINGS_HELPER_SHA256 = (
    "fc02de4d91bae3988079e3fb3fec3da96ae467fd548295745c2846af179f3870"
)
OFFICIAL_SUPPORT_TREE_SHA256 = (
    "6cd13337b46bd6a53a32ac0c557da79b0ddd536ac82be885cc57be77e80f1632"
)
OFFICIAL_SUPPORT_MODULES = (
    "__init__.py",
    "_hypothesis_stubs/__init__.py",
    "_hypothesis_stubs/_helpers.py",
    "_hypothesis_stubs/strategies.py",
    "ast_helper.py",
    "asynchat.py",
    "asyncore.py",
    "bytecode_helper.py",
    "channels.py",
    "hashlib_helper.py",
    "hypothesis_helper.py",
    "i18n_helper.py",
    "import_helper.py",
    "logging_helper.py",
    "numbers.py",
    "os_helper.py",
    "pty_helper.py",
    "refleak_helper.py",
    "script_helper.py",
    "smtpd.py",
    "socket_helper.py",
    "strace_helper.py",
    "testcase.py",
    "threading_helper.py",
    "venv.py",
    "warnings_helper.py",
)

# Root alone fills these pins after actually freezing the new source and
# protocol. None is never a success, a guessed fingerprint, or evidence.
SOURCE_SHA256: str | None = None
PROTOCOL_SHA256: str | None = None
METHOD_MATRIX_SHA256: str | None = (
    "5802606619ee4aad65a1d031259740b003c891de8674a5321d0bf6dbce2b590a"
)
REFRESHED_EDGE_PROOF_RELATIVE: str | None = None
REFRESHED_EDGE_PROOF_SHA256: str | None = None
REFRESHED_DEEP_PROOF_RELATIVE: str | None = None
REFRESHED_DEEP_PROOF_SHA256: str | None = None

V3_SOURCE_SHA256 = (
    "28b98c8913ca89ec2ba600484205c3bcb63ae22a86e33d4f7cf3c6f1a68c8a58"
)
V3_PROTOCOL_SHA256 = (
    "a1f77b1628c03d42b9d8e2650c9b501d9be4cec917d765539c91c750154bd6ac"
)
V3_REPORT_SHA256 = (
    "18a011a5ce6e47e52cd02e4cb0812c8f9f7919a069edd7d74e57631623b901b5"
)
CAMPAIGN_SOURCE_SHA256 = (
    "92e397149585ee35ce5d26e984f00d093992471d3e92b929f65dd0386f75b243"
)
CAMPAIGN_PROTOCOL_SHA256 = (
    "dd7e6f80128fb9c8198398755caa178ede0a0ce178fedce2049a7e066be3250c"
)
CAMPAIGN_REPORT_SHA256: dict[str, str | None] = {
    "rust": None,
    "vm": None,
    "zig": None,
}
CAMPAIGN_REPORT_RELATIVES = {
    role: "candidates/evidence/rust-v8-" + role
    + "-postfinal-locale-v7-sealed-campaign.json"
    for role in ("rust", "vm", "zig")
}
CAMPAIGN_STEP_DENOMINATORS = {
    "full-unicode-plane": 4_494_555,
    "frozen-correctness-v2": 8_244,
    "frozen-correctness-v3": 44_084,
    "official-cpython-tests": 146,
    "upstream-public-surface": 190,
    "replacement-and-callback-adversarial": 8_862,
    "deep-replacement-and-callback-adversarial": 11_266,
    "isolated-crash-and-resource-safety": 254,
    "isolated-depth-and-overflow-safety": 348,
    "frozen-cross-family-observability": 479,
}
CAMPAIGN_NATIVE_BOUNDARY_STEPS = (
    "independent-native-boundary-self-oracle",
    "independent-native-boundary-integrity",
    "independent-native-boundary-poison",
    "independent-native-boundary-compatibility",
)

# This is an actual preserved first failure, not a passing campaign. The
# source-only self-test does not open this path or any candidate evidence.
FIRST_CAMPAIGN_FAILURE_RELATIVE = (
    "candidates/evidence/"
    "rust-v8-rust-postfinal-locale-v7-sealed-campaign-first-failure.json"
)
FIRST_CAMPAIGN_FAILURE_SHA256 = (
    "62aba93fa8bdd6df7be93199aea6f58be7b24c095750c520179e96b98084b75a"
)
FIRST_CAMPAIGN_FAILURE_SCHEMA = (
    "rebar-postfinal-campaign-v7-first-current-build-failure-v1"
)
FIRST_CAMPAIGN_FAILURE_PHASE = (
    "candidate-edge-proof-validation-before-first-campaign-stage"
)

ROLES = ("stdlib", "rust", "vm", "zig")
ORIGINAL_CLASS_METHOD_COUNTS = {
    "ReTests": 139,
    "DebugTests": 4,
    "PatternReprTests": 11,
    "ImplementationTest": 9,
    "ExternalTests": 2,
}
PRIVATE_CLASS_WAIVERS = {
    "DebugTests": {
        "methods": 4,
        "reason": (
            "CPython-only textual disassembly of private matching opcodes"
        ),
    },
    "ImplementationTest": {
        "methods": 9,
        "reason": (
            "private CPython regex compiler, _sre, type internals, "
            "and deprecated private implementation modules"
        ),
    },
}

# V3 excluded these real public methods. V4 includes every one. This tuple is
# provenance, never a V4 waiver, replacement, or alternate test.
FORMERLY_WAIVED_PUBLIC_METHODS = (
    "ReTests.test_re_groupref_overflow",
    "ReTests.test_large_search",
    "ReTests.test_large_subn",
    "ReTests.test_search_anchor_at_beginning",
    "ReTests.test_regression_gh94675",
    "ReTests.test_memory_leaks",
)
PUBLIC_METHOD_WAIVERS: tuple[str, ...] = ()

# Exact source-order identities taken from the unchanged pinned CPython file.
# A method renamed, omitted, inserted, or replaced fails source introspection.
PUBLIC_ORIGINAL_METHODS = (
    "ReTests.test_error_is_PatternError_alias",
    "ReTests.test_keep_buffer",
    "ReTests.test_weakref",
    "ReTests.test_search_star_plus",
    "ReTests.test_branching",
    "ReTests.test_basic_re_sub",
    "ReTests.test_bug_449964",
    "ReTests.test_bug_449000",
    "ReTests.test_bug_1661",
    "ReTests.test_bug_3629",
    "ReTests.test_sub_template_numeric_escape",
    "ReTests.test_qualified_re_sub",
    "ReTests.test_misuse_flags",
    "ReTests.test_bug_114660",
    "ReTests.test_symbolic_groups",
    "ReTests.test_symbolic_groups_errors",
    "ReTests.test_symbolic_refs",
    "ReTests.test_symbolic_refs_errors",
    "ReTests.test_re_subn",
    "ReTests.test_re_split",
    "ReTests.test_qualified_re_split",
    "ReTests.test_re_findall",
    "ReTests.test_bug_117612",
    "ReTests.test_re_match",
    "ReTests.test_group",
    "ReTests.test_match_getitem",
    "ReTests.test_re_fullmatch",
    "ReTests.test_re_groupref_exists",
    "ReTests.test_re_groupref_exists_errors",
    "ReTests.test_re_groupref_exists_validation_bug",
    "ReTests.test_re_groupref_overflow",
    "ReTests.test_re_groupref",
    "ReTests.test_groupdict",
    "ReTests.test_expand",
    "ReTests.test_repeat_minmax",
    "ReTests.test_getattr",
    "ReTests.test_special_escapes",
    "ReTests.test_other_escapes",
    "ReTests.test_named_unicode_escapes",
    "ReTests.test_word_boundaries",
    "ReTests.test_bigcharset",
    "ReTests.test_big_codesize",
    "ReTests.test_anyall",
    "ReTests.test_lookahead",
    "ReTests.test_lookbehind",
    "ReTests.test_ignore_case",
    "ReTests.test_ignore_case_set",
    "ReTests.test_ignore_case_range",
    "ReTests.test_category",
    "ReTests.test_not_literal",
    "ReTests.test_possible_set_operations",
    "ReTests.test_search_coverage",
    "ReTests.test_re_escape",
    "ReTests.test_re_escape_bytes",
    "ReTests.test_re_escape_non_ascii",
    "ReTests.test_re_escape_non_ascii_bytes",
    "ReTests.test_pickling",
    "ReTests.test_copying",
    "ReTests.test_constants",
    "ReTests.test_flags",
    "ReTests.test_sre_character_literals",
    "ReTests.test_sre_character_class_literals",
    "ReTests.test_sre_byte_literals",
    "ReTests.test_sre_byte_class_literals",
    "ReTests.test_character_set_errors",
    "ReTests.test_bug_113254",
    "ReTests.test_bug_527371",
    "ReTests.test_bug_418626",
    "ReTests.test_bug_612074",
    "ReTests.test_stack_overflow",
    "ReTests.test_nothing_to_repeat",
    "ReTests.test_multiple_repeat",
    "ReTests.test_unlimited_zero_width_repeat",
    "ReTests.test_scanner",
    "ReTests.test_bug_448951",
    "ReTests.test_bug_725106",
    "ReTests.test_bug_725149",
    "ReTests.test_bug_764548",
    "ReTests.test_finditer",
    "ReTests.test_bug_926075",
    "ReTests.test_bug_931848",
    "ReTests.test_bug_581080",
    "ReTests.test_bug_817234",
    "ReTests.test_bug_6561",
    "ReTests.test_empty_array",
    "ReTests.test_inline_flags",
    "ReTests.test_dollar_matches_twice",
    "ReTests.test_bytes_str_mixing",
    "ReTests.test_ascii_and_unicode_flag",
    "ReTests.test_locale_flag",
    "ReTests.test_scoped_flags",
    "ReTests.test_ignore_spaces",
    "ReTests.test_comments",
    "ReTests.test_bug_6509",
    "ReTests.test_search_dot_unicode",
    "ReTests.test_compile",
    "ReTests.test_large_search",
    "ReTests.test_large_subn",
    "ReTests.test_bug_16688",
    "ReTests.test_repeat_minmax_overflow",
    "ReTests.test_look_behind_overflow",
    "ReTests.test_backref_group_name_in_exception",
    "ReTests.test_group_name_in_exception",
    "ReTests.test_issue17998",
    "ReTests.test_match_repr",
    "ReTests.test_zerowidth",
    "ReTests.test_bug_2537",
    "ReTests.test_keyword_parameters",
    "ReTests.test_bug_20998",
    "ReTests.test_locale_caching",
    "ReTests.test_locale_compiled",
    "ReTests.test_error",
    "ReTests.test_misc_errors",
    "ReTests.test_enum",
    "ReTests.test_pattern_compare",
    "ReTests.test_pattern_compare_bytes",
    "ReTests.test_bug_29444",
    "ReTests.test_bug_34294",
    "ReTests.test_MARK_PUSH_macro_bug",
    "ReTests.test_MIN_UNTIL_mark_bug",
    "ReTests.test_REPEAT_ONE_mark_bug",
    "ReTests.test_MIN_REPEAT_ONE_mark_bug",
    "ReTests.test_ASSERT_NOT_mark_bug",
    "ReTests.test_bug_40736",
    "ReTests.test_search_anchor_at_beginning",
    "ReTests.test_possessive_quantifiers",
    "ReTests.test_fullmatch_possessive_quantifiers",
    "ReTests.test_findall_possessive_quantifiers",
    "ReTests.test_atomic_grouping",
    "ReTests.test_fullmatch_atomic_grouping",
    "ReTests.test_findall_atomic_grouping",
    "ReTests.test_bug_gh91616",
    "ReTests.test_bug_gh100061",
    "ReTests.test_bug_gh101955",
    "ReTests.test_regression_gh94675",
    "ReTests.test_fail",
    "ReTests.test_character_set_any",
    "ReTests.test_character_set_none",
    "ReTests.test_memory_leaks",
    "PatternReprTests.test_without_flags",
    "PatternReprTests.test_single_flag",
    "PatternReprTests.test_multiple_flags",
    "PatternReprTests.test_unicode_flag",
    "PatternReprTests.test_inline_flags",
    "PatternReprTests.test_unknown_flags",
    "PatternReprTests.test_bytes",
    "PatternReprTests.test_locale",
    "PatternReprTests.test_quotes",
    "PatternReprTests.test_long_pattern",
    "PatternReprTests.test_flags_repr",
    "ExternalTests.test_re_benchmarks",
    "ExternalTests.test_re_tests",
)
PRIVATE_ORIGINAL_METHODS = (
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

CORPUS_INITIAL_CASES = 400
CORPUS_EXTENSION_CASES = 3
CORPUS_CASES = CORPUS_INITIAL_CASES + CORPUS_EXTENSION_CASES
EXTERNAL_FIXTURE_ASSERTION_CASES = 11
ORIGINAL_METHODS = 165
PUBLIC_METHODS = 152
PRIVATE_METHODS = 13
REQUIRED_LOCALE_METHODS = frozenset({
    "ReTests.test_locale_caching",
    "ReTests.test_locale_compiled",
})
OUTCOME_STATUSES = frozenset({
    "PASS", "SKIP", "FAIL", "ERROR", "TIMEOUT", "CRASH",
})
MAX_FROZEN_SOURCE_BYTES = 1_048_576
MAX_UPSTREAM_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_EVIDENCE_BYTES = 32 * 1024 * 1024
MAX_WORKER_OUTPUT_BYTES = 8 * 1024 * 1024
MAX_FAILURE_STREAM_PREVIEW_BYTES = 65_536
CONFIGURED_OFFICIAL_MEMORY_BYTES = 40 * 1024**3
REQUIRED_OFFICIAL_SUBN_MEMORY_BYTES = 18 * 2**31


class OfficialV4Error(AssertionError):
    """A real original upstream obligation cannot honestly be qualified."""


class OfficialV4WorkerFailure(OfficialV4Error):
    """Preserve an actual failed isolated role rather than inventing records."""

    def __init__(self, role: str, message: str, details: Mapping[str, Any]):
        super().__init__(message)
        self.role = role
        self.details = dict(details)


def require(condition: Any, message: str) -> None:
    if not condition:
        raise OfficialV4Error(message)


def is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def verify_runtime() -> None:
    require(
        tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.implementation.name == "cpython"
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and Path(sys.executable).resolve() == PINNED_CPYTHON.resolve(),
        "the exact pinned, isolated, bytecode-free CPython 3.14.6 is required",
    )
    forbidden = [
        name for name, module in sys.modules.items()
        if module is not None
        and (
            name == "rebar"
            or name.startswith("rebar.")
            or name == "candidates"
            or name.startswith("candidates.")
        )
    ]
    require(not forbidden, "a candidate escaped into the source-only controller")
    _validate_preloaded_support(sys.modules)


def _validate_preloaded_support(modules: Mapping[str, Any]) -> None:
    """Reject ModuleType shims without importing or assembling test support."""
    for name in ("test", "test.support", "test.support.warnings_helper"):
        module = modules.get(name)
        if module is None:
            continue
        specification = getattr(module, "__spec__", None)
        origin = getattr(specification, "origin", None)
        actual_file = getattr(module, "__file__", None)
        require(
            isinstance(origin, str)
            and isinstance(actual_file, str)
            and Path(origin).resolve() == Path(actual_file).resolve()
            and Path(actual_file).resolve().is_relative_to(
                (UPSTREAM_LIB / "test").resolve()
            ),
            "a fabricated or unauthenticated official test.support shim is forbidden",
        )
    support = modules.get("test.support")
    if support is not None:
        for name in ("bigmemtest", "requires_resource"):
            function = getattr(support, name, None)
            require(
                callable(function)
                and getattr(function, "__module__", None) == "test.support",
                "an original upstream resource decorator was replaced: " + name,
            )


def _read_bounded_regular(path: Path, maximum: int, label: str) -> bytes:
    require(maximum > 0, "a genuine source-reader bound is required")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise OfficialV4Error(
            "the genuine authenticated upstream source is unavailable: " + label
        ) from error
    try:
        metadata = os.fstat(descriptor)
        require(
            stat.S_ISREG(metadata.st_mode)
            and 0 < metadata.st_size <= maximum,
            "an authenticated upstream input is not one bounded regular file: "
            + label,
        )
        chunks: list[bytes] = []
        count = 0
        while True:
            chunk = os.read(descriptor, 65_536)
            if not chunk:
                break
            count += len(chunk)
            require(count <= maximum,
                    "an authenticated upstream input exceeded its bound: " + label)
            chunks.append(chunk)
    finally:
        os.close(descriptor)
    source = b"".join(chunks)
    require(len(source) == metadata.st_size,
            "an authenticated upstream input changed during reading: " + label)
    return source


def read_pinned_source(relative: str, expected_sha256: str) -> bytes:
    allowed = {
        TEST_SOURCE_RELATIVE: TEST_SOURCE_SHA256,
        CORPUS_SOURCE_RELATIVE: CORPUS_SOURCE_SHA256,
    }
    require(
        relative in allowed
        and allowed[relative] == expected_sha256
        and is_sha256(expected_sha256),
        "only the two unchanged real official Python source files may be read",
    )
    source = _read_bounded_regular(
        ROOT / relative, MAX_FROZEN_SOURCE_BYTES, relative,
    )
    require(
        hashlib.sha256(source).hexdigest() == expected_sha256,
        "the pinned original upstream source changed: " + relative,
    )
    return source


def authenticate_upstream_support() -> dict[str, Any]:
    """Independently authenticate the actual archive and all 26 support files."""
    archive = _read_bounded_regular(
        UPSTREAM_ARCHIVE, MAX_UPSTREAM_ARCHIVE_BYTES,
        "official CPython 3.14.6 source archive",
    )
    require(
        hashlib.sha256(archive).hexdigest() == UPSTREAM_ARCHIVE_SHA256,
        "the original independently authenticated CPython archive changed",
    )
    del archive
    root = UPSTREAM_LIB / "test"
    expected_files = (
        (root / "__init__.py", UPSTREAM_TEST_INIT_SHA256),
        (root / "test_re.py", TEST_SOURCE_SHA256),
        (root / "re_tests.py", CORPUS_SOURCE_SHA256),
        (root / "support" / "__init__.py", UPSTREAM_SUPPORT_INIT_SHA256),
        (root / "support" / "warnings_helper.py",
         UPSTREAM_WARNINGS_HELPER_SHA256),
    )
    for path, expected in expected_files:
        actual = _read_bounded_regular(
            path, MAX_FROZEN_SOURCE_BYTES,
            "original upstream " + path.relative_to(UPSTREAM_LIB).as_posix(),
        )
        require(
            hashlib.sha256(actual).hexdigest() == expected,
            "an authentic upstream test/support module was replaced: "
            + path.relative_to(UPSTREAM_LIB).as_posix(),
        )
    support = root / "support"
    files = sorted(
        (path for path in support.rglob("*.py") if path.is_file()),
        key=lambda path: path.relative_to(support).as_posix(),
    )
    names = tuple(path.relative_to(support).as_posix() for path in files)
    require(
        names == OFFICIAL_SUPPORT_MODULES and len(files) == 26,
        "the genuine complete 26-module upstream support tree was replaced",
    )
    fingerprint = hashlib.sha256()
    for path in files:
        relative = path.relative_to(support).as_posix()
        source = _read_bounded_regular(
            path, MAX_FROZEN_SOURCE_BYTES,
            "original upstream test/support/" + relative,
        )
        fingerprint.update(relative.encode("utf-8"))
        fingerprint.update(b"\x00")
        fingerprint.update(source)
        fingerprint.update(b"\x00")
    require(
        fingerprint.hexdigest() == OFFICIAL_SUPPORT_TREE_SHA256,
        "the authenticated complete official test.support tree changed",
    )
    return {
        "upstream_archive_path": str(UPSTREAM_ARCHIVE),
        "upstream_archive_sha256": UPSTREAM_ARCHIVE_SHA256,
        "upstream_test_package_path": str(root),
        "official_support_tree_sha256": OFFICIAL_SUPPORT_TREE_SHA256,
        "official_support_module_count": len(files),
        "official_support_shim_used": False,
        "official_test_source_rewritten": False,
        "test_source_sha256": TEST_SOURCE_SHA256,
        "corpus_source_sha256": CORPUS_SOURCE_SHA256,
        "support_init_sha256": UPSTREAM_SUPPORT_INIT_SHA256,
        "warnings_helper_sha256": UPSTREAM_WARNINGS_HELPER_SHA256,
    }


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _call_name(node.value)
        return prefix + "." + node.attr if prefix else node.attr
    return ""


def _decorator(
    method: ast.FunctionDef | ast.AsyncFunctionDef,
    name: str,
) -> ast.Call:
    found = [
        item for item in method.decorator_list
        if isinstance(item, ast.Call) and _call_name(item.func) == name
    ]
    require(len(found) == 1,
            "an exact original resource decorator is missing: " + name)
    return found[0]


def _official_integer_expression(node: ast.AST) -> int:
    if isinstance(node, ast.Constant) and type(node.value) is int:
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return (
            _official_integer_expression(node.left)
            + _official_integer_expression(node.right)
        )
    raise OfficialV4Error("an original constant memory expression was replaced")


def _validate_resource_requirements(
    methods: Mapping[str, ast.FunctionDef | ast.AsyncFunctionDef],
) -> dict[str, dict[str, Any]]:
    requirements: dict[str, dict[str, Any]] = {}
    for method_name, memory_use in (
        ("ReTests.test_large_search", 1),
        ("ReTests.test_large_subn", 18),
    ):
        node = methods[method_name]
        decorator = _decorator(node, "bigmemtest")
        keywords = {item.arg: item.value for item in decorator.keywords}
        require(
            set(keywords) == {"size", "memuse"}
            and isinstance(keywords["size"], ast.Name)
            and keywords["size"].id == "_2G"
            and _official_integer_expression(keywords["memuse"]) == memory_use,
            "an official two-gibibyte method was weakened: " + method_name,
        )
        requirements[method_name] = {
            "kind": "original-bigmemtest",
            "size_expression": "_2G",
            "size_bytes": 2**31,
            "memory_expression": ast.unparse(keywords["memuse"]),
            "declared_memory_multiplier": memory_use,
            "declared_memory_bytes": (2**31) * memory_use,
            "is_actual_official_method": True,
            "is_companion_control": False,
        }

    name = "ReTests.test_search_anchor_at_beginning"
    anchor = methods[name]
    decorator = _decorator(anchor, "requires_resource")
    require(
        len(decorator.args) == 1
        and isinstance(decorator.args[0], ast.Constant)
        and decorator.args[0].value == "cpu"
        and any(isinstance(item, ast.Name) and item.id == "Stopwatch"
                for item in ast.walk(anchor))
        and any(
            isinstance(item, ast.BinOp)
            and isinstance(item.op, ast.Pow)
            and isinstance(item.left, ast.Constant)
            and item.left.value == 10
            and isinstance(item.right, ast.Constant)
            and item.right.value == 7
            for item in ast.walk(anchor)
        )
        and any(
            isinstance(item, ast.Call)
            and _call_name(item.func) == "self.assertLess"
            and len(item.args) == 2
            and isinstance(item.args[1], ast.Constant)
            and item.args[1].value == 0.1
            for item in ast.walk(anchor)
        ),
        "the exact original CPU resource, input, Stopwatch, or limit changed",
    )
    requirements[name] = {
        "kind": "original-cpu-resource-and-stopwatch",
        "required_resource": "cpu",
        "original_subject_characters": 10**7,
        "original_upper_bound_seconds": 0.1,
        "is_actual_official_method": True,
        "is_companion_control": False,
    }

    name = "ReTests.test_regression_gh94675"
    process = methods[name]
    decorator = _decorator(process, "unittest.skipIf")
    require(
        len(decorator.args) >= 1
        and ast.unparse(decorator.args[0]) == "multiprocessing is None"
        and any(
            isinstance(item, ast.Call)
            and _call_name(item.func) == "multiprocessing.Process"
            for item in ast.walk(process)
        )
        and any(
            isinstance(item, ast.Name) and item.id == "SHORT_TIMEOUT"
            for item in ast.walk(process)
        ),
        "the original multiprocessing subprocess or real timeout was changed",
    )
    requirements[name] = {
        "kind": "original-multiprocessing-regression",
        "required_extension": "_multiprocessing",
        "required_timeout": "test.support.SHORT_TIMEOUT",
        "is_actual_official_method": True,
        "is_companion_control": False,
    }

    name = "ReTests.test_re_groupref_overflow"
    overflow = methods[name]
    require(
        any(
            isinstance(item, ast.ImportFrom)
            and item.module == "re._constants"
            and any(alias.name == "MAXGROUPS" for alias in item.names)
            for item in ast.walk(overflow)
        ),
        "the real public method no longer imports re._constants.MAXGROUPS",
    )
    requirements[name] = {
        "kind": "original-public-overflow-with-real-private-constant-import",
        "required_import": "re._constants.MAXGROUPS",
        "candidate_stdlib_delegation_allowed": False,
        "is_actual_official_method": True,
        "is_companion_control": False,
    }

    name = "ReTests.test_memory_leaks"
    leaks = methods[name]
    decorator = _decorator(leaks, "unittest.skipUnless")
    require(
        len(decorator.args) >= 2
        and ast.unparse(decorator.args[0])
        == "hasattr(re.Pattern, '_fail_after')"
        and isinstance(decorator.args[1], ast.Constant)
        and decorator.args[1].value == "requires debug build",
        "the exact official debug-only memory-leak condition was changed",
    )
    requirements[name] = {
        "kind": "original-public-method-with-private-debug-build-condition",
        "required_debug_attribute": "re.Pattern._fail_after",
        "baseline_release_outcome_if_attribute_absent": "SKIP",
        "a_skip_qualifies_universal_compatibility": False,
        "is_actual_official_method": True,
        "is_companion_control": False,
    }
    require(
        tuple(requirements) == (
            "ReTests.test_large_search",
            "ReTests.test_large_subn",
            "ReTests.test_search_anchor_at_beginning",
            "ReTests.test_regression_gh94675",
            "ReTests.test_re_groupref_overflow",
            "ReTests.test_memory_leaks",
        )
        and set(requirements) == set(FORMERLY_WAIVED_PUBLIC_METHODS),
        "an original formerly omitted public resource method disappeared",
    )
    return requirements


def _introspect_test_source(source: bytes) -> dict[str, Any]:
    try:
        tree = ast.parse(source, filename=TEST_SOURCE_RELATIVE)
    except (SyntaxError, TypeError, ValueError) as error:
        raise OfficialV4Error("the unchanged upstream test is not valid Python") from error
    classes = {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.ClassDef)
        and node.name in ORIGINAL_CLASS_METHOD_COUNTS
    }
    require(
        set(classes) == set(ORIGINAL_CLASS_METHOD_COUNTS),
        "an original official test class was omitted or replaced",
    )
    require(
        sum(
            1 for node in tree.body
            if isinstance(node, ast.Import)
            and any(alias.name == "re" and alias.asname is None
                    for alias in node.names)
        ) == 1
        and sum(
            1 for node in tree.body
            if isinstance(node, ast.ImportFrom)
            and node.module == "re"
            and any(alias.name == "Scanner" and alias.asname is None
                    for alias in node.names)
        ) == 1,
        "the original `import re` or `from re import Scanner` was rewritten",
    )
    records: list[dict[str, Any]] = []
    method_nodes: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
    class_counts: dict[str, int] = {}
    for class_node in tree.body:
        if not isinstance(class_node, ast.ClassDef):
            continue
        if class_node.name not in ORIGINAL_CLASS_METHOD_COUNTS:
            continue
        actual = [
            node for node in class_node.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
        ]
        class_counts[class_node.name] = len(actual)
        for node in actual:
            identity = class_node.name + "." + node.name
            require(identity not in method_nodes,
                    "an original official method identity was duplicated")
            method_nodes[identity] = node
            scope = (
                "named-private-class-waiver"
                if class_node.name in PRIVATE_CLASS_WAIVERS
                else "required-original-public-method"
            )
            records.append({
                "test": identity,
                "class": class_node.name,
                "scope": scope,
                "source_line": node.lineno,
                "source_ast_sha256": hashlib.sha256(
                    ast.dump(node, include_attributes=False).encode("utf-8")
                ).hexdigest(),
                "former_public_waiver": identity in FORMERLY_WAIVED_PUBLIC_METHODS,
                "actual_upstream_source": TEST_SOURCE_RELATIVE,
            })
    require(
        class_counts == ORIGINAL_CLASS_METHOD_COUNTS,
        "the actual official five-class method denominators changed",
    )
    public = tuple(
        record["test"] for record in records
        if record["scope"] == "required-original-public-method"
    )
    private = tuple(
        record["test"] for record in records
        if record["scope"] == "named-private-class-waiver"
    )
    require(
        len(records) == ORIGINAL_METHODS
        and len(public) == PUBLIC_METHODS
        and len(private) == PRIVATE_METHODS
        and public == PUBLIC_ORIGINAL_METHODS
        and private == PRIVATE_ORIGINAL_METHODS
        and not PUBLIC_METHOD_WAIVERS
        and len(set(public)) == PUBLIC_METHODS
        and len(set(private)) == PRIVATE_METHODS
        and not (set(public) & set(private)),
        "V4 must retain all 152 real public methods and only 13 private methods",
    )
    debug = classes["DebugTests"]
    require(
        any(_call_name(item) == "cpython_only" for item in debug.decorator_list),
        "the four genuinely private CPython-only debug tests were changed",
    )
    imports = [
        node for node in tree.body
        if isinstance(node, ast.ImportFrom) and node.module == "test.support"
    ]
    require(len(imports) == 1,
            "the real upstream test.support import was replaced or hidden")
    actual_support = frozenset(item.name for item in imports[0].names)
    require(
        actual_support == frozenset({
            "gc_collect", "bigmemtest", "_2G", "cpython_only",
            "captured_stdout", "check_disallow_instantiation",
            "linked_to_musl", "warnings_helper", "SHORT_TIMEOUT",
            "Stopwatch", "requires_resource",
        }),
        "the real upstream test.support requirements were weakened",
    )
    corpus_method = method_nodes["ExternalTests.test_re_tests"]
    require(
        any(
            isinstance(node, ast.ImportFrom)
            and node.module == "test.re_tests"
            and {item.name for item in node.names}
            == {"tests", "FAIL", "SYNTAX_ERROR"}
            for node in ast.walk(corpus_method)
        ),
        "the unchanged actual upstream correctness corpus was replaced",
    )
    official_fixture_assertions = method_nodes["ExternalTests.test_re_benchmarks"]
    require(
        any(
            isinstance(node, ast.ImportFrom)
            and node.module == "test.re_tests"
            and any(item.name == "benchmarks" for item in node.names)
            for node in ast.walk(official_fixture_assertions)
        ),
        "the real upstream external-fixture correctness method was omitted",
    )
    require(
        REQUIRED_LOCALE_METHODS <= set(public),
        "both genuine original official locale methods are mandatory",
    )
    requirements = _validate_resource_requirements(method_nodes)
    return {
        "class_method_counts": class_counts,
        "all_original_methods": ORIGINAL_METHODS,
        "public_original_methods": PUBLIC_METHODS,
        "private_original_methods": PRIVATE_METHODS,
        "public_method_waivers": list(PUBLIC_METHOD_WAIVERS),
        "named_private_class_waivers": PRIVATE_CLASS_WAIVERS,
        "formerly_waived_public_methods_now_required": list(
            FORMERLY_WAIVED_PUBLIC_METHODS
        ),
        "required_locale_methods": sorted(REQUIRED_LOCALE_METHODS),
        "official_test_support_imports": sorted(actual_support),
        "official_resource_requirements": requirements,
        "original_method_records": records,
        "public_method_matrix": [
            record for record in records
            if record["scope"] == "required-original-public-method"
        ],
    }


def _introspect_corpus_source(source: bytes) -> dict[str, Any]:
    try:
        tree = ast.parse(source, filename=CORPUS_SOURCE_RELATIVE)
    except (SyntaxError, TypeError, ValueError) as error:
        raise OfficialV4Error("the unchanged official corpus is not valid Python") from error
    assignments = [
        node for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "tests"
                for target in node.targets)
    ]
    require(
        len(assignments) == 1
        and isinstance(assignments[0].value, (ast.List, ast.Tuple)),
        "the actual upstream tests corpus was replaced or assigned twice",
    )
    initial = assignments[0].value.elts
    extensions: list[ast.AST] = []
    for node in tree.body:
        if not isinstance(node, ast.Expr) or not isinstance(node.value, ast.Call):
            continue
        call = node.value
        if not isinstance(call.func, ast.Attribute):
            continue
        if not isinstance(call.func.value, ast.Name):
            continue
        if call.func.value.id != "tests":
            continue
        require(
            call.func.attr == "extend"
            and len(call.args) == 1
            and not call.keywords
            and isinstance(call.args[0], (ast.List, ast.Tuple)),
            "the actual official corpus gained an unsealed dynamic mutation",
        )
        extensions.extend(call.args[0].elts)
    require(
        len(initial) == CORPUS_INITIAL_CASES
        and len(extensions) == CORPUS_EXTENSION_CASES
        and len(initial) + len(extensions) == CORPUS_CASES
        and all(
            isinstance(item, (ast.List, ast.Tuple))
            and len(item.elts) in (3, 5)
            for item in [*initial, *extensions]
        ),
        "the 403 real upstream cases must include all three locale extensions",
    )
    assertion_fixtures = [
        node for node in tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "benchmarks"
            for target in node.targets
        )
    ]
    require(
        len(assertion_fixtures) == 1
        and isinstance(assertion_fixtures[0].value, (ast.List, ast.Tuple))
        and len(assertion_fixtures[0].value.elts)
        == EXTERNAL_FIXTURE_ASSERTION_CASES
        and all(
            isinstance(item, (ast.List, ast.Tuple)) and len(item.elts) == 2
            for item in assertion_fixtures[0].value.elts
        ),
        "the original eleven upstream external correctness assertions changed",
    )
    return {
        "initial_case_count": len(initial),
        "actual_extended_case_count": len(extensions),
        "actual_upstream_corpus_cases": len(initial) + len(extensions),
        "actual_external_fixture_assertion_cases": (
            len(assertion_fixtures[0].value.elts)
        ),
        "corpus_ast_sha256": hashlib.sha256(
            ast.dump(tree, include_attributes=False).encode("utf-8")
        ).hexdigest(),
    }


def introspect_official_sources() -> dict[str, Any]:
    verify_runtime()
    test_source = read_pinned_source(TEST_SOURCE_RELATIVE, TEST_SOURCE_SHA256)
    corpus_source = read_pinned_source(
        CORPUS_SOURCE_RELATIVE, CORPUS_SOURCE_SHA256,
    )
    official = _introspect_test_source(test_source)
    corpus = _introspect_corpus_source(corpus_source)
    method_matrix = official["public_method_matrix"]
    matrix_sha256 = digest(method_matrix)
    require(
        METHOD_MATRIX_SHA256 is None or matrix_sha256 == METHOD_MATRIX_SHA256,
        "the frozen complete 152-method official matrix was changed",
    )
    return {
        "schema": SCHEMA + "-source-introspection",
        "python": "3.14.6",
        "test_source_path": TEST_SOURCE_RELATIVE,
        "test_source_sha256": TEST_SOURCE_SHA256,
        "corpus_source_path": CORPUS_SOURCE_RELATIVE,
        "corpus_source_sha256": CORPUS_SOURCE_SHA256,
        "public_method_matrix_sha256": matrix_sha256,
        **official,
        **corpus,
    }


def assess_role_records(
    role: str,
    records: Any,
    matrix: list[dict[str, Any]],
) -> dict[str, Any]:
    require(role in ROLES, "an unapproved original official test role was used")
    require(
        isinstance(records, list)
        and len(records) == PUBLIC_METHODS
        and isinstance(matrix, list)
        and len(matrix) == PUBLIC_METHODS,
        "every role must preserve all 152 actual official method records",
    )
    counts = {status: 0 for status in sorted(OUTCOME_STATUSES)}
    seen: set[str] = set()
    named_private_debug_skips = 0
    for expected, actual in zip(matrix, records, strict=True):
        require(isinstance(actual, Mapping),
                "an actual original method observation was not recorded")
        identity = expected["test"]
        require(
            actual.get("test") == identity
            and identity not in seen
            and actual.get("source_ast_sha256")
            == expected["source_ast_sha256"],
            "an original official result was missing, reordered, or substituted",
        )
        status = actual.get("status")
        require(status in OUTCOME_STATUSES,
                "an actual official PASS/SKIP/failure status was concealed")
        if status == "SKIP":
            require(
                isinstance(actual.get("reason"), str)
                and bool(actual["reason"].strip()),
                "an original official skip must retain its actual reason",
            )
            if (
                identity == "ReTests.test_memory_leaks"
                and actual["reason"] == "requires debug build"
                and actual.get("skip_kind") == "named-private-debug-condition"
            ):
                named_private_debug_skips += 1
        if status in {"FAIL", "ERROR", "TIMEOUT", "CRASH"}:
            require(
                isinstance(actual.get("reason"), str)
                and bool(actual["reason"].strip()),
                "an original official failure must retain its actual reason",
            )
        seen.add(identity)
        counts[status] += 1
    require(seen == set(PUBLIC_ORIGINAL_METHODS),
            "the actual complete original method identities do not match")
    failing = sum(counts[item] for item in ("FAIL", "ERROR", "TIMEOUT", "CRASH"))
    unexplained_skips = counts["SKIP"] - named_private_debug_skips
    applicable = PUBLIC_METHODS - named_private_debug_skips
    verdict = (
        "FAIL" if failing
        else "BLOCKED" if unexplained_skips
        else "PASS" if counts["PASS"] == applicable
        else "BLOCKED"
    )
    return {
        "role": role,
        "methods": PUBLIC_METHODS,
        "applicable": applicable,
        "passed": counts["PASS"],
        "skipped": counts["SKIP"],
        "named_private_debug_skips": named_private_debug_skips,
        "unexplained_skips": unexplained_skips,
        "failed": counts["FAIL"],
        "errors": counts["ERROR"],
        "timeouts": counts["TIMEOUT"],
        "crashes": counts["CRASH"],
        "status": verdict,
        "debug_build_coverage": (
            "NOT RUN" if named_private_debug_skips else "PASS"
        ),
        "records_sha256": digest(records),
        "record_count": len(records),
    }


def published_pins(
    source_sha256: str | None = None,
    protocol_sha256: str | None = None,
) -> dict[str, str]:
    candidates: dict[str, str | None] = {
        "v4_source": source_sha256 if source_sha256 is not None else SOURCE_SHA256,
        "v4_protocol": (
            protocol_sha256 if protocol_sha256 is not None else PROTOCOL_SHA256
        ),
        "official_upstream_archive": UPSTREAM_ARCHIVE_SHA256,
        "official_support_tree": OFFICIAL_SUPPORT_TREE_SHA256,
        "refreshed_edge_proof": REFRESHED_EDGE_PROOF_SHA256,
        "refreshed_deep_proof": REFRESHED_DEEP_PROOF_SHA256,
        "v7_campaign_rust": CAMPAIGN_REPORT_SHA256["rust"],
        "v7_campaign_vm": CAMPAIGN_REPORT_SHA256["vm"],
        "v7_campaign_zig": CAMPAIGN_REPORT_SHA256["zig"],
    }
    require(
        METHOD_MATRIX_SHA256 is not None and is_sha256(METHOD_MATRIX_SHA256),
        "BLOCKED: the exact genuine 152-method matrix is not published",
    )
    for name, fingerprint in candidates.items():
        require(
            is_sha256(fingerprint),
            "BLOCKED: the genuine " + name + " fingerprint is not published",
        )
    require(
        all(
            isinstance(path, str)
            and path
            and not Path(path).is_absolute()
            and ".." not in Path(path).parts
            for path in (
                REFRESHED_EDGE_PROOF_RELATIVE,
                REFRESHED_DEEP_PROOF_RELATIVE,
            )
        ),
        "BLOCKED: a refreshed genuine current-build edge or deep path is missing",
    )
    values = {key: str(value) for key, value in candidates.items()}
    require(len(values) == len(set(values.values())),
            "a distinct genuine prerequisite was replaced by another fingerprint")
    return values


def validate_official_report(
    document: Any,
    matrix: list[dict[str, Any]],
) -> dict[str, Any]:
    require(isinstance(document, Mapping),
            "a complete actual four-role upstream report is required")
    pins = published_pins(
        document.get("source_sha256"), document.get("protocol_sha256"),
    )
    for path, expected in (
        (SOURCE_RELATIVE, pins["v4_source"]),
        (PROTOCOL_RELATIVE, pins["v4_protocol"]),
    ):
        actual = _read_bounded_regular(
            ROOT / path, MAX_FROZEN_SOURCE_BYTES, path,
        )
        require(
            hashlib.sha256(actual).hexdigest() == expected,
            "the frozen V4 controller or protocol changed after production",
        )
    require(
        document.get("schema") == SCHEMA
        and document.get("source_path") == SOURCE_RELATIVE
        and document.get("source_sha256") == pins["v4_source"]
        and document.get("protocol_path") == PROTOCOL_RELATIVE
        and document.get("protocol_sha256") == pins["v4_protocol"]
        and document.get("python") == "3.14.6"
        and document.get("test_source_sha256") == TEST_SOURCE_SHA256
        and document.get("corpus_source_sha256") == CORPUS_SOURCE_SHA256
        and document.get("upstream_archive_sha256") == UPSTREAM_ARCHIVE_SHA256
        and document.get("official_support_tree_sha256")
        == OFFICIAL_SUPPORT_TREE_SHA256
        and document.get("official_support_module_count")
        == len(OFFICIAL_SUPPORT_MODULES)
        and document.get("public_method_matrix_sha256") == METHOD_MATRIX_SHA256
        and document.get("all_original_methods") == ORIGINAL_METHODS
        and document.get("public_original_methods") == PUBLIC_METHODS
        and document.get("private_original_methods") == PRIVATE_METHODS
        and document.get("actual_upstream_corpus_cases") == CORPUS_CASES
        and document.get("actual_external_fixture_assertion_cases")
        == EXTERNAL_FIXTURE_ASSERTION_CASES
        and document.get("public_method_waivers") == []
        and document.get("synthetic") is not True,
        "a complete immutable original CPython V4 report was forged or weakened",
    )
    private = document.get("named_private_class_waivers")
    require(private == PRIVATE_CLASS_WAIVERS,
            "only the two exact private upstream classes can be excluded")
    roles = document.get("roles")
    require(isinstance(roles, Mapping) and set(roles) == set(ROLES),
            "the exact Python, Rust, C, and Zig original roles are required")
    summaries: dict[str, Any] = {}
    for role in ROLES:
        evidence = roles[role]
        require(isinstance(evidence, Mapping),
                "a complete genuine upstream role record is required: " + role)
        summaries[role] = _validate_role_evidence(role, evidence, matrix)
    baseline_records = roles["stdlib"]["records"]
    baseline_statuses = tuple(
        (row["test"], row["status"], row.get("skip_kind"), row.get("reason"))
        for row in baseline_records
    )
    for role in ("rust", "vm", "zig"):
        actual_statuses = tuple(
            (row["test"], row["status"], row.get("skip_kind"), row.get("reason"))
            for row in roles[role]["records"]
        )
        require(
            actual_statuses == baseline_statuses,
            "an original native release status or named private skip differs "
            "from the independently observed Python baseline: " + role,
        )
    require(document.get("prerequisite_sha256") == pins,
            "the refreshed genuine upstream prerequisite chain is incomplete")
    incident = document.get("preserved_first_campaign_failure")
    require(
        isinstance(incident, Mapping)
        and incident.get("path") == FIRST_CAMPAIGN_FAILURE_RELATIVE
        and incident.get("sha256") == FIRST_CAMPAIGN_FAILURE_SHA256
        and incident.get("schema") == FIRST_CAMPAIGN_FAILURE_SCHEMA
        and incident.get("phase") == FIRST_CAMPAIGN_FAILURE_PHASE
        and incident.get("successful_campaign") is False
        and incident.get("campaign_stages_run") == 0,
        "the genuine failed first campaign was hidden or treated as a pass",
    )
    require(document.get("status") == "PASS",
            "an actual incomplete official test cannot qualify as a pass")
    return {"status": "PASS", "roles": summaries, "public_waivers": 0}


def inspect_environment() -> dict[str, Any]:
    verify_runtime()
    authentic_support = authenticate_upstream_support()
    baseline = importlib.import_module("re")
    origin = getattr(baseline, "__file__", None)
    require(
        isinstance(origin, str)
        and Path(origin).resolve().is_relative_to(Path(sys.base_prefix).resolve()),
        "the baseline must be the pinned, unmodified standard-library re module",
    )
    test_package = importlib.util.find_spec("test")
    support_available = False
    corpus_available = False
    if test_package is not None:
        try:
            support_available = importlib.util.find_spec("test.support") is not None
            corpus_available = importlib.util.find_spec("test.re_tests") is not None
        except (ImportError, ModuleNotFoundError, ValueError):
            support_available = False
            corpus_available = False
    previous_path = list(sys.path)
    try:
        sys.path.insert(0, str(UPSTREAM_LIB))
        support = importlib.import_module("test.support")
        warnings_helper = importlib.import_module("test.support.warnings_helper")
        corpus = importlib.import_module("test.re_tests")
        _validate_preloaded_support(sys.modules)
        live_fixtures = _verify_live_official_fixtures(
            support, warnings_helper, corpus,
        )
        require(
            Path(support.__file__).resolve()
            == (UPSTREAM_LIB / "test" / "support" / "__init__.py").resolve()
            and Path(warnings_helper.__file__).resolve()
            == (UPSTREAM_LIB / "test" / "support" / "warnings_helper.py").resolve()
            and Path(corpus.__file__).resolve()
            == (UPSTREAM_LIB / "test" / "re_tests.py").resolve()
            and support.bigmemtest.__module__ == "test.support"
            and support.requires_resource.__module__ == "test.support"
            and support._2G == 2**31,
            "the genuine archive-backed official support was substituted",
        )
        cpu_enabled = support.is_resource_enabled("cpu")
        actual_memory_limit = support.real_max_memuse
        authentic_support_available = True
    finally:
        sys.path[:] = previous_path
    return {
        "python": "3.14.6",
        "stdlib_re_origin": origin,
        "upstream_archive_sha256": authentic_support["upstream_archive_sha256"],
        "official_support_tree_sha256": (
            authentic_support["official_support_tree_sha256"]
        ),
        "official_support_module_count": (
            authentic_support["official_support_module_count"]
        ),
        "authenticated_official_support_available": authentic_support_available,
        "live_upstream_corpus_cases": live_fixtures[
            "actual_upstream_corpus_cases"
        ],
        "live_external_fixture_assertion_cases": live_fixtures[
            "actual_external_fixture_assertion_cases"
        ],
        "official_support_shim_used": False,
        "official_test_source_rewritten": False,
        "installed_official_test_package": test_package is not None,
        "installed_official_test_support": support_available,
        "installed_official_test_corpus_package": corpus_available,
        "baseline_private_debug_fail_after": hasattr(
            baseline.Pattern, "_fail_after",
        ),
        "cpu_resource_enabled_by_authentic_default": cpu_enabled,
        "real_max_memuse_initial": actual_memory_limit,
        "nominal_big_memory_tests_actually_executed": False,
        "multiprocessing_extension_available": (
            importlib.util.find_spec("_multiprocessing") is not None
        ),
        "localedef_program_available": shutil.which("localedef") is not None,
        "big_memory_tests_executed": False,
        "locales_generated": False,
        "official_tests_executed": 0,
        "native_workers_started": 0,
        "candidate_imports": 0,
        "performance_oracle_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
    }


def diagnose_prerequisites(environment: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    for label, value in (
        ("frozen V4 controller source", SOURCE_SHA256),
        ("frozen V4 protocol", PROTOCOL_SHA256),
        ("frozen exact 152-method source matrix", METHOD_MATRIX_SHA256),
        ("refreshed current-build edge proof", REFRESHED_EDGE_PROOF_SHA256),
        ("refreshed current-build deep proof", REFRESHED_DEEP_PROOF_SHA256),
        ("genuine successful Rust V7 campaign", CAMPAIGN_REPORT_SHA256["rust"]),
        ("genuine successful C V7 campaign", CAMPAIGN_REPORT_SHA256["vm"]),
        ("genuine successful Zig V7 campaign", CAMPAIGN_REPORT_SHA256["zig"]),
    ):
        if not is_sha256(value):
            blockers.append(label + " is not published")
    if environment.get("authenticated_official_support_available") is not True:
        blockers.append(
            "the exact authenticated complete original CPython support tree "
            "is unavailable"
        )
    if environment.get("multiprocessing_extension_available") is not True:
        blockers.append(
            "the real GH94675 official multiprocessing regression would be skipped"
        )
    if environment.get("localedef_program_available") is not True:
        blockers.append(
            "fresh real ISO-8859-1 and UTF-8 private locales cannot be compiled"
        )
    return blockers


def _strict_json(source: bytes, label: str) -> Any:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        output: dict[str, Any] = {}
        for key, value in items:
            require(key not in output, "a JSON evidence field was duplicated: " + key)
            output[key] = value
        return output

    try:
        return json.loads(
            source.decode("utf-8"),
            object_pairs_hook=pairs,
            parse_constant=lambda value: (_ for _ in ()).throw(
                OfficialV4Error("non-finite JSON evidence is forbidden: " + value)
            ),
        )
    except (UnicodeError, json.JSONDecodeError) as error:
        raise OfficialV4Error("a genuine evidence record is invalid: " + label) from error


def _read_verified_evidence(relative: str, expected_sha256: str) -> Any:
    require(
        isinstance(relative, str)
        and bool(relative)
        and not Path(relative).is_absolute()
        and ".." not in Path(relative).parts
        and is_sha256(expected_sha256),
        "an exact frozen production evidence path and fingerprint are required",
    )
    source = _read_bounded_regular(
        ROOT / relative, MAX_EVIDENCE_BYTES, relative,
    )
    require(
        hashlib.sha256(source).hexdigest() == expected_sha256,
        "the actual frozen production evidence changed: " + relative,
    )
    return _strict_json(source, relative)


def _validate_campaign(document: Any, role: str) -> dict[str, Any]:
    candidate = "candidates." + role + "_candidate"
    require(
        isinstance(document, dict)
        and document.get("schema") == "rebar-rust-campaign-gate-v1"
        and document.get("postfinal_schema")
        == "rebar-v8-multi-candidate-sealed-campaign-postfinal-v7"
        and document.get("candidate") == candidate
        and document.get("pinned_cpython") == "3.14.6"
        and document.get("passed") is True
        and document.get("required_correctness_step_count") == 22,
        "a fresh source-bound actual V7 campaign did not pass: " + role,
    )
    steps = document.get("steps")
    require(
        isinstance(steps, list)
        and len(steps) == 22
        and all(isinstance(step, dict) for step in steps)
        and len({step.get("name") for step in steps}) == 22,
        "the fresh genuine V7 campaign omitted an entire stage: " + role,
    )
    for step in steps:
        evidence = step.get("evidence")
        require(
            step.get("passed") is True
            and step.get("candidate") == candidate
            and isinstance(evidence, dict)
            and is_sha256(step.get("evidence_sha256"))
            and step["evidence_sha256"] == digest(evidence)
            and step.get("holdout_accessed") is False
            and step.get("timing_performed") is False
            and step.get("performance") == "NOT MEASURED",
            "a fresh V7 campaign stage was incomplete or falsified: "
            + role + "/" + str(step.get("name")),
        )
    by_name = {step["name"]: step for step in steps}
    for name, expected in CAMPAIGN_STEP_DENOMINATORS.items():
        require(
            name in by_name and by_name[name].get("expected_checks") == expected,
            "the real sealed V7 campaign denominator changed: "
            + role + "/" + name,
        )
    require(
        set(CAMPAIGN_NATIVE_BOUNDARY_STEPS) <= set(by_name)
        and by_name["full-unicode-plane"]["evidence"].get(
            "correctness_checks",
        ) == 4_494_555,
        "the current independent native and full-Unicode campaign was weakened",
    )
    return document


def authenticate_production_prerequisites(
    source_sha256: str,
    protocol_sha256: str,
) -> dict[str, Any]:
    """Fail before importing a candidate or starting any original-test worker."""
    verify_runtime()
    pins = published_pins(source_sha256, protocol_sha256)
    for path, expected in (
        (SOURCE_RELATIVE, pins["v4_source"]),
        (PROTOCOL_RELATIVE, pins["v4_protocol"]),
    ):
        source = _read_bounded_regular(ROOT / path, MAX_FROZEN_SOURCE_BYTES, path)
        require(hashlib.sha256(source).hexdigest() == expected,
                "the actually frozen V4 source or protocol changed: " + path)
    authentic_support = authenticate_upstream_support()
    official_source = _read_bounded_regular(
        ROOT / "tools/postfinal_cpython_locale_oracle_v3.py",
        MAX_FROZEN_SOURCE_BYTES,
        "tools/postfinal_cpython_locale_oracle_v3.py",
    )
    require(hashlib.sha256(official_source).hexdigest() == V3_SOURCE_SHA256,
            "the frozen historical V3 audit validator was substituted")
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    official = importlib.import_module("tools.postfinal_cpython_locale_oracle_v3")
    historical_pins = official.pins()
    base = _read_verified_evidence(
        official.V7_BASE_REPORT_RELATIVE, historical_pins["base_report"],
    )
    strict = _read_verified_evidence(
        official.V7_STRICT_REPORT_RELATIVE, historical_pins["strict_report"],
    )
    official.validate_v7_audits(
        base,
        strict,
        source_relative=official.V7_BASE_REPORT_RELATIVE,
        strict_relative=official.V7_STRICT_REPORT_RELATIVE,
        source_digest=historical_pins["base_report"],
    )
    qualified_sources, qualified_binaries, native_by_family = (
        official.previous._base_graph(base)
    )
    official.original.verify_production_fingerprints(
        qualified_sources, qualified_binaries,
    )
    require(set(native_by_family) >= {"rust", "vm", "zig"},
            "one independently owned exact native family was omitted")
    edge = _read_verified_evidence(
        str(REFRESHED_EDGE_PROOF_RELATIVE), pins["refreshed_edge_proof"],
    )
    deep = _read_verified_evidence(
        str(REFRESHED_DEEP_PROOF_RELATIVE), pins["refreshed_deep_proof"],
    )
    for label, proof in (("edge", edge), ("deep", deep)):
        require(
            isinstance(proof, Mapping)
            and (
                proof.get("status") == "PASS"
                or proof.get("passed") is True
            ),
            "the actual refreshed current-build " + label + " proof did not pass",
        )
    campaigns: dict[str, Any] = {}
    for role in ("rust", "vm", "zig"):
        campaigns[role] = _validate_campaign(
            _read_verified_evidence(
                CAMPAIGN_REPORT_RELATIVES[role],
                pins["v7_campaign_" + role],
            ),
            role,
        )
    incident = _read_verified_evidence(
        FIRST_CAMPAIGN_FAILURE_RELATIVE,
        FIRST_CAMPAIGN_FAILURE_SHA256,
    )
    require(
        isinstance(incident, Mapping)
        and incident.get("schema") == FIRST_CAMPAIGN_FAILURE_SCHEMA
        and incident.get("phase") == FIRST_CAMPAIGN_FAILURE_PHASE
        and incident.get("successful_campaign") is not True,
        "the genuine first current-build V7 failure was hidden or forged",
    )
    return {
        "prerequisite_sha256": pins,
        "historical_v3_support": "synthetic support shim; not a V4 official pass",
        "native_sha256_by_family": native_by_family,
        "v7_campaign_roles": list(campaigns),
        "official_support": authentic_support,
        "preserved_first_campaign_failure": {
            "path": FIRST_CAMPAIGN_FAILURE_RELATIVE,
            "sha256": FIRST_CAMPAIGN_FAILURE_SHA256,
            "schema": FIRST_CAMPAIGN_FAILURE_SCHEMA,
            "phase": FIRST_CAMPAIGN_FAILURE_PHASE,
            "successful_campaign": False,
            "campaign_stages_run": 0,
        },
    }


@contextlib.contextmanager
def _single_memory_worker() -> Any:
    """A real 40-GiB role is exclusive; source controls never acquire a lock."""
    import fcntl

    path = Path("/tmp/rebar-cpython/rebar-cpython-v4-bigmem.lock")
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o600)
    try:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise OfficialV4Error(
                "another real upstream 40-GiB official worker is still active"
            ) from error
        yield
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


@contextlib.contextmanager
def _fresh_private_locales() -> Any:
    localedef = shutil.which("localedef")
    require(isinstance(localedef, str),
            "actual localedef is required for both real official locales")
    previous_locale = locale.setlocale(locale.LC_CTYPE)
    previous_path = os.environ.get("LOCPATH")
    with tempfile.TemporaryDirectory(prefix="rebar-cpython-v4-locales-") as root:
        for encoding, name in (
            ("ISO-8859-1", "en_US.iso88591"),
            ("UTF-8", "en_US.utf8"),
        ):
            result = subprocess.run(
                [localedef, "--no-archive", "-i", "en_US", "-f", encoding,
                 str(Path(root) / name)],
                check=False,
                capture_output=True,
            )
            require(result.returncode == 0,
                    "a genuine private official locale could not be compiled: " + name)
        os.environ["LOCPATH"] = root
        try:
            for name in ("en_US.iso88591", "en_US.utf8"):
                try:
                    locale.setlocale(locale.LC_CTYPE, name)
                except locale.Error as error:
                    raise OfficialV4Error(
                        "a genuinely compiled private locale is not usable: " + name
                    ) from error
            locale.setlocale(locale.LC_CTYPE, previous_locale)
            yield {
                "fresh_private_localedef": True,
                "iso_8859_1_passed": True,
                "utf_8_passed": True,
            }
        finally:
            locale.setlocale(locale.LC_CTYPE, previous_locale)
            if previous_path is None:
                os.environ.pop("LOCPATH", None)
            else:
                os.environ["LOCPATH"] = previous_path


@contextlib.contextmanager
def _observe_original_call(method: str, official_path: Path) -> Any:
    observations: dict[str, Any] = {}
    if method not in {
        "ReTests.test_large_search",
        "ReTests.test_large_subn",
        "ReTests.test_regression_gh94675",
    }:
        yield observations
        return
    previous = sys.getprofile()
    wanted = method.split(".", 1)[1]

    def profile(frame: Any, event: str, argument: Any) -> None:
        del argument
        if event != "call":
            return
        if (
            frame.f_code.co_name == wanted
            and Path(frame.f_code.co_filename).resolve()
            == official_path.resolve()
        ):
            value = frame.f_locals.get("size")
            if type(value) is int:
                observations["delivered_size"] = value
        if (
            method == "ReTests.test_regression_gh94675"
            and frame.f_code.co_name == "start"
            and str(frame.f_globals.get("__name__", "")).startswith(
                "multiprocessing."
            )
        ):
            observations["process_started"] = True

    sys.setprofile(profile)
    try:
        yield observations
    finally:
        sys.setprofile(previous)


def _verify_live_official_fixtures(
    support: Any,
    warnings_helper: Any,
    corpus: Any,
) -> dict[str, Any]:
    _validate_preloaded_support(sys.modules)
    expected = (
        (
            "test.support",
            support,
            UPSTREAM_LIB / "test" / "support" / "__init__.py",
            UPSTREAM_SUPPORT_INIT_SHA256,
        ),
        (
            "test.support.warnings_helper",
            warnings_helper,
            UPSTREAM_LIB / "test" / "support" / "warnings_helper.py",
            UPSTREAM_WARNINGS_HELPER_SHA256,
        ),
        (
            "test.re_tests",
            corpus,
            UPSTREAM_LIB / "test" / "re_tests.py",
            CORPUS_SOURCE_SHA256,
        ),
    )
    modules: dict[str, Any] = {}
    for name, module, path, expected_sha256 in expected:
        specification = getattr(module, "__spec__", None)
        origin = getattr(specification, "origin", None)
        actual = getattr(module, "__file__", None)
        require(
            sys.modules.get(name) is module
            and isinstance(origin, str)
            and isinstance(actual, str)
            and Path(origin).resolve() == path.resolve()
            and Path(actual).resolve() == path.resolve(),
            "an active authenticated upstream fixture was replaced: " + name,
        )
        source = _read_bounded_regular(
            path, MAX_FROZEN_SOURCE_BYTES, "active official fixture " + name,
        )
        require(
            hashlib.sha256(source).hexdigest() == expected_sha256,
            "an active official fixture's unchanged bytes were replaced: " + name,
        )
        modules[name] = {"path": str(path), "sha256": expected_sha256}
    require(
        isinstance(getattr(corpus, "tests", None), list)
        and len(corpus.tests) == CORPUS_CASES
        and all(
            isinstance(row, tuple) and len(row) in {3, 5}
            for row in corpus.tests
        )
        and isinstance(getattr(corpus, "benchmarks", None), list)
        and len(corpus.benchmarks) == EXTERNAL_FIXTURE_ASSERTION_CASES
        and all(
            isinstance(row, tuple) and len(row) == 2
            for row in corpus.benchmarks
        )
        and support.bigmemtest.__module__ == "test.support"
        and support.requires_resource.__module__ == "test.support"
        and support.SHORT_TIMEOUT == 30.0,
        "an actual original upstream fixture, decorator, or timeout changed",
    )
    return {
        "modules": modules,
        "actual_upstream_corpus_cases": len(corpus.tests),
        "actual_external_fixture_assertion_cases": len(corpus.benchmarks),
        "support_tree_sha256": OFFICIAL_SUPPORT_TREE_SHA256,
        "official_support_shim_used": False,
    }


@contextlib.contextmanager
def _role_regex_module(
    role: str,
    baseline: Any,
    constant_module: Any,
    provenance: Mapping[str, Any],
) -> Any:
    if role == "stdlib":
        yield baseline, {
            "passed": True,
            "candidate_isolation": True,
            "baseline_only": True,
        }
        return
    require(role in ("rust", "vm", "zig"),
            "an unaudited candidate cannot enter a genuine original worker")
    expected = provenance["native_sha256_by_family"].get(role)
    require(isinstance(expected, dict) and bool(expected),
            "the current independently owned native bridge is not authenticated")
    guarded = importlib.import_module(
        "tools.python_re_universal_public_oracle_stage07",
    )
    official = importlib.import_module("tools.postfinal_cpython_locale_oracle_v3")
    native_guard = guarded._install_family_guard(role, expected)
    official.previous._validate_guard(native_guard, role)
    candidate = importlib.import_module("candidates." + role + "_candidate")
    mapped = guarded._verify_family_native_mappings(role, provenance)
    require(isinstance(mapped, dict) and bool(mapped),
            "the active independently owned native matching bridge is missing")

    saved_re = sys.modules.get("re")
    saved_constants = sys.modules.get("re._constants")
    constants = types.ModuleType("re._constants")
    constants.__dict__["MAXGROUPS"] = constant_module.MAXGROUPS
    constants.__dict__["__package__"] = "re"
    constants.__dict__["__spec__"] = importlib.machinery.ModuleSpec(
        "re._constants", loader=None,
    )
    allowed = {
        "candidates." + role + "_candidate",
        official.OWNED_BRIDGES[role],
    }

    def live_native_modules() -> set[str]:
        return {
            name
            for name, value in sys.modules.items()
            if name.startswith("candidates.")
            and value is not None
            and not isinstance(value, guarded._ForbiddenRegexModule)
        }

    require(
        live_native_modules() <= allowed,
        "a different matching family escaped into the real original worker",
    )
    before_guard_sha256 = digest(native_guard)
    before_native_sha256 = digest(mapped)
    recorded_guard = {
        "passed": True,
        "candidate_isolation": True,
        "native_matching_executed": True,
        "stdlib_re_delegation": False,
        "sre_delegation": False,
        "external_package_delegation": False,
        "other_candidate_delegation": False,
        "original_test_source_rewritten": False,
        "oracle_maxgroups_constant_only": True,
        "native_binary_sha256": mapped,
        "native_guard_sha256_before": before_guard_sha256,
        "native_mapping_sha256_before": before_native_sha256,
    }
    try:
        sys.modules["re"] = candidate
        sys.modules["re._constants"] = constants
        require(
            sys.modules.get("re") is candidate
            and sys.modules.get("re._constants") is constants
            and set(constants.__dict__) <= {
                "__name__", "__doc__", "__package__", "__loader__",
                "__spec__", "MAXGROUPS",
            }
            and constants.MAXGROUPS == constant_module.MAXGROUPS,
            "the original-test constant shim exposed a matching implementation",
        )
        yield candidate, recorded_guard
        require(
            sys.modules.get("re") is candidate
            and sys.modules.get("re._constants") is constants
            and set(constants.__dict__) <= {
                "__name__", "__doc__", "__package__", "__loader__",
                "__spec__", "MAXGROUPS",
            }
            and constants.MAXGROUPS == constant_module.MAXGROUPS,
            "an original native test replaced its isolated module or constant",
        )
        official.previous._validate_guard(native_guard, role)
        after = guarded._verify_family_native_mappings(role, provenance)
        require(
            isinstance(after, dict)
            and digest(after) == before_native_sha256
            and digest(native_guard) == before_guard_sha256
            and live_native_modules() <= allowed,
            "the native guard, mapped binary, or engine changed during 152 tests",
        )
        recorded_guard["native_guard_sha256_after"] = digest(native_guard)
        recorded_guard["native_mapping_sha256_after"] = digest(after)
        recorded_guard["loaded_native_modules_after"] = sorted(
            live_native_modules(),
        )
    finally:
        if saved_re is None:
            sys.modules.pop("re", None)
        else:
            sys.modules["re"] = saved_re
        if saved_constants is None:
            sys.modules.pop("re._constants", None)
        else:
            sys.modules["re._constants"] = saved_constants


def _run_one_original_method(
    namespace: Any,
    requirement: Mapping[str, Any],
    official_path: Path,
    support: Any,
    start_method: str,
) -> dict[str, Any]:
    identity = requirement["test"]
    class_name, method_name = identity.split(".", 1)
    test_class = getattr(namespace, class_name, None)
    require(
        isinstance(test_class, type)
        and issubclass(test_class, unittest.TestCase)
        and callable(getattr(test_class, method_name, None)),
        "the unchanged original upstream test method is unavailable: " + identity,
    )
    result = unittest.TestResult()
    with _observe_original_call(identity, official_path) as observed:
        test_class(method_name).run(result)
    require(result.testsRun == 1,
            "an original public method did not actually run: " + identity)
    record: dict[str, Any] = {
        "test": identity,
        "source_ast_sha256": requirement["source_ast_sha256"],
        "status": "PASS",
    }
    if result.skipped:
        require(len(result.skipped) == 1,
                "the actual upstream skip record is malformed: " + identity)
        record["status"] = "SKIP"
        record["reason"] = str(result.skipped[0][1])
        if (
            identity == "ReTests.test_memory_leaks"
            and record["reason"] == "requires debug build"
        ):
            record["skip_kind"] = "named-private-debug-condition"
    elif result.failures:
        record["status"] = "FAIL"
        record["reason"] = str(result.failures[0][1])
    elif result.errors:
        record["status"] = "ERROR"
        record["reason"] = str(result.errors[0][1])
    elif result.unexpectedSuccesses:
        record["status"] = "ERROR"
        record["reason"] = "the original upstream unittest unexpectedly succeeded"
    if identity in {"ReTests.test_large_search", "ReTests.test_large_subn"}:
        record["resource"] = {
            "delivered_size": observed.get("delivered_size"),
            "real_max_memuse": support.real_max_memuse,
            "declared_size": support._2G,
            "dry_run": observed.get("delivered_size") != support._2G,
        }
        if record["status"] == "PASS":
            require(
                observed.get("delivered_size") == 2**31,
                "a nominal original 2-GiB pass actually used a dry-run size: "
                + identity,
            )
    elif identity == "ReTests.test_search_anchor_at_beginning":
        record["resource"] = {
            "cpu_resource_enabled": support.is_resource_enabled("cpu"),
            "subject_characters": 10**7,
            "original_upper_bound_seconds": 0.1,
            "original_stopwatch_assertion_passed": record["status"] == "PASS",
        }
    elif identity == "ReTests.test_regression_gh94675":
        record["resource"] = {
            "process_started": observed.get("process_started", False),
            "start_method": start_method,
            "short_timeout_seconds": support.SHORT_TIMEOUT,
        }
        if record["status"] == "PASS":
            require(observed.get("process_started") is True,
                    "the real original multiprocessing regression never started")
    return record


def execute_original_role(
    role: str,
    source_sha256: str,
    protocol_sha256: str,
) -> dict[str, Any]:
    """Run the literal upstream file only after the complete genuine gate."""
    require(role in ROLES, "only an exact frozen real original role can run")
    provenance = authenticate_production_prerequisites(
        source_sha256, protocol_sha256,
    )
    official = introspect_official_sources()
    matrix = official["public_method_matrix"]
    expected_path = UPSTREAM_LIB / "test" / "test_re.py"
    exact_source = _read_bounded_regular(
        expected_path, MAX_FROZEN_SOURCE_BYTES,
        "authentic unchanged upstream Lib/test/test_re.py",
    )
    require(hashlib.sha256(exact_source).hexdigest() == TEST_SOURCE_SHA256,
            "the actual executed official upstream source is not authentic")
    previous_path = list(sys.path)
    output = io.StringIO()
    error_output = io.StringIO()
    records: list[dict[str, Any]] = []
    active_method: str | None = None
    try:
        sys.path.insert(0, str(UPSTREAM_LIB))
        baseline = importlib.import_module("re")
        constants = importlib.import_module("re._constants")
        support = importlib.import_module("test.support")
        warnings_helper = importlib.import_module("test.support.warnings_helper")
        corpus = importlib.import_module("test.re_tests")
        _validate_preloaded_support(sys.modules)
        fixtures_before = _verify_live_official_fixtures(
            support, warnings_helper, corpus,
        )
        require(
            support.bigmemtest.__module__ == "test.support"
            and support.requires_resource.__module__ == "test.support"
            and support._2G == 2**31,
            "the actual official role loaded a fabricated support shim",
        )
        support.verbose = 0
        support.set_memlimit("40G")
        require(
            support.real_max_memuse == CONFIGURED_OFFICIAL_MEMORY_BYTES
            and support.is_resource_enabled("cpu"),
            "the exact 40-GiB official memory and CPU resources were not enabled",
        )
        multiprocessing = importlib.import_module("multiprocessing")
        methods = multiprocessing.get_all_start_methods()
        require("fork" in methods,
                "the original GH94675 worker requires the real available fork mode")
        multiprocessing.set_start_method("fork", force=True)
        require(multiprocessing.get_start_method() == "fork",
                "the genuine upstream subprocess start method was not isolated")
        with _single_memory_worker():
            with _fresh_private_locales() as locale_report:
                with _role_regex_module(
                    role, baseline, constants, provenance,
                ) as (regex, guard):
                    specification = importlib.util.spec_from_file_location(
                        "test.test_re", expected_path,
                    )
                    require(
                        specification is not None
                        and specification.loader is not None,
                        "the untouched genuine official test cannot be imported",
                    )
                    namespace = importlib.util.module_from_spec(specification)
                    saved_official = sys.modules.get("test.test_re")
                    try:
                        sys.modules["test.test_re"] = namespace
                        with contextlib.redirect_stdout(output):
                            with contextlib.redirect_stderr(error_output):
                                specification.loader.exec_module(namespace)
                                require(
                                    _verify_live_official_fixtures(
                                        support, warnings_helper, corpus,
                                    ) == fixtures_before,
                                    "candidate alias replaced an authentic official fixture",
                                )
                                for item in matrix:
                                    active_method = item["test"]
                                    if item["test"] in {
                                        "ExternalTests.test_re_tests",
                                        "ExternalTests.test_re_benchmarks",
                                    }:
                                        require(
                                            _verify_live_official_fixtures(
                                                support, warnings_helper, corpus,
                                            ) == fixtures_before,
                                            "the actual original corpus was replaced "
                                            "before its upstream method",
                                        )
                                    records.append(_run_one_original_method(
                                        namespace, item, expected_path,
                                        support, "fork",
                                    ))
                                    active_method = None
                                fixtures_after = _verify_live_official_fixtures(
                                    support, warnings_helper, corpus,
                                )
                                require(
                                    fixtures_after == fixtures_before,
                                    "the live actual original fixture was mutated",
                                )
                    finally:
                        if saved_official is None:
                            sys.modules.pop("test.test_re", None)
                        else:
                            sys.modules["test.test_re"] = saved_official
                    summary = assess_role_records(role, records, matrix)
                    resources = {
                        "real_max_memuse": support.real_max_memuse,
                        "large_method_sizes": {
                            item["test"]: item.get("resource", {}).get(
                                "delivered_size",
                            )
                            for item in records
                            if item["test"] in {
                                "ReTests.test_large_search",
                                "ReTests.test_large_subn",
                            }
                        },
                        "cpu_resource_enabled": support.is_resource_enabled("cpu"),
                        "multiprocessing_extension_available": (
                            importlib.util.find_spec("_multiprocessing")
                            is not None
                        ),
                        "multiprocessing_start_method": "fork",
                        "private_debug_fail_after": hasattr(
                            regex.Pattern, "_fail_after",
                        ),
                        "actual_upstream_corpus_cases": len(corpus.tests),
                        "actual_external_fixture_assertion_cases": len(
                            corpus.benchmarks,
                        ),
                        "exclusive_big_memory_worker": True,
                        "official_support_shim_used": False,
                        "official_test_source_rewritten": False,
                    }
                    return {
                        **summary,
                        "records": records,
                        "locale": locale_report,
                        "guard": guard,
                        "resource_provenance": resources,
                        "executed_test_source_sha256": TEST_SOURCE_SHA256,
                        "official_support_tree_sha256": (
                            OFFICIAL_SUPPORT_TREE_SHA256
                        ),
                        "live_official_fixture_provenance": fixtures_after,
                        "captured_official_stdout": output.getvalue(),
                        "captured_official_stderr": error_output.getvalue(),
                    }
    except OfficialV4WorkerFailure:
        raise
    except (OfficialV4Error, OSError, MemoryError) as error:
        if records or active_method is not None:
            raise OfficialV4WorkerFailure(
                role,
                "the genuine original role stopped after actual upstream methods: "
                + role,
                {
                    "completed_original_method_records": records,
                    "completed_original_method_count": len(records),
                    "active_original_method": active_method,
                    "actual_error_type": type(error).__name__,
                    "actual_error": str(error),
                    "captured_official_stdout": _bounded_failure_stream(
                        output.getvalue(),
                    ),
                    "captured_official_stderr": _bounded_failure_stream(
                        error_output.getvalue(),
                    ),
                },
            ) from error
        raise
    finally:
        sys.path[:] = previous_path


def _safe_output_path(relative: str) -> Path:
    approved = {
        REPORT_RELATIVE,
        FAILURE_RELATIVE,
        SELF_ORACLE_RELATIVE,
        SELF_ORACLE_FAILURE_RELATIVE,
        *ROLE_REPORT_RELATIVES.values(),
    }
    require(
        isinstance(relative, str)
        and relative in approved
        and not Path(relative).is_absolute()
        and ".." not in Path(relative).parts
        and "\\" not in relative
        and "\x00" not in relative,
        "only a new exact version-four official evidence path is permitted",
    )
    return ROOT / relative


def _exclusive_write(document: Mapping[str, Any], relative: str) -> str:
    path = _safe_output_path(relative)
    source = canonical(document) + b"\n"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, 0o600)
    except OSError as error:
        raise OfficialV4Error(
            "the genuine exclusive V4 report cannot replace prior evidence: "
            + relative
        ) from error
    try:
        view = memoryview(source)
        while view:
            written = os.write(descriptor, view)
            require(written > 0, "the exclusive genuine V4 report was truncated")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    return hashlib.sha256(source).hexdigest()


WORKER_BOOTSTRAP = (
    "import sys;sys.path.insert(0,sys.argv[1]);"
    "from tools.postfinal_cpython_locale_oracle_v4 import worker_entry;"
    "raise SystemExit(worker_entry(sys.argv[2],sys.argv[3],sys.argv[4]))"
)


def worker_entry(role: str, source_sha256: str, protocol_sha256: str) -> int:
    try:
        document = execute_original_role(role, source_sha256, protocol_sha256)
    except OfficialV4WorkerFailure as error:
        print(json.dumps({
            "schema": SCHEMA + "-actual-worker-failure",
            "status": "FAIL",
            "role": error.role,
            "reason": str(error),
            "details": error.details,
            "performance": "NOT MEASURED",
        }, sort_keys=True, separators=(",", ":")))
        return 2
    except (OfficialV4Error, OSError, subprocess.SubprocessError) as error:
        print(json.dumps({
            "schema": SCHEMA + "-actual-worker-failure",
            "status": "FAIL",
            "role": role,
            "reason": str(error),
            "performance": "NOT MEASURED",
        }, sort_keys=True, separators=(",", ":")))
        return 2
    print(json.dumps({
        "schema": SCHEMA + "-actual-worker",
        "python": "3.14.6",
        "role": role,
        "source_sha256": source_sha256,
        "protocol_sha256": protocol_sha256,
        "public_method_matrix_sha256": METHOD_MATRIX_SHA256,
        "role_report": document,
        "performance": "NOT MEASURED",
    }, sort_keys=True, separators=(",", ":")))
    return 0


def _bounded_failure_stream(value: Any) -> dict[str, Any]:
    if value is None:
        original = b""
    elif isinstance(value, bytes):
        original = value
    elif isinstance(value, str):
        original = value.encode("utf-8", errors="surrogatepass")
    else:
        raise OfficialV4Error("an actual worker stream is not text or bytes")
    preview = original[:MAX_FAILURE_STREAM_PREVIEW_BYTES]
    return {
        "bytes": len(original),
        "sha256": hashlib.sha256(original).hexdigest(),
        "preview_bytes": len(preview),
        "preview_hex": preview.hex(),
        "preview_utf8": preview.decode("utf-8", errors="replace"),
        "preview_truncated": len(original) > len(preview),
    }


def _run_isolated_worker(
    role: str,
    source_sha256: str,
    protocol_sha256: str,
) -> dict[str, Any]:
    require(role in ROLES, "an approved original isolated role is required")
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        completed = subprocess.run(
            [
                str(PINNED_CPYTHON),
                "-I",
                "-B",
                "-c",
                WORKER_BOOTSTRAP,
                str(ROOT),
                role,
                source_sha256,
                protocol_sha256,
            ],
            check=False,
            capture_output=True,
            env=environment,
            timeout=3_600,
        )
    except subprocess.TimeoutExpired as error:
        raise OfficialV4WorkerFailure(
            role,
            "a real isolated original official worker timed out: " + role,
            {
                "status": "TIMEOUT",
                "timeout_seconds": 3_600,
                "stdout": _bounded_failure_stream(error.stdout),
                "stderr": _bounded_failure_stream(error.stderr),
            },
        ) from error
    bounded_stdout = _bounded_failure_stream(completed.stdout)
    bounded_stderr = _bounded_failure_stream(completed.stderr)
    actual_details: dict[str, Any] = {
        "returncode": completed.returncode,
        "signal": -completed.returncode if completed.returncode < 0 else None,
        "stdout_bytes": len(completed.stdout),
        "stderr_bytes": len(completed.stderr),
        "stdout_sha256": bounded_stdout["sha256"],
        "stderr_sha256": bounded_stderr["sha256"],
        "stdout_truncated": len(completed.stdout) > MAX_WORKER_OUTPUT_BYTES,
        "stderr_truncated": len(completed.stderr) > MAX_WORKER_OUTPUT_BYTES,
        "stdout": bounded_stdout,
        "stderr": bounded_stderr,
    }
    if (
        len(completed.stdout) > MAX_WORKER_OUTPUT_BYTES
        or len(completed.stderr) > MAX_WORKER_OUTPUT_BYTES
    ):
        raise OfficialV4WorkerFailure(
            role,
            "a real original worker exceeded the bounded preserved output: " + role,
            actual_details,
        )
    document: Any = None
    decode_error: OfficialV4Error | None = None
    try:
        document = _strict_json(completed.stdout, "real V4 " + role + " worker")
    except OfficialV4Error as error:
        decode_error = error
        actual_details["json_error"] = str(error)
    if isinstance(document, Mapping):
        actual_details["actual_worker_document"] = document
    if completed.returncode != 0:
        raise OfficialV4WorkerFailure(
            role,
            "a genuine isolated original official worker failed: " + role,
            actual_details,
        )
    if decode_error is not None:
        raise OfficialV4WorkerFailure(
            role,
            "a real original worker returned malformed official evidence: " + role,
            actual_details,
        ) from decode_error
    if not (
        isinstance(document, Mapping)
        and document.get("schema") == SCHEMA + "-actual-worker"
        and document.get("python") == "3.14.6"
        and document.get("role") == role
        and document.get("source_sha256") == source_sha256
        and document.get("protocol_sha256") == protocol_sha256
        and document.get("public_method_matrix_sha256")
        == METHOD_MATRIX_SHA256
    ):
        raise OfficialV4WorkerFailure(
            role,
            "a real official worker changed or omitted its frozen provenance: "
            + role,
            actual_details,
        )
    report = document.get("role_report")
    if not isinstance(report, dict):
        raise OfficialV4WorkerFailure(
            role,
            "a real original worker omitted all preserved method records: " + role,
            actual_details,
        )
    return report


def _validate_role_evidence(
    role: str,
    evidence: Mapping[str, Any],
    matrix: list[dict[str, Any]],
) -> dict[str, Any]:
    summary = assess_role_records(role, evidence.get("records"), matrix)
    for field in (
        "role", "methods", "applicable", "passed", "skipped",
        "named_private_debug_skips", "unexplained_skips", "failed", "errors",
        "timeouts", "crashes", "status", "debug_build_coverage",
        "records_sha256", "record_count",
    ):
        require(
            evidence.get(field) == summary[field],
            "an independently computed real official role field differs: "
            + role + ":" + field,
        )
    require(
        summary["status"] == "PASS"
        and summary["methods"] == 152
        and summary["applicable"] == 151
        and summary["passed"] == 151
        and summary["skipped"] == 1
        and summary["named_private_debug_skips"] == 1
        and summary["unexplained_skips"] == 0
        and summary["debug_build_coverage"] == "NOT RUN",
        "all pinned-release roles must retain the exact one named private "
        "debug-build skip: " + role,
    )
    resource = evidence.get("resource_provenance")
    require(
        isinstance(resource, Mapping)
        and isinstance(resource.get("real_max_memuse"), int)
        and resource["real_max_memuse"] == CONFIGURED_OFFICIAL_MEMORY_BYTES
        and resource.get("large_method_sizes") == {
            "ReTests.test_large_search": 2**31,
            "ReTests.test_large_subn": 2**31,
        }
        and resource.get("cpu_resource_enabled") is True
        and resource.get("multiprocessing_extension_available") is True
        and resource.get("multiprocessing_start_method") == "fork"
        and resource.get("actual_upstream_corpus_cases") == CORPUS_CASES
        and resource.get("actual_external_fixture_assertion_cases")
        == EXTERNAL_FIXTURE_ASSERTION_CASES
        and resource.get("exclusive_big_memory_worker") is True
        and resource.get("private_debug_fail_after") is False
        and resource.get("official_support_shim_used") is False
        and resource.get("official_test_source_rewritten") is False,
        "a real original support/resource/delegation requirement failed: " + role,
    )
    for item in evidence["records"]:
        if item["test"] in {
            "ReTests.test_large_search", "ReTests.test_large_subn",
        }:
            observed = item.get("resource")
            require(
                isinstance(observed, Mapping)
                and observed.get("delivered_size") == 2**31
                and observed.get("declared_size") == 2**31
                and observed.get("real_max_memuse")
                == CONFIGURED_OFFICIAL_MEMORY_BYTES
                and observed.get("dry_run") is False,
                "an actual official bigmem method fell back to 5147: "
                + role + ":" + item["test"],
            )
        elif item["test"] == "ReTests.test_regression_gh94675":
            observed = item.get("resource")
            require(
                isinstance(observed, Mapping)
                and observed.get("process_started") is True
                and observed.get("start_method") == "fork"
                and observed.get("short_timeout_seconds") == 30.0,
                "the real original GH94675 subprocess did not run: " + role,
            )
        elif item["test"] == "ReTests.test_search_anchor_at_beginning":
            observed = item.get("resource")
            require(
                isinstance(observed, Mapping)
                and observed.get("cpu_resource_enabled") is True
                and observed.get("subject_characters") == 10**7
                and observed.get("original_upper_bound_seconds") == 0.1
                and observed.get("original_stopwatch_assertion_passed") is True,
                "the real original CPU-anchor requirement did not pass: " + role,
            )
    locale_evidence = evidence.get("locale")
    require(
        isinstance(locale_evidence, Mapping)
        and locale_evidence.get("fresh_private_localedef") is True
        and locale_evidence.get("iso_8859_1_passed") is True
        and locale_evidence.get("utf_8_passed") is True,
        "a real private official locale was not generated: " + role,
    )
    guard = evidence.get("guard")
    require(
        isinstance(guard, Mapping)
        and guard.get("passed") is True
        and guard.get("candidate_isolation") is True
        and (
            (role == "stdlib" and guard.get("baseline_only") is True)
            or (
                role != "stdlib"
                and guard.get("native_matching_executed") is True
                and guard.get("stdlib_re_delegation") is False
                and guard.get("sre_delegation") is False
                and guard.get("external_package_delegation") is False
                and guard.get("other_candidate_delegation") is False
                and guard.get("oracle_maxgroups_constant_only") is True
                and is_sha256(guard.get("native_guard_sha256_before"))
                and guard.get("native_guard_sha256_before")
                == guard.get("native_guard_sha256_after")
                and is_sha256(guard.get("native_mapping_sha256_before"))
                and guard.get("native_mapping_sha256_before")
                == guard.get("native_mapping_sha256_after")
                and isinstance(guard.get("native_binary_sha256"), Mapping)
                and digest(guard["native_binary_sha256"])
                == guard["native_mapping_sha256_before"]
                and isinstance(guard.get("loaded_native_modules_after"), list)
            )
        ),
        "the authentic isolated original native role guard failed: " + role,
    )
    require(
        evidence.get("executed_test_source_sha256") == TEST_SOURCE_SHA256
        and evidence.get("official_support_tree_sha256")
        == OFFICIAL_SUPPORT_TREE_SHA256,
        "an actual role rewrote official source or loaded synthetic support",
    )
    fixtures = evidence.get("live_official_fixture_provenance")
    require(
        isinstance(fixtures, Mapping)
        and fixtures.get("actual_upstream_corpus_cases") == CORPUS_CASES
        and fixtures.get("actual_external_fixture_assertion_cases")
        == EXTERNAL_FIXTURE_ASSERTION_CASES
        and fixtures.get("support_tree_sha256") == OFFICIAL_SUPPORT_TREE_SHA256
        and fixtures.get("official_support_shim_used") is False
        and isinstance(fixtures.get("modules"), Mapping)
        and set(fixtures["modules"])
        == {"test.support", "test.support.warnings_helper", "test.re_tests"}
        and fixtures["modules"]["test.support"]["sha256"]
        == UPSTREAM_SUPPORT_INIT_SHA256
        and fixtures["modules"]["test.support.warnings_helper"]["sha256"]
        == UPSTREAM_WARNINGS_HELPER_SHA256
        and fixtures["modules"]["test.re_tests"]["sha256"]
        == CORPUS_SOURCE_SHA256,
        "a real original role did not preserve live authenticated fixtures",
    )
    return summary


def _base_official_document(
    source_sha256: str,
    protocol_sha256: str,
    provenance: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "python": "3.14.6",
        "source_path": SOURCE_RELATIVE,
        "source_sha256": source_sha256,
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": protocol_sha256,
        "test_source_sha256": TEST_SOURCE_SHA256,
        "corpus_source_sha256": CORPUS_SOURCE_SHA256,
        "upstream_archive_sha256": UPSTREAM_ARCHIVE_SHA256,
        "official_support_tree_sha256": OFFICIAL_SUPPORT_TREE_SHA256,
        "official_support_module_count": len(OFFICIAL_SUPPORT_MODULES),
        "public_method_matrix_sha256": METHOD_MATRIX_SHA256,
        "all_original_methods": ORIGINAL_METHODS,
        "public_original_methods": PUBLIC_METHODS,
        "private_original_methods": PRIVATE_METHODS,
        "actual_upstream_corpus_cases": CORPUS_CASES,
        "actual_external_fixture_assertion_cases": (
            EXTERNAL_FIXTURE_ASSERTION_CASES
        ),
        "public_method_waivers": [],
        "named_private_class_waivers": PRIVATE_CLASS_WAIVERS,
        "prerequisite_sha256": provenance["prerequisite_sha256"],
        "preserved_first_campaign_failure": provenance[
            "preserved_first_campaign_failure"
        ],
        "historical_v3_support": provenance["historical_v3_support"],
        "synthetic": False,
        "performance": "NOT MEASURED",
    }


def run_self_oracle(
    source_sha256: str,
    protocol_sha256: str,
) -> dict[str, Any]:
    provenance = authenticate_production_prerequisites(
        source_sha256, protocol_sha256,
    )
    official = introspect_official_sources()
    evidence = _run_isolated_worker("stdlib", source_sha256, protocol_sha256)
    try:
        _validate_role_evidence(
            "stdlib", evidence, official["public_method_matrix"],
        )
    except OfficialV4Error as error:
        raise OfficialV4WorkerFailure(
            "stdlib",
            "the actual complete original standard-library role did not qualify",
            {"actual_role_report": evidence, "validation_failure": str(error)},
        ) from error
    document = {
        **_base_official_document(source_sha256, protocol_sha256, provenance),
        "schema": SCHEMA + "-self-oracle",
        "status": "PASS",
        "roles": {"stdlib": evidence},
    }
    _exclusive_write(document, SELF_ORACLE_RELATIVE)
    return document


def run_candidates(
    selected: str,
    source_sha256: str,
    protocol_sha256: str,
    reference_sha256: str,
) -> dict[str, Any]:
    require(selected in {"all", "rust", "vm", "zig"},
            "an explicitly approved exact original role is required")
    provenance = authenticate_production_prerequisites(
        source_sha256, protocol_sha256,
    )
    official = introspect_official_sources()
    matrix = official["public_method_matrix"]
    baseline = _read_verified_evidence(SELF_ORACLE_RELATIVE, reference_sha256)
    require(
        isinstance(baseline, Mapping)
        and baseline.get("schema") == SCHEMA + "-self-oracle"
        and baseline.get("status") == "PASS"
        and baseline.get("source_sha256") == source_sha256
        and baseline.get("protocol_sha256") == protocol_sha256
        and baseline.get("public_method_matrix_sha256") == METHOD_MATRIX_SHA256
        and isinstance(baseline.get("roles"), Mapping)
        and set(baseline["roles"]) == {"stdlib"},
        "a genuinely complete real V4 standard-library reference is required",
    )
    baseline_role = baseline["roles"]["stdlib"]
    require(isinstance(baseline_role, Mapping),
            "the authentic complete V4 standard-library role is missing")
    _validate_role_evidence("stdlib", baseline_role, matrix)
    chosen = ("rust", "vm", "zig") if selected == "all" else (selected,)
    for role in chosen:
        require(
            not _safe_output_path(ROLE_REPORT_RELATIVES[role]).exists(),
            "a genuine V4 role report already exists: " + role,
        )
    if selected == "all":
        require(not _safe_output_path(REPORT_RELATIVE).exists(),
                "the exclusively created complete V4 report already exists")
    reports: dict[str, Any] = {"stdlib": baseline_role}
    for role in chosen:
        evidence = _run_isolated_worker(role, source_sha256, protocol_sha256)
        try:
            _validate_role_evidence(role, evidence, matrix)
            require(
                tuple(
                    (
                        item["test"], item["status"],
                        item.get("skip_kind"), item.get("reason"),
                    )
                    for item in evidence["records"]
                ) == tuple(
                    (
                        item["test"], item["status"],
                        item.get("skip_kind"), item.get("reason"),
                    )
                    for item in baseline_role["records"]
                ),
                "the genuine native official status vector differs from Python",
            )
        except OfficialV4Error as error:
            raise OfficialV4WorkerFailure(
                role,
                "the actual complete original native role did not qualify: " + role,
                {"actual_role_report": evidence, "validation_failure": str(error)},
            ) from error
        role_report = {
            **_base_official_document(source_sha256, protocol_sha256, provenance),
            "schema": SCHEMA + "-actual-" + role + "-role",
            "status": "PASS",
            "reference_sha256": reference_sha256,
            "roles": {role: evidence},
        }
        _exclusive_write(role_report, ROLE_REPORT_RELATIVES[role])
        reports[role] = evidence
    if selected != "all":
        return {
            "schema": SCHEMA + "-single-candidate-result",
            "status": "PASS",
            "role": selected,
            "path": ROLE_REPORT_RELATIVES[selected],
            "methods": PUBLIC_METHODS,
            "performance": "NOT MEASURED",
        }
    document = {
        **_base_official_document(source_sha256, protocol_sha256, provenance),
        "schema": SCHEMA,
        "status": "PASS",
        "reference_path": SELF_ORACLE_RELATIVE,
        "reference_sha256": reference_sha256,
        "roles": reports,
    }
    validate_official_report(document, matrix)
    _exclusive_write(document, REPORT_RELATIVE)
    return document


@contextlib.contextmanager
def _source_only_boundary() -> Any:
    """Make clocks, workers, candidate imports, and all writes impossible."""
    counts = {
        "clock_attempts_blocked": 0,
        "worker_attempts_blocked": 0,
        "candidate_import_attempts_blocked": 0,
        "write_attempts_blocked": 0,
        "evidence_read_attempts_blocked": 0,
        "unauthorized_read_attempts_blocked": 0,
        "locale_attempts_blocked": 0,
    }
    replacements: list[tuple[Any, str, Any]] = []

    def reject_effect(kind: str, label: str) -> Any:
        def blocked(*args: Any, **kwargs: Any) -> Any:
            del args, kwargs
            counts[kind] += 1
            raise OfficialV4Error(
                "the genuine source-only V4 boundary forbids " + label,
            )

        return blocked

    def replace(target: Any, name: str, substitute: Any) -> None:
        if not hasattr(target, name):
            return
        previous = getattr(target, name)
        replacements.append((target, name, previous))
        setattr(target, name, substitute)

    for name in (
        "time", "time_ns", "monotonic", "monotonic_ns",
        "perf_counter", "perf_counter_ns", "process_time",
        "process_time_ns", "thread_time", "thread_time_ns",
    ):
        replace(time, name, reject_effect("clock_attempts_blocked", "clock " + name))
    for target, name in (
        (subprocess, "run"),
        (subprocess, "Popen"),
        (threading.Thread, "start"),
        (multiprocessing.Process, "start"),
    ):
        replace(
            target, name,
            reject_effect("worker_attempts_blocked", "worker " + name),
        )
    for name in ("fork", "posix_spawn", "posix_spawnp", "system"):
        replace(
            os, name,
            reject_effect("worker_attempts_blocked", "process " + name),
        )
    def allowed_read(path: Any) -> bool:
        if not isinstance(path, (str, bytes, os.PathLike)):
            return False
        try:
            actual = Path(os.fsdecode(path)).resolve()
        except (OSError, TypeError, ValueError):
            return False
        official_files = {
            (ROOT / TEST_SOURCE_RELATIVE).resolve(),
            (ROOT / CORPUS_SOURCE_RELATIVE).resolve(),
            UPSTREAM_ARCHIVE.resolve(),
        }
        return (
            actual in official_files
            or actual.is_relative_to((UPSTREAM_LIB / "test").resolve())
        )

    original_open = os.open

    def checked_open(path: Any, flags: int, *args: Any, **kwargs: Any) -> int:
        write_flags = (
            os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC
            | getattr(os, "O_APPEND", 0)
        )
        if flags & write_flags:
            counts["write_attempts_blocked"] += 1
            raise OfficialV4Error("a source-only official control cannot write")
        if not allowed_read(path):
            counts["unauthorized_read_attempts_blocked"] += 1
            raise OfficialV4Error(
                "a source-only control cannot inspect unrelated data or evidence",
            )
        return original_open(path, flags, *args, **kwargs)

    replace(os, "open", checked_open)

    def readonly_file_opener(original: Any) -> Any:
        def guarded(
            file: Any,
            mode: str = "r",
            *args: Any,
            **kwargs: Any,
        ) -> Any:
            if not isinstance(mode, str) or any(
                character in mode for character in ("w", "a", "x", "+")
            ):
                counts["write_attempts_blocked"] += 1
                raise OfficialV4Error(
                    "a source-only official control cannot open a writable file",
                )
            if not allowed_read(file):
                counts["unauthorized_read_attempts_blocked"] += 1
                raise OfficialV4Error(
                    "a source-only control cannot open unrelated data or evidence",
                )
            return original(file, mode, *args, **kwargs)

        return guarded

    replace(builtins, "open", readonly_file_opener(builtins.open))
    replace(io, "open", readonly_file_opener(io.open))
    for name in ("unlink", "remove", "rename", "replace", "mkdir", "makedirs"):
        replace(os, name,
                reject_effect("write_attempts_blocked", "filesystem " + name))
    replace(
        tempfile, "TemporaryDirectory",
        reject_effect("locale_attempts_blocked", "temporary private locale"),
    )
    module = sys.modules[__name__]
    replace(
        module, "_exclusive_write",
        reject_effect("write_attempts_blocked", "exclusive evidence output"),
    )
    replace(
        module, "_read_verified_evidence",
        reject_effect("evidence_read_attempts_blocked", "production evidence"),
    )
    replace(
        module, "_run_isolated_worker",
        reject_effect("worker_attempts_blocked", "isolated native worker"),
    )
    previous_import = importlib.import_module
    previous_builtin_import = builtins.__import__

    def checked_import(name: str, package: str | None = None) -> Any:
        if name == "rebar" or name.startswith("rebar.") or (
            name == "candidates" or name.startswith("candidates.")
        ):
            counts["candidate_import_attempts_blocked"] += 1
            raise OfficialV4Error(
                "a native candidate cannot be imported by source-only controls",
            )
        return previous_import(name, package)

    replace(importlib, "import_module", checked_import)

    def checked_builtin_import(
        name: str,
        globals: Any = None,
        locals: Any = None,
        fromlist: Any = (),
        level: int = 0,
    ) -> Any:
        if name == "rebar" or name.startswith("rebar.") or (
            name == "candidates" or name.startswith("candidates.")
        ):
            counts["candidate_import_attempts_blocked"] += 1
            raise OfficialV4Error(
                "a native candidate cannot enter through Python import syntax",
            )
        return previous_builtin_import(name, globals, locals, fromlist, level)

    replace(builtins, "__import__", checked_builtin_import)
    try:
        yield counts
    finally:
        for target, name, previous in reversed(replacements):
            setattr(target, name, previous)


def _source_self_test_body(
    official: Mapping[str, Any],
    environment: Mapping[str, Any],
    effect_counts: Mapping[str, int],
) -> dict[str, Any]:
    matrix = official["public_method_matrix"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: Any) -> None:
        require(not any(item["name"] == name for item in checks),
                "a genuine V4 synthetic source control was duplicated")
        checks.append({"name": name, "passed": bool(condition)})

    def reject(name: str, operation: Any) -> None:
        try:
            operation()
        except (OfficialV4Error, KeyError, TypeError, ValueError):
            check(name, True)
        else:
            check(name, False)

    check("pin-exact-original-cpython-3.14.6-test-source",
          official["test_source_sha256"] == TEST_SOURCE_SHA256)
    check("pin-exact-original-cpython-3.14.6-corpus-source",
          official["corpus_source_sha256"] == CORPUS_SOURCE_SHA256)
    check("authenticate-the-genuine-official-cpython-source-archive",
          environment["upstream_archive_sha256"] == UPSTREAM_ARCHIVE_SHA256)
    check("authenticate-all-26-real-official-test-support-modules",
          environment["official_support_tree_sha256"]
          == OFFICIAL_SUPPORT_TREE_SHA256
          and environment["official_support_module_count"] == 26
          and environment["authenticated_official_support_available"] is True)
    check("reject-a-fabricated-unconditional-skip-support-shim",
          environment["official_support_shim_used"] is False
          and environment["official_test_source_rewritten"] is False)
    check("recognize-real-upstream-cpu-resource-default",
          environment["cpu_resource_enabled_by_authentic_default"] is True)
    check("detect-the-real-upstream-zero-memory-dry-run-default",
          environment["real_max_memuse_initial"] == 0
          and environment["nominal_big_memory_tests_actually_executed"]
          is False)
    check("classify-all-165-genuine-upstream-methods",
          official["all_original_methods"] == 165)
    check("preserve-all-152-original-public-method-identities",
          tuple(item["test"] for item in matrix) == PUBLIC_ORIGINAL_METHODS)
    check("exclude-only-13-methods-in-two-named-private-classes",
          official["private_original_methods"] == 13
          and official["named_private_class_waivers"] == PRIVATE_CLASS_WAIVERS)
    check("never-waive-a-single-original-public-method",
          official["public_method_waivers"] == []
          and not PUBLIC_METHOD_WAIVERS)
    check("include-all-six-formerly-omitted-original-public-methods",
          set(FORMERLY_WAIVED_PUBLIC_METHODS)
          <= {record["test"] for record in matrix})
    check("count-all-400-original-and-three-extended-corpus-cases",
          official["initial_case_count"] == 400
          and official["actual_extended_case_count"] == 3
          and official["actual_upstream_corpus_cases"] == 403
          and environment["live_upstream_corpus_cases"] == 403)
    check("preserve-all-eleven-live-external-fixture-correctness-assertions",
          official["actual_external_fixture_assertion_cases"] == 11
          and environment["live_external_fixture_assertion_cases"] == 11)
    check("preserve-both-genuine-fresh-locale-methods",
          REQUIRED_LOCALE_METHODS <= set(PUBLIC_ORIGINAL_METHODS))
    check("preserve-all-six-exact-original-resource-decorators",
          set(official["official_resource_requirements"])
          == set(FORMERLY_WAIVED_PUBLIC_METHODS))
    check("preserve-exact-36-gibibyte-upstream-subn-memory-declaration",
          official["official_resource_requirements"]
          ["ReTests.test_large_subn"]["declared_memory_bytes"]
          == 38_654_705_664)
    check("keep-official-external-fixture-assertions-as-correctness",
          "ExternalTests.test_re_benchmarks" in PUBLIC_ORIGINAL_METHODS)
    check("keep-source-only-standard-library-isolation",
          environment["candidate_imports"] == 0
          and environment["native_workers_started"] == 0
          and environment["official_tests_executed"] == 0)
    check("never-read-performance-or-holdout-data",
          environment["performance_fixtures_read"] == 0
          and environment["holdout_cases_read"] == 0
          and environment["performance_oracle_executed"] is False)

    synthetic = [
        {
            "test": item["test"],
            "source_ast_sha256": item["source_ast_sha256"],
            "status": "PASS",
        }
        for item in matrix
    ]
    sample = assess_role_records("stdlib", synthetic, matrix)
    check("separately-validate-all-152-in-memory-role-record-identities",
          sample["status"] == "PASS"
          and sample["passed"] == 152
          and sample["skipped"] == 0
          and sample["record_count"] == 152)

    skipped = [dict(item) for item in synthetic]
    leak_index = PUBLIC_ORIGINAL_METHODS.index("ReTests.test_memory_leaks")
    skipped[leak_index]["status"] = "SKIP"
    skipped[leak_index]["reason"] = "requires debug build"
    skipped[leak_index]["skip_kind"] = "named-private-debug-condition"
    actual_skip = assess_role_records("stdlib", skipped, matrix)
    check("preserve-one-exact-named-private-debug-condition-not-a-public-waiver",
          actual_skip["status"] == "PASS"
          and actual_skip["applicable"] == 151
          and actual_skip["passed"] == 151
          and actual_skip["skipped"] == 1
          and actual_skip["named_private_debug_skips"] == 1
          and actual_skip["unexplained_skips"] == 0
          and actual_skip["debug_build_coverage"] == "NOT RUN")

    synthetic_release_records = copy.deepcopy(skipped)
    for record in synthetic_release_records:
        identity = record["test"]
        if identity in {
            "ReTests.test_large_search", "ReTests.test_large_subn",
        }:
            record["resource"] = {
                "delivered_size": 2**31,
                "real_max_memuse": CONFIGURED_OFFICIAL_MEMORY_BYTES,
                "declared_size": 2**31,
                "dry_run": False,
            }
        elif identity == "ReTests.test_regression_gh94675":
            record["resource"] = {
                "process_started": True,
                "start_method": "fork",
                "short_timeout_seconds": 30.0,
            }
        elif identity == "ReTests.test_search_anchor_at_beginning":
            record["resource"] = {
                "cpu_resource_enabled": True,
                "subject_characters": 10**7,
                "original_upper_bound_seconds": 0.1,
                "original_stopwatch_assertion_passed": True,
            }
    synthetic_release_summary = assess_role_records(
        "stdlib", synthetic_release_records, matrix,
    )
    synthetic_release = {
        **synthetic_release_summary,
        "records": synthetic_release_records,
        "locale": {
            "fresh_private_localedef": True,
            "iso_8859_1_passed": True,
            "utf_8_passed": True,
        },
        "guard": {
            "passed": True,
            "candidate_isolation": True,
            "baseline_only": True,
        },
        "resource_provenance": {
            "real_max_memuse": CONFIGURED_OFFICIAL_MEMORY_BYTES,
            "large_method_sizes": {
                "ReTests.test_large_search": 2**31,
                "ReTests.test_large_subn": 2**31,
            },
            "cpu_resource_enabled": True,
            "multiprocessing_extension_available": True,
            "multiprocessing_start_method": "fork",
            "private_debug_fail_after": False,
            "actual_upstream_corpus_cases": CORPUS_CASES,
            "actual_external_fixture_assertion_cases": (
                EXTERNAL_FIXTURE_ASSERTION_CASES
            ),
            "exclusive_big_memory_worker": True,
            "official_support_shim_used": False,
            "official_test_source_rewritten": False,
        },
        "executed_test_source_sha256": TEST_SOURCE_SHA256,
        "official_support_tree_sha256": OFFICIAL_SUPPORT_TREE_SHA256,
        "live_official_fixture_provenance": {
            "modules": {
                "test.support": {
                    "path": str(UPSTREAM_LIB / "test" / "support" / "__init__.py"),
                    "sha256": UPSTREAM_SUPPORT_INIT_SHA256,
                },
                "test.support.warnings_helper": {
                    "path": str(
                        UPSTREAM_LIB / "test" / "support" / "warnings_helper.py",
                    ),
                    "sha256": UPSTREAM_WARNINGS_HELPER_SHA256,
                },
                "test.re_tests": {
                    "path": str(UPSTREAM_LIB / "test" / "re_tests.py"),
                    "sha256": CORPUS_SOURCE_SHA256,
                },
            },
            "actual_upstream_corpus_cases": CORPUS_CASES,
            "actual_external_fixture_assertion_cases": (
                EXTERNAL_FIXTURE_ASSERTION_CASES
            ),
            "support_tree_sha256": OFFICIAL_SUPPORT_TREE_SHA256,
            "official_support_shim_used": False,
        },
    }
    check("validate-only-in-memory-real-152-record-release-role-shape",
          _validate_role_evidence("stdlib", synthetic_release, matrix)
          == synthetic_release_summary)

    dry_run = copy.deepcopy(synthetic_release)
    for record in dry_run["records"]:
        if record["test"] == "ReTests.test_large_subn":
            record["resource"]["delivered_size"] = 5_147
            record["resource"]["dry_run"] = True
    dry_run.update(assess_role_records("stdlib", dry_run["records"], matrix))
    reject("reject-an-official-5147-item-bigmem-dry-run",
           lambda: _validate_role_evidence("stdlib", dry_run, matrix))
    insufficient = copy.deepcopy(synthetic_release)
    insufficient["resource_provenance"]["real_max_memuse"] = 0
    reject("reject-a-real-bigmem-method-without-its-36-gibibyte-budget",
           lambda: _validate_role_evidence("stdlib", insufficient, matrix))
    changed_budget = copy.deepcopy(synthetic_release)
    changed_budget["resource_provenance"]["real_max_memuse"] = (
        REQUIRED_OFFICIAL_SUBN_MEMORY_BYTES
    )
    reject("reject-a-substituted-36-gibibyte-limit-for-the-frozen-40-gibibyte-role",
           lambda: _validate_role_evidence("stdlib", changed_budget, matrix))
    no_process = copy.deepcopy(synthetic_release)
    for record in no_process["records"]:
        if record["test"] == "ReTests.test_regression_gh94675":
            record["resource"]["process_started"] = False
    no_process.update(assess_role_records("stdlib", no_process["records"], matrix))
    reject("reject-a-GH94675-pass-without-an-actual-process",
           lambda: _validate_role_evidence("stdlib", no_process, matrix))
    no_cpu = copy.deepcopy(synthetic_release)
    no_cpu["resource_provenance"]["cpu_resource_enabled"] = False
    reject("reject-a-disabled-original-CPU-resource",
           lambda: _validate_role_evidence("stdlib", no_cpu, matrix))
    false_debug = copy.deepcopy(synthetic_release)
    false_debug["resource_provenance"]["private_debug_fail_after"] = True
    reject("reject-a-false-private-debug-hook-claim",
           lambda: _validate_role_evidence("stdlib", false_debug, matrix))
    fabricated_support = copy.deepcopy(synthetic_release)
    fabricated_support["resource_provenance"]["official_support_shim_used"] = True
    reject("reject-a-historical-shim-as-genuine-upstream-support",
           lambda: _validate_role_evidence("stdlib", fabricated_support, matrix))
    changed_source = copy.deepcopy(synthetic_release)
    changed_source["resource_provenance"]["official_test_source_rewritten"] = True
    reject("reject-a-rewritten-original-official-test-source",
           lambda: _validate_role_evidence("stdlib", changed_source, matrix))

    unclassified = [dict(item) for item in skipped]
    del unclassified[leak_index]["skip_kind"]
    check("an-unclassified-original-release-skip-cannot-qualify",
          assess_role_records("stdlib", unclassified, matrix)["status"]
          == "BLOCKED")
    wrong_private_skip = [dict(item) for item in synthetic]
    wrong_private_skip[0]["status"] = "SKIP"
    wrong_private_skip[0]["reason"] = "requires debug build"
    wrong_private_skip[0]["skip_kind"] = "named-private-debug-condition"
    check("reject-a-private-debug-excuse-for-any-other-public-method",
          assess_role_records("stdlib", wrong_private_skip, matrix)["status"]
          == "BLOCKED")

    failed = [dict(item) for item in synthetic]
    failed[0]["status"] = "FAIL"
    failed[0]["reason"] = "synthetic poison; not an executed upstream test"
    check("a-preserved-original-method-failure-never-qualifies",
          assess_role_records("stdlib", failed, matrix)["status"] == "FAIL")
    reject("reject-an-omitted-original-public-method",
           lambda: assess_role_records("stdlib", synthetic[:-1], matrix))
    swapped = [dict(item) for item in synthetic]
    swapped[0], swapped[1] = swapped[1], swapped[0]
    reject("reject-reordered-original-method-identities",
           lambda: assess_role_records("stdlib", swapped, matrix))
    substituted = [dict(item) for item in synthetic]
    substituted[0]["source_ast_sha256"] = "0" * 64
    reject("reject-a-substituted-original-method-body",
           lambda: assess_role_records("stdlib", substituted, matrix))
    concealed = [dict(item) for item in skipped]
    del concealed[leak_index]["reason"]
    reject("reject-an-original-skip-without-its-actual-reason",
           lambda: assess_role_records("stdlib", concealed, matrix))
    reject("reject-an-unapproved-candidate-role",
           lambda: assess_role_records("external-package", synthetic, matrix))
    reject("reject-any-unpublished-production-prerequisite", published_pins)
    reject("never-classify-synthetic-records-as-a-genuine-V4-report",
           lambda: validate_official_report({"synthetic": True}, matrix))
    shim = types.ModuleType("test.support")
    reject("reject-the-historical-module-type-unconditional-skip-shim",
           lambda: _validate_preloaded_support({"test.support": shim}))
    raw_original = read_pinned_source(TEST_SOURCE_RELATIVE, TEST_SOURCE_SHA256)
    prefix, original_import, suffix = raw_original.partition(b"\nimport re\n")
    require(original_import == b"\nimport re\n",
            "the genuine original regex import is required for its poison control")
    rewritten_import = prefix + b"\nimport synthetic_candidate as re\n" + suffix
    reject("reject-the-historical-original-import-source-replacement",
           lambda: _introspect_test_source(rewritten_import))
    prefix, original_scanner, suffix = raw_original.partition(
        b"from re import Scanner",
    )
    require(original_scanner == b"from re import Scanner",
            "the genuine original scanner import is required for its poison control")
    rewritten_scanner = (
        prefix + b"Scanner = getattr(re, 'Scanner', None)" + suffix
    )
    reject("reject-the-historical-original-Scanner-source-replacement",
           lambda: _introspect_test_source(rewritten_scanner))
    for name, path in (
        ("absolute", "/tmp/postfinal-locale-v4-forged.json"),
        ("traversal", "oracle/cpython-3.14.6/evidence/../forged.json"),
        ("previous-version", "oracle/cpython-3.14.6/evidence/postfinal-locale-v3-all.json"),
        ("backslash", "oracle\\cpython-3.14.6\\fake.json"),
    ):
        reject("reject-unsafe-or-historical-evidence-path-" + name,
               lambda path=path: _safe_output_path(path))

    for name in ("time", "monotonic", "perf_counter", "process_time"):
        if hasattr(time, name):
            reject("forbid-source-only-clock-" + name,
                   lambda name=name: getattr(time, name)())
    reject("forbid-source-only-subprocess-worker",
           lambda: subprocess.run([str(PINNED_CPYTHON), "-V"]))
    reject("forbid-source-only-thread-worker",
           lambda: threading.Thread(target=lambda: None).start())
    reject("forbid-source-only-native-candidate-import",
           lambda: importlib.import_module("candidates.rust_candidate"))
    reject("forbid-source-only-native-candidate-builtin-import",
           lambda: builtins.__import__("candidates.rust_candidate"))
    reject("forbid-source-only-evidence-write",
           lambda: _exclusive_write({"synthetic": True}, REPORT_RELATIVE))
    reject("forbid-source-only-production-evidence-read",
           lambda: _read_verified_evidence(REPORT_RELATIVE, "0" * 64))
    reject("forbid-source-only-private-locale-or-temporary-directory",
           lambda: tempfile.TemporaryDirectory())
    reject("forbid-source-only-filesystem-write",
           lambda: os.open(
               "/tmp/rebar-cpython-v4-forbidden-source-control",
               os.O_WRONLY | os.O_CREAT,
               0o600,
           ))
    reject("forbid-source-only-builtin-file-write",
           lambda: builtins.open(
               "/tmp/rebar-cpython-v4-forbidden-builtin-write", "w",
           ))
    reject("forbid-source-only-path-file-write",
           lambda: (ROOT / "v4-forbidden-source-control").open("w"))
    reject("forbid-source-only-unrelated-read",
           lambda: os.open(ROOT / "README.md", os.O_RDONLY))
    reject("forbid-source-only-unrelated-builtin-read",
           lambda: builtins.open(ROOT / "README.md", "r"))
    check("observe-and-block-every-source-only-external-effect",
          effect_counts["clock_attempts_blocked"] >= 4
          and effect_counts["worker_attempts_blocked"] >= 2
          and effect_counts["candidate_import_attempts_blocked"] >= 2
          and effect_counts["write_attempts_blocked"] >= 4
          and effect_counts["evidence_read_attempts_blocked"] >= 1
          and effect_counts["unauthorized_read_attempts_blocked"] >= 2
          and effect_counts["locale_attempts_blocked"] >= 1)

    blockers = diagnose_prerequisites(environment)
    if not environment["baseline_private_debug_fail_after"]:
        check("truthfully-observe-the-pinned-release-private-debug-hook",
              actual_skip["debug_build_coverage"] == "NOT RUN"
              and actual_skip["named_private_debug_skips"] == 1)
    check("never-confuse-installed-support-with-authenticated-extracted-support",
          environment["authenticated_official_support_available"] is True)
    check("never-infer-three-successful-campaigns",
          all(CAMPAIGN_REPORT_SHA256[role] is None
              for role in ("rust", "vm", "zig")))
    check("preserve-failed-first-campaign-as-a-failure-only",
          is_sha256(FIRST_CAMPAIGN_FAILURE_SHA256)
          and FIRST_CAMPAIGN_FAILURE_PHASE
          == "candidate-edge-proof-validation-before-first-campaign-stage")
    failures = [item["name"] for item in checks if item["passed"] is not True]
    require(not failures,
            "a V4 source-only control failed: " + ", ".join(failures))
    verify_runtime()
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS",
        "source_controls_passed": True,
        "check_count": len(checks),
        "checks": checks,
        "python": "3.14.6",
        "test_source_sha256": TEST_SOURCE_SHA256,
        "corpus_source_sha256": CORPUS_SOURCE_SHA256,
        "upstream_archive_sha256": UPSTREAM_ARCHIVE_SHA256,
        "official_support_tree_sha256": OFFICIAL_SUPPORT_TREE_SHA256,
        "official_support_module_count": len(OFFICIAL_SUPPORT_MODULES),
        "public_method_matrix_sha256": official["public_method_matrix_sha256"],
        "class_method_counts": official["class_method_counts"],
        "all_original_methods": ORIGINAL_METHODS,
        "public_original_methods": PUBLIC_METHODS,
        "private_original_methods": PRIVATE_METHODS,
        "public_method_waivers": [],
        "actual_upstream_corpus_cases": CORPUS_CASES,
        "actual_external_fixture_assertion_cases": (
            EXTERNAL_FIXTURE_ASSERTION_CASES
        ),
        "actual_extended_corpus_cases": CORPUS_EXTENSION_CASES,
        "environment": environment,
        "production_status": "BLOCKED" if blockers else "PREREQUISITES PUBLISHED",
        "production_blockers": blockers,
        "production_case_records": 0,
        "actual_official_roles_run": 0,
        "actual_official_method_checks": 0,
        "real_locale_methods_executed": 0,
        "pinned_repository_source_files_read": 2,
        "authenticated_official_support_modules": len(
            OFFICIAL_SUPPORT_MODULES
        ),
        "evidence_files_read": 0,
        "evidence_files_written": 0,
        "native_workers_started": 0,
        "candidate_imports": 0,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "timers_sampled": 0,
        "source_only_effect_attempts_blocked": dict(effect_counts),
        "performance": "NOT MEASURED",
    }


def source_self_test() -> dict[str, Any]:
    """Authenticate real sources, then prove no production side effect is possible."""
    verify_runtime()
    official = introspect_official_sources()
    environment = inspect_environment()
    candidate_before = {
        name for name, value in sys.modules.items()
        if value is not None
        and (
            name == "rebar" or name.startswith("rebar.")
            or name == "candidates" or name.startswith("candidates.")
        )
    }
    require(not candidate_before,
            "a native candidate was already present before source controls")
    with _source_only_boundary() as effect_counts:
        result = _source_self_test_body(official, environment, effect_counts)
        candidate_after = {
            name for name, value in sys.modules.items()
            if value is not None
            and (
                name == "rebar" or name.startswith("rebar.")
                or name == "candidates" or name.startswith("candidates.")
            )
        }
        require(candidate_after == candidate_before,
                "a native module escaped a source-only poison control")
    verify_runtime()
    return result


def preflight() -> dict[str, Any]:
    official = introspect_official_sources()
    environment = inspect_environment()
    blockers = diagnose_prerequisites(environment)
    return {
        "schema": SCHEMA + "-preflight",
        "status": "BLOCKED" if blockers else "PREREQUISITES PUBLISHED",
        "python": "3.14.6",
        "public_method_matrix_sha256": official["public_method_matrix_sha256"],
        "all_original_methods": ORIGINAL_METHODS,
        "public_original_methods": PUBLIC_METHODS,
        "private_original_methods": PRIVATE_METHODS,
        "actual_upstream_corpus_cases": CORPUS_CASES,
        "public_method_waivers": [],
        "blockers": blockers,
        "environment": environment,
        "official_tests_executed": 0,
        "native_workers_started": 0,
        "evidence_files_read": 0,
        "evidence_files_written": 0,
        "performance": "NOT MEASURED",
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect every unchanged CPython 3.14.6 public regex test without "
            "running candidates or inventing official passes."
        ),
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true",
                       help="run only frozen-source and in-memory poison controls")
    modes.add_argument("--preflight", action="store_true",
                       help="report real missing prerequisites without a worker")
    modes.add_argument(
        "--self-oracle", action="store_true",
        help="after publication, run one real isolated upstream stdlib role",
    )
    modes.add_argument(
        "--candidate", choices=("all", "rust", "vm", "zig"),
        help="after a genuine reference, run isolated actual native roles",
    )
    parser.add_argument(
        "--source-sha256",
        help="actual externally frozen and pushed V4 controller SHA-256",
    )
    parser.add_argument(
        "--protocol-sha256",
        help="actual externally frozen and pushed V4 protocol SHA-256",
    )
    parser.add_argument(
        "--reference-sha256",
        help="actual separately preserved V4 standard-library report SHA-256",
    )
    options = parser.parse_args(arguments)
    try:
        if options.self_test:
            document = source_self_test()
        elif options.preflight:
            document = preflight()
        elif options.self_oracle:
            require(
                is_sha256(options.source_sha256)
                and is_sha256(options.protocol_sha256),
                "BLOCKED: publish exact actual source/protocol hashes first",
            )
            document = run_self_oracle(
                options.source_sha256, options.protocol_sha256,
            )
        else:
            require(
                is_sha256(options.source_sha256)
                and is_sha256(options.protocol_sha256)
                and is_sha256(options.reference_sha256),
                "BLOCKED: publish exact actual source, protocol, and reference first",
            )
            document = run_candidates(
                options.candidate,
                options.source_sha256,
                options.protocol_sha256,
                options.reference_sha256,
            )
    except OfficialV4WorkerFailure as error:
        failure = {
            "schema": SCHEMA + "-actual-role-failure",
            "status": "FAIL",
            "role": error.role,
            "reason": str(error),
            "details": error.details,
            "source_sha256": options.source_sha256,
            "protocol_sha256": options.protocol_sha256,
            "performance": "NOT MEASURED",
        }
        failure_path = (
            SELF_ORACLE_FAILURE_RELATIVE
            if error.role == "stdlib" else FAILURE_RELATIVE
        )
        try:
            failure["exclusive_report_sha256"] = _exclusive_write(
                failure, failure_path,
            )
            failure["exclusive_report_path"] = failure_path
        except (OfficialV4Error, OSError) as preservation_error:
            failure["preservation_error"] = str(preservation_error)
        print(json.dumps(failure, sort_keys=True, separators=(",", ":")),
              file=sys.stderr)
        return 2
    except (OfficialV4Error, OSError) as error:
        print(json.dumps({
            "schema": SCHEMA + "-controller-failure",
            "status": "BLOCKED",
            "reason": str(error),
            "native_workers_started": 0,
            "evidence_files_written": 0,
            "performance": "NOT MEASURED",
        }, sort_keys=True, separators=(",", ":")), file=sys.stderr)
        return 2
    print(json.dumps(document, sort_keys=True, separators=(",", ":")))
    if options.preflight and document["status"] != "PREREQUISITES PUBLISHED":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
