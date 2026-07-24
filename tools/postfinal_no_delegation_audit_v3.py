#!/usr/bin/env python3
"""Requalify four from-scratch source families against the V3 source audit.

The default-safe ``--self-test`` uses deterministic synthetic objects only.  It
does not read a report, import or run a candidate, inspect a holdout, take a
measurement, write a file, or start a subprocess.  Only explicit ``--audit``
authenticates the exact public V3 base and reruns the immutable independent
32- and 76-control production checks in continuously guarded worker processes.
Historical V1 and V2 evidence is authenticated and never overwritten.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
from typing import Any, Callable, Mapping


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import postfinal_no_delegation_audit_v2 as previous


SCHEMA = "rebar-postfinal-no-delegation-audit-v3"
BASE_POSTFINAL_SCHEMA = "rebar-postfinal-from-scratch-audit-v3"
PREVIOUS_STRICT_SCHEMA = "rebar-postfinal-no-delegation-audit-v2"
SOURCE_RELATIVE = "tools/postfinal_no_delegation_audit_v3.py"
SOURCE = ROOT / SOURCE_RELATIVE
BASE_V3_SOURCE_RELATIVE = "tools/postfinal_from_scratch_audit_v3.py"
BASE_V3_SOURCE = ROOT / BASE_V3_SOURCE_RELATIVE
BASE_V3_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V3.json"
)
BASE_V3_REPORT = ROOT / BASE_V3_REPORT_RELATIVE
PREVIOUS_BASE_SOURCE_RELATIVE = "tools/postfinal_from_scratch_audit_v2.py"
PREVIOUS_BASE_SOURCE_SHA256 = (
    "6f540074c9f7f4bdffe9e53939efe4cec25e5c029ca1f73ec791d377bddc9306"
)
PREVIOUS_BASE_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V2.json"
)
PREVIOUS_BASE_REPORT_SHA256 = (
    "5e299a767cbd494683100519a6ad461d1a0eb9de1564b1437c7e0229cca7a551"
)
PREVIOUS_STRICT_SOURCE_RELATIVE = "tools/postfinal_no_delegation_audit_v2.py"
PREVIOUS_STRICT_SOURCE_SHA256 = (
    "571c11885f9c9694025ea0434e57bfaa56651057eee62fa4396a2bcb95ae4cb5"
)
PREVIOUS_STRICT_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V2.json"
)
PREVIOUS_STRICT_REPORT_SHA256 = (
    "183cd04f5e1587c181505c09867566b4bd18db270f974475c2b456ff09af1d9f"
)
REPORT_RELATIVE = "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V3.json"
REPORT = ROOT / REPORT_RELATIVE
MAX_SOURCE_BYTES = 16 * 1024 * 1024
MAX_DOCUMENT_BYTES = 16 * 1024 * 1024

PUBLIC_INPUTS = frozenset(
    {
        SOURCE_RELATIVE,
        PREVIOUS_STRICT_SOURCE_RELATIVE,
        "tools/postfinal_no_delegation_audit_v1.py",
        BASE_V3_SOURCE_RELATIVE,
        PREVIOUS_BASE_SOURCE_RELATIVE,
        "tools/audit_from_scratch.py",
        BASE_V3_REPORT_RELATIVE,
        PREVIOUS_BASE_REPORT_RELATIVE,
        "candidates/audits/FROM-SCRATCH-AUDIT.json",
        "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V1.json",
        PREVIOUS_STRICT_REPORT_RELATIVE,
    }
)


class AuditFailure(previous.AuditFailure):
    """A V3 independence proof or immutable predecessor did not verify."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise AuditFailure(message)


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    except (OverflowError, TypeError, UnicodeError, ValueError) as error:
        raise AuditFailure("V3 evidence must be finite canonical ASCII JSON") from error


def require_candidate_free() -> None:
    previous.require_candidate_free()


def verify_pinned_runtime() -> None:
    previous.verify_pinned_runtime()


def validate_public_relative(relative: Any) -> str:
    require(
        isinstance(relative, str) and relative in PUBLIC_INPUTS,
        "refusing a private, holdout, final, benchmark, or unapproved input",
    )
    return relative


def relative_public_path(path: Path) -> str:
    require(
        isinstance(path, Path) and not path.is_symlink(),
        "a V3 public input is missing or is a symlink",
    )
    try:
        resolved = path.resolve(strict=True)
        relative = resolved.relative_to(ROOT.resolve()).as_posix()
    except (OSError, RuntimeError, ValueError) as error:
        raise AuditFailure("a V3 public input is missing or escaped the project") from error
    validate_public_relative(relative)
    require(resolved.is_file(), f"a V3 public input is not a regular file: {relative}")
    return relative


def bounded_public_bytes(path: Path, *, maximum: int) -> tuple[bytes, str]:
    relative = relative_public_path(path)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor: int | None = None
    try:
        descriptor = os.open(path, flags)
        before = os.fstat(descriptor)
        require(
            stat.S_ISREG(before.st_mode) and 0 <= before.st_size <= maximum,
            f"a V3 public input is not a bounded regular file: {relative}",
        )
        chunks: list[bytes] = []
        count = 0
        while True:
            chunk = os.read(descriptor, min(1024 * 1024, maximum + 1 - count))
            if not chunk:
                break
            count += len(chunk)
            require(count <= maximum, f"a V3 public input exceeds its bound: {relative}")
            chunks.append(chunk)
        after = os.fstat(descriptor)
    except OSError as error:
        raise AuditFailure(f"cannot safely read pinned V3 public input: {relative}") from error
    finally:
        if descriptor is not None:
            os.close(descriptor)
    require(
        (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns)
        == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
        and count == before.st_size,
        f"a pinned V3 public input changed while being authenticated: {relative}",
    )
    payload = b"".join(chunks)
    return payload, hashlib.sha256(payload).hexdigest()


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in result, "V3 public JSON contains a duplicate object key")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> Any:
    raise AuditFailure(f"V3 public JSON contains a nonfinite constant: {value}")


def decode_public_json(payload: bytes) -> dict[str, Any]:
    require(
        isinstance(payload, bytes) and len(payload) <= MAX_DOCUMENT_BYTES,
        "V3 public JSON must be a bounded byte string",
    )
    try:
        result = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_unique_json_object,
            parse_constant=_reject_json_constant,
        )
    except (UnicodeError, json.JSONDecodeError, OverflowError, TypeError, ValueError) as error:
        raise AuditFailure("a V3 public audit input is not strict UTF-8 JSON") from error
    require(isinstance(result, dict), "a V3 public audit input is not an object")
    return result


def public_document(path: Path) -> tuple[dict[str, Any], str]:
    payload, digest = bounded_public_bytes(path, maximum=MAX_DOCUMENT_BYTES)
    return decode_public_json(payload), digest


