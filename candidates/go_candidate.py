"""Python's public matching interface backed only by the owned Go engine.

This is an experimental candidate. Compatibility, safe native construction,
and performance must be established by separately frozen experiments before it
can be considered a replacement or selected as the public rebar module.
"""

from __future__ import annotations

import copyreg
import enum
import operator
import types
import warnings

from candidates import _go_bridge


__version__ = "2.2.1"

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

_MAX_INDEX = (1 << 63) - 1
_MIN_INDEX = -(1 << 63)


class RegexFlag(enum.IntFlag, boundary=enum.KEEP):
    """The public Python 3.14 regular-expression flag values."""

    NOFLAG = 0
    ASCII = A = 256
    IGNORECASE = I = 2
    LOCALE = L = 4
    MULTILINE = M = 8
    DOTALL = S = 16
    UNICODE = U = 32
    VERBOSE = X = 64
    DEBUG = 128
    _numeric_repr_ = hex

    def __repr__(self):
        value = int(self)
        if value == 0:
            return "re.NOFLAG"
        spellings = (
            (256, "ASCII"),
            (2, "IGNORECASE"),
            (4, "LOCALE"),
            (8, "MULTILINE"),
            (16, "DOTALL"),
            (32, "UNICODE"),
            (64, "VERBOSE"),
            (128, "DEBUG"),
        )
        pieces = [
            "re." + spelling
            for bit, spelling in spellings
            if value & bit
        ]
        unknown = value & ~sum(bit for bit, _ in spellings)
        if unknown:
            pieces.append(hex(unknown))
        return "|".join(pieces)

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
    """A pattern error with Python's public source-position attributes."""

    def __init__(self, msg, pattern=None, pos=None):
        self.msg = msg
        self.pattern = pattern
        self.pos = pos
        if pattern is None or pos is None:
            self.lineno = None
            self.colno = None
            explanation = msg
        else:
            newline = "\n" if isinstance(pattern, str) else b"\n"
            self.lineno = pattern.count(newline, 0, pos) + 1
            self.colno = pos - pattern.rfind(newline, 0, pos)
            explanation = f"{msg} at position {pos}"
            if newline in pattern:
                explanation += (
                    f" (line {self.lineno}, column {self.colno})"
                )
        super().__init__(explanation)


error = PatternError


def _as_index(value):
    result = operator.index(value)
    if not _MIN_INDEX <= result <= _MAX_INDEX:
        raise OverflowError(
            "Python int too large to convert to C ssize_t"
        )
    return result


def _as_flags(value):
    result = operator.index(value)
    if result < 0 or result > 0xFFFFFFFF:
        raise OverflowError(
            "regular-expression flags exceed 32 bits"
        )
    return result


def _subject_piece(subject, beginning, end):
    if isinstance(subject, (str, bytes)):
        return subject[beginning:end]
    with memoryview(subject) as original:
        with original.cast("B") as flat:
            return flat[beginning:end].tobytes()


