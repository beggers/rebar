"""From-scratch Rust regular expressions with a mandatory native bridge."""

import enum
import operator
import os
import types
import unicodedata
import warnings

from candidates import _rust_bridge


class RegexFlag(enum.IntFlag):
    ASCII = 256
    IGNORECASE = 2
    LOCALE = 4
    UNICODE = 32
    MULTILINE = 8
    DOTALL = 16
    VERBOSE = 64
    DEBUG = 128

    def __repr__(self):
        value = int(self)
        if not value:
            return "re.NOFLAG"
        ordered = ((self.ASCII, "ASCII"), (self.IGNORECASE, "IGNORECASE"), (self.LOCALE, "LOCALE"), (self.UNICODE, "UNICODE"), (self.MULTILINE, "MULTILINE"), (self.DOTALL, "DOTALL"), (self.VERBOSE, "VERBOSE"), (self.DEBUG, "DEBUG"))
        known = sum(int(bit) for bit, _ in ordered)
        parts = [f"re.{name}" for bit, name in ordered if value & int(bit)]
        unknown = value & ~known
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
NOFLAG = RegexFlag(0)
_BYTE = 1 << 31
_ESCAPE_MAP = {ord(char): "\\" + char for char in "()[]{}?*+-|^$\\.&~# \t\n\r\v\f"}
_MISSING = object()
_WARNING_PREFIX = (os.path.dirname(__file__),)
_MAX_ENDPOS = (1 << 63) - 1
_MIN_ENDPOS = -_MAX_ENDPOS - 1
_PATTERN_METHODS = ("search", "match", "fullmatch", "findall", "finditer", "split", "sub", "subn", "scanner")
_SIMPLE_TEMPLATE_ESCAPES = {"a": "\a", "b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t", "v": "\v", "\\": "\\"}


class PatternError(Exception):
    def __init__(self, msg, pattern=None, pos=None):
        self.msg = msg
        self.pattern = pattern
        self.pos = pos
        if pattern is None or pos is None:
            self.lineno = self.colno = None
            text = msg
        else:
            scan = pattern.decode("latin1") if isinstance(pattern, bytes) else pattern
            self.lineno = scan.count("\n", 0, pos) + 1
            self.colno = pos - scan.rfind("\n", 0, pos)
            text = f"{msg} at position {pos}"
            if "\n" in scan:
                text += f" (line {self.lineno}, column {self.colno})"
        super().__init__(text)


error = PatternError


def _name_text(value):
    if isinstance(value, bytes):
        return value.decode("ascii", "backslashreplace")
    return value


def _character_range_error(pattern, message, position):
    if (
        not isinstance(pattern, str)
        or not message.startswith("bad character range ")
        or position is None
        or position < 0
        or position + 2 >= len(pattern)
        or pattern[position + 1] != "-"
    ):
        return message, position

    dash = position + 1

    def escape_end(start):
        if start + 1 >= len(pattern) or pattern[start] != "\\":
            return start + 1
        marker = pattern[start + 1]
        if marker == "x":
            return start + 4
        if marker == "u":
            return start + 6
        if marker == "U":
            return start + 10
        if marker == "N" and pattern[start + 2:start + 3] == "{":
            close = pattern.find("}", start + 3)
            return len(pattern) if close < 0 else close + 1
        return start + 2

    escaped_left = pattern.rfind("\\", 0, dash)
    if escaped_left >= 0 and escape_end(escaped_left) == dash:
        left = pattern[escaped_left:escaped_left + 2]
    else:
        left = pattern[dash - 1]
    right_start = dash + 1
    if pattern[right_start] == "\\":
        right = pattern[right_start:right_start + 2]
        right_end = escape_end(right_start)
    else:
        right = pattern[right_start]
        right_end = right_start + 1
    return f"bad character range {left}-{right}", right_end - len(left) - len(right) - 1


def _group_name_error(pattern, message, position):
    if (
        not isinstance(pattern, str)
        or position is None
        or not 0 <= position < len(pattern)
    ):
        return message
    if message.startswith("bad character in group name "):
        prefix = "bad character in group name"
    elif message.startswith("unknown group name "):
        prefix = "unknown group name"
    elif message == "invalid group reference ":
        prefix = "bad character in group name"
    else:
        return message
    end = min(
        (
            index
            for index in (pattern.find(">", position), pattern.find(")", position))
            if index >= 0
        ),
        default=len(pattern),
    )
    name = pattern[position:end]
    if name and not name.isprintable():
        return f"{prefix} {name!r}"
    return message


