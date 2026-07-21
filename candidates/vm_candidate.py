"""From-scratch bytecode compiler and native C VM candidate for the frozen re P0 contract."""

import enum
import os
import types
import unicodedata
import warnings

from candidates import _vm_native


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
_MISSING = object()
_WARNING_PREFIX = (os.path.dirname(__file__),)


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


class _BytecodeParser:
    """An iterative frame-stack parser independent of the recursive AST candidate."""

    def __init__(self, original, flags):
        self.original = original
        self.source = original.decode("latin1") if isinstance(original, bytes) else original
        self.byte_mode = isinstance(original, bytes)
        self.flags = int(flags) | (_BYTE if self.byte_mode else 0)
        self.at = 0
        self.groups = 0
        self.groupindex = {}
        self.groupwidth = {}

    def error(self, message, position=None, include_pattern=True):
        raise PatternError(message, self.original if include_pattern else None, position)

    def current(self):
        return self.source[self.at] if self.at < len(self.source) else None

    def advance(self):
        value = self.current()
        if value is not None:
            self.at += 1
        return value

    def insignificant(self, flags):
        if not flags & int(VERBOSE):
            return
        while self.current() is not None:
            value = self.current()
            if value in " \t\n\r\v\f":
                self.at += 1
            elif value == "#":
                newline = self.source.find("\n", self.at)
                self.at = len(self.source) if newline < 0 else newline + 1
            else:
                break

    def frame(self, tag, flags, start, value=None):
        return {"tag": tag, "flags": flags, "start": start, "value": value, "parts": [[]]}

    def sequence_node(self, parts):
        return ("seq", parts)

    def frame_node(self, frame):
        branches = [self.sequence_node(items) for items in frame["parts"]]
        node = branches[0] if len(branches) == 1 else ("alt", branches)
        tag, value = frame["tag"], frame["value"]
        if tag == "root" or tag == "plain":
            return node
        if tag == "capture":
            self.groupwidth[value] = _width(node, self.groupwidth)
            return ("group", value, node)
        if tag == "atomic":
            return ("atomic", node)
        if tag in {"ahead+", "ahead-", "behind+", "behind-"}:
            behind = tag.startswith("behind")
            width = None
            if behind:
                minimum, maximum = _width(node, self.groupwidth)
                if minimum != maximum:
                    self.error("look-behind requires fixed-width pattern", include_pattern=False)
                width = minimum
            return ("look", "behind" if behind else "ahead", tag.endswith("+"), node, width)
        if tag == "conditional":
            yes = branches[0]
            no = branches[1] if len(branches) > 1 else ("seq", [])
            if len(branches) > 2:
                self.error("conditional backref with more than two branches", frame["start"])
            return ("conditional", value, yes, no)
        raise RuntimeError(f"unknown parser frame {tag}")

    def name(self, terminator, position):
        close = self.source.find(terminator, self.at)
        if close < 0:
            self.error(f"missing {terminator}, unterminated name", position)
        value = self.source[self.at:close]
        self.at = close + 1
        if not value:
            self.error("missing group name", position)
        if not value.isidentifier() or (self.byte_mode and not value.isascii()):
            if self.byte_mode:
                shown = "".join(char if char.isascii() else f"\\x{ord(char):02x}" for char in value)
                self.error(f"bad character in group name '{shown}'", position)
            self.error(f"bad character in group name {value!r}", position)
        return value

    def escaped(self, flags, in_set, slash):
        char = self.advance()
        if char is None:
            self.error("bad escape (end of pattern)", slash)
        controls = {"a": "\a", "f": "\f", "n": "\n", "r": "\r", "t": "\t", "v": "\v"}
        if char in controls:
            return ("lit", controls[char], flags)
        if char == "b":
            return ("lit", "\b", flags) if in_set else ("boundary", True, flags)
        if char == "B" and not in_set:
            return ("boundary", False, flags)
        if char in "dDsSwW":
            return ("category", char, flags)
        if char in "AZz" and not in_set:
            return ("anchor", char, flags)
        if char == "x":
            digits = self.source[self.at:self.at + 2]
            if len(digits) != 2 or any(item not in "0123456789abcdefABCDEF" for item in digits):
                self.error("incomplete escape \\x", slash)
            self.at += 2
            return ("lit", chr(int(digits, 16)), flags)
        if char in {"u", "U"} and not self.byte_mode:
            count = 4 if char == "u" else 8
            digits = self.source[self.at:self.at + count]
            if len(digits) != count or any(item not in "0123456789abcdefABCDEF" for item in digits):
                self.error(f"incomplete escape \\{char}", slash)
            self.at += count
            return ("lit", chr(int(digits, 16)), flags)
        if char == "N" and not self.byte_mode and self.current() == "{":
            self.at += 1
            close = self.source.find("}", self.at)
            if close < 0:
                self.error("missing }, unterminated name", slash + 2)
            label = self.source[self.at:close]
            self.at = close + 1
            try:
                return ("lit", unicodedata.lookup(label), flags)
            except KeyError:
                self.error(f"undefined character name {label!r}", slash)
        if char.isdigit():
            digits = char
            if char == "0" or in_set:
                while len(digits) < 3 and self.current() is not None and self.current() in "01234567":
                    digits += self.advance()
                return ("lit", chr(int(digits, 8)), flags)
            if self.current() is not None and self.current().isdigit():
                digits += self.advance()
            number = int(digits)
            if number > self.groups:
                self.error(f"invalid group reference {number}", slash + 1)
            return ("backref", number, flags)
        if char.isalpha():
            self.error(f"bad escape \\{char}", slash)
        return ("lit", char, flags)

    def set_node(self, flags, opening):
        negative = self.current() == "^"
        if negative:
            self.at += 1
        members = []
        initial = True
        while self.current() is not None:
            if self.current() == "]" and not initial:
                self.at += 1
                intersection = self.source.find("&&", opening, self.at)
                if intersection >= 0:
                    warnings.warn(f"Possible set intersection at position {intersection}", FutureWarning, skip_file_prefixes=_WARNING_PREFIX)
                if self.source[opening + 1:opening + 2] == "[":
                    warnings.warn(f"Possible nested set at position {opening + 1}", FutureWarning, skip_file_prefixes=_WARNING_PREFIX)
                for marker, label in (("||", "union"), ("~~", "symmetric difference"), ("--", "difference")):
                    location = self.source.find(marker, opening, self.at)
                    if location >= 0:
                        warnings.warn(f"Possible set {label} at position {location}", FutureWarning, skip_file_prefixes=_WARNING_PREFIX)
                return ("class", members, negative, flags)
            initial = False
            if self.current() == "\\":
                slash = self.at
                self.at += 1
                left = self.escaped(flags, True, slash)
            else:
                left = ("lit", self.advance(), flags)
            if self.current() == "-" and self.at + 1 < len(self.source) and self.source[self.at + 1] != "]":
                dash = self.at
                self.at += 1
                if self.current() == "\\":
                    slash = self.at
                    self.at += 1
                    right = self.escaped(flags, True, slash)
                else:
                    right = ("lit", self.advance(), flags)
                if left[0] != "lit" or right[0] != "lit":
                    self.error("bad character range", dash)
                if ord(left[1]) > ord(right[1]):
                    self.error(f"bad character range {left[1]}-{right[1]}", dash - 1)
                members.append(("range", left[1], right[1]))
            else:
                members.append(left)
        self.error("unterminated character set", opening)

    def repeated(self, node, flags):
        char = self.current()
        if char not in {"*", "+", "?", "{"}:
            return node
        if node[0] in {"anchor", "boundary", "look"}:
            self.error("nothing to repeat", self.at)
        opening = self.at
        self.at += 1
        if char == "*":
            minimum, maximum = 0, None
        elif char == "+":
            minimum, maximum = 1, None
        elif char == "?":
            minimum, maximum = 0, 1
        else:
            close = self.source.find("}", self.at)
            if close < 0:
                self.at = opening
                return node
            value = self.source[self.at:close]
            if not value or value.count(",") > 1 or any(item not in "0123456789," for item in value):
                self.at = opening
                return node
            self.at = close + 1
            if "," not in value:
                minimum = maximum = int(value)
            else:
                left, right = value.split(",", 1)
                minimum = int(left) if left else 0
                maximum = int(right) if right else None
            if maximum is not None and minimum > maximum:
                self.error("min repeat greater than max repeat", opening + 1)
        mode = "greedy"
        if self.current() in {"?", "+"}:
            mode = "lazy" if self.advance() == "?" else "possessive"
        if self.current() in {"*", "+", "?"}:
            self.error("multiple repeat", self.at)
        return ("repeat", node, minimum, maximum, mode, flags)

    def parse(self):
        stack = [self.frame("root", self.flags, 0)]
        while stack:
            active = stack[-1]
            flags = active["flags"]
            self.insignificant(flags)
            char = self.current()
            if char is None:
                if len(stack) != 1:
                    self.error("missing ), unterminated subpattern", active["start"])
                self.flags = active["flags"]
                return self.frame_node(active)
            if char == "|":
                self.at += 1
                active["parts"].append([])
                continue
            if char == ")":
                if len(stack) == 1:
                    self.error("unbalanced parenthesis", self.at)
                self.at += 1
                node = self.frame_node(stack.pop())
                parent = stack[-1]
                self.insignificant(parent["flags"])
                parent["parts"][-1].append(self.repeated(node, parent["flags"]))
                continue
            opening = self.at
            self.at += 1
            if char == "(":
                if self.current() != "?":
                    self.groups += 1
                    stack.append(self.frame("capture", flags, opening, self.groups))
                    continue
                self.at += 1
                extension = self.advance()
                if extension == ":":
                    stack.append(self.frame("plain", flags, opening))
                    continue
                if extension in {"=", "!"}:
                    stack.append(self.frame("ahead+" if extension == "=" else "ahead-", flags, opening))
                    continue
                if extension == "<" and self.current() in {"=", "!"}:
                    sign = self.advance()
                    stack.append(self.frame("behind+" if sign == "=" else "behind-", flags, opening))
                    continue
                if extension == ">":
                    stack.append(self.frame("atomic", flags, opening))
                    continue
                if extension == "#":
                    close = self.source.find(")", self.at)
                    if close < 0:
                        self.error("missing ), unterminated comment", opening)
                    self.at = close + 1
                    continue
                if extension == "P":
                    form = self.advance()
                    if form == "<":
                        name_start = self.at
                        label = self.name(">", name_start)
                        self.groups += 1
                        number = self.groups
                        if label in self.groupindex:
                            self.error(f"redefinition of group name {label!r} as group {number}; was group {self.groupindex[label]}", name_start)
                        self.groupindex[label] = number
                        stack.append(self.frame("capture", flags, opening, number))
                        continue
                    if form == "=":
                        name_start = self.at
                        label = self.name(")", name_start)
                        if label not in self.groupindex:
                            self.error(f"unknown group name {label!r}", name_start)
                        node = ("backref", self.groupindex[label], flags)
                        self.insignificant(flags)
                        active["parts"][-1].append(self.repeated(node, flags))
                        continue
                    self.error("unknown extension ?P", opening + 1)
                if extension == "(":
                    reference_start = self.at
                    close = self.source.find(")", self.at)
                    if close < 0:
                        self.error("missing ), unterminated name", reference_start)
                    reference = self.source[self.at:close]
                    self.at = close + 1
                    if reference.isdecimal():
                        number = int(reference)
                        if number < 1 or number > self.groups:
                            self.error(f"invalid group reference {number}", reference_start)
                    else:
                        if reference not in self.groupindex:
                            self.error(f"unknown group name {reference!r}", reference_start)
                        number = self.groupindex[reference]
                    stack.append(self.frame("conditional", flags, opening, number))
                    continue
                if extension is not None and extension in "aiLmsux-":
                    self.at -= 1
                    turn_on = turn_off = 0
                    removing = False
                    table = {"a": int(ASCII), "i": int(IGNORECASE), "L": int(LOCALE), "m": int(MULTILINE), "s": int(DOTALL), "u": int(UNICODE), "x": int(VERBOSE)}
                    while self.current() is not None and self.current() not in {":", ")"}:
                        item = self.advance()
                        if item == "-":
                            removing = True
                        elif item in table:
                            if removing:
                                if item in "aLu":
                                    self.error("bad inline flags: cannot turn off flags 'a', 'u' and 'L'", self.at)
                                turn_off |= table[item]
                            else:
                                if item == "L" and not self.byte_mode:
                                    self.error("bad inline flags: cannot use 'L' flag with a str pattern", self.at)
                                if item == "u" and self.byte_mode:
                                    self.error("bad inline flags: cannot use 'u' flag with a bytes pattern", self.at)
                                if item in "aLu" and turn_on & int(ASCII | LOCALE | UNICODE):
                                    self.error("bad inline flags: flags 'a', 'u' and 'L' are incompatible", self.at)
                                turn_on |= table[item]
                        else:
                            if removing and not turn_off and item in "+*?{":
                                self.error("missing flag", self.at - 1)
                            if removing and item in "+*?{":
                                self.error("missing :", self.at - 1)
                            if not removing and item in "+*?{":
                                self.error("missing -, : or )", self.at - 1)
                            self.error("unknown flag", self.at - 1)
                    if turn_on & turn_off:
                        self.error("bad inline flags: flag turned on and off", self.at)
                    changed = (flags | turn_on) & ~turn_off
                    if turn_on & int(ASCII | LOCALE):
                        changed &= ~int(UNICODE)
                    elif turn_on & int(UNICODE):
                        changed &= ~int(ASCII | LOCALE)
                    terminator = self.advance()
                    if removing and not turn_off:
                        self.error("missing flag", self.at)
                    if removing and terminator in {None, ")"}:
                        self.error("missing :", self.at - (terminator == ")"))
                    if terminator is None:
                        self.error("missing -, : or )", self.at)
                    if terminator == ")":
                        if len(stack) != 1 or len(active["parts"]) != 1 or active["parts"][0]:
                            self.error("global flags not at the start of the expression", opening)
                        active["flags"] = changed
                        self.flags = changed
                        continue
                    stack.append(self.frame("plain", changed, opening))
                    continue
                self.error(f"unknown extension ?{extension}", opening + 1)
            if char == "[":
                node = self.set_node(flags, opening)
            elif char == "\\":
                node = self.escaped(flags, False, opening)
            elif char == ".":
                node = ("dot", flags)
            elif char in "^$":
                node = ("anchor", char, flags)
            elif char in "*+?":
                self.error("nothing to repeat", opening)
            else:
                node = ("lit", char, flags)
            self.insignificant(flags)
            active["parts"][-1].append(self.repeated(node, flags))


