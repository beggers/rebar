#!/usr/bin/env python3
"""Run sealed, actual frozen correctness campaigns for independent regex engines."""

from __future__ import annotations

import argparse
import builtins
import collections
import copy
import dataclasses
import gzip
import hashlib
import importlib.abc
import json
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any
from unittest import mock

from tools import audit_from_scratch as scratch
from tools import rust_campaign_gate as campaign
from tools import rust_v8_multi_candidate_contract as contract


ROOT = campaign.ROOT
EVIDENCE = ROOT / "candidates/evidence"
MODULES = (
    "candidates.rust_candidate",
    "candidates.zig_candidate",
    "candidates.vm_candidate",
)
SCHEMA = "rebar-rust-campaign-gate-v1"
SELF_TEST_SCHEMA = "rebar-v8-multi-candidate-sealed-campaign-self-test-v1"
OBSERVABILITY_SCHEMA = "rebar-v8-multi-candidate-observability-v1"
OBSERVABILITY_SEED = 2026072343
OBSERVABILITY_FIXTURE_SHA256 = (
    "1d5a84b9fe2213289d96126dab740d103958bd593b811b262238bfc57a4a5403"
)
EXCLUDED_NAMES = campaign.SEALED_EXCLUDED_STEP_NAMES
REQUIRED_NAMES = frozenset(
    {
        "from-scratch-static-audit",
        "frozen-correctness-v2",
        "frozen-correctness-v3",
        "official-cpython-tests",
        "upstream-public-surface",
        "frozen-cross-family-observability",
        "replacement-and-callback-adversarial",
        "deep-replacement-and-callback-adversarial",
        "isolated-crash-and-resource-safety",
        "isolated-depth-and-overflow-safety",
        "full-unicode-plane",
    }
)
GENERIC_STEP_NAMES = frozenset(
    {
        "frozen-correctness-v2",
        "frozen-correctness-v3",
        "official-cpython-tests",
        "upstream-public-surface",
        "rust-public-surface",
        "unicode-group-name-errors",
        "replacement-and-callback-adversarial",
        "deep-replacement-and-callback-adversarial",
        "extended-cpython-paths",
        "isolated-crash-and-resource-safety",
        "isolated-depth-and-overflow-safety",
        "full-unicode-plane",
    }
)


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def digest_file(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def digest_value(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def family_for(module: str) -> str:
    require(module in MODULES, "only the three independently audited candidate families are allowed")
    return {
        "RUST": "rust",
        "ZIG": "zig",
        "C": "vm",
    }[contract.SPECS[module].family]


def reject_performance_path(path: Any) -> None:
    if isinstance(path, int) or not isinstance(path, (str, bytes, os.PathLike)):
        return
    try:
        resolved = Path(os.fsdecode(path)).resolve()
    except (OSError, TypeError, ValueError):
        return
    performance = (ROOT / "performance").resolve()
    tools = (ROOT / "tools").resolve()
    if resolved.is_relative_to(performance):
        raise AssertionError("sealed candidate campaign refused to open performance evidence")
    if resolved.is_relative_to(tools) and resolved.name.startswith("perf_"):
        raise AssertionError("sealed candidate campaign refused to open a performance runner")


class PerformanceImportGuard(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname: str, path: Any, target: Any = None) -> None:
        if (
            fullname == "performance"
            or fullname.startswith("performance.")
            or fullname.startswith("tools.perf_")
        ):
            raise AssertionError("sealed candidate campaign refused a performance import")
        return None


_SEAL_INSTALLED = False


def install_seal() -> None:
    global _SEAL_INSTALLED
    if _SEAL_INSTALLED:
        return

    def audit(event: str, arguments: tuple[Any, ...]) -> None:
        if event == "open" and arguments:
            reject_performance_path(arguments[0])
        elif event == "subprocess.Popen" and len(arguments) >= 2:
            supplied = arguments[1]
            if isinstance(supplied, (tuple, list)):
                for argument in supplied:
                    reject_performance_path(argument)

    sys.addaudithook(audit)
    sys.meta_path.insert(0, PerformanceImportGuard())
    _SEAL_INSTALLED = True


SEALED_WORKER = r"""
import importlib.abc
import os
import runpy
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
SCRIPT = Path(sys.argv[2]).resolve()

def reject(value):
    if isinstance(value, int) or not isinstance(value, (str, bytes, os.PathLike)):
        return
    path = Path(os.fsdecode(value)).resolve()
    if path.is_relative_to((ROOT / "performance").resolve()):
        raise AssertionError("sealed worker attempted to access a performance fixture")
    tools = (ROOT / "tools").resolve()
    if path.is_relative_to(tools) and path.name.startswith("perf_"):
        raise AssertionError("sealed worker attempted to access a performance runner")

def audit(event, arguments):
    if event == "open" and arguments:
        reject(arguments[0])
    elif event == "subprocess.Popen" and len(arguments) >= 2:
        command = arguments[1]
        if isinstance(command, (tuple, list)):
            for item in command:
                reject(item)

class Guard(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path, target=None):
        if name == "performance" or name.startswith("performance.") or name.startswith("tools.perf_"):
            raise AssertionError("sealed worker attempted to import a performance suite")
        return None

sys.addaudithook(audit)
sys.meta_path.insert(0, Guard())
reject(SCRIPT)
sys.argv = [str(SCRIPT), *sys.argv[3:]]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
runpy.run_path(str(SCRIPT), run_name="__main__")
"""


def step_arguments(step: campaign.Step, module: str) -> tuple[str, ...]:
    arguments = list(step.arguments)
    for index in range(len(arguments) - 1):
        if arguments[index] == "--module" and arguments[index + 1] == campaign.RUST_MODULE:
            arguments[index + 1] = module
    require(
        campaign.RUST_MODULE not in arguments or module == campaign.RUST_MODULE,
        "a sealed step silently selected the Rust candidate",
    )
    return tuple(arguments)


def generic_steps(module: str, directory: Path) -> tuple[campaign.Step, ...]:
    complete = campaign.suite_steps(directory)
    excluded = tuple(step for step in complete if campaign.performance_suite_step(step))
    require(
        tuple(step.name for step in excluded) == EXCLUDED_NAMES,
        "sealed performance exclusions changed",
    )
    retained = campaign.suite_steps(directory, sealed_practice_only=True)
    selected = []
    for step in retained:
        if step.name not in GENERIC_STEP_NAMES:
            continue
        renamed = (
            "candidate-public-surface"
            if step.name == "rust-public-surface"
            else step.name
        )
        selected.append(
            dataclasses.replace(
                step,
                name=renamed,
                arguments=step_arguments(step, module),
            )
        )
    require(len(selected) == 12, "a sealed frozen generic oracle was added or omitted")
    require(
        not any(campaign.performance_suite_step(step) for step in selected),
        "a performance fixture entered the generic sealed plan",
    )
    require(
        all("--module" in step.arguments for step in selected),
        "a generic oracle does not explicitly select its actual candidate",
    )
    return tuple(selected)


def exclusion_records(directory: Path) -> list[dict[str, str]]:
    complete = campaign.suite_steps(directory)
    excluded = [
        {
            "name": item.name,
            "script": item.script,
            "reason": "performance fixture or held-out workload",
        }
        for item in complete
        if campaign.performance_suite_step(item)
    ]
    require(
        tuple(item["name"] for item in excluded) == EXCLUDED_NAMES,
        "a legacy performance fixture was not explicitly excluded",
    )
    return excluded


def read_deep_document(path: Path, spec: contract.CandidateSpec, edge: dict) -> dict:
    resolved = Path(path).resolve()
    require(not Path(path).is_symlink(), "deep evidence must not be a symlink")
    require(
        resolved.is_file() and resolved.is_relative_to((ROOT / "candidates").resolve()),
        "candidate deep evidence escaped authorized production evidence",
    )
    compressed = resolved.read_bytes()
    require(
        len(compressed) >= 10
        and compressed[:2] == b"\x1f\x8b"
        and not compressed[3] & 0x08
        and compressed[4:8] == b"\x00\x00\x00\x00",
        "candidate deep evidence is not deterministic gzip",
    )
    try:
        payload = gzip.decompress(compressed)
        report = json.loads(payload)
    except (OSError, EOFError, ValueError, json.JSONDecodeError) as error:
        raise AssertionError("candidate deep evidence cannot be decoded") from error
    require(isinstance(report, dict), "candidate deep evidence is not an object")
    require(canonical(report) == payload, "candidate deep evidence is not canonical JSON")

    scalars = {
        "schema": contract.FROZEN_SCHEMA,
        "status": "PASS",
        "python": "3.14.6",
        "seed": contract.FROZEN_SEED,
        "seeded_case_count": contract.FROZEN_SEEDED_CASES,
        "checks": contract.FROZEN_CASES,
        "fixture_sha256": contract.FROZEN_FIXTURE_SHA256,
        "suite_path": "tools/rust_v8_deep_contract_oracle.py",
        "suite_sha256": contract.FROZEN_SUITE_SHA256,
        "reference_a_sha256": contract.FROZEN_REFERENCE_SHA256,
        "reference_b_sha256": contract.FROZEN_REFERENCE_SHA256,
        "candidate_sha256": contract.FROZEN_REFERENCE_SHA256,
        "public_mismatch_count": 0,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    for name, expected in scalars.items():
        require(report.get(name) == expected, f"candidate deep proof changed: {name}")
    require(report.get("public_mismatches") == [], "candidate deep public failures were hidden")
    require(
        report.get("public_mismatch_family_counts") == {},
        "candidate deep public mismatch categories were hidden",
    )
    require(
        report.get("stdlib_vs_stdlib_mismatches") in ([], 0),
        "candidate deep Python references disagree",
    )
    require(
        report.get("candidate_module") == spec.module
        and report.get("candidate_family") == spec.family,
        "candidate deep proof belongs to another engine family",
    )
    artifacts = edge["production_artifacts"]
    require(
        report.get("native_artifacts") == artifacts,
        "candidate deep proof used stale or foreign native artifacts",
    )
    proof = report.get("edge_oracle")
    require(isinstance(proof, dict), "candidate deep edge proof is missing")
    require(
        proof.get("archive_sha256") == edge["archive_sha256"]
        and proof.get("module") == spec.module
        and proof.get("family") == spec.family
        and proof.get("checks") == contract.EDGE_CHECKS
        and proof.get("failed") == 0,
        "candidate deep proof is not bound to its actual edge-qualified build",
    )
    suite = contract.load_frozen_suite()
    expected_ids = [item["id"] for item in suite.build_cases()]
    require(len(expected_ids) == contract.FROZEN_CASES, "deep fixture denominator changed")
    for label in ("reference", "reference_independent_repeat", "candidate"):
        worker = report.get(label)
        require(isinstance(worker, dict), f"candidate deep {label} report is missing")
        rows = worker.get("observations")
        require(
            worker.get("checks") == contract.FROZEN_CASES
            and isinstance(rows, list)
            and len(rows) == contract.FROZEN_CASES,
            f"candidate deep {label} omitted an actual observation",
        )
        require(
            [item.get("id") for item in rows] == expected_ids,
            f"candidate deep {label} changed a frozen case identity",
        )
        require(
            suite.digest(rows) == worker.get("observation_sha256"),
            f"candidate deep {label} observation digest changed",
        )
        require(
            all(suite.digest(item.get("observation")) == item.get("sha256") for item in rows),
            f"candidate deep {label} contains a poisoned observation",
        )
        diagnostics = worker.get("implementation_private_gc_diagnostics")
        require(
            isinstance(diagnostics, list)
            and len(diagnostics) == contract.FROZEN_SEEDED_CASES,
            f"candidate deep {label} omitted a private diagnostic",
        )
    require(
        suite.mismatches(
            report["reference"]["observations"],
            report["reference_independent_repeat"]["observations"],
        )
        == [],
        "candidate deep standard-library self-reference is false",
    )
    require(
        suite.mismatches(
            report["reference"]["observations"], report["candidate"]["observations"]
        )
        == [],
        "candidate deep proof concealed a real public mismatch",
    )
    require(
        report.get("forbidden_regex_guards", 0) >= 13,
        "candidate deep proof lost an active regex poison",
    )
    cross = report.get("cross_engine_guard_observations")
    require(
        isinstance(cross, list)
        and len(cross) >= 10
        and report.get("cross_engine_guard_count") == len(cross),
        "candidate deep proof lost an independent-engine poison guard",
    )
    return {
        "path": resolved.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "archive_sha256": hashlib.sha256(compressed).hexdigest(),
        "checks": contract.FROZEN_CASES,
        "public_mismatches": 0,
        "seed": contract.FROZEN_SEED,
        "fixture_sha256": contract.FROZEN_FIXTURE_SHA256,
        "candidate_module": spec.module,
        "candidate_family": spec.family,
        "native_artifacts": artifacts,
        "report": report,
    }


def static_family_audit(module: str, edge: dict) -> dict:
    family = family_for(module)
    evidence = scratch.run_audit()
    require(evidence.get("passed") is True, "complete from-scratch audit failed")
    require(evidence.get("result") == "PASS", "complete from-scratch audit is not passing")
    require(
        evidence.get("verified_core_family_count", 0) >= 3
        and evidence.get("verified_distinct_pipeline_count", 0) >= 3,
        "three independent semantic parser/compiler/executor families were not proven",
    )
    details = evidence.get("families", {}).get(family)
    require(isinstance(details, dict) and details.get("passed"), "candidate family source audit failed")
    pipeline = details.get("owned_pipeline", {})
    require(pipeline.get("passed") is True, "candidate has no owned semantic pipeline")
    runtime = details.get("isolated_runtime", {})
    require(runtime.get("passed") is True, "candidate isolated native provenance failed")
    mappings = runtime.get("native_mapping_provenance", {})
    require(mappings.get("passed") is True, "candidate actual native mappings failed")
    source = details.get("python_source", {})
    expected = next(
        (item for item in edge["production_artifacts"] if item["role"] == "public-python"),
        None,
    )
    require(
        expected is not None and source.get("sha256") == expected["sha256"],
        "candidate static source is not the edge-qualified public source",
    )
    scope = evidence.get("scope", {})
    require(
        scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_or_case_fixture_access") is False,
        "the static audit accessed a held-out workload",
    )
    return evidence


def output_path(path: Path, module: str) -> Path:
    requested = Path(path)
    require(not requested.is_symlink(), "campaign output must not be a symlink")
    resolved = requested.resolve()
    require(resolved.parent == EVIDENCE.resolve(), "campaign output must be directly inside candidates/evidence")
    require(resolved.suffix == ".json", "campaign output must be plain verifiable JSON")
    family = family_for(module)
    require(
        family in resolved.name.casefold() and "campaign" in resolved.name.casefold(),
        "campaign output must identify its independent candidate family",
    )
    require(not resolved.exists(), "refusing to overwrite an existing campaign report")
    return resolved


def validate_edge(path: Path, module: str) -> tuple[contract.CandidateSpec, dict]:
    spec = contract.SPECS[module]
    requested = Path(path)
    require(not requested.is_symlink(), "candidate edge proof must not be a symlink")
    resolved = requested.resolve()
    require(
        resolved.is_file() and resolved.is_relative_to(EVIDENCE.resolve()),
        "candidate edge proof escaped candidate evidence",
    )
    _, proof, _ = contract.read_edge_proof(resolved, spec)
    require(proof.get("module") == module, "candidate edge proof belongs to another family")
    require(proof.get("family") == spec.family, "candidate edge family changed")
    require(
        proof.get("checks") == contract.EDGE_CHECKS
        and proof.get("category_count") == contract.EDGE_CATEGORIES
        and proof.get("failed") == 0,
        "candidate comprehensive edge proof is incomplete",
    )
    require(
        proof.get("candidate_sha256")
        == proof.get("reference_sha256")
        == contract.EDGE_REFERENCE_SHA256,
        "candidate edge proof does not reproduce the frozen Python answers",
    )
    return spec, proof


def parse_child_json(value: str) -> dict:
    lines = [line for line in value.splitlines() if line.strip()]
    require(bool(lines), "isolated frozen suite produced no report")
    try:
        report = json.loads(lines[-1])
    except (ValueError, TypeError, json.JSONDecodeError) as error:
        raise AssertionError("isolated frozen suite returned invalid JSON") from error
    require(isinstance(report, dict), "isolated frozen suite report is not an object")
    return report


def validate_observability_document(
    document: dict,
    module: str,
    edge: dict,
    deep_proof: dict,
) -> None:
    spec = contract.SPECS[module]
    require(
        document.get("schema") == OBSERVABILITY_SCHEMA
        and document.get("status") == "PASS"
        and document.get("python") == "3.14.6"
        and document.get("seed") == OBSERVABILITY_SEED
        and document.get("fixture_sha256") == OBSERVABILITY_FIXTURE_SHA256
        and document.get("checks") == 479
        and document.get("self_oracle_checks") == 479
        and document.get("candidate_checks") == 479
        and document.get("candidate_module") == module
        and document.get("candidate_family") == spec.family,
        "frozen cross-family public observability is incomplete or belongs to another engine",
    )
    require(
        document.get("self_oracle_failures") in ([], 0)
        and document.get("candidate_failures") in ([], 0)
        and document.get("candidate_failures_by_family") == {}
        and document.get("failures") == [],
        "candidate cross-family observability conceals a Python or public mismatch",
    )
    references = []
    for label in ("reference", "reference_independent_repeat", "candidate"):
        worker = document.get(label)
        require(isinstance(worker, dict), f"cross-family observability omitted {label}")
        rows = worker.get("observations")
        require(
            worker.get("checks") == 479
            and isinstance(rows, list)
            and len(rows) == 479,
            f"cross-family observability omitted a {label} public result",
        )
        require(
            len({row.get("id") for row in rows}) == 479,
            f"cross-family observability duplicated a {label} public result",
        )
        require(
            worker.get("observation_sha256") == digest_value(rows),
            f"cross-family observability changed its {label} observation digest",
        )
        require(
            all(
                row.get("sha256") == digest_value(row.get("observation"))
                for row in rows
            ),
            f"cross-family observability contains a poisoned {label} result",
        )
        references.append(rows)
    require(
        references[0] == references[1] == references[2],
        "the independent cross-family candidate differs from its frozen Python references",
    )

    candidate = document["candidate"]
    private = candidate.get("private_binder_observations")
    public_private = document.get("private_binder_observations")
    require(
        document.get("private_binder_checks") == 34
        and document.get("private_binder_failures") in ([], 0)
        and isinstance(private, list)
        and len(private) == 34
        and private == public_private
        and all(row.get("passed") is True for row in private),
        "candidate did not pass and preserve its own 34 actual native binders",
    )
    guards = document.get(
        "forbidden_regex_guard_observations",
        candidate.get(
            "forbidden_regex_guard_observations",
            candidate.get("guard_observations", []),
        ),
    )
    require(
        document.get("forbidden_regex_guards") == 13
        and isinstance(guards, list)
        and len(guards) == 13
        and all(
            row.get("passed") is True or row.get("type") == "GuardSignal"
            for row in guards
        ),
        "candidate observability lost an actively poisoned CPython regex entry point",
    )
    cross = document.get(
        "cross_engine_guard_observations",
        document.get(
            "cross_engine_guards",
            candidate.get(
                "cross_engine_guard_observations",
                candidate.get("cross_engine_guards", []),
            ),
        ),
    )
    require(
        isinstance(cross, list)
        and len(cross) >= 10
        and document.get("cross_engine_guard_count") == len(cross),
        "candidate observability lost its actual cross-family regex guards",
    )
    require(
        document.get("holdout") == "NOT ACCESSED"
        and document.get("performance") == "NOT MEASURED",
        "candidate public observability accessed a holdout or benchmark",
    )
    require(
        document.get("native_artifacts") == edge["production_artifacts"],
        "candidate observability loaded stale or foreign native artifacts",
    )
    observed_edge = document.get("edge_oracle", {})
    require(
        observed_edge.get("archive_sha256") == edge["archive_sha256"]
        and observed_edge.get("module") == module
        and observed_edge.get("production_artifacts") == edge["production_artifacts"],
        "candidate observability is not bound to its actual owned edge proof",
    )
    observed_deep = document.get("deep_proof", {})
    require(
        isinstance(observed_deep, dict)
        and observed_deep.get("checks") == contract.FROZEN_CASES
        and observed_deep.get("candidate_module") == module
        and observed_deep.get("candidate_family") == spec.family
        and observed_deep.get("edge_archive_sha256") == edge["archive_sha256"]
        and observed_deep.get("native_artifacts") == edge["production_artifacts"],
        "candidate observability is not bound to its actual passing deep proof",
    )
    require(
        observed_deep.get("archive_sha256") == deep_proof["archive_sha256"],
        "candidate observability used a stale deep-contract archive",
    )


def child_step(
    step: campaign.Step,
    module: str,
    memory_mib: int,
    *,
    contract_role: str | None = None,
    edge: dict | None = None,
    deep_proof: dict | None = None,
) -> dict:
    require(not campaign.performance_suite_step(step), "sealed campaign rejected a performance step")
    script = (ROOT / step.script).resolve()
    require(script.is_file(), f"frozen candidate suite is missing: {step.script}")
    reject_performance_path(script)
    command = [
        sys.executable,
        "-B",
        "-c",
        SEALED_WORKER,
        str(ROOT),
        str(script),
        *step.arguments,
    ]
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
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
            preexec_fn=campaign.restrict_process(memory_mib, step.timeout_seconds + 5),
        )
    except subprocess.TimeoutExpired as error:
        raise AssertionError(f"isolated suite timed out: {step.name}") from error
    if child.returncode:
        raise AssertionError(
            f"isolated suite failed: {step.name}; exit={child.returncode}; "
            f"stderr={child.stderr[-6000:]}; stdout={child.stdout[-3000:]}"
        )

    if step.artifact is not None:
        artifact = Path(step.artifact)
        require(artifact.is_file(), f"frozen suite omitted its actual evidence: {step.name}")
        try:
            raw = artifact.read_bytes()
            if artifact.suffix == ".gz":
                require(
                    len(raw) >= 10
                    and raw[:2] == b"\x1f\x8b"
                    and not raw[3] & 0x08
                    and raw[4:8] == b"\x00\x00\x00\x00",
                    f"frozen suite evidence is not deterministic gzip: {step.name}",
                )
                payload = gzip.decompress(raw)
                document = json.loads(payload)
                require(
                    canonical(document) == payload,
                    f"frozen suite evidence is not canonical JSON: {step.name}",
                )
            else:
                document = json.loads(raw)
        except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as error:
            raise AssertionError(f"frozen suite evidence is not valid: {step.name}") from error
    else:
        document = parse_child_json(child.stdout)
    require(isinstance(document, dict), f"frozen suite evidence is invalid: {step.name}")
    failures = campaign.failure_values(document)
    require(not failures, f"frozen suite reported genuine failures: {step.name}: {failures[:3]}")
    if step.expected_checks is not None:
        metrics = campaign.all_metric_values(document)
        require(
            any(item.get("value") == step.expected_checks for item in metrics),
            f"frozen suite denominator changed: {step.name}",
        )
    if step.name == "frozen-cross-family-observability":
        require(edge is not None and deep_proof is not None, "observability proof lacks native provenance")
        validate_observability_document(document, module, edge, deep_proof)
    elif contract_role is None:
        require(document.get("module") == module, f"frozen suite substituted another candidate: {step.name}")
    else:
        spec = contract.SPECS[module]
        suite = contract.load_frozen_suite()
        if contract_role == "guard-self-test":
            require(
                document.get("role") == "guard-self-test"
                and document.get("module") == module
                and document.get("family") == spec.family
                and document.get("guard_count") == 13
                and len(document.get("guards", [])) == 13
                and document.get("cross_engine_guard_count", 0) >= 10
                and len(document.get("cross_engine_guards", []))
                == document.get("cross_engine_guard_count"),
                "candidate native-boundary cross-engine poison failed",
            )
        elif contract_role == "stdlib-a":
            contract.verify_worker_report(suite, document, "stdlib-a", None)
            require(
                document.get("observation_sha256") == contract.FROZEN_REFERENCE_SHA256,
                "candidate native reference changed frozen Python answers",
            )
        else:
            require(edge is not None, "candidate native worker has no edge authorization")
            contract.verify_worker_report(suite, document, contract_role, edge)
            require(
                document.get("candidate_module") == module
                and document.get("candidate_family") == spec.family,
                "native candidate worker loaded a foreign semantic engine",
            )
            if contract_role == "candidate":
                require(
                    document.get("observation_sha256")
                    == contract.FROZEN_REFERENCE_SHA256,
                    "candidate native worker changed a frozen public result",
                )
    if step.name == "official-cpython-tests":
        require(
            document.get("methods") == 146
            and document.get("passed") == 144
            and document.get("skipped") == 2,
            "candidate changed the exact official CPython result or named skips",
        )
    if step.name == "unicode-group-name-errors":
        require(
            document.get("schema") == "rebar-rust-unicode-group-name-adversarial-v1"
            and document.get("formatter") == "production"
            and document.get("self_oracle_passes") == 2
            and document.get("self_oracle_failures") == [],
            "candidate changed the frozen group-name self-oracle",
        )
    if step.name == "full-unicode-plane":
        require(
            document.get("correctness_checks") == 4_494_555,
            "candidate omitted full-plane Python Unicode comparisons",
        )
    return {
        "name": step.name,
        "passed": True,
        "status": "passed",
        "script": step.script,
        "command": command,
        "expected_checks": step.expected_checks,
        "timeout_seconds": step.timeout_seconds,
        "memory_limit_mib": memory_mib,
        "core_dumps": "disabled",
        "candidate": module,
        "evidence": document,
        "evidence_sha256": digest_value(document),
        "holdout_accessed": False,
        "performance": "NOT MEASURED",
        "timing_performed": False,
    }


def internal_step(name: str, module: str, evidence: dict, expected: int | None = None) -> dict:
    return {
        "name": name,
        "passed": True,
        "status": "passed",
        "candidate": module,
        "expected_checks": expected,
        "evidence": evidence,
        "evidence_sha256": digest_value(evidence),
        "holdout_accessed": False,
        "performance": "NOT MEASURED",
        "timing_performed": False,
    }


def contract_steps(
    module: str, edge_path: Path, directory: Path
) -> tuple[tuple[campaign.Step, str], ...]:
    source = "tools/rust_v8_multi_candidate_contract.py"
    resolved = str(Path(edge_path).resolve())
    return (
        (
            campaign.Step(
                "independent-native-boundary-self-oracle",
                source,
                ("--worker", "stdlib-a", "--module", module),
                contract.FROZEN_CASES,
                300,
            ),
            "stdlib-a",
        ),
        (
            campaign.Step(
                "independent-native-boundary-integrity",
                source,
                ("--worker", "guard-self-test", "--module", module),
                contract.FROZEN_CASES,
                300,
            ),
            "guard-self-test",
        ),
        (
            campaign.Step(
                "independent-native-boundary-poison",
                source,
                ("--worker", "poison", "--module", module, "--edge-oracle", resolved),
                contract.FROZEN_CASES,
                300,
            ),
            "poison",
        ),
        (
            campaign.Step(
                "independent-native-boundary-compatibility",
                source,
                ("--worker", "candidate", "--module", module, "--edge-oracle", resolved),
                contract.FROZEN_CASES,
                600,
            ),
            "candidate",
        ),
    )


def observability_step(module: str, edge_path: Path, deep_path: Path, directory: Path) -> campaign.Step:
    artifact = directory / (
        f"rust-v8-observability-{family_for(module)}-qualified.json.gz"
    )
    return campaign.Step(
        "frozen-cross-family-observability",
        "tools/rust_v8_multi_candidate_observability.py",
        (
            "--gate",
            "--module",
            module,
            "--edge-oracle",
            str(Path(edge_path).resolve()),
            "--deep-proof",
            str(Path(deep_path).resolve()),
            "--output",
            str(artifact),
        ),
        479,
        900,
        str(artifact),
    )


def validate_report_structure(report: dict, module: str) -> None:
    require(isinstance(report, dict), "candidate campaign is not a JSON object")
    require(report.get("schema") == SCHEMA, "candidate campaign schema changed")
    require(report.get("candidate") == module, "candidate campaign selected a foreign engine")
    require(report.get("pinned_cpython") == "3.14.6", "candidate campaign changed pinned Python")
    require(report.get("mode") == "sealed-practice-only", "candidate campaign is not sealed")
    require(report.get("passed") is True, "candidate campaign did not actually pass")
    require(report.get("holdout_accessed") is False, "candidate campaign accessed a holdout")
    require(report.get("performance") == "NOT MEASURED", "candidate campaign executed timing")
    require(report.get("timing_performed") is False, "candidate campaign performed timing")
    goal = report.get("goal")
    require(
        isinstance(goal, dict)
        and goal.get("passed") is True
        and goal.get("actual_sha256") == campaign.GOAL_SHA256
        and goal.get("expected_sha256") == campaign.GOAL_SHA256,
        "candidate campaign changed the immutable objective",
    )
    exclusions = report.get("excluded_steps")
    require(isinstance(exclusions, list), "candidate campaign omitted performance exclusions")
    require(
        {row.get("name") for row in exclusions if isinstance(row, dict)}
        == frozenset(EXCLUDED_NAMES),
        "candidate campaign failed to exclude all original performance fixtures",
    )
    require(len(exclusions) == len(EXCLUDED_NAMES), "performance exclusion was duplicated")
    steps = report.get("steps")
    require(isinstance(steps, list) and len(steps) >= 18, "full candidate campaign is incomplete")
    names = set()
    for row in steps:
        require(isinstance(row, dict), "candidate campaign step is malformed")
        require(row.get("passed") is True, "candidate campaign step did not pass")
        require(row.get("status") in (None, "passed"), "candidate campaign step has a failure status")
        require(row.get("candidate") == module, "candidate campaign step substituted another engine")
        name = row.get("name")
        require(isinstance(name, str) and bool(name), "candidate campaign step has no identity")
        require(name not in names, "candidate campaign repeats a correctness step")
        names.add(name)
        evidence = row.get("evidence")
        require(isinstance(evidence, dict), "candidate campaign fabricated step evidence")
        require(
            row.get("evidence_sha256") == digest_value(evidence),
            "candidate campaign step evidence was poisoned",
        )
        require(row.get("holdout_accessed") is False, "candidate step opened a holdout")
        require(row.get("performance") == "NOT MEASURED", "candidate step timed a benchmark")
        require(row.get("timing_performed") is False, "candidate step performed timing")
    require(REQUIRED_NAMES <= names, "candidate campaign omitted a required P0 obligation")
    full_unicode = next(item for item in steps if item["name"] == "full-unicode-plane")
    require(
        full_unicode.get("expected_checks") == 4_494_555
        and full_unicode["evidence"].get("correctness_checks") == 4_494_555,
        "candidate campaign weakened complete Unicode coverage",
    )
    for step_name, minimum in (
        ("frozen-correctness-v2", 8244),
        ("frozen-correctness-v3", 44084),
        ("official-cpython-tests", 144),
        ("upstream-public-surface", 190),
        ("replacement-and-callback-adversarial", 8862),
        ("deep-replacement-and-callback-adversarial", 11266),
        ("isolated-crash-and-resource-safety", 254),
        ("isolated-depth-and-overflow-safety", 348),
    ):
        step = next((row for row in steps if row["name"] == step_name), None)
        require(step is not None and step.get("expected_checks") == minimum, f"candidate weakened {step_name}")
    for step_name in (
        "independent-native-boundary-self-oracle",
        "independent-native-boundary-integrity",
        "independent-native-boundary-poison",
        "independent-native-boundary-compatibility",
    ):
        require(step_name in names, f"candidate omitted actual family-specific guards: {step_name}")
    observability = next(
        (row for row in steps if row["name"] == "frozen-cross-family-observability"),
        None,
    )
    require(
        observability is not None and observability.get("expected_checks") == 479,
        "candidate omitted its actual frozen 479-case public observability suite",
    )
    edge = report.get("edge_oracle")
    require(
        isinstance(edge, dict)
        and edge.get("module") == module
        and edge.get("checks") == contract.EDGE_CHECKS
        and edge.get("category_count") == contract.EDGE_CATEGORIES
        and edge.get("failed") == 0,
        "candidate campaign edge provenance is invalid",
    )
    deep_proof = report.get("deep_proof")
    require(
        isinstance(deep_proof, dict)
        and deep_proof.get("candidate_module") == module
        and deep_proof.get("checks") == contract.FROZEN_CASES
        and deep_proof.get("public_mismatches") == 0,
        "candidate campaign is not bound to its actual passing public deep contract",
    )
    require(
        report.get("native_artifacts") == edge.get("production_artifacts")
        and deep_proof.get("native_artifacts") == edge.get("production_artifacts"),
        "candidate campaign substituted stale or foreign native artifacts",
    )


def run_campaign(module: str, edge_path: Path, deep_path: Path, target: Path, memory_mib: int) -> dict:
    require(tuple(sys.version_info[:3]) == campaign.PINNED_CPYTHON, "requires pinned CPython 3.14.6")
    install_seal()
    destination = output_path(target, module)
    spec, edge = validate_edge(edge_path, module)
    deep_proof = read_deep_document(deep_path, spec, edge)
    goal = campaign.goal_state()
    require(goal.get("passed") is True, "the immutable objective changed")

    with tempfile.TemporaryDirectory(
        prefix=f"rebar-v8-{family_for(module)}-sealed-campaign-", dir="/tmp"
    ) as temporary:
        directory = Path(temporary)
        report = {
            "schema": SCHEMA,
            "candidate": module,
            "python_version": platform.python_version(),
            "python_executable": sys.executable,
            "pinned_cpython": "3.14.6",
            "mode": "sealed-practice-only",
            "holdout_accessed": False,
            "performance": "NOT MEASURED",
            "timing_performed": False,
            "fail_fast": True,
            "memory_limit_mib": memory_mib,
            "goal": goal,
            "excluded_steps": exclusion_records(directory),
            "edge_oracle": edge,
            "deep_proof": deep_proof,
            "native_artifacts": edge["production_artifacts"],
            "steps": [],
            "passed": False,
        }

        audit = static_family_audit(module, edge)
        report["steps"].append(internal_step("from-scratch-static-audit", module, audit))
        family = family_for(module)
        family_details = audit["families"][family]
        report["steps"].append(
            internal_step("independent-source-no-delegation", module, family_details["python_source"])
        )
        report["steps"].append(
            internal_step("independent-owned-native-pipeline", module, family_details)
        )
        report["steps"].append(
            internal_step("candidate-frozen-edge-proof", module, edge, contract.EDGE_CHECKS)
        )
        report["steps"].append(
            internal_step("candidate-frozen-deep-public-proof", module, deep_proof, contract.FROZEN_CASES)
        )
        for step, role in contract_steps(module, edge_path, directory):
            report["steps"].append(
                child_step(step, module, memory_mib, contract_role=role, edge=edge)
            )
        report["steps"].append(
            child_step(
                observability_step(module, edge_path, deep_path, directory),
                module,
                memory_mib,
                edge=edge,
                deep_proof=deep_proof,
            )
        )
        for step in generic_steps(module, directory):
            report["steps"].append(child_step(step, module, memory_mib))
        report["required_correctness_step_count"] = len(report["steps"])
        report["goal"] = campaign.goal_state()
        report["passed"] = (
            report["goal"].get("passed") is True
            and all(step.get("passed") is True for step in report["steps"])
        )
        validate_report_structure(report, module)
        require(not destination.exists(), "refusing to overwrite a candidate campaign")
        with destination.open("x", encoding="ascii") as stream:
            json.dump(report, stream, ensure_ascii=True, allow_nan=False, indent=2, sort_keys=True)
            stream.write("\n")
        with destination.open("r", encoding="ascii") as stream:
            restored = json.load(stream)
        require(restored == report, "sealed campaign evidence did not exactly round-trip")
        validate_report_structure(restored, module)
        require(
            campaign.goal_state().get("actual_sha256") == campaign.GOAL_SHA256,
            "immutable objective changed while running the sealed campaign",
        )
    return {
        "schema": SCHEMA,
        "candidate": module,
        "status": "PASS",
        "passed": True,
        "mode": "sealed-practice-only",
        "steps": len(report["steps"]),
        "edge_checks": contract.EDGE_CHECKS,
        "deep_checks": contract.FROZEN_CASES,
        "deep_public_mismatches": 0,
        "excluded_steps": list(EXCLUDED_NAMES),
        "output": destination.relative_to(ROOT).as_posix(),
        "output_sha256": digest_file(destination),
        "holdout_accessed": False,
        "performance": "NOT MEASURED",
        "timing_performed": False,
    }


def synthetic_campaign(module: str) -> dict:
    proof = {
        "module": module,
        "family": contract.SPECS[module].family,
        "checks": contract.EDGE_CHECKS,
        "category_count": contract.EDGE_CATEGORIES,
        "failed": 0,
        "production_artifacts": [
            {"role": "public-python", "path": "candidates/example.py", "sha256": "1" * 64}
        ],
    }
    deep_evidence = {
        "candidate_module": module,
        "checks": contract.FROZEN_CASES,
        "public_mismatches": 0,
        "native_artifacts": proof["production_artifacts"],
    }
    expected = {
        "frozen-correctness-v2": 8244,
        "frozen-correctness-v3": 44084,
        "official-cpython-tests": 144,
        "upstream-public-surface": 190,
        "replacement-and-callback-adversarial": 8862,
        "deep-replacement-and-callback-adversarial": 11266,
        "isolated-crash-and-resource-safety": 254,
        "isolated-depth-and-overflow-safety": 348,
        "full-unicode-plane": 4_494_555,
        "frozen-cross-family-observability": 479,
    }
    names = (
        "from-scratch-static-audit",
        "independent-source-no-delegation",
        "independent-owned-native-pipeline",
        "candidate-frozen-edge-proof",
        "candidate-frozen-deep-public-proof",
        "independent-native-boundary-self-oracle",
        "independent-native-boundary-integrity",
        "independent-native-boundary-poison",
        "independent-native-boundary-compatibility",
        "frozen-cross-family-observability",
        "frozen-correctness-v2",
        "frozen-correctness-v3",
        "official-cpython-tests",
        "upstream-public-surface",
        "candidate-public-surface",
        "unicode-group-name-errors",
        "replacement-and-callback-adversarial",
        "deep-replacement-and-callback-adversarial",
        "extended-cpython-paths",
        "isolated-crash-and-resource-safety",
        "isolated-depth-and-overflow-safety",
        "full-unicode-plane",
    )
    steps = []
    for name in names:
        evidence = {"module": module, "synthetic_self_test_only": True}
        if name == "full-unicode-plane":
            evidence["correctness_checks"] = 4_494_555
        steps.append(
            {
                "name": name,
                "passed": True,
                "status": "passed",
                "candidate": module,
                "expected_checks": expected.get(name),
                "evidence": evidence,
                "evidence_sha256": digest_value(evidence),
                "holdout_accessed": False,
                "performance": "NOT MEASURED",
                "timing_performed": False,
            }
        )
    return {
        "schema": SCHEMA,
        "candidate": module,
        "pinned_cpython": "3.14.6",
        "mode": "sealed-practice-only",
        "holdout_accessed": False,
        "performance": "NOT MEASURED",
        "timing_performed": False,
        "passed": True,
        "goal": {
            "passed": True,
            "expected_sha256": campaign.GOAL_SHA256,
            "actual_sha256": campaign.GOAL_SHA256,
        },
        "excluded_steps": [
            {"name": name, "script": "synthetic-self-test-only", "reason": "sealed"}
            for name in EXCLUDED_NAMES
        ],
        "edge_oracle": proof,
        "deep_proof": deep_evidence,
        "native_artifacts": proof["production_artifacts"],
        "steps": steps,
    }


def expect_rejection(name: str, action: Any) -> dict:
    try:
        action()
    except (AssertionError, KeyError, TypeError, ValueError, OSError) as error:
        return {"id": name, "passed": True, "rejection": str(error)}
    raise AssertionError(f"sealed multi-candidate poison was accepted: {name}")


def self_test() -> dict:
    install_seal()
    checks = []
    synthetic = synthetic_campaign(MODULES[0])
    candidate_plan_step_counts = {}
    with mock.patch.object(
        subprocess,
        "run",
        side_effect=AssertionError("campaign self-test must not start a candidate or benchmark"),
    ) as process:
        validate_report_structure(synthetic, MODULES[0])
        for module in MODULES:
            validate_report_structure(synthetic_campaign(module), module)
            directory = Path("/tmp/rebar-v8-sealed-campaign-synthetic-only")
            planned = generic_steps(module, directory)
            native = contract_steps(
                module,
                directory / "synthetic-edge-proof-never-opened.json.gz",
                directory,
            )
            observed = observability_step(
                module,
                directory / "synthetic-edge-proof-never-opened.json.gz",
                directory / "synthetic-deep-proof-never-opened.json.gz",
                directory,
            )
            require(
                len(planned) == 12
                and len(native) == 4
                and observed.expected_checks == 479,
                "sealed campaign changed its genuine module-specific step plan",
            )
            for step in (*planned, *(item[0] for item in native), observed):
                require(
                    not campaign.performance_suite_step(step),
                    "a performance runner entered an actual sealed candidate plan",
                )
                require(
                    module in step.arguments,
                    "a planned frozen suite does not select its actual candidate",
                )
            candidate_plan_step_counts[module] = 5 + len(native) + 1 + len(planned)
            require(
                candidate_plan_step_counts[module] == 22,
                "a candidate does not have all twenty-two actual correctness steps",
            )

        def poisoned(label: str, mutation: Any) -> dict:
            changed = copy.deepcopy(synthetic)
            mutation(changed)
            return expect_rejection(
                label, lambda: validate_report_structure(changed, MODULES[0])
            )

        def poison_step(name: str, mutator: Any) -> Any:
            def alter(report: dict) -> None:
                step = next(row for row in report["steps"] if row["name"] == name)
                mutator(step)
            return alter

        for name in sorted(REQUIRED_NAMES):
            checks.append(
                poisoned(
                    f"missing-required-step/{name}",
                    lambda report, target=name: report.update(
                        steps=[row for row in report["steps"] if row["name"] != target]
                    ),
                )
            )

        mutations = (
            ("wrong-campaign-schema", lambda item: item.update(schema="poison")),
            ("wrong-candidate-family", lambda item: item.update(candidate=MODULES[1])),
            ("wrong-pinned-python", lambda item: item.update(pinned_cpython="3.13.0")),
            ("unsealed-campaign-mode", lambda item: item.update(mode="unsealed")),
            ("candidate-campaign-failure", lambda item: item.update(passed=False)),
            ("candidate-holdout-access", lambda item: item.update(holdout_accessed=True)),
            ("candidate-timing", lambda item: item.update(timing_performed=True)),
            ("candidate-performance-measurement", lambda item: item.update(performance="MEASURED")),
            ("mutated-objective", lambda item: item["goal"].update(actual_sha256="0" * 64)),
            ("missing-performance-exclusion", lambda item: item["excluded_steps"].pop()),
            (
                "duplicated-performance-exclusion",
                lambda item: item["excluded_steps"].append(copy.deepcopy(item["excluded_steps"][0])),
            ),
            ("wrong-edge-family", lambda item: item["edge_oracle"].update(module=MODULES[1])),
            ("weakened-edge-denominator", lambda item: item["edge_oracle"].update(checks=1)),
            ("hidden-edge-failure", lambda item: item["edge_oracle"].update(failed=1)),
            ("wrong-deep-family", lambda item: item["deep_proof"].update(candidate_module=MODULES[1])),
            ("weakened-deep-denominator", lambda item: item["deep_proof"].update(checks=1)),
            ("hidden-deep-mismatch", lambda item: item["deep_proof"].update(public_mismatches=1)),
            ("stale-native-artifacts", lambda item: item.update(native_artifacts=[])),
            (
                "hidden-step-failure",
                poison_step("frozen-correctness-v3", lambda item: item.update(passed=False)),
            ),
            (
                "changed-step-candidate",
                poison_step("frozen-correctness-v3", lambda item: item.update(candidate=MODULES[1])),
            ),
            (
                "mutated-step-evidence-digest",
                poison_step("frozen-correctness-v3", lambda item: item.update(evidence_sha256="0" * 64)),
            ),
            (
                "step-holdout-access",
                poison_step("frozen-correctness-v3", lambda item: item.update(holdout_accessed=True)),
            ),
            (
                "step-performance-timing",
                poison_step("frozen-correctness-v3", lambda item: item.update(timing_performed=True)),
            ),
            (
                "weakened-full-unicode-denominator",
                poison_step("full-unicode-plane", lambda item: item.update(expected_checks=128)),
            ),
            (
                "mutated-full-unicode-report",
                poison_step(
                    "full-unicode-plane",
                    lambda item: item.update(
                        evidence={"module": MODULES[0], "correctness_checks": 128}
                    ),
                ),
            ),
            (
                "weakened-replacement-callbacks",
                poison_step(
                    "replacement-and-callback-adversarial",
                    lambda item: item.update(expected_checks=32),
                ),
            ),
            (
                "missing-actual-native-boundary-guard",
                lambda item: item.update(
                    steps=[
                        row
                        for row in item["steps"]
                        if row["name"] != "independent-native-boundary-integrity"
                    ]
                ),
            ),
        )
        for label, mutation in mutations:
            checks.append(poisoned(label, mutation))

        performance_root = ROOT / "performance"
        tools_root = ROOT / "tools"
        for label, path in (
            ("refused-v6-performance-path", performance_root / "v6/manifest.json"),
            ("refused-v7-performance-path", performance_root / "v7/manifest.json"),
            ("refused-v8-performance-path", performance_root / "v8/holdout-manifest.json"),
            ("refused-v6-performance-runner", tools_root / "perf_v6.py"),
            ("refused-v7-performance-runner", tools_root / "perf_v7.py"),
            ("refused-v8-performance-runner", tools_root / "perf_v8.py"),
        ):
            checks.append(expect_rejection(label, lambda item=path: reject_performance_path(item)))
        checks.append(
            expect_rejection(
                "rejected-performance-module-import",
                lambda: __import__("performance.v8"),
            )
        )
        checks.append(
            expect_rejection(
                "rejected-performance-runner-import",
                lambda: __import__("tools.perf_v7", fromlist=["self_test"]),
            )
        )
        require(process.call_count == 0, "campaign self-test started a candidate or benchmark")

    require(len(checks) >= 20, "sealed campaign did not prove enough malicious controls")
    require(
        len({row["id"] for row in checks}) == len(checks)
        and all(row.get("passed") is True for row in checks),
        "a sealed candidate-campaign poison was accepted",
    )
    return {
        "schema": SELF_TEST_SCHEMA,
        "status": "PASS",
        "python": "3.14.6",
        "candidate_modules": list(MODULES),
        "synthetic_only": True,
        "candidate_processes_started": 0,
        "candidate_reports_written": 0,
        "performance_processes_started": 0,
        "performance_fixtures_opened": 0,
        "performance_modules_imported": 0,
        "holdout_accessed": False,
        "performance": "NOT MEASURED",
        "timing_performed": False,
        "excluded_step_names": list(EXCLUDED_NAMES),
        "required_step_names": sorted(REQUIRED_NAMES),
        "synthetic_step_count": len(synthetic["steps"]),
        "actual_planned_step_counts": candidate_plan_step_counts,
        "poison_control_count": len(checks),
        "poison_controls": checks,
        "failed": 0,
    }


def parse_arguments(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--module", choices=MODULES)
    parser.add_argument("--edge-oracle", type=Path)
    parser.add_argument("--deep-proof", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--memory-mib", type=int, default=2048)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_arguments(argv)
    if args.self_test:
        require(
            args.module is None
            and args.edge_oracle is None
            and args.deep_proof is None
            and args.output is None,
            "campaign self-test cannot run a candidate or write repository evidence",
        )
        print(json.dumps(self_test(), ensure_ascii=True, sort_keys=True), flush=True)
        return 0
    require(args.module in MODULES, "sealed campaign requires one explicit candidate")
    require(args.edge_oracle is not None, "sealed campaign requires an exact candidate edge proof")
    require(args.deep_proof is not None, "sealed campaign requires a passing candidate deep proof")
    require(args.output is not None, "sealed campaign requires a unique candidate evidence output")
    require(args.memory_mib >= 256, "sealed campaign memory limit must be at least 256 MiB")
    result = run_campaign(
        args.module,
        args.edge_oracle,
        args.deep_proof,
        args.output,
        args.memory_mib,
    )
    print(json.dumps(result, ensure_ascii=True, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
