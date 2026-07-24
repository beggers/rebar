#!/usr/bin/env python3
"""Verify four isolated fresh-case workers using public, nonproduction inputs.

``--self-test`` is entirely in-memory: it never starts a process, imports a
candidate, reads a file, draws entropy, or uses a clock.  ``--smoke`` must be
explicitly requested.  Its only cases use the published key
``bytes(range(32))``; it never opens a final holdout or requests a timing.
"""

from __future__ import annotations

import argparse
import base64
import collections
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
from typing import Any, Mapping


SCHEMA = "rebar-postfinal-fresh-holdout-adapter-smoke-v2"
ADAPTER_SCHEMA = "rebar-postfinal-fresh-holdout-adapter-v1"
ADAPTER_AUDIT_SCHEMA = "rebar-postfinal-fresh-holdout-adapter-audit-v2"
ADAPTER_DECLARED_AUDIT_SCHEMA = "rebar-postfinal-fresh-holdout-adapter-audit-v1"
STRICT_AUDIT_SCHEMA = "rebar-postfinal-no-delegation-audit-v1"
UNIVERSAL_ORACLE_SCHEMA = "rebar-python-re-universal-public-oracle-v1"
CASE_SCHEMA = "rebar-postfinal-fresh-holdout-v1-case"

ROOT = Path(__file__).resolve().parent.parent
SOURCE_PATH = ROOT / "tools" / "postfinal_fresh_holdout_adapter_smoke_v1.py"
FRESH_SOURCE_PATH = ROOT / "tools" / "postfinal_fresh_holdout_v1.py"
ADAPTER_SOURCE_PATH = ROOT / "tools" / "postfinal_fresh_holdout_adapter_v1.py"
STRICT_SOURCE_PATH = ROOT / "tools" / "postfinal_no_delegation_audit_v1.py"
BASE_AUDIT_PATH = ROOT / "candidates" / "audits" / "FROM-SCRATCH-AUDIT.json"
STRICT_AUDIT_PATH = (
    ROOT / "candidates" / "audits" / "POSTFINAL-NO-DELEGATION-AUDIT-V1.json"
)
ADAPTER_AUDIT_PATH = (
    ROOT / "candidates" / "audits" / "POSTFINAL-FRESH-HOLDOUT-ADAPTER-AUDIT-V2.json"
)
UNIVERSAL_ORACLE_PATH = (
    ROOT / "candidates" / "evidence" / "python-re-universal-public-oracle-v3-all.json"
)
OUTPUT_PATH = (
    ROOT / "candidates" / "audits" / "POSTFINAL-FRESH-HOLDOUT-ADAPTER-SMOKE-V2.json"
)

PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
PINNED_VERSION = (3, 14, 6)
ADAPTER_SOURCE_SHA256 = (
    "cc29f089344e2ccfb85765689d36938f01ee2e26289c525bafd7aec629cbdba0"
)
STRICT_SOURCE_SHA256 = (
    "e505e17f4849242d990ee8e184794962327335d807000d1a8a0e65a0cb10c0ed"
)
ADAPTER_AUDIT_SOURCE_SHA256 = (
    "eb1db6b4985cf10364997477f9ca318a409e7d04e38ba7a947763b419aef138b"
)
BOOTSTRAP_SOURCE_SHA256 = (
    "d9950b54c140e4739e3edae09c07a68e588a4bbc5f3680ceb7576941d75fe0a8"
)
BASE_WORKER_SOURCE_SHA256 = (
    "527c5a5b1c3a717d9786ae04fb8ad738987b10c3a92319d542df574360b84656"
)
DERIVED_WORKER_SOURCE_SHA256 = (
    "8bf0774b8f98d89545fd4d5b336c65bdd570812ee84f10da6ae9bc40c9c02590"
)
WORKER_EXTENSION_SHA256 = (
    "1c629b89f61d5dc4c73cfb0da4034c5b1081c3d5207a42ae253a0d20a43535e3"
)
ORACLE_SOURCE_PATH = "tools/python_re_universal_public_oracle_stage03.py"
ORACLE_SOURCE_SHA256 = (
    "477c3f7e9955a9207b9345fc281705b6d643446b5d5c933009fa22a64b8d44ce"
)

