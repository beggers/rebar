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


class CorrectnessHarnessConditionalGroupExistsReplacementWorkflowTest(unittest.TestCase):
    def test_runner_regenerates_combined_conditional_group_exists_replacement_scorecard(
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

        self.assertEqual(scorecard["fixtures"]["manifest_count"], 58)
        self.assertIn(
            "conditional-group-exists-replacement-workflows",
            scorecard["fixtures"]["manifest_ids"],
        )
        self.assertIn(
            "conditional-group-exists-no-else-replacement-workflows",
            scorecard["fixtures"]["manifest_ids"],
        )
        self.assertIn(
            "conditional-group-exists-empty-else-replacement-workflows",
            scorecard["fixtures"]["manifest_ids"],
        )
        self.assertIn(
            "conditional-group-exists-empty-yes-else-replacement-workflows",
            scorecard["fixtures"]["manifest_ids"],
        )
        self.assertIn(
            "conditional-group-exists-fully-empty-replacement-workflows",
            scorecard["fixtures"]["manifest_ids"],
        )

        self.assertEqual(
            scorecard["summary"],
            {
                "executed_cases": 432,
                "failed_cases": 0,
                "passed_cases": 432,
                "skipped_cases": 0,
                "total_cases": 432,
                "unimplemented_cases": 0,
            },
        )
        self.assertEqual(len(scorecard["cases"]), 432)

        workflow_layer = scorecard["layers"]["module_workflow"]
        self.assertEqual(
            workflow_layer["summary"],
            {
                "executed_cases": 120,
                "failed_cases": 0,
                "passed_cases": 120,
                "skipped_cases": 0,
                "total_cases": 120,
                "unimplemented_cases": 0,
            },
        )
        self.assertIn(
            "conditional-group-exists-replacement-workflows",
            workflow_layer["manifest_ids"],
        )
        self.assertEqual(
            workflow_layer["operations"],
            [
                "cache_distinct_workflow",
                "cache_workflow",
                "compile",
                "module_call",
                "pattern_call",
                "purge_workflow",
            ],
        )
        self.assertEqual(workflow_layer["text_models"], ["bytes", "str"])

        suite_ids = [suite["id"] for suite in scorecard["suites"]]
        self.assertIn("collection.replacement.conditional_group_exists", suite_ids)
        self.assertIn("collection.replacement.conditional_group_exists.str", suite_ids)
        self.assertIn("collection.replacement.conditional_group_exists.module_call", suite_ids)
        self.assertIn("collection.replacement.conditional_group_exists.pattern_call", suite_ids)

        replacement_suite = next(
            suite
            for suite in scorecard["suites"]
            if suite["id"] == "collection.replacement.conditional_group_exists"
        )
        self.assertEqual(
            replacement_suite["summary"],
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
            replacement_suite["families"],
            [
                "conditional_group_exists_replacement_absent_count_workflow",
                "conditional_group_exists_replacement_present_workflow",
                "named_conditional_group_exists_replacement_absent_count_workflow",
                "named_conditional_group_exists_replacement_present_workflow",
            ],
        )

        cases_by_id = {case["id"]: case for case in scorecard["cases"]}

        module_present_case = cases_by_id[
            "module-sub-conditional-group-exists-replacement-present-str"
        ]
        self.assertEqual(module_present_case["comparison"], "pass")
        self.assertEqual(module_present_case["helper"], "sub")
        self.assertEqual(module_present_case["args"], ["a(b)?c(?(1)d|e)", "X", "zzabcdzz"])
        self.assertEqual(module_present_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(module_present_case["observations"]["cpython"]["result"], "zzXzz")
        self.assertEqual(module_present_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(module_present_case["observations"]["rebar"]["result"], "zzXzz")
        self.assertIsNone(module_present_case["observations"]["rebar"]["exception"])

        module_absent_case = cases_by_id[
            "module-subn-conditional-group-exists-replacement-absent-str"
        ]
        self.assertEqual(module_absent_case["comparison"], "pass")
        self.assertEqual(module_absent_case["helper"], "subn")
        self.assertEqual(module_absent_case["args"], ["a(b)?c(?(1)d|e)", "X", "zzacezz", 1])
        self.assertEqual(module_absent_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(module_absent_case["observations"]["cpython"]["result"], ["zzXzz", 1])
        self.assertEqual(module_absent_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(module_absent_case["observations"]["rebar"]["result"], ["zzXzz", 1])
        self.assertIsNone(module_absent_case["observations"]["rebar"]["exception"])

        pattern_present_case = cases_by_id[
            "pattern-sub-conditional-group-exists-replacement-present-str"
        ]
        self.assertEqual(pattern_present_case["comparison"], "pass")
        self.assertEqual(pattern_present_case["helper"], "sub")
        self.assertEqual(pattern_present_case["args"], ["X", "zzabcdzz"])
        self.assertEqual(pattern_present_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(pattern_present_case["observations"]["cpython"]["result"], "zzXzz")
        self.assertEqual(pattern_present_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(pattern_present_case["observations"]["rebar"]["result"], "zzXzz")
        self.assertIsNone(pattern_present_case["observations"]["rebar"]["exception"])

        named_pattern_absent_case = cases_by_id[
            "pattern-subn-named-conditional-group-exists-replacement-absent-str"
        ]
        self.assertEqual(named_pattern_absent_case["comparison"], "pass")
        self.assertEqual(named_pattern_absent_case["helper"], "subn")
        self.assertEqual(named_pattern_absent_case["args"], ["X", "zzacezz", 1])
        self.assertEqual(named_pattern_absent_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(
            named_pattern_absent_case["observations"]["cpython"]["result"],
            ["zzXzz", 1],
        )
        self.assertEqual(named_pattern_absent_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(
            named_pattern_absent_case["observations"]["rebar"]["result"],
            ["zzXzz", 1],
        )
        self.assertIsNone(named_pattern_absent_case["observations"]["rebar"]["exception"])


if __name__ == "__main__":
    unittest.main()
