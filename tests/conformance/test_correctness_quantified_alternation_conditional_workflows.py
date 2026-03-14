from __future__ import annotations

import json
import pathlib
import platform
import subprocess
import sys
import tempfile
import unittest

from tests.conformance.scorecard_suite_support import load_published_correctness_scorecard


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.py"


class CorrectnessHarnessQuantifiedAlternationConditionalWorkflowTest(unittest.TestCase):
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

    def test_runner_regenerates_combined_quantified_alternation_conditional_scorecard(
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
        tracked_scorecard = load_published_correctness_scorecard()

        self.assertEqual(
            scorecard["fixtures"]["manifest_count"],
            tracked_scorecard["fixtures"]["manifest_count"],
        )
        self.assertIn(
            "quantified-alternation-conditional-workflows",
            scorecard["fixtures"]["manifest_ids"],
        )
        self.assertEqual(scorecard["summary"], tracked_scorecard["summary"])
        self.assertEqual(len(scorecard["cases"]), len(tracked_scorecard["cases"]))

        match_layer = scorecard["layers"]["match_behavior"]
        self.assertIn(
            "quantified-alternation-conditional-workflows",
            match_layer["manifest_ids"],
        )
        self.assertEqual(
            match_layer["summary"],
            tracked_scorecard["layers"]["match_behavior"]["summary"],
        )

        suite_ids = [suite["id"] for suite in scorecard["suites"]]
        self.assertIn("match.quantified_alternation_conditional", suite_ids)
        self.assertIn("match.quantified_alternation_conditional.str", suite_ids)
        self.assertIn("match.quantified_alternation_conditional.compile", suite_ids)
        self.assertIn("match.quantified_alternation_conditional.module_call", suite_ids)
        self.assertIn("match.quantified_alternation_conditional.pattern_call", suite_ids)

        workflow_suite = next(
            suite
            for suite in scorecard["suites"]
            if suite["id"] == "match.quantified_alternation_conditional"
        )
        self.assertEqual(workflow_suite["summary"]["total_cases"], 12)
        self.assertEqual(workflow_suite["summary"]["failed_cases"], 0)
        self.assertEqual(workflow_suite["summary"]["skipped_cases"], 0)
        self.assertEqual(
            workflow_suite["summary"]["passed_cases"]
            + workflow_suite["summary"]["unimplemented_cases"],
            12,
        )
        self.assertEqual(
            workflow_suite["families"],
            [
                "quantified_alternation_conditional_named_compile_metadata",
                "quantified_alternation_conditional_named_module_absent_workflow",
                "quantified_alternation_conditional_named_module_lower_bound_c_workflow",
                "quantified_alternation_conditional_named_pattern_no_match_workflow",
                "quantified_alternation_conditional_named_pattern_second_repetition_c_workflow",
                "quantified_alternation_conditional_named_pattern_second_repetition_mixed_workflow",
                "quantified_alternation_conditional_numbered_compile_metadata",
                "quantified_alternation_conditional_numbered_module_absent_workflow",
                "quantified_alternation_conditional_numbered_module_lower_bound_b_workflow",
                "quantified_alternation_conditional_numbered_pattern_no_match_workflow",
                "quantified_alternation_conditional_numbered_pattern_second_repetition_b_workflow",
                "quantified_alternation_conditional_numbered_pattern_second_repetition_mixed_workflow",
            ],
        )

        cases_by_id = {case["id"]: case for case in scorecard["cases"]}

        numbered_compile_case = cases_by_id[
            "quantified-alternation-conditional-numbered-compile-metadata-str"
        ]
        self.assertEqual(numbered_compile_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(
            numbered_compile_case["observations"]["cpython"]["result"]["groupindex"],
            {},
        )
        self.assertEqual(
            numbered_compile_case["observations"]["cpython"]["result"]["groups"],
            2,
        )
        self.assert_rebar_pass_or_unimplemented(
            numbered_compile_case,
            expected_result={
                "flags": 32,
                "groupindex": {},
                "groups": 2,
                "pattern": "a((b|c){1,2})?(?(1)d|e)",
                "pattern_type": "str",
            },
        )

        numbered_absent_case = cases_by_id[
            "quantified-alternation-conditional-numbered-module-search-absent-workflow-str"
        ]
        self.assertEqual(numbered_absent_case["helper"], "search")
        self.assertEqual(numbered_absent_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(
            numbered_absent_case["observations"]["cpython"]["result"]["group0"],
            "ae",
        )
        self.assertEqual(
            numbered_absent_case["observations"]["cpython"]["result"]["groups"],
            [None, None],
        )
        self.assertEqual(
            numbered_absent_case["observations"]["cpython"]["result"]["group_spans"],
            [[-1, -1], [-1, -1]],
        )
        self.assert_rebar_pass_or_unimplemented(
            numbered_absent_case,
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

        numbered_lower_bound_case = cases_by_id[
            "quantified-alternation-conditional-numbered-module-search-lower-bound-b-workflow-str"
        ]
        self.assertEqual(numbered_lower_bound_case["helper"], "search")
        self.assertEqual(
            numbered_lower_bound_case["observations"]["cpython"]["outcome"],
            "success",
        )
        self.assertEqual(
            numbered_lower_bound_case["observations"]["cpython"]["result"]["group0"],
            "abd",
        )
        self.assertEqual(
            numbered_lower_bound_case["observations"]["cpython"]["result"]["groups"],
            ["b", "b"],
        )
        self.assertEqual(
            numbered_lower_bound_case["observations"]["cpython"]["result"]["group_spans"],
            [[3, 4], [3, 4]],
        )
        self.assert_rebar_pass_or_unimplemented(
            numbered_lower_bound_case,
            expected_result={
                "endpos": 7,
                "group0": "abd",
                "group1": "b",
                "group_spans": [[3, 4], [3, 4]],
                "groupdict": {},
                "groups": ["b", "b"],
                "lastgroup": None,
                "lastindex": 1,
                "matched": True,
                "pos": 0,
                "span": [2, 5],
                "span1": [3, 4],
                "string_type": "str",
            },
        )

        numbered_second_repetition_b_case = cases_by_id[
            "quantified-alternation-conditional-numbered-pattern-fullmatch-second-repetition-b-workflow-str"
        ]
        self.assertEqual(numbered_second_repetition_b_case["helper"], "fullmatch")
        self.assertEqual(
            numbered_second_repetition_b_case["observations"]["cpython"]["outcome"],
            "success",
        )
        self.assertEqual(
            numbered_second_repetition_b_case["observations"]["cpython"]["result"]["group0"],
            "abbd",
        )
        self.assertEqual(
            numbered_second_repetition_b_case["observations"]["cpython"]["result"]["groups"],
            ["bb", "b"],
        )
        self.assertEqual(
            numbered_second_repetition_b_case["observations"]["cpython"]["result"]["group_spans"],
            [[1, 3], [2, 3]],
        )
        self.assert_rebar_pass_or_unimplemented(
            numbered_second_repetition_b_case,
            expected_result={
                "endpos": 4,
                "group0": "abbd",
                "group1": "bb",
                "group_spans": [[1, 3], [2, 3]],
                "groupdict": {},
                "groups": ["bb", "b"],
                "lastgroup": None,
                "lastindex": 1,
                "matched": True,
                "pos": 0,
                "span": [0, 4],
                "span1": [1, 3],
                "string_type": "str",
            },
        )

        numbered_second_repetition_mixed_case = cases_by_id[
            "quantified-alternation-conditional-numbered-pattern-fullmatch-second-repetition-mixed-workflow-str"
        ]
        self.assertEqual(numbered_second_repetition_mixed_case["helper"], "fullmatch")
        self.assertEqual(
            numbered_second_repetition_mixed_case["observations"]["cpython"]["outcome"],
            "success",
        )
        self.assertEqual(
            numbered_second_repetition_mixed_case["observations"]["cpython"]["result"]["group0"],
            "abcd",
        )
        self.assertEqual(
            numbered_second_repetition_mixed_case["observations"]["cpython"]["result"]["groups"],
            ["bc", "c"],
        )
        self.assertEqual(
            numbered_second_repetition_mixed_case["observations"]["cpython"]["result"]["group_spans"],
            [[1, 3], [2, 3]],
        )
        self.assert_rebar_pass_or_unimplemented(
            numbered_second_repetition_mixed_case,
            expected_result={
                "endpos": 4,
                "group0": "abcd",
                "group1": "bc",
                "group_spans": [[1, 3], [2, 3]],
                "groupdict": {},
                "groups": ["bc", "c"],
                "lastgroup": None,
                "lastindex": 1,
                "matched": True,
                "pos": 0,
                "span": [0, 4],
                "span1": [1, 3],
                "string_type": "str",
            },
        )

        numbered_no_match_case = cases_by_id[
            "quantified-alternation-conditional-numbered-pattern-fullmatch-no-match-workflow-str"
        ]
        self.assertEqual(numbered_no_match_case["helper"], "fullmatch")
        self.assertEqual(
            numbered_no_match_case["observations"]["cpython"]["outcome"],
            "success",
        )
        self.assertIsNone(numbered_no_match_case["observations"]["cpython"]["result"])
        self.assert_rebar_pass_or_unimplemented(numbered_no_match_case, expected_result=None)

        named_compile_case = cases_by_id[
            "quantified-alternation-conditional-named-compile-metadata-str"
        ]
        self.assertEqual(named_compile_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(
            named_compile_case["observations"]["cpython"]["result"]["groupindex"],
            {"outer": 1},
        )
        self.assertEqual(
            named_compile_case["observations"]["cpython"]["result"]["groups"],
            2,
        )
        self.assert_rebar_pass_or_unimplemented(
            named_compile_case,
            expected_result={
                "flags": 32,
                "groupindex": {"outer": 1},
                "groups": 2,
                "pattern": "a(?P<outer>(b|c){1,2})?(?(outer)d|e)",
                "pattern_type": "str",
            },
        )

        named_absent_case = cases_by_id[
            "quantified-alternation-conditional-named-module-search-absent-workflow-str"
        ]
        self.assertEqual(named_absent_case["helper"], "search")
        self.assertEqual(named_absent_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(named_absent_case["observations"]["cpython"]["result"]["group0"], "ae")
        self.assertEqual(
            named_absent_case["observations"]["cpython"]["result"]["groups"],
            [None, None],
        )
        self.assertEqual(
            named_absent_case["observations"]["cpython"]["result"]["named_groups"],
            {"outer": None},
        )
        self.assert_rebar_pass_or_unimplemented(
            named_absent_case,
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

        named_lower_bound_case = cases_by_id[
            "quantified-alternation-conditional-named-module-search-lower-bound-c-workflow-str"
        ]
        self.assertEqual(named_lower_bound_case["helper"], "search")
        self.assertEqual(
            named_lower_bound_case["observations"]["cpython"]["outcome"],
            "success",
        )
        self.assertEqual(
            named_lower_bound_case["observations"]["cpython"]["result"]["group0"],
            "acd",
        )
        self.assertEqual(
            named_lower_bound_case["observations"]["cpython"]["result"]["groups"],
            ["c", "c"],
        )
        self.assertEqual(
            named_lower_bound_case["observations"]["cpython"]["result"]["named_groups"],
            {"outer": "c"},
        )
        self.assert_rebar_pass_or_unimplemented(
            named_lower_bound_case,
            expected_result={
                "endpos": 7,
                "group0": "acd",
                "group1": "c",
                "group_spans": [[3, 4], [3, 4]],
                "groupdict": {"outer": "c"},
                "groups": ["c", "c"],
                "lastgroup": "outer",
                "lastindex": 1,
                "matched": True,
                "named_group_spans": {"outer": [3, 4]},
                "named_groups": {"outer": "c"},
                "pos": 0,
                "span": [2, 5],
                "span1": [3, 4],
                "string_type": "str",
            },
        )

        named_second_repetition_c_case = cases_by_id[
            "quantified-alternation-conditional-named-pattern-fullmatch-second-repetition-c-workflow-str"
        ]
        self.assertEqual(named_second_repetition_c_case["helper"], "fullmatch")
        self.assertEqual(
            named_second_repetition_c_case["observations"]["cpython"]["outcome"],
            "success",
        )
        self.assertEqual(
            named_second_repetition_c_case["observations"]["cpython"]["result"]["group0"],
            "accd",
        )
        self.assertEqual(
            named_second_repetition_c_case["observations"]["cpython"]["result"]["groups"],
            ["cc", "c"],
        )
        self.assertEqual(
            named_second_repetition_c_case["observations"]["cpython"]["result"]["named_groups"],
            {"outer": "cc"},
        )
        self.assert_rebar_pass_or_unimplemented(
            named_second_repetition_c_case,
            expected_result={
                "endpos": 4,
                "group0": "accd",
                "group1": "cc",
                "group_spans": [[1, 3], [2, 3]],
                "groupdict": {"outer": "cc"},
                "groups": ["cc", "c"],
                "lastgroup": "outer",
                "lastindex": 1,
                "matched": True,
                "named_group_spans": {"outer": [1, 3]},
                "named_groups": {"outer": "cc"},
                "pos": 0,
                "span": [0, 4],
                "span1": [1, 3],
                "string_type": "str",
            },
        )

        named_second_repetition_mixed_case = cases_by_id[
            "quantified-alternation-conditional-named-pattern-fullmatch-second-repetition-mixed-workflow-str"
        ]
        self.assertEqual(named_second_repetition_mixed_case["helper"], "fullmatch")
        self.assertEqual(
            named_second_repetition_mixed_case["observations"]["cpython"]["outcome"],
            "success",
        )
        self.assertEqual(
            named_second_repetition_mixed_case["observations"]["cpython"]["result"]["group0"],
            "abcd",
        )
        self.assertEqual(
            named_second_repetition_mixed_case["observations"]["cpython"]["result"]["groups"],
            ["bc", "c"],
        )
        self.assertEqual(
            named_second_repetition_mixed_case["observations"]["cpython"]["result"]["named_groups"],
            {"outer": "bc"},
        )
        self.assert_rebar_pass_or_unimplemented(
            named_second_repetition_mixed_case,
            expected_result={
                "endpos": 4,
                "group0": "abcd",
                "group1": "bc",
                "group_spans": [[1, 3], [2, 3]],
                "groupdict": {"outer": "bc"},
                "groups": ["bc", "c"],
                "lastgroup": "outer",
                "lastindex": 1,
                "matched": True,
                "named_group_spans": {"outer": [1, 3]},
                "named_groups": {"outer": "bc"},
                "pos": 0,
                "span": [0, 4],
                "span1": [1, 3],
                "string_type": "str",
            },
        )

        named_no_match_case = cases_by_id[
            "quantified-alternation-conditional-named-pattern-fullmatch-no-match-workflow-str"
        ]
        self.assertEqual(named_no_match_case["helper"], "fullmatch")
        self.assertEqual(
            named_no_match_case["observations"]["cpython"]["outcome"],
            "success",
        )
        self.assertIsNone(named_no_match_case["observations"]["cpython"]["result"])
        self.assert_rebar_pass_or_unimplemented(named_no_match_case, expected_result=None)


if __name__ == "__main__":
    unittest.main()
