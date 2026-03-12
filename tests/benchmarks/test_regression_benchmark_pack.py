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
REGRESSION_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "regression_matrix.json"
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "benchmarks" / "latest.json"


class RegressionBenchmarkPackTest(unittest.TestCase):
    def test_runner_regenerates_combined_phase3_scorecard(self) -> None:
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
                    "--manifest",
                    str(REGRESSION_MANIFEST_PATH),
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
                    "known_gap_count": 17,
                    "measured_workloads": 2,
                    "module_workloads": 11,
                    "parser_workloads": 8,
                    "regression_workloads": 5,
                    "total_workloads": 19,
                },
            )

            scorecard = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(scorecard["schema_version"], "1.0")
        self.assertEqual(scorecard["phase"], "phase3-regression-stability-suite")
        self.assertEqual(scorecard["baseline"]["python_implementation"], platform.python_implementation())
        self.assertEqual(scorecard["baseline"]["python_version"], platform.python_version())
        self.assertEqual(scorecard["implementation"]["module_name"], "rebar")
        self.assertEqual(scorecard["implementation"]["adapter_mode_requested"], "source-tree-shim")
        self.assertEqual(scorecard["implementation"]["adapter_mode_resolved"], "source-tree-shim")
        self.assertEqual(scorecard["implementation"]["build_mode"], "source-tree-shim")
        self.assertEqual(scorecard["implementation"]["timing_path"], "source-tree-shim")
        self.assertFalse(scorecard["implementation"]["native_module_loaded"])
        self.assertIn("not requested", scorecard["implementation"]["native_unavailable_reason"])
        self.assertEqual(scorecard["environment"]["runner_version"], "phase3")
        self.assertEqual(scorecard["summary"]["total_workloads"], 19)
        self.assertEqual(scorecard["summary"]["parser_workloads"], 8)
        self.assertEqual(scorecard["summary"]["module_workloads"], 11)
        self.assertEqual(scorecard["summary"]["regression_workloads"], 5)
        self.assertEqual(scorecard["summary"]["measured_workloads"], 2)
        self.assertEqual(scorecard["summary"]["known_gap_count"], 17)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["cold"], 10)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["warm"], 5)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["purged"], 4)
        self.assertEqual(scorecard["families"]["parser"]["workload_count"], 8)
        self.assertEqual(scorecard["families"]["module"]["workload_count"], 11)
        self.assertEqual(scorecard["artifacts"]["manifest_id"], "combined-benchmark-suite")
        self.assertEqual(scorecard["artifacts"]["selection_mode"], "full")
        self.assertEqual(len(scorecard["artifacts"]["manifests"]), 3)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        regression_manifest = scorecard["manifests"]["regression-matrix"]
        self.assertEqual(regression_manifest["workload_count"], 5)
        self.assertEqual(regression_manifest["selected_workload_count"], 5)
        self.assertEqual(regression_manifest["measured_workloads"], 1)
        self.assertEqual(regression_manifest["known_gap_count"], 4)
        self.assertEqual(regression_manifest["readiness"], "partial")
        self.assertEqual(regression_manifest["selection_mode"], "full")
        self.assertEqual(regression_manifest["available_smoke_workload_count"], 2)
        self.assertEqual(
            regression_manifest["smoke_workload_ids"],
            ["regression-import-cold", "regression-parser-atomic-lookbehind-cold"],
        )
        self.assertEqual(
            regression_manifest["spec_refs"],
            [
                "docs/benchmarks/plan.md",
                "docs/spec/syntax-scope.md",
                "docs/spec/drop-in-re-compatibility.md",
            ],
        )

        regression_record = next(
            manifest
            for manifest in scorecard["artifacts"]["manifests"]
            if manifest["manifest_id"] == "regression-matrix"
        )
        self.assertEqual(
            regression_record["manifest"],
            "benchmarks/workloads/regression_matrix.json",
        )
        self.assertEqual(
            regression_record["smoke_workload_ids"],
            ["regression-import-cold", "regression-parser-atomic-lookbehind-cold"],
        )

        import_workload = next(
            workload for workload in scorecard["workloads"] if workload["id"] == "regression-import-cold"
        )
        self.assertEqual(import_workload["manifest_id"], "regression-matrix")
        self.assertEqual(import_workload["family"], "module")
        self.assertEqual(import_workload["operation"], "import")
        self.assertEqual(import_workload["status"], "measured")
        self.assertGreater(import_workload["implementation_ns"], 0)
        self.assertIsInstance(import_workload["speedup_vs_cpython"], float)

        parser_workload = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "regression-parser-bytes-backreference-purged"
        )
        self.assertEqual(parser_workload["family"], "parser")
        self.assertEqual(parser_workload["text_model"], "bytes")
        self.assertEqual(parser_workload["cache_mode"], "purged")
        self.assertEqual(parser_workload["implementation_timing"]["status"], "unimplemented")
        self.assertIsNone(parser_workload["speedup_vs_cpython"])

    def test_runner_can_execute_smoke_subset_for_regression_pack(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = pathlib.Path(temp_dir) / "benchmarks-smoke.json"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "rebar_harness.benchmarks",
                    "--manifest",
                    str(REGRESSION_MANIFEST_PATH),
                    "--smoke",
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
                    "module_workloads": 1,
                    "parser_workloads": 1,
                    "regression_workloads": 2,
                    "total_workloads": 2,
                },
            )

            scorecard = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(scorecard["phase"], "phase3-regression-stability-suite")
        self.assertEqual(scorecard["environment"]["runner_version"], "phase3")
        self.assertEqual(scorecard["implementation"]["adapter_mode_requested"], "source-tree-shim")
        self.assertEqual(scorecard["implementation"]["adapter_mode_resolved"], "source-tree-shim")
        self.assertEqual(scorecard["artifacts"]["selection_mode"], "smoke")
        self.assertEqual(scorecard["artifacts"]["manifest"], "benchmarks/workloads/regression_matrix.json")
        self.assertEqual(scorecard["summary"]["total_workloads"], 2)
        self.assertEqual(scorecard["summary"]["parser_workloads"], 1)
        self.assertEqual(scorecard["summary"]["module_workloads"], 1)
        self.assertEqual(scorecard["summary"]["regression_workloads"], 2)
        self.assertEqual(scorecard["summary"]["measured_workloads"], 1)
        self.assertEqual(scorecard["summary"]["known_gap_count"], 1)
        self.assertEqual(
            [workload["id"] for workload in scorecard["workloads"]],
            ["regression-import-cold", "regression-parser-atomic-lookbehind-cold"],
        )
        self.assertEqual(scorecard["manifests"]["regression-matrix"]["selected_workload_count"], 2)
        self.assertEqual(scorecard["manifests"]["regression-matrix"]["selection_mode"], "smoke")


if __name__ == "__main__":
    unittest.main()
