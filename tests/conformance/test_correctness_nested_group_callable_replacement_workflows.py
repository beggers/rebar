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
NAMED_BACKREFERENCE_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "named_backreference_workflows.json"
)
NUMBERED_BACKREFERENCE_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "numbered_backreference_workflows.json"
)
GROUPED_SEGMENT_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "grouped_segment_workflows.json"
)
NESTED_GROUP_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "nested_group_workflows.json"
)
NESTED_GROUP_REPLACEMENT_FIXTURES_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "nested_group_replacement_workflows.json"
)
NESTED_GROUP_CALLABLE_REPLACEMENT_FIXTURES_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "nested_group_callable_replacement_workflows.json"
)
LITERAL_ALTERNATION_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "literal_alternation_workflows.json"
)
GROUPED_ALTERNATION_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "grouped_alternation_workflows.json"
)
GROUPED_ALTERNATION_REPLACEMENT_FIXTURES_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "grouped_alternation_replacement_workflows.json"
)
GROUPED_ALTERNATION_CALLABLE_REPLACEMENT_FIXTURES_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "grouped_alternation_callable_replacement_workflows.json"
)
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.json"


class CorrectnessHarnessNestedGroupCallableReplacementWorkflowTest(unittest.TestCase):
    def test_runner_regenerates_combined_nested_group_callable_replacement_scorecard(
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
                    str(NAMED_BACKREFERENCE_FIXTURES_PATH),
                    str(NUMBERED_BACKREFERENCE_FIXTURES_PATH),
                    str(GROUPED_SEGMENT_FIXTURES_PATH),
                    str(NESTED_GROUP_FIXTURES_PATH),
                    str(NESTED_GROUP_REPLACEMENT_FIXTURES_PATH),
                    str(NESTED_GROUP_CALLABLE_REPLACEMENT_FIXTURES_PATH),
                    str(LITERAL_ALTERNATION_FIXTURES_PATH),
                    str(GROUPED_ALTERNATION_FIXTURES_PATH),
                    str(GROUPED_ALTERNATION_REPLACEMENT_FIXTURES_PATH),
                    str(GROUPED_ALTERNATION_CALLABLE_REPLACEMENT_FIXTURES_PATH),
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
                    "executed_cases": 152,
                    "failed_cases": 0,
                    "passed_cases": 152,
                    "skipped_cases": 0,
                    "total_cases": 152,
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
        self.assertEqual(scorecard["fixtures"]["manifest_count"], 21)
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
                "named-backreference-workflows",
                "numbered-backreference-workflows",
                "grouped-segment-workflows",
                "nested-group-workflows",
                "nested-group-replacement-workflows",
                "nested-group-callable-replacement-workflows",
                "literal-alternation-workflows",
                "grouped-alternation-workflows",
                "grouped-alternation-replacement-workflows",
                "grouped-alternation-callable-replacement-workflows",
            ],
        )
        self.assertEqual(len(scorecard["cases"]), 152)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        workflow_layer = scorecard["layers"]["module_workflow"]
        self.assertEqual(workflow_layer["summary"]["total_cases"], 72)
        self.assertEqual(workflow_layer["summary"]["passed_cases"], 72)
        self.assertEqual(workflow_layer["summary"]["failed_cases"], 0)
        self.assertEqual(workflow_layer["summary"]["unimplemented_cases"], 0)
        self.assertEqual(
            workflow_layer["manifest_ids"],
            [
                "collection-replacement-workflows",
                "grouped-alternation-callable-replacement-workflows",
                "grouped-alternation-replacement-workflows",
                "literal-flag-workflows",
                "module-workflow-surface",
                "named-group-replacement-workflows",
                "nested-group-callable-replacement-workflows",
                "nested-group-replacement-workflows",
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
        self.assertIn("collection.replacement.nested_group.callable", suite_ids)
        self.assertIn("collection.replacement.nested_group.callable.str", suite_ids)
        self.assertIn("collection.replacement.nested_group.callable.module_call", suite_ids)
        self.assertIn("collection.replacement.nested_group.callable.pattern_call", suite_ids)

        callable_suite = next(
            suite
            for suite in scorecard["suites"]
            if suite["id"] == "collection.replacement.nested_group.callable"
        )
        self.assertEqual(callable_suite["summary"]["total_cases"], 8)
        self.assertEqual(callable_suite["summary"]["passed_cases"], 8)
        self.assertEqual(callable_suite["summary"]["failed_cases"], 0)
        self.assertEqual(callable_suite["summary"]["unimplemented_cases"], 0)
        self.assertEqual(
            callable_suite["families"],
            [
                "named_nested_group_callable_replacement_workflow",
                "nested_group_callable_replacement_workflow",
            ],
        )

        module_case = next(
            case
            for case in scorecard["cases"]
            if case["id"] == "module-sub-callable-nested-group-numbered-str"
        )
        self.assertEqual(module_case["comparison"], "pass")
        self.assertEqual(module_case["helper"], "sub")
        self.assertEqual(module_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(module_case["observations"]["cpython"]["result"], "bxbx")
        self.assertEqual(module_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(module_case["observations"]["rebar"]["result"], "bxbx")

        module_subn_case = next(
            case
            for case in scorecard["cases"]
            if case["id"] == "module-subn-callable-nested-group-numbered-str"
        )
        self.assertEqual(module_subn_case["comparison"], "pass")
        self.assertEqual(module_subn_case["helper"], "subn")
        self.assertEqual(module_subn_case["observations"]["cpython"]["result"], ["bxabd", 1])
        self.assertEqual(module_subn_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(module_subn_case["observations"]["rebar"]["result"], ["bxabd", 1])

        named_pattern_case = next(
            case
            for case in scorecard["cases"]
            if case["id"] == "pattern-sub-callable-nested-group-named-str"
        )
        self.assertEqual(named_pattern_case["comparison"], "pass")
        self.assertEqual(named_pattern_case["helper"], "sub")
        self.assertEqual(named_pattern_case["observations"]["cpython"]["result"], "bxbx")
        self.assertEqual(named_pattern_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(named_pattern_case["observations"]["rebar"]["result"], "bxbx")
        self.assertEqual(named_pattern_case["args"][0]["type"], "callable")
        self.assertEqual(named_pattern_case["args"][0]["qualname"], "callable_match_group")


if __name__ == "__main__":
    unittest.main()