def _width(node, groupwidth=None):
    kind = node[0]
    if kind in {"lit", "dot", "class", "category"}:
        return 1, 1
    if kind in {"anchor", "boundary", "look", "setflags"}:
        return 0, 0
    if kind == "backref":
        return groupwidth.get(node[1], (0, 10 ** 9)) if groupwidth is not None else (0, 10 ** 9)
    if kind == "group" or kind == "atomic":
        return _width(node[-1], groupwidth)
    if kind == "conditional":
        a, b = _width(node[2], groupwidth), _width(node[3], groupwidth)
        return min(a[0], b[0]), max(a[1], b[1])
    if kind == "seq":
        values = [_width(item, groupwidth) for item in node[1]]
        return sum(item[0] for item in values), sum(item[1] for item in values)
    if kind == "alt":
        values = [_width(item, groupwidth) for item in node[1]]
        return min(item[0] for item in values), max(item[1] for item in values)
    if kind == "repeat":
        child = _width(node[1], groupwidth)
        return child[0] * node[2], 10 ** 9 if node[3] is None else child[1] * node[3]
    raise RuntimeError(f"unknown width node {kind}")


def _fold(char, ascii_only=False):
    if ascii_only and not char.isascii():
        return char
    if not ascii_only and char in "İıſK":
        return {"İ": "i", "ı": "i", "ſ": "s", "K": "k"}[char]
    return char.casefold()


