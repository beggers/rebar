from __future__ import annotations

from collections.abc import Callable, Iterable
import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.py"
if str(PYTHON_SOURCE) not in sys.path:
    sys.path.append(str(PYTHON_SOURCE))

from rebar_harness.correctness import (
    CpythonReAdapter,
    RebarAdapter,
    evaluate_case,
)
from tests.conformance.correctness_expectations import (
    CorrectnessScorecardExpectation,
    branch_local_backreference_scorecard_case,
    branch_local_backreference_scorecard_target_manifest_ids,
    build_rebar_extension,
    combined_correctness_case,
    combined_target_manifest_ids,
    conditional_alternation_scorecard_case,
    conditional_alternation_scorecard_target_manifest_ids,
    conditional_nested_quantified_scorecard_case,
    conditional_nested_quantified_scorecard_target_manifest_ids,
    conditional_replacement_scorecard_case,
    conditional_replacement_scorecard_target_manifest_ids,
    nested_broader_range_wider_ranged_repeat_quantified_group_alternation_scorecard_case,
    nested_broader_range_wider_ranged_repeat_quantified_group_alternation_scorecard_target_manifest_ids,
    open_ended_quantified_group_scorecard_case,
    open_ended_quantified_group_scorecard_target_manifest_ids,
    quantified_alternation_scorecard_case,
    quantified_alternation_scorecard_target_manifest_ids,
    run_correctness_scorecard,
    wider_ranged_repeat_quantified_group_scorecard_case,
    wider_ranged_repeat_quantified_group_scorecard_target_manifest_ids,
)
from tests.report_assertions import (
    assert_correctness_case_record_matches,
    assert_correctness_fixture_contract,
    assert_correctness_layer_contract,
    assert_correctness_report_contract,
    assert_correctness_suite_case_accounting,
    assert_correctness_suite_contract,
    assert_correctness_suites_present,
    find_correctness_case_record,
)


def assert_correctness_scorecard_suite(
    testcase: unittest.TestCase,
    *,
    target_manifest_ids: Iterable[str],
    case_factory: Callable[[str], CorrectnessScorecardExpectation],
) -> None:
    target_manifest_ids = tuple(target_manifest_ids)
    build_rebar_extension()
    cpython_adapter = CpythonReAdapter()
    rebar_adapter = RebarAdapter()

    for target_manifest_id in target_manifest_ids:
        with testcase.subTest(manifest_id=target_manifest_id):
            case = case_factory(target_manifest_id)
            summary, scorecard = run_correctness_scorecard(case.fixture_paths)

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

    def test_runner_regenerates_combined_correctness_scorecards(self) -> None:
        assert_correctness_scorecard_suite(
            self,
            target_manifest_ids=combined_target_manifest_ids(),
            case_factory=combined_correctness_case,
        )

    def test_runner_regenerates_branch_local_backreference_correctness_scorecards(
        self,
    ) -> None:
        assert_correctness_scorecard_suite(
            self,
            target_manifest_ids=(
                branch_local_backreference_scorecard_target_manifest_ids()
            ),
            case_factory=branch_local_backreference_scorecard_case,
        )

    def test_runner_regenerates_conditional_replacement_correctness_scorecards(
        self,
    ) -> None:
        assert_correctness_scorecard_suite(
            self,
            target_manifest_ids=conditional_replacement_scorecard_target_manifest_ids(),
            case_factory=conditional_replacement_scorecard_case,
        )

    def test_runner_regenerates_conditional_alternation_correctness_scorecards(
        self,
    ) -> None:
        assert_correctness_scorecard_suite(
            self,
            target_manifest_ids=conditional_alternation_scorecard_target_manifest_ids(),
            case_factory=conditional_alternation_scorecard_case,
        )

    def test_runner_regenerates_conditional_nested_quantified_correctness_scorecards(
        self,
    ) -> None:
        assert_correctness_scorecard_suite(
            self,
            target_manifest_ids=(
                conditional_nested_quantified_scorecard_target_manifest_ids()
            ),
            case_factory=conditional_nested_quantified_scorecard_case,
        )

    def test_runner_regenerates_quantified_alternation_correctness_scorecards(
        self,
    ) -> None:
        assert_correctness_scorecard_suite(
            self,
            target_manifest_ids=quantified_alternation_scorecard_target_manifest_ids(),
            case_factory=quantified_alternation_scorecard_case,
        )

    def test_runner_regenerates_open_ended_quantified_group_scorecards(self) -> None:
        assert_correctness_scorecard_suite(
            self,
            target_manifest_ids=open_ended_quantified_group_scorecard_target_manifest_ids(),
            case_factory=open_ended_quantified_group_scorecard_case,
        )

    def test_runner_regenerates_wider_ranged_repeat_quantified_group_scorecards(
        self,
    ) -> None:
        assert_correctness_scorecard_suite(
            self,
            target_manifest_ids=(
                wider_ranged_repeat_quantified_group_scorecard_target_manifest_ids()
            ),
            case_factory=wider_ranged_repeat_quantified_group_scorecard_case,
        )

    def test_runner_regenerates_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_scorecards(
        self,
    ) -> None:
        assert_correctness_scorecard_suite(
            self,
            target_manifest_ids=(
                nested_broader_range_wider_ranged_repeat_quantified_group_alternation_scorecard_target_manifest_ids()
            ),
            case_factory=(
                nested_broader_range_wider_ranged_repeat_quantified_group_alternation_scorecard_case
            ),
        )


if __name__ == "__main__":
    unittest.main()
