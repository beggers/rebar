"""Expanded, versioned CPython 3.14.6 re correctness matrix and deep differential cases."""

import importlib.util
import random
from pathlib import Path


V1_PATH = Path(__file__).resolve().parents[1] / "v1" / "suite.py"
spec = importlib.util.spec_from_file_location("rebar_oracle_v1_parent", V1_PATH)
v1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v1)

SEEDS = {
    **v1.SEEDS,
    "deep_str": 1979121301,
    "deep_bytes": 1979121302,
}

OBLIGATIONS = {
    **v1.OBLIGATIONS,
    "API-GENERIC": "Pattern[str/bytes] and Match[str/bytes] generic aliases",
    "API-BYTESLIKE": "bytearray and memoryview subjects/replacements/escape",
    "API-REPRESENTATION": "documented pattern and match representations",
    "API-MATCH-COPY": "atomic copy/deepcopy and pickle rejection for Match",
    "E-DEPRECATION": "3.13+ positional split/sub/subn deprecation warnings",
    "S-LOOKBEHIND-REF": "fixed-width numbered/named lookbehind references",
    "S-DEEP-FUZZ": "larger seeded combinations of advanced documented syntax",
}


def C(case_id, kind, obligations, **values):
    return {"id": case_id, "kind": kind, "obligations": obligations.split(), **values}


