"""From-scratch capture-aware Zig bytecode candidate with a dependency-free native bridge."""

import ctypes
import enum
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
_MAXREPEAT = (1 << 32) - 1
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
        lib.rebar_zig_program_memory.argtypes = [ctypes.c_void_p]
        lib.rebar_zig_program_memory.restype = ctypes.c_size_t
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
            named = _named_escapes(pattern) if "\\N" in pattern else ()
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
        compiled = _zig_bridge.compile(raw, native_flags, isinstance(pattern, bytes))
        if compiled is None:
            raise PatternError("unsupported or invalid Zig pattern", pattern, 0)
        return compiled

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


def _fixed_width(text):
    """Return the width of a simple fixed-width expression, or None when it varies."""
    at = 0
    length = len(text)

    def expression():
        nonlocal at
        widths = []
        total = 0
        while at < length and text[at] != ")":
            if text[at] == "|":
                widths.append(total)
                total = 0
                at += 1
                continue
            if text[at] == "(":
                if text.startswith("(?:", at) or text.startswith("(?>", at):
                    at += 3
                elif text.startswith("(?P<", at):
                    close = text.find(">", at + 4)
                    if close < 0:
                        return None
                    at = close + 1
                elif text.startswith("(?", at):
                    return None
                else:
                    at += 1
                width = expression()
                if width is None or at >= length or text[at] != ")":
                    return None
                at += 1
            elif text[at] == "[":
                at += 1
                if at < length and text[at] == "^":
                    at += 1
                first = True
                while at < length:
                    if text[at] == "]" and not first:
                        break
                    first = False
                    at += 2 if text[at] == "\\" and at + 1 < length else 1
                if at >= length:
                    return None
                at += 1
                width = 1
            elif text[at] == "\\":
                at += 2
                width = 1
            elif text[at] in "^$":
                at += 1
                width = 0
            else:
                at += 1
                width = 1
            if at < length and text[at] in "*+?":
                return None
            if at < length and text[at] == "{":
                opening = at
                at += 1
                begin = at
                while at < length and text[at].isdigit():
                    at += 1
                left = text[begin:at]
                right = left
                if at < length and text[at] == ",":
                    at += 1
                    begin = at
                    while at < length and text[at].isdigit():
                        at += 1
                    right = text[begin:at]
                if at >= length or text[at] != "}" or not left and not right:
                    at = opening
                else:
                    at += 1
                    if not left or not right or left != right:
                        return None
                    width *= int(left)
                    if at < length and text[at] in "?+":
                        at += 1
            total += width
        widths.append(total)
        return widths[0] if all(value == widths[0] for value in widths) else None

    width = expression()
    return width if at == length else None


