#!/usr/bin/env python3
"""Revalidate the unchanged official Python tests against repaired V6 engines."""

from __future__ import annotations

import argparse
import builtins
import copy
from contextlib import contextmanager
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
import time
from typing import Any, Iterator, Mapping


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import postfinal_cpython_locale_oracle_v1 as previous


SCHEMA = "rebar-postfinal-cpython-public-locale-v2"
SOURCE_RELATIVE = "tools/postfinal_cpython_locale_oracle_v2.py"
REPORT_RELATIVE = "oracle/cpython-3.14.6/evidence/postfinal-locale-v2-all.json"
EVIDENCE_PATH = ROOT / REPORT_RELATIVE

V1_SCHEMA = "rebar-postfinal-cpython-public-locale-v1"
V1_SOURCE_RELATIVE = "tools/postfinal_cpython_locale_oracle_v1.py"
V1_SOURCE_SHA256 = (
    "b87bbdcddef2d19a462e8c4b37bd159f6c3a30ea9b4fe5d9471eff1f51fbcb55"
)
V1_REPORT_RELATIVE = "oracle/cpython-3.14.6/evidence/postfinal-locale-v1-all.json"
V1_REPORT_SHA256 = (
    "bc17ee74409543d1b57f3aee65088e990ab21ac83dc75ac46fbd1f97f04b6621"
)

V6_BASE_SOURCE_RELATIVE = "tools/postfinal_from_scratch_audit_v6.py"
V6_BASE_REPORT_RELATIVE = "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V6.json"
V6_BASE_SCHEMA = "rebar-postfinal-from-scratch-audit-v6"
V6_BASE_SOURCE_SHA256: str | None = (
    "77e7ea97f96280019b3be9abfeeb8fc6ff27ca6ecd13189e611586af5719c18f"
)
V6_BASE_REPORT_SHA256: str | None = (
    "0314e3e5de3386d7c9c1e7f8fa4648554ff53cb53e3aafcecc4cb8e4923ddcbb"
)

V6_STRICT_SOURCE_RELATIVE = "tools/postfinal_no_delegation_audit_v6.py"
V6_STRICT_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V6.json"
)
V6_STRICT_SCHEMA = "rebar-postfinal-no-delegation-audit-v6"
# Both values were pinned only after root committed the strict controller,
# actually ran the isolated audit, and exclusively created its real report.
V6_STRICT_SOURCE_SHA256: str | None = (
    "a936abe91d67169ea361b6770404ffe7bc925fdb3275aef854fbe12fe68a8649"
)
V6_STRICT_REPORT_SHA256: str | None = (
    "93f174f0861b0ee6e9feadf6e49bf222f0766b393ff74179219e65452b03d84f"
)

CORE_FAMILIES = ("rust", "vm", "zig")
ALL_FAMILIES = frozenset({"ast", *CORE_FAMILIES})
SOURCE_PATHS = frozenset(previous.SOURCE_PATHS)
NATIVE_PATHS = dict(previous.NATIVE_PATHS)
OWNED_SOURCE_PATHS: dict[str, tuple[str, ...]] = {
    "rust": (
        "candidates/rust_candidate.py",
        "candidates/rust/py_bridge.c",
        "candidates/rust/src/lib.rs",
        "candidates/rust/src/newline.rs",
        "candidates/rust/src/search.rs",
        "candidates/rust/src/stack.rs",
        "candidates/rust/src/unicode_tables.rs",
    ),
    "vm": ("candidates/vm_candidate.py", "candidates/_vm_native.c"),
    "zig": (
        "candidates/zig_candidate.py",
        "candidates/zig/mini_regex.zig",
        "candidates/zig/py_bridge.c",
    ),
}
NATIVE_FILE_ROLES: dict[str, dict[str, str]] = {
    "rust": {
        "bridge": "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "engine": "candidates/_rust_engine.so",
    },
    "vm": {"native": "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so"},
    "zig": {
        "bridge": "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
        "engine": "candidates/_zig_probe.so",
    },
}
OWNED_BRIDGES = {
    "rust": "candidates._rust_bridge",
    "vm": "candidates._vm_native",
    "zig": "candidates._zig_bridge",
}
NATIVE_LOADER_ALIASES = (
    "ctypes.CDLL",
    "ctypes.cdll.LoadLibrary",
    "ctypes.cdll._dlltype",
    "ctypes._dlopen",
    "_ctypes.dlopen",
)
PICKLE_PROTOCOLS = (0, 2, 4, 5)
REQUIRED_CORPUS_METHOD = "ExternalTests.test_re_tests"