EXTRA_CASES = [
    C("v2.generic.pattern-str", "generic", "API-GENERIC API-PATTERN", owner="Pattern", argument="str"),
    C("v2.generic.pattern-bytes", "generic", "API-GENERIC API-PATTERN", owner="Pattern", argument="bytes"),
    C("v2.generic.match-str", "generic", "API-GENERIC API-MATCH-OBJECT", owner="Match", argument="str"),
    C("v2.generic.match-bytes", "generic", "API-GENERIC API-MATCH-OBJECT", owner="Match", argument="bytes"),
    C("v2.byteslike.bytearray-search", "byteslike", "API-BYTESLIKE API-SEARCH API-MATCH-OBJECT", surface="pattern", api="search", pattern=b"a+", string=b"zaaa!", subject_kind="bytearray", flags=[]),
    C("v2.byteslike.memoryview-search", "byteslike", "API-BYTESLIKE API-SEARCH API-MATCH-OBJECT", surface="module", api="search", pattern=b"a+", string=b"zaaa!", subject_kind="memoryview", flags=[]),
    C("v2.byteslike.bytearray-match", "byteslike", "API-BYTESLIKE API-MATCH API-MATCH-OBJECT", surface="pattern", api="match", pattern=b"a+", string=b"aaaz", subject_kind="bytearray", flags=[]),
    C("v2.byteslike.memoryview-fullmatch", "byteslike", "API-BYTESLIKE API-FULLMATCH API-MATCH-OBJECT", surface="pattern", api="fullmatch", pattern=b"a+", string=b"aaa", subject_kind="memoryview", flags=[]),
    C("v2.byteslike.bytearray-findall", "byteslike", "API-BYTESLIKE API-FINDALL", surface="pattern", api="findall", pattern=b"(a)?b", string=b"b ab bb", subject_kind="bytearray", flags=[]),
    C("v2.byteslike.memoryview-finditer", "byteslike", "API-BYTESLIKE API-FINDITER API-MATCH-OBJECT", surface="module", api="finditer", pattern=b"(?P<x>a+)", string=b"zaa a", subject_kind="memoryview", flags=[]),
    C("v2.byteslike.memoryview-split", "byteslike", "API-BYTESLIKE API-SPLIT", surface="pattern", api="split", pattern=b"(,)", string=b"a,b,c", subject_kind="memoryview", flags=[], maxsplit=0),
    C("v2.byteslike.bytearray-sub", "byteslike", "API-BYTESLIKE API-SUB", surface="pattern", api="sub", pattern=b"a", string=b"aba", subject_kind="bytearray", repl=b"X", replacement_kind="bytes", flags=[], count=0),
    C("v2.byteslike.memoryview-subn", "byteslike", "API-BYTESLIKE API-SUBN", surface="module", api="subn", pattern=b"a", string=b"aba", subject_kind="memoryview", repl=b"X", replacement_kind="bytes", flags=[], count=1),
    C("v2.byteslike.bytearray-replacement", "byteslike", "API-BYTESLIKE API-SUB", surface="pattern", api="sub", pattern=b"a", string=b"aba", subject_kind="bytes", repl=b"X", replacement_kind="bytearray", flags=[], count=0),
    C("v2.byteslike.memoryview-replacement", "byteslike", "API-BYTESLIKE API-SUBN", surface="pattern", api="subn", pattern=b"a", string=b"aba", subject_kind="bytes", repl=b"X", replacement_kind="memoryview", flags=[], count=0),
    C("v2.byteslike.escape-bytearray", "byteslike-escape", "API-BYTESLIKE API-ESCAPE", value=b"a+b [x]", value_kind="bytearray"),
    C("v2.byteslike.escape-memoryview", "byteslike-escape", "API-BYTESLIKE API-ESCAPE", value=b"a+b [x]", value_kind="memoryview"),
    C("v2.repr.pattern-flags", "representation", "API-REPRESENTATION API-PATTERN API-FLAGS", target="pattern", pattern="(?i)a+", flags=["M"]),
    C("v2.repr.pattern-bytes", "representation", "API-REPRESENTATION API-PATTERN", target="pattern", pattern=b"a+", flags=[]),
    C("v2.repr.match-text", "representation", "API-REPRESENTATION API-MATCH-OBJECT", target="match", pattern="a+", string="zaa", flags=[]),
    C("v2.repr.match-bytes", "representation", "API-REPRESENTATION API-MATCH-OBJECT", target="match", pattern=b"a+", string=b"zaa", flags=[]),
    C("v2.repr.match-long", "representation", "API-REPRESENTATION API-MATCH-OBJECT", target="match", pattern="a+", string="z" + "a" * 80, flags=[]),
    C("v2.pattern.equality-hash", "pattern-equality", "API-PATTERN API-COMPILE", pattern="(?i)a+", flags=["M"]),
    C("v2.match.copy", "match-copy", "API-MATCH-COPY API-MATCH-OBJECT", action="copy", pattern="(a)", string="za", flags=[]),
    C("v2.match.deepcopy", "match-copy", "API-MATCH-COPY API-MATCH-OBJECT", action="deepcopy", pattern="(a)", string="za", flags=[]),
    C("v2.match.pickle", "match-copy", "API-MATCH-COPY API-MATCH-OBJECT", action="pickle", pattern="(a)", string="za", flags=[]),
    C("v2.B.empty-search", "call", "S-ANCHOR S-EMPTY API-SEARCH API-MATCH-OBJECT", surface="module", api="search", pattern=r"\B", string="", flags=[]),
    C("v2.B.empty-findall", "call", "S-ANCHOR S-EMPTY API-FINDALL", surface="module", api="findall", pattern=r"\B", string="", flags=[]),
    C("v2.B.empty-split", "call", "S-ANCHOR S-EMPTY API-SPLIT", surface="module", api="split", pattern=r"\B", string="", flags=[], maxsplit=0),
    C("v2.B.empty-sub", "call", "S-ANCHOR S-EMPTY API-SUB", surface="module", api="sub", pattern=r"\B", string="", repl="#", flags=[], count=0),
    C("v2.anchor.final-newline", "call", "S-ANCHOR API-SEARCH API-MATCH-OBJECT", surface="module", api="search", pattern=r"a$", string="a\n", flags=[]),
    C("v2.anchor.window-final-newline", "call", "S-ANCHOR S-WINDOW API-SEARCH API-MATCH-OBJECT", surface="pattern", api="search", pattern=r"a$", string="xa\n!", flags=[], pos=1, endpos=3),
    C("v2.escape.named-unicode", "call", "S-LITERAL S-UNICODE API-SEARCH API-MATCH-OBJECT", surface="module", api="search", pattern=r"\N{SNOWMAN}+", string="x☃☃y", flags=[]),
    C("v2.lookbehind.number-ref", "call", "S-LOOKBEHIND-REF S-LOOKAROUND S-BACKREF API-SEARCH API-MATCH-OBJECT", surface="module", api="search", pattern=r"(a)(?<=\1)b", string="ab", flags=[]),
    C("v2.lookbehind.named-ref", "call", "S-LOOKBEHIND-REF S-LOOKAROUND S-BACKREF API-SEARCH API-MATCH-OBJECT", surface="module", api="search", pattern=r"(?P<x>ab)(?<=(?P=x))c", string="abc", flags=[]),
    C("v2.lookbehind.negative-ref", "call", "S-LOOKBEHIND-REF S-LOOKAROUND S-BACKREF API-SEARCH", surface="module", api="search", pattern=r"(a)(?<!\1)b", string="cb", flags=[]),
    C("v2.error.lookbehind-variable-ref", "error", "S-LOOKBEHIND-REF S-LOOKAROUND E-PATTERN", action="compile", pattern=r"(a+)(?<=\1)b", flags=[]),
    C("v2.error.inline-au", "error", "S-INLINE E-PATTERN", action="compile", pattern=r"(?au:a)", flags=[]),
    C("v2.error.inline-a-u", "error", "S-INLINE E-PATTERN", action="compile", pattern=r"(?a-u:a)", flags=[]),
    C("v2.error.inline-u-a", "error", "S-INLINE E-PATTERN", action="compile", pattern=r"(?u-a:a)", flags=[]),
    C("v2.error.inline-minus-a", "error", "S-INLINE E-PATTERN", action="compile", pattern=r"(?-a:a)", flags=[]),
    C("v2.error.inline-L-str", "error", "S-INLINE E-PATTERN E-TYPE", action="compile", pattern=r"(?L:a)", flags=[]),
    C("v2.error.inline-i-i", "error", "S-INLINE E-PATTERN", action="compile", pattern=r"(?i-i:a)", flags=[]),
    C("v2.error.bytes-unicode-escape", "error", "S-ASCII E-PATTERN", action="compile", pattern=br"\u0041", flags=[]),
    C("v2.error.octal-group", "error", "S-BACKREF E-PATTERN", action="compile", pattern=r"(a)\11", flags=[]),
    C("v2.warning.nested-set", "warning", "E-WARNING S-DOT-CLASS", pattern=r"[[a]", flags=[]),
    C("v2.warning.double-pipe", "warning", "E-WARNING S-DOT-CLASS", pattern=r"[a||b]", flags=[]),
    C("v2.warning.double-tilde", "warning", "E-WARNING S-DOT-CLASS", pattern=r"[a~~b]", flags=[]),
    C("v2.warning.double-minus", "warning", "E-WARNING S-DOT-CLASS", pattern=r"[a-z--]", flags=[]),
    C("v2.deprecation.split-positional", "positional-warning", "E-DEPRECATION API-SPLIT", api="split", pattern=",", string="a,b,c", repl=None, count=1, flags=["I"]),
    C("v2.deprecation.sub-positional", "positional-warning", "E-DEPRECATION API-SUB", api="sub", pattern="a", string="aba", repl="X", count=1, flags=["I"]),
    C("v2.deprecation.subn-positional", "positional-warning", "E-DEPRECATION API-SUBN", api="subn", pattern="a", string="aba", repl="X", count=1, flags=["I"]),
]


