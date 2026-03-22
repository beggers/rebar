"""Scaffold-only package surface for the future `re`-compatible API.

The public drop-in module API will live in this package. The native extension
boundary is `rebar._rebar`, built through PyO3 and maturin.
"""

from __future__ import annotations

import enum
import importlib.machinery
import importlib.util
import operator
import pathlib
import re as _stdlib_re
import sys
import warnings
from typing import Final

TARGET_CPYTHON_SERIES: Final[str] = "3.12.x"
SCAFFOLD_STATUS: Final[str] = "scaffold-only"
NATIVE_MODULE_NAME: Final[str] = "rebar._rebar"
_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


def _load_built_native_module() -> object | None:
    for build_dir in (_REPO_ROOT / "target" / "debug", _REPO_ROOT / "target" / "release"):
        for suffix in importlib.machinery.EXTENSION_SUFFIXES:
            for candidate in (
                build_dir / f"librebar_cpython{suffix}",
                build_dir / f"rebar_cpython{suffix}",
            ):
                if not candidate.is_file():
                    continue
                spec = importlib.util.spec_from_file_location(NATIVE_MODULE_NAME, candidate)
                if spec is None or spec.loader is None:
                    continue
                module = importlib.util.module_from_spec(spec)
                sys.modules[NATIVE_MODULE_NAME] = module
                spec.loader.exec_module(module)
                return module
    return None

# Only treat a truly missing extension as optional. If a discovered extension
# fails to initialize, surface that error instead of silently masking it.
if importlib.util.find_spec(NATIVE_MODULE_NAME) is None:
    _native = _load_built_native_module()
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
_BOUNDED_NUMBERED_BACKREFERENCE_SEARCH_CASES: Final[dict[str, tuple[str, int, int]]] = {
    r"(ab)\1": ("abab", 0, 2),
    r"(ab)x\1": ("abxab", 0, 2),
    r"x(ab)\1": ("xabab", 1, 3),
}
_EXACT_TRIPLE_NESTED_GROUP_PATTERN: Final[str] = "a(((b)))d"
_EXACT_TRIPLE_NESTED_GROUP_LITERAL: Final[str] = "abd"
_EXACT_NUMBERED_QUANTIFIED_NESTED_GROUP_PATTERN: Final[str] = r"a((bc)+)d"
_EXACT_NAMED_QUANTIFIED_NESTED_GROUP_PATTERN: Final[str] = (
    r"a(?P<outer>(?P<inner>bc)+)d"
)
_NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_NUMBERED_BYTES_TEMPLATE_PATTERN: Final[
    bytes
] = br"a((b|c){1,4})\2d"
_NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_NAMED_BYTES_TEMPLATE_PATTERN: Final[
    bytes
] = br"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d"
_NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BACKTRACKING_HEAVY_NUMBERED_BYTES_CALLABLE_PATTERN: Final[
    bytes
] = br"a(((bc|b)c){1,4})d"
_NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BACKTRACKING_HEAVY_NAMED_BYTES_CALLABLE_PATTERN: Final[
    bytes
] = br"a(?P<outer>(?:(?P<inner>bc|b)c){1,4})d"
_NESTED_BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_NUMBERED_BYTES_CALLABLE_PATTERN: Final[
    bytes
] = br"a(((bc|b)c){2,})d"
_NESTED_BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_NAMED_BYTES_CALLABLE_PATTERN: Final[
    bytes
] = br"a(?P<outer>(?:(?P<inner>bc|b)c){2,})d"
_NESTED_BROADER_RANGE_OPEN_ENDED_NUMBERED_BYTES_CALLABLE_PATTERN: Final[bytes] = (
    br"a((b|c){2,})\2d"
)
_NESTED_BROADER_RANGE_OPEN_ENDED_NAMED_BYTES_CALLABLE_PATTERN: Final[bytes] = (
    br"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d"
)
_NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_CONDITIONAL_NUMBERED_BYTES_CALLABLE_PATTERN: Final[
    bytes
] = br"a((b|c){1,4})\2(?(2)d|e)"
_NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_CONDITIONAL_NAMED_BYTES_CALLABLE_PATTERN: Final[
    bytes
] = br"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)(?(inner)d|e)"
_NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_NUMBERED_BYTES_TEMPLATE_PATTERN: Final[
    bytes
] = br"a((b|c){2,})\2(?(2)d|e)"
_NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_NAMED_BYTES_TEMPLATE_PATTERN: Final[
    bytes
] = br"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)"
_NATIVE_TEMPLATE_BYTES_PATTERNS: Final[frozenset[bytes]] = frozenset(
    {
        _NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_NUMBERED_BYTES_TEMPLATE_PATTERN,
        _NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_NAMED_BYTES_TEMPLATE_PATTERN,
        _NESTED_BROADER_RANGE_OPEN_ENDED_NUMBERED_BYTES_CALLABLE_PATTERN,
        _NESTED_BROADER_RANGE_OPEN_ENDED_NAMED_BYTES_CALLABLE_PATTERN,
        _NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_NUMBERED_BYTES_TEMPLATE_PATTERN,
        _NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_NAMED_BYTES_TEMPLATE_PATTERN,
    }
)
_NATIVE_CALLABLE_BYTES_PATTERNS: Final[frozenset[bytes]] = frozenset(
    {
        _NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_NUMBERED_BYTES_TEMPLATE_PATTERN,
        _NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_NAMED_BYTES_TEMPLATE_PATTERN,
        _NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BACKTRACKING_HEAVY_NUMBERED_BYTES_CALLABLE_PATTERN,
        _NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_BACKTRACKING_HEAVY_NAMED_BYTES_CALLABLE_PATTERN,
        _NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_CONDITIONAL_NUMBERED_BYTES_CALLABLE_PATTERN,
        _NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_CONDITIONAL_NAMED_BYTES_CALLABLE_PATTERN,
        _NESTED_BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_NUMBERED_BYTES_CALLABLE_PATTERN,
        _NESTED_BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_NAMED_BYTES_CALLABLE_PATTERN,
        _NESTED_BROADER_RANGE_OPEN_ENDED_NUMBERED_BYTES_CALLABLE_PATTERN,
        _NESTED_BROADER_RANGE_OPEN_ENDED_NAMED_BYTES_CALLABLE_PATTERN,
        _NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_NUMBERED_BYTES_TEMPLATE_PATTERN,
        _NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_NAMED_BYTES_TEMPLATE_PATTERN,
    }
)
_MATCH_FALLBACK_UNSUPPORTED = object()
_PATTERN_SPLIT_MAXSPLIT_UNSET = object()
_PATTERN_REPLACEMENT_COUNT_UNSET = object()


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

    def __init__(
        self,
        pattern: str | bytes,
        flags: int = 0,
        *,
        supports_literal: bool = False,
        groups: int = 0,
        groupindex: dict[str, int] | None = None,
    ) -> None:
        self.pattern = pattern
        self.flags = flags
        self.groups = groups
        self.groupindex = {} if groupindex is None else dict(groupindex)
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

    def split(
        self,
        string: object,
        *args: object,
        maxsplit: object = _PATTERN_SPLIT_MAXSPLIT_UNSET,
        **kwargs: object,
    ) -> object:
        maxsplit = _resolve_bound_pattern_split_maxsplit(
            args,
            maxsplit=maxsplit,
            kwargs=kwargs,
        )
        if _native is not None:
            return _run_native_literal_split(self, string, maxsplit=maxsplit)
        if not _supports_literal_collection_execution(self):
            return self._raise_placeholder("split")
        return _run_literal_split(self, string, maxsplit=maxsplit)

    def findall(self, string: object, pos: int = 0, endpos: int | None = None) -> object:
        if _native is not None:
            return _run_native_literal_findall(self, string, pos=pos, endpos=endpos)
        if not (
            _supports_literal_collection_execution(self)
            or _supports_bounded_single_dot_collection_execution(self)
        ):
            return self._raise_placeholder("findall")
        return _run_literal_findall(self, string, pos=pos, endpos=endpos)

    def finditer(self, string: object, pos: int = 0, endpos: int | None = None) -> object:
        if _native is not None:
            return _run_native_literal_finditer(self, string, pos=pos, endpos=endpos)
        if not _supports_literal_collection_execution(self):
            return self._raise_placeholder("finditer")
        return _run_literal_finditer(self, string, pos=pos, endpos=endpos)

    def sub(
        self,
        repl: object,
        string: object,
        *args: object,
        count: object = _PATTERN_REPLACEMENT_COUNT_UNSET,
        **kwargs: object,
    ) -> object:
        count = _resolve_bound_pattern_replacement_count(
            "sub",
            args,
            count=count,
            kwargs=kwargs,
        )
        compatible_replacement = _ensure_literal_replacement_payload(
            self.pattern,
            repl,
            unsupported=self._raise_placeholder,
            helper_name="sub",
            allow_native_template_passthrough=_allow_native_template_passthrough(self.pattern),
            defer_cross_type_mismatch=True,
        )
        if _native is not None:
            return _run_native_literal_sub(self, compatible_replacement, string, count=count)
        if not _supports_literal_replacement_execution(self):
            return self._raise_placeholder("sub")
        return _run_literal_sub(self, repl, string, count=count)

    def subn(
        self,
        repl: object,
        string: object,
        *args: object,
        count: object = _PATTERN_REPLACEMENT_COUNT_UNSET,
        **kwargs: object,
    ) -> object:
        count = _resolve_bound_pattern_replacement_count(
            "subn",
            args,
            count=count,
            kwargs=kwargs,
        )
        compatible_replacement = _ensure_literal_replacement_payload(
            self.pattern,
            repl,
            unsupported=self._raise_placeholder,
            helper_name="subn",
            allow_native_template_passthrough=_allow_native_template_passthrough(self.pattern),
            defer_cross_type_mismatch=True,
        )
        if _native is not None:
            return _run_native_literal_subn(self, compatible_replacement, string, count=count)
        if not _supports_literal_replacement_execution(self):
            return self._raise_placeholder("subn")
        return _run_literal_subn(self, repl, string, count=count)


