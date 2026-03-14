from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

from tests.conformance.scorecard_suite_support import load_published_correctness_scorecard


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.py"
FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py"
)
TARGET_MANIFEST_ID = (
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows"
)
TARGET_SUITE_ID = (
    "match.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy"
)
EXPECTED_CASE_IDS = (
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-str",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-short-branch-str",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-long-branch-str",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-short-then-long-str",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-long-then-short-str",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-fourth-repetition-mixed-str",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-no-match-invalid-tail-str",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-compile-metadata-str",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-module-search-lower-bound-long-branch-str",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-module-search-second-repetition-short-then-long-str",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-module-search-fourth-repetition-mixed-str",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-second-repetition-long-then-short-str",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-no-match-invalid-tail-str",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-no-match-overflow-str",
)
EXPECTED_SUITE_IDS = (
    TARGET_SUITE_ID,
    f"{TARGET_SUITE_ID}.str",
    f"{TARGET_SUITE_ID}.compile",
    f"{TARGET_SUITE_ID}.module_call",
    f"{TARGET_SUITE_ID}.pattern_call",
)

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.append(str(PYTHON_SOURCE))

from rebar_harness.correctness import (
    CpythonReAdapter,
    RebarAdapter,
    evaluate_case,
    load_fixture_manifest,
)
from tests.report_assertions import (
    assert_correctness_case_record_matches,
    assert_correctness_report_contract,
    assert_correctness_suite_case_accounting,
    assert_correctness_suite_contract,
    assert_correctness_suite_summary_consistent,
    find_correctness_case_record,
)


class NestedBroaderRangeWiderRangedRepeatQuantifiedGroupAlternationBacktrackingHeavyWorkflowTest(
    unittest.TestCase
):
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
        cls.fixture_manifest, fixture_cases = load_fixture_manifest(FIXTURE_PATH)
        cls.fixture_cases = tuple(fixture_cases)

    def _run_scorecard(self) -> tuple[dict[str, object], dict[str, object]]:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = pathlib.Path(temp_dir) / "correctness.json"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "rebar_harness.correctness",
                    "--report",
                    str(report_path),
                ],
                check=True,
                cwd=REPO_ROOT,
                env={"PYTHONPATH": str(PYTHON_SOURCE)},
                capture_output=True,
                text=True,
            )
            summary = json.loads(result.stdout.strip())
            scorecard = json.loads(report_path.read_text(encoding="utf-8"))
        return summary, scorecard

    def test_runner_regenerates_combined_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_scorecard(
        self,
    ) -> None:
        summary, scorecard = self._run_scorecard()

        assert_correctness_report_contract(
            self,
            scorecard,
            summary,
            expected_phase="phase3-module-workflow-pack",
            tracked_report_path=TRACKED_REPORT_PATH,
        )
        tracked_scorecard = load_published_correctness_scorecard()
        self.assertEqual(scorecard["summary"], tracked_scorecard["summary"])
        self.assertEqual(
            scorecard["fixtures"]["manifest_count"],
            tracked_scorecard["fixtures"]["manifest_count"],
        )
        self.assertEqual(len(scorecard["cases"]), len(tracked_scorecard["cases"]))
        self.assertIn(TARGET_MANIFEST_ID, scorecard["fixtures"]["manifest_ids"])
        self.assertIn(
            TARGET_MANIFEST_ID,
            scorecard["layers"]["match_behavior"]["manifest_ids"],
        )

        self.assertEqual(self.fixture_manifest.manifest_id, TARGET_MANIFEST_ID)
        self.assertEqual(self.fixture_manifest.suite_id, TARGET_SUITE_ID)
        self.assertEqual(
            {case.case_id for case in self.fixture_cases},
            set(EXPECTED_CASE_IDS),
        )

        suite_ids = [suite["id"] for suite in scorecard["suites"]]
        for suite_id in EXPECTED_SUITE_IDS:
            self.assertIn(suite_id, suite_ids)

        workflow_suite = assert_correctness_suite_contract(
            self,
            scorecard,
            TARGET_SUITE_ID,
            expected_manifest_ids=(TARGET_MANIFEST_ID,),
            expected_families=tuple(
                sorted({case.family for case in self.fixture_cases})
            ),
            expected_operations=("compile", "module_call", "pattern_call"),
            expected_text_models=("str",),
        )
        assert_correctness_suite_case_accounting(
            self,
            workflow_suite,
            expected_case_count=len(self.fixture_cases),
        )

        for suite_id in EXPECTED_SUITE_IDS[1:]:
            assert_correctness_suite_summary_consistent(self, scorecard, suite_id)

        cpython_adapter = CpythonReAdapter()
        rebar_adapter = RebarAdapter()
        for fixture_case in self.fixture_cases:
            with self.subTest(case_id=fixture_case.case_id):
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
