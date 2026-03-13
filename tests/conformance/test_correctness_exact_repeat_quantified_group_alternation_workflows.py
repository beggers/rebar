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


class CorrectnessHarnessExactRepeatQuantifiedGroupAlternationWorkflowTest(
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

    def test_runner_regenerates_combined_exact_repeat_quantified_group_alternation_scorecard(
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
            "exact-repeat-quantified-group-alternation-workflows",
            scorecard["fixtures"]["manifest_ids"],
        )
        self.assertEqual(scorecard["summary"], tracked_scorecard["summary"])
        self.assertEqual(len(scorecard["cases"]), len(tracked_scorecard["cases"]))

        match_layer = scorecard["layers"]["match_behavior"]
        self.assertIn(
            "exact-repeat-quantified-group-alternation-workflows",
            match_layer["manifest_ids"],
        )
        self.assertEqual(
            match_layer["summary"],
            tracked_scorecard["layers"]["match_behavior"]["summary"],
        )

        suite_ids = [suite["id"] for suite in scorecard["suites"]]
        self.assertIn("match.exact_repeat_quantified_group_alternation", suite_ids)
        self.assertIn("match.exact_repeat_quantified_group_alternation.str", suite_ids)
        self.assertIn("match.exact_repeat_quantified_group_alternation.compile", suite_ids)
        self.assertIn(
            "match.exact_repeat_quantified_group_alternation.module_call",
            suite_ids,
        )
        self.assertIn(
            "match.exact_repeat_quantified_group_alternation.pattern_call",
            suite_ids,
        )

        workflow_suite = next(
            suite
            for suite in scorecard["suites"]
            if suite["id"] == "match.exact_repeat_quantified_group_alternation"
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
                "exact_repeat_quantified_group_alternation_named_compile_metadata",
                "exact_repeat_quantified_group_alternation_named_module_bc_bc_workflow",
                "exact_repeat_quantified_group_alternation_named_module_bc_de_workflow",
                "exact_repeat_quantified_group_alternation_named_pattern_de_de_workflow",
                "exact_repeat_quantified_group_alternation_named_pattern_no_match_extra_repetition_workflow",
                "exact_repeat_quantified_group_alternation_numbered_compile_metadata",
                "exact_repeat_quantified_group_alternation_numbered_module_bc_bc_workflow",
                "exact_repeat_quantified_group_alternation_numbered_module_bc_de_workflow",
                "exact_repeat_quantified_group_alternation_numbered_pattern_de_de_workflow",
                "exact_repeat_quantified_group_alternation_numbered_pattern_no_match_short_workflow",
            ],
        )

        cases_by_id = {case["id"]: case for case in scorecard["cases"]}

        self.assert_compile_case(
            cases_by_id[
                "exact-repeat-quantified-group-alternation-numbered-compile-metadata-str"
            ],
            pattern="a(bc|de){2}d",
            groupindex={},
        )
        self.assert_match_case(
            cases_by_id[
                "exact-repeat-quantified-group-alternation-numbered-module-search-bc-bc-str"
            ],
            helper="search",
            group0="abcbcd",
            group1="bc",
            endpos=10,
            span=[2, 8],
            span1=[5, 7],
        )
        self.assert_match_case(
            cases_by_id[
                "exact-repeat-quantified-group-alternation-numbered-module-search-bc-de-str"
            ],
            helper="search",
            group0="abcded",
            group1="de",
            endpos=10,
            span=[2, 8],
            span1=[5, 7],
        )
        self.assert_match_case(
            cases_by_id[
                "exact-repeat-quantified-group-alternation-numbered-pattern-fullmatch-de-de-str"
            ],
            helper="fullmatch",
            group0="adeded",
            group1="de",
            endpos=6,
            span=[0, 6],
            span1=[3, 5],
        )
        self.assert_match_case(
            cases_by_id[
                "exact-repeat-quantified-group-alternation-numbered-pattern-fullmatch-no-match-short-str"
            ],
            helper="fullmatch",
            group0=None,
            endpos=4,
        )
        self.assert_compile_case(
            cases_by_id["exact-repeat-quantified-group-alternation-named-compile-metadata-str"],
            pattern="a(?P<word>bc|de){2}d",
            groupindex={"word": 1},
        )
        self.assert_match_case(
            cases_by_id[
                "exact-repeat-quantified-group-alternation-named-module-search-bc-bc-str"
            ],
            helper="search",
            group0="abcbcd",
            group1="bc",
            endpos=10,
            span=[2, 8],
            span1=[5, 7],
            named=True,
        )
        self.assert_match_case(
            cases_by_id[
                "exact-repeat-quantified-group-alternation-named-module-search-bc-de-str"
            ],
            helper="search",
            group0="abcded",
            group1="de",
            endpos=10,
            span=[2, 8],
            span1=[5, 7],
            named=True,
        )
        self.assert_match_case(
            cases_by_id[
                "exact-repeat-quantified-group-alternation-named-pattern-fullmatch-de-de-str"
            ],
            helper="fullmatch",
            group0="adeded",
            group1="de",
            endpos=6,
            span=[0, 6],
            span1=[3, 5],
            named=True,
        )
        self.assert_match_case(
            cases_by_id[
                "exact-repeat-quantified-group-alternation-named-pattern-fullmatch-no-match-extra-repetition-str"
            ],
            helper="fullmatch",
            group0=None,
            endpos=8,
            named=True,
        )


if __name__ == "__main__":
    unittest.main()
