from __future__ import annotations

from array import array
from collections.abc import Callable
from collections import Counter
from dataclasses import dataclass
from itertools import product
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
from types import SimpleNamespace

import pytest

import rebar
from rebar_harness import benchmarks
from rebar_harness.correctness import (
    CORRECTNESS_FIXTURES_ROOT,
    FixtureCase,
    normalize_exported_symbol_metadata,
    normalize_exported_symbol_value,
    normalize_pattern_object_metadata,
)
from tests.conftest import PYTHON_SOURCE
from tests.python import conftest as python_conftest
from tests.python.conftest import _unsupported_backend_skip_reason
from tests.python.fixture_parity_support import (
    FixtureBundle,
    RecordingNativeBoundary,
    assert_direct_test_case_id_buckets_cover_selected_frontier,
    assert_fixture_bundle_contract,
    assert_fixture_bundle_tracks_published_case_frontier,
    assert_finditer_parity,
    assert_match_convenience_api_parity,
    assert_match_result_parity,
    assert_pattern_parity,
    assert_placeholder_message_contains,
    assert_value_parity,
    build_fixture_bundle,
    case_pattern,
    compile_with_cpython_parity,
    fixture_cases_for_operation,
    load_published_fixture_bundles,
    published_fixture_bundle_by_manifest_id,
)

MATURIN = shutil.which("maturin")
_BUILT_WHEEL_SMOKE_PROBE = textwrap.dedent(
    """
    import json
    import rebar
    import rebar._rebar as native

    result = {
        "native_module_loaded": rebar.native_module_loaded(),
        "native_scaffold_status": rebar.native_scaffold_status(),
        "native_target_cpython_series": rebar.native_target_cpython_series(),
        "native_private_flag": getattr(native, "__rebar_scaffold__", False),
        "native_module_name": native.__name__,
        "exported_helpers_present": all(
            hasattr(rebar, name)
            for name in (
                "search",
                "match",
                "fullmatch",
                "split",
                "findall",
                "finditer",
                "template",
                "purge",
            )
        ),
        "purge_result": rebar.purge(),
    }

    try:
        rebar.template("abc")
    except Exception as exc:
        result["template_exception"] = {
            "type": type(exc).__name__,
            "message": str(exc),
        }
    else:
        result["template_exception"] = None

    try:
        compiled = rebar.compile("abc", rebar.IGNORECASE)
    except Exception as exc:
        result["compile_exception"] = {
            "type": type(exc).__name__,
            "message": str(exc),
        }
    else:
        result["compile_exception"] = None
        result["compiled_pattern"] = {
            "type_name": type(compiled).__name__,
            "type_module": type(compiled).__module__,
            "pattern": compiled.pattern,
            "flags": compiled.flags,
            "groups": compiled.groups,
            "groupindex": compiled.groupindex,
        }
        try:
            compiled_search = compiled.search("abc")
        except Exception as exc:
            result["compiled_search_exception"] = {
                "type": type(exc).__name__,
                "message": str(exc),
            }
        else:
            result["compiled_search_exception"] = None
            result["compiled_search"] = {
                "type_name": type(compiled_search).__name__,
                "group0": compiled_search.group(0),
                "span": list(compiled_search.span()),
            }

    search_match = rebar.search("abc", "zzabczz")
    full_match = rebar.fullmatch("abc", "abc")
    result["literal_search"] = {
        "type_name": type(search_match).__name__,
        "group0": search_match.group(0),
        "span": list(search_match.span()),
    }
    result["literal_match_none"] = rebar.match("abc", "zabc")
    result["literal_fullmatch"] = {
        "type_name": type(full_match).__name__,
        "group0": full_match.group(0),
        "span": list(full_match.span()),
    }
    result["literal_split"] = rebar.split("abc", "abcabc", 1)
    result["literal_findall"] = rebar.findall("abc", "zabcabc")
    result["literal_finditer"] = [
        {
            "type_name": type(match).__name__,
            "group0": match.group(0),
            "span": list(match.span()),
        }
        for match in rebar.finditer("abc", "zabcabc")
    ]
    result["escape_outputs"] = {
        "simple_str": rebar.escape("a-b.c"),
        "punctuation_str": rebar.escape(' !"#%&,/:;<=>@`~'),
        "simple_bytes": rebar.escape(b"a-b.c").decode("latin-1"),
    }

    print(json.dumps(result))
    """
)


MODULE_WORKFLOW_FIXTURE_PATH = CORRECTNESS_FIXTURES_ROOT / "module_workflow_surface.py"
MATCH_BEHAVIOR_FIXTURE_PATH = CORRECTNESS_FIXTURES_ROOT / "match_behavior_smoke.py"
MODULE_WORKFLOW_BOUNDED_WILDCARD_COMPILE_CASE_IDS = (
    "workflow-compile-str-bounded-wildcard",
    "workflow-compile-str-bounded-wildcard-ignorecase",
)
MODULE_WORKFLOW_BOUNDED_WILDCARD_PATTERN_CASE_IDS = (
    "workflow-pattern-search-str-bounded-wildcard-ignorecase",
    "workflow-pattern-match-str-bounded-wildcard",
    "workflow-pattern-fullmatch-str-bounded-wildcard",
    "workflow-pattern-findall-str-bounded-wildcard",
    "workflow-pattern-finditer-str-bounded-wildcard",
    "workflow-pattern-search-str-bounded-wildcard-endpos-miss",
)


def _published_case_ids(bundle: FixtureBundle) -> tuple[str, ...]:
    return tuple(case.case_id for case in bundle.manifest.cases)


def _fixture_cases_for_helpers(
    bundle: FixtureBundle,
    helpers: frozenset[str],
) -> tuple[FixtureCase, ...]:
    return tuple(case for case in bundle.cases if case.helper in helpers)


(MODULE_WORKFLOW_BUNDLE, MATCH_BEHAVIOR_BUNDLE) = load_published_fixture_bundles(
    (MODULE_WORKFLOW_FIXTURE_PATH, MATCH_BEHAVIOR_FIXTURE_PATH)
)

COMPILE_CASES = fixture_cases_for_operation((MODULE_WORKFLOW_BUNDLE,), "compile")
COMPILE_CASES_BY_ID = {case.case_id: case for case in COMPILE_CASES}
NOFLAG_COMPILE_CASES = tuple(
    case for case in COMPILE_CASES if (case.flags or 0) == 0
)
VERBOSE_COMPILE_CASE_ID = "workflow-compile-str-verbose-regression"
MULTILINE_COMPILE_CASE_ID = "workflow-compile-str-multiline-regression"
VERBOSE_BYTES_COMPILE_CASE_ID = "workflow-compile-bytes-verbose-regression"
MULTILINE_BYTES_COMPILE_CASE_ID = "workflow-compile-bytes-multiline-regression"
(VERBOSE_COMPILE_CASE,) = tuple(
    case for case in COMPILE_CASES if case.case_id == VERBOSE_COMPILE_CASE_ID
)
(VERBOSE_BYTES_COMPILE_CASE,) = tuple(
    case for case in COMPILE_CASES if case.case_id == VERBOSE_BYTES_COMPILE_CASE_ID
)
(MULTILINE_COMPILE_CASE,) = tuple(
    case for case in COMPILE_CASES if case.case_id == MULTILINE_COMPILE_CASE_ID
)
(MULTILINE_BYTES_COMPILE_CASE,) = tuple(
    case for case in COMPILE_CASES if case.case_id == MULTILINE_BYTES_COMPILE_CASE_ID
)
PATTERN_CASES = fixture_cases_for_operation((MODULE_WORKFLOW_BUNDLE,), "pattern_call")
MATCH_HELPER_PATTERN_CASES = tuple(
    case
    for case in PATTERN_CASES
    if case.helper in {"search", "match", "fullmatch"}
)
CACHE_CASES = fixture_cases_for_operation((MODULE_WORKFLOW_BUNDLE,), "cache_workflow")
PURGE_CASES = fixture_cases_for_operation((MODULE_WORKFLOW_BUNDLE,), "purge_workflow")
MODULE_CALL_CASES = fixture_cases_for_operation((MODULE_WORKFLOW_BUNDLE,), "module_call")
PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASES = tuple(
    case
    for case in MODULE_CALL_CASES
    if not case.use_compiled_pattern
    and case_pattern(case) == "a.c"
    and case.helper in {"search", "match", "fullmatch"}
)
PUBLISHED_MODULE_KEYWORD_MODULE_HELPER_CASES = tuple(
    case
    for case in MODULE_CALL_CASES
    if case.case_id
    in {
        "workflow-module-search-flags-keyword-str",
        "workflow-module-match-flags-keyword-bytes",
        "workflow-module-fullmatch-flags-keyword-str",
        "workflow-module-split-maxsplit-keyword-bytes",
        "workflow-module-split-maxsplit-indexlike-bytes",
        "workflow-module-sub-count-keyword-str",
        "workflow-module-sub-count-indexlike-str",
        "workflow-module-subn-count-keyword-bytes",
        "workflow-module-subn-count-indexlike-bytes",
    }
)
PUBLISHED_MODULE_KEYWORD_ERROR_MODULE_HELPER_CASES = tuple(
    case
    for case in MODULE_CALL_CASES
    if case.case_id
    in {
        "workflow-module-search-duplicate-flags-keyword",
        "workflow-module-split-duplicate-maxsplit-keyword",
        "workflow-module-sub-duplicate-count-keyword",
        "workflow-module-fullmatch-unexpected-keyword",
        "workflow-module-sub-unexpected-keyword",
    }
)
PUBLISHED_PATTERN_KEYWORD_PATTERN_CASES = tuple(
    case
    for case in PATTERN_CASES
    if case.case_id
    in {
        "workflow-pattern-search-str-pos-keyword",
        "workflow-pattern-search-str-bool-endpos-keyword",
        "workflow-pattern-search-bytes-endpos-keyword",
        "workflow-pattern-search-str-pos-indexlike",
        "workflow-pattern-search-bytes-endpos-indexlike",
        "workflow-pattern-match-str-pos-keyword",
        "workflow-pattern-match-str-bool-pos-keyword",
        "workflow-pattern-fullmatch-bytes-window-keyword",
        "workflow-pattern-fullmatch-bytes-window-indexlike",
        "workflow-pattern-findall-str-window-keyword",
        "workflow-pattern-findall-str-window-indexlike",
        "workflow-pattern-findall-str-bool-window-keyword",
        "workflow-pattern-finditer-bytes-window-keyword",
        "workflow-pattern-finditer-bytes-window-indexlike",
        "workflow-pattern-finditer-bytes-bool-window-keyword",
        "workflow-pattern-split-str-maxsplit-keyword",
        "workflow-pattern-split-str-maxsplit-indexlike",
        "workflow-pattern-sub-count-keyword-bytes",
        "workflow-pattern-sub-count-indexlike-bytes",
        "workflow-pattern-subn-count-keyword-str",
        "workflow-pattern-subn-count-indexlike-str",
    }
)
PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES = tuple(
    case
    for case in MODULE_CALL_CASES
    if case.use_compiled_pattern
)


def _fixture_cases_for_text_model(
    cases: tuple[FixtureCase, ...],
    text_model: str,
) -> tuple[FixtureCase, ...]:
    return tuple(
        case
        for case in cases
        if case.text_model == text_model
    )


def _workflow_keyword_kwargs_signature(
    kwargs: dict[str, object],
) -> tuple[tuple[str, str, object], ...]:
    signature: list[tuple[str, str, object]] = []
    for name, value in sorted(kwargs.items()):
        if isinstance(value, bool):
            signature.append((name, "bool", value))
            continue
        if isinstance(value, int):
            signature.append((name, "int", int(value)))
            continue
        if hasattr(value, "__index__"):
            signature.append((name, "indexlike", int(value.__index__())))
            continue
        signature.append((name, type(value).__name__, repr(value)))
    return tuple(signature)


ESCAPE_CASES = tuple(
    case
    for case in MODULE_CALL_CASES
    if case.helper == "escape"
)
PATTERN_CASES_BY_ID = {case.case_id: case for case in PATTERN_CASES}
VERBOSE_BYTES_SEARCH_PATTERN_CASE = PATTERN_CASES_BY_ID[
    "workflow-pattern-search-bytes-verbose-regression"
]
VERBOSE_BYTES_FULLMATCH_PATTERN_CASE = PATTERN_CASES_BY_ID[
    "workflow-pattern-fullmatch-bytes-verbose-regression"
]


PUBLISHED_BOUNDED_WILDCARD_COMPILE_CASES = tuple(
    COMPILE_CASES_BY_ID[case_id]
    for case_id in MODULE_WORKFLOW_BOUNDED_WILDCARD_COMPILE_CASE_IDS
)
PUBLISHED_BOUNDED_WILDCARD_PATTERN_CASES = tuple(
    PATTERN_CASES_BY_ID[case_id]
    for case_id in MODULE_WORKFLOW_BOUNDED_WILDCARD_PATTERN_CASE_IDS
)
PUBLISHED_BOUNDED_WILDCARD_PATTERN_MATCH_CASES = tuple(
    case
    for case in PUBLISHED_BOUNDED_WILDCARD_PATTERN_CASES
    if case.helper in {"search", "match", "fullmatch"}
)
PUBLISHED_BOUNDED_WILDCARD_PATTERN_COLLECTION_CASES = tuple(
    case
    for case in PUBLISHED_BOUNDED_WILDCARD_PATTERN_CASES
    if case.helper in {"findall", "finditer"}
)


def _public_surface_loader_token(case: FixtureCase) -> str | bytes:
    if case.pattern is None and not case.args:
        return case.case_id
    return case_pattern(case)

PUBLIC_SURFACE_EXPECTED_TEXT_MODELS_BY_MANIFEST_ID = {
    "pattern-object-surface": frozenset({"bytes", "str"})
}


# Keep the public-surface coverage on the module workflow owner file.
ADDITIONAL_PUBLIC_HELPER_NAMES = (
    pytest.param("match", id="match"),
    pytest.param("fullmatch", id="fullmatch"),
    pytest.param("split", id="split"),
    pytest.param("findall", id="findall"),
    pytest.param("finditer", id="finditer"),
    pytest.param("sub", id="sub"),
    pytest.param("subn", id="subn"),
    pytest.param("template", id="template"),
    pytest.param("escape", id="escape"),
)
PRIMARY_FLAG_EXPORTS = (
    "NOFLAG",
    "ASCII",
    "A",
    "IGNORECASE",
    "I",
    "LOCALE",
    "L",
    "MULTILINE",
    "M",
    "DOTALL",
    "S",
    "VERBOSE",
    "X",
    "UNICODE",
    "U",
    "DEBUG",
    "TEMPLATE",
    "T",
)
FLAG_ALIAS_PAIRS = (
    ("A", "ASCII"),
    ("I", "IGNORECASE"),
    ("L", "LOCALE"),
    ("M", "MULTILINE"),
    ("S", "DOTALL"),
    ("X", "VERBOSE"),
    ("U", "UNICODE"),
    ("T", "TEMPLATE"),
)
NON_INSTANTIABLE_EXPORTS = (
    pytest.param(
        "Pattern",
        "cannot create 're.Pattern' instances",
        id="Pattern",
    ),
    pytest.param(
        "Match",
        "cannot create 're.Match' instances",
        id="Match",
    ),
)
# Reuse the shared full-manifest loader even for owner rows without pattern
# payloads, then reapply this file's case-id-based contract on the returned bundles.
PUBLIC_SURFACE_BUNDLES = tuple(
    build_fixture_bundle(
        bundle.manifest,
        bundle.cases,
        expected_patterns=frozenset(case.case_id for case in bundle.cases),
        expected_case_ids=frozenset(case.case_id for case in bundle.cases),
        expected_text_models=PUBLIC_SURFACE_EXPECTED_TEXT_MODELS_BY_MANIFEST_ID.get(
            bundle.manifest.manifest_id
        ),
    )
    for bundle in load_published_fixture_bundles(
        (
            CORRECTNESS_FIXTURES_ROOT / "public_api_surface.py",
            CORRECTNESS_FIXTURES_ROOT / "exported_symbol_surface.py",
            CORRECTNESS_FIXTURES_ROOT / "pattern_object_surface.py",
        ),
        pattern_extractor=_public_surface_loader_token,
    )
)
PUBLIC_API_BUNDLE = published_fixture_bundle_by_manifest_id(
    PUBLIC_SURFACE_BUNDLES,
    "public-api-surface",
)
EXPORTED_SYMBOL_BUNDLE = published_fixture_bundle_by_manifest_id(
    PUBLIC_SURFACE_BUNDLES,
    "exported-symbol-surface",
)
PATTERN_OBJECT_BUNDLE = published_fixture_bundle_by_manifest_id(
    PUBLIC_SURFACE_BUNDLES,
    "pattern-object-surface",
)
PUBLIC_HELPER_CASES = fixture_cases_for_operation((PUBLIC_API_BUNDLE,), "module_has_attr")
PUBLIC_MODULE_CALL_CASES = fixture_cases_for_operation((PUBLIC_API_BUNDLE,), "module_call")
EXPORTED_METADATA_CASES = fixture_cases_for_operation(
    (EXPORTED_SYMBOL_BUNDLE,),
    "module_attr_metadata",
)
EXPORTED_VALUE_CASES = fixture_cases_for_operation(
    (EXPORTED_SYMBOL_BUNDLE,),
    "module_attr_value",
)
EXPORTED_CONSTRUCTOR_GUARD_CASES = fixture_cases_for_operation(
    (EXPORTED_SYMBOL_BUNDLE,),
    "module_call",
)
PATTERN_METADATA_CASES = fixture_cases_for_operation(
    (PATTERN_OBJECT_BUNDLE,),
    "pattern_metadata",
)
PATTERN_CALL_CASES = fixture_cases_for_operation((PATTERN_OBJECT_BUNDLE,), "pattern_call")


EXPLICIT_ESCAPE_STR_CASES = (
    ("", ""),
    ("abc_123", "abc_123"),
    (".^$*+?{}[]\\|()", "\\.\\^\\$\\*\\+\\?\\{\\}\\[\\]\\\\\\|\\(\\)"),
    (' !"#%&,/:;<=>@`~', '\\ !"\\#%\\&,/:;<=>@`\\~'),
    (" \t\n\r\x0b\x0c", "\\ \\\t\\\n\\\r\\\x0b\\\x0c"),
    ("a-b", "a\\-b"),
)
EXPLICIT_ESCAPE_BYTES_CASES = (
    (b"", b""),
    (b"abc_123", b"abc_123"),
    (br".^$*+?{}[]\|()", b"\\.\\^\\$\\*\\+\\?\\{\\}\\[\\]\\\\\\|\\(\\)"),
    (b' !"#%&,/:;<=>@`~', b'\\ !"\\#%\\&,/:;<=>@`\\~'),
    (b" \t\n\r\x0b\x0c", b"\\ \\\t\\\n\\\r\\\x0b\\\x0c"),
    (b"a-b", b"a\\-b"),
)
ESCAPE_DIFFERENTIAL_STR_CORPUS = tuple(chr(codepoint) for codepoint in range(128)) + (
    "cafe",
    "café",
    "Straße",
    "😀",
    "😀+?",
    "a\x00b",
    "line1\nline2",
    "tab\tspace ",
    "[a-z]{2,4}",
    r"\0foo",
    "é-😀[]",
)
ESCAPE_DIFFERENTIAL_BYTES_CORPUS = tuple(
    bytes([value]) for value in range(256)
) + (
    b"\x00foo",
    b"[a-z]{2,4}",
    b"foo\\bar",
    bytes(range(16)),
    bytes(range(240, 256)),
    b" \t\n\r\x0b\x0c",
    b"\xff-\x80[]",
)


@dataclass(frozen=True)
class VerboseCompileWorkflowCase:
    case_id: str
    helper: str
    text: str
    expected_group0: str | None
    expected_key: str | None
    expected_span: tuple[int, int] | None


@dataclass(frozen=True)
class CompiledPatternModuleHelperCase:
    case_id: str
    helper: str
    pattern: str | bytes
    args: tuple[object, ...]
    result_kind: str
    flags: int = 0


@dataclass(frozen=True)
class CompiledPatternModuleHelperErrorCase:
    case_id: str
    helper: str
    pattern: str | bytes
    args: tuple[object, ...]


@dataclass(frozen=True)
class CompiledPatternCompileCase:
    case_id: str
    pattern: str | bytes


@dataclass(frozen=True)
class ModuleKeywordCallCase:
    case_id: str
    helper: str
    args: tuple[object, ...]
    kwargs: dict[str, object]
    result_kind: str


@dataclass(frozen=True)
class PatternKeywordCallCase:
    case_id: str
    helper: str
    pattern: str | bytes
    args: tuple[object, ...]
    kwargs: dict[str, object]
    result_kind: str
    flags: int = 0


@dataclass(frozen=True)
class ModuleKeywordErrorCase:
    case_id: str
    helper: str
    args: tuple[object, ...]
    kwargs: dict[str, object]


@dataclass(frozen=True)
class CompiledPatternModuleKeywordCallCase:
    case_id: str
    helper: str
    pattern: str | bytes
    args: tuple[object, ...]
    kwargs: dict[str, object]
    flags: int = 0


@dataclass(frozen=True)
class CompiledPatternModuleKeywordErrorCase:
    case_id: str
    helper: str
    pattern: str | bytes
    args: tuple[object, ...]
    kwargs: dict[str, object]
    flags: int = 0


@dataclass(frozen=True)
class SupplementalMatchBehaviorCase:
    case_id: str
    helper: str
    pattern: bytes
    string: bytes
    matches: bool


class _EscapeStrSubclass(str):
    pass


class _EscapeBytesSubclass(bytes):
    pass


class _IndexLike:
    """Minimal __index__ carrier for keyword-argument parity coverage."""

    __slots__ = ("value",)

    def __init__(self, value: int) -> None:
        self.value = value

    def __index__(self) -> int:
        return self.value

    def __repr__(self) -> str:
        return f"IndexLike({self.value})"


_INDEX_ONE = _IndexLike(1)
_INDEX_TWO = _IndexLike(2)
_INDEX_FOUR = _IndexLike(4)
_INDEX_SEVEN = _IndexLike(7)


@dataclass(frozen=True)
class EscapeCompatibleInputCase:
    case_id: str
    input_factory: Callable[[], object]


@dataclass(frozen=True)
class EscapeInvalidInputCase:
    case_id: str
    input_factory: Callable[[], object]


@dataclass(frozen=True)
class CollectionModuleCase:
    case_id: str
    helper: str
    pattern: str | bytes
    string: str | bytes
    extra_args: tuple[object, ...] = ()


@dataclass(frozen=True)
class CollectionPatternCase:
    case_id: str
    helper: str
    pattern: str | bytes
    string: str | bytes
    extra_args: tuple[object, ...] = ()
    flags: int = 0


@dataclass(frozen=True)
class CollectionTypeErrorCase:
    case_id: str
    helper: str
    pattern: str | bytes
    string: str | bytes
    compiled: bool = False


@dataclass(frozen=True)
class BoundPatternTypeErrorCase:
    case_id: str
    helper: str
    pattern: str | bytes
    args: tuple[object, ...]


@dataclass(frozen=True)
class BoundedWildcardModuleCase:
    case_id: str
    helper: str
    pattern: str
    string: str
    flags: int = 0
    compiled: bool = False


def _module_collection_case_from_fixture(case: FixtureCase) -> CollectionModuleCase:
    assert case.operation == "module_call"
    assert case.helper is not None
    assert not case.kwargs
    assert len(case.args) >= 2

    pattern = case.args[0]
    string = case.args[1]
    extra_args = tuple(case.args[2:])

    assert isinstance(pattern, (str, bytes))
    assert isinstance(string, (str, bytes))
    return CollectionModuleCase(
        case_id=case.case_id,
        helper=case.helper,
        pattern=pattern,
        string=string,
        extra_args=extra_args,
    )


def _pattern_collection_case_from_fixture(case: FixtureCase) -> CollectionPatternCase:
    assert case.operation == "pattern_call"
    assert case.helper is not None
    assert not case.kwargs
    assert len(case.args) >= 1

    string = case.args[0]
    extra_args = tuple(case.args[1:])
    assert isinstance(string, (str, bytes))

    return CollectionPatternCase(
        case_id=case.case_id,
        helper=case.helper,
        pattern=case_pattern(case),
        string=string,
        extra_args=extra_args,
        flags=case.flags or 0,
    )


def _call_module_collection_helper(
    regex_api: object,
    case: CollectionModuleCase,
) -> object:
    return getattr(regex_api, case.helper)(case.pattern, case.string, *case.extra_args)


def _call_pattern_collection_helper(
    pattern: object,
    case: CollectionPatternCase,
) -> object:
    return getattr(pattern, case.helper)(case.string, *case.extra_args)


def _invoke_collection_helper(
    regex_api: object,
    case: CollectionTypeErrorCase,
) -> object:
    target = regex_api.compile(case.pattern) if case.compiled else regex_api
    args = (case.string,) if case.compiled else (case.pattern, case.string)
    result = getattr(target, case.helper)(*args)
    if case.helper == "finditer":
        return list(result)
    return result


