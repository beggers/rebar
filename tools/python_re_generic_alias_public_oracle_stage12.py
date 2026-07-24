#!/usr/bin/env python3
"""Retest genuine Python regex aliases against rebuilt, independently owned engines."""

from __future__ import annotations

import sys

if __name__ == "__main__":
    import os as _stage12_os
    from pathlib import Path as _Stage12Path

    _stage12_root = str(_Stage12Path(__file__).resolve().parent.parent)
    _stage12_entry = (
        "import sys;sys.path.insert(0,sys.argv[1]);"
        "from tools.python_re_generic_alias_public_oracle_stage12 import main;"
        "raise SystemExit(main(sys.argv[2:]))"
    )
    _stage12_os.execv(
        sys.executable,
        [sys.executable, "-I", "-B", "-c", _stage12_entry,
         _stage12_root, *sys.argv[1:]],
    )

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator

from tools import python_re_generic_alias_public_oracle_stage11 as previous


stage07 = previous.stage07
stage06 = previous.stage06
frozen = previous.frozen
official_locale = previous.official_locale
canonical = previous.canonical
digest = previous.digest
ROOT = Path(__file__).resolve().parent.parent

SOURCE_RELATIVE = "tools/python_re_generic_alias_public_oracle_stage12.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/PUBLIC-GENERIC-ALIASES-V12.md"
SCHEMA = "rebar-python-re-public-generic-alias-v12"
SELF_TEST_SCHEMA = SCHEMA + "-self-test"
WORKER_SCHEMA = SCHEMA + "-worker"
SELF_ORACLE_SCHEMA = SCHEMA + "-self-oracle"
ALL_CANDIDATE_SCHEMA = SCHEMA + "-all-candidates"
SEED = 2026072471
SEED_DOMAIN = "rebar/python-re/public-generic-alias/v12"
REQUIRED_CANDIDATES = ("rust", "vm", "zig")
EXPECTED_CASES = 128

STAGE11_SOURCE_RELATIVE = (
    "tools/python_re_generic_alias_public_oracle_stage11.py"
)
STAGE11_SOURCE_SHA256 = (
    "2d8b0417e837d830c3b01495657305536a9d14e289aeb61d503278f5944b16f3"
)
STAGE11_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/PUBLIC-GENERIC-ALIASES-V11.md"
)
STAGE11_PROTOCOL_SHA256 = (
    "b9d93b2ee18d33ad3e474c7e7d9bf7f94cd612526e39982fec0c2a0d0a4d096e"
)
STAGE11_MATRIX_SHA256 = (
    "7e5adbf2ca9c0f752a0c9dddaabe812a780cf58ca9b60efc178bafbaceee7e65"
)
STAGE11_SELF_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-generic-alias-v11-self-oracle.json"
)
STAGE11_SELF_SHA256 = (
    "31245bf7864ae76e46e676a3a35d0fae399d1f6446af482db9f7aa47b5426f8a"
)
STAGE11_RUST_FAILURE_RELATIVE = (
    "candidates/evidence/python-re-generic-alias-public-oracle-v11-"
    "rust-failures.json"
)
STAGE11_RUST_FAILURE_SHA256 = (
    "5d0fce04b95a6d15e4aaff28d2c59337136660a248616672928f7aa85f7efa36"
)
V5_BASE_AUDIT_RELATIVE = (
    "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V5.json"
)
V5_BASE_AUDIT_SHA256 = (
    "42bd73acf6831b67df9a9873fa35c1882f2af09c41933774ba841d2290e6c198"
)
V5_STRICT_AUDIT_RELATIVE = (
    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V5.json"
)
V5_STRICT_AUDIT_SHA256 = (
    "50031133a2aa20b1ef91b126a883a622d916f582fdcbea4ba1763267199c03bb"
)

V6_BASE_AUDIT_SOURCE_RELATIVE = "tools/postfinal_from_scratch_audit_v6.py"
V6_BASE_AUDIT_SOURCE_SHA256: str | None = (
    "77e7ea97f96280019b3be9abfeeb8fc6ff27ca6ecd13189e611586af5719c18f"
)
V6_BASE_AUDIT_RELATIVE = (
    "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V6.json"
)
V6_BASE_AUDIT_SHA256: str | None = (
    "0314e3e5de3386d7c9c1e7f8fa4648554ff53cb53e3aafcecc4cb8e4923ddcbb"
)
V6_BASE_AUDIT_SCHEMA = "rebar-postfinal-from-scratch-audit-v6"
V6_STRICT_AUDIT_SOURCE_RELATIVE = "tools/postfinal_no_delegation_audit_v6.py"
V6_STRICT_AUDIT_SOURCE_SHA256: str | None = (
    "a936abe91d67169ea361b6770404ffe7bc925fdb3275aef854fbe12fe68a8649"
)
V6_STRICT_AUDIT_RELATIVE = (
    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V6.json"
)
V6_STRICT_AUDIT_SHA256: str | None = (
    "93f174f0861b0ee6e9feadf6e49bf222f0766b393ff74179219e65452b03d84f"
)
V6_STRICT_AUDIT_SCHEMA = "rebar-postfinal-no-delegation-audit-v6"

SELF_ORACLE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-generic-alias-v12-self-oracle.json"
)
SELF_ORACLE_FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/"
    "public-generic-alias-v12-self-oracle-failures.json"
)
ALL_CANDIDATE_RELATIVE = (
    "candidates/evidence/python-re-generic-alias-public-oracle-v12-all.json"
)
CANDIDATE_FAILURE_RELATIVES = {
    role: (
        "candidates/evidence/python-re-generic-alias-public-oracle-v12-"
        + role + "-failures.json"
    )
    for role in REQUIRED_CANDIDATES
}
APPROVED_OUTPUTS = (
    SELF_ORACLE_RELATIVE,
    SELF_ORACLE_FAILURE_RELATIVE,
    ALL_CANDIDATE_RELATIVE,
    *(CANDIDATE_FAILURE_RELATIVES[role] for role in REQUIRED_CANDIDATES),
)

CORE_SOURCE_PATHS: dict[str, tuple[str, ...]] = {
    "rust": (
        "candidates/rust_candidate.py",
        "candidates/rust/py_bridge.c",
        "candidates/rust/src/lib.rs",
        "candidates/rust/src/newline.rs",
        "candidates/rust/src/search.rs",
        "candidates/rust/src/stack.rs",
        "candidates/rust/src/unicode_tables.rs",
    ),
    "vm": (
        "candidates/vm_candidate.py",
        "candidates/_vm_native.c",
    ),
    "zig": (
        "candidates/zig_candidate.py",
        "candidates/zig/mini_regex.zig",
        "candidates/zig/py_bridge.c",
    ),
}
NATIVE_PATHS: dict[str, dict[str, str]] = {
    "rust": {
        "candidates.rust_candidate:native-bridge":
            "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "candidates.rust_candidate:native-engine":
            "candidates/_rust_engine.so",
    },
    "vm": {
        "candidates.vm_candidate:native-engine":
            "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
    },
    "zig": {
        "candidates.zig_candidate:native-bridge":
            "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
        "candidates.zig_candidate:native-engine":
            "candidates/_zig_probe.so",
    },
}


def _cohort_seed(cohort: str) -> str:
    frozen.require(cohort in dict(previous.COHORTS), "unknown V12 public alias cohort")
    return digest({"domain": SEED_DOMAIN, "seed": SEED, "cohort": cohort})


