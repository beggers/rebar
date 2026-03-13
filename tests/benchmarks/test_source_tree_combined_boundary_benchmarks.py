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

from tests.benchmarks.benchmark_expectations import (
    representative_measured_workload_ids,
    source_tree_combined_case,
    source_tree_combined_target_manifest_ids,
)
from tests.report_assertions import (
    assert_benchmark_manifest_contract,
    assert_benchmark_workload_contract,
    assert_source_tree_benchmark_contract,
    find_manifest_record,
    find_workload_document,
    find_workload_record,
)


class SourceTreeCombinedBoundaryBenchmarkSuiteTest(unittest.TestCase):
    maxDiff = None

    def test_runner_regenerates_combined_source_tree_boundary_scorecards(self) -> None:
        for target_manifest_id in source_tree_combined_target_manifest_ids():
            with self.subTest(manifest_id=target_manifest_id):
                case = source_tree_combined_case(target_manifest_id)
                manifest_expectation = case["manifest_expectation"]

                with tempfile.TemporaryDirectory() as temp_dir:
                    report_path = pathlib.Path(temp_dir) / "benchmarks.json"
                    command = [sys.executable, "-m", "rebar_harness.benchmarks"]
                    for manifest_path in case["manifest_paths"]:
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
                    expected_phase=case["expected_phase"],
                    expected_runner_version=case["expected_runner_version"],
                    expected_manifest_paths=case["expected_manifest_paths"],
                    tracked_report_path=TRACKED_REPORT_PATH,
                )
                self.assertEqual(summary, case["expected_summary"])
                self.assertEqual(
                    scorecard["summary"]["workloads_by_cache_mode"],
                    case["expected_cache_counts"],
                )

                manifest_id = case["manifest_id"]
                manifest_summary = scorecard["manifests"][manifest_id]
                manifest_record = find_manifest_record(scorecard, manifest_id)
                assert_benchmark_manifest_contract(
                    self,
                    manifest_summary,
                    manifest_record,
                    manifest_document=case["target_manifest"],
                    manifest_path=case["manifest_path"],
                    known_gap_count=manifest_expectation["known_gap_count"],
                )

                representative_ids = representative_measured_workload_ids(
                    scorecard,
                    case["target_manifest"],
                    extra_workload_ids=manifest_expectation["representative_measured_workload_ids"],
                )
                representative_gap_ids = set(
                    manifest_expectation["representative_known_gap_workload_ids"]
                )
                representative_ids.extend(manifest_expectation["representative_known_gap_workload_ids"])

                seen_ids: set[str] = set()
                for workload_id in representative_ids:
                    if workload_id in seen_ids:
                        continue
                    seen_ids.add(workload_id)
                    expected_status = (
                        "unimplemented"
                        if workload_id in representative_gap_ids
                        else "measured"
                    )
                    assert_benchmark_workload_contract(
                        self,
                        find_workload_record(scorecard, workload_id),
                        manifest_id=manifest_id,
                        workload_document=find_workload_document(case["target_manifest"], workload_id),
                        expected_status=expected_status,
                    )


if __name__ == "__main__":
    unittest.main()