def _invoke_bound_pattern_helper(
    pattern: object,
    case: BoundPatternTypeErrorCase,
) -> object:
    return getattr(pattern, case.helper)(*case.args)


_LITERAL_COLLECTION_MATRIX_ALPHABET = "ab"
_LITERAL_MATCH_HELPERS = ("search", "match", "fullmatch")
_LITERAL_COLLECTION_SPLIT_COUNTS = (0, 1, -1)


def _literal_collection_matrix_payloads(
    text_model: str,
) -> tuple[tuple[str | bytes, ...], tuple[str | bytes, ...]]:
    patterns = tuple(
        "".join(chars)
        for length in (1, 2)
        for chars in product(_LITERAL_COLLECTION_MATRIX_ALPHABET, repeat=length)
    )
    strings = tuple(
        "".join(chars)
        for length in range(4)
        for chars in product(_LITERAL_COLLECTION_MATRIX_ALPHABET, repeat=length)
    )
    if text_model == "bytes":
        return (
            tuple(pattern.encode("ascii") for pattern in patterns),
            tuple(string.encode("ascii") for string in strings),
        )
    return patterns, strings


def _literal_collection_window_cases(
    string_length: int,
) -> tuple[tuple[int, int | None], ...]:
    candidate_windows = [(0, None), (0, string_length)]
    if string_length:
        candidate_windows.extend(((1, None), (0, string_length - 1)))

    windows: list[tuple[int, int | None]] = []
    seen: set[tuple[int, int | None]] = set()
    for window in candidate_windows:
        if window in seen:
            continue
        seen.add(window)
        windows.append(window)
    return tuple(windows)


def _call_pattern_helper_with_window(
    pattern: object,
    helper: str,
    string: str | bytes,
    pos: int,
    endpos: int | None,
) -> object:
    method = getattr(pattern, helper)
    if endpos is None:
        return method(string, pos)
    return method(string, pos, endpos)


def _assert_literal_match_helper_result_matches_cpython(
    *,
    backend_name: str,
    context: str,
    helper: str,
    pattern: str | bytes,
    string: str | bytes,
    observed: object,
    expected: re.Match[str] | re.Match[bytes] | None,
    pos: int | None = None,
    endpos: int | None = None,
) -> None:
    try:
        assert_match_result_parity(
            backend_name,
            observed,
            expected,
            check_regs=True,
        )
        if expected is not None:
            assert_match_convenience_api_parity(observed, expected)
    except AssertionError as exc:
        window_suffix = ""
        if pos is not None or endpos is not None:
            window_suffix = f", pos={pos}, endpos={endpos}"
        raise AssertionError(
            f"{backend_name} {context} {helper} mismatch for "
            f"pattern={pattern!r}, string={string!r}{window_suffix}"
        ) from exc


def _evaluate_bounded_wildcard_module_case(
    regex_backend: tuple[str, object],
    case: BoundedWildcardModuleCase,
) -> tuple[str, object, object]:
    backend_name, backend = regex_backend
    if case.compiled:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            case.pattern,
            case.flags,
        )
        observed = getattr(backend, case.helper)(observed_pattern, case.string)
        expected = getattr(re, case.helper)(expected_pattern, case.string)
        return backend_name, observed, expected

    call_args: tuple[object, ...]
    if case.flags:
        call_args = (case.pattern, case.string, case.flags)
    else:
        call_args = (case.pattern, case.string)

    observed = getattr(backend, case.helper)(*call_args)
    expected = getattr(re, case.helper)(*call_args)
    return backend_name, observed, expected


class _BoundedWildcardFakeNativeBoundary(RecordingNativeBoundary):
    def compile_result(self, pattern: str | bytes, flags: int) -> tuple[str, int, bool]:
        return ("compiled", 34, False)

    def literal_match_result(
        self,
        pattern: str | bytes,
        flags: int,
        mode: str,
        string: str | bytes,
        pos: int,
        endpos: int | None,
    ) -> tuple[str, int, int, tuple[int, int] | None]:
        return ("matched", 0, len(string), (0, 3))

    def literal_findall_result(
        self,
        pattern: str | bytes,
        flags: int,
        string: str | bytes,
        pos: int,
        endpos: int | None,
    ) -> tuple[str, list[str] | list[bytes] | None]:
        return ("supported", ["abc"])


class _ModuleWorkflowFakeNativeBoundary(RecordingNativeBoundary):
    def __init__(
        self,
        *,
        str_compile_flags: int = 4098,
        bytes_compile_flags: int = 2050,
        native_placeholder_messages: bool = False,
    ) -> None:
        super().__init__(native_placeholder_messages=native_placeholder_messages)
        self._str_compile_flags = str_compile_flags
        self._bytes_compile_flags = bytes_compile_flags

    def compile_result(self, pattern: str | bytes, flags: int) -> tuple[str, int, bool]:
        if pattern == "boom":
            raise re.error("native compile failure", pattern, 2)
        normalized_flags = (
            self._bytes_compile_flags if isinstance(pattern, bytes) else self._str_compile_flags
        )
        return ("compiled", normalized_flags | flags, True)

    def literal_match_result(
        self,
        pattern: str | bytes,
        flags: int,
        mode: str,
        string: str | bytes,
        pos: int,
        endpos: int | None,
    ) -> tuple[str, int, int, tuple[int, int] | None]:
        if pattern == "unsupported":
            return ("unsupported", 0, len(string), None)
        return ("matched", 1, len(string) - 1, (1, 4))

    def literal_split_result(
        self,
        pattern: str | bytes,
        flags: int,
        string: str | bytes,
        maxsplit: int,
    ) -> tuple[str, list[str] | list[bytes] | None]:
        if isinstance(pattern, bytes):
            return ("supported", [b"native-bytes-split"])
        return ("supported", ["native-split"])

    def literal_findall_result(
        self,
        pattern: str | bytes,
        flags: int,
        string: str | bytes,
        pos: int,
        endpos: int | None,
    ) -> tuple[str, list[str] | list[bytes] | None]:
        if pattern == "unsupported" or flags == int(rebar.IGNORECASE):
            return ("unsupported", None)
        if isinstance(pattern, bytes):
            return ("supported", [b"native-bytes-findall"])
        return ("supported", ["native-findall"])

    def literal_finditer_result(
        self,
        pattern: str | bytes,
        flags: int,
        string: str | bytes,
        pos: int,
        endpos: int | None,
    ) -> tuple[str, int, int, list[tuple[int, int]]]:
        if pattern == "unsupported":
            return ("unsupported", 0, 0, [])
        return ("supported", 1, 6, [(2, 5)])

    def literal_subn_result(
        self,
        pattern: str | bytes,
        flags: int,
        repl: str | bytes,
        string: str | bytes,
        count: int,
    ) -> tuple[str, str | bytes | None, int]:
        if pattern == "unsupported":
            return ("unsupported", None, 0)
        if isinstance(pattern, bytes):
            return ("supported", b"native-bytes-subn", 7)
        return ("supported", "native-subn", 9)

    def escape_result(self, pattern: str | bytes) -> str | bytes:
        if isinstance(pattern, bytes):
            return b"native:" + pattern
        return f"native:{pattern}"


# Keep the published collection/replacement owner surface on its own fixture manifest.
_COLLECTION_FRONTIER_HELPERS = frozenset({"split", "findall", "finditer"})
_REPLACEMENT_FRONTIER_HELPERS = frozenset({"sub", "subn"})
(COLLECTION_REPLACEMENT_BUNDLE,) = load_published_fixture_bundles(
    (CORRECTNESS_FIXTURES_ROOT / "collection_replacement_workflows.py",)
)
PUBLISHED_COLLECTION_FIXTURE_CASES = _fixture_cases_for_helpers(
    COLLECTION_REPLACEMENT_BUNDLE,
    _COLLECTION_FRONTIER_HELPERS,
)
PUBLISHED_COLLECTION_MODULE_CASES = tuple(
    _module_collection_case_from_fixture(case)
    for case in PUBLISHED_COLLECTION_FIXTURE_CASES
    if case.operation == "module_call"
)
PUBLISHED_COLLECTION_PATTERN_CASES = tuple(
    _pattern_collection_case_from_fixture(case)
    for case in PUBLISHED_COLLECTION_FIXTURE_CASES
    if case.operation == "pattern_call"
)
MODULE_COLLECTION_CASES = (
    *(case for case in PUBLISHED_COLLECTION_MODULE_CASES if case.helper == "split"),
    CollectionModuleCase(
        "module-split-str-maxsplit-one",
        "split",
        "abc",
        "abcabc",
        (1,),
    ),
    CollectionModuleCase(
        "module-split-str-negative-maxsplit",
        "split",
        "abc",
        "abcabc",
        (-1,),
    ),
    CollectionModuleCase(
        "module-split-bytes-maxsplit-one",
        "split",
        b"abc",
        b"zzabczzabc",
        (1,),
    ),
    *(case for case in PUBLISHED_COLLECTION_MODULE_CASES if case.helper == "findall"),
    CollectionModuleCase("module-findall-str-repeated", "findall", "abc", "abcabc"),
    CollectionModuleCase("module-findall-str-no-match", "findall", "abc", "zzz"),
    *(case for case in PUBLISHED_COLLECTION_MODULE_CASES if case.helper == "finditer"),
    CollectionModuleCase("module-finditer-str-no-match", "finditer", "abc", "zzz"),
    CollectionModuleCase(
        "module-finditer-bytes-repeated",
        "finditer",
        b"abc",
        b"zabcabc",
    ),
)
PATTERN_COLLECTION_CASES = (
    *(case for case in PUBLISHED_COLLECTION_PATTERN_CASES if case.helper == "split"),
    CollectionPatternCase("pattern-split-str-no-match", "split", "abc", "zzz"),
    CollectionPatternCase("pattern-split-str-repeated", "split", "abc", "abcabc"),
    CollectionPatternCase(
        "pattern-split-str-maxsplit-one",
        "split",
        "abc",
        "abcabc",
        (1,),
    ),
    CollectionPatternCase(
        "pattern-split-str-negative-maxsplit",
        "split",
        "abc",
        "abcabc",
        (-1,),
    ),
    *(case for case in PUBLISHED_COLLECTION_PATTERN_CASES if case.helper == "findall"),
    CollectionPatternCase(
        "pattern-findall-str-bounded",
        "findall",
        "abc",
        "zabcabcz",
        (1, 7),
    ),
    CollectionPatternCase(
        "pattern-findall-str-bounded-no-match",
        "findall",
        "abc",
        "zabz",
        (1, 4),
    ),
    CollectionPatternCase(
        "pattern-findall-bytes-bounded",
        "findall",
        b"abc",
        b"zabcabcz",
        (1, 7),
    ),
    *(case for case in PUBLISHED_COLLECTION_PATTERN_CASES if case.helper == "finditer"),
    CollectionPatternCase(
        "pattern-finditer-str-bounded",
        "finditer",
        "abc",
        "zabcabcx",
        (1, 7),
    ),
    CollectionPatternCase(
        "pattern-finditer-str-bounded-no-match",
        "finditer",
        "abc",
        "zabz",
        (1, 4),
    ),
)


def _module_collection_cases_for_helper(
    helper: str,
) -> tuple[CollectionModuleCase, ...]:
    return tuple(case for case in MODULE_COLLECTION_CASES if case.helper == helper)


def _pattern_collection_cases_for_helper(
    helper: str,
) -> tuple[CollectionPatternCase, ...]:
    return tuple(case for case in PATTERN_COLLECTION_CASES if case.helper == helper)


BOUNDED_WILDCARD_MODULE_MATCH_CASES = (
    BoundedWildcardModuleCase(
        case_id="module-search-ignorecase-bounded-hit",
        helper="search",
        pattern="a.c",
        string="ABC",
        flags=int(re.IGNORECASE),
    ),
    BoundedWildcardModuleCase(
        case_id="module-match-bounded-miss",
        helper="match",
        pattern="a.c",
        string="zabc",
    ),
    BoundedWildcardModuleCase(
        case_id="module-fullmatch-bounded-hit",
        helper="fullmatch",
        pattern="a.c",
        string="abc",
    ),
    BoundedWildcardModuleCase(
        case_id="compiled-module-search-ignorecase-bounded-hit",
        helper="search",
        pattern="a.c",
        string="ABC",
        flags=int(re.IGNORECASE),
        compiled=True,
    ),
    BoundedWildcardModuleCase(
        case_id="compiled-module-match-bounded-hit",
        helper="match",
        pattern="a.c",
        string="abc",
        compiled=True,
    ),
    BoundedWildcardModuleCase(
        case_id="compiled-module-fullmatch-bounded-hit",
        helper="fullmatch",
        pattern="a.c",
        string="abc",
        compiled=True,
    ),
)
BOUNDED_WILDCARD_MODULE_COLLECTION_CASES = (
    BoundedWildcardModuleCase(
        case_id="module-findall-bounded-default",
        helper="findall",
        pattern="a.c",
        string="zabcaxcz",
    ),
    BoundedWildcardModuleCase(
        case_id="module-finditer-bounded-default",
        helper="finditer",
        pattern="a.c",
        string="zabcaxcx",
    ),
    BoundedWildcardModuleCase(
        case_id="compiled-module-findall-bounded-default",
        helper="findall",
        pattern="a.c",
        string="zabcaxcz",
        compiled=True,
    ),
    BoundedWildcardModuleCase(
        case_id="compiled-module-finditer-bounded-default",
        helper="finditer",
        pattern="a.c",
        string="zabcaxcx",
        compiled=True,
    ),
)
COLLECTION_TYPE_ERROR_CASES = (
    CollectionTypeErrorCase(
        case_id="module-split-str-pattern-on-bytes-string",
        helper="split",
        pattern="abc",
        string=b"abc",
    ),
    CollectionTypeErrorCase(
        case_id="module-findall-str-pattern-on-bytes-string",
        helper="findall",
        pattern="abc",
        string=b"abc",
    ),
    CollectionTypeErrorCase(
        case_id="pattern-findall-bytes-pattern-on-str-string",
        helper="findall",
        pattern=b"abc",
        string="abc",
        compiled=True,
    ),
    CollectionTypeErrorCase(
        case_id="pattern-finditer-bytes-pattern-on-str-string",
        helper="finditer",
        pattern=b"abc",
        string="abc",
        compiled=True,
    ),
)
BOUND_PATTERN_TYPE_ERROR_CASES = (
    BoundPatternTypeErrorCase(
        case_id="pattern-search-str-pattern-on-bytes-string",
        helper="search",
        pattern="abc",
        args=(b"abc",),
    ),
    BoundPatternTypeErrorCase(
        case_id="pattern-match-bytes-pattern-on-str-string",
        helper="match",
        pattern=b"abc",
        args=("abc",),
    ),
    BoundPatternTypeErrorCase(
        case_id="pattern-fullmatch-str-pattern-on-bytes-string",
        helper="fullmatch",
        pattern="abc",
        args=(b"abc",),
    ),
    BoundPatternTypeErrorCase(
        case_id="pattern-split-str-pattern-on-bytes-string",
        helper="split",
        pattern="abc",
        args=(b"zabczz",),
    ),
    BoundPatternTypeErrorCase(
        case_id="pattern-sub-str-pattern-on-bytes-string",
        helper="sub",
        pattern="abc",
        args=("x", b"zabczz"),
    ),
    BoundPatternTypeErrorCase(
        case_id="pattern-subn-bytes-pattern-on-str-string",
        helper="subn",
        pattern=b"abc",
        args=(b"x", "zabczz"),
    ),
)
COLLECTION_UNSUPPORTED_CASES = (
    pytest.param(
        lambda: rebar.findall("abc", "abc", rebar.IGNORECASE),
        "rebar.findall() is a scaffold placeholder",
        id="module-flags-findall",
    ),
    pytest.param(
        lambda: rebar.finditer("[ab]c", "abc"),
        "rebar.compile() is a scaffold placeholder",
        id="module-nonliteral-finditer",
    ),
    pytest.param(
        lambda: rebar.split("", "abc"),
        "rebar.split() is a scaffold placeholder",
        id="module-empty-split",
    ),
    pytest.param(
        lambda: rebar.compile("abc", rebar.IGNORECASE).finditer("abc"),
        "rebar.Pattern.finditer() is a scaffold placeholder",
        id="pattern-flags-finditer",
    ),
    pytest.param(
        lambda: rebar.compile("").findall("abc"),
        "rebar.Pattern.findall() is a scaffold placeholder",
        id="pattern-empty-findall",
    ),
)


