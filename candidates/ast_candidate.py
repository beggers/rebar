"""From-scratch recursive AST/backtracking candidate for the frozen re P0 contract."""

import enum
import operator
import os
import types
import unicodedata
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


class _Parser:
    def __init__(self, original, flags):
        self.original = original
        self.text = original.decode("latin1") if isinstance(original, bytes) else original
        self.byte_mode = isinstance(original, bytes)
        self.flags = int(flags) | (_BYTE if self.byte_mode else 0)
        self.index = 0
        self.groups = 0
        self.groupindex = {}
        self.groupwidth = {}
        self.global_allowed = True
        self.group_depth = 0

    def fail(self, msg, pos=None, pattern=True):
        raise PatternError(msg, self.original if pattern else None, pos)

    def peek(self):
        return self.text[self.index] if self.index < len(self.text) else None

    def take(self):
        value = self.peek()
        self.index += value is not None
        return value

    def skip_verbose(self, flags):
        if not flags & int(VERBOSE):
            return
        while self.index < len(self.text):
            value = self.text[self.index]
            if value in " \t\n\r\v\f":
                self.index += 1
            elif value == "#":
                end = self.text.find("\n", self.index)
                self.index = len(self.text) if end < 0 else end + 1
            else:
                return

    def parse(self):
        node = self.alternation(self.flags)
        self.skip_verbose(self.flags)
        if self.index != len(self.text):
            self.fail("unbalanced parenthesis", self.index)
        return node

    def alternation(self, flags, stop=")"):
        branches = [self.sequence(flags, stop)]
        while self.peek() == "|":
            self.global_allowed = False
            self.index += 1
            branch_flags = self.flags if self.group_depth == 0 else flags
            branches.append(self.sequence(branch_flags, stop))
        if len(branches) == 1:
            return branches[0]
        return ("alt", branches)

    def sequence(self, flags, stop=")"):
        nodes = []
        while True:
            self.skip_verbose(flags)
            char = self.peek()
            if char is None or char in {"|", stop}:
                break
            start = self.index
            atom = self.atom(flags)
            self.skip_verbose(flags)
            quant = self.peek()
            if quant in {"*", "+", "?", "{"}:
                parsed = self.quantifier(atom, flags)
                if parsed is not None:
                    atom = parsed
            if atom[0] == "setflags":
                if self.group_depth or not self.global_allowed:
                    self.fail("global flags not at the start of the expression", start)
                flags = atom[1]
                self.flags = flags
            else:
                if atom != ("seq", []) or self.text[start + 1:start + 3] != "?#":
                    self.global_allowed = False
                nodes.append(atom)
        return ("seq", nodes)

    def quantifier(self, atom, flags):
        if atom[0] in {"anchor", "boundary", "look"}:
            self.fail("nothing to repeat", self.index)
        start = self.index
        char = self.take()
        if char == "*":
            minimum, maximum = 0, None
        elif char == "+":
            minimum, maximum = 1, None
        elif char == "?":
            minimum, maximum = 0, 1
        else:
            close = self.text.find("}", self.index)
            if close < 0:
                self.index = start
                return None
            spec = self.text[self.index:close]
            if not spec or any(ch not in "0123456789," for ch in spec) or spec.count(",") > 1:
                self.index = start
                return None
            if "," not in spec:
                minimum = maximum = int(spec)
            else:
                left, right = spec.split(",", 1)
                minimum = int(left) if left else 0
                maximum = int(right) if right else None
            self.index = close + 1
            if maximum is not None and minimum > maximum:
                self.fail("min repeat greater than max repeat", start + 1)
        mode = "greedy"
        if self.peek() in {"?", "+"}:
            mode = "lazy" if self.take() == "?" else "possessive"
        if self.peek() in {"*", "+", "?"} or self.brace_repeat(self.index):
            self.fail("multiple repeat", self.index)
        return ("repeat", atom, minimum, maximum, mode, flags)

    def brace_repeat(self, position):
        if self.text[position:position + 1] != "{":
            return False
        close = self.text.find("}", position + 1)
        if close < 0:
            return False
        value = self.text[position + 1:close]
        return bool(value) and value.count(",") <= 1 and all(item in "0123456789," for item in value)

    def atom(self, flags):
        start = self.index
        char = self.take()
        if char == ".":
            return ("dot", flags)
        if char == "^":
            return ("anchor", "^", flags)
        if char == "$":
            return ("anchor", "$", flags)
        if char == "[":
            return self.charclass(flags, start)
        if char == "\\":
            return self.escape(flags, False, start)
        if char == "(":
            return self.group(flags, start)
        if char in {"*", "+", "?"}:
            self.fail("nothing to repeat", start)
        if char == "{" and self.brace_repeat(start):
            self.fail("nothing to repeat", start)
        return ("lit", char, flags)

    def escape(self, flags, in_class, slash):
        char = self.take()
        if char is None:
            self.fail("bad escape (end of pattern)", slash)
        simple = {"a": "\a", "f": "\f", "n": "\n", "r": "\r", "t": "\t", "v": "\v"}
        if char in simple:
            return ("lit", simple[char], flags)
        if char == "b":
            return ("lit", "\b", flags) if in_class else ("boundary", True, flags)
        if char == "B" and not in_class:
            return ("boundary", False, flags)
        if char in "dDsSwW":
            return ("category", char, flags)
        if char in "AZz" and not in_class:
            return ("anchor", char, flags)
        if char == "x":
            digits = self.text[self.index:self.index + 2]
            if len(digits) != 2 or any(ch not in "0123456789abcdefABCDEF" for ch in digits):
                valid = []
                for item in digits:
                    if item not in "0123456789abcdefABCDEF":
                        break
                    valid.append(item)
                self.fail(f"incomplete escape \\x{''.join(valid)}", slash)
            self.index += 2
            return ("lit", chr(int(digits, 16)), flags)
        if char in {"u", "U"} and not self.byte_mode:
            size = 4 if char == "u" else 8
            digits = self.text[self.index:self.index + size]
            if len(digits) != size or any(ch not in "0123456789abcdefABCDEF" for ch in digits):
                valid = []
                for item in digits:
                    if item not in "0123456789abcdefABCDEF":
                        break
                    valid.append(item)
                self.fail(f"incomplete escape \\{char}{''.join(valid)}", slash)
            self.index += size
            value = int(digits, 16)
            if value > 0x10FFFF:
                self.fail(f"bad escape \\{char}{digits}", slash)
            return ("lit", chr(value), flags)
        if char == "N" and not self.byte_mode:
            if self.peek() != "{":
                self.fail("missing {", slash + 2)
            self.index += 1
            end = self.text.find("}", self.index)
            if end == self.index or (end < 0 and self.index == len(self.text)):
                self.fail("missing character name", slash + 3)
            if end < 0:
                self.fail("missing }, unterminated name", slash + 3)
            name = self.text[self.index:end]
            self.index = end + 1
            try:
                value = unicodedata.lookup(name)
            except KeyError:
                self.fail(f"undefined character name {name!r}", slash)
            if len(value) != 1:
                self.fail(f"undefined character name {name!r}", slash)
            return ("lit", value, flags)
        if char in "0123456789":
            digits = char
            octal = char == "0" or in_class or (
                char in "1234567"
                and self.index + 1 < len(self.text)
                and self.text[self.index] in "01234567"
                and self.text[self.index + 1] in "01234567"
            )
            if octal:
                if char not in "01234567":
                    self.fail(f"bad escape \\{char}", slash)
                while len(digits) < 3 and self.peek() is not None and self.peek() in "01234567":
                    digits += self.take()
                value = int(digits, 8)
                if value > 0o377:
                    self.fail(f"octal escape value \\{digits} outside of range 0-0o377", slash)
                return ("lit", chr(value), flags)
            if self.peek() is not None and self.peek() in "0123456789":
                digits += self.take()
            number = int(digits)
            if number > self.groups:
                self.fail(f"invalid group reference {number}", slash + 1)
            return ("backref", number, flags)
        if char.isalpha():
            self.fail(f"bad escape \\{char}", slash)
        return ("lit", char, flags)

    def charclass(self, flags, start):
        negate = self.peek() == "^"
        if negate:
            self.index += 1
        items = []
        first = True
        while self.index < len(self.text):
            if self.peek() == "]" and not first:
                self.index += 1
                if "&&" in self.text[start:self.index]:
                    warnings.warn(f"Possible set intersection at position {self.text.find('&&', start, self.index)}", FutureWarning, skip_file_prefixes=_WARNING_PREFIX)
                if self.text[start + 1:start + 2] == "[":
                    warnings.warn(f"Possible nested set at position {start + 1}", FutureWarning, skip_file_prefixes=_WARNING_PREFIX)
                for marker, label in (("||", "union"), ("~~", "symmetric difference"), ("--", "difference")):
                    location = self.text.find(marker, start, self.index)
                    if location >= 0:
                        warnings.warn(f"Possible set {label} at position {location}", FutureWarning, skip_file_prefixes=_WARNING_PREFIX)
                return ("class", items, negate, flags)
            first = False
            left_start = self.index
            if self.peek() == "\\":
                slash = self.index
                self.index += 1
                left = self.escape(flags, True, slash)
            else:
                left = ("lit", self.take(), flags)
            if self.peek() == "-" and self.index + 1 < len(self.text) and self.text[self.index + 1] != "]":
                dash = self.index
                self.index += 1
                if self.peek() == "\\":
                    self.index += 1
                    right = self.escape(flags, True, dash + 1)
                else:
                    right = ("lit", self.take(), flags)
                if left[0] != "lit" or right[0] != "lit":
                    self.fail(f"bad character range {self.text[left_start:self.index]}", left_start)
                if ord(left[1]) > ord(right[1]):
                    self.fail(f"bad character range {left[1]}-{right[1]}", dash - 1)
                items.append(("range", left[1], right[1]))
            else:
                items.append(left)
        self.fail("unterminated character set", start)

    def read_name(self, terminator, name_start):
        end = self.text.find(terminator, self.index)
        if end < 0:
            self.fail(f"missing {terminator}, unterminated name", name_start)
        name = self.text[self.index:end]
        self.index = end + 1
        if not name:
            self.fail("missing group name", name_start)
        if not name.isidentifier() or (self.byte_mode and not name.isascii()):
            if self.byte_mode:
                shown = "".join(char if char.isascii() else f"\\x{ord(char):02x}" for char in name)
                self.fail(f"bad character in group name '{shown}'", name_start)
            self.fail(f"bad character in group name {name!r}", name_start)
        return name

    def group(self, flags, start):
        self.group_depth += 1
        try:
            return self._group(flags, start)
        finally:
            self.group_depth -= 1

    def _group(self, flags, start):
        if self.peek() != "?":
            self.groups += 1
            number = self.groups
            child = self.alternation(flags)
            if self.take() != ")":
                self.fail("missing ), unterminated subpattern", start)
            self.groupwidth[number] = _width(child, self.groupwidth)
            return ("group", number, child)
        self.index += 1
        char = self.take()
        if char == ":":
            child = self.alternation(flags)
            if self.take() != ")":
                self.fail("missing ), unterminated subpattern", start)
            return child
        if char in {"=", "!"}:
            child = self.alternation(flags)
            if self.take() != ")":
                self.fail("missing ), unterminated subpattern", start)
            return ("look", "ahead", char == "=", child, None)
        if char == "<" and self.peek() in {"=", "!"}:
            positive = self.take() == "="
            child = self.alternation(flags)
            if self.take() != ")":
                self.fail("missing ), unterminated subpattern", start)
            minimum, maximum = _width(child, self.groupwidth)
            if minimum != maximum:
                self.fail("look-behind requires fixed-width pattern", pattern=False)
            return ("look", "behind", positive, child, minimum)
        if char == ">":
            child = self.alternation(flags)
            if self.take() != ")":
                self.fail("missing ), unterminated subpattern", start)
            return ("atomic", child)
        if char == "#":
            end = self.text.find(")", self.index)
            if end < 0:
                self.fail("missing ), unterminated comment", start)
            self.index = end + 1
            return ("seq", [])
        if char == "P":
            kind = self.take()
            if kind == "<":
                name_start = self.index
                name = self.read_name(">", name_start)
                self.groups += 1
                number = self.groups
                if name in self.groupindex:
                    old = self.groupindex[name]
                    self.fail(f"redefinition of group name {name!r} as group {number}; was group {old}", name_start)
                self.groupindex[name] = number
                child = self.alternation(flags)
                if self.take() != ")":
                    self.fail("missing ), unterminated subpattern", start)
                self.groupwidth[number] = _width(child, self.groupwidth)
                return ("group", number, child)
            if kind == "=":
                name_start = self.index
                name = self.read_name(")", name_start)
                if name not in self.groupindex:
                    self.fail(f"unknown group name {name!r}", name_start)
                return ("backref", self.groupindex[name], flags)
            self.fail("unknown extension ?P", start + 1)
        if char == "(":
            ref_start = self.index
            end = self.text.find(")", self.index)
            if end < 0:
                self.fail("missing ), unterminated name", ref_start)
            ref = self.text[self.index:end]
            self.index = end + 1
            if ref.isdecimal():
                number = int(ref)
                if number < 1 or number > self.groups:
                    self.fail(f"invalid group reference {number}", ref_start)
            else:
                if ref not in self.groupindex:
                    self.fail(f"unknown group name {ref!r}", ref_start)
                number = self.groupindex[ref]
            yes = self.sequence(flags)
            no = ("seq", [])
            if self.peek() == "|":
                self.index += 1
                no = self.sequence(flags)
            if self.take() != ")":
                self.fail("missing ), unterminated subpattern", start)
            return ("conditional", number, yes, no)
        if char is not None and char in "aiLmsux-":
            self.index -= 1
            enabled = 0
            disabled = 0
            negative = False
            mapping = {"a": int(ASCII), "i": int(IGNORECASE), "L": int(LOCALE), "m": int(MULTILINE), "s": int(DOTALL), "u": int(UNICODE), "x": int(VERBOSE)}
            while self.peek() is not None and self.peek() not in {":", ")"}:
                item = self.take()
                if item == "-":
                    negative = True
                elif item in mapping:
                    if negative:
                        if item in "aLu":
                            self.fail("bad inline flags: cannot turn off flags 'a', 'u' and 'L'", self.index)
                        disabled |= mapping[item]
                    else:
                        if item == "L" and not self.byte_mode:
                            self.fail("bad inline flags: cannot use 'L' flag with a str pattern", self.index)
                        if item == "u" and self.byte_mode:
                            self.fail("bad inline flags: cannot use 'u' flag with a bytes pattern", self.index)
                        if item in "aLu" and enabled & int(ASCII | LOCALE | UNICODE):
                            self.fail("bad inline flags: flags 'a', 'u' and 'L' are incompatible", self.index)
                        enabled |= mapping[item]
                else:
                    if negative and not disabled and item in "+*?{":
                        self.fail("missing flag", self.index - 1)
                    if negative and item in "+*?{":
                        self.fail("missing :", self.index - 1)
                    if not negative and item in "+*?{":
                        self.fail("missing -, : or )", self.index - 1)
                    self.fail("unknown flag", self.index - 1)
            if enabled & disabled:
                self.fail("bad inline flags: flag turned on and off", self.index)
            new_flags = (flags | enabled) & ~disabled
            if enabled & int(ASCII | LOCALE):
                new_flags &= ~int(UNICODE)
            elif enabled & int(UNICODE):
                new_flags &= ~int(ASCII | LOCALE)
            terminator = self.take()
            if negative and not disabled:
                self.fail("missing flag", self.index)
            if negative and terminator in {None, ")"}:
                self.fail("missing :", self.index - (terminator == ")"))
            if terminator is None:
                self.fail("missing -, : or )", self.index)
            if terminator == ")":
                return ("setflags", new_flags)
            child = self.alternation(new_flags)
            if self.take() != ")":
                self.fail("missing ), unterminated subpattern", start)
            return child
        self.fail(f"unknown extension ?{char}", start + 1)


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


