#!/usr/bin/env python3
"""Run the genuine 22-stage campaign against exact V5 real-locale proofs."""

from __future__ import annotations

import copy
import dataclasses
import hashlib
import json
import os
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
import subprocess
import sys
from typing import Any, Iterator, Mapping
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import postfinal_from_scratch_audit_v5 as audit_v5
from tools import postfinal_no_delegation_audit_v5 as strict_v5
from tools import rust_v8_multi_candidate_campaign as original
from tools import rust_v8_multi_candidate_campaign_postfinal_v2 as hardened


SCHEMA = "rebar-v8-multi-candidate-sealed-campaign-postfinal-v4"
SELF_TEST_SCHEMA = SCHEMA + "-self-test"
SOURCE_RELATIVE = "tools/rust_v8_multi_candidate_campaign_postfinal_v4.py"
SOURCE_PATH = ROOT / SOURCE_RELATIVE
V5_SOURCE_SHA256 = (
    "100520ae06c3a837b3fa4ca508099ceb6e11efda8f63bcc0234b544071d17843"
)
V5_REPORT_SHA256 = (
    "42bd73acf6831b67df9a9873fa35c1882f2af09c41933774ba841d2290e6c198"
)
STRICT_SOURCE_SHA256 = (
    "18a04023659e386780d6e9cd6b90065553254c18f2fe54ae78c37acbc468a7b6"
)
STRICT_REPORT_SHA256 = (
    "50031133a2aa20b1ef91b126a883a622d916f582fdcbea4ba1763267199c03bb"
)
HARDENED_SOURCE_SHA256 = (
    "cdabec673a905b122c474a8279b84f194534fda77a0c70555fb9aa9fd299592d"
)
LOCALE_RELATIVE = "oracle/cpython-3.14.6/evidence/postfinal-locale-v1-all.json"
LOCALE_PATH = ROOT / LOCALE_RELATIVE
LOCALE_SHA256 = (
    "bc17ee74409543d1b57f3aee65088e990ab21ac83dc75ac46fbd1f97f04b6621"
)
LOCALE_SOURCE_RELATIVE = "tools/postfinal_cpython_locale_oracle_v1.py"
LOCALE_SOURCE_SHA256 = (
    "b87bbdcddef2d19a462e8c4b37bd159f6c3a30ea9b4fe5d9471eff1f51fbcb55"
)
LOCALE_SCHEMA = "rebar-postfinal-cpython-public-locale-v1"
EXPECTED_LOCPATH = "/tmp/rebar-official-locale-proof-0EdjeBJ1lS"
OFFICIAL_METHODS = 146
REQUIRED_STEP_COUNT = 22
ORIGINAL_STATIC_AUDIT = original.static_family_audit
ORIGINAL_GENERIC_STEPS = original.generic_steps
ORIGINAL_CHILD_STEP = original.child_step
ORIGINAL_VALIDATE_REPORT = original.validate_report_structure
ORIGINAL_OUTPUT_PATH = original.output_path


def require(condition: Any, message: str) -> None:
    original.require(bool(condition), message)


def _valid_relative(value: Any, expected: str, label: str) -> str:
    require(type(value) is str, f"the V4 {label} is not an exact public path")
    path = PurePosixPath(value)
    require(
        not path.is_absolute()
        and ".." not in path.parts
        and "\\" not in value
        and "\x00" not in value
        and str(path) == value
        and value == expected,
        f"the V4 {label} was substituted, noncanonical, or private",
    )
    return value


def _bounded_document(path: Path, *, expected: str, label: str) -> dict[str, Any]:
    require(not path.is_symlink(), f"the exact V4 {label} is a symlink")
    digest, payload = audit_v5.previous.previous.bounded_file(
        path,
        maximum=audit_v5.MAX_REPORT_BYTES,
        label="locale-aware sealed V4 " + label,
        keep=True,
    )
    require(digest == expected, f"the exact V4 {label} has changed")
    return audit_v5.previous.previous.decode_report(
        payload, label="locale-aware sealed V4 " + label
    )


def _bounded_source(path: Path, expected: str, label: str) -> None:
    require(not path.is_symlink(), f"the V4 {label} is a symlink")
    digest, _ = audit_v5.previous.previous.bounded_file(
        path,
        maximum=audit_v5.MAX_SOURCE_BYTES,
        label="locale-aware sealed V4 " + label,
    )
    require(digest == expected, f"the immutable V4 {label} changed")


