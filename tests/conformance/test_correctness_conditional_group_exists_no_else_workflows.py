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
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.json"


class CorrectnessHarnessConditionalGroupExistsNoElseWorkflowTest(unittest.TestCase):
    def test_runner_regenerates_combined_conditional_group_exists_no_else_scorecard(self) -> None:
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
                    "executed_cases": 200,
                    "failed_cases": 0,
                    "passed_cases": 194,
                    "skipped_cases": 0,
                    "total_cases": 200,
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
        self.assertEqual(scorecard["fixtures"]["manifest_count"], 29)
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
                "nested-group-alternation-workflows",
                "nested-group-replacement-workflows",
                "nested-group-callable-replacement-workflows",
                "literal-alternation-workflows",
                "grouped-alternation-workflows",
                "grouped-alternation-replacement-workflows",
                "grouped-alternation-callable-replacement-workflows",
                "branch-local-backreference-workflows",
                "optional-group-workflows",
                "exact-repeat-quantified-group-workflows",
                "ranged-repeat-quantified-group-workflows",
                "optional-group-alternation-workflows",
                "conditional-group-exists-workflows",
                "conditional-group-exists-no-else-workflows",
            ],
        )
        self.assertEqual(len(scorecard["cases"]), 200)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        match_layer = scorecard["layers"]["match_behavior"]
        self.assertEqual(match_layer["summary"]["total_cases"], 90)
        self.assertEqual(match_layer["summary"]["passed_cases"], 84)
        self.assertEqual(match_layer["summary"]["failed_cases"], 0)
        self.assertEqual(match_layer["summary"]["unimplemented_cases"], 6)
        self.assertEqual(
            match_layer["manifest_ids"],
            [
                "branch-local-backreference-workflows",
                "conditional-group-exists-no-else-workflows",
                "conditional-group-exists-workflows",
                "exact-repeat-quantified-group-workflows",
                "grouped-alternation-workflows",
                "grouped-match-workflows",
                "grouped-segment-workflows",
                "literal-alternation-workflows",
                "match-behavior-smoke",
                "named-backreference-workflows",
                "named-group-workflows",
                "nested-group-alternation-workflows",
                "nested-group-workflows",
                "numbered-backreference-workflows",
                "optional-group-alternation-workflows",
                "optional-group-workflows",
                "ranged-repeat-quantified-group-workflows",
            ],
        )
        self.assertEqual(match_layer["operations"], ["compile", "module_call", "pattern_call"])
        self.assertEqual(match_layer["text_models"], ["bytes", "str"])

        suite_ids = [suite["id"] for suite in scorecard["suites"]]
        self.assertIn("match.conditional_group_exists_no_else", suite_ids)
        self.assertIn("match.conditional_group_exists_no_else.str", suite_ids)
        self.assertIn("match.conditional_group_exists_no_else.compile", suite_ids)
        self.assertIn("match.conditional_group_exists_no_else.module_call", suite_ids)
        self.assertIn("match.conditional_group_exists_no_else.pattern_call", suite_ids)

        conditional_suite = next(
            suite
            for suite in scorecard["suites"]
            if suite["id"] == "match.conditional_group_exists_no_else"
        )
        self.assertEqual(conditional_suite["summary"]["total_cases"], 6)
        self.assertEqual(conditional_suite["summary"]["passed_cases"], 0)
        self.assertEqual(conditional_suite["summary"]["failed_cases"], 0)
        self.assertEqual(conditional_suite["summary"]["unimplemented_cases"], 6)
        self.assertEqual(
            conditional_suite["families"],
            [
                "conditional_group_exists_no_else_compile_metadata",
                "conditional_group_exists_no_else_module_present_workflow",
                "conditional_group_exists_no_else_pattern_absent_workflow",
                "named_conditional_group_exists_no_else_compile_metadata",
                "named_conditional_group_exists_no_else_module_present_workflow",
                "named_conditional_group_exists_no_else_pattern_absent_workflow",
            ],
        )

        compile_case = next(
            case
            for case in scorecard["cases"]
            if case["id"] == "conditional-group-exists-no-else-compile-metadata-str"
        )
        self.assertEqual(compile_case["comparison"], "unimplemented")
        self.assertEqual(compile_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(compile_case["observations"]["cpython"]["result"]["groupindex"], {})
        self.assertEqual(compile_case["observations"]["cpython"]["result"]["groups"], 1)
        self.assertEqual(compile_case["observations"]["rebar"]["outcome"], "unimplemented")

        module_present_case = next(
            case
            for case in scorecard["cases"]
            if case["id"] == "conditional-group-exists-no-else-module-search-present-str"
        )
        self.assertEqual(module_present_case["comparison"], "unimplemented")
        self.assertEqual(module_present_case["helper"], "search")
        self.assertEqual(module_present_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(module_present_case["observations"]["cpython"]["result"]["group0"], "abcd")
        self.assertEqual(module_present_case["observations"]["cpython"]["result"]["groups"], ["b"])
        self.assertEqual(module_present_case["observations"]["cpython"]["result"]["lastindex"], 1)
        self.assertEqual(module_present_case["observations"]["cpython"]["result"]["span1"], [3, 4])
        self.assertEqual(module_present_case["observations"]["rebar"]["outcome"], "unimplemented")

        pattern_absent_case = next(
            case
            for case in scorecard["cases"]
            if case["id"] == "conditional-group-exists-no-else-pattern-fullmatch-absent-str"
        )
        self.assertEqual(pattern_absent_case["comparison"], "unimplemented")
        self.assertEqual(pattern_absent_case["helper"], "fullmatch")
        self.assertEqual(pattern_absent_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(pattern_absent_case["observations"]["cpython"]["result"]["group0"], "ac")
        self.assertEqual(pattern_absent_case["observations"]["cpython"]["result"]["groups"], [None])
        self.assertEqual(pattern_absent_case["observations"]["cpython"]["result"]["lastindex"], None)
        self.assertEqual(pattern_absent_case["observations"]["cpython"]["result"]["span1"], [-1, -1])
        self.assertEqual(pattern_absent_case["observations"]["rebar"]["outcome"], "unimplemented")

        named_compile_case = next(
            case
            for case in scorecard["cases"]
            if case["id"] == "named-conditional-group-exists-no-else-compile-metadata-str"
        )
        self.assertEqual(named_compile_case["comparison"], "unimplemented")
        self.assertEqual(named_compile_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(
            named_compile_case["observations"]["cpython"]["result"]["groupindex"],
            {"word": 1},
        )
        self.assertEqual(named_compile_case["observations"]["cpython"]["result"]["groups"], 1)
        self.assertEqual(named_compile_case["observations"]["rebar"]["outcome"], "unimplemented")

        named_module_present_case = next(
            case
            for case in scorecard["cases"]
            if case["id"] == "named-conditional-group-exists-no-else-module-search-present-str"
        )
        self.assertEqual(named_module_present_case["comparison"], "unimplemented")
        self.assertEqual(named_module_present_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(named_module_present_case["observations"]["cpython"]["result"]["group0"], "abcd")
        self.assertEqual(named_module_present_case["observations"]["cpython"]["result"]["groups"], ["b"])
        self.assertEqual(
            named_module_present_case["observations"]["cpython"]["result"]["groupdict"],
            {"word": "b"},
        )
        self.assertEqual(named_module_present_case["observations"]["cpython"]["result"]["lastgroup"], "word")
        self.assertEqual(named_module_present_case["observations"]["rebar"]["outcome"], "unimplemented")

        named_pattern_absent_case = next(
            case
            for case in scorecard["cases"]
            if case["id"] == "named-conditional-group-exists-no-else-pattern-fullmatch-absent-str"
        )
        self.assertEqual(named_pattern_absent_case["comparison"], "unimplemented")
        self.assertEqual(named_pattern_absent_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(named_pattern_absent_case["observations"]["cpython"]["result"]["group0"], "ac")
        self.assertEqual(named_pattern_absent_case["observations"]["cpython"]["result"]["groups"], [None])
        self.assertEqual(
            named_pattern_absent_case["observations"]["cpython"]["result"]["groupdict"],
            {"word": None},
        )
        self.assertEqual(named_pattern_absent_case["observations"]["cpython"]["result"]["lastgroup"], None)
        self.assertEqual(named_pattern_absent_case["observations"]["rebar"]["outcome"], "unimplemented")


if __name__ == "__main__":
    unittest.main()
