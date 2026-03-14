from __future__ import annotations

from dataclasses import dataclass
import pathlib
import re
import sys

import pytest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))


import rebar


BACKENDS = (
    pytest.param("stdlib", re, id="stdlib"),
    pytest.param("rebar", rebar, id="rebar"),
)


@dataclass(frozen=True)
class LiteralCase:
    id: str
    pattern: str | bytes
    string: str | bytes
    maxsplit: int = 0


@dataclass(frozen=True)
class BoundedCollectionCase:
    id: str
    pattern: str | bytes
    string: str | bytes
    pos: int
    endpos: int


@dataclass(frozen=True)
class TypeErrorCase:
    id: str
    helper: str
    pattern: str | bytes
    string: str | bytes
    compiled: bool = False


MODULE_SPLIT_CASES = (
    LiteralCase("module-split-str-no-match", "abc", "zzz"),
    LiteralCase("module-split-str-repeated-leading-trailing", "abc", "abczzabc"),
    LiteralCase("module-split-str-maxsplit-one", "abc", "abcabc", 1),
    LiteralCase("module-split-str-negative-maxsplit", "abc", "abcabc", -1),
    LiteralCase("module-split-bytes-maxsplit-one", b"abc", b"zzabczzabc", 1),
)

PATTERN_SPLIT_CASES = (
    LiteralCase("pattern-split-str-no-match", "abc", "zzz"),
    LiteralCase("pattern-split-str-repeated", "abc", "abcabc"),
    LiteralCase("pattern-split-str-maxsplit-one", "abc", "abcabc", 1),
    LiteralCase("pattern-split-str-negative-maxsplit", "abc", "abcabc", -1),
    LiteralCase("pattern-split-bytes-maxsplit-one", b"abc", b"zzabczzabc", 1),
)

MODULE_FINDALL_CASES = (
    LiteralCase("module-findall-str-repeated", "abc", "abcabc"),
    LiteralCase("module-findall-str-no-match", "abc", "zzz"),
    LiteralCase("module-findall-bytes-repeated", b"abc", b"zabcabc"),
)

PATTERN_FINDALL_CASES = (
    BoundedCollectionCase("pattern-findall-str-bounded", "abc", "zabcabcz", 1, 7),
    BoundedCollectionCase("pattern-findall-str-bounded-no-match", "abc", "zzzzzzz", 1, 7),
    BoundedCollectionCase("pattern-findall-bytes-bounded", b"abc", b"zabcabcz", 1, 7),
)

MODULE_FINDITER_CASES = (
    LiteralCase("module-finditer-str-repeated", "abc", "zabcabc"),
    LiteralCase("module-finditer-str-no-match", "abc", "zzz"),
    LiteralCase("module-finditer-bytes-repeated", b"abc", b"zabcabc"),
)

