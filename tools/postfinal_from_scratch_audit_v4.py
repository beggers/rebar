#!/usr/bin/env python3
"""Additively audit live owned engines without changing V1, V2, or V3."""

from __future__ import annotations

import argparse
import copy
import gc
import hashlib
import os
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
import stat
import sys
from typing import Any, Iterator, Mapping


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import postfinal_from_scratch_audit_v3 as previous


SCHEMA = "rebar-postfinal-from-scratch-audit-v4"
SOURCE_RELATIVE = "tools/postfinal_from_scratch_audit_v4.py"
SOURCE_PATH = ROOT / SOURCE_RELATIVE
REPORT_RELATIVE = "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V4.json"
REPORT_PATH = ROOT / REPORT_RELATIVE
PREVIOUS_SOURCE_SHA256 = (
    "d8230d1f0272bffc6ef2fb61136935047a4d4008afd8a66291c87c48b7a36767"
)
PREVIOUS_REPORT_SHA256 = (
    "f1a1f2402819d85d0d9135b0fc2b89aecd2212bb3259700bf7628cb881a32f05"
)
RUST_SOURCE_RELATIVE = "candidates/rust/src/lib.rs"
ALLOWED_LOCALE_LIBC_PRIMITIVES = frozenset({"isalnum", "tolower"})
MINIMUM_PREVIOUS_CONTROLS = 129
MAX_SOURCE_BYTES = previous.MAX_SOURCE_BYTES
MAX_REPORT_BYTES = previous.MAX_REPORT_BYTES


