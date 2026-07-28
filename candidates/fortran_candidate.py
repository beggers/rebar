"""An exploratory, independently owned Fortran regular-expression candidate.

Matching is performed exclusively by this project's Fortran engine through
``candidates._fortran_bridge``. Compatibility and speed are not established.
"""

from __future__ import annotations

import enum
import operator
import sys
import types
import warnings

from candidates import _fortran_bridge


__version__ = "2.2.1"
_UNSET = object()
_LARGEST_INDEX = sys.maxsize
_SMALLEST_INDEX = -sys.maxsize - 1


class RegexFlag(enum.IntFlag):
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
        number = int(self)
        if number == 0:
            return "re.NOFLAG"
        definitions = (
            (256, "ASCII"),
            (2, "IGNORECASE"),
            (4, "LOCALE"),
            (32, "UNICODE"),
            (8, "MULTILINE"),
            (16, "DOTALL"),
            (64, "VERBOSE"),
            (128, "DEBUG"),
        )
        labels = [f"re.{label}" for bit, label in definitions if number & bit]
        remainder = number & ~sum(bit for bit, _ in definitions)
        if remainder:
            labels.append(hex(remainder))
        return "|".join(labels)

    __str__ = __repr__


A = ASCII = RegexFlag.ASCII
I = IGNORECASE = RegexFlag.IGNORECASE
L = LOCALE = RegexFlag.LOCALE
M = MULTILINE = RegexFlag.MULTILINE
S = DOTALL = RegexFlag.DOTALL
U = UNICODE = RegexFlag.UNICODE
X = VERBOSE = RegexFlag.VERBOSE
DEBUG = RegexFlag.DEBUG
NOFLAG = RegexFlag.NOFLAG


class PatternError(Exception):
    def __init__(self, message, pattern=None, position=None):
        self.msg = message
        self.pattern = pattern
        self.pos = position
        self.lineno = None
        self.colno = None
        rendered = message
        if pattern is not None and position is not None:
            readable = pattern.decode("latin1") if isinstance(pattern, bytes) else pattern
            self.lineno = readable.count("\n", 0, position) + 1
            self.colno = position - readable.rfind("\n", 0, position)
            rendered = f"{message} at position {position}"
            if "\n" in readable:
                rendered += f" (line {self.lineno}, column {self.colno})"
        super().__init__(rendered)


error = PatternError


def _bounded_integer(value):
    result = operator.index(value)
    if result < _SMALLEST_INDEX or result > _LARGEST_INDEX:
        raise OverflowError("Python int too large to convert to C ssize_t")
    return result


def _flag_integer(value):
    result = operator.index(value)
    if result < 0 or result > 0x7FFFFFFF:
        raise OverflowError("regular-expression flags exceed 31 bits")
    return result


def _native_error(exception, pattern):
    values = exception.args
    description = values[0] if values else "invalid regular expression"
    position = values[1] if len(values) > 1 else None
    return PatternError(description, pattern, position)


def _portion(value, beginning, ending):
    if isinstance(value, (str, bytes)):
        return value[beginning:ending]
    return memoryview(value).cast("B")[beginning:ending].tobytes()