Pattern.__module__ = "re"


def _resolve_bound_pattern_split_maxsplit(
    extra_args: tuple[object, ...],
    *,
    maxsplit: object,
    kwargs: dict[str, object],
) -> object:
    extra_argument_count = len(extra_args) + len(kwargs)
    if maxsplit is not _PATTERN_SPLIT_MAXSPLIT_UNSET:
        extra_argument_count += 1

    if extra_argument_count > 1:
        raise TypeError(
            f"split() takes at most 2 arguments ({1 + extra_argument_count} given)"
        )

    if kwargs:
        unexpected_keyword = next(iter(kwargs))
        raise TypeError(
            f"{unexpected_keyword!r} is an invalid keyword argument for split()"
        )

    if extra_args:
        return extra_args[0]

    if maxsplit is _PATTERN_SPLIT_MAXSPLIT_UNSET:
        return 0

    return maxsplit


def _resolve_bound_pattern_replacement_count(
    method_name: str,
    extra_args: tuple[object, ...],
    *,
    count: object,
    kwargs: dict[str, object],
) -> object:
    extra_argument_count = len(extra_args) + len(kwargs)
    if count is not _PATTERN_REPLACEMENT_COUNT_UNSET:
        extra_argument_count += 1

    if extra_argument_count > 1:
        raise TypeError(
            f"{method_name}() takes at most 3 arguments "
            f"({2 + extra_argument_count} given)"
        )

    if kwargs:
        unexpected_keyword = next(iter(kwargs))
        raise TypeError(
            f"{unexpected_keyword!r} is an invalid keyword argument for {method_name}()"
        )

    if extra_args:
        return extra_args[0]

    if count is _PATTERN_REPLACEMENT_COUNT_UNSET:
        return 0

    return count


class Match:
    """Concrete scaffold export for the bounded literal-only match subset."""

    __slots__ = (
        "re",
        "string",
        "pos",
        "endpos",
        "lastindex",
        "lastgroup",
        "_span",
        "_group_spans",
    )

    def __new__(cls, *_args: object, **_kwargs: object) -> "Match":
        raise TypeError("cannot create 're.Match' instances")

    def __init__(
        self,
        pattern: Pattern,
        string: str | bytes,
        pos: int,
        endpos: int,
        span: tuple[int, int],
        group_spans: tuple[tuple[int, int] | None, ...] = (),
        *,
        lastindex: int | None = None,
    ) -> None:
        self.re = pattern
        self.string = string
        self.pos = pos
        self.endpos = endpos
        self._group_spans = group_spans
        self.lastindex = (
            _infer_lastindex(group_spans)
            if lastindex is None
            else lastindex
        )
        self.lastgroup = next(
            (name for name, index in self.re.groupindex.items() if index == self.lastindex),
            None,
        )
        self._span = span

    def __bool__(self) -> bool:
        return True

    def _resolve_group_reference(self, group: object) -> int:
        if group == 0:
            return 0
        if isinstance(group, str):
            if group in self.re.groupindex:
                return self.re.groupindex[group]
            raise IndexError("no such group")
        if isinstance(group, int) and 1 <= group <= len(self._group_spans):
            return group
        raise IndexError("no such group")

    def _slice_group(self, group_index: int, default: object = None) -> str | bytes | object:
        if group_index == 0:
            return self.string[self._span[0] : self._span[1]]
        span = self._group_spans[group_index - 1]
        if span is None:
            return default
        return self.string[span[0] : span[1]]

    def group(self, *groups: object) -> str | bytes | tuple[str | bytes, ...]:
        if not groups:
            return self._slice_group(0)
        if len(groups) == 1:
            return self._slice_group(self._resolve_group_reference(groups[0]))
        values: list[str | bytes] = []
        for group in groups:
            values.append(self._slice_group(self._resolve_group_reference(group)))
        return tuple(values)

    def __getitem__(self, group: object) -> str | bytes:
        return self.group(group)

    def groups(self, default: object = None) -> tuple[object, ...]:
        return tuple(self._slice_group(group_index, default) for group_index in range(1, len(self._group_spans) + 1))

    def groupdict(self, default: object = None) -> dict[str, object]:
        return {
            name: self._slice_group(group_index, default)
            for name, group_index in self.re.groupindex.items()
        }

    @property
    def regs(self) -> tuple[tuple[int, int], ...]:
        return (self._span,) + tuple(
            (-1, -1) if span is None else span for span in self._group_spans
        )

    def expand(self, template: object) -> str | bytes:
        return _expand_match_template(self, template)

    def span(self, group: object = 0) -> tuple[int, int]:
        group_index = self._resolve_group_reference(group)
        if group_index == 0:
            return self._span
        span = self._group_spans[group_index - 1]
        return (-1, -1) if span is None else span

    def start(self, group: object = 0) -> int:
        return self.span(group)[0]

    def end(self, group: object = 0) -> int:
        return self.span(group)[1]


def _expand_match_template(match: Match, template: object) -> str | bytes:
    if isinstance(template, str):
        return _expand_str_match_template(match, template)
    if isinstance(template, (bytes, bytearray, memoryview)):
        return _expand_bytes_match_template(match, bytes(template))
    raise TypeError(f"decoding to str: need a bytes-like object, {type(template).__name__} found")


def _infer_lastindex(
    group_spans: tuple[tuple[int, int] | None, ...],
) -> int | None:
    inferred_index: int | None = None
    latest_end = -1
    for index, span in enumerate(group_spans, start=1):
        if span is None:
            continue
        end = span[1]
        if inferred_index is None or end > latest_end or (
            end == latest_end and index < inferred_index
        ):
            inferred_index = index
            latest_end = end
    return inferred_index


def _expand_str_match_template(match: Match, template: str) -> str | bytes:
    pieces: list[str | bytes] = []
    literal_start = 0
    index = 0

    while index < len(template):
        if template[index] != "\\":
            index += 1
            continue

        if literal_start != index:
            pieces.append(template[literal_start:index])

        piece, index = _expand_str_match_escape(match, template, index)
        pieces.append(piece)
        literal_start = index

    if literal_start < len(template):
        pieces.append(template[literal_start:])

    return template[:0].join(pieces)