def validate_wrapper_self_test(value: Any, *, label: str, current_v3: bool) -> None:
    require(isinstance(value, Mapping), f"{label} omitted its candidate-free controls")
    records = value.get("checks")
    count = value.get("check_count")
    require(
        value.get("passed") is True
        and value.get("result") == "PASS"
        and type(count) is int
        and count >= 52
        and isinstance(records, list)
        and len(records) == count
        and all(
            isinstance(item, Mapping)
            and isinstance(item.get("name"), str)
            and item.get("passed") is True
            for item in records
        )
        and len({item["name"] for item in records}) == count
        and value.get("failed") == []
        and value.get("fixture_storage") == "in-memory only"
        and value.get("candidate_imported") is False
        and value.get("subprocesses") == 0
        and value.get("file_reads") == 0
        and value.get("file_writes") == 0
        and value.get("historical_holdout_accessed") is False
        and value.get("holdout_or_case_fixture_access") is False
        and value.get("benchmark_or_timing_executed") is False,
        f"{label} weakened, renamed, repeated, or executed a safety control",
    )
    require(
        value.get("schema")
        == (
            BASE_POSTFINAL_SCHEMA + "-self-test"
            if current_v3
            else previous.BASE_POSTFINAL_SCHEMA + "-self-test"
        ),
        f"{label} substituted its immutable candidate-free self-test schema",
    )
    if current_v3:
        require(
            value.get("candidate_imports") == []
            and value.get("guard_accessed") is False
            and value.get("production_cases_materialized") == 0
            and value.get("report_written") is False,
            f"{label} imported a candidate, accessed a guard, or created evidence",
        )


def validate_base_report(report: Mapping[str, Any]) -> dict[str, dict[str, str]]:
    require(isinstance(report, Mapping), "the V3 base independence proof is not an object")
    expected: dict[str, Any] = {
        "schema_version": 1,
        "audit": "bounded-from-scratch-engine-provenance",
        "postfinal_schema": BASE_POSTFINAL_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "audit_source_path": BASE_V3_SOURCE_RELATIVE,
        "original_audit_source_path": "tools/audit_from_scratch.py",
        "original_audit_source_sha256": previous.ORIGINAL_BASE_SOURCE_SHA256,
        "original_v1_audit_report_path": "candidates/audits/FROM-SCRATCH-AUDIT.json",
        "original_v1_audit_report_sha256": previous.ORIGINAL_BASE_REPORT_SHA256,
        "previous_v2_audit_source_path": PREVIOUS_BASE_SOURCE_RELATIVE,
        "previous_v2_audit_source_sha256": PREVIOUS_BASE_SOURCE_SHA256,
        "previous_v2_audit_report_path": PREVIOUS_BASE_REPORT_RELATIVE,
        "previous_v2_audit_report_sha256": PREVIOUS_BASE_REPORT_SHA256,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
    }
    for field, value in expected.items():
        require(
            report.get(field) == value and type(report.get(field)) is type(value),
            f"the V3 base proof changed its immutable {field}",
        )
    require(
        previous.valid_sha256(report.get("audit_source_sha256")),
        "the V3 base proof omitted its actual current source fingerprint",
    )
    validate_wrapper_self_test(
        report.get("postfinal_wrapper_self_test"),
        label="the V3 from-scratch wrapper",
        current_v3=True,
    )
    historical_wrapper = report.get("previous_v2_wrapper_self_test")
    if historical_wrapper is not None:
        validate_wrapper_self_test(
            historical_wrapper,
            label="the immutable V2 from-scratch wrapper",
            current_v3=False,
        )
    adapted: dict[str, Any] = {
        **report,
        "postfinal_schema": previous.BASE_POSTFINAL_SCHEMA,
        "audit_source_path": PREVIOUS_BASE_SOURCE_RELATIVE,
        "audit_source_sha256": PREVIOUS_BASE_SOURCE_SHA256,
    }
    sources = previous.validate_base_report(adapted)
    require(
        set(sources) == set(previous.AUDITED_FAMILIES),
        "the V3 base proof did not preserve all four independent source families",
    )
    return sources


def _validate_flattened_native(report: Mapping[str, Any], *, label: str) -> None:
    fingerprints = report.get("native_elf_fingerprints")
    evidence = report.get("native_elf_provenance")
    require(
        isinstance(fingerprints, Mapping)
        and set(fingerprints) == previous.EXPECTED_NATIVE_KEYS
        and all(previous.valid_sha256(value) for value in fingerprints.values())
        and isinstance(evidence, Mapping)
        and evidence.get("passed") is True
        and evidence.get("audited_binary_count") == 5
        and evidence.get("expected_binary_count") == 5,
        f"{label} omitted, substituted, or added an independently owned native role",
    )
    families = evidence.get("families")
    require(isinstance(families, Mapping), f"{label} omitted its actual parsed ELF families")
    for family, roles in previous.NATIVE_ROLE_PATHS.items():
        current = families.get(family)
        require(
            isinstance(current, Mapping) and current.get("passed") is True,
            f"{label} omitted the actual {family} parsed native engine",
        )
        files = current.get("files")
        require(
            isinstance(files, Mapping) and set(files) == set(roles),
            f"{label} changed the closed {family} native role set",
        )
        for role, (relative, identity) in roles.items():
            item = files.get(role)
            require(
                isinstance(item, Mapping)
                and item.get("file") == relative
                and previous.valid_sha256(item.get("sha256"))
                and item.get("sha256") == fingerprints[identity],
                f"{label} did not bind its actual {family}/{role} ELF",
            )


