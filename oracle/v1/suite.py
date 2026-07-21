"""Frozen, versioned correctness cases for the CPython 3.14.6 re contract."""

import random

SEEDS = {
    "valid_str": 1511506918,
    "valid_bytes": 1511506919,
    "properties": 1511506920,
    "invalid_patterns": 1511506921,
    "invalid_templates": 1511506922,
}

OBLIGATIONS = {
    "API-EXPORTS": "exact public exports and aliases",
    "API-FLAGS": "flag names, values, and combinations",
    "API-COMPILE": "compile, public cache behavior, and purge",
    "API-SEARCH": "module and pattern search",
    "API-MATCH": "module and pattern match",
    "API-FULLMATCH": "module and pattern fullmatch",
    "API-FINDALL": "findall result shapes",
    "API-FINDITER": "finditer ordering and advancement",
    "API-SPLIT": "split semantics",
    "API-SUB": "sub semantics",
    "API-SUBN": "subn semantics",
    "API-ESCAPE": "escape semantics",
    "API-PATTERN": "compiled-pattern public contract",
    "API-MATCH-OBJECT": "match-object public contract",
    "API-SCANNER": "scanner public contract",
    "S-LITERAL": "ordinary and escaped literals",
    "S-DOT-CLASS": "dot and character classes",
    "S-ANCHOR": "anchors and boundaries",
    "S-QUANTIFIER": "greedy and lazy quantifiers",
    "S-POSSESSIVE": "possessive quantifiers",
    "S-ALTERNATION": "ordered alternation",
    "S-GROUP": "capturing and non-capturing groups",
    "S-BACKREF": "numbered and named backreferences",
    "S-CONDITIONAL": "conditional groups",
    "S-LOOKAROUND": "lookahead and lookbehind",
    "S-ATOMIC": "atomic groups",
    "S-INLINE": "inline flags",
    "S-VERBOSE": "verbose syntax",
    "S-UNICODE": "Unicode classes and folding",
    "S-ASCII": "ASCII semantics",
    "S-LOCALE": "C-locale bytes semantics",
    "S-EMPTY": "zero-width and empty patterns",
    "S-WINDOW": "pos and endpos semantics",
    "E-PATTERN": "invalid-pattern errors",
    "E-TYPE": "invalid public argument types",
    "E-TEMPLATE": "invalid replacement errors",
    "E-WARNING": "ambiguous-set warnings",
    "E-DEBUG": "debug flag diagnostics",
}


def C(case_id, kind, obligations, **values):
    return {"id": case_id, "kind": kind, "obligations": obligations.split(), **values}


