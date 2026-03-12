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
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.json"


class CorrectnessHarnessGroupedMatchWorkflowTest(unittest.TestCase):
    def test_runner_regenerates_combined_grouped_match_scorecard(self) -> None:
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
                    "executed_cases": 86,
                    "failed_cases": 0,
                    "passed_cases": 86,
                    "skipped_cases": 0,
                    "total_cases": 86,
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
        self.assertEqual(scorecard["fixtures"]["manifest_count"], 9)
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
            ],
        )
        self.assertEqual(len(scorecard["cases"]), 86)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        match_layer = scorecard["layers"]["match_behavior"]
        self.assertEqual(match_layer["summary"]["total_cases"], 12)
        self.assertEqual(match_layer["summary"]["passed_cases"], 12)
        self.assertEqual(match_layer["summary"]["failed_cases"], 0)
        self.assertEqual(match_layer["summary"]["unimplemented_cases"], 0)
        self.assertEqual(
            match_layer["manifest_ids"],
            ["grouped-match-workflows", "match-behavior-smoke"],
        )
        self.assertEqual(match_layer["operations"], ["module_call", "pattern_call"])
        self.assertEqual(match_layer["text_models"], ["bytes", "str"])

        suite_ids = [suite["id"] for suite in scorecard["suites"]]
        self.assertIn("match.grouped", suite_ids)
        self.assertIn("match.grouped.str", suite_ids)
        self.assertIn("match.grouped.module_call", suite_ids)
        self.assertIn("match.grouped.pattern_call", suite_ids)

        grouped_suite = next(suite for suite in scorecard["suites"] if suite["id"] == "match.grouped")
        self.assertEqual(grouped_suite["summary"]["total_cases"], 6)
        self.assertEqual(grouped_suite["summary"]["passed_cases"], 6)
        self.assertEqual(grouped_suite["summary"]["unimplemented_cases"], 0)
        self.assertEqual(
            grouped_suite["families"],
            ["numbered_capture_gap_workflow", "single_capture_module_workflow", "single_capture_pattern_workflow"],
        )

        search_case = next(
            case for case in scorecard["cases"] if case["id"] == "grouped-module-search-single-capture-str"
        )
        self.assertEqual(search_case["comparison"], "pass")
        self.assertEqual(search_case["helper"], "search")
        self.assertEqual(search_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(search_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(search_case["observations"]["rebar"]["result"]["group0"], "abc")
        self.assertEqual(search_case["observations"]["rebar"]["result"]["group1"], "abc")
        self.assertEqual(search_case["observations"]["rebar"]["result"]["groups"], ["abc"])
        self.assertEqual(search_case["observations"]["rebar"]["result"]["span"], [2, 5])
        self.assertEqual(search_case["observations"]["rebar"]["result"]["span1"], [2, 5])
        self.assertEqual(search_case["observations"]["rebar"]["result"]["group_spans"], [[2, 5]])
        self.assertEqual(search_case["observations"]["rebar"]["result"]["lastindex"], 1)
        self.assertEqual(
            search_case["observations"]["rebar"]["result"],
            search_case["observations"]["cpython"]["result"],
        )

        pattern_case = next(
            case for case in scorecard["cases"] if case["id"] == "grouped-pattern-match-single-capture-str"
        )
        self.assertEqual(pattern_case["comparison"], "pass")
        self.assertEqual(pattern_case["helper"], "match")
        self.assertEqual(pattern_case["observations"]["rebar"]["result"]["group1"], "abc")
        self.assertEqual(pattern_case["observations"]["rebar"]["result"]["span1"], [0, 3])
        self.assertEqual(pattern_case["observations"]["rebar"]["result"]["lastindex"], 1)

        gap_case = next(
            case
            for case in scorecard["cases"]
            if case["id"] == "grouped-module-fullmatch-two-capture-gap-str"
        )
        self.assertEqual(gap_case["comparison"], "pass")
        self.assertEqual(gap_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(gap_case["observations"]["cpython"]["result"]["group1"], "ab")
        self.assertEqual(gap_case["observations"]["cpython"]["result"]["groups"], ["ab", "c"])
        self.assertEqual(gap_case["observations"]["cpython"]["result"]["span1"], [0, 2])
        self.assertEqual(gap_case["observations"]["cpython"]["result"]["group_spans"], [[0, 2], [2, 3]])
        self.assertEqual(gap_case["observations"]["cpython"]["result"]["lastindex"], 2)
        self.assertEqual(gap_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(
            gap_case["observations"]["rebar"]["result"],
            gap_case["observations"]["cpython"]["result"],
        )


if __name__ == "__main__":
    unittest.main()