def validate_locale_document(
    document: Mapping[str, Any], *, module: str | None = None
) -> dict[str, Any]:
    require(isinstance(document, Mapping), "the real locale proof is not an object")
    require(
        document.get("schema") == LOCALE_SCHEMA
        and document.get("status") == "PASS"
        and document.get("result") == "PASS"
        and document.get("source_path") == LOCALE_SOURCE_RELATIVE
        and document.get("source_sha256") == LOCALE_SOURCE_SHA256
        and document.get("holdout_accessed") is False
        and document.get("performance") == "NOT MEASURED"
        and document.get("timing_performed") is False,
        "the actual real-locale all-role proof failed or used hidden cases or timing",
    )
    audits = document.get("audits")
    require(isinstance(audits, Mapping), "the locale proof omitted its exact V5 audits")
    expected = {
        "from_scratch": {
            "path": audit_v5.REPORT_RELATIVE,
            "postfinal_schema": audit_v5.SCHEMA,
            "sha256": V5_REPORT_SHA256,
            "source_path": audit_v5.SOURCE_RELATIVE,
            "source_sha256": V5_SOURCE_SHA256,
        },
        "no_delegation": {
            "path": strict_v5.REPORT_RELATIVE,
            "postfinal_schema": strict_v5.SCHEMA,
            "sha256": STRICT_REPORT_SHA256,
            "source_path": strict_v5.SOURCE_RELATIVE,
            "source_sha256": STRICT_SOURCE_SHA256,
        },
    }
    require(set(audits) == set(expected), "the locale proof omitted or added a source audit")
    for name, fields in expected.items():
        current = audits.get(name)
        require(
            isinstance(current, Mapping)
            and all(current.get(key) == value for key, value in fields.items()),
            f"the locale proof substituted its exact {name} V5 audit",
        )
    locales = document.get("locales")
    reference = document.get("locale_reference")
    require(
        isinstance(locales, Mapping)
        and locales.get("genuine") is True
        and locales.get("holdout_accessed") is False
        and locales.get("performance") == "NOT MEASURED"
        and locales.get("timing_performed") is False
        and isinstance(locales.get("iso88591"), Mapping)
        and locales["iso88591"].get("name") == "en_US.iso88591"
        and isinstance(locales.get("utf8"), Mapping)
        and locales["utf8"].get("name") == "en_US.utf8"
        and isinstance(reference, Mapping)
        and reference.get("status") == "PASS"
        and reference.get("genuine_locales") is True
        and reference.get("compiled_locale_switch") is True
        and reference.get("candidate_modules_loaded") is False,
        "the official campaign has no genuine independently established locales",
    )
    native = document.get("native_elf_fingerprints")
    sources = document.get("qualified_source_fingerprints")
    require(
        isinstance(native, Mapping)
        and len(native) == 5
        and isinstance(sources, Mapping)
        and len(sources) == 12,
        "the actual locale proof omitted a native role or qualified source",
    )
    roles = document.get("roles")
    require(isinstance(roles, Mapping), "the real locale proof omitted candidate roles")
    expected_roles = {
        "re": "re",
        "rust": "candidates.rust_candidate",
        "vm": "candidates.vm_candidate",
        "zig": "candidates.zig_candidate",
    }
    require(set(roles) == set(expected_roles), "the locale proof omitted or substituted an engine")
    official_names: set[str] | None = None
    for role, expected_module in expected_roles.items():
        result = roles.get(role)
        require(
            isinstance(result, Mapping)
            and result.get("module") == expected_module
            and result.get("methods") == OFFICIAL_METHODS
            and result.get("passed") == OFFICIAL_METHODS
            and result.get("skipped") == 0
            and result.get("failed") == 0
            and result.get("failures") == 0
            and result.get("crashes") == 0
            and result.get("timeouts") == 0
            and result.get("locale_caching_passed") is True
            and result.get("locale_compiled_passed") is True
            and result.get("holdout_accessed") is False
            and result.get("performance") == "NOT MEASURED"
            and result.get("timing_performed") is False,
            f"the real locale proof weakened the actual {role} official 146 tests",
        )
        records = result.get("records")
        require(
            isinstance(records, list)
            and len(records) == OFFICIAL_METHODS
            and all(
                isinstance(item, Mapping)
                and isinstance(item.get("test"), str)
                and item.get("status") == "passed"
                and item.get("skipped") == 0
                for item in records
            ),
            f"the real locale proof omitted named official {role} methods",
        )
        names = {item["test"] for item in records}
        require(len(names) == OFFICIAL_METHODS, f"official {role} methods repeat")
        if official_names is None:
            official_names = names
        else:
            require(names == official_names, f"official {role} test names differ from stdlib")
    if module is not None:
        family = original.family_for(module)
        require(roles[family]["module"] == module, "the locale proof selected another candidate")
    return dict(document)


