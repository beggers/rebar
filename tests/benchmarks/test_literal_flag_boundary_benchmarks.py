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
COLLECTION_REPLACEMENT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "collection_replacement_boundary.json"
)
LITERAL_FLAG_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "literal_flag_boundary.json"
REGRESSION_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "regression_matrix.json"
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "benchmarks" / "latest.json"


class LiteralFlagBoundaryBenchmarkSuiteTest(unittest.TestCase):
    def test_runner_regenerates_combined_literal_flag_scorecard(self) -> None:
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
                    str(COLLECTION_REPLACEMENT_MANIFEST_PATH),
                    "--manifest",
                    str(LITERAL_FLAG_MANIFEST_PATH),
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
                    "known_gap_count": 15,
                    "measured_workloads": 30,
                    "module_workloads": 37,
                    "parser_workloads": 8,
                    "regression_workloads": 5,
                    "total_workloads": 45,
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
        self.assertEqual(scorecard["summary"]["total_workloads"], 45)
        self.assertEqual(scorecard["summary"]["parser_workloads"], 8)
        self.assertEqual(scorecard["summary"]["module_workloads"], 37)
        self.assertEqual(scorecard["summary"]["regression_workloads"], 5)
        self.assertEqual(scorecard["summary"]["measured_workloads"], 30)
        self.assertEqual(scorecard["summary"]["known_gap_count"], 15)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["cold"], 11)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["warm"], 18)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["purged"], 16)
        self.assertEqual(scorecard["families"]["parser"]["workload_count"], 8)
        self.assertEqual(scorecard["families"]["module"]["workload_count"], 37)
        self.assertEqual(scorecard["families"]["module"]["known_gap_count"], 7)
        self.assertEqual(scorecard["families"]["module"]["readiness"], "partial")
        self.assertEqual(scorecard["families"]["module"]["cache_modes"]["cold"]["workload_count"], 7)
        self.assertEqual(scorecard["families"]["module"]["cache_modes"]["warm"]["workload_count"], 16)
        self.assertEqual(scorecard["families"]["module"]["cache_modes"]["purged"]["workload_count"], 14)
        self.assertEqual(scorecard["artifacts"]["manifest"], None)
        self.assertEqual(scorecard["artifacts"]["manifest_id"], "combined-benchmark-suite")
        self.assertEqual(scorecard["artifacts"]["manifest_schema_version"], 1)
        self.assertEqual(scorecard["artifacts"]["selection_mode"], "full")
        self.assertEqual(len(scorecard["artifacts"]["manifests"]), 6)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        manifest_summary = scorecard["manifests"]["literal-flag-boundary"]
        self.assertEqual(manifest_summary["workload_count"], 10)
        self.assertEqual(manifest_summary["selected_workload_count"], 10)
        self.assertEqual(manifest_summary["measured_workloads"], 8)
        self.assertEqual(manifest_summary["known_gap_count"], 2)
        self.assertEqual(manifest_summary["readiness"], "partial")
        self.assertEqual(manifest_summary["selection_mode"], "full")
        self.assertEqual(manifest_summary["available_smoke_workload_count"], 2)
        self.assertEqual(
            manifest_summary["smoke_workload_ids"],
            ["module-search-ignorecase-warm-str-hit", "pattern-fullmatch-ignorecase-purged-bytes-hit"],
        )
        self.assertEqual(
            manifest_summary["operations"],
            [
                "module.match",
                "module.search",
                "pattern.fullmatch",
                "pattern.search",
            ],
        )
        self.assertEqual(
            manifest_summary["spec_refs"],
            [
                "docs/benchmarks/plan.md",
                "docs/spec/drop-in-re-compatibility.md",
            ],
        )
        self.assertIn("API-level IGNORECASE helper-call overhead", manifest_summary["notes"][0])

        manifest_record = next(
            manifest
            for manifest in scorecard["artifacts"]["manifests"]
            if manifest["manifest_id"] == "literal-flag-boundary"
        )
        self.assertEqual(
            manifest_record["manifest"],
            "benchmarks/workloads/literal_flag_boundary.json",
        )
        self.assertEqual(
            manifest_record["smoke_workload_ids"],
            ["module-search-ignorecase-warm-str-hit", "pattern-fullmatch-ignorecase-purged-bytes-hit"],
        )

        module_search = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-search-ignorecase-warm-str-hit"
        )
        self.assertEqual(module_search["manifest_id"], "literal-flag-boundary")
        self.assertEqual(module_search["family"], "module")
        self.assertEqual(module_search["operation"], "module.search")
        self.assertEqual(module_search["flags"], 2)
        self.assertEqual(module_search["cache_mode"], "warm")
        self.assertEqual(module_search["status"], "measured")
        self.assertEqual(module_search["implementation_timing"]["status"], "measured")
        self.assertGreater(module_search["baseline_ns"], 0)
        self.assertGreater(module_search["implementation_ns"], 0)
        self.assertIsInstance(module_search["speedup_vs_cpython"], float)

        bytes_pattern = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "pattern-fullmatch-ignorecase-purged-bytes-hit"
        )
        self.assertEqual(bytes_pattern["text_model"], "bytes")
        self.assertEqual(bytes_pattern["cache_mode"], "purged")
        self.assertIn("api-level-ignorecase", bytes_pattern["syntax_features"])
        self.assertEqual(bytes_pattern["status"], "measured")
        self.assertEqual(bytes_pattern["implementation_timing"]["status"], "measured")

        module_gap = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-search-ignorecase-ascii-cold-gap"
        )
        self.assertEqual(module_gap["flags"], 258)
        self.assertEqual(module_gap["cache_mode"], "cold")
        self.assertEqual(module_gap["status"], "unimplemented")
        self.assertEqual(module_gap["implementation_timing"]["status"], "unimplemented")
        self.assertIsNone(module_gap["implementation_ns"])
        self.assertIsNone(module_gap["speedup_vs_cpython"])

        pattern_gap = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "pattern-search-ignorecase-ascii-warm-gap"
        )
        self.assertEqual(pattern_gap["operation"], "pattern.search")
        self.assertEqual(pattern_gap["flags"], 258)
        self.assertEqual(pattern_gap["status"], "unimplemented")
        self.assertEqual(pattern_gap["implementation_timing"]["status"], "unimplemented")
        self.assertIsNone(pattern_gap["speedup_vs_cpython"])


if __name__ == "__main__":
    unittest.main()