class _Native:
    __slots__ = ("native_compile", "native_error", "native_free")

    def __init__(self):
        self.native_compile = _rust_bridge.compile
        self.native_error = _rust_bridge.error
        self.native_free = _rust_bridge.free

    def error(self, pattern):
        message, position, include = self.native_error()
        message, position = _character_range_error(pattern, message, position)
        message = _group_name_error(pattern, message, position)
        if message == "the repetition number is too large":
            raise OverflowError(message)
        if message == "maximum recursion depth exceeded":
            raise RecursionError(message)
        if message.startswith("redefinition of group name "):
            try:
                raise PatternError(message)
            except PatternError:
                raise PatternError(
                    message,
                    pattern if include else None,
                    position if position is not None and position >= 0 else None,
                ) from None
        raise PatternError(message, pattern if include else None, position if position is not None and position >= 0 else None)

    def compile(self, pattern, flags):
        named = _named_escapes(pattern) if isinstance(pattern, str) and "\\N" in pattern else ()
        if named:
            positions = tuple(item[0] for item in named)
            values = tuple(item[1] for item in named)
        else:
            positions = values = ()
        compiled = self.native_compile(pattern, flags, positions, values)
        if compiled is None:
            self.error(pattern)
        return compiled

    def run(self, handle, string, groups, pos, endpos, mode, nonempty):
        return _rust_bridge.run(handle, string, groups, pos, endpos, mode, nonempty)

    def collect(self, handle, string, groups, pos, endpos):
        return _rust_bridge.collect(handle, string, groups, pos, endpos)

    def free(self, handle):
        self.native_free(handle)


_NATIVE = _Native()


def _named_escapes(pattern):
    if isinstance(pattern, bytes):
        return []
    found = []
    index = 0
    while index < len(pattern):
        if pattern[index] != "\\":
            index += 1
            continue
        slash = index
        index += 1
        if pattern[index:index + 2] != "N{":
            index += bool(pattern[index:index + 1])
            continue
        close = pattern.find("}", index + 2)
        if close == index + 2 or (close < 0 and index + 2 == len(pattern)):
            raise PatternError("missing character name", pattern, slash + 3)
        if close < 0:
            raise PatternError("missing }, unterminated name", pattern, slash + 3)
        name = pattern[index + 2:close]
        try:
            value = unicodedata.lookup(name)
        except KeyError:
            raise PatternError(f"undefined character name {name!r}", pattern, slash) from None
        if len(value) != 1:
            raise PatternError(f"undefined character name {name!r}", pattern, slash)
        found.append((slash, ord(value)))
        index = close + 1
    return found


def _warn_ambiguous(pattern):
    text = pattern.decode("latin1") if isinstance(pattern, bytes) else pattern
    opening = -1
    escaped = False
    for index, char in enumerate(text):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
        elif char == "[" and opening < 0:
            opening = index
        elif char == "]":
            first = opening + 1 + (text[opening + 1:opening + 2] == "^")
            if opening < 0 or index != first:
                opening = -1
        elif opening >= 0:
            if char == "[" and index == opening + 1:
                warnings.warn(f"Possible nested set at position {index}", FutureWarning, skip_file_prefixes=_WARNING_PREFIX)
            first = opening + 1 + (text[opening + 1:opening + 2] == "^")
            if index > first:
                for marker, label in (("&&", "intersection"), ("||", "union"), ("~~", "symmetric difference"), ("--", "difference")):
                    if text[index:index + 2] == marker:
                        warnings.warn(f"Possible set {label} at position {index}", FutureWarning, skip_file_prefixes=_WARNING_PREFIX)


