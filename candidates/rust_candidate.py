"""From-scratch Rust continuation-arena candidate with a dependency-free ctypes FFI."""

import ctypes
import enum
import os
import warnings


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
        if not self:
            return "re.NOFLAG"
        return super().__repr__()


A = ASCII = RegexFlag.ASCII
I = IGNORECASE = RegexFlag.IGNORECASE
L = LOCALE = RegexFlag.LOCALE
M = MULTILINE = RegexFlag.MULTILINE
S = DOTALL = RegexFlag.DOTALL
X = VERBOSE = RegexFlag.VERBOSE
U = UNICODE = RegexFlag.UNICODE
DEBUG = RegexFlag.DEBUG
NOFLAG = RegexFlag(0)
_BYTE = 1 << 20


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
            if self.lineno > 1:
                text += f" (line {self.lineno}, column {self.colno})"
        super().__init__(text)


error = PatternError


def _name_text(value):
    if isinstance(value, bytes):
        return value.decode("ascii", "backslashreplace")
    return value


class _Native:
    def __init__(self):
        path = os.path.join(os.path.dirname(__file__), "_rust_engine.so")
        self.library = ctypes.CDLL(path)
        u32p = ctypes.POINTER(ctypes.c_uint32)
        u8p = ctypes.POINTER(ctypes.c_uint8)
        ssizep = ctypes.POINTER(ctypes.c_ssize_t)
        lib = self.library
        lib.rebar_compile.argtypes = [u32p, ctypes.c_size_t, ctypes.c_uint32, ctypes.c_uint8]
        lib.rebar_compile.restype = ctypes.c_void_p
        lib.rebar_free.argtypes = [ctypes.c_void_p]
        lib.rebar_groups.argtypes = [ctypes.c_void_p]
        lib.rebar_groups.restype = ctypes.c_size_t
        lib.rebar_flags.argtypes = [ctypes.c_void_p]
        lib.rebar_flags.restype = ctypes.c_uint32
        lib.rebar_name_count.argtypes = [ctypes.c_void_p]
        lib.rebar_name_count.restype = ctypes.c_size_t
        lib.rebar_name_len.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        lib.rebar_name_len.restype = ctypes.c_size_t
        lib.rebar_name_group.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        lib.rebar_name_group.restype = ctypes.c_size_t
        lib.rebar_name_copy.argtypes = [ctypes.c_void_p, ctypes.c_size_t, u8p, ctypes.c_size_t]
        lib.rebar_name_copy.restype = ctypes.c_size_t
        lib.rebar_error_len.restype = ctypes.c_size_t
        lib.rebar_error_pos.restype = ctypes.c_ssize_t
        lib.rebar_error_include.restype = ctypes.c_uint8
        lib.rebar_error_copy.argtypes = [u8p, ctypes.c_size_t]
        lib.rebar_error_copy.restype = ctypes.c_size_t
        lib.rebar_match.argtypes = [ctypes.c_void_p, u32p, u32p, u8p, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_uint8, ctypes.c_uint8, ssizep, ssizep, ssizep]
        lib.rebar_match.restype = ctypes.c_int

    def error(self, pattern):
        size = self.library.rebar_error_len()
        output = (ctypes.c_uint8 * max(size, 1))()
        self.library.rebar_error_copy(output, size)
        message = bytes(output[:size]).decode("utf-8")
        position = self.library.rebar_error_pos()
        include = bool(self.library.rebar_error_include())
        raise PatternError(message, pattern if include else None, position if position >= 0 else None)

    def compile(self, pattern, flags):
        values = list(pattern) if isinstance(pattern, bytes) else [ord(char) for char in pattern]
        encoded = (ctypes.c_uint32 * max(len(values), 1))(*values)
        handle = self.library.rebar_compile(encoded, len(values), flags, int(isinstance(pattern, bytes)))
        if not handle:
            self.error(pattern)
        groups = self.library.rebar_groups(handle)
        effective_flags = self.library.rebar_flags(handle)
        names = {}
        for index in range(self.library.rebar_name_count(handle)):
            size = self.library.rebar_name_len(handle, index)
            output = (ctypes.c_uint8 * max(size, 1))()
            self.library.rebar_name_copy(handle, index, output, size)
            names[bytes(output[:size]).decode("utf-8")] = self.library.rebar_name_group(handle, index)
        return handle, groups, effective_flags, names

    def run(self, handle, string, groups, pos, endpos, mode, nonempty):
        if isinstance(string, bytes):
            chars = list(string)
            folds = [value + 32 if 65 <= value <= 90 else value for value in chars]
            masks = [int(48 <= value <= 57) | (int(value in (9, 10, 11, 12, 13, 32)) << 1) | (int((48 <= value <= 57) or (65 <= value <= 90) or (97 <= value <= 122)) << 2) for value in chars]
        else:
            chars = [ord(char) for char in string]
            folded = {"İ": ord("i"), "ı": ord("i"), "ſ": ord("s"), "K": ord("k")}
            folds = [folded.get(char, ord(char.lower()[0])) for char in string]
            masks = [int(char.isdecimal()) | (int(char.isspace()) << 1) | (int(char.isalnum()) << 2) for char in string]
        count = max(len(chars), 1)
        char_array = (ctypes.c_uint32 * count)(*chars)
        fold_array = (ctypes.c_uint32 * count)(*folds)
        mask_array = (ctypes.c_uint8 * count)(*masks)
        starts = (ctypes.c_ssize_t * (groups + 1))()
        ends = (ctypes.c_ssize_t * (groups + 1))()
        last = ctypes.c_ssize_t(-1)
        result = self.library.rebar_match(handle, char_array, fold_array, mask_array, len(chars), pos, endpos, mode, int(nonempty), starts, ends, ctypes.byref(last))
        if result < 0:
            raise RuntimeError("Rust continuation engine rejected the FFI call")
        if not result:
            return None
        spans = tuple(None if starts[index] < 0 else (starts[index], ends[index]) for index in range(groups + 1))
        return spans, None if last.value < 0 else last.value


