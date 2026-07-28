"""An independently written C++ candidate for Python's public ``re`` API.

This module is a candidate, not a qualified replacement. Every matching
operation is performed by ``candidates._cpp_bridge`` and its owned C++ engine.
"""

from __future__ import annotations

import enum
import operator
import sys
import types
import warnings

from candidates import _cpp_bridge


__version__ = "2.2.1"
_MISSING = object()
_MAX_INDEX = sys.maxsize
_MIN_INDEX = -sys.maxsize - 1


class RegexFlag(enum.IntFlag):
    NOFLAG = 0
    ASCII = A = 256
    IGNORECASE = I = 2
    LOCALE = L = 4
    UNICODE = U = 32
    MULTILINE = M = 8
    DOTALL = S = 16
    VERBOSE = X = 64
    DEBUG = 128
    _numeric_repr_ = hex

    def __repr__(self):
        number = int(self)
        if not number:
            return "re.NOFLAG"
        ordered = (
            (256, "ASCII"),
            (2, "IGNORECASE"),
            (4, "LOCALE"),
            (32, "UNICODE"),
            (8, "MULTILINE"),
            (16, "DOTALL"),
            (64, "VERBOSE"),
            (128, "DEBUG"),
        )
        parts = ["re." + name for flag, name in ordered if number & flag]
        unknown = number & ~sum(flag for flag, _ in ordered)
        if unknown:
            parts.append(hex(unknown))
        return "|".join(parts)

    __str__ = __repr__


A = ASCII = RegexFlag.ASCII
I = IGNORECASE = RegexFlag.IGNORECASE
L = LOCALE = RegexFlag.LOCALE
M = MULTILINE = RegexFlag.MULTILINE
S = DOTALL = RegexFlag.DOTALL
X = VERBOSE = RegexFlag.VERBOSE
U = UNICODE = RegexFlag.UNICODE
DEBUG = RegexFlag.DEBUG
NOFLAG = RegexFlag.NOFLAG


class PatternError(Exception):
    def __init__(self, msg, pattern=None, pos=None):
        self.msg = msg
        self.pattern = pattern
        self.pos = pos
        self.lineno = None
        self.colno = None
        message = msg
        if pattern is not None and pos is not None:
            source = pattern.decode("latin1") if isinstance(pattern, bytes) else pattern
            self.lineno = source.count("\n", 0, pos) + 1
            self.colno = pos - source.rfind("\n", 0, pos)
            message = f"{msg} at position {pos}"
            if "\n" in source:
                message += f" (line {self.lineno}, column {self.colno})"
        super().__init__(message)


error = PatternError


def _index(value):
    result = operator.index(value)
    if result < _MIN_INDEX or result > _MAX_INDEX:
        raise OverflowError("Python int too large to convert to C ssize_t")
    return result


def _count(value):
    return _index(value)


def _flags(value):
    number = operator.index(value)
    if number < 0 or number > 0xFFFFFFFF:
        raise OverflowError("regular-expression flags exceed 32 bits")
    return number


def _error_from_native(exc, pattern):
    values = exc.args
    message = values[0] if values else "invalid regular expression"
    position = values[1] if len(values) > 1 else None
    return PatternError(message, pattern, position)


def _slice_subject(subject, begin, end):
    if isinstance(subject, str):
        return subject[begin:end]
    if isinstance(subject, bytes):
        return subject[begin:end]
    return memoryview(subject).cast("B")[begin:end].tobytes()


