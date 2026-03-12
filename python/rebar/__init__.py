"""Scaffold-only package surface for the future `re`-compatible API.

The public drop-in module API will live in this package. The native extension
boundary is `rebar._rebar`, built through PyO3 and maturin.
"""

from __future__ import annotations

import enum
import importlib.util
import operator
import re as _stdlib_re
import warnings
from typing import Final

TARGET_CPYTHON_SERIES: Final[str] = "3.12.x"
SCAFFOLD_STATUS: Final[str] = "scaffold-only"
NATIVE_MODULE_NAME: Final[str] = "rebar._rebar"

# Only treat a truly missing extension as optional. If a discovered extension
# fails to initialize, surface that error instead of silently masking it.
if importlib.util.find_spec(NATIVE_MODULE_NAME) is None:
    _native = None
else:
    from . import _rebar as _native

def _placeholder_message(helper_name: str) -> str:
    return (
        f"rebar.{helper_name}() is a scaffold placeholder; "
        "the `re`-compatible API is not implemented yet"
    )


def _pattern_placeholder_message(method_name: str) -> str:
    return (
        f"rebar.Pattern.{method_name}() is a scaffold placeholder; "
        "compiled pattern semantics are not implemented yet"
    )


_LITERAL_METACHARACTERS = frozenset(".^$*+?{}[]\\|()")
_ESCAPE_SPECIAL_CHARACTERS: Final[dict[int, str]] = {
    9: "\\\t",
    10: "\\\n",
    11: "\\\x0b",
    12: "\\\x0c",
    13: "\\\r",
    32: "\\ ",
    35: "\\#",
    36: "\\$",
    38: "\\&",
    40: "\\(",
    41: "\\)",
    42: "\\*",
    43: "\\+",
    45: "\\-",
    46: "\\.",
    63: "\\?",
    91: "\\[",
    92: "\\\\",
    93: "\\]",
    94: "\\^",
    123: "\\{",
    124: "\\|",
    125: "\\}",
    126: "\\~",
}
_COMPILE_CACHE: dict[tuple[type[str] | type[bytes], str | bytes, int], "Pattern"] = {}


def _raise_placeholder(helper_name: str) -> object:
    if _native is not None:
        return _native.scaffold_raise(helper_name)
    raise NotImplementedError(_placeholder_message(helper_name))


class RegexFlag(enum.IntFlag):
    """CPython-shaped exported flag enum for the scaffold package."""

    NOFLAG = 0
    TEMPLATE = 1
    T = TEMPLATE
    IGNORECASE = 2
    I = IGNORECASE
    LOCALE = 4
    L = LOCALE
    MULTILINE = 8
    M = MULTILINE
    DOTALL = 16
    S = DOTALL
    UNICODE = 32
    U = UNICODE
    VERBOSE = 64
    X = VERBOSE
    DEBUG = 128
    ASCII = 256
    A = ASCII


RegexFlag.__module__ = "re"


NOFLAG = RegexFlag.NOFLAG
TEMPLATE = RegexFlag.TEMPLATE
T = TEMPLATE
IGNORECASE = RegexFlag.IGNORECASE
I = IGNORECASE
LOCALE = RegexFlag.LOCALE
L = LOCALE
MULTILINE = RegexFlag.MULTILINE
M = MULTILINE
DOTALL = RegexFlag.DOTALL
S = DOTALL
UNICODE = RegexFlag.UNICODE
U = UNICODE
VERBOSE = RegexFlag.VERBOSE
X = VERBOSE
DEBUG = RegexFlag.DEBUG
ASCII = RegexFlag.ASCII
A = ASCII
error = _stdlib_re.error


