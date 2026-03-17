from __future__ import annotations

import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "benchmarks" / "latest.py"

from tests.benchmarks.benchmark_expectations import (
    SOURCE_TREE_SCORECARD_EXPECTATIONS,
    SourceTreeScorecardCase,
    relative_manifest_path,
    run_source_tree_benchmark_scorecard,
    source_tree_combined_case,
    source_tree_combined_manifest_representative_measured_workload_ids,
    source_tree_combined_slice_expectations,
    source_tree_scorecard_case,
    source_tree_scorecard_case_ids,
)
from tests.report_assertions import (
    assert_benchmark_manifest_contract,
    assert_benchmark_workload_contract,
    assert_source_tree_benchmark_contract,
    find_manifest_record,
    find_workload_document,
    find_workload_record,
)


def _case_manifest_paths(case: SourceTreeScorecardCase) -> list[pathlib.Path]:
    return [manifest.path for manifest in case.manifests]


def _case_relative_manifest_paths(case: SourceTreeScorecardCase) -> list[str]:
    return [relative_manifest_path(manifest.path) for manifest in case.manifests]


class SourceTreeBenchmarkScorecardTest(unittest.TestCase):
    maxDiff = None

    def test_raw_scorecard_case_definitions_use_direct_manifest_ids(self) -> None:
        for case_id, case_definition in SOURCE_TREE_SCORECARD_EXPECTATIONS.items():
            with self.subTest(case_id=case_id):
                self.assertFalse(isinstance(case_definition, dict))
                self.assertFalse(hasattr(case_definition, "full_manifest_ids"))
                self.assertTrue(hasattr(case_definition, "manifest_ids"))
                self.assertGreaterEqual(len(case_definition.manifest_ids), 1)
                self.assertIn(case_definition.selection_mode, {"full", "smoke"})

    def test_full_scorecard_cases_derive_known_gap_counts_from_manifest_inventories(
        self,
    ) -> None:
        case = source_tree_scorecard_case("post-parser-workflows")
        self.assertEqual(
            case.manifest_expectations["literal-flag-boundary"].known_gap_count,
            0,
        )

    def test_post_parser_workflows_promote_ignorecase_ascii_pair_to_measured_representatives(
        self,
    ) -> None:
        case = source_tree_scorecard_case("post-parser-workflows")
        for workload_id in (
            "module-search-ignorecase-ascii-cold-gap",
            "pattern-search-ignorecase-ascii-warm-gap",
        ):
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_regression_pack_full_promotes_bytes_backreference_probe_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("regression-pack-full")
        self.assertIn(
            "regression-parser-bytes-backreference-purged",
            case.representative_measured_workload_ids,
        )
        self.assertNotIn(
            "regression-parser-bytes-backreference-purged",
            case.representative_known_gap_workload_ids,
        )

    def test_numbered_backreference_manifest_promotes_grouped_segment_pair_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("numbered-backreference-boundary")
        self.assertEqual(
            case.manifest_expectations["numbered-backreference-boundary"].known_gap_count,
            0,
        )
        self.assertEqual(
            case.representative_measured_workload_ids,
            (
                "module-search-numbered-backreference-segment-cold-gap",
                "pattern-search-numbered-backreference-prefix-purged-gap",
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())

    def test_nested_group_manifest_promotes_nested_pair_to_measured(self) -> None:
        case = source_tree_scorecard_case("nested-group-boundary")
        self.assertEqual(
            case.manifest_expectations["nested-group-boundary"].known_gap_count,
            0,
        )
        self.assertEqual(
            case.representative_measured_workload_ids,
            (
                "module-search-triple-nested-group-cold-gap",
                "pattern-fullmatch-named-quantified-nested-group-purged-gap",
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())

    def test_wider_ranged_manifest_exposes_broader_range_conditional_bytes_rows_as_measured(
        self,
    ) -> None:
        manifest_id = "wider-ranged-repeat-quantified-group-boundary"
        expected_workload_ids = (
            "module-compile-numbered-wider-ranged-repeat-group-broader-range-conditional-cold-bytes",
            "module-search-numbered-wider-ranged-repeat-group-broader-range-conditional-absent-warm-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-conditional-lower-bound-bc-purged-bytes",
            "module-compile-named-wider-ranged-repeat-group-broader-range-conditional-warm-bytes",
            "module-search-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-purged-bytes",
        )
        case = source_tree_combined_case(manifest_id)
        public_representatives = (
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            )
        )

        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(case.manifest_expectation.representative_known_gap_workload_ids, ())

        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, public_representatives)
                self.assertIn(
                    workload_id,
                    case.manifest_expectation.representative_measured_workload_ids,
                )

    def test_wider_ranged_manifest_exposes_broader_range_backtracking_heavy_bytes_rows_as_measured(
        self,
    ) -> None:
        manifest_id = "wider-ranged-repeat-quantified-group-boundary"
        expected_workload_ids = (
            "module-compile-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-cold-bytes",
            "module-search-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-second-repetition-b-then-bc-purged-bytes",
            "module-compile-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-warm-bytes",
            "module-search-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-lower-bound-bc-branch-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-fourth-repetition-mixed-purged-bytes",
        )
        case = source_tree_combined_case(manifest_id)
        public_representatives = (
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            )
        )

        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(case.manifest_expectation.representative_known_gap_workload_ids, ())

        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, public_representatives)
                self.assertIn(
                    workload_id,
                    case.manifest_expectation.representative_measured_workload_ids,
                )

    def test_wider_ranged_manifest_exposes_nested_broader_range_backtracking_heavy_bytes_rows_as_measured(
        self,
    ) -> None:
        manifest_id = "wider-ranged-repeat-quantified-group-boundary"
        expected_workload_ids = (
            "module-compile-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-cold-bytes",
            "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-second-repetition-b-then-bc-purged-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-fourth-repetition-mixed-purged-bytes",
            "module-compile-named-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-warm-bytes",
            "module-search-named-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-lower-bound-bc-branch-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-bytes",
        )
        case = source_tree_combined_case(manifest_id)
        public_representatives = (
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            )
        )

        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(case.manifest_expectation.representative_known_gap_workload_ids, ())

        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, public_representatives)
                self.assertIn(
                    workload_id,
                    case.manifest_expectation.representative_measured_workload_ids,
                )

    def test_wider_ranged_manifest_exposes_nested_broader_range_grouped_alternation_bytes_rows_as_measured(
        self,
    ) -> None:
        manifest_id = "wider-ranged-repeat-quantified-group-boundary"
        expected_workload_ids = (
            "module-compile-numbered-wider-ranged-repeat-group-nested-broader-range-cold-bytes",
            "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-lower-bound-bc-warm-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-third-repetition-mixed-purged-bytes",
            "module-compile-named-wider-ranged-repeat-group-nested-broader-range-warm-bytes",
            "module-search-named-wider-ranged-repeat-group-nested-broader-range-lower-bound-de-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-upper-bound-all-de-purged-bytes",
        )
        case = source_tree_combined_case(manifest_id)
        public_representatives = (
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            )
        )

        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(case.manifest_expectation.representative_known_gap_workload_ids, ())

        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, public_representatives)
                self.assertIn(
                    workload_id,
                    case.manifest_expectation.representative_measured_workload_ids,
                )

    def test_combined_cases_treat_counted_repeat_manifest_pair_as_fully_measured(
        self,
    ) -> None:
        expected_cases = (
            (
                "exact-repeat-quantified-group-boundary",
                "module-search-numbered-broader-ranged-repeat-group-cold-gap",
            ),
            (
                "ranged-repeat-quantified-group-boundary",
                "module-search-numbered-ranged-repeat-group-wider-range-cold-gap",
            ),
        )

        for manifest_id, workload_id in expected_cases:
            with self.subTest(manifest_id=manifest_id):
                case = source_tree_combined_case(manifest_id)
                self.assertEqual(case.manifest_expectation.known_gap_count, 0)
                self.assertEqual(
                    case.manifest_expectation.representative_measured_workload_ids,
                    (workload_id,),
                )
                self.assertEqual(
                    case.manifest_expectation.representative_known_gap_workload_ids,
                    (),
                )

    def test_compile_smoke_case_restores_single_manifest_expectations(self) -> None:
        case = source_tree_scorecard_case("compile-smoke")
        manifest_expectation = case.manifest_expectations["compile-smoke"]
        self.assertEqual(manifest_expectation.known_gap_count, 1)
        self.assertEqual(
            manifest_expectation.representative_measured_workload_ids,
            ("compile-literal-cold",),
        )
        self.assertEqual(
            manifest_expectation.representative_known_gap_workload_ids,
            ("compile-character-class-warm",),
        )
        self.assertIsNotNone(case.expected_first_deferred)
        assert case.expected_first_deferred is not None
        self.assertEqual(case.expected_first_deferred.area, "module-boundary")
        self.assertEqual(case.expected_first_deferred.follow_up, "RBR-0015")
        self.assertFalse(hasattr(case, "workload_note_substrings"))

    def test_single_manifest_scorecards_keep_slice_backed_representatives(self) -> None:
        for case_id in (
            "nested-group-replacement-boundary",
            "nested-group-callable-replacement-boundary",
            "branch-local-backreference-boundary",
            "conditional-group-exists-boundary",
        ):
            with self.subTest(case_id=case_id):
                case = source_tree_scorecard_case(case_id)
                self.assertEqual(
                    case.representative_measured_workload_ids,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        case_id
                    ),
                )
                self.assertEqual(
                    case.representative_measured_workload_ids,
                    tuple(
                        workload_id
                        for expectation in source_tree_combined_slice_expectations(case_id)
                        for workload_id in expectation.expected_workload_ids
                    ),
                )

    def test_runner_regenerates_source_tree_scorecards(self) -> None:
        for case_id in source_tree_scorecard_case_ids():
            with self.subTest(case_id=case_id):
                case = source_tree_scorecard_case(case_id)
                summary, scorecard = run_source_tree_benchmark_scorecard(
                    _case_manifest_paths(case),
                    smoke=case.selection_mode == "smoke",
                )

                assert_source_tree_benchmark_contract(
                    self,
                    scorecard,
                    summary,
                    expected_phase=case.expected_phase,
                    expected_runner_version=case.expected_runner_version,
                    expected_adapter=case.expected_adapter,
                    expected_manifests=case.manifests,
                    expected_manifest_paths=_case_relative_manifest_paths(case),
                    expected_selection_mode=case.selection_mode,
                    tracked_report_path=TRACKED_REPORT_PATH,
                )
                self.assertEqual(summary, case.expected_summary)

                expected_first_deferred = case.expected_first_deferred
                if expected_first_deferred is not None:
                    self.assertGreaterEqual(len(scorecard["deferred"]), 1)
                    self.assertEqual(
                        scorecard["deferred"][0]["area"],
                        expected_first_deferred.area,
                    )
                    self.assertEqual(
                        scorecard["deferred"][0]["follow_up"],
                        expected_first_deferred.follow_up,
                    )

                expected_workload_order = case.expected_workload_order
                if expected_workload_order is not None:
                    self.assertEqual(
                        [workload["id"] for workload in scorecard["workloads"]],
                        list(expected_workload_order),
                    )

                self._assert_manifest_contracts(case, scorecard)
                self._assert_representative_workloads(case, scorecard)

    def _assert_manifest_contracts(
        self,
        case: SourceTreeScorecardCase,
        scorecard: dict[str, object],
    ) -> None:
        manifest_expectations = case.manifest_expectations
        for manifest_id, manifest_expectation in manifest_expectations.items():
            manifest_summary = scorecard["manifests"][manifest_id]
            manifest_record = find_manifest_record(scorecard, manifest_id)
            manifest = case.manifest_for_id(manifest_id)
            assert_benchmark_manifest_contract(
                self,
                manifest_summary,
                manifest_record,
                manifest=manifest,
                manifest_path=relative_manifest_path(manifest.path),
                known_gap_count=manifest_expectation.known_gap_count,
                selection_mode=case.selection_mode,
                selected_workload_ids=case.selected_workload_ids_by_manifest[manifest_id],
            )

    def _assert_representative_workloads(
        self,
        case: SourceTreeScorecardCase,
        scorecard: dict[str, object],
    ) -> None:
        self._assert_workloads(
            case,
            scorecard,
            case.representative_measured_workload_ids,
            expected_status="measured",
        )
        self._assert_workloads(
            case,
            scorecard,
            case.representative_known_gap_workload_ids,
            expected_status="unimplemented",
        )

    def _assert_workloads(
        self,
        case: SourceTreeScorecardCase,
        scorecard: dict[str, object],
        workload_ids: tuple[str, ...],
        *,
        expected_status: str,
    ) -> None:
        for workload_id in workload_ids:
            with self.subTest(workload_id=workload_id):
                workload_record = find_workload_record(scorecard, workload_id)
                manifest_id = workload_record["manifest_id"]
                manifest = case.manifest_for_id(manifest_id)
                assert_benchmark_workload_contract(
                    self,
                    workload_record,
                    manifest_id=manifest_id,
                    workload_document=find_workload_document(manifest, workload_id),
                    expected_status=expected_status,
                )


if __name__ == "__main__":
    unittest.main()
