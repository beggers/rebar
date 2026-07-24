#!/usr/bin/env python3
"""Preserve all public regex obligations with portable, process-stable evidence."""

from __future__ import annotations

import sys

if __name__ == "__main__":
    import os as _stage08_os
    from pathlib import Path as _Stage08Path

    _stage08_root = str(_Stage08Path(__file__).resolve().parent.parent)
    _stage08_entry = (
        "import sys;sys.path.insert(0,sys.argv[1]);"
        "from tools.python_re_universal_public_oracle_stage08 import main;"
        "raise SystemExit(main(sys.argv[2:]))"
    )
    _stage08_os.execv(
        sys.executable,
        [sys.executable, "-I", "-B", "-c", _stage08_entry, _stage08_root, *sys.argv[1:]],
    )

import argparse
import hashlib
import json
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator


ROOT = Path(__file__).resolve().parent.parent
SOURCE_RELATIVE = "tools/python_re_universal_public_oracle_stage08.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V8.md"
SCHEMA = "rebar-python-re-public-contract-v8"
SELF_TEST_SCHEMA = SCHEMA + "-self-test"
SELF_ORACLE_SCHEMA = SCHEMA + "-self-oracle"
ALL_CANDIDATE_SCHEMA = SCHEMA + "-all-candidates"
OBSERVATION_DOMAIN = "rebar/python-re/public-contract/v8"
SELF_ORACLE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-contract-v8-self-oracle.json"
)
SELF_ORACLE_FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-contract-v8-self-oracle-failures.json"
)
ALL_CANDIDATE_RELATIVE = (
    "candidates/evidence/python-re-universal-public-oracle-v8-all.json"
)
REQUIRED_CANDIDATES = ("rust", "vm", "zig")
CANDIDATE_FAILURE_RELATIVES = {
    family: (
        "candidates/evidence/python-re-universal-public-oracle-v8-"
        + family
        + "-failures.json"
    )
    for family in REQUIRED_CANDIDATES
}
FROZEN_STAGE07_SOURCE_RELATIVE = (
    "tools/python_re_universal_public_oracle_stage07.py"
)
FROZEN_STAGE07_SOURCE_SHA256 = (
    "150abcfc597658f48d64c04053889bd4b299c75ad7413bc1cafa5f864e9e7c25"
)
FROZEN_STAGE07_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/PUBLIC-CONTRACT-V7.md"
)
FROZEN_STAGE07_PROTOCOL_SHA256 = (
    "b4d719609179dde5f582695393539e7a320c09438e4bc635ca843627ac9d7524"
)
FROZEN_STAGE07_FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-contract-v7-self-oracle-failures.json"
)
FROZEN_STAGE07_FAILURE_SHA256 = (
    "765e635745a7e332a1bd22426065c43fd52036d013add0d88d840d8fde1121e0"
)
MATRIX_SHA256 = (
    "0233ca9bc1229b2f905192f9b8ae0c0268b7d23ba3621124192993c6d486f3db"
)
SURROGATE_TAG = "rebar-python-unicode-surrogatepass-v8"
SURROGATE_MAPPING_TAG = "rebar-python-surrogate-key-mapping-v8"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import python_re_universal_public_oracle_stage07 as stage07


stage06 = stage07.stage06
frozen = stage07.frozen
official_locale = stage07.official_locale
frozen.candidate_free()
frozen.require(
    Path(stage07.__file__).resolve() == ROOT / FROZEN_STAGE07_SOURCE_RELATIVE
    and stage07.REQUIRED_CANDIDATES == REQUIRED_CANDIDATES
    and stage07.EXPECTED_CASES == 3_584
    and stage07.MATRIX_SHA256 == MATRIX_SHA256
    and len(stage07.COHORTS) == 8
    and stage07.PINNED_BASE_REPORT_SHA256
    == "42bd73acf6831b67df9a9873fa35c1882f2af09c41933774ba841d2290e6c198"
    and stage07.PINNED_STRICT_REPORT_SHA256
    == "50031133a2aa20b1ef91b126a883a622d916f582fdcbea4ba1763267199c03bb"
    and stage07.PINNED_LOCALE_REPORT_SHA256
    == "bc17ee74409543d1b57f3aee65088e990ab21ac83dc75ac46fbd1f97f04b6621",
    "stage-08 substituted the actual immutable Python, family, or locale obligations",
)

_FROZEN_CANONICAL = stage07.canonical
_FROZEN_NORMALIZE = stage07._normalize
_FROZEN_OBJECT_OBLIGATION = stage07._object_obligation
_FROZEN_AUTHENTICATE = stage07._authenticate_current_provenance
_FROZEN_EVIDENCE_WRITER = stage07._exclusive_evidence
_FROZEN_VALIDATE_WORKER_REPORT = stage07._validate_worker_report
_FROZEN_VALIDATE_SELF_ORACLE = stage07._validate_self_oracle

