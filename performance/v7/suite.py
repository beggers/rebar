"""Frozen, additive, independently seeded Python ``re`` workload families."""

from __future__ import annotations

import random

from performance.v6.suite import MODULES, cases as parent_cases


TRIALS = 13
WARMUPS = 4
BOOTSTRAPS = 2000
VARIANTS = 64
SEEDS = {"calibration": 1986072311, "holdout": 1986072329}
ORDER_SEED = 1986072301
BOOTSTRAP_SEED = 1986072302
PARENT_CASES_PER_COHORT = 6216


def spec(
    name,
    domain,
    api,
    pattern,
    subject,
    *,
    lifecycle="compiled",
    flags=(),
    repeat=True,
    **extra,
):
    return {
        "name": name,
        "domain": domain,
        "api": api,
        "lifecycle": lifecycle,
        "pattern": pattern,
        "subject": subject,
        "flags": tuple(flags),
        "repeat": repeat,
        "extra": extra,
    }


SPECS = (
    spec("apache-vhost-log", "protocols", "finditer", r'^(?P<host>[a-z0-9.-]+) "(?P<method>GET|POST) (?P<path>/[^ ]*) HTTP/[0-9.]+" (?P<status>[0-9]{3})$', 'api.{word}.test "GET /v1/{other}/{number} HTTP/1.1" 200', flags=("M",)),
    spec("rfc5424-syslog", "protocols", "findall", r'<(?P<priority>[0-9]{1,3})>1 (?P<time>[^ ]+) (?P<host>[^ ]+) (?P<app>[^ ]+) - - - (?P<message>[^\n]+)', '<34>1 2026-07-23T11:12:13Z {word}.test {other} - - - event-{number}'),
    spec("json-escaped-string", "protocols", "finditer", r'"(?P<key>[^"\\]+)"\s*:\s*"(?P<value>(?:\\.|[^"\\])*)"', '"{word}": "path\\\\{other}\\\"{number}"'),
    spec("ndjson-event-fields", "protocols", "findall", r'"(?:event|trace_id|level)"\s*:\s*"([^"\n]+)"', '{"event":"{word}","trace_id":"{other}-{number}","level":"info"}'),
    spec("http-cookie-pairs", "protocols", "scanner", r'(?P<key>[A-Za-z_][A-Za-z0-9_]*)=(?P<value>[A-Za-z0-9_.-]+);?\s*', '{word}={other}-{number}; '),
    spec("percent-query-pairs", "protocols", "findall", r'(?:^|[?&])(?P<key>[A-Za-z_]+)=(?P<value>(?:%[0-9A-Fa-f]{2}|[A-Za-z0-9_.-])*)', '?{word}={other}%20{number}&page=2'),
    spec("jwt-token-segments", "protocols", "search", r'(?<![A-Za-z0-9_-])(?P<head>[A-Za-z0-9_-]{8,})\.(?P<body>[A-Za-z0-9_-]{8,})\.(?P<sig>[A-Za-z0-9_-]{8,})(?![A-Za-z0-9_-])', '{word} eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTYifQ.abcdEFGHijklMNOP {other}-{number}'),
    spec("bracketed-ipv6-host", "protocols", "fullmatch", r'\[(?P<host>[0-9a-fA-F:]+)\]:(?P<port>[0-9]{2,5})', '[2001:0db8:85a3::{number}]:443', repeat=False),

    spec("python-relative-import", "source", "findall", r'(?m)^\s*(?:from\s+(?P<package>[.A-Za-z_][.A-Za-z0-9_]*)\s+import\s+(?P<name>[A-Za-z0-9_, ]+)|import\s+(?P<direct>[.A-Za-z0-9_]+))', 'from {word}.{other} import entry_{number}, value'),
    spec("python-decorator", "source", "match", r'(?m)^\s*@(?P<name>[A-Za-z_][A-Za-z0-9_.]*)(?:\((?P<args>[^\n()]*)\))?', '@{word}.{other}(timeout={number})'),
    spec("rust-attribute", "source", "findall", r'#\[(?P<attribute>[A-Za-z_][A-Za-z0-9_]*)(?:\((?P<args>[^\]]*)\))?\]', '#[derive({word}, {other}, Variant{number})]'),
    spec("rust-use-tree", "source", "search", r'\buse\s+(?P<path>[A-Za-z_][A-Za-z0-9_:]*)(?:::\{(?P<items>[A-Za-z0-9_, ]+)\})?\s*;', 'use {word}::{other}::{value_{number}, item};'),
    spec("js-template-hole", "source", "finditer", r'\$\{\s*(?P<expr>[A-Za-z_$][A-Za-z0-9_$.]*)\s*\}', '${{word}.{other}{number}}'),
    spec("c-preprocessor-line", "source", "findall", r'(?m)^\s*#\s*(?P<kind>include|define|ifdef|ifndef)\s+(?P<value>[^\n]+)', '#define {word}_VALUE {number}'),
    spec("git-unified-hunk", "source", "finditer", r'(?m)^@@ -(?P<old>[0-9]+)(?:,(?P<oldn>[0-9]+))? \+(?P<new>[0-9]+)(?:,(?P<newn>[0-9]+))? @@(?P<context>[^\n]*)$', '@@ -12,4 +18,6 @@ def {word}_{number}'),
    spec("toml-dotted-key", "source", "fullmatch", r'(?P<key>[A-Za-z_][A-Za-z0-9_.-]*)\s*=\s*"(?P<value>(?:\\.|[^"\\])*)"', '{word}.{other}="value-{number}"', repeat=False),

    spec("greek-simple-fold", "unicode", "findall", r'(?i)\b(?:δελτα|ωμεγα|αλφα)\b', 'ΔΕΛΤΑ ΩΜΕΓΑ αλφα {word}-{number}'),
    spec("turkish-simple-fold", "unicode", "finditer", r'(?i)[iI]\w+', 'İstanbul ıstanbul Istanbul {word}-{number}'),
    spec("cyrillic-case-fold", "unicode", "findall", r'(?i)\b(?:слово|пример)\b', 'СЛОВО ПрИмеР слово {word}-{number}'),
    spec("combining-mark-run", "unicode", "finditer", r'\w+[\u0300-\u036f]+', '{word}e\u0301 {other}a\u0308 {number}'),
    spec("astral-emoji-run", "unicode", "findall", r'[\U0001f300-\U0001faff]+', 'report \ud800 😀🌍✨ 🧪🚀 {word}-{number}'),
    spec("cjk-word-boundary", "unicode", "finditer", r'\b\w+\b', '雪山 東京 العربية {word}_{number}'),
    spec("cross-script-digits", "unicode", "findall", r'(?<!\w)\d+(?!\w)', '١٢٣ १२३ １２３ {number}'),
    spec("unicode-space-split", "unicode", "split", r'\s+', '{word}\u2003{other}\u00a0next\u202fend{number}'),

    spec("conjunct-lookahead", "lookaround", "finditer", r'(?=\b[A-Za-z_]+\d+\b)(?=\b.{3,24}\b)[A-Za-z_]+\d+', '{word}{number} {other}17'),
    spec("fixed-width-lookbehind", "lookaround", "findall", r'(?<=id=)[A-Za-z0-9_-]+', 'id={word}-{number} id={other}-2'),
    spec("negative-delimiter-boundary", "lookaround", "finditer", r'(?<![A-Za-z0-9_])@[A-Za-z_][A-Za-z0-9_]*(?![A-Za-z0-9_])', '@{word} x@{other} @{other}_{number}'),
    spec("dual-lookaround-password", "lookaround", "search", r'(?=[A-Za-z0-9_]{6,24}\b)(?=[A-Za-z_]*\d)[A-Za-z0-9_]+', '{word}{number} {other}7'),
    spec("quoted-named-backref", "lookaround", "findall", r'(?P<q>["\'])(?P<body>.*?)(?P=q)', '"{word} {number}" \'{other}\''),
    spec("named-match-surface", "lookaround", "match-surface", r'(?P<key>[A-Za-z_]+)=(?P<value>[A-Za-z0-9_-]+)', '{word}={other}-{number}', repeat=False, expand=r'<\g<key>:\g<value>>'),
    spec("lookahead-empty-steps", "lookaround", "finditer", r'(?=[A-Za-z])|(?<=\d)(?=[:,])', '{word}{number},{other}8:'),
    spec("nested-local-flag", "lookaround", "finditer", r'(?i:[a-z]+)(?-i:[A-Z]{2})', '{word}AB {other}CD {number}'),

    spec("atomic-prefix-guard", "backtracking", "search", r'(?>[A-Za-z]+(?:_[A-Za-z]+)*)=[0-9]+', '{word}_{other}={number}'),
    spec("possessive-digit-run", "backtracking", "search", r'[0-9]++(?:ms|s|%)', '{number}ms 42%'),
    spec("conditional-angle-pair", "backtracking", "fullmatch", r'(?P<open><)?(?P<word>[A-Za-z_][A-Za-z0-9_]*)(?(open)>|:)', '<{word}_{number}>', repeat=False),
    spec("lazy-markup-tag", "backtracking", "finditer", r'<(?P<tag>[A-Za-z]+)\b[^>]*>.*?</(?P=tag)>', '<item key="{word}">{other}-{number}</item>', flags=("S",)),
    spec("bounded-greedy-code", "backtracking", "findall", r'\b[A-Z]{2,5}(?:-[A-Z0-9]{1,6}){1,3}\b', 'AB-X7-RED CD-42 marker-{word}-{number}'),
    spec("overlap-ordered-branches", "backtracking", "finditer", r'\b(?:render|renderer|rendering|rendered|record|recover|remove)\b', 'renderer rendering render record recover {word}-{number}'),
    spec("negative-class-columns", "backtracking", "split", r'[;,](?=(?:[^"\n]*"[^"\n]*")*[^"\n]*$)', '"{word},{other}",{word};end{number}'),
    spec("nullable-branch-cursor", "backtracking", "finditer", r'(?:a?|b?)(?=[:;])|(?=,)', 'a:;,{word}:,b; {number}'),

    spec("binary-highbit-fields", "buffers", "findall", rb'(?P<word>[A-Za-z]+)|(?P<high>[\x80-\xff]+)', b'alpha \x90\xff beta \xe1', subject_kind="bytes"),
    spec("mutable-buffer-captures", "buffers", "finditer", rb'(?P<key>[A-Za-z_]+)=(?P<num>[0-9]+)', b'alpha=12 beta=34', subject_kind="bytearray"),
    spec("readonly-buffer-scanner", "buffers", "scanner", rb'(?P<token>[A-Za-z_]+|[0-9]+|[=;])\s*', b'alpha=12; beta=34;', subject_kind="memoryview"),
    spec("nul-separated-binary", "buffers", "split", rb'\x00+', b'alpha\x00beta\x00\x00gamma', subject_kind="bytes"),
    spec("highbit-negative-bytes", "buffers", "finditer", rb'[^\x00-\x7f]+', b'alpha\xfe\xff beta\x80', subject_kind="memoryview"),
    spec("named-byte-match-surface", "buffers", "match-surface", rb'(?P<name>[a-z]+):(?P<num>[0-9]+)', b'alpha:42', repeat=False, subject_kind="bytearray", expand=rb'<\g<name>-\g<num>>'),
    spec("binary-template-subn", "buffers", "subn", rb'(?P<name>[a-z]+)=(?P<num>[0-9]+)', b'alpha=12 beta=34', subject_kind="bytearray", repl=rb'<\g<name>:\g<num>>', count=2),
    spec("windowed-binary-collect", "buffers", "findall", rb'([a-z]+)([0-9]+)', b'xxalpha12 beta34zz', subject_kind="memoryview", pos=2, endpos=16),

    spec("cold-compile-lookaround", "lifecycle", "compile", r'(?<=id=)(?P<{word}_{number}>[A-Za-z0-9_-]+)(?=\b)', '', lifecycle="cold", repeat=False),
    spec("cold-module-search", "lifecycle", "search", r'\b(?P<word>[A-Za-z]+)-(?P<num>[0-9]+)\b', '{word}-{number}', lifecycle="cold"),
    spec("warm-module-search", "lifecycle", "search", r'\b[A-Za-z]+_[0-9]+\b', '{word}_{number}', lifecycle="module"),
    spec("warm-module-sub", "lifecycle", "sub", r'(?P<word>[A-Za-z]+)', '{word} {other} {number}', lifecycle="module", repl=r'<\g<word>>'),
    spec("warm-module-subn", "lifecycle", "subn", r'(?P<word>[A-Za-z]+)', '{word} {other} {number}', lifecycle="module", repl=r'<\g<word>>', count=2),
    spec("warm-module-finditer", "lifecycle", "finditer", r'[A-Za-z]+|[0-9]+', '{word} {number} {other}', lifecycle="module"),
    spec("warm-module-findall", "lifecycle", "findall", r'([A-Za-z]+)([0-9]+)', '{word}{number} {other}7', lifecycle="module"),
    spec("escape-literal-mixture", "lifecycle", "escape", 'a.b[0] (x)+ # {word}:{number}', None, lifecycle="module", repeat=False),

    spec("long-tail-search-hit", "density", "search", r'END:[A-Z]{2}[0-9]{2}', 'END:AB42 {word}-{number}', repeat=False, pad="hit"),
    spec("long-tail-search-miss", "density", "search", r'END:[A-Z]{2}[0-9]{2}', 'NOT-A-MATCH {word}-{number}', repeat=False, pad="miss"),
    spec("dense-literal-collection", "density", "findall", r'#[A-Za-z]+', '#{word} #{other} #{word} #v{number}'),
    spec("multiline-mixed-windows", "density", "finditer", r'^(?P<name>[A-Za-z_]+):(?P<num>[0-9]+)$', '{word}:{number}', flags=("M",)),
    spec("scanner-dense-stream", "density", "scanner", r'(?P<word>[A-Za-z]+)|(?P<num>[0-9]+)|(?P<mark>[,;])|(?P<space>\s+)', '{word},{number}; {other}'),
    spec("split-optional-captures", "density", "split", r'(,)?;|(:)', '{word},;{other}:last{number}'),
    spec("callable-capture-replace", "density", "sub", r'\b[A-Za-z]+\b', '{word} {other} {number}', repl={"callable": "upper_bracket"}),
    spec("bounded-template-subn", "density", "subn", r'(?P<word>[A-Za-z]+)-(?P<num>[0-9]+)', '{word}-{number} {other}-7', repl=r'<\g<word>:\g<num>>', count=2),
)

