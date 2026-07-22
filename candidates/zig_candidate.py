"""From-scratch capture-aware Zig bytecode candidate with a dependency-free native bridge."""

import ctypes
import enum
import operator
import os
import types
import unicodedata
import warnings

from candidates import _zig_bridge


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


class _Native:
    def __init__(self):
        path = os.path.join(os.path.dirname(__file__), "_zig_probe.so")
        self.library = ctypes.CDLL(path)
        lib = self.library
        lib.rebar_zig_compile.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32]
        lib.rebar_zig_compile.restype = ctypes.c_void_p
        lib.rebar_zig_free.argtypes = [ctypes.c_void_p]
        lib.rebar_zig_groups.argtypes = [ctypes.c_void_p]
        lib.rebar_zig_groups.restype = ctypes.c_size_t
        lib.rebar_zig_flags.argtypes = [ctypes.c_void_p]
        lib.rebar_zig_flags.restype = ctypes.c_uint32
        lib.rebar_zig_name_count.argtypes = [ctypes.c_void_p]
        lib.rebar_zig_name_count.restype = ctypes.c_size_t
        lib.rebar_zig_name_length.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        lib.rebar_zig_name_length.restype = ctypes.c_size_t
        lib.rebar_zig_name_group.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        lib.rebar_zig_name_group.restype = ctypes.c_size_t
        lib.rebar_zig_name_copy.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t]
        lib.rebar_zig_name_copy.restype = ctypes.c_size_t

    def compile(self, pattern, flags):
        native_flags = flags
        if isinstance(pattern, bytes):
            raw = pattern
        else:
            named = _named_escapes(pattern)
            if named:
                pieces = []
                previous = 0
                for slash, value in named:
                    close = pattern.index("}", slash + 3)
                    pieces.extend((pattern[previous:slash], chr(value)))
                    previous = close + 1
                pieces.append(pattern[previous:])
                native_pattern = "".join(pieces)
            else:
                native_pattern = pattern
            raw = native_pattern.encode("utf-8", "surrogatepass")
            native_flags |= 0x80000000
        handle = self.library.rebar_zig_compile(raw, len(raw), native_flags)
        if not handle:
            raise PatternError("unsupported or invalid Zig pattern", pattern, 0)
        groups = self.library.rebar_zig_groups(handle)
        effective_flags = self.library.rebar_zig_flags(handle)
        names = {}
        for index in range(self.library.rebar_zig_name_count(handle)):
            length = self.library.rebar_zig_name_length(handle, index)
            value = ctypes.create_string_buffer(length)
            self.library.rebar_zig_name_copy(handle, index, value, length)
            names[value.raw.decode("ascii")] = self.library.rebar_zig_name_group(handle, index)
        return handle, groups, effective_flags, names

    def run(self, handle, string, groups, pos, endpos, mode, nonempty):
        return _zig_bridge.match(handle, string, pos, endpos, mode, nonempty)

    def collect(self, handle, string, groups, pos, endpos):
        return _zig_bridge.collect(handle, string, groups, pos, endpos)

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
        if pattern[index:index + 1] == "N" and pattern[index + 1:index + 2] != "{":
            raise PatternError("missing {", pattern, slash + 2)
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
            opening = -1
        elif opening >= 0:
            if char == "[" and index == opening + 1:
                warnings.warn(f"Possible nested set at position {index}", FutureWarning, skip_file_prefixes=_WARNING_PREFIX)
            for marker, label in (("&&", "intersection"), ("||", "union"), ("~~", "symmetric difference"), ("--", "difference")):
                if text[index:index + 2] == marker:
                    warnings.warn(f"Possible set {label} at position {index}", FutureWarning, skip_file_prefixes=_WARNING_PREFIX)


