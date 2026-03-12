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
GROUPED_NAMED_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_named_boundary.json"
)
NUMBERED_BACKREFERENCE_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "numbered_backreference_boundary.json"
)
GROUPED_SEGMENT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_segment_boundary.json"
)
LITERAL_ALTERNATION_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "literal_alternation_boundary.json"
)
GROUPED_ALTERNATION_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_alternation_boundary.json"
)
GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_alternation_replacement_boundary.json"
)
REGRESSION_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "regression_matrix.json"
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "benchmarks" / "latest.json"


class GroupedAlternationReplacementBoundaryBenchmarkSuiteTest(unittest.TestCase):
    def test_runner_regenerates_combined_grouped_alternation_replacement_scorecard(self) -> None:
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
                    str(GROUPED_NAMED_MANIFEST_PATH),
                    "--manifest",
                    str(NUMBERED_BACKREFERENCE_MANIFEST_PATH),
                    "--manifest",
                    str(GROUPED_SEGMENT_MANIFEST_PATH),
                    "--manifest",
                    str(LITERAL_ALTERNATION_MANIFEST_PATH),
                    "--manifest",
                    str(GROUPED_ALTERNATION_MANIFEST_PATH),
                    "--manifest",
                    str(GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH),
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
                    "known_gap_count": 21,
                    "measured_workloads": 73,
                    "module_workloads": 86,
                    "parser_workloads": 8,
                    "regression_workloads": 5,
                    "total_workloads": 94,
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
        self.assertIsInstance(scorecard["implementation"]["native_module_loaded"], bool)
        self.assertIn("not requested", scorecard["implementation"]["native_unavailable_reason"])
        self.assertEqual(scorecard["environment"]["runner_version"], "phase3")
        self.assertEqual(scorecard["summary"]["total_workloads"], 94)
        self.assertEqual(scorecard["summary"]["parser_workloads"], 8)
        self.assertEqual(scorecard["summary"]["module_workloads"], 86)
        self.assertEqual(scorecard["summary"]["regression_workloads"], 5)
        self.assertEqual(scorecard["summary"]["measured_workloads"], 73)
        self.assertEqual(scorecard["summary"]["known_gap_count"], 21)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["cold"], 21)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["warm"], 37)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["purged"], 36)
        self.assertEqual(scorecard["families"]["parser"]["workload_count"], 8)
        self.assertEqual(scorecard["families"]["parser"]["known_gap_count"], 3)
        self.assertEqual(scorecard["families"]["parser"]["readiness"], "partial")
        self.assertEqual(scorecard["families"]["module"]["workload_count"], 86)
        self.assertEqual(scorecard["families"]["module"]["known_gap_count"], 18)
        self.assertEqual(scorecard["families"]["module"]["readiness"], "partial")
        self.assertEqual(scorecard["families"]["module"]["cache_modes"]["cold"]["workload_count"], 17)
        self.assertEqual(scorecard["families"]["module"]["cache_modes"]["warm"]["workload_count"], 35)
        self.assertEqual(scorecard["families"]["module"]["cache_modes"]["purged"]["workload_count"], 34)
        self.assertEqual(scorecard["artifacts"]["manifest"], None)
        self.assertEqual(scorecard["artifacts"]["manifest_id"], "combined-benchmark-suite")
        self.assertEqual(scorecard["artifacts"]["manifest_schema_version"], 1)
        self.assertEqual(scorecard["artifacts"]["selection_mode"], "full")
        self.assertEqual(len(scorecard["artifacts"]["manifests"]), 12)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        manifest_summary = scorecard["manifests"]["grouped-alternation-replacement-boundary"]
        self.assertEqual(manifest_summary["workload_count"], 10)
        self.assertEqual(manifest_summary["selected_workload_count"], 10)
        self.assertEqual(manifest_summary["measured_workloads"], 8)
        self.assertEqual(manifest_summary["known_gap_count"], 2)
        self.assertEqual(manifest_summary["readiness"], "partial")
        self.assertEqual(manifest_summary["selection_mode"], "full")
        self.assertEqual(manifest_summary["available_smoke_workload_count"], 2)
        self.assertEqual(
            manifest_summary["smoke_workload_ids"],
            [
                "module-sub-template-grouped-alternation-warm-str",
                "pattern-subn-template-named-grouped-alternation-purged-str",
            ],
        )
        self.assertEqual(
            manifest_summary["operations"],
            [
                "module.sub",
                "module.subn",
                "pattern.sub",
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
        self.assertIn("nested-group follow-ons", manifest_summary["notes"][1])

        manifest_record = next(
            manifest
            for manifest in scorecard["artifacts"]["manifests"]
            if manifest["manifest_id"] == "grouped-alternation-replacement-boundary"
        )
        self.assertEqual(
            manifest_record["manifest"],
            "benchmarks/workloads/grouped_alternation_replacement_boundary.json",
        )
        self.assertEqual(
            manifest_record["smoke_workload_ids"],
            [
                "module-sub-template-grouped-alternation-warm-str",
                "pattern-subn-template-named-grouped-alternation-purged-str",
            ],
        )

        module_sub = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-sub-template-grouped-alternation-warm-str"
        )
        self.assertEqual(module_sub["manifest_id"], "grouped-alternation-replacement-boundary")
        self.assertEqual(module_sub["operation"], "module.sub")
        self.assertEqual(module_sub["cache_mode"], "warm")
        self.assertEqual(module_sub["replacement"], "\\1x")
        self.assertEqual(module_sub["status"], "measured")
        self.assertEqual(module_sub["implementation_timing"]["status"], "measured")
        self.assertGreater(module_sub["implementation_ns"], 0)

        module_subn = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-subn-template-named-grouped-alternation-warm-str"
        )
        self.assertEqual(module_subn["operation"], "module.subn")
        self.assertEqual(module_subn["count"], 1)
        self.assertIn("named-groups", module_subn["syntax_features"])
        self.assertEqual(module_subn["status"], "measured")
        self.assertEqual(module_subn["implementation_timing"]["status"], "measured")
        self.assertGreater(module_subn["baseline_ns"], 0)
        self.assertGreater(module_subn["implementation_ns"], 0)

        pattern_sub = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "pattern-sub-template-grouped-alternation-purged-str"
        )
        self.assertEqual(pattern_sub["operation"], "pattern.sub")
        self.assertEqual(pattern_sub["cache_mode"], "purged")
        self.assertIn("cache-purge", pattern_sub["syntax_features"])
        self.assertEqual(pattern_sub["status"], "measured")
        self.assertEqual(pattern_sub["implementation_timing"]["status"], "measured")

        pattern_subn = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "pattern-subn-template-named-grouped-alternation-purged-str"
        )
        self.assertEqual(pattern_subn["operation"], "pattern.subn")
        self.assertEqual(pattern_subn["replacement"], "\\g<word>x")
        self.assertEqual(pattern_subn["status"], "measured")
        self.assertEqual(pattern_subn["implementation_timing"]["status"], "measured")

        module_gap = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-sub-template-nested-grouped-alternation-cold-gap"
        )
        self.assertEqual(module_gap["status"], "unimplemented")
        self.assertEqual(module_gap["implementation_timing"]["status"], "unimplemented")
        self.assertIsNone(module_gap["implementation_ns"])
        self.assertIsNone(module_gap["speedup_vs_cpython"])

        pattern_gap = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-subn-template-named-nested-grouped-alternation-replacement-purged-gap"
        )
        self.assertEqual(pattern_gap["status"], "unimplemented")
        self.assertEqual(pattern_gap["implementation_timing"]["status"], "unimplemented")
        self.assertIsNone(pattern_gap["implementation_ns"])
        self.assertIsNone(pattern_gap["speedup_vs_cpython"])


if __name__ == "__main__":
    unittest.main()