STATIC_CASES = [
    C("api.exports", "exports", "API-EXPORTS"),
    C("api.flags", "flags", "API-FLAGS"),
    C("api.cache", "cache", "API-COMPILE API-PATTERN", pattern="ab+", flags=[]),
    C("api.compile.str", "compile", "API-COMPILE API-PATTERN S-LITERAL S-GROUP", pattern="(?P<name>a)(b)?", flags=[]),
    C("api.compile.bytes", "compile", "API-COMPILE API-PATTERN S-LITERAL S-ASCII", pattern=b"(?P<name>a)(b)?", flags=[]),
    C("api.search.module", "call", "API-SEARCH API-MATCH-OBJECT S-LITERAL S-GROUP", surface="module", api="search", pattern="(?P<first>a)(b)?", string="zzabz", flags=[]),
    C("api.search.pattern", "call", "API-SEARCH API-MATCH-OBJECT API-PATTERN S-WINDOW", surface="pattern", api="search", pattern="^b|b$", string="abxba", flags=[], pos=1, endpos=4),
    C("api.match.module", "call", "API-MATCH API-MATCH-OBJECT", surface="module", api="match", pattern="a+", string="aaab", flags=[]),
    C("api.match.pattern", "call", "API-MATCH API-MATCH-OBJECT S-WINDOW", surface="pattern", api="match", pattern="a+", string="zzaaab", flags=[], pos=2, endpos=5),
    C("api.fullmatch.module", "call", "API-FULLMATCH API-MATCH-OBJECT S-QUANTIFIER", surface="module", api="fullmatch", pattern="a+b?", string="aaab", flags=[]),
    C("api.fullmatch.pattern.fail", "call", "API-FULLMATCH S-WINDOW", surface="pattern", api="fullmatch", pattern="a+", string="zaaab", flags=[], pos=1, endpos=5),
    C("api.findall.zero", "call", "API-FINDALL S-QUANTIFIER", surface="module", api="findall", pattern="a+", string="baa caaa", flags=[]),
    C("api.findall.one", "call", "API-FINDALL S-GROUP", surface="pattern", api="findall", pattern="(a+)(?:b)?", string="a ab aaab", flags=[]),
    C("api.findall.many", "call", "API-FINDALL S-GROUP", surface="module", api="findall", pattern="(a)?(b)", string="b ab bb", flags=[]),
    C("api.finditer.empty", "call", "API-FINDITER API-MATCH-OBJECT S-EMPTY", surface="module", api="finditer", pattern="x*", string="abxd", flags=[]),
    C("api.finditer.window", "call", "API-FINDITER API-MATCH-OBJECT S-WINDOW", surface="pattern", api="finditer", pattern="(?P<w>\\w+)", string="one two three", flags=[], pos=4, endpos=12),
    C("api.split.capture", "call", "API-SPLIT S-GROUP", surface="module", api="split", pattern="([,:])", string="a,b:c", flags=[]),
    C("api.split.max", "call", "API-SPLIT", surface="pattern", api="split", pattern="[, ]+", string="a, b, c, d", flags=[], maxsplit=2),
    C("api.split.empty", "call", "API-SPLIT S-EMPTY S-ANCHOR", surface="module", api="split", pattern="\\b", string="Words, words.", flags=[]),
    C("api.sub.number", "call", "API-SUB API-MATCH-OBJECT S-GROUP", surface="module", api="sub", pattern="(\\w+)-(\\d+)", repl="\\2:\\1", string="ab-12 cd-3", flags=[]),
    C("api.sub.named", "call", "API-SUB S-GROUP", surface="pattern", api="sub", pattern="(?P<word>[a-z]+)(?P<num>\\d+)?", repl="<\\g<num>|\\g<word>>", string="ab12 cd", flags=[]),
    C("api.sub.callable", "call", "API-SUB API-MATCH-OBJECT", surface="module", api="sub", pattern="[a-z]+", repl={"callable": "bracket_upper"}, string="ab 12 cd", flags=[], count=1),
    C("api.sub.bytes", "call", "API-SUB S-ASCII", surface="module", api="sub", pattern=b"([a-z]+)-(\\d+)", repl=b"\\2:\\1", string=b"ab-12 cd-3", flags=[]),
    C("api.subn", "call", "API-SUBN API-SUB", surface="pattern", api="subn", pattern="a", repl="x", string="banana", flags=[], count=2),
    C("api.escape.str", "escape", "API-ESCAPE S-LITERAL", value="a b.c+[x]-(y){z}?^$|\\~!@#%&,:;<>/='\"_"),
    C("api.escape.bytes", "escape", "API-ESCAPE S-LITERAL S-ASCII", value=b"a b.c+[x]-(y){z}?^$|\\~!@#%&,:;<>/='\"_\xff"),
    C("api.scanner.search", "scanner", "API-SCANNER API-MATCH-OBJECT S-EMPTY", pattern="x*", string="abxd", flags=[], method="search", calls=7),
    C("api.scanner.match", "scanner", "API-SCANNER API-MATCH-OBJECT", pattern="(?:ab|a)", string="abaX", flags=[], method="match", calls=4),
    C("api.pattern.roundtrip", "roundtrip", "API-PATTERN API-COMPILE S-GROUP", pattern="(?P<a>a+)(b)?", flags=["I"]),
    C("syntax.literal.unicode", "call", "S-LITERAL S-UNICODE API-SEARCH API-MATCH-OBJECT", surface="module", api="search", pattern="café\\+雪", string="--café+雪--", flags=[]),
    C("syntax.dot.default", "call", "S-DOT-CLASS API-FINDALL", surface="module", api="findall", pattern="a.b", string="a-b a\nb", flags=[]),
    C("syntax.dot.dotall", "call", "S-DOT-CLASS S-INLINE API-FINDALL", surface="pattern", api="findall", pattern="(?s:a.b)", string="a-b a\nb", flags=[]),
    C("syntax.class.ranges", "call", "S-DOT-CLASS API-FINDALL", surface="module", api="findall", pattern="[^a-c\\-][a-c\\-]", string="Za !- xq", flags=[]),
    C("syntax.class.escapes", "call", "S-DOT-CLASS S-ASCII API-FINDALL", surface="module", api="findall", pattern="[\\d\\s\\w\\x21\\101]+", string="!A_ 19-?", flags=["A"]),
    C("syntax.anchor.caret-dollar", "call", "S-ANCHOR API-FINDITER API-MATCH-OBJECT", surface="module", api="finditer", pattern="^.$", string="a\nb\n", flags=["M"]),
    C("syntax.anchor.absolute", "call", "S-ANCHOR API-SEARCH", surface="pattern", api="search", pattern="\\Aab\\Z", string="ab\n", flags=[]),
    C("syntax.anchor.z", "call", "S-ANCHOR API-FULLMATCH", surface="module", api="fullmatch", pattern="ab\\z", string="ab", flags=[]),
    C("syntax.anchor.boundary", "call", "S-ANCHOR S-UNICODE API-FINDALL", surface="module", api="findall", pattern="\\b\\w+\\b|\\B!\\B", string="é!x --_--", flags=[]),
    C("syntax.quant.greedy", "call", "S-QUANTIFIER API-SEARCH API-MATCH-OBJECT", surface="module", api="search", pattern="a{2,4}a?", string="aaaaaa", flags=[]),
    C("syntax.quant.lazy", "call", "S-QUANTIFIER API-SEARCH API-MATCH-OBJECT", surface="module", api="search", pattern="a{2,4}?a??", string="aaaaaa", flags=[]),
    C("syntax.quant.open", "call", "S-QUANTIFIER API-FINDALL", surface="module", api="findall", pattern="ba{,2}|ca{2,}", string="b ba baa baaa ca caa caaaa", flags=[]),
    C("syntax.possessive.star", "call", "S-POSSESSIVE API-SEARCH", surface="module", api="search", pattern="a*+a", string="aaaa", flags=[]),
    C("syntax.possessive.bounds", "call", "S-POSSESSIVE API-SEARCH", surface="module", api="search", pattern="a{2,4}+aa", string="aaaaa", flags=[]),
    C("syntax.alternation.order", "call", "S-ALTERNATION API-SEARCH API-MATCH-OBJECT", surface="module", api="search", pattern="a|ab", string="ab", flags=[]),
    C("syntax.group.nested", "call", "S-GROUP API-SEARCH API-MATCH-OBJECT", surface="module", api="search", pattern="((a)(?:b(c))?)(?P<n>d)?", string="abcd", flags=[]),
    C("syntax.backref.number", "call", "S-BACKREF S-GROUP API-SEARCH API-MATCH-OBJECT", surface="module", api="search", pattern="([ab]+)-\\1", string="xx aba-aba yy", flags=[]),
    C("syntax.backref.name", "call", "S-BACKREF S-GROUP API-SEARCH API-MATCH-OBJECT", surface="module", api="search", pattern="(?P<q>['\"])(?P<body>.*?)((?P=q))", string="x 'ab' y", flags=[]),
    C("syntax.conditional.number", "call", "S-CONDITIONAL S-GROUP API-FINDALL", surface="module", api="findall", pattern="(<)?(\\w+@\\w+(?:\\.\\w+)+)(?(1)>|$)", string="<u@x.io> u@x.io bad@x.io>", flags=[]),
    C("syntax.conditional.name", "call", "S-CONDITIONAL S-GROUP API-FULLMATCH", surface="module", api="fullmatch", pattern="(?P<s>a)?b(?(s)c|d)", string="abc", flags=[]),
    C("syntax.lookahead", "call", "S-LOOKAROUND API-FINDALL", surface="module", api="findall", pattern="\\w+(?=,)|\\w+(?![\\w,])", string="one,two three", flags=[]),
    C("syntax.lookbehind", "call", "S-LOOKAROUND API-FINDALL", surface="module", api="findall", pattern="(?<=-)[a-z]+|(?<!-)\\d+", string="-word 42 -17", flags=[]),
    C("syntax.atomic", "call", "S-ATOMIC API-SEARCH", surface="module", api="search", pattern="(?>a*)a", string="aaaa", flags=[]),
    C("syntax.inline.global", "call", "S-INLINE API-FINDALL", surface="module", api="findall", pattern="(?im)^abc$", string="ABC\nabc\nxabc", flags=[]),
    C("syntax.inline.scoped", "call", "S-INLINE API-FULLMATCH", surface="module", api="fullmatch", pattern="(?i:ab)(?-i:cd)", string="ABcd", flags=[]),
    C("syntax.verbose", "call", "S-VERBOSE S-INLINE API-SEARCH API-MATCH-OBJECT", surface="module", api="search", pattern="(?x) (?P<a> a+ ) \\  # a literal space\n (?P<b>b+) ", string="--aa bbb--", flags=[]),
    C("syntax.unicode.classes", "call", "S-UNICODE S-DOT-CLASS API-FINDALL", surface="module", api="findall", pattern="\\d+|\\s+|\\w+", string="Aé_٣ \u2003雪-!", flags=[]),
    C("syntax.unicode.case", "call", "S-UNICODE API-FINDALL", surface="module", api="findall", pattern="[a-z]+", string="A İ ı ſ K é", flags=["I"]),
    C("syntax.ascii.case", "call", "S-ASCII API-FINDALL", surface="module", api="findall", pattern="[a-z]+|\\w+", string="A İ ı ſ K é_4", flags=["I", "A"]),
    C("syntax.bytes", "call", "S-ASCII S-LITERAL S-DOT-CLASS API-FINDITER API-MATCH-OBJECT", surface="module", api="finditer", pattern=b"(?P<w>\\w+)|(?P<hi>[\\x80-\\xff]+)", string=b"A_9 \xff\xe9!", flags=[]),
    C("syntax.locale", "call", "S-LOCALE S-ASCII API-FINDALL", surface="module", api="findall", pattern=b"\\b\\w+\\b", string=b"Ab_9 \xe9 x", flags=["L"]),
    C("syntax.empty.pattern", "call", "S-EMPTY API-FINDITER API-MATCH-OBJECT", surface="module", api="finditer", pattern="", string="ab", flags=[]),
    C("syntax.empty.alternation", "call", "S-EMPTY S-ALTERNATION API-FINDITER API-MATCH-OBJECT", surface="module", api="finditer", pattern="|a", string="a", flags=[]),
    C("syntax.window.anchor", "call", "S-WINDOW S-ANCHOR API-SEARCH API-MATCH-OBJECT", surface="pattern", api="search", pattern="^b|c$", string="ab\ncd", flags=["M"], pos=1, endpos=4),
    C("error.pattern.escape", "error", "E-PATTERN", action="compile", pattern="\\q", flags=[]),
    C("error.pattern.class", "error", "E-PATTERN", action="compile", pattern="[abc", flags=[]),
    C("error.pattern.repeat", "error", "E-PATTERN", action="compile", pattern="a**", flags=[]),
    C("error.pattern.group", "error", "E-PATTERN", action="compile", pattern="(?P<x>a)(?P<x>b)", flags=[]),
    C("error.pattern.ref", "error", "E-PATTERN", action="compile", pattern="(a)\\2", flags=[]),
    C("error.pattern.lookbehind", "error", "E-PATTERN S-LOOKAROUND", action="compile", pattern="(?<=a+)b", flags=[]),
    C("error.pattern.flags", "error", "E-PATTERN S-INLINE", action="compile", pattern="a(?i)b", flags=[]),
    C("error.pattern.bytes-name", "error", "E-PATTERN S-ASCII", action="compile", pattern=b"(?P<\xff>a)", flags=[]),
    C("error.type.mixed-search", "error", "E-TYPE", action="search", pattern="a", string=b"a", flags=[]),
    C("error.type.mixed-sub", "error", "E-TYPE", action="sub", pattern=b"a", repl="x", string=b"a", flags=[]),
    C("error.type.locale-str", "error", "E-TYPE S-LOCALE", action="compile", pattern="a", flags=["L"]),
    C("error.type.unicode-bytes", "error", "E-TYPE S-UNICODE", action="compile", pattern=b"a", flags=["U"]),
    C("error.template.group", "error", "E-TEMPLATE", action="sub", pattern="(a)", repl="\\2", string="a", flags=[]),
    C("error.template.name", "error", "E-TEMPLATE", action="sub", pattern="(a)", repl="\\g<missing>", string="a", flags=[]),
    C("error.template.escape", "error", "E-TEMPLATE", action="sub", pattern="a", repl="\\q", string="a", flags=[]),
    C("warning.ambiguous-set", "warning", "E-WARNING S-DOT-CLASS", pattern="[a&&b]", flags=[]),
    C("debug.output", "debug", "E-DEBUG API-FLAGS", pattern="(?P<a>a+)|b", flags=["DEBUG"]),
]