def _range_case_match(left, right, char, ascii_only):
    if left <= char <= right:
        return True
    if ascii_only:
        variants = {char, char.lower(), char.upper()} if char.isascii() else {char}
    else:
        variants = {char}
        variants.update(value for value in (char.lower(), char.upper(), char.casefold()) if len(value) == 1)
        closures = ("Iiİı", "Ssſ", "KkK", "Ввᲀ", "ﬅﬆ", "ßẞ")
        for closure in closures:
            if char in closure:
                variants.update(closure)
    return any(left <= value <= right for value in variants)


def _equal(left, right, flags):
    if flags & int(IGNORECASE):
        return _fold(left, bool(flags & int(ASCII | LOCALE | _BYTE))) == _fold(right, bool(flags & int(ASCII | LOCALE | _BYTE)))
    return left == right


def _category(char, code, flags):
    ascii_only = bool(flags & int(ASCII | LOCALE | _BYTE))
    if code.lower() == "d":
        value = "0" <= char <= "9" if ascii_only else char.isdecimal()
    elif code.lower() == "s":
        value = char in " \t\n\r\v\f" if ascii_only else char.isspace()
    else:
        value = (char.isascii() and (char.isalnum() or char == "_")) if ascii_only else (char.isalnum() or char == "_")
    return not value if code.isupper() else value


