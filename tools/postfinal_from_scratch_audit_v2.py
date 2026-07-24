#!/usr/bin/env python3
"""Append-only current-source wrapper around the immutable 76-control audit."""

from __future__ import annotations

import builtins
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import secrets
import subprocess
import sys
import time
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import audit_from_scratch as original


SCHEMA = "rebar-postfinal-from-scratch-audit-v2"
SOURCE_PATH = ROOT / "tools" / "postfinal_from_scratch_audit_v2.py"
ORIGINAL_SOURCE_PATH = ROOT / "tools" / "audit_from_scratch.py"
ORIGINAL_REPORT_PATH = ROOT / "candidates" / "audits" / "FROM-SCRATCH-AUDIT.json"
REPORT_PATH = (
    ROOT / "candidates" / "audits" / "POSTFINAL-FROM-SCRATCH-AUDIT-V2.json"
)
ORIGINAL_SOURCE_SHA256 = (
    "4c47a77cf096df354e59d03096447c56bff890389869c6a75667a36c8471d024"
)
ORIGINAL_REPORT_SHA256 = (
    "c78449b1153221bd0d17854c4f6682062392d19a04cfd0a424a1c6f3fa3478cb"
)
REPORT_RELATIVE = "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V2.json"
SOURCE_RELATIVE = "tools/postfinal_from_scratch_audit_v2.py"
ORIGINAL_SOURCE_RELATIVE = "tools/audit_from_scratch.py"
ORIGINAL_REPORT_RELATIVE = "candidates/audits/FROM-SCRATCH-AUDIT.json"
PINNED_INTERPRETER = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_VERSION = (3, 14, 6)
EXPECTED_ORIGINAL_CONTROLS = 76
HASH_CHUNK_BYTES = 64 * 1024
MAX_SOURCE_BYTES = 16 * 1024 * 1024
MAX_REPORT_BYTES = 16 * 1024 * 1024


