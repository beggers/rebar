#!/usr/bin/env python3
"""Exclusively verify genuine immutable guards against the V5 locale proof."""

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

from tools import postfinal_from_scratch_audit_v5 as source_v5
from tools import postfinal_no_delegation_audit_v4 as previous


SCHEMA = "rebar-postfinal-no-delegation-audit-v5"
SOURCE_RELATIVE = "tools/postfinal_no_delegation_audit_v5.py"
SOURCE_PATH = ROOT / SOURCE_RELATIVE
REPORT_RELATIVE = "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V5.json"
REPORT_PATH = ROOT / REPORT_RELATIVE
PREVIOUS_SOURCE_SHA256 = (
    "f4587015e8ab90a3bab3cc5a8874aabe3664da4c69445c0845a6672960209658"
)
MAX_SOURCE_BYTES = previous.MAX_SOURCE_BYTES
MAX_REPORT_BYTES = previous.MAX_REPORT_BYTES
ADDITIVE_PUBLIC_INPUTS = frozenset(
    {source_v5.SOURCE_RELATIVE, source_v5.REPORT_RELATIVE, SOURCE_RELATIVE}
)
PUBLIC_INPUTS = previous.PUBLIC_INPUTS | ADDITIVE_PUBLIC_INPUTS
ORIGINAL_CONTROL_BOOTSTRAP = r'''
import hashlib
import json
import sys
from pathlib import Path

if len(sys.argv) != 3:
    raise RuntimeError("the isolated V5 control bootstrap is not exact")
root = Path(sys.argv[1]).resolve(strict=True)
expected = sys.argv[2]
if len(expected) != 64 or any(item not in "0123456789abcdef" for item in expected):
    raise RuntimeError("the isolated V5 controller fingerprint is invalid")
sys.path.insert(0, str(root))
from tools import postfinal_from_scratch_audit_v5 as source_v5
if source_v5.ROOT.resolve(strict=True) != root:
    raise RuntimeError("the isolated V5 source escaped its exact root")
with source_v5.SOURCE_PATH.open("rb") as stream:
    payload = stream.read(source_v5.MAX_SOURCE_BYTES + 1)
if len(payload) > source_v5.MAX_SOURCE_BYTES:
    raise RuntimeError("the isolated V5 source exceeds its limit")
if hashlib.sha256(payload).hexdigest() != expected:
    raise RuntimeError("the isolated V5 source fingerprint changed")
del payload
with source_v5.allow_owned_locale_ctype():
    result = source_v5.original.self_test()
sys.stdout.write(json.dumps(result, sort_keys=True) + "\n")
raise SystemExit(0 if result.get("passed") is True else 1)
'''


