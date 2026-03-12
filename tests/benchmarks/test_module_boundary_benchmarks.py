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
COMPILE_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "compile_matrix.json"
MODULE_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "module_boundary.json"
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "benchmarks" / "latest.json"


class ModuleBoundaryBenchmarkSuiteTest(unittest.TestCase):
    def test_runner_regenerates_combined_phase2_scorecard(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = pathlib.Path(temp_dir) / "benchmarks.json"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "rebar_harness.benchmarks",
                    "--manifest",
                    str(COMPILE_MANIFEST_PATH),
                    "--manifest",
                    str(MODULE_MANIFEST_PATH),
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
                    "known_gap_count": 5,
                    "measured_workloads": 9,
                    "module_workloads": 8,
                    "parser_workloads": 6,
                    "regression_workloads": 0,
                    "total_workloads": 14,
                },
            )

            scorecard = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(scorecard["schema_version"], "1.0")
        self.assertEqual(scorecard["phase"], "phase2-module-boundary-suite")
        self.assertEqual(scorecard["baseline"]["python_implementation"], platform.python_implementation())
        self.assertEqual(scorecard["baseline"]["python_version"], platform.python_version())
        self.assertEqual(scorecard["implementation"]["module_name"], "rebar")
        self.assertEqual(scorecard["implementation"]["adapter"], "rebar.module-surface")
        self.assertEqual(scorecard["implementation"]["adapter_mode_requested"], "source-tree-shim")
        self.assertEqual(scorecard["implementation"]["adapter_mode_resolved"], "source-tree-shim")
        self.assertEqual(scorecard["implementation"]["build_mode"], "source-tree-shim")
        self.assertEqual(scorecard["implementation"]["timing_path"], "source-tree-shim")
        self.assertFalse(scorecard["implementation"]["native_module_loaded"])
        self.assertIn("not requested", scorecard["implementation"]["native_unavailable_reason"])
        self.assertEqual(scorecard["environment"]["runner_version"], "phase2")
        self.assertEqual(scorecard["summary"]["total_workloads"], 14)
        self.assertEqual(scorecard["summary"]["parser_workloads"], 6)
        self.assertEqual(scorecard["summary"]["module_workloads"], 8)
        self.assertEqual(scorecard["summary"]["measured_workloads"], 9)
        self.assertEqual(scorecard["summary"]["known_gap_count"], 5)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["cold"], 7)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["warm"], 5)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["purged"], 2)
        self.assertEqual(scorecard["families"]["parser"]["workload_count"], 6)
        self.assertEqual(scorecard["families"]["parser"]["known_gap_count"], 1)
        self.assertEqual(scorecard["families"]["parser"]["readiness"], "partial")
        self.assertEqual(scorecard["families"]["module"]["workload_count"], 8)
        self.assertEqual(scorecard["families"]["module"]["known_gap_count"], 4)
        self.assertEqual(scorecard["families"]["module"]["readiness"], "partial")
        self.assertEqual(scorecard["families"]["module"]["cache_modes"]["cold"]["workload_count"], 4)
        self.assertEqual(scorecard["families"]["module"]["cache_modes"]["warm"]["workload_count"], 3)
        self.assertEqual(scorecard["families"]["module"]["cache_modes"]["purged"]["workload_count"], 1)
        self.assertEqual(scorecard["artifacts"]["manifest"], None)
        self.assertEqual(scorecard["artifacts"]["manifest_id"], "combined-benchmark-suite")
        self.assertEqual(scorecard["artifacts"]["manifest_schema_version"], 1)
        self.assertEqual(len(scorecard["artifacts"]["manifests"]), 2)
        self.assertEqual(
            scorecard["artifacts"]["manifests"][0]["manifest"],
            "benchmarks/workloads/compile_matrix.json",
        )
        self.assertEqual(
            scorecard["artifacts"]["manifests"][1]["manifest"],
            "benchmarks/workloads/module_boundary.json",
        )
        self.assertEqual(len(scorecard["deferred"]), 1)
        self.assertEqual(scorecard["deferred"][0]["area"], "regex-execution-throughput")
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        import_workload = next(
            workload for workload in scorecard["workloads"] if workload["id"] == "import-module-cold"
        )
        self.assertEqual(import_workload["family"], "module")
        self.assertEqual(import_workload["manifest_id"], "module-boundary")
        self.assertEqual(import_workload["operation"], "import")
        self.assertEqual(import_workload["timing_scope"], "module-import")
        self.assertEqual(import_workload["baseline_timing"]["status"], "measured")
        self.assertEqual(import_workload["implementation_timing"]["status"], "measured")
        self.assertGreater(import_workload["baseline_ns"], 0)
        self.assertGreater(import_workload["implementation_ns"], 0)
        self.assertIsInstance(import_workload["speedup_vs_cpython"], float)

        helper_workload = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-search-literal-cold-miss"
        )
        self.assertEqual(helper_workload["family"], "module")
        self.assertEqual(helper_workload["operation"], "module.search")
        self.assertEqual(helper_workload["cache_mode"], "cold")
        self.assertEqual(helper_workload["haystack"], "zzz")
        self.assertEqual(helper_workload["implementation_timing"]["status"], "unimplemented")
        self.assertIsNone(helper_workload["implementation_ns"])
        self.assertIsNone(helper_workload["speedup_vs_cpython"])

        compile_manifest = scorecard["manifests"]["compile-matrix"]
        self.assertEqual(compile_manifest["measured_workloads"], 5)
        self.assertEqual(compile_manifest["known_gap_count"], 1)
        self.assertEqual(compile_manifest["readiness"], "partial")

        warm_helper = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-search-literal-warm-hit"
        )
        self.assertEqual(warm_helper["status"], "measured")
        self.assertEqual(warm_helper["implementation_timing"]["status"], "measured")
        self.assertGreater(warm_helper["implementation_ns"], 0)

        bytes_workload = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-search-bytes-cold-miss"
        )
        self.assertEqual(bytes_workload["text_model"], "bytes")
        self.assertIn("pattern-text-model", bytes_workload["syntax_features"])
        self.assertEqual(bytes_workload["status"], "measured")


if __name__ == "__main__":
    unittest.main()