class Match:
    """One match produced by the independently owned Go program."""

    __slots__ = (
        "_pattern",
        "_subject",
        "_spans",
        "_lastindex",
        "_pos",
        "_endpos",
        "__weakref__",
    )

    def __new__(cls, *args, **kwargs):
        del args, kwargs
        raise TypeError("cannot create 're.Match' instances")

    @classmethod
    def _create(
        cls,
        pattern,
        subject,
        spans,
        lastindex,
        pos,
        endpos,
    ):
        result = object.__new__(cls)
        result._pattern = pattern
        result._subject = subject
        result._spans = spans
        result._lastindex = lastindex
        result._pos = pos
        result._endpos = endpos
        return result

    @classmethod
    def __class_getitem__(cls, value):
        return types.GenericAlias(cls, value)

    @property
    def re(self):
        return self._pattern

    @property
    def string(self):
        return self._subject

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
        for name, number in self._pattern.groupindex.items():
            if number == self._lastindex:
                return name
        return None

    @property
    def regs(self):
        return self._spans

    def _group_index(self, value):
        if isinstance(value, str):
            try:
                return self._pattern.groupindex[value]
            except KeyError:
                raise IndexError("no such group") from None
        try:
            number = operator.index(value)
        except TypeError:
            raise IndexError("no such group") from None
        if not 0 <= number < len(self._spans):
            raise IndexError("no such group")
        return number

    def _group(self, value):
        beginning, end = self._spans[self._group_index(value)]
        if beginning < 0:
            return None
        return _subject_piece(self._subject, beginning, end)

    def group(self, *values):
        if len(values) == 0:
            return self._group(0)
        if len(values) == 1:
            return self._group(values[0])
        return tuple(self._group(value) for value in values)

    def __getitem__(self, value):
        return self._group(value)

    def groups(self, default=None):
        return tuple(
            default
            if beginning < 0
            else _subject_piece(self._subject, beginning, end)
            for beginning, end in self._spans[1:]
        )

    def groupdict(self, default=None):
        return {
            name: (
                default
                if self._spans[number][0] < 0
                else _subject_piece(
                    self._subject,
                    *self._spans[number],
                )
            )
            for name, number in self._pattern.groupindex.items()
        }

    def start(self, group=0):
        return self._spans[self._group_index(group)][0]

    def end(self, group=0):
        return self._spans[self._group_index(group)][1]

    def span(self, group=0):
        return self._spans[self._group_index(group)]

    def expand(self, template):
        return _render_template(
            _parse_template(self._pattern, template),
            self,
        )

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        del memo
        return self

    def __reduce__(self):
        raise TypeError("cannot pickle 're.Match' object")

    def __repr__(self):
        return (
            f"<re.Match object; span={self.span()}, "
            f"match={self.group()!r}>"
        )


class _PatternScanner:
    """Stateful search using one interpreter-local native program."""

    __slots__ = (
        "_pattern",
        "_subject",
        "_position",
        "_endpos",
        "_must_advance",
        "_finished",
    )

    def __init__(self, pattern, subject, pos, endpos):
        self._pattern = pattern
        self._subject = subject
        self._position = pos
        self._endpos = endpos
        self._must_advance = False
        self._finished = False

    @property
    def pattern(self):
        return self._pattern

    def _next(self, anchored):
        if self._finished:
            return None
        result = self._pattern._run(
            self._subject,
            self._position,
            self._endpos,
            anchored=anchored,
            fullmatch=False,
            reject_empty=self._must_advance,
        )
        if result is None:
            self._finished = True
            return None
        beginning, end = result.span()
        self._position = end
        self._must_advance = beginning == end
        return result

    def search(self):
        return self._next(False)

    def match(self):
        return self._next(True)


class _MatchIterator:
    __slots__ = ("_scanner",)

    def __init__(self, scanner):
        self._scanner = scanner

    def __iter__(self):
        return self

    def __next__(self):
        result = self._scanner.search()
        if result is None:
            raise StopIteration
        return result