VERBOSE_COMPILE_WORKFLOW_CASES = (
    VerboseCompileWorkflowCase(
        case_id="fullmatch-digits-without-literal-spaces",
        helper="fullmatch",
        text="ENV_VAR = 123",
        expected_group0="ENV_VAR = 123",
        expected_key="ENV_VAR",
        expected_span=(0, 13),
    ),
    VerboseCompileWorkflowCase(
        case_id="fullmatch-alpha-with-extra-whitespace",
        helper="fullmatch",
        text="ENV_VAR   =   ABCD",
        expected_group0="ENV_VAR   =   ABCD",
        expected_key="ENV_VAR",
        expected_span=(0, 18),
    ),
    VerboseCompileWorkflowCase(
        case_id="search-multiline-middle-line-digits",
        helper="search",
        text="prefix\nENV_VAR = 123\nsuffix",
        expected_group0="ENV_VAR = 123",
        expected_key="ENV_VAR",
        expected_span=(7, 20),
    ),
    VerboseCompileWorkflowCase(
        case_id="search-multiline-middle-line-alpha",
        helper="search",
        text="prefix\nENV_VAR=ABCD\nsuffix",
        expected_group0="ENV_VAR=ABCD",
        expected_key="ENV_VAR",
        expected_span=(7, 19),
    ),
    VerboseCompileWorkflowCase(
        case_id="fullmatch-rejects-lowercase-key",
        helper="fullmatch",
        text="env_var = 123",
        expected_group0=None,
        expected_key=None,
        expected_span=None,
    ),
    VerboseCompileWorkflowCase(
        case_id="search-rejects-too-many-digits",
        helper="search",
        text="prefix\nENV_VAR = 12345\nsuffix",
        expected_group0=None,
        expected_key=None,
        expected_span=None,
    ),
)
VERBOSE_BYTES_COMPILED_PATTERN_MODULE_HELPER_CASES = (
    CompiledPatternModuleHelperCase(
        case_id="compiled-pattern-search-bytes-verbose-regression",
        helper="search",
        pattern=case_pattern(VERBOSE_BYTES_SEARCH_PATTERN_CASE),
        args=tuple(VERBOSE_BYTES_SEARCH_PATTERN_CASE.args),
        result_kind="match",
        flags=VERBOSE_BYTES_SEARCH_PATTERN_CASE.flags or 0,
    ),
    CompiledPatternModuleHelperCase(
        case_id="compiled-pattern-fullmatch-bytes-verbose-regression",
        helper="fullmatch",
        pattern=case_pattern(VERBOSE_BYTES_FULLMATCH_PATTERN_CASE),
        args=tuple(VERBOSE_BYTES_FULLMATCH_PATTERN_CASE.args),
        result_kind="match",
        flags=VERBOSE_BYTES_FULLMATCH_PATTERN_CASE.flags or 0,
    ),
)
COMPILED_PATTERN_MODULE_HELPER_CASES = (
    CompiledPatternModuleHelperCase(
        case_id="compiled-pattern-search-str",
        helper="search",
        pattern="abc",
        args=("zabczz",),
        result_kind="match",
    ),
    CompiledPatternModuleHelperCase(
        case_id="compiled-pattern-match-str",
        helper="match",
        pattern="abc",
        args=("abcdef",),
        result_kind="match",
    ),
    CompiledPatternModuleHelperCase(
        case_id="compiled-pattern-fullmatch-bytes",
        helper="fullmatch",
        pattern=b"abc",
        args=(b"abc",),
        result_kind="match",
    ),
    *VERBOSE_BYTES_COMPILED_PATTERN_MODULE_HELPER_CASES,
    CompiledPatternModuleHelperCase(
        case_id="compiled-pattern-split-str-maxsplit",
        helper="split",
        pattern="abc",
        args=("zzabczzabc", 1),
        result_kind="value",
    ),
    CompiledPatternModuleHelperCase(
        case_id="compiled-pattern-findall-bytes",
        helper="findall",
        pattern=b"abc",
        args=(b"zabcabc",),
        result_kind="value",
    ),
    CompiledPatternModuleHelperCase(
        case_id="compiled-pattern-finditer-str",
        helper="finditer",
        pattern="abc",
        args=("zabcabc",),
        result_kind="iter",
    ),
    CompiledPatternModuleHelperCase(
        case_id="compiled-pattern-sub-str-count",
        helper="sub",
        pattern="abc",
        args=("x", "zabcabc", 1),
        result_kind="value",
    ),
    CompiledPatternModuleHelperCase(
        case_id="compiled-pattern-subn-bytes-count",
        helper="subn",
        pattern=b"abc",
        args=(b"x", b"zabcabc", 1),
        result_kind="value",
    ),
)
COMPILED_PATTERN_MODULE_HELPER_ERROR_CASES = (
    CompiledPatternModuleHelperErrorCase(
        case_id="compiled-pattern-search-str-on-bytes-string",
        helper="search",
        pattern="abc",
        args=(b"abc",),
    ),
    CompiledPatternModuleHelperErrorCase(
        case_id="compiled-pattern-match-bytes-on-str-string",
        helper="match",
        pattern=b"abc",
        args=("abc",),
    ),
    CompiledPatternModuleHelperErrorCase(
        case_id="compiled-pattern-fullmatch-str-on-bytes-string",
        helper="fullmatch",
        pattern="abc",
        args=(b"abc",),
    ),
    CompiledPatternModuleHelperErrorCase(
        case_id="compiled-pattern-split-str-on-bytes-string",
        helper="split",
        pattern="abc",
        args=(b"zabczz", 1),
    ),
    CompiledPatternModuleHelperErrorCase(
        case_id="compiled-pattern-findall-bytes-on-str-string",
        helper="findall",
        pattern=b"abc",
        args=("zabczz",),
    ),
    CompiledPatternModuleHelperErrorCase(
        case_id="compiled-pattern-finditer-str-on-bytes-string",
        helper="finditer",
        pattern="abc",
        args=(b"zabczz",),
    ),
    CompiledPatternModuleHelperErrorCase(
        case_id="compiled-pattern-sub-str-on-bytes-string",
        helper="sub",
        pattern="abc",
        args=("x", b"zabczz", 1),
    ),
    CompiledPatternModuleHelperErrorCase(
        case_id="compiled-pattern-subn-bytes-on-str-string",
        helper="subn",
        pattern=b"abc",
        args=(b"x", "zabczz", 1),
    ),
)
COMPILED_PATTERN_COMPILE_CASES = (
    CompiledPatternCompileCase(
        case_id="compiled-pattern-compile-str-literal",
        pattern="abc",
    ),
    CompiledPatternCompileCase(
        case_id="compiled-pattern-compile-bytes-literal",
        pattern=b"abc",
    ),
    CompiledPatternCompileCase(
        case_id="compiled-pattern-compile-str-named-group",
        pattern=r"(?P<word>abc)",
    ),
)
MODULE_KEYWORD_CALL_CASES = (
    ModuleKeywordCallCase(
        case_id="module-search-flags-keyword-str",
        helper="search",
        args=("abc", "zAbc"),
        kwargs={"flags": int(re.IGNORECASE)},
        result_kind="match",
    ),
    ModuleKeywordCallCase(
        case_id="module-match-flags-keyword-bytes",
        helper="match",
        args=(b"abc", b"Abc"),
        kwargs={"flags": int(re.IGNORECASE)},
        result_kind="match",
    ),
    ModuleKeywordCallCase(
        case_id="module-fullmatch-flags-keyword-str",
        helper="fullmatch",
        args=("abc", "Abc"),
        kwargs={"flags": int(re.IGNORECASE)},
        result_kind="match",
    ),
    ModuleKeywordCallCase(
        case_id="module-split-maxsplit-keyword-bytes",
        helper="split",
        args=(b"abc", b"zabczabc"),
        kwargs={"maxsplit": 1},
        result_kind="value",
    ),
    ModuleKeywordCallCase(
        case_id="module-split-maxsplit-indexlike-bytes",
        helper="split",
        args=(b"abc", b"zabcabcabc"),
        kwargs={"maxsplit": _INDEX_TWO},
        result_kind="value",
    ),
    ModuleKeywordCallCase(
        case_id="module-split-maxsplit-bool-false-bytes",
        helper="split",
        args=(b"abc", b"abcabc"),
        kwargs={"maxsplit": False},
        result_kind="value",
    ),
    ModuleKeywordCallCase(
        case_id="module-sub-count-keyword-str",
        helper="sub",
        args=("abc", "x", "abcabc"),
        kwargs={"count": 1},
        result_kind="value",
    ),
    ModuleKeywordCallCase(
        case_id="module-sub-count-indexlike-str",
        helper="sub",
        args=("abc", "x", "abcabcabc"),
        kwargs={"count": _INDEX_TWO},
        result_kind="value",
    ),
    ModuleKeywordCallCase(
        case_id="module-sub-count-bool-true-str",
        helper="sub",
        args=("abc", "x", "abcabc"),
        kwargs={"count": True},
        result_kind="value",
    ),
    ModuleKeywordCallCase(
        case_id="module-subn-count-keyword-bytes",
        helper="subn",
        args=(b"abc", b"x", b"abcabc"),
        kwargs={"count": 1},
        result_kind="value",
    ),
    ModuleKeywordCallCase(
        case_id="module-subn-count-indexlike-bytes",
        helper="subn",
        args=(b"abc", b"x", b"abcabcabc"),
        kwargs={"count": _INDEX_TWO},
        result_kind="value",
    ),
    ModuleKeywordCallCase(
        case_id="module-subn-count-bool-false-bytes",
        helper="subn",
        args=(b"abc", b"x", b"abcabc"),
        kwargs={"count": False},
        result_kind="value",
    ),
)
PATTERN_KEYWORD_CALL_CASES = (
    PatternKeywordCallCase(
        case_id="pattern-search-pos-keyword-str",
        helper="search",
        pattern="abc",
        args=("zabcabc",),
        kwargs={"pos": 2},
        result_kind="match",
    ),
    PatternKeywordCallCase(
        case_id="pattern-search-bool-endpos-keyword-str",
        helper="search",
        pattern="z",
        args=("zabcabc",),
        kwargs={"endpos": True},
        result_kind="match",
    ),
    PatternKeywordCallCase(
        case_id="pattern-search-endpos-keyword-bytes",
        helper="search",
        pattern=b"abc",
        args=(b"zabcabc",),
        kwargs={"endpos": 4},
        result_kind="match",
    ),
    PatternKeywordCallCase(
        case_id="pattern-search-pos-indexlike-str",
        helper="search",
        pattern="abc",
        args=("zabcabc",),
        kwargs={"pos": _INDEX_TWO},
        result_kind="match",
    ),
    PatternKeywordCallCase(
        case_id="pattern-search-endpos-indexlike-bytes",
        helper="search",
        pattern=b"abc",
        args=(b"zabcabc",),
        kwargs={"endpos": _INDEX_FOUR},
        result_kind="match",
    ),
    PatternKeywordCallCase(
        case_id="pattern-match-pos-keyword-str",
        helper="match",
        pattern="abc",
        args=("zabcabc",),
        kwargs={"pos": 1},
        result_kind="match",
    ),
    PatternKeywordCallCase(
        case_id="pattern-match-bool-pos-keyword-str",
        helper="match",
        pattern="abc",
        args=("zabcabc",),
        kwargs={"pos": True},
        result_kind="match",
    ),
    PatternKeywordCallCase(
        case_id="pattern-fullmatch-window-keyword-bytes",
        helper="fullmatch",
        pattern=b"abc",
        args=(b"zabc",),
        kwargs={"pos": 1, "endpos": 4},
        result_kind="match",
    ),
    PatternKeywordCallCase(
        case_id="pattern-fullmatch-window-indexlike-bytes",
        helper="fullmatch",
        pattern=b"abc",
        args=(b"zabc",),
        kwargs={"pos": _INDEX_ONE, "endpos": _INDEX_FOUR},
        result_kind="match",
    ),
    PatternKeywordCallCase(
        case_id="pattern-findall-window-keyword-str",
        helper="findall",
        pattern="abc",
        args=("zabcabcz",),
        kwargs={"pos": 1, "endpos": 7},
        result_kind="value",
    ),
    PatternKeywordCallCase(
        case_id="pattern-findall-window-indexlike-str",
        helper="findall",
        pattern="abc",
        args=("zabcabcabcz",),
        kwargs={"pos": _INDEX_ONE, "endpos": _INDEX_SEVEN},
        result_kind="value",
    ),
    PatternKeywordCallCase(
        case_id="pattern-findall-bool-window-keyword-str",
        helper="findall",
        pattern="abc",
        args=("zabcabcz",),
        kwargs={"pos": True, "endpos": 7},
        result_kind="value",
    ),
    PatternKeywordCallCase(
        case_id="pattern-finditer-window-keyword-bytes",
        helper="finditer",
        pattern=b"abc",
        args=(b"zabcabcz",),
        kwargs={"pos": 1, "endpos": 7},
        result_kind="iter",
    ),
    PatternKeywordCallCase(
        case_id="pattern-finditer-window-indexlike-bytes",
        helper="finditer",
        pattern=b"abc",
        args=(b"zabcabcabcz",),
        kwargs={"pos": _INDEX_ONE, "endpos": _INDEX_SEVEN},
        result_kind="iter",
    ),
    PatternKeywordCallCase(
        case_id="pattern-finditer-bool-window-keyword-bytes",
        helper="finditer",
        pattern=b"abc",
        args=(b"zabcabcz",),
        kwargs={"pos": True, "endpos": 7},
        result_kind="iter",
    ),
    PatternKeywordCallCase(
        case_id="pattern-split-maxsplit-keyword-str",
        helper="split",
        pattern="abc",
        args=("zabczabc",),
        kwargs={"maxsplit": 1},
        result_kind="value",
    ),
    PatternKeywordCallCase(
        case_id="pattern-split-maxsplit-indexlike-str",
        helper="split",
        pattern="abc",
        args=("zabcabcabc",),
        kwargs={"maxsplit": _INDEX_TWO},
        result_kind="value",
    ),
    PatternKeywordCallCase(
        case_id="pattern-split-maxsplit-bool-true-str",
        helper="split",
        pattern="abc",
        args=("zabczabc",),
        kwargs={"maxsplit": True},
        result_kind="value",
    ),
    PatternKeywordCallCase(
        case_id="pattern-sub-count-keyword-bytes",
        helper="sub",
        pattern=b"abc",
        args=(b"x", b"abcabc"),
        kwargs={"count": 1},
        result_kind="value",
    ),
    PatternKeywordCallCase(
        case_id="pattern-sub-count-indexlike-bytes",
        helper="sub",
        pattern=b"abc",
        args=(b"x", b"abcabcabc"),
        kwargs={"count": _INDEX_TWO},
        result_kind="value",
    ),
    PatternKeywordCallCase(
        case_id="pattern-sub-count-bool-false-bytes",
        helper="sub",
        pattern=b"abc",
        args=(b"x", b"abcabc"),
        kwargs={"count": False},
        result_kind="value",
    ),
    PatternKeywordCallCase(
        case_id="pattern-subn-count-keyword-str",
        helper="subn",
        pattern="abc",
        args=("x", "abcabc"),
        kwargs={"count": 1},
        result_kind="value",
    ),
    PatternKeywordCallCase(
        case_id="pattern-subn-count-indexlike-str",
        helper="subn",
        pattern="abc",
        args=("x", "abcabcabc"),
        kwargs={"count": _INDEX_TWO},
        result_kind="value",
    ),
    PatternKeywordCallCase(
        case_id="pattern-subn-count-bool-true-str",
        helper="subn",
        pattern="abc",
        args=("x", "abcabc"),
        kwargs={"count": True},
        result_kind="value",
    ),
)
MODULE_KEYWORD_ERROR_CASES = (
    ModuleKeywordErrorCase(
        case_id="module-search-duplicate-flags-keyword",
        helper="search",
        args=("abc", "abc", 0),
        kwargs={"flags": 0},
    ),
    ModuleKeywordErrorCase(
        case_id="module-split-duplicate-maxsplit-keyword",
        helper="split",
        args=("abc", "abc", 1),
        kwargs={"maxsplit": 1},
    ),
    ModuleKeywordErrorCase(
        case_id="module-sub-duplicate-count-keyword",
        helper="sub",
        args=("abc", "x", "abc", 1),
        kwargs={"count": 1},
    ),
    ModuleKeywordErrorCase(
        case_id="module-fullmatch-unexpected-keyword",
        helper="fullmatch",
        args=("abc", "abc"),
        kwargs={"missing": 1},
    ),
    ModuleKeywordErrorCase(
        case_id="module-sub-unexpected-keyword",
        helper="sub",
        args=("abc", "x", "abc"),
        kwargs={"missing": 1},
    ),
)
COMPILED_PATTERN_MODULE_KEYWORD_CALL_CASES = (
    CompiledPatternModuleKeywordCallCase(
        case_id="compiled-pattern-compile-flags-int-zero-str",
        helper="compile",
        pattern="abc",
        args=(),
        kwargs={"flags": 0},
    ),
    CompiledPatternModuleKeywordCallCase(
        case_id="compiled-pattern-compile-flags-bool-false-str",
        helper="compile",
        pattern="abc",
        args=(),
        kwargs={"flags": False},
    ),
    CompiledPatternModuleKeywordCallCase(
        case_id="compiled-pattern-compile-flags-int-zero-str-named-group",
        helper="compile",
        pattern=r"(?P<word>abc)",
        args=(),
        kwargs={"flags": 0},
    ),
    CompiledPatternModuleKeywordCallCase(
        case_id="compiled-pattern-compile-flags-bool-false-str-named-group",
        helper="compile",
        pattern=r"(?P<word>abc)",
        args=(),
        kwargs={"flags": False},
    ),
    CompiledPatternModuleKeywordCallCase(
        case_id="compiled-pattern-compile-flags-int-zero-bytes",
        helper="compile",
        pattern=b"abc",
        args=(),
        kwargs={"flags": 0},
    ),
    CompiledPatternModuleKeywordCallCase(
        case_id="compiled-pattern-compile-flags-bool-false-bytes",
        helper="compile",
        pattern=b"abc",
        args=(),
        kwargs={"flags": False},
    ),
    CompiledPatternModuleKeywordCallCase(
        case_id="compiled-pattern-split-maxsplit-keyword-str",
        helper="split",
        pattern="abc",
        args=("zabczabc",),
        kwargs={"maxsplit": 1},
    ),
    CompiledPatternModuleKeywordCallCase(
        case_id="compiled-pattern-split-maxsplit-indexlike-bytes",
        helper="split",
        pattern=b"abc",
        args=(b"zabcabcabc",),
        kwargs={"maxsplit": _INDEX_TWO},
    ),
    CompiledPatternModuleKeywordCallCase(
        case_id="compiled-pattern-split-maxsplit-bool-false-bytes",
        helper="split",
        pattern=b"abc",
        args=(b"abcabc",),
        kwargs={"maxsplit": False},
    ),
    CompiledPatternModuleKeywordCallCase(
        case_id="compiled-pattern-sub-count-keyword-str",
        helper="sub",
        pattern="abc",
        args=("x", "abcabc"),
        kwargs={"count": 1},
    ),
    CompiledPatternModuleKeywordCallCase(
        case_id="compiled-pattern-sub-count-indexlike-bytes",
        helper="sub",
        pattern=b"abc",
        args=(b"x", b"abcabcabc"),
        kwargs={"count": _INDEX_TWO},
    ),
    CompiledPatternModuleKeywordCallCase(
        case_id="compiled-pattern-sub-count-bool-true-str",
        helper="sub",
        pattern="abc",
        args=("x", "abcabc"),
        kwargs={"count": True},
    ),
    CompiledPatternModuleKeywordCallCase(
        case_id="compiled-pattern-subn-count-keyword-bytes",
        helper="subn",
        pattern=b"abc",
        args=(b"x", b"abcabc"),
        kwargs={"count": 1},
    ),
    CompiledPatternModuleKeywordCallCase(
        case_id="compiled-pattern-subn-count-indexlike-str",
        helper="subn",
        pattern="abc",
        args=("x", "abcabcabc"),
        kwargs={"count": _INDEX_TWO},
    ),
    CompiledPatternModuleKeywordCallCase(
        case_id="compiled-pattern-subn-count-bool-false-bytes",
        helper="subn",
        pattern=b"abc",
        args=(b"x", b"abcabc"),
        kwargs={"count": False},
    ),
)
COMPILED_PATTERN_MODULE_KEYWORD_ERROR_CASES = (
    CompiledPatternModuleKeywordErrorCase(
        case_id="compiled-pattern-split-duplicate-maxsplit-keyword-str",
        helper="split",
        pattern="abc",
        args=("abc", 1),
        kwargs={"maxsplit": 1},
    ),
    CompiledPatternModuleKeywordErrorCase(
        case_id="compiled-pattern-sub-duplicate-count-keyword-str",
        helper="sub",
        pattern="abc",
        args=("x", "abc", 1),
        kwargs={"count": 1},
    ),
    CompiledPatternModuleKeywordErrorCase(
        case_id="compiled-pattern-subn-duplicate-count-keyword-bytes",
        helper="subn",
        pattern=b"abc",
        args=(b"x", b"abc", 1),
        kwargs={"count": 1},
    ),
    CompiledPatternModuleKeywordErrorCase(
        case_id="compiled-pattern-split-unexpected-keyword-bytes",
        helper="split",
        pattern=b"abc",
        args=(b"abc",),
        kwargs={"missing": 1},
    ),
    CompiledPatternModuleKeywordErrorCase(
        case_id="compiled-pattern-sub-unexpected-keyword-str",
        helper="sub",
        pattern="abc",
        args=("x", "abc"),
        kwargs={"missing": 1},
    ),
    CompiledPatternModuleKeywordErrorCase(
        case_id="compiled-pattern-subn-unexpected-keyword-bytes",
        helper="subn",
        pattern=b"abc",
        args=(b"x", b"abc"),
        kwargs={"missing": 1},
    ),
)
# Exercise CPython-supported input shapes that are easy to miss when escape()
# only appears to support plain str and bytes inputs.
ESCAPE_COMPATIBLE_INPUT_CASES = (
    EscapeCompatibleInputCase(
        case_id="str-subclass",
        input_factory=lambda: _EscapeStrSubclass("a-b.c"),
    ),
    EscapeCompatibleInputCase(
        case_id="bytes-subclass",
        input_factory=lambda: _EscapeBytesSubclass(b"a-b.c"),
    ),
    EscapeCompatibleInputCase(
        case_id="bytearray",
        input_factory=lambda: bytearray(b"a-b.c"),
    ),
    EscapeCompatibleInputCase(
        case_id="memoryview",
        input_factory=lambda: memoryview(b"a-b.c"),
    ),
    EscapeCompatibleInputCase(
        case_id="memoryview-bytearray",
        input_factory=lambda: memoryview(bytearray(b"a-b.c")),
    ),
    EscapeCompatibleInputCase(
        case_id="memoryview-contiguous-slice",
        input_factory=lambda: memoryview(b"0a-b.c1")[1:-1],
    ),
    EscapeCompatibleInputCase(
        case_id="array-B",
        input_factory=lambda: array("B", b"a-b.c"),
    ),
    EscapeCompatibleInputCase(
        case_id="array-b",
        input_factory=lambda: array("b", b"a-b.c"),
    ),
)
ESCAPE_INVALID_INPUT_CASES = (
    EscapeInvalidInputCase(
        case_id="int",
        input_factory=lambda: 123,
    ),
    EscapeInvalidInputCase(
        case_id="none",
        input_factory=lambda: None,
    ),
    EscapeInvalidInputCase(
        case_id="object",
        input_factory=object,
    ),
    EscapeInvalidInputCase(
        case_id="list",
        input_factory=lambda: ["a-b.c"],
    ),
    EscapeInvalidInputCase(
        case_id="dict",
        input_factory=lambda: {"pattern": "a-b.c"},
    ),
    EscapeInvalidInputCase(
        case_id="memoryview-noncontiguous-slice",
        input_factory=lambda: memoryview(b"0a-b.c1")[1:-1:2],
    ),
)
SUPPLEMENTAL_BYTES_CASES = (
    SupplementalMatchBehaviorCase(
        case_id="search-bytes-success-literal",
        helper="search",
        pattern=b"abc",
        string=b"zzabczz",
        matches=True,
    ),
    SupplementalMatchBehaviorCase(
        case_id="search-bytes-no-match",
        helper="search",
        pattern=b"abc",
        string=b"zzz",
        matches=False,
    ),
    SupplementalMatchBehaviorCase(
        case_id="match-bytes-success-literal",
        helper="match",
        pattern=b"ab",
        string=b"abbb",
        matches=True,
    ),
    SupplementalMatchBehaviorCase(
        case_id="match-bytes-no-match",
        helper="match",
        pattern=b"abc",
        string=b"zabc",
        matches=False,
    ),
    SupplementalMatchBehaviorCase(
        case_id="fullmatch-bytes-no-match",
        helper="fullmatch",
        pattern=b"123",
        string=b"1234",
        matches=False,
    ),
)
MATCH_REFERENCE_IDENTITY_CASES = (
    pytest.param(
        "search",
        ("ab", "c"),
        ("z", "ab", "c", "zz"),
        id="search-str",
    ),
    pytest.param(
        "match",
        ("ab",),
        ("ab", "zz"),
        id="match-str",
    ),
    pytest.param(
        "fullmatch",
        (b"12", b"3"),
        (b"12", b"3"),
        id="fullmatch-bytes",
    ),
)

# CPython accepts multiple zero-valued flag spellings for compiled-pattern entry
# points; keep those variants covered in one place so helper wrappers do not
# drift into special-casing only one form.
COMPILED_PATTERN_ZERO_FLAG_MODES = (
    pytest.param("default", id="default"),
    pytest.param("noflag", id="explicit-noflag"),
    pytest.param("int-zero", id="explicit-int-zero"),
    pytest.param("bool-false", id="explicit-bool-false"),
)


def _join_runtime_text(parts: tuple[str, ...] | tuple[bytes, ...]) -> str | bytes:
    first_part = parts[0]
    if isinstance(first_part, bytes):
        return b"".join(parts)
    return "".join(parts)


def _compile_verbose_regression_pattern(
    backend_name: str,
    backend: object,
) -> tuple[object, re.Pattern[str]]:
    pattern = case_pattern(VERBOSE_COMPILE_CASE)
    assert isinstance(pattern, str)

    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        pattern,
        VERBOSE_COMPILE_CASE.flags or 0,
    )

    assert expected_pattern.flags == int(re.MULTILINE | re.VERBOSE | re.UNICODE)
    assert expected_pattern.groupindex == {"key": 1}
    return observed_pattern, expected_pattern


def _compile_verbose_regression_bytes_pattern(
    backend_name: str,
    backend: object,
) -> tuple[object, re.Pattern[bytes]]:
    pattern = case_pattern(VERBOSE_BYTES_COMPILE_CASE)
    assert isinstance(pattern, bytes)

    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        pattern,
        VERBOSE_BYTES_COMPILE_CASE.flags or 0,
    )

    assert expected_pattern.flags == int(re.MULTILINE | re.VERBOSE)
    assert expected_pattern.groupindex == {"key": 1}
    return observed_pattern, expected_pattern


def _compile_compiled_pattern_case(
    regex_api: object,
    pattern: str | bytes,
    flags: int = 0,
) -> object:
    compiled = regex_api.compile(pattern, flags)
    assert regex_api.compile(compiled) is compiled
    return compiled


def _compile_with_flag_mode(
    regex_api: object,
    pattern: object,
    flag_mode: str,
) -> object:
    if flag_mode == "default":
        return regex_api.compile(pattern)
    if flag_mode == "noflag":
        return regex_api.compile(pattern, regex_api.NOFLAG)
    if flag_mode == "int-zero":
        return regex_api.compile(pattern, int(regex_api.NOFLAG))
    if flag_mode == "bool-false":
        return regex_api.compile(pattern, False)
    raise AssertionError(f"unsupported compile flag mode {flag_mode!r}")


def _call_module_helper_with_flag_mode(
    regex_api: object,
    compiled_pattern: object,
    case: CompiledPatternModuleHelperCase,
    flag_mode: str,
) -> object:
    helper = getattr(regex_api, case.helper)
    if flag_mode == "default":
        return helper(compiled_pattern, *case.args)
    if flag_mode == "noflag":
        return helper(compiled_pattern, *case.args, flags=regex_api.NOFLAG)
    if flag_mode == "int-zero":
        return helper(compiled_pattern, *case.args, flags=int(regex_api.NOFLAG))
    if flag_mode == "bool-false":
        return helper(compiled_pattern, *case.args, flags=False)
    raise AssertionError(f"unsupported module helper flag mode {flag_mode!r}")


def _call_module_keyword_case(regex_api: object, case: ModuleKeywordCallCase) -> object:
    return getattr(regex_api, case.helper)(*case.args, **case.kwargs)


def _call_compiled_pattern_module_keyword_case(
    regex_api: object,
    case: CompiledPatternModuleKeywordCallCase | CompiledPatternModuleKeywordErrorCase,
) -> object:
    compiled_pattern = _compile_compiled_pattern_case(regex_api, case.pattern, case.flags)
    return getattr(regex_api, case.helper)(compiled_pattern, *case.args, **case.kwargs)


def _call_pattern_keyword_case(pattern: object, case: PatternKeywordCallCase) -> object:
    return getattr(pattern, case.helper)(*case.args, **case.kwargs)


def _capture_error(callback) -> BaseException:
    try:
        callback()
    except BaseException as error:  # noqa: BLE001 - parity helper compares exception details.
        return error
    raise AssertionError("expected call to raise")


def _assert_literal_match_contract(
    match: rebar.Match,
    expected_group0: str | bytes,
    expected_span: tuple[int, int],
    expected_endpos: int,
) -> None:
    assert type(match) is rebar.Match
    assert bool(match)
    assert match.group() == expected_group0
    assert match.group(0) == expected_group0
    assert match.group(0, 0) == (expected_group0, expected_group0)
    assert match.groups() == ()
    assert match.groupdict() == {}
    assert match.span() == expected_span
    assert match.start() == expected_span[0]
    assert match.end() == expected_span[1]
    assert match.pos == 0
    assert match.endpos == expected_endpos
    assert match.lastindex is None
    assert match.lastgroup is None


def _match_behavior_case_string(case: FixtureCase) -> str | bytes:
    string = case.args[1]
    assert isinstance(string, (str, bytes))
    return string


def _assert_match_input_identity(
    observed: object,
    expected: re.Match[str] | re.Match[bytes],
    *,
    pattern: str | bytes,
    string: str | bytes,
) -> None:
    assert observed.string is string
    assert expected.string is string
    assert observed.re.pattern is pattern
    assert expected.re.pattern is pattern


def _assert_compiled_match_identity(
    observed: object,
    expected: re.Match[str] | re.Match[bytes],
    *,
    pattern: str | bytes,
    string: str | bytes,
    observed_pattern: object,
    expected_pattern: re.Pattern[str] | re.Pattern[bytes],
) -> None:
    _assert_match_input_identity(
        observed,
        expected,
        pattern=pattern,
        string=string,
    )
    assert observed.re is observed_pattern
    assert expected.re is expected_pattern
    assert getattr(observed_pattern, "pattern") is pattern
    assert expected_pattern.pattern is pattern


def _assert_verbose_compile_case_matches_cpython(
    backend_name: str,
    observed_pattern: object,
    expected_pattern: re.Pattern[str],
    case: VerboseCompileWorkflowCase,
) -> None:
    observed = getattr(observed_pattern, case.helper)(case.text)
    expected = getattr(expected_pattern, case.helper)(case.text)

    assert_match_result_parity(backend_name, observed, expected, check_regs=True)

    if case.expected_group0 is None:
        assert observed is None
        assert expected is None
        return

    assert observed is not None
    assert expected is not None
    assert observed.group(0) == expected.group(0) == case.expected_group0
    assert observed.group("key") == expected.group("key") == case.expected_key
    assert observed.groupdict() == expected.groupdict() == {"key": case.expected_key}
    assert observed.span() == expected.span() == case.expected_span
    assert_match_convenience_api_parity(observed, expected)


def _assert_verbose_compile_bytes_case_matches_cpython(
    backend_name: str,
    observed_pattern: object,
    expected_pattern: re.Pattern[bytes],
    case: VerboseCompileWorkflowCase,
) -> None:
    bytes_text = case.text.encode("ascii")
    observed = getattr(observed_pattern, case.helper)(bytes_text)
    expected = getattr(expected_pattern, case.helper)(bytes_text)

    assert_match_result_parity(backend_name, observed, expected, check_regs=True)

    if case.expected_group0 is None:
        assert observed is None
        assert expected is None
        return

    expected_group0 = case.expected_group0.encode("ascii")
    expected_key = case.expected_key.encode("ascii")

    assert observed is not None
    assert expected is not None
    assert observed.group(0) == expected.group(0) == expected_group0
    assert observed.group("key") == expected.group("key") == expected_key
    assert observed.groupdict() == expected.groupdict() == {"key": expected_key}
    assert observed.span() == expected.span() == case.expected_span
    assert_match_convenience_api_parity(observed, expected)


@dataclass(frozen=True)
class BackendFixtureContractCase:
    unsupported_backends: tuple[str, ...] = ()
    unsupported_backend_reason: str | None = None


def _request_with_backend_params(**params: object) -> object:
    return SimpleNamespace(node=SimpleNamespace(callspec=SimpleNamespace(params=params)))


def _backend_fixture_request(backend_name: str, **params: object) -> object:
    return SimpleNamespace(
        param=backend_name,
        node=SimpleNamespace(callspec=SimpleNamespace(params=params)),
    )


def test_module_workflow_parity_suite_stays_aligned_with_published_fixture() -> None:
    assert_fixture_bundle_contract(
        MODULE_WORKFLOW_BUNDLE,
        pattern_extractor=case_pattern,
        expected_fixture_path=MODULE_WORKFLOW_FIXTURE_PATH,
        expected_ordered_case_ids=_published_case_ids(MODULE_WORKFLOW_BUNDLE),
    )