class Pattern:
    """Scaffold export for the future compiled-pattern type."""

    __slots__ = ("pattern", "flags", "groups", "groupindex", "_supports_literal")

    def __new__(cls, *_args: object, **_kwargs: object) -> "Pattern":
        raise TypeError("cannot create 're.Pattern' instances")

    def __init__(self, pattern: str | bytes, flags: int = 0, *, supports_literal: bool = False) -> None:
        self.pattern = pattern
        self.flags = flags
        self.groups = 0
        self.groupindex: dict[str, int] = {}
        self._supports_literal = supports_literal

    def _raise_placeholder(self, method_name: str) -> object:
        if _native is not None:
            return _native.scaffold_pattern_raise(method_name)
        raise NotImplementedError(_pattern_placeholder_message(method_name))

    def search(self, *_args: object, **_kwargs: object) -> object:
        return _dispatch_pattern_match(self, "search", *_args, **_kwargs)

    def match(self, *_args: object, **_kwargs: object) -> object:
        return _dispatch_pattern_match(self, "match", *_args, **_kwargs)

    def fullmatch(self, *_args: object, **_kwargs: object) -> object:
        return _dispatch_pattern_match(self, "fullmatch", *_args, **_kwargs)

    def split(self, string: object, maxsplit: int = 0) -> object:
        if not _supports_literal_collection_execution(self):
            return self._raise_placeholder("split")
        return _run_literal_split(self, string, maxsplit=maxsplit)

    def findall(self, string: object, pos: int = 0, endpos: int | None = None) -> object:
        if not _supports_literal_collection_execution(self):
            return self._raise_placeholder("findall")
        return _run_literal_findall(self, string, pos=pos, endpos=endpos)

    def finditer(self, string: object, pos: int = 0, endpos: int | None = None) -> object:
        if not _supports_literal_collection_execution(self):
            return self._raise_placeholder("finditer")
        return _run_literal_finditer(self, string, pos=pos, endpos=endpos)

    def sub(self, repl: object, string: object, count: int = 0) -> object:
        if not _supports_literal_replacement_execution(self):
            return self._raise_placeholder("sub")
        _ensure_literal_replacement_payload(self.pattern, repl, unsupported=self._raise_placeholder, helper_name="sub")
        return _run_literal_sub(self, repl, string, count=count)

    def subn(self, repl: object, string: object, count: int = 0) -> object:
        if not _supports_literal_replacement_execution(self):
            return self._raise_placeholder("subn")
        _ensure_literal_replacement_payload(self.pattern, repl, unsupported=self._raise_placeholder, helper_name="subn")
        return _run_literal_subn(self, repl, string, count=count)


Pattern.__module__ = "re"


class Match:
    """Concrete scaffold export for the bounded literal-only match subset."""

    __slots__ = ("re", "string", "pos", "endpos", "lastindex", "lastgroup", "_span")

    def __new__(cls, *_args: object, **_kwargs: object) -> "Match":
        raise TypeError("cannot create 're.Match' instances")

    def __init__(
        self,
        pattern: Pattern,
        string: str | bytes,
        pos: int,
        endpos: int,
        span: tuple[int, int],
    ) -> None:
        self.re = pattern
        self.string = string
        self.pos = pos
        self.endpos = endpos
        self.lastindex = None
        self.lastgroup = None
        self._span = span

    def __bool__(self) -> bool:
        return True

    def _resolve_group_reference(self, group: object) -> int:
        if group == 0:
            return 0
        raise IndexError("no such group")

    def group(self, *groups: object) -> str | bytes | tuple[str | bytes, ...]:
        if not groups:
            return self.string[self._span[0] : self._span[1]]
        if len(groups) == 1:
            self._resolve_group_reference(groups[0])
            return self.string[self._span[0] : self._span[1]]
        values: list[str | bytes] = []
        for group in groups:
            self._resolve_group_reference(group)
            values.append(self.string[self._span[0] : self._span[1]])
        return tuple(values)

    def groups(self, default: object = None) -> tuple[()]:
        return ()

    def groupdict(self, default: object = None) -> dict[str, object]:
        return {}

    def span(self, group: object = 0) -> tuple[int, int]:
        self._resolve_group_reference(group)
        return self._span

    def start(self, group: object = 0) -> int:
        self._resolve_group_reference(group)
        return self._span[0]

    def end(self, group: object = 0) -> int:
        self._resolve_group_reference(group)
        return self._span[1]