def validate_previous_v2_report(report: Mapping[str, Any]) -> None:
    require(isinstance(report, Mapping), "the historical strict V2 proof is not an object")
    exact: dict[str, Any] = {
        "schema": PREVIOUS_STRICT_SCHEMA,
        "postfinal_schema": PREVIOUS_STRICT_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "audit_source_path": PREVIOUS_STRICT_SOURCE_RELATIVE,
        "audit_source_sha256": PREVIOUS_STRICT_SOURCE_SHA256,
        "base_audit_postfinal_schema": previous.BASE_POSTFINAL_SCHEMA,
        "base_audit_source_path": PREVIOUS_BASE_SOURCE_RELATIVE,
        "base_audit_source_sha256": PREVIOUS_BASE_SOURCE_SHA256,
        "base_audit_report_path": PREVIOUS_BASE_REPORT_RELATIVE,
        "base_audit_report_sha256": PREVIOUS_BASE_REPORT_SHA256,
        "inherited_control_count": len(previous.BASE_CONTROL_NAMES),
        "immutable_no_delegation_source_path": "tools/postfinal_no_delegation_audit_v1.py",
        "immutable_no_delegation_source_sha256": previous.IMMUTABLE_STRICT_SOURCE_SHA256,
        "immutable_no_delegation_report_path": (
            "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V1.json"
        ),
        "immutable_no_delegation_report_sha256": previous.IMMUTABLE_STRICT_REPORT_SHA256,
        "immutable_no_delegation_schema": previous.IMMUTABLE_STRICT_SCHEMA,
    }
    for field, value in exact.items():
        require(
            report.get(field) == value and type(report.get(field)) is type(value),
            f"the immutable historical strict V2 proof changed {field}",
        )
    previous.validate_controls(
        report,
        names=previous.STRICT_CONTROL_NAMES,
        label="the immutable strict V2 no-delegation proof",
    )
    inherited = report.get("inherited_self_test")
    require(isinstance(inherited, Mapping), "the strict V2 proof lost its inherited controls")
    previous.validate_controls(
        {"self_test": inherited},
        names=previous.BASE_CONTROL_NAMES,
        label="the immutable strict V2 inherited original controls",
    )
    _validate_flattened_native(report, label="the immutable strict V2 proof")
    families = report.get("families")
    require(
        isinstance(families, Mapping)
        and set(families) == set(previous.AUDITED_FAMILIES),
        "the immutable strict V2 proof lost an independent source family",
    )
    for family in previous.AUDITED_FAMILIES:
        current = families.get(family)
        require(
            isinstance(current, Mapping)
            and current.get("passed") is True
            and isinstance(current.get("isolated_runtime"), Mapping)
            and current["isolated_runtime"].get("passed") is True
            and isinstance(current.get("native_mapping_provenance"), Mapping)
            and current["native_mapping_provenance"].get("passed") is True,
            f"the immutable strict V2 proof lost guarded {family} execution",
        )
    graph = report.get("source_graph_provenance")
    scope = report.get("scope")
    require(
        isinstance(graph, Mapping)
        and graph.get("passed") is True
        and graph.get("implicit_rust_build_script_present") is False
        and graph.get("zig_build_manifest_present") is False
        and isinstance(scope, Mapping)
        and scope.get("closed_owned_source_graph") is True
        and scope.get("mapped_binaries_hashed_against_static_elf") is True
        and scope.get("persistent_measurement_worker_available") is True
        and scope.get("immutable_v1_source_preserved") is True
        and scope.get("immutable_v1_reports_mutated") is False
        and scope.get("base_v2_report_only") is True
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_or_case_fixture_access") is False,
        "the immutable strict V2 proof weakened source, mapping, or isolation safety",
    )


def validated_v3_base() -> tuple[dict[str, Any], str, str]:
    base, base_digest = public_document(BASE_V3_REPORT)
    validate_base_report(base)
    _base_source, base_source_digest = bounded_public_bytes(
        BASE_V3_SOURCE,
        maximum=MAX_SOURCE_BYTES,
    )
    require(
        base.get("audit_source_sha256") == base_source_digest,
        "the V3 base proof is not bound to its actual independently authored source",
    )
    _old_base_source, old_base_source_digest = bounded_public_bytes(
        ROOT / PREVIOUS_BASE_SOURCE_RELATIVE,
        maximum=MAX_SOURCE_BYTES,
    )
    old_base, old_base_digest = public_document(ROOT / PREVIOUS_BASE_REPORT_RELATIVE)
    require(
        old_base_source_digest == PREVIOUS_BASE_SOURCE_SHA256
        and old_base_digest == PREVIOUS_BASE_REPORT_SHA256,
        "the immutable V2 from-scratch source or report was modified",
    )
    previous.validate_base_report(old_base)
    original, original_digest = public_document(previous.ORIGINAL_BASE_REPORT)
    require(
        original_digest == previous.ORIGINAL_BASE_REPORT_SHA256
        and original.get("schema_version") == 1
        and original.get("audit") == "bounded-from-scratch-engine-provenance"
        and original.get("passed") is True
        and original.get("result") == "PASS",
        "the immutable original from-scratch evidence was modified",
    )
    _original_source, original_source_digest = bounded_public_bytes(
        previous.ORIGINAL_BASE_SOURCE,
        maximum=MAX_SOURCE_BYTES,
    )
    require(
        original_source_digest == previous.ORIGINAL_BASE_SOURCE_SHA256,
        "the immutable original 76-control audit source was modified",
    )
    return base, base_digest, base_source_digest


