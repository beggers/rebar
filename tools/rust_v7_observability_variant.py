#!/usr/bin/env python3
"""Verify the corrected Rust scanner without changing its frozen observability oracle."""

from __future__ import annotations

import argparse
import collections
import contextlib
import copy
import gzip
import hashlib
import io
import json
import sys
from pathlib import Path

from tools import rust_v7_observability_oracle as frozen


SCHEMA = "rebar-rust-v8-scanner-lifetime-observability-v1"
FROZEN_SOURCE_SHA256 = (
    "931da02cbc819ba2ae9fed4fcf7bcd676e729c767fb804c9fc5be0429f76c4f7"
)
FROZEN_MANIFEST_SHA256 = (
    "ef6d102b214e9dfc14e88e13e37fec2ebad633024a2349181ce062e6a11e59fa"
)
FROZEN_REJECTED_SHA256 = (
    "e0e5d3abe4f252d0b76b373fc7847ecabf39b31ae4b08f10b142c324dff04edf"
)
SCANNER_EDGE_SHA256 = (
    "113fd5cae48a4e808d782259bbc116b47a8eee68f22afa8b5cd74f77803dc288"
)
GOAL_SHA256 = (
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
)
SCANNER_EDGE = (
    frozen.EVIDENCE / "rust-v8-edge-oracle-rust-scanner-lifetimes.json.gz"
)
VARIANT_ARCHIVE = (
    frozen.EVIDENCE / "rust-v8-observability-scanner-lifetimes.json.gz"
)
ITERATOR_IDS = (
    "malicious-public-binder/finditer/shape=end-index/mode=value",
    "malicious-public-binder/finditer/shape=index/mode=value",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def clone(value):
    return copy.deepcopy(value)


def current_source() -> dict:
    path = Path(__file__).resolve()
    return {
        "path": path.relative_to(frozen.ROOT).as_posix(),
        "sha256": frozen.path_digest(path),
    }


def check_frozen_history() -> dict:
    require(tuple(sys.version_info[:3]) == frozen.PINNED, "requires pinned CPython 3.14.6")
    require(
        frozen.path_digest(frozen.ROOT / "GOAL.md") == GOAL_SHA256,
        "the immutable objective changed",
    )
    source = Path(frozen.__file__).resolve()
    require(
        source == (frozen.ROOT / "tools/rust_v7_observability_oracle.py").resolve(),
        "the immutable observability source was replaced",
    )
    require(
        frozen.path_digest(source) == FROZEN_SOURCE_SHA256,
        "the immutable observability source hash changed",
    )
    cases = frozen.build_cases()
    require(len(cases) == 479, "the frozen observability denominator changed")
    require(
        frozen.value_digest(cases) == frozen.FROZEN_FIXTURE_SHA256,
        "the frozen observability fixture changed",
    )

    manifest_path = frozen.EVIDENCE / frozen.ARCHIVE_NAMES["manifest"]
    rejected_path = frozen.EVIDENCE / frozen.ARCHIVE_NAMES["rejected-iterator-control"]
    require(
        frozen.path_digest(manifest_path) == FROZEN_MANIFEST_SHA256,
        "the historical observability manifest changed",
    )
    require(
        frozen.path_digest(rejected_path) == FROZEN_REJECTED_SHA256,
        "the historical iterator false-positive archive changed",
    )

    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        result = frozen.verify_evidence()
    require(result == 0, "immutable observability evidence no longer verifies")
    output = captured.getvalue().splitlines()
    require(len(output) == 1, "immutable observability verification output changed")
    verification = json.loads(output[0])
    require(verification.get("status") == "PASS", "the historical baseline does not pass")
    require(verification.get("checks") == 479, "the historical baseline is incomplete")
    require(
        verification.get("private_binder_checks") == 34
        and verification.get("private_binder_failures") == 0,
        "the historical private binder controls changed",
    )
    require(
        verification.get("forbidden_regex_guards") == 13,
        "the historical delegation guard denominator changed",
    )
    require(
        verification.get("rejected_iterator_false_positives") == 2
        and verification.get("genuine_public_iterator_mismatches") == 0,
        "the historical iterator false positives changed",
    )

    historical_standard = frozen.read_report(
        frozen.EVIDENCE / frozen.ARCHIVE_NAMES["stdlib-a"]
    )
    historical_candidate = frozen.read_report(
        frozen.EVIDENCE / frozen.ARCHIVE_NAMES["candidate"]
    )
    archived_rejection = frozen.read_report(rejected_path)
    reproduced = frozen.rejected_iterator_report(
        historical_standard, historical_candidate
    )
    require(
        reproduced == archived_rejection,
        "the original private iterator false positives were not reproduced",
    )
    require(
        tuple(row["id"] for row in reproduced["observations"]) == ITERATOR_IDS,
        "the historical iterator identities changed",
    )

    poison_controls = frozen.edge_provenance_self_test()
    require(len(poison_controls) == 10, "the frozen evidence-poison denominator changed")
    require(
        all(row.get("passed") is True for row in poison_controls),
        "an immutable edge-evidence poison was accepted",
    )

    return {
        "source": {
            "path": source.relative_to(frozen.ROOT).as_posix(),
            "sha256": FROZEN_SOURCE_SHA256,
        },
        "manifest": {
            "path": manifest_path.relative_to(frozen.ROOT).as_posix(),
            "sha256": FROZEN_MANIFEST_SHA256,
        },
        "rejected_iterator_archive": {
            "path": rejected_path.relative_to(frozen.ROOT).as_posix(),
            "sha256": FROZEN_REJECTED_SHA256,
        },
        "verification": verification,
        "reproduced_historical_iterator_control": reproduced,
        "frozen_artifact_poison_controls": poison_controls,
    }


def validated_scanner_edge(path: Path) -> dict:
    requested = Path(path)
    require(not requested.is_symlink(), "the scanner edge oracle must not be a symlink")
    require(
        requested.resolve() == SCANNER_EDGE.resolve(),
        "only the frozen scanner-lifetime edge oracle is authorized",
    )
    require(
        frozen.path_digest(SCANNER_EDGE) == SCANNER_EDGE_SHA256,
        "the frozen scanner-lifetime edge oracle changed",
    )
    provenance, _ = frozen.validate_edge_oracle(SCANNER_EDGE)
    require(
        provenance.get("sha256") == SCANNER_EDGE_SHA256,
        "the scanner edge provenance does not identify its frozen archive",
    )
    require(
        provenance.get("checks") == frozen.EDGE_CHECKS
        and provenance.get("categories") == frozen.EDGE_CATEGORIES
        and provenance.get("failed") == 0,
        "the scanner edge correctness proof is incomplete",
    )
    require(len(provenance.get("artifacts", [])) == 5, "five scanner artifacts are required")
    return provenance


def validate_worker(report: dict, role: str) -> None:
    require(report.get("schema") == frozen.SCHEMA, "worker evidence schema changed")
    require(report.get("role") == role, "worker role changed")
    require(report.get("python") == "3.14.6", "worker Python version changed")
    require(report.get("seed") == frozen.SEED, "worker seed changed")
    require(
        report.get("fixture_sha256") == frozen.FROZEN_FIXTURE_SHA256,
        "worker fixture digest changed",
    )
    observations = report.get("observations")
    require(isinstance(observations, list), "worker observations are missing")
    require(
        report.get("checks") == 479 and len(observations) == 479,
        "worker observations do not cover all 479 frozen cases",
    )
    expected_ids = [case["id"] for case in frozen.build_cases()]
    require(
        [row.get("id") for row in observations] == expected_ids,
        "worker changed a frozen observation identity or ordering",
    )
    for row in observations:
        require(
            row.get("sha256") == frozen.value_digest(row.get("observation")),
            f"worker observation digest changed: {row.get('id')}",
        )
    require(
        report.get("observation_sha256") == frozen.value_digest(observations),
        "worker full-observation digest changed",
    )
    expected_families = dict(
        sorted(collections.Counter(case["family"] for case in frozen.build_cases()).items())
    )
    require(report.get("family_counts") == expected_families, "frozen case families changed")
    require(report.get("holdout") == "NOT ACCESSED", "worker accessed a holdout")
    require(report.get("performance") == "NOT MEASURED", "worker measured performance")


def classify_resolved_iterators(expected: dict, actual: dict) -> dict:
    standard = expected.get("rejected_iterator_controls")
    corrected = actual.get("rejected_iterator_controls")
    require(isinstance(standard, list), "standard iterator controls are missing")
    require(isinstance(corrected, list), "corrected iterator controls are missing")
    require(len(standard) == 2 and len(corrected) == 2, "iterator-control denominator changed")
    require(
        tuple(row.get("id") for row in standard) == ITERATOR_IDS
        and tuple(row.get("id") for row in corrected) == ITERATOR_IDS,
        "corrected iterator-control identities changed",
    )
    rows = []
    for left, right in zip(standard, corrected, strict=True):
        require(
            left.get("correct_public_observation")
            == right.get("correct_public_observation"),
            f"corrected iterator has a genuine public mismatch: {left['id']}",
        )
        require(
            left.get("legacy_private_type_observation")
            == right.get("legacy_private_type_observation"),
            f"corrected scanner does not return the CPython-equivalent iterator: {left['id']}",
        )
        require(
            left.get("diagnostic_private_iterator_type") == "callable_iterator"
            and right.get("diagnostic_private_iterator_type") == "callable_iterator",
            f"corrected scanner does not return a genuine callable_iterator: {left['id']}",
        )
        rows.append(
            {
                "id": left["id"],
                "classification": (
                    "RESOLVED: genuine CPython callable_iterator; historical "
                    "private-type false positive preserved separately"
                ),
                "standard_private_type": left["diagnostic_private_iterator_type"],
                "candidate_private_type": right["diagnostic_private_iterator_type"],
                "standard_legacy_observation": left["legacy_private_type_observation"],
                "candidate_legacy_observation": right["legacy_private_type_observation"],
                "standard_public_observation": left["correct_public_observation"],
                "candidate_public_observation": right["correct_public_observation"],
            }
        )
    return {
        "checks": len(rows),
        "resolved_private_false_positives": len(rows),
        "genuine_public_mismatches": 0,
        "observations": rows,
        "observation_sha256": frozen.value_digest(rows),
    }


def validate_live_reports(
    standard_a: dict,
    standard_b: dict,
    candidate: dict,
    edge: dict,
) -> dict:
    validate_worker(standard_a, "stdlib-a")
    validate_worker(standard_b, "stdlib-b")
    validate_worker(candidate, "candidate")

    self_failures = frozen.mismatch_records(
        standard_a["observations"], standard_b["observations"]
    )
    require(not self_failures, "the independent standard-library controls disagree")
    failures = frozen.mismatch_records(
        standard_a["observations"], candidate["observations"]
    )
    require(not failures, f"corrected public observation mismatch: {failures[:3]}")
    require(
        candidate.get("observation_sha256") == standard_a.get("observation_sha256"),
        "corrected candidate full-observation hash differs from CPython",
    )

    private_observations = candidate.get("private_binder_observations")
    private_failures = candidate.get("private_binder_failures")
    require(isinstance(private_observations, list), "private binder observations are missing")
    require(
        candidate.get("private_binder_checks") == 34
        and len(private_observations) == 34,
        "private native binder denominator changed",
    )
    require(private_failures == [], "a private native binder failure was hidden")
    require(
        all(row.get("passed") is True for row in private_observations),
        "a private native binder control failed",
    )

    guards = candidate.get("forbidden_regex_guard_observations")
    require(isinstance(guards, list), "native regex poison controls are missing")
    require(
        candidate.get("forbidden_regex_guards") == 13 and len(guards) == 13,
        "the forbidden regex entry-point denominator changed",
    )
    require(
        len({row.get("id") for row in guards}) == 13,
        "a forbidden regex entry-point control was duplicated",
    )
    require(
        all(row.get("passed") is True for row in guards),
        "the candidate delegated to an unpoisoned regex entry point",
    )

    require(candidate.get("edge_oracle") == edge, "candidate edge authorization changed")
    artifacts = candidate.get("native_artifacts")
    expected_artifacts = edge.get("artifacts")
    require(isinstance(artifacts, list), "candidate native artifacts are missing")
    require(len(artifacts) == 5, "candidate must identify five native artifacts")
    require(artifacts == expected_artifacts, "candidate artifacts differ from edge evidence")
    require(
        {row.get("role") for row in artifacts} == set(frozen.PRODUCTION_ARTIFACTS),
        "candidate omitted or duplicated a canonical native artifact",
    )
    for item in artifacts:
        role = item["role"]
        canonical_path = frozen.PRODUCTION_ARTIFACTS[role][0].resolve()
        require(
            item.get("path") == canonical_path.relative_to(frozen.ROOT).as_posix(),
            f"candidate artifact path changed: {role}",
        )
        require(
            frozen.path_digest(canonical_path) == item.get("sha256"),
            f"candidate artifact is stale or poisoned: {role}",
        )

    private = frozen.private_binder_report(candidate)
    require(
        private.get("status") == "PASS" and private.get("checks") == 34,
        "frozen native binder controls did not independently pass",
    )
    iterator_controls = classify_resolved_iterators(standard_a, candidate)
    return {
        "self_oracle_failures": self_failures,
        "candidate_failures": failures,
        "private_binder_report": private,
        "resolved_iterator_controls": iterator_controls,
    }


def expect_rejection(label: str, action) -> dict:
    try:
        action()
    except (AssertionError, KeyError, TypeError, ValueError) as error:
        return {"id": label, "passed": True, "rejection": str(error)}
    raise AssertionError(f"a deliberately poisoned scanner observation was accepted: {label}")


def collect_negative_controls(
    standard_a: dict,
    standard_b: dict,
    candidate: dict,
    edge: dict,
) -> list[dict]:
    def poisoned_candidate(label, mutation):
        modified = clone(candidate)
        mutation(modified)
        return expect_rejection(
            label,
            lambda: validate_live_reports(standard_a, standard_b, modified, edge),
        )

    def poison_observation(report):
        row = report["observations"][0]
        row["observation"] = {"poisoned": True}
        row["sha256"] = frozen.value_digest(row["observation"])
        report["observation_sha256"] = frozen.value_digest(report["observations"])

    def missing_observation(report):
        report["observations"].pop()

    def stale_observation_digest(report):
        report["observation_sha256"] = "0" * 64

    def stale_fixture(report):
        report["fixture_sha256"] = "0" * 64

    def poison_private(report):
        report["private_binder_observations"][0]["passed"] = False

    def hide_private_failure(report):
        report["private_binder_failures"] = [{"id": "poisoned-native-binder"}]

    def poison_guard(report):
        report["forbidden_regex_guard_observations"][0]["passed"] = False

    def missing_guard(report):
        report["forbidden_regex_guard_observations"].pop()

    def missing_artifact(report):
        report["native_artifacts"].pop()

    def duplicate_artifact(report):
        report["native_artifacts"][1] = clone(report["native_artifacts"][0])

    def stale_artifact(report):
        report["native_artifacts"][0]["sha256"] = "0" * 64

    def swapped_artifact(report):
        first, second = report["native_artifacts"][:2]
        first["path"], second["path"] = second["path"], first["path"]

    def poison_public_iterator(report):
        report["rejected_iterator_controls"][0][
            "correct_public_observation"
        ] = {"poisoned": True}

    def fake_private_iterator(report):
        report["rejected_iterator_controls"][0][
            "diagnostic_private_iterator_type"
        ] = "_RustMatchIterator"

    mutations = (
        ("poisoned-public-observation", poison_observation),
        ("missing-frozen-observation", missing_observation),
        ("stale-observation-digest", stale_observation_digest),
        ("changed-frozen-fixture", stale_fixture),
        ("poisoned-private-native-binder", poison_private),
        ("hidden-private-native-failure", hide_private_failure),
        ("unpoisoned-regex-delegation-guard", poison_guard),
        ("missing-regex-delegation-guard", missing_guard),
        ("missing-native-artifact", missing_artifact),
        ("duplicated-native-artifact", duplicate_artifact),
        ("stale-native-artifact", stale_artifact),
        ("swapped-native-artifact-path", swapped_artifact),
        ("poisoned-public-iterator", poison_public_iterator),
        ("forged-cpython-iterator-type", fake_private_iterator),
    )
    controls = [poisoned_candidate(label, mutate) for label, mutate in mutations]

    modified_standard = clone(standard_b)
    poison_observation(modified_standard)
    controls.append(
        expect_rejection(
            "poisoned-independent-standard-library-reference",
            lambda: validate_live_reports(
                standard_a, modified_standard, candidate, edge
            ),
        )
    )

    changed_edge = clone(edge)
    changed_edge["artifacts"][0]["sha256"] = "0" * 64
    controls.append(
        expect_rejection(
            "poisoned-independent-edge-provenance",
            lambda: validate_live_reports(
                standard_a, standard_b, candidate, changed_edge
            ),
        )
    )
    require(len(controls) == 16, "scanner negative-control denominator changed")
    require(all(row["passed"] for row in controls), "scanner negative control failed")
    return controls


def make_report(edge_path: Path) -> dict:
    history = check_frozen_history()
    edge = validated_scanner_edge(edge_path)
    standard_a = frozen.run_worker("stdlib-a")
    standard_b = frozen.run_worker("stdlib-b")
    candidate = frozen.run_worker("candidate", edge_oracle=SCANNER_EDGE)
    validated = validate_live_reports(standard_a, standard_b, candidate, edge)
    controls = collect_negative_controls(standard_a, standard_b, candidate, edge)
    return {
        "schema": SCHEMA,
        "role": "scanner-lifetime-observability",
        "status": "PASS",
        "python": "3.14.6",
        "seed": frozen.SEED,
        "goal_sha256": GOAL_SHA256,
        "fixture_sha256": frozen.FROZEN_FIXTURE_SHA256,
        "checks": 479,
        "self_oracle_checks": 479,
        "self_oracle_failures": validated["self_oracle_failures"],
        "candidate_checks": 479,
        "candidate_failures": validated["candidate_failures"],
        "private_binder_checks": 34,
        "private_binder_failures": [],
        "forbidden_regex_guards": 13,
        "negative_controls": controls,
        "negative_control_failures": 0,
        "immutable_frozen_baseline": history,
        "edge_oracle": edge,
        "standard_library_a": standard_a,
        "standard_library_b": standard_b,
        "candidate": candidate,
        "private_binder_report": validated["private_binder_report"],
        "resolved_iterator_controls": validated["resolved_iterator_controls"],
        "native_artifacts": candidate["native_artifacts"],
        "expected_observation_sha256": standard_a["observation_sha256"],
        "actual_observation_sha256": candidate["observation_sha256"],
        "script": current_source(),
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def validate_report(report: dict, edge_path: Path) -> None:
    require(isinstance(report, dict), "scanner observability evidence is not an object")
    require(report.get("schema") == SCHEMA, "scanner observability schema changed")
    require(
        report.get("role") == "scanner-lifetime-observability",
        "scanner observability evidence role changed",
    )
    require(report.get("status") == "PASS", "scanner observability evidence failed")
    require(report.get("python") == "3.14.6", "scanner Python baseline changed")
    require(report.get("seed") == frozen.SEED, "scanner observability seed changed")
    require(report.get("goal_sha256") == GOAL_SHA256, "scanner objective hash changed")
    require(
        report.get("fixture_sha256") == frozen.FROZEN_FIXTURE_SHA256,
        "scanner observability fixture hash changed",
    )
    require(
        report.get("checks") == 479
        and report.get("self_oracle_checks") == 479
        and report.get("candidate_checks") == 479,
        "scanner observability denominator changed",
    )
    require(
        report.get("self_oracle_failures") == []
        and report.get("candidate_failures") == [],
        "scanner observability evidence hides failures",
    )
    require(report.get("private_binder_checks") == 34, "private binder count changed")
    require(report.get("private_binder_failures") == [], "private binder failures hidden")
    require(report.get("forbidden_regex_guards") == 13, "regex guard count changed")
    require(
        report.get("performance") == "NOT MEASURED"
        and report.get("holdout") == "NOT ACCESSED",
        "scanner observability accessed a holdout or benchmark",
    )
    require(report.get("script") == current_source(), "variant self-reference changed")

    history = check_frozen_history()
    require(
        report.get("immutable_frozen_baseline") == history,
        "the preserved immutable baseline is inconsistent",
    )
    edge = validated_scanner_edge(edge_path)
    require(report.get("edge_oracle") == edge, "scanner edge evidence changed")
    standard_a = report.get("standard_library_a")
    standard_b = report.get("standard_library_b")
    candidate = report.get("candidate")
    validated = validate_live_reports(standard_a, standard_b, candidate, edge)
    require(
        report.get("private_binder_report") == validated["private_binder_report"],
        "private native binder archive differs from its observations",
    )
    require(
        report.get("resolved_iterator_controls")
        == validated["resolved_iterator_controls"],
        "resolved iterator evidence changed",
    )
    require(
        report.get("native_artifacts") == candidate["native_artifacts"],
        "native artifact evidence differs from the production worker",
    )
    require(
        report.get("expected_observation_sha256")
        == standard_a["observation_sha256"]
        and report.get("actual_observation_sha256")
        == candidate["observation_sha256"],
        "scanner full observation digest changed",
    )
    controls = report.get("negative_controls")
    require(isinstance(controls, list) and len(controls) == 16, "negative controls changed")
    require(
        report.get("negative_control_failures") == 0
        and all(row.get("passed") is True for row in controls)
        and len({row.get("id") for row in controls}) == 16,
        "a poisoned scanner evidence control failed",
    )


def compressed_report(report: dict) -> bytes:
    data = io.BytesIO()
    with gzip.GzipFile(
        filename="", fileobj=data, mode="wb", compresslevel=9, mtime=0
    ) as output:
        output.write(frozen.canonical(report))
    return data.getvalue()


def read_variant(path: Path) -> dict:
    requested = Path(path)
    require(not requested.is_symlink(), "variant evidence must not be a symlink")
    require(
        requested.resolve() == VARIANT_ARCHIVE.resolve(),
        "only the uniquely named scanner evidence archive is authorized",
    )
    raw = requested.read_bytes()
    require(len(raw) >= 10 and raw[:2] == b"\x1f\x8b", "variant evidence is not gzip")
    require(
        not raw[3] & 0x08 and raw[4:8] == b"\x00\x00\x00\x00",
        "variant evidence is not deterministically compressed",
    )
    try:
        payload = gzip.decompress(raw)
        report = json.loads(payload)
    except (OSError, EOFError, ValueError, json.JSONDecodeError) as error:
        raise AssertionError("scanner observability archive is unreadable") from error
    require(frozen.canonical(report) == payload, "variant evidence is not canonical JSON")
    require(compressed_report(report) == raw, "variant gzip does not reproduce exactly")
    return report


def write_variant(report: dict, edge_path: Path) -> str:
    validate_report(report, edge_path)
    require(not VARIANT_ARCHIVE.is_symlink(), "variant archive must not be a symlink")
    require(not VARIANT_ARCHIVE.exists(), "variant archive already exists; refusing to overwrite")
    payload = compressed_report(report)
    require(payload == compressed_report(report), "gzip generation is nondeterministic")
    with VARIANT_ARCHIVE.open("xb") as output:
        output.write(payload)
    persisted = read_variant(VARIANT_ARCHIVE)
    require(persisted == report, "scanner observability report did not round-trip")
    validate_report(persisted, edge_path)
    return frozen.path_digest(VARIANT_ARCHIVE)


def write_self_test(path: Path, report: dict) -> None:
    destination = Path(path)
    require(not destination.is_symlink(), "self-test output must not be a symlink")
    resolved = destination.resolve()
    require(resolved.is_relative_to(Path("/tmp").resolve()), "self-test output must remain in /tmp")
    require(not resolved.exists(), "self-test output already exists; refusing to overwrite")
    with resolved.open("x", encoding="ascii") as output:
        output.write(frozen.canonical(report).decode("ascii"))
        output.write("\n")
    require(
        json.loads(resolved.read_text(encoding="ascii")) == report,
        "scanner self-test output did not round-trip",
    )


def announce(report: dict, *, archive_sha256: str | None = None) -> None:
    summary = {
        "schema": SCHEMA,
        "phase": report.get("phase", "candidate"),
        "status": report["status"],
        "checks": report["checks"],
        "self_oracle_failures": len(report["self_oracle_failures"]),
        "candidate_failures": len(report["candidate_failures"]),
        "private_binder_checks": report["private_binder_checks"],
        "private_binder_failures": len(report["private_binder_failures"]),
        "forbidden_regex_guards": report["forbidden_regex_guards"],
        "resolved_iterator_controls": report["resolved_iterator_controls"]["checks"],
        "negative_controls": len(report["negative_controls"]),
        "historical_evidence_poison_controls": len(
            report["immutable_frozen_baseline"]["frozen_artifact_poison_controls"]
        ),
        "native_artifacts": len(report["native_artifacts"]),
        "edge_checks": report["edge_oracle"]["checks"],
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    if archive_sha256 is not None:
        summary.update(
            {
                "archive": VARIANT_ARCHIVE.relative_to(frozen.ROOT).as_posix(),
                "archive_sha256": archive_sha256,
            }
        )
    print(json.dumps(summary, ensure_ascii=True, sort_keys=True), flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    self_test = subparsers.add_parser("self-test", help="prove historical and poisoned controls")
    self_test.add_argument("--edge-oracle", type=Path, required=True)
    self_test.add_argument("--output", type=Path)
    candidate = subparsers.add_parser("candidate", help="verify and archive the actual scanner build")
    candidate.add_argument("--edge-oracle", type=Path, required=True)
    verify = subparsers.add_parser("verify", help="verify the unique scanner evidence archive")
    verify.add_argument("--edge-oracle", type=Path, required=True)
    args = parser.parse_args()

    if args.command == "self-test":
        report = make_report(args.edge_oracle)
        validate_report(report, args.edge_oracle)
        report["phase"] = "self-test"
        validate_report(report, args.edge_oracle)

        poisoned_source = clone(report)
        poisoned_source["script"]["sha256"] = "0" * 64
        source_control = expect_rejection(
            "poisoned-variant-self-reference",
            lambda: validate_report(poisoned_source, args.edge_oracle),
        )
        poisoned_history = clone(report)
        poisoned_history["immutable_frozen_baseline"]["manifest"]["sha256"] = "0" * 64
        history_control = expect_rejection(
            "poisoned-historical-baseline-reference",
            lambda: validate_report(poisoned_history, args.edge_oracle),
        )
        require(source_control["passed"] and history_control["passed"], "self-reference control failed")
        report["self_reference_controls"] = [source_control, history_control]
        require(
            compressed_report(report) == compressed_report(report),
            "scanner self-reference gzip is not deterministic",
        )
        if args.output is not None:
            write_self_test(args.output, report)
        announce(report)
        return 0

    if args.command == "candidate":
        report = make_report(args.edge_oracle)
        fingerprint = write_variant(report, args.edge_oracle)
        announce(report, archive_sha256=fingerprint)
        return 0

    report = read_variant(VARIANT_ARCHIVE)
    validate_report(report, args.edge_oracle)
    announce(report, archive_sha256=frozen.path_digest(VARIANT_ARCHIVE))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