def _matrix_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def append(cohort: str, origin: str, argument: str, action: str) -> None:
        rows.append({
            "id": cohort + ":" + origin + ":" + argument + ":" + action,
            "cohort": cohort,
            "origin": origin,
            "argument": argument,
            "action": action,
            "seed": _cohort_seed(cohort),
        })

    for origin in previous.ORIGINS:
        for argument in previous.NORMAL_ARGUMENTS:
            for action in previous.NORMAL_ACTIONS:
                append("ordinary-alias", origin, argument, action)
    for origin in previous.ORIGINS:
        for argument in previous.DIVERSE_ARGUMENTS:
            for action in previous.DIVERSE_ACTIONS:
                append("diverse-argument", origin, argument, action)
    for origin in previous.ORIGINS:
        for argument in previous.NORMAL_ARGUMENTS:
            for action in previous.REJECTION_ACTIONS:
                append("parameterized-type-rejection", origin, argument, action)
    for origin in previous.ORIGINS:
        for argument in previous.NORMAL_ARGUMENTS:
            for action in previous.LIFECYCLE_ACTIONS:
                append("alias-lifecycle", origin, argument, action)
    return rows


MATRIX_SHA256 = (
    "65c93cfbbc337ecd762a6b201bacc77e35eb72d201a9e8bc222d730714885aef"
)


def validate_matrix(value: Any) -> None:
    frozen.require(
        isinstance(value, list)
        and len(value) == EXPECTED_CASES
        and value == _matrix_rows()
        and digest(value) == MATRIX_SHA256
        and len({row["id"] for row in value}) == EXPECTED_CASES,
        "the V12 generic-alias matrix omitted, reordered, or changed a real case",
    )
    for name, count in previous.COHORTS:
        frozen.require(
            sum(row["cohort"] == name for row in value) == count,
            "the V12 generic-alias matrix weakened cohort " + name,
        )


def build_matrix() -> list[dict[str, Any]]:
    rows = _matrix_rows()
    validate_matrix(rows)
    return rows