class Match:
    __slots__ = (
        "_expression",
        "_subject",
        "_retained",
        "_positions",
        "_last",
        "_beginning",
        "_ending",
    )

    def __init__(self, expression, retained, positions, last, beginning, ending):
        self._expression = expression
        self._subject = retained.string
        self._retained = retained
        self._positions = tuple(positions)
        self._last = last
        self._beginning = beginning
        self._ending = ending

    @classmethod
    def __class_getitem__(cls, argument):
        return types.GenericAlias(cls, argument)

    @property
    def re(self):
        return self._expression

    @property
    def string(self):
        return self._subject

    @property
    def pos(self):
        return self._beginning

    @property
    def endpos(self):
        return self._ending

    @property
    def lastindex(self):
        return self._last

    @property
    def lastgroup(self):
        if self._last is None:
            return None
        return next(
            (name for name, number in self._expression.groupindex.items()
             if number == self._last),
            None,
        )

    @property
    def regs(self):
        return self._positions

    def _resolve_group(self, group):
        if isinstance(group, str):
            try:
                return self._expression.groupindex[group]
            except KeyError:
                raise IndexError("no such group") from None
        try:
            number = operator.index(group)
        except TypeError:
            raise IndexError("no such group") from None
        if not 0 <= number < len(self._positions):
            raise IndexError("no such group")
        return number

    def _extract(self, group):
        first, last = self._positions[self._resolve_group(group)]
        return None if first == -1 else _portion(self._subject, first, last)

    def group(self, *groups):
        if not groups:
            return self._extract(0)
        if len(groups) == 1:
            return self._extract(groups[0])
        return tuple(self._extract(group) for group in groups)

    def __getitem__(self, group):
        return self._extract(group)

    def groups(self, default=None):
        return tuple(
            default if first == -1 else _portion(self._subject, first, last)
            for first, last in self._positions[1:]
        )

    def groupdict(self, default=None):
        return {
            name: (
                default if self._positions[number][0] == -1
                else _portion(self._subject, *self._positions[number])
            )
            for name, number in self._expression.groupindex.items()
        }

    def start(self, group=0):
        return self._positions[self._resolve_group(group)][0]

    def end(self, group=0):
        return self._positions[self._resolve_group(group)][1]

    def span(self, group=0):
        return self._positions[self._resolve_group(group)]

    def expand(self, template):
        return _render_template(_read_template(template, self._expression), self)

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self

    def __reduce__(self):
        raise TypeError("cannot pickle 're.Match' object")

    def __repr__(self):
        return f"<re.Match object; span={self.span()}, match={self.group()!r}>"


class _MatchCursor:
    __slots__ = ("expression", "subject", "position", "limit", "origin", "empty", "closed")

    def __init__(self, expression, subject, position, limit):
        self.expression = expression
        self.subject = subject
        self.position = position
        self.limit = limit
        self.origin = position
        self.empty = False
        self.closed = False

    def _step(self, operation):
        if self.closed:
            return None
        match_object = self.expression._invoke(
            self.subject,
            self.position,
            self.limit,
            operation,
            self.empty,
            self.origin,
        )
        if match_object is None:
            if operation == 1 or self.position >= self.limit:
                self.closed = True
                return None
            if self.empty:
                self.position += 1
                self.empty = False
                match_object = self.expression._invoke(
                    self.subject,
                    self.position,
                    self.limit,
                    operation,
                    False,
                    self.origin,
                )
            if match_object is None:
                self.closed = True
                return None
        beginning, ending = match_object.span()
        self.position = ending
        self.empty = beginning == ending
        return match_object

    def search(self):
        return self._step(0)

    def match(self):
        return self._step(1)