def subject(rng, *, byte_mode):
    alphabet = "abcXYZ019 _,-.!\n" if byte_mode else "abcXYZ019 _,-.!\näßİıſK٣雪\u2003"
    value = "".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 30)))
    return value.encode("ascii") if byte_mode else value


def expression(rng, depth=0):
    atoms = ["a", "b", "c", "X", "0", "_", "\\.", "\\-", ".", "[abc]", "[^x\\n]", "[a-z0-9_]", "\\d", "\\D", "\\s", "\\S", "\\w", "\\W", "\\b", "\\B", "^", "$", "\\A", "\\Z", "(?:ab|c)", "(?=a)a", "(?!z)[ab]", "(?<=a)b", "(?<!z)c", "(?>ab|a)"]
    quantifiers = ["", "", "?", "*", "+", "{2}", "{0,2}", "{1,3}", "??", "*?", "+?", "{0,2}?", "?+", "*+", "++", "{0,2}+"]
    pieces = []
    for _ in range(rng.randrange(1, 5)):
        atom = rng.choice(atoms)
        if depth < 1 and rng.randrange(7) == 0:
            atom = "(" + expression(rng, depth + 1) + ")"
        if atom not in {"^", "$", "\\A", "\\Z", "\\b", "\\B"} and not atom.startswith("(?=") and not atom.startswith("(?<=") and not atom.startswith("(?<!"):
            atom += rng.choice(quantifiers)
        pieces.append(atom)
    result = "".join(pieces)
    if depth == 0 and rng.randrange(4) == 0:
        result += "|" + "".join(rng.choice(["a", "b", "[0-9]", "\\w", "(?:ab|c)"]) for _ in range(rng.randrange(1, 4)))
    return result


