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
REGRESSION_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "regression_matrix.json"
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "benchmarks" / "latest.json"


class CollectionReplacementBoundaryBenchmarkSuiteTest(unittest.TestCase):
    def test_runner_regenerates_combined_collection_replacement_scorecard(self) -> None:
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
                    "measured_workloads": 22,
                    "module_workloads": 27,
                    "parser_workloads": 8,
                    "regression_workloads": 5,
                    "total_workloads": 35,
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
        self.assertEqual(scorecard["summary"]["total_workloads"], 35)
        self.assertEqual(scorecard["summary"]["parser_workloads"], 8)
        self.assertEqual(scorecard["summary"]["module_workloads"], 27)
        self.assertEqual(scorecard["summary"]["regression_workloads"], 5)
        self.assertEqual(scorecard["summary"]["measured_workloads"], 22)
        self.assertEqual(scorecard["summary"]["known_gap_count"], 13)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["cold"], 10)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["warm"], 13)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["purged"], 12)
        self.assertEqual(scorecard["families"]["parser"]["workload_count"], 8)
        self.assertEqual(scorecard["families"]["module"]["workload_count"], 27)
        self.assertEqual(scorecard["families"]["module"]["known_gap_count"], 5)
        self.assertEqual(scorecard["families"]["module"]["readiness"], "partial")
        self.assertEqual(scorecard["families"]["module"]["cache_modes"]["cold"]["workload_count"], 6)
        self.assertEqual(scorecard["families"]["module"]["cache_modes"]["warm"]["workload_count"], 11)
        self.assertEqual(scorecard["families"]["module"]["cache_modes"]["purged"]["workload_count"], 10)
        self.assertEqual(scorecard["artifacts"]["manifest"], None)
        self.assertEqual(scorecard["artifacts"]["manifest_id"], "combined-benchmark-suite")
        self.assertEqual(scorecard["artifacts"]["manifest_schema_version"], 1)
        self.assertEqual(scorecard["artifacts"]["selection_mode"], "full")
        self.assertEqual(len(scorecard["artifacts"]["manifests"]), 5)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        manifest_summary = scorecard["manifests"]["collection-replacement-boundary"]
        self.assertEqual(manifest_summary["workload_count"], 10)
        self.assertEqual(manifest_summary["selected_workload_count"], 10)
        self.assertEqual(manifest_summary["measured_workloads"], 10)
        self.assertEqual(manifest_summary["known_gap_count"], 0)
        self.assertEqual(manifest_summary["readiness"], "measured")
        self.assertEqual(manifest_summary["selection_mode"], "full")
        self.assertEqual(manifest_summary["available_smoke_workload_count"], 2)
        self.assertEqual(
            manifest_summary["smoke_workload_ids"],
            ["module-split-literal-warm-str", "pattern-subn-literal-purged-bytes"],
        )
        self.assertEqual(
            manifest_summary["operations"],
            [
                "module.findall",
                "module.split",
                "module.sub",
                "pattern.finditer",
                "pattern.subn",
            ],
        )
        self.assertEqual(
            manifest_summary["spec_refs"],
            [
                "docs/benchmarks/plan.md",
                "docs/spec/drop-in-re-compatibility.md",
            ],
        )
        self.assertIn("helper-call overhead", manifest_summary["notes"][0])

        manifest_record = next(
            manifest
            for manifest in scorecard["artifacts"]["manifests"]
            if manifest["manifest_id"] == "collection-replacement-boundary"
        )
        self.assertEqual(
            manifest_record["manifest"],
            "benchmarks/workloads/collection_replacement_boundary.json",
        )
        self.assertEqual(
            manifest_record["smoke_workload_ids"],
            ["module-split-literal-warm-str", "pattern-subn-literal-purged-bytes"],
        )

        module_split = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-split-literal-warm-str"
        )
        self.assertEqual(module_split["manifest_id"], "collection-replacement-boundary")
        self.assertEqual(module_split["family"], "module")
        self.assertEqual(module_split["operation"], "module.split")
        self.assertEqual(module_split["cache_mode"], "warm")
        self.assertEqual(module_split["text_model"], "str")
        self.assertEqual(module_split["status"], "measured")
        self.assertEqual(module_split["implementation_timing"]["status"], "measured")
        self.assertGreater(module_split["implementation_ns"], 0)
        self.assertIsInstance(module_split["speedup_vs_cpython"], float)

        module_sub_bytes = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-sub-literal-purged-bytes"
        )
        self.assertEqual(module_sub_bytes["text_model"], "bytes")
        self.assertEqual(module_sub_bytes["count"], 1)
        self.assertEqual(module_sub_bytes["replacement"], "XY")
        self.assertEqual(module_sub_bytes["status"], "measured")

        pattern_finditer = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "pattern-finditer-literal-warm-str"
        )
        self.assertEqual(pattern_finditer["operation"], "pattern.finditer")
        self.assertEqual(pattern_finditer["timing_scope"], "pattern-helper-call")
        self.assertEqual(pattern_finditer["status"], "measured")
        self.assertEqual(pattern_finditer["implementation_timing"]["status"], "measured")
        self.assertGreater(pattern_finditer["baseline_ns"], 0)
        self.assertGreater(pattern_finditer["implementation_ns"], 0)

        pattern_subn_bytes = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "pattern-subn-literal-purged-bytes"
        )
        self.assertEqual(pattern_subn_bytes["text_model"], "bytes")
        self.assertEqual(pattern_subn_bytes["cache_mode"], "purged")
        self.assertEqual(pattern_subn_bytes["count"], 1)
        self.assertEqual(pattern_subn_bytes["implementation_timing"]["status"], "measured")


if __name__ == "__main__":
    unittest.main()
