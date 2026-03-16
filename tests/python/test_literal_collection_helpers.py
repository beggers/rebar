from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re

import pytest

import rebar
from rebar_harness.correctness import FixtureCase
from tests.python.fixture_parity_support import (
    assert_fixture_bundle_contract,
    assert_finditer_parity,
    case_pattern,
    compile_with_cpython_parity,
    load_fixture_bundle,
)


@dataclass(frozen=True)
class ModuleCollectionCase:
    id: str
    helper: str
    pattern: str | bytes
    string: str | bytes
    extra_args: tuple[object, ...] = ()


@dataclass(frozen=True)
class PatternCollectionCase:
    id: str
    helper: str
    pattern: str | bytes
    string: str | bytes
    extra_args: tuple[object, ...] = ()
    flags: int = 0


@dataclass(frozen=True)
class TypeErrorCase:
    id: str
    helper: str
    pattern: str | bytes
    string: str | bytes
    compiled: bool = False


def _module_case_from_fixture(case: FixtureCase) -> ModuleCollectionCase:
    assert case.operation == "module_call"
    assert case.helper is not None
    assert not case.kwargs
    assert len(case.args) >= 2

    pattern = case.args[0]
    string = case.args[1]
    extra_args = tuple(case.args[2:])

    assert isinstance(pattern, (str, bytes))
    assert isinstance(string, (str, bytes))
    return ModuleCollectionCase(
        id=case.case_id,
        helper=case.helper,
        pattern=pattern,
        string=string,
        extra_args=extra_args,
    )


def _pattern_case_from_fixture(case: FixtureCase) -> PatternCollectionCase:
    assert case.operation == "pattern_call"
    assert case.helper is not None
    assert not case.kwargs
    assert len(case.args) >= 1

    string = case.args[0]
    extra_args = tuple(case.args[1:])
    assert isinstance(string, (str, bytes))

    return PatternCollectionCase(
        id=case.case_id,
        helper=case.helper,
        pattern=case_pattern(case),
        string=string,
        extra_args=extra_args,
        flags=case.flags or 0,
    )


def _call_module_helper(regex_api: object, case: ModuleCollectionCase) -> object:
    return getattr(regex_api, case.helper)(case.pattern, case.string, *case.extra_args)


def _call_pattern_helper(pattern: object, case: PatternCollectionCase) -> object:
    return getattr(pattern, case.helper)(case.string, *case.extra_args)


def _invoke_collection_helper(regex_api: object, case: TypeErrorCase) -> object:
    target = regex_api.compile(case.pattern) if case.compiled else regex_api
    args = (case.string,) if case.compiled else (case.pattern, case.string)
    result = getattr(target, case.helper)(*args)
    if case.helper == "finditer":
        return list(result)
    return result


TARGET_FIXTURE_CASE_IDS = (
    "module-split-str-leading-trailing",
    "module-split-str-no-match",
    "pattern-split-bytes-maxsplit",
    "module-findall-bytes-repeated",
    "pattern-findall-str-no-match",
    "module-finditer-str-repeated",
    "pattern-finditer-bytes-bounded",
)
COLLECTION_FIXTURE_BUNDLE = load_fixture_bundle(
    "collection_replacement_workflows.py",
    expected_manifest_id="collection-replacement-workflows",
    selected_case_ids=TARGET_FIXTURE_CASE_IDS,
    expected_case_ids=frozenset(TARGET_FIXTURE_CASE_IDS),
    expected_patterns=frozenset({"abc", b"abc"}),
    expected_operation_helper_counts=Counter(
        {
            ("module_call", "split"): 2,
            ("pattern_call", "split"): 1,
            ("module_call", "findall"): 1,
            ("pattern_call", "findall"): 1,
            ("module_call", "finditer"): 1,
            ("pattern_call", "finditer"): 1,
        }
    ),
)
PUBLISHED_MODULE_CASES = tuple(
    _module_case_from_fixture(case)
    for case in COLLECTION_FIXTURE_BUNDLE.cases
    if case.operation == "module_call"
)
PUBLISHED_PATTERN_CASES = tuple(
    _pattern_case_from_fixture(case)
    for case in COLLECTION_FIXTURE_BUNDLE.cases
    if case.operation == "pattern_call"
)

MODULE_SPLIT_CASES = tuple(
    case for case in PUBLISHED_MODULE_CASES if case.helper == "split"
) + (
    ModuleCollectionCase("module-split-str-maxsplit-one", "split", "abc", "abcabc", (1,)),
    ModuleCollectionCase("module-split-str-negative-maxsplit", "split", "abc", "abcabc", (-1,)),
    ModuleCollectionCase(
        "module-split-bytes-maxsplit-one",
        "split",
        b"abc",
        b"zzabczzabc",
        (1,),
    ),
)
PATTERN_SPLIT_CASES = tuple(
    case for case in PUBLISHED_PATTERN_CASES if case.helper == "split"
) + (
    PatternCollectionCase("pattern-split-str-no-match", "split", "abc", "zzz"),
    PatternCollectionCase("pattern-split-str-repeated", "split", "abc", "abcabc"),
    PatternCollectionCase("pattern-split-str-maxsplit-one", "split", "abc", "abcabc", (1,)),
    PatternCollectionCase(
        "pattern-split-str-negative-maxsplit",
        "split",
        "abc",
        "abcabc",
        (-1,),
    ),
)

