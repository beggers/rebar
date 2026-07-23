#!/usr/bin/env python3
"""Reproducible CPython differential checks for from-scratch Rust regex paths."""

from __future__ import annotations

import argparse
import importlib
import json
import random
import re
from pathlib import Path

from re import _casefix


SEED = 2026072307
MULTI_UPPER = tuple(value for value in range(0x110000) if len(chr(value).upper()) > 1)
CASEFOLD_GROUPS = (
    (0x0049, 0x0069, 0x0130, 0x0131),
    (0x004B, 0x006B, 0x212A), (0x0053, 0x0073, 0x017F),
    (0x00B5, 0x039C, 0x03BC), (0x00DF, 0x1E9E),
    (0x0345, 0x0399, 0x03B9, 0x1FBE), (0x0390, 0x1FD3),
    (0x03B0, 0x1FE3), (0x0392, 0x03B2, 0x03D0),
    (0x0395, 0x03B5, 0x03F5), (0x0398, 0x03B8, 0x03D1),
    (0x039A, 0x03BA, 0x03F0), (0x03A0, 0x03C0, 0x03D6),
    (0x03A1, 0x03C1, 0x03F1), (0x03A3, 0x03C2, 0x03C3),
    (0x03A6, 0x03C6, 0x03D5), (0x0412, 0x0432, 0x1C80),
    (0x0414, 0x0434, 0x1C81), (0x041E, 0x043E, 0x1C82),
    (0x0421, 0x0441, 0x1C83), (0x0422, 0x0442, 0x1C84, 0x1C85),
    (0x042A, 0x044A, 0x1C86), (0x0462, 0x0463, 0x1C87),
    (0xA64A, 0xA64B, 0x1C88), (0x1E60, 0x1E61, 0x1E9B),
    (0xFB05, 0xFB06),
)


def casefix_components():
    graph = {}
    for value, extras in _casefix._EXTRA_CASES.items():
        graph.setdefault(value, set()).update(extras)
        for extra in extras:
            graph.setdefault(extra, set()).add(value)
    remaining = set(graph)
    count = 0
    while remaining:
        todo = [remaining.pop()]
        count += 1
        while todo:
            for adjacent in graph[todo.pop()]:
                if adjacent in remaining:
                    remaining.remove(adjacent)
                    todo.append(adjacent)
    return count


def normalized(value):
    if isinstance(value, bytes):
        return {"bytes_hex": value.hex()}
    if isinstance(value, bytearray):
        return {"bytearray_hex": value.hex()}
    if isinstance(value, memoryview):
        return {"memoryview_hex": value.tobytes().hex()}
    if isinstance(value, tuple):
        return {"tuple": [normalized(item) for item in value]}
    if isinstance(value, list):
        return [normalized(item) for item in value]
    if isinstance(value, dict):
        return {str(key): normalized(item) for key, item in value.items()}
    return value


def match_value(match):
    if match is None:
        return None
    return {
        "span": normalized(match.span()),
        "regs": normalized(match.regs),
        "group": normalized(match.group()),
        "groups": normalized(match.groups()),
        "groups_default": normalized(match.groups(default=b"!" if isinstance(match.re.pattern, bytes) else "!")),
        "groupdict": normalized(match.groupdict()),
        "lastindex": match.lastindex,
        "lastgroup": match.lastgroup,
        "pos": match.pos,
        "endpos": match.endpos,
    }


def observed(action):
    try:
        return {"value": normalized(action())}
    except Exception as error:
        result = {"error": type(error).__name__, "message": str(error)}
        if isinstance(error, (re.PatternError,)) or all(
            hasattr(error, name) for name in ("msg", "pattern", "pos", "lineno", "colno")
        ):
            result["pattern_error"] = {
                name: normalized(getattr(error, name, None))
                for name in ("msg", "pattern", "pos", "lineno", "colno")
            }
        return result


