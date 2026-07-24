#!/usr/bin/env python3
"""Freeze and independently check Python's observable public regex contract.

``--self-test`` is exclusively an in-memory, source-only control.  It never
matches a regular expression, opens a source or evidence file, starts a worker,
imports a candidate, samples a clock, changes a locale, or writes a report.

Real reference and candidate execution are deliberately separate.  A reference
can depend only on this frozen source/protocol and the actual, independently
published version-five two-reference Python report.  Version-ten native audits
and qualified proofs are relevant exclusively to candidate execution.
"""

from __future__ import annotations

import argparse
import ast
import builtins
import contextlib
import copy
import enum
import gc
import hashlib
import importlib
import io
import json
import locale
import os
from pathlib import Path, PurePosixPath
import pickle
import stat
import subprocess
import sys
import threading
import time
import types
import typing
import unicodedata
import warnings
import weakref
from array import array
from collections.abc import Mapping
from typing import Any, Callable, Iterator


ROOT = Path(os.path.abspath(__file__)).parent.parent
PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
SCHEMA = "rebar-python-re-independent-public-surface-v17"
SOURCE_RELATIVE = "tools/python_re_public_surface_oracle_stage17.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-SURFACE-V17.md"

V5_SOURCE_RELATIVE = "tools/postfinal_cpython_locale_oracle_v5.py"
V5_SOURCE_SHA256 = (
    "9a4f2ac53617fb91e498ae2935bde622417921415af255e390668f69ba908730"
)
V5_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-LOCALE-V5.md"
V5_PROTOCOL_SHA256 = (
    "1329cf9c8e36391af134b2fb2b212e71067ace736b282dacd2a6c90233384840"
)
V5_REFERENCE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v5-self-oracle.json"
)
V5_REFERENCE_SHA256 = (
    "3a5c300640b4d5207694d474eb231ce6ff7cb11ce6f3a17da0edd2e48fea3916"
)
ORIGINAL_SOURCE_RELATIVE = "oracle/cpython-3.14.6/test_re.py"
ORIGINAL_SOURCE_SHA256 = (
    "879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2"
)
ORIGINAL_CORPUS_SHA256 = (
    "ec04a2b2a77338d20b37d931693c7e588a2896d3c73c7b4b47973e24c13b5aab"
)
ORIGINAL_MATRIX_SHA256 = (
    "5802606619ee4aad65a1d031259740b003c891de8674a5321d0bf6dbce2b590a"
)
ORIGINAL_SUPPORT_TREE_SHA256 = (
    "6cd13337b46bd6a53a32ac0c557da79b0ddd536ac82be885cc57be77e80f1632"
)
ORIGINAL_ARCHIVE_SHA256 = (
    "143b1dddefaec3bd2e21e3b839b34a2b7fb9842272883c576420d605e9f30c63"
)
PUBLIC_CLASSES = ("ReTests", "PatternReprTests", "ExternalTests")
PRIVATE_CLASS_COUNTS = {"DebugTests": 4, "ImplementationTest": 9}
FORMERLY_EXCLUDED_PUBLIC_METHODS = frozenset({
    "ReTests.test_re_groupref_overflow",
    "ReTests.test_large_search",
    "ReTests.test_large_subn",
    "ReTests.test_search_anchor_at_beginning",
    "ReTests.test_regression_gh94675",
    "ReTests.test_memory_leaks",
})
PRIVATE_CONDITIONAL_METHOD = "ReTests.test_memory_leaks"
PUBLIC_EXPORTS = (
    "match", "fullmatch", "search", "sub", "subn", "split",
    "findall", "finditer", "compile", "purge", "escape", "error",
    "Pattern", "Match", "A", "I", "L", "M", "S", "X", "U", "ASCII",
    "IGNORECASE", "LOCALE", "MULTILINE", "DOTALL", "VERBOSE",
    "UNICODE", "NOFLAG", "RegexFlag", "PatternError",
)
PUBLIC_PATTERN_MEMBERS = (
    "findall", "finditer", "flags", "fullmatch", "groupindex", "groups",
    "match", "pattern", "scanner", "search", "split", "sub", "subn",
)
PUBLIC_MATCH_MEMBERS = (
    "end", "endpos", "expand", "group", "groupdict", "groups",
    "lastgroup", "lastindex", "pos", "re", "regs", "span", "start",
    "string",
)
PUBLIC_ALIASES = (
    ("A", "ASCII"), ("I", "IGNORECASE"), ("L", "LOCALE"),
    ("M", "MULTILINE"), ("S", "DOTALL"), ("X", "VERBOSE"),
    ("U", "UNICODE"), ("error", "PatternError"),
)

# All 640 base cases are independently regenerated from this source alone.
# No previous stage is imported, opened, qualified, or used as a prerequisite.
BASE_SEED = 2026072483
BASE_DOMAIN = "rebar/python-re/complete-public-surface/v16"
BASE_MATRIX_SHA256 = (
    "748ef9556f3202678d42ff47a4d55ce2cf965ed16026b5b62ed1c1d75937aeb7"
)
BASE_STIMULUS_SHA256 = (
    "82856f5f3782ddd80caab6b420749565c1c225405bccad5850400bc00d327cbe"
)
CASES_PER_COHORT = 32
BASE_COHORTS = (
    "complete-public-exports",
    "module-aliases-and-version",
    "regexflag-intflag-and-noflag",
    "public-purge-and-cache-identity",
    "pattern-properties",
    "pattern-pos-and-endpos-windows",
    "match-properties-and-groups",
    "scanner-string-and-callback",
    "scanner-bytes-and-remainder",
    "contiguous-buffer-inputs",
    "noncontiguous-and-released-buffers",
    "replacement-numeric-and-named",
    "replacement-octal-and-errors",
    "replacement-callables",
    "pattern-error-coordinates",
    "unicode-astral-and-surrogates",
    "unicode-casefold-and-flags",
    "generic-types-and-standard-pickle",
    "reentrant-replacement-callbacks",
    "synchronized-compile-match-and-purge",
)
ADDITIONAL_SEED = 2026072497
ADDITIONAL_DOMAIN = "rebar/python-re/independent-public-surface/v17"
ADDITIONAL_COHORTS = (
    "unknown-flags-actually-compiled",
    "mixed-inverted-and-indexed-flags",
    "compiled-pattern-every-pickle-protocol",
    "pattern-cache-equality-hash-and-weakref",
    "match-copy-and-weakref-behavior",
    "live-finditer-buffer-resize-and-release",
    "live-scanner-and-match-buffer-lifetime",
    "typed-empty-strided-and-released-buffers",
    "valid-unicode-character-names",
    "unicode-and-astral-named-captures",
    "extended-unicode-folding-and-boundaries",
    "real-locale-switch-on-compiled-bytes",
    "real-locale-invalid-flags-and-cache",
    "replacement-callback-failure-side-effects",
    "scanner-callback-failure-side-effects",
    "public-deprecation-warning-caller-location",
    "ambiguous-character-set-future-warnings",
    "pattern-group-mapping-and-error-identity",
    "match-regs-identity-and-group-errors",
    "public-generic-pickle-every-protocol",
    "public-typing-origin-args-and-rejections",
    "public-error-fields-cause-and-pickling",
    "separate-interpreter-guard-capability",
)
COHORTS = BASE_COHORTS + ADDITIONAL_COHORTS
EXPECTED_BASE_CASES = len(BASE_COHORTS) * CASES_PER_COHORT
EXPECTED_ADDITIONAL_CASES = len(ADDITIONAL_COHORTS) * CASES_PER_COHORT
EXPECTED_CASES = len(COHORTS) * CASES_PER_COHORT

# Independently derived by the direct, file-free, candidate-free pinned source
# control. Neither digest represents a matching run or a candidate result.
MATRIX_SHA256: str | None = (
    "7885a9ac0b2e22db88db7dc4ab9c33c4ba229ddb6d15fcdd4bfe9b0d6f10e8aa"
)
STIMULUS_SHA256: str | None = (
    "8c1a4fd434af5fb1ea0dcd1aa3faaa06b07e7d186ca52c1593575eff93b4d7da"
)

FAMILIES = ("rust", "vm", "zig")
V10_BASE_SOURCE_RELATIVE = "tools/postfinal_from_scratch_audit_v10.py"
V10_STRICT_SOURCE_RELATIVE = "tools/postfinal_no_delegation_audit_v10.py"
V10_OWNERSHIP_PROTOCOL_RELATIVE = (
    "candidates/audits/POSTFINAL-NATIVE-OWNERSHIP-V10.md"
)
V10_PROOF_SOURCE_RELATIVE = "tools/postfinal_current_build_proofs_v10.py"
V10_PROOF_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V10.md"
)
V10_BASE_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V10.json"
)
V10_STRICT_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V10.json"
)
V10_EDGE_RELATIVES = {
    family: (
        "candidates/evidence/rust-v7-edge-oracle-" + family
        + "-postfinal-current-build-v10-qualified-pass.json.gz"
    )
    for family in FAMILIES
}
V10_DEEP_RELATIVES = {
    family: (
        "candidates/audits/RUST-V8-DEEP-CONTRACT-"
        + {"rust": "RUST", "vm": "C", "zig": "ZIG"}[family]
        + "-POSTFINAL-CURRENT-BUILD-V10-PASS.json.gz"
    )
    for family in FAMILIES
}
# Supplied independently by the owners after their real source-only reviews.
# None of these sources or protocols is read in reference or self-test mode.
V10_BASE_SOURCE_SHA256 = (
    "0c4d3f07bb51b0ce5ddc148810cb157d21067ddb07b578d3a793aaac5c671505"
)
V10_STRICT_SOURCE_SHA256 = (
    "885168bd6df92ac9cabc8fc78a8389ee487f0be8d3c7fe67a393e984011b8d95"
)
V10_OWNERSHIP_PROTOCOL_SHA256 = (
    "902bc095d08331089dcc1d1d11233747438a0cacb0cf1057ae41a2474bde2fa6"
)
V10_PROOF_SOURCE_SHA256 = (
    "74209ed4e59351802c7dae3af3d21a03a23c0e464e340c3bf29eeddf8337d5b9"
)
V10_PROOF_PROTOCOL_SHA256 = (
    "2eb5b5c0828059b1d02d306e9cf6f05e90d30575e3a386c20f83582456de1ae0"
)

SELF_ORACLE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-surface-v17-self-oracle.json"
)
SELF_ORACLE_FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-surface-v17-self-oracle-failures.json"
)
ALL_CANDIDATE_RELATIVE = (
    "candidates/evidence/python-re-public-surface-v17-all.json"
)
CANDIDATE_FAILURE_RELATIVES = {
    family: (
        "candidates/evidence/python-re-public-surface-v17-"
        + family + "-failures.json"
    )
    for family in FAMILIES
}
APPROVED_OUTPUTS = frozenset({
    SELF_ORACLE_RELATIVE,
    SELF_ORACLE_FAILURE_RELATIVE,
    ALL_CANDIDATE_RELATIVE,
    *CANDIDATE_FAILURE_RELATIVES.values(),
})
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_EVIDENCE_BYTES = 64 * 1024 * 1024
MAX_COMPRESSED_PROOF_BYTES = 128 * 1024 * 1024
MAX_WORKER_BYTES = 48 * 1024 * 1024


class PublicSurfaceError(AssertionError):
    """The frozen public contract cannot be truthfully established."""


class PublicSurfaceWorkerFailure(PublicSurfaceError):
    """Retain the actual partial report of a failed isolated worker."""

    def __init__(self, role: str, message: str, details: Mapping[str, Any]):
        super().__init__(message)
        self.role = role
        self.details = dict(details)


def require(condition: Any, message: str) -> None:
    if not condition:
        raise PublicSurfaceError(message)


def valid_sha256(value: Any) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
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


def verify_runtime() -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and os.path.abspath(sys.executable) == str(PINNED_PYTHON)
        and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE),
        "use the exact direct, isolated, bytecode-free pinned CPython 3.14.6",
    )


def _variant(domain: str, seed: int, cohort: str, index: int) -> int:
    material = f"{domain}:{seed}:{cohort}:{index}".encode("ascii")
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big")


def build_base_matrix() -> list[dict[str, Any]]:
    return [
        {
            "id": f"surface16.{number:02d}.{index:02d}",
            "cohort": cohort,
            "index": index,
            "variant": _variant(BASE_DOMAIN, BASE_SEED, cohort, index),
        }
        for number, cohort in enumerate(BASE_COHORTS)
        for index in range(CASES_PER_COHORT)
    ]


def build_matrix() -> list[dict[str, Any]]:
    return build_base_matrix() + [
        {
            "id": f"surface17.{number:02d}.{index:02d}",
            "cohort": cohort,
            "index": index,
            "variant": _variant(
                ADDITIONAL_DOMAIN, ADDITIONAL_SEED, cohort, index,
            ),
        }
        for number, cohort in enumerate(ADDITIONAL_COHORTS)
        for index in range(CASES_PER_COHORT)
    ]


def validate_matrix(
    matrix: Any, *, expected_sha256: str | None = None,
) -> str:
    require(
        isinstance(matrix, list)
        and len(matrix) == EXPECTED_CASES
        and len(PUBLIC_EXPORTS) == 31
        and len(PUBLIC_PATTERN_MEMBERS) == 13
        and len(PUBLIC_MATCH_MEMBERS) == 14
        and len(COHORTS) == len(set(COHORTS))
        and len(BASE_COHORTS) == 20,
        "the exact independent public obligation denominator changed",
    )
    seen: set[str] = set()
    for offset, row in enumerate(matrix):
        is_base = offset < EXPECTED_BASE_CASES
        position = offset if is_base else offset - EXPECTED_BASE_CASES
        cohort_number, index = divmod(position, CASES_PER_COHORT)
        cohorts = BASE_COHORTS if is_base else ADDITIONAL_COHORTS
        prefix = "surface16" if is_base else "surface17"
        domain = BASE_DOMAIN if is_base else ADDITIONAL_DOMAIN
        seed = BASE_SEED if is_base else ADDITIONAL_SEED
        cohort = cohorts[cohort_number]
        require(
            isinstance(row, dict)
            and set(row) == {"id", "cohort", "index", "variant"}
            and row.get("id") == f"{prefix}.{cohort_number:02d}.{index:02d}"
            and row.get("cohort") == cohort
            and type(row.get("index")) is int
            and row["index"] == index
            and type(row.get("variant")) is int
            and row["variant"] == _variant(domain, seed, cohort, index)
            and row["id"] not in seen,
            "a seeded public obligation was omitted, reordered, or forged",
        )
        seen.add(row["id"])
    require(
        digest(matrix[:EXPECTED_BASE_CASES]) == BASE_MATRIX_SHA256,
        "the standalone source-local 640-case generator is not reproducible",
    )
    observed = digest(matrix)
    if expected_sha256 is not None:
        require(
            valid_sha256(expected_sha256) and observed == expected_sha256,
            "the independently frozen V17 matrix changed",
        )
    return observed


