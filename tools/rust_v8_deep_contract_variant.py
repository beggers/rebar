#!/usr/bin/env python3
"""Run the immutable v8 deep-contract fixture against edge-proven Rust builds.

The original suite and its published failing archive are never rewritten.  Every
production worker independently verifies an explicit 223,198-check edge proof
before installing only its five authorized artifact hashes into the unchanged
393-case suite.  Public failures remain failures; implementation-private GC
topology remains separately recorded.
"""

from __future__ import annotations

import argparse
import collections
import copy
import gzip
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
RUNNER = Path(__file__).resolve()
FROZEN_SUITE = ROOT / "tools/rust_v8_deep_contract_oracle.py"
FROZEN_SUITE_SHA256 = (
    "ba4b640d12444a5346d918a039d8a7a9fef0c78a54f6b66c6f0eb0c9dddbe978"
)
FROZEN_FAILURE = ROOT / "candidates/audits/RUST-V8-DEEP-CONTRACT.json.gz"
FROZEN_FAILURE_SHA256 = (
    "db43cbf8be1d6891eb4f009b8ae92995a6434f9753b944fbf0a8ed0b44237192"
)
FROZEN_SCHEMA = "rebar-rust-v8-deep-public-contract-v1"
FROZEN_SEED = 2026072347
FROZEN_CASES = 393
FROZEN_SEEDED_CASES = 64
FROZEN_FIXTURE_SHA256 = (
    "c72a5e47f15c94ce13ce34d4918c05ef81eea5b010ac119b255264e60939ef16"
)
FROZEN_REFERENCE_SHA256 = (
    "b184f3388320909b3c28fbd3ce9c15cefc992d3e852e9495ad8fb503d1cbaad8"
)
FROZEN_BASELINE_CANDIDATE_SHA256 = (
    "f7e55d7715f887ccde54b09f323512b684f486e560b497e7107097822f504185"
)
FROZEN_BASELINE_FAILURES = 104
FROZEN_BASELINE_PRIVATE_DIFFERENCES = 64
PINNED_EXECUTABLE = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
AUDITS = ROOT / "candidates/audits"
BASELINE_SELF_TEST_PROOF = Path(
    "/tmp/rebar-rust-v7-restored-baseline-post-match-0c27626c.json.gz"
)
BASELINE_SELF_TEST_PROOF_SHA256 = (
    "4ad0a2516ede95751a8f2bc6b4d907f12048b2556311ff3bd71c4e4a7664bb2b"
)
EDGE_SCHEMA = "rebar-v7-independent-edge-oracle-v1"
EDGE_SEED = 2026072329
EDGE_CHECKS = 223198
EDGE_CATEGORIES = 49
EDGE_SCRIPT_SHA256 = (
    "fe6a263a48f243ea02faaa78fc3bbd051233a2b2221967a5f76dd1bb79d242ca"
)
EDGE_REFERENCE_SHA256 = (
    "b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526"
)
EDGE_INDEPENDENT_SEEDS = {
    "edge_generation": 2026072329,
    "memory_safety": 5928217332825410871,
    "module_api": 35403857216905324734871187764,
    "object_contract": 5928217332825411394,
    "parser_grammar": 6518143889424763005106639421778,
    "repeat_stream": 23157159151883287,
}
ARTIFACT_PATHS = {
    "bridge-source": "candidates/rust/py_bridge.c",
    "native-bridge": "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
    "native-engine": "candidates/_rust_engine.so",
    "native-source": "candidates/rust/src/lib.rs",
    "public-python": "candidates/rust_candidate.py",
}
SUPPORTED_MODULE = "candidates.rust_candidate"
HEX_DIGITS = frozenset("0123456789abcdef")


