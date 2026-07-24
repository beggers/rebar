#!/usr/bin/env python3
"""Exclusively rerun genuine 32-control guards against the V4 source proof."""

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

from tools import postfinal_from_scratch_audit_v4 as source_v4
from tools import postfinal_no_delegation_audit_v3 as previous


SCHEMA = "rebar-postfinal-no-delegation-audit-v4"
SOURCE_RELATIVE = "tools/postfinal_no_delegation_audit_v4.py"
SOURCE_PATH = ROOT / SOURCE_RELATIVE
REPORT_RELATIVE = "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V4.json"
REPORT_PATH = ROOT / REPORT_RELATIVE
PREVIOUS_SOURCE_SHA256 = (
    "80d2450439893e1d6e1e2d1986cc59cc7da20e4d4c871f6670b31587da0f24f5"
)
PREVIOUS_REPORT_SHA256 = (
    "51f745b0cf4a1a91457d865b8fac26b71534f801ca6632b2fd762bd6933c6ab5"
)
MINIMUM_SOURCE_CONTROLS = source_v4.MINIMUM_PREVIOUS_CONTROLS
MAX_SOURCE_BYTES = previous.MAX_SOURCE_BYTES
MAX_REPORT_BYTES = previous.MAX_DOCUMENT_BYTES
ADDITIVE_PUBLIC_INPUTS = frozenset(
    {
        previous.REPORT_RELATIVE,
        source_v4.SOURCE_RELATIVE,
        source_v4.REPORT_RELATIVE,
        SOURCE_RELATIVE,
    }
)
PUBLIC_INPUTS = previous.PUBLIC_INPUTS | ADDITIVE_PUBLIC_INPUTS
ORIGINAL_CONTROL_BOOTSTRAP = r'''
import hashlib
import json
import sys
from pathlib import Path

if len(sys.argv) != 3:
    raise RuntimeError("the isolated original-control bootstrap is not exact")
root = Path(sys.argv[1]).resolve(strict=True)
expected = sys.argv[2]
if len(expected) != 64 or any(item not in "0123456789abcdef" for item in expected):
    raise RuntimeError("the isolated V4 source digest is not exact")
sys.path.insert(0, str(root))
from tools import postfinal_from_scratch_audit_v4 as source_v4
if source_v4.ROOT.resolve(strict=True) != root:
    raise RuntimeError("the isolated V4 source escaped the authenticated root")
with source_v4.SOURCE_PATH.open("rb") as stream:
    payload = stream.read(source_v4.MAX_SOURCE_BYTES + 1)
if len(payload) > source_v4.MAX_SOURCE_BYTES:
    raise RuntimeError("the isolated V4 source exceeds its bound")
if hashlib.sha256(payload).hexdigest() != expected:
    raise RuntimeError("the isolated V4 source fingerprint changed")
del payload
with source_v4.allow_owned_rust_locale_ctype():
    result = source_v4.previous.original.self_test()
sys.stdout.write(json.dumps(result, sort_keys=True) + "\n")
raise SystemExit(0 if result.get("passed") is True else 1)
'''


