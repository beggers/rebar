from __future__ import annotations

from collections.abc import Callable
from collections import Counter
from dataclasses import dataclass
import re

import pytest

import rebar
from rebar_harness.correctness import FixtureCase
from tests.python.fixture_parity_support import (
    FIXTURES_DIR,
    assert_direct_test_case_id_buckets_cover_selected_frontier,
    assert_finditer_parity,
    FixtureBundleSpec,
    assert_fixture_bundle_contract,
    assert_fixture_bundle_tracks_published_case_frontier,
    assert_match_convenience_api_parity,
    assert_match_result_parity,
    assert_pattern_parity,
    case_pattern,
    compile_with_cpython_parity,
    fixture_cases_for_operation,
    load_fixture_bundles,
)


MODULE_WORKFLOW_FIXTURE_PATH = FIXTURES_DIR / "module_workflow_surface.py"
MATCH_BEHAVIOR_FIXTURE_PATH = FIXTURES_DIR / "match_behavior_smoke.py"
MODULE_WORKFLOW_EXPECTED_CASE_IDS = (
    "workflow-compile-str-literal",
    "workflow-compile-str-anchored-literal",
    "workflow-compile-str-verbose-regression",
    "workflow-compile-bytes-literal",
    "workflow-pattern-search-str",
    "workflow-pattern-match-str",
    "workflow-pattern-fullmatch-bytes",
    "workflow-cache-hit-str",
    "workflow-cache-hit-bytes",
    "workflow-purge-reset-str",
    "workflow-escape-str",
    "workflow-escape-bytes",
)
MODULE_WORKFLOW_EXPECTED_PATTERNS = frozenset(
    {
        "abc",
        "^abc$",
        "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
        b"abc",
        b"123",
        "cache-me",
        b"cache-me",
        "purge-me",
        "a-b.c",
        b"a-b.c",
    }
)
MODULE_WORKFLOW_EXPECTED_OPERATION_HELPER_COUNTS = Counter(
    {
        ("compile", None): 4,
        ("pattern_call", "search"): 1,
        ("pattern_call", "match"): 1,
        ("pattern_call", "fullmatch"): 1,
        ("cache_workflow", None): 2,
        ("purge_workflow", None): 1,
        ("module_call", "escape"): 2,
    }
)
MATCH_BEHAVIOR_EXPECTED_CASE_IDS = (
    "search-str-success-literal",
    "search-str-no-match",
    "match-str-success-literal",
    "match-str-no-match",
    "fullmatch-str-success-literal",
    "fullmatch-bytes-success-literal",
)
MATCH_BEHAVIOR_EXPECTED_PATTERNS = frozenset({"abc", "ab", "123", b"123"})
MATCH_BEHAVIOR_EXPECTED_OPERATION_HELPER_COUNTS = Counter(
    {
        ("module_call", "search"): 2,
        ("module_call", "match"): 2,
        ("module_call", "fullmatch"): 2,
    }
)
SELECTED_CASE_BUNDLE_SPECS = (
    FixtureBundleSpec(
        fixture_name="module_workflow_surface.py",
        expected_manifest_id="module-workflow-surface",
        selected_case_ids=MODULE_WORKFLOW_EXPECTED_CASE_IDS,
        expected_patterns=MODULE_WORKFLOW_EXPECTED_PATTERNS,
        expected_operation_helper_counts=MODULE_WORKFLOW_EXPECTED_OPERATION_HELPER_COUNTS,
        expected_text_models=frozenset({"bytes", "str"}),
    ),
    FixtureBundleSpec(
        fixture_name="match_behavior_smoke.py",
        expected_manifest_id="match-behavior-smoke",
        selected_case_ids=MATCH_BEHAVIOR_EXPECTED_CASE_IDS,
        expected_patterns=MATCH_BEHAVIOR_EXPECTED_PATTERNS,
        expected_operation_helper_counts=MATCH_BEHAVIOR_EXPECTED_OPERATION_HELPER_COUNTS,
        expected_text_models=frozenset({"bytes", "str"}),
    ),
)
(MODULE_WORKFLOW_BUNDLE, MATCH_BEHAVIOR_BUNDLE) = load_fixture_bundles(
    SELECTED_CASE_BUNDLE_SPECS
)