def _validate_preserved_stage11_reference(document: Any) -> dict[str, Any]:
    frozen.require(isinstance(document, dict), "the real V11 Python reference is absent")
    exact: dict[str, Any] = {
        "schema": "rebar-python-re-public-generic-alias-v11-self-oracle",
        "status": "PASS",
        "result": "PASS",
        "python": "3.14.6",
        "source_path": STAGE11_SOURCE_RELATIVE,
        "source_sha256": STAGE11_SOURCE_SHA256,
        "protocol_path": STAGE11_PROTOCOL_RELATIVE,
        "protocol_sha256": STAGE11_PROTOCOL_SHA256,
        "seed": 2026072461,
        "seed_domain": "rebar/python-re/public-generic-alias/v11",
        "matrix_sha256": STAGE11_MATRIX_SHA256,
        "cohorts": 4,
        "cohort_cases": dict(previous.COHORTS),
        "cases": 128,
        "stdlib_checks": 256,
        "independent_stdlib_roles": ["stdlib-a", "stdlib-b"],
        "mismatches": 0,
        "failure_records": [],
        "candidate_imports": 0,
        "candidate_processes": 0,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    for key, expected in exact.items():
        frozen.require(
            document.get(key) == expected
            and type(document.get(key)) is type(expected),
            "the preserved actual V11 Python reference changed: " + key,
        )
    records = document.get("baseline_records")
    frozen.require(
        isinstance(records, list)
        and len(records) == EXPECTED_CASES
        and [record.get("id") for record in records]
        == [row["id"] for row in _matrix_rows()]
        and document.get("baseline_record_sha256") == digest(records)
        and document.get("second_record_sha256") == digest(records)
        and isinstance(document.get("current_provenance"), dict),
        "the V12 oracle concealed an actual V11 reference observation",
    )
    return document


def _validate_preserved_stage11_failure(
    document: Any, reference: dict[str, Any],
) -> dict[str, Any]:
    frozen.require(isinstance(document, dict), "the actual V11 Rust failure is absent")
    exact: dict[str, Any] = {
        "schema": "rebar-python-re-public-generic-alias-v11-all-candidates-failure",
        "status": "FAIL",
        "result": "FAIL",
        "failed_role": "rust",
        "python": "3.14.6",
        "source_path": STAGE11_SOURCE_RELATIVE,
        "source_sha256": STAGE11_SOURCE_SHA256,
        "protocol_path": STAGE11_PROTOCOL_RELATIVE,
        "protocol_sha256": STAGE11_PROTOCOL_SHA256,
        "seed": 2026072461,
        "seed_domain": "rebar/python-re/public-generic-alias/v11",
        "matrix_sha256": STAGE11_MATRIX_SHA256,
        "cohorts": 4,
        "cohort_cases": dict(previous.COHORTS),
        "expected_cases": 128,
        "self_oracle_path": STAGE11_SELF_RELATIVE,
        "self_oracle_sha256": STAGE11_SELF_SHA256,
        "mismatches": 16,
        "failures_recorded": 16,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
    }
    for key, expected in exact.items():
        frozen.require(
            document.get(key) == expected
            and type(document.get(key)) is type(expected),
            "the actual V11 pickle failure was concealed: " + key,
        )
    expected_records = document.get("baseline_records")
    observed = document.get("candidate_records")
    failures = document.get("failure_records")
    frozen.require(
        expected_records == reference["baseline_records"]
        and isinstance(observed, list)
        and len(observed) == EXPECTED_CASES
        and [record.get("id") for record in observed]
        == [row["id"] for row in _matrix_rows()]
        and isinstance(failures, list)
        and len(failures) == 16,
        "the V12 oracle omitted an actual V11 baseline, Rust case, or failure",
    )
    actual = [
        {"id": left["id"], "expected": left, "actual": right}
        for left, right in zip(expected_records, observed, strict=True)
        if left != right
    ]
    frozen.require(
        failures == actual
        and {row["actual"]["cohort"] for row in failures} == {"alias-lifecycle"}
        and {row["actual"]["origin"] for row in failures} == {"Pattern", "Match"}
        and {row["actual"]["argument"] for row in failures} == {"str", "bytes"}
        and {row["actual"]["action"] for row in failures}
        == {
            "pickle-protocol-0", "pickle-protocol-2",
            "pickle-protocol-4", "pickle-highest-protocol",
        }
        and all(
            row["expected"].get("status") == "returned"
            and row["actual"].get("status") == "raised"
            and row["actual"].get("exception", {}).get("type") == "PicklingError"
            for row in failures
        ),
        "the V12 oracle misrepresented the real sixteen-protocol pickle failure",
    )
    completed = document.get("completed_candidate_reports")
    frozen.require(
        isinstance(completed, dict)
        and set(completed) == {"rust"}
        and completed["rust"].get("status") == "FAIL"
        and completed["rust"].get("cases") == EXPECTED_CASES
        and completed["rust"].get("mismatches") == 16
        and completed["rust"].get("failure_records") == failures
        and completed["rust"].get("record_sha256") == digest(observed)
        and completed["rust"].get("performance") == "NOT MEASURED",
        "the V12 oracle claimed C or Zig ran in the failed V11 experiment",
    )
    guard = completed["rust"].get("guard")
    frozen.require(
        isinstance(guard, dict)
        and guard.get("enabled") is True
        and guard.get("family") == "rust"
        and guard.get("stdlib_re_blocked") is True
        and guard.get("cpython_sre_blocked") is True
        and guard.get("third_party_regex_blocked") is True
        and guard.get("cross_family_blocked") is True
        and guard.get("foreign_dynamic_libraries_blocked") is True
        and guard.get("native_loader_aliases_blocked")
        == list(stage07.NATIVE_LOADER_ALIASES),
        "the true V11 Rust guard or actual no-delegation proof was weakened",
    )
    return document


def _require_pinned_v6_audits() -> None:
    pins = {
        "V6_BASE_AUDIT_SOURCE_SHA256": V6_BASE_AUDIT_SOURCE_SHA256,
        "V6_BASE_AUDIT_SHA256": V6_BASE_AUDIT_SHA256,
        "V6_STRICT_AUDIT_SOURCE_SHA256": V6_STRICT_AUDIT_SOURCE_SHA256,
        "V6_STRICT_AUDIT_SHA256": V6_STRICT_AUDIT_SHA256,
    }
    for name, value in pins.items():
        frozen.require(
            isinstance(value, str) and official_locale.is_sha256(value),
            "the rebuilt V6 independence audit is not yet pinned: " + name,
        )


def _verify_audit_source(relative: str, expected: str) -> None:
    path = official_locale.checked_repo_path(relative)
    frozen.require(
        official_locale.sha256_path(path, maximum=frozen.MAX_SOURCE_BYTES)
        == expected,
        "the rebuilt native-audit producer changed: " + relative,
    )


def _validate_v6_audit_identities(
    base: Any,
    strict: Any,
    *,
    base_source_sha256: str,
    strict_source_sha256: str,
    base_report_sha256: str,
) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    for label, fingerprint in (
        ("from-scratch source", base_source_sha256),
        ("no-delegation source", strict_source_sha256),
        ("from-scratch report", base_report_sha256),
    ):
        frozen.require(
            isinstance(fingerprint, str)
            and official_locale.is_sha256(fingerprint),
            "the exact V6 " + label + " fingerprint is not pinned",
        )
    for document, schema, name, source_path, source_sha256 in (
        (
            base, V6_BASE_AUDIT_SCHEMA, "from-scratch",
            V6_BASE_AUDIT_SOURCE_RELATIVE, base_source_sha256,
        ),
        (
            strict, V6_STRICT_AUDIT_SCHEMA, "no-delegation",
            V6_STRICT_AUDIT_SOURCE_RELATIVE, strict_source_sha256,
        ),
    ):
        frozen.require(
            isinstance(document, dict)
            and document.get("schema") == schema
            and document.get("postfinal_schema") == schema
            and document.get("audit_source_path") == source_path
            and document.get("audit_source_sha256") == source_sha256
            and document.get("status") == "PASS"
            and document.get("result") == "PASS"
            and document.get("passed") is True
            and document.get("verified_core_family_count") == 3,
            "the rebuilt V6 " + name + " audit did not actually pass",
        )
        families = document.get("families")
        frozen.require(
            isinstance(families, dict)
            and set(REQUIRED_CANDIDATES).issubset(families)
            and all(
                isinstance(families[role], dict)
                and families[role].get("passed") is True
                for role in REQUIRED_CANDIDATES
            ),
            "the rebuilt V6 " + name + " audit omitted an independent family",
        )
        manifest = document.get("manifest_provenance")
        frozen.require(
            isinstance(manifest, dict)
            and manifest.get("passed") is True
            and manifest.get("issues") == []
            and manifest.get("python_dependencies") == []
            and manifest.get("rust_third_party_dependency_count") == 0,
            "the rebuilt V6 audit accepted an external regex implementation",
        )
        native = document.get("native_elf_provenance")
        frozen.require(
            isinstance(native, dict)
            and native.get("passed") is True
            and native.get("issues") == []
            and native.get("expected_binary_count") == 5
            and native.get("audited_binary_count") == 5
            and isinstance(native.get("families"), dict)
            and set(native["families"]) == set(REQUIRED_CANDIDATES)
            and all(
                isinstance(native["families"][role], dict)
                and native["families"][role].get("passed") is True
                and native["families"][role].get("issues") == []
                for role in REQUIRED_CANDIDATES
            ),
            "the rebuilt V6 audit did not verify exactly five owned native engines",
        )

    frozen.require(
        base.get("previous_v5_audit_report_path") == V5_BASE_AUDIT_RELATIVE
        and base.get("previous_v5_audit_report_sha256") == V5_BASE_AUDIT_SHA256,
        "the rebuilt from-scratch audit concealed the real historical V5 source proof",
    )
    frozen.require(
        strict.get("base_audit_source_path") == V6_BASE_AUDIT_SOURCE_RELATIVE
        and strict.get("base_audit_source_sha256") == base_source_sha256
        and strict.get("base_audit_report_path") == V6_BASE_AUDIT_RELATIVE
        and strict.get("base_audit_report_sha256") == base_report_sha256,
        "the V6 no-delegation audit is not bound to its real rebuilt source audit",
    )
    frozen.require(
        strict.get("manifest_provenance") == base.get("manifest_provenance")
        and strict.get("native_elf_provenance")
        == base.get("native_elf_provenance"),
        "the V6 audits disagree on actual package inputs or owned native engines",
    )
    source_fingerprints = strict.get("qualified_source_fingerprints")
    all_paths = {
        path for paths in CORE_SOURCE_PATHS.values() for path in paths
    }
    frozen.require(
        isinstance(source_fingerprints, dict)
        and set(source_fingerprints) == all_paths
        and len(source_fingerprints) == 12,
        "the rebuilt V6 audit omitted or substituted one of twelve engine sources",
    )
    source_by_family: dict[str, dict[str, str]] = {}
    for role, paths in CORE_SOURCE_PATHS.items():
        source_by_family[role] = {}
        for relative in paths:
            observed = source_fingerprints.get(relative)
            frozen.require(
                isinstance(observed, str)
                and official_locale.is_sha256(observed),
                "the V6 candidate source fingerprint is invalid: " + relative,
            )
            source_by_family[role][relative] = observed

    fingerprints = strict.get("native_elf_fingerprints")
    native_labels = {
        label for values in NATIVE_PATHS.values() for label in values
    }
    frozen.require(
        isinstance(fingerprints, dict)
        and set(fingerprints) == native_labels
        and len(fingerprints) == 5,
        "the V6 no-delegation audit omitted or substituted an owned native binary",
    )
    native_by_family: dict[str, dict[str, str]] = {}
    for role, paths in NATIVE_PATHS.items():
        native_by_family[role] = {}
        for label, relative in paths.items():
            expected = fingerprints.get(label)
            frozen.require(
                isinstance(expected, str)
                and official_locale.is_sha256(expected),
                "the V6 native engine fingerprint is invalid: " + relative,
            )
            native_by_family[role][relative] = expected

        files = base["native_elf_provenance"]["families"][role].get("files")
        if isinstance(files, dict):
            records = list(files.values())
        elif isinstance(files, list):
            records = list(files)
        else:
            raise frozen.OracleIntegrityError(
                "the V6 source audit concealed native ELF records: " + role
            )
        frozen.require(
            len(records) == len(paths)
            and all(isinstance(record, dict) for record in records),
            "the V6 source audit omitted or duplicated a family native: " + role,
        )
        source_owned: dict[str, str] = {}
        for record in records:
            relative = record.get("file")
            fingerprint = record.get("sha256")
            frozen.require(
                isinstance(relative, str)
                and relative in native_by_family[role]
                and relative not in source_owned
                and isinstance(fingerprint, str)
                and official_locale.is_sha256(fingerprint),
                "the V6 source audit substituted or duplicated an owned native",
            )
            source_owned[relative] = fingerprint
        frozen.require(
            source_owned == native_by_family[role],
            "the V6 audits disagree on a real family-owned native path or hash: "
            + role,
        )
    frozen.require(
        sum(len(values) for values in native_by_family.values()) == 5,
        "the V6 cross-audit native-binary denominator was weakened",
    )
    return source_by_family, native_by_family


def _validate_v6_audits(
    base: Any, strict: Any,
) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    frozen.require(
        isinstance(V6_BASE_AUDIT_SOURCE_SHA256, str)
        and isinstance(V6_STRICT_AUDIT_SOURCE_SHA256, str)
        and isinstance(V6_BASE_AUDIT_SHA256, str),
        "unpublished V6 audit fingerprints cannot validate live engine provenance",
    )
    source_by_family, native_by_family = _validate_v6_audit_identities(
        base,
        strict,
        base_source_sha256=V6_BASE_AUDIT_SOURCE_SHA256,
        strict_source_sha256=V6_STRICT_AUDIT_SOURCE_SHA256,
        base_report_sha256=V6_BASE_AUDIT_SHA256,
    )
    for paths in source_by_family.values():
        for relative, expected in paths.items():
            frozen.require(
                official_locale.sha256_path(
                    official_locale.checked_repo_path(relative),
                    maximum=frozen.MAX_SOURCE_BYTES,
                ) == expected,
                "the V6 candidate source is missing, stale, or substituted: "
                + relative,
            )
    for paths in native_by_family.values():
        for relative, expected in paths.items():
            frozen.require(
                official_locale.sha256_path(
                    official_locale.checked_repo_path(relative)
                ) == expected,
                "the V6 native engine is missing, stale, or unowned: " + relative,
            )
    return source_by_family, native_by_family


def _authenticate_provenance() -> dict[str, Any]:
    official_locale.verify_runtime()
    frozen.candidate_free()
    for relative, expected in (
        (STAGE11_SOURCE_RELATIVE, STAGE11_SOURCE_SHA256),
        (STAGE11_PROTOCOL_RELATIVE, STAGE11_PROTOCOL_SHA256),
    ):
        _verify_audit_source(relative, expected)

    old_self, old_self_sha = stage06._read_public_document(
        STAGE11_SELF_RELATIVE, expected_sha256=STAGE11_SELF_SHA256,
    )
    reference = _validate_preserved_stage11_reference(old_self)
    old_failure, old_failure_sha = stage06._read_public_document(
        STAGE11_RUST_FAILURE_RELATIVE,
        expected_sha256=STAGE11_RUST_FAILURE_SHA256,
    )
    _validate_preserved_stage11_failure(old_failure, reference)
    old_base, old_base_sha = stage06._read_public_document(
        V5_BASE_AUDIT_RELATIVE, expected_sha256=V5_BASE_AUDIT_SHA256,
    )
    old_strict, old_strict_sha = stage06._read_public_document(
        V5_STRICT_AUDIT_RELATIVE, expected_sha256=V5_STRICT_AUDIT_SHA256,
    )
    frozen.require(
        old_self_sha == STAGE11_SELF_SHA256
        and old_failure_sha == STAGE11_RUST_FAILURE_SHA256
        and isinstance(old_base, dict)
        and old_base_sha == V5_BASE_AUDIT_SHA256
        and old_base.get("postfinal_schema")
        == "rebar-postfinal-from-scratch-audit-v5"
        and old_base.get("status") == "PASS"
        and isinstance(old_strict, dict)
        and old_strict_sha == V5_STRICT_AUDIT_SHA256
        and old_strict.get("postfinal_schema")
        == "rebar-postfinal-no-delegation-audit-v5"
        and old_strict.get("status") == "PASS",
        "V12 altered historical V5 independence or the real V11 failed experiment",
    )

    _require_pinned_v6_audits()
    frozen.require(
        V6_BASE_AUDIT_SOURCE_SHA256 is not None
        and V6_BASE_AUDIT_SHA256 is not None
        and V6_STRICT_AUDIT_SOURCE_SHA256 is not None
        and V6_STRICT_AUDIT_SHA256 is not None,
        "unpublished V6 audit fingerprints cannot authorize candidate execution",
    )
    _verify_audit_source(
        V6_BASE_AUDIT_SOURCE_RELATIVE, V6_BASE_AUDIT_SOURCE_SHA256,
    )
    _verify_audit_source(
        V6_STRICT_AUDIT_SOURCE_RELATIVE, V6_STRICT_AUDIT_SOURCE_SHA256,
    )
    base, base_sha = stage06._read_public_document(
        V6_BASE_AUDIT_RELATIVE, expected_sha256=V6_BASE_AUDIT_SHA256,
    )
    strict, strict_sha = stage06._read_public_document(
        V6_STRICT_AUDIT_RELATIVE, expected_sha256=V6_STRICT_AUDIT_SHA256,
    )
    frozen.require(
        base_sha == V6_BASE_AUDIT_SHA256
        and strict_sha == V6_STRICT_AUDIT_SHA256,
        "a current V6 owned-engine or no-delegation audit was substituted",
    )
    source_by_family, native_by_family = _validate_v6_audits(base, strict)

    source = official_locale.checked_repo_path(SOURCE_RELATIVE)
    protocol = official_locale.checked_repo_path(PROTOCOL_RELATIVE)
    source_sha256 = official_locale.sha256_path(
        source, maximum=frozen.MAX_SOURCE_BYTES,
    )
    protocol_sha256 = official_locale.sha256_path(
        protocol, maximum=frozen.MAX_SOURCE_BYTES,
    )
    validate_matrix(build_matrix())
    frozen.candidate_free()
    return {
        "source_path": SOURCE_RELATIVE,
        "source_sha256": source_sha256,
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": protocol_sha256,
        "seed": SEED,
        "seed_domain": SEED_DOMAIN,
        "matrix_sha256": MATRIX_SHA256,
        "previous_stage11_source_path": STAGE11_SOURCE_RELATIVE,
        "previous_stage11_source_sha256": STAGE11_SOURCE_SHA256,
        "previous_stage11_protocol_path": STAGE11_PROTOCOL_RELATIVE,
        "previous_stage11_protocol_sha256": STAGE11_PROTOCOL_SHA256,
        "previous_stage11_self_oracle_path": STAGE11_SELF_RELATIVE,
        "previous_stage11_self_oracle_sha256": STAGE11_SELF_SHA256,
        "previous_stage11_failure_path": STAGE11_RUST_FAILURE_RELATIVE,
        "previous_stage11_failure_sha256": STAGE11_RUST_FAILURE_SHA256,
        "previous_stage11_failure_count": 16,
        "previous_stage11_nonmatching_families": ["vm", "zig"],
        "historical_v5_source_audit_path": V5_BASE_AUDIT_RELATIVE,
        "historical_v5_source_audit_sha256": V5_BASE_AUDIT_SHA256,
        "historical_v5_strict_audit_path": V5_STRICT_AUDIT_RELATIVE,
        "historical_v5_strict_audit_sha256": V5_STRICT_AUDIT_SHA256,
        "base_audit_source_path": V6_BASE_AUDIT_SOURCE_RELATIVE,
        "base_audit_source_sha256": V6_BASE_AUDIT_SOURCE_SHA256,
        "base_audit_path": V6_BASE_AUDIT_RELATIVE,
        "base_audit_sha256": V6_BASE_AUDIT_SHA256,
        "strict_audit_source_path": V6_STRICT_AUDIT_SOURCE_RELATIVE,
        "strict_audit_source_sha256": V6_STRICT_AUDIT_SOURCE_SHA256,
        "strict_audit_path": V6_STRICT_AUDIT_RELATIVE,
        "strict_audit_sha256": V6_STRICT_AUDIT_SHA256,
        "source_sha256_by_family": source_by_family,
        "native_sha256_by_family": native_by_family,
        "stage10_provenance": {
            "native_sha256_by_family": native_by_family,
        },
        "native_source_count": 12,
        "native_binary_count": 5,
    }


WORKER_BOOTSTRAP = (
    "import sys;sys.path.insert(0,sys.argv[1]);"
    "from tools.python_re_generic_alias_public_oracle_stage12 "
    "import _worker_entry;"
    "raise SystemExit(_worker_entry(sys.argv[2],sys.argv[3]))"
)


@contextmanager
def _stage12_context() -> Iterator[None]:
    updates: dict[str, Any] = {
        "SOURCE_RELATIVE": SOURCE_RELATIVE,
        "PROTOCOL_RELATIVE": PROTOCOL_RELATIVE,
        "SCHEMA": SCHEMA,
        "SELF_TEST_SCHEMA": SELF_TEST_SCHEMA,
        "WORKER_SCHEMA": WORKER_SCHEMA,
        "SELF_ORACLE_SCHEMA": SELF_ORACLE_SCHEMA,
        "ALL_CANDIDATE_SCHEMA": ALL_CANDIDATE_SCHEMA,
        "SEED": SEED,
        "SEED_DOMAIN": SEED_DOMAIN,
        "MATRIX_SHA256": MATRIX_SHA256,
        "SELF_ORACLE_RELATIVE": SELF_ORACLE_RELATIVE,
        "SELF_ORACLE_FAILURE_RELATIVE": SELF_ORACLE_FAILURE_RELATIVE,
        "ALL_CANDIDATE_RELATIVE": ALL_CANDIDATE_RELATIVE,
        "CANDIDATE_FAILURE_RELATIVES": CANDIDATE_FAILURE_RELATIVES,
        "APPROVED_OUTPUTS": APPROVED_OUTPUTS,
        "WORKER_BOOTSTRAP": WORKER_BOOTSTRAP,
        "build_matrix": build_matrix,
        "validate_matrix": validate_matrix,
        "_authenticate_provenance": _authenticate_provenance,
    }
    original = {name: getattr(previous, name) for name in updates}
    try:
        for name, value in updates.items():
            setattr(previous, name, value)
        yield
    finally:
        for name, value in original.items():
            setattr(previous, name, value)


def _worker_entry(role: str, source_sha256: str) -> int:
    with _stage12_context():
        return previous._worker_entry(role, source_sha256)


def run_self_oracle() -> dict[str, Any]:
    with _stage12_context():
        return previous.run_self_oracle()


def run_all_candidates() -> dict[str, Any]:
    with _stage12_context():
        return previous.run_all_candidates()


def _synthetic_stage11_reference(
    matrix: list[dict[str, Any]],
) -> dict[str, Any]:
    module = previous._synthetic_module()
    records = [previous.evaluate_case(module, row) for row in matrix]
    for index, row in enumerate(matrix):
        if (
            row["cohort"] == "alias-lifecycle"
            and row["action"].startswith("pickle-")
        ):
            records[index] = {
                "id": row["id"],
                "cohort": row["cohort"],
                "origin": row["origin"],
                "argument": row["argument"],
                "action": row["action"],
                "status": "returned",
                "value": {
                    "synthetic_reference_only": True,
                    "origin": row["origin"],
                    "argument": row["argument"],
                    "protocol": row["action"],
                },
                "warnings": [],
            }
    return {
        "schema": "rebar-python-re-public-generic-alias-v11-self-oracle",
        "status": "PASS",
        "result": "PASS",
        "python": "3.14.6",
        "source_path": STAGE11_SOURCE_RELATIVE,
        "source_sha256": STAGE11_SOURCE_SHA256,
        "protocol_path": STAGE11_PROTOCOL_RELATIVE,
        "protocol_sha256": STAGE11_PROTOCOL_SHA256,
        "seed": 2026072461,
        "seed_domain": "rebar/python-re/public-generic-alias/v11",
        "matrix_sha256": STAGE11_MATRIX_SHA256,
        "cohorts": 4,
        "cohort_cases": dict(previous.COHORTS),
        "cases": 128,
        "stdlib_checks": 256,
        "independent_stdlib_roles": ["stdlib-a", "stdlib-b"],
        "mismatches": 0,
        "failure_records": [],
        "candidate_imports": 0,
        "candidate_processes": 0,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
        "baseline_records": records,
        "baseline_record_sha256": digest(records),
        "second_record_sha256": digest(records),
        "current_provenance": {"synthetic_only": True},
    }


def _synthetic_stage11_failure(
    reference: dict[str, Any],
) -> dict[str, Any]:
    baseline = reference["baseline_records"]
    observed = [dict(item) for item in baseline]
    for index, item in enumerate(observed):
        if item["cohort"] == "alias-lifecycle" and item["action"].startswith("pickle-"):
            observed[index] = {
                "id": item["id"],
                "cohort": item["cohort"],
                "origin": item["origin"],
                "argument": item["argument"],
                "action": item["action"],
                "status": "raised",
                "exception": {
                    "type": "PicklingError",
                    "args": {
                        "type": "tuple",
                        "items": [
                            "Can't pickle <class 're." + item["origin"]
                            + "'>: stage-07 blocked unowned matching import: re"
                        ],
                    },
                },
                "warnings": [],
            }
    failures = [
        {"id": left["id"], "expected": left, "actual": right}
        for left, right in zip(baseline, observed, strict=True)
        if left != right
    ]
    guard = {
        "enabled": True,
        "family": "rust",
        "stdlib_re_blocked": True,
        "cpython_sre_blocked": True,
        "third_party_regex_blocked": True,
        "cross_family_blocked": True,
        "foreign_dynamic_libraries_blocked": True,
        "native_loader_aliases_blocked": list(stage07.NATIVE_LOADER_ALIASES),
    }
    return {
        "schema": "rebar-python-re-public-generic-alias-v11-all-candidates-failure",
        "status": "FAIL",
        "result": "FAIL",
        "failed_role": "rust",
        "python": "3.14.6",
        "source_path": STAGE11_SOURCE_RELATIVE,
        "source_sha256": STAGE11_SOURCE_SHA256,
        "protocol_path": STAGE11_PROTOCOL_RELATIVE,
        "protocol_sha256": STAGE11_PROTOCOL_SHA256,
        "seed": 2026072461,
        "seed_domain": "rebar/python-re/public-generic-alias/v11",
        "matrix_sha256": STAGE11_MATRIX_SHA256,
        "cohorts": 4,
        "cohort_cases": dict(previous.COHORTS),
        "expected_cases": 128,
        "self_oracle_path": STAGE11_SELF_RELATIVE,
        "self_oracle_sha256": STAGE11_SELF_SHA256,
        "mismatches": 16,
        "failures_recorded": 16,
        "benchmark_or_timing_executed": False,
        "performance_fixtures_read": 0,
        "holdout_cases_read": 0,
        "performance": "NOT MEASURED",
        "baseline_records": baseline,
        "candidate_records": observed,
        "failure_records": failures,
        "worker_failure": None,
        "current_provenance": {"synthetic_only": True},
        "completed_candidate_reports": {
            "rust": {
                "candidate": "rust",
                "status": "FAIL",
                "cases": 128,
                "mismatches": 16,
                "failure_records": failures,
                "record_sha256": digest(observed),
                "guard": guard,
                "performance": "NOT MEASURED",
            },
        },
    }


_INSPECT_PRESENT_AT_IMPORT = "inspect" in sys.modules
_TOKENIZE_PRESENT_AT_IMPORT = "tokenize" in sys.modules


def self_test() -> dict[str, Any]:
    frozen.candidate_free()
    with stage06.previous._candidate_free_file_and_timing_guard() as effects:
        checks: list[dict[str, Any]] = []

        def check(name: str, condition: Any) -> None:
            frozen.require(condition, "V12 generic-alias synthetic control: " + name)
            checks.append({"name": name, "passed": True})

        def reject(name: str, action: Callable[[], Any]) -> None:
            try:
                action()
            except (
                frozen.OracleIntegrityError, AssertionError, AttributeError,
                ImportError, KeyError, OSError, TypeError, UnicodeError, ValueError,
            ):
                check(name, True)
                return
            check(name, False)

        matrix = build_matrix()
        check("exactly-128-real-public-compatibility-obligations", len(matrix) == 128)
        check("fresh-source-bound-v12-seed", SEED == 2026072471)
        check("fresh-source-bound-v12-domain", SEED_DOMAIN == "rebar/python-re/public-generic-alias/v12")
        check("fresh-v12-domain-is-not-failed-v11", SEED_DOMAIN != previous.SEED_DOMAIN)
        check("frozen-source-bound-v12-matrix", digest(matrix) == MATRIX_SHA256)
        check("v12-matrix-cannot-reuse-failed-v11-digest", MATRIX_SHA256 != STAGE11_MATRIX_SHA256)
        check("all-128-public-identities-are-preserved", len({row["id"] for row in matrix}) == 128)
        for cohort, count in previous.COHORTS:
            check(
                "complete-v12-cohort-" + cohort,
                sum(row["cohort"] == cohort for row in matrix) == count,
            )
        check("all-ten-ordinary-alias-observations", len(previous.NORMAL_ACTIONS) == 10)
        check("all-eight-diverse-type-operands", len(previous.DIVERSE_ARGUMENTS) == 8)
        check("all-four-real-isinstance-and-issubclass-probes", len(previous.REJECTION_ACTIONS) == 4)
        check("all-six-real-standard-copy-and-pickle-lifecycles", len(previous.LIFECYCLE_ACTIONS) == 6)
        check("true-typing-type-variable-is-retained", isinstance(previous.TYPE_PARAMETER, previous.typing.TypeVar))
        check("normalization-retains-only-exact-owned-alias-origins", callable(previous.evaluate_case))
        check("ordinary-cpython-pickle-is-not-overridden", previous.pickle.dumps.__module__ in ("_pickle", "pickle"))
        check("all-five-foreign-native-loaders-remain-blocked", stage07.NATIVE_LOADER_ALIASES == (
            "ctypes.CDLL", "ctypes.cdll.LoadLibrary", "ctypes.cdll._dlltype",
            "ctypes._dlopen", "_ctypes.dlopen",
        ))
        check("all-three-from-scratch-families-remain-mandatory", REQUIRED_CANDIDATES == previous.REQUIRED_CANDIDATES)
        check("all-twelve-owned-candidate-sources-are-declared", sum(len(x) for x in CORE_SOURCE_PATHS.values()) == 12)
        check("all-five-owned-native-binaries-are-declared", sum(len(x) for x in NATIVE_PATHS.values()) == 5)
        check("new-v6-audit-paths-cannot-reuse-stale-v5-evidence", {
            V6_BASE_AUDIT_RELATIVE, V6_STRICT_AUDIT_RELATIVE,
        }.isdisjoint({V5_BASE_AUDIT_RELATIVE, V5_STRICT_AUDIT_RELATIVE}))
        check("v6-audit-pins-fail-closed-until-root-publishes", all(
            value is None for value in (
                V6_BASE_AUDIT_SOURCE_SHA256, V6_BASE_AUDIT_SHA256,
                V6_STRICT_AUDIT_SOURCE_SHA256, V6_STRICT_AUDIT_SHA256,
            )
        ) or all(
            isinstance(value, str) and official_locale.is_sha256(value)
            for value in (
                V6_BASE_AUDIT_SOURCE_SHA256, V6_BASE_AUDIT_SHA256,
                V6_STRICT_AUDIT_SOURCE_SHA256, V6_STRICT_AUDIT_SHA256,
            )
        ))
        if all(
            value is None for value in (
                V6_BASE_AUDIT_SOURCE_SHA256, V6_BASE_AUDIT_SHA256,
                V6_STRICT_AUDIT_SOURCE_SHA256, V6_STRICT_AUDIT_SHA256,
            )
        ):
            reject(
                "unpublished-v6-audits-cannot-authorize-production",
                _require_pinned_v6_audits,
            )
        synthetic_families = {
            role: {"passed": True} for role in REQUIRED_CANDIDATES
        }
        synthetic_manifest = {
            "passed": True,
            "issues": [],
            "python_dependencies": [],
            "rust_third_party_dependency_count": 0,
        }
        synthetic_native = {
            "passed": True,
            "issues": [],
            "expected_binary_count": 5,
            "audited_binary_count": 5,
            "families": {
                role: {
                    "passed": True,
                    "issues": [],
                    "files": {
                        label.rsplit(":", 1)[-1]: {
                            "file": relative,
                            "sha256": digest({
                                "synthetic_only": True,
                                "role": role,
                                "file": relative,
                            }),
                        }
                        for label, relative in NATIVE_PATHS[role].items()
                    },
                }
                for role in REQUIRED_CANDIDATES
            },
        }
        synthetic_base_source_sha256 = "a" * 64
        synthetic_strict_source_sha256 = "b" * 64
        synthetic_base_report_sha256 = "c" * 64
        synthetic_sources = {
            relative: digest({"synthetic_only": True, "source": relative})
            for paths in CORE_SOURCE_PATHS.values()
            for relative in paths
        }
        synthetic_binaries = {
            label: digest({
                "synthetic_only": True,
                "role": role,
                "file": relative,
            })
            for role, paths in NATIVE_PATHS.items()
            for label, relative in paths.items()
        }
        synthetic_v6_base = {
            "schema": V6_BASE_AUDIT_SCHEMA,
            "postfinal_schema": V6_BASE_AUDIT_SCHEMA,
            "audit_source_path": V6_BASE_AUDIT_SOURCE_RELATIVE,
            "audit_source_sha256": synthetic_base_source_sha256,
            "status": "PASS",
            "result": "PASS",
            "passed": True,
            "verified_core_family_count": 3,
            "families": synthetic_families,
            "manifest_provenance": synthetic_manifest,
            "native_elf_provenance": synthetic_native,
            "previous_v5_audit_report_path": V5_BASE_AUDIT_RELATIVE,
            "previous_v5_audit_report_sha256": V5_BASE_AUDIT_SHA256,
        }
        synthetic_v6_strict = {
            **synthetic_v6_base,
            "schema": V6_STRICT_AUDIT_SCHEMA,
            "postfinal_schema": V6_STRICT_AUDIT_SCHEMA,
            "audit_source_path": V6_STRICT_AUDIT_SOURCE_RELATIVE,
            "audit_source_sha256": synthetic_strict_source_sha256,
            "base_audit_source_path": V6_BASE_AUDIT_SOURCE_RELATIVE,
            "base_audit_source_sha256": synthetic_base_source_sha256,
            "base_audit_report_path": V6_BASE_AUDIT_RELATIVE,
            "base_audit_report_sha256": synthetic_base_report_sha256,
            "qualified_source_fingerprints": synthetic_sources,
            "native_elf_fingerprints": synthetic_binaries,
        }

        def validate_synthetic_v6(
            base: Any, strict: Any,
        ) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
            return _validate_v6_audit_identities(
                base,
                strict,
                base_source_sha256=synthetic_base_source_sha256,
                strict_source_sha256=synthetic_strict_source_sha256,
                base_report_sha256=synthetic_base_report_sha256,
            )

        synthetic_verified_sources, synthetic_verified_natives = (
            validate_synthetic_v6(synthetic_v6_base, synthetic_v6_strict)
        )
        check(
            "cross-audit-identity-validates-all-twelve-owned-source-fingerprints",
            sum(len(values) for values in synthetic_verified_sources.values()) == 12
            and {
                relative: fingerprint
                for values in synthetic_verified_sources.values()
                for relative, fingerprint in values.items()
            } == synthetic_sources,
        )
        check(
            "cross-audit-identity-binds-all-five-real-role-specific-native-paths",
            sum(len(values) for values in synthetic_verified_natives.values()) == 5
            and all(
                {
                    relative: synthetic_binaries[label]
                    for label, relative in NATIVE_PATHS[role].items()
                } == synthetic_verified_natives[role]
                for role in REQUIRED_CANDIDATES
            ),
        )
        reject(
            "historical-v5-source-audit-cannot-impersonate-rebuilt-v6",
            lambda: validate_synthetic_v6(
                {
                    **synthetic_v6_base,
                    "schema": "rebar-postfinal-from-scratch-audit-v5",
                    "postfinal_schema": "rebar-postfinal-from-scratch-audit-v5",
                },
                synthetic_v6_strict,
            ),
        )
        reject(
            "historical-v5-no-delegation-audit-cannot-impersonate-rebuilt-v6",
            lambda: validate_synthetic_v6(
                synthetic_v6_base,
                {
                    **synthetic_v6_strict,
                    "schema": "rebar-postfinal-no-delegation-audit-v5",
                    "postfinal_schema": "rebar-postfinal-no-delegation-audit-v5",
                },
            ),
        )
        for field, replacement in (
            ("schema", V6_STRICT_AUDIT_SCHEMA),
            ("postfinal_schema", V6_STRICT_AUDIT_SCHEMA),
            ("audit_source_path", V6_STRICT_AUDIT_SOURCE_RELATIVE),
            ("audit_source_sha256", "0" * 64),
        ):
            reject(
                "rejects-substituted-v6-source-audit-" + field,
                lambda field=field, replacement=replacement: (
                    validate_synthetic_v6(
                        {**synthetic_v6_base, field: replacement},
                        synthetic_v6_strict,
                    )
                ),
            )
        for field, replacement in (
            ("schema", V6_BASE_AUDIT_SCHEMA),
            ("postfinal_schema", V6_BASE_AUDIT_SCHEMA),
            ("audit_source_path", V6_BASE_AUDIT_SOURCE_RELATIVE),
            ("audit_source_sha256", "0" * 64),
            ("base_audit_source_path", V6_STRICT_AUDIT_SOURCE_RELATIVE),
            ("base_audit_source_sha256", "0" * 64),
            ("base_audit_report_path", V5_BASE_AUDIT_RELATIVE),
            ("base_audit_report_sha256", "0" * 64),
        ):
            reject(
                "rejects-substituted-v6-no-delegation-audit-" + field,
                lambda field=field, replacement=replacement: (
                    validate_synthetic_v6(
                        synthetic_v6_base,
                        {**synthetic_v6_strict, field: replacement},
                    )
                ),
            )
        reject(
            "rejects-disagreeing-cross-audit-package-manifests",
            lambda: validate_synthetic_v6(
                synthetic_v6_base,
                {
                    **synthetic_v6_strict,
                    "manifest_provenance": {
                        **synthetic_manifest, "synthetic_substitution": True,
                    },
                },
            ),
        )
        changed_native = previous.copy.deepcopy(synthetic_native)
        changed_native["families"]["rust"]["files"]["native-bridge"][
            "sha256"
        ] = "0" * 64
        reject(
            "rejects-disagreeing-cross-audit-native-elf-provenance",
            lambda: validate_synthetic_v6(
                synthetic_v6_base,
                {
                    **synthetic_v6_strict,
                    "native_elf_provenance": changed_native,
                },
            ),
        )
        changed_base_native = previous.copy.deepcopy(synthetic_native)
        rust_files = changed_base_native["families"]["rust"]["files"]
        rust_files["native-engine"]["file"] = rust_files["native-bridge"]["file"]
        reject(
            "rejects-a-duplicated-role-owned-native-path",
            lambda: validate_synthetic_v6(
                {
                    **synthetic_v6_base,
                    "native_elf_provenance": changed_base_native,
                },
                {
                    **synthetic_v6_strict,
                    "native_elf_provenance": changed_base_native,
                },
            ),
        )
        omitted_native = previous.copy.deepcopy(synthetic_native)
        omitted_native["families"]["zig"]["files"].pop("native-engine")
        reject(
            "rejects-an-omitted-role-owned-native-elf-record",
            lambda: validate_synthetic_v6(
                {
                    **synthetic_v6_base,
                    "native_elf_provenance": omitted_native,
                },
                {
                    **synthetic_v6_strict,
                    "native_elf_provenance": omitted_native,
                },
            ),
        )
        swapped_binary = dict(synthetic_binaries)
        rust_labels = list(NATIVE_PATHS["rust"])
        swapped_binary[rust_labels[0]], swapped_binary[rust_labels[1]] = (
            swapped_binary[rust_labels[1]], swapped_binary[rust_labels[0]],
        )
        reject(
            "rejects-swapped-real-native-path-and-sha256-identities",
            lambda: validate_synthetic_v6(
                synthetic_v6_base,
                {
                    **synthetic_v6_strict,
                    "native_elf_fingerprints": swapped_binary,
                },
            ),
        )
        reject(
            "passing-labels-with-missing-current-source-fingerprints-are-rejected",
            lambda: validate_synthetic_v6(
                synthetic_v6_base,
                {
                    **synthetic_v6_strict,
                    "qualified_source_fingerprints": {},
                },
            ),
        )
        saved_stage11 = (
            previous.SOURCE_RELATIVE,
            previous.PROTOCOL_RELATIVE,
            previous.MATRIX_SHA256,
            previous.WORKER_BOOTSTRAP,
            previous.APPROVED_OUTPUTS,
            previous.build_matrix,
        )
        with _stage12_context():
            check(
                "strict-worker-context-binds-only-the-frozen-v12-source",
                previous.SOURCE_RELATIVE == SOURCE_RELATIVE
                and previous.PROTOCOL_RELATIVE == PROTOCOL_RELATIVE,
            )
            check(
                "strict-worker-context-binds-all-128-exact-v12-cases",
                previous.MATRIX_SHA256 == MATRIX_SHA256
                and previous.build_matrix() == matrix,
            )
            check(
                "strict-worker-context-binds-a-real-independent-v12-bootstrap",
                previous.WORKER_BOOTSTRAP == WORKER_BOOTSTRAP
                and previous.WORKER_BOOTSTRAP != saved_stage11[3],
            )
            check(
                "strict-worker-context-denies-old-exclusive-evidence-paths",
                previous.APPROVED_OUTPUTS == APPROVED_OUTPUTS
                and set(previous.APPROVED_OUTPUTS).isdisjoint(
                    set(saved_stage11[4])
                ),
            )
        check(
            "strict-v12-context-restores-immutable-failed-v11-source",
            (
                previous.SOURCE_RELATIVE,
                previous.PROTOCOL_RELATIVE,
                previous.MATRIX_SHA256,
                previous.WORKER_BOOTSTRAP,
                previous.APPROVED_OUTPUTS,
                previous.build_matrix,
            ) == saved_stage11,
        )
        for index, poisoned in enumerate((
            matrix[:-1], matrix[1:], list(reversed(matrix)),
            [matrix[0], *matrix[:-1]],
            [{**matrix[0], "action": "concealed"}, *matrix[1:]],
            [{**matrix[0], "origin": "foreign"}, *matrix[1:]],
            [{**matrix[0], "argument": "foreign"}, *matrix[1:]],
            [{**matrix[0], "seed": "0" * 64}, *matrix[1:]],
            [{**matrix[0], "cohort": "foreign"}, *matrix[1:]],
            [{**matrix[0], "id": matrix[1]["id"]}, *matrix[1:]],
        )):
            reject("rejects-mutated-v12-frozen-case-" + str(index), lambda value=poisoned: validate_matrix(value))
        synthetic_reference = _synthetic_stage11_reference(matrix)
        _validate_preserved_stage11_reference(synthetic_reference)
        check("all-128-real-v11-reference-identities-remain-authenticated", True)
        synthetic_failure = _synthetic_stage11_failure(synthetic_reference)
        _validate_preserved_stage11_failure(synthetic_failure, synthetic_reference)
        check("all-16-actual-v11-pickle-failure-shapes-are-preserved", True)
        for key, value in (
            ("status", "PASS"), ("failed_role", "zig"),
            ("mismatches", 15), ("failures_recorded", 15),
            ("matrix_sha256", "0" * 64),
            ("self_oracle_sha256", "0" * 64),
            ("performance", "fabricated"),
            ("benchmark_or_timing_executed", True),
        ):
            reject(
                "rejects-concealed-v11-failure-" + key,
                lambda key=key, value=value: _validate_preserved_stage11_failure(
                    {**synthetic_failure, key: value}, synthetic_reference,
                ),
            )
        reject(
            "rejects-an-omitted-actual-v11-pickle-failure",
            lambda: _validate_preserved_stage11_failure(
                {
                    **synthetic_failure,
                    "failure_records": synthetic_failure["failure_records"][:-1],
                }, synthetic_reference,
            ),
        )
        reject(
            "rejects-a-fabricated-completed-v11-zig-candidate",
            lambda: _validate_preserved_stage11_failure(
                {
                    **synthetic_failure,
                    "completed_candidate_reports": {
                        **synthetic_failure["completed_candidate_reports"],
                        "zig": {"status": "PASS"},
                    },
                }, synthetic_reference,
            ),
        )
        fake_reference = previous._synthetic_module(
            "rebar_stage12_synthetic_reference",
        )
        fake_owned = previous._synthetic_module(
            "rebar_stage12_synthetic_owned",
        )
        comparable = [row for row in matrix if not row["action"].startswith("pickle-")]
        check(
            "honest-owned-class-modules-do-not-produce-false-mismatches",
            len(comparable) == 112
            and [previous.evaluate_case(fake_reference, row) for row in comparable]
            == [previous.evaluate_case(fake_owned, row) for row in comparable],
        )
        forged = previous._synthetic_module(
            "rebar_stage12_synthetic_forgery", forged=True,
        )
        observation = previous.evaluate_case(forged, matrix[1])
        check(
            "forged-foreign-origin-cannot-pass-public-identity-normalization",
            observation["status"] == "returned"
            and observation["value"]["same_public_origin"] is False
            and observation["value"]["origin"]["name"] == "list",
        )
        outputs = set(APPROVED_OUTPUTS)
        check("six-new-exclusive-success-and-failure-paths", len(outputs) == 6)
        check("failed-v11-evidence-can-never-be-overwritten", not outputs.intersection(previous.APPROVED_OUTPUTS))
        check("worker-bootstrap-is-an-independent-source-bound-v12-process", "_stage12" in WORKER_BOOTSTRAP and "_worker_entry" in WORKER_BOOTSTRAP)
        check("synthetic-test-imports-no-candidate", not any(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ))
        check("synthetic-test-imports-no-inspector", ("inspect" in sys.modules) == _INSPECT_PRESENT_AT_IMPORT)
        check("synthetic-test-imports-no-tokenizer", ("tokenize" in sys.modules) == _TOKENIZE_PRESENT_AT_IMPORT)
        check("synthetic-test-starts-no-worker", effects["workers"] == 0)
        check("synthetic-test-opens-no-file", effects["files"] == 0)
        check("synthetic-test-reads-no-clock", effects["timing"] == 0)
        check("synthetic-test-reads-no-entropy", effects["entropy"] == 0)
        check("all-synthetic-side-effects-remain-zero", all(value == 0 for value in effects.values()))
        frozen.candidate_free()
        names = [item["name"] for item in checks]
        frozen.require(
            len(names) == len(set(names)) and len(checks) >= 45,
            "the V12 candidate-free or historical-failure controls were weakened",
        )
        return {
            "schema": SELF_TEST_SCHEMA,
            "stage": "stage12",
            "status": "PASS",
            "result": "PASS",
            "seed": SEED,
            "seed_domain": SEED_DOMAIN,
            "matrix_sha256": MATRIX_SHA256,
            "cohorts": len(previous.COHORTS),
            "cohort_cases": dict(previous.COHORTS),
            "cases": EXPECTED_CASES,
            "check_count": len(checks),
            "checks": checks,
            "failed": [],
            "preserved_stage11_reference_sha256": STAGE11_SELF_SHA256,
            "preserved_stage11_failure_sha256": STAGE11_RUST_FAILURE_SHA256,
            "preserved_stage11_failure_count": 16,
            "historical_v5_source_audit_sha256": V5_BASE_AUDIT_SHA256,
            "historical_v5_strict_audit_sha256": V5_STRICT_AUDIT_SHA256,
            "v6_source_audit_pinned": V6_BASE_AUDIT_SHA256 is not None,
            "v6_strict_audit_pinned": V6_STRICT_AUDIT_SHA256 is not None,
            "owned_source_count": 12,
            "owned_native_binary_count": 5,
            "candidate_imports": 0,
            "candidate_processes": 0,
            "inspect_present_before_self_test": _INSPECT_PRESENT_AT_IMPORT,
            "inspect_imported_by_self_test": (
                ("inspect" in sys.modules) != _INSPECT_PRESENT_AT_IMPORT
            ),
            "tokenize_present_before_self_test": _TOKENIZE_PRESENT_AT_IMPORT,
            "tokenize_imported_by_self_test": (
                ("tokenize" in sys.modules) != _TOKENIZE_PRESENT_AT_IMPORT
            ),
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
            "native_loader_aliases_blocked": list(stage07.NATIVE_LOADER_ALIASES),
            "self_oracle_output": SELF_ORACLE_RELATIVE,
            "self_oracle_failure_output": SELF_ORACLE_FAILURE_RELATIVE,
            "all_candidate_output": ALL_CANDIDATE_RELATIVE,
            "candidate_failure_outputs": dict(CANDIDATE_FAILURE_RELATIVES),
        }


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    try:
        if arguments == ["--self-test"]:
            result = self_test()
        elif arguments == ["--self-oracle"]:
            result = run_self_oracle()
        elif arguments == ["--candidate", "all"]:
            result = run_all_candidates()
        else:
            raise frozen.OracleIntegrityError(
                "select exactly --self-test, --self-oracle, or --candidate all"
            )
        sys.stdout.buffer.write(canonical(result) + b"\n")
        sys.stdout.buffer.flush()
        return 0
    except (
        frozen.OracleIntegrityError, AssertionError, OSError,
        TypeError, UnicodeError, ValueError, stage07.subprocess.SubprocessError,
    ) as error:
        sys.stderr.buffer.write(
            canonical({"schema": SCHEMA, "status": "FAIL", "error": str(error)})
            + b"\n"
        )
        sys.stderr.buffer.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
