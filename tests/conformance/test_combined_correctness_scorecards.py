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
    combined_correctness_case,
    combined_target_manifest_ids,
)
from tests.report_assertions import (
    assert_correctness_fixture_contract,
    assert_correctness_layer_contract,
    assert_correctness_report_contract,
    assert_correctness_suite_contract,
    assert_correctness_suite_summary_consistent,
    find_correctness_case_record,
)


class CombinedCorrectnessScorecardSuiteTest(unittest.TestCase):
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

    def assert_case_matches_expected(
        self,
        actual_case: dict[str, object],
        expected_case: dict[str, object],
    ) -> None:
        for key in (
            "id",
            "manifest_id",
            "suite_id",
            "layer",
            "family",
            "operation",
            "notes",
            "categories",
            "comparison",
            "comparison_notes",
            "observations",
        ):
            self.assertEqual(actual_case.get(key), expected_case.get(key))

        for key in ("text_model", "pattern", "flags", "helper", "kwargs"):
            self.assertEqual(actual_case.get(key), expected_case.get(key))

        actual_args = actual_case.get("args")
        expected_args = expected_case.get("args")
        self.assertEqual(bool(actual_args), bool(expected_args))
        if not actual_args or not expected_args:
            return

        self.assertEqual(len(actual_args), len(expected_args))
        for actual_arg, expected_arg in zip(actual_args, expected_args):
            if (
                isinstance(actual_arg, dict)
                and isinstance(expected_arg, dict)
                and actual_arg.get("type") == "callable"
                and expected_arg.get("type") == "callable"
            ):
                self.assertEqual(actual_arg["type"], expected_arg["type"])
                self.assertEqual(actual_arg["qualname"], expected_arg["qualname"])
                continue
            self.assertEqual(actual_arg, expected_arg)

    def test_runner_regenerates_combined_correctness_scorecards(self) -> None:
        for target_manifest_id in combined_target_manifest_ids():
            with self.subTest(manifest_id=target_manifest_id):
                case = combined_correctness_case(target_manifest_id)

                with tempfile.TemporaryDirectory() as temp_dir:
                    report_path = pathlib.Path(temp_dir) / "correctness.json"
                    command = [
                        sys.executable,
                        "-m",
                        "rebar_harness.correctness",
                        "--fixtures",
                        *(str(path) for path in case.fixture_paths),
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
                assert_correctness_suite_contract(
                    self,
                    scorecard,
                    case.target_suite_id,
                    expected_manifest_ids=(case.target_manifest_id,),
                    expected_families=case.target_suite_families,
                    expected_operations=case.target_suite_operations,
                    expected_text_models=case.target_suite_text_models,
                )

                for suite_id in case.expected_suite_ids[1:]:
                    assert_correctness_suite_summary_consistent(self, scorecard, suite_id)

                for fixture_case in case.representative_cases:
                    expected_case = evaluate_case(
                        fixture_case,
                        CpythonReAdapter(),
                        RebarAdapter(),
                    )
                    self.assert_case_matches_expected(
                        find_correctness_case_record(scorecard, fixture_case.case_id),
                        expected_case,
                    )


if __name__ == "__main__":
    unittest.main()
