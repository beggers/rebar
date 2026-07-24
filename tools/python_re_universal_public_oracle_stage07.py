#!/usr/bin/env python3
"""Freeze and independently check eight public Python regular-expression cohorts."""

from __future__ import annotations

import sys

if __name__ == "__main__":
    import os as _stage07_os
    from pathlib import Path as _Stage07Path

    _stage07_root = str(_Stage07Path(__file__).resolve().parent.parent)
    _stage07_entry = (
        "import sys;sys.path.insert(0,sys.argv[1]);"
        "from tools.python_re_universal_public_oracle_stage07 import main;"
        "raise SystemExit(main(sys.argv[2:]))"
    )
    _stage07_os.execv(
        sys.executable,
        [sys.executable, "-I", "-B", "-c", _stage07_entry, _stage07_root, *sys.argv[1:]],
    )

import argparse
import gc
import hashlib
import importlib
import json
import os
import subprocess
import types
from pathlib import Path, PurePosixPath
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent.parent
SOURCE_RELATIVE = "tools/python_re_universal_public_oracle_stage07.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V7.md"
SCHEMA = "rebar-python-re-public-contract-v7"
SELF_TEST_SCHEMA = SCHEMA + "-self-test"
SELF_ORACLE_SCHEMA = SCHEMA + "-self-oracle"
ALL_CANDIDATE_SCHEMA = SCHEMA + "-all-candidates"
SELF_ORACLE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-contract-v7-self-oracle.json"
)
SELF_ORACLE_FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-contract-v7-self-oracle-failures.json"
)
ALL_CANDIDATE_RELATIVE = (
    "candidates/evidence/python-re-universal-public-oracle-v7-all.json"
)
CANDIDATE_FAILURE_RELATIVES = {
    family: f"candidates/evidence/python-re-universal-public-oracle-v7-{family}-failures.json"
    for family in ("rust", "vm", "zig")
}
SEED = 2026072437
SEED_DOMAIN = "rebar/python-re/public-contract/v7"
REQUIRED_CANDIDATES = ("rust", "vm", "zig")
COHORTS: tuple[tuple[str, str, int], ...] = (
    ("public-surface", "module-exports-signatures-flags", 256),
    ("invalid-grammar", "errors-warnings-and-scoped-flags", 256),
    ("real-locale", "all-bytes-genuine-locale-transitions", 1_024),
    ("buffer-lifetime", "contiguous-and-noncontiguous-buffers", 256),
    ("object-contract", "copy-pickle-hash-weakrefs-and-groups", 256),
    ("callback-scanner", "callback-reentry-and-scanner-actions", 256),
    ("shared-pattern-threads", "four-and-eight-synchronized-threads", 256),
    ("bounded-unicode", "index-limits-and-unicode-boundaries", 1_024),
)
EXPECTED_CASES = 3_584
MATRIX_SHA256 = "0233ca9bc1229b2f905192f9b8ae0c0268b7d23ba3621124192993c6d486f3db"
MAX_WORKER_BYTES = 8 * 1024 * 1024
MAX_MISMATCHES = EXPECTED_CASES
NATIVE_LOADER_ALIASES = (
    "ctypes.CDLL",
    "ctypes.cdll.LoadLibrary",
    "ctypes.cdll._dlltype",
    "ctypes._dlopen",
    "_ctypes.dlopen",
)
PINNED_INTERPRETER = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_STAGE06_SOURCE_SHA256 = (
    "ff365f1d867f4873146aaf6f77fa2f360b197bbccfb9dd06239bdcf4b776e7f2"
)
PINNED_STAGE06_REPORT_SHA256 = (
    "bf4f7cc82c876ee54e55c0971c65db209f6fdf0c8b00baa8c57fbc5f460b1528"
)
PINNED_BASE_REPORT_SHA256 = (
    "42bd73acf6831b67df9a9873fa35c1882f2af09c41933774ba841d2290e6c198"
)
PINNED_STRICT_REPORT_SHA256 = (
    "50031133a2aa20b1ef91b126a883a622d916f582fdcbea4ba1763267199c03bb"
)
PINNED_LOCALE_REPORT_SHA256 = (
    "bc17ee74409543d1b57f3aee65088e990ab21ac83dc75ac46fbd1f97f04b6621"
)
PINNED_OFFICIAL_METHOD_SHA256 = (
    "d33571d09a3a9cb428a84dece5af233e66267b831d3043c90e3ad77cb8de5178"
)

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import python_re_universal_public_oracle_stage06 as stage06


frozen = stage06.frozen
official_locale = stage06.official_locale
frozen.candidate_free()
frozen.require(
    Path(stage06.__file__).resolve()
    == ROOT / "tools/python_re_universal_public_oracle_stage06.py"
    and stage06.REQUIRED_CANDIDATES == REQUIRED_CANDIDATES
    and stage06.BASE_AUDIT_REPORT_SHA256 == PINNED_BASE_REPORT_SHA256
    and stage06.STRICT_AUDIT_REPORT_SHA256 == PINNED_STRICT_REPORT_SHA256
    and stage06.LOCALE_REPORT_SHA256 == PINNED_LOCALE_REPORT_SHA256
    and official_locale.SELECTED_METHOD_SHA256 == PINNED_OFFICIAL_METHOD_SHA256
    and frozen.SCHEMA == "rebar-python-re-universal-public-oracle-v1"
    and frozen.EXPECTED_CASES == 8_192
    and frozen.OBSERVATIONS_PER_CASE == 48
    and frozen.EXPECTED_OBSERVATIONS == 393_216,
    "stage-07 substituted its current Python, locale, independence, or public oracle",
)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def cohort_seed(name: str) -> str:
    frozen.require(
        name in {item[0] for item in COHORTS},
        "stage-07 rejected an unrecognized public contract cohort",
    )
    return hashlib.sha256(
        canonical({"domain": SEED_DOMAIN, "seed": SEED, "cohort": name})
    ).hexdigest()


