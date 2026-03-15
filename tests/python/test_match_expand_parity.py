from __future__ import annotations

from dataclasses import dataclass
import re

import pytest

import rebar


@dataclass(frozen=True)
class ExpandCase:
    id: str
    pattern: str | bytes
    string: str | bytes
    template: object
    helper: str = "search"
    use_compiled_pattern: bool = False


SUCCESS_CASES = (
    ExpandCase(
        id="module-search-grouped-whole-match-str",
        pattern="(abc)",
        string="zzabczz",
        template=r"<\g<0>>",
    ),
    ExpandCase(
        id="pattern-search-grouped-capture-str",
        pattern="(abc)",
        string="zzabczz",
        template=r"<\1>",
        use_compiled_pattern=True,
    ),
    ExpandCase(
        id="module-search-named-capture-str",
        pattern=r"(?P<word>abc)",
        string="zzabczz",
        template=r"<\g<word>>",
    ),
    ExpandCase(
        id="pattern-fullmatch-optional-missing-capture-str",
        pattern=r"a(b)?d",
        string="ad",
        template=r"<\g<0>:\1>",
        helper="fullmatch",
        use_compiled_pattern=True,
    ),
    ExpandCase(
        id="module-fullmatch-named-optional-missing-capture-str",
        pattern=r"a(?P<word>b)?d",
        string="ad",
        template=r"<\g<0>:\g<word>>",
        helper="fullmatch",
    ),
    ExpandCase(
        id="module-search-literal-whole-match-bytes",
        pattern=b"abc",
        string=b"zzabczz",
        template=b"<\\g<0>>",
    ),
    ExpandCase(
        id="pattern-search-literal-escaped-backslash-bytes",
        pattern=b"abc",
        string=b"zzabczz",
        template=b"<\\\\>",
        use_compiled_pattern=True,
    ),
    ExpandCase(
        id="module-search-literal-whole-match-bytearray",
        pattern=b"abc",
        string=b"zzabczz",
        template=bytearray(b"<\\g<0>>"),
    ),
    ExpandCase(
        id="pattern-search-literal-escaped-backslash-memoryview",
        pattern=b"abc",
        string=b"zzabczz",
        template=memoryview(b"<\\\\>"),
        use_compiled_pattern=True,
    ),
)


ERROR_CASES = (
    ExpandCase(
        id="module-search-invalid-numbered-reference-str",
        pattern="(abc)",
        string="abc",
        template=r"<\2>",
    ),
    ExpandCase(
        id="pattern-search-unknown-group-name-str",
        pattern=r"(?P<word>abc)",
        string="abc",
        template=r"<\g<missing>>",
        use_compiled_pattern=True,
    ),
    ExpandCase(
        id="module-search-unterminated-group-name-str",
        pattern=r"(?P<word>abc)",
        string="abc",
        template=r"<\g<word",
    ),
    ExpandCase(
        id="pattern-search-bad-escape-str",
        pattern="(abc)",
        string="abc",
        template=r"<\x>",
        use_compiled_pattern=True,
    ),
    ExpandCase(
        id="module-search-invalid-numbered-reference-bytes",
        pattern=b"abc",
        string=b"abc",
        template=b"<\\1>",
    ),
    ExpandCase(
        id="pattern-search-unknown-group-name-bytes",
        pattern=b"abc",
        string=b"abc",
        template=b"<\\g<missing>>",
        use_compiled_pattern=True,
    ),
    ExpandCase(
        id="module-search-unterminated-group-name-bytes",
        pattern=b"abc",
        string=b"abc",
        template=b"<\\g<0",
    ),
    ExpandCase(
        id="module-search-invalid-numbered-reference-bytearray",
        pattern=b"abc",
        string=b"abc",
        template=bytearray(b"<\\1>"),
    ),
    ExpandCase(
        id="pattern-search-unknown-group-name-memoryview",
        pattern=b"abc",
        string=b"abc",
        template=memoryview(b"<\\g<missing>>"),
        use_compiled_pattern=True,
    ),
    ExpandCase(
        id="module-search-str-match-bytearray-type-error",
        pattern="abc",
        string="abc",
        template=bytearray(b"<\\g<0>>"),
    ),
    ExpandCase(
        id="pattern-search-str-match-memoryview-type-error",
        pattern="abc",
        string="abc",
        template=memoryview(b"<\\g<0>>"),
        use_compiled_pattern=True,
    ),
)


def _match_for_case(backend: object, case: ExpandCase) -> object:
    if case.use_compiled_pattern:
        target = backend.compile(case.pattern)
        match = getattr(target, case.helper)(case.string)
    else:
        match = getattr(backend, case.helper)(case.pattern, case.string)

    assert match is not None
    return match


def _assert_match_type_parity(
    backend_name: str,
    observed: object,
    expected: object,
) -> None:
    if backend_name == "rebar":
        assert type(observed) is rebar.Match
    else:
        assert type(observed) is type(expected)


def _capture_expand_error(match: object, template: object) -> BaseException:
    try:
        match.expand(template)
    except BaseException as error:  # noqa: BLE001 - parity helper compares exception details.
        return error
    raise AssertionError("expected match.expand() to raise")


@pytest.mark.parametrize("case", SUCCESS_CASES, ids=lambda case: case.id)
def test_match_expand_matches_cpython(
    regex_backend: tuple[str, object],
    case: ExpandCase,
) -> None:
    backend_name, backend = regex_backend
    observed_match = _match_for_case(backend, case)
    expected_match = _match_for_case(re, case)

    _assert_match_type_parity(backend_name, observed_match, expected_match)

    observed = observed_match.expand(case.template)
    expected = expected_match.expand(case.template)

    assert type(observed) is type(expected)
    assert observed == expected


@pytest.mark.parametrize("case", ERROR_CASES, ids=lambda case: case.id)
def test_match_expand_error_paths_match_cpython(
    regex_backend: tuple[str, object],
    case: ExpandCase,
) -> None:
    backend_name, backend = regex_backend
    observed_match = _match_for_case(backend, case)
    expected_match = _match_for_case(re, case)

    _assert_match_type_parity(backend_name, observed_match, expected_match)

    expected_error = _capture_expand_error(expected_match, case.template)

    with pytest.raises(type(expected_error)) as observed_error_info:
        observed_match.expand(case.template)

    observed_error = observed_error_info.value
    assert type(observed_error) is type(expected_error)
    assert observed_error.args == expected_error.args

    if isinstance(expected_error, re.error):
        assert observed_error.pattern == expected_error.pattern
        assert observed_error.pos == expected_error.pos
