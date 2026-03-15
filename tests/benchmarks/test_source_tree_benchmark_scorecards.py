from __future__ import annotations

import pathlib
import sys
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "benchmarks" / "latest.py"
if str(PYTHON_SOURCE) not in sys.path:
    sys.path.append(str(PYTHON_SOURCE))

from tests.benchmarks.benchmark_expectations import (
    run_source_tree_benchmark_scorecard,
    source_tree_scorecard_case,
    source_tree_scorecard_case_ids,
)
from tests.report_assertions import (
    assert_benchmark_manifest_contract,
    assert_benchmark_workload_contract,
    assert_source_tree_benchmark_contract,
    find_manifest_record,
    find_workload_document,
    find_workload_record,
)


class SourceTreeBenchmarkScorecardTest(unittest.TestCase):
    maxDiff = None

    def test_runner_regenerates_source_tree_scorecards(self) -> None:
        for case_id in source_tree_scorecard_case_ids():
            with self.subTest(case_id=case_id):
                case = source_tree_scorecard_case(case_id)
                summary, scorecard = run_source_tree_benchmark_scorecard(
                    case["manifest_paths"],
                    smoke=case["selection_mode"] == "smoke",
                )

                assert_source_tree_benchmark_contract(
                    self,
                    scorecard,
                    summary,
                    expected_phase=case["expected_phase"],
                    expected_runner_version=case["expected_runner_version"],
                    expected_adapter=case["expected_adapter"],
                    expected_manifest_documents=case["manifest_documents"],
                    expected_manifest_paths=case["expected_manifest_paths"],
                    expected_selection_mode=case["selection_mode"],
                    tracked_report_path=TRACKED_REPORT_PATH,
                )
                self.assertEqual(summary, case["expected_summary"])

                expected_first_deferred = case.get("expected_first_deferred")
                if expected_first_deferred is not None:
                    self.assertGreaterEqual(len(scorecard["deferred"]), 1)
                    self.assertEqual(
                        scorecard["deferred"][0]["area"],
                        expected_first_deferred["area"],
                    )
                    self.assertEqual(
                        scorecard["deferred"][0]["follow_up"],
                        expected_first_deferred["follow_up"],
                    )

                expected_workload_order = case.get("expected_workload_order")
                if expected_workload_order is not None:
                    self.assertEqual(
                        [workload["id"] for workload in scorecard["workloads"]],
                        list(expected_workload_order),
                    )

                self._assert_manifest_contracts(case, scorecard)
                self._assert_representative_workloads(case, scorecard)

    def _assert_manifest_contracts(
        self,
        case: dict[str, object],
        scorecard: dict[str, object],
    ) -> None:
        manifest_expectations = case["manifest_expectations"]
        for manifest_id, manifest_expectation in manifest_expectations.items():
            manifest_summary = scorecard["manifests"][manifest_id]
            manifest_record = find_manifest_record(scorecard, manifest_id)
            assert_benchmark_manifest_contract(
                self,
                manifest_summary,
                manifest_record,
                manifest_document=case["manifest_documents_by_id"][manifest_id],
                manifest_path=case["manifest_paths_by_id"][manifest_id],
                known_gap_count=manifest_expectation["known_gap_count"],
                selection_mode=case["selection_mode"],
                selected_workload_ids=case["selected_workload_ids_by_manifest"][manifest_id],
            )

    def _assert_representative_workloads(
        self,
        case: dict[str, object],
        scorecard: dict[str, object],
    ) -> None:
        note_expectations = case.get("workload_note_substrings", {})
        self._assert_workloads(
            case,
            scorecard,
            case["representative_measured_workload_ids"],
            expected_status="measured",
            note_expectations=note_expectations,
        )
        self._assert_workloads(
            case,
            scorecard,
            case["representative_known_gap_workload_ids"],
            expected_status="unimplemented",
            note_expectations=note_expectations,
        )

    def _assert_workloads(
        self,
        case: dict[str, object],
        scorecard: dict[str, object],
        workload_ids: tuple[str, ...],
        *,
        expected_status: str,
        note_expectations: dict[str, str],
    ) -> None:
        for workload_id in workload_ids:
            with self.subTest(workload_id=workload_id):
                workload_record = find_workload_record(scorecard, workload_id)
                manifest_id = workload_record["manifest_id"]
                manifest_document = case["manifest_documents_by_id"][manifest_id]
                assert_benchmark_workload_contract(
                    self,
                    workload_record,
                    manifest_id=manifest_id,
                    workload_document=find_workload_document(manifest_document, workload_id),
                    expected_status=expected_status,
                )

                note_substring = note_expectations.get(workload_id)
                if note_substring is not None:
                    self.assertTrue(
                        any(note_substring in note for note in workload_record["notes"])
                    )

    def test_nested_group_callable_replacement_scorecard_covers_open_ended_rows(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-callable-replacement-boundary")
        summary, scorecard = run_source_tree_benchmark_scorecard(case["manifest_paths"])

        self.assertEqual(summary, case["expected_summary"])
        self.assertEqual(case["representative_known_gap_workload_ids"], ())

        for workload_id in case["representative_measured_workload_ids"]:
            with self.subTest(workload_id=workload_id):
                workload_record = find_workload_record(scorecard, workload_id)
                manifest_id = workload_record["manifest_id"]
                manifest_document = case["manifest_documents_by_id"][manifest_id]
                assert_benchmark_workload_contract(
                    self,
                    workload_record,
                    manifest_id=manifest_id,
                    workload_document=find_workload_document(
                        manifest_document,
                        workload_id,
                    ),
                    expected_status="measured",
                )

    def test_nested_group_replacement_scorecard_covers_open_ended_rows(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-replacement-boundary")
        summary, scorecard = run_source_tree_benchmark_scorecard(case["manifest_paths"])

        self.assertEqual(summary, case["expected_summary"])
        self.assertEqual(case["representative_known_gap_workload_ids"], ())

        for workload_id in case["representative_measured_workload_ids"]:
            with self.subTest(workload_id=workload_id):
                workload_record = find_workload_record(scorecard, workload_id)
                manifest_id = workload_record["manifest_id"]
                manifest_document = case["manifest_documents_by_id"][manifest_id]
                assert_benchmark_workload_contract(
                    self,
                    workload_record,
                    manifest_id=manifest_id,
                    workload_document=find_workload_document(
                        manifest_document,
                        workload_id,
                    ),
                    expected_status="measured",
                )


if __name__ == "__main__":
    unittest.main()