class Match:
    __slots__ = (
        "_pattern",
        "_string",
        "_token",
        "_spans",
        "_lastindex",
        "_pos",
        "_endpos",
    )

    def __init__(self, pattern, token, spans, lastindex, pos, endpos):
        self._pattern = pattern
        self._string = token.string
        self._token = token
        self._spans = tuple(spans)
        self._lastindex = lastindex
        self._pos = pos
        self._endpos = endpos

    @property
    def re(self):
        return self._pattern

    @property
    def string(self):
        return self._string

    @property
    def pos(self):
        return self._pos

    @property
    def endpos(self):
        return self._endpos

    @property
    def lastindex(self):
        return self._lastindex

    @property
    def lastgroup(self):
        if self._lastindex is None:
            return None
        for name, index in self._pattern.groupindex.items():
            if index == self._lastindex:
                return name
        return None

    @property
    def regs(self):
        return self._spans

    @classmethod
    def __class_getitem__(cls, item):
        return types.GenericAlias(cls, item)

    def _group_number(self, value):
        if isinstance(value, str):
            try:
                return self._pattern.groupindex[value]
            except KeyError:
                raise IndexError("no such group") from None
        try:
            number = operator.index(value)
        except TypeError:
            raise IndexError("no such group") from None
        if number < 0 or number >= len(self._spans):
            raise IndexError("no such group")
        return number

    def _one_group(self, value):
        begin, end = self._spans[self._group_number(value)]
        if begin == -1:
            return None
        return _slice_subject(self._string, begin, end)

    def group(self, *groups):
        if not groups:
            return self._one_group(0)
        if len(groups) == 1:
            return self._one_group(groups[0])
        return tuple(self._one_group(value) for value in groups)

    def __getitem__(self, group):
        return self._one_group(group)

    def groups(self, default=None):
        return tuple(
            default if begin == -1 else _slice_subject(self._string, begin, end)
            for begin, end in self._spans[1:]
        )

    def groupdict(self, default=None):
        return {
            name: (
                default if self._spans[index][0] == -1
                else _slice_subject(self._string, *self._spans[index])
            )
            for name, index in self._pattern.groupindex.items()
        }

    def start(self, group=0):
        return self._spans[self._group_number(group)][0]

    def end(self, group=0):
        return self._spans[self._group_number(group)][1]

    def span(self, group=0):
        return self._spans[self._group_number(group)]

    def expand(self, template):
        return _expand_replacement(_replacement_tokens(template, self._pattern), self)

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self

    def __reduce__(self):
        raise TypeError("cannot pickle 're.Match' object")

    def __repr__(self):
        return f"<re.Match object; span={self.span()}, match={self.group()!r}>"


class _PatternScanner:
    __slots__ = (
        "_pattern",
        "_subject",
        "_cursor",
        "_end",
        "_origin",
        "_empty",
        "_finished",
    )

    def __init__(self, pattern, token, start, end):
        self._pattern = pattern
        self._subject = token
        self._cursor = start
        self._end = end
        self._origin = start
        self._empty = False
        self._finished = False

    @property
    def pattern(self):
        return self._pattern

    def _next(self, mode):
        if self._finished:
            return None
        result = self._pattern._run(
            self._subject,
            self._cursor,
            self._end,
            mode,
            self._empty,
            self._origin,
        )
        if result is None:
            if mode == 1 or self._cursor >= self._end:
                self._finished = True
                return None
            if self._empty:
                self._cursor += 1
                self._empty = False
                result = self._pattern._run(
                    self._subject,
                    self._cursor,
                    self._end,
                    mode,
                    False,
                    self._origin,
                )
            if result is None:
                self._finished = True
                return None
        begin, end = result.span()
        self._cursor = end
        self._empty = begin == end
        return result

    def search(self):
        return self._next(0)

    def match(self):
        return self._next(1)


