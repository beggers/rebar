#!/usr/bin/env python3
"""Exclusively requalify current owned regex engines against immutable V2/V1."""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import postfinal_from_scratch_audit_v2 as previous


original = previous.original
SCHEMA = "rebar-postfinal-from-scratch-audit-v3"
PREVIOUS_SCHEMA = "rebar-postfinal-from-scratch-audit-v2"
AUDIT_NAME = "bounded-from-scratch-engine-provenance"
SOURCE_RELATIVE = "tools/postfinal_from_scratch_audit_v3.py"
REPORT_RELATIVE = "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V3.json"
SOURCE_PATH = ROOT / SOURCE_RELATIVE
REPORT_PATH = ROOT / REPORT_RELATIVE
PREVIOUS_SOURCE_RELATIVE = "tools/postfinal_from_scratch_audit_v2.py"
PREVIOUS_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V2.json"
)
PREVIOUS_SOURCE_PATH = ROOT / PREVIOUS_SOURCE_RELATIVE
PREVIOUS_REPORT_PATH = ROOT / PREVIOUS_REPORT_RELATIVE
PREVIOUS_SOURCE_SHA256 = (
    "6f540074c9f7f4bdffe9e53939efe4cec25e5c029ca1f73ec791d377bddc9306"
)
PREVIOUS_REPORT_SHA256 = (
    "5e299a767cbd494683100519a6ad461d1a0eb9de1564b1437c7e0229cca7a551"
)
ORIGINAL_SOURCE_RELATIVE = previous.ORIGINAL_SOURCE_RELATIVE
ORIGINAL_REPORT_RELATIVE = previous.ORIGINAL_REPORT_RELATIVE
ORIGINAL_SOURCE_SHA256 = previous.ORIGINAL_SOURCE_SHA256
ORIGINAL_REPORT_SHA256 = previous.ORIGINAL_REPORT_SHA256
PINNED_INTERPRETER = previous.PINNED_INTERPRETER
PINNED_VERSION = previous.PINNED_VERSION
ORIGINAL_CONTROL_COUNT = 76
MINIMUM_PREVIOUS_WRAPPER_CONTROLS = 52
HASH_CHUNK_BYTES = 64 * 1024
MAX_SOURCE_BYTES = 16 * 1024 * 1024
MAX_REPORT_BYTES = 16 * 1024 * 1024
FAMILIES = ("ast", "vm", "rust", "zig")
NATIVE_FAMILIES = ("vm", "rust", "zig")
EXPECTED_NATIVE_PATHS: dict[str, dict[str, str]] = {
    "ast": {},
    "vm": {
        "native": "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
    },
    "rust": {
        "bridge": "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "engine": "candidates/_rust_engine.so",
    },
    "zig": {
        "bridge": "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
        "engine": "candidates/_zig_probe.so",
    },
}
EXPECTED_LOADED_MODULES: dict[str, frozenset[str]] = {
    "ast": frozenset({"candidates.ast_candidate"}),
    "vm": frozenset({"candidates.vm_candidate", "candidates._vm_native"}),
    "rust": frozenset({"candidates.rust_candidate", "candidates._rust_bridge"}),
    "zig": frozenset({"candidates.zig_candidate", "candidates._zig_bridge"}),
}
EXPECTED_PROBES = frozenset(
    {
        "cpython_sre",
        "foreign_native_loader",
        "other_candidate",
        "stdlib_re",
        "third_party_regex",
    }
)