class Pattern:
    """An immutable Python pattern backed by one owned Go program."""

    __slots__ = (
        "_native",
        "_source",
        "_flags",
        "_groups",
        "_groupindex",
        "__weakref__",
    )

    def __new__(cls, *args, **kwargs):
        del args, kwargs
        raise TypeError("cannot create 're.Pattern' instances")

    @classmethod
    def _create(cls, source, native):
        result = object.__new__(cls)
        result._native = native
        result._source = source
        result._flags = native.flags
        result._groups = native.groups
        result._groupindex = types.MappingProxyType(
            dict(native.groupindex)
        )
        return result

    @classmethod
    def __class_getitem__(cls, value):
        return types.GenericAlias(cls, value)

    @property
    def pattern(self):
        return self._source

    @property
    def flags(self):
        return self._flags

    @property
    def groups(self):
        return self._groups

    @property
    def groupindex(self):
        return self._groupindex

    def _run(
        self,
        string,
        pos,
        endpos,
        *,
        anchored,
        fullmatch,
        reject_empty=False,
    ):
        result = _go_bridge.execute(
            self._native,
            string,
            _as_index(pos),
            _as_index(endpos),
            anchored,
            fullmatch,
            reject_empty,
        )
        if result is None:
            return None
        spans, lastindex, beginning, end = result
        return Match._create(
            self,
            string,
            spans,
            lastindex,
            beginning,
            end,
        )

    def search(self, string, pos=0, endpos=_MAX_INDEX):
        return self._run(
            string,
            pos,
            endpos,
            anchored=False,
            fullmatch=False,
        )

    def match(self, string, pos=0, endpos=_MAX_INDEX):
        return self._run(
            string,
            pos,
            endpos,
            anchored=True,
            fullmatch=False,
        )

    def fullmatch(self, string, pos=0, endpos=_MAX_INDEX):
        return self._run(
            string,
            pos,
            endpos,
            anchored=True,
            fullmatch=True,
        )

    def scanner(self, string, pos=0, endpos=_MAX_INDEX):
        return _PatternScanner(
            self,
            string,
            _as_index(pos),
            _as_index(endpos),
        )

    def finditer(self, string, pos=0, endpos=_MAX_INDEX):
        return _MatchIterator(self.scanner(string, pos, endpos))

    def findall(self, string, pos=0, endpos=_MAX_INDEX):
        empty = "" if isinstance(self._source, str) else b""
        matches = []
        for found in self.finditer(string, pos, endpos):
            if self._groups == 0:
                matches.append(found.group())
            elif self._groups == 1:
                value = found.group(1)
                matches.append(empty if value is None else value)
            else:
                matches.append(found.groups(empty))
        return matches

    def split(self, string, maxsplit=0):
        maximum = _as_index(maxsplit)
        if maximum < 0:
            return [_subject_piece(string, 0, _MAX_INDEX)]
        iterator = self.scanner(string)
        pieces = []
        previous = 0
        completed = 0
        while maximum == 0 or completed < maximum:
            found = iterator.search()
            if found is None:
                break
            beginning, end = found.span()
            pieces.append(
                _subject_piece(string, previous, beginning)
            )
            pieces.extend(found.groups())
            previous = end
            completed += 1
        pieces.append(_subject_piece(string, previous, _MAX_INDEX))
        return pieces

    def sub(self, repl, string, count=0):
        return self.subn(repl, string, count)[0]

    def subn(self, repl, string, count=0):
        maximum = _as_index(count)
        if maximum < 0:
            return _subject_piece(string, 0, _MAX_INDEX), 0
        text_mode = isinstance(self._source, str)
        action = repl if callable(repl) else None
        template = (
            None
            if action is not None
            else _parse_template(self, repl)
        )
        iterator = self.scanner(string)
        previous = 0
        completed = 0
        pieces = []
        while maximum == 0 or completed < maximum:
            found = iterator.search()
            if found is None:
                break
            beginning, end = found.span()
            pieces.append(
                _subject_piece(string, previous, beginning)
            )
            replacement = (
                action(found)
                if action is not None
                else _render_template(template, found)
            )
            if text_mode:
                if not isinstance(replacement, str):
                    raise TypeError(
                        "sequence item: expected str instance"
                    )
            elif not isinstance(replacement, bytes):
                try:
                    replacement = bytes(
                        memoryview(replacement).cast("B")
                    )
                except (TypeError, BufferError):
                    raise TypeError(
                        "sequence item: expected a bytes-like object"
                    ) from None
            pieces.append(replacement)
            previous = end
            completed += 1
        pieces.append(_subject_piece(string, previous, _MAX_INDEX))
        separator = "" if text_mode else b""
        return separator.join(pieces), completed

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        del memo
        return self

    def __reduce__(self):
        return _compile, (self._source, self._flags)

    def __eq__(self, other):
        if not isinstance(other, Pattern):
            return NotImplemented
        return (
            type(self._source) is type(other._source)
            and self._source == other._source
            and self._flags == other._flags
        )

    def __hash__(self):
        return hash(
            (type(self._source), self._source, self._flags)
        )

    def __repr__(self):
        flags = self._flags
        if isinstance(self._source, str):
            flags &= ~int(UNICODE)
        if flags:
            return (
                f"re.compile({self._source!r}, "
                f"{RegexFlag(flags)!r})"
            )
        return f"re.compile({self._source!r})"