def _preflight_pattern(pattern, flags):
    """Validate syntax and preserve Python-compatible errors before Zig compilation."""
    byte_mode = isinstance(pattern, bytes)
    text = pattern.decode("latin1") if byte_mode else pattern
    length = len(text)
    groups = {}
    group_count = 0
    open_groups = []
    variable_groups = set()
    lookbehind_bases = []
    conditionals = []
    conditional_branches = {}
    stack = []
    active_flags = flags
    root_prefix = True
    can_repeat = False
    repeated = False

    def fail(message, position=None, keep_pattern=True):
        raise PatternError(message, pattern if keep_pattern else None, position)

    def group_name(name, position):
        valid = bool(name) and (name.isascii() and name.isidentifier() if byte_mode else name.isidentifier())
        if not valid:
            shown = ascii(name) if byte_mode else repr(name)
            fail(f"bad character in group name {shown}", position)

    def escape_at(start, in_class=False):
        if start + 1 >= length:
            fail("bad escape (end of pattern)", start)
        code = text[start + 1]
        if code in "xXuU":
            widths = {"x": 2, "u": 4, "U": 8}
            if code == "X":
                fail(r"bad escape \X", start)
            if byte_mode and code in "uU":
                fail(f"bad escape \\{code}", start)
            width = widths[code]
            end = start + 2
            while end < length and end < start + 2 + width and text[end] in "0123456789abcdefABCDEF":
                end += 1
            if end != start + 2 + width:
                fail(f"incomplete escape {text[start:end]}", start)
            value = int(text[start + 2:end], 16)
            if code == "U" and value > 0x10ffff:
                fail(f"bad escape {text[start:end]}", start)
            return end, False, text[start:end]
        if code == "N":
            if byte_mode:
                fail(r"bad escape \N", start)
            if start + 2 >= length or text[start + 2] != "{":
                fail("missing {", start + 2)
            close = text.find("}", start + 3)
            if close == start + 3:
                fail("missing character name", start + 3)
            if close < 0:
                fail("missing character name" if start + 3 == length else "missing }, unterminated name", start + 3)
            name = text[start + 3:close]
            try:
                value = unicodedata.lookup(name)
            except KeyError:
                fail(f"undefined character name {name!r}", start)
            if len(value) != 1:
                fail(f"undefined character name {name!r}", start)
            return close + 1, False, text[start:close + 1]
        if code in "dDsSwW":
            return start + 2, True, "\\" + code
        if code.isdigit():
            end = start + 2
            while end < length and text[end] in "01234567" and end < start + 4:
                end += 1
            digits = text[start + 1:end]
            if code == "0" or in_class or len(digits) == 3 and code in "01234567":
                if code not in "01234567":
                    fail(f"bad escape \\{code}", start)
                value = int(digits, 8)
                if value > 0o377:
                    fail(f"octal escape value \\{digits} outside of range 0-0o377", start)
                return end, False, text[start:end]
            if in_class:
                fail(f"bad escape \\{code}", start)
            number = int(digits[:2])
            if number > group_count:
                fail(f"invalid group reference {number}", start + 1)
            if number in open_groups:
                fail("cannot refer to an open group", start)
            if lookbehind_bases and number > lookbehind_bases[0]:
                fail("cannot refer to group defined in the same lookbehind subpattern", start + 1 + len(str(number)))
            return start + 1 + len(str(number)), False, text[start:start + 1 + len(str(number))]
        allowed = "abfnrtv" if in_class else "abfnrtvABZzb"
        if code.isascii() and code.isalpha() and code not in allowed:
            fail(f"bad escape \\{code}", start)
        return start + 2, False, "\\" + code

    def scalar(value):
        if not value.startswith("\\"):
            return ord(value)
        code = value[1]
        if code in "xuU":
            return int(value[2:], 16)
        if code == "N":
            return ord(unicodedata.lookup(value[3:-1]))
        if code in "01234567":
            return int(value[1:], 8)
        return ord({"a": "\a", "b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t", "v": "\v"}.get(code, code))

    def scan_class(opening):
        index = opening + 1
        if index < length and text[index] == "^":
            index += 1
        first = True
        previous = None
        previous_category = False
        while index < length:
            if text[index] == "]" and not first:
                return index + 1
            first = False
            if text[index] == "\\":
                end, category_value, value = escape_at(index, True)
            else:
                end, category_value, value = index + 1, False, text[index]
            if value == "-" and previous is not None and end < length and text[end] != "]":
                if previous_category:
                    fail(f"bad character range {previous}-" + (text[end:end + 2] if text[end:end + 1] == "\\" else text[end:end + 1]), opening + 1)
                if text[end] == "\\":
                    right_end, right_category, right = escape_at(end, True)
                else:
                    right_end, right_category, right = end + 1, False, text[end]
                if right_category:
                    fail(f"bad character range {previous}-{right}", opening + 1)
                if scalar(right) < scalar(previous):
                    fail(f"bad character range {previous}-{right}", opening + 1)
                index = right_end
                previous = None
                previous_category = False
                continue
            previous, previous_category = value, category_value
            index = end
        fail("unterminated character set", opening)

    index = 0
    while index < length:
        char = text[index]
        if active_flags & int(VERBOSE):
            if char in " \t\n\r\v\f":
                index += 1
                continue
            if char == "#":
                end = text.find("\n", index)
                index = length if end < 0 else end + 1
                continue
        if char == "\\":
            index, _, _ = escape_at(index)
            can_repeat, repeated, root_prefix = True, False, False
            continue
        if char == "[":
            index = scan_class(index)
            can_repeat, repeated, root_prefix = True, False, False
            continue
        if char == "(":
            opening = index
            if text.startswith("(?#", index):
                close = text.find(")", index + 3)
                if close < 0:
                    fail("missing ), unterminated comment", opening)
                index = close + 1
                continue
            capture = False
            group_number = None
            kind = "group"
            if text.startswith("(?P<", index):
                close = text.find(">", index + 4)
                if close < 0:
                    fail("missing group name" if index + 4 == length else "missing >, unterminated name", index + 4)
                name = text[index + 4:close]
                if not name:
                    fail("missing group name", index + 4)
                group_name(name, index + 4)
                group_count += 1
                group_number = group_count
                if name in groups:
                    fail(f"redefinition of group name {name!r} as group {group_number}; was group {groups[name]}", index + 4)
                groups[name] = group_number
                capture = True
                index = close + 1
            elif text.startswith("(?P=", index):
                close = text.find(")", index + 4)
                if close < 0:
                    fail("missing group name" if index + 4 == length else "missing ), unterminated name", index + 4)
                name = text[index + 4:close]
                if not name:
                    fail("missing group name", index + 4)
                group_name(name, index + 4)
                if name not in groups:
                    fail(f"unknown group name {name!r}", index + 4)
                if groups[name] in open_groups:
                    fail(f"cannot refer to an open group", index + 4)
                if lookbehind_bases and groups[name] > lookbehind_bases[0]:
                    fail("cannot refer to group defined in the same lookbehind subpattern", close + 1)
                index = close + 1
                can_repeat, repeated, root_prefix = True, False, False
                continue
            elif text.startswith("(?(", index):
                close = text.find(")", index + 3)
                if close < 0:
                    fail("missing group name" if index + 3 == length else "missing ), unterminated name", index + 3)
                reference = text[index + 3:close]
                if not reference:
                    fail("missing group name", index + 3)
                if reference.isascii() and reference.isdigit():
                    number = int(reference)
                    if number == 0:
                        fail("bad group number", index + 3)
                    if lookbehind_bases and number > group_count:
                        fail("cannot refer to an open group", close + 1)
                    if lookbehind_bases and number > lookbehind_bases[0]:
                        fail("cannot refer to group defined in the same lookbehind subpattern", close + 1)
                    conditionals.append((number, index + 3))
                else:
                    group_name(reference, index + 3)
                    if reference not in groups:
                        fail(f"unknown group name {reference!r}", index + 3)
                    if lookbehind_bases and groups[reference] > lookbehind_bases[0]:
                        fail("cannot refer to group defined in the same lookbehind subpattern", close + 1)
                kind = "conditional"
                conditional_branches[opening] = 0
                index = close + 1
            elif text.startswith(("(?<=", "(?<!"), index):
                index += 4
                stack.append((opening, active_flags, can_repeat, repeated, None, "lookbehind"))
                lookbehind_bases.append(group_count)
                can_repeat = repeated = False
                root_prefix = False
                continue
            elif text.startswith(("(?=", "(?!", "(?:", "(?>"), index):
                index += 3
            elif text.startswith("(?", index):
                if index + 2 >= length:
                    fail("unexpected end of pattern", index + 2)
                first = text[index + 2]
                if first == "P" and not text.startswith(("(?P<", "(?P="), index):
                    if index + 3 >= length:
                        fail("unexpected end of pattern", index + 3)
                    fail(f"unknown extension ?P{text[index + 3]}", index + 1)
                if first == "<" and not text.startswith(("(?<=", "(?<!"), index):
                    if index + 3 >= length:
                        fail("unexpected end of pattern", index + 3)
                    fail(f"unknown extension ?<{text[index + 3]}", index + 1)
                if first not in "aiLmsux-":
                    fail(f"unknown extension ?{first}", index + 1)
                cursor = index + 2
                adding = set()
                removing = set()
                removed = False
                while cursor < length and text[cursor] not in ":)":
                    mark = text[cursor]
                    if mark == "-":
                        if removed:
                            fail("missing flag", cursor)
                        removed = True
                        cursor += 1
                        continue
                    allowed = "aiLmsux" if byte_mode else "aLimsux"
                    if mark not in allowed:
                        if mark in "*+?{":
                            if not removed:
                                fail("missing -, : or )", cursor)
                            fail("missing :" if removing else "missing flag", cursor)
                        fail("unknown flag", cursor)
                    target = removing if removed else adding
                    target.add(mark)
                    cursor += 1
                if cursor >= length:
                    if removed and not removing:
                        fail("missing flag", cursor)
                    fail("missing :" if removed else "missing -, : or )", cursor)
                if removed and not removing:
                    fail("missing flag", cursor)
                common = adding & removing
                if common:
                    fail("bad inline flags: flag turned on and off", cursor)
                type_flags = (adding | removing) & {"a", "u", "L"}
                if type_flags & removing:
                    fail("bad inline flags: cannot turn off flags 'a', 'u' and 'L'", cursor)
                if byte_mode and "u" in adding:
                    fail("bad inline flags: cannot use 'u' flag with a bytes pattern", index + 3 + next(item for item, mark in enumerate(text[index + 2:cursor]) if mark == "u"))
                if not byte_mode and "L" in adding:
                    fail("bad inline flags: cannot use 'L' flag with a str pattern", index + 3 + next(item for item, mark in enumerate(text[index + 2:cursor]) if mark == "L"))
                if len(type_flags) > 1:
                    fail("bad inline flags: flags 'a', 'u' and 'L' are incompatible", cursor)
                bits = {"i": int(IGNORECASE), "L": int(LOCALE), "m": int(MULTILINE), "s": int(DOTALL), "x": int(VERBOSE), "a": int(ASCII), "u": int(UNICODE)}
                local_flags = active_flags
                for mark in adding:
                    if mark in "aLu":
                        local_flags &= ~(int(ASCII) | int(LOCALE) | int(UNICODE))
                    local_flags |= bits[mark]
                for mark in removing:
                    local_flags &= ~bits[mark]
                if text[cursor] == ")":
                    if removed:
                        fail("missing :", cursor)
                    if stack or not root_prefix:
                        fail("global flags not at the start of the expression", opening)
                    active_flags = local_flags
                    index = cursor + 1
                    continue
                stack.append((opening, active_flags, can_repeat, repeated, None, "group"))
                active_flags = local_flags
                can_repeat = repeated = False
                root_prefix = False
                index = cursor + 1
                continue
            else:
                group_count += 1
                group_number = group_count
                capture = True
                index += 1
            stack.append((opening, active_flags, can_repeat, repeated, group_number if capture else None, kind))
            if capture:
                open_groups.append(group_number)
            can_repeat = repeated = False
            root_prefix = False
            continue
        if char == ")":
            if not stack:
                fail("unbalanced parenthesis", index)
            opening, parent_flags, _, _, group_number, kind = stack.pop()
            if group_number is not None:
                open_groups.remove(group_number)
                body = text[opening + 1:index]
                variable = "*" in body or "+" in body or "|" in body or any(body[offset] == "?" and (offset == 0 or body[offset - 1] != "(") for offset in range(len(body)))
                variable = variable or any("," in value and value.split(",", 1)[0] != value.split(",", 1)[1] for value in (part.split("}", 1)[0] for part in body.split("{")[1:]))
                if variable:
                    variable_groups.add(group_number)
            if kind == "lookbehind":
                body = text[opening + 4:index]
                lookbehind_bases.pop()
                variable = "*" in body or "+" in body or any(body[offset] == "?" and (offset == 0 or body[offset - 1] != "(") for offset in range(len(body)))
                variable = variable or any("," in value and value.split(",", 1)[0] != value.split(",", 1)[1] for value in (part.split("}", 1)[0] for part in body.split("{")[1:]))
                variable = variable or any(f"\\{number}" in body or any(f"(?P={name})" in body for name, value in groups.items() if value == number) for number in variable_groups)
                if variable:
                    fail("look-behind requires fixed-width pattern", keep_pattern=False)
            active_flags = parent_flags
            can_repeat, repeated = kind != "lookbehind", False
            index += 1
            continue
        if char == "|":
            if stack and stack[-1][-1] == "conditional":
                opening = stack[-1][0]
                conditional_branches[opening] += 1
                if conditional_branches[opening] > 1:
                    fail("conditional backref with more than two branches", index)
            can_repeat = repeated = False
            root_prefix = False
            index += 1
            continue
        if char in "^$":
            can_repeat = repeated = False
            root_prefix = False
            index += 1
            continue
        if char in "*+?" or char == "{":
            quantifier_start = index
            end = index + 1
            if char == "{":
                cursor = index + 1
                while cursor < length and text[cursor].isdigit():
                    cursor += 1
                first = text[index + 1:cursor]
                second = first
                if cursor < length and text[cursor] == ",":
                    cursor += 1
                    end_digits = cursor
                    while cursor < length and text[cursor].isdigit():
                        cursor += 1
                    second = text[end_digits:cursor]
                if cursor >= length or text[cursor] != "}" or not first and not second:
                    can_repeat, repeated, root_prefix = True, False, False
                    index += 1
                    continue
                minimum = int(first or 0)
                maximum = int(second) if second else None
                if maximum is not None and minimum > maximum:
                    fail("min repeat greater than max repeat", quantifier_start + 1)
                end = cursor + 1
            if not can_repeat:
                fail("nothing to repeat", quantifier_start)
            if repeated:
                fail("multiple repeat", quantifier_start)
            if end < length and text[end] in "?+":
                end += 1
            can_repeat, repeated, root_prefix = True, True, False
            index = end
            continue
        can_repeat, repeated, root_prefix = True, False, False
        index += 1

    if stack:
        fail("missing ), unterminated subpattern", stack[0][0])
    for number, position in conditionals:
        if number > group_count:
            fail(f"invalid group reference {number}", position)


