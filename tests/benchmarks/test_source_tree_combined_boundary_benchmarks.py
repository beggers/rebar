from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "benchmarks" / "latest.json"
if str(PYTHON_SOURCE) not in sys.path:
    sys.path.append(str(PYTHON_SOURCE))

from rebar_harness.benchmarks import DEFAULT_MANIFEST_PATHS
from tests.benchmarks.benchmark_expectations import SOURCE_TREE_BOUNDARY_GAP_EXPECTATIONS
from tests.report_assertions import (
    assert_benchmark_manifest_contract,
    assert_benchmark_workload_contract,
    assert_source_tree_benchmark_contract,
)


BASE_MANIFEST_IDS = frozenset(
    {
        "compile-matrix",
        "module-boundary",
        "pattern-boundary",
        "regression-matrix",
    }
)


def _manifest_id(path: pathlib.Path) -> str:
    return path.stem.replace("_", "-")


def _relative_manifest_path(path: pathlib.Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def _load_manifest(path: pathlib.Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _selected_manifest_paths(target_manifest_id: str) -> list[pathlib.Path]:
    manifest_paths: list[pathlib.Path] = []
    regression_path = next(
        (
            path
            for path in DEFAULT_MANIFEST_PATHS
            if _manifest_id(path) == "regression-matrix"
        ),
        None,
    )
    for path in DEFAULT_MANIFEST_PATHS:
        manifest_id = _manifest_id(path)
        if manifest_id == "regression-matrix":
            continue
        manifest_paths.append(path)
        if manifest_id == target_manifest_id:
            break
    else:
        raise AssertionError(f"target manifest {target_manifest_id!r} is not in DEFAULT_MANIFEST_PATHS")
    if regression_path is None:
        raise AssertionError("DEFAULT_MANIFEST_PATHS is missing regression_matrix.json")
    manifest_paths.append(regression_path)
    return manifest_paths


def _ordered_operations(workloads: list[dict[str, object]]) -> list[str]:
    operations: list[str] = []
    for workload in workloads:
        operation = str(workload["operation"])
        if operation not in operations:
            operations.append(operation)
    return operations


def _expected_summary(manifest_documents: list[dict[str, object]]) -> tuple[dict[str, int], dict[str, int]]:
    workloads = [
        workload
        for manifest in manifest_documents
        for workload in manifest["workloads"]  # type: ignore[index]
    ]
    known_gap_count = sum(
        SOURCE_TREE_BOUNDARY_GAP_EXPECTATIONS[str(manifest["manifest_id"])]["known_gap_count"]
        for manifest in manifest_documents
    )
    summary = {
        "known_gap_count": known_gap_count,
        "measured_workloads": len(workloads) - known_gap_count,
        "module_workloads": sum(1 for workload in workloads if workload["family"] == "module"),
        "parser_workloads": sum(1 for workload in workloads if workload["family"] == "parser"),
        "regression_workloads": sum(
            len(manifest["workloads"])  # type: ignore[arg-type]
            for manifest in manifest_documents
            if manifest["manifest_id"] == "regression-matrix"
        ),
        "total_workloads": len(workloads),
    }
    cache_counts = {
        cache_mode: sum(1 for workload in workloads if workload["cache_mode"] == cache_mode)
        for cache_mode in ("cold", "warm", "purged")
    }
    return summary, cache_counts


def _find_manifest_record(scorecard: dict[str, object], manifest_id: str) -> dict[str, object]:
    for manifest_record in scorecard["artifacts"]["manifests"]:  # type: ignore[index]
        if manifest_record["manifest_id"] == manifest_id:
            return manifest_record
    raise AssertionError(f"missing manifest record for {manifest_id!r}")


def _find_workload_record(scorecard: dict[str, object], workload_id: str) -> dict[str, object]:
    for workload in scorecard["workloads"]:  # type: ignore[index]
        if workload["id"] == workload_id:
            return workload
    raise AssertionError(f"missing workload record for {workload_id!r}")


def _find_workload_document(
    manifest_document: dict[str, object],
    workload_id: str,
) -> dict[str, object]:
    for workload in manifest_document["workloads"]:  # type: ignore[index]
        if workload["id"] == workload_id:
            return workload
    raise AssertionError(
        f"missing workload definition {workload_id!r} in {manifest_document['manifest_id']!r}"
    )


def _representative_measured_workload_ids(
    scorecard: dict[str, object],
    manifest_document: dict[str, object],
) -> list[str]:
    manifest_id = str(manifest_document["manifest_id"])
    smoke_ids = [
        str(workload["id"])
        for workload in manifest_document["workloads"]  # type: ignore[index]
        if workload.get("smoke", False)
    ]
    representative_ids = list(smoke_ids)
    operations = _ordered_operations(manifest_document["workloads"])  # type: ignore[arg-type]
    for operation in operations:
        for workload in scorecard["workloads"]:  # type: ignore[index]
            if workload["manifest_id"] != manifest_id:
                continue
            if workload["operation"] != operation or workload["status"] != "measured":
                continue
            workload_id = str(workload["id"])
            if workload_id not in representative_ids:
                representative_ids.append(workload_id)
            break
    return representative_ids


class SourceTreeCombinedBoundaryBenchmarkSuiteTest(unittest.TestCase):
    maxDiff = None

    def test_runner_regenerates_combined_source_tree_boundary_scorecards(self) -> None:
        for target_manifest_id in (
            _manifest_id(path)
            for path in DEFAULT_MANIFEST_PATHS
            if _manifest_id(path) not in BASE_MANIFEST_IDS
        ):
            with self.subTest(manifest_id=target_manifest_id):
                manifest_paths = _selected_manifest_paths(target_manifest_id)
                manifest_documents = [_load_manifest(path) for path in manifest_paths]
                target_manifest = manifest_documents[-2]
                expected_summary, expected_cache_counts = _expected_summary(manifest_documents)

                with tempfile.TemporaryDirectory() as temp_dir:
                    report_path = pathlib.Path(temp_dir) / "benchmarks.json"
                    command = [sys.executable, "-m", "rebar_harness.benchmarks"]
                    for manifest_path in manifest_paths:
                        command.extend(("--manifest", str(manifest_path)))
                    command.extend(("--report", str(report_path)))
                    result = subprocess.run(
                        command,
                        check=True,
                        cwd=REPO_ROOT,
                        env={"PYTHONPATH": str(PYTHON_SOURCE)},
                        capture_output=True,
                        text=True,
                    )
                    summary = json.loads(result.stdout.strip())
                    scorecard = json.loads(report_path.read_text(encoding="utf-8"))

                assert_source_tree_benchmark_contract(
                    self,
                    scorecard,
                    summary,
                    expected_phase="phase3-regression-stability-suite",
                    expected_runner_version="phase3",
                    expected_manifest_paths=[
                        _relative_manifest_path(path) for path in manifest_paths
                    ],
                )
                self.assertEqual(summary, expected_summary)
                self.assertEqual(
                    scorecard["summary"]["workloads_by_cache_mode"],
                    expected_cache_counts,
                )
                self.assertTrue(TRACKED_REPORT_PATH.is_file())

                manifest_id = str(target_manifest["manifest_id"])
                manifest_summary = scorecard["manifests"][manifest_id]
                manifest_record = _find_manifest_record(scorecard, manifest_id)
                known_gap_count = SOURCE_TREE_BOUNDARY_GAP_EXPECTATIONS[manifest_id]["known_gap_count"]
                assert_benchmark_manifest_contract(
                    self,
                    manifest_summary,
                    manifest_record,
                    manifest_document=target_manifest,
                    manifest_path=_relative_manifest_path(manifest_paths[-2]),
                    known_gap_count=known_gap_count,
                )

                representative_ids = _representative_measured_workload_ids(scorecard, target_manifest)
                representative_gap_workload_id = SOURCE_TREE_BOUNDARY_GAP_EXPECTATIONS[manifest_id][
                    "representative_known_gap_workload_id"
                ]
                if representative_gap_workload_id is not None:
                    representative_ids.append(representative_gap_workload_id)

                seen_ids: set[str] = set()
                for workload_id in representative_ids:
                    if workload_id in seen_ids:
                        continue
                    seen_ids.add(workload_id)
                    expected_status = (
                        "unimplemented"
                        if workload_id == representative_gap_workload_id
                        else "measured"
                    )
                    assert_benchmark_workload_contract(
                        self,
                        _find_workload_record(scorecard, workload_id),
                        manifest_id=manifest_id,
                        workload_document=_find_workload_document(target_manifest, workload_id),
                        expected_status=expected_status,
                    )


if __name__ == "__main__":
    unittest.main()
