from __future__ import annotations

from collections.abc import Callable, Iterable
from functools import lru_cache, partial
import pathlib
import subprocess
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.py"
NUMBERED_BACKREFERENCE_FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "numbered_backreference_workflows.py"
)
NUMBERED_BACKREFERENCE_SUITE_ID = "match.numbered_backreference"

from rebar_harness.correctness import (
    CpythonReAdapter,
    RebarAdapter,
    SCORECARD_REPORT as CORRECTNESS_SCORECARD_REPORT,
    evaluate_case,
    load_fixture_manifest,
)
from tests.conformance.correctness_expectations import (
    CorrectnessScorecardExpectation,
    correctness_scorecard_case,
    correctness_scorecard_target_manifest_ids,
    tracked_correctness_scorecard_suites,
)
from tests.harness_cli_test_support import run_harness_scorecard
from tests.report_assertions import (
    assert_correctness_case_record_matches,
    assert_correctness_fixture_contract,
    assert_correctness_layer_contract,
    assert_correctness_report_contract,
    assert_correctness_suite_case_accounting,
    assert_correctness_suite_contract,
    assert_correctness_suites_present,
    find_correctness_case_record,
    find_correctness_suite_record,
)


@lru_cache(maxsize=1)
def _build_rebar_extension() -> None:
    subprocess.run(
        ["cargo", "build", "-p", "rebar-cpython"],
        check=True,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )

def assert_correctness_scorecard_suite(
    testcase: unittest.TestCase,
    *,
    target_manifest_ids: Iterable[str],
    case_factory: Callable[[str], CorrectnessScorecardExpectation],
) -> None:
    target_manifest_ids = tuple(target_manifest_ids)
    _build_rebar_extension()
    cpython_adapter = CpythonReAdapter()
    rebar_adapter = RebarAdapter()

    for target_manifest_id in target_manifest_ids:
        with testcase.subTest(manifest_id=target_manifest_id):
            case = case_factory(target_manifest_id)
            summary, scorecard = run_harness_scorecard(
                "rebar_harness.correctness",
                [
                    "--fixtures",
                    *(str(path) for path in case.fixture_paths),
                ],
                report_name="correctness.json",
            )

            assert_correctness_report_contract(
                testcase,
                scorecard,
                summary,
                expected_phase=case.expected_phase,
                tracked_report_path=TRACKED_REPORT_PATH,
            )
            assert_correctness_fixture_contract(
                testcase,
                scorecard,
                expected_manifest_ids=case.expected_fixture_manifest_ids,
                expected_paths=case.expected_fixture_paths,
                expected_case_count=case.expected_fixture_case_count,
            )
            testcase.assertEqual(
                [suite["id"] for suite in scorecard["suites"]],
                list(case.expected_cumulative_suite_ids),
            )
            testcase.assertEqual(
                tuple(scorecard["layers"]),
                tuple(
                    layer_expectation.layer_id
                    for layer_expectation in case.layer_expectations
                ),
            )
            for layer_expectation in case.layer_expectations:
                assert_correctness_layer_contract(
                    testcase,
                    scorecard,
                    layer_expectation.layer_id,
                    expected_manifest_ids=layer_expectation.expected_manifest_ids,
                    expected_operations=layer_expectation.expected_operations,
                    expected_text_models=layer_expectation.expected_text_models,
                )
            workflow_suite = assert_correctness_suite_contract(
                testcase,
                scorecard,
                case.target_suite_id,
                expected_manifest_ids=(case.target_manifest_id,),
                expected_families=case.target_suite_families,
                expected_operations=case.target_suite_operations,
                expected_text_models=case.target_suite_text_models,
            )
            assert_correctness_suite_case_accounting(
                testcase,
                workflow_suite,
                expected_case_count=case.target_manifest_case_count,
            )
            assert_correctness_suites_present(
                testcase,
                scorecard,
                case.expected_suite_ids[1:],
            )

            for fixture_case in case.representative_cases:
                with testcase.subTest(
                    manifest_id=target_manifest_id,
                    case_id=fixture_case.case_id,
                ):
                    expected_case = evaluate_case(
                        fixture_case,
                        cpython_adapter,
                        rebar_adapter,
                    )
                    assert_correctness_case_record_matches(
                        testcase,
                        find_correctness_case_record(scorecard, fixture_case.case_id),
                        expected_case,
                    )


class CorrectnessScorecardSuitesTest(unittest.TestCase):
    maxDiff = None

    def test_runner_regenerates_correctness_scorecards(self) -> None:
        for suite in tracked_correctness_scorecard_suites():
            with self.subTest(suite_id=suite.suite_id):
                assert_correctness_scorecard_suite(
                    self,
                    target_manifest_ids=correctness_scorecard_target_manifest_ids(
                        suite.suite_id
                    ),
                    case_factory=partial(correctness_scorecard_case, suite.suite_id),
                )

    def test_tracked_report_keeps_numbered_backreference_manifest_fresh(self) -> None:
        _build_rebar_extension()
        manifest_cases = load_fixture_manifest(NUMBERED_BACKREFERENCE_FIXTURE_PATH).cases
        _, expected_scorecard = run_harness_scorecard(
            "rebar_harness.correctness",
            [
                "--fixtures",
                str(NUMBERED_BACKREFERENCE_FIXTURE_PATH),
            ],
            report_name="correctness.json",
        )
        tracked_scorecard = CORRECTNESS_SCORECARD_REPORT.load(TRACKED_REPORT_PATH)

        expected_suite = find_correctness_suite_record(
            expected_scorecard,
            NUMBERED_BACKREFERENCE_SUITE_ID,
        )
        tracked_suite = find_correctness_suite_record(
            tracked_scorecard,
            NUMBERED_BACKREFERENCE_SUITE_ID,
        )

        self.assertEqual(tracked_suite["manifest_ids"], expected_suite["manifest_ids"])
        self.assertEqual(tracked_suite["families"], expected_suite["families"])
        self.assertEqual(tracked_suite["operations"], expected_suite["operations"])
        self.assertEqual(tracked_suite["text_models"], expected_suite["text_models"])
        self.assertEqual(tracked_suite["case_count"], expected_suite["case_count"])
        self.assertEqual(tracked_suite["summary"], expected_suite["summary"])
        self.assertEqual(tracked_suite["diagnostics"], expected_suite["diagnostics"])

        for fixture_case in manifest_cases:
            with self.subTest(case_id=fixture_case.case_id):
                assert_correctness_case_record_matches(
                    self,
                    find_correctness_case_record(tracked_scorecard, fixture_case.case_id),
                    find_correctness_case_record(expected_scorecard, fixture_case.case_id),
                )


if __name__ == "__main__":
    unittest.main()