def equivalent(expected, actual):
    if "error" not in expected and "error" not in actual:
        return expected == actual
    if expected.get("error") != actual.get("error"):
        return False
    if "pattern_error" in expected or "pattern_error" in actual:
        return expected.get("pattern_error") == actual.get("pattern_error")
    return True


def scan_values(pattern, subject, pos, endpos, method):
    scanner = pattern.scanner(subject, pos, endpos)
    values = []
    for _ in range((max(0, min(len(subject), endpos) - max(0, pos)) + 1) * 2 + 5):
        match = getattr(scanner, method)()
        values.append(match_value(match))
        if match is None:
            break
    else:
        raise RuntimeError("scanner did not terminate")
    return values


def record_check(failures, label, operation, pattern, subject, flags, action, oracle, actual, pos=None, endpos=None):
    expected = observed(lambda: action(oracle))
    got = observed(lambda: action(actual))
    if not equivalent(expected, got):
        row = {
            "label": label,
            "operation": operation,
            "pattern": repr(pattern),
            "subject": repr(subject),
            "flags": int(flags),
            "expected": expected,
            "actual": got,
        }
        if pos is not None:
            row["pos"] = pos
            row["endpos"] = endpos
        failures.append(row)
    return 1


def check(module, pattern, subject, flags, label, failures):
    oracle_result = observed(lambda: re.compile(pattern, flags))
    actual_result = observed(lambda: module.compile(pattern, flags))
    if "error" in oracle_result or "error" in actual_result:
        if not equivalent(oracle_result, actual_result):
            failures.append({"label": label, "operation": "compile", "pattern": repr(pattern), "subject": repr(subject), "flags": int(flags), "expected": oracle_result, "actual": actual_result})
        return 1

    oracle = re.compile(pattern, flags)
    actual = module.compile(pattern, flags)
    checks = 1
    length = len(subject)
    windows = (
        (0, length),
        (min(1, length), length),
        (0, max(0, length - 1)),
        (-2, length + 2),
        (min(length + 2, 5), max(0, length - 2)),
    )
    for pos, endpos in windows:
        actions = (
            ("search", lambda item: match_value(item.search(subject, pos, endpos))),
            ("match", lambda item: match_value(item.match(subject, pos, endpos))),
            ("fullmatch", lambda item: match_value(item.fullmatch(subject, pos, endpos))),
            ("findall", lambda item: item.findall(subject, pos, endpos)),
            ("findall-keywords", lambda item: item.findall(string=subject, pos=pos, endpos=endpos)),
            ("finditer", lambda item: [match_value(value) for value in item.finditer(subject, pos, endpos)]),
            ("scanner-search", lambda item: scan_values(item, subject, pos, endpos, "search")),
            ("scanner-match", lambda item: scan_values(item, subject, pos, endpos, "match")),
        )
        for operation, action in actions:
            checks += record_check(failures, label, operation, pattern, subject, flags, action, oracle, actual, pos, endpos)

    replacement = rb"<\g<0>>" if isinstance(pattern, bytes) else r"<\g<0>>"
    default = b"?" if isinstance(pattern, bytes) else "?"
    actions = (
        ("split", lambda item: item.split(subject)),
        ("split-limited", lambda item: item.split(subject, 2)),
        ("sub", lambda item: item.sub(replacement, subject)),
        ("subn-limited", lambda item: item.subn(replacement, subject, 2)),
        ("sub-callable", lambda item: item.sub(lambda match: match.group(0), subject, 2)),
        ("match-surface", lambda item: match_value(item.search(subject))),
        ("pattern-metadata", lambda item: (item.pattern, item.flags, item.groups, dict(item.groupindex))),
        ("group-default", lambda item: None if item.search(subject) is None else item.search(subject).groups(default)),
    )
    for operation, action in actions:
        checks += record_check(failures, label, operation, pattern, subject, flags, action, oracle, actual)
    return checks