def expression(rng, *, byte_mode):
    atoms = [
        "a", "b", "c", "X", "0", "_", r"\.", r"\-", ".", "[abc]", "[^x\\n]", "[a-z0-9_]",
        r"\d", r"\D", r"\s", r"\S", r"\w", r"\W", r"\b", r"\B", "^", "$", r"\A", r"\Z", r"\z",
        "(?:ab|c)", "(?=a)a", "(?!z)[ab]", "(?<=a)b", "(?<!z)c", "(?>ab|a)", "(?i:a)", "(?-i:a)",
        r"(?:([ab])\1)", r"(a)?(?(1)b|c)", "(?:a|ab)", "(?:|a)", "(?:(?=a)a|b)",
    ]
    if not byte_mode:
        atoms.extend([r"\N{SNOWMAN}", "雪", "[İıſK]"])
    quantifiers = ["", "", "?", "*", "+", "{2}", "{0,2}", "{1,4}", "??", "*?", "+?", "{0,2}?", "?+", "*+", "++", "{0,2}+"]
    parts = []
    for _ in range(rng.randrange(1, 6)):
        atom = rng.choice(atoms)
        if atom not in {"^", "$", r"\A", r"\Z", r"\z", r"\b", r"\B"} and not atom.startswith(("(?=", "(?<=", "(?<!")):
            atom += rng.choice(quantifiers)
        parts.append(atom)
    value = "".join(parts)
    if rng.randrange(3) == 0:
        value += "|" + rng.choice(atoms)
    return value