def _pattern_recursion_weight(pattern, flags):
    """Measure real nested groups without counting escapes, sets, or comments."""
    text = pattern.decode("latin1") if isinstance(pattern, bytes) else pattern
    length = len(text)
    index = 0
    weight = 0
    maximum = 0
    verbose = bool(flags & int(VERBOSE))
    scopes = []

    while index < length:
        char = text[index]
        if verbose and char in " \t\n\r\v\f":
            index += 1
            continue
        if verbose and char == "#":
            newline = text.find("\n", index + 1)
            index = length if newline < 0 else newline + 1
            continue
        if char == "\\":
            index += min(2, length - index)
            continue
        if char == "[":
            index += 1
            if index < length and text[index] == "^":
                index += 1
            if index < length and text[index] == "]":
                index += 1
            while index < length and text[index] != "]":
                index += 2 if text[index] == "\\" and index + 1 < length else 1
            if index < length:
                index += 1
            continue
        if char == ")":
            if scopes:
                group_weight, verbose = scopes.pop()
                weight -= group_weight
            index += 1
            continue
        if char != "(":
            index += 1
            continue
        if text.startswith("(?#", index):
            close = text.find(")", index + 3)
            index = length if close < 0 else close + 1
            continue
        if text.startswith("(?P=", index):
            close = text.find(")", index + 4)
            index = length if close < 0 else close + 1
            continue

        scoped_verbose = verbose
        next_index = index + 1
        conditional = text.startswith("(?(", index)
        if conditional:
            close = text.find(")", index + 3)
            next_index = close + 1 if close >= 0 else index + 3
        elif text.startswith("(?P<", index):
            close = text.find(">", index + 4)
            next_index = close + 1 if close >= 0 else index + 4
        elif text.startswith(("(?<=", "(?<!"), index):
            next_index = index + 4
        elif text.startswith(("(?=", "(?!", "(?:", "(?>"), index):
            next_index = index + 3
        elif text.startswith("(?", index):
            cursor = index + 2
            while cursor < length and text[cursor] in "aiLmsux-":
                cursor += 1
            if cursor < length and text[cursor] in ":)":
                marks = text[index + 2:cursor]
                adding, separator, removing = marks.partition("-")
                scoped_verbose = (verbose or "x" in adding) and not (
                    separator and "x" in removing
                )
                if text[cursor] == ")":
                    verbose = scoped_verbose
                    index = cursor + 1
                    continue
                next_index = cursor + 1

        group_weight = 1 if conditional else 2
        scopes.append((group_weight, verbose))
        weight += group_weight
        if weight > maximum:
            maximum = weight
        verbose = scoped_verbose
        index = next_index

    return maximum


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
    recursion_weight = 0
    pending_lookbehind_width_error = False
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
                    left_head = previous[:2] if previous.startswith("\\") else previous
                    right_head = right[:2] if right.startswith("\\") else right
                    position = right_end - len(left_head) - 1 - len(right_head)
                    fail(f"bad character range {left_head}-{right_head}", position)
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
                    message = (
                        f"redefinition of group name {name!r} as group "
                        f"{group_number}; was group {groups[name]}"
                    )
                    try:
                        raise PatternError(message)
                    except PatternError:
                        raise PatternError(message, pattern, index + 4) from None
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
                _zig_bridge.recursion_guard(recursion_weight + 2, False)
                stack.append((opening, active_flags, can_repeat, repeated,
                              None, "lookbehind"))
                recursion_weight += 2
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
                _zig_bridge.recursion_guard(recursion_weight + 2, False)
                stack.append((opening, active_flags, can_repeat, repeated,
                              None, "group"))
                recursion_weight += 2
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
            group_weight = 1 if kind == "conditional" else 2
            _zig_bridge.recursion_guard(recursion_weight + group_weight, False)
            stack.append((opening, active_flags, can_repeat, repeated,
                          group_number if capture else None, kind))
            recursion_weight += group_weight
            if capture:
                open_groups.append(group_number)
            can_repeat = repeated = False
            root_prefix = False
            continue
        if char == ")":
            if not stack:
                fail("unbalanced parenthesis", index)
            opening, parent_flags, _, _, group_number, kind = stack.pop()
            recursion_weight -= 1 if kind == "conditional" else 2
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
                width = _fixed_width(body)
                if variable or width is None:
                    pending_lookbehind_width_error = True
                elif width > _MAXREPEAT:
                    fail("looks too much behind", keep_pattern=False)
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
                if minimum >= _MAXREPEAT or maximum is not None and maximum >= _MAXREPEAT:
                    raise OverflowError("the repetition number is too large")
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
        fail("missing ), unterminated subpattern", stack[-1][0])
    for number, position in conditionals:
        if number > group_count:
            fail(f"invalid group reference {number}", position)
    if pending_lookbehind_width_error:
        fail("look-behind requires fixed-width pattern", keep_pattern=False)


