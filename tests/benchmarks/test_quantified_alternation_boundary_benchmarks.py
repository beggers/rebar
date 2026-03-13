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
GROUPED_ALTERNATION_CALLABLE_REPLACEMENT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_alternation_callable_replacement_boundary.json"
)
NESTED_GROUP_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "nested_group_boundary.json"
NESTED_GROUP_ALTERNATION_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "nested_group_alternation_boundary.json"
)
NESTED_GROUP_REPLACEMENT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "nested_group_replacement_boundary.json"
)
NESTED_GROUP_CALLABLE_REPLACEMENT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "nested_group_callable_replacement_boundary.json"
)
BRANCH_LOCAL_BACKREFERENCE_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "branch_local_backreference_boundary.json"
)
OPTIONAL_GROUP_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "optional_group_boundary.json"
)
EXACT_REPEAT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "exact_repeat_quantified_group_boundary.json"
)
RANGED_REPEAT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "ranged_repeat_quantified_group_boundary.json"
)
WIDER_RANGED_REPEAT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "wider_ranged_repeat_quantified_group_boundary.json"
)
QUANTIFIED_ALTERNATION_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "quantified_alternation_boundary.json"
)
OPTIONAL_GROUP_ALTERNATION_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "optional_group_alternation_boundary.json"
)
CONDITIONAL_GROUP_EXISTS_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "conditional_group_exists_boundary.json"
)
CONDITIONAL_GROUP_EXISTS_NO_ELSE_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "conditional_group_exists_no_else_boundary.json"
)
CONDITIONAL_GROUP_EXISTS_EMPTY_ELSE_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "conditional_group_exists_empty_else_boundary.json"
)
CONDITIONAL_GROUP_EXISTS_EMPTY_YES_ELSE_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "conditional_group_exists_empty_yes_else_boundary.json"
)
CONDITIONAL_GROUP_EXISTS_FULLY_EMPTY_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "conditional_group_exists_fully_empty_boundary.json"
)
REGRESSION_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "regression_matrix.json"
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "benchmarks" / "latest.json"