class LocaleV2Error(AssertionError):
    """A current four-role official compatibility proof is unsafe."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise LocaleV2Error(message)


def _candidate_modules() -> tuple[str, ...]:
    return tuple(sorted(
        name for name, module in sys.modules.items()
        if module is not None and (name == "candidates" or name.startswith("candidates."))
    ))


def _destination(value: Any) -> str:
    require(isinstance(value, str), "the official output path must be text")
    parsed = PurePosixPath(value)
    require(
        not parsed.is_absolute()
        and ".." not in parsed.parts
        and "\\" not in value
        and "\x00" not in value
        and str(parsed) == value
        and value == REPORT_RELATIVE,
        "only the new exclusive version-two official evidence is permitted",
    )
    return value


def _pin_values(overrides: Mapping[str, Any] | None = None) -> dict[str, str]:
    actual: Mapping[str, Any]
    if overrides is None:
        actual = {
            "base_source": V6_BASE_SOURCE_SHA256,
            "base_report": V6_BASE_REPORT_SHA256,
            "strict_source": V6_STRICT_SOURCE_SHA256,
            "strict_report": V6_STRICT_REPORT_SHA256,
        }
    else:
        actual = overrides
    require(
        isinstance(actual, Mapping)
        and set(actual) == {
            "base_source", "base_report", "strict_source", "strict_report"
        }
        and all(previous.is_sha256(value) for value in actual.values())
        and len(set(actual.values())) == 4,
        "all four genuine version-six source and report hashes must be pinned",
    )
    return {key: str(value) for key, value in actual.items()}


def _validate_guard(document: Any, family: str) -> None:
    require(isinstance(document, dict), "the native family guard is missing")
    require(document.get("family") == family, "the native guard selects another family")
    for name in (
        "enabled", "stdlib_re_blocked", "cpython_sre_blocked",
        "third_party_regex_blocked", "cross_family_blocked",
        "foreign_dynamic_libraries_blocked",
    ):
        require(document.get(name) is True, "the audited native guard weakened: " + name)
    require(
        document.get("native_loader_aliases_blocked") == list(NATIVE_LOADER_ALIASES),
        "the audited native guard omitted or reordered a real native loader",
    )


def _base_graph(document: Mapping[str, Any]) -> tuple[dict[str, str], dict[str, str], dict[str, dict[str, str]]]:
    families = document.get("families")
    native = document.get("native_elf_provenance")
    manifest = document.get("manifest_provenance")
    runtime = document.get("runtime_native_mapping_provenance")
    require(
        isinstance(families, dict)
        and set(families) == ALL_FAMILIES
        and isinstance(native, dict)
        and native.get("passed") is True
        and native.get("audited_binary_count") == 5
        and native.get("expected_binary_count") == 5
        and isinstance(native.get("families"), dict)
        and set(native["families"]) == set(CORE_FAMILIES)
        and isinstance(manifest, dict)
        and manifest.get("passed") is True
        and manifest.get("issues") == []
        and manifest.get("python_dependencies") == []
        and manifest.get("rust_third_party_dependency_count") == 0
        and manifest.get("rust_lock_packages") == ["rebar-rust-continuation"]
        and isinstance(runtime, dict)
        and runtime.get("passed") is True,
        "the audited source graph, independent engines, or native provenance changed",
    )
    sources: dict[str, str] = {}
    flat_native: dict[str, str] = {}
    native_by_family: dict[str, dict[str, str]] = {}
    for family in CORE_FAMILIES:
        item = families[family]
        require(
            isinstance(item, dict)
            and item.get("passed") is True
            and isinstance(item.get("owned_pipeline"), dict)
            and item["owned_pipeline"].get("passed") is True
            and item["owned_pipeline"].get("issues") == [],
            "an independently implemented engine is unqualified: " + family,
        )
        python_source = item.get("python_source")
        native_sources = item.get("native_sources")
        require(isinstance(python_source, dict) and isinstance(native_sources, list),
                "an owned candidate source was omitted: " + family)
        actual_sources = [python_source, *native_sources]
        require(
            len(actual_sources) == len(OWNED_SOURCE_PATHS[family])
            and all(isinstance(source, dict) for source in actual_sources)
            and {source.get("file") for source in actual_sources}
            == set(OWNED_SOURCE_PATHS[family]),
            "an owned parser, compiler, bridge, or matching source was substituted: " + family,
        )
        for source in actual_sources:
            require(
                source.get("passed") is True
                and source.get("issues") == []
                and previous.is_sha256(source.get("sha256")),
                "a candidate source did not genuinely pass its source audit",
            )
            require(source["file"] not in sources, "a candidate source was counted twice")
            sources[source["file"]] = source["sha256"]

        entries = native["families"][family].get("files")
        require(
            isinstance(entries, dict)
            and set(entries) == set(NATIVE_FILE_ROLES[family]),
            "an audited native bridge or matcher was omitted: " + family,
        )
        native_by_family[family] = {}
        for native_role, relative in NATIVE_FILE_ROLES[family].items():
            entry = entries[native_role]
            runpaths = ["$ORIGIN"] if native_role == "bridge" else []
            require(
                isinstance(entry, dict)
                and entry.get("file") == relative
                and previous.is_sha256(entry.get("sha256"))
                and entry.get("elf_class") == 64
                and entry.get("forbidden_regex_symbols") == []
                and entry.get("cross_candidate_symbols") == []
                and entry.get("runpaths") == runpaths
                and isinstance(entry.get("needed"), list),
                "an owned native matcher, dependency, or bridge changed: " + relative,
            )
            native_by_family[family][relative] = entry["sha256"]
            matches = [role for role, candidate in NATIVE_PATHS.items() if candidate == relative]
            require(len(matches) == 1, "a native binary has no unique public family role")
            flat_native[matches[0]] = entry["sha256"]
    require(set(sources) == SOURCE_PATHS and len(sources) == 12,
            "the audit does not establish the exact twelve owned candidate sources")
    require(set(flat_native) == set(NATIVE_PATHS) and len(flat_native) == 5,
            "the audit does not establish the exact five owned native binaries")
    require(
        document.get("verified_candidate_source_count") == 12
        and set(document.get("verified_candidate_source_paths", ())) == SOURCE_PATHS
        and document.get("verified_native_role_count") == 5
        and document.get("native_sha256_by_family") == native_by_family,
        "the version-six source audit concealed its complete source or native mapping",
    )
    return sources, flat_native, native_by_family


def _validate_ownership(source: Mapping[str, Any], strict: Mapping[str, Any],
                        natives: Mapping[str, dict[str, str]]) -> None:
    base_owners = source.get("public_type_ownership")
    strict_owners = strict.get("public_type_ownership")
    require(
        isinstance(base_owners, dict)
        and isinstance(strict_owners, dict)
        and set(base_owners) == set(CORE_FAMILIES)
        and set(strict_owners) == set(CORE_FAMILIES)
        and source.get("standard_pickle_checks") == 48
        and source.get("standard_pickle_checks_per_family") == 16
        and strict.get("verified_standard_pickle_count") == 48
        and strict.get("verified_public_type_family_count") == 3,
        "the independent audits omitted real native type and pickle ownership",
    )
    for family in CORE_FAMILIES:
        candidate = "candidates." + family + "_candidate"
        expected_rows = [
            (origin, argument, protocol)
            for origin in ("Pattern", "Match")
            for argument in ("str", "bytes")
            for protocol in PICKLE_PROTOCOLS
        ]
        base = base_owners[family]
        isolated = strict_owners[family]
        require(
            isinstance(base, dict)
            and base.get("schema") == V6_BASE_SCHEMA + "-owned-types"
            and base.get("status") == "PASS"
            and base.get("result") == "PASS"
            and base.get("passed") is True
            and base.get("family") == family
            and base.get("candidate_module") == candidate
            and base.get("native_bridge_module") == OWNED_BRIDGES[family]
            and base.get("native_sha256") == natives[family]
            and base.get("standard_pickle_checks") == 16
            and base.get("candidate_regex_matching_executed") is False
            and base.get("third_party_regex_packages") == 0
            and base.get("benchmark_or_timing_executed") is False
            and base.get("fixture_accessed") is False,
            "the source audit accepted a foreign public type: " + family,
        )
        base_types = base.get("public_types")
        require(isinstance(base_types, dict) and set(base_types) == {"Pattern", "Match"},
                "the source audit omitted an actual pattern or match type")
        for name in ("Pattern", "Match"):
            item = base_types[name]
            expected_module = candidate if name == "Pattern" else OWNED_BRIDGES[family]
            require(
                isinstance(item, dict)
                and item.get("module") == expected_module
                and item.get("name") == name
                and item.get("qualified_name") == name
                and item.get("native_bridge_module") == OWNED_BRIDGES[family]
                and item.get("candidate_identity") is True
                and item.get("native_bridge_identity") is (name == "Match")
                and item.get("genuinely_importable") is True,
                "a public native type claims foreign or unimportable ownership",
            )
        records = base.get("records")
        require(
            isinstance(records, list)
            and len(records) == 16
            and all(isinstance(row, dict) for row in records)
            and [(row.get("origin"), row.get("argument"), row.get("protocol"))
                 for row in records] == expected_rows
            and all(
                row.get("passed") is True
                and row.get("genuine_generic_alias") is True
                and row.get("same_owned_native_origin") is True
                and row.get("standard_pickle_round_trip") is True
                for row in records
            ),
            "the source audit omitted or counterfeited an ordinary pickle round trip",
        )
        _validate_guard(base.get("guard"), family)
        require(
            isinstance(isolated, dict)
            and isolated.get("schema")
            == "rebar-postfinal-no-delegation-public-owner-worker-v6"
            and isolated.get("status") == "PASS"
            and isolated.get("role") == family
            and isolated.get("standard_pickle_check_count") == 16
            and isolated.get("native_binary_sha256") == natives[family]
            and isolated.get("cached_json_decoder_regex_blocked") is True
            and isolated.get("benchmark_or_timing_executed") is False
            and isolated.get("holdout_or_case_fixture_access") is False,
            "the no-delegation audit omitted an isolated genuine owner: " + family,
        )
        isolated_types = isolated.get("public_type_ownership")
        require(isinstance(isolated_types, dict)
                and set(isolated_types) == {"Pattern", "Match"},
                "the strict audit omitted a genuine public class")
        for name in ("Pattern", "Match"):
            item = isolated_types[name]
            require(
                isinstance(item, dict)
                and item.get("module")
                == (candidate if name == "Pattern" else OWNED_BRIDGES[family])
                and item.get("name") == name
                and item.get("qualified_name") == name
                and item.get("genuinely_importable") is True,
                "the strict audit accepted a substituted public owner",
            )
        strict_records = isolated.get("standard_pickle_checks")
        require(
            isinstance(strict_records, list)
            and len(strict_records) == 16
            and all(isinstance(row, dict) for row in strict_records)
            and [(row.get("origin"), row.get("argument"), row.get("protocol"))
                 for row in strict_records] == expected_rows
            and all(row.get("passed") is True for row in strict_records),
            "the strict audit omitted or replaced a real standard-library pickle",
        )
        _validate_guard(isolated.get("guard"), family)


def validate_v6_audits(
    source: dict[str, Any], strict: dict[str, Any], *,
    source_relative: str, strict_relative: str, source_digest: str,
    _synthetic_pins: Mapping[str, Any] | None = None,
) -> tuple[dict[str, str], dict[str, str]]:
    pins = _pin_values(_synthetic_pins)
    require(source_relative == V6_BASE_REPORT_RELATIVE,
            "a stale or substituted source-audit report cannot qualify current engines")
    require(strict_relative == V6_STRICT_REPORT_RELATIVE,
            "a stale or substituted no-delegation report cannot qualify current engines")
    require(source_digest == pins["base_report"],
            "the actual V6 source report is not the predeclared current proof")
    require(isinstance(source, dict) and isinstance(strict, dict),
            "both real current independence reports are required")
    for label, document, schema, controller, controller_hash in (
        ("source", source, V6_BASE_SCHEMA,
         V6_BASE_SOURCE_RELATIVE, pins["base_source"]),
        ("no-delegation", strict, V6_STRICT_SCHEMA,
         V6_STRICT_SOURCE_RELATIVE, pins["strict_source"]),
    ):
        require(
            document.get("schema") == schema
            and document.get("postfinal_schema") == schema
            and document.get("status") == "PASS"
            and document.get("result") == "PASS"
            and document.get("passed") is True
            and document.get("audit_source_path") == controller
            and document.get("audit_source_sha256") == controller_hash
            and document.get("verified_core_family_count") == 3
            and document.get("verified_distinct_pipeline_count") == 4,
            "the fresh version-six " + label + " proof is absent or forged",
        )
        families = document.get("families")
        require(isinstance(families, dict) and set(families) == ALL_FAMILIES,
                "an independence proof omitted an independently owned family")
        for family in CORE_FAMILIES:
            require(isinstance(families[family], dict)
                    and families[family].get("passed") is True,
                    "an actual native family did not pass: " + family)
    require(
        source.get("previous_v5_report_historical") is True
        and strict.get("previous_v5_report_historical") is True
        and strict.get("base_audit_source_path") == V6_BASE_SOURCE_RELATIVE
        and strict.get("base_audit_source_sha256") == pins["base_source"]
        and strict.get("base_audit_report_path") == V6_BASE_REPORT_RELATIVE
        and strict.get("base_audit_report_sha256") == pins["base_report"]
        and strict.get("base_audit_postfinal_schema") == V6_BASE_SCHEMA
        and strict.get("inherited_control_count") == 76,
        "the strict source proof was substituted, weakened, or bound to stale V5",
    )
    source_controls = source.get("postfinal_wrapper_self_test")
    strict_controls = strict.get("postfinal_wrapper_self_test")
    require(
        isinstance(source_controls, dict)
        and source_controls.get("passed") is True
        and source_controls.get("check_count", 0) >= 198
        and isinstance(strict_controls, dict)
        and strict_controls.get("passed") is True
        and strict_controls.get("inherited_v5_control_count", 0) >= 676,
        "an actual version-six source or no-delegation poison-control suite failed",
    )
    sources, natives, native_by_family = _base_graph(source)
    require(strict.get("native_elf_provenance") == source.get("native_elf_provenance"),
            "the source and no-delegation audits mapped different real native engines")
    require(strict.get("manifest_provenance") == source.get("manifest_provenance"),
            "the strict audit substituted an external dependency or lockfile")
    require(strict.get("qualified_source_fingerprints") == sources,
            "the strict audit does not bind all twelve exact current candidate sources")
    require(strict.get("native_elf_fingerprints") == natives,
            "the strict audit does not bind all five exact current native binaries")
    _validate_ownership(source, strict, native_by_family)
    scope = strict.get("scope")
    require(
        isinstance(scope, dict)
        and scope.get("fresh_v6_source_report_only") is True
        and scope.get("closed_owned_source_graph") is True
        and scope.get("mapped_binaries_hashed_against_static_elf") is True
        and scope.get("all_five_native_loader_aliases_blocked") is True
        and scope.get("enum_json_decoder_registry_bypass_blocked") is True
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_or_case_fixture_access") is False,
        "the genuine strict native independence or no-timing scope was weakened",
    )
    return sources, natives


def _validate_historical_v1() -> dict[str, Any]:
    source_path = previous.checked_repo_path(V1_SOURCE_RELATIVE)
    require(previous.sha256_path(source_path) == V1_SOURCE_SHA256,
            "the preserved official version-one source changed")
    evidence_path = previous.checked_repo_path(V1_REPORT_RELATIVE)
    require(previous.sha256_path(evidence_path) == V1_REPORT_SHA256,
            "the preserved historical official result changed")
    document = previous.read_json(evidence_path)
    require(
        document.get("schema") == V1_SCHEMA
        and document.get("status") == "PASS"
        and document.get("result") == "PASS"
        and document.get("python") == "3.14.6"
        and document.get("goal_sha256") == previous.GOAL_SHA256
        and document.get("source_path") == V1_SOURCE_RELATIVE
        and document.get("source_sha256") == V1_SOURCE_SHA256,
        "the authentic historical official result was counterfeited",
    )
    original = document.get("original_oracle")
    require(
        isinstance(original, dict)
        and original.get("manifest_path") == previous.ORIGINAL_MANIFEST_PATH
        and original.get("manifest_sha256") == previous.ORIGINAL_MANIFEST_SHA256
        and original.get("runner_path") == previous.ORIGINAL_RUNNER_PATH
        and original.get("runner_sha256") == previous.ORIGINAL_RUNNER_SHA256
        and original.get("source_sha256") == previous.SOURCE_HASHES
        and original.get("total_public_methods") == 152
        and original.get("selected_methods") == 146
        and original.get("selected_method_sha256") == previous.SELECTED_METHOD_SHA256
        and original.get("named_waivers") == previous.METHOD_WAIVERS
        and original.get("named_class_waivers") == previous.CLASS_WAIVERS
        and original.get("all_named_waivers")
        == (previous.CLASS_WAIVERS | previous.METHOD_WAIVERS)
        and original.get("corpus_cases") == 403,
        "the historical official source, 403-pattern corpus, or named waivers changed",
    )
    audits = document.get("audits")
    require(
        isinstance(audits, dict)
        and isinstance(audits.get("from_scratch"), dict)
        and isinstance(audits.get("no_delegation"), dict)
        and audits["from_scratch"].get("postfinal_schema")
        == "rebar-postfinal-from-scratch-audit-v5"
        and audits["no_delegation"].get("postfinal_schema")
        == "rebar-postfinal-no-delegation-audit-v5",
        "the historical V1 report cannot be represented as fresh V6 qualification",
    )
    roles = document.get("roles")
    require(isinstance(roles, dict) and set(roles) == set(previous.ROLE_MODULES),
            "the historical official report omitted a real engine")
    baseline = roles["re"]
    require(isinstance(baseline, dict) and isinstance(baseline.get("records"), list),
            "the historical Python official method baseline is absent")
    expected = frozenset(record.get("test") for record in baseline["records"]
                         if isinstance(record, dict))
    require(REQUIRED_CORPUS_METHOD in expected,
            "the actual official test of all 403 upstream regex cases was omitted")
    for family, module in previous.ROLE_MODULES.items():
        role = roles[family]
        require(isinstance(role, dict), "a preserved official family result is missing")
        raw = dict(role)
        raw.update({
            "schema": "rebar-cpython-re-result-v1",
            "runner_sha256": previous.ORIGINAL_RUNNER_SHA256,
            "source_sha256": previous.SOURCE_HASHES,
        })
        require(previous.validate_role(raw, module, expected_ids=expected) == role,
                "a historical official method result was hidden or changed")
    require(
        document.get("holdout_accessed") is False
        and document.get("timing_performed") is False
        and document.get("performance") == "NOT MEASURED",
        "the historical correctness-only official result changed its scope",
    )
    return {
        "schema": V1_SCHEMA,
        "source_path": V1_SOURCE_RELATIVE,
        "source_sha256": V1_SOURCE_SHA256,
        "report_path": V1_REPORT_RELATIVE,
        "report_sha256": V1_REPORT_SHA256,
        "historical": True,
        "qualifies_current_sources": False,
    }


@contextmanager
def _scoped_previous(history: Mapping[str, Any]) -> Iterator[None]:
    saved = {
        "SCHEMA": previous.SCHEMA,
        "SOURCE_PATH": previous.SOURCE_PATH,
        "EVIDENCE_PATH": previous.EVIDENCE_PATH,
        "validate_audits": previous.validate_audits,
        "exclusive_evidence": previous.exclusive_evidence,
    }

    def write_v2(document: dict[str, Any]) -> None:
        require(document.get("schema") == SCHEMA,
                "the unchanged original runner produced a substituted official schema")
        require(document.get("source_path") == SOURCE_RELATIVE,
                "the official output is not bound to the new source")
        require(document.get("python") == "3.14.6",
                "the official output is not bound to genuine pinned Python")
        roles = document.get("roles")
        require(isinstance(roles, dict)
                and set(roles) == set(previous.ROLE_MODULES),
                "the new official result omitted a separately run engine")
        require(all(isinstance(item, dict)
                    and item.get("methods") == 146
                    and item.get("passed") == 146
                    and item.get("skipped") == 0
                    and item.get("failed") == 0
                    and item.get("crashes") == 0
                    and item.get("timeouts") == 0
                    for item in roles.values()),
                "a real official test failed, skipped, timed out, or crashed")
        require(all(
            isinstance(item.get("records"), list)
            and REQUIRED_CORPUS_METHOD
            in {row.get("test") for row in item["records"] if isinstance(row, dict)}
            for item in roles.values()
        ), "one engine did not run all 403 original upstream corpus cases")
        document["supersedes"] = dict(history)
        document["official_scope"] = {
            "genuine_official_methods_per_engine": 146,
            "original_public_methods": 152,
            "original_upstream_corpus_cases": 403,
            "real_locale_methods_per_engine": 2,
            "independently_run_engine_count": 4,
            "verified_owned_source_count": 12,
            "verified_native_binary_count": 5,
            "named_waiver_count": 8,
            "previous_v1_report_historical": True,
            "previous_v1_qualifies_current_sources": False,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        }
        saved["exclusive_evidence"](document)

    previous.SCHEMA = SCHEMA
    previous.SOURCE_PATH = SOURCE_RELATIVE
    previous.EVIDENCE_PATH = EVIDENCE_PATH
    previous.validate_audits = validate_v6_audits
    previous.exclusive_evidence = write_v2
    try:
        yield
    finally:
        for name, value in saved.items():
            setattr(previous, name, value)


def run_audit() -> dict[str, Any]:
    previous.verify_runtime()
    require(not _candidate_modules(),
            "the official controller must not preload a candidate or matching engine")
    pins = _pin_values()
    _destination(REPORT_RELATIVE)
    require(EVIDENCE_PATH == ROOT / REPORT_RELATIVE,
            "the exclusive official output was redirected")
    require(not EVIDENCE_PATH.exists() and not EVIDENCE_PATH.is_symlink(),
            "the exclusive version-two official result already exists")
    history = _validate_historical_v1()
    base_source = previous.checked_repo_path(V6_BASE_SOURCE_RELATIVE)
    strict_source = previous.checked_repo_path(V6_STRICT_SOURCE_RELATIVE)
    base_report = previous.checked_repo_path(V6_BASE_REPORT_RELATIVE)
    strict_report = previous.checked_repo_path(V6_STRICT_REPORT_RELATIVE)
    for path, expected, name in (
        (base_source, pins["base_source"], "fresh source-audit controller"),
        (strict_source, pins["strict_source"], "fresh strict-audit controller"),
        (base_report, pins["base_report"], "fresh source-audit report"),
        (strict_report, pins["strict_report"], "fresh strict-audit report"),
    ):
        require(previous.sha256_path(path) == expected,
                "a genuinely passing version-six proof was substituted: " + name)
    source_document = previous.read_json(base_report)
    strict_document = previous.read_json(strict_report)
    sources, natives = validate_v6_audits(
        source_document, strict_document,
        source_relative=V6_BASE_REPORT_RELATIVE,
        strict_relative=V6_STRICT_REPORT_RELATIVE,
        source_digest=pins["base_report"],
    )
    previous.verify_production_fingerprints(sources, natives)
    require(not _candidate_modules(), "candidate modules leaked into the official controller")
    with _scoped_previous(history):
        report = previous.run_audit(V6_BASE_REPORT_RELATIVE, V6_STRICT_REPORT_RELATIVE)
    require(report.get("supersedes") == history
            and report.get("schema") == SCHEMA
            and report.get("source_path") == SOURCE_RELATIVE,
            "the actual source-bound official result was not exclusively recorded")
    require(not _candidate_modules(), "a candidate leaked out of its isolated official worker")
    return report


class _BlockSelfTestEffects:
    """Count and reject file, process, clock, and entropy side effects."""

    def __init__(self) -> None:
        self.counts = {"files": 0, "processes": 0, "clocks": 0, "entropy": 0}
        self.saved: list[tuple[Any, str, Any]] = []

    def _block(self, owner: Any, name: str, kind: str) -> None:
        if not hasattr(owner, name):
            return
        original = getattr(owner, name)

        def denied(*args: Any, **kwargs: Any) -> Any:
            del args, kwargs
            self.counts[kind] += 1
            raise LocaleV2Error("the synthetic official self-test attempted " + kind)

        self.saved.append((owner, name, original))
        setattr(owner, name, denied)

    def __enter__(self) -> _BlockSelfTestEffects:
        for owner, name in (
            (builtins, "open"), (io, "open"), (os, "open"),
            (tempfile, "mkdtemp"), (tempfile, "TemporaryDirectory"),
            (os, "mkdir"), (os, "makedirs"), (os, "unlink"), (os, "remove"),
        ):
            self._block(owner, name, "files")
        for owner, name in (
            (subprocess, "run"), (subprocess, "Popen"),
            (os, "system"), (os, "fork"), (os, "posix_spawn"),
        ):
            self._block(owner, name, "processes")
        for name in (
            "time", "time_ns", "monotonic", "monotonic_ns",
            "perf_counter", "perf_counter_ns", "process_time", "process_time_ns",
            "thread_time", "thread_time_ns",
        ):
            self._block(time, name, "clocks")
        self._block(os, "urandom", "entropy")
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        del exc_type, exc, traceback
        for owner, name, original in reversed(self.saved):
            setattr(owner, name, original)


def _synthetic_documents() -> tuple[dict[str, str], dict[str, Any], dict[str, Any]]:
    digest = lambda value: hashlib.sha256(value.encode("ascii")).hexdigest()
    pins = {name: digest("official-v2:" + name) for name in (
        "base_source", "base_report", "strict_source", "strict_report"
    )}
    families: dict[str, Any] = {"ast": {"passed": True}}
    native_families: dict[str, Any] = {}
    by_family: dict[str, dict[str, str]] = {}
    flattened: dict[str, str] = {}
    base_owners: dict[str, Any] = {}
    strict_owners: dict[str, Any] = {}
    all_sources: dict[str, str] = {}
    for family in CORE_FAMILIES:
        source_records = [
            {"file": path, "sha256": digest("source:" + path),
             "passed": True, "issues": []}
            for path in OWNED_SOURCE_PATHS[family]
        ]
        families[family] = {
            "passed": True,
            "owned_pipeline": {"passed": True, "issues": []},
            "python_source": source_records[0],
            "native_sources": source_records[1:],
        }
        all_sources.update({row["file"]: row["sha256"] for row in source_records})
        entries: dict[str, Any] = {}
        by_family[family] = {}
        for name, path in NATIVE_FILE_ROLES[family].items():
            fingerprint = digest("native:" + path)
            entries[name] = {
                "file": path, "sha256": fingerprint,
                "elf_class": 64, "forbidden_regex_symbols": [],
                "cross_candidate_symbols": [],
                "runpaths": ["$ORIGIN"] if name == "bridge" else [],
                "needed": [],
            }
            by_family[family][path] = fingerprint
            role = next(key for key, value in NATIVE_PATHS.items() if value == path)
            flattened[role] = fingerprint
        native_families[family] = {"files": entries}
        candidate = "candidates." + family + "_candidate"
        guard = {
            "family": family, "enabled": True,
            "stdlib_re_blocked": True, "cpython_sre_blocked": True,
            "third_party_regex_blocked": True, "cross_family_blocked": True,
            "foreign_dynamic_libraries_blocked": True,
            "native_loader_aliases_blocked": list(NATIVE_LOADER_ALIASES),
        }
        base_types: dict[str, Any] = {}
        strict_types: dict[str, Any] = {}
        for name in ("Pattern", "Match"):
            module = candidate if name == "Pattern" else OWNED_BRIDGES[family]
            strict_types[name] = {
                "module": module, "name": name, "qualified_name": name,
                "genuinely_importable": True,
            }
            base_types[name] = {
                **strict_types[name],
                "native_bridge_module": OWNED_BRIDGES[family],
                "candidate_identity": True,
                "native_bridge_identity": name == "Match",
            }
        rows = [
            {"origin": name, "argument": argument,
             "protocol": protocol, "passed": True}
            for name in ("Pattern", "Match")
            for argument in ("str", "bytes")
            for protocol in PICKLE_PROTOCOLS
        ]
        base_owners[family] = {
            "schema": V6_BASE_SCHEMA + "-owned-types",
            "status": "PASS", "result": "PASS", "passed": True,
            "family": family, "candidate_module": candidate,
            "native_bridge_module": OWNED_BRIDGES[family],
            "native_sha256": by_family[family],
            "standard_pickle_checks": 16,
            "public_types": base_types,
            "records": [
                {**row, "genuine_generic_alias": True,
                 "same_owned_native_origin": True,
                 "standard_pickle_round_trip": True}
                for row in rows
            ],
            "guard": dict(guard),
            "candidate_regex_matching_executed": False,
            "third_party_regex_packages": 0,
            "benchmark_or_timing_executed": False,
            "fixture_accessed": False,
        }
        strict_owners[family] = {
            "schema": "rebar-postfinal-no-delegation-public-owner-worker-v6",
            "status": "PASS", "role": family,
            "standard_pickle_check_count": 16,
            "standard_pickle_checks": rows,
            "public_type_ownership": strict_types,
            "native_binary_sha256": by_family[family],
            "cached_json_decoder_regex_blocked": True,
            "guard": dict(guard),
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        }
    manifest = {
        "passed": True, "issues": [], "python_dependencies": [],
        "rust_third_party_dependency_count": 0,
        "rust_lock_packages": ["rebar-rust-continuation"],
    }
    native = {
        "passed": True, "audited_binary_count": 5,
        "expected_binary_count": 5, "families": native_families,
    }
    shared = {
        "status": "PASS", "result": "PASS", "passed": True,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
        "previous_v5_report_historical": True,
        "families": families,
        "manifest_provenance": manifest,
        "native_elf_provenance": native,
    }
    source = {
        **copy.deepcopy(shared),
        "schema": V6_BASE_SCHEMA, "postfinal_schema": V6_BASE_SCHEMA,
        "audit_source_path": V6_BASE_SOURCE_RELATIVE,
        "audit_source_sha256": pins["base_source"],
        "postfinal_wrapper_self_test": {"passed": True, "check_count": 198},
        "runtime_native_mapping_provenance": {"passed": True},
        "verified_candidate_source_count": 12,
        "verified_candidate_source_paths": list(all_sources),
        "verified_native_role_count": 5,
        "native_sha256_by_family": by_family,
        "public_type_ownership": base_owners,
        "standard_pickle_checks": 48,
        "standard_pickle_checks_per_family": 16,
    }
    strict = {
        **copy.deepcopy(shared),
        "schema": V6_STRICT_SCHEMA, "postfinal_schema": V6_STRICT_SCHEMA,
        "audit_source_path": V6_STRICT_SOURCE_RELATIVE,
        "audit_source_sha256": pins["strict_source"],
        "base_audit_source_path": V6_BASE_SOURCE_RELATIVE,
        "base_audit_source_sha256": pins["base_source"],
        "base_audit_report_path": V6_BASE_REPORT_RELATIVE,
        "base_audit_report_sha256": pins["base_report"],
        "base_audit_postfinal_schema": V6_BASE_SCHEMA,
        "inherited_control_count": 76,
        "postfinal_wrapper_self_test": {
            "passed": True, "inherited_v5_control_count": 676,
        },
        "qualified_source_fingerprints": all_sources,
        "native_elf_fingerprints": flattened,
        "public_type_ownership": strict_owners,
        "verified_standard_pickle_count": 48,
        "verified_public_type_family_count": 3,
        "scope": {
            "fresh_v6_source_report_only": True,
            "closed_owned_source_graph": True,
            "mapped_binaries_hashed_against_static_elf": True,
            "all_five_native_loader_aliases_blocked": True,
            "enum_json_decoder_registry_bypass_blocked": True,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        },
    }
    return pins, source, strict


def self_test() -> dict[str, Any]:
    previous.verify_runtime()
    require(not _candidate_modules(),
            "the candidate-free official self-test began with a loaded engine")
    checks: list[dict[str, Any]] = []
    effects = _BlockSelfTestEffects()

    def check(name: str, condition: Any) -> None:
        require(not any(item["name"] == name for item in checks),
                "an official synthetic control was counted twice")
        checks.append({"name": name, "passed": bool(condition)})

    def reject(name: str, operation: Any) -> None:
        try:
            operation()
        except (AssertionError, KeyError, TypeError, ValueError, OSError):
            check(name, True)
        else:
            check(name, False)

    with effects:
        inherited = previous.self_test()
        check("retain-at-least-73-real-inherited-official-poison-controls",
              inherited.get("schema") == V1_SCHEMA + "-self-test"
              and inherited.get("status") == "PASS"
              and isinstance(inherited.get("passed"), int)
              and inherited["passed"] >= 73
              and inherited.get("candidate_imported") is False
              and inherited.get("candidate_executed") is False
              and inherited.get("files_read") == 0
              and inherited.get("files_written") == 0
              and inherited.get("locales_compiled") == 0
              and inherited.get("holdout_accessed") is False
              and inherited.get("timing_performed") is False)
        pins, source, strict = _synthetic_documents()

        def inspect(left: dict[str, Any], right: dict[str, Any], **changes: Any) -> Any:
            arguments: dict[str, Any] = {
                "source_relative": V6_BASE_REPORT_RELATIVE,
                "strict_relative": V6_STRICT_REPORT_RELATIVE,
                "source_digest": pins["base_report"],
                "_synthetic_pins": pins,
            }
            arguments.update(changes)
            return validate_v6_audits(left, right, **arguments)

        expected_sources, expected_native = inspect(source, strict)
        check("accept-complete-synthetic-v6-source-and-five-native-roles",
              len(expected_sources) == 12 and len(expected_native) == 5)
        check("pin-exact-authentic-root-created-v6-source",
              V6_BASE_SOURCE_SHA256
              == "77e7ea97f96280019b3be9abfeeb8fc6ff27ca6ecd13189e611586af5719c18f")
        check("pin-exact-authentic-root-created-v6-source-report",
              V6_BASE_REPORT_SHA256
              == "0314e3e5de3386d7c9c1e7f8fa4648554ff53cb53e3aafcecc4cb8e4923ddcbb")
        check("pin-exact-authentic-root-created-v6-strict-source",
              V6_STRICT_SOURCE_SHA256
              == "a936abe91d67169ea361b6770404ffe7bc925fdb3275aef854fbe12fe68a8649")
        check("pin-exact-authentic-root-created-v6-strict-report",
              V6_STRICT_REPORT_SHA256
              == "93f174f0861b0ee6e9feadf6e49bf222f0766b393ff74179219e65452b03d84f")
        check("accept-only-all-four-genuine-current-root-pins",
              _pin_values() == {
                  "base_source": V6_BASE_SOURCE_SHA256,
                  "base_report": V6_BASE_REPORT_SHA256,
                  "strict_source": V6_STRICT_SOURCE_SHA256,
                  "strict_report": V6_STRICT_REPORT_SHA256,
              })
        for key in pins:
            for label, poison in (("missing", None), ("invalid", "bad")):
                changed = dict(pins)
                changed[key] = poison
                reject("reject-" + key + "-" + label,
                       lambda changed=changed: _pin_values(changed))
        duplicate = dict(pins)
        duplicate["strict_report"] = duplicate["base_report"]
        reject("reject-shared-or-substituted-audit-fingerprints",
               lambda: _pin_values(duplicate))

        check("permit-only-exclusive-version-two-output",
              _destination(REPORT_RELATIVE) == REPORT_RELATIVE)
        for label, poison in (
            ("historical-v1-output", V1_REPORT_RELATIVE),
            ("source-audit-output", V6_BASE_REPORT_RELATIVE),
            ("strict-audit-output", V6_STRICT_REPORT_RELATIVE),
            ("absolute-output", "/" + REPORT_RELATIVE),
            ("traversing-output", "oracle/cpython-3.14.6/evidence/../foreign.json"),
            ("foreign-output", "oracle/cpython-3.14.6/evidence/foreign.json"),
            ("noncanonical-output", "oracle//cpython-3.14.6/evidence/x.json"),
            ("backslash-output", "oracle\\cpython-3.14.6\\evidence\\x.json"),
            ("nul-output", REPORT_RELATIVE + "\x00"),
            ("nontext-output", 6),
        ):
            reject("reject-" + label,
                   lambda poison=poison: _destination(poison))

        for label, key, poison in (
            ("base", "schema", V1_SCHEMA),
            ("base", "postfinal_schema", "rebar-postfinal-from-scratch-audit-v5"),
            ("base", "status", "FAIL"),
            ("base", "result", "FAIL"),
            ("base", "passed", False),
            ("base", "audit_source_path", V1_SOURCE_RELATIVE),
            ("base", "audit_source_sha256", pins["strict_source"]),
            ("base", "verified_core_family_count", 2),
            ("base", "verified_distinct_pipeline_count", 3),
            ("base", "previous_v5_report_historical", False),
            ("base", "verified_candidate_source_count", 11),
            ("base", "verified_candidate_source_paths", []),
            ("base", "verified_native_role_count", 4),
            ("base", "standard_pickle_checks", 47),
            ("base", "standard_pickle_checks_per_family", 15),
            ("strict", "schema", V1_SCHEMA),
            ("strict", "postfinal_schema", "rebar-postfinal-no-delegation-audit-v5"),
            ("strict", "status", "FAIL"),
            ("strict", "result", "FAIL"),
            ("strict", "passed", False),
            ("strict", "audit_source_path", V1_SOURCE_RELATIVE),
            ("strict", "audit_source_sha256", pins["base_source"]),
            ("strict", "base_audit_source_path", V1_SOURCE_RELATIVE),
            ("strict", "base_audit_source_sha256", pins["strict_source"]),
            ("strict", "base_audit_report_path", V1_REPORT_RELATIVE),
            ("strict", "base_audit_report_sha256", pins["strict_report"]),
            ("strict", "base_audit_postfinal_schema", V1_SCHEMA),
            ("strict", "inherited_control_count", 75),
            ("strict", "verified_core_family_count", 2),
            ("strict", "verified_distinct_pipeline_count", 3),
            ("strict", "previous_v5_report_historical", False),
            ("strict", "qualified_source_fingerprints", {}),
            ("strict", "native_elf_fingerprints", {}),
            ("strict", "verified_standard_pickle_count", 47),
            ("strict", "verified_public_type_family_count", 2),
        ):
            left, right = copy.deepcopy(source), copy.deepcopy(strict)
            (left if label == "base" else right)[key] = poison
            reject("reject-" + label + "-" + key,
                   lambda left=left, right=right: inspect(left, right))

        for family in CORE_FAMILIES:
            for owner in ("base", "strict"):
                left, right = copy.deepcopy(source), copy.deepcopy(strict)
                target = left if owner == "base" else right
                target["families"][family]["passed"] = False
                reject("reject-" + owner + "-failed-family-" + family,
                       lambda left=left, right=right: inspect(left, right))

                left, right = copy.deepcopy(source), copy.deepcopy(strict)
                target = left if owner == "base" else right
                del target["public_type_ownership"][family]
                reject("reject-" + owner + "-missing-public-owner-" + family,
                       lambda left=left, right=right: inspect(left, right))

                left, right = copy.deepcopy(source), copy.deepcopy(strict)
                target = left if owner == "base" else right
                record = target["public_type_ownership"][family]
                types_key = "public_types" if owner == "base" else "public_type_ownership"
                record[types_key]["Pattern"]["module"] = "re"
                reject("reject-" + owner + "-fake-stdlib-pattern-owner-" + family,
                       lambda left=left, right=right: inspect(left, right))

                left, right = copy.deepcopy(source), copy.deepcopy(strict)
                target = left if owner == "base" else right
                record = target["public_type_ownership"][family]
                rows_key = "records" if owner == "base" else "standard_pickle_checks"
                record[rows_key] = record[rows_key][:-1]
                reject("reject-" + owner + "-omitted-pickle-round-trip-" + family,
                       lambda left=left, right=right: inspect(left, right))

                left, right = copy.deepcopy(source), copy.deepcopy(strict)
                target = left if owner == "base" else right
                record = target["public_type_ownership"][family]
                record["guard"]["stdlib_re_blocked"] = False
                reject("reject-" + owner + "-stdlib-delegation-" + family,
                       lambda left=left, right=right: inspect(left, right))

        for key, poison in (
            ("fresh_v6_source_report_only", False),
            ("closed_owned_source_graph", False),
            ("mapped_binaries_hashed_against_static_elf", False),
            ("all_five_native_loader_aliases_blocked", False),
            ("enum_json_decoder_registry_bypass_blocked", False),
            ("benchmark_or_timing_executed", True),
            ("holdout_or_case_fixture_access", True),
        ):
            changed = copy.deepcopy(strict)
            changed["scope"][key] = poison
            reject("reject-weakened-native-scope-" + key,
                   lambda changed=changed: inspect(source, changed))

        for label, name in (
            ("stale-version-five-source", "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V5.json"),
            ("stale-version-five-strict", "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V5.json"),
        ):
            key = "source_relative" if "source" in label else "strict_relative"
            reject("reject-" + label,
                   lambda name=name, key=key: inspect(source, strict, **{key: name}))
        reject("reject-substituted-source-report-fingerprint",
               lambda: inspect(source, strict, source_digest=pins["strict_report"]))

        original_schema = previous.SCHEMA
        original_path = previous.SOURCE_PATH
        original_output = previous.EVIDENCE_PATH
        with _scoped_previous({"historical": True}):
            check("scope-only-v2-controller-schema-and-source",
                  previous.SCHEMA == SCHEMA
                  and previous.SOURCE_PATH == SOURCE_RELATIVE
                  and previous.EVIDENCE_PATH == EVIDENCE_PATH
                  and previous.validate_audits is validate_v6_audits)
        check("restore-all-original-official-controller-bindings",
              previous.SCHEMA == original_schema
              and previous.SOURCE_PATH == original_path
              and previous.EVIDENCE_PATH == original_output)
        check("preserve-exact-official-152-to-146-denominator",
              len(previous.METHOD_WAIVERS) == 6
              and len(previous.CLASS_WAIVERS) == 2)
        check("preserve-exact-403-case-official-corpus-test",
              REQUIRED_CORPUS_METHOD == "ExternalTests.test_re_tests")
        check("preserve-both-real-upstream-locale-method-identities",
              previous.REQUIRED_LOCALE_TESTS == frozenset({
                  "ReTests.test_locale_caching", "ReTests.test_locale_compiled"
              }))
        check("retain-unchanged-genuine-cpython-official-runner",
              previous.ORIGINAL_RUNNER_PATH == "tools/cpython_re_oracle.py")
        check("never-import-a-candidate-into-synthetic-controls",
              not _candidate_modules())

    for label, kind in (
        ("zero-files-read-or-written", "files"),
        ("zero-workers-or-candidate-processes", "processes"),
        ("zero-clock-or-performance-samples", "clocks"),
        ("zero-production-entropy-draws", "entropy"),
    ):
        check(label, effects.counts[kind] == 0)
    require(not _candidate_modules(),
            "an actual candidate leaked into the no-effect synthetic controls")
    failures = [item["name"] for item in checks if item["passed"] is not True]
    require(not failures, "synthetic official control failed: " + ", ".join(failures))
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "check_count": len(checks),
        "checks": checks,
        "inherited_v1_control_count": inherited["passed"],
        "candidate_imported": False,
        "candidate_executed": False,
        "candidate_imports": 0,
        "files_read": effects.counts["files"],
        "files_written": 0,
        "subprocesses": effects.counts["processes"],
        "clock_samples": effects.counts["clocks"],
        "production_entropy_drawn": False,
        "locales_compiled": 0,
        "production_cases_materialized": 0,
        "report_written": False,
        "holdout_accessed": False,
        "timing_performed": False,
        "performance": "NOT MEASURED",
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true",
                      help="run only blocked, synthetic, candidate-free controls")
    mode.add_argument("--audit", action="store_true",
                      help="exclusively run the four real unchanged official test suites")
    args = parser.parse_args(arguments)
    try:
        report = self_test() if args.self_test else run_audit()
    except (AssertionError, OSError, subprocess.SubprocessError,
            UnicodeError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"schema": SCHEMA, "status": "FAIL", "error": str(error)},
                         ensure_ascii=True, sort_keys=True), file=sys.stderr)
        return 1
    if args.self_test:
        print(json.dumps(report, ensure_ascii=True, sort_keys=True))
    else:
        print(json.dumps({
            "schema": SCHEMA,
            "status": "PASS",
            "evidence": REPORT_RELATIVE,
            "roles": {
                name: {key: value for key, value in item.items() if key != "records"}
                for name, item in report["roles"].items()
            },
            "previous_v1_report_historical": True,
            "performance": "NOT MEASURED",
        }, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