FAMILIES = tuple(item["name"] for item in SPECS)
CASES_PER_COHORT = PARENT_CASES_PER_COHORT + len(FAMILIES) * VARIANTS


def render(value, word, other, number):
    if value is None:
        return None
    if isinstance(value, bytes):
        return (
            value.replace(b"alpha", word.encode("ascii"))
            .replace(b"beta", other.encode("ascii"))
            .replace(b"12", str(number).encode("ascii"))
            .replace(b"34", str(number + 11).encode("ascii"))
            + b" "
            + str(number).encode("ascii")
        )
    return (
        value.replace("{word}", word)
        .replace("{other}", other)
        .replace("{number}", str(number))
    )


def generated_case(cohort, family, variant):
    if cohort not in SEEDS:
        raise ValueError(f"unknown broader performance cohort: {cohort}")
    if not isinstance(variant, int) or isinstance(variant, bool) or not 0 <= variant < VARIANTS:
        raise ValueError("broader family variant must be between 0 and 63")
    try:
        index = FAMILIES.index(family)
    except ValueError as error:
        raise ValueError(f"unknown broader performance family: {family}") from error
    item = SPECS[index]
    rng = random.Random(SEEDS[cohort] + index * 1009 + variant * 9181)
    names = (
        ("amber", "cedar", "delta", "ember", "maple", "north")
        if cohort == "holdout"
        else ("acorn", "birch", "copper", "drift", "elm", "fjord")
    )
    alternatives = (
        ("violet", "stable", "remote", "signal", "winter")
        if cohort == "holdout"
        else ("beacon", "direct", "grove", "harbor", "summer")
    )
    word = rng.choice(names)
    other = rng.choice(alternatives)
    number = 2 * (100 + variant * 32 + rng.randrange(32)) + int(cohort == "holdout")
    copies = (1, 2, 3, 4, 8, 12, 16, 24)[variant % 8]
    value = render(item["subject"], word, other, number)
    if item["repeat"] and value:
        separator = b" " if isinstance(value, bytes) else "\n"
        value = separator.join(value for _ in range(copies))
    if item["extra"].get("pad"):
        width = (32, 128, 512, 2048, 8192, 16384, 32768, 65536)[variant // 8]
        value = "x" * width + " " + value
    extras = {
        key: value
        for key, value in item["extra"].items()
        if key != "pad"
    }
    case = {
        "id": (
            f"{'hold' if cohort == 'holdout' else 'cal'}"
            f".broader.{family}.{variant:02d}"
        ),
        "cohort": cohort,
        "category": f"broader-{family}",
        "api": item["api"],
        "lifecycle": item["lifecycle"],
        "pattern": (
            render(item["pattern"], word, other, number)
            if isinstance(item["pattern"], str)
            else item["pattern"]
        ),
        "string": value,
        "ops": max(1, min(128, 96 // copies)),
        "weight": 1,
        "flags": list(item["flags"]),
        **extras,
    }
    if case["api"] == "compile":
        case["ops"] = max(2, 8 // copies)
    if case["api"] == "split":
        case["maxsplit"] = (0, 1, 2, 4, 8)[variant % 5]
    if case["api"] in {"sub", "subn"} and "count" not in case:
        case["count"] = (0, 1, 2, 4)[variant % 4]
    if item["extra"].get("pad"):
        case["ops"] = max(1, min(64, 8192 // width))
    return case


def cases():
    result = list(parent_cases())
    for cohort in ("calibration", "holdout"):
        for family in FAMILIES:
            for variant in range(VARIANTS):
                result.append(generated_case(cohort, family, variant))
    return result