class Pattern:
    __slots__ = (
        "_pattern",
        "_flags",
        "_handle",
        "_groups",
        "_groupindex",
        "__weakref__",
    )

    def __init__(self, pattern, flags, handle, groups, names):
        object.__setattr__(self, "_pattern", pattern)
        object.__setattr__(self, "_flags", flags)
        object.__setattr__(self, "_handle", handle)
        object.__setattr__(self, "_groups", groups)
        object.__setattr__(self, "_groupindex", types.MappingProxyType(dict(names)))

    @property
    def pattern(self):
        return self._pattern

    @property
    def flags(self):
        return self._flags

    @property
    def groups(self):
        return self._groups

    @property
    def groupindex(self):
        return self._groupindex

    @classmethod
    def __class_getitem__(cls, item):
        return types.GenericAlias(cls, item)

    def __setattr__(self, name, value):
        raise AttributeError("readonly attribute")

    def __delattr__(self, name):
        raise AttributeError("readonly attribute")

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self

    def __reduce__(self):
        return compile, (self._pattern, self._flags)

    def __hash__(self):
        return hash((type(self._pattern), self._pattern, self._flags))

    def __eq__(self, other):
        if not isinstance(other, Pattern):
            return NotImplemented
        return (
            type(self._pattern) is type(other._pattern)
            and self._pattern == other._pattern
            and self._flags == other._flags
        )

    def __repr__(self):
        flags = self._flags
        if isinstance(self._pattern, str):
            flags &= ~int(UNICODE)
        suffix = "" if not flags else ", " + repr(RegexFlag(flags))
        return f"re.compile({self._pattern!r}{suffix})"

    def _subject(self, string):
        return _cpp_bridge.subject(string, isinstance(self._pattern, bytes))

    @staticmethod
    def _window(token, pos, endpos):
        start = _index(pos)
        end = _index(endpos)
        length = token.length
        return max(0, min(start, length)), max(0, min(end, length))

    def _run(self, token, pos, endpos, mode, nonempty, original_pos=None):
        outcome = _cpp_bridge.run(
            self._handle,
            token,
            pos,
            endpos,
            mode,
            nonempty,
        )
        if outcome is None:
            return None
        spans, lastindex = outcome
        return Match(
            self,
            token,
            spans,
            lastindex,
            pos if original_pos is None else original_pos,
            endpos,
        )

    def search(self, string, pos=0, endpos=_MAX_INDEX):
        token = self._subject(string)
        start, end = self._window(token, pos, endpos)
        return self._run(token, start, end, 0, False)

    def match(self, string, pos=0, endpos=_MAX_INDEX):
        token = self._subject(string)
        start, end = self._window(token, pos, endpos)
        return self._run(token, start, end, 1, False)

    def fullmatch(self, string, pos=0, endpos=_MAX_INDEX):
        token = self._subject(string)
        start, end = self._window(token, pos, endpos)
        return self._run(token, start, end, 2, False)

    def scanner(self, string, pos=0, endpos=_MAX_INDEX):
        token = self._subject(string)
        start, end = self._window(token, pos, endpos)
        return _PatternScanner(self, token, start, end)

    def finditer(self, string, pos=0, endpos=_MAX_INDEX):
        return iter(self.scanner(string, pos, endpos).search, None)

    def findall(self, string, pos=0, endpos=_MAX_INDEX):
        matches = self.finditer(string, pos, endpos)
        if self._groups == 0:
            return [match.group() for match in matches]
        if self._groups == 1:
            empty = "" if isinstance(self._pattern, str) else b""
            return [empty if match.group(1) is None else match.group(1) for match in matches]
        empty = "" if isinstance(self._pattern, str) else b""
        return [
            tuple(empty if value is None else value for value in match.groups())
            for match in matches
        ]

    def split(self, string, maxsplit=0):
        maximum = _count(maxsplit)
        if maximum < 0:
            return [string]
        token = self._subject(string)
        scanner = _PatternScanner(self, token, 0, token.length)
        pieces = []
        previous = 0
        completed = 0
        while maximum == 0 or completed < maximum:
            match = scanner.search()
            if match is None:
                break
            begin, end = match.span()
            pieces.append(_slice_subject(string, previous, begin))
            pieces.extend(match.groups())
            previous = end
            completed += 1
        pieces.append(_slice_subject(string, previous, token.length))
        return pieces

    def sub(self, repl, string, count=0):
        return self.subn(repl, string, count)[0]

    def subn(self, repl, string, count=0):
        maximum = _count(count)
        token = self._subject(string)
        is_text = isinstance(self._pattern, str)
        if callable(repl):
            replacement = repl
            tokens = None
        else:
            replacement = None
            tokens = _replacement_tokens(repl, self)
        if maximum < 0:
            return _slice_subject(string, 0, token.length), 0
        scanner = _PatternScanner(self, token, 0, token.length)
        pieces = []
        previous = 0
        completed = 0
        while maximum == 0 or completed < maximum:
            match = scanner.search()
            if match is None:
                break
            begin, end = match.span()
            pieces.append(_slice_subject(string, previous, begin))
            value = (
                replacement(match)
                if replacement is not None
                else _expand_replacement(tokens, match)
            )
            if is_text:
                if not isinstance(value, str):
                    raise TypeError("sequence item: expected str instance")
            elif not isinstance(value, bytes):
                if isinstance(value, (bytearray, memoryview)):
                    value = bytes(value)
                else:
                    raise TypeError("sequence item: expected a bytes-like object")
            pieces.append(value)
            previous = end
            completed += 1
        pieces.append(_slice_subject(string, previous, token.length))
        separator = "" if is_text else b""
        return separator.join(pieces), completed


