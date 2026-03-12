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
OPTIONAL_GROUP_ALTERNATION_FIXTURES_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "optional_group_alternation_workflows.json"
)
CONDITIONAL_GROUP_EXISTS_FIXTURES_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "conditional_group_exists_workflows.json"
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
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.json"


class CorrectnessHarnessConditionalGroupExistsAssertionDiagnosticsTest(unittest.TestCase):
    def test_runner_regenerates_combined_conditional_group_exists_assertion_diagnostic_scorecard(
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
                    str(OPTIONAL_GROUP_ALTERNATION_FIXTURES_PATH),
                    str(CONDITIONAL_GROUP_EXISTS_FIXTURES_PATH),
                    str(CONDITIONAL_GROUP_EXISTS_NO_ELSE_FIXTURES_PATH),
                    str(CONDITIONAL_GROUP_EXISTS_EMPTY_ELSE_FIXTURES_PATH),
                    str(CONDITIONAL_GROUP_EXISTS_EMPTY_YES_ELSE_FIXTURES_PATH),
                    str(CONDITIONAL_GROUP_EXISTS_FULLY_EMPTY_FIXTURES_PATH),
                    str(CONDITIONAL_GROUP_EXISTS_ASSERTION_DIAGNOSTICS_FIXTURES_PATH),
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
                    "executed_cases": 220,
                    "failed_cases": 0,
                    "passed_cases": 220,
                    "skipped_cases": 0,
                    "total_cases": 220,
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
        self.assertEqual(scorecard["fixtures"]["manifest_count"], 33)
        self.assertIn(
            "conditional-group-exists-assertion-diagnostics",
            scorecard["fixtures"]["manifest_ids"],
        )
        self.assertEqual(len(scorecard["cases"]), 220)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        parser_layer = scorecard["layers"]["parser_acceptance_and_diagnostics"]
        self.assertEqual(parser_layer["summary"]["total_cases"], 17)
        self.assertEqual(parser_layer["summary"]["passed_cases"], 17)
        self.assertEqual(parser_layer["summary"]["unimplemented_cases"], 0)
        self.assertIn(
            "conditional-group-exists-assertion-diagnostics",
            parser_layer["manifest_ids"],
        )

        assertion_suite = next(
            suite
            for suite in scorecard["suites"]
            if suite["id"] == "parser.conditional_group_exists_assertion_diagnostics"
        )
        self.assertEqual(assertion_suite["summary"]["total_cases"], 2)
        self.assertEqual(assertion_suite["summary"]["passed_cases"], 2)
        self.assertEqual(assertion_suite["summary"]["unimplemented_cases"], 0)
        self.assertEqual(
            assertion_suite["families"],
            ["conditional_group_exists_assertion_compile_diagnostic"],
        )

        assertion_str_suite = next(
            suite
            for suite in scorecard["suites"]
            if suite["id"] == "parser.conditional_group_exists_assertion_diagnostics.str"
        )
        self.assertEqual(assertion_str_suite["summary"]["total_cases"], 2)
        self.assertEqual(assertion_str_suite["summary"]["passed_cases"], 2)
        self.assertEqual(assertion_str_suite["summary"]["unimplemented_cases"], 0)

        cpython_diagnostics = assertion_suite["diagnostics"]["by_adapter"]["cpython"]
        self.assertEqual(cpython_diagnostics["outcomes"], {"exception": 2})
        self.assertEqual(cpython_diagnostics["exception_case_count"], 2)
        self.assertEqual(cpython_diagnostics["exception_types"], {"error": 2})

        rebar_diagnostics = assertion_suite["diagnostics"]["by_adapter"]["rebar"]
        self.assertEqual(rebar_diagnostics["outcomes"], {"exception": 2})
        self.assertEqual(rebar_diagnostics["exception_case_count"], 2)
        self.assertEqual(rebar_diagnostics["exception_types"], {"error": 2})

        positive_case = next(
            case
            for case in scorecard["cases"]
            if case["id"] == "conditional-group-exists-assertion-positive-lookahead-error-str"
        )
        self.assertEqual(positive_case["layer"], "parser_acceptance_and_diagnostics")
        self.assertEqual(positive_case["comparison"], "pass")
        self.assertEqual(positive_case["observations"]["cpython"]["outcome"], "exception")
        self.assertEqual(
            positive_case["observations"]["cpython"]["exception"],
            {
                "colno": 5,
                "lineno": 1,
                "message": "bad character in group name '?=b' at position 4",
                "pos": 4,
                "type": "error",
            },
        )
        self.assertEqual(positive_case["observations"]["rebar"]["outcome"], "exception")
        self.assertEqual(
            positive_case["observations"]["rebar"]["exception"],
            positive_case["observations"]["cpython"]["exception"],
        )

        negative_case = next(
            case
            for case in scorecard["cases"]
            if case["id"] == "conditional-group-exists-assertion-negative-lookahead-error-str"
        )
        self.assertEqual(negative_case["comparison"], "pass")
        self.assertEqual(
            negative_case["observations"]["cpython"]["exception"],
            {
                "colno": 5,
                "lineno": 1,
                "message": "bad character in group name '?!b' at position 4",
                "pos": 4,
                "type": "error",
            },
        )
        self.assertEqual(negative_case["observations"]["rebar"]["outcome"], "exception")
        self.assertEqual(
            negative_case["observations"]["rebar"]["exception"],
            negative_case["observations"]["cpython"]["exception"],
        )


if __name__ == "__main__":
    unittest.main()