def manual_cases():
    rows = [
        (r"((a)?)*", "", 0),
        (r"((a)?)*", "a", 0),
        (r"(a(b)?)+", "aba", 0),
        (r"(a?){2}", "", 0),
        (r"(a?){0}", "", 0),
        (r"(?=(a|ab))\1$", "ab", 0),
        (r"(?:(a)|a)(?(1)b|c)", "ac", 0),
        (r"(a|ab)", "ab", 0),
        (r"a{4294967294}", "aaa", 0),
        (r"(?:ab){4294967294}", "abab", 0),
        (r"(?:(a)|(b))+", "abba", 0),
        (r"((ab)?)*", "abab", 0),
        (r"(?=(a))a", "a", 0),
        (r"(?!(a)b)a", "a", 0),
        (r"(?<=(a))b", "ab", 0),
        (r"(?<!ab)c", "abc ac c", 0),
        (r"(?P<a>a)?(?(a)b|c)", "ab ac c", 0),
        (r"(?P<word>[a-z]+)-(?P=word)", "ab-ab x-y ab-a", 0),
        (r"(?:ab|abc|abcd)c", "abc abcc abcdc xabc", 0),
        (r"(?>a|ab)b", "ab abb", 0),
        (r"a*+a", "aaa", 0),
        (r"(?m)^\s*(?P<word>\w+)\s+(?P<num>\d+)\s*$", "café ٣\n雪 １２\nalpha 42\n", re.M),
        (r"(?a:\w+)|(?u:\w+)", "alpha café 雪_２", 0),
        (r"(?i:[a-z]+)(?-i:[A-Z]+)", "abCD ABcd xyZZ", 0),
        (r"(?i)[A-Z]+", "ABC İ ı ſ K ς σ µ μ ϐ β", re.I),
        (r"[\x1c-\x1f]", " \x1c\x1d\x1e\x1f\t\n", 0),
        (r"\s", " \x1c\x1d\x1e\x1f\u0085\u00a0\u2028", 0),
        (r"\s", " \x1c\x1d\x1e\x1f\u0085\u00a0\u2028", re.A),
        (r"\d", "0²¼٣２Ⅻ", 0),
        (r"\w", "a_²¼٣２Ⅻ\u0301", 0),
        (r"(?:|a|ab)", "ab a", 0),
        (r"a*", "baab", 0),
        (r"\b", " café a_1 雪", 0),
        (r"\B", " café a_1 雪", 0),
        (r"(?m)^abc$", "x\nabc\nabc\ny", re.M),
        (r"\Aabc\Z", "abc", 0),
        ("café", "café caféine café 雪café", 0),
        ("雪山", "雪山 x雪山 雪山雪山", 0),
        ("😀", "😀a😀😀", 0),
        ("\x00x", "a\x00x b\x00x", 0),
        (rb"(?P<first>[a-z]+)(?P<digits>[0-9]*)", b"ab12 cd ef3", 0),
        (rb"\b[a-z]+\b", bytearray(b"ab cd ef"), re.I),
        (rb"(?:ab|abc)c", memoryview(b"abc abcc zz"), 0),
        (rb"\s", bytes(range(32)), 0),
        (rb"\w", bytes(range(256)), 0),
    ]
    for left, right in (
        ("ς", "σ"), ("µ", "μ"), ("ϐ", "β"),
        ("ᲁ", "д"), ("ι", "ι"), ("ẛ", "ṡ"),
        ("İ", "i"), ("ı", "i"), ("ſ", "s"), ("K", "k"),
    ):
        escaped = re.escape(left)
        rows.extend((
            (left, right, re.I),
            (f"[{escaped}]", right, re.I),
            (f"[^{escaped}]", right, re.I),
            (f"(?i:{escaped})", right, 0),
            (f"(?a:{escaped})", right, re.I),
            (f"({escaped})\\1", left + right, re.I),
        ))
    for value, extras in sorted(_casefix._EXTRA_CASES.items()):
        for extra in sorted(extras):
            left, right = chr(value), chr(extra)
            escaped = re.escape(left)
            rows.extend((
                (left, right, re.I),
                (f"[{escaped}]", right, re.I),
                (f"[^{escaped}]", right, re.I),
                (f"(?i:{escaped})", right, 0),
                (f"({escaped})\\1", left + right, re.I),
            ))
    for value in MULTI_UPPER:
        char = chr(value)
        first = char.upper()[0]
        escaped = re.escape(first)
        rows.extend((
            (escaped, char, re.I),
            (f"[{escaped}]", char, re.I),
            (f"[{escaped}-{escaped}]", char, re.I),
            (f"[^{escaped}]", char, re.I),
            (f"({escaped})\\1", first + char, re.I),
        ))
    return rows


