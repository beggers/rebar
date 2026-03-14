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
FIXTURES_PATH = REPO_ROOT / "tests" / "conformance" / "fixtures" / "parser_matrix.py"
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.json"


class CorrectnessHarnessParserMatrixTest(unittest.TestCase):
    def test_runner_regenerates_parser_matrix_scorecard(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = pathlib.Path(temp_dir) / "correctness.json"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "rebar_harness.correctness",
                    "--fixtures",
                    str(FIXTURES_PATH),
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
                    "executed_cases": 15,
                    "failed_cases": 0,
                    "passed_cases": 15,
                    "skipped_cases": 0,
                    "total_cases": 15,
                    "unimplemented_cases": 0,
                },
            )

            scorecard = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(scorecard["schema_version"], "1.0")
        self.assertEqual(scorecard["phase"], "phase1-parser-conformance-pack")
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
        self.assertEqual(scorecard["fixtures"]["manifest_id"], "parser-matrix")
        self.assertEqual(scorecard["fixtures"]["case_count"], 15)
        self.assertEqual(scorecard["summary"], summary)
        self.assertEqual(len(scorecard["cases"]), 15)
        self.assertEqual(len(scorecard["suites"]), 3)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        overall_suite = scorecard["suites"][0]
        self.assertEqual(overall_suite["id"], "parser.compile")
        self.assertEqual(overall_suite["case_count"], 15)
        self.assertEqual(overall_suite["text_models"], ["bytes", "str"])
        self.assertEqual(
            overall_suite["families"],
            [
                "assertions",
                "character_classes",
                "flags",
                "grouping",
                "literals_and_escapes",
                "pattern_text_model",
                "quantifiers",
            ],
        )

        cpython_diagnostics = scorecard["diagnostics"]["by_adapter"]["cpython"]
        self.assertEqual(cpython_diagnostics["outcomes"], {"exception": 6, "success": 9})
        self.assertEqual(cpython_diagnostics["warning_case_count"], 1)
        self.assertEqual(cpython_diagnostics["warning_categories"], {"FutureWarning": 1})
        self.assertEqual(cpython_diagnostics["exception_types"], {"error": 6})

        rebar_diagnostics = scorecard["diagnostics"]["by_adapter"]["rebar"]
        self.assertEqual(rebar_diagnostics["outcomes"], {"exception": 6, "success": 9})
        self.assertEqual(rebar_diagnostics["warning_case_count"], 1)
        self.assertEqual(rebar_diagnostics["warning_categories"], {"FutureWarning": 1})
        self.assertEqual(rebar_diagnostics["exception_case_count"], 6)
        self.assertEqual(rebar_diagnostics["exception_types"], {"error": 6})

        str_suite = next(suite for suite in scorecard["suites"] if suite["id"] == "parser.compile.str")
        self.assertEqual(str_suite["summary"]["total_cases"], 11)
        self.assertEqual(str_suite["summary"]["passed_cases"], 11)

        bytes_suite = next(
            suite for suite in scorecard["suites"] if suite["id"] == "parser.compile.bytes"
        )
        self.assertEqual(bytes_suite["summary"]["total_cases"], 4)
        self.assertEqual(bytes_suite["summary"]["passed_cases"], 4)

        first_str_case = next(case for case in scorecard["cases"] if case["id"] == "str-literal-success")
        self.assertEqual(first_str_case["comparison"], "pass")
        self.assertEqual(first_str_case["observations"]["rebar"]["outcome"], "success")

        str_inline_case = next(
            case for case in scorecard["cases"] if case["id"] == "str-inline-unicode-flag-success"
        )
        self.assertEqual(str_inline_case["comparison"], "pass")
        self.assertEqual(str_inline_case["observations"]["rebar"]["outcome"], "success")

        str_character_class_case = next(
            case for case in scorecard["cases"] if case["id"] == "str-character-class-ignorecase-success"
        )
        self.assertEqual(str_character_class_case["comparison"], "pass")
        self.assertEqual(str_character_class_case["observations"]["rebar"]["outcome"], "success")

        str_possessive_case = next(
            case for case in scorecard["cases"] if case["id"] == "str-possessive-quantifier-success"
        )
        self.assertEqual(str_possessive_case["comparison"], "pass")
        self.assertEqual(str_possessive_case["observations"]["rebar"]["outcome"], "success")

        str_atomic_case = next(
            case for case in scorecard["cases"] if case["id"] == "str-atomic-group-success"
        )
        self.assertEqual(str_atomic_case["comparison"], "pass")
        self.assertEqual(str_atomic_case["observations"]["rebar"]["outcome"], "success")

        str_lookbehind_success_case = next(
            case for case in scorecard["cases"] if case["id"] == "str-fixed-width-lookbehind-success"
        )
        self.assertEqual(str_lookbehind_success_case["comparison"], "pass")
        self.assertEqual(str_lookbehind_success_case["observations"]["rebar"]["outcome"], "success")

        str_lookbehind_error_case = next(
            case for case in scorecard["cases"] if case["id"] == "str-variable-width-lookbehind-error"
        )
        self.assertEqual(str_lookbehind_error_case["comparison"], "pass")
        self.assertEqual(str_lookbehind_error_case["observations"]["rebar"]["outcome"], "exception")
        self.assertEqual(
            str_lookbehind_error_case["observations"]["rebar"]["exception"]["message"],
            "look-behind requires fixed-width pattern",
        )

        bytes_locale_case = next(
            case for case in scorecard["cases"] if case["id"] == "bytes-inline-locale-flag-success"
        )
        self.assertEqual(bytes_locale_case["comparison"], "pass")
        self.assertEqual(bytes_locale_case["observations"]["rebar"]["outcome"], "success")

        first_bytes_case = next(
            case for case in scorecard["cases"] if case["id"] == "bytes-inline-unicode-flag-error"
        )
        self.assertEqual(first_bytes_case["text_model"], "bytes")
        self.assertEqual(first_bytes_case["comparison"], "pass")
        self.assertEqual(first_bytes_case["observations"]["cpython"]["outcome"], "exception")
        self.assertEqual(first_bytes_case["observations"]["rebar"]["outcome"], "exception")
        self.assertEqual(
            first_bytes_case["observations"]["cpython"]["exception"]["message"],
            "bad inline flags: cannot use 'u' flag with a bytes pattern at position 3",
        )


if __name__ == "__main__":
    unittest.main()
