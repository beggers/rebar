#!/usr/bin/env python3
"""Run frozen Python-visible tracing and native safety on independent engines.

The 479 original observations, two pinned Python references, and the original
13 poisoned regex entry points are never altered.  A candidate must first
prove its own passing 223,198-case edge result and 393-case public contract.
Its 34 malformed-binding controls exercise only its own actual native bridge.
Evidence is deterministic, exclusive-create gzip; self-tests write only /tmp.
"""

from __future__ import annotations

import argparse
import collections
import contextlib
import copy
import gzip
import hashlib
import importlib
import inspect
import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from tools import rust_v7_observability_oracle as frozen
from tools import rust_v8_multi_candidate_contract as deep


SCHEMA = "rebar-v8-multi-candidate-observability-v1"
RUNNER = Path(__file__).resolve()
ROOT = deep.ROOT
EVIDENCE = ROOT / "candidates" / "evidence"
OBSERVABILITY_SOURCE = ROOT / "tools" / "rust_v7_observability_oracle.py"
OBSERVABILITY_SOURCE_SHA256 = (
    "931da02cbc819ba2ae9fed4fcf7bcd676e729c767fb804c9fc5be0429f76c4f7"
)
DEEP_RUNNER = ROOT / "tools" / "rust_v8_multi_candidate_contract.py"
DEEP_RUNNER_SHA256 = (
    "167f9d9114f95cd9c9821465339264f8b6eca9bf7f70b84774f4108f62f11a70"
)
MANIFEST_SHA256 = (
    "ef6d102b214e9dfc14e88e13e37fec2ebad633024a2349181ce062e6a11e59fa"
)
FROZEN_REFERENCE_SHA256 = (
    "6e3593b963036e2381569475cac390ccbb7bc6dbc8358acda578fcbcb7e0642e"
)
FROZEN_ARCHIVE_SHA256 = {
    "stdlib-a": "66ac1f8073da1b8d43370be000bdb26c55a11eeadd65f1afda46875ea27b3ba9",
    "stdlib-b": "820b4216721ef2a0de6cdc4350d7f926cdab10e8114154336d2132e557ea0ab0",
    "candidate": "3c272d15c9bd4636f5818739709fa36f6dd722c9d14f59e15d02131b5357948b",
    "private-binders": "c6a54bc29e8d10cada3a1aac9a9730b804e2ad9af28055ba25620ec3d01c78e6",
    "rejected-iterator-control": (
        "e0e5d3abe4f252d0b76b373fc7847ecabf39b31ae4b08f10b142c324dff04edf"
    ),
}
CASE_COUNT = 479
BINDER_COUNT = 34
GUARD_COUNT = 13
SUPPORTED = {
    name: spec
    for name, spec in deep.SPECS.items()
    if spec.family in {"RUST", "ZIG", "C"}
}
OUTPUT_SLUG = {"RUST": "rust", "ZIG": "zig", "C": "vm"}
BOUND_BINDERS = (
    "bound_search",
    "bound_match",
    "bound_fullmatch",
    "bound_findall",
    "bound_literal_findall",
    "bound_finditer",
    "bound_scanner",
    "bound_split",
    "bound_sub",
    "bound_subn",
)
C_MODULE_BINDERS = (
    "build", "match", "collect", "configure", "pattern_type", "escape"
)
C_PATTERN_BINDERS = ("search", "match", "fullmatch", "findall", "finditer")
MALFORMED_SHAPES = ("no-arguments", "one-argument", "unexpected-keyword")


