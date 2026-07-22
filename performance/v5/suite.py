"""Expanded, balanced, deterministic performance matrix for everyday Python re use."""

import random

from performance.v4.suite import cases as parent_cases


MODULES = ["re", "candidates.ast_candidate", "candidates.vm_candidate", "candidates.rust_candidate", "candidates.zig_candidate"]
TRIALS = 13
WARMUPS = 4
ORDER_SEED = 1984073101
BOOTSTRAP_SEED = 1984073102
BOOTSTRAPS = 2000
VARIANTS = 48
SEEDS = {"calibration": 1984073111, "holdout": 1984073129}
FAMILIES = (
    "long-literal", "line-records", "json-fields", "html-tags", "markdown-links", "source-tokens",
    "comment-strip", "url-extract", "email-extract", "ip-version", "dates-numbers", "phone-postcode",
    "path-text", "path-bytes", "csv-fields", "quoted-escapes", "whitespace-clean", "newline-normalize",
    "split-delimiters", "split-captures", "replace-redact", "replace-template", "replace-callback",
    "unicode-words", "unicode-case", "combining-emoji", "ascii-boundary", "byte-buffer", "lookaround",
    "backreference", "conditionals", "atomic-possessive", "nullable-empty", "branch-alternatives",
    "class-heavy", "windowed", "scanner", "cold-compile", "cold-module", "match-surface",
)
PARENT_CASES_PER_COHORT = 1224
CASES_PER_COHORT = PARENT_CASES_PER_COHORT + len(FAMILIES) * VARIANTS


def C(case_id, cohort, category, api, lifecycle, pattern, string, ops, **values):
    return {"id": case_id, "cohort": cohort, "category": category, "api": api, "lifecycle": lifecycle, "pattern": pattern, "string": string, "ops": ops, "weight": 1, "flags": values.pop("flags", []), **values}