_cache = {}
_cache2 = {}
_MAXCACHE = 512
_MAXCACHE2 = 256
_template_cache = {}


def _compile(pattern, flags=0):
    requested = _as_flags(flags)
    if isinstance(pattern, Pattern):
        if requested:
            raise ValueError(
                "cannot process flags argument with a compiled pattern"
            )
        return pattern
    if not isinstance(pattern, (str, bytes)):
        raise TypeError(
            "first argument must be string or compiled pattern"
        )
    if isinstance(pattern, str) and requested & int(LOCALE):
        raise ValueError(
            "cannot use LOCALE flag with a str pattern"
        )
    if isinstance(pattern, bytes) and requested & int(UNICODE):
        raise ValueError(
            "cannot use UNICODE flag with a bytes pattern"
        )
    if requested & int(ASCII) and requested & int(LOCALE):
        raise ValueError("ASCII and LOCALE flags are incompatible")
    if requested & int(ASCII) and requested & int(UNICODE):
        raise ValueError("ASCII and UNICODE flags are incompatible")

    key = (type(pattern), pattern, requested)
    cached = _cache2.get(key)
    if cached is not None:
        return cached
    cached = _cache.pop(key, None)
    if cached is None:
        effective = requested
        if isinstance(pattern, str) and not requested & int(ASCII):
            effective |= int(UNICODE)
        try:
            native = _go_bridge.compile(pattern, effective)
        except _go_bridge.NativePatternError as exc:
            message = (
                exc.args[0]
                if exc.args
                else "invalid regular expression"
            )
            position = (
                exc.args[1]
                if len(exc.args) > 1
                else None
            )
            raise PatternError(
                message,
                pattern,
                position,
            ) from None
        cached = Pattern._create(pattern, native)
        if requested & int(DEBUG):
            return cached
        if len(_cache) >= _MAXCACHE:
            try:
                del _cache[next(iter(_cache))]
            except (StopIteration, RuntimeError, KeyError):
                pass
    _cache[key] = cached
    if len(_cache2) >= _MAXCACHE2:
        try:
            del _cache2[next(iter(_cache2))]
        except (StopIteration, RuntimeError, KeyError):
            pass
    _cache2[key] = cached
    return cached


def compile(pattern, flags=0):
    return _compile(pattern, flags)


def purge():
    _cache.clear()
    _cache2.clear()
    _template_cache.clear()


def search(pattern, string, flags=0):
    return _compile(pattern, flags).search(string)


def match(pattern, string, flags=0):
    return _compile(pattern, flags).match(string)


def fullmatch(pattern, string, flags=0):
    return _compile(pattern, flags).fullmatch(string)


def findall(pattern, string, flags=0):
    return _compile(pattern, flags).findall(string)


def finditer(pattern, string, flags=0):
    return _compile(pattern, flags).finditer(string)


class _ZeroSentinel(int):
    pass


_zero_sentinel = _ZeroSentinel()


def sub(
    pattern,
    repl,
    string,
    *args,
    count=_zero_sentinel,
    flags=_zero_sentinel,
):
    if args:
        if count is not _zero_sentinel:
            raise TypeError(
                "sub() got multiple values for argument 'count'"
            )
        count, *remaining = args
        if remaining:
            if flags is not _zero_sentinel:
                raise TypeError(
                    "sub() got multiple values for argument 'flags'"
                )
            flags, *remaining = remaining
            if remaining:
                raise TypeError(
                    "sub() takes from 3 to 5 positional arguments "
                    f"but {5 + len(remaining)} were given"
                )
        warnings.warn(
            "'count' is passed as positional argument",
            DeprecationWarning,
            stacklevel=2,
        )
    return _compile(pattern, flags).sub(repl, string, count)


def subn(
    pattern,
    repl,
    string,
    *args,
    count=_zero_sentinel,
    flags=_zero_sentinel,
):
    if args:
        if count is not _zero_sentinel:
            raise TypeError(
                "subn() got multiple values for argument 'count'"
            )
        count, *remaining = args
        if remaining:
            if flags is not _zero_sentinel:
                raise TypeError(
                    "subn() got multiple values for argument 'flags'"
                )
            flags, *remaining = remaining
            if remaining:
                raise TypeError(
                    "subn() takes from 3 to 5 positional arguments "
                    f"but {5 + len(remaining)} were given"
                )
        warnings.warn(
            "'count' is passed as positional argument",
            DeprecationWarning,
            stacklevel=2,
        )
    return _compile(pattern, flags).subn(repl, string, count)


