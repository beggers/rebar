from __future__ import annotations

import unittest

from tests.conformance.correctness_expectations import (
    wider_ranged_repeat_quantified_group_scorecard_case,
    wider_ranged_repeat_quantified_group_scorecard_target_manifest_ids,
)
from tests.conformance.scorecard_suite_support import assert_correctness_scorecard_suite


class WiderRangedRepeatQuantifiedGroupScorecardSuiteTest(unittest.TestCase):
    maxDiff = None

    def test_runner_regenerates_wider_ranged_repeat_quantified_group_scorecards(self) -> None:
        assert_correctness_scorecard_suite(
            self,
            target_manifest_ids=(
                wider_ranged_repeat_quantified_group_scorecard_target_manifest_ids()
            ),
            case_factory=wider_ranged_repeat_quantified_group_scorecard_case,
        )


if __name__ == "__main__":
    unittest.main()
