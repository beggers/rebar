from __future__ import annotations

import pytest

import rebar


EXPECTED_HELPERS = {
    "compile",
    "search",
    "match",
    "fullmatch",
    "split",
    "findall",
    "finditer",
    "sub",
    "subn",
    "template",
    "escape",
    "purge",
}

STR_CASES = [
    ("", ""),
    ("abc_123", "abc_123"),
    (".^$*+?{}[]\\|()", "\\.\\^\\$\\*\\+\\?\\{\\}\\[\\]\\\\\\|\\(\\)"),
    (' !"#%&,/:;<=>@`~', '\\ !"\\#%\\&,/:;<=>@`\\~'),
    (" \t\n\r\x0b\x0c", "\\ \\\t\\\n\\\r\\\x0b\\\x0c"),
    ("a-b", "a\\-b"),
]

BYTES_CASES = [
    (b"", b""),
    (b"abc_123", b"abc_123"),
    (br".^$*+?{}[]\|()", b"\\.\\^\\$\\*\\+\\?\\{\\}\\[\\]\\\\\\|\\(\\)"),
    (b' !"#%&,/:;<=>@`~', b'\\ !"\\#%\\&,/:;<=>@`\\~'),
    (b" \t\n\r\x0b\x0c", b"\\ \\\t\\\n\\\r\\\x0b\\\x0c"),
    (b"a-b", b"a\\-b"),
]


def _assert_placeholder_message(error: BaseException, expected_prefix: str) -> None:
    assert expected_prefix in str(error)


def _assert_match_contract(
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


def test_source_package_exports_helper_surface() -> None:
    exported = set(rebar.__all__)

    assert EXPECTED_HELPERS.issubset(exported)
    for helper_name in sorted(EXPECTED_HELPERS):
        assert callable(getattr(rebar, helper_name))


def test_source_package_template_placeholder_fails_loudly() -> None:
    with pytest.raises(NotImplementedError) as raised:
        rebar.template("abc")

    _assert_placeholder_message(
        raised.value,
        "rebar.template() is a scaffold placeholder",
    )


def test_source_package_compile_returns_pattern_scaffold_with_pinned_metadata() -> None:
    pattern = rebar.compile("abc", rebar.IGNORECASE)

    assert type(pattern) is rebar.Pattern
    assert pattern.pattern == "abc"
    assert pattern.flags == int(rebar.IGNORECASE | rebar.UNICODE)
    assert pattern.groups == 0
    assert pattern.groupindex == {}

    bytes_pattern = rebar.compile(b"abc", rebar.IGNORECASE)

    assert type(bytes_pattern) is rebar.Pattern
    assert bytes_pattern.pattern == b"abc"
    assert bytes_pattern.flags == int(rebar.IGNORECASE)
    assert bytes_pattern.groups == 0
    assert bytes_pattern.groupindex == {}


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


def test_source_package_module_literal_helpers_support_str_matches() -> None:
    search_match = rebar.search("abc", "zzabczz")
    _assert_match_contract(search_match, "abc", (2, 5), 7)

    anchored_match = rebar.match("abc", "abcdef")
    assert type(anchored_match) is rebar.Match
    assert anchored_match.group(0) == "abc"
    assert anchored_match.span() == (0, 3)

    full_match = rebar.fullmatch("abc", "abc")
    assert type(full_match) is rebar.Match
    assert full_match.group(0) == "abc"
    assert full_match.span() == (0, 3)

    assert rebar.search("abc", "zzz") is None
    assert rebar.match("abc", "zabc") is None
    assert rebar.fullmatch("abc", "abcz") is None


def test_source_package_pattern_literal_helpers_support_str_matches() -> None:
    pattern = rebar.compile("abc")

    search_match = pattern.search("zzabczz")
    _assert_match_contract(search_match, "abc", (2, 5), 7)

    anchored_match = pattern.match("abcdef")
    assert type(anchored_match) is rebar.Match
    assert anchored_match.group(0) == "abc"
    assert anchored_match.span() == (0, 3)

    full_match = pattern.fullmatch("abc")
    assert type(full_match) is rebar.Match
    assert full_match.group(0) == "abc"
    assert full_match.span() == (0, 3)

    assert pattern.search("zzz") is None
    assert pattern.match("zabc") is None
    assert pattern.fullmatch("abcz") is None


def test_source_package_pattern_literal_helpers_support_bytes_matches() -> None:
    pattern = rebar.compile(b"abc")

    search_match = pattern.search(b"zzabczz")
    _assert_match_contract(search_match, b"abc", (2, 5), 7)

    anchored_match = pattern.match(b"abcdef")
    assert type(anchored_match) is rebar.Match
    assert anchored_match.group(0) == b"abc"
    assert anchored_match.span() == (0, 3)

    full_match = pattern.fullmatch(b"abc")
    assert type(full_match) is rebar.Match
    assert full_match.group(0) == b"abc"
    assert full_match.span() == (0, 3)

    assert pattern.search(b"zzz") is None
    assert pattern.match(b"zabc") is None
    assert pattern.fullmatch(b"abcz") is None


@pytest.mark.parametrize("method_name", ["group", "span", "start", "end"])
def test_source_package_match_methods_reject_missing_groups(method_name: str) -> None:
    match = rebar.search("abc", "abc")

    with pytest.raises(IndexError) as raised:
        getattr(match, method_name)(1)

    assert str(raised.value) == "no such group"


def test_source_package_match_group_rejects_missing_named_group() -> None:
    match = rebar.search("abc", "abc")

    with pytest.raises(IndexError) as raised:
        match.group("name")

    assert str(raised.value) == "no such group"


def test_source_package_matching_rejects_string_bytes_mismatch() -> None:
    with pytest.raises(TypeError) as string_pattern_error:
        rebar.search("abc", b"abc")

    assert str(string_pattern_error.value) == (
        "cannot use a string pattern on a bytes-like object"
    )

    with pytest.raises(TypeError) as bytes_pattern_error:
        rebar.search(b"abc", "abc")

    assert str(bytes_pattern_error.value) == (
        "cannot use a bytes pattern on a string-like object"
    )


def test_source_package_module_and_pattern_helpers_stay_loud_for_unsupported_cases() -> None:
    with pytest.raises(NotImplementedError) as module_flags:
        rebar.search("abc", "abc", rebar.IGNORECASE | rebar.ASCII)

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

    pattern = rebar.compile("abc", rebar.IGNORECASE | rebar.ASCII)

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


@pytest.mark.parametrize(("raw", "expected"), STR_CASES)
def test_source_package_escape_preserves_cpython_str_cases(
    raw: str,
    expected: str,
) -> None:
    escaped = rebar.escape(raw)

    assert type(escaped) is str
    assert escaped == expected


@pytest.mark.parametrize(("raw", "expected"), BYTES_CASES)
def test_source_package_escape_preserves_cpython_bytes_cases(
    raw: bytes,
    expected: bytes,
) -> None:
    escaped = rebar.escape(raw)

    assert type(escaped) is bytes
    assert escaped == expected
