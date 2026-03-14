from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.json"
if str(PYTHON_SOURCE) not in sys.path:
    sys.path.append(str(PYTHON_SOURCE))

from rebar_harness.correctness import CpythonReAdapter, RebarAdapter, evaluate_case
from tests.conformance.correctness_expectations import (
    open_ended_quantified_group_scorecard_case,
    open_ended_quantified_group_scorecard_target_manifest_ids,
)
from tests.report_assertions import (
    assert_correctness_case_record_matches,
    assert_correctness_fixture_contract,
    assert_correctness_layer_contract,
    assert_correctness_report_contract,
    assert_correctness_suite_case_accounting,
    assert_correctness_suite_contract,
    assert_correctness_suite_summary_consistent,
    find_correctness_case_record,
)


class OpenEndedQuantifiedGroupScorecardSuiteTest(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            ["cargo", "build", "-p", "rebar-cpython"],
            check=True,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

    def _run_scorecard(
        self,
        fixture_paths: tuple[pathlib.Path, ...],
    ) -> tuple[dict[str, object], dict[str, object]]:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = pathlib.Path(temp_dir) / "correctness.json"
            command = [
                sys.executable,
                "-m",
                "rebar_harness.correctness",
                "--fixtures",
                *(str(path) for path in fixture_paths),
                "--report",
                str(report_path),
            ]
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
        return summary, scorecard

    def test_runner_regenerates_open_ended_quantified_group_scorecards(self) -> None:
        cpython_adapter = CpythonReAdapter()
        rebar_adapter = RebarAdapter()

        for target_manifest_id in open_ended_quantified_group_scorecard_target_manifest_ids():
            with self.subTest(manifest_id=target_manifest_id):
                case = open_ended_quantified_group_scorecard_case(target_manifest_id)
                summary, scorecard = self._run_scorecard(case.fixture_paths)

                assert_correctness_report_contract(
                    self,
                    scorecard,
                    summary,
                    expected_phase=case.expected_phase,
                    tracked_report_path=TRACKED_REPORT_PATH,
                )
                assert_correctness_fixture_contract(
                    self,
                    scorecard,
                    expected_manifest_ids=case.expected_fixture_manifest_ids,
                    expected_paths=case.expected_fixture_paths,
                    expected_case_count=case.expected_fixture_case_count,
                )
                assert_correctness_layer_contract(
                    self,
                    scorecard,
                    case.target_layer_id,
                    expected_manifest_ids=case.target_layer_manifest_ids,
                    expected_operations=case.target_layer_operations,
                    expected_text_models=case.target_layer_text_models,
                )
                workflow_suite = assert_correctness_suite_contract(
                    self,
                    scorecard,
                    case.target_suite_id,
                    expected_manifest_ids=(case.target_manifest_id,),
                    expected_families=case.target_suite_families,
                    expected_operations=case.target_suite_operations,
                    expected_text_models=case.target_suite_text_models,
                )
                assert_correctness_suite_case_accounting(
                    self,
                    workflow_suite,
                    expected_case_count=case.target_manifest_case_count,
                )

                for suite_id in case.expected_suite_ids[1:]:
                    assert_correctness_suite_summary_consistent(self, scorecard, suite_id)

                for fixture_case in case.representative_cases:
                    with self.subTest(
                        manifest_id=target_manifest_id,
                        case_id=fixture_case.case_id,
                    ):
                        expected_case = evaluate_case(
                            fixture_case,
                            cpython_adapter,
                            rebar_adapter,
                        )
                        assert_correctness_case_record_matches(
                            self,
                            find_correctness_case_record(scorecard, fixture_case.case_id),
                            expected_case,
                        )


if __name__ == "__main__":
    unittest.main()