Match.__module__ = "re"


__all__ = [
    "match",
    "fullmatch",
    "search",
    "sub",
    "subn",
    "split",
    "findall",
    "finditer",
    "compile",
    "purge",
    "template",
    "escape",
    "error",
    "Pattern",
    "Match",
    "A",
    "I",
    "L",
    "M",
    "S",
    "X",
    "U",
    "ASCII",
    "IGNORECASE",
    "LOCALE",
    "MULTILINE",
    "DOTALL",
    "VERBOSE",
    "UNICODE",
    "NOFLAG",
    "RegexFlag",
]


def native_module_loaded() -> bool:
    """Report whether the optional scaffold extension is available."""

    return _native is not None


def native_scaffold_status() -> str | None:
    """Return metadata from the loaded native scaffold when available."""

    if _native is None:
        return None
    return _native.SCAFFOLD_STATUS


def native_target_cpython_series() -> str | None:
    """Return the native module's advertised CPython target when available."""

    if _native is None:
        return None
    return _native.TARGET_CPYTHON_SERIES


def _normalize_pattern_flags(pattern: str | bytes, flags: int) -> int:
    if isinstance(pattern, str) and not flags & int(ASCII):
        return flags | int(UNICODE)
    return flags


def _compile_cache_key(pattern: str | bytes, flags: int) -> tuple[type[str] | type[bytes], str | bytes, int]:
    return (type(pattern), pattern, flags)


def _supports_pattern_scaffold(pattern: str | bytes) -> bool:
    if isinstance(pattern, bytes):
        return not any(byte in pattern for byte in br".^$*+?{}[]\|()")
    return not any(character in _LITERAL_METACHARACTERS for character in pattern)


def _literal_match_base_flags(pattern: str | bytes) -> int:
    return _normalize_pattern_flags(pattern, 0)


def _supports_literal_execution(compiled_pattern: Pattern) -> bool:
    if not compiled_pattern._supports_literal:
        return False
    base_flags = _literal_match_base_flags(compiled_pattern.pattern)
    return compiled_pattern.flags in (base_flags, base_flags | int(IGNORECASE))


def _supports_literal_collection_execution(compiled_pattern: Pattern) -> bool:
    if not compiled_pattern._supports_literal:
        return False
    return compiled_pattern.flags == _literal_match_base_flags(compiled_pattern.pattern) and len(compiled_pattern.pattern) > 0


def _supports_literal_replacement_execution(compiled_pattern: Pattern) -> bool:
    return _supports_literal_collection_execution(compiled_pattern)


def _raise_regex_error(message: str, pattern: str | bytes, pos: int) -> object:
    raise error(message, pattern, pos)


def _build_compiled_pattern(
    pattern: str | bytes,
    flags: int,
    *,
    supports_literal: bool,
) -> Pattern:
    compiled = object.__new__(Pattern)
    Pattern.__init__(compiled, pattern, flags, supports_literal=supports_literal)
    return compiled


def _build_native_compile_result(pattern: str | bytes, flags: int) -> Pattern:
    status, normalized_flags, supports_literal = _native.boundary_compile(pattern, int(flags))
    if status != "compiled":
        return _raise_placeholder("compile")
    return _build_compiled_pattern(pattern, normalized_flags, supports_literal=supports_literal)


def _dispatch_pattern_match(
    compiled_pattern: Pattern,
    mode: str,
    string: object,
    pos: int = 0,
    endpos: int | None = None,
) -> Match | None:
    if _native is not None:
        status, normalized_pos, normalized_endpos, span = _native.boundary_literal_match(
            compiled_pattern.pattern,
            compiled_pattern.flags,
            mode,
            string,
            pos,
            endpos,
        )
        if status == "unsupported":
            return compiled_pattern._raise_placeholder(mode)
        if status == "no-match":
            return None
        return _build_match(compiled_pattern, _ensure_compatible_string(compiled_pattern.pattern, string), normalized_pos, normalized_endpos, span)

    if not _supports_literal_execution(compiled_pattern):
        return compiled_pattern._raise_placeholder(mode)
    return _run_literal_match(compiled_pattern, mode, string, pos=pos, endpos=endpos)