class Pattern:
    __slots__ = (
        "_source",
        "_settings",
        "_program",
        "_count",
        "_names",
        "__weakref__",
    )

    def __init__(self, source, settings, program, count, names):
        object.__setattr__(self, "_source", source)
        object.__setattr__(self, "_settings", settings)
        object.__setattr__(self, "_program", program)
        object.__setattr__(self, "_count", count)
        object.__setattr__(self, "_names", types.MappingProxyType(dict(names)))

    @classmethod
    def __class_getitem__(cls, argument):
        return types.GenericAlias(cls, argument)

    @property
    def pattern(self):
        return self._source

    @property
    def flags(self):
        return self._settings

    @property
    def groups(self):
        return self._count

    @property
    def groupindex(self):
        return self._names

    def __setattr__(self, name, value):
        raise AttributeError("readonly attribute")

    def __delattr__(self, name):
        raise AttributeError("readonly attribute")

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self

    def __reduce__(self):
        return compile, (self._source, self._settings)

    def __hash__(self):
        return hash((type(self._source), self._source, self._settings))

    def __eq__(self, other):
        if not isinstance(other, Pattern):
            return NotImplemented
        return (
            type(self._source) is type(other._source)
            and self._source == other._source
            and self._settings == other._settings
        )

    def __repr__(self):
        settings = self._settings
        if isinstance(self._source, str):
            settings &= ~int(UNICODE)
        addition = "" if settings == 0 else ", " + repr(RegexFlag(settings))
        return f"re.compile({self._source!r}{addition})"

    def _retain(self, value):
        return _fortran_bridge.subject(value, isinstance(self._source, bytes))

    def _limits(self, retained, first, last):
        first = _bounded_integer(first)
        last = _bounded_integer(last)
        size = retained.length
        return min(max(first, 0), size), min(max(last, 0), size)

    def _invoke(self, retained, first, last, operation, require_nonempty, origin=None):
        returned = _fortran_bridge.run(
            self._program,
            retained,
            first,
            last,
            operation,
            require_nonempty,
        )
        if returned is None:
            return None
        locations, recent = returned
        return Match(
            self,
            retained,
            locations,
            recent,
            first if origin is None else origin,
            last,
        )

    def search(self, string, pos=0, endpos=_LARGEST_INDEX):
        retained = self._retain(string)
        first, last = self._limits(retained, pos, endpos)
        return self._invoke(retained, first, last, 0, False)

    def match(self, string, pos=0, endpos=_LARGEST_INDEX):
        retained = self._retain(string)
        first, last = self._limits(retained, pos, endpos)
        return self._invoke(retained, first, last, 1, False)

    def fullmatch(self, string, pos=0, endpos=_LARGEST_INDEX):
        retained = self._retain(string)
        first, last = self._limits(retained, pos, endpos)
        return self._invoke(retained, first, last, 2, False)

    def scanner(self, string, pos=0, endpos=_LARGEST_INDEX):
        retained = self._retain(string)
        first, last = self._limits(retained, pos, endpos)
        return _MatchCursor(self, retained, first, last)

    def finditer(self, string, pos=0, endpos=_LARGEST_INDEX):
        return iter(self.scanner(string, pos, endpos).search, None)

    def findall(self, string, pos=0, endpos=_LARGEST_INDEX):
        found = self.finditer(string, pos, endpos)
        if self._count == 0:
            return [item.group() for item in found]
        empty = "" if isinstance(self._source, str) else b""
        if self._count == 1:
            return [empty if item.group(1) is None else item.group(1) for item in found]
        return [
            tuple(empty if group is None else group for group in item.groups())
            for item in found
        ]

    def split(self, string, maxsplit=0):
        maximum = _bounded_integer(maxsplit)
        if maximum < 0:
            return [string]
        retained = self._retain(string)
        cursor = _MatchCursor(self, retained, 0, retained.length)
        pieces = []
        previous = 0
        operations = 0
        while maximum == 0 or operations < maximum:
            found = cursor.search()
            if found is None:
                break
            first, last = found.span()
            pieces.append(_portion(string, previous, first))
            pieces.extend(found.groups())
            previous = last
            operations += 1
        pieces.append(_portion(string, previous, retained.length))
        return pieces

    def sub(self, repl, string, count=0):
        return self.subn(repl, string, count)[0]

    def subn(self, repl, string, count=0):
        maximum = _bounded_integer(count)
        retained = self._retain(string)
        if callable(repl):
            callback = repl
            recipe = None
        else:
            callback = None
            recipe = _read_template(repl, self)
        if maximum < 0:
            return _portion(string, 0, retained.length), 0
        cursor = _MatchCursor(self, retained, 0, retained.length)
        sections = []
        previous = 0
        performed = 0
        while maximum == 0 or performed < maximum:
            found = cursor.search()
            if found is None:
                break
            first, last = found.span()
            sections.append(_portion(string, previous, first))
            replacement = callback(found) if callback else _render_template(recipe, found)
            if isinstance(self._source, str):
                if not isinstance(replacement, str):
                    raise TypeError("sequence item: expected str instance")
            elif not isinstance(replacement, bytes):
                if isinstance(replacement, (bytearray, memoryview)):
                    replacement = bytes(replacement)
                else:
                    raise TypeError("sequence item: expected a bytes-like object")
            sections.append(replacement)
            previous = last
            performed += 1
        sections.append(_portion(string, previous, retained.length))
        joiner = "" if isinstance(self._source, str) else b""
        return joiner.join(sections), performed