def test_module_workflow_parity_suite_tracks_published_case_frontier() -> None:
    assert_fixture_bundle_tracks_published_case_frontier(
        MODULE_WORKFLOW_BUNDLE,
        selected_case_ids=_published_case_ids(MODULE_WORKFLOW_BUNDLE),
    )


def test_module_workflow_direct_test_buckets_cover_selected_frontier() -> None:
    assert_direct_test_case_id_buckets_cover_selected_frontier(
        {
            "compile": frozenset(case.case_id for case in COMPILE_CASES),
            "pattern": frozenset(case.case_id for case in PATTERN_CASES),
            "cache": frozenset(case.case_id for case in CACHE_CASES),
            "purge": frozenset(case.case_id for case in PURGE_CASES),
            "bounded-wildcard-module-helper": frozenset(
                case.case_id for case in PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASES
            ),
            "module-keyword-helper": frozenset(
                case.case_id for case in PUBLISHED_MODULE_KEYWORD_MODULE_HELPER_CASES
            ),
            "module-keyword-error": frozenset(
                case.case_id
                for case in PUBLISHED_MODULE_KEYWORD_ERROR_MODULE_HELPER_CASES
            ),
            "compiled-module-helper": frozenset(
                case.case_id for case in PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES
            ),
            "escape": frozenset(case.case_id for case in ESCAPE_CASES),
        },
        selected_case_ids=_published_case_ids(MODULE_WORKFLOW_BUNDLE),
        coverage_label="module workflow direct-test case-id buckets",
    )


def test_module_workflow_surface_bundle_contract_covers_regression_compile_cases() -> None:
    assert MODULE_WORKFLOW_BUNDLE.manifest.path == MODULE_WORKFLOW_FIXTURE_PATH
    assert (
        tuple(case.case_id for case in MODULE_WORKFLOW_BUNDLE.cases)
        == _published_case_ids(MODULE_WORKFLOW_BUNDLE)
    )
    assert len(MODULE_WORKFLOW_BUNDLE.cases) == 114
    assert Counter(case.text_model for case in MODULE_WORKFLOW_BUNDLE.cases) == Counter(
        {"str": 72, "bytes": 42}
    )
    assert len(PATTERN_CASES) == 42
    assert Counter(case.helper for case in PATTERN_CASES) == Counter(
        {
            "search": 14,
            "match": 4,
            "fullmatch": 10,
            "findall": 4,
            "finditer": 4,
            "split": 2,
            "sub": 2,
            "subn": 2,
        }
    )
    assert len(MODULE_CALL_CASES) == 60
    assert Counter(case.helper for case in MODULE_CALL_CASES) == Counter(
        {
            "compile": 9,
            "search": 7,
            "match": 5,
            "fullmatch": 6,
            "split": 9,
            "findall": 2,
            "finditer": 2,
            "sub": 10,
            "subn": 8,
            "escape": 2,
        }
    )
    assert_fixture_bundle_contract(
        MODULE_WORKFLOW_BUNDLE,
        pattern_extractor=case_pattern,
        expected_fixture_path=MODULE_WORKFLOW_FIXTURE_PATH,
        expected_ordered_case_ids=_published_case_ids(MODULE_WORKFLOW_BUNDLE),
    )
    assert VERBOSE_COMPILE_CASE.case_id == VERBOSE_COMPILE_CASE_ID
    assert {
        VERBOSE_COMPILE_CASE_ID,
        MULTILINE_COMPILE_CASE_ID,
        VERBOSE_BYTES_COMPILE_CASE_ID,
        MULTILINE_BYTES_COMPILE_CASE_ID,
    } <= {case.case_id for case in MODULE_WORKFLOW_BUNDLE.cases}
    assert {
        *MODULE_WORKFLOW_BOUNDED_WILDCARD_PATTERN_CASE_IDS,
        "workflow-pattern-search-str-verbose-regression",
        "workflow-pattern-search-str-verbose-regression-digits",
        "workflow-pattern-search-str-verbose-regression-too-many-digits",
        "workflow-pattern-search-str-pos-keyword",
        "workflow-pattern-search-str-bool-endpos-keyword",
        "workflow-pattern-search-bytes-endpos-keyword",
        "workflow-pattern-search-str-pos-indexlike",
        "workflow-pattern-search-bytes-endpos-indexlike",
        "workflow-pattern-search-bytes-verbose-regression",
        "workflow-pattern-search-bytes-verbose-regression-digits",
        "workflow-pattern-search-bytes-verbose-regression-too-many-digits",
        "workflow-pattern-match-str-pos-keyword",
        "workflow-pattern-match-str-bool-pos-keyword",
        "workflow-pattern-fullmatch-str-verbose-regression",
        "workflow-pattern-fullmatch-str-verbose-regression-alpha",
        "workflow-pattern-fullmatch-str-verbose-regression-lowercase-key",
        "workflow-pattern-fullmatch-bytes-verbose-regression",
        "workflow-pattern-fullmatch-bytes-verbose-regression-alpha",
        "workflow-pattern-fullmatch-bytes-verbose-regression-lowercase-key",
        "workflow-pattern-fullmatch-bytes-window-keyword",
        "workflow-pattern-fullmatch-bytes-window-indexlike",
        "workflow-pattern-findall-str-window-keyword",
        "workflow-pattern-findall-str-window-indexlike",
        "workflow-pattern-findall-str-bool-window-keyword",
        "workflow-pattern-finditer-bytes-window-keyword",
        "workflow-pattern-finditer-bytes-window-indexlike",
        "workflow-pattern-finditer-bytes-bool-window-keyword",
    } <= {case.case_id for case in PATTERN_CASES}

    verbose_cases_by_id = {case.case_id: case for case in VERBOSE_COMPILE_WORKFLOW_CASES}
    verbose_bytes_pattern = case_pattern(VERBOSE_BYTES_COMPILE_CASE)
    bounded_wildcard_compile_cases = PUBLISHED_BOUNDED_WILDCARD_COMPILE_CASES
    bounded_wildcard_pattern_cases = PUBLISHED_BOUNDED_WILDCARD_PATTERN_CASES

    assert all(case.text_model == "str" for case in bounded_wildcard_compile_cases)
    assert tuple(
        (case.case_id, case_pattern(case), case.flags or 0)
        for case in bounded_wildcard_compile_cases
    ) == (
        ("workflow-compile-str-bounded-wildcard", "a.c", 0),
        ("workflow-compile-str-bounded-wildcard-ignorecase", "a.c", 2),
    )

    assert all(case.text_model == "str" for case in bounded_wildcard_pattern_cases)
    assert tuple(
        (
            case.case_id,
            case.helper,
            case_pattern(case),
            tuple(case.args),
            case.flags or 0,
        )
        for case in bounded_wildcard_pattern_cases
    ) == (
        (
            "workflow-pattern-search-str-bounded-wildcard-ignorecase",
            "search",
            "a.c",
            ("zaBczz", 1, 5),
            2,
        ),
        (
            "workflow-pattern-match-str-bounded-wildcard",
            "match",
            "a.c",
            ("zabcaxc", 1, 4),
            0,
        ),
        (
            "workflow-pattern-fullmatch-str-bounded-wildcard",
            "fullmatch",
            "a.c",
            ("zaxcz", 1, 4),
            0,
        ),
        (
            "workflow-pattern-findall-str-bounded-wildcard",
            "findall",
            "a.c",
            ("zabcaxcz", 1, 7),
            0,
        ),
        (
            "workflow-pattern-finditer-str-bounded-wildcard",
            "finditer",
            "a.c",
            ("zabcaxcx", 1, 7),
            0,
        ),
        (
            "workflow-pattern-search-str-bounded-wildcard-endpos-miss",
            "search",
            "a.c",
            ("zabc", 1, 3),
            0,
        ),
    )

    assert PATTERN_CASES_BY_ID["workflow-pattern-search-str-verbose-regression-digits"].helper == (
        verbose_cases_by_id["search-multiline-middle-line-digits"].helper
    )
    assert PATTERN_CASES_BY_ID["workflow-pattern-search-str-verbose-regression-digits"].args == [
        verbose_cases_by_id["search-multiline-middle-line-digits"].text
    ]
    assert PATTERN_CASES_BY_ID["workflow-pattern-search-bytes-verbose-regression"].helper == (
        verbose_cases_by_id["search-multiline-middle-line-alpha"].helper
    )
    assert (
        case_pattern(PATTERN_CASES_BY_ID["workflow-pattern-search-bytes-verbose-regression"])
        == verbose_bytes_pattern
    )
    assert (
        PATTERN_CASES_BY_ID["workflow-pattern-search-bytes-verbose-regression"].flags
        == VERBOSE_BYTES_COMPILE_CASE.flags
    )
    assert PATTERN_CASES_BY_ID["workflow-pattern-search-bytes-verbose-regression"].args == [
        verbose_cases_by_id["search-multiline-middle-line-alpha"].text.encode("latin-1")
    ]
    assert PATTERN_CASES_BY_ID[
        "workflow-pattern-search-bytes-verbose-regression-digits"
    ].helper == verbose_cases_by_id["search-multiline-middle-line-digits"].helper
    assert (
        case_pattern(
            PATTERN_CASES_BY_ID["workflow-pattern-search-bytes-verbose-regression-digits"]
        )
        == verbose_bytes_pattern
    )
    assert (
        PATTERN_CASES_BY_ID["workflow-pattern-search-bytes-verbose-regression-digits"].flags
        == VERBOSE_BYTES_COMPILE_CASE.flags
    )
    assert PATTERN_CASES_BY_ID[
        "workflow-pattern-search-bytes-verbose-regression-digits"
    ].args == [verbose_cases_by_id["search-multiline-middle-line-digits"].text.encode("latin-1")]
    assert PATTERN_CASES_BY_ID[
        "workflow-pattern-search-str-verbose-regression-too-many-digits"
    ].helper == verbose_cases_by_id["search-rejects-too-many-digits"].helper
    assert PATTERN_CASES_BY_ID[
        "workflow-pattern-search-str-verbose-regression-too-many-digits"
    ].args == [verbose_cases_by_id["search-rejects-too-many-digits"].text]
    assert PATTERN_CASES_BY_ID[
        "workflow-pattern-search-bytes-verbose-regression-too-many-digits"
    ].helper == verbose_cases_by_id["search-rejects-too-many-digits"].helper
    assert (
        case_pattern(
            PATTERN_CASES_BY_ID["workflow-pattern-search-bytes-verbose-regression-too-many-digits"]
        )
        == verbose_bytes_pattern
    )
    assert (
        PATTERN_CASES_BY_ID["workflow-pattern-search-bytes-verbose-regression-too-many-digits"].flags
        == VERBOSE_BYTES_COMPILE_CASE.flags
    )
    assert PATTERN_CASES_BY_ID[
        "workflow-pattern-search-bytes-verbose-regression-too-many-digits"
    ].args == [verbose_cases_by_id["search-rejects-too-many-digits"].text.encode("latin-1")]
    assert PATTERN_CASES_BY_ID[
        "workflow-pattern-fullmatch-str-verbose-regression-alpha"
    ].helper == verbose_cases_by_id["fullmatch-alpha-with-extra-whitespace"].helper
    assert PATTERN_CASES_BY_ID[
        "workflow-pattern-fullmatch-str-verbose-regression-alpha"
    ].args == [verbose_cases_by_id["fullmatch-alpha-with-extra-whitespace"].text]
    assert PATTERN_CASES_BY_ID[
        "workflow-pattern-fullmatch-bytes-verbose-regression"
    ].helper == verbose_cases_by_id["fullmatch-digits-without-literal-spaces"].helper
    assert (
        case_pattern(PATTERN_CASES_BY_ID["workflow-pattern-fullmatch-bytes-verbose-regression"])
        == verbose_bytes_pattern
    )
    assert (
        PATTERN_CASES_BY_ID["workflow-pattern-fullmatch-bytes-verbose-regression"].flags
        == VERBOSE_BYTES_COMPILE_CASE.flags
    )
    assert PATTERN_CASES_BY_ID["workflow-pattern-fullmatch-bytes-verbose-regression"].args == [
        verbose_cases_by_id["fullmatch-digits-without-literal-spaces"].text.encode("latin-1")
    ]
    assert PATTERN_CASES_BY_ID[
        "workflow-pattern-fullmatch-bytes-verbose-regression-alpha"
    ].helper == verbose_cases_by_id["fullmatch-alpha-with-extra-whitespace"].helper
    assert (
        case_pattern(
            PATTERN_CASES_BY_ID["workflow-pattern-fullmatch-bytes-verbose-regression-alpha"]
        )
        == verbose_bytes_pattern
    )
    assert (
        PATTERN_CASES_BY_ID["workflow-pattern-fullmatch-bytes-verbose-regression-alpha"].flags
        == VERBOSE_BYTES_COMPILE_CASE.flags
    )
    assert PATTERN_CASES_BY_ID[
        "workflow-pattern-fullmatch-bytes-verbose-regression-alpha"
    ].args == [verbose_cases_by_id["fullmatch-alpha-with-extra-whitespace"].text.encode("latin-1")]
    assert PATTERN_CASES_BY_ID[
        "workflow-pattern-fullmatch-str-verbose-regression-lowercase-key"
    ].helper == verbose_cases_by_id["fullmatch-rejects-lowercase-key"].helper
    assert PATTERN_CASES_BY_ID[
        "workflow-pattern-fullmatch-str-verbose-regression-lowercase-key"
    ].args == [verbose_cases_by_id["fullmatch-rejects-lowercase-key"].text]
    assert PATTERN_CASES_BY_ID[
        "workflow-pattern-fullmatch-bytes-verbose-regression-lowercase-key"
    ].helper == verbose_cases_by_id["fullmatch-rejects-lowercase-key"].helper
    assert (
        case_pattern(
            PATTERN_CASES_BY_ID["workflow-pattern-fullmatch-bytes-verbose-regression-lowercase-key"]
        )
        == verbose_bytes_pattern
    )
    assert (
        PATTERN_CASES_BY_ID[
            "workflow-pattern-fullmatch-bytes-verbose-regression-lowercase-key"
        ].flags
        == VERBOSE_BYTES_COMPILE_CASE.flags
    )
    assert PATTERN_CASES_BY_ID[
        "workflow-pattern-fullmatch-bytes-verbose-regression-lowercase-key"
    ].args == [verbose_cases_by_id["fullmatch-rejects-lowercase-key"].text.encode("latin-1")]


def test_module_workflow_surface_publishes_bounded_wildcard_raw_module_helpers_from_direct_cases(
) -> None:
    published_case_signatures = frozenset(
        (
            case.helper,
            case_pattern(case),
            tuple(case.args),
            case.flags,
            case.use_compiled_pattern,
        )
        for case in PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASES
    )
    selected_direct_cases = tuple(
        case
        for case in BOUNDED_WILDCARD_MODULE_MATCH_CASES
        if (
            case.helper,
            case.pattern,
            (case.string,),
            case.flags,
            case.compiled,
        )
        in published_case_signatures
    )

    assert tuple(
        case.case_id for case in PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASES
    ) == (
        "workflow-module-search-str-bounded-wildcard-ignorecase",
        "workflow-module-match-str-bounded-wildcard-miss",
        "workflow-module-fullmatch-str-bounded-wildcard",
    )
    assert len(selected_direct_cases) == len(
        PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASES
    )
    assert tuple(case.case_id for case in selected_direct_cases) == (
        "module-search-ignorecase-bounded-hit",
        "module-match-bounded-miss",
        "module-fullmatch-bounded-hit",
    )
    assert tuple(
        case.helper for case in PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASES
    ) == tuple(case.helper for case in selected_direct_cases)

    for fixture_case, direct_case in zip(
        PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASES,
        selected_direct_cases,
    ):
        assert direct_case.compiled is False
        assert fixture_case.use_compiled_pattern is False
        assert fixture_case.text_model == "str"
        assert case_pattern(fixture_case) == direct_case.pattern
        assert tuple(fixture_case.args) == (direct_case.string,)
        assert fixture_case.flags == direct_case.flags


def test_module_workflow_surface_publishes_module_keyword_helpers_from_direct_cases(
) -> None:
    def direct_signature(
        case: ModuleKeywordCallCase,
    ) -> tuple[str, str | bytes, tuple[object, ...], tuple[tuple[str, str, object], ...], str]:
        pattern, *args = case.args
        return (
            case.helper,
            pattern,
            tuple(args),
            _workflow_keyword_kwargs_signature(case.kwargs),
            "bytes" if isinstance(pattern, bytes) else "str",
        )

    direct_cases_by_signature = {
        direct_signature(case): case for case in MODULE_KEYWORD_CALL_CASES
    }
    selected_direct_cases = tuple(
        direct_cases_by_signature[
            (
                case.helper,
                case_pattern(case),
                tuple(case.args),
                _workflow_keyword_kwargs_signature(case.kwargs),
                case.text_model,
            )
        ]
        for case in PUBLISHED_MODULE_KEYWORD_MODULE_HELPER_CASES
    )

    assert tuple(
        case.case_id
        for case in _fixture_cases_for_text_model(
            PUBLISHED_MODULE_KEYWORD_MODULE_HELPER_CASES,
            "str",
        )
    ) == (
        "workflow-module-search-flags-keyword-str",
        "workflow-module-fullmatch-flags-keyword-str",
        "workflow-module-sub-count-keyword-str",
        "workflow-module-sub-count-indexlike-str",
    )
    assert tuple(
        case.case_id
        for case in _fixture_cases_for_text_model(
            PUBLISHED_MODULE_KEYWORD_MODULE_HELPER_CASES,
            "bytes",
        )
    ) == (
        "workflow-module-match-flags-keyword-bytes",
        "workflow-module-split-maxsplit-keyword-bytes",
        "workflow-module-split-maxsplit-indexlike-bytes",
        "workflow-module-subn-count-keyword-bytes",
        "workflow-module-subn-count-indexlike-bytes",
    )
    assert tuple(
        case.case_id for case in PUBLISHED_MODULE_KEYWORD_MODULE_HELPER_CASES
    ) == (
        "workflow-module-search-flags-keyword-str",
        "workflow-module-match-flags-keyword-bytes",
        "workflow-module-fullmatch-flags-keyword-str",
        "workflow-module-split-maxsplit-keyword-bytes",
        "workflow-module-split-maxsplit-indexlike-bytes",
        "workflow-module-sub-count-keyword-str",
        "workflow-module-sub-count-indexlike-str",
        "workflow-module-subn-count-keyword-bytes",
        "workflow-module-subn-count-indexlike-bytes",
    )
    assert tuple(
        case.case_id for case in selected_direct_cases
    ) == (
        "module-search-flags-keyword-str",
        "module-match-flags-keyword-bytes",
        "module-fullmatch-flags-keyword-str",
        "module-split-maxsplit-keyword-bytes",
        "module-split-maxsplit-indexlike-bytes",
        "module-sub-count-keyword-str",
        "module-sub-count-indexlike-str",
        "module-subn-count-keyword-bytes",
        "module-subn-count-indexlike-bytes",
    )
    assert len(selected_direct_cases) == len(PUBLISHED_MODULE_KEYWORD_MODULE_HELPER_CASES)
    assert Counter(case.helper for case in PUBLISHED_MODULE_KEYWORD_MODULE_HELPER_CASES) == (
        Counter(
            {
                "search": 1,
                "match": 1,
                "fullmatch": 1,
                "split": 2,
                "sub": 2,
                "subn": 2,
            }
        )
    )
    assert tuple(
        case.helper for case in PUBLISHED_MODULE_KEYWORD_MODULE_HELPER_CASES
    ) == tuple(case.helper for case in selected_direct_cases)

    for fixture_case, direct_case in zip(
        PUBLISHED_MODULE_KEYWORD_MODULE_HELPER_CASES,
        selected_direct_cases,
    ):
        direct_pattern, *direct_args = direct_case.args
        assert fixture_case.use_compiled_pattern is False
        assert fixture_case.text_model == (
            "bytes" if isinstance(direct_pattern, bytes) else "str"
        )
        assert case_pattern(fixture_case) == direct_pattern
        assert tuple(fixture_case.args) == tuple(direct_args)
        assert _workflow_keyword_kwargs_signature(
            fixture_case.kwargs
        ) == _workflow_keyword_kwargs_signature(direct_case.kwargs)
        assert fixture_case.flags == 0


def test_module_workflow_surface_publishes_module_keyword_error_slice_from_direct_cases(
) -> None:
    def direct_signature(
        case: ModuleKeywordErrorCase,
    ) -> tuple[str, str | bytes, tuple[object, ...], tuple[tuple[str, str, object], ...], str]:
        pattern, *args = case.args
        return (
            case.helper,
            pattern,
            tuple(args),
            _workflow_keyword_kwargs_signature(case.kwargs),
            "bytes" if isinstance(pattern, bytes) else "str",
        )

    direct_cases_by_signature = {
        direct_signature(case): case for case in MODULE_KEYWORD_ERROR_CASES
    }
    selected_direct_cases = tuple(
        direct_cases_by_signature[
            (
                case.helper,
                case_pattern(case),
                tuple(case.args),
                _workflow_keyword_kwargs_signature(case.kwargs),
                case.text_model,
            )
        ]
        for case in PUBLISHED_MODULE_KEYWORD_ERROR_MODULE_HELPER_CASES
    )

    assert tuple(
        case.case_id for case in PUBLISHED_MODULE_KEYWORD_ERROR_MODULE_HELPER_CASES
    ) == (
        "workflow-module-search-duplicate-flags-keyword",
        "workflow-module-split-duplicate-maxsplit-keyword",
        "workflow-module-sub-duplicate-count-keyword",
        "workflow-module-fullmatch-unexpected-keyword",
        "workflow-module-sub-unexpected-keyword",
    )
    assert tuple(
        case.case_id for case in _fixture_cases_for_text_model(
            PUBLISHED_MODULE_KEYWORD_ERROR_MODULE_HELPER_CASES,
            "str",
        )
    ) == tuple(
        case.case_id for case in PUBLISHED_MODULE_KEYWORD_ERROR_MODULE_HELPER_CASES
    )
    assert tuple(case.case_id for case in selected_direct_cases) == (
        "module-search-duplicate-flags-keyword",
        "module-split-duplicate-maxsplit-keyword",
        "module-sub-duplicate-count-keyword",
        "module-fullmatch-unexpected-keyword",
        "module-sub-unexpected-keyword",
    )
    assert len(selected_direct_cases) == len(PUBLISHED_MODULE_KEYWORD_ERROR_MODULE_HELPER_CASES)
    assert Counter(
        case.helper for case in PUBLISHED_MODULE_KEYWORD_ERROR_MODULE_HELPER_CASES
    ) == Counter(
        {
            "search": 1,
            "split": 1,
            "sub": 2,
            "fullmatch": 1,
        }
    )
    assert tuple(
        case.helper for case in PUBLISHED_MODULE_KEYWORD_ERROR_MODULE_HELPER_CASES
    ) == tuple(case.helper for case in selected_direct_cases)

    for fixture_case, direct_case in zip(
        PUBLISHED_MODULE_KEYWORD_ERROR_MODULE_HELPER_CASES,
        selected_direct_cases,
    ):
        direct_pattern, *direct_args = direct_case.args
        assert fixture_case.include_pattern_arg is True
        assert fixture_case.use_compiled_pattern is False
        assert fixture_case.text_model == "str"
        assert case_pattern(fixture_case) == direct_pattern
        assert tuple(fixture_case.args) == tuple(direct_args)
        assert _workflow_keyword_kwargs_signature(
            fixture_case.kwargs
        ) == _workflow_keyword_kwargs_signature(direct_case.kwargs)
        assert fixture_case.flags == 0


