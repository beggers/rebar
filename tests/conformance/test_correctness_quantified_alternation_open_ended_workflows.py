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


class CorrectnessHarnessQuantifiedAlternationOpenEndedWorkflowTest(unittest.TestCase):
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
        self.assertEqual(case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(
            case["observations"]["cpython"]["result"],
            {
                "flags": 32,
                "groupindex": groupindex,
                "groups": 1,
                "pattern": pattern,
                "pattern_type": "str",
            },
        )
        self.assert_rebar_pass_or_unimplemented(
            case,
            expected_result={
                "flags": 32,
                "groupindex": groupindex,
                "groups": 1,
                "pattern": pattern,
                "pattern_type": "str",
            },
        )

    def assert_match_case(
        self,
        case: dict[str, object],
        *,
        helper: str,
        group0: str | None,
        group1: str | None = None,
        endpos: int,
        span: list[int] | None = None,
        span1: list[int] | None = None,
        named: bool = False,
    ) -> None:
        self.assertEqual(case["helper"], helper)
        self.assertEqual(case["observations"]["cpython"]["outcome"], "success")

        if group0 is None:
            self.assertIsNone(case["observations"]["cpython"]["result"])
            self.assert_rebar_pass_or_unimplemented(case, expected_result=None)
            return

        groupdict = {"word": group1} if named else {}
        cpython_result = {
            "endpos": endpos,
            "group0": group0,
            "group1": group1,
            "group_spans": [span1],
            "groupdict": groupdict,
            "groups": [group1],
            "lastgroup": "word" if named else None,
            "lastindex": 1,
            "matched": True,
            "pos": 0,
            "span": span,
            "span1": span1,
            "string_type": "str",
        }
        if named:
            cpython_result["named_group_spans"] = {"word": span1}
            cpython_result["named_groups"] = {"word": group1}

        self.assertEqual(case["observations"]["cpython"]["result"], cpython_result)
        self.assert_rebar_pass_or_unimplemented(case, expected_result=cpython_result)

    def test_runner_regenerates_combined_quantified_alternation_open_ended_scorecard(
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
            "quantified-alternation-open-ended-workflows",
            scorecard["fixtures"]["manifest_ids"],
        )
        self.assertEqual(scorecard["summary"], tracked_scorecard["summary"])
        self.assertEqual(len(scorecard["cases"]), len(tracked_scorecard["cases"]))

        match_layer = scorecard["layers"]["match_behavior"]
        self.assertIn(
            "quantified-alternation-open-ended-workflows",
            match_layer["manifest_ids"],
        )
        self.assertEqual(
            match_layer["summary"],
            tracked_scorecard["layers"]["match_behavior"]["summary"],
        )

        suite_ids = [suite["id"] for suite in scorecard["suites"]]
        self.assertIn("match.quantified_alternation_open_ended", suite_ids)
        self.assertIn("match.quantified_alternation_open_ended.str", suite_ids)
        self.assertIn("match.quantified_alternation_open_ended.compile", suite_ids)
        self.assertIn(
            "match.quantified_alternation_open_ended.module_call",
            suite_ids,
        )
        self.assertIn(
            "match.quantified_alternation_open_ended.pattern_call",
            suite_ids,
        )

        workflow_suite = next(
            suite
            for suite in scorecard["suites"]
            if suite["id"] == "match.quantified_alternation_open_ended"
        )
        self.assertEqual(workflow_suite["summary"]["total_cases"], 16)
        self.assertEqual(workflow_suite["summary"]["failed_cases"], 0)
        self.assertEqual(workflow_suite["summary"]["skipped_cases"], 0)
        self.assertEqual(
            workflow_suite["summary"]["passed_cases"]
            + workflow_suite["summary"]["unimplemented_cases"],
            16,
        )
        self.assertEqual(
            workflow_suite["families"],
            [
                "quantified_alternation_open_ended_named_compile_metadata",
                "quantified_alternation_open_ended_named_module_lower_bound_b_workflow",
                "quantified_alternation_open_ended_named_module_lower_bound_c_workflow",
                "quantified_alternation_open_ended_named_pattern_fourth_repetition_bcbc_workflow",
                "quantified_alternation_open_ended_named_pattern_no_match_below_lower_bound_workflow",
                "quantified_alternation_open_ended_named_pattern_no_match_invalid_branch_workflow",
                "quantified_alternation_open_ended_named_pattern_second_repetition_workflow",
                "quantified_alternation_open_ended_named_pattern_third_repetition_bcc_workflow",
                "quantified_alternation_open_ended_numbered_compile_metadata",
                "quantified_alternation_open_ended_numbered_module_lower_bound_b_workflow",
                "quantified_alternation_open_ended_numbered_module_lower_bound_c_workflow",
                "quantified_alternation_open_ended_numbered_pattern_fourth_repetition_bcbc_workflow",
                "quantified_alternation_open_ended_numbered_pattern_no_match_below_lower_bound_workflow",
                "quantified_alternation_open_ended_numbered_pattern_no_match_invalid_branch_workflow",
                "quantified_alternation_open_ended_numbered_pattern_second_repetition_workflow",
                "quantified_alternation_open_ended_numbered_pattern_third_repetition_bcc_workflow",
            ],
        )

        cases_by_id = {case["id"]: case for case in scorecard["cases"]}

        self.assert_compile_case(
            cases_by_id["quantified-alternation-open-ended-numbered-compile-metadata-str"],
            pattern="a(b|c){1,}d",
            groupindex={},
        )
        self.assert_match_case(
            cases_by_id[
                "quantified-alternation-open-ended-numbered-module-search-lower-bound-b-str"
            ],
            helper="search",
            group0="abd",
            group1="b",
            endpos=7,
            span=[2, 5],
            span1=[3, 4],
        )
        self.assert_match_case(
            cases_by_id[
                "quantified-alternation-open-ended-numbered-module-search-lower-bound-c-str"
            ],
            helper="search",
            group0="acd",
            group1="c",
            endpos=7,
            span=[2, 5],
            span1=[3, 4],
        )
        self.assert_match_case(
            cases_by_id[
                "quantified-alternation-open-ended-numbered-pattern-fullmatch-second-repetition-str"
            ],
            helper="fullmatch",
            group0="abcd",
            group1="c",
            endpos=4,
            span=[0, 4],
            span1=[2, 3],
        )
        self.assert_match_case(
            cases_by_id[
                "quantified-alternation-open-ended-numbered-pattern-fullmatch-third-repetition-bcc-str"
            ],
            helper="fullmatch",
            group0="abccd",
            group1="c",
            endpos=5,
            span=[0, 5],
            span1=[3, 4],
        )
        self.assert_match_case(
            cases_by_id[
                "quantified-alternation-open-ended-numbered-pattern-fullmatch-fourth-repetition-bcbc-str"
            ],
            helper="fullmatch",
            group0="abcbcd",
            group1="c",
            endpos=6,
            span=[0, 6],
            span1=[4, 5],
        )
        self.assert_match_case(
            cases_by_id[
                "quantified-alternation-open-ended-numbered-pattern-fullmatch-no-match-below-lower-bound-str"
            ],
            helper="fullmatch",
            group0=None,
            endpos=2,
        )
        self.assert_match_case(
            cases_by_id[
                "quantified-alternation-open-ended-numbered-pattern-fullmatch-no-match-invalid-branch-str"
            ],
            helper="fullmatch",
            group0=None,
            endpos=4,
        )

        self.assert_compile_case(
            cases_by_id["quantified-alternation-open-ended-named-compile-metadata-str"],
            pattern="a(?P<word>b|c){1,}d",
            groupindex={"word": 1},
        )
        self.assert_match_case(
            cases_by_id[
                "quantified-alternation-open-ended-named-module-search-lower-bound-b-str"
            ],
            helper="search",
            group0="abd",
            group1="b",
            endpos=7,
            span=[2, 5],
            span1=[3, 4],
            named=True,
        )
        self.assert_match_case(
            cases_by_id[
                "quantified-alternation-open-ended-named-module-search-lower-bound-c-str"
            ],
            helper="search",
            group0="acd",
            group1="c",
            endpos=7,
            span=[2, 5],
            span1=[3, 4],
            named=True,
        )
        self.assert_match_case(
            cases_by_id[
                "quantified-alternation-open-ended-named-pattern-fullmatch-second-repetition-str"
            ],
            helper="fullmatch",
            group0="abcd",
            group1="c",
            endpos=4,
            span=[0, 4],
            span1=[2, 3],
            named=True,
        )
        self.assert_match_case(
            cases_by_id[
                "quantified-alternation-open-ended-named-pattern-fullmatch-third-repetition-bcc-str"
            ],
            helper="fullmatch",
            group0="abccd",
            group1="c",
            endpos=5,
            span=[0, 5],
            span1=[3, 4],
            named=True,
        )
        self.assert_match_case(
            cases_by_id[
                "quantified-alternation-open-ended-named-pattern-fullmatch-fourth-repetition-bcbc-str"
            ],
            helper="fullmatch",
            group0="abcbcd",
            group1="c",
            endpos=6,
            span=[0, 6],
            span1=[4, 5],
            named=True,
        )
        self.assert_match_case(
            cases_by_id[
                "quantified-alternation-open-ended-named-pattern-fullmatch-no-match-below-lower-bound-str"
            ],
            helper="fullmatch",
            group0=None,
            endpos=2,
            named=True,
        )
        self.assert_match_case(
            cases_by_id[
                "quantified-alternation-open-ended-named-pattern-fullmatch-no-match-invalid-branch-str"
            ],
            helper="fullmatch",
            group0=None,
            endpos=4,
            named=True,
        )


if __name__ == "__main__":
    unittest.main()
