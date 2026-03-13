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
OPTIONAL_GROUP_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "optional_group_boundary.json"
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


class ConditionalGroupExistsEmptyYesElseBoundaryBenchmarkSuiteTest(unittest.TestCase):
    def test_runner_regenerates_combined_conditional_group_exists_empty_yes_else_scorecard(
        self,
    ) -> None:
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
                    "known_gap_count": 50,
                    "measured_workloads": 253,
                    "module_workloads": 295,
                    "parser_workloads": 8,
                    "regression_workloads": 5,
                    "total_workloads": 303,
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
        self.assertEqual(scorecard["summary"]["total_workloads"], 303)
        self.assertEqual(scorecard["summary"]["parser_workloads"], 8)
        self.assertEqual(scorecard["summary"]["module_workloads"], 295)
        self.assertEqual(scorecard["summary"]["regression_workloads"], 5)
        self.assertEqual(scorecard["summary"]["measured_workloads"], 253)
        self.assertEqual(scorecard["summary"]["known_gap_count"], 50)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["cold"], 55)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["warm"], 121)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["purged"], 127)
        self.assertEqual(scorecard["families"]["parser"]["workload_count"], 8)
        self.assertEqual(scorecard["families"]["parser"]["known_gap_count"], 3)
        self.assertEqual(scorecard["families"]["parser"]["readiness"], "partial")
        self.assertEqual(scorecard["families"]["module"]["workload_count"], 295)
        self.assertEqual(scorecard["families"]["module"]["known_gap_count"], 47)
        self.assertEqual(scorecard["families"]["module"]["readiness"], "partial")
        self.assertEqual(scorecard["families"]["module"]["cache_modes"]["cold"]["workload_count"], 51)
        self.assertEqual(scorecard["families"]["module"]["cache_modes"]["warm"]["workload_count"], 119)
        self.assertEqual(scorecard["families"]["module"]["cache_modes"]["purged"]["workload_count"], 125)
        self.assertEqual(scorecard["artifacts"]["manifest"], None)
        self.assertEqual(scorecard["artifacts"]["manifest_id"], "combined-benchmark-suite")
        self.assertEqual(scorecard["artifacts"]["manifest_schema_version"], 1)
        self.assertEqual(scorecard["artifacts"]["selection_mode"], "full")
        self.assertEqual(len(scorecard["artifacts"]["manifests"]), 29)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        manifest_summary = scorecard["manifests"]["conditional-group-exists-empty-yes-else-boundary"]
        self.assertEqual(manifest_summary["workload_count"], 24)
        self.assertEqual(manifest_summary["selected_workload_count"], 24)
        self.assertEqual(manifest_summary["measured_workloads"], 23)
        self.assertEqual(manifest_summary["known_gap_count"], 1)
        self.assertEqual(manifest_summary["readiness"], "partial")
        self.assertEqual(manifest_summary["selection_mode"], "full")
        self.assertEqual(manifest_summary["available_smoke_workload_count"], 2)
        self.assertEqual(
            manifest_summary["smoke_workload_ids"],
            [
                "module-search-numbered-conditional-group-exists-empty-yes-else-present-warm-str",
                "pattern-fullmatch-named-conditional-group-exists-empty-yes-else-absent-purged-str",
            ],
        )
        self.assertEqual(
            manifest_summary["operations"],
            [
                "module.compile",
                "module.search",
                "module.sub",
                "module.subn",
                "pattern.fullmatch",
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
        self.assertIn("constant-replacement `sub()`/`subn()` paths", manifest_summary["notes"][1])
        self.assertIn("bounded nested empty-yes-arm slice now times", manifest_summary["notes"][1])
        self.assertIn("bounded quantified empty-yes-arm", manifest_summary["notes"][1])
        self.assertIn("Assertion-conditioned branches remain outside", manifest_summary["notes"][2])

        manifest_record = next(
            manifest
            for manifest in scorecard["artifacts"]["manifests"]
            if manifest["manifest_id"] == "conditional-group-exists-empty-yes-else-boundary"
        )
        self.assertEqual(
            manifest_record["manifest"],
            "benchmarks/workloads/conditional_group_exists_empty_yes_else_boundary.json",
        )
        self.assertEqual(
            manifest_record["smoke_workload_ids"],
            [
                "module-search-numbered-conditional-group-exists-empty-yes-else-present-warm-str",
                "pattern-fullmatch-named-conditional-group-exists-empty-yes-else-absent-purged-str",
            ],
        )

        compile_workload = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-compile-numbered-conditional-group-exists-empty-yes-else-cold-str"
        )
        self.assertEqual(
            compile_workload["manifest_id"], "conditional-group-exists-empty-yes-else-boundary"
        )
        self.assertEqual(compile_workload["operation"], "module.compile")
        self.assertEqual(compile_workload["cache_mode"], "cold")
        self.assertIn("conditionals", compile_workload["syntax_features"])
        self.assertEqual(compile_workload["status"], "measured")
        self.assertEqual(compile_workload["implementation_timing"]["status"], "measured")
        self.assertGreater(compile_workload["implementation_ns"], 0)

        module_search = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "module-search-numbered-conditional-group-exists-empty-yes-else-present-warm-str"
        )
        self.assertEqual(module_search["operation"], "module.search")
        self.assertEqual(module_search["pattern"], "a(b)?c(?(1)|e)")
        self.assertEqual(module_search["status"], "measured")
        self.assertEqual(module_search["implementation_timing"]["status"], "measured")
        self.assertGreater(module_search["baseline_ns"], 0)
        self.assertGreater(module_search["implementation_ns"], 0)

        named_pattern = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-fullmatch-named-conditional-group-exists-empty-yes-else-absent-purged-str"
        )
        self.assertEqual(named_pattern["operation"], "pattern.fullmatch")
        self.assertEqual(named_pattern["cache_mode"], "purged")
        self.assertIn("cache-purge", named_pattern["syntax_features"])
        self.assertEqual(named_pattern["status"], "measured")
        self.assertEqual(named_pattern["implementation_timing"]["status"], "measured")

        fully_empty_gap = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-search-numbered-conditional-group-exists-fully-empty-cold-gap"
        )
        self.assertEqual(fully_empty_gap["status"], "measured")
        self.assertEqual(fully_empty_gap["implementation_timing"]["status"], "measured")
        self.assertGreater(fully_empty_gap["baseline_ns"], 0)
        self.assertGreater(fully_empty_gap["implementation_ns"], 0)

        replacement_gap = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "module-sub-numbered-conditional-group-exists-empty-yes-else-replacement-warm-gap"
        )
        self.assertEqual(replacement_gap["operation"], "module.sub")
        self.assertEqual(replacement_gap["status"], "measured")
        self.assertEqual(replacement_gap["implementation_timing"]["status"], "measured")
        self.assertEqual(replacement_gap["replacement"], "X")
        self.assertGreater(replacement_gap["implementation_ns"], 0)

        subn_numbered = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "module-subn-numbered-conditional-group-exists-empty-yes-else-replacement-warm-str"
        )
        self.assertEqual(subn_numbered["operation"], "module.subn")
        self.assertEqual(subn_numbered["count"], 1)
        self.assertEqual(subn_numbered["status"], "measured")
        self.assertEqual(subn_numbered["implementation_timing"]["status"], "measured")
        self.assertGreater(subn_numbered["implementation_ns"], 0)

        pattern_subn_named = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-subn-named-conditional-group-exists-empty-yes-else-replacement-purged-str"
        )
        self.assertEqual(pattern_subn_named["operation"], "pattern.subn")
        self.assertEqual(pattern_subn_named["count"], 1)
        self.assertIn("named-groups", pattern_subn_named["syntax_features"])
        self.assertEqual(pattern_subn_named["status"], "measured")
        self.assertEqual(pattern_subn_named["implementation_timing"]["status"], "measured")
        self.assertGreater(pattern_subn_named["baseline_ns"], 0)
        self.assertGreater(pattern_subn_named["implementation_ns"], 0)

        quantified_numbered_search = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "module-search-numbered-quantified-conditional-group-exists-empty-yes-else-present-warm-str"
        )
        self.assertEqual(quantified_numbered_search["status"], "measured")
        self.assertEqual(quantified_numbered_search["implementation_timing"]["status"], "measured")
        self.assertEqual(quantified_numbered_search["pattern"], "(?:a(b)?c(?(1)|e)){2}")
        self.assertEqual(quantified_numbered_search["haystack"], "zzabcabczz")
        self.assertGreater(quantified_numbered_search["implementation_ns"], 0)

        quantified_numbered_pattern = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-fullmatch-numbered-quantified-conditional-group-exists-empty-yes-else-purged-gap"
        )
        self.assertEqual(quantified_numbered_pattern["status"], "measured")
        self.assertEqual(quantified_numbered_pattern["implementation_timing"]["status"], "measured")
        self.assertEqual(quantified_numbered_pattern["operation"], "pattern.fullmatch")
        self.assertEqual(quantified_numbered_pattern["pattern"], "(?:a(b)?c(?(1)|e)){2}")
        self.assertEqual(quantified_numbered_pattern["haystack"], "aceace")
        self.assertGreater(quantified_numbered_pattern["implementation_ns"], 0)

        quantified_named_search = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "module-search-named-quantified-conditional-group-exists-empty-yes-else-present-warm-str"
        )
        self.assertEqual(quantified_named_search["status"], "measured")
        self.assertEqual(quantified_named_search["implementation_timing"]["status"], "measured")
        self.assertEqual(
            quantified_named_search["pattern"],
            "(?:a(?P<word>b)?c(?(word)|e)){2}",
        )
        self.assertEqual(quantified_named_search["haystack"], "zzabcabczz")
        self.assertGreater(quantified_named_search["implementation_ns"], 0)

        quantified_named_pattern = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-fullmatch-named-quantified-conditional-group-exists-empty-yes-else-absent-purged-str"
        )
        self.assertEqual(quantified_named_pattern["status"], "measured")
        self.assertEqual(quantified_named_pattern["implementation_timing"]["status"], "measured")
        self.assertEqual(quantified_named_pattern["operation"], "pattern.fullmatch")
        self.assertEqual(
            quantified_named_pattern["pattern"],
            "(?:a(?P<word>b)?c(?(word)|e)){2}",
        )
        self.assertEqual(quantified_named_pattern["haystack"], "aceace")
        self.assertGreater(quantified_named_pattern["implementation_ns"], 0)

        backtracking_gap = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "module-search-numbered-conditional-group-exists-empty-yes-else-alternation-heavy-warm-gap"
        )
        self.assertEqual(backtracking_gap["pattern"], "a(b)?c(?(1)|(e|f))")
        self.assertEqual(backtracking_gap["haystack"], "zzacezz")
        self.assertEqual(backtracking_gap["status"], "unimplemented")
        self.assertEqual(backtracking_gap["implementation_timing"]["status"], "unimplemented")
        self.assertIsNone(backtracking_gap["implementation_ns"])
        self.assertIn("empty-yes-arm", backtracking_gap["notes"][0])
        self.assertIn("a(b)?c(?(1)|(e|f))", backtracking_gap["notes"][0])
        self.assertIn("not implemented", backtracking_gap["implementation_timing"]["reason"].lower())

        nested_gap = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-search-numbered-nested-conditional-group-exists-empty-yes-else-cold-gap"
        )
        self.assertEqual(nested_gap["pattern"], "a(b)?c(?(1)|(?(1)e|f))")
        self.assertEqual(nested_gap["haystack"], "zzabczz")
        self.assertEqual(nested_gap["status"], "measured")
        self.assertEqual(nested_gap["implementation_timing"]["status"], "measured")
        self.assertGreater(nested_gap["implementation_ns"], 0)

        numbered_pattern_nested = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-fullmatch-numbered-nested-conditional-group-exists-empty-yes-else-absent-purged-str"
        )
        self.assertEqual(numbered_pattern_nested["status"], "measured")
        self.assertEqual(numbered_pattern_nested["implementation_timing"]["status"], "measured")
        self.assertEqual(numbered_pattern_nested["operation"], "pattern.fullmatch")
        self.assertEqual(numbered_pattern_nested["cache_mode"], "purged")
        self.assertEqual(numbered_pattern_nested["haystack"], "acf")
        self.assertGreater(numbered_pattern_nested["implementation_ns"], 0)

        named_nested = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "module-search-named-nested-conditional-group-exists-empty-yes-else-present-warm-str"
        )
        self.assertEqual(named_nested["status"], "measured")
        self.assertEqual(named_nested["implementation_timing"]["status"], "measured")
        self.assertEqual(named_nested["operation"], "module.search")
        self.assertEqual(named_nested["pattern"], "a(?P<word>b)?c(?(word)|(?(word)e|f))")
        self.assertEqual(named_nested["haystack"], "zzabczz")
        self.assertGreater(named_nested["implementation_ns"], 0)

        named_pattern_nested = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-fullmatch-named-nested-conditional-group-exists-empty-yes-else-absent-purged-str"
        )
        self.assertEqual(named_pattern_nested["status"], "measured")
        self.assertEqual(named_pattern_nested["implementation_timing"]["status"], "measured")
        self.assertEqual(named_pattern_nested["operation"], "pattern.fullmatch")
        self.assertEqual(named_pattern_nested["cache_mode"], "purged")
        self.assertEqual(named_pattern_nested["haystack"], "acf")
        self.assertGreater(named_pattern_nested["implementation_ns"], 0)


if __name__ == "__main__":
    unittest.main()
