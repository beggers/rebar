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
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["cold"], 68)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["warm"], 179)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["purged"], 173)
        self.assertEqual(scorecard["families"]["parser"]["readiness"], "partial")
        self.assertEqual(scorecard["families"]["module"]["readiness"], "partial")
        self.assertEqual(scorecard["artifacts"]["manifest"], None)
        self.assertEqual(scorecard["artifacts"]["manifest_id"], "combined-benchmark-suite")
        self.assertEqual(scorecard["artifacts"]["manifest_schema_version"], 1)
        self.assertEqual(scorecard["artifacts"]["selection_mode"], "full")
        self.assertEqual(len(scorecard["artifacts"]["manifests"]), 30)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        manifest_summary = scorecard["manifests"]["quantified-alternation-boundary"]
        self.assertEqual(manifest_summary["workload_count"], 42)
        self.assertEqual(manifest_summary["selected_workload_count"], 42)
        self.assertEqual(manifest_summary["measured_workloads"], 42)
        self.assertEqual(manifest_summary["known_gap_count"], 0)
        self.assertEqual(manifest_summary["readiness"], "measured")
        self.assertEqual(manifest_summary["selection_mode"], "full")
        self.assertEqual(manifest_summary["available_smoke_workload_count"], 3)
        self.assertEqual(
            manifest_summary["smoke_workload_ids"],
            [
                "module-search-numbered-quantified-alternation-lower-bound-warm-str",
                "pattern-fullmatch-named-quantified-alternation-lower-bound-purged-str",
                "pattern-fullmatch-named-quantified-alternation-branch-backref-second-repetition-purged-str",
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
        self.assertIn("open-ended", manifest_summary["notes"][1])

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
                "pattern-fullmatch-named-quantified-alternation-branch-backref-second-repetition-purged-str",
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

        broader_range_compile = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-compile-numbered-quantified-alternation-broader-range-cold-str"
        )
        self.assertEqual(broader_range_compile["operation"], "module.compile")
        self.assertEqual(broader_range_compile["cache_mode"], "cold")
        self.assertEqual(broader_range_compile["pattern"], "a(b|c){1,3}d")
        self.assertEqual(broader_range_compile["status"], "measured")
        self.assertEqual(broader_range_compile["implementation_timing"]["status"], "measured")
        self.assertGreater(broader_range_compile["implementation_ns"], 0)

        broader_range_search = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "module-search-numbered-quantified-alternation-broader-range-third-repetition-cold-str"
        )
        self.assertEqual(broader_range_search["operation"], "module.search")
        self.assertEqual(broader_range_search["pattern"], "a(b|c){1,3}d")
        self.assertEqual(broader_range_search["haystack"], "zzabccdzz")
        self.assertEqual(broader_range_search["status"], "measured")
        self.assertEqual(broader_range_search["implementation_timing"]["status"], "measured")
        self.assertGreater(broader_range_search["baseline_ns"], 0)
        self.assertGreater(broader_range_search["implementation_ns"], 0)

        broader_range_pattern = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-fullmatch-numbered-quantified-alternation-broader-range-third-repetition-bcb-purged-str"
        )
        self.assertEqual(broader_range_pattern["operation"], "pattern.fullmatch")
        self.assertEqual(broader_range_pattern["cache_mode"], "purged")
        self.assertEqual(broader_range_pattern["haystack"], "abcbd")
        self.assertEqual(broader_range_pattern["status"], "measured")
        self.assertEqual(broader_range_pattern["implementation_timing"]["status"], "measured")
        self.assertGreater(broader_range_pattern["implementation_ns"], 0)

        broader_range_named_compile = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-compile-named-quantified-alternation-broader-range-warm-str"
        )
        self.assertEqual(broader_range_named_compile["operation"], "module.compile")
        self.assertEqual(broader_range_named_compile["cache_mode"], "warm")
        self.assertIn("named-groups", broader_range_named_compile["syntax_features"])
        self.assertEqual(broader_range_named_compile["status"], "measured")
        self.assertEqual(
            broader_range_named_compile["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(broader_range_named_compile["implementation_ns"], 0)

        broader_range_named_search = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "module-search-named-quantified-alternation-broader-range-third-repetition-bcc-warm-str"
        )
        self.assertEqual(broader_range_named_search["operation"], "module.search")
        self.assertEqual(
            broader_range_named_search["pattern"],
            "a(?P<word>b|c){1,3}d",
        )
        self.assertEqual(broader_range_named_search["haystack"], "zzabccdzz")
        self.assertEqual(broader_range_named_search["status"], "measured")
        self.assertEqual(
            broader_range_named_search["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(broader_range_named_search["baseline_ns"], 0)
        self.assertGreater(broader_range_named_search["implementation_ns"], 0)

        broader_range_named_pattern = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-fullmatch-named-quantified-alternation-broader-range-third-repetition-bbb-purged-str"
        )
        self.assertEqual(broader_range_named_pattern["operation"], "pattern.fullmatch")
        self.assertEqual(broader_range_named_pattern["cache_mode"], "purged")
        self.assertIn("named-groups", broader_range_named_pattern["syntax_features"])
        self.assertEqual(broader_range_named_pattern["haystack"], "abbbd")
        self.assertEqual(broader_range_named_pattern["status"], "measured")
        self.assertEqual(
            broader_range_named_pattern["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(broader_range_named_pattern["implementation_ns"], 0)

        open_ended_compile = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-compile-numbered-quantified-alternation-open-ended-cold-str"
        )
        self.assertEqual(open_ended_compile["operation"], "module.compile")
        self.assertEqual(open_ended_compile["cache_mode"], "cold")
        self.assertEqual(open_ended_compile["pattern"], "a(b|c){1,}d")
        self.assertEqual(open_ended_compile["status"], "measured")
        self.assertEqual(open_ended_compile["implementation_timing"]["status"], "measured")
        self.assertGreater(open_ended_compile["implementation_ns"], 0)

        open_ended_search = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "module-search-numbered-quantified-alternation-open-ended-lower-bound-b-warm-str"
        )
        self.assertEqual(open_ended_search["operation"], "module.search")
        self.assertEqual(open_ended_search["haystack"], "zzabdzz")
        self.assertEqual(open_ended_search["status"], "measured")
        self.assertEqual(open_ended_search["implementation_timing"]["status"], "measured")
        self.assertGreater(open_ended_search["baseline_ns"], 0)
        self.assertGreater(open_ended_search["implementation_ns"], 0)

        open_ended_pattern = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-fullmatch-numbered-quantified-alternation-open-ended-fourth-repetition-bcbc-purged-str"
        )
        self.assertEqual(open_ended_pattern["operation"], "pattern.fullmatch")
        self.assertEqual(open_ended_pattern["cache_mode"], "purged")
        self.assertEqual(open_ended_pattern["haystack"], "abcbcd")
        self.assertEqual(open_ended_pattern["status"], "measured")
        self.assertEqual(open_ended_pattern["implementation_timing"]["status"], "measured")
        self.assertGreater(open_ended_pattern["implementation_ns"], 0)

        open_ended_named_compile = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-compile-named-quantified-alternation-open-ended-warm-str"
        )
        self.assertEqual(open_ended_named_compile["operation"], "module.compile")
        self.assertEqual(open_ended_named_compile["cache_mode"], "warm")
        self.assertIn("named-groups", open_ended_named_compile["syntax_features"])
        self.assertEqual(open_ended_named_compile["status"], "measured")
        self.assertEqual(
            open_ended_named_compile["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(open_ended_named_compile["implementation_ns"], 0)

        open_ended_named_search = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "module-search-named-quantified-alternation-open-ended-lower-bound-c-warm-str"
        )
        self.assertEqual(open_ended_named_search["operation"], "module.search")
        self.assertEqual(open_ended_named_search["pattern"], "a(?P<word>b|c){1,}d")
        self.assertEqual(open_ended_named_search["haystack"], "zzacdzz")
        self.assertEqual(open_ended_named_search["status"], "measured")
        self.assertEqual(
            open_ended_named_search["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(open_ended_named_search["baseline_ns"], 0)
        self.assertGreater(open_ended_named_search["implementation_ns"], 0)

        open_ended_named_pattern = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-fullmatch-named-quantified-alternation-open-ended-fourth-repetition-bcbc-purged-str"
        )
        self.assertEqual(open_ended_named_pattern["operation"], "pattern.fullmatch")
        self.assertEqual(open_ended_named_pattern["cache_mode"], "purged")
        self.assertIn("named-groups", open_ended_named_pattern["syntax_features"])
        self.assertEqual(open_ended_named_pattern["haystack"], "abcbcd")
        self.assertEqual(open_ended_named_pattern["status"], "measured")
        self.assertEqual(
            open_ended_named_pattern["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(open_ended_named_pattern["implementation_ns"], 0)

        numbered_backtracking_compile = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-compile-numbered-quantified-alternation-backtracking-heavy-cold-str"
        )
        self.assertEqual(numbered_backtracking_compile["operation"], "module.compile")
        self.assertEqual(numbered_backtracking_compile["cache_mode"], "cold")
        self.assertIn("alternation", numbered_backtracking_compile["syntax_features"])
        self.assertEqual(numbered_backtracking_compile["status"], "measured")
        self.assertEqual(
            numbered_backtracking_compile["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(numbered_backtracking_compile["implementation_ns"], 0)

        numbered_backtracking_search = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "module-search-numbered-quantified-alternation-backtracking-heavy-lower-bound-b-branch-warm-str"
        )
        self.assertEqual(numbered_backtracking_search["operation"], "module.search")
        self.assertEqual(numbered_backtracking_search["pattern"], "a(b|bc){1,2}d")
        self.assertEqual(numbered_backtracking_search["haystack"], "zzabdzz")
        self.assertEqual(numbered_backtracking_search["status"], "measured")
        self.assertEqual(
            numbered_backtracking_search["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(numbered_backtracking_search["baseline_ns"], 0)
        self.assertGreater(numbered_backtracking_search["implementation_ns"], 0)

        numbered_backtracking_pattern = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-fullmatch-numbered-quantified-alternation-backtracking-heavy-lower-bound-bc-branch-purged-str"
        )
        self.assertEqual(numbered_backtracking_pattern["operation"], "pattern.fullmatch")
        self.assertEqual(numbered_backtracking_pattern["cache_mode"], "purged")
        self.assertIn("alternation", numbered_backtracking_pattern["syntax_features"])
        self.assertEqual(numbered_backtracking_pattern["status"], "measured")
        self.assertEqual(
            numbered_backtracking_pattern["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(numbered_backtracking_pattern["implementation_ns"], 0)

        named_backtracking_compile = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-compile-named-quantified-alternation-backtracking-heavy-warm-str"
        )
        self.assertEqual(named_backtracking_compile["operation"], "module.compile")
        self.assertEqual(named_backtracking_compile["cache_mode"], "warm")
        self.assertIn("named-groups", named_backtracking_compile["syntax_features"])
        self.assertEqual(named_backtracking_compile["status"], "measured")
        self.assertEqual(
            named_backtracking_compile["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(named_backtracking_compile["implementation_ns"], 0)

        named_backtracking_search = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "module-search-named-quantified-alternation-backtracking-heavy-lower-bound-bc-branch-warm-str"
        )
        self.assertEqual(named_backtracking_search["operation"], "module.search")
        self.assertEqual(
            named_backtracking_search["pattern"],
            "a(?P<word>b|bc){1,2}d",
        )
        self.assertEqual(named_backtracking_search["haystack"], "zzabcdzz")
        self.assertEqual(named_backtracking_search["status"], "measured")
        self.assertEqual(
            named_backtracking_search["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(named_backtracking_search["baseline_ns"], 0)
        self.assertGreater(named_backtracking_search["implementation_ns"], 0)

        named_backtracking_pattern = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-fullmatch-named-quantified-alternation-backtracking-heavy-second-repetition-bc-then-b-purged-str"
        )
        self.assertEqual(named_backtracking_pattern["operation"], "pattern.fullmatch")
        self.assertEqual(named_backtracking_pattern["cache_mode"], "purged")
        self.assertIn("named-groups", named_backtracking_pattern["syntax_features"])
        self.assertEqual(named_backtracking_pattern["status"], "measured")
        self.assertEqual(
            named_backtracking_pattern["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(named_backtracking_pattern["implementation_ns"], 0)

        numbered_nested_branch_compile = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-compile-numbered-quantified-alternation-nested-branch-cold-str"
        )
        self.assertEqual(numbered_nested_branch_compile["operation"], "module.compile")
        self.assertEqual(numbered_nested_branch_compile["cache_mode"], "cold")
        self.assertIn("alternation", numbered_nested_branch_compile["syntax_features"])
        self.assertEqual(numbered_nested_branch_compile["status"], "measured")
        self.assertEqual(
            numbered_nested_branch_compile["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(numbered_nested_branch_compile["implementation_ns"], 0)

        numbered_nested_branch_search = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "module-search-numbered-quantified-alternation-nested-branch-lower-bound-inner-branch-warm-str"
        )
        self.assertEqual(numbered_nested_branch_search["operation"], "module.search")
        self.assertEqual(numbered_nested_branch_search["pattern"], "a((b|c)|de){1,2}d")
        self.assertEqual(numbered_nested_branch_search["haystack"], "zzabdzz")
        self.assertEqual(numbered_nested_branch_search["status"], "measured")
        self.assertEqual(
            numbered_nested_branch_search["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(numbered_nested_branch_search["baseline_ns"], 0)
        self.assertGreater(numbered_nested_branch_search["implementation_ns"], 0)

        numbered_nested_branch_pattern = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-fullmatch-numbered-quantified-alternation-nested-branch-lower-bound-literal-branch-purged-str"
        )
        self.assertEqual(numbered_nested_branch_pattern["operation"], "pattern.fullmatch")
        self.assertEqual(numbered_nested_branch_pattern["cache_mode"], "purged")
        self.assertIn("alternation", numbered_nested_branch_pattern["syntax_features"])
        self.assertEqual(numbered_nested_branch_pattern["status"], "measured")
        self.assertEqual(
            numbered_nested_branch_pattern["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(numbered_nested_branch_pattern["implementation_ns"], 0)

        named_nested_branch_compile = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-compile-named-quantified-alternation-nested-branch-warm-str"
        )
        self.assertEqual(named_nested_branch_compile["operation"], "module.compile")
        self.assertEqual(named_nested_branch_compile["cache_mode"], "warm")
        self.assertIn("named-groups", named_nested_branch_compile["syntax_features"])
        self.assertEqual(named_nested_branch_compile["status"], "measured")
        self.assertEqual(named_nested_branch_compile["implementation_timing"]["status"], "measured")
        self.assertGreater(named_nested_branch_compile["implementation_ns"], 0)

        named_nested_branch_search = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "module-search-named-quantified-alternation-nested-branch-lower-bound-literal-branch-warm-str"
        )
        self.assertEqual(named_nested_branch_search["operation"], "module.search")
        self.assertEqual(
            named_nested_branch_search["pattern"],
            "a(?P<word>(b|c)|de){1,2}d",
        )
        self.assertEqual(named_nested_branch_search["haystack"], "zzadedzz")
        self.assertEqual(named_nested_branch_search["status"], "measured")
        self.assertEqual(named_nested_branch_search["implementation_timing"]["status"], "measured")
        self.assertGreater(named_nested_branch_search["baseline_ns"], 0)
        self.assertGreater(named_nested_branch_search["implementation_ns"], 0)

        named_nested_branch_pattern = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-fullmatch-named-quantified-alternation-nested-branch-second-repetition-mixed-purged-str"
        )
        self.assertEqual(named_nested_branch_pattern["operation"], "pattern.fullmatch")
        self.assertEqual(named_nested_branch_pattern["cache_mode"], "purged")
        self.assertIn("named-groups", named_nested_branch_pattern["syntax_features"])
        self.assertEqual(named_nested_branch_pattern["status"], "measured")
        self.assertEqual(named_nested_branch_pattern["implementation_timing"]["status"], "measured")
        self.assertGreater(named_nested_branch_pattern["implementation_ns"], 0)

        numbered_branch_compile = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-compile-numbered-quantified-alternation-branch-backref-cold-str"
        )
        self.assertEqual(numbered_branch_compile["operation"], "module.compile")
        self.assertEqual(numbered_branch_compile["cache_mode"], "cold")
        self.assertIn("branch-local-backreferences", numbered_branch_compile["syntax_features"])
        self.assertEqual(numbered_branch_compile["status"], "measured")
        self.assertEqual(numbered_branch_compile["implementation_timing"]["status"], "measured")
        self.assertGreater(numbered_branch_compile["implementation_ns"], 0)

        numbered_branch_search = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-search-numbered-quantified-alternation-branch-backref-cold-str"
        )
        self.assertEqual(numbered_branch_search["operation"], "module.search")
        self.assertEqual(numbered_branch_search["pattern"], "a((b|c)\\2){1,2}d")
        self.assertEqual(numbered_branch_search["status"], "measured")
        self.assertEqual(numbered_branch_search["implementation_timing"]["status"], "measured")
        self.assertGreater(numbered_branch_search["baseline_ns"], 0)
        self.assertGreater(numbered_branch_search["implementation_ns"], 0)

        numbered_branch_pattern = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-fullmatch-numbered-quantified-alternation-branch-backref-second-repetition-purged-str"
        )
        self.assertEqual(numbered_branch_pattern["operation"], "pattern.fullmatch")
        self.assertEqual(numbered_branch_pattern["cache_mode"], "purged")
        self.assertIn("branch-local-backreferences", numbered_branch_pattern["syntax_features"])
        self.assertEqual(numbered_branch_pattern["status"], "measured")
        self.assertEqual(numbered_branch_pattern["implementation_timing"]["status"], "measured")
        self.assertGreater(numbered_branch_pattern["implementation_ns"], 0)

        named_branch_compile = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-compile-named-quantified-alternation-branch-backref-warm-str"
        )
        self.assertEqual(named_branch_compile["operation"], "module.compile")
        self.assertEqual(named_branch_compile["cache_mode"], "warm")
        self.assertIn("branch-local-backreferences", named_branch_compile["syntax_features"])
        self.assertEqual(named_branch_compile["status"], "measured")
        self.assertEqual(named_branch_compile["implementation_timing"]["status"], "measured")
        self.assertGreater(named_branch_compile["implementation_ns"], 0)

        named_branch_search = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "module-search-named-quantified-alternation-branch-backref-lower-bound-c-branch-warm-str"
        )
        self.assertEqual(named_branch_search["operation"], "module.search")
        self.assertEqual(
            named_branch_search["pattern"],
            "a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d",
        )
        self.assertEqual(named_branch_search["status"], "measured")
        self.assertEqual(named_branch_search["implementation_timing"]["status"], "measured")
        self.assertGreater(named_branch_search["baseline_ns"], 0)
        self.assertGreater(named_branch_search["implementation_ns"], 0)

        named_branch_pattern = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-fullmatch-named-quantified-alternation-branch-backref-second-repetition-purged-str"
        )
        self.assertEqual(named_branch_pattern["operation"], "pattern.fullmatch")
        self.assertEqual(named_branch_pattern["cache_mode"], "purged")
        self.assertIn("branch-local-backreferences", named_branch_pattern["syntax_features"])
        self.assertEqual(named_branch_pattern["status"], "measured")
        self.assertEqual(named_branch_pattern["implementation_timing"]["status"], "measured")
        self.assertGreater(named_branch_pattern["implementation_ns"], 0)

        numbered_conditional_compile = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-compile-numbered-quantified-alternation-conditional-cold-str"
        )
        self.assertEqual(numbered_conditional_compile["operation"], "module.compile")
        self.assertEqual(numbered_conditional_compile["cache_mode"], "cold")
        self.assertIn("conditionals", numbered_conditional_compile["syntax_features"])
        self.assertEqual(numbered_conditional_compile["status"], "measured")
        self.assertEqual(numbered_conditional_compile["implementation_timing"]["status"], "measured")
        self.assertGreater(numbered_conditional_compile["implementation_ns"], 0)

        numbered_conditional_search = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "module-search-numbered-quantified-alternation-conditional-lower-bound-b-warm-str"
        )
        self.assertEqual(numbered_conditional_search["operation"], "module.search")
        self.assertEqual(numbered_conditional_search["pattern"], "a((b|c){1,2})?(?(1)d|e)")
        self.assertEqual(numbered_conditional_search["haystack"], "zzabdzz")
        self.assertEqual(numbered_conditional_search["status"], "measured")
        self.assertEqual(numbered_conditional_search["implementation_timing"]["status"], "measured")
        self.assertGreater(numbered_conditional_search["baseline_ns"], 0)
        self.assertGreater(numbered_conditional_search["implementation_ns"], 0)

        numbered_conditional_pattern = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-fullmatch-numbered-quantified-alternation-conditional-second-repetition-mixed-purged-str"
        )
        self.assertEqual(numbered_conditional_pattern["operation"], "pattern.fullmatch")
        self.assertEqual(numbered_conditional_pattern["cache_mode"], "purged")
        self.assertIn("conditionals", numbered_conditional_pattern["syntax_features"])
        self.assertEqual(numbered_conditional_pattern["status"], "measured")
        self.assertEqual(numbered_conditional_pattern["implementation_timing"]["status"], "measured")
        self.assertGreater(numbered_conditional_pattern["implementation_ns"], 0)

        named_conditional_compile = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-compile-named-quantified-alternation-conditional-warm-str"
        )
        self.assertEqual(named_conditional_compile["operation"], "module.compile")
        self.assertEqual(named_conditional_compile["cache_mode"], "warm")
        self.assertIn("named-groups", named_conditional_compile["syntax_features"])
        self.assertEqual(named_conditional_compile["status"], "measured")
        self.assertEqual(named_conditional_compile["implementation_timing"]["status"], "measured")
        self.assertGreater(named_conditional_compile["implementation_ns"], 0)

        named_conditional_search = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-search-named-quantified-alternation-conditional-absent-warm-str"
        )
        self.assertEqual(named_conditional_search["operation"], "module.search")
        self.assertEqual(
            named_conditional_search["pattern"],
            "a(?P<outer>(b|c){1,2})?(?(outer)d|e)",
        )
        self.assertEqual(named_conditional_search["haystack"], "zzaezz")
        self.assertEqual(named_conditional_search["status"], "measured")
        self.assertEqual(named_conditional_search["implementation_timing"]["status"], "measured")
        self.assertGreater(named_conditional_search["baseline_ns"], 0)
        self.assertGreater(named_conditional_search["implementation_ns"], 0)

        named_conditional_pattern = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-fullmatch-named-quantified-alternation-conditional-second-repetition-c-purged-str"
        )
        self.assertEqual(named_conditional_pattern["operation"], "pattern.fullmatch")
        self.assertEqual(named_conditional_pattern["cache_mode"], "purged")
        self.assertIn("conditionals", named_conditional_pattern["syntax_features"])
        self.assertIn("named-groups", named_conditional_pattern["syntax_features"])
        self.assertEqual(named_conditional_pattern["status"], "measured")
        self.assertEqual(named_conditional_pattern["implementation_timing"]["status"], "measured")
        self.assertGreater(named_conditional_pattern["implementation_ns"], 0)


if __name__ == "__main__":
    unittest.main()