class AuditV3Error(RuntimeError):
    """A current-source obligation or exclusive additive V3 slot failed."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise AuditV3Error(message)


def valid_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def canonical(document: Any) -> bytes:
    return json.dumps(
        document,
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
    require(not loaded, f"the V3 audit controller imported a candidate: {loaded!r}")


def destination_name(value: Any) -> str:
    require(type(value) is str, "the exclusive V3 destination is not text")
    path = PurePosixPath(value)
    require(
        not path.is_absolute()
        and ".." not in path.parts
        and "\\" not in value
        and "\x00" not in value
        and str(path) == value
        and value == REPORT_RELATIVE,
        "only the distinct, canonical, append-only V3 report is authorized",
    )
    return value


def unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, value in pairs:
        require(name not in result, "a source-bound audit JSON key was duplicated")
        result[name] = value
    return result


def reject_json_constant(value: str) -> None:
    raise AuditV3Error(f"a source-bound audit JSON number is nonfinite: {value}")


def transition(state: str, action: str) -> str:
    transitions = {
        ("absent", "exclusive-create"): "armed",
        ("armed", "write-payload"): "payload-written",
        ("payload-written", "fsync-file"): "file-durable",
        ("file-durable", "open-exact-parent"): "parent-open",
        ("parent-open", "fsync-parent"): "durable",
    }
    if action == "failure" and state in {
        "armed",
        "payload-written",
        "file-durable",
        "parent-open",
    }:
        return "poisoned"
    result = transitions.get((state, action))
    require(
        result is not None,
        "the exclusive V3 report cannot be reused or skip a durability event",
    )
    return result


def validate_runtime_values(value: Any) -> dict[str, Any]:
    require(isinstance(value, Mapping), "the pinned V3 interpreter snapshot is invalid")
    version = value.get("version")
    require(
        value.get("implementation") == "cpython"
        and isinstance(version, (tuple, list))
        and len(version) == 3
        and all(type(part) is int for part in version)
        and tuple(version) == PINNED_VERSION
        and value.get("executable") == PINNED_INTERPRETER
        and type(value.get("isolated")) is int
        and value.get("isolated") == 1
        and value.get("dont_write_bytecode") is True,
        "V3 auditing requires the exact pinned CPython 3.14.6 with -I -B",
    )
    return dict(value)


def verify_production_runtime() -> dict[str, Any]:
    runtime = validate_runtime_values(
        {
            "implementation": sys.implementation.name,
            "version": tuple(sys.version_info[:3]),
            "executable": sys.executable,
            "isolated": sys.flags.isolated,
            "dont_write_bytecode": sys.dont_write_bytecode,
        }
    )
    try:
        actual = Path(sys.executable).resolve(strict=True)
        expected = Path(PINNED_INTERPRETER).resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise AuditV3Error("the pinned V3 interpreter cannot be verified") from error
    require(actual == expected, "the exact pinned V3 interpreter was substituted")
    return runtime


def validate_original_controls(document: Any) -> dict[str, Any]:
    try:
        result = previous.validate_original_controls(document)
    except previous.AuditV2Error as error:
        raise AuditV3Error("the exact original 76 malicious controls changed") from error
    require(
        result.get("check_count") == ORIGINAL_CONTROL_COUNT,
        "the V3 audit weakened the original 76-control denominator",
    )
    return result


def validate_wrapper_controls(
    document: Any, *, schema: str, minimum: int
) -> dict[str, Any]:
    require(isinstance(document, dict), "an inherited wrapper control report is missing")
    controls = document.get("checks")
    count = document.get("check_count")
    require(
        document.get("schema") == schema + "-self-test"
        and document.get("status") == "PASS"
        and document.get("result") == "PASS"
        and document.get("passed") is True
        and type(count) is int
        and count >= minimum
        and isinstance(controls, list)
        and len(controls) == count
        and all(
            isinstance(item, dict)
            and isinstance(item.get("name"), str)
            and item.get("passed") is True
            for item in controls
        )
        and len({item["name"] for item in controls}) == count
        and document.get("failed") == []
        and document.get("fixture_storage") == "in-memory only"
        and document.get("candidate_imported") is False
        and document.get("file_reads") == 0
        and document.get("file_writes") == 0
        and document.get("subprocesses") == 0
        and document.get("clock_samples") == 0
        and document.get("production_entropy_drawn") is False
        and document.get("historical_holdout_accessed") is False
        and document.get("holdout_or_case_fixture_access") is False
        and document.get("benchmark_or_timing_executed") is False
        and document.get("production_cases_materialized") == 0
        and document.get("report_written") is False,
        "a predecessor or V3 candidate-free wrapper control was weakened",
    )
    validate_original_controls(document.get("inherited_self_test"))
    return document


def validate_native_provenance(document: Mapping[str, Any]) -> None:
    native = document.get("native_elf_provenance")
    require(
        isinstance(native, dict)
        and native.get("passed") is True
        and native.get("audited_binary_count") == 5
        and native.get("expected_binary_count") == 5
        and native.get("issues") == [],
        "the V3 audit omitted one of its five independently parsed native ELFs",
    )
    static_families = native.get("families")
    require(
        isinstance(static_families, dict)
        and set(static_families) == set(NATIVE_FAMILIES),
        "the V3 audit omitted a C, Rust, or Zig native ELF family",
    )
    families = document.get("families")
    require(
        isinstance(families, dict) and set(families) == set(FAMILIES),
        "the V3 audit omitted an independently owned production family",
    )
    global_mapping = document.get("runtime_native_mapping_provenance")
    require(
        isinstance(global_mapping, dict)
        and global_mapping.get("passed") is True
        and global_mapping.get("source") == "/proc/self/maps in each isolated candidate worker"
        and isinstance(global_mapping.get("families"), dict)
        and set(global_mapping["families"]) == set(FAMILIES),
        "the V3 audit omitted actual isolated /proc native mappings",
    )
    total = 0
    for family in FAMILIES:
        item = families[family]
        require(
            isinstance(item, dict) and item.get("passed") is True,
            f"the independently owned {family} production family did not pass",
        )
        pipeline = item.get("owned_pipeline")
        require(
            isinstance(pipeline, dict)
            and pipeline.get("passed") is True
            and pipeline.get("issues") == []
            and all(
                isinstance(pipeline.get(role), str) and bool(pipeline[role])
                for role in ("parser", "compiler", "executor")
            ),
            f"the {family} family omitted its independently owned pipeline",
        )
        runtime = item.get("isolated_runtime")
        require(
            isinstance(runtime, dict)
            and runtime.get("passed") is True
            and runtime.get("module") == f"candidates.{family}_candidate"
            and runtime.get("forbidden_loaded_modules") == []
            and runtime.get("forbidden_candidate_import_attempts") == []
            and runtime.get("unexpected_candidate_modules") == []
            and isinstance(runtime.get("loaded_candidate_modules"), list)
            and frozenset(runtime["loaded_candidate_modules"])
            == EXPECTED_LOADED_MODULES[family],
            f"the {family} subprocess delegated or imported a foreign engine",
        )
        probes = runtime.get("prohibited_import_and_loader_probes")
        require(
            isinstance(probes, dict)
            and set(probes) == EXPECTED_PROBES
            and all(value is True for value in probes.values()),
            f"the {family} subprocess lost a CPython, external, or cross-engine guard",
        )
        mapping = runtime.get("native_mapping_provenance")
        expected_roles = EXPECTED_NATIVE_PATHS[family]
        count = len(expected_roles)
        require(
            isinstance(mapping, dict)
            and mapping.get("passed") is True
            and mapping.get("source") == "/proc/self/maps"
            and mapping.get("issues") == []
            and mapping.get("expected_owned_mapping_count") == count
            and mapping.get("observed_owned_mapping_count") == count
            and isinstance(mapping.get("observed_owned_mappings"), list)
            and len(mapping["observed_owned_mappings"]) == count,
            f"the {family} subprocess omitted an actual owned native mapping",
        )
        observed: dict[str, dict[str, Any]] = {}
        for record in mapping["observed_owned_mappings"]:
            require(isinstance(record, dict), "an observed native mapping is invalid")
            role = record.get("role")
            require(
                isinstance(role, str) and role in expected_roles and role not in observed,
                f"the {family} subprocess substituted a native mapping role",
            )
            require(
                record.get("file") == expected_roles[role]
                and valid_sha256(record.get("sha256"))
                and record.get("matches_static_elf") is True
                and type(record.get("mapping_count")) is int
                and record["mapping_count"] > 0,
                f"the {family} subprocess did not map its exact owned ELF",
            )
            observed[role] = record
        require(set(observed) == set(expected_roles), "an isolated native role was hidden")
        family_summary = global_mapping["families"][family]
        require(
            isinstance(family_summary, dict)
            and family_summary.get("passed") is True
            and family_summary.get("expected_owned_mapping_count") == count
            and family_summary.get("observed_owned_mapping_count") == count,
            f"the {family} aggregate native mapping is incomplete",
        )
        if family in NATIVE_FAMILIES:
            static = static_families[family]
            require(
                isinstance(static, dict)
                and static.get("passed") is True
                and static.get("issues") == []
                and isinstance(static.get("files"), dict)
                and set(static["files"]) == set(expected_roles),
                f"the {family} static ELF role graph was weakened",
            )
            for role, path in expected_roles.items():
                record = static["files"][role]
                require(
                    isinstance(record, dict)
                    and record.get("file") == path
                    and record.get("sha256") == observed[role]["sha256"]
                    and record.get("forbidden_regex_symbols") == []
                    and record.get("cross_candidate_symbols") == [],
                    f"the {family} mapped ELF delegated or changed after static audit",
                )
        total += count
    require(total == 5, "the three native production families did not expose five ELFs")


def validate_current_report(document: Any, *, label: str) -> dict[str, Any]:
    try:
        result = previous.validate_report(document, label=label)
    except previous.AuditV2Error as error:
        raise AuditV3Error(f"{label} failed inherited V1/V2 controls") from error
    require(
        result.get("schema_version") == 1
        and result.get("audit") == AUDIT_NAME
        and result.get("result") == "PASS"
        and result.get("passed") is True
        and result.get("verified_core_family_count") == 3
        and result.get("verified_distinct_pipeline_count") == 4
        and result.get("minimum_required_independent_families") == 3
        and isinstance(result.get("all_public_source_families"), list)
        and set(result["all_public_source_families"]) == set(FAMILIES),
        f"{label} weakened the immutable four-family source-audit contract",
    )
    manifest = result.get("manifest_provenance")
    require(
        isinstance(manifest, dict)
        and manifest.get("passed") is True
        and manifest.get("issues") == []
        and manifest.get("python_dependencies") == []
        and manifest.get("rust_third_party_dependency_count") == 0,
        f"{label} introduced an external Python or Rust regex dependency",
    )
    scope = result.get("scope")
    require(
        isinstance(scope, dict)
        and scope.get("explicit_source_paths_only") is True
        and scope.get("mapped_binaries_hashed_against_static_elf") is True
        and scope.get("candidate_imports")
        == "isolated subprocess only, with prohibited import and native-loader probes"
        and scope.get("runtime_native_mapping_source")
        == "/proc/self/maps inside isolated candidate workers only"
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_or_case_fixture_access") is False,
        f"{label} accessed hidden cases, timed work, or weakened engine isolation",
    )
    validate_native_provenance(result)
    return result


def validate_previous_v2_report(document: Any, *, label: str) -> dict[str, Any]:
    result = validate_current_report(document, label=label)
    require(
        result.get("postfinal_schema") == PREVIOUS_SCHEMA
        and result.get("status") == "PASS"
        and result.get("audit_source_path") == PREVIOUS_SOURCE_RELATIVE
        and result.get("audit_source_sha256") == PREVIOUS_SOURCE_SHA256
        and result.get("original_audit_source_path") == ORIGINAL_SOURCE_RELATIVE
        and result.get("original_audit_source_sha256") == ORIGINAL_SOURCE_SHA256
        and result.get("original_v1_audit_report_path") == ORIGINAL_REPORT_RELATIVE
        and result.get("original_v1_audit_report_sha256") == ORIGINAL_REPORT_SHA256,
        f"{label} is not the exact source-bound V2/V1 predecessor",
    )
    validate_runtime_values(result.get("postfinal_interpreter"))
    validate_wrapper_controls(
        result.get("postfinal_wrapper_self_test"),
        schema=PREVIOUS_SCHEMA,
        minimum=MINIMUM_PREVIOUS_WRAPPER_CONTROLS,
    )
    scope = result.get("postfinal_scope")
    require(
        isinstance(scope, dict)
        and scope.get("append_only") is True
        and scope.get("exclusive_report_path") == PREVIOUS_REPORT_RELATIVE
        and scope.get("original_v1_report_preserved") is True
        and scope.get("original_main_invoked") is False
        and scope.get("full_original_audit_rerun") is True
        and scope.get("original_synthetic_controls_rerun") == ORIGINAL_CONTROL_COUNT
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_or_case_fixture_access") is False,
        f"{label} weakened its immutable append-only V2 scope",
    )
    return result


def validate_v3_report(document: Any, *, label: str) -> dict[str, Any]:
    result = validate_current_report(document, label=label)
    require(
        result.get("postfinal_schema") == SCHEMA
        and result.get("status") == "PASS"
        and result.get("audit_source_path") == SOURCE_RELATIVE
        and valid_sha256(result.get("audit_source_sha256"))
        and result.get("original_audit_source_path") == ORIGINAL_SOURCE_RELATIVE
        and result.get("original_audit_source_sha256") == ORIGINAL_SOURCE_SHA256
        and result.get("original_v1_audit_report_path") == ORIGINAL_REPORT_RELATIVE
        and result.get("original_v1_audit_report_sha256") == ORIGINAL_REPORT_SHA256
        and result.get("previous_v2_audit_source_path") == PREVIOUS_SOURCE_RELATIVE
        and result.get("previous_v2_audit_source_sha256") == PREVIOUS_SOURCE_SHA256
        and result.get("previous_v2_audit_report_path") == PREVIOUS_REPORT_RELATIVE
        and result.get("previous_v2_audit_report_sha256") == PREVIOUS_REPORT_SHA256
        and result.get("previous_v2_postfinal_schema") == PREVIOUS_SCHEMA,
        f"{label} changed its actual V3 source or immutable V2/V1 ancestry",
    )
    validate_runtime_values(result.get("postfinal_interpreter"))
    validate_wrapper_controls(
        result.get("postfinal_wrapper_self_test"),
        schema=SCHEMA,
        minimum=MINIMUM_PREVIOUS_WRAPPER_CONTROLS,
    )
    validate_wrapper_controls(
        result.get("previous_v2_wrapper_self_test"),
        schema=PREVIOUS_SCHEMA,
        minimum=MINIMUM_PREVIOUS_WRAPPER_CONTROLS,
    )
    scope = result.get("postfinal_scope")
    require(
        isinstance(scope, dict)
        and scope.get("append_only") is True
        and scope.get("exclusive_report_path") == REPORT_RELATIVE
        and scope.get("original_v1_report_preserved") is True
        and scope.get("previous_v2_report_preserved") is True
        and scope.get("original_main_invoked") is False
        and scope.get("full_original_audit_rerun") is True
        and scope.get("original_synthetic_controls_rerun") == ORIGINAL_CONTROL_COUNT
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_or_case_fixture_access") is False,
        f"{label} weakened its exclusive, no-holdout V3 production scope",
    )
    return result


def _synthetic_sha(label: str) -> str:
    return hashlib.sha256(("v3-source-audit-self-test:" + label).encode()).hexdigest()


def synthetic_previous_report(wrapper: dict[str, Any]) -> dict[str, Any]:
    families: dict[str, Any] = {}
    native_families: dict[str, Any] = {}
    global_families: dict[str, Any] = {}
    for family in FAMILIES:
        expected = EXPECTED_NATIVE_PATHS[family]
        mappings = [
            {
                "role": role,
                "file": path,
                "sha256": _synthetic_sha(family + ":" + role),
                "matches_static_elf": True,
                "mapping_count": 1,
            }
            for role, path in expected.items()
        ]
        mapping = {
            "passed": True,
            "source": "/proc/self/maps",
            "issues": [],
            "expected_owned_mapping_count": len(expected),
            "observed_owned_mapping_count": len(expected),
            "observed_owned_mappings": mappings,
        }
        families[family] = {
            "passed": True,
            "owned_pipeline": {
                "passed": True,
                "issues": [],
                "parser": family + "::parser",
                "compiler": family + "::compiler",
                "executor": family + "::executor",
            },
            "isolated_runtime": {
                "passed": True,
                "module": f"candidates.{family}_candidate",
                "forbidden_candidate_import_attempts": [],
                "forbidden_loaded_modules": [],
                "unexpected_candidate_modules": [],
                "loaded_candidate_modules": sorted(EXPECTED_LOADED_MODULES[family]),
                "prohibited_import_and_loader_probes": {
                    name: True for name in sorted(EXPECTED_PROBES)
                },
                "native_mapping_provenance": mapping,
            },
        }
        global_families[family] = {
            "passed": True,
            "expected_owned_mapping_count": len(expected),
            "observed_owned_mapping_count": len(expected),
        }
        if family in NATIVE_FAMILIES:
            native_families[family] = {
                "passed": True,
                "issues": [],
                "files": {
                    item["role"]: {
                        "file": item["file"],
                        "sha256": item["sha256"],
                        "forbidden_regex_symbols": [],
                        "cross_candidate_symbols": [],
                    }
                    for item in mappings
                },
            }
    return {
        "schema_version": 1,
        "audit": AUDIT_NAME,
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "postfinal_schema": PREVIOUS_SCHEMA,
        "audit_source_path": PREVIOUS_SOURCE_RELATIVE,
        "audit_source_sha256": PREVIOUS_SOURCE_SHA256,
        "original_audit_source_path": ORIGINAL_SOURCE_RELATIVE,
        "original_audit_source_sha256": ORIGINAL_SOURCE_SHA256,
        "original_v1_audit_report_path": ORIGINAL_REPORT_RELATIVE,
        "original_v1_audit_report_sha256": ORIGINAL_REPORT_SHA256,
        "self_test": wrapper["inherited_self_test"],
        "postfinal_wrapper_self_test": wrapper,
        "postfinal_interpreter": {
            "implementation": "cpython",
            "version": PINNED_VERSION,
            "executable": PINNED_INTERPRETER,
            "isolated": 1,
            "dont_write_bytecode": True,
        },
        "families": families,
        "all_public_source_families": list(FAMILIES),
        "core_families": ["ast", "vm", "rust"],
        "minimum_required_independent_families": 3,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
        "native_elf_provenance": {
            "passed": True,
            "issues": [],
            "audited_binary_count": 5,
            "expected_binary_count": 5,
            "families": native_families,
        },
        "runtime_native_mapping_provenance": {
            "passed": True,
            "source": "/proc/self/maps in each isolated candidate worker",
            "families": global_families,
        },
        "manifest_provenance": {
            "passed": True,
            "issues": [],
            "python_dependencies": [],
            "rust_lock_packages": ["rebar-rust-continuation"],
            "rust_third_party_dependency_count": 0,
        },
        "scope": {
            "explicit_source_paths_only": True,
            "mapped_binaries_hashed_against_static_elf": True,
            "candidate_imports": (
                "isolated subprocess only, with prohibited import and native-loader probes"
            ),
            "runtime_native_mapping_source": (
                "/proc/self/maps inside isolated candidate workers only"
            ),
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        },
        "postfinal_scope": {
            "append_only": True,
            "exclusive_report_path": PREVIOUS_REPORT_RELATIVE,
            "original_v1_report_preserved": True,
            "original_main_invoked": False,
            "full_original_audit_rerun": True,
            "original_synthetic_controls_rerun": ORIGINAL_CONTROL_COUNT,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        },
    }


def synthetic_v3_report(previous_report: dict[str, Any]) -> dict[str, Any]:
    inherited_wrapper = previous_report["postfinal_wrapper_self_test"]
    wrapper = copy.deepcopy(inherited_wrapper)
    wrapper.update(
        {
            "schema": SCHEMA + "-self-test",
            "candidate_imports": [],
            "guard_accessed": False,
            "previous_v2_self_test": inherited_wrapper,
        }
    )
    result = copy.deepcopy(previous_report)
    result.update(
        {
            "postfinal_schema": SCHEMA,
            "audit_source_path": SOURCE_RELATIVE,
            "audit_source_sha256": _synthetic_sha("v3-source"),
            "previous_v2_audit_source_path": PREVIOUS_SOURCE_RELATIVE,
            "previous_v2_audit_source_sha256": PREVIOUS_SOURCE_SHA256,
            "previous_v2_audit_report_path": PREVIOUS_REPORT_RELATIVE,
            "previous_v2_audit_report_sha256": PREVIOUS_REPORT_SHA256,
            "previous_v2_postfinal_schema": PREVIOUS_SCHEMA,
            "previous_v2_wrapper_self_test": inherited_wrapper,
            "postfinal_wrapper_self_test": wrapper,
            "postfinal_scope": {
                "append_only": True,
                "exclusive_report_path": REPORT_RELATIVE,
                "original_v1_report_preserved": True,
                "previous_v2_report_preserved": True,
                "original_main_invoked": False,
                "full_original_audit_rerun": True,
                "original_synthetic_controls_rerun": ORIGINAL_CONTROL_COUNT,
                "benchmark_or_timing_executed": False,
                "holdout_or_case_fixture_access": False,
            },
        }
    )
    return result


def _changed(document: dict[str, Any], path: tuple[str, ...], value: Any) -> dict[str, Any]:
    result = copy.deepcopy(document)
    target: Any = result
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = value
    return result


def self_test() -> dict[str, Any]:
    ensure_candidate_free()
    effects = previous.BlockSelfTestEffects()
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: Any) -> None:
        checks.append({"name": name, "passed": bool(condition)})

    def rejected(name: str, action: Any) -> None:
        try:
            action()
        except (
            AuditV3Error,
            previous.AuditV2Error,
            TypeError,
            ValueError,
            UnicodeError,
            OverflowError,
            RecursionError,
        ):
            check(name, True)
        else:
            check(name, False)

    with effects:
        predecessor_controls = previous.self_test()
        validate_wrapper_controls(
            predecessor_controls,
            schema=PREVIOUS_SCHEMA,
            minimum=MINIMUM_PREVIOUS_WRAPPER_CONTROLS,
        )
        inherited_controls = validate_original_controls(
            predecessor_controls["inherited_self_test"]
        )
        check("preserve-exact-original-76-in-memory-controls", True)
        check("preserve-all-original-distinct-malicious-control-names", True)
        check("rerun-all-source-bound-v2-wrapper-controls-in-memory", True)
        check("preserve-at-least-52-v2-wrapper-controls", True)
        check("preserve-version-one-universal-audit-schema", True)
        check("authorize-only-exclusive-v3-report", destination_name(REPORT_RELATIVE) == REPORT_RELATIVE)
        check("distinct-source-bound-v3-audit-schema", SCHEMA == "rebar-postfinal-from-scratch-audit-v3")
        for name, target in (
            ("reject-immutable-original-v1-report-slot", ORIGINAL_REPORT_RELATIVE),
            ("reject-immutable-previous-v2-report-slot", PREVIOUS_REPORT_RELATIVE),
            ("reject-absolute-report-slot", "/" + REPORT_RELATIVE),
            ("reject-parent-traversal-report-slot", "candidates/audits/../POSTFINAL-FROM-SCRATCH-AUDIT-V3.json"),
            ("reject-noncanonical-report-slot", "candidates//audits/POSTFINAL-FROM-SCRATCH-AUDIT-V3.json"),
            ("reject-unrelated-report-slot", "candidates/audits/FOREIGN.json"),
            ("reject-backslash-report-slot", "candidates\\audits\\POSTFINAL-FROM-SCRATCH-AUDIT-V3.json"),
            ("reject-nul-report-slot", REPORT_RELATIVE + "\x00"),
            ("reject-nontext-report-slot", 3),
        ):
            rejected(name, lambda value=target: destination_name(value))

        state = "absent"
        for name, action, expected in (
            ("exclusive-v3-slot-created-once", "exclusive-create", "armed"),
            ("exclusive-v3-payload-fully-written", "write-payload", "payload-written"),
            ("exclusive-v3-report-fsynced", "fsync-file", "file-durable"),
            ("exclusive-v3-parent-opened", "open-exact-parent", "parent-open"),
            ("exclusive-v3-parent-fsynced", "fsync-parent", "durable"),
        ):
            state = transition(state, action)
            check(name, state == expected)
        for name, old, action in (
            ("reject-overwritten-v3-slot", "durable", "exclusive-create"),
            ("reject-repeated-v3-create", "armed", "exclusive-create"),
            ("reject-file-fsync-before-payload", "armed", "fsync-file"),
            ("reject-directory-fsync-before-file", "payload-written", "fsync-parent"),
            ("reject-early-directory-open", "payload-written", "open-exact-parent"),
            ("reject-reused-poisoned-v3-slot", "poisoned", "exclusive-create"),
            ("reject-repeated-v3-directory-fsync", "durable", "fsync-parent"),
        ):
            rejected(name, lambda before=old, event=action: transition(before, event))
        for old in ("armed", "payload-written", "file-durable", "parent-open"):
            check("preserve-poisoned-v3-slot:" + old, transition(old, "failure") == "poisoned")

        synthetic_v2 = synthetic_previous_report(predecessor_controls)
        validate_previous_v2_report(synthetic_v2, label="synthetic immutable V2")
        synthetic_v3 = synthetic_v3_report(synthetic_v2)
        validate_v3_report(synthetic_v3, label="synthetic current V3")
        check("validate-complete-synthetic-v2-ancestry", True)
        check("validate-complete-synthetic-current-v3-family-graph", True)
        check("preserve-all-four-owned-source-families", True)
        check("preserve-all-three-independent-native-families", True)
        check("preserve-all-five-parsed-and-actually-mapped-native-elves", True)
        check("preserve-all-five-external-regex-and-cross-engine-poison-guards", True)

        for name, path, value in (
            ("reject-foreign-universal-audit-schema", ("schema_version",), 2),
            ("reject-foreign-universal-audit-name", ("audit",), "external-regex-wrapper"),
            ("reject-failing-current-source-audit", ("passed",), False),
            ("reject-missing-owned-native-family", ("families",), {key: val for key, val in synthetic_v3["families"].items() if key != "rust"}),
            ("reject-reduced-native-binary-count", ("native_elf_provenance", "audited_binary_count"), 4),
            ("reject-nonproc-native-mapping", ("runtime_native_mapping_provenance", "source"), "guessed native artifacts"),
            ("reject-third-party-python-regex", ("manifest_provenance", "python_dependencies"), ["regex"]),
            ("reject-third-party-rust-regex", ("manifest_provenance", "rust_third_party_dependency_count"), 1),
            ("reject-manifest-provenance-issue", ("manifest_provenance", "issues"), ["external-engine"]),
            ("reject-nonisolated-candidate-import", ("scope", "candidate_imports"), "shared candidate interpreter"),
            ("reject-hidden-or-final-fixture-access", ("scope", "holdout_or_case_fixture_access"), True),
            ("reject-production-timing", ("scope", "benchmark_or_timing_executed"), True),
            ("reject-unbounded-source-enumeration", ("scope", "explicit_source_paths_only"), False),
            ("reject-unchecked-static-native-elf", ("scope", "mapped_binaries_hashed_against_static_elf"), False),
            ("reject-stale-v2-schema-as-v3", ("postfinal_schema",), PREVIOUS_SCHEMA),
            ("reject-substituted-v3-source-path", ("audit_source_path",), PREVIOUS_SOURCE_RELATIVE),
            ("reject-invalid-v3-source-fingerprint", ("audit_source_sha256",), "0"),
            ("reject-substituted-original-source", ("original_audit_source_sha256",), "0" * 64),
            ("reject-substituted-original-v1-report", ("original_v1_audit_report_sha256",), "0" * 64),
            ("reject-substituted-v2-source-path", ("previous_v2_audit_source_path",), SOURCE_RELATIVE),
            ("reject-substituted-v2-source-fingerprint", ("previous_v2_audit_source_sha256",), "0" * 64),
            ("reject-substituted-v2-report-path", ("previous_v2_audit_report_path",), REPORT_RELATIVE),
            ("reject-substituted-v2-report-fingerprint", ("previous_v2_audit_report_sha256",), "0" * 64),
            ("reject-substituted-v2-ancestry-schema", ("previous_v2_postfinal_schema",), SCHEMA),
            ("reject-overwriting-v2-scope", ("postfinal_scope", "exclusive_report_path"), PREVIOUS_REPORT_RELATIVE),
            ("reject-unpreserved-v1-history", ("postfinal_scope", "original_v1_report_preserved"), False),
            ("reject-unpreserved-v2-history", ("postfinal_scope", "previous_v2_report_preserved"), False),
            ("reject-unrerun-original-audit", ("postfinal_scope", "full_original_audit_rerun"), False),
            ("reject-weakened-original-76-denominator", ("postfinal_scope", "original_synthetic_controls_rerun"), 75),
            ("reject-scope-holdout-access", ("postfinal_scope", "holdout_or_case_fixture_access"), True),
            ("reject-scope-production-timing", ("postfinal_scope", "benchmark_or_timing_executed"), True),
        ):
            rejected(
                name,
                lambda item_path=path, replacement=value: validate_v3_report(
                    _changed(synthetic_v3, item_path, replacement),
                    label="synthetic poisoned V3 source audit",
                ),
            )

        for family in FAMILIES:
            for name, path, value in (
                ("reject-delegating-owned-pipeline", ("families", family, "owned_pipeline", "passed"), False),
                ("reject-cross-family-runtime-module", ("families", family, "isolated_runtime", "module"), "candidates.foreign_candidate"),
                ("reject-cross-candidate-loaded-module", ("families", family, "isolated_runtime", "unexpected_candidate_modules"), ["candidates.foreign_candidate"]),
                ("reject-stdlib-regex-runtime-guard", ("families", family, "isolated_runtime", "prohibited_import_and_loader_probes", "stdlib_re"), False),
                ("reject-third-party-regex-runtime-guard", ("families", family, "isolated_runtime", "prohibited_import_and_loader_probes", "third_party_regex"), False),
                ("reject-hidden-proc-native-mapping", ("families", family, "isolated_runtime", "native_mapping_provenance", "source"), "foreign process"),
            ):
                rejected(
                    name + ":" + family,
                    lambda item_path=path, replacement=value: validate_v3_report(
                        _changed(synthetic_v3, item_path, replacement),
                        label="synthetic poisoned native family",
                    ),
                )
        for family in NATIVE_FAMILIES:
            role = next(iter(EXPECTED_NATIVE_PATHS[family]))
            for name, path, value in (
                ("reject-foreign-static-native-symbols", ("native_elf_provenance", "families", family, "files", role, "forbidden_regex_symbols"), ["pcre2_match"]),
                ("reject-cross-candidate-native-symbols", ("native_elf_provenance", "families", family, "files", role, "cross_candidate_symbols"), ["rebar_zig_match"]),
                ("reject-substituted-static-native-elf", ("native_elf_provenance", "families", family, "files", role, "sha256"), "0" * 64),
                ("reject-unmapped-owned-native-role", ("families", family, "isolated_runtime", "native_mapping_provenance", "observed_owned_mapping_count"), 0),
            ):
                rejected(
                    name + ":" + family,
                    lambda item_path=path, replacement=value: validate_v3_report(
                        _changed(synthetic_v3, item_path, replacement),
                        label="synthetic poisoned owned ELF",
                    ),
                )

        runtime = {
            "implementation": "cpython",
            "version": PINNED_VERSION,
            "executable": PINNED_INTERPRETER,
            "isolated": 1,
            "dont_write_bytecode": True,
        }
        check("accept-exact-isolated-pinned-cpython-3146", validate_runtime_values(runtime) == runtime)
        for name, key, value in (
            ("reject-foreign-interpreter-implementation", "implementation", "pypy"),
            ("reject-foreign-interpreter-version", "version", (3, 14, 5)),
            ("reject-boolean-interpreter-version", "version", (True, 14, 6)),
            ("reject-unpinned-interpreter-path", "executable", "/usr/bin/python3"),
            ("reject-disabled-interpreter-isolation", "isolated", 0),
            ("reject-boolean-interpreter-isolation", "isolated", True),
            ("reject-enabled-production-bytecode", "dont_write_bytecode", False),
        ):
            rejected(name, lambda field=key, replacement=value: validate_runtime_values({**runtime, field: replacement}))
        fixture = {"high": "\ud800", "low": "\udfff", "emoji": "\U0001f9ea"}
        wire = canonical(fixture)
        check("lossless-deterministic-ascii-surrogate-wire", wire.isascii() and json.loads(wire) == fixture)
        check("canonical-ordered-provenance", canonical({"b": 2, "a": 1}) == b'{"a":1,"b":2}')
        for name, value in (
            ("reject-nan-provenance", float("nan")),
            ("reject-positive-infinite-provenance", float("inf")),
            ("reject-negative-infinite-provenance", -float("inf")),
        ):
            rejected(name, lambda item=value: canonical({"value": item}))
        rejected("reject-duplicate-audit-json-keys", lambda: unique_json_object([("audit", 1), ("audit", 2)]))
        for name, value in (
            ("pin-exact-immutable-v1-source-sha256", ORIGINAL_SOURCE_SHA256),
            ("pin-exact-immutable-v1-report-sha256", ORIGINAL_REPORT_SHA256),
            ("pin-exact-immutable-v2-source-sha256", PREVIOUS_SOURCE_SHA256),
            ("pin-exact-immutable-v2-report-sha256", PREVIOUS_REPORT_SHA256),
        ):
            check(name, valid_sha256(value))
        ensure_candidate_free()
        check("candidate-free-after-all-v1-v2-v3-in-memory-controls", True)

    check("zero-production-evidence-file-reads", effects.counts["files"] == 0)
    check("zero-production-evidence-file-writes", effects.counts["files"] == 0)
    check("zero-candidate-worker-or-subprocess-starts", effects.counts["processes"] == 0)
    check("zero-production-benchmark-clock-samples", effects.counts["clocks"] == 0)
    check("zero-production-entropy-draws", effects.counts["entropy"] == 0)
    names = [item["name"] for item in checks]
    failed = sorted(item["name"] for item in checks if not item["passed"])
    if len(names) != len(set(names)):
        failed.append("duplicate-v3-wrapper-control-name")
    if len(checks) < MINIMUM_PREVIOUS_WRAPPER_CONTROLS:
        failed.append("weakened-v3-wrapper-control-denominator")
    ensure_candidate_free()
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS" if not failed else "FAIL",
        "result": "PASS" if not failed else "FAIL",
        "passed": not failed,
        "checks": checks,
        "check_count": len(checks),
        "failed": failed,
        "inherited_self_test": inherited_controls,
        "inherited_control_count": ORIGINAL_CONTROL_COUNT,
        "previous_v2_self_test": predecessor_controls,
        "previous_v2_control_count": predecessor_controls["check_count"],
        "fixture_storage": "in-memory only",
        "candidate_imported": False,
        "candidate_imports": [],
        "guard_accessed": False,
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


def bounded_file(
    path: Path, *, maximum: int, label: str, keep: bool = False
) -> tuple[str, bytes]:
    require(isinstance(path, Path), f"{label} is not an exact owned path")
    require(not path.is_symlink(), f"{label} cannot be a symbolic link")
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(ROOT.resolve(strict=True))
        flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        flags |= getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(resolved, flags)
        try:
            before = os.fstat(descriptor)
            require(stat.S_ISREG(before.st_mode), f"{label} is not a regular file")
            require(0 < before.st_size <= maximum, f"{label} exceeds its finite bound")
            digest = hashlib.sha256()
            payload = bytearray() if keep else None
            length = 0
            while True:
                block = os.read(descriptor, HASH_CHUNK_BYTES)
                if not block:
                    break
                length += len(block)
                require(length <= maximum, f"{label} exceeds its finite bound")
                digest.update(block)
                if payload is not None:
                    payload.extend(block)
            after = os.fstat(descriptor)
        finally:
            os.close(descriptor)
    except (OSError, RuntimeError, ValueError) as error:
        if isinstance(error, AuditV3Error):
            raise
        raise AuditV3Error(f"cannot independently fingerprint {label}") from error
    before_identity = (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
        before.st_ctime_ns,
    )
    after_identity = (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
        after.st_ctime_ns,
    )
    require(before_identity == after_identity, f"{label} changed while being hashed")
    require(length == before.st_size, f"{label} changed length while being hashed")
    return digest.hexdigest(), bytes(payload or b"")


def decode_report(payload: bytes, *, label: str) -> dict[str, Any]:
    try:
        document = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=unique_json_object,
            parse_constant=reject_json_constant,
        )
    except (TypeError, ValueError, UnicodeError) as error:
        raise AuditV3Error(f"{label} is not strict finite canonical JSON") from error
    require(isinstance(document, dict), f"{label} is not a JSON object")
    return document


def audit() -> dict[str, Any]:
    runtime = verify_production_runtime()
    ensure_candidate_free()
    require(
        Path(previous.__file__).resolve() == PREVIOUS_SOURCE_PATH.resolve()
        and Path(original.__file__).resolve() == previous.ORIGINAL_SOURCE_PATH.resolve(),
        "the immutable V2 or original 76-control audit module was substituted",
    )
    for path, expected, label in (
        (PREVIOUS_SOURCE_PATH, PREVIOUS_SOURCE_SHA256, "immutable V2 audit source"),
        (previous.ORIGINAL_SOURCE_PATH, ORIGINAL_SOURCE_SHA256, "immutable original V1 audit source"),
        (previous.ORIGINAL_REPORT_PATH, ORIGINAL_REPORT_SHA256, "immutable original V1 audit report"),
    ):
        actual, _ = bounded_file(path, maximum=MAX_SOURCE_BYTES, label=label)
        require(actual == expected, f"{label} changed before V3 verification")
    predecessor_digest, predecessor_payload = bounded_file(
        PREVIOUS_REPORT_PATH,
        maximum=MAX_REPORT_BYTES,
        label="immutable complete V2 source-audit report",
        keep=True,
    )
    require(
        predecessor_digest == PREVIOUS_REPORT_SHA256,
        "the immutable complete V2 source-audit report changed",
    )
    predecessor_report = decode_report(
        predecessor_payload,
        label="immutable complete V2 source-audit report",
    )
    validate_previous_v2_report(predecessor_report, label="immutable complete V2 source audit")
    controls = self_test()
    validate_wrapper_controls(controls, schema=SCHEMA, minimum=MINIMUM_PREVIOUS_WRAPPER_CONTROLS)
    ensure_candidate_free()
    current = previous.audit()
    validate_previous_v2_report(current, label="fresh isolated current-source V2 audit")
    ensure_candidate_free()
    for path, expected, label in (
        (PREVIOUS_SOURCE_PATH, PREVIOUS_SOURCE_SHA256, "preserved immutable V2 source"),
        (PREVIOUS_REPORT_PATH, PREVIOUS_REPORT_SHA256, "preserved immutable V2 report"),
        (previous.ORIGINAL_SOURCE_PATH, ORIGINAL_SOURCE_SHA256, "preserved immutable V1 source"),
        (previous.ORIGINAL_REPORT_PATH, ORIGINAL_REPORT_SHA256, "preserved immutable V1 report"),
    ):
        actual, _ = bounded_file(path, maximum=MAX_REPORT_BYTES, label=label)
        require(actual == expected, f"{label} changed during actual V3 verification")
    source_digest, _ = bounded_file(
        SOURCE_PATH,
        maximum=MAX_SOURCE_BYTES,
        label="actual exclusive V3 audit source",
    )
    reserved = {
        "previous_v2_audit_source_path",
        "previous_v2_audit_source_sha256",
        "previous_v2_audit_report_path",
        "previous_v2_audit_report_sha256",
        "previous_v2_postfinal_schema",
        "previous_v2_wrapper_self_test",
    }
    require(not (reserved & set(current)), "the current audit collides with V3 provenance")
    result = dict(current)
    result.update(
        {
            "postfinal_schema": SCHEMA,
            "status": "PASS",
            "audit_source_path": SOURCE_RELATIVE,
            "audit_source_sha256": source_digest,
            "original_audit_source_path": ORIGINAL_SOURCE_RELATIVE,
            "original_audit_source_sha256": ORIGINAL_SOURCE_SHA256,
            "original_v1_audit_report_path": ORIGINAL_REPORT_RELATIVE,
            "original_v1_audit_report_sha256": ORIGINAL_REPORT_SHA256,
            "previous_v2_audit_source_path": PREVIOUS_SOURCE_RELATIVE,
            "previous_v2_audit_source_sha256": PREVIOUS_SOURCE_SHA256,
            "previous_v2_audit_report_path": PREVIOUS_REPORT_RELATIVE,
            "previous_v2_audit_report_sha256": PREVIOUS_REPORT_SHA256,
            "previous_v2_postfinal_schema": PREVIOUS_SCHEMA,
            "previous_v2_wrapper_self_test": current["postfinal_wrapper_self_test"],
            "postfinal_wrapper_self_test": controls,
            "postfinal_interpreter": runtime,
            "postfinal_scope": {
                "append_only": True,
                "exclusive_report_path": REPORT_RELATIVE,
                "original_v1_report_preserved": True,
                "previous_v2_report_preserved": True,
                "original_main_invoked": False,
                "full_original_audit_rerun": True,
                "original_synthetic_controls_rerun": ORIGINAL_CONTROL_COUNT,
                "benchmark_or_timing_executed": False,
                "holdout_or_case_fixture_access": False,
            },
        }
    )
    validate_v3_report(result, label="additive actual current-source V3 audit")
    ensure_candidate_free()
    return result


def write_report(report: Mapping[str, Any], target: Path) -> None:
    require(isinstance(target, Path), "the exclusive V3 report target is invalid")
    require(
        target.name == REPORT_PATH.name
        and not target.is_symlink()
        and target.parent.resolve() == REPORT_PATH.parent.resolve(),
        "only the exact, non-symlink, additive V3 report may be created",
    )
    parent = REPORT_PATH.parent
    require(not parent.is_symlink(), "the exclusive V3 report parent is a symlink")
    try:
        resolved_parent = parent.resolve(strict=True)
        resolved_parent.relative_to(ROOT.resolve(strict=True))
    except (OSError, RuntimeError, ValueError) as error:
        raise AuditV3Error("the exclusive V3 report parent escaped the repository") from error
    payload = canonical(report) + b"\n"
    require(len(payload) <= MAX_REPORT_BYTES, "the V3 audit report exceeds its bound")
    directory_flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    directory_flags |= getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    file_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    file_flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    try:
        parent_descriptor = os.open(resolved_parent, directory_flags)
    except OSError as error:
        raise AuditV3Error("cannot open the exact no-follow V3 audit directory") from error
    try:
        parent_stat = os.fstat(parent_descriptor)
        require(stat.S_ISDIR(parent_stat.st_mode), "the V3 audit parent is not a directory")
        try:
            descriptor = os.open(REPORT_PATH.name, file_flags, 0o644, dir_fd=parent_descriptor)
        except OSError as error:
            raise AuditV3Error("refusing to overwrite or reuse an exclusive V3 report") from error
        try:
            payload_view = memoryview(payload)
            while payload_view:
                written = os.write(descriptor, payload_view)
                require(written > 0, "the exclusive V3 report write made no progress")
                payload_view = payload_view[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        os.fsync(parent_descriptor)
    finally:
        os.close(parent_descriptor)


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
            "select --self-test or --audit [--output POSTFINAL-FROM-SCRATCH-AUDIT-V3.json]",
        )
        target = REPORT_PATH if len(selected) == 1 else Path(selected[2])
        result = audit()
        write_report(result, target)
        summary = {
            "postfinal_schema": SCHEMA,
            "schema_version": 1,
            "audit": AUDIT_NAME,
            "status": "PASS",
            "result": "PASS",
            "passed": True,
            "report": REPORT_RELATIVE,
            "audit_source_path": SOURCE_RELATIVE,
            "audit_source_sha256": result["audit_source_sha256"],
            "previous_v2_audit_source_path": PREVIOUS_SOURCE_RELATIVE,
            "previous_v2_audit_source_sha256": PREVIOUS_SOURCE_SHA256,
            "previous_v2_audit_report_path": PREVIOUS_REPORT_RELATIVE,
            "previous_v2_audit_report_sha256": PREVIOUS_REPORT_SHA256,
            "original_audit_source_sha256": ORIGINAL_SOURCE_SHA256,
            "original_v1_audit_report_sha256": ORIGINAL_REPORT_SHA256,
            "self_test_checks": result["self_test"]["check_count"],
            "previous_v2_wrapper_self_test_checks": (
                result["previous_v2_wrapper_self_test"]["check_count"]
            ),
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
        AuditV3Error,
        previous.AuditV2Error,
        OSError,
        TypeError,
        ValueError,
        UnicodeError,
        subprocess.SubprocessError,
    ) as error:
        sys.stdout.buffer.write(
            canonical(
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