class AuditV5Error(previous.AuditV4Error):
    """The additive V5 strict proof violated an exact provenance obligation."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise AuditV5Error(message)


def validate_public_relative(value: Any) -> str:
    require(type(value) is str, "the strict V5 public path is not text")
    path = PurePosixPath(value)
    require(
        not path.is_absolute()
        and ".." not in path.parts
        and "\\" not in value
        and "\x00" not in value
        and str(path) == value
        and value in PUBLIC_INPUTS,
        "refusing a private, final, benchmark, foreign, or unapproved V5 input",
    )
    return value


def bounded_public_bytes(path: Path, *, maximum: int) -> tuple[bytes, str]:
    require(
        isinstance(path, Path) and not path.is_symlink(),
        "a strict V5 public input is absent or a symlink",
    )
    try:
        resolved = path.resolve(strict=True)
        relative = resolved.relative_to(ROOT.resolve(strict=True)).as_posix()
    except (OSError, RuntimeError, ValueError) as error:
        raise AuditV5Error("a strict V5 public input escaped the repository") from error
    validate_public_relative(relative)
    require(resolved.is_file(), "a strict V5 public input is not a regular file")
    digest, payload = source_v5.previous.previous.bounded_file(
        path,
        maximum=maximum,
        label="exact authenticated strict V5 input: " + relative,
        keep=True,
    )
    return payload, digest


def public_document(path: Path) -> tuple[dict[str, Any], str]:
    payload, digest = bounded_public_bytes(path, maximum=MAX_REPORT_BYTES)
    return previous.previous.decode_public_json(payload), digest


def destination_name(value: Any) -> str:
    require(type(value) is str, "the exclusive strict V5 destination is not text")
    path = PurePosixPath(value)
    require(
        not path.is_absolute()
        and ".." not in path.parts
        and "\\" not in value
        and "\x00" not in value
        and str(path) == value
        and value == REPORT_RELATIVE,
        "only the exact exclusive V5 no-delegation report is authorized",
    )
    return value


def adapt_original_control_command(command: Any, source_digest: Any) -> list[str]:
    expected = [
        sys.executable,
        "-I",
        "-B",
        str(Path(source_v5.original.__file__).resolve()),
        "--self-test",
    ]
    require(
        type(command) is list
        and len(command) == len(expected)
        and all(type(item) is str for item in command)
        and command == expected,
        "refusing a substituted immutable original 76-control child",
    )
    require(
        source_v5.previous.previous.valid_sha256(source_digest),
        "refusing an unverified isolated V5 source bootstrap",
    )
    return [
        sys.executable,
        "-I",
        "-B",
        "-c",
        ORIGINAL_CONTROL_BOOTSTRAP,
        str(ROOT),
        source_digest,
    ]


@contextmanager
def scoped_original_control_bootstrap(source_digest: str) -> Iterator[None]:
    runner = source_v5.original.subprocess.run
    exact_source = str(Path(source_v5.original.__file__).resolve())

    def run(command: Any, *args: Any, **kwargs: Any) -> Any:
        if isinstance(command, (list, tuple)) and exact_source in command:
            return runner(
                adapt_original_control_command(command, source_digest),
                *args,
                **kwargs,
            )
        return runner(command, *args, **kwargs)

    source_v5.original.subprocess.run = run
    try:
        yield
    finally:
        source_v5.original.subprocess.run = runner


def candidate_free_self_test() -> dict[str, Any]:
    previous.previous.verify_pinned_runtime()
    previous.previous.require_candidate_free()
    effects = source_v5.previous.previous.previous.BlockSelfTestEffects()
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: Any) -> None:
        checks.append({"name": name, "passed": bool(condition)})

    def rejected(name: str, action: Any) -> None:
        try:
            action()
        except (
            source_v5.previous.previous.AuditV3Error,
            previous.previous.previous.AuditFailure,
            TypeError,
            ValueError,
            UnicodeError,
            KeyError,
        ):
            check(name, True)
        else:
            check(name, False)

    with effects:
        inherited_source = source_v5.self_test()
        source_v5.validate_v5_controls(inherited_source)
        inherited_strict = previous.candidate_free_self_test()
        require(
            isinstance(inherited_strict, dict)
            and inherited_strict.get("schema") == previous.SCHEMA + "-self-test"
            and inherited_strict.get("passed") is True
            and inherited_strict.get("failed") == []
            and inherited_strict.get("file_reads") == 0
            and inherited_strict.get("file_writes") == 0
            and inherited_strict.get("subprocesses") == 0
            and inherited_strict.get("candidate_imports") == 0,
            "the complete strict V4 candidate-free safeguards failed",
        )
        for item in inherited_source["checks"]:
            check("source-v5:" + item["name"], item["passed"] is True)
        for item in inherited_strict["checks"]:
            check("strict-v4:" + item["name"], item["passed"] is True)
        check("preserve-original-76-control-names", len(previous.previous.previous.BASE_CONTROL_NAMES) == 76)
        check("preserve-immutable-32-independence-controls", len(previous.previous.previous.STRICT_CONTROL_NAMES) == 32)
        check("preserve-at-least-198-v5-source-controls", inherited_source["check_count"] >= 198)
        check("preserve-at-least-430-v4-strict-controls", inherited_strict["check_count"] >= 430)
        check("preserve-four-independent-source-families", previous.previous.previous.AUDITED_FAMILIES == ("ast", "vm", "rust", "zig"))
        check("preserve-three-independent-native-families", previous.previous.previous.QUALIFIED_FAMILIES == ("vm", "rust", "zig"))
        check("preserve-five-actual-native-roles", len(previous.previous.previous.EXPECTED_NATIVE_KEYS) == 5)
        check("accept-only-two-libc-ctype-symbols", source_v5.LOCALE_SYMBOLS == frozenset({"tolower", "isalnum"}))
        check("allow-exactly-three-owned-locale-source-roots", set(source_v5.OWNED_LOCALE_SOURCES) == {"rust", "vm", "zig"})
        check("preserve-all-historical-v4-public-inputs", previous.PUBLIC_INPUTS.issubset(PUBLIC_INPUTS))
        check("admit-only-exact-three-v5-public-inputs", PUBLIC_INPUTS - previous.PUBLIC_INPUTS == ADDITIVE_PUBLIC_INPUTS)
        for label, value in (
            ("accept-exact-v5-source-controller", source_v5.SOURCE_RELATIVE),
            ("accept-exact-v5-source-proof", source_v5.REPORT_RELATIVE),
            ("accept-exact-v5-strict-controller", SOURCE_RELATIVE),
        ):
            check(label, validate_public_relative(value) == value)
        for label, value in (
            ("reject-private-audit-input", "sealed/private/cases.json"),
            ("reject-hidden-audit-input", "sealed/holdout/cases.json"),
            ("reject-final-audit-input", "sealed/final/cases.json"),
            ("reject-benchmark-audit-input", "benchmarks/cases.json"),
            ("reject-foreign-audit-input", "candidates/audits/FOREIGN.json"),
            ("reject-absolute-audit-input", "/" + source_v5.REPORT_RELATIVE),
            ("reject-traversing-audit-input", "candidates/audits/../POSTFINAL-FROM-SCRATCH-AUDIT-V5.json"),
            ("reject-noncanonical-audit-input", "candidates//audits/POSTFINAL-FROM-SCRATCH-AUDIT-V5.json"),
            ("reject-backslash-audit-input", "candidates\\audits\\POSTFINAL-FROM-SCRATCH-AUDIT-V5.json"),
            ("reject-nul-audit-input", source_v5.REPORT_RELATIVE + "\x00"),
            ("reject-nontext-audit-input", 5),
        ):
            rejected(label, lambda item=value: validate_public_relative(item))
        original_command = [
            sys.executable,
            "-I",
            "-B",
            str(Path(source_v5.original.__file__).resolve()),
            "--self-test",
        ]
        adapted = adapt_original_control_command(
            original_command,
            source_v5.PREVIOUS_SOURCE_SHA256,
        )
        check(
            "preserve-pinned-fresh-genuine-76-control-child",
            adapted[:4] == [sys.executable, "-I", "-B", "-c"]
            and adapted[4] == ORIGINAL_CONTROL_BOOTSTRAP
            and adapted[5] == str(ROOT)
            and adapted[6] == source_v5.PREVIOUS_SOURCE_SHA256,
        )
        check(
            "verify-v5-bootstrap-hash-and-exact-owned-libc-adapter",
            "hashlib.sha256(payload).hexdigest() != expected" in ORIGINAL_CONTROL_BOOTSTRAP
            and "source_v5.allow_owned_locale_ctype()" in ORIGINAL_CONTROL_BOOTSTRAP
            and "source_v5.original.self_test()" in ORIGINAL_CONTROL_BOOTSTRAP,
        )
        for label, command, digest in (
            ("reject-control-child-without-isolation", [sys.executable, "-B", original_command[3], "--self-test"], source_v5.PREVIOUS_SOURCE_SHA256),
            ("reject-control-child-without-bytecode-guard", [sys.executable, "-I", original_command[3], "--self-test"], source_v5.PREVIOUS_SOURCE_SHA256),
            ("reject-control-child-with-foreign-source", [sys.executable, "-I", "-B", "/tmp/foreign.py", "--self-test"], source_v5.PREVIOUS_SOURCE_SHA256),
            ("reject-control-child-with-wrong-mode", [sys.executable, "-I", "-B", original_command[3], "--audit"], source_v5.PREVIOUS_SOURCE_SHA256),
            ("reject-control-child-with-extra-argument", original_command + ["foreign"], source_v5.PREVIOUS_SOURCE_SHA256),
            ("reject-control-child-with-invalid-hash", original_command, "invalid"),
            ("reject-control-child-with-nontext-hash", original_command, 5),
            ("reject-control-child-with-tuple-command", tuple(original_command), source_v5.PREVIOUS_SOURCE_SHA256),
        ):
            rejected(label, lambda item=command, digest=digest: adapt_original_control_command(item, digest))
        check("accept-only-v5-strict-destination", destination_name(REPORT_RELATIVE) == REPORT_RELATIVE)
        for label, target in (
            ("reject-v4-strict-report-overwrite", previous.REPORT_RELATIVE),
            ("reject-v5-source-report-substitution", source_v5.REPORT_RELATIVE),
            ("reject-absolute-strict-report", "/" + REPORT_RELATIVE),
            ("reject-traversing-strict-report", "candidates/audits/../POSTFINAL-NO-DELEGATION-AUDIT-V5.json"),
            ("reject-noncanonical-strict-report", "candidates//audits/POSTFINAL-NO-DELEGATION-AUDIT-V5.json"),
            ("reject-foreign-strict-report", "candidates/audits/FOREIGN.json"),
            ("reject-nontext-strict-report", 5),
        ):
            rejected(label, lambda value=target: destination_name(value))
        previous.previous.require_candidate_free()

    check("zero-evidence-file-reads", effects.counts["files"] == 0)
    check("zero-evidence-file-writes", effects.counts["files"] == 0)
    check("zero-worker-or-subprocess-starts", effects.counts["processes"] == 0)
    check("zero-benchmark-clock-samples", effects.counts["clocks"] == 0)
    check("zero-entropy-draws", effects.counts["entropy"] == 0)
    names = [item["name"] for item in checks]
    failed = sorted(item["name"] for item in checks if not item["passed"])
    if len(names) != len(set(names)):
        failed.append("duplicate-strict-v5-control-name")
    previous.previous.require_candidate_free()
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS" if not failed else "FAIL",
        "result": "PASS" if not failed else "FAIL",
        "passed": not failed,
        "checks": checks,
        "check_count": len(checks),
        "failed": failed,
        "source_v5_self_test": inherited_source,
        "inherited_v4_self_test": inherited_strict,
        "inherited_source_control_count": inherited_source["check_count"],
        "inherited_strict_control_count": inherited_strict["check_count"],
        "fixture_storage": "in-memory only",
        "candidate_imports": 0,
        "candidate_imported": False,
        "file_reads": effects.counts["files"],
        "file_writes": 0,
        "subprocesses": effects.counts["processes"],
        "clock_samples": effects.counts["clocks"],
        "production_entropy_drawn": False,
        "guard_accessed": False,
        "historical_holdout_accessed": False,
        "holdout_or_case_fixture_access": False,
        "benchmark_or_timing_executed": False,
        "production_cases_materialized": 0,
        "report_written": False,
    }


def run_audit() -> dict[str, Any]:
    legacy = previous.previous
    immutable_v2 = legacy.previous
    legacy.require_candidate_free()
    legacy.verify_pinned_runtime()
    _v4_source, historical_v4_source_digest = bounded_public_bytes(
        previous.SOURCE_PATH, maximum=MAX_SOURCE_BYTES
    )
    require(
        historical_v4_source_digest == PREVIOUS_SOURCE_SHA256,
        "the immutable historical strict V4 controller changed",
    )
    del _v4_source
    historical_v3, historical_v3_digest = previous.public_document(legacy.REPORT)
    require(
        historical_v3_digest == previous.PREVIOUS_REPORT_SHA256,
        "the preserved strict V3 report changed",
    )
    previous.validate_historical_v3(historical_v3)
    del historical_v3
    legacy.validated_v3_base()

    historical_v4, historical_v4_digest = previous.public_document(
        source_v5.previous.REPORT_PATH
    )
    require(
        historical_v4_digest == source_v5.PREVIOUS_REPORT_SHA256,
        "the preserved rejected V4 source proof changed",
    )
    source_v5.previous.validate_v4_report(
        historical_v4,
        label="immutable historical-only V4 source proof",
    )
    del historical_v4

    base, base_digest = public_document(source_v5.REPORT_PATH)
    source_v5.validate_v5_report(base, label="the actual live complete V5 source proof")
    _v5_source, v5_source_digest = bounded_public_bytes(
        source_v5.SOURCE_PATH, maximum=MAX_SOURCE_BYTES
    )
    require(
        base.get("audit_source_sha256") == v5_source_digest,
        "the live V5 base report is not bound to its actual V5 source",
    )
    del _v5_source
    controls = candidate_free_self_test()
    require(controls.get("passed") is True, "the complete strict V5 poison controls failed")

    immutable = immutable_v2.import_pinned_strict_v1()
    actual_controls = immutable.self_test()
    immutable_v2.validate_controls(
        {"self_test": actual_controls},
        names=immutable_v2.STRICT_CONTROL_NAMES,
        label="the actual immutable V5 32-control no-delegation self-test",
    )
    del actual_controls
    saved_loader = immutable._load_original_report
    saved_report = immutable.original.REPORT
    require(
        isinstance(saved_report, Path)
        and saved_report.resolve() == immutable_v2.ORIGINAL_BASE_REPORT.resolve(),
        "the immutable original strict V1 worker was already rebound",
    )

    def load_authenticated_v5_base() -> tuple[dict[str, Any], str]:
        current, digest = public_document(source_v5.REPORT_PATH)
        require(
            digest == base_digest and current == base,
            "the exact authenticated V5 source report changed during strict execution",
        )
        source_v5.validate_v5_report(current, label="continuously authenticated V5 source proof")
        return current, digest

    immutable._load_original_report = load_authenticated_v5_base
    immutable.original.REPORT = source_v5.REPORT_PATH
    try:
        gc.collect()
        with source_v5.allow_owned_locale_ctype():
            with scoped_original_control_bootstrap(v5_source_digest):
                result = immutable.run_audit()
    finally:
        immutable.original.REPORT = saved_report
        immutable._load_original_report = saved_loader
    legacy.require_candidate_free()
    require(
        isinstance(result, dict)
        and result.get("schema") == immutable_v2.IMMUTABLE_STRICT_SCHEMA
        and result.get("passed") is True
        and result.get("result") == "PASS"
        and result.get("inherited_control_count") == 76,
        "the immutable V5 worker did not genuinely complete all 76 original controls",
    )
    immutable_v2.validate_controls(
        result,
        names=immutable_v2.STRICT_CONTROL_NAMES,
        label="the actual 32-control V5 no-delegation result",
    )
    immutable_v2.validate_controls(
        {"self_test": result.get("inherited_self_test")},
        names=immutable_v2.BASE_CONTROL_NAMES,
        label="the actual independently rerun 76 original V5 controls",
    )
    require(
        result.get("base_audit_report_path") == source_v5.REPORT_RELATIVE
        and result.get("base_audit_report_sha256") == base_digest,
        "the guarded immutable worker did not consume the exact V5 source report",
    )
    immutable_v2._verify_result_native(result, base)
    legacy._validate_flattened_native(result, label="the complete live five-role V5 strict proof")
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
        "the actual strict V5 source graph, native roles, or guarded isolation failed",
    )
    _current_source, current_source_digest = bounded_public_bytes(
        SOURCE_PATH, maximum=MAX_SOURCE_BYTES
    )
    result.update(
        {
            "schema": SCHEMA,
            "postfinal_schema": SCHEMA,
            "status": "PASS",
            "result": "PASS",
            "passed": True,
            "audit_source_path": SOURCE_RELATIVE,
            "audit_source_sha256": current_source_digest,
            "base_audit_source_path": source_v5.SOURCE_RELATIVE,
            "base_audit_source_sha256": v5_source_digest,
            "base_audit_report_path": source_v5.REPORT_RELATIVE,
            "base_audit_report_sha256": base_digest,
            "base_audit_postfinal_schema": source_v5.SCHEMA,
            "previous_v4_audit_source_path": previous.SOURCE_RELATIVE,
            "previous_v4_audit_source_sha256": PREVIOUS_SOURCE_SHA256,
            "previous_v4_source_report_path": source_v5.previous.REPORT_RELATIVE,
            "previous_v4_source_report_sha256": historical_v4_digest,
            "previous_v4_source_report_historical": True,
            "previous_v4_strict_report_created": False,
            "previous_v3_audit_report_path": legacy.REPORT_RELATIVE,
            "previous_v3_audit_report_sha256": historical_v3_digest,
            "previous_v3_audit_source_path": legacy.SOURCE_RELATIVE,
            "previous_v3_audit_source_sha256": previous.PREVIOUS_SOURCE_SHA256,
            "postfinal_wrapper_self_test": controls,
            "verified_core_family_count": base["verified_core_family_count"],
            "verified_distinct_pipeline_count": base["verified_distinct_pipeline_count"],
            "v5_allowed_locale_libc_primitives": sorted(source_v5.LOCALE_SYMBOLS),
            "v5_owned_locale_sources": dict(source_v5.OWNED_LOCALE_SOURCES),
            "scope": {
                **dict(scope),
                "immutable_v1_source_preserved": True,
                "immutable_v1_reports_mutated": False,
                "immutable_v2_reports_mutated": False,
                "immutable_v3_reports_mutated": False,
                "immutable_v4_reports_mutated": False,
                "previous_v4_source_report_historical": True,
                "base_v5_report_only": True,
                "production_report_path": REPORT_RELATIVE,
            },
            "supersedes": {
                "schema": previous.SCHEMA,
                "source_path": previous.SOURCE_RELATIVE,
                "source_sha256": PREVIOUS_SOURCE_SHA256,
                "source_preserved": True,
                "strict_report_created": False,
                "historical_source_report_path": source_v5.previous.REPORT_RELATIVE,
                "historical_source_report_sha256": historical_v4_digest,
            },
        }
    )
    legacy.require_candidate_free()
    return result


def write_report(report: Mapping[str, Any], target: Path) -> str:
    require(
        isinstance(target, Path)
        and target.name == REPORT_PATH.name
        and not target.is_symlink()
        and target.parent.resolve() == REPORT_PATH.parent.resolve(),
        "only the exact non-symlink exclusive V5 strict report is authorized",
    )
    parent = REPORT_PATH.parent
    require(not parent.is_symlink(), "the strict V5 report parent is a symlink")
    resolved = parent.resolve(strict=True)
    require(resolved.is_relative_to(ROOT.resolve(strict=True)), "the strict V5 report escaped its root")
    payload = previous.previous.canonical(report) + b"\n"
    require(len(payload) <= MAX_REPORT_BYTES, "the complete strict V5 report exceeds its bound")
    directory_flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    directory_flags |= getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    file_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    file_flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    directory = os.open(resolved, directory_flags)
    try:
        require(stat.S_ISDIR(os.fstat(directory).st_mode), "the strict V5 parent is not a directory")
        descriptor = os.open(REPORT_PATH.name, file_flags, 0o644, dir_fd=directory)
        try:
            view = memoryview(payload)
            while view:
                written = os.write(descriptor, view)
                require(written > 0, "the exclusive strict V5 report write stalled")
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
        previous.previous.require_candidate_free()
        if args.self_test:
            require(args.output == REPORT_PATH, "the V5 strict self-test cannot create a report")
            report = candidate_free_self_test()
            sys.stdout.buffer.write(previous.previous.canonical(report) + b"\n")
            return 0 if report["passed"] else 1
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
            "actual_strict_control_count": 32,
            "original_control_count": 76,
            "verified_family_count": len(report["families"]),
            "verified_native_role_count": len(report["native_elf_fingerprints"]),
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        }
        sys.stdout.buffer.write(previous.previous.canonical(summary) + b"\n")
        return 0
    except (
        source_v5.previous.previous.AuditV3Error,
        previous.previous.previous.AuditFailure,
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
        KeyError,
    ) as error:
        sys.stdout.buffer.write(
            previous.previous.canonical(
                {
                    "schema": SCHEMA,
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
