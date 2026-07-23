#!/usr/bin/env python3
"""Independently verify the final native-heap Rust public observability."""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

from tools import rust_v7_observability_oracle as frozen
from tools import rust_v7_observability_variant as original
from tools import rust_v8_deep_contract_oracle as deep
from tools import rust_v8_observability_variants as variants


SCHEMA = "rebar-rust-v8-native-heap-observability-v1"
PINNED_EXECUTABLE = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
VARIANTS_SOURCE_SHA256 = (
    "feeae4ba159c8094f88f30653a734f0177c42a835c3ecf8a5231095046f94cbe"
)
CMETHOD_ARCHIVE_SHA256 = (
    "06715db288a754ec324934d2f750dcb4d68908b2b971cccb62c30197ad8184d2"
)
NATIVE_EDGE_SHA256 = (
    "0c8748f78809e0f29f4bbacaad48296d4f51ca14445a4f9e8938376b37d85a21"
)
NATIVE_DEEP_SHA256 = (
    "f31ec92ffa7975406267ee9cdb29e2a3e0314d436d643ccfb34862f09956c2c5"
)
NATIVE_EDGE = (
    frozen.EVIDENCE / "rust-v8-edge-oracle-rust-native-heap-final.json.gz"
)
NATIVE_DEEP = (
    frozen.ROOT / "candidates/audits/RUST-V8-DEEP-CONTRACT-NATIVE-HEAP-FINAL.json.gz"
)
ARCHIVE = (
    frozen.EVIDENCE / "rust-v8-observability-native-heap-final.json.gz"
)
CURRENT_ARTIFACTS = {
    "bridge-source": (
        "candidates/rust/py_bridge.c",
        "6fc3b6f52a9e7beebfb099160f19565e8c5fb663fab899478bdc00ce9aac8ec7",
    ),
    "native-bridge": (
        "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "840497035864542caf33bdc80a7c1cf5f1a31414a8bd28699536927b3a4732c8",
    ),
    "native-engine": (
        "candidates/_rust_engine.so",
        "890f9e34e966244067a3dc173c2276043ae15d4830a05228fb37ec2571aa17cd",
    ),
    "native-source": (
        "candidates/rust/src/lib.rs",
        "a2fa04912bb1f6957f833560446f4d3d1c5d13df8b5efac992fa63e28803668b",
    ),
    "public-python": (
        "candidates/rust_candidate.py",
        "80812459261edb9585bdf703f137af3e0e788638af2ad7183d00b6d357e8a926",
    ),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython", "requires canonical CPython")
    require(
        tuple(sys.version_info[:3]) == frozen.PINNED,
        "requires pinned CPython 3.14.6",
    )
    require(
        Path(sys.executable).resolve() == PINNED_EXECUTABLE.resolve(),
        "requires the exact pinned CPython executable",
    )


def current_source() -> dict:
    source = Path(__file__).resolve()
    require(
        source == (frozen.ROOT / "tools/rust_v8_observability_native_heap.py").resolve(),
        "the native-heap observability verifier was replaced",
    )
    return {
        "path": source.relative_to(frozen.ROOT).as_posix(),
        "sha256": frozen.path_digest(source),
    }


def exact_artifacts() -> list[dict]:
    return [
        {"role": role, "path": path, "sha256": fingerprint}
        for role, (path, fingerprint) in sorted(CURRENT_ARTIFACTS.items())
    ]


def validate_current_edge(path: Path) -> dict:
    verify_runtime()
    requested = Path(path)
    require(not requested.is_symlink(), "native-heap edge cannot be a symlink")
    require(
        requested.resolve() == NATIVE_EDGE.resolve(),
        "only the frozen native-heap edge archive is authorized",
    )
    require(
        frozen.path_digest(NATIVE_EDGE) == NATIVE_EDGE_SHA256,
        "the frozen native-heap edge archive changed",
    )
    provenance, artifacts = frozen.validate_edge_oracle(NATIVE_EDGE)
    require(
        provenance.get("sha256") == NATIVE_EDGE_SHA256
        and provenance.get("checks") == frozen.EDGE_CHECKS
        and provenance.get("categories") == frozen.EDGE_CATEGORIES
        and provenance.get("failed") == 0,
        "the complete native-heap edge correctness proof changed",
    )
    require(
        provenance.get("artifacts") == exact_artifacts()
        and set(artifacts) == set(CURRENT_ARTIFACTS),
        "the edge does not authorize the exact five native-heap artifacts",
    )
    for role, (relative, fingerprint) in CURRENT_ARTIFACTS.items():
        source = (frozen.ROOT / relative).resolve()
        require(
            artifacts[role] == (source, fingerprint)
            and frozen.path_digest(source) == fingerprint,
            f"the current native-heap artifact changed: {role}",
        )
    return provenance


def historical_edge_provenance() -> dict:
    configuration = variants.VARIANTS["scanner-cmethod"]
    path = frozen.EVIDENCE / configuration.edge_name
    require(
        frozen.path_digest(path) == variants.CMETHOD_EDGE_SHA256,
        "the historical genuine-method edge archive changed",
    )
    resolved, report = frozen.read_edge_archive(path)
    artifacts = frozen.validate_edge_document(
        report,
        frozen.frozen_edge_baseline(),
        check_live_files=False,
    )
    return {
        "path": resolved.relative_to(frozen.ROOT).as_posix(),
        "sha256": variants.CMETHOD_EDGE_SHA256,
        "schema": report["schema"],
        "script_sha256": report["script_sha256"],
        "baseline_archive_sha256": frozen.EDGE_BASELINE_SHA256,
        "reference_sha256": report["expected_sha256"],
        "checks": report["correctness_checks"],
        "categories": len(report["categories"]),
        "failed": report["failed"],
        "artifacts": [
            {
                "role": role,
                "path": source.relative_to(frozen.ROOT).as_posix(),
                "sha256": fingerprint,
            }
            for role, (source, fingerprint) in sorted(artifacts.items())
        ],
    }


def validate_archived_cmethod(history: dict, first_scanner: dict) -> dict:
    variant_source = Path(variants.__file__).resolve()
    require(
        variant_source
        == (frozen.ROOT / "tools/rust_v8_observability_variants.py").resolve()
        and frozen.path_digest(variant_source) == VARIANTS_SOURCE_SHA256,
        "the preserved scanner-variant verifier source changed",
    )
    archive = frozen.EVIDENCE / "rust-v8-observability-scanner-cmethod.json.gz"
    report = variants.read_canonical_archive(archive, CMETHOD_ARCHIVE_SHA256)
    require(
        report.get("schema") == variants.SCHEMA
        and report.get("role") == "scanner-variant-observability"
        and report.get("variant") == "scanner-cmethod"
        and report.get("status") == "PASS"
        and report.get("python") == "3.14.6",
        "the preserved genuine-method scanner verdict changed",
    )
    require(
        report.get("checks") == 479
        and report.get("self_oracle_checks") == 479
        and report.get("candidate_checks") == 479
        and report.get("self_oracle_failures") == []
        and report.get("candidate_failures") == [],
        "the preserved genuine-method scanner hid a frozen observation",
    )
    require(
        report.get("goal_sha256") == original.GOAL_SHA256
        and report.get("seed") == frozen.SEED
        and report.get("fixture_sha256") == frozen.FROZEN_FIXTURE_SHA256,
        "the preserved genuine-method scanner fixture changed",
    )
    require(
        report.get("immutable_frozen_baseline") == history
        and report.get("preserved_first_scanner") == first_scanner,
        "the genuine-method stage omitted its immutable scanner history",
    )
    edge = historical_edge_provenance()
    require(
        report.get("edge_oracle") == edge,
        "the genuine-method stage was silently rebound to another edge",
    )
    standard_a = report.get("standard_library_a")
    standard_b = report.get("standard_library_b")
    candidate = report.get("candidate")
    for role, worker in (
        ("stdlib-a", standard_a),
        ("stdlib-b", standard_b),
        ("candidate", candidate),
    ):
        original.validate_worker(worker, role)
    require(
        frozen.mismatch_records(
            standard_a["observations"], standard_b["observations"]
        )
        == []
        and frozen.mismatch_records(
            standard_a["observations"], candidate["observations"]
        )
        == [],
        "the archived genuine-method scanner observations disagree",
    )
    require(
        report.get("expected_observation_sha256")
        == standard_a.get("observation_sha256")
        and report.get("actual_observation_sha256")
        == candidate.get("observation_sha256"),
        "the archived genuine-method observation fingerprint changed",
    )
    require(
        report.get("private_binder_checks") == 34
        and report.get("private_binder_failures") == []
        and candidate.get("private_binder_checks") == 34
        and candidate.get("private_binder_failures") == []
        and len(candidate.get("private_binder_observations", [])) == 34
        and all(
            row.get("passed") is True
            for row in candidate["private_binder_observations"]
        ),
        "a historical genuine-method private binder was removed",
    )
    guards = candidate.get("forbidden_regex_guard_observations", [])
    require(
        report.get("forbidden_regex_guards") == 13
        and candidate.get("forbidden_regex_guards") == 13
        and len(guards) == 13
        and len({row.get("id") for row in guards}) == 13
        and all(row.get("passed") is True for row in guards),
        "a historical genuine-method regex guard was removed",
    )
    require(
        candidate.get("native_artifacts") == edge["artifacts"]
        and report.get("native_artifacts") == edge["artifacts"]
        and candidate.get("edge_oracle") == edge,
        "historical genuine-method native artifacts were replaced",
    )
    require(
        report.get("private_binder_report")
        == frozen.private_binder_report(candidate)
        and report.get("resolved_iterator_controls")
        == original.classify_resolved_iterators(standard_a, candidate),
        "historical scanner binders or genuine callable iterators changed",
    )
    preserved_deep = variants.validate_preserved_deep(edge)
    require(
        report.get("preserved_deep_contract") == preserved_deep,
        "the historical honest 43-failure deep-contract report was hidden",
    )
    controls = report.get("negative_controls", [])
    self_references = report.get("self_reference_controls", [])
    require(
        len(controls) == 31
        and len({row.get("id") for row in controls}) == 31
        and all(row.get("passed") is True for row in controls)
        and len(self_references) == 4
        and all(row.get("passed") is True for row in self_references),
        "historical genuine-method tamper controls were hidden",
    )
    require(
        report.get("script")
        == {
            "path": "tools/rust_v8_observability_variants.py",
            "sha256": VARIANTS_SOURCE_SHA256,
        }
        and report.get("holdout") == "NOT ACCESSED"
        and report.get("performance") == "NOT MEASURED",
        "the genuine-method source or benchmark-blind scope changed",
    )
    return {
        "source": report["script"],
        "archive": {
            "path": archive.relative_to(frozen.ROOT).as_posix(),
            "sha256": CMETHOD_ARCHIVE_SHA256,
        },
        "edge": edge,
        "checks": 479,
        "private_binder_checks": 34,
        "forbidden_regex_guards": 13,
        "negative_controls": 31,
        "report": report,
    }


def validate_native_deep_document(report: dict, edge: dict) -> None:
    require(
        report.get("schema") == deep.SCHEMA
        and report.get("status") == "PASS"
        and report.get("python") == "3.14.6"
        and report.get("seed") == deep.SEED
        and report.get("checks") == 393
        and report.get("public_mismatch_count") == 0
        and report.get("public_mismatches") == []
        and report.get("public_mismatch_family_counts") == {},
        "the complete native-heap deep-contract pass changed",
    )
    cases = deep.build_cases()
    require(
        len(cases) == 393
        and deep.digest(cases) == variants.DEEP_FIXTURE_SHA256
        and report.get("fixture_sha256") == variants.DEEP_FIXTURE_SHA256,
        "the frozen 393-case deep-contract fixture changed",
    )
    expected_ids = [case["id"] for case in cases]
    for name, role in (
        ("reference", "stdlib-a"),
        ("reference_independent_repeat", "stdlib-b"),
        ("candidate", "candidate"),
    ):
        worker = report.get(name)
        require(
            isinstance(worker, dict) and worker.get("role") == role,
            f"the 393-case {role} worker was replaced",
        )
        rows = worker.get("observations")
        require(
            worker.get("checks") == 393
            and isinstance(rows, list)
            and len(rows) == 393
            and [row.get("id") for row in rows] == expected_ids,
            f"the 393-case {role} observations changed",
        )
        require(
            deep.digest(rows) == worker.get("observation_sha256")
            and all(
                deep.digest(row.get("observation")) == row.get("sha256")
                for row in rows
            ),
            f"the 393-case {role} observation fingerprint was poisoned",
        )
    expected = report["reference"]["observations"]
    repeated = report["reference_independent_repeat"]["observations"]
    candidate = report["candidate"]["observations"]
    require(
        report.get("stdlib_vs_stdlib_mismatches") == []
        and deep.mismatches(expected, repeated) == [],
        "the 393-case independent Python references disagree",
    )
    require(
        deep.mismatches(expected, candidate) == [],
        "a genuine 393-case native-heap public mismatch was concealed",
    )
    guards = report.get("guard_observations")
    require(
        report.get("forbidden_regex_guards") == 13
        and isinstance(guards, list)
        and len(guards) == 13
        and len({(row.get("module"), row.get("name")) for row in guards}) == 13
        and all(row.get("type") == "GuardSignal" for row in guards)
        and report["candidate"].get("guard_count") == 13,
        "a 393-case native regex-delegation guard was hidden",
    )
    require(
        report.get("native_artifacts") == edge.get("artifacts")
        and report.get("native_artifacts") == exact_artifacts(),
        "the deep-contract native build differs from the authorized edge",
    )
    proof = report.get("edge_oracle", {})
    require(
        proof.get("archive_sha256") == edge.get("sha256")
        and proof.get("path") == str(NATIVE_EDGE.resolve())
        and proof.get("schema") == frozen.EDGE_SCHEMA
        and proof.get("script_sha256") == frozen.EDGE_SCRIPT_SHA256
        and proof.get("seed") == frozen.EDGE_SEED
        and proof.get("checks") == frozen.EDGE_CHECKS
        and proof.get("category_count") == frozen.EDGE_CATEGORIES
        and proof.get("failed") == 0
        and proof.get("reference_sha256") == frozen.EDGE_REFERENCE_SHA256
        and proof.get("candidate_sha256") == frozen.EDGE_REFERENCE_SHA256
        and proof.get("candidate_artifacts") == edge.get("artifacts"),
        "the complete deep-contract pass is not bound to its frozen edge",
    )
    require(
        report.get("suite_path") == "tools/rust_v8_deep_contract_oracle.py"
        and report.get("suite_sha256") == variants.DEEP_SOURCE_SHA256
        and frozen.path_digest(Path(deep.__file__).resolve())
        == variants.DEEP_SOURCE_SHA256,
        "the immutable deep-contract source was replaced",
    )
    require(
        report.get("variant_runner")
        == {
            "path": "tools/rust_v8_deep_contract_variant.py",
            "sha256": variants.DEEP_RUNNER_SHA256,
        }
        and frozen.path_digest(
            frozen.ROOT / "tools/rust_v8_deep_contract_variant.py"
        )
        == variants.DEEP_RUNNER_SHA256,
        "the canonical deep-contract variant runner changed",
    )
    failure = report.get("frozen_failure_evidence", {})
    require(
        failure.get("path") == "candidates/audits/RUST-V8-DEEP-CONTRACT.json.gz"
        and failure.get("archive_sha256") == variants.DEEP_FAILURE_SHA256
        and failure.get("public_mismatch_count") == 104
        and failure.get("status") == "FAIL"
        and frozen.path_digest(variants.DEEP_FAILURE)
        == variants.DEEP_FAILURE_SHA256,
        "the original honest 104-failure deep-contract archive was hidden",
    )
    require(
        report.get("holdout") == "NOT ACCESSED"
        and report.get("performance") == "NOT MEASURED",
        "the deep-contract proof accessed performance or holdout data",
    )


def validate_current_deep(edge: dict) -> dict:
    require(
        frozen.path_digest(NATIVE_DEEP) == NATIVE_DEEP_SHA256,
        "the frozen native-heap deep-contract archive changed",
    )
    report = variants.read_canonical_archive(NATIVE_DEEP, NATIVE_DEEP_SHA256)
    validate_native_deep_document(report, edge)
    return {
        "archive": {
            "path": NATIVE_DEEP.relative_to(frozen.ROOT).as_posix(),
            "sha256": NATIVE_DEEP_SHA256,
        },
        "status": "PASS",
        "checks": 393,
        "public_mismatch_count": 0,
        "stdlib_vs_stdlib_mismatches": 0,
        "forbidden_regex_guards": 13,
        "original_public_mismatch_count": 104,
        "edge_archive_sha256": edge["sha256"],
        "report": report,
    }


def collect_negative_controls(
    standard_a: dict,
    standard_b: dict,
    candidate: dict,
    edge: dict,
    deep_report: dict,
) -> list[dict]:
    controls = original.collect_negative_controls(
        standard_a, standard_b, candidate, edge
    )

    def reject_candidate(label: str, mutate) -> dict:
        changed = original.clone(candidate)
        mutate(changed)
        return original.expect_rejection(
            label,
            lambda: original.validate_live_reports(
                standard_a, standard_b, changed, edge
            ),
        )

    def duplicate_observation(report: dict) -> None:
        report["observations"][1] = original.clone(report["observations"][0])
        report["observation_sha256"] = frozen.value_digest(report["observations"])

    def reorder_observations(report: dict) -> None:
        rows = report["observations"]
        rows[0], rows[1] = rows[1], rows[0]
        report["observation_sha256"] = frozen.value_digest(rows)

    def duplicate_guard(report: dict) -> None:
        rows = report["forbidden_regex_guard_observations"]
        rows[1] = original.clone(rows[0])

    def omit_private(report: dict) -> None:
        report["private_binder_observations"].pop()

    def stale_edge_path(report: dict) -> None:
        report["edge_oracle"]["path"] = (
            "candidates/evidence/rust-v8-edge-oracle-rust-scanner-cmethod.json.gz"
        )

    def stale_edge_hash(report: dict) -> None:
        report["edge_oracle"]["sha256"] = variants.CMETHOD_EDGE_SHA256

    def poison_edge_source(report: dict) -> None:
        report["edge_oracle"]["script_sha256"] = "0" * 64

    def poison_edge_reference(report: dict) -> None:
        report["edge_oracle"]["reference_sha256"] = "0" * 64

    def wrong_role(report: dict) -> None:
        report["role"] = "stdlib-a"

    def access_holdout(report: dict) -> None:
        report["holdout"] = "ACCESSED"

    def measure_performance(report: dict) -> None:
        report["performance"] = "MEASURED"

    mutations = (
        ("duplicate-frozen-public-observation", duplicate_observation),
        ("reordered-frozen-public-observations", reorder_observations),
        ("duplicated-regex-delegation-guard", duplicate_guard),
        ("missing-private-native-binder", omit_private),
        ("stale-historical-scanner-edge-path", stale_edge_path),
        ("stale-historical-scanner-edge-hash", stale_edge_hash),
        ("poisoned-native-heap-edge-source", poison_edge_source),
        ("poisoned-native-heap-edge-reference", poison_edge_reference),
        ("swapped-candidate-worker-role", wrong_role),
        ("forbidden-holdout-access", access_holdout),
        ("forbidden-performance-measurement", measure_performance),
    )
    controls.extend(
        reject_candidate(label, mutation) for label, mutation in mutations
    )

    def reject_deep(label: str, mutate) -> dict:
        changed = original.clone(deep_report)
        mutate(changed)
        return original.expect_rejection(
            label,
            lambda: validate_native_deep_document(changed, edge),
        )

    def deep_poison_observation(report: dict) -> None:
        report["candidate"]["observations"][0]["observation"] = {
            "poisoned": True
        }

    def deep_reorder_observations(report: dict) -> None:
        rows = report["candidate"]["observations"]
        rows[0], rows[1] = rows[1], rows[0]
        report["candidate"]["observation_sha256"] = deep.digest(rows)

    deep_mutations = (
        (
            "forged-native-heap-deep-pass-status",
            lambda report: report.update(status="FAIL"),
        ),
        (
            "hidden-native-heap-deep-public-mismatch",
            lambda report: report.update(public_mismatch_count=1),
        ),
        (
            "truncated-native-heap-deep-reference",
            lambda report: report["reference"]["observations"].pop(),
        ),
        (
            "truncated-native-heap-deep-candidate",
            lambda report: report["candidate"]["observations"].pop(),
        ),
        ("poisoned-native-heap-deep-observation", deep_poison_observation),
        (
            "reordered-native-heap-deep-observations",
            deep_reorder_observations,
        ),
        (
            "stale-native-heap-deep-edge-hash",
            lambda report: report["edge_oracle"].update(
                archive_sha256=variants.CMETHOD_EDGE_SHA256
            ),
        ),
        (
            "stale-native-heap-deep-native-artifacts",
            lambda report: report["native_artifacts"][0].update(
                sha256="0" * 64
            ),
        ),
        (
            "poisoned-native-heap-deep-suite-source",
            lambda report: report.update(suite_sha256="0" * 64),
        ),
        (
            "hidden-native-heap-deep-regex-guard",
            lambda report: report["guard_observations"].pop(),
        ),
        (
            "poisoned-native-heap-deep-regex-guard",
            lambda report: report["guard_observations"][0].update(
                type="DelegationAccepted"
            ),
        ),
        (
            "hidden-original-deep-contract-failure-history",
            lambda report: report["frozen_failure_evidence"].update(
                public_mismatch_count=0
            ),
        ),
        (
            "poisoned-native-heap-deep-frozen-fixture",
            lambda report: report.update(fixture_sha256="0" * 64),
        ),
    )
    controls.extend(
        reject_deep(label, mutation) for label, mutation in deep_mutations
    )
    require(len(controls) == 40, "native-heap tamper-control denominator changed")
    require(
        len({row.get("id") for row in controls}) == 40
        and all(row.get("passed") is True for row in controls),
        "a poisoned native-heap observation, artifact, or guard was accepted",
    )
    return controls


def make_report(edge_path: Path) -> dict:
    verify_runtime()
    history = original.check_frozen_history()
    first_scanner = variants.validate_archived_first_scanner(history)
    cmethod_scanner = validate_archived_cmethod(history, first_scanner)
    edge = validate_current_edge(edge_path)
    deep_evidence = validate_current_deep(edge)
    standard_a = frozen.run_worker("stdlib-a")
    standard_b = frozen.run_worker("stdlib-b")
    candidate = frozen.run_worker("candidate", edge_oracle=NATIVE_EDGE)
    validation = original.validate_live_reports(
        standard_a, standard_b, candidate, edge
    )
    controls = collect_negative_controls(
        standard_a, standard_b, candidate, edge, deep_evidence["report"]
    )
    return {
        "schema": SCHEMA,
        "role": "native-heap-observability",
        "variant": "native-heap",
        "status": "PASS",
        "python": "3.14.6",
        "python_executable": str(PINNED_EXECUTABLE.resolve()),
        "seed": frozen.SEED,
        "goal_sha256": original.GOAL_SHA256,
        "fixture_sha256": frozen.FROZEN_FIXTURE_SHA256,
        "checks": 479,
        "self_oracle_checks": 479,
        "self_oracle_failures": validation["self_oracle_failures"],
        "candidate_checks": 479,
        "candidate_failures": validation["candidate_failures"],
        "private_binder_checks": 34,
        "private_binder_failures": [],
        "forbidden_regex_guards": 13,
        "negative_controls": controls,
        "negative_control_failures": 0,
        "immutable_frozen_baseline": history,
        "preserved_first_scanner": first_scanner,
        "preserved_cmethod_scanner": cmethod_scanner,
        "preserved_deep_contract": deep_evidence,
        "edge_oracle": edge,
        "standard_library_a": standard_a,
        "standard_library_b": standard_b,
        "candidate": candidate,
        "private_binder_report": validation["private_binder_report"],
        "resolved_iterator_controls": validation["resolved_iterator_controls"],
        "native_artifacts": candidate["native_artifacts"],
        "expected_observation_sha256": standard_a["observation_sha256"],
        "actual_observation_sha256": candidate["observation_sha256"],
        "script": current_source(),
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def validate_report(report: dict, edge_path: Path) -> None:
    verify_runtime()
    require(isinstance(report, dict), "native-heap evidence is not an object")
    require(
        report.get("schema") == SCHEMA
        and report.get("role") == "native-heap-observability"
        and report.get("variant") == "native-heap"
        and report.get("status") == "PASS"
        and report.get("python") == "3.14.6"
        and report.get("python_executable") == str(PINNED_EXECUTABLE.resolve()),
        "the native-heap verifier or pinned Python was replaced",
    )
    require(
        report.get("seed") == frozen.SEED
        and report.get("goal_sha256") == original.GOAL_SHA256
        and frozen.path_digest(frozen.ROOT / "GOAL.md") == original.GOAL_SHA256
        and report.get("fixture_sha256") == frozen.FROZEN_FIXTURE_SHA256,
        "the immutable goal or complete observability fixture changed",
    )
    require(
        report.get("checks") == 479
        and report.get("self_oracle_checks") == 479
        and report.get("candidate_checks") == 479
        and report.get("self_oracle_failures") == []
        and report.get("candidate_failures") == [],
        "the complete 479-case observable public contract did not pass",
    )
    require(
        report.get("private_binder_checks") == 34
        and report.get("private_binder_failures") == []
        and report.get("forbidden_regex_guards") == 13,
        "the private native-binder or regex-delegation controls changed",
    )
    require(
        report.get("script") == current_source(),
        "the native-heap verifier source self-reference was poisoned",
    )
    require(
        report.get("holdout") == "NOT ACCESSED"
        and report.get("performance") == "NOT MEASURED",
        "native-heap correctness evidence accessed a holdout or benchmark",
    )
    history = original.check_frozen_history()
    require(
        report.get("immutable_frozen_baseline") == history,
        "the immutable original observability proof was hidden",
    )
    first_scanner = variants.validate_archived_first_scanner(history)
    require(
        report.get("preserved_first_scanner") == first_scanner,
        "the first-scanner observability archive was changed or omitted",
    )
    cmethod_scanner = validate_archived_cmethod(history, first_scanner)
    require(
        report.get("preserved_cmethod_scanner") == cmethod_scanner,
        "the genuine-method observability archive was changed or omitted",
    )
    edge = validate_current_edge(edge_path)
    require(
        report.get("edge_oracle") == edge,
        "the final native-heap proof was rebound to a different edge",
    )
    deep_evidence = validate_current_deep(edge)
    require(
        report.get("preserved_deep_contract") == deep_evidence,
        "the complete frozen 393-case native-heap proof was omitted",
    )
    standard_a = report.get("standard_library_a")
    standard_b = report.get("standard_library_b")
    candidate = report.get("candidate")
    validation = original.validate_live_reports(
        standard_a, standard_b, candidate, edge
    )
    require(
        report.get("private_binder_report")
        == validation["private_binder_report"]
        and report.get("resolved_iterator_controls")
        == validation["resolved_iterator_controls"]
        and validation["resolved_iterator_controls"].get("checks") == 2
        and validation["resolved_iterator_controls"].get(
            "genuine_public_mismatches"
        )
        == 0,
        "a private binder or genuine callable iterator was hidden",
    )
    require(
        report.get("native_artifacts") == exact_artifacts()
        and report.get("native_artifacts") == candidate.get("native_artifacts")
        and report.get("native_artifacts") == edge.get("artifacts"),
        "one of the exact five current native artifacts was substituted",
    )
    require(
        report.get("expected_observation_sha256")
        == standard_a.get("observation_sha256")
        and report.get("actual_observation_sha256")
        == candidate.get("observation_sha256")
        and report.get("expected_observation_sha256")
        == report.get("actual_observation_sha256"),
        "the complete public-observation fingerprint was changed",
    )
    controls = report.get("negative_controls")
    require(
        isinstance(controls, list)
        and len(controls) == 40
        and len({row.get("id") for row in controls}) == 40
        and all(row.get("passed") is True for row in controls)
        and report.get("negative_control_failures") == 0,
        "a native-heap no-delegation or evidence-forgery control failed",
    )
    self_references = report.get("self_reference_controls")
    if self_references is not None:
        require(
            isinstance(self_references, list)
            and len(self_references) == 6
            and len({row.get("id") for row in self_references}) == 6
            and all(row.get("passed") is True for row in self_references),
            "a native-heap source or historical archive poison was accepted",
        )


def self_reference_controls(report: dict, edge_path: Path) -> list[dict]:
    mutations = (
        (
            "poisoned-native-heap-verifier-source-self-reference",
            lambda item: item["script"].update(sha256="0" * 64),
        ),
        (
            "poisoned-immutable-original-oracle-source-reference",
            lambda item: item["immutable_frozen_baseline"]["source"].update(
                sha256="0" * 64
            ),
        ),
        (
            "poisoned-first-scanner-archive-reference",
            lambda item: item["preserved_first_scanner"]["archive"].update(
                sha256="0" * 64
            ),
        ),
        (
            "poisoned-genuine-method-scanner-archive-reference",
            lambda item: item["preserved_cmethod_scanner"]["archive"].update(
                sha256="0" * 64
            ),
        ),
        (
            "poisoned-native-heap-deep-archive-reference",
            lambda item: item["preserved_deep_contract"]["archive"].update(
                sha256="0" * 64
            ),
        ),
        (
            "poisoned-native-heap-edge-archive-reference",
            lambda item: item["edge_oracle"].update(sha256="0" * 64),
        ),
    )
    controls = []
    for label, mutation in mutations:
        changed = original.clone(report)
        mutation(changed)
        controls.append(
            original.expect_rejection(
                label, lambda value=changed: validate_report(value, edge_path)
            )
        )
    require(
        len(controls) == 6
        and all(row.get("passed") is True for row in controls),
        "a native-heap source or archive self-reference poison was accepted",
    )
    return controls


def write_archive(report: dict, edge_path: Path) -> str:
    require(
        ARCHIVE.resolve()
        == (
            frozen.EVIDENCE / "rust-v8-observability-native-heap-final.json.gz"
        ).resolve(),
        "refusing to replace historical or unrelated correctness evidence",
    )
    validate_report(report, edge_path)
    require(not ARCHIVE.is_symlink(), "native-heap evidence cannot be a symlink")
    require(not ARCHIVE.exists(), "native-heap evidence already exists")
    payload = variants.canonical_archive(report)
    require(
        payload == variants.canonical_archive(report),
        "native-heap evidence compression is nondeterministic",
    )
    with ARCHIVE.open("xb") as output:
        output.write(payload)
    persisted = variants.read_canonical_archive(ARCHIVE)
    require(persisted == report, "native-heap archive changed during its round-trip")
    validate_report(persisted, edge_path)
    return frozen.path_digest(ARCHIVE)


def announce(
    report: dict,
    *,
    phase: str,
    archive_sha256: str | None = None,
) -> None:
    summary = {
        "schema": SCHEMA,
        "phase": phase,
        "variant": "native-heap",
        "status": report["status"],
        "checks": report["checks"],
        "self_oracle_checks": report["self_oracle_checks"],
        "self_oracle_failures": len(report["self_oracle_failures"]),
        "candidate_checks": report["candidate_checks"],
        "candidate_failures": len(report["candidate_failures"]),
        "private_binder_checks": report["private_binder_checks"],
        "private_binder_failures": len(report["private_binder_failures"]),
        "forbidden_regex_guards": report["forbidden_regex_guards"],
        "genuine_callable_iterators": report["resolved_iterator_controls"][
            "checks"
        ],
        "native_artifacts": len(report["native_artifacts"]),
        "negative_controls": len(report["negative_controls"]),
        "negative_control_failures": report["negative_control_failures"],
        "self_reference_controls": len(
            report.get("self_reference_controls", [])
        ),
        "preserved_first_scanner_checks": report[
            "preserved_first_scanner"
        ]["checks"],
        "preserved_cmethod_scanner_checks": report[
            "preserved_cmethod_scanner"
        ]["checks"],
        "deep_checks": report["preserved_deep_contract"]["checks"],
        "deep_public_mismatches": report["preserved_deep_contract"][
            "public_mismatch_count"
        ],
        "edge_checks": report["edge_oracle"]["checks"],
        "edge_failed": report["edge_oracle"]["failed"],
        "script_sha256": report["script"]["sha256"],
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    if archive_sha256 is not None:
        summary["archive"] = ARCHIVE.relative_to(frozen.ROOT).as_posix()
        summary["archive_sha256"] = archive_sha256
    print(json.dumps(summary, ensure_ascii=True, sort_keys=True), flush=True)


def main() -> int:
    verify_runtime()
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command, description in (
        ("self-test", "verify frozen history and every tamper control"),
        ("candidate", "write the immutable native-heap observable proof"),
        ("verify", "verify the preserved native-heap observable proof"),
    ):
        option = commands.add_parser(command, help=description)
        option.add_argument("--edge-oracle", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "verify":
        validate_current_edge(args.edge_oracle)
        report = variants.read_canonical_archive(ARCHIVE)
        validate_report(report, args.edge_oracle)
        require(
            len(report.get("self_reference_controls", [])) == 6,
            "the archived native-heap source controls are missing",
        )
        announce(
            report,
            phase="verify",
            archive_sha256=frozen.path_digest(ARCHIVE),
        )
        return 0

    report = make_report(args.edge_oracle)
    validate_report(report, args.edge_oracle)
    report["self_reference_controls"] = self_reference_controls(
        report, args.edge_oracle
    )
    validate_report(report, args.edge_oracle)
    if args.command == "self-test":
        require(
            variants.canonical_archive(report)
            == variants.canonical_archive(report),
            "native-heap evidence cannot be compressed reproducibly",
        )
        announce(report, phase="self-test")
        return 0
    fingerprint = write_archive(report, args.edge_oracle)
    announce(report, phase="candidate", archive_sha256=fingerprint)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