class _Engine:
    def __init__(self, node, text, endpos):
        self.node = node
        self.text = text
        self.endpos = endpos

    def run(self, node, state):
        kind = node[0]
        pos, captures, last = state
        if kind == "lit":
            if pos < self.endpos and _equal(node[1], self.text[pos], node[2]):
                yield pos + 1, captures, last
            return
        if kind == "dot":
            if pos < self.endpos and (node[1] & int(DOTALL) or self.text[pos] != "\n"):
                yield pos + 1, captures, last
            return
        if kind == "category":
            if pos < self.endpos and _category(self.text[pos], node[1], node[2]):
                yield pos + 1, captures, last
            return
        if kind == "class":
            if pos < self.endpos and _class_match(node, self.text[pos]):
                yield pos + 1, captures, last
            return
        if kind == "anchor":
            code, flags = node[1], node[2]
            if code == "^":
                okay = pos == 0 or (flags & int(MULTILINE) and pos > 0 and self.text[pos - 1] == "\n")
            elif code == "$":
                okay = pos == self.endpos or (pos + 1 == self.endpos and self.text[pos:pos + 1] == "\n") or (flags & int(MULTILINE) and pos < self.endpos and self.text[pos] == "\n")
            elif code == "A":
                okay = pos == 0
            else:
                okay = pos == self.endpos
            if okay:
                yield state
            return
        if kind == "boundary":
            left = pos > 0 and _category(self.text[pos - 1], "w", node[2])
            right = pos < self.endpos and _category(self.text[pos], "w", node[2])
            if (left != right) == node[1]:
                yield state
            return
        if kind == "seq":
            def walk(index, current):
                if index == len(node[1]):
                    yield current
                else:
                    for updated in self.run(node[1][index], current):
                        yield from walk(index + 1, updated)
            yield from walk(0, state)
            return
        if kind == "alt":
            for branch in node[1]:
                yield from self.run(branch, state)
            return
        if kind == "group":
            number, child = node[1], node[2]
            for updated in self.run(child, state):
                end, groups, _ = updated
                values = list(groups)
                values[number] = (pos, end)
                yield end, tuple(values), number
            return
        if kind == "backref":
            span = captures[node[1]]
            if span is None:
                return
            value = self.text[span[0]:span[1]]
            target = self.text[pos:pos + len(value)]
            if pos + len(value) <= self.endpos and len(target) == len(value) and all(_equal(a, b, node[2]) for a, b in zip(value, target)):
                yield pos + len(value), captures, last
            return
        if kind == "repeat":
            child, minimum, maximum, mode = node[1:5]
            limit = self.endpos - pos + minimum + 1 if maximum is None else maximum

            def repeat(current, count):
                if mode == "lazy" and count >= minimum:
                    yield current
                if count < limit:
                    for updated in self.run(child, current):
                        if updated[0] == current[0]:
                            if count + 1 < minimum:
                                yield from repeat(updated, count + 1)
                            elif mode in {"lazy", "greedy", "possessive"}:
                                yield updated
                            continue
                        yield from repeat(updated, count + 1)
                if mode != "lazy" and count >= minimum:
                    yield current

            values = repeat(state, 0)
            if mode == "possessive":
                first = next(values, None)
                if first is not None:
                    yield first
            else:
                yield from values
            return
        if kind == "look":
            direction, positive, child, width = node[1:5]
            if direction == "ahead":
                matches = self.run(child, state)
            else:
                start = pos - width
                if start < 0:
                    matches = iter(())
                else:
                    matches = (item for item in self.run(child, (start, captures, last)) if item[0] == pos)
            first = next(matches, None)
            if positive and first is not None:
                yield pos, first[1], first[2]
            elif not positive and first is None:
                yield state
            return
        if kind == "atomic":
            first = next(self.run(node[1], state), None)
            if first is not None:
                yield first
            return
        if kind == "conditional":
            yield from self.run(node[2] if captures[node[1]] is not None else node[3], state)
            return
        raise RuntimeError(f"unknown engine node {kind}")