def _class_match(node, char):
    _, items, negate, flags = node
    found = False
    for item in items:
        if item[0] == "range":
            left, right = item[1], item[2]
            found = _range_case_match(left, right, char, bool(flags & int(ASCII | LOCALE | _BYTE))) if flags & int(IGNORECASE) else left <= char <= right
        elif item[0] == "lit" and _equal(item[1], char, flags):
            found = True
        elif item[0] == "category" and _category(char, item[1], flags):
            found = True
        if found:
            break
    return not found if negate else found


class _BytecodeCompiler:
    CHAR, DOT, CAT, CLASS, ANCHOR, BOUNDARY, BACKREF, SAVE_START, SAVE_END, SPLIT, JUMP, LOOK, ATOMIC_START, ATOMIC_END, COND, MATCH, REPEAT1 = range(1, 18)

    def __init__(self):
        self.programs = [[]]
        self.classes = []
        self.current = self.programs[0]

    def instruction(self, op, a=0, b=0, c=0):
        self.current.append([op, a, b, c])
        return len(self.current) - 1

    def patch(self, index, *, a=None, b=None, c=None):
        row = self.current[index]
        if a is not None:
            row[1] = a
        if b is not None:
            row[2] = b
        if c is not None:
            row[3] = c

    def child_program(self, node):
        saved = self.current
        index = len(self.programs)
        self.current = []
        self.programs.append(self.current)
        self.emit(node)
        self.instruction(self.MATCH)
        self.current = saved
        return index

    def emit(self, node):
        kind = node[0]
        if kind == "lit":
            self.instruction(self.CHAR, ord(node[1]), node[2])
        elif kind == "dot":
            self.instruction(self.DOT, node[1])
        elif kind == "category":
            self.instruction(self.CAT, ord(node[1]), node[2])
        elif kind == "class":
            rows = []
            for item in node[1]:
                if item[0] == "lit":
                    rows.append((1, ord(item[1]), 0))
                elif item[0] == "range":
                    rows.append((2, ord(item[1]), ord(item[2])))
                else:
                    rows.append((3, ord(item[1]), 0))
            index = len(self.classes)
            self.classes.append(rows)
            self.instruction(self.CLASS, index, node[3], int(node[2]))
        elif kind == "anchor":
            self.instruction(self.ANCHOR, ord(node[1]), node[2])
        elif kind == "boundary":
            self.instruction(self.BOUNDARY, int(node[1]), node[2])
        elif kind == "backref":
            self.instruction(self.BACKREF, node[1], node[2])
        elif kind == "seq":
            for child in node[1]:
                self.emit(child)
        elif kind == "alt":
            endings = []
            for branch in node[1][:-1]:
                split = self.instruction(self.SPLIT)
                branch_start = len(self.current)
                self.emit(branch)
                endings.append(self.instruction(self.JUMP))
                next_branch = len(self.current)
                self.patch(split, a=branch_start, b=next_branch, c=-1)
            self.emit(node[1][-1])
            end = len(self.current)
            for jump in endings:
                self.patch(jump, a=end)
        elif kind == "group":
            self.instruction(self.SAVE_START, node[1])
            self.emit(node[2])
            self.instruction(self.SAVE_END, node[1])
        elif kind == "repeat":
            child, minimum, maximum, mode = node[1:5]
            if child[0] in {"lit", "dot", "category", "class"} and (maximum is None or maximum > minimum):
                self.instruction(self.REPEAT1, minimum, -1 if maximum is None else maximum, {"greedy": 0, "lazy": 1, "possessive": 2}[mode])
                self.emit(child)
                return
            atomic = mode == "possessive"
            if atomic:
                self.instruction(self.ATOMIC_START)
            for _ in range(minimum):
                self.emit(child)
            if maximum is None:
                split = self.instruction(self.SPLIT)
                child_start = len(self.current)
                self.emit(child)
                self.instruction(self.JUMP, split)
                end = len(self.current)
                if mode == "lazy":
                    self.patch(split, a=end, b=child_start, c=end)
                else:
                    self.patch(split, a=child_start, b=end, c=end)
            else:
                for _ in range(maximum - minimum):
                    split = self.instruction(self.SPLIT)
                    child_start = len(self.current)
                    self.emit(child)
                    end = len(self.current)
                    if mode == "lazy":
                        self.patch(split, a=end, b=child_start, c=-1)
                    else:
                        self.patch(split, a=child_start, b=end, c=-1)
            if atomic:
                self.instruction(self.ATOMIC_END)
        elif kind == "look":
            subprogram = self.child_program(node[3])
            mode = int(node[2]) | (2 if node[1] == "behind" else 0)
            self.instruction(self.LOOK, subprogram, mode, node[4] or 0)
        elif kind == "atomic":
            self.instruction(self.ATOMIC_START)
            self.emit(node[1])
            self.instruction(self.ATOMIC_END)
        elif kind == "conditional":
            test = self.instruction(self.COND, node[1])
            yes = len(self.current)
            self.emit(node[2])
            jump = self.instruction(self.JUMP)
            no = len(self.current)
            self.emit(node[3])
            end = len(self.current)
            self.patch(test, b=yes, c=no)
            self.patch(jump, a=end)
        else:
            raise RuntimeError(f"unknown bytecode node {kind}")

    def build(self, node, groups):
        self.emit(node)
        self.instruction(self.MATCH)
        return _vm_native.build([list(map(tuple, program)) for program in self.programs], self.classes, groups)


