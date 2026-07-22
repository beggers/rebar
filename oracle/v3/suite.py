"""Large, deterministic CPython 3.14.6 re correctness holdout."""

import importlib.util
import random
from pathlib import Path


V2_PATH = Path(__file__).resolve().parents[1] / "v2" / "suite.py"
spec = importlib.util.spec_from_file_location("rebar_oracle_v2_parent", V2_PATH)
v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)

SEEDS = {
    **v2.SEEDS,
    "hold_deep_text": 2026072901,
    "hold_deep_bytes": 2026072902,
    "hold_real_text": 2026072903,
    "hold_real_bytes": 2026072904,
    "hold_scanner": 2026072905,
    "hold_properties": 2026072906,
    "hold_invalid_patterns": 2026072907,
    "hold_invalid_templates": 2026072908,
}

OBLIGATIONS = {
    **v2.OBLIGATIONS,
    "API-HOLDOUT": "balanced unseen module/compiled API, input, and flag combinations",
    "API-SCANNER-SEQUENCE": "mixed scanner search/match sequences and window behavior",
    "API-BUFFER-MUTATION": "observable bytearray/memoryview mutation between calls",
    "E-HOLDOUT": "larger unseen invalid-pattern and invalid-template matrix",
    "S-REAL-WORLD": "logs, URLs, identifiers, configuration, markup, and text-cleanup patterns",
    "S-STRESS-HOLDOUT": "deeper unseen syntax, input, and cross-API property combinations",
}

HOLDOUT_COUNTS = {
    "deep-text": 16384,
    "deep-bytes": 8192,
    "real-text": 4096,
    "real-bytes": 2048,
    "scanner": 1024,
    "properties": 2048,
    "invalid-pattern": 1024,
    "invalid-template": 1024,
}

APIS = ("search", "match", "fullmatch", "findall", "finditer", "split", "sub", "subn")
API_OBLIGATION = {
    "search": "API-SEARCH",
    "match": "API-MATCH",
    "fullmatch": "API-FULLMATCH",
    "findall": "API-FINDALL",
    "finditer": "API-FINDITER",
    "split": "API-SPLIT",
    "sub": "API-SUB",
    "subn": "API-SUBN",
}


def C(case_id, kind, obligations, **values):
    return {"id": case_id, "kind": kind, "obligations": obligations.split(), **values}


def syntax_obligations(byte_mode):
    mode = "S-ASCII" if byte_mode else "S-UNICODE"
    return f"S-STRESS-HOLDOUT S-LITERAL S-DOT-CLASS S-ANCHOR S-QUANTIFIER S-POSSESSIVE S-ALTERNATION S-GROUP S-BACKREF S-CONDITIONAL S-LOOKAROUND S-ATOMIC S-INLINE S-EMPTY {mode}"


def expression(rng, *, byte_mode):
    atoms = [
        "a", "b", "c", "X", "0", "_", r"\.", r"\-", ".", "[abc]", r"[^x\n]", "[a-z0-9_]",
        r"\d", r"\D", r"\s", r"\S", r"\w", r"\W", r"\b", r"\B", "^", "$", r"\A", r"\Z", r"\z",
        "(?:ab|c)", "(?:a|ab)", "(?:|a)", "(?=a)a", "(?!z)[ab]", "(?<=a)b", "(?<!z)c", "(?>ab|a)",
        "(?i:ab)", "(?-i:a)", r"(?:([ab])\1)", r"(a)?(?(1)b|c)", r"(?:(?=a)a|b)",
        r"(?:[A-Z]{1,3}_[0-9]{1,3})", r"(?:\w+[-.]\w+)", r"(?:[^,\n]{1,8},)",
    ]
    if not byte_mode:
        atoms.extend([r"\N{SNOWMAN}", "雪", "[İıſK]", r"(?:é|ß|雪)", r"(?:\d+|\w+)"])
    quantifiers = ("", "", "?", "*", "+", "{2}", "{0,2}", "{1,4}", "??", "*?", "+?", "{0,2}?", "?+", "*+", "++", "{0,2}+")
    pieces = []
    for _ in range(rng.randrange(1, 7)):
        atom = rng.choice(atoms)
        zero_width = atom in {"^", "$", r"\A", r"\Z", r"\z", r"\b", r"\B"} or atom.startswith(("(?=", "(?<=", "(?<!"))
        if not zero_width:
            atom += rng.choice(quantifiers)
        pieces.append(atom)
    value = "".join(pieces)
    if rng.randrange(3) == 0:
        value += "|" + rng.choice(atoms)
    return value


