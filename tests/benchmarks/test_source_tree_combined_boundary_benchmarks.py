from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from functools import partial
import json
import re
from typing import Any
import unittest

import pytest

from rebar_harness import benchmarks
from rebar_harness.benchmarks import (
    BenchmarkManifest,
    Workload,
    published_benchmark_manifests,
    workload_from_payload,
    workload_to_payload,
)
from tests.benchmarks.benchmark_test_support import (
    STANDARD_BENCHMARK_DEFINITIONS,
    MODULE_BOUNDARY_MANIFEST_PATH as COMPILED_PATTERN_MODULE_COMPILE_MANIFEST_PATH,
    PATTERN_BOUNDARY_MANIFEST_PATH,
    RecordingBenchmarkModule,
    _COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES,
    _COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS,
    _COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS,
    _COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS,
    _COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES,
    _assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call,
    _is_collection_replacement_keyword_workload,
    _is_collection_replacement_wrong_text_model_workload,
    _is_module_workflow_keyword_error_workload,
    _is_module_workflow_keyword_flags_workload,
    _module_workflow_keyword_correctness_case_signature,
    _module_workflow_keyword_workload_signature,
    compiled_pattern_contract_expected_build_calls,
    _expected_exception_instance,
    _record_numeric_materialization_fields,
    _source_tree_contract_manifest,
    _source_tree_contract_workload,
    _write_test_manifest,
    _definition_anchor_expectations,
    _workload_case_pair_anchor_expectations,
    anchored_workload_case_ids,
    assert_benchmark_workload_matches_expected_result,
    assert_benchmark_workload_contract,
    assert_zero_gap_manifest_workloads_measured,
    compile_proxy_correctness_case_signature,
    expected_anchored_workload_case_pairs,
    compile_proxy_workload_signature,
    find_workload_document,
    find_workload_record,
    is_compile_proxy_workload,
    published_case_ids_by_signature,
    run_benchmark_workload_with_cpython,
    selected_manifest_workloads,
    StandardBenchmarkAnchorContractDefinition,
    unanchored_workload_ids,
    _is_module_workflow_compiled_pattern_bounded_wildcard_success_workload,
    _is_module_workflow_compiled_pattern_literal_success_workload,
    _is_module_workflow_compiled_pattern_verbose_bytes_success_workload,
    _is_module_workflow_compiled_pattern_wrong_text_model_workload,
    _is_pattern_bounded_wildcard_workload,
    _is_pattern_boundary_wrong_text_model_workload,
    _is_pattern_keyword_window_workload,
    _is_pattern_verbose_regression_workload,
    _is_pattern_window_positional_indexlike_workload,
    _module_workflow_compiled_pattern_correctness_case_signature,
    _module_workflow_compiled_pattern_workload_signature,
    _pattern_bounded_wildcard_correctness_case_signature,
    _pattern_bounded_wildcard_workload_signature,
    _pattern_boundary_wrong_text_model_correctness_case_signature,
    _pattern_boundary_wrong_text_model_workload_signature,
    _pattern_keyword_window_correctness_case_signature,
    _pattern_keyword_window_workload_signature,
    _pattern_verbose_regression_correctness_case_signature,
    _pattern_verbose_regression_workload_signature,
    _pattern_window_positional_indexlike_correctness_case_signature,
    _pattern_window_positional_indexlike_workload_signature,
)
from tests.benchmarks import benchmark_test_support as compiled_pattern_module_helper_support
from tests.benchmarks.collection_replacement_benchmark_anchor_support import \
    _COLLECTION_REPLACEMENT_GROUPED_CALLABLE_WORKLOAD_CASE_PAIRS, \
    _COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_ROUTES, \
    _COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_SELECTOR, \
    _COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES, \
    _COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_SELECTOR, \
    CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_STR_WORKLOAD_IDS, \
    CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS, \
    CONDITIONAL_GROUP_EXISTS_CALLABLE_BYTES_WORKLOAD_IDS, \
    CONDITIONAL_GROUP_EXISTS_CALLABLE_NEGATIVE_COUNT_BYTES_WORKLOAD_IDS, \
    CONDITIONAL_GROUP_EXISTS_CALLABLE_NEGATIVE_COUNT_STR_WORKLOAD_IDS, \
    CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS, \
    CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS, \
    CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_IDS, \
    CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS, \
    CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS, \
    CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS, \
    CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS, \
    CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS, \
    CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS, \
    CONDITIONAL_GROUP_EXISTS_TEMPLATE_ROUND_TRIP_WORKLOAD_IDS, \
    _collection_replacement_compiled_pattern_success_correctness_case_signature, \
    _collection_replacement_compiled_pattern_success_workload_signature, \
    _collection_replacement_grouped_callable_correctness_case_signature, \
    _collection_replacement_grouped_callable_workload_signature, \
    _collection_replacement_literal_replacement_correctness_case_signature, \
    _collection_replacement_literal_replacement_workload_signature, \
    _collection_replacement_keyword_correctness_case_signature, \
    _conditional_group_exists_nested_callable_correctness_case_signature, \
    _conditional_group_exists_nested_callable_workload_signature, \
    _conditional_group_exists_quantified_callable_correctness_case_signature, \
    _conditional_group_exists_quantified_callable_workload_signature, \
    _collection_replacement_pattern_wrong_text_model_correctness_case_signature, \
    _collection_replacement_pattern_wrong_text_model_workload_signature, \
    _is_collection_replacement_compiled_pattern_success_workload, \
    _collection_replacement_keyword_workload_signature, \
    _collection_replacement_positional_indexlike_workload_signature, \
    _collection_replacement_wrong_text_model_correctness_case_signature, \
    _collection_replacement_wrong_text_model_workload_signature, \
    _is_collection_replacement_grouped_callable_workload, \
    _is_collection_replacement_pattern_wrong_text_model_workload, \
    _is_collection_replacement_positional_indexlike_workload, \
    _module_workflow_positional_indexlike_correctness_case_signature, \
    _workload_ids_for_text_model