_patterns = {}
_maximum_patterns = 512


def compile(pattern, flags=0):
    requested = _flag_integer(flags)
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
    identity = (type(pattern), pattern, requested)
    if not requested & int(DEBUG):
        previous = _patterns.get(identity)
        if previous is not None:
            return previous
    passed_flags = requested
    if isinstance(pattern, str) and not requested & int(ASCII):
        passed_flags |= int(UNICODE)
    try:
        program, count, names, actual = _fortran_bridge.compile(pattern, passed_flags)
    except _fortran_bridge.PatternSyntaxError as exc:
        raise _native_error(exc, pattern) from None
    expression = Pattern(pattern, actual, program, count, names)
    if not requested & int(DEBUG):
        if len(_patterns) >= _maximum_patterns:
            _patterns.pop(next(iter(_patterns)))
        _patterns[identity] = expression
    return expression


def purge():
    _patterns.clear()


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


def _warn_positional(argument, values):
    if values:
        warnings.warn(
            f"'{argument}' is passed as positional argument",
            DeprecationWarning,
            stacklevel=3,
        )


def split(pattern, string, *values, maxsplit=_UNSET, flags=_UNSET):
    if len(values) > 2:
        raise TypeError("split() takes at most 4 arguments")
    _warn_positional("maxsplit", values)
    if values:
        if maxsplit is not _UNSET:
            raise TypeError("split() got multiple values for argument 'maxsplit'")
        maxsplit = values[0]
    if len(values) == 2:
        if flags is not _UNSET:
            raise TypeError("split() got multiple values for argument 'flags'")
        flags = values[1]
    setting = 0 if flags is _UNSET else flags
    limit = 0 if maxsplit is _UNSET else maxsplit
    return compile(pattern, setting).split(string, limit)


def sub(pattern, repl, string, *values, count=_UNSET, flags=_UNSET):
    if len(values) > 2:
        raise TypeError("sub() takes at most 5 arguments")
    _warn_positional("count", values)
    if values:
        if count is not _UNSET:
            raise TypeError("sub() got multiple values for argument 'count'")
        count = values[0]
    if len(values) == 2:
        if flags is not _UNSET:
            raise TypeError("sub() got multiple values for argument 'flags'")
        flags = values[1]
    setting = 0 if flags is _UNSET else flags
    limit = 0 if count is _UNSET else count
    return compile(pattern, setting).sub(repl, string, limit)


def subn(pattern, repl, string, *values, count=_UNSET, flags=_UNSET):
    if len(values) > 2:
        raise TypeError("subn() takes at most 5 arguments")
    _warn_positional("count", values)
    if values:
        if count is not _UNSET:
            raise TypeError("subn() got multiple values for argument 'count'")
        count = values[0]
    if len(values) == 2:
        if flags is not _UNSET:
            raise TypeError("subn() got multiple values for argument 'flags'")
        flags = values[1]
    setting = 0 if flags is _UNSET else flags
    limit = 0 if count is _UNSET else count
    return compile(pattern, setting).subn(repl, string, limit)


_escaped_characters = "()[]{}?*+-|^$\\.&~# \t\n\r\v\f"
_escaped_translation = {
    ord(character): "\\" + character
    for character in _escaped_characters
}


def escape(pattern):
    if isinstance(pattern, str):
        return pattern.translate(_escaped_translation)
    try:
        raw = memoryview(pattern).cast("B").tobytes()
    except TypeError:
        raise TypeError("decoding to str: need a bytes-like object") from None
    return raw.decode("latin1").translate(_escaped_translation).encode("latin1")


_template_escapes = {
    "a": "\a",
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
    "v": "\v",
    "\\": "\\",
}


def _template_group(expression, name, original, position):
    if name.isascii() and name.isdecimal():
        number = int(name)
    else:
        try:
            number = expression.groupindex[name]
        except KeyError:
            raise IndexError(f"unknown group name {name!r}") from None
    if number > expression.groups:
        raise PatternError(f"invalid group reference {number}", original, position)
    return number


