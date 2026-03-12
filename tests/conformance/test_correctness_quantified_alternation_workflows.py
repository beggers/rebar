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
NESTED_GROUP_ALTERNATION_FIXTURES_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "nested_group_alternation_workflows.json"
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
BRANCH_LOCAL_BACKREFERENCE_FIXTURES_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "branch_local_backreference_workflows.json"
)
OPTIONAL_GROUP_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "optional_group_workflows.json"
)
EXACT_REPEAT_QUANTIFIED_GROUP_FIXTURES_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "exact_repeat_quantified_group_workflows.json"
)
RANGED_REPEAT_QUANTIFIED_GROUP_FIXTURES_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "ranged_repeat_quantified_group_workflows.json"
)
WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_FIXTURES_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "wider_ranged_repeat_quantified_group_workflows.json"
)
OPTIONAL_GROUP_ALTERNATION_FIXTURES_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "optional_group_alternation_workflows.json"
)
CONDITIONAL_GROUP_EXISTS_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "conditional_group_exists_workflows.json"
)
CONDITIONAL_GROUP_EXISTS_NO_ELSE_FIXTURES_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_no_else_workflows.json"
)
CONDITIONAL_GROUP_EXISTS_EMPTY_ELSE_FIXTURES_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_empty_else_workflows.json"
)
CONDITIONAL_GROUP_EXISTS_EMPTY_YES_ELSE_FIXTURES_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_empty_yes_else_workflows.json"
)
CONDITIONAL_GROUP_EXISTS_FULLY_EMPTY_FIXTURES_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_fully_empty_workflows.json"
)
CONDITIONAL_GROUP_EXISTS_ASSERTION_DIAGNOSTICS_FIXTURES_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_assertion_diagnostics.json"
)
QUANTIFIED_ALTERNATION_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "quantified_alternation_workflows.json"
)
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.json"


