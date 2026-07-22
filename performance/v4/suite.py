"""Large, balanced, deterministic performance matrix for the rebar experiment."""

import random

from performance.v3.suite import cases as parent_cases


MODULES = ["re", "candidates.ast_candidate", "candidates.vm_candidate", "candidates.rust_candidate"]
TRIALS = 13
WARMUPS = 4
ORDER_SEED = 1983072901
BOOTSTRAP_SEED = 1983072902
BOOTSTRAPS = 2000
VARIANTS = 32
SEEDS = {"calibration": 1983072911, "holdout": 1983072929}
FAMILIES = (
    "literal-hit", "literal-miss", "long-ending", "formatted-lines", "prefix-check", "whole-check",
    "nearby-capture", "findall-tokens", "finditer-pairs", "split-keep", "replace-groups", "replace-callback",
    "bytes-tokens", "bytes-buffer", "unicode-words", "unicode-casefold", "cold-compile", "cold-search",
    "module-search", "module-replace", "empty-iterator", "references", "conditionals", "branch-control",
    "scanner-text", "scanner-bytes", "window-search", "window-collection", "request-records", "everyday-address",
    "structured-text", "cleanup", "escape", "bytes-replace", "ascii-mode", "verbose-dotall",
)
CASES_PER_COHORT = 72 + len(FAMILIES) * VARIANTS


def C(case_id, cohort, category, api, lifecycle, pattern, string, ops, **values):
    return {"id": case_id, "cohort": cohort, "category": category, "api": api, "lifecycle": lifecycle, "pattern": pattern, "string": string, "ops": ops, "weight": 1, "flags": values.pop("flags", []), **values}