class AuditV4Error(previous.AuditFailure):
    """An additive V4 independence or provenance obligation failed."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise AuditV4Error(message)


def validate_public_relative(relative: Any) -> str:
    require(type(relative) is str, "the exact V4 public input is not text")
    path = PurePosixPath(relative)
    require(
        not path.is_absolute()
        and ".." not in path.parts
        and "\\" not in relative
        and "\x00" not in relative
        and str(path) == relative
        and relative in PUBLIC_INPUTS,
        "refusing a private, final, benchmark, foreign, or unapproved V4 input",
    )
    return relative


def relative_public_path(path: Path) -> str:
    require(
        isinstance(path, Path) and not path.is_symlink(),
        "an exact V4 public proof is missing or is a symlink",
    )
    try:
        resolved = path.resolve(strict=True)
        relative = resolved.relative_to(ROOT.resolve(strict=True)).as_posix()
    except (OSError, RuntimeError, ValueError) as error:
        raise AuditV4Error("an exact V4 public input escaped the repository") from error
    validate_public_relative(relative)
    require(resolved.is_file(), "an exact V4 public proof is not a regular file")
    return relative


def bounded_public_bytes(path: Path, *, maximum: int) -> tuple[bytes, str]:
    relative = relative_public_path(path)
    digest, payload = source_v4.previous.bounded_file(
        path,
        maximum=maximum,
        label="exact authenticated V4 public input: " + relative,
        keep=True,
    )
    return payload, digest


def public_document(path: Path) -> tuple[dict[str, Any], str]:
    payload, digest = bounded_public_bytes(path, maximum=MAX_REPORT_BYTES)
    return previous.decode_public_json(payload), digest


def adapt_original_control_command(command: Any, source_digest: Any) -> list[str]:
    original = source_v4.previous.original
    expected = [
        sys.executable,
        "-I",
        "-B",
        str(Path(original.__file__).resolve()),
        "--self-test",
    ]
    require(
        type(command) is list
        and len(command) == len(expected)
        and all(type(item) is str for item in command)
        and command == expected,
        "refusing a substituted original 76-control child command",
    )
    require(
        source_v4.previous.valid_sha256(source_digest),
        "refusing an unauthenticated original-control V4 bootstrap",
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
    original = source_v4.previous.original
    runner = original.subprocess.run
    original_source = str(Path(original.__file__).resolve())

    def run(command: Any, *args: Any, **kwargs: Any) -> Any:
        if isinstance(command, (list, tuple)) and original_source in command:
            return runner(
                adapt_original_control_command(command, source_digest),
                *args,
                **kwargs,
            )
        return runner(command, *args, **kwargs)

    original.subprocess.run = run
    try:
        yield
    finally:
        original.subprocess.run = runner


def destination_name(value: Any) -> str:
    require(type(value) is str, "the exclusive strict V4 destination is not text")
    path = PurePosixPath(value)
    require(
        not path.is_absolute()
        and ".." not in path.parts
        and "\\" not in value
        and "\x00" not in value
        and str(path) == value
        and value == REPORT_RELATIVE,
        "only the exact canonical V4 no-delegation report is authorized",
    )
    return value


def validate_historical_v3(document: Any) -> dict[str, Any]:
    require(isinstance(document, dict), "the immutable strict V3 report is missing")
    expected = {
        "schema": previous.SCHEMA,
        "postfinal_schema": previous.SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "audit_source_path": previous.SOURCE_RELATIVE,
        "audit_source_sha256": PREVIOUS_SOURCE_SHA256,
        "base_audit_postfinal_schema": source_v4.previous.SCHEMA,
        "base_audit_source_path": source_v4.previous.SOURCE_RELATIVE,
        "base_audit_source_sha256": source_v4.PREVIOUS_SOURCE_SHA256,
        "base_audit_report_path": source_v4.previous.REPORT_RELATIVE,
        "base_audit_report_sha256": source_v4.PREVIOUS_REPORT_SHA256,
        "inherited_control_count": len(previous.previous.BASE_CONTROL_NAMES),
    }
    for key, value in expected.items():
        require(
            document.get(key) == value and type(document.get(key)) is type(value),
            "the immutable V3 strict report changed " + key,
        )
    previous.previous.validate_controls(
        document,
        names=previous.previous.STRICT_CONTROL_NAMES,
        label="the complete immutable V3 32-control independence proof",
    )
    inherited = document.get("inherited_self_test")
    previous.previous.validate_controls(
        {"self_test": inherited},
        names=previous.previous.BASE_CONTROL_NAMES,
        label="the immutable V3 inherited original 76 controls",
    )
    previous._validate_flattened_native(document, label="the immutable V3 five-role native proof")
    return document


def candidate_free_self_test() -> dict[str, Any]:
    previous.verify_pinned_runtime()
    previous.require_candidate_free()
    effects = source_v4.previous.previous.BlockSelfTestEffects()
    checks: list[dict[str, Any]] = []

    def check(name: str, value: Any) -> None:
        checks.append({"name": name, "passed": bool(value)})

    def rejected(name: str, operation: Any) -> None:
        try:
            operation()
        except (
            source_v4.previous.AuditV3Error,
            previous.AuditFailure,
            TypeError,
            ValueError,
            KeyError,
            UnicodeError,
        ):
            check(name, True)
        else:
            check(name, False)

    with effects:
        inherited_source = source_v4.self_test()
        source_v4.validate_v4_controls(inherited_source)
        inherited_strict = previous.candidate_free_self_test()
        require(
            isinstance(inherited_strict, dict)
            and inherited_strict.get("schema") == previous.SCHEMA + "-self-test"
            and inherited_strict.get("passed") is True
            and inherited_strict.get("failed") == []
            and inherited_strict.get("candidate_imports") == 0
            and inherited_strict.get("subprocesses") == 0
            and inherited_strict.get("file_reads") == 0
            and inherited_strict.get("file_writes") == 0,
            "the immutable strict V3 in-memory poison controls did not pass",
        )
        for item in inherited_source["checks"]:
            check("source-v4:" + item["name"], item["passed"] is True)
        for item in inherited_strict["checks"]:
            check("strict-v3:" + item["name"], item["passed"] is True)
        check("preserve-exact-32-actual-strict-control-names", len(previous.previous.STRICT_CONTROL_NAMES) == 32)
        check("preserve-exact-76-original-control-names", len(previous.previous.BASE_CONTROL_NAMES) == 76)
        check("preserve-at-least-129-source-controls", inherited_source["inherited_v3_control_count"] >= 129)
        check("preserve-four-independent-source-families", previous.previous.AUDITED_FAMILIES == ("ast", "vm", "rust", "zig"))
        check("preserve-three-independent-native-families", previous.previous.QUALIFIED_FAMILIES == ("vm", "rust", "zig"))
        check("preserve-five-actual-native-role-identities", len(previous.previous.EXPECTED_NATIVE_KEYS) == 5)
        check("allow-only-authenticated-owned-locale-primitives", source_v4.ALLOWED_LOCALE_LIBC_PRIMITIVES == frozenset({"tolower", "isalnum"}))
        check("pin-exact-immutable-strict-v3-source-shape", previous.previous.valid_sha256(PREVIOUS_SOURCE_SHA256))
        check("pin-exact-immutable-strict-v3-report-shape", previous.previous.valid_sha256(PREVIOUS_REPORT_SHA256))
        original_control_command = [
            sys.executable,
            "-I",
            "-B",
            str(Path(source_v4.previous.original.__file__).resolve()),
            "--self-test",
        ]
        adapted = adapt_original_control_command(
            original_control_command,
            source_v4.PREVIOUS_SOURCE_SHA256,
        )
        check(
            "preserve-fresh-pinned-isolated-original-76-control-child",
            adapted[:4] == [sys.executable, "-I", "-B", "-c"]
            and adapted[4] == ORIGINAL_CONTROL_BOOTSTRAP
            and adapted[5] == str(ROOT)
            and adapted[6] == source_v4.PREVIOUS_SOURCE_SHA256,
        )
        check(
            "bootstrap-retains-exact-transparent-owned-libc-allowance",
            "source_v4.allow_owned_rust_locale_ctype()" in ORIGINAL_CONTROL_BOOTSTRAP
            and "source_v4.previous.original.self_test()" in ORIGINAL_CONTROL_BOOTSTRAP
            and "hashlib.sha256(payload).hexdigest() != expected"
            in ORIGINAL_CONTROL_BOOTSTRAP,
        )
        for label, command, digest in (
            (
                "reject-original-child-without-isolation",
                [sys.executable, "-B", original_control_command[3], "--self-test"],
                source_v4.PREVIOUS_SOURCE_SHA256,
            ),
            (
                "reject-original-child-without-bytecode-guard",
                [sys.executable, "-I", original_control_command[3], "--self-test"],
                source_v4.PREVIOUS_SOURCE_SHA256,
            ),
            (
                "reject-original-child-with-foreign-source",
                [sys.executable, "-I", "-B", "/tmp/foreign-audit.py", "--self-test"],
                source_v4.PREVIOUS_SOURCE_SHA256,
            ),
            (
                "reject-original-child-with-substituted-command",
                [sys.executable, "-I", "-B", original_control_command[3], "--audit"],
                source_v4.PREVIOUS_SOURCE_SHA256,
            ),
            (
                "reject-original-child-with-extra-arguments",
                original_control_command + ["foreign"],
                source_v4.PREVIOUS_SOURCE_SHA256,
            ),
            (
                "reject-original-child-with-invalid-source-hash",
                original_control_command,
                "not-a-sha256",
            ),
            (
                "reject-original-child-with-nontext-source-hash",
                original_control_command,
                4,
            ),
            (
                "reject-original-child-with-tuple-command",
                tuple(original_control_command),
                source_v4.PREVIOUS_SOURCE_SHA256,
            ),
        ):
            rejected(
                label,
                lambda item=command, fingerprint=digest: adapt_original_control_command(
                    item, fingerprint
                ),
            )
        check(
            "preserve-exact-immutable-v3-public-input-allowlist",
            previous.PUBLIC_INPUTS.issubset(PUBLIC_INPUTS),
        )
        check(
            "admit-only-four-exact-additive-v4-public-inputs",
            PUBLIC_INPUTS - previous.PUBLIC_INPUTS == ADDITIVE_PUBLIC_INPUTS,
        )
        for label, value in (
            ("accept-exact-historical-v3-strict-report", previous.REPORT_RELATIVE),
            ("accept-exact-v4-source-controller", source_v4.SOURCE_RELATIVE),
            ("accept-exact-v4-authenticated-source-proof", source_v4.REPORT_RELATIVE),
            ("accept-exact-v4-strict-controller", SOURCE_RELATIVE),
        ):
            check(label, validate_public_relative(value) == value)
        for label, value in (
            ("reject-private-proof-input", "sealed/private/cases.json"),
            ("reject-hidden-proof-input", "sealed/holdout/cases.json"),
            ("reject-final-proof-input", "sealed/final/cases.json"),
            ("reject-benchmark-proof-input", "benchmarks/cases.json"),
            ("reject-foreign-audit-input", "candidates/audits/FOREIGN.json"),
            ("reject-absolute-public-input", "/" + source_v4.REPORT_RELATIVE),
            ("reject-traversing-public-input", "candidates/audits/../POSTFINAL-FROM-SCRATCH-AUDIT-V4.json"),
            ("reject-noncanonical-public-input", "candidates//audits/POSTFINAL-FROM-SCRATCH-AUDIT-V4.json"),
            ("reject-backslash-public-input", "candidates\\audits\\POSTFINAL-FROM-SCRATCH-AUDIT-V4.json"),
            ("reject-nul-public-input", source_v4.REPORT_RELATIVE + "\x00"),
            ("reject-nontext-public-input", 4),
        ):
            rejected(label, lambda item=value: validate_public_relative(item))
        check("accept-exclusive-v4-strict-report", destination_name(REPORT_RELATIVE) == REPORT_RELATIVE)
        for label, value in (
            ("reject-v3-strict-report-overwrite", previous.REPORT_RELATIVE),
            ("reject-v4-source-report-substitution", source_v4.REPORT_RELATIVE),
            ("reject-absolute-strict-report", "/" + REPORT_RELATIVE),
            ("reject-parent-traversal-strict-report", "candidates/audits/../POSTFINAL-NO-DELEGATION-AUDIT-V4.json"),
            ("reject-noncanonical-strict-report", "candidates//audits/POSTFINAL-NO-DELEGATION-AUDIT-V4.json"),
            ("reject-foreign-strict-report", "candidates/audits/FOREIGN.json"),
            ("reject-nontext-strict-report", 4),
        ):
            rejected(label, lambda item=value: destination_name(item))
        previous.require_candidate_free()

    check("zero-evidence-file-reads", effects.counts["files"] == 0)
    check("zero-evidence-file-writes", effects.counts["files"] == 0)
    check("zero-worker-or-subprocess-starts", effects.counts["processes"] == 0)
    check("zero-benchmark-clock-samples", effects.counts["clocks"] == 0)
    check("zero-entropy-draws", effects.counts["entropy"] == 0)
    names = [item["name"] for item in checks]
    failed = sorted(item["name"] for item in checks if not item["passed"])
    if len(names) != len(set(names)):
        failed.append("duplicate-strict-v4-control-name")
    previous.require_candidate_free()
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS" if not failed else "FAIL",
        "result": "PASS" if not failed else "FAIL",
        "passed": not failed,
        "checks": checks,
        "check_count": len(checks),
        "failed": failed,
        "source_v4_self_test": inherited_source,
        "inherited_v3_self_test": inherited_strict,
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
    previous.require_candidate_free()
    previous.verify_pinned_runtime()
    v3_source_payload, v3_source_digest = bounded_public_bytes(
        previous.SOURCE, maximum=MAX_SOURCE_BYTES
    )
    require(v3_source_digest == PREVIOUS_SOURCE_SHA256, "the immutable strict V3 controller changed")
    del v3_source_payload
    historical, historical_digest = public_document(previous.REPORT)
    require(historical_digest == PREVIOUS_REPORT_SHA256, "the immutable strict V3 report changed")
    validate_historical_v3(historical)
    del historical
    previous.validated_v3_base()

    base, base_digest = public_document(source_v4.REPORT_PATH)
    source_v4.validate_v4_report(base, label="the actual complete V4 source audit")
    _v4_source, v4_source_digest = bounded_public_bytes(
        source_v4.SOURCE_PATH, maximum=MAX_SOURCE_BYTES
    )
    require(
        base.get("audit_source_sha256") == v4_source_digest,
        "the actual V4 source audit is not bound to its live controller",
    )
    del _v4_source
    controls = candidate_free_self_test()
    require(controls.get("passed") is True, "the V4 strict poison controls failed")

    immutable = previous.previous.import_pinned_strict_v1()
    actual_controls = immutable.self_test()
    previous.previous.validate_controls(
        {"self_test": actual_controls},
        names=previous.previous.STRICT_CONTROL_NAMES,
        label="the actual immutable 32-control V4 independence self-test",
    )
    saved_loader = immutable._load_original_report
    saved_report = immutable.original.REPORT
    require(
        isinstance(saved_report, Path)
        and saved_report.resolve() == previous.previous.ORIGINAL_BASE_REPORT.resolve(),
        "the immutable original strict worker was already rebound",
    )

    def load_authenticated_v4_base() -> tuple[dict[str, Any], str]:
        current, digest = public_document(source_v4.REPORT_PATH)
        require(
            digest == base_digest and current == base,
            "the authenticated V4 source audit changed during guarded execution",
        )
        source_v4.validate_v4_report(current, label="the continuously authenticated V4 source audit")
        return current, digest

    immutable._load_original_report = load_authenticated_v4_base
    immutable.original.REPORT = source_v4.REPORT_PATH
    try:
        gc.collect()
        with source_v4.allow_owned_rust_locale_ctype():
            with scoped_original_control_bootstrap(v4_source_digest):
                result = immutable.run_audit()
    finally:
        immutable.original.REPORT = saved_report
        immutable._load_original_report = saved_loader
    previous.require_candidate_free()
    require(
        isinstance(result, dict)
        and result.get("schema") == previous.previous.IMMUTABLE_STRICT_SCHEMA
        and result.get("passed") is True
        and result.get("result") == "PASS"
        and result.get("inherited_control_count") == 76,
        "the immutable V4 guarded worker did not complete all original controls",
    )
    previous.previous.validate_controls(
        result,
        names=previous.previous.STRICT_CONTROL_NAMES,
        label="the actual 32-control V4 no-delegation result",
    )
    previous.previous.validate_controls(
        {"self_test": result.get("inherited_self_test")},
        names=previous.previous.BASE_CONTROL_NAMES,
        label="the actual independently rerun 76 original V4 controls",
    )
    require(
        result.get("base_audit_report_path") == source_v4.REPORT_RELATIVE
        and result.get("base_audit_report_sha256") == base_digest,
        "the immutable strict worker did not consume the exact V4 source audit",
    )
    previous.previous._verify_result_native(result, base)
    previous._validate_flattened_native(result, label="the actual five-role V4 strict proof")
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
        "the V4 proof weakened actual source, engine, mapping, or worker isolation",
    )
    _source, source_digest = bounded_public_bytes(
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
            "audit_source_sha256": source_digest,
            "base_audit_source_path": source_v4.SOURCE_RELATIVE,
            "base_audit_source_sha256": v4_source_digest,
            "base_audit_report_path": source_v4.REPORT_RELATIVE,
            "base_audit_report_sha256": base_digest,
            "base_audit_postfinal_schema": source_v4.SCHEMA,
            "previous_v3_audit_source_path": previous.SOURCE_RELATIVE,
            "previous_v3_audit_source_sha256": PREVIOUS_SOURCE_SHA256,
            "previous_v3_audit_report_path": previous.REPORT_RELATIVE,
            "previous_v3_audit_report_sha256": PREVIOUS_REPORT_SHA256,
            "previous_v3_postfinal_schema": previous.SCHEMA,
            "postfinal_wrapper_self_test": controls,
            "v4_allowed_rust_libc_primitives": sorted(source_v4.ALLOWED_LOCALE_LIBC_PRIMITIVES),
            "scope": {
                **dict(scope),
                "immutable_v1_source_preserved": True,
                "immutable_v1_reports_mutated": False,
                "immutable_v2_reports_mutated": False,
                "immutable_v3_reports_mutated": False,
                "base_v4_report_only": True,
                "production_report_path": REPORT_RELATIVE,
            },
            "supersedes": {
                "schema": previous.SCHEMA,
                "source_path": previous.SOURCE_RELATIVE,
                "source_sha256": PREVIOUS_SOURCE_SHA256,
                "report_path": previous.REPORT_RELATIVE,
                "report_sha256": historical_digest,
                "report_preserved": True,
            },
        }
    )
    previous.require_candidate_free()
    return result


def write_report(report: Mapping[str, Any], target: Path) -> str:
    require(isinstance(target, Path), "the V4 strict evidence target is not a path")
    require(
        target.name == REPORT_PATH.name
        and not target.is_symlink()
        and target.parent.resolve() == REPORT_PATH.parent.resolve(),
        "only the exact non-symlink V4 strict report may be created",
    )
    parent = REPORT_PATH.parent
    require(not parent.is_symlink(), "the exclusive V4 strict directory is a symlink")
    resolved = parent.resolve(strict=True)
    require(resolved.is_relative_to(ROOT.resolve(strict=True)), "the V4 strict report escaped the repository")
    payload = previous.canonical(report) + b"\n"
    require(len(payload) <= MAX_REPORT_BYTES, "the V4 strict evidence exceeds its bound")
    directory_flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    directory_flags |= getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    file_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    file_flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    parent_fd = os.open(resolved, directory_flags)
    try:
        require(stat.S_ISDIR(os.fstat(parent_fd).st_mode), "the V4 strict parent is not a directory")
        descriptor = os.open(REPORT_PATH.name, file_flags, 0o644, dir_fd=parent_fd)
        try:
            view = memoryview(payload)
            while view:
                count = os.write(descriptor, view)
                require(count > 0, "the exclusive V4 strict write made no progress")
                view = view[count:]
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
        previous.require_candidate_free()
        if args.self_test:
            require(args.output == REPORT_PATH, "the V4 strict self-test cannot select an output")
            result = candidate_free_self_test()
            sys.stdout.buffer.write(previous.canonical(result) + b"\n")
            return 0 if result["passed"] else 1
        result = run_audit()
        digest = write_report(result, args.output)
        summary = {
            "schema": SCHEMA,
            "postfinal_schema": SCHEMA,
            "status": "PASS",
            "result": "PASS",
            "passed": True,
            "report": REPORT_RELATIVE,
            "report_sha256": digest,
            "audit_source_sha256": result["audit_source_sha256"],
            "base_audit_report_sha256": result["base_audit_report_sha256"],
            "previous_v3_audit_report_sha256": PREVIOUS_REPORT_SHA256,
            "actual_strict_control_count": len(previous.previous.STRICT_CONTROL_NAMES),
            "original_control_count": len(previous.previous.BASE_CONTROL_NAMES),
            "verified_family_count": len(result["families"]),
            "verified_native_role_count": len(result["native_elf_fingerprints"]),
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        }
        sys.stdout.buffer.write(previous.canonical(summary) + b"\n")
        return 0
    except (
        source_v4.previous.AuditV3Error,
        previous.previous.AuditFailure,
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
        KeyError,
    ) as error:
        sys.stdout.buffer.write(
            previous.canonical(
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