def generated(rng, index):
    family = index % 14
    flags = rng.choice((0, re.I, re.A, re.I | re.A, re.M, re.I | re.M))
    alphabet = " abXYZ019_.,;-İıſKßΩςσµμϐβᲁдιιẛṡ雪😀\x00\n"
    if family == 0:
        literal = "".join(rng.choice(alphabet[:-1]) for _ in range(rng.randrange(1, 7)))
        pattern = re.escape(literal)
        subject = " ".join(literal if rng.randrange(3) else "".join(rng.choice(alphabet) for _ in range(rng.randrange(7))) for _ in range(rng.randrange(8)))
    elif family == 1:
        atom = rng.choice((r"[A-Za-z0-9_.-]", r"[A-Z]", r"[0-9]", r"[^,;\s]", r"[a-z_]", r"[\u0100-\u04ff]", r"\w", r"\d", r"\s"))
        pattern = rng.choice(("", r"\b", r"(?<![A-Za-z0-9_])")) + atom + rng.choice(("+", "{1,6}", "*", "?")) + rng.choice(("", r"\b", r"(?![A-Za-z0-9_])"))
        subject = "".join(rng.choice(alphabet) for _ in range(rng.randrange(45)))
    elif family == 2:
        prefix = rng.choice(("pre", "read", "alpha", "ki", "ss"))
        words = [prefix + "".join(rng.choice("abcdeinorst012") for _ in range(rng.randrange(5))) for _ in range(rng.randrange(2, 14))]
        pattern = "(?:" + "|".join(map(re.escape, words)) + ")" + rng.choice(("", "!", "[0-9]", "(?:x|xy)", "(?:[-_][0-9]{1,3})?"))
        subject = " ".join(rng.choice(words).swapcase() + rng.choice(("", "!", "x", "-12")) for _ in range(rng.randrange(12)))
    elif family == 3:
        flags |= re.M
        atom = rng.choice((r"[A-Za-z]+", r"\w+", r"[^\n]+", r"(?:cat|catalog|cater)", r"(?P<word>\w+(?:[-']\w+)*)"))
        pattern = r"^" + rng.choice(("", r"\s*")) + atom + rng.choice(("", r"\s+[0-9]+", r"\s+(?P<num>\d+)")) + rng.choice(("$", r"\s*$"))
        subject = "\n".join("".join(rng.choice(alphabet[:-1]) for _ in range(rng.randrange(18))) for _ in range(rng.randrange(1, 7)))
    elif family == 4:
        pattern = rng.choice((r"((a)?)*", r"(a(b)?)+", r"(a?){2}", r"(?:|a|ab)", r"(?:(a)|(b))+", r"((ab)?)*", r"(?:a?b?){0,4}"))
        subject = "".join(rng.choice("ab ") for _ in range(rng.randrange(10)))
    elif family == 5:
        pattern = rng.choice((r"(?=(a|ab))\1$", r"(?=(a))a", r"(?!(a)b)a", r"a(?=b)", r"a(?!b)", r"(?=(?P<v>a+))(?P=v)"))
        subject = "".join(rng.choice("abc ") for _ in range(rng.randrange(12)))
    elif family == 6:
        pattern = rng.choice((r"(?<=ab)c", r"(?<!ab)c", r"(?<=(a))b", r"(?<=\b[a-z])\d", r"(?<![a-z]{2})[0-9]"))
        subject = "".join(rng.choice("abc019 ") for _ in range(rng.randrange(16)))
    elif family == 7:
        pattern = rng.choice((r"(?:(a)|a)(?(1)b|c)", r"(?P<a>a)?(?(a)b|c)", r"((a)?)(?(2)b|c)", r"(?P<w>[ab]+)-(?P=w)"))
        subject = "".join(rng.choice("abc- ") for _ in range(rng.randrange(14)))
    elif family == 8:
        pattern = rng.choice((r"(?>a|ab)b", r"(?>ab|a)b", r"a*+a", r"(?:ab){1,4}+", r"[a-c]++d"))
        subject = "".join(rng.choice("abcd ") for _ in range(rng.randrange(14)))
    elif family == 9:
        pattern = rng.choice((r"\A[a-z]+\Z", r"(?m)^[a-z]*$", r"\b\w+\b", r"\B[a-z]*\B", r"(?:^|\n)[a-z]+"))
        subject = "".join(rng.choice("abc 019_\n") for _ in range(rng.randrange(18)))
    elif family == 10:
        pairs = (("ς", "σ"), ("µ", "μ"), ("ϐ", "β"), ("ᲁ", "д"), ("ι", "ι"), ("ẛ", "ṡ"), ("İ", "i"), ("ı", "i"), ("ſ", "s"), ("K", "k"))
        left, right = rng.choice(pairs)
        escaped = re.escape(left)
        pattern = rng.choice((escaped, f"[{escaped}]", f"[^{escaped}]", f"(?i:{escaped})", f"({escaped})\\1"))
        flags |= re.I
        subject = " ".join(rng.choice((left, right, left + right, "x")) for _ in range(rng.randrange(1, 9)))
    elif family == 11:
        pattern = rng.choice((r"(?a:\w+)|(?u:\w+)", r"(?i:[a-z]+)(?-i:[A-Z]+)", r"(?a:\d+)|\d+", r"(?i:[a-z])(?-i:[A-Z])", r"(?s:.)+?"))
        subject = "".join(rng.choice(alphabet) for _ in range(rng.randrange(16)))
    elif family == 12:
        pattern = rng.choice((r"(?P<x>a)(?P<y>b)?", r"(a)?(b)", r"(?P<d>[0-9]+)", r"(a)|(b)", r"(?P<w>\w+)"))
        subject = "".join(rng.choice("ab019_ \n") for _ in range(rng.randrange(18)))
    else:
        pattern = rng.choice((r"[a-z]+", r"\s+", r"\w+", r"(?:ab|abc)c", r"(?P<a>a)?b", r"(?<=a)b", r"a*"))
        subject = "".join(rng.choice("abcz019_ \t\n") for _ in range(rng.randrange(20)))

    if family in (2, 4, 5, 6, 7, 8, 9, 12, 13) and index % 3 == 1:
        try:
            pattern = pattern.encode("ascii")
            subject = subject.encode("ascii")
            flags &= ~re.UNICODE
            if index % 9 == 1:
                subject = bytearray(subject)
            elif index % 9 == 4:
                subject = memoryview(subject)
        except UnicodeEncodeError:
            pass
    return pattern, subject, flags