class AuditV4Error(previous.AuditV3Error):
    """A current V4 audit, provenance check, or exclusive slot failed."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise AuditV4Error(message)


def destination_name(value: Any) -> str:
    require(type(value) is str, "the exclusive V4 destination is not text")
    path = PurePosixPath(value)
    require(
        not path.is_absolute()
        and ".." not in path.parts
        and "\\" not in value
        and "\x00" not in value
        and str(path) == value
        and value == REPORT_RELATIVE,
        "only the exact canonical exclusive V4 source-audit report is authorized",
    )
    return value


@contextmanager
def allow_owned_rust_locale_ctype() -> Iterator[None]:
    """Temporarily accept exactly two libc primitives in the owned Rust root."""

    original = previous.original
    inherited = original.analyze_native
    require(
        callable(inherited)
        and getattr(inherited, "__module__", None) == original.__name__
        and getattr(inherited, "__name__", None) == "analyze_native",
        "the immutable native source analyzer was already replaced",
    )

    def narrowed(source: str, path: str, family: str) -> dict[str, Any]:
        result = inherited(source, path, family)
        if family != "rust" or path != RUST_SOURCE_RELATIVE:
            return result
        issues = result.get("issues")
        require(isinstance(issues, list), "the immutable Rust analyzer changed its findings")
        retained = [
            item
            for item in issues
            if not (
                isinstance(item, dict)
                and item.get("file") == RUST_SOURCE_RELATIVE
                and item.get("code") == "unowned_rust_extern"
                and item.get("detail") in ALLOWED_LOCALE_LIBC_PRIMITIVES
            )
        ]
        if len(retained) == len(issues):
            return result
        return {**result, "issues": retained, "passed": not retained}

    original.analyze_native = narrowed
    try:
        yield
    finally:
        original.analyze_native = inherited


def validate_v4_controls(document: Any) -> dict[str, Any]:
    require(isinstance(document, dict), "the V4 in-memory controls are missing")
    checks = document.get("checks")
    count = document.get("check_count")
    require(
        document.get("schema") == SCHEMA + "-self-test"
        and document.get("passed") is True
        and document.get("status") == "PASS"
        and document.get("result") == "PASS"
        and type(count) is int
        and count >= MINIMUM_PREVIOUS_CONTROLS
        and isinstance(checks, list)
        and len(checks) == count
        and all(
            isinstance(item, dict)
            and isinstance(item.get("name"), str)
            and item.get("passed") is True
            for item in checks
        )
        and len({item["name"] for item in checks}) == count
        and document.get("failed") == []
        and document.get("fixture_storage") == "in-memory only"
        and document.get("candidate_imported") is False
        and document.get("file_reads") == 0
        and document.get("file_writes") == 0
        and document.get("subprocesses") == 0
        and document.get("clock_samples") == 0
        and document.get("production_entropy_drawn") is False
        and document.get("holdout_or_case_fixture_access") is False
        and document.get("benchmark_or_timing_executed") is False
        and document.get("production_cases_materialized") == 0
        and document.get("report_written") is False,
        "the V4 controls are incomplete, duplicated, unsafe, or weakened",
    )
    previous.validate_wrapper_controls(
        document.get("inherited_v3_self_test"),
        schema=previous.SCHEMA,
        minimum=MINIMUM_PREVIOUS_CONTROLS,
    )
    return document


def validate_v4_report(document: Any, *, label: str) -> dict[str, Any]:
    require(isinstance(document, dict), f"{label} is not a source-audit object")
    expected = {
        "schema_version": 1,
        "audit": previous.AUDIT_NAME,
        "postfinal_schema": SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "audit_source_path": SOURCE_RELATIVE,
        "previous_v3_audit_source_path": previous.SOURCE_RELATIVE,
        "previous_v3_audit_source_sha256": PREVIOUS_SOURCE_SHA256,
        "previous_v3_audit_report_path": previous.REPORT_RELATIVE,
        "previous_v3_audit_report_sha256": PREVIOUS_REPORT_SHA256,
        "previous_v3_postfinal_schema": previous.SCHEMA,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
    }
    for name, value in expected.items():
        require(
            document.get(name) == value and type(document.get(name)) is type(value),
            f"{label} substituted its exact V4 or immutable V3 {name}",
        )
    require(
        previous.valid_sha256(document.get("audit_source_sha256"))
        and document.get("v4_allowed_rust_libc_primitives")
        == sorted(ALLOWED_LOCALE_LIBC_PRIMITIVES),
        f"{label} omitted its actual V4 source or exact libc ctype allowance",
    )
    controls = validate_v4_controls(document.get("postfinal_wrapper_self_test"))
    previous_controls = document.get("previous_v3_wrapper_self_test")
    previous.validate_wrapper_controls(
        previous_controls,
        schema=previous.SCHEMA,
        minimum=MINIMUM_PREVIOUS_CONTROLS,
    )
    require(
        previous_controls == controls["inherited_v3_self_test"],
        f"{label} substituted its live complete V3 wrapper controls",
    )
    scope = document.get("postfinal_scope")
    require(
        isinstance(scope, dict)
        and scope.get("append_only") is True
        and scope.get("exclusive_report_path") == REPORT_RELATIVE
        and scope.get("original_v1_report_preserved") is True
        and scope.get("previous_v2_report_preserved") is True
        and scope.get("previous_v3_report_preserved") is True
        and scope.get("original_main_invoked") is False
        and scope.get("full_original_audit_rerun") is True
        and scope.get("original_synthetic_controls_rerun") == 76
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_or_case_fixture_access") is False,
        f"{label} weakened its exact append-only V4 production scope",
    )
    adapted = dict(document)
    adapted.update(
        {
            "postfinal_schema": previous.SCHEMA,
            "audit_source_path": previous.SOURCE_RELATIVE,
            "audit_source_sha256": PREVIOUS_SOURCE_SHA256,
            "postfinal_wrapper_self_test": previous_controls,
            "postfinal_scope": {
                "append_only": True,
                "exclusive_report_path": previous.REPORT_RELATIVE,
                "original_v1_report_preserved": True,
                "previous_v2_report_preserved": True,
                "original_main_invoked": False,
                "full_original_audit_rerun": True,
                "original_synthetic_controls_rerun": 76,
                "benchmark_or_timing_executed": False,
                "holdout_or_case_fixture_access": False,
            },
        }
    )
    previous.validate_v3_report(adapted, label=label + " inherited V3 proof")
    return document


def self_test() -> dict[str, Any]:
    previous.ensure_candidate_free()
    effects = previous.previous.BlockSelfTestEffects()
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: Any) -> None:
        checks.append({"name": name, "passed": bool(condition)})

    def rejected(name: str, operation: Any) -> None:
        try:
            operation()
        except (previous.AuditV3Error, TypeError, ValueError, KeyError, UnicodeError):
            check(name, True)
        else:
            check(name, False)

    with effects:
        inherited = previous.self_test()
        previous.validate_wrapper_controls(
            inherited,
            schema=previous.SCHEMA,
            minimum=MINIMUM_PREVIOUS_CONTROLS,
        )
        for item in inherited["checks"]:
            check("v3:" + item["name"], item["passed"] is True)
        check("preserve-exact-original-76-controls", inherited["inherited_control_count"] == 76)
        check("preserve-at-least-129-v3-controls", inherited["check_count"] >= 129)
        check("pin-exact-v3-source-fingerprint", previous.valid_sha256(PREVIOUS_SOURCE_SHA256))
        check("pin-exact-v3-report-fingerprint", previous.valid_sha256(PREVIOUS_REPORT_SHA256))
        check("preserve-four-source-families", previous.FAMILIES == ("ast", "vm", "rust", "zig"))
        check("preserve-three-native-families", previous.NATIVE_FAMILIES == ("vm", "rust", "zig"))
        check("preserve-five-native-roles", sum(map(len, previous.EXPECTED_NATIVE_PATHS.values())) == 5)
        check("allow-only-two-owned-libc-ctype-primitives", ALLOWED_LOCALE_LIBC_PRIMITIVES == frozenset({"tolower", "isalnum"}))

        original = previous.original
        clean_source = 'unsafe extern "C" { fn tolower(x: i32) -> i32; fn isalnum(x: i32) -> i32; }'
        rejected_before = original.analyze_native(clean_source, RUST_SOURCE_RELATIVE, "rust")
        check(
            "immutable-v1-explicitly-rejects-locale-ctype-before-v4-adaptation",
            rejected_before["passed"] is False
            and {
                item.get("detail")
                for item in rejected_before["issues"]
                if item.get("code") == "unowned_rust_extern"
            }
            == ALLOWED_LOCALE_LIBC_PRIMITIVES,
        )
        saved = original.analyze_native
        with allow_owned_rust_locale_ctype():
            check(
                "accept-only-exact-owned-rust-libc-locale-primitives",
                original.analyze_native(clean_source, RUST_SOURCE_RELATIVE, "rust")["passed"],
            )
            for foreign in (
                "pcre2_match",
                "regexec",
                "rebar_zig_compile",
                "rebar_zig_match_wide",
                "innocent_engine_match",
                "dlopen",
                "system",
            ):
                hostile = (
                    'unsafe extern "C" { fn tolower(x: i32) -> i32; '
                    f"fn {foreign}(); "
                    "}"
                )
                check(
                    "reject-locale-ctype-plus-foreign-extern:" + foreign,
                    not original.analyze_native(hostile, RUST_SOURCE_RELATIVE, "rust")["passed"],
                )
            for path, family, fixture in (
                ("candidates/rust/src/search.rs", "rust", clean_source),
                (
                    "candidates/zig/mini_regex.zig",
                    "zig",
                    "extern fn tolower(x: c_int) c_int;",
                ),
                (RUST_SOURCE_RELATIVE, "vm", clean_source),
            ):
                check(
                    "reject-locale-ctype-outside-owned-rust-root:" + family + ":" + path,
                    not original.analyze_native(fixture, path, family)["passed"],
                )
        check("restore-exact-immutable-native-analyzer", original.analyze_native is saved)

        check("accept-exclusive-v4-source-report", destination_name(REPORT_RELATIVE) == REPORT_RELATIVE)
        for name, value in (
            ("reject-v3-report-overwrite", previous.REPORT_RELATIVE),
            ("reject-absolute-report", "/" + REPORT_RELATIVE),
            ("reject-parent-traversal-report", "candidates/audits/../POSTFINAL-FROM-SCRATCH-AUDIT-V4.json"),
            ("reject-noncanonical-report", "candidates//audits/POSTFINAL-FROM-SCRATCH-AUDIT-V4.json"),
            ("reject-foreign-report", "candidates/audits/FOREIGN.json"),
            ("reject-nontext-report", 4),
        ):
            rejected(name, lambda item=value: destination_name(item))
        previous.ensure_candidate_free()

    check("zero-production-evidence-file-reads", effects.counts["files"] == 0)
    check("zero-production-evidence-file-writes", effects.counts["files"] == 0)
    check("zero-candidate-worker-or-subprocess-starts", effects.counts["processes"] == 0)
    check("zero-production-clock-samples", effects.counts["clocks"] == 0)
    check("zero-production-entropy-draws", effects.counts["entropy"] == 0)
    names = [item["name"] for item in checks]
    failed = sorted(item["name"] for item in checks if not item["passed"])
    if len(names) != len(set(names)):
        failed.append("duplicate-v4-control-name")
    if len(checks) < MINIMUM_PREVIOUS_CONTROLS:
        failed.append("weakened-v4-control-denominator")
    previous.ensure_candidate_free()
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS" if not failed else "FAIL",
        "result": "PASS" if not failed else "FAIL",
        "passed": not failed,
        "checks": checks,
        "check_count": len(checks),
        "failed": failed,
        "inherited_v3_self_test": inherited,
        "inherited_v3_control_count": inherited["check_count"],
        "inherited_self_test": inherited["inherited_self_test"],
        "inherited_control_count": 76,
        "allowed_rust_libc_primitives": sorted(ALLOWED_LOCALE_LIBC_PRIMITIVES),
        "fixture_storage": "in-memory only",
        "candidate_imported": False,
        "candidate_imports": [],
        "file_reads": effects.counts["files"],
        "file_writes": 0,
        "subprocesses": effects.counts["processes"],
        "clock_samples": effects.counts["clocks"],
        "production_entropy_drawn": False,
        "historical_holdout_accessed": False,
        "holdout_or_case_fixture_access": False,
        "benchmark_or_timing_executed": False,
        "production_cases_materialized": 0,
        "report_written": False,
    }


def audit() -> dict[str, Any]:
    runtime = previous.verify_production_runtime()
    previous.ensure_candidate_free()
    actual_v3_source, _ = previous.bounded_file(
        previous.SOURCE_PATH, maximum=MAX_SOURCE_BYTES, label="immutable V3 audit source"
    )
    require(actual_v3_source == PREVIOUS_SOURCE_SHA256, "the immutable V3 source audit changed")
    historical_digest, payload = previous.bounded_file(
        previous.REPORT_PATH,
        maximum=MAX_REPORT_BYTES,
        label="immutable V3 source-audit report",
        keep=True,
    )
    require(historical_digest == PREVIOUS_REPORT_SHA256, "the immutable V3 source report changed")
    historical = previous.decode_report(payload, label="immutable V3 source audit")
    previous.validate_v3_report(historical, label="immutable V3 source audit")
    del historical, payload
    controls = self_test()
    validate_v4_controls(controls)
    previous.ensure_candidate_free()
    gc.collect()
    with allow_owned_rust_locale_ctype():
        current = previous.audit()
    previous.validate_v3_report(current, label="fresh actual four-family V3 source audit")
    require(
        current.get("audit_source_sha256") == PREVIOUS_SOURCE_SHA256,
        "the fresh live V3 source audit is not bound to its immutable controller",
    )
    engine_digest, engine_payload = previous.bounded_file(
        previous.original.RUST_BINARIES["engine"],
        maximum=MAX_SOURCE_BYTES,
        label="actual owned Rust locale engine",
        keep=True,
    )
    engine = previous.original.parse_elf(engine_payload)
    expected_engine = current["rust_native_elf_provenance"]["files"]["engine"]
    require(
        engine_digest == expected_engine.get("sha256")
        and "libc.so.6" in engine.get("needed", [])
        and ALLOWED_LOCALE_LIBC_PRIMITIVES.issubset(set(engine.get("undefined", []))),
        "the owned locale engine does not resolve exactly through its audited libc dependency",
    )
    del engine_payload
    source_digest, _ = previous.bounded_file(
        SOURCE_PATH, maximum=MAX_SOURCE_BYTES, label="actual V4 source-audit controller"
    )
    result = dict(current)
    result.update(
        {
            "postfinal_schema": SCHEMA,
            "status": "PASS",
            "audit_source_path": SOURCE_RELATIVE,
            "audit_source_sha256": source_digest,
            "previous_v3_audit_source_path": previous.SOURCE_RELATIVE,
            "previous_v3_audit_source_sha256": PREVIOUS_SOURCE_SHA256,
            "previous_v3_audit_report_path": previous.REPORT_RELATIVE,
            "previous_v3_audit_report_sha256": PREVIOUS_REPORT_SHA256,
            "previous_v3_postfinal_schema": previous.SCHEMA,
            "previous_v3_wrapper_self_test": current["postfinal_wrapper_self_test"],
            "postfinal_wrapper_self_test": controls,
            "postfinal_interpreter": runtime,
            "v4_allowed_rust_libc_primitives": sorted(ALLOWED_LOCALE_LIBC_PRIMITIVES),
            "postfinal_scope": {
                "append_only": True,
                "exclusive_report_path": REPORT_RELATIVE,
                "original_v1_report_preserved": True,
                "previous_v2_report_preserved": True,
                "previous_v3_report_preserved": True,
                "original_main_invoked": False,
                "full_original_audit_rerun": True,
                "original_synthetic_controls_rerun": 76,
                "benchmark_or_timing_executed": False,
                "holdout_or_case_fixture_access": False,
            },
        }
    )
    validate_v4_report(result, label="actual complete V4 source audit")
    previous.ensure_candidate_free()
    return result


def write_report(report: Mapping[str, Any], target: Path) -> str:
    require(isinstance(target, Path), "the exclusive V4 destination is not a path")
    require(
        target.name == REPORT_PATH.name
        and not target.is_symlink()
        and target.parent.resolve() == REPORT_PATH.parent.resolve(),
        "only the exact non-symlink V4 source report is authorized",
    )
    parent = REPORT_PATH.parent
    require(not parent.is_symlink(), "the V4 report directory is a symlink")
    resolved = parent.resolve(strict=True)
    require(resolved.is_relative_to(ROOT.resolve(strict=True)), "the V4 report directory escaped the repository")
    payload = previous.canonical(report) + b"\n"
    require(len(payload) <= MAX_REPORT_BYTES, "the complete V4 report exceeds its bound")
    directory_flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    directory_flags |= getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    file_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    file_flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    parent_fd = os.open(resolved, directory_flags)
    try:
        require(stat.S_ISDIR(os.fstat(parent_fd).st_mode), "the V4 report parent is not a directory")
        descriptor = os.open(REPORT_PATH.name, file_flags, 0o644, dir_fd=parent_fd)
        try:
            view = memoryview(payload)
            while view:
                written = os.write(descriptor, view)
                require(written > 0, "the V4 exclusive evidence write made no progress")
                view = view[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        os.fsync(parent_fd)
    finally:
        os.close(parent_fd)
    return hashlib.sha256(payload).hexdigest()


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_mutually_exclusive_group(required=True)
    commands.add_argument("--self-test", action="store_true")
    commands.add_argument("--audit", action="store_true")
    parser.add_argument("--output", type=Path, default=REPORT_PATH)
    args = parser.parse_args(arguments)
    try:
        previous.ensure_candidate_free()
        if args.self_test:
            require(args.output == REPORT_PATH, "the V4 self-test cannot select a report")
            result = self_test()
            sys.stdout.buffer.write(previous.canonical(result) + b"\n")
            return 0 if result["passed"] else 1
        result = audit()
        report_digest = write_report(result, args.output)
        summary = {
            "postfinal_schema": SCHEMA,
            "status": "PASS",
            "result": "PASS",
            "passed": True,
            "report": REPORT_RELATIVE,
            "report_sha256": report_digest,
            "audit_source_sha256": result["audit_source_sha256"],
            "original_control_count": 76,
            "previous_v3_control_count": result["previous_v3_wrapper_self_test"]["check_count"],
            "v4_control_count": result["postfinal_wrapper_self_test"]["check_count"],
            "verified_core_family_count": result["verified_core_family_count"],
            "verified_distinct_pipeline_count": result["verified_distinct_pipeline_count"],
            "verified_native_role_count": result["native_elf_provenance"]["audited_binary_count"],
            "allowed_rust_libc_primitives": sorted(ALLOWED_LOCALE_LIBC_PRIMITIVES),
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        }
        sys.stdout.buffer.write(previous.canonical(summary) + b"\n")
        return 0
    except (previous.AuditV3Error, OSError, RuntimeError, TypeError, ValueError, KeyError) as error:
        sys.stdout.buffer.write(
            previous.canonical(
                {
                    "postfinal_schema": SCHEMA,
                    "status": "FAIL",
                    "result": "FAIL",
                    "passed": False,
                    "error": str(error),
                    "candidate_imported": False,
                    "benchmark_or_timing_executed": False,
                    "holdout_or_case_fixture_access": False,
                }
            )
            + b"\n"
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