COMPILE_CASES = fixture_cases_for_operation((MODULE_WORKFLOW_BUNDLE,), "compile")
NOFLAG_COMPILE_CASES = tuple(
    case for case in COMPILE_CASES if (case.flags or 0) == 0
)
VERBOSE_COMPILE_CASE_ID = "workflow-compile-str-verbose-regression"
(VERBOSE_COMPILE_CASE,) = tuple(
    case for case in COMPILE_CASES if case.case_id == VERBOSE_COMPILE_CASE_ID
)
PATTERN_CASES = fixture_cases_for_operation((MODULE_WORKFLOW_BUNDLE,), "pattern_call")
CACHE_CASES = fixture_cases_for_operation((MODULE_WORKFLOW_BUNDLE,), "cache_workflow")
PURGE_CASES = fixture_cases_for_operation((MODULE_WORKFLOW_BUNDLE,), "purge_workflow")
ESCAPE_CASES = tuple(
    case
    for case in fixture_cases_for_operation((MODULE_WORKFLOW_BUNDLE,), "module_call")
    if case.helper == "escape"
)
MATCH_BEHAVIOR_CASES = tuple(MATCH_BEHAVIOR_BUNDLE.cases)
MATCH_BEHAVIOR_DIRECT_TEST_CASE_IDS = frozenset(
    case.case_id for case in MATCH_BEHAVIOR_CASES
)
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
MODULE_WORKFLOW_DIRECT_TEST_CASE_ID_BUCKETS = {
    "compile": frozenset(case.case_id for case in COMPILE_CASES),
    "pattern": frozenset(case.case_id for case in PATTERN_CASES),
    "cache": frozenset(case.case_id for case in CACHE_CASES),
    "purge": frozenset(case.case_id for case in PURGE_CASES),
    "escape": frozenset(case.case_id for case in ESCAPE_CASES),
}


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


@dataclass(frozen=True)
class EscapeCompatibleInputCase:
    case_id: str
    input_factory: Callable[[], object]


@dataclass(frozen=True)
class EscapeInvalidInputCase:
    case_id: str
    input_factory: Callable[[], object]


