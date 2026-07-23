#!/usr/bin/env python3
"""Reproduce full-plane CPython Unicode checks for the Rust regex candidate."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import itertools
import json
import random
import re
import unicodedata
from pathlib import Path
from re._casefix import _EXTRA_CASES


SEED = 2026072302
CODEPOINTS = 0x110000

# Each alternative has exactly one named capture.  Consequently lastindex
# gives the complete category partition without collecting a million matches
# or repeatedly copying a million-codepoint string across the native boundary.
CATEGORY_PARTITION = (
    r"(?P<digit>\d)|(?P<space>\s)|(?P<word>\w)|(?P<other>[\s\S])"
)
CASE_PARTITION = (
    r"(?P<latin>[A-Za-z])"
    r"|(?P<latin1>[\xc0-\xde])"
    r"|(?P<greek>[\u0391-\u03a9])"
    r"|(?P<cyrillic>[\u0400-\u042f])"
    r"|(?P<deseret>[\U00010400-\U00010427])"
    r"|(?P<other>[\s\S])"
)
PARTITIONS = (
    ("unicode-categories", CATEGORY_PARTITION, 0),
    ("ascii-categories", CATEGORY_PARTITION, re.ASCII),
    ("unicode-ignorecase-ranges", CASE_PARTITION, re.IGNORECASE),
    ("ascii-ignorecase-ranges", CASE_PARTITION, re.ASCII | re.IGNORECASE),
)

CASE_EQUIVALENCES = (
    (0x0049, 0x0069, 0x0130, 0x0131),
    (0x004B, 0x006B, 0x212A),
    (0x0053, 0x0073, 0x017F),
    (0x00B5, 0x039C, 0x03BC),
    (0x00DF, 0x1E9E),
    (0x0345, 0x0399, 0x03B9, 0x1FBE),
    (0x0390, 0x1FD3),
    (0x03B0, 0x1FE3),
    (0x0392, 0x03B2, 0x03D0),
    (0x0395, 0x03B5, 0x03F5),
    (0x0398, 0x03B8, 0x03D1),
    (0x039A, 0x03BA, 0x03F0),
    (0x03A0, 0x03C0, 0x03D6),
    (0x03A1, 0x03C1, 0x03F1),
    (0x03A3, 0x03C2, 0x03C3),
    (0x03A6, 0x03C6, 0x03D5),
    (0x0412, 0x0432, 0x1C80),
    (0x0414, 0x0434, 0x1C81),
    (0x041E, 0x043E, 0x1C82),
    (0x0421, 0x0441, 0x1C83),
    (0x0422, 0x0442, 0x1C84, 0x1C85),
    (0x042A, 0x044A, 0x1C86),
    (0x0462, 0x0463, 0x1C87),
    (0xA64A, 0xA64B, 0x1C88),
    (0x1E60, 0x1E61, 0x1E9B),
    (0xFB05, 0xFB06),
)


def json_value(value):
    """Keep bytes, buffers, surrogates, and tuple results reproducible."""

    if isinstance(value, bytes):
        return {"bytes_hex": value.hex()}
    if isinstance(value, bytearray):
        return {"bytearray_hex": value.hex()}
    if isinstance(value, memoryview):
        return {"memoryview_hex": value.tobytes().hex()}
    if isinstance(value, tuple):
        return {"tuple": [json_value(item) for item in value]}
    if isinstance(value, list):
        return [json_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): json_value(item) for key, item in value.items()}
    return value


def snapshot(match):
    if match is None:
        return None
    return {
        "span": match.span(),
        "regs": match.regs,
        "groups": match.groups(),
        "groupdict": match.groupdict(),
        "lastindex": match.lastindex,
        "lastgroup": match.lastgroup,
        "pos": match.pos,
        "endpos": match.endpos,
    }


def attempted(action):
    try:
        return {"value": action()}
    except Exception as error:
        return {"error": type(error).__name__, "message": str(error)}


def subject_length(subject):
    if isinstance(subject, str):
        return len(subject)
    return memoryview(subject).nbytes


def add_failure(failures, kind, expected, actual, **details):
    failures.append(
        {
            "kind": kind,
            **{key: json_value(value) for key, value in details.items()},
            "expected": json_value(expected),
            "actual": json_value(actual),
        }
    )


def full_plane(module, stride, failures):
    results = []
    checks = 0
    for label, pattern, flags in PARTITIONS:
        expected_pattern = re.compile(pattern, flags)
        actual_pattern = module.compile(pattern, flags)
        expected_digest = hashlib.sha256()
        actual_digest = hashlib.sha256()
        visited = 0
        initial_failures = len(failures)
        for codepoint in range(0, CODEPOINTS, stride):
            subject = chr(codepoint)
            expected_match = expected_pattern.fullmatch(subject)
            expected = (
                expected_match.lastindex if expected_match is not None else 0
            )
            try:
                actual_match = actual_pattern.fullmatch(subject)
                actual = (
                    actual_match.lastindex if actual_match is not None else 0
                )
            except Exception as error:
                actual = {
                    "error": type(error).__name__,
                    "message": str(error),
                }
            expected_digest.update(bytes((expected,)))
            if isinstance(actual, int) and 0 <= actual <= 255:
                actual_digest.update(bytes((actual,)))
            else:
                actual_digest.update(b"\xff")
            checks += 1
            visited += 1
            if actual != expected:
                add_failure(
                    failures,
                    "full-plane",
                    expected,
                    actual,
                    partition=label,
                    pattern=pattern,
                    flags=int(flags),
                    codepoint=codepoint,
                    unicode=f"U+{codepoint:04X}",
                )
            if visited % 262144 == 0:
                print(
                    f"{label}: checked {visited} codepoints; "
                    f"failures={len(failures) - initial_failures}",
                    flush=True,
                )
        result = {
            "name": label,
            "flags": int(flags),
            "codepoints_checked": visited,
            "expected_sha256": expected_digest.hexdigest(),
            "actual_sha256": actual_digest.hexdigest(),
            "failed": len(failures) - initial_failures,
        }
        results.append(result)
        print(json.dumps(result, sort_keys=True), flush=True)
    return results, checks


def check_case(module, label, pattern, subject, flags, failures):
    checks = 0
    expected_compilation = attempted(lambda: re.compile(pattern, flags))
    actual_compilation = attempted(lambda: module.compile(pattern, flags))
    if "error" in expected_compilation or "error" in actual_compilation:
        checks += 1
        if expected_compilation != actual_compilation:
            add_failure(
                failures,
                "compile",
                expected_compilation,
                actual_compilation,
                label=label,
                pattern=pattern,
                subject=subject,
                flags=int(flags),
            )
        return checks

    expected_pattern = expected_compilation["value"]
    actual_pattern = actual_compilation["value"]
    length = subject_length(subject)
    windows = (
        (0, length),
        (min(1, length), length),
        (0, max(0, length - 1)),
        (min(3, length), max(0, length - 2)),
    )
    for pos, endpos in windows:
        operations = (
            ("search", lambda item: snapshot(item.search(subject, pos, endpos))),
            ("match", lambda item: snapshot(item.match(subject, pos, endpos))),
            (
                "fullmatch",
                lambda item: snapshot(item.fullmatch(subject, pos, endpos)),
            ),
            ("findall", lambda item: item.findall(subject, pos, endpos)),
            (
                "finditer",
                lambda item: [
                    snapshot(match)
                    for match in itertools.islice(
                        item.finditer(subject, pos, endpos), 512
                    )
                ],
            ),
            (
                "scanner-search",
                lambda item: scanner_results(item, subject, pos, endpos, False),
            ),
            (
                "scanner-match",
                lambda item: scanner_results(item, subject, pos, endpos, True),
            ),
        )
        for operation, action in operations:
            expected = attempted(lambda: action(expected_pattern))
            actual = attempted(lambda: action(actual_pattern))
            checks += 1
            if actual != expected:
                add_failure(
                    failures,
                    "unicode-api",
                    expected,
                    actual,
                    label=label,
                    operation=operation,
                    pattern=pattern,
                    subject=subject,
                    flags=int(flags),
                    pos=pos,
                    endpos=endpos,
                )

    replacement = b"<\\g<0>>" if isinstance(pattern, bytes) else r"<\g<0>>"
    collections = (
        ("split", lambda item: item.split(subject)),
        ("split-limited", lambda item: item.split(subject, 3)),
        ("sub", lambda item: item.sub(replacement, subject)),
        ("sub-limited", lambda item: item.sub(replacement, subject, 3)),
        ("subn", lambda item: item.subn(replacement, subject)),
        ("subn-limited", lambda item: item.subn(replacement, subject, 3)),
    )
    for operation, action in collections:
        expected = attempted(lambda: action(expected_pattern))
        actual = attempted(lambda: action(actual_pattern))
        checks += 1
        if actual != expected:
            add_failure(
                failures,
                "unicode-api",
                expected,
                actual,
                label=label,
                operation=operation,
                pattern=pattern,
                subject=subject,
                flags=int(flags),
            )
    return checks


def scanner_results(pattern, subject, pos, endpos, anchored):
    scanner = pattern.scanner(subject, pos, endpos)
    operation = scanner.match if anchored else scanner.search
    result = []
    for _ in range(16):
        match = operation()
        result.append(snapshot(match))
        if match is None:
            break
    return result


def manual_cases():
    rows = [
        (r"\d+|\s+|\w+|\W+", "A\x1c\x1d\x1e\x1f ٣９雪😀\ud800", 0),
        (r"(?a:\d+|\s+|\w+|\W+)", "A\x1c\x1f ٣９雪😀", 0),
        (r"\b\w+\b", "café Straße İıſK ٣٣ 雪_1 😀", 0),
        (r"\B\w+\B", "_Straße_ café123 雪山 İi", 0),
        (r"(?a:\b\w+\b)|(?u:\b\w+\b)", "café 雪_1 İıſK", 0),
        (r"[a-z]+", "abc ABC İıſK Straße 雪", re.IGNORECASE),
        (r"[A-Z]+", "abc ABC İıſK Straße 雪", re.IGNORECASE),
        (r"[^a-z\s]+", "abc İıſK ٣９雪😀", re.IGNORECASE),
        (r"[\xc0-\xde]+", "Àà Þþ × ßẞ", re.IGNORECASE),
        (r"[\u0391-\u03a9]+", "Αα Ββ Σςσ µμ", re.IGNORECASE),
        (r"[\u0400-\u042f]+", "Ввᲀ Ддᲁ Ттᲄᲅ", re.IGNORECASE),
        (
            r"[\U00010400-\U00010427]+",
            "\U00010400\U00010428 \U00010427\U0001044f",
            re.IGNORECASE,
        ),
        (r"(?i:[a-z]+)(?-i:[A-Z]+)", "abcDEF İxYY ABCdef", 0),
        (r"(?a:[a-z]+)|(?u:[a-z]+)", "ſ K İ ı ABC", re.IGNORECASE),
        (r"(?P<word>\w+)[-](?P=word)", "café-café 雪-雪 abc-ABC", 0),
        (
            r"(?P<word>\w+)[-](?P=word)",
            "ABC-abc İ-i K-k ſ-s Σ-ς",
            re.IGNORECASE,
        ),
        (r"(?P<雪>[\w\u0301]+)", "café e\u0301 雪_1", 0),
        (r"(?<!雪)\w+(?=★)", "雪abc★ xété★ ٣٣★", 0),
        (r"(?<=\w)\B(?=\w)", "café 雪山 A٣", 0),
        (r"(?:é|ß|雪){0,3}?\w", "éß雪a ßé 雪_", 0),
        (r"(?m)^\s*(?P<word>\w+)\s*$", "café\n 雪_1 \n٣٣\n", 0),
        (r"(?ms)^.*?$", "café\n雪\n😀\n", 0),
        (r"\A(?:café|雪|😀)+\Z", "café雪😀", 0),
        (r"\N{SNOWMAN}+|\N{KELVIN SIGN}+", "☃☃ K K", re.IGNORECASE),
        (r"[😀-🙏]+|[^😀-🙏]+", "a😀😁🙏雪\ud800", 0),
        (r"\ud800|\udfff|[\U00010000-\U0010ffff]", "\ud800\udfff😀", 0),
        (r"\x00|\x1c|\x1f|\u0085|\u2028|\u2029", "\x00\x1c\x1f\x85\u2028\u2029", 0),
        (r"(?:\b|\B)", "café 雪 😀", 0),
        (r"(?i)(?:ki|kin|kind|skip|skin)", "KI KI ſkin İin kind", 0),
        (r"(?i)(?:ss|ß|ẞ)", "SS ss ß ẞ Straße", 0),
    ]
    byte_rows = [
        (rb"\d+|\s+|\w+|\W+", bytes(range(256)), 0),
        (rb"[a-z]+|[^a-z]+", bytes(range(256)), re.IGNORECASE),
        (rb"\b\w+\b", b"abc_123 \xffABC-009\x1c", 0),
        (rb"(?a:\w+)|\W+", b"caf\xe9 _123 \xff", 0),
        (rb"(?i:[a-z]+)(?-i:[A-Z]+)", b"abcDEF ABCdef", 0),
        (rb"(?P<word>\w+)-(?P=word)", b"abc-abc ABC-abc", re.IGNORECASE),
        (rb"(?m)^\s*(\w+)\s*$", b"alpha\n beta_1\n\xff\n", 0),
        (rb"[\x80-\xff]+|[\x00-\x1f]+", bytes(range(256)), 0),
    ]
    for pattern, subject, flags in byte_rows:
        rows.append((pattern, subject, flags))
        rows.append((pattern, bytearray(subject), flags))
        rows.append((pattern, memoryview(subject), flags))
    return rows


def generated_case(rng, index):
    flags = rng.choice(
        (0, re.ASCII, re.IGNORECASE, re.ASCII | re.IGNORECASE, re.MULTILINE)
    )
    family = index % 9
    alphabet = (
        "aAzZ09_,-. \t\n\x1c\x1f"
        "éßẞİıſKΩΣςВвᲀ٣９雪\u0301\u2003☃★😀🙏\ud800"
    )
    if family == 0:
        pattern = rng.choice((r"\d+", r"\D+", r"\s+", r"\S+", r"\w+", r"\W+"))
    elif family == 1:
        pattern = rng.choice(
            (
                r"[a-z]{1,8}",
                r"[^a-z\s]{1,8}",
                r"[\xc0-\xde]+",
                r"[\u0391-\u03a9]+",
                r"[\u0400-\u042f]+",
                r"[\U00010400-\U00010427]+",
            )
        )
        flags |= re.IGNORECASE
    elif family == 2:
        pattern = rng.choice((r"\b\w+\b", r"\B\w+\B", r"(?<=\w)\B(?=\w)", r"\b|\B"))
    elif family == 3:
        pattern = rng.choice(
            (
                r"(?P<word>\w+)-(?P=word)",
                r"(?P<outer>(?P<inner>\w){1,5})",
                r"(?<!雪)\w+(?=★)",
                r"(?P<a>雪)?(?(a)\w|\d)",
            )
        )
    elif family == 4:
        flags |= re.MULTILINE
        pattern = rng.choice((r"^\w+$", r"^\s*\w+\s*$", r"\A\w+", r"\w+\Z", r"^|$"))
    elif family == 5:
        pattern = rng.choice(
            (
                r"(?i:[a-z]+)(?-i:[A-Z]+)",
                r"(?a:\w+)|(?u:\w+)",
                r"(?i:ki|kin|kind|skip|skin)",
                r"(?i:[\u0400-\u042f]+)",
            )
        )
    elif family == 6:
        pattern = rng.choice(
            (
                r"\N{SNOWMAN}+",
                r"\N{KELVIN SIGN}+",
                r"[😀-🙏]+",
                r"\ud800|\udfff",
                r"(?:é|ß|雪){0,3}?\w",
            )
        )
    elif family == 7:
        pattern = rng.choice(
            (
                rb"\d+|\s+|\w+|\W+",
                rb"[a-z]+|[^a-z]+",
                rb"\b\w+\b",
                rb"(?P<word>\w+)-(?P=word)",
                rb"[\x80-\xff]+",
            )
        )
        flags &= ~re.UNICODE
        payload = bytes(rng.randrange(256) for _ in range(rng.randrange(0, 72)))
        variant = (index // 9) % 3
        subject = (
            payload
            if variant == 0
            else bytearray(payload)
            if variant == 1
            else memoryview(payload)
        )
        return pattern, subject, flags
    else:
        pattern = rng.choice((r"(?:\w|\W)*?", r"\s*", r"(?:é|雪|😀)?", r"(?=\w)", r"(\b|\B)"))
    subject = "".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 73)))
    return pattern, subject, flags


def check_equivalences(module, failures):
    checks = 0
    for group in CASE_EQUIVALENCES:
        for left in group:
            escaped = rf"\u{left:04x}" if left <= 0xFFFF else rf"\U{left:08x}"
            patterns = (
                (escaped, re.IGNORECASE),
                (f"[19{escaped}]", re.IGNORECASE),
                (f"[{escaped}-{escaped}]", re.IGNORECASE),
                (f"(?i:{escaped})", 0),
                (f"(?a:{escaped})", re.IGNORECASE),
            )
            for right in group:
                subject = chr(right)
                for pattern, flags in patterns:
                    expected = attempted(
                        lambda: snapshot(re.compile(pattern, flags).fullmatch(subject))
                    )
                    actual = attempted(
                        lambda: snapshot(
                            module.compile(pattern, flags).fullmatch(subject)
                        )
                    )
                    checks += 1
                    if actual != expected:
                        add_failure(
                            failures,
                            "case-equivalence",
                            expected,
                            actual,
                            pattern=pattern,
                            flags=int(flags),
                            left=f"U+{left:04X}",
                            right=f"U+{right:04X}",
                        )

    extra_checks = 0
    for left, equivalents in sorted(_EXTRA_CASES.items()):
        escaped = rf"\u{left:04x}" if left <= 0xFFFF else rf"\U{left:08x}"
        patterns = (
            (escaped, re.IGNORECASE),
            (f"[19{escaped}]", re.IGNORECASE),
            (f"[{escaped}-{escaped}]", re.IGNORECASE),
            (f"(?i:{escaped})", 0),
            (f"(?a:{escaped})", re.IGNORECASE),
        )
        for right in equivalents:
            subject = chr(right)
            for pattern, flags in patterns:
                expected = attempted(
                    lambda: snapshot(re.compile(pattern, flags).fullmatch(subject))
                )
                actual = attempted(
                    lambda: snapshot(module.compile(pattern, flags).fullmatch(subject))
                )
                checks += 1
                extra_checks += 1
                if actual != expected:
                    add_failure(
                        failures,
                        "cpython-extra-case",
                        expected,
                        actual,
                        pattern=pattern,
                        flags=int(flags),
                        left=f"U+{left:04X}",
                        right=f"U+{right:04X}",
                    )
    return checks, extra_checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", default="candidates.rust_candidate")
    parser.add_argument("--output", required=True)
    parser.add_argument("--seeded-cases", type=int, default=4096)
    parser.add_argument("--membership-stride", type=int, default=1)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    if args.seeded_cases < 0:
        parser.error("--seeded-cases must not be negative")
    if args.membership_stride < 1:
        parser.error("--membership-stride must be at least one")

    module = importlib.import_module(args.module)
    failures = []
    membership, checks = full_plane(module, args.membership_stride, failures)
    manual = manual_cases()
    manual_checks = 0
    for index, (pattern, subject, flags) in enumerate(manual):
        manual_checks += check_case(
            module, f"manual-{index}", pattern, subject, flags, failures
        )
    checks += manual_checks

    rng = random.Random(args.seed)
    generated_checks = 0
    for index in range(args.seeded_cases):
        pattern, subject, flags = generated_case(rng, index)
        generated_checks += check_case(
            module, f"seeded-{index}", pattern, subject, flags, failures
        )
        if index and index % 1024 == 0:
            print(f"seeded: checked {index}/{args.seeded_cases}", flush=True)
    checks += generated_checks
    equivalence_checks, extra_case_checks = check_equivalences(module, failures)
    checks += equivalence_checks

    result = {
        "schema": "rebar-rust-unicode-probe-v1",
        "module": args.module,
        "oracle": "CPython stdlib re",
        "python_unicode_version": unicodedata.unidata_version,
        "seed": args.seed,
        "unicode_codepoints": CODEPOINTS,
        "membership_stride": args.membership_stride,
        "membership_partitions": membership,
        "manual_cases": len(manual),
        "manual_checks": manual_checks,
        "seeded_cases": args.seeded_cases,
        "seeded_checks": generated_checks,
        "case_equivalence_groups": len(CASE_EQUIVALENCES),
        "case_equivalence_checks": equivalence_checks,
        "cpython_extra_case_keys": len(_EXTRA_CASES),
        "cpython_extra_case_links": sum(map(len, _EXTRA_CASES.values())),
        "cpython_extra_case_checks": extra_case_checks,
        "correctness_checks": checks,
        "failed": len(failures),
        "failures": failures,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                key: value
                for key, value in result.items()
                if key not in {"failures", "membership_partitions"}
            },
            sort_keys=True,
        ),
        flush=True,
    )
    for failure in failures[:20]:
        print(
            json.dumps(failure, ensure_ascii=True, sort_keys=True), flush=True
        )
    raise SystemExit(bool(failures))


if __name__ == "__main__":
    main()
