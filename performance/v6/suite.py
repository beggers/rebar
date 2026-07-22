"""Broader, balanced, deterministic end-to-end performance matrix for Python re."""

import random

from performance.v5.suite import cases as parent_cases


MODULES = ["re", "candidates.ast_candidate", "candidates.vm_candidate", "candidates.rust_candidate", "candidates.zig_candidate"]
TRIALS = 13
WARMUPS = 4
ORDER_SEED = 1985072201
BOOTSTRAP_SEED = 1985072202
BOOTSTRAPS = 2000
VARIANTS = 64
SEEDS = {"calibration": 1985072211, "holdout": 1985072229}
FAMILIES = (
    "request-logs", "error-stack", "http-headers", "html-attributes", "markdown-code", "sql-tokens",
    "config-lines", "shell-vars", "source-comments", "uuid-hash", "version-tags", "money-units",
    "dates-zones", "file-names", "path-mixed-bytes", "csv-split-even", "quote-captures", "email-mixed",
    "unicode-word-lines", "unicode-casefold", "combining-wide", "byte-highbit", "buffer-tokenize",
    "dense-literal-findall", "dense-class-finditer", "boundary-positions", "nullable-positions",
    "lookahead-chain", "lookbehind-chain", "backref-named", "conditionals-nested", "atomic-alternatives",
    "bounded-repeats", "shared-prefix-alternatives", "negative-class", "multiline-anchors", "inline-modes",
    "search-long-hit", "search-long-miss", "match-short", "fullmatch-structured", "module-warm-search",
    "module-warm-sub", "cold-compile", "escape-mixed", "windowed-collect", "scanner-window", "match-access",
)
PARENT_CASES_PER_COHORT = 3144
CASES_PER_COHORT = PARENT_CASES_PER_COHORT + len(FAMILIES) * VARIANTS


def C(case_id, cohort, category, api, lifecycle, pattern, string, ops, **values):
    return {"id": case_id, "cohort": cohort, "category": category, "api": api, "lifecycle": lifecycle, "pattern": pattern, "string": string, "ops": ops, "weight": 1, "flags": values.pop("flags", []), **values}


