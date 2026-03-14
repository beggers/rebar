from __future__ import annotations

import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "benchmarks" / "latest.py"
if str(PYTHON_SOURCE) not in sys.path:
    sys.path.append(str(PYTHON_SOURCE))

from tests.benchmarks.benchmark_expectations import (
    representative_measured_workload_ids,
    run_source_tree_benchmark_scorecard,
    source_tree_combined_case,
    source_tree_combined_target_manifest_ids,
)
from tests.report_assertions import (
    assert_benchmark_manifest_contract,
    assert_benchmark_workload_contract,
    assert_source_tree_benchmark_contract,
    find_manifest_record,
    find_workload_document,
    find_workload_record,
)

WIDER_RANGED_REPEAT_MANIFEST_ID = "wider-ranged-repeat-quantified-group-boundary"
WIDER_RANGED_REPEAT_REPRESENTATIVE_MEASURED_WORKLOAD_IDS = (
    "module-search-numbered-wider-ranged-repeat-group-broader-range-cold-gap",
    "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-upper-bound-mixed-purged-str",
    "pattern-fullmatch-numbered-wider-ranged-repeat-group-open-ended-purged-gap",
    "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-absent-warm-str",
    "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-fourth-repetition-mixed-purged-str",
)
WIDER_RANGED_REPEAT_PATTERN_GROUPS = (
    {
        "label": "nested broader-range grouped alternation",
        "patterns": (
            "a((bc|de){1,4})d",
            "a(?P<outer>(bc|de){1,4})d",
        ),
        "minimum_rows": 6,
        "required_operations": (
            "module.compile",
            "module.search",
            "pattern.fullmatch",
        ),
        "required_categories": (
            "nested-group",
            "alternation",
            "ranged-repeat",
            "broader-range",
            "counted-repeat",
        ),
        "search_haystack_substrings": (
            "abcd",
            "aded",
        ),
        "pattern_haystacks": (
            "abcbcded",
            "adedededed",
        ),
    },
    {
        "label": "nested broader-range grouped conditional",
        "patterns": (
            "a(((bc|de){1,4})d)?(?(1)e|f)",
            "a(?P<outer>((bc|de){1,4})d)?(?(outer)e|f)",
        ),
        "minimum_rows": 7,
        "required_operations": (
            "module.compile",
            "module.search",
            "pattern.fullmatch",
        ),
        "required_categories": (
            "nested-group",
            "alternation",
            "conditional",
            "optional-group",
            "ranged-repeat",
            "broader-range",
            "counted-repeat",
        ),
        "search_haystacks": (
            "zzafzz",
            "zzabcdezz",
            "zzadedezz",
        ),
        "pattern_haystacks": (
            "abcbcdede",
            "adedededede",
        ),
    },
    {
        "label": "nested broader-range grouped backtracking-heavy",
        "patterns": (
            "a(((bc|b)c){1,4})d",
            "a(?P<outer>((bc|b)c){1,4})d",
        ),
        "minimum_rows": 7,
        "required_operations": (
            "module.compile",
            "module.search",
            "pattern.fullmatch",
        ),
        "required_categories": (
            "grouped",
            "nested-group",
            "alternation",
            "backtracking-heavy",
            "ranged-repeat",
            "broader-range",
            "counted-repeat",
        ),
        "search_haystacks": (
            "zzabcdzz",
            "zzabccdzz",
        ),
        "pattern_haystacks": (
            "abcbccd",
            "abccbcd",
            "abcbccbccbcd",
        ),
    },
)