def _template(value, match, validate_only=False):
    if isinstance(value, (bytearray, memoryview)):
        value = bytes(value)
    if not isinstance(value, (str, bytes)):
        hash(value)
        raise TypeError(f"decoding to str: need a bytes-like object, {type(value).__name__} found")
    byte_mode = isinstance(value, bytes)
    text = value.decode("latin1") if isinstance(value, bytes) else value
    output = []
    index = 0
    while index < len(text):
        char = text[index]
        if char != "\\":
            output.append(char)
            index += 1
            continue
        slash = index
        index += 1
        if index == len(text):
            raise PatternError("bad escape (end of pattern)", value, slash)
        char = text[index]
        index += 1
        if char == "g":
            if index >= len(text) or text[index] != "<":
                raise PatternError("missing <", value, index)
            index += 1
            name_start = index
            close = text.find(">", index)
            if close < 0:
                name = text[index:]
                if not name:
                    raise PatternError("missing group name", value, name_start)
                raise PatternError("missing >, unterminated name", value, name_start)
            name = text[index:close]
            index = close + 1
            if not name:
                raise PatternError("missing group name", value, name_start)
            if all(item in "0123456789" for item in name):
                number = int(name)
                if number > match.re.groups:
                    raise PatternError(f"invalid group reference {number}", value, name_start)
            else:
                if not name.isidentifier() or (byte_mode and not name.isascii()):
                    shown = "".join(item if item.isascii() else f"\\x{ord(item):02x}" for item in name) if byte_mode else name
                    raise PatternError(f"bad character in group name '{shown}'", value, name_start)
                if name not in match.re.groupindex:
                    raise IndexError(f"unknown group name {name!r}")
                number = match.re.groupindex[name]
            part = (b"" if byte_mode else "") if validate_only else match.group(number)
            if part is not None and byte_mode != isinstance(part, bytes):
                expected = "a bytes-like object" if byte_mode else "str instance"
                raise TypeError(f"sequence item 1: expected {expected}, {type(part).__name__} found")
            output.append("" if part is None else part.decode("latin1") if isinstance(part, bytes) else part)
        elif char in "0123456789":
            digits = char
            octal = char == "0" or (
                char in "1234567"
                and index + 1 < len(text)
                and text[index] in "01234567"
                and text[index + 1] in "01234567"
            )
            if octal:
                while len(digits) < 3 and index < len(text) and text[index] in "01234567":
                    digits += text[index]
                    index += 1
                number = int(digits, 8)
                if number > 0o377:
                    raise PatternError(f"octal escape value \\{digits} outside of range 0-0o377", value, slash)
                output.append(chr(number))
                continue
            if index < len(text) and text[index] in "0123456789":
                digits += text[index]
                index += 1
            number = int(digits)
            if number > match.re.groups:
                raise PatternError(f"invalid group reference {number}", value, slash + 1)
            part = (b"" if byte_mode else "") if validate_only else match.group(number)
            if part is not None and byte_mode != isinstance(part, bytes):
                expected = "a bytes-like object" if byte_mode else "str instance"
                raise TypeError(f"sequence item 1: expected {expected}, {type(part).__name__} found")
            output.append("" if part is None else part.decode("latin1") if isinstance(part, bytes) else part)
        elif char in _SIMPLE_TEMPLATE_ESCAPES:
            output.append(_SIMPLE_TEMPLATE_ESCAPES[char])
        elif char.isalpha():
            raise PatternError(f"bad escape \\{char}", value, slash)
        else:
            output.append("\\" + char)
    joined = "".join(output)
    return joined.encode("latin1") if byte_mode else joined


def _template_tokens(value, pattern):
    byte_mode = isinstance(value, bytes)
    text = value.decode("latin1") if byte_mode else value
    tokens = []
    literal = []
    index = 0

    def group(number):
        if literal:
            joined = "".join(literal)
            tokens.append(joined.encode("latin1") if byte_mode else joined)
            literal.clear()
        tokens.append(number)

    while index < len(text):
        char = text[index]
        index += 1
        if char != "\\":
            literal.append(char)
            continue
        char = text[index]
        index += 1
        if char == "g":
            index += 1
            close = text.index(">", index)
            name = text[index:close]
            index = close + 1
            group(int(name) if all(item in "0123456789" for item in name) else pattern.groupindex[name])
        elif char in "0123456789":
            digits = char
            octal = char == "0" or (char in "1234567" and index + 1 < len(text) and text[index] in "01234567" and text[index + 1] in "01234567")
            if octal:
                while len(digits) < 3 and index < len(text) and text[index] in "01234567":
                    digits += text[index]
                    index += 1
                literal.append(chr(int(digits, 8)))
            else:
                if index < len(text) and text[index] in "0123456789":
                    digits += text[index]
                    index += 1
                group(int(digits))
        elif char in _SIMPLE_TEMPLATE_ESCAPES:
            literal.append(_SIMPLE_TEMPLATE_ESCAPES[char])
        else:
            literal.extend(("\\", char))
    if literal:
        joined = "".join(literal)
        tokens.append(joined.encode("latin1") if byte_mode else joined)
    return tuple(tokens)