def run_audit() -> dict[str, Any]:
    """Explicitly rerun genuine immutable guards against current V3 sources."""

    require_candidate_free()
    verify_pinned_runtime()
    base, base_digest, base_source_digest = validated_v3_base()

    immutable, immutable_digest = public_document(previous.IMMUTABLE_STRICT_REPORT)
    previous.validate_immutable_strict_report_digest(immutable_digest)
    previous.validate_strict_controls(immutable)

    _v2_source, v2_source_digest = bounded_public_bytes(
        ROOT / PREVIOUS_STRICT_SOURCE_RELATIVE,
        maximum=MAX_SOURCE_BYTES,
    )
    require(
        v2_source_digest == PREVIOUS_STRICT_SOURCE_SHA256,
        "the immutable strict V2 audit source was modified",
    )
    predecessor, predecessor_digest = public_document(
        ROOT / PREVIOUS_STRICT_REPORT_RELATIVE
    )
    require(
        predecessor_digest == PREVIOUS_STRICT_REPORT_SHA256,
        "the immutable strict V2 audit report was modified",
    )
    validate_previous_v2_report(predecessor)

    strict = previous.import_pinned_strict_v1()
    controls = strict.self_test()
    previous.validate_controls(
        {"self_test": controls},
        names=previous.STRICT_CONTROL_NAMES,
        label="the actual immutable 32-control V3 no-delegation self-test",
    )
    require(
        controls.get("candidate_imported") is False
        and controls.get("benchmark_or_timing_executed") is False
        and controls.get("holdout_or_case_fixture_access") is False,
        "the immutable strict controls unexpectedly executed candidate or timing work",
    )
    require_candidate_free()

    previous_loader = strict._load_original_report
    previous_report = strict.original.REPORT
    require(
        isinstance(previous_report, Path)
        and previous_report.resolve() == previous.ORIGINAL_BASE_REPORT.resolve(),
        "the immutable original worker report was already rebound",
    )

    def load_verified_v3_base() -> tuple[dict[str, Any], str]:
        current, current_digest = public_document(BASE_V3_REPORT)
        require(
            current_digest == base_digest and current == base,
            "the independently authenticated V3 base changed during verification",
        )
        validate_base_report(current)
        return current, current_digest

    strict._load_original_report = load_verified_v3_base
    strict.original.REPORT = BASE_V3_REPORT
    try:
        result = strict.run_audit()
    finally:
        strict.original.REPORT = previous_report
        strict._load_original_report = previous_loader
    require_candidate_free()

    require(
        isinstance(result, dict)
        and result.get("schema") == previous.IMMUTABLE_STRICT_SCHEMA
        and result.get("passed") is True
        and result.get("result") == "PASS"
        and result.get("inherited_control_count") == len(previous.BASE_CONTROL_NAMES),
        "the immutable guarded worker did not genuinely complete against the V3 base",
    )
    previous.validate_controls(
        result,
        names=previous.STRICT_CONTROL_NAMES,
        label="the actual V3 immutable 32-control no-delegation result",
    )
    inherited = result.get("inherited_self_test")
    require(isinstance(inherited, Mapping), "the V3 result omitted inherited controls")
    previous.validate_controls(
        {"self_test": inherited},
        names=previous.BASE_CONTROL_NAMES,
        label="the actual V3 independently rerun original 76 controls",
    )
    require(
        result.get("base_audit_report_path") == BASE_V3_REPORT_RELATIVE
        and result.get("base_audit_report_sha256") == base_digest,
        "the immutable worker did not consume the authenticated current V3 base",
    )
    graph = result.get("source_graph_provenance")
    scope = result.get("scope")
    require(
        isinstance(graph, Mapping)
        and graph.get("passed") is True
        and graph.get("implicit_rust_build_script_present") is False
        and graph.get("zig_build_manifest_present") is False
        and isinstance(scope, Mapping)
        and scope.get("explicit_source_paths_only") is True
        and scope.get("closed_owned_source_graph") is True
        and scope.get("mapped_binaries_hashed_against_static_elf") is True
        and scope.get("persistent_measurement_worker_available") is True
        and scope.get("candidate_imports") == "isolated guarded subprocesses only"
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_or_case_fixture_access") is False,
        "the actual V3 source graph, ELF mapping, or worker isolation is unsafe",
    )
    previous._verify_result_native(result, base)
    _validate_flattened_native(result, label="the actual V3 strict independence proof")

    _wrapper, wrapper_digest = bounded_public_bytes(SOURCE, maximum=MAX_SOURCE_BYTES)
    _immutable_source, immutable_source_digest = bounded_public_bytes(
        previous.IMMUTABLE_STRICT_SOURCE,
        maximum=MAX_SOURCE_BYTES,
    )
    require(
        immutable_source_digest == previous.IMMUTABLE_STRICT_SOURCE_SHA256,
        "the immutable V1 strict source changed during V3 execution",
    )
    immutable_controls = result["self_test"]
    result.update(
        {
            "schema": SCHEMA,
            "postfinal_schema": SCHEMA,
            "status": "PASS",
            "result": "PASS",
            "passed": True,
            "audit_source_path": SOURCE_RELATIVE,
            "audit_source_sha256": wrapper_digest,
            "base_audit_source_path": BASE_V3_SOURCE_RELATIVE,
            "base_audit_source_sha256": base_source_digest,
            "base_audit_report_path": BASE_V3_REPORT_RELATIVE,
            "base_audit_report_sha256": base_digest,
            "base_audit_postfinal_schema": BASE_POSTFINAL_SCHEMA,
            "previous_v2_audit_source_path": PREVIOUS_STRICT_SOURCE_RELATIVE,
            "previous_v2_audit_source_sha256": v2_source_digest,
            "previous_v2_audit_report_path": PREVIOUS_STRICT_REPORT_RELATIVE,
            "previous_v2_audit_report_sha256": predecessor_digest,
            "immutable_no_delegation_source_path": (
                "tools/postfinal_no_delegation_audit_v1.py"
            ),
            "immutable_no_delegation_source_sha256": immutable_source_digest,
            "immutable_no_delegation_report_path": (
                "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V1.json"
            ),
            "immutable_no_delegation_report_sha256": immutable_digest,
            "immutable_no_delegation_schema": previous.IMMUTABLE_STRICT_SCHEMA,
            "immutable_control_source_schema": immutable_controls.get("schema"),
            "scope": {
                **dict(scope),
                "immutable_v1_source_preserved": True,
                "immutable_v1_reports_mutated": False,
                "immutable_v2_reports_mutated": False,
                "base_v3_report_only": True,
                "production_report_path": REPORT_RELATIVE,
            },
            "supersedes": {
                "schema": PREVIOUS_STRICT_SCHEMA,
                "source_path": PREVIOUS_STRICT_SOURCE_RELATIVE,
                "source_sha256": v2_source_digest,
                "report_path": PREVIOUS_STRICT_REPORT_RELATIVE,
                "report_sha256": predecessor_digest,
                "report_preserved": True,
            },
            "immutable_v1_provenance": {
                "schema": previous.IMMUTABLE_STRICT_SCHEMA,
                "source_path": "tools/postfinal_no_delegation_audit_v1.py",
                "source_sha256": immutable_source_digest,
                "report_path": (
                    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V1.json"
                ),
                "report_sha256": immutable_digest,
                "report_preserved": True,
            },
        }
    )
    require_candidate_free()
    return result