VERBOSE_COMPILE_WORKFLOW_CASES = (
    VerboseCompileWorkflowCase(
        case_id="fullmatch-digits-without-literal-spaces",
        helper="fullmatch",
        text="ENV_VAR=123",
        expected_group0="ENV_VAR=123",
        expected_key="ENV_VAR",
        expected_span=(0, 11),
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
        case_id="module-sub-count-keyword-str",
        helper="sub",
        args=("abc", "x", "abcabc"),
        kwargs={"count": 1},
        result_kind="value",
    ),
    ModuleKeywordCallCase(
        case_id="module-subn-count-keyword-bytes",
        helper="subn",
        args=(b"abc", b"x", b"abcabc"),
        kwargs={"count": 1},
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
        case_id="pattern-findall-window-keyword-str",
        helper="findall",
        pattern="abc",
        args=("zabcabcz",),
        kwargs={"pos": 1, "endpos": 7},
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
        case_id="pattern-sub-count-keyword-bytes",
        helper="sub",
        pattern=b"abc",
        args=(b"x", b"abcabc"),
        kwargs={"count": 1},
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

# CPython accepts multiple zero-valued flag spellings for compiled-pattern entry
# points; keep those variants covered in one place so helper wrappers do not
# drift into special-casing only one form.
COMPILED_PATTERN_ZERO_FLAG_MODES = (
    pytest.param("default", id="default"),
    pytest.param("noflag", id="explicit-noflag"),
    pytest.param("int-zero", id="explicit-int-zero"),
    pytest.param("bool-false", id="explicit-bool-false"),
)


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


def _compile_compiled_pattern_case(
    regex_api: object,
    pattern: str | bytes,
) -> object:
    compiled = regex_api.compile(pattern)
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


def _call_pattern_keyword_case(pattern: object, case: PatternKeywordCallCase) -> object:
    return getattr(pattern, case.helper)(*case.args, **case.kwargs)


def _capture_error(callback) -> BaseException:
    try:
        callback()
    except BaseException as error:  # noqa: BLE001 - parity helper compares exception details.
        return error
    raise AssertionError("expected call to raise")


def _assert_placeholder_message(error: BaseException, expected_prefix: str) -> None:
    assert expected_prefix in str(error)


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


def test_module_workflow_parity_suite_stays_aligned_with_published_fixture() -> None:
    assert_fixture_bundle_contract(
        MODULE_WORKFLOW_BUNDLE,
        pattern_extractor=case_pattern,
        expected_fixture_path=MODULE_WORKFLOW_FIXTURE_PATH,
        expected_ordered_case_ids=MODULE_WORKFLOW_EXPECTED_CASE_IDS,
    )


def test_module_workflow_parity_suite_tracks_published_case_frontier() -> None:
    assert_fixture_bundle_tracks_published_case_frontier(
        MODULE_WORKFLOW_BUNDLE,
        selected_case_ids=MODULE_WORKFLOW_EXPECTED_CASE_IDS,
    )


def test_module_workflow_direct_test_buckets_cover_selected_frontier() -> None:
    assert_direct_test_case_id_buckets_cover_selected_frontier(
        MODULE_WORKFLOW_DIRECT_TEST_CASE_ID_BUCKETS,
        selected_case_ids=MODULE_WORKFLOW_EXPECTED_CASE_IDS,
        coverage_label="module workflow direct-test case-id buckets",
    )


def test_match_behavior_parity_suite_stays_aligned_with_published_fixture() -> None:
    assert_fixture_bundle_contract(
        MATCH_BEHAVIOR_BUNDLE,
        pattern_extractor=case_pattern,
        expected_fixture_path=MATCH_BEHAVIOR_FIXTURE_PATH,
        expected_ordered_case_ids=MATCH_BEHAVIOR_EXPECTED_CASE_IDS,
    )


def test_match_behavior_parity_suite_tracks_published_case_frontier() -> None:
    assert_fixture_bundle_tracks_published_case_frontier(
        MATCH_BEHAVIOR_BUNDLE,
        selected_case_ids=MATCH_BEHAVIOR_EXPECTED_CASE_IDS,
    )


def test_match_behavior_direct_test_bucket_covers_selected_frontier() -> None:
    assert_direct_test_case_id_buckets_cover_selected_frontier(
        {"module-call": MATCH_BEHAVIOR_DIRECT_TEST_CASE_IDS},
        selected_case_ids=MATCH_BEHAVIOR_EXPECTED_CASE_IDS,
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


@pytest.mark.parametrize("case", MATCH_BEHAVIOR_CASES, ids=lambda case: case.case_id)
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


@pytest.mark.parametrize("case", COMPILE_CASES, ids=lambda case: case.case_id)
def test_compile_workflows_match_cpython(
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


@pytest.mark.parametrize("case", PATTERN_CASES, ids=lambda case: case.case_id)
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
    assert expected is not None
    assert_match_convenience_api_parity(observed, expected)


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
    observed_pattern = _compile_compiled_pattern_case(backend, case.pattern)
    expected_pattern = _compile_compiled_pattern_case(re, case.pattern)

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

    assert observed == expected


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
    observed_pattern = _compile_compiled_pattern_case(backend, case.pattern)
    expected_pattern = _compile_compiled_pattern_case(re, case.pattern)

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

    assert observed == expected


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

    assert observed == expected


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

    compiled, expected = _compile_verbose_regression_pattern("rebar", rebar)

    assert type(compiled) is rebar.Pattern
    assert compiled.pattern == expected.pattern == pattern
    assert compiled.flags == expected.flags == int(
        re.MULTILINE | re.VERBOSE | re.UNICODE
    )
    assert compiled.groups == expected.groups == 1
    assert compiled.groupindex == expected.groupindex == {"key": 1}
    assert rebar.compile(pattern, VERBOSE_COMPILE_CASE.flags or 0) is compiled

    with pytest.raises(NotImplementedError) as missing_verbose:
        rebar.compile(pattern, rebar.MULTILINE)

    _assert_placeholder_message(
        missing_verbose.value,
        "rebar.compile() is a scaffold placeholder",
    )

    with pytest.raises(NotImplementedError) as bytes_variant:
        rebar.compile(pattern.encode("ascii"), int(VERBOSE_COMPILE_CASE.flags or 0))

    _assert_placeholder_message(
        bytes_variant.value,
        "rebar.compile() is a scaffold placeholder",
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

    _assert_placeholder_message(
        module_flags.value,
        "rebar.search() is a scaffold placeholder",
    )

    with pytest.raises(NotImplementedError) as module_meta:
        rebar.search("[ab]c", "abc")

    _assert_placeholder_message(
        module_meta.value,
        "rebar.compile() is a scaffold placeholder",
    )

    pattern = rebar.compile("abc", rebar.IGNORECASE | rebar.VERBOSE)
    for method_name in ("search", "match", "fullmatch"):
        with pytest.raises(NotImplementedError) as bound_flags:
            getattr(pattern, method_name)("abc")

        _assert_placeholder_message(
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

    _assert_placeholder_message(
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