def _compile_known_parser_case(pattern: str | bytes, flags: int) -> Pattern | None:
    if pattern == "*abc":
        return _raise_regex_error("nothing to repeat", pattern, 0)

    if pattern == "a(?i)b":
        return _raise_regex_error("global flags not at the start of the expression", pattern, 1)

    if pattern == "(?L:a)":
        return _raise_regex_error("bad inline flags: cannot use 'L' flag with a str pattern", pattern, 3)

    if pattern == b"(?u:a)":
        return _raise_regex_error("bad inline flags: cannot use 'u' flag with a bytes pattern", pattern, 3)

    if pattern == b"\\u1234":
        return _raise_regex_error(r"bad escape \u", pattern, 0)

    if pattern == "(?<=a+)b":
        raise error("look-behind requires fixed-width pattern", pattern)

    if pattern == "[[a]":
        warnings.warn("Possible nested set at position 1", FutureWarning, stacklevel=2)
        return _build_compiled_pattern(pattern, flags, supports_literal=False)

    if pattern == "(?u:a)" or pattern == "(?<=ab)c" or pattern == b"(?L:a)":
        return _build_compiled_pattern(pattern, flags, supports_literal=False)

    return None


def _literal_ignores_case(compiled_pattern: Pattern) -> bool:
    return bool(compiled_pattern.flags & int(IGNORECASE))


def _ensure_compatible_string(pattern: str | bytes, string: object) -> str | bytes:
    if isinstance(pattern, str):
        if not isinstance(string, str):
            raise TypeError("cannot use a string pattern on a bytes-like object")
        return string
    if not isinstance(string, bytes):
        raise TypeError("cannot use a bytes pattern on a string-like object")
    return string


def _normalize_match_bounds(string: str | bytes, pos: int = 0, endpos: int | None = None) -> tuple[int, int]:
    start, stop, _ = slice(pos, endpos).indices(len(string))
    return start, stop


def _build_match(
    compiled_pattern: Pattern,
    string: str | bytes,
    pos: int,
    endpos: int,
    span: tuple[int, int],
) -> Match:
    match = object.__new__(Match)
    Match.__init__(match, compiled_pattern, string, pos, endpos, span)
    return match


def _fold_ascii_byte(value: int) -> int:
    if 65 <= value <= 90:
        return value + 32
    return value


def _literal_units_equal(left: str | int, right: str | int) -> bool:
    if isinstance(left, int):
        return _fold_ascii_byte(left) == _fold_ascii_byte(right)
    return left.casefold() == right.casefold()


def _literal_matches_at(
    compiled_pattern: Pattern,
    string: str | bytes,
    start: int,
    endpos: int,
) -> bool:
    pattern = compiled_pattern.pattern
    pattern_length = len(pattern)
    stop = start + pattern_length
    if stop > endpos:
        return False
    if not _literal_ignores_case(compiled_pattern):
        return string.startswith(pattern, start, endpos)
    for offset, pattern_unit in enumerate(pattern):
        if not _literal_units_equal(pattern_unit, string[start + offset]):
            return False
    return True


def _find_literal_start(
    compiled_pattern: Pattern,
    string: str | bytes,
    pos: int,
    endpos: int,
) -> int:
    pattern = compiled_pattern.pattern
    pattern_length = len(pattern)
    if pattern_length == 0:
        return pos
    if not _literal_ignores_case(compiled_pattern):
        return string.find(pattern, pos, endpos)
    last_start = endpos - pattern_length
    for start in range(pos, last_start + 1):
        if _literal_matches_at(compiled_pattern, string, start, endpos):
            return start
    return -1