def test_module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases(
) -> None:
    def direct_signature(
        case: PatternKeywordCallCase,
    ) -> tuple[str, str | bytes, tuple[object, ...], tuple[tuple[str, str, object], ...], str]:
        return (
            case.helper,
            case.pattern,
            tuple(case.args),
            _workflow_keyword_kwargs_signature(case.kwargs),
            "bytes" if isinstance(case.pattern, bytes) else "str",
        )

    direct_cases_by_signature = {
        direct_signature(case): case for case in PATTERN_KEYWORD_CALL_CASES
    }
    selected_direct_cases = tuple(
        direct_cases_by_signature[
            (
                case.helper,
                case_pattern(case),
                tuple(case.args),
                _workflow_keyword_kwargs_signature(case.kwargs),
                case.text_model,
            )
        ]
        for case in PUBLISHED_PATTERN_KEYWORD_PATTERN_CASES
    )

    assert tuple(
        case.case_id
        for case in _fixture_cases_for_text_model(
            PUBLISHED_PATTERN_KEYWORD_PATTERN_CASES,
            "str",
        )
    ) == (
        "workflow-pattern-search-str-pos-keyword",
        "workflow-pattern-search-str-bool-endpos-keyword",
        "workflow-pattern-search-str-pos-indexlike",
        "workflow-pattern-match-str-pos-keyword",
        "workflow-pattern-match-str-bool-pos-keyword",
        "workflow-pattern-findall-str-window-keyword",
        "workflow-pattern-findall-str-window-indexlike",
        "workflow-pattern-findall-str-bool-window-keyword",
        "workflow-pattern-split-str-maxsplit-keyword",
        "workflow-pattern-split-str-maxsplit-indexlike",
        "workflow-pattern-subn-count-keyword-str",
        "workflow-pattern-subn-count-indexlike-str",
    )
    assert tuple(
        case.case_id
        for case in _fixture_cases_for_text_model(
            PUBLISHED_PATTERN_KEYWORD_PATTERN_CASES,
            "bytes",
        )
    ) == (
        "workflow-pattern-search-bytes-endpos-keyword",
        "workflow-pattern-search-bytes-endpos-indexlike",
        "workflow-pattern-fullmatch-bytes-window-keyword",
        "workflow-pattern-fullmatch-bytes-window-indexlike",
        "workflow-pattern-finditer-bytes-window-keyword",
        "workflow-pattern-finditer-bytes-window-indexlike",
        "workflow-pattern-finditer-bytes-bool-window-keyword",
        "workflow-pattern-sub-count-keyword-bytes",
        "workflow-pattern-sub-count-indexlike-bytes",
    )
    assert tuple(
        case.case_id for case in PUBLISHED_PATTERN_KEYWORD_PATTERN_CASES
    ) == (
        "workflow-pattern-search-str-pos-keyword",
        "workflow-pattern-search-str-bool-endpos-keyword",
        "workflow-pattern-search-bytes-endpos-keyword",
        "workflow-pattern-search-str-pos-indexlike",
        "workflow-pattern-search-bytes-endpos-indexlike",
        "workflow-pattern-match-str-pos-keyword",
        "workflow-pattern-match-str-bool-pos-keyword",
        "workflow-pattern-fullmatch-bytes-window-keyword",
        "workflow-pattern-fullmatch-bytes-window-indexlike",
        "workflow-pattern-findall-str-window-keyword",
        "workflow-pattern-findall-str-window-indexlike",
        "workflow-pattern-findall-str-bool-window-keyword",
        "workflow-pattern-finditer-bytes-window-keyword",
        "workflow-pattern-finditer-bytes-window-indexlike",
        "workflow-pattern-finditer-bytes-bool-window-keyword",
        "workflow-pattern-split-str-maxsplit-keyword",
        "workflow-pattern-split-str-maxsplit-indexlike",
        "workflow-pattern-sub-count-keyword-bytes",
        "workflow-pattern-sub-count-indexlike-bytes",
        "workflow-pattern-subn-count-keyword-str",
        "workflow-pattern-subn-count-indexlike-str",
    )
    assert tuple(
        case.case_id for case in selected_direct_cases
    ) == (
        "pattern-search-pos-keyword-str",
        "pattern-search-bool-endpos-keyword-str",
        "pattern-search-endpos-keyword-bytes",
        "pattern-search-pos-indexlike-str",
        "pattern-search-endpos-indexlike-bytes",
        "pattern-match-pos-keyword-str",
        "pattern-match-bool-pos-keyword-str",
        "pattern-fullmatch-window-keyword-bytes",
        "pattern-fullmatch-window-indexlike-bytes",
        "pattern-findall-window-keyword-str",
        "pattern-findall-window-indexlike-str",
        "pattern-findall-bool-window-keyword-str",
        "pattern-finditer-window-keyword-bytes",
        "pattern-finditer-window-indexlike-bytes",
        "pattern-finditer-bool-window-keyword-bytes",
        "pattern-split-maxsplit-keyword-str",
        "pattern-split-maxsplit-indexlike-str",
        "pattern-sub-count-keyword-bytes",
        "pattern-sub-count-indexlike-bytes",
        "pattern-subn-count-keyword-str",
        "pattern-subn-count-indexlike-str",
    )
    assert len(selected_direct_cases) == len(PUBLISHED_PATTERN_KEYWORD_PATTERN_CASES)
    assert Counter(case.helper for case in PUBLISHED_PATTERN_KEYWORD_PATTERN_CASES) == (
        Counter(
            {
                "search": 5,
                "match": 2,
                "fullmatch": 2,
                "findall": 3,
                "finditer": 3,
                "split": 2,
                "sub": 2,
                "subn": 2,
            }
        )
    )
    assert tuple(
        case.helper for case in PUBLISHED_PATTERN_KEYWORD_PATTERN_CASES
    ) == tuple(case.helper for case in selected_direct_cases)

    for fixture_case, direct_case in zip(
        PUBLISHED_PATTERN_KEYWORD_PATTERN_CASES,
        selected_direct_cases,
    ):
        assert fixture_case.text_model == (
            "bytes" if isinstance(direct_case.pattern, bytes) else "str"
        )
        assert case_pattern(fixture_case) == direct_case.pattern
        assert tuple(fixture_case.args) == direct_case.args
        assert _workflow_keyword_kwargs_signature(
            fixture_case.kwargs
        ) == _workflow_keyword_kwargs_signature(direct_case.kwargs)
        assert fixture_case.flags == 0


def test_module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases(
) -> None:
    def direct_case_helper(
        case: (
            CompiledPatternCompileCase
            | CompiledPatternModuleHelperCase
            | CompiledPatternModuleKeywordCallCase
            | CompiledPatternModuleKeywordErrorCase
            | CompiledPatternModuleHelperErrorCase
            | BoundedWildcardModuleCase
        ),
    ) -> str:
        if isinstance(case, CompiledPatternCompileCase):
            return "compile"
        return case.helper

    def direct_case_args(
        case: (
            CompiledPatternCompileCase
            | CompiledPatternModuleHelperCase
            | CompiledPatternModuleKeywordCallCase
            | CompiledPatternModuleKeywordErrorCase
            | CompiledPatternModuleHelperErrorCase
            | BoundedWildcardModuleCase
        ),
    ) -> tuple[object, ...]:
        if isinstance(case, CompiledPatternCompileCase):
            return ()
        return tuple(case.args) if hasattr(case, "args") else (case.string,)

    def direct_signature(
        case: (
            CompiledPatternCompileCase
            |
            CompiledPatternModuleHelperCase
            | CompiledPatternModuleKeywordCallCase
            | CompiledPatternModuleKeywordErrorCase
            | CompiledPatternModuleHelperErrorCase
            | BoundedWildcardModuleCase
        ),
    ) -> tuple[
        str,
        str | bytes,
        tuple[object, ...],
        int,
        bool,
        tuple[tuple[str, str, object], ...],
    ]:
        return (
            direct_case_helper(case),
            case.pattern,
            direct_case_args(case),
            getattr(case, "flags", 0),
            getattr(case, "compiled", True),
            _workflow_keyword_kwargs_signature(getattr(case, "kwargs", {})),
        )

    direct_cases_by_signature = {
        direct_signature(case): case
        for case in (
            *COMPILED_PATTERN_COMPILE_CASES,
            *COMPILED_PATTERN_MODULE_HELPER_CASES,
            *COMPILED_PATTERN_MODULE_KEYWORD_CALL_CASES,
            *COMPILED_PATTERN_MODULE_KEYWORD_ERROR_CASES,
            *COMPILED_PATTERN_MODULE_HELPER_ERROR_CASES,
            *BOUNDED_WILDCARD_MODULE_MATCH_CASES,
        )
    }
    selected_direct_cases = tuple(
        direct_cases_by_signature[
            (
                case.helper,
                case_pattern(case),
                tuple(case.args),
                case.flags,
                case.use_compiled_pattern,
                _workflow_keyword_kwargs_signature(case.kwargs),
            )
        ]
        for case in PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES
    )

    assert tuple(
        case.case_id
        for case in _fixture_cases_for_text_model(
            PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES,
            "str",
        )
    ) == (
        "workflow-module-compile-str-compiled-pattern",
        "workflow-module-compile-flags-int-zero-str-compiled-pattern",
        "workflow-module-compile-flags-bool-false-str-compiled-pattern",
        "workflow-module-compile-str-compiled-pattern-named-group",
        "workflow-module-compile-flags-int-zero-str-compiled-pattern-named-group",
        "workflow-module-compile-flags-bool-false-str-compiled-pattern-named-group",
        "workflow-module-search-str-compiled-pattern",
        "workflow-module-search-str-compiled-pattern-on-bytes-string",
        "workflow-module-match-str-compiled-pattern",
        "workflow-module-search-str-bounded-wildcard-ignorecase-compiled-pattern",
        "workflow-module-match-str-bounded-wildcard-compiled-pattern",
        "workflow-module-fullmatch-str-bounded-wildcard-compiled-pattern",
        "workflow-module-fullmatch-str-compiled-pattern-on-bytes-string",
        "workflow-module-split-str-compiled-pattern",
        "workflow-module-split-maxsplit-keyword-str-compiled-pattern",
        "workflow-module-split-duplicate-maxsplit-keyword-str-compiled-pattern",
        "workflow-module-split-str-compiled-pattern-on-bytes-string",
        "workflow-module-finditer-str-compiled-pattern",
        "workflow-module-finditer-str-compiled-pattern-on-bytes-string",
        "workflow-module-sub-str-compiled-pattern",
        "workflow-module-sub-count-keyword-str-compiled-pattern",
        "workflow-module-sub-duplicate-count-keyword-str-compiled-pattern",
        "workflow-module-sub-unexpected-keyword-str-compiled-pattern",
        "workflow-module-sub-str-compiled-pattern-on-bytes-string",
        "workflow-module-subn-count-indexlike-str-compiled-pattern",
    )
    assert tuple(
        case.case_id
        for case in _fixture_cases_for_text_model(
            PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES,
            "bytes",
        )
    ) == (
        "workflow-module-compile-bytes-compiled-pattern",
        "workflow-module-compile-flags-int-zero-bytes-compiled-pattern",
        "workflow-module-compile-flags-bool-false-bytes-compiled-pattern",
        "workflow-module-match-bytes-compiled-pattern-on-str-string",
        "workflow-module-search-bytes-verbose-regression-compiled-pattern",
        "workflow-module-fullmatch-bytes-verbose-regression-compiled-pattern",
        "workflow-module-split-maxsplit-indexlike-bytes-compiled-pattern",
        "workflow-module-split-unexpected-keyword-bytes-compiled-pattern",
        "workflow-module-findall-bytes-compiled-pattern",
        "workflow-module-findall-bytes-compiled-pattern-on-str-string",
        "workflow-module-sub-count-indexlike-bytes-compiled-pattern",
        "workflow-module-subn-bytes-compiled-pattern",
        "workflow-module-subn-count-keyword-bytes-compiled-pattern",
        "workflow-module-subn-duplicate-count-keyword-bytes-compiled-pattern",
        "workflow-module-subn-unexpected-keyword-bytes-compiled-pattern",
        "workflow-module-subn-bytes-compiled-pattern-on-str-string",
    )
    assert len(PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES) == 41
    assert tuple(
        case.case_id for case in PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES
    ) == (
        "workflow-module-compile-str-compiled-pattern",
        "workflow-module-compile-flags-int-zero-str-compiled-pattern",
        "workflow-module-compile-flags-bool-false-str-compiled-pattern",
        "workflow-module-compile-str-compiled-pattern-named-group",
        "workflow-module-compile-flags-int-zero-str-compiled-pattern-named-group",
        "workflow-module-compile-flags-bool-false-str-compiled-pattern-named-group",
        "workflow-module-search-str-compiled-pattern",
        "workflow-module-search-str-compiled-pattern-on-bytes-string",
        "workflow-module-match-str-compiled-pattern",
        "workflow-module-compile-bytes-compiled-pattern",
        "workflow-module-compile-flags-int-zero-bytes-compiled-pattern",
        "workflow-module-compile-flags-bool-false-bytes-compiled-pattern",
        "workflow-module-match-bytes-compiled-pattern-on-str-string",
        "workflow-module-search-str-bounded-wildcard-ignorecase-compiled-pattern",
        "workflow-module-match-str-bounded-wildcard-compiled-pattern",
        "workflow-module-fullmatch-str-bounded-wildcard-compiled-pattern",
        "workflow-module-fullmatch-str-compiled-pattern-on-bytes-string",
        "workflow-module-search-bytes-verbose-regression-compiled-pattern",
        "workflow-module-fullmatch-bytes-verbose-regression-compiled-pattern",
        "workflow-module-split-str-compiled-pattern",
        "workflow-module-split-maxsplit-keyword-str-compiled-pattern",
        "workflow-module-split-maxsplit-indexlike-bytes-compiled-pattern",
        "workflow-module-split-duplicate-maxsplit-keyword-str-compiled-pattern",
        "workflow-module-split-unexpected-keyword-bytes-compiled-pattern",
        "workflow-module-split-str-compiled-pattern-on-bytes-string",
        "workflow-module-findall-bytes-compiled-pattern",
        "workflow-module-findall-bytes-compiled-pattern-on-str-string",
        "workflow-module-finditer-str-compiled-pattern",
        "workflow-module-finditer-str-compiled-pattern-on-bytes-string",
        "workflow-module-sub-str-compiled-pattern",
        "workflow-module-sub-count-keyword-str-compiled-pattern",
        "workflow-module-sub-count-indexlike-bytes-compiled-pattern",
        "workflow-module-sub-duplicate-count-keyword-str-compiled-pattern",
        "workflow-module-sub-unexpected-keyword-str-compiled-pattern",
        "workflow-module-sub-str-compiled-pattern-on-bytes-string",
        "workflow-module-subn-bytes-compiled-pattern",
        "workflow-module-subn-count-keyword-bytes-compiled-pattern",
        "workflow-module-subn-count-indexlike-str-compiled-pattern",
        "workflow-module-subn-duplicate-count-keyword-bytes-compiled-pattern",
        "workflow-module-subn-unexpected-keyword-bytes-compiled-pattern",
        "workflow-module-subn-bytes-compiled-pattern-on-str-string",
    )
    assert tuple(
        case.case_id for case in selected_direct_cases
    ) == (
        "compiled-pattern-compile-str-literal",
        "compiled-pattern-compile-flags-int-zero-str",
        "compiled-pattern-compile-flags-bool-false-str",
        "compiled-pattern-compile-str-named-group",
        "compiled-pattern-compile-flags-int-zero-str-named-group",
        "compiled-pattern-compile-flags-bool-false-str-named-group",
        "compiled-pattern-search-str",
        "compiled-pattern-search-str-on-bytes-string",
        "compiled-pattern-match-str",
        "compiled-pattern-compile-bytes-literal",
        "compiled-pattern-compile-flags-int-zero-bytes",
        "compiled-pattern-compile-flags-bool-false-bytes",
        "compiled-pattern-match-bytes-on-str-string",
        "compiled-module-search-ignorecase-bounded-hit",
        "compiled-module-match-bounded-hit",
        "compiled-module-fullmatch-bounded-hit",
        "compiled-pattern-fullmatch-str-on-bytes-string",
        "compiled-pattern-search-bytes-verbose-regression",
        "compiled-pattern-fullmatch-bytes-verbose-regression",
        "compiled-pattern-split-str-maxsplit",
        "compiled-pattern-split-maxsplit-keyword-str",
        "compiled-pattern-split-maxsplit-indexlike-bytes",
        "compiled-pattern-split-duplicate-maxsplit-keyword-str",
        "compiled-pattern-split-unexpected-keyword-bytes",
        "compiled-pattern-split-str-on-bytes-string",
        "compiled-pattern-findall-bytes",
        "compiled-pattern-findall-bytes-on-str-string",
        "compiled-pattern-finditer-str",
        "compiled-pattern-finditer-str-on-bytes-string",
        "compiled-pattern-sub-str-count",
        "compiled-pattern-sub-count-keyword-str",
        "compiled-pattern-sub-count-indexlike-bytes",
        "compiled-pattern-sub-duplicate-count-keyword-str",
        "compiled-pattern-sub-unexpected-keyword-str",
        "compiled-pattern-sub-str-on-bytes-string",
        "compiled-pattern-subn-bytes-count",
        "compiled-pattern-subn-count-keyword-bytes",
        "compiled-pattern-subn-count-indexlike-str",
        "compiled-pattern-subn-duplicate-count-keyword-bytes",
        "compiled-pattern-subn-unexpected-keyword-bytes",
        "compiled-pattern-subn-bytes-on-str-string",
    )
    assert len(selected_direct_cases) == len(
        PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES
    )
    assert tuple(
        case.helper for case in PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES
    ) == tuple(direct_case_helper(case) for case in selected_direct_cases)

    for fixture_case, direct_case in zip(
        PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES,
        selected_direct_cases,
    ):
        assert fixture_case.use_compiled_pattern is True
        direct_pattern = direct_case.pattern
        direct_args = direct_case_args(direct_case)
        assert fixture_case.text_model == (
            "bytes" if isinstance(direct_pattern, bytes) else "str"
        )
        assert case_pattern(fixture_case) == direct_case.pattern
        assert tuple(fixture_case.args) == direct_args
        assert _workflow_keyword_kwargs_signature(
            fixture_case.kwargs
        ) == _workflow_keyword_kwargs_signature(getattr(direct_case, "kwargs", {}))
        assert fixture_case.flags == getattr(direct_case, "flags", 0)


def test_module_workflow_surface_compile_case_selection_preserves_row_order() -> None:
    manifest_compile_cases = tuple(
        case
        for case in MODULE_WORKFLOW_BUNDLE.manifest.cases
        if case.operation == "compile"
    )
    expected_compile_case_ids = tuple(case.case_id for case in COMPILE_CASES)
    expected_compile_patterns = frozenset(case_pattern(case) for case in COMPILE_CASES)
    expected_operation_helper_counts = Counter(
        (case.operation, case.helper) for case in COMPILE_CASES
    )
    expected_text_models = frozenset(case.text_model for case in COMPILE_CASES)

    assert tuple(case.case_id for case in manifest_compile_cases) == expected_compile_case_ids
    assert (
        frozenset(case_pattern(case) for case in manifest_compile_cases)
        == expected_compile_patterns
    )
    assert (
        Counter((case.operation, case.helper) for case in manifest_compile_cases)
        == expected_operation_helper_counts
    )
    assert expected_operation_helper_counts == Counter(
        {("compile", None): len(COMPILE_CASES)}
    )
    assert frozenset(case.text_model for case in manifest_compile_cases) == expected_text_models
    assert expected_text_models == frozenset({"bytes", "str"})


def test_match_behavior_parity_suite_stays_aligned_with_published_fixture() -> None:
    assert_fixture_bundle_contract(
        MATCH_BEHAVIOR_BUNDLE,
        pattern_extractor=case_pattern,
        expected_fixture_path=MATCH_BEHAVIOR_FIXTURE_PATH,
        expected_ordered_case_ids=_published_case_ids(MATCH_BEHAVIOR_BUNDLE),
    )


def test_match_behavior_parity_suite_tracks_published_case_frontier() -> None:
    assert_fixture_bundle_tracks_published_case_frontier(
        MATCH_BEHAVIOR_BUNDLE,
        selected_case_ids=_published_case_ids(MATCH_BEHAVIOR_BUNDLE),
    )


def test_match_behavior_direct_test_bucket_covers_selected_frontier() -> None:
    assert_direct_test_case_id_buckets_cover_selected_frontier(
        {
            "module-call": frozenset(
                case.case_id for case in MATCH_BEHAVIOR_BUNDLE.cases
            )
        },
        selected_case_ids=_published_case_ids(MATCH_BEHAVIOR_BUNDLE),
        coverage_label="match behavior direct-test case-id bucket",
    )


def test_match_behavior_supplemental_bytes_cases_cover_missing_module_paths() -> None:
    assert {(case.helper, case.matches) for case in SUPPLEMENTAL_BYTES_CASES} == {
        ("search", True),
        ("search", False),
        ("match", True),
        ("match", False),
        ("fullmatch", False),
    }
    assert all(
        isinstance(payload, bytes)
        for case in SUPPLEMENTAL_BYTES_CASES
        for payload in (case.pattern, case.string)
    )


def test_unsupported_backend_skip_reason_ignores_requests_without_callspec() -> None:
    request = SimpleNamespace(node=SimpleNamespace())

    assert _unsupported_backend_skip_reason(request, "rebar") is None


def test_unsupported_backend_skip_reason_preserves_case_param_compatibility() -> None:
    request = _request_with_backend_params(
        case=BackendFixtureContractCase(
            unsupported_backends=("rebar",),
            unsupported_backend_reason="case-style reason",
        )
    )

    assert _unsupported_backend_skip_reason(request, "rebar") == "case-style reason"


def test_unsupported_backend_skip_reason_supports_nonstandard_case_param_names() -> None:
    request = _request_with_backend_params(
        supplemental_case=BackendFixtureContractCase(
            unsupported_backends=("rebar",),
            unsupported_backend_reason="supplemental reason",
        )
    )

    assert _unsupported_backend_skip_reason(request, "rebar") == "supplemental reason"


def test_unsupported_backend_skip_reason_ignores_unrelated_params() -> None:
    request = _request_with_backend_params(
        text="abc",
        flags=0,
        supplemental_case=BackendFixtureContractCase(unsupported_backends=("stdlib",)),
    )

    assert _unsupported_backend_skip_reason(request, "rebar") is None


def test_unsupported_backend_skip_reason_defaults_missing_reason() -> None:
    request = _request_with_backend_params(
        supplemental_case=BackendFixtureContractCase(unsupported_backends=("rebar",))
    )

    assert (
        _unsupported_backend_skip_reason(request, "rebar")
        == "rebar backend unsupported for this parity case"
    )


def test_unsupported_backend_skip_reason_rejects_multiple_param_sources() -> None:
    request = _request_with_backend_params(
        case=BackendFixtureContractCase(
            unsupported_backends=("rebar",),
            unsupported_backend_reason="primary reason",
        ),
        supplemental_case=BackendFixtureContractCase(
            unsupported_backends=("rebar",),
            unsupported_backend_reason="secondary reason",
        ),
    )

    with pytest.raises(
        AssertionError,
        match="multiple parametrized values declare unsupported_backends",
    ):
        _unsupported_backend_skip_reason(request, "rebar")


def test_workflow_keyword_kwargs_signature_distinguishes_bool_int_and_indexlike() -> None:
    assert _workflow_keyword_kwargs_signature(
        {
            "bool_value": True,
            "index_value": _INDEX_ONE,
            "int_value": 1,
        }
    ) == (
        ("bool_value", "bool", True),
        ("index_value", "indexlike", 1),
        ("int_value", "int", 1),
    )
    assert _workflow_keyword_kwargs_signature({"pos": 1}) != (
        _workflow_keyword_kwargs_signature({"pos": _INDEX_ONE})
    )


def test_workflow_keyword_kwargs_signature_normalizes_indexlike_carriers_by_value() -> None:
    class _AlternateIndexLike:
        __slots__ = ("value",)

        def __init__(self, value: int) -> None:
            self.value = value

        def __index__(self) -> int:
            return self.value

        def __repr__(self) -> str:
            return f"AlternateIndexLike({self.value})"

    assert _workflow_keyword_kwargs_signature({"endpos": _INDEX_FOUR}) == (
        _workflow_keyword_kwargs_signature({"endpos": _AlternateIndexLike(4)})
    )


