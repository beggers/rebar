#!/usr/bin/env python3
"""Rebind the unchanged public Python oracle to the additive V2 source audit."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Callable


WRAPPER = Path(__file__).resolve()
ROOT = WRAPPER.parent.parent
FROZEN_SOURCE = ROOT / "tools" / "python_re_universal_public_oracle_v1.py"
FROZEN_SOURCE_SHA256 = (
    "744876e5b8409b8d49982ccfb61d93a99f3e2d4fd64d0543b29b831bd26796a0"
)
STAGE03_SOURCE = ROOT / "tools" / "python_re_universal_public_oracle_stage03.py"
STAGE03_SOURCE_SHA256 = (
    "477c3f7e9955a9207b9345fc281705b6d643446b5d5c933009fa22a64b8d44ce"
)
V3_ALL_REPORT = (
    ROOT / "candidates" / "evidence" / "python-re-universal-public-oracle-v3-all.json"
)
V3_ALL_REPORT_SHA256 = (
    "a7b6aea6e612de511990d446c8572aa4e1d3094f28ddd2b9f012b1083e73f208"
)
FROZEN_CASE_SHA256 = (
    "8e5c120a4e637c30940363e20d6042324d65d9f7d03fbd35240ffabf2df282ae"
)

AUDIT_SCHEMA = "rebar-postfinal-from-scratch-audit-v2"
AUDIT_SOURCE_RELATIVE = "tools/postfinal_from_scratch_audit_v2.py"
AUDIT_REPORT_RELATIVE = "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V2.json"
ORIGINAL_AUDIT_SOURCE_RELATIVE = "tools/audit_from_scratch.py"
ORIGINAL_AUDIT_SOURCE_SHA256 = (
    "4c47a77cf096df354e59d03096447c56bff890389869c6a75667a36c8471d024"
)
ORIGINAL_AUDIT_REPORT_RELATIVE = "candidates/audits/FROM-SCRATCH-AUDIT.json"
ORIGINAL_AUDIT_REPORT_SHA256 = (
    "c78449b1153221bd0d17854c4f6682062392d19a04cfd0a424a1c6f3fa3478cb"
)
OUTPUT_CANDIDATES = frozenset({"rust", "vm", "zig", "all"})
SYNTHETIC_INTERPRETER = "/synthetic/pinned/bin/python3.14"
SYNTHETIC_AUDIT_SOURCE_SHA256 = hashlib.sha256(
    b"rebar/python-re/universal-public/stage04/synthetic-v2-audit-source"
).hexdigest()

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import python_re_universal_public_oracle_v1 as frozen


frozen.candidate_free()
frozen.require(
    Path(frozen.__file__).resolve() == FROZEN_SOURCE,
    "stage-04 did not import the exact immutable V1 universal public oracle",
)
frozen.require(
    frozen.SCHEMA == "rebar-python-re-universal-public-oracle-v1"
    and frozen.SEED == 2026072417
    and frozen.SEED_DOMAIN == "rebar/python-re/universal-public/v1"
    and frozen.EXPECTED_CASES == 8_192
    and frozen.EXAMPLES_PER_STRATUM == 32
    and frozen.OBSERVATIONS_PER_CASE == 48
    and frozen.EXPECTED_OBSERVATIONS == 393_216
    and len(frozen.GRAMMAR_FAMILIES) == 16
    and len(frozen.INPUT_STRATA) == 16
    and frozenset(frozen.CANDIDATES) == frozenset({"rust", "vm", "zig"}),
    "stage-04 cannot change the immutable seed, cases, comparisons, or isolation",
)

_frozen_build_cases = frozen.build_cases
_frozen_synthetic_audit = frozen.synthetic_audit
_frozen_validate_audit_document = frozen.validate_audit_document
_frozen_verified_provenance = frozen.verified_provenance
_frozen_self_test = frozen.self_test


def stage04_validate_oracle_fingerprints(
    oracle_sha256: str,
    stage03_sha256: str,
) -> None:
    frozen.require(
        oracle_sha256 == FROZEN_SOURCE_SHA256,
        "the immutable V1 universal public oracle changed before stage-04",
    )
    frozen.require(
        stage03_sha256 == STAGE03_SOURCE_SHA256,
        "the immutable stage-03 public oracle wrapper changed before stage-04",
    )


def stage04_production_preflight() -> None:
    """Read and authenticate immutable sources only for actual production."""

    frozen.candidate_free()
    stage04_validate_oracle_fingerprints(
        frozen.sha256_path(FROZEN_SOURCE, frozen.MAX_SOURCE_BYTES),
        frozen.sha256_path(STAGE03_SOURCE, frozen.MAX_SOURCE_BYTES),
    )


def stage04_default_output(candidate: str) -> Path:
    frozen.require(
        candidate in OUTPUT_CANDIDATES,
        "stage-04 must select an exact independently audited candidate slot",
    )
    return (
        frozen.EVIDENCE_ROOT
        / f"python-re-universal-public-oracle-v4-{candidate}.json"
    )


def stage04_build_cases() -> list[dict[str, Any]]:
    cases = _frozen_build_cases()
    frozen.require(
        len(cases) == frozen.EXPECTED_CASES
        and frozen.value_digest(cases) == FROZEN_CASE_SHA256,
        "stage-04 changed the original exact 8,192 deterministic public cases",
    )
    return cases


def stage04_synthetic_audit(
    selected: tuple[str, ...],
) -> tuple[dict[str, Any], dict[str, dict[str, str]], dict[str, dict[str, str]], str]:
    document, sources, binaries, interpreter = _frozen_synthetic_audit(selected)
    frozen.require(
        interpreter == SYNTHETIC_INTERPRETER,
        "stage-04 changed the candidate-free synthetic pinned interpreter",
    )
    document.update(
        {
            "postfinal_schema": AUDIT_SCHEMA,
            "status": "PASS",
            "audit_source_path": AUDIT_SOURCE_RELATIVE,
            "audit_source_sha256": SYNTHETIC_AUDIT_SOURCE_SHA256,
            "original_audit_source_path": ORIGINAL_AUDIT_SOURCE_RELATIVE,
            "original_audit_source_sha256": ORIGINAL_AUDIT_SOURCE_SHA256,
            "original_v1_audit_report_path": ORIGINAL_AUDIT_REPORT_RELATIVE,
            "original_v1_audit_report_sha256": ORIGINAL_AUDIT_REPORT_SHA256,
        }
    )
    return document, sources, binaries, interpreter


def stage04_validate_audit_document(
    document: Any,
    selected: tuple[str, ...],
    actual_sources: dict[str, dict[str, str]],
    actual_binaries: dict[str, dict[str, str]],
    interpreter: str,
) -> None:
    frozen.require(isinstance(document, dict), "stage-04 V2 audit is not an object")
    frozen.require(
        document.get("postfinal_schema") == AUDIT_SCHEMA
        and document.get("schema_version") == 1
        and document.get("audit") == "bounded-from-scratch-engine-provenance"
        and document.get("status") == "PASS"
        and document.get("result") == "PASS"
        and document.get("passed") is True,
        "stage-04 requires the exact V2 audit with unchanged V1 validation",
    )
    frozen.require(
        document.get("audit_source_path") == AUDIT_SOURCE_RELATIVE,
        "stage-04 V2 audit did not bind its exact additive audit source",
    )
    source_sha256 = document.get("audit_source_sha256")
    frozen.require(
        isinstance(source_sha256, str)
        and len(source_sha256) == 64
        and all(character in "0123456789abcdef" for character in source_sha256),
        "stage-04 V2 audit did not provide a canonical source fingerprint",
    )
    if interpreter == SYNTHETIC_INTERPRETER:
        frozen.require(
            source_sha256 == SYNTHETIC_AUDIT_SOURCE_SHA256,
            "stage-04 synthetic V2 audit source fingerprint was poisoned",
        )
    else:
        frozen.require(
            source_sha256
            == frozen.sha256_path(
                ROOT / AUDIT_SOURCE_RELATIVE,
                frozen.MAX_SOURCE_BYTES,
            ),
            "stage-04 actual V2 audit source fingerprint does not match disk",
        )
    frozen.require(
        document.get("original_audit_source_path")
        == ORIGINAL_AUDIT_SOURCE_RELATIVE
        and document.get("original_audit_source_sha256")
        == ORIGINAL_AUDIT_SOURCE_SHA256
        and document.get("original_v1_audit_report_path")
        == ORIGINAL_AUDIT_REPORT_RELATIVE
        and document.get("original_v1_audit_report_sha256")
        == ORIGINAL_AUDIT_REPORT_SHA256,
        "stage-04 V2 audit substituted the immutable original V1 audit",
    )
    _frozen_validate_audit_document(
        document,
        selected,
        actual_sources,
        actual_binaries,
        interpreter,
    )


def stage04_verified_provenance(selected: tuple[str, ...]) -> dict[str, Any]:
    stage04_production_preflight()
    provenance = _frozen_verified_provenance(selected)
    frozen.require(
        provenance.get("audit_path") == AUDIT_REPORT_RELATIVE
        and provenance.get("oracle_source_path")
        == WRAPPER.relative_to(ROOT).as_posix(),
        "stage-04 production did not use its exact V2 audit and public runner",
    )
    frozen.require(
        frozen.sha256_path(FROZEN_SOURCE, frozen.MAX_SOURCE_BYTES)
        == FROZEN_SOURCE_SHA256
        and frozen.sha256_path(STAGE03_SOURCE, frozen.MAX_SOURCE_BYTES)
        == STAGE03_SOURCE_SHA256
        and frozen.sha256_path(
            ROOT / ORIGINAL_AUDIT_SOURCE_RELATIVE,
            frozen.MAX_SOURCE_BYTES,
        )
        == ORIGINAL_AUDIT_SOURCE_SHA256
        and frozen.sha256_path(
            ROOT / ORIGINAL_AUDIT_REPORT_RELATIVE,
            frozen.MAX_AUDIT_BYTES,
        )
        == ORIGINAL_AUDIT_REPORT_SHA256
        and frozen.sha256_path(V3_ALL_REPORT, frozen.MAX_AUDIT_BYTES)
        == V3_ALL_REPORT_SHA256,
        "stage-04 cannot change any original public oracle or audit evidence",
    )
    return {
        **provenance,
        "postfinal_audit_schema": AUDIT_SCHEMA,
        "postfinal_audit_source_path": AUDIT_SOURCE_RELATIVE,
        "postfinal_audit_source_sha256": frozen.sha256_path(
            ROOT / AUDIT_SOURCE_RELATIVE,
            frozen.MAX_SOURCE_BYTES,
        ),
        "original_oracle_source_path": FROZEN_SOURCE.relative_to(ROOT).as_posix(),
        "original_oracle_source_sha256": FROZEN_SOURCE_SHA256,
        "previous_oracle_source_path": STAGE03_SOURCE.relative_to(ROOT).as_posix(),
        "previous_oracle_source_sha256": STAGE03_SOURCE_SHA256,
        "previous_all_candidate_report_path": V3_ALL_REPORT.relative_to(ROOT).as_posix(),
        "previous_all_candidate_report_sha256": V3_ALL_REPORT_SHA256,
        "original_audit_source_path": ORIGINAL_AUDIT_SOURCE_RELATIVE,
        "original_audit_source_sha256": ORIGINAL_AUDIT_SOURCE_SHA256,
        "original_v1_audit_report_path": ORIGINAL_AUDIT_REPORT_RELATIVE,
        "original_v1_audit_report_sha256": ORIGINAL_AUDIT_REPORT_SHA256,
        "immutable_public_case_sha256": FROZEN_CASE_SHA256,
    }


def _stage04_file_free_self_test() -> dict[str, Any]:
    """Run the complete original controls and additive V2 poisons in memory."""

    frozen.candidate_free()
    inherited = _frozen_self_test()
    checks: list[dict[str, Any]] = list(inherited["checks"])

    def check(name: str, condition: Any) -> None:
        frozen.require(condition, f"stage-04 candidate-free self-test failed: {name}")
        checks.append({"name": name, "passed": True})

    stage04_validate_oracle_fingerprints(
        FROZEN_SOURCE_SHA256,
        STAGE03_SOURCE_SHA256,
    )
    check("stage04-accepts-exact-in-memory-immutable-source-hashes", True)

    def reject_source_fingerprints(
        name: str,
        oracle_sha256: str,
        stage03_sha256: str,
    ) -> None:
        try:
            stage04_validate_oracle_fingerprints(
                oracle_sha256,
                stage03_sha256,
            )
        except frozen.OracleIntegrityError:
            check(name, True)
        else:
            check(name, False)

    reject_source_fingerprints(
        "stage04-rejects-poisoned-immutable-v1-source-hash-in-memory",
        "0" * 64,
        STAGE03_SOURCE_SHA256,
    )
    reject_source_fingerprints(
        "stage04-rejects-poisoned-immutable-stage03-source-hash-in-memory",
        FROZEN_SOURCE_SHA256,
        "0" * 64,
    )

    check(
        "stage04-preserves-exact-immutable-public-case-digest",
        inherited.get("case_sha256") == FROZEN_CASE_SHA256,
    )
    check(
        "stage04-preserves-all-48-observations",
        inherited.get("cases") == 8_192
        and inherited.get("observations_per_case") == 48
        and inherited.get("observations_per_candidate") == 393_216,
    )
    check(
        "stage04-preserves-exact-v4-exclusive-output-slots",
        all(
            frozen.validate_output(stage04_default_output(name), name)
            == stage04_default_output(name).resolve()
            for name in ("rust", "vm", "zig", "all")
        ),
    )

    selected = ("rust", "vm", "zig")
    document, sources, binaries, interpreter = stage04_synthetic_audit(selected)
    stage04_validate_audit_document(
        document,
        selected,
        sources,
        binaries,
        interpreter,
    )
    check("stage04-accepts-complete-in-memory-v2-audit", True)

    def reject(name: str, mutate: Callable[[dict[str, Any]], None]) -> None:
        poisoned = json.loads(frozen.canonical(document))
        mutate(poisoned)
        try:
            stage04_validate_audit_document(
                poisoned,
                selected,
                sources,
                binaries,
                interpreter,
            )
        except (frozen.OracleIntegrityError, KeyError, TypeError, ValueError):
            check(name, True)
        else:
            check(name, False)

    reject("stage04-rejects-missing-v2-schema", lambda value: value.pop("postfinal_schema"))
    reject(
        "stage04-rejects-substituted-v2-schema",
        lambda value: value.update(postfinal_schema="rebar-postfinal-from-scratch-audit-v1"),
    )
    reject("stage04-rejects-changed-v1-schema", lambda value: value.update(schema_version=2))
    reject("stage04-rejects-failed-v2-status", lambda value: value.update(status="FAIL"))
    reject("stage04-rejects-failed-v1-result", lambda value: value.update(result="FAIL"))
    reject("stage04-rejects-failed-v1-pass", lambda value: value.update(passed=False))
    reject(
        "stage04-rejects-substituted-v2-source-path",
        lambda value: value.update(audit_source_path=ORIGINAL_AUDIT_SOURCE_RELATIVE),
    )
    reject(
        "stage04-rejects-malformed-v2-source-hash",
        lambda value: value.update(audit_source_sha256="0"),
    )
    reject(
        "stage04-rejects-poisoned-v2-source-hash",
        lambda value: value.update(audit_source_sha256="0" * 64),
    )
    reject(
        "stage04-rejects-substituted-original-audit-source",
        lambda value: value.update(original_audit_source_path=AUDIT_SOURCE_RELATIVE),
    )
    reject(
        "stage04-rejects-poisoned-original-audit-source",
        lambda value: value.update(original_audit_source_sha256="0" * 64),
    )
    reject(
        "stage04-rejects-substituted-original-audit-report",
        lambda value: value.update(original_v1_audit_report_path=AUDIT_REPORT_RELATIVE),
    )
    reject(
        "stage04-rejects-poisoned-original-audit-report",
        lambda value: value.update(original_v1_audit_report_sha256="0" * 64),
    )

    def reject_output(name: str, value: Path, candidate: str) -> None:
        try:
            frozen.validate_output(value, candidate)
        except frozen.OracleIntegrityError:
            check(name, True)
        else:
            check(name, False)

    reject_output(
        "stage04-rejects-overwriting-stage03-evidence",
        frozen.EVIDENCE_ROOT / "python-re-universal-public-oracle-v3-rust.json",
        "rust",
    )
    reject_output(
        "stage04-rejects-overwriting-original-evidence",
        frozen.EVIDENCE_ROOT / "python-re-universal-public-oracle-v1-rust.json",
        "rust",
    )
    reject_output(
        "stage04-rejects-cross-candidate-evidence",
        stage04_default_output("zig"),
        "rust",
    )
    check(
        "stage04-self-test-keeps-candidates-processes-and-files-at-zero",
        inherited.get("candidate_imports") == 0
        and inherited.get("candidate_processes") == 0
        and inherited.get("files_read") == 0
        and inherited.get("files_written") == 0,
    )
    check(
        "stage04-self-test-never-accesses-timing-fixtures-or-holdout",
        inherited.get("performance_fixtures_read") == 0
        and inherited.get("holdout_cases_read") == 0
        and inherited.get("external_regex_packages") == 0
        and inherited.get("benchmark_or_timing_executed") is False,
    )
    frozen.candidate_free()
    check("stage04-self-test-never-imports-production-candidates", True)
    return {
        **inherited,
        "stage": "stage04",
        "postfinal_audit_schema": AUDIT_SCHEMA,
        "original_oracle_source_sha256": FROZEN_SOURCE_SHA256,
        "previous_oracle_source_sha256": STAGE03_SOURCE_SHA256,
        "previous_all_candidate_report_sha256": V3_ALL_REPORT_SHA256,
        "checks": checks,
        "check_count": len(checks),
    }


def stage04_self_test() -> dict[str, Any]:
    """Fail if any synthetic control explicitly hashes a source or evidence."""

    original_sha256_path = frozen.sha256_path

    def reject_file_hash(path: Path, maximum: int) -> str:
        del maximum
        raise frozen.OracleIntegrityError(
            "stage-04 candidate-free self-test attempted to read a file: "
            f"{path}"
        )

    frozen.sha256_path = reject_file_hash
    try:
        report = _stage04_file_free_self_test()
        frozen.require(
            frozen.sha256_path is reject_file_hash,
            "stage-04 candidate-free file-read guard was replaced",
        )
        report["checks"].append(
            {
                "name": "stage04-self-test-guards-all-explicit-file-hashing",
                "passed": True,
            }
        )
        report["check_count"] = len(report["checks"])
        return report
    finally:
        frozen.sha256_path = original_sha256_path


frozen.RUNNER = WRAPPER
frozen.AUDIT_PATH = ROOT / AUDIT_REPORT_RELATIVE
frozen.default_output = stage04_default_output
frozen.build_cases = stage04_build_cases
frozen.synthetic_audit = stage04_synthetic_audit
frozen.validate_audit_document = stage04_validate_audit_document
frozen.verified_provenance = stage04_verified_provenance
frozen.self_test = stage04_self_test


if __name__ == "__main__":
    if "--self-test" not in sys.argv[1:]:
        stage04_production_preflight()
    raise SystemExit(frozen.main())