def _template(value, match):
    if isinstance(value, (bytearray, memoryview)):
        value = bytes(value)
    if not isinstance(value, (str, bytes)):
        raise TypeError("decoding to str: need a bytes-like object, function found")
    byte_mode = not isinstance(match.string, str)
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


def _slice(value, start, end):
    result = value[start:end]
    return bytes(result) if isinstance(result, (bytearray, memoryview)) else result


class Match:
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
        return _template(template, self)


class _Scanner:
    __slots__ = ("pattern", "_string", "_pos", "_start", "_end", "_empty")

    def __init__(self, pattern, string, pos=0, endpos=None):
        self.pattern = pattern
        self._string = string
        self._start = self._pos = max(pos, 0)
        self._end = len(string) if endpos is None else min(max(endpos, 0), len(string))
        self._empty = False

    def search(self):
        result = self.pattern._search(self._string, self._pos, self._end, self._empty, self._start)
        if result is None:
            self._pos = self._end + 1
            return None
        self._empty = result.end() == result.start()
        self._pos = result.end() if not self._empty else result.start()
        return result

    def match(self):
        if self._pos > self._end:
            return None
        result = self.pattern._at(self._string, self._pos, self._end, self._start, self._empty)
        if result is None:
            self._pos = self._end + 1
            return None
        self._empty = result.end() == result.start()
        self._pos = result.end() if not self._empty else result.start() + 1
        return result