def test_purge_regex_caches_calls_both_backends_before_and_after_test(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    def _record_stdlib_purge() -> None:
        calls.append("stdlib")

    def _record_rebar_purge() -> None:
        calls.append("rebar")

    monkeypatch.setattr(python_conftest.re, "purge", _record_stdlib_purge)
    monkeypatch.setattr(python_conftest.rebar, "purge", _record_rebar_purge)

    fixture_gen = python_conftest.purge_regex_caches.__wrapped__()

    next(fixture_gen)
    assert calls == ["stdlib", "rebar"]

    with pytest.raises(StopIteration):
        next(fixture_gen)

    assert calls == ["stdlib", "rebar", "stdlib", "rebar"]


def test_regex_backend_fixture_returns_stdlib_backend_module() -> None:
    request = _backend_fixture_request("stdlib")

    assert python_conftest.regex_backend.__wrapped__(request) == ("stdlib", re)


@pytest.mark.skipif(
    not rebar.native_module_loaded(),
    reason="rebar backend fixture only resolves when rebar._rebar is available",
)
def test_regex_backend_fixture_returns_rebar_backend_module() -> None:
    request = _backend_fixture_request("rebar")

    assert python_conftest.regex_backend.__wrapped__(request) == ("rebar", rebar)


def test_regex_backend_fixture_propagates_unsupported_backend_skips() -> None:
    request = _backend_fixture_request(
        "rebar",
        case=BackendFixtureContractCase(
            unsupported_backends=("rebar",),
            unsupported_backend_reason="feature slice is stdlib-only",
        ),
    )

    with pytest.raises(pytest.skip.Exception, match="feature slice is stdlib-only"):
        python_conftest.regex_backend.__wrapped__(request)


@pytest.mark.parametrize(
    "case",
    MATCH_BEHAVIOR_BUNDLE.cases,
    ids=lambda case: case.case_id,
)
def test_match_behavior_module_calls_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.operation == "module_call"
    assert case.helper is not None

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = getattr(re, case.helper)(*case.args, **case.kwargs)

    assert_match_result_parity(backend_name, observed, expected, check_regs=True)
    if expected is None:
        assert observed is None
        return

    assert observed is not None
    assert_match_convenience_api_parity(observed, expected)
    assert type(observed.group(0)) is type(expected.group(0))
    assert observed.re.pattern == expected.re.pattern == case_pattern(case)
    assert observed.string == expected.string == _match_behavior_case_string(case)


@pytest.mark.parametrize("case", SUPPLEMENTAL_BYTES_CASES, ids=lambda case: case.case_id)
def test_match_behavior_supplemental_bytes_module_calls_match_cpython(
    regex_backend: tuple[str, object],
    case: SupplementalMatchBehaviorCase,
) -> None:
    backend_name, backend = regex_backend

    observed = getattr(backend, case.helper)(case.pattern, case.string)
    expected = getattr(re, case.helper)(case.pattern, case.string)

    assert_match_result_parity(backend_name, observed, expected, check_regs=True)
    assert (expected is not None) is case.matches
    if expected is None:
        assert observed is None
        return

    assert observed is not None
    assert_match_convenience_api_parity(observed, expected)
    assert type(observed.group(0)) is type(expected.group(0)) is bytes
    assert observed.re.pattern == expected.re.pattern == case.pattern
    assert observed.string == expected.string == case.string


@pytest.mark.parametrize(
    ("helper", "pattern_parts", "string_parts"),
    MATCH_REFERENCE_IDENTITY_CASES,
)
def test_module_match_objects_preserve_pattern_and_string_identity_like_cpython(
    regex_backend: tuple[str, object],
    helper: str,
    pattern_parts: tuple[str, ...] | tuple[bytes, ...],
    string_parts: tuple[str, ...] | tuple[bytes, ...],
) -> None:
    backend_name, backend = regex_backend
    pattern = _join_runtime_text(pattern_parts)
    string = _join_runtime_text(string_parts)

    observed = getattr(backend, helper)(pattern, string)
    expected = getattr(re, helper)(pattern, string)

    assert_match_result_parity(backend_name, observed, expected, check_regs=True)
    assert observed is not None
    assert expected is not None
    _assert_match_input_identity(
        observed,
        expected,
        pattern=pattern,
        string=string,
    )


@pytest.mark.parametrize("case", COMPILE_CASES, ids=lambda case: case.case_id)
def test_compile_workflows_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    pattern = case_pattern(case)

    compile_with_cpython_parity(
        backend_name,
        backend,
        pattern,
        case.flags or 0,
    )


@pytest.mark.parametrize("case", NOFLAG_COMPILE_CASES, ids=lambda case: case.case_id)
def test_explicit_noflag_compile_workflows_match_default_and_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    pattern = case_pattern(case)

    observed_default, expected_default = compile_with_cpython_parity(
        backend_name,
        backend,
        pattern,
    )
    observed_noflag, expected_noflag = compile_with_cpython_parity(
        backend_name,
        backend,
        pattern,
        backend.NOFLAG,
    )

    assert observed_default is observed_noflag
    assert expected_default is expected_noflag
    assert_pattern_parity(backend_name, observed_noflag, expected_noflag)


@pytest.mark.parametrize(
    "flag_mode",
    COMPILED_PATTERN_ZERO_FLAG_MODES,
)
@pytest.mark.parametrize(
    "case",
    COMPILED_PATTERN_COMPILE_CASES,
    ids=lambda case: case.case_id,
)
def test_compile_accepts_compiled_patterns_with_zero_flags_like_cpython(
    regex_backend: tuple[str, object],
    case: CompiledPatternCompileCase,
    flag_mode: str,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern,
    )

    observed = _compile_with_flag_mode(backend, observed_pattern, flag_mode)
    expected = _compile_with_flag_mode(re, expected_pattern, flag_mode)

    assert observed is observed_pattern
    assert expected is expected_pattern
    assert_pattern_parity(backend_name, observed, expected)


@pytest.mark.parametrize(
    "case",
    COMPILED_PATTERN_COMPILE_CASES,
    ids=lambda case: case.case_id,
)
def test_compile_rejects_nonzero_flags_for_compiled_patterns_like_cpython(
    regex_backend: tuple[str, object],
    case: CompiledPatternCompileCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern,
    )

    assert_pattern_parity(backend_name, observed_pattern, expected_pattern)

    with pytest.raises(ValueError) as expected_error:
        re.compile(expected_pattern, int(re.IGNORECASE))

    with pytest.raises(type(expected_error.value)) as observed_error:
        backend.compile(observed_pattern, int(backend.IGNORECASE))

    assert str(observed_error.value) == str(expected_error.value)


@pytest.mark.parametrize(
    "case", VERBOSE_COMPILE_WORKFLOW_CASES, ids=lambda case: case.case_id
)
def test_verbose_compile_workflow_contract_matches_cpython(
    regex_backend: tuple[str, object],
    case: VerboseCompileWorkflowCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = _compile_verbose_regression_pattern(
        backend_name,
        backend,
    )

    _assert_verbose_compile_case_matches_cpython(
        backend_name,
        observed_pattern,
        expected_pattern,
        case,
    )


@pytest.mark.parametrize(
    "case", VERBOSE_COMPILE_WORKFLOW_CASES, ids=lambda case: f"bytes-{case.case_id}"
)
def test_verbose_bytes_compile_workflow_contract_matches_cpython(
    regex_backend: tuple[str, object],
    case: VerboseCompileWorkflowCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = _compile_verbose_regression_bytes_pattern(
        backend_name,
        backend,
    )

    _assert_verbose_compile_bytes_case_matches_cpython(
        backend_name,
        observed_pattern,
        expected_pattern,
        case,
    )


@pytest.mark.parametrize(
    "case", VERBOSE_COMPILE_WORKFLOW_CASES, ids=lambda case: case.case_id
)
def test_verbose_compile_purge_workflow_contract_matches_cpython(
    regex_backend: tuple[str, object],
    case: VerboseCompileWorkflowCase,
) -> None:
    backend_name, backend = regex_backend
    observed_before, expected_before = _compile_verbose_regression_pattern(
        backend_name,
        backend,
    )

    observed_purge_result = backend.purge()
    expected_purge_result = re.purge()

    assert observed_purge_result is None
    assert observed_purge_result == expected_purge_result

    observed_after, expected_after = _compile_verbose_regression_pattern(
        backend_name,
        backend,
    )

    assert observed_before is not observed_after
    assert expected_before is not expected_after
    _assert_verbose_compile_case_matches_cpython(
        backend_name,
        observed_after,
        expected_after,
        case,
    )


@pytest.mark.parametrize(
    "case",
    MATCH_HELPER_PATTERN_CASES,
    ids=lambda case: case.case_id,
)
def test_compiled_pattern_workflows_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case_pattern(case),
        case.flags or 0,
    )
    observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
    expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert_match_result_parity(backend_name, observed, expected)
    if expected is None:
        assert observed is None
        return
    assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize(
    ("helper", "pattern_parts", "string_parts"),
    MATCH_REFERENCE_IDENTITY_CASES,
)
def test_bound_pattern_match_objects_preserve_compiled_pattern_identity_like_cpython(
    regex_backend: tuple[str, object],
    helper: str,
    pattern_parts: tuple[str, ...] | tuple[bytes, ...],
    string_parts: tuple[str, ...] | tuple[bytes, ...],
) -> None:
    backend_name, backend = regex_backend
    pattern = _join_runtime_text(pattern_parts)
    string = _join_runtime_text(string_parts)
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        pattern,
    )

    observed = getattr(observed_pattern, helper)(string)
    expected = getattr(expected_pattern, helper)(string)

    assert_match_result_parity(backend_name, observed, expected, check_regs=True)
    assert observed is not None
    assert expected is not None
    _assert_compiled_match_identity(
        observed,
        expected,
        pattern=pattern,
        string=string,
        observed_pattern=observed_pattern,
        expected_pattern=expected_pattern,
    )


@pytest.mark.parametrize(
    "flag_mode",
    COMPILED_PATTERN_ZERO_FLAG_MODES,
)
@pytest.mark.parametrize(
    "case",
    COMPILED_PATTERN_MODULE_HELPER_CASES,
    ids=lambda case: case.case_id,
)
def test_module_helpers_accept_compiled_patterns_with_cpython_parity(
    regex_backend: tuple[str, object],
    case: CompiledPatternModuleHelperCase,
    flag_mode: str,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern = _compile_compiled_pattern_case(
        backend,
        case.pattern,
        case.flags,
    )
    expected_pattern = _compile_compiled_pattern_case(
        re,
        case.pattern,
        case.flags,
    )

    assert_pattern_parity(backend_name, observed_pattern, expected_pattern)

    observed = _call_module_helper_with_flag_mode(
        backend,
        observed_pattern,
        case,
        flag_mode,
    )
    expected = _call_module_helper_with_flag_mode(
        re,
        expected_pattern,
        case,
        flag_mode,
    )

    if case.result_kind == "match":
        assert_match_result_parity(backend_name, observed, expected, check_regs=True)
        assert expected is not None
        assert_match_convenience_api_parity(observed, expected)
        return

    if case.result_kind == "iter":
        assert_finditer_parity(backend_name, observed, expected, check_regs=True)
        return

    assert_value_parity(observed, expected)


@pytest.mark.parametrize(
    ("helper", "pattern_parts", "string_parts"),
    MATCH_REFERENCE_IDENTITY_CASES,
)
def test_module_helpers_with_compiled_patterns_preserve_match_identity_like_cpython(
    regex_backend: tuple[str, object],
    helper: str,
    pattern_parts: tuple[str, ...] | tuple[bytes, ...],
    string_parts: tuple[str, ...] | tuple[bytes, ...],
) -> None:
    backend_name, backend = regex_backend
    pattern = _join_runtime_text(pattern_parts)
    string = _join_runtime_text(string_parts)
    observed_pattern = _compile_compiled_pattern_case(backend, pattern)
    expected_pattern = _compile_compiled_pattern_case(re, pattern)

    observed = getattr(backend, helper)(observed_pattern, string)
    expected = getattr(re, helper)(expected_pattern, string)

    assert_match_result_parity(backend_name, observed, expected, check_regs=True)
    assert observed is not None
    assert expected is not None
    _assert_compiled_match_identity(
        observed,
        expected,
        pattern=pattern,
        string=string,
        observed_pattern=observed_pattern,
        expected_pattern=expected_pattern,
    )


@pytest.mark.parametrize(
    "flag_mode",
    COMPILED_PATTERN_ZERO_FLAG_MODES,
)
@pytest.mark.parametrize(
    "case",
    VERBOSE_BYTES_COMPILED_PATTERN_MODULE_HELPER_CASES,
    ids=lambda case: case.case_id,
)
def test_module_helpers_preserve_verbose_bytes_compiled_pattern_identity_like_cpython(
    regex_backend: tuple[str, object],
    case: CompiledPatternModuleHelperCase,
    flag_mode: str,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern = _compile_compiled_pattern_case(
        backend,
        case.pattern,
        case.flags,
    )
    expected_pattern = _compile_compiled_pattern_case(
        re,
        case.pattern,
        case.flags,
    )
    string = case.args[0]
    assert isinstance(string, bytes)

    observed = _call_module_helper_with_flag_mode(
        backend,
        observed_pattern,
        case,
        flag_mode,
    )
    expected = _call_module_helper_with_flag_mode(
        re,
        expected_pattern,
        case,
        flag_mode,
    )

    assert_match_result_parity(backend_name, observed, expected, check_regs=True)
    assert observed is not None
    assert expected is not None
    _assert_compiled_match_identity(
        observed,
        expected,
        pattern=case.pattern,
        string=string,
        observed_pattern=observed_pattern,
        expected_pattern=expected_pattern,
    )


@pytest.mark.parametrize(
    "case",
    COMPILED_PATTERN_MODULE_HELPER_CASES,
    ids=lambda case: case.case_id,
)
def test_module_helpers_reject_flags_for_compiled_patterns_like_cpython(
    regex_backend: tuple[str, object],
    case: CompiledPatternModuleHelperCase,
) -> None:
    _, backend = regex_backend
    observed_pattern = _compile_compiled_pattern_case(
        backend,
        case.pattern,
        case.flags,
    )
    expected_pattern = _compile_compiled_pattern_case(
        re,
        case.pattern,
        case.flags,
    )

    with pytest.raises(ValueError) as expected_error:
        getattr(re, case.helper)(
            expected_pattern,
            *case.args,
            flags=int(re.IGNORECASE),
        )

    with pytest.raises(type(expected_error.value)) as observed_error:
        getattr(backend, case.helper)(
            observed_pattern,
            *case.args,
            flags=int(backend.IGNORECASE),
        )

    assert str(observed_error.value) == str(expected_error.value)


@pytest.mark.parametrize(
    "case",
    COMPILED_PATTERN_MODULE_HELPER_ERROR_CASES,
    ids=lambda case: case.case_id,
)
def test_module_helpers_preserve_compiled_pattern_type_errors_like_cpython(
    regex_backend: tuple[str, object],
    case: CompiledPatternModuleHelperErrorCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern = _compile_compiled_pattern_case(backend, case.pattern)
    expected_pattern = _compile_compiled_pattern_case(re, case.pattern)

    assert_pattern_parity(backend_name, observed_pattern, expected_pattern)

    observed_error = _capture_error(
        lambda: getattr(backend, case.helper)(observed_pattern, *case.args)
    )
    expected_error = _capture_error(
        lambda: getattr(re, case.helper)(expected_pattern, *case.args)
    )

    assert type(observed_error) is type(expected_error)
    assert observed_error.args == expected_error.args


@pytest.mark.parametrize("case", MODULE_KEYWORD_CALL_CASES, ids=lambda case: case.case_id)
def test_module_keyword_argument_calls_match_cpython(
    regex_backend: tuple[str, object],
    case: ModuleKeywordCallCase,
) -> None:
    backend_name, backend = regex_backend
    observed = _call_module_keyword_case(backend, case)
    expected = _call_module_keyword_case(re, case)

    if case.result_kind == "match":
        assert_match_result_parity(backend_name, observed, expected, check_regs=True)
        assert expected is not None
        assert_match_convenience_api_parity(observed, expected)
        return

    assert_value_parity(observed, expected)


@pytest.mark.parametrize("case", PATTERN_KEYWORD_CALL_CASES, ids=lambda case: case.case_id)
def test_pattern_keyword_argument_calls_match_cpython(
    regex_backend: tuple[str, object],
    case: PatternKeywordCallCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern,
        case.flags,
    )

    observed = _call_pattern_keyword_case(observed_pattern, case)
    expected = _call_pattern_keyword_case(expected_pattern, case)

    if case.result_kind == "match":
        assert_match_result_parity(backend_name, observed, expected, check_regs=True)
        assert expected is not None
        assert_match_convenience_api_parity(observed, expected)
        return

    if case.result_kind == "iter":
        assert_finditer_parity(backend_name, observed, expected, check_regs=True)
        return

    assert_value_parity(observed, expected)


@pytest.mark.parametrize("case", MODULE_KEYWORD_ERROR_CASES, ids=lambda case: case.case_id)
def test_module_keyword_argument_errors_match_cpython(
    regex_backend: tuple[str, object],
    case: ModuleKeywordErrorCase,
) -> None:
    _, backend = regex_backend

    observed_error = _capture_error(
        lambda: getattr(backend, case.helper)(*case.args, **case.kwargs)
    )
    expected_error = _capture_error(
        lambda: getattr(re, case.helper)(*case.args, **case.kwargs)
    )

    assert type(observed_error) is type(expected_error)
    assert observed_error.args == expected_error.args


@pytest.mark.parametrize(
    "case",
    COMPILED_PATTERN_MODULE_KEYWORD_CALL_CASES,
    ids=lambda case: case.case_id,
)
def test_compiled_pattern_module_keyword_argument_calls_match_cpython(
    regex_backend: tuple[str, object],
    case: CompiledPatternModuleKeywordCallCase,
) -> None:
    observed_backend_name, observed_backend = regex_backend
    observed_pattern = _compile_compiled_pattern_case(
        observed_backend,
        case.pattern,
        case.flags,
    )
    expected_pattern = _compile_compiled_pattern_case(re, case.pattern, case.flags)

    observed = getattr(observed_backend, case.helper)(
        observed_pattern,
        *case.args,
        **case.kwargs,
    )
    expected = getattr(re, case.helper)(expected_pattern, *case.args, **case.kwargs)

    if case.helper == "compile":
        assert observed is observed_pattern
        assert expected is expected_pattern
        assert_pattern_parity(observed_backend_name, observed, expected)
        return

    assert_value_parity(observed, expected)


@pytest.mark.parametrize(
    "case",
    COMPILED_PATTERN_MODULE_KEYWORD_ERROR_CASES,
    ids=lambda case: case.case_id,
)
def test_compiled_pattern_module_keyword_argument_errors_match_cpython(
    regex_backend: tuple[str, object],
    case: CompiledPatternModuleKeywordErrorCase,
) -> None:
    _, backend = regex_backend

    observed_error = _capture_error(
        lambda: _call_compiled_pattern_module_keyword_case(backend, case)
    )
    expected_error = _capture_error(
        lambda: _call_compiled_pattern_module_keyword_case(re, case)
    )

    assert type(observed_error) is type(expected_error)
    assert observed_error.args == expected_error.args


@pytest.mark.parametrize("case", CACHE_CASES, ids=lambda case: case.case_id)
def test_compile_cache_workflows_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    pattern = case_pattern(case)
    flags = case.flags or 0

    observed_first, expected_first = compile_with_cpython_parity(
        backend_name,
        backend,
        pattern,
        flags,
    )
    observed_second = backend.compile(pattern, flags)
    expected_second = re.compile(pattern, flags)

    assert observed_first is observed_second
    assert expected_first is expected_second
    assert_pattern_parity(backend_name, observed_second, expected_second)


@pytest.mark.parametrize("case", PURGE_CASES, ids=lambda case: case.case_id)
def test_purge_workflows_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    pattern = case_pattern(case)
    flags = case.flags or 0

    observed_before, expected_before = compile_with_cpython_parity(
        backend_name,
        backend,
        pattern,
        flags,
    )
    assert observed_before is backend.compile(pattern, flags)
    assert expected_before is re.compile(pattern, flags)

    observed_purge_result = backend.purge()
    expected_purge_result = re.purge()
    assert observed_purge_result is None
    assert observed_purge_result == expected_purge_result

    observed_after = backend.compile(pattern, flags)
    expected_after = re.compile(pattern, flags)

    assert observed_before is not observed_after
    assert expected_before is not expected_after
    assert observed_after is backend.compile(pattern, flags)
    assert expected_after is re.compile(pattern, flags)
    assert_pattern_parity(backend_name, observed_after, expected_after)


@pytest.mark.parametrize("case", ESCAPE_CASES, ids=lambda case: case.case_id)
def test_escape_workflows_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    _, backend = regex_backend
    assert case.helper == "escape"

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = re.escape(*case.args, **case.kwargs)

    assert type(observed) is type(expected)
    assert observed == expected


@pytest.mark.parametrize(
    "case",
    ESCAPE_COMPATIBLE_INPUT_CASES,
    ids=lambda case: case.case_id,
)
def test_escape_accepts_cpython_compatible_input_shapes(
    regex_backend: tuple[str, object],
    case: EscapeCompatibleInputCase,
) -> None:
    _, backend = regex_backend
    raw = case.input_factory()

    observed = backend.escape(raw)
    expected = re.escape(raw)

    assert type(observed) is type(expected)
    assert observed == expected


def test_escape_matches_cpython_across_deterministic_str_corpus(
    regex_backend: tuple[str, object],
) -> None:
    _, backend = regex_backend

    for raw in ESCAPE_DIFFERENTIAL_STR_CORPUS:
        observed = backend.escape(raw)
        expected = re.escape(raw)

        assert type(observed) is type(expected)
        assert observed == expected, repr(raw)


def test_escape_matches_cpython_across_deterministic_bytes_corpus(
    regex_backend: tuple[str, object],
) -> None:
    _, backend = regex_backend

    for raw in ESCAPE_DIFFERENTIAL_BYTES_CORPUS:
        observed = backend.escape(raw)
        expected = re.escape(raw)

        assert type(observed) is type(expected)
        assert observed == expected, repr(raw)


@pytest.mark.parametrize(
    "case",
    ESCAPE_INVALID_INPUT_CASES,
    ids=lambda case: case.case_id,
)
def test_escape_rejects_invalid_input_shapes_like_cpython(
    regex_backend: tuple[str, object],
    case: EscapeInvalidInputCase,
) -> None:
    _, backend = regex_backend
    raw = case.input_factory()

    observed_error = _capture_error(lambda: backend.escape(raw))
    expected_error = _capture_error(lambda: re.escape(raw))

    assert type(observed_error) is type(expected_error)
    assert observed_error.args == expected_error.args


def test_source_package_native_metadata_matches_literal_contract() -> None:
    assert rebar.TARGET_CPYTHON_SERIES == "3.12.x"
    assert rebar.SCAFFOLD_STATUS == "scaffold-only"
    assert rebar.NATIVE_MODULE_NAME == "rebar._rebar"
    assert isinstance(rebar.native_module_loaded(), bool)

    if rebar.native_module_loaded():
        assert rebar.native_scaffold_status() == "scaffold-only"
        assert rebar.native_target_cpython_series() == "3.12.x"
    else:
        assert rebar.native_scaffold_status() is None
        assert rebar.native_target_cpython_series() is None


@pytest.mark.skipif(
    MATURIN is None,
    reason="native extension smoke requires a maturin executable on PATH",
)
def test_built_native_module_workflow_surface_contract() -> None:
    with tempfile.TemporaryDirectory(prefix="rebar-native-smoke-") as temp_dir:
        temp_root = pathlib.Path(temp_dir)
        provisioned, temp_dir_handle, error = benchmarks.provision_built_native_runtime()
        assert provisioned is not None, error
        assert temp_dir_handle is not None, error

        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join(
            str(path) for path in (provisioned["install_root"], PYTHON_SOURCE)
        )

        try:
            completed = subprocess.run(
                [sys.executable, "-c", _BUILT_WHEEL_SMOKE_PROBE],
                cwd=temp_root,
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )
        finally:
            temp_dir_handle.cleanup()
        result = json.loads(completed.stdout)

        assert result["native_module_loaded"]
        assert result["native_scaffold_status"] == "scaffold-only"
        assert result["native_target_cpython_series"] == "3.12.x"
        assert result["native_private_flag"]
        assert result["native_module_name"] == "rebar._rebar"
        assert result["exported_helpers_present"]
        assert result["purge_result"] is None
        assert result["template_exception"] == {
            "type": "NotImplementedError",
            "message": "rebar.template() is a scaffold placeholder",
        }
        assert result["compile_exception"] is None
        assert result["compiled_pattern"] == {
            "type_name": "Pattern",
            "type_module": "re",
            "pattern": "abc",
            "flags": 34,
            "groups": 0,
            "groupindex": {},
        }
        assert result["compiled_search_exception"] is None
        assert result["compiled_search"] == {
            "type_name": "Match",
            "group0": "abc",
            "span": [0, 3],
        }
        assert result["literal_search"] == {
            "type_name": "Match",
            "group0": "abc",
            "span": [2, 5],
        }
        assert result["literal_match_none"] is None
        assert result["literal_fullmatch"] == {
            "type_name": "Match",
            "group0": "abc",
            "span": [0, 3],
        }
        assert result["literal_split"] == ["", "abc"]
        assert result["literal_findall"] == ["abc", "abc"]
        assert result["literal_finditer"] == [
            {
                "type_name": "Match",
                "group0": "abc",
                "span": [1, 4],
            },
            {
                "type_name": "Match",
                "group0": "abc",
                "span": [4, 7],
            },
        ]
        assert result["escape_outputs"] == {
            "simple_str": "a\\-b\\.c",
            "punctuation_str": '\\ !"\\#%\\&,/:;<=>@`\\~',
            "simple_bytes": "a\\-b\\.c",
        }


def test_source_package_compile_metadata_matches_pinned_literal_contract() -> None:
    literal_pattern, expected_literal = compile_with_cpython_parity(
        "rebar",
        rebar,
        "abc",
        int(rebar.IGNORECASE),
    )
    assert type(literal_pattern) is rebar.Pattern
    assert literal_pattern.pattern == expected_literal.pattern == "abc"
    assert literal_pattern.flags == expected_literal.flags == int(
        rebar.IGNORECASE | rebar.UNICODE
    )
    assert literal_pattern.groups == expected_literal.groups == 0
    assert literal_pattern.groupindex == expected_literal.groupindex == {}

    bytes_pattern, expected_bytes = compile_with_cpython_parity(
        "rebar",
        rebar,
        b"abc",
        int(rebar.IGNORECASE),
    )
    assert type(bytes_pattern) is rebar.Pattern
    assert bytes_pattern.pattern == expected_bytes.pattern == b"abc"
    assert bytes_pattern.flags == expected_bytes.flags == int(rebar.IGNORECASE)
    assert bytes_pattern.groups == expected_bytes.groups == 0
    assert bytes_pattern.groupindex == expected_bytes.groupindex == {}

    anchored_pattern, expected_anchored = compile_with_cpython_parity(
        "rebar",
        rebar,
        "^abc$",
    )
    assert type(anchored_pattern) is rebar.Pattern
    assert anchored_pattern.pattern == expected_anchored.pattern == "^abc$"
    assert anchored_pattern.flags == expected_anchored.flags == int(rebar.UNICODE)
    assert anchored_pattern.groups == expected_anchored.groups == 0
    assert anchored_pattern.groupindex == expected_anchored.groupindex == {}


@pytest.mark.skipif(
    not rebar.native_module_loaded(),
    reason="verbose regression compile support requires rebar._rebar",
)
def test_source_package_verbose_compile_metadata_and_neighbor_gaps_remain_pinned() -> None:
    pattern = case_pattern(VERBOSE_COMPILE_CASE)
    assert isinstance(pattern, str)
    multiline_pattern = case_pattern(MULTILINE_COMPILE_CASE)
    assert multiline_pattern == pattern
    bytes_pattern = case_pattern(MULTILINE_BYTES_COMPILE_CASE)
    assert isinstance(bytes_pattern, bytes)
    assert bytes_pattern == pattern.encode("ascii")

    compiled, expected = _compile_verbose_regression_pattern("rebar", rebar)
    compiled_bytes, expected_bytes = compile_with_cpython_parity(
        "rebar",
        rebar,
        bytes_pattern,
        int(VERBOSE_COMPILE_CASE.flags or 0),
    )

    assert type(compiled) is rebar.Pattern
    assert compiled.pattern == expected.pattern == pattern
    assert compiled.flags == expected.flags == int(
        re.MULTILINE | re.VERBOSE | re.UNICODE
    )
    assert compiled.groups == expected.groups == 1
    assert compiled.groupindex == expected.groupindex == {"key": 1}
    assert rebar.compile(pattern, VERBOSE_COMPILE_CASE.flags or 0) is compiled

    assert type(compiled_bytes) is rebar.Pattern
    assert compiled_bytes.pattern == expected_bytes.pattern == bytes_pattern
    assert compiled_bytes.flags == expected_bytes.flags == int(
        re.MULTILINE | re.VERBOSE
    )
    assert compiled_bytes.groups == expected_bytes.groups == 1
    assert compiled_bytes.groupindex == expected_bytes.groupindex == {"key": 1}
    assert (
        rebar.compile(bytes_pattern, int(VERBOSE_COMPILE_CASE.flags or 0))
        is compiled_bytes
    )
    for case in VERBOSE_COMPILE_WORKFLOW_CASES:
        _assert_verbose_compile_bytes_case_matches_cpython(
            "rebar",
            compiled_bytes,
            expected_bytes,
            case,
        )

    compiled_multiline, expected_multiline = compile_with_cpython_parity(
        "rebar",
        rebar,
        multiline_pattern,
        rebar.MULTILINE,
    )

    assert int(MULTILINE_COMPILE_CASE.flags or 0) == int(rebar.MULTILINE)
    assert type(compiled_multiline) is rebar.Pattern
    assert compiled_multiline.pattern == expected_multiline.pattern == multiline_pattern
    assert compiled_multiline.flags == expected_multiline.flags == int(
        re.MULTILINE | re.UNICODE
    )
    assert compiled_multiline.groups == expected_multiline.groups == 1
    assert compiled_multiline.groupindex == expected_multiline.groupindex == {"key": 1}
    assert rebar.compile(multiline_pattern, rebar.MULTILINE) is compiled_multiline

    assert int(MULTILINE_BYTES_COMPILE_CASE.flags or 0) == int(rebar.MULTILINE)
    compiled_bytes_multiline, expected_bytes_multiline = compile_with_cpython_parity(
        "rebar",
        rebar,
        bytes_pattern,
        int(MULTILINE_BYTES_COMPILE_CASE.flags or 0),
    )

    assert type(compiled_bytes_multiline) is rebar.Pattern
    assert compiled_bytes_multiline.pattern == expected_bytes_multiline.pattern == bytes_pattern
    assert compiled_bytes_multiline.flags == expected_bytes_multiline.flags == int(
        re.MULTILINE
    )
    assert compiled_bytes_multiline.groups == expected_bytes_multiline.groups == 1
    assert (
        compiled_bytes_multiline.groupindex
        == expected_bytes_multiline.groupindex
        == {"key": 1}
    )
    assert (
        rebar.compile(bytes_pattern, int(MULTILINE_BYTES_COMPILE_CASE.flags or 0))
        is compiled_bytes_multiline
    )


def test_source_package_compile_reuses_existing_pattern_without_reprocessing_flags() -> None:
    pattern = rebar.compile("abc")

    assert rebar.compile(pattern) is pattern

    with pytest.raises(ValueError) as raised:
        rebar.compile(pattern, rebar.IGNORECASE)

    assert str(raised.value) == "cannot process flags argument with a compiled pattern"


def test_source_package_compile_rejects_non_pattern_inputs() -> None:
    with pytest.raises(TypeError) as raised:
        rebar.compile(123)

    assert str(raised.value) == "first argument must be string or compiled pattern"


def test_source_package_module_literal_match_contract_matches_cpython() -> None:
    search_match = rebar.search("abc", "zzabczz")
    expected_search = re.search("abc", "zzabczz")
    assert search_match is not None
    assert expected_search is not None
    assert_match_result_parity("rebar", search_match, expected_search, check_regs=True)
    assert_match_convenience_api_parity(search_match, expected_search)
    _assert_literal_match_contract(search_match, "abc", (2, 5), 7)

    anchored_match = rebar.match("abc", "abcdef")
    expected_match = re.match("abc", "abcdef")
    assert anchored_match is not None
    assert expected_match is not None
    assert_match_result_parity("rebar", anchored_match, expected_match, check_regs=True)
    assert_match_convenience_api_parity(anchored_match, expected_match)
    _assert_literal_match_contract(anchored_match, "abc", (0, 3), 6)

    full_match = rebar.fullmatch("abc", "abc")
    expected_fullmatch = re.fullmatch("abc", "abc")
    assert full_match is not None
    assert expected_fullmatch is not None
    assert_match_result_parity("rebar", full_match, expected_fullmatch, check_regs=True)
    assert_match_convenience_api_parity(full_match, expected_fullmatch)
    _assert_literal_match_contract(full_match, "abc", (0, 3), 3)

    assert rebar.search("abc", "zzz") is re.search("abc", "zzz") is None
    assert rebar.match("abc", "zabc") is re.match("abc", "zabc") is None
    assert rebar.fullmatch("abc", "abcz") is re.fullmatch("abc", "abcz") is None


def test_source_package_pattern_literal_str_match_contract_matches_cpython() -> None:
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        "rebar",
        rebar,
        "abc",
    )

    search_match = observed_pattern.search("zzabczz")
    expected_search = expected_pattern.search("zzabczz")
    assert search_match is not None
    assert expected_search is not None
    assert_match_result_parity("rebar", search_match, expected_search, check_regs=True)
    assert_match_convenience_api_parity(search_match, expected_search)
    _assert_literal_match_contract(search_match, "abc", (2, 5), 7)

    anchored_match = observed_pattern.match("abcdef")
    expected_match = expected_pattern.match("abcdef")
    assert anchored_match is not None
    assert expected_match is not None
    assert_match_result_parity("rebar", anchored_match, expected_match, check_regs=True)
    assert_match_convenience_api_parity(anchored_match, expected_match)
    _assert_literal_match_contract(anchored_match, "abc", (0, 3), 6)

    full_match = observed_pattern.fullmatch("abc")
    expected_fullmatch = expected_pattern.fullmatch("abc")
    assert full_match is not None
    assert expected_fullmatch is not None
    assert_match_result_parity("rebar", full_match, expected_fullmatch, check_regs=True)
    assert_match_convenience_api_parity(full_match, expected_fullmatch)
    _assert_literal_match_contract(full_match, "abc", (0, 3), 3)

    assert observed_pattern.search("zzz") is expected_pattern.search("zzz") is None
    assert observed_pattern.match("zabc") is expected_pattern.match("zabc") is None
    assert (
        observed_pattern.fullmatch("abcz")
        is expected_pattern.fullmatch("abcz")
        is None
    )


def test_source_package_pattern_literal_bytes_match_contract_matches_cpython() -> None:
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        "rebar",
        rebar,
        b"abc",
    )

    search_match = observed_pattern.search(b"zzabczz")
    expected_search = expected_pattern.search(b"zzabczz")
    assert search_match is not None
    assert expected_search is not None
    assert_match_result_parity("rebar", search_match, expected_search, check_regs=True)
    assert_match_convenience_api_parity(search_match, expected_search)
    _assert_literal_match_contract(search_match, b"abc", (2, 5), 7)

    anchored_match = observed_pattern.match(b"abcdef")
    expected_match = expected_pattern.match(b"abcdef")
    assert anchored_match is not None
    assert expected_match is not None
    assert_match_result_parity("rebar", anchored_match, expected_match, check_regs=True)
    assert_match_convenience_api_parity(anchored_match, expected_match)
    _assert_literal_match_contract(anchored_match, b"abc", (0, 3), 6)

    full_match = observed_pattern.fullmatch(b"abc")
    expected_fullmatch = expected_pattern.fullmatch(b"abc")
    assert full_match is not None
    assert expected_fullmatch is not None
    assert_match_result_parity("rebar", full_match, expected_fullmatch, check_regs=True)
    assert_match_convenience_api_parity(full_match, expected_fullmatch)
    _assert_literal_match_contract(full_match, b"abc", (0, 3), 3)

    assert observed_pattern.search(b"zzz") is expected_pattern.search(b"zzz") is None
    assert observed_pattern.match(b"zabc") is expected_pattern.match(b"zabc") is None
    assert (
        observed_pattern.fullmatch(b"abcz")
        is expected_pattern.fullmatch(b"abcz")
        is None
    )


@pytest.mark.parametrize("accessor_name", ("group", "span", "start", "end"))
def test_source_package_match_accessors_reject_missing_groups_like_cpython(
    accessor_name: str,
) -> None:
    observed_match = rebar.search("abc", "abc")
    expected_match = re.search("abc", "abc")
    assert observed_match is not None
    assert expected_match is not None

    observed_error = _capture_error(lambda: getattr(observed_match, accessor_name)(1))
    expected_error = _capture_error(lambda: getattr(expected_match, accessor_name)(1))

    assert type(observed_error) is type(expected_error)
    assert observed_error.args == expected_error.args == ("no such group",)


def test_source_package_match_group_rejects_missing_named_groups_like_cpython() -> None:
    observed_match = rebar.search("abc", "abc")
    expected_match = re.search("abc", "abc")
    assert observed_match is not None
    assert expected_match is not None

    observed_error = _capture_error(lambda: observed_match.group("name"))
    expected_error = _capture_error(lambda: expected_match.group("name"))

    assert type(observed_error) is type(expected_error)
    assert observed_error.args == expected_error.args == ("no such group",)


def test_source_package_matching_rejects_string_bytes_mismatch_like_cpython() -> None:
    observed_string_error = _capture_error(lambda: rebar.search("abc", b"abc"))
    expected_string_error = _capture_error(lambda: re.search("abc", b"abc"))
    assert type(observed_string_error) is type(expected_string_error)
    assert observed_string_error.args == expected_string_error.args == (
        "cannot use a string pattern on a bytes-like object",
    )

    observed_bytes_error = _capture_error(lambda: rebar.search(b"abc", "abc"))
    expected_bytes_error = _capture_error(lambda: re.search(b"abc", "abc"))
    assert type(observed_bytes_error) is type(expected_bytes_error)
    assert observed_bytes_error.args == expected_bytes_error.args == (
        "cannot use a bytes pattern on a string-like object",
    )


def test_source_package_unsupported_match_surface_stays_loud() -> None:
    with pytest.raises(NotImplementedError) as module_flags:
        rebar.search("abc", "abc", rebar.IGNORECASE | rebar.VERBOSE)

    assert_placeholder_message_contains(
        module_flags.value,
        "rebar.search() is a scaffold placeholder",
    )

    with pytest.raises(NotImplementedError) as module_meta:
        rebar.search("[ab]c", "abc")

    assert_placeholder_message_contains(
        module_meta.value,
        "rebar.compile() is a scaffold placeholder",
    )

    pattern = rebar.compile("abc", rebar.IGNORECASE | rebar.VERBOSE)
    for method_name in ("search", "match", "fullmatch"):
        with pytest.raises(NotImplementedError) as bound_flags:
            getattr(pattern, method_name)("abc")

        assert_placeholder_message_contains(
            bound_flags.value,
            f"rebar.Pattern.{method_name}() is a scaffold placeholder",
        )


def test_source_package_compile_reuses_cached_patterns_for_supported_inputs() -> None:
    first = rebar.compile("abc")
    second = rebar.compile("abc")
    flagged = rebar.compile("abc", rebar.IGNORECASE)
    flagged_again = rebar.compile("abc", rebar.IGNORECASE)
    bytes_pattern = rebar.compile(b"abc")
    bytes_pattern_again = rebar.compile(b"abc")

    assert first is second
    assert flagged is flagged_again
    assert bytes_pattern is bytes_pattern_again
    assert first is not flagged
    assert first is not bytes_pattern


def test_source_package_purge_clears_cached_patterns_and_returns_none() -> None:
    original = rebar.compile("abc")

    assert rebar.purge() is None
    assert rebar.purge() is None

    refreshed = rebar.compile("abc")
    assert original is not refreshed
    assert refreshed is rebar.compile("abc")


def test_source_package_unsupported_compile_requests_do_not_mutate_cache() -> None:
    cached = rebar.compile("abc")

    with pytest.raises(NotImplementedError) as placeholder:
        rebar.compile("[ab]c")

    assert_placeholder_message_contains(
        placeholder.value,
        "rebar.compile() is a scaffold placeholder",
    )
    assert rebar.compile("abc") is cached

    with pytest.raises(TypeError) as wrong_type:
        rebar.compile(123)

    assert str(wrong_type.value) == "first argument must be string or compiled pattern"
    assert rebar.compile("abc") is cached

    with pytest.raises(ValueError) as compiled_flags:
        rebar.compile(cached, rebar.IGNORECASE)

    assert str(compiled_flags.value) == (
        "cannot process flags argument with a compiled pattern"
    )
    assert rebar.compile("abc") is cached


def test_source_package_cache_keys_distinguish_normalized_flags() -> None:
    default_pattern = rebar.compile("abc")
    unicode_pattern = rebar.compile("abc", rebar.UNICODE)
    ascii_pattern = rebar.compile("abc", rebar.ASCII)

    assert default_pattern is unicode_pattern
    assert default_pattern is not ascii_pattern


@pytest.mark.parametrize(("raw", "expected"), EXPLICIT_ESCAPE_STR_CASES)
def test_source_package_escape_preserves_explicit_str_cases(
    raw: str,
    expected: str,
) -> None:
    escaped = rebar.escape(raw)

    assert type(escaped) is str
    assert escaped == re.escape(raw) == expected


@pytest.mark.parametrize(("raw", "expected"), EXPLICIT_ESCAPE_BYTES_CASES)
def test_source_package_escape_preserves_explicit_bytes_cases(
    raw: bytes,
    expected: bytes,
) -> None:
    escaped = rebar.escape(raw)

    assert type(escaped) is bytes
    assert escaped == re.escape(raw) == expected


def test_literal_collection_suite_stays_aligned_with_published_fixture_rows() -> None:
    assert_fixture_bundle_contract(
        COLLECTION_REPLACEMENT_BUNDLE,
        pattern_extractor=case_pattern,
        expected_fixture_path=(
            CORRECTNESS_FIXTURES_ROOT / "collection_replacement_workflows.py"
        ),
        expected_ordered_case_ids=_published_case_ids(COLLECTION_REPLACEMENT_BUNDLE),
    )


def test_literal_collection_suite_tracks_published_case_frontier() -> None:
    assert_fixture_bundle_tracks_published_case_frontier(
        COLLECTION_REPLACEMENT_BUNDLE,
        selected_case_ids=tuple(
            case.case_id for case in PUBLISHED_COLLECTION_FIXTURE_CASES
        ),
        expected_uncovered_case_ids=tuple(
            case.case_id
            for case in _fixture_cases_for_helpers(
                COLLECTION_REPLACEMENT_BUNDLE,
                _REPLACEMENT_FRONTIER_HELPERS,
            )
        ),
    )


def test_literal_collection_direct_test_buckets_cover_selected_frontier() -> None:
    assert_direct_test_case_id_buckets_cover_selected_frontier(
        {
            "module-split": frozenset(
                case.case_id
                for case in PUBLISHED_COLLECTION_MODULE_CASES
                if case.helper == "split"
            ),
            "pattern-split": frozenset(
                case.case_id
                for case in PUBLISHED_COLLECTION_PATTERN_CASES
                if case.helper == "split"
            ),
            "module-findall": frozenset(
                case.case_id
                for case in PUBLISHED_COLLECTION_MODULE_CASES
                if case.helper == "findall"
            ),
            "pattern-findall": frozenset(
                case.case_id
                for case in PUBLISHED_COLLECTION_PATTERN_CASES
                if case.helper == "findall"
            ),
            "module-finditer": frozenset(
                case.case_id
                for case in PUBLISHED_COLLECTION_MODULE_CASES
                if case.helper == "finditer"
            ),
            "pattern-finditer": frozenset(
                case.case_id
                for case in PUBLISHED_COLLECTION_PATTERN_CASES
                if case.helper == "finditer"
            ),
        },
        selected_case_ids=tuple(
            case.case_id for case in PUBLISHED_COLLECTION_FIXTURE_CASES
        ),
        coverage_label="literal collection direct-test case-id buckets",
    )


@pytest.mark.parametrize(
    "case",
    PUBLISHED_BOUNDED_WILDCARD_COMPILE_CASES,
    ids=lambda case: case.case_id,
)
def test_bounded_wildcard_compile_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    compile_with_cpython_parity(
        backend_name,
        backend,
        case_pattern(case),
        case.flags or 0,
    )


@pytest.mark.parametrize(
    "case",
    BOUNDED_WILDCARD_MODULE_MATCH_CASES,
    ids=lambda case: case.case_id,
)
def test_bounded_wildcard_module_match_helpers_match_cpython(
    regex_backend: tuple[str, object],
    case: BoundedWildcardModuleCase,
) -> None:
    backend_name, observed, expected = _evaluate_bounded_wildcard_module_case(
        regex_backend,
        case,
    )

    _assert_literal_match_helper_result_matches_cpython(
        backend_name=backend_name,
        context="compiled-pattern module" if case.compiled else "module",
        helper=case.helper,
        pattern=case.pattern,
        string=case.string,
        observed=observed,
        expected=expected,
    )


@pytest.mark.parametrize(
    "case",
    BOUNDED_WILDCARD_MODULE_COLLECTION_CASES,
    ids=lambda case: case.case_id,
)
def test_bounded_wildcard_module_collection_helpers_match_cpython(
    regex_backend: tuple[str, object],
    case: BoundedWildcardModuleCase,
) -> None:
    backend_name, observed, expected = _evaluate_bounded_wildcard_module_case(
        regex_backend,
        case,
    )
    context = "compiled-pattern module" if case.compiled else "module"

    if case.helper == "finditer":
        try:
            assert_finditer_parity(backend_name, observed, expected)
        except AssertionError as exc:
            raise AssertionError(
                f"{backend_name} {context} {case.helper} mismatch for "
                f"pattern={case.pattern!r}, string={case.string!r}"
            ) from exc
        return

    assert_value_parity(observed, expected)


def test_rebar_bounded_wildcard_unsupported_paths_keep_placeholder_messages() -> None:
    with pytest.raises(
        NotImplementedError,
        match=r"rebar\.compile\(\) is a scaffold placeholder",
    ):
        rebar.search("[ab]c", "abc")

    unsupported = rebar.compile("abc", rebar.IGNORECASE)
    with pytest.raises(
        NotImplementedError,
        match=r"rebar\.Pattern\.findall\(\) is a scaffold placeholder",
    ):
        unsupported.findall("ABC")


@pytest.mark.parametrize(
    "case",
    PUBLISHED_BOUNDED_WILDCARD_PATTERN_MATCH_CASES,
    ids=lambda case: case.case_id,
)
def test_bounded_wildcard_pattern_match_helpers_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case_pattern(case),
        case.flags or 0,
    )

    observed = getattr(observed_pattern, case.helper)(*case.args)
    expected = getattr(expected_pattern, case.helper)(*case.args)

    assert_match_result_parity(backend_name, observed, expected)
    if expected is not None:
        assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize(
    "case",
    PUBLISHED_BOUNDED_WILDCARD_PATTERN_COLLECTION_CASES,
    ids=lambda case: case.case_id,
)
def test_bounded_wildcard_pattern_collection_helpers_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case_pattern(case),
        case.flags or 0,
    )

    observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
    expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    if case.helper == "finditer":
        assert_finditer_parity(backend_name, observed, expected)
        return

    assert_value_parity(observed, expected)