def _adapt_v5_for_hardened_validator(document: Mapping[str, Any]) -> dict[str, Any]:
    adapted = dict(document)
    adapted.update(
        {
            "postfinal_schema": hardened.audit_v3.SCHEMA,
            "audit_source_path": hardened.audit_v3.SOURCE_RELATIVE,
            "audit_source_sha256": hardened.V3_SOURCE_SHA256,
            "postfinal_wrapper_self_test": document["previous_v3_wrapper_self_test"],
            "postfinal_scope": {
                "append_only": True,
                "exclusive_report_path": hardened.audit_v3.REPORT_RELATIVE,
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
    return adapted


def validate_current_proofs(
    source: Mapping[str, Any],
    strict: Mapping[str, Any],
    locale: Mapping[str, Any],
    module: str,
    edge: Mapping[str, Any],
    *,
    verify_live_bytes: bool,
) -> dict[str, Any]:
    require(module in original.MODULES, "the V5 campaign selected a foreign module")
    source = audit_v5.validate_v5_report(dict(source), label="actual sealed V5 source audit")
    require(
        source.get("audit_source_sha256") == V5_SOURCE_SHA256
        and source.get("postfinal_wrapper_self_test", {}).get("check_count") >= 198,
        "the sealed campaign's exact V5 source proof is stale or incomplete",
    )
    require(
        isinstance(strict, Mapping)
        and strict.get("schema") == strict_v5.SCHEMA
        and strict.get("postfinal_schema") == strict_v5.SCHEMA
        and strict.get("status") == "PASS"
        and strict.get("result") == "PASS"
        and strict.get("passed") is True
        and strict.get("audit_source_path") == strict_v5.SOURCE_RELATIVE
        and strict.get("audit_source_sha256") == STRICT_SOURCE_SHA256
        and strict.get("base_audit_report_path") == audit_v5.REPORT_RELATIVE
        and strict.get("base_audit_report_sha256") == V5_REPORT_SHA256
        and strict.get("inherited_control_count") == 76
        and isinstance(strict.get("self_test"), Mapping)
        and strict["self_test"].get("check_count") == 32
        and strict["self_test"].get("passed") is True
        and isinstance(strict.get("inherited_self_test"), Mapping)
        and strict["inherited_self_test"].get("check_count") == 76
        and strict["inherited_self_test"].get("passed") is True
        and isinstance(strict.get("postfinal_wrapper_self_test"), Mapping)
        and strict["postfinal_wrapper_self_test"].get("passed") is True
        and strict["postfinal_wrapper_self_test"].get("check_count", 0) >= 676,
        "the genuine V5 immutable 32/76 strict independence proof failed",
    )
    strict_sources = strict.get("qualified_source_fingerprints")
    strict_native = strict.get("native_elf_fingerprints")
    require(
        isinstance(strict_sources, Mapping)
        and len(strict_sources) == 12
        and isinstance(strict_native, Mapping)
        and len(strict_native) == 5,
        "the strict V5 proof omitted one of the 12 sources or five native roles",
    )
    scope = strict.get("scope")
    require(
        isinstance(scope, Mapping)
        and scope.get("base_v5_report_only") is True
        and scope.get("closed_owned_source_graph") is True
        and scope.get("mapped_binaries_hashed_against_static_elf") is True
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_or_case_fixture_access") is False,
        "the sealed V5 strict proof weakened source isolation or hidden-data safety",
    )
    checked_locale = validate_locale_document(locale, module=module)
    require(
        checked_locale["qualified_source_fingerprints"] == strict_sources
        and checked_locale["native_elf_fingerprints"] == strict_native,
        "the official locale proof substituted a native candidate source or ELF",
    )
    hardened._validate_current_document(
        _adapt_v5_for_hardened_validator(source),
        module,
        edge,
        observed_report_sha256=hardened.V3_REPORT_SHA256,
        expected_report_sha256=hardened.V3_REPORT_SHA256,
        observed_source_sha256=hardened.V3_SOURCE_SHA256,
        expected_source_sha256=hardened.V3_SOURCE_SHA256,
        verify_live_bytes=verify_live_bytes,
    )
    result = dict(source)
    result["sealed_locale_provenance"] = {
        "schema": LOCALE_SCHEMA,
        "path": LOCALE_RELATIVE,
        "sha256": LOCALE_SHA256,
        "source_path": LOCALE_SOURCE_RELATIVE,
        "source_sha256": LOCALE_SOURCE_SHA256,
        "official_methods": OFFICIAL_METHODS,
        "candidate_family": original.family_for(module),
        "all_roles": ["re", "rust", "vm", "zig"],
    }
    result["sealed_no_delegation_provenance"] = {
        "schema": strict_v5.SCHEMA,
        "path": strict_v5.REPORT_RELATIVE,
        "sha256": STRICT_REPORT_SHA256,
        "source_path": strict_v5.SOURCE_RELATIVE,
        "source_sha256": STRICT_SOURCE_SHA256,
        "strict_control_count": 32,
        "inherited_control_count": 76,
    }
    return result


def static_family_audit(module: str, edge: dict[str, Any]) -> dict[str, Any]:
    require(
        os.environ.get("LOCPATH") == EXPECTED_LOCPATH,
        "the genuine official locale environment is absent or substituted",
    )
    _bounded_source(
        hardened.LEGACY_SOURCE_PATH,
        hardened.LEGACY_SOURCE_SHA256,
        "immutable original 22-stage source",
    )
    _bounded_source(
        hardened.SOURCE_PATH,
        HARDENED_SOURCE_SHA256,
        "immutable hardened V2 campaign wrapper",
    )
    _bounded_source(audit_v5.SOURCE_PATH, V5_SOURCE_SHA256, "actual V5 source audit")
    _bounded_source(strict_v5.SOURCE_PATH, STRICT_SOURCE_SHA256, "actual V5 strict audit")
    _bounded_source(ROOT / LOCALE_SOURCE_RELATIVE, LOCALE_SOURCE_SHA256, "actual official locale producer")
    source = _bounded_document(
        audit_v5.REPORT_PATH, expected=V5_REPORT_SHA256, label="actual V5 source proof"
    )
    strict = _bounded_document(
        strict_v5.REPORT_PATH,
        expected=STRICT_REPORT_SHA256,
        label="actual V5 strict proof",
    )
    locale = _bounded_document(
        LOCALE_PATH, expected=LOCALE_SHA256, label="actual official all-role locale proof"
    )
    return validate_current_proofs(
        source,
        strict,
        locale,
        module,
        edge,
        verify_live_bytes=True,
    )


def generic_steps(module: str, directory: Path) -> tuple[Any, ...]:
    steps = ORIGINAL_GENERIC_STEPS(module, directory)
    require(len(steps) == 12, "the immutable campaign changed its generic step count")
    actual = []
    seen = 0
    for step in steps:
        if step.name == "official-cpython-tests":
            require(step.expected_checks == 144, "the exact legacy official denominator changed")
            actual.append(dataclasses.replace(step, expected_checks=OFFICIAL_METHODS))
            seen += 1
        else:
            actual.append(step)
    require(seen == 1, "the campaign omitted or duplicated its real official locale stage")
    return tuple(actual)


def child_step(
    step: Any,
    module: str,
    memory_mib: int,
    *,
    contract_role: str | None = None,
    edge: dict[str, Any] | None = None,
    deep_proof: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if step.name != "official-cpython-tests":
        return ORIGINAL_CHILD_STEP(
            step,
            module,
            memory_mib,
            contract_role=contract_role,
            edge=edge,
            deep_proof=deep_proof,
        )
    require(contract_role is None, "the official locale stage changed its guard role")
    require(
        step.expected_checks == OFFICIAL_METHODS,
        "the official real-locale stage weakened its 146-test denominator",
    )
    require(
        not original.campaign.performance_suite_step(step),
        "the real-locale official stage selected a benchmark",
    )
    script = (ROOT / step.script).resolve()
    require(script.is_file(), "the frozen official CPython suite is missing")
    original.reject_performance_path(script)
    require(
        os.environ.get("LOCPATH") == EXPECTED_LOCPATH,
        "the genuine real locale disappeared before the official worker",
    )
    command = [
        sys.executable,
        "-B",
        "-c",
        original.SEALED_WORKER,
        str(ROOT),
        str(script),
        *step.arguments,
    ]
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    require(
        environment.get("LOCPATH") == EXPECTED_LOCPATH,
        "the official worker did not inherit its independently proven locale",
    )
    try:
        child = subprocess.run(
            command,
            cwd=str(ROOT),
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="backslashreplace",
            timeout=step.timeout_seconds,
            check=False,
            preexec_fn=original.campaign.restrict_process(
                memory_mib, step.timeout_seconds + 5
            ),
        )
    except subprocess.TimeoutExpired as error:
        raise AssertionError("the genuine official locale worker timed out") from error
    require(
        child.returncode == 0,
        "the genuine official locale worker failed: "
        + child.stderr[-6000:]
        + child.stdout[-3000:],
    )
    if step.artifact is not None:
        artifact = Path(step.artifact)
        require(artifact.is_file(), "the genuine official suite omitted its evidence")
        raw = artifact.read_bytes()
        if artifact.suffix == ".gz":
            require(
                len(raw) >= 10
                and raw[:2] == b"\x1f\x8b"
                and not raw[3] & 0x08
                and raw[4:8] == b"\x00\x00\x00\x00",
                "official locale evidence is not deterministic gzip",
            )
            payload = original.gzip.decompress(raw)
            document = json.loads(payload)
            require(original.canonical(document) == payload, "official evidence is not canonical")
        else:
            document = json.loads(raw)
    else:
        document = original.parse_child_json(child.stdout)
    require(isinstance(document, dict), "official locale output is not an object")
    failures = original.campaign.failure_values(document)
    require(not failures, "the real locale official worker reported actual failures")
    metrics = original.campaign.all_metric_values(document)
    require(
        any(item.get("value") == OFFICIAL_METHODS for item in metrics),
        "the real locale worker omitted its actual 146-test denominator",
    )
    require(
        document.get("module") == module
        and document.get("methods") == OFFICIAL_METHODS
        and document.get("passed") == OFFICIAL_METHODS
        and document.get("skipped") == 0,
        "the actual official locale stage did not pass all 146 tests",
    )
    return {
        "name": step.name,
        "passed": True,
        "status": "passed",
        "script": step.script,
        "command": command,
        "expected_checks": OFFICIAL_METHODS,
        "timeout_seconds": step.timeout_seconds,
        "memory_limit_mib": memory_mib,
        "core_dumps": "disabled",
        "candidate": module,
        "evidence": document,
        "evidence_sha256": original.digest_value(document),
        "holdout_accessed": False,
        "performance": "NOT MEASURED",
        "timing_performed": False,
    }


def validate_report_structure(report: dict[str, Any], module: str) -> None:
    require(isinstance(report, dict), "candidate campaign is not a JSON object")
    require(report.get("schema") == original.SCHEMA, "the original campaign schema changed")
    require(report.get("candidate") == module, "the campaign selected a foreign engine")
    require(report.get("pinned_cpython") == "3.14.6", "the pinned CPython oracle changed")
    require(report.get("mode") == "sealed-practice-only", "the campaign is not sealed")
    require(report.get("passed") is True, "the actual campaign did not pass")
    require(report.get("holdout_accessed") is False, "the campaign accessed a holdout")
    require(report.get("performance") == "NOT MEASURED", "the campaign ran a benchmark")
    require(report.get("timing_performed") is False, "the campaign sampled timing")
    goal = report.get("goal")
    require(
        isinstance(goal, dict)
        and goal.get("passed") is True
        and goal.get("actual_sha256") == original.campaign.GOAL_SHA256
        and goal.get("expected_sha256") == original.campaign.GOAL_SHA256,
        "the immutable user objective changed",
    )
    exclusions = report.get("excluded_steps")
    require(
        isinstance(exclusions, list)
        and {item.get("name") for item in exclusions if isinstance(item, dict)}
        == frozenset(original.EXCLUDED_NAMES)
        and len(exclusions) == len(original.EXCLUDED_NAMES),
        "the V4 campaign omitted or duplicated a performance exclusion",
    )
    steps = report.get("steps")
    require(
        isinstance(steps, list)
        and len(steps) == REQUIRED_STEP_COUNT
        and report.get("required_correctness_step_count") == REQUIRED_STEP_COUNT,
        "the complete locale-aware 22-stage campaign is incomplete",
    )
    names: set[str] = set()
    for row in steps:
        require(
            isinstance(row, dict)
            and row.get("passed") is True
            and row.get("status") in (None, "passed")
            and row.get("candidate") == module,
            "an actual locale-aware campaign stage failed or substituted an engine",
        )
        name = row.get("name")
        require(
            isinstance(name, str) and bool(name) and name not in names,
            "the locale campaign stage was unnamed or duplicated",
        )
        names.add(name)
        evidence = row.get("evidence")
        require(
            isinstance(evidence, dict)
            and row.get("evidence_sha256") == original.digest_value(evidence)
            and row.get("holdout_accessed") is False
            and row.get("performance") == "NOT MEASURED"
            and row.get("timing_performed") is False,
            "locale campaign evidence changed, was timed, or accessed hidden inputs",
        )
    require(original.REQUIRED_NAMES <= names, "the campaign dropped a required P0 stage")
    for name, denominator in (
        ("frozen-correctness-v2", 8244),
        ("frozen-correctness-v3", 44084),
        ("official-cpython-tests", OFFICIAL_METHODS),
        ("upstream-public-surface", 190),
        ("replacement-and-callback-adversarial", 8862),
        ("deep-replacement-and-callback-adversarial", 11266),
        ("isolated-crash-and-resource-safety", 254),
        ("isolated-depth-and-overflow-safety", 348),
    ):
        row = next((item for item in steps if item["name"] == name), None)
        require(
            isinstance(row, dict) and row.get("expected_checks") == denominator,
            "the locale-aware campaign weakened " + name,
        )
    official = next(item for item in steps if item["name"] == "official-cpython-tests")
    official_evidence = official["evidence"]
    require(
        official_evidence.get("module") == module
        and official_evidence.get("methods") == OFFICIAL_METHODS
        and official_evidence.get("passed") == OFFICIAL_METHODS
        and official_evidence.get("skipped") == 0,
        "the actual official 146-method locale result is false or incomplete",
    )
    full = next(item for item in steps if item["name"] == "full-unicode-plane")
    require(
        full.get("expected_checks") == 4_494_555
        and full["evidence"].get("correctness_checks") == 4_494_555,
        "the candidate weakened the complete 4,494,555-observation Unicode proof",
    )
    for name in (
        "independent-native-boundary-self-oracle",
        "independent-native-boundary-integrity",
        "independent-native-boundary-poison",
        "independent-native-boundary-compatibility",
    ):
        require(name in names, "the candidate omitted its independent native guard " + name)
    observability = next(
        (item for item in steps if item["name"] == "frozen-cross-family-observability"),
        None,
    )
    require(
        isinstance(observability, dict)
        and observability.get("expected_checks") == 479,
        "the actual candidate omitted its 479-case observability proof",
    )
    source_stage = next(item for item in steps if item["name"] == "from-scratch-static-audit")
    source = source_stage["evidence"]
    require(
        source.get("postfinal_schema") == audit_v5.SCHEMA
        and source.get("audit_source_sha256") == V5_SOURCE_SHA256
        and source.get("sealed_locale_provenance", {}).get("sha256") == LOCALE_SHA256
        and source.get("sealed_no_delegation_provenance", {}).get("sha256")
        == STRICT_REPORT_SHA256,
        "the campaign did not include the authentic V5 audit and real-locale proof",
    )
    edge = report.get("edge_oracle")
    require(
        isinstance(edge, dict)
        and edge.get("module") == module
        and edge.get("checks") == original.contract.EDGE_CHECKS
        and edge.get("category_count") == original.contract.EDGE_CATEGORIES
        and edge.get("failed") == 0,
        "the campaign edge proof is false or incomplete",
    )
    deep = report.get("deep_proof")
    require(
        isinstance(deep, dict)
        and deep.get("candidate_module") == module
        and deep.get("checks") == original.contract.FROZEN_CASES
        and deep.get("public_mismatches") == 0,
        "the campaign deep proof is false or incomplete",
    )
    require(
        report.get("native_artifacts") == edge.get("production_artifacts")
        and deep.get("native_artifacts") == edge.get("production_artifacts"),
        "the campaign substituted a candidate native engine",
    )


def output_path(path: Path, module: str) -> Path:
    result = ORIGINAL_OUTPUT_PATH(path, module)
    lowered = result.name.casefold()
    require(
        "postfinal" in lowered and "v4" in lowered,
        "the locale-aware V4 campaign cannot reuse an earlier report destination",
    )
    return result


@contextmanager
def current_locale_campaign() -> Iterator[None]:
    require(original.static_family_audit is ORIGINAL_STATIC_AUDIT, "the historical static audit was already substituted")
    require(original.generic_steps is ORIGINAL_GENERIC_STEPS, "the immutable generic campaign was already substituted")
    require(original.child_step is ORIGINAL_CHILD_STEP, "the sealed child runner was already substituted")
    require(original.validate_report_structure is ORIGINAL_VALIDATE_REPORT, "the historical report validator was already substituted")
    require(original.output_path is ORIGINAL_OUTPUT_PATH, "the exclusive output selector was already substituted")
    original.static_family_audit = static_family_audit
    original.generic_steps = generic_steps
    original.child_step = child_step
    original.validate_report_structure = validate_report_structure
    original.output_path = output_path
    try:
        yield
    finally:
        original.output_path = ORIGINAL_OUTPUT_PATH
        original.validate_report_structure = ORIGINAL_VALIDATE_REPORT
        original.child_step = ORIGINAL_CHILD_STEP
        original.generic_steps = ORIGINAL_GENERIC_STEPS
        original.static_family_audit = ORIGINAL_STATIC_AUDIT


def _synthetic_locale(source: Mapping[str, Any], strict: Mapping[str, Any]) -> dict[str, Any]:
    names = [f"OfficialLocaleTests.test_{index:03d}" for index in range(OFFICIAL_METHODS)]
    records = [{"test": name, "status": "passed", "skipped": 0} for name in names]
    roles = {}
    for family, module in (
        ("re", "re"),
        ("rust", "candidates.rust_candidate"),
        ("vm", "candidates.vm_candidate"),
        ("zig", "candidates.zig_candidate"),
    ):
        roles[family] = {
            "module": module,
            "methods": OFFICIAL_METHODS,
            "passed": OFFICIAL_METHODS,
            "skipped": 0,
            "failed": 0,
            "failures": 0,
            "crashes": 0,
            "timeouts": 0,
            "locale_caching_passed": True,
            "locale_compiled_passed": True,
            "holdout_accessed": False,
            "performance": "NOT MEASURED",
            "timing_performed": False,
            "records": copy.deepcopy(records),
        }
    return {
        "schema": LOCALE_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "source_path": LOCALE_SOURCE_RELATIVE,
        "source_sha256": LOCALE_SOURCE_SHA256,
        "audits": {
            "from_scratch": {
                "path": audit_v5.REPORT_RELATIVE,
                "postfinal_schema": audit_v5.SCHEMA,
                "sha256": V5_REPORT_SHA256,
                "source_path": audit_v5.SOURCE_RELATIVE,
                "source_sha256": V5_SOURCE_SHA256,
            },
            "no_delegation": {
                "path": strict_v5.REPORT_RELATIVE,
                "postfinal_schema": strict_v5.SCHEMA,
                "sha256": STRICT_REPORT_SHA256,
                "source_path": strict_v5.SOURCE_RELATIVE,
                "source_sha256": STRICT_SOURCE_SHA256,
            },
        },
        "locale_reference": {
            "status": "PASS",
            "genuine_locales": True,
            "compiled_locale_switch": True,
            "candidate_modules_loaded": False,
        },
        "locales": {
            "genuine": True,
            "holdout_accessed": False,
            "performance": "NOT MEASURED",
            "timing_performed": False,
            "iso88591": {"name": "en_US.iso88591"},
            "utf8": {"name": "en_US.utf8"},
        },
        "qualified_source_fingerprints": dict(strict["qualified_source_fingerprints"]),
        "native_elf_fingerprints": dict(strict["native_elf_fingerprints"]),
        "roles": roles,
        "holdout_accessed": False,
        "performance": "NOT MEASURED",
        "timing_performed": False,
    }


def self_test() -> dict[str, Any]:
    controls: list[dict[str, Any]] = []

    def check(name: str, value: Any) -> None:
        controls.append({"id": name, "passed": bool(value)})

    def rejected(name: str, action: Any) -> None:
        try:
            action()
        except (AssertionError, audit_v5.AuditV5Error, TypeError, ValueError, KeyError):
            check(name, True)
        else:
            check(name, False)

    with (
        mock.patch.object(subprocess, "Popen", side_effect=AssertionError("candidate workers forbidden in V4 self-test")) as worker,
        mock.patch.object(audit_v5, "audit", side_effect=AssertionError("production V5 audit forbidden")) as source_audit,
        mock.patch.object(strict_v5, "run_audit", side_effect=AssertionError("production strict V5 audit forbidden")) as strict_audit,
        mock.patch.object(audit_v5.previous.previous, "bounded_file", side_effect=AssertionError("production file reads forbidden")) as file_read,
    ):
        inherited = hardened.self_test()
        require(
            isinstance(inherited, Mapping)
            and inherited.get("schema") == hardened.SELF_TEST_SCHEMA
            and inherited.get("passed") is True
            and inherited.get("status") == "PASS"
            and inherited.get("failed") == 0
            and inherited.get("poison_control_count", 0) >= 43
            and inherited.get("inherited_campaign_control_count", 0) >= 46
            and inherited.get("candidate_processes_started") == 0
            and inherited.get("production_audits_run") == 0
            and inherited.get("historical_audits_run") == 0
            and inherited.get("production_report_reads") == 0,
            "the complete hardened V2 and immutable 22-stage safeguards failed",
        )
        for item in inherited["poison_controls"]:
            check("v2:" + item["id"], item["passed"] is True)
        check("preserve-all-46-original-campaign-controls", inherited["inherited_campaign_control_count"] >= 46)
        check("preserve-all-43-hardened-v2-controls", inherited["poison_control_count"] >= 43)
        check("preserve-exact-three-independent-candidates", set(original.MODULES) == {"candidates.rust_candidate", "candidates.vm_candidate", "candidates.zig_candidate"})
        check("require-all-146-official-tests", OFFICIAL_METHODS == 146)
        check("require-all-22-original-correctness-stages", REQUIRED_STEP_COUNT == 22)
        check("pin-v5-source-report-digest-shape", audit_v5.previous.previous.valid_sha256(V5_REPORT_SHA256))
        check("pin-v5-strict-report-digest-shape", audit_v5.previous.previous.valid_sha256(STRICT_REPORT_SHA256))
        check("pin-real-locale-proof-digest-shape", audit_v5.previous.previous.valid_sha256(LOCALE_SHA256))
        synthetic_strict = {
            "qualified_source_fingerprints": {
                f"candidates/synthetic/source-{index:02d}":
                hardened._synthetic_digest("source:" + str(index))
                for index in range(12)
            },
            "native_elf_fingerprints": {
                f"native-{index}": hardened._synthetic_digest("native:" + str(index))
                for index in range(5)
            },
        }
        synthetic = _synthetic_locale({}, synthetic_strict)
        validate_locale_document(synthetic)
        check("accept-only-four-real-locale-146-role-proofs", True)
        for module in original.MODULES:
            validate_locale_document(synthetic, module=module)
            check("accept-exact-real-locale-role:" + original.family_for(module), True)

        def poison_locale(label: str, change: Any) -> None:
            def run() -> None:
                poisoned = copy.deepcopy(synthetic)
                change(poisoned)
                validate_locale_document(poisoned)

            rejected(label, run)

        poison_locale("reject-false-locale-candidate-pass", lambda value: value["roles"]["rust"].update(passed=145))
        poison_locale("reject-old-144-official-denominator", lambda value: value["roles"]["vm"].update(methods=144, passed=144))
        poison_locale("reject-145-official-denominator", lambda value: value["roles"]["zig"].update(methods=145, passed=145))
        poison_locale("reject-restored-official-skip", lambda value: value["roles"]["rust"].update(skipped=1))
        poison_locale("reject-missing-real-locale-test-name", lambda value: value["roles"]["zig"]["records"].pop())
        poison_locale("reject-duplicated-real-locale-test-name", lambda value: value["roles"]["vm"]["records"].__setitem__(1, dict(value["roles"]["vm"]["records"][0])))
        poison_locale("reject-foreign-candidate-module", lambda value: value["roles"]["rust"].update(module="candidates.zig_candidate"))
        poison_locale("reject-historical-v4-source-audit", lambda value: value["audits"]["from_scratch"].update(postfinal_schema="rebar-postfinal-from-scratch-audit-v4"))
        poison_locale("reject-historical-v4-strict-audit", lambda value: value["audits"]["no_delegation"].update(postfinal_schema="rebar-postfinal-no-delegation-audit-v4"))
        poison_locale("reject-substituted-v5-source-report", lambda value: value["audits"]["from_scratch"].update(sha256="0" * 64))
        poison_locale("reject-substituted-v5-strict-report", lambda value: value["audits"]["no_delegation"].update(sha256="0" * 64))
        poison_locale("reject-substituted-locale-producer", lambda value: value.update(source_sha256="0" * 64))
        poison_locale("reject-false-genuine-locales", lambda value: value["locales"].update(genuine=False))
        poison_locale("reject-missing-iso88591", lambda value: value["locales"].pop("iso88591"))
        poison_locale("reject-uncompiled-locale-switch", lambda value: value["locale_reference"].update(compiled_locale_switch=False))
        poison_locale("reject-candidate-loaded-in-reference", lambda value: value["locale_reference"].update(candidate_modules_loaded=True))
        poison_locale("reject-omitted-native-role", lambda value: value["native_elf_fingerprints"].pop("native-0"))
        poison_locale("reject-omitted-qualified-source", lambda value: value["qualified_source_fingerprints"].pop("candidates/synthetic/source-00"))
        poison_locale("reject-locale-timing", lambda value: value.update(timing_performed=True))
        poison_locale("reject-locale-performance", lambda value: value.update(performance="MEASURED"))
        poison_locale("reject-locale-hidden-access", lambda value: value.update(holdout_accessed=True))

        for label, value in (
            ("reject-private-locale-proof-path", "sealed/private/cases.json"),
            ("reject-hidden-locale-proof-path", "sealed/holdout/cases.json"),
            ("reject-final-locale-proof-path", "sealed/final/cases.json"),
            ("reject-benchmark-locale-proof-path", "benchmarks/cases.json"),
            ("reject-foreign-locale-proof-path", "oracle/cpython-3.14.6/evidence/foreign.json"),
            ("reject-absolute-locale-proof-path", "/" + LOCALE_RELATIVE),
            ("reject-traversing-locale-proof-path", "oracle/cpython-3.14.6/evidence/../postfinal-locale-v1-all.json"),
            ("reject-noncanonical-locale-proof-path", "oracle//cpython-3.14.6/evidence/postfinal-locale-v1-all.json"),
            ("reject-nontext-locale-proof-path", 5),
        ):
            rejected(label, lambda target=value: _valid_relative(target, LOCALE_RELATIVE, "real-locale proof"))
        check("accept-only-exact-real-locale-proof-path", _valid_relative(LOCALE_RELATIVE, LOCALE_RELATIVE, "real-locale proof") == LOCALE_RELATIVE)
        check("never-start-candidate-process", worker.call_count == 0)
        check("never-run-v5-source-audit", source_audit.call_count == 0)
        check("never-run-v5-strict-audit", strict_audit.call_count == 0)
        check("never-read-production-report-or-file", file_read.call_count == 0)
        check("never-replace-immutable-static-audit", original.static_family_audit is ORIGINAL_STATIC_AUDIT)
        check("never-replace-immutable-child-worker", original.child_step is ORIGINAL_CHILD_STEP)
        check("never-replace-immutable-report-validator", original.validate_report_structure is ORIGINAL_VALIDATE_REPORT)

    names = [item["id"] for item in controls]
    require(
        len(names) == len(set(names))
        and len(controls) >= 43
        and all(item.get("passed") is True for item in controls),
        "the real-locale campaign weakened or duplicated a synthetic safeguard",
    )
    return {
        "schema": SELF_TEST_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "python": "3.14.6",
        "synthetic_only": True,
        "inherited_campaign_schema": original.SELF_TEST_SCHEMA,
        "inherited_campaign_control_count": inherited["inherited_campaign_control_count"],
        "inherited_hardened_schema": hardened.SELF_TEST_SCHEMA,
        "inherited_hardened_control_count": inherited["poison_control_count"],
        "candidate_modules": list(original.MODULES),
        "actual_planned_step_counts": inherited["actual_planned_step_counts"],
        "official_method_count": OFFICIAL_METHODS,
        "poison_control_count": len(controls),
        "poison_controls": controls,
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


def main(argv: list[str] | None = None) -> int:
    args = original.parse_arguments(argv)
    if args.self_test:
        require(
            args.module is None
            and args.edge_oracle is None
            and args.deep_proof is None
            and args.output is None,
            "the locale-aware V4 self-test cannot run candidates or create reports",
        )
        print(json.dumps(self_test(), ensure_ascii=True, sort_keys=True), flush=True)
        return 0
    with current_locale_campaign():
        return original.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