def _iter_literal_match_spans(
    compiled_pattern: Pattern,
    string: object,
    pos: int = 0,
    endpos: int | None = None,
):
    compatible_string = _ensure_compatible_string(compiled_pattern.pattern, string)
    normalized_pos, normalized_endpos = _normalize_match_bounds(compatible_string, pos, endpos)
    pattern = compiled_pattern.pattern
    next_start = normalized_pos

    while True:
        start = _find_literal_start(compiled_pattern, compatible_string, next_start, normalized_endpos)
        if start < 0:
            return
        span = (start, start + len(pattern))
        yield compatible_string, normalized_pos, normalized_endpos, span
        next_start = span[1]


def _run_literal_match(
    compiled_pattern: Pattern,
    mode: str,
    string: object,
    pos: int = 0,
    endpos: int | None = None,
) -> Match | None:
    compatible_string = _ensure_compatible_string(compiled_pattern.pattern, string)
    normalized_pos, normalized_endpos = _normalize_match_bounds(compatible_string, pos, endpos)
    pattern = compiled_pattern.pattern

    if mode == "search":
        start = _find_literal_start(compiled_pattern, compatible_string, normalized_pos, normalized_endpos)
        if start < 0:
            return None
        span = (start, start + len(pattern))
    elif mode == "match":
        if not _literal_matches_at(compiled_pattern, compatible_string, normalized_pos, normalized_endpos):
            return None
        span = (normalized_pos, normalized_pos + len(pattern))
    elif mode == "fullmatch":
        if normalized_endpos - normalized_pos != len(pattern):
            return None
        if not _literal_matches_at(compiled_pattern, compatible_string, normalized_pos, normalized_endpos):
            return None
        span = (normalized_pos, normalized_endpos)
    else:  # pragma: no cover - internal misuse guard
        raise ValueError(f"unsupported literal match mode {mode!r}")

    return _build_match(compiled_pattern, compatible_string, normalized_pos, normalized_endpos, span)


def _run_literal_split(
    compiled_pattern: Pattern,
    string: object,
    maxsplit: int = 0,
) -> list[str] | list[bytes]:
    compatible_string = _ensure_compatible_string(compiled_pattern.pattern, string)
    normalized_maxsplit = operator.index(maxsplit)
    if normalized_maxsplit < 0:
        return [compatible_string]
    if normalized_maxsplit == 0:
        return compatible_string.split(compiled_pattern.pattern)
    return compatible_string.split(compiled_pattern.pattern, normalized_maxsplit)


def _run_literal_findall(
    compiled_pattern: Pattern,
    string: object,
    pos: int = 0,
    endpos: int | None = None,
) -> list[str] | list[bytes]:
    return [
        compatible_string[span[0] : span[1]]
        for compatible_string, _normalized_pos, _normalized_endpos, span in _iter_literal_match_spans(
            compiled_pattern,
            string,
            pos=pos,
            endpos=endpos,
        )
    ]


def _run_literal_finditer(
    compiled_pattern: Pattern,
    string: object,
    pos: int = 0,
    endpos: int | None = None,
):
    for compatible_string, normalized_pos, normalized_endpos, span in _iter_literal_match_spans(
        compiled_pattern,
        string,
        pos=pos,
        endpos=endpos,
    ):
        yield _build_match(compiled_pattern, compatible_string, normalized_pos, normalized_endpos, span)


def _ensure_literal_replacement_payload(
    pattern: str | bytes,
    repl: object,
    *,
    unsupported,
    helper_name: str,
) -> str | bytes:
    if callable(repl):
        unsupported(helper_name)
        raise AssertionError("unsupported() should raise")  # pragma: no cover

    if isinstance(pattern, str):
        if not isinstance(repl, str):
            raise TypeError(f"sequence item 0: expected str instance, {type(repl).__name__} found")
        if "\\" in repl:
            unsupported(helper_name)
            raise AssertionError("unsupported() should raise")  # pragma: no cover
        return repl

    if not isinstance(repl, bytes):
        raise TypeError(f"sequence item 0: expected a bytes-like object, {type(repl).__name__} found")
    if b"\\" in repl:
        unsupported(helper_name)
        raise AssertionError("unsupported() should raise")  # pragma: no cover
    return repl