def split(
    pattern,
    string,
    *args,
    maxsplit=_zero_sentinel,
    flags=_zero_sentinel,
):
    if args:
        if maxsplit is not _zero_sentinel:
            raise TypeError(
                "split() got multiple values for argument 'maxsplit'"
            )
        maxsplit, *remaining = args
        if remaining:
            if flags is not _zero_sentinel:
                raise TypeError(
                    "split() got multiple values for argument 'flags'"
                )
            flags, *remaining = remaining
            if remaining:
                raise TypeError(
                    "split() takes from 2 to 4 positional arguments "
                    f"but {4 + len(remaining)} were given"
                )
        warnings.warn(
            "'maxsplit' is passed as positional argument",
            DeprecationWarning,
            stacklevel=2,
        )
    return _compile(pattern, flags).split(string, maxsplit)


_special_characters = "()[]{}?*+-|^$\\.&~# \t\n\r\v\f"
_escape_translation = {
    ord(character): "\\" + character
    for character in _special_characters
}


def escape(pattern):
    if isinstance(pattern, str):
        return pattern.translate(_escape_translation)
    text = str(pattern, "latin1")
    return text.translate(_escape_translation).encode("latin1")


_simple_template_escapes = {
    "a": "\a",
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
    "v": "\v",
    "\\": "\\",
}


def _template_group(pattern, spelling, original, position):
    if spelling.isascii() and spelling.isdecimal():
        number = int(spelling)
    else:
        try:
            number = pattern.groupindex[spelling]
        except KeyError:
            raise IndexError(
                f"unknown group name {spelling!r}"
            ) from None
    if number > pattern.groups:
        raise PatternError(
            f"invalid group reference {number}",
            original,
            position,
        )
    return number


def _parse_template(pattern, template):
    text_mode = isinstance(pattern.pattern, str)
    if text_mode:
        if not isinstance(template, str):
            raise TypeError(
                "cannot use a bytes replacement on a string pattern"
            )
        original = template
        source = template
    else:
        if isinstance(template, str):
            raise TypeError(
                "cannot use a string replacement on a bytes pattern"
            )
        try:
            original = bytes(memoryview(template).cast("B"))
        except (TypeError, BufferError):
            raise TypeError(
                "expected a bytes-like replacement"
            ) from None
        source = original.decode("latin1")

    cache_key = (pattern, type(original), original)
    cached = _template_cache.get(cache_key)
    if cached is not None:
        return cached

    def literal(value):
        return value if text_mode else value.encode("latin1")

    tokens = []
    pending = []
    cursor = 0
    while cursor < len(source):
        character = source[cursor]
        if character != "\\":
            pending.append(character)
            cursor += 1
            continue
        if pending:
            tokens.append(literal("".join(pending)))
            pending.clear()
        opening = cursor
        cursor += 1
        if cursor == len(source):
            raise PatternError(
                "bad escape (end of pattern)",
                original,
                opening,
            )
        escaped = source[cursor]
        cursor += 1

        if escaped == "g":
            if cursor == len(source) or source[cursor] != "<":
                raise PatternError(
                    "missing <",
                    original,
                    cursor,
                )
            cursor += 1
            start = cursor
            while (
                cursor < len(source)
                and source[cursor] != ">"
            ):
                cursor += 1
            if cursor == len(source):
                raise PatternError(
                    "missing >, unterminated name",
                    original,
                    start,
                )
            name = source[start:cursor]
            cursor += 1
            if not name:
                raise PatternError(
                    "missing group name",
                    original,
                    start,
                )
            tokens.append(
                (_template_group(
                    pattern,
                    name,
                    original,
                    start,
                ),)
            )
            continue

        if escaped in "0123456789":
            if escaped == "0":
                digits = escaped
                for _ in range(2):
                    if (
                        cursor < len(source)
                        and source[cursor] in "01234567"
                    ):
                        digits += source[cursor]
                        cursor += 1
                    else:
                        break
                tokens.append(literal(chr(int(digits, 8))))
                continue
            if (
                escaped in "01234567"
                and cursor + 1 < len(source)
                and source[cursor] in "01234567"
                and source[cursor + 1] in "01234567"
            ):
                digits = escaped + source[cursor:cursor + 2]
                cursor += 2
                number = int(digits, 8)
                if number > 0xFF:
                    raise PatternError(
                        (
                            f"octal escape value \\{digits} "
                            "outside of range 0-0o377"
                        ),
                        original,
                        opening,
                    )
                tokens.append(literal(chr(number)))
                continue
            digits = escaped
            if (
                cursor < len(source)
                and source[cursor].isascii()
                and source[cursor].isdigit()
            ):
                digits += source[cursor]
                cursor += 1
            tokens.append(
                (_template_group(
                    pattern,
                    digits,
                    original,
                    opening + 1,
                ),)
            )
            continue

        if escaped in _simple_template_escapes:
            tokens.append(
                literal(_simple_template_escapes[escaped])
            )
            continue
        if escaped.isascii() and escaped.isalpha():
            raise PatternError(
                f"bad escape \\{escaped}",
                original,
                opening,
            )
        tokens.append(literal("\\" + escaped))

    if pending:
        tokens.append(literal("".join(pending)))
    result = tuple(tokens)
    if len(_template_cache) >= _MAXCACHE:
        try:
            del _template_cache[
                next(iter(_template_cache))
            ]
        except (StopIteration, RuntimeError, KeyError):
            pass
    _template_cache[cache_key] = result
    return result