WORKER_BOOTSTRAP = (
    "import sys;"
    "sys.path.insert(0,sys.argv[1]);"
    "from tools.python_re_universal_public_oracle_stage08 "
    "import _worker_entry;"
    "raise SystemExit(_worker_entry(sys.argv[2],sys.argv[3]))"
)


def _legacy_digest(value: Any) -> str:
    """Bind historical hashing to V7 canonical bytes, not mutable globals."""

    return hashlib.sha256(_FROZEN_CANONICAL(value)).hexdigest()


def _portable(value: Any) -> Any:
    if isinstance(value, str):
        if any(0xD800 <= ord(character) <= 0xDFFF for character in value):
            return {
                "type": SURROGATE_TAG,
                "encoding": "utf-8/surrogatepass",
                "hex": value.encode("utf-8", "surrogatepass").hex(),
            }
        return value
    if isinstance(value, list):
        return [_portable(item) for item in value]
    if isinstance(value, tuple):
        return [_portable(item) for item in value]
    if isinstance(value, dict):
        ordinary_keys = all(
            isinstance(key, str)
            and not any(0xD800 <= ord(item) <= 0xDFFF for item in key)
            for key in value
        )
        reserved_envelope = (
            set(value) == {"type", "encoding", "hex"}
            and value.get("type") == SURROGATE_TAG
        ) or (
            set(value) == {"type", "items"}
            and value.get("type") == SURROGATE_MAPPING_TAG
        )
        if ordinary_keys and not reserved_envelope:
            return {key: _portable(item) for key, item in value.items()}
        entries = [[_portable(key), _portable(item)] for key, item in value.items()]
        entries.sort(key=lambda pair: canonical(pair[0]))
        return {"type": SURROGATE_MAPPING_TAG, "items": entries}
    return value


