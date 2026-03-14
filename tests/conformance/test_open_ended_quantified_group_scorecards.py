from __future__ import annotations

import unittest

from tests.conformance.correctness_expectations import (
    open_ended_quantified_group_scorecard_case,
    open_ended_quantified_group_scorecard_target_manifest_ids,
)
from tests.conformance.scorecard_suite_support import assert_correctness_scorecard_suite


class OpenEndedQuantifiedGroupScorecardSuiteTest(unittest.TestCase):
    maxDiff = None

    def test_runner_regenerates_open_ended_quantified_group_scorecards(self) -> None:
        assert_correctness_scorecard_suite(
            self,
            target_manifest_ids=open_ended_quantified_group_scorecard_target_manifest_ids(),
            case_factory=open_ended_quantified_group_scorecard_case,
        )


if __name__ == "__main__":
    unittest.main()
