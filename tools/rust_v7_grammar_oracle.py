#!/usr/bin/env python3
"""Frozen, independently seeded, crash-isolated CPython regex grammar oracle.

No benchmark, performance fixture, holdout, or external regex package is read.
The standard-library regex engine is imported only by an explicit ``re`` oracle
worker. Each candidate is imported in its own isolated child process.
"""

from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import importlib
import itertools
import json
import pathlib
import platform
import random
import subprocess
import sys
import warnings


ROOT = pathlib.Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "candidates" / "evidence"
SCHEMA = "rebar-independent-parser-grammar-fuzz-v1"
SEED = 0x52454241525F4752414D4D4152
PINNED_PYTHON = (3, 14, 6)
PER_FAMILY = 1_280
FIXTURE_SHA256 = "f2b0e9bfaa7dedacdf201e66499019f30860050b75dd722310f27bb1c79e35dd"
ORACLE_SHA256 = "740e4602f67fa1cfc1ba65d176453009470316a5653cceb19b3c62853a7faab7"
I, M, S, X, A = 2, 8, 16, 64, 256
CANDIDATES = (
    ("ast", "candidates.ast_candidate", "ast_candidate", 5_573),
    ("native", "candidates.vm_candidate", "vm_candidate", 5_587),
    ("rust", "candidates.rust_candidate", "rust_candidate", 5_535),
    ("zig", "candidates.zig_candidate", "zig_candidate", 279),
)
FAMILIES = (
    "quantified-positive-lookahead",
    "quantified-negative-lookahead",
    "quantified-positive-lookbehind",
    "quantified-negative-lookbehind",
    "nested-capture-conditionals",
    "conditional-error-offsets",
    "scoped-inline-flags",
    "invalid-inline-flags",
    "verbose-comments-and-escapes",
    "bytes-named-backreferences",
    "bytes-error-offsets",
    "atomic-ordered-alternation",
    "possessive-repeat-captures",
    "lookbehind-backreference-width",
    "nullable-branch-captures",
    "escape-and-character-class-errors",
)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))


def sha256(path):
    digest = hashlib.sha256()
    with pathlib.Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1_048_576), b""):
            digest.update(block)
    return digest.hexdigest()


def check_python():
    if tuple(sys.version_info[:3]) != PINNED_PYTHON:
        raise RuntimeError(f"requires pinned CPython {PINNED_PYTHON}; got {sys.version}")


def encode_domain(value):
    if isinstance(value, bytes):
        return {"kind": "bytes", "hex": value.hex()}
    return {"kind": "str", "value": value}


def decode_domain(value):
    if value["kind"] == "bytes":
        return bytes.fromhex(value["hex"])
    if value["kind"] == "str":
        return value["value"]
    raise ValueError(f"unknown grammar domain: {value['kind']!r}")


