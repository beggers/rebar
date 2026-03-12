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
                    "known_gap_count": 1,
                    "measured_workloads": 1,
                    "module_workloads": 0,
                    "parser_workloads": 2,
                    "regression_workloads": 0,
                    "total_workloads": 2,
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
        self.assertEqual(scorecard["implementation"]["module_name"], "rebar")
        self.assertEqual(scorecard["implementation"]["adapter_mode_requested"], "source-tree-shim")
        self.assertEqual(scorecard["implementation"]["adapter_mode_resolved"], "source-tree-shim")
        self.assertEqual(scorecard["implementation"]["build_mode"], "source-tree-shim")
        self.assertEqual(scorecard["implementation"]["timing_path"], "source-tree-shim")
        self.assertFalse(scorecard["implementation"]["native_module_loaded"])
        self.assertIn("not requested", scorecard["implementation"]["native_unavailable_reason"])
        self.assertEqual(scorecard["summary"]["known_gap_count"], 1)
        self.assertEqual(scorecard["summary"]["total_workloads"], 2)
        self.assertEqual(scorecard["artifacts"]["manifest"], "benchmarks/workloads/compile_smoke.json")
        self.assertEqual(scorecard["deferred"][0]["area"], "module-boundary")
        self.assertEqual(scorecard["deferred"][0]["follow_up"], "RBR-0015")
        self.assertEqual(len(scorecard["workloads"]), 2)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        first_workload = scorecard["workloads"][0]
        self.assertEqual(first_workload["family"], "parser")
        self.assertEqual(first_workload["baseline_timing"]["status"], "measured")
        self.assertGreater(first_workload["baseline_ns"], 0)
        self.assertEqual(first_workload["implementation_timing"]["status"], "measured")
        self.assertGreater(first_workload["implementation_ns"], 0)
        self.assertIsInstance(first_workload["speedup_vs_cpython"], float)


if __name__ == "__main__":
    unittest.main()
