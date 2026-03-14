from __future__ import annotations

import json
import pathlib
import platform
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.json"


class CorrectnessHarnessBroaderRangeWiderRangedRepeatQuantifiedGroupAlternationBacktrackingHeavyWorkflowTest(
    unittest.TestCase
):
    def assert_rebar_pass_or_unimplemented(
        self,
        case: dict[str, object],
        *,
        expected_result: object | None = None,
    ) -> None:
        comparison = case["comparison"]
        rebar_observation = case["observations"]["rebar"]

        if comparison == "pass":
            self.assertEqual(rebar_observation["outcome"], "success")
            self.assertEqual(rebar_observation["result"], expected_result)
            return

        self.assertEqual(comparison, "unimplemented")
        self.assertEqual(rebar_observation["outcome"], "unimplemented")

    def assert_compile_case(
        self,
        case: dict[str, object],
        *,
        pattern: str,
        groupindex: dict[str, int],
    ) -> None:
        expected_result = {
            "flags": 32,
            "groupindex": groupindex,
            "groups": 2,
            "pattern": pattern,
            "pattern_type": "str",
        }
        self.assertEqual(case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(case["observations"]["cpython"]["result"], expected_result)
        self.assert_rebar_pass_or_unimplemented(case, expected_result=expected_result)

    def assert_match_case(
        self,
        case: dict[str, object],
        *,
        helper: str,
        group0: str | None,
        group1: str | None = None,
        group2: str | None = None,
        endpos: int,
        span: list[int] | None = None,
        span1: list[int] | None = None,
        span2: list[int] | None = None,
        named: bool = False,
    ) -> None:
        self.assertEqual(case["helper"], helper)
        self.assertEqual(case["observations"]["cpython"]["outcome"], "success")

        if group0 is None:
            self.assertIsNone(case["observations"]["cpython"]["result"])
            self.assert_rebar_pass_or_unimplemented(case, expected_result=None)
            return

        result = {
            "endpos": endpos,
            "group0": group0,
            "group1": group1,
            "group_spans": [span1, span2],
            "groupdict": {"word": group1} if named else {},
            "groups": [group1, group2],
            "lastgroup": "word" if named else None,
            "lastindex": 1,
            "matched": True,
            "pos": 0,
            "span": span,
            "span1": span1,
            "string_type": "str",
        }
        if named:
            result["named_group_spans"] = {"word": span1}
            result["named_groups"] = {"word": group1}

        self.assertEqual(case["observations"]["cpython"]["result"], result)
        self.assert_rebar_pass_or_unimplemented(case, expected_result=result)

    def test_runner_regenerates_combined_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_scorecard(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = pathlib.Path(temp_dir) / "correctness.json"
            subprocess.run(
                ["cargo", "build", "-p", "rebar-cpython"],
                check=True,
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
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

        self.assertEqual(scorecard["schema_version"], "1.0")
        self.assertEqual(scorecard["phase"], "phase3-module-workflow-pack")
        self.assertEqual(
            scorecard["baseline"]["python_implementation"],
            platform.python_implementation(),
        )
        self.assertEqual(scorecard["baseline"]["python_version"], platform.python_version())
        self.assertEqual(scorecard["baseline"]["python_version_family"], "3.12.x")
        self.assertEqual(
            scorecard["baseline"]["python_build"],
            {
                "name": platform.python_build()[0],
                "date": platform.python_build()[1],
            },
        )
        self.assertEqual(scorecard["baseline"]["python_compiler"], platform.python_compiler())
        self.assertEqual(scorecard["baseline"]["platform"], platform.platform())
        self.assertEqual(scorecard["baseline"]["executable"], sys.executable)
        self.assertEqual(scorecard["baseline"]["re_module"], "re")
        self.assertEqual(scorecard["summary"], summary)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())
        tracked_scorecard = json.loads(TRACKED_REPORT_PATH.read_text(encoding="utf-8"))

        self.assertEqual(
            scorecard["fixtures"]["manifest_count"],
            tracked_scorecard["fixtures"]["manifest_count"],
        )
        self.assertIn(
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows",
            scorecard["fixtures"]["manifest_ids"],
        )
        self.assertEqual(scorecard["summary"], tracked_scorecard["summary"])
        self.assertEqual(len(scorecard["cases"]), len(tracked_scorecard["cases"]))

        match_layer = scorecard["layers"]["match_behavior"]
        self.assertIn(
            "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows",
            match_layer["manifest_ids"],
        )
        self.assertEqual(
            match_layer["summary"],
            tracked_scorecard["layers"]["match_behavior"]["summary"],
        )

        suite_ids = [suite["id"] for suite in scorecard["suites"]]
        self.assertIn(
            "match.broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy",
            suite_ids,
        )
        self.assertIn(
            "match.broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy.str",
            suite_ids,
        )
        self.assertIn(
            "match.broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy.compile",
            suite_ids,
        )
        self.assertIn(
            "match.broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy.module_call",
            suite_ids,
        )
        self.assertIn(
            "match.broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy.pattern_call",
            suite_ids,
        )

        workflow_suite = next(
            suite
            for suite in scorecard["suites"]
            if suite["id"]
            == "match.broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy"
        )
        self.assertEqual(workflow_suite["summary"]["total_cases"], 14)
        self.assertEqual(workflow_suite["summary"]["failed_cases"], 0)
        self.assertEqual(workflow_suite["summary"]["skipped_cases"], 0)
        self.assertEqual(
            workflow_suite["summary"]["passed_cases"]
            + workflow_suite["summary"]["unimplemented_cases"],
            14,
        )
        self.assertEqual(
            workflow_suite["families"],
            [
                "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_named_compile_metadata",
                "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_named_module_fourth_repetition_mixed_workflow",
                "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_named_module_lower_bound_long_branch_workflow",
                "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_named_module_second_repetition_short_then_long_workflow",
                "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_named_pattern_no_match_invalid_tail_workflow",
                "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_named_pattern_no_match_overflow_workflow",
                "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_named_pattern_second_repetition_long_then_short_workflow",
                "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_numbered_compile_metadata",
                "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_numbered_module_lower_bound_long_branch_workflow",
                "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_numbered_module_lower_bound_short_branch_workflow",
                "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_numbered_pattern_fourth_repetition_mixed_workflow",
                "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_numbered_pattern_no_match_invalid_tail_workflow",
                "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_numbered_pattern_second_repetition_long_then_short_workflow",
                "broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_numbered_pattern_second_repetition_short_then_long_workflow",
            ],
        )

        cases_by_id = {case["id"]: case for case in scorecard["cases"]}

        self.assert_compile_case(
            cases_by_id[
                "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-str"
            ],
            pattern="a((bc|b)c){1,4}d",
            groupindex={},
        )
        self.assert_match_case(
            cases_by_id[
                "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-short-branch-str"
            ],
            helper="search",
            group0="abcd",
            group1="bc",
            group2="b",
            endpos=8,
            span=[2, 6],
            span1=[3, 5],
            span2=[3, 4],
        )
        self.assert_match_case(
            cases_by_id[
                "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-long-branch-str"
            ],
            helper="search",
            group0="abccd",
            group1="bcc",
            group2="bc",
            endpos=9,
            span=[2, 7],
            span1=[3, 6],
            span2=[3, 5],
        )
        self.assert_match_case(
            cases_by_id[
                "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-short-then-long-str"
            ],
            helper="fullmatch",
            group0="abcbccd",
            group1="bcc",
            group2="bc",
            endpos=7,
            span=[0, 7],
            span1=[3, 6],
            span2=[3, 5],
        )
        self.assert_match_case(
            cases_by_id[
                "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-long-then-short-str"
            ],
            helper="fullmatch",
            group0="abccbcd",
            group1="bc",
            group2="b",
            endpos=7,
            span=[0, 7],
            span1=[4, 6],
            span2=[4, 5],
        )
        self.assert_match_case(
            cases_by_id[
                "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-fourth-repetition-mixed-str"
            ],
            helper="fullmatch",
            group0="abcbccbccbcd",
            group1="bc",
            group2="b",
            endpos=12,
            span=[0, 12],
            span1=[9, 11],
            span2=[9, 10],
        )
        self.assert_match_case(
            cases_by_id[
                "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-no-match-invalid-tail-str"
            ],
            helper="fullmatch",
            group0=None,
            endpos=6,
        )

        self.assert_compile_case(
            cases_by_id[
                "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-compile-metadata-str"
            ],
            pattern="a(?P<word>(bc|b)c){1,4}d",
            groupindex={"word": 1},
        )
        self.assert_match_case(
            cases_by_id[
                "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-module-search-lower-bound-long-branch-str"
            ],
            helper="search",
            group0="abccd",
            group1="bcc",
            group2="bc",
            endpos=9,
            span=[2, 7],
            span1=[3, 6],
            span2=[3, 5],
            named=True,
        )
        self.assert_match_case(
            cases_by_id[
                "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-module-search-second-repetition-short-then-long-str"
            ],
            helper="search",
            group0="abcbccd",
            group1="bcc",
            group2="bc",
            endpos=11,
            span=[2, 9],
            span1=[5, 8],
            span2=[5, 7],
            named=True,
        )
        self.assert_match_case(
            cases_by_id[
                "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-module-search-fourth-repetition-mixed-str"
            ],
            helper="search",
            group0="abcbccbccbcd",
            group1="bc",
            group2="b",
            endpos=16,
            span=[2, 14],
            span1=[11, 13],
            span2=[11, 12],
            named=True,
        )
        self.assert_match_case(
            cases_by_id[
                "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-second-repetition-long-then-short-str"
            ],
            helper="fullmatch",
            group0="abccbcd",
            group1="bc",
            group2="b",
            endpos=7,
            span=[0, 7],
            span1=[4, 6],
            span2=[4, 5],
            named=True,
        )
        self.assert_match_case(
            cases_by_id[
                "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-no-match-invalid-tail-str"
            ],
            helper="fullmatch",
            group0=None,
            endpos=6,
            named=True,
        )
        self.assert_match_case(
            cases_by_id[
                "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-no-match-overflow-str"
            ],
            helper="fullmatch",
            group0=None,
            endpos=12,
            named=True,
        )


if __name__ == "__main__":
    unittest.main()