_NATIVE = _Native()


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
            opening = -1
        elif char == "&" and opening >= 0 and index + 1 < len(text) and text[index + 1] == "&":
            warnings.warn(f"Possible set intersection at position {index}", FutureWarning, stacklevel=4)
            return


def _template(value, match):
    if not isinstance(value, (str, bytes)):
        raise TypeError("decoding to str: need a bytes-like object, function found")
    byte_mode = isinstance(match.string, bytes)
    if byte_mode != isinstance(value, bytes):
        expected = "bytes-like object" if byte_mode else "str instance"
        actual = "str" if isinstance(value, str) else "bytes"
        raise TypeError(f"sequence item 0: expected a {expected}, {actual} found")
    text = value.decode("latin1") if isinstance(value, bytes) else value
    output = []
    index = 0
    simple = {"a": "\a", "b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t", "v": "\v", "\\": "\\"}
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
        if char == "g" and index < len(text) and text[index] == "<":
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
            if name.isdecimal():
                number = int(name)
                if number > match.re.groups:
                    raise PatternError(f"invalid group reference {number}", value, name_start)
            else:
                if not name.isidentifier() or (byte_mode and not name.isascii()):
                    raise PatternError(f"bad character in group name {name!r}", value, name_start)
                if name not in match.re.groupindex:
                    raise IndexError(f"unknown group name {name!r}")
                number = match.re.groupindex[name]
            part = match.group(number)
            output.append("" if part is None else part.decode("latin1") if isinstance(part, bytes) else part)
        elif char.isdigit():
            digits = char
            if index < len(text) and text[index].isdigit():
                digits += text[index]
                index += 1
            number = int(digits)
            if number > match.re.groups:
                raise PatternError(f"invalid group reference {number}", value, slash + 1)
            part = match.group(number)
            output.append("" if part is None else part.decode("latin1") if isinstance(part, bytes) else part)
        elif char in simple:
            output.append(simple[char])
        elif char.isalpha():
            raise PatternError(f"bad escape \\{char}", value, slash)
        else:
            output.append("\\" + char)
    joined = "".join(output)
    return joined.encode("latin1") if byte_mode else joined


