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
PARSER_FIXTURES_PATH = REPO_ROOT / "tests" / "conformance" / "fixtures" / "parser_matrix.py"
PUBLIC_API_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "public_api_surface.py"
)
MATCH_BEHAVIOR_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "match_behavior_smoke.py"
)
EXPORTED_SYMBOL_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "exported_symbol_surface.py"
)
PATTERN_OBJECT_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "pattern_object_surface.py"
)
MODULE_WORKFLOW_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "module_workflow_surface.py"
)
COLLECTION_REPLACEMENT_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "collection_replacement_workflows.py"
)
LITERAL_FLAG_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "literal_flag_workflows.py"
)
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.py"


class CorrectnessHarnessLiteralFlagWorkflowTest(unittest.TestCase):
    def test_runner_regenerates_combined_literal_flag_scorecard(self) -> None:
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
                    "executed_cases": 80,
                    "failed_cases": 0,
                    "passed_cases": 80,
                    "skipped_cases": 0,
                    "total_cases": 80,
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
        self.assertEqual(scorecard["fixtures"]["manifest_count"], 8)
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
            ],
        )
        self.assertEqual(len(scorecard["cases"]), 80)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        workflow_layer = scorecard["layers"]["module_workflow"]
        self.assertEqual(workflow_layer["summary"]["total_cases"], 36)
        self.assertEqual(workflow_layer["summary"]["passed_cases"], 36)
        self.assertEqual(workflow_layer["summary"]["failed_cases"], 0)
        self.assertEqual(workflow_layer["summary"]["unimplemented_cases"], 0)
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
        self.assertEqual(
            workflow_layer["manifest_ids"],
            [
                "collection-replacement-workflows",
                "literal-flag-workflows",
                "module-workflow-surface",
            ],
        )

        suite_ids = [suite["id"] for suite in scorecard["suites"]]
        self.assertIn("literal.flag.workflow", suite_ids)
        self.assertIn("literal.flag.workflow.bytes", suite_ids)
        self.assertIn("literal.flag.workflow.str", suite_ids)
        self.assertIn("literal.flag.workflow.cache_distinct_workflow", suite_ids)
        self.assertIn("literal.flag.workflow.module_call", suite_ids)
        self.assertIn("literal.flag.workflow.pattern_call", suite_ids)

        flag_suite = next(suite for suite in scorecard["suites"] if suite["id"] == "literal.flag.workflow")
        self.assertEqual(flag_suite["summary"]["total_cases"], 11)
        self.assertEqual(flag_suite["summary"]["passed_cases"], 11)
        self.assertEqual(flag_suite["summary"]["unimplemented_cases"], 0)
        self.assertEqual(
            flag_suite["families"],
            [
                "bounded_wildcard_flag_workflow",
                "literal_flag_cache_workflow",
                "literal_ignorecase_workflow",
                "unsupported_flag_workflow",
            ],
        )

        search_case = next(
            case for case in scorecard["cases"] if case["id"] == "flag-module-search-ignorecase-str-hit"
        )
        self.assertEqual(search_case["comparison"], "pass")
        self.assertEqual(search_case["helper"], "search")
        self.assertEqual(search_case["flags"], 2)
        self.assertEqual(search_case["observations"]["rebar"]["result"]["group0"], "aBc")
        self.assertEqual(search_case["observations"]["rebar"]["result"]["span"], [2, 5])

        miss_case = next(
            case for case in scorecard["cases"] if case["id"] == "flag-pattern-fullmatch-ignorecase-str-miss"
        )
        self.assertEqual(miss_case["comparison"], "pass")
        self.assertEqual(miss_case["observations"]["rebar"]["result"], None)
        self.assertEqual(miss_case["observations"]["rebar"]["result"], miss_case["observations"]["cpython"]["result"])

        bytes_case = next(
            case for case in scorecard["cases"] if case["id"] == "flag-pattern-match-ignorecase-bytes-hit"
        )
        self.assertEqual(bytes_case["comparison"], "pass")
        self.assertEqual(bytes_case["text_model"], "bytes")
        self.assertEqual(
            bytes_case["observations"]["rebar"]["result"]["group0"],
            {"encoding": "latin-1", "value": "aBc"},
        )

        cache_case = next(
            case for case in scorecard["cases"] if case["id"] == "flag-cache-distinct-str-normalized"
        )
        self.assertEqual(cache_case["comparison"], "pass")
        self.assertEqual(cache_case["kwargs"], {"alias_flags": 2, "distinct_flags": 0})
        self.assertEqual(cache_case["observations"]["rebar"]["result"]["same_object_as_alias"], True)
        self.assertEqual(cache_case["observations"]["rebar"]["result"]["same_object_as_distinct"], False)
        self.assertEqual(
            cache_case["observations"]["rebar"]["result"],
            cache_case["observations"]["cpython"]["result"],
        )

        inline_case = next(
            case for case in scorecard["cases"] if case["id"] == "flag-unsupported-inline-flag-search"
        )
        self.assertEqual(inline_case["comparison"], "pass")
        self.assertEqual(inline_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(inline_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(
            inline_case["observations"]["rebar"]["result"],
            inline_case["observations"]["cpython"]["result"],
        )

        locale_case = next(
            case for case in scorecard["cases"] if case["id"] == "flag-unsupported-locale-bytes-search"
        )
        self.assertEqual(locale_case["comparison"], "pass")
        self.assertEqual(locale_case["text_model"], "bytes")
        self.assertEqual(locale_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(locale_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(
            locale_case["observations"]["rebar"]["result"],
            locale_case["observations"]["cpython"]["result"],
        )

        nonliteral_case = next(
            case
            for case in scorecard["cases"]
            if case["id"] == "flag-unsupported-nonliteral-ignorecase-search"
        )
        self.assertEqual(nonliteral_case["comparison"], "pass")
        self.assertEqual(nonliteral_case["family"], "bounded_wildcard_flag_workflow")
        self.assertEqual(nonliteral_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(nonliteral_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(
            nonliteral_case["observations"]["rebar"]["result"],
            nonliteral_case["observations"]["cpython"]["result"],
        )


if __name__ == "__main__":
    unittest.main()
