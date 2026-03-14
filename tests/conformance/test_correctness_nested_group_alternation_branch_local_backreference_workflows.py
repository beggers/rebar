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


class CorrectnessHarnessNestedGroupAlternationBranchLocalBackreferenceWorkflowTest(
    unittest.TestCase
):
    def assert_rebar_pass_or_unimplemented(self, case: dict[str, object]) -> None:
        comparison = case["comparison"]
        cpython_observation = case["observations"]["cpython"]
        rebar_observation = case["observations"]["rebar"]

        if comparison == "pass":
            self.assertEqual(rebar_observation["outcome"], "success")
            self.assertEqual(rebar_observation["result"], cpython_observation["result"])
            return

        self.assertEqual(comparison, "unimplemented")
        self.assertEqual(rebar_observation["outcome"], "unimplemented")

    def test_runner_regenerates_combined_nested_group_alternation_branch_local_backreference_scorecard(
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
            "nested-group-alternation-branch-local-backreference-workflows",
            scorecard["fixtures"]["manifest_ids"],
        )
        self.assertEqual(scorecard["summary"], tracked_scorecard["summary"])
        self.assertEqual(len(scorecard["cases"]), len(tracked_scorecard["cases"]))

        match_layer = scorecard["layers"]["match_behavior"]
        self.assertIn(
            "nested-group-alternation-branch-local-backreference-workflows",
            match_layer["manifest_ids"],
        )
        self.assertEqual(
            match_layer["summary"],
            tracked_scorecard["layers"]["match_behavior"]["summary"],
        )

        suite_ids = [suite["id"] for suite in scorecard["suites"]]
        self.assertIn(
            "match.nested_group_alternation_branch_local_backreference",
            suite_ids,
        )
        self.assertIn(
            "match.nested_group_alternation_branch_local_backreference.str",
            suite_ids,
        )
        self.assertIn(
            "match.nested_group_alternation_branch_local_backreference.compile",
            suite_ids,
        )
        self.assertIn(
            "match.nested_group_alternation_branch_local_backreference.module_call",
            suite_ids,
        )
        self.assertIn(
            "match.nested_group_alternation_branch_local_backreference.pattern_call",
            suite_ids,
        )

        workflow_suite = next(
            suite
            for suite in scorecard["suites"]
            if suite["id"] == "match.nested_group_alternation_branch_local_backreference"
        )
        self.assertEqual(workflow_suite["summary"]["total_cases"], 8)
        self.assertEqual(workflow_suite["summary"]["failed_cases"], 0)
        self.assertEqual(workflow_suite["summary"]["skipped_cases"], 0)
        self.assertEqual(
            workflow_suite["summary"]["passed_cases"]
            + workflow_suite["summary"]["unimplemented_cases"],
            8,
        )
        self.assertEqual(
            workflow_suite["families"],
            [
                "nested_group_alternation_branch_local_named_backreference_compile_metadata",
                "nested_group_alternation_branch_local_named_backreference_module_c_branch_workflow",
                "nested_group_alternation_branch_local_named_backreference_pattern_b_branch_workflow",
                "nested_group_alternation_branch_local_named_backreference_pattern_no_match_workflow",
                "nested_group_alternation_branch_local_numbered_backreference_compile_metadata",
                "nested_group_alternation_branch_local_numbered_backreference_module_b_branch_workflow",
                "nested_group_alternation_branch_local_numbered_backreference_pattern_c_branch_workflow",
                "nested_group_alternation_branch_local_numbered_backreference_pattern_no_match_workflow",
            ],
        )

        cases_by_id = {case["id"]: case for case in scorecard["cases"]}

        numbered_compile_case = cases_by_id[
            "nested-group-alternation-branch-local-numbered-backreference-compile-metadata-str"
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
        self.assert_rebar_pass_or_unimplemented(numbered_compile_case)

        numbered_b_branch_case = cases_by_id[
            "nested-group-alternation-branch-local-numbered-backreference-module-search-b-branch-str"
        ]
        self.assertEqual(numbered_b_branch_case["helper"], "search")
        self.assertEqual(
            numbered_b_branch_case["observations"]["cpython"]["outcome"],
            "success",
        )
        self.assertEqual(
            numbered_b_branch_case["observations"]["cpython"]["result"]["group0"],
            "abbd",
        )
        self.assertEqual(
            numbered_b_branch_case["observations"]["cpython"]["result"]["groups"],
            ["b", "b"],
        )
        self.assertEqual(
            numbered_b_branch_case["observations"]["cpython"]["result"]["group_spans"],
            [[3, 4], [3, 4]],
        )
        self.assert_rebar_pass_or_unimplemented(numbered_b_branch_case)

        numbered_c_branch_case = cases_by_id[
            "nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-c-branch-str"
        ]
        self.assertEqual(numbered_c_branch_case["helper"], "fullmatch")
        self.assertEqual(
            numbered_c_branch_case["observations"]["cpython"]["outcome"],
            "success",
        )
        self.assertEqual(
            numbered_c_branch_case["observations"]["cpython"]["result"]["group0"],
            "accd",
        )
        self.assertEqual(
            numbered_c_branch_case["observations"]["cpython"]["result"]["groups"],
            ["c", "c"],
        )
        self.assertEqual(
            numbered_c_branch_case["observations"]["cpython"]["result"]["span"],
            [0, 4],
        )
        self.assert_rebar_pass_or_unimplemented(numbered_c_branch_case)

        numbered_no_match_case = cases_by_id[
            "nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-str"
        ]
        self.assertEqual(numbered_no_match_case["helper"], "fullmatch")
        self.assertIsNone(numbered_no_match_case["observations"]["cpython"]["result"])
        self.assert_rebar_pass_or_unimplemented(numbered_no_match_case)

        named_compile_case = cases_by_id[
            "nested-group-alternation-branch-local-named-backreference-compile-metadata-str"
        ]
        self.assertEqual(named_compile_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(
            named_compile_case["observations"]["cpython"]["result"]["groupindex"],
            {"inner": 2, "outer": 1},
        )
        self.assertEqual(
            named_compile_case["observations"]["cpython"]["result"]["groups"],
            2,
        )
        self.assert_rebar_pass_or_unimplemented(named_compile_case)

        named_c_branch_case = cases_by_id[
            "nested-group-alternation-branch-local-named-backreference-module-search-c-branch-str"
        ]
        self.assertEqual(named_c_branch_case["helper"], "search")
        self.assertEqual(
            named_c_branch_case["observations"]["cpython"]["outcome"],
            "success",
        )
        self.assertEqual(
            named_c_branch_case["observations"]["cpython"]["result"]["named_groups"],
            {"inner": "c", "outer": "c"},
        )
        self.assertEqual(
            named_c_branch_case["observations"]["cpython"]["result"]["named_group_spans"],
            {"inner": [3, 4], "outer": [3, 4]},
        )
        self.assertEqual(
            named_c_branch_case["observations"]["cpython"]["result"]["lastgroup"],
            "outer",
        )
        self.assert_rebar_pass_or_unimplemented(named_c_branch_case)

        named_b_branch_case = cases_by_id[
            "nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-b-branch-str"
        ]
        self.assertEqual(named_b_branch_case["helper"], "fullmatch")
        self.assertEqual(
            named_b_branch_case["observations"]["cpython"]["outcome"],
            "success",
        )
        self.assertEqual(
            named_b_branch_case["observations"]["cpython"]["result"]["named_groups"],
            {"inner": "b", "outer": "b"},
        )
        self.assertEqual(
            named_b_branch_case["observations"]["cpython"]["result"]["group_spans"],
            [[1, 2], [1, 2]],
        )
        self.assertEqual(
            named_b_branch_case["observations"]["cpython"]["result"]["lastgroup"],
            "outer",
        )
        self.assert_rebar_pass_or_unimplemented(named_b_branch_case)

        named_no_match_case = cases_by_id[
            "nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-str"
        ]
        self.assertEqual(named_no_match_case["helper"], "fullmatch")
        self.assertIsNone(named_no_match_case["observations"]["cpython"]["result"])
        self.assert_rebar_pass_or_unimplemented(named_no_match_case)


if __name__ == "__main__":
    unittest.main()