def normalise(value):
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (bytes, bytearray, memoryview)):
        return {"kind": type(value).__name__, "hex": bytes(value).hex()}
    if isinstance(value, tuple):
        return {"tuple": [normalise(item) for item in value]}
    if isinstance(value, list):
        return [normalise(item) for item in value]
    if isinstance(value, dict):
        return {
            str(key): normalise(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    return {"kind": type(value).__name__, "repr": repr(value)}


def short_word(rng):
    return "".join(rng.choice("abcxyz") for _ in range(rng.randrange(1, 6)))


def text_subject(rng, token="a"):
    atoms = ("", "a", "b", "ab", "ba", "x", "\n", "1", "_", "é", "İ", "ß")
    return rng.choice(atoms) + token + rng.choice(atoms) + rng.choice(atoms)


def byte_subject(rng, token=b"a"):
    atoms = (b"", b"a", b"b", b"ab", b"ba", b"x", b"\n", b"1", b"_", b"\x80", b"\xff")
    return rng.choice(atoms) + token + rng.choice(atoms) + rng.choice(atoms)


def quantified_case(family, rng, name):
    behind = "lookbehind" in family
    negative = "negative" in family
    prefix = "?<!" if behind and negative else "?<=" if behind else "?!" if negative else "?="
    if behind:
        inner = rng.choice(("a", "b", "[ab]", ".", "(?i:a)", "(?:a|b)", f"(?P<{name}>a)"))
    else:
        inner = rng.choice((
            "a", "b", "[ab]", ".", r"\d", "(?:a|ab)",
            f"(?P<{name}>a)", "(?i:a)", "(?=a)", "(?!z)",
        ))
    quantifier = rng.choice(("*", "+", "?", "{0}", "{1}", "{2}", "{0,1}", "{1,3}", "{2,4}"))
    quantifier += rng.choice(("", "?", "+"))
    assertion = "(" + prefix + inner + ")" + quantifier
    shape = rng.randrange(6)
    if shape == 0:
        pattern = assertion
    elif shape == 1:
        pattern = assertion + rng.choice(("a", "b", "", "(?:a|)", r"\b"))
    elif shape == 2:
        pattern = "(?:" + assertion + ")" + rng.choice(("", "a", "b"))
    elif shape == 3:
        pattern = rng.choice(("a", "", r"\b")) + assertion + rng.choice(("", "a"))
    elif shape == 4:
        pattern = "(" + assertion + ")" + rng.choice(("", "a"))
    else:
        pattern = "(?:" + assertion + "|" + rng.choice(("a", "b", "")) + ")"
    flags = rng.choice((0, I, M, S, I | M, A, A | I))
    return pattern, text_subject(rng, rng.choice(("a", "b", "ab", "1"))), flags


def make_case(family, rng, index):
    name = "g" + short_word(rng) + str(rng.randrange(0, 4096))
    word = short_word(rng)
    if family.startswith("quantified-"):
        pattern, subject, flags = quantified_case(family, rng, name)
    elif family == "nested-capture-conditionals":
        patterns = (
            f"(?P<{name}>a)?(?(" + name + ")b|c)",
            f"((?P<{name}>a)?b)(?({name})c|d)",
            f"(?:(?P<{name}>a)|b)(?({name})c|d)",
            f"(?P<{name}>a(b)?)?(?({name})(c|d)|e)",
            f"(?=(?P<{name}>a))(?({name})a|b)",
            f"(?P<{name}>(a|ab))(?({name})b|c)",
            f"(?:(?P<{name}>a)?)*?(?({name})b|c)",
            f"(?P<{name}>a)?(?({name})(?=b)b|(?!b)c)",
        )
        pattern, subject, flags = rng.choice(patterns), text_subject(rng, rng.choice(("ab", "c", "abd", "ac"))), rng.choice((0, I, M))
    elif family == "conditional-error-offsets":
        bad = rng.choice((
            "(?(missing)a|b)", "(?(0)a|b)", "(?(999)a|b)", "(?(1)a|b)",
            "(?(name)a|b|c)", "(?(<x>)a|b)", "(?(=a)b|c)", "(?(?=a)b|c)",
            "(?(a)", "(?(a)a|", "(?(a)a|b", "(?(a)a|b|c)",
        ))
        pattern = rng.choice(("", word, "(?:", "(?i:")) + bad + rng.choice(("", "x", ")"))
        subject, flags = text_subject(rng, word), rng.choice((0, I, M, X))
    elif family == "scoped-inline-flags":
        local = rng.choice(("i", "m", "s", "x", "a", "im", "is", "ms", "ix", "a-i", "i-m", "im-s"))
        core = rng.choice(("a", "A", ".", "[a-z]", r"\w", "a b", "(?:a|A)", "(?-i:a)"))
        pattern = rng.choice(("", "a?", "(?:b|)")) + f"(?{local}:{core})" + rng.choice(("", "A", "(?i:a)", "(?-i:A)"))
        subject, flags = text_subject(rng, rng.choice(("a", "A", "ab", "a b"))), rng.choice((0, I, M, S, X, A))
    elif family == "invalid-inline-flags":
        bad = rng.choice((
            "(?i)", "(?m)", "(?s)", "(?x)", "(?a)", "(?u)", "(?L)", "(?z)",
            "(?i-)", "(?-i)", "(?i-a:a)", "(?a-u:a)", "(?au:a)", "(?i::a)",
            "(?i", "(?i:", "(?-:a)", "(?i--m:a)", "(?u-a:a)", "(?L:a)",
        ))
        pattern = rng.choice(("a", "(?:a)", word, "a|", "")) + bad + rng.choice(("", "a", word, ")"))
        subject, flags = text_subject(rng, word), rng.choice((0, I, M, X, A))
    elif family == "verbose-comments-and-escapes":
        token = rng.choice(("a", "b", word))
        patterns = (
            f"(?x) {token} [ ] b",
            f"(?x:{token} \\# b)",
            f"(?x:{token} # comment {word}\n b)",
            f"(?x) (?P<{name}> {token} ) \\s* (?P={name})",
            f"(?x) [a # b] + \\# ?",
            f"(?x:{token} (?-x: ) b)",
            f"(?x) (?: {token} | b ) {{ 1,2 }}",
            f"(?x) {token} \\ \\# comment {word}\n b",
        )
        pattern, subject, flags = rng.choice(patterns), text_subject(rng, rng.choice((token, token + " b", token + token, "a#b"))), rng.choice((0, M, I))
    elif family == "bytes-named-backreferences":
        byte_name = name.encode("ascii")
        patterns = (
            b"(?P<" + byte_name + b">a)(?P=" + byte_name + b")",
            b"(?P<" + byte_name + b">[a-z]+)(?P=" + byte_name + b")",
            b"(?:(?P<" + byte_name + b">a)|b)(?(" + byte_name + b")a|b)",
            b"(?=(?P<" + byte_name + b">a)){2}a",
            b"(?P<" + byte_name + b">a)?(?(" + byte_name + b")b|c)",
            b"(?i:(?P<" + byte_name + b">a))(?P=" + byte_name + b")",
            b"(?P<" + byte_name + b">[\\x80-\\xff]+)(?P=" + byte_name + b")",
            b"(a)(b)\\2\\1",
        )
        pattern, subject, flags = rng.choice(patterns), byte_subject(rng, rng.choice((b"a", b"aa", b"abba", b"\x80\x80"))), rng.choice((0, I, M, S, A))
    elif family == "bytes-error-offsets":
        bad = rng.choice((
            b"(?P<\xff>a)", b"(?P<\x80>a)", b"(?P<>a)", b"(?P<1x>a)",
            b"(?P<x>a)(?P<x>b)", b"(?P=x)", b"\\u1234", b"\\U00000041",
            b"\\N{LATIN SMALL LETTER A}", b"\\x", b"\\x1", b"\\xGG",
            b"[\\u1234]", b"(?u:a)", b"(?au:a)", b"(?P<ab",
        ))
        pattern = rng.choice((b"", word.encode("ascii"), b"(?:")) + bad + rng.choice((b"", b"x", b")"))
        subject, flags = byte_subject(rng), rng.choice((0, I, M, S, A))
    elif family == "atomic-ordered-alternation":
        patterns = (
            "(?>a|ab)b", "(?>ab|a)b", "(?>a*)a", "(?>a+?)a",
            "(?>(a)|(ab))b", "(?>(a|ab))b", "(?>a|)a",
            "(?>(?=a)a|ab)b", f"(?>(?P<{name}>a)|ab)b",
            "((?>a|ab)b|ab)", "(?>a(?>b|bc))c", "(?>(?:a|aa){1,3})a",
        )
        pattern, subject, flags = rng.choice(patterns), text_subject(rng, rng.choice(("a", "ab", "aab", "abb", "abc"))), rng.choice((0, I, M, S))
    elif family == "possessive-repeat-captures":
        atom = rng.choice(("a", "(?:a|aa)", "(a)", "(?:a?)", "[ab]", ".", r"\w"))
        quantifier = rng.choice(("*+", "++", "?+", "{0,2}+", "{1,3}+", "{2}+", "{0}+"))
        pattern = rng.choice(("", "(?:", "(")) + atom + quantifier + rng.choice(("a", "b", "", r"\b"))
        if pattern.startswith("(?:") or pattern.startswith("(") and not pattern.startswith("(a)"):
            pattern += ")"
        subject, flags = text_subject(rng, rng.choice(("a", "aa", "aaa", "ab"))), rng.choice((0, I, M, S))
    elif family == "lookbehind-backreference-width":
        patterns = (
            r"(a)(?<=\1)b", r"(ab)(?<=\1)c", r"(a|b)(?<=\1)c",
            r"(a?)(?<=\1)b", r"(a+)(?<=\1)b", r"(?<=(a))\1",
            f"(?P<{name}>a)(?<=(?P={name}))b",
            f"(?P<{name}>a+)(?<=(?P={name}))b",
            r"(?<=(?:a|b))c", r"(?<=(?:a|bc))d",
            r"(?<=a{2})b", r"(?<=a{1,2})b",
            r"(?<!a{2})b", r"(?<!a{1,2})b",
        )
        pattern, subject, flags = rng.choice(patterns), text_subject(rng, rng.choice(("ab", "abc", "aac", "aab", "b"))), rng.choice((0, I, M))
    elif family == "nullable-branch-captures":
        patterns = (
            "(|a)*", "(a?)*", "((a)?)*", "((a)|)*", "(?:|a)+?",
            "((?=a)|a)*", "((?!z)|a)+", "(?:(a)?|b)*?",
            "((a)?){0,3}", "((?:a|){1,2})*", "(?:(a)|(b)|)*",
            f"(?:(?P<{name}>a)?)*?(?({name})b|c)",
            "(?:a?)*+a", "(?:(a)|)*+", "(|(?:a|))*?",
        )
        pattern, subject, flags = rng.choice(patterns), text_subject(rng, rng.choice(("", "a", "aa", "ab", "c"))), rng.choice((0, I, M))
    elif family == "escape-and-character-class-errors":
        bad = rng.choice((
            "\\", r"\x", r"\x1", r"\xGG", r"\u", r"\u12", r"\uGGGG",
            r"\U00110000", r"\N{}", r"\N{", r"\N{NOT A CHARACTER}",
            r"\8", r"\9", r"\11", r"\400", r"\777",
            "[", "[]", "[z-a]", r"[\x]", r"[\8]", "[a-", "[a--b]",
            "*", "+", "?", "{1,2}*", "a**", "a++?", "a{2,1}",
            "(?", "(?P<", "(?P=", "(?z)", "(?<=a+)", "(?<!a*)",
        ))
        pattern = rng.choice(("", word, "(?:")) + bad + rng.choice(("", "x", ")"))
        subject, flags = text_subject(rng, word), rng.choice((0, I, M, S, X, A))
    else:
        raise ValueError(f"unfrozen grammar family: {family}")
    return {
        "id": f"{family}:{index:05d}",
        "family": family,
        "pattern": encode_domain(pattern),
        "subject": encode_domain(subject),
        "flags": int(flags),
    }


def generated_cases():
    rng = random.Random(SEED)
    seen = set()
    for family in FAMILIES:
        index = 0
        attempts = 0
        while index < PER_FAMILY:
            attempts += 1
            if attempts > PER_FAMILY * 100:
                raise RuntimeError(f"could not regenerate distinct grammar cases: {family}")
            case = make_case(family, rng, index)
            key = canonical((family, case["pattern"], case["subject"], case["flags"]))
            if key in seen:
                continue
            seen.add(key)
            yield case
            index += 1


def fixture_digest():
    digest = hashlib.sha256()
    count = 0
    for case in generated_cases():
        digest.update((canonical(case) + "\n").encode("ascii"))
        count += 1
    return count, digest.hexdigest()


def json_lines(path):
    with pathlib.Path(path).open("r", encoding="utf-8") as source:
        for line in source:
            if line.strip():
                yield json.loads(line)


def json_file(path):
    with pathlib.Path(path).open("r", encoding="utf-8") as source:
        return json.load(source)


def archive(path, fields, arrays=()):
    """Write canonical streaming JSON in deterministic, filename-free gzip."""
    array_fields = dict(arrays)
    if set(fields) & set(array_fields):
        raise ValueError("duplicate compressed archive field")
    payload_digest = hashlib.sha256()
    with pathlib.Path(path).open("wb") as target:
        with gzip.GzipFile(filename="", fileobj=target, mode="wb", compresslevel=6, mtime=0) as compressed:
            def emit(piece):
                data = piece.encode("ascii")
                compressed.write(data)
                payload_digest.update(data)

            emit("{")
            for field_index, name in enumerate(sorted(set(fields) | set(array_fields))):
                if field_index:
                    emit(",")
                emit(canonical(name))
                emit(":")
                if name not in array_fields:
                    emit(canonical(fields[name]))
                    continue
                emit("[")
                for row_index, row in enumerate(array_fields[name]()):
                    if row_index:
                        emit(",")
                    emit(canonical(row))
                emit("]")
            emit("}\n")
    return {
        "file": pathlib.Path(path).name,
        "sha256": sha256(path),
        "uncompressed_sha256": payload_digest.hexdigest(),
        "compressed_bytes": pathlib.Path(path).stat().st_size,
        "gzip_level": 6,
        "gzip_mtime": 0,
        "gzip_filename": "",
    }


def assert_source_fixture(source):
    manifest = json_file(source / "manifest.json")
    count, regenerated = fixture_digest()
    if count != len(FAMILIES) * PER_FAMILY or regenerated != FIXTURE_SHA256:
        raise RuntimeError("seeded committed grammar generator does not reproduce the frozen fixture")
    if (
        manifest.get("schema") != SCHEMA
        or manifest.get("seed") != SEED
        or manifest.get("cases") != count
        or manifest.get("cases_per_family") != PER_FAMILY
        or manifest.get("families") != list(FAMILIES)
        or manifest.get("fixture_sha256") != FIXTURE_SHA256
        or sha256(source / "cases.jsonl") != FIXTURE_SHA256
    ):
        raise RuntimeError("source grammar fixture is not the original frozen 20,480-case corpus")
    return manifest


def validate_self(source, manifest):
    report = json_file(source / "self-oracle.json")
    left = source / "oracle-a.jsonl"
    right = source / "oracle-b.jsonl"
    if (
        report.get("self_oracle_failures") != 0
        or report.get("cases") != manifest["cases"]
        or report.get("valid_grammars") != 14_818
        or report.get("invalid_grammars_retained") != 5_662
        or report.get("fixture_sha256") != FIXTURE_SHA256
        or report.get("pass_a", {}).get("sha256") != ORACLE_SHA256
        or report.get("pass_b", {}).get("sha256") != ORACLE_SHA256
        or sha256(left) != ORACLE_SHA256
        or sha256(right) != ORACLE_SHA256
    ):
        raise RuntimeError("the complete, twice-run CPython self-oracle is not exact")
    for index, (case, first, second) in enumerate(
        itertools.zip_longest(json_lines(source / "cases.jsonl"), json_lines(left), json_lines(right)), 1
    ):
        if case is None or first is None or second is None:
            raise RuntimeError(f"the grammar self-oracle changed its denominator at row {index}")
        if first != second or first.get("id") != case["id"] or first.get("family") != case["family"]:
            raise RuntimeError(f"the CPython self-oracle is unstable at row {index}")
    return report


def validate_candidate(source, manifest, label, module, slug, expected_mismatches):
    report = json_file(source / (slug + "-report.json"))
    actual_path = source / (slug + "-actual.jsonl")
    mismatch_path = source / (slug + "-mismatches.jsonl")
    if (
        report.get("module") != module
        or report.get("cases") != manifest["cases"]
        or report.get("mismatches") != expected_mismatches
        or report.get("matches") != manifest["cases"] - expected_mismatches
        or report.get("crashes") != 0
        or report.get("timeouts") != 0
        or report.get("fixture_sha256") != FIXTURE_SHA256
        or report.get("source_hashes") != manifest["source_hashes"]
        or report.get("actual", {}).get("sha256") != sha256(actual_path)
        or report.get("mismatch_evidence_sha256") != sha256(mismatch_path)
    ):
        raise RuntimeError(f"the complete original {label} baseline changed")
    category_counts = collections.Counter()
    mismatch_rows = json_lines(mismatch_path)
    observed_mismatches = 0
    for index, (case, expected, actual) in enumerate(
        itertools.zip_longest(
            json_lines(source / "cases.jsonl"),
            json_lines(source / "oracle-a.jsonl"),
            json_lines(actual_path),
        ), 1
    ):
        if case is None or expected is None or actual is None:
            raise RuntimeError(f"{label} changed the frozen denominator at row {index}")
        if case["id"] != expected.get("id") or case["id"] != actual.get("id"):
            raise RuntimeError(f"{label} changed frozen case order at row {index}")
        if expected["observation"] == actual["observation"]:
            continue
        observed_mismatches += 1
        category_counts[case["family"]] += 1
        record = next(mismatch_rows, None)
        if (
            record is None
            or record.get("case") != case
            or record.get("candidate") != module
            or record.get("expected") != expected["observation"]
            or record.get("actual") != actual["observation"]
        ):
            raise RuntimeError(f"{label} mismatch was omitted or changed at frozen row {index}")
    if next(mismatch_rows, None) is not None:
        raise RuntimeError(f"{label} contains extra mismatch evidence")
    if (
        observed_mismatches != expected_mismatches
        or dict(sorted(category_counts.items())) != report.get("mismatches_by_family")
    ):
        raise RuntimeError(f"{label} mismatch totals or family denominators changed")
    return report


def command_regenerate(args):
    check_python()
    target = pathlib.Path(args.output)
    digest = hashlib.sha256()
    with target.open("x", encoding="ascii", newline="\n") as output:
        for case in generated_cases():
            line = canonical(case) + "\n"
            output.write(line)
            digest.update(line.encode("ascii"))
    if digest.hexdigest() != FIXTURE_SHA256:
        raise RuntimeError("regenerated fixture does not match the frozen SHA-256")
    print(canonical({
        "schema": SCHEMA,
        "seed": SEED,
        "python": platform.python_version(),
        "cases": len(FAMILIES) * PER_FAMILY,
        "families": len(FAMILIES),
        "cases_per_family": PER_FAMILY,
        "fixture_sha256": digest.hexdigest(),
        "output": str(target),
    }), flush=True)


def command_bundle(args):
    check_python()
    source = pathlib.Path(args.source).resolve()
    target = pathlib.Path(args.evidence_dir).resolve()
    if target != EVIDENCE.resolve():
        raise RuntimeError("grammar baseline archives may only be written to candidates/evidence")
    manifest = assert_source_fixture(source)
    self_report = validate_self(source, manifest)
    validated = []
    for label, module, slug, count in CANDIDATES:
        validated.append((label, module, slug, validate_candidate(source, manifest, label, module, slug, count)))

    shared = {
        "schema": SCHEMA,
        "seed": SEED,
        "python": platform.python_version(),
        "fixture_sha256": FIXTURE_SHA256,
        "oracle_sha256": ORACLE_SHA256,
        "cases": manifest["cases"],
        "families": list(FAMILIES),
        "source_hashes": manifest["source_hashes"],
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "external_regex_packages": 0,
    }
    artifacts = []
    name = "rust-v7-grammar-fixture.json.gz"
    artifacts.append(archive(
        target / name,
        {**shared, "kind": "frozen-grammar-fixture", "cases_per_family": PER_FAMILY},
        (("records", lambda: json_lines(source / "cases.jsonl")),),
    ))
    name = "rust-v7-grammar-self-oracle.json.gz"
    artifacts.append(archive(
        target / name,
        {**shared, "kind": "stdlib-vs-stdlib-self-oracle", "report": self_report},
    ))
    for letter, filename in (("a", "oracle-a.jsonl"), ("b", "oracle-b.jsonl")):
        name = f"rust-v7-grammar-self-{letter}.json.gz"
        artifacts.append(archive(
            target / name,
            {**shared, "kind": "complete-stdlib-oracle-pass", "pass": letter, "records_sha256": ORACLE_SHA256},
            (("records", lambda filename=filename: json_lines(source / filename)),),
        ))
    for label, module, slug, report in validated:
        name = f"rust-v7-grammar-{label}-initial.json.gz"
        artifacts.append(archive(
            target / name,
            {**shared, "kind": "complete-original-candidate-baseline", "module": module, "report": report},
            (
                ("actual_records", lambda slug=slug: json_lines(source / (slug + "-actual.jsonl"))),
                ("mismatch_records", lambda slug=slug: json_lines(source / (slug + "-mismatches.jsonl"))),
            ),
        ))
    triage = json_file(source / "triage.json")
    if (
        triage.get("fixture_sha256") != FIXTURE_SHA256
        or triage.get("oracle_self_failures") != 0
        or triage.get("cases") != manifest["cases"]
        or triage.get("candidates_measured") != len(CANDIDATES)
    ):
        raise RuntimeError("the complete grammar mismatch triage changed")
    artifacts.append(archive(
        target / "rust-v7-grammar-triage.json.gz",
        {**shared, "kind": "all-family-compact-triage", "triage": triage},
    ))
    summary = {
        **shared,
        "kind": "frozen-all-candidate-grammar-manifest",
        "cases_per_family": PER_FAMILY,
        "valid_grammars": self_report["valid_grammars"],
        "invalid_grammars_retained": self_report["invalid_grammars_retained"],
        "self_oracle_failures": self_report["self_oracle_failures"],
        "original_candidates": [
            {
                "label": label,
                "module": module,
                "cases": report["cases"],
                "matches": report["matches"],
                "mismatches": report["mismatches"],
                "valid_grammars_rejected": report["valid_grammars_rejected"],
                "invalid_grammars_accepted": report["invalid_grammars_accepted"],
                "error_message_or_offset_mismatches": report["error_message_or_offset_mismatches"],
                "crashes": report["crashes"],
                "timeouts": report["timeouts"],
                "mismatches_by_family": report["mismatches_by_family"],
            }
            for label, module, slug, report in validated
        ],
        "artifacts": artifacts,
    }
    final = archive(target / "rust-v7-grammar-manifest.json.gz", summary)
    print(canonical({
        "schema": SCHEMA + "-bundle",
        "python": platform.python_version(),
        "cases": manifest["cases"],
        "families": len(FAMILIES),
        "self_oracle_failures": 0,
        "valid_grammars": 14_818,
        "invalid_grammars_retained": 5_662,
        "fixture_sha256": FIXTURE_SHA256,
        "oracle_sha256": ORACLE_SHA256,
        "candidate_mismatches": {label: count for label, _, _, count in CANDIDATES},
        "artifact_count": len(artifacts) + 1,
        "total_compressed_bytes": sum(item["compressed_bytes"] for item in artifacts) + final["compressed_bytes"],
        "manifest": final,
    }), flush=True)


def decompressed_digest(path):
    digest = hashlib.sha256()
    with gzip.open(path, "rb") as source:
        for block in iter(lambda: source.read(1_048_576), b""):
            digest.update(block)
    return digest.hexdigest()


def archive_json(path):
    with gzip.open(path, "rt", encoding="ascii") as source:
        return json.load(source)


def command_verify(args):
    check_python()
    directory = pathlib.Path(args.evidence_dir).resolve()
    manifest = archive_json(directory / "rust-v7-grammar-manifest.json.gz")
    count, digest = fixture_digest()
    if (
        manifest.get("schema") != SCHEMA
        or manifest.get("seed") != SEED
        or manifest.get("fixture_sha256") != FIXTURE_SHA256
        or manifest.get("oracle_sha256") != ORACLE_SHA256
        or manifest.get("cases") != count
        or digest != FIXTURE_SHA256
        or manifest.get("families") != list(FAMILIES)
        or manifest.get("self_oracle_failures") != 0
        or manifest.get("valid_grammars") != 14_818
        or manifest.get("invalid_grammars_retained") != 5_662
        or manifest.get("performance_fixtures_read") != 0
        or manifest.get("holdout_cases_read") != 0
        or manifest.get("external_regex_packages") != 0
    ):
        raise RuntimeError("frozen grammar manifest, oracle, denominator, or isolation changed")
    expected = {label: count for label, _, _, count in CANDIDATES}
    actual = {entry["label"]: entry["mismatches"] for entry in manifest["original_candidates"]}
    if expected != actual or any(entry["crashes"] or entry["timeouts"] for entry in manifest["original_candidates"]):
        raise RuntimeError("a complete original-candidate baseline was changed or omitted")
    for item in manifest["artifacts"]:
        path = directory / item["file"]
        if (
            not path.is_file()
            or sha256(path) != item["sha256"]
            or decompressed_digest(path) != item["uncompressed_sha256"]
            or path.stat().st_size != item["compressed_bytes"]
        ):
            raise RuntimeError(f"compressed grammar evidence is missing, corrupted, or changed: {item['file']}")
    print(canonical({
        "schema": SCHEMA + "-verification",
        "python": platform.python_version(),
        "seed": SEED,
        "cases": count,
        "families": len(FAMILIES),
        "cases_per_family": PER_FAMILY,
        "fixture_sha256": digest,
        "oracle_sha256": ORACLE_SHA256,
        "self_oracle_failures": 0,
        "valid_grammars": 14_818,
        "invalid_grammars_retained": 5_662,
        "candidate_mismatches": actual,
        "crashes": 0,
        "timeouts": 0,
        "verified_archives": len(manifest["artifacts"]) + 1,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "external_regex_packages": 0,
    }), flush=True)


def error_snapshot(error):
    result = {
        "status": "error",
        "type": type(error).__name__,
        "str": str(error),
        "args": normalise(error.args),
    }
    if all(hasattr(error, key) for key in ("msg", "pattern", "pos", "lineno", "colno")):
        result["pattern_error"] = {
            key: normalise(getattr(error, key))
            for key in ("msg", "pattern", "pos", "lineno", "colno")
        }
    return result


def attempt(action):
    try:
        return {"status": "ok", "value": normalise(action())}
    except Exception as error:
        return error_snapshot(error)


def match_snapshot(match):
    if match is None:
        return None
    default = b"!" if isinstance(match.re.pattern, bytes) else "!"
    return {
        "span": normalise(match.span()),
        "regs": normalise(match.regs),
        "group0": normalise(match.group(0)),
        "groups": normalise(match.groups()),
        "groups_default": normalise(match.groups(default)),
        "groupdict": normalise(match.groupdict()),
        "lastindex": match.lastindex,
        "lastgroup": match.lastgroup,
        "pos": match.pos,
        "endpos": match.endpos,
    }


def observation(module, case):
    pattern = decode_domain(case["pattern"])
    subject = decode_domain(case["subject"])
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            compiled = module.compile(pattern, case["flags"])
        except Exception as error:
            return {
                "compile": error_snapshot(error),
                "warnings": [
                    {"category": item.category.__name__, "message": str(item.message)}
                    for item in caught
                ],
            }
    result = {
        "compile": {"status": "ok", "value": {
            "pattern": normalise(compiled.pattern),
            "flags": int(compiled.flags),
            "groups": compiled.groups,
            "groupindex": normalise(dict(compiled.groupindex)),
        }},
        "warnings": [
            {"category": item.category.__name__, "message": str(item.message)}
            for item in caught
        ],
        "operations": {},
    }
    length = len(subject)
    windows = tuple(dict.fromkeys((
        (0, length), (min(1, length), length), (0, max(0, length - 1)), (length, length),
    )))
    for pos, endpos in windows:
        for operation in ("search", "match", "fullmatch"):
            result["operations"][f"{operation}:{pos}:{endpos}"] = attempt(
                lambda operation=operation, pos=pos, endpos=endpos: match_snapshot(
                    getattr(compiled, operation)(subject, pos, endpos)
                )
            )
    replacement = rb"<\g<0>>" if isinstance(pattern, bytes) else r"<\g<0>>"
    for label, action in (
        ("findall", lambda: compiled.findall(subject)),
        ("finditer", lambda: [match_snapshot(item) for item in itertools.islice(compiled.finditer(subject), 129)]),
        ("split:2", lambda: compiled.split(subject, 2)),
        ("sub:2", lambda: compiled.sub(replacement, subject, 2)),
        ("subn:2", lambda: compiled.subn(replacement, subject, 2)),
    ):
        result["operations"][label] = attempt(action)
    return result


def command_worker(args):
    check_python()
    allowed = {"re"} | {module for _, module, _, _ in CANDIDATES}
    if args.module not in allowed:
        raise RuntimeError(f"unapproved independent candidate: {args.module}")
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    module = importlib.import_module(args.module)
    for line in sys.stdin:
        if line.strip():
            case = json.loads(line)
            print(canonical({
                "id": case["id"],
                "family": case["family"],
                "observation": observation(module, case),
            }), flush=True)


def batch_observations(module, cases, timeout):
    command = [sys.executable, str(pathlib.Path(__file__).resolve()), "worker", "--module", module]
    payload = "".join(canonical(case) + "\n" for case in cases)
    try:
        completed = subprocess.run(
            command, input=payload, capture_output=True, text=True,
            cwd=ROOT, timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired:
        failure = {"status": "timeout", "timeout_seconds": timeout}
    else:
        if completed.returncode == 0:
            try:
                rows = [json.loads(line) for line in completed.stdout.splitlines() if line.strip()]
                if len(rows) == len(cases) and all(
                    row["id"] == case["id"] for row, case in zip(rows, cases, strict=True)
                ):
                    return rows
            except (TypeError, ValueError, KeyError):
                pass
        failure = {
            "status": "crash" if completed.returncode else "malformed-output",
            "returncode": completed.returncode,
            "stderr": completed.stderr[-12_000:],
            "stdout": completed.stdout[-12_000:],
        }
    if len(cases) > 1:
        middle = len(cases) // 2
        return (
            batch_observations(module, cases[:middle], timeout)
            + batch_observations(module, cases[middle:], timeout)
        )
    case = cases[0]
    return [{
        "id": case["id"],
        "family": case["family"],
        "observation": {"worker_failure": failure},
    }]


def command_gate(args):
    check_python()
    directory = pathlib.Path(args.evidence_dir).resolve()
    frozen = archive_json(directory / "rust-v7-grammar-manifest.json.gz")
    if (
        frozen.get("fixture_sha256") != FIXTURE_SHA256
        or frozen.get("oracle_sha256") != ORACLE_SHA256
        or frozen.get("self_oracle_failures") != 0
    ):
        raise RuntimeError("the committed grammar self-oracle is not frozen or passing")
    cases = archive_json(directory / "rust-v7-grammar-fixture.json.gz")["records"]
    expected_rows = archive_json(directory / "rust-v7-grammar-self-a.json.gz")["records"]
    if len(cases) != frozen["cases"] or len(expected_rows) != frozen["cases"]:
        raise RuntimeError("the committed grammar oracle changed its denominator")
    actual_rows = []
    mismatches = []
    counts = collections.Counter()
    crashes = 0
    timeouts = 0
    for start in range(0, len(cases), args.batch_size):
        group = cases[start:start + args.batch_size]
        for offset, actual in enumerate(batch_observations(args.module, group, args.timeout)):
            index = start + offset
            case = cases[index]
            expected = expected_rows[index]
            actual_rows.append(actual)
            if actual["id"] != case["id"] or expected["id"] != case["id"]:
                raise RuntimeError("a candidate changed the committed grammar case order")
            if actual["observation"] == expected["observation"]:
                continue
            counts[case["family"]] += 1
            failure = actual["observation"].get("worker_failure")
            if failure is not None:
                if failure["status"] == "timeout":
                    timeouts += 1
                else:
                    crashes += 1
            mismatches.append({
                "case": case,
                "candidate": args.module,
                "expected": expected["observation"],
                "actual": actual["observation"],
            })
        if start == 0 or (start + len(group)) % 2_048 == 0 or start + len(group) == len(cases):
            print(canonical({
                "phase": "progress", "module": args.module,
                "completed": start + len(group), "total": len(cases),
            }), flush=True)
    report = {
        "schema": SCHEMA + "-candidate-gate",
        "module": args.module,
        "python": platform.python_version(),
        "seed": SEED,
        "fixture_sha256": FIXTURE_SHA256,
        "oracle_sha256": ORACLE_SHA256,
        "cases": len(cases),
        "matches": len(cases) - len(mismatches),
        "mismatches": len(mismatches),
        "mismatches_by_family": dict(sorted(counts.items())),
        "crashes": crashes,
        "timeouts": timeouts,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "external_regex_packages": 0,
    }
    if args.output:
        target = pathlib.Path(args.output).resolve()
        if not target.name.startswith("rust-v7-grammar-") or target.suffixes[-2:] != [".json", ".gz"]:
            raise RuntimeError("gate output must be named rust-v7-grammar-*.json.gz")
        report["archive"] = archive(
            target, {"report": report.copy()},
            (("actual_records", lambda: iter(actual_rows)), ("mismatch_records", lambda: iter(mismatches))),
        )
    print(canonical(report), flush=True)
    if mismatches and args.require_pass:
        raise SystemExit(2)


def parser():
    main = argparse.ArgumentParser(description=__doc__)
    commands = main.add_subparsers(dest="command", required=True)
    regenerate = commands.add_parser("regenerate", help="regenerate the exact frozen 20,480-case fixture")
    regenerate.add_argument("--output", required=True)
    regenerate.set_defaults(handler=command_regenerate)
    bundle = commands.add_parser("bundle", help="validate and deterministically archive all frozen initial results")
    bundle.add_argument("--source", required=True)
    bundle.add_argument("--evidence-dir", default=str(EVIDENCE))
    bundle.set_defaults(handler=command_bundle)
    verify = commands.add_parser("verify", help="reproduce fixture and verify every complete compressed artifact")
    verify.add_argument("--evidence-dir", default=str(EVIDENCE))
    verify.set_defaults(handler=command_verify)
    worker = commands.add_parser("worker", help="isolated stdlib or candidate grammar worker")
    worker.add_argument("--module", required=True, choices=("re",) + tuple(row[1] for row in CANDIDATES))
    worker.set_defaults(handler=command_worker)
    gate = commands.add_parser("gate", help="compare a candidate with the entire unchanged committed oracle")
    gate.add_argument("--module", required=True, choices=("re",) + tuple(row[1] for row in CANDIDATES))
    gate.add_argument("--evidence-dir", default=str(EVIDENCE))
    gate.add_argument("--batch-size", type=int, default=256)
    gate.add_argument("--timeout", type=float, default=15)
    gate.add_argument("--output")
    gate.add_argument("--require-pass", action="store_true")
    gate.set_defaults(handler=command_gate)
    return main


def main():
    arguments = parser().parse_args()
    if getattr(arguments, "batch_size", 1) <= 0 or getattr(arguments, "timeout", 1) <= 0:
        raise SystemExit("batch size and timeout must be positive")
    arguments.handler(arguments)


if __name__ == "__main__":
    main()
