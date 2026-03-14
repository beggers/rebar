from __future__ import annotations

import json
import pathlib
import platform
import subprocess
import sys
import tempfile
import unittest

from tests.report_assertions import (
    assert_correctness_layer_summary_consistent,
    assert_correctness_summary_consistent,
    assert_correctness_suite_summary_consistent,
)


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
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.py"


class CorrectnessHarnessModuleWorkflowTest(unittest.TestCase):
    def test_runner_regenerates_combined_module_workflow_scorecard(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = pathlib.Path(temp_dir) / "correctness.json"
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

        assert_correctness_summary_consistent(self, scorecard, summary)
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
        self.assertEqual(scorecard["fixtures"]["manifest_count"], 6)
        self.assertEqual(
            scorecard["fixtures"]["manifest_ids"],
            [
                "parser-matrix",
                "public-api-surface",
                "match-behavior-smoke",
                "exported-symbol-surface",
                "pattern-object-surface",
                "module-workflow-surface",
            ],
        )
        self.assertEqual(len(scorecard["cases"]), 54)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        workflow_layer = assert_correctness_layer_summary_consistent(
            self,
            scorecard,
            "module_workflow",
        )
        self.assertEqual(workflow_layer["summary"]["total_cases"], 10)
        self.assertEqual(workflow_layer["summary"]["passed_cases"], 10)
        self.assertEqual(workflow_layer["summary"]["failed_cases"], 0)
        self.assertEqual(workflow_layer["summary"]["unimplemented_cases"], 0)
        self.assertEqual(
            workflow_layer["operations"],
            ["cache_workflow", "compile", "module_call", "pattern_call", "purge_workflow"],
        )
        self.assertEqual(workflow_layer["text_models"], ["bytes", "str"])

        suite_ids = [suite["id"] for suite in scorecard["suites"]]
        self.assertEqual(
            suite_ids,
            [
                "parser.compile",
                "parser.compile.bytes",
                "parser.compile.str",
                "module.surface",
                "module.surface.module_call",
                "module.surface.module_has_attr",
                "match.behavior",
                "match.behavior.bytes",
                "match.behavior.str",
                "module.exports",
                "module.exports.module_attr_metadata",
                "module.exports.module_attr_value",
                "module.exports.module_call",
                "pattern.object",
                "pattern.object.bytes",
                "pattern.object.str",
                "pattern.object.pattern_call",
                "pattern.object.pattern_metadata",
                "module.workflow",
                "module.workflow.bytes",
                "module.workflow.str",
                "module.workflow.cache_workflow",
                "module.workflow.compile",
                "module.workflow.module_call",
                "module.workflow.pattern_call",
                "module.workflow.purge_workflow",
            ],
        )

        workflow_suite = assert_correctness_suite_summary_consistent(
            self,
            scorecard,
            "module.workflow",
        )
        self.assertEqual(workflow_suite["summary"]["total_cases"], 10)
        self.assertEqual(workflow_suite["summary"]["passed_cases"], 10)
        self.assertEqual(
            workflow_suite["families"],
            [
                "bound_fullmatch_workflow",
                "bound_match_workflow",
                "bound_search_workflow",
                "cache_workflow",
                "compile_workflow",
                "escape_workflow",
                "purge_workflow",
            ],
        )

        cache_case = next(case for case in scorecard["cases"] if case["id"] == "workflow-cache-hit-str")
        self.assertEqual(cache_case["comparison"], "pass")
        self.assertEqual(cache_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(cache_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(cache_case["observations"]["rebar"]["result"]["same_object"], True)
        self.assertEqual(
            cache_case["observations"]["rebar"]["result"],
            cache_case["observations"]["cpython"]["result"],
        )

        purge_case = next(case for case in scorecard["cases"] if case["id"] == "workflow-purge-reset-str")
        self.assertEqual(purge_case["comparison"], "pass")
        self.assertEqual(purge_case["observations"]["rebar"]["result"]["before_purge_same_object"], True)
        self.assertEqual(purge_case["observations"]["rebar"]["result"]["after_purge_new_object"], True)
        self.assertEqual(purge_case["observations"]["rebar"]["result"]["after_purge_cache_hit"], True)
        self.assertEqual(purge_case["observations"]["rebar"]["result"]["purge_result"], None)

        bound_search_case = next(
            case for case in scorecard["cases"] if case["id"] == "workflow-pattern-search-str"
        )
        self.assertEqual(bound_search_case["comparison"], "pass")
        self.assertEqual(bound_search_case["helper"], "search")
        self.assertEqual(bound_search_case["observations"]["rebar"]["result"]["group0"], "abc")
        self.assertEqual(bound_search_case["observations"]["rebar"]["result"]["span"], [2, 5])

        bytes_fullmatch_case = next(
            case for case in scorecard["cases"] if case["id"] == "workflow-pattern-fullmatch-bytes"
        )
        self.assertEqual(bytes_fullmatch_case["comparison"], "pass")
        self.assertEqual(bytes_fullmatch_case["text_model"], "bytes")
        self.assertEqual(
            bytes_fullmatch_case["observations"]["rebar"]["result"]["group0"],
            {"encoding": "latin-1", "value": "123"},
        )

        escape_case = next(case for case in scorecard["cases"] if case["id"] == "workflow-escape-bytes")
        self.assertEqual(escape_case["comparison"], "pass")
        self.assertEqual(
            escape_case["observations"]["rebar"]["result"],
            {"encoding": "latin-1", "value": "a\\-b\\.c"},
        )
        self.assertEqual(
            escape_case["observations"]["rebar"]["result"],
            escape_case["observations"]["cpython"]["result"],
        )


if __name__ == "__main__":
    unittest.main()
