#!/usr/bin/env python3
"""Run the immutable sealed campaign with a current, source-bound V3 audit.

The original 22-stage campaign and every historical correctness report remain
unchanged.  This additive entry point replaces only its static-audit provider:
an existing, exclusively produced V3 report is fully verified, all owned
source and native-library bytes are rehashed, and the actual edge-qualified
candidate artifacts are compared before any sealed correctness step runs.

The self-test uses synthetic in-memory reports only.  It cannot run an audit,
start a candidate, create a report, take a timing, or inspect a final holdout.
"""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import Any, Iterator, Mapping
from unittest import mock

from tools import audit_from_scratch as scratch
from tools import postfinal_from_scratch_audit_v3 as audit_v3
from tools import rust_v8_multi_candidate_campaign as original


ROOT = original.ROOT
SOURCE_PATH = Path(__file__).resolve()
LEGACY_SOURCE_PATH = ROOT / "tools" / "rust_v8_multi_candidate_campaign.py"
LEGACY_SOURCE_SHA256 = (
    "46e53abac0d2347d5fc505aa792a5ee5f55489a6e73b1f57edf37a93a0a6d45d"
)
V3_SOURCE_PATH = ROOT / "tools" / "postfinal_from_scratch_audit_v3.py"
V3_SOURCE_SHA256 = (
    "d8230d1f0272bffc6ef2fb61136935047a4d4008afd8a66291c87c48b7a36767"
)
V3_REPORT_PATH = (
    ROOT / "candidates" / "audits" / "POSTFINAL-FROM-SCRATCH-AUDIT-V3.json"
)
V3_REPORT_SHA256 = (
    "f1a1f2402819d85d0d9135b0fc2b89aecd2212bb3259700bf7628cb881a32f05"
)
SELF_TEST_SCHEMA = "rebar-v8-multi-candidate-sealed-campaign-postfinal-v2-self-test"
MAX_NATIVE_BYTES = 64 * 1024 * 1024

_ORIGINAL_STATIC_FAMILY_AUDIT = original.static_family_audit


def require(condition: Any, message: str) -> None:
    """Retain the historical sealed campaign's fail-closed error semantics."""

    original.require(bool(condition), message)


def _relative(path: Path) -> str:
    resolved = path.resolve()
    require(
        resolved.is_relative_to(ROOT.resolve()),
        "the sealed V3 audit escaped its exact repository-owned path",
    )
    return resolved.relative_to(ROOT.resolve()).as_posix()


def _valid_relative(value: Any, expected: Path, label: str) -> str:
    require(isinstance(value, str), f"the {label} path is not public text")
    relative = PurePosixPath(value)
    require(
        not relative.is_absolute()
        and ".." not in relative.parts
        and "\\" not in value
        and "\x00" not in value
        and relative.as_posix() == value
        and value == _relative(expected),
        f"the sealed V3 {label} source was substituted or escaped",
    )
    return value


def _bounded_digest(path: Path, *, maximum: int, label: str) -> str:
    require(isinstance(path, Path), f"the sealed V3 {label} is not an owned path")
    require(not path.is_symlink(), f"the sealed V3 {label} cannot be a symlink")
    digest, _payload = audit_v3.bounded_file(
        path,
        maximum=maximum,
        label=f"sealed V3 {label}",
    )
    require(audit_v3.valid_sha256(digest), f"invalid sealed V3 {label} fingerprint")
    return digest


def _expected_edge_paths(family: str) -> dict[str, Path]:
    require(family in {"rust", "vm", "zig"}, "the edge family is not independently native")
    sources = scratch.PYTHON_SOURCES
    binaries = scratch.NATIVE_BINARIES
    if family == "rust":
        return {
            "public-python": sources["rust"],
            "native-source": ROOT / "candidates" / "rust" / "src" / "lib.rs",
            "bridge-source": ROOT / "candidates" / "rust" / "py_bridge.c",
            "native-bridge": binaries["rust"]["bridge"],
            "native-engine": binaries["rust"]["engine"],
        }
    if family == "vm":
        return {
            "public-python": sources["vm"],
            "native-bridge": binaries["vm"]["native"],
        }
    return {
        "public-python": sources["zig"],
        "native-bridge": binaries["zig"]["bridge"],
        "native-engine": binaries["zig"]["engine"],
    }