_CACHE = {}
_MAXCACHE = 512


def compile(pattern, flags=0):
    requested = _flags(flags)
    if isinstance(pattern, Pattern):
        if requested:
            raise ValueError("cannot process flags argument with a compiled pattern")
        return pattern
    if not isinstance(pattern, (str, bytes)):
        raise TypeError("first argument must be string or compiled pattern")
    if isinstance(pattern, str) and requested & int(LOCALE):
        raise ValueError("cannot use LOCALE flag with a str pattern")
    if isinstance(pattern, bytes) and requested & int(UNICODE):
        raise ValueError("cannot use UNICODE flag with a bytes pattern")
    if requested & int(ASCII) and requested & int(LOCALE):
        raise ValueError("ASCII and LOCALE flags are incompatible")
    if requested & int(ASCII) and requested & int(UNICODE):
        raise ValueError("ASCII and UNICODE flags are incompatible")
    key = (type(pattern), pattern, requested)
    if not requested & int(DEBUG):
        cached = _CACHE.get(key)
        if cached is not None:
            return cached
    effective = requested
    if isinstance(pattern, str) and not requested & int(ASCII):
        effective |= int(UNICODE)
    try:
        handle, groups, names, actual_flags = _cpp_bridge.compile(pattern, effective)
    except _cpp_bridge.PatternSyntaxError as exc:
        raise _error_from_native(exc, pattern) from None
    result = Pattern(pattern, actual_flags, handle, groups, names)
    if not requested & int(DEBUG):
        if len(_CACHE) >= _MAXCACHE:
            del _CACHE[next(iter(_CACHE))]
        _CACHE[key] = result
    return result


def purge():
    _CACHE.clear()


def search(pattern, string, flags=0):
    return compile(pattern, flags).search(string)


def match(pattern, string, flags=0):
    return compile(pattern, flags).match(string)


def fullmatch(pattern, string, flags=0):
    return compile(pattern, flags).fullmatch(string)


def findall(pattern, string, flags=0):
    return compile(pattern, flags).findall(string)


def finditer(pattern, string, flags=0):
    return compile(pattern, flags).finditer(string)


def _deprecated_positional(argument, supplied):
    if supplied:
        warnings.warn(
            f"'{argument}' is passed as positional argument",
            DeprecationWarning,
            stacklevel=3,
        )