def build_matrix() -> list[dict[str, Any]]:
    matrix: list[dict[str, Any]] = []
    for cohort, operation, count in COHORTS:
        seed = cohort_seed(cohort)
        for index in range(count):
            row: dict[str, Any] = {
                "id": f"{cohort}:{index:04d}",
                "cohort": cohort,
                "operation": operation,
                "index": index,
                "seed": seed,
            }
            if cohort == "real-locale":
                row.update(
                    {
                        "byte": index % 256,
                        "locale": ("iso88591", "utf8")[(index // 256) % 2],
                        "compiled_before_switch": bool(index // 512),
                    }
                )
            if cohort == "shared-pattern-threads":
                row["threads"] = (4, 8)[index % 2]
            matrix.append(row)
    validate_matrix(matrix)
    return matrix


def validate_matrix(matrix: Any) -> None:
    frozen.require(
        isinstance(matrix, list)
        and len(matrix) == EXPECTED_CASES
        and len(COHORTS) == 8
        and sum(count for _, _, count in COHORTS) == EXPECTED_CASES,
        "stage-07 weakened the eight-cohort public obligation denominator",
    )
    names: set[str] = set()
    counts = {name: 0 for name, _, _ in COHORTS}
    operations = {name: operation for name, operation, _ in COHORTS}
    indices = {name: set() for name, _, _ in COHORTS}
    for row in matrix:
        frozen.require(
            isinstance(row, dict)
            and isinstance(row.get("id"), str)
            and row["id"] not in names
            and row.get("cohort") in counts
            and type(row.get("index")) is int
            and row["id"] == f"{row['cohort']}:{row['index']:04d}"
            and row.get("operation") == operations[row["cohort"]]
            and row.get("seed") == cohort_seed(row["cohort"]),
            "stage-07 duplicated or substituted a deterministic public obligation",
        )
        names.add(row["id"])
        counts[row["cohort"]] += 1
        indices[row["cohort"]].add(row["index"])
    for name, _, expected in COHORTS:
        frozen.require(
            counts[name] == expected and indices[name] == set(range(expected)),
            f"stage-07 lost or duplicated a public {name} obligation",
        )
    locale_rows = [row for row in matrix if row["cohort"] == "real-locale"]
    frozen.require(
        len(locale_rows) == 1_024
        and {
            (row["byte"], row["locale"], row["compiled_before_switch"])
            for row in locale_rows
        }
        == {
            (byte, locale, switched)
            for byte in range(256)
            for locale in ("iso88591", "utf8")
            for switched in (False, True)
        },
        "stage-07 omitted a genuine byte, locale, or compile-before-switch state",
    )
    threaded = [row for row in matrix if row["cohort"] == "shared-pattern-threads"]
    frozen.require(
        sum(row["threads"] == 4 for row in threaded) == 128
        and sum(row["threads"] == 8 for row in threaded) == 128,
        "stage-07 weakened deterministic four- and eight-thread coverage",
    )


def exact_output(value: Any, expected: str) -> str:
    frozen.require(type(value) is str, "stage-07 evidence path must be exact text")
    path = PurePosixPath(value)
    frozen.require(
        not path.is_absolute()
        and ".." not in path.parts
        and "\\" not in value
        and "\x00" not in value
        and str(path) == value
        and value == expected,
        "stage-07 rejected a foreign or nonexclusive public evidence path",
    )
    return value


def _normalize(value: Any) -> Any:
    if value is None or type(value) in (bool, int, str):
        return value
    if isinstance(value, bytes):
        return {"type": "bytes", "hex": value.hex()}
    if isinstance(value, bytearray):
        return {"type": "bytearray", "hex": bytes(value).hex()}
    if isinstance(value, tuple):
        return {"type": "tuple", "items": [_normalize(item) for item in value]}
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    if isinstance(value, dict):
        return {
            "type": "dict",
            "items": [
                [_normalize(key), _normalize(item)]
                for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
            ],
        }
    if isinstance(value, memoryview):
        return {"type": "memoryview", "hex": value.tobytes().hex()}
    if isinstance(value, BaseException):
        return {
            "type": value.__class__.__name__,
            "args": _normalize(value.args),
            **{
                field: _normalize(getattr(value, field))
                for field in ("msg", "pattern", "pos", "lineno", "colno")
                if hasattr(value, field)
            },
        }
    raise TypeError("cannot erase a public observation type: " + type(value).__name__)


def _match_value(value: Any) -> Any:
    if value is None:
        return None
    return {
        "span": _normalize(value.span()),
        "groups": _normalize(value.groups()),
        "groupdict": _normalize(value.groupdict()),
        "lastindex": value.lastindex,
        "lastgroup": value.lastgroup,
        "pos": value.pos,
        "endpos": value.endpos,
    }


def _surface_obligation(module: Any, index: int) -> Any:
    import inspect

    exports = (
        "compile", "search", "match", "fullmatch", "findall", "finditer",
        "split", "sub", "subn", "escape", "purge", "Pattern", "Match",
        "Scanner", "RegexFlag", "PatternError", "error", "A", "ASCII", "I",
        "IGNORECASE", "L", "LOCALE", "M", "MULTILINE", "S", "DOTALL", "X",
        "VERBOSE", "U", "UNICODE", "DEBUG", "NOFLAG",
    )
    name = exports[index % len(exports)]
    present = hasattr(module, name)
    if not present:
        return {"name": name, "present": False}
    item = getattr(module, name)
    result: dict[str, Any] = {"name": name, "present": True}
    if name in ("A", "ASCII", "I", "IGNORECASE", "L", "LOCALE", "M",
                "MULTILINE", "S", "DOTALL", "X", "VERBOSE", "U", "UNICODE",
                "DEBUG", "NOFLAG"):
        result.update(value=int(item), representation=repr(item))
    elif name in ("compile", "search", "match", "fullmatch", "findall",
                  "finditer", "split", "sub", "subn", "escape", "purge"):
        result["signature"] = str(inspect.signature(item))
    elif name == "error":
        result["is_pattern_error"] = item is getattr(module, "PatternError", item)
    elif name in ("Pattern", "Match", "RegexFlag", "PatternError", "Scanner"):
        result["class_name"] = item.__name__
    if index % 3 == 0 and hasattr(module, "__all__"):
        result["listed"] = name in module.__all__
    return result


def _grammar_obligation(module: Any, index: int) -> Any:
    invalid = (
        "(", "[", "*", "a**", "(?", "(?P<", "(?P<1>x)", "(?P<x>a)(?P<x>b)",
        "(?P=x)", "\\", "\\x", "\\u123", "\\U00110000", "[z-a]",
        "(?<=a+)b", "(?i-a:x)", "(?L:x)", "a{3,2}", "(?P<é>x)", "[a--b]",
        "[a&&b]", "[[a]", "(?z)", "(?(missing)a|b)",
    )
    flags = (0, module.I, module.M, module.S, module.X, module.A)
    pattern = invalid[index % len(invalid)]
    flag = flags[(index // len(invalid)) % len(flags)]
    if index % 17 == 0:
        pattern = pattern.encode("utf-8", "surrogatepass")
    module.compile(pattern, flag)
    return {"compiled": True, "pattern": _normalize(pattern), "flags": int(flag)}


def _locale_obligation(module: Any, row: dict[str, Any]) -> Any:
    import locale

    value = bytes((row["byte"],))
    target = official_locale.LOCALE_NAMES[row["locale"]]
    other_key = "utf8" if row["locale"] == "iso88591" else "iso88591"
    other = official_locale.LOCALE_NAMES[other_key]
    saved = locale.setlocale(locale.LC_CTYPE)
    try:
        locale.setlocale(locale.LC_CTYPE, other if row["compiled_before_switch"] else target)
        patterns = (
            module.compile(rb"\w", module.L),
            module.compile(rb"\W", module.L),
            module.compile(rb"(?i:[a-z])", module.L),
            module.compile(rb"\b\w+\b", module.L),
            module.compile(rb"(?i)([a-z])\1", module.L),
        )
        locale.setlocale(locale.LC_CTYPE, target)
        return {
            "byte": row["byte"],
            "locale": row["locale"],
            "compiled_before_switch": row["compiled_before_switch"],
            "word": _match_value(patterns[0].fullmatch(value)),
            "nonword": _match_value(patterns[1].fullmatch(value)),
            "ignorecase": _match_value(patterns[2].fullmatch(value)),
            "boundary": _match_value(patterns[3].search(value)),
            "backreference": _match_value(patterns[4].fullmatch(value + value)),
        }
    finally:
        locale.setlocale(locale.LC_CTYPE, saved)


def _buffer_obligation(module: Any, index: int) -> Any:
    raw = bytearray(b"xaba\x00aba-z")
    choice = index % 8
    if choice == 0:
        subject: Any = bytes(raw)
    elif choice == 1:
        subject = raw
    elif choice == 2:
        subject = memoryview(raw)
    elif choice == 3:
        subject = memoryview(raw)[::2]
    elif choice == 4:
        subject = memoryview(raw)[1:8]
    elif choice == 5:
        subject = memoryview(raw)
        subject.release()
    elif choice == 6:
        subject = memoryview(bytes(raw))
    else:
        subject = memoryview(raw).cast("B")
    pattern = module.compile(rb"(?P<item>a)(b)?")
    match = pattern.search(subject, index % 3)
    return {
        "subject_kind": (
            "memoryview" if isinstance(subject, memoryview)
            else type(subject).__name__
        ),
        "match": _match_value(match),
        "findall": _normalize(pattern.findall(subject)),
    }


def _object_obligation(module: Any, index: int) -> Any:
    import copy
    import pickle
    import weakref

    pattern = module.compile(r"(?P<word>a+)(b)?", module.I)
    sample = "xxAAAb"
    choice = index % 8
    if choice == 0:
        return {"hash": hash(pattern), "self_equal": pattern == pattern}
    if choice == 1:
        return {"same": copy.copy(pattern) is pattern}
    if choice == 2:
        return {"same": copy.deepcopy(pattern) is pattern}
    if choice == 3:
        protocol = (0, 2, 4, pickle.HIGHEST_PROTOCOL)[(index // 8) % 4]
        restored = pickle.loads(pickle.dumps(pattern, protocol=protocol))
        return {
            "protocol": protocol,
            "pattern": restored.pattern,
            "flags": restored.flags,
            "equal": restored == pattern,
            "match": _match_value(restored.search(sample)),
        }
    if choice == 4:
        reference = weakref.ref(pattern)
        return {"reference_alive": reference() is pattern}
    match = pattern.search(sample)
    if choice == 5:
        return _match_value(match)
    if choice == 6:
        return {"groupindex": _normalize(dict(pattern.groupindex))}
    return {
        "word": _normalize(match.group("word")),
        "numbered": _normalize(match.group(1)),
        "span": _normalize(match.span("word")),
    }


def _callback_obligation(module: Any, index: int) -> Any:
    events: list[Any] = []
    pattern = module.compile(r"(?P<word>a+)|(?P<digit>\d+)")
    subject = "aa-12-a-3"
    choice = index % 6
    if choice in (0, 1, 2):
        def replacement(match: Any) -> str:
            nested = module.search(r"a|\d", match.group())
            events.append((match.lastgroup, match.span(), nested.group() if nested else None))
            if choice == 2 and len(events) == 2:
                raise ValueError("stage07 callback propagation")
            return "<" + match.group() + ">"

        result = (
            pattern.subn(replacement, subject)
            if choice == 1
            else pattern.sub(replacement, subject)
        )
        return {"result": _normalize(result), "events": _normalize(events)}
    if choice == 3:
        return {
            "result": pattern.sub(r"[\g<word>\g<digit>]", subject),
            "events": [],
        }
    if choice == 4:
        empty = module.compile(r"(?=a)|a")
        return {"spans": [_normalize(item.span()) for item in empty.finditer("aa")]}

    def action(scanner: Any, token: str) -> Any:
        events.append(token)
        return token.upper()

    scanner = module.Scanner([(r"a+", action), (r"\d+", action), (r"-", None)])
    scanned, remainder = scanner.scan(subject)
    return {
        "result": _normalize(scanned),
        "remainder": _normalize(remainder),
        "events": _normalize(events),
    }


def _thread_obligation(module: Any, row: dict[str, Any]) -> Any:
    import threading

    count = row["threads"]
    shared = module.compile(r"(?P<word>a+)|(?P<number>\d+)")
    barrier = threading.Barrier(count)
    observations: list[Any] = [None] * count

    def run(position: int) -> None:
        try:
            barrier.wait()
            subject = ("aa-" if position % 2 == 0 else "bbb-") + str(
                row["index"] + position
            )
            observations[position] = {
                "position": position,
                "findall": _normalize(shared.findall(subject)),
                "search": _match_value(shared.search(subject)),
            }
        except BaseException as error:
            observations[position] = {
                "position": position,
                "error": _normalize(error),
            }

    threads = [threading.Thread(target=run, args=(position,)) for position in range(count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)
    if any(thread.is_alive() for thread in threads):
        barrier.abort()
        raise RuntimeError("the deterministic shared-pattern thread did not join")
    return {"threads": count, "observations": observations}


def _unicode_obligation(module: Any, index: int) -> Any:
    subjects = (
        "", "a", "\n", "İ", "ı", "ſ", "K", "é", "ß", "𝄞",
        "\ud800", "\udfff", "a\x00b", "１２", "a\u0301",
        "a" * 4_096,
    )
    patterns = (
        r".", r"\w+", r"\W", r"\b", r"\B", r"^", r"$",
        r"(?i)[a-z]", r"(?a)\w+", r"(?s).+", r"(?m)^a",
        r"(?P<x>a)?(?(x)b|c)",
    )
    subject = subjects[index % len(subjects)]
    expression = patterns[(index // len(subjects)) % len(patterns)]
    pattern = module.compile(expression)
    positions = (-10, -1, 0, 1, len(subject), len(subject) + 10)
    position = positions[(index // (len(subjects) * len(patterns))) % len(positions)]
    end = positions[(index // 7) % len(positions)]
    return {
        "pattern": expression,
        "subject": subject,
        "position": position,
        "end": end,
        "search": _match_value(pattern.search(subject, position, end)),
        "match": _match_value(pattern.match(subject, position, end)),
        "fullmatch": _match_value(pattern.fullmatch(subject, position, end)),
    }


def evaluate_case(module: Any, row: dict[str, Any]) -> dict[str, Any]:
    import warnings

    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        try:
            name = row["cohort"]
            if name == "public-surface":
                value = _surface_obligation(module, row["index"])
            elif name == "invalid-grammar":
                value = _grammar_obligation(module, row["index"])
            elif name == "real-locale":
                value = _locale_obligation(module, row)
            elif name == "buffer-lifetime":
                value = _buffer_obligation(module, row["index"])
            elif name == "object-contract":
                value = _object_obligation(module, row["index"])
            elif name == "callback-scanner":
                value = _callback_obligation(module, row["index"])
            elif name == "shared-pattern-threads":
                value = _thread_obligation(module, row)
            elif name == "bounded-unicode":
                value = _unicode_obligation(module, row["index"])
            else:
                raise frozen.OracleIntegrityError("unrecognized frozen obligation")
            outcome: dict[str, Any] = {"status": "returned", "value": _normalize(value)}
        except (Exception, RecursionError) as error:
            outcome = {"status": "raised", "exception": _normalize(error)}
        outcome["warnings"] = [
            {"category": item.category.__name__, "message": str(item.message)}
            for item in captured
        ]
        return {"id": row["id"], "cohort": row["cohort"], **outcome}


def _validate_current_public_report(
    report: Any, provenance: dict[str, Any]
) -> None:
    frozen.require(isinstance(report, dict), "the current public proof is incomplete")
    expected: dict[str, Any] = {
        "schema": frozen.SCHEMA,
        "status": "PASS",
        "selected": "all",
        "selected_candidates": list(REQUIRED_CANDIDATES),
        "completed_candidates": list(REQUIRED_CANDIDATES),
        "comparison_complete": True,
        "failed_candidate": None,
        "worker_failure": None,
        "python": "3.14.6",
        "seed": frozen.SEED,
        "seed_domain": frozen.SEED_DOMAIN,
        "cases": 8_192,
        "grammar_family_count": 16,
        "input_stratum_count": 16,
        "examples_per_stratum": 32,
        "case_sha256": stage06.previous.FROZEN_CASE_SHA256,
        "observations_per_case": 48,
        "observations_per_candidate": 393_216,
        "total_comparisons": 1_179_648,
        "planned_total_comparisons": 1_179_648,
        "mismatches": 0,
        "performance": "NOT MEASURED",
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "external_regex_packages": 0,
    }
    for field, value in expected.items():
        frozen.require(
            report.get(field) == value and type(report.get(field)) is type(value),
            f"stage-07 rejected a weakened current public comparison: {field}",
        )
    audit = report.get("audit")
    frozen.require(
        isinstance(audit, dict)
        and audit.get("audit_sha256") == PINNED_BASE_REPORT_SHA256
        and audit.get("oracle_source_sha256") == PINNED_STAGE06_SOURCE_SHA256
        and audit.get("postfinal_no_delegation_audit_sha256")
        == PINNED_STRICT_REPORT_SHA256
        and audit.get("official_locale_report_sha256")
        == PINNED_LOCALE_REPORT_SHA256
        and audit.get("official_locale_methods_per_role") == 146
        and audit.get("official_locale_total_method_results") == 584
        and audit.get("official_locale_skipped") == 0
        and audit.get("source_sha256") == provenance.get("source_sha256")
        and audit.get("native_binary_sha256")
        == provenance.get("native_binary_sha256"),
        "stage-07 rejected stale public sources, mapped native engines, or real locales",
    )
    candidates = report.get("candidate_reports")
    frozen.require(
        isinstance(candidates, dict) and set(candidates) == set(REQUIRED_CANDIDATES),
        "the current all-engine proof omitted an independent native family",
    )
    for family in REQUIRED_CANDIDATES:
        result = candidates[family]
        frozen.require(
            isinstance(result, dict)
            and result.get("candidate") == family
            and result.get("module") == f"candidates.{family}_candidate"
            and result.get("status") == "PASS"
            and result.get("cases") == 8_192
            and result.get("observations_per_case") == 48
            and result.get("checks") == 393_216
            and result.get("expected_checks") == 393_216
            and result.get("comparison_complete") is True
            and result.get("mismatches") == 0
            and result.get("worker_failure") is None
            and result.get("benchmark_or_timing_executed") is False
            and result.get("holdout_cases_read") == 0
            and result.get("external_regex_packages") == 0,
            f"the current {family} public compatibility proof is incomplete",
        )


def _authenticate_current_provenance() -> dict[str, Any]:
    """Authenticate only exact, current, public Phase-1 correctness evidence."""

    frozen.candidate_free()
    official_locale.verify_runtime()
    source = official_locale.checked_repo_path(SOURCE_RELATIVE)
    protocol = official_locale.checked_repo_path(PROTOCOL_RELATIVE)
    source_digest = official_locale.sha256_path(
        source, maximum=frozen.MAX_SOURCE_BYTES
    )
    protocol_digest = official_locale.sha256_path(
        protocol, maximum=frozen.MAX_SOURCE_BYTES
    )
    previous_source = official_locale.checked_repo_path(
        "tools/python_re_universal_public_oracle_stage06.py"
    )
    frozen.require(
        official_locale.sha256_path(
            previous_source, maximum=frozen.MAX_SOURCE_BYTES
        )
        == PINNED_STAGE06_SOURCE_SHA256,
        "the exact previous Phase-1 oracle source has changed",
    )
    provenance = stage06.stage06_verified_provenance(REQUIRED_CANDIDATES)
    public, public_digest = stage06._read_public_document(
        stage06.OUTPUT_RELATIVE,
        expected_sha256=PINNED_STAGE06_REPORT_SHA256,
    )
    frozen.require(
        public_digest == PINNED_STAGE06_REPORT_SHA256,
        "the exact previous all-engine public proof has changed",
    )
    _validate_current_public_report(public, provenance)
    matrix = build_matrix()
    frozen.require(
        digest(matrix) == MATRIX_SHA256,
        "the frozen stage-07 matrix changed before a production worker",
    )
    frozen.candidate_free()
    return {
        "source_path": SOURCE_RELATIVE,
        "source_sha256": source_digest,
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": protocol_digest,
        "previous_public_source_sha256": PINNED_STAGE06_SOURCE_SHA256,
        "previous_public_report_path": stage06.OUTPUT_RELATIVE,
        "previous_public_report_sha256": PINNED_STAGE06_REPORT_SHA256,
        "previous_public_cases": 8_192,
        "previous_public_comparisons": 1_179_648,
        "base_audit_path": stage06.BASE_AUDIT_REPORT_RELATIVE,
        "base_audit_sha256": PINNED_BASE_REPORT_SHA256,
        "strict_audit_path": stage06.STRICT_AUDIT_REPORT_RELATIVE,
        "strict_audit_sha256": PINNED_STRICT_REPORT_SHA256,
        "official_locale_path": stage06.LOCALE_REPORT_RELATIVE,
        "official_locale_sha256": PINNED_LOCALE_REPORT_SHA256,
        "official_selected_method_sha256": PINNED_OFFICIAL_METHOD_SHA256,
        "official_methods_per_role": 146,
        "official_role_count": 4,
        "official_skipped": 0,
        "source_sha256_by_family": provenance["source_sha256"],
        "native_sha256_by_family": provenance["native_binary_sha256"],
    }


class _ForbiddenRegexModule(types.ModuleType):
    """Fail visibly if a native candidate tries an unowned matching engine."""

    def __getattr__(self, name: str) -> Any:
        raise ImportError(
            "stage-07 blocked external or cross-family matching: " + self.__name__
        )


def _poison_cached_module_aliases(
    modules: dict[str, Any],
    targets: tuple[Any, ...],
    replacement: Any,
) -> int:
    count = 0
    for imported in tuple(modules.values()):
        if not isinstance(imported, types.ModuleType):
            continue
        try:
            bindings = tuple(vars(imported).items())
        except TypeError:
            continue
        for name, value in bindings:
            if any(value is target for target in targets):
                try:
                    setattr(imported, name, replacement)
                except (AttributeError, TypeError):
                    continue
                count += 1
    return count


def _validate_owned_native_loader(
    *,
    family: str,
    requested: Any,
    expected_path: str,
    observed_sha256: str,
    expected_sha256: str,
) -> str:
    frozen.require(
        family == "zig"
        and type(requested) is str
        and requested == expected_path
        and "\x00" not in requested
        and official_locale.is_sha256(observed_sha256)
        and official_locale.is_sha256(expected_sha256)
        and observed_sha256 == expected_sha256,
        "stage-07 blocked a foreign, disguised, or stale native matching engine",
    )
    return requested


def _install_family_guard(
    family: str, expected_native: dict[str, str]
) -> dict[str, Any]:
    import _ctypes
    import builtins
    import ctypes

    frozen.require(
        family in REQUIRED_CANDIDATES,
        "stage-07 refuses an unaudited candidate family",
    )
    names = {
        "re", "_sre", "regex", "re2", "pcre", "pcre2",
        "candidates.ast_candidate",
    }
    names.update(
        f"candidates.{other}_candidate"
        for other in REQUIRED_CANDIDATES
        if other != family
    )
    original_modules = tuple(
        module for name in names if (module := sys.modules.get(name)) is not None
    )
    blocker = _ForbiddenRegexModule("stage07_blocked_regex")
    poisoned_aliases = _poison_cached_module_aliases(
        sys.modules, original_modules, blocker
    )
    for name in names:
        sys.modules[name] = blocker

    original_import = builtins.__import__

    def guarded_import(
        name: str,
        globals: Any = None,
        locals: Any = None,
        fromlist: Any = (),
        level: int = 0,
    ) -> Any:
        cross_family_from_import = name == "candidates" and any(
            f"candidates.{item}" in names
            for item in (fromlist or ())
            if isinstance(item, str)
        )
        if (
            cross_family_from_import
            or name in names
            or any(name.startswith(item + ".") for item in names)
        ):
            raise ImportError("stage-07 blocked unowned matching import: " + name)
        return original_import(name, globals, locals, fromlist, level)

    builtins.__import__ = guarded_import
    original_cdll = ctypes.CDLL
    original_private_loader = ctypes._dlopen
    original_extension_loader = _ctypes.dlopen
    allowed_path = ROOT / "candidates/_zig_probe.so"
    expected_zig_sha256 = expected_native.get("candidates/_zig_probe.so")

    def owned_library(name: Any) -> str:
        if not isinstance(name, (str, os.PathLike)):
            raise ImportError("stage-07 blocked an unowned native library path")
        resolved = Path(name).resolve(strict=True)
        if resolved != allowed_path.resolve(strict=True):
            raise ImportError("stage-07 blocked a foreign native matching library")
        observed = official_locale.sha256_path(resolved)
        return _validate_owned_native_loader(
            family=family,
            requested=str(resolved),
            expected_path=str(allowed_path.resolve(strict=True)),
            observed_sha256=observed,
            expected_sha256=(
                expected_zig_sha256 if isinstance(expected_zig_sha256, str) else ""
            ),
        )

    def guarded_cdll(name: Any, *args: Any, **kwargs: Any) -> Any:
        return original_cdll(owned_library(name), *args, **kwargs)

    def guarded_private_loader(name: Any, *args: Any, **kwargs: Any) -> Any:
        return original_private_loader(owned_library(name), *args, **kwargs)

    def guarded_extension_loader(name: Any, *args: Any, **kwargs: Any) -> Any:
        return original_extension_loader(owned_library(name), *args, **kwargs)

    ctypes.CDLL = guarded_cdll
    ctypes._dlopen = guarded_private_loader
    _ctypes.dlopen = guarded_extension_loader
    ctypes.cdll._dlltype = guarded_cdll
    _poison_cached_module_aliases(
        sys.modules, (original_cdll,), guarded_cdll
    )
    _poison_cached_module_aliases(
        sys.modules, (original_private_loader,), guarded_private_loader
    )
    _poison_cached_module_aliases(
        sys.modules, (original_extension_loader,), guarded_extension_loader
    )
    return {
        "enabled": True,
        "family": family,
        "stdlib_re_blocked": True,
        "cpython_sre_blocked": True,
        "third_party_regex_blocked": True,
        "cross_family_blocked": True,
        "foreign_dynamic_libraries_blocked": True,
        "native_loader_aliases_blocked": list(NATIVE_LOADER_ALIASES),
        "cached_regex_aliases_poisoned": poisoned_aliases,
        "prohibited_modules": sorted(names),
    }


def _verify_family_native_mappings(
    family: str, provenance: dict[str, Any]
) -> dict[str, str]:
    actual = provenance["native_sha256_by_family"].get(family)
    frozen.require(
        isinstance(actual, dict), "the candidate has no current audited native role"
    )
    with open("/proc/self/maps", "rb") as stream:
        mappings = stream.read(4 * 1024 * 1024 + 1)
    frozen.require(
        len(mappings) <= 4 * 1024 * 1024,
        "the isolated worker native mapping is not safely bounded",
    )
    for relative, expected in actual.items():
        path = official_locale.checked_repo_path(relative)
        frozen.require(
            official_locale.sha256_path(path) == expected
            and os.fsencode(str(path)) in mappings,
            f"the actual isolated {family} native mapping changed: {relative}",
        )
    return dict(actual)


def _worker_report(role: str, expected_source_sha256: str) -> dict[str, Any]:
    official_locale.verify_runtime()
    source = official_locale.checked_repo_path(SOURCE_RELATIVE)
    frozen.require(
        official_locale.sha256_path(source, maximum=frozen.MAX_SOURCE_BYTES)
        == expected_source_sha256,
        "the source-bound isolated stage-07 worker changed before execution",
    )
    matrix = build_matrix()
    frozen.require(
        digest(matrix) == MATRIX_SHA256,
        "the isolated worker changed the complete frozen obligation matrix",
    )
    if role in ("stdlib-a", "stdlib-b"):
        frozen.candidate_free()
        module = importlib.import_module("re")
        guards: dict[str, Any] = {"baseline_only": True, "candidate_imported": False}
        natives: dict[str, str] = {}
    else:
        frozen.require(role in REQUIRED_CANDIDATES, "an unknown worker role was rejected")
        provenance = _authenticate_current_provenance()
        expected_native = provenance["native_sha256_by_family"].get(role)
        frozen.require(
            isinstance(expected_native, dict) and bool(expected_native),
            "the isolated candidate has no exact current native-role proof",
        )
        guards = _install_family_guard(role, expected_native)
        module = importlib.import_module(f"candidates.{role}_candidate")
        natives = _verify_family_native_mappings(role, provenance)
        loaded = {
            name for name, value in sys.modules.items()
            if name.startswith("candidates.")
            and value is not None
            and not isinstance(value, _ForbiddenRegexModule)
        }
        allowed_prefix = {f"candidates.{role}_candidate"}
        if role == "rust":
            allowed_prefix.add("candidates._rust_bridge")
        elif role == "vm":
            allowed_prefix.add("candidates._vm_native")
        else:
            allowed_prefix.add("candidates._zig_bridge")
        frozen.require(
            loaded <= allowed_prefix,
            "the isolated candidate imported a different regex implementation",
        )
        guards["loaded_candidate_modules"] = sorted(loaded)
    observations = [evaluate_case(module, row) for row in matrix]
    frozen.require(
        len(observations) == EXPECTED_CASES
        and [record.get("id") for record in observations]
        == [row["id"] for row in matrix],
        "an isolated worker concealed or reordered a public obligation",
    )
    return {
        "schema": SCHEMA + "-worker",
        "status": "PASS",
        "role": role,
        "python": "3.14.6",
        "source_sha256": expected_source_sha256,
        "seed": SEED,
        "seed_domain": SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "cases": EXPECTED_CASES,
        "cohort_cases": {name: count for name, _, count in COHORTS},
        "records": observations,
        "record_sha256": digest(observations),
        "guard": guards,
        "native_binary_sha256": natives,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }


WORKER_BOOTSTRAP = (
    "import sys;"
    "sys.path.insert(0,sys.argv[1]);"
    "from tools.python_re_universal_public_oracle_stage07 "
    "import _worker_entry;"
    "raise SystemExit(_worker_entry(sys.argv[2],sys.argv[3]))"
)


def _worker_entry(role: str, source_sha256: str) -> int:
    try:
        report = _worker_report(role, source_sha256)
        sys.stdout.buffer.write(canonical(report) + b"\n")
        sys.stdout.buffer.flush()
        return 0
    except (Exception, RecursionError) as error:
        failure = {
            "schema": SCHEMA + "-worker",
            "status": "FAIL",
            "role": role,
            "error": _normalize(error),
            "benchmark_or_timing_executed": False,
            "performance": "NOT MEASURED",
        }
        sys.stdout.buffer.write(canonical(failure) + b"\n")
        sys.stdout.buffer.flush()
        return 1


def _worker_environment(locale_root: Path) -> dict[str, str]:
    return {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "PYTHONPATH": str(ROOT),
        "LOCPATH": str(locale_root),
        "LC_ALL": "C",
        "PATH": "/usr/bin:/bin",
    }


def _validate_worker_report(
    document: Any,
    *,
    role: str,
    source_sha256: str,
) -> dict[str, Any]:
    frozen.require(isinstance(document, dict), "the isolated worker report is invalid")
    exact: dict[str, Any] = {
        "schema": SCHEMA + "-worker",
        "status": "PASS",
        "role": role,
        "python": "3.14.6",
        "source_sha256": source_sha256,
        "seed": SEED,
        "seed_domain": SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "cases": EXPECTED_CASES,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    for field, value in exact.items():
        frozen.require(
            document.get(field) == value
            and type(document.get(field)) is type(value),
            f"the stage-07 isolated {role} worker changed {field}",
        )
    frozen.require(
        document.get("cohort_cases")
        == {name: count for name, _, count in COHORTS},
        f"the isolated {role} worker changed its public cohort denominators",
    )
    records = document.get("records")
    frozen.require(
        isinstance(records, list)
        and len(records) == EXPECTED_CASES
        and document.get("record_sha256") == digest(records)
        and [record.get("id") for record in records]
        == [row["id"] for row in build_matrix()],
        f"the isolated {role} worker concealed or fabricated public observations",
    )
    guards = document.get("guard")
    if role in ("stdlib-a", "stdlib-b"):
        frozen.require(
            guards == {"baseline_only": True, "candidate_imported": False}
            and document.get("native_binary_sha256") == {},
            "the Python self-oracle imported a candidate or a native regex engine",
        )
    else:
        frozen.require(
            isinstance(guards, dict)
            and guards.get("enabled") is True
            and guards.get("family") == role
            and guards.get("stdlib_re_blocked") is True
            and guards.get("cpython_sre_blocked") is True
            and guards.get("third_party_regex_blocked") is True
            and guards.get("cross_family_blocked") is True
            and guards.get("foreign_dynamic_libraries_blocked") is True
            and guards.get("native_loader_aliases_blocked")
            == list(NATIVE_LOADER_ALIASES)
            and type(guards.get("cached_regex_aliases_poisoned")) is int
            and isinstance(document.get("native_binary_sha256"), dict)
            and bool(document["native_binary_sha256"]),
            f"the isolated {role} worker weakened its owned-engine guard",
        )
    return document


class PublicWorkerFailure(frozen.OracleIntegrityError):
    """Retain an actual bounded isolated-worker failure for durable evidence."""

    def __init__(self, role: str, message: str, details: dict[str, Any]) -> None:
        super().__init__(message)
        self.role = role
        self.details = details


def _run_worker(
    role: str,
    *,
    source_sha256: str,
    locale_root: Path,
) -> dict[str, Any]:
    frozen.require(
        role in ("stdlib-a", "stdlib-b", *REQUIRED_CANDIDATES),
        "refusing an unaudited stage-07 worker role",
    )
    command = [
        str(PINNED_INTERPRETER),
        "-I",
        "-B",
        "-c",
        WORKER_BOOTSTRAP,
        str(ROOT),
        role,
        source_sha256,
    ]
    try:
        child = subprocess.run(
            command,
            cwd=str(ROOT),
            env=_worker_environment(locale_root),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=600,
        )
    except subprocess.SubprocessError as error:
        raise PublicWorkerFailure(
            role,
            f"the isolated {role} worker did not complete",
            {
                "kind": type(error).__name__,
                "exception": _normalize(error),
                "returncode": None,
            },
        ) from error
    if (
        not 0 < len(child.stdout) <= MAX_WORKER_BYTES
        or len(child.stderr) > MAX_WORKER_BYTES
    ):
        raise PublicWorkerFailure(
            role,
            f"the isolated {role} worker returned empty or excessive output",
            {
                "kind": "invalid-bounded-worker-output",
                "returncode": child.returncode,
                "stdout_bytes": len(child.stdout),
                "stderr_bytes": len(child.stderr),
                "stdout": _normalize(child.stdout[:MAX_WORKER_BYTES]),
                "stderr": _normalize(child.stderr[:MAX_WORKER_BYTES]),
            },
        )
    try:
        document = json.loads(child.stdout)
    except (UnicodeError, ValueError) as error:
        raise PublicWorkerFailure(
            role,
            f"the isolated {role} worker produced malformed public evidence",
            {
                "kind": "malformed-worker-evidence",
                "returncode": child.returncode,
                "stdout": _normalize(child.stdout),
                "stderr": _normalize(child.stderr),
                "exception": _normalize(error),
            },
        ) from error
    if child.returncode != 0:
        raise PublicWorkerFailure(
            role,
            f"the isolated {role} worker failed",
            {
                "kind": "worker-nonzero-exit",
                "returncode": child.returncode,
                "worker_report": document,
                "stderr": _normalize(child.stderr),
            },
        )
    return _validate_worker_report(
        document, role=role, source_sha256=source_sha256
    )


def _exclusive_evidence(document: dict[str, Any], relative: str) -> str:
    frozen.require(
        relative
        in {
            SELF_ORACLE_RELATIVE,
            SELF_ORACLE_FAILURE_RELATIVE,
            ALL_CANDIDATE_RELATIVE,
            *CANDIDATE_FAILURE_RELATIVES.values(),
        },
        "stage-07 refuses to create unapproved success or failure evidence",
    )
    exact_output(relative, relative)
    target = ROOT / relative
    parent = target.parent
    frozen.require(
        parent.is_dir()
        and not parent.is_symlink()
        and parent.resolve(strict=True).is_relative_to(ROOT.resolve(strict=True))
        and not target.is_symlink(),
        "the stage-07 exclusive public evidence escaped its approved directory",
    )
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(target, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as output:
            descriptor = -1
            output.write(canonical(document) + b"\n")
            output.flush()
            os.fsync(output.fileno())
        directory = os.open(parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    return official_locale.sha256_path(target, maximum=official_locale.MAX_JSON_BYTES)


def _mismatch_records(
    expected: list[dict[str, Any]], observed: list[dict[str, Any]]
) -> tuple[int, list[dict[str, Any]]]:
    frozen.require(
        len(expected) == len(observed) == EXPECTED_CASES,
        "a public obligation comparison silently changed its denominator",
    )
    mismatches: list[dict[str, Any]] = []
    count = 0
    for left, right in zip(expected, observed, strict=True):
        frozen.require(
            left.get("id") == right.get("id"),
            "a public obligation was substituted or reordered",
        )
        if left != right:
            count += 1
            frozen.require(
                len(mismatches) < MAX_MISMATCHES,
                "stage-07 cannot conceal or truncate a genuine public mismatch",
            )
            mismatches.append(
                {"id": left["id"], "expected": left, "actual": right}
            )
    return count, mismatches


def _preserve_worker_failure(
    *,
    role: str,
    error: BaseException,
    provenance: dict[str, Any],
    locales: dict[str, Any],
    baseline_records: list[dict[str, Any]] | None,
    completed_reports: dict[str, Any] | None = None,
    self_oracle_sha256: str | None = None,
) -> str:
    is_baseline = role in ("stdlib-a", "stdlib-b")
    frozen.require(
        is_baseline or role in REQUIRED_CANDIDATES,
        "refusing to persist an unaudited isolated-worker identity",
    )
    relative = (
        SELF_ORACLE_FAILURE_RELATIVE
        if is_baseline
        else CANDIDATE_FAILURE_RELATIVES[role]
    )
    details = (
        error.details
        if isinstance(error, PublicWorkerFailure)
        else {"kind": type(error).__name__, "exception": _normalize(error)}
    )
    document = {
        "schema": (
            SELF_ORACLE_SCHEMA + "-failure"
            if is_baseline
            else ALL_CANDIDATE_SCHEMA + "-failure"
        ),
        "status": "FAIL",
        "result": "FAIL",
        "failure_kind": "isolated-worker-failure",
        "failed_role": role,
        "source_path": SOURCE_RELATIVE,
        "source_sha256": provenance["source_sha256"],
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": provenance["protocol_sha256"],
        "seed": SEED,
        "seed_domain": SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "cohorts": len(COHORTS),
        "cohort_cases": {name: count for name, _, count in COHORTS},
        "expected_cases": EXPECTED_CASES,
        "baseline_records": baseline_records,
        "completed_candidate_reports": completed_reports,
        "self_oracle_path": None if is_baseline else SELF_ORACLE_RELATIVE,
        "self_oracle_sha256": self_oracle_sha256,
        "worker_failure": details,
        "current_provenance": provenance,
        "locales": locales,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    failure_digest = _exclusive_evidence(document, relative)
    return f"{relative} (sha256 {failure_digest})"


def _locale_metadata(locale_root: Path) -> dict[str, Any]:
    actual = official_locale.build_private_locales(locale_root)
    reference, _reference_digest = stage06._read_public_document(
        stage06.LOCALE_REPORT_RELATIVE,
        expected_sha256=PINNED_LOCALE_REPORT_SHA256,
    )
    frozen.require(
        actual == reference.get("locales"),
        "stage-07 generated locales different from the frozen genuine CPython proof",
    )
    verified = official_locale.verify_locale_reference(locale_root)
    frozen.require(
        verified == reference.get("locale_reference"),
        "stage-07 genuine CPython locale transitions failed before the worker",
    )
    return actual


def run_self_oracle() -> dict[str, Any]:
    """Run two real isolated Python references before any candidate is possible."""

    import tempfile

    provenance = _authenticate_current_provenance()
    destination = ROOT / SELF_ORACLE_RELATIVE
    frozen.require(
        not destination.exists() and not destination.is_symlink(),
        "the exclusive stage-07 Python self-oracle already exists",
    )
    frozen.candidate_free()
    with tempfile.TemporaryDirectory(
        prefix="rebar-public-contract-v7-locale-", dir="/tmp"
    ) as temporary:
        locale_root = Path(temporary)
        locales = _locale_metadata(locale_root)
        baseline_a: dict[str, Any] | None = None
        for baseline_role in ("stdlib-a", "stdlib-b"):
            try:
                observed = _run_worker(
                    baseline_role,
                    source_sha256=provenance["source_sha256"],
                    locale_root=locale_root,
                )
            except (Exception, RecursionError) as error:
                retained = _preserve_worker_failure(
                    role=baseline_role,
                    error=error,
                    provenance=provenance,
                    locales=locales,
                    baseline_records=(
                        baseline_a["records"] if baseline_a is not None else None
                    ),
                )
                raise frozen.OracleIntegrityError(
                    f"the isolated {baseline_role} failure was preserved in {retained}"
                ) from error
            if baseline_role == "stdlib-a":
                baseline_a = observed
            else:
                baseline_b = observed
        frozen.require(
            baseline_a is not None and isinstance(baseline_b, dict),
            "stage-07 did not run two independent pinned Python references",
        )
        mismatches, failures = _mismatch_records(
            baseline_a["records"], baseline_b["records"]
        )
        if mismatches or failures:
            failure = {
                "schema": SELF_ORACLE_SCHEMA + "-failure",
                "status": "FAIL",
                "result": "FAIL",
                "python": "3.14.6",
                "source_path": SOURCE_RELATIVE,
                "source_sha256": provenance["source_sha256"],
                "protocol_path": PROTOCOL_RELATIVE,
                "protocol_sha256": provenance["protocol_sha256"],
                "seed": SEED,
                "seed_domain": SEED_DOMAIN,
                "matrix_sha256": MATRIX_SHA256,
                "cohorts": len(COHORTS),
                "cohort_cases": {name: count for name, _, count in COHORTS},
                "cases": EXPECTED_CASES,
                "independent_stdlib_roles": ["stdlib-a", "stdlib-b"],
                "stdlib_checks": EXPECTED_CASES * 2,
                "baseline_record_sha256": baseline_a["record_sha256"],
                "second_record_sha256": baseline_b["record_sha256"],
                "baseline_records": baseline_a["records"],
                "second_records": baseline_b["records"],
                "mismatches": mismatches,
                "failure_records": failures,
                "failures_recorded": len(failures),
                "current_provenance": provenance,
                "locales": locales,
                "candidate_imports": 0,
                "candidate_processes": 0,
                "benchmark_or_timing_executed": False,
                "performance_fixtures_read": 0,
                "holdout_cases_read": 0,
                "performance": "NOT MEASURED",
            }
            failure_digest = _exclusive_evidence(
                failure, SELF_ORACLE_FAILURE_RELATIVE
            )
            raise frozen.OracleIntegrityError(
                "two isolated standard Python references disagree; all "
                + str(mismatches)
                + " mismatches were preserved in "
                + SELF_ORACLE_FAILURE_RELATIVE
                + " (sha256 "
                + failure_digest
                + ")"
            )
        frozen.candidate_free()
        report = {
            "schema": SELF_ORACLE_SCHEMA,
            "status": "PASS",
            "result": "PASS",
            "python": "3.14.6",
            "source_path": SOURCE_RELATIVE,
            "source_sha256": provenance["source_sha256"],
            "protocol_path": PROTOCOL_RELATIVE,
            "protocol_sha256": provenance["protocol_sha256"],
            "seed": SEED,
            "seed_domain": SEED_DOMAIN,
            "matrix_sha256": MATRIX_SHA256,
            "cohorts": len(COHORTS),
            "cohort_cases": {name: count for name, _, count in COHORTS},
            "cases": EXPECTED_CASES,
            "independent_stdlib_roles": ["stdlib-a", "stdlib-b"],
            "stdlib_checks": EXPECTED_CASES * 2,
            "baseline_record_sha256": baseline_a["record_sha256"],
            "second_record_sha256": baseline_b["record_sha256"],
            "baseline_records": baseline_a["records"],
            "mismatches": 0,
            "failure_records": [],
            "current_provenance": provenance,
            "locales": locales,
            "candidate_imports": 0,
            "candidate_processes": 0,
            "benchmark_or_timing_executed": False,
            "performance_fixtures_read": 0,
            "holdout_cases_read": 0,
            "performance": "NOT MEASURED",
        }
        evidence_sha256 = _exclusive_evidence(report, SELF_ORACLE_RELATIVE)
    frozen.candidate_free()
    return {
        "schema": SELF_ORACLE_SCHEMA,
        "status": "PASS",
        "cases": EXPECTED_CASES,
        "stdlib_checks": EXPECTED_CASES * 2,
        "mismatches": 0,
        "evidence": SELF_ORACLE_RELATIVE,
        "evidence_sha256": evidence_sha256,
        "benchmark_or_timing_executed": False,
        "performance": "NOT MEASURED",
    }


def _validate_self_oracle(
    document: Any, provenance: dict[str, Any]
) -> dict[str, Any]:
    frozen.require(isinstance(document, dict), "the required Python self-oracle is absent")
    required: dict[str, Any] = {
        "schema": SELF_ORACLE_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "python": "3.14.6",
        "source_path": SOURCE_RELATIVE,
        "source_sha256": provenance["source_sha256"],
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": provenance["protocol_sha256"],
        "seed": SEED,
        "seed_domain": SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "cohorts": 8,
        "cases": EXPECTED_CASES,
        "independent_stdlib_roles": ["stdlib-a", "stdlib-b"],
        "stdlib_checks": EXPECTED_CASES * 2,
        "mismatches": 0,
        "failure_records": [],
        "candidate_imports": 0,
        "candidate_processes": 0,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    for field, value in required.items():
        frozen.require(
            document.get(field) == value
            and type(document.get(field)) is type(value),
            f"stage-07 requires a genuinely passing Python self-oracle: {field}",
        )
    records = document.get("baseline_records")
    frozen.require(
        isinstance(records, list)
        and len(records) == EXPECTED_CASES
        and document.get("baseline_record_sha256") == digest(records)
        and document.get("second_record_sha256") == digest(records)
        and document.get("cohort_cases")
        == {name: count for name, _, count in COHORTS}
        and [record.get("id") for record in records]
        == [row["id"] for row in build_matrix()]
        and document.get("current_provenance") == provenance,
        "the Python self-oracle concealed a case or substituted current source evidence",
    )
    return document


def run_all_candidates() -> dict[str, Any]:
    """Require a complete real self-oracle before any isolated candidate starts."""

    import tempfile

    provenance = _authenticate_current_provenance()
    destination = ROOT / ALL_CANDIDATE_RELATIVE
    frozen.require(
        not destination.exists() and not destination.is_symlink(),
        "the exclusive stage-07 all-candidate evidence already exists",
    )
    self_oracle, self_oracle_digest = stage06._read_public_document(
        SELF_ORACLE_RELATIVE, expected_sha256=None
    )
    _validate_self_oracle(self_oracle, provenance)
    expected = self_oracle["baseline_records"]
    outcomes: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(
        prefix="rebar-public-contract-v7-locale-", dir="/tmp"
    ) as temporary:
        locale_root = Path(temporary)
        locales = _locale_metadata(locale_root)
        frozen.require(
            locales == self_oracle.get("locales"),
            "the candidate locales differ from both actual Python references",
        )
        for family in REQUIRED_CANDIDATES:
            try:
                worker = _run_worker(
                    family,
                    source_sha256=provenance["source_sha256"],
                    locale_root=locale_root,
                )
            except (Exception, RecursionError) as error:
                retained = _preserve_worker_failure(
                    role=family,
                    error=error,
                    provenance=provenance,
                    locales=locales,
                    baseline_records=expected,
                    completed_reports=outcomes,
                    self_oracle_sha256=self_oracle_digest,
                )
                raise frozen.OracleIntegrityError(
                    f"the isolated {family} failure was preserved in {retained}"
                ) from error
            mismatches, failures = _mismatch_records(expected, worker["records"])
            outcomes[family] = {
                "candidate": family,
                "module": f"candidates.{family}_candidate",
                "status": "PASS" if mismatches == 0 else "FAIL",
                "cases": EXPECTED_CASES,
                "cohort_cases": worker["cohort_cases"],
                "record_sha256": worker["record_sha256"],
                "mismatches": mismatches,
                "failure_records": failures,
                "failures_recorded": len(failures),
                "native_binary_sha256": worker["native_binary_sha256"],
                "guard": worker["guard"],
                "benchmark_or_timing_executed": False,
                "holdout_cases_read": 0,
                "performance": "NOT MEASURED",
            }
            if mismatches:
                failure = {
                    "schema": ALL_CANDIDATE_SCHEMA + "-failure",
                    "status": "FAIL",
                    "result": "FAIL",
                    "candidate": family,
                    "module": f"candidates.{family}_candidate",
                    "source_path": SOURCE_RELATIVE,
                    "source_sha256": provenance["source_sha256"],
                    "protocol_path": PROTOCOL_RELATIVE,
                    "protocol_sha256": provenance["protocol_sha256"],
                    "seed": SEED,
                    "seed_domain": SEED_DOMAIN,
                    "matrix_sha256": MATRIX_SHA256,
                    "cohorts": len(COHORTS),
                    "cohort_cases": worker["cohort_cases"],
                    "cases": EXPECTED_CASES,
                    "self_oracle_path": SELF_ORACLE_RELATIVE,
                    "self_oracle_sha256": self_oracle_digest,
                    "baseline_record_sha256": self_oracle[
                        "baseline_record_sha256"
                    ],
                    "candidate_record_sha256": worker["record_sha256"],
                    "baseline_records": expected,
                    "candidate_records": worker["records"],
                    "mismatches": mismatches,
                    "failure_records": failures,
                    "failures_recorded": len(failures),
                    "completed_candidate_reports": outcomes,
                    "current_provenance": provenance,
                    "locales": locales,
                    "native_binary_sha256": worker["native_binary_sha256"],
                    "guard": worker["guard"],
                    "benchmark_or_timing_executed": False,
                    "performance_fixtures_read": 0,
                    "holdout_cases_read": 0,
                    "performance": "NOT MEASURED",
                }
                failure_path = CANDIDATE_FAILURE_RELATIVES[family]
                failure_digest = _exclusive_evidence(failure, failure_path)
                raise frozen.OracleIntegrityError(
                    f"the {family} candidate failed {mismatches} frozen public "
                    f"obligations; every mismatch was preserved in {failure_path} "
                    f"(sha256 {failure_digest})"
                )
            frozen.require(
                worker["record_sha256"] == self_oracle["baseline_record_sha256"],
                f"the complete {family} public records do not match both Python references",
            )
        frozen.require(
            set(outcomes) == set(REQUIRED_CANDIDATES),
            "stage-07 omitted an independently implemented candidate",
        )
        report = {
            "schema": ALL_CANDIDATE_SCHEMA,
            "status": "PASS",
            "result": "PASS",
            "selected": "all",
            "selected_candidates": list(REQUIRED_CANDIDATES),
            "completed_candidates": list(REQUIRED_CANDIDATES),
            "comparison_complete": True,
            "python": "3.14.6",
            "source_path": SOURCE_RELATIVE,
            "source_sha256": provenance["source_sha256"],
            "protocol_path": PROTOCOL_RELATIVE,
            "protocol_sha256": provenance["protocol_sha256"],
            "seed": SEED,
            "seed_domain": SEED_DOMAIN,
            "matrix_sha256": MATRIX_SHA256,
            "cohorts": 8,
            "cohort_cases": {name: count for name, _, count in COHORTS},
            "cases_per_candidate": EXPECTED_CASES,
            "candidate_checks": EXPECTED_CASES * len(REQUIRED_CANDIDATES),
            "previous_public_cases": 8_192,
            "previous_public_comparisons": 1_179_648,
            "combined_public_comparisons": (
                1_179_648 + EXPECTED_CASES * len(REQUIRED_CANDIDATES)
            ),
            "mismatches": 0,
            "self_oracle_path": SELF_ORACLE_RELATIVE,
            "self_oracle_sha256": self_oracle_digest,
            "current_provenance": provenance,
            "locales": locales,
            "candidate_reports": outcomes,
            "external_regex_packages": 0,
            "candidate_cross_delegation": False,
            "benchmark_or_timing_executed": False,
            "performance_fixtures_read": 0,
            "holdout_cases_read": 0,
            "performance": "NOT MEASURED",
        }
        evidence_sha256 = _exclusive_evidence(report, ALL_CANDIDATE_RELATIVE)
    return {
        "schema": ALL_CANDIDATE_SCHEMA,
        "status": "PASS",
        "cases_per_candidate": EXPECTED_CASES,
        "candidate_checks": EXPECTED_CASES * len(REQUIRED_CANDIDATES),
        "combined_public_comparisons": (
            1_179_648 + EXPECTED_CASES * len(REQUIRED_CANDIDATES)
        ),
        "mismatches": 0,
        "evidence": ALL_CANDIDATE_RELATIVE,
        "evidence_sha256": evidence_sha256,
        "performance": "NOT MEASURED",
    }


def self_test() -> dict[str, Any]:
    """Exercise inherited and new synthetic controls without real side effects."""

    frozen.candidate_free()
    with stage06.previous._candidate_free_file_and_timing_guard() as effects:
        inherited = stage06.stage06_self_test()
        frozen.require(
            inherited.get("stage") == "stage06"
            and inherited.get("status") == "PASS"
            and inherited.get("check_count", 0) >= 337
            and inherited.get("candidate_imports") == 0
            and inherited.get("candidate_processes") == 0
            and inherited.get("files_read") == 0
            and inherited.get("files_written") == 0
            and inherited.get("holdout_cases_read") == 0
            and inherited.get("performance_fixtures_read") == 0
            and inherited.get("benchmark_or_timing_executed") is False,
            "stage-07 lost the complete candidate-free stage-06 safeguards",
        )
        gc.collect()
        checks = list(inherited["checks"])

        def check(name: str, condition: Any) -> None:
            frozen.require(condition, f"stage-07 synthetic control failed: {name}")
            checks.append({"name": name, "passed": True})

        def reject(name: str, action: Callable[[], Any]) -> None:
            try:
                action()
            except (
                frozen.OracleIntegrityError,
                AssertionError,
                ImportError,
                TypeError,
                ValueError,
                KeyError,
            ):
                check(name, True)
            else:
                check(name, False)

        matrix = build_matrix()
        check("stage07-preserves-eight-disjoint-public-obligation-cohorts", True)
        check(
            "stage07-preserves-all-3584-explicit-public-obligations",
            len(matrix) == EXPECTED_CASES,
        )
        check(
            "stage07-preserves-eight-domain-separated-deterministic-seeds",
            len({cohort_seed(name) for name, _, _ in COHORTS}) == 8,
        )
        check(
            "stage07-never-materializes-hidden-or-random-inputs",
            digest(matrix) == MATRIX_SHA256,
        )
        for name, _, count in COHORTS:
            check(
                "stage07-preserves-exact-cohort-" + name,
                sum(row["cohort"] == name for row in matrix) == count,
            )
            omitted = [row for row in matrix if row["id"] != f"{name}:0000"]
            reject(
                "stage07-rejects-omitted-obligation-" + name,
                lambda rows=omitted: validate_matrix(rows),
            )
        reject(
            "stage07-rejects-duplicated-public-obligation",
            lambda: validate_matrix([matrix[0], *matrix[1:-1], matrix[0]]),
        )
        for field, replacement in (
            ("id", "public-surface:9999"),
            ("cohort", "foreign-cohort"),
            ("operation", "foreign-operation"),
            ("index", -1),
            ("seed", "0" * 64),
        ):
            poisoned = list(matrix)
            poisoned[0] = {**matrix[0], field: replacement}
            reject(
                "stage07-rejects-poisoned-case-" + field,
                lambda rows=poisoned: validate_matrix(rows),
            )
        authorized_outputs = (
            SELF_ORACLE_RELATIVE,
            SELF_ORACLE_FAILURE_RELATIVE,
            ALL_CANDIDATE_RELATIVE,
            *CANDIDATE_FAILURE_RELATIVES.values(),
        )
        check(
            "stage07-preserves-six-distinct-exclusive-success-and-failure-paths",
            len(authorized_outputs) == len(set(authorized_outputs)) == 6,
        )
        for expected in authorized_outputs:
            check(
                "stage07-accepts-only-exact-" + PurePosixPath(expected).name,
                exact_output(expected, expected) == expected,
            )
            for value in (
                "/" + expected,
                "../" + expected,
                expected.replace("/", "//", 1),
                expected + "\x00",
                next(item for item in authorized_outputs if item != expected),
            ):
                reject(
                    "stage07-rejects-foreign-"
                    + PurePosixPath(expected).name
                    + "-"
                    + str(len(checks)),
                    lambda target=value, expected=expected: exact_output(
                        target, expected
                    ),
                )
        fake_re = types.ModuleType("re")
        fake_decoder = types.ModuleType("json.decoder")
        fake_decoder.re = fake_re
        fake_enum = types.ModuleType("enum")
        fake_enum.sys = types.SimpleNamespace(
            modules={"json.decoder": fake_decoder}
        )
        denied = _ForbiddenRegexModule("stage07_synthetic_regex")
        poisoned = _poison_cached_module_aliases(
            {"json.decoder": fake_decoder, "enum": fake_enum},
            (fake_re,),
            denied,
        )
        check(
            "stage07-poisons-cached-enum-json-decoder-regex-alias",
            poisoned == 1
            and fake_decoder.re is denied
            and fake_enum.sys.modules["json.decoder"].re is denied,
        )
        reject(
            "stage07-rejects-poisoned-enum-json-decoder-executor",
            lambda: fake_enum.sys.modules["json.decoder"].re.compile("a"),
        )
        expected_library = "/synthetic/rebar/candidates/_zig_probe.so"
        expected_library_sha = hashlib.sha256(
            b"stage07/synthetic/owned-zig-native"
        ).hexdigest()
        check(
            "stage07-accepts-only-exact-source-bound-owned-zig-library",
            _validate_owned_native_loader(
                family="zig",
                requested=expected_library,
                expected_path=expected_library,
                observed_sha256=expected_library_sha,
                expected_sha256=expected_library_sha,
            )
            == expected_library,
        )
        for alias in NATIVE_LOADER_ALIASES:
            for suffix, changes in (
                ("foreign-family", {"family": "rust"}),
                ("foreign-path", {"requested": "/synthetic/foreign.so"}),
                ("foreign-hash", {"observed_sha256": "0" * 64}),
                ("malformed-hash", {"expected_sha256": "invalid"}),
            ):
                arguments: dict[str, Any] = {
                    "family": "zig",
                    "requested": expected_library,
                    "expected_path": expected_library,
                    "observed_sha256": expected_library_sha,
                    "expected_sha256": expected_library_sha,
                }
                arguments.update(changes)
                reject(
                    "stage07-rejects-native-loader-"
                    + alias.replace(".", "-")
                    + "-"
                    + suffix,
                    lambda arguments=arguments: _validate_owned_native_loader(
                        **arguments
                    ),
                )
        check(
            "stage07-preserves-all-146-real-locale-official-identities",
            official_locale.SELECTED_METHOD_SHA256
            == PINNED_OFFICIAL_METHOD_SHA256,
        )
        check(
            "stage07-preserves-six-named-method-and-two-private-class-waivers",
            len(official_locale.METHOD_WAIVERS) == 6
            and len(official_locale.CLASS_WAIVERS) == 2,
        )
        check(
            "stage07-preserves-all-three-independent-candidate-identities",
            REQUIRED_CANDIDATES == ("rust", "vm", "zig"),
        )
        check(
            "stage07-never-starts-a-candidate-worker",
            inherited["candidate_processes"] == 0
            and effects["workers"] == 0,
        )
        check(
            "stage07-guards-files-clocks-entropy-and-production",
            all(value == 0 for value in effects.values()),
        )
        frozen.candidate_free()
        check("stage07-never-imports-a-production-candidate", True)
        names = [item["name"] for item in checks]
        frozen.require(
            len(names) == len(set(names)) and len(checks) >= 375,
            "stage-07 public controls were duplicated or weakened",
        )
        return {
            "schema": SELF_TEST_SCHEMA,
            "stage": "stage07",
            "status": "PASS",
            "result": "PASS",
            "seed": SEED,
            "seed_domain": SEED_DOMAIN,
            "cohorts": len(COHORTS),
            "cases": EXPECTED_CASES,
            "matrix_sha256": digest(matrix),
            "cohort_cases": {name: count for name, _, count in COHORTS},
            "cohort_seeds": {
                name: cohort_seed(name) for name, _, _ in COHORTS
            },
            "inherited_stage06_control_count": inherited["check_count"],
            "checks": checks,
            "check_count": len(checks),
            "failed": [],
            "candidate_imports": 0,
            "candidate_processes": 0,
            "files_read": 0,
            "files_written": 0,
            "clock_samples": 0,
            "entropy_drawn": False,
            "benchmark_or_timing_executed": False,
            "performance_fixtures_read": 0,
            "holdout_cases_read": 0,
            "performance": "NOT MEASURED",
            "self_oracle_executed": False,
            "production_evidence_written": False,
            "self_oracle_output": SELF_ORACLE_RELATIVE,
            "all_candidate_output": ALL_CANDIDATE_RELATIVE,
            "self_oracle_failure_output": SELF_ORACLE_FAILURE_RELATIVE,
            "candidate_failure_outputs": dict(CANDIDATE_FAILURE_RELATIVES),
            "native_loader_aliases_blocked": list(NATIVE_LOADER_ALIASES),
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--self-oracle", action="store_true")
    modes.add_argument("--candidate", choices=("all",))
    args = parser.parse_args(argv)
    try:
        if args.self_test:
            report = self_test()
        elif args.self_oracle:
            report = run_self_oracle()
        else:
            frozen.require(args.candidate == "all", "all three candidates are mandatory")
            report = run_all_candidates()
        print(json.dumps(report, sort_keys=True, separators=(",", ":")))
        return 0
    except (
        frozen.OracleIntegrityError,
        AssertionError,
        OSError,
        ValueError,
        subprocess.SubprocessError,
    ) as error:
        print(
            json.dumps(
                {"schema": SCHEMA, "status": "FAIL", "error": str(error)},
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