MODULE_FINDALL_CASES = tuple(
    case for case in PUBLISHED_MODULE_CASES if case.helper == "findall"
) + (
    ModuleCollectionCase("module-findall-str-repeated", "findall", "abc", "abcabc"),
    ModuleCollectionCase("module-findall-str-no-match", "findall", "abc", "zzz"),
)
PATTERN_FINDALL_CASES = tuple(
    case for case in PUBLISHED_PATTERN_CASES if case.helper == "findall"
) + (
    PatternCollectionCase("pattern-findall-str-bounded", "findall", "abc", "zabcabcz", (1, 7)),
    PatternCollectionCase(
        "pattern-findall-str-bounded-no-match",
        "findall",
        "abc",
        "zzzzzzz",
        (1, 7),
    ),
    PatternCollectionCase(
        "pattern-findall-bytes-bounded",
        "findall",
        b"abc",
        b"zabcabcz",
        (1, 7),
    ),
)

MODULE_FINDITER_CASES = tuple(
    case for case in PUBLISHED_MODULE_CASES if case.helper == "finditer"
) + (
    ModuleCollectionCase("module-finditer-str-no-match", "finditer", "abc", "zzz"),
    ModuleCollectionCase("module-finditer-bytes-repeated", "finditer", b"abc", b"zabcabc"),
)
PATTERN_FINDITER_CASES = tuple(
    case for case in PUBLISHED_PATTERN_CASES if case.helper == "finditer"
) + (
    PatternCollectionCase("pattern-finditer-str-bounded", "finditer", "abc", "zabcabcx", (1, 7)),
    PatternCollectionCase(
        "pattern-finditer-str-bounded-no-match",
        "finditer",
        "abc",
        "zzzzzzzx",
        (1, 7),
    ),
)

TYPE_ERROR_CASES = (
    TypeErrorCase(
        id="module-split-str-pattern-on-bytes-string",
        helper="split",
        pattern="abc",
        string=b"abc",
    ),
    TypeErrorCase(
        id="module-findall-str-pattern-on-bytes-string",
        helper="findall",
        pattern="abc",
        string=b"abc",
    ),
    TypeErrorCase(
        id="pattern-findall-bytes-pattern-on-str-string",
        helper="findall",
        pattern=b"abc",
        string="abc",
        compiled=True,
    ),
    TypeErrorCase(
        id="pattern-finditer-bytes-pattern-on-str-string",
        helper="finditer",
        pattern=b"abc",
        string="abc",
        compiled=True,
    ),
)

UNSUPPORTED_CASES = (
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


def test_literal_collection_suite_stays_aligned_with_published_fixture_rows() -> None:
    bundle = COLLECTION_FIXTURE_BUNDLE

    assert_fixture_bundle_contract(bundle, pattern_extractor=case_pattern)


@pytest.mark.parametrize("case", MODULE_SPLIT_CASES, ids=lambda case: case.id)
def test_module_split_matches_cpython(
    regex_backend: tuple[str, object],
    case: ModuleCollectionCase,
) -> None:
    _, backend = regex_backend

    assert _call_module_helper(backend, case) == _call_module_helper(re, case)


@pytest.mark.parametrize("case", PATTERN_SPLIT_CASES, ids=lambda case: case.id)
def test_pattern_split_matches_cpython(
    regex_backend: tuple[str, object],
    case: PatternCollectionCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern,
        case.flags,
    )

    assert _call_pattern_helper(observed_pattern, case) == _call_pattern_helper(
        expected_pattern,
        case,
    )


@pytest.mark.parametrize("case", MODULE_FINDALL_CASES, ids=lambda case: case.id)
def test_module_findall_matches_cpython(
    regex_backend: tuple[str, object],
    case: ModuleCollectionCase,
) -> None:
    _, backend = regex_backend

    assert _call_module_helper(backend, case) == _call_module_helper(re, case)


@pytest.mark.parametrize("case", PATTERN_FINDALL_CASES, ids=lambda case: case.id)
def test_pattern_findall_matches_cpython(
    regex_backend: tuple[str, object],
    case: PatternCollectionCase,
) -> None:
    backend_name, backend = regex_backend
    observed_pattern, expected_pattern = compile_with_cpython_parity(
        backend_name,
        backend,
        case.pattern,
        case.flags,
    )

    assert _call_pattern_helper(observed_pattern, case) == _call_pattern_helper(
        expected_pattern,
        case,
    )


@pytest.mark.parametrize("case", MODULE_FINDITER_CASES, ids=lambda case: case.id)
def test_module_finditer_matches_cpython(
    regex_backend: tuple[str, object],
    case: ModuleCollectionCase,
) -> None:
    backend_name, backend = regex_backend

    assert_finditer_parity(
        backend_name,
        _call_module_helper(backend, case),
        _call_module_helper(re, case),
        check_regs=True,
    )


@pytest.mark.parametrize("case", PATTERN_FINDITER_CASES, ids=lambda case: case.id)
def test_pattern_finditer_matches_cpython(
    regex_backend: tuple[str, object],
    case: PatternCollectionCase,
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
        _call_pattern_helper(observed_pattern, case),
        _call_pattern_helper(expected_pattern, case),
        check_regs=True,
    )


@pytest.mark.parametrize("case", TYPE_ERROR_CASES, ids=lambda case: case.id)
def test_collection_helper_type_errors_match_cpython(
    regex_backend: tuple[str, object],
    case: TypeErrorCase,
) -> None:
    _, backend = regex_backend

    with pytest.raises(TypeError) as expected_error:
        _invoke_collection_helper(re, case)

    with pytest.raises(type(expected_error.value)) as observed_error:
        _invoke_collection_helper(backend, case)

    assert str(observed_error.value) == str(expected_error.value)


@pytest.mark.parametrize(("operation", "message"), UNSUPPORTED_CASES)
def test_collection_helpers_stay_loud_for_unsupported_cases(
    operation: object,
    message: str,
) -> None:
    with pytest.raises(NotImplementedError, match=re.escape(message)):
        operation()