def _may_accept_invalid_pattern(pattern):
    """Quickly find the few invalid forms the native parser can otherwise accept."""
    text = pattern.decode("latin1") if isinstance(pattern, bytes) else pattern
    byte_mode = isinstance(pattern, bytes)
    length = len(text)
    if text.startswith("{") or "(?:{" in text:
        return True
    slash = text.find("\\")
    while slash >= 0 and slash + 1 < length:
        code = text[slash + 1]
        if code in "dDsSwW" and (slash and text[slash - 1] == "-" or slash + 2 < length and text[slash + 2] == "-"):
            return True
        if byte_mode and code == "N":
            return True
        if code in "ABZzN89":
            opening = text.rfind("[", 0, slash)
            closing = text.rfind("]", 0, slash)
            if opening > closing:
                return True
        if code.isascii() and code.isalpha() and code not in "abfnrtvABZzbdDsSwWxuUN":
            return True
        slash = text.find("\\", slash + 2)
    group = text.find("(?")
    while group >= 0:
        cursor = group + 2
        if cursor >= length or text[cursor] not in "aiLmsux-":
            group = text.find("(?", cursor)
            continue
        adding = set()
        removing = set()
        removed = False
        while cursor < length and text[cursor] in "aiLmsux-":
            mark = text[cursor]
            if mark == "-":
                removed = True
            elif removed:
                removing.add(mark)
            else:
                adding.add(mark)
            cursor += 1
        type_flags = (adding | removing) & {"a", "u", "L"}
        if adding & removing or len(type_flags) > 1 or byte_mode and "u" in adding or not byte_mode and "L" in adding or removed and cursor < length and text[cursor] == ")" or cursor < length and text[cursor] == ")" and (group or cursor + 1 < length and text[cursor + 1] in "*+?{"):
            return True
        group = text.find("(?", group + 2)
    return False


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
    return memoryview(value).cast("B")[start:end].tobytes()


