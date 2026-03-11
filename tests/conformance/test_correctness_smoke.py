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
FIXTURES_PATH = REPO_ROOT / "tests" / "conformance" / "fixtures" / "parser_smoke.json"
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.json"


class CorrectnessHarnessSmokeTest(unittest.TestCase):
    def test_runner_regenerates_smoke_scorecard(self) -> None:
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
                    "executed_cases": 2,
                    "failed_cases": 0,
                    "passed_cases": 0,
                    "skipped_cases": 0,
                    "total_cases": 2,
                    "unimplemented_cases": 2,
                },
            )

            scorecard = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(scorecard["schema_version"], "1.0")
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
        self.assertEqual(scorecard["fixtures"]["manifest_id"], "parser-smoke")
        self.assertEqual(scorecard["summary"], summary)
        self.assertEqual(len(scorecard["cases"]), 2)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        first_case = scorecard["cases"][0]
        self.assertEqual(first_case["comparison"], "unimplemented")
        self.assertEqual(first_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(first_case["observations"]["rebar"]["outcome"], "unimplemented")

        second_case = scorecard["cases"][1]
        self.assertEqual(second_case["comparison"], "unimplemented")
        self.assertEqual(second_case["observations"]["cpython"]["outcome"], "exception")
        self.assertEqual(second_case["observations"]["rebar"]["outcome"], "unimplemented")


if __name__ == "__main__":
    unittest.main()