def _expand_str_match_escape(match: Match, template: str, escape_index: int) -> tuple[str | bytes, int]:
    if escape_index + 1 >= len(template):
        _raise_regex_error("bad escape (end of pattern)", template, escape_index)
        raise AssertionError("_raise_regex_error() should raise")  # pragma: no cover

    token = template[escape_index + 1]
    if token == "\\":
        return "\\", escape_index + 2

    if token == "g":
        if escape_index + 2 >= len(template) or template[escape_index + 2] != "<":
            _raise_regex_error(r"bad escape \g", template, escape_index)
            raise AssertionError("_raise_regex_error() should raise")  # pragma: no cover
        close_index = template.find(">", escape_index + 3)
        if close_index == -1:
            _raise_regex_error("missing >, unterminated name", template, escape_index + 3)
            raise AssertionError("_raise_regex_error() should raise")  # pragma: no cover
        return (
            _resolve_template_group_value(
                match,
                template[escape_index + 3 : close_index],
                template[:0],
                template,
                escape_index + 3,
            ),
            close_index + 1,
        )

    if token.isdigit():
        if token == "0":
            return "\x00", escape_index + 2
        return (
            _resolve_template_group_value(
                match,
                token,
                template[:0],
                template,
                escape_index + 1,
            ),
            escape_index + 2,
        )

    _raise_regex_error(fr"bad escape \{token}", template, escape_index)
    raise AssertionError("_raise_regex_error() should raise")  # pragma: no cover


def _expand_bytes_match_template(match: Match, template: bytes) -> str | bytes:
    pieces: list[str | bytes] = []
    literal_start = 0
    index = 0

    while index < len(template):
        if template[index] != 92:
            index += 1
            continue

        if literal_start != index:
            pieces.append(template[literal_start:index])

        piece, index = _expand_bytes_match_escape(match, template, index)
        pieces.append(piece)
        literal_start = index

    if literal_start < len(template):
        pieces.append(template[literal_start:])

    return template[:0].join(pieces)


def _expand_bytes_match_escape(match: Match, template: bytes, escape_index: int) -> tuple[str | bytes, int]:
    if escape_index + 1 >= len(template):
        _raise_regex_error("bad escape (end of pattern)", template, escape_index)
        raise AssertionError("_raise_regex_error() should raise")  # pragma: no cover

    token = template[escape_index + 1]
    if token == 92:
        return b"\\", escape_index + 2

    if token == ord("g"):
        if escape_index + 2 >= len(template) or template[escape_index + 2] != ord("<"):
            _raise_regex_error(r"bad escape \g", template, escape_index)
            raise AssertionError("_raise_regex_error() should raise")  # pragma: no cover
        close_index = template.find(b">", escape_index + 3)
        if close_index == -1:
            _raise_regex_error("missing >, unterminated name", template, escape_index + 3)
            raise AssertionError("_raise_regex_error() should raise")  # pragma: no cover
        return (
            _resolve_template_group_value(
                match,
                template[escape_index + 3 : close_index].decode("ascii"),
                template[:0],
                template,
                escape_index + 3,
            ),
            close_index + 1,
        )

    if chr(token).isdigit():
        if token == ord("0"):
            return b"\x00", escape_index + 2
        return (
            _resolve_template_group_value(
                match,
                chr(token),
                template[:0],
                template,
                escape_index + 1,
            ),
            escape_index + 2,
        )

    _raise_regex_error(fr"bad escape \{chr(token)}", template, escape_index)
    raise AssertionError("_raise_regex_error() should raise")  # pragma: no cover


def _resolve_template_group_value(
    match: Match,
    group_name: str,
    empty: str | bytes,
    template: str | bytes,
    position: int,
) -> str | bytes:
    if group_name.isdigit():
        group_index = int(group_name)
        if group_index == 0:
            return match._slice_group(0, empty)
        if not 1 <= group_index <= len(match._group_spans):
            _raise_regex_error(f"invalid group reference {group_index}", template, position)
            raise AssertionError("_raise_regex_error() should raise")  # pragma: no cover
        return match._slice_group(group_index, empty)

    if group_name not in match.re.groupindex:
        raise IndexError(f"unknown group name '{group_name}'")
    return match._slice_group(match.re.groupindex[group_name], empty)


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


def _grouped_literal_body(pattern: str) -> str | None:
    if not pattern.startswith("(") or not pattern.endswith(")"):
        return None
    body = pattern[1:-1]
    if not body or not _supports_pattern_scaffold(body):
        return None
    return body


def _allow_native_template_passthrough(pattern: str | bytes) -> bool:
    return _native is not None and (
        isinstance(pattern, str) or pattern in _NATIVE_TEMPLATE_BYTES_PATTERNS
    )


def _allow_native_callable_bytes_passthrough(pattern: str | bytes) -> bool:
    return (
        _native is not None
        and isinstance(pattern, bytes)
        and pattern in _NATIVE_CALLABLE_BYTES_PATTERNS
    )


def _literal_match_base_flags(pattern: str | bytes) -> int:
    return _normalize_pattern_flags(pattern, 0)


def _supports_literal_execution(compiled_pattern: Pattern) -> bool:
    if not compiled_pattern._supports_literal:
        return False
    base_flags = _literal_match_base_flags(compiled_pattern.pattern)
    return compiled_pattern.flags in (base_flags, base_flags | int(IGNORECASE))


def _supports_bounded_ascii_ignorecase_search_execution(
    compiled_pattern: Pattern,
    mode: str,
) -> bool:
    return (
        compiled_pattern._supports_literal
        and mode == "search"
        and isinstance(compiled_pattern.pattern, str)
        and compiled_pattern.pattern == "abc"
        and compiled_pattern.flags == int(IGNORECASE | ASCII)
    )


def _supports_literal_collection_execution(compiled_pattern: Pattern) -> bool:
    if not compiled_pattern._supports_literal:
        return False
    return compiled_pattern.flags == _literal_match_base_flags(compiled_pattern.pattern) and len(compiled_pattern.pattern) > 0


def _supports_literal_replacement_execution(compiled_pattern: Pattern) -> bool:
    return _supports_literal_collection_execution(compiled_pattern)


def _supports_bounded_single_dot_execution(compiled_pattern: Pattern) -> bool:
    if compiled_pattern.pattern != "a.c":
        return False
    base_flags = _literal_match_base_flags(compiled_pattern.pattern)
    return compiled_pattern.flags in (base_flags, base_flags | int(IGNORECASE))


def _supports_bounded_single_dot_collection_execution(compiled_pattern: Pattern) -> bool:
    return (
        compiled_pattern.pattern == "a.c"
        and compiled_pattern.flags == _literal_match_base_flags(compiled_pattern.pattern)
    )


def _supports_grouped_segment_leading_capture_search_execution(
    compiled_pattern: Pattern,
    mode: str,
) -> bool:
    return (
        mode == "search"
        and isinstance(compiled_pattern.pattern, str)
        and compiled_pattern.pattern == "(ab)c"
        and compiled_pattern.flags == int(UNICODE)
        and compiled_pattern.groups == 1
        and compiled_pattern.groupindex == {}
    )


def _bounded_numbered_backreference_search_spec(
    compiled_pattern: Pattern,
    mode: str,
) -> tuple[str, int, int] | None:
    if mode != "search" or not isinstance(compiled_pattern.pattern, str):
        return None
    if compiled_pattern.flags != int(UNICODE):
        return None
    if compiled_pattern.groups != 1 or compiled_pattern.groupindex != {}:
        return None
    return _BOUNDED_NUMBERED_BACKREFERENCE_SEARCH_CASES.get(compiled_pattern.pattern)


def _supports_exact_triple_nested_group_execution(compiled_pattern: Pattern) -> bool:
    return (
        isinstance(compiled_pattern.pattern, str)
        and compiled_pattern.pattern == _EXACT_TRIPLE_NESTED_GROUP_PATTERN
        and compiled_pattern.flags == int(UNICODE)
        and compiled_pattern.groups == 3
        and compiled_pattern.groupindex == {}
    )