def test_recording_native_boundary_dispatch_helpers_record_calls_and_results() -> None:
    boundary = _ModuleWorkflowFakeNativeBoundary(
        str_compile_flags=0,
        bytes_compile_flags=0,
    )

    assert boundary.boundary_compile("abc", 4) == ("compiled", 4, True)
    assert boundary.boundary_literal_match("abc", 4, "search", "zabc", 1, None) == (
        "matched",
        1,
        3,
        (1, 4),
    )
    assert boundary.boundary_literal_split(b"abc", 2, b"zabc", 1) == (
        "supported",
        [b"native-bytes-split"],
    )
    assert boundary.boundary_literal_findall("abc", 0, "zabc", 0, 4) == (
        "supported",
        ["native-findall"],
    )
    assert boundary.boundary_literal_finditer(b"abc", 0, b"zabc", 2, None) == (
        "supported",
        1,
        6,
        [(2, 5)],
    )
    assert boundary.boundary_literal_subn("abc", 0, "x", "zabc", 3) == (
        "supported",
        "native-subn",
        9,
    )
    assert boundary.boundary_escape(b"a-b") == b"native:a-b"

    assert boundary.calls == [
        ("compile", "abc", 4),
        ("match", "abc", 4, "search", "zabc", 1, None),
        ("split", b"abc", 2, b"zabc", 1),
        ("findall", "abc", 0, "zabc", 0, 4),
        ("finditer", b"abc", 0, b"zabc", 2, None),
        ("subn", "abc", 0, "x", "zabc", 3),
        ("escape", b"a-b"),
    ]


def test_recording_native_boundary_placeholder_helpers_follow_selected_message_source(
) -> None:
    boundary = RecordingNativeBoundary()

    with pytest.raises(NotImplementedError) as helper_raised:
        boundary.scaffold_raise("search")
    with pytest.raises(NotImplementedError) as pattern_raised:
        boundary.scaffold_pattern_raise("finditer")

    assert helper_raised.value.args == (rebar._placeholder_message("search"),)
    assert pattern_raised.value.args == (
        rebar._pattern_placeholder_message("finditer"),
    )

    native_boundary = RecordingNativeBoundary(native_placeholder_messages=True)
    with pytest.raises(NotImplementedError, match="native helper placeholder search"):
        native_boundary.scaffold_raise("search")
    with pytest.raises(NotImplementedError, match="native pattern placeholder finditer"):
        native_boundary.scaffold_pattern_raise("finditer")

    native_boundary.scaffold_purge()
    assert native_boundary.calls == [("purge",)]


def test_recording_native_boundary_missing_handlers_raise_clear_assertions() -> None:
    boundary = RecordingNativeBoundary()

    with pytest.raises(AssertionError, match="unexpected compile call"):
        boundary.boundary_compile("abc", 0)

    assert boundary.calls == [("compile", "abc", 0)]


def test_fake_native_boundary_handles_bounded_wildcard_wrappers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_native = _BoundedWildcardFakeNativeBoundary()
    monkeypatch.setattr(rebar, "_native", fake_native)

    rebar.purge()

    search_match = rebar.search("a.c", "ABC", rebar.IGNORECASE)

    assert search_match is not None
    assert type(search_match) is rebar.Match
    assert search_match.group(0) == "ABC"
    assert search_match.span() == (0, 3)
    assert rebar.findall("a.c", "abc") == ["abc"]

    assert fake_native.calls == [
        ("purge",),
        ("compile", "a.c", int(rebar.IGNORECASE)),
        ("match", "a.c", 34, "search", "ABC", 0, None),
        ("compile", "a.c", 0),
        ("findall", "a.c", 34, "abc", 0, None),
    ]


def test_compile_match_and_escape_use_native_boundary_hooks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_native = _ModuleWorkflowFakeNativeBoundary(native_placeholder_messages=True)

    rebar.purge()
    try:
        with monkeypatch.context() as native_patch:
            native_patch.setattr(rebar, "_native", fake_native)
            rebar.purge()

            compiled = rebar.compile("abc", rebar.IGNORECASE)
            assert compiled.flags == 4098

            match = compiled.search("zabczz")
            assert type(match) is rebar.Match
            assert match.span() == (1, 4)
            assert match.pos == 1
            assert match.endpos == 5
            assert match.group(0) == "abc"

            assert rebar.escape("a-b") == "native:a-b"
            assert rebar.escape(b"a-b") == b"native:a-b"

            assert fake_native.calls == [
                ("purge",),
                ("compile", "abc", int(rebar.IGNORECASE)),
                ("match", "abc", 4098, "search", "zabczz", 0, None),
                ("escape", "a-b"),
                ("escape", "a-b"),
            ]
    finally:
        rebar.purge()