class CorrectnessHarnessQuantifiedAlternationWorkflowTest(unittest.TestCase):
    def test_runner_regenerates_combined_quantified_alternation_scorecard(self) -> None:
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
                    str(NESTED_GROUP_ALTERNATION_FIXTURES_PATH),
                    str(NESTED_GROUP_REPLACEMENT_FIXTURES_PATH),
                    str(NESTED_GROUP_CALLABLE_REPLACEMENT_FIXTURES_PATH),
                    str(LITERAL_ALTERNATION_FIXTURES_PATH),
                    str(GROUPED_ALTERNATION_FIXTURES_PATH),
                    str(GROUPED_ALTERNATION_REPLACEMENT_FIXTURES_PATH),
                    str(GROUPED_ALTERNATION_CALLABLE_REPLACEMENT_FIXTURES_PATH),
                    str(BRANCH_LOCAL_BACKREFERENCE_FIXTURES_PATH),
                    str(OPTIONAL_GROUP_FIXTURES_PATH),
                    str(EXACT_REPEAT_QUANTIFIED_GROUP_FIXTURES_PATH),
                    str(RANGED_REPEAT_QUANTIFIED_GROUP_FIXTURES_PATH),
                    str(WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_FIXTURES_PATH),
                    str(OPTIONAL_GROUP_ALTERNATION_FIXTURES_PATH),
                    str(CONDITIONAL_GROUP_EXISTS_FIXTURES_PATH),
                    str(CONDITIONAL_GROUP_EXISTS_NO_ELSE_FIXTURES_PATH),
                    str(CONDITIONAL_GROUP_EXISTS_EMPTY_ELSE_FIXTURES_PATH),
                    str(CONDITIONAL_GROUP_EXISTS_EMPTY_YES_ELSE_FIXTURES_PATH),
                    str(CONDITIONAL_GROUP_EXISTS_FULLY_EMPTY_FIXTURES_PATH),
                    str(CONDITIONAL_GROUP_EXISTS_ASSERTION_DIAGNOSTICS_FIXTURES_PATH),
                    str(QUANTIFIED_ALTERNATION_FIXTURES_PATH),
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
                    "executed_cases": 232,
                    "failed_cases": 0,
                    "passed_cases": 226,
                    "skipped_cases": 0,
                    "total_cases": 232,
                    "unimplemented_cases": 6,
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
        self.assertEqual(scorecard["fixtures"]["manifest_count"], 35)
        self.assertEqual(scorecard["fixtures"]["manifest_ids"][-1], "quantified-alternation-workflows")
        self.assertEqual(len(scorecard["cases"]), 232)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        match_layer = scorecard["layers"]["match_behavior"]
        self.assertEqual(
            match_layer["summary"],
            {
                "executed_cases": 120,
                "failed_cases": 0,
                "passed_cases": 114,
                "skipped_cases": 0,
                "total_cases": 120,
                "unimplemented_cases": 6,
            },
        )
        self.assertIn("quantified-alternation-workflows", match_layer["manifest_ids"])
        self.assertEqual(match_layer["operations"], ["compile", "module_call", "pattern_call"])
        self.assertEqual(match_layer["text_models"], ["bytes", "str"])

        suite_ids = [suite["id"] for suite in scorecard["suites"]]
        self.assertIn("match.quantified_alternation", suite_ids)
        self.assertIn("match.quantified_alternation.str", suite_ids)
        self.assertIn("match.quantified_alternation.compile", suite_ids)
        self.assertIn("match.quantified_alternation.module_call", suite_ids)
        self.assertIn("match.quantified_alternation.pattern_call", suite_ids)

        quantified_suite = next(
            suite for suite in scorecard["suites"] if suite["id"] == "match.quantified_alternation"
        )
        self.assertEqual(
            quantified_suite["summary"],
            {
                "executed_cases": 6,
                "failed_cases": 0,
                "passed_cases": 0,
                "skipped_cases": 0,
                "total_cases": 6,
                "unimplemented_cases": 6,
            },
        )
        self.assertEqual(
            quantified_suite["families"],
            [
                "quantified_alternation_named_compile_metadata",
                "quantified_alternation_named_module_search_second_repetition_workflow",
                "quantified_alternation_named_pattern_fullmatch_lower_bound_workflow",
                "quantified_alternation_numbered_compile_metadata",
                "quantified_alternation_numbered_module_search_lower_bound_workflow",
                "quantified_alternation_numbered_pattern_fullmatch_second_repetition_workflow",
            ],
        )

        cases_by_id = {case["id"]: case for case in scorecard["cases"]}

        numbered_lower_bound_case = cases_by_id[
            "quantified-alternation-numbered-module-search-lower-bound-str"
        ]
        self.assertEqual(numbered_lower_bound_case["comparison"], "unimplemented")
        self.assertEqual(numbered_lower_bound_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(numbered_lower_bound_case["observations"]["cpython"]["result"]["group0"], "acd")
        self.assertEqual(numbered_lower_bound_case["observations"]["cpython"]["result"]["group1"], "c")
        self.assertEqual(numbered_lower_bound_case["observations"]["cpython"]["result"]["span1"], [3, 4])
        self.assertEqual(numbered_lower_bound_case["observations"]["rebar"]["outcome"], "unimplemented")

        named_second_repetition_case = cases_by_id[
            "quantified-alternation-named-module-search-second-repetition-str"
        ]
        self.assertEqual(named_second_repetition_case["comparison"], "unimplemented")
        self.assertEqual(named_second_repetition_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(named_second_repetition_case["observations"]["cpython"]["result"]["group0"], "acbd")
        self.assertEqual(named_second_repetition_case["observations"]["cpython"]["result"]["group1"], "b")
        self.assertEqual(
            named_second_repetition_case["observations"]["cpython"]["result"]["named_groups"],
            {"word": "b"},
        )
        self.assertEqual(
            named_second_repetition_case["observations"]["cpython"]["result"]["named_group_spans"],
            {"word": [4, 5]},
        )
        self.assertEqual(named_second_repetition_case["observations"]["rebar"]["outcome"], "unimplemented")
