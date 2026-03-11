from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "compile_smoke.json"
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "benchmarks" / "latest.json"


class BenchmarkHarnessSmokeTest(unittest.TestCase):
    def test_runner_regenerates_smoke_scorecard(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = pathlib.Path(temp_dir) / "benchmarks.json"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "rebar_harness.benchmarks",
                    "--manifest",
                    str(MANIFEST_PATH),
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
                    "known_gap_count": 2,
                    "measured_workloads": 0,
                    "module_workloads": 0,
                    "parser_workloads": 2,
                    "total_workloads": 2,
                },
            )

            scorecard = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(scorecard["schema_version"], "1.0")
        self.assertEqual(scorecard["baseline"]["python_version_family"], "3.12.x")
        self.assertEqual(scorecard["implementation"]["module_name"], "rebar")
        self.assertEqual(scorecard["summary"]["known_gap_count"], 2)
        self.assertEqual(scorecard["summary"]["total_workloads"], 2)
        self.assertEqual(scorecard["artifacts"]["manifest"], "benchmarks/workloads/compile_smoke.json")
        self.assertEqual(len(scorecard["workloads"]), 2)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        first_workload = scorecard["workloads"][0]
        self.assertEqual(first_workload["family"], "parser")
        self.assertEqual(first_workload["baseline_timing"]["status"], "measured")
        self.assertGreater(first_workload["baseline_ns"], 0)
        self.assertEqual(first_workload["implementation_timing"]["status"], "unimplemented")
        self.assertIsNone(first_workload["implementation_ns"])
        self.assertIsNone(first_workload["speedup_vs_cpython"])


if __name__ == "__main__":
    unittest.main()
