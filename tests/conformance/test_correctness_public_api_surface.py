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
            self.assertEqual(
                summary,
                {
                    "executed_cases": 22,
                    "failed_cases": 0,
                    "passed_cases": 4,
                    "skipped_cases": 0,
                    "total_cases": 22,
                    "unimplemented_cases": 18,
                },
            )

            scorecard = json.loads(report_path.read_text(encoding="utf-8"))

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

        parser_layer = scorecard["layers"]["parser_acceptance_and_diagnostics"]
        self.assertEqual(parser_layer["summary"]["total_cases"], 15)
        self.assertEqual(parser_layer["summary"]["unimplemented_cases"], 15)

        public_api_layer = scorecard["layers"]["module_api_surface"]
        self.assertEqual(public_api_layer["summary"]["total_cases"], 7)
        self.assertEqual(public_api_layer["summary"]["passed_cases"], 4)
        self.assertEqual(public_api_layer["summary"]["unimplemented_cases"], 3)
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

        public_api_suite = next(suite for suite in scorecard["suites"] if suite["id"] == "module.surface")
        self.assertEqual(public_api_suite["summary"]["passed_cases"], 4)
        self.assertEqual(public_api_suite["summary"]["unimplemented_cases"], 3)

        compile_case = next(
            case for case in scorecard["cases"] if case["id"] == "compile-placeholder-notimplemented"
        )
        self.assertEqual(compile_case["layer"], "module_api_surface")
        self.assertEqual(compile_case["helper"], "compile")
        self.assertEqual(compile_case["comparison"], "unimplemented")
        self.assertEqual(compile_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(compile_case["observations"]["rebar"]["outcome"], "unimplemented")
        self.assertEqual(
            compile_case["observations"]["rebar"]["exception"]["type"],
            "NotImplementedError",
        )
        self.assertIn(
            "rebar.compile() is a scaffold placeholder",
            compile_case["observations"]["rebar"]["exception"]["message"],
        )

        purge_case = next(case for case in scorecard["cases"] if case["id"] == "purge-noop-success")
        self.assertEqual(purge_case["comparison"], "pass")
        self.assertEqual(purge_case["observations"]["cpython"]["result"], None)
        self.assertEqual(purge_case["observations"]["rebar"]["result"], None)


if __name__ == "__main__":
    unittest.main()
