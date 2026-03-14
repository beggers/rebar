from __future__ import annotations

import unittest

from tests.conformance.correctness_expectations import (
    branch_local_backreference_scorecard_case,
    branch_local_backreference_scorecard_target_manifest_ids,
    combined_correctness_case,
    combined_target_manifest_ids,
    conditional_alternation_scorecard_case,
    conditional_alternation_scorecard_target_manifest_ids,
    conditional_nested_quantified_scorecard_case,
    conditional_nested_quantified_scorecard_target_manifest_ids,
    conditional_replacement_scorecard_case,
    conditional_replacement_scorecard_target_manifest_ids,
    open_ended_quantified_group_scorecard_case,
    open_ended_quantified_group_scorecard_target_manifest_ids,
    quantified_alternation_scorecard_case,
    quantified_alternation_scorecard_target_manifest_ids,
    wider_ranged_repeat_quantified_group_scorecard_case,
    wider_ranged_repeat_quantified_group_scorecard_target_manifest_ids,
)
from tests.conformance.scorecard_suite_support import assert_correctness_scorecard_suite


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


if __name__ == "__main__":
    unittest.main()
