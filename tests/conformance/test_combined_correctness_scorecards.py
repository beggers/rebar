from __future__ import annotations

import unittest

from tests.conformance.correctness_expectations import (
    combined_correctness_case,
    combined_target_manifest_ids,
)
from tests.conformance.scorecard_suite_support import assert_correctness_scorecard_suite


class CombinedCorrectnessScorecardSuiteTest(unittest.TestCase):
    maxDiff = None

    def test_runner_regenerates_combined_correctness_scorecards(self) -> None:
        assert_correctness_scorecard_suite(
            self,
            target_manifest_ids=combined_target_manifest_ids(),
            case_factory=combined_correctness_case,
        )


if __name__ == "__main__":
    unittest.main()