class Match:
    __slots__ = ("_pattern", "_string", "_spans", "_lastindex", "pos", "endpos")

    def __init__(self, pattern, string, spans, lastindex, pos, endpos):
        self._pattern = pattern
        self._string = string
        self._spans = spans
        self._lastindex = lastindex
        self.pos = pos
        self.endpos = endpos

    @property
    def re(self):
        return self._pattern

    @property
    def string(self):
        return self._string

    @property
    def regs(self):
        return tuple((-1, -1) if value is None else value for value in self._spans)

    @property
    def lastindex(self):
        return self._lastindex

    @property
    def lastgroup(self):
        return next((name for name, index in self._pattern.groupindex.items() if index == self._lastindex), None)

    def _number(self, group):
        if isinstance(group, str):
            if group not in self._pattern.groupindex:
                raise IndexError("no such group")
            return self._pattern.groupindex[group]
        if not isinstance(group, int) or group < 0 or group > self._pattern.groups:
            raise IndexError("no such group")
        return group

    def group(self, *groups):
        if not groups:
            groups = (0,)
        values = []
        for group in groups:
            span = self._spans[self._number(group)]
            values.append(None if span is None else self._string[span[0]:span[1]])
        return values[0] if len(values) == 1 else tuple(values)

    def __getitem__(self, group):
        return self.group(group)

    def groups(self, default=None):
        return tuple(default if item is None else self._string[item[0]:item[1]] for item in self._spans[1:])

    def groupdict(self, default=None):
        return {name: default if self._spans[number] is None else self._string[self._spans[number][0]:self._spans[number][1]] for name, number in self._pattern.groupindex.items()}

    def start(self, group=0):
        span = self._spans[self._number(group)]
        return -1 if span is None else span[0]

    def end(self, group=0):
        span = self._spans[self._number(group)]
        return -1 if span is None else span[1]

    def span(self, group=0):
        value = self._spans[self._number(group)]
        return (-1, -1) if value is None else value

    def expand(self, template):
        return _template(template, self)


class _Scanner:
    __slots__ = ("pattern", "_string", "_pos", "_empty")

    def __init__(self, pattern, string):
        self.pattern = pattern
        self._string = string
        self._pos = 0
        self._empty = False

    def search(self):
        result = self.pattern._search(self._string, self._pos, len(self._string), self._empty, 0)
        if result is None:
            self._pos = len(self._string) + 1
            return None
        self._empty = result.end() == result.start()
        self._pos = result.end() if not self._empty else result.start()
        return result

    def match(self):
        if self._pos > len(self._string):
            return None
        result = self.pattern._at(self._string, self._pos, len(self._string), 0, self._empty)
        if result is None:
            self._pos = len(self._string) + 1
            return None
        self._empty = result.end() == result.start()
        self._pos = result.end() if not self._empty else result.start() + 1
        return result