def _validate_source_record(
    record: Any,
    expected: Path,
    *,
    family: str,
    verify_live_bytes: bool,
) -> tuple[str, str]:
    require(isinstance(record, dict), f"the {family} source evidence is missing")
    relative = _valid_relative(record.get("file"), expected, f"{family} owned")
    digest = record.get("sha256")
    require(
        record.get("passed") is True
        and record.get("issues") == []
        and audit_v3.valid_sha256(digest),
        f"the {family} independently owned source failed its V3 audit",
    )
    if verify_live_bytes:
        require(
            _bounded_digest(
                expected,
                maximum=audit_v3.MAX_SOURCE_BYTES,
                label=f"{family} production source {relative}",
            )
            == digest,
            f"the {family} source changed after its passing V3 audit: {relative}",
        )
    return relative, digest


def _validate_current_document(
    evidence: Mapping[str, Any],
    module: str,
    edge: Mapping[str, Any],
    *,
    observed_report_sha256: str,
    expected_report_sha256: str,
    observed_source_sha256: str,
    expected_source_sha256: str,
    verify_live_bytes: bool,
) -> dict[str, Any]:
    """Validate all four pipelines, five real ELFs, and exact edge provenance."""

    require(module in original.MODULES, "the V3 static audit selected a foreign engine")
    require(
        audit_v3.valid_sha256(observed_report_sha256)
        and audit_v3.valid_sha256(expected_report_sha256)
        and observed_report_sha256 == expected_report_sha256,
        "the complete current V3 from-scratch report was stale or substituted",
    )
    require(
        audit_v3.valid_sha256(observed_source_sha256)
        and audit_v3.valid_sha256(expected_source_sha256)
        and observed_source_sha256 == expected_source_sha256,
        "the complete current V3 from-scratch verifier was stale or substituted",
    )
    try:
        report = audit_v3.validate_v3_report(
            evidence,
            label="sealed campaign current source-bound V3 audit",
        )
    except audit_v3.AuditV3Error as error:
        raise AssertionError("the complete source-bound V3 audit did not pass") from error
    require(
        report.get("audit_source_sha256") == observed_source_sha256
        and report.get("schema_version") == 1
        and report.get("postfinal_schema") == audit_v3.SCHEMA
        and report.get("audit_source_path") == audit_v3.SOURCE_RELATIVE
        and report.get("status") == "PASS"
        and report.get("result") == "PASS"
        and report.get("passed") is True
        and report.get("verified_core_family_count") == 3
        and report.get("verified_distinct_pipeline_count") == 4
        and report.get("minimum_required_independent_families") == 3
        and set(report.get("all_public_source_families", ()))
        == {"ast", "vm", "rust", "zig"},
        "the sealed campaign V3 report lost its four independently owned pipelines",
    )
    controls = report.get("self_test")
    require(
        isinstance(controls, dict)
        and controls.get("passed") is True
        and controls.get("check_count") == 76
        and controls.get("failed") == [],
        "the sealed V3 report omitted the immutable 76 malicious-source controls",
    )
    wrapper = report.get("postfinal_wrapper_self_test")
    require(
        isinstance(wrapper, dict)
        and wrapper.get("passed") is True
        and type(wrapper.get("check_count")) is int
        and wrapper["check_count"] >= audit_v3.MINIMUM_PREVIOUS_WRAPPER_CONTROLS
        and wrapper.get("failed") == []
        and wrapper.get("candidate_imported") is False
        and wrapper.get("file_reads") == 0
        and wrapper.get("subprocesses") == 0
        and wrapper.get("benchmark_or_timing_executed") is False
        and wrapper.get("holdout_or_case_fixture_access") is False,
        "the sealed campaign V3 wrapper controls were missing or unsafe",
    )

    families = report.get("families")
    require(
        isinstance(families, dict)
        and set(families) == {"ast", "vm", "rust", "zig"},
        "the sealed V3 source graph omitted an independently owned family",
    )
    source_digests: dict[str, str] = {}
    for family in ("ast", "vm", "rust", "zig"):
        details = families[family]
        require(
            isinstance(details, dict) and details.get("passed") is True,
            f"the independently owned {family} production family failed",
        )
        pipeline = details.get("owned_pipeline")
        require(
            isinstance(pipeline, dict)
            and pipeline.get("passed") is True
            and pipeline.get("issues") == []
            and all(
                isinstance(pipeline.get(role), str) and bool(pipeline[role])
                for role in ("parser", "compiler", "executor")
            ),
            f"the {family} candidate lost its owned parser, compiler, or executor",
        )
        runtime = details.get("isolated_runtime")
        require(
            isinstance(runtime, dict) and runtime.get("passed") is True,
            f"the {family} isolated production runtime failed",
        )
        python_source = scratch.PYTHON_SOURCES[family]
        relative, digest = _validate_source_record(
            details.get("python_source"),
            python_source,
            family=family,
            verify_live_bytes=verify_live_bytes,
        )
        require(relative not in source_digests, "candidate families shared a source")
        source_digests[relative] = digest

        entries = details.get("native_sources", [])
        expected_paths = tuple(scratch.NATIVE_SOURCES.get(family, ()))
        require(
            isinstance(entries, list) and len(entries) == len(expected_paths),
            f"the {family} candidate hid or added a native production source",
        )
        expected_by_path = {_relative(path): path for path in expected_paths}
        observed_paths: set[str] = set()
        for entry in entries:
            require(isinstance(entry, dict), "a sealed native source is not an object")
            relative_name = entry.get("file")
            require(
                isinstance(relative_name, str)
                and relative_name in expected_by_path
                and relative_name not in observed_paths,
                f"the {family} native source was foreign, duplicated, or omitted",
            )
            relative, digest = _validate_source_record(
                entry,
                expected_by_path[relative_name],
                family=family,
                verify_live_bytes=verify_live_bytes,
            )
            require(relative not in source_digests, "native candidate sources were shared")
            observed_paths.add(relative)
            source_digests[relative] = digest
        require(
            observed_paths == set(expected_by_path),
            f"the {family} source graph is not closed",
        )

    native = report.get("native_elf_provenance")
    require(
        isinstance(native, dict)
        and native.get("passed") is True
        and native.get("issues") == []
        and native.get("audited_binary_count") == 5
        and native.get("expected_binary_count") == 5
        and isinstance(native.get("families"), dict)
        and set(native["families"]) == {"rust", "vm", "zig"},
        "the sealed V3 audit omitted an independently parsed native ELF",
    )
    native_digests: dict[str, str] = {}
    for family in ("rust", "vm", "zig"):
        static = native["families"][family]
        expected_binaries = scratch.NATIVE_BINARIES[family]
        require(
            isinstance(static, dict)
            and static.get("passed") is True
            and static.get("issues") == []
            and isinstance(static.get("files"), dict)
            and set(static["files"]) == set(expected_binaries),
            f"the {family} sealed V3 native role graph is incomplete",
        )
        mappings = families[family]["isolated_runtime"].get(
            "native_mapping_provenance"
        )
        require(
            isinstance(mappings, dict)
            and mappings.get("passed") is True
            and mappings.get("issues") == []
            and mappings.get("source") == "/proc/self/maps"
            and mappings.get("expected_owned_mapping_count")
            == len(expected_binaries)
            and mappings.get("observed_owned_mapping_count")
            == len(expected_binaries)
            and isinstance(mappings.get("observed_owned_mappings"), list)
            and len(mappings["observed_owned_mappings"]) == len(expected_binaries),
            f"the {family} sealed V3 runtime did not map every actual owned ELF",
        )
        observed_mappings: dict[str, dict[str, Any]] = {}
        for mapping in mappings["observed_owned_mappings"]:
            require(isinstance(mapping, dict), "a mapped candidate ELF is malformed")
            role = mapping.get("role")
            require(
                isinstance(role, str)
                and role in expected_binaries
                and role not in observed_mappings,
                f"the {family} native mapping role was substituted or duplicated",
            )
            observed_mappings[role] = mapping
        require(
            set(observed_mappings) == set(expected_binaries),
            f"the {family} sealed V3 runtime omitted a native mapping",
        )
        for role, expected in expected_binaries.items():
            item = static["files"][role]
            require(isinstance(item, dict), "a candidate static ELF is malformed")
            relative = _valid_relative(item.get("file"), expected, f"{family}/{role} ELF")
            digest = item.get("sha256")
            require(
                audit_v3.valid_sha256(digest)
                and item.get("forbidden_regex_symbols") == []
                and item.get("cross_candidate_symbols") == [],
                f"the {family}/{role} ELF delegates, shares matching, or has no hash",
            )
            mapping = observed_mappings[role]
            require(
                mapping.get("file") == relative
                and mapping.get("sha256") == digest
                and mapping.get("matches_static_elf") is True
                and type(mapping.get("mapping_count")) is int
                and mapping["mapping_count"] > 0,
                f"the {family}/{role} ELF does not match its actual mapped engine",
            )
            if verify_live_bytes:
                require(
                    _bounded_digest(
                        expected,
                        maximum=MAX_NATIVE_BYTES,
                        label=f"{family}/{role} actual native engine",
                    )
                    == digest,
                    f"the {family}/{role} ELF changed after source-bound V3 auditing",
                )
            require(relative not in native_digests, "native engines shared an ELF")
            native_digests[relative] = digest
    require(
        len(native_digests) == 5,
        "the sealed V3 campaign did not requalify exactly five actual native ELFs",
    )

    family = original.family_for(module)
    require(
        isinstance(edge, Mapping)
        and edge.get("module") == module
        and edge.get("family") == original.contract.SPECS[module].family
        and edge.get("checks") == original.contract.EDGE_CHECKS
        and edge.get("category_count") == original.contract.EDGE_CATEGORIES
        and edge.get("failed") == 0,
        "the sealed V3 audit received a stale or foreign candidate edge proof",
    )
    artifacts = edge.get("production_artifacts")
    expected_artifacts = _expected_edge_paths(family)
    require(
        isinstance(artifacts, list) and len(artifacts) == len(expected_artifacts),
        "the V3 edge proof omitted or fabricated an owned production artifact",
    )
    observed_roles: set[str] = set()
    for artifact in artifacts:
        require(isinstance(artifact, dict), "an edge artifact is not an object")
        role = artifact.get("role")
        require(
            isinstance(role, str)
            and role in expected_artifacts
            and role not in observed_roles,
            "the V3 edge proof substituted or duplicated a candidate artifact role",
        )
        expected_path = expected_artifacts[role]
        relative = _valid_relative(artifact.get("path"), expected_path, f"{family}/{role} edge")
        expected_digest = (
            native_digests.get(relative)
            if role.startswith("native-") and role != "native-source"
            else source_digests.get(relative)
        )
        require(
            audit_v3.valid_sha256(expected_digest)
            and artifact.get("sha256") == expected_digest,
            f"the V3 edge proof did not bind the actual {family}/{role} artifact",
        )
        observed_roles.add(role)
    require(
        observed_roles == set(expected_artifacts),
        "the V3 edge proof concealed an independently owned native or source role",
    )
    scope = report.get("scope")
    require(
        isinstance(scope, dict)
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_or_case_fixture_access") is False,
        "the sealed V3 source audit accessed a held-out workload or timing",
    )
    return report