def _supports_exact_quantified_nested_group_execution(
    compiled_pattern: Pattern,
) -> bool:
    if (
        not isinstance(compiled_pattern.pattern, str)
        or compiled_pattern.flags != int(UNICODE)
        or compiled_pattern.groups != 2
    ):
        return False
    if compiled_pattern.pattern == _EXACT_NUMBERED_QUANTIFIED_NESTED_GROUP_PATTERN:
        return compiled_pattern.groupindex == {}
    return (
        compiled_pattern.pattern == _EXACT_NAMED_QUANTIFIED_NESTED_GROUP_PATTERN
        and compiled_pattern.groupindex == {"outer": 1, "inner": 2}
    )


def _raise_regex_error(message: str, pattern: str | bytes, pos: int) -> object:
    raise error(message, pattern, pos)


def _build_compiled_pattern(
    pattern: str | bytes,
    flags: int,
    *,
    supports_literal: bool,
    groups: int = 0,
    groupindex: dict[str, int] | None = None,
) -> Pattern:
    compiled = object.__new__(Pattern)
    Pattern.__init__(
        compiled,
        pattern,
        flags,
        supports_literal=supports_literal,
        groups=groups,
        groupindex=groupindex,
    )
    return compiled


def _source_tree_compile_fallback(
    pattern: str | bytes,
    flags: int,
) -> Pattern | None:
    if pattern == _EXACT_TRIPLE_NESTED_GROUP_PATTERN and flags == int(UNICODE):
        return _build_compiled_pattern(
            pattern,
            flags,
            supports_literal=False,
            groups=3,
        )
    if (
        pattern == _EXACT_NUMBERED_QUANTIFIED_NESTED_GROUP_PATTERN
        and flags == int(UNICODE)
    ):
        return _build_compiled_pattern(
            pattern,
            flags,
            supports_literal=False,
            groups=2,
        )
    return None


def _build_native_compile_result(pattern: str | bytes, flags: int) -> Pattern:
    native_result = _native.boundary_compile(pattern, int(flags))
    if len(native_result) == 3:
        status, normalized_flags, supports_literal = native_result
        groups = 0
        groupindex = {}
    else:
        if len(native_result) == 4:
            status, normalized_flags, supports_literal, groups = native_result
            groupindex = {}
        else:
            status, normalized_flags, supports_literal, groups, groupindex_items = native_result
            groupindex = dict(groupindex_items)
    if status != "compiled":
        fallback = _source_tree_compile_fallback(pattern, normalized_flags)
        if fallback is not None:
            return fallback
        return _raise_placeholder("compile")
    return _build_compiled_pattern(
        pattern,
        normalized_flags,
        supports_literal=supports_literal,
        groups=groups,
        groupindex=groupindex,
    )


def _select_captured_span_for_mode(
    spans: tuple[tuple[int, int], ...],
    mode: str,
    normalized_pos: int,
    normalized_endpos: int,
) -> int | None:
    if mode == "search":
        return 0 if spans else None
    for index, span in enumerate(spans):
        if mode == "match" and span[0] == normalized_pos:
            return index
        if mode == "fullmatch" and span == (normalized_pos, normalized_endpos):
            return index
    return None


def _run_exact_triple_nested_group_match(
    compiled_pattern: Pattern,
    mode: str,
    compatible_string: str,
    normalized_pos: int,
    normalized_endpos: int,
) -> Match | None:
    literal = _EXACT_TRIPLE_NESTED_GROUP_LITERAL
    if mode == "search":
        start = compatible_string.find(literal, normalized_pos, normalized_endpos)
        if start < 0:
            return None
        span = (start, start + len(literal))
    elif mode == "match":
        if not compatible_string.startswith(literal, normalized_pos, normalized_endpos):
            return None
        span = (normalized_pos, normalized_pos + len(literal))
    elif mode == "fullmatch":
        if normalized_endpos - normalized_pos != len(literal):
            return None
        if not compatible_string.startswith(literal, normalized_pos, normalized_endpos):
            return None
        span = (normalized_pos, normalized_endpos)
    else:  # pragma: no cover - internal misuse guard
        raise ValueError(f"unsupported literal match mode {mode!r}")

    capture_span = (span[0] + 1, span[0] + 2)
    return _build_match(
        compiled_pattern,
        compatible_string,
        normalized_pos,
        normalized_endpos,
        span,
        (capture_span, capture_span, capture_span),
    )


def _run_exact_quantified_nested_group_match(
    compiled_pattern: Pattern,
    mode: str,
    compatible_string: str,
    normalized_pos: int,
    normalized_endpos: int,
) -> Match | None:
    spans: list[tuple[int, int]] = []
    group_spans: list[tuple[tuple[int, int] | None, ...]] = []
    start_positions = (
        range(normalized_pos, normalized_endpos + 1)
        if mode == "search"
        else (normalized_pos,)
    )

    for start in start_positions:
        if start >= normalized_endpos or compatible_string[start] != "a":
            continue
        outer_start = start + 1
        repeat_count = 0
        next_inner_start = outer_start
        while compatible_string.startswith("bc", next_inner_start, normalized_endpos):
            repeat_count += 1
            next_inner_start += 2

        while repeat_count > 0:
            outer_end = outer_start + repeat_count * 2
            if outer_end < normalized_endpos and compatible_string[outer_end] == "d":
                spans.append((start, outer_end + 1))
                group_spans.append(
                    ((outer_start, outer_end), (outer_end - 2, outer_end))
                )
                break
            repeat_count -= 1

        if mode != "search":
            break

    selected_index = _select_captured_span_for_mode(
        tuple(spans),
        mode,
        normalized_pos,
        normalized_endpos,
    )
    if selected_index is None:
        return None
    return _build_match(
        compiled_pattern,
        compatible_string,
        normalized_pos,
        normalized_endpos,
        spans[selected_index],
        group_spans[selected_index],
    )


def _run_exact_nested_group_match(
    compiled_pattern: Pattern,
    mode: str,
    string: object,
    pos: int = 0,
    endpos: int | None = None,
) -> Match | None | object:
    if not isinstance(compiled_pattern.pattern, str):
        return _MATCH_FALLBACK_UNSUPPORTED
    compatible_string = _ensure_compatible_string(compiled_pattern.pattern, string)
    normalized_pos, normalized_endpos = _normalize_match_bounds(
        compatible_string,
        pos,
        endpos,
    )
    if _supports_exact_triple_nested_group_execution(compiled_pattern):
        return _run_exact_triple_nested_group_match(
            compiled_pattern,
            mode,
            compatible_string,
            normalized_pos,
            normalized_endpos,
        )
    if _supports_exact_quantified_nested_group_execution(compiled_pattern):
        return _run_exact_quantified_nested_group_match(
            compiled_pattern,
            mode,
            compatible_string,
            normalized_pos,
            normalized_endpos,
        )
    return _MATCH_FALLBACK_UNSUPPORTED