def _expand_tokens(tokens, match, byte_mode):
    empty = b"" if byte_mode else ""
    return empty.join(empty if value is None else value for value in (match.group(token) if isinstance(token, int) else token for token in tokens))


def _slice(value, start, end):
    if isinstance(value, str):
        return str(value)[start:end]
    if isinstance(value, bytes):
        return bytes(value)[start:end]
    return memoryview(value).cast("B")[start:end].tobytes()


def _subject_length(value):
    if isinstance(value, (str, bytes, bytearray)):
        return len(value)
    return memoryview(value).nbytes


def _normalize_window(string, pos, endpos):
    length = _subject_length(string)
    start = pos if type(pos) is int else operator.index(pos)
    end = endpos if type(endpos) is int else operator.index(endpos)
    if start > _MAX_ENDPOS or start < _MIN_ENDPOS or end > _MAX_ENDPOS or end < _MIN_ENDPOS:
        raise OverflowError("Python int too large to convert to C ssize_t")
    return min(max(start, 0), length), min(max(end, 0), length), length


def _normalize_count(value):
    count = value if type(value) is int else operator.index(value)
    if count > _MAX_ENDPOS or count < _MIN_ENDPOS:
        raise OverflowError("Python int too large to convert to C ssize_t")
    return count


class _OwnedGenericAlias(types.GenericAlias):
    __slots__ = ()

    def __reduce__(self):
        origin = self.__origin__
        if origin is Pattern:
            name = "Pattern"
        elif origin is Match:
            name = "Match"
        else:
            raise TypeError(
                "cannot pickle an unowned Rust regular-expression generic alias"
            )
        return _restore_owned_generic_alias, (name, self.__args__)


def _restore_owned_generic_alias(name, arguments):
    if type(name) is not str or type(arguments) is not tuple:
        raise TypeError("invalid owned Rust regular-expression generic alias")
    if name == "Pattern":
        origin = Pattern
    elif name == "Match":
        origin = Match
    else:
        raise ValueError("unknown owned Rust regular-expression generic alias")
    return _OwnedGenericAlias(origin, arguments)


Match = _rust_bridge.Match
_NATIVE_BIND = _rust_bridge.bind


class _PatternType(type):
    pass


class Pattern(metaclass=_PatternType):
    __module__ = "re"
    __slots__ = (
        "pattern", "flags", "groups", "_groupindex", "_handle",
        "_literal", "_bound_methods", "_templates", "__weakref__",
    )

    def __init__(self, value, flags, handle, groups, groupindex):
        names = dict(groupindex)
        object.__setattr__(self, "pattern", value)
        object.__setattr__(self, "flags", flags)
        object.__setattr__(self, "groups", groups)
        self._groupindex = names
        self._handle = handle
        self._bound_methods = None
        self._templates = None
        metacharacters = b".^$*+?{}[]\\|()" if isinstance(value, bytes) else ".^$*+?{}[]\\|()"
        self._literal = value if value and not flags & int(IGNORECASE | VERBOSE) and not any(char in metacharacters for char in value) else None

    @property
    def groupindex(self):
        names = self._groupindex
        return types.MappingProxyType(names) if names else {}

    def __setattr__(self, name, value):
        if name in ("pattern", "flags", "groups"):
            raise AttributeError("readonly attribute")
        if name == "groupindex":
            raise AttributeError("attribute 'groupindex' of 're.Pattern' objects is not writable")
        if name in _PATTERN_METHODS:
            raise AttributeError(f"'re.Pattern' object attribute '{name}' is read-only")
        object.__setattr__(self, name, value)

    def __del__(self):
        handle = getattr(self, "_handle", None)
        if handle:
            _NATIVE.free(handle)
            self._handle = None

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self

    def __reduce__(self):
        return compile, (self.pattern, self.flags)

    @classmethod
    def __class_getitem__(cls, item):
        return _OwnedGenericAlias(cls, item)

    def __repr__(self):
        flags = self.flags & ~int(UNICODE)
        shown = repr(self.pattern)
        if len(shown) > 200:
            shown = shown[:200]
        suffix = f", {RegexFlag(flags)!r}" if flags else ""
        return f"re.compile({shown}{suffix})"

    def __eq__(self, other):
        if not isinstance(other, Pattern):
            return NotImplemented
        return (type(self.pattern), self.pattern, self.flags) == (type(other.pattern), other.pattern, other.flags)

    def __hash__(self):
        return hash((type(self.pattern), self.pattern, self.flags))

    def _cached_template(self, repl, string, length):
        raw = bytes(repl) if isinstance(repl, (bytearray, memoryview)) else repl
        templates = self._templates
        if templates is not None:
            cached = templates.get(raw, _MISSING)
            if cached is not _MISSING:
                return raw, cached

        _template(
            repl,
            Match(self, string, ((0, 0),) + (None,) * self.groups, None, 0, length),
            True,
        )
        escaped = b"\\" in raw if isinstance(raw, bytes) else "\\" in raw
        tokens = _template_tokens(raw, self) if escaped else None
        if templates is None:
            templates = {}
            self._templates = templates
        elif len(templates) >= 32:
            templates.clear()
        templates[raw] = tokens
        return raw, tokens

