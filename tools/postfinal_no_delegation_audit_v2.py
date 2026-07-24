#!/usr/bin/env python3
"""Requalify the immutable no-delegation audit against the additive V2 base.

``--self-test`` is deterministic and entirely in memory.  It never imports a
candidate, reads an audit or source, starts a worker, draws entropy, or takes a
timing.  Only an explicit ``--audit`` performs source-bound, independently
guarded production verification and exclusively creates the new V2 report.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
from typing import Any, Mapping


SCHEMA = "rebar-postfinal-no-delegation-audit-v2"
BASE_POSTFINAL_SCHEMA = "rebar-postfinal-from-scratch-audit-v2"
IMMUTABLE_STRICT_SCHEMA = "rebar-postfinal-no-delegation-audit-v1"
ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "tools" / "postfinal_no_delegation_audit_v2.py"
IMMUTABLE_STRICT_SOURCE = ROOT / "tools" / "postfinal_no_delegation_audit_v1.py"
ORIGINAL_BASE_SOURCE = ROOT / "tools" / "audit_from_scratch.py"
BASE_V2_SOURCE = ROOT / "tools" / "postfinal_from_scratch_audit_v2.py"
BASE_V2_REPORT = (
    ROOT / "candidates" / "audits" / "POSTFINAL-FROM-SCRATCH-AUDIT-V2.json"
)
ORIGINAL_BASE_REPORT = ROOT / "candidates" / "audits" / "FROM-SCRATCH-AUDIT.json"
IMMUTABLE_STRICT_REPORT = (
    ROOT / "candidates" / "audits" / "POSTFINAL-NO-DELEGATION-AUDIT-V1.json"
)
REPORT = (
    ROOT / "candidates" / "audits" / "POSTFINAL-NO-DELEGATION-AUDIT-V2.json"
)
PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_VERSION = (3, 14, 6)
IMMUTABLE_STRICT_SOURCE_SHA256 = (
    "e505e17f4849242d990ee8e184794962327335d807000d1a8a0e65a0cb10c0ed"
)
IMMUTABLE_STRICT_REPORT_SHA256 = (
    "c4605c8af5da805c099b1efb7f15e8390781768bb3014276b465a7712b4ed06b"
)
ORIGINAL_BASE_SOURCE_SHA256 = (
    "4c47a77cf096df354e59d03096447c56bff890389869c6a75667a36c8471d024"
)
ORIGINAL_BASE_REPORT_SHA256 = (
    "c78449b1153221bd0d17854c4f6682062392d19a04cfd0a424a1c6f3fa3478cb"
)
MAX_SOURCE_BYTES = 16 * 1024 * 1024
MAX_DOCUMENT_BYTES = 16 * 1024 * 1024
HASH_CHUNK_BYTES = 1024 * 1024

AUDITED_FAMILIES = ("ast", "vm", "rust", "zig")
QUALIFIED_FAMILIES = ("vm", "rust", "zig")
FAMILY_SOURCE_PATHS: Mapping[str, tuple[str, ...]] = {
    "ast": ("candidates/ast_candidate.py",),
    "vm": ("candidates/vm_candidate.py", "candidates/_vm_native.c"),
    "rust": (
        "candidates/rust_candidate.py",
        "candidates/rust/py_bridge.c",
        "candidates/rust/src/lib.rs",
        "candidates/rust/src/search.rs",
        "candidates/rust/src/newline.rs",
        "candidates/rust/src/stack.rs",
        "candidates/rust/src/unicode_tables.rs",
    ),
    "zig": (
        "candidates/zig_candidate.py",
        "candidates/zig/py_bridge.c",
        "candidates/zig/mini_regex.zig",
    ),
}
NATIVE_ROLE_PATHS: Mapping[str, Mapping[str, tuple[str, str]]] = {
    "vm": {
        "native": (
            "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
            "candidates.vm_candidate:native-engine",
        ),
    },
    "rust": {
        "engine": (
            "candidates/_rust_engine.so",
            "candidates.rust_candidate:native-engine",
        ),
        "bridge": (
            "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
            "candidates.rust_candidate:native-bridge",
        ),
    },
    "zig": {
        "engine": (
            "candidates/_zig_probe.so",
            "candidates.zig_candidate:native-engine",
        ),
        "bridge": (
            "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
            "candidates.zig_candidate:native-bridge",
        ),
    },
}
EXPECTED_NATIVE_KEYS = frozenset(
    key
    for roles in NATIVE_ROLE_PATHS.values()
    for _path, key in roles.values()
)
BASE_CONTROL_NAMES = frozenset(
    {
        "direct_stdlib_re",
        "direct_cpython_sre",
        "third_party_regex",
        "aliased_regex",
        "cross_candidate",
        "cross_candidate_dotted",
        "dynamic_import",
        "chr_obfuscated_import",
        "join_obfuscated_import",
        "importlib_indirection",
        "builtins_subscript",
        "getattr_indirection",
        "foreign_ctypes",
        "unowned_zig_library",
        "zig_owned_path_reassignment",
        "environment_dispatch",
        "environment_mapping",
        "external_process",
        "dynamic_eval",
        "dynamic_exec",
        "benchmark_clock",
        "holdout_path",
        "benchmark_file",
        "unowned_vm_configuration",
        "native_posix_regex",
        "native_pcre",
        "native_cpython_import",
        "native_copyreg_unowned_family",
        "native_copyreg_near_miss",
        "native_dynamic_loader",
        "native_hidden_header",
        "native_hidden_extern",
        "rust_external_crate",
        "rust_environment",
        "rust_hidden_extern",
        "zig_external_package",
        "zig_hidden_extern",
        "zig_c_import",
        "native_benchmark_clock",
        "ignore_native_comments_and_display_literals",
        "allow_owned_rust_generic_object_copy_protocol_only",
        "preserve_rust_lifetimes_and_owned_pipeline",
        "parse_in_memory_owned_elf",
        "reject_excessive_elf_section_count",
        "reject_excessive_elf_symbol_string",
        "reject_in_memory_external_elf_dependency",
        "reject_bridge_without_owned_elf_link",
        "reject_disguised_third_party_elf_dependency",
        "accept_five_owned_synthetic_elf_binaries_and_python_api_symbols",
        "reject_vm_disguised_external_engine",
        "reject_vm_external_regex_symbol",
        "reject_vm_cross_candidate_engine_symbol",
        "reject_vm_untrusted_runpath",
        "reject_vm_wrong_module_initializer",
        "reject_zig_engine_disguised_external_dependency",
        "reject_zig_bridge_disguised_external_dependency",
        "reject_zig_bridge_wrong_linked_rust_engine",
        "reject_zig_bridge_wrong_engine_cross_candidate",
        "reject_zig_bridge_compiler_bypass",
        "reject_zig_bridge_executor_bypass",
        "reject_zig_bridge_unresolved_owned_symbols",
        "reject_zig_engine_untrusted_runpath",
        "reject_zig_bridge_untrusted_runpath",
        "reject_zig_rust_cross_candidate_symbol",
        "reject_rust_zig_cross_candidate_symbol",
        "reject_rust_bridge_untrusted_runpath",
        "accept_exact_ast_owned_memory_mappings",
        "accept_exact_vm_owned_memory_mappings",
        "accept_exact_rust_owned_memory_mappings",
        "accept_exact_zig_owned_memory_mappings",
        "reject_cross_candidate_actual_memory_mapping",
        "reject_external_regex_actual_memory_mapping",
        "reject_unapproved_candidate_actual_memory_mapping",
        "reject_deleted_owned_native_memory_mapping",
        "reject_invalid_elf",
        "reject_renamed_and_transitive_cargo_dependency",
    }
)
STRICT_CONTROL_NAMES = frozenset(
    {
        "direct_stdlib_re",
        "direct_cpython_sre",
        "third_party_regex",
        "cross_family_import",
        "dynamic_import",
        "enum_sys_modules",
        "aliased_registry",
        "from_import_sys_alias",
        "registry_assignment_alias",
        "getattr_registry",
        "joined_registry_key",
        "vars_module_registry",
        "dunder_module_registry",
        "cached_json_decoder_regex",
        "conditional_registry_delegation",
        "cross_family_registry",
        "function_globals_reflection",
        "os_sys_registry",
        "warnings_sys_registry",
        "c_python_module_registry",
        "c_python_module_loader",
        "c_computed_loader",
        "rust_external_crate",
        "rust_link_name_and_include",
        "rust_inline_assembly",
        "zig_external_package",
        "zig_dynamic_loader_and_external",
        "allow_owned_callback_calls",
        "allow_owned_generic_attributes",
        "allow_owned_rust_helper_imports",
        "allow_owned_zig_unicode_extern",
        "preserve_original_76_control_manifest",
    }
)


class AuditFailure(RuntimeError):
    """An additive V2 source, control, native mapping, or output was unsafe."""


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
        raise AuditFailure("additive no-delegation evidence is not canonical ASCII JSON") from error


def valid_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def require_candidate_free() -> None:
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


def relative_public_path(path: Path) -> str:
    require(isinstance(path, Path) and not path.is_symlink(), "a V2 public input is missing or is a symlink")
    try:
        resolved = path.resolve(strict=True)
        relative = resolved.relative_to(ROOT.resolve()).as_posix()
    except (OSError, RuntimeError, ValueError) as error:
        raise AuditFailure("a V2 public input is missing or escaped the repository") from error
    require(resolved.is_file(), f"a V2 public input is not a regular file: {relative}")
    require(
        relative
        in {
            "tools/postfinal_no_delegation_audit_v2.py",
            "tools/postfinal_no_delegation_audit_v1.py",
            "tools/audit_from_scratch.py",
            "tools/postfinal_from_scratch_audit_v2.py",
            "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V2.json",
            "candidates/audits/FROM-SCRATCH-AUDIT.json",
            "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V1.json",
        },
        f"refusing to inspect a private, final, guard, or unapproved input: {relative}",
    )
    return relative


def bounded_public_bytes(path: Path, *, maximum: int) -> tuple[bytes, str]:
    relative = relative_public_path(path)
    try:
        with path.open("rb") as stream:
            data = stream.read(maximum + 1)
    except OSError as error:
        raise AuditFailure(f"a pinned V2 public input cannot be read: {relative}") from error
    require(len(data) <= maximum, f"a pinned V2 public input exceeds its bound: {relative}")
    return data, hashlib.sha256(data).hexdigest()


def public_document(path: Path) -> tuple[dict[str, Any], str]:
    data, digest = bounded_public_bytes(path, maximum=MAX_DOCUMENT_BYTES)
    try:
        value = json.loads(data)
    except (UnicodeError, ValueError) as error:
        raise AuditFailure("a V2 public audit input is not valid JSON") from error
    require(isinstance(value, dict), "a V2 public audit input is not an object")
    return value, digest


def validate_controls(
    report: Mapping[str, Any],
    *,
    names: frozenset[str],
    label: str,
) -> dict[str, Any]:
    controls = report.get("self_test")
    require(isinstance(controls, dict), f"{label} omitted its exact self-test evidence")
    records = controls.get("checks")
    require(
        controls.get("passed") is True
        and controls.get("check_count") == len(names)
        and controls.get("failed") == []
        and controls.get("fixture_storage") == "in-memory only"
        and isinstance(records, list)
        and len(records) == len(names)
        and all(
            isinstance(record, dict)
            and isinstance(record.get("name"), str)
            and record.get("passed") is True
            for record in records
        )
        and {record["name"] for record in records} == names,
        f"{label} omitted, duplicated, weakened, or renamed an independent control",
    )
    return controls


def validate_base_report(report: Mapping[str, Any]) -> dict[str, dict[str, str]]:
    require(
        isinstance(report, Mapping)
        and report.get("schema_version") == 1
        and report.get("audit") == "bounded-from-scratch-engine-provenance"
        and report.get("postfinal_schema") == BASE_POSTFINAL_SCHEMA
        and report.get("passed") is True
        and report.get("result") == "PASS"
        and report.get("audit_source_path")
        == "tools/postfinal_from_scratch_audit_v2.py"
        and valid_sha256(report.get("audit_source_sha256"))
        and report.get("original_audit_source_path") == "tools/audit_from_scratch.py"
        and report.get("original_audit_source_sha256") == ORIGINAL_BASE_SOURCE_SHA256
        and report.get("original_v1_audit_report_path")
        == "candidates/audits/FROM-SCRATCH-AUDIT.json"
        and report.get("original_v1_audit_report_sha256")
        == ORIGINAL_BASE_REPORT_SHA256,
        "the additive V2 base report is missing, stale V1, or not source-bound",
    )
    validate_controls(report, names=BASE_CONTROL_NAMES, label="additive original 76-control audit")
    require(
        report.get("minimum_required_independent_families") == 3
        and type(report.get("verified_core_family_count")) is int
        and report["verified_core_family_count"] >= 3
        and type(report.get("verified_distinct_pipeline_count")) is int
        and report["verified_distinct_pipeline_count"] >= 3
        and set(report.get("all_public_source_families", ())) == set(AUDITED_FAMILIES),
        "the additive V2 base audit lost an independent candidate family",
    )
    manifest = report.get("manifest_provenance")
    mapping = report.get("runtime_native_mapping_provenance")
    native = report.get("native_elf_provenance")
    scope = report.get("scope")
    require(
        isinstance(manifest, Mapping)
        and manifest.get("passed") is True
        and isinstance(mapping, Mapping)
        and mapping.get("passed") is True
        and isinstance(native, Mapping)
        and native.get("passed") is True
        and native.get("audited_binary_count") == 5
        and native.get("expected_binary_count") == 5
        and isinstance(scope, Mapping)
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_or_case_fixture_access") is False
        and scope.get("mapped_binaries_hashed_against_static_elf") is True,
        "the additive V2 base audit omitted its closed source or actual native mapping proof",
    )
    families = report.get("families")
    require(isinstance(families, Mapping) and set(families) == set(AUDITED_FAMILIES), "the V2 base audit changed its complete source family graph")
    native_families = native.get("families")
    require(isinstance(native_families, Mapping), "the V2 base omitted its actual five native ELF records")
    result: dict[str, dict[str, str]] = {}
    for family in AUDITED_FAMILIES:
        current = families.get(family)
        require(
            isinstance(current, Mapping)
            and current.get("passed") is True,
            f"the additive V2 base candidate did not genuinely pass: {family}",
        )
        python = current.get("python_source")
        sources = current.get("native_sources")
        require(
            isinstance(python, Mapping)
            and python.get("file") == FAMILY_SOURCE_PATHS[family][0]
            and valid_sha256(python.get("sha256"))
            and isinstance(sources, list),
            f"the additive V2 base omitted the actual {family} Python source",
        )
        observed_sources = {python["file"]: python["sha256"]}
        for entry in sources:
            require(
                isinstance(entry, Mapping)
                and entry.get("passed") is True
                and isinstance(entry.get("file"), str)
                and valid_sha256(entry.get("sha256"))
                and entry["file"] not in observed_sources,
                f"the additive V2 base native source was missing or duplicated: {family}",
            )
            observed_sources[entry["file"]] = entry["sha256"]
        require(
            set(observed_sources) == set(FAMILY_SOURCE_PATHS[family]),
            f"the additive V2 base changed the closed {family} production source graph",
        )
        result[family] = observed_sources
        runtime = current.get("isolated_runtime")
        require(
            isinstance(runtime, Mapping)
            and runtime.get("passed") is True,
            f"the additive V2 base omitted independently guarded {family} execution",
        )
        if family == "ast":
            continue
        evidence = native_families.get(family)
        require(isinstance(evidence, Mapping) and evidence.get("passed") is True, f"the V2 base omitted parsed {family} ELF provenance")
        files = evidence.get("files")
        require(isinstance(files, Mapping) and set(files) == set(NATIVE_ROLE_PATHS[family]), f"the V2 base omitted an actual mapped {family} native role")
        for role, (relative, _key) in NATIVE_ROLE_PATHS[family].items():
            item = files.get(role)
            require(
                isinstance(item, Mapping)
                and item.get("file") == relative
                and valid_sha256(item.get("sha256")),
                f"the V2 base native role is missing or substituted: {family}/{role}",
            )
    return result


def validate_strict_controls(report: Mapping[str, Any]) -> None:
    require(
        report.get("schema") == IMMUTABLE_STRICT_SCHEMA
        and report.get("passed") is True
        and report.get("result") == "PASS"
        and report.get("audit_source_path")
        == "tools/postfinal_no_delegation_audit_v1.py"
        and report.get("audit_source_sha256") == IMMUTABLE_STRICT_SOURCE_SHA256
        and report.get("inherited_control_count") == 76,
        "the immutable predecessor no-delegation proof was replaced or invalid",
    )
    validate_controls(report, names=STRICT_CONTROL_NAMES, label="immutable 32-control no-delegation audit")
    native = report.get("native_elf_provenance")
    fingerprints = report.get("native_elf_fingerprints")
    scope = report.get("scope")
    require(
        isinstance(native, Mapping)
        and native.get("passed") is True
        and native.get("audited_binary_count") == 5
        and native.get("expected_binary_count") == 5
        and isinstance(fingerprints, Mapping)
        and set(fingerprints) == EXPECTED_NATIVE_KEYS
        and all(valid_sha256(item) for item in fingerprints.values())
        and isinstance(scope, Mapping)
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_or_case_fixture_access") is False,
        "the immutable predecessor no-delegation proof lost its five mapped native engines",
    )


def validate_immutable_strict_report_digest(digest: str) -> None:
    require(
        valid_sha256(digest)
        and digest == IMMUTABLE_STRICT_REPORT_SHA256,
        "the immutable historical V1 no-delegation report was substituted",
    )


def verify_pinned_runtime() -> None:
    require(
        sys.version_info[:3] == PINNED_VERSION
        and Path(sys.executable).resolve() == PINNED_PYTHON.resolve()
        and sys.flags.isolated
        and sys.dont_write_bytecode,
        "additive V2 audit requires pinned isolated CPython 3.14.6",
    )


def import_pinned_strict_v1() -> Any:
    require_candidate_free()
    _source, digest = bounded_public_bytes(IMMUTABLE_STRICT_SOURCE, maximum=MAX_SOURCE_BYTES)
    require(digest == IMMUTABLE_STRICT_SOURCE_SHA256, "the immutable no-delegation V1 source changed")
    root = str(ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)
    try:
        module = importlib.import_module("tools.postfinal_no_delegation_audit_v1")
    except (ImportError, OSError, RuntimeError, ValueError) as error:
        raise AuditFailure("the immutable no-delegation V1 source cannot be imported") from error
    require(
        Path(getattr(module, "__file__", "")).resolve()
        == IMMUTABLE_STRICT_SOURCE.resolve()
        and module.SCHEMA == IMMUTABLE_STRICT_SCHEMA
        and module.EXPECTED_SELF_TEST_CHECKS == 32
        and module.EXPECTED_SELF_TEST_NAMES == STRICT_CONTROL_NAMES
        and module.original.EXPECTED_SELF_TEST_CHECKS == 76
        and module.original.EXPECTED_SELF_TEST_NAMES == BASE_CONTROL_NAMES,
        "the immutable no-delegation control manifest or inherited source was substituted",
    )
    original_path = Path(getattr(module.original, "__file__", ""))
    require(original_path.resolve() == ORIGINAL_BASE_SOURCE.resolve(), "the original 76-control source was substituted")
    _original, original_digest = bounded_public_bytes(ORIGINAL_BASE_SOURCE, maximum=MAX_SOURCE_BYTES)
    require(original_digest == ORIGINAL_BASE_SOURCE_SHA256, "the original 76-control audit source changed")
    require_candidate_free()
    return module


def validated_v2_base() -> tuple[dict[str, Any], str, str]:
    report, digest = public_document(BASE_V2_REPORT)
    validate_base_report(report)
    _source, source_digest = bounded_public_bytes(BASE_V2_SOURCE, maximum=MAX_SOURCE_BYTES)
    require(
        report.get("audit_source_sha256") == source_digest,
        "the additive V2 base report is not bound to the actual wrapper source",
    )
    original_report, original_digest = public_document(ORIGINAL_BASE_REPORT)
    require(
        original_digest == ORIGINAL_BASE_REPORT_SHA256
        and original_report.get("schema_version") == 1
        and original_report.get("audit") == "bounded-from-scratch-engine-provenance"
        and original_report.get("result") == "PASS"
        and original_report.get("passed") is True,
        "the immutable original base report was modified or falsely attributed",
    )
    return report, digest, source_digest


def _verify_result_native(
    result: Mapping[str, Any],
    base: Mapping[str, Any],
) -> None:
    fingerprints = result.get("native_elf_fingerprints")
    require(
        isinstance(fingerprints, Mapping)
        and set(fingerprints) == EXPECTED_NATIVE_KEYS
        and all(valid_sha256(value) for value in fingerprints.values()),
        "the V2 no-delegation audit omitted one of five actual native mappings",
    )
    base_native = base["native_elf_provenance"]["families"]
    for family, roles in NATIVE_ROLE_PATHS.items():
        for role, (path, key) in roles.items():
            item = base_native[family]["files"][role]
            require(
                item.get("file") == path
                and item.get("sha256") == fingerprints[key],
                f"actual V2 no-delegation native hash disagrees with base: {family}/{role}",
            )
    families = result.get("families")
    require(isinstance(families, Mapping) and set(families) == set(AUDITED_FAMILIES), "the V2 no-delegation audit lost an independent source family")
    for family in AUDITED_FAMILIES:
        current = families[family]
        require(isinstance(current, Mapping) and current.get("passed") is True, f"the V2 no-delegation candidate did not pass: {family}")
        runtime = current.get("isolated_runtime")
        mapping = current.get("native_mapping_provenance")
        require(
            isinstance(runtime, Mapping)
            and runtime.get("passed") is True
            and isinstance(mapping, Mapping)
            and mapping.get("passed") is True,
            f"the V2 no-delegation candidate omitted independently verified native mappings: {family}",
        )


def run_audit() -> dict[str, Any]:
    """Run immutable V1 guards against only the independently verified V2 base."""

    require_candidate_free()
    verify_pinned_runtime()
    base, base_digest, base_source_digest = validated_v2_base()
    predecessor, predecessor_digest = public_document(IMMUTABLE_STRICT_REPORT)
    validate_immutable_strict_report_digest(predecessor_digest)
    validate_strict_controls(predecessor)
    strict = import_pinned_strict_v1()

    controls = strict.self_test()
    validate_controls(
        {"self_test": controls},
        names=STRICT_CONTROL_NAMES,
        label="actual immutable 32-control no-delegation self-test",
    )
    require_candidate_free()

    previous_loader = strict._load_original_report
    previous_report = strict.original.REPORT
    require(
        isinstance(previous_report, Path)
        and previous_report.resolve() == ORIGINAL_BASE_REPORT.resolve(),
        "the original immutable audit-report binding was already modified",
    )

    def load_verified_v2_base() -> tuple[dict[str, Any], str]:
        current, current_digest = public_document(BASE_V2_REPORT)
        require(
            current_digest == base_digest
            and current == base,
            "the independently verified V2 base changed before guarded execution",
        )
        validate_base_report(current)
        return current, current_digest

    strict._load_original_report = load_verified_v2_base
    strict.original.REPORT = BASE_V2_REPORT
    try:
        result = strict.run_audit()
    finally:
        strict.original.REPORT = previous_report
        strict._load_original_report = previous_loader
    require_candidate_free()

    require(
        isinstance(result, dict)
        and result.get("schema") == IMMUTABLE_STRICT_SCHEMA
        and result.get("passed") is True
        and result.get("result") == "PASS",
        "the independently guarded immutable 32-control audit did not actually pass",
    )
    validate_controls(result, names=STRICT_CONTROL_NAMES, label="completed immutable 32-control no-delegation audit")
    inherited = result.get("inherited_self_test")
    require(
        isinstance(inherited, Mapping)
        and inherited.get("passed") is True
        and inherited.get("check_count") == 76
        and inherited.get("failed") == []
        and inherited.get("fixture_storage") == "in-memory only"
        and isinstance(inherited.get("checks"), list)
        and len(inherited["checks"]) == 76
        and {item.get("name") for item in inherited["checks"] if isinstance(item, Mapping)}
        == BASE_CONTROL_NAMES,
        "the immutable audit did not independently rerun every inherited control",
    )
    require(
        result.get("base_audit_report_path")
        == "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V2.json"
        and result.get("base_audit_report_sha256") == base_digest,
        "the immutable worker unexpectedly consumed archived V1 base provenance",
    )
    graph = result.get("source_graph_provenance")
    scope = result.get("scope")
    require(
        isinstance(graph, Mapping)
        and graph.get("passed") is True
        and graph.get("implicit_rust_build_script_present") is False
        and graph.get("zig_build_manifest_present") is False
        and isinstance(scope, Mapping)
        and scope.get("closed_owned_source_graph") is True
        and scope.get("mapped_binaries_hashed_against_static_elf") is True
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_or_case_fixture_access") is False,
        "the immutable no-delegation audit weakened a runtime or source safety invariant",
    )
    _verify_result_native(result, base)

    _wrapper, wrapper_digest = bounded_public_bytes(SOURCE, maximum=MAX_SOURCE_BYTES)
    _strict, strict_digest = bounded_public_bytes(
        IMMUTABLE_STRICT_SOURCE,
        maximum=MAX_SOURCE_BYTES,
    )
    require(strict_digest == IMMUTABLE_STRICT_SOURCE_SHA256, "the immutable strict source changed during execution")
    immutable_controls = result["self_test"]
    result["schema"] = SCHEMA
    result["postfinal_schema"] = SCHEMA
    result["status"] = "PASS"
    result["audit_source_path"] = "tools/postfinal_no_delegation_audit_v2.py"
    result["audit_source_sha256"] = wrapper_digest
    result["base_audit_source_path"] = "tools/postfinal_from_scratch_audit_v2.py"
    result["base_audit_source_sha256"] = base_source_digest
    result["base_audit_report_path"] = (
        "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V2.json"
    )
    result["base_audit_report_sha256"] = base_digest
    result["base_audit_postfinal_schema"] = BASE_POSTFINAL_SCHEMA
    result["immutable_no_delegation_source_path"] = (
        "tools/postfinal_no_delegation_audit_v1.py"
    )
    result["immutable_no_delegation_source_sha256"] = strict_digest
    result["immutable_no_delegation_report_path"] = (
        "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V1.json"
    )
    result["immutable_no_delegation_report_sha256"] = predecessor_digest
    result["immutable_no_delegation_schema"] = IMMUTABLE_STRICT_SCHEMA
    result["immutable_control_source_schema"] = immutable_controls.get("schema")
    result["scope"] = {
        **dict(scope),
        "immutable_v1_source_preserved": True,
        "immutable_v1_reports_mutated": False,
        "base_v2_report_only": True,
        "production_report_path": (
            "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V2.json"
        ),
    }
    result["supersedes"] = {
        "schema": IMMUTABLE_STRICT_SCHEMA,
        "source_path": "tools/postfinal_no_delegation_audit_v1.py",
        "source_sha256": strict_digest,
        "report_path": "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V1.json",
        "report_sha256": predecessor_digest,
        "report_preserved": True,
    }
    require_candidate_free()
    return result


def _directory_fsync(path: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0)
    descriptor = os.open(path, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def write_report(report: Mapping[str, Any], output: Path) -> str:
    require(
        isinstance(output, Path)
        and output.resolve() == REPORT.resolve()
        and output.parent.resolve() == (ROOT / "candidates" / "audits").resolve()
        and not output.is_symlink(),
        "only the new additive V2 no-delegation report may be created",
    )
    require(
        report.get("schema") == SCHEMA
        and report.get("postfinal_schema") == SCHEMA
        and report.get("status") == "PASS"
        and report.get("result") == "PASS"
        and report.get("passed") is True
        and report.get("base_audit_report_path")
        == "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V2.json",
        "refusing to publish an incomplete, stale V1, or failing V2 report",
    )
    payload = canonical(dict(report)) + b"\n"
    require(len(payload) <= MAX_DOCUMENT_BYTES, "the additive V2 report exceeds its bound")
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
        raise AuditFailure("refusing to overwrite an immutable existing V2 report") from error
    except OSError as error:
        raise AuditFailure("the exact additive V2 report could not be exclusively created") from error
    try:
        view = memoryview(payload)
        while view:
            count = os.write(descriptor, view)
            require(count > 0, "the additive V2 report write made no progress")
            view = view[count:]
        os.fsync(descriptor)
        _directory_fsync(output.parent)
    except OSError as error:
        raise AuditFailure("the additive V2 report could not be durably completed") from error
    finally:
        os.close(descriptor)
    return hashlib.sha256(payload).hexdigest()


def _synthetic_controls(names: frozenset[str]) -> dict[str, Any]:
    records = [{"name": name, "passed": True} for name in sorted(names)]
    return {
        "passed": True,
        "check_count": len(records),
        "failed": [],
        "checks": records,
        "fixture_storage": "in-memory only",
    }


def _synthetic_base() -> dict[str, Any]:
    families: dict[str, Any] = {}
    native_families: dict[str, Any] = {}
    for family in AUDITED_FAMILIES:
        sources = FAMILY_SOURCE_PATHS[family]
        families[family] = {
            "passed": True,
            "python_source": {
                "file": sources[0],
                "sha256": hashlib.sha256(sources[0].encode("ascii")).hexdigest(),
            },
            "native_sources": [
                {
                    "file": path,
                    "sha256": hashlib.sha256(path.encode("ascii")).hexdigest(),
                    "passed": True,
                }
                for path in sources[1:]
            ],
            "isolated_runtime": {"passed": True},
        }
        if family in NATIVE_ROLE_PATHS:
            native_families[family] = {
                "passed": True,
                "files": {
                    role: {
                        "file": relative,
                        "sha256": hashlib.sha256(relative.encode("ascii")).hexdigest(),
                    }
                    for role, (relative, _key) in NATIVE_ROLE_PATHS[family].items()
                },
            }
    return {
        "schema_version": 1,
        "audit": "bounded-from-scratch-engine-provenance",
        "postfinal_schema": BASE_POSTFINAL_SCHEMA,
        "passed": True,
        "result": "PASS",
        "audit_source_path": "tools/postfinal_from_scratch_audit_v2.py",
        "audit_source_sha256": hashlib.sha256(b"synthetic additive V2 source").hexdigest(),
        "original_audit_source_path": "tools/audit_from_scratch.py",
        "original_audit_source_sha256": ORIGINAL_BASE_SOURCE_SHA256,
        "original_v1_audit_report_path": "candidates/audits/FROM-SCRATCH-AUDIT.json",
        "original_v1_audit_report_sha256": ORIGINAL_BASE_REPORT_SHA256,
        "minimum_required_independent_families": 3,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
        "all_public_source_families": list(AUDITED_FAMILIES),
        "self_test": _synthetic_controls(BASE_CONTROL_NAMES),
        "manifest_provenance": {"passed": True},
        "native_elf_provenance": {
            "passed": True,
            "audited_binary_count": 5,
            "expected_binary_count": 5,
            "families": native_families,
        },
        "runtime_native_mapping_provenance": {"passed": True},
        "families": families,
        "scope": {
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
            "mapped_binaries_hashed_against_static_elf": True,
        },
    }


def _synthetic_strict() -> dict[str, Any]:
    return {
        "schema": IMMUTABLE_STRICT_SCHEMA,
        "passed": True,
        "result": "PASS",
        "audit_source_path": "tools/postfinal_no_delegation_audit_v1.py",
        "audit_source_sha256": IMMUTABLE_STRICT_SOURCE_SHA256,
        "inherited_control_count": 76,
        "self_test": _synthetic_controls(STRICT_CONTROL_NAMES),
        "native_elf_provenance": {
            "passed": True,
            "audited_binary_count": 5,
            "expected_binary_count": 5,
        },
        "native_elf_fingerprints": {
            key: hashlib.sha256(key.encode("ascii")).hexdigest()
            for key in sorted(EXPECTED_NATIVE_KEYS)
        },
        "scope": {
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        },
    }


def candidate_free_self_test() -> dict[str, Any]:
    """Exercise all V2 provenance poison controls entirely in memory."""

    require_candidate_free()
    checks: list[dict[str, Any]] = []

    def check(name: str, value: bool) -> None:
        checks.append({"name": name, "passed": bool(value)})

    def rejected(name: str, action: Any) -> None:
        try:
            action()
        except (AuditFailure, KeyError, OverflowError, TypeError, ValueError):
            check(name, True)
        else:
            check(name, False)

    check("immutable-base-control-manifest-is-exactly-76", len(BASE_CONTROL_NAMES) == 76)
    check("immutable-no-delegation-control-manifest-is-exactly-32", len(STRICT_CONTROL_NAMES) == 32)
    check("three-fully-independent-qualified-native-families", QUALIFIED_FAMILIES == ("vm", "rust", "zig"))
    check("include-independent-pure-python-reference-family", AUDITED_FAMILIES == ("ast", "vm", "rust", "zig"))
    check("exactly-five-independent-owned-native-roles", len(EXPECTED_NATIVE_KEYS) == 5)
    check("pin-immutable-strict-source-sha256", valid_sha256(IMMUTABLE_STRICT_SOURCE_SHA256))
    check("pin-immutable-strict-report-sha256", valid_sha256(IMMUTABLE_STRICT_REPORT_SHA256))
    check("pin-immutable-base-source-sha256", valid_sha256(ORIGINAL_BASE_SOURCE_SHA256))
    check("pin-immutable-original-base-report-sha256", valid_sha256(ORIGINAL_BASE_REPORT_SHA256))
    check("v2-no-delegation-schema-is-independent", SCHEMA != IMMUTABLE_STRICT_SCHEMA and SCHEMA.endswith("-v2"))
    check("v2-base-postfinal-schema-is-independent", BASE_POSTFINAL_SCHEMA.endswith("-v2"))

    surrogate = "\ud800\n\udfff"
    encoded = canonical({"surrogate": surrogate})
    check("canonical-v2-proof-is-ascii", encoded.isascii())
    check("canonical-v2-proof-preserves-lone-surrogates", json.loads(encoded)["surrogate"] == surrogate)
    check("canonical-v2-proof-has-no-unescaped-newline", b"\n" not in encoded)
    rejected("reject-nonfinite-proof-value", lambda: canonical({"poison": float("nan")}))

    base = _synthetic_base()
    sources = validate_base_report(base)
    check("accept-only-synthetic-fully-qualified-v2-base", set(sources) == set(AUDITED_FAMILIES))
    predecessor = _synthetic_strict()
    validate_strict_controls(predecessor)
    check("accept-only-synthetic-exact-immutable-v1-controls", True)
    validate_immutable_strict_report_digest(IMMUTABLE_STRICT_REPORT_SHA256)
    check("accept-only-pinned-immutable-v1-no-delegation-report", True)

    def clone(value: Any) -> Any:
        return json.loads(canonical(value))

    poisoned = clone(base)
    poisoned.pop("postfinal_schema")
    rejected("reject-stale-unmarked-original-v1-report", lambda: validate_base_report(poisoned))
    poisoned = clone(base)
    poisoned["postfinal_schema"] = "rebar-postfinal-from-scratch-audit-v1"
    rejected("reject-wrong-v1-postfinal-schema", lambda value=poisoned: validate_base_report(value))
    poisoned = clone(base)
    poisoned["schema_version"] = 2
    rejected("preserve-cpython-oracle-compatible-base-schema-version", lambda value=poisoned: validate_base_report(value))
    poisoned = clone(base)
    poisoned["audit"] = "poison"
    rejected("reject-changed-original-base-audit-identity", lambda value=poisoned: validate_base_report(value))
    poisoned = clone(base)
    poisoned["audit_source_path"] = "tools/audit_from_scratch.py"
    rejected("reject-stale-v1-base-audit-source", lambda value=poisoned: validate_base_report(value))
    poisoned = clone(base)
    poisoned["original_audit_source_sha256"] = "0" * 64
    rejected("reject-changed-immutable-base-source", lambda value=poisoned: validate_base_report(value))
    poisoned = clone(base)
    poisoned["original_v1_audit_report_sha256"] = "0" * 64
    rejected("reject-changed-immutable-v1-base-report", lambda value=poisoned: validate_base_report(value))
    poisoned = clone(base)
    poisoned["self_test"]["checks"].pop()
    rejected("reject-one-omitted-inherited-base-control", lambda value=poisoned: validate_base_report(value))
    poisoned = clone(base)
    poisoned["self_test"]["checks"][0]["passed"] = False
    rejected("reject-one-failing-inherited-base-control", lambda value=poisoned: validate_base_report(value))
    poisoned = clone(base)
    poisoned["self_test"]["checks"][0]["name"] = "substituted"
    rejected("reject-renamed-inherited-base-control", lambda value=poisoned: validate_base_report(value))
    poisoned = clone(base)
    poisoned["verified_distinct_pipeline_count"] = 2
    rejected("reject-reused-or-insufficient-engine-family", lambda value=poisoned: validate_base_report(value))
    for family in AUDITED_FAMILIES:
        poisoned = clone(base)
        poisoned["families"].pop(family)
        rejected("reject-missing-owned-source-family:" + family, lambda value=poisoned: validate_base_report(value))
        poisoned = clone(base)
        poisoned["families"][family]["python_source"]["sha256"] = "x"
        rejected("reject-invalid-owned-source-binding:" + family, lambda value=poisoned: validate_base_report(value))
    for family, roles in NATIVE_ROLE_PATHS.items():
        for role in roles:
            poisoned = clone(base)
            poisoned["native_elf_provenance"]["families"][family]["files"].pop(role)
            rejected(
                "reject-missing-owned-native-role:" + family + "/" + role,
                lambda value=poisoned: validate_base_report(value),
            )
            poisoned = clone(base)
            poisoned["native_elf_provenance"]["families"][family]["files"][role]["sha256"] = "0"
            rejected(
                "reject-invalid-owned-native-binding:" + family + "/" + role,
                lambda value=poisoned: validate_base_report(value),
            )
    poisoned = clone(base)
    poisoned["runtime_native_mapping_provenance"]["passed"] = False
    rejected("reject-missing-actual-native-mappings", lambda value=poisoned: validate_base_report(value))
    poisoned = clone(base)
    poisoned["scope"]["holdout_or_case_fixture_access"] = True
    rejected("reject-nonpublic-or-final-fixture-access", lambda value=poisoned: validate_base_report(value))
    poisoned = clone(base)
    poisoned["scope"]["benchmark_or_timing_executed"] = True
    rejected("reject-any-benchmark-or-timing", lambda value=poisoned: validate_base_report(value))

    poisoned = clone(predecessor)
    poisoned["self_test"]["checks"].pop()
    rejected("reject-omitted-immutable-no-delegation-control", lambda value=poisoned: validate_strict_controls(value))
    poisoned = clone(predecessor)
    poisoned["self_test"]["checks"][0]["passed"] = False
    rejected("reject-failing-immutable-no-delegation-control", lambda value=poisoned: validate_strict_controls(value))
    poisoned = clone(predecessor)
    poisoned["native_elf_fingerprints"].pop(next(iter(EXPECTED_NATIVE_KEYS)))
    rejected("reject-omitted-independent-native-fingerprint", lambda value=poisoned: validate_strict_controls(value))
    poisoned = clone(predecessor)
    poisoned["native_elf_fingerprints"]["foreign:regex"] = "0" * 64
    rejected("reject-external-or-cross-candidate-regex-engine", lambda value=poisoned: validate_strict_controls(value))
    poisoned = clone(predecessor)
    poisoned["audit_source_sha256"] = "0" * 64
    rejected("reject-substituted-immutable-no-delegation-source", lambda value=poisoned: validate_strict_controls(value))
    rejected(
        "reject-substituted-historical-no-delegation-report-digest",
        lambda: validate_immutable_strict_report_digest("0" * 64),
    )

    require_candidate_free()
    failed = [check["name"] for check in checks if not check["passed"]]
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS" if not failed else "FAIL",
        "result": "PASS" if not failed else "FAIL",
        "passed": not failed,
        "checks": checks,
        "check_count": len(checks),
        "failed": failed,
        "immutable_no_delegation_controls": len(STRICT_CONTROL_NAMES),
        "inherited_original_controls": len(BASE_CONTROL_NAMES),
        "independent_families": list(AUDITED_FAMILIES),
        "owned_native_roles": len(EXPECTED_NATIVE_KEYS),
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
    commands.add_argument("--self-test", action="store_true", help="run only in-memory, candidate-free controls")
    commands.add_argument("--audit", action="store_true", help="explicitly run source-bound, isolated V2 verification")
    parser.add_argument("--output", type=Path, default=REPORT, help="the sole exact additive V2 report path")
    args = parser.parse_args(arguments)
    try:
        require_candidate_free()
        if args.self_test:
            require(args.output == REPORT, "the candidate-free self-test does not accept an output path")
            report = candidate_free_self_test()
            sys.stdout.buffer.write(canonical(report) + b"\n")
            return 0 if report.get("passed") is True else 1
        report = run_audit()
        digest = write_report(report, args.output)
        result = {
            "schema": SCHEMA,
            "postfinal_schema": SCHEMA,
            "status": "PASS",
            "result": "PASS",
            "passed": True,
            "report": "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V2.json",
            "report_sha256": digest,
            "audit_source_sha256": report["audit_source_sha256"],
            "base_audit_report_path": report["base_audit_report_path"],
            "base_audit_report_sha256": report["base_audit_report_sha256"],
            "self_test_checks": len(STRICT_CONTROL_NAMES),
            "inherited_self_test_checks": len(BASE_CONTROL_NAMES),
            "verified_family_count": len(report["families"]),
            "verified_native_library_count": len(report["native_elf_fingerprints"]),
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
            "immutable_v1_reports_mutated": False,
        }
        sys.stdout.buffer.write(canonical(result) + b"\n")
        return 0
    except (AuditFailure, OSError, RuntimeError, TypeError, ValueError, KeyError) as error:
        result = {
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
        sys.stdout.buffer.write(canonical(result) + b"\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