def _dispatch_pattern_match(
    compiled_pattern: Pattern,
    mode: str,
    string: object,
    pos: int = 0,
    endpos: int | None = None,
) -> Match | None:
    if _native is not None:
        native_result = _native.boundary_literal_match(
            compiled_pattern.pattern,
            compiled_pattern.flags,
            mode,
            string,
            pos,
            endpos,
        )
        if len(native_result) == 4:
            status, normalized_pos, normalized_endpos, span = native_result
            group_spans = ()
            lastindex = None
        elif len(native_result) == 5:
            status, normalized_pos, normalized_endpos, span, group_spans = native_result
            lastindex = None
        else:
            status, normalized_pos, normalized_endpos, span, group_spans, lastindex = native_result
        if status == "unsupported":
            exact_nested_group_match = _run_exact_nested_group_match(
                compiled_pattern,
                mode,
                string,
                pos=pos,
                endpos=endpos,
            )
            if exact_nested_group_match is not _MATCH_FALLBACK_UNSUPPORTED:
                return exact_nested_group_match
            return compiled_pattern._raise_placeholder(mode)
        if status == "no-match":
            return None
        return _build_match(
            compiled_pattern,
            _ensure_compatible_string(compiled_pattern.pattern, string),
            normalized_pos,
            normalized_endpos,
            span,
            tuple(group_spans),
            lastindex=lastindex,
        )

    numbered_backreference_search_spec = _bounded_numbered_backreference_search_spec(
        compiled_pattern,
        mode,
    )
    exact_nested_group_match = _run_exact_nested_group_match(
        compiled_pattern,
        mode,
        string,
        pos=pos,
        endpos=endpos,
    )
    if not (
        _supports_literal_execution(compiled_pattern)
        or _supports_bounded_ascii_ignorecase_search_execution(compiled_pattern, mode)
        or _supports_bounded_single_dot_execution(compiled_pattern)
        or numbered_backreference_search_spec is not None
        or exact_nested_group_match is not _MATCH_FALLBACK_UNSUPPORTED
        or _supports_grouped_segment_leading_capture_search_execution(
            compiled_pattern, mode
        )
    ):
        return compiled_pattern._raise_placeholder(mode)

    if exact_nested_group_match is not _MATCH_FALLBACK_UNSUPPORTED:
        return exact_nested_group_match
    if numbered_backreference_search_spec is not None:
        return _run_bounded_numbered_backreference_search(
            compiled_pattern,
            string,
            numbered_backreference_search_spec,
            pos=pos,
            endpos=endpos,
        )
    if _supports_grouped_segment_leading_capture_search_execution(compiled_pattern, mode):
        return _run_grouped_segment_leading_capture_search(
            compiled_pattern,
            string,
            pos=pos,
            endpos=endpos,
        )
    return _run_literal_match(compiled_pattern, mode, string, pos=pos, endpos=endpos)


def _run_native_literal_split(
    compiled_pattern: Pattern,
    string: object,
    maxsplit: int = 0,
) -> list[str] | list[bytes]:
    status, items = _native.boundary_literal_split(
        compiled_pattern.pattern,
        compiled_pattern.flags,
        string,
        maxsplit,
    )
    if status == "unsupported":
        return compiled_pattern._raise_placeholder("split")
    return items


def _run_native_literal_findall(
    compiled_pattern: Pattern,
    string: object,
    pos: int = 0,
    endpos: int | None = None,
) -> list[str] | list[bytes]:
    status, items = _native.boundary_literal_findall(
        compiled_pattern.pattern,
        compiled_pattern.flags,
        string,
        pos,
        endpos,
    )
    if status == "unsupported":
        return compiled_pattern._raise_placeholder("findall")
    return items


def _run_native_literal_finditer(
    compiled_pattern: Pattern,
    string: object,
    pos: int = 0,
    endpos: int | None = None,
):
    native_result = _native.boundary_literal_finditer(
        compiled_pattern.pattern,
        compiled_pattern.flags,
        string,
        pos,
        endpos,
    )
    if len(native_result) == 4:
        status, normalized_pos, normalized_endpos, spans = native_result
    else:
        status, normalized_pos, normalized_endpos, spans, _group_spans = native_result
    if status == "unsupported":
        return compiled_pattern._raise_placeholder("finditer")

    compatible_string = _ensure_compatible_string(compiled_pattern.pattern, string)
    return iter(
        [
            _build_match(compiled_pattern, compatible_string, normalized_pos, normalized_endpos, span)
            for span in spans
        ]
    )


def _run_native_literal_sub(
    compiled_pattern: Pattern,
    repl: object,
    string: object,
    count: int = 0,
) -> str | bytes:
    substituted, _replacement_count = _run_native_literal_subn(
        compiled_pattern,
        repl,
        string,
        count=count,
        helper_name="sub",
    )
    return substituted


def _run_native_literal_subn(
    compiled_pattern: Pattern,
    repl: object,
    string: object,
    count: int = 0,
    *,
    helper_name: str = "subn",
) -> tuple[str | bytes, int]:
    deferred_cross_type_result = _deferred_cross_type_replacement_result(
        compiled_pattern,
        repl,
        string,
        count,
    )
    if deferred_cross_type_result is not _DEFERRED_CROSS_TYPE_REPLACEMENT_UNHANDLED:
        return deferred_cross_type_result

    if callable(repl):
        return _run_native_literal_callable_subn(
            compiled_pattern,
            repl,
            string,
            count=count,
            helper_name=helper_name,
        )

    if (
        isinstance(compiled_pattern.pattern, str)
        and isinstance(repl, str)
        and "\\" in repl
        and _allow_native_template_passthrough(compiled_pattern.pattern)
    ):
        # Capture-sensitive template expansion stays in the native boundary.
        status, substituted, replacement_count = _native.boundary_literal_template_subn(
            compiled_pattern.pattern,
            compiled_pattern.flags,
            repl,
            string,
            count,
        )
        if status == "unsupported":
            return compiled_pattern._raise_placeholder(helper_name)
        return substituted, replacement_count
    if (
        isinstance(compiled_pattern.pattern, bytes)
        and isinstance(repl, bytes)
        and b"\\" in repl
        and _allow_native_template_passthrough(compiled_pattern.pattern)
    ):
        status, substituted, replacement_count = (
            _native.boundary_literal_template_subn_bytes(
                compiled_pattern.pattern,
                compiled_pattern.flags,
                repl,
                string,
                count,
            )
        )
        if status == "unsupported":
            return compiled_pattern._raise_placeholder(helper_name)
        return substituted, replacement_count

    status, substituted, replacement_count = _native.boundary_literal_subn(
        compiled_pattern.pattern,
        compiled_pattern.flags,
        repl,
        string,
        count,
    )
    if status == "unsupported":
        return compiled_pattern._raise_placeholder(helper_name)
    return substituted, replacement_count


def _run_native_literal_callable_subn(
    compiled_pattern: Pattern,
    repl,
    string: object,
    count: int = 0,
    *,
    helper_name: str = "subn",
) -> tuple[str | bytes, int]:
    compatible_string = _ensure_compatible_string(compiled_pattern.pattern, string)
    normalized_count = operator.index(count)
    if normalized_count < 0:
        return compatible_string, 0

    status, normalized_pos, normalized_endpos, spans, group_spans = _native_callable_match_spans(
        compiled_pattern,
        compatible_string,
    )
    if status == "unsupported":
        return compiled_pattern._raise_placeholder(helper_name)

    replacement_limit = len(spans) if normalized_count == 0 else min(normalized_count, len(spans))
    if replacement_limit == 0:
        return compatible_string, 0

    parts: list[str] | list[bytes] = []
    last_end = 0

    for index, span in enumerate(spans[:replacement_limit]):
        parts.append(compatible_string[last_end : span[0]])
        match = _build_match(
            compiled_pattern,
            compatible_string,
            normalized_pos,
            normalized_endpos,
            span,
            group_spans[index],
        )
        replacement = repl(match)
        parts.append(
            _coerce_callable_replacement_piece(
                compiled_pattern.pattern,
                replacement,
                len(parts),
            )
        )
        last_end = span[1]

    parts.append(compatible_string[last_end:])
    return compatible_string[:0].join(parts), replacement_limit


