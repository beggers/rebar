#!/usr/bin/env python3
"""Reproduce isolated, from-scratch Rust ordered-automata experiments.

CPython's ``re`` is imported and executed only in a dedicated ``_oracle``
subprocess.  The standalone Rust executable contains its own parser,
compiler, ordered executor, Unicode tables, and conservative optimizations.
No performance measurement inspects or generates a holdout case: timed cases
come exclusively from ``v6.generated_case("calibration", ...)``.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import random
import statistics
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools" / "rust_automata_lab.rs"
DEFAULT_BINARY = Path("/tmp/rebar-rust-automata-lab-v1")
DEFAULT_EVIDENCE = (
    ROOT / "candidates" / "evidence" / "rust-v6-automata-lab.json.gz"
)
SEED = 0xA170_2026
ARCHITECTURES = ("ordered", "dispatch", "needle", "pike")
FLAG_VALUES = {"I": 2, "L": 4, "M": 8, "S": 16, "U": 32, "X": 64, "A": 256}


@dataclass(frozen=True, slots=True)
class Case:
    case_id: str
    family: str
    pattern: str | bytes
    subject: str | bytes
    flags: int
    position: int
    end_position: int
    operation: str
    origin: str

    @property
    def kind(self) -> str:
        return "b" if isinstance(self.pattern, bytes) else "t"

    def line(
        self,
        architecture: str | None = None,
        operations: int | None = None,
        warmups: int | None = None,
        *,
        trial: int | None = None,
    ) -> str:
        identifier = self.case_id if trial is None else f"{self.case_id}@{trial}"
        fields = [
            identifier,
            self.kind,
            str(self.flags),
            encode_value(self.pattern),
            encode_value(self.subject),
            str(self.position),
            str(self.end_position),
            self.operation,
        ]
        if architecture is not None:
            fields.append(architecture)
        if operations is not None:
            if architecture is None:
                raise ValueError("timing requires an explicit architecture")
            fields.append(str(operations))
            fields.append(str(0 if warmups is None else warmups))
        return "\t".join(fields)


def encode_value(value: str | bytes) -> str:
    if isinstance(value, bytes):
        return value.hex()
    return "".join(f"{ord(character):08x}" for character in value)


def decode_value(value: str, kind: str) -> str | bytes:
    data = bytes.fromhex(value)
    if kind == "b":
        return data
    if kind != "t" or len(data) % 4:
        raise ValueError("invalid encoded text")
    return "".join(
        chr(int.from_bytes(data[index : index + 4], "big"))
        for index in range(0, len(data), 4)
    )


def frozen_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def oracle_process() -> int:
    # The oracle is the only process in this experiment that may execute
    # CPython's regex engine.  No production component imports this function.
    if sys.implementation.name != "cpython" or sys.version_info[:3] != (3, 14, 6):
        print("the isolated oracle requires pinned CPython 3.14.6", file=sys.stderr)
        return 2
    import re

    for number, line in enumerate(sys.stdin, 1):
        try:
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 8:
                raise ValueError("expected eight protocol fields")
            identifier, kind, flag_text, raw_pattern, raw_subject, first, last, mode = (
                fields[:8]
            )
            pattern = decode_value(raw_pattern, kind)
            subject = decode_value(raw_subject, kind)
            compiled = re.compile(pattern, int(flag_text))
            operation = {"s": compiled.search, "m": compiled.match, "f": compiled.fullmatch}[
                mode
            ]
            match = operation(subject, int(first), int(last))
            if match is None:
                result = [identifier, "none", "-1", "-1", "-1", "-", "-1", "-1"]
            else:
                registers = ",".join(
                    f"{start}:{end}" for start, end in match.regs
                )
                result = [
                    identifier,
                    "match",
                    str(match.start()),
                    str(match.end()),
                    str(-1 if match.lastindex is None else match.lastindex),
                    registers,
                    str(match.pos),
                    str(match.endpos),
                ]
            print("\t".join(result))
        except Exception as error:
            print(f"oracle line {number}: {error!r}", file=sys.stderr)
            return 2
    return 0


def subprocess_rows(command: list[str], rows: Iterable[str]) -> list[list[str]]:
    payload = "".join(f"{row}\n" for row in rows)
    result = subprocess.run(
        command,
        input=payload,
        text=True,
        encoding="utf-8",
        errors="surrogatepass",
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"{' '.join(command)} exited {result.returncode}: "
            f"{result.stderr.strip()[:3000]}"
        )
    return [line.split("\t") for line in result.stdout.splitlines()]


def run_oracle(cases: list[Case]) -> dict[str, tuple[str, ...]]:
    rows = subprocess_rows(
        [sys.executable, str(Path(__file__).resolve()), "_oracle"],
        (case.line() for case in cases),
    )
    if len(rows) != len(cases):
        raise RuntimeError("isolated oracle returned the wrong number of results")
    result: dict[str, tuple[str, ...]] = {}
    for case, row in zip(cases, rows, strict=True):
        if len(row) != 8 or row[0] != case.case_id:
            raise RuntimeError(f"isolated oracle lost case identity: {case.case_id}")
        result[case.case_id] = tuple(row)
    if len(result) != len(cases):
        raise RuntimeError("duplicate oracle case identifiers")
    return result


def run_candidate(
    binary: Path,
    cases: list[Case],
    architecture: str,
) -> list[list[str]]:
    rows = subprocess_rows(
        [str(binary), architecture],
        (case.line() for case in cases),
    )
    if len(rows) != len(cases):
        raise RuntimeError(f"{architecture} returned the wrong number of results")
    return rows


def escaped_literal(value: str) -> str:
    return "".join(
        f"\\{character}" if character in r"\.^$*+?{}[]|()" else character
        for character in value
    )


def add_case_group(
    output: list[Case],
    family: str,
    pattern: str | bytes,
    subjects: Iterable[str | bytes],
    *,
    flags: int = 0,
    windows: int = 4,
    origin: str = "seeded differential",
) -> None:
    for subject_number, subject in enumerate(subjects):
        if isinstance(pattern, bytes) != isinstance(subject, bytes):
            raise TypeError("pattern and subject must have the same input kind")
        length = len(subject)
        candidates = (
            (0, length),
            (min(1, length), length),
            (0, max(0, length - 1)),
            (length, length),
            (-3, length + 3),
            (length + 2, length + 5),
            (min(2, length), min(1, length)),
        )
        for window_number, (first, last) in enumerate(candidates[:windows]):
            for mode in ("s", "m", "f"):
                identifier = (
                    f"{family}.{len(output):06d}.{subject_number:02d}."
                    f"{window_number}.{mode}"
                )
                output.append(
                    Case(
                        identifier,
                        family,
                        pattern,
                        subject,
                        flags,
                        first,
                        last,
                        mode,
                        origin,
                    )
                )


def manual_cases() -> list[Case]:
    output: list[Case] = []
    ascii_subjects = (
        "",
        "x foo bar baz qux tail",
        "xxababcabcax",
        "AAERROR:73 and ZZERROR:91",
        "\nline 39\nfoo\n",
        "aaaaabbbbbcccccx",
    )
    patterns = (
        ("disjoint-literals", r"(?:foo|bar|baz|qux)"),
        ("overlapping-literals", r"(?:a|ab|abc|abca)x?"),
        ("shared-prefix", r"(?:foo|food|foobar|fool)"),
        ("disjoint-class", r"(?:[a-f]z|[g-m]y|[n-z]x|[0-9]q)"),
        ("overlapping-class", r"(?:[a-z]a|[a-f]b|[^x]c)"),
        ("ordered-captures", r"((foo)|(bar)|(baz)|(qux))([0-9]?)"),
        ("nested-captures", r"((a)(b)?|((c)(d)?))x?"),
        ("repeated-captures", r"((a)(b)?)+x?"),
        ("optional-captures", r"((a)|(ab)|(b))?x"),
        ("nullable-alternative", r"(?:|a|ab|b)c"),
        ("empty-groups", r"(()|a|ab|b)c?"),
        ("greedy-repeat", r"(?:a|b|c)+x?"),
        ("lazy-repeat", r"(?:a|b|c)+?x?"),
        ("bounded-repeat", r"(?:ab|cd|ef){1,4}?x?"),
        ("optional-repeat", r"(?:foo|bar|baz){0,2}"),
        ("lazy-dot", r".*?(?:foo|bar|baz|qux)"),
        ("greedy-dot", r".+(?:foo|bar|baz|qux)"),
        ("fixed-offset-needle", r"[A-Z]{2}ERROR:[0-9]{2}"),
        ("capture-needle", r"([A-Z]{2})(ERROR:)([0-9]{2})"),
        ("escaped-literal", r"(?:foo\.|bar\+|baz\?|qux\[)"),
        ("ascii-categories", r"(?:\d+|\w+|\s+|[^a-z]+)"),
        ("scoped-case", r"(?i:(?:foo|Bar|QuX|K))(?-i:x)?"),
        ("scoped-dot", r"(?s:(?:a.|b.|c.))x?"),
    )
    for family, pattern in patterns:
        add_case_group(output, family, pattern, ascii_subjects, windows=5)

    unicode_subjects = (
        "",
        "éclair Ωmega 🦀rust 𐍈run",
        "İıſK ÅåÅ ΩωΩ ςσΣ",
        "a\u0301 雪 ٣ ² _\u001c",
        "\ud800x \udfffy 🦀",
        "prefix éclair suffix",
    )
    unicode_patterns = (
        ("unicode-disjoint", "(?:éclair|Ωmega|🦀rust|𐍈run)"),
        ("unicode-overlap", "(?:é|éc|éclair|éclat)"),
        ("unicode-captures", "((é)|(Ω)|(🦀)|(𐍈))"),
        ("unicode-category", r"(?:\d+|\w+|\s+|[^\w]+)"),
        ("unicode-surrogates", "(?:\ud800x|\udfffy|🦀)"),
        ("unicode-case-components", r"(?i:(?:i|s|k|ω|å|σ))"),
        ("unicode-scoped-ascii", r"(?a:(?i:(?:i|s|k|ω|å|σ)))"),
        ("unicode-range-case", r"(?i:(?:[A-Z]|[Ω-Ω]|[Å-Å]))"),
    )
    for family, pattern in unicode_patterns:
        add_case_group(output, family, pattern, unicode_subjects, windows=5)

    byte_subjects = (
        b"",
        b"x foo bar baz qux tail",
        bytes(range(32)),
        bytes(range(128, 256)),
        b"AAERROR:73 \xff ZZERROR:91",
        b"aaaaabbbbbcccccx\x00\xff",
    )
    byte_patterns = (
        ("bytes-disjoint", rb"(?:foo|bar|baz|qux)"),
        ("bytes-overlap", rb"(?:a|ab|abc|abca)x?"),
        ("bytes-captures", rb"((foo)|(bar)|(baz)|(qux))"),
        ("bytes-category", rb"(?:\d+|\w+|\s+|[^a-z]+)"),
        ("bytes-high-bit", rb"(?:\xff|\x80|\x00|q)"),
        ("bytes-needle", rb"[A-Z]{2}ERROR:[0-9]{2}"),
        ("bytes-ignorecase", rb"(?:FOO|bar|BAZ|QuX)"),
    )
    for family, pattern in byte_patterns:
        add_case_group(
            output,
            family,
            pattern,
            byte_subjects,
            flags=2 if family == "bytes-ignorecase" else 0,
            windows=5,
        )
    return output


def fuzz_cases(patterns: int, seed: int) -> list[Case]:
    rng = random.Random(seed)
    output: list[Case] = []
    plain_words = ("alpha", "beta", "cedar", "delta", "ember", "fjord", "grove")
    unicode_words = ("éclair", "Ωmega", "🦀rust", "𐍈run", "雪", "Ångström")
    for index in range(patterns):
        family = index % 12
        words = rng.sample(plain_words, rng.randrange(3, 6))
        escaped = [escaped_literal(word) for word in words]
        flags = 0
        bytes_mode = family in (8, 9)
        if family == 0:
            pattern = "(?:" + "|".join(escaped) + ")"
        elif family == 1:
            shared = rng.choice(("a", "ab", "token", "error"))
            pattern = "(?:" + "|".join(
                escaped_literal(shared + tail)
                for tail in ("", "x", "xy", "xyz")
            ) + ")x?"
        elif family == 2:
            pattern = r"(?:[a-f]z|[g-m]y|[n-z]x|[0-9]q)"
        elif family == 3:
            pattern = "((" + ")|(".join(escaped) + "))([0-9]?)"
        elif family == 4:
            pattern = "(?:|" + "|".join(escaped[:3]) + ")x?"
        elif family == 5:
            pattern = "(?:" + "|".join(escaped[:3]) + r"){1,3}?x?"
        elif family == 6:
            pattern = "(?i:(?:" + "|".join(escaped) + "))(?-i:x)?"
        elif family == 7:
            words = rng.sample(unicode_words, 4)
            pattern = "(?:" + "|".join(escaped_literal(item) for item in words) + ")"
        elif family == 8:
            pattern = "(?:" + "|".join(escaped) + ")"
        elif family == 9:
            pattern = r"(?:\xff|\x80|\x00|[A-Z][0-9])"
        elif family == 10:
            pattern = r"[A-Z]{2}ERROR:[0-9]{2}"
        else:
            pattern = r"(?:\d+|\w+|\s+|[^a-z]+)"

        if bytes_mode:
            encoded_pattern: str | bytes = pattern.encode("ascii")
            subjects: list[str | bytes] = [
                (" ".join(rng.choices(plain_words, k=5))).encode("ascii"),
                b"before " + words[0].encode("ascii") + b" after\xff",
                bytes(rng.randrange(256) for _ in range(24)),
            ]
        else:
            encoded_pattern = pattern
            alphabet = "abcxyz019_ \n"
            subjects = [
                "".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 48))),
                "before " + rng.choice(words) + " after",
                (
                    "AAERROR:73 xx ZZERROR:91"
                    if family == 10
                    else " ".join(rng.choices((*plain_words, *unicode_words), k=4))
                ),
            ]
        add_case_group(
            output,
            f"fuzz-{family:02d}-{index:04d}",
            encoded_pattern,
            subjects,
            flags=flags,
            windows=2,
        )
    return output


def differential_cases(patterns: int, seed: int) -> list[Case]:
    cases = manual_cases()
    cases.extend(fuzz_cases(patterns, seed))
    identifiers = {case.case_id for case in cases}
    if len(identifiers) != len(cases):
        raise RuntimeError("seeded automata cases contain duplicate identifiers")
    return cases


def negative_controls() -> list[Case]:
    controls = (
        ("atomic-priority", r"(?>a|ab)c", "abc ac"),
        ("possessive-cut", r"a*+a", "aaa a"),
        ("positive-lookahead", r"(?=(a))a", "ba"),
        ("negative-lookahead", r"a(?!b)", "ab ac"),
        ("capturing-lookbehind", r"(?<=(a))b", "ab"),
        ("numeric-backreference", r"(a)\1", "aa"),
        ("capture-conditional", r"(a)?(?(1)b|c)", "ab c"),
        ("beginning-anchor", r"^a", "x\na"),
        ("terminal-newline-anchor", r"a$", "a\n"),
        ("word-boundary", r"\ba\b", " a "),
        ("empty-nonboundary", r"\B", ""),
        ("nullable-unbounded-repeat", r"(?:a?)*", "aaa"),
    )
    return [
        Case(
            f"reject.{family}",
            family,
            pattern,
            subject,
            0,
            0,
            len(subject),
            "s",
            "mandatory unsupported-semantics negative control",
        )
        for family, pattern, subject in controls
    ]


def verify_negative_controls(binary: Path) -> dict:
    controls = negative_controls()
    expected = run_oracle(controls)
    probe = subprocess_rows(
        [str(binary), "probe"],
        (case.line() for case in controls),
    )
    if len(probe) != len(controls):
        raise RuntimeError("unsupported-semantics probe lost negative controls")
    records = []
    for case, row in zip(controls, probe, strict=True):
        if len(row) < 3 or row[0] != case.case_id or row[1] != "error":
            raise RuntimeError(
                f"automata lab unsafely accepted unsupported semantics: {case.case_id}"
            )
        records.append(
            {
                "case": case.case_id,
                "family": case.family,
                "pattern": repr(case.pattern),
                "subject": repr(case.subject),
                "oracle": list(expected[case.case_id]),
                "rejection": row[2],
            }
        )
    return {
        "cases": len(records),
        "oracle_checks": len(records),
        "unsafe_acceptances": 0,
        "controls": records,
    }


def summarize_counts(rows: list[list[str]]) -> dict[str, int]:
    totals = Counter()
    for row in rows:
        if len(row) != 16:
            raise RuntimeError("candidate returned an invalid result width")
        for name, position in (
            ("vm_steps", 8),
            ("start_attempts", 9),
            ("saved_alternatives", 10),
            ("dispatches", 11),
            ("prefilter_codepoints", 12),
        ):
            totals[name] += int(row[position])
    return dict(totals)


def verify_cases(binary: Path, cases: list[Case], seed: int) -> dict:
    expected = run_oracle(cases)
    controls = verify_negative_controls(binary)
    engines = {}
    failures = []
    evidence_rows = []
    for architecture in ARCHITECTURES:
        rows = run_candidate(binary, cases, architecture)
        observed = set()
        for case, row in zip(cases, rows, strict=True):
            if len(row) != 16 or row[0] != case.case_id:
                raise RuntimeError(f"{architecture} changed case order or result shape")
            observed.add(row[0])
            evidence_rows.append(
                {
                    "case": case.case_id,
                    "family": case.family,
                    "architecture": architecture,
                    "result": row[1:8],
                    "vm_steps": int(row[8]),
                    "start_attempts": int(row[9]),
                    "saved_alternatives": int(row[10]),
                    "dispatches": int(row[11]),
                    "prefilter_codepoints": int(row[12]),
                }
            )
            if tuple(row[:8]) != expected[case.case_id]:
                failures.append(
                    {
                        "case": case.case_id,
                        "family": case.family,
                        "architecture": architecture,
                        "expected": list(expected[case.case_id]),
                        "actual": row[:8],
                        "pattern": repr(case.pattern),
                        "subject": repr(case.subject),
                        "flags": case.flags,
                        "window": [case.position, case.end_position],
                    }
                )
        if len(observed) != len(cases):
            raise RuntimeError(f"{architecture} repeated or omitted cases")
        engines[architecture] = {
            "cases": len(rows),
            "mismatches": sum(
                failure["architecture"] == architecture for failure in failures
            ),
            "deterministic_operation_counts": summarize_counts(rows),
        }
    return {
        "schema": "rebar-rust-isolated-ordered-automata-differential-v1",
        "oracle": "CPython 3.14.6 re in a separate oracle-only process",
        "production_candidate": False,
        "end_to_end_speed": "NOT MEASURED",
        "holdout_access": "NONE",
        "seed": seed,
        "python": sys.version.split()[0],
        "patterns": len({(repr(case.pattern), case.flags) for case in cases}),
        "cases": len(cases),
        "oracle_comparisons": len(cases) * len(ARCHITECTURES),
        "unsupported_semantics": controls,
        "families": dict(sorted(Counter(case.family for case in cases).items())),
        "input_kinds": dict(sorted(Counter(case.kind for case in cases).items())),
        "operations": dict(
            sorted(Counter(case.operation for case in cases).items())
        ),
        "architectures": engines,
        "raw_cases": evidence_rows,
        "mismatches": len(failures),
        "failures": failures,
        "source_sha256": frozen_hash(SOURCE),
        "driver_sha256": frozen_hash(Path(__file__).resolve()),
        "unicode_table_sha256": frozen_hash(
            ROOT / "candidates" / "rust" / "src" / "unicode_tables.rs"
        ),
    }


def calibration_candidates() -> tuple[list[Case], dict]:
    # Do not call suite.cases(): it constructs the unseen cohort.  Calling the
    # seeded generator with the literal calibration cohort cannot inspect,
    # construct, tune against, or accidentally time a holdout case.
    from performance.v6 import suite

    rows: list[Case] = []
    excluded: Counter[str] = Counter()
    for family in suite.FAMILIES:
        for variant in range(suite.VARIANTS):
            source = suite.generated_case("calibration", family, variant)
            api = source["api"]
            if api not in {"search", "match", "fullmatch"}:
                excluded[f"unsupported standalone API: {api}"] += 1
                continue
            pattern = source.get("pattern")
            subject = source.get("string")
            if not isinstance(pattern, (str, bytes)):
                excluded["unsupported pattern input kind"] += 1
                continue
            if isinstance(subject, (bytearray, memoryview)):
                subject = bytes(subject)
            if not isinstance(subject, (str, bytes)):
                excluded["unsupported subject input kind"] += 1
                continue
            if isinstance(pattern, bytes) != isinstance(subject, bytes):
                excluded["mixed pattern and subject input kinds"] += 1
                continue
            raw_flags = source.get("flags", [])
            if isinstance(raw_flags, int):
                flags = raw_flags
            else:
                flags = 0
                for flag in raw_flags:
                    if flag not in FLAG_VALUES:
                        excluded[f"unsupported flag: {flag}"] += 1
                        flags = -1
                        break
                    flags |= FLAG_VALUES[flag]
                if flags < 0:
                    continue
            rows.append(
                Case(
                    source["id"],
                    source["category"],
                    pattern,
                    subject,
                    flags,
                    source.get("pos", 0),
                    source.get("endpos", len(subject)),
                    {"search": "s", "match": "m", "fullmatch": "f"}[api],
                    "frozen v6 calibration only",
                )
            )
    return rows, {
        "cohort": "calibration",
        "holdout_constructed": False,
        "frozen_generated_families": len(suite.FAMILIES),
        "frozen_variations_per_family": suite.VARIANTS,
        "eligible_api_rows": len(rows),
        "excluded_before_parser": dict(sorted(excluded.items())),
        "suite_sha256": frozen_hash(ROOT / "performance" / "v6" / "suite.py"),
        "manifest_sha256": frozen_hash(
            ROOT / "performance" / "v6" / "manifest.json"
        ),
    }


def supported_calibration(binary: Path, maximum_subject: int) -> tuple[list[Case], dict]:
    candidates, selection = calibration_candidates()
    short = [case for case in candidates if len(case.subject) <= maximum_subject]
    selection["excluded_subject_limit"] = len(candidates) - len(short)
    probe = subprocess_rows([str(binary), "probe"], (case.line() for case in short))
    if len(probe) != len(short):
        raise RuntimeError("Rust parser eligibility probe lost calibration cases")
    accepted: list[Case] = []
    rejected = Counter()
    rejected_cases = []
    for case, row in zip(short, probe, strict=True):
        if row[0] != case.case_id:
            raise RuntimeError("eligibility probe changed calibration case identity")
        if len(row) >= 3 and row[1] == "error":
            reason = row[2]
            rejected[reason] += 1
            rejected_cases.append({"case": case.case_id, "reason": reason})
        elif len(row) == 16:
            accepted.append(case)
        else:
            raise RuntimeError(f"invalid eligibility result: {row[:3]!r}")
    selection.update(
        {
            "maximum_subject_codepoints": maximum_subject,
            "parser_accepted": len(accepted),
            "parser_rejected": len(rejected_cases),
            "parser_rejection_reasons": dict(sorted(rejected.items())),
            "parser_rejected_cases": rejected_cases,
        }
    )
    return accepted, selection


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        raise ValueError("confidence interval requires observations")
    ordered = sorted(values)
    rank = fraction * (len(ordered) - 1)
    left = math.floor(rank)
    right = math.ceil(rank)
    return ordered[left] + (ordered[right] - ordered[left]) * (rank - left)


def regression_gt_20pct(speedup: float) -> bool:
    """True only when the candidate takes strictly over 120% of baseline time."""
    if not math.isfinite(speedup) or speedup <= 0:
        raise ValueError("regression classification requires a positive finite speedup")
    return speedup < 5 / 6


def regression_boundary_self_test() -> None:
    threshold = 5 / 6
    checks = (
        (threshold, False),
        (math.nextafter(threshold, 0.0), True),
        (math.nextafter(threshold, math.inf), False),
        (0.8, True),
        (1.0, False),
        (1.5, False),
    )
    for speedup, expected in checks:
        if regression_gt_20pct(speedup) != expected:
            raise AssertionError(f"incorrect >20% regression boundary: {speedup!r}")
    for invalid in (0.0, -1.0, math.inf, -math.inf, math.nan):
        try:
            regression_gt_20pct(invalid)
        except ValueError:
            continue
        raise AssertionError(f"accepted invalid regression speedup: {invalid!r}")


def bootstrap_interval(
    case_logs: list[float], repetitions: int, seed: int
) -> tuple[float, float]:
    if not case_logs or repetitions < 2:
        raise ValueError("paired bootstrap requires cases and repetitions")
    rng = random.Random(seed)
    samples = []
    count = len(case_logs)
    for _ in range(repetitions):
        samples.append(
            math.exp(sum(case_logs[rng.randrange(count)] for _ in range(count)) / count)
        )
    return percentile(samples, 0.025), percentile(samples, 0.975)


def timed_calibration(
    binary: Path,
    *,
    limit: int,
    maximum_subject: int,
    trials: int,
    operations: int,
    warmups: int,
    bootstraps: int,
    seed: int,
) -> dict:
    regression_boundary_self_test()
    cases, selection = supported_calibration(binary, maximum_subject)
    if not cases:
        raise RuntimeError("no eligible frozen calibration cases")
    if limit:
        cases = cases[:limit]
    expected = run_oracle(cases)
    tasks: list[tuple[Case, int, str]] = []
    for case in cases:
        for trial in range(trials):
            order = list(ARCHITECTURES)
            random.Random(
                seed + trial * 1009 + sum(map(ord, case.case_id))
            ).shuffle(order)
            tasks.extend((case, trial, architecture) for architecture in order)
    rows = subprocess_rows(
        [str(binary), "stream"],
        (
            case.line(architecture, operations, warmups, trial=trial)
            for case, trial, architecture in tasks
        ),
    )
    if len(rows) != len(tasks):
        raise RuntimeError("paired calibration timing lost trials")
    timings: dict[tuple[str, int, str], int] = {}
    evidence_rows = []
    checks = 0
    for (case, trial, architecture), row in zip(tasks, rows, strict=True):
        identifier = f"{case.case_id}@{trial}"
        if len(row) != 16 or row[0] != identifier or row[15] != architecture:
            raise RuntimeError(f"invalid paired result for {identifier}")
        want = list(expected[case.case_id])
        want[0] = identifier
        if row[:8] != want:
            raise RuntimeError(
                f"timed {architecture} disagrees with the isolated oracle: "
                f"{identifier}; expected={want!r}; actual={row[:8]!r}"
            )
        elapsed = int(row[13])
        observed_operations = int(row[14])
        if elapsed <= 0 or observed_operations != operations:
            raise RuntimeError(f"invalid timed sample: {identifier}")
        key = (case.case_id, trial, architecture)
        if key in timings:
            raise RuntimeError(f"duplicate timed sample: {identifier}")
        timings[key] = elapsed
        checks += 2  # The Rust timer verifies both its before and after result.
        evidence_rows.append(
            {
                "case": case.case_id,
                "family": case.family,
                "trial": trial,
                "architecture": architecture,
                "operations": observed_operations,
                "elapsed_ns": elapsed,
                "vm_steps": int(row[8]),
                "start_attempts": int(row[9]),
                "saved_alternatives": int(row[10]),
                "dispatches": int(row[11]),
                "prefilter_codepoints": int(row[12]),
            }
        )

    rankings = {}
    case_summaries = []
    for architecture in ARCHITECTURES[1:]:
        means = []
        for case in cases:
            logs = [
                math.log(timings[(case.case_id, trial, "ordered")])
                - math.log(timings[(case.case_id, trial, architecture)])
                for trial in range(trials)
            ]
            center = sum(logs) / len(logs)
            means.append(center)
            lo, hi = bootstrap_interval(
                logs,
                bootstraps,
                seed + sum(map(ord, case.case_id + architecture)),
            )
            case_summaries.append(
                {
                    "case": case.case_id,
                    "family": case.family,
                    "architecture": architecture,
                    "paired_speedup_vs_isolated_ordered": math.exp(center),
                    "confidence_interval_95": [lo, hi],
                    "statistically_faster": lo > 1,
                    "regression_gt_20pct": regression_gt_20pct(math.exp(center)),
                }
            )
        lo, hi = bootstrap_interval(
            means, bootstraps, seed + sum(map(ord, architecture))
        )
        selected = [row for row in case_summaries if row["architecture"] == architecture]
        rankings[architecture] = {
            "paired_speedup_vs_isolated_ordered": math.exp(statistics.fmean(means)),
            "confidence_interval_95": [lo, hi],
            "cases": len(selected),
            "statistically_faster_cases": sum(
                row["statistically_faster"] for row in selected
            ),
            "regressions_gt_20pct": sum(
                row["regression_gt_20pct"] for row in selected
            ),
        }
    return {
        "schema": "rebar-rust-isolated-ordered-automata-calibration-v1",
        "scope": "isolated Rust architecture components; not a production or Python baseline benchmark",
        "end_to_end_vs_stdlib": "NOT MEASURED",
        "expanded_holdout": "NOT MEASURED",
        "holdout_access": "NONE",
        "selection": selection,
        "case_selection_order": "frozen v6 calibration generation order",
        "seed": seed,
        "cases": len(cases),
        "architectures": list(ARCHITECTURES),
        "trials": trials,
        "operations_per_sample": operations,
        "warmups": warmups,
        "bootstraps": bootstraps,
        "regression_threshold": {
            "definition": "candidate time strictly greater than 120% of baseline time",
            "speedup_strictly_below": 5 / 6,
            "boundary_self_test": "PASS",
        },
        "correctness_checks": checks,
        "timed_samples": len(evidence_rows),
        "rankings": rankings,
        "cases_all": case_summaries,
        "raw_samples": evidence_rows,
        "source_sha256": frozen_hash(SOURCE),
        "driver_sha256": frozen_hash(Path(__file__).resolve()),
        "unicode_table_sha256": frozen_hash(
            ROOT / "candidates" / "rust" / "src" / "unicode_tables.rs"
        ),
    }


def save_evidence(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (
        json.dumps(report, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")
    with path.open("wb") as target:
        with gzip.GzipFile(filename="", mode="wb", fileobj=target, mtime=0) as stream:
            stream.write(payload)


def print_summary(report: dict) -> None:
    if "rankings" in report:
        summary = {
            key: report[key]
            for key in (
                "schema",
                "scope",
                "end_to_end_vs_stdlib",
                "holdout_access",
                "cases",
                "trials",
                "correctness_checks",
                "rankings",
            )
        }
    else:
        summary = {
            key: report[key]
            for key in (
                "schema",
                "end_to_end_speed",
                "holdout_access",
                "patterns",
                "cases",
                "oracle_comparisons",
                "mismatches",
                "architectures",
            )
        }
    print(json.dumps(summary, indent=2, sort_keys=True))


def build(binary: Path) -> None:
    binary.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "rustc",
        "--edition=2024",
        "-C",
        "opt-level=3",
        "-C",
        "debuginfo=1",
        str(SOURCE),
        "-o",
        str(binary),
    ]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"standalone Rust compilation failed: {result.stderr[:5000]}")
    print(
        json.dumps(
            {
                "binary": str(binary),
                "source_sha256": frozen_hash(SOURCE),
                "unicode_table_sha256": frozen_hash(
                    ROOT / "candidates" / "rust" / "src" / "unicode_tables.rs"
                ),
                "dependencies": "Rust standard library and frozen generated Python 3.14.6 Unicode tables only",
                "production_candidate": False,
            },
            indent=2,
            sort_keys=True,
        )
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    builder = commands.add_parser("build", help="compile only the isolated lab")
    builder.add_argument("--binary", type=Path, default=DEFAULT_BINARY)

    verifier = commands.add_parser("verify", help="compare all three designs with isolated CPython")
    verifier.add_argument("--binary", type=Path, default=DEFAULT_BINARY)
    verifier.add_argument("--patterns", type=int, default=1024)
    verifier.add_argument("--seed", type=int, default=SEED)
    verifier.add_argument("--output", type=Path)

    timer = commands.add_parser("measure", help="pair architecture trials on frozen practice cases only")
    timer.add_argument("--binary", type=Path, default=DEFAULT_BINARY)
    timer.add_argument("--limit", type=int, default=128)
    timer.add_argument("--maximum-subject", type=int, default=4096)
    timer.add_argument("--trials", type=int, default=9)
    timer.add_argument("--operations", type=int, default=12)
    timer.add_argument("--warmups", type=int, default=3)
    timer.add_argument("--bootstraps", type=int, default=1000)
    timer.add_argument("--seed", type=int, default=SEED)
    timer.add_argument("--output", type=Path, default=DEFAULT_EVIDENCE)

    commands.add_parser("self-test", help="verify the strict greater-than-20-percent boundary")

    args = parser.parse_args(argv)
    if sys.implementation.name != "cpython" or sys.version_info[:3] != (3, 14, 6):
        raise RuntimeError("the isolated automata lab requires pinned CPython 3.14.6")
    if args.command == "build":
        build(args.binary)
        return 0
    if args.command == "self-test":
        regression_boundary_self_test()
        print(
            json.dumps(
                {
                    "regression_threshold": "speedup strictly below 5/6",
                    "exact_boundary": "not a greater-than-20-percent regression",
                    "adjacent_floating_point_boundaries": "PASS",
                    "invalid_nonfinite_values": "PASS",
                    "timing": "NOT MEASURED",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    if not args.binary.is_file():
        raise RuntimeError(f"isolated Rust executable does not exist: {args.binary}")
    if args.command == "verify":
        if args.patterns < 0:
            raise ValueError("--patterns cannot be negative")
        report = verify_cases(
            args.binary,
            differential_cases(args.patterns, args.seed),
            args.seed,
        )
        if args.output:
            save_evidence(args.output, report)
        print_summary(report)
        return 1 if report["mismatches"] else 0
    if min(args.maximum_subject, args.trials, args.operations, args.bootstraps) < 1:
        raise ValueError("subject limit, trials, operations and bootstraps must be positive")
    if args.limit < 0 or args.warmups < 0:
        raise ValueError("case limit and warmups cannot be negative")
    report = timed_calibration(
        args.binary,
        limit=args.limit,
        maximum_subject=args.maximum_subject,
        trials=args.trials,
        operations=args.operations,
        warmups=args.warmups,
        bootstraps=args.bootstraps,
        seed=args.seed,
    )
    save_evidence(args.output, report)
    print_summary(report)
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "_oracle":
        raise SystemExit(oracle_process())
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        print(f"rust automata lab: {error}", file=sys.stderr)
        raise SystemExit(2) from error