def _directory_fsync(path: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0)
    descriptor = os.open(path, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def validate_destination_relative(relative: Any) -> str:
    require(
        isinstance(relative, str) and relative == REPORT_RELATIVE,
        "only the one new V3 strict evidence path may ever be created",
    )
    return relative


def write_report(report: Mapping[str, Any], output: Path) -> str:
    require(
        isinstance(output, Path)
        and output.resolve() == REPORT.resolve()
        and output.parent.resolve() == (ROOT / "candidates" / "audits").resolve()
        and not output.is_symlink(),
        "only the exact new V3 strict evidence path may ever be created",
    )
    validate_destination_relative(REPORT_RELATIVE)
    exact: dict[str, Any] = {
        "schema": SCHEMA,
        "postfinal_schema": SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "audit_source_path": SOURCE_RELATIVE,
        "base_audit_source_path": BASE_V3_SOURCE_RELATIVE,
        "base_audit_report_path": BASE_V3_REPORT_RELATIVE,
        "base_audit_postfinal_schema": BASE_POSTFINAL_SCHEMA,
        "previous_v2_audit_source_path": PREVIOUS_STRICT_SOURCE_RELATIVE,
        "previous_v2_audit_source_sha256": PREVIOUS_STRICT_SOURCE_SHA256,
        "previous_v2_audit_report_path": PREVIOUS_STRICT_REPORT_RELATIVE,
        "previous_v2_audit_report_sha256": PREVIOUS_STRICT_REPORT_SHA256,
        "inherited_control_count": len(previous.BASE_CONTROL_NAMES),
    }
    require(isinstance(report, Mapping), "a V3 production report must be an object")
    for field, value in exact.items():
        require(
            report.get(field) == value and type(report.get(field)) is type(value),
            f"refusing to publish incomplete or historical V3 evidence: {field}",
        )
    for field in (
        "audit_source_sha256",
        "base_audit_source_sha256",
        "base_audit_report_sha256",
        "immutable_no_delegation_source_sha256",
        "immutable_no_delegation_report_sha256",
    ):
        require(
            previous.valid_sha256(report.get(field)),
            f"refusing to publish unbound V3 evidence: {field}",
        )
    previous.validate_controls(
        report,
        names=previous.STRICT_CONTROL_NAMES,
        label="the publishable V3 strict controls",
    )
    inherited = report.get("inherited_self_test")
    require(isinstance(inherited, Mapping), "refusing to omit original V3 controls")
    previous.validate_controls(
        {"self_test": inherited},
        names=previous.BASE_CONTROL_NAMES,
        label="the publishable V3 original controls",
    )
    _validate_flattened_native(report, label="the publishable V3 native provenance")
    scope = report.get("scope")
    require(
        isinstance(scope, Mapping)
        and scope.get("base_v3_report_only") is True
        and scope.get("immutable_v1_reports_mutated") is False
        and scope.get("immutable_v2_reports_mutated") is False
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_or_case_fixture_access") is False
        and scope.get("production_report_path") == REPORT_RELATIVE,
        "refusing to publish unsafe or unbound V3 production evidence",
    )
    payload = canonical(dict(report)) + b"\n"
    require(len(payload) <= MAX_DOCUMENT_BYTES, "the V3 report exceeds its safe bound")
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_CLOEXEC", 0)
    )
    try:
        descriptor = os.open(output, flags, 0o644)
    except FileExistsError as error:
        raise AuditFailure("refusing to overwrite an existing immutable V3 report") from error
    except OSError as error:
        raise AuditFailure("cannot exclusively create the sole V3 strict report") from error
    try:
        view = memoryview(payload)
        while view:
            count = os.write(descriptor, view)
            require(count > 0, "the exclusive V3 report write made no progress")
            view = view[count:]
        os.fsync(descriptor)
        _directory_fsync(output.parent)
    except OSError as error:
        raise AuditFailure("cannot durably finish the exclusive V3 report") from error
    finally:
        os.close(descriptor)
    return hashlib.sha256(payload).hexdigest()


def _synthetic_wrapper(label: str) -> dict[str, Any]:
    records = [
        {"name": f"synthetic-{label}-control-{index:02d}", "passed": True}
        for index in range(52)
    ]
    return {
        "schema": f"rebar-postfinal-from-scratch-audit-{label}-self-test",
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "check_count": len(records),
        "checks": records,
        "failed": [],
        "fixture_storage": "in-memory only",
        "candidate_imported": False,
        "candidate_imports": [],
        "subprocesses": 0,
        "file_reads": 0,
        "file_writes": 0,
        "guard_accessed": False,
        "historical_holdout_accessed": False,
        "holdout_or_case_fixture_access": False,
        "benchmark_or_timing_executed": False,
        "production_cases_materialized": 0,
        "report_written": False,
    }


def _synthetic_v3_base() -> dict[str, Any]:
    base = previous._synthetic_base()
    base.update(
        {
            "postfinal_schema": BASE_POSTFINAL_SCHEMA,
            "status": "PASS",
            "audit_source_path": BASE_V3_SOURCE_RELATIVE,
            "audit_source_sha256": hashlib.sha256(
                b"candidate-free-synthetic-v3-base-source"
            ).hexdigest(),
            "previous_v2_audit_source_path": PREVIOUS_BASE_SOURCE_RELATIVE,
            "previous_v2_audit_source_sha256": PREVIOUS_BASE_SOURCE_SHA256,
            "previous_v2_audit_report_path": PREVIOUS_BASE_REPORT_RELATIVE,
            "previous_v2_audit_report_sha256": PREVIOUS_BASE_REPORT_SHA256,
            "postfinal_wrapper_self_test": _synthetic_wrapper("v3"),
            "previous_v2_wrapper_self_test": _synthetic_wrapper("v2"),
        }
    )
    return base


def _synthetic_previous_v2() -> dict[str, Any]:
    base = previous._synthetic_base()
    report = previous._synthetic_strict()
    native = base["native_elf_provenance"]
    fingerprints = {
        identity: native["families"][family]["files"][role]["sha256"]
        for family, roles in previous.NATIVE_ROLE_PATHS.items()
        for role, (_relative, identity) in roles.items()
    }
    report.update(
        {
            "schema": PREVIOUS_STRICT_SCHEMA,
            "postfinal_schema": PREVIOUS_STRICT_SCHEMA,
            "status": "PASS",
            "result": "PASS",
            "passed": True,
            "audit_source_path": PREVIOUS_STRICT_SOURCE_RELATIVE,
            "audit_source_sha256": PREVIOUS_STRICT_SOURCE_SHA256,
            "base_audit_postfinal_schema": previous.BASE_POSTFINAL_SCHEMA,
            "base_audit_source_path": PREVIOUS_BASE_SOURCE_RELATIVE,
            "base_audit_source_sha256": PREVIOUS_BASE_SOURCE_SHA256,
            "base_audit_report_path": PREVIOUS_BASE_REPORT_RELATIVE,
            "base_audit_report_sha256": PREVIOUS_BASE_REPORT_SHA256,
            "inherited_control_count": len(previous.BASE_CONTROL_NAMES),
            "inherited_self_test": previous._synthetic_controls(
                previous.BASE_CONTROL_NAMES
            ),
            "immutable_no_delegation_source_path": (
                "tools/postfinal_no_delegation_audit_v1.py"
            ),
            "immutable_no_delegation_source_sha256": (
                previous.IMMUTABLE_STRICT_SOURCE_SHA256
            ),
            "immutable_no_delegation_report_path": (
                "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V1.json"
            ),
            "immutable_no_delegation_report_sha256": (
                previous.IMMUTABLE_STRICT_REPORT_SHA256
            ),
            "immutable_no_delegation_schema": previous.IMMUTABLE_STRICT_SCHEMA,
            "native_elf_provenance": native,
            "native_elf_fingerprints": fingerprints,
            "families": {
                family: {
                    **current,
                    "native_mapping_provenance": {"passed": True},
                }
                for family, current in base["families"].items()
            },
            "source_graph_provenance": {
                "passed": True,
                "implicit_rust_build_script_present": False,
                "zig_build_manifest_present": False,
            },
            "scope": {
                "closed_owned_source_graph": True,
                "mapped_binaries_hashed_against_static_elf": True,
                "persistent_measurement_worker_available": True,
                "immutable_v1_source_preserved": True,
                "immutable_v1_reports_mutated": False,
                "base_v2_report_only": True,
                "benchmark_or_timing_executed": False,
                "holdout_or_case_fixture_access": False,
            },
        }
    )
    return report