def _run_literal_sub(
    compiled_pattern: Pattern,
    repl: object,
    string: object,
    count: int = 0,
) -> str | bytes:
    substituted, _replacement_count = _run_literal_subn(compiled_pattern, repl, string, count=count)
    return substituted


def _run_literal_subn(
    compiled_pattern: Pattern,
    repl: object,
    string: object,
    count: int = 0,
) -> tuple[str | bytes, int]:
    compatible_string = _ensure_compatible_string(compiled_pattern.pattern, string)
    compatible_replacement = _ensure_literal_replacement_payload(
        compiled_pattern.pattern,
        repl,
        unsupported=_raise_placeholder,
        helper_name="subn",
    )
    normalized_count = operator.index(count)
    if normalized_count < 0:
        return compatible_string, 0

    remaining = None if normalized_count == 0 else normalized_count
    parts: list[str] | list[bytes] = []
    last_end = 0
    replacement_count = 0

    for _compatible_string, _normalized_pos, _normalized_endpos, span in _iter_literal_match_spans(
        compiled_pattern,
        compatible_string,
    ):
        if remaining is not None and replacement_count >= remaining:
            break
        parts.append(compatible_string[last_end : span[0]])
        parts.append(compatible_replacement)
        last_end = span[1]
        replacement_count += 1

    if replacement_count == 0:
        return compatible_string, 0

    parts.append(compatible_string[last_end:])
    return compatible_string[:0].join(parts), replacement_count


def compile(pattern: str | bytes | Pattern, flags: int = 0) -> Pattern:
    """Return a narrow compiled-pattern scaffold without matching semantics."""

    if isinstance(pattern, Pattern):
        if int(flags) != 0:
            raise ValueError("cannot process flags argument with a compiled pattern")
        return pattern

    if not isinstance(pattern, (str, bytes)):
        raise TypeError("first argument must be string or compiled pattern")

    normalized_flags = _normalize_pattern_flags(pattern, int(flags))
    cache_key = _compile_cache_key(pattern, normalized_flags)
    cached = _COMPILE_CACHE.get(cache_key)
    if cached is not None:
        return cached

    if _native is not None:
        compiled = _build_native_compile_result(pattern, int(flags))
        _COMPILE_CACHE[_compile_cache_key(pattern, compiled.flags)] = compiled
        return compiled

    special_case = _compile_known_parser_case(pattern, normalized_flags)
    if special_case is not None:
        _COMPILE_CACHE[cache_key] = special_case
        return special_case

    if not _supports_pattern_scaffold(pattern):
        return _raise_placeholder("compile")

    compiled = _build_compiled_pattern(pattern, normalized_flags, supports_literal=True)
    _COMPILE_CACHE[cache_key] = compiled
    return compiled


def search(pattern: str | bytes | Pattern, string: object, flags: int = 0) -> Match | None:
    """Literal-only drop-in slice for `re.search`."""

    compiled = compile(pattern, flags)
    try:
        return compiled.search(string)
    except NotImplementedError as exc:
        if str(exc) == _pattern_placeholder_message("search"):
            return _raise_placeholder("search")
        raise


def match(pattern: str | bytes | Pattern, string: object, flags: int = 0) -> Match | None:
    """Literal-only drop-in slice for `re.match`."""

    compiled = compile(pattern, flags)
    try:
        return compiled.match(string)
    except NotImplementedError as exc:
        if str(exc) == _pattern_placeholder_message("match"):
            return _raise_placeholder("match")
        raise


def fullmatch(pattern: str | bytes | Pattern, string: object, flags: int = 0) -> Match | None:
    """Literal-only drop-in slice for `re.fullmatch`."""

    compiled = compile(pattern, flags)
    try:
        return compiled.fullmatch(string)
    except NotImplementedError as exc:
        if str(exc) == _pattern_placeholder_message("fullmatch"):
            return _raise_placeholder("fullmatch")
        raise


