from __future__ import annotations

import unittest

from tests.conformance.correctness_expectations import combined_correctness_case
from tests.conformance.scorecard_suite_support import assert_correctness_scorecard_suite


TARGET_MANIFEST_ID = "quantified-nested-group-callable-replacement-workflows"


class CorrectnessHarnessQuantifiedNestedGroupCallableReplacementWorkflowTest(
    unittest.TestCase
):
    maxDiff = None

    def test_runner_regenerates_combined_quantified_nested_group_callable_replacement_scorecard(
        self,
    ) -> None:
        assert_correctness_scorecard_suite(
            self,
            target_manifest_ids=(TARGET_MANIFEST_ID,),
            case_factory=combined_correctness_case,
        )


if __name__ == "__main__":
    unittest.main()