def build_stimulus(row: Mapping[str, Any]) -> dict[str, Any]:
    cohort = row.get("cohort")
    index = row.get("index")
    variant = row.get("variant")
    require(
        cohort in COHORTS
        and type(index) is int
        and 0 <= index < CASES_PER_COHORT
        and type(variant) is int
        and 0 <= variant < 1 << 64,
        "a public case has no real reproducibly seeded matching stimulus",
    )
    token = f"{variant:016x}"
    word = "a" + token
    digits = str(100_000 + variant % 900_000)
    first_group = "w" + token[:8]
    second_group = "n" + token[8:]
    expression = (
        "(?P<" + first_group + ">" + word + ")-"
        + "(?P<" + second_group + ">\\d+)"
    )
    subject = "pre-" + word + "-" + digits + "-post"
    result: dict[str, Any] = {
        "cohort": cohort,
        "expression": expression,
        "subject": subject,
        "match_subject": word + "-" + digits,
    }
    if cohort == "complete-public-exports":
        result.update(
            symbol=(PUBLIC_EXPORTS + ("Scanner",))[index],
            public_argument=word + ".[]",
        )
    elif cohort == "module-aliases-and-version":
        result.update(
            alias=list(PUBLIC_ALIASES[index % len(PUBLIC_ALIASES)]),
            safe_flag_selector=(variant >> 9) & 7,
            check_debug=index % 4 == 3,
            verbose_expression=expression + "  # " + word + "\n",
            escaped_literal=word + ".[seeded]",
        )
    elif cohort == "regexflag-intflag-and-noflag":
        result.update(
            flag_value=((variant & 0xFFFF) << 12) | (index << 5),
            safe_flag_selector=(variant >> 4) & 7,
        )
    elif cohort == "public-purge-and-cache-identity":
        result.update(cache_pressure=(0, 1, 31, 255, 512, 600)[variant % 6])
    elif cohort == "pattern-properties":
        result.update(
            member=PUBLIC_PATTERN_MEMBERS[index % len(PUBLIC_PATTERN_MEMBERS)],
            use_bytes=bool(variant & 1),
            group_names=[first_group, second_group],
        )
    elif cohort == "pattern-pos-and-endpos-windows":
        lefts = (-99, -1, 0, 1, 4, len(subject), len(subject) + 7)
        rights = (-2, 0, 4, len(subject) // 2, len(subject), len(subject) + 9)
        result.update(
            pos=lefts[(variant >> 3) % len(lefts)],
            endpos=rights[(variant >> 11) % len(rights)],
            use_keywords=bool(variant & 1),
        )
    elif cohort == "match-properties-and-groups":
        result.update(
            member=PUBLIC_MATCH_MEMBERS[index % len(PUBLIC_MATCH_MEMBERS)],
            group_names=[first_group, second_group],
            invalid_group=("missing_" + token if index % 2 else 99_999 + index),
            use_index_key=bool((variant >> 7) & 1),
        )
    elif cohort in {"scanner-string-and-callback", "scanner-bytes-and-remainder"}:
        result.update(
            scan_subject=word + "-" + digits + "-end!",
            use_bytes=cohort == "scanner-bytes-and-remainder",
            zero_width=index % 7 == 6,
            raises=index % 11 == 10,
            low_level_operation="match" if variant & 1 else "search",
        )
    elif cohort == "contiguous-buffer-inputs":
        result.update(
            raw_subject="--" + word + "-" + digits + "--",
            buffer_kind=("bytes", "bytearray", "memoryview")[index % 3],
        )
    elif cohort == "noncontiguous-and-released-buffers":
        result.update(
            raw_subject="--" + word + "-" + digits + "--",
            buffer_kind="released" if variant & 1 else "noncontiguous",
        )
    elif cohort == "replacement-numeric-and-named":
        result.update(
            replacement=(
                "\\g<" + second_group + ">-\\g<" + first_group + ">",
                "\\2-\\1",
                "\\g<0>",
            )[index % 3],
            count=(variant >> 5) % 4,
            record_warning=index % 4 == 3,
        )
    elif cohort == "replacement-octal-and-errors":
        result.update(
            replacement=(
                r"\101", "\\g<missing_" + token + ">", r"\9",
                "\\", "\\g<" + first_group + ">",
            )[index % 5],
        )
    elif cohort in {"replacement-callables", "reentrant-replacement-callbacks"}:
        result.update(
            callback_subject=word + " " + digits + " " + word + "z",
            callback_expression="[a-f0-9]+",
            count=(variant >> 3) % 4,
            raises=cohort == "replacement-callables" and index % 7 == 6,
        )
    elif cohort == "pattern-error-coordinates":
        invalid = (
            "(" + word,
            "[z-a]" + word,
            "(?P<" + first_group + ">a)(?P<" + first_group + ">b)",
            "\\x" + token[0],
            word + "\n(",
            "(?P<1" + token[:4] + ">x)",
            "(?<=" + word + "+)b",
            "\\N{NO SUCH NAME " + token + "}",
        )
        result.update(invalid_pattern=invalid[index % len(invalid)])
    elif cohort == "unicode-astral-and-surrogates":
        choices = (
            "\U0001f600", "\ud800", "\udfff", "\u00df", "\u0130",
            chr(0x10000 + variant % (0x10FFFF - 0x10000)),
        )
        result.update(unicode_subject=choices[index % len(choices)] + word)
    elif cohort == "unicode-casefold-and-flags":
        pairs = (
            ("k", "\u212a"), ("i", "\u0130"),
            ("\u017f", "S"), ("\u03c3", "\u03c2"),
        )
        pattern, value = pairs[index % len(pairs)]
        result.update(casefold_pattern=pattern + word, casefold_subject=value + word)
    elif cohort == "generic-types-and-standard-pickle":
        result.update(
            origin=("Pattern", "Match")[index % 2],
            argument=("str", "bytes")[(index // 2) % 2],
            pickle_protocol=(0, 2, 4, pickle.HIGHEST_PROTOCOL)[(index // 4) % 4],
            copy_pattern=word,
        )
    elif cohort == "synchronized-compile-match-and-purge":
        result.update(thread_count=2 if variant & 1 == 0 else 4)
    elif cohort in ADDITIONAL_COHORTS:
        result.update(
            token=token,
            group_names=[first_group, second_group],
            high_flag=0x100000 | ((variant & 0xFF) << 12),
            selected_protocol=index % (pickle.HIGHEST_PROTOCOL + 1),
            callback_fail_after=1 + index % 3,
            use_bytes=bool(variant & 1),
            unicode_name=(
                "LATIN SMALL LETTER SHARP S",
                "GREEK SMALL LETTER FINAL SIGMA",
                "KELVIN SIGN",
                "SNAKE",
                "DESERET CAPITAL LETTER LONG I",
            )[index % 5],
            unicode_group=("µ", "π", "𝔘", "名")[index % 4] + token[:6],
            future_pattern=(
                "[[" + word + "]",
                "[a&&" + word + "]",
                "[a~~" + word + "]",
                "[a||" + word + "]",
                "[a--" + word + "]",
            )[index % 5],
            typed_buffer_kind=(
                "bytearray", "memoryview", "unsigned-short", "strided",
                "released", "empty",
            )[index % 6],
            warning_operation=("sub", "subn", "split")[index % 3],
        )
    else:
        raise PublicSurfaceError("a real source-frozen public cohort is missing")
    return result


def validate_stimuli(
    matrix: list[dict[str, Any]],
    *,
    expected_sha256: str | None = None,
    observed: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    validate_matrix(matrix, expected_sha256=MATRIX_SHA256)
    generated = [build_stimulus(row) for row in matrix]
    probes = generated if observed is None else observed
    require(
        isinstance(probes, list)
        and len(probes) == EXPECTED_CASES
        and all(
            isinstance(actual, dict) and actual == expected
            for actual, expected in zip(probes, generated, strict=True)
        ),
        "an actual public matching stimulus was deleted or substituted",
    )
    identities = [digest(probe) for probe in probes]
    require(
        len(set(identities)) == EXPECTED_CASES,
        "two public cases claim the same actual behavioral stimulus",
    )
    require(
        digest(probes[:EXPECTED_BASE_CASES]) == BASE_STIMULUS_SHA256,
        "the independently reconstructed 640 real base inputs changed",
    )
    counts = {
        cohort: sum(row["cohort"] == cohort for row in matrix)
        for cohort in COHORTS
    }
    require(
        all(count == CASES_PER_COHORT for count in counts.values()),
        "a public cohort does not contain 32 actual distinct stimuli",
    )
    actual_digest = digest(probes)
    if expected_sha256 is not None:
        require(
            valid_sha256(expected_sha256) and actual_digest == expected_sha256,
            "the source-frozen V17 behavioral inputs changed",
        )
    return {
        "cases": EXPECTED_CASES,
        "base_cases": EXPECTED_BASE_CASES,
        "additional_cases": EXPECTED_ADDITIONAL_CASES,
        "cohorts": len(COHORTS),
        "cohort_cases": counts,
        "distinct_stimuli": len(set(identities)),
        "base_matrix_sha256": BASE_MATRIX_SHA256,
        "base_stimulus_sha256": BASE_STIMULUS_SHA256,
        "stimulus_sha256": actual_digest,
    }


def normalize(value: Any, *, depth: int = 0) -> Any:
    require(depth < 24, "a public observation contains a recursive object")
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is float:
        return {"kind": "float", "hex": value.hex()}
    if isinstance(value, (bytes, bytearray)):
        return {"kind": type(value).__name__, "hex": bytes(value).hex()}
    if isinstance(value, BaseException):
        return {
            "kind": "exception",
            "type": type(value).__name__,
            "message": str(value),
            "args": normalize(value.args, depth=depth + 1),
            "pattern": normalize(getattr(value, "pattern", None), depth=depth + 1),
            "msg": normalize(getattr(value, "msg", None), depth=depth + 1),
            "pos": normalize(getattr(value, "pos", None), depth=depth + 1),
            "lineno": normalize(getattr(value, "lineno", None), depth=depth + 1),
            "colno": normalize(getattr(value, "colno", None), depth=depth + 1),
            "cause": (
                None if value.__cause__ is None
                else normalize(value.__cause__, depth=depth + 1)
            ),
        }
    if isinstance(value, enum.IntFlag):
        return {
            "kind": "intflag",
            "type": type(value).__name__,
            "value": int(value),
            "name": value.name,
            "repr": repr(value),
        }
    if isinstance(value, Mapping):
        items = [
            [normalize(key, depth=depth + 1), normalize(item, depth=depth + 1)]
            for key, item in value.items()
        ]
        items.sort(key=lambda item: canonical(item[0]))
        return {"kind": "mapping", "items": items}
    if isinstance(value, (tuple, list)):
        return {
            "kind": type(value).__name__,
            "items": [normalize(item, depth=depth + 1) for item in value],
        }
    if isinstance(value, (set, frozenset)):
        entries = [normalize(item, depth=depth + 1) for item in value]
        entries.sort(key=canonical)
        return {"kind": type(value).__name__, "items": entries}
    if isinstance(value, types.GenericAlias):
        return {
            "kind": "generic-alias",
            "origin": getattr(value.__origin__, "__name__", None),
            "args": [getattr(item, "__name__", repr(item)) for item in value.__args__],
            "parameters": [repr(item) for item in value.__parameters__],
        }
    if isinstance(value, type):
        return {"kind": "type", "name": value.__name__}
    if isinstance(value, memoryview):
        return {
            "kind": "memoryview",
            "format": value.format,
            "shape": normalize(value.shape, depth=depth + 1),
            "hex": value.tobytes().hex(),
        }
    return {"kind": "public-object", "type": type(value).__name__}


def match_value(value: Any) -> Any:
    if value is None:
        return None
    return {
        "group": normalize(value.group(0)),
        "groups": normalize(value.groups()),
        "groupdict": normalize(value.groupdict()),
        "span": normalize(value.span()),
        "pos": value.pos,
        "endpos": value.endpos,
        "lastindex": value.lastindex,
        "lastgroup": value.lastgroup,
    }


def observe(action: Callable[[], Any]) -> dict[str, Any]:
    try:
        return {"status": "return", "value": normalize(action())}
    except (
        PublicSurfaceError, locale.Error, MemoryError, KeyboardInterrupt, SystemExit,
    ):
        raise
    except Exception as error:
        return {"status": "raise", "exception": normalize(error)}


def safe_flags(module: Any, selector: int) -> Any:
    options = (
        module.NOFLAG, module.I, module.M, module.S, module.I | module.M,
        module.A, module.I | module.S, module.M | module.S,
    )
    return options[selector % len(options)]


def _warning_records(records: list[Any]) -> list[dict[str, Any]]:
    observed: list[dict[str, Any]] = []
    for item in records:
        filename = os.path.abspath(item.filename)
        own_source = filename == str(ROOT / SOURCE_RELATIVE)
        observed.append({
            "category": item.category.__name__,
            "message": str(item.message),
            "filename": SOURCE_RELATIVE if own_source else filename,
            "lineno": item.lineno,
            "points_to_public_caller": own_source,
        })
    return observed


def _public_debug(module: Any, expression: str, subject: str) -> dict[str, Any]:
    patterns: list[Any] = []
    emitted: list[bool] = []
    for _ in range(2):
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            patterns.append(module.compile(expression, module.DEBUG))
        emitted.append(bool(captured.getvalue()))
    return {
        "debug_is_public": hasattr(module, "DEBUG"),
        "debug_is_exported": "DEBUG" in module.__all__,
        "emitted_on_each_compile": emitted,
        "flag_retained": [bool(pattern.flags & module.DEBUG) for pattern in patterns],
        "match": [match_value(pattern.search(subject)) for pattern in patterns],
        "same_cached_object": patterns[0] is patterns[1],
    }


def _export_probe(module: Any, stimulus: Mapping[str, Any]) -> dict[str, Any]:
    symbol = stimulus["symbol"]
    public = getattr(module, symbol)
    expression = stimulus["expression"]
    subject = stimulus["subject"]
    matched = stimulus["match_subject"]
    if symbol in {"match", "fullmatch"}:
        value = match_value(public(expression, matched))
    elif symbol == "search":
        value = match_value(public(expression, subject))
    elif symbol in {"sub", "subn"}:
        value = public(expression, "replaced", subject)
    elif symbol in {"split", "findall"}:
        value = public(expression, subject)
    elif symbol == "finditer":
        value = [match_value(item) for item in public(expression, subject)]
    elif symbol == "compile":
        value = match_value(public(expression).search(subject))
    elif symbol == "purge":
        before = module.compile(expression)
        public()
        after = module.compile(expression)
        value = {
            "cleared": before is not after,
            "match": match_value(after.search(subject)),
        }
    elif symbol == "escape":
        value = public(stimulus["public_argument"])
    elif symbol in {"error", "PatternError"}:
        value = {
            "alias": module.error is module.PatternError,
            "name": public.__name__,
            "actual_error": observe(lambda: module.compile("(" + matched)),
        }
    elif symbol == "Pattern":
        value = {
            "name": public.__name__,
            "actual_instance": isinstance(module.compile(expression), public),
            "match": match_value(module.search(expression, subject)),
        }
    elif symbol == "Match":
        actual = module.search(expression, subject)
        value = {
            "name": public.__name__,
            "actual_instance": isinstance(actual, public),
            "match": match_value(actual),
        }
    elif symbol == "RegexFlag":
        flag = public(module.I | module.M)
        value = {
            "name": public.__name__,
            "value": int(flag),
            "intflag": isinstance(flag, enum.IntFlag),
            "match": match_value(module.search(expression, subject, flag)),
        }
    elif symbol == "Scanner":
        scanner = public([
            (module.escape(matched), lambda _scanner, token: token),
        ])
        tokens, remainder = scanner.scan(matched)
        value = {"name": public.__name__, "tokens": tokens, "remainder": remainder}
    else:
        if symbol in {"L", "LOCALE"}:
            actual = observe(lambda: match_value(module.search(
                expression.encode("ascii"), subject.encode("ascii"), public,
            )))
        else:
            actual = observe(lambda: match_value(module.search(
                expression, subject, public,
            )))
        value = {"flag": int(public), "actual_operation": actual}
    return {"symbol": symbol, "observation": normalize(value)}


def _scanner_probe(module: Any, stimulus: Mapping[str, Any]) -> dict[str, Any]:
    traces: list[Any] = []
    bytes_mode = stimulus["use_bytes"]
    subject: Any = stimulus["scan_subject"]
    if bytes_mode:
        subject = subject.encode("ascii")

    def action(_scanner: Any, token: Any) -> Any:
        if stimulus["raises"]:
            raise ValueError("public scanner callback failure")
        traces.append(normalize(token))
        return token

    literal = module.escape(stimulus["match_subject"].split("-")[0])
    lexicon: list[tuple[Any, Any]]
    if bytes_mode:
        lexicon = [
            (literal.encode("ascii"), action), (br"\d+", action), (br"-", None),
        ]
    else:
        lexicon = [(literal, action), (r"\d+", action), (r"-", None)]
    if stimulus["zero_width"]:
        lexicon.insert(0, (b"" if bytes_mode else "", action))
    scanner = module.Scanner(lexicon)
    tokens, remainder = scanner.scan(subject)
    expression: Any = stimulus["expression"]
    full_subject: Any = stimulus["subject"]
    if bytes_mode:
        expression = expression.encode("ascii")
        full_subject = full_subject.encode("ascii")
    low = module.compile(expression).scanner(full_subject)
    operation = stimulus["low_level_operation"]
    return {
        "tokens": normalize(tokens),
        "remainder": normalize(remainder),
        "callbacks": traces,
        "low_level_members": [
            name for name in ("match", "pattern", "search") if hasattr(low, name)
        ],
        "operation": operation,
        "first": match_value(getattr(low, operation)()),
        "next": match_value(low.search()),
    }


def _threaded_probe(module: Any, stimulus: Mapping[str, Any]) -> dict[str, Any]:
    count = stimulus["thread_count"]
    barrier = threading.Barrier(count + 1)
    observations: list[Any] = [None] * count
    failures: list[Any] = []

    def run(position: int) -> None:
        try:
            barrier.wait(timeout=10)
            first = module.compile(stimulus["expression"]).fullmatch(
                stimulus["match_subject"],
            )
            barrier.wait(timeout=10)
            second = module.search(r"\d+", stimulus["subject"])
            observations[position] = [match_value(first), match_value(second)]
        except BaseException as error:
            failures.append(normalize(error))
            barrier.abort()

    threads = [threading.Thread(target=run, args=(index,)) for index in range(count)]
    for thread in threads:
        thread.start()
    barrier.wait(timeout=10)
    barrier.wait(timeout=10)
    for thread in threads:
        thread.join(timeout=10)
    require(not failures and not any(thread.is_alive() for thread in threads),
            "a real concurrent public correctness operation did not terminate")
    module.purge()
    return {
        "threads": count,
        "observations": observations,
        "after_purge": match_value(module.compile(
            stimulus["expression"],
        ).fullmatch(stimulus["match_subject"])),
    }


def _pattern_probe(module: Any, stimulus: Mapping[str, Any]) -> dict[str, Any]:
    expression: Any = stimulus["expression"]
    subject: Any = stimulus["subject"]
    matched: Any = stimulus["match_subject"]
    replacement: Any = "replaced"
    if stimulus["use_bytes"]:
        expression = expression.encode("ascii")
        subject = subject.encode("ascii")
        matched = matched.encode("ascii")
        replacement = replacement.encode("ascii")
    pattern = module.compile(expression, module.I)
    member = stimulus["member"]
    if member == "findall":
        value = pattern.findall(subject)
    elif member == "finditer":
        value = [match_value(item) for item in pattern.finditer(subject)]
    elif member in {"flags", "groups", "pattern"}:
        value = getattr(pattern, member)
    elif member == "fullmatch":
        value = match_value(pattern.fullmatch(matched))
    elif member == "groupindex":
        value = dict(pattern.groupindex)
    elif member == "match":
        value = match_value(pattern.match(matched))
    elif member == "scanner":
        scanner = pattern.scanner(subject)
        value = {
            "members": [name for name in ("match", "pattern", "search")
                        if hasattr(scanner, name)],
            "first": match_value(scanner.search()),
            "next": match_value(scanner.search()),
        }
    elif member == "search":
        value = match_value(pattern.search(subject))
    elif member == "split":
        value = pattern.split(subject)
    elif member in {"sub", "subn"}:
        value = getattr(pattern, member)(replacement, subject)
    else:
        raise PublicSurfaceError("an original public Pattern member was omitted")
    return {
        "public_members": [name for name in dir(pattern) if not name.startswith("_")],
        "member": member,
        "observation": normalize(value),
        "pattern_type": isinstance(pattern, module.Pattern),
        "group_names": normalize(dict(pattern.groupindex)),
        "match": match_value(pattern.search(subject)),
    }


def _match_probe(module: Any, stimulus: Mapping[str, Any]) -> dict[str, Any]:
    value = module.search(stimulus["expression"], stimulus["subject"])
    require(value is not None, "the actual seeded public Match is absent")
    first_group, second_group = stimulus["group_names"]
    member = stimulus["member"]
    if member in {"end", "span", "start"}:
        observed = getattr(value, member)(second_group if member == "end" else first_group)
    elif member in {"endpos", "lastgroup", "lastindex", "pos", "string"}:
        observed = getattr(value, member)
    elif member == "expand":
        observed = value.expand("\\g<" + second_group + ">-\\g<" + first_group + ">")
    elif member == "group":
        observed = value.group(first_group, second_group)
    elif member == "groupdict":
        observed = value.groupdict(default=stimulus["match_subject"])
    elif member == "groups":
        observed = value.groups(default=stimulus["match_subject"])
    elif member == "re":
        observed = {"pattern": value.re.pattern, "flags": int(value.re.flags)}
    elif member == "regs":
        observed = value.regs
    else:
        raise PublicSurfaceError("an original public Match member was omitted")

    class IndexKey:
        def __index__(self) -> int:
            return 1

    group_key: Any = IndexKey() if stimulus["use_index_key"] else first_group
    return {
        "public_members": [name for name in dir(value) if not name.startswith("_")],
        "member": member,
        "observation": normalize(observed),
        "full_match": match_value(value),
        "valid_group": observe(lambda: value.group(group_key)),
        "invalid_group": observe(lambda: value.group(stimulus["invalid_group"])),
        "index_group": observe(lambda: value.group(IndexKey())),
        "getitem": observe(lambda: value[second_group]),
        "match_type": isinstance(value, module.Match),
    }


def _actual_flags(module: Any, stimulus: Mapping[str, Any]) -> dict[str, Any]:
    high = stimulus["high_flag"]

    class IndexedFlag:
        def __index__(self) -> int:
            return high | int(module.I)

    options: list[tuple[str, Any]] = [
        ("unknown", high),
        ("unknown-and-ignorecase", high | int(module.I)),
        ("unknown-and-multiline", high | int(module.M)),
        ("indexed", IndexedFlag()),
        ("inverted-known", ~module.RegexFlag(module.I | module.M)),
    ]
    results = []
    for label, flags in options:
        def run(flags: Any = flags) -> Any:
            pattern = module.compile(stimulus["expression"], flags)
            return {
                "flags": int(pattern.flags),
                "repr": repr(pattern),
                "match": match_value(pattern.search(stimulus["subject"])),
            }
        results.append({"kind": label, "actual_compile": observe(run)})
    return {
        "cases": results,
        "unknown_flag_intflag": normalize(module.RegexFlag(high)),
        "noflag_identity": module.NOFLAG is module.RegexFlag(0),
    }


def _pattern_pickle(module: Any, stimulus: Mapping[str, Any]) -> dict[str, Any]:
    expression: Any = stimulus["expression"]
    subject: Any = stimulus["subject"]
    if stimulus["use_bytes"]:
        expression = expression.encode("ascii")
        subject = subject.encode("ascii")
    pattern = module.compile(expression, module.I)
    records = []
    for protocol in range(pickle.HIGHEST_PROTOCOL + 1):
        def roundtrip(protocol: int = protocol) -> Any:
            restored = pickle.loads(pickle.dumps(pattern, protocol=protocol))
            return {
                "public_pattern_type": isinstance(restored, module.Pattern),
                "source_pattern": normalize(restored.pattern),
                "flags": int(restored.flags),
                "same_cached_object": restored is pattern,
                "structural_equality": restored == pattern,
                "same_hash": hash(restored) == hash(pattern),
                "match": match_value(restored.search(subject)),
            }
        records.append({"protocol": protocol, "roundtrip": observe(roundtrip)})
    return {
        "protocol_count": pickle.HIGHEST_PROTOCOL + 1,
        "protocols": records,
        "copy_identity": copy.copy(pattern) is pattern,
        "deepcopy_identity": copy.deepcopy(pattern) is pattern,
    }


def _cache_and_weakref(module: Any, stimulus: Mapping[str, Any]) -> dict[str, Any]:
    expression: Any = stimulus["expression"]
    subject: Any = stimulus["subject"]
    if stimulus["use_bytes"]:
        expression = expression.encode("ascii")
        subject = subject.encode("ascii")
    module.purge()
    first = module.compile(expression)
    cached = module.compile(expression)
    proxy_result = observe(lambda: match_value(
        weakref.proxy(first).search(subject),
    ))
    module.purge()
    restored = module.compile(expression)
    different = module.compile(expression, module.I)
    return {
        "same_cached_object": first is cached,
        "purge_recreates_object": first is not restored,
        "equal_after_purge": first == restored,
        "hash_equal_after_purge": hash(first) == hash(restored),
        "different_flags_equal": first == different,
        "weakref_proxy": proxy_result,
        "match": match_value(restored.search(subject)),
    }


def _match_copy(module: Any, stimulus: Mapping[str, Any]) -> dict[str, Any]:
    value = module.search(stimulus["expression"], stimulus["subject"])
    require(value is not None, "the seeded match copy probe lacks its real Match")
    return {
        "copy_identity": copy.copy(value) is value,
        "deepcopy_identity": copy.deepcopy(value) is value,
        "weakref": observe(lambda: weakref.ref(value)() is value),
        "match": match_value(value),
    }


def _live_buffer(module: Any, stimulus: Mapping[str, Any]) -> dict[str, Any]:
    raw = bytearray(stimulus["match_subject"].encode("ascii"))
    expression = stimulus["expression"].encode("ascii")
    iterator = module.finditer(expression, raw)
    blocked = observe(lambda: raw.extend(b"x" * 400))
    matches = [match_value(item) for item in iterator]
    del iterator
    gc.collect()
    released = observe(lambda: raw.extend(b"y" * 400))
    return {
        "live_iterator_resize": blocked,
        "matches": matches,
        "resize_after_release": released,
        "final_size": len(raw),
    }


def _scanner_buffer(module: Any, stimulus: Mapping[str, Any]) -> dict[str, Any]:
    raw = bytearray(stimulus["match_subject"].encode("ascii"))
    pattern = module.compile(stimulus["expression"].encode("ascii"))
    scanner = pattern.scanner(raw)
    while_scanner = observe(lambda: raw.extend(b"s"))
    first = scanner.search()
    first_record = match_value(first)
    while_match = observe(lambda: raw.extend(b"m"))
    del first
    del scanner
    gc.collect()
    after = observe(lambda: raw.extend(b"z"))
    return {
        "live_scanner_resize": while_scanner,
        "match": first_record,
        "live_match_resize": while_match,
        "resize_after_release": after,
    }


def _typed_buffer(module: Any, stimulus: Mapping[str, Any]) -> dict[str, Any]:
    raw = stimulus["match_subject"].encode("ascii")
    kind = stimulus["typed_buffer_kind"]
    if kind == "bytearray":
        value: Any = bytearray(raw)
    elif kind == "memoryview":
        value = memoryview(bytearray(raw))
    elif kind == "unsigned-short":
        storage = array("H", [byte for byte in raw])
        value = memoryview(storage)
    elif kind == "strided":
        interleaved = bytearray()
        for byte in raw:
            interleaved.extend((byte, ord("#")))
        value = memoryview(interleaved)[::2]
    elif kind == "released":
        value = memoryview(bytearray(raw))
        value.release()
    else:
        value = memoryview(bytearray())
    return {
        "kind": kind,
        "actual_search": observe(lambda: match_value(module.search(
            stimulus["expression"].encode("ascii"), value,
        ))),
    }


def _unicode_names(module: Any, stimulus: Mapping[str, Any]) -> dict[str, Any]:
    name = stimulus["unicode_name"]
    character = unicodedata.lookup(name)
    pattern = "\\N{" + name + "}" + stimulus["token"]
    subject = character + stimulus["token"]
    return {
        "unicode_name": name,
        "actual_character": character,
        "match": match_value(module.fullmatch(pattern, subject)),
        "lowercase_name": observe(lambda: match_value(module.fullmatch(
            "\\N{" + name.lower() + "}" + stimulus["token"], subject,
        ))),
        "bytes_rejection": observe(lambda: module.compile(pattern.encode("ascii"))),
    }


def _unicode_groups(module: Any, stimulus: Mapping[str, Any]) -> dict[str, Any]:
    name = stimulus["unicode_group"]
    token = stimulus["token"]
    expression = "(?P<" + name + ">" + token + ")"
    subject = "before-" + token + "-after"
    pattern = module.compile(expression)
    value = pattern.search(subject)
    require(value is not None, "the actual non-ASCII public named group vanished")
    return {
        "name": name,
        "group": observe(lambda: value.group(name)),
        "groupdict": normalize(value.groupdict()),
        "groupindex": normalize(dict(pattern.groupindex)),
        "replacement": observe(lambda: module.sub(
            expression, "[\\g<" + name + ">]", subject,
        )),
        "bytes_name": observe(lambda: module.compile(expression.encode("utf-8"))),
    }


def _extended_casefold(module: Any, stimulus: Mapping[str, Any]) -> dict[str, Any]:
    pairs = (
        ("k", "\u212a"), ("i", "\u0130"), ("\u017f", "S"),
        ("\u03c3", "\u03c2"), ("\ufb05", "\ufb06"),
        ("\U00010400", "\U00010428"),
    )
    results = []
    for pattern, value in pairs:
        subject = value + stimulus["token"]
        expression = pattern + stimulus["token"]
        results.append({
            "pattern": pattern,
            "value": value,
            "unicode": match_value(module.fullmatch(expression, subject, module.I)),
            "ascii": match_value(module.fullmatch(
                expression, subject, module.I | module.A,
            )),
            "boundary": normalize(module.findall(r"\b", subject)),
        })
    return {"pairs": results}


def _normalized_codeset() -> str:
    encoding = locale.getencoding()
    return "".join(character for character in encoding.lower()
                   if character.isalnum())


def _preflight_real_locales(locale_names: Mapping[str, str]) -> dict[str, Any]:
    iso = locale_names.get("iso8859_1")
    utf = locale_names.get("utf8")
    require(
        type(iso) is str and type(utf) is str and iso and utf and iso != utf,
        "two genuinely available distinct fresh ISO-8859-1 and UTF-8 locales "
        "are required",
    )
    original = locale.setlocale(locale.LC_CTYPE)
    original_locpath = os.environ.get("LOCPATH")
    observed: dict[str, str] = {}
    try:
        for kind, name, encodings in (
            ("iso8859_1", iso, {"iso88591", "latin1"}),
            ("utf8", utf, {"utf8"}),
        ):
            locale.setlocale(locale.LC_CTYPE, name)
            actual = _normalized_codeset()
            require(
                actual in encodings,
                "the actual independently provided " + kind
                + " locale has the wrong character encoding",
            )
            observed[kind] = actual
    except locale.Error as error:
        raise PublicSurfaceError(
            "a genuine freshly provisioned ISO-8859-1 or UTF-8 locale "
            "is unavailable",
        ) from error
    finally:
        try:
            locale.setlocale(locale.LC_CTYPE, original)
            restored = locale.setlocale(locale.LC_CTYPE)
        except locale.Error as error:
            raise PublicSurfaceError(
                "a real locale preflight could not restore LC_CTYPE",
            ) from error
        require(restored == original,
                "a real locale preflight did not restore LC_CTYPE")
        require(os.environ.get("LOCPATH") == original_locpath,
                "a real locale preflight changed the process locale path")
    return {
        "iso8859_1_codeset": observed["iso8859_1"],
        "utf8_codeset": observed["utf8"],
        "ctype_restored": True,
        "locale_path_unchanged": True,
    }


def _locale_probe(
    module: Any,
    stimulus: Mapping[str, Any],
    locale_names: Mapping[str, str],
) -> dict[str, Any]:
    iso = locale_names.get("iso8859_1")
    utf = locale_names.get("utf8")
    require(
        type(iso) is str and type(utf) is str and iso and utf and iso != utf,
        "real independently available ISO-8859-1 and UTF-8 locales are required",
    )
    original = locale.setlocale(locale.LC_CTYPE)
    original_locpath = os.environ.get("LOCPATH")
    expression = br"\w+"
    high = b"\xe4"
    rows: list[dict[str, Any]] = []
    try:
        locale.setlocale(locale.LC_CTYPE, iso)
        require(_normalized_codeset() in {"iso88591", "latin1"},
                "the first real locale is not ISO-8859-1")
        pattern = module.compile(expression, module.L | module.I)
        initially_compiled = pattern
        for kind, chosen, encoding in (
            ("iso8859_1", iso, {"iso88591", "latin1"}),
            ("utf8", utf, {"utf8"}),
            ("iso8859_1_again", iso, {"iso88591", "latin1"}),
        ):
            locale.setlocale(locale.LC_CTYPE, chosen)
            codeset = _normalized_codeset()
            require(codeset in encoding,
                    "an actual locale switch did not install its claimed encoding")
            rows.append({
                "locale": kind,
                "codeset": codeset,
                "same_compiled_pattern": pattern is initially_compiled,
                "high_byte": match_value(pattern.fullmatch(high)),
                "ascii_byte": match_value(pattern.fullmatch(b"A")),
                "scanner": match_value(pattern.scanner(high).search()),
            })
        module.purge()
        rebuilt = module.compile(expression, module.L | module.I)
        return {
            "transitions": rows,
            "purge_recreates": rebuilt is not pattern,
            "purge_match": match_value(rebuilt.fullmatch(high)),
            "locale_with_text": observe(lambda: module.compile(
                stimulus["expression"], module.L,
            )),
            "locale_with_ascii": observe(lambda: module.compile(
                expression, module.L | module.A,
            )),
        }
    except locale.Error as error:
        raise PublicSurfaceError(
            "a genuine locale matching transition or restoration failed",
        ) from error
    finally:
        try:
            locale.setlocale(locale.LC_CTYPE, original)
            restored = locale.setlocale(locale.LC_CTYPE)
        except locale.Error as error:
            raise PublicSurfaceError(
                "a real public locale probe could not restore LC_CTYPE",
            ) from error
        require(restored == original,
                "an actual public locale probe failed to restore LC_CTYPE")
        require(os.environ.get("LOCPATH") == original_locpath,
                "an actual public locale probe changed its locale path")


def _normalized_mapping(value: Any, label: str) -> dict[str, Any]:
    require(
        isinstance(value, dict)
        and set(value) == {"kind", "items"}
        and value.get("kind") == "mapping"
        and isinstance(value.get("items"), list),
        "a real normalized " + label + " mapping was removed or forged",
    )
    result: dict[str, Any] = {}
    for pair in value["items"]:
        require(
            isinstance(pair, list)
            and len(pair) == 2
            and type(pair[0]) is str
            and pair[0] not in result,
            "a real normalized " + label + " field was removed or duplicated",
        )
        result[pair[0]] = pair[1]
    return result


def _validate_locale_case(record: Any) -> None:
    require(
        isinstance(record, dict)
        and record.get("cohort") in {
            "real-locale-switch-on-compiled-bytes",
            "real-locale-invalid-flags-and-cache",
        }
        and isinstance(record.get("outcome"), dict)
        and record["outcome"].get("status") == "return"
        and set(record["outcome"]) == {"status", "value"},
        "an unavailable or failing real locale cannot pass as an equal exception",
    )
    result = _normalized_mapping(record["outcome"]["value"], "locale result")
    transitions = result.get("transitions")
    require(
        isinstance(transitions, dict)
        and transitions.get("kind") == "list"
        and isinstance(transitions.get("items"), list)
        and len(transitions["items"]) == 3,
        "exactly three real ISO-8859-1/UTF-8/ISO-8859-1 transitions are required",
    )
    for actual, (expected_name, encodings, high_matches) in zip(
        transitions["items"],
        (
            ("iso8859_1", {"iso88591", "latin1"}, True),
            ("utf8", {"utf8"}, False),
            ("iso8859_1_again", {"iso88591", "latin1"}, True),
        ),
        strict=True,
    ):
        transition = _normalized_mapping(actual, "locale transition")
        require(
            transition.get("locale") == expected_name
            and transition.get("codeset") in encodings
            and transition.get("same_compiled_pattern") is True
            and transition.get("ascii_byte") is not None
            and (transition.get("high_byte") is not None) is high_matches
            and (transition.get("scanner") is not None) is high_matches,
            "a genuine same-pattern locale transition or high-byte match failed",
        )
    require(
        result.get("purge_recreates") is True
        and result.get("purge_match") is not None,
        "a genuine locale-sensitive pattern was not recreated after purge",
    )
    for label in ("locale_with_text", "locale_with_ascii"):
        operation = _normalized_mapping(result.get(label), label)
        require(
            operation.get("status") == "raise",
            "a real invalid LOCALE flag combination was silently accepted",
        )


def _callback_failure(module: Any, stimulus: Mapping[str, Any]) -> dict[str, Any]:
    events: list[Any] = []
    subject = stimulus["token"] + " 123 " + stimulus["token"] + " 456"
    fail_after = stimulus["callback_fail_after"]

    def callback(value: Any) -> str:
        events.append({
            "ordinal": len(events),
            "group": normalize(value.group(0)),
            "span": normalize(value.span()),
            "nested": match_value(module.search(r"\d+", value.group(0))),
        })
        if len(events) == fail_after:
            raise ValueError("stage17 seeded replacement callback failure")
        return value.group(0).upper()

    outcome = observe(lambda: module.sub(r"[a-f0-9]+", callback, subject))
    return {"operation": outcome, "events": events, "fail_after": fail_after}


def _scanner_failure(module: Any, stimulus: Mapping[str, Any]) -> dict[str, Any]:
    events: list[Any] = []
    token = stimulus["token"]
    fail_after = stimulus["callback_fail_after"]

    def action(_scanner: Any, value: str) -> str:
        current = getattr(_scanner, "match", None)
        events.append({
            "ordinal": len(events),
            "token": value,
            "span": (
                observe(lambda: current.span()) if current is not None
                else {"status": "not-available"}
            ),
            "nested": observe(lambda: match_value(module.search(r"\d+", value))),
        })
        if len(events) == fail_after:
            raise ValueError("stage17 seeded scanner callback failure")
        return value.upper()

    scanner = module.Scanner([(r"[a-f0-9]+", action), (r"\s+", None)])
    outcome = observe(lambda: scanner.scan(token + " 123 " + token + " 456"))
    return {"operation": outcome, "events": events, "fail_after": fail_after}


def _positional_warning(module: Any, stimulus: Mapping[str, Any]) -> dict[str, Any]:
    operation = stimulus["warning_operation"]
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        if operation == "sub":
            outcome = observe(lambda: module.sub(
                stimulus["expression"], "x", stimulus["subject"], 1,
            ))
        elif operation == "subn":
            outcome = observe(lambda: module.subn(
                stimulus["expression"], "x", stimulus["subject"], 1,
            ))
        else:
            outcome = observe(lambda: module.split(
                stimulus["expression"], stimulus["subject"], 1,
            ))
    return {
        "operation": operation,
        "outcome": outcome,
        "warnings": _warning_records(captured),
    }


def _future_warning(module: Any, stimulus: Mapping[str, Any]) -> dict[str, Any]:
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        outcome = observe(lambda: module.compile(stimulus["future_pattern"]))
    return {
        "pattern": stimulus["future_pattern"],
        "outcome": outcome,
        "warnings": _warning_records(captured),
    }


def _mapping_identity(module: Any, stimulus: Mapping[str, Any]) -> dict[str, Any]:
    pattern = module.compile(stimulus["expression"])
    first = pattern.groupindex
    second = pattern.groupindex
    return {
        "type": type(first).__name__,
        "mapping": normalize(dict(first)),
        "same_object": first is second,
        "mappingproxy": isinstance(first, types.MappingProxyType),
        "mutation": observe(lambda: first.__setitem__("forged", 99)),
        "delete": observe(lambda: first.__delitem__(stimulus["group_names"][0])),
        "contains": stimulus["group_names"][0] in first,
        "keys": normalize(tuple(first.keys())),
        "match": match_value(pattern.search(stimulus["subject"])),
    }


def _match_identity(module: Any, stimulus: Mapping[str, Any]) -> dict[str, Any]:
    value = module.search(stimulus["expression"], stimulus["subject"])
    require(value is not None, "the real cached Match property is missing")
    first_group, second_group = stimulus["group_names"]
    return {
        "regs": normalize(value.regs),
        "regs_same_object": value.regs is value.regs,
        "pattern_identity": value.re is module.compile(stimulus["expression"]),
        "group": observe(lambda: value.group(first_group, second_group)),
        "invalid_name": observe(lambda: value.group("missing_" + stimulus["token"])),
        "invalid_index": observe(lambda: value.group(1_000_000)),
        "invalid_item": observe(lambda: value["missing_" + stimulus["token"]]),
        "unmatched_start": observe(lambda: value.start(1_000_000)),
        "expand": observe(lambda: value.expand(
            "\\g<" + second_group + ">-\\g<" + first_group + ">",
        )),
    }


def _generic_alias(module: Any, stimulus: Mapping[str, Any]) -> dict[str, Any]:
    origins = (module.Pattern, module.Match)
    arguments = (str, bytes)
    records: list[dict[str, Any]] = []
    for origin in origins:
        for argument in arguments:
            alias = origin[argument]
            for protocol in range(pickle.HIGHEST_PROTOCOL + 1):
                def roundtrip(
                    alias: Any = alias,
                    origin: Any = origin,
                    argument: Any = argument,
                    protocol: int = protocol,
                ) -> Any:
                    restored = pickle.loads(pickle.dumps(alias, protocol=protocol))
                    return {
                        "generic_alias": isinstance(restored, types.GenericAlias),
                        "origin_identity": restored.__origin__ is origin,
                        "args": normalize(restored.__args__),
                        "origin": getattr(typing.get_origin(restored), "__name__", None),
                        "typing_args": normalize(typing.get_args(restored)),
                        "equality": restored == alias,
                        "hash_equal": hash(restored) == hash(alias),
                        "argument_identity": restored.__args__ == (argument,),
                    }
                records.append({
                    "origin": origin.__name__,
                    "argument": argument.__name__,
                    "protocol": protocol,
                    "roundtrip": observe(roundtrip),
                })
    return {
        "protocol_count": pickle.HIGHEST_PROTOCOL + 1,
        "roundtrips": records,
        "seeded_match": match_value(module.search(
            stimulus["expression"], stimulus["subject"],
        )),
    }


def _typing_contract(module: Any, stimulus: Mapping[str, Any]) -> dict[str, Any]:
    aliases = []
    for origin in (module.Pattern, module.Match):
        for argument in (str, bytes):
            alias = origin[argument]
            aliases.append({
                "origin": origin.__name__,
                "argument": argument.__name__,
                "generic_alias": isinstance(alias, types.GenericAlias),
                "origin_identity": alias.__origin__ is origin,
                "typing_origin_identity": typing.get_origin(alias) is origin,
                "args": normalize(alias.__args__),
                "typing_args": normalize(typing.get_args(alias)),
                "parameters": normalize(alias.__parameters__),
                "same_subscription_equal": alias == origin[argument],
                "same_subscription_hash": hash(alias) == hash(origin[argument]),
                "copy_origin": copy.copy(alias).__origin__ is origin,
                "deepcopy_origin": copy.deepcopy(alias).__origin__ is origin,
                "instance_check": observe(lambda alias=alias: isinstance(
                    module.compile(stimulus["expression"]), alias,
                )),
                "subclass_check": observe(lambda alias=alias: issubclass(
                    module.Pattern, alias,
                )),
            })
    return {
        "aliases": aliases,
        "pattern_invalid_subscription": observe(lambda: module.Pattern[()]),
        "match_invalid_subscription": observe(lambda: module.Match[()]),
    }


def _error_contract(module: Any, stimulus: Mapping[str, Any]) -> dict[str, Any]:
    invalid = (
        "(" + stimulus["token"],
        "[z-a]" + stimulus["token"],
        stimulus["token"] + "\n(",
        "\\N{NO SUCH NAME " + stimulus["token"] + "}",
    )
    entries = []
    for expression in invalid:
        try:
            module.compile(expression)
        except BaseException as error:
            entries.append({
                "pattern": expression,
                "actual_error": normalize(error),
                "public_error": isinstance(error, module.PatternError),
                "public_alias": isinstance(error, module.error),
                "pickle": observe(lambda error=error: normalize(pickle.loads(
                    pickle.dumps(error, protocol=pickle.HIGHEST_PROTOCOL),
                ))),
            })
        else:
            entries.append({"pattern": expression, "unexpected_success": True})
    return {"errors": entries}


def _subinterpreter_capability(stimulus: Mapping[str, Any]) -> dict[str, Any]:
    # An independently owned V10 implementation does not expose a genuine,
    # audited fresh-interpreter guard. Importing a candidate in a new Python
    # interpreter would silently remove its no-delegation protections. Do not
    # substitute an unguarded smoke test or claim interpreter compatibility.
    return {
        "status": "NOT RUN",
        "reason": "no authenticated fresh-interpreter candidate guard is published",
        "candidate_imported": False,
        "subinterpreter_started": False,
        "seeded_expression": stimulus["expression"],
    }


def _evaluate_base(module: Any, stimulus: Mapping[str, Any]) -> Any:
    cohort = stimulus["cohort"]
    if cohort == "complete-public-exports":
        exports = getattr(module, "__all__")
        return {
            "exports": normalize(list(exports)),
            "unique": len(exports) == len(set(exports)),
            "all_resolve": all(hasattr(module, name) for name in exports),
            "scanner_is_public": hasattr(module, "Scanner"),
            "scanner_is_exported": "Scanner" in exports,
            "debug_is_public": hasattr(module, "DEBUG"),
            "debug_is_exported": "DEBUG" in exports,
            "selected": _export_probe(module, stimulus),
        }
    if cohort == "module-aliases-and-version":
        left, right = stimulus["alias"]
        return {
            "version": getattr(module, "__version__", None),
            "aliases": [getattr(module, a) is getattr(module, b)
                        for a, b in PUBLIC_ALIASES],
            "selected_alias": [left, right],
            "selected_identity": getattr(module, left) is getattr(module, right),
            "actual_match": match_value(module.search(
                stimulus["expression"], stimulus["subject"],
                safe_flags(module, stimulus["safe_flag_selector"]),
            )),
            "verbose_match": match_value(module.search(
                stimulus["verbose_expression"], stimulus["subject"], module.X,
            )),
            "escaped_match": match_value(module.search(
                module.escape(stimulus["escaped_literal"]),
                "before-" + stimulus["escaped_literal"] + "-after",
            )),
            "debug": (
                _public_debug(module, stimulus["expression"], stimulus["subject"])
                if stimulus["check_debug"] else None
            ),
        }
    if cohort == "regexflag-intflag-and-noflag":
        flag = module.RegexFlag(stimulus["flag_value"])
        selected = safe_flags(module, stimulus["safe_flag_selector"])
        return {
            "flag": normalize(flag),
            "noflag": int(module.NOFLAG),
            "noflag_identity": module.NOFLAG is module.RegexFlag(0),
            "safe_flags": int(selected),
            "match": match_value(module.search(
                stimulus["expression"], stimulus["subject"], selected,
            )),
        }
    if cohort == "public-purge-and-cache-identity":
        module.purge()
        first = module.compile(stimulus["expression"])
        second = module.compile(stimulus["expression"])
        flagged = module.compile(stimulus["expression"], module.I)
        for index in range(stimulus["cache_pressure"]):
            module.compile(stimulus["match_subject"] + "-cache-" + str(index))
        retained = module.compile(stimulus["expression"])
        module.purge()
        restored = module.compile(stimulus["expression"])
        return {
            "cached_identity": first is second,
            "flags_distinct": first is not flagged,
            "retained_identity": retained is first,
            "purge_clears_identity": restored is not retained,
            "match": match_value(restored.search(stimulus["subject"])),
        }
    if cohort == "pattern-properties":
        return _pattern_probe(module, stimulus)
    if cohort == "pattern-pos-and-endpos-windows":
        pattern = module.compile(stimulus["expression"], module.I)
        subject = stimulus["subject"]
        left, right = stimulus["pos"], stimulus["endpos"]
        if stimulus["use_keywords"]:
            values = [
                pattern.search(subject, pos=left, endpos=right),
                pattern.match(subject, pos=left, endpos=right),
                pattern.fullmatch(subject, pos=left, endpos=right),
            ]
        else:
            values = [
                pattern.search(subject, left, right),
                pattern.match(subject, left, right),
                pattern.fullmatch(subject, left, right),
            ]
        return {
            "search": match_value(values[0]),
            "match": match_value(values[1]),
            "fullmatch": match_value(values[2]),
            "keywords": stimulus["use_keywords"],
        }
    if cohort == "match-properties-and-groups":
        return _match_probe(module, stimulus)
    if cohort in {"scanner-string-and-callback", "scanner-bytes-and-remainder"}:
        return _scanner_probe(module, stimulus)
    if cohort == "contiguous-buffer-inputs":
        raw = stimulus["raw_subject"].encode("ascii")
        values = {
            "bytes": raw,
            "bytearray": bytearray(raw),
            "memoryview": memoryview(raw),
        }
        return {
            "kind": stimulus["buffer_kind"],
            "match": match_value(module.search(
                stimulus["expression"].encode("ascii"),
                values[stimulus["buffer_kind"]],
            )),
        }
    if cohort == "noncontiguous-and-released-buffers":
        raw = stimulus["raw_subject"].encode("ascii")
        if stimulus["buffer_kind"] == "released":
            view = memoryview(bytearray(raw))
            view.release()
        else:
            interleaved = bytearray()
            for byte in raw:
                interleaved.extend((byte, ord("#")))
            view = memoryview(interleaved)[::2]
        return {
            "kind": stimulus["buffer_kind"],
            "match": match_value(module.search(
                stimulus["expression"].encode("ascii"), view,
            )),
        }
    if cohort == "replacement-numeric-and-named":
        result: dict[str, Any] = {
            "subn": normalize(module.subn(
                stimulus["expression"], stimulus["replacement"],
                stimulus["subject"], count=stimulus["count"],
            )),
        }
        if stimulus["record_warning"]:
            with warnings.catch_warnings(record=True) as captured:
                warnings.simplefilter("always")
                actual = module.sub(
                    stimulus["expression"], stimulus["replacement"],
                    stimulus["subject"], stimulus["count"],
                )
            result["positional_warning"] = {
                "value": normalize(actual), "warnings": _warning_records(captured),
            }
        return result
    if cohort == "replacement-octal-and-errors":
        return module.sub(
            stimulus["expression"], stimulus["replacement"], stimulus["subject"],
        )
    if cohort == "replacement-callables":
        events: list[Any] = []

        def callback(value: Any) -> str:
            if stimulus["raises"]:
                raise ValueError("public replacement callback failure")
            events.append(normalize(value.group(0)))
            return value.group(0).upper()

        return {
            "value": module.sub(
                stimulus["callback_expression"], callback,
                stimulus["callback_subject"], count=stimulus["count"],
            ),
            "calls": events,
        }
    if cohort == "pattern-error-coordinates":
        return observe(lambda: module.compile(stimulus["invalid_pattern"]))
    if cohort == "unicode-astral-and-surrogates":
        value = stimulus["unicode_subject"]
        return {
            "dot": match_value(module.search(".", value)),
            "escaped": module.escape(value),
            "word": match_value(module.search(r"\w+", value)),
            "boundary": normalize(module.findall(r"\b", value)),
        }
    if cohort == "unicode-casefold-and-flags":
        pattern = stimulus["casefold_pattern"]
        value = stimulus["casefold_subject"]
        return {
            "unicode": match_value(module.fullmatch(pattern, value, module.I)),
            "ascii": match_value(module.fullmatch(
                pattern, value, module.I | module.A,
            )),
        }
    if cohort == "generic-types-and-standard-pickle":
        origin = getattr(module, stimulus["origin"])
        argument = {"str": str, "bytes": bytes}[stimulus["argument"]]
        alias = origin[argument]
        protocol = stimulus["pickle_protocol"]
        restored = pickle.loads(pickle.dumps(alias, protocol=protocol))
        pattern = module.compile(stimulus["copy_pattern"])
        return {
            "origin": origin.__name__,
            "argument": argument.__name__,
            "protocol": protocol,
            "alias": isinstance(alias, types.GenericAlias),
            "restored_alias": isinstance(restored, types.GenericAlias),
            "origin_identity": restored.__origin__ is origin,
            "args": normalize(restored.__args__),
            "equal": restored == alias,
            "same_hash": hash(restored) == hash(alias),
            "copy_origin": copy.copy(alias).__origin__ is origin,
            "deepcopy_origin": copy.deepcopy(alias).__origin__ is origin,
            "pattern_copy_identity": copy.copy(pattern) is pattern,
            "pattern_deepcopy_identity": copy.deepcopy(pattern) is pattern,
            "match": match_value(module.search(
                stimulus["copy_pattern"], stimulus["subject"],
            )),
        }
    if cohort == "reentrant-replacement-callbacks":
        events: list[Any] = []

        def callback(value: Any) -> str:
            nested = module.search(r"\d+", value.group(0) + stimulus["subject"])
            events.append(match_value(nested))
            return value.group(0).upper()

        return {
            "result": module.sub(
                stimulus["callback_expression"], callback,
                stimulus["callback_subject"], count=stimulus["count"],
            ),
            "nested": events,
        }
    if cohort == "synchronized-compile-match-and-purge":
        return _threaded_probe(module, stimulus)
    raise PublicSurfaceError("a standalone original public cohort is missing")


def evaluate_case(
    module: Any,
    row: Mapping[str, Any],
    *,
    locale_names: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    stimulus = build_stimulus(row)
    cohort = stimulus["cohort"]
    try:
        if cohort in BASE_COHORTS:
            value = _evaluate_base(module, stimulus)
        elif cohort in {
            "unknown-flags-actually-compiled",
            "mixed-inverted-and-indexed-flags",
        }:
            value = _actual_flags(module, stimulus)
        elif cohort == "compiled-pattern-every-pickle-protocol":
            value = _pattern_pickle(module, stimulus)
        elif cohort == "pattern-cache-equality-hash-and-weakref":
            value = _cache_and_weakref(module, stimulus)
        elif cohort == "match-copy-and-weakref-behavior":
            value = _match_copy(module, stimulus)
        elif cohort == "live-finditer-buffer-resize-and-release":
            value = _live_buffer(module, stimulus)
        elif cohort == "live-scanner-and-match-buffer-lifetime":
            value = _scanner_buffer(module, stimulus)
        elif cohort == "typed-empty-strided-and-released-buffers":
            value = _typed_buffer(module, stimulus)
        elif cohort == "valid-unicode-character-names":
            value = _unicode_names(module, stimulus)
        elif cohort == "unicode-and-astral-named-captures":
            value = _unicode_groups(module, stimulus)
        elif cohort == "extended-unicode-folding-and-boundaries":
            value = _extended_casefold(module, stimulus)
        elif cohort in {
            "real-locale-switch-on-compiled-bytes",
            "real-locale-invalid-flags-and-cache",
        }:
            value = _locale_probe(module, stimulus, locale_names or {})
        elif cohort == "replacement-callback-failure-side-effects":
            value = _callback_failure(module, stimulus)
        elif cohort == "scanner-callback-failure-side-effects":
            value = _scanner_failure(module, stimulus)
        elif cohort == "public-deprecation-warning-caller-location":
            value = _positional_warning(module, stimulus)
        elif cohort == "ambiguous-character-set-future-warnings":
            value = _future_warning(module, stimulus)
        elif cohort == "pattern-group-mapping-and-error-identity":
            value = _mapping_identity(module, stimulus)
        elif cohort == "match-regs-identity-and-group-errors":
            value = _match_identity(module, stimulus)
        elif cohort == "public-generic-pickle-every-protocol":
            value = _generic_alias(module, stimulus)
        elif cohort == "public-typing-origin-args-and-rejections":
            value = _typing_contract(module, stimulus)
        elif cohort == "public-error-fields-cause-and-pickling":
            value = _error_contract(module, stimulus)
        elif cohort == "separate-interpreter-guard-capability":
            value = _subinterpreter_capability(stimulus)
        else:
            raise PublicSurfaceError("an actual additive public probe was omitted")
        outcome = {"status": "return", "value": normalize(value)}
    except (PublicSurfaceError, locale.Error, MemoryError, KeyboardInterrupt, SystemExit):
        raise
    except Exception as error:
        outcome = {"status": "raise", "exception": normalize(error)}
    return {
        "id": row["id"],
        "cohort": cohort,
        "stimulus_sha256": digest(stimulus),
        "outcome": outcome,
    }


def _safe_relative(relative: Any, *, approved: frozenset[str] | None = None) -> str:
    require(type(relative) is str, "an exact repository-relative path is required")
    value = PurePosixPath(relative)
    require(
        not value.is_absolute()
        and ".." not in value.parts
        and "\\" not in relative
        and "\x00" not in relative
        and value.as_posix() == relative
        and (approved is None or relative in approved),
        "refusing a substituted, escaping, or unapproved evidence path",
    )
    return relative


def _read_bounded(relative: str, limit: int, *, expected: str) -> bytes:
    relative = _safe_relative(relative)
    require(type(limit) is int and 0 < limit <= MAX_COMPRESSED_PROOF_BYTES,
            "a genuine bounded source or proof limit is required")
    require(valid_sha256(expected), "a real externally published SHA-256 is required")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(ROOT / relative, flags)
    except OSError as error:
        raise PublicSurfaceError("the exact authenticated input is unavailable: "
                                 + relative) from error
    try:
        metadata = os.fstat(descriptor)
        require(stat.S_ISREG(metadata.st_mode) and 0 < metadata.st_size <= limit,
                "the real authenticated input is not one bounded regular file: "
                + relative)
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, 65_536)
            if not chunk:
                break
            total += len(chunk)
            require(total <= limit, "the authenticated input exceeds its bound")
            chunks.append(chunk)
    finally:
        os.close(descriptor)
    payload = b"".join(chunks)
    require(len(payload) == metadata.st_size,
            "the authenticated input changed while it was read")
    require(hashlib.sha256(payload).hexdigest() == expected,
            "the actual frozen input hash changed: " + relative)
    return payload


def _unique_json_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in result, "a genuine JSON report duplicates a field")
        result[key] = value
    return result


def _strict_json(payload: bytes, label: str) -> dict[str, Any]:
    def reject_constant(value: str) -> None:
        raise PublicSurfaceError("a non-finite JSON value was supplied: " + value)

    try:
        document = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_unique_json_pairs,
            parse_constant=reject_constant,
        )
    except (ValueError, UnicodeError, json.JSONDecodeError) as error:
        raise PublicSurfaceError("an authentic JSON report is malformed: " + label) from error
    require(isinstance(document, dict) and canonical(document) + b"\n" == payload,
            "the actual report is not complete canonical, newline-terminated JSON")
    return document


def _original_matrix(payload: bytes) -> dict[str, Any]:
    tree = ast.parse(payload.decode("utf-8"), filename=ORIGINAL_SOURCE_RELATIVE)
    public: list[dict[str, Any]] = []
    private_counts = {name: 0 for name in PRIVATE_CLASS_COUNTS}
    all_methods = 0
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        if node.name not in (*PUBLIC_CLASSES, *PRIVATE_CLASS_COUNTS):
            continue
        for method in node.body:
            if not isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if not method.name.startswith("test_"):
                continue
            all_methods += 1
            identity = node.name + "." + method.name
            if node.name in PRIVATE_CLASS_COUNTS:
                private_counts[node.name] += 1
                continue
            public.append({
                "test": identity,
                "class": node.name,
                "scope": "required-original-public-method",
                "source_line": method.lineno,
                "source_ast_sha256": hashlib.sha256(
                    ast.dump(method, include_attributes=False).encode("utf-8"),
                ).hexdigest(),
                "former_public_waiver": identity in FORMERLY_EXCLUDED_PUBLIC_METHODS,
                "actual_upstream_source": ORIGINAL_SOURCE_RELATIVE,
            })
    require(
        all_methods == 165
        and len(public) == 152
        and private_counts == PRIVATE_CLASS_COUNTS
        and len({row["test"] for row in public}) == 152
        and digest(public) == ORIGINAL_MATRIX_SHA256,
        "the complete genuine original 152-method Python source matrix changed",
    )
    return {"matrix": public, "private_counts": private_counts}


def _v5_vector(records: Any, matrix: list[dict[str, Any]]) -> list[dict[str, Any]]:
    require(isinstance(records, list) and len(records) == 152,
            "all 152 original public V5 method records are required")
    vector: list[dict[str, Any]] = []
    for original, record in zip(matrix, records, strict=True):
        require(
            isinstance(record, dict)
            and record.get("test") == original["test"]
            and record.get("source_ast_sha256") == original["source_ast_sha256"],
            "a genuine source-ordered original Python method was substituted",
        )
        status = record.get("status")
        if original["test"] == PRIVATE_CONDITIONAL_METHOD:
            require(
                status == "SKIP"
                and record.get("reason") == "requires debug build"
                and record.get("skip_kind") == "named-private-debug-condition",
                "the sole genuine upstream private-debug skip was changed",
            )
        else:
            require(status == "PASS", "a genuine original public method did not pass")
        vector.append({
            "test": record["test"],
            "source_ast_sha256": record["source_ast_sha256"],
            "status": status,
            "reason": record.get("reason"),
            "skip_kind": record.get("skip_kind"),
        })
    require(
        sum(row["status"] == "PASS" for row in vector) == 151
        and sum(row["status"] == "SKIP" for row in vector) == 1,
        "the real original 151-pass/one-private-skip denominator changed",
    )
    return vector


def _validate_original_v5_resources(
    report: Mapping[str, Any], records: list[dict[str, Any]],
) -> None:
    by_method = {row["test"]: row for row in records}
    require(
        len(by_method) == 152,
        "a real original upstream resource method was removed or duplicated",
    )
    for identity in (
        "ReTests.test_large_search", "ReTests.test_large_subn",
    ):
        actual = by_method.get(identity)
        require(isinstance(actual, dict),
                "a genuine original two-gibibyte method is missing: " + identity)
        resource = actual.get("resource")
        require(
            isinstance(resource, dict)
            and resource.get("declared_size") == 2**31
            and resource.get("delivered_size") == 2**31
            and type(resource.get("real_max_memuse")) is int
            and resource["real_max_memuse"] >= 18 * 2**31
            and resource.get("dry_run") is False,
            "an original two-gibibyte method was dry-run or fabricated: " + identity,
        )
    cpu = by_method.get("ReTests.test_search_anchor_at_beginning")
    require(isinstance(cpu, dict),
            "the original upstream CPU-bound test was omitted")
    cpu_resource = cpu.get("resource")
    require(
        isinstance(cpu_resource, dict)
        and cpu_resource.get("cpu_resource_enabled") is True
        and cpu_resource.get("subject_characters") == 10_000_000
        and cpu_resource.get("original_upper_bound_seconds") == 0.1
        and cpu_resource.get("original_stopwatch_assertion_passed") is True,
        "the actual original ten-million-character stopwatch test did not pass",
    )
    process = by_method.get("ReTests.test_regression_gh94675")
    require(isinstance(process, dict),
            "the original upstream fork regression was omitted")
    process_resource = process.get("resource")
    require(
        isinstance(process_resource, dict)
        and process_resource.get("process_started") is True
        and process_resource.get("start_method") == "fork"
        and process_resource.get("short_timeout_seconds") == 30.0,
        "the actual original fork regression or 30-second limit did not pass",
    )
    fixture = report.get("live_official_fixture_provenance")
    require(
        isinstance(fixture, dict)
        and fixture.get("actual_upstream_corpus_cases") == 403
        and fixture.get("actual_external_fixture_assertion_cases") == 11
        and fixture.get("support_tree_sha256") == ORIGINAL_SUPPORT_TREE_SHA256
        and fixture.get("official_support_shim_used") is False,
        "the complete genuine live original corpus or support tree is absent",
    )
    modules = fixture.get("modules")
    require(
        isinstance(modules, dict)
        and all(
            isinstance(modules.get(name), dict)
            and valid_sha256(modules[name].get("sha256"))
            for name in ("test.support", "test.support.warnings_helper", "test.re_tests")
        )
        and modules["test.re_tests"]["sha256"] == ORIGINAL_CORPUS_SHA256,
        "a genuine original upstream fixture module was changed or fabricated",
    )
    guard = report.get("guard")
    require(
        isinstance(guard, dict)
        and guard.get("passed") is True
        and guard.get("candidate_isolation") is True
        and guard.get("baseline_only") is True,
        "a genuine V5 Python reference loaded an independent candidate",
    )


def validate_v5_reference(
    document: Any,
    matrix: list[dict[str, Any]],
    *,
    actual_payload_sha256: str,
) -> dict[str, Any]:
    require(actual_payload_sha256 == V5_REFERENCE_SHA256,
            "source-only synthetic data cannot qualify as the real V5 reference")
    require(
        isinstance(document, dict)
        and document.get("schema")
        == "rebar-postfinal-cpython-full-public-locale-v5-self-oracle"
        and document.get("status") == "PASS"
        and document.get("synthetic") is False
        and document.get("python") == "3.14.6"
        and document.get("source_path") == V5_SOURCE_RELATIVE
        and document.get("source_sha256") == V5_SOURCE_SHA256
        and document.get("protocol_path") == V5_PROTOCOL_RELATIVE
        and document.get("protocol_sha256") == V5_PROTOCOL_SHA256
        and document.get("test_source_sha256") == ORIGINAL_SOURCE_SHA256
        and document.get("corpus_source_sha256") == ORIGINAL_CORPUS_SHA256
        and document.get("upstream_archive_sha256") == ORIGINAL_ARCHIVE_SHA256
        and document.get("official_support_tree_sha256") == ORIGINAL_SUPPORT_TREE_SHA256
        and document.get("official_support_module_count") == 26
        and document.get("public_method_matrix_sha256") == ORIGINAL_MATRIX_SHA256
        and document.get("all_original_methods") == 165
        and document.get("public_original_methods") == 152
        and document.get("private_original_methods") == 13
        and document.get("actual_upstream_corpus_cases") == 403
        and document.get("actual_external_fixture_assertion_cases") == 11
        and document.get("public_method_waivers") == []
        and document.get("actual_independent_reference_count") == 2
        and document.get("old_v7_campaign_prerequisite") is False
        and document.get("reference_candidate_imports") == 0
        and document.get("reference_candidate_audits_read") == 0
        and document.get("reference_candidate_proofs_read") == 0
        and document.get("reference_holdout_cases_read") == 0
        and document.get("performance") == "NOT MEASURED",
        "the real candidate-free complete two-worker V5 reference is not authentic",
    )
    roles = document.get("roles")
    require(
        isinstance(roles, dict)
        and tuple(roles) == ("reference_a", "reference_b"),
        "two original independently retained Python references are required",
    )
    vectors: list[list[dict[str, Any]]] = []
    for label in ("reference_a", "reference_b"):
        report = roles[label]
        require(isinstance(report, dict), "an actual original V5 worker is missing")
        records = report.get("records")
        vector = _v5_vector(records, matrix)
        require(
            report.get("role") == "stdlib"
            and report.get("status") == "PASS"
            and report.get("methods") == 152
            and report.get("record_count") == 152
            and report.get("records_sha256") == digest(records)
            and report.get("executed_test_source_sha256") == ORIGINAL_SOURCE_SHA256
            and report.get("official_support_tree_sha256") == ORIGINAL_SUPPORT_TREE_SHA256
            and report.get("captured_official_stderr") == "",
            "an authentic full original Python worker was changed: " + label,
        )
        locale_report = report.get("locale")
        require(
            isinstance(locale_report, dict)
            and locale_report.get("fresh_private_localedef") is True
            and locale_report.get("iso_8859_1_passed") is True
            and locale_report.get("utf_8_passed") is True,
            "the genuine original two fresh private locales were not passed",
        )
        resources = report.get("resource_provenance")
        require(
            isinstance(resources, dict)
            and type(resources.get("real_max_memuse")) is int
            and resources["real_max_memuse"] >= 18 * 2**31
            and resources.get("large_method_sizes") == {
                "ReTests.test_large_search": 2**31,
                "ReTests.test_large_subn": 2**31,
            }
            and resources.get("cpu_resource_enabled") is True
            and resources.get("multiprocessing_extension_available") is True
            and resources.get("multiprocessing_start_method") == "fork"
            and resources.get("actual_upstream_corpus_cases") == 403
            and resources.get("actual_external_fixture_assertion_cases") == 11
            and resources.get("exclusive_big_memory_worker") is True
            and resources.get("official_support_shim_used") is False
            and resources.get("official_test_source_rewritten") is False,
            "a genuine original upstream fixture or resource was fabricated",
        )
        _validate_original_v5_resources(report, records)
        vectors.append(vector)
    require(vectors[0] == vectors[1],
            "the actual independent original Python reference vectors disagree")
    require(document.get("reference_status_vector_sha256") == digest(vectors[0]),
            "the original independent Python status-vector digest changed")
    return {"reference_sha256": actual_payload_sha256, "vector": vectors[0]}


def _require_frozen_matrix() -> None:
    require(valid_sha256(MATRIX_SHA256) and valid_sha256(STIMULUS_SHA256),
            "BLOCKED: independently freeze both actual V17 matrix digests first")


def authenticate_reference(
    source_sha256: str,
    protocol_sha256: str,
) -> dict[str, Any]:
    verify_runtime()
    _require_frozen_matrix()
    _read_bounded(SOURCE_RELATIVE, MAX_SOURCE_BYTES, expected=source_sha256)
    _read_bounded(PROTOCOL_RELATIVE, MAX_SOURCE_BYTES, expected=protocol_sha256)
    _read_bounded(V5_SOURCE_RELATIVE, MAX_SOURCE_BYTES, expected=V5_SOURCE_SHA256)
    _read_bounded(
        V5_PROTOCOL_RELATIVE, MAX_SOURCE_BYTES, expected=V5_PROTOCOL_SHA256,
    )
    original = _read_bounded(
        ORIGINAL_SOURCE_RELATIVE, MAX_SOURCE_BYTES, expected=ORIGINAL_SOURCE_SHA256,
    )
    original_matrix = _original_matrix(original)["matrix"]
    payload = _read_bounded(
        V5_REFERENCE_RELATIVE, MAX_EVIDENCE_BYTES, expected=V5_REFERENCE_SHA256,
    )
    document = _strict_json(payload, V5_REFERENCE_RELATIVE)
    reference = validate_v5_reference(
        document, original_matrix,
        actual_payload_sha256=hashlib.sha256(payload).hexdigest(),
    )
    return {
        "source_sha256": source_sha256,
        "protocol_sha256": protocol_sha256,
        "v5_reference_sha256": reference["reference_sha256"],
        "original_matrix_sha256": ORIGINAL_MATRIX_SHA256,
        "original_public_methods": 152,
        "original_passed": 151,
        "original_named_private_skips": 1,
        "candidate_audits_read": 0,
        "candidate_proofs_read": 0,
        "candidate_imports": 0,
        "performance": "NOT MEASURED",
    }


def _proof_pin_values(values: Mapping[str, Any]) -> dict[str, str]:
    required: dict[str, Any] = {
        "v10_base_report": values.get("v10_base_report"),
        "v10_strict_report": values.get("v10_strict_report"),
        **{
            family + "_" + kind: values.get(family + "_" + kind)
            for family in FAMILIES
            for kind in ("edge", "deep")
        },
    }
    require(
        all(valid_sha256(value) for value in required.values())
        and len(set(required.values())) == len(required),
        "BLOCKED: publish the two actual V10 audit hashes and all six distinct "
        "real current-family V10 qualified edge/deep archive hashes first",
    )
    return {name: str(value) for name, value in required.items()}


def authenticate_candidate(
    reference: Mapping[str, Any],
    values: Mapping[str, Any],
) -> dict[str, Any]:
    require(
        reference.get("v5_reference_sha256") == V5_REFERENCE_SHA256
        and reference.get("candidate_audits_read") == 0
        and reference.get("candidate_proofs_read") == 0
        and reference.get("candidate_imports") == 0,
        "authenticate the actual candidate-free V5 baseline before any V10 audit",
    )
    pins = _proof_pin_values(values)
    exact_sources = (
        (V10_BASE_SOURCE_RELATIVE, V10_BASE_SOURCE_SHA256),
        (V10_STRICT_SOURCE_RELATIVE, V10_STRICT_SOURCE_SHA256),
        (V10_OWNERSHIP_PROTOCOL_RELATIVE, V10_OWNERSHIP_PROTOCOL_SHA256),
        (V10_PROOF_SOURCE_RELATIVE, V10_PROOF_SOURCE_SHA256),
        (V10_PROOF_PROTOCOL_RELATIVE, V10_PROOF_PROTOCOL_SHA256),
    )
    for relative, expected in exact_sources:
        require(valid_sha256(expected),
                "BLOCKED: independently freeze the actual reviewed V10 source: "
                + relative)
        _read_bounded(relative, MAX_SOURCE_BYTES, expected=str(expected))
    require(
        not any(name == "candidates" or name.startswith("candidates.")
                for name in sys.modules),
        "no candidate may be imported while authenticating actual V10 proofs",
    )
    original_path = list(sys.path)
    try:
        if not sys.path or sys.path[0] != str(ROOT):
            sys.path.insert(0, str(ROOT))
        owner = importlib.import_module("tools.postfinal_from_scratch_audit_v10")
        strict = importlib.import_module("tools.postfinal_no_delegation_audit_v10")
        proof = importlib.import_module("tools.postfinal_current_build_proofs_v10")
        for module, relative in (
            (owner, V10_BASE_SOURCE_RELATIVE),
            (strict, V10_STRICT_SOURCE_RELATIVE),
            (proof, V10_PROOF_SOURCE_RELATIVE),
        ):
            require(
                os.path.abspath(module.__file__) == str(ROOT / relative),
                "an exact authenticated V10 validator was substituted: " + relative,
            )
        require(
            strict.independent is owner
            and proof.V10_BASE_SOURCE_SHA256 == V10_BASE_SOURCE_SHA256
            and proof.V10_STRICT_SOURCE_SHA256 == V10_STRICT_SOURCE_SHA256
            and proof.V10_OWNERSHIP_PROTOCOL_SHA256
            == V10_OWNERSHIP_PROTOCOL_SHA256
            and proof.REFRESH_PROTOCOL_SHA256 == V10_PROOF_PROTOCOL_SHA256
            and proof.BASELINE_SHA256 == V5_REFERENCE_SHA256
            and tuple(proof.FAMILIES) == FAMILIES,
            "an actual current-build V10 audit dependency was substituted",
        )
        proof_pins = proof.validated_report_pins(
            True, pins["v10_base_report"], pins["v10_strict_report"],
        )
        require(
            isinstance(proof_pins, dict)
            and proof_pins.get("base_source") == V10_BASE_SOURCE_SHA256
            and proof_pins.get("strict_source") == V10_STRICT_SOURCE_SHA256,
            "the exact genuine all-family V10 audit pins were weakened",
        )
        audits = proof.audit_v10_reports(owner, strict, proof_pins)
        require(
            isinstance(audits, dict)
            and isinstance(audits.get("graph"), dict)
            and audits["graph"].get("source_count") == 12
            and audits["graph"].get("native_binary_count") == 5,
            "the original full V10 all-family validator rejected a real audit",
        )
        v8 = proof.import_frozen(
            "tools.postfinal_current_build_proofs_v8",
            proof.V8_PROOF_RELATIVE,
            proof.V8_PROOF_SHA256,
        )
        contract = v8.load_contract()
        archives: dict[str, dict[str, str]] = {}
        for family in FAMILIES:
            snapshot = proof.snapshot_family(family)
            require(
                snapshot["native_sha256_by_path"]
                == audits["graph"]["native_sha256_by_family"][family],
                "the real audited native family changed before proof validation: "
                + family,
            )
            edge = _read_bounded(
                V10_EDGE_RELATIVES[family], MAX_COMPRESSED_PROOF_BYTES,
                expected=pins[family + "_edge"],
            )
            edge_document, edge_proof, edge_passed = v8.validate_original_edge(
                edge,
                ROOT / V10_EDGE_RELATIVES[family],
                family,
                snapshot,
                contract,
            )
            require(
                isinstance(edge_document, dict)
                and isinstance(edge_proof, dict)
                and edge_passed is True
                and edge_proof.get("failed") == 0
                and edge_proof.get("checks") == proof.EDGE_CHECKS
                and edge_proof.get("category_count") == proof.EDGE_CATEGORIES,
                "the complete original all-case V10 edge proof failed: " + family,
            )
            deep = _read_bounded(
                V10_DEEP_RELATIVES[family], MAX_COMPRESSED_PROOF_BYTES,
                expected=pins[family + "_deep"],
            )
            deep_document, deep_passed = v8.validate_deep(
                deep,
                family,
                edge_proof,
                snapshot,
                contract,
            )
            require(
                isinstance(deep_document, dict)
                and deep_passed is True
                and deep_document.get("public_mismatch_count") == 0,
                "the complete original current-family deep proof failed: " + family,
            )
            archives[family] = {
                "edge_path": V10_EDGE_RELATIVES[family],
                "edge_sha256": pins[family + "_edge"],
                "deep_path": V10_DEEP_RELATIVES[family],
                "deep_sha256": pins[family + "_deep"],
            }
        require(
            not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "an actual V10 proof validator imported an unguarded candidate",
        )
        # A complete original-suite archive does not retain the actual V10
        # owner observations before and after its producer. Wait for a genuine
        # durable V11 proof and an authenticated public-worker guard. Neither
        # a gzip header nor an audit reporting PASS can fill that gap.
        require(
            False,
            "BLOCKED: the complete V10 audits and original-suite archives do "
            "not publish durable per-family guarded owner-before/after "
            "proof; authenticate an actual V11 durable proof and a safe "
            "public-worker guard before importing any candidate",
        )
        return {"audit_pins": pins, "validated_original_archives": archives}
    finally:
        sys.path[:] = original_path


def validate_records(records: Any, matrix: list[dict[str, Any]]) -> str:
    require(isinstance(records, list) and len(records) == EXPECTED_CASES,
            "all actual independently observed public cases must be retained")
    actual_additional = 0
    actual_locales = 0
    for expected, record in zip(matrix, records, strict=True):
        stimulus = build_stimulus(expected)
        require(
            isinstance(record, dict)
            and set(record) == {"id", "cohort", "stimulus_sha256", "outcome"}
            and record.get("id") == expected["id"]
            and record.get("cohort") == expected["cohort"]
            and record.get("stimulus_sha256") == digest(stimulus)
            and isinstance(record.get("outcome"), dict)
            and record["outcome"].get("status") in {"return", "raise"}
            and (
                (record["outcome"]["status"] == "return"
                 and set(record["outcome"]) == {"status", "value"})
                or (record["outcome"]["status"] == "raise"
                    and set(record["outcome"]) == {"status", "exception"})
            ),
            "a real public case or original exception was omitted or forged",
        )
        if expected["cohort"] in ADDITIONAL_COHORTS:
            require(
                record["outcome"]["status"] == "return",
                "an additional public infrastructure or probe failure "
                "cannot qualify as a matching exception",
            )
            actual_additional += 1
        if expected["cohort"] in {
            "real-locale-switch-on-compiled-bytes",
            "real-locale-invalid-flags-and-cache",
        }:
            _validate_locale_case(record)
            actual_locales += 1
    require(
        actual_additional == EXPECTED_ADDITIONAL_CASES
        and actual_locales == 2 * CASES_PER_COHORT,
        "all 736 successful additive cases and 64 genuine locale cases "
        "must be individually retained",
    )
    return digest(records)


def _safe_output(relative: str) -> Path:
    return ROOT / _safe_relative(relative, approved=APPROVED_OUTPUTS)


def _preflight_outputs(relatives: tuple[str, ...]) -> None:
    require(len(relatives) == len(set(relatives)),
            "independent genuine outcomes cannot share an evidence destination")
    for relative in relatives:
        path = _safe_output(relative)
        require(
            path.parent.is_dir()
            and not path.parent.is_symlink()
            and path.resolve(strict=False) == path
            and not path.exists()
            and not path.is_symlink(),
            "refusing to replace, retry, or redirect an existing real result: "
            + relative,
        )


def _exclusive_write(document: Mapping[str, Any], relative: str) -> str:
    path = _safe_output(relative)
    payload = canonical(document) + b"\n"
    require(0 < len(payload) <= MAX_EVIDENCE_BYTES,
            "an actual complete public report exceeds the frozen bound")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, 0o600)
    except OSError as error:
        raise PublicSurfaceError(
            "refusing to overwrite an existing real public result: " + relative,
        ) from error
    try:
        remaining = memoryview(payload)
        while remaining:
            written = os.write(descriptor, remaining)
            require(written > 0, "the genuine public evidence was truncated")
            remaining = remaining[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    directory_flags |= getattr(os, "O_CLOEXEC", 0)
    directory = os.open(path.parent, directory_flags)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    return hashlib.sha256(payload).hexdigest()


@contextlib.contextmanager
def _source_only_effects() -> Iterator[dict[str, int]]:
    counts = {
        "files_read": 0,
        "files_written": 0,
        "processes": 0,
        "threads": 0,
        "clock_samples": 0,
        "entropy_draws": 0,
        "locale_changes": 0,
        "candidate_imports": 0,
        "regex_matches": 0,
    }
    saved: list[tuple[Any, str, Any]] = []

    def install(target: Any, name: str, replacement: Any) -> None:
        if hasattr(target, name):
            original = getattr(target, name)
            saved.append((target, name, original))
            setattr(target, name, replacement)

    def blocker(kind: str) -> Callable[..., Any]:
        def blocked(*_args: Any, **_kwargs: Any) -> Any:
            counts[kind] += 1
            raise PublicSurfaceError("a source-only control attempted " + kind)
        return blocked

    real_import = builtins.__import__
    real_import_module = importlib.import_module

    def checked_import(
        name: str,
        globals: Any = None,
        locals: Any = None,
        fromlist: Any = (),
        level: int = 0,
    ) -> Any:
        if name == "candidates" or name.startswith("candidates."):
            counts["candidate_imports"] += 1
            raise PublicSurfaceError("a source-only control imported a candidate")
        return real_import(name, globals, locals, fromlist, level)

    def checked_import_module(name: str, package: str | None = None) -> Any:
        if name == "candidates" or name.startswith("candidates."):
            counts["candidate_imports"] += 1
            raise PublicSurfaceError("a source-only control imported a candidate")
        return real_import_module(name, package)

    try:
        install(builtins, "open", blocker("files_read"))
        install(io, "open", blocker("files_read"))
        install(os, "open", blocker("files_read"))
        install(os, "read", blocker("files_read"))
        install(os, "write", blocker("files_written"))
        install(os, "fsync", blocker("files_written"))
        install(os, "system", blocker("processes"))
        install(os, "popen", blocker("processes"))
        install(os, "fork", blocker("processes"))
        install(os, "posix_spawn", blocker("processes"))
        install(os, "urandom", blocker("entropy_draws"))
        install(os, "getrandom", blocker("entropy_draws"))
        install(subprocess, "run", blocker("processes"))
        install(subprocess, "Popen", blocker("processes"))
        install(threading.Thread, "start", blocker("threads"))
        install(locale, "setlocale", blocker("locale_changes"))
        loaded_regex = sys.modules.get("re")
        if isinstance(loaded_regex, types.ModuleType):
            for name in (
                "compile", "match", "fullmatch", "search", "sub", "subn",
                "split", "findall", "finditer", "purge",
            ):
                install(loaded_regex, name, blocker("regex_matches"))
        loaded_engine = sys.modules.get("_sre")
        if isinstance(loaded_engine, types.ModuleType):
            install(loaded_engine, "compile", blocker("regex_matches"))
        for name in (
            "time", "time_ns", "monotonic", "monotonic_ns",
            "perf_counter", "perf_counter_ns", "process_time", "thread_time",
        ):
            install(time, name, blocker("clock_samples"))
        install(builtins, "__import__", checked_import)
        install(importlib, "import_module", checked_import_module)
        yield counts
    finally:
        for target, name, original in reversed(saved):
            setattr(target, name, original)


def self_test() -> dict[str, Any]:
    verify_runtime()
    require(
        not any(name == "candidates" or name.startswith("candidates.")
                for name in sys.modules),
        "source-only controls cannot begin with a preloaded candidate",
    )
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: Any) -> None:
        require(not any(row["name"] == name for row in checks),
                "a distinct source-only poison control was counted twice")
        checks.append({"name": name, "passed": bool(condition)})

    def reject(name: str, action: Callable[[], Any]) -> None:
        try:
            action()
        except (PublicSurfaceError, ValueError, TypeError, KeyError):
            check(name, True)
        else:
            check(name, False)

    with _source_only_effects() as effects:
        matrix = build_matrix()
        matrix_hash = validate_matrix(matrix, expected_sha256=MATRIX_SHA256)
        semantic = validate_stimuli(matrix, expected_sha256=STIMULUS_SHA256)
        check("independently-regenerate-all-source-local-base-cases",
              len(matrix[:EXPECTED_BASE_CASES]) == 640)
        check("recompute-original-source-local-case-identity-digest",
              digest(matrix[:EXPECTED_BASE_CASES]) == BASE_MATRIX_SHA256)
        check("recompute-original-source-local-real-stimulus-digest",
              digest([build_stimulus(row)
                      for row in matrix[:EXPECTED_BASE_CASES]])
              == BASE_STIMULUS_SHA256)
        check("retain-distinct-additional-seed-domain",
              BASE_DOMAIN != ADDITIONAL_DOMAIN and BASE_SEED != ADDITIONAL_SEED)
        check("derive-exact-case-denominator-from-real-source-rows",
              semantic["cases"] == len(matrix) == EXPECTED_CASES)
        check("each-source-input-is-a-distinct-real-behavioral-stimulus",
              semantic["distinct_stimuli"] == EXPECTED_CASES)
        check("retain-exact-31-ordered-python-public-exports",
              len(PUBLIC_EXPORTS) == 31 and len(set(PUBLIC_EXPORTS)) == 31)
        check("keep-scanner-public-but-outside-all",
              "Scanner" not in PUBLIC_EXPORTS)
        check("keep-debug-public-but-outside-all",
              "DEBUG" not in PUBLIC_EXPORTS)
        check("retain-all-13-pattern-and-14-match-members",
              len(PUBLIC_PATTERN_MEMBERS) == 13 and len(PUBLIC_MATCH_MEMBERS) == 14)
        check("pin-real-complete-two-reference-v5-without-candidate-audits",
              valid_sha256(V5_REFERENCE_SHA256)
              and V5_REFERENCE_RELATIVE.endswith("v5-self-oracle.json"))
        check("retain-exact-genuine-original-152-source-matrix",
              valid_sha256(ORIGINAL_MATRIX_SHA256))
        check("retain-only-the-real-debug-conditioned-original-skip",
              PRIVATE_CONDITIONAL_METHOD == "ReTests.test_memory_leaks")
        check("candidate-proof-names-are-not-reference-prerequisites",
              "candidate" not in V5_REFERENCE_RELATIVE
              and "audit" not in V5_REFERENCE_RELATIVE)
        check("never-invent-an-all-family-v10-proof-manifest",
              len(V10_EDGE_RELATIVES) == 3 and len(V10_DEEP_RELATIVES) == 3)

        for index, cohort in enumerate(COHORTS):
            cohort_rows = [row for row in matrix if row["cohort"] == cohort]
            check(
                "retain-32-actual-stimuli-" + cohort,
                len(cohort_rows) == CASES_PER_COHORT
                and len({digest(build_stimulus(row)) for row in cohort_rows})
                == CASES_PER_COHORT,
            )
            check(
                "actual-variant-changes-expression-and-subject-" + cohort,
                len({build_stimulus(row)["expression"] for row in cohort_rows})
                == CASES_PER_COHORT
                and len({build_stimulus(row)["subject"] for row in cohort_rows})
                == CASES_PER_COHORT,
            )
            chosen = matrix[index * CASES_PER_COHORT]
            check(
                "seed-reproduces-cohort-" + cohort,
                chosen["cohort"] == cohort
                and chosen["index"] == 0,
            )

        for symbol in PUBLIC_EXPORTS:
            check("freeze-exact-public-export-" + symbol,
                  PUBLIC_EXPORTS.count(symbol) == 1)
        for member in PUBLIC_PATTERN_MEMBERS:
            check("freeze-exact-public-pattern-member-" + member,
                  PUBLIC_PATTERN_MEMBERS.count(member) == 1)
        for member in PUBLIC_MATCH_MEMBERS:
            check("freeze-exact-public-match-member-" + member,
                  PUBLIC_MATCH_MEMBERS.count(member) == 1)
        for left, right in PUBLIC_ALIASES:
            check("freeze-genuine-public-alias-" + left + "-" + right,
                  left in PUBLIC_EXPORTS and right in PUBLIC_EXPORTS)

        poison_positions = (
            0, 1, 15, 31, 32, 63, 127, 255, 511, 639,
            EXPECTED_BASE_CASES, EXPECTED_CASES - 2, EXPECTED_CASES - 1,
        )
        for position in poison_positions:
            forged = copy.deepcopy(matrix)
            forged[position]["variant"] ^= 1
            reject("reject-real-variant-substitution-" + str(position),
                   lambda forged=forged: validate_matrix(forged))
        for position in (0, 31, 639, EXPECTED_BASE_CASES, EXPECTED_CASES - 1):
            forged = copy.deepcopy(matrix)
            forged[position]["id"] += ".forged"
            reject("reject-real-case-identity-substitution-" + str(position),
                   lambda forged=forged: validate_matrix(forged))
        for position in (0, 31, 639, EXPECTED_BASE_CASES, EXPECTED_CASES - 1):
            probes = [build_stimulus(row) for row in matrix]
            probes[position]["subject"] += "-forged"
            reject("reject-real-matching-input-substitution-" + str(position),
                   lambda probes=probes: validate_stimuli(matrix, observed=probes))
        for label, forged in (
            ("removed-row", matrix[:-1]),
            ("duplicated-row", matrix + [matrix[0]]),
            ("reversed-rows", list(reversed(matrix))),
        ):
            reject("reject-" + label,
                   lambda forged=forged: validate_matrix(forged))
        for name, value in (
            ("empty", ""), ("short", "a" * 63), ("long", "a" * 65),
            ("uppercase", "A" * 64), ("nonhex", "g" * 64),
            ("integer", 0), ("none", None), ("bytes", b"a" * 64),
        ):
            check("reject-invalid-frozen-sha256-" + name, not valid_sha256(value))
        for name, value in (
            ("absolute", "/tmp/forged.json"),
            ("parent", "../forged.json"),
            ("nested-parent", "candidates/../forged.json"),
            ("backslash", "candidates\\forged.json"),
            ("nul", "candidates/forged\x00.json"),
            ("unknown", "candidates/evidence/not-allowlisted.json"),
        ):
            reject("reject-unsafe-exclusive-output-" + name,
                   lambda value=value: _safe_relative(
                       value, approved=APPROVED_OUTPUTS,
                   ))
        for relative in sorted(APPROVED_OUTPUTS):
            check("allow-only-exact-output-" + relative.rsplit("/", 1)[-1],
                  _safe_relative(relative, approved=APPROVED_OUTPUTS) == relative)
        check("keep-reference-success-and-failure-destinations-distinct",
              SELF_ORACLE_RELATIVE != SELF_ORACLE_FAILURE_RELATIVE)
        check("keep-all-three-real-candidate-failures-separate",
              len(set(CANDIDATE_FAILURE_RELATIVES.values())) == 3)
        for family in FAMILIES:
            check("pin-exact-qualified-edge-path-" + family,
                  V10_EDGE_RELATIVES[family].endswith(
                      "-v10-qualified-pass.json.gz",
                  ))
            check("pin-exact-qualified-deep-path-" + family,
                  V10_DEEP_RELATIVES[family].endswith(
                      "-POSTFINAL-CURRENT-BUILD-V10-PASS.json.gz",
                  ))
        for missing in (
            "v10_base_report", "v10_strict_report",
            "rust_edge", "rust_deep", "vm_edge", "vm_deep",
            "zig_edge", "zig_deep",
        ):
            synthetic = {
                "v10_base_report": "1" * 64,
                "v10_strict_report": "2" * 64,
                "rust_edge": "3" * 64,
                "rust_deep": "4" * 64,
                "vm_edge": "5" * 64,
                "vm_deep": "6" * 64,
                "zig_edge": "7" * 64,
                "zig_deep": "8" * 64,
            }
            synthetic.pop(missing)
            reject("reject-missing-real-v10-proof-pin-" + missing,
                   lambda synthetic=synthetic: _proof_pin_values(synthetic))
        duplicated = {
            "v10_base_report": "1" * 64,
            "v10_strict_report": "1" * 64,
            **{family + "_" + kind: str(position + 2) * 64
               for position, (family, kind) in enumerate(
                   (family, kind)
                   for family in FAMILIES
                   for kind in ("edge", "deep")
               )},
        }
        reject("reject-reused-actual-v10-proof-or-audit-hash",
               lambda: _proof_pin_values(duplicated))
        reject("reject-synthetic-reference-as-published-v5",
               lambda: validate_v5_reference({}, [], actual_payload_sha256="0" * 64))
        reject("reject-absent-original-public-source-matrix",
               lambda: _v5_vector([], []))
        synthetic_special_methods = {
            10: "ReTests.test_large_search",
            11: "ReTests.test_large_subn",
            12: "ReTests.test_search_anchor_at_beginning",
            13: "ReTests.test_regression_gh94675",
            73: PRIVATE_CONDITIONAL_METHOD,
        }
        synthetic_matrix = [
            {
                "test": synthetic_special_methods.get(
                    index, "ReTests.test_source_only_v17_" + str(index),
                ),
                "source_ast_sha256": hashlib.sha256(
                    ("source-only-v17-original-method:" + str(index)).encode("ascii"),
                ).hexdigest(),
            }
            for index in range(152)
        ]
        synthetic_records = [
            {
                "test": row["test"],
                "source_ast_sha256": row["source_ast_sha256"],
                "status": "PASS",
            }
            for row in synthetic_matrix
        ]
        synthetic_records[73].update({
            "status": "SKIP",
            "reason": "requires debug build",
            "skip_kind": "named-private-debug-condition",
        })
        vector = _v5_vector(synthetic_records, synthetic_matrix)
        check("validate-all-152-source-only-synthetic-original-identities",
              len(vector) == 152)
        check("derive-exact-151-applicable-synthetic-original-passes",
              sum(row["status"] == "PASS" for row in vector) == 151)
        check("derive-only-real-named-private-debug-skip-shape",
              sum(row["status"] == "SKIP" for row in vector) == 1
              and vector[73]["test"] == PRIVATE_CONDITIONAL_METHOD)
        check("retain-exact-real-v5-five-field-status-vector-shape",
              all(set(row) == {
                  "test", "source_ast_sha256", "status", "reason", "skip_kind",
              } for row in vector))
        for label, change in (
            ("missing-original-source-record", lambda rows: rows.pop()),
            ("reordered-original-source-record", lambda rows: rows.reverse()),
            ("false-original-public-skip", lambda rows: rows[0].update(
                status="SKIP",
            )),
            ("failed-original-public-case", lambda rows: rows[0].update(
                status="FAIL",
            )),
            ("changed-original-ast", lambda rows: rows[0].update(
                source_ast_sha256="0" * 64,
            )),
            ("missing-genuine-debug-skip", lambda rows: rows[73].update(
                status="PASS",
            )),
            ("forged-private-skip-reason", lambda rows: rows[73].update(
                reason="synthetic exception",
            )),
            ("forged-private-skip-scope", lambda rows: rows[73].update(
                skip_kind="public-waiver",
            )),
        ):
            forged = copy.deepcopy(synthetic_records)
            change(forged)
            reject("reject-" + label,
                   lambda forged=forged: _v5_vector(forged, synthetic_matrix))

        for position in (10, 11):
            synthetic_records[position]["resource"] = {
                "declared_size": 2**31,
                "delivered_size": 2**31,
                "real_max_memuse": 40 * 1024**3,
                "dry_run": False,
            }
        synthetic_records[12]["resource"] = {
            "cpu_resource_enabled": True,
            "subject_characters": 10_000_000,
            "original_upper_bound_seconds": 0.1,
            "original_stopwatch_assertion_passed": True,
        }
        synthetic_records[13]["resource"] = {
            "process_started": True,
            "start_method": "fork",
            "short_timeout_seconds": 30.0,
        }
        synthetic_role = {
            "guard": {
                "passed": True,
                "candidate_isolation": True,
                "baseline_only": True,
            },
            "live_official_fixture_provenance": {
                "actual_upstream_corpus_cases": 403,
                "actual_external_fixture_assertion_cases": 11,
                "support_tree_sha256": ORIGINAL_SUPPORT_TREE_SHA256,
                "official_support_shim_used": False,
                "modules": {
                    "test.support": {"sha256": "a" * 64},
                    "test.support.warnings_helper": {"sha256": "b" * 64},
                    "test.re_tests": {"sha256": ORIGINAL_CORPUS_SHA256},
                },
            },
        }
        check("validate-complete-source-only-original-resource-record-shapes",
              _validate_original_v5_resources(synthetic_role, synthetic_records)
              is None)
        for label, position, field, value in (
            ("dry-run-two-gibibyte-search", 10, "dry_run", True),
            ("undersized-two-gibibyte-search", 10, "delivered_size", 5147),
            ("undersized-two-gibibyte-subn", 11, "declared_size", 5147),
            ("missing-original-36-gibibyte-memory", 11, "real_max_memuse", 1),
            ("disabled-original-cpu-resource", 12, "cpu_resource_enabled", False),
            ("shortened-original-ten-million-subject", 12, "subject_characters", 1),
            ("changed-original-stopwatch-bound", 12,
             "original_upper_bound_seconds", 1.0),
            ("failed-original-stopwatch-assertion", 12,
             "original_stopwatch_assertion_passed", False),
            ("unstarted-original-fork", 13, "process_started", False),
            ("substituted-original-fork", 13, "start_method", "spawn"),
            ("changed-original-fork-timeout", 13, "short_timeout_seconds", 1.0),
        ):
            changed_records = copy.deepcopy(synthetic_records)
            changed_records[position]["resource"][field] = value
            reject("reject-" + label,
                   lambda changed_records=changed_records:
                   _validate_original_v5_resources(synthetic_role, changed_records))
        for label, change in (
            ("fabricated-live-upstream-support-shim", lambda role: role[
                "live_official_fixture_provenance"
            ].update(official_support_shim_used=True)),
            ("missing-original-403-entry-corpus", lambda role: role[
                "live_official_fixture_provenance"
            ].update(actual_upstream_corpus_cases=402)),
            ("missing-original-11-external-fixtures", lambda role: role[
                "live_official_fixture_provenance"
            ].update(actual_external_fixture_assertion_cases=10)),
            ("forged-genuine-live-corpus-module", lambda role: role[
                "live_official_fixture_provenance"
            ]["modules"]["test.re_tests"].update(sha256="0" * 64)),
            ("candidate-import-in-original-python-reference", lambda role: role[
                "guard"
            ].update(baseline_only=False)),
            ("failed-original-python-isolation-guard", lambda role: role[
                "guard"
            ].update(passed=False)),
        ):
            changed_role = copy.deepcopy(synthetic_role)
            change(changed_role)
            reject("reject-" + label,
                   lambda changed_role=changed_role:
                   _validate_original_v5_resources(changed_role, synthetic_records))

        synthetic_transitions = [
            {
                "locale": "iso8859_1",
                "codeset": "iso88591",
                "same_compiled_pattern": True,
                "high_byte": {"genuine": True},
                "ascii_byte": {"genuine": True},
                "scanner": {"genuine": True},
            },
            {
                "locale": "utf8",
                "codeset": "utf8",
                "same_compiled_pattern": True,
                "high_byte": None,
                "ascii_byte": {"genuine": True},
                "scanner": None,
            },
            {
                "locale": "iso8859_1_again",
                "codeset": "iso88591",
                "same_compiled_pattern": True,
                "high_byte": {"genuine": True},
                "ascii_byte": {"genuine": True},
                "scanner": {"genuine": True},
            },
        ]
        synthetic_locale_value = {
            "transitions": synthetic_transitions,
            "purge_recreates": True,
            "purge_match": {"genuine": True},
            "locale_with_text": {"status": "raise", "exception": {}},
            "locale_with_ascii": {"status": "raise", "exception": {}},
        }
        synthetic_locale = {
            "cohort": "real-locale-switch-on-compiled-bytes",
            "outcome": {
                "status": "return",
                "value": normalize(synthetic_locale_value),
            },
        }
        check("validate-all-three-source-only-locale-transition-shapes",
              _validate_locale_case(synthetic_locale) is None)
        for label, change in (
            ("locale-reported-as-matching-exception", lambda row: row.update(
                outcome={"status": "raise", "exception": {"type": "locale.Error"}},
            )),
            ("missing-actual-locale-transition", lambda row: row[
                "outcome"
            ]["value"]["items"].pop()),
            ("unknown-locale-cohort", lambda row: row.update(
                cohort="fake-locale",
            )),
        ):
            forged_locale = copy.deepcopy(synthetic_locale)
            change(forged_locale)
            reject("reject-" + label,
                   lambda forged_locale=forged_locale:
                   _validate_locale_case(forged_locale))
        for label, transition, field, value in (
            ("wrong-iso-codeset", 0, "codeset", "utf8"),
            ("wrong-utf8-codeset", 1, "codeset", "iso88591"),
            ("wrong-returned-iso-codeset", 2, "codeset", "utf8"),
            ("different-compiled-locale-pattern", 0, "same_compiled_pattern", False),
            ("missing-real-iso-high-byte-match", 0, "high_byte", None),
            ("fabricated-utf8-high-byte-match", 1, "high_byte", {"genuine": True}),
            ("missing-real-iso-scanner-match", 2, "scanner", None),
            ("missing-real-locale-ascii-match", 1, "ascii_byte", None),
        ):
            changed_value = copy.deepcopy(synthetic_locale_value)
            changed_value["transitions"][transition][field] = value
            forged_locale = {
                "cohort": "real-locale-switch-on-compiled-bytes",
                "outcome": {
                    "status": "return", "value": normalize(changed_value),
                },
            }
            reject("reject-" + label,
                   lambda forged_locale=forged_locale:
                   _validate_locale_case(forged_locale))
        check("preserve-exact-bytes-without-text-loss",
              normalize(b"\x00\xff") == {"kind": "bytes", "hex": "00ff"})
        check("distinguish-real-bytearray-from-bytes",
              normalize(bytearray(b"x")) != normalize(b"x"))
        check("distinguish-real-tuple-from-list",
              normalize((1,)) != normalize([1]))
        check("canonical-mapping-order-is-deterministic",
              normalize({"b": 2, "a": 1}) == normalize({"a": 1, "b": 2}))
        observed_error = observe(lambda: (_ for _ in ()).throw(ValueError("real")))
        check("preserve-real-public-exception-type",
              observed_error["exception"]["type"] == "ValueError")
        check("preserve-real-public-exception-message",
              observed_error["exception"]["message"] == "real")
        capability = _subinterpreter_capability(
            build_stimulus(matrix[-1]),
        )
        check("never-invent-a-safe-fresh-interpreter-guard",
              capability["status"] == "NOT RUN")
        check("never-start-an-unguarded-fresh-interpreter",
              capability["subinterpreter_started"] is False)
        check("never-import-a-candidate-for-interpreter-capability",
              capability["candidate_imported"] is False)
        check("do-not-import-preexisting-or-current-candidates",
              not any(name == "candidates" or name.startswith("candidates.")
                      for name in sys.modules))

    for label, counter in (
        ("read-zero-source-fixtures-evidence-or-holdout-files", "files_read"),
        ("write-zero-reports-case-files-or-bytecode", "files_written"),
        ("start-zero-reference-or-candidate-workers", "processes"),
        ("start-zero-correctness-or-subinterpreter-threads", "threads"),
        ("sample-zero-performance-or-correctness-clocks", "clock_samples"),
        ("draw-zero-production-entropy", "entropy_draws"),
        ("make-zero-process-global-locale-changes", "locale_changes"),
        ("import-zero-independent-engine-candidates", "candidate_imports"),
        ("execute-zero-standard-library-regex-matching-calls", "regex_matches"),
    ):
        check(label, effects[counter] == 0)
    failed = [entry["name"] for entry in checks if not entry["passed"]]
    require(not failed, "a real source-only poison control failed: " + ", ".join(failed))
    require(len(checks) >= 150,
            "at least 150 distinct genuine source-only controls are required")
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS",
        "result": "PASS",
        "check_count": len(checks),
        "failed": [],
        "python": "3.14.6",
        "source_path": SOURCE_RELATIVE,
        "protocol_path": PROTOCOL_RELATIVE,
        "base_seed": BASE_SEED,
        "base_seed_domain": BASE_DOMAIN,
        "additional_seed": ADDITIONAL_SEED,
        "additional_seed_domain": ADDITIONAL_DOMAIN,
        "cohorts": semantic["cohorts"],
        "cohort_cases": semantic["cohort_cases"],
        "cases": semantic["cases"],
        "source_local_base_cases": semantic["base_cases"],
        "additional_cases": semantic["additional_cases"],
        "distinct_behavioral_stimuli": semantic["distinct_stimuli"],
        "base_matrix_sha256": BASE_MATRIX_SHA256,
        "base_stimulus_sha256": BASE_STIMULUS_SHA256,
        "matrix_sha256": matrix_hash,
        "matrix_frozen": MATRIX_SHA256 is not None,
        "stimulus_sha256": semantic["stimulus_sha256"],
        "stimuli_frozen": STIMULUS_SHA256 is not None,
        "public_exports": len(PUBLIC_EXPORTS),
        "public_pattern_members": len(PUBLIC_PATTERN_MEMBERS),
        "public_match_members": len(PUBLIC_MATCH_MEMBERS),
        "original_public_methods": 152,
        "original_applicable_methods": 151,
        "original_named_private_debug_skips": 1,
        "original_public_method_waivers": 0,
        "published_v5_reference_sha256": V5_REFERENCE_SHA256,
        "v10_sources_pinned": all(valid_sha256(value) for value in (
            V10_BASE_SOURCE_SHA256,
            V10_STRICT_SOURCE_SHA256,
            V10_OWNERSHIP_PROTOCOL_SHA256,
            V10_PROOF_SOURCE_SHA256,
            V10_PROOF_PROTOCOL_SHA256,
        )),
        "candidate_imports": effects["candidate_imports"],
        "reference_workers": 0,
        "candidate_workers": 0,
        "subprocesses": effects["processes"],
        "threads_started": effects["threads"],
        "source_files_read": effects["files_read"],
        "case_files_read": effects["files_read"],
        "evidence_files_read": effects["files_read"],
        "files_written": effects["files_written"],
        "clock_samples": effects["clock_samples"],
        "entropy_draws": effects["entropy_draws"],
        "locale_changes": effects["locale_changes"],
        "regex_matching_calls": effects["regex_matches"],
        "subinterpreter_coverage": "NOT RUN",
        "self_oracle_executed": False,
        "candidate_oracle_executed": False,
        "report_written": False,
        "holdout_cases_read": 0,
        "performance_fixtures_read": 0,
        "benchmark_or_timing_executed": False,
        "performance": "NOT MEASURED",
    }


def _locale_arguments(options: argparse.Namespace) -> dict[str, str]:
    names = {
        "iso8859_1": options.iso8859_1_locale,
        "utf8": options.utf8_locale,
    }
    require(
        all(type(value) is str and bool(value) for value in names.values())
        and names["iso8859_1"] != names["utf8"],
        "BLOCKED: supply actually available freshly provisioned "
        "--iso8859-1-locale and --utf8-locale; completed V5 temporary "
        "locales were destroyed and cannot be reused",
    )
    return names


def _worker_document(
    role: str,
    source_sha256: str,
    protocol_sha256: str,
    locale_names: Mapping[str, str],
) -> dict[str, Any]:
    verify_runtime()
    require(role in ("reference_a", "reference_b"),
            "no candidate can run before a published genuine V10 guard exists")
    _read_bounded(SOURCE_RELATIVE, MAX_SOURCE_BYTES, expected=source_sha256)
    _read_bounded(PROTOCOL_RELATIVE, MAX_SOURCE_BYTES, expected=protocol_sha256)
    _require_frozen_matrix()
    matrix = build_matrix()
    validate_matrix(matrix, expected_sha256=MATRIX_SHA256)
    validate_stimuli(matrix, expected_sha256=STIMULUS_SHA256)
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "a genuine reference worker cannot preload an independent engine")
    locale_preflight = _preflight_real_locales(locale_names)
    module = importlib.import_module("re")
    require(module.__name__ == "re", "a genuine Python reference was substituted")
    records: list[dict[str, Any]] = []
    active: str | None = None
    try:
        for row in matrix:
            active = row["id"]
            record = evaluate_case(module, row, locale_names=locale_names)
            if row["cohort"] in ADDITIONAL_COHORTS:
                require(
                    record["outcome"]["status"] == "return",
                    "an additive public infrastructure failure is not a pass",
                )
            if row["cohort"] in {
                "real-locale-switch-on-compiled-bytes",
                "real-locale-invalid-flags-and-cache",
            }:
                _validate_locale_case(record)
            records.append(record)
            active = None
    except BaseException as error:
        raise PublicSurfaceWorkerFailure(
            role,
            "a genuine isolated public reference stopped: " + role,
            {
                "completed_records": records,
                "completed_count": len(records),
                "active_case": active,
                "actual_error": normalize(error),
            },
        ) from error
    return {
        "schema": SCHEMA + "-worker",
        "status": "PASS",
        "role": role,
        "python": "3.14.6",
        "source_sha256": source_sha256,
        "protocol_sha256": protocol_sha256,
        "matrix_sha256": MATRIX_SHA256,
        "stimulus_sha256": STIMULUS_SHA256,
        "cases": EXPECTED_CASES,
        "locale_preflight": locale_preflight,
        "successful_additional_cases": EXPECTED_ADDITIONAL_CASES,
        "successful_real_locale_cases": 2 * CASES_PER_COHORT,
        "real_locale_transition_count": 6 * CASES_PER_COHORT,
        "records": records,
        "record_sha256": validate_records(records, matrix),
        "guard": {"baseline_only": True, "candidate_imported": False},
        "subinterpreter_coverage": "NOT RUN",
        "holdout_cases_read": 0,
        "performance_fixtures_read": 0,
        "benchmark_or_timing_executed": False,
        "performance": "NOT MEASURED",
    }


def _run_reference_worker(
    role: str,
    source_sha256: str,
    protocol_sha256: str,
    locale_names: Mapping[str, str],
) -> dict[str, Any]:
    arguments = [
        str(PINNED_PYTHON), "-I", "-B", str(ROOT / SOURCE_RELATIVE),
        "--worker", role,
        "--source-sha256", source_sha256,
        "--protocol-sha256", protocol_sha256,
        "--iso8859-1-locale", locale_names["iso8859_1"],
        "--utf8-locale", locale_names["utf8"],
    ]
    try:
        completed = subprocess.run(
            arguments,
            cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=3_600,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise PublicSurfaceWorkerFailure(
            role,
            "an actual isolated public reference worker could not complete",
            {"role": role, "actual_error": normalize(error)},
        ) from error
    require(
        len(completed.stdout) <= MAX_WORKER_BYTES
        and len(completed.stderr) <= MAX_WORKER_BYTES,
        "an actual worker exceeded its bounded complete output",
    )
    details = {
        "role": role,
        "returncode": completed.returncode,
        "stdout": completed.stdout.decode("utf-8", errors="backslashreplace"),
        "stderr": completed.stderr.decode("utf-8", errors="backslashreplace"),
    }
    if completed.returncode != 0 or completed.stderr:
        raise PublicSurfaceWorkerFailure(
            role, "an actual independent standard-library worker failed", details,
        )
    document = _strict_json(completed.stdout, role)
    require(
        document.get("schema") == SCHEMA + "-worker"
        and document.get("status") == "PASS"
        and document.get("role") == role
        and document.get("python") == "3.14.6"
        and document.get("source_sha256") == source_sha256
        and document.get("protocol_sha256") == protocol_sha256
        and document.get("matrix_sha256") == MATRIX_SHA256
        and document.get("stimulus_sha256") == STIMULUS_SHA256
        and document.get("cases") == EXPECTED_CASES
        and isinstance(document.get("locale_preflight"), dict)
        and document["locale_preflight"].get("iso8859_1_codeset")
        in {"iso88591", "latin1"}
        and document["locale_preflight"].get("utf8_codeset") == "utf8"
        and document["locale_preflight"].get("ctype_restored") is True
        and document["locale_preflight"].get("locale_path_unchanged") is True
        and document.get("successful_additional_cases") == EXPECTED_ADDITIONAL_CASES
        and document.get("successful_real_locale_cases") == 2 * CASES_PER_COHORT
        and document.get("real_locale_transition_count") == 6 * CASES_PER_COHORT
        and document.get("guard") == {
            "baseline_only": True, "candidate_imported": False,
        }
        and document.get("holdout_cases_read") == 0
        and document.get("performance_fixtures_read") == 0
        and document.get("benchmark_or_timing_executed") is False
        and document.get("performance") == "NOT MEASURED",
        "an actual isolated reference substituted its source or observations",
    )
    matrix = build_matrix()
    require(validate_records(document.get("records"), matrix)
            == document.get("record_sha256"),
            "a genuine independent reference hid an actual public record")
    return document


def run_self_oracle(options: argparse.Namespace) -> dict[str, Any]:
    reference = authenticate_reference(
        options.source_sha256, options.protocol_sha256,
    )
    locale_names = _locale_arguments(options)
    _preflight_outputs((SELF_ORACLE_RELATIVE, SELF_ORACLE_FAILURE_RELATIVE))
    observed: dict[str, dict[str, Any]] = {}
    try:
        for role in ("reference_a", "reference_b"):
            observed[role] = _run_reference_worker(
                role, options.source_sha256, options.protocol_sha256, locale_names,
            )
        first, second = observed["reference_a"], observed["reference_b"]
        require(first["records"] == second["records"],
                "two independently started real public Python references disagree")
        document = {
            "schema": SCHEMA + "-self-oracle",
            "status": "PASS",
            "synthetic": False,
            "python": "3.14.6",
            "source_path": SOURCE_RELATIVE,
            "source_sha256": options.source_sha256,
            "protocol_path": PROTOCOL_RELATIVE,
            "protocol_sha256": options.protocol_sha256,
            "v5_reference_path": V5_REFERENCE_RELATIVE,
            "v5_reference_sha256": V5_REFERENCE_SHA256,
            "original_public_method_matrix_sha256": ORIGINAL_MATRIX_SHA256,
            "original_public_methods": 152,
            "original_passed": 151,
            "original_named_private_debug_skips": 1,
            "original_public_method_waivers": 0,
            "base_cases": EXPECTED_BASE_CASES,
            "additional_cases": EXPECTED_ADDITIONAL_CASES,
            "cohorts": len(COHORTS),
            "cases": EXPECTED_CASES,
            "successful_additional_cases_per_worker": EXPECTED_ADDITIONAL_CASES,
            "successful_real_locale_cases_per_worker": 2 * CASES_PER_COHORT,
            "real_locale_transitions_per_worker": 6 * CASES_PER_COHORT,
            "matrix_sha256": MATRIX_SHA256,
            "stimulus_sha256": STIMULUS_SHA256,
            "actual_independent_reference_count": 2,
            "reference_worker_reports": observed,
            "record_sha256": first["record_sha256"],
            "candidate_audits_read": reference["candidate_audits_read"],
            "candidate_proofs_read": reference["candidate_proofs_read"],
            "candidate_imports": 0,
            "subinterpreter_coverage": "NOT RUN",
            "holdout_cases_read": 0,
            "performance_fixtures_read": 0,
            "benchmark_or_timing_executed": False,
            "performance": "NOT MEASURED",
        }
        _exclusive_write(document, SELF_ORACLE_RELATIVE)
        return document
    except (PublicSurfaceError, OSError, subprocess.SubprocessError) as error:
        failure: dict[str, Any] = {
            "schema": SCHEMA + "-self-oracle-failure",
            "status": "FAIL",
            "synthetic": False,
            "completed_reference_workers": observed,
            "actual_error": normalize(error),
            "performance": "NOT MEASURED",
        }
        if isinstance(error, PublicSurfaceWorkerFailure):
            failure["failed_role"] = error.role
            failure["actual_failure_details"] = error.details
        _exclusive_write(failure, SELF_ORACLE_FAILURE_RELATIVE)
        raise


def authenticate_surface_reference(
    provenance: Mapping[str, Any],
    *,
    source_sha256: str,
    protocol_sha256: str,
    reference_sha256: str | None,
) -> dict[str, Any]:
    require(
        provenance.get("v5_reference_sha256") == V5_REFERENCE_SHA256
        and provenance.get("candidate_audits_read") == 0
        and provenance.get("candidate_proofs_read") == 0
        and provenance.get("candidate_imports") == 0,
        "the complete actual V5 Python baseline must be authenticated first",
    )
    require(
        valid_sha256(reference_sha256),
        "BLOCKED: publish the actual complete two-worker V17 public "
        "reference SHA-256 before any candidate or ownership audit",
    )
    payload = _read_bounded(
        SELF_ORACLE_RELATIVE,
        MAX_EVIDENCE_BYTES,
        expected=str(reference_sha256),
    )
    report = _strict_json(payload, SELF_ORACLE_RELATIVE)
    require(
        report.get("schema") == SCHEMA + "-self-oracle"
        and report.get("status") == "PASS"
        and report.get("synthetic") is False
        and report.get("python") == "3.14.6"
        and report.get("source_path") == SOURCE_RELATIVE
        and report.get("source_sha256") == source_sha256
        and report.get("protocol_path") == PROTOCOL_RELATIVE
        and report.get("protocol_sha256") == protocol_sha256
        and report.get("v5_reference_path") == V5_REFERENCE_RELATIVE
        and report.get("v5_reference_sha256") == V5_REFERENCE_SHA256
        and report.get("original_public_method_matrix_sha256")
        == ORIGINAL_MATRIX_SHA256
        and report.get("original_public_methods") == 152
        and report.get("original_passed") == 151
        and report.get("original_named_private_debug_skips") == 1
        and report.get("original_public_method_waivers") == 0
        and report.get("base_cases") == EXPECTED_BASE_CASES
        and report.get("additional_cases") == EXPECTED_ADDITIONAL_CASES
        and report.get("cohorts") == len(COHORTS)
        and report.get("cases") == EXPECTED_CASES
        and report.get("successful_additional_cases_per_worker")
        == EXPECTED_ADDITIONAL_CASES
        and report.get("successful_real_locale_cases_per_worker")
        == 2 * CASES_PER_COHORT
        and report.get("real_locale_transitions_per_worker")
        == 6 * CASES_PER_COHORT
        and report.get("matrix_sha256") == MATRIX_SHA256
        and report.get("stimulus_sha256") == STIMULUS_SHA256
        and report.get("actual_independent_reference_count") == 2
        and report.get("candidate_audits_read") == 0
        and report.get("candidate_proofs_read") == 0
        and report.get("candidate_imports") == 0
        and report.get("subinterpreter_coverage") == "NOT RUN"
        and report.get("holdout_cases_read") == 0
        and report.get("performance_fixtures_read") == 0
        and report.get("benchmark_or_timing_executed") is False
        and report.get("performance") == "NOT MEASURED",
        "a complete real candidate-free V17 dual public reference is required",
    )
    workers = report.get("reference_worker_reports")
    require(
        isinstance(workers, dict)
        and set(workers) == {"reference_a", "reference_b"},
        "both genuinely retained independent V17 Python workers are required",
    )
    matrix = build_matrix()
    record_hashes: list[str] = []
    records_by_role: list[list[dict[str, Any]]] = []
    for role in ("reference_a", "reference_b"):
        actual = workers[role]
        require(
            isinstance(actual, dict)
            and actual.get("schema") == SCHEMA + "-worker"
            and actual.get("status") == "PASS"
            and actual.get("role") == role
            and actual.get("python") == "3.14.6"
            and actual.get("source_sha256") == source_sha256
            and actual.get("protocol_sha256") == protocol_sha256
            and actual.get("matrix_sha256") == MATRIX_SHA256
            and actual.get("stimulus_sha256") == STIMULUS_SHA256
            and actual.get("cases") == EXPECTED_CASES
            and actual.get("successful_additional_cases")
            == EXPECTED_ADDITIONAL_CASES
            and actual.get("successful_real_locale_cases")
            == 2 * CASES_PER_COHORT
            and actual.get("real_locale_transition_count")
            == 6 * CASES_PER_COHORT
            and actual.get("guard") == {
                "baseline_only": True, "candidate_imported": False,
            }
            and isinstance(actual.get("locale_preflight"), dict)
            and actual["locale_preflight"].get("iso8859_1_codeset")
            in {"iso88591", "latin1"}
            and actual["locale_preflight"].get("utf8_codeset") == "utf8"
            and actual["locale_preflight"].get("ctype_restored") is True
            and actual["locale_preflight"].get("locale_path_unchanged") is True
            and actual.get("subinterpreter_coverage") == "NOT RUN"
            and actual.get("holdout_cases_read") == 0
            and actual.get("performance_fixtures_read") == 0
            and actual.get("benchmark_or_timing_executed") is False
            and actual.get("performance") == "NOT MEASURED",
            "a real independent V17 reference worker was forged: " + role,
        )
        records = actual.get("records")
        observed_hash = validate_records(records, matrix)
        require(
            observed_hash == actual.get("record_sha256"),
            "an actual full V17 reference record was hidden: " + role,
        )
        records_by_role.append(records)
        record_hashes.append(observed_hash)
    require(
        records_by_role[0] == records_by_role[1]
        and record_hashes[0] == record_hashes[1]
        and report.get("record_sha256") == record_hashes[0],
        "the two actual complete V17 public reference workers do not agree",
    )
    return {
        **provenance,
        "surface_reference_sha256": reference_sha256,
        "surface_reference_record_sha256": record_hashes[0],
    }


def run_candidates(options: argparse.Namespace) -> None:
    original_reference = authenticate_reference(
        options.source_sha256, options.protocol_sha256,
    )
    reference = authenticate_surface_reference(
        original_reference,
        source_sha256=options.source_sha256,
        protocol_sha256=options.protocol_sha256,
        reference_sha256=options.reference_sha256,
    )
    pins = {
        "v10_base_report": options.v10_base_report_sha256,
        "v10_strict_report": options.v10_strict_report_sha256,
        **{
            family + "_" + kind: getattr(options, family + "_" + kind + "_sha256")
            for family in FAMILIES for kind in ("edge", "deep")
        },
    }
    authenticate_candidate(reference, pins)
    raise PublicSurfaceError(
        "BLOCKED: genuine individually guarded V10 public candidate workers "
        "have not yet been independently reviewed or executed"
    )


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--self-oracle", action="store_true")
    mode.add_argument("--candidate", choices=("all",))
    mode.add_argument("--worker", choices=("reference_a", "reference_b"),
                      help=argparse.SUPPRESS)
    parser.add_argument("--source-sha256")
    parser.add_argument("--protocol-sha256")
    parser.add_argument("--reference-sha256")
    parser.add_argument("--iso8859-1-locale", dest="iso8859_1_locale")
    parser.add_argument("--utf8-locale")
    parser.add_argument("--v10-base-report-sha256")
    parser.add_argument("--v10-strict-report-sha256")
    for family in FAMILIES:
        for kind in ("edge", "deep"):
            parser.add_argument("--" + family + "-" + kind + "-sha256")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    try:
        if options.self_test:
            document = self_test()
        elif options.worker:
            locale_names = _locale_arguments(options)
            document = _worker_document(
                options.worker, options.source_sha256,
                options.protocol_sha256, locale_names,
            )
        elif options.self_oracle:
            document = run_self_oracle(options)
        else:
            run_candidates(options)
            raise PublicSurfaceError("an unexecuted candidate cannot be a pass")
        sys.stdout.write(canonical(document).decode("ascii") + "\n")
    except (
        PublicSurfaceError, OSError, subprocess.SubprocessError,
        ValueError, UnicodeError, json.JSONDecodeError,
    ) as error:
        sys.stderr.write(canonical({
            "schema": SCHEMA,
            "status": "FAIL",
            "error": str(error),
            "performance": "NOT MEASURED",
        }).decode("ascii") + "\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
