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
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.json"


class CorrectnessHarnessExportedSymbolSurfaceTest(unittest.TestCase):
    def test_runner_regenerates_combined_exported_symbol_scorecard(self) -> None:
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
                    "executed_cases": 38,
                    "failed_cases": 0,
                    "passed_cases": 25,
                    "skipped_cases": 0,
                    "total_cases": 38,
                    "unimplemented_cases": 13,
                },
            )

            scorecard = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(scorecard["schema_version"], "1.0")
        self.assertEqual(scorecard["phase"], "phase3-match-behavior-pack")
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
        self.assertEqual(scorecard["fixtures"]["manifest_count"], 4)
        self.assertEqual(
            scorecard["fixtures"]["manifest_ids"],
            [
                "parser-matrix",
                "public-api-surface",
                "match-behavior-smoke",
                "exported-symbol-surface",
            ],
        )
        self.assertEqual(len(scorecard["cases"]), 38)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        public_api_layer = scorecard["layers"]["module_api_surface"]
        self.assertEqual(public_api_layer["summary"]["total_cases"], 17)
        self.assertEqual(public_api_layer["summary"]["passed_cases"], 17)
        self.assertEqual(public_api_layer["summary"]["failed_cases"], 0)
        self.assertEqual(public_api_layer["summary"]["unimplemented_cases"], 0)
        self.assertEqual(
            public_api_layer["operations"],
            ["module_attr_metadata", "module_attr_value", "module_call", "module_has_attr"],
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
                "match.behavior",
                "match.behavior.bytes",
                "match.behavior.str",
                "module.exports",
                "module.exports.module_attr_metadata",
                "module.exports.module_attr_value",
                "module.exports.module_call",
            ],
        )

        export_suite = next(suite for suite in scorecard["suites"] if suite["id"] == "module.exports")
        self.assertEqual(export_suite["summary"]["total_cases"], 10)
        self.assertEqual(export_suite["summary"]["passed_cases"], 10)
        self.assertEqual(export_suite["summary"]["failed_cases"], 0)
        self.assertEqual(
            export_suite["families"],
            [
                "exception_type_metadata",
                "flag_constant_values",
                "helper_type_instantiation_guard",
                "helper_type_metadata",
            ],
        )

        regexflag_case = next(case for case in scorecard["cases"] if case["id"] == "regexflag-type-metadata")
        self.assertEqual(regexflag_case["comparison"], "pass")
        self.assertEqual(regexflag_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(regexflag_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(regexflag_case["observations"]["cpython"]["result"]["module"], "re")
        self.assertEqual(regexflag_case["observations"]["rebar"]["result"]["module"], "re")
        self.assertIn("A", regexflag_case["observations"]["cpython"]["result"]["members"])
        self.assertIn("A", regexflag_case["observations"]["rebar"]["result"]["members"])
        self.assertEqual(
            regexflag_case["observations"]["rebar"]["result"]["members"]["ASCII"],
            256,
        )
        self.assertEqual(
            regexflag_case["observations"]["rebar"]["result"],
            regexflag_case["observations"]["cpython"]["result"],
        )

        error_case = next(case for case in scorecard["cases"] if case["id"] == "error-type-metadata")
        self.assertEqual(error_case["comparison"], "pass")
        self.assertEqual(error_case["observations"]["cpython"]["result"]["module"], "re")
        self.assertEqual(error_case["observations"]["rebar"]["result"]["module"], "re")

        ascii_case = next(case for case in scorecard["cases"] if case["id"] == "ascii-constant-value")
        self.assertEqual(ascii_case["comparison"], "pass")
        self.assertEqual(
            ascii_case["observations"]["cpython"]["result"],
            {
                "name": "ASCII",
                "present": True,
                "type_name": "RegexFlag",
                "value": 256,
            },
        )
        self.assertEqual(
            ascii_case["observations"]["rebar"]["result"],
            ascii_case["observations"]["cpython"]["result"],
        )

        pattern_case = next(case for case in scorecard["cases"] if case["id"] == "pattern-type-metadata")
        self.assertEqual(pattern_case["comparison"], "pass")
        self.assertEqual(pattern_case["observations"]["cpython"]["result"]["qualname"], "Pattern")
        self.assertEqual(pattern_case["observations"]["rebar"]["result"]["qualname"], "Pattern")
        self.assertEqual(pattern_case["observations"]["cpython"]["result"]["type_name"], "type")
        self.assertEqual(pattern_case["observations"]["rebar"]["result"]["type_name"], "type")
        self.assertEqual(
            pattern_case["observations"]["rebar"]["result"],
            pattern_case["observations"]["cpython"]["result"],
        )

        constructor_case = next(
            case for case in scorecard["cases"] if case["id"] == "pattern-constructor-guard"
        )
        self.assertEqual(constructor_case["comparison"], "pass")
        self.assertEqual(constructor_case["observations"]["cpython"]["outcome"], "exception")
        self.assertEqual(constructor_case["observations"]["rebar"]["outcome"], "exception")
        self.assertEqual(
            constructor_case["observations"]["cpython"]["exception"]["message"],
            "cannot create 're.Pattern' instances",
        )
        self.assertEqual(
            constructor_case["observations"]["rebar"]["exception"]["message"],
            "cannot create 're.Pattern' instances",
        )


if __name__ == "__main__":
    unittest.main()