def split(pattern, string, *args, maxsplit=_MISSING, flags=_MISSING):
    if len(args) > 2:
        raise TypeError("split() takes at most 4 arguments")
    _deprecated_positional("maxsplit", args)
    if args:
        if maxsplit is not _MISSING:
            raise TypeError("split() got multiple values for argument 'maxsplit'")
        maxsplit = args[0]
    if len(args) == 2:
        if flags is not _MISSING:
            raise TypeError("split() got multiple values for argument 'flags'")
        flags = args[1]
    return compile(
        pattern,
        0 if flags is _MISSING else flags,
    ).split(string, 0 if maxsplit is _MISSING else maxsplit)


def sub(pattern, repl, string, *args, count=_MISSING, flags=_MISSING):
    if len(args) > 2:
        raise TypeError("sub() takes at most 5 arguments")
    _deprecated_positional("count", args)
    if args:
        if count is not _MISSING:
            raise TypeError("sub() got multiple values for argument 'count'")
        count = args[0]
    if len(args) == 2:
        if flags is not _MISSING:
            raise TypeError("sub() got multiple values for argument 'flags'")
        flags = args[1]
    return compile(
        pattern,
        0 if flags is _MISSING else flags,
    ).sub(repl, string, 0 if count is _MISSING else count)


def subn(pattern, repl, string, *args, count=_MISSING, flags=_MISSING):
    if len(args) > 2:
        raise TypeError("subn() takes at most 5 arguments")
    _deprecated_positional("count", args)
    if args:
        if count is not _MISSING:
            raise TypeError("subn() got multiple values for argument 'count'")
        count = args[0]
    if len(args) == 2:
        if flags is not _MISSING:
            raise TypeError("subn() got multiple values for argument 'flags'")
        flags = args[1]
    return compile(
        pattern,
        0 if flags is _MISSING else flags,
    ).subn(repl, string, 0 if count is _MISSING else count)


_SPECIAL_CHARACTERS = "()[]{}?*+-|^$\\.&~# \t\n\r\v\f"
_ESCAPE_TABLE = {ord(value): "\\" + value for value in _SPECIAL_CHARACTERS}


def escape(pattern):
    if isinstance(pattern, str):
        return pattern.translate(_ESCAPE_TABLE)
    try:
        raw = memoryview(pattern).cast("B").tobytes()
    except TypeError:
        raise TypeError("decoding to str: need a bytes-like object") from None
    return raw.decode("latin1").translate(_ESCAPE_TABLE).encode("latin1")


_REPLACEMENT_ESCAPES = {
    "a": "\a",
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
    "v": "\v",
    "\\": "\\",
}


def _replacement_error(message, original, position):
    raise PatternError(message, original, position)


def _replacement_group(pattern, value, original, position):
    if value.isdecimal() and value.isascii():
        number = int(value)
    else:
        try:
            number = pattern.groupindex[value]
        except KeyError:
            raise IndexError(f"unknown group name {value!r}") from None
    if number > pattern.groups:
        _replacement_error(f"invalid group reference {number}", original, position)
    return number


