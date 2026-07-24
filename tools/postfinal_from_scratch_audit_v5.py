#!/usr/bin/env python3
"""Additively audit all three genuinely locale-aware owned native engines."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import gc
import hashlib
import os
from pathlib import Path, PurePosixPath
import stat
import sys
from typing import Any, Iterator, Mapping


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import postfinal_from_scratch_audit_v4 as previous


original = previous.previous.original
SCHEMA = "rebar-postfinal-from-scratch-audit-v5"
SOURCE_RELATIVE = "tools/postfinal_from_scratch_audit_v5.py"
SOURCE_PATH = ROOT / SOURCE_RELATIVE
REPORT_RELATIVE = "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V5.json"
REPORT_PATH = ROOT / REPORT_RELATIVE
PREVIOUS_SOURCE_SHA256 = (
    "efdbcd1d9bebb1716e84e8c618fedadb19206c20847900036a7b156ca12679ff"
)
PREVIOUS_REPORT_SHA256 = (
    "5677065d42ba0c4f135182cb681533181e57de823a367fdd54fde3d90120f87a"
)
LOCALE_SYMBOLS = frozenset({"tolower", "isalnum"})
OWNED_LOCALE_SOURCES = {
    "rust": "candidates/rust/src/lib.rs",
    "vm": "candidates/_vm_native.c",
    "zig": "candidates/zig/mini_regex.zig",
}
MINIMUM_PREVIOUS_CONTROLS = 162
MAX_SOURCE_BYTES = previous.MAX_SOURCE_BYTES
MAX_REPORT_BYTES = previous.MAX_REPORT_BYTES


class AuditV5Error(previous.AuditV4Error):
    """An exact V5 provenance, source, or exclusive destination failed."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise AuditV5Error(message)


def destination_name(value: Any) -> str:
    require(type(value) is str, "the exact V5 source report is not text")
    target = PurePosixPath(value)
    require(
        not target.is_absolute()
        and ".." not in target.parts
        and "\\" not in value
        and "\x00" not in value
        and str(target) == value
        and value == REPORT_RELATIVE,
        "only the distinct canonical exclusive V5 source report is authorized",
    )
    return value


@contextmanager
def allow_owned_locale_ctype() -> Iterator[None]:
    """Admit only audited libc ctype in the three exact owned source roots."""

    inherited = original.analyze_native
    require(
        callable(inherited)
        and getattr(inherited, "__module__", None) == original.__name__
        and getattr(inherited, "__name__", None) == "analyze_native",
        "the immutable original native analyzer was already substituted",
    )

    def narrowed(source: str, path: str, family: str) -> dict[str, Any]:
        result = inherited(source, path, family)
        owned = OWNED_LOCALE_SOURCES.get(family) == path
        if not owned and (family != "zig" or not path.endswith(".zig")):
            return result
        findings = result.get("issues")
        require(isinstance(findings, list), "the original native analyzer changed its findings")

        def is_allowed(item: Any) -> bool:
            if not owned or not isinstance(item, dict) or item.get("file") != path:
                return False
            code = item.get("code")
            detail = item.get("detail")
            if family == "rust":
                return code == "unowned_rust_extern" and detail in LOCALE_SYMBOLS
            if family == "vm":
                return (
                    code == "unapproved_native_header" and detail == "ctype.h"
                ) or (
                    code == "unowned_native_extern" and detail in LOCALE_SYMBOLS
                )
            return code == "unowned_zig_extern" and detail in LOCALE_SYMBOLS

        retained = [item for item in findings if not is_allowed(item)]
        if family == "zig":
            code = original.strip_native(source, preserve_strings=True)
            declarations = original.re.finditer(
                r'(?m)^[ \t]*extern(?:[ \t]+"(?:c|C)")?[ \t]+fn[ \t]+'
                r'([A-Za-z_][A-Za-z_0-9]*)',
                code,
            )
            approved = set(original.ALLOWED_ZIG_UNICODE_EXTERNS)
            if owned:
                approved.update(LOCALE_SYMBOLS)
            for declaration in declarations:
                target = declaration.group(1)
                if target not in approved:
                    issue = original.finding(
                        path,
                        "unowned_zig_extern",
                        target,
                        code.count("\n", 0, declaration.start()) + 1,
                    )
                    if issue not in retained:
                        retained.append(issue)
        if retained == findings:
            return result
        return {**result, "issues": retained, "passed": not retained}

    original.analyze_native = narrowed
    try:
        yield
    finally:
        original.analyze_native = inherited