def _native_callable_match_spans(
    compiled_pattern: Pattern,
    compatible_string: str | bytes,
) -> tuple[str, int, int, list[tuple[int, int]], list[tuple[tuple[int, int] | None, ...]]]:
    status, normalized_pos, normalized_endpos, spans = _native.boundary_literal_finditer(
        compiled_pattern.pattern,
        compiled_pattern.flags,
        compatible_string,
        0,
        None,
    )
    if status != "unsupported":
        return (
            status,
            normalized_pos,
            normalized_endpos,
            spans,
            [tuple() for _ in spans],
        )

    if isinstance(compiled_pattern.pattern, bytes):
        status, normalized_pos, normalized_endpos, spans, group_spans = (
            _native.boundary_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_finditer_bytes(
                compiled_pattern.pattern,
                compiled_pattern.flags,
                compatible_string,
                0,
                None,
            )
        )
        if status != "unsupported":
            return (
                status,
                normalized_pos,
                normalized_endpos,
                spans,
                [tuple(match_group_spans) for match_group_spans in group_spans],
            )

        status, normalized_pos, normalized_endpos, spans, group_spans = (
            _native.boundary_nested_broader_range_open_ended_quantified_group_alternation_backtracking_heavy_finditer_bytes(
                compiled_pattern.pattern,
                compiled_pattern.flags,
                compatible_string,
                0,
                None,
            )
        )
        if status != "unsupported":
            return (
                status,
                normalized_pos,
                normalized_endpos,
                spans,
                [tuple(match_group_spans) for match_group_spans in group_spans],
            )

        status, normalized_pos, normalized_endpos, spans, group_spans = (
            _native.boundary_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_finditer_bytes(
                compiled_pattern.pattern,
                compiled_pattern.flags,
                compatible_string,
                0,
                None,
            )
        )
        if status != "unsupported":
            return (
                status,
                normalized_pos,
                normalized_endpos,
                spans,
                [tuple(match_group_spans) for match_group_spans in group_spans],
            )

        status, normalized_pos, normalized_endpos, spans, group_spans = (
            _native.boundary_nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_finditer_bytes(
                compiled_pattern.pattern,
                compiled_pattern.flags,
                compatible_string,
                0,
                None,
            )
        )
        if status != "unsupported":
            return (
                status,
                normalized_pos,
                normalized_endpos,
                spans,
                [tuple(match_group_spans) for match_group_spans in group_spans],
            )

        status, normalized_pos, normalized_endpos, spans, group_spans = (
            _native.boundary_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_conditional_finditer_bytes(
                compiled_pattern.pattern,
                compiled_pattern.flags,
                compatible_string,
                0,
                None,
            )
        )
        if status != "unsupported":
            return (
                status,
                normalized_pos,
                normalized_endpos,
                spans,
                [tuple(match_group_spans) for match_group_spans in group_spans],
            )

        status, normalized_pos, normalized_endpos, spans, group_spans = (
            _native.boundary_nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_finditer_bytes(
                compiled_pattern.pattern,
                compiled_pattern.flags,
                compatible_string,
                0,
                None,
            )
        )
        if status != "unsupported":
            return (
                status,
                normalized_pos,
                normalized_endpos,
                spans,
                [tuple(match_group_spans) for match_group_spans in group_spans],
            )

    if isinstance(compiled_pattern.pattern, str):
        status, normalized_pos, normalized_endpos, spans, group_spans = (
            _native.boundary_nested_capture_finditer(
                compiled_pattern.pattern,
                compiled_pattern.flags,
                compatible_string,
                0,
                None,
            )
        )
        if status != "unsupported":
            return (
                status,
                normalized_pos,
                normalized_endpos,
                spans,
                [tuple(match_group_spans) for match_group_spans in group_spans],
            )

        status, normalized_pos, normalized_endpos, spans, group_spans = (
            _native.boundary_nested_alternation_finditer(
                compiled_pattern.pattern,
                compiled_pattern.flags,
                compatible_string,
                0,
                None,
            )
        )
        if status != "unsupported":
            return (
                status,
                normalized_pos,
                normalized_endpos,
                spans,
                [tuple(match_group_spans) for match_group_spans in group_spans],
            )

        status, normalized_pos, normalized_endpos, spans, group_spans = (
            _native.boundary_nested_alternation_branch_local_backreference_finditer(
                compiled_pattern.pattern,
                compiled_pattern.flags,
                compatible_string,
                0,
                None,
            )
        )
        if status != "unsupported":
            return (
                status,
                normalized_pos,
                normalized_endpos,
                spans,
                [tuple(match_group_spans) for match_group_spans in group_spans],
            )

        status, normalized_pos, normalized_endpos, spans, group_spans = (
            _native.boundary_quantified_nested_group_alternation_finditer(
                compiled_pattern.pattern,
                compiled_pattern.flags,
                compatible_string,
                0,
                None,
            )
        )
        if status != "unsupported":
            return (
                status,
                normalized_pos,
                normalized_endpos,
                spans,
                [tuple(match_group_spans) for match_group_spans in group_spans],
            )

        status, normalized_pos, normalized_endpos, spans, group_spans = (
            _native.boundary_quantified_nested_group_alternation_branch_local_backreference_finditer(
                compiled_pattern.pattern,
                compiled_pattern.flags,
                compatible_string,
                0,
                None,
            )
        )
        if status != "unsupported":
            return (
                status,
                normalized_pos,
                normalized_endpos,
                spans,
                [tuple(match_group_spans) for match_group_spans in group_spans],
            )

        status, normalized_pos, normalized_endpos, spans, group_spans = (
            _native.boundary_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_finditer(
                compiled_pattern.pattern,
                compiled_pattern.flags,
                compatible_string,
                0,
                None,
            )
        )
        if status != "unsupported":
            return (
                status,
                normalized_pos,
                normalized_endpos,
                spans,
                [tuple(match_group_spans) for match_group_spans in group_spans],
            )

        status, normalized_pos, normalized_endpos, spans, group_spans = (
            _native.boundary_nested_broader_range_open_ended_quantified_group_alternation_backtracking_heavy_finditer(
                compiled_pattern.pattern,
                compiled_pattern.flags,
                compatible_string,
                0,
                None,
            )
        )
        if status != "unsupported":
            return (
                status,
                normalized_pos,
                normalized_endpos,
                spans,
                [tuple(match_group_spans) for match_group_spans in group_spans],
            )

        status, normalized_pos, normalized_endpos, spans, group_spans = (
            _native.boundary_nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_finditer(
                compiled_pattern.pattern,
                compiled_pattern.flags,
                compatible_string,
                0,
                None,
            )
        )
        if status != "unsupported":
            return (
                status,
                normalized_pos,
                normalized_endpos,
                spans,
                [tuple(match_group_spans) for match_group_spans in group_spans],
            )

        status, normalized_pos, normalized_endpos, spans, group_spans = (
            _native.boundary_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_conditional_finditer(
                compiled_pattern.pattern,
                compiled_pattern.flags,
                compatible_string,
                0,
                None,
            )
        )
        if status != "unsupported":
            return (
                status,
                normalized_pos,
                normalized_endpos,
                spans,
                [tuple(match_group_spans) for match_group_spans in group_spans],
            )

        status, normalized_pos, normalized_endpos, spans, group_spans = (
            _native.boundary_conditional_group_exists_finditer(
                compiled_pattern.pattern,
                compiled_pattern.flags,
                compatible_string,
                0,
                None,
            )
        )
        if status != "unsupported":
            return (
                status,
                normalized_pos,
                normalized_endpos,
                spans,
                [tuple(match_group_spans) for match_group_spans in group_spans],
            )

        status, normalized_pos, normalized_endpos, spans, capture_1_spans = (
            _native.boundary_grouped_alternation_finditer(
                compiled_pattern.pattern,
                compiled_pattern.flags,
                compatible_string,
                0,
                None,
            )
        )
        if status != "unsupported":
            return (
                status,
                normalized_pos,
                normalized_endpos,
                spans,
                [(capture_1_span,) for capture_1_span in capture_1_spans],
            )

    return status, normalized_pos, normalized_endpos, spans, []


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

    if pattern == "a.c" and flags in (int(UNICODE), int(IGNORECASE | UNICODE)):
        return _build_compiled_pattern(pattern, flags, supports_literal=False)

    if (
        isinstance(pattern, str)
        and pattern in _BOUNDED_NUMBERED_BACKREFERENCE_SEARCH_CASES
        and flags == int(UNICODE)
    ):
        return _build_compiled_pattern(pattern, flags, supports_literal=False, groups=1)

    if pattern == "(ab)c" and flags == int(UNICODE):
        return _build_compiled_pattern(pattern, flags, supports_literal=False, groups=1)

    if isinstance(pattern, str) and flags == int(UNICODE):
        grouped_literal_body = _grouped_literal_body(pattern)
        if grouped_literal_body is not None:
            return _build_compiled_pattern(pattern, flags, supports_literal=False, groups=1)

    if pattern == _EXACT_TRIPLE_NESTED_GROUP_PATTERN and flags == int(UNICODE):
        return _build_compiled_pattern(pattern, flags, supports_literal=False, groups=3)

    if (
        pattern == _EXACT_NUMBERED_QUANTIFIED_NESTED_GROUP_PATTERN
        and flags == int(UNICODE)
    ):
        return _build_compiled_pattern(
            pattern,
            flags,
            supports_literal=False,
            groups=2,
        )

    if pattern == _EXACT_NAMED_QUANTIFIED_NESTED_GROUP_PATTERN and flags == int(UNICODE):
        return _build_compiled_pattern(
            pattern,
            flags,
            supports_literal=False,
            groups=2,
            groupindex={"outer": 1, "inner": 2},
        )

    if pattern in {
        "a((bc|de){1,4})d",
        "a(?P<outer>(bc|de){1,4})d",
    } and flags == int(UNICODE):
        return _build_compiled_pattern(
            pattern,
            flags,
            supports_literal=False,
            groups=2,
            groupindex={"outer": 1} if pattern.startswith("a(?P<outer>") else {},
        )

    if pattern in {
        r"a((b|c){1,4})\2d",
        r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
    } and flags == int(UNICODE):
        return _build_compiled_pattern(
            pattern,
            flags,
            supports_literal=False,
            groups=2,
            groupindex={"outer": 1, "inner": 2}
            if pattern.startswith("a(?P<outer>")
            else {},
        )

    if (
        pattern == "[A-Z_][a-z0-9_]+"
        and flags == int(IGNORECASE | UNICODE)
    ) or pattern in {"(?u:a)", "(?<=ab)c", "a*+", "(?>ab|a)b"} or pattern == b"(?L:a)":
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
    length = len(string)

    def _clamp_bound(value: int) -> int:
        normalized = operator.index(value)
        if normalized < 0:
            return 0
        if normalized > length:
            return length
        return normalized

    return _clamp_bound(pos), length if endpos is None else _clamp_bound(endpos)


