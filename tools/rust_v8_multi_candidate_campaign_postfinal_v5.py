#!/usr/bin/env python3
"""Run all 22 real-locale stages with immutable, source-bound V5 provenance."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Mapping
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import rust_v8_multi_candidate_campaign_postfinal_v4 as ancestor


original = ancestor.original
hardened = ancestor.hardened
audit_v5 = ancestor.audit_v5
strict_v5 = ancestor.strict_v5
SCHEMA = "rebar-v8-multi-candidate-sealed-campaign-postfinal-v5"
SELF_TEST_SCHEMA = SCHEMA + "-self-test"
SOURCE_RELATIVE = "tools/rust_v8_multi_candidate_campaign_postfinal_v5.py"
SOURCE_PATH = ROOT / SOURCE_RELATIVE
ANCESTOR_SOURCE_RELATIVE = (
    "tools/rust_v8_multi_candidate_campaign_postfinal_v4.py"
)
ANCESTOR_SOURCE_SHA256 = (
    "67a7555976ab60c371c9aad1b7f94c112bd1c6aaf990e39c02f4484f3010e799"
)
ORIGINAL_HARDENED_EDGE_PATHS = hardened._expected_edge_paths
_ACTIVE_PROVENANCE: dict[str, Any] | None = None


def require(condition: Any, message: str) -> None:
    original.require(bool(condition), message)


def expected_edge_paths(family: str) -> dict[str, Path]:
    require(family in {"rust", "vm", "zig"}, "the V5 edge selected another family")
    expected = dict(ORIGINAL_HARDENED_EDGE_PATHS(family))
    module = {
        "rust": "candidates.rust_candidate",
        "vm": "candidates.vm_candidate",
        "zig": "candidates.zig_candidate",
    }[family]
    for role, relative in original.contract.SPECS[module].source_paths:
        actual = ROOT / relative
        if role in expected:
            require(expected[role] == actual, f"the exact {family}/{role} source changed")
        expected[role] = actual
    roles = {
        "rust": frozenset(
            {"public-python", "native-source", "bridge-source", "native-bridge", "native-engine"}
        ),
        "vm": frozenset({"public-python", "native-source", "native-bridge"}),
        "zig": frozenset(
            {"public-python", "native-source", "bridge-source", "native-bridge", "native-engine"}
        ),
    }
    require(set(expected) == roles[family], f"the V5 {family} edge role set changed")
    return expected


def validate_edge_artifacts(
    report: Mapping[str, Any], module: str, edge: Mapping[str, Any]
) -> None:
    require(module in original.MODULES, "the V5 edge selected a foreign engine")
    family = original.family_for(module)
    require(
        isinstance(edge, Mapping)
        and edge.get("module") == module
        and edge.get("family") == original.contract.SPECS[module].family
        and edge.get("checks") == original.contract.EDGE_CHECKS
        and edge.get("category_count") == original.contract.EDGE_CATEGORIES
        and edge.get("failed") == 0,
        "the V5 edge proof is stale, foreign, or incomplete",
    )
    families = report.get("families")
    native = report.get("native_elf_provenance")
    require(
        isinstance(families, Mapping)
        and isinstance(families.get(family), Mapping)
        and isinstance(native, Mapping)
        and isinstance(native.get("families"), Mapping)
        and isinstance(native["families"].get(family), Mapping),
        "the authentic V5 audit omitted the selected candidate",
    )
    current = families[family]
    python = current.get("python_source")
    sources = current.get("native_sources")
    require(
        isinstance(python, Mapping) and isinstance(sources, list),
        f"the exact {family} qualified source evidence is incomplete",
    )
    source_hashes: dict[str, str] = {}
    for record in (python, *sources):
        require(
            isinstance(record, Mapping)
            and isinstance(record.get("file"), str)
            and audit_v5.previous.previous.valid_sha256(record.get("sha256"))
            and record.get("passed") is True,
            "an owned V5 candidate source is unqualified",
        )
        filename = record["file"]
        require(filename not in source_hashes, "a V5 source role was duplicated")
        source_hashes[filename] = record["sha256"]
    files = native["families"][family].get("files")
    require(isinstance(files, Mapping), "the V5 candidate native roles are missing")
    native_hashes: dict[str, str] = {}
    for record in files.values():
        require(
            isinstance(record, Mapping)
            and isinstance(record.get("file"), str)
            and audit_v5.previous.previous.valid_sha256(record.get("sha256")),
            "a V5 native role has no verified ELF fingerprint",
        )
        filename = record["file"]
        require(filename not in native_hashes, "a V5 native role was duplicated")
        native_hashes[filename] = record["sha256"]

    expected = expected_edge_paths(family)
    artifacts = edge.get("production_artifacts")
    require(
        isinstance(artifacts, list) and len(artifacts) == len(expected),
        f"the V5 {family} complete production proof has missing or extra roles",
    )
    observed: set[str] = set()
    for artifact in artifacts:
        require(isinstance(artifact, Mapping), "an owned production artifact is malformed")
        role = artifact.get("role")
        require(
            isinstance(role, str) and role in expected and role not in observed,
            "a V5 artifact is duplicated, foreign, or cross-family",
        )
        path = hardened._valid_relative(
            artifact.get("path"), expected[role], f"exact {family}/{role}"
        )
        digest = (
            native_hashes.get(path)
            if role in {"native-bridge", "native-engine"}
            else source_hashes.get(path)
        )
        require(
            audit_v5.previous.previous.valid_sha256(digest)
            and artifact.get("sha256") == digest,
            f"the V5 candidate substituted the audited {family}/{role} bytes",
        )
        observed.add(role)
    require(observed == set(expected), "the V5 proof concealed an owned artifact")


@contextmanager
def scoped_edge_roles() -> Iterator[None]:
    require(
        hardened._expected_edge_paths is ORIGINAL_HARDENED_EDGE_PATHS,
        "the immutable hardened edge checker was already replaced",
    )
    hardened._expected_edge_paths = expected_edge_paths
    try:
        yield
    finally:
        hardened._expected_edge_paths = ORIGINAL_HARDENED_EDGE_PATHS


def _actual_controller_digest() -> str:
    digest, _ = audit_v5.previous.previous.bounded_file(
        SOURCE_PATH,
        maximum=audit_v5.MAX_SOURCE_BYTES,
        label="actual additive real-locale V5 campaign controller",
    )
    return digest


def static_family_audit(module: str, edge: dict[str, Any]) -> dict[str, Any]:
    ancestor._bounded_source(
        ancestor.SOURCE_PATH,
        ANCESTOR_SOURCE_SHA256,
        "immutable historical V4 campaign controller",
    )
    with scoped_edge_roles():
        result = ancestor.static_family_audit(module, edge)
    validate_edge_artifacts(result, module, edge)
    result["sealed_campaign_controller"] = {
        "postfinal_schema": SCHEMA,
        "source_path": SOURCE_RELATIVE,
        "source_sha256": _actual_controller_digest(),
        "ancestor_source_path": ANCESTOR_SOURCE_RELATIVE,
        "ancestor_source_sha256": ANCESTOR_SOURCE_SHA256,
        "expected_complete_production_role_count": len(
            expected_edge_paths(original.family_for(module))
        ),
    }
    return result


def output_path(path: Path, module: str) -> Path:
    result = ancestor.ORIGINAL_OUTPUT_PATH(path, module)
    family = original.family_for(module)
    expected = f"rust-v8-{family}-postfinal-locale-v5-sealed-campaign.json"
    require(
        result.name == expected,
        "only the exact fresh candidate-specific V5 locale campaign may be created",
    )
    return result


def validate_report_structure(report: dict[str, Any], module: str) -> None:
    state = _ACTIVE_PROVENANCE
    require(isinstance(state, dict), "the V5 report was validated outside its live scope")
    source_digest = state.get("source_sha256")
    require(
        audit_v5.previous.previous.valid_sha256(source_digest)
        and _actual_controller_digest() == source_digest,
        "the actual V5 campaign controller changed during execution",
    )
    keys = {
        "postfinal_schema",
        "controller_source_path",
        "controller_source_sha256",
        "ancestor_source_path",
        "ancestor_source_sha256",
    }
    existing = keys & set(report)
    if not state["armed"]:
        require(not existing, "the live V5 report arrived with forged producer fields")
        report.update(
            {
                "postfinal_schema": SCHEMA,
                "controller_source_path": SOURCE_RELATIVE,
                "controller_source_sha256": source_digest,
                "ancestor_source_path": ANCESTOR_SOURCE_RELATIVE,
                "ancestor_source_sha256": ANCESTOR_SOURCE_SHA256,
            }
        )
        state["armed"] = True
    else:
        require(existing == keys, "the restored V5 report dropped producer provenance")
    require(
        report.get("postfinal_schema") == SCHEMA
        and report.get("controller_source_path") == SOURCE_RELATIVE
        and report.get("controller_source_sha256") == source_digest
        and report.get("ancestor_source_path") == ANCESTOR_SOURCE_RELATIVE
        and report.get("ancestor_source_sha256") == ANCESTOR_SOURCE_SHA256,
        "the V5 report forged its actual producer or immutable V4 ancestor",
    )
    ancestor.validate_report_structure(report, module)
    source_step = next(
        item for item in report["steps"] if item["name"] == "from-scratch-static-audit"
    )
    proof = source_step["evidence"].get("sealed_campaign_controller")
    require(
        isinstance(proof, Mapping)
        and proof.get("postfinal_schema") == SCHEMA
        and proof.get("source_path") == SOURCE_RELATIVE
        and proof.get("source_sha256") == source_digest
        and proof.get("ancestor_source_path") == ANCESTOR_SOURCE_RELATIVE
        and proof.get("ancestor_source_sha256") == ANCESTOR_SOURCE_SHA256
        and proof.get("expected_complete_production_role_count")
        == len(expected_edge_paths(original.family_for(module))),
        "the V5 static stage is not bound to its exact producer and native roles",
    )


@contextmanager
def current_v5_campaign() -> Iterator[None]:
    global _ACTIVE_PROVENANCE
    require(_ACTIVE_PROVENANCE is None, "a V5 campaign is already active")
    source_digest = _actual_controller_digest()
    with ancestor.current_locale_campaign():
        require(
            original.static_family_audit is ancestor.static_family_audit
            and original.output_path is ancestor.output_path
            and original.validate_report_structure is ancestor.validate_report_structure,
            "the restored V4 campaign provider was substituted",
        )
        _ACTIVE_PROVENANCE = {"source_sha256": source_digest, "armed": False}
        original.static_family_audit = static_family_audit
        original.output_path = output_path
        original.validate_report_structure = validate_report_structure
        try:
            yield
        finally:
            original.validate_report_structure = ancestor.validate_report_structure
            original.output_path = ancestor.output_path
            original.static_family_audit = ancestor.static_family_audit
            _ACTIVE_PROVENANCE = None


def _synthetic_edge(module: str) -> tuple[dict[str, Any], dict[str, Any]]:
    family = original.family_for(module)
    paths = expected_edge_paths(family)
    python_path = hardened.scratch.PYTHON_SOURCES[family]
    python = {
        "file": hardened._relative(python_path),
        "sha256": hardened._synthetic_digest("v5-edge:" + hardened._relative(python_path)),
        "passed": True,
    }
    sources = [
        {
            "file": hardened._relative(path),
            "sha256": hardened._synthetic_digest("v5-edge:" + hardened._relative(path)),
            "passed": True,
        }
        for path in hardened.scratch.NATIVE_SOURCES[family]
    ]
    files = {
        role: {
            "file": hardened._relative(path),
            "sha256": hardened._synthetic_digest("v5-native:" + hardened._relative(path)),
        }
        for role, path in hardened.scratch.NATIVE_BINARIES[family].items()
    }
    source = {
        "families": {family: {"python_source": python, "native_sources": sources}},
        "native_elf_provenance": {"families": {family: {"files": files}}},
    }
    source_hashes = {item["file"]: item["sha256"] for item in (python, *sources)}
    native_hashes = {item["file"]: item["sha256"] for item in files.values()}
    artifacts = []
    for role, path in sorted(paths.items()):
        relative = hardened._relative(path)
        digest = (
            native_hashes.get(relative)
            if role in {"native-bridge", "native-engine"}
            else source_hashes.get(relative)
        )
        require(audit_v5.previous.previous.valid_sha256(digest), "the synthetic edge lost a role")
        artifacts.append({"role": role, "path": relative, "sha256": digest})
    return source, {
        "module": module,
        "family": original.contract.SPECS[module].family,
        "checks": original.contract.EDGE_CHECKS,
        "category_count": original.contract.EDGE_CATEGORIES,
        "failed": 0,
        "production_artifacts": artifacts,
    }


def self_test() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def check(name: str, value: Any) -> None:
        checks.append({"id": name, "passed": bool(value)})

    def rejected(name: str, operation: Any) -> None:
        try:
            operation()
        except (AssertionError, TypeError, ValueError, KeyError):
            check(name, True)
        else:
            check(name, False)

    with (
        mock.patch.object(subprocess, "Popen", side_effect=AssertionError("V5 self-tests cannot launch workers")) as processes,
        mock.patch.object(audit_v5, "audit", side_effect=AssertionError("V5 self-tests cannot run production audits")) as source_audit,
        mock.patch.object(strict_v5, "run_audit", side_effect=AssertionError("V5 self-tests cannot run strict audits")) as strict_audit,
        mock.patch.object(audit_v5.previous.previous, "bounded_file", side_effect=AssertionError("V5 self-tests cannot read evidence")) as evidence,
    ):
        inherited = ancestor.self_test()
        require(
            isinstance(inherited, Mapping)
            and inherited.get("schema") == ancestor.SELF_TEST_SCHEMA
            and inherited.get("passed") is True
            and inherited.get("poison_control_count", 0) >= 93
            and inherited.get("inherited_hardened_control_count", 0) >= 43
            and inherited.get("inherited_campaign_control_count", 0) >= 46
            and inherited.get("candidate_processes_started") == 0
            and inherited.get("production_audits_run") == 0
            and inherited.get("production_report_reads") == 0,
            "the immutable locale-aware V4/V2/original safeguards failed",
        )
        for item in inherited["poison_controls"]:
            check("v4:" + item["id"], item["passed"] is True)
        check("pin-exact-actual-v4-ancestor-digest", audit_v5.previous.previous.valid_sha256(ANCESTOR_SOURCE_SHA256))
        check("preserve-all-93-v4-locale-controls", inherited["poison_control_count"] >= 93)
        check("preserve-all-43-hardened-v2-controls", inherited["inherited_hardened_control_count"] >= 43)
        check("preserve-all-46-original-campaign-controls", inherited["inherited_campaign_control_count"] >= 46)
        check("preserve-real-official-146-denominator", ancestor.OFFICIAL_METHODS == 146)
        check("preserve-full-22-stage-denominator", ancestor.REQUIRED_STEP_COUNT == 22)
        check("preserve-hardened-original-edge-provider", hardened._expected_edge_paths is ORIGINAL_HARDENED_EDGE_PATHS)

        for module in original.MODULES:
            family = original.family_for(module)
            source, edge = _synthetic_edge(module)
            expected_count = {"rust": 5, "vm": 3, "zig": 5}[family]
            check("pin-exact-owned-edge-role-denominator:" + family, len(expected_edge_paths(family)) == expected_count)
            validate_edge_artifacts(source, module, edge)
            check("accept-exact-owned-v5-edge-artifacts:" + family, True)

            def poison(name: str, mutation: Any) -> None:
                def wrong() -> None:
                    changed = copy.deepcopy(edge)
                    mutation(changed)
                    validate_edge_artifacts(source, module, changed)

                rejected(name + ":" + family, wrong)

            poison("reject-missing-owned-edge-role", lambda item: item["production_artifacts"].pop())
            poison(
                "reject-extra-owned-edge-role",
                lambda item: item["production_artifacts"].append(
                    {"role": "foreign-native", "path": "candidates/_foreign.so", "sha256": "0" * 64}
                ),
            )
            poison(
                "reject-duplicated-owned-edge-role",
                lambda item: item["production_artifacts"].__setitem__(
                    -1, dict(item["production_artifacts"][0])
                ),
            )
            poison("reject-poisoned-owned-edge-hash", lambda item: item["production_artifacts"][0].update(sha256="0" * 64))
            poison("reject-cross-family-owned-edge-path", lambda item: item["production_artifacts"][0].update(path="candidates/_foreign_native.so"))
            poison("reject-cross-family-edge-module", lambda item: item.update(module="candidates.ast_candidate"))
        with scoped_edge_roles():
            check("scope-exact-hardened-v5-edge-provider", hardened._expected_edge_paths is expected_edge_paths)
        check("restore-immutable-hardened-v2-edge-provider", hardened._expected_edge_paths is ORIGINAL_HARDENED_EDGE_PATHS)
        check("never-start-candidate-process", processes.call_count == 0)
        check("never-run-v5-source-audit", source_audit.call_count == 0)
        check("never-run-v5-strict-audit", strict_audit.call_count == 0)
        check("never-read-production-evidence", evidence.call_count == 0)
        check("never-replace-immutable-v4-static-provider", original.static_family_audit is ancestor.ORIGINAL_STATIC_AUDIT)

    names = [item["id"] for item in checks]
    require(
        len(checks) >= 120
        and len(names) == len(set(names))
        and all(item["passed"] is True for item in checks),
        "the additive V5 real-locale edge safeguards failed or were weakened",
    )
    return {
        "schema": SELF_TEST_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "python": "3.14.6",
        "synthetic_only": True,
        "ancestor_source_path": ANCESTOR_SOURCE_RELATIVE,
        "ancestor_source_sha256": ANCESTOR_SOURCE_SHA256,
        "inherited_v4_schema": ancestor.SELF_TEST_SCHEMA,
        "inherited_v4_control_count": inherited["poison_control_count"],
        "inherited_hardened_control_count": inherited["inherited_hardened_control_count"],
        "inherited_campaign_control_count": inherited["inherited_campaign_control_count"],
        "candidate_modules": list(original.MODULES),
        "actual_planned_step_counts": inherited["actual_planned_step_counts"],
        "official_method_count": ancestor.OFFICIAL_METHODS,
        "poison_control_count": len(checks),
        "poison_controls": checks,
        "candidate_processes_started": 0,
        "candidate_reports_written": 0,
        "production_audits_run": 0,
        "historical_audits_run": 0,
        "historical_audit_fallback_available": False,
        "production_report_reads": 0,
        "performance_processes_started": 0,
        "performance_fixtures_opened": 0,
        "holdout_accessed": False,
        "performance": "NOT MEASURED",
        "timing_performed": False,
        "failed": 0,
    }


def main(arguments: list[str] | None = None) -> int:
    args = original.parse_arguments(arguments)
    if args.self_test:
        require(
            args.module is None
            and args.edge_oracle is None
            and args.deep_proof is None
            and args.output is None,
            "the V5 campaign self-test cannot run a candidate or create evidence",
        )
        print(json.dumps(self_test(), ensure_ascii=True, sort_keys=True), flush=True)
        return 0
    with current_v5_campaign():
        return original.main(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