def _read_template(template, expression):
    text = isinstance(expression.pattern, str)
    if text:
        if not isinstance(template, str):
            raise TypeError("cannot use a bytes replacement on a string pattern")
        original = template
        readable = template
    else:
        if isinstance(template, str):
            raise TypeError("cannot use a string replacement on a bytes pattern")
        try:
            original = memoryview(template).cast("B").tobytes()
        except TypeError:
            raise TypeError("expected a bytes-like replacement") from None
        readable = original.decode("latin1")
    pieces = []
    index = 0
    previous = 0
    while index < len(readable):
        if readable[index] != "\\":
            index += 1
            continue
        if previous < index:
            literal = readable[previous:index]
            pieces.append(literal if text else literal.encode("latin1"))
        opening = index
        index += 1
        if index == len(readable):
            raise PatternError("bad escape (end of pattern)", original, opening)
        marker = readable[index]
        index += 1
        if marker == "g":
            if index == len(readable) or readable[index] != "<":
                raise PatternError("missing <", original, index)
            index += 1
            name_start = index
            while index < len(readable) and readable[index] != ">":
                index += 1
            if index == len(readable):
                raise PatternError("missing >, unterminated name", original, name_start)
            name = readable[name_start:index]
            index += 1
            if not name:
                raise PatternError("missing group name", original, name_start)
            pieces.append((_template_group(expression, name, original, name_start),))
        elif marker in "123456789":
            digits = marker
            if index < len(readable) and readable[index].isascii() and readable[index].isdigit():
                digits += readable[index]
                index += 1
            pieces.append((_template_group(expression, digits, original, opening + 1),))
        elif marker == "0":
            digits = marker
            while len(digits) < 3 and index < len(readable) and readable[index] in "01234567":
                digits += readable[index]
                index += 1
            character = chr(int(digits, 8))
            pieces.append(character if text else character.encode("latin1"))
        elif marker in _template_escapes:
            character = _template_escapes[marker]
            pieces.append(character if text else character.encode("latin1"))
        elif marker.isascii() and marker.isalpha():
            raise PatternError(f"bad escape \\{marker}", original, opening)
        else:
            character = "\\" + marker
            pieces.append(character if text else character.encode("latin1"))
        previous = index
    if previous < len(readable):
        literal = readable[previous:]
        pieces.append(literal if text else literal.encode("latin1"))
    return tuple(pieces)


def _render_template(recipe, found):
    empty = "" if isinstance(found.re.pattern, str) else b""
    values = []
    for item in recipe:
        if isinstance(item, tuple):
            value = found.group(item[0])
            values.append(empty if value is None else value)
        else:
            values.append(item)
    return empty.join(values)


class Scanner:
    def __init__(self, lexicon, flags=0):
        self.lexicon = lexicon
        self.flags = _flag_integer(flags)
        self._entries = []
        expressions = []
        kind = None
        for entry in lexicon:
            try:
                source, action = entry
            except (TypeError, ValueError):
                raise TypeError("scanner entries must contain a pattern and an action") from None
            if not isinstance(source, (str, bytes)):
                raise TypeError("scanner patterns must be strings or bytes")
            if kind is None:
                kind = type(source)
            elif type(source) is not kind:
                raise TypeError("scanner patterns must all have the same type")
            expressions.append(source)
            self._entries.append((compile(source, self.flags), action))
        if kind is bytes:
            combined = b"|".join(b"(" + source + b")" for source in expressions)
        else:
            combined = "|".join("(" + source + ")" for source in expressions)
        self.scanner = compile(combined, self.flags)

    def scan(self, string):
        if not self._entries:
            return [], string
        retained = self._entries[0][0]._retain(string)
        items = []
        offset = 0
        while offset < retained.length:
            selected = None
            action = None
            for expression, candidate_action in self._entries:
                found = expression._invoke(retained, offset, retained.length, 1, False)
                if found is not None:
                    selected = found
                    action = candidate_action
                    break
            if selected is None or selected.end() == offset:
                break
            if action is not None:
                if callable(action):
                    self.match = selected
                    value = action(self, selected.group())
                else:
                    value = action
                if value is not None:
                    items.append(value)
            offset = selected.end()
        return items, _portion(string, offset, retained.length)


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