Pattern = _rust_bridge.pattern_type(Pattern)

for _pattern_descriptor in _rust_bridge.pattern_descriptors(Pattern):
    type.__setattr__(
        Pattern, _pattern_descriptor.__name__, _pattern_descriptor
    )

_rust_bridge.set_template(_template)


class Scanner:
    def __init__(self, lexicon, flags=0):
        self.lexicon = list(lexicon)
        if not self.lexicon:
            raise RuntimeError("invalid scanner lexicon")
        phrases = [item[0] for item in self.lexicon]
        byte_mode = isinstance(phrases[0], bytes)
        if any(isinstance(item, bytes) != byte_mode for item in phrases):
            raise TypeError("scanner patterns must all have the same type")
        separator = b"|" if byte_mode else "|"
        opening = b"(?:" if byte_mode else "(?:"
        closing = b")" if byte_mode else ")"
        self.scanner = compile(separator.join(opening + item + closing for item in phrases), flags)
        self._patterns = [compile(item, flags) for item in phrases]

    def scan(self, string):
        result = []
        position = 0
        length = _subject_length(string)
        while position < length:
            matched = None
            action = None
            for pattern, (_, candidate_action) in zip(self._patterns, self.lexicon):
                item = pattern.match(string, position)
                if item is not None:
                    matched = item
                    action = candidate_action
                    break
            if matched is None or matched.end() == position:
                break
            if callable(action):
                self.match = matched
                action = action(self, matched.group())
            if action is not None:
                result.append(action)
            position = matched.end()
        return result, _slice(string, position, length)


_CACHE = {}
_CACHE2 = {}
_MAX_CACHE = 512
_MAX_CACHE2 = 256


def _cache_pattern(key, pattern):
    if len(_CACHE) >= _MAX_CACHE:
        _CACHE.pop(next(iter(_CACHE)))
    _CACHE[key] = pattern
    if len(_CACHE2) >= _MAX_CACHE2:
        _CACHE2.pop(next(iter(_CACHE2)))
    _CACHE2[key] = pattern
    return pattern


def compile(pattern, flags=0):
    if isinstance(flags, RegexFlag):
        flags = flags.value
    try:
        return _CACHE2[type(pattern), pattern, flags]
    except KeyError:
        pass

    key = (type(pattern), pattern, flags)
    cached = _CACHE.pop(key, None)
    if cached is not None:
        return _cache_pattern(key, cached)

    if isinstance(pattern, Pattern):
        if flags:
            raise ValueError("cannot process flags argument with a compiled pattern")
        return pattern
    if not isinstance(pattern, (str, bytes)):
        raise TypeError("first argument must be string or compiled pattern")

    if isinstance(pattern, str) and flags & int(LOCALE):
        raise ValueError("cannot use LOCALE flag with a str pattern")
    if isinstance(pattern, bytes) and flags & int(UNICODE):
        raise ValueError("cannot use UNICODE flag with a bytes pattern")
    if isinstance(pattern, str) and flags & int(ASCII) and flags & int(UNICODE):
        raise ValueError("ASCII and UNICODE flags are incompatible")
    if isinstance(pattern, bytes) and flags & int(ASCII) and flags & int(LOCALE):
        raise ValueError("ASCII and LOCALE flags are incompatible")
    if flags > (1 << 31) - 1 or flags < -(1 << 31):
        raise OverflowError("Python int too large to convert to C int")
    implicit_unicode = int(UNICODE) if isinstance(pattern, str) and not flags & int(ASCII) else 0
    if (b"[" if isinstance(pattern, bytes) else "[") in pattern:
        _warn_ambiguous(pattern)
    native_flags = int(flags | implicit_unicode) & ((1 << 32) - 1)
    handle, groups, effective_flags, groupindex = _NATIVE.compile(pattern, native_flags)
    if flags < 0:
        effective_flags |= flags
    if isinstance(pattern, str) and ((flags & int(ASCII) and effective_flags & int(UNICODE)) or (flags & int(UNICODE) and effective_flags & int(ASCII))):
        _NATIVE.free(handle)
        raise ValueError("ASCII and UNICODE flags are incompatible")
    if isinstance(pattern, bytes) and ((flags & int(ASCII) and effective_flags & int(LOCALE)) or (flags & int(LOCALE) and effective_flags & int(ASCII))):
        _NATIVE.free(handle)
        raise ValueError("ASCII and LOCALE flags are incompatible")
    result = Pattern(pattern, effective_flags, handle, groups, groupindex)
    if flags & int(DEBUG):
        print(f"RUST-CONTINUATION groups={groups} flags={effective_flags}")
        return result
    return _cache_pattern(key, result)