def _replacement_tokens(value, pattern):
    text_pattern = isinstance(pattern.pattern, str)
    if text_pattern:
        if not isinstance(value, str):
            raise TypeError("cannot use a bytes replacement on a string pattern")
        original = value
        source = value
    else:
        if isinstance(value, str):
            raise TypeError("cannot use a string replacement on a bytes pattern")
        try:
            original = bytes(memoryview(value).cast("B"))
        except TypeError:
            raise TypeError("expected a bytes-like replacement") from None
        source = original.decode("latin1")
    tokens = []
    literal_start = 0
    index = 0
    length = len(source)
    while index < length:
        if source[index] != "\\":
            index += 1
            continue
        if literal_start < index:
            literal = source[literal_start:index]
            tokens.append(literal if text_pattern else literal.encode("latin1"))
        opening = index
        index += 1
        if index >= length:
            _replacement_error("bad escape (end of pattern)", original, opening)
        escaped = source[index]
        index += 1
        if escaped == "g":
            if index >= length or source[index] != "<":
                _replacement_error("missing <", original, index)
            index += 1
            begin = index
            while index < length and source[index] != ">":
                index += 1
            if index == length:
                _replacement_error("missing >, unterminated name", original, begin)
            name = source[begin:index]
            index += 1
            if not name:
                _replacement_error("missing group name", original, begin)
            tokens.append((
                _replacement_group(pattern, name, original, begin),
            ))
        elif escaped in "0123456789":
            if escaped == "0":
                digits = escaped
                for _ in range(2):
                    if index < length and source[index] in "01234567":
                        digits += source[index]
                        index += 1
                    else:
                        break
                character = chr(int(digits, 8))
                tokens.append(character if text_pattern else character.encode("latin1"))
            elif (
                escaped in "01234567"
                and index + 1 < length
                and source[index] in "01234567"
                and source[index + 1] in "01234567"
            ):
                digits = escaped + source[index:index + 2]
                index += 2
                number = int(digits, 8)
                if number > 0xFF:
                    _replacement_error(
                        f"octal escape value \\{digits} outside of range 0-0o377",
                        original,
                        opening,
                    )
                character = chr(number)
                tokens.append(character if text_pattern else bytes((number,)))
            else:
                digits = escaped
                if index < length and source[index].isascii() and source[index].isdigit():
                    digits += source[index]
                    index += 1
                tokens.append((
                    _replacement_group(pattern, digits, original, opening + 1),
                ))
        elif escaped in _REPLACEMENT_ESCAPES:
            character = _REPLACEMENT_ESCAPES[escaped]
            tokens.append(character if text_pattern else character.encode("latin1"))
        elif escaped.isascii() and escaped.isalpha():
            _replacement_error(f"bad escape \\{escaped}", original, opening)
        else:
            character = "\\" + escaped
            tokens.append(character if text_pattern else character.encode("latin1"))
        literal_start = index
    if literal_start < length:
        literal = source[literal_start:]
        tokens.append(literal if text_pattern else literal.encode("latin1"))
    return tuple(tokens)


def _expand_replacement(tokens, match):
    text_pattern = isinstance(match.re.pattern, str)
    empty = "" if text_pattern else b""
    pieces = []
    for value in tokens:
        if isinstance(value, tuple):
            group = match.group(value[0])
            pieces.append(empty if group is None else group)
        else:
            pieces.append(value)
    return empty.join(pieces)


class Scanner:
    def __init__(self, lexicon, flags=0):
        self.lexicon = lexicon
        self.flags = _flags(flags)
        self._patterns = []
        expressions = []
        expected_type = None
        for item in lexicon:
            try:
                expression, action = item
            except (TypeError, ValueError):
                raise TypeError("scanner lexicon entries must contain a pattern and an action") from None
            if not isinstance(expression, (str, bytes)):
                raise TypeError("scanner patterns must be strings or bytes")
            if expected_type is None:
                expected_type = type(expression)
            elif type(expression) is not expected_type:
                raise TypeError("scanner patterns must all have the same type")
            expressions.append(expression)
            self._patterns.append((compile(expression, self.flags), action))
        if expected_type is bytes:
            combined = b"|".join(b"(" + value + b")" for value in expressions)
        else:
            combined = "|".join("(" + value + ")" for value in expressions)
        self.scanner = compile(combined, self.flags)

    def scan(self, string):
        if not self._patterns:
            return [], string
        first, _ = self._patterns[0]
        token = first._subject(string)
        position = 0
        results = []
        while position < token.length:
            selected = None
            selected_action = None
            for pattern, action in self._patterns:
                found = pattern._run(token, position, token.length, 1, False)
                if found is not None:
                    selected = found
                    selected_action = action
                    break
            if selected is None or selected.end() == position:
                break
            if selected_action is not None:
                if callable(selected_action):
                    self.match = selected
                    value = selected_action(self, selected.group())
                else:
                    value = selected_action
                if value is not None:
                    results.append(value)
            position = selected.end()
        return results, _slice_subject(string, position, token.length)


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
    "PatternError",
]