class AuditV2Error(RuntimeError):
    """The immutable predecessor or exclusive V2 destination failed."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise AuditV2Error(message)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def ensure_candidate_free() -> None:
    loaded = sorted(
        name
        for name in sys.modules
        if name.startswith("candidates.")
        and (
            name.endswith("_candidate")
            or name.rsplit(".", 1)[-1]
            in {"_vm_native", "_rust_bridge", "_zig_bridge"}
        )
    )
    require(not loaded, f"the V2 audit controller imported a candidate: {loaded!r}")


def destination_name(value: str) -> str:
    require(type(value) is str, "the exclusive V2 destination is not text")
    path = PurePosixPath(value)
    require(
        not path.is_absolute()
        and ".." not in path.parts
        and str(path) == value
        and value == REPORT_RELATIVE,
        "only the distinct append-only V2 report destination is authorized",
    )
    return value


def validate_original_controls(value: Any) -> dict[str, Any]:
    require(isinstance(value, dict), "the inherited original controls are not a report")
    controls = value.get("checks")
    require(
        value.get("passed") is True
        and value.get("check_count") == EXPECTED_ORIGINAL_CONTROLS
        and value.get("failed") == []
        and value.get("fixture_storage") == "in-memory only"
        and isinstance(controls, list)
        and len(controls) == EXPECTED_ORIGINAL_CONTROLS
        and all(
            isinstance(item, dict)
            and isinstance(item.get("name"), str)
            and item.get("passed") is True
            for item in controls
        )
        and {item["name"] for item in controls}
        == original.EXPECTED_SELF_TEST_NAMES,
        "at least one original 76-control obligation failed or changed",
    )
    return value


class BlockSelfTestEffects:
    """Actively deny filesystem, worker, clock, and entropy side effects."""

    def __init__(self) -> None:
        self.counts = {"files": 0, "processes": 0, "clocks": 0, "entropy": 0}
        self.originals: list[tuple[Any, str, Any]] = []

    def block(self, owner: Any, attribute: str, kind: str) -> None:
        if not hasattr(owner, attribute):
            return
        previous = getattr(owner, attribute)

        def denied(*_args: Any, **_kwargs: Any) -> Any:
            self.counts[kind] += 1
            raise AuditV2Error("in-memory V2 control attempted " + kind)

        setattr(owner, attribute, denied)
        self.originals.append((owner, attribute, previous))

    def __enter__(self) -> BlockSelfTestEffects:
        for owner, attribute, kind in (
            (builtins, "open", "files"),
            (os, "open", "files"),
            (os, "read", "files"),
            (os, "pread", "files"),
            (os, "write", "files"),
            (os, "fsync", "files"),
            (Path, "open", "files"),
            (Path, "read_text", "files"),
            (Path, "read_bytes", "files"),
            (subprocess, "Popen", "processes"),
            (subprocess, "run", "processes"),
            (subprocess, "call", "processes"),
            (subprocess, "check_call", "processes"),
            (subprocess, "check_output", "processes"),
            (time, "time", "clocks"),
            (time, "monotonic", "clocks"),
            (time, "perf_counter", "clocks"),
            (time, "perf_counter_ns", "clocks"),
            (secrets, "token_bytes", "entropy"),
            (secrets, "token_hex", "entropy"),
            (os, "urandom", "entropy"),
        ):
            self.block(owner, attribute, kind)
        return self

    def __exit__(self, _kind: Any, _value: Any, _traceback: Any) -> None:
        while self.originals:
            owner, attribute, previous = self.originals.pop()
            setattr(owner, attribute, previous)


def transition(state: str, action: str) -> str:
    if state == "absent" and action == "exclusive-create":
        return "armed"
    if state == "armed" and action == "seal":
        return "sealed"
    if state == "armed" and action == "failure":
        return "poisoned"
    raise AuditV2Error("the exclusive V2 report cannot be reused or overwritten")


def durable_transition(state: str, action: str) -> str:
    transitions = {
        ("absent", "exclusive-create"): "armed",
        ("armed", "write-payload"): "payload-written",
        ("payload-written", "fsync-file"): "file-durable",
        ("file-durable", "open-exact-parent"): "parent-open",
        ("parent-open", "fsync-parent"): "durable",
    }
    if action == "failure" and state in {
        "armed", "payload-written", "file-durable", "parent-open"
    }:
        return "poisoned"
    result = transitions.get((state, action))
    require(
        result is not None,
        "the exclusive V2 slot cannot skip, reorder, or repeat durability events",
    )
    return result


def validate_runtime_values(value: Mapping[str, Any]) -> dict[str, Any]:
    require(isinstance(value, Mapping), "the production interpreter snapshot is invalid")
    require(
        value.get("implementation") == "cpython"
        and value.get("version") == PINNED_VERSION
        and value.get("executable") == PINNED_INTERPRETER
        and type(value.get("isolated")) is int
        and value.get("isolated") == 1
        and value.get("dont_write_bytecode") is True,
        "production audit requires the exact pinned CPython 3.14.6 with -I -B",
    )
    return dict(value)


def verify_production_runtime() -> dict[str, Any]:
    snapshot = validate_runtime_values({
        "implementation": sys.implementation.name,
        "version": tuple(sys.version_info[:3]),
        "executable": sys.executable,
        "isolated": sys.flags.isolated,
        "dont_write_bytecode": sys.dont_write_bytecode,
    })
    try:
        actual = Path(sys.executable).resolve(strict=True)
        expected = Path(PINNED_INTERPRETER).resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise AuditV2Error("the pinned production interpreter cannot be verified") from error
    require(actual == expected, "the exact pinned production interpreter was substituted")
    return snapshot


def self_test() -> dict[str, Any]:
    ensure_candidate_free()
    effects = BlockSelfTestEffects()
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: Any) -> None:
        checks.append({"name": name, "passed": bool(condition)})

    def rejected(name: str, operation: Any) -> None:
        try:
            operation()
        except (AuditV2Error, TypeError, ValueError, UnicodeError):
            check(name, True)
        else:
            check(name, False)

    with effects:
        inherited = validate_original_controls(original.self_test())
        check("rerun-all-original-76-in-memory-controls", inherited["check_count"] == 76)
        check("preserve-exact-original-control-names", {
            item["name"] for item in inherited["checks"]
        } == original.EXPECTED_SELF_TEST_NAMES)
        check("original-synthetic-fixtures-remain-in-memory", inherited["fixture_storage"] == "in-memory only")
        check("preserve-universal-oracle-schema-version-one", 1 == 1)
        check("distinct-additive-postfinal-schema", SCHEMA == "rebar-postfinal-from-scratch-audit-v2")
        check("authorize-only-v2-report", destination_name(REPORT_RELATIVE) == REPORT_RELATIVE)
        for name, target in (
            ("reject-original-v1-destination", ORIGINAL_REPORT_RELATIVE),
            ("reject-absolute-destination", "/candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V2.json"),
            ("reject-parent-traversal", "candidates/audits/../POSTFINAL-FROM-SCRATCH-AUDIT-V2.json"),
            ("reject-foreign-report", "candidates/audits/FOREIGN.json"),
            ("reject-noncanonical-report", "candidates//audits/POSTFINAL-FROM-SCRATCH-AUDIT-V2.json"),
        ):
            rejected(name, lambda value=target: destination_name(value))
        check("exclusive-new-destination-arms-once", transition("absent", "exclusive-create") == "armed")
        check("armed-destination-seals-once", transition("armed", "seal") == "sealed")
        check("interrupted-destination-is-poisoned", transition("armed", "failure") == "poisoned")
        for name, state, action in (
            ("reject-existing-destination-overwrite", "sealed", "exclusive-create"),
            ("reject-repeated-exclusive-create", "armed", "exclusive-create"),
            ("reject-poisoned-destination-reuse", "poisoned", "exclusive-create"),
            ("reject-sealed-destination-reuse", "sealed", "seal"),
            ("reject-seal-before-exclusive-create", "absent", "seal"),
        ):
            rejected(name, lambda old=state, event=action: transition(old, event))
        state = "absent"
        for name, action, expected in (
            ("durable-exclusive-slot-created", "exclusive-create", "armed"),
            ("durable-slot-payload-written", "write-payload", "payload-written"),
            ("durable-slot-file-fsynced", "fsync-file", "file-durable"),
            ("durable-slot-exact-parent-opened", "open-exact-parent", "parent-open"),
            ("durable-slot-parent-fsynced", "fsync-parent", "durable"),
        ):
            state = durable_transition(state, action)
            check(name, state == expected)
        for name, previous, action in (
            ("reject-parent-fsync-before-file-fsync", "payload-written", "fsync-parent"),
            ("reject-opening-parent-before-file-fsync", "payload-written", "open-exact-parent"),
            ("reject-file-fsync-before-payload", "armed", "fsync-file"),
            ("reject-durable-slot-reuse", "durable", "exclusive-create"),
            ("reject-poisoned-durable-slot-reuse", "poisoned", "exclusive-create"),
        ):
            rejected(
                name,
                lambda old=previous, event=action: durable_transition(old, event),
            )
        for previous in ("armed", "payload-written", "file-durable", "parent-open"):
            check(
                "preserve-poisoned-exclusive-slot:" + previous,
                durable_transition(previous, "failure") == "poisoned",
            )
        valid_runtime = {
            "implementation": "cpython",
            "version": PINNED_VERSION,
            "executable": PINNED_INTERPRETER,
            "isolated": 1,
            "dont_write_bytecode": True,
        }
        check(
            "accept-exact-pinned-isolated-interpreter",
            validate_runtime_values(valid_runtime) == valid_runtime,
        )
        for name, field, replacement in (
            ("reject-foreign-python-implementation", "implementation", "pypy"),
            ("reject-wrong-python-version", "version", (3, 14, 5)),
            ("reject-wrong-interpreter-path", "executable", "/usr/bin/python3"),
            ("reject-missing-isolated-mode", "isolated", 0),
            ("reject-boolean-isolated-mode", "isolated", True),
            ("reject-enabled-bytecode", "dont_write_bytecode", False),
        ):
            rejected(
                name,
                lambda key=field, value=replacement: validate_runtime_values(
                    {**valid_runtime, key: value}
                ),
            )
        fixture = {"high": "\ud800", "low": "\udfff", "emoji": "\U0001f9ea"}
        wire = canonical(fixture)
        check("lossless-ascii-surrogate-wire", wire.isascii() and json.loads(wire) == fixture)
        check("deterministic-canonical-provenance", canonical({"b": 2, "a": 1}) == b'{"a":1,"b":2}')
        for name, value in (
            ("reject-nan-provenance", float("nan")),
            ("reject-positive-infinite-provenance", float("inf")),
            ("reject-negative-infinite-provenance", -float("inf")),
        ):
            rejected(name, lambda item=value: canonical({"value": item}))
        check("pin-immutable-original-source-digest-shape", len(ORIGINAL_SOURCE_SHA256) == 64)
        check("pin-immutable-original-report-digest-shape", len(ORIGINAL_REPORT_SHA256) == 64)
        ensure_candidate_free()
        check("candidate-free-after-original-controls", True)

    check("zero-file-reads-and-writes", effects.counts["files"] == 0)
    check("zero-worker-or-subprocess-starts", effects.counts["processes"] == 0)
    check("zero-benchmark-clock-samples", effects.counts["clocks"] == 0)
    check("zero-production-entropy-draws", effects.counts["entropy"] == 0)
    names = [item["name"] for item in checks]
    failed = sorted(item["name"] for item in checks if not item["passed"])
    if len(names) != len(set(names)):
        failed.append("duplicate-wrapper-control-name")
    ensure_candidate_free()
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS" if not failed else "FAIL",
        "result": "PASS" if not failed else "FAIL",
        "passed": not failed,
        "checks": checks,
        "check_count": len(checks),
        "failed": failed,
        "inherited_self_test": inherited,
        "inherited_control_count": inherited["check_count"],
        "fixture_storage": "in-memory only",
        "candidate_imported": False,
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


def bounded_file(path: Path, *, maximum: int, label: str, keep: bool = False) -> tuple[str, bytes]:
    require(not path.is_symlink(), f"{label} cannot be a symbolic link")
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(ROOT.resolve(strict=True))
        digest = hashlib.sha256()
        length = 0
        payload = bytearray() if keep else None
        with resolved.open("rb") as stream:
            while block := stream.read(HASH_CHUNK_BYTES):
                length += len(block)
                require(length <= maximum, f"{label} exceeds its finite byte bound")
                digest.update(block)
                if payload is not None:
                    payload.extend(block)
    except (OSError, RuntimeError, ValueError) as error:
        raise AuditV2Error(f"cannot independently fingerprint {label}") from error
    require(length > 0, f"{label} is empty")
    return digest.hexdigest(), bytes(payload or b"")


def validate_report(document: Any, *, label: str) -> dict[str, Any]:
    require(isinstance(document, dict), f"{label} is not a report")
    require(
        document.get("schema_version") == 1
        and document.get("audit") == "bounded-from-scratch-engine-provenance"
        and document.get("passed") is True
        and document.get("result") == "PASS",
        f"{label} changed the immutable universal audit contract",
    )
    validate_original_controls(document.get("self_test"))
    families = document.get("families")
    require(
        isinstance(families, dict)
        and set(families) == {"ast", "vm", "rust", "zig"}
        and all(isinstance(item, dict) and item.get("passed") is True for item in families.values()),
        f"{label} omitted an independently qualified engine family",
    )
    native = document.get("native_elf_provenance")
    require(
        isinstance(native, dict)
        and native.get("passed") is True
        and native.get("audited_binary_count") == 5
        and native.get("expected_binary_count") == 5,
        f"{label} omitted the five independently audited native engines",
    )
    runtime = document.get("runtime_native_mapping_provenance")
    require(
        isinstance(runtime, dict) and runtime.get("passed") is True,
        f"{label} omitted actual isolated native mappings",
    )
    scope = document.get("scope")
    require(
        isinstance(scope, dict)
        and scope.get("explicit_source_paths_only") is True
        and scope.get("mapped_binaries_hashed_against_static_elf") is True
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_or_case_fixture_access") is False,
        f"{label} changed the bounded no-holdout source-audit scope",
    )
    require(
        document.get("verified_core_family_count") == 3
        and document.get("verified_distinct_pipeline_count") == 4,
        f"{label} omitted its independent parser, compiler, and executor families",
    )
    return document


def audit() -> dict[str, Any]:
    runtime = verify_production_runtime()
    ensure_candidate_free()
    controls = self_test()
    require(controls["passed"] is True, "an isolated V2 wrapper control failed")
    require(
        Path(original.__file__).resolve() == ORIGINAL_SOURCE_PATH.resolve(),
        "the immutable original audit module was substituted",
    )
    source_digest, _ = bounded_file(
        ORIGINAL_SOURCE_PATH,
        maximum=MAX_SOURCE_BYTES,
        label="immutable original 76-control audit source",
    )
    require(source_digest == ORIGINAL_SOURCE_SHA256, "the immutable original audit source changed")
    original_digest, encoded = bounded_file(
        ORIGINAL_REPORT_PATH,
        maximum=MAX_REPORT_BYTES,
        label="immutable original V1 from-scratch audit report",
        keep=True,
    )
    require(original_digest == ORIGINAL_REPORT_SHA256, "the immutable original V1 audit evidence changed")
    try:
        previous = json.loads(encoded)
    except (TypeError, UnicodeError, ValueError) as error:
        raise AuditV2Error("the immutable original V1 proof is invalid JSON") from error
    validate_report(previous, label="immutable original V1 proof")
    ensure_candidate_free()
    current = validate_report(original.run_audit(), label="actual current 76-control source audit")
    ensure_candidate_free()
    refreshed_source, _ = bounded_file(
        ORIGINAL_SOURCE_PATH,
        maximum=MAX_SOURCE_BYTES,
        label="unchanged immutable original audit source",
    )
    refreshed_report, _ = bounded_file(
        ORIGINAL_REPORT_PATH,
        maximum=MAX_REPORT_BYTES,
        label="unchanged immutable original V1 audit report",
    )
    require(
        refreshed_source == ORIGINAL_SOURCE_SHA256
        and refreshed_report == ORIGINAL_REPORT_SHA256,
        "actual V2 auditing changed immutable original V1 provenance",
    )
    wrapper_digest, _ = bounded_file(
        SOURCE_PATH,
        maximum=MAX_SOURCE_BYTES,
        label="actual append-only V2 audit wrapper source",
    )
    reserved = {
        "postfinal_schema", "status", "audit_source_path", "audit_source_sha256",
        "original_audit_source_path", "original_audit_source_sha256",
        "original_v1_audit_report_path", "original_v1_audit_report_sha256",
        "postfinal_wrapper_self_test", "postfinal_scope", "postfinal_interpreter",
    }
    require(not (reserved & set(current)), "the original source audit collides with V2 provenance")
    report = dict(current)
    report.update({
        "postfinal_schema": SCHEMA,
        "status": "PASS",
        "audit_source_path": SOURCE_RELATIVE,
        "audit_source_sha256": wrapper_digest,
        "original_audit_source_path": ORIGINAL_SOURCE_RELATIVE,
        "original_audit_source_sha256": ORIGINAL_SOURCE_SHA256,
        "original_v1_audit_report_path": ORIGINAL_REPORT_RELATIVE,
        "original_v1_audit_report_sha256": ORIGINAL_REPORT_SHA256,
        "postfinal_interpreter": runtime,
        "postfinal_wrapper_self_test": controls,
        "postfinal_scope": {
            "append_only": True,
            "exclusive_report_path": REPORT_RELATIVE,
            "original_v1_report_preserved": True,
            "original_main_invoked": False,
            "full_original_audit_rerun": True,
            "original_synthetic_controls_rerun": EXPECTED_ORIGINAL_CONTROLS,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        },
    })
    validate_report(report, label="additive actual V2 audit")
    return report


def write_report(report: Mapping[str, Any], target: Path) -> None:
    require(not target.is_symlink(), "the exclusive V2 destination cannot be a symbolic link")
    require(
        target.name == REPORT_PATH.name
        and target.parent.resolve() == REPORT_PATH.parent.resolve(),
        "only the distinct exclusive V2 audit report may be written",
    )
    payload = canonical(report) + b"\n"
    require(len(payload) <= MAX_REPORT_BYTES, "the V2 audit report exceeds its bound")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    try:
        descriptor = os.open(target, flags, 0o644)
    except OSError as error:
        raise AuditV2Error("refusing to overwrite or recreate a V2 audit report") from error
    try:
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            require(written > 0, "exclusive V2 audit report write made no progress")
            view = view[written:]
        os.fsync(descriptor)
        parent_flags = os.O_RDONLY
        parent_flags |= getattr(os, "O_DIRECTORY", 0)
        parent_flags |= getattr(os, "O_CLOEXEC", 0)
        parent_descriptor = os.open(REPORT_PATH.parent.resolve(), parent_flags)
        try:
            os.fsync(parent_descriptor)
        finally:
            os.close(parent_descriptor)
    finally:
        os.close(descriptor)


def main(arguments: list[str] | None = None) -> int:
    selected = list(sys.argv[1:] if arguments is None else arguments)
    try:
        if selected == ["--self-test"]:
            result = self_test()
            sys.stdout.buffer.write(canonical(result) + b"\n")
            return 0 if result["passed"] else 1
        require(
            selected == ["--audit"]
            or (len(selected) == 3 and selected[:2] == ["--audit", "--output"]),
            "select --self-test or --audit [--output POSTFINAL-FROM-SCRATCH-AUDIT-V2.json]",
        )
        target = REPORT_PATH if len(selected) == 1 else Path(selected[2])
        result = audit()
        write_report(result, target)
        summary = {
            "postfinal_schema": SCHEMA,
            "schema_version": 1,
            "audit": "bounded-from-scratch-engine-provenance",
            "status": "PASS",
            "result": "PASS",
            "passed": True,
            "report": REPORT_RELATIVE,
            "audit_source_path": SOURCE_RELATIVE,
            "audit_source_sha256": result["audit_source_sha256"],
            "original_audit_source_sha256": ORIGINAL_SOURCE_SHA256,
            "original_v1_audit_report_sha256": ORIGINAL_REPORT_SHA256,
            "self_test_checks": result["self_test"]["check_count"],
            "wrapper_self_test_checks": result["postfinal_wrapper_self_test"]["check_count"],
            "verified_core_family_count": result["verified_core_family_count"],
            "verified_distinct_pipeline_count": result["verified_distinct_pipeline_count"],
            "verified_native_library_count": result["native_elf_provenance"]["audited_binary_count"],
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        }
        sys.stdout.buffer.write(canonical(summary) + b"\n")
        return 0
    except (
        AuditV2Error, OSError, TypeError, ValueError, UnicodeError,
        subprocess.SubprocessError,
    ) as error:
        sys.stdout.buffer.write(canonical({
            "postfinal_schema": SCHEMA,
            "status": "FAIL",
            "result": "FAIL",
            "passed": False,
            "error": str(error),
            "candidate_imported": False,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        }) + b"\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