class Pattern:
    __slots__ = ("pattern", "flags", "groups", "groupindex", "_handle")

    def __init__(self, value, flags, handle, groups, groupindex):
        self.pattern = value
        self.flags = flags
        self.groups = groups
        self.groupindex = groupindex
        self._handle = handle

    def __del__(self):
        handle = getattr(self, "_handle", None)
        if handle:
            _NATIVE.library.rebar_free(handle)
            self._handle = None

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self

    def __reduce__(self):
        return compile, (self.pattern, self.flags)

    def _validate_string(self, string):
        if not isinstance(string, (str, bytes)):
            raise TypeError(f"expected string or bytes-like object, got '{type(string).__name__}'")
        if isinstance(self.pattern, str) and isinstance(string, bytes):
            raise TypeError("cannot use a string pattern on a bytes-like object")
        if isinstance(self.pattern, bytes) and isinstance(string, str):
            raise TypeError("cannot use a bytes pattern on a string-like object")

    def _at(self, string, start, endpos, original_pos, require_nonempty=False):
        self._validate_string(string)
        result = _NATIVE.run(self._handle, string, self.groups, start, endpos, 1, require_nonempty)
        if result is None:
            return None
        spans, last = result
        return Match(self, string, spans, last, original_pos, endpos)

    def _search(self, string, pos, endpos, require_nonempty=False, original_pos=None):
        self._validate_string(string)
        if pos > endpos:
            return None
        for start in range(pos, endpos + 1):
            result = self._at(string, start, endpos, pos if original_pos is None else original_pos, require_nonempty and start == pos)
            if result is not None:
                return result
        return None

    def search(self, string, pos=0, endpos=None):
        end = len(string) if endpos is None else min(max(endpos, 0), len(string))
        return self._search(string, max(pos, 0), end)

    def match(self, string, pos=0, endpos=None):
        end = len(string) if endpos is None else min(max(endpos, 0), len(string))
        return self._at(string, max(pos, 0), end, max(pos, 0)) if pos <= end else None

    def fullmatch(self, string, pos=0, endpos=None):
        end = len(string) if endpos is None else min(max(endpos, 0), len(string))
        self._validate_string(string)
        start = max(pos, 0)
        result = _NATIVE.run(self._handle, string, self.groups, start, end, 2, False)
        if result is None:
            return None
        spans, last = result
        return Match(self, string, spans, last, start, end)

    def finditer(self, string, pos=0, endpos=None):
        end = len(string) if endpos is None else min(max(endpos, 0), len(string))
        current = max(pos, 0)
        empty = False
        while current <= end:
            result = self._search(string, current, end, empty, max(pos, 0))
            if result is None:
                break
            yield result
            if result.start() == result.end():
                empty = True
                current = result.start()
            else:
                current = result.end()
                empty = False

    def findall(self, string, pos=0, endpos=None):
        empty = b"" if isinstance(string, bytes) else ""
        output = []
        for item in self.finditer(string, pos, endpos):
            if self.groups == 0:
                output.append(item.group(0))
            elif self.groups == 1:
                value = item.group(1)
                output.append(empty if value is None else value)
            else:
                output.append(tuple(empty if value is None else value for value in item.groups()))
        return output

    def split(self, string, maxsplit=0):
        result = []
        previous = 0
        count = 0
        for item in self.finditer(string):
            if maxsplit and count >= maxsplit:
                break
            result.append(string[previous:item.start()])
            result.extend(item.groups())
            previous = item.end()
            count += 1
        result.append(string[previous:])
        return result

    def subn(self, repl, string, count=0):
        self._validate_string(string)
        parts = []
        previous = 0
        replacements = 0
        for item in self.finditer(string):
            if count and replacements >= count:
                break
            parts.append(string[previous:item.start()])
            value = repl(item) if callable(repl) else item.expand(repl)
            if isinstance(string, bytes) != isinstance(value, bytes):
                expected = "bytes-like object" if isinstance(string, bytes) else "str instance"
                raise TypeError(f"sequence item {len(parts)}: expected a {expected}, {type(value).__name__} found")
            parts.append(value)
            previous = item.end()
            replacements += 1
        parts.append(string[previous:])
        return (b"" if isinstance(string, bytes) else "").join(parts), replacements

    def sub(self, repl, string, count=0):
        return self.subn(repl, string, count)[0]

    def scanner(self, string):
        self._validate_string(string)
        return _Scanner(self, string)


_CACHE = {}


def compile(pattern, flags=0):
    flags = int(flags)
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
    key = (type(pattern), pattern, flags)
    if key in _CACHE:
        return _CACHE[key]
    implicit_unicode = int(UNICODE) if isinstance(pattern, str) and not flags & int(ASCII) else 0
    _warn_ambiguous(pattern)
    handle, groups, effective_flags, groupindex = _NATIVE.compile(pattern, flags | implicit_unicode)
    result = Pattern(pattern, effective_flags, handle, groups, groupindex)
    _CACHE[key] = result
    if flags & int(DEBUG):
        print(f"RUST-CONTINUATION groups={groups} flags={effective_flags}")
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


def split(pattern, string, maxsplit=0, flags=0):
    return compile(pattern, flags).split(string, maxsplit)


def sub(pattern, repl, string, count=0, flags=0):
    return compile(pattern, flags).sub(repl, string, count)


def subn(pattern, repl, string, count=0, flags=0):
    return compile(pattern, flags).subn(repl, string, count)


def escape(pattern):
    special = set("()[]{}?*+-|^$\\.&~# \t\n\r\v\f")
    if isinstance(pattern, bytes):
        return b"".join((b"\\" + bytes([char])) if chr(char) in special else bytes([char]) for char in pattern)
    return "".join("\\" + char if char in special else char for char in pattern)


__all__ = ["match", "fullmatch", "search", "sub", "subn", "split", "findall", "finditer", "compile", "purge", "escape", "error", "Pattern", "Match", "A", "I", "L", "M", "S", "X", "U", "ASCII", "IGNORECASE", "LOCALE", "MULTILINE", "DOTALL", "VERBOSE", "UNICODE", "NOFLAG", "RegexFlag", "PatternError"]
