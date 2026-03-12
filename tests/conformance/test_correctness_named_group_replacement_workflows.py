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
PARSER_FIXTURES_PATH = REPO_ROOT / "tests" / "conformance" / "fixtures" / "parser_matrix.json"
PUBLIC_API_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "public_api_surface.json"
)
MATCH_BEHAVIOR_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "match_behavior_smoke.json"
)
EXPORTED_SYMBOL_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "exported_symbol_surface.json"
)
PATTERN_OBJECT_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "pattern_object_surface.json"
)
MODULE_WORKFLOW_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "module_workflow_surface.json"
)
COLLECTION_REPLACEMENT_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "collection_replacement_workflows.json"
)
LITERAL_FLAG_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "literal_flag_workflows.json"
)
GROUPED_MATCH_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "grouped_match_workflows.json"
)
NAMED_GROUP_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "named_group_workflows.json"
)
NAMED_GROUP_REPLACEMENT_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "named_group_replacement_workflows.json"
)
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.json"


class CorrectnessHarnessNamedGroupReplacementWorkflowTest(unittest.TestCase):
    def test_runner_regenerates_combined_named_group_replacement_scorecard(self) -> None:
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
                    "--fixtures",
                    str(PARSER_FIXTURES_PATH),
                    str(PUBLIC_API_FIXTURES_PATH),
                    str(MATCH_BEHAVIOR_FIXTURES_PATH),
                    str(EXPORTED_SYMBOL_FIXTURES_PATH),
                    str(PATTERN_OBJECT_FIXTURES_PATH),
                    str(MODULE_WORKFLOW_FIXTURES_PATH),
                    str(COLLECTION_REPLACEMENT_FIXTURES_PATH),
                    str(LITERAL_FLAG_FIXTURES_PATH),
                    str(GROUPED_MATCH_FIXTURES_PATH),
                    str(NAMED_GROUP_FIXTURES_PATH),
                    str(NAMED_GROUP_REPLACEMENT_FIXTURES_PATH),
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
            self.assertEqual(
                summary,
                {
                    "executed_cases": 93,
                    "failed_cases": 0,
                    "passed_cases": 93,
                    "skipped_cases": 0,
                    "total_cases": 93,
                    "unimplemented_cases": 0,
                },
            )

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
        self.assertEqual(scorecard["fixtures"]["manifest_count"], 11)
        self.assertEqual(
            scorecard["fixtures"]["manifest_ids"],
            [
                "parser-matrix",
                "public-api-surface",
                "match-behavior-smoke",
                "exported-symbol-surface",
                "pattern-object-surface",
                "module-workflow-surface",
                "collection-replacement-workflows",
                "literal-flag-workflows",
                "grouped-match-workflows",
                "named-group-workflows",
                "named-group-replacement-workflows",
            ],
        )
        self.assertEqual(len(scorecard["cases"]), 93)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        workflow_layer = scorecard["layers"]["module_workflow"]
        self.assertEqual(workflow_layer["summary"]["total_cases"], 40)
        self.assertEqual(workflow_layer["summary"]["passed_cases"], 40)
        self.assertEqual(workflow_layer["summary"]["failed_cases"], 0)
        self.assertEqual(workflow_layer["summary"]["unimplemented_cases"], 0)
        self.assertEqual(
            workflow_layer["manifest_ids"],
            [
                "collection-replacement-workflows",
                "literal-flag-workflows",
                "module-workflow-surface",
                "named-group-replacement-workflows",
            ],
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
        self.assertIn("collection.replacement.named_group", suite_ids)
        self.assertIn("collection.replacement.named_group.str", suite_ids)
        self.assertIn("collection.replacement.named_group.module_call", suite_ids)
        self.assertIn("collection.replacement.named_group.pattern_call", suite_ids)

        named_replacement_suite = next(
            suite for suite in scorecard["suites"] if suite["id"] == "collection.replacement.named_group"
        )
        self.assertEqual(named_replacement_suite["summary"]["total_cases"], 4)
        self.assertEqual(named_replacement_suite["summary"]["passed_cases"], 4)
        self.assertEqual(named_replacement_suite["summary"]["failed_cases"], 0)
        self.assertEqual(named_replacement_suite["summary"]["unimplemented_cases"], 0)
        self.assertEqual(
            named_replacement_suite["families"],
            ["named_group_replacement_workflow"],
        )

        module_sub_case = next(
            case for case in scorecard["cases"] if case["id"] == "module-sub-template-named-group-str"
        )
        self.assertEqual(module_sub_case["comparison"], "pass")
        self.assertEqual(module_sub_case["helper"], "sub")
        self.assertEqual(module_sub_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(module_sub_case["observations"]["cpython"]["result"], "<abc><abc>")
        self.assertEqual(module_sub_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(module_sub_case["observations"]["rebar"]["result"], "<abc><abc>")
        self.assertEqual(module_sub_case["comparison_notes"], [])

        module_subn_case = next(
            case for case in scorecard["cases"] if case["id"] == "module-subn-template-named-group-str"
        )
        self.assertEqual(module_subn_case["comparison"], "pass")
        self.assertEqual(module_subn_case["helper"], "subn")
        self.assertEqual(module_subn_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(module_subn_case["observations"]["cpython"]["result"], ["<abc>abc", 1])
        self.assertEqual(module_subn_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(module_subn_case["observations"]["rebar"]["result"], ["<abc>abc", 1])

        pattern_sub_case = next(
            case for case in scorecard["cases"] if case["id"] == "pattern-sub-template-named-group-str"
        )
        self.assertEqual(pattern_sub_case["comparison"], "pass")
        self.assertEqual(pattern_sub_case["helper"], "sub")
        self.assertEqual(pattern_sub_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(pattern_sub_case["observations"]["cpython"]["result"], "<abc><abc>")
        self.assertEqual(pattern_sub_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(pattern_sub_case["observations"]["rebar"]["result"], "<abc><abc>")

        pattern_subn_case = next(
            case for case in scorecard["cases"] if case["id"] == "pattern-subn-template-named-group-str"
        )
        self.assertEqual(pattern_subn_case["comparison"], "pass")
        self.assertEqual(pattern_subn_case["helper"], "subn")
        self.assertEqual(pattern_subn_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(pattern_subn_case["observations"]["cpython"]["result"], ["<abc>abc", 1])
        self.assertEqual(pattern_subn_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(pattern_subn_case["observations"]["rebar"]["result"], ["<abc>abc", 1])


if __name__ == "__main__":
    unittest.main()