def _template_parts(value, pattern, byte_mode):
    if isinstance(value, (bytearray, memoryview)):
        value = bytes(value)
    if not isinstance(value, (str, bytes)):
        raise TypeError("decoding to str: need a bytes-like object, function found")
    if byte_mode != isinstance(value, bytes):
        expected = "bytes-like object" if byte_mode else "str instance"
        actual = "str" if isinstance(value, str) else "bytes"
        raise TypeError(f"sequence item 0: expected a {expected}, {actual} found")
    text = value.decode("latin1") if isinstance(value, bytes) else value
    output = []
    literal = []

    def flush():
        if literal:
            part = "".join(literal)
            output.append(part.encode("latin1") if byte_mode else part)
            literal.clear()
    index = 0
    simple = {"a": "\a", "b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t", "v": "\v", "\\": "\\"}
    while index < len(text):
        char = text[index]
        if char != "\\":
            literal.append(char)
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
                if number > pattern.groups:
                    raise PatternError(f"invalid group reference {number}", value, name_start)
            else:
                if not name.isidentifier() or (byte_mode and not name.isascii()):
                    raise PatternError(f"bad character in group name {name!r}", value, name_start)
                if name not in pattern.groupindex:
                    raise IndexError(f"unknown group name {name!r}")
                number = pattern.groupindex[name]
            flush()
            output.append(number)
        elif char.isdigit():
            digits = char
            if index < len(text) and text[index].isdigit():
                digits += text[index]
                index += 1
            number = int(digits)
            if number > pattern.groups:
                raise PatternError(f"invalid group reference {number}", value, slash + 1)
            flush()
            output.append(number)
        elif char in simple:
            literal.append(simple[char])
        elif char.isalpha():
            raise PatternError(f"bad escape \\{char}", value, slash)
        else:
            literal.append("\\" + char)
    flush()
    return tuple(output)