def generated_case(cohort, family, variant):
    hold = cohort == "holdout"
    family_index = FAMILIES.index(family)
    rng = random.Random(SEEDS[cohort] + family_index * 1009 + variant * 9176)
    copies = (1, 2, 4, 8, 16, 32)[variant % 6]
    width = (32, 128, 512, 2048, 8192, 32768)[(variant // 6) % 6]
    number = 31 + variant * 41 + family_index * 7
    lower = rng.choice(("amber", "cedar", "delta", "ember", "maple", "north", "orbit", "signal") if hold else ("acorn", "beacon", "copper", "drift", "elm", "fjord", "grove", "harbor"))
    other = rng.choice(("violet", "willow", "remote", "stable", "vector", "winter") if hold else ("birch", "direct", "native", "quartz", "summer", "zebra"))
    upper = lower.upper()
    prefix = "hold.expanded" if hold else "cal.expanded"
    case_id = f"{prefix}.{family}.{variant:02d}"
    category = f"expanded-{family}"
    ops = max(3, 144 // copies)

    if family == "long-literal":
        marker = f"{other.upper()}-{number}-DONE" if hold else f"{other}-{number}-ready"
        tail = marker if variant % 3 else "ordinary-tail"
        return C(case_id, cohort, category, "search", "compiled", marker, ("q" if hold else "x") * width + tail, max(2, 18000 // width))
    if family == "line-records":
        pattern = r"^(?P<level>INFO|WARN|ERROR)\s+(?P<code>[A-Z]{2,5}-[0-9]{2,5})\s+(?P<text>[^\n]+)$"
        lines = [f"{'ERROR' if item % 3 == 0 else 'INFO'} {upper[:4]}-{number + item} {other} message {item}" for item in range(copies)]
        if variant % 5 == 0:
            lines.insert(len(lines) // 2, "broken record")
        return C(case_id, cohort, category, "finditer", "compiled", pattern, "\n".join(lines), ops, flags=["M"])
    if family == "json-fields":
        pattern = r'"(?P<key>[A-Za-z_][A-Za-z0-9_]*)"\s*:\s*(?P<value>"[^"\n]*"|-?[0-9]+(?:\.[0-9]+)?|true|false|null)'
        values = [f'"{lower}_{item}": ' + (f'"{other}-{number + item}"' if item % 2 else str(number + item)) for item in range(copies)]
        return C(case_id, cohort, category, "finditer", "compiled", pattern, "{" + ", ".join(values) + "}", ops)
    if family == "html-tags":
        pattern = r"<(?P<tag>[A-Za-z][A-Za-z0-9-]*)(?:\s+[A-Za-z_:][-A-Za-z0-9_:.]*(?:=(?:\"[^\"]*\"|'[^']*'|[^ >]+))?)*\s*/?>"
        value = " ".join(f'<{lower}-{item} class="{other}" data-id="{number + item}">' for item in range(copies))
        return C(case_id, cohort, category, "findall", "compiled", pattern, value, ops)
    if family == "markdown-links":
        pattern = r"\[(?P<label>[^]\n]{1,80})\]\((?P<url>https?://[^ )\n]+)(?:\s+\"(?P<title>[^\"]*)\")?\)"
        value = " ".join(f'[{lower} {item}](https://{other}.example/{number + item}' + (f' "note {item}"' if item % 2 else "") + ")" for item in range(copies))
        return C(case_id, cohort, category, "finditer", "compiled", pattern, value, ops)
    if family == "source-tokens":
        pattern = r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)|(?P<number>[0-9]+(?:\.[0-9]+)?)|(?P<op>==|!=|<=|>=|[-+*/=(){}.,:])"
        value = " ".join(f"{lower}_{item} = ({number + item} + {item}.5) * {other}" for item in range(copies))
        return C(case_id, cohort, category, "scanner" if variant % 3 == 0 else "finditer", "compiled", pattern, value, max(3, 100 // copies))
    if family == "comment-strip":
        if variant % 2:
            pattern = r"(?m)^[ \t]*#.*$|[ \t]+#.*$"
            value = "\n".join(f"{lower}_{item} = {number + item} # {other} note" for item in range(copies))
        else:
            pattern = r"//[^\n]*|/\*.*?\*/"
            value = "\n".join(f"{lower}({item}); // {other}\n/* {lower} {number + item} */" for item in range(copies))
        return C(case_id, cohort, category, "sub", "compiled", pattern, value, ops, repl="", flags=["S"] if variant % 2 == 0 else [])
    if family == "url-extract":
        pattern = r"(?P<scheme>https?|ftp)://(?P<host>[A-Za-z0-9.-]+)(?::(?P<port>[0-9]{1,5}))?(?P<path>/[^ ?#\n]*)?(?:\?(?P<query>[^ #\n]*))?"
        value = " ".join(f"see {'ftp' if item % 3 == 0 else 'https'}://{lower}{item}.{other}.example:{2000 + number + item}/docs/{item}?q={number}" for item in range(copies))
        return C(case_id, cohort, category, "finditer", "compiled", pattern, value, ops)
    if family == "email-extract":
        pattern = r"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![A-Za-z0-9._%+-])"
        value = " ".join(f"<{lower}{item}+{other}@mail{item % 4}.example.org>" for item in range(copies))
        return C(case_id, cohort, category, "findall", "compiled", pattern, value, max(3, 112 // copies))
    if family == "ip-version":
        if variant % 2:
            pattern = r"\b(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})(?:\.(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})){3}\b"
            value = " ".join(f"10.{item % 250}.{number % 250}.{(item * 7 + number) % 250}" for item in range(copies))
        else:
            pattern = r"\bv?(?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<patch>[0-9]+)(?:-(?P<tag>[A-Za-z0-9.-]+))?\b"
            value = " ".join(f"v{1 + item % 4}.{number % 30}.{item}" + (f"-{other}.{item}" if item % 2 else "") for item in range(copies))
        return C(case_id, cohort, category, "findall", "compiled", pattern, value, ops)
    if family == "dates-numbers":
        if variant % 2:
            pattern = r"(?P<date>[0-9]{4}[-/][0-9]{2}[-/][0-9]{2})[ T](?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2})(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})?"
            value = " ".join(f"2026-{1 + item % 12:02d}-{1 + item % 27:02d}T06:{number % 60:02d}:{item % 60:02d}+01:00" for item in range(copies))
        else:
            pattern = r"(?<![A-Za-z0-9_])[-+]?(?:[0-9]+(?:_[0-9]+)*(?:\.[0-9]+)?|\.[0-9]+)(?:[eE][-+]?[0-9]+)?(?![A-Za-z0-9_])"
            value = " ".join(f"{number + item}_{item:02d}.{item % 100:02d}e-{1 + item % 4}" for item in range(copies))
        return C(case_id, cohort, category, "finditer", "compiled", pattern, value, ops)
    if family == "phone-postcode":
        pattern = r"(?:\+[0-9]{1,3}[ .-]?)?(?:\([0-9]{2,4}\)|[0-9]{2,4})[ .-][0-9]{3,4}[ .-][0-9]{3,4}|\b[A-Z]{1,2}[0-9][A-Z0-9]?[ ]?[0-9][A-Z]{2}\b"
        value = " ".join(f"+44 (20) {1000 + item} {2000 + number % 7000}" if item % 2 else f"{upper[:2]}{1 + item % 8} {1 + item % 8}{other[:2].upper()}" for item in range(copies))
        return C(case_id, cohort, category, "findall", "compiled", pattern, value, ops)
    if family == "path-text":
        pattern = r"(?:[A-Za-z]:\\|/|\.{1,2}/)?[A-Za-z0-9_.-]+(?:(?:/|\\)[A-Za-z0-9_.-]+)+"
        separator = "\\" if variant % 2 else "/"
        root = "C:\\" if variant % 2 else "../"
        value = " ".join(f"{root}{lower}{separator}{other}{separator}{number + item}.txt" for item in range(copies))
        return C(case_id, cohort, category, "findall", "compiled", pattern, value, ops)
    if family == "path-bytes":
        pattern = rb"(?:/|\.{1,2}/)?[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+"
        value = b" ".join(f"../{lower}/{other}/{number + item}.bin".encode("ascii") for item in range(copies))
        return C(case_id, cohort, category, "finditer", "compiled", pattern, value, ops, subject_kind="memoryview" if variant % 2 else "bytes")
    if family == "csv-fields":
        pattern = r'(?:^|,)(?:"(?P<quoted>(?:[^"]|"")*)"|(?P<plain>[^,\n]*))'
        value = ",".join(f'"{lower},{other} {item}"' if item % 2 else f"{lower}_{number + item}" for item in range(copies * 2))
        return C(case_id, cohort, category, "finditer", "compiled", pattern, value, max(3, 104 // copies))
    if family == "quoted-escapes":
        pattern = r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''
        value = " ".join(f'"{lower}\\n{other} {item}"' if item % 2 else f"'{lower}\\'{other} {item}'" for item in range(copies))
        return C(case_id, cohort, category, "findall", "compiled", pattern, value, ops)
    if family == "whitespace-clean":
        pattern = r"^[ \t]+|[ \t]+$|[ \t]{2,}"
        value = "\n".join(f"  {lower}\t  {other}   {number + item}  " for item in range(copies))
        return C(case_id, cohort, category, "sub", "compiled", pattern, value, ops, repl=" ", flags=["M"])
    if family == "newline-normalize":
        pattern = r"\r\n?|\n"
        endings = ("\r\n", "\n", "\r")
        value = "".join(f"{lower} {number + item}{endings[item % 3]}" for item in range(copies * 2))
        return C(case_id, cohort, category, "subn", "compiled", pattern, value, ops, repl="\n", count=5 if variant % 7 == 0 else 0)
    if family == "split-delimiters":
        pattern = r"\s*(?:[,;|]|::|->)\s*"
        separators = (",", ";", "|", "::", "->")
        value = "".join(f"{lower}{item} {separators[item % 5]} " for item in range(copies * 2)) + other
        return C(case_id, cohort, category, "split", "compiled", pattern, value, ops, maxsplit=5 if variant % 4 == 0 else 0)
    if family == "split-captures":
        pattern = r"(\s*(?:[,;|]|::|->)\s*)"
        separators = (",", ";", "|", "::", "->")
        value = "".join(f"{lower}{item} {separators[item % 5]} " for item in range(copies * 2)) + other
        return C(case_id, cohort, category, "split", "compiled", pattern, value, ops, maxsplit=5 if variant % 4 == 0 else 0)
    if family == "replace-redact":
        pattern = r"(?P<key>password|token|secret|api_key)\s*[:=]\s*(?P<value>[^,; \n]+)"
        value = " ".join(f"{'token' if item % 2 else 'password'}={lower}{number + item};" for item in range(copies))
        return C(case_id, cohort, category, "subn", "compiled", pattern, value, ops, repl=r"\g<key>=<redacted>", flags=["I"], count=4 if variant % 6 == 0 else 0)
    if family == "replace-template":
        pattern = r"(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>[A-Za-z0-9_.-]+)"
        value = " ".join(f"{lower}_{item}={other}-{number + item}" for item in range(copies))
        return C(case_id, cohort, category, "sub", "compiled", pattern, value, ops, repl=r"[\g<value>: \g<key>]", count=4 if variant % 7 == 0 else 0)
    if family == "replace-callback":
        pattern = r"[A-Za-z]+(?:-[A-Za-z]+)?"
        value = " ".join(f"{lower}-{other} {number + item}" for item in range(copies))
        return C(case_id, cohort, category, "subn", "compiled", pattern, value, max(3, 108 // copies), repl={"callable": "upper_bracket" if variant % 2 else "lower_bracket"}, count=4 if variant % 5 == 0 else 0)
    if family == "unicode-words":
        pattern = r"\b\w+(?:['’-]\w+)*\b"
        value = " ".join(f"{lower} café naïve 雪_{number + item} Straße العربية" for item in range(copies))
        return C(case_id, cohort, category, "findall", "compiled", pattern, value, ops)
    if family == "unicode-case":
        pattern = r"[a-z]+|kelvin|straße"
        value = " ".join(f"{upper} İıſK KELVIN Straße {other.upper()}" for _ in range(copies))
        return C(case_id, cohort, category, "finditer", "compiled", pattern, value, ops, flags=["I"])
    if family == "combining-emoji":
        pattern = r"(?:[A-Za-z]+[\u0300-\u036f]+)|[😀-🙏]+|[🌀-🗿]+"
        value = " ".join(f"{lower}e\u0301 😀🙏 雪 🌀 {other}a\u0308" for _ in range(copies))
        return C(case_id, cohort, category, "findall", "compiled", pattern, value, ops)
    if family == "ascii-boundary":
        pattern = r"\b[A-Za-z0-9_]+\b|\B[-.]\B"
        value = " ".join(f"{lower}_{number + item} café.雪 {other}-{item}" for item in range(copies))
        return C(case_id, cohort, category, "finditer", "compiled", pattern, value, ops, flags=["A"])
    if family == "byte-buffer":
        pattern = rb"(?P<key>[A-Za-z_][A-Za-z0-9_]*)=(?P<value>[A-Za-z0-9_.-]+)|0x[0-9A-Fa-f]+"
        value = b" ".join(f"{lower}_{item}={other}-{number + item} 0x{number + item:x}".encode("ascii") for item in range(copies)) + b" \xff"
        return C(case_id, cohort, category, "findall" if variant % 2 else "finditer", "compiled", pattern, value, ops, subject_kind=("memoryview", "bytearray", "bytes")[variant % 3])
    if family == "lookaround":
        pattern = r"(?<![A-Za-z0-9_])(?P<name>[A-Za-z_][A-Za-z0-9_]*)(?=\s*[:=])"
        value = " ".join(f"{lower}_{item} {'=' if item % 2 else ':'} {number + item}" for item in range(copies))
        return C(case_id, cohort, category, "finditer", "compiled", pattern, value, ops)
    if family == "backreference":
        pattern = r"(?P<word>[A-Za-z]{2,8})(?P<sep>[-:/])(?P=word)(?P=sep)[0-9]+"
        value = " ".join(f"{lower[:5]}{('-' if item % 2 else ':')}{lower[:5]}{('-' if item % 2 else ':')}{number + item}" for item in range(copies))
        return C(case_id, cohort, category, "findall", "compiled", pattern, value, ops, flags=["I"] if variant % 3 == 0 else [])
    if family == "conditionals":
        pattern = r"(?P<open>[<\[])?(?P<word>[A-Za-z][A-Za-z0-9_-]*)(?(open)[>\]]|!)"
        value = " ".join(f"<{lower}_{item}>" if item % 2 else f"{other}_{item}!" for item in range(copies))
        return C(case_id, cohort, category, "finditer", "compiled", pattern, value, ops)
    if family == "atomic-possessive":
        pattern = r"(?>[A-Za-z]+(?:_[A-Za-z]+)*)=[0-9]++|(?:ab|a)++z|x*+y"
        value = " ".join(f"{lower}_{other}={number + item}" for item in range(copies)) + (" ababz" if variant % 3 else " xxxy")
        return C(case_id, cohort, category, "findall", "compiled", pattern, value, ops)
    if family == "nullable-empty":
        pattern = r"(?:|[A-Za-z])*?(?=[:;])|\b|(?=,)"
        value = " ".join(f"{lower}{':' if item % 2 else ';'}{other}," for item in range(copies))
        return C(case_id, cohort, category, "finditer", "compiled", pattern, value, max(3, 80 // copies))
    if family == "branch-alternatives":
        words = ("alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "india", "juliet", "kilo", "lima", "mike", "november", "oscar", "papa")
        pattern = r"(?:" + "|".join(words) + r")(?:-[0-9]{1,5})?"
        value = " ".join(f"{words[(item + variant) % len(words)]}-{number + item}" for item in range(copies))
        return C(case_id, cohort, category, "findall", "compiled", pattern, value, ops, flags=["I"] if variant % 4 == 0 else [])
    if family == "class-heavy":
        pattern = r"[A-F0-9]{2}(?:[:-][A-F0-9]{2}){5}|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|[^\s,;:]+"
        value = " ".join(f"AA:0B:{item % 255:02X}:12:FE:{number % 255:02X}, {lower}{item}@{other}.example; token-{item}" for item in range(copies))
        return C(case_id, cohort, category, "finditer", "compiled", pattern, value, ops, flags=["I"] if variant % 3 == 0 else [])
    if family == "windowed":
        body = " ".join(f"{lower}_{item}={number + item}" for item in range(copies))
        value = f"SKIP000 ! {body} ! TAIL999"
        api = ("search", "findall", "finditer")[variant % 3]
        return C(case_id, cohort, category, api, "compiled", r"(?P<key>[A-Za-z_]+)_(?P<index>[0-9]+)=(?P<num>[0-9]+)", value, ops, pos=10, endpos=10 + len(body))
    if family == "scanner":
        byte_mode = variant % 2 == 1
        pattern = r"(?P<key>[A-Za-z_][A-Za-z0-9_]*)=(?P<value>[A-Za-z0-9_.-]+)|(?P<number>[0-9]+)|(?P<mark>[:,;])"
        value = " ".join(f"{lower}_{item}={other}-{number + item}; {item}," for item in range(copies))
        if byte_mode:
            pattern, value = pattern.encode("ascii"), value.encode("ascii")
        return C(case_id, cohort, category, "scanner", "compiled", pattern, value, max(3, 88 // copies), subject_kind="memoryview" if byte_mode and variant % 4 == 1 else "bytes" if byte_mode else "text")
    if family == "cold-compile":
        choices = (
            r"^(?P<scheme>https?)://(?P<host>[A-Za-z0-9.-]+)(?::(?P<port>[0-9]{1,5}))?(?P<path>/[^?#]*)?(?:\?(?P<query>[^#]*))?$",
            r"^(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})[ T](?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2})(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})?$",
            r"^(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>\"[^\"]*\"|'[^']*'|[^#\n]*?)\s*(?:#.*)?$",
        )
        return C(case_id, cohort, category, "compile", "cold", choices[variant % len(choices)], None, 4 + variant % 5, flags=["M"] if variant % 3 == 2 else [])
    if family == "cold-module":
        pattern = r"(?P<key>[A-Za-z_][A-Za-z0-9_]*)=(?P<value>[A-Za-z0-9_.-]+)"
        value = f"prefix {lower}={other}-{number} suffix"
        return C(case_id, cohort, category, "search" if variant % 2 else "sub", "cold", pattern, value, 4 + variant % 5, repl=r"[\g<key>: \g<value>]" if variant % 2 == 0 else "")
    if family == "match-surface":
        pattern = r"(?P<left>[A-Za-z_]+)-(?P<num>[0-9]+)(?:\.(?P<tail>[A-Za-z]+))?"
        value = f"prefix {lower}_{variant}-{number}" + (f".{other}" if variant % 2 else "") + " suffix"
        return C(case_id, cohort, category, "match-surface", "compiled", pattern, value, ops, expand=r"<\g<num>: \g<left>: \g<tail>>")
    raise RuntimeError(f"unknown expanded performance family: {family}")


def cases():
    result = list(parent_cases())
    for cohort in ("calibration", "holdout"):
        for family in FAMILIES:
            for variant in range(VARIANTS):
                result.append(generated_case(cohort, family, variant))
    return result