def _subject_length(value):
    if isinstance(value, str):
        return len(value)
    return memoryview(value).nbytes


class Match:
    __module__ = "re"
    __slots__ = ("_pattern", "_string", "_spans", "_lastindex", "pos", "endpos")

    def __init__(self, pattern, string, spans, lastindex, pos, endpos):
        self._pattern = pattern
        self._string = string
        self._spans = spans
        self._lastindex = lastindex
        self.pos = pos
        self.endpos = endpos

    @classmethod
    def __class_getitem__(cls, item):
        return types.GenericAlias(cls, item)

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self

    def __reduce__(self):
        raise TypeError("cannot pickle 're.Match' object")

    def __repr__(self):
        return f"<re.Match object; span={self.span()}, match={repr(self.group(0))[:50]}>"

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
        try:
            group = operator.index(group)
        except TypeError:
            raise IndexError("no such group") from None
        if group < 0 or group > self._pattern.groups:
            raise IndexError("no such group")
        return group

    def group(self, *groups):
        if not groups:
            groups = (0,)
        values = []
        for group in groups:
            span = self._spans[self._number(group)]
            values.append(None if span is None else _slice(self._string, span[0], span[1]))
        return values[0] if len(values) == 1 else tuple(values)

    def __getitem__(self, group):
        return self.group(group)

    def groups(self, default=None):
        return tuple(default if item is None else _slice(self._string, item[0], item[1]) for item in self._spans[1:])

    def groupdict(self, default=None):
        return {name: default if self._spans[number] is None else _slice(self._string, self._spans[number][0], self._spans[number][1]) for name, number in self._pattern.groupindex.items()}

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
        raw = bytes(template) if isinstance(template, (bytearray, memoryview)) else template
        tokens = self.re._templates.get(raw)
        if tokens is None:
            _template(template, self, True)
            tokens = _template_tokens(raw, self.re)
            if len(self.re._templates) >= 32:
                self.re._templates.clear()
            self.re._templates[raw] = tokens
        return _expand_tokens(tokens, self, isinstance(raw, bytes))