def static_family_audit(module: str, edge: dict[str, Any]) -> dict[str, Any]:
    """Consume the exact existing V3 proof without running another audit."""

    require(
        V3_REPORT_PATH.is_file() and not V3_REPORT_PATH.is_symlink(),
        "the exact mandatory V3 source-audit report is missing, invalid, or a symlink",
    )
    require(
        V3_SOURCE_PATH.is_file() and not V3_SOURCE_PATH.is_symlink(),
        "the exact mandatory V3 source-audit verifier is missing, invalid, or a symlink",
    )
    require(
        Path(original.__file__).resolve() == LEGACY_SOURCE_PATH.resolve()
        and _bounded_digest(
            LEGACY_SOURCE_PATH,
            maximum=audit_v3.MAX_SOURCE_BYTES,
            label="immutable historical 22-stage campaign source",
        )
        == LEGACY_SOURCE_SHA256,
        "the immutable historical sealed campaign source was substituted",
    )
    require(
        Path(audit_v3.__file__).resolve() == V3_SOURCE_PATH.resolve(),
        "the sealed V3 source-audit verifier module was substituted",
    )
    source_digest = _bounded_digest(
        V3_SOURCE_PATH,
        maximum=audit_v3.MAX_SOURCE_BYTES,
        label="current V3 source-audit verifier",
    )
    report_digest, payload = audit_v3.bounded_file(
        V3_REPORT_PATH,
        maximum=audit_v3.MAX_REPORT_BYTES,
        label="complete current sealed V3 source-audit report",
        keep=True,
    )
    try:
        report = audit_v3.decode_report(
            payload,
            label="complete source-bound sealed V3 source audit",
        )
    except audit_v3.AuditV3Error as error:
        raise AssertionError("the sealed V3 source-audit report cannot be decoded") from error
    return _validate_current_document(
        report,
        module,
        edge,
        observed_report_sha256=report_digest,
        expected_report_sha256=V3_REPORT_SHA256,
        observed_source_sha256=source_digest,
        expected_source_sha256=V3_SOURCE_SHA256,
        verify_live_bytes=True,
    )