def _template(value, match):
    byte_mode = not isinstance(match.string, str)
    empty = b"" if byte_mode else ""
    return empty.join(match.group(part) or empty if isinstance(part, int) else part for part in _template_parts(value, match.re, byte_mode))


class _Scanner:
    __slots__ = ("pattern", "_string", "_pos", "_end", "_empty", "_searches")

    def __init__(self, pattern, string, pos=0, endpos=None):
        self.pattern = pattern
        self._string = string
        self._pos = max(pos, 0)
        self._end = len(string) if endpos is None else min(max(endpos, 0), len(string))
        self._empty = False
        self._searches = pattern.finditer(string, self._pos, self._end)

    def search(self):
        result = next(self._searches, None)
        if result is None:
            self._pos = self._end + 1
            return None
        self._empty = result.end() == result.start()
        self._pos = result.end() if not self._empty else result.start()
        return result

    def match(self):
        if self._pos > self._end:
            return None
        result = next(self._searches, None)
        if result is None or result.start() != self._pos:
            self._pos = self._end + 1
            return None
        self._empty = result.end() == result.start()
        self._pos = result.end() if not self._empty else result.start() + 1
        return result


Match = _vm_native.Match
_vm_native.configure(_template, _template_parts)


class Pattern(_vm_native.Pattern):
    __slots__ = ("__weakref__",)

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

    def scanner(self, string, pos=0, endpos=None):
        return _Scanner(self, string, pos, endpos)


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
    parser = _BytecodeParser(pattern, flags | implicit_unicode)
    node = parser.parse()
    if isinstance(pattern, str) and ((flags & int(ASCII) and parser.flags & int(UNICODE)) or (flags & int(UNICODE) and parser.flags & int(ASCII))):
        raise ValueError("ASCII and UNICODE flags are incompatible")
    if isinstance(pattern, bytes) and ((flags & int(ASCII) and parser.flags & int(LOCALE)) or (flags & int(LOCALE) and parser.flags & int(ASCII))):
        raise ValueError("ASCII and LOCALE flags are incompatible")
    vm = _BytecodeCompiler().build(node, parser.groups)
    result = Pattern(pattern, parser.flags & ~_BYTE, vm, parser.groups, dict(parser.groupindex))
    _CACHE[key] = result
    if flags & int(DEBUG):
        print(f"AST {node!r}")
    return result


def purge():
    _CACHE.clear()


def search(pattern, string, flags=0):
    flags = int(flags)
    cached = _CACHE.get((type(pattern), pattern, flags)) if isinstance(pattern, (str, bytes)) else None
    return (cached if cached is not None else compile(pattern, flags)).search(string)


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
    special = set("()[]{}?*+-|^$\\.&~# \t\n\r\v\f")
    if isinstance(pattern, (bytes, bytearray, memoryview)):
        pattern = bytes(pattern)
        return b"".join((b"\\" + bytes([char])) if chr(char) in special else bytes([char]) for char in pattern)
    return "".join("\\" + char if char in special else char for char in pattern)


__all__ = ["match", "fullmatch", "search", "sub", "subn", "split", "findall", "finditer", "compile", "purge", "escape", "error", "Pattern", "Match", "A", "I", "L", "M", "S", "X", "U", "ASCII", "IGNORECASE", "LOCALE", "MULTILINE", "DOTALL", "VERBOSE", "UNICODE", "NOFLAG", "RegexFlag", "PatternError"]
