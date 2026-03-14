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
FIXTURE_PATH = (
    "tests/conformance/fixtures/quantified_nested_group_replacement_workflows.py"
)


class CorrectnessHarnessQuantifiedNestedGroupReplacementWorkflowTest(unittest.TestCase):
    def test_runner_regenerates_combined_quantified_nested_group_replacement_scorecard(
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
            "quantified-nested-group-replacement-workflows",
            scorecard["fixtures"]["manifest_ids"],
        )
        self.assertIn(
            "nested-group-replacement-workflows",
            scorecard["fixtures"]["manifest_ids"],
        )
        self.assertIn(FIXTURE_PATH, scorecard["fixtures"]["paths"])
        self.assertIn(FIXTURE_PATH, tracked_scorecard["fixtures"]["paths"])

        self.assertEqual(scorecard["summary"], tracked_scorecard["summary"])
        self.assertEqual(len(scorecard["cases"]), len(tracked_scorecard["cases"]))

        workflow_layer = scorecard["layers"]["module_workflow"]
        self.assertEqual(
            workflow_layer["summary"],
            tracked_scorecard["layers"]["module_workflow"]["summary"],
        )
        self.assertIn(
            "quantified-nested-group-replacement-workflows",
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
        self.assertIn("collection.replacement.quantified_nested_group", suite_ids)
        self.assertIn("collection.replacement.quantified_nested_group.str", suite_ids)
        self.assertIn(
            "collection.replacement.quantified_nested_group.module_call",
            suite_ids,
        )
        self.assertIn(
            "collection.replacement.quantified_nested_group.pattern_call",
            suite_ids,
        )

        quantified_replacement_suite = next(
            suite
            for suite in scorecard["suites"]
            if suite["id"] == "collection.replacement.quantified_nested_group"
        )
        self.assertEqual(
            quantified_replacement_suite["summary"],
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
            quantified_replacement_suite["families"],
            [
                "named_quantified_nested_group_inner_template_count_workflow",
                "named_quantified_nested_group_outer_template_workflow",
                "quantified_nested_group_numbered_inner_template_count_workflow",
                "quantified_nested_group_numbered_outer_template_workflow",
            ],
        )

        cases_by_id = {case["id"]: case for case in scorecard["cases"]}

        module_lower_bound_case = cases_by_id[
            "module-sub-template-quantified-nested-group-numbered-lower-bound-str"
        ]
        self.assertEqual(module_lower_bound_case["comparison"], "pass")
        self.assertEqual(module_lower_bound_case["helper"], "sub")
        self.assertEqual(
            module_lower_bound_case["args"],
            [r"a((bc)+)d", r"\1x", "zzabcdzz"],
        )
        self.assertEqual(
            module_lower_bound_case["observations"]["cpython"]["outcome"],
            "success",
        )
        self.assertEqual(
            module_lower_bound_case["observations"]["cpython"]["result"],
            "zzbcxzz",
        )
        self.assertEqual(
            module_lower_bound_case["observations"]["rebar"]["outcome"],
            "success",
        )
        self.assertEqual(
            module_lower_bound_case["observations"]["rebar"]["result"],
            "zzbcxzz",
        )
        self.assertIsNone(module_lower_bound_case["observations"]["rebar"]["exception"])

        module_first_match_only_case = cases_by_id[
            "module-subn-template-quantified-nested-group-numbered-first-match-only-str"
        ]
        self.assertEqual(module_first_match_only_case["comparison"], "pass")
        self.assertEqual(module_first_match_only_case["helper"], "subn")
        self.assertEqual(
            module_first_match_only_case["args"],
            [r"a((bc)+)d", r"\2x", "zzabcbcdabcbcdzz", 1],
        )
        self.assertEqual(
            module_first_match_only_case["observations"]["cpython"]["outcome"],
            "success",
        )
        self.assertEqual(
            module_first_match_only_case["observations"]["cpython"]["result"],
            ["zzbcxabcbcdzz", 1],
        )
        self.assertEqual(
            module_first_match_only_case["observations"]["rebar"]["outcome"],
            "success",
        )
        self.assertEqual(
            module_first_match_only_case["observations"]["rebar"]["result"],
            ["zzbcxabcbcdzz", 1],
        )
        self.assertIsNone(module_first_match_only_case["observations"]["rebar"]["exception"])

        named_pattern_repeated_case = cases_by_id[
            "pattern-sub-template-quantified-nested-group-named-repeated-outer-capture-str"
        ]
        self.assertEqual(named_pattern_repeated_case["comparison"], "pass")
        self.assertEqual(named_pattern_repeated_case["helper"], "sub")
        self.assertEqual(
            named_pattern_repeated_case["args"],
            [r"\g<outer>x", "zzabcbcdzz"],
        )
        self.assertEqual(
            named_pattern_repeated_case["observations"]["cpython"]["outcome"],
            "success",
        )
        self.assertEqual(
            named_pattern_repeated_case["observations"]["cpython"]["result"],
            "zzbcbcxzz",
        )
        self.assertEqual(
            named_pattern_repeated_case["observations"]["rebar"]["outcome"],
            "success",
        )
        self.assertEqual(
            named_pattern_repeated_case["observations"]["rebar"]["result"],
            "zzbcbcxzz",
        )
        self.assertIsNone(named_pattern_repeated_case["observations"]["rebar"]["exception"])

        named_pattern_first_match_only_case = cases_by_id[
            "pattern-subn-template-quantified-nested-group-named-first-match-only-str"
        ]
        self.assertEqual(
            named_pattern_first_match_only_case["comparison"],
            "pass",
        )
        self.assertEqual(named_pattern_first_match_only_case["helper"], "subn")
        self.assertEqual(
            named_pattern_first_match_only_case["args"],
            [r"\g<inner>x", "zzabcbcdabcbcdzz", 1],
        )
        self.assertEqual(
            named_pattern_first_match_only_case["observations"]["cpython"]["outcome"],
            "success",
        )
        self.assertEqual(
            named_pattern_first_match_only_case["observations"]["cpython"]["result"],
            ["zzbcxabcbcdzz", 1],
        )
        self.assertEqual(
            named_pattern_first_match_only_case["observations"]["rebar"]["outcome"],
            "success",
        )
        self.assertEqual(
            named_pattern_first_match_only_case["observations"]["rebar"]["result"],
            ["zzbcxabcbcdzz", 1],
        )
        self.assertIsNone(
            named_pattern_first_match_only_case["observations"]["rebar"]["exception"]
        )


if __name__ == "__main__":
    unittest.main()