class SourceTreeCombinedBoundaryBenchmarkSuiteTest(unittest.TestCase):
    maxDiff = None

    def test_runner_regenerates_combined_source_tree_boundary_scorecards(self) -> None:
        for target_manifest_id in source_tree_combined_target_manifest_ids():
            with self.subTest(manifest_id=target_manifest_id):
                case = source_tree_combined_case(target_manifest_id)
                manifest_expectation = case["manifest_expectation"]
                summary, scorecard = run_source_tree_benchmark_scorecard(
                    case["manifest_paths"],
                )

                assert_source_tree_benchmark_contract(
                    self,
                    scorecard,
                    summary,
                    expected_phase=case["expected_phase"],
                    expected_runner_version=case["expected_runner_version"],
                    expected_adapter=case["expected_adapter"],
                    expected_manifest_documents=case["manifest_documents"],
                    expected_manifest_paths=case["expected_manifest_paths"],
                    expected_selection_mode=case["selection_mode"],
                    tracked_report_path=TRACKED_REPORT_PATH,
                )
                self.assertEqual(summary, case["expected_summary"])

                manifest_id = case["manifest_id"]
                manifest_summary = scorecard["manifests"][manifest_id]
                manifest_record = find_manifest_record(scorecard, manifest_id)
                assert_benchmark_manifest_contract(
                    self,
                    manifest_summary,
                    manifest_record,
                    manifest_document=case["target_manifest"],
                    manifest_path=case["manifest_path"],
                    known_gap_count=manifest_expectation["known_gap_count"],
                    selection_mode=case["selection_mode"],
                    selected_workload_ids=case["selected_workload_ids_by_manifest"][manifest_id],
                )

                representative_ids = representative_measured_workload_ids(
                    scorecard,
                    case["target_manifest"],
                    extra_workload_ids=manifest_expectation["representative_measured_workload_ids"],
                )
                representative_gap_ids = set(
                    manifest_expectation["representative_known_gap_workload_ids"]
                )
                representative_ids.extend(manifest_expectation["representative_known_gap_workload_ids"])

                seen_ids: set[str] = set()
                for workload_id in representative_ids:
                    if workload_id in seen_ids:
                        continue
                    seen_ids.add(workload_id)
                    expected_status = (
                        "unimplemented"
                        if workload_id in representative_gap_ids
                        else "measured"
                    )
                    assert_benchmark_workload_contract(
                        self,
                        find_workload_record(scorecard, workload_id),
                        manifest_id=manifest_id,
                        workload_document=find_workload_document(case["target_manifest"], workload_id),
                        expected_status=expected_status,
                    )

    def test_wider_ranged_repeat_manifest_shape_stays_covered_in_combined_suite(
        self,
    ) -> None:
        case = source_tree_combined_case(WIDER_RANGED_REPEAT_MANIFEST_ID)
        _, scorecard = run_source_tree_benchmark_scorecard(case["manifest_paths"])

        manifest_summary = scorecard["manifests"][WIDER_RANGED_REPEAT_MANIFEST_ID]
        self.assertEqual(manifest_summary["known_gap_count"], 0)
        self.assertEqual(
            manifest_summary["measured_workloads"],
            len(case["target_manifest"]["workloads"]),
        )
        self.assertEqual(
            manifest_summary["workload_count"],
            len(case["target_manifest"]["workloads"]),
        )

        for workload_id in WIDER_RANGED_REPEAT_REPRESENTATIVE_MEASURED_WORKLOAD_IDS:
            with self.subTest(workload_id=workload_id):
                assert_benchmark_workload_contract(
                    self,
                    find_workload_record(scorecard, workload_id),
                    manifest_id=WIDER_RANGED_REPEAT_MANIFEST_ID,
                    workload_document=find_workload_document(
                        case["target_manifest"],
                        workload_id,
                    ),
                    expected_status="measured",
                )

        for pattern_group in WIDER_RANGED_REPEAT_PATTERN_GROUPS:
            with self.subTest(group=pattern_group["label"]):
                self._assert_wider_ranged_repeat_pattern_group(
                    case["target_manifest"],
                    scorecard,
                    label=pattern_group["label"],
                    patterns=pattern_group["patterns"],
                    minimum_rows=pattern_group["minimum_rows"],
                    required_operations=pattern_group["required_operations"],
                    required_categories=pattern_group["required_categories"],
                    search_haystacks=pattern_group.get("search_haystacks", ()),
                    search_haystack_substrings=pattern_group.get(
                        "search_haystack_substrings",
                        (),
                    ),
                    pattern_haystacks=pattern_group["pattern_haystacks"],
                )

    def _assert_wider_ranged_repeat_pattern_group(
        self,
        manifest_document: dict[str, object],
        scorecard: dict[str, object],
        *,
        label: str,
        patterns: tuple[str, ...],
        minimum_rows: int,
        required_operations: tuple[str, ...],
        required_categories: tuple[str, ...],
        search_haystacks: tuple[str, ...],
        search_haystack_substrings: tuple[str, ...],
        pattern_haystacks: tuple[str, ...],
    ) -> None:
        manifest_rows = [
            workload
            for workload in manifest_document["workloads"]
            if workload.get("pattern") in patterns
        ]

        self.assertGreaterEqual(
            len(manifest_rows),
            minimum_rows,
            f"expected benchmark rows for the {label} slice",
        )

        for pattern in patterns:
            pattern_rows = [
                workload for workload in manifest_rows if workload["pattern"] == pattern
            ]
            self.assertGreaterEqual(
                len(pattern_rows),
                3,
                f"expected compile/search/fullmatch coverage for {pattern!r}",
            )
            self.assertTrue(
                set(required_operations).issubset(
                    {workload["operation"] for workload in pattern_rows}
                )
            )
            for workload in pattern_rows:
                with self.subTest(pattern=pattern, workload_id=workload["id"]):
                    for category in required_categories:
                        self.assertIn(category, workload["categories"])

        manifest_search_haystacks = {
            str(workload["haystack"])
            for workload in manifest_rows
            if workload["operation"] == "module.search"
        }
        for haystack in search_haystacks:
            self.assertIn(haystack, manifest_search_haystacks)
        for snippet in search_haystack_substrings:
            self.assertTrue(
                any(snippet in haystack for haystack in manifest_search_haystacks),
                f"expected a module.search workload covering {snippet!r}",
            )

        manifest_pattern_haystacks = {
            str(workload["haystack"])
            for workload in manifest_rows
            if workload["operation"] == "pattern.fullmatch"
        }
        for haystack in pattern_haystacks:
            self.assertIn(haystack, manifest_pattern_haystacks)

        scorecard_rows = [
            workload
            for workload in scorecard["workloads"]
            if workload["manifest_id"] == WIDER_RANGED_REPEAT_MANIFEST_ID
            and workload["pattern"] in patterns
        ]
        self.assertEqual(
            {workload["id"] for workload in scorecard_rows},
            {workload["id"] for workload in manifest_rows},
        )
        for workload in scorecard_rows:
            with self.subTest(scorecard_workload_id=workload["id"]):
                self.assertEqual(workload["status"], "measured")
                self.assertEqual(workload["implementation_timing"]["status"], "measured")
                self.assertGreater(workload["implementation_ns"], 0)


if __name__ == "__main__":
    unittest.main()