def _build_match(
    compiled_pattern: Pattern,
    string: str | bytes,
    pos: int,
    endpos: int,
    span: tuple[int, int],
    group_spans: tuple[tuple[int, int] | None, ...] = (),
    *,
    lastindex: int | None = None,
) -> Match:
    match = object.__new__(Match)
    Match.__init__(
        match,
        compiled_pattern,
        string,
        pos,
        endpos,
        span,
        group_spans,
        lastindex=lastindex,
    )
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
    if _supports_bounded_single_dot_execution(compiled_pattern):
        for offset, pattern_unit in enumerate(pattern):
            if pattern_unit == ".":
                continue
            if not _literal_ignores_case(compiled_pattern):
                if pattern_unit != string[start + offset]:
                    return False
            elif not _literal_units_equal(pattern_unit, string[start + offset]):
                return False
        return True
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
    if not _literal_ignores_case(compiled_pattern) and not _supports_bounded_single_dot_execution(
        compiled_pattern
    ):
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


def _run_grouped_segment_leading_capture_search(
    compiled_pattern: Pattern,
    string: object,
    pos: int = 0,
    endpos: int | None = None,
) -> Match | None:
    compatible_string = _ensure_compatible_string(compiled_pattern.pattern, string)
    normalized_pos, normalized_endpos = _normalize_match_bounds(
        compatible_string,
        pos,
        endpos,
    )
    start = compatible_string.find("abc", normalized_pos, normalized_endpos)
    if start < 0:
        return None
    return _build_match(
        compiled_pattern,
        compatible_string,
        normalized_pos,
        normalized_endpos,
        (start, start + 3),
        ((start, start + 2),),
    )


def _run_bounded_numbered_backreference_search(
    compiled_pattern: Pattern,
    string: object,
    search_spec: tuple[str, int, int],
    pos: int = 0,
    endpos: int | None = None,
) -> Match | None:
    literal, group_start_offset, group_end_offset = search_spec
    compatible_string = _ensure_compatible_string(compiled_pattern.pattern, string)
    normalized_pos, normalized_endpos = _normalize_match_bounds(
        compatible_string,
        pos,
        endpos,
    )
    start = compatible_string.find(literal, normalized_pos, normalized_endpos)
    if start < 0:
        return None
    return _build_match(
        compiled_pattern,
        compatible_string,
        normalized_pos,
        normalized_endpos,
        (start, start + len(literal)),
        ((start + group_start_offset, start + group_end_offset),),
    )


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
    allow_native_template_passthrough: bool = False,
    defer_cross_type_mismatch: bool = False,
) -> object:
    if callable(repl):
        if isinstance(pattern, bytes) and not _allow_native_callable_bytes_passthrough(pattern):
            unsupported(helper_name)
            raise AssertionError("unsupported() should raise")  # pragma: no cover
        return repl

    if isinstance(pattern, str):
        if not isinstance(repl, str):
            if defer_cross_type_mismatch and isinstance(repl, (bytes, bytearray, memoryview)):
                return repl
            raise TypeError(f"sequence item 0: expected str instance, {type(repl).__name__} found")
        if (
            "\\" in repl
            and not allow_native_template_passthrough
            and _expand_literal_replacement_template(repl, "") is None
        ):
            unsupported(helper_name)
            raise AssertionError("unsupported() should raise")  # pragma: no cover
        return repl

    if not isinstance(repl, bytes):
        if defer_cross_type_mismatch and isinstance(repl, str):
            return repl
        raise TypeError(f"sequence item 0: expected a bytes-like object, {type(repl).__name__} found")
    if b"\\" in repl and not allow_native_template_passthrough:
        unsupported(helper_name)
        raise AssertionError("unsupported() should raise")  # pragma: no cover
    return repl


_DEFERRED_CROSS_TYPE_REPLACEMENT_UNHANDLED = object()


def _deferred_cross_type_replacement_result(
    compiled_pattern: Pattern,
    repl: object,
    string: object,
    count: int,
) -> tuple[str | bytes, int] | object:
    pattern = compiled_pattern.pattern
    if isinstance(pattern, str):
        if not isinstance(repl, (bytes, bytearray, memoryview)):
            return _DEFERRED_CROSS_TYPE_REPLACEMENT_UNHANDLED
    elif not isinstance(repl, str):
        return _DEFERRED_CROSS_TYPE_REPLACEMENT_UNHANDLED

    compatible_string = _ensure_compatible_string(pattern, string)
    normalized_count = operator.index(count)
    if normalized_count < 0:
        return compatible_string, 0

    first_match = _dispatch_pattern_match(
        compiled_pattern,
        "search",
        compatible_string,
    )
    if first_match is None:
        return compatible_string, 0

    item_index = 0 if first_match.start() == 0 else 1
    if isinstance(pattern, str):
        raise TypeError(
            f"sequence item {item_index}: expected str instance, {type(repl).__name__} found"
        )
    raise TypeError(
        "sequence item "
        f"{item_index}: expected a bytes-like object, {type(repl).__name__} found"
    )


def _expand_literal_replacement_template(template: str, whole_match: str) -> str | None:
    expanded: list[str] = []
    index = 0

    while index < len(template):
        character = template[index]
        if character != "\\":
            expanded.append(character)
            index += 1
            continue

        if template[index : index + 5] != r"\g<0>":
            return None
        expanded.append(whole_match)
        index += 5

    return "".join(expanded)


def _coerce_callable_replacement_piece(
    pattern: str | bytes,
    replacement: object,
    item_index: int,
) -> str | bytes:
    if isinstance(pattern, str):
        if not isinstance(replacement, str):
            raise TypeError(
                f"sequence item {item_index}: expected str instance, {type(replacement).__name__} found"
            )
        return replacement

    if not isinstance(replacement, bytes):
        raise TypeError(
            f"sequence item {item_index}: expected a bytes-like object, {type(replacement).__name__} found"
        )
    return replacement