def _synthetic_report(
    wrapper_controls: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    previous = audit_v3.synthetic_previous_report(
        wrapper_controls["previous_v2_self_test"]
    )
    report = audit_v3.synthetic_v3_report(previous)
    for family in ("ast", "vm", "rust", "zig"):
        details = report["families"][family]
        source = scratch.PYTHON_SOURCES[family]
        details["python_source"] = {
            "file": _relative(source),
            "sha256": _synthetic_digest(_relative(source)),
            "passed": True,
            "issues": [],
        }
        details["native_sources"] = [
            {
                "file": _relative(path),
                "sha256": _synthetic_digest(_relative(path)),
                "passed": True,
                "issues": [],
            }
            for path in scratch.NATIVE_SOURCES.get(family, ())
        ]
    digest = hashlib.sha256(original.canonical(report) + b"\n").hexdigest()
    return report, digest


def _synthetic_digest(label: str) -> str:
    return hashlib.sha256(
        ("rebar/sealed-campaign/postfinal-v2/" + label).encode("utf-8")
    ).hexdigest()


def _synthetic_edge(report: Mapping[str, Any], module: str) -> dict[str, Any]:
    family = original.family_for(module)
    details = report["families"][family]
    source_digests = {
        item["file"]: item["sha256"]
        for item in (details["python_source"], *details.get("native_sources", []))
    }
    native_digests = {
        item["file"]: item["sha256"]
        for item in report["native_elf_provenance"]["families"][family]["files"].values()
    }
    artifacts = []
    for role, path in _expected_edge_paths(family).items():
        relative = _relative(path)
        digest = (
            native_digests.get(relative)
            if role.startswith("native-") and role != "native-source"
            else source_digests.get(relative)
        )
        require(audit_v3.valid_sha256(digest), "synthetic edge omitted an owned role")
        artifacts.append({"role": role, "path": relative, "sha256": digest})
    return {
        "module": module,
        "family": original.contract.SPECS[module].family,
        "checks": original.contract.EDGE_CHECKS,
        "category_count": original.contract.EDGE_CATEGORIES,
        "failed": 0,
        "production_artifacts": artifacts,
    }


@contextmanager
def _current_audit_provider() -> Iterator[None]:
    """Scope the V3 provider to one additive run without changing old source."""

    require(
        original.static_family_audit is _ORIGINAL_STATIC_FAMILY_AUDIT,
        "the immutable sealed campaign static-audit provider was already changed",
    )
    original.static_family_audit = static_family_audit
    try:
        yield
    finally:
        original.static_family_audit = _ORIGINAL_STATIC_FAMILY_AUDIT


def self_test() -> dict[str, Any]:
    """Preserve every old campaign check and reject poisoned V3 evidence in memory."""

    controls: list[dict[str, Any]] = []
    with (
        mock.patch.object(
            subprocess,
            "Popen",
            side_effect=AssertionError("the V3 campaign self-test cannot start a worker"),
        ) as process,
        mock.patch.object(
            scratch,
            "run_audit",
            side_effect=AssertionError("the V3 campaign self-test cannot run a source audit"),
        ) as production_audit,
        mock.patch.object(
            audit_v3,
            "bounded_file",
            side_effect=AssertionError("the V3 campaign self-test cannot read production files"),
        ) as production_file,
        mock.patch.object(
            sys.modules[__name__],
            "_ORIGINAL_STATIC_FAMILY_AUDIT",
            side_effect=AssertionError(
                "the additive V3 campaign must never invoke a historical audit"
            ),
        ) as historical_audit,
    ):
        inherited = original.self_test()
        require(
            inherited.get("schema") == original.SELF_TEST_SCHEMA
            and inherited.get("status") == "PASS"
            and inherited.get("failed") == 0
            and inherited.get("synthetic_only") is True
            and inherited.get("candidate_processes_started") == 0
            and inherited.get("candidate_reports_written") == 0
            and inherited.get("performance_processes_started") == 0
            and inherited.get("performance_fixtures_opened") == 0
            and inherited.get("performance_modules_imported") == 0
            and inherited.get("holdout_accessed") is False
            and inherited.get("timing_performed") is False
            and all(count == 22 for count in inherited["actual_planned_step_counts"].values()),
            "the immutable 22-stage sealed campaign synthetic controls failed",
        )
        wrapper_controls = audit_v3.self_test()
        require(
            wrapper_controls.get("schema") == audit_v3.SCHEMA + "-self-test"
            and wrapper_controls.get("passed") is True
            and wrapper_controls.get("failed") == []
            and wrapper_controls.get("candidate_imported") is False
            and wrapper_controls.get("file_reads") == 0
            and wrapper_controls.get("file_writes") == 0
            and wrapper_controls.get("subprocesses") == 0
            and wrapper_controls.get("clock_samples") == 0
            and wrapper_controls.get("holdout_or_case_fixture_access") is False
            and wrapper_controls.get("benchmark_or_timing_executed") is False,
            "the immutable source-bound V3 synthetic audit controls failed",
        )
        report, report_digest = _synthetic_report(wrapper_controls)
        source_digest = report["audit_source_sha256"]

        def validate(
            document: Mapping[str, Any],
            module: str,
            edge: Mapping[str, Any],
            *,
            observed_report: str = report_digest,
            expected_report: str = report_digest,
            observed_source: str = source_digest,
            expected_source: str = source_digest,
        ) -> dict[str, Any]:
            return _validate_current_document(
                document,
                module,
                edge,
                observed_report_sha256=observed_report,
                expected_report_sha256=expected_report,
                observed_source_sha256=observed_source,
                expected_source_sha256=expected_source,
                verify_live_bytes=False,
            )

        for module in original.MODULES:
            edge = _synthetic_edge(report, module)
            require(
                validate(report, module, edge) == report,
                "the sealed V3 synthetic family did not preserve its complete audit",
            )
            controls.append(
                {"id": "accept-complete-v3-audit/" + original.family_for(module), "passed": True}
            )

        module = "candidates.rust_candidate"
        edge = _synthetic_edge(report, module)

        def rejected(name: str, action: Any) -> None:
            try:
                action()
            except (
                AssertionError,
                audit_v3.AuditV3Error,
                KeyError,
                TypeError,
                ValueError,
                OSError,
            ):
                controls.append({"id": name, "passed": True})
                return
            raise AssertionError(f"sealed V3 audit poison was accepted: {name}")

        def missing_report() -> None:
            with (
                mock.patch.object(
                    Path,
                    "is_file",
                    autospec=True,
                    side_effect=lambda path: path != V3_REPORT_PATH,
                ),
                mock.patch.object(
                    Path,
                    "is_symlink",
                    autospec=True,
                    return_value=False,
                ),
            ):
                static_family_audit(module, edge)

        def missing_source() -> None:
            with (
                mock.patch.object(
                    Path,
                    "is_file",
                    autospec=True,
                    side_effect=lambda path: path == V3_REPORT_PATH,
                ),
                mock.patch.object(
                    Path,
                    "is_symlink",
                    autospec=True,
                    return_value=False,
                ),
            ):
                static_family_audit(module, edge)

        def symlinked_input(target: Path) -> None:
            with (
                mock.patch.object(
                    Path,
                    "is_file",
                    autospec=True,
                    return_value=True,
                ),
                mock.patch.object(
                    Path,
                    "is_symlink",
                    autospec=True,
                    side_effect=lambda path: path == target,
                ),
            ):
                static_family_audit(module, edge)

        for name, action in (
            ("reject-missing-mandatory-v3-report-without-legacy-audit", missing_report),
            ("reject-missing-mandatory-v3-source-without-legacy-audit", missing_source),
            (
                "reject-symlinked-mandatory-v3-report-without-legacy-audit",
                lambda: symlinked_input(V3_REPORT_PATH),
            ),
            (
                "reject-symlinked-mandatory-v3-source-without-legacy-audit",
                lambda: symlinked_input(V3_SOURCE_PATH),
            ),
        ):
            before = (
                historical_audit.call_count,
                production_audit.call_count,
                production_file.call_count,
            )
            rejected(name, action)
            require(
                (
                    historical_audit.call_count,
                    production_audit.call_count,
                    production_file.call_count,
                )
                == before,
                "a missing or substituted V3 input invoked a production audit or file",
            )

        for name, mutate in (
            ("reject-historical-v2-audit", lambda item: item.update(postfinal_schema=audit_v3.PREVIOUS_SCHEMA)),
            ("reject-failed-v3-audit", lambda item: item.update(passed=False)),
            ("reject-failed-v3-status", lambda item: item.update(status="FAIL")),
            ("reject-foreign-v3-audit-source", lambda item: item.update(audit_source_path="tools/foreign_audit.py")),
            ("reject-tampered-v3-audit-source-hash", lambda item: item.update(audit_source_sha256="0" * 64)),
            ("reject-stale-v2-ancestry", lambda item: item.update(previous_v2_audit_report_sha256="0" * 64)),
            ("reject-stale-v1-ancestry", lambda item: item.update(original_v1_audit_report_sha256="0" * 64)),
            ("reject-weakened-original-76-controls", lambda item: item["self_test"].update(check_count=75)),
            ("reject-missing-rust-family", lambda item: item["families"].pop("rust")),
            ("reject-failed-rust-owned-pipeline", lambda item: item["families"]["rust"]["owned_pipeline"].update(passed=False)),
            ("reject-missing-rust-parser", lambda item: item["families"]["rust"]["owned_pipeline"].update(parser="")),
            ("reject-failed-rust-isolated-runtime", lambda item: item["families"]["rust"]["isolated_runtime"].update(passed=False)),
            ("reject-unverified-rust-source", lambda item: item["families"]["rust"]["python_source"].update(passed=False)),
            ("reject-poisoned-rust-source-hash", lambda item: item["families"]["rust"]["python_source"].update(sha256="0" * 64)),
            ("reject-escaped-rust-source-path", lambda item: item["families"]["rust"]["python_source"].update(file="../candidates/rust_candidate.py")),
            ("reject-missing-rust-native-source", lambda item: item["families"]["rust"]["native_sources"].pop()),
            ("reject-weakened-five-native-roles", lambda item: item["native_elf_provenance"].update(audited_binary_count=4)),
            ("reject-hidden-rust-engine-role", lambda item: item["native_elf_provenance"]["families"]["rust"]["files"].pop("engine")),
            ("reject-poisoned-rust-native-engine", lambda item: item["native_elf_provenance"]["families"]["rust"]["files"]["engine"].update(sha256="0" * 64)),
            ("reject-external-native-regex-symbol", lambda item: item["native_elf_provenance"]["families"]["rust"]["files"]["engine"].update(forbidden_regex_symbols=["pcre2_match"])),
            ("reject-cross-family-native-symbol", lambda item: item["native_elf_provenance"]["families"]["rust"]["files"]["engine"].update(cross_candidate_symbols=["rebar_zig_match"])),
            ("reject-unmapped-rust-engine", lambda item: item["families"]["rust"]["isolated_runtime"]["native_mapping_provenance"].update(observed_owned_mapping_count=1)),
            ("reject-production-timing", lambda item: item["scope"].update(benchmark_or_timing_executed=True)),
            ("reject-hidden-holdout-access", lambda item: item["scope"].update(holdout_or_case_fixture_access=True)),
        ):
            def poisoned_report(mutation: Any = mutate) -> None:
                changed = copy.deepcopy(report)
                mutation(changed)
                validate(changed, module, edge)

            rejected(name, poisoned_report)

        for name, mutate in (
            ("reject-foreign-edge-candidate", lambda item: item.update(module="candidates.zig_candidate")),
            ("reject-foreign-edge-family", lambda item: item.update(family="ZIG")),
            ("reject-incomplete-edge-checks", lambda item: item.update(checks=1)),
            ("reject-hidden-edge-failure", lambda item: item.update(failed=1)),
            ("reject-missing-edge-native-engine", lambda item: item.update(production_artifacts=[row for row in item["production_artifacts"] if row["role"] != "native-engine"])),
            ("reject-duplicate-edge-native-role", lambda item: item["production_artifacts"].append(copy.deepcopy(item["production_artifacts"][0]))),
            ("reject-poisoned-edge-engine-hash", lambda item: next(row for row in item["production_artifacts"] if row["role"] == "native-engine").update(sha256="0" * 64)),
            ("reject-escaped-edge-engine-path", lambda item: next(row for row in item["production_artifacts"] if row["role"] == "native-engine").update(path="../candidates/_rust_engine.so")),
        ):
            def poisoned_edge(mutation: Any = mutate) -> None:
                changed = copy.deepcopy(edge)
                mutation(changed)
                validate(report, module, changed)

            rejected(name, poisoned_edge)

        rejected(
            "reject-stale-v3-report-fingerprint",
            lambda: validate(report, module, edge, observed_report="0" * 64),
        )
        rejected(
            "reject-substituted-v3-report-fingerprint",
            lambda: validate(report, module, edge, expected_report="0" * 64),
        )
        rejected(
            "reject-stale-v3-source-fingerprint",
            lambda: validate(report, module, edge, observed_source="0" * 64),
        )
        rejected(
            "reject-substituted-v3-source-fingerprint",
            lambda: validate(report, module, edge, expected_source="0" * 64),
        )
        require(
            process.call_count == 0
            and production_audit.call_count == 0
            and production_file.call_count == 0,
            "the additive sealed self-test accessed a candidate, audit, or real file",
        )
        require(
            historical_audit.call_count == 0,
            "the additive sealed V3 self-test invoked its historical audit provider",
        )

    names = [item["id"] for item in controls]
    require(
        len(controls) >= 35
        and len(set(names)) == len(names)
        and all(item.get("passed") is True for item in controls)
        and original.static_family_audit is _ORIGINAL_STATIC_FAMILY_AUDIT,
        "the additive sealed V3 campaign weakened or duplicated a poison control",
    )
    return {
        "schema": SELF_TEST_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "python": "3.14.6",
        "synthetic_only": True,
        "inherited_campaign_schema": original.SELF_TEST_SCHEMA,
        "inherited_campaign_control_count": inherited["poison_control_count"],
        "inherited_v3_audit_control_count": wrapper_controls["check_count"],
        "candidate_modules": list(original.MODULES),
        "actual_planned_step_counts": inherited["actual_planned_step_counts"],
        "poison_control_count": len(controls),
        "poison_controls": controls,
        "candidate_processes_started": 0,
        "candidate_reports_written": 0,
        "production_audits_run": 0,
        "historical_audits_run": 0,
        "historical_audit_fallback_available": False,
        "missing_v3_report_fails_closed": True,
        "missing_v3_source_fails_closed": True,
        "production_report_reads": 0,
        "performance_processes_started": 0,
        "performance_fixtures_opened": 0,
        "holdout_accessed": False,
        "performance": "NOT MEASURED",
        "timing_performed": False,
        "historical_campaign_source_modified": False,
        "failed": 0,
    }


def main(argv: list[str] | None = None) -> int:
    args = original.parse_arguments(argv)
    if args.self_test:
        require(
            args.module is None
            and args.edge_oracle is None
            and args.deep_proof is None
            and args.output is None,
            "the additive campaign self-test cannot run a candidate or write evidence",
        )
        print(json.dumps(self_test(), ensure_ascii=True, sort_keys=True), flush=True)
        return 0
    with _current_audit_provider():
        return original.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
