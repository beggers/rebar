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
PATTERN_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "pattern_boundary.json"
REGRESSION_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "regression_matrix.json"
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "benchmarks" / "latest.json"


class PatternBoundaryBenchmarkSuiteTest(unittest.TestCase):
    def test_runner_regenerates_combined_pattern_boundary_scorecard(self) -> None:
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
                    str(PATTERN_MANIFEST_PATH),
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
                    "known_gap_count": 13,
                    "measured_workloads": 12,
                    "module_workloads": 17,
                    "parser_workloads": 8,
                    "regression_workloads": 5,
                    "total_workloads": 25,
                },
            )

            scorecard = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(scorecard["schema_version"], "1.0")
        self.assertEqual(scorecard["phase"], "phase3-regression-stability-suite")
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
        self.assertEqual(scorecard["environment"]["runner_version"], "phase3")
        self.assertEqual(scorecard["summary"]["total_workloads"], 25)
        self.assertEqual(scorecard["summary"]["parser_workloads"], 8)
        self.assertEqual(scorecard["summary"]["module_workloads"], 17)
        self.assertEqual(scorecard["summary"]["regression_workloads"], 5)
        self.assertEqual(scorecard["summary"]["measured_workloads"], 12)
        self.assertEqual(scorecard["summary"]["known_gap_count"], 13)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["cold"], 10)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["warm"], 8)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["purged"], 7)
        self.assertEqual(scorecard["families"]["parser"]["workload_count"], 8)
        self.assertEqual(scorecard["families"]["module"]["workload_count"], 17)
        self.assertEqual(scorecard["families"]["module"]["known_gap_count"], 5)
        self.assertEqual(scorecard["families"]["module"]["readiness"], "partial")
        self.assertEqual(scorecard["families"]["module"]["cache_modes"]["cold"]["workload_count"], 6)
        self.assertEqual(scorecard["families"]["module"]["cache_modes"]["warm"]["workload_count"], 6)
        self.assertEqual(scorecard["families"]["module"]["cache_modes"]["purged"]["workload_count"], 5)
        self.assertEqual(scorecard["artifacts"]["manifest"], None)
        self.assertEqual(scorecard["artifacts"]["manifest_id"], "combined-benchmark-suite")
        self.assertEqual(scorecard["artifacts"]["manifest_schema_version"], 1)
        self.assertEqual(len(scorecard["artifacts"]["manifests"]), 4)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        pattern_manifest = scorecard["manifests"]["pattern-boundary"]
        self.assertEqual(pattern_manifest["workload_count"], 6)
        self.assertEqual(pattern_manifest["selected_workload_count"], 6)
        self.assertEqual(pattern_manifest["measured_workloads"], 6)
        self.assertEqual(pattern_manifest["known_gap_count"], 0)
        self.assertEqual(pattern_manifest["readiness"], "measured")
        self.assertEqual(pattern_manifest["selection_mode"], "full")
        self.assertEqual(pattern_manifest["available_smoke_workload_count"], 2)
        self.assertEqual(
            pattern_manifest["smoke_workload_ids"],
            ["pattern-search-literal-warm-hit", "pattern-fullmatch-bytes-purged-hit"],
        )
        self.assertEqual(
            pattern_manifest["spec_refs"],
            [
                "docs/benchmarks/plan.md",
                "docs/spec/drop-in-re-compatibility.md",
            ],
        )
        self.assertIn("Pattern helper overhead", pattern_manifest["notes"][0])

        pattern_record = next(
            manifest
            for manifest in scorecard["artifacts"]["manifests"]
            if manifest["manifest_id"] == "pattern-boundary"
        )
        self.assertEqual(
            pattern_record["manifest"],
            "benchmarks/workloads/pattern_boundary.json",
        )
        self.assertEqual(
            pattern_record["smoke_workload_ids"],
            ["pattern-search-literal-warm-hit", "pattern-fullmatch-bytes-purged-hit"],
        )

        pattern_search = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "pattern-search-literal-warm-hit"
        )
        self.assertEqual(pattern_search["manifest_id"], "pattern-boundary")
        self.assertEqual(pattern_search["family"], "module")
        self.assertEqual(pattern_search["operation"], "pattern.search")
        self.assertEqual(pattern_search["cache_mode"], "warm")
        self.assertEqual(pattern_search["timing_scope"], "pattern-helper-call")
        self.assertEqual(pattern_search["status"], "measured")
        self.assertEqual(pattern_search["implementation_timing"]["status"], "measured")
        self.assertGreater(pattern_search["baseline_ns"], 0)
        self.assertGreater(pattern_search["implementation_ns"], 0)
        self.assertIsInstance(pattern_search["speedup_vs_cpython"], float)

        pattern_bytes = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "pattern-fullmatch-bytes-purged-hit"
        )
        self.assertEqual(pattern_bytes["text_model"], "bytes")
        self.assertEqual(pattern_bytes["cache_mode"], "purged")
        self.assertIn("pattern-text-model", pattern_bytes["syntax_features"])
        self.assertEqual(pattern_bytes["implementation_timing"]["status"], "measured")


if __name__ == "__main__":
    unittest.main()
