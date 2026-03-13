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


class CorrectnessHarnessOptionalGroupAlternationBranchLocalBackreferenceWorkflowTest(
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

    def test_runner_regenerates_combined_optional_group_alternation_branch_local_backreference_scorecard(
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
            "optional-group-alternation-branch-local-backreference-workflows",
            scorecard["fixtures"]["manifest_ids"],
        )
        self.assertEqual(scorecard["summary"], tracked_scorecard["summary"])
        self.assertEqual(len(scorecard["cases"]), len(tracked_scorecard["cases"]))

        match_layer = scorecard["layers"]["match_behavior"]
        self.assertIn(
            "optional-group-alternation-branch-local-backreference-workflows",
            match_layer["manifest_ids"],
        )
        self.assertEqual(
            match_layer["summary"],
            tracked_scorecard["layers"]["match_behavior"]["summary"],
        )

        suite_ids = [suite["id"] for suite in scorecard["suites"]]
        self.assertIn(
            "match.optional_group_alternation_branch_local_backreference",
            suite_ids,
        )
        self.assertIn(
            "match.optional_group_alternation_branch_local_backreference.str",
            suite_ids,
        )
        self.assertIn(
            "match.optional_group_alternation_branch_local_backreference.compile",
            suite_ids,
        )
        self.assertIn(
            "match.optional_group_alternation_branch_local_backreference.module_call",
            suite_ids,
        )
        self.assertIn(
            "match.optional_group_alternation_branch_local_backreference.pattern_call",
            suite_ids,
        )

        workflow_suite = next(
            suite
            for suite in scorecard["suites"]
            if suite["id"] == "match.optional_group_alternation_branch_local_backreference"
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
                "optional_group_alternation_branch_local_named_backreference_compile_metadata",
                "optional_group_alternation_branch_local_named_backreference_module_c_branch_workflow",
                "optional_group_alternation_branch_local_named_backreference_pattern_absent_group_workflow",
                "optional_group_alternation_branch_local_named_backreference_pattern_b_branch_workflow",
                "optional_group_alternation_branch_local_named_backreference_pattern_no_match_workflow",
                "optional_group_alternation_branch_local_numbered_backreference_compile_metadata",
                "optional_group_alternation_branch_local_numbered_backreference_module_b_branch_workflow",
                "optional_group_alternation_branch_local_numbered_backreference_pattern_absent_group_workflow",
                "optional_group_alternation_branch_local_numbered_backreference_pattern_c_branch_workflow",
                "optional_group_alternation_branch_local_numbered_backreference_pattern_no_match_workflow",
            ],
        )

        cases_by_id = {case["id"]: case for case in scorecard["cases"]}

        numbered_compile_case = cases_by_id[
            "optional-group-alternation-branch-local-numbered-backreference-compile-metadata-str"
        ]
        self.assertIn(numbered_compile_case["comparison"], {"pass", "unimplemented"})
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
                "pattern": "a((b|c)\\2)?d",
                "pattern_type": "str",
            },
        )

        numbered_b_branch_case = cases_by_id[
            "optional-group-alternation-branch-local-numbered-backreference-module-search-b-branch-str"
        ]
        self.assertEqual(numbered_b_branch_case["helper"], "search")
        self.assertEqual(numbered_b_branch_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(
            numbered_b_branch_case["observations"]["cpython"]["result"]["group0"],
            "abbd",
        )
        self.assertEqual(
            numbered_b_branch_case["observations"]["cpython"]["result"]["groups"],
            ["bb", "b"],
        )
        self.assertEqual(
            numbered_b_branch_case["observations"]["cpython"]["result"]["group_spans"],
            [[3, 5], [3, 4]],
        )
        self.assert_rebar_pass_or_unimplemented(
            numbered_b_branch_case,
            expected_result={
                "endpos": 8,
                "group0": "abbd",
                "group1": "bb",
                "group_spans": [[3, 5], [3, 4]],
                "groupdict": {},
                "groups": ["bb", "b"],
                "lastgroup": None,
                "lastindex": 1,
                "matched": True,
                "pos": 0,
                "span": [2, 6],
                "span1": [3, 5],
                "string_type": "str",
            },
        )

        numbered_c_branch_case = cases_by_id[
            "optional-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-c-branch-str"
        ]
        self.assertEqual(numbered_c_branch_case["helper"], "fullmatch")
        self.assertEqual(numbered_c_branch_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(
            numbered_c_branch_case["observations"]["cpython"]["result"]["group0"],
            "accd",
        )
        self.assertEqual(
            numbered_c_branch_case["observations"]["cpython"]["result"]["groups"],
            ["cc", "c"],
        )
        self.assertEqual(
            numbered_c_branch_case["observations"]["cpython"]["result"]["span"],
            [0, 4],
        )
        self.assert_rebar_pass_or_unimplemented(
            numbered_c_branch_case,
            expected_result={
                "endpos": 4,
                "group0": "accd",
                "group1": "cc",
                "group_spans": [[1, 3], [1, 2]],
                "groupdict": {},
                "groups": ["cc", "c"],
                "lastgroup": None,
                "lastindex": 1,
                "matched": True,
                "pos": 0,
                "span": [0, 4],
                "span1": [1, 3],
                "string_type": "str",
            },
        )

        numbered_absent_case = cases_by_id[
            "optional-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-absent-group-str"
        ]
        self.assertEqual(numbered_absent_case["helper"], "fullmatch")
        self.assertEqual(numbered_absent_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(
            numbered_absent_case["observations"]["cpython"]["result"]["group0"],
            "ad",
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
                "endpos": 2,
                "group0": "ad",
                "group1": None,
                "group_spans": [[-1, -1], [-1, -1]],
                "groupdict": {},
                "groups": [None, None],
                "lastgroup": None,
                "lastindex": None,
                "matched": True,
                "pos": 0,
                "span": [0, 2],
                "span1": [-1, -1],
                "string_type": "str",
            },
        )

        numbered_no_match_case = cases_by_id[
            "optional-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-str"
        ]
        self.assertEqual(numbered_no_match_case["helper"], "fullmatch")
        self.assertEqual(numbered_no_match_case["observations"]["cpython"]["outcome"], "success")
        self.assertIsNone(numbered_no_match_case["observations"]["cpython"]["result"])
        self.assert_rebar_pass_or_unimplemented(
            numbered_no_match_case,
            expected_result=None,
        )

        named_compile_case = cases_by_id[
            "optional-group-alternation-branch-local-named-backreference-compile-metadata-str"
        ]
        self.assertEqual(named_compile_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(
            named_compile_case["observations"]["cpython"]["result"]["groupindex"],
            {"inner": 2, "outer": 1},
        )
        self.assertEqual(named_compile_case["observations"]["cpython"]["result"]["groups"], 2)
        self.assert_rebar_pass_or_unimplemented(
            named_compile_case,
            expected_result={
                "flags": 32,
                "groupindex": {"inner": 2, "outer": 1},
                "groups": 2,
                "pattern": "a(?P<outer>(?P<inner>b|c)(?P=inner))?d",
                "pattern_type": "str",
            },
        )

        named_c_branch_case = cases_by_id[
            "optional-group-alternation-branch-local-named-backreference-module-search-c-branch-str"
        ]
        self.assertEqual(named_c_branch_case["helper"], "search")
        self.assertEqual(named_c_branch_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(named_c_branch_case["observations"]["cpython"]["result"]["group0"], "accd")
        self.assertEqual(
            named_c_branch_case["observations"]["cpython"]["result"]["named_groups"],
            {"inner": "c", "outer": "cc"},
        )
        self.assertEqual(
            named_c_branch_case["observations"]["cpython"]["result"]["named_group_spans"],
            {"inner": [3, 4], "outer": [3, 5]},
        )
        self.assert_rebar_pass_or_unimplemented(
            named_c_branch_case,
            expected_result={
                "endpos": 8,
                "group0": "accd",
                "group1": "cc",
                "group_spans": [[3, 5], [3, 4]],
                "groupdict": {"inner": "c", "outer": "cc"},
                "groups": ["cc", "c"],
                "lastgroup": "outer",
                "lastindex": 1,
                "matched": True,
                "named_group_spans": {"inner": [3, 4], "outer": [3, 5]},
                "named_groups": {"inner": "c", "outer": "cc"},
                "pos": 0,
                "span": [2, 6],
                "span1": [3, 5],
                "string_type": "str",
            },
        )

        named_b_branch_case = cases_by_id[
            "optional-group-alternation-branch-local-named-backreference-pattern-fullmatch-b-branch-str"
        ]
        self.assertEqual(named_b_branch_case["helper"], "fullmatch")
        self.assertEqual(named_b_branch_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(named_b_branch_case["observations"]["cpython"]["result"]["group0"], "abbd")
        self.assertEqual(
            named_b_branch_case["observations"]["cpython"]["result"]["named_groups"],
            {"inner": "b", "outer": "bb"},
        )
        self.assertEqual(
            named_b_branch_case["observations"]["cpython"]["result"]["lastgroup"],
            "outer",
        )
        self.assert_rebar_pass_or_unimplemented(
            named_b_branch_case,
            expected_result={
                "endpos": 4,
                "group0": "abbd",
                "group1": "bb",
                "group_spans": [[1, 3], [1, 2]],
                "groupdict": {"inner": "b", "outer": "bb"},
                "groups": ["bb", "b"],
                "lastgroup": "outer",
                "lastindex": 1,
                "matched": True,
                "named_group_spans": {"inner": [1, 2], "outer": [1, 3]},
                "named_groups": {"inner": "b", "outer": "bb"},
                "pos": 0,
                "span": [0, 4],
                "span1": [1, 3],
                "string_type": "str",
            },
        )

        named_absent_case = cases_by_id[
            "optional-group-alternation-branch-local-named-backreference-pattern-fullmatch-absent-group-str"
        ]
        self.assertEqual(named_absent_case["helper"], "fullmatch")
        self.assertEqual(named_absent_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(named_absent_case["observations"]["cpython"]["result"]["group0"], "ad")
        self.assertEqual(
            named_absent_case["observations"]["cpython"]["result"]["named_groups"],
            {"inner": None, "outer": None},
        )
        self.assertEqual(
            named_absent_case["observations"]["cpython"]["result"]["group_spans"],
            [[-1, -1], [-1, -1]],
        )
        self.assert_rebar_pass_or_unimplemented(
            named_absent_case,
            expected_result={
                "endpos": 2,
                "group0": "ad",
                "group1": None,
                "group_spans": [[-1, -1], [-1, -1]],
                "groupdict": {"inner": None, "outer": None},
                "groups": [None, None],
                "lastgroup": None,
                "lastindex": None,
                "matched": True,
                "named_group_spans": {"inner": [-1, -1], "outer": [-1, -1]},
                "named_groups": {"inner": None, "outer": None},
                "pos": 0,
                "span": [0, 2],
                "span1": [-1, -1],
                "string_type": "str",
            },
        )

        named_no_match_case = cases_by_id[
            "optional-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-str"
        ]
        self.assertEqual(named_no_match_case["helper"], "fullmatch")
        self.assertEqual(named_no_match_case["observations"]["cpython"]["outcome"], "success")
        self.assertIsNone(named_no_match_case["observations"]["cpython"]["result"])
        self.assert_rebar_pass_or_unimplemented(
            named_no_match_case,
            expected_result=None,
        )


if __name__ == "__main__":
    unittest.main()