def validate_v5_controls(document: Any) -> dict[str, Any]:
    require(isinstance(document, dict), "the V5 candidate-free controls are missing")
    records = document.get("checks")
    count = document.get("check_count")
    require(
        document.get("schema") == SCHEMA + "-self-test"
        and document.get("passed") is True
        and document.get("status") == "PASS"
        and document.get("result") == "PASS"
        and type(count) is int
        and count >= MINIMUM_PREVIOUS_CONTROLS
        and isinstance(records, list)
        and len(records) == count
        and all(
            isinstance(item, dict)
            and isinstance(item.get("name"), str)
            and item.get("passed") is True
            for item in records
        )
        and len({item["name"] for item in records}) == count
        and document.get("failed") == []
        and document.get("fixture_storage") == "in-memory only"
        and document.get("candidate_imported") is False
        and document.get("file_reads") == 0
        and document.get("file_writes") == 0
        and document.get("subprocesses") == 0
        and document.get("clock_samples") == 0
        and document.get("production_entropy_drawn") is False
        and document.get("benchmark_or_timing_executed") is False
        and document.get("holdout_or_case_fixture_access") is False
        and document.get("production_cases_materialized") == 0
        and document.get("report_written") is False,
        "the V5 source controls are failing, duplicated, incomplete, or unsafe",
    )
    previous.validate_v4_controls(document.get("inherited_v4_self_test"))
    return document