class _Scanner:
    __slots__ = ("pattern", "_string", "_pos", "_start", "_end", "_empty", "_pending")

    def __init__(self, pattern, string, pos=0, endpos=None):
        self.pattern = pattern
        self._string = string
        self._start = self._pos = max(pos, 0)
        length = _subject_length(string)
        self._end = length if endpos is None else min(max(endpos, 0), length)
        self._empty = False
        self._pending = None

    def search(self):
        if isinstance(self._string, (str, bytes)) and (self._pending is not None or not self._empty):
            if self._pending is None:
                self._pending = iter(_NATIVE.collect(self.pattern._handle, self._string, self.pattern.groups, self._pos, self._end))
            item = next(self._pending, None)
            result = None if item is None else Match(self.pattern, self._string, item[0], item[1], self._start, self._end)
        else:
            result = self.pattern._search(self._string, self._pos, self._end, self._empty, self._start)
        if result is None:
            self._pos = self._end + 1
            return None
        self._empty = result.end() == result.start()
        self._pos = result.end() if not self._empty else result.start()
        return result

    def match(self):
        self._pending = None
        if self._pos > self._end:
            return None
        result = self.pattern._at(self._string, self._pos, self._end, self._start, self._empty)
        if result is None:
            self._pos = self._end + 1
            return None
        self._empty = result.end() == result.start()
        self._pos = result.end()
        return result