class Pattern:
    __slots__ = ("pattern", "flags", "groups", "groupindex", "_node", "__weakref__")

    def __init__(self, value, flags, node, groups, groupindex):
        self.pattern = value
        self.flags = flags
        self.groups = groups
        self.groupindex = types.MappingProxyType(dict(groupindex))
        self._node = node

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
        if not isinstance(string, (str, bytes, bytearray, memoryview)):
            raise TypeError(f"expected string or bytes-like object, got '{type(string).__name__}'")
        if isinstance(self.pattern, str) and not isinstance(string, str):
            raise TypeError("cannot use a string pattern on a bytes-like object")
        if isinstance(self.pattern, bytes) and isinstance(string, str):
            raise TypeError("cannot use a bytes pattern on a string-like object")

    def _at(self, string, start, endpos, original_pos, require_nonempty=False):
        self._validate_string(string)
        text = bytes(string).decode("latin1") if not isinstance(string, str) else string
        engine = _Engine(self._node, text, endpos)
        state = (start, tuple([None] * (self.groups + 1)), None)
        for result in engine.run(self._node, state):
            end, captures, last = result
            if require_nonempty and end == start:
                continue
            values = list(captures)
            values[0] = (start, end)
            return Match(self, string, tuple(values), last, original_pos, endpos)
        return None

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
        text = bytes(string).decode("latin1") if not isinstance(string, str) else string
        start = max(pos, 0)
        state = (start, tuple([None] * (self.groups + 1)), None)
        for result in _Engine(self._node, text, end).run(self._node, state):
            if result[0] == end:
                captures = list(result[1])
                captures[0] = (start, end)
                return Match(self, string, tuple(captures), result[2], start, end)
        return None

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
        empty = b"" if not isinstance(string, str) else ""
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
            result.append(_slice(string, previous, item.start()))
            result.extend(item.groups())
            previous = item.end()
            count += 1
        result.append(_slice(string, previous, len(string)))
        return result

    def subn(self, repl, string, count=0):
        self._validate_string(string)
        if not callable(repl):
            _template(repl, Match(self, string, [(0, 0)] + [None] * self.groups, None, 0, len(string)))
        parts = []
        previous = 0
        replacements = 0
        for item in self.finditer(string):
            if count and replacements >= count:
                break
            parts.append(_slice(string, previous, item.start()))
            value = repl(item) if callable(repl) else item.expand(repl)
            if (not isinstance(string, str)) != isinstance(value, bytes):
                expected = "bytes-like object" if not isinstance(string, str) else "str instance"
                raise TypeError(f"sequence item {len(parts)}: expected a {expected}, {type(value).__name__} found")
            parts.append(value)
            previous = item.end()
            replacements += 1
        parts.append(_slice(string, previous, len(string)))
        return (b"" if not isinstance(string, str) else "").join(parts), replacements

    def sub(self, repl, string, count=0):
        return self.subn(repl, string, count)[0]

    def scanner(self, string, pos=0, endpos=None):
        self._validate_string(string)
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
    parser = _Parser(pattern, flags | implicit_unicode)
    node = parser.parse()
    if isinstance(pattern, str) and ((flags & int(ASCII) and parser.flags & int(UNICODE)) or (flags & int(UNICODE) and parser.flags & int(ASCII))):
        raise ValueError("ASCII and UNICODE flags are incompatible")
    if isinstance(pattern, bytes) and ((flags & int(ASCII) and parser.flags & int(LOCALE)) or (flags & int(LOCALE) and parser.flags & int(ASCII))):
        raise ValueError("ASCII and LOCALE flags are incompatible")
    result = Pattern(pattern, parser.flags & ~_BYTE, node, parser.groups, dict(parser.groupindex))
    _CACHE[key] = result
    if flags & int(DEBUG):
        print(f"AST {node!r}")
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
    special = set("()[]{}?*+-|^$\\.&~# \t\n\r\v\f")
    if isinstance(pattern, (bytes, bytearray, memoryview)):
        pattern = bytes(pattern)
        return b"".join((b"\\" + bytes([char])) if chr(char) in special else bytes([char]) for char in pattern)
    return "".join("\\" + char if char in special else char for char in pattern)


__all__ = ["match", "fullmatch", "search", "sub", "subn", "split", "findall", "finditer", "compile", "purge", "escape", "error", "Pattern", "Match", "A", "I", "L", "M", "S", "X", "U", "ASCII", "IGNORECASE", "LOCALE", "MULTILINE", "DOTALL", "VERBOSE", "UNICODE", "NOFLAG", "RegexFlag", "PatternError"]