class QuantifiedAlternationBoundaryBenchmarkSuiteTest(unittest.TestCase):
    def test_runner_regenerates_combined_quantified_alternation_scorecard(self) -> None:
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
                    str(GROUPED_ALTERNATION_CALLABLE_REPLACEMENT_MANIFEST_PATH),
                    "--manifest",
                    str(NESTED_GROUP_MANIFEST_PATH),
                    "--manifest",
                    str(NESTED_GROUP_ALTERNATION_MANIFEST_PATH),
                    "--manifest",
                    str(NESTED_GROUP_REPLACEMENT_MANIFEST_PATH),
                    "--manifest",
                    str(NESTED_GROUP_CALLABLE_REPLACEMENT_MANIFEST_PATH),
                    "--manifest",
                    str(BRANCH_LOCAL_BACKREFERENCE_MANIFEST_PATH),
                    "--manifest",
                    str(OPTIONAL_GROUP_MANIFEST_PATH),
                    "--manifest",
                    str(EXACT_REPEAT_MANIFEST_PATH),
                    "--manifest",
                    str(RANGED_REPEAT_MANIFEST_PATH),
                    "--manifest",
                    str(WIDER_RANGED_REPEAT_MANIFEST_PATH),
                    "--manifest",
                    str(QUANTIFIED_ALTERNATION_MANIFEST_PATH),
                    "--manifest",
                    str(OPTIONAL_GROUP_ALTERNATION_MANIFEST_PATH),
                    "--manifest",
                    str(CONDITIONAL_GROUP_EXISTS_MANIFEST_PATH),
                    "--manifest",
                    str(CONDITIONAL_GROUP_EXISTS_NO_ELSE_MANIFEST_PATH),
                    "--manifest",
                    str(CONDITIONAL_GROUP_EXISTS_EMPTY_ELSE_MANIFEST_PATH),
                    "--manifest",
                    str(CONDITIONAL_GROUP_EXISTS_EMPTY_YES_ELSE_MANIFEST_PATH),
                    "--manifest",
                    str(CONDITIONAL_GROUP_EXISTS_FULLY_EMPTY_MANIFEST_PATH),
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
                    "known_gap_count": 44,
                    "measured_workloads": 327,
                    "module_workloads": 363,
                    "parser_workloads": 8,
                    "regression_workloads": 5,
                    "total_workloads": 371,
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
        self.assertEqual(scorecard["summary"]["total_workloads"], 371)
        self.assertEqual(scorecard["summary"]["parser_workloads"], 8)
        self.assertEqual(scorecard["summary"]["module_workloads"], 363)
        self.assertEqual(scorecard["summary"]["regression_workloads"], 5)
        self.assertEqual(scorecard["summary"]["measured_workloads"], 327)
        self.assertEqual(scorecard["summary"]["known_gap_count"], 44)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["cold"], 58)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["warm"], 155)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["purged"], 158)
        self.assertEqual(scorecard["families"]["parser"]["workload_count"], 8)
        self.assertEqual(scorecard["families"]["parser"]["known_gap_count"], 3)
        self.assertEqual(scorecard["families"]["parser"]["readiness"], "partial")
        self.assertEqual(scorecard["families"]["module"]["workload_count"], 363)
        self.assertEqual(scorecard["families"]["module"]["known_gap_count"], 41)
        self.assertEqual(scorecard["families"]["module"]["readiness"], "partial")
        self.assertEqual(scorecard["families"]["module"]["cache_modes"]["cold"]["workload_count"], 54)
        self.assertEqual(scorecard["families"]["module"]["cache_modes"]["warm"]["workload_count"], 153)
        self.assertEqual(scorecard["families"]["module"]["cache_modes"]["purged"]["workload_count"], 156)
        self.assertEqual(scorecard["artifacts"]["manifest"], None)
        self.assertEqual(scorecard["artifacts"]["manifest_id"], "combined-benchmark-suite")
        self.assertEqual(scorecard["artifacts"]["manifest_schema_version"], 1)
        self.assertEqual(scorecard["artifacts"]["selection_mode"], "full")
        self.assertEqual(len(scorecard["artifacts"]["manifests"]), 29)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        manifest_summary = scorecard["manifests"]["quantified-alternation-boundary"]
        self.assertEqual(manifest_summary["workload_count"], 12)
        self.assertEqual(manifest_summary["selected_workload_count"], 12)
        self.assertEqual(manifest_summary["measured_workloads"], 6)
        self.assertEqual(manifest_summary["known_gap_count"], 6)
        self.assertEqual(manifest_summary["readiness"], "partial")
        self.assertEqual(manifest_summary["selection_mode"], "full")
        self.assertEqual(manifest_summary["available_smoke_workload_count"], 2)
        self.assertEqual(
            manifest_summary["smoke_workload_ids"],
            [
                "module-search-numbered-quantified-alternation-lower-bound-warm-str",
                "pattern-fullmatch-named-quantified-alternation-lower-bound-purged-str",
            ],
        )
        self.assertEqual(
            manifest_summary["operations"],
            [
                "module.compile",
                "module.search",
                "pattern.fullmatch",
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
        self.assertIn("branch-local backreferences inside quantified alternation", manifest_summary["notes"][1])

        manifest_record = next(
            manifest
            for manifest in scorecard["artifacts"]["manifests"]
            if manifest["manifest_id"] == "quantified-alternation-boundary"
        )
        self.assertEqual(
            manifest_record["manifest"],
            "benchmarks/workloads/quantified_alternation_boundary.json",
        )
        self.assertEqual(
            manifest_record["smoke_workload_ids"],
            [
                "module-search-numbered-quantified-alternation-lower-bound-warm-str",
                "pattern-fullmatch-named-quantified-alternation-lower-bound-purged-str",
            ],
        )

        compile_workload = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-compile-numbered-quantified-alternation-cold-str"
        )
        self.assertEqual(compile_workload["manifest_id"], "quantified-alternation-boundary")
        self.assertEqual(compile_workload["operation"], "module.compile")
        self.assertEqual(compile_workload["cache_mode"], "cold")
        self.assertIn("alternation", compile_workload["syntax_features"])
        self.assertEqual(compile_workload["status"], "measured")
        self.assertEqual(compile_workload["implementation_timing"]["status"], "measured")
        self.assertGreater(compile_workload["implementation_ns"], 0)

        module_search = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-search-numbered-quantified-alternation-lower-bound-warm-str"
        )
        self.assertEqual(module_search["operation"], "module.search")
        self.assertEqual(module_search["pattern"], "a(b|c){1,2}d")
        self.assertEqual(module_search["haystack"], "zzacdz")
        self.assertEqual(module_search["status"], "measured")
        self.assertEqual(module_search["implementation_timing"]["status"], "measured")
        self.assertGreater(module_search["baseline_ns"], 0)
        self.assertGreater(module_search["implementation_ns"], 0)

        named_pattern = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "pattern-fullmatch-named-quantified-alternation-lower-bound-purged-str"
        )
        self.assertEqual(named_pattern["operation"], "pattern.fullmatch")
        self.assertEqual(named_pattern["cache_mode"], "purged")
        self.assertIn("named-groups", named_pattern["syntax_features"])
        self.assertEqual(named_pattern["status"], "measured")
        self.assertEqual(named_pattern["implementation_timing"]["status"], "measured")

        broader_range_gap = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-search-numbered-quantified-alternation-broader-range-cold-gap"
        )
        self.assertEqual(broader_range_gap["status"], "unimplemented")
        self.assertEqual(broader_range_gap["pattern"], "a(b|c){1,3}d")
        self.assertEqual(broader_range_gap["implementation_timing"]["status"], "unimplemented")
        self.assertIsNone(broader_range_gap["implementation_ns"])
        self.assertIsNone(broader_range_gap["speedup_vs_cpython"])

        open_ended_gap = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "pattern-fullmatch-numbered-quantified-alternation-open-ended-purged-gap"
        )
        self.assertEqual(open_ended_gap["status"], "unimplemented")
        self.assertEqual(open_ended_gap["pattern"], "a(b|c){1,}d")
        self.assertEqual(open_ended_gap["implementation_timing"]["status"], "unimplemented")
        self.assertIsNone(open_ended_gap["implementation_ns"])
        self.assertIsNone(open_ended_gap["speedup_vs_cpython"])

        nested_branch_gap = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "pattern-fullmatch-named-quantified-alternation-nested-branch-purged-gap"
        )
        self.assertEqual(nested_branch_gap["status"], "unimplemented")
        self.assertIn("named-groups", nested_branch_gap["syntax_features"])
        self.assertEqual(nested_branch_gap["implementation_timing"]["status"], "unimplemented")
        self.assertIsNone(nested_branch_gap["implementation_ns"])
        self.assertIsNone(nested_branch_gap["speedup_vs_cpython"])

        branch_backref_gap = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-search-numbered-quantified-alternation-branch-backref-cold-gap"
        )
        self.assertEqual(branch_backref_gap["status"], "unimplemented")
        self.assertIn("backreferences", branch_backref_gap["syntax_features"])
        self.assertEqual(branch_backref_gap["implementation_timing"]["status"], "unimplemented")
        self.assertIsNone(branch_backref_gap["implementation_ns"])
        self.assertIsNone(branch_backref_gap["speedup_vs_cpython"])

        conditional_gap = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-search-numbered-quantified-alternation-conditional-warm-gap"
        )
        self.assertEqual(conditional_gap["status"], "unimplemented")
        self.assertIn("conditionals", conditional_gap["syntax_features"])
        self.assertEqual(conditional_gap["implementation_timing"]["status"], "unimplemented")
        self.assertIsNone(conditional_gap["implementation_ns"])
        self.assertIsNone(conditional_gap["speedup_vs_cpython"])

        backtracking_gap = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "pattern-fullmatch-numbered-quantified-alternation-backtracking-heavy-purged-gap"
        )
        self.assertEqual(backtracking_gap["status"], "unimplemented")
        self.assertIn("alternation", backtracking_gap["syntax_features"])
        self.assertEqual(backtracking_gap["implementation_timing"]["status"], "unimplemented")
        self.assertIsNone(backtracking_gap["implementation_ns"])
        self.assertIsNone(backtracking_gap["speedup_vs_cpython"])


if __name__ == "__main__":
    unittest.main()