def error_surface(module, failures):
    text = "abc"
    cases = (
        ("compile-unclosed-group", lambda item: item.compile("(")),
        ("compile-unclosed-class", lambda item: item.compile("[")),
        ("compile-repeat", lambda item: item.compile("*a")),
        ("compile-duplicate-name", lambda item: item.compile(r"(?P<x>a)(?P<x>b)")),
        ("compile-invalid-reference", lambda item: item.compile(r"(a)\2")),
        ("compile-variable-lookbehind", lambda item: item.compile(r"(?<=a+)b")),
        ("compile-bytes-unicode-flag", lambda item: item.compile(b"a", re.U)),
        ("compile-text-locale-flag", lambda item: item.compile("a", re.L)),
        ("wrong-text-subject", lambda item: item.compile("a").search(b"a")),
        ("wrong-bytes-subject", lambda item: item.compile(b"a").search("a")),
        ("noncontiguous-subject", lambda item: item.compile(b"a").search(memoryview(b"aabb")[::2])),
        ("findall-missing", lambda item: item.compile("a").findall()),
        ("findall-too-many", lambda item: item.compile("a").findall("a", 0, 1, 2)),
        ("findall-unknown-keyword", lambda item: item.compile("a").findall("a", other=1)),
        ("findall-duplicate-string", lambda item: item.compile("a").findall("a", string="a")),
        ("findall-invalid-position", lambda item: item.compile("a").findall("a", "0")),
        ("invalid-match-group", lambda item: item.search("a", "a").group(2)),
        ("invalid-named-group", lambda item: item.search("a", "a").group("missing")),
        ("invalid-template-backreference", lambda item: item.sub("a", r"\2", text)),
        ("invalid-template-escape", lambda item: item.sub("a", r"\k", text)),
    )
    for label, action in cases:
        expected = observed(lambda action=action: action(re))
        actual = observed(lambda action=action: action(module))
        if not equivalent(expected, actual):
            failures.append({"label": "error." + label, "operation": "public-error", "expected": expected, "actual": actual})
    return len(cases)