def _may_accept_invalid_pattern(pattern):
    """Quickly find the few invalid forms the native parser can otherwise accept."""
    text = pattern.decode("latin1") if isinstance(pattern, bytes) else pattern
    byte_mode = isinstance(pattern, bytes)
    length = len(text)
    if text.startswith("{") or "(?:{" in text:
        return True
    if not byte_mode:
        opening = text.find("(?P<")
        while opening >= 0:
            close = text.find(">", opening + 4)
            if close < 0:
                break
            name = text[opening + 4:close]
            if name and not name.isascii() and not name.isidentifier():
                return True
            opening = text.find("(?P<", close + 1)
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
    if isinstance(value, (str, bytes)):
        return len(value)
    return memoryview(value).nbytes


Match = _zig_bridge.Match


def _resolve_zig_generic_alias(origin_name, arguments):
    if type(origin_name) is not str or type(arguments) is not tuple:
        raise TypeError("a Zig generic alias requires an origin name and argument tuple")
    if origin_name == "Pattern":
        origin = Pattern
    elif origin_name == "Match":
        origin = Match
    else:
        raise TypeError("unowned Zig regular-expression generic alias origin")
    return _ZigGenericAlias(origin, arguments)


class _ZigGenericAlias(types.GenericAlias):
    __slots__ = ()

    def __reduce__(self):
        origin = self.__origin__
        if origin is Pattern:
            origin_name = "Pattern"
        elif origin is Match:
            origin_name = "Match"
        else:
            raise TypeError("unowned Zig regular-expression generic alias origin")
        return _resolve_zig_generic_alias, (origin_name, self.__args__)


_PATTERN_METHODS = ("search", "match", "fullmatch", "findall", "finditer", "split", "sub", "subn", "scanner")


class Pattern:
    __module__ = "re"
    __slots__ = ("pattern", "flags", "groups", "_groupindex", "_handle",
                 "_literal", "_templates", "__weakref__")

    @property
    def groupindex(self):
        names = self._groupindex
        return types.MappingProxyType(names) if names else {}

    def __init__(self, value, flags, handle, groups, groupindex):
        names = dict(groupindex)
        metacharacters = b".^$*+?{}[]\\|()" if isinstance(value, bytes) else ".^$*+?{}[]\\|()"
        literal = value if value and not flags & int(IGNORECASE | VERBOSE) and not any(char in metacharacters for char in value) else None
        _zig_bridge.initialize_pattern(self, value, flags, groups, types.MappingProxyType(names), names, handle, literal, {})

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
            _zig_bridge.free(handle)
            self._handle = None

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self

    def __reduce__(self):
        return compile, (self.pattern, self.flags)

    @classmethod
    def __class_getitem__(cls, item):
        return _ZigGenericAlias(cls, item)

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
        if not isinstance(string, (str, bytes, bytearray)):
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

    def _at(self, string, start, endpos, original_pos, require_nonempty=False, validate=True):
        if validate:
            self._validate_string(string)
        if self._literal is not None and isinstance(string, (str, bytes)):
            source = str(string) if isinstance(string, str) else bytes(string)
            if source.startswith(self._literal, start, endpos):
                return _zig_bridge.span_object(self, string, self.groups, self._groupindex, start, start + len(self._literal), original_pos, endpos)
            return None
        return _zig_bridge.match_object(self, self._handle, self._groupindex, string, start, endpos, 1, require_nonempty, original_pos)

    def _search(self, string, pos, endpos, require_nonempty=False, original_pos=None, validate=True):
        if validate:
            self._validate_string(string)
        if pos > endpos:
            return None
        if self._literal is not None and isinstance(string, (str, bytes)):
            source = str(string) if isinstance(string, str) else bytes(string)
            begin = source.find(self._literal, pos, endpos)
            if begin < 0:
                return None
            return _zig_bridge.span_object(self, string, self.groups, self._groupindex, begin, begin + len(self._literal), pos if original_pos is None else original_pos, endpos)
        return _zig_bridge.match_object(self, self._handle, self._groupindex, string, pos, endpos, 0, require_nonempty, pos if original_pos is None else original_pos)

    def _cache_template(self, repl, string):
        source = repl
        if type(repl) is str or type(repl) is bytes:
            raw = repl
        elif isinstance(repl, str):
            try:
                hash(repl)
            except TypeError:
                source = str(repl)
            raw = str(repl)
        elif isinstance(repl, bytes):
            try:
                hash(repl)
            except TypeError:
                source = bytes(repl)
            raw = bytes(repl)
        else:
            try:
                hash(repl)
            except TypeError:
                pass
            raw = str(repl, "latin1").encode("latin1")
            source = raw
        template = self._templates.get(raw)
        if template is None:
            dummy = _zig_bridge.span_object(
                self, string, self.groups, self._groupindex, 0, 0, 0, 0
            )
            _template(source, dummy, True)
            template = (
                _template_tokens(source, self)
                if (b"\\" in raw if isinstance(raw, bytes) else "\\" in raw)
                else (raw,)
            )
            if len(self._templates) >= 32:
                self._templates.clear()
            self._templates[raw] = template
        return template

    def _expand(self, template, match):
        raw = bytes(template) if isinstance(template, (bytearray, memoryview)) else template
        tokens = self._templates.get(raw)
        if tokens is None:
            _template(template, match, True)
            tokens = _template_tokens(raw, self)
            if len(self._templates) >= 32:
                self._templates.clear()
            self._templates[raw] = tokens
        return _expand_tokens(tokens, match, isinstance(raw, bytes))