def sha256_path(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def load_frozen_suite() -> Any:
    actual = sha256_path(FROZEN_SUITE)
    if actual != FROZEN_SUITE_SHA256:
        raise AssertionError(
            "immutable deep-contract suite changed: "
            f"expected {FROZEN_SUITE_SHA256}, observed {actual}"
        )
    # The frozen script's final ``__main__`` block must never be executed by
    # import.  Restore only its script-defined witness-class identity below;
    # otherwise complete private GC evidence records a synthetic module name.
    spec = importlib.util.spec_from_file_location(
        "rebar_immutable_v8_deep_contract", FROZEN_SUITE
    )
    if spec is None or spec.loader is None:
        raise AssertionError("cannot import the verified immutable deep-contract suite")
    suite = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = suite
    spec.loader.exec_module(suite)
    entry_module = sys.modules.get("__main__")
    if entry_module is None:
        raise AssertionError("the isolated frozen worker lost its script module")
    for item in tuple(vars(suite).values()):
        if isinstance(item, type) and item.__module__ == spec.name:
            item.__module__ = "__main__"
            setattr(entry_module, item.__name__, item)
    if suite.SCHEMA != FROZEN_SCHEMA or suite.SEED != FROZEN_SEED:
        raise AssertionError("the immutable deep-contract schema or seed changed")
    if suite.SEEDED_CASES != FROZEN_SEEDED_CASES:
        raise AssertionError("the immutable seeded-case denominator changed")
    if suite.SCRIPT != FROZEN_SUITE:
        raise AssertionError("the imported fixture does not point to its frozen source")
    fixture = suite.build_cases()
    if len(fixture) != FROZEN_CASES:
        raise AssertionError("the immutable deep-contract denominator changed")
    if suite.digest(fixture) != FROZEN_FIXTURE_SHA256:
        raise AssertionError("the immutable deep-contract case fixture changed")
    if {
        role: value[0] for role, value in suite.CANONICAL_ARTIFACTS.items()
    } != ARTIFACT_PATHS:
        raise AssertionError("the immutable production artifact paths changed")
    suite.verify_runtime()
    return suite


def original_failure(suite: Any) -> tuple[dict[str, Any], bytes]:
    raw = FROZEN_FAILURE.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != FROZEN_FAILURE_SHA256:
        raise AssertionError(
            "the preserved failing deep-contract evidence changed: "
            f"expected {FROZEN_FAILURE_SHA256}, observed {actual}"
        )
    if len(raw) < 10 or raw[:2] != b"\x1f\x8b":
        raise AssertionError("the preserved deep-contract failure is not gzip")
    if raw[3] & 0x08 or raw[4:8] != b"\x00\x00\x00\x00":
        raise AssertionError("preserved deep-contract gzip metadata changed")
    payload = gzip.decompress(raw)
    document = json.loads(payload)
    if suite.canonical(document) != payload:
        raise AssertionError("the preserved failure no longer has canonical JSON")
    expected_scalars = {
        "schema": FROZEN_SCHEMA,
        "status": "FAIL",
        "python": "3.14.6",
        "seed": FROZEN_SEED,
        "seeded_case_count": FROZEN_SEEDED_CASES,
        "checks": FROZEN_CASES,
        "fixture_sha256": FROZEN_FIXTURE_SHA256,
        "suite_path": "tools/rust_v8_deep_contract_oracle.py",
        "suite_sha256": FROZEN_SUITE_SHA256,
        "reference_a_sha256": FROZEN_REFERENCE_SHA256,
        "reference_b_sha256": FROZEN_REFERENCE_SHA256,
        "candidate_sha256": FROZEN_BASELINE_CANDIDATE_SHA256,
        "public_mismatch_count": FROZEN_BASELINE_FAILURES,
        "implementation_private_gc_topology_difference_count": (
            FROZEN_BASELINE_PRIVATE_DIFFERENCES
        ),
        "forbidden_regex_guards": 13,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    for key, expected in expected_scalars.items():
        if document.get(key) != expected:
            raise AssertionError(f"preserved deep-contract baseline changed: {key}")
    if document.get("stdlib_vs_stdlib_mismatches") != []:
        raise AssertionError("the preserved standard-library self-control failed")
    if len(document.get("public_mismatches", ())) != FROZEN_BASELINE_FAILURES:
        raise AssertionError("the preserved full public failure denominator changed")
    if len(document.get("implementation_private_gc_topology_differences", ())) != (
        FROZEN_BASELINE_PRIVATE_DIFFERENCES
    ):
        raise AssertionError("the preserved private GC diagnostic denominator changed")
    for key in ("reference", "reference_independent_repeat", "candidate"):
        report = document.get(key)
        if not isinstance(report, dict) or report.get("checks") != FROZEN_CASES:
            raise AssertionError(f"preserved complete {key} observations changed")
        rows = report.get("observations")
        if not isinstance(rows, list) or len(rows) != FROZEN_CASES:
            raise AssertionError(f"preserved complete {key} cases are missing")
        if suite.digest(rows) != report.get("observation_sha256"):
            raise AssertionError(f"preserved {key} case integrity is invalid")
    baseline_artifacts = [
        {"role": role, "path": relative, "sha256": expected}
        for role, (relative, expected) in sorted(suite.CANONICAL_ARTIFACTS.items())
    ]
    if document.get("native_artifacts") != baseline_artifacts:
        raise AssertionError("preserved original artifact provenance changed")
    return document, raw


def require_sha256(value: Any, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in HEX_DIGITS for character in value)
    ):
        raise AssertionError(f"invalid SHA-256 for {label}")
    return value


def validate_edge_document(
    suite: Any,
    document: Any,
    archive_sha256: str,
    source_path: Path,
) -> tuple[dict[str, tuple[str, str]], dict[str, Any]]:
    if not isinstance(document, dict):
        raise AssertionError("the edge proof must be a JSON object")
    expected_scalars = {
        "schema": EDGE_SCHEMA,
        "seed": EDGE_SEED,
        "correctness_checks": EDGE_CHECKS,
        "failed": 0,
        "module": SUPPORTED_MODULE,
        "oracle": "CPython standard-library re",
        "python": "3.14.6",
        "script_sha256": EDGE_SCRIPT_SHA256,
        "expected_sha256": EDGE_REFERENCE_SHA256,
        "actual_sha256": EDGE_REFERENCE_SHA256,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    for key, expected in expected_scalars.items():
        if document.get(key) != expected:
            raise AssertionError(f"the explicit edge proof is invalid: {key}")
    if document.get("failures") != []:
        raise AssertionError("the explicit edge proof contains correctness failures")
    if document.get("independent_source_seeds") != EDGE_INDEPENDENT_SEEDS:
        raise AssertionError("the explicit edge proof changed its frozen source seeds")
    categories = document.get("categories")
    if not isinstance(categories, dict) or len(categories) != EDGE_CATEGORIES:
        raise AssertionError("the edge proof changed its frozen category denominator")
    if any(not isinstance(value, int) or value < 0 for value in categories.values()):
        raise AssertionError("the edge proof contains an invalid category count")
    if sum(categories.values()) != EDGE_CHECKS:
        raise AssertionError("the edge proof category counts do not cover all checks")
    embedded = document.get("embedded_frozen_oracles")
    if not isinstance(embedded, list) or len(embedded) != 2:
        raise AssertionError("the edge proof lost an independently frozen sub-oracle")
    artifacts = document.get("candidate_artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != len(ARTIFACT_PATHS):
        raise AssertionError("the edge proof must authorize exactly five artifacts")
    mapped: dict[str, tuple[str, str]] = {}
    for item in artifacts:
        if not isinstance(item, dict) or set(item) != {"role", "path", "sha256"}:
            raise AssertionError("the edge proof contains malformed artifact provenance")
        role = item["role"]
        if role not in ARTIFACT_PATHS or role in mapped:
            raise AssertionError("the edge proof repeats or changes an artifact role")
        relative = item["path"]
        if relative != ARTIFACT_PATHS[role]:
            raise AssertionError(f"edge proof changed the canonical {role} path")
        authorized = require_sha256(item["sha256"], role)
        artifact_path = (ROOT / relative).resolve()
        if artifact_path != ROOT / relative:
            raise AssertionError(f"the canonical {role} escaped the workspace")
        actual = sha256_path(artifact_path)
        if actual != authorized:
            raise AssertionError(
                f"edge proof does not authorize actual {role}: "
                f"expected {authorized}, observed {actual}"
            )
        mapped[role] = (relative, authorized)
    if set(mapped) != set(ARTIFACT_PATHS):
        raise AssertionError("the edge proof omitted a canonical artifact")
    provenance = {
        "schema": EDGE_SCHEMA,
        "path": str(source_path.resolve()),
        "archive_sha256": require_sha256(archive_sha256, "edge proof archive"),
        "script_sha256": EDGE_SCRIPT_SHA256,
        "seed": EDGE_SEED,
        "checks": EDGE_CHECKS,
        "category_count": EDGE_CATEGORIES,
        "reference_sha256": EDGE_REFERENCE_SHA256,
        "candidate_sha256": EDGE_REFERENCE_SHA256,
        "failed": 0,
        "candidate_artifacts": [
            {"role": role, "path": path, "sha256": value}
            for role, (path, value) in sorted(mapped.items())
        ],
    }
    return mapped, provenance


def read_edge_proof(
    suite: Any, path: Path
) -> tuple[dict[str, tuple[str, str]], dict[str, Any], dict[str, Any]]:
    resolved = path.resolve()
    if resolved == FROZEN_FAILURE:
        raise AssertionError("the frozen deep-contract failure is not an edge proof")
    try:
        raw = resolved.read_bytes()
    except OSError as error:
        raise AssertionError("the explicitly supplied edge proof is unavailable") from error
    if len(raw) < 10 or raw[:2] != b"\x1f\x8b":
        raise AssertionError("the explicit edge proof is not gzip")
    if raw[3] & 0x08 or raw[4:8] != b"\x00\x00\x00\x00":
        raise AssertionError("the explicit edge proof has nondeterministic metadata")
    try:
        document = json.loads(gzip.decompress(raw))
    except (OSError, ValueError, EOFError, UnicodeError) as error:
        raise AssertionError("the explicit edge proof cannot be decoded") from error
    archive_sha256 = hashlib.sha256(raw).hexdigest()
    artifacts, provenance = validate_edge_document(
        suite, document, archive_sha256, resolved
    )
    return artifacts, provenance, document


def verify_original_still_frozen() -> None:
    actual_suite = sha256_path(FROZEN_SUITE)
    actual_failure = sha256_path(FROZEN_FAILURE)
    if actual_suite != FROZEN_SUITE_SHA256:
        raise AssertionError("the immutable deep-contract source changed during the run")
    if actual_failure != FROZEN_FAILURE_SHA256:
        raise AssertionError("the preserved failing deep-contract archive was overwritten")


def validated_output(path: Path, temporary_root: Path | None = None) -> Path:
    resolved = path.resolve()
    if resolved == FROZEN_FAILURE.resolve():
        raise AssertionError("refusing to overwrite the preserved failing evidence")
    if not resolved.name.endswith(".json.gz"):
        raise AssertionError("variant evidence must have the .json.gz suffix")
    if temporary_root is None:
        if resolved.parent != AUDITS.resolve():
            raise AssertionError("variant output must remain directly in candidates/audits")
    else:
        if temporary_root.resolve().parent != Path("/tmp"):
            raise AssertionError("self-test evidence must remain in a /tmp temporary directory")
        if resolved.parent != temporary_root.resolve():
            raise AssertionError("self-test output escaped its /tmp temporary directory")
    if not resolved.parent.is_dir():
        raise AssertionError("the authorized output directory does not exist")
    return resolved


def evaluate_variant_worker(role: str, proof_path: Path) -> dict[str, Any]:
    suite = load_frozen_suite()
    original_failure(suite)
    artifacts, provenance, unused = read_edge_proof(suite, proof_path)
    if role in ("candidate", "poison"):
        suite.CANONICAL_ARTIFACTS = artifacts
    elif role not in ("stdlib-a", "stdlib-b"):
        raise AssertionError(f"unsupported isolated deep-contract worker: {role}")
    report = suite.evaluate_worker(role)
    if report.get("schema") != FROZEN_SCHEMA or report.get("role") != role:
        raise AssertionError("the frozen handler returned unexpected worker provenance")
    if report.get("seed") != FROZEN_SEED:
        raise AssertionError("the frozen handler changed the deep-contract seed")
    if report.get("checks") != FROZEN_CASES:
        raise AssertionError("the frozen handler changed the deep-contract denominator")
    if report.get("fixture_sha256") != FROZEN_FIXTURE_SHA256:
        raise AssertionError("the frozen handler changed the 393-case fixture")
    if role in ("candidate", "poison"):
        expected = provenance["candidate_artifacts"]
        if report.get("native_artifacts") != expected:
            raise AssertionError("worker native artifacts differ from its edge proof")
        if role == "poison" and report.get("guard_count") != 13:
            raise AssertionError("the frozen poison worker lost a delegation guard")
        if role == "candidate" and report.get("guard_count") != 13:
            raise AssertionError("the candidate did not preserve all poison guards")
    verify_original_still_frozen()
    return report


def run_variant_worker(suite: Any, role: str, proof_path: Path) -> dict[str, Any]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPATH"] = str(ROOT)
    command = [
        str(PINNED_EXECUTABLE),
        "-B",
        str(RUNNER),
        "--worker",
        role,
        "--edge-oracle",
        str(proof_path.resolve()),
    ]
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
            f"isolated frozen {role} worker failed ({result.returncode}): "
            f"{result.stderr[-10000:]} {result.stdout[-4000:]}"
        )
    try:
        report = json.loads(result.stdout)
    except (TypeError, ValueError) as error:
        raise AssertionError(f"isolated frozen {role} produced invalid JSON") from error
    if report.get("schema") != FROZEN_SCHEMA or report.get("role") != role:
        raise AssertionError(f"isolated frozen {role} has invalid provenance")
    if report.get("seed") != FROZEN_SEED or report.get("checks") != FROZEN_CASES:
        raise AssertionError(f"isolated frozen {role} changed its seed or cases")
    if report.get("fixture_sha256") != FROZEN_FIXTURE_SHA256:
        raise AssertionError(f"isolated frozen {role} changed the fixture")
    if role == "poison":
        if report.get("guard_count") != 13 or len(report.get("guards", ())) != 13:
            raise AssertionError("isolated poison self-test did not verify 13 guards")
        return report
    rows = report.get("observations")
    if not isinstance(rows, list) or len(rows) != FROZEN_CASES:
        raise AssertionError(f"isolated frozen {role} lost complete observations")
    if suite.digest(rows) != report.get("observation_sha256"):
        raise AssertionError(f"isolated frozen {role} has invalid observation integrity")
    if any(item.get("sha256") != suite.digest(item.get("observation")) for item in rows):
        raise AssertionError(f"isolated frozen {role} changed a per-case digest")
    if role in ("stdlib-a", "stdlib-b"):
        if report.get("observation_sha256") != FROZEN_REFERENCE_SHA256:
            raise AssertionError("isolated reference differs from the published reference")
    return report


def write_variant_report(suite: Any, path: Path, report: dict[str, Any]) -> str:
    verify_original_still_frozen()
    if path.resolve() == FROZEN_FAILURE.resolve():
        raise AssertionError("refusing to write the preserved original evidence")
    payload = suite.canonical(report)
    with path.open("wb") as raw:
        with gzip.GzipFile(
            filename="",
            fileobj=raw,
            mode="wb",
            compresslevel=9,
            mtime=0,
        ) as compressed:
            compressed.write(payload)
    raw = path.read_bytes()
    if len(raw) < 10 or raw[:2] != b"\x1f\x8b":
        raise AssertionError("variant evidence is not a valid gzip archive")
    if raw[3] & 0x08 or raw[4:8] != b"\x00\x00\x00\x00":
        raise AssertionError("variant gzip evidence is nondeterministic")
    if gzip.decompress(raw) != payload:
        raise AssertionError("variant evidence failed its canonical round-trip")
    verify_original_still_frozen()
    return hashlib.sha256(raw).hexdigest()


def build_variant_report(
    suite: Any,
    baseline: dict[str, Any],
    proof_path: Path,
) -> dict[str, Any]:
    authorized, proof, unused = read_edge_proof(suite, proof_path)
    reference_a = run_variant_worker(suite, "stdlib-a", proof_path)
    reference_b = run_variant_worker(suite, "stdlib-b", proof_path)
    reference_failures = suite.mismatches(
        reference_a["observations"], reference_b["observations"]
    )
    if reference_failures:
        raise AssertionError(
            "the frozen pinned references are nondeterministic: "
            + suite.canonical(reference_failures[:3]).decode("ascii")
        )
    if reference_a["observations"] != baseline["reference"]["observations"]:
        raise AssertionError("reference A differs from the immutable 393-case baseline")
    if reference_b["observations"] != baseline["reference_independent_repeat"]["observations"]:
        raise AssertionError("reference B differs from the immutable 393-case baseline")
    poison = run_variant_worker(suite, "poison", proof_path)
    differential = suite.verify_differential_self_test()
    candidate = run_variant_worker(suite, "candidate", proof_path)
    expected_artifacts = proof["candidate_artifacts"]
    if poison.get("native_artifacts") != expected_artifacts:
        raise AssertionError("the poison worker loaded unproven native artifacts")
    if candidate.get("native_artifacts") != expected_artifacts:
        raise AssertionError("the candidate worker loaded unproven native artifacts")
    failures = suite.mismatches(reference_a["observations"], candidate["observations"])
    topology = suite.diagnostic_differences(
        reference_a["implementation_private_gc_diagnostics"],
        candidate["implementation_private_gc_diagnostics"],
    )
    family_counts = collections.Counter(
        item.get("family", "missing") for item in failures
    )
    report = {
        "schema": FROZEN_SCHEMA,
        "status": "FAIL" if failures else "PASS",
        "python": "3.14.6",
        "seed": FROZEN_SEED,
        "seeded_case_count": FROZEN_SEEDED_CASES,
        "checks": FROZEN_CASES,
        "fixture_sha256": FROZEN_FIXTURE_SHA256,
        "suite_path": "tools/rust_v8_deep_contract_oracle.py",
        "suite_sha256": FROZEN_SUITE_SHA256,
        "reference_a_sha256": reference_a["observation_sha256"],
        "reference_b_sha256": reference_b["observation_sha256"],
        "candidate_sha256": candidate["observation_sha256"],
        "stdlib_vs_stdlib_mismatches": reference_failures,
        "public_mismatch_count": len(failures),
        "public_mismatch_family_counts": dict(sorted(family_counts.items())),
        "public_mismatches": failures,
        "implementation_private_gc_topology_difference_count": len(topology),
        "implementation_private_gc_topology_differences": topology,
        "implementation_private_gc_topology_policy": (
            "fully recorded and separately compared; explicitly not represented "
            "as documented public lifetime or collectability equality"
        ),
        "differential_poison_self_tests": differential,
        "forbidden_regex_guards": poison["guard_count"],
        "guard_observations": candidate["guard_observations"],
        "native_under_poison": poison["native_under_poison"],
        "native_artifacts": candidate["native_artifacts"],
        "reference": reference_a,
        "reference_independent_repeat": reference_b,
        "candidate": candidate,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
        "edge_oracle": proof,
        "frozen_failure_evidence": {
            "path": "candidates/audits/RUST-V8-DEEP-CONTRACT.json.gz",
            "archive_sha256": FROZEN_FAILURE_SHA256,
            "status": "FAIL",
            "public_mismatch_count": FROZEN_BASELINE_FAILURES,
        },
        "variant_runner": {
            "path": "tools/rust_v8_deep_contract_variant.py",
            "sha256": sha256_path(RUNNER),
        },
    }
    verify_original_still_frozen()
    return report


def summarize(
    report: dict[str, Any], output: Path, evidence_sha256: str
) -> dict[str, Any]:
    keys = (
        "schema",
        "status",
        "python",
        "seed",
        "seeded_case_count",
        "checks",
        "fixture_sha256",
        "suite_sha256",
        "reference_a_sha256",
        "reference_b_sha256",
        "candidate_sha256",
        "public_mismatch_count",
        "public_mismatch_family_counts",
        "implementation_private_gc_topology_difference_count",
        "forbidden_regex_guards",
        "native_artifacts",
        "performance",
        "holdout",
    )
    result = {key: report[key] for key in keys}
    result["stdlib_vs_stdlib_mismatches"] = len(
        report["stdlib_vs_stdlib_mismatches"]
    )
    result["differential_poison_self_tests"] = report[
        "differential_poison_self_tests"
    ]
    result["edge_oracle"] = report["edge_oracle"]
    result["frozen_failure_evidence"] = report["frozen_failure_evidence"]
    result["evidence_path"] = str(output)
    result["evidence_sha256"] = evidence_sha256
    if report["public_mismatches"]:
        result["first_public_mismatches"] = report["public_mismatches"][:8]
    return result


def run_gate(
    proof_path: Path,
    output_path: Path,
    temporary_root: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any], int]:
    suite = load_frozen_suite()
    baseline, unused = original_failure(suite)
    output = validated_output(output_path, temporary_root)
    report = build_variant_report(suite, baseline, proof_path)
    evidence_sha256 = write_variant_report(suite, output, report)
    summary = summarize(report, output, evidence_sha256)
    return report, summary, 1 if report["public_mismatches"] else 0


def expect_rejection(label: str, action: Any) -> dict[str, str]:
    try:
        action()
    except (AssertionError, OSError, RuntimeError, ValueError) as error:
        return {
            "status": "PASS",
            "rejected": label,
            "error_type": type(error).__name__,
        }
    raise AssertionError(f"the variant provenance poison unexpectedly passed: {label}")


def self_test(proof_path: Path) -> dict[str, Any]:
    suite = load_frozen_suite()
    baseline, original_bytes = original_failure(suite)
    artifacts, proof, document = read_edge_proof(suite, proof_path)
    if proof["archive_sha256"] != BASELINE_SELF_TEST_PROOF_SHA256:
        raise AssertionError("self-test requires the published restored baseline edge proof")
    if proof["candidate_artifacts"] != baseline["native_artifacts"]:
        raise AssertionError("self-test edge proof does not reproduce frozen baseline artifacts")
    if set(artifacts) != set(ARTIFACT_PATHS):
        raise AssertionError("self-test edge proof changed its five artifact roles")

    def changed_document(mutator: Any) -> Any:
        changed = copy.deepcopy(document)
        mutator(changed)
        return lambda: validate_edge_document(
            suite,
            changed,
            proof["archive_sha256"],
            proof_path.resolve(),
        )

    provenance_poisons = [
        expect_rejection(
            "incorrect-edge-schema",
            changed_document(lambda item: item.update({"schema": "poison"})),
        ),
        expect_rejection(
            "nonpassing-edge-proof",
            changed_document(lambda item: item.update({"failed": 1})),
        ),
        expect_rejection(
            "incorrect-edge-reference",
            changed_document(
                lambda item: item.update({"actual_sha256": "0" * 64})
            ),
        ),
        expect_rejection(
            "missing-authorized-artifact",
            changed_document(lambda item: item["candidate_artifacts"].pop()),
        ),
        expect_rejection(
            "stale-authorized-artifact",
            changed_document(
                lambda item: item["candidate_artifacts"][0].update(
                    {"sha256": "0" * 64}
                )
            ),
        ),
        expect_rejection(
            "artifact-path-traversal",
            changed_document(
                lambda item: item["candidate_artifacts"][0].update(
                    {"path": "candidates/../candidates/rust_candidate.py"}
                )
            ),
        ),
        expect_rejection(
            "incorrect-edge-denominator",
            changed_document(
                lambda item: item.update({"correctness_checks": EDGE_CHECKS - 1})
            ),
        ),
        expect_rejection(
            "overwrite-frozen-failure",
            lambda: validated_output(FROZEN_FAILURE),
        ),
        expect_rejection(
            "audit-output-traversal",
            lambda: validated_output(
                AUDITS / ".." / "RUST-V8-DEEP-CONTRACT-VARIANT.json.gz"
            ),
        ),
        expect_rejection(
            "incorrect-output-suffix",
            lambda: validated_output(AUDITS / "RUST-V8-DEEP-CONTRACT-VARIANT.json"),
        ),
    ]

    with tempfile.TemporaryDirectory(
        prefix="rebar-rust-v8-deep-contract-", dir="/tmp"
    ) as temporary:
        temporary_root = Path(temporary)
        provenance_poisons.append(
            expect_rejection(
                "missing-edge-proof",
                lambda: read_edge_proof(
                    suite, temporary_root / "missing-edge-proof.json.gz"
                ),
            )
        )
        provenance_poisons.append(
            expect_rejection(
                "temporary-output-traversal",
                lambda: validated_output(
                    temporary_root / ".." / "escaped.json.gz",
                    temporary_root,
                ),
            )
        )
        output = temporary_root / "RUST-V8-DEEP-CONTRACT-VARIANT-SELFTEST.json.gz"
        report, summary, gate_status = run_gate(
            proof_path, output, temporary_root=temporary_root
        )
        extension_keys = {"edge_oracle", "frozen_failure_evidence", "variant_runner"}
        reconstructed = {
            key: value for key, value in report.items() if key not in extension_keys
        }
        if suite.canonical(reconstructed) != suite.canonical(baseline):
            changed = sorted(
                key
                for key in set(reconstructed) | set(baseline)
                if reconstructed.get(key) != baseline.get(key)
            )
            raise AssertionError(
                "baseline variant failed to reproduce the complete immutable "
                f"393-case failure report: {changed}"
            )
        if gate_status != 1 or report["public_mismatch_count"] != 104:
            raise AssertionError("baseline self-test concealed genuine public failures")
        if report["candidate_sha256"] != FROZEN_BASELINE_CANDIDATE_SHA256:
            raise AssertionError("baseline self-test changed actual candidate observations")
        if report["stdlib_vs_stdlib_mismatches"]:
            raise AssertionError("baseline self-test changed the stdlib control")
        if len(report["guard_observations"]) != 13:
            raise AssertionError("baseline self-test changed its poison guards")
        temporary_sha256 = summary["evidence_sha256"]
    if FROZEN_FAILURE.read_bytes() != original_bytes:
        raise AssertionError("self-test modified the preserved failure archive")
    verify_original_still_frozen()
    return {
        "schema": FROZEN_SCHEMA,
        "mode": "variant-self-test",
        "status": "PASS",
        "python": "3.14.6",
        "seed": FROZEN_SEED,
        "checks": FROZEN_CASES,
        "fixture_sha256": FROZEN_FIXTURE_SHA256,
        "suite_path": "tools/rust_v8_deep_contract_oracle.py",
        "suite_sha256": FROZEN_SUITE_SHA256,
        "original_failure_sha256": FROZEN_FAILURE_SHA256,
        "original_failure_unchanged": True,
        "reference_a_sha256": FROZEN_REFERENCE_SHA256,
        "reference_b_sha256": FROZEN_REFERENCE_SHA256,
        "stdlib_vs_stdlib_mismatches": 0,
        "baseline_candidate_sha256": FROZEN_BASELINE_CANDIDATE_SHA256,
        "baseline_gate_status": "FAIL",
        "baseline_gate_exit": 1,
        "baseline_public_mismatches": FROZEN_BASELINE_FAILURES,
        "baseline_private_gc_differences": FROZEN_BASELINE_PRIVATE_DIFFERENCES,
        "baseline_report_reproduced_byte_for_byte": True,
        "forbidden_regex_guards": 13,
        "edge_oracle": proof,
        "provenance_poison_self_tests": provenance_poisons,
        "temporary_evidence_sha256": temporary_sha256,
        "temporary_evidence_removed": True,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run immutable deep-contract cases on a proof-authorized Rust variant."
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--gate", action="store_true")
    modes.add_argument(
        "--worker", choices=("stdlib-a", "stdlib-b", "candidate", "poison")
    )
    parser.add_argument("--edge-oracle", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--module", default=SUPPORTED_MODULE, choices=(SUPPORTED_MODULE,))
    return parser.parse_args(arguments)


def main(arguments: list[str]) -> int:
    options = parse_arguments(arguments)
    if options.self_test:
        if options.output is not None:
            raise AssertionError("self-test cannot write repository evidence")
        proof = options.edge_oracle or BASELINE_SELF_TEST_PROOF
        suite = load_frozen_suite()
        result = self_test(proof)
        print(suite.canonical(result).decode("ascii"))
        return 0
    if options.worker is not None:
        if options.edge_oracle is None or options.output is not None:
            raise AssertionError("isolated workers require only an explicit edge proof")
        suite = load_frozen_suite()
        report = evaluate_variant_worker(options.worker, options.edge_oracle)
        print(suite.canonical(report).decode("ascii"))
        return 0
    if options.edge_oracle is None or options.output is None:
        raise AssertionError("the variant gate requires explicit --edge-oracle and --output")
    report, summary, status = run_gate(options.edge_oracle, options.output)
    suite = load_frozen_suite()
    print(suite.canonical(summary).decode("ascii"))
    return status


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