def deep_cases(seed, count, *, byte_mode):
    rng = random.Random(seed)
    apis = ["search", "match", "fullmatch", "findall", "finditer", "split", "sub", "subn"]
    obligations = {"search": "API-SEARCH", "match": "API-MATCH", "fullmatch": "API-FULLMATCH", "findall": "API-FINDALL", "finditer": "API-FINDITER", "split": "API-SPLIT", "sub": "API-SUB", "subn": "API-SUBN"}
    alphabet = "abcXYZ019 _,-.!\n" if byte_mode else "abcXYZ019 _,-.!\näßİıſK٣雪☃\u2003"
    prefix = "v2.deep.bytes" if byte_mode else "v2.deep.str"
    syntax = "S-DEEP-FUZZ S-LITERAL S-DOT-CLASS S-ANCHOR S-QUANTIFIER S-POSSESSIVE S-ALTERNATION S-GROUP S-BACKREF S-CONDITIONAL S-LOOKAROUND S-ATOMIC S-INLINE S-EMPTY S-ASCII" if byte_mode else "S-DEEP-FUZZ S-LITERAL S-DOT-CLASS S-ANCHOR S-QUANTIFIER S-POSSESSIVE S-ALTERNATION S-GROUP S-BACKREF S-CONDITIONAL S-LOOKAROUND S-ATOMIC S-INLINE S-EMPTY S-UNICODE"
    for index in range(count):
        pattern = expression(rng, byte_mode=byte_mode)
        string = "".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 60)))
        if byte_mode:
            pattern, string = pattern.encode("ascii"), string.encode("ascii")
        flags = [name for name in ("I", "M", "S", "A") if rng.randrange(5) == 0]
        api = apis[index % len(apis)]
        surface = "pattern" if index % 2 else "module"
        values = {"surface": surface, "api": api, "pattern": pattern, "string": string, "flags": flags}
        if surface == "pattern" and api in {"search", "match", "fullmatch", "findall", "finditer"} and rng.randrange(3) == 0:
            values["pos"] = rng.randrange(0, len(string) + 1)
            values["endpos"] = rng.randrange(values["pos"], len(string) + 1)
        if api == "split":
            values["maxsplit"] = rng.randrange(0, 4)
        if api in {"sub", "subn"}:
            values["repl"] = {"callable": "bracket_upper"} if index % 3 == 0 else (b"#" if byte_mode else "#")
            values["count"] = rng.randrange(0, 4)
        extra = " API-MATCH-OBJECT" if api in {"search", "match", "fullmatch", "finditer"} else ""
        extra += " S-WINDOW" if "pos" in values else ""
        yield C(f"{prefix}.{index:04d}", "call", f"{obligations[api]} {syntax}{extra}", **values)


def cases():
    return [*v1.cases(), *EXTRA_CASES, *deep_cases(SEEDS["deep_str"], 4096, byte_mode=False), *deep_cases(SEEDS["deep_bytes"], 2048, byte_mode=True)]
