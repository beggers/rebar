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
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.json"


class CorrectnessHarnessPublicApiSurfaceTest(unittest.TestCase):
    def test_runner_regenerates_combined_public_api_scorecard(self) -> None:
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
        self.assertEqual(scorecard["phase"], "phase2-public-api-surface-pack")
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
        self.assertEqual(scorecard["fixtures"]["manifest_count"], 2)
        self.assertEqual(
            scorecard["fixtures"]["manifest_ids"],
            ["parser-matrix", "public-api-surface"],
        )
        self.assertEqual(len(scorecard["cases"]), 22)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        parser_layer = assert_correctness_layer_summary_consistent(
            self,
            scorecard,
            "parser_acceptance_and_diagnostics",
        )
        self.assertEqual(parser_layer["summary"]["total_cases"], 15)
        self.assertEqual(parser_layer["summary"]["passed_cases"], 15)
        self.assertEqual(parser_layer["summary"]["unimplemented_cases"], 0)

        public_api_layer = assert_correctness_layer_summary_consistent(
            self,
            scorecard,
            "module_api_surface",
        )
        self.assertEqual(public_api_layer["summary"]["total_cases"], 7)
        self.assertEqual(public_api_layer["summary"]["passed_cases"], 7)
        self.assertEqual(public_api_layer["summary"]["unimplemented_cases"], 0)
        self.assertEqual(
            public_api_layer["operations"],
            ["module_call", "module_has_attr"],
        )

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
            ],
        )

        public_api_suite = assert_correctness_suite_summary_consistent(
            self,
            scorecard,
            "module.surface",
        )
        self.assertEqual(public_api_suite["summary"]["passed_cases"], 7)
        self.assertEqual(public_api_suite["summary"]["unimplemented_cases"], 0)

        compile_case = next(case for case in scorecard["cases"] if case["id"] == "compile-pattern-scaffold-success")
        self.assertEqual(compile_case["layer"], "module_api_surface")
        self.assertEqual(compile_case["helper"], "compile")
        self.assertEqual(compile_case["comparison"], "pass")
        self.assertEqual(compile_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(compile_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(
            compile_case["observations"]["rebar"]["result"],
            compile_case["observations"]["cpython"]["result"],
        )

        purge_case = next(case for case in scorecard["cases"] if case["id"] == "purge-noop-success")
        self.assertEqual(purge_case["comparison"], "pass")
        self.assertEqual(purge_case["observations"]["cpython"]["result"], None)
        self.assertEqual(purge_case["observations"]["rebar"]["result"], None)

        search_case = next(case for case in scorecard["cases"] if case["id"] == "search-literal-success")
        self.assertEqual(search_case["comparison"], "pass")
        self.assertEqual(search_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(
            search_case["observations"]["rebar"]["result"],
            search_case["observations"]["cpython"]["result"],
        )

        escape_case = next(case for case in scorecard["cases"] if case["id"] == "escape-success")
        self.assertEqual(escape_case["comparison"], "pass")
        self.assertEqual(escape_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(escape_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(
            escape_case["observations"]["rebar"]["result"],
            "a\\-b\\.c",
        )
        self.assertEqual(
            escape_case["observations"]["rebar"]["result"],
            escape_case["observations"]["cpython"]["result"],
        )

        parser_literal_case = next(case for case in scorecard["cases"] if case["id"] == "str-literal-success")
        self.assertEqual(parser_literal_case["comparison"], "pass")
        self.assertEqual(parser_literal_case["observations"]["rebar"]["outcome"], "success")


if __name__ == "__main__":
    unittest.main()