FIXED_NONPRODUCTION_KEY = bytes(range(32))
FIXED_KEY_LABEL = "public fixed nonproduction bytes(range(32)); never OS entropy"
FIXTURE_DOMAIN = "rebar/fresh-holdout-adapter/public-fixed-key-smoke/v1"
LANE_DOMAIN = b"rebar/fresh-holdout/v1/observable-lane\x00"
CHANNELS = (
    "compiled-pattern-metadata",
    "return-values-match-spans-and-buffer-representation",
    "exception-class-arguments-and-public-pattern-error-fields",
    "documented-converter-callback-warning-and-scanner-traces",
)
PARTICIPANTS = ("re", "rust", "vm", "zig")
CANDIDATES = PARTICIPANTS[1:]
SEMANTIC_FAMILIES = (
    "literal",
    "character-class",
    "alternation",
    "greedy-repeat",
    "lazy-repeat",
    "counted-repeat",
    "named-captures",
    "backreference",
    "lookahead",
    "fixed-lookbehind",
    "multiline-anchor",
    "dotall-newline",
    "ignorecase",
    "unicode-word",
    "word-boundary",
    "empty-progress",
)
MODULE_OPERATIONS = (
    "search",
    "match",
    "fullmatch",
    "findall",
    "finditer",
    "split",
    "sub",
    "subn",
)
COMPILED_OPERATIONS = MODULE_OPERATIONS + ("scanner",)
FAMILY_COUNT = 16
STRATUM_COUNT = 16
VARIANT_COUNT = 256
EXPECTED_CASES = FAMILY_COUNT * (
    (STRATUM_COUNT // 2) * len(MODULE_OPERATIONS)
    + (STRATUM_COUNT // 2) * len(COMPILED_OPERATIONS)
)
EXPECTED_SNAPSHOTS = EXPECTED_CASES * len(PARTICIPANTS)
EXPECTED_COMPARISONS = EXPECTED_CASES * len(CANDIDATES) * len(CHANNELS)
EXPECTED_RUNTIME_GUARD_CHECKS = (
    2 * len(PARTICIPANTS) + 2 * EXPECTED_CASES * len(PARTICIPANTS)
)
EXPECTED_NATIVE_KEYS = frozenset(
    {
        "candidates.rust_candidate:native-bridge",
        "candidates.rust_candidate:native-engine",
        "candidates.vm_candidate:native-engine",
        "candidates.zig_candidate:native-bridge",
        "candidates.zig_candidate:native-engine",
    }
)
EXPECTED_ANCHORS = {
    "frozen-worker-mode": 1,
    "guarded-fresh-functions": 1,
    "guarded-fresh-dispatch": 1,
}
MAX_SOURCE_BYTES = 16 * 1024 * 1024
MAX_DOCUMENT_BYTES = 16 * 1024 * 1024
HASH_CHUNK_BYTES = 1024 * 1024


class SmokeError(RuntimeError):
    """Public fixed-key provenance or four-channel isolation failed."""


class SmokeMismatch(SmokeError):
    """Preserve one fixed-public-input mismatch without writing false proof."""

    def __init__(self, message: str, details: Mapping[str, Any]) -> None:
        super().__init__(message)
        self.details = dict(details)


def require(condition: Any, message: str) -> None:
    if not condition:
        raise SmokeError(message)


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
        raise SmokeError("public fixed-key evidence is not canonical ASCII JSON") from error


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
    require(not loaded, f"public smoke controller imported a candidate: {loaded!r}")


def valid_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def bounded_file(path: Path, *, maximum: int) -> tuple[bytes, str]:
    require(isinstance(path, Path), "a public input path is invalid")
    require(not path.is_symlink(), "a public smoke input cannot be a symlink")
    try:
        resolved = path.resolve(strict=True)
        relative = resolved.relative_to(ROOT.resolve()).as_posix()
    except (OSError, RuntimeError, ValueError) as error:
        raise SmokeError("a required public smoke input is missing or escaped the repository") from error
    require(resolved.is_file(), "a required public smoke input is not a regular file")
    require(
        relative
        in {
            "tools/postfinal_fresh_holdout_adapter_smoke_v1.py",
            "tools/postfinal_fresh_holdout_v1.py",
            "tools/postfinal_fresh_holdout_adapter_v1.py",
            "tools/postfinal_no_delegation_audit_v1.py",
            "candidates/audits/FROM-SCRATCH-AUDIT.json",
            "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V1.json",
            "candidates/audits/POSTFINAL-FRESH-HOLDOUT-ADAPTER-AUDIT-V2.json",
            "candidates/evidence/python-re-universal-public-oracle-v3-all.json",
        },
        "a private, final, marker, or nonpublic input was refused",
    )
    try:
        with resolved.open("rb") as stream:
            data = stream.read(maximum + 1)
    except OSError as error:
        raise SmokeError(f"a required public smoke input cannot be read: {relative}") from error
    require(len(data) <= maximum, f"a public smoke input exceeded its bounded size: {relative}")
    return data, hashlib.sha256(data).hexdigest()


def public_document(path: Path) -> tuple[dict[str, Any], str]:
    data, digest = bounded_file(path, maximum=MAX_DOCUMENT_BYTES)
    try:
        value = json.loads(data)
    except (UnicodeError, ValueError) as error:
        raise SmokeError("public fixed-key audit evidence is not valid JSON") from error
    require(isinstance(value, dict), "public fixed-key audit evidence is not an object")
    return value, digest


def verify_pinned_runtime() -> None:
    require(
        sys.version_info[:3] == PINNED_VERSION
        and Path(sys.executable).resolve() == PINNED_PYTHON.resolve()
        and sys.flags.isolated
        and sys.dont_write_bytecode,
        "public fixed-key smoke requires the exact pinned isolated CPython 3.14.6",
    )


def verify_passing_checks(document: Mapping[str, Any], expected: int, label: str) -> None:
    tests = document.get("self_test")
    require(isinstance(tests, Mapping), f"{label} omitted its pinned malicious controls")
    checks = tests.get("checks")
    require(
        tests.get("passed") is True
        and tests.get("check_count") == expected
        and tests.get("failed") == []
        and isinstance(checks, list)
        and len(checks) == expected
        and all(
            isinstance(item, Mapping)
            and isinstance(item.get("name"), str)
            and item.get("passed") is True
            for item in checks
        )
        and len({item["name"] for item in checks}) == expected,
        f"{label} omitted or weakened its exact named malicious controls",
    )


def verify_base_audit(document: Mapping[str, Any]) -> None:
    require(
        document.get("schema_version") == 1
        and document.get("audit") == "bounded-from-scratch-engine-provenance"
        and document.get("passed") is True
        and document.get("result") == "PASS",
        "the original from-scratch audit is not a passing public report",
    )
    verify_passing_checks(document, 76, "original from-scratch audit")
    native = document.get("native_elf_provenance")
    mappings = document.get("runtime_native_mapping_provenance")
    scope = document.get("scope")
    require(
        isinstance(native, Mapping)
        and native.get("passed") is True
        and native.get("audited_binary_count") == 5
        and native.get("expected_binary_count") == 5
        and isinstance(mappings, Mapping)
        and mappings.get("passed") is True
        and isinstance(scope, Mapping)
        and scope.get("holdout_or_case_fixture_access") is False
        and scope.get("benchmark_or_timing_executed") is False,
        "the original audit did not bind five independently mapped owned native engines",
    )
    families = document.get("families")
    require(
        isinstance(families, Mapping)
        and set(families) == {"ast", "rust", "vm", "zig"}
        and all(
            isinstance(families[name], Mapping)
            and families[name].get("passed") is True
            for name in families
        ),
        "the original audit does not establish all independently owned families",
    )


def verify_strict_audit(
    document: Mapping[str, Any],
    *,
    base_audit_sha256: str,
) -> dict[str, str]:
    require(
        document.get("schema") == STRICT_AUDIT_SCHEMA
        and document.get("passed") is True
        and document.get("result") == "PASS"
        and document.get("audit_source_path")
        == "tools/postfinal_no_delegation_audit_v1.py"
        and document.get("audit_source_sha256") == STRICT_SOURCE_SHA256
        and document.get("base_audit_report_path")
        == "candidates/audits/FROM-SCRATCH-AUDIT.json"
        and document.get("base_audit_report_sha256") == base_audit_sha256
        and document.get("inherited_control_count") == 76,
        "the independently guarded strict audit is not bound to the passing original audit",
    )
    verify_passing_checks(document, 32, "strict no-delegation audit")
    graph = document.get("source_graph_provenance")
    native = document.get("native_elf_provenance")
    scope = document.get("scope")
    require(
        isinstance(graph, Mapping)
        and graph.get("passed") is True
        and graph.get("implicit_rust_build_script_present") is False
        and graph.get("zig_build_manifest_present") is False
        and isinstance(native, Mapping)
        and native.get("passed") is True
        and native.get("audited_binary_count") == 5
        and native.get("expected_binary_count") == 5
        and isinstance(scope, Mapping)
        and scope.get("holdout_or_case_fixture_access") is False
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("closed_owned_source_graph") is True
        and scope.get("persistent_measurement_worker_available") is True
        and scope.get("mapped_binaries_hashed_against_static_elf") is True,
        "the strict no-delegation audit changed its isolation or exact native evidence",
    )
    fingerprints = document.get("native_elf_fingerprints")
    require(
        isinstance(fingerprints, dict)
        and set(fingerprints) == EXPECTED_NATIVE_KEYS
        and all(valid_sha256(item) for item in fingerprints.values()),
        "the strict audit omitted or changed one of the five owned native engines",
    )
    return dict(fingerprints)


def verify_universal_oracle(
    document: Mapping[str, Any],
    *,
    base_audit_sha256: str,
    native_fingerprints: Mapping[str, str],
) -> None:
    require(
        document.get("schema") == UNIVERSAL_ORACLE_SCHEMA
        and document.get("status") == "PASS"
        and document.get("selected") == "all"
        and document.get("selected_candidates") == list(CANDIDATES)
        and document.get("cases") == 8_192
        and document.get("observations_per_case") == 48
        and document.get("observations_per_candidate") == 393_216
        and document.get("total_comparisons") == 1_179_648
        and document.get("mismatches") == 0
        and document.get("performance_fixtures_read") == 0
        and document.get("holdout_cases_read") == 0
        and document.get("external_regex_packages") == 0
        and document.get("benchmark_or_timing_executed") is False,
        "the complete public correctness oracle is not a source-bound all-candidate PASS",
    )
    audit = document.get("audit")
    require(
        isinstance(audit, Mapping)
        and audit.get("oracle_source_path") == ORACLE_SOURCE_PATH
        and audit.get("oracle_source_sha256") == ORACLE_SOURCE_SHA256
        and audit.get("audit_path") == "candidates/audits/FROM-SCRATCH-AUDIT.json"
        and audit.get("audit_sha256") == base_audit_sha256
        and audit.get("selected_candidates") == list(CANDIDATES),
        "the complete public oracle changed its frozen original audit or source identity",
    )
    native = audit.get("native_binary_sha256")
    require(isinstance(native, Mapping) and set(native) == set(CANDIDATES), "the public oracle omitted an independent native engine")
    bindings = {
        "rust": {
            "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so":
            "candidates.rust_candidate:native-bridge",
            "candidates/_rust_engine.so":
            "candidates.rust_candidate:native-engine",
        },
        "vm": {
            "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so":
            "candidates.vm_candidate:native-engine",
        },
        "zig": {
            "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so":
            "candidates.zig_candidate:native-bridge",
            "candidates/_zig_probe.so":
            "candidates.zig_candidate:native-engine",
        },
    }
    reports = document.get("candidate_reports")
    require(isinstance(reports, Mapping) and set(reports) == set(CANDIDATES), "the public oracle omitted an actual completed candidate")
    for family, expected in bindings.items():
        values = native.get(family)
        result = reports.get(family)
        require(
            isinstance(values, Mapping)
            and set(values) == set(expected)
            and all(values[path] == native_fingerprints[key] for path, key in expected.items()),
            f"the public oracle changed its exact native mappings: {family}",
        )
        require(
            isinstance(result, Mapping)
            and result.get("status") == "PASS"
            and result.get("cases") == 8_192
            and result.get("checks") == 393_216
            and result.get("mismatches") == 0
            and result.get("holdout_cases_read") == 0
            and result.get("external_regex_packages") == 0
            and result.get("benchmark_or_timing_executed") is False,
            f"the complete public oracle did not qualify {family}",
        )


def verify_adapter_audit(
    document: Mapping[str, Any],
    *,
    native_fingerprints: Mapping[str, str],
    base_audit_sha256: str,
    strict_audit_sha256: str,
) -> None:
    require(
        document.get("schema") == ADAPTER_AUDIT_SCHEMA
        and document.get("result") == "PASS"
        and document.get("status") == "PASS"
        and document.get("passed") is True
        and document.get("audit_source_path")
        == "tools/postfinal_fresh_holdout_adapter_audit_v1.py"
        and document.get("audit_source_sha256") == ADAPTER_AUDIT_SOURCE_SHA256
        and document.get("adapter_source_path")
        == "tools/postfinal_fresh_holdout_adapter_v1.py"
        and document.get("adapter_source_sha256") == ADAPTER_SOURCE_SHA256
        and document.get("adapter_declared_audit_schema")
        == ADAPTER_DECLARED_AUDIT_SCHEMA
        and document.get("guard_source_path")
        == "tools/postfinal_no_delegation_audit_v1.py"
        and document.get("guard_source_sha256") == STRICT_SOURCE_SHA256
        and document.get("bootstrap_source_path")
        == "tools/postfinal_fresh_holdout_bootstrap_v1.c"
        and document.get("bootstrap_source_sha256") == BOOTSTRAP_SOURCE_SHA256
        and document.get("base_worker_source_sha256") == BASE_WORKER_SOURCE_SHA256
        and document.get("derived_worker_source_sha256") == DERIVED_WORKER_SOURCE_SHA256
        and document.get("worker_extension_sha256") == WORKER_EXTENSION_SHA256
        and document.get("worker_anchor_counts") == EXPECTED_ANCHORS
        and document.get("channel_names") == list(CHANNELS)
        and document.get("inherited_control_count") == 76
        and document.get("original_no_delegation_control_count") == 32,
        "the independent adapter source audit is missing, failing, or not frozen",
    )
    pinned_native = document.get("native_elf_fingerprints")
    require(
        isinstance(pinned_native, Mapping)
        and dict(pinned_native) == dict(native_fingerprints),
        "the independent adapter audit changed an owned native fingerprint",
    )
    native = document.get("native_elf_provenance")
    require(
        isinstance(native, Mapping)
        and native.get("passed") is True
        and native.get("audited_binary_count") == 5
        and native.get("expected_binary_count") == 5
        and native.get("base_audit_report_sha256") == base_audit_sha256
        and native.get("postfinal_no_delegation_audit_path") == str(STRICT_AUDIT_PATH)
        and native.get("postfinal_no_delegation_audit_sha256") == strict_audit_sha256
        and native.get("postfinal_no_delegation_audit_source_sha256")
        == STRICT_SOURCE_SHA256
        and native.get("postfinal_no_delegation_control_count") == 32
        and native.get("inherited_control_count") == 76,
        "the adapter audit omitted or changed exact original and strict native provenance",
    )
    verify_passing_checks(document, 63, "independent fresh adapter audit")
    scope = document.get("scope")
    require(
        isinstance(scope, Mapping)
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_or_case_fixture_access") is False
        and scope.get("candidate_workers_started") == 0
        and scope.get("production_cases_materialized") == 0
        and scope.get("guard_read") is False
        and scope.get("guard_created") is False,
        "the independent adapter audit accessed nonpublic data or started a candidate",
    )


def _load_public_module(name: str, path: Path, *, expected_sha256: str) -> Any:
    ensure_candidate_free()
    _data, digest = bounded_file(path, maximum=MAX_SOURCE_BYTES)
    require(digest == expected_sha256, f"the pinned public source changed: {name}")
    root = str(ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)
    try:
        module = importlib.import_module(name)
    except (ImportError, OSError, RuntimeError, ValueError) as error:
        raise SmokeError(f"the pinned public controller could not be imported: {name}") from error
    require(
        getattr(module, "__name__", None) == name
        and Path(getattr(module, "__file__", "")).resolve() == path.resolve(),
        f"the pinned public controller was substituted: {name}",
    )
    _verified, after = bounded_file(path, maximum=MAX_SOURCE_BYTES)
    require(after == digest, f"the pinned public controller changed while being imported: {name}")
    ensure_candidate_free()
    return module


def _expected_operations(stratum_index: int) -> tuple[str, ...]:
    require(type(stratum_index) is int and 0 <= stratum_index < STRATUM_COUNT, "public smoke stratum index is invalid")
    return COMPILED_OPERATIONS if stratum_index & 1 else MODULE_OPERATIONS


def iter_public_cases(generator: Any, adapter: Any):
    """One fixed-key case for every compatible family, stratum, and operation."""

    require(
        getattr(generator, "FAMILY_COUNT", None) == FAMILY_COUNT
        and getattr(generator, "STRATUM_COUNT", None) == STRATUM_COUNT
        and getattr(generator, "VARIANTS_PER_STRATUM", None) == VARIANT_COUNT
        and getattr(generator, "CASE_SCHEMA", None) == CASE_SCHEMA,
        "the frozen public fixed-key generator changed its case matrix",
    )
    published_families = getattr(generator, "FAMILIES", None)
    require(
        isinstance(published_families, tuple)
        and tuple(item.name for item in published_families) == SEMANTIC_FAMILIES,
        "the public fixed-key generator changed its 16 semantic families",
    )
    for family_index, family_name in enumerate(SEMANTIC_FAMILIES):
        for stratum_index in range(STRATUM_COUNT):
            operations = _expected_operations(stratum_index)
            selected: dict[str, dict[str, Any]] = {}
            for variant in range(VARIANT_COUNT):
                case = generator.fresh_case(
                    FIXED_NONPRODUCTION_KEY,
                    family_index,
                    stratum_index,
                    variant,
                )
                operation = case.get("operation")
                if operation in operations and operation not in selected:
                    require(
                        case.get("family") == family_name
                        and case.get("family_index") == family_index
                        and isinstance(case.get("stratum"), Mapping)
                        and case["stratum"].get("index") == stratum_index
                        and case.get("variant") == variant,
                        "the fixed-key public smoke generator substituted a case",
                    )
                    adapter.private_case_descriptor(case)
                    selected[operation] = case
                    if len(selected) == len(operations):
                        break
            require(
                set(selected) == set(operations),
                f"the public fixed key did not cover every operation: {family_name}/{stratum_index}",
            )
            for operation in operations:
                yield selected[operation]


def verify_worker_source(worker: Any) -> None:
    evidence = worker.source_provenance
    require(
        isinstance(evidence, Mapping)
        and evidence.get("schema") == ADAPTER_SCHEMA + "-guarded-source"
        and evidence.get("base_source_sha256") == BASE_WORKER_SOURCE_SHA256
        and evidence.get("derived_source_sha256") == DERIVED_WORKER_SOURCE_SHA256
        and evidence.get("extension_sha256") == WORKER_EXTENSION_SHA256
        and evidence.get("audit_source_path")
        == "tools/postfinal_no_delegation_audit_v1.py"
        and evidence.get("audit_source_sha256") == STRICT_SOURCE_SHA256
        and evidence.get("anchor_counts") == EXPECTED_ANCHORS
        and evidence.get("channel_names") == list(CHANNELS)
        and evidence.get("unchanged_original_guard_restores_exactly") is True,
        "the running fixed-public worker changed its independently audited guard",
    )


def verify_worker_mapping(response: Mapping[str, Any], family: str, *, force_hash: bool) -> None:
    require(
        isinstance(response, Mapping)
        and response.get("passed") is True
        and response.get("family") == family,
        "a public isolated smoke worker failed its independent mapping",
    )
    mapping = response.get("native_mapping_provenance")
    require(
        isinstance(mapping, Mapping)
        and mapping.get("passed") is True
        and mapping.get("force_hash") is force_hash
        and mapping.get("digest_cache_key") == "device,inode,size,mtime_ns,ctime_ns",
        "a public smoke worker omitted its exact owned native mapping",
    )
    expected = {"re": 0, "rust": 2, "vm": 1, "zig": 2}[family]
    records = mapping.get("observed_owned_mappings")
    require(
        isinstance(records, list)
        and len(records) == expected
        and mapping.get("expected_owned_mapping_count") == expected
        and mapping.get("observed_owned_mapping_count") == expected
        and all(
            isinstance(item, Mapping)
            and valid_sha256(item.get("sha256"))
            and item.get("matches_static_elf") is True
            and type(item.get("mapping_count")) is int
            and item["mapping_count"] > 0
            and (not force_hash or item.get("content_sha256_recomputed") is True)
            for item in records
        ),
        "an isolated public smoke worker mapped an omitted or unaudited engine",
    )


def compare_snapshot(
    adapter: Any,
    baseline: Mapping[str, Any],
    observed: Mapping[str, Any],
    *,
    case: Mapping[str, Any],
    family: str,
) -> int:
    expected = adapter.validate_channel_digests(baseline.get("channel_digests"))
    actual = adapter.validate_channel_digests(observed.get("channel_digests"))
    require(
        baseline.get("case") == case["id"]
        and observed.get("case") == case["id"]
        and baseline.get("family") == "re"
        and observed.get("family") == family
        and baseline.get("channel_count") == len(CHANNELS)
        and observed.get("channel_count") == len(CHANNELS),
        "the isolated public smoke substituted its case or correctness denominator",
    )
    for lane in CHANNELS:
        if actual[lane] != expected[lane]:
            raise SmokeMismatch(
                "a fixed public case disagrees with isolated CPython: "
                + str(case["id"])
                + "/"
                + family
                + "/"
                + lane,
                {
                    "case": case["id"],
                    "semantic_family": case["family"],
                    "stratum": case["stratum"]["index"],
                    "operation": case["operation"],
                    "candidate": family,
                    "channel": lane,
                    "baseline_digest": expected[lane],
                    "candidate_digest": actual[lane],
                    "fixture_domain": FIXTURE_DOMAIN,
                },
            )
    return len(CHANNELS)


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0)
    descriptor = os.open(path, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def write_public_report(document: Mapping[str, Any], path: Path) -> str:
    require(
        isinstance(path, Path)
        and path.resolve() == OUTPUT_PATH.resolve()
        and path.parent.resolve() == (ROOT / "candidates" / "audits").resolve()
        and not path.is_symlink(),
        "only the exact additive public smoke proof is authorized",
    )
    require(
        document.get("schema") == SCHEMA
        and document.get("status") == "PASS"
        and document.get("passed") is True,
        "refusing to write incomplete or failing fixed-public smoke evidence",
    )
    payload = canonical(dict(document)) + b"\n"
    require(len(payload) <= MAX_DOCUMENT_BYTES, "the public smoke evidence exceeds its bound")
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_CLOEXEC", 0)
    )
    try:
        descriptor = os.open(path, flags, 0o644)
    except FileExistsError as error:
        raise SmokeError("refusing to overwrite an existing public fixed-key smoke proof") from error
    except OSError as error:
        raise SmokeError("the exact additive public smoke proof could not be created") from error
    try:
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            require(written > 0, "the exclusive public smoke proof made no progress")
            view = view[written:]
        os.fsync(descriptor)
        _fsync_directory(path.parent)
    except OSError as error:
        raise SmokeError("the exclusive public smoke proof could not be durably completed") from error
    finally:
        os.close(descriptor)
    return hashlib.sha256(payload).hexdigest()


def run_smoke(*, output: Path = OUTPUT_PATH) -> dict[str, Any]:
    """Run only explicitly authorized, fixed-public, untimed worker checks."""

    ensure_candidate_free()
    verify_pinned_runtime()
    require(output.resolve() == OUTPUT_PATH.resolve(), "public smoke output path is not canonical")
    require(not output.exists(), "refusing to overwrite an existing fixed-public smoke proof")

    base, base_digest = public_document(BASE_AUDIT_PATH)
    verify_base_audit(base)
    strict, strict_digest = public_document(STRICT_AUDIT_PATH)
    native_fingerprints = verify_strict_audit(strict, base_audit_sha256=base_digest)
    adapter_audit, adapter_audit_digest = public_document(ADAPTER_AUDIT_PATH)
    verify_adapter_audit(
        adapter_audit,
        native_fingerprints=native_fingerprints,
        base_audit_sha256=base_digest,
        strict_audit_sha256=strict_digest,
    )
    oracle, oracle_digest = public_document(UNIVERSAL_ORACLE_PATH)
    verify_universal_oracle(
        oracle,
        base_audit_sha256=base_digest,
        native_fingerprints=native_fingerprints,
    )

    _source, source_digest = bounded_file(SOURCE_PATH, maximum=MAX_SOURCE_BYTES)
    _fresh, fresh_digest = bounded_file(FRESH_SOURCE_PATH, maximum=MAX_SOURCE_BYTES)
    adapter = _load_public_module(
        "tools.postfinal_fresh_holdout_adapter_v1",
        ADAPTER_SOURCE_PATH,
        expected_sha256=ADAPTER_SOURCE_SHA256,
    )
    require(
        adapter.ADAPTER_SCHEMA == ADAPTER_SCHEMA
        and adapter.AUDIT_SCHEMA == ADAPTER_DECLARED_AUDIT_SCHEMA
        and tuple(adapter.CHANNELS) == CHANNELS
        and tuple(adapter.FAMILIES) == PARTICIPANTS
        and tuple(adapter.CANDIDATE_FAMILIES) == CANDIDATES
        and adapter.GUARDED_AUDIT_SOURCE_SHA256 == STRICT_SOURCE_SHA256,
        "the public adapter changed its four guarded workers or correctness channels",
    )
    generator = _load_public_module(
        "tools.postfinal_fresh_holdout_v1",
        FRESH_SOURCE_PATH,
        expected_sha256=fresh_digest,
    )
    audit_module = _load_public_module(
        "tools.postfinal_no_delegation_audit_v1",
        STRICT_SOURCE_PATH,
        expected_sha256=STRICT_SOURCE_SHA256,
    )
    ensure_candidate_free()

    workers: dict[str, Any] = {}
    family_counts: collections.Counter[str] = collections.Counter()
    stratum_counts: collections.Counter[str] = collections.Counter()
    operation_counts: collections.Counter[str] = collections.Counter()
    input_counts: collections.Counter[str] = collections.Counter()
    case_digest = hashlib.sha256()
    comparisons = 0
    snapshots = 0
    runtime_guard_checks = 0
    cleanup_errors: list[str] = []
    try:
        for family in PARTICIPANTS:
            worker = adapter.PersistentFreshHoldoutWorker(
                audit_module,
                family,
                native_fingerprints,
            )
            workers[family] = worker
            verify_worker_source(worker)
            runtime_guard_checks += 1

        for case in iter_public_cases(generator, adapter):
            case_digest.update(canonical(case) + b"\n")
            family_counts[case["family"]] += 1
            stratum_counts[str(case["stratum"]["index"])] += 1
            operation_counts[case["operation"]] += 1
            input_counts[case["subject"]["kind"]] += 1

            for family in PARTICIPANTS:
                preparation = workers[family].prepare(case)
                verify_worker_mapping(preparation, family, force_hash=False)
                runtime_guard_checks += 1

            reference = workers["re"].snapshot(case["id"])
            snapshots += 1
            for family in CANDIDATES:
                observed = workers[family].snapshot(case["id"])
                snapshots += 1
                try:
                    comparisons += compare_snapshot(
                        adapter,
                        reference,
                        observed,
                        case=case,
                        family=family,
                    )
                except SmokeMismatch as error:
                    expected_detail = workers["re"].snapshot(case["id"], reveal=True)
                    candidate_detail = workers[family].snapshot(case["id"], reveal=True)
                    error.details["baseline_channels"] = expected_detail["channels"]
                    error.details["candidate_channels"] = candidate_detail["channels"]
                    raise

            for family in PARTICIPANTS:
                mapping = workers[family].verify(force_hash=False)
                verify_worker_mapping(mapping, family, force_hash=False)
                runtime_guard_checks += 1

        for family in PARTICIPANTS:
            mapping = workers[family].verify(force_hash=True)
            verify_worker_mapping(mapping, family, force_hash=True)
            runtime_guard_checks += 1
        ensure_candidate_free()
    finally:
        for family in reversed(PARTICIPANTS):
            worker = workers.get(family)
            if worker is None:
                continue
            try:
                worker.close()
            except BaseException as error:
                cleanup_errors.append(f"{family}: {type(error).__name__}: {error}")

    require(not cleanup_errors, "an isolated fixed-public worker did not close cleanly")
    require(sum(family_counts.values()) == EXPECTED_CASES, "the public fixed-key case denominator changed")
    require(set(family_counts) == set(SEMANTIC_FAMILIES), "fixed-public smoke omitted a semantic family")
    require(
        all(family_counts[name] == 136 for name in SEMANTIC_FAMILIES),
        "fixed-public smoke changed a semantic-family denominator",
    )
    require(
        set(stratum_counts) == {str(index) for index in range(STRATUM_COUNT)}
        and all(
            stratum_counts[str(index)] == FAMILY_COUNT * len(_expected_operations(index))
            for index in range(STRATUM_COUNT)
        ),
        "fixed-public smoke omitted or reweighted an input stratum",
    )
    require(
        operation_counts
        == collections.Counter(
            {
                **{name: FAMILY_COUNT * STRATUM_COUNT for name in MODULE_OPERATIONS},
                "scanner": FAMILY_COUNT * (STRATUM_COUNT // 2),
            }
        ),
        "fixed-public smoke omitted or silently reweighted a public API",
    )
    require(
        set(input_counts) == {"str", "bytes", "bytearray", "memoryview"},
        "fixed-public smoke omitted a required Python text or bytes-like input",
    )
    require(snapshots == EXPECTED_SNAPSHOTS, "an isolated fixed-public worker snapshot was omitted")
    require(comparisons == EXPECTED_COMPARISONS, "an independently reconstructed correctness lane was omitted")
    require(runtime_guard_checks == EXPECTED_RUNTIME_GUARD_CHECKS, "a before/after actual native mapping verification was omitted")

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "source_path": "tools/postfinal_fresh_holdout_adapter_smoke_v1.py",
        "source_sha256": source_digest,
        "generator_source_path": "tools/postfinal_fresh_holdout_v1.py",
        "generator_source_sha256": fresh_digest,
        "adapter_source_path": "tools/postfinal_fresh_holdout_adapter_v1.py",
        "adapter_source_sha256": ADAPTER_SOURCE_SHA256,
        "strict_guard_source_path": "tools/postfinal_no_delegation_audit_v1.py",
        "strict_guard_source_sha256": STRICT_SOURCE_SHA256,
        "base_audit_path": "candidates/audits/FROM-SCRATCH-AUDIT.json",
        "base_audit_sha256": base_digest,
        "strict_audit_path": "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V1.json",
        "strict_audit_sha256": strict_digest,
        "adapter_audit_path": "candidates/audits/POSTFINAL-FRESH-HOLDOUT-ADAPTER-AUDIT-V2.json",
        "adapter_audit_sha256": adapter_audit_digest,
        "universal_public_oracle_path": "candidates/evidence/python-re-universal-public-oracle-v3-all.json",
        "universal_public_oracle_sha256": oracle_digest,
        "base_worker_source_sha256": BASE_WORKER_SOURCE_SHA256,
        "derived_worker_source_sha256": DERIVED_WORKER_SOURCE_SHA256,
        "worker_extension_sha256": WORKER_EXTENSION_SHA256,
        "worker_anchor_counts": dict(EXPECTED_ANCHORS),
        "native_elf_fingerprints": dict(sorted(native_fingerprints.items())),
        "fixture_domain": FIXTURE_DOMAIN,
        "fixed_key_source": FIXED_KEY_LABEL,
        "fixed_key_sha256": hashlib.sha256(FIXED_NONPRODUCTION_KEY).hexdigest(),
        "production_entropy_drawn": False,
        "production_cases_materialized": 0,
        "historical_holdout_accessed": False,
        "guard_accessed": False,
        "benchmark_or_timing_executed": False,
        "observe_calls": 0,
        "controller_candidate_imported": False,
        "worker_families": list(PARTICIPANTS),
        "persistent_isolated_worker_count": len(PARTICIPANTS),
        "correctness_channels": list(CHANNELS),
        "cases": EXPECTED_CASES,
        "fixed_public_case_sha256": case_digest.hexdigest(),
        "semantic_families": dict(sorted(family_counts.items())),
        "strata": dict(sorted(stratum_counts.items(), key=lambda item: int(item[0]))),
        "operations": dict(sorted(operation_counts.items())),
        "input_representations": dict(sorted(input_counts.items())),
        "worker_snapshots": snapshots,
        "independent_channel_comparisons": comparisons,
        "runtime_guard_checks": runtime_guard_checks,
        "forced_native_hash_boundaries": 2 * len(PARTICIPANTS),
        "failed": 0,
        "mismatches": [],
        "limitations": [
            "Every case is public and deterministically derives from bytes(range(32)); none is a production holdout case.",
            "This report validates four independent observable channels without performing or reporting a timing.",
            "Matching independently audited source and binary hashes establish identity, not a hermetic or reproducible native build.",
        ],
    }
    evidence_digest = write_public_report(report, output)
    ensure_candidate_free()
    return {
        "schema": SCHEMA,
        "status": "PASS",
        "passed": True,
        "report": "candidates/audits/POSTFINAL-FRESH-HOLDOUT-ADAPTER-SMOKE-V2.json",
        "report_sha256": evidence_digest,
        "fixture_domain": FIXTURE_DOMAIN,
        "cases": EXPECTED_CASES,
        "semantic_family_count": FAMILY_COUNT,
        "stratum_count": STRATUM_COUNT,
        "operation_count": len(COMPILED_OPERATIONS),
        "isolated_worker_count": len(PARTICIPANTS),
        "worker_snapshots": snapshots,
        "independent_channel_comparisons": comparisons,
        "runtime_guard_checks": runtime_guard_checks,
        "candidate_imported": False,
        "production_entropy_drawn": False,
        "production_cases_materialized": 0,
        "historical_holdout_accessed": False,
        "guard_accessed": False,
        "benchmark_or_timing_executed": False,
    }


def _synthetic_base_document() -> dict[str, Any]:
    checks = [
        {"name": f"public-base-control-{index:02d}", "passed": True}
        for index in range(76)
    ]
    return {
        "schema_version": 1,
        "audit": "bounded-from-scratch-engine-provenance",
        "passed": True,
        "result": "PASS",
        "self_test": {"passed": True, "check_count": 76, "failed": [], "checks": checks},
        "native_elf_provenance": {
            "passed": True,
            "audited_binary_count": 5,
            "expected_binary_count": 5,
        },
        "runtime_native_mapping_provenance": {"passed": True},
        "scope": {
            "holdout_or_case_fixture_access": False,
            "benchmark_or_timing_executed": False,
        },
        "families": {
            name: {"passed": True} for name in ("ast", "rust", "vm", "zig")
        },
    }


def _synthetic_strict_document(base_digest: str) -> dict[str, Any]:
    checks = [
        {"name": f"public-strict-control-{index:02d}", "passed": True}
        for index in range(32)
    ]
    return {
        "schema": STRICT_AUDIT_SCHEMA,
        "passed": True,
        "result": "PASS",
        "audit_source_path": "tools/postfinal_no_delegation_audit_v1.py",
        "audit_source_sha256": STRICT_SOURCE_SHA256,
        "base_audit_report_path": "candidates/audits/FROM-SCRATCH-AUDIT.json",
        "base_audit_report_sha256": base_digest,
        "inherited_control_count": 76,
        "self_test": {"passed": True, "check_count": 32, "failed": [], "checks": checks},
        "source_graph_provenance": {
            "passed": True,
            "implicit_rust_build_script_present": False,
            "zig_build_manifest_present": False,
        },
        "native_elf_provenance": {
            "passed": True,
            "audited_binary_count": 5,
            "expected_binary_count": 5,
        },
        "scope": {
            "holdout_or_case_fixture_access": False,
            "benchmark_or_timing_executed": False,
            "closed_owned_source_graph": True,
            "persistent_measurement_worker_available": True,
            "mapped_binaries_hashed_against_static_elf": True,
        },
        "native_elf_fingerprints": {
            key: hashlib.sha256(key.encode("ascii")).hexdigest()
            for key in sorted(EXPECTED_NATIVE_KEYS)
        },
    }


def _synthetic_adapter_document(
    native: Mapping[str, str],
    *,
    base_audit_sha256: str,
    strict_audit_sha256: str,
) -> dict[str, Any]:
    checks = [
        {"name": f"public-adapter-control-{index:02d}", "passed": True}
        for index in range(63)
    ]
    return {
        "schema": ADAPTER_AUDIT_SCHEMA,
        "result": "PASS",
        "status": "PASS",
        "passed": True,
        "audit_source_path": "tools/postfinal_fresh_holdout_adapter_audit_v1.py",
        "audit_source_sha256": ADAPTER_AUDIT_SOURCE_SHA256,
        "adapter_source_path": "tools/postfinal_fresh_holdout_adapter_v1.py",
        "adapter_source_sha256": ADAPTER_SOURCE_SHA256,
        "adapter_declared_audit_schema": ADAPTER_DECLARED_AUDIT_SCHEMA,
        "guard_source_path": "tools/postfinal_no_delegation_audit_v1.py",
        "guard_source_sha256": STRICT_SOURCE_SHA256,
        "bootstrap_source_path": "tools/postfinal_fresh_holdout_bootstrap_v1.c",
        "bootstrap_source_sha256": BOOTSTRAP_SOURCE_SHA256,
        "base_worker_source_sha256": BASE_WORKER_SOURCE_SHA256,
        "derived_worker_source_sha256": DERIVED_WORKER_SOURCE_SHA256,
        "worker_extension_sha256": WORKER_EXTENSION_SHA256,
        "worker_anchor_counts": dict(EXPECTED_ANCHORS),
        "channel_names": list(CHANNELS),
        "inherited_control_count": 76,
        "original_no_delegation_control_count": 32,
        "native_elf_fingerprints": dict(native),
        "native_elf_provenance": {
            "passed": True,
            "audited_binary_count": 5,
            "expected_binary_count": 5,
            "base_audit_report_sha256": base_audit_sha256,
            "postfinal_no_delegation_audit_path": str(STRICT_AUDIT_PATH),
            "postfinal_no_delegation_audit_sha256": strict_audit_sha256,
            "postfinal_no_delegation_audit_source_sha256": STRICT_SOURCE_SHA256,
            "postfinal_no_delegation_control_count": 32,
            "inherited_control_count": 76,
        },
        "self_test": {
            "passed": True,
            "check_count": 63,
            "failed": [],
            "checks": checks,
        },
        "scope": {
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
            "candidate_workers_started": 0,
            "production_cases_materialized": 0,
            "guard_read": False,
            "guard_created": False,
        },
    }


def candidate_free_self_test() -> dict[str, Any]:
    """Validate fixed-public arithmetic and poisoned evidence only in memory."""

    ensure_candidate_free()
    checks: list[dict[str, Any]] = []

    def check(name: str, value: bool) -> None:
        checks.append({"name": name, "passed": bool(value)})

    def rejected(name: str, action: Any) -> None:
        try:
            action()
        except (SmokeError, OverflowError, TypeError, ValueError):
            check(name, True)
        else:
            check(name, False)

    check("explicit-public-fixed-nonproduction-key", FIXED_NONPRODUCTION_KEY == bytes(range(32)))
    check("fixed-public-domain-is-explicit", FIXTURE_DOMAIN.endswith("/public-fixed-key-smoke/v1"))
    check("exact-sixteen-independent-semantic-families", len(SEMANTIC_FAMILIES) == 16 and len(set(SEMANTIC_FAMILIES)) == 16)
    check("exact-sixteen-input-strata", STRATUM_COUNT == 16)
    check("exact-nine-public-operations", len(COMPILED_OPERATIONS) == 9 and len(set(COMPILED_OPERATIONS)) == 9)
    check("module-never-requests-a-scanner", "scanner" not in MODULE_OPERATIONS)
    check("compiled-public-cases-include-scanner", COMPILED_OPERATIONS[-1] == "scanner")
    check("exact-2176-public-fixed-key-cases", EXPECTED_CASES == 2_176)
    check("exact-8704-four-worker-snapshots", EXPECTED_SNAPSHOTS == 8_704)
    check("exact-26112-four-lane-candidate-comparisons", EXPECTED_COMPARISONS == 26_112)
    check("exact-17416-before-after-native-mapping-checks", EXPECTED_RUNTIME_GUARD_CHECKS == 17_416)
    check("exact-four-distinct-public-lanes", len(CHANNELS) == 4 and len(set(CHANNELS)) == 4)
    check("exact-four-independent-process-families", PARTICIPANTS == ("re", "rust", "vm", "zig"))
    check("exact-five-owned-native-roles", len(EXPECTED_NATIVE_KEYS) == 5)
    check("fixed-audit-and-worker-hashes-are-sha256", all(valid_sha256(item) for item in (ADAPTER_SOURCE_SHA256, STRICT_SOURCE_SHA256, ADAPTER_AUDIT_SOURCE_SHA256, BOOTSTRAP_SOURCE_SHA256, BASE_WORKER_SOURCE_SHA256, DERIVED_WORKER_SOURCE_SHA256, WORKER_EXTENSION_SHA256, ORACLE_SOURCE_SHA256)))

    surrogate = "\ud800\n\udfff"
    encoded = canonical({"surrogate": surrogate})
    check("public-frame-is-ascii", encoded.isascii())
    check("public-frame-preserves-lone-surrogates", json.loads(encoded)["surrogate"] == surrogate)
    check("public-frame-has-no-unescaped-newline", b"\n" not in encoded)
    rejected("reject-nonfinite-public-evidence", lambda: canonical({"poison": float("nan")}))

    expected_operations: collections.Counter[str] = collections.Counter()
    synthetic_cases: set[tuple[int, int, str]] = set()
    for family in range(FAMILY_COUNT):
        for stratum in range(STRATUM_COUNT):
            for operation in _expected_operations(stratum):
                synthetic_cases.add((family, stratum, operation))
                expected_operations[operation] += 1
    check("synthetic-matrix-has-no-duplicate-family-stratum-operation", len(synthetic_cases) == EXPECTED_CASES)
    check("each-nonscanner-api-is-tested-256-times", all(expected_operations[name] == 256 for name in MODULE_OPERATIONS))
    check("compiled-scanner-is-tested-128-times", expected_operations["scanner"] == 128)
    check("all-even-module-strata-have-eight-operations", all(len(_expected_operations(index)) == 8 for index in range(0, 16, 2)))
    check("all-odd-compiled-strata-have-nine-operations", all(len(_expected_operations(index)) == 9 for index in range(1, 16, 2)))
    rejected("reject-out-of-range-public-stratum", lambda: _expected_operations(16))
    rejected("reject-boolean-public-stratum", lambda: _expected_operations(True))

    base = _synthetic_base_document()
    verify_base_audit(base)
    check("accept-source-bound-synthetic-76-control-audit", True)
    base_digest = hashlib.sha256(canonical(base)).hexdigest()
    strict = _synthetic_strict_document(base_digest)
    native = verify_strict_audit(strict, base_audit_sha256=base_digest)
    check("accept-source-bound-synthetic-32-control-audit", set(native) == EXPECTED_NATIVE_KEYS)
    strict_digest = hashlib.sha256(canonical(strict)).hexdigest()
    adapter = _synthetic_adapter_document(
        native,
        base_audit_sha256=base_digest,
        strict_audit_sha256=strict_digest,
    )
    verify_adapter_audit(
        adapter,
        native_fingerprints=native,
        base_audit_sha256=base_digest,
        strict_audit_sha256=strict_digest,
    )
    check("accept-independently-bound-synthetic-adapter-audit", True)

    def clone(value: Any) -> Any:
        return json.loads(canonical(value))

    poisoned_base = clone(base)
    poisoned_base["self_test"]["checks"][0]["passed"] = False
    rejected("reject-poisoned-original-76-control-audit", lambda: verify_base_audit(poisoned_base))
    missing_base = clone(base)
    missing_base["native_elf_provenance"]["audited_binary_count"] = 4
    rejected("reject-missing-original-native-engine", lambda: verify_base_audit(missing_base))
    poisoned_strict = clone(strict)
    poisoned_strict["base_audit_report_sha256"] = "0" * 64
    rejected("reject-substituted-original-audit-digest", lambda: verify_strict_audit(poisoned_strict, base_audit_sha256=base_digest))
    shortened_strict = clone(strict)
    shortened_strict["self_test"]["checks"].pop()
    rejected("reject-omitted-strict-poison-control", lambda: verify_strict_audit(shortened_strict, base_audit_sha256=base_digest))
    external_native = clone(strict)
    external_native["native_elf_fingerprints"]["foreign:regex"] = "0" * 64
    rejected("reject-extra-or-foreign-regex-engine", lambda: verify_strict_audit(external_native, base_audit_sha256=base_digest))
    unsafe_scope = clone(strict)
    unsafe_scope["scope"]["holdout_or_case_fixture_access"] = True
    rejected("reject-audit-with-nonpublic-case-access", lambda: verify_strict_audit(unsafe_scope, base_audit_sha256=base_digest))
    timed_scope = clone(strict)
    timed_scope["scope"]["benchmark_or_timing_executed"] = True
    rejected("reject-audit-that-executed-a-timing", lambda: verify_strict_audit(timed_scope, base_audit_sha256=base_digest))
    changed_adapter = clone(adapter)
    changed_adapter["adapter_source_sha256"] = "0" * 64
    rejected("reject-substituted-fresh-adapter-source", lambda: verify_adapter_audit(changed_adapter, native_fingerprints=native, base_audit_sha256=base_digest, strict_audit_sha256=strict_digest))
    changed_guard = clone(adapter)
    changed_guard["derived_worker_source_sha256"] = "0" * 64
    rejected("reject-substituted-derived-guard-source", lambda: verify_adapter_audit(changed_guard, native_fingerprints=native, base_audit_sha256=base_digest, strict_audit_sha256=strict_digest))
    dropped_lane = clone(adapter)
    dropped_lane["channel_names"].pop()
    rejected("reject-missing-independent-correctness-lane", lambda: verify_adapter_audit(dropped_lane, native_fingerprints=native, base_audit_sha256=base_digest, strict_audit_sha256=strict_digest))
    poisoned_anchor = clone(adapter)
    poisoned_anchor["worker_anchor_counts"]["guarded-fresh-functions"] = 2
    rejected("reject-ambiguous-original-guard-anchor", lambda: verify_adapter_audit(poisoned_anchor, native_fingerprints=native, base_audit_sha256=base_digest, strict_audit_sha256=strict_digest))
    cross_native = clone(adapter)
    cross_native["native_elf_fingerprints"][next(iter(EXPECTED_NATIVE_KEYS))] = "0" * 64
    rejected("reject-cross-audit-native-fingerprint-change", lambda: verify_adapter_audit(cross_native, native_fingerprints=native, base_audit_sha256=base_digest, strict_audit_sha256=strict_digest))

    sample = {
        name: {"lane": name, "surrogate": surrogate}
        for name in CHANNELS
    }
    reference = {
        name: hashlib.sha256(
            LANE_DOMAIN + name.encode("ascii") + b"\x00" + canonical(sample[name])
        ).hexdigest()
        for name in CHANNELS
    }
    check("all-four-correctness-digests-are-domain-separated", len(set(reference.values())) == 4)
    for index, name in enumerate(CHANNELS):
        mutated = dict(sample)
        mutated[name] = {"lane": name, "poison": index}
        actual = {
            label: hashlib.sha256(
                LANE_DOMAIN + label.encode("ascii") + b"\x00" + canonical(mutated[label])
            ).hexdigest()
            for label in CHANNELS
        }
        check(
            "detect-independent-fixed-public-lane-poison:" + name,
            actual[name] != reference[name]
            and all(actual[other] == reference[other] for other in CHANNELS if other != name),
        )

    ensure_candidate_free()
    failed = [item["name"] for item in checks if not item["passed"]]
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS" if not failed else "FAIL",
        "passed": not failed,
        "checks": checks,
        "check_count": len(checks),
        "failed": failed,
        "fixture_domain": FIXTURE_DOMAIN,
        "fixed_key_source": FIXED_KEY_LABEL,
        "synthetic_cases": EXPECTED_CASES,
        "semantic_families": FAMILY_COUNT,
        "strata": STRATUM_COUNT,
        "operations": len(COMPILED_OPERATIONS),
        "isolated_worker_processes_started": 0,
        "candidate_imports": 0,
        "file_reads": 0,
        "file_writes": 0,
        "production_entropy_drawn": False,
        "production_cases_materialized": 0,
        "guard_accessed": False,
        "historical_holdout_accessed": False,
        "benchmark_or_timing_executed": False,
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_mutually_exclusive_group(required=True)
    commands.add_argument(
        "--self-test",
        action="store_true",
        help="run only deterministic, in-memory, candidate-free public controls",
    )
    commands.add_argument(
        "--smoke",
        action="store_true",
        help="explicitly run isolated fixed-public-key comparisons; never time or open a holdout",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_PATH,
        help="the sole exact, exclusively created public smoke proof",
    )
    args = parser.parse_args(arguments)
    try:
        if args.self_test:
            require(
                args.output == OUTPUT_PATH,
                "the in-memory candidate-free self-test cannot select an evidence file",
            )
            result = candidate_free_self_test()
        else:
            result = run_smoke(output=args.output)
    except SmokeMismatch as error:
        result = {
            "schema": SCHEMA,
            "status": "FAIL",
            "passed": False,
            "error": str(error),
            "mismatch": error.details,
            "fixture_domain": FIXTURE_DOMAIN,
            "candidate_imported": False,
            "production_entropy_drawn": False,
            "production_cases_materialized": 0,
            "guard_accessed": False,
            "historical_holdout_accessed": False,
            "benchmark_or_timing_executed": False,
        }
    except (SmokeError, OSError, RuntimeError, TypeError, ValueError) as error:
        result = {
            "schema": SCHEMA if args.smoke else SCHEMA + "-self-test",
            "status": "FAIL",
            "passed": False,
            "error": str(error),
            "fixture_domain": FIXTURE_DOMAIN,
            "candidate_imported": False,
            "production_entropy_drawn": False,
            "production_cases_materialized": 0,
            "guard_accessed": False,
            "historical_holdout_accessed": False,
            "benchmark_or_timing_executed": False,
        }
    sys.stdout.buffer.write(canonical(result) + b"\n")
    return 0 if result.get("passed") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