def invalid_window_matrix(module, failures):
    patterns = ("", r"\b", r"\B", "a?", "a*", "^", "$", "((a)?)*", "(a?){0}", "(?:|a)")
    subjects = ("", "a", "ab")
    windows = ((2, 0), (3, 0), (3, 1), (-3, -1), (-3, 0), (0, -2))
    checks = 0
    for pattern_index, pattern in enumerate(patterns):
        oracle = re.compile(pattern)
        actual = module.compile(pattern)
        for subject_index, subject in enumerate(subjects):
            for window_index, (pos, endpos) in enumerate(windows):
                actions = (
                    ("search", lambda item: match_value(item.search(subject, pos, endpos))),
                    ("match", lambda item: match_value(item.match(subject, pos, endpos))),
                    ("fullmatch", lambda item: match_value(item.fullmatch(subject, pos, endpos))),
                    ("findall", lambda item: item.findall(subject, pos, endpos)),
                    ("finditer", lambda item: [match_value(value) for value in item.finditer(subject, pos, endpos)]),
                    ("scanner-search", lambda item: scan_values(item, subject, pos, endpos, "search")),
                    ("scanner-match", lambda item: scan_values(item, subject, pos, endpos, "match")),
                )
                label = f"invalid-window-{pattern_index}-{subject_index}-{window_index}"
                for operation, action in actions:
                    checks += record_check(failures, label, operation, pattern, subject, 0, action, oracle, actual, pos, endpos)
    return checks


def surrogate_matrix(module, failures):
    low, high = "\ud800", "\udfff"
    cases = (
        (low, low), (high, high), ("[" + low + "]", low),
        ("[" + low + "-" + high + "]", low),
        ("[" + low + "-" + high + "]", high),
        (r"\ud800", low), (r"[\ud800-\udfff]", low),
        (r"[\ud800-\udfff]", high),
        ("(?P<x>" + low + ")(?P=x)", low + low),
        ("(" + low + r")\1", low + low), (r"(.)\1", low + low),
        ("x" + low + "y", "x" + low + "y"), ("[^" + low + "]", "x"),
        (r"[\ud800-\udfff]+", "x" + low + high + "z"),
        (r".", low), (r"\w", low), (r"\W", low),
        (r"\b", low), ("😀", "😀"),
    )
    checks = 0
    for index, (pattern, subject) in enumerate(cases):
        for flags in (0, re.I, re.A, re.I | re.A):
            for operation in ("search", "match", "fullmatch", "findall", "finditer"):
                def action(engine, pattern=pattern, subject=subject, flags=flags, operation=operation):
                    compiled = engine.compile(pattern, flags)
                    value = getattr(compiled, operation)(subject)
                    if operation == "findall":
                        return value
                    if operation == "finditer":
                        return [match_value(match) for match in value]
                    return match_value(value)

                checks += record_check(failures, f"surrogate-{index}", operation, pattern, subject, flags, action, re, module)
    return checks


