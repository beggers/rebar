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


class CorrectnessHarnessQuantifiedNestedGroupAlternationBranchLocalBackreferenceWorkflowTest(
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

        self.assertIn(case["comparison"], {"pass", "unimplemented"})
        self.assertEqual(case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(case["observations"]["cpython"]["result"], expected_result)
        self.assert_rebar_pass_or_unimplemented(case, expected_result=expected_result)

    def assert_match_case(
        self,
        case: dict[str, object],
        *,
        helper: str,
        endpos: int,
        group0: str | None,
        groups: list[str] | None = None,
        group_spans: list[list[int]] | None = None,
        span: list[int] | None = None,
        named: bool = False,
    ) -> None:
        self.assertIn(case["comparison"], {"pass", "unimplemented"})
        self.assertEqual(case["helper"], helper)
        self.assertEqual(case["observations"]["cpython"]["outcome"], "success")

        if group0 is None:
            self.assertIsNone(case["observations"]["cpython"]["result"])
            self.assert_rebar_pass_or_unimplemented(case, expected_result=None)
            return

        assert groups is not None
        assert group_spans is not None
        assert span is not None

        expected_result: dict[str, object] = {
            "endpos": endpos,
            "group0": group0,
            "group1": groups[0],
            "group_spans": group_spans,
            "groupdict": {"inner": groups[1], "outer": groups[0]} if named else {},
            "groups": groups,
            "lastgroup": "outer" if named else None,
            "lastindex": 1,
            "matched": True,
            "pos": 0,
            "span": span,
            "span1": group_spans[0],
            "string_type": "str",
        }
        if named:
            expected_result["named_group_spans"] = {
                "inner": group_spans[1],
                "outer": group_spans[0],
            }
            expected_result["named_groups"] = {
                "inner": groups[1],
                "outer": groups[0],
            }

        self.assertEqual(case["observations"]["cpython"]["result"], expected_result)
        self.assert_rebar_pass_or_unimplemented(case, expected_result=expected_result)

    def test_runner_regenerates_combined_quantified_nested_group_alternation_branch_local_backreference_scorecard(
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
            "quantified-nested-group-alternation-workflows",
            scorecard["fixtures"]["manifest_ids"],
        )
        self.assertIn(
            "nested-group-alternation-branch-local-backreference-workflows",
            scorecard["fixtures"]["manifest_ids"],
        )
        self.assertIn(
            "quantified-nested-group-alternation-branch-local-backreference-workflows",
            scorecard["fixtures"]["manifest_ids"],
        )
        self.assertEqual(scorecard["summary"], tracked_scorecard["summary"])
        self.assertEqual(len(scorecard["cases"]), len(tracked_scorecard["cases"]))

        match_layer = scorecard["layers"]["match_behavior"]
        self.assertIn(
            "quantified-nested-group-alternation-branch-local-backreference-workflows",
            match_layer["manifest_ids"],
        )
        self.assertEqual(
            match_layer["summary"],
            tracked_scorecard["layers"]["match_behavior"]["summary"],
        )

        suite_ids = [suite["id"] for suite in scorecard["suites"]]
        self.assertIn(
            "match.quantified_nested_group_alternation_branch_local_backreference",
            suite_ids,
        )
        self.assertIn(
            "match.quantified_nested_group_alternation_branch_local_backreference.str",
            suite_ids,
        )
        self.assertIn(
            "match.quantified_nested_group_alternation_branch_local_backreference.compile",
            suite_ids,
        )
        self.assertIn(
            "match.quantified_nested_group_alternation_branch_local_backreference.module_call",
            suite_ids,
        )
        self.assertIn(
            "match.quantified_nested_group_alternation_branch_local_backreference.pattern_call",
            suite_ids,
        )

        workflow_suite = next(
            suite
            for suite in scorecard["suites"]
            if suite["id"] == "match.quantified_nested_group_alternation_branch_local_backreference"
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
                "quantified_nested_group_alternation_branch_local_named_backreference_compile_metadata",
                "quantified_nested_group_alternation_branch_local_named_backreference_module_lower_bound_c_branch_workflow",
                "quantified_nested_group_alternation_branch_local_named_backreference_pattern_lower_bound_b_branch_workflow",
                "quantified_nested_group_alternation_branch_local_named_backreference_pattern_no_match_workflow",
                "quantified_nested_group_alternation_branch_local_named_backreference_pattern_second_iteration_mixed_branches_workflow",
                "quantified_nested_group_alternation_branch_local_numbered_backreference_compile_metadata",
                "quantified_nested_group_alternation_branch_local_numbered_backreference_module_lower_bound_b_branch_workflow",
                "quantified_nested_group_alternation_branch_local_numbered_backreference_pattern_lower_bound_c_branch_workflow",
                "quantified_nested_group_alternation_branch_local_numbered_backreference_pattern_no_match_workflow",
                "quantified_nested_group_alternation_branch_local_numbered_backreference_pattern_second_iteration_b_branch_workflow",
            ],
        )

        cases_by_id = {case["id"]: case for case in scorecard["cases"]}

        self.assert_compile_case(
            cases_by_id[
                "quantified-nested-group-alternation-branch-local-numbered-backreference-compile-metadata-str"
            ],
            pattern=r"a((b|c)+)\2d",
            groupindex={},
        )
        self.assert_match_case(
            cases_by_id[
                "quantified-nested-group-alternation-branch-local-numbered-backreference-module-search-lower-bound-b-branch-str"
            ],
            helper="search",
            endpos=8,
            group0="abbd",
            groups=["b", "b"],
            group_spans=[[3, 4], [3, 4]],
            span=[2, 6],
        )
        self.assert_match_case(
            cases_by_id[
                "quantified-nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-lower-bound-c-branch-str"
            ],
            helper="fullmatch",
            endpos=4,
            group0="accd",
            groups=["c", "c"],
            group_spans=[[1, 2], [1, 2]],
            span=[0, 4],
        )
        self.assert_match_case(
            cases_by_id[
                "quantified-nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-second-iteration-b-branch-str"
            ],
            helper="fullmatch",
            endpos=5,
            group0="abbbd",
            groups=["bb", "b"],
            group_spans=[[1, 3], [2, 3]],
            span=[0, 5],
        )
        self.assert_match_case(
            cases_by_id[
                "quantified-nested-group-alternation-branch-local-numbered-backreference-pattern-fullmatch-no-match-str"
            ],
            helper="fullmatch",
            endpos=4,
            group0=None,
        )

        self.assert_compile_case(
            cases_by_id[
                "quantified-nested-group-alternation-branch-local-named-backreference-compile-metadata-str"
            ],
            pattern=r"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
            groupindex={"inner": 2, "outer": 1},
        )
        self.assert_match_case(
            cases_by_id[
                "quantified-nested-group-alternation-branch-local-named-backreference-module-search-lower-bound-c-branch-str"
            ],
            helper="search",
            endpos=8,
            group0="accd",
            groups=["c", "c"],
            group_spans=[[3, 4], [3, 4]],
            span=[2, 6],
            named=True,
        )
        self.assert_match_case(
            cases_by_id[
                "quantified-nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-lower-bound-b-branch-str"
            ],
            helper="fullmatch",
            endpos=4,
            group0="abbd",
            groups=["b", "b"],
            group_spans=[[1, 2], [1, 2]],
            span=[0, 4],
            named=True,
        )
        self.assert_match_case(
            cases_by_id[
                "quantified-nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-second-iteration-mixed-branches-str"
            ],
            helper="fullmatch",
            endpos=5,
            group0="abccd",
            groups=["bc", "c"],
            group_spans=[[1, 3], [2, 3]],
            span=[0, 5],
            named=True,
        )
        self.assert_match_case(
            cases_by_id[
                "quantified-nested-group-alternation-branch-local-named-backreference-pattern-fullmatch-no-match-str"
            ],
            helper="fullmatch",
            endpos=4,
            group0=None,
        )


if __name__ == "__main__":
    unittest.main()
