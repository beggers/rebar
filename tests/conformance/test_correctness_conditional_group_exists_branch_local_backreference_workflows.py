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


class CorrectnessHarnessConditionalGroupExistsBranchLocalBackreferenceWorkflowTest(unittest.TestCase):
    def test_runner_regenerates_combined_conditional_group_exists_branch_local_backreference_scorecard(
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
        tracked_scorecard = load_published_correctness_scorecard()

        self.assertEqual(
            scorecard["fixtures"]["manifest_count"],
            tracked_scorecard["fixtures"]["manifest_count"],
        )
        self.assertIn(
            "conditional-group-exists-branch-local-backreference-workflows",
            scorecard["fixtures"]["manifest_ids"],
        )
        self.assertEqual(scorecard["summary"], tracked_scorecard["summary"])
        self.assertEqual(len(scorecard["cases"]), len(tracked_scorecard["cases"]))

        match_layer = scorecard["layers"]["match_behavior"]
        self.assertIn(
            "conditional-group-exists-branch-local-backreference-workflows",
            match_layer["manifest_ids"],
        )
        self.assertEqual(
            match_layer["summary"],
            tracked_scorecard["layers"]["match_behavior"]["summary"],
        )

        suite_ids = [suite["id"] for suite in scorecard["suites"]]
        self.assertIn("match.conditional_group_exists_branch_local_backreference", suite_ids)
        self.assertIn("match.conditional_group_exists_branch_local_backreference.str", suite_ids)
        self.assertIn(
            "match.conditional_group_exists_branch_local_backreference.compile",
            suite_ids,
        )
        self.assertIn(
            "match.conditional_group_exists_branch_local_backreference.module_call",
            suite_ids,
        )
        self.assertIn(
            "match.conditional_group_exists_branch_local_backreference.pattern_call",
            suite_ids,
        )

        workflow_suite = next(
            suite
            for suite in scorecard["suites"]
            if suite["id"] == "match.conditional_group_exists_branch_local_backreference"
        )
        self.assertEqual(
            workflow_suite["summary"],
            {
                "executed_cases": 6,
                "failed_cases": 0,
                "passed_cases": 6,
                "skipped_cases": 0,
                "total_cases": 6,
                "unimplemented_cases": 0,
            },
        )
        self.assertEqual(
            workflow_suite["families"],
            [
                "conditional_group_exists_branch_local_named_backreference_compile_metadata",
                "conditional_group_exists_branch_local_named_backreference_module_present_workflow",
                "conditional_group_exists_branch_local_named_backreference_pattern_absent_workflow",
                "conditional_group_exists_branch_local_numbered_backreference_compile_metadata",
                "conditional_group_exists_branch_local_numbered_backreference_module_present_workflow",
                "conditional_group_exists_branch_local_numbered_backreference_pattern_absent_workflow",
            ],
        )

        cases_by_id = {case["id"]: case for case in scorecard["cases"]}

        numbered_compile_case = cases_by_id[
            "conditional-group-exists-branch-local-numbered-backreference-compile-metadata-str"
        ]
        self.assertEqual(numbered_compile_case["comparison"], "pass")
        self.assertEqual(numbered_compile_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(numbered_compile_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(numbered_compile_case["observations"]["cpython"]["result"]["groups"], 2)
        self.assertEqual(
            numbered_compile_case["observations"]["rebar"]["result"]["groupindex"],
            {},
        )

        numbered_present_case = cases_by_id[
            "conditional-group-exists-branch-local-numbered-backreference-module-search-present-str"
        ]
        self.assertEqual(numbered_present_case["comparison"], "pass")
        self.assertEqual(numbered_present_case["helper"], "search")
        self.assertEqual(numbered_present_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(numbered_present_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(numbered_present_case["observations"]["cpython"]["result"]["group0"], "abbd")
        self.assertEqual(numbered_present_case["observations"]["cpython"]["result"]["groups"], ["b", "b"])
        self.assertEqual(numbered_present_case["observations"]["cpython"]["result"]["lastindex"], 1)
        self.assertEqual(
            numbered_present_case["observations"]["rebar"]["result"]["span"],
            [2, 6],
        )

        numbered_absent_case = cases_by_id[
            "conditional-group-exists-branch-local-numbered-backreference-pattern-fullmatch-absent-str"
        ]
        self.assertEqual(numbered_absent_case["comparison"], "pass")
        self.assertEqual(numbered_absent_case["helper"], "fullmatch")
        self.assertEqual(numbered_absent_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(numbered_absent_case["observations"]["rebar"]["outcome"], "success")
        self.assertIsNone(numbered_absent_case["observations"]["cpython"]["result"])
        self.assertIsNone(numbered_absent_case["observations"]["rebar"]["result"])

        named_compile_case = cases_by_id[
            "conditional-group-exists-branch-local-named-backreference-compile-metadata-str"
        ]
        self.assertEqual(named_compile_case["comparison"], "pass")
        self.assertEqual(named_compile_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(named_compile_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(
            named_compile_case["observations"]["cpython"]["result"]["groupindex"],
            {"inner": 2, "outer": 1},
        )
        self.assertEqual(
            named_compile_case["observations"]["rebar"]["result"]["groupindex"],
            {"inner": 2, "outer": 1},
        )

        named_present_case = cases_by_id[
            "conditional-group-exists-branch-local-named-backreference-module-search-present-str"
        ]
        self.assertEqual(named_present_case["comparison"], "pass")
        self.assertEqual(named_present_case["helper"], "search")
        self.assertEqual(named_present_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(named_present_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(named_present_case["observations"]["cpython"]["result"]["group0"], "abbd")
        self.assertEqual(
            named_present_case["observations"]["cpython"]["result"]["named_groups"],
            {"inner": "b", "outer": "b"},
        )
        self.assertEqual(
            named_present_case["observations"]["rebar"]["result"]["lastgroup"],
            "outer",
        )

        named_absent_case = cases_by_id[
            "conditional-group-exists-branch-local-named-backreference-pattern-fullmatch-absent-str"
        ]
        self.assertEqual(named_absent_case["comparison"], "pass")
        self.assertEqual(named_absent_case["helper"], "fullmatch")
        self.assertEqual(named_absent_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(named_absent_case["observations"]["rebar"]["outcome"], "success")
        self.assertIsNone(named_absent_case["observations"]["cpython"]["result"])
        self.assertIsNone(named_absent_case["observations"]["rebar"]["result"])


if __name__ == "__main__":
    unittest.main()