def canonical(value: Any) -> bytes:
    portable = _portable(value)
    return json.dumps(
        portable,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii", "strict")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def _normalize(value: Any) -> Any:
    # Preserve genuine text in memory.  Canonical serialization applies the
    # reversible codec exactly once at each isolated process boundary.
    return _FROZEN_NORMALIZE(value)


def _restore_portable(value: Any) -> Any:
    if isinstance(value, list):
        return [_restore_portable(item) for item in value]
    if isinstance(value, dict):
        if set(value) == {"type", "encoding", "hex"} and value.get("type") == SURROGATE_TAG:
            frozen.require(
                value.get("encoding") == "utf-8/surrogatepass"
                and isinstance(value.get("hex"), str),
                "a portable stage-08 Unicode value is missing its exact encoding",
            )
            try:
                encoded = bytes.fromhex(value["hex"])
                frozen.require(
                    encoded.hex() == value["hex"],
                    "a portable stage-08 Unicode encoding is not canonical",
                )
                restored = encoded.decode(
                    "utf-8", "surrogatepass"
                )
                frozen.require(
                    any(0xD800 <= ord(item) <= 0xDFFF for item in restored)
                    and restored.encode("utf-8", "surrogatepass") == encoded,
                    "a portable stage-08 Unicode tag does not contain a surrogate",
                )
                return restored
            except (UnicodeError, ValueError) as error:
                raise frozen.OracleIntegrityError(
                    "a portable stage-08 Unicode value is not reversible"
                ) from error
        if set(value) == {"type", "items"} and value.get("type") == SURROGATE_MAPPING_TAG:
            pairs = value.get("items")
            frozen.require(
                isinstance(pairs, list),
                "a portable stage-08 surrogate-key dictionary is malformed",
            )
            restored: dict[Any, Any] = {}
            for pair in pairs:
                frozen.require(
                    isinstance(pair, list) and len(pair) == 2,
                    "a portable stage-08 dictionary entry is malformed",
                )
                key = _restore_portable(pair[0])
                try:
                    frozen.require(
                        key not in restored,
                        "a portable stage-08 dictionary key was duplicated",
                    )
                    restored[key] = _restore_portable(pair[1])
                except TypeError as error:
                    raise frozen.OracleIntegrityError(
                        "a portable stage-08 dictionary key is not hashable"
                    ) from error
            return restored
        return {key: _restore_portable(item) for key, item in value.items()}
    return value


def _object_obligation(module: Any, index: int) -> Any:
    if index % 8 != 0:
        return _FROZEN_OBJECT_OBLIGATION(module, index)
    expression = r"(?P<word>a+)(b)?"
    pattern = module.compile(expression, module.I)
    value = hash(pattern)
    same = module.compile(expression, module.I)
    module.purge()
    independently_compiled = module.compile(expression, module.I)
    mapping = {pattern: "stage08-equal-pattern"}
    return {
        "hash_is_int": type(value) is int,
        "repeat_hash_stable": hash(pattern) == value,
        "self_equal": pattern == pattern,
        "cached_pattern_equal": pattern == same,
        "cached_equal_hash": hash(same) == value,
        "independently_compiled_equal": pattern == independently_compiled,
        "independently_compiled_equal_hash": (
            hash(independently_compiled) == value
        ),
        "equal_pattern_dictionary_lookup": (
            mapping.get(independently_compiled) == "stage08-equal-pattern"
        ),
    }


def _validate_preserved_failure(document: Any) -> None:
    frozen.require(
        isinstance(document, dict)
        and document.get("schema")
        == "rebar-python-re-public-contract-v7-self-oracle-failure"
        and document.get("status") == "FAIL"
        and document.get("result") == "FAIL"
        and document.get("source_path") == FROZEN_STAGE07_SOURCE_RELATIVE
        and document.get("source_sha256") == FROZEN_STAGE07_SOURCE_SHA256
        and document.get("protocol_path") == FROZEN_STAGE07_PROTOCOL_RELATIVE
        and document.get("protocol_sha256") == FROZEN_STAGE07_PROTOCOL_SHA256
        and document.get("seed") == stage07.SEED
        and document.get("seed_domain") == stage07.SEED_DOMAIN
        and document.get("matrix_sha256") == MATRIX_SHA256
        and document.get("cases") == 3_584
        and document.get("stdlib_checks") == 7_168
        and document.get("mismatches") == 32
        and document.get("failures_recorded") == 32,
        "stage-08 cannot conceal or replace the actual stage-07 self-oracle failure",
    )
    baseline = document.get("baseline_records")
    second = document.get("second_records")
    identities = [item["id"] for item in stage07.build_matrix()]
    frozen.require(
        isinstance(baseline, list)
        and isinstance(second, list)
        and len(baseline) == len(second) == 3_584
        and all(isinstance(record, dict) for record in baseline)
        and all(isinstance(record, dict) for record in second)
        and [record.get("id") for record in baseline] == identities
        and [record.get("id") for record in second] == identities
        and document.get("baseline_record_sha256") == _legacy_digest(baseline)
        and document.get("second_record_sha256") == _legacy_digest(second),
        "stage-08 cannot omit, reorder, or replace either full failed Python run",
    )
    failures = document.get("failure_records")
    frozen.require(
        isinstance(failures, list) and len(failures) == 32,
        "stage-08 requires all 32 immutable actual Python self-oracle failures",
    )
    frozen.require(
        {item.get("id") for item in failures if isinstance(item, dict)}
        == {f"object-contract:{index:04d}" for index in range(0, 256, 8)},
        "stage-08 cannot discard or rename a single falsified pattern-hash case",
    )
    for item in failures:
        left = item.get("expected")
        right = item.get("actual")
        frozen.require(
            isinstance(left, dict)
            and isinstance(right, dict)
            and left.get("id") == item["id"]
            and right.get("id") == item["id"]
            and left.get("cohort") == "object-contract"
            and right.get("cohort") == "object-contract"
            and left.get("status") == "returned"
            and right.get("status") == "returned",
            "stage-08 substituted a frozen process-local hash failure",
        )
        frozen.require(
            {key: value for key, value in left.items() if key != "value"}
            == {key: value for key, value in right.items() if key != "value"},
            "a historical Python disagreement was not confined to its hash",
        )
        left_value = left.get("value")
        right_value = right.get("value")
        frozen.require(
            isinstance(left_value, dict)
            and isinstance(right_value, dict)
            and set(left_value) == set(right_value) == {"type", "items"}
            and left_value.get("type") == right_value.get("type") == "dict"
            and isinstance(left_value.get("items"), list)
            and isinstance(right_value.get("items"), list)
            and len(left_value["items"]) == len(right_value["items"]) == 2
            and all(
                isinstance(pair, list) and len(pair) == 2
                for pair in [*left_value["items"], *right_value["items"]]
            ),
            "the historical object obligation changed its public observation shape",
        )
        left_fields = dict(left_value["items"])
        right_fields = dict(right_value["items"])
        frozen.require(
            set(left_fields) == set(right_fields) == {"hash", "self_equal"}
            and type(left_fields.get("hash")) is int
            and type(right_fields.get("hash")) is int
            and left_fields["hash"] != right_fields["hash"]
            and left_fields.get("self_equal") is True
            and right_fields.get("self_equal") is True,
            "a preserved Python mismatch was not exclusively process-local hashing",
        )
    actual_failures = [
        {"id": left["id"], "expected": left, "actual": right}
        for left, right in zip(baseline, second, strict=True)
        if left != right
    ]
    frozen.require(
        len(actual_failures) == 32 and actual_failures == failures,
        "stage-08 concealed a historical disagreement or changed a preserved row",
    )


def _authenticate_current_provenance() -> dict[str, Any]:
    """Bind V8 and the complete, unmodified actual V7 failed experiment."""

    provenance = _FROZEN_AUTHENTICATE()
    for relative, expected in (
        (FROZEN_STAGE07_SOURCE_RELATIVE, FROZEN_STAGE07_SOURCE_SHA256),
        (FROZEN_STAGE07_PROTOCOL_RELATIVE, FROZEN_STAGE07_PROTOCOL_SHA256),
    ):
        path = official_locale.checked_repo_path(relative)
        frozen.require(
            official_locale.sha256_path(path, maximum=frozen.MAX_SOURCE_BYTES)
            == expected,
            "stage-08 cannot change the exact failed stage-07 source or protocol",
        )
    failure, failure_digest = stage06._read_public_document(
        FROZEN_STAGE07_FAILURE_RELATIVE,
        expected_sha256=FROZEN_STAGE07_FAILURE_SHA256,
    )
    frozen.require(
        failure_digest == FROZEN_STAGE07_FAILURE_SHA256,
        "stage-08 cannot substitute the exclusive actual failed self-oracle",
    )
    _validate_preserved_failure(failure)
    frozen.candidate_free()
    return {
        **provenance,
        "observation_domain": OBSERVATION_DOMAIN,
        "previous_failed_source_path": FROZEN_STAGE07_SOURCE_RELATIVE,
        "previous_failed_source_sha256": FROZEN_STAGE07_SOURCE_SHA256,
        "previous_failed_protocol_path": FROZEN_STAGE07_PROTOCOL_RELATIVE,
        "previous_failed_protocol_sha256": FROZEN_STAGE07_PROTOCOL_SHA256,
        "previous_self_oracle_failure_path": FROZEN_STAGE07_FAILURE_RELATIVE,
        "previous_self_oracle_failure_sha256": FROZEN_STAGE07_FAILURE_SHA256,
        "previous_self_oracle_failure_count": 32,
        "previous_hash_nondeterminism_only": True,
    }


def _validate_worker_report(
    document: Any, *, role: str, source_sha256: str
) -> dict[str, Any]:
    """Decode a real child boundary before authenticating its record digest."""

    return _FROZEN_VALIDATE_WORKER_REPORT(
        _restore_portable(document), role=role, source_sha256=source_sha256
    )


def _validate_self_oracle(document: Any, provenance: dict[str, Any]) -> dict[str, Any]:
    """Restore exclusively written strict JSON before inherited validation."""

    frozen.require(isinstance(document, dict), "the stage-08 self-oracle is absent")
    restored = _restore_portable(document)
    frozen.require(isinstance(restored, dict), "the stage-08 self-oracle is malformed")
    document.clear()
    document.update(restored)
    return _FROZEN_VALIDATE_SELF_ORACLE(document, provenance)


@contextmanager
def _stage08_context() -> Iterator[None]:
    updates = {
        "SOURCE_RELATIVE": SOURCE_RELATIVE,
        "PROTOCOL_RELATIVE": PROTOCOL_RELATIVE,
        "SCHEMA": SCHEMA,
        "SELF_TEST_SCHEMA": SELF_TEST_SCHEMA,
        "SELF_ORACLE_SCHEMA": SELF_ORACLE_SCHEMA,
        "ALL_CANDIDATE_SCHEMA": ALL_CANDIDATE_SCHEMA,
        "SELF_ORACLE_RELATIVE": SELF_ORACLE_RELATIVE,
        "SELF_ORACLE_FAILURE_RELATIVE": SELF_ORACLE_FAILURE_RELATIVE,
        "ALL_CANDIDATE_RELATIVE": ALL_CANDIDATE_RELATIVE,
        "CANDIDATE_FAILURE_RELATIVES": CANDIDATE_FAILURE_RELATIVES,
        "WORKER_BOOTSTRAP": WORKER_BOOTSTRAP,
        "canonical": canonical,
        "digest": digest,
        "_normalize": _normalize,
        "_object_obligation": _object_obligation,
        "_authenticate_current_provenance": _authenticate_current_provenance,
        "_validate_worker_report": _validate_worker_report,
        "_validate_self_oracle": _validate_self_oracle,
    }
    original = {name: getattr(stage07, name) for name in updates}
    try:
        for name, value in updates.items():
            setattr(stage07, name, value)
        yield
    finally:
        for name, value in original.items():
            setattr(stage07, name, value)


def _worker_entry(role: str, source_sha256: str) -> int:
    """Run the real inherited worker in its own source-bound V8 context."""

    with _stage08_context():
        provenance = _authenticate_current_provenance()
        frozen.require(
            provenance.get("source_sha256") == source_sha256,
            "the independent stage-08 child does not match its frozen controller",
        )
        return stage07._worker_entry(role, source_sha256)


def run_self_oracle() -> dict[str, Any]:
    with _stage08_context():
        return stage07.run_self_oracle()


def run_all_candidates() -> dict[str, Any]:
    with _stage08_context():
        return stage07.run_all_candidates()


def _synthetic_previous_failure(matrix: list[dict[str, Any]]) -> dict[str, Any]:
    """Construct all historical shapes in memory, never by reading evidence."""

    left_records: list[dict[str, Any]] = []
    right_records: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for row in matrix:
        if row["cohort"] == "object-contract" and row["index"] % 8 == 0:
            left = {
                "id": row["id"],
                "cohort": row["cohort"],
                "status": "returned",
                "value": {
                    "type": "dict",
                    "items": [["hash", -49], ["self_equal", True]],
                },
                "warnings": [],
            }
            right = {
                **left,
                "value": {
                    "type": "dict",
                    "items": [["hash", -70], ["self_equal", True]],
                },
            }
            failures.append({"id": row["id"], "expected": left, "actual": right})
        else:
            if row["cohort"] == "bounded-unicode" and row["index"] % 16 == 10:
                synthetic_value: Any = "\ud800"
            elif row["cohort"] == "bounded-unicode" and row["index"] % 16 == 11:
                synthetic_value = "\udfff"
            else:
                synthetic_value = None
            left = {
                "id": row["id"],
                "cohort": row["cohort"],
                "status": "returned",
                "value": synthetic_value,
                "warnings": [],
            }
            right = left
        left_records.append(left)
        right_records.append(right)
    return {
        "schema": "rebar-python-re-public-contract-v7-self-oracle-failure",
        "status": "FAIL",
        "result": "FAIL",
        "source_path": FROZEN_STAGE07_SOURCE_RELATIVE,
        "source_sha256": FROZEN_STAGE07_SOURCE_SHA256,
        "protocol_path": FROZEN_STAGE07_PROTOCOL_RELATIVE,
        "protocol_sha256": FROZEN_STAGE07_PROTOCOL_SHA256,
        "seed": stage07.SEED,
        "seed_domain": stage07.SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "cases": 3_584,
        "stdlib_checks": 7_168,
        "baseline_records": left_records,
        "second_records": right_records,
        "baseline_record_sha256": _legacy_digest(left_records),
        "second_record_sha256": _legacy_digest(right_records),
        "mismatches": 32,
        "failures_recorded": 32,
        "failure_records": failures,
    }


def self_test() -> dict[str, Any]:
    """Test every V8 change synthetically without files, workers or timing."""

    frozen.candidate_free()
    with stage06.previous._candidate_free_file_and_timing_guard() as effects:
        inherited = stage07.self_test()
        frozen.require(
            inherited.get("stage") == "stage07"
            and inherited.get("status") == "PASS"
            and inherited.get("check_count", 0) >= 375
            and inherited.get("candidate_imports") == 0
            and inherited.get("candidate_processes") == 0
            and inherited.get("files_read") == 0
            and inherited.get("files_written") == 0
            and inherited.get("holdout_cases_read") == 0
            and inherited.get("performance_fixtures_read") == 0
            and inherited.get("benchmark_or_timing_executed") is False,
            "stage-08 lost an inherited candidate-free stage-07 protection",
        )
        stage07.gc.collect()
        checks = list(inherited["checks"])

        def check(name: str, condition: Any) -> None:
            frozen.require(condition, "stage-08 synthetic control failed: " + name)
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
                UnicodeError,
            ):
                check(name, True)
            else:
                check(name, False)

        matrix = stage07.build_matrix()
        check("stage08-preserves-all-3584-public-case-identities", len(matrix) == 3_584)
        check(
            "stage08-preserves-exact-original-ascii-canonical-matrix",
            digest(matrix) == _legacy_digest(matrix) == MATRIX_SHA256,
        )
        check(
            "stage08-preserves-original-matrix-seed-and-domain",
            stage07.SEED == 2026072437
            and stage07.SEED_DOMAIN == "rebar/python-re/public-contract/v7",
        )
        for name, _operation, expected in stage07.COHORTS:
            check(
                "stage08-preserves-exact-cohort-" + name,
                sum(row["cohort"] == name for row in matrix) == expected,
            )
        locales = [row for row in matrix if row["cohort"] == "real-locale"]
        check(
            "stage08-preserves-all-1024-real-locale-triples",
            len(locales) == 1_024
            and len(
                {
                    (row["byte"], row["locale"], row["compiled_before_switch"])
                    for row in locales
                }
            )
            == 1_024,
        )
        threaded = [row for row in matrix if row["cohort"] == "shared-pattern-threads"]
        for thread_count in (4, 8):
            check(
                "stage08-preserves-128-real-shared-pattern-threads-"
                + str(thread_count),
                sum(row["threads"] == thread_count for row in threaded) == 128,
            )
        check(
            "stage08-preserves-all-five-guarded-native-loader-aliases",
            stage07.NATIVE_LOADER_ALIASES
            == (
                "ctypes.CDLL",
                "ctypes.cdll.LoadLibrary",
                "ctypes.cdll._dlltype",
                "ctypes._dlopen",
                "_ctypes.dlopen",
            ),
        )
        check(
            "stage08-preserves-official-upstream-locale-method-fingerprint",
            stage07.PINNED_OFFICIAL_METHOD_SHA256
            == "d33571d09a3a9cb428a84dece5af233e66267b831d3043c90e3ad77cb8de5178",
        )
        check(
            "stage08-preserves-only-six-method-and-two-private-class-waivers",
            len(official_locale.METHOD_WAIVERS) == 6
            and len(official_locale.CLASS_WAIVERS) == 2,
        )
        check(
            "stage08-child-bootstrap-imports-the-authenticated-v8-worker",
            "tools.python_re_universal_public_oracle_stage08" in WORKER_BOOTSTRAP
            and "import _worker_entry" in WORKER_BOOTSTRAP
            and "python_re_universal_public_oracle_stage07" not in WORKER_BOOTSTRAP,
        )
        for label, observed in (
            ("stage07-source", FROZEN_STAGE07_SOURCE_SHA256),
            ("stage07-protocol", FROZEN_STAGE07_PROTOCOL_SHA256),
            ("actual-stage07-failure", FROZEN_STAGE07_FAILURE_SHA256),
            ("immutable-public-matrix", MATRIX_SHA256),
        ):
            check(
                "stage08-pins-exact-64-character-" + label,
                isinstance(observed, str)
                and len(observed) == 64
                and all(character in "0123456789abcdef" for character in observed),
            )

        samples: tuple[Any, ...] = (
            "\ud800",
            "\udfff",
            "\ud800\udfff",
            "before\ud800after",
            "𝄞",
            "ordinary",
            {"\ud800": "x", "plain": "\udfff"},
            {
                "type": SURROGATE_TAG,
                "encoding": "utf-8/surrogatepass",
                "hex": "eda080",
            },
            {
                "type": SURROGATE_MAPPING_TAG,
                "items": [["ordinary", "\ud800"]],
            },
            {
                "nested": [
                    {"\ud800": {"text": "before\udfffafter"}},
                    {
                        "type": SURROGATE_TAG,
                        "encoding": "utf-8/surrogatepass",
                        "hex": "eda080",
                    },
                    {
                        "type": SURROGATE_MAPPING_TAG,
                        "items": [["ordinary", "literal"]],
                    },
                ]
            },
        )
        for index, sample in enumerate(samples):
            encoded = canonical({"value": sample})
            decoded = json.loads(encoded)
            check(
                "stage08-roundtrips-exact-unicode-and-reserved-envelope-"
                + str(index),
                _restore_portable(decoded) == {"value": sample},
            )
            check(
                "stage08-emits-strict-ascii-portable-json-" + str(index),
                encoded.decode("ascii").encode("ascii") == encoded
                and b"\\ud800" not in encoded
                and b"\\udfff" not in encoded,
            )
            check(
                "stage08-roundtrips-canonical-worker-boundary-" + str(index),
                canonical(_restore_portable(json.loads(encoded))) == encoded,
            )
        poisoned_tags: tuple[Any, ...] = (
            {"type": SURROGATE_TAG, "encoding": "wrong", "hex": "eda080"},
            {"type": SURROGATE_TAG, "encoding": "utf-8/surrogatepass", "hex": "EDA080"},
            {"type": SURROGATE_TAG, "encoding": "utf-8/surrogatepass", "hex": "ed a0 80"},
            {"type": SURROGATE_TAG, "encoding": "utf-8/surrogatepass", "hex": "ed"},
            {"type": SURROGATE_TAG, "encoding": "utf-8/surrogatepass", "hex": "61"},
            {"type": SURROGATE_TAG, "encoding": "utf-8/surrogatepass", "hex": "zz"},
            {"type": SURROGATE_MAPPING_TAG, "items": "invalid"},
            {"type": SURROGATE_MAPPING_TAG, "items": [["same", 1], ["same", 2]]},
            {"type": SURROGATE_MAPPING_TAG, "items": [[["unhashable"], 1]]},
            {"type": SURROGATE_MAPPING_TAG, "items": [["missing-value"]]},
        )
        for index, poisoned in enumerate(poisoned_tags):
            reject(
                "stage08-rejects-malformed-portable-envelope-" + str(index),
                lambda document=poisoned: _restore_portable(document),
            )

        class SyntheticPattern:
            def __init__(self, expression: str, flags: int) -> None:
                self.expression = expression
                self.flags = flags

            def __hash__(self) -> int:
                return 17

            def __eq__(self, other: object) -> bool:
                return (
                    isinstance(other, SyntheticPattern)
                    and self.expression == other.expression
                    and self.flags == other.flags
                )

        class SyntheticModule:
            I = 2

            def __init__(self) -> None:
                self.cache: dict[tuple[str, int], SyntheticPattern] = {}
                self.purges = 0

            def compile(self, expression: str, flags: int) -> SyntheticPattern:
                key = (expression, flags)
                if key not in self.cache:
                    self.cache[key] = SyntheticPattern(expression, flags)
                return self.cache[key]

            def purge(self) -> None:
                self.purges += 1
                self.cache.clear()

        expected_hash_fields = {
            "hash_is_int",
            "repeat_hash_stable",
            "self_equal",
            "cached_pattern_equal",
            "cached_equal_hash",
            "independently_compiled_equal",
            "independently_compiled_equal_hash",
            "equal_pattern_dictionary_lookup",
        }
        for index in range(0, 256, 8):
            module = SyntheticModule()
            result = _object_obligation(module, index)
            check(
                "stage08-preserves-real-process-local-hash-obligation-"
                + f"{index:04d}",
                set(result) == expected_hash_fields
                and all(type(value) is bool and value for value in result.values())
                and module.purges == 1
                and b'"hash":' not in canonical(result),
            )

        synthetic_failure = _synthetic_previous_failure(matrix)
        _validate_preserved_failure(synthetic_failure)
        check("stage08-verifies-all-3584-historical-baseline-records", True)
        check("stage08-verifies-all-3584-historical-second-records", True)
        check("stage08-verifies-all-3552-unchanged-historical-agreements", True)
        check("stage08-verifies-exactly-32-real-hash-only-failure-identities", True)
        check(
            "stage08-synthetic-historical-records-preserve-genuine-lone-surrogates",
            sum(
                record.get("value") == "\ud800"
                for record in synthetic_failure["baseline_records"]
            )
            == 64
            and sum(
                record.get("value") == "\udfff"
                for record in synthetic_failure["baseline_records"]
            )
            == 64,
        )
        check(
            "stage08-separates-v7-surrogate-hashes-from-strict-v8-observations",
            synthetic_failure["baseline_record_sha256"]
            == _legacy_digest(synthetic_failure["baseline_records"])
            and synthetic_failure["baseline_record_sha256"]
            != digest(synthetic_failure["baseline_records"]),
        )
        for field, replacement in (
            ("schema", "foreign-schema"),
            ("status", "PASS"),
            ("result", "PASS"),
            ("source_path", SOURCE_RELATIVE),
            ("source_sha256", "0" * 64),
            ("protocol_path", PROTOCOL_RELATIVE),
            ("protocol_sha256", "0" * 64),
            ("seed", 0),
            ("seed_domain", OBSERVATION_DOMAIN),
            ("matrix_sha256", "0" * 64),
            ("cases", 3_583),
            ("stdlib_checks", 7_167),
            ("baseline_record_sha256", "0" * 64),
            ("second_record_sha256", "0" * 64),
            ("mismatches", 31),
            ("failures_recorded", 31),
        ):
            reject(
                "stage08-rejects-substituted-historical-" + field,
                lambda field=field, replacement=replacement: (
                    _validate_preserved_failure(
                        {**synthetic_failure, field: replacement}
                    )
                ),
            )
        reject(
            "stage08-rejects-an-omitted-historical-baseline-obligation",
            lambda: _validate_preserved_failure(
                {**synthetic_failure, "baseline_records": synthetic_failure["baseline_records"][:-1]}
            ),
        )
        reject(
            "stage08-rejects-an-omitted-historical-second-obligation",
            lambda: _validate_preserved_failure(
                {**synthetic_failure, "second_records": synthetic_failure["second_records"][:-1]}
            ),
        )
        reject(
            "stage08-rejects-an-omitted-historical-hash-disagreement",
            lambda: _validate_preserved_failure(
                {**synthetic_failure, "failure_records": synthetic_failure["failure_records"][:-1]}
            ),
        )
        duplicate_records = list(synthetic_failure["failure_records"])
        duplicate_records[-1] = duplicate_records[0]
        reject(
            "stage08-rejects-a-duplicated-historical-hash-disagreement",
            lambda: _validate_preserved_failure(
                {**synthetic_failure, "failure_records": duplicate_records}
            ),
        )

        v7_outputs = (
            stage07.SELF_ORACLE_RELATIVE,
            stage07.SELF_ORACLE_FAILURE_RELATIVE,
            stage07.ALL_CANDIDATE_RELATIVE,
            *stage07.CANDIDATE_FAILURE_RELATIVES.values(),
        )
        outputs = (
            SELF_ORACLE_RELATIVE,
            SELF_ORACLE_FAILURE_RELATIVE,
            ALL_CANDIDATE_RELATIVE,
            *CANDIDATE_FAILURE_RELATIVES.values(),
        )
        check(
            "stage08-authorizes-six-exclusive-distinct-fresh-evidence-paths",
            len(outputs) == len(set(outputs)) == 6
            and not set(outputs).intersection(v7_outputs),
        )
        with _stage08_context():
            check(
                "stage08-legacy-canonical-remains-bound-under-the-real-v8-context",
                _legacy_digest(synthetic_failure["baseline_records"])
                == synthetic_failure["baseline_record_sha256"]
                and _legacy_digest(synthetic_failure["second_records"])
                == synthetic_failure["second_record_sha256"]
                and stage07.digest(synthetic_failure["baseline_records"])
                != synthetic_failure["baseline_record_sha256"],
            )
            _validate_preserved_failure(synthetic_failure)
            check(
                "stage08-authenticates-surrogate-bearing-v7-failure-in-real-v8-context",
                True,
            )
            check(
                "stage08-binds-the-actual-child-bootstrap-in-every-worker",
                stage07.WORKER_BOOTSTRAP == WORKER_BOOTSTRAP,
            )
            check(
                "stage08-binds-the-current-v8-source-and-protocol",
                stage07.SOURCE_RELATIVE == SOURCE_RELATIVE
                and stage07.PROTOCOL_RELATIVE == PROTOCOL_RELATIVE,
            )
            check(
                "stage08-binds-source-authentication-in-every-child",
                stage07._authenticate_current_provenance
                is _authenticate_current_provenance,
            )
            check(
                "stage08-decodes-real-worker-records-before-digest-validation",
                stage07._validate_worker_report is _validate_worker_report
                and stage07._validate_self_oracle is _validate_self_oracle,
            )
            check(
                "stage08-preserves-the-authenticated-exclusive-o-excl-writer",
                stage07._exclusive_evidence is _FROZEN_EVIDENCE_WRITER,
            )
            check(
                "stage08-context-preserves-the-identical-frozen-case-matrix",
                stage07.digest(stage07.build_matrix()) == MATRIX_SHA256,
            )
            for output in outputs:
                check(
                    "stage08-authorizes-only-exact-" + Path(output).name,
                    stage07.exact_output(output, output) == output,
                )
                for poisoned in (
                    "/" + output,
                    "../" + output,
                    output.replace("/", "//", 1),
                    output + "\x00",
                    next(item for item in outputs if item != output),
                ):
                    reject(
                        "stage08-rejects-foreign-exclusive-path-"
                        + Path(output).name
                        + "-"
                        + str(len(checks)),
                        lambda value=poisoned, expected=output: (
                            stage07.exact_output(value, expected)
                        ),
                    )
        check(
            "stage08-restores-the-immutable-stage07-worker-context",
            stage07.SOURCE_RELATIVE == FROZEN_STAGE07_SOURCE_RELATIVE
            and stage07.PROTOCOL_RELATIVE == FROZEN_STAGE07_PROTOCOL_RELATIVE
            and stage07.WORKER_BOOTSTRAP != WORKER_BOOTSTRAP
            and stage07._authenticate_current_provenance is _FROZEN_AUTHENTICATE
            and stage07._exclusive_evidence is _FROZEN_EVIDENCE_WRITER,
        )
        check(
            "stage08-never-opens-files-starts-workers-times-or-draws-entropy",
            all(value == 0 for value in effects.values()),
        )
        frozen.candidate_free()
        check("stage08-never-imports-any-production-candidate", True)
        names = [item["name"] for item in checks]
        frozen.require(
            len(names) == len(set(names)) and len(checks) >= 475,
            "stage-08 synthetic controls were duplicated, omitted or weakened",
        )
        return {
            "schema": SELF_TEST_SCHEMA,
            "stage": "stage08",
            "status": "PASS",
            "result": "PASS",
            "seed": stage07.SEED,
            "seed_domain": stage07.SEED_DOMAIN,
            "observation_domain": OBSERVATION_DOMAIN,
            "cohorts": len(stage07.COHORTS),
            "cases": stage07.EXPECTED_CASES,
            "matrix_sha256": MATRIX_SHA256,
            "cohort_cases": {
                name: count for name, _operation, count in stage07.COHORTS
            },
            "inherited_stage07_control_count": inherited["check_count"],
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
            "previous_failed_source_sha256": FROZEN_STAGE07_SOURCE_SHA256,
            "previous_failed_protocol_sha256": FROZEN_STAGE07_PROTOCOL_SHA256,
            "previous_self_oracle_failure_sha256": FROZEN_STAGE07_FAILURE_SHA256,
            "previous_self_oracle_failure_count": 32,
            "self_oracle_output": SELF_ORACLE_RELATIVE,
            "self_oracle_failure_output": SELF_ORACLE_FAILURE_RELATIVE,
            "all_candidate_output": ALL_CANDIDATE_RELATIVE,
            "candidate_failure_outputs": dict(CANDIDATE_FAILURE_RELATIVES),
            "native_loader_aliases_blocked": list(stage07.NATIVE_LOADER_ALIASES),
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
            frozen.require(args.candidate == "all", "all three native families are mandatory")
            report = run_all_candidates()
        sys.stdout.buffer.write(canonical(report) + b"\n")
        sys.stdout.buffer.flush()
        return 0
    except (
        frozen.OracleIntegrityError,
        AssertionError,
        OSError,
        ValueError,
        stage07.subprocess.SubprocessError,
    ) as error:
        sys.stderr.buffer.write(
            canonical({"schema": SCHEMA, "status": "FAIL", "error": str(error)})
            + b"\n"
        )
        sys.stderr.buffer.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
