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
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.py"


class CorrectnessHarnessMatchBehaviorTest(unittest.TestCase):
    def test_runner_regenerates_combined_match_behavior_scorecard(self) -> None:
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
        self.assertEqual(scorecard["fixtures"]["manifest_count"], 3)
        self.assertEqual(
            scorecard["fixtures"]["manifest_ids"],
            ["parser-matrix", "public-api-surface", "match-behavior-smoke"],
        )
        self.assertEqual(len(scorecard["cases"]), 28)
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

        match_layer = assert_correctness_layer_summary_consistent(
            self,
            scorecard,
            "match_behavior",
        )
        self.assertEqual(match_layer["summary"]["total_cases"], 6)
        self.assertEqual(match_layer["summary"]["passed_cases"], 6)
        self.assertEqual(match_layer["summary"]["unimplemented_cases"], 0)
        self.assertEqual(match_layer["operations"], ["module_call"])
        self.assertEqual(match_layer["text_models"], ["bytes", "str"])

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
            ],
        )

        match_suite = assert_correctness_suite_summary_consistent(
            self,
            scorecard,
            "match.behavior",
        )
        self.assertEqual(match_suite["summary"]["total_cases"], 6)
        self.assertEqual(match_suite["summary"]["passed_cases"], 6)
        self.assertEqual(match_suite["summary"]["unimplemented_cases"], 0)
        self.assertEqual(
            match_suite["families"],
            ["fullmatch_result_shape", "match_result_shape", "search_result_shape"],
        )

        bytes_suite = assert_correctness_suite_summary_consistent(
            self,
            scorecard,
            "match.behavior.bytes",
        )
        self.assertEqual(bytes_suite["summary"]["total_cases"], 1)
        self.assertEqual(bytes_suite["summary"]["passed_cases"], 1)

        search_case = next(case for case in scorecard["cases"] if case["id"] == "search-str-success-literal")
        self.assertEqual(search_case["layer"], "match_behavior")
        self.assertEqual(search_case["helper"], "search")
        self.assertEqual(search_case["comparison"], "pass")
        self.assertEqual(search_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(search_case["observations"]["cpython"]["result"]["matched"], True)
        self.assertEqual(search_case["observations"]["cpython"]["result"]["group0"], "abc")
        self.assertEqual(search_case["observations"]["cpython"]["result"]["groups"], [])
        self.assertEqual(search_case["observations"]["cpython"]["result"]["groupdict"], {})
        self.assertEqual(search_case["observations"]["cpython"]["result"]["span"], [2, 5])
        self.assertEqual(search_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(
            search_case["observations"]["rebar"]["result"],
            search_case["observations"]["cpython"]["result"],
        )

        no_match_case = next(case for case in scorecard["cases"] if case["id"] == "match-str-no-match")
        self.assertEqual(no_match_case["comparison"], "pass")
        self.assertEqual(no_match_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(no_match_case["observations"]["cpython"]["result"], None)
        self.assertEqual(no_match_case["observations"]["rebar"]["result"], None)

        bytes_case = next(
            case for case in scorecard["cases"] if case["id"] == "fullmatch-bytes-success-literal"
        )
        self.assertEqual(bytes_case["text_model"], "bytes")
        self.assertEqual(bytes_case["comparison"], "pass")
        self.assertEqual(bytes_case["observations"]["cpython"]["result"]["matched"], True)
        self.assertEqual(
            bytes_case["observations"]["cpython"]["result"]["group0"],
            {"encoding": "latin-1", "value": "123"},
        )
        self.assertEqual(bytes_case["observations"]["cpython"]["result"]["groups"], [])
        self.assertEqual(bytes_case["observations"]["cpython"]["result"]["groupdict"], {})
        self.assertEqual(bytes_case["observations"]["cpython"]["result"]["string_type"], "bytes")
        self.assertEqual(
            bytes_case["observations"]["rebar"]["result"],
            bytes_case["observations"]["cpython"]["result"],
        )


if __name__ == "__main__":
    unittest.main()