def generated_case(cohort, family, variant):
    hold = cohort == "holdout"
    family_index = FAMILIES.index(family)
    rng = random.Random(SEEDS[cohort] + family_index * 1009 + variant * 9181)
    copies = (1, 2, 4, 8, 16, 32, 64, 128)[variant % 8]
    width = (64, 256, 1024, 4096, 16384, 65536, 131072, 262144)[(variant // 8) % 8]
    number = 73 + variant * 37 + family_index * 11
    lower = rng.choice(("amber", "cedar", "delta", "ember", "maple", "north", "orbit", "signal") if hold else ("acorn", "beacon", "copper", "drift", "elm", "fjord", "grove", "harbor"))
    other = rng.choice(("violet", "willow", "remote", "stable", "vector", "winter") if hold else ("birch", "direct", "native", "quartz", "summer", "zebra"))
    upper = lower.upper()
    case_id = f"{'hold' if hold else 'cal'}.deeper.{family}.{variant:02d}"
    category = f"deeper-{family}"
    ops = max(2, 128 // copies)

    if family == "request-logs":
        pattern = r'^(?P<host>[A-Za-z0-9.-]+) - - \[(?P<when>[^]]+)\] "(?P<method>GET|POST|PUT|DELETE) (?P<path>/[^ ]*) HTTP/[0-9.]+" (?P<status>[0-9]{3}) (?P<size>[0-9-]+)$'
        lines = [f'{lower}{item}.{other}.example - - [22/Jul/2026:11:{item % 60:02d}:03 +0000] "{"POST" if item % 3 == 0 else "GET"} /{lower}/{number + item}?q={item} HTTP/1.1" {200 + item % 5} {700 + item}' for item in range(copies)]
        if variant % 7 == 0:
            lines.insert(len(lines) // 2, "unrelated line")
        return C(case_id, cohort, category, "finditer", "compiled", pattern, "\n".join(lines), ops, flags=["M"])
    if family == "error-stack":
        pattern = r'^\s*File "(?P<file>[^"\n]+)", line (?P<line>[0-9]+), in (?P<name>[A-Za-z_][A-Za-z0-9_]*)$'
        lines = [f'  File "/srv/{lower}/{other}{item}.py", line {number + item}, in {lower}_{item}' for item in range(copies)]
        return C(case_id, cohort, category, "findall", "compiled", pattern, "Traceback:\n" + "\n".join(lines), ops, flags=["M"])
    if family == "http-headers":
        pattern = r'^(?P<key>[A-Za-z0-9-]+):[ \t]*(?P<value>[^\r\n]*)\r?$'
        value = "\r\n".join(f"X-{upper}-{item}: {other}-{number + item}" for item in range(copies))
        return C(case_id, cohort, category, "finditer", "compiled", pattern, value, ops, flags=["M"])
    if family == "html-attributes":
        pattern = r'(?P<key>[A-Za-z_:][-A-Za-z0-9_:.]*)\s*=\s*(?:"(?P<double>[^"]*)"|\'(?P<single>[^\']*)\'|(?P<bare>[^\s>]+))'
        value = " ".join(f'data-{lower}-{item}="{other} {number + item}" class=\'{lower}_{item}\' enabled=yes' for item in range(copies))
        return C(case_id, cohort, category, "findall", "compiled", pattern, value, ops)
    if family == "markdown-code":
        pattern = r'(?P<fence>```[A-Za-z0-9_-]*\n.*?\n```)|(?P<inline>`[^`\n]+`)|(?P<link>\[[^]\n]+\]\([^ )\n]+\))'
        value = "\n".join(f'`{lower}_{item}` [{other}](/docs/{number + item})\n```py\n{lower} = {item}\n```' for item in range(copies))
        return C(case_id, cohort, category, "finditer", "compiled", pattern, value, max(2, 96 // copies), flags=["S"])
    if family == "sql-tokens":
        pattern = r'(?P<word>[A-Za-z_][A-Za-z0-9_]*)|(?P<number>[0-9]+(?:\.[0-9]+)?)|(?P<string>\'(?:\'\'|[^\'])*\')|(?P<op><=|>=|<>|!=|[(),.*=+/-])'
        value = " ".join(f"SELECT {lower}_{item}, {number + item}.5 FROM {other} WHERE name='{lower}''{item}' AND id>={item};" for item in range(copies))
        return C(case_id, cohort, category, "scanner", "compiled", pattern, value, max(2, 80 // copies))
    if family == "config-lines":
        pattern = r'^\s*(?P<key>[A-Za-z_][A-Za-z0-9_.-]*)\s*=\s*(?P<value>"[^"]*"|\'[^\']*\'|[^#\n]*?)\s*(?:#.*)?$'
        value = "\n".join(f'{lower}.{item} = "{other} {number + item}" # note' for item in range(copies))
        return C(case_id, cohort, category, "findall", "compiled", pattern, value, ops, flags=["M"])
    if family == "shell-vars":
        pattern = r'\$(?P<plain>[A-Za-z_][A-Za-z0-9_]*)|\$\{(?P<braced>[A-Za-z_][A-Za-z0-9_]*)(?::-(?P<default>[^}]*))?\}'
        value = " ".join(f"${upper}_{item} ${{{upper}_{item}:-{other}-{number + item}}}" for item in range(copies))
        return C(case_id, cohort, category, "subn", "compiled", pattern, value, ops, repl=r"<\g<plain>\g<braced>>", count=5 if variant % 7 == 0 else 0)
    if family == "source-comments":
        pattern = r'(?m)^[ \t]*(?://|#)[^\n]*$|/\*.*?\*/'
        value = "\n".join(f"# {other} {item}\n{lower}_{item} = {number + item}; /* note {item} */" for item in range(copies))
        return C(case_id, cohort, category, "sub", "compiled", pattern, value, ops, repl="", flags=["S"])
    if family == "uuid-hash":
        pattern = r'\b(?:[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}|sha(?:1|256):[0-9a-f]{40,64})\b'
        value = " ".join(f"{number + item:08x}-a1b2-4c3d-8e4f-{item + number:012x} sha256:{number + item:064x}" for item in range(copies))
        return C(case_id, cohort, category, "findall", "compiled", pattern, value, ops, flags=["I"])
    if family == "version-tags":
        pattern = r'v?(?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<patch>[0-9]+)(?:-(?P<tag>[A-Za-z0-9.-]+))?(?:\+(?P<meta>[A-Za-z0-9.-]+))?'
        value = f"v{1 + variant % 6}.{number % 50}.{variant}" + (f"-{other}.{variant}+{lower}.{number}" if variant % 2 else "")
        return C(case_id, cohort, category, "fullmatch" if variant % 2 else "match", "compiled", pattern, value, 128)
    if family == "money-units":
        pattern = r'(?<![A-Za-z0-9_])(?:[$€£][0-9]+(?:,[0-9]{3})*(?:\.[0-9]{2})?|[-+]?[0-9]+(?:\.[0-9]+)?(?:ms|s|KB|MB|GiB|%))(?![A-Za-z0-9_])'
        value = " ".join(f"${number + item},{item % 1000:03d}.{item % 100:02d} {1 + item}.5ms {item % 100}%" for item in range(copies))
        return C(case_id, cohort, category, "findall", "compiled", pattern, value, ops, flags=["I"] if variant % 3 == 0 else [])
    if family == "dates-zones":
        pattern = r'(?P<date>[0-9]{4}[-/][0-9]{2}[-/][0-9]{2})[ T](?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2})(?:\.[0-9]{1,6})?(?P<zone>Z|[+-][0-9]{2}:?[0-9]{2})?'
        value = " ".join(f"2026-{1 + item % 12:02d}-{1 + item % 27:02d}T08:{number % 60:02d}:{item % 60:02d}.{item % 1000:03d}+01:00" for item in range(copies))
        return C(case_id, cohort, category, "finditer", "compiled", pattern, value, ops)
    if family == "file-names":
        pattern = r'(?i)(?<![A-Za-z0-9_.-])(?:README|LICENSE|[A-Za-z0-9_.-]+\.(?:py|rs|zig|c|h|json|ya?ml|md|txt))(?![A-Za-z0-9_.-])'
        value = " ".join(f"{lower}_{item}.{('zig' if item % 2 else 'json')} {other}-{item}.md" for item in range(copies))
        return C(case_id, cohort, category, "search" if variant % 4 == 0 else "findall", "compiled", pattern, value, ops)
    if family == "path-mixed-bytes":
        pattern = rb'(?:[A-Za-z]:\\|/|\.{1,2}/)?[A-Za-z0-9_.-]+(?:(?:/|\\)[A-Za-z0-9_.-]+)+'
        separator = "\\" if variant % 2 else "/"
        root = "C:\\" if variant % 2 else "../"
        value = b" ".join(f"{root}{lower}{separator}{other}{separator}{number + item}.bin".encode("ascii") for item in range(copies)) + b" \xff"
        return C(case_id, cohort, category, "finditer", "compiled", pattern, value, ops, subject_kind=("bytes", "bytearray", "memoryview")[variant % 3])
    if family == "csv-split-even":
        separator = ";" if variant % 2 else ","
        quote = "'" if variant % 4 >= 2 else '"'
        escaped = "\\'" if quote == "'" else '\\"'
        pattern = rf'{separator}(?=(?:[^{escaped}]*{escaped}[^{escaped}]*{escaped})*[^{escaped}]*$)'
        value = separator.join(f"{quote}{lower}{separator}{other} {item}{quote}" if item % 2 else f"{lower}_{number + item}" for item in range(copies * 2))
        return C(case_id, cohort, category, "split", "compiled", pattern, value, max(2, 96 // copies), maxsplit=6 if variant % 9 == 0 else 0)
    if family == "quote-captures":
        pattern = r'(["\'])(.*?)\1'
        value = " ".join(f'"{lower} {item}"' if item % 2 else f"'{other} {number + item}'" for item in range(copies * 2))
        return C(case_id, cohort, category, "findall", "compiled", pattern, value, max(2, 96 // copies), flags=["S"] if variant % 5 == 0 else [])
    if family == "email-mixed":
        pattern = r'(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![A-Za-z0-9._%+-])'
        value = " ".join(f"<{lower}.{item}+{other}@mail{item % 7}.example.org>" for item in range(copies))
        return C(case_id, cohort, category, "findall", "compiled", pattern, value, max(2, 96 // copies))
    if family == "unicode-word-lines":
        pattern = r'(?m)^\s*(?P<word>\w+(?:[’\'-]\w+)*)\s+(?P<num>\d+)\s*$'
        value = "\n".join(f"{lower} café Straße العربية 雪_{item} {number + item}" for item in range(copies))
        return C(case_id, cohort, category, "finditer", "compiled", pattern, value, ops)
    if family == "unicode-casefold":
        pattern = r'(?i)\b(?:kelvin|straße|istanbul|[a-z]{2,12})\b'
        value = " ".join(f"KELVIN İSTANBUL Straße {upper} ſignal {other.upper()}" for _ in range(copies))
        return C(case_id, cohort, category, "findall", "compiled", pattern, value, ops)
    if family == "combining-wide":
        pattern = r'[A-Za-z]+[\u0300-\u036f]+|[😀-🙏]+|[🌀-🗿]+|[一-鿿]+'
        value = " ".join(f"{lower}e\u0301 雪山 😀🙏 🌀 {other}a\u0308" for _ in range(copies))
        return C(case_id, cohort, category, "finditer", "compiled", pattern, value, ops)
    if family == "byte-highbit":
        pattern = rb'(?P<ascii>[A-Za-z_][A-Za-z0-9_]*)|(?P<hex>0x[0-9A-Fa-f]+)|(?P<high>[\x80-\xff]+)'
        value = b" ".join(f"{lower}_{item} 0x{number + item:x}".encode("ascii") + bytes((0x80 + item % 64, 0xe0 + item % 16)) for item in range(copies))
        return C(case_id, cohort, category, "findall", "compiled", pattern, value, max(2, 96 // copies), subject_kind=("bytes", "bytearray", "memoryview")[variant % 3])
    if family == "buffer-tokenize":
        pattern = rb'(?P<key>[A-Za-z_][A-Za-z0-9_]*)=(?P<value>[A-Za-z0-9_.-]+)|(?P<num>[0-9]+)|(?P<mark>[:,;])'
        value = b" ".join(f"{lower}_{item}={other}-{number + item}; {item},".encode("ascii") for item in range(copies))
        return C(case_id, cohort, category, "scanner", "compiled", pattern, value, max(2, 80 // copies), subject_kind="memoryview" if variant % 2 else "bytearray")
    if family == "dense-literal-findall":
        pattern = f"{lower[:3]}-{other[:3]}"
        value = " ".join(pattern if item % 4 else f"{other}-{item}" for item in range(copies * 4))
        return C(case_id, cohort, category, "findall", "compiled", pattern, value, max(2, 80 // copies))
    if family == "dense-class-finditer":
        pattern = r'[A-Za-z]{1,12}|[0-9]{1,8}|[^A-Za-z0-9\s]'
        value = " ".join(f"{lower}{item}+{other}-{number + item}" for item in range(copies * 2))
        return C(case_id, cohort, category, "finditer", "compiled", pattern, value, max(2, 80 // copies))
    if family == "boundary-positions":
        pattern = r'\b|(?=[,;])|(?<![A-Za-z0-9_])(?=:)'
        value = " ".join(f"{lower}_{item},{other}:{number + item};" for item in range(copies))
        return C(case_id, cohort, category, "finditer", "compiled", pattern, value, max(2, 72 // copies))
    if family == "nullable-positions":
        pattern = r'(?:|[A-Za-z])*?(?=[:;])|\B|(?=,)'
        value = " ".join(f"{lower}{':' if item % 2 else ';'}{other}," for item in range(copies))
        return C(case_id, cohort, category, "finditer", "compiled", pattern, value, max(2, 72 // copies))
    if family == "lookahead-chain":
        pattern = r'(?=[A-Za-z_])(?=[A-Za-z0-9_]{2,24}[:=])(?P<key>[A-Za-z_][A-Za-z0-9_]*)(?=[:=])'
        value = " ".join(f"{lower}_{item}{'=' if item % 2 else ':'}{number + item}" for item in range(copies))
        return C(case_id, cohort, category, "finditer", "compiled", pattern, value, ops)
    if family == "lookbehind-chain":
        pattern = r'(?<![A-Za-z0-9_])(?<!\\)@(?P<name>[A-Za-z_][A-Za-z0-9_]*)(?![A-Za-z0-9_])'
        value = " ".join(f"@{lower}_{item} \\@{other}_{item}" for item in range(copies))
        return C(case_id, cohort, category, "findall", "compiled", pattern, value, ops)
    if family == "backref-named":
        pattern = r'(?P<word>[A-Za-z]{2,10})(?P<sep>[-:/])(?P=word)(?P=sep)(?P<num>[0-9]+)'
        value = " ".join(f"{lower[:6]}{('-' if item % 2 else ':')}{lower[:6]}{('-' if item % 2 else ':')}{number + item}" for item in range(copies))
        return C(case_id, cohort, category, "findall", "compiled", pattern, value, ops, flags=["I"] if variant % 4 == 0 else [])
    if family == "conditionals-nested":
        pattern = r'(?P<open>[<\[])?(?P<word>[A-Za-z][A-Za-z0-9_-]*)(?P<mark>!)?(?(open)[>\]]|:)(?(mark)!|\.)'
        value = " ".join(f"<{lower}_{item}>." if item % 2 else f"{other}_{item}!:!" for item in range(copies))
        return C(case_id, cohort, category, "finditer", "compiled", pattern, value, ops)
    if family == "atomic-alternatives":
        pattern = r'(?>[A-Za-z]+(?:_[A-Za-z]+)*)=[0-9]++|(?:ab|a)++z|x*+y|(?:cat|car|cap)-[0-9]+'
        value = " ".join(f"{lower}_{other}={number + item} cat-{item} xxxy" for item in range(copies))
        return C(case_id, cohort, category, "findall", "compiled", pattern, value, ops)
    if family == "bounded-repeats":
        pattern = r'(?P<code>[A-Z]{2,5})(?:[-_](?P<part>[A-Z0-9]{1,6})){1,4}:(?P<num>[0-9]{2,7})'
        value = " ".join(f"{upper[:4]}-{other[:3].upper()}_{item % 1000:03d}:{number + item}" for item in range(copies))
        return C(case_id, cohort, category, "finditer", "compiled", pattern, value, ops)
    if family == "shared-prefix-alternatives":
        words = ("read", "reader", "reading", "ready", "reason", "record", "recover", "reduce", "remove", "remote", "render", "repair", "repeat", "report", "request", "reset")
        pattern = r'(?:' + "|".join(words) + r')(?:[-_][0-9]{1,6})?'
        value = " ".join(f"{words[(item + variant) % len(words)]}-{number + item}" for item in range(copies))
        return C(case_id, cohort, category, "findall", "compiled", pattern, value, ops, flags=["I"] if variant % 4 == 0 else [])
    if family == "negative-class":
        pattern = r'(?P<key>[^=,;\s]{1,40})=(?P<value>[^,;\n]{0,80})(?=[,;]|$)'
        value = "; ".join(f"{lower}_{item}={other}-{number + item}" for item in range(copies))
        return C(case_id, cohort, category, "findall", "compiled", pattern, value, ops)
    if family == "multiline-anchors":
        pattern = r'^(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?P<value>[^\n]+?)\s*$'
        value = "\n".join(f"{lower}_{item}: {other} {number + item}   " for item in range(copies)) + ("\n" if variant % 3 == 0 else "")
        return C(case_id, cohort, category, "finditer", "compiled", pattern, value, ops, flags=["M"])
    if family == "inline-modes":
        pattern = r'(?i:[a-z_]+)(?-i:[A-Z]{1,6})\s*(?s:.){0,2}:(?a:\w+)'
        value = " ".join(f"{lower}{upper[:3]} :{other}_{item}" for item in range(copies))
        return C(case_id, cohort, category, "findall", "compiled", pattern, value, ops)
    if family == "search-long-hit":
        marker = f"{other.upper()}-{number}-DONE"
        value = ("q" if hold else "x") * width + marker + " tail"
        return C(case_id, cohort, category, "search", "compiled", marker, value, max(1, 24000 // width))
    if family == "search-long-miss":
        marker = f"{other.upper()}-{number}-ABSENT"
        value = ("q" if hold else "x") * width + "ordinary-tail"
        return C(case_id, cohort, category, "search", "compiled", marker, value, max(1, 24000 // width))
    if family == "match-short":
        pattern = r'(?P<key>[A-Za-z_][A-Za-z0-9_]*)=(?P<num>[0-9]+)'
        value = f"{lower}_{variant}={number}" if variant % 3 else f"!{lower}_{variant}={number}"
        return C(case_id, cohort, category, "match", "compiled", pattern, value, 128)
    if family == "fullmatch-structured":
        pattern = r'(?P<scheme>https?)://(?P<host>[A-Za-z0-9.-]+)(?::(?P<port>[0-9]{1,5}))?(?P<path>/[^ ?#]*)?(?:\?(?P<query>[^ #]*))?'
        value = f"https://{lower}.{other}.example:{2000 + number}/docs/{variant}?q={number}" + (" tail" if variant % 5 == 0 else "")
        return C(case_id, cohort, category, "fullmatch", "compiled", pattern, value, 112)
    if family == "module-warm-search":
        pattern = r'[A-Z]{2,8}_[0-9]+'
        value = f"prefix {upper}_{number} suffix" if variant % 5 else f"prefix {lower}_{number} suffix"
        return C(case_id, cohort, category, "search", "module", pattern, value, 128)
    if family == "module-warm-sub":
        pattern = r'(?P<key>[A-Za-z_][A-Za-z0-9_]*)=(?P<value>[A-Za-z0-9_.-]+)'
        value = " ".join(f"{lower}_{item}={other}-{number + item}" for item in range((1, 2, 4, 8)[variant % 4]))
        return C(case_id, cohort, category, "subn", "module", pattern, value, 112, repl=r"[\g<value>: \g<key>]", count=2 if variant % 6 == 0 else 0)
    if family == "cold-compile":
        choices = (
            r'^(?P<scheme>https?)://(?P<host>[A-Za-z0-9.-]+)(?::(?P<port>[0-9]{1,5}))?(?P<path>/[^?#]*)?(?:\?(?P<query>[^#]*))?$',
            r'^(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})[ T](?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2})(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})?$',
            r'^(?P<key>[A-Za-z_][A-Za-z0-9_.-]*)\s*=\s*(?P<value>"[^"]*"|\'[^\']*\'|[^#\n]*?)\s*(?:#.*)?$',
            r'(?P<word>[A-Za-z]{2,10})(?P<sep>[-:/])(?P=word)(?P=sep)[0-9]+',
        )
        return C(case_id, cohort, category, "compile", "cold", choices[variant % len(choices)], None, 4 + variant % 5, flags=["M"] if variant % 4 == 2 else [])
    if family == "escape-mixed":
        pattern = f"{lower}+[{other}] # {number}\\tail café 雪.*?(){{}}|^$"
        if variant % 2:
            pattern = pattern.encode("utf-8")
        return C(case_id, cohort, category, "escape", "module", pattern, None, 128)
    if family == "windowed-collect":
        body = " ".join(f"{lower}_{item}={number + item}" for item in range(copies))
        value = f"SKIP000 ! {body} ! TAIL999"
        pattern = r'(?P<key>[A-Za-z_]+)_(?P<index>[0-9]+)=(?P<num>[0-9]+)'
        api = "finditer" if variant % 2 else "findall"
        return C(case_id, cohort, category, api, "compiled", pattern, value, ops, pos=10, endpos=10 + len(body))
    if family == "scanner-window":
        body = " ".join(f"{lower}_{item}={other}-{number + item}; {item}," for item in range(copies))
        value = f"SKIP000 ! {body} ! TAIL999"
        pattern = r'(?P<key>[A-Za-z_][A-Za-z0-9_]*)=(?P<value>[A-Za-z0-9_.-]+)|(?P<num>[0-9]+)|(?P<mark>[:,;])'
        return C(case_id, cohort, category, "scanner", "compiled", pattern, value, max(2, 80 // copies), pos=10, endpos=10 + len(body))
    if family == "match-access":
        pattern = r'(?P<left>[A-Za-z_]+)-(?P<num>[0-9]+)(?:\.(?P<tail>[A-Za-z]+))?'
        value = f"prefix {lower}_{variant}-{number}" + (f".{other}" if variant % 2 else "") + " suffix"
        return C(case_id, cohort, category, "match-surface", "compiled", pattern, value, 96, expand=r"<\g<num>: \g<left>: \g<tail>>")
    raise RuntimeError(f"unknown deeper performance family: {family}")


def cases():
    result = list(parent_cases())
    for cohort in ("calibration", "holdout"):
        for family in FAMILIES:
            for variant in range(VARIANTS):
                result.append(generated_case(cohort, family, variant))
    return result