def test_compile_surfaces_native_re_error(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_native = _ModuleWorkflowFakeNativeBoundary(native_placeholder_messages=True)

    rebar.purge()
    try:
        with monkeypatch.context() as native_patch:
            native_patch.setattr(rebar, "_native", fake_native)
            with pytest.raises(rebar.error) as raised:
                rebar.compile("boom")

            assert type(raised.value) is re.error
            assert str(raised.value) == "native compile failure at position 2"
            assert fake_native.calls == [("compile", "boom", 0)]
    finally:
        rebar.purge()


def test_pattern_placeholder_comes_from_native_boundary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_native = _ModuleWorkflowFakeNativeBoundary(native_placeholder_messages=True)

    rebar.purge()
    try:
        with monkeypatch.context() as native_patch:
            native_patch.setattr(rebar, "_native", fake_native)
            compiled = rebar.compile("unsupported")
            with pytest.raises(NotImplementedError) as raised:
                compiled.search("unsupported")

            assert str(raised.value) == "native pattern placeholder search"
            assert fake_native.calls == [
                ("compile", "unsupported", 0),
                ("match", "unsupported", 4098, "search", "unsupported", 0, None),
            ]
    finally:
        rebar.purge()


def test_collection_and_replacement_helpers_use_native_boundary_hooks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_native = _ModuleWorkflowFakeNativeBoundary(
        str_compile_flags=8192,
        bytes_compile_flags=4096,
    )

    rebar.purge()
    try:
        with monkeypatch.context() as native_patch:
            native_patch.setattr(rebar, "_native", fake_native)
            rebar.purge()

            assert rebar.split("abc", "zzabczz", maxsplit=1) == ["native-split"]

            pattern = rebar.compile("abc")
            assert pattern.flags == 8192
            assert pattern.findall("zzabczz", 2, 5) == ["native-findall"]

            iterator = rebar.finditer("abc", "zzabczz")
            matches = list(iterator)
            assert [match.group(0) for match in matches] == ["abc"]
            assert [match.span() for match in matches] == [(2, 5)]
            assert [match.pos for match in matches] == [1]
            assert [match.endpos for match in matches] == [6]

            assert pattern.sub("x", "abcabc") == "native-subn"
            assert rebar.subn("abc", "x", "abcabc", count=1) == ("native-subn", 9)

            bytes_pattern = rebar.compile(b"abc")
            assert bytes_pattern.split(b"zzabczz") == [b"native-bytes-split"]
            assert rebar.subn(b"abc", b"x", b"abcabc") == (b"native-bytes-subn", 7)

            assert fake_native.calls == [
                ("purge",),
                ("compile", "abc", 0),
                ("split", "abc", 8192, "zzabczz", 1),
                ("compile", "abc", 0),
                ("findall", "abc", 8192, "zzabczz", 2, 5),
                ("compile", "abc", 0),
                ("finditer", "abc", 8192, "zzabczz", 0, None),
                ("subn", "abc", 8192, "x", "abcabc", 0),
                ("compile", "abc", 0),
                ("subn", "abc", 8192, "x", "abcabc", 1),
                ("compile", b"abc", 0),
                ("split", b"abc", 4096, b"zzabczz", 0),
                ("compile", b"abc", 0),
                ("subn", b"abc", 4096, b"x", b"abcabc", 0),
            ]
    finally:
        rebar.purge()


def test_module_and_pattern_placeholders_still_surface_for_unsupported_native_results(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_native = _ModuleWorkflowFakeNativeBoundary(
        str_compile_flags=8192,
        bytes_compile_flags=4096,
    )

    rebar.purge()
    try:
        with monkeypatch.context() as native_patch:
            native_patch.setattr(rebar, "_native", fake_native)
            with pytest.raises(NotImplementedError) as module_raised:
                rebar.findall("unsupported", "unsupported")
            assert "rebar.findall() is a scaffold placeholder" in str(module_raised.value)

            pattern = rebar.compile("unsupported")
            with pytest.raises(NotImplementedError) as pattern_raised:
                list(pattern.finditer("unsupported"))
            assert "rebar.Pattern.finditer() is a scaffold placeholder" in str(
                pattern_raised.value
            )
    finally:
        rebar.purge()


@pytest.mark.parametrize(
    "case",
    _module_collection_cases_for_helper("split"),
    ids=lambda case: case.case_id,
)
def test_module_split_collection_helpers_match_cpython(
    regex_backend: tuple[str, object],
    case: CollectionModuleCase,
) -> None:
    _, backend = regex_backend

    assert_value_parity(
        _call_module_collection_helper(
            backend,
            case,
        ),
        _call_module_collection_helper(re, case),
    )


@pytest.mark.parametrize(
    "case",
    _pattern_collection_cases_for_helper("split"),
    ids=lambda case: case.case_id,
)
def test_pattern_split_collection_helpers_match_cpython(
    regex_backend: tuple[str, object],
    case: CollectionPatternCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern,
        case.flags,
    )

    assert_value_parity(
        _call_pattern_collection_helper(
            observed_pattern,
            case,
        ),
        _call_pattern_collection_helper(expected_pattern, case),
    )


@pytest.mark.parametrize(
    "case",
    _module_collection_cases_for_helper("findall"),
    ids=lambda case: case.case_id,
)
def test_module_findall_collection_helpers_match_cpython(
    regex_backend: tuple[str, object],
    case: CollectionModuleCase,
) -> None:
    _, backend = regex_backend

    assert_value_parity(
        _call_module_collection_helper(
            backend,
            case,
        ),
        _call_module_collection_helper(re, case),
    )


@pytest.mark.parametrize(
    "case",
    _pattern_collection_cases_for_helper("findall"),
    ids=lambda case: case.case_id,
)
def test_pattern_findall_collection_helpers_match_cpython(
    regex_backend: tuple[str, object],
    case: CollectionPatternCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern,
        case.flags,
    )

    assert_value_parity(
        _call_pattern_collection_helper(
            observed_pattern,
            case,
        ),
        _call_pattern_collection_helper(expected_pattern, case),
    )


@pytest.mark.parametrize(
    "case",
    _module_collection_cases_for_helper("finditer"),
    ids=lambda case: case.case_id,
)
def test_module_finditer_collection_helpers_match_cpython(
    regex_backend: tuple[str, object],
    case: CollectionModuleCase,
) -> None:
    backend_name, backend = regex_backend

    assert_finditer_parity(
        backend_name,
        _call_module_collection_helper(backend, case),
        _call_module_collection_helper(re, case),
        check_regs=True,
    )


@pytest.mark.parametrize(
    "case",
    _pattern_collection_cases_for_helper("finditer"),
    ids=lambda case: case.case_id,
)
def test_pattern_finditer_collection_helpers_match_cpython(
    regex_backend: tuple[str, object],
    case: CollectionPatternCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern,
        case.flags,
    )

    assert_finditer_parity(
        backend_name,
        _call_pattern_collection_helper(observed_pattern, case),
        _call_pattern_collection_helper(expected_pattern, case),
        check_regs=True,
    )


@pytest.mark.parametrize(
    "text_model",
    (
        pytest.param("str", id="str"),
        pytest.param("bytes", id="bytes"),
    ),
)
def test_literal_collection_matrix_split_matches_cpython(
    regex_backend: tuple[str, object],
    text_model: str,
) -> None:
    backend_name, backend = regex_backend
    patterns, strings = _literal_collection_matrix_payloads(text_model)

    for pattern in patterns:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            pattern,
        )
        for string in strings:
            for maxsplit in _LITERAL_COLLECTION_SPLIT_COUNTS:
                observed_module = backend.split(pattern, string, maxsplit)
                expected_module = re.split(pattern, string, maxsplit)
                assert observed_module == expected_module, (
                    f"{backend_name} module split mismatch for pattern={pattern!r}, "
                    f"string={string!r}, maxsplit={maxsplit}"
                )

                observed_bound = observed_pattern.split(string, maxsplit)
                expected_bound = expected_pattern.split(string, maxsplit)
                assert observed_bound == expected_bound, (
                    f"{backend_name} pattern split mismatch for pattern={pattern!r}, "
                    f"string={string!r}, maxsplit={maxsplit}"
                )


@pytest.mark.parametrize(
    "text_model",
    (
        pytest.param("str", id="str"),
        pytest.param("bytes", id="bytes"),
    ),
)
def test_literal_collection_matrix_module_split_accepts_compiled_patterns(
    regex_backend: tuple[str, object],
    text_model: str,
) -> None:
    backend_name, backend = regex_backend
    patterns, strings = _literal_collection_matrix_payloads(text_model)

    for pattern in patterns:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            pattern,
        )
        for string in strings:
            for maxsplit in _LITERAL_COLLECTION_SPLIT_COUNTS:
                observed_module = backend.split(observed_pattern, string, maxsplit)
                expected_module = re.split(expected_pattern, string, maxsplit)
                assert observed_module == expected_module, (
                    f"{backend_name} compiled-pattern module split mismatch for "
                    f"pattern={pattern!r}, string={string!r}, maxsplit={maxsplit}"
                )


@pytest.mark.parametrize(
    "text_model",
    (
        pytest.param("str", id="str"),
        pytest.param("bytes", id="bytes"),
    ),
)
def test_literal_collection_matrix_findall_and_finditer_match_cpython(
    regex_backend: tuple[str, object],
    text_model: str,
) -> None:
    backend_name, backend = regex_backend
    patterns, strings = _literal_collection_matrix_payloads(text_model)

    for pattern in patterns:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            pattern,
        )
        for string in strings:
            observed_module_findall = backend.findall(pattern, string)
            expected_module_findall = re.findall(pattern, string)
            assert observed_module_findall == expected_module_findall, (
                f"{backend_name} module findall mismatch for pattern={pattern!r}, "
                f"string={string!r}"
            )

            try:
                assert_finditer_parity(
                    backend_name,
                    backend.finditer(pattern, string),
                    re.finditer(pattern, string),
                    check_regs=True,
                )
            except AssertionError as exc:
                raise AssertionError(
                    f"{backend_name} module finditer mismatch for pattern={pattern!r}, "
                    f"string={string!r}"
                ) from exc

            for pos, endpos in _literal_collection_window_cases(len(string)):
                observed_bound_findall = _call_pattern_helper_with_window(
                    observed_pattern,
                    "findall",
                    string,
                    pos,
                    endpos,
                )
                expected_bound_findall = _call_pattern_helper_with_window(
                    expected_pattern,
                    "findall",
                    string,
                    pos,
                    endpos,
                )
                assert observed_bound_findall == expected_bound_findall, (
                    f"{backend_name} pattern findall mismatch for pattern={pattern!r}, "
                    f"string={string!r}, pos={pos}, endpos={endpos}"
                )

                try:
                    assert_finditer_parity(
                        backend_name,
                        _call_pattern_helper_with_window(
                            observed_pattern,
                            "finditer",
                            string,
                            pos,
                            endpos,
                        ),
                        _call_pattern_helper_with_window(
                            expected_pattern,
                            "finditer",
                            string,
                            pos,
                            endpos,
                        ),
                        check_regs=True,
                    )
                except AssertionError as exc:
                    raise AssertionError(
                        f"{backend_name} pattern finditer mismatch for pattern={pattern!r}, "
                        f"string={string!r}, pos={pos}, endpos={endpos}"
                    ) from exc


@pytest.mark.parametrize(
    "text_model",
    (
        pytest.param("str", id="str"),
        pytest.param("bytes", id="bytes"),
    ),
)
def test_literal_collection_matrix_module_find_helpers_accept_compiled_patterns(
    regex_backend: tuple[str, object],
    text_model: str,
) -> None:
    backend_name, backend = regex_backend
    patterns, strings = _literal_collection_matrix_payloads(text_model)

    for pattern in patterns:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            pattern,
        )
        for string in strings:
            observed_module_findall = backend.findall(observed_pattern, string)
            expected_module_findall = re.findall(expected_pattern, string)
            assert observed_module_findall == expected_module_findall, (
                f"{backend_name} compiled-pattern module findall mismatch for "
                f"pattern={pattern!r}, string={string!r}"
            )

            try:
                assert_finditer_parity(
                    backend_name,
                    backend.finditer(observed_pattern, string),
                    re.finditer(expected_pattern, string),
                    check_regs=True,
                )
            except AssertionError as exc:
                raise AssertionError(
                    f"{backend_name} compiled-pattern module finditer mismatch for "
                    f"pattern={pattern!r}, string={string!r}"
                ) from exc


@pytest.mark.parametrize(
    "text_model",
    (
        pytest.param("str", id="str"),
        pytest.param("bytes", id="bytes"),
    ),
)
def test_literal_match_matrix_module_helpers_match_cpython(
    regex_backend: tuple[str, object],
    text_model: str,
) -> None:
    backend_name, backend = regex_backend
    patterns, strings = _literal_collection_matrix_payloads(text_model)

    for pattern in patterns:
        for string in strings:
            for helper in _LITERAL_MATCH_HELPERS:
                _assert_literal_match_helper_result_matches_cpython(
                    backend_name=backend_name,
                    context="module",
                    helper=helper,
                    pattern=pattern,
                    string=string,
                    observed=getattr(backend, helper)(pattern, string),
                    expected=getattr(re, helper)(pattern, string),
                )


@pytest.mark.parametrize(
    "text_model",
    (
        pytest.param("str", id="str"),
        pytest.param("bytes", id="bytes"),
    ),
)
def test_literal_match_matrix_module_helpers_accept_compiled_patterns(
    regex_backend: tuple[str, object],
    text_model: str,
) -> None:
    backend_name, backend = regex_backend
    patterns, strings = _literal_collection_matrix_payloads(text_model)

    for pattern in patterns:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            pattern,
        )
        for string in strings:
            for helper in _LITERAL_MATCH_HELPERS:
                _assert_literal_match_helper_result_matches_cpython(
                    backend_name=backend_name,
                    context="compiled-pattern module",
                    helper=helper,
                    pattern=pattern,
                    string=string,
                    observed=getattr(backend, helper)(observed_pattern, string),
                    expected=getattr(re, helper)(expected_pattern, string),
                )


@pytest.mark.parametrize(
    "text_model",
    (
        pytest.param("str", id="str"),
        pytest.param("bytes", id="bytes"),
    ),
)
def test_literal_match_matrix_pattern_helpers_match_cpython_with_windows(
    regex_backend: tuple[str, object],
    text_model: str,
) -> None:
    backend_name, backend = regex_backend
    patterns, strings = _literal_collection_matrix_payloads(text_model)

    for pattern in patterns:
        observed_pattern, expected_pattern = compile_with_cpython_parity(
            backend_name,
            backend,
            pattern,
        )
        for string in strings:
            for pos, endpos in _literal_collection_window_cases(len(string)):
                for helper in _LITERAL_MATCH_HELPERS:
                    _assert_literal_match_helper_result_matches_cpython(
                        backend_name=backend_name,
                        context="pattern",
                        helper=helper,
                        pattern=pattern,
                        string=string,
                        observed=_call_pattern_helper_with_window(
                            observed_pattern,
                            helper,
                            string,
                            pos,
                            endpos,
                        ),
                        expected=_call_pattern_helper_with_window(
                            expected_pattern,
                            helper,
                            string,
                            pos,
                            endpos,
                        ),
                        pos=pos,
                        endpos=endpos,
                    )


@pytest.mark.parametrize(
    "case",
    COLLECTION_TYPE_ERROR_CASES,
    ids=lambda case: case.case_id,
)
def test_collection_helper_type_errors_match_cpython(
    regex_backend: tuple[str, object],
    case: CollectionTypeErrorCase,
) -> None:
    _, backend = regex_backend

    with pytest.raises(TypeError) as expected_error:
        _invoke_collection_helper(re, case)

    with pytest.raises(type(expected_error.value)) as observed_error:
        _invoke_collection_helper(backend, case)

    assert str(observed_error.value) == str(expected_error.value)


@pytest.mark.parametrize(
    "case",
    BOUND_PATTERN_TYPE_ERROR_CASES,
    ids=lambda case: case.case_id,
)
def test_bound_pattern_helper_type_errors_match_cpython(
    regex_backend: tuple[str, object],
    case: BoundPatternTypeErrorCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern,
    )

    assert_pattern_parity(backend_name, observed_pattern, expected_pattern)

    observed_error = _capture_error(
        lambda: _invoke_bound_pattern_helper(observed_pattern, case)
    )
    expected_error = _capture_error(
        lambda: _invoke_bound_pattern_helper(expected_pattern, case)
    )

    assert type(observed_error) is type(expected_error)
    assert observed_error.args == expected_error.args


@pytest.mark.parametrize(("operation", "message"), COLLECTION_UNSUPPORTED_CASES)
def test_collection_helpers_stay_loud_for_unsupported_cases(
    operation: object,
    message: str,
) -> None:
    with pytest.raises(NotImplementedError, match=re.escape(message)):
        operation()


def _public_surface_case_contract_token(case: FixtureCase) -> str:
    return case.case_id


@pytest.mark.parametrize(
    "bundle",
    PUBLIC_SURFACE_BUNDLES,
    ids=lambda bundle: bundle.expected_manifest_id,
)
def test_public_surface_parity_suite_stays_aligned_with_published_fixtures(
    bundle: FixtureBundle,
) -> None:
    assert_fixture_bundle_contract(
        bundle,
        pattern_extractor=_public_surface_case_contract_token,
    )


def test_public_surface_parity_suite_tracks_published_case_frontier() -> None:
    for bundle in PUBLIC_SURFACE_BUNDLES:
        assert_fixture_bundle_tracks_published_case_frontier(
            bundle,
            selected_case_ids=tuple(case.case_id for case in bundle.cases),
        )


def test_public_surface_direct_test_buckets_cover_selected_frontier() -> None:
    assert_direct_test_case_id_buckets_cover_selected_frontier(
        {
            "public-helper-presence": frozenset(
                case.case_id for case in PUBLIC_HELPER_CASES
            ),
            "public-module-call": frozenset(
                case.case_id for case in PUBLIC_MODULE_CALL_CASES
            ),
            "exported-symbol-metadata": frozenset(
                case.case_id for case in EXPORTED_METADATA_CASES
            ),
            "exported-symbol-value": frozenset(
                case.case_id for case in EXPORTED_VALUE_CASES
            ),
            "exported-constructor-guard": frozenset(
                case.case_id for case in EXPORTED_CONSTRUCTOR_GUARD_CASES
            ),
            "pattern-object-metadata": frozenset(
                case.case_id for case in PATTERN_METADATA_CASES
            ),
            "pattern-object-call": frozenset(
                case.case_id for case in PATTERN_CALL_CASES
            ),
        },
        selected_case_ids=tuple(
            case.case_id
            for bundle in PUBLIC_SURFACE_BUNDLES
            for case in bundle.cases
        ),
        coverage_label="public surface direct-test case-id buckets",
    )


@pytest.mark.parametrize("case", PUBLIC_HELPER_CASES, ids=lambda case: case.case_id)
def test_public_helper_presence_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    _, backend = regex_backend
    assert case.helper is not None

    observed = getattr(backend, case.helper, None)
    expected = getattr(re, case.helper, None)

    assert observed is not None
    assert expected is not None
    assert callable(observed) == callable(expected)
    assert case.helper in backend.__all__
    assert case.helper in re.__all__


@pytest.mark.parametrize("helper_name", ADDITIONAL_PUBLIC_HELPER_NAMES)
def test_additional_public_helpers_match_cpython_surface(helper_name: str) -> None:
    observed = getattr(rebar, helper_name, None)
    expected = getattr(re, helper_name, None)

    assert observed is not None
    assert expected is not None
    assert callable(observed) == callable(expected)
    assert helper_name in rebar.__all__
    assert helper_name in re.__all__


@pytest.mark.parametrize("case", PUBLIC_MODULE_CALL_CASES, ids=lambda case: case.case_id)
def test_public_module_calls_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    if case.helper == "compile":
        pattern = case.args[0]
        assert isinstance(pattern, (str, bytes))
        compile_with_cpython_parity(backend_name, backend, pattern)
        return

    if case.helper == "purge":
        assert getattr(backend, case.helper)(*case.args, **case.kwargs) is None
        assert re.purge() is None
        return

    if case.helper == "escape":
        observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
        expected = getattr(re, case.helper)(*case.args, **case.kwargs)

        assert type(observed) is type(expected)
        assert observed == expected
        return

    observed = getattr(backend, case.helper)(*case.args, **case.kwargs)
    expected = getattr(re, case.helper)(*case.args, **case.kwargs)

    assert observed is not None
    assert expected is not None
    assert_match_result_parity(backend_name, observed, expected, check_regs=True)
    assert_match_convenience_api_parity(observed, expected)


@pytest.mark.parametrize("case", EXPORTED_METADATA_CASES, ids=lambda case: case.case_id)
def test_exported_symbol_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    _, backend = regex_backend
    assert case.helper is not None

    observed = getattr(backend, case.helper, None)
    expected = getattr(re, case.helper, None)

    assert normalize_exported_symbol_metadata(observed) == (
        normalize_exported_symbol_metadata(expected)
    )
    if case.helper == "error":
        assert observed is expected is re.error


@pytest.mark.parametrize("case", EXPORTED_VALUE_CASES, ids=lambda case: case.case_id)
def test_exported_symbol_values_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    _, backend = regex_backend
    assert case.helper is not None

    observed = getattr(backend, case.helper, None)
    expected = getattr(re, case.helper, None)

    assert normalize_exported_symbol_value(observed) == normalize_exported_symbol_value(
        expected
    )
    assert int(observed) == int(expected)
    assert type(observed).__name__ == type(expected).__name__


@pytest.mark.parametrize(
    "case",
    EXPORTED_CONSTRUCTOR_GUARD_CASES,
    ids=lambda case: case.case_id,
)
def test_exported_type_constructor_guards_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    _, backend = regex_backend
    assert case.helper is not None

    observed_error = _capture_error(
        lambda: getattr(backend, case.helper)(*case.args, **case.kwargs)
    )
    expected_error = _capture_error(
        lambda: getattr(re, case.helper)(*case.args, **case.kwargs)
    )

    assert type(observed_error) is type(expected_error)
    assert observed_error.args == expected_error.args


@pytest.mark.parametrize("case", PATTERN_METADATA_CASES, ids=lambda case: case.case_id)
def test_pattern_object_metadata_matches_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case_pattern(case),
        case.flags or 0,
    )

    assert normalize_pattern_object_metadata(observed_pattern) == (
        normalize_pattern_object_metadata(expected_pattern)
    )


@pytest.mark.parametrize("case", PATTERN_CALL_CASES, ids=lambda case: case.case_id)
def test_pattern_object_calls_match_cpython(
    regex_backend: tuple[str, object],
    case: FixtureCase,
) -> None:
    backend_name, backend = regex_backend
    assert case.helper is not None

    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case_pattern(case),
        case.flags or 0,
    )
    observed = getattr(observed_pattern, case.helper)(*case.args, **case.kwargs)
    expected = getattr(expected_pattern, case.helper)(*case.args, **case.kwargs)

    assert observed is not None
    assert expected is not None
    assert_match_result_parity(backend_name, observed, expected, check_regs=True)
    assert_match_convenience_api_parity(observed, expected)


def test_public_surface_exports_cover_cpython_contract() -> None:
    assert set(re.__all__).issubset(set(rebar.__all__))


def test_public_surface_exported_metadata_matches_source_package_contract() -> None:
    assert rebar.RegexFlag is rebar.ASCII.__class__
    assert rebar.error is re.error
    assert isinstance(rebar.Pattern, type)
    assert isinstance(rebar.Match, type)
    assert rebar.RegexFlag.__module__ == "re"
    assert rebar.Pattern.__module__ == "re"
    assert rebar.Match.__module__ == "re"


def test_public_surface_primary_flag_exports_match_cpython_values_and_aliases() -> None:
    for name in PRIMARY_FLAG_EXPORTS:
        assert hasattr(rebar, name)
        assert int(getattr(rebar, name)) == int(getattr(re, name))

    for short_name, long_name in FLAG_ALIAS_PAIRS:
        assert getattr(rebar, short_name) is getattr(rebar, long_name)


def test_public_surface_regexflag_members_match_cpython() -> None:
    assert {member.name: int(member) for member in rebar.RegexFlag} == {
        member.name: int(member) for member in re.RegexFlag
    }


@pytest.mark.parametrize(
    ("constructor_name", "expected_message"),
    NON_INSTANTIABLE_EXPORTS,
)
def test_public_surface_exported_type_constructors_stay_non_instantiable(
    constructor_name: str,
    expected_message: str,
) -> None:
    with pytest.raises(TypeError, match=re.escape(expected_message)):
        getattr(rebar, constructor_name)()


def test_public_surface_template_placeholder_stays_loud() -> None:
    with pytest.raises(NotImplementedError) as raised:
        rebar.template("abc")

    assert "rebar.template() is a scaffold placeholder" in str(raised.value)
