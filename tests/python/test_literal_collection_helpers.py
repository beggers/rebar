from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import product
import re

import pytest

import rebar
from rebar_harness.correctness import FixtureCase
from tests.python.fixture_parity_support import (
    SelectedCaseBundleSpec,
    assert_fixture_bundle_contract,
    assert_finditer_parity,
    case_pattern,
    compile_with_cpython_parity,
    load_selected_case_fixture_bundles,
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


_LITERAL_MATRIX_ALPHABET = "ab"
_LITERAL_MATRIX_SPLIT_COUNTS = (0, 1, -1)


def _literal_collection_matrix_payloads(
    text_model: str,
) -> tuple[tuple[str | bytes, ...], tuple[str | bytes, ...]]:
    patterns = tuple(
        "".join(chars)
        for length in (1, 2)
        for chars in product(_LITERAL_MATRIX_ALPHABET, repeat=length)
    )
    strings = tuple(
        "".join(chars)
        for length in range(4)
        for chars in product(_LITERAL_MATRIX_ALPHABET, repeat=length)
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
    # Stay within the already-published non-negative bounded-window slice.
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


def _call_pattern_collection_helper_with_window(
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


TARGET_FIXTURE_CASE_IDS = (
    "module-split-str-leading-trailing",
    "module-split-str-no-match",
    "pattern-split-bytes-maxsplit",
    "module-findall-bytes-repeated",
    "pattern-findall-str-no-match",
    "module-finditer-str-repeated",
    "pattern-finditer-bytes-bounded",
)
COLLECTION_FIXTURE_BUNDLE, = load_selected_case_fixture_bundles(
    (
        SelectedCaseBundleSpec(
            "collection_replacement_workflows.py",
            expected_manifest_id="collection-replacement-workflows",
            selected_case_ids=TARGET_FIXTURE_CASE_IDS,
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
            expected_text_models=frozenset({"bytes", "str"}),
        ),
    )
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
            for maxsplit in _LITERAL_MATRIX_SPLIT_COUNTS:
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
                observed_bound_findall = _call_pattern_collection_helper_with_window(
                    observed_pattern,
                    "findall",
                    string,
                    pos,
                    endpos,
                )
                expected_bound_findall = _call_pattern_collection_helper_with_window(
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
                        _call_pattern_collection_helper_with_window(
                            observed_pattern,
                            "finditer",
                            string,
                            pos,
                            endpos,
                        ),
                        _call_pattern_collection_helper_with_window(
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
