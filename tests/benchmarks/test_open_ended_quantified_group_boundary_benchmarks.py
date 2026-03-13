from __future__ import annotations

import json
import pathlib
import platform
import subprocess
import sys
import tempfile
import unittest

from tests.report_assertions import assert_benchmark_summary_consistent


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
OPEN_ENDED_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "open_ended_quantified_group_boundary.json"
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


class OpenEndedQuantifiedGroupBoundaryBenchmarkSuiteTest(unittest.TestCase):
    def test_runner_regenerates_combined_open_ended_quantified_group_scorecard(self) -> None:
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
                    str(OPEN_ENDED_MANIFEST_PATH),
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
            scorecard = json.loads(report_path.read_text(encoding="utf-8"))

        assert_benchmark_summary_consistent(self, scorecard, summary)
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
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["cold"], 70)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["warm"], 184)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["purged"], 176)
        self.assertEqual(scorecard["families"]["parser"]["readiness"], "partial")
        self.assertEqual(scorecard["families"]["module"]["readiness"], "partial")
        self.assertEqual(scorecard["artifacts"]["manifest"], None)
        self.assertEqual(scorecard["artifacts"]["manifest_id"], "combined-benchmark-suite")
        self.assertEqual(scorecard["artifacts"]["manifest_schema_version"], 1)
        self.assertEqual(scorecard["artifacts"]["selection_mode"], "full")
        self.assertEqual(len(scorecard["artifacts"]["manifests"]), 30)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        manifest_summary = scorecard["manifests"]["open-ended-quantified-group-boundary"]
        self.assertEqual(manifest_summary["workload_count"], 14)
        self.assertEqual(manifest_summary["selected_workload_count"], 14)
        self.assertEqual(
            manifest_summary["measured_workloads"] + manifest_summary["known_gap_count"],
            manifest_summary["selected_workload_count"],
        )
        self.assertIn(manifest_summary["readiness"], {"partial", "measured"})
        self.assertEqual(manifest_summary["selection_mode"], "full")
        self.assertEqual(manifest_summary["available_smoke_workload_count"], 2)
        self.assertEqual(
            manifest_summary["smoke_workload_ids"],
            [
                "module-search-numbered-open-ended-group-alternation-lower-bound-bc-warm-str",
                "pattern-fullmatch-named-open-ended-group-alternation-fourth-repetition-de-purged-str",
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
        self.assertIn("a(bc|de){1,}d", manifest_summary["notes"][1])
        self.assertIn("a((bc|de){1,})?(?(1)d|e)", manifest_summary["notes"][1])
        self.assertIn("a(?P<outer>(bc|de){1,})?(?(outer)d|e)", manifest_summary["notes"][1])

        manifest_record = next(
            manifest
            for manifest in scorecard["artifacts"]["manifests"]
            if manifest["manifest_id"] == "open-ended-quantified-group-boundary"
        )
        self.assertEqual(
            manifest_record["manifest"],
            "benchmarks/workloads/open_ended_quantified_group_boundary.json",
        )
        self.assertEqual(
            manifest_record["smoke_workload_ids"],
            [
                "module-search-numbered-open-ended-group-alternation-lower-bound-bc-warm-str",
                "pattern-fullmatch-named-open-ended-group-alternation-fourth-repetition-de-purged-str",
            ],
        )

        compile_workload = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-compile-numbered-open-ended-group-alternation-cold-str"
        )
        self.assertEqual(compile_workload["manifest_id"], "open-ended-quantified-group-boundary")
        self.assertEqual(compile_workload["operation"], "module.compile")
        self.assertEqual(compile_workload["cache_mode"], "cold")
        self.assertIn("counted-repeats", compile_workload["syntax_features"])
        self.assertEqual(compile_workload["status"], "measured")
        self.assertEqual(compile_workload["implementation_timing"]["status"], "measured")
        self.assertGreater(compile_workload["implementation_ns"], 0)

        module_search = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "module-search-numbered-open-ended-group-alternation-lower-bound-bc-warm-str"
        )
        self.assertEqual(module_search["operation"], "module.search")
        self.assertEqual(module_search["pattern"], "a(bc|de){1,}d")
        self.assertEqual(module_search["haystack"], "zzabcdzz")
        self.assertEqual(module_search["status"], "measured")
        self.assertEqual(module_search["implementation_timing"]["status"], "measured")
        self.assertGreater(module_search["baseline_ns"], 0)
        self.assertGreater(module_search["implementation_ns"], 0)

        named_pattern = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-fullmatch-named-open-ended-group-alternation-fourth-repetition-de-purged-str"
        )
        self.assertEqual(named_pattern["operation"], "pattern.fullmatch")
        self.assertEqual(named_pattern["cache_mode"], "purged")
        self.assertIn("named-groups", named_pattern["syntax_features"])
        self.assertEqual(named_pattern["haystack"], "adededed")
        self.assertEqual(named_pattern["status"], "measured")
        self.assertEqual(named_pattern["implementation_timing"]["status"], "measured")
        self.assertGreater(named_pattern["implementation_ns"], 0)

        broader_range_gap = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-search-numbered-open-ended-group-broader-range-cold-gap"
        )
        self.assertEqual(broader_range_gap["status"], "unimplemented")
        self.assertEqual(broader_range_gap["pattern"], "a(bc|de){2,}d")
        self.assertEqual(broader_range_gap["implementation_timing"]["status"], "unimplemented")
        self.assertIsNone(broader_range_gap["implementation_ns"])
        self.assertIsNone(broader_range_gap["speedup_vs_cpython"])

        numbered_conditional_compile = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-compile-numbered-open-ended-group-conditional-cold-str"
        )
        self.assertEqual(numbered_conditional_compile["status"], "measured")
        self.assertEqual(numbered_conditional_compile["operation"], "module.compile")
        self.assertEqual(numbered_conditional_compile["cache_mode"], "cold")
        self.assertEqual(numbered_conditional_compile["pattern"], "a((bc|de){1,})?(?(1)d|e)")
        self.assertIn("conditionals", numbered_conditional_compile["syntax_features"])
        self.assertEqual(
            numbered_conditional_compile["implementation_timing"]["status"], "measured"
        )
        self.assertGreater(numbered_conditional_compile["implementation_ns"], 0)

        conditional_anchor = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-search-numbered-open-ended-group-conditional-warm-gap"
        )
        self.assertEqual(conditional_anchor["status"], "measured")
        self.assertEqual(conditional_anchor["pattern"], "a((bc|de){1,})?(?(1)d|e)")
        self.assertEqual(conditional_anchor["haystack"], "zzabcbcdzz")
        self.assertIn("conditionals", conditional_anchor["syntax_features"])
        self.assertEqual(conditional_anchor["implementation_timing"]["status"], "measured")
        self.assertGreater(conditional_anchor["implementation_ns"], 0)

        numbered_conditional_pattern = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-fullmatch-numbered-open-ended-group-conditional-third-repetition-mixed-purged-str"
        )
        self.assertEqual(numbered_conditional_pattern["status"], "measured")
        self.assertEqual(numbered_conditional_pattern["haystack"], "abcbcded")
        self.assertEqual(numbered_conditional_pattern["cache_mode"], "purged")
        self.assertIn("conditionals", numbered_conditional_pattern["syntax_features"])
        self.assertEqual(
            numbered_conditional_pattern["implementation_timing"]["status"], "measured"
        )
        self.assertGreater(numbered_conditional_pattern["implementation_ns"], 0)

        named_conditional_compile = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-compile-named-open-ended-group-conditional-warm-str"
        )
        self.assertEqual(named_conditional_compile["status"], "measured")
        self.assertEqual(named_conditional_compile["cache_mode"], "warm")
        self.assertIn("named-groups", named_conditional_compile["syntax_features"])
        self.assertEqual(
            named_conditional_compile["implementation_timing"]["status"], "measured"
        )
        self.assertGreater(named_conditional_compile["implementation_ns"], 0)

        named_conditional_search = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "module-search-named-open-ended-group-conditional-fourth-repetition-de-warm-str"
        )
        self.assertEqual(named_conditional_search["status"], "measured")
        self.assertEqual(
            named_conditional_search["pattern"], "a(?P<outer>(bc|de){1,})?(?(outer)d|e)"
        )
        self.assertEqual(named_conditional_search["haystack"], "zzadedededzz")
        self.assertIn("named-groups", named_conditional_search["syntax_features"])
        self.assertEqual(
            named_conditional_search["implementation_timing"]["status"], "measured"
        )
        self.assertGreater(named_conditional_search["implementation_ns"], 0)

        named_conditional_pattern = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-fullmatch-named-open-ended-group-conditional-third-repetition-mixed-purged-str"
        )
        self.assertEqual(named_conditional_pattern["status"], "measured")
        self.assertEqual(named_conditional_pattern["haystack"], "abcbcded")
        self.assertEqual(named_conditional_pattern["cache_mode"], "purged")
        self.assertIn("named-groups", named_conditional_pattern["syntax_features"])
        self.assertEqual(
            named_conditional_pattern["implementation_timing"]["status"], "measured"
        )
        self.assertGreater(named_conditional_pattern["implementation_ns"], 0)

        backtracking_gap = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "pattern-fullmatch-named-open-ended-group-backtracking-heavy-purged-gap"
        )
        self.assertIn(backtracking_gap["status"], {"measured", "unimplemented"})
        self.assertEqual(backtracking_gap["pattern"], "a(?P<word>(bc|b)c){1,}d")
        self.assertIn("named-groups", backtracking_gap["syntax_features"])
        self.assertEqual(
            backtracking_gap["implementation_timing"]["status"],
            backtracking_gap["status"],
        )
        if backtracking_gap["status"] == "measured":
            self.assertGreater(backtracking_gap["implementation_ns"], 0)


if __name__ == "__main__":
    unittest.main()