class IndependentEngineGuard(AssertionError):
    """A selected candidate tried to import another matching engine."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def verify_runtime() -> None:
    require(tuple(sys.version_info[:3]) == frozen.PINNED, "requires pinned CPython 3.14.6")
    require(sys.implementation.name == "cpython", "requires genuine CPython")
    require(
        Path(sys.executable).resolve() == deep.PINNED_EXECUTABLE.resolve(),
        "requires the exact pinned CPython executable",
    )
    require(
        os.environ.get("PYTHONDONTWRITEBYTECODE") == "1",
        "PYTHONDONTWRITEBYTECODE=1 is mandatory",
    )
    path_entries = os.environ.get("PYTHONPATH", "").split(os.pathsep)
    require(
        "." in path_entries or str(ROOT) in path_entries,
        "PYTHONPATH must identify the exact project root",
    )


def frozen_history() -> dict[str, Any]:
    verify_runtime()
    require(
        Path(frozen.__file__).resolve() == OBSERVABILITY_SOURCE,
        "a different public observability suite was imported",
    )
    require(
        deep.sha256_path(OBSERVABILITY_SOURCE) == OBSERVABILITY_SOURCE_SHA256,
        "the immutable 479-case source changed",
    )
    require(
        Path(deep.__file__).resolve() == DEEP_RUNNER,
        "a different multi-candidate deep runner was imported",
    )
    require(
        deep.sha256_path(DEEP_RUNNER) == DEEP_RUNNER_SHA256,
        "the immutable multi-candidate deep runner changed",
    )
    cases = frozen.build_cases()
    require(len(cases) == CASE_COUNT, "the frozen 479-case denominator changed")
    require(
        frozen.value_digest(cases) == frozen.FROZEN_FIXTURE_SHA256,
        "the frozen 479-case fixture or seed changed",
    )
    manifest_path = EVIDENCE / frozen.ARCHIVE_NAMES["manifest"]
    require(
        deep.sha256_path(manifest_path) == MANIFEST_SHA256,
        "the frozen passing observability manifest changed",
    )
    manifest = frozen.read_report(manifest_path)
    require(manifest.get("status") == "PASS", "the historical manifest is not passing")
    require(manifest.get("checks") == CASE_COUNT, "the historical case count changed")
    require(manifest.get("self_oracle_checks") == CASE_COUNT, "the historical self-control changed")
    require(manifest.get("self_oracle_failures") == 0, "the historical references disagree")
    require(manifest.get("candidate_failures") == 0, "the historical candidate was not passing")
    require(manifest.get("private_binder_checks") == BINDER_COUNT, "the frozen native count changed")
    require(manifest.get("private_binder_failures") == [], "a frozen native failure was hidden")
    require(manifest.get("forbidden_regex_guards") == GUARD_COUNT, "the frozen regex guards changed")
    require(
        manifest.get("expected_observation_sha256") == FROZEN_REFERENCE_SHA256,
        "the historical CPython reference changed",
    )
    require(
        manifest.get("actual_observation_sha256") == FROZEN_REFERENCE_SHA256,
        "the historical passing candidate observations changed",
    )
    archives: dict[str, dict[str, Any]] = {}
    recorded = manifest.get("isolated_worker_archives")
    require(isinstance(recorded, dict), "historical isolated-worker evidence is missing")
    require(set(recorded) == set(FROZEN_ARCHIVE_SHA256), "historical archive roles changed")
    for role, fingerprint in FROZEN_ARCHIVE_SHA256.items():
        path = EVIDENCE / frozen.ARCHIVE_NAMES[role]
        expected_relative = path.relative_to(ROOT).as_posix()
        require(deep.sha256_path(path) == fingerprint, f"historical {role} archive changed")
        require(
            recorded[role] == {"path": expected_relative, "sha256": fingerprint},
            f"historical {role} manifest provenance changed",
        )
        archives[role] = frozen.read_report(path)
    for role in ("stdlib-a", "stdlib-b", "candidate"):
        validate_public_worker(archives[role], role)
    require(
        archives["stdlib-a"]["observations"]
        == archives["stdlib-b"]["observations"],
        "historical independent pinned references disagree",
    )
    require(
        archives["candidate"]["observations"]
        == archives["stdlib-a"]["observations"],
        "historical passing public candidate differs from the reference",
    )
    private = archives["private-binders"]
    require(private.get("status") == "PASS", "historical native binder safety failed")
    require(private.get("checks") == BINDER_COUNT, "historical native binder count changed")
    require(private.get("failures") == [], "historical native binder errors were hidden")
    require(
        len(private.get("observations", ())) == BINDER_COUNT,
        "historical native binder observations are incomplete",
    )
    require(
        private.get("observations")
        == archives["candidate"].get("private_binder_observations"),
        "historical Rust native controls differ from their complete archived worker",
    )
    rejected = archives["rejected-iterator-control"]
    require(
        rejected == frozen.rejected_iterator_report(
            archives["stdlib-a"], archives["candidate"]
        ),
        "the historical implementation-private iterator control changed",
    )
    return {"manifest": manifest, "archives": archives}


def validate_public_worker(report: Any, role: str) -> None:
    require(isinstance(report, dict), f"{role} did not return an object")
    expected = {
        "schema": frozen.SCHEMA,
        "role": role,
        "python": "3.14.6",
        "seed": frozen.SEED,
        "fixture_sha256": frozen.FROZEN_FIXTURE_SHA256,
        "checks": CASE_COUNT,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    for name, value in expected.items():
        require(report.get(name) == value, f"{role} changed frozen {name}")
    rows = report.get("observations")
    require(isinstance(rows, list) and len(rows) == CASE_COUNT, f"{role} lost public observations")
    case_ids = [case["id"] for case in frozen.build_cases()]
    require([row.get("id") for row in rows] == case_ids, f"{role} reordered frozen cases")
    require(
        report.get("observation_sha256") == frozen.value_digest(rows),
        f"{role} changed the complete frozen observation digest",
    )
    for row in rows:
        require(
            row.get("sha256") == frozen.value_digest(row.get("observation")),
            f"{role} changed observation {row.get('id')}",
        )
    expected_families = dict(
        sorted(collections.Counter(case["family"] for case in frozen.build_cases()).items())
    )
    require(report.get("family_counts") == expected_families, f"{role} changed frozen families")
    if role in ("stdlib-a", "stdlib-b"):
        require(
            report.get("observation_sha256") == FROZEN_REFERENCE_SHA256,
            f"{role} differs from the archived pinned Python reference",
        )


def checked_gzip(path: Path, *, parent: Path, description: str) -> tuple[bytes, Any]:
    require(not path.is_symlink(), f"{description} cannot be a symlink")
    resolved = path.resolve()
    require(resolved.parent == parent.resolve(), f"{description} escaped its directory")
    require(resolved.name.endswith(".json.gz"), f"{description} is not gzip evidence")
    try:
        raw = resolved.read_bytes()
    except OSError as error:
        raise AssertionError(f"{description} is unavailable") from error
    require(len(raw) >= 10 and raw[:2] == b"\x1f\x8b", f"{description} is not gzip")
    require(not raw[3] & 0x08, f"{description} contains a nondeterministic filename")
    require(raw[4:8] == b"\x00\x00\x00\x00", f"{description} timestamp is not frozen")
    try:
        payload = gzip.decompress(raw)
        document = json.loads(payload)
    except (OSError, ValueError, EOFError, UnicodeError) as error:
        raise AssertionError(f"{description} cannot be decoded") from error
    require(frozen.canonical(document) == payload, f"{description} is not canonical JSON")
    return raw, document


def validate_deep_document(
    document: Any,
    spec: deep.CandidateSpec,
    edge: dict[str, Any],
    archive_sha256: str,
    source_path: Path,
) -> dict[str, Any]:
    require(isinstance(document, dict), "the explicit deep proof is not an object")
    expected = {
        "schema": deep.FROZEN_SCHEMA,
        "status": "PASS",
        "python": "3.14.6",
        "seed": deep.FROZEN_SEED,
        "seeded_case_count": deep.FROZEN_SEEDED_CASES,
        "checks": deep.FROZEN_CASES,
        "fixture_sha256": deep.FROZEN_FIXTURE_SHA256,
        "suite_path": "tools/rust_v8_deep_contract_oracle.py",
        "suite_sha256": deep.FROZEN_SUITE_SHA256,
        "reference_a_sha256": deep.FROZEN_REFERENCE_SHA256,
        "reference_b_sha256": deep.FROZEN_REFERENCE_SHA256,
        "candidate_sha256": deep.FROZEN_REFERENCE_SHA256,
        "public_mismatch_count": 0,
        "forbidden_regex_guards": GUARD_COUNT,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    for key, value in expected.items():
        require(document.get(key) == value, f"deep proof changed {key}")
    require(document.get("stdlib_vs_stdlib_mismatches") == [], "deep Python references disagree")
    require(document.get("public_mismatches") == [], "deep proof hides public failures")
    require(
        document.get("public_mismatch_family_counts") == {},
        "deep proof conceals a failing case family",
    )
    actual_family = document.get("candidate_family", spec.family)
    actual_module = document.get("candidate_module", spec.module)
    require(actual_family == spec.family, "deep proof names a different candidate family")
    require(actual_module == spec.module, "deep proof names a different candidate module")
    require(
        document.get("native_artifacts") == edge["production_artifacts"],
        "deep proof authorizes different source or native artifacts",
    )
    edge_link = document.get("edge_oracle")
    require(isinstance(edge_link, dict), "deep proof omitted its exact edge authorization")
    require(
        edge_link.get("archive_sha256") == edge["archive_sha256"],
        "deep proof is bound to a different edge evidence archive",
    )
    require(edge_link.get("checks") == deep.EDGE_CHECKS, "deep proof changed edge check count")
    require(edge_link.get("failed") == 0, "deep proof contains a failing edge candidate")
    require(
        edge_link.get("candidate_sha256") == deep.EDGE_REFERENCE_SHA256,
        "deep proof changed its actual edge answers",
    )
    require(
        edge_link.get("reference_sha256") == deep.EDGE_REFERENCE_SHA256,
        "deep proof changed its pinned edge reference",
    )
    if "module" in edge_link:
        require(edge_link["module"] == spec.module, "deep-linked edge changed candidate module")
    if "family" in edge_link:
        require(edge_link["family"] == spec.family, "deep-linked edge changed candidate family")

    deep_suite = deep.load_frozen_suite()
    baseline, _ = deep.original_failure(deep_suite)
    case_ids = [case["id"] for case in deep_suite.build_cases()]
    for role, expected_role in (
        ("reference", "stdlib-a"),
        ("reference_independent_repeat", "stdlib-b"),
        ("candidate", "candidate"),
    ):
        report = document.get(role)
        require(isinstance(report, dict), f"deep proof omitted complete {role} observations")
        require(report.get("role") == expected_role, f"deep {role} provenance changed")
        require(report.get("checks") == deep.FROZEN_CASES, f"deep {role} denominator changed")
        require(
            report.get("fixture_sha256") == deep.FROZEN_FIXTURE_SHA256,
            f"deep {role} fixture changed",
        )
        rows = report.get("observations")
        require(isinstance(rows, list) and len(rows) == deep.FROZEN_CASES, f"deep {role} rows missing")
        require([row.get("id") for row in rows] == case_ids, f"deep {role} cases reordered")
        require(
            report.get("observation_sha256") == deep_suite.digest(rows),
            f"deep {role} digest changed",
        )
        for row in rows:
            require(
                row.get("sha256") == deep_suite.digest(row.get("observation")),
                f"deep {role} row digest changed: {row.get('id')}",
            )
    require(
        document["reference"]["observations"] == baseline["reference"]["observations"],
        "deep reference differs from the immutable 393 answers",
    )
    require(
        document["reference_independent_repeat"]["observations"]
        == baseline["reference_independent_repeat"]["observations"],
        "independent deep reference differs from its immutable answers",
    )
    require(
        not deep_suite.mismatches(
            document["reference"]["observations"], document["candidate"]["observations"]
        ),
        "deep proof conceals a genuine public mismatch",
    )
    candidate = document["candidate"]
    require(
        candidate.get("native_artifacts") == edge["production_artifacts"],
        "deep candidate loaded different native production artifacts",
    )
    guards = document.get("guard_observations")
    require(isinstance(guards, list) and len(guards) == GUARD_COUNT, "deep regex guards missing")
    cross = document.get("cross_engine_guard_count")
    if spec.family != "RUST":
        require(isinstance(cross, int) and cross >= 10, "deep foreign-engine guards missing")
        require(
            len(document.get("cross_engine_guard_observations", ())) == cross,
            "deep foreign-engine guard observations are incomplete",
        )
    diagnostics = deep_suite.diagnostic_differences(
        document["reference"]["implementation_private_gc_diagnostics"],
        candidate["implementation_private_gc_diagnostics"],
    )
    require(
        document.get("implementation_private_gc_topology_difference_count") == len(diagnostics),
        "deep proof hides implementation-private collector diagnostics",
    )
    require(
        document.get("implementation_private_gc_topology_differences") == diagnostics,
        "deep private diagnostics were modified",
    )
    return {
        "schema": deep.FROZEN_SCHEMA,
        "path": str(source_path.resolve()),
        "archive_sha256": deep.require_sha256(archive_sha256, "deep proof archive"),
        "status": "PASS",
        "checks": deep.FROZEN_CASES,
        "seed": deep.FROZEN_SEED,
        "fixture_sha256": deep.FROZEN_FIXTURE_SHA256,
        "reference_sha256": deep.FROZEN_REFERENCE_SHA256,
        "candidate_sha256": deep.FROZEN_REFERENCE_SHA256,
        "candidate_module": spec.module,
        "candidate_family": spec.family,
        "edge_archive_sha256": edge["archive_sha256"],
        "native_artifacts": edge["production_artifacts"],
    }


def read_deep_proof(
    path: Path, spec: deep.CandidateSpec, edge: dict[str, Any]
) -> dict[str, Any]:
    require(path.name.startswith("RUST-V8-DEEP-CONTRACT-"), "deep proof has an unapproved name")
    raw, document = checked_gzip(
        path, parent=deep.AUDITS, description="candidate-specific 393-case deep proof"
    )
    return validate_deep_document(
        document, spec, edge, hashlib.sha256(raw).hexdigest(), path.resolve()
    )


def require_native_callable(function: Any, owner: Any, label: str) -> None:
    require(inspect.isbuiltin(function), f"{label} is not a real native built-in binding")
    require(getattr(function, "__self__", None) is owner, f"{label} does not belong to its engine")
    require(type(function).__module__ == "builtins", f"{label} is not a CPython native binding")
    require(callable(function), f"{label} is not callable")


def binder_ids(spec: deep.CandidateSpec) -> tuple[str, ...]:
    if spec.family in {"RUST", "ZIG"}:
        result = [
            f"private-native-binder/{name}/{shape}"
            for name in BOUND_BINDERS
            for shape in MALFORMED_SHAPES
        ]
        if spec.family == "RUST":
            result.extend(
                (
                    "private-native-binder/bind/missing",
                    "private-native-binder/bind/one-argument",
                    "private-native-binder/bind/noncallable",
                    "private-native-binder/bind/vectorcall-success",
                )
            )
        else:
            result.extend(
                f"private-native-binder/compile/{shape}"
                for shape in MALFORMED_SHAPES
            )
            result.append("private-native-binder/compile/native-success")
    elif spec.family == "C":
        result = [
            f"private-native-binder/module/{name}/{shape}"
            for name in C_MODULE_BINDERS
            for shape in MALFORMED_SHAPES
        ]
        result.extend(
            f"private-native-binder/pattern/{name}/{shape}"
            for name in C_PATTERN_BINDERS
            for shape in MALFORMED_SHAPES
        )
        result.append("private-native-binder/pattern/search/native-success")
    else:
        raise AssertionError("observability requires a genuinely native candidate")
    require(len(result) == BINDER_COUNT, "native binder denominator is not exactly 34")
    require(len(set(result)) == BINDER_COUNT, "native binder controls repeat an identity")
    return tuple(result)


def binder_metadata(function: Any, owner_label: str) -> dict[str, Any]:
    doc = getattr(function, "__doc__", None)
    require(doc is None or isinstance(doc, str), "native binding documentation is malformed")
    signature = getattr(function, "__text_signature__", None)
    require(signature is None or isinstance(signature, str), "native text signature is malformed")
    return {
        "native_owner": owner_label,
        "callable_type": type(function).__name__,
        "callable_name": getattr(function, "__name__", None),
        "documentation": doc,
        "documentation_sha256": (
            hashlib.sha256(doc.encode("utf-8")).hexdigest() if doc is not None else None
        ),
        "text_signature": signature,
    }


def malformed_action(function: Any, shape: str) -> Any:
    if shape == "no-arguments":
        return function()
    if shape == "one-argument":
        return function(None)
    if shape == "unexpected-keyword":
        return function(unexpected_native_keyword=1)
    raise AssertionError("unknown native malformed-binder shape")


def native_recovery(module: Any) -> dict[str, Any]:
    result = frozen.attempted(lambda: module.fullmatch("a", "a"))
    require(result.get("status") == "value", "engine failed to recover after a native call")
    value = result.get("value")
    require(isinstance(value, dict) and value.get("span") == [0, 1], "native recovery returned a false match")
    return result


def record_malformed(
    observations: list[dict[str, Any]],
    failures: list[dict[str, Any]],
    identity: str,
    function: Any,
    owner: Any,
    owner_label: str,
    shape: str,
    module: Any,
) -> None:
    require_native_callable(function, owner, identity)
    result = frozen.attempted(lambda: malformed_action(function, shape))
    recovery = native_recovery(module)
    passed = (
        result.get("status") == "error"
        and result.get("error", {}).get("type") == "TypeError"
    )
    row = {
        "id": identity,
        "passed": passed,
        "result": result,
        "recovery": recovery,
        **binder_metadata(function, owner_label),
    }
    observations.append(row)
    if not passed:
        failures.append(row)


def zig_native_compile_success(bridge: Any) -> dict[str, Any]:
    compiled = bridge.compile(b"a", 0, True)
    require(isinstance(compiled, tuple) and len(compiled) == 4, "Zig native compiler returned invalid metadata")
    handle, groups, flags, names = compiled
    require(isinstance(handle, int) and handle != 0, "Zig native compiler did not return a handle")
    try:
        require(groups == 0, "Zig native compiler changed literal group count")
        require(isinstance(flags, int), "Zig native compiler returned invalid flags")
        require(isinstance(names, dict) and not names, "Zig native compiler invented groups")
        return {"compiled": True, "groups": groups, "names": names}
    finally:
        bridge.free(handle)


def family_private_binder_safety(
    module: Any, spec: deep.CandidateSpec, bridge: Any
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    require(
        getattr(bridge, "__name__", None) == spec.native_module,
        "private binder controls loaded another candidate's native bridge",
    )
    observations: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    if spec.family == "ZIG":
        for name in BOUND_BINDERS:
            function = getattr(bridge, name, None)
            for shape in MALFORMED_SHAPES:
                record_malformed(
                    observations,
                    failures,
                    f"private-native-binder/{name}/{shape}",
                    function,
                    bridge,
                    spec.native_module,
                    shape,
                    module,
                )
        function = getattr(bridge, "compile", None)
        for shape in MALFORMED_SHAPES:
            record_malformed(
                observations,
                failures,
                f"private-native-binder/compile/{shape}",
                function,
                bridge,
                spec.native_module,
                shape,
                module,
            )
        require_native_callable(function, bridge, "private-native-binder/compile/native-success")
        result = frozen.attempted(lambda: zig_native_compile_success(bridge))
        row = {
            "id": "private-native-binder/compile/native-success",
            "passed": (
                result.get("status") == "value"
                and result.get("value", {}).get("compiled") is True
            ),
            "result": result,
            "recovery": native_recovery(module),
            **binder_metadata(function, spec.native_module),
        }
        observations.append(row)
        if not row["passed"]:
            failures.append(row)
    elif spec.family == "C":
        for name in C_MODULE_BINDERS:
            function = getattr(bridge, name, None)
            for shape in MALFORMED_SHAPES:
                record_malformed(
                    observations,
                    failures,
                    f"private-native-binder/module/{name}/{shape}",
                    function,
                    bridge,
                    spec.native_module,
                    shape,
                    module,
                )
        compiled = module.compile("a")
        require(isinstance(compiled, module.Pattern), "C native binder received a false Pattern")
        for name in C_PATTERN_BINDERS:
            function = getattr(compiled, name, None)
            for shape in MALFORMED_SHAPES:
                record_malformed(
                    observations,
                    failures,
                    f"private-native-binder/pattern/{name}/{shape}",
                    function,
                    compiled,
                    "re.Pattern",
                    shape,
                    module,
                )
        function = getattr(compiled, "search", None)
        identity = "private-native-binder/pattern/search/native-success"
        require_native_callable(function, compiled, identity)
        result = frozen.attempted(lambda: function("a"))
        row = {
            "id": identity,
            "passed": (
                result.get("status") == "value"
                and result.get("value", {}).get("span") == [0, 1]
            ),
            "result": result,
            "recovery": native_recovery(module),
            **binder_metadata(function, "re.Pattern"),
        }
        observations.append(row)
        if not row["passed"]:
            failures.append(row)
    else:
        raise AssertionError("the frozen Rust controls must not be replaced")
    validate_binder_observations(observations, failures, spec)
    return observations, failures


def validate_binder_observations(
    observations: Any, failures: Any, spec: deep.CandidateSpec
) -> None:
    require(isinstance(observations, list), "native binder observations are missing")
    require(len(observations) == BINDER_COUNT, "native binder denominator is not 34")
    require(
        tuple(row.get("id") for row in observations) == binder_ids(spec),
        "native binder identities were dropped, changed, or reordered",
    )
    require(isinstance(failures, list), "native binder failures are missing")
    actual_failures = [row for row in observations if row.get("passed") is not True]
    require(failures == actual_failures, "native binder failures were concealed")
    for row in observations:
        require(isinstance(row.get("result"), dict), "a native binder result is missing")
        recovery = row.get("recovery")
        require(
            isinstance(recovery, dict) and recovery.get("status") == "value",
            "a native binder did not prove independent engine recovery",
        )
        if spec.family != "RUST":
            require(
                row.get("native_owner") in {spec.native_module, "re.Pattern"},
                "a family-private binder belongs to another candidate",
            )
            require(
                row.get("callable_type") in {"builtin_function_or_method", "builtin_method"},
                "a private native binder was replaced by a Python wrapper",
            )
            doc = row.get("documentation")
            require(doc is None or isinstance(doc, str), "a native binder documentation value is fake")
            expected_doc = hashlib.sha256(doc.encode("utf-8")).hexdigest() if doc is not None else None
            require(
                row.get("documentation_sha256") == expected_doc,
                "a native binder documentation value or hash was forged",
            )


def add_cross_guard() -> None:
    frozen.GuardSignal = IndependentEngineGuard


def evaluate_worker(
    role: str,
    spec: deep.CandidateSpec,
    edge_path: Path | None,
    deep_path: Path | None,
) -> dict[str, Any]:
    history = frozen_history()
    if role in {"stdlib-a", "stdlib-b"}:
        require(edge_path is None and deep_path is None, "reference cannot load production proofs")
        report = frozen.worker(role, None)
        validate_public_worker(report, role)
        require(
            report["observations"] == history["archives"][role]["observations"],
            "fresh reference differs from its immutable historical archive",
        )
        return report
    add_cross_guard()
    if role == "guard-self-test":
        require(edge_path is None and deep_path is None, "guard self-test cannot import candidates")
        with deep.active_cross_engine_guard(frozen, spec) as isolation:
            guards = frozen.install_regex_guards()
            regex = frozen.audit_regex_guards(guards)
            cross = deep.audit_cross_engine_guards(isolation)
            require(len(regex) == GUARD_COUNT, "self-test lost a frozen regex guard")
            require(len(cross) >= 10, "self-test lost a cross-engine guard")
            require(
                regex == frozen.audit_regex_guards(guards),
                "self-test changed a frozen regex guard",
            )
            return {
                "schema": SCHEMA,
                "role": role,
                "python": "3.14.6",
                "seed": frozen.SEED,
                "fixture_sha256": frozen.FROZEN_FIXTURE_SHA256,
                "checks": CASE_COUNT,
                "forbidden_regex_guards": len(regex),
                "forbidden_regex_guard_observations": regex,
                "cross_engine_guard_count": len(cross),
                "cross_engine_guard_observations": cross,
                "candidate_module": spec.module,
                "candidate_family": spec.family,
                "performance": "NOT MEASURED",
                "holdout": "NOT ACCESSED",
            }
    require(role in {"candidate", "poison"}, "unknown isolated observability worker")
    require(edge_path is not None and deep_path is not None, "candidate requires both passing proofs")
    authorized, edge, _ = deep.read_edge_proof(edge_path, spec)
    contract = read_deep_proof(deep_path, spec, edge)
    with deep.active_cross_engine_guard(frozen, spec) as isolation:
        module = importlib.import_module(spec.module)
        artifacts = deep.production_provenance(module, spec, authorized, isolation)
        require(artifacts == edge["production_artifacts"], "candidate loaded unproven artifacts")
        cross_before = deep.audit_cross_engine_guards(isolation)
        frozen.importlib = deep.FrozenEvaluatorImports(module)
        frozen.production_provenance = (
            lambda candidate, expected=None: deep.production_provenance(
                candidate, spec, authorized, isolation
            )
        )
        if spec.family in {"ZIG", "C"}:
            bridge = sys.modules.get(spec.native_module)
            require(bridge is not None, "the selected candidate native bridge was not loaded")
            frozen.private_binder_safety = lambda candidate: family_private_binder_safety(
                candidate, spec, bridge
            )
        if role == "poison":
            guards = frozen.install_regex_guards()
            before = frozen.audit_regex_guards(guards)
            search = frozen.attempted(lambda: module.search("(?P<letter>a)", "a"))
            replacement = frozen.attempted(lambda: module.sub("a", "x", "aba"))
            after = frozen.audit_regex_guards(guards)
            cross_after = deep.audit_cross_engine_guards(isolation)
            require(before == after, "native execution removed a standard-library regex guard")
            require(cross_before == cross_after, "native execution removed a foreign-engine guard")
            require(search.get("status") == "value", "candidate failed native poisoned search")
            require(
                replacement == {"status": "value", "value": "xbx"},
                "candidate failed native poisoned substitution",
            )
            return {
                "schema": SCHEMA,
                "role": role,
                "python": "3.14.6",
                "seed": frozen.SEED,
                "fixture_sha256": frozen.FROZEN_FIXTURE_SHA256,
                "checks": CASE_COUNT,
                "forbidden_regex_guards": len(after),
                "forbidden_regex_guard_observations": after,
                "cross_engine_guard_count": len(cross_after),
                "cross_engine_guard_observations": cross_after,
                "candidate_module": spec.module,
                "candidate_family": spec.family,
                "native_artifacts": artifacts,
                "edge_oracle": edge,
                "deep_proof": contract,
                "native_under_poison": {"search": search, "sub": replacement},
                "performance": "NOT MEASURED",
                "holdout": "NOT ACCESSED",
            }
        report = frozen.worker("candidate", None)
        cross_after = deep.audit_cross_engine_guards(isolation)
        require(cross_before == cross_after, "observability candidate removed an engine guard")
        report.update(
            {
                "candidate_module": spec.module,
                "candidate_family": spec.family,
                "cross_engine_guard_count": len(cross_after),
                "cross_engine_guard_observations": cross_after,
                "edge_oracle": edge,
                "deep_proof": contract,
                "private_binder_observation_sha256": frozen.value_digest(
                    report["private_binder_observations"]
                ),
            }
        )
        validate_candidate_worker(report, spec, edge, contract)
        return report


def validate_candidate_worker(
    report: Any,
    spec: deep.CandidateSpec,
    edge: dict[str, Any],
    contract: dict[str, Any],
) -> None:
    validate_public_worker(report, "candidate")
    require(report.get("candidate_module") == spec.module, "worker changed candidate module")
    require(report.get("candidate_family") == spec.family, "worker changed candidate family")
    require(report.get("edge_oracle") == edge, "worker changed its exact passing edge proof")
    require(report.get("deep_proof") == contract, "worker changed its exact passing deep proof")
    require(
        report.get("native_artifacts") == edge["production_artifacts"],
        "worker changed its actual native mappings or sources",
    )
    regex = report.get("forbidden_regex_guard_observations")
    require(isinstance(regex, list) and len(regex) == GUARD_COUNT, "worker dropped a frozen guard")
    require(report.get("forbidden_regex_guards") == GUARD_COUNT, "worker changed guard denominator")
    require(
        all(row.get("passed") is True for row in regex),
        "worker reached or disabled a standard-library regex engine",
    )
    require(len({row.get("id") for row in regex}) == GUARD_COUNT, "worker duplicated a regex guard")
    cross = report.get("cross_engine_guard_observations")
    require(isinstance(cross, list) and len(cross) >= 10, "worker dropped independent-engine guards")
    require(report.get("cross_engine_guard_count") == len(cross), "cross-engine guard count changed")
    require(
        len({row.get("module") for row in cross}) == len(cross),
        "worker duplicated a foreign-engine guard",
    )
    require(
        all(row.get("type") == "IndependentEngineGuard" for row in cross),
        "a foreign-engine guard did not fail closed",
    )
    observations = report.get("private_binder_observations")
    failures = report.get("private_binder_failures")
    require(report.get("private_binder_checks") == BINDER_COUNT, "native binder count changed")
    validate_binder_observations(observations, failures, spec)
    require(
        report.get("private_binder_observation_sha256")
        == frozen.value_digest(observations),
        "native binder observations or documentation were changed",
    )


def run_worker(
    role: str,
    spec: deep.CandidateSpec,
    edge_path: Path | None = None,
    deep_path: Path | None = None,
) -> dict[str, Any]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPATH"] = str(ROOT)
    command = [
        str(deep.PINNED_EXECUTABLE),
        "-B",
        str(RUNNER),
        "--worker",
        role,
        "--module",
        spec.module,
    ]
    if edge_path is not None:
        command.extend(("--edge-oracle", str(edge_path.resolve())))
    if deep_path is not None:
        command.extend(("--deep-proof", str(deep_path.resolve())))
    result = subprocess.run(
        command,
        cwd=str(ROOT),
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(
            f"isolated {spec.family} {role} observability worker failed "
            f"({result.returncode}): {result.stderr[-8000:]} {result.stdout[-2500:]}"
        )
    try:
        report = json.loads(result.stdout)
    except (TypeError, ValueError) as error:
        raise AssertionError(f"isolated {role} observability report is not JSON") from error
    if role in {"stdlib-a", "stdlib-b"}:
        validate_public_worker(report, role)
    elif role == "guard-self-test":
        require(report.get("schema") == SCHEMA, "guard self-test schema changed")
        require(report.get("role") == role, "guard self-test role changed")
        require(report.get("checks") == CASE_COUNT, "guard self-test case denominator changed")
        require(report.get("fixture_sha256") == frozen.FROZEN_FIXTURE_SHA256, "guard fixture changed")
        require(report.get("candidate_module") == spec.module, "guard selected wrong candidate family")
        require(report.get("forbidden_regex_guards") == GUARD_COUNT, "guard self-test lost regex poisons")
        require(len(report.get("forbidden_regex_guard_observations", ())) == GUARD_COUNT, "guard evidence missing")
        require(report.get("cross_engine_guard_count", 0) >= 10, "guard self-test lost foreign poisons")
        require(
            len(report.get("cross_engine_guard_observations", ()))
            == report["cross_engine_guard_count"],
            "guard self-test lost a foreign guard observation",
        )
    elif role == "candidate":
        require(edge_path is not None and deep_path is not None, "worker proofs missing")
        _, edge, _ = deep.read_edge_proof(edge_path, spec)
        contract = read_deep_proof(deep_path, spec, edge)
        validate_candidate_worker(report, spec, edge, contract)
    elif role == "poison":
        require(report.get("schema") == SCHEMA, "poison report schema changed")
        require(report.get("role") == "poison", "poison report role changed")
        require(report.get("candidate_module") == spec.module, "poison selected a foreign family")
        require(report.get("forbidden_regex_guards") == GUARD_COUNT, "poison dropped a regex guard")
        require(report.get("cross_engine_guard_count", 0) >= 10, "poison dropped a family guard")
    else:
        raise AssertionError("unknown isolated observability role")
    return report


def full_mismatches(expected: list[Any], actual: list[Any]) -> list[dict[str, Any]]:
    left = {row["id"]: row for row in expected}
    right = {row["id"]: row for row in actual}
    result: list[dict[str, Any]] = []
    for identity in sorted(left.keys() | right.keys()):
        reference = left.get(identity)
        candidate = right.get(identity)
        if reference is None or candidate is None:
            result.append(
                {
                    "id": identity,
                    "family": (reference or candidate or {}).get("family", "missing"),
                    "expected": reference,
                    "actual": candidate,
                }
            )
        elif reference["observation"] != candidate["observation"]:
            result.append(
                {
                    "id": identity,
                    "family": reference["family"],
                    "expected_sha256": reference["sha256"],
                    "actual_sha256": candidate["sha256"],
                    "expected": reference["observation"],
                    "actual": candidate["observation"],
                }
            )
    return result


def iterator_controls(expected: dict[str, Any], actual: dict[str, Any]) -> dict[str, Any]:
    references = expected.get("rejected_iterator_controls")
    candidates = actual.get("rejected_iterator_controls")
    require(isinstance(references, list) and len(references) == 2, "frozen reference iterator controls missing")
    require(isinstance(candidates, list) and len(candidates) == 2, "candidate iterator controls missing")
    results = []
    failures = []
    for reference, candidate in zip(references, candidates, strict=True):
        require(reference.get("id") == candidate.get("id"), "iterator control identity changed")
        passed = (
            reference.get("correct_public_observation")
            == candidate.get("correct_public_observation")
        )
        entry = {
            "id": reference["id"],
            "passed": passed,
            "reference_public_observation": reference.get("correct_public_observation"),
            "candidate_public_observation": candidate.get("correct_public_observation"),
            "reference_private_type": reference.get("diagnostic_private_iterator_type"),
            "candidate_private_type": candidate.get("diagnostic_private_iterator_type"),
            "private_type_counted_as_public_failure": False,
        }
        results.append(entry)
        if not passed:
            failures.append(entry)
    return {"checks": len(results), "failures": failures, "observations": results}


def validated_output(
    path: Path, spec: deep.CandidateSpec, temporary_root: Path | None = None
) -> Path:
    resolved = path.resolve()
    slug = OUTPUT_SLUG[spec.family]
    prefix = f"rust-v8-observability-{slug}-qualified"
    require(resolved.name.endswith(".json.gz"), "observability evidence must be gzip")
    stem = resolved.name[: -len(".json.gz")]
    require(stem.startswith(prefix), "observability output names another engine family")
    suffix = stem[len(prefix) :]
    require(
        not suffix
        or (
            suffix.startswith("-")
            and all(character.isascii() and (character.isalnum() or character == "-") for character in suffix[1:])
            and len(suffix) > 1
        ),
        "observability output has an unsafe stage suffix",
    )
    if temporary_root is not None:
        root = temporary_root.resolve()
        require(root.parent == Path("/tmp"), "self-test evidence escaped its /tmp directory")
        require(resolved.parent == root, "self-test evidence changed its temporary root")
    elif resolved.parent != EVIDENCE.resolve():
        require(
            resolved.is_relative_to(Path("/tmp")),
            "observability output must remain in candidates/evidence or caller-owned /tmp",
        )
        require(resolved.parent.is_dir(), "caller-owned temporary evidence directory is missing")
    require(resolved.parent.is_dir(), "observability evidence directory is missing")
    require(not resolved.exists() and not resolved.is_symlink(), "refusing to overwrite observability evidence")
    return resolved


def verify_frozen_history_unchanged() -> None:
    require(
        deep.sha256_path(OBSERVABILITY_SOURCE) == OBSERVABILITY_SOURCE_SHA256,
        "the immutable 479-case suite changed during execution",
    )
    require(
        deep.sha256_path(DEEP_RUNNER) == DEEP_RUNNER_SHA256,
        "the frozen family-specific deep gate changed during execution",
    )
    require(
        deep.sha256_path(EVIDENCE / frozen.ARCHIVE_NAMES["manifest"]) == MANIFEST_SHA256,
        "the preserved observability manifest was overwritten",
    )
    deep.verify_original_still_frozen()


def write_report(path: Path, report: dict[str, Any]) -> str:
    verify_frozen_history_unchanged()
    payload = frozen.canonical(report)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o644)
    with os.fdopen(descriptor, "wb") as stream:
        with gzip.GzipFile(
            filename="", fileobj=stream, mode="wb", compresslevel=9, mtime=0
        ) as archive:
            archive.write(payload)
    raw = path.read_bytes()
    require(len(raw) >= 10 and raw[:2] == b"\x1f\x8b", "new observability evidence is not gzip")
    require(not raw[3] & 0x08, "new evidence recorded a nondeterministic filename")
    require(raw[4:8] == b"\x00\x00\x00\x00", "new evidence recorded a timestamp")
    require(gzip.decompress(raw) == payload, "new evidence failed its exact round-trip")
    verify_frozen_history_unchanged()
    return hashlib.sha256(raw).hexdigest()


def build_report(
    spec: deep.CandidateSpec, edge_path: Path, deep_path: Path
) -> dict[str, Any]:
    history = frozen_history()
    _, edge, _ = deep.read_edge_proof(edge_path, spec)
    contract = read_deep_proof(deep_path, spec, edge)
    first = run_worker("stdlib-a", spec)
    second = run_worker("stdlib-b", spec)
    reference_failures = full_mismatches(first["observations"], second["observations"])
    require(not reference_failures, "fresh pinned CPython references disagree")
    require(
        first["observations"] == history["archives"]["stdlib-a"]["observations"],
        "fresh reference A differs from the frozen historical answers",
    )
    require(
        second["observations"] == history["archives"]["stdlib-b"]["observations"],
        "fresh reference B differs from the frozen historical answers",
    )
    poison = run_worker("poison", spec, edge_path, deep_path)
    candidate = run_worker("candidate", spec, edge_path, deep_path)
    require(poison.get("native_artifacts") == edge["production_artifacts"], "poison worker loaded stale artifacts")
    require(poison.get("edge_oracle") == edge, "poison worker substituted edge evidence")
    require(poison.get("deep_proof") == contract, "poison worker substituted deep evidence")
    require(
        poison.get("cross_engine_guard_observations")
        == candidate.get("cross_engine_guard_observations"),
        "candidate and poison workers exercised different foreign-engine controls",
    )
    failures = full_mismatches(first["observations"], candidate["observations"])
    controls = iterator_controls(first, candidate)
    binder_failures = candidate["private_binder_failures"]
    failed = bool(failures or binder_failures or controls["failures"])
    counts = collections.Counter(item.get("family", "missing") for item in failures)
    report = {
        "schema": SCHEMA,
        "status": "FAIL" if failed else "PASS",
        "python": "3.14.6",
        "seed": frozen.SEED,
        "fixture_sha256": frozen.FROZEN_FIXTURE_SHA256,
        "checks": CASE_COUNT,
        "self_oracle_checks": CASE_COUNT,
        "self_oracle_failures": len(reference_failures),
        "candidate_checks": CASE_COUNT,
        "candidate_failures": len(failures),
        "candidate_failures_by_family": dict(sorted(counts.items())),
        "failures": failures,
        "family_counts": first["family_counts"],
        "seeded_cases": sum(
            value
            for family, value in first["family_counts"].items()
            if family.startswith("seeded-")
        ),
        "private_binder_checks": BINDER_COUNT,
        "private_binder_failures": binder_failures,
        "private_binder_observations": candidate["private_binder_observations"],
        "private_binder_observation_sha256": candidate[
            "private_binder_observation_sha256"
        ],
        "forbidden_regex_guards": GUARD_COUNT,
        "forbidden_regex_guard_observations": candidate[
            "forbidden_regex_guard_observations"
        ],
        "cross_engine_guard_count": candidate["cross_engine_guard_count"],
        "cross_engine_guard_observations": candidate[
            "cross_engine_guard_observations"
        ],
        "candidate_module": spec.module,
        "candidate_family": spec.family,
        "expected_observation_sha256": first["observation_sha256"],
        "actual_observation_sha256": candidate["observation_sha256"],
        "monitoring_available": first["monitoring_available"],
        "native_artifacts": candidate["native_artifacts"],
        "edge_oracle": edge,
        "deep_proof": contract,
        "reference": first,
        "reference_independent_repeat": second,
        "candidate": candidate,
        "poison": poison,
        "public_iterator_controls": controls,
        "immutable_frozen_observability": {
            "path": "tools/rust_v7_observability_oracle.py",
            "sha256": OBSERVABILITY_SOURCE_SHA256,
            "manifest_path": "candidates/evidence/rust-v7-observability-manifest.json.gz",
            "manifest_sha256": MANIFEST_SHA256,
            "reference_sha256": FROZEN_REFERENCE_SHA256,
        },
        "multi_candidate_deep_runner": {
            "path": "tools/rust_v8_multi_candidate_contract.py",
            "sha256": DEEP_RUNNER_SHA256,
        },
        "runner": {
            "path": "tools/rust_v8_multi_candidate_observability.py",
            "sha256": deep.sha256_path(RUNNER),
        },
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    verify_frozen_history_unchanged()
    return report


def summarize(report: dict[str, Any], output: Path, digest: str) -> dict[str, Any]:
    names = (
        "schema",
        "status",
        "python",
        "seed",
        "fixture_sha256",
        "checks",
        "self_oracle_checks",
        "self_oracle_failures",
        "candidate_checks",
        "candidate_failures",
        "candidate_failures_by_family",
        "seeded_cases",
        "private_binder_checks",
        "private_binder_failures",
        "forbidden_regex_guards",
        "cross_engine_guard_count",
        "candidate_module",
        "candidate_family",
        "expected_observation_sha256",
        "actual_observation_sha256",
        "native_artifacts",
        "edge_oracle",
        "deep_proof",
        "performance",
        "holdout",
    )
    result = {name: report[name] for name in names}
    result["private_binder_failures"] = len(report["private_binder_failures"])
    result["iterator_public_control_failures"] = len(
        report["public_iterator_controls"]["failures"]
    )
    result["evidence_path"] = str(output)
    result["evidence_sha256"] = digest
    if report["failures"]:
        result["first_failure_ids"] = [item["id"] for item in report["failures"][:8]]
    return result


def run_gate(
    spec: deep.CandidateSpec,
    edge_path: Path,
    deep_path: Path,
    output_path: Path,
) -> tuple[dict[str, Any], dict[str, Any], int]:
    output = validated_output(output_path, spec)
    report = build_report(spec, edge_path, deep_path)
    archive_sha256 = write_report(output, report)
    return report, summarize(report, output, archive_sha256), int(report["status"] != "PASS")


def expect_rejection(label: str, action: Any) -> dict[str, str]:
    try:
        action()
    except (AssertionError, RuntimeError, TypeError, ValueError, OSError) as error:
        return {"name": label, "status": "PASS", "error_type": type(error).__name__}
    raise AssertionError(f"a poisoned multi-candidate observation was accepted: {label}")


def synthetic_deep_document(
    spec: deep.CandidateSpec, edge: dict[str, Any]
) -> dict[str, Any]:
    suite = deep.load_frozen_suite()
    baseline, _ = deep.original_failure(suite)
    reference = copy.deepcopy(baseline["reference"])
    repeat = copy.deepcopy(baseline["reference_independent_repeat"])
    candidate = copy.deepcopy(reference)
    candidate["role"] = "candidate"
    candidate["native_artifacts"] = copy.deepcopy(edge["production_artifacts"])
    candidate["guard_count"] = GUARD_COUNT
    candidate["guard_observations"] = copy.deepcopy(baseline["guard_observations"])
    topology = suite.diagnostic_differences(
        reference["implementation_private_gc_diagnostics"],
        candidate["implementation_private_gc_diagnostics"],
    )
    return {
        "schema": deep.FROZEN_SCHEMA,
        "status": "PASS",
        "python": "3.14.6",
        "seed": deep.FROZEN_SEED,
        "seeded_case_count": deep.FROZEN_SEEDED_CASES,
        "checks": deep.FROZEN_CASES,
        "fixture_sha256": deep.FROZEN_FIXTURE_SHA256,
        "suite_path": "tools/rust_v8_deep_contract_oracle.py",
        "suite_sha256": deep.FROZEN_SUITE_SHA256,
        "reference_a_sha256": deep.FROZEN_REFERENCE_SHA256,
        "reference_b_sha256": deep.FROZEN_REFERENCE_SHA256,
        "candidate_sha256": deep.FROZEN_REFERENCE_SHA256,
        "stdlib_vs_stdlib_mismatches": [],
        "public_mismatch_count": 0,
        "public_mismatch_family_counts": {},
        "public_mismatches": [],
        "implementation_private_gc_topology_difference_count": len(topology),
        "implementation_private_gc_topology_differences": topology,
        "forbidden_regex_guards": GUARD_COUNT,
        "guard_observations": copy.deepcopy(baseline["guard_observations"]),
        "native_artifacts": copy.deepcopy(edge["production_artifacts"]),
        "candidate_module": spec.module,
        "candidate_family": spec.family,
        "edge_oracle": copy.deepcopy(edge),
        "reference": reference,
        "reference_independent_repeat": repeat,
        "candidate": candidate,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def synthetic_binders(spec: deep.CandidateSpec) -> list[dict[str, Any]]:
    doc = "Synthetic native-binding self-test only."
    digest = hashlib.sha256(doc.encode("utf-8")).hexdigest()
    rows = []
    for identity in binder_ids(spec):
        success = identity.endswith("native-success")
        rows.append(
            {
                "id": identity,
                "passed": True,
                "result": (
                    {"status": "value", "value": {"span": [0, 1]}}
                    if success
                    else {"status": "error", "error": {"type": "TypeError", "args": []}}
                ),
                "recovery": {"status": "value", "value": {"span": [0, 1]}},
                "native_owner": spec.native_module,
                "callable_type": "builtin_function_or_method",
                "callable_name": "synthetic-self-test-only",
                "documentation": doc,
                "documentation_sha256": digest,
                "text_signature": None,
            }
        )
    return rows


def self_test() -> dict[str, Any]:
    history = frozen_history()
    spec = SUPPORTED["candidates.rust_candidate"]
    reference_a = run_worker("stdlib-a", spec)
    reference_b = run_worker("stdlib-b", spec)
    require(
        not full_mismatches(reference_a["observations"], reference_b["observations"]),
        "fresh pinned self-test references differ",
    )
    guards = run_worker("guard-self-test", spec)
    edge_document = deep.synthetic_edge_document(spec)
    _, synthetic_edge = deep.validate_edge_document(
        edge_document,
        spec,
        "1" * 64,
        Path("/tmp/rebar-v8-observability-synthetic-edge.json.gz"),
    )
    contract = synthetic_deep_document(spec, synthetic_edge)
    valid = validate_deep_document(
        contract,
        spec,
        synthetic_edge,
        "2" * 64,
        Path("/tmp/rebar-v8-observability-synthetic-deep.json.gz"),
    )

    def changed_reference(mutator: Any) -> Any:
        report = copy.deepcopy(reference_a)
        mutator(report)
        return lambda: validate_public_worker(report, "stdlib-a")

    def changed_contract(mutator: Any, selected: deep.CandidateSpec = spec) -> Any:
        document = copy.deepcopy(contract)
        mutator(document)
        return lambda: validate_deep_document(
            document,
            selected,
            synthetic_edge,
            "2" * 64,
            Path("/tmp/rebar-v8-observability-synthetic-deep.json.gz"),
        )

    checks = [
        expect_rejection(
            "changed-public-case-count",
            changed_reference(lambda report: report.update({"checks": CASE_COUNT - 1})),
        ),
        expect_rejection(
            "changed-public-seed",
            changed_reference(lambda report: report.update({"seed": frozen.SEED + 1})),
        ),
        expect_rejection(
            "changed-public-fixture",
            changed_reference(lambda report: report.update({"fixture_sha256": "0" * 64})),
        ),
        expect_rejection(
            "dropped-public-observation",
            changed_reference(lambda report: report["observations"].pop()),
        ),
        expect_rejection(
            "reordered-public-observations",
            changed_reference(
                lambda report: report["observations"].reverse()
            ),
        ),
        expect_rejection(
            "changed-public-observation",
            changed_reference(
                lambda report: report["observations"][0].update(
                    {"observation": {"poisoned": True}}
                )
            ),
        ),
        expect_rejection(
            "changed-complete-public-digest",
            changed_reference(lambda report: report.update({"observation_sha256": "0" * 64})),
        ),
        expect_rejection(
            "wrong-deep-candidate-family",
            changed_contract(lambda report: report.update({"candidate_family": "ZIG"})),
        ),
        expect_rejection(
            "wrong-deep-candidate-module",
            changed_contract(
                lambda report: report.update({"candidate_module": "candidates.zig_candidate"})
            ),
        ),
        expect_rejection(
            "nonpassing-deep-proof",
            changed_contract(lambda report: report.update({"status": "FAIL"})),
        ),
        expect_rejection(
            "hidden-deep-public-failure",
            changed_contract(lambda report: report.update({"public_mismatch_count": 1})),
        ),
        expect_rejection(
            "wrong-deep-reference-digest",
            changed_contract(lambda report: report.update({"reference_a_sha256": "0" * 64})),
        ),
        expect_rejection(
            "dropped-deep-reference-observation",
            changed_contract(lambda report: report["reference"]["observations"].pop()),
        ),
        expect_rejection(
            "swapped-deep-edge-archive",
            changed_contract(
                lambda report: report["edge_oracle"].update({"archive_sha256": "0" * 64})
            ),
        ),
        expect_rejection(
            "stale-deep-native-artifact",
            changed_contract(
                lambda report: report["native_artifacts"][0].update({"sha256": "0" * 64})
            ),
        ),
        expect_rejection(
            "dropped-deep-regex-guard",
            changed_contract(lambda report: report["guard_observations"].pop()),
        ),
        expect_rejection(
            "fake-python-native-binder",
            lambda: require_native_callable(lambda: None, object(), "poison-binder"),
        ),
        expect_rejection(
            "wrong-native-binder-owner",
            lambda: require_native_callable(len, object(), "foreign-binder"),
        ),
        expect_rejection(
            "wrong-evidence-family",
            lambda: validated_output(
                EVIDENCE / "rust-v8-observability-zig-qualified.json.gz", spec
            ),
        ),
        expect_rejection(
            "wrong-evidence-suffix",
            lambda: validated_output(
                EVIDENCE / "rust-v8-observability-rust-qualified.json", spec
            ),
        ),
        expect_rejection(
            "evidence-path-traversal",
            lambda: validated_output(
                EVIDENCE / ".." / "rust-v8-observability-rust-qualified.json.gz", spec
            ),
        ),
    ]

    zig = SUPPORTED["candidates.zig_candidate"]
    binders = synthetic_binders(zig)
    validate_binder_observations(binders, [], zig)

    def poisoned_binder(mutator: Any) -> Any:
        rows = copy.deepcopy(binders)
        mutator(rows)
        return lambda: validate_binder_observations(rows, [], zig)

    checks.extend(
        (
            expect_rejection(
                "dropped-private-native-binder",
                poisoned_binder(lambda rows: rows.pop()),
            ),
            expect_rejection(
                "swapped-private-native-binder-family",
                poisoned_binder(lambda rows: rows[0].update({"native_owner": "candidates._rust_bridge"})),
            ),
            expect_rejection(
                "forged-native-binder-documentation",
                poisoned_binder(lambda rows: rows[0].update({"documentation": "fake native docs"})),
            ),
            expect_rejection(
                "python-wrapper-pretending-to-be-native",
                poisoned_binder(lambda rows: rows[0].update({"callable_type": "function"})),
            ),
            expect_rejection(
                "hidden-private-binder-failure",
                poisoned_binder(lambda rows: rows[0].update({"passed": False})),
            ),
        )
    )

    with tempfile.TemporaryDirectory(
        prefix="rebar-v8-multifamily-observability-", dir="/tmp"
    ) as temporary:
        temporary_root = Path(temporary)
        output = validated_output(
            temporary_root / "rust-v8-observability-rust-qualified-self-test.json.gz",
            spec,
            temporary_root,
        )
        synthetic = {
            "schema": SCHEMA,
            "mode": "synthetic-integrity-self-test-only",
            "status": "PASS",
            "checks": CASE_COUNT,
            "reference": reference_a,
            "reference_independent_repeat": reference_b,
            "synthetic_edge_proof": synthetic_edge,
            "synthetic_deep_proof": valid,
            "private_binder_checks": BINDER_COUNT,
            "synthetic_zig_native_binder_controls": binders,
            "forbidden_regex_guards": GUARD_COUNT,
            "cross_engine_guard_count": guards["cross_engine_guard_count"],
            "performance": "NOT MEASURED",
            "holdout": "NOT ACCESSED",
        }
        archive_sha256 = write_report(output, synthetic)
        require(
            json.loads(gzip.decompress(output.read_bytes())) == synthetic,
            "synthetic evidence does not round-trip",
        )
        checks.append(
            expect_rejection(
                "overwrite-existing-temporary-evidence",
                lambda: validated_output(output, spec, temporary_root),
            )
        )
        checks.append(
            expect_rejection(
                "temporary-evidence-path-traversal",
                lambda: validated_output(
                    temporary_root.parent / "rust-v8-observability-rust-qualified-poison.json.gz",
                    spec,
                    temporary_root,
                ),
            )
        )

    verify_frozen_history_unchanged()
    return {
        "schema": SCHEMA,
        "mode": "multi-candidate-observability-self-test",
        "status": "PASS",
        "python": "3.14.6",
        "seed": frozen.SEED,
        "fixture_sha256": frozen.FROZEN_FIXTURE_SHA256,
        "checks": CASE_COUNT,
        "self_oracle_checks": CASE_COUNT,
        "self_oracle_failures": 0,
        "reference_a_sha256": reference_a["observation_sha256"],
        "reference_b_sha256": reference_b["observation_sha256"],
        "historical_reference_sha256": FROZEN_REFERENCE_SHA256,
        "historical_manifest_sha256": MANIFEST_SHA256,
        "historical_observability_source_sha256": OBSERVABILITY_SOURCE_SHA256,
        "historical_deep_runner_sha256": DEEP_RUNNER_SHA256,
        "supported_candidates": {
            name: spec.family for name, spec in sorted(SUPPORTED.items())
        },
        "family_private_binder_controls": {
            spec.family: len(binder_ids(spec)) for spec in SUPPORTED.values()
        },
        "forbidden_regex_guards": guards["forbidden_regex_guards"],
        "cross_engine_guard_count": guards["cross_engine_guard_count"],
        "integrity_poison_self_test_count": len(checks),
        "integrity_poison_self_tests": checks,
        "synthetic_evidence_sha256": archive_sha256,
        "temporary_evidence_removed": True,
        "repository_evidence_written": False,
        "production_candidates_executed": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify unchanged frozen public tracing and genuine family-native safety."
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--gate", action="store_true")
    modes.add_argument(
        "--worker", choices=("stdlib-a", "stdlib-b", "candidate", "poison", "guard-self-test")
    )
    parser.add_argument("--module", choices=tuple(SUPPORTED))
    parser.add_argument("--edge-oracle", type=Path)
    parser.add_argument("--deep-proof", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args(arguments)


def main(arguments: list[str]) -> int:
    options = parse_arguments(arguments)
    if options.self_test:
        require(options.module is None, "synthetic self-test cannot select a candidate")
        require(options.edge_oracle is None, "synthetic self-test cannot use actual edge evidence")
        require(options.deep_proof is None, "synthetic self-test cannot use actual deep evidence")
        require(options.output is None, "synthetic self-test cannot write repository evidence")
        print(frozen.canonical(self_test()).decode("ascii"))
        return 0
    require(options.module is not None, "a real worker requires its exact candidate module")
    spec = SUPPORTED[options.module]
    if options.worker is not None:
        require(options.output is None, "an isolated worker cannot write repository evidence")
        if options.worker in {"stdlib-a", "stdlib-b", "guard-self-test"}:
            require(options.edge_oracle is None, "a nonproduction worker cannot access candidate evidence")
            require(options.deep_proof is None, "a nonproduction worker cannot access deep evidence")
        else:
            require(options.edge_oracle is not None, "production worker requires its edge proof")
            require(options.deep_proof is not None, "production worker requires its deep proof")
        result = evaluate_worker(options.worker, spec, options.edge_oracle, options.deep_proof)
        print(frozen.canonical(result).decode("ascii"))
        return 0
    require(options.edge_oracle is not None, "the gate requires a passing family-specific edge proof")
    require(options.deep_proof is not None, "the gate requires a passing family-specific deep proof")
    require(options.output is not None, "the gate requires a fresh explicit evidence path")
    _, summary, status = run_gate(
        spec, options.edge_oracle, options.deep_proof, options.output
    )
    print(frozen.canonical(summary).decode("ascii"))
    return status


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