def candidate_free_self_test() -> dict[str, Any]:
    """Run inherited and new V3 poison controls entirely in memory."""

    verify_pinned_runtime()
    require_candidate_free()
    inherited = previous.candidate_free_self_test()
    require(
        isinstance(inherited, Mapping)
        and inherited.get("schema") == previous.SCHEMA + "-self-test"
        and inherited.get("status") == "PASS"
        and inherited.get("result") == "PASS"
        and inherited.get("passed") is True
        and isinstance(inherited.get("checks"), list)
        and type(inherited.get("check_count")) is int
        and inherited["check_count"] >= 52
        and len(inherited["checks"]) == inherited["check_count"]
        and inherited.get("failed") == []
        and inherited.get("candidate_imports") == 0
        and inherited.get("subprocesses") == 0
        and inherited.get("file_reads") == 0
        and inherited.get("file_writes") == 0
        and inherited.get("guard_accessed") is False
        and inherited.get("historical_holdout_accessed") is False
        and inherited.get("benchmark_or_timing_executed") is False
        and inherited.get("fixture_storage") == "in-memory only",
        "the actual candidate-free V2 poison-control self-test did not pass",
    )
    checks: list[dict[str, Any]] = [
        {"name": "inherited-v2:" + record["name"], "passed": True}
        for record in inherited["checks"]
        if isinstance(record, Mapping)
        and isinstance(record.get("name"), str)
        and record.get("passed") is True
    ]
    require(
        len(checks) == inherited["check_count"],
        "the inherited V2 controls contain a missing or failing record",
    )

    def check(name: str, value: bool) -> None:
        checks.append({"name": name, "passed": bool(value)})

    def rejected(name: str, action: Callable[[], Any]) -> None:
        try:
            action()
        except (
            previous.AuditFailure,
            KeyError,
            OverflowError,
            TypeError,
            UnicodeError,
            ValueError,
        ):
            check(name, True)
        else:
            check(name, False)

    def clone(value: Any) -> Any:
        return json.loads(canonical(value))

    check("v3-schema-is-distinct-from-v1-and-v2", SCHEMA not in {previous.SCHEMA, previous.IMMUTABLE_STRICT_SCHEMA} and SCHEMA.endswith("-v3"))
    check("v3-base-schema-is-distinct-from-v2", BASE_POSTFINAL_SCHEMA != previous.BASE_POSTFINAL_SCHEMA and BASE_POSTFINAL_SCHEMA.endswith("-v3"))
    check("preserve-exact-76-original-controls", len(previous.BASE_CONTROL_NAMES) == 76)
    check("preserve-exact-32-independent-strict-controls", len(previous.STRICT_CONTROL_NAMES) == 32)
    check("preserve-four-independent-source-families", previous.AUDITED_FAMILIES == ("ast", "vm", "rust", "zig"))
    check("preserve-three-independently-implemented-native-families", previous.QUALIFIED_FAMILIES == ("vm", "rust", "zig"))
    check("preserve-exact-five-owned-native-roles", len(previous.EXPECTED_NATIVE_KEYS) == 5)
    for label, digest in (
        ("original-base-source", previous.ORIGINAL_BASE_SOURCE_SHA256),
        ("original-base-report", previous.ORIGINAL_BASE_REPORT_SHA256),
        ("immutable-v1-strict-source", previous.IMMUTABLE_STRICT_SOURCE_SHA256),
        ("immutable-v1-strict-report", previous.IMMUTABLE_STRICT_REPORT_SHA256),
        ("immutable-v2-base-source", PREVIOUS_BASE_SOURCE_SHA256),
        ("immutable-v2-base-report", PREVIOUS_BASE_REPORT_SHA256),
        ("immutable-v2-strict-source", PREVIOUS_STRICT_SOURCE_SHA256),
        ("immutable-v2-strict-report", PREVIOUS_STRICT_REPORT_SHA256),
    ):
        check("pin-" + label + "-sha256", previous.valid_sha256(digest))

    surrogate = "\ud800\n\udfff"
    encoded = canonical({"surrogate": surrogate})
    check("canonical-v3-json-is-ascii", encoded.isascii())
    check("canonical-v3-json-preserves-lone-surrogates", json.loads(encoded)["surrogate"] == surrogate)
    check("canonical-v3-json-never-contains-an-unescaped-newline", b"\n" not in encoded)
    rejected("reject-v3-nan-evidence", lambda: canonical({"value": float("nan")}))
    rejected("reject-v3-positive-infinity-evidence", lambda: canonical({"value": float("inf")}))
    rejected("reject-v3-negative-infinity-evidence", lambda: canonical({"value": float("-inf")}))
    rejected("reject-v3-non-json-bytes", lambda: canonical({"value": b"unsafe"}))
    rejected("reject-v3-duplicate-json-keys", lambda: decode_public_json(b'{"same":1,"same":2}'))
    rejected("reject-v3-json-nan-token", lambda: decode_public_json(b'{"value":NaN}'))
    rejected("reject-v3-json-infinity-token", lambda: decode_public_json(b'{"value":Infinity}'))
    rejected("reject-v3-json-negative-infinity-token", lambda: decode_public_json(b'{"value":-Infinity}'))
    rejected("reject-v3-invalid-utf8-json", lambda: decode_public_json(b'{"value":"\xff"}'))
    rejected("reject-v3-json-top-level-list", lambda: decode_public_json(b"[]"))

    base = _synthetic_v3_base()
    sources = validate_base_report(base)
    check("accept-only-complete-synthetic-four-family-v3-base", set(sources) == set(previous.AUDITED_FAMILIES))
    predecessor = _synthetic_previous_v2()
    validate_previous_v2_report(predecessor)
    check("accept-only-complete-synthetic-immutable-strict-v2", True)
    immutable = previous._synthetic_strict()
    previous.validate_strict_controls(immutable)
    check("preserve-all-real-immutable-v1-strict-validation", True)

    def reject_base(name: str, mutate: Callable[[dict[str, Any]], None]) -> None:
        poisoned = clone(base)
        mutate(poisoned)
        rejected(name, lambda: validate_base_report(poisoned))

    for field, poison in (
        ("schema_version", 2),
        ("audit", "external-regex-wrapper"),
        ("postfinal_schema", previous.BASE_POSTFINAL_SCHEMA),
        ("status", "FAIL"),
        ("result", "FAIL"),
        ("passed", False),
        ("audit_source_path", PREVIOUS_BASE_SOURCE_RELATIVE),
        ("audit_source_sha256", "invalid"),
        ("original_audit_source_path", BASE_V3_SOURCE_RELATIVE),
        ("original_audit_source_sha256", "0" * 64),
        ("original_v1_audit_report_path", BASE_V3_REPORT_RELATIVE),
        ("original_v1_audit_report_sha256", "0" * 64),
        ("previous_v2_audit_source_path", BASE_V3_SOURCE_RELATIVE),
        ("previous_v2_audit_source_sha256", "0" * 64),
        ("previous_v2_audit_report_path", BASE_V3_REPORT_RELATIVE),
        ("previous_v2_audit_report_sha256", "0" * 64),
        ("verified_core_family_count", 2),
        ("verified_distinct_pipeline_count", 3),
    ):
        reject_base(
            "reject-poisoned-v3-base-" + field.replace("_", "-"),
            lambda value, field=field, poison=poison: value.update({field: poison}),
        )
    reject_base("reject-omitted-v3-wrapper-controls", lambda value: value.pop("postfinal_wrapper_self_test"))
    for field, poison in (
        ("passed", False),
        ("result", "FAIL"),
        ("check_count", 51),
        ("failed", ["external-engine"]),
        ("fixture_storage", "disk"),
        ("candidate_imports", 1),
        ("subprocesses", 1),
        ("file_reads", 1),
        ("file_writes", 1),
        ("guard_accessed", True),
        ("historical_holdout_accessed", True),
        ("benchmark_or_timing_executed", True),
    ):
        reject_base(
            "reject-v3-wrapper-" + field.replace("_", "-"),
            lambda value, field=field, poison=poison: value[
                "postfinal_wrapper_self_test"
            ].update({field: poison}),
        )
    reject_base(
        "reject-one-failing-v3-wrapper-control",
        lambda value: value["postfinal_wrapper_self_test"]["checks"][0].update(
            {"passed": False}
        ),
    )
    reject_base(
        "reject-duplicate-v3-wrapper-control",
        lambda value: value["postfinal_wrapper_self_test"]["checks"][0].update(
            {
                "name": value["postfinal_wrapper_self_test"]["checks"][1][
                    "name"
                ]
            }
        ),
    )
    reject_base(
        "reject-poisoned-historical-v2-wrapper",
        lambda value: value["previous_v2_wrapper_self_test"].update(
            {"file_reads": 1}
        ),
    )
    reject_base(
        "reject-one-omitted-original-v3-control",
        lambda value: value["self_test"]["checks"].pop(),
    )
    reject_base(
        "reject-one-failing-original-v3-control",
        lambda value: value["self_test"]["checks"][0].update({"passed": False}),
    )
    reject_base(
        "reject-renamed-original-v3-control",
        lambda value: value["self_test"]["checks"][0].update(
            {"name": "external-package-wrapper"}
        ),
    )
    reject_base(
        "reject-external-or-shared-v3-source-family",
        lambda value: value["families"].update(
            {"external-regex-wrapper": {"passed": True}}
        ),
    )
    for family in previous.AUDITED_FAMILIES:
        reject_base(
            "reject-omitted-v3-independent-family:" + family,
            lambda value, family=family: value["families"].pop(family),
        )
        reject_base(
            "reject-substituted-v3-owned-source:" + family,
            lambda value, family=family: value["families"][family][
                "python_source"
            ].update({"sha256": "invalid"}),
        )
        reject_base(
            "reject-failing-v3-guarded-family:" + family,
            lambda value, family=family: value["families"][family][
                "isolated_runtime"
            ].update({"passed": False}),
        )
    for family, roles in previous.NATIVE_ROLE_PATHS.items():
        for role in roles:
            reject_base(
                "reject-omitted-v3-owned-native-role:" + family + "/" + role,
                lambda value, family=family, role=role: value[
                    "native_elf_provenance"
                ]["families"][family]["files"].pop(role),
            )
            reject_base(
                "reject-substituted-v3-owned-native-role:" + family + "/" + role,
                lambda value, family=family, role=role: value[
                    "native_elf_provenance"
                ]["families"][family]["files"][role].update(
                    {"sha256": "invalid"}
                ),
            )
    reject_base(
        "reject-foreign-v3-native-role",
        lambda value: value["native_elf_provenance"]["families"]["rust"][
            "files"
        ].update(
            {
                "external-regex": {
                    "file": "site-packages/regex.so",
                    "sha256": "0" * 64,
                }
            }
        ),
    )
    reject_base(
        "reject-v3-native-runtime-mapping-bypass",
        lambda value: value["runtime_native_mapping_provenance"].update(
            {"passed": False}
        ),
    )
    for field, poison in (
        ("mapped_binaries_hashed_against_static_elf", False),
        ("holdout_or_case_fixture_access", True),
        ("benchmark_or_timing_executed", True),
    ):
        reject_base(
            "reject-v3-base-scope-" + field.replace("_", "-"),
            lambda value, field=field, poison=poison: value["scope"].update(
                {field: poison}
            ),
        )

    def reject_previous(
        name: str,
        mutate: Callable[[dict[str, Any]], None],
    ) -> None:
        poisoned = clone(predecessor)
        mutate(poisoned)
        rejected(name, lambda: validate_previous_v2_report(poisoned))

    for field, poison in (
        ("schema", previous.IMMUTABLE_STRICT_SCHEMA),
        ("postfinal_schema", SCHEMA),
        ("status", "FAIL"),
        ("result", "FAIL"),
        ("passed", False),
        ("audit_source_path", SOURCE_RELATIVE),
        ("audit_source_sha256", "0" * 64),
        ("base_audit_postfinal_schema", BASE_POSTFINAL_SCHEMA),
        ("base_audit_source_path", BASE_V3_SOURCE_RELATIVE),
        ("base_audit_source_sha256", "0" * 64),
        ("base_audit_report_path", BASE_V3_REPORT_RELATIVE),
        ("base_audit_report_sha256", "0" * 64),
        ("inherited_control_count", 75),
        ("immutable_no_delegation_source_path", SOURCE_RELATIVE),
        ("immutable_no_delegation_source_sha256", "0" * 64),
        ("immutable_no_delegation_report_path", REPORT_RELATIVE),
        ("immutable_no_delegation_report_sha256", "0" * 64),
        ("immutable_no_delegation_schema", SCHEMA),
    ):
        reject_previous(
            "reject-poisoned-immutable-strict-v2-" + field.replace("_", "-"),
            lambda value, field=field, poison=poison: value.update({field: poison}),
        )
    reject_previous(
        "reject-omitted-immutable-v2-strict-control",
        lambda value: value["self_test"]["checks"].pop(),
    )
    reject_previous(
        "reject-failing-immutable-v2-strict-control",
        lambda value: value["self_test"]["checks"][0].update({"passed": False}),
    )
    reject_previous(
        "reject-omitted-immutable-v2-inherited-control",
        lambda value: value["inherited_self_test"]["checks"].pop(),
    )
    for family, roles in previous.NATIVE_ROLE_PATHS.items():
        for role, (_relative, identity) in roles.items():
            reject_previous(
                "reject-omitted-immutable-v2-native-role:" + family + "/" + role,
                lambda value, identity=identity: value[
                    "native_elf_fingerprints"
                ].pop(identity),
            )
            reject_previous(
                "reject-substituted-immutable-v2-native-role:"
                + family
                + "/"
                + role,
                lambda value, identity=identity: value[
                    "native_elf_fingerprints"
                ].update({identity: "0" * 64}),
            )
    reject_previous(
        "reject-immutable-v2-external-native-engine",
        lambda value: value["native_elf_fingerprints"].update(
            {"third_party.regex:native-engine": "0" * 64}
        ),
    )
    for field, poison in (
        ("closed_owned_source_graph", False),
        ("mapped_binaries_hashed_against_static_elf", False),
        ("persistent_measurement_worker_available", False),
        ("immutable_v1_source_preserved", False),
        ("immutable_v1_reports_mutated", True),
        ("base_v2_report_only", False),
        ("benchmark_or_timing_executed", True),
        ("holdout_or_case_fixture_access", True),
    ):
        reject_previous(
            "reject-immutable-v2-unsafe-scope-" + field.replace("_", "-"),
            lambda value, field=field, poison=poison: value["scope"].update(
                {field: poison}
            ),
        )

    for relative in sorted(PUBLIC_INPUTS):
        check(
            "allow-only-explicit-public-input:" + relative,
            validate_public_relative(relative) == relative,
        )
    for name, relative in (
        ("private-holdout", "benchmarks/private/holdout.json"),
        ("benchmark-data", "benchmarks/results/timings.json"),
        ("final-measurements", "candidates/evidence/final.json"),
        ("user-failure-evidence", "candidates/evidence/rust-v8-native-expand-direct-replacement-controls-failures.json"),
        ("third-party-engine", "site-packages/regex/__init__.py"),
        ("root-escape", "../holdout.json"),
        ("absolute-path", "/tmp/holdout.json"),
        ("production-output-as-input", REPORT_RELATIVE),
    ):
        rejected(
            "reject-unapproved-v3-input:" + name,
            lambda relative=relative: validate_public_relative(relative),
        )
    check(
        "accept-only-exact-additive-v3-output-path",
        validate_destination_relative(REPORT_RELATIVE) == REPORT_RELATIVE,
    )
    for name, relative in (
        ("immutable-v1-base", "candidates/audits/FROM-SCRATCH-AUDIT.json"),
        ("immutable-v1-strict", "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V1.json"),
        ("immutable-v2-base", PREVIOUS_BASE_REPORT_RELATIVE),
        ("immutable-v2-strict", PREVIOUS_STRICT_REPORT_RELATIVE),
        ("current-base", BASE_V3_REPORT_RELATIVE),
        ("private-holdout", "benchmarks/private/holdout.json"),
        ("absolute-path", "/tmp/evidence.json"),
    ):
        rejected(
            "reject-v3-report-overwrite:" + name,
            lambda relative=relative: validate_destination_relative(relative),
        )

    require_candidate_free()
    names = [record["name"] for record in checks]
    require(len(names) == len(set(names)), "V3 self-test control names are not unique")
    failed = [record["name"] for record in checks if not record["passed"]]
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS" if not failed else "FAIL",
        "result": "PASS" if not failed else "FAIL",
        "passed": not failed,
        "check_count": len(checks),
        "checks": checks,
        "failed": failed,
        "inherited_v2_check_count": inherited["check_count"],
        "immutable_no_delegation_controls": len(previous.STRICT_CONTROL_NAMES),
        "inherited_original_controls": len(previous.BASE_CONTROL_NAMES),
        "independent_families": list(previous.AUDITED_FAMILIES),
        "owned_native_roles": len(previous.EXPECTED_NATIVE_KEYS),
        "candidate_imports": 0,
        "subprocesses": 0,
        "file_reads": 0,
        "file_writes": 0,
        "production_cases_materialized": 0,
        "guard_accessed": False,
        "historical_holdout_accessed": False,
        "benchmark_or_timing_executed": False,
        "fixture_storage": "in-memory only",
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_mutually_exclusive_group(required=True)
    commands.add_argument(
        "--self-test",
        action="store_true",
        help="run only deterministic in-memory candidate-free V3 poison controls",
    )
    commands.add_argument(
        "--audit",
        action="store_true",
        help="explicitly verify the V3 source graph in independently guarded workers",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPORT,
        help="the sole authorized new strict V3 evidence path",
    )
    args = parser.parse_args(arguments)
    try:
        require_candidate_free()
        if args.self_test:
            require(
                args.output == REPORT,
                "the in-memory V3 self-test does not accept a report destination",
            )
            report = candidate_free_self_test()
            sys.stdout.buffer.write(canonical(report) + b"\n")
            return 0 if report.get("passed") is True else 1
        report = run_audit()
        digest = write_report(report, args.output)
        summary = {
            "schema": SCHEMA,
            "postfinal_schema": SCHEMA,
            "status": "PASS",
            "result": "PASS",
            "passed": True,
            "report": REPORT_RELATIVE,
            "report_sha256": digest,
            "audit_source_sha256": report["audit_source_sha256"],
            "base_audit_report_path": report["base_audit_report_path"],
            "base_audit_report_sha256": report["base_audit_report_sha256"],
            "previous_v2_audit_report_sha256": report[
                "previous_v2_audit_report_sha256"
            ],
            "self_test_checks": len(previous.STRICT_CONTROL_NAMES),
            "inherited_self_test_checks": len(previous.BASE_CONTROL_NAMES),
            "verified_family_count": len(report["families"]),
            "verified_native_library_count": len(report["native_elf_fingerprints"]),
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
            "immutable_v1_reports_mutated": False,
            "immutable_v2_reports_mutated": False,
        }
        sys.stdout.buffer.write(canonical(summary) + b"\n")
        return 0
    except (
        previous.AuditFailure,
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
        KeyError,
    ) as error:
        failure = {
            "schema": SCHEMA if args.audit else SCHEMA + "-self-test",
            "status": "FAIL",
            "result": "FAIL",
            "passed": False,
            "error": str(error),
            "candidate_imported": False,
            "guard_accessed": False,
            "historical_holdout_accessed": False,
            "benchmark_or_timing_executed": False,
        }
        sys.stdout.buffer.write(canonical(failure) + b"\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
