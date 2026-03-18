from __future__ import annotations

from collections.abc import Iterable
import pathlib
import unittest

from rebar_harness.benchmarks import BenchmarkManifest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "benchmarks" / "latest.py"

from tests.benchmarks.benchmark_expectations import (
    COUNTED_REPEAT_FULLY_MEASURED_MANIFEST_IDS,
    SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS,
    ZERO_GAP_BYTES_CASES,
    ZERO_GAP_PROMOTION_MANIFEST_IDS,
    SourceTreeCombinedPatternGroupExpectation,
    SourceTreeCombinedSliceExpectation,
    relative_manifest_path,
    representative_measured_workload_ids,
    run_source_tree_benchmark_scorecard,
    select_source_tree_combined_slice_rows,
    source_tree_combined_case,
    source_tree_combined_manifest_shape_expectation,
    source_tree_combined_manifest_representative_measured_workload_ids,
    source_tree_combined_slice_derived_manifest_ids,
    source_tree_combined_slice_expectations,
    source_tree_scorecard_case,
    source_tree_combined_slice_manifest_ids,
    source_tree_combined_target_manifest_ids,
    zero_gap_fully_measured_manifest_case,
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


class SourceTreeCombinedBoundaryBenchmarkSuiteTest(unittest.TestCase):
    maxDiff = None

    def _assert_manifest_workload_contracts(
        self,
        manifest: BenchmarkManifest,
        scorecard: dict[str, object],
        workload_expectations: Iterable[tuple[str, str]],
        *,
        subtest_label: str | None = None,
    ) -> None:
        manifest_id = manifest.manifest_id
        for workload_id, expected_status in workload_expectations:
            if subtest_label is None:
                assert_benchmark_workload_contract(
                    self,
                    find_workload_record(scorecard, workload_id),
                    manifest_id=manifest_id,
                    workload_document=find_workload_document(
                        manifest,
                        workload_id,
                    ),
                    expected_status=expected_status,
                )
                continue

            with self.subTest(**{subtest_label: workload_id}):
                assert_benchmark_workload_contract(
                    self,
                    find_workload_record(scorecard, workload_id),
                    manifest_id=manifest_id,
                    workload_document=find_workload_document(
                        manifest,
                        workload_id,
                    ),
                    expected_status=expected_status,
                )

    def _assert_zero_gap_manifest_workloads_measured(
        self,
        case,
        manifest_id: str,
        expected_measured_workload_ids: tuple[str, ...],
        expected_measured_workload_count: int,
        expected_total_workload_count: int | None = None,
    ) -> None:
        _, scorecard = run_source_tree_benchmark_scorecard(
            [case.target_manifest.path]
        )
        manifest_summary = scorecard["manifests"][manifest_id]
        self.assertEqual(manifest_summary["known_gap_count"], 0)
        self.assertEqual(
            manifest_summary["measured_workloads"],
            expected_measured_workload_count,
        )
        if expected_total_workload_count is not None:
            self.assertEqual(
                manifest_summary["workload_count"],
                expected_total_workload_count,
            )

        subtest_label: str | None = None
        if expected_total_workload_count is not None:
            subtest_label = "measured_workload_id"
        elif len(expected_measured_workload_ids) > 1:
            subtest_label = "workload_id"

        self._assert_manifest_workload_contracts(
            case.target_manifest,
            scorecard,
            (
                (workload_id, "measured")
                for workload_id in expected_measured_workload_ids
            ),
            subtest_label=subtest_label,
        )

    def _assert_zero_gap_bytes_representative_subset(
        self,
        manifest_id: str,
        expected_workload_ids: tuple[str, ...],
        expected_measured_workload_count: int,
        expected_total_workload_count: int,
    ) -> None:
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    manifest_definition.representative_measured_workload_ids,
                )

        case = source_tree_combined_case(manifest_id)
        manifest_expectation = case.manifest_expectation
        self.assertEqual(manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        for workload_id in expected_workload_ids:
            with self.subTest(public_workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    manifest_expectation.representative_measured_workload_ids,
                )

        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_measured_workload_count,
            expected_total_workload_count=expected_total_workload_count,
        )

    def _assert_zero_gap_manifest_representative_promotion(
        self,
        manifest_id: str,
    ) -> None:
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        expected_workload_ids = (
            manifest_definition.representative_measured_workload_ids
        )
        self.assertIsNotNone(expected_workload_ids)
        assert expected_workload_ids is not None
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertEqual(
            manifest_definition.representative_measured_workload_ids,
            expected_workload_ids,
        )
        self.assertEqual(
            manifest_definition.representative_known_gap_workload_ids or (),
            (),
        )

        case = source_tree_combined_case(manifest_id)
        expected_measured_workload_count = len(
            case.selected_workload_ids_for_manifest(manifest_id)
        )
        manifest_expectation = case.manifest_expectation
        self.assertEqual(manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            manifest_expectation.representative_measured_workload_ids,
            expected_workload_ids,
        )
        self.assertEqual(
            manifest_expectation.representative_known_gap_workload_ids,
            (),
        )

        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_measured_workload_count,
        )

    def test_raw_manifest_expectations_omit_empty_measured_representative_defaults(
        self,
    ) -> None:
        stored_empty_representative_ids = sorted(
            manifest_id
            for manifest_id, expectation in SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.items()
            if expectation.representative_measured_workload_ids == ()
        )
        self.assertEqual(stored_empty_representative_ids, [])

    def test_manifest_gap_inventories_derive_public_known_gap_counts(self) -> None:
        for manifest_id, manifest_definition in (
            SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.items()
        ):
            expected_ids = manifest_definition.known_gap_workload_ids
            if expected_ids is None:
                continue
            with self.subTest(manifest_id=manifest_id):
                self.assertFalse(hasattr(manifest_definition, "known_gap_count"))
                self.assertEqual(
                    source_tree_combined_case(manifest_id).manifest_expectation.known_gap_count,
                    len(expected_ids),
                )

    def test_zero_gap_manifests_omit_raw_defaults_but_public_case_restores_them(
        self,
    ) -> None:
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
            "pattern-boundary"
        ]
        self.assertFalse(hasattr(manifest_definition, "known_gap_count"))
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )

        manifest_expectation = source_tree_combined_case(
            "pattern-boundary"
        ).manifest_expectation
        self.assertEqual(manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            manifest_expectation.representative_known_gap_workload_ids,
            (),
        )

    def test_zero_default_public_manifest_expectations_restore_empty_representative_ids(
        self,
    ) -> None:
        manifest_expectation = source_tree_combined_case(
            "collection-replacement-boundary"
        ).manifest_expectation
        self.assertEqual(
            manifest_expectation.representative_measured_workload_ids,
            (),
        )

    def test_literal_flag_manifest_no_longer_classifies_ascii_pair_as_known_gaps(
        self,
    ) -> None:
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
            "literal-flag-boundary"
        ]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )

        case = source_tree_combined_case("literal-flag-boundary")
        manifest_expectation = case.manifest_expectation
        self.assertEqual(manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            manifest_expectation.representative_known_gap_workload_ids,
            (),
        )

        self._assert_zero_gap_manifest_workloads_measured(
            case,
            "literal-flag-boundary",
            (
                "module-search-ignorecase-ascii-cold-gap",
                "pattern-search-ignorecase-ascii-warm-gap",
            ),
            10,
        )

    def test_zero_gap_manifest_representative_promotions_keep_selected_rows_measured(
        self,
    ) -> None:
        for manifest_id in ZERO_GAP_PROMOTION_MANIFEST_IDS:
            with self.subTest(manifest_id=manifest_id):
                self._assert_zero_gap_manifest_representative_promotion(
                    manifest_id
                )

    def test_literal_flag_combined_case_preserves_expected_manifest_paths(self) -> None:
        case = source_tree_combined_case("literal-flag-boundary")

        self.assertEqual(
            [manifest.path.name for manifest in case.manifests],
            [
                "compile_matrix.py",
                "module_boundary.py",
                "pattern_boundary.py",
                "collection_replacement_boundary.py",
                "literal_flag_boundary.py",
                "regression_matrix.py",
            ],
        )
        self.assertEqual(
            [relative_manifest_path(manifest.path) for manifest in case.manifests],
            [
                "benchmarks/workloads/compile_matrix.py",
                "benchmarks/workloads/module_boundary.py",
                "benchmarks/workloads/pattern_boundary.py",
                "benchmarks/workloads/collection_replacement_boundary.py",
                "benchmarks/workloads/literal_flag_boundary.py",
                "benchmarks/workloads/regression_matrix.py",
            ],
        )

    def test_counted_repeat_manifests_promote_legacy_upper_bound_rows_to_measured(
        self,
    ) -> None:
        for manifest_id in COUNTED_REPEAT_FULLY_MEASURED_MANIFEST_IDS:
            (
                _,
                expected_workload_ids,
                expected_measured_workload_count,
                _,
            ) = zero_gap_fully_measured_manifest_case(manifest_id)
            with self.subTest(manifest_id=manifest_id):
                manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
                    manifest_id
                ]
                self.assertIsNone(manifest_definition.known_gap_workload_ids)
                self.assertEqual(
                    manifest_definition.representative_measured_workload_ids,
                    expected_workload_ids,
                )
                self.assertEqual(
                    manifest_definition.representative_known_gap_workload_ids,
                    (),
                )

                case = source_tree_combined_case(manifest_id)
                manifest_expectation = case.manifest_expectation
                self.assertEqual(manifest_expectation.known_gap_count, 0)
                self.assertEqual(
                    manifest_expectation.representative_measured_workload_ids,
                    expected_workload_ids,
                )
                self.assertEqual(
                    manifest_expectation.representative_known_gap_workload_ids,
                    (),
                )

                self._assert_zero_gap_manifest_workloads_measured(
                    case,
                    manifest_id,
                    expected_workload_ids,
                    expected_measured_workload_count,
                )

    def test_zero_gap_bytes_manifest_promotions_keep_selected_rows_publicly_measured(
        self,
    ) -> None:
        for (
            manifest_id,
            expected_workload_ids,
            expected_measured_workload_count,
            expected_total_workload_count,
        ) in ZERO_GAP_BYTES_CASES:
            with self.subTest(manifest_id=manifest_id):
                self._assert_zero_gap_bytes_representative_subset(
                    manifest_id,
                    expected_workload_ids,
                    expected_measured_workload_count,
                    expected_total_workload_count,
                )

    def test_quantified_alternation_manifest_promotes_bounded_conditional_nested_branch_broader_range_open_ended_and_backtracking_heavy_bytes_rows_to_measured(
        self,
    ) -> None:
        (
            manifest_id,
            expected_workload_ids,
            expected_measured_workload_count,
            expected_total_workload_count,
        ) = zero_gap_fully_measured_manifest_case(
            "quantified-alternation-boundary"
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertEqual(
            manifest_definition.representative_measured_workload_ids,
            expected_workload_ids,
        )
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )

        case = source_tree_combined_case(manifest_id)
        manifest_expectation = case.manifest_expectation
        self.assertEqual(manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            manifest_expectation.representative_measured_workload_ids,
            expected_workload_ids,
        )
        self.assertEqual(
            manifest_expectation.representative_known_gap_workload_ids,
            (),
        )

        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_measured_workload_count,
            expected_total_workload_count=expected_total_workload_count,
        )

    def test_shape_backed_manifests_keep_derived_representatives(self) -> None:
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
            "pattern-boundary"
        ]
        shape_expectation = source_tree_combined_manifest_shape_expectation(
            "pattern-boundary"
        )
        self.assertIs(manifest_definition.shape_expectation, shape_expectation)
        self.assertEqual(
            source_tree_combined_manifest_representative_measured_workload_ids(
                "pattern-boundary"
            ),
            shape_expectation.representative_measured_workload_ids,
        )

    def test_regression_manifest_is_fully_measured_on_the_shared_surface(self) -> None:
        scorecard_case = source_tree_scorecard_case("regression-pack-full")
        self.assertEqual(
            scorecard_case.manifest_expectations["regression-matrix"].known_gap_count,
            0,
        )

        _, scorecard = run_source_tree_benchmark_scorecard(
            [REPO_ROOT / "benchmarks" / "workloads" / "regression_matrix.py"]
        )

        manifest_summary = scorecard["manifests"]["regression-matrix"]
        self.assertEqual(manifest_summary["known_gap_count"], 0)
        self.assertEqual(manifest_summary["measured_workloads"], 5)

        self._assert_manifest_workload_contracts(
            scorecard_case.manifest_for_id("regression-matrix"),
            scorecard,
            (("regression-parser-bytes-backreference-purged", "measured"),),
        )

    def test_scoped_manifests_keep_slice_backed_representatives(self) -> None:
        for manifest_id in source_tree_combined_slice_derived_manifest_ids():
            with self.subTest(manifest_id=manifest_id):
                case = source_tree_combined_case(manifest_id)
                self.assertEqual(
                    case.manifest_expectation.representative_measured_workload_ids,
                    (),
                )
                self.assertEqual(
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                    tuple(
                        workload_id
                        for expectation in source_tree_combined_slice_expectations(
                            manifest_id
                        )
                        for workload_id in expectation.expected_workload_ids
                    ),
                )

    def test_runner_regenerates_combined_source_tree_boundary_scorecards(self) -> None:
        for target_manifest_id in source_tree_combined_target_manifest_ids():
            with self.subTest(manifest_id=target_manifest_id):
                case = source_tree_combined_case(target_manifest_id)
                manifest_expectation = case.manifest_expectation
                summary, scorecard = run_source_tree_benchmark_scorecard(
                    [manifest.path for manifest in case.manifests],
                )

                assert_source_tree_benchmark_contract(
                    self,
                    scorecard,
                    summary,
                    expected_phase=case.expected_phase,
                    expected_runner_version=case.expected_runner_version,
                    expected_adapter=case.expected_adapter,
                    expected_manifests=case.manifests,
                    expected_manifest_paths=[
                        relative_manifest_path(manifest.path)
                        for manifest in case.manifests
                    ],
                    expected_selection_mode=case.selection_mode,
                    tracked_report_path=TRACKED_REPORT_PATH,
                )
                self.assertEqual(summary, case.expected_summary)

                manifest_id = case.manifest_id
                manifest_summary = scorecard["manifests"][manifest_id]
                manifest_record = find_manifest_record(scorecard, manifest_id)
                assert_benchmark_manifest_contract(
                    self,
                    manifest_summary,
                    manifest_record,
                    manifest=case.target_manifest,
                    manifest_path=relative_manifest_path(case.target_manifest.path),
                    known_gap_count=manifest_expectation.known_gap_count,
                    selection_mode=case.selection_mode,
                    selected_workload_ids=case.selected_workload_ids_for_manifest(
                        manifest_id
                    ),
                )

                representative_ids = representative_measured_workload_ids(
                    scorecard,
                    case.target_manifest,
                    extra_workload_ids=manifest_expectation.representative_measured_workload_ids,
                )
                representative_gap_ids = set(
                    manifest_expectation.representative_known_gap_workload_ids
                )
                representative_ids.extend(
                    manifest_expectation.representative_known_gap_workload_ids
                )

                seen_ids: set[str] = set()
                workload_expectations: list[tuple[str, str]] = []
                for workload_id in representative_ids:
                    if workload_id in seen_ids:
                        continue
                    seen_ids.add(workload_id)
                    workload_expectations.append(
                        (
                            workload_id,
                            (
                                "unimplemented"
                                if workload_id in representative_gap_ids
                                else "measured"
                            ),
                        )
                    )

                self._assert_manifest_workload_contracts(
                    case.target_manifest,
                    scorecard,
                    workload_expectations,
                )

    def test_selected_combined_source_tree_manifest_slices_stay_covered(self) -> None:
        for manifest_id in source_tree_combined_slice_manifest_ids():
            with self.subTest(manifest_id=manifest_id):
                case = source_tree_combined_case(manifest_id)
                _, scorecard = run_source_tree_benchmark_scorecard(
                    [manifest.path for manifest in case.manifests]
                )

                manifest_summary = scorecard["manifests"][manifest_id]
                self.assertEqual(
                    manifest_summary["known_gap_count"],
                    case.manifest_expectation.known_gap_count,
                )

                for expectation in source_tree_combined_slice_expectations(manifest_id):
                    with self.subTest(slice_id=expectation.slice_id):
                        self._assert_source_tree_combined_manifest_slice(
                            case.target_manifest,
                            scorecard,
                            expectation=expectation,
                        )

    def _assert_source_tree_combined_manifest_slice(
        self,
        manifest: BenchmarkManifest,
        scorecard: dict[str, object],
        *,
        expectation: SourceTreeCombinedSliceExpectation,
    ) -> None:
        manifest_id = expectation.manifest_id
        expected_workload_ids = expectation.expected_workload_ids
        expected_status = expectation.expected_status
        matched_rows = select_source_tree_combined_slice_rows(
            manifest,
            expectation,
        )

        self.assertEqual(
            tuple(workload.workload_id for workload in matched_rows),
            expected_workload_ids,
        )
        self.assertEqual(
            {workload.pattern for workload in matched_rows},
            expectation.expected_patterns,
        )
        self.assertEqual(
            {workload.operation for workload in matched_rows},
            expectation.expected_operations,
        )
        self.assertEqual(
            {
                str(workload.haystack)
                for workload in matched_rows
                if workload.haystack is not None
            },
            expectation.expected_haystacks,
        )

        for workload in matched_rows:
            with self.subTest(
                slice_id=expectation.slice_id,
                workload_id=workload.workload_id,
            ):
                for category in expectation.required_row_categories:
                    self.assertIn(category, workload.categories)

        scorecard_rows = [
            workload
            for workload in scorecard["workloads"]
            if workload["manifest_id"] == manifest_id
            and workload["id"] in expected_workload_ids
        ]
        self.assertEqual(
            {workload["id"] for workload in scorecard_rows},
            set(expected_workload_ids),
        )

        with self.subTest(slice_id=expectation.slice_id):
            self._assert_manifest_workload_contracts(
                manifest,
                scorecard,
                (
                    (workload_id, expected_status)
                    for workload_id in expected_workload_ids
                ),
                subtest_label="workload_id",
            )

    def test_wider_ranged_repeat_manifest_shape_stays_covered_in_combined_suite(
        self,
    ) -> None:
        case = source_tree_combined_case(WIDER_RANGED_REPEAT_MANIFEST_ID)
        shape_expectation = source_tree_combined_manifest_shape_expectation(
            WIDER_RANGED_REPEAT_MANIFEST_ID
        )
        _, scorecard = run_source_tree_benchmark_scorecard(
            [manifest.path for manifest in case.manifests]
        )

        manifest_summary = scorecard["manifests"][WIDER_RANGED_REPEAT_MANIFEST_ID]
        self.assertEqual(manifest_summary["known_gap_count"], 0)
        self.assertEqual(
            manifest_summary["measured_workloads"],
            len(case.target_manifest.workloads),
        )
        self.assertEqual(
            manifest_summary["workload_count"],
            len(case.target_manifest.workloads),
        )

        self._assert_manifest_workload_contracts(
            case.target_manifest,
            scorecard,
            (
                (workload_id, "measured")
                for workload_id in shape_expectation.representative_measured_workload_ids
            ),
            subtest_label="workload_id",
        )

        for pattern_group in shape_expectation.pattern_groups:
            with self.subTest(slice_id=pattern_group.slice_id):
                self._assert_source_tree_combined_pattern_group(
                    case.target_manifest,
                    scorecard,
                    manifest_id=WIDER_RANGED_REPEAT_MANIFEST_ID,
                    expectation=pattern_group,
                )

    def _assert_source_tree_combined_pattern_group(
        self,
        manifest: BenchmarkManifest,
        scorecard: dict[str, object],
        *,
        manifest_id: str,
        expectation: SourceTreeCombinedPatternGroupExpectation,
    ) -> None:
        slice_id = expectation.slice_id
        patterns = expectation.patterns
        required_operations = expectation.required_operations
        required_categories = expectation.required_categories
        search_haystacks = expectation.search_haystacks
        search_haystack_substrings = expectation.search_haystack_substrings
        pattern_haystacks = expectation.pattern_haystacks
        manifest_rows = [
            workload
            for workload in manifest.workloads
            if workload.pattern in patterns
        ]

        self.assertGreaterEqual(
            len(manifest_rows),
            expectation.minimum_rows,
            f"expected benchmark rows for the {slice_id} slice",
        )

        for pattern in patterns:
            pattern_rows = [
                workload for workload in manifest_rows if workload.pattern == pattern
            ]
            self.assertGreaterEqual(
                len(pattern_rows),
                3,
                f"expected compile/search/fullmatch coverage for {pattern!r}",
            )
            self.assertTrue(
                set(required_operations).issubset(
                    {workload.operation for workload in pattern_rows}
                )
            )
            for workload in pattern_rows:
                with self.subTest(pattern=pattern, workload_id=workload.workload_id):
                    for category in required_categories:
                        self.assertIn(category, workload.categories)

        manifest_search_haystacks = {
            str(workload.haystack)
            for workload in manifest_rows
            if workload.operation == "module.search"
        }
        for haystack in search_haystacks:
            self.assertIn(haystack, manifest_search_haystacks)
        for snippet in search_haystack_substrings:
            self.assertTrue(
                any(snippet in haystack for haystack in manifest_search_haystacks),
                f"expected a module.search workload covering {snippet!r}",
            )

        manifest_pattern_haystacks = {
            str(workload.haystack)
            for workload in manifest_rows
            if workload.operation == "pattern.fullmatch"
        }
        for haystack in pattern_haystacks:
            self.assertIn(haystack, manifest_pattern_haystacks)

        scorecard_rows = [
            workload
            for workload in scorecard["workloads"]
            if workload["manifest_id"] == manifest_id
            and workload["pattern"] in patterns
        ]
        self.assertEqual(
            {workload["id"] for workload in scorecard_rows},
            {workload.workload_id for workload in manifest_rows},
        )
        for workload in scorecard_rows:
            with self.subTest(scorecard_workload_id=workload["id"]):
                self.assertEqual(workload["status"], "measured")
                self.assertEqual(workload["implementation_timing"]["status"], "measured")
                self.assertGreater(workload["implementation_ns"], 0)


if __name__ == "__main__":
    unittest.main()