_zig_bridge.install_pattern_methods(Pattern)


def _scanner_capture_name(branch, number):
    return f"_rebar_scanner_inner_{branch}_{number}"


def _scanner_phrase(phrase, branch, flags, native_outer_group):
    if isinstance(phrase, str):
        if flags & int(LOCALE):
            raise ValueError("cannot use LOCALE flag with a str pattern")
        if flags & int(ASCII) and flags & int(UNICODE):
            raise ValueError("ASCII and UNICODE flags are incompatible")
        text = phrase
    elif isinstance(phrase, bytes):
        if flags & int(UNICODE):
            raise ValueError("cannot use UNICODE flag with a bytes pattern")
        if flags & int(ASCII) and flags & int(LOCALE):
            raise ValueError("ASCII and LOCALE flags are incompatible")
        text = phrase.decode("latin1")
    else:
        raise TypeError("first argument must be string or compiled pattern")

    _preflight_pattern(phrase, flags)
    markers = (b"[[", b"&&", b"||", b"~~", b"--") if isinstance(phrase, bytes) else ("[[", "&&", "||", "~~", "--")
    if any(marker in phrase for marker in markers):
        _warn_ambiguous(phrase)

    pieces = []
    names = {}
    group_count = 0
    verbose = bool(flags & int(VERBOSE))
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        if char == "[":
            end = index + 1
            if end < length and text[end] == "^":
                end += 1
            if end < length and text[end] == "]":
                end += 1
            while end < length:
                if text[end] == "\\":
                    end += 2
                elif text[end] == "]":
                    end += 1
                    break
                else:
                    end += 1
            pieces.append(text[index:end])
            index = end
            continue

        if char == "\\":
            if index + 1 >= length:
                pieces.append(char)
                index += 1
                continue
            code = text[index + 1]
            if code in "123456789":
                octal = (
                    code in "1234567"
                    and index + 3 < length
                    and text[index + 2] in "01234567"
                    and text[index + 3] in "01234567"
                )
                if octal:
                    pieces.append(text[index:index + 4])
                    index += 4
                else:
                    end = index + 2
                    if end < length and text[end] in "0123456789":
                        end += 1
                    number = int(text[index + 1:end])
                    pieces.append(
                        f"(?P={_scanner_capture_name(branch, number)})"
                    )
                    index = end
            else:
                pieces.append(text[index:index + 2])
                index += 2
            continue

        if text.startswith("(?#", index):
            end = text.index(")", index + 3) + 1
            pieces.append(text[index:end])
            index = end
            continue

        if text.startswith("(?P<", index):
            end = text.index(">", index + 4)
            original_name = text[index + 4:end]
            group_count += 1
            names[original_name] = group_count
            pieces.append(
                f"(?P<{_scanner_capture_name(branch, group_count)}>"
            )
            index = end + 1
            continue

        if text.startswith("(?P=", index):
            end = text.index(")", index + 4)
            original_name = text[index + 4:end]
            pieces.append(
                f"(?P={_scanner_capture_name(branch, names[original_name])})"
            )
            index = end + 1
            continue

        if text.startswith("(?(", index):
            end = text.index(")", index + 3)
            reference = text[index + 3:end]
            if reference.isascii() and reference.isdigit():
                rewritten_reference = str(native_outer_group + int(reference))
            else:
                rewritten_reference = _scanner_capture_name(
                    branch, names[reference]
                )
            pieces.append(f"(?({rewritten_reference})")
            index = end + 1
            continue

        if text.startswith("(?", index):
            cursor = index + 2
            while cursor < length and text[cursor] in "aiLmsux-":
                cursor += 1
            if cursor > index + 2 and cursor < length and text[cursor] == ")":
                enabled, separator, disabled = text[index + 2:cursor].partition("-")
                if "x" in enabled:
                    verbose = True
                if separator and "x" in disabled:
                    verbose = False
                index = cursor + 1
                continue

        if char == "(" and not text.startswith("(?", index):
            group_count += 1
            pieces.append(
                f"(?P<{_scanner_capture_name(branch, group_count)}>"
            )
            index += 1
            continue

        pieces.append(char)
        index += 1

    rewritten = "".join(pieces)
    if verbose != bool(flags & int(VERBOSE)):
        rewritten = ("(?x:" if verbose else "(?-x:") + rewritten + ")"
    return rewritten, group_count


