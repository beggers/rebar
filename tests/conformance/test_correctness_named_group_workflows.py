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
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.json"


class CorrectnessHarnessNamedGroupWorkflowTest(unittest.TestCase):
    def test_runner_regenerates_combined_named_group_scorecard(self) -> None:
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
                    "executed_cases": 89,
                    "failed_cases": 0,
                    "passed_cases": 89,
                    "skipped_cases": 0,
                    "total_cases": 89,
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
        self.assertEqual(scorecard["fixtures"]["manifest_count"], 10)
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
            ],
        )
        self.assertEqual(len(scorecard["cases"]), 89)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        match_layer = scorecard["layers"]["match_behavior"]
        self.assertEqual(match_layer["summary"]["total_cases"], 15)
        self.assertEqual(match_layer["summary"]["passed_cases"], 15)
        self.assertEqual(match_layer["summary"]["failed_cases"], 0)
        self.assertEqual(match_layer["summary"]["unimplemented_cases"], 0)
        self.assertEqual(
            match_layer["manifest_ids"],
            [
                "grouped-match-workflows",
                "match-behavior-smoke",
                "named-group-workflows",
            ],
        )
        self.assertEqual(match_layer["operations"], ["compile", "module_call", "pattern_call"])
        self.assertEqual(match_layer["text_models"], ["bytes", "str"])

        suite_ids = [suite["id"] for suite in scorecard["suites"]]
        self.assertIn("match.named", suite_ids)
        self.assertIn("match.named.str", suite_ids)
        self.assertIn("match.named.compile", suite_ids)
        self.assertIn("match.named.module_call", suite_ids)
        self.assertIn("match.named.pattern_call", suite_ids)

        named_suite = next(suite for suite in scorecard["suites"] if suite["id"] == "match.named")
        self.assertEqual(named_suite["summary"]["total_cases"], 3)
        self.assertEqual(named_suite["summary"]["passed_cases"], 3)
        self.assertEqual(named_suite["summary"]["unimplemented_cases"], 0)
        self.assertEqual(
            named_suite["families"],
            [
                "named_group_compile_metadata",
                "named_group_module_workflow",
                "named_group_pattern_workflow",
            ],
        )

        compile_case = next(
            case for case in scorecard["cases"] if case["id"] == "named-group-compile-metadata-str"
        )
        self.assertEqual(compile_case["comparison"], "pass")
        self.assertEqual(compile_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(
            compile_case["observations"]["cpython"]["result"]["groupindex"],
            {"word": 1},
        )
        self.assertEqual(compile_case["observations"]["cpython"]["result"]["groups"], 1)
        self.assertEqual(compile_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(
            compile_case["observations"]["rebar"]["result"]["groupindex"],
            {"word": 1},
        )

        module_case = next(
            case for case in scorecard["cases"] if case["id"] == "named-group-module-search-metadata-str"
        )
        self.assertEqual(module_case["comparison"], "pass")
        self.assertEqual(module_case["helper"], "search")
        self.assertEqual(module_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(
            module_case["observations"]["cpython"]["result"]["groupdict"],
            {"word": "abc"},
        )
        self.assertEqual(
            module_case["observations"]["cpython"]["result"]["named_groups"],
            {"word": "abc"},
        )
        self.assertEqual(
            module_case["observations"]["cpython"]["result"]["named_group_spans"],
            {"word": [2, 5]},
        )
        self.assertEqual(module_case["observations"]["cpython"]["result"]["lastgroup"], "word")
        self.assertEqual(module_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(
            module_case["observations"]["rebar"]["result"]["groupdict"],
            {"word": "abc"},
        )
        self.assertEqual(
            module_case["observations"]["rebar"]["result"]["named_groups"],
            {"word": "abc"},
        )
        self.assertEqual(
            module_case["observations"]["rebar"]["result"]["named_group_spans"],
            {"word": [2, 5]},
        )
        self.assertEqual(module_case["observations"]["rebar"]["result"]["lastgroup"], "word")

        pattern_case = next(
            case for case in scorecard["cases"] if case["id"] == "named-group-pattern-search-metadata-str"
        )
        self.assertEqual(pattern_case["comparison"], "pass")
        self.assertEqual(pattern_case["helper"], "search")
        self.assertEqual(
            pattern_case["observations"]["cpython"]["result"]["named_groups"],
            {"word": "abc"},
        )
        self.assertEqual(
            pattern_case["observations"]["cpython"]["result"]["named_group_spans"],
            {"word": [2, 5]},
        )
        self.assertEqual(pattern_case["observations"]["cpython"]["result"]["lastgroup"], "word")
        self.assertEqual(pattern_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(
            pattern_case["observations"]["rebar"]["result"]["named_groups"],
            {"word": "abc"},
        )
        self.assertEqual(
            pattern_case["observations"]["rebar"]["result"]["named_group_spans"],
            {"word": [2, 5]},
        )
        self.assertEqual(pattern_case["observations"]["rebar"]["result"]["lastgroup"], "word")


if __name__ == "__main__":
    unittest.main()