from tests.benchmarks.source_tree_benchmark_anchor_support import SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS, SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS, SOURCE_TREE_SCORECARD_EXPECTATIONS, SourceTreeBenchmarkCommonCase, SourceTreeCombinedCase, SourceTreeCombinedFullyMeasuredManifestExpectation, SourceTreeCombinedManifestExpectationDefinition, SourceTreeCombinedManifestShapeExpectation, SourceTreeCombinedPatternGroupExpectation, SourceTreeCombinedSliceExpectation
from tests.benchmarks.source_tree_benchmark_anchor_support import SourceTreeDeferredExpectation, SourceTreeManifestExpectation, SourceTreeScorecardCase, _combined_fully_measured_manifest_expectation, _combined_manifest_definition, _is_non_alternation_counted_repeat_workload, _counted_repeat_correctness_case_signature, _counted_repeat_workload_signature, _grouped_alternation_correctness_case_signature, _grouped_alternation_replacement_correctness_case_signature
from tests.benchmarks.source_tree_benchmark_anchor_support import _conditional_group_exists_alternation_callable_bytes_workloads, _conditional_group_exists_alternation_callable_replacement_expectation, _conditional_group_exists_callable_bytes_slice_workloads, _conditional_group_exists_callable_replacement_expectations, _conditional_group_exists_callable_str_slice_workloads, _conditional_group_exists_nested_callable_bytes_replacement_expectation, _conditional_group_exists_nested_callable_bytes_workloads, _conditional_group_exists_nested_callable_replacement_expectation, _conditional_group_exists_nested_callable_str_workloads, _conditional_group_exists_quantified_callable_bytes_replacement_expectation, _conditional_group_exists_quantified_callable_bytes_workloads, _conditional_group_exists_quantified_callable_replacement_expectation, _conditional_group_exists_quantified_callable_str_workloads, _conditional_group_exists_template_replacement_expectation, _grouped_alternation_workload_signature, _is_optional_group_conditional_workload, _mirrored_bytes_workload_ids, _nested_group_correctness_case_signature, _nested_group_workload_signature, _optional_group_correctness_case_signature, _optional_group_workload_signature, _OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID as OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID, _selected_workload_ids, _split_workload_ids_by_text_model, _text_model_agnostic_callable_match_group_signature, assert_benchmark_manifest_contract, assert_source_tree_benchmark_contract
from tests.benchmarks.source_tree_benchmark_anchor_support import expected_summary_for_manifests, find_manifest_record, relative_manifest_path, representative_measured_workload_ids, select_source_tree_combined_slice_rows, source_tree_combined_case, source_tree_combined_fully_measured_manifest_expectation, source_tree_combined_fully_measured_manifest_ids, source_tree_combined_manifest_representative_measured_workload_ids
from tests.benchmarks.source_tree_benchmark_anchor_support import source_tree_combined_manifest_shape_expectation, source_tree_combined_slice_derived_manifest_ids, source_tree_combined_slice_expectations, source_tree_combined_slice_manifest_ids, source_tree_combined_target_manifest_ids, source_tree_scorecard_case, source_tree_scorecard_case_ids
from tests.conftest import (
    REPO_ROOT,
    records_by_string_id,
    run_harness_scorecard,
)
from tests.python.fixture_parity_support import (
    BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    OPEN_ENDED_ALTERNATION_BYTES_CASES,
    OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    callable_match_group_signature,
)
TRACKED_REPORT_PATH = benchmarks.SCORECARD_REPORT.published_path

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
        _, scorecard = run_harness_scorecard(
            "rebar_harness.benchmarks",
            ["--manifest", str(case.target_manifest.path)],
            report_name="benchmarks.json",
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
    ) -> None:
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        public_representatives = (
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            )
        )
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        self.assertIn(
            expected_workload_ids,
            manifest_definition.zero_gap_bytes_representative_subsets,
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, public_representatives)
                if manifest_definition.representative_measured_workload_ids is not None:
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
        expected_measured_workload_count = len(
            case.selected_workload_ids_for_manifest(manifest_id)
        )
        expected_total_workload_count = len(case.target_manifest.workloads)
        self.assertEqual(
            expected_measured_workload_count,
            expected_total_workload_count,
        )
        for workload_id in expected_workload_ids:
            with self.subTest(public_workload_id=workload_id):
                self.assertIn(workload_id, public_representatives)
                if manifest_expectation.representative_measured_workload_ids:
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
        promotion_manifest_ids = tuple(
            manifest_id
            for manifest_id in source_tree_combined_target_manifest_ids()
            if SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
                manifest_id
            ].promote_zero_gap_representatives
        )
        self.assertEqual(
            promotion_manifest_ids,
            (
                "grouped-named-boundary",
                "numbered-backreference-boundary",
                "nested-group-boundary",
                "optional-group-boundary",
            ),
        )
        for manifest_id in promotion_manifest_ids:
            with self.subTest(manifest_id=manifest_id):
                self._assert_zero_gap_manifest_representative_promotion(
                    manifest_id
                )

    def test_combined_target_manifest_ids_exclude_only_definition_owned_base_manifests(
        self,
    ) -> None:
        excluded_manifest_ids = tuple(
            manifest.manifest_id
            for manifest in published_benchmark_manifests()
            if SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
                manifest.manifest_id
            ].exclude_from_combined_targets
        )
        self.assertEqual(
            excluded_manifest_ids,
            ("compile-matrix", "regression-matrix"),
        )
        self.assertEqual(
            source_tree_combined_target_manifest_ids(),
            tuple(
                manifest.manifest_id
                for manifest in published_benchmark_manifests()
                if not SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
                    manifest.manifest_id
                ].exclude_from_combined_targets
            ),
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
        for manifest_id in source_tree_combined_fully_measured_manifest_ids(
            "counted-repeat"
        ):
            fully_measured_expectation = (
                source_tree_combined_fully_measured_manifest_expectation(manifest_id)
            )
            expected_workload_ids = (
                fully_measured_expectation.representative_measured_workload_ids
            )
            expected_measured_workload_count = (
                fully_measured_expectation.expected_measured_workload_count
            )
            with self.subTest(manifest_id=manifest_id):
                manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
                    manifest_id
                ]
                self.assertIsNone(manifest_definition.known_gap_workload_ids)
                self.assertEqual(
                    manifest_definition.fully_measured_expectation,
                    fully_measured_expectation,
                )
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
        zero_gap_bytes_subsets_by_manifest = {
            manifest_id: manifest_definition.zero_gap_bytes_representative_subsets
            for manifest_id, manifest_definition in (
                SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.items()
            )
            if manifest_definition.zero_gap_bytes_representative_subsets
        }
        expected_subset_counts = {
            "conditional-group-exists-boundary": 5,
            "wider-ranged-repeat-quantified-group-boundary": 6,
            "open-ended-quantified-group-boundary": 5,
            "branch-local-backreference-boundary": 1,
        }
        self.assertEqual(
            {
                manifest_id: len(representative_subsets)
                for manifest_id, representative_subsets in (
                    zero_gap_bytes_subsets_by_manifest.items()
                )
            },
            expected_subset_counts,
        )
        self.assertEqual(
            sum(
                len(representative_subsets)
                for representative_subsets in zero_gap_bytes_subsets_by_manifest.values()
            ),
            sum(expected_subset_counts.values()),
        )
        for manifest_id, representative_subsets in zero_gap_bytes_subsets_by_manifest.items():
            for expected_workload_ids in representative_subsets:
                with self.subTest(manifest_id=manifest_id):
                    self._assert_zero_gap_bytes_representative_subset(
                        manifest_id,
                        expected_workload_ids,
                    )

    def test_nested_group_callable_replacement_manifest_promotes_bounded_nested_group_bytes_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-callable-replacement-boundary"
        expected_workload_ids = (
            "module-sub-callable-nested-group-numbered-warm-bytes",
            "module-subn-callable-nested-group-numbered-warm-bytes",
            "pattern-sub-callable-nested-group-numbered-purged-bytes",
            "pattern-subn-callable-nested-group-numbered-purged-bytes",
            "module-sub-callable-nested-group-named-warm-bytes",
            "module-subn-callable-nested-group-named-warm-bytes",
            "pattern-sub-callable-nested-group-named-purged-bytes",
            "pattern-subn-callable-nested-group-named-purged-bytes",
        )

        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )

        case = source_tree_combined_case(manifest_id)
        expected_workload_count = len(
            case.selected_workload_ids_for_manifest(manifest_id)
        )
        public_representatives = (
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            )
        )
        manifest_expectation = case.manifest_expectation
        self.assertEqual(manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self.assertEqual(manifest_expectation.representative_measured_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(public_workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    public_representatives,
                )

        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_conditional_group_exists_template_bytes_manifest_promotes_minimal_replacement_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        template_expectation = (
            _conditional_group_exists_template_replacement_expectation()
        )
        case = source_tree_combined_case(manifest_id)
        matched_rows = tuple(
            select_source_tree_combined_slice_rows(
                case.target_manifest,
                template_expectation,
            )
        )
        expected_workload_ids = template_expectation.expected_workload_ids
        expected_workload_count = len(case.selected_workload_ids_for_manifest(manifest_id))

        self.assertEqual(
            tuple(workload.workload_id for workload in matched_rows),
            expected_workload_ids,
        )
        self.assertEqual({workload.text_model for workload in matched_rows}, {"str", "bytes"})
        for workload_id in CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_conditional_group_exists_template_bytes_workloads_keep_bytes_template_payloads_through_round_trip(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        case = source_tree_combined_case(manifest_id)
        workloads_by_id = records_by_string_id(
            (
                workload
                for workload in case.target_manifest.workloads
                if workload.workload_id
                in CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS
                or workload.workload_id
                in CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS
            ),
            id_attr="workload_id",
        )

        self.assertEqual(
            tuple(workloads_by_id),
            CONDITIONAL_GROUP_EXISTS_TEMPLATE_ROUND_TRIP_WORKLOAD_IDS,
        )

        for workload_id in CONDITIONAL_GROUP_EXISTS_TEMPLATE_ROUND_TRIP_WORKLOAD_IDS:
            expected_serialized_replacement = "\\g<word>x" if "-named-" in workload_id else "\\1x"
            expected_text_model = "bytes" if workload_id.endswith("-bytes") else "str"
            expected_template_payload = (
                b"\\g<word>x"
                if "-named-" in workload_id and workload_id.endswith("-bytes")
                else "\\g<word>x"
                if "-named-" in workload_id
                else b"\\1x"
                if workload_id.endswith("-bytes")
                else "\\1x"
            )
            if "negative-count" in workload_id:
                expected_count = -1
                expected_result = (
                    (b"abcdaceabcd", 0)
                    if workload_id.endswith("-bytes") and "-subn-" in workload_id
                    else ("abcdaceabcd", 0)
                    if "-subn-" in workload_id
                    else b"abcdaceabcd"
                    if workload_id.endswith("-bytes")
                    else "abcdaceabcd"
                )
            else:
                expected_count = 1 if "-subn-" in workload_id else 0
                expected_result = (
                    (b"zzxzz", 1)
                    if workload_id.endswith("-bytes") and "-subn-" in workload_id
                    else ("zzxzz", 1)
                    if "-subn-" in workload_id
                    else b"zzbxzz"
                    if workload_id.endswith("-bytes")
                    else "zzbxzz"
                )

            with self.subTest(workload_id=workload_id):
                workload = workloads_by_id[workload_id]
                payload = workload_to_payload(workload)
                round_tripped = workload_from_payload(payload)

                self.assertEqual(workload.text_model, expected_text_model)
                self.assertEqual(payload["text_model"], expected_text_model)
                self.assertEqual(payload["replacement"], expected_serialized_replacement)
                self.assertEqual(payload["count"], expected_count)
                self.assertIsInstance(
                    workload.pattern_payload(),
                    bytes if workload_id.endswith("-bytes") else str,
                )
                self.assertIsInstance(
                    workload.haystack_payload(),
                    bytes if workload_id.endswith("-bytes") else str,
                )
                self.assertEqual(
                    workload.replacement_payload(),
                    expected_template_payload,
                )
                self.assertEqual(
                    run_benchmark_workload_with_cpython(workload),
                    expected_result,
                )

                self.assertEqual(round_tripped.text_model, expected_text_model)
                self.assertEqual(round_tripped.count, expected_count)
                self.assertIsInstance(
                    round_tripped.pattern_payload(),
                    bytes if workload_id.endswith("-bytes") else str,
                )
                self.assertIsInstance(
                    round_tripped.haystack_payload(),
                    bytes if workload_id.endswith("-bytes") else str,
                )
                self.assertEqual(
                    round_tripped.replacement_payload(),
                    expected_template_payload,
                )
                self.assertEqual(
                    run_benchmark_workload_with_cpython(round_tripped),
                    expected_result,
                )

    def test_conditional_group_exists_callable_bytes_manifest_promotes_replacement_and_exception_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        expected_workload_ids = CONDITIONAL_GROUP_EXISTS_CALLABLE_BYTES_WORKLOAD_IDS
        case = source_tree_combined_case(manifest_id)
        expected_workload_count = len(case.selected_workload_ids_for_manifest(manifest_id))
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_conditional_group_exists_callable_none_count_bytes_manifest_promotes_rows_to_measured(
        self,
    ) -> None:
        self._assert_zero_gap_bytes_representative_subset(
            "conditional-group-exists-boundary",
            CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS,
        )

    def test_conditional_group_exists_nested_callable_str_manifest_promotes_replacement_and_exception_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        expectation = _conditional_group_exists_nested_callable_replacement_expectation()
        case = source_tree_combined_case(manifest_id)
        matched_rows = tuple(
            select_source_tree_combined_slice_rows(case.target_manifest, expectation)
        )
        expected_workload_ids = CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS
        expected_workload_count = len(case.selected_workload_ids_for_manifest(manifest_id))

        self.assertEqual(
            tuple(workload.workload_id for workload in matched_rows),
            expected_workload_ids,
        )
        self.assertEqual({workload.text_model for workload in matched_rows}, {"str"})
        self.assertEqual(
            Counter((workload.operation, workload.count) for workload in matched_rows),
            Counter(
                {
                    ("module.sub", 0): 4,
                    ("module.sub", None): 1,
                    ("module.sub", -1): 1,
                    ("module.subn", 1): 4,
                    ("module.subn", None): 1,
                    ("module.subn", -1): 1,
                    ("pattern.sub", 0): 4,
                    ("pattern.sub", None): 1,
                    ("pattern.sub", -1): 1,
                    ("pattern.subn", 1): 4,
                    ("pattern.subn", None): 1,
                    ("pattern.subn", -1): 1,
                }
            ),
        )
        self.assertEqual(
            Counter("exception" in workload.categories for workload in matched_rows),
            Counter({False: 16, True: 8}),
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_conditional_group_exists_nested_callable_bytes_manifest_promotes_replacement_and_exception_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        expected_workload_ids = CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS
        self._assert_zero_gap_bytes_representative_subset(
            manifest_id,
            expected_workload_ids,
        )

    def test_conditional_group_exists_quantified_callable_str_manifest_promotes_replacement_and_exception_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        expectation = _conditional_group_exists_quantified_callable_replacement_expectation()
        case = source_tree_combined_case(manifest_id)
        matched_rows = tuple(
            select_source_tree_combined_slice_rows(case.target_manifest, expectation)
        )
        expected_workload_ids = CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS
        expected_workload_count = len(case.selected_workload_ids_for_manifest(manifest_id))

        self.assertEqual(
            tuple(workload.workload_id for workload in matched_rows),
            expected_workload_ids,
        )
        self.assertEqual({workload.text_model for workload in matched_rows}, {"str"})
        self.assertEqual(
            Counter((workload.operation, workload.count) for workload in matched_rows),
            Counter(
                {
                    ("module.sub", 0): 4,
                    ("module.sub", None): 1,
                    ("module.sub", -1): 4,
                    ("module.subn", 1): 4,
                    ("module.subn", None): 1,
                    ("module.subn", -1): 4,
                    ("pattern.sub", 0): 4,
                    ("pattern.sub", None): 1,
                    ("pattern.sub", -1): 4,
                    ("pattern.subn", 1): 4,
                    ("pattern.subn", None): 1,
                    ("pattern.subn", -1): 4,
                }
            ),
        )
        self.assertEqual(
            Counter("exception" in workload.categories for workload in matched_rows),
            Counter({False: 28, True: 8}),
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_conditional_group_exists_quantified_callable_bytes_manifest_promotes_replacement_and_exception_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        expected_workload_ids = (
            CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS
        )
        self._assert_zero_gap_bytes_representative_subset(
            manifest_id,
            expected_workload_ids,
        )

    def test_conditional_group_exists_nested_callable_str_workloads_round_trip_preserves_outcomes(
        self,
    ) -> None:
        source_workloads = _conditional_group_exists_nested_callable_str_workloads()

        self.assertEqual(
            tuple(workload.workload_id for workload in source_workloads),
            CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS,
        )

        for source_workload in source_workloads:
            with self.subTest(workload_id=source_workload.workload_id):
                payload = workload_to_payload(source_workload)
                round_tripped = workload_from_payload(payload)
                expected_signature = callable_match_group_signature(
                    source_workload.replacement_payload()
                )
                observed_signature = callable_match_group_signature(
                    round_tripped.replacement_payload()
                )

                self.assertEqual(payload["text_model"], "str")
                self.assertEqual(round_tripped.text_model, "str")
                self.assertEqual(payload["count"], source_workload.count)
                self.assertEqual(round_tripped.count, source_workload.count)
                self.assertEqual(
                    payload["expected_exception"],
                    source_workload.expected_exception,
                )
                self.assertEqual(
                    round_tripped.expected_exception,
                    source_workload.expected_exception,
                )
                self.assertEqual(
                    round_tripped.pattern_payload(),
                    source_workload.pattern_payload(),
                )
                self.assertEqual(
                    round_tripped.haystack_payload(),
                    source_workload.haystack_payload(),
                )
                self.assertEqual(observed_signature, expected_signature)
                self.assertIsNotNone(observed_signature)
                assert observed_signature is not None
                self.assertIsInstance(observed_signature[2], str)
                self.assertIsInstance(observed_signature[3], str)

                if source_workload.expected_exception is None:
                    assert_benchmark_workload_matches_expected_result(
                        round_tripped,
                        run_benchmark_workload_with_cpython(source_workload),
                    )
                    continue

                expected_exception = source_workload.expected_exception
                assert expected_exception is not None

                with pytest.raises(
                    TypeError,
                    match=re.escape(expected_exception["message_substring"]),
                ) as expected_error:
                    run_benchmark_workload_with_cpython(source_workload)
                with pytest.raises(TypeError) as observed_error:
                    run_benchmark_workload_with_cpython(round_tripped)
                self.assertEqual(
                    str(observed_error.value),
                    str(expected_error.value),
                )

    def test_conditional_group_exists_nested_callable_bytes_workloads_round_trip_preserves_outcomes(
        self,
    ) -> None:
        source_workloads = _conditional_group_exists_nested_callable_bytes_workloads()

        self.assertEqual(
            tuple(workload.workload_id for workload in source_workloads),
            CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS,
        )

        def normalized_text_model_payload(value: str | bytes | None) -> str | None:
            if isinstance(value, bytes):
                return value.decode("latin-1")
            return value

        for source_workload in source_workloads:
            workload_id = source_workload.workload_id
            expected_replacement = {
                "type": "callable_match_group",
                "group": "word" if "-named-" in workload_id else 1,
                "suffix": "x",
            }
            expected_signature = (
                "callable_match_group",
                expected_replacement["group"],
                b"",
                b"x",
            )

            with self.subTest(workload_id=workload_id):
                payload = workload_to_payload(source_workload)
                round_tripped = workload_from_payload(payload)
                observed_signature = callable_match_group_signature(
                    round_tripped.replacement_payload()
                )

                self.assertEqual(payload["text_model"], "bytes")
                self.assertEqual(round_tripped.text_model, "bytes")
                self.assertEqual(payload["replacement"], expected_replacement)
                self.assertEqual(payload["count"], source_workload.count)
                self.assertEqual(round_tripped.count, source_workload.count)
                self.assertEqual(
                    payload["expected_exception"],
                    source_workload.expected_exception,
                )
                self.assertEqual(
                    round_tripped.expected_exception,
                    source_workload.expected_exception,
                )
                self.assertEqual(
                    normalized_text_model_payload(payload["pattern"]),
                    source_workload.pattern,
                )
                self.assertEqual(
                    normalized_text_model_payload(payload["haystack"]),
                    source_workload.haystack,
                )
                self.assertEqual(
                    normalized_text_model_payload(round_tripped.pattern),
                    source_workload.pattern,
                )
                self.assertEqual(
                    normalized_text_model_payload(round_tripped.haystack),
                    source_workload.haystack,
                )
                self.assertEqual(
                    callable_match_group_signature(
                        source_workload.replacement_payload()
                    ),
                    expected_signature,
                )
                self.assertEqual(observed_signature, expected_signature)
                self.assertIsNotNone(observed_signature)
                assert observed_signature is not None
                self.assertIsInstance(observed_signature[2], bytes)
                self.assertIsInstance(observed_signature[3], bytes)
                if source_workload.expected_exception is None:
                    expected_result = run_benchmark_workload_with_cpython(
                        source_workload
                    )
                    assert_benchmark_workload_matches_expected_result(
                        round_tripped,
                        expected_result,
                    )
                    continue

                expected_exception = source_workload.expected_exception
                assert expected_exception is not None

                with pytest.raises(
                    TypeError,
                    match=re.escape(expected_exception["message_substring"]),
                ) as expected_error:
                    run_benchmark_workload_with_cpython(source_workload)
                with pytest.raises(TypeError) as observed_error:
                    run_benchmark_workload_with_cpython(round_tripped)
                self.assertEqual(
                    str(observed_error.value),
                    str(expected_error.value),
                )

    def test_conditional_group_exists_nested_callable_workloads_anchor_to_unique_published_cases(
        self,
    ) -> None:
        workloads = (
            _conditional_group_exists_nested_callable_str_workloads()
            + _conditional_group_exists_nested_callable_bytes_workloads()
        )
        case_ids_by_signature = published_case_ids_by_signature(
            _conditional_group_exists_nested_callable_correctness_case_signature
        )
        anchored_case_ids: list[str] = []

        for workload in workloads:
            signature = _conditional_group_exists_nested_callable_workload_signature(
                workload
            )
            with self.subTest(workload_id=workload.workload_id):
                case_ids = case_ids_by_signature.get(signature)
                self.assertIsNotNone(
                    case_ids,
                    f"missing published correctness case for {workload.workload_id!r}",
                )
                assert case_ids is not None
                self.assertEqual(
                    len(case_ids),
                    1,
                    f"expected a unique published case for {workload.workload_id!r}",
                )
                anchored_case_ids.append(case_ids[0])

        self.assertEqual(len(anchored_case_ids), len(workloads))
        self.assertEqual(len(set(anchored_case_ids)), len(anchored_case_ids))

    def test_conditional_group_exists_quantified_callable_str_workloads_round_trip_preserves_outcomes(
        self,
    ) -> None:
        source_workloads = _conditional_group_exists_quantified_callable_str_workloads()

        self.assertEqual(
            tuple(workload.workload_id for workload in source_workloads),
            CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS,
        )

        for source_workload in source_workloads:
            with self.subTest(workload_id=source_workload.workload_id):
                payload = workload_to_payload(source_workload)
                round_tripped = workload_from_payload(payload)
                expected_signature = callable_match_group_signature(
                    source_workload.replacement_payload()
                )
                observed_signature = callable_match_group_signature(
                    round_tripped.replacement_payload()
                )

                self.assertEqual(payload["text_model"], "str")
                self.assertEqual(round_tripped.text_model, "str")
                self.assertEqual(payload["count"], source_workload.count)
                self.assertEqual(round_tripped.count, source_workload.count)
                self.assertEqual(
                    payload["expected_exception"],
                    source_workload.expected_exception,
                )
                self.assertEqual(
                    round_tripped.expected_exception,
                    source_workload.expected_exception,
                )
                self.assertEqual(
                    round_tripped.pattern_payload(),
                    source_workload.pattern_payload(),
                )
                self.assertEqual(
                    round_tripped.haystack_payload(),
                    source_workload.haystack_payload(),
                )
                self.assertEqual(observed_signature, expected_signature)
                self.assertIsNotNone(observed_signature)
                assert observed_signature is not None
                self.assertIsInstance(observed_signature[2], str)
                self.assertIsInstance(observed_signature[3], str)

                if source_workload.expected_exception is None:
                    assert_benchmark_workload_matches_expected_result(
                        round_tripped,
                        run_benchmark_workload_with_cpython(source_workload),
                    )
                    continue

                expected_exception = source_workload.expected_exception
                assert expected_exception is not None

                with pytest.raises(
                    TypeError,
                    match=re.escape(expected_exception["message_substring"]),
                ) as expected_error:
                    run_benchmark_workload_with_cpython(source_workload)
                with pytest.raises(TypeError) as observed_error:
                    run_benchmark_workload_with_cpython(round_tripped)
                self.assertEqual(
                    str(observed_error.value),
                    str(expected_error.value),
                )

    def test_conditional_group_exists_quantified_callable_bytes_workloads_round_trip_preserves_outcomes(
        self,
    ) -> None:
        source_workloads = _conditional_group_exists_quantified_callable_bytes_workloads()

        self.assertEqual(
            tuple(workload.workload_id for workload in source_workloads),
            CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS,
        )

        for source_workload in source_workloads:
            with self.subTest(workload_id=source_workload.workload_id):
                payload = workload_to_payload(source_workload)
                round_tripped = workload_from_payload(payload)
                expected_signature = callable_match_group_signature(
                    source_workload.replacement_payload()
                )
                observed_signature = callable_match_group_signature(
                    round_tripped.replacement_payload()
                )

                self.assertEqual(payload["text_model"], "bytes")
                self.assertEqual(round_tripped.text_model, "bytes")
                self.assertEqual(payload["count"], source_workload.count)
                self.assertEqual(
                    payload["expected_exception"],
                    source_workload.expected_exception,
                )
                self.assertEqual(
                    round_tripped.expected_exception,
                    source_workload.expected_exception,
                )
                self.assertEqual(
                    round_tripped.pattern_payload(),
                    source_workload.pattern_payload(),
                )
                self.assertEqual(
                    round_tripped.haystack_payload(),
                    source_workload.haystack_payload(),
                )
                self.assertEqual(observed_signature, expected_signature)

                if source_workload.expected_exception is None:
                    assert_benchmark_workload_matches_expected_result(
                        round_tripped,
                        run_benchmark_workload_with_cpython(source_workload),
                    )
                    continue

                expected_exception = source_workload.expected_exception
                assert expected_exception is not None

                with pytest.raises(
                    TypeError,
                    match=re.escape(expected_exception["message_substring"]),
                ) as expected_error:
                    run_benchmark_workload_with_cpython(source_workload)
                with pytest.raises(TypeError) as observed_error:
                    run_benchmark_workload_with_cpython(round_tripped)
                self.assertEqual(
                    str(observed_error.value),
                    str(expected_error.value),
                )

    def test_conditional_group_exists_quantified_callable_workloads_anchor_to_unique_published_cases(
        self,
    ) -> None:
        workloads = (
            _conditional_group_exists_quantified_callable_str_workloads()
            + _conditional_group_exists_quantified_callable_bytes_workloads()
        )
        case_ids_by_signature = published_case_ids_by_signature(
            _conditional_group_exists_quantified_callable_correctness_case_signature
        )
        anchored_case_ids: list[str] = []

        for workload in workloads:
            signature = _conditional_group_exists_quantified_callable_workload_signature(
                workload
            )
            with self.subTest(workload_id=workload.workload_id):
                case_ids = case_ids_by_signature.get(signature)
                self.assertIsNotNone(
                    case_ids,
                    f"missing published correctness case for {workload.workload_id!r}",
                )
                assert case_ids is not None
                self.assertEqual(
                    len(case_ids),
                    1,
                    f"expected a unique published case for {workload.workload_id!r}",
                )
                anchored_case_ids.append(case_ids[0])

        self.assertEqual(len(anchored_case_ids), len(workloads))
        self.assertEqual(len(set(anchored_case_ids)), len(anchored_case_ids))

    def test_conditional_group_exists_callable_str_slice_workloads_round_trip_preserves_outcomes(
        self,
    ) -> None:
        source_workloads = _conditional_group_exists_callable_str_slice_workloads()

        self.assertEqual(
            tuple(workload.workload_id for workload in source_workloads),
            tuple(
                workload_id
                for expectation in _conditional_group_exists_callable_replacement_expectations()
                for workload_id in expectation.expected_workload_ids
                if not workload_id.endswith("-bytes")
            ),
        )

        for source_workload in source_workloads:
            with self.subTest(workload_id=source_workload.workload_id):
                payload = workload_to_payload(source_workload)
                round_tripped = workload_from_payload(payload)
                expected_signature = callable_match_group_signature(
                    source_workload.replacement_payload()
                )
                observed_signature = callable_match_group_signature(
                    round_tripped.replacement_payload()
                )

                self.assertEqual(payload["text_model"], "str")
                self.assertEqual(round_tripped.text_model, "str")
                self.assertEqual(payload["count"], source_workload.count)
                self.assertEqual(round_tripped.count, source_workload.count)
                self.assertEqual(
                    payload["expected_exception"],
                    source_workload.expected_exception,
                )
                self.assertEqual(
                    round_tripped.expected_exception,
                    source_workload.expected_exception,
                )
                self.assertEqual(
                    round_tripped.pattern_payload(),
                    source_workload.pattern_payload(),
                )
                self.assertEqual(
                    round_tripped.haystack_payload(),
                    source_workload.haystack_payload(),
                )
                self.assertEqual(observed_signature, expected_signature)
                self.assertIsNotNone(observed_signature)
                assert observed_signature is not None
                self.assertIsInstance(observed_signature[2], str)
                self.assertIsInstance(observed_signature[3], str)

                if source_workload.expected_exception is None:
                    assert_benchmark_workload_matches_expected_result(
                        round_tripped,
                        run_benchmark_workload_with_cpython(source_workload),
                    )
                    continue

                expected_exception = source_workload.expected_exception
                assert expected_exception is not None

                with pytest.raises(
                    TypeError,
                    match=re.escape(expected_exception["message_substring"]),
                ) as expected_error:
                    run_benchmark_workload_with_cpython(source_workload)
                with pytest.raises(TypeError) as observed_error:
                    run_benchmark_workload_with_cpython(round_tripped)
                self.assertEqual(
                    str(observed_error.value),
                    str(expected_error.value),
                )

    def test_conditional_group_exists_callable_bytes_slice_workloads_round_trip_preserves_outcomes(
        self,
    ) -> None:
        source_workloads = _conditional_group_exists_callable_bytes_slice_workloads()

        self.assertEqual(
            tuple(workload.workload_id for workload in source_workloads),
            tuple(
                workload_id
                for expectation in _conditional_group_exists_callable_replacement_expectations()
                for workload_id in expectation.expected_workload_ids
                if workload_id.endswith("-bytes")
            ),
        )

        for source_workload in source_workloads:
            with self.subTest(workload_id=source_workload.workload_id):
                payload = workload_to_payload(source_workload)
                round_tripped = workload_from_payload(payload)
                expected_signature = callable_match_group_signature(
                    source_workload.replacement_payload()
                )
                observed_signature = callable_match_group_signature(
                    round_tripped.replacement_payload()
                )

                self.assertEqual(payload["text_model"], "bytes")
                self.assertEqual(round_tripped.text_model, "bytes")
                self.assertEqual(payload["count"], source_workload.count)
                self.assertEqual(
                    payload["expected_exception"],
                    source_workload.expected_exception,
                )
                self.assertEqual(
                    round_tripped.expected_exception,
                    source_workload.expected_exception,
                )
                self.assertEqual(
                    round_tripped.pattern_payload(),
                    source_workload.pattern_payload(),
                )
                self.assertEqual(
                    round_tripped.haystack_payload(),
                    source_workload.haystack_payload(),
                )
                self.assertEqual(observed_signature, expected_signature)
                self.assertIsNotNone(observed_signature)
                assert observed_signature is not None
                self.assertIsInstance(observed_signature[2], bytes)
                self.assertIsInstance(observed_signature[3], bytes)

                if source_workload.expected_exception is None:
                    assert_benchmark_workload_matches_expected_result(
                        round_tripped,
                        run_benchmark_workload_with_cpython(source_workload),
                    )
                    continue

                expected_exception = source_workload.expected_exception
                assert expected_exception is not None

                with pytest.raises(
                    TypeError,
                    match=re.escape(expected_exception["message_substring"]),
                ) as expected_error:
                    run_benchmark_workload_with_cpython(source_workload)
                with pytest.raises(TypeError) as observed_error:
                    run_benchmark_workload_with_cpython(round_tripped)
                self.assertEqual(
                    str(observed_error.value),
                    str(expected_error.value),
                )

    def test_conditional_group_exists_alternation_callable_bytes_workloads_round_trip_preserves_outcomes(
        self,
    ) -> None:
        for source_workload in (
            _conditional_group_exists_alternation_callable_bytes_workloads()
        ):
            with self.subTest(workload_id=source_workload.workload_id):
                payload = workload_to_payload(source_workload)
                round_tripped = workload_from_payload(payload)

                self.assertEqual(payload["text_model"], "bytes")
                self.assertEqual(round_tripped.text_model, "bytes")
                self.assertEqual(
                    payload["expected_exception"],
                    source_workload.expected_exception,
                )
                self.assertEqual(
                    round_tripped.expected_exception,
                    source_workload.expected_exception,
                )
                self.assertEqual(
                    round_tripped.pattern_payload(),
                    source_workload.pattern_payload(),
                )
                self.assertEqual(
                    round_tripped.haystack_payload(),
                    source_workload.haystack_payload(),
                )
                self.assertEqual(
                    _text_model_agnostic_callable_match_group_signature(
                        round_tripped.replacement_payload()
                    ),
                    _text_model_agnostic_callable_match_group_signature(
                        source_workload.replacement_payload()
                    ),
                )

                if source_workload.expected_exception is None:
                    assert_benchmark_workload_matches_expected_result(
                        round_tripped,
                        run_benchmark_workload_with_cpython(source_workload),
                    )
                    continue

                expected_exception = source_workload.expected_exception
                assert expected_exception is not None

                with pytest.raises(
                    TypeError,
                    match=re.escape(expected_exception["message_substring"]),
                ) as expected_error:
                    run_benchmark_workload_with_cpython(source_workload)
                with pytest.raises(TypeError) as observed_error:
                    run_benchmark_workload_with_cpython(round_tripped)
                self.assertEqual(
                    str(observed_error.value),
                    str(expected_error.value),
                )

    def test_nested_group_alternation_manifest_promotes_broader_range_open_ended_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-alternation-boundary"
        expected_workload_ids = (
            "module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-lower-bound-b-branch-warm-bytes",
            "module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-warm-bytes",
            "pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-lower-bound-c-branch-purged-bytes",
        )

        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )

        case = source_tree_combined_case(manifest_id)
        expected_workload_count = len(
            case.selected_workload_ids_for_manifest(manifest_id)
        )
        public_representatives = (
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            )
        )
        manifest_expectation = case.manifest_expectation
        self.assertEqual(manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self.assertEqual(manifest_expectation.representative_measured_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(public_workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    public_representatives,
                )

        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_quantified_alternation_manifest_promotes_bounded_branch_backref_conditional_nested_branch_broader_range_open_ended_and_backtracking_heavy_bytes_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "quantified-alternation-boundary"
        fully_measured_expectation = (
            source_tree_combined_fully_measured_manifest_expectation(
                manifest_id
            )
        )
        expected_workload_ids = (
            fully_measured_expectation.representative_measured_workload_ids
        )
        expected_measured_workload_count = (
            fully_measured_expectation.expected_measured_workload_count
        )
        expected_total_workload_count = (
            fully_measured_expectation.expected_total_workload_count
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertEqual(
            manifest_definition.fully_measured_expectation,
            fully_measured_expectation,
        )
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

    def test_nested_group_replacement_manifest_promotes_broader_range_open_ended_conditional_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-replacement-boundary"
        expected_workload_ids = (
            "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-bytes",
            "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-bytes",
            "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-bytes",
            "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-bytes",
        )
        expected_workload_count = len(
            source_tree_combined_case(manifest_id).selected_workload_ids_for_manifest(
                manifest_id
            )
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        case = source_tree_combined_case(manifest_id)
        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_nested_group_callable_replacement_manifest_promotes_broader_range_open_ended_conditional_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-callable-replacement-boundary"
        expected_workload_ids = (
            "module-sub-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-bytes",
            "pattern-sub-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-bytes",
            "pattern-subn-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-bytes",
        )
        expected_workload_count = len(
            source_tree_combined_case(manifest_id).selected_workload_ids_for_manifest(
                manifest_id
            )
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        case = source_tree_combined_case(manifest_id)
        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_nested_group_replacement_manifest_promotes_broader_range_open_ended_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-replacement-boundary"
        expected_workload_ids = (
            "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-bytes",
            "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-bytes",
            "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-bytes",
            "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-bytes",
        )
        expected_workload_count = len(
            source_tree_combined_case(manifest_id).selected_workload_ids_for_manifest(
                manifest_id
            )
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        case = source_tree_combined_case(manifest_id)
        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_nested_group_replacement_manifest_promotes_broader_range_branch_local_backreference_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-replacement-boundary"
        expected_workload_ids = (
            "module-sub-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-subn-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str",
            "pattern-sub-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-str",
            "pattern-subn-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-str",
        )
        expected_workload_count = len(
            source_tree_combined_case(manifest_id).selected_workload_ids_for_manifest(
                manifest_id
            )
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        case = source_tree_combined_case(manifest_id)
        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_nested_group_replacement_manifest_promotes_broader_range_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-replacement-boundary"
        expected_workload_ids = (
            "module-sub-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-subn-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-bytes",
            "pattern-sub-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-bytes",
            "pattern-subn-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-bytes",
        )
        expected_workload_count = len(
            source_tree_combined_case(manifest_id).selected_workload_ids_for_manifest(
                manifest_id
            )
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        case = source_tree_combined_case(manifest_id)
        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_nested_group_callable_replacement_manifest_promotes_nested_broader_range_backtracking_heavy_str_and_bytes_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-callable-replacement-boundary"
        expected_workload_ids = (
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-str",
            "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-str",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-upper-bound-mixed-purged-str",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-str",
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-bytes",
            "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-bytes",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-upper-bound-mixed-purged-bytes",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-bytes",
        )
        expected_workload_count = len(
            source_tree_combined_case(manifest_id).selected_workload_ids_for_manifest(
                manifest_id
            )
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        case = source_tree_combined_case(manifest_id)
        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_nested_group_callable_replacement_manifest_promotes_nested_broader_range_open_ended_backtracking_heavy_str_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-callable-replacement-boundary"
        expected_workload_ids = (
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-str",
            "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-str",
            "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-fourth-repetition-short-only-purged-str",
            "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-str",
        )
        expected_workload_count = len(
            source_tree_combined_case(manifest_id).selected_workload_ids_for_manifest(
                manifest_id
            )
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        case = source_tree_combined_case(manifest_id)
        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_nested_group_callable_replacement_manifest_promotes_nested_broader_range_open_ended_backtracking_heavy_bytes_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-callable-replacement-boundary"
        expected_workload_ids = (
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-bytes",
            "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-bytes",
            "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-fourth-repetition-short-only-purged-bytes",
            "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-bytes",
        )
        expected_workload_count = len(
            source_tree_combined_case(manifest_id).selected_workload_ids_for_manifest(
                manifest_id
            )
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        case = source_tree_combined_case(manifest_id)
        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )


def test_compiled_pattern_module_compile_cpython_dispatch_covers_success_and_keyword_lanes(
) -> None:
    success_case = next(
        case
        for case in _COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES
        if case.case_id == "success"
    )
    success_source_workload = success_case.source_workloads()[0]
    success_workload = _source_tree_contract_workload(
        success_source_workload,
        spec=success_case.contract_builder_spec(),
    )

    keyword_case = next(
        case
        for case in _COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES
        if case.case_id == "bool-false"
    )
    keyword_source_workload = keyword_case.source_workloads()[0]
    keyword_workload = _source_tree_contract_workload(
        keyword_source_workload,
        spec=keyword_case.contract_builder_spec(),
    )

    success_result = success_case.run_cpython_workload(success_workload)
    keyword_result = keyword_case.run_cpython_workload(keyword_workload)

    assert success_result.pattern == success_workload.pattern_payload()
    assert success_case.callback_flags(success_source_workload) == success_source_workload.flags
    assert keyword_result.pattern == keyword_workload.pattern_payload()
    assert keyword_case.callback_flags(keyword_source_workload) is False


def test_compiled_pattern_module_compile_anchor_and_case_metadata_stay_pinned_to_live_rows(
) -> None:
    contract_cases = _COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES
    anchor_lanes = _COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES

    success_case = next(case for case in contract_cases if case.case_id == "success")
    bool_false_case = next(
        case for case in contract_cases if case.case_id == "bool-false"
    )
    success_anchor_lane = next(
        lane for lane in anchor_lanes if lane.case_id == success_case.case_id
    )
    bool_false_anchor_lane = next(
        lane for lane in anchor_lanes if lane.case_id == bool_false_case.case_id
    )

    assert success_case.expected_source_workload_ids() == (
        "module-compile-literal-warm-str-compiled-pattern",
        "module-compile-literal-purged-bytes-compiled-pattern",
        "module-compile-named-group-warm-str-compiled-pattern",
        "module-compile-named-group-purged-bytes-compiled-pattern",
    )
    assert success_anchor_lane.expected_anchor_pairs == (
        (
            "module-compile-literal-warm-str-compiled-pattern-contract",
            "workflow-module-compile-str-compiled-pattern",
        ),
        (
            "module-compile-literal-purged-bytes-compiled-pattern-contract",
            "workflow-module-compile-bytes-compiled-pattern",
        ),
        (
            "module-compile-named-group-warm-str-compiled-pattern-contract",
            "workflow-module-compile-str-compiled-pattern-named-group",
        ),
        (
            "module-compile-named-group-purged-bytes-compiled-pattern-contract",
            "workflow-module-compile-bytes-compiled-pattern-named-group",
        ),
    )
    assert tuple(
        workload.workload_id for workload in bool_false_anchor_lane.source_workloads
    ) == (
        "module-compile-flags-bool-false-warm-str-compiled-pattern",
        "module-compile-flags-bool-false-purged-bytes-compiled-pattern",
    )
    assert bool_false_anchor_lane.expected_anchor_pairs == (
        (
            "module-compile-flags-bool-false-warm-str-compiled-pattern-contract",
            "workflow-module-compile-flags-bool-false-str-compiled-pattern",
        ),
        (
            "module-compile-flags-bool-false-purged-bytes-compiled-pattern-contract",
            "workflow-module-compile-flags-bool-false-bytes-compiled-pattern",
        ),
    )


@pytest.mark.parametrize(
    "owner_spec",
    (
        *_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS,
        *_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS,
    ),
    ids=lambda owner_spec: owner_spec.anchor_definition_name,
)
def test_compiled_pattern_module_compile_owner_specs_keep_module_boundary_rows_measured(
    owner_spec: object,
) -> None:
    manifest_workload_count = len(
        selected_manifest_workloads(COMPILED_PATTERN_MODULE_COMPILE_MANIFEST_PATH)
    )
    expected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in selected_manifest_workloads(
            COMPILED_PATTERN_MODULE_COMPILE_MANIFEST_PATH,
            include_workload=owner_spec.includes_workload,
        )
    )

    assert expected_measured_workload_ids == owner_spec.expected_anchor_workload_ids()
    assert_zero_gap_manifest_workloads_measured(
        manifest_path=COMPILED_PATTERN_MODULE_COMPILE_MANIFEST_PATH,
        manifest_id="module-boundary",
        expected_measured_workload_ids=expected_measured_workload_ids,
        expected_measured_workload_count=manifest_workload_count,
        expected_total_workload_count=manifest_workload_count,
    )


@pytest.mark.parametrize(
    "anchor_lane",
    _COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES,
    ids=lambda anchor_lane: anchor_lane.case_id,
)
def test_compiled_pattern_module_compile_contract_rows_stay_anchored_to_published_correctness_cases(
    tmp_path,
    anchor_lane: object,
) -> None:
    manifest = _source_tree_contract_manifest(
        anchor_lane.source_workloads,
        spec=anchor_lane.contract_builder_spec(),
    )
    manifest_path = _write_test_manifest(
        tmp_path,
        anchor_lane.contract_filename,
        f"MANIFEST = {manifest!r}\n",
    )
    expected_anchor_case_ids = anchor_lane.expected_anchor_case_ids(manifest_path)
    anchor_case_ids = anchor_lane.anchor_case_ids

    assert anchored_workload_case_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=anchor_lane.workload_signature,
        include_workload=anchor_lane.include_workload,
    ) == expected_anchor_case_ids
    assert unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=anchor_lane.workload_signature,
        include_workload=anchor_lane.include_workload,
    ) == ()
    assert tuple(
        (pair.workload_id, pair.case_id)
        for pair in expected_anchored_workload_case_pairs(
            manifest_path,
            expected_anchor_case_ids=expected_anchor_case_ids,
            include_workload=anchor_lane.include_workload,
        )
    ) == anchor_lane.expected_anchor_pairs


@pytest.mark.parametrize(
    ("case_group", "source_workload"),
    tuple(
        pytest.param(case_group, source_workload, id=source_workload.workload_id)
        for case_group in (
            owner_spec.contract_case()
            for owner_spec in _COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS
        )
        for source_workload in case_group.source_workloads()
    ),
)
def test_compiled_pattern_module_compile_keyword_kwargs_materialize_at_callback_time(
    monkeypatch: pytest.MonkeyPatch,
    case_group: object,
    source_workload: Workload,
) -> None:
    workload = _source_tree_contract_workload(
        source_workload,
        spec=case_group.contract_builder_spec(),
    )
    observed_field_names = _record_numeric_materialization_fields(monkeypatch)

    re.purge()
    try:
        callback = benchmarks.build_callable(re, "re", workload)
        assert observed_field_names == []

        if source_workload.expected_exception is None:
            observed_result = callback()
            assert observed_result.pattern == workload.pattern_payload()
        else:
            expected_exception = _expected_exception_instance(
                source_workload.expected_exception
            )
            with pytest.raises(
                type(expected_exception),
                match=source_workload.expected_exception["message_substring"],
            ):
                callback()

        assert observed_field_names == ["kwargs.flags"]
    finally:
        re.purge()


@pytest.mark.parametrize(
    ("contract_case", "source_workload"),
    _COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS,
)
@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
def test_run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads(
    contract_case: object,
    source_workload: Workload,
    import_name: str,
    adapter_name: str,
) -> None:
    workload = _source_tree_contract_workload(
        source_workload,
        spec=contract_case.contract_builder_spec(),
    )
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    contract_case.assert_payload_round_trip(
        source_workload,
        payload,
        round_tripped,
    )

    probe = benchmarks.run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name=import_name,
        adapter_name=adapter_name,
    )

    assert probe["status"] == "measured"
    assert probe["median_ns"] > 0


@pytest.mark.parametrize(
    ("contract_case", "source_workload"),
    _COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS,
)
def test_compiled_pattern_module_compile_contract_callbacks_precompile_first_argument_before_timing(
    contract_case: object,
    source_workload: Workload,
) -> None:
    expected_build_calls = contract_case.expected_build_calls(source_workload)
    compile_exception = (
        None
        if source_workload.expected_exception is None
        else _expected_exception_instance(source_workload.expected_exception)
    )
    module = RecordingBenchmarkModule(compile_exception=compile_exception)
    callback = benchmarks.build_callable(
        module,
        "re",
        _source_tree_contract_workload(
            source_workload,
            spec=contract_case.contract_builder_spec(),
        ),
    )

    assert module.calls == expected_build_calls
    assert len(module.compiled_patterns) == 1

    compiled_pattern = module.compiled_patterns[0]
    if source_workload.expected_exception is None:
        assert callback() is compiled_pattern
    else:
        with pytest.raises(
            type(compile_exception),
            match=source_workload.expected_exception["message_substring"],
        ):
            callback()

    last_call = module.calls[-1]
    assert last_call[0] == "compile"
    assert last_call[1] is compiled_pattern
    assert last_call[2:] == (contract_case.callback_flags(source_workload),)

    def test_nested_group_callable_replacement_manifest_promotes_broader_range_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-callable-replacement-boundary"
        expected_workload_ids = (
            "module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-mixed-branches-first-match-only-warm-bytes",
            "pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-bytes",
            "pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-bytes",
        )
        expected_workload_count = len(
            source_tree_combined_case(manifest_id).selected_workload_ids_for_manifest(
                manifest_id
            )
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        case = source_tree_combined_case(manifest_id)
        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_nested_group_callable_replacement_manifest_promotes_quantified_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-callable-replacement-boundary"
        expected_workload_ids = (
            "module-sub-callable-numbered-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-bytes",
            "pattern-sub-callable-named-quantified-nested-group-alternation-branch-local-backreference-mixed-branches-purged-bytes",
            "pattern-subn-callable-named-quantified-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-bytes",
        )
        expected_workload_count = len(
            source_tree_combined_case(manifest_id).selected_workload_ids_for_manifest(
                manifest_id
            )
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        case = source_tree_combined_case(manifest_id)
        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_nested_group_callable_replacement_manifest_promotes_broader_range_conditional_branch_local_backreference_str_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-callable-replacement-boundary"
        expected_workload_ids = (
            "module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-first-match-only-b-branch-warm-str",
            "pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-all-c-purged-str",
            "pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-c-branch-first-match-only-purged-str",
        )
        expected_workload_count = len(
            source_tree_combined_case(manifest_id).selected_workload_ids_for_manifest(
                manifest_id
            )
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        case = source_tree_combined_case(manifest_id)
        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_nested_group_callable_replacement_manifest_promotes_broader_range_conditional_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-callable-replacement-boundary"
        expected_workload_ids = (
            "module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-first-match-only-b-branch-warm-bytes",
            "pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-all-c-purged-bytes",
            "pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-c-branch-first-match-only-purged-bytes",
        )
        expected_workload_count = len(
            source_tree_combined_case(manifest_id).selected_workload_ids_for_manifest(
                manifest_id
            )
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        case = source_tree_combined_case(manifest_id)
        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_nested_group_callable_replacement_manifest_promotes_broader_range_open_ended_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "nested-group-callable-replacement-boundary"
        expected_workload_ids = (
            "module-sub-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-bytes",
            "pattern-sub-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-bytes",
            "pattern-subn-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-bytes",
        )
        expected_workload_count = len(
            source_tree_combined_case(manifest_id).selected_workload_ids_for_manifest(
                manifest_id
            )
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_measured_workload_ids)
        self.assertIsNone(
            manifest_definition.representative_known_gap_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    ),
                )

        case = source_tree_combined_case(manifest_id)
        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_measured_workload_ids,
            (),
        )
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self._assert_zero_gap_manifest_workloads_measured(
            case,
            manifest_id,
            expected_workload_ids,
            expected_workload_count,
            expected_total_workload_count=expected_workload_count,
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

        _, scorecard = run_harness_scorecard(
            "rebar_harness.benchmarks",
            [
                "--manifest",
                str(REPO_ROOT / "benchmarks" / "workloads" / "regression_matrix.py"),
            ],
            report_name="benchmarks.json",
        )

        manifest_summary = scorecard["manifests"]["regression-matrix"]
        self.assertEqual(manifest_summary["known_gap_count"], 0)
        self.assertEqual(manifest_summary["measured_workloads"], 8)

        self._assert_manifest_workload_contracts(
            scorecard_case.manifest_for_id("regression-matrix"),
            scorecard,
            (
                ("regression-parser-bytes-backreference-purged", "measured"),
                ("regression-module-compile-multiline-purged", "measured"),
                ("regression-module-compile-multiline-purged-bytes", "measured"),
                ("regression-module-compile-verbose-purged-bytes", "measured"),
            ),
        )

    def test_source_tree_combined_slice_filters_match_expected_manifest_rows(self) -> None:
        for manifest_id in source_tree_combined_slice_manifest_ids():
            with self.subTest(manifest_id=manifest_id):
                manifest = source_tree_combined_case(manifest_id).target_manifest
                for expectation in source_tree_combined_slice_expectations(manifest_id):
                    with self.subTest(slice_id=expectation.slice_id):
                        self.assertEqual(
                            tuple(
                                workload.workload_id
                                for workload in select_source_tree_combined_slice_rows(
                                    manifest,
                                    expectation,
                                )
                            ),
                            expectation.expected_workload_ids,
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
                summary, scorecard = run_harness_scorecard(
                    "rebar_harness.benchmarks",
                    [
                        argument
                        for manifest in case.manifests
                        for argument in ("--manifest", str(manifest.path))
                    ],
                    report_name="benchmarks.json",
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
                _, scorecard = run_harness_scorecard(
                    "rebar_harness.benchmarks",
                    [
                        argument
                        for manifest in case.manifests
                        for argument in ("--manifest", str(manifest.path))
                    ],
                    report_name="benchmarks.json",
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
        _, scorecard = run_harness_scorecard(
            "rebar_harness.benchmarks",
            [
                argument
                for manifest in case.manifests
                for argument in ("--manifest", str(manifest.path))
            ],
            report_name="benchmarks.json",
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


class SourceTreeScorecardBenchmarkSuiteTest(unittest.TestCase):
    maxDiff = None

    def test_combined_manifest_definition_defaults_to_fully_measured_representatives(
        self,
    ) -> None:
        fully_measured_expectation = _combined_fully_measured_manifest_expectation(
            coverage_group="contract",
            representative_measured_workload_ids=("measured-a", "measured-b"),
            expected_measured_workload_count=2,
        )

        definition = _combined_manifest_definition(
            fully_measured_expectation=fully_measured_expectation,
        )

        self.assertEqual(
            definition.representative_measured_workload_ids,
            ("measured-a", "measured-b"),
        )
        self.assertIs(
            definition.fully_measured_expectation,
            fully_measured_expectation,
        )

    def test_combined_manifest_definition_rejects_fully_measured_representative_drift(
        self,
    ) -> None:
        fully_measured_expectation = _combined_fully_measured_manifest_expectation(
            coverage_group="contract",
            representative_measured_workload_ids=("measured-a", "measured-b"),
            expected_measured_workload_count=2,
        )

        with self.assertRaisesRegex(
            AssertionError,
            re.escape(
                "fully measured manifest definitions must keep their "
                "representative rows on the shared definition-owned contract"
            ),
        ):
            _combined_manifest_definition(
                fully_measured_expectation=fully_measured_expectation,
                representative_measured_workload_ids=("drifted-measured-row",),
            )

    def _assert_single_manifest_zero_gap_scorecard_case_reuses_shared_expectation(
        self,
        manifest_id: str,
    ) -> None:
        case = source_tree_scorecard_case(manifest_id)
        combined_case = source_tree_combined_case(manifest_id)

        self.assertEqual(
            case.manifest_expectations[manifest_id].known_gap_count,
            0,
        )
        self.assertEqual(
            case.representative_measured_workload_ids,
            combined_case.manifest_expectation.representative_measured_workload_ids,
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())

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

    def test_published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks(
        self,
    ) -> None:
        manifests = list(published_benchmark_manifests())
        self.assertEqual(len(manifests), 30)
        tracked_report = benchmarks.SCORECARD_REPORT.load(TRACKED_REPORT_PATH)
        self.assertEqual(
            expected_summary_for_manifests(manifests, selection_mode="full"),
            {
                key: tracked_report["summary"][key]
                for key in (
                    "known_gap_count",
                    "measured_workloads",
                    "module_workloads",
                    "parser_workloads",
                    "regression_workloads",
                    "total_workloads",
                )
            },
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

    def test_regression_pack_full_promotes_regression_probes_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("regression-pack-full")
        for workload_id in (
            "regression-parser-bytes-backreference-purged",
            "regression-module-compile-multiline-purged",
            "regression-module-compile-multiline-purged-bytes",
            "regression-module-compile-verbose-purged-bytes",
        ):
            with self.subTest(workload_id=workload_id):
                self.assertIn(
                    workload_id,
                    case.representative_measured_workload_ids,
                )
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_numbered_backreference_manifest_promotes_grouped_segment_pair_to_measured(
        self,
    ) -> None:
        self._assert_single_manifest_zero_gap_scorecard_case_reuses_shared_expectation(
            "numbered-backreference-boundary"
        )

    def test_nested_group_manifest_promotes_nested_pair_to_measured(self) -> None:
        self._assert_single_manifest_zero_gap_scorecard_case_reuses_shared_expectation(
            "nested-group-boundary"
        )

    def test_case_builders_reuse_cached_source_tree_manifest_records(self) -> None:
        scorecard_case = source_tree_scorecard_case("post-parser-workflows")
        combined_case = source_tree_combined_case("literal-flag-boundary")

        self.assertEqual(
            [manifest.manifest_id for manifest in scorecard_case.manifests],
            [
                "module-boundary",
                "collection-replacement-boundary",
                "literal-flag-boundary",
            ],
        )
        self.assertEqual(
            [manifest.manifest_id for manifest in combined_case.manifests],
            [
                "compile-matrix",
                "module-boundary",
                "pattern-boundary",
                "collection-replacement-boundary",
                "literal-flag-boundary",
                "regression-matrix",
            ],
        )
        self.assertIs(
            scorecard_case.manifest_for_id("module-boundary"),
            combined_case.manifest_for_id("module-boundary"),
        )
        self.assertIs(
            scorecard_case.manifest_for_id("collection-replacement-boundary"),
            combined_case.manifest_for_id("collection-replacement-boundary"),
        )
        self.assertIs(
            scorecard_case.manifest_for_id("literal-flag-boundary"),
            combined_case.target_manifest,
        )
        self.assertEqual(
            combined_case.target_manifest.manifest_id,
            "literal-flag-boundary",
        )

    def test_post_parser_workflows_preserve_expected_manifest_paths(self) -> None:
        case = source_tree_scorecard_case("post-parser-workflows")

        self.assertEqual(
            [manifest.path.name for manifest in case.manifests],
            [
                "module_boundary.py",
                "collection_replacement_boundary.py",
                "literal_flag_boundary.py",
            ],
        )
        self.assertEqual(
            [relative_manifest_path(manifest.path) for manifest in case.manifests],
            [
                "benchmarks/workloads/module_boundary.py",
                "benchmarks/workloads/collection_replacement_boundary.py",
                "benchmarks/workloads/literal_flag_boundary.py",
            ],
        )

    def test_case_selection_helpers_derive_workload_ids_from_manifests(self) -> None:
        compile_matrix = source_tree_scorecard_case("compile-matrix")
        self.assertEqual(
            compile_matrix.selected_workload_ids_for_manifest("compile-matrix"),
            (
                "compile-inline-locale-bytes-warm",
                "compile-lookbehind-cold",
                "compile-character-class-ignorecase-warm",
                "compile-possessive-quantifier-cold",
                "compile-atomic-group-purged",
                "compile-parser-stress-cold",
            ),
        )

        post_parser = source_tree_scorecard_case("post-parser-workflows")
        self.assertEqual(
            post_parser.selected_workload_ids_for_manifest("module-boundary"),
            tuple(
                workload.workload_id
                for workload in post_parser.manifest_for_id("module-boundary").workloads
            ),
        )

        combined_case = source_tree_combined_case("literal-flag-boundary")
        self.assertEqual(
            combined_case.selected_workload_ids_for_manifest("regression-matrix"),
            tuple(
                workload.workload_id
                for workload in combined_case.manifest_for_id("regression-matrix").workloads
            ),
        )

    def _assert_zero_gap_representative_workload_subset(
        self,
        manifest_id: str,
        expected_workload_ids: tuple[str, ...],
    ) -> None:
        case = source_tree_combined_case(manifest_id)
        public_representatives = (
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            )
        )

        self.assertEqual(case.manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )

        explicit_representatives = (
            case.manifest_expectation.representative_measured_workload_ids
        )
        for workload_id in expected_workload_ids:
            with self.subTest(manifest_id=manifest_id, workload_id=workload_id):
                self.assertIn(workload_id, public_representatives)
                if explicit_representatives:
                    self.assertIn(workload_id, explicit_representatives)

        if not explicit_representatives:
            self.assertEqual(explicit_representatives, ())

    def test_zero_gap_source_tree_manifests_keep_selected_bytes_representatives_publicly_measured(
        self,
    ) -> None:
        for manifest_id, manifest_definition in (
            SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.items()
        ):
            for expected_workload_ids in (
                manifest_definition.zero_gap_bytes_representative_subsets
            ):
                with self.subTest(manifest_id=manifest_id):
                    self._assert_zero_gap_representative_workload_subset(
                        manifest_id,
                        expected_workload_ids,
                    )

    def test_combined_cases_treat_counted_repeat_manifest_pair_as_fully_measured(
        self,
    ) -> None:
        for manifest_id in source_tree_combined_fully_measured_manifest_ids(
            "counted-repeat"
        ):
            expected_workload_ids = (
                source_tree_combined_fully_measured_manifest_expectation(
                    manifest_id
                ).representative_measured_workload_ids
            )
            with self.subTest(manifest_id=manifest_id):
                case = source_tree_combined_case(manifest_id)
                self.assertEqual(case.manifest_expectation.known_gap_count, 0)
                self.assertEqual(
                    case.manifest_expectation.representative_measured_workload_ids,
                    expected_workload_ids,
                )
                self.assertEqual(
                    case.manifest_expectation.representative_known_gap_workload_ids,
                    (),
                )

    def test_compile_matrix_manifest_reuses_zero_gap_expectation(self) -> None:
        case = source_tree_scorecard_case("compile-matrix")
        manifest_expectation = case.manifest_expectations["compile-matrix"]
        self.assertEqual(manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            case.representative_measured_workload_ids,
            (
                "compile-inline-locale-bytes-warm",
                "compile-lookbehind-cold",
                "compile-atomic-group-purged",
                "compile-parser-stress-cold",
            ),
        )
        self.assertEqual(
            case.representative_known_gap_workload_ids,
            (),
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
                        for expectation in source_tree_combined_slice_expectations(
                            case_id
                        )
                        for workload_id in expectation.expected_workload_ids
                    ),
                )

    def test_conditional_group_exists_callable_scorecards_keep_negative_count_follow_on_workloads_in_sync(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        expectations = _conditional_group_exists_callable_replacement_expectations()
        case = source_tree_scorecard_case(manifest_id)
        manifest = case.manifest_for_id(manifest_id)
        expected_negative_count_str_workload_ids = (
            "module-sub-callable-numbered-conditional-group-exists-replacement-negative-count-warm-str",
            "module-subn-callable-named-conditional-group-exists-replacement-negative-count-warm-str",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-negative-count-purged-str",
            "pattern-subn-callable-named-conditional-group-exists-replacement-negative-count-purged-str",
            "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-str",
            "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-str",
            "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-str",
            "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-str",
        )
        expected_negative_count_bytes_workload_ids = (
            "module-sub-callable-numbered-conditional-group-exists-replacement-negative-count-warm-bytes",
            "module-subn-callable-named-conditional-group-exists-replacement-negative-count-warm-bytes",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-negative-count-purged-bytes",
            "pattern-subn-callable-named-conditional-group-exists-replacement-negative-count-purged-bytes",
            "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-bytes",
            "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-bytes",
            "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-bytes",
            "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-bytes",
        )
        expected_callable_workload_ids = tuple(
            workload_id
            for expectation in expectations
            for workload_id in expectation.expected_workload_ids
        )
        callable_slice_rows = tuple(
            workload
            for expectation in expectations
            for workload in select_source_tree_combined_slice_rows(manifest, expectation)
        )
        representative_callable_workload_ids = tuple(
            workload_id
            for workload_id in case.representative_measured_workload_ids
            if workload_id in expected_callable_workload_ids
        )
        expected_str_workload_ids, expected_bytes_workload_ids = (
            _split_workload_ids_by_text_model(expected_callable_workload_ids)
        )
        representative_str_workload_ids, representative_bytes_workload_ids = (
            _split_workload_ids_by_text_model(representative_callable_workload_ids)
        )
        manifest_negative_count_str_workload_ids = tuple(
            workload.workload_id
            for workload in callable_slice_rows
            if workload.text_model == "str"
            and "negative-count" in workload.categories
            and "none-count" not in workload.categories
        )
        manifest_negative_count_bytes_workload_ids = tuple(
            workload.workload_id
            for workload in callable_slice_rows
            if workload.text_model == "bytes"
            and "negative-count" in workload.categories
            and "none-count" not in workload.categories
        )
        str_workload_signatures = Counter(
            (
                workload.operation,
                workload.pattern,
                workload.haystack,
                _text_model_agnostic_callable_match_group_signature(
                    workload.replacement_payload()
                ),
                workload.count,
                workload.cache_mode,
            )
            for workload in callable_slice_rows
            if workload.text_model == "str"
        )
        bytes_workload_signatures = Counter(
            (
                workload.operation,
                workload.pattern,
                workload.haystack,
                _text_model_agnostic_callable_match_group_signature(
                    workload.replacement_payload()
                ),
                workload.count,
                workload.cache_mode,
            )
            for workload in callable_slice_rows
            if workload.text_model == "bytes"
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        self.assertEqual(
            representative_callable_workload_ids,
            expected_callable_workload_ids,
        )
        self.assertEqual(
            representative_str_workload_ids,
            expected_str_workload_ids,
        )
        self.assertEqual(
            representative_bytes_workload_ids,
            expected_bytes_workload_ids,
        )
        self.assertEqual(
            manifest_negative_count_str_workload_ids,
            expected_negative_count_str_workload_ids,
        )
        self.assertEqual(
            manifest_negative_count_bytes_workload_ids,
            expected_negative_count_bytes_workload_ids,
        )
        self.assertEqual(
            tuple(
                workload_id
                for workload_id in representative_str_workload_ids
                if workload_id in manifest_negative_count_str_workload_ids
            ),
            manifest_negative_count_str_workload_ids,
        )
        self.assertEqual(
            tuple(
                workload_id
                for workload_id in representative_bytes_workload_ids
                if workload_id in manifest_negative_count_bytes_workload_ids
            ),
            manifest_negative_count_bytes_workload_ids,
        )
        self.assertEqual(
            str_workload_signatures,
            bytes_workload_signatures,
        )
        self.assertEqual(
            Counter(
                (workload.operation, workload.count)
                for workload in callable_slice_rows
                if workload.workload_id in manifest_negative_count_str_workload_ids
            ),
            Counter(
                {
                    ("module.sub", -1): 2,
                    ("module.subn", -1): 2,
                    ("pattern.sub", -1): 2,
                    ("pattern.subn", -1): 2,
                }
            ),
        )
        self.assertEqual(
            Counter(
                (workload.operation, workload.count)
                for workload in callable_slice_rows
                if workload.workload_id in manifest_negative_count_bytes_workload_ids
            ),
            Counter(
                {
                    ("module.sub", -1): 2,
                    ("module.subn", -1): 2,
                    ("pattern.sub", -1): 2,
                    ("pattern.subn", -1): 2,
                }
            ),
        )

    def test_conditional_group_exists_callable_scorecards_keep_none_count_follow_on_workloads_in_sync(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        expectations = _conditional_group_exists_callable_replacement_expectations()
        case = source_tree_scorecard_case(manifest_id)
        manifest = case.manifest_for_id(manifest_id)
        expected_none_count_workload_ids = (
            CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_IDS
        )
        callable_slice_rows = tuple(
            workload
            for expectation in expectations
            for workload in select_source_tree_combined_slice_rows(manifest, expectation)
        )
        none_count_rows = tuple(
            workload
            for workload in callable_slice_rows
            if "none-count" in workload.categories
        )
        representative_none_count_workload_ids = tuple(
            workload_id
            for workload_id in case.representative_measured_workload_ids
            if workload_id in expected_none_count_workload_ids
        )
        representative_str_workload_ids, representative_bytes_workload_ids = (
            _split_workload_ids_by_text_model(representative_none_count_workload_ids)
        )
        manifest_none_count_str_workload_ids = tuple(
            workload.workload_id
            for workload in none_count_rows
            if workload.text_model == "str"
        )
        manifest_none_count_bytes_workload_ids = tuple(
            workload.workload_id
            for workload in none_count_rows
            if workload.text_model == "bytes"
        )

        def none_count_signature(workload: Workload) -> tuple[object, ...]:
            return (
                workload.operation,
                workload.pattern,
                workload.haystack,
                _text_model_agnostic_callable_match_group_signature(
                    workload.replacement_payload()
                ),
                workload.count,
                workload.cache_mode,
                frozenset(
                    category
                    for category in workload.categories
                    if category not in {"str", "bytes"}
                ),
            )

        self.assertEqual(case.representative_known_gap_workload_ids, ())
        self.assertEqual(
            representative_str_workload_ids,
            CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS,
        )
        self.assertEqual(
            representative_bytes_workload_ids,
            CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS,
        )
        self.assertEqual(
            manifest_none_count_str_workload_ids,
            CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS,
        )
        self.assertEqual(
            manifest_none_count_bytes_workload_ids,
            CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS,
        )
        self.assertEqual(
            Counter(
                none_count_signature(workload)
                for workload in none_count_rows
                if workload.text_model == "str"
            ),
            Counter(
                none_count_signature(workload)
                for workload in none_count_rows
                if workload.text_model == "bytes"
            ),
        )
        self.assertEqual(
            Counter(
                (workload.operation, workload.count)
                for workload in none_count_rows
                if workload.text_model == "str"
            ),
            Counter(
                {
                    ("module.sub", None): 4,
                    ("module.subn", None): 4,
                    ("pattern.sub", None): 4,
                    ("pattern.subn", None): 4,
                }
            ),
        )
        self.assertEqual(
            Counter(
                (workload.operation, workload.count)
                for workload in none_count_rows
                if workload.text_model == "bytes"
            ),
            Counter(
                {
                    ("module.sub", None): 4,
                    ("module.subn", None): 4,
                    ("pattern.sub", None): 4,
                    ("pattern.subn", None): 4,
                }
            ),
        )

    def test_conditional_group_exists_nested_callable_scorecards_keep_bytes_rows_in_sync_with_str_slice(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        case = source_tree_scorecard_case(manifest_id)
        manifest = case.manifest_for_id(manifest_id)
        str_expectation = _conditional_group_exists_nested_callable_replacement_expectation()
        bytes_expectation = _conditional_group_exists_nested_callable_bytes_replacement_expectation()
        str_rows = tuple(
            select_source_tree_combined_slice_rows(manifest, str_expectation)
        )
        bytes_rows = tuple(
            select_source_tree_combined_slice_rows(manifest, bytes_expectation)
        )
        representative_nested_workload_ids = tuple(
            workload_id
            for workload_id in case.representative_measured_workload_ids
            if workload_id
            in (
                CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS
                + CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS
            )
        )
        representative_str_workload_ids, representative_bytes_workload_ids = (
            _split_workload_ids_by_text_model(representative_nested_workload_ids)
        )

        def normalized_text_model_payload(value: str | bytes | None) -> str | None:
            if isinstance(value, bytes):
                return value.decode("latin-1")
            return value

        def expected_exception_signature(
            expected_exception: dict[str, str] | None,
        ) -> tuple[tuple[str, str], ...] | None:
            if expected_exception is None:
                return None
            return tuple(sorted(expected_exception.items()))

        def nested_workload_signature(workload: Workload) -> tuple[object, ...]:
            return (
                workload.operation,
                normalized_text_model_payload(workload.pattern_payload()),
                normalized_text_model_payload(workload.haystack_payload()),
                _text_model_agnostic_callable_match_group_signature(
                    workload.replacement_payload()
                ),
                workload.count,
                workload.cache_mode,
                frozenset(
                    category
                    for category in workload.categories
                    if category not in {"str", "bytes"}
                ),
                expected_exception_signature(workload.expected_exception),
            )

        self.assertEqual(
            tuple(workload.workload_id for workload in str_rows),
            CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS,
        )
        self.assertEqual(
            tuple(workload.workload_id for workload in bytes_rows),
            CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS,
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        self.assertEqual(
            representative_str_workload_ids,
            CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS,
        )
        self.assertEqual(
            representative_bytes_workload_ids,
            CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS,
        )
        self.assertEqual(
            Counter(nested_workload_signature(workload) for workload in str_rows),
            Counter(nested_workload_signature(workload) for workload in bytes_rows),
        )

    def test_conditional_group_exists_quantified_callable_scorecards_keep_negative_count_follow_on_workloads_in_sync(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        case = source_tree_scorecard_case(manifest_id)
        manifest = case.manifest_for_id(manifest_id)
        str_expectation = _conditional_group_exists_quantified_callable_replacement_expectation()
        bytes_expectation = (
            _conditional_group_exists_quantified_callable_bytes_replacement_expectation()
        )
        str_rows = tuple(
            select_source_tree_combined_slice_rows(manifest, str_expectation)
        )
        bytes_rows = tuple(
            select_source_tree_combined_slice_rows(manifest, bytes_expectation)
        )
        representative_quantified_workload_ids = tuple(
            workload_id
            for workload_id in case.representative_measured_workload_ids
            if workload_id
            in (
                CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS
                + CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS
            )
        )
        representative_str_workload_ids, representative_bytes_workload_ids = (
            _split_workload_ids_by_text_model(representative_quantified_workload_ids)
        )
        manifest_negative_count_str_workload_ids = _selected_workload_ids(
            str_rows,
            text_model="str",
            required_categories=("negative-count",),
        )
        manifest_negative_count_bytes_workload_ids = _selected_workload_ids(
            bytes_rows,
            text_model="bytes",
            required_categories=("negative-count",),
        )
        manifest_negative_count_no_match_str_workload_ids = _selected_workload_ids(
            str_rows,
            text_model="str",
            required_categories=("negative-count", "no-match"),
        )
        manifest_negative_count_no_match_bytes_workload_ids = _selected_workload_ids(
            bytes_rows,
            text_model="bytes",
            required_categories=("negative-count", "no-match"),
        )
        manifest_none_count_str_workload_ids = _selected_workload_ids(
            str_rows,
            text_model="str",
            required_categories=("none-count",),
        )
        manifest_none_count_bytes_workload_ids = _selected_workload_ids(
            bytes_rows,
            text_model="bytes",
            required_categories=("none-count",),
        )
        manifest_plain_no_match_str_workload_ids = _selected_workload_ids(
            str_rows,
            text_model="str",
            required_categories=("no-match",),
            excluded_categories=("negative-count",),
        )
        manifest_plain_no_match_bytes_workload_ids = _selected_workload_ids(
            bytes_rows,
            text_model="bytes",
            required_categories=("no-match",),
            excluded_categories=("negative-count",),
        )
        representative_negative_count_str_workload_ids = tuple(
            workload_id
            for workload_id in representative_str_workload_ids
            if workload_id in manifest_negative_count_str_workload_ids
        )
        representative_negative_count_bytes_workload_ids = tuple(
            workload_id
            for workload_id in representative_bytes_workload_ids
            if workload_id in manifest_negative_count_bytes_workload_ids
        )
        representative_negative_count_no_match_str_workload_ids = tuple(
            workload_id
            for workload_id in representative_str_workload_ids
            if workload_id in manifest_negative_count_no_match_str_workload_ids
        )
        representative_negative_count_no_match_bytes_workload_ids = tuple(
            workload_id
            for workload_id in representative_bytes_workload_ids
            if workload_id in manifest_negative_count_no_match_bytes_workload_ids
        )
        representative_none_count_str_workload_ids = tuple(
            workload_id
            for workload_id in representative_str_workload_ids
            if workload_id in manifest_none_count_str_workload_ids
        )
        representative_none_count_bytes_workload_ids = tuple(
            workload_id
            for workload_id in representative_bytes_workload_ids
            if workload_id in manifest_none_count_bytes_workload_ids
        )
        representative_plain_no_match_str_workload_ids = tuple(
            workload_id
            for workload_id in representative_str_workload_ids
            if workload_id in manifest_plain_no_match_str_workload_ids
        )
        representative_plain_no_match_bytes_workload_ids = tuple(
            workload_id
            for workload_id in representative_bytes_workload_ids
            if workload_id in manifest_plain_no_match_bytes_workload_ids
        )

        def normalized_text_model_payload(value: str | bytes | None) -> str | None:
            if isinstance(value, bytes):
                return value.decode("latin-1")
            return value

        def expected_exception_signature(
            expected_exception: dict[str, str] | None,
        ) -> tuple[tuple[str, str], ...] | None:
            if expected_exception is None:
                return None
            return tuple(sorted(expected_exception.items()))

        def quantified_workload_signature(workload: Workload) -> tuple[object, ...]:
            return (
                workload.operation,
                normalized_text_model_payload(workload.pattern_payload()),
                normalized_text_model_payload(workload.haystack_payload()),
                _text_model_agnostic_callable_match_group_signature(
                    workload.replacement_payload()
                ),
                workload.count,
                workload.cache_mode,
                frozenset(
                    category
                    for category in workload.categories
                    if category not in {"str", "bytes"}
                ),
                expected_exception_signature(workload.expected_exception),
            )

        self.assertEqual(
            tuple(workload.workload_id for workload in str_rows),
            CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS,
        )
        self.assertEqual(
            tuple(workload.workload_id for workload in bytes_rows),
            CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS,
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        self.assertEqual(
            representative_str_workload_ids,
            CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS,
        )
        self.assertEqual(
            representative_bytes_workload_ids,
            CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS,
        )
        self.assertEqual(
            Counter(
                quantified_workload_signature(workload) for workload in str_rows
            ),
            Counter(
                quantified_workload_signature(workload) for workload in bytes_rows
            ),
        )
        self.assertEqual(
            len(manifest_negative_count_str_workload_ids),
            len(manifest_negative_count_bytes_workload_ids),
        )
        self.assertEqual(len(manifest_negative_count_str_workload_ids), 16)
        self.assertEqual(
            len(manifest_none_count_str_workload_ids),
            len(manifest_none_count_bytes_workload_ids),
        )
        self.assertEqual(len(manifest_none_count_str_workload_ids), 4)
        self.assertEqual(
            len(manifest_negative_count_no_match_str_workload_ids),
            len(manifest_negative_count_no_match_bytes_workload_ids),
        )
        self.assertEqual(len(manifest_negative_count_no_match_str_workload_ids), 8)
        self.assertEqual(
            len(manifest_plain_no_match_str_workload_ids),
            len(manifest_plain_no_match_bytes_workload_ids),
        )
        self.assertEqual(len(manifest_plain_no_match_str_workload_ids), 8)
        self.assertEqual(
            manifest_negative_count_bytes_workload_ids,
            _mirrored_bytes_workload_ids(manifest_negative_count_str_workload_ids),
        )
        self.assertEqual(
            manifest_negative_count_no_match_bytes_workload_ids,
            _mirrored_bytes_workload_ids(
                manifest_negative_count_no_match_str_workload_ids
            ),
        )
        self.assertEqual(
            manifest_none_count_bytes_workload_ids,
            _mirrored_bytes_workload_ids(manifest_none_count_str_workload_ids),
        )
        self.assertEqual(
            manifest_plain_no_match_bytes_workload_ids,
            _mirrored_bytes_workload_ids(manifest_plain_no_match_str_workload_ids),
        )
        self.assertEqual(
            representative_negative_count_str_workload_ids,
            manifest_negative_count_str_workload_ids,
        )
        self.assertEqual(
            representative_negative_count_bytes_workload_ids,
            _mirrored_bytes_workload_ids(representative_negative_count_str_workload_ids),
        )
        self.assertEqual(
            representative_negative_count_no_match_str_workload_ids,
            manifest_negative_count_no_match_str_workload_ids,
        )
        self.assertEqual(
            representative_negative_count_no_match_bytes_workload_ids,
            _mirrored_bytes_workload_ids(
                representative_negative_count_no_match_str_workload_ids
            ),
        )
        self.assertEqual(
            representative_none_count_str_workload_ids,
            manifest_none_count_str_workload_ids,
        )
        self.assertEqual(
            representative_none_count_bytes_workload_ids,
            _mirrored_bytes_workload_ids(representative_none_count_str_workload_ids),
        )
        self.assertEqual(
            representative_plain_no_match_str_workload_ids,
            manifest_plain_no_match_str_workload_ids,
        )
        self.assertEqual(
            representative_plain_no_match_bytes_workload_ids,
            _mirrored_bytes_workload_ids(representative_plain_no_match_str_workload_ids),
        )
        self.assertEqual(
            representative_negative_count_str_workload_ids[
                -len(representative_negative_count_no_match_str_workload_ids) :
            ],
            representative_negative_count_no_match_str_workload_ids,
        )
        self.assertEqual(
            representative_negative_count_bytes_workload_ids[
                -len(representative_negative_count_no_match_bytes_workload_ids) :
            ],
            representative_negative_count_no_match_bytes_workload_ids,
        )
        self.assertEqual(
            representative_str_workload_ids[
                -len(representative_plain_no_match_str_workload_ids) :
            ],
            representative_plain_no_match_str_workload_ids,
        )
        self.assertEqual(
            representative_bytes_workload_ids[
                -len(representative_plain_no_match_bytes_workload_ids) :
            ],
            representative_plain_no_match_bytes_workload_ids,
        )
        self.assertEqual(
            Counter(
                (workload.operation, workload.count)
                for workload in str_rows
                if workload.workload_id in manifest_negative_count_str_workload_ids
            ),
            Counter(
                {
                    ("module.sub", -1): 4,
                    ("module.subn", -1): 4,
                    ("pattern.sub", -1): 4,
                    ("pattern.subn", -1): 4,
                }
            ),
        )
        self.assertEqual(
            Counter(
                (workload.operation, workload.count)
                for workload in bytes_rows
                if workload.workload_id in manifest_negative_count_bytes_workload_ids
            ),
            Counter(
                {
                    ("module.sub", -1): 4,
                    ("module.subn", -1): 4,
                    ("pattern.sub", -1): 4,
                    ("pattern.subn", -1): 4,
                }
            ),
        )

    def test_conditional_group_exists_callable_scorecards_include_alternation_heavy_rows(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        expectation = (
            _conditional_group_exists_alternation_callable_replacement_expectation()
        )
        case = source_tree_scorecard_case(manifest_id)
        manifest = case.manifest_for_id(manifest_id)
        matched_rows = tuple(
            select_source_tree_combined_slice_rows(manifest, expectation)
        )

        self.assertEqual(
            tuple(workload.workload_id for workload in matched_rows),
            CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS,
        )
        self.assertEqual(
            Counter(workload.text_model for workload in matched_rows),
            Counter({"str": 16, "bytes": 16}),
        )
        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )
        self.assertEqual(
            Counter((workload.operation, workload.count) for workload in matched_rows),
            Counter(
                {
                    ("module.sub", 0): 4,
                    ("module.sub", None): 2,
                    ("module.sub", -1): 2,
                    ("module.subn", 1): 4,
                    ("module.subn", None): 2,
                    ("module.subn", -1): 2,
                    ("pattern.sub", 0): 4,
                    ("pattern.sub", None): 2,
                    ("pattern.sub", -1): 2,
                    ("pattern.subn", 1): 4,
                    ("pattern.subn", None): 2,
                    ("pattern.subn", -1): 2,
                }
            ),
        )
        self.assertEqual(
            Counter(
                "exception" in workload.categories for workload in matched_rows
            ),
            Counter({False: 16, True: 16}),
        )

    def test_conditional_group_exists_template_bytes_scorecard_promotes_minimal_replacement_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        template_expectation = (
            _conditional_group_exists_template_replacement_expectation()
        )
        case = source_tree_scorecard_case(manifest_id)
        matched_rows = tuple(
            select_source_tree_combined_slice_rows(
                case.manifest_for_id(manifest_id),
                template_expectation,
            )
        )
        expected_workload_ids = template_expectation.expected_workload_ids

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        self.assertEqual({workload.text_model for workload in matched_rows}, {"str", "bytes"})
        for workload_id in CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )
        self.assertEqual(
            tuple(
                workload.workload_id
                for workload in matched_rows
                if workload.workload_id in case.representative_measured_workload_ids
            ),
            expected_workload_ids,
        )

    def test_conditional_group_exists_replacement_template_scorecards_keep_bytes_negative_count_follow_on_workloads_in_sync(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        template_expectation = (
            _conditional_group_exists_template_replacement_expectation()
        )
        case = source_tree_scorecard_case(manifest_id)
        expected_negative_count_str_workload_ids = (
            "module-sub-template-numbered-conditional-group-exists-replacement-negative-count-warm-str",
            "module-subn-template-named-conditional-group-exists-replacement-negative-count-warm-str",
            "pattern-sub-template-numbered-conditional-group-exists-replacement-negative-count-purged-str",
            "pattern-subn-template-named-conditional-group-exists-replacement-negative-count-purged-str",
        )
        expected_negative_count_bytes_workload_ids = (
            "module-sub-template-numbered-conditional-group-exists-replacement-negative-count-warm-bytes",
            "module-subn-template-named-conditional-group-exists-replacement-negative-count-warm-bytes",
            "pattern-sub-template-numbered-conditional-group-exists-replacement-negative-count-purged-bytes",
            "pattern-subn-template-named-conditional-group-exists-replacement-negative-count-purged-bytes",
        )
        representative_template_workload_ids = tuple(
            workload_id
            for workload_id in case.representative_measured_workload_ids
            if workload_id in template_expectation.expected_workload_ids
        )
        expected_str_workload_ids, expected_bytes_workload_ids = (
            _split_workload_ids_by_text_model(template_expectation.expected_workload_ids)
        )
        representative_str_workload_ids, representative_bytes_workload_ids = (
            _split_workload_ids_by_text_model(representative_template_workload_ids)
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        self.assertEqual(
            representative_template_workload_ids,
            template_expectation.expected_workload_ids,
        )
        self.assertEqual(
            representative_str_workload_ids,
            expected_str_workload_ids,
        )
        self.assertEqual(
            representative_bytes_workload_ids,
            expected_bytes_workload_ids,
        )
        self.assertEqual(
            expected_bytes_workload_ids,
            CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS,
        )
        self.assertEqual(
            representative_str_workload_ids[-len(expected_negative_count_str_workload_ids) :],
            expected_negative_count_str_workload_ids,
        )
        self.assertEqual(
            tuple(
                workload_id
                for workload_id in representative_str_workload_ids
                if "negative-count" in workload_id
            ),
            expected_negative_count_str_workload_ids,
        )
        self.assertEqual(
            representative_bytes_workload_ids[-len(expected_negative_count_bytes_workload_ids) :],
            expected_negative_count_bytes_workload_ids,
        )
        self.assertEqual(
            tuple(
                workload_id
                for workload_id in representative_bytes_workload_ids
                if "negative-count" in workload_id
            ),
            expected_negative_count_bytes_workload_ids,
        )

    def test_nested_group_callable_replacement_scorecard_promotes_broader_range_open_ended_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-callable-replacement-boundary")
        expected_workload_ids = (
            "module-sub-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-bytes",
            "pattern-sub-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-bytes",
            "pattern-subn-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-bytes",
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                "nested-group-callable-replacement-boundary"
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_nested_group_callable_replacement_scorecard_promotes_bounded_nested_group_bytes_rows_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-callable-replacement-boundary")
        expected_workload_ids = (
            "module-sub-callable-nested-group-numbered-warm-bytes",
            "module-subn-callable-nested-group-numbered-warm-bytes",
            "pattern-sub-callable-nested-group-numbered-purged-bytes",
            "pattern-subn-callable-nested-group-numbered-purged-bytes",
            "module-sub-callable-nested-group-named-warm-bytes",
            "module-subn-callable-nested-group-named-warm-bytes",
            "pattern-sub-callable-nested-group-named-purged-bytes",
            "pattern-subn-callable-nested-group-named-purged-bytes",
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                "nested-group-callable-replacement-boundary"
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_nested_group_callable_replacement_scorecard_promotes_quantified_nested_group_bytes_rows_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-callable-replacement-boundary")
        expected_workload_ids = (
            "module-sub-callable-numbered-quantified-nested-group-lower-bound-warm-bytes",
            "module-subn-callable-numbered-quantified-nested-group-first-match-only-warm-bytes",
            "pattern-sub-callable-named-quantified-nested-group-repeated-outer-purged-bytes",
            "pattern-subn-callable-named-quantified-nested-group-first-match-only-purged-bytes",
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                "nested-group-callable-replacement-boundary"
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_nested_group_callable_replacement_scorecard_promotes_quantified_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-callable-replacement-boundary")
        expected_workload_ids = (
            "module-sub-callable-numbered-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-bytes",
            "pattern-sub-callable-named-quantified-nested-group-alternation-branch-local-backreference-mixed-branches-purged-bytes",
            "pattern-subn-callable-named-quantified-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-bytes",
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                "nested-group-callable-replacement-boundary"
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_nested_group_replacement_scorecard_promotes_broader_range_branch_local_backreference_rows_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-replacement-boundary")
        expected_workload_ids = (
            "module-sub-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-subn-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str",
            "pattern-sub-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-str",
            "pattern-subn-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-str",
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                "nested-group-replacement-boundary"
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_nested_group_replacement_scorecard_promotes_broader_range_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-replacement-boundary")
        expected_workload_ids = (
            "module-sub-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-subn-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-bytes",
            "pattern-sub-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-bytes",
            "pattern-subn-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-bytes",
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                "nested-group-replacement-boundary"
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_nested_group_callable_replacement_scorecard_promotes_broader_range_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-callable-replacement-boundary")
        expected_workload_ids = (
            "module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-mixed-branches-first-match-only-warm-bytes",
            "pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-bytes",
            "pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-bytes",
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                "nested-group-callable-replacement-boundary"
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_nested_group_callable_replacement_scorecard_promotes_exact_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-callable-replacement-boundary")
        expected_workload_ids = (
            "module-sub-callable-numbered-nested-group-alternation-branch-local-backreference-b-branch-warm-bytes",
            "module-subn-callable-numbered-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-bytes",
            "pattern-sub-callable-named-nested-group-alternation-branch-local-backreference-c-branch-purged-bytes",
            "pattern-subn-callable-named-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-bytes",
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                "nested-group-callable-replacement-boundary"
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_nested_group_callable_replacement_scorecard_promotes_nested_broader_range_backtracking_heavy_str_and_bytes_rows_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-callable-replacement-boundary")
        expected_workload_ids = (
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-str",
            "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-str",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-upper-bound-mixed-purged-str",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-str",
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-bytes",
            "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-bytes",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-upper-bound-mixed-purged-bytes",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-bytes",
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                "nested-group-callable-replacement-boundary"
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_nested_group_callable_replacement_scorecard_promotes_nested_broader_range_open_ended_backtracking_heavy_str_rows_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-callable-replacement-boundary")
        expected_workload_ids = (
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-str",
            "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-str",
            "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-fourth-repetition-short-only-purged-str",
            "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-str",
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                "nested-group-callable-replacement-boundary"
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_nested_group_callable_replacement_scorecard_promotes_nested_broader_range_open_ended_backtracking_heavy_bytes_rows_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-callable-replacement-boundary")
        expected_workload_ids = (
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-bytes",
            "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-bytes",
            "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-fourth-repetition-short-only-purged-bytes",
            "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-bytes",
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                "nested-group-callable-replacement-boundary"
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_nested_group_callable_replacement_scorecard_promotes_broader_range_conditional_branch_local_backreference_str_rows_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-callable-replacement-boundary")
        expected_workload_ids = (
            "module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-first-match-only-b-branch-warm-str",
            "pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-all-c-purged-str",
            "pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-c-branch-first-match-only-purged-str",
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                "nested-group-callable-replacement-boundary"
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_nested_group_callable_replacement_scorecard_promotes_broader_range_conditional_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-callable-replacement-boundary")
        expected_workload_ids = (
            "module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-first-match-only-b-branch-warm-bytes",
            "pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-all-c-purged-bytes",
            "pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-c-branch-first-match-only-purged-bytes",
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                "nested-group-callable-replacement-boundary"
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_nested_group_replacement_scorecard_promotes_broader_range_open_ended_branch_local_backreference_bytes_rows_to_measured(
        self,
    ) -> None:
        case = source_tree_scorecard_case("nested-group-replacement-boundary")
        expected_workload_ids = (
            "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-bytes",
            "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-bytes",
            "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-bytes",
            "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-bytes",
        )

        self.assertEqual(
            case.representative_measured_workload_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                "nested-group-replacement-boundary"
            ),
        )
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, case.representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )

    def test_runner_regenerates_source_tree_scorecards(self) -> None:
        for case_id in source_tree_scorecard_case_ids():
            with self.subTest(case_id=case_id):
                case = source_tree_scorecard_case(case_id)
                command = [
                    argument
                    for manifest in case.manifests
                    for argument in ("--manifest", str(manifest.path))
                ]
                if case.selection_mode == "smoke":
                    command.append("--smoke")

                summary, scorecard = run_harness_scorecard(
                    "rebar_harness.benchmarks",
                    command,
                    report_name="benchmarks.json",
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
                selected_workload_ids=case.selected_workload_ids_for_manifest(
                    manifest_id
                ),
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


# Detached benchmark-anchor contract coverage from the former
# `test_standard_benchmark_correctness_anchor_contracts.py` lives below so this
# file is the single benchmark-owner suite.

MODULE_BOUNDARY_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "module_boundary.py"
)
PATTERN_BOUNDARY_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "pattern_boundary.py"
)
COLLECTION_REPLACEMENT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "collection_replacement_boundary.py"
)
OPTIONAL_GROUP_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "optional_group_boundary.py"
)
NESTED_GROUP_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "nested_group_boundary.py"
EXACT_REPEAT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "exact_repeat_quantified_group_boundary.py"
)
RANGED_REPEAT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "ranged_repeat_quantified_group_boundary.py"
)
GROUPED_ALTERNATION_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_alternation_boundary.py"
)
GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_alternation_replacement_boundary.py"
)
NESTED_GROUP_REPLACEMENT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "nested_group_replacement_boundary.py"
)
OPEN_ENDED_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "open_ended_quantified_group_boundary.py"
)


def _compiled_pattern_module_helper_keyword_contract_surface(case_id: str) -> object:
    return next(
        surface
        for surface in (
            compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES
        )
        if surface.case_id == case_id
    )


@pytest.mark.parametrize(
    ("owner_spec", "include_workload"),
    (
        pytest.param(
            compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC,
            _is_collection_replacement_compiled_pattern_success_workload,
            id="collection-replacement-success",
        ),
        pytest.param(
            compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC,
            _is_module_workflow_compiled_pattern_literal_success_workload,
            id="module-boundary-literal-success",
        ),
        pytest.param(
            compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC,
            _is_module_workflow_compiled_pattern_bounded_wildcard_success_workload,
            id="module-boundary-bounded-wildcard-success",
        ),
        pytest.param(
            compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC,
            _is_module_workflow_compiled_pattern_verbose_bytes_success_workload,
            id="module-boundary-verbose-bytes-success",
        ),
    ),
)
def test_compiled_pattern_module_helper_owner_specs_keep_zero_gap_rows_measured(
    owner_spec: object,
    include_workload: object,
) -> None:
    manifest_workload_count = len(selected_manifest_workloads(owner_spec.manifest_path))
    manifest_id = owner_spec.source_workloads()[0].manifest_id
    expected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in selected_manifest_workloads(
            owner_spec.manifest_path,
            include_workload=include_workload,
        )
    )

    assert_zero_gap_manifest_workloads_measured(
        manifest_path=owner_spec.manifest_path,
        manifest_id=manifest_id,
        expected_measured_workload_ids=expected_measured_workload_ids,
        expected_measured_workload_count=manifest_workload_count,
        expected_total_workload_count=manifest_workload_count,
    )


@pytest.mark.parametrize(
    "spec",
    tuple(
        pytest.param(spec, id=str(spec["case_id"]))
        for spec in compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_specs()
    ),
)
@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
def test_run_internal_workload_probe_measures_compiled_pattern_wrong_text_model_contract_workloads(
    spec: dict[str, object],
    import_name: str,
    adapter_name: str,
) -> None:
    for source_workload in (
        compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_source_workloads(
            spec
        )
    ):
        workload = _source_tree_contract_workload(
            source_workload,
            spec=compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_contract_spec(
                spec
            ),
        )
        payload = workload_to_payload(workload)
        round_tripped = workload_from_payload(payload)

        compiled_pattern_module_helper_support._assert_wrong_text_model_payload_round_trip(
            source_workload,
            payload,
            round_tripped,
        )

        probe = benchmarks.run_internal_workload_probe(
            workload_payload=json.dumps(payload, sort_keys=True),
            import_name=import_name,
            adapter_name=adapter_name,
        )

        assert probe["status"] == "measured"
        assert probe["median_ns"] > 0


@pytest.mark.parametrize(
    "spec",
    tuple(
        pytest.param(spec, id=str(spec["case_id"]))
        for spec in compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_specs()
    ),
)
def test_compiled_pattern_wrong_text_model_callbacks_preserve_precompile_contract(
    spec: dict[str, object],
) -> None:
    for source_workload in (
        compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_source_workloads(
            spec
        )
    ):
        expected_build_calls = compiled_pattern_contract_expected_build_calls(
            source_workload,
            label="wrong-text-model",
        )
        expected_callback_result, expected_callback_call, _, _ = (
            compiled_pattern_module_helper_support._compiled_pattern_module_helper_route(
                source_workload,
                collection_replacement_callback_flags=0,
            )
        )
        module = RecordingBenchmarkModule()
        callback = benchmarks.build_callable(
            module,
            "re",
            _source_tree_contract_workload(
                source_workload,
                spec=compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_contract_spec(
                    spec
                ),
            ),
        )

        assert module.calls == expected_build_calls
        assert len(module.compiled_patterns) == 1
        assert callback() == expected_callback_result

        compiled_pattern = module.compiled_patterns[0]
        last_call = module.calls[-1]
        assert last_call[0] == expected_callback_call[0]
        assert last_call[1] is compiled_pattern
        assert last_call[2:] == expected_callback_call[1:]


@pytest.mark.parametrize(
    ("owner_spec", "source_workload"),
    compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS,
)
@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
def test_run_internal_workload_probe_measures_compiled_pattern_module_success_contract_workloads(
    owner_spec: object,
    source_workload: Workload,
    import_name: str,
    adapter_name: str,
) -> None:
    workload = _source_tree_contract_workload(
        source_workload,
        spec=owner_spec.contract_builder_spec(),
    )
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    compiled_pattern_module_helper_support._assert_compiled_pattern_module_success_payload_round_trip(
        source_workload,
        payload,
        round_tripped,
        owner_spec=owner_spec,
    )

    probe = benchmarks.run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name=import_name,
        adapter_name=adapter_name,
    )

    assert probe["status"] == "measured"
    assert probe["median_ns"] > 0


@pytest.mark.parametrize(
    ("owner_spec", "source_workload"),
    compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS,
)
def test_compiled_pattern_module_success_callbacks_precompile_first_argument_before_timing(
    owner_spec: object,
    source_workload: Workload,
) -> None:
    expected_build_calls = owner_spec.expected_build_calls(source_workload)
    expected_callback_call = owner_spec.expected_callback_call(source_workload)
    module = RecordingBenchmarkModule()
    callback = benchmarks.build_callable(
        module,
        "re",
        _source_tree_contract_workload(
            source_workload,
            spec=owner_spec.contract_builder_spec(),
        ),
    )

    assert module.calls == expected_build_calls
    assert len(module.compiled_patterns) == 1
    assert callback() == owner_spec.expected_callback_result(source_workload)

    compiled_pattern = module.compiled_patterns[0]
    last_call = module.calls[-1]
    assert last_call[0] == expected_callback_call[0]
    assert last_call[1] is compiled_pattern
    assert last_call[2:] == expected_callback_call[1:]


def test_compiled_pattern_module_helper_keyword_error_rows_keep_collection_replacement_manifest_measured(
) -> None:
    expected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in selected_manifest_workloads(
            compiled_pattern_module_helper_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
            include_workload=(
                compiled_pattern_module_helper_support._is_collection_replacement_compiled_pattern_keyword_error_workload
            ),
        )
    )
    expected_source_workload_ids = tuple(
        workload.workload_id
        for workload in (
            compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS
        )
    )
    manifest_workload_count = len(
        selected_manifest_workloads(
            compiled_pattern_module_helper_support.COLLECTION_REPLACEMENT_MANIFEST_PATH
        )
    )

    assert expected_measured_workload_ids == expected_source_workload_ids
    assert_zero_gap_manifest_workloads_measured(
        manifest_path=compiled_pattern_module_helper_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
        manifest_id="collection-replacement-boundary",
        expected_measured_workload_ids=expected_measured_workload_ids,
        expected_measured_workload_count=manifest_workload_count,
        expected_total_workload_count=manifest_workload_count,
    )


@pytest.mark.parametrize(
    "source_workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in (
            compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS
        )
    ),
)
def test_compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time(
    monkeypatch: pytest.MonkeyPatch,
    source_workload: Workload,
) -> None:
    workload = _source_tree_contract_workload(
        source_workload,
        spec=(
            compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC.contract_builder_spec()
        ),
    )
    _assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call(
        monkeypatch,
        workload,
        expected_result=run_benchmark_workload_with_cpython(source_workload),
        expected_field_names=(
            compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC.expected_materialized_field_names(
                source_workload
            )
        ),
    )


@pytest.mark.parametrize(
    ("contract_surface", "source_workload"),
    compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS,
)
@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
def test_run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_contract_workloads(
    contract_surface: object,
    source_workload: Workload,
    import_name: str,
    adapter_name: str,
) -> None:
    workload = _source_tree_contract_workload(
        source_workload,
        spec=contract_surface.spec.contract_builder_spec(),
    )
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    contract_surface.assert_payload_round_trip(
        source_workload,
        payload,
        round_tripped,
    )

    probe = benchmarks.run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name=import_name,
        adapter_name=adapter_name,
    )

    assert probe["status"] == "measured"
    assert probe["median_ns"] > 0


@pytest.mark.parametrize(
    ("contract_surface", "source_workload"),
    compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS,
)
def test_compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing(
    contract_surface: object,
    source_workload: Workload,
) -> None:
    expected_build_calls = contract_surface.expected_build_calls(source_workload)
    expected_callback_call = contract_surface.expected_callback_call(source_workload)
    module = RecordingBenchmarkModule()
    callback = benchmarks.build_callable(
        module,
        "re",
        _source_tree_contract_workload(
            source_workload,
            spec=contract_surface.spec.contract_builder_spec(),
        ),
    )

    assert module.calls == expected_build_calls
    assert len(module.compiled_patterns) == 1
    assert callback() == contract_surface.expected_callback_result(source_workload)

    compiled_pattern = module.compiled_patterns[0]
    last_call = module.calls[-1]
    assert last_call[0] == expected_callback_call[0]
    assert last_call[1] is compiled_pattern
    assert last_call[2:] == expected_callback_call[1:]


@pytest.mark.parametrize(
    "source_workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in (
            compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS
        )
    ),
)
def test_compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions(
    monkeypatch: pytest.MonkeyPatch,
    source_workload: Workload,
) -> None:
    contract_surface = _compiled_pattern_module_helper_keyword_contract_surface(
        "keyword-error"
    )
    workload = _source_tree_contract_workload(
        source_workload,
        spec=(
            compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC.contract_builder_spec()
        ),
    )
    observed_field_names = _record_numeric_materialization_fields(monkeypatch)

    re.purge()
    try:
        callback = benchmarks.build_callable(re, "re", workload)
        assert observed_field_names == []

        with pytest.raises(TypeError) as expected_error:
            contract_surface.run_cpython_helper_workload(workload)
        with pytest.raises(TypeError) as observed_error:
            callback()

        assert observed_field_names == list(
            compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC.expected_materialized_field_names(
                source_workload
            )
        )
        assert str(observed_error.value) == str(expected_error.value)
    finally:
        re.purge()