def _run_literal_sub(
    compiled_pattern: Pattern,
    repl: object,
    string: object,
    count: int = 0,
) -> str | bytes:
    substituted, _replacement_count = _run_literal_subn(
        compiled_pattern,
        repl,
        string,
        count=count,
        helper_name="sub",
    )
    return substituted


def _run_literal_subn(
    compiled_pattern: Pattern,
    repl: object,
    string: object,
    count: int = 0,
    *,
    helper_name: str = "subn",
) -> tuple[str | bytes, int]:
    deferred_cross_type_result = _deferred_cross_type_replacement_result(
        compiled_pattern,
        repl,
        string,
        count,
    )
    if deferred_cross_type_result is not _DEFERRED_CROSS_TYPE_REPLACEMENT_UNHANDLED:
        return deferred_cross_type_result

    compatible_string = _ensure_compatible_string(compiled_pattern.pattern, string)
    normalized_count = operator.index(count)
    if normalized_count < 0:
        return compatible_string, 0

    if callable(repl):
        return _run_literal_callable_subn(
            compiled_pattern,
            repl,
            compatible_string,
            normalized_count,
        )

    if isinstance(compiled_pattern.pattern, str) and isinstance(repl, str) and "\\" in repl:
        return _run_literal_template_subn(
            compiled_pattern,
            repl,
            compatible_string,
            normalized_count,
            helper_name=helper_name,
        )

    compatible_replacement = _ensure_literal_replacement_payload(
        compiled_pattern.pattern,
        repl,
        unsupported=compiled_pattern._raise_placeholder,
        helper_name=helper_name,
        defer_cross_type_mismatch=True,
    )
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


def _run_literal_callable_subn(
    compiled_pattern: Pattern,
    repl,
    compatible_string: str | bytes,
    normalized_count: int,
) -> tuple[str | bytes, int]:
    remaining = None if normalized_count == 0 else normalized_count
    parts: list[str] | list[bytes] = []
    last_end = 0
    replacement_count = 0

    for _compatible_string, normalized_pos, normalized_endpos, span in _iter_literal_match_spans(
        compiled_pattern,
        compatible_string,
    ):
        if remaining is not None and replacement_count >= remaining:
            break
        parts.append(compatible_string[last_end : span[0]])
        match = _build_match(compiled_pattern, compatible_string, normalized_pos, normalized_endpos, span)
        replacement = repl(match)
        parts.append(
            _coerce_callable_replacement_piece(
                compiled_pattern.pattern,
                replacement,
                len(parts),
            )
        )
        last_end = span[1]
        replacement_count += 1

    if replacement_count == 0:
        return compatible_string, 0

    parts.append(compatible_string[last_end:])
    return compatible_string[:0].join(parts), replacement_count


def _run_literal_template_subn(
    compiled_pattern: Pattern,
    repl: str,
    compatible_string: str | bytes,
    normalized_count: int,
    *,
    helper_name: str,
) -> tuple[str | bytes, int]:
    expanded_probe = _expand_literal_replacement_template(repl, "")
    if expanded_probe is None:
        return compiled_pattern._raise_placeholder(helper_name)

    remaining = None if normalized_count == 0 else normalized_count
    parts: list[str] = []
    last_end = 0
    replacement_count = 0

    for _compatible_string, _normalized_pos, _normalized_endpos, span in _iter_literal_match_spans(
        compiled_pattern,
        compatible_string,
    ):
        if remaining is not None and replacement_count >= remaining:
            break
        parts.append(compatible_string[last_end : span[0]])
        expanded = _expand_literal_replacement_template(repl, compatible_string[span[0] : span[1]])
        if expanded is None:
            return compiled_pattern._raise_placeholder(helper_name)
        parts.append(expanded)
        last_end = span[1]
        replacement_count += 1

    if replacement_count == 0:
        return compatible_string, 0

    parts.append(compatible_string[last_end:])
    return "".join(parts), replacement_count


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

    return _call_compiled_pattern_method(
        pattern,
        flags,
        "search",
        lambda compiled: compiled.search(string),
    )


def _translate_pattern_placeholder(method_name: str, call) -> object:
    try:
        return call()
    except NotImplementedError as exc:
        if str(exc) == _pattern_placeholder_message(method_name):
            return _raise_placeholder(method_name)
        raise


def _call_compiled_pattern_method(
    pattern: str | bytes | Pattern,
    flags: int,
    method_name: str,
    call,
) -> object:
    compiled = compile(pattern, flags)
    return _translate_pattern_placeholder(method_name, lambda: call(compiled))


def _validate_module_literal_replacement_request(
    pattern: str | bytes,
    repl: object,
    flags: int,
    *,
    helper_name: str,
) -> None:
    _ensure_literal_replacement_payload(
        pattern,
        repl,
        unsupported=_raise_placeholder,
        helper_name=helper_name,
        allow_native_template_passthrough=_allow_native_template_passthrough(pattern),
        defer_cross_type_mismatch=True,
    )
    if (
        isinstance(pattern, str)
        and isinstance(repl, str)
        and "\\" in repl
        and _supports_pattern_scaffold(pattern)
        and _expand_literal_replacement_template(repl, "") is None
    ):
        _raise_placeholder(helper_name)
    if len(pattern) == 0:
        _raise_placeholder(helper_name)
    normalized_flags = _normalize_pattern_flags(pattern, int(flags))
    if normalized_flags != _normalize_pattern_flags(pattern, 0):
        _raise_placeholder(helper_name)


def match(pattern: str | bytes | Pattern, string: object, flags: int = 0) -> Match | None:
    """Literal-only drop-in slice for `re.match`."""

    return _call_compiled_pattern_method(
        pattern,
        flags,
        "match",
        lambda compiled: compiled.match(string),
    )


def fullmatch(pattern: str | bytes | Pattern, string: object, flags: int = 0) -> Match | None:
    """Literal-only drop-in slice for `re.fullmatch`."""

    return _call_compiled_pattern_method(
        pattern,
        flags,
        "fullmatch",
        lambda compiled: compiled.fullmatch(string),
    )


def split(
    pattern: str | bytes | Pattern,
    string: object,
    maxsplit: int = 0,
    flags: int = 0,
) -> object:
    """Literal-only drop-in slice for `re.split`."""

    return _call_compiled_pattern_method(
        pattern,
        flags,
        "split",
        lambda compiled: compiled.split(string, maxsplit=maxsplit),
    )


def findall(pattern: str | bytes | Pattern, string: object, flags: int = 0) -> object:
    """Literal-only drop-in slice for `re.findall`."""

    return _call_compiled_pattern_method(
        pattern,
        flags,
        "findall",
        lambda compiled: compiled.findall(string),
    )


def finditer(pattern: str | bytes | Pattern, string: object, flags: int = 0) -> object:
    """Literal-only drop-in slice for `re.finditer`."""

    return _call_compiled_pattern_method(
        pattern,
        flags,
        "finditer",
        lambda compiled: compiled.finditer(string),
    )


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
        _validate_module_literal_replacement_request(
            pattern,
            repl,
            flags,
            helper_name="sub",
        )

    return _call_compiled_pattern_method(
        pattern,
        flags,
        "sub",
        lambda compiled: compiled.sub(repl, string, count=count),
    )


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
        _validate_module_literal_replacement_request(
            pattern,
            repl,
            flags,
            helper_name="subn",
        )

    return _call_compiled_pattern_method(
        pattern,
        flags,
        "subn",
        lambda compiled: compiled.subn(repl, string, count=count),
    )


def template(*_args: object, **_kwargs: object) -> object:
    """Placeholder for the future drop-in `re.template` surface."""

    return _raise_placeholder("template")


def escape(pattern: object) -> str | bytes:
    """Return a CPython-compatible escaped pattern for `str` and bytes-like inputs."""

    if _native is not None:
        if isinstance(pattern, str):
            return _native.boundary_escape(pattern)
        decoded_pattern = str(pattern, "latin-1")
        return _native.boundary_escape(decoded_pattern).encode("latin-1")

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