def flags_for(rng, *, byte_mode):
    names = [name for name in ("I", "M", "S") if rng.randrange(5) == 0]
    if rng.randrange(6) == 0:
        names.append("A")
    if byte_mode and "A" not in names and rng.randrange(13) == 0:
        names.append("L")
    return names


def subject_for(rng, *, byte_mode, maximum):
    if byte_mode:
        alphabet = b"abcXYZ019 _,-.!:/=\n\t\xff\x80"
        return bytes(rng.choice(alphabet) for _ in range(rng.randrange(maximum + 1)))
    alphabet = "abcXYZ019 _,-.!:/=\n\täßİıſK٣雪☃\u2003\u0301😀"
    return "".join(rng.choice(alphabet) for _ in range(rng.randrange(maximum + 1)))


def call_values(rng, index, *, pattern, string, byte_mode):
    api = APIS[index % len(APIS)]
    surface = "module" if (index // len(APIS)) % 2 == 0 else "pattern"
    values = {"surface": surface, "api": api, "pattern": pattern, "string": string, "flags": flags_for(rng, byte_mode=byte_mode), "subject_kind": ("bytes", "bytearray", "memoryview")[(index // (len(APIS) * 2)) % 3] if byte_mode else "text"}
    if surface == "pattern" and api in {"search", "match", "fullmatch", "findall", "finditer"} and rng.randrange(3) != 0:
        start = rng.randrange(0, len(string) + 1)
        values["pos"] = start
        values["endpos"] = rng.randrange(start, len(string) + 1)
    if api == "split":
        values["maxsplit"] = rng.choice((0, 0, 1, 2, 5, -1))
    if api in {"sub", "subn"}:
        choices = ((b"#", b"<\\g<0>>", b"\\n[\\g<0>]", {"callable": "bracket_upper"}) if byte_mode else ("#", r"<\g<0>>", r"\n[\g<0>]", {"callable": "bracket_upper"}))
        values["repl"] = rng.choice(choices)
        values["count"] = rng.choice((0, 0, 1, 2, 5, -1))
    return values


def deep_cases(seed, count, *, byte_mode):
    rng = random.Random(seed)
    prefix = "v3.hold.deep.bytes" if byte_mode else "v3.hold.deep.text"
    syntax = syntax_obligations(byte_mode)
    for index in range(count):
        pattern = expression(rng, byte_mode=byte_mode)
        string = subject_for(rng, byte_mode=byte_mode, maximum=100)
        if byte_mode:
            pattern = pattern.encode("ascii")
        values = call_values(rng, index, pattern=pattern, string=string, byte_mode=byte_mode)
        api = values["api"]
        extra = " API-MATCH-OBJECT" if api in {"search", "match", "fullmatch", "finditer"} else ""
        extra += " S-WINDOW" if "pos" in values else ""
        extra += " API-BYTESLIKE" if values["subject_kind"] != "text" else ""
        yield C(f"{prefix}.{index:05d}", "hold-call", f"API-HOLDOUT {API_OBLIGATION[api]} {syntax}{extra}", **values)


REAL_PATTERNS = (
    (r"(?P<method>GET|POST|PUT|DELETE) (?P<path>/[A-Za-z0-9_./-]+) HTTP/[0-9.]+", ('GET /api/v1/items HTTP/1.1', 'POST /upload/a_2 HTTP/2.0', 'missing request')),
    (r"(?P<scheme>https?)://(?P<host>[A-Za-z0-9.-]+)(?::(?P<port>[0-9]+))?(?P<path>/[^ ?#]*)?", ('https://example.org:8443/docs/a-b?q=1', 'http://a.test/x', 'no url here')),
    (r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", ('a.one@example.org', 'b+tag@sub.example.net', 'broken@email')),
    (r"(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})[ T](?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2})(?:\.[0-9]+)?Z?", ('2026-07-29T23:14:08.127Z', '2027-01-03 01:02:03', '2026-7-2')),
    (r"v?[0-9]+\.[0-9]+\.[0-9]+(?:-(?:alpha|beta|rc)[0-9]*)?(?:\+[A-Za-z0-9.-]+)?", ('v3.14.6-rc2+linux.x86_64', '1.2.3', 'version unknown')),
    (r"[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}", ('4d3c2b1a-0123-4abc-8def-0123456789ab', 'ABCDEF01-0123-4567-89AB-0123456789AB', 'not-a-uuid')),
    (r"(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})(?:\.(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})){3}", ('192.168.42.7', '255.0.1.42', '999.300.1.2')),
    (r"(?:^|\s)(?:\./|/)?[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+", ('./src/main.py', '/var/log/service/error.log', 'filename-only')),
    (r"^(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>[^#\n]*?)\s*(?:#.*)?$", ('PORT = 8080 # service', 'NAME=alpha beta', '2BAD = value')),
    (r"#[^\n]*$", ('x = 1 # first', '# whole line', 'without comment')),
    (r"^[ \t]+|[ \t]+$", ('  padded  ', '\tsecond\t', 'clean')),
    (r"<(?P<tag>[A-Za-z][A-Za-z0-9]*)\b[^>]*>", ('<main id="x">', '<a href="/docs">', 'plain < text')),
    (r"([\"'])(.*?)\1", ('title="alpha beta"', "name='gamma'", 'unterminated="value')),
    (r",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", ('one,"two,too",three', 'a,b,c', '"a,b"')),
    (r"(?<![A-Za-z])(?:TODO|FIXME|NOTE)(?=[:\s])", ('TODO: repair', 'x FIXME now', 'METHOD')),
    (r"\b(?:true|false|null)\b", ('true false null', 'value=true', 'nullable')),
    (r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\((?P<args>[^()]*)\)", ('render(name, count)', 'f()', 'not a call(')),
    (r"(?P<sign>[-+]?)(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)(?:[eE][-+]?[0-9]+)?", ('-12.5e+3', '.75', 'number: none')),
    (r"(?:^|\s)@[A-Za-z0-9_]{1,24}\b|#[A-Za-z0-9_]{2,32}\b", ('hello @alice #release_2', '#go @x', 'plain words')),
    (r"(?P<left>[A-Za-z0-9_.-]+):(?P<right>[A-Za-z0-9_.-]+)", ('host:443', 'key:value', 'missing delimiter')),
    (r"(?P<q>[\"'])(?P<body>(?:\\.|(?!\1).)*)(?P=q)", ('"quoted \\" value"', "'simple'", 'no quotes')),
    (r"(?<=\bID[:=])(?P<id>[A-Z]{2}[0-9]{2,6})(?=\b)", ('ID:ZX9021', 'ID=AB42', 'id=ab42')),
    (r"(?:^|\n)(?P<level>TRACE|DEBUG|INFO|WARN|ERROR)\s+(?P<message>[^\n]*)", ('INFO ready\nERROR failed', 'DEBUG start', 'ordinary text')),
    (r"(?:\b[A-Z][a-z]+\b)(?:[ -](?:\b[A-Z][a-z]+\b)){0,3}", ('North-East-West', 'Ada Lovelace', 'lower case')),
)


def real_cases(seed, count, *, byte_mode):
    rng = random.Random(seed)
    prefix = "v3.hold.real.bytes" if byte_mode else "v3.hold.real.text"
    syntax = f"S-REAL-WORLD S-STRESS-HOLDOUT S-LITERAL S-DOT-CLASS S-ANCHOR S-QUANTIFIER S-ALTERNATION S-GROUP S-BACKREF S-LOOKAROUND S-EMPTY {'S-ASCII' if byte_mode else 'S-UNICODE'}"
    unicode_samples = (" café 雪 ", " İıſK ", " ٣٣ ", " 😀\u0301 ")
    byte_noise = (b" ", b" \xff ", b" \x80 ", b"\n")
    text_noise = (" ", " -- ", "\n", " :: ")
    for index in range(count):
        pattern, samples = REAL_PATTERNS[index % len(REAL_PATTERNS)]
        sample = rng.choice(samples)
        if byte_mode:
            pattern = pattern.encode("ascii")
            sample = sample.encode("ascii")
            string = rng.choice(byte_noise) + sample + rng.choice(byte_noise)
        else:
            string = rng.choice(text_noise + unicode_samples) + sample + rng.choice(text_noise + unicode_samples)
        values = call_values(rng, index, pattern=pattern, string=string, byte_mode=byte_mode)
        if index % len(REAL_PATTERNS) in {8, 9, 10, 22} and "M" not in values["flags"]:
            values["flags"].append("M")
        api = values["api"]
        extra = " API-MATCH-OBJECT" if api in {"search", "match", "fullmatch", "finditer"} else ""
        extra += " S-WINDOW" if "pos" in values else ""
        extra += " API-BYTESLIKE" if byte_mode else ""
        yield C(f"{prefix}.{index:05d}", "hold-call", f"API-HOLDOUT {API_OBLIGATION[api]} {syntax}{extra}", **values)


SCANNER_PATTERNS = (
    r"\w+", r"(?P<word>[A-Za-z]+)(?P<num>[0-9]+)?", r"(?:^|\s)[A-Za-z_]+", r"a*", r"|a", r"\B|(?=,)",
    r"(?=(a))", r"(a)?b", r"(?P<x>a)|(b)", r"[A-Za-z]+:[0-9]+", r"(?<![A-Za-z])[A-Z]{2}[0-9]+", r"(?:ab|a)b*",
)


def scanner_cases(seed, count):
    rng = random.Random(seed)
    for index in range(count):
        byte_mode = index % 3 != 0
        pattern = SCANNER_PATTERNS[index % len(SCANNER_PATTERNS)]
        alphabet = b"abXYZ019 ,:_-\n" if byte_mode else "abXYZ019 ,:_-\nä雪İ"
        length = rng.randrange(0, 70)
        string = bytes(rng.choice(alphabet) for _ in range(length)) if byte_mode else "".join(rng.choice(alphabet) for _ in range(length))
        if byte_mode:
            pattern = pattern.encode("ascii")
        subject_kind = "text" if not byte_mode else ("bytes", "bytearray", "memoryview")[index % 3]
        pos = rng.randrange(0, len(string) + 1)
        endpos = rng.randrange(pos, len(string) + 1)
        methods = [rng.choice(("search", "search", "match")) for _ in range(rng.randrange(2, 11))]
        mutations = []
        if subject_kind in {"bytearray", "memoryview"} and string:
            for step in range(len(methods)):
                if rng.randrange(3) == 0:
                    mutations.append({"after": step, "index": rng.randrange(len(string)), "value": rng.choice(b"abXZ19 ,:_-\n")})
        obligations = "API-HOLDOUT API-SCANNER API-SCANNER-SEQUENCE API-MATCH-OBJECT S-STRESS-HOLDOUT S-EMPTY S-WINDOW S-ANCHOR S-GROUP S-LOOKAROUND"
        obligations += " API-BUFFER-MUTATION API-BYTESLIKE S-ASCII" if subject_kind in {"bytearray", "memoryview"} else " S-ASCII" if byte_mode else " S-UNICODE"
        yield C(f"v3.hold.scanner.{index:05d}", "hold-scanner", obligations, pattern=pattern, string=string, subject_kind=subject_kind, flags=flags_for(rng, byte_mode=byte_mode), pos=pos, endpos=endpos, methods=methods, mutations=mutations)


def property_cases(seed, count):
    rng = random.Random(seed)
    for index in range(count):
        byte_mode = index % 3 != 0
        pattern = expression(rng, byte_mode=byte_mode)
        string = subject_for(rng, byte_mode=byte_mode, maximum=70)
        if byte_mode:
            pattern = pattern.encode("ascii")
        subject_kind = "text" if not byte_mode else ("bytes", "bytearray", "memoryview")[index % 3]
        pos = rng.randrange(0, len(string) + 1)
        endpos = rng.randrange(pos, len(string) + 1)
        obligations = "API-HOLDOUT API-COMPILE API-SEARCH API-MATCH API-FULLMATCH API-FINDALL API-FINDITER API-SPLIT API-SUB API-SUBN API-ESCAPE API-SCANNER API-PATTERN API-MATCH-OBJECT S-STRESS-HOLDOUT S-EMPTY S-WINDOW"
        obligations += " API-BYTESLIKE S-ASCII" if byte_mode else " S-UNICODE"
        yield C(f"v3.hold.property.{index:05d}", "hold-property", obligations, pattern=pattern, string=string, subject_kind=subject_kind, flags=flags_for(rng, byte_mode=byte_mode), count=rng.choice((0, 1, 2, 5)), pos=pos, endpos=endpos)


def invalid_pattern_cases(seed, count):
    rng = random.Random(seed)
    forms = (
        lambda tail: r"\q" + tail,
        lambda tail: "[abc" + tail.replace("]", ""),
        lambda tail: "(" + tail,
        lambda tail: "a**" + tail,
        lambda tail: "a{3,1}" + tail,
        lambda tail: "(?P<x>a)(?P<x>b)" + tail,
        lambda tail: r"(a)\2" + tail,
        lambda tail: "(?<=a+)b" + tail,
        lambda tail: "a(?i)b" + tail,
        lambda tail: "(?P<bad-name>a)" + tail,
        lambda tail: "(?P=x)" + tail,
        lambda tail: "(?(99)a|b)" + tail,
        lambda tail: "(?i-i:a)" + tail,
        lambda tail: "(?a-u:a)" + tail,
        lambda tail: r"[\x1]" + tail,
        lambda tail: tail + r"\x1",
    )
    tails = ("", "x", "ab", "|z", "[0-9]", "(?:q)", "(?=a)")
    for index in range(count):
        pattern = forms[index % len(forms)](rng.choice(tails))
        if index % 4 == 0:
            pattern = pattern.encode("ascii")
        yield C(f"v3.hold.invalid-pattern.{index:05d}", "error", "API-HOLDOUT E-HOLDOUT E-PATTERN S-STRESS-HOLDOUT S-LOOKAROUND S-INLINE S-GROUP S-BACKREF S-CONDITIONAL", action="compile", pattern=pattern, flags=[])


def invalid_template_cases(seed, count):
    rng = random.Random(seed)
    templates = (r"\2", r"\9", r"\q", r"\g<missing>", r"\g<2>", r"\g<", r"\g<bad-name>", r"\g<-1>", r"\g<1", "\\", r"\u0041", r"\x41")
    tails = ("", "x", "-tail", r"\n", " value")
    patterns = ("(a)", "(?P<word>a+)", "(a)?b", "(?P<x>a)|(b)")
    for index in range(count):
        byte_mode = index % 3 != 0
        pattern = patterns[index % len(patterns)]
        string = rng.choice(("a", "aa", "b", "", "aba"))
        template = templates[index % len(templates)]
        tail = rng.choice(tails)
        repl = tail + template if template == "\\" else template + tail
        if byte_mode:
            pattern, string, repl = pattern.encode("ascii"), string.encode("ascii"), repl.encode("ascii")
        yield C(f"v3.hold.invalid-template.{index:05d}", "error", "API-HOLDOUT E-HOLDOUT E-TEMPLATE API-SUB S-STRESS-HOLDOUT S-GROUP", action="sub", pattern=pattern, repl=repl, string=string, flags=[])


def cases():
    return [
        *v2.cases(),
        *deep_cases(SEEDS["hold_deep_text"], HOLDOUT_COUNTS["deep-text"], byte_mode=False),
        *deep_cases(SEEDS["hold_deep_bytes"], HOLDOUT_COUNTS["deep-bytes"], byte_mode=True),
        *real_cases(SEEDS["hold_real_text"], HOLDOUT_COUNTS["real-text"], byte_mode=False),
        *real_cases(SEEDS["hold_real_bytes"], HOLDOUT_COUNTS["real-bytes"], byte_mode=True),
        *scanner_cases(SEEDS["hold_scanner"], HOLDOUT_COUNTS["scanner"]),
        *property_cases(SEEDS["hold_properties"], HOLDOUT_COUNTS["properties"]),
        *invalid_pattern_cases(SEEDS["hold_invalid_patterns"], HOLDOUT_COUNTS["invalid-pattern"]),
        *invalid_template_cases(SEEDS["hold_invalid_templates"], HOLDOUT_COUNTS["invalid-template"]),
    ]
