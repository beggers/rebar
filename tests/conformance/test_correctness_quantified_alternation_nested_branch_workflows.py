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


class CorrectnessHarnessQuantifiedAlternationNestedBranchWorkflowTest(unittest.TestCase):
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

    def test_runner_regenerates_combined_quantified_alternation_nested_branch_scorecard(
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
            "quantified-alternation-nested-branch-workflows",
            scorecard["fixtures"]["manifest_ids"],
        )
        self.assertEqual(scorecard["summary"], tracked_scorecard["summary"])
        self.assertEqual(len(scorecard["cases"]), len(tracked_scorecard["cases"]))

        match_layer = scorecard["layers"]["match_behavior"]
        self.assertIn(
            "quantified-alternation-nested-branch-workflows",
            match_layer["manifest_ids"],
        )
        self.assertEqual(
            match_layer["summary"],
            tracked_scorecard["layers"]["match_behavior"]["summary"],
        )

        suite_ids = [suite["id"] for suite in scorecard["suites"]]
        self.assertIn("match.quantified_alternation_nested_branch", suite_ids)
        self.assertIn("match.quantified_alternation_nested_branch.str", suite_ids)
        self.assertIn("match.quantified_alternation_nested_branch.compile", suite_ids)
        self.assertIn("match.quantified_alternation_nested_branch.module_call", suite_ids)
        self.assertIn("match.quantified_alternation_nested_branch.pattern_call", suite_ids)

        workflow_suite = next(
            suite
            for suite in scorecard["suites"]
            if suite["id"] == "match.quantified_alternation_nested_branch"
        )
        self.assertEqual(workflow_suite["summary"]["total_cases"], 10)
        self.assertEqual(workflow_suite["summary"]["failed_cases"], 0)
        self.assertEqual(workflow_suite["summary"]["skipped_cases"], 0)
        self.assertEqual(
            workflow_suite["summary"]["passed_cases"]
            + workflow_suite["summary"]["unimplemented_cases"],
            10,
        )
        self.assertEqual(
            workflow_suite["families"],
            [
                "quantified_alternation_nested_branch_named_compile_metadata",
                "quantified_alternation_nested_branch_named_module_lower_bound_literal_branch_workflow",
                "quantified_alternation_nested_branch_named_pattern_lower_bound_inner_branch_workflow",
                "quantified_alternation_nested_branch_named_pattern_no_match_workflow",
                "quantified_alternation_nested_branch_named_pattern_second_repetition_mixed_branches_workflow",
                "quantified_alternation_nested_branch_numbered_compile_metadata",
                "quantified_alternation_nested_branch_numbered_module_lower_bound_inner_branch_workflow",
                "quantified_alternation_nested_branch_numbered_pattern_lower_bound_literal_branch_workflow",
                "quantified_alternation_nested_branch_numbered_pattern_no_match_workflow",
                "quantified_alternation_nested_branch_numbered_pattern_second_repetition_mixed_branches_workflow",
            ],
        )

        cases_by_id = {case["id"]: case for case in scorecard["cases"]}

        numbered_compile_case = cases_by_id[
            "quantified-alternation-nested-branch-numbered-compile-metadata-str"
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
                "pattern": "a((b|c)|de){1,2}d",
                "pattern_type": "str",
            },
        )

        numbered_inner_case = cases_by_id[
            "quantified-alternation-nested-branch-numbered-module-search-lower-bound-inner-branch-str"
        ]
        self.assertEqual(numbered_inner_case["helper"], "search")
        self.assertEqual(numbered_inner_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(
            numbered_inner_case["observations"]["cpython"]["result"]["group0"],
            "abd",
        )
        self.assertEqual(
            numbered_inner_case["observations"]["cpython"]["result"]["groups"],
            ["b", "b"],
        )
        self.assertEqual(
            numbered_inner_case["observations"]["cpython"]["result"]["group_spans"],
            [[3, 4], [3, 4]],
        )
        self.assert_rebar_pass_or_unimplemented(
            numbered_inner_case,
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

        numbered_literal_case = cases_by_id[
            "quantified-alternation-nested-branch-numbered-pattern-fullmatch-lower-bound-literal-branch-str"
        ]
        self.assertEqual(numbered_literal_case["helper"], "fullmatch")
        self.assertEqual(
            numbered_literal_case["observations"]["cpython"]["outcome"],
            "success",
        )
        self.assertEqual(
            numbered_literal_case["observations"]["cpython"]["result"]["group0"],
            "aded",
        )
        self.assertEqual(
            numbered_literal_case["observations"]["cpython"]["result"]["groups"],
            ["de", None],
        )
        self.assertEqual(
            numbered_literal_case["observations"]["cpython"]["result"]["group_spans"],
            [[1, 3], [-1, -1]],
        )
        self.assert_rebar_pass_or_unimplemented(
            numbered_literal_case,
            expected_result={
                "endpos": 4,
                "group0": "aded",
                "group1": "de",
                "group_spans": [[1, 3], [-1, -1]],
                "groupdict": {},
                "groups": ["de", None],
                "lastgroup": None,
                "lastindex": 1,
                "matched": True,
                "pos": 0,
                "span": [0, 4],
                "span1": [1, 3],
                "string_type": "str",
            },
        )

        numbered_mixed_case = cases_by_id[
            "quantified-alternation-nested-branch-numbered-pattern-fullmatch-second-repetition-mixed-branches-str"
        ]
        self.assertEqual(numbered_mixed_case["helper"], "fullmatch")
        self.assertEqual(
            numbered_mixed_case["observations"]["cpython"]["outcome"],
            "success",
        )
        self.assertEqual(
            numbered_mixed_case["observations"]["cpython"]["result"]["group0"],
            "abded",
        )
        self.assertEqual(
            numbered_mixed_case["observations"]["cpython"]["result"]["groups"],
            ["de", "b"],
        )
        self.assertEqual(
            numbered_mixed_case["observations"]["cpython"]["result"]["group_spans"],
            [[2, 4], [1, 2]],
        )
        self.assert_rebar_pass_or_unimplemented(
            numbered_mixed_case,
            expected_result={
                "endpos": 5,
                "group0": "abded",
                "group1": "de",
                "group_spans": [[2, 4], [1, 2]],
                "groupdict": {},
                "groups": ["de", "b"],
                "lastgroup": None,
                "lastindex": 1,
                "matched": True,
                "pos": 0,
                "span": [0, 5],
                "span1": [2, 4],
                "string_type": "str",
            },
        )

        numbered_no_match_case = cases_by_id[
            "quantified-alternation-nested-branch-numbered-pattern-fullmatch-no-match-str"
        ]
        self.assertEqual(numbered_no_match_case["helper"], "fullmatch")
        self.assertEqual(
            numbered_no_match_case["observations"]["cpython"]["outcome"],
            "success",
        )
        self.assertIsNone(numbered_no_match_case["observations"]["cpython"]["result"])
        self.assert_rebar_pass_or_unimplemented(numbered_no_match_case, expected_result=None)

        named_compile_case = cases_by_id[
            "quantified-alternation-nested-branch-named-compile-metadata-str"
        ]
        self.assertEqual(named_compile_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(
            named_compile_case["observations"]["cpython"]["result"]["groupindex"],
            {"word": 1},
        )
        self.assertEqual(named_compile_case["observations"]["cpython"]["result"]["groups"], 2)
        self.assert_rebar_pass_or_unimplemented(
            named_compile_case,
            expected_result={
                "flags": 32,
                "groupindex": {"word": 1},
                "groups": 2,
                "pattern": "a(?P<word>(b|c)|de){1,2}d",
                "pattern_type": "str",
            },
        )

        named_literal_case = cases_by_id[
            "quantified-alternation-nested-branch-named-module-search-lower-bound-literal-branch-str"
        ]
        self.assertEqual(named_literal_case["helper"], "search")
        self.assertEqual(named_literal_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(
            named_literal_case["observations"]["cpython"]["result"]["group0"],
            "aded",
        )
        self.assertEqual(
            named_literal_case["observations"]["cpython"]["result"]["named_groups"],
            {"word": "de"},
        )
        self.assertEqual(
            named_literal_case["observations"]["cpython"]["result"]["named_group_spans"],
            {"word": [3, 5]},
        )
        self.assert_rebar_pass_or_unimplemented(
            named_literal_case,
            expected_result={
                "endpos": 8,
                "group0": "aded",
                "group1": "de",
                "group_spans": [[3, 5], [-1, -1]],
                "groupdict": {"word": "de"},
                "groups": ["de", None],
                "lastgroup": "word",
                "lastindex": 1,
                "matched": True,
                "named_group_spans": {"word": [3, 5]},
                "named_groups": {"word": "de"},
                "pos": 0,
                "span": [2, 6],
                "span1": [3, 5],
                "string_type": "str",
            },
        )

        named_inner_case = cases_by_id[
            "quantified-alternation-nested-branch-named-pattern-fullmatch-lower-bound-inner-branch-str"
        ]
        self.assertEqual(named_inner_case["helper"], "fullmatch")
        self.assertEqual(named_inner_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(
            named_inner_case["observations"]["cpython"]["result"]["group0"],
            "acd",
        )
        self.assertEqual(
            named_inner_case["observations"]["cpython"]["result"]["named_groups"],
            {"word": "c"},
        )
        self.assertEqual(
            named_inner_case["observations"]["cpython"]["result"]["named_group_spans"],
            {"word": [1, 2]},
        )
        self.assert_rebar_pass_or_unimplemented(
            named_inner_case,
            expected_result={
                "endpos": 3,
                "group0": "acd",
                "group1": "c",
                "group_spans": [[1, 2], [1, 2]],
                "groupdict": {"word": "c"},
                "groups": ["c", "c"],
                "lastgroup": "word",
                "lastindex": 1,
                "matched": True,
                "named_group_spans": {"word": [1, 2]},
                "named_groups": {"word": "c"},
                "pos": 0,
                "span": [0, 3],
                "span1": [1, 2],
                "string_type": "str",
            },
        )

        named_mixed_case = cases_by_id[
            "quantified-alternation-nested-branch-named-pattern-fullmatch-second-repetition-mixed-branches-str"
        ]
        self.assertEqual(named_mixed_case["helper"], "fullmatch")
        self.assertEqual(
            named_mixed_case["observations"]["cpython"]["outcome"],
            "success",
        )
        self.assertEqual(
            named_mixed_case["observations"]["cpython"]["result"]["group0"],
            "adebd",
        )
        self.assertEqual(
            named_mixed_case["observations"]["cpython"]["result"]["named_groups"],
            {"word": "b"},
        )
        self.assertEqual(
            named_mixed_case["observations"]["cpython"]["result"]["named_group_spans"],
            {"word": [3, 4]},
        )
        self.assert_rebar_pass_or_unimplemented(
            named_mixed_case,
            expected_result={
                "endpos": 5,
                "group0": "adebd",
                "group1": "b",
                "group_spans": [[3, 4], [3, 4]],
                "groupdict": {"word": "b"},
                "groups": ["b", "b"],
                "lastgroup": "word",
                "lastindex": 1,
                "matched": True,
                "named_group_spans": {"word": [3, 4]},
                "named_groups": {"word": "b"},
                "pos": 0,
                "span": [0, 5],
                "span1": [3, 4],
                "string_type": "str",
            },
        )

        named_no_match_case = cases_by_id[
            "quantified-alternation-nested-branch-named-pattern-fullmatch-no-match-str"
        ]
        self.assertEqual(named_no_match_case["helper"], "fullmatch")
        self.assertEqual(
            named_no_match_case["observations"]["cpython"]["outcome"],
            "success",
        )
        self.assertIsNone(named_no_match_case["observations"]["cpython"]["result"])
        self.assert_rebar_pass_or_unimplemented(named_no_match_case, expected_result=None)