def backreference_matrix(module, failures):
    variants = (
        (r"(?i)(.)\1", 0),
        (r"(?i)(?P<part>.)(?P=part)", 0),
        (r"(.)(?i:\1)", 0),
        (r"(?P<part>.)(?i:(?P=part))", 0),
        (r"(?i:(.))(?-i:\1)", 0),
        (r"(?ai)(.)\1", 0),
        (r"(?ai)(?P<part>.)(?P=part)", 0),
    )
    checks = 0
    for group_index, group in enumerate(CASEFOLD_GROUPS):
        for left in group:
            for right in group:
                subject = chr(left) + chr(right)
                for variant_index, (pattern, flags) in enumerate(variants):
                    def action(engine, pattern=pattern, subject=subject, flags=flags):
                        return match_value(engine.compile(pattern, flags).fullmatch(subject))

                    label = f"backreference-{group_index}-U+{left:04X}-U+{right:04X}-{variant_index}"
                    checks += record_check(failures, label, "fullmatch", pattern, subject, flags, action, re, module)
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", default="candidates.rust_candidate")
    parser.add_argument("--output", required=True)
    parser.add_argument("--seeded-cases", type=int, default=4096)
    parser.add_argument("--seed", type=int, default=SEED)
    selected = parser.add_mutually_exclusive_group()
    selected.add_argument("--case-index", type=int)
    selected.add_argument("--manual-index", type=int)
    args = parser.parse_args()
    if args.seeded_cases < 0:
        parser.error("--seeded-cases must not be negative")
    module = importlib.import_module(args.module)
    failures = []
    checks = 0
    manual = manual_cases()
    if args.manual_index is not None:
        if not 0 <= args.manual_index < len(manual):
            parser.error(f"--manual-index must be between 0 and {len(manual) - 1}")
        checks += check(module, *manual[args.manual_index], f"manual-{args.manual_index}", failures)
    elif args.case_index is None:
        for index, case in enumerate(manual):
            checks += check(module, *case, f"manual-{index}", failures)
        checks += error_surface(module, failures)
        checks += invalid_window_matrix(module, failures)
        checks += surrogate_matrix(module, failures)
        checks += backreference_matrix(module, failures)
    elif not 0 <= args.case_index < args.seeded_cases:
        parser.error("--case-index must be nonnegative and less than --seeded-cases")
    rng = random.Random(args.seed)
    for index in range(0 if args.manual_index is not None else args.seeded_cases):
        case = generated(rng, index)
        if args.case_index is not None and index != args.case_index:
            continue
        checks += check(module, *case, f"seeded-{index}", failures)
        if index and index % 512 == 0:
            print(f"checked seeded {index}/{args.seeded_cases}; mismatches={len(failures)}", flush=True)
    report = {
        "schema": "rebar-rust-v6-paths-probe-v1",
        "module": args.module,
        "seed": args.seed,
        "manual_cases": 1 if args.manual_index is not None else len(manual) if args.case_index is None else 0,
        "manual_index": args.manual_index,
        "casefix_keys": len(_casefix._EXTRA_CASES),
        "casefix_directed_edges": sum(map(len, _casefix._EXTRA_CASES.values())),
        "casefix_components": casefix_components(),
        "multi_upper_codepoints": len(MULTI_UPPER),
        "casefold_groups": len(CASEFOLD_GROUPS),
        "backreference_pairs": sum(len(group) ** 2 for group in CASEFOLD_GROUPS),
        "backreference_variants": 7,
        "invalid_window_checks": 1260 if args.manual_index is None and args.case_index is None else 0,
        "surrogate_checks": 380 if args.manual_index is None and args.case_index is None else 0,
        "seeded_cases": args.seeded_cases,
        "case_index": args.case_index,
        "correctness_checks": checks,
        "failed": len(failures),
        "failures": failures,
    }
    Path(args.output).write_text(json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "failures"}, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
