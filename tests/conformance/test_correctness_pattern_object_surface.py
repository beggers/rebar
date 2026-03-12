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
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.json"


class CorrectnessHarnessPatternObjectSurfaceTest(unittest.TestCase):
    def test_runner_regenerates_combined_pattern_object_scorecard(self) -> None:
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
                    "executed_cases": 44,
                    "failed_cases": 0,
                    "passed_cases": 31,
                    "skipped_cases": 0,
                    "total_cases": 44,
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
        self.assertEqual(scorecard["fixtures"]["manifest_count"], 5)
        self.assertEqual(
            scorecard["fixtures"]["manifest_ids"],
            [
                "parser-matrix",
                "public-api-surface",
                "match-behavior-smoke",
                "exported-symbol-surface",
                "pattern-object-surface",
            ],
        )
        self.assertEqual(len(scorecard["cases"]), 44)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        pattern_layer = scorecard["layers"]["pattern_object_parity"]
        self.assertEqual(pattern_layer["summary"]["total_cases"], 6)
        self.assertEqual(pattern_layer["summary"]["passed_cases"], 6)
        self.assertEqual(pattern_layer["summary"]["failed_cases"], 0)
        self.assertEqual(pattern_layer["summary"]["unimplemented_cases"], 0)
        self.assertEqual(pattern_layer["operations"], ["pattern_call", "pattern_metadata"])
        self.assertEqual(pattern_layer["text_models"], ["bytes", "str"])

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
            ],
        )

        pattern_suite = next(suite for suite in scorecard["suites"] if suite["id"] == "pattern.object")
        self.assertEqual(pattern_suite["summary"]["total_cases"], 6)
        self.assertEqual(pattern_suite["summary"]["failed_cases"], 0)
        self.assertEqual(pattern_suite["summary"]["passed_cases"], 6)
        self.assertEqual(pattern_suite["summary"]["unimplemented_cases"], 0)
        self.assertEqual(
            pattern_suite["families"],
            ["compiled_pattern_literal_behavior", "compiled_pattern_metadata"],
        )

        metadata_case = next(
            case for case in scorecard["cases"] if case["id"] == "pattern-object-str-metadata"
        )
        self.assertEqual(metadata_case["comparison"], "pass")
        self.assertEqual(metadata_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(metadata_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(
            metadata_case["observations"]["cpython"]["result"]["compiled_type"]["module"],
            "re",
        )
        self.assertEqual(
            metadata_case["observations"]["rebar"]["result"]["compiled_type"]["module"],
            "re",
        )
        self.assertEqual(
            metadata_case["observations"]["cpython"]["result"]["pattern"],
            "abc",
        )
        self.assertEqual(
            metadata_case["observations"]["rebar"]["result"]["pattern"],
            "abc",
        )
        self.assertEqual(metadata_case["observations"]["cpython"]["result"]["flags"], 32)
        self.assertEqual(metadata_case["observations"]["rebar"]["result"]["flags"], 32)
        self.assertEqual(
            metadata_case["observations"]["rebar"]["result"],
            metadata_case["observations"]["cpython"]["result"],
        )

        bytes_metadata_case = next(
            case
            for case in scorecard["cases"]
            if case["id"] == "pattern-object-bytes-ignorecase-metadata"
        )
        self.assertEqual(bytes_metadata_case["comparison"], "pass")
        self.assertEqual(bytes_metadata_case["text_model"], "bytes")
        self.assertEqual(
            bytes_metadata_case["observations"]["cpython"]["result"]["pattern"],
            {"encoding": "latin-1", "value": "abc"},
        )
        self.assertEqual(
            bytes_metadata_case["observations"]["rebar"]["result"]["pattern"],
            {"encoding": "latin-1", "value": "abc"},
        )
        self.assertEqual(bytes_metadata_case["observations"]["cpython"]["result"]["flags"], 2)
        self.assertEqual(bytes_metadata_case["observations"]["rebar"]["result"]["flags"], 2)
        self.assertEqual(
            bytes_metadata_case["observations"]["rebar"]["result"],
            bytes_metadata_case["observations"]["cpython"]["result"],
        )

        literal_case = next(
            case for case in scorecard["cases"] if case["id"] == "pattern-search-literal-success"
        )
        self.assertEqual(literal_case["comparison"], "pass")
        self.assertEqual(literal_case["helper"], "search")
        self.assertEqual(literal_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(
            literal_case["observations"]["cpython"]["result"]["group0"],
            "abc",
        )
        self.assertEqual(literal_case["observations"]["cpython"]["result"]["span"], [2, 5])
        self.assertEqual(literal_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(
            literal_case["observations"]["rebar"]["result"],
            literal_case["observations"]["cpython"]["result"],
        )


if __name__ == "__main__":
    unittest.main()