class Scanner:
    def __init__(self, lexicon, flags=0):
        flags = int(flags)
        self.lexicon = lexicon
        branches = []
        byte_mode = None
        native_outer_group = 1
        for phrase, _action in lexicon:
            if byte_mode is None:
                byte_mode = isinstance(phrase, bytes)
            body, local_groups = _scanner_phrase(
                phrase, len(branches), flags, native_outer_group
            )
            outer = f"_rebar_scanner_outer_{len(branches)}"
            branches.append((f"(?P<{outer}>{body})", local_groups))
            native_outer_group += 1 + local_groups

        if not branches:
            raise RuntimeError("invalid SRE code")
        group_count = len(branches)
        if any(local_groups > group_count for _body, local_groups in branches):
            raise RuntimeError("invalid SRE code")

        source = "|".join(body for body, _local_groups in branches)
        if byte_mode:
            source = source.encode("latin1")
        handle, _native_groups, _effective_flags, _native_names = _NATIVE.compile(
            source, flags
        )
        try:
            combined = Pattern.__new__(Pattern)
        except BaseException:
            _zig_bridge.free(handle)
            raise
        try:
            Pattern.__init__(combined, None, flags, handle, group_count, {})
        except BaseException:
            if getattr(combined, "_handle", None):
                object.__setattr__(combined, "_handle", None)
            _zig_bridge.free(handle)
            raise
        self.scanner = combined

    def scan(self, string):
        result = []
        append = result.append
        match = self.scanner.scanner(string).match
        position = 0
        while True:
            matched = match()
            if not matched:
                break
            end = matched.end()
            if end == position:
                break
            action = self.lexicon[matched.lastindex - 1][1]
            if callable(action):
                self.match = matched
                action = action(self, matched.group())
            if action is not None:
                append(action)
            position = end
        return result, string[position:]