def purge():
    _CACHE.clear()
    _CACHE2.clear()


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


def split(pattern, string, *args, maxsplit=_MISSING, flags=_MISSING):
    keyword_maxsplit = maxsplit is not _MISSING
    keyword_flags = flags is not _MISSING
    maxsplit = 0 if maxsplit is _MISSING else maxsplit
    flags = 0 if flags is _MISSING else flags
    if args:
        if len(args) > 2:
            raise TypeError(f"split() takes from 2 to 4 positional arguments but {len(args) + 2} were given")
        if keyword_maxsplit:
            raise TypeError("split() got multiple values for argument 'maxsplit'")
        if len(args) > 1 and keyword_flags:
            raise TypeError("split() got multiple values for argument 'flags'")
        warnings.warn("'maxsplit' is passed as positional argument", DeprecationWarning, skip_file_prefixes=_WARNING_PREFIX)
        maxsplit, flags = (args + (flags,))[:2]
    return compile(pattern, flags).split(string, maxsplit)


def sub(pattern, repl, string, *args, count=_MISSING, flags=_MISSING):
    keyword_count = count is not _MISSING
    keyword_flags = flags is not _MISSING
    count = 0 if count is _MISSING else count
    flags = 0 if flags is _MISSING else flags
    if args:
        if len(args) > 2:
            raise TypeError(f"sub() takes from 3 to 5 positional arguments but {len(args) + 3} were given")
        if keyword_count:
            raise TypeError("sub() got multiple values for argument 'count'")
        if len(args) > 1 and keyword_flags:
            raise TypeError("sub() got multiple values for argument 'flags'")
        warnings.warn("'count' is passed as positional argument", DeprecationWarning, skip_file_prefixes=_WARNING_PREFIX)
        count, flags = (args + (flags,))[:2]
    return compile(pattern, flags).sub(repl, string, count)


def subn(pattern, repl, string, *args, count=_MISSING, flags=_MISSING):
    keyword_count = count is not _MISSING
    keyword_flags = flags is not _MISSING
    count = 0 if count is _MISSING else count
    flags = 0 if flags is _MISSING else flags
    if args:
        if len(args) > 2:
            raise TypeError(f"subn() takes from 3 to 5 positional arguments but {len(args) + 3} were given")
        if keyword_count:
            raise TypeError("subn() got multiple values for argument 'count'")
        if len(args) > 1 and keyword_flags:
            raise TypeError("subn() got multiple values for argument 'flags'")
        warnings.warn("'count' is passed as positional argument", DeprecationWarning, skip_file_prefixes=_WARNING_PREFIX)
        count, flags = (args + (flags,))[:2]
    return compile(pattern, flags).subn(repl, string, count)


split.__text_signature__ = "(pattern, string, maxsplit=0, flags=0)"
sub.__text_signature__ = "(pattern, repl, string, count=0, flags=0)"
subn.__text_signature__ = "(pattern, repl, string, count=0, flags=0)"


def escape(pattern):
    if isinstance(pattern, str):
        return pattern.translate(_ESCAPE_MAP)
    return str(pattern, "latin1").translate(_ESCAPE_MAP).encode("latin1")


__all__ = ["match", "fullmatch", "search", "sub", "subn", "split", "findall", "finditer", "compile", "purge", "escape", "error", "Pattern", "Match", "A", "I", "L", "M", "S", "X", "U", "ASCII", "IGNORECASE", "LOCALE", "MULTILINE", "DOTALL", "VERBOSE", "UNICODE", "NOFLAG", "RegexFlag", "PatternError"]
