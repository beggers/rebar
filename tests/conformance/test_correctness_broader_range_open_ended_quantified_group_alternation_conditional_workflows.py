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


class CorrectnessHarnessBroaderRangeOpenEndedQuantifiedGroupAlternationConditionalWorkflowTest(
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
        expected_result: dict[str, object] | None,
    ) -> None:
        self.assertEqual(case["helper"], helper)
        self.assertEqual(case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(case["observations"]["cpython"]["result"], expected_result)
        self.assert_rebar_pass_or_unimplemented(case, expected_result=expected_result)

    def test_runner_regenerates_combined_broader_range_open_ended_quantified_group_alternation_conditional_scorecard(
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
            "broader-range-open-ended-quantified-group-alternation-conditional-workflows",
            scorecard["fixtures"]["manifest_ids"],
        )
        self.assertEqual(scorecard["summary"], tracked_scorecard["summary"])
        self.assertEqual(len(scorecard["cases"]), len(tracked_scorecard["cases"]))

        match_layer = scorecard["layers"]["match_behavior"]
        self.assertIn(
            "broader-range-open-ended-quantified-group-alternation-conditional-workflows",
            match_layer["manifest_ids"],
        )
        self.assertEqual(
            match_layer["summary"],
            tracked_scorecard["layers"]["match_behavior"]["summary"],
        )

        suite_ids = [suite["id"] for suite in scorecard["suites"]]
        self.assertIn(
            "match.broader_range_open_ended_quantified_group_alternation_conditional",
            suite_ids,
        )
        self.assertIn(
            "match.broader_range_open_ended_quantified_group_alternation_conditional.str",
            suite_ids,
        )
        self.assertIn(
            "match.broader_range_open_ended_quantified_group_alternation_conditional.compile",
            suite_ids,
        )
        self.assertIn(
            "match.broader_range_open_ended_quantified_group_alternation_conditional.module_call",
            suite_ids,
        )
        self.assertIn(
            "match.broader_range_open_ended_quantified_group_alternation_conditional.pattern_call",
            suite_ids,
        )

        workflow_suite = next(
            suite
            for suite in scorecard["suites"]
            if suite["id"] == "match.broader_range_open_ended_quantified_group_alternation_conditional"
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
                "broader_range_open_ended_quantified_group_alternation_conditional_named_compile_metadata",
                "broader_range_open_ended_quantified_group_alternation_conditional_named_module_absent_workflow",
                "broader_range_open_ended_quantified_group_alternation_conditional_named_module_fourth_repetition_de_workflow",
                "broader_range_open_ended_quantified_group_alternation_conditional_named_module_lower_bound_de_workflow",
                "broader_range_open_ended_quantified_group_alternation_conditional_named_pattern_no_match_short_workflow",
                "broader_range_open_ended_quantified_group_alternation_conditional_named_pattern_third_repetition_mixed_workflow",
                "broader_range_open_ended_quantified_group_alternation_conditional_numbered_compile_metadata",
                "broader_range_open_ended_quantified_group_alternation_conditional_numbered_module_absent_workflow",
                "broader_range_open_ended_quantified_group_alternation_conditional_numbered_module_lower_bound_bc_workflow",
                "broader_range_open_ended_quantified_group_alternation_conditional_numbered_module_lower_bound_de_workflow",
                "broader_range_open_ended_quantified_group_alternation_conditional_numbered_pattern_no_match_missing_trailing_d_workflow",
                "broader_range_open_ended_quantified_group_alternation_conditional_numbered_pattern_no_match_one_repetition_workflow",
                "broader_range_open_ended_quantified_group_alternation_conditional_numbered_pattern_second_repetition_mixed_workflow",
                "broader_range_open_ended_quantified_group_alternation_conditional_numbered_pattern_third_repetition_mixed_workflow",
            ],
        )

        cases_by_id = {case["id"]: case for case in scorecard["cases"]}

        self.assert_compile_case(
            cases_by_id[
                "broader-range-open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-str"
            ],
            pattern="a((bc|de){2,})?(?(1)d|e)",
            groupindex={},
        )
        self.assert_match_case(
            cases_by_id[
                "broader-range-open-ended-quantified-group-alternation-conditional-numbered-module-search-absent-workflow-str"
            ],
            helper="search",
            expected_result={
                "endpos": 6,
                "group0": "ae",
                "group1": None,
                "group_spans": [[-1, -1], [-1, -1]],
                "groupdict": {},
                "groups": [None, None],
                "lastgroup": None,
                "lastindex": None,
                "matched": True,
                "pos": 0,
                "span": [2, 4],
                "span1": [-1, -1],
                "string_type": "str",
            },
        )
        self.assert_match_case(
            cases_by_id[
                "broader-range-open-ended-quantified-group-alternation-conditional-numbered-module-search-lower-bound-bc-workflow-str"
            ],
            helper="search",
            expected_result={
                "endpos": 10,
                "group0": "abcbcd",
                "group1": "bcbc",
                "group_spans": [[3, 7], [5, 7]],
                "groupdict": {},
                "groups": ["bcbc", "bc"],
                "lastgroup": None,
                "lastindex": 1,
                "matched": True,
                "pos": 0,
                "span": [2, 8],
                "span1": [3, 7],
                "string_type": "str",
            },
        )
        self.assert_match_case(
            cases_by_id[
                "broader-range-open-ended-quantified-group-alternation-conditional-numbered-module-search-lower-bound-de-workflow-str"
            ],
            helper="search",
            expected_result={
                "endpos": 10,
                "group0": "adeded",
                "group1": "dede",
                "group_spans": [[3, 7], [5, 7]],
                "groupdict": {},
                "groups": ["dede", "de"],
                "lastgroup": None,
                "lastindex": 1,
                "matched": True,
                "pos": 0,
                "span": [2, 8],
                "span1": [3, 7],
                "string_type": "str",
            },
        )
        self.assert_match_case(
            cases_by_id[
                "broader-range-open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-second-repetition-mixed-workflow-str"
            ],
            helper="fullmatch",
            expected_result={
                "endpos": 6,
                "group0": "abcded",
                "group1": "bcde",
                "group_spans": [[1, 5], [3, 5]],
                "groupdict": {},
                "groups": ["bcde", "de"],
                "lastgroup": None,
                "lastindex": 1,
                "matched": True,
                "pos": 0,
                "span": [0, 6],
                "span1": [1, 5],
                "string_type": "str",
            },
        )
        self.assert_match_case(
            cases_by_id[
                "broader-range-open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-third-repetition-mixed-workflow-str"
            ],
            helper="fullmatch",
            expected_result={
                "endpos": 8,
                "group0": "abcbcded",
                "group1": "bcbcde",
                "group_spans": [[1, 7], [5, 7]],
                "groupdict": {},
                "groups": ["bcbcde", "de"],
                "lastgroup": None,
                "lastindex": 1,
                "matched": True,
                "pos": 0,
                "span": [0, 8],
                "span1": [1, 7],
                "string_type": "str",
            },
        )
        self.assert_match_case(
            cases_by_id[
                "broader-range-open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-no-match-missing-trailing-d-workflow-str"
            ],
            helper="fullmatch",
            expected_result=None,
        )
        self.assert_match_case(
            cases_by_id[
                "broader-range-open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-no-match-one-repetition-str"
            ],
            helper="fullmatch",
            expected_result=None,
        )
        self.assert_compile_case(
            cases_by_id[
                "broader-range-open-ended-quantified-group-alternation-conditional-named-compile-metadata-str"
            ],
            pattern="a(?P<outer>(bc|de){2,})?(?(outer)d|e)",
            groupindex={"outer": 1},
        )
        self.assert_match_case(
            cases_by_id[
                "broader-range-open-ended-quantified-group-alternation-conditional-named-module-search-absent-workflow-str"
            ],
            helper="search",
            expected_result={
                "endpos": 6,
                "group0": "ae",
                "group1": None,
                "group_spans": [[-1, -1], [-1, -1]],
                "groupdict": {"outer": None},
                "groups": [None, None],
                "lastgroup": None,
                "lastindex": None,
                "matched": True,
                "named_group_spans": {"outer": [-1, -1]},
                "named_groups": {"outer": None},
                "pos": 0,
                "span": [2, 4],
                "span1": [-1, -1],
                "string_type": "str",
            },
        )
        self.assert_match_case(
            cases_by_id[
                "broader-range-open-ended-quantified-group-alternation-conditional-named-module-search-lower-bound-de-workflow-str"
            ],
            helper="search",
            expected_result={
                "endpos": 10,
                "group0": "adeded",
                "group1": "dede",
                "group_spans": [[3, 7], [5, 7]],
                "groupdict": {"outer": "dede"},
                "groups": ["dede", "de"],
                "lastgroup": "outer",
                "lastindex": 1,
                "matched": True,
                "named_group_spans": {"outer": [3, 7]},
                "named_groups": {"outer": "dede"},
                "pos": 0,
                "span": [2, 8],
                "span1": [3, 7],
                "string_type": "str",
            },
        )
        self.assert_match_case(
            cases_by_id[
                "broader-range-open-ended-quantified-group-alternation-conditional-named-module-search-fourth-repetition-de-workflow-str"
            ],
            helper="search",
            expected_result={
                "endpos": 12,
                "group0": "adededed",
                "group1": "dedede",
                "group_spans": [[3, 9], [7, 9]],
                "groupdict": {"outer": "dedede"},
                "groups": ["dedede", "de"],
                "lastgroup": "outer",
                "lastindex": 1,
                "matched": True,
                "named_group_spans": {"outer": [3, 9]},
                "named_groups": {"outer": "dedede"},
                "pos": 0,
                "span": [2, 10],
                "span1": [3, 9],
                "string_type": "str",
            },
        )
        self.assert_match_case(
            cases_by_id[
                "broader-range-open-ended-quantified-group-alternation-conditional-named-pattern-fullmatch-third-repetition-mixed-workflow-str"
            ],
            helper="fullmatch",
            expected_result={
                "endpos": 8,
                "group0": "abcbcded",
                "group1": "bcbcde",
                "group_spans": [[1, 7], [5, 7]],
                "groupdict": {"outer": "bcbcde"},
                "groups": ["bcbcde", "de"],
                "lastgroup": "outer",
                "lastindex": 1,
                "matched": True,
                "named_group_spans": {"outer": [1, 7]},
                "named_groups": {"outer": "bcbcde"},
                "pos": 0,
                "span": [0, 8],
                "span1": [1, 7],
                "string_type": "str",
            },
        )
        self.assert_match_case(
            cases_by_id[
                "broader-range-open-ended-quantified-group-alternation-conditional-named-pattern-fullmatch-no-match-short-workflow-str"
            ],
            helper="fullmatch",
            expected_result=None,
        )