def generated_valid(seed, count, *, byte_mode):
    rng = random.Random(seed)
    apis = ["search", "match", "fullmatch", "findall", "finditer", "split", "sub", "subn"]
    api_obligation = {"search": "API-SEARCH", "match": "API-MATCH", "fullmatch": "API-FULLMATCH", "findall": "API-FINDALL", "finditer": "API-FINDITER", "split": "API-SPLIT", "sub": "API-SUB", "subn": "API-SUBN"}
    prefix = "fuzz.bytes" if byte_mode else "fuzz.str"
    syntax = "S-LITERAL S-DOT-CLASS S-ANCHOR S-QUANTIFIER S-POSSESSIVE S-ALTERNATION S-GROUP S-LOOKAROUND S-ATOMIC S-EMPTY S-ASCII" if byte_mode else "S-LITERAL S-DOT-CLASS S-ANCHOR S-QUANTIFIER S-POSSESSIVE S-ALTERNATION S-GROUP S-LOOKAROUND S-ATOMIC S-EMPTY S-UNICODE"
    for index in range(count):
        pattern = expression(rng)
        string = subject(rng, byte_mode=byte_mode)
        if byte_mode:
            pattern = pattern.encode("ascii")
        api = apis[index % len(apis)]
        flags = [name for name in ("I", "M", "S") if rng.randrange(4) == 0]
        if not byte_mode and rng.randrange(4) == 0:
            flags.append("A")
        surface = "pattern" if index % 2 else "module"
        values = {"surface": surface, "api": api, "pattern": pattern, "string": string, "flags": flags}
        if surface == "pattern" and api in {"search", "match", "fullmatch", "findall", "finditer"} and rng.randrange(3) == 0:
            start = rng.randrange(0, len(string) + 1)
            values["pos"] = start
            values["endpos"] = rng.randrange(start, len(string) + 1)
        if api == "split":
            values["maxsplit"] = rng.randrange(0, 4)
        if api in {"sub", "subn"}:
            values["repl"] = {"callable": "bracket_upper"} if index % 3 == 0 else (b"#" if byte_mode else "#")
            values["count"] = rng.randrange(0, 4)
        extra = " API-MATCH-OBJECT" if api in {"search", "match", "fullmatch", "finditer"} else ""
        extra += " S-WINDOW" if "pos" in values else ""
        yield C(f"{prefix}.{index:04d}", "call", f"{api_obligation[api]} {syntax}{extra}", **values)