_CACHE = {}
_CACHE2 = {}
_MAX_CACHE = 512
_MAX_CACHE2 = 256


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
        _CACHE[key] = cached
        if len(_CACHE2) >= _MAX_CACHE2:
            try:
                del _CACHE2[next(iter(_CACHE2))]
            except (StopIteration, RuntimeError, KeyError):
                pass
        _CACHE2[key] = cached
        return cached
    if isinstance(pattern, Pattern):
        if flags:
            raise ValueError("cannot process flags argument with a compiled pattern")
        return pattern
    if not isinstance(pattern, (str, bytes)):
        raise TypeError("first argument must be string or compiled pattern")
    flags = int(flags)
    if isinstance(pattern, str) and flags & int(LOCALE):
        raise ValueError("cannot use LOCALE flag with a str pattern")
    if isinstance(pattern, bytes) and flags & int(UNICODE):
        raise ValueError("cannot use UNICODE flag with a bytes pattern")
    if isinstance(pattern, str) and flags & int(ASCII) and flags & int(UNICODE):
        raise ValueError("ASCII and UNICODE flags are incompatible")
    if isinstance(pattern, bytes) and flags & int(ASCII) and flags & int(LOCALE):
        raise ValueError("ASCII and LOCALE flags are incompatible")
    implicit_unicode = int(UNICODE) if isinstance(pattern, str) and not flags & int(ASCII) else 0
    opening = b"(" if isinstance(pattern, bytes) else "("
    if opening in pattern and _zig_bridge.recursion_guard(
        _pattern_recursion_weight(pattern, flags | implicit_unicode), True
    ):
        _preflight_pattern(pattern, flags | implicit_unicode)
    if _may_accept_invalid_pattern(pattern):
        _preflight_pattern(pattern, flags | implicit_unicode)
    markers = (b"[[", b"&&", b"||", b"~~", b"--") if isinstance(pattern, bytes) else ("[[", "&&", "||", "~~", "--")
    if any(marker in pattern for marker in markers):
        _warn_ambiguous(pattern)
    native_error = None
    try:
        handle, groups, effective_flags, groupindex = _NATIVE.compile(pattern, flags | implicit_unicode)
    except PatternError as error:
        native_error = error
    if native_error is not None:
        _preflight_pattern(pattern, flags | implicit_unicode)
        raise native_error
    if isinstance(pattern, str) and ((flags & int(ASCII) and effective_flags & int(UNICODE)) or (flags & int(UNICODE) and effective_flags & int(ASCII))):
        _zig_bridge.free(handle)
        raise ValueError("ASCII and UNICODE flags are incompatible")
    if isinstance(pattern, bytes) and ((flags & int(ASCII) and effective_flags & int(LOCALE)) or (flags & int(LOCALE) and effective_flags & int(ASCII))):
        _zig_bridge.free(handle)
        raise ValueError("ASCII and LOCALE flags are incompatible")
    result = Pattern(pattern, effective_flags, handle, groups, groupindex)
    if flags & int(DEBUG):
        print(f"ZIG-BYTECODE groups={groups} flags={effective_flags}")
        return result
    if len(_CACHE) >= _MAX_CACHE:
        try:
            del _CACHE[next(iter(_CACHE))]
        except (StopIteration, RuntimeError, KeyError):
            pass
    _CACHE[key] = result
    if len(_CACHE2) >= _MAX_CACHE2:
        try:
            del _CACHE2[next(iter(_CACHE2))]
        except (StopIteration, RuntimeError, KeyError):
            pass
    _CACHE2[key] = result
    return result


_compile = compile


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


def escape(pattern):
    if isinstance(pattern, str):
        return pattern.translate(_ESCAPE_MAP)
    return str(pattern, "latin1").translate(_ESCAPE_MAP).encode("latin1")


split.__text_signature__ = "(pattern, string, maxsplit=0, flags=0)"
sub.__text_signature__ = "(pattern, repl, string, count=0, flags=0)"
subn.__text_signature__ = "(pattern, repl, string, count=0, flags=0)"


__all__ = ["match", "fullmatch", "search", "sub", "subn", "split", "findall", "finditer", "compile", "purge", "escape", "error", "Pattern", "Match", "A", "I", "L", "M", "S", "X", "U", "ASCII", "IGNORECASE", "LOCALE", "MULTILINE", "DOTALL", "VERBOSE", "UNICODE", "NOFLAG", "RegexFlag", "PatternError"]