def _render_template(tokens, match_object):
    separator = (
        ""
        if isinstance(match_object.re.pattern, str)
        else b""
    )
    pieces = []
    for token in tokens:
        if isinstance(token, tuple):
            value = match_object.group(token[0])
            pieces.append(
                separator
                if value is None
                else value
            )
        else:
            pieces.append(token)
    return separator.join(pieces)


def _pickle_pattern(pattern):
    return _compile, (pattern.pattern, pattern.flags)


copyreg.pickle(Pattern, _pickle_pattern, _compile)


class Scanner:
    """A Python-compatible lexical scanner using only the Go engine."""

    __slots__ = (
        "lexicon",
        "scanner",
        "_phrase_groups",
        "match",
        "__weakref__",
    )

    def __init__(self, lexicon, flags=0):
        self.lexicon = lexicon
        entries = list(lexicon)
        if not entries:
            self.scanner = _compile("", flags)
            self._phrase_groups = ()
            return

        first = entries[0][0]
        byte_mode = isinstance(first, bytes)
        empty = b"" if byte_mode else ""
        opening = b"(" if byte_mode else "("
        closing = b")" if byte_mode else ")"
        divider = b"|" if byte_mode else "|"
        fragments = []
        phrase_groups = []
        next_group = 1
        for phrase, action in entries:
            if not isinstance(
                phrase,
                bytes if byte_mode else str,
            ):
                raise TypeError(
                    "scanner phrases must share one pattern type"
                )
            parsed = _compile(phrase, flags)
            fragments.append(
                opening + phrase + closing
            )
            phrase_groups.append((next_group, action))
            next_group += parsed.groups + 1
        combined = (
            divider.join(fragments)
            if fragments
            else empty
        )
        self.scanner = _compile(combined, flags)
        self._phrase_groups = tuple(phrase_groups)

    def scan(self, string):
        found = []
        cursor = 0
        iterator = self.scanner.scanner(string)
        while True:
            result = iterator.match()
            if result is None:
                break
            following = result.end()
            if following == cursor:
                break
            action = None
            for group, candidate in self._phrase_groups:
                if result.start(group) >= 0:
                    action = candidate
                    break
            if callable(action):
                self.match = result
                action = action(self, result.group())
            if action is not None:
                found.append(action)
            cursor = following
        return found, _subject_piece(
            string,
            cursor,
            _MAX_INDEX,
        )
