"""Scaffold-only package surface for the future `re`-compatible API.

The public drop-in module API will live in this package. The native extension
boundary is `rebar._rebar`, built through PyO3 and maturin.
"""

from __future__ import annotations

import enum
import importlib.util
import operator
import re as _stdlib_re
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
    IGNORECASE = 2
    LOCALE = 4
    MULTILINE = 8
    DOTALL = 16
    UNICODE = 32
    VERBOSE = 64
    DEBUG = 128
    ASCII = 256


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


class _NonInstantiableScaffoldType(type):
    def __call__(cls, *_args: object, **_kwargs: object) -> object:
        raise TypeError(f"cannot create '{cls.__module__}.{cls.__name__}' instances")


_PATTERN_CONSTRUCTION_TOKEN = object()
_MATCH_CONSTRUCTION_TOKEN = object()


class _PatternScaffoldType(_NonInstantiableScaffoldType):
    def __call__(cls, *_args: object, **kwargs: object) -> object:
        token = kwargs.pop("_rebar_internal_token", None)
        if token is _PATTERN_CONSTRUCTION_TOKEN:
            return super(_NonInstantiableScaffoldType, cls).__call__(*_args, **kwargs)
        raise TypeError(f"cannot create '{cls.__module__}.{cls.__name__}' instances")


class _MatchScaffoldType(_NonInstantiableScaffoldType):
    def __call__(cls, *_args: object, **kwargs: object) -> object:
        token = kwargs.pop("_rebar_internal_token", None)
        if token is _MATCH_CONSTRUCTION_TOKEN:
            return super(_NonInstantiableScaffoldType, cls).__call__(*_args, **kwargs)
        raise TypeError(f"cannot create '{cls.__module__}.{cls.__name__}' instances")


class Pattern(metaclass=_PatternScaffoldType):
    """Scaffold export for the future compiled-pattern type."""

    __slots__ = ("pattern", "flags", "groups", "groupindex")

    def __init__(self, pattern: str | bytes, flags: int = 0) -> None:
        self.pattern = pattern
        self.flags = flags
        self.groups = 0
        self.groupindex: dict[str, int] = {}

    def _raise_placeholder(self, method_name: str) -> object:
        raise NotImplementedError(_pattern_placeholder_message(method_name))

    def search(self, *_args: object, **_kwargs: object) -> object:
        if not _supports_literal_execution(self):
            return self._raise_placeholder("search")
        return _run_literal_match(self, "search", *_args, **_kwargs)

    def match(self, *_args: object, **_kwargs: object) -> object:
        if not _supports_literal_execution(self):
            return self._raise_placeholder("match")
        return _run_literal_match(self, "match", *_args, **_kwargs)

    def fullmatch(self, *_args: object, **_kwargs: object) -> object:
        if not _supports_literal_execution(self):
            return self._raise_placeholder("fullmatch")
        return _run_literal_match(self, "fullmatch", *_args, **_kwargs)

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

    def sub(self, *_args: object, **_kwargs: object) -> object:
        return self._raise_placeholder("sub")

    def subn(self, *_args: object, **_kwargs: object) -> object:
        return self._raise_placeholder("subn")


class Match(metaclass=_MatchScaffoldType):
    """Concrete scaffold export for the bounded literal-only match subset."""

    __slots__ = ("re", "string", "pos", "endpos", "lastindex", "lastgroup", "_span")

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


def _supports_literal_execution(compiled_pattern: Pattern) -> bool:
    return compiled_pattern.flags == _normalize_pattern_flags(compiled_pattern.pattern, 0)


def _supports_literal_collection_execution(compiled_pattern: Pattern) -> bool:
    return _supports_literal_execution(compiled_pattern) and len(compiled_pattern.pattern) > 0


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
    return Match(
        compiled_pattern,
        string,
        pos,
        endpos,
        span,
        _rebar_internal_token=_MATCH_CONSTRUCTION_TOKEN,
    )


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
        start = compatible_string.find(pattern, next_start, normalized_endpos)
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
        start = compatible_string.find(pattern, normalized_pos, normalized_endpos)
        if start < 0:
            return None
        span = (start, start + len(pattern))
    elif mode == "match":
        if not compatible_string.startswith(pattern, normalized_pos, normalized_endpos):
            return None
        span = (normalized_pos, normalized_pos + len(pattern))
    elif mode == "fullmatch":
        if normalized_endpos - normalized_pos != len(pattern):
            return None
        if not compatible_string.startswith(pattern, normalized_pos, normalized_endpos):
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


def compile(pattern: str | bytes | Pattern, flags: int = 0) -> Pattern:
    """Return a narrow compiled-pattern scaffold without matching semantics."""

    if isinstance(pattern, Pattern):
        if int(flags) != 0:
            raise ValueError("cannot process flags argument with a compiled pattern")
        return pattern

    if not isinstance(pattern, (str, bytes)):
        raise TypeError("first argument must be string or compiled pattern")

    if not _supports_pattern_scaffold(pattern):
        return _raise_placeholder("compile")

    normalized_flags = _normalize_pattern_flags(pattern, int(flags))
    cache_key = _compile_cache_key(pattern, normalized_flags)
    cached = _COMPILE_CACHE.get(cache_key)
    if cached is not None:
        return cached

    compiled = Pattern(
        pattern,
        normalized_flags,
        _rebar_internal_token=_PATTERN_CONSTRUCTION_TOKEN,
    )
    _COMPILE_CACHE[cache_key] = compiled
    return compiled


def search(pattern: str | bytes | Pattern, string: object, flags: int = 0) -> Match | None:
    """Literal-only drop-in slice for `re.search`."""

    compiled = compile(pattern, flags)
    if not _supports_literal_execution(compiled):
        return _raise_placeholder("search")
    return compiled.search(string)


def match(pattern: str | bytes | Pattern, string: object, flags: int = 0) -> Match | None:
    """Literal-only drop-in slice for `re.match`."""

    compiled = compile(pattern, flags)
    if not _supports_literal_execution(compiled):
        return _raise_placeholder("match")
    return compiled.match(string)


def fullmatch(pattern: str | bytes | Pattern, string: object, flags: int = 0) -> Match | None:
    """Literal-only drop-in slice for `re.fullmatch`."""

    compiled = compile(pattern, flags)
    if not _supports_literal_execution(compiled):
        return _raise_placeholder("fullmatch")
    return compiled.fullmatch(string)


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


def sub(*_args: object, **_kwargs: object) -> object:
    """Placeholder for the future drop-in `re.sub` surface."""

    return _raise_placeholder("sub")


def subn(*_args: object, **_kwargs: object) -> object:
    """Placeholder for the future drop-in `re.subn` surface."""

    return _raise_placeholder("subn")


def template(*_args: object, **_kwargs: object) -> object:
    """Placeholder for the future drop-in `re.template` surface."""

    return _raise_placeholder("template")


def escape(pattern: object) -> str | bytes:
    """Return a CPython-compatible escaped pattern for `str` and bytes-like inputs."""

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
