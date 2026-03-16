from __future__ import annotations

import re as stdlib_re
from unittest import mock

import pytest

import rebar
from tests.python.fixture_parity_support import RecordingNativeBoundary


class _FakeNativeBoundary(RecordingNativeBoundary):
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
            raise stdlib_re.error("native compile failure", pattern, 2)
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


@pytest.fixture(autouse=True)
def purge_rebar_cache() -> None:
    yield
    rebar.purge()


def test_compile_match_and_escape_use_native_boundary_hooks() -> None:
    fake_native = _FakeNativeBoundary(native_placeholder_messages=True)

    with mock.patch.object(rebar, "_native", fake_native):
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
        ("escape", b"a-b"),
    ]


def test_compile_surfaces_native_re_error() -> None:
    fake_native = _FakeNativeBoundary(native_placeholder_messages=True)

    with mock.patch.object(rebar, "_native", fake_native):
        with pytest.raises(rebar.error) as raised:
            rebar.compile("boom")

    assert type(raised.value) is stdlib_re.error
    assert str(raised.value) == "native compile failure at position 2"
    assert fake_native.calls == [("compile", "boom", 0)]


def test_pattern_placeholder_comes_from_native_boundary() -> None:
    fake_native = _FakeNativeBoundary(native_placeholder_messages=True)

    with mock.patch.object(rebar, "_native", fake_native):
        compiled = rebar.compile("unsupported")
        with pytest.raises(NotImplementedError) as raised:
            compiled.search("unsupported")

    assert str(raised.value) == "native pattern placeholder search"
    assert fake_native.calls == [
        ("compile", "unsupported", 0),
        ("match", "unsupported", 4098, "search", "unsupported", 0, None),
    ]


def test_collection_and_replacement_helpers_use_native_boundary_hooks() -> None:
    fake_native = _FakeNativeBoundary(
        str_compile_flags=8192,
        bytes_compile_flags=4096,
    )

    with mock.patch.object(rebar, "_native", fake_native):
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


def test_module_and_pattern_placeholders_still_surface_for_unsupported_native_results() -> None:
    fake_native = _FakeNativeBoundary(
        str_compile_flags=8192,
        bytes_compile_flags=4096,
    )

    with mock.patch.object(rebar, "_native", fake_native):
        with pytest.raises(NotImplementedError) as module_raised:
            rebar.findall("unsupported", "unsupported")
        assert "rebar.findall() is a scaffold placeholder" in str(module_raised.value)

        pattern = rebar.compile("unsupported")
        with pytest.raises(NotImplementedError) as pattern_raised:
            list(pattern.finditer("unsupported"))
        assert "rebar.Pattern.finditer() is a scaffold placeholder" in str(
            pattern_raised.value
        )