def generated_case(cohort, family, variant):
    hold = cohort == "holdout"
    prefix = "hold.large" if hold else "cal.large"
    family_index = FAMILIES.index(family)
    rng = random.Random(SEEDS[cohort] + family_index * 1009 + variant * 9176)
    copies = (1, 2, 4, 8)[variant % 4]
    width = (64, 192, 640, 2048)[(variant // 4) % 4]
    number = 17 + variant * 37 + family_index
    lower = rng.choice(("alpha", "bravo", "delta", "ember", "maple", "orbit", "quartz", "signal") if hold else ("acorn", "beacon", "cedar", "drift", "elm", "fjord", "grove", "harbor"))
    upper = lower.upper()
    other = rng.choice(("violet", "willow", "zebra", "remote", "stable", "vector") if hold else ("amber", "birch", "copper", "direct", "native", "winter"))
    token = f"{lower}_{number}"
    ops = max(8, 192 // copies)
    case_id = f"{prefix}.{family}.{variant:02d}"
    category = f"large-{family}"

    if family == "literal-hit":
        marker = f"{other}-{number}"
        return C(case_id, cohort, category, "search", "compiled", marker, (f"{lower} {upper} " * copies) + marker + " end", ops)
    if family == "literal-miss":
        marker = f"missing-{number}-{other}"
        return C(case_id, cohort, category, "search", "compiled", marker, (f"{lower} {upper} {token} " * copies) + "ordinary words", ops)
    if family == "long-ending":
        marker = "FINISH" if hold else "COMPLETE"
        return C(case_id, cohort, category, "search", "compiled", marker + r"$", ("q" if hold else "x") * width + marker, max(6, 16000 // width))
    if family == "formatted-lines":
        line = f"{upper}-{number:04d}" if hold else f"{lower}_{number:04d}"
        pattern = r"^[A-Z]{3,8}-[0-9]{2,5}$" if hold else r"^[a-z]{3,8}_[0-9]{2,5}$"
        return C(case_id, cohort, category, "findall", "compiled", pattern, ("ignore\n" + line + "\nwrong_!\n") * copies, max(8, 144 // copies), flags=["M"])
    if family == "prefix-check":
        pattern = r"[A-Z]{3,8}_[0-9]{2,5}" if hold else r"[a-z]{3,8}-[0-9]{2,5}"
        value = f"{upper}_{number} tail" if hold else f"{lower}-{number} tail"
        if variant % 4 == 3:
            value = "!" + value
        return C(case_id, cohort, category, "match", "compiled", pattern, value, ops)
    if family == "whole-check":
        pattern = r"(?:[A-Z]+(?:-[0-9]+)?)(?:\.(?:[A-Z]+(?:-[0-9]+)?))*" if hold else r"(?:[a-z]+(?:_[0-9]+)?)(?:/(?:[a-z]+(?:_[0-9]+)?))*"
        parts = [f"{upper}-{number + item}" if hold else f"{lower}_{number + item}" for item in range(copies)]
        value = ("." if hold else "/").join(parts)
        if variant % 7 == 6:
            value += "!"
        return C(case_id, cohort, category, "fullmatch", "compiled", pattern, value, max(8, 128 // copies))
    if family == "nearby-capture":
        pattern = r"(?<=code:)(?P<value>[A-Z]{2}[0-9]+)(?=;)" if hold else r"(?<=id=)(?P<value>[a-z]{2}[0-9]+)(?=,)"
        item = f"code:{upper[:2]}{number};" if hold else f"id={lower[:2]}{number},"
        return C(case_id, cohort, category, "search", "compiled", pattern, ("skip=0; " * copies) + item + " next", ops)
    if family == "findall-tokens":
        pattern = r"[A-Z]+(?:_[0-9]+)?" if hold else r"[a-z]+(?:-[0-9]+)?"
        items = [f"{upper}_{number + item}" if hold else f"{lower}-{number + item}" for item in range(copies * 2)]
        return C(case_id, cohort, category, "findall", "compiled", pattern, " :: ".join(items), max(8, 128 // copies))
    if family == "finditer-pairs":
        pattern = r"(?P<key>[A-Z]+):(?P<num>[0-9]+)" if hold else r"(?P<key>[a-z]+)=(?P<num>[0-9]+)"
        items = [f"{upper}:{number + item}" if hold else f"{lower}={number + item}" for item in range(copies * 2)]
        return C(case_id, cohort, category, "finditer", "compiled", pattern, " ".join(items), max(8, 112 // copies))
    if family == "split-keep":
        separators = (";", "|", ":") if hold else (",", ":", ";")
        value = "".join(f"{lower}{item}{separators[item % 3]}" for item in range(copies * 3)) + other
        pattern = r"([;|:])" if hold else r"([,:;])"
        values = {"maxsplit": 4} if variant % 4 == 0 else {}
        return C(case_id, cohort, category, "split", "compiled", pattern, value, max(8, 112 // copies), **values)
    if family == "replace-groups":
        pattern = r"(?P<left>[A-Z]+)_(?P<num>[0-9]+)" if hold else r"(?P<left>[a-z]+)-(?P<num>[0-9]+)"
        value = " ".join(f"{upper}_{number + item}" if hold else f"{lower}-{number + item}" for item in range(copies * 2))
        repl = r"\g<num>:\g<left>" if hold else r"<\g<num>/\g<left>>"
        return C(case_id, cohort, category, "sub", "compiled", pattern, value, max(8, 112 // copies), repl=repl, count=3 if variant % 5 == 0 else 0)
    if family == "replace-callback":
        pattern = r"[A-Z]+" if hold else r"[a-z]+"
        value = " ".join(f"{upper if hold else lower} {number + item}" for item in range(copies * 2))
        callable_name = "lower_bracket" if hold else "upper_bracket"
        return C(case_id, cohort, category, "subn", "compiled", pattern, value, max(8, 96 // copies), repl={"callable": callable_name}, count=2 if variant % 3 == 0 else 0)
    if family == "bytes-tokens":
        pattern = rb"[A-Z]+|[0-9]+" if hold else rb"[a-z]+|[0-9]+"
        item = (f"{upper if hold else lower}{number} ").encode("ascii")
        return C(case_id, cohort, category, "findall", "compiled", pattern, item * (copies * 2) + b"\xff end", max(8, 128 // copies))
    if family == "bytes-buffer":
        pattern = rb"[A-Z]{2,4}[0-9]{2,5}" if hold else rb"[a-z]{2,4}[0-9]{2,5}"
        word = (upper if hold else lower)[:4]
        item = (f"{word}{number} xx ").encode("ascii")
        kind = "memoryview" if variant % 2 else "bytearray"
        return C(case_id, cohort, category, "finditer", "compiled", pattern, item * (copies * 3), max(8, 104 // copies), subject_kind=kind)
    if family == "unicode-words":
        value = ((f"{lower} café 雪_{number} 😀 ٣٣ ") * copies).strip()
        return C(case_id, cohort, category, "findall", "compiled", r"\b\w+\b|[😀-🙏]+", value, max(8, 112 // copies))
    if family == "unicode-casefold":
        value = ((f"{upper} İıſK Kelvin Straße {lower} ") * copies).strip()
        return C(case_id, cohort, category, "findall", "compiled", r"[a-z]+", value, max(8, 96 // copies), flags=["I"])
    if family == "cold-compile":
        pattern = r"^(?P<user>[A-Za-z0-9._+-]+)@(?P<host>[A-Za-z0-9.-]+)(?::(?P<port>[0-9]{1,5}))?(?P<path>/[A-Za-z0-9_./-]*)?$" if hold else r"^(?P<scheme>https?)://(?P<host>[A-Za-z0-9.-]+)(?::(?P<port>[0-9]{1,5}))?(?P<path>/[^?#]*)?(?:\?(?P<query>[^#]*))?$"
        return C(case_id, cohort, category, "compile", "cold", pattern, None, 8 + variant % 8)
    if family == "cold-search":
        pattern = r"(?P<tag>[A-Z]{2,8})_[0-9]{1,5}" if hold else r"(?P<name>[a-z]{2,8})-[0-9]{1,5}"
        value = f"prefix {upper}_{number} suffix" if hold else f"prefix {lower}-{number} suffix"
        return C(case_id, cohort, category, "search", "cold", pattern, value, 10 + variant % 7)
    if family == "module-search":
        pattern = r"[A-Z]{2,8}_[0-9]+" if hold else r"[a-z]{2,8}-[0-9]+"
        value = f"prefix {upper}_{number} suffix" if hold else f"prefix {lower}-{number} suffix"
        return C(case_id, cohort, category, "search", "module", pattern, value, ops)
    if family == "module-replace":
        pattern = r"(?P<key>[A-Z]+):(?P<num>[0-9]+)" if hold else r"(?P<key>[a-z]+)=(?P<num>[0-9]+)"
        value = " ".join(f"{upper}:{number + item}" if hold else f"{lower}={number + item}" for item in range(copies * 2))
        return C(case_id, cohort, category, "sub", "module", pattern, value, max(8, 104 // copies), repl=r"\g<num>/\g<key>")
    if family == "empty-iterator":
        pattern = r"(?=;)|\b" if hold else r"\B|(?=,)"
        value = ((f"{lower};{other} " if hold else f"{lower},{other} ") * copies).strip()
        return C(case_id, cohort, category, "finditer", "compiled", pattern, value, max(8, 88 // copies))
    if family == "references":
        word = upper[: 2 + variant % 3] if hold else lower[: 2 + variant % 3]
        pattern = r"([A-Z]{2,5}):\1" if hold else r"([a-z]{2,5})-\1"
        value = f"{word}:{word}" if hold else f"{word}-{word}"
        if variant % 6 == 5:
            value += "x"
        return C(case_id, cohort, category, "fullmatch", "compiled", pattern, value, ops)
    if family == "conditionals":
        pattern = r"(\[)?[0-9]+(?(1)\]|;)" if hold else r"(<)?[A-Za-z]+(?(1)>|!)"
        value = f"[{number}] rest" if hold else f"<{lower}> rest"
        if variant % 3 == 1:
            value = f"{number}; rest" if hold else f"{lower}! rest"
        return C(case_id, cohort, category, "match", "compiled", pattern, value, ops)
    if family == "branch-control":
        pattern = r"a*+b|cd+|(?>(?:xy|x))z+" if hold else r"(?>ab|a)b+|c*+d|(?:xy)++z"
        value = ("x " * copies) + ("cdddd" if hold else "abbbbb") + " tail"
        return C(case_id, cohort, category, "search", "compiled", pattern, value, max(8, 112 // copies))
    if family == "scanner-text":
        pattern = r"(?P<key>[A-Z]+):(?P<num>[0-9]+)" if hold else r"(?P<key>[a-z]+)=(?P<num>[0-9]+)"
        value = " ".join(f"{upper}:{number + item}" if hold else f"{lower}={number + item}" for item in range(copies * 2))
        return C(case_id, cohort, category, "scanner", "compiled", pattern, value, max(8, 80 // copies))
    if family == "scanner-bytes":
        pattern = rb"(?P<key>[A-Z]+)=(?P<num>[0-9]+)" if hold else rb"(?P<key>[a-z]+):(?P<num>[0-9]+)"
        value = b" ".join((f"{upper if hold else lower}{'=' if hold else ':'}{number + item}").encode("ascii") for item in range(copies * 2))
        return C(case_id, cohort, category, "scanner", "compiled", pattern, value, max(8, 80 // copies), subject_kind="memoryview" if variant % 2 else "bytes")
    if family == "window-search":
        pattern = r"[A-Z]{2,8}[0-9]+" if hold else r"[a-z]{2,8}[0-9]+"
        middle = f"{upper if hold else lower}{number}"
        value = f"SKIP000 xx {middle} yy TAIL999"
        start = value.index(middle)
        return C(case_id, cohort, category, "search", "compiled", pattern, value, ops, pos=start - 3, endpos=start + len(middle) + 3)
    if family == "window-collection":
        pattern = r"[A-Z]+|[0-9]+" if hold else r"[a-z]+|[0-9]+"
        body = " ".join(f"{upper if hold else lower}{number + item}" for item in range(copies * 2))
        value = "SKIP000 " + body + " TAIL999"
        api = "findall" if variant % 2 else "finditer"
        return C(case_id, cohort, category, api, "compiled", pattern, value, max(8, 104 // copies), pos=8, endpos=8 + len(body))
    if family == "request-records":
        method = "PATCH" if hold else "POST"
        pattern = r"(?P<method>GET|POST|PATCH|DELETE) (?P<path>/[A-Za-z0-9_./-]+) HTTP/[0-9.]+"
        value = "\n".join(f'10.0.0.{item + 1} "{method} /{lower}/{number + item}/items HTTP/1.1" 20{item % 5}' for item in range(copies * 2))
        return C(case_id, cohort, category, "finditer", "compiled", pattern, value, max(8, 80 // copies))
    if family == "everyday-address":
        choice = variant % 3
        if choice == 0:
            pattern = r"(?P<scheme>https?|ftp)://(?P<host>[A-Za-z0-9.-]+)(?::(?P<port>[0-9]+))?(?P<path>/[^ ?#]*)?"
            value = f"see {'ftp' if hold else 'https'}://{lower}.example.net:{2000 + number}/docs/{other}-{number}?q=1"
            api = "search"
        elif choice == 1:
            pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
            value = " ".join(f"{lower}{item}+tag@{other}.example.org" for item in range(copies * 2))
            api = "findall"
        else:
            pattern = r"(?P<date>[0-9]{4}[-/][0-9]{2}[-/][0-9]{2})[ T](?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2})(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})?"
            value = f"done 2026{'/' if hold else '-'}08{'/' if hold else '-'}{10 + variant % 18:02d} 06:31:{number % 60:02d}+01:00 ready"
            api = "search"
        return C(case_id, cohort, category, api, "compiled", pattern, value, max(8, 104 // copies))
    if family == "structured-text":
        choice = variant % 3
        if choice == 0:
            pattern = r"^(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?P<value>[^#\n]*?)\s*(?:#.*)?$" if hold else r"^(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>[^#\n]*?)\s*(?:#.*)?$"
            separator = ":" if hold else "="
            value = "\n".join(f"{lower}_{item} {separator} {other} {number + item}" + (" # note" if item % 2 else "") for item in range(copies * 2))
            return C(case_id, cohort, category, "finditer", "compiled", pattern, value, max(8, 72 // copies), flags=["M"])
        if choice == 1:
            pattern = r"(?:^|\s)(?:\.\./|/)?[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+" if hold else r"(?:^|\s)(?:\./|/)?[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+"
            value = " ".join(f"{'../' if hold else './'}{lower}/{other}/{number + item}.txt" for item in range(copies * 2))
            return C(case_id, cohort, category, "findall", "compiled", pattern, value, max(8, 88 // copies))
        pattern = r"([\"'])(.*?)\1"
        value = " ".join(f"{lower}={'\"' if item % 2 else chr(39)}{other} {number + item}{'\"' if item % 2 else chr(39)}" for item in range(copies * 2))
        return C(case_id, cohort, category, "findall", "compiled", pattern, value, max(8, 80 // copies))
    if family == "cleanup":
        if variant % 2:
            value = ((f"  {lower}\t {other}  \n") * copies).strip("\n")
            return C(case_id, cohort, category, "sub", "compiled", r"^[ \t]+|[ \t]+$", value, max(8, 104 // copies), repl="", flags=["M"])
        separators = ":|/" if hold else ",;|"
        value = "".join(f"{lower}{item} {separators[item % 3]} " for item in range(copies * 3)) + other
        pattern = r"\s*[:|/]\s*" if hold else r"\s*[,;|]\s*"
        return C(case_id, cohort, category, "split", "compiled", pattern, value, max(8, 104 // copies), maxsplit=4 if variant % 4 == 0 else 0)
    if family == "escape":
        if variant % 2:
            pattern = (f"{upper}+[{other}] # {number}\\tail").encode("ascii")
        else:
            pattern = f"{lower}+[{other}] # {number}\\tail café 雪"
        return C(case_id, cohort, category, "escape", "module", pattern, None, ops)
    if family == "bytes-replace":
        pattern = rb"([A-Z]+)=([0-9]+)" if hold else rb"([a-z]+):([0-9]+)"
        separator = "=" if hold else ":"
        value = b" ".join((f"{upper if hold else lower}{separator}{number + item}").encode("ascii") for item in range(copies * 2))
        return C(case_id, cohort, category, "subn", "compiled", pattern, value, max(8, 104 // copies), repl=rb"\2/\1", count=3 if variant % 5 == 0 else 0, subject_kind="bytearray" if variant % 2 else "bytes")
    if family == "ascii-mode":
        value = ((f"{lower} café 雪 {upper}_{number} naïve ") * copies).strip()
        return C(case_id, cohort, category, "findall", "compiled", r"\b\w+\b", value, max(8, 104 // copies), flags=["A"])
    if family == "verbose-dotall":
        if variant % 2:
            pattern = r"(?P<name>[A-Za-z_][A-Za-z0-9_]*) \s* : \s* (?P<num>[0-9]+) # field" if hold else r"(?P<name>[A-Za-z_][A-Za-z0-9_]*) \s* = \s* (?P<num>[0-9]+) # field"
            value = f"prefix {lower}_{variant} {':' if hold else '='} {number} suffix"
            return C(case_id, cohort, category, "search", "compiled", pattern, value, ops, flags=["X"])
        marker = "START" if hold else "BEGIN"
        finish = "STOP" if hold else "END"
        pattern = marker + r"\n(?P<body>.*?)\n" + finish
        value = "header\n" + marker + "\n" + (f"{lower} {other} {number}\n" * copies) + finish + "\nfooter"
        return C(case_id, cohort, category, "search", "compiled", pattern, value, max(8, 96 // copies), flags=["S"])
    raise RuntimeError(f"unknown performance family: {family}")


def cases():
    result = list(parent_cases())
    for cohort in ("calibration", "holdout"):
        for family in FAMILIES:
            for variant in range(VARIANTS):
                result.append(generated_case(cohort, family, variant))
    return result
