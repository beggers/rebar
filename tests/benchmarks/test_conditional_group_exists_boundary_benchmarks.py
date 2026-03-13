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


class ConditionalGroupExistsBoundaryBenchmarkSuiteTest(unittest.TestCase):
    def test_runner_regenerates_combined_conditional_group_exists_scorecard(self) -> None:
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
                    "known_gap_count": 46,
                    "measured_workloads": 315,
                    "module_workloads": 353,
                    "parser_workloads": 8,
                    "regression_workloads": 5,
                    "total_workloads": 361,
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
        self.assertEqual(scorecard["summary"]["total_workloads"], 361)
        self.assertEqual(scorecard["summary"]["parser_workloads"], 8)
        self.assertEqual(scorecard["summary"]["module_workloads"], 353)
        self.assertEqual(scorecard["summary"]["regression_workloads"], 5)
        self.assertEqual(scorecard["summary"]["measured_workloads"], 315)
        self.assertEqual(scorecard["summary"]["known_gap_count"], 46)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["cold"], 56)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["warm"], 150)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["purged"], 155)
        self.assertEqual(scorecard["families"]["parser"]["workload_count"], 8)
        self.assertEqual(scorecard["families"]["parser"]["known_gap_count"], 3)
        self.assertEqual(scorecard["families"]["parser"]["readiness"], "partial")
        self.assertEqual(scorecard["families"]["module"]["workload_count"], 353)
        self.assertEqual(scorecard["families"]["module"]["known_gap_count"], 43)
        self.assertEqual(scorecard["families"]["module"]["readiness"], "partial")
        self.assertEqual(scorecard["families"]["module"]["cache_modes"]["cold"]["workload_count"], 52)
        self.assertEqual(scorecard["families"]["module"]["cache_modes"]["warm"]["workload_count"], 148)
        self.assertEqual(scorecard["families"]["module"]["cache_modes"]["purged"]["workload_count"], 153)
        self.assertEqual(scorecard["artifacts"]["manifest"], None)
        self.assertEqual(scorecard["artifacts"]["manifest_id"], "combined-benchmark-suite")
        self.assertEqual(scorecard["artifacts"]["manifest_schema_version"], 1)
        self.assertEqual(scorecard["artifacts"]["selection_mode"], "full")
        self.assertEqual(len(scorecard["artifacts"]["manifests"]), 29)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        manifest_summary = scorecard["manifests"]["conditional-group-exists-boundary"]
        self.assertEqual(manifest_summary["workload_count"], 50)
        self.assertEqual(manifest_summary["selected_workload_count"], 50)
        self.assertEqual(manifest_summary["measured_workloads"], 48)
        self.assertEqual(manifest_summary["known_gap_count"], 2)
        self.assertEqual(manifest_summary["readiness"], "partial")
        self.assertEqual(manifest_summary["selection_mode"], "full")
        self.assertEqual(manifest_summary["available_smoke_workload_count"], 2)
        self.assertEqual(
            manifest_summary["smoke_workload_ids"],
            [
                "module-search-numbered-conditional-group-exists-present-warm-str",
                "pattern-fullmatch-named-conditional-group-exists-absent-purged-str",
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
        self.assertIn("bounded alternation-heavy replacement", manifest_summary["notes"][1])
        self.assertIn("bounded nested two-arm", manifest_summary["notes"][1])
        self.assertIn("constant-replacement `sub()`/`subn()` paths", manifest_summary["notes"][1])
        self.assertIn("module-search, Pattern.fullmatch, and constant-replacement", manifest_summary["notes"][1])
        self.assertIn("bounded quantified `{2}` Pattern.fullmatch companion", manifest_summary["notes"][1])
        self.assertIn("bounded quantified two-arm replacement", manifest_summary["notes"][1])
        self.assertIn("bounded quantified alternation-heavy", manifest_summary["notes"][1])
        self.assertIn("alternation-heavy quantified replacement arms", manifest_summary["notes"][1])
        self.assertIn("replacement templates that read captures", manifest_summary["notes"][1])

        manifest_record = next(
            manifest
            for manifest in scorecard["artifacts"]["manifests"]
            if manifest["manifest_id"] == "conditional-group-exists-boundary"
        )
        self.assertEqual(
            manifest_record["manifest"],
            "benchmarks/workloads/conditional_group_exists_boundary.json",
        )
        self.assertEqual(
            manifest_record["smoke_workload_ids"],
            [
                "module-search-numbered-conditional-group-exists-present-warm-str",
                "pattern-fullmatch-named-conditional-group-exists-absent-purged-str",
            ],
        )

        compile_workload = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-compile-numbered-conditional-group-exists-cold-str"
        )
        self.assertEqual(compile_workload["manifest_id"], "conditional-group-exists-boundary")
        self.assertEqual(compile_workload["operation"], "module.compile")
        self.assertEqual(compile_workload["cache_mode"], "cold")
        self.assertIn("conditionals", compile_workload["syntax_features"])
        self.assertEqual(compile_workload["status"], "measured")
        self.assertEqual(compile_workload["implementation_timing"]["status"], "measured")
        self.assertGreater(compile_workload["implementation_ns"], 0)

        module_search = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-search-numbered-conditional-group-exists-present-warm-str"
        )
        self.assertEqual(module_search["operation"], "module.search")
        self.assertEqual(module_search["pattern"], "a(b)?c(?(1)d|e)")
        self.assertEqual(module_search["status"], "measured")
        self.assertEqual(module_search["implementation_timing"]["status"], "measured")
        self.assertGreater(module_search["baseline_ns"], 0)
        self.assertGreater(module_search["implementation_ns"], 0)

        named_pattern = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "pattern-fullmatch-named-conditional-group-exists-absent-purged-str"
        )
        self.assertEqual(named_pattern["operation"], "pattern.fullmatch")
        self.assertEqual(named_pattern["cache_mode"], "purged")
        self.assertIn("cache-purge", named_pattern["syntax_features"])
        self.assertEqual(named_pattern["status"], "measured")
        self.assertEqual(named_pattern["implementation_timing"]["status"], "measured")

        replacement_numbered = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-sub-numbered-conditional-group-exists-replacement-warm-gap"
        )
        self.assertEqual(replacement_numbered["operation"], "module.sub")
        self.assertEqual(replacement_numbered["pattern"], "a(b)?c(?(1)d|e)")
        self.assertEqual(replacement_numbered["haystack"], "zzabcdzz")
        self.assertEqual(replacement_numbered["replacement"], "X")
        self.assertEqual(replacement_numbered["status"], "measured")
        self.assertEqual(replacement_numbered["implementation_timing"]["status"], "measured")
        self.assertGreater(replacement_numbered["implementation_ns"], 0)

        replacement_numbered_subn = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-subn-numbered-conditional-group-exists-replacement-warm-str"
        )
        self.assertEqual(replacement_numbered_subn["operation"], "module.subn")
        self.assertEqual(replacement_numbered_subn["count"], 1)
        self.assertEqual(replacement_numbered_subn["haystack"], "zzacezz")
        self.assertEqual(replacement_numbered_subn["status"], "measured")
        self.assertEqual(replacement_numbered_subn["implementation_timing"]["status"], "measured")
        self.assertGreater(replacement_numbered_subn["implementation_ns"], 0)

        replacement_named_pattern = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "pattern-subn-named-conditional-group-exists-replacement-purged-str"
        )
        self.assertEqual(replacement_named_pattern["operation"], "pattern.subn")
        self.assertEqual(replacement_named_pattern["count"], 1)
        self.assertEqual(
            replacement_named_pattern["pattern"],
            "a(?P<word>b)?c(?(word)d|e)",
        )
        self.assertIn("named-groups", replacement_named_pattern["syntax_features"])
        self.assertEqual(replacement_named_pattern["status"], "measured")
        self.assertEqual(replacement_named_pattern["implementation_timing"]["status"], "measured")
        self.assertGreater(replacement_named_pattern["baseline_ns"], 0)
        self.assertGreater(replacement_named_pattern["implementation_ns"], 0)

        template_gap = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-sub-template-numbered-conditional-group-exists-replacement-warm-gap"
        )
        self.assertEqual(template_gap["operation"], "module.sub")
        self.assertEqual(template_gap["replacement"], "<\\1>")
        self.assertEqual(template_gap["status"], "unimplemented")
        self.assertEqual(template_gap["implementation_timing"]["status"], "unimplemented")
        self.assertIn("placeholder", template_gap["implementation_timing"]["reason"])
        self.assertIn("replacement-template", template_gap["syntax_features"])

        callable_gap = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-subn-callable-named-conditional-group-exists-replacement-purged-gap"
        )
        self.assertEqual(callable_gap["operation"], "pattern.subn")
        self.assertEqual(callable_gap["count"], 1)
        self.assertEqual(callable_gap["status"], "unimplemented")
        self.assertEqual(callable_gap["implementation_timing"]["status"], "unimplemented")
        self.assertIn("Pattern.subn()", callable_gap["implementation_timing"]["reason"])
        self.assertIn("callable-replacement", callable_gap["syntax_features"])

        alternation_replacement_gap = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "module-sub-numbered-conditional-group-exists-alternation-heavy-replacement-warm-gap"
        )
        self.assertEqual(alternation_replacement_gap["operation"], "module.sub")
        self.assertEqual(
            alternation_replacement_gap["pattern"],
            "a(b)?c(?(1)(de|df)|(eg|eh))",
        )
        self.assertEqual(alternation_replacement_gap["haystack"], "zzabcdezz")
        self.assertEqual(alternation_replacement_gap["status"], "measured")
        self.assertEqual(alternation_replacement_gap["implementation_timing"]["status"], "measured")
        self.assertGreater(alternation_replacement_gap["implementation_ns"], 0)

        alternation_replacement_subn = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "module-subn-numbered-conditional-group-exists-alternation-heavy-replacement-warm-str"
        )
        self.assertEqual(alternation_replacement_subn["operation"], "module.subn")
        self.assertEqual(alternation_replacement_subn["haystack"], "zzabcdfzz")
        self.assertEqual(alternation_replacement_subn["count"], 1)
        self.assertEqual(alternation_replacement_subn["status"], "measured")
        self.assertEqual(
            alternation_replacement_subn["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(alternation_replacement_subn["implementation_ns"], 0)

        alternation_replacement_pattern = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-subn-named-conditional-group-exists-alternation-heavy-replacement-purged-str"
        )
        self.assertEqual(alternation_replacement_pattern["operation"], "pattern.subn")
        self.assertEqual(
            alternation_replacement_pattern["pattern"],
            "a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
        )
        self.assertEqual(alternation_replacement_pattern["haystack"], "zzacehzz")
        self.assertEqual(alternation_replacement_pattern["count"], 1)
        self.assertEqual(alternation_replacement_pattern["status"], "measured")
        self.assertEqual(
            alternation_replacement_pattern["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(alternation_replacement_pattern["implementation_ns"], 0)

        nested_replacement_module_sub = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-sub-numbered-nested-conditional-group-exists-replacement-warm-gap"
        )
        self.assertEqual(nested_replacement_module_sub["operation"], "module.sub")
        self.assertEqual(
            nested_replacement_module_sub["pattern"],
            "a(b)?c(?(1)(?(1)d|e)|f)",
        )
        self.assertEqual(nested_replacement_module_sub["haystack"], "zzabcdzz")
        self.assertEqual(nested_replacement_module_sub["status"], "measured")
        self.assertEqual(
            nested_replacement_module_sub["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(nested_replacement_module_sub["implementation_ns"], 0)
        self.assertNotIn("unsupported", nested_replacement_module_sub["categories"])

        nested_replacement_module_subn = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-subn-numbered-nested-conditional-group-exists-replacement-warm-str"
        )
        self.assertEqual(nested_replacement_module_subn["operation"], "module.subn")
        self.assertEqual(nested_replacement_module_subn["haystack"], "zzacfzz")
        self.assertEqual(nested_replacement_module_subn["count"], 1)
        self.assertEqual(nested_replacement_module_subn["status"], "measured")
        self.assertEqual(
            nested_replacement_module_subn["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(nested_replacement_module_subn["implementation_ns"], 0)

        nested_replacement_pattern_sub = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "pattern-sub-numbered-nested-conditional-group-exists-replacement-purged-str"
        )
        self.assertEqual(nested_replacement_pattern_sub["operation"], "pattern.sub")
        self.assertEqual(nested_replacement_pattern_sub["cache_mode"], "purged")
        self.assertEqual(nested_replacement_pattern_sub["haystack"], "zzabcdzz")
        self.assertEqual(nested_replacement_pattern_sub["status"], "measured")
        self.assertEqual(
            nested_replacement_pattern_sub["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(nested_replacement_pattern_sub["implementation_ns"], 0)

        nested_replacement_pattern_subn = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "pattern-subn-numbered-nested-conditional-group-exists-replacement-purged-str"
        )
        self.assertEqual(nested_replacement_pattern_subn["operation"], "pattern.subn")
        self.assertEqual(nested_replacement_pattern_subn["cache_mode"], "purged")
        self.assertEqual(nested_replacement_pattern_subn["haystack"], "zzacfzz")
        self.assertEqual(nested_replacement_pattern_subn["count"], 1)
        self.assertEqual(nested_replacement_pattern_subn["status"], "measured")
        self.assertEqual(
            nested_replacement_pattern_subn["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(nested_replacement_pattern_subn["implementation_ns"], 0)

        nested_replacement_named_module_sub = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-sub-named-nested-conditional-group-exists-replacement-warm-str"
        )
        self.assertEqual(nested_replacement_named_module_sub["operation"], "module.sub")
        self.assertEqual(
            nested_replacement_named_module_sub["pattern"],
            "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
        )
        self.assertIn("named-groups", nested_replacement_named_module_sub["syntax_features"])
        self.assertEqual(nested_replacement_named_module_sub["status"], "measured")
        self.assertEqual(
            nested_replacement_named_module_sub["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(nested_replacement_named_module_sub["implementation_ns"], 0)

        nested_replacement_named_module_subn = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "module-subn-named-nested-conditional-group-exists-replacement-warm-str"
        )
        self.assertEqual(nested_replacement_named_module_subn["operation"], "module.subn")
        self.assertEqual(nested_replacement_named_module_subn["haystack"], "zzacfzz")
        self.assertEqual(nested_replacement_named_module_subn["count"], 1)
        self.assertEqual(nested_replacement_named_module_subn["status"], "measured")
        self.assertEqual(
            nested_replacement_named_module_subn["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(nested_replacement_named_module_subn["implementation_ns"], 0)

        nested_replacement_named_pattern_sub = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "pattern-sub-named-nested-conditional-group-exists-replacement-purged-str"
        )
        self.assertEqual(nested_replacement_named_pattern_sub["operation"], "pattern.sub")
        self.assertEqual(nested_replacement_named_pattern_sub["cache_mode"], "purged")
        self.assertEqual(nested_replacement_named_pattern_sub["status"], "measured")
        self.assertEqual(
            nested_replacement_named_pattern_sub["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(nested_replacement_named_pattern_sub["implementation_ns"], 0)

        nested_replacement_named_pattern_subn = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "pattern-subn-named-nested-conditional-group-exists-replacement-purged-str"
        )
        self.assertEqual(nested_replacement_named_pattern_subn["operation"], "pattern.subn")
        self.assertEqual(nested_replacement_named_pattern_subn["cache_mode"], "purged")
        self.assertEqual(nested_replacement_named_pattern_subn["count"], 1)
        self.assertEqual(nested_replacement_named_pattern_subn["status"], "measured")
        self.assertEqual(
            nested_replacement_named_pattern_subn["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(nested_replacement_named_pattern_subn["implementation_ns"], 0)

        quantified_replacement_module_sub = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "module-sub-numbered-quantified-conditional-group-exists-replacement-warm-str"
        )
        self.assertEqual(quantified_replacement_module_sub["operation"], "module.sub")
        self.assertEqual(
            quantified_replacement_module_sub["pattern"],
            "a(b)?c(?(1)d|e){2}",
        )
        self.assertEqual(quantified_replacement_module_sub["haystack"], "zzabcddzz")
        self.assertEqual(quantified_replacement_module_sub["status"], "measured")
        self.assertEqual(
            quantified_replacement_module_sub["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(quantified_replacement_module_sub["implementation_ns"], 0)

        quantified_replacement_module_subn = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "module-subn-numbered-quantified-conditional-group-exists-replacement-warm-str"
        )
        self.assertEqual(quantified_replacement_module_subn["operation"], "module.subn")
        self.assertEqual(quantified_replacement_module_subn["haystack"], "zzaceezz")
        self.assertEqual(quantified_replacement_module_subn["count"], 1)
        self.assertEqual(quantified_replacement_module_subn["status"], "measured")
        self.assertEqual(
            quantified_replacement_module_subn["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(quantified_replacement_module_subn["implementation_ns"], 0)

        quantified_replacement_pattern_sub = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-sub-numbered-quantified-conditional-group-exists-replacement-purged-str"
        )
        self.assertEqual(quantified_replacement_pattern_sub["operation"], "pattern.sub")
        self.assertEqual(quantified_replacement_pattern_sub["cache_mode"], "purged")
        self.assertEqual(quantified_replacement_pattern_sub["haystack"], "zzabcddzz")
        self.assertEqual(quantified_replacement_pattern_sub["status"], "measured")
        self.assertEqual(
            quantified_replacement_pattern_sub["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(quantified_replacement_pattern_sub["implementation_ns"], 0)

        quantified_replacement_pattern_subn = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-subn-numbered-quantified-conditional-group-exists-replacement-purged-gap"
        )
        self.assertEqual(quantified_replacement_pattern_subn["operation"], "pattern.subn")
        self.assertEqual(quantified_replacement_pattern_subn["haystack"], "zzaceezz")
        self.assertEqual(quantified_replacement_pattern_subn["count"], 1)
        self.assertEqual(quantified_replacement_pattern_subn["status"], "measured")
        self.assertEqual(
            quantified_replacement_pattern_subn["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(quantified_replacement_pattern_subn["implementation_ns"], 0)

        quantified_replacement_named_module_sub = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "module-sub-named-quantified-conditional-group-exists-replacement-warm-str"
        )
        self.assertEqual(quantified_replacement_named_module_sub["operation"], "module.sub")
        self.assertEqual(
            quantified_replacement_named_module_sub["pattern"],
            "a(?P<word>b)?c(?(word)d|e){2}",
        )
        self.assertIn("named-groups", quantified_replacement_named_module_sub["syntax_features"])
        self.assertEqual(quantified_replacement_named_module_sub["status"], "measured")
        self.assertEqual(
            quantified_replacement_named_module_sub["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(quantified_replacement_named_module_sub["implementation_ns"], 0)

        quantified_replacement_named_module_subn = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "module-subn-named-quantified-conditional-group-exists-replacement-warm-str"
        )
        self.assertEqual(quantified_replacement_named_module_subn["operation"], "module.subn")
        self.assertEqual(quantified_replacement_named_module_subn["haystack"], "zzaceezz")
        self.assertEqual(quantified_replacement_named_module_subn["count"], 1)
        self.assertEqual(quantified_replacement_named_module_subn["status"], "measured")
        self.assertEqual(
            quantified_replacement_named_module_subn["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(quantified_replacement_named_module_subn["implementation_ns"], 0)

        quantified_replacement_named_pattern_sub = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-sub-named-quantified-conditional-group-exists-replacement-purged-str"
        )
        self.assertEqual(quantified_replacement_named_pattern_sub["operation"], "pattern.sub")
        self.assertEqual(quantified_replacement_named_pattern_sub["cache_mode"], "purged")
        self.assertEqual(quantified_replacement_named_pattern_sub["status"], "measured")
        self.assertEqual(
            quantified_replacement_named_pattern_sub["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(quantified_replacement_named_pattern_sub["implementation_ns"], 0)

        quantified_replacement_named_pattern_subn = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-subn-named-quantified-conditional-group-exists-replacement-purged-str"
        )
        self.assertEqual(quantified_replacement_named_pattern_subn["operation"], "pattern.subn")
        self.assertEqual(quantified_replacement_named_pattern_subn["cache_mode"], "purged")
        self.assertEqual(quantified_replacement_named_pattern_subn["count"], 1)
        self.assertEqual(quantified_replacement_named_pattern_subn["status"], "measured")
        self.assertEqual(
            quantified_replacement_named_pattern_subn["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(quantified_replacement_named_pattern_subn["implementation_ns"], 0)

        nested_numbered = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "module-search-numbered-nested-conditional-group-exists-present-cold-str"
        )
        self.assertEqual(nested_numbered["pattern"], "a(b)?c(?(1)(?(1)d|e)|f)")
        self.assertEqual(nested_numbered["operation"], "module.search")
        self.assertEqual(nested_numbered["cache_mode"], "cold")
        self.assertEqual(nested_numbered["status"], "measured")
        self.assertEqual(nested_numbered["implementation_timing"]["status"], "measured")
        self.assertGreater(nested_numbered["baseline_ns"], 0)
        self.assertGreater(nested_numbered["implementation_ns"], 0)

        nested_numbered_pattern = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-fullmatch-numbered-nested-conditional-group-exists-absent-purged-str"
        )
        self.assertEqual(
            nested_numbered_pattern["pattern"],
            "a(b)?c(?(1)(?(1)d|e)|f)",
        )
        self.assertEqual(nested_numbered_pattern["operation"], "pattern.fullmatch")
        self.assertEqual(nested_numbered_pattern["cache_mode"], "purged")
        self.assertEqual(nested_numbered_pattern["status"], "measured")
        self.assertEqual(
            nested_numbered_pattern["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(nested_numbered_pattern["baseline_ns"], 0)
        self.assertGreater(nested_numbered_pattern["implementation_ns"], 0)

        nested_named = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "module-search-named-nested-conditional-group-exists-present-warm-str"
        )
        self.assertEqual(
            nested_named["pattern"],
            "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
        )
        self.assertEqual(nested_named["operation"], "module.search")
        self.assertEqual(nested_named["cache_mode"], "warm")
        self.assertEqual(nested_named["status"], "measured")
        self.assertEqual(nested_named["implementation_timing"]["status"], "measured")
        self.assertIn("named-groups", nested_named["syntax_features"])
        self.assertGreater(nested_named["baseline_ns"], 0)
        self.assertGreater(nested_named["implementation_ns"], 0)

        nested_named_pattern = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-fullmatch-named-nested-conditional-group-exists-absent-purged-str"
        )
        self.assertEqual(
            nested_named_pattern["pattern"],
            "a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
        )
        self.assertEqual(nested_named_pattern["operation"], "pattern.fullmatch")
        self.assertEqual(nested_named_pattern["cache_mode"], "purged")
        self.assertEqual(nested_named_pattern["status"], "measured")
        self.assertEqual(
            nested_named_pattern["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(nested_named_pattern["baseline_ns"], 0)
        self.assertGreater(nested_named_pattern["implementation_ns"], 0)

        quantified_numbered = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "pattern-fullmatch-numbered-quantified-conditional-group-exists-purged-gap"
        )
        self.assertEqual(quantified_numbered["pattern"], "a(b)?c(?(1)d|e){2}")
        self.assertEqual(quantified_numbered["status"], "measured")
        self.assertEqual(quantified_numbered["implementation_timing"]["status"], "measured")
        self.assertGreater(quantified_numbered["baseline_ns"], 0)
        self.assertGreater(quantified_numbered["implementation_ns"], 0)
        self.assertNotIn("unsupported", quantified_numbered["categories"])

        quantified_named = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"] == "pattern-fullmatch-named-quantified-conditional-group-exists-purged-str"
        )
        self.assertEqual(quantified_named["pattern"], "a(?P<word>b)?c(?(word)d|e){2}")
        self.assertEqual(quantified_named["status"], "measured")
        self.assertEqual(quantified_named["implementation_timing"]["status"], "measured")
        self.assertGreater(quantified_named["baseline_ns"], 0)
        self.assertGreater(quantified_named["implementation_ns"], 0)
        self.assertIn("named-groups", quantified_named["syntax_features"])

        alternation_numbered_search = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "module-search-numbered-conditional-group-exists-quantified-alternation-heavy-present-warm-str"
        )
        self.assertEqual(
            alternation_numbered_search["pattern"],
            "a(b)?c(?(1)(de|df)|(eg|eh)){2}",
        )
        self.assertEqual(alternation_numbered_search["haystack"], "zzabcdedezz")
        self.assertEqual(alternation_numbered_search["status"], "measured")
        self.assertEqual(
            alternation_numbered_search["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(alternation_numbered_search["implementation_ns"], 0)
        self.assertIn("quantifiers", alternation_numbered_search["syntax_features"])

        alternation_named_search = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "module-search-named-conditional-group-exists-quantified-alternation-heavy-absent-warm-str"
        )
        self.assertEqual(
            alternation_named_search["pattern"],
            "a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}",
        )
        self.assertEqual(alternation_named_search["haystack"], "zzacegegzz")
        self.assertEqual(alternation_named_search["status"], "measured")
        self.assertEqual(
            alternation_named_search["implementation_timing"]["status"],
            "measured",
        )
        self.assertIn("named-groups", alternation_named_search["syntax_features"])
        self.assertGreater(alternation_named_search["implementation_ns"], 0)

        alternation_numbered_pattern = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-fullmatch-numbered-conditional-group-exists-quantified-alternation-heavy-absent-purged-str"
        )
        self.assertEqual(
            alternation_numbered_pattern["pattern"],
            "a(b)?c(?(1)(de|df)|(eg|eh)){2}",
        )
        self.assertEqual(alternation_numbered_pattern["haystack"], "aceheh")
        self.assertEqual(alternation_numbered_pattern["status"], "measured")
        self.assertEqual(
            alternation_numbered_pattern["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(alternation_numbered_pattern["baseline_ns"], 0)
        self.assertGreater(alternation_numbered_pattern["implementation_ns"], 0)

        alternation_named_pattern = next(
            workload
            for workload in scorecard["workloads"]
            if workload["id"]
            == "pattern-fullmatch-named-conditional-group-exists-quantified-alternation-heavy-present-purged-str"
        )
        self.assertEqual(
            alternation_named_pattern["pattern"],
            "a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}",
        )
        self.assertEqual(alternation_named_pattern["haystack"], "abcdfdf")
        self.assertEqual(alternation_named_pattern["status"], "measured")
        self.assertEqual(
            alternation_named_pattern["implementation_timing"]["status"],
            "measured",
        )
        self.assertGreater(alternation_named_pattern["baseline_ns"], 0)
        self.assertGreater(alternation_named_pattern["implementation_ns"], 0)


if __name__ == "__main__":
    unittest.main()