def validate_v5_report(document: Any, *, label: str) -> dict[str, Any]:
    require(isinstance(document, dict), f"{label} is not a complete object")
    expected = {
        "schema_version": 1,
        "audit": previous.previous.AUDIT_NAME,
        "postfinal_schema": SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "audit_source_path": SOURCE_RELATIVE,
        "previous_v4_audit_source_path": previous.SOURCE_RELATIVE,
        "previous_v4_audit_source_sha256": PREVIOUS_SOURCE_SHA256,
        "previous_v4_audit_report_path": previous.REPORT_RELATIVE,
        "previous_v4_audit_report_sha256": PREVIOUS_REPORT_SHA256,
        "previous_v4_postfinal_schema": previous.SCHEMA,
        "previous_v4_report_historical": True,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
    }
    for key, value in expected.items():
        require(
            document.get(key) == value and type(document.get(key)) is type(value),
            f"{label} changed the immutable V4/V5 field {key}",
        )
    require(
        previous.previous.valid_sha256(document.get("audit_source_sha256"))
        and document.get("v5_allowed_locale_libc_primitives") == sorted(LOCALE_SYMBOLS)
        and document.get("v5_owned_locale_sources") == OWNED_LOCALE_SOURCES,
        f"{label} concealed or widened its exact three-family libc allowance",
    )
    controls = validate_v5_controls(document.get("postfinal_wrapper_self_test"))
    previous.validate_v4_controls(document.get("previous_v4_wrapper_self_test"))
    require(
        document["previous_v4_wrapper_self_test"] == controls["inherited_v4_self_test"],
        f"{label} substituted inherited V4 synthetic safeguards",
    )
    v3_controls = document.get("previous_v3_wrapper_self_test")
    previous.previous.validate_wrapper_controls(
        v3_controls,
        schema=previous.previous.SCHEMA,
        minimum=previous.MINIMUM_PREVIOUS_CONTROLS,
    )
    scope = document.get("postfinal_scope")
    require(
        isinstance(scope, dict)
        and scope.get("append_only") is True
        and scope.get("exclusive_report_path") == REPORT_RELATIVE
        and scope.get("original_v1_report_preserved") is True
        and scope.get("previous_v2_report_preserved") is True
        and scope.get("previous_v3_report_preserved") is True
        and scope.get("previous_v4_report_preserved") is True
        and scope.get("previous_v4_report_historical") is True
        and scope.get("full_original_audit_rerun") is True
        and scope.get("original_synthetic_controls_rerun") == 76
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_or_case_fixture_access") is False,
        f"{label} weakened its immutable lineage or exclusive no-measurement scope",
    )
    inherited = dict(document)
    inherited.update(
        {
            "postfinal_schema": previous.previous.SCHEMA,
            "audit_source_path": previous.previous.SOURCE_RELATIVE,
            "audit_source_sha256": previous.PREVIOUS_SOURCE_SHA256,
            "postfinal_wrapper_self_test": v3_controls,
            "postfinal_scope": {
                "append_only": True,
                "exclusive_report_path": previous.previous.REPORT_RELATIVE,
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
    previous.previous.validate_v3_report(inherited, label=label + " live universal proof")
    return document


def self_test() -> dict[str, Any]:
    previous.previous.ensure_candidate_free()
    effects = previous.previous.previous.BlockSelfTestEffects()
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: Any) -> None:
        checks.append({"name": name, "passed": bool(passed)})

    def rejected(name: str, action: Any) -> None:
        try:
            action()
        except (previous.previous.AuditV3Error, TypeError, ValueError, KeyError, UnicodeError):
            check(name, True)
        else:
            check(name, False)

    with effects:
        inherited = previous.self_test()
        previous.validate_v4_controls(inherited)
        for item in inherited["checks"]:
            check("v4:" + item["name"], item["passed"] is True)
        check("preserve-all-original-76-controls", inherited["inherited_control_count"] == 76)
        check("preserve-at-least-129-v3-controls", inherited["inherited_v3_control_count"] >= 129)
        check("preserve-at-least-162-v4-controls", inherited["check_count"] >= 162)
        check("preserve-exact-three-owned-locale-families", set(OWNED_LOCALE_SOURCES) == {"vm", "rust", "zig"})
        check("allow-only-two-audited-libc-primitives", LOCALE_SYMBOLS == frozenset({"isalnum", "tolower"}))
        check("pin-exact-historical-v4-source-digest", previous.previous.valid_sha256(PREVIOUS_SOURCE_SHA256))
        check("pin-exact-historical-v4-report-digest", previous.previous.valid_sha256(PREVIOUS_REPORT_SHA256))

        rust = 'unsafe extern "C" { fn tolower(v: i32) -> i32; fn isalnum(v: i32) -> i32; }'
        vm = "#include <ctype.h>\nextern int tolower(int);\nextern int isalnum(int);\n"
        zig = 'extern "c" fn tolower(c_int) c_int;\nextern "c" fn isalnum(c_int) c_int;\n'
        fixtures = {"rust": rust, "vm": vm, "zig": zig}
        check(
            "immutable-original-rejects-rust-libc-extern-before-v5",
            not original.analyze_native(rust, OWNED_LOCALE_SOURCES["rust"], "rust")["passed"],
        )
        check(
            "immutable-original-rejects-vm-ctype-header-before-v5",
            not original.analyze_native(vm, OWNED_LOCALE_SOURCES["vm"], "vm")["passed"],
        )
        saved = original.analyze_native
        with allow_owned_locale_ctype():
            for family, fixture in fixtures.items():
                check(
                    "accept-libc-ctype-only-for-owned-root:" + family,
                    original.analyze_native(
                        fixture, OWNED_LOCALE_SOURCES[family], family
                    )["passed"],
                )
            for family, foreign in (
                ("rust", "pcre2_match"),
                ("rust", "rebar_zig_compile"),
                ("vm", "regexec"),
                ("vm", "dlopen"),
                ("zig", "pcre2_match"),
                ("zig", "rebar_compile"),
                ("zig", "innocent_engine_match"),
            ):
                if family == "rust":
                    fixture = (
                        'unsafe extern "C" { fn tolower(v: i32) -> i32; '
                        f"fn {foreign}(); "
                        "}"
                    )
                elif family == "vm":
                    fixture = "#include <ctype.h>\n" + f"extern int {foreign}(void);\n"
                else:
                    fixture = (
                        'extern "c" fn tolower(c_int) c_int;\n'
                        + f'extern "c" fn {foreign}() c_int;\n'
                    )
                check(
                    "reject-foreign-extern-even-with-locale-libc:"
                    + family + ":" + foreign,
                    not original.analyze_native(
                        fixture, OWNED_LOCALE_SOURCES[family], family
                    )["passed"],
                )
            for family in ("rust", "vm", "zig"):
                wrong = {
                    "rust": "candidates/rust/src/foreign.rs",
                    "vm": "candidates/_foreign_native.c",
                    "zig": "candidates/zig/foreign.zig",
                }[family]
                check(
                    "reject-locale-libc-outside-owned-root:" + family,
                    not original.analyze_native(fixtures[family], wrong, family)["passed"],
                )
        check("restore-exact-original-native-analyzer", original.analyze_native is saved)
        check("accept-only-exclusive-v5-source-report", destination_name(REPORT_RELATIVE) == REPORT_RELATIVE)
        for label, value in (
            ("reject-historical-v4-report-overwrite", previous.REPORT_RELATIVE),
            ("reject-historical-v3-report-overwrite", previous.previous.REPORT_RELATIVE),
            ("reject-absolute-report", "/" + REPORT_RELATIVE),
            ("reject-traversing-report", "candidates/audits/../POSTFINAL-FROM-SCRATCH-AUDIT-V5.json"),
            ("reject-noncanonical-report", "candidates//audits/POSTFINAL-FROM-SCRATCH-AUDIT-V5.json"),
            ("reject-foreign-report", "candidates/audits/FOREIGN.json"),
            ("reject-nontext-report", 5),
        ):
            rejected(label, lambda target=value: destination_name(target))
        previous.previous.ensure_candidate_free()

    check("zero-file-reads", effects.counts["files"] == 0)
    check("zero-file-writes", effects.counts["files"] == 0)
    check("zero-worker-starts", effects.counts["processes"] == 0)
    check("zero-benchmark-clock-samples", effects.counts["clocks"] == 0)
    check("zero-entropy-draws", effects.counts["entropy"] == 0)
    names = [item["name"] for item in checks]
    failed = sorted(item["name"] for item in checks if not item["passed"])
    if len(set(names)) != len(names):
        failed.append("duplicate-v5-source-control-name")
    if len(checks) < MINIMUM_PREVIOUS_CONTROLS:
        failed.append("weakened-v5-source-control-denominator")
    previous.previous.ensure_candidate_free()
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS" if not failed else "FAIL",
        "result": "PASS" if not failed else "FAIL",
        "passed": not failed,
        "checks": checks,
        "check_count": len(checks),
        "failed": failed,
        "inherited_v4_self_test": inherited,
        "inherited_v4_control_count": inherited["check_count"],
        "inherited_self_test": inherited["inherited_self_test"],
        "inherited_control_count": 76,
        "allowed_locale_libc_primitives": sorted(LOCALE_SYMBOLS),
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
    runtime = previous.previous.verify_production_runtime()
    previous.previous.ensure_candidate_free()
    predecessor_source, _ = previous.previous.bounded_file(
        previous.SOURCE_PATH,
        maximum=MAX_SOURCE_BYTES,
        label="immutable historical V4 source controller",
    )
    require(predecessor_source == PREVIOUS_SOURCE_SHA256, "the preserved V4 source controller changed")
    predecessor_digest, payload = previous.previous.bounded_file(
        previous.REPORT_PATH,
        maximum=MAX_REPORT_BYTES,
        label="preserved historical V4 source report",
        keep=True,
    )
    require(predecessor_digest == PREVIOUS_REPORT_SHA256, "the immutable historical V4 report changed")
    historical = previous.previous.decode_report(payload, label="historical V4 source report")
    previous.validate_v4_report(historical, label="preserved historical V4 proof")
    del historical, payload
    controls = self_test()
    validate_v5_controls(controls)
    previous.previous.ensure_candidate_free()
    gc.collect()
    with allow_owned_locale_ctype():
        current = previous.previous.audit()
    previous.previous.validate_v3_report(current, label="fresh live four-family V5 source audit")

    for family, role in (("rust", "engine"), ("vm", "native"), ("zig", "engine")):
        binary = original.NATIVE_BINARIES[family][role]
        digest, payload = previous.previous.bounded_file(
            binary,
            maximum=MAX_SOURCE_BYTES,
            label="actual locale-aware owned " + family + " native binary",
            keep=True,
        )
        parsed = original.parse_elf(payload)
        expected = current["native_elf_provenance"]["families"][family]["files"][role]
        require(
            digest == expected.get("sha256")
            and "libc.so.6" in parsed.get("needed", []),
            "the actual owned " + family + " locale engine is not bound to audited libc",
        )
        observed = set(parsed.get("undefined", []))
        if family in {"rust", "zig"}:
            require(
                LOCALE_SYMBOLS.issubset(observed),
                "the actual " + family + " engine does not resolve both declared libc primitives",
            )
        else:
            require(
                bool(observed & {"tolower", "isalnum", "__ctype_b_loc", "__ctype_tolower_loc"}),
                "the actual C engine does not resolve audited libc ctype",
            )
        del payload

    source_digest, _ = previous.previous.bounded_file(
        SOURCE_PATH, maximum=MAX_SOURCE_BYTES, label="actual exclusive V5 source controller"
    )
    result = dict(current)
    result.update(
        {
            "postfinal_schema": SCHEMA,
            "status": "PASS",
            "audit_source_path": SOURCE_RELATIVE,
            "audit_source_sha256": source_digest,
            "previous_v4_audit_source_path": previous.SOURCE_RELATIVE,
            "previous_v4_audit_source_sha256": PREVIOUS_SOURCE_SHA256,
            "previous_v4_audit_report_path": previous.REPORT_RELATIVE,
            "previous_v4_audit_report_sha256": PREVIOUS_REPORT_SHA256,
            "previous_v4_postfinal_schema": previous.SCHEMA,
            "previous_v4_report_historical": True,
            "previous_v4_wrapper_self_test": controls["inherited_v4_self_test"],
            "previous_v3_wrapper_self_test": current["postfinal_wrapper_self_test"],
            "postfinal_wrapper_self_test": controls,
            "postfinal_interpreter": runtime,
            "v5_allowed_locale_libc_primitives": sorted(LOCALE_SYMBOLS),
            "v5_owned_locale_sources": dict(OWNED_LOCALE_SOURCES),
            "postfinal_scope": {
                "append_only": True,
                "exclusive_report_path": REPORT_RELATIVE,
                "original_v1_report_preserved": True,
                "previous_v2_report_preserved": True,
                "previous_v3_report_preserved": True,
                "previous_v4_report_preserved": True,
                "previous_v4_report_historical": True,
                "original_main_invoked": False,
                "full_original_audit_rerun": True,
                "original_synthetic_controls_rerun": 76,
                "benchmark_or_timing_executed": False,
                "holdout_or_case_fixture_access": False,
            },
        }
    )
    validate_v5_report(result, label="actual additive all-engine V5 source audit")
    previous.previous.ensure_candidate_free()
    return result


def write_report(report: Mapping[str, Any], target: Path) -> str:
    require(
        isinstance(target, Path)
        and target.name == REPORT_PATH.name
        and not target.is_symlink()
        and target.parent.resolve() == REPORT_PATH.parent.resolve(),
        "only the exact non-symlink exclusive V5 source proof may be written",
    )
    parent = REPORT_PATH.parent
    require(not parent.is_symlink(), "the V5 source report parent is a symlink")
    resolved = parent.resolve(strict=True)
    require(resolved.is_relative_to(ROOT.resolve(strict=True)), "the V5 report escaped the repository")
    payload = previous.previous.canonical(report) + b"\n"
    require(len(payload) <= MAX_REPORT_BYTES, "the complete V5 proof exceeds its size bound")
    directory_flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    directory_flags |= getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    directory = os.open(resolved, directory_flags)
    try:
        require(stat.S_ISDIR(os.fstat(directory).st_mode), "the V5 parent is not a directory")
        descriptor = os.open(REPORT_PATH.name, flags, 0o644, dir_fd=directory)
        try:
            view = memoryview(payload)
            while view:
                written = os.write(descriptor, view)
                require(written > 0, "the V5 exclusive source report write stalled")
                view = view[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        os.fsync(directory)
    finally:
        os.close(directory)
    return hashlib.sha256(payload).hexdigest()


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_mutually_exclusive_group(required=True)
    commands.add_argument("--self-test", action="store_true")
    commands.add_argument("--audit", action="store_true")
    parser.add_argument("--output", type=Path, default=REPORT_PATH)
    args = parser.parse_args(arguments)
    try:
        previous.previous.ensure_candidate_free()
        if args.self_test:
            require(args.output == REPORT_PATH, "the V5 self-test cannot create a report")
            result = self_test()
            sys.stdout.buffer.write(previous.previous.canonical(result) + b"\n")
            return 0 if result["passed"] else 1
        result = audit()
        digest = write_report(result, args.output)
        sys.stdout.buffer.write(
            previous.previous.canonical(
                {
                    "schema_version": 1,
                    "postfinal_schema": SCHEMA,
                    "status": "PASS",
                    "result": "PASS",
                    "passed": True,
                    "report": REPORT_RELATIVE,
                    "report_sha256": digest,
                    "audit_source_sha256": result["audit_source_sha256"],
                    "original_control_count": 76,
                    "inherited_v4_control_count": result["postfinal_wrapper_self_test"]["inherited_v4_control_count"],
                    "v5_control_count": result["postfinal_wrapper_self_test"]["check_count"],
                    "verified_family_count": len(result["families"]),
                    "verified_native_role_count": result["native_elf_provenance"]["audited_binary_count"],
                    "allowed_locale_libc_primitives": sorted(LOCALE_SYMBOLS),
                    "benchmark_or_timing_executed": False,
                    "holdout_or_case_fixture_access": False,
                }
            )
            + b"\n"
        )
        return 0
    except (previous.previous.AuditV3Error, OSError, RuntimeError, TypeError, ValueError, KeyError) as error:
        sys.stdout.buffer.write(
            previous.previous.canonical(
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