PATTERN_FINDITER_CASES = (
    BoundedCollectionCase("pattern-finditer-str-bounded", "abc", "zabcabcx", 1, 7),
    BoundedCollectionCase("pattern-finditer-str-bounded-no-match", "abc", "zzzzzzzx", 1, 7),
    BoundedCollectionCase("pattern-finditer-bytes-bounded", b"abc", b"zabcabcx", 1, 7),
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


def _normalize_match(match: object) -> dict[str, object]:
    return {
        "group0": match.group(0),
        "groups": match.groups(),
        "groupdict": match.groupdict(),
        "span": match.span(),
        "pos": match.pos,
        "endpos": match.endpos,
        "lastindex": match.lastindex,
        "lastgroup": match.lastgroup,
    }


def _assert_finditer_parity(
    backend_name: str,
    observed_iter: object,
    expected_iter: object,
) -> None:
    observed_matches = list(observed_iter)
    expected_matches = list(expected_iter)

    if backend_name == "rebar":
        assert [type(match) for match in observed_matches] == [rebar.Match] * len(observed_matches)
    else:
        assert [type(match) for match in observed_matches] == [type(match) for match in expected_matches]

    assert [_normalize_match(match) for match in observed_matches] == [
        _normalize_match(match) for match in expected_matches
    ]
    assert next(observed_iter, None) is None
    assert next(expected_iter, None) is None


def _invoke_collection_helper(module: object, case: TypeErrorCase) -> object:
    target = module.compile(case.pattern) if case.compiled else module
    args = (case.string,) if case.compiled else (case.pattern, case.string)
    result = getattr(target, case.helper)(*args)
    if case.helper == "finditer":
        return list(result)
    return result


@pytest.mark.parametrize(("backend_name", "backend"), BACKENDS)
@pytest.mark.parametrize("case", MODULE_SPLIT_CASES, ids=lambda case: case.id)
def test_module_split_matches_cpython(
    backend_name: str,
    backend: object,
    case: LiteralCase,
) -> None:
    del backend_name
    observed = backend.split(case.pattern, case.string, maxsplit=case.maxsplit)
    expected = re.split(case.pattern, case.string, maxsplit=case.maxsplit)

    assert observed == expected


@pytest.mark.parametrize(("backend_name", "backend"), BACKENDS)
@pytest.mark.parametrize("case", PATTERN_SPLIT_CASES, ids=lambda case: case.id)
def test_pattern_split_matches_cpython(
    backend_name: str,
    backend: object,
    case: LiteralCase,
) -> None:
    del backend_name
    observed_pattern = backend.compile(case.pattern)
    expected_pattern = re.compile(case.pattern)

    assert observed_pattern.split(case.string, case.maxsplit) == expected_pattern.split(
        case.string,
        case.maxsplit,
    )


@pytest.mark.parametrize(("backend_name", "backend"), BACKENDS)
@pytest.mark.parametrize("case", MODULE_FINDALL_CASES, ids=lambda case: case.id)
def test_module_findall_matches_cpython(
    backend_name: str,
    backend: object,
    case: LiteralCase,
) -> None:
    del backend_name
    observed = backend.findall(case.pattern, case.string)
    expected = re.findall(case.pattern, case.string)

    assert observed == expected


@pytest.mark.parametrize(("backend_name", "backend"), BACKENDS)
@pytest.mark.parametrize("case", PATTERN_FINDALL_CASES, ids=lambda case: case.id)
def test_pattern_findall_matches_cpython(
    backend_name: str,
    backend: object,
    case: BoundedCollectionCase,
) -> None:
    del backend_name
    observed_pattern = backend.compile(case.pattern)
    expected_pattern = re.compile(case.pattern)

    assert observed_pattern.findall(case.string, case.pos, case.endpos) == expected_pattern.findall(
        case.string,
        case.pos,
        case.endpos,
    )


@pytest.mark.parametrize(("backend_name", "backend"), BACKENDS)
@pytest.mark.parametrize("case", MODULE_FINDITER_CASES, ids=lambda case: case.id)
def test_module_finditer_matches_cpython(
    backend_name: str,
    backend: object,
    case: LiteralCase,
) -> None:
    _assert_finditer_parity(
        backend_name,
        backend.finditer(case.pattern, case.string),
        re.finditer(case.pattern, case.string),
    )


@pytest.mark.parametrize(("backend_name", "backend"), BACKENDS)
@pytest.mark.parametrize("case", PATTERN_FINDITER_CASES, ids=lambda case: case.id)
def test_pattern_finditer_matches_cpython(
    backend_name: str,
    backend: object,
    case: BoundedCollectionCase,
) -> None:
    observed_pattern = backend.compile(case.pattern)
    expected_pattern = re.compile(case.pattern)

    _assert_finditer_parity(
        backend_name,
        observed_pattern.finditer(case.string, case.pos, case.endpos),
        expected_pattern.finditer(case.string, case.pos, case.endpos),
    )


@pytest.mark.parametrize(("backend_name", "backend"), BACKENDS)
@pytest.mark.parametrize("case", TYPE_ERROR_CASES, ids=lambda case: case.id)
def test_collection_helper_type_errors_match_cpython(
    backend_name: str,
    backend: object,
    case: TypeErrorCase,
) -> None:
    del backend_name
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