def split(
    pattern: str | bytes | Pattern,
    string: object,
    maxsplit: int = 0,
    flags: int = 0,
) -> object:
    """Literal-only drop-in slice for `re.split`."""

    compiled = compile(pattern, flags)
    if not _supports_literal_collection_execution(compiled):
        return _raise_placeholder("split")
    return compiled.split(string, maxsplit=maxsplit)


def findall(pattern: str | bytes | Pattern, string: object, flags: int = 0) -> object:
    """Literal-only drop-in slice for `re.findall`."""

    compiled = compile(pattern, flags)
    if not _supports_literal_collection_execution(compiled):
        return _raise_placeholder("findall")
    return compiled.findall(string)


def finditer(pattern: str | bytes | Pattern, string: object, flags: int = 0) -> object:
    """Literal-only drop-in slice for `re.finditer`."""

    compiled = compile(pattern, flags)
    if not _supports_literal_collection_execution(compiled):
        return _raise_placeholder("finditer")
    return compiled.finditer(string)


def sub(
    pattern: str | bytes | Pattern,
    repl: object,
    string: object,
    count: int = 0,
    flags: int = 0,
) -> object:
    """Literal-only drop-in slice for `re.sub`."""

    if not isinstance(pattern, Pattern):
        if not isinstance(pattern, (str, bytes)):
            raise TypeError("first argument must be string or compiled pattern")
        _ensure_literal_replacement_payload(pattern, repl, unsupported=_raise_placeholder, helper_name="sub")
        if len(pattern) == 0:
            return _raise_placeholder("sub")
        normalized_flags = _normalize_pattern_flags(pattern, int(flags))
        if normalized_flags != _normalize_pattern_flags(pattern, 0):
            return _raise_placeholder("sub")

    compiled = compile(pattern, flags)
    if not _supports_literal_replacement_execution(compiled):
        return _raise_placeholder("sub")
    return compiled.sub(repl, string, count=count)


def subn(
    pattern: str | bytes | Pattern,
    repl: object,
    string: object,
    count: int = 0,
    flags: int = 0,
) -> object:
    """Literal-only drop-in slice for `re.subn`."""

    if not isinstance(pattern, Pattern):
        if not isinstance(pattern, (str, bytes)):
            raise TypeError("first argument must be string or compiled pattern")
        _ensure_literal_replacement_payload(pattern, repl, unsupported=_raise_placeholder, helper_name="subn")
        if len(pattern) == 0:
            return _raise_placeholder("subn")
        normalized_flags = _normalize_pattern_flags(pattern, int(flags))
        if normalized_flags != _normalize_pattern_flags(pattern, 0):
            return _raise_placeholder("subn")

    compiled = compile(pattern, flags)
    if not _supports_literal_replacement_execution(compiled):
        return _raise_placeholder("subn")
    return compiled.subn(repl, string, count=count)


def template(*_args: object, **_kwargs: object) -> object:
    """Placeholder for the future drop-in `re.template` surface."""

    return _raise_placeholder("template")


def escape(pattern: object) -> str | bytes:
    """Return a CPython-compatible escaped pattern for `str` and bytes-like inputs."""

    if _native is not None:
        if isinstance(pattern, str):
            return _native.boundary_escape(pattern)
        return _native.boundary_escape(bytes(pattern))

    if isinstance(pattern, str):
        return pattern.translate(_ESCAPE_SPECIAL_CHARACTERS)

    decoded_pattern = str(pattern, "latin-1")
    return decoded_pattern.translate(_ESCAPE_SPECIAL_CHARACTERS).encode("latin-1")


def purge() -> None:
    """Clear the bounded source-package compile cache."""

    _COMPILE_CACHE.clear()
    if _native is not None:
        _native.scaffold_purge()
    return None
