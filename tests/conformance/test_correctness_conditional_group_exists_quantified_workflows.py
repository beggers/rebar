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


class CorrectnessHarnessConditionalGroupExistsQuantifiedWorkflowTest(unittest.TestCase):
    def test_runner_regenerates_combined_conditional_group_exists_quantified_scorecard(
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
        self.assertEqual(scorecard["baseline"]["python_implementation"], platform.python_implementation())
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

        self.assertEqual(scorecard["fixtures"]["manifest_count"], 43)
        self.assertIn(
            "conditional-group-exists-quantified-workflows",
            scorecard["fixtures"]["manifest_ids"],
        )
        self.assertIn(
            "conditional-group-exists-no-else-nested-workflows",
            scorecard["fixtures"]["manifest_ids"],
        )

        self.assertEqual(
            scorecard["summary"],
            {
                "executed_cases": 296,
                "failed_cases": 0,
                "passed_cases": 296,
                "skipped_cases": 0,
                "total_cases": 296,
                "unimplemented_cases": 0,
            },
        )
        self.assertEqual(len(scorecard["cases"]), 296)

        match_layer = scorecard["layers"]["match_behavior"]
        self.assertEqual(
            match_layer["summary"],
            {
                "executed_cases": 152,
                "failed_cases": 0,
                "passed_cases": 152,
                "skipped_cases": 0,
                "total_cases": 152,
                "unimplemented_cases": 0,
            },
        )
        self.assertIn(
            "conditional-group-exists-quantified-workflows",
            match_layer["manifest_ids"],
        )
        self.assertEqual(match_layer["operations"], ["compile", "module_call", "pattern_call"])
        self.assertEqual(match_layer["text_models"], ["bytes", "str"])

        suite_ids = [suite["id"] for suite in scorecard["suites"]]
        self.assertIn("match.conditional_group_exists_quantified", suite_ids)
        self.assertIn("match.conditional_group_exists_quantified.str", suite_ids)
        self.assertIn("match.conditional_group_exists_quantified.compile", suite_ids)
        self.assertIn("match.conditional_group_exists_quantified.module_call", suite_ids)
        self.assertIn("match.conditional_group_exists_quantified.pattern_call", suite_ids)

        quantified_suite = next(
            suite
            for suite in scorecard["suites"]
            if suite["id"] == "match.conditional_group_exists_quantified"
        )
        self.assertEqual(
            quantified_suite["summary"],
            {
                "executed_cases": 8,
                "failed_cases": 0,
                "passed_cases": 8,
                "skipped_cases": 0,
                "total_cases": 8,
                "unimplemented_cases": 0,
            },
        )
        self.assertEqual(
            quantified_suite["families"],
            [
                "conditional_group_exists_quantified_compile_metadata",
                "conditional_group_exists_quantified_module_absent_workflow",
                "conditional_group_exists_quantified_module_present_workflow",
                "conditional_group_exists_quantified_pattern_missing_repeat_workflow",
                "named_conditional_group_exists_quantified_compile_metadata",
                "named_conditional_group_exists_quantified_module_absent_workflow",
                "named_conditional_group_exists_quantified_module_present_workflow",
                "named_conditional_group_exists_quantified_pattern_missing_repeat_workflow",
            ],
        )

        cases_by_id = {case["id"]: case for case in scorecard["cases"]}

        compile_case = cases_by_id["conditional-group-exists-quantified-compile-metadata-str"]
        self.assertEqual(compile_case["comparison"], "pass")
        self.assertEqual(compile_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(compile_case["observations"]["cpython"]["result"]["groupindex"], {})
        self.assertEqual(compile_case["observations"]["cpython"]["result"]["groups"], 1)
        self.assertEqual(compile_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(
            compile_case["observations"]["rebar"]["result"],
            compile_case["observations"]["cpython"]["result"],
        )

        present_case = cases_by_id[
            "conditional-group-exists-quantified-module-search-present-str"
        ]
        self.assertEqual(present_case["comparison"], "pass")
        self.assertEqual(present_case["helper"], "search")
        self.assertEqual(present_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(present_case["observations"]["cpython"]["result"]["group0"], "abcdd")
        self.assertEqual(present_case["observations"]["cpython"]["result"]["groups"], ["b"])
        self.assertEqual(present_case["observations"]["cpython"]["result"]["lastindex"], 1)
        self.assertEqual(present_case["observations"]["cpython"]["result"]["span1"], [3, 4])
        self.assertEqual(
            present_case["observations"]["rebar"]["outcome"],
            "success",
        )
        self.assertEqual(
            present_case["observations"]["rebar"]["result"],
            present_case["observations"]["cpython"]["result"],
        )

        absent_case = cases_by_id[
            "conditional-group-exists-quantified-module-fullmatch-absent-str"
        ]
        self.assertEqual(absent_case["comparison"], "pass")
        self.assertEqual(absent_case["helper"], "fullmatch")
        self.assertEqual(absent_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(absent_case["observations"]["cpython"]["result"]["group0"], "acee")
        self.assertEqual(absent_case["observations"]["cpython"]["result"]["groups"], [None])
        self.assertEqual(absent_case["observations"]["cpython"]["result"]["lastindex"], None)
        self.assertEqual(absent_case["observations"]["cpython"]["result"]["span1"], [-1, -1])
        self.assertEqual(
            absent_case["observations"]["rebar"]["outcome"],
            "success",
        )
        self.assertEqual(
            absent_case["observations"]["rebar"]["result"],
            absent_case["observations"]["cpython"]["result"],
        )

        missing_repeat_case = cases_by_id[
            "conditional-group-exists-quantified-pattern-fullmatch-missing-repeat-str"
        ]
        self.assertEqual(missing_repeat_case["comparison"], "pass")
        self.assertEqual(missing_repeat_case["helper"], "fullmatch")
        self.assertEqual(missing_repeat_case["observations"]["cpython"]["outcome"], "success")
        self.assertIsNone(missing_repeat_case["observations"]["cpython"]["result"])
        self.assertEqual(
            missing_repeat_case["observations"]["rebar"]["outcome"],
            "success",
        )
        self.assertIsNone(missing_repeat_case["observations"]["rebar"]["result"])

        named_compile_case = cases_by_id[
            "named-conditional-group-exists-quantified-compile-metadata-str"
        ]
        self.assertEqual(named_compile_case["comparison"], "pass")
        self.assertEqual(named_compile_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(
            named_compile_case["observations"]["cpython"]["result"]["groupindex"],
            {"word": 1},
        )
        self.assertEqual(named_compile_case["observations"]["cpython"]["result"]["groups"], 1)
        self.assertEqual(
            named_compile_case["observations"]["rebar"]["outcome"],
            "success",
        )
        self.assertEqual(
            named_compile_case["observations"]["rebar"]["result"],
            named_compile_case["observations"]["cpython"]["result"],
        )

        named_present_case = cases_by_id[
            "named-conditional-group-exists-quantified-module-search-present-str"
        ]
        self.assertEqual(named_present_case["comparison"], "pass")
        self.assertEqual(named_present_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(named_present_case["observations"]["cpython"]["result"]["group0"], "abcdd")
        self.assertEqual(named_present_case["observations"]["cpython"]["result"]["groups"], ["b"])
        self.assertEqual(
            named_present_case["observations"]["cpython"]["result"]["groupdict"],
            {"word": "b"},
        )
        self.assertEqual(
            named_present_case["observations"]["cpython"]["result"]["named_group_spans"],
            {"word": [3, 4]},
        )
        self.assertEqual(
            named_present_case["observations"]["rebar"]["outcome"],
            "success",
        )
        self.assertEqual(
            named_present_case["observations"]["rebar"]["result"],
            named_present_case["observations"]["cpython"]["result"],
        )

        named_absent_case = cases_by_id[
            "named-conditional-group-exists-quantified-module-fullmatch-absent-str"
        ]
        self.assertEqual(named_absent_case["comparison"], "pass")
        self.assertEqual(named_absent_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(named_absent_case["observations"]["cpython"]["result"]["group0"], "acee")
        self.assertEqual(named_absent_case["observations"]["cpython"]["result"]["groups"], [None])
        self.assertEqual(
            named_absent_case["observations"]["cpython"]["result"]["groupdict"],
            {"word": None},
        )
        self.assertEqual(
            named_absent_case["observations"]["cpython"]["result"]["named_group_spans"],
            {"word": [-1, -1]},
        )
        self.assertEqual(
            named_absent_case["observations"]["rebar"]["outcome"],
            "success",
        )
        self.assertEqual(
            named_absent_case["observations"]["rebar"]["result"],
            named_absent_case["observations"]["cpython"]["result"],
        )

        named_missing_repeat_case = cases_by_id[
            "named-conditional-group-exists-quantified-pattern-fullmatch-missing-repeat-str"
        ]
        self.assertEqual(named_missing_repeat_case["comparison"], "pass")
        self.assertEqual(named_missing_repeat_case["observations"]["cpython"]["outcome"], "success")
        self.assertIsNone(named_missing_repeat_case["observations"]["cpython"]["result"])
        self.assertEqual(
            named_missing_repeat_case["observations"]["rebar"]["outcome"],
            "success",
        )
        self.assertIsNone(named_missing_repeat_case["observations"]["rebar"]["result"])


if __name__ == "__main__":
    unittest.main()