class Pattern:
    __slots__ = ("pattern", "flags", "groups", "groupindex", "_handle", "_literal", "_templates", "__weakref__")

    def __init__(self, value, flags, handle, groups, groupindex):
        self.pattern = value
        self.flags = flags
        self.groups = groups
        self.groupindex = types.MappingProxyType(dict(groupindex))
        self._handle = handle
        metacharacters = b".^$*+?{}[]\\|()" if isinstance(value, bytes) else ".^$*+?{}[]\\|()"
        self._literal = value if value and not flags & int(IGNORECASE) and not any(char in metacharacters for char in value) else None
        self._templates = {}

    def __del__(self):
        handle = getattr(self, "_handle", None)
        if handle:
            _NATIVE.library.rebar_zig_free(handle)
            self._handle = None

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self

    def __reduce__(self):
        return compile, (self.pattern, self.flags)

    @classmethod
    def __class_getitem__(cls, item):
        return types.GenericAlias(cls, item)

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

    def _validate_string(self, string):
        if not isinstance(string, str):
            try:
                contiguous = memoryview(string).c_contiguous
            except TypeError:
                contiguous = False
            if not contiguous:
                raise TypeError(f"expected string or bytes-like object, got '{type(string).__name__}'")
        if isinstance(self.pattern, str) and not isinstance(string, str):
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
        result = _NATIVE.run(self._handle, string, self.groups, pos, endpos, 0, require_nonempty)
        if result is None:
            return None
        spans, last = result
        return Match(self, string, spans, last, pos if original_pos is None else original_pos, endpos)

    def search(self, string, pos=0, endpos=None):
        self._validate_string(string)
        length = _subject_length(string)
        end = length if endpos is None else min(max(endpos, 0), length)
        return self._search(string, max(pos, 0), end)

    def match(self, string, pos=0, endpos=None):
        self._validate_string(string)
        length = _subject_length(string)
        end = length if endpos is None else min(max(endpos, 0), length)
        return self._at(string, max(pos, 0), end, max(pos, 0)) if pos <= end else None

    def fullmatch(self, string, pos=0, endpos=None):
        self._validate_string(string)
        length = _subject_length(string)
        end = length if endpos is None else min(max(endpos, 0), length)
        start = max(pos, 0)
        result = _NATIVE.run(self._handle, string, self.groups, start, end, 2, False)
        if result is None:
            return None
        spans, last = result
        return Match(self, string, spans, last, start, end)

    def finditer(self, string, pos=0, endpos=None):
        self._validate_string(string)
        length = _subject_length(string)
        end = length if endpos is None else min(max(endpos, 0), length)
        if isinstance(string, (str, bytes)):
            return self._collected(string, max(pos, 0), end)
        return self._finditer(string, pos, end, memoryview(string))

    def _finditer(self, string, pos, end, view):
        current = max(pos, 0)
        empty = False
        while current <= end:
            result = self._search(string, current, end, empty, max(pos, 0))
            if result is None:
                break
            yield result
            begin, finish = result._spans[0]
            if begin == finish:
                empty = True
                current = begin
            else:
                current = finish
                empty = False

    def _collected(self, string, pos, end):
        result = _NATIVE.collect(self._handle, string, self.groups, pos, end)
        if result is None:
            yield from self._finditer(string, pos, end, None)
            return
        for spans, last in result:
            yield Match(self, string, spans, last, pos, end)

    def findall(self, string, pos=0, endpos=None):
        self._validate_string(string)
        length = _subject_length(string)
        end = length if endpos is None else min(max(endpos, 0), length)
        native = _zig_bridge.findall(self._handle, string, self.groups, max(pos, 0), end)
        if native is not None:
            return native
        empty = b"" if not isinstance(string, str) else ""
        output = []
        for item in self._collected(string, max(pos, 0), end):
            if self.groups == 0:
                begin, finish = item._spans[0]
                output.append(_slice(string, begin, finish))
            elif self.groups == 1:
                span = item._spans[1]
                output.append(empty if span is None else _slice(string, span[0], span[1]))
            else:
                output.append(tuple(empty if span is None else _slice(string, span[0], span[1]) for span in item._spans[1:]))
        return output

    def split(self, string, maxsplit=0):
        self._validate_string(string)
        return _zig_bridge.split(self._handle, string, self.groups, maxsplit)

    def subn(self, repl, string, count=0):
        self._validate_string(string)
        length = _subject_length(string)
        is_callable = callable(repl)
        raw = None
        template = None
        if not is_callable:
            raw = bytes(repl) if isinstance(repl, (bytearray, memoryview)) else repl
            if isinstance(raw, (str, bytes)) and isinstance(string, str) != isinstance(raw, str):
                expected = "str instance" if isinstance(string, str) else "a bytes-like object"
                raise TypeError(f"sequence item 0: expected {expected}, {type(raw).__name__} found")
            escaped = b"\\" in raw if isinstance(raw, bytes) else "\\" in raw
            template = self._templates.get(raw)
            if template is None:
                _template(repl, Match(self, string, [(0, 0)] + [None] * self.groups, None, 0, length), True)
                template = _template_tokens(raw, self) if escaped else (raw,)
                if len(self._templates) >= 32:
                    self._templates.clear()
                self._templates[raw] = template
            if escaped:
                return _zig_bridge.subn(self._handle, string, self.groups, template, count)
            elif self._literal is not None and isinstance(string, str) == isinstance(raw, str):
                if count < 0:
                    return _slice(string, 0, length), 0
                source = str(string) if isinstance(string, str) else bytes(string)
                occurrences = source.count(self._literal)
                replacements = occurrences if count == 0 else min(occurrences, count)
                return source.replace(self._literal, raw, -1 if count == 0 else count), replacements
            return _zig_bridge.subn(self._handle, string, self.groups, template, count)
        parts = []
        previous = 0
        replacements = 0
        matches = self.finditer(string) if is_callable else self._collected(string, 0, length)
        for item in matches:
            if count and replacements >= count:
                break
            begin, finish = item._spans[0]
            prefix = _slice(string, previous, begin)
            if prefix:
                parts.append(prefix)
            if is_callable:
                value = repl(item)
            else:
                value = _expand_tokens(template, item, isinstance(raw, bytes)) if template is not None else repl
            parts.append(value)
            previous = finish
            replacements += 1
        tail = _slice(string, previous, length)
        if tail:
            parts.append(tail)
        return (b"" if not isinstance(string, str) else "").join(parts), replacements

    def sub(self, repl, string, count=0):
        return self.subn(repl, string, count)[0]

    def scanner(self, string, pos=0, endpos=None):
        self._validate_string(string)
        return _Scanner(self, string, pos, endpos)


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
    if isinstance(pattern, str) and flags & int(ASCII) and flags & int(UNICODE):
        raise ValueError("ASCII and UNICODE flags are incompatible")
    if isinstance(pattern, bytes) and flags & int(ASCII) and flags & int(LOCALE):
        raise ValueError("ASCII and LOCALE flags are incompatible")
    key = (type(pattern), pattern, flags)
    if key in _CACHE:
        return _CACHE[key]
    implicit_unicode = int(UNICODE) if isinstance(pattern, str) and not flags & int(ASCII) else 0
    if _may_accept_invalid_pattern(pattern):
        _preflight_pattern(pattern, flags | implicit_unicode)
    _warn_ambiguous(pattern)
    try:
        handle, groups, effective_flags, groupindex = _NATIVE.compile(pattern, flags | implicit_unicode)
    except PatternError:
        _preflight_pattern(pattern, flags | implicit_unicode)
        raise
    if isinstance(pattern, str) and ((flags & int(ASCII) and effective_flags & int(UNICODE)) or (flags & int(UNICODE) and effective_flags & int(ASCII))):
        _NATIVE.library.rebar_zig_free(handle)
        raise ValueError("ASCII and UNICODE flags are incompatible")
    if isinstance(pattern, bytes) and ((flags & int(ASCII) and effective_flags & int(LOCALE)) or (flags & int(LOCALE) and effective_flags & int(ASCII))):
        _NATIVE.library.rebar_zig_free(handle)
        raise ValueError("ASCII and LOCALE flags are incompatible")
    result = Pattern(pattern, effective_flags, handle, groups, groupindex)
    _CACHE[key] = result
    if flags & int(DEBUG):
        print(f"ZIG-BYTECODE groups={groups} flags={effective_flags}")
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


def escape(pattern):
    if isinstance(pattern, str):
        return pattern.translate(_ESCAPE_MAP)
    return str(pattern, "latin1").translate(_ESCAPE_MAP).encode("latin1")


__all__ = ["match", "fullmatch", "search", "sub", "subn", "split", "findall", "finditer", "compile", "purge", "escape", "error", "Pattern", "Match", "A", "I", "L", "M", "S", "X", "U", "ASCII", "IGNORECASE", "LOCALE", "MULTILINE", "DOTALL", "VERBOSE", "UNICODE", "NOFLAG", "RegexFlag", "PatternError"]