def generated_properties(seed, count):
    rng = random.Random(seed)
    for index in range(count):
        byte_mode = index % 3 == 0
        pattern = expression(rng)
        string = subject(rng, byte_mode=byte_mode)
        if byte_mode:
            pattern = pattern.encode("ascii")
        flags = [name for name in ("I", "M", "S") if rng.randrange(4) == 0]
        if not byte_mode and rng.randrange(5) == 0:
            flags.append("A")
        syntax = "S-ASCII" if byte_mode or "A" in flags else "S-UNICODE"
        yield C(f"property.{index:04d}", "property", f"API-COMPILE API-SEARCH API-MATCH API-FULLMATCH API-FINDALL API-FINDITER API-SPLIT API-SUB API-SUBN API-ESCAPE API-PATTERN API-MATCH-OBJECT S-EMPTY {syntax}", pattern=pattern, string=string, flags=flags, count=rng.randrange(0, 4))


def generated_invalid_patterns(seed, count):
    rng = random.Random(seed)
    forms = [
        lambda tail: "\\q" + tail,
        lambda tail: "[abc" + tail.replace("]", ""),
        lambda tail: "(" + tail,
        lambda tail: "a**" + tail,
        lambda tail: "a{3,1}" + tail,
        lambda tail: "(?P<x>a)(?P<x>b)" + tail,
        lambda tail: "(a)\\2" + tail,
        lambda tail: "(?<=a+)b" + tail,
        lambda tail: "a(?i)b" + tail,
        lambda tail: "(?P<bad-name>a)" + tail,
        lambda tail: "(?P=x)" + tail,
        lambda tail: "(?(99)a|b)" + tail,
    ]
    tails = ["", "x", "ab", "|z", "[0-9]", "(?:q)"]
    for index in range(count):
        pattern = forms[index % len(forms)](rng.choice(tails))
        byte_mode = index % 4 == 0
        if byte_mode:
            pattern = pattern.encode("ascii")
        yield C(f"fuzz.invalid-pattern.{index:04d}", "error", "E-PATTERN S-LOOKAROUND S-INLINE S-GROUP S-BACKREF S-CONDITIONAL", action="compile", pattern=pattern, flags=[])


def generated_invalid_templates(seed, count):
    rng = random.Random(seed)
    templates = ["\\2", "\\9", "\\q", "\\g<missing>", "\\g<2>", "\\g<", "\\g<bad-name>", "\\g<-1>"]
    tails = ["", "x", "-tail", "\\n"]
    for index in range(count):
        byte_mode = index % 3 == 0
        repl = templates[index % len(templates)] + rng.choice(tails)
        pattern = "(a)"
        string = "a"
        if byte_mode:
            repl, pattern, string = repl.encode("ascii"), pattern.encode("ascii"), string.encode("ascii")
        yield C(f"fuzz.invalid-template.{index:04d}", "error", "E-TEMPLATE API-SUB S-GROUP", action="sub", pattern=pattern, repl=repl, string=string, flags=[])


def cases():
    return [
        *STATIC_CASES,
        *generated_valid(SEEDS["valid_str"], 768, byte_mode=False),
        *generated_valid(SEEDS["valid_bytes"], 384, byte_mode=True),
        *generated_properties(SEEDS["properties"], 384),
        *generated_invalid_patterns(SEEDS["invalid_patterns"], 240),
        *generated_invalid_templates(SEEDS["invalid_templates"], 192),
    ]
