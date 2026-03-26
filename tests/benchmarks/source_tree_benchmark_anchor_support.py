from __future__ import annotations

import ast
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from functools import cache
import importlib
import pathlib
import re
from typing import Any

import pytest

from rebar_harness.benchmarks import (
    BENCHMARK_WORKLOADS_ROOT,
    BenchmarkManifest,
    Workload,
    determine_phase,
    determine_runner_version,
    published_benchmark_manifests,
    select_workloads,
    workload_from_payload,
    workload_to_payload,
)
from rebar_harness.scorecard_io import build_cpython_baseline
from tests.benchmarks import benchmark_test_support
from tests.benchmarks import (
    collection_replacement_benchmark_anchor_support as collection_replacement_support,
)
from tests.conftest import REPO_ROOT, manifest_records_by_id
from tests.python.fixture_parity_support import (
    BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    OPEN_ENDED_ALTERNATION_BYTES_CASES,
    OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    callable_match_group_signature,
    case_pattern,
    case_replacement_argument,
    case_text_argument,
)

_OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID = (
    "module-search-numbered-optional-group-conditional-cold-gap"
)


_KNOWN_GAP_STATUSES = {"known-gap", "unimplemented"}

SOURCE_TREE_MOVED_CLASS_NAMES = (
    "_SourceTreeContractBuilderSpec",
    "SourceTreeBenchmarkCommonCase",
    "SourceTreeManifestExpectation",
    "SourceTreeDeferredExpectation",
    "SourceTreeScorecardCase",
    "SourceTreeCombinedCase",
    "SourceTreeCombinedPatternGroupExpectation",
    "SourceTreeCombinedManifestShapeExpectation",
    "SourceTreeCombinedFullyMeasuredManifestExpectation",
    "SourceTreeCombinedManifestExpectationDefinition",
    "SourceTreeCombinedSliceExpectation",
)

SOURCE_TREE_MOVED_FUNCTION_NAMES = (
    "_source_tree_contract_workload",
    "_source_tree_contract_manifest",
    "source_tree_scorecard_case_ids",
    "source_tree_scorecard_case",
    "source_tree_combined_target_manifest_ids",
    "source_tree_combined_case",
    "source_tree_combined_manifest_shape_expectation",
    "source_tree_combined_slice_manifest_ids",
    "source_tree_combined_slice_derived_manifest_ids",
    "source_tree_combined_slice_expectations",
    "source_tree_combined_fully_measured_manifest_ids",
    "source_tree_combined_fully_measured_manifest_expectation",
    "source_tree_combined_manifest_representative_measured_workload_ids",
    "assert_zero_gap_bytes_representative_subset",
    "assert_zero_gap_manifest_representative_promotion",
    "expected_summary_for_manifests",
    "representative_measured_workload_ids",
    "select_source_tree_combined_slice_rows",
    "assert_source_tree_combined_manifest_slice",
    "assert_source_tree_combined_pattern_group",
    "assert_single_manifest_zero_gap_scorecard_case_reuses_shared_expectation",
    "assert_zero_gap_representative_workload_subset",
)

SOURCE_TREE_MOVED_CONSTANT_NAMES = (
    "SOURCE_TREE_SCORECARD_EXPECTATIONS",
    "SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS",
    "SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS",
)

SOURCE_TREE_ROUTED_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_NAMES = (
    "_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES",
    "_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES",
    "_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS",
    "_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS",
    "_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS",
)

SOURCE_TREE_ROUTED_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_NAMES = (
    "_compiled_pattern_wrong_text_model_specs",
    "_compiled_pattern_wrong_text_model_source_workloads",
    "compiled_pattern_contract_expected_build_calls",
    "_compiled_pattern_module_helper_route",
)

SOURCE_TREE_ROUTED_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_NAMES = (
    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS",
    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS",
    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC",
    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS",
    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS",
    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES",
    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC",
    "_is_collection_replacement_compiled_pattern_keyword_error_workload",
    "_assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call",
)

SOURCE_TREE_ROUTED_COMPILED_PATTERN_MODULE_SUCCESS_CONTRACT_NAMES = (
    "_is_module_workflow_compiled_pattern_literal_success_workload",
    "_is_module_workflow_compiled_pattern_bounded_wildcard_success_workload",
    "_is_module_workflow_compiled_pattern_verbose_bytes_success_workload",
    "_assert_compiled_pattern_module_success_payload_round_trip",
)

SOURCE_TREE_LOCAL_CONTRACT_BUILDER_FUNCTION_NAMES = (
    "compiled_pattern_module_compile_contract_builder_spec",
    "compiled_pattern_module_success_contract_builder_spec",
    "compiled_pattern_module_helper_keyword_contract_builder_spec",
)

SOURCE_TREE_LOCAL_CONTRACT_BUILDER_CONSTANT_NAMES = (
    "_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_SPECS",
)

SOURCE_TREE_CENTRALIZED_MANIFEST_PATH_NAMES = (
    "OPTIONAL_GROUP_MANIFEST_PATH",
    "NESTED_GROUP_MANIFEST_PATH",
    "EXACT_REPEAT_MANIFEST_PATH",
    "RANGED_REPEAT_MANIFEST_PATH",
    "GROUPED_ALTERNATION_MANIFEST_PATH",
    "GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH",
    "NESTED_GROUP_REPLACEMENT_MANIFEST_PATH",
    "OPEN_ENDED_MANIFEST_PATH",
)

SOURCE_TREE_RETIRED_SHARED_SUPPORT_NAMES = (
    "MODULE_BOUNDARY_MANIFEST_PATH",
    *SOURCE_TREE_CENTRALIZED_MANIFEST_PATH_NAMES,
    "StandardBenchmarkAnchorContractDefinition",
    "_definition_anchor_expectations",
    "_workload_case_pair_anchor_expectations",
    "_workload_case_pairs_case_ids",
    "_workload_case_pairs_workload_ids",
    "freeze_signature_value",
    "live_manifest_workloads",
    "published_case_ids_by_signature",
    "published_cases_by_id",
    "CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS",
)

SOURCE_TREE_MOVED_REPORT_CONTRACT_HELPER_NAMES = (
    "_assert_benchmark_summary_consistent",
    "_artifact_manifest_record",
    "assert_source_tree_benchmark_contract",
    "assert_benchmark_manifest_contract",
    "find_manifest_record",
)

SOURCE_TREE_ROUTED_REPORT_CONTRACT_HELPER_NAMES = (
    "assert_source_tree_benchmark_contract",
    "assert_benchmark_manifest_contract",
    "find_manifest_record",
    "assert_zero_gap_bytes_representative_subset",
    "assert_zero_gap_manifest_representative_promotion",
)

SOURCE_TREE_ROUTED_SUITE_ASSERTION_HELPER_NAMES = (
    "assert_source_tree_combined_manifest_slice",
    "assert_source_tree_combined_pattern_group",
    "assert_single_manifest_zero_gap_scorecard_case_reuses_shared_expectation",
    "assert_zero_gap_representative_workload_subset",
)


@dataclass(frozen=True, slots=True)
class _SourceTreeContractBuilderSpec:
    manifest_id: str
    excluded_fields: frozenset[str]
    manifest_timed_samples: int = 2
    timing_scope: str | None = None
    notes: tuple[str, ...] = ()


def _source_tree_contract_workload(
    source_workload: Workload,
    *,
    spec: _SourceTreeContractBuilderSpec,
) -> Workload:
    manifest_payload = _source_tree_contract_manifest((source_workload,), spec=spec)[
        "workloads"
    ][0]
    return workload_from_payload(
        {
            "manifest_id": spec.manifest_id,
            "workload_id": str(manifest_payload["id"]),
            **{key: value for key, value in manifest_payload.items() if key != "id"},
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "categories": [],
            "syntax_features": [],
            "smoke": False,
        }
    )


def _source_tree_contract_manifest(
    source_workloads: tuple[Workload, ...],
    *,
    spec: _SourceTreeContractBuilderSpec,
) -> dict[str, object]:
    workloads: list[dict[str, object]] = []
    for source_workload in source_workloads:
        payload = workload_to_payload(source_workload)
        manifest_payload: dict[str, object] = {
            "id": f"{source_workload.workload_id}-contract",
            **{
                key: value
                for key, value in payload.items()
                if key not in spec.excluded_fields
            },
        }
        if spec.timing_scope is not None:
            manifest_payload["timing_scope"] = spec.timing_scope
        if spec.notes:
            manifest_payload["notes"] = list(spec.notes)
        workloads.append(manifest_payload)
    return {
        "schema_version": 1,
        "manifest_id": spec.manifest_id,
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": spec.manifest_timed_samples,
        },
        "workloads": workloads,
    }


@cache
def _source_tree_combined_suite_module() -> object:
    return importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )


@cache
def _parsed_source_tree_combined_suite_ast() -> ast.Module:
    return benchmark_test_support._parsed_module_ast(_source_tree_combined_suite_module())


def _assert_source_tree_combined_routes_owner_names_through_module_alias(
    *,
    alias_name: str,
    owner_module: object,
    owner_names: tuple[str, ...],
) -> object:
    combined_suite = _source_tree_combined_suite_module()
    combined_suite_ast = _parsed_source_tree_combined_suite_ast()
    _, local_assignment_names = (
        benchmark_test_support.top_level_module_definition_and_assignment_names(
            combined_suite
        )
    )
    owner_module_name = owner_module.__name__
    owner_import_name = owner_module_name.rsplit(".", 1)[-1]
    benchmark_test_support_alias_names = benchmark_test_support._module_alias_names(
        combined_suite_ast,
        import_from_module="tests.benchmarks",
        import_name="benchmark_test_support",
        dotted_import_name="tests.benchmarks.benchmark_test_support",
    )
    owner_alias_names = benchmark_test_support._module_alias_names(
        combined_suite_ast,
        import_from_module="tests.benchmarks",
        import_name=owner_import_name,
        dotted_import_name=owner_module_name,
    )

    assert alias_name in owner_alias_names
    assert getattr(combined_suite, alias_name) is owner_module

    direct_import_names = {
        alias.name
        for node in ast.walk(combined_suite_ast)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }
    local_alias_names: set[str] = set()
    for node in combined_suite_ast.body:
        if isinstance(node, ast.Assign):
            targets = tuple(
                target.id for target in node.targets if isinstance(target, ast.Name)
            )
            value = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            targets = (node.target.id,)
            value = node.value
        else:
            continue

        if isinstance(value, ast.Name) and value.id in owner_names:
            local_alias_names.update(targets)
            continue

        if (
            isinstance(value, ast.Attribute)
            and isinstance(value.value, ast.Name)
            and value.value.id
            in (owner_alias_names | benchmark_test_support_alias_names)
            and value.attr in owner_names
        ):
            local_alias_names.update(targets)

    local_name_loads = {
        node.id
        for node in ast.walk(combined_suite_ast)
        if isinstance(node, ast.Name)
        and isinstance(node.ctx, ast.Load)
        and node.id in owner_names
    }
    direct_benchmark_test_support_refs = {
        node.attr
        for node in ast.walk(combined_suite_ast)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id in benchmark_test_support_alias_names
        and node.attr in owner_names
    }
    aliased_owner_refs = {
        node.attr
        for node in ast.walk(combined_suite_ast)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id in (owner_alias_names - {alias_name})
        and node.attr in owner_names
    }
    owner_alias = getattr(combined_suite, alias_name)
    for name in owner_names:
        assert getattr(owner_alias, name) is getattr(owner_module, name)
        assert name not in direct_import_names
        assert name not in local_assignment_names
        assert name not in local_name_loads
    assert local_alias_names == set()
    assert direct_benchmark_test_support_refs == set()
    assert aliased_owner_refs == set()
    return combined_suite


def compiled_pattern_module_compile_contract_builder_spec(
    contract_case: Any,
) -> _SourceTreeContractBuilderSpec:
    return _SourceTreeContractBuilderSpec(
        manifest_id="module-boundary",
        excluded_fields=contract_case.manifest_excluded_fields(),
        manifest_timed_samples=2,
        timing_scope="module-helper-call",
        notes=(contract_case.note(),),
    )


def build_compiled_pattern_module_contract_anchor_lanes(
    *,
    contract_cases: Iterable[benchmark_test_support.CompiledPatternModuleCompileContractCase],
    published_case_ids_by_signature: Callable[
        [Callable[[Any], tuple[Any, ...] | None]],
        dict[tuple[Any, ...], tuple[str, ...]],
    ],
) -> tuple[benchmark_test_support._CompiledPatternModuleContractAnchorLane, ...]:
    contract_cases = tuple(contract_cases)
    return tuple(
        benchmark_test_support._CompiledPatternModuleContractAnchorLane(
            case_id=contract_case.case_id,
            contract_filename=contract_case.anchor_contract_filename,
            source_workloads=source_workloads,
            contract_builder_spec=lambda contract_case=contract_case: (
                compiled_pattern_module_compile_contract_builder_spec(contract_case)
            ),
            expected_anchor_case_ids=contract_case.expected_anchor_case_ids,
            anchor_case_ids=published_case_ids_by_signature(
                contract_case.correctness_case_signature
            ),
            workload_signature=contract_case.workload_signature,
            include_workload=contract_case.include_workload,
            expected_anchor_pairs=contract_case.expected_anchor_pairs,
        )
        for contract_case in contract_cases
        for source_workloads in (contract_case.source_workloads(),)
    )


def _build_compiled_pattern_module_compile_standard_benchmark_definitions() -> tuple[
    benchmark_test_support.StandardBenchmarkAnchorContractDefinition, ...
]:
    return tuple(
        owner_spec.anchor_definition()
        for owner_spec in (
            *_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS,
            *_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS,
        )
    )


def compiled_pattern_module_success_contract_builder_spec(
    owner_spec: Any,
) -> _SourceTreeContractBuilderSpec:
    return _SourceTreeContractBuilderSpec(
        manifest_id=owner_spec.contract_manifest_id,
        excluded_fields=_COMPILED_PATTERN_MODULE_SUCCESS_CONTRACT_EXCLUDED_FIELDS,
        timing_scope="module-helper-call",
        notes=(
            "Ensures benchmark manifests keep the bounded "
            "compiled-pattern-first-argument successful "
            f"{owner_spec.note_surface} rows unresolved until helper invocation.",
        ),
    )


def compiled_pattern_module_helper_keyword_contract_builder_spec(
    spec: Any,
) -> _SourceTreeContractBuilderSpec:
    excluded_fields = (
        _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_PAYLOAD_DROP_FIELDS
    )
    if not spec.preserve_expected_exception:
        excluded_fields = excluded_fields | {"expected_exception"}
    return _SourceTreeContractBuilderSpec(
        manifest_id="collection-replacement-boundary",
        excluded_fields=excluded_fields,
        manifest_timed_samples=spec.manifest_timed_samples,
        timing_scope="module-helper-call",
        notes=spec.notes,
    )


def _compiled_pattern_wrong_text_model_specs() -> tuple[dict[str, object], ...]:
    return (
        {
            "case_id": "compiled_pattern_module_helper_wrong_text_model",
            "manifest_path": "collection_replacement_boundary.py",
            "include_workload": (
                benchmark_test_support._is_collection_replacement_wrong_text_model_workload
            ),
            "contract_manifest_id": "collection-replacement-boundary",
            "contract_filename": (
                "python_benchmark_compiled_pattern_collection_replacement_wrong_text_model_contract.py"
            ),
            "expected_source_workload_ids": (
                benchmark_test_support._COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
            ),
        },
        {
            "case_id": "compiled_pattern_module_boundary_wrong_text_model",
            "manifest_path": "module_boundary.py",
            "include_workload": _is_module_workflow_compiled_pattern_wrong_text_model_workload,
            "contract_manifest_id": "module-boundary",
            "contract_filename": (
                "python_benchmark_compiled_pattern_module_boundary_wrong_text_model_contract.py"
            ),
            "expected_source_workload_ids": _COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS,
        },
    )


def _compiled_pattern_wrong_text_model_source_workloads(
    spec: dict[str, object],
) -> tuple[Workload, ...]:
    return benchmark_test_support.selected_manifest_workloads(
        spec["manifest_path"],
        include_workload=spec["include_workload"],
    )


_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_PAYLOAD_DROP_FIELDS = frozenset(
    {
        "manifest_id",
        "workload_id",
        "warmup_iterations",
        "sample_iterations",
        "timed_samples",
        "notes",
        "smoke",
        "categories",
        "syntax_features",
        "haystack_text_model",
    }
)


_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_SPECS = {
    "collection-replacement-boundary": _SourceTreeContractBuilderSpec(
        manifest_id="collection-replacement-boundary",
        excluded_fields=(
            benchmark_test_support.COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS
        ),
        timing_scope="module-helper-call",
        notes=(
            "Ensures benchmark manifests keep the bounded compiled-pattern-first-argument wrong-text-model collection/replacement rows unresolved until helper invocation.",
        ),
    ),
    "module-boundary": _SourceTreeContractBuilderSpec(
        manifest_id="module-boundary",
        excluded_fields=(
            benchmark_test_support.COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS
        ),
        timing_scope="module-helper-call",
        notes=(
            "Ensures benchmark manifests keep the bounded compiled-pattern-first-argument wrong-text-model module-boundary rows unresolved until helper invocation.",
        ),
    ),
}
_COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS = (
    "module-search-on-bytes-string-warm-str-compiled-pattern",
    "module-match-on-str-string-purged-bytes-compiled-pattern",
    "module-fullmatch-on-bytes-string-warm-str-compiled-pattern",
)
_COMPILED_PATTERN_MODULE_SUCCESS_CONTRACT_EXCLUDED_FIELDS = (
    benchmark_test_support.COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS
    | {
        "categories",
        "syntax_features",
        "expected_exception",
        "haystack_text_model",
    }
)


def _is_module_workflow_compiled_pattern_wrong_text_model_workload(
    workload: object,
) -> bool:
    return (
        not workload.kwargs
        and workload.use_compiled_pattern
        and workload.operation
        in benchmark_test_support._COMPILED_PATTERN_MODULE_HELPER_OPERATIONS
        and getattr(workload, "haystack_text_model", None) is not None
        and workload.expected_exception is not None
        and workload.expected_exception.get("type") == "TypeError"
    )


_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC = _SourceTreeContractBuilderSpec(
    manifest_id="pattern-boundary",
    excluded_fields=(
        benchmark_test_support._PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_EXCLUDED_FIELDS
    ),
    timing_scope="pattern-helper-call",
)


def _assert_benchmark_summary_consistent(
    testcase: Any,
    scorecard: dict[str, Any],
    summary: dict[str, Any],
) -> None:
    workloads = scorecard["workloads"]
    expected_summary = {
        key: scorecard["summary"][key]
        for key in (
            "known_gap_count",
            "measured_workloads",
            "module_workloads",
            "parser_workloads",
            "regression_workloads",
            "total_workloads",
        )
    }
    testcase.assertEqual(summary, expected_summary)
    testcase.assertEqual(summary["total_workloads"], len(workloads))
    testcase.assertEqual(
        summary["measured_workloads"] + summary["known_gap_count"],
        summary["total_workloads"],
    )
    testcase.assertEqual(
        summary["parser_workloads"],
        scorecard["families"]["parser"]["workload_count"],
    )
    testcase.assertEqual(
        summary["module_workloads"],
        scorecard["families"]["module"]["workload_count"],
    )
    testcase.assertEqual(
        summary["regression_workloads"],
        sum(1 for workload in workloads if workload["manifest_id"] == "regression-matrix"),
    )

    for cache_mode, expected_count in scorecard["summary"]["workloads_by_cache_mode"].items():
        testcase.assertEqual(
            expected_count,
            sum(1 for workload in workloads if workload["cache_mode"] == cache_mode),
        )

    if summary["measured_workloads"] > 0:
        testcase.assertIsInstance(scorecard["summary"]["baseline_median_ns"], int)
        testcase.assertGreater(scorecard["summary"]["baseline_median_ns"], 0)
        testcase.assertGreater(scorecard["summary"]["baseline_median_ops_per_second"], 0)
        testcase.assertIsInstance(scorecard["summary"]["implementation_median_ns"], int)
        testcase.assertGreater(scorecard["summary"]["implementation_median_ns"], 0)
        testcase.assertGreater(
            scorecard["summary"]["implementation_median_ops_per_second"],
            0,
        )

    for family_id, family_summary in scorecard["families"].items():
        family_workloads = [workload for workload in workloads if workload["family"] == family_id]
        testcase.assertEqual(family_summary["workload_count"], len(family_workloads))
        testcase.assertEqual(
            family_summary["known_gap_count"],
            sum(
                1
                for workload in family_workloads
                if workload["status"] in _KNOWN_GAP_STATUSES
            ),
        )
        for cache_mode, cache_summary in family_summary["cache_modes"].items():
            testcase.assertEqual(
                cache_summary["workload_count"],
                sum(
                    1
                    for workload in family_workloads
                    if workload["cache_mode"] == cache_mode
                ),
            )

    for cache_mode, cache_summary in scorecard["cache_modes"].items():
        cache_workloads = [workload for workload in workloads if workload["cache_mode"] == cache_mode]
        testcase.assertEqual(cache_summary["workload_count"], len(cache_workloads))
        testcase.assertEqual(
            cache_summary["known_gap_count"],
            sum(1 for workload in cache_workloads if workload["status"] in _KNOWN_GAP_STATUSES),
        )


def _artifact_manifest_record(
    manifest_path: str,
    manifest: BenchmarkManifest,
) -> dict[str, Any]:
    return {
        "manifest": manifest_path,
        "manifest_id": manifest.manifest_id,
        "manifest_schema_version": manifest.schema_version,
        "workload_count": len(manifest.workloads),
        "smoke_workload_ids": manifest.smoke_workload_ids(),
        "spec_refs": list(manifest.spec_refs),
    }


def assert_source_tree_benchmark_contract(
    testcase: Any,
    scorecard: dict[str, Any],
    summary: dict[str, Any],
    *,
    expected_phase: str,
    expected_runner_version: str,
    expected_adapter: str,
    expected_manifests: list[BenchmarkManifest],
    expected_manifest_paths: list[str],
    expected_selection_mode: str,
    tracked_report_path: pathlib.Path | None = None,
) -> None:
    expected_manifest_records = [
        _artifact_manifest_record(manifest_path, manifest)
        for manifest_path, manifest in zip(
            expected_manifest_paths,
            expected_manifests,
            strict=True,
        )
    ]

    _assert_benchmark_summary_consistent(testcase, scorecard, summary)
    testcase.assertEqual(scorecard["schema_version"], "1.0")
    testcase.assertEqual(scorecard["suite"], "benchmarks")
    testcase.assertEqual(scorecard["phase"], expected_phase)
    expected_baseline = {
        **build_cpython_baseline(version_family="3.12.x"),
        "re_module": "re",
    }
    for key, expected_value in expected_baseline.items():
        testcase.assertEqual(scorecard["baseline"][key], expected_value)
    testcase.assertEqual(scorecard["implementation"]["module_name"], "rebar")
    testcase.assertEqual(scorecard["implementation"]["adapter"], expected_adapter)
    testcase.assertEqual(
        scorecard["implementation"]["adapter_mode_requested"],
        "source-tree-shim",
    )
    testcase.assertEqual(
        scorecard["implementation"]["adapter_mode_resolved"],
        "source-tree-shim",
    )
    testcase.assertEqual(scorecard["implementation"]["build_mode"], "source-tree-shim")
    testcase.assertEqual(scorecard["implementation"]["timing_path"], "source-tree-shim")
    testcase.assertIsNone(scorecard["implementation"]["native_build_tool"])
    testcase.assertIsNone(scorecard["implementation"]["native_wheel"])
    testcase.assertIsInstance(scorecard["implementation"]["native_module_loaded"], bool)
    testcase.assertEqual(scorecard["implementation"]["native_module_name"], "rebar._rebar")
    if scorecard["implementation"]["native_module_loaded"]:
        testcase.assertEqual(scorecard["implementation"]["native_scaffold_status"], "scaffold-only")
        testcase.assertEqual(
            scorecard["implementation"]["native_target_cpython_series"],
            "3.12.x",
        )
    else:
        testcase.assertIsNone(scorecard["implementation"]["native_scaffold_status"])
        testcase.assertIsNone(
            scorecard["implementation"]["native_target_cpython_series"]
        )
    testcase.assertIn(
        "not requested",
        scorecard["implementation"]["native_unavailable_reason"],
    )
    testcase.assertEqual(scorecard["environment"]["runner_version"], expected_runner_version)
    testcase.assertEqual(
        scorecard["environment"]["execution_model"],
        "single-process in-process adapter comparison",
    )
    testcase.assertEqual(scorecard["artifacts"]["selection_mode"], expected_selection_mode)
    testcase.assertIsNone(scorecard["artifacts"]["raw_samples"])
    testcase.assertEqual(scorecard["artifacts"]["manifests"], expected_manifest_records)
    if len(expected_manifest_records) == 1:
        testcase.assertEqual(
            scorecard["artifacts"]["manifest"],
            expected_manifest_records[0]["manifest"],
        )
        testcase.assertEqual(
            scorecard["artifacts"]["manifest_id"],
            expected_manifest_records[0]["manifest_id"],
        )
        testcase.assertEqual(
            scorecard["artifacts"]["manifest_schema_version"],
            expected_manifest_records[0]["manifest_schema_version"],
        )
        testcase.assertEqual(
            scorecard["artifacts"]["workload_count"],
            expected_manifest_records[0]["workload_count"],
        )
        testcase.assertEqual(
            scorecard["artifacts"]["smoke_workload_ids"],
            expected_manifest_records[0]["smoke_workload_ids"],
        )
        testcase.assertEqual(
            scorecard["artifacts"]["spec_refs"],
            expected_manifest_records[0]["spec_refs"],
        )
    else:
        testcase.assertEqual(scorecard["artifacts"]["manifest"], None)
        testcase.assertEqual(scorecard["artifacts"]["manifest_id"], "combined-benchmark-suite")
        testcase.assertEqual(scorecard["artifacts"]["manifest_schema_version"], 1)
    if tracked_report_path is not None:
        testcase.assertTrue(tracked_report_path.is_file())


def assert_benchmark_manifest_contract(
    testcase: Any,
    manifest_summary: dict[str, Any],
    manifest_record: dict[str, Any],
    *,
    manifest: BenchmarkManifest,
    manifest_path: str,
    known_gap_count: int,
    selection_mode: str = "full",
    selected_workload_ids: tuple[str, ...] | None = None,
) -> None:
    workloads = list(manifest.workloads)
    selected_workloads = manifest.selected_workloads(
        selected_workload_ids=selected_workload_ids
    )
    smoke_ids = manifest.smoke_workload_ids()
    operations = sorted({workload.operation for workload in selected_workloads})
    families = sorted({workload.family for workload in selected_workloads})

    testcase.assertEqual(manifest_summary["workload_count"], len(workloads))
    testcase.assertEqual(manifest_summary["selected_workload_count"], len(selected_workloads))
    testcase.assertEqual(
        manifest_summary["measured_workloads"],
        len(selected_workloads) - known_gap_count,
    )
    testcase.assertEqual(manifest_summary["known_gap_count"], known_gap_count)
    testcase.assertEqual(
        manifest_summary["readiness"],
        "measured" if known_gap_count == 0 else "partial",
    )
    testcase.assertEqual(manifest_summary["selection_mode"], selection_mode)
    testcase.assertEqual(manifest_summary["available_smoke_workload_count"], len(smoke_ids))
    testcase.assertEqual(manifest_summary["smoke_workload_ids"], smoke_ids)
    testcase.assertEqual(manifest_summary["families"], families)
    testcase.assertEqual(manifest_summary["operations"], operations)
    testcase.assertEqual(manifest_summary["spec_refs"], manifest.spec_refs)
    if manifest.notes:
        testcase.assertEqual(manifest_summary["notes"], manifest.notes)

    testcase.assertEqual(manifest_record["manifest_id"], manifest.manifest_id)
    testcase.assertEqual(manifest_record["manifest"], manifest_path)
    testcase.assertEqual(manifest_record["smoke_workload_ids"], smoke_ids)


def find_manifest_record(scorecard: dict[str, Any], manifest_id: str) -> dict[str, Any]:
    for manifest_record in scorecard["artifacts"]["manifests"]:
        if str(manifest_record["manifest_id"]) == manifest_id:
            return manifest_record
    raise AssertionError(f"missing manifest record for {manifest_id!r}")


def _assert_zero_gap_manifest_state(
    testcase: Any,
    manifest_id: str,
) -> tuple[Any, tuple[str, ...], Any, Any, int]:
    manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
    public_representatives = (
        source_tree_combined_manifest_representative_measured_workload_ids(
            manifest_id
        )
    )
    testcase.assertIsNone(manifest_definition.known_gap_workload_ids)
    testcase.assertEqual(
        manifest_definition.representative_known_gap_workload_ids or (),
        (),
    )

    case = source_tree_combined_case(manifest_id)
    manifest_expectation = case.manifest_expectation
    testcase.assertEqual(manifest_expectation.known_gap_count, 0)
    testcase.assertEqual(
        manifest_expectation.representative_known_gap_workload_ids,
        (),
    )
    expected_measured_workload_count = len(
        case.selected_workload_ids_for_manifest(manifest_id)
    )
    return (
        manifest_definition,
        public_representatives,
        case,
        manifest_expectation,
        expected_measured_workload_count,
    )


def assert_zero_gap_bytes_representative_subset(
    testcase: Any,
    manifest_id: str,
    expected_workload_ids: tuple[str, ...],
) -> None:
    (
        manifest_definition,
        public_representatives,
        case,
        manifest_expectation,
        expected_measured_workload_count,
    ) = _assert_zero_gap_manifest_state(testcase, manifest_id)
    testcase.assertIsNone(
        manifest_definition.representative_known_gap_workload_ids
    )
    testcase.assertIn(
        expected_workload_ids,
        manifest_definition.zero_gap_bytes_representative_subsets,
    )
    for workload_id in expected_workload_ids:
        with testcase.subTest(workload_id=workload_id):
            testcase.assertIn(workload_id, public_representatives)
            if manifest_definition.representative_measured_workload_ids is not None:
                testcase.assertIn(
                    workload_id,
                    manifest_definition.representative_measured_workload_ids,
                )
    expected_total_workload_count = len(case.target_manifest.workloads)
    testcase.assertEqual(
        expected_measured_workload_count,
        expected_total_workload_count,
    )
    for workload_id in expected_workload_ids:
        with testcase.subTest(public_workload_id=workload_id):
            testcase.assertIn(workload_id, public_representatives)
            if manifest_expectation.representative_measured_workload_ids:
                testcase.assertIn(
                    workload_id,
                    manifest_expectation.representative_measured_workload_ids,
                )

    benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
        manifest_path=case.target_manifest.path,
        manifest_id=manifest_id,
        expected_measured_workload_ids=expected_workload_ids,
        expected_measured_workload_count=expected_measured_workload_count,
        expected_total_workload_count=expected_total_workload_count,
    )


def assert_zero_gap_manifest_representative_promotion(
    testcase: Any,
    manifest_id: str,
) -> None:
    (
        manifest_definition,
        _public_representatives,
        case,
        manifest_expectation,
        expected_measured_workload_count,
    ) = _assert_zero_gap_manifest_state(testcase, manifest_id)
    expected_workload_ids = manifest_definition.representative_measured_workload_ids
    testcase.assertIsNotNone(expected_workload_ids)
    assert expected_workload_ids is not None
    testcase.assertEqual(
        manifest_definition.representative_measured_workload_ids,
        expected_workload_ids,
    )
    testcase.assertEqual(
        manifest_expectation.representative_measured_workload_ids,
        expected_workload_ids,
    )

    benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
        manifest_path=case.target_manifest.path,
        manifest_id=manifest_id,
        expected_measured_workload_ids=expected_workload_ids,
        expected_measured_workload_count=expected_measured_workload_count,
    )


def assert_source_tree_combined_manifest_slice(
    testcase: Any,
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

    testcase.assertEqual(
        tuple(workload.workload_id for workload in matched_rows),
        expected_workload_ids,
    )
    testcase.assertEqual(
        {workload.pattern for workload in matched_rows},
        expectation.expected_patterns,
    )
    testcase.assertEqual(
        {workload.operation for workload in matched_rows},
        expectation.expected_operations,
    )
    testcase.assertEqual(
        {
            str(workload.haystack)
            for workload in matched_rows
            if workload.haystack is not None
        },
        expectation.expected_haystacks,
    )

    for workload in matched_rows:
        with testcase.subTest(
            slice_id=expectation.slice_id,
            workload_id=workload.workload_id,
        ):
            for category in expectation.required_row_categories:
                testcase.assertIn(category, workload.categories)

    scorecard_rows = [
        workload
        for workload in scorecard["workloads"]
        if workload["manifest_id"] == manifest_id
        and workload["id"] in expected_workload_ids
    ]
    testcase.assertEqual(
        {workload["id"] for workload in scorecard_rows},
        set(expected_workload_ids),
    )

    with testcase.subTest(slice_id=expectation.slice_id):
        benchmark_test_support.assert_manifest_workload_contracts(
            testcase,
            manifest,
            scorecard,
            (
                (workload_id, expected_status)
                for workload_id in expected_workload_ids
            ),
            subtest_label="workload_id",
        )


def assert_source_tree_combined_pattern_group(
    testcase: Any,
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

    testcase.assertGreaterEqual(
        len(manifest_rows),
        expectation.minimum_rows,
        f"expected benchmark rows for the {slice_id} slice",
    )

    for pattern in patterns:
        pattern_rows = [
            workload for workload in manifest_rows if workload.pattern == pattern
        ]
        testcase.assertGreaterEqual(
            len(pattern_rows),
            3,
            f"expected compile/search/fullmatch coverage for {pattern!r}",
        )
        testcase.assertTrue(
            set(required_operations).issubset(
                {workload.operation for workload in pattern_rows}
            )
        )
        for workload in pattern_rows:
            with testcase.subTest(pattern=pattern, workload_id=workload.workload_id):
                for category in required_categories:
                    testcase.assertIn(category, workload.categories)

    manifest_search_haystacks = {
        str(workload.haystack)
        for workload in manifest_rows
        if workload.operation == "module.search"
    }
    for haystack in search_haystacks:
        testcase.assertIn(haystack, manifest_search_haystacks)
    for snippet in search_haystack_substrings:
        testcase.assertTrue(
            any(snippet in haystack for haystack in manifest_search_haystacks),
            f"expected a module.search workload covering {snippet!r}",
        )

    manifest_pattern_haystacks = {
        str(workload.haystack)
        for workload in manifest_rows
        if workload.operation == "pattern.fullmatch"
    }
    for haystack in pattern_haystacks:
        testcase.assertIn(haystack, manifest_pattern_haystacks)

    scorecard_rows = [
        workload
        for workload in scorecard["workloads"]
        if workload["manifest_id"] == manifest_id
        and workload["pattern"] in patterns
    ]
    testcase.assertEqual(
        {workload["id"] for workload in scorecard_rows},
        {workload.workload_id for workload in manifest_rows},
    )
    for workload in scorecard_rows:
        with testcase.subTest(scorecard_workload_id=workload["id"]):
            testcase.assertEqual(workload["status"], "measured")
            testcase.assertEqual(
                workload["implementation_timing"]["status"],
                "measured",
            )
            testcase.assertGreater(workload["implementation_ns"], 0)


def assert_single_manifest_zero_gap_scorecard_case_reuses_shared_expectation(
    testcase: Any,
    manifest_id: str,
) -> None:
    case = source_tree_scorecard_case(manifest_id)
    combined_case = source_tree_combined_case(manifest_id)

    testcase.assertEqual(
        case.manifest_expectations[manifest_id].known_gap_count,
        0,
    )
    testcase.assertEqual(
        case.representative_measured_workload_ids,
        combined_case.manifest_expectation.representative_measured_workload_ids,
    )
    testcase.assertEqual(case.representative_known_gap_workload_ids, ())


def assert_zero_gap_representative_workload_subset(
    testcase: Any,
    manifest_id: str,
    expected_workload_ids: tuple[str, ...],
) -> None:
    case = source_tree_combined_case(manifest_id)
    public_representatives = (
        source_tree_combined_manifest_representative_measured_workload_ids(
            manifest_id
        )
    )

    testcase.assertEqual(case.manifest_expectation.known_gap_count, 0)
    testcase.assertEqual(
        case.manifest_expectation.representative_known_gap_workload_ids,
        (),
    )

    explicit_representatives = (
        case.manifest_expectation.representative_measured_workload_ids
    )
    for workload_id in expected_workload_ids:
        with testcase.subTest(manifest_id=manifest_id, workload_id=workload_id):
            testcase.assertIn(workload_id, public_representatives)
            if explicit_representatives:
                testcase.assertIn(workload_id, explicit_representatives)

    if not explicit_representatives:
        testcase.assertEqual(explicit_representatives, ())


@cache
def _source_tree_standard_benchmark_definitions() -> tuple[object, ...]:
    return (
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="optional-group-conditional",
            manifest_paths=(benchmark_test_support.OPTIONAL_GROUP_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
                benchmark_test_support.OPTIONAL_GROUP_MANIFEST_PATH,
                {
                    _OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID: (
                        "optional-group-conditional-module-search-present-str",
                    ),
                },
            ),
            include_workload=_is_optional_group_conditional_workload,
            correctness_case_signature=_optional_group_correctness_case_signature,
            workload_signature=_optional_group_workload_signature,
            run_callback_result_parity=True,
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="nested-group",
            manifest_paths=(benchmark_test_support.NESTED_GROUP_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
                benchmark_test_support.NESTED_GROUP_MANIFEST_PATH,
                {
                    "module-compile-nested-group-cold-str": (
                        "nested-group-compile-metadata-str",
                    ),
                    "module-search-nested-group-warm-str": (
                        "nested-group-module-search-str",
                    ),
                    "pattern-fullmatch-nested-group-purged-str": (
                        "nested-group-pattern-fullmatch-str",
                    ),
                    "module-compile-named-nested-group-warm-str": (
                        "named-nested-group-compile-metadata-str",
                    ),
                    "module-search-named-nested-group-warm-str": (
                        "named-nested-group-module-search-str",
                    ),
                    "pattern-fullmatch-named-nested-group-purged-str": (
                        "named-nested-group-pattern-fullmatch-str",
                    ),
                },
            ),
            include_workload=lambda _: True,
            correctness_case_signature=_nested_group_correctness_case_signature,
            workload_signature=_nested_group_workload_signature,
            run_callback_result_parity=True,
            expected_excluded_workload_ids=frozenset(
                {
                    "module-search-triple-nested-group-cold-gap",
                    "pattern-fullmatch-named-quantified-nested-group-purged-gap",
                }
            ),
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="exact-repeat",
            manifest_paths=(benchmark_test_support.EXACT_REPEAT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
                benchmark_test_support.EXACT_REPEAT_MANIFEST_PATH,
                {
                    "module-compile-numbered-exact-repeat-group-cold-str": (
                        "exact-repeat-numbered-group-compile-metadata-str",
                    ),
                    "module-search-numbered-exact-repeat-group-warm-str": (
                        "exact-repeat-numbered-group-module-search-str",
                    ),
                    "pattern-fullmatch-numbered-exact-repeat-group-purged-str": (
                        "exact-repeat-numbered-group-pattern-fullmatch-str",
                    ),
                    "module-compile-named-exact-repeat-group-warm-str": (
                        "exact-repeat-named-group-compile-metadata-str",
                    ),
                    "module-search-named-exact-repeat-group-warm-str": (
                        "exact-repeat-named-group-module-search-str",
                    ),
                    "pattern-fullmatch-named-exact-repeat-group-purged-str": (
                        "exact-repeat-named-group-pattern-fullmatch-str",
                    ),
                    "module-search-numbered-broader-ranged-repeat-group-cold-gap": (
                        "broader-range-wider-ranged-repeat-numbered-group-module-search-upper-bound-str",
                    ),
                },
            ),
            include_workload=_is_non_alternation_counted_repeat_workload,
            correctness_case_signature=_counted_repeat_correctness_case_signature,
            workload_signature=_counted_repeat_workload_signature,
            run_callback_result_parity=True,
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="ranged-repeat",
            manifest_paths=(benchmark_test_support.RANGED_REPEAT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
                benchmark_test_support.RANGED_REPEAT_MANIFEST_PATH,
                {
                    "module-compile-numbered-ranged-repeat-group-cold-str": (
                        "ranged-repeat-numbered-group-compile-metadata-str",
                    ),
                    "module-search-numbered-ranged-repeat-group-lower-bound-warm-str": (
                        "ranged-repeat-numbered-group-module-search-lower-bound-str",
                    ),
                    "pattern-fullmatch-numbered-ranged-repeat-group-upper-bound-purged-str": (
                        "ranged-repeat-numbered-group-pattern-fullmatch-upper-bound-str",
                    ),
                    "module-compile-named-ranged-repeat-group-warm-str": (
                        "ranged-repeat-named-group-compile-metadata-str",
                    ),
                    "module-search-named-ranged-repeat-group-upper-bound-warm-str": (
                        "ranged-repeat-named-group-module-search-upper-bound-str",
                    ),
                    "pattern-fullmatch-named-ranged-repeat-group-lower-bound-purged-str": (
                        "ranged-repeat-named-group-pattern-fullmatch-lower-bound-str",
                    ),
                    "module-search-numbered-ranged-repeat-group-wider-range-cold-gap": (
                        "broader-range-wider-ranged-repeat-numbered-group-module-search-upper-bound-str",
                    ),
                },
            ),
            include_workload=_is_non_alternation_counted_repeat_workload,
            correctness_case_signature=_counted_repeat_correctness_case_signature,
            workload_signature=_counted_repeat_workload_signature,
            run_callback_result_parity=True,
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="grouped-alternation",
            manifest_paths=(benchmark_test_support.GROUPED_ALTERNATION_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
                benchmark_test_support.GROUPED_ALTERNATION_MANIFEST_PATH,
                {
                    "module-compile-grouped-alternation-cold-str": (
                        "grouped-alternation-compile-metadata-str",
                    ),
                    "module-search-grouped-alternation-warm-str": (
                        "grouped-alternation-module-search-str",
                    ),
                    "pattern-fullmatch-grouped-alternation-purged-str": (
                        "grouped-alternation-pattern-fullmatch-str",
                    ),
                    "module-compile-named-grouped-alternation-warm-str": (
                        "named-grouped-alternation-compile-metadata-str",
                    ),
                    "module-search-named-grouped-alternation-warm-str": (
                        "named-grouped-alternation-module-search-str",
                    ),
                    "pattern-fullmatch-named-grouped-alternation-purged-str": (
                        "named-grouped-alternation-pattern-fullmatch-str",
                    ),
                    "module-sub-template-nested-grouped-alternation-warm-gap": (
                        "module-sub-template-nested-group-alternation-numbered-wrapper-str",
                    ),
                    "pattern-subn-template-named-nested-grouped-alternation-purged-gap": (
                        "pattern-subn-template-nested-group-alternation-named-wrapper-first-match-only-str",
                    ),
                },
            ),
            include_workload=lambda _: True,
            correctness_case_signature=_grouped_alternation_correctness_case_signature,
            workload_signature=_grouped_alternation_workload_signature,
            run_callback_result_parity=True,
            expected_legacy_workload_ids=frozenset(
                {
                    "module-sub-template-nested-grouped-alternation-warm-gap",
                    "pattern-subn-template-named-nested-grouped-alternation-purged-gap",
                }
            ),
            callback_anchor_workload_ids=frozenset(
                {
                    "module-sub-template-nested-grouped-alternation-warm-gap",
                    "pattern-subn-template-named-nested-grouped-alternation-purged-gap",
                }
            ),
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="grouped-alternation-replacement",
            manifest_paths=(benchmark_test_support.GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
                benchmark_test_support.GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,
                {
                    "module-sub-template-grouped-alternation-warm-str": (
                        "module-sub-template-grouped-alternation-str",
                    ),
                    "module-subn-template-grouped-alternation-warm-str": (
                        "module-subn-template-grouped-alternation-str",
                    ),
                    "pattern-sub-template-grouped-alternation-purged-str": (
                        "pattern-sub-template-grouped-alternation-str",
                    ),
                    "pattern-subn-template-grouped-alternation-purged-str": (
                        "pattern-subn-template-grouped-alternation-str",
                    ),
                    "module-sub-template-named-grouped-alternation-warm-str": (
                        "module-sub-template-named-grouped-alternation-str",
                    ),
                    "module-subn-template-named-grouped-alternation-warm-str": (
                        "module-subn-template-named-grouped-alternation-str",
                    ),
                    "pattern-sub-template-named-grouped-alternation-purged-str": (
                        "pattern-sub-template-named-grouped-alternation-str",
                    ),
                    "pattern-subn-template-named-grouped-alternation-purged-str": (
                        "pattern-subn-template-named-grouped-alternation-str",
                    ),
                    "module-sub-template-nested-grouped-alternation-cold-gap": (
                        "module-sub-template-nested-group-alternation-numbered-outer-str",
                    ),
                    "pattern-subn-template-named-nested-grouped-alternation-replacement-purged-gap": (
                        "pattern-subn-template-nested-group-alternation-named-outer-first-match-only-str",
                    ),
                },
            ),
            include_workload=lambda _: True,
            correctness_case_signature=(
                _grouped_alternation_replacement_correctness_case_signature
            ),
            workload_signature=_grouped_alternation_workload_signature,
            run_callback_result_parity=True,
            expected_legacy_workload_ids=frozenset(
                {
                    "module-sub-template-nested-grouped-alternation-cold-gap",
                    "pattern-subn-template-named-nested-grouped-alternation-replacement-purged-gap",
                }
            ),
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="nested-group-replacement",
            manifest_paths=(benchmark_test_support.NESTED_GROUP_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
                benchmark_test_support.NESTED_GROUP_REPLACEMENT_MANIFEST_PATH,
                {
                    "module-sub-template-nested-group-numbered-warm-str": (
                        "module-sub-template-nested-group-numbered-str",
                    ),
                    "module-subn-template-nested-group-numbered-warm-str": (
                        "module-subn-template-nested-group-numbered-str",
                    ),
                    "pattern-sub-template-nested-group-numbered-purged-str": (
                        "pattern-sub-template-nested-group-numbered-str",
                    ),
                    "pattern-subn-template-nested-group-numbered-purged-str": (
                        "pattern-subn-template-nested-group-numbered-str",
                    ),
                    "module-sub-template-nested-group-named-warm-str": (
                        "module-sub-template-nested-group-named-str",
                    ),
                    "module-subn-template-nested-group-named-warm-str": (
                        "module-subn-template-nested-group-named-str",
                    ),
                    "pattern-sub-template-nested-group-named-purged-str": (
                        "pattern-sub-template-nested-group-named-str",
                    ),
                    "pattern-subn-template-nested-group-named-purged-str": (
                        "pattern-subn-template-nested-group-named-str",
                    ),
                    "module-sub-template-numbered-quantified-nested-group-replacement-lower-bound-warm-str": (
                        "module-sub-template-quantified-nested-group-numbered-lower-bound-str",
                    ),
                    "module-subn-template-numbered-quantified-nested-group-replacement-first-match-only-warm-str": (
                        "module-subn-template-quantified-nested-group-numbered-first-match-only-str",
                    ),
                    "pattern-sub-template-named-quantified-nested-group-replacement-repeated-outer-purged-str": (
                        "pattern-sub-template-quantified-nested-group-named-repeated-outer-capture-str",
                    ),
                    "pattern-subn-template-named-quantified-nested-group-replacement-purged-gap": (
                        "pattern-subn-template-quantified-nested-group-named-first-match-only-str",
                    ),
                    "module-sub-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str": (
                        "module-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
                    ),
                    "module-subn-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str": (
                        "module-subn-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
                    ),
                    "pattern-sub-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-str": (
                        "pattern-sub-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-upper-bound-c-branch-str",
                    ),
                    "pattern-subn-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-str": (
                        "pattern-subn-template-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
                    ),
                    "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str": (
                        "module-sub-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
                    ),
                    "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str": (
                        "module-subn-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
                    ),
                    "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-lower-bound-c-branch-purged-str": (
                        "pattern-sub-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-lower-bound-c-branch-str",
                    ),
                    "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-str": (
                        "pattern-subn-template-nested-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
                    ),
                    "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-str": (
                        "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-lower-bound-b-branch-str",
                    ),
                    "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-str": (
                        "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-numbered-first-match-only-b-branch-str",
                    ),
                    "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-str": (
                        "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-lower-bound-c-branch-str",
                    ),
                    "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-str": (
                        "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-named-c-branch-first-match-only-str",
                    ),
                    "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-str": (
                        "module-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-lower-bound-b-branch-str",
                    ),
                    "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-str": (
                        "module-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-numbered-first-match-only-b-branch-str",
                    ),
                    "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-str": (
                        "pattern-sub-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-lower-bound-c-branch-str",
                    ),
                    "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-str": (
                        "pattern-subn-template-nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-named-c-branch-first-match-only-str",
                    ),
                },
            ),
            include_workload=lambda _: True,
            correctness_case_signature=(
                _grouped_alternation_replacement_correctness_case_signature
            ),
            workload_signature=_grouped_alternation_workload_signature,
            run_callback_result_parity=True,
            expected_special_unanchored_workload_ids=(
                "module-sub-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-bytes",
                "module-subn-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-bytes",
                "pattern-sub-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-bytes",
                "pattern-subn-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-bytes",
                "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-bytes",
                "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-bytes",
                "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-bytes",
                "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-bytes",
                "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-bytes",
                "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-bytes",
                "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-bytes",
                "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-bytes",
            ),
            run_special_unanchored_result_parity=True,
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="open-ended-grouped-alternation",
            manifest_paths=(benchmark_test_support.OPEN_ENDED_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
                benchmark_test_support.OPEN_ENDED_MANIFEST_PATH,
                {
                    "module-compile-numbered-open-ended-group-alternation-cold-str": (
                        "open-ended-quantified-group-alternation-numbered-compile-metadata-str",
                    ),
                    "module-search-numbered-open-ended-group-alternation-lower-bound-bc-warm-str": (
                        "open-ended-quantified-group-alternation-numbered-module-search-lower-bound-bc-str",
                    ),
                    "pattern-fullmatch-numbered-open-ended-group-alternation-third-repetition-mixed-purged-str": (
                        "open-ended-quantified-group-alternation-numbered-pattern-fullmatch-third-repetition-mixed-str",
                    ),
                    "module-compile-named-open-ended-group-alternation-warm-str": (
                        "open-ended-quantified-group-alternation-named-compile-metadata-str",
                    ),
                    "module-search-named-open-ended-group-alternation-lower-bound-de-warm-str": (
                        "open-ended-quantified-group-alternation-named-module-search-lower-bound-de-str",
                    ),
                    "pattern-fullmatch-named-open-ended-group-alternation-fourth-repetition-de-purged-str": (
                        "open-ended-quantified-group-alternation-named-pattern-fullmatch-fourth-repetition-de-str",
                    ),
                    "module-compile-numbered-open-ended-group-alternation-cold-bytes": (
                        "open-ended-quantified-group-alternation-numbered-compile-metadata-bytes",
                    ),
                    "module-compile-named-open-ended-group-alternation-warm-bytes": (
                        "open-ended-quantified-group-alternation-named-compile-metadata-bytes",
                    ),
                    "module-compile-numbered-open-ended-group-conditional-cold-str": (
                        "open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-str",
                    ),
                    "module-compile-numbered-open-ended-group-broader-range-cold-str": (
                        "broader-range-open-ended-quantified-group-alternation-numbered-compile-metadata-str",
                    ),
                    "module-search-numbered-open-ended-group-broader-range-cold-gap": (
                        "broader-range-open-ended-quantified-group-alternation-numbered-module-search-lower-bound-bc-str",
                    ),
                    "pattern-fullmatch-numbered-open-ended-group-broader-range-third-repetition-mixed-purged-str": (
                        "broader-range-open-ended-quantified-group-alternation-numbered-pattern-fullmatch-third-repetition-mixed-str",
                    ),
                    "module-compile-named-open-ended-group-broader-range-warm-str": (
                        "broader-range-open-ended-quantified-group-alternation-named-compile-metadata-str",
                    ),
                    "module-search-named-open-ended-group-broader-range-lower-bound-de-warm-str": (
                        "broader-range-open-ended-quantified-group-alternation-named-module-search-lower-bound-de-str",
                    ),
                    "pattern-fullmatch-named-open-ended-group-broader-range-third-repetition-de-purged-str": (
                        "broader-range-open-ended-quantified-group-alternation-named-pattern-fullmatch-fourth-repetition-de-str",
                    ),
                    "module-compile-numbered-open-ended-group-broader-range-cold-bytes": (
                        "broader-range-open-ended-quantified-group-alternation-numbered-compile-metadata-bytes",
                    ),
                    "module-compile-named-open-ended-group-broader-range-warm-bytes": (
                        "broader-range-open-ended-quantified-group-alternation-named-compile-metadata-bytes",
                    ),
                    "module-compile-numbered-open-ended-group-broader-range-conditional-cold-str": (
                        "broader-range-open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-str",
                    ),
                    "module-search-numbered-open-ended-group-broader-range-conditional-warm-gap": (
                        "broader-range-open-ended-quantified-group-alternation-conditional-numbered-module-search-lower-bound-bc-workflow-str",
                    ),
                    "pattern-fullmatch-numbered-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-str": (
                        "broader-range-open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-third-repetition-mixed-workflow-str",
                    ),
                    "module-compile-named-open-ended-group-broader-range-conditional-warm-str": (
                        "broader-range-open-ended-quantified-group-alternation-conditional-named-compile-metadata-str",
                    ),
                    "module-search-named-open-ended-group-broader-range-conditional-fourth-repetition-de-warm-str": (
                        "broader-range-open-ended-quantified-group-alternation-conditional-named-module-search-fourth-repetition-de-workflow-str",
                    ),
                    "pattern-fullmatch-named-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-str": (
                        "broader-range-open-ended-quantified-group-alternation-conditional-named-pattern-fullmatch-third-repetition-mixed-workflow-str",
                    ),
                    "module-compile-numbered-open-ended-group-broader-range-conditional-cold-bytes": (
                        "broader-range-open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-bytes",
                    ),
                    "module-compile-named-open-ended-group-broader-range-conditional-warm-bytes": (
                        "broader-range-open-ended-quantified-group-alternation-conditional-named-compile-metadata-bytes",
                    ),
                    "module-compile-numbered-open-ended-group-broader-range-backtracking-heavy-cold-str": (
                        "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-str",
                    ),
                    "module-search-numbered-open-ended-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-str": (
                        "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-short-branch-str",
                    ),
                    "pattern-fullmatch-numbered-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-str": (
                        "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-long-then-short-str",
                    ),
                    "module-compile-named-open-ended-group-broader-range-backtracking-heavy-warm-str": (
                        "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-str",
                    ),
                    "module-search-named-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-warm-str": (
                        "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-second-repetition-long-then-short-str",
                    ),
                    "module-compile-numbered-open-ended-group-broader-range-backtracking-heavy-cold-bytes": (
                        "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-bytes",
                    ),
                    "module-compile-named-open-ended-group-broader-range-backtracking-heavy-warm-bytes": (
                        "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-bytes",
                    ),
                    "pattern-fullmatch-numbered-open-ended-group-conditional-third-repetition-mixed-purged-str": (
                        "open-ended-quantified-group-alternation-conditional-numbered-pattern-fullmatch-third-repetition-mixed-workflow-str",
                    ),
                    "module-compile-named-open-ended-group-conditional-warm-str": (
                        "open-ended-quantified-group-alternation-conditional-named-compile-metadata-str",
                    ),
                    "module-search-named-open-ended-group-conditional-fourth-repetition-de-warm-str": (
                        "open-ended-quantified-group-alternation-conditional-named-module-search-fourth-repetition-de-workflow-str",
                    ),
                    "pattern-fullmatch-named-open-ended-group-conditional-third-repetition-mixed-purged-str": (
                        "open-ended-quantified-group-alternation-conditional-named-pattern-fullmatch-third-repetition-mixed-workflow-str",
                    ),
                    "module-compile-numbered-open-ended-group-conditional-cold-bytes": (
                        "open-ended-quantified-group-alternation-conditional-numbered-compile-metadata-bytes",
                    ),
                    "module-compile-named-open-ended-group-conditional-warm-bytes": (
                        "open-ended-quantified-group-alternation-conditional-named-compile-metadata-bytes",
                    ),
                    "module-compile-numbered-open-ended-group-backtracking-heavy-cold-str": (
                        "open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-str",
                    ),
                    "module-search-numbered-open-ended-group-backtracking-heavy-lower-bound-b-branch-warm-str": (
                        "open-ended-quantified-group-alternation-backtracking-heavy-numbered-module-search-lower-bound-short-branch-str",
                    ),
                    "pattern-fullmatch-numbered-open-ended-group-backtracking-heavy-second-repetition-b-then-bc-purged-str": (
                        "open-ended-quantified-group-alternation-backtracking-heavy-numbered-pattern-fullmatch-second-repetition-short-then-long-str",
                    ),
                    "module-compile-named-open-ended-group-backtracking-heavy-warm-str": (
                        "open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-str",
                    ),
                    "module-search-named-open-ended-group-backtracking-heavy-third-repetition-mixed-warm-str": (
                        "open-ended-quantified-group-alternation-backtracking-heavy-named-module-search-third-repetition-mixed-str",
                    ),
                    "pattern-fullmatch-named-open-ended-group-backtracking-heavy-purged-gap": (
                        "open-ended-quantified-group-alternation-backtracking-heavy-named-pattern-fullmatch-fourth-repetition-short-only-str",
                    ),
                    "module-compile-numbered-open-ended-group-backtracking-heavy-cold-bytes": (
                        "open-ended-quantified-group-alternation-backtracking-heavy-numbered-compile-metadata-bytes",
                    ),
                    "module-compile-named-open-ended-group-backtracking-heavy-warm-bytes": (
                        "open-ended-quantified-group-alternation-backtracking-heavy-named-compile-metadata-bytes",
                    ),
                },
            ),
            include_workload=lambda _: True,
            correctness_case_signature=_counted_repeat_correctness_case_signature,
            workload_signature=_counted_repeat_workload_signature,
            run_callback_result_parity=True,
            expected_special_unanchored_workload_ids=(
                "module-search-numbered-open-ended-group-alternation-lower-bound-bc-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-alternation-third-repetition-mixed-purged-bytes",
                "module-search-named-open-ended-group-alternation-lower-bound-de-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-alternation-fourth-repetition-de-purged-bytes",
                "module-search-numbered-open-ended-group-broader-range-lower-bound-bc-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-broader-range-third-repetition-mixed-purged-bytes",
                "module-search-named-open-ended-group-broader-range-lower-bound-de-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-broader-range-third-repetition-de-purged-bytes",
                "module-search-numbered-open-ended-group-broader-range-conditional-second-repetition-bc-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-bytes",
                "module-search-named-open-ended-group-broader-range-conditional-fourth-repetition-de-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-bytes",
                "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-str",
                "module-search-numbered-open-ended-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-bytes",
                "module-search-named-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-bytes",
                "module-search-numbered-open-ended-group-conditional-warm-gap",
                "module-search-numbered-open-ended-group-conditional-second-repetition-bc-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-conditional-third-repetition-mixed-purged-bytes",
                "module-search-named-open-ended-group-conditional-fourth-repetition-de-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-conditional-third-repetition-mixed-purged-bytes",
                "module-search-numbered-open-ended-group-backtracking-heavy-lower-bound-b-branch-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-backtracking-heavy-second-repetition-b-then-bc-purged-bytes",
                "module-search-named-open-ended-group-backtracking-heavy-third-repetition-mixed-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-backtracking-heavy-purged-bytes",
            ),
            direct_parity_supplemental_cases=(
                *OPEN_ENDED_ALTERNATION_BYTES_CASES,
                *OPEN_ENDED_CONDITIONAL_BYTES_CASES,
                *OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
                *BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES,
                *BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
                *BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
            ),
            run_special_unanchored_result_parity=True,
        ),
    )




@dataclass(frozen=True, slots=True)
class SourceTreeBenchmarkCommonCase:
    expected_adapter: str
    expected_phase: str
    expected_runner_version: str
    expected_summary: dict[str, int]
    manifests: list[BenchmarkManifest]
    selection_mode: str

    def manifest_for_id(self, manifest_id: str) -> BenchmarkManifest:
        for manifest in self.manifests:
            if manifest.manifest_id == manifest_id:
                return manifest
        raise AssertionError(f"unknown source-tree benchmark manifest {manifest_id!r}")

    def selected_workload_ids_for_manifest(self, manifest_id: str) -> tuple[str, ...]:
        return _selected_source_tree_manifest_workload_ids(
            self.manifest_for_id(manifest_id),
            selection_mode=self.selection_mode,
        )


@dataclass(frozen=True, slots=True)
class SourceTreeManifestExpectation:
    known_gap_count: int
    representative_measured_workload_ids: tuple[str, ...] = ()
    representative_known_gap_workload_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class SourceTreeDeferredExpectation:
    area: str
    follow_up: str


@dataclass(frozen=True, slots=True)
class SourceTreeScorecardCase(SourceTreeBenchmarkCommonCase):
    case_id: str
    manifest_expectations: dict[str, SourceTreeManifestExpectation]
    representative_measured_workload_ids: tuple[str, ...]
    representative_known_gap_workload_ids: tuple[str, ...]
    expected_first_deferred: SourceTreeDeferredExpectation | None = None
    expected_workload_order: tuple[str, ...] | None = None


@dataclass(frozen=True, slots=True)
class _SourceTreeScorecardDefinition:
    manifest_ids: tuple[str, ...]
    selection_mode: str = "full"
    representative_measured_workload_ids: tuple[str, ...] = ()
    representative_known_gap_workload_ids: tuple[str, ...] = ()
    expected_first_deferred: SourceTreeDeferredExpectation | None = None
    expected_workload_order: tuple[str, ...] | None = None


@dataclass(frozen=True, slots=True)
class SourceTreeCombinedCase(SourceTreeBenchmarkCommonCase):
    manifest_expectation: SourceTreeManifestExpectation
    manifest_id: str
    target_manifest: BenchmarkManifest


@dataclass(frozen=True, slots=True)
class SourceTreeCombinedPatternGroupExpectation:
    slice_id: str
    patterns: tuple[str, ...]
    minimum_rows: int
    required_operations: tuple[str, ...]
    required_categories: tuple[str, ...]
    search_haystacks: tuple[str, ...]
    search_haystack_substrings: tuple[str, ...]
    pattern_haystacks: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SourceTreeCombinedManifestShapeExpectation:
    representative_measured_workload_ids: tuple[str, ...]
    pattern_groups: tuple[SourceTreeCombinedPatternGroupExpectation, ...] = ()


@dataclass(frozen=True, slots=True)
class SourceTreeCombinedFullyMeasuredManifestExpectation:
    coverage_group: str
    representative_measured_workload_ids: tuple[str, ...]
    expected_measured_workload_count: int
    expected_total_workload_count: int | None = None


@dataclass(frozen=True, slots=True)
class SourceTreeCombinedManifestExpectationDefinition:
    exclude_from_combined_targets: bool = False
    promote_zero_gap_representatives: bool = False
    known_gap_workload_ids: tuple[str, ...] | None = None
    representative_measured_workload_ids: tuple[str, ...] | None = None
    representative_known_gap_workload_ids: tuple[str, ...] | None = None
    fully_measured_expectation: SourceTreeCombinedFullyMeasuredManifestExpectation | None = None
    shape_expectation: SourceTreeCombinedManifestShapeExpectation | None = None
    zero_gap_bytes_representative_subsets: tuple[tuple[str, ...], ...] = ()


def _text_model_agnostic_callable_match_group_signature(
    replacement: object,
) -> tuple[object, ...] | None:
    signature = callable_match_group_signature(replacement)
    if signature is None:
        return None
    return tuple(
        value.decode("utf-8") if isinstance(value, bytes) else value
        for value in signature
    )


@dataclass(frozen=True, slots=True)
class SourceTreeCombinedSliceExpectation:
    manifest_id: str
    slice_id: str
    required_syntax_features: tuple[str, ...] = ()
    excluded_syntax_features: tuple[str, ...] = ()
    required_categories: tuple[str, ...] = ()
    excluded_categories: tuple[str, ...] = ()
    required_id_suffix: str | None = None
    expected_workload_ids: tuple[str, ...] = ()
    expected_patterns: frozenset[str] = frozenset()
    expected_operations: frozenset[str] = frozenset()
    expected_haystacks: frozenset[str] = frozenset()
    required_row_categories: tuple[str, ...] = ()
    expected_status: str = "measured"


SOURCE_TREE_SCORECARD_EXPECTATIONS = {
    "compile-matrix": _SourceTreeScorecardDefinition(
        manifest_ids=("compile-matrix",),
        expected_first_deferred=SourceTreeDeferredExpectation(
            area="module-boundary",
            follow_up="RBR-0015",
        ),
        representative_measured_workload_ids=(
            "compile-inline-locale-bytes-warm",
            "compile-lookbehind-cold",
            "compile-atomic-group-purged",
            "compile-parser-stress-cold",
        ),
    ),
    "post-parser-workflows": _SourceTreeScorecardDefinition(
        manifest_ids=(
            "module-boundary",
            "collection-replacement-boundary",
            "literal-flag-boundary",
        ),
        representative_measured_workload_ids=(
            "module-compile-literal-cold",
            "module-compile-literal-warm",
            "module-compile-literal-purged",
            "module-search-grouped-literal-cold-hit",
            "module-search-flags-keyword-warm-str",
            "module-search-duplicate-flags-keyword-warm-str",
            "module-match-flags-keyword-purged-bytes",
            "module-fullmatch-flags-keyword-warm-str",
            "module-fullmatch-unexpected-keyword-purged-str",
            "module-findall-single-dot-warm-str",
            "module-sub-template-warm-str",
            "module-sub-callable-grouped-warm-str",
            "pattern-subn-grouped-template-warm-str",
            "pattern-subn-callable-named-grouped-warm-str",
            "module-search-inline-flag-warm-str-hit",
            "pattern-search-inline-flag-warm-str-hit",
            "module-search-locale-purged-bytes-hit",
            "pattern-search-locale-purged-bytes-hit",
            "module-search-ignorecase-ascii-cold-gap",
            "pattern-search-ignorecase-ascii-warm-gap",
        ),
        representative_known_gap_workload_ids=(),
    ),
    "numbered-backreference-boundary": _SourceTreeScorecardDefinition(
        manifest_ids=("numbered-backreference-boundary",),
    ),
    "nested-group-boundary": _SourceTreeScorecardDefinition(
        manifest_ids=("nested-group-boundary",),
    ),
    "nested-group-replacement-boundary": _SourceTreeScorecardDefinition(
        manifest_ids=("nested-group-replacement-boundary",),
    ),
    "nested-group-callable-replacement-boundary": _SourceTreeScorecardDefinition(
        manifest_ids=("nested-group-callable-replacement-boundary",),
    ),
    "branch-local-backreference-boundary": _SourceTreeScorecardDefinition(
        manifest_ids=("branch-local-backreference-boundary",),
    ),
    "conditional-group-exists-boundary": _SourceTreeScorecardDefinition(
        manifest_ids=("conditional-group-exists-boundary",),
    ),
    "regression-pack-full": _SourceTreeScorecardDefinition(
        manifest_ids=(
            "compile-matrix",
            "module-boundary",
            "regression-matrix",
        ),
        representative_measured_workload_ids=(
            "compile-inline-locale-bytes-warm",
            "module-compile-literal-cold",
            "module-compile-literal-warm",
            "module-compile-literal-purged",
            "regression-import-cold",
            "regression-parser-bytes-backreference-purged",
            "regression-module-compile-multiline-purged",
            "regression-module-compile-multiline-purged-bytes",
            "regression-module-compile-verbose-purged-bytes",
            "regression-module-search-bytes-cold-miss",
        ),
        representative_known_gap_workload_ids=(),
    ),
    "regression-pack-smoke": _SourceTreeScorecardDefinition(
        manifest_ids=("regression-matrix",),
        selection_mode="smoke",
        expected_workload_order=(
            "regression-import-cold",
            "regression-parser-atomic-lookbehind-cold",
        ),
        representative_measured_workload_ids=(
            "regression-import-cold",
            "regression-parser-atomic-lookbehind-cold",
        ),
        representative_known_gap_workload_ids=(),
    ),
}

def _combined_manifest_definition(
    *,
    exclude_from_combined_targets: bool = False,
    promote_zero_gap_representatives: bool = False,
    known_gap_workload_ids: tuple[str, ...] | None = None,
    representative_measured_workload_ids: tuple[str, ...] | None = None,
    representative_known_gap_workload_ids: tuple[str, ...] | None = None,
    fully_measured_expectation: SourceTreeCombinedFullyMeasuredManifestExpectation
    | None = None,
    shape_expectation: SourceTreeCombinedManifestShapeExpectation | None = None,
    zero_gap_bytes_representative_subsets: tuple[tuple[str, ...], ...] = (),
) -> SourceTreeCombinedManifestExpectationDefinition:
    if fully_measured_expectation is not None:
        if representative_measured_workload_ids is None:
            representative_measured_workload_ids = (
                fully_measured_expectation.representative_measured_workload_ids
            )
        elif (
            representative_measured_workload_ids
            != fully_measured_expectation.representative_measured_workload_ids
        ):
            raise AssertionError(
                "fully measured manifest definitions must keep their "
                "representative rows on the shared definition-owned contract"
            )
    return SourceTreeCombinedManifestExpectationDefinition(
        exclude_from_combined_targets=exclude_from_combined_targets,
        promote_zero_gap_representatives=promote_zero_gap_representatives,
        known_gap_workload_ids=known_gap_workload_ids,
        representative_measured_workload_ids=representative_measured_workload_ids,
        representative_known_gap_workload_ids=representative_known_gap_workload_ids,
        fully_measured_expectation=fully_measured_expectation,
        shape_expectation=shape_expectation,
        zero_gap_bytes_representative_subsets=tuple(
            tuple(str(workload_id) for workload_id in workload_ids)
            for workload_ids in zero_gap_bytes_representative_subsets
        ),
    )


def _combined_fully_measured_manifest_expectation(
    *,
    coverage_group: str,
    representative_measured_workload_ids: tuple[str, ...],
    expected_measured_workload_count: int,
    expected_total_workload_count: int | None = None,
) -> SourceTreeCombinedFullyMeasuredManifestExpectation:
    return SourceTreeCombinedFullyMeasuredManifestExpectation(
        coverage_group=coverage_group,
        representative_measured_workload_ids=tuple(
            str(workload_id) for workload_id in representative_measured_workload_ids
        ),
        expected_measured_workload_count=expected_measured_workload_count,
        expected_total_workload_count=expected_total_workload_count,
    )


def _combined_manifest_shape(
    *,
    representative_measured_workload_ids: tuple[str, ...],
    pattern_groups: tuple[SourceTreeCombinedPatternGroupExpectation, ...] = (),
) -> SourceTreeCombinedManifestShapeExpectation:
    return SourceTreeCombinedManifestShapeExpectation(
        representative_measured_workload_ids=representative_measured_workload_ids,
        pattern_groups=pattern_groups,
    )


def _combined_pattern_group(
    *,
    slice_id: str,
    patterns: tuple[str, ...],
    minimum_rows: int,
    required_operations: tuple[str, ...],
    required_categories: tuple[str, ...],
    search_haystacks: tuple[str, ...] = (),
    search_haystack_substrings: tuple[str, ...] = (),
    pattern_haystacks: tuple[str, ...] = (),
) -> SourceTreeCombinedPatternGroupExpectation:
    return SourceTreeCombinedPatternGroupExpectation(
        slice_id=slice_id,
        patterns=patterns,
        minimum_rows=minimum_rows,
        required_operations=required_operations,
        required_categories=required_categories,
        search_haystacks=search_haystacks,
        search_haystack_substrings=search_haystack_substrings,
        pattern_haystacks=pattern_haystacks,
    )


@cache
def _published_benchmark_manifest_ids() -> frozenset[str]:
    return frozenset(
        manifest.manifest_id for manifest in published_benchmark_manifests()
    )


_SOURCE_TREE_DEFAULT_COMBINED_MANIFEST_EXPECTATION = _combined_manifest_definition()


class _SourceTreeCombinedManifestExpectations(
    dict[str, SourceTreeCombinedManifestExpectationDefinition]
):
    def _supports_fallback(self, manifest_id: object) -> bool:
        return (
            isinstance(manifest_id, str)
            and manifest_id in _published_benchmark_manifest_ids()
        )

    def __missing__(
        self,
        manifest_id: str,
    ) -> SourceTreeCombinedManifestExpectationDefinition:
        if self._supports_fallback(manifest_id):
            return _SOURCE_TREE_DEFAULT_COMBINED_MANIFEST_EXPECTATION
        raise KeyError(manifest_id)

    def get(
        self,
        manifest_id: str,
        default: SourceTreeCombinedManifestExpectationDefinition | None = None,
    ) -> SourceTreeCombinedManifestExpectationDefinition | None:
        if self._supports_fallback(manifest_id):
            return self[manifest_id]
        return default

    def __contains__(self, manifest_id: object) -> bool:
        return super().__contains__(manifest_id) or self._supports_fallback(
            manifest_id
        )


SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS = _SourceTreeCombinedManifestExpectations({
    "compile-matrix": _combined_manifest_definition(
        exclude_from_combined_targets=True,
    ),
    "module-boundary": _combined_manifest_definition(
        representative_measured_workload_ids=(
            "module-compile-literal-cold",
            "module-compile-literal-warm",
            "module-compile-literal-purged",
            "import-module-cold",
            "module-search-grouped-literal-cold-hit",
            "module-search-literal-warm-hit",
            "module-search-flags-keyword-warm-str",
            "module-search-duplicate-flags-keyword-warm-str",
            "module-match-flags-keyword-purged-bytes",
            "module-fullmatch-flags-keyword-warm-str",
            "module-fullmatch-unexpected-keyword-purged-str",
            "module-search-bytes-cold-miss",
        ),
    ),
    "pattern-boundary": _combined_manifest_definition(
        shape_expectation=_combined_manifest_shape(
            representative_measured_workload_ids=(
                "pattern-search-literal-warm-hit",
                "pattern-fullmatch-bytes-purged-hit",
            ),
        ),
    ),
    "grouped-named-boundary": _combined_manifest_definition(
        promote_zero_gap_representatives=True,
        representative_measured_workload_ids=(
            "module-search-grouped-segment-cold-gap",
            "pattern-search-grouped-segment-warm-gap",
        ),
    ),
    "numbered-backreference-boundary": _combined_manifest_definition(
        promote_zero_gap_representatives=True,
        representative_measured_workload_ids=(
            "module-search-numbered-backreference-segment-cold-gap",
            "pattern-search-numbered-backreference-prefix-purged-gap",
        ),
        representative_known_gap_workload_ids=(),
    ),
    "grouped-alternation-boundary": _combined_manifest_definition(
        representative_measured_workload_ids=(
            "module-sub-template-nested-grouped-alternation-warm-gap",
            "pattern-subn-template-named-nested-grouped-alternation-purged-gap",
        ),
        representative_known_gap_workload_ids=(),
    ),
    "grouped-alternation-replacement-boundary": _combined_manifest_definition(
        representative_measured_workload_ids=(
            "module-sub-template-nested-grouped-alternation-cold-gap",
            "pattern-subn-template-named-nested-grouped-alternation-replacement-purged-gap",
        ),
        representative_known_gap_workload_ids=(),
    ),
    "nested-group-boundary": _combined_manifest_definition(
        promote_zero_gap_representatives=True,
        representative_measured_workload_ids=(
            "module-search-triple-nested-group-cold-gap",
            "pattern-fullmatch-named-quantified-nested-group-purged-gap",
        ),
        representative_known_gap_workload_ids=(),
    ),
    "branch-local-backreference-boundary": _combined_manifest_definition(
        representative_measured_workload_ids=(
            "module-compile-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-cold-str",
            "module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-str",
            "pattern-fullmatch-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-mixed-branches-purged-str",
            "module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-warm-str",
            "module-search-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-warm-str",
            "pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-purged-str",
            "module-compile-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-cold-bytes",
            "module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-mixed-branches-purged-bytes",
            "module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-warm-bytes",
            "module-search-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-warm-bytes",
            "pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-purged-bytes",
        ),
        zero_gap_bytes_representative_subsets=(
            (
                "module-compile-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-cold-bytes",
                "module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-mixed-branches-purged-bytes",
                "module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-warm-bytes",
                "module-search-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-warm-bytes",
                "pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-purged-bytes",
            ),
        ),
    ),
    "optional-group-boundary": _combined_manifest_definition(
        promote_zero_gap_representatives=True,
        representative_measured_workload_ids=(
            "module-search-numbered-optional-group-conditional-cold-gap",
        ),
        representative_known_gap_workload_ids=(),
    ),
    "exact-repeat-quantified-group-boundary": _combined_manifest_definition(
        fully_measured_expectation=_combined_fully_measured_manifest_expectation(
            coverage_group="counted-repeat",
            representative_measured_workload_ids=(
                "module-search-numbered-broader-ranged-repeat-group-cold-gap",
            ),
            expected_measured_workload_count=13,
        ),
        representative_known_gap_workload_ids=(),
    ),
    "ranged-repeat-quantified-group-boundary": _combined_manifest_definition(
        fully_measured_expectation=_combined_fully_measured_manifest_expectation(
            coverage_group="counted-repeat",
            representative_measured_workload_ids=(
                "module-search-numbered-ranged-repeat-group-wider-range-cold-gap",
            ),
            expected_measured_workload_count=8,
        ),
        representative_known_gap_workload_ids=(),
    ),
    "wider-ranged-repeat-quantified-group-boundary": _combined_manifest_definition(
        representative_measured_workload_ids=(
            "module-search-numbered-wider-ranged-repeat-group-broader-range-cold-gap",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-third-repetition-mixed-purged-str",
            "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-upper-bound-mixed-purged-str",
            "module-compile-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-cold-bytes",
            "module-search-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-second-repetition-b-then-bc-purged-bytes",
            "module-compile-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-warm-bytes",
            "module-search-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-lower-bound-bc-branch-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-fourth-repetition-mixed-purged-bytes",
            "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-absent-warm-str",
            "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-lower-bound-bc-warm-str",
            "module-search-named-wider-ranged-repeat-group-nested-broader-range-conditional-lower-bound-de-warm-str",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-mixed-purged-str",
            "pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-conditional-upper-bound-all-de-purged-str",
            "module-compile-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-cold-bytes",
            "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-absent-warm-bytes",
            "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-lower-bound-bc-warm-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-mixed-purged-bytes",
            "module-compile-named-wider-ranged-repeat-group-nested-broader-range-conditional-warm-bytes",
            "module-search-named-wider-ranged-repeat-group-nested-broader-range-conditional-lower-bound-de-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-conditional-upper-bound-all-de-purged-bytes",
            "module-compile-numbered-wider-ranged-repeat-group-nested-broader-range-cold-bytes",
            "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-lower-bound-bc-warm-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-third-repetition-mixed-purged-bytes",
            "module-compile-named-wider-ranged-repeat-group-nested-broader-range-warm-bytes",
            "module-search-named-wider-ranged-repeat-group-nested-broader-range-lower-bound-de-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-upper-bound-all-de-purged-bytes",
            "module-compile-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-cold-bytes",
            "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-second-repetition-b-then-bc-purged-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-fourth-repetition-mixed-purged-bytes",
            "module-compile-named-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-warm-bytes",
            "module-search-named-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-lower-bound-bc-branch-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-bytes",
            "module-search-numbered-wider-ranged-repeat-group-broader-range-conditional-absent-warm-str",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-conditional-lower-bound-bc-purged-str",
            "module-search-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-warm-str",
            "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-purged-str",
            "module-compile-numbered-wider-ranged-repeat-group-broader-range-conditional-cold-bytes",
            "module-search-numbered-wider-ranged-repeat-group-broader-range-conditional-absent-warm-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-conditional-lower-bound-bc-purged-bytes",
            "module-compile-named-wider-ranged-repeat-group-broader-range-conditional-warm-bytes",
            "module-search-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-purged-bytes",
            "module-search-numbered-wider-ranged-repeat-group-open-ended-lower-bound-bc-warm-str",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-open-ended-purged-gap",
            "pattern-fullmatch-named-wider-ranged-repeat-group-open-ended-fourth-repetition-de-purged-str",
            "module-compile-numbered-wider-ranged-repeat-group-open-ended-cold-bytes",
            "module-search-numbered-wider-ranged-repeat-group-open-ended-lower-bound-bc-warm-bytes",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-open-ended-purged-bytes",
            "module-compile-named-wider-ranged-repeat-group-open-ended-warm-bytes",
            "module-search-named-wider-ranged-repeat-group-open-ended-lower-bound-de-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-group-open-ended-fourth-repetition-de-purged-bytes",
        ),
        zero_gap_bytes_representative_subsets=(
            (
                "module-compile-numbered-wider-ranged-repeat-group-broader-range-conditional-cold-bytes",
                "module-search-numbered-wider-ranged-repeat-group-broader-range-conditional-absent-warm-bytes",
                "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-conditional-lower-bound-bc-purged-bytes",
                "module-compile-named-wider-ranged-repeat-group-broader-range-conditional-warm-bytes",
                "module-search-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-warm-bytes",
                "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-purged-bytes",
            ),
            (
                "module-compile-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-cold-bytes",
                "module-search-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes",
                "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-second-repetition-b-then-bc-purged-bytes",
                "module-compile-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-warm-bytes",
                "module-search-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-lower-bound-bc-branch-warm-bytes",
                "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-fourth-repetition-mixed-purged-bytes",
            ),
            (
                "module-compile-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-cold-bytes",
                "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes",
                "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-second-repetition-b-then-bc-purged-bytes",
                "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-fourth-repetition-mixed-purged-bytes",
                "module-compile-named-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-warm-bytes",
                "module-search-named-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-lower-bound-bc-branch-warm-bytes",
                "pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-bytes",
            ),
            (
                "module-compile-numbered-wider-ranged-repeat-group-nested-broader-range-cold-bytes",
                "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-lower-bound-bc-warm-bytes",
                "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-third-repetition-mixed-purged-bytes",
                "module-compile-named-wider-ranged-repeat-group-nested-broader-range-warm-bytes",
                "module-search-named-wider-ranged-repeat-group-nested-broader-range-lower-bound-de-warm-bytes",
                "pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-upper-bound-all-de-purged-bytes",
            ),
            (
                "module-compile-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-cold-bytes",
                "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-absent-warm-bytes",
                "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-lower-bound-bc-warm-bytes",
                "pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-mixed-purged-bytes",
                "module-compile-named-wider-ranged-repeat-group-nested-broader-range-conditional-warm-bytes",
                "module-search-named-wider-ranged-repeat-group-nested-broader-range-conditional-lower-bound-de-warm-bytes",
                "pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-conditional-upper-bound-all-de-purged-bytes",
            ),
            (
                "module-compile-numbered-wider-ranged-repeat-group-open-ended-cold-bytes",
                "module-search-numbered-wider-ranged-repeat-group-open-ended-lower-bound-bc-warm-bytes",
                "pattern-fullmatch-numbered-wider-ranged-repeat-group-open-ended-purged-bytes",
                "module-compile-named-wider-ranged-repeat-group-open-ended-warm-bytes",
                "module-search-named-wider-ranged-repeat-group-open-ended-lower-bound-de-warm-bytes",
                "pattern-fullmatch-named-wider-ranged-repeat-group-open-ended-fourth-repetition-de-purged-bytes",
            ),
        ),
        shape_expectation=_combined_manifest_shape(
            representative_measured_workload_ids=(
                "module-search-numbered-wider-ranged-repeat-group-broader-range-cold-gap",
                "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-upper-bound-mixed-purged-str",
                "pattern-fullmatch-numbered-wider-ranged-repeat-group-open-ended-purged-gap",
                "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-absent-warm-str",
                "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-fourth-repetition-mixed-purged-str",
            ),
            pattern_groups=(
                _combined_pattern_group(
                    slice_id="broader-range-grouped-backtracking-heavy",
                    patterns=(
                        "a((bc|b)c){1,4}d",
                        "a(?P<word>(bc|b)c){1,4}d",
                    ),
                    minimum_rows=12,
                    required_operations=(
                        "module.compile",
                        "module.search",
                        "pattern.fullmatch",
                    ),
                    required_categories=(
                        "grouped",
                        "alternation",
                        "backtracking-heavy",
                        "ranged-repeat",
                        "broader-range",
                        "counted-repeat",
                    ),
                    search_haystacks=(
                        "zzabcdzz",
                        "zzabccdzz",
                    ),
                    pattern_haystacks=(
                        "abcbccd",
                        "abcbccbccbcd",
                    ),
                ),
                _combined_pattern_group(
                    slice_id="nested-broader-range-grouped-alternation",
                    patterns=(
                        "a((bc|de){1,4})d",
                        "a(?P<outer>(bc|de){1,4})d",
                    ),
                    minimum_rows=12,
                    required_operations=(
                        "module.compile",
                        "module.search",
                        "pattern.fullmatch",
                    ),
                    required_categories=(
                        "nested-group",
                        "alternation",
                        "ranged-repeat",
                        "broader-range",
                        "counted-repeat",
                    ),
                    search_haystack_substrings=(
                        "abcd",
                        "aded",
                    ),
                    pattern_haystacks=(
                        "abcbcded",
                        "adedededed",
                    ),
                ),
                _combined_pattern_group(
                    slice_id="nested-broader-range-grouped-conditional",
                    patterns=(
                        "a(((bc|de){1,4})d)?(?(1)e|f)",
                        "a(?P<outer>((bc|de){1,4})d)?(?(outer)e|f)",
                    ),
                    minimum_rows=14,
                    required_operations=(
                        "module.compile",
                        "module.search",
                        "pattern.fullmatch",
                    ),
                    required_categories=(
                        "nested-group",
                        "alternation",
                        "conditional",
                        "optional-group",
                        "ranged-repeat",
                        "broader-range",
                        "counted-repeat",
                    ),
                    search_haystacks=(
                        "zzafzz",
                        "zzabcdezz",
                        "zzadedezz",
                    ),
                    pattern_haystacks=(
                        "abcbcdede",
                        "adedededede",
                    ),
                ),
                _combined_pattern_group(
                    slice_id="nested-broader-range-grouped-backtracking-heavy",
                    patterns=(
                        "a(((bc|b)c){1,4})d",
                        "a(?P<outer>((bc|b)c){1,4})d",
                    ),
                    minimum_rows=14,
                    required_operations=(
                        "module.compile",
                        "module.search",
                        "pattern.fullmatch",
                    ),
                    required_categories=(
                        "grouped",
                        "nested-group",
                        "alternation",
                        "backtracking-heavy",
                        "ranged-repeat",
                        "broader-range",
                        "counted-repeat",
                    ),
                    search_haystacks=(
                        "zzabcdzz",
                        "zzabccdzz",
                    ),
                    pattern_haystacks=(
                        "abcbccd",
                        "abccbcd",
                        "abcbccbccbcd",
                    ),
                ),
            ),
        ),
    ),
    "open-ended-quantified-group-boundary": _combined_manifest_definition(
        representative_measured_workload_ids=(
            "module-compile-numbered-open-ended-group-alternation-cold-bytes",
            "module-search-numbered-open-ended-group-alternation-lower-bound-bc-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-alternation-third-repetition-mixed-purged-bytes",
            "module-compile-named-open-ended-group-alternation-warm-bytes",
            "module-search-named-open-ended-group-alternation-lower-bound-de-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-alternation-fourth-repetition-de-purged-bytes",
            "module-compile-numbered-open-ended-group-conditional-cold-bytes",
            "module-search-numbered-open-ended-group-conditional-second-repetition-bc-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-conditional-third-repetition-mixed-purged-bytes",
            "module-compile-named-open-ended-group-conditional-warm-bytes",
            "module-search-named-open-ended-group-conditional-fourth-repetition-de-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-conditional-third-repetition-mixed-purged-bytes",
            "module-compile-numbered-open-ended-group-broader-range-cold-bytes",
            "module-search-numbered-open-ended-group-broader-range-lower-bound-bc-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-broader-range-third-repetition-mixed-purged-bytes",
            "module-compile-named-open-ended-group-broader-range-warm-bytes",
            "module-search-named-open-ended-group-broader-range-lower-bound-de-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-broader-range-third-repetition-de-purged-bytes",
            "module-compile-numbered-open-ended-group-broader-range-conditional-cold-bytes",
            "module-search-numbered-open-ended-group-broader-range-conditional-second-repetition-bc-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-bytes",
            "module-compile-named-open-ended-group-broader-range-conditional-warm-bytes",
            "module-search-named-open-ended-group-broader-range-conditional-fourth-repetition-de-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-bytes",
            "module-compile-numbered-open-ended-group-broader-range-backtracking-heavy-cold-bytes",
            "module-search-numbered-open-ended-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-bytes",
            "module-compile-named-open-ended-group-broader-range-backtracking-heavy-warm-bytes",
            "module-search-named-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-bytes",
            "module-compile-numbered-open-ended-group-backtracking-heavy-cold-bytes",
            "module-search-numbered-open-ended-group-backtracking-heavy-lower-bound-b-branch-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-group-backtracking-heavy-second-repetition-b-then-bc-purged-bytes",
            "module-compile-named-open-ended-group-backtracking-heavy-warm-bytes",
            "module-search-named-open-ended-group-backtracking-heavy-third-repetition-mixed-warm-bytes",
            "pattern-fullmatch-named-open-ended-group-backtracking-heavy-purged-bytes",
        ),
        zero_gap_bytes_representative_subsets=(
            (
                "module-compile-numbered-open-ended-group-conditional-cold-bytes",
                "module-search-numbered-open-ended-group-conditional-second-repetition-bc-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-conditional-third-repetition-mixed-purged-bytes",
                "module-compile-named-open-ended-group-conditional-warm-bytes",
                "module-search-named-open-ended-group-conditional-fourth-repetition-de-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-conditional-third-repetition-mixed-purged-bytes",
                "module-compile-numbered-open-ended-group-broader-range-conditional-cold-bytes",
                "module-search-numbered-open-ended-group-broader-range-conditional-second-repetition-bc-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-bytes",
                "module-compile-named-open-ended-group-broader-range-conditional-warm-bytes",
                "module-search-named-open-ended-group-broader-range-conditional-fourth-repetition-de-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-bytes",
            ),
            (
                "module-compile-numbered-open-ended-group-alternation-cold-bytes",
                "module-search-numbered-open-ended-group-alternation-lower-bound-bc-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-alternation-third-repetition-mixed-purged-bytes",
                "module-compile-named-open-ended-group-alternation-warm-bytes",
                "module-search-named-open-ended-group-alternation-lower-bound-de-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-alternation-fourth-repetition-de-purged-bytes",
            ),
            (
                "module-compile-numbered-open-ended-group-broader-range-cold-bytes",
                "module-search-numbered-open-ended-group-broader-range-lower-bound-bc-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-broader-range-third-repetition-mixed-purged-bytes",
                "module-compile-named-open-ended-group-broader-range-warm-bytes",
                "module-search-named-open-ended-group-broader-range-lower-bound-de-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-broader-range-third-repetition-de-purged-bytes",
            ),
            (
                "module-compile-numbered-open-ended-group-backtracking-heavy-cold-bytes",
                "module-search-numbered-open-ended-group-backtracking-heavy-lower-bound-b-branch-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-backtracking-heavy-second-repetition-b-then-bc-purged-bytes",
                "module-compile-named-open-ended-group-backtracking-heavy-warm-bytes",
                "module-search-named-open-ended-group-backtracking-heavy-third-repetition-mixed-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-backtracking-heavy-purged-bytes",
            ),
            (
                "module-compile-numbered-open-ended-group-broader-range-backtracking-heavy-cold-bytes",
                "module-search-numbered-open-ended-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes",
                "pattern-fullmatch-numbered-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-bytes",
                "module-compile-named-open-ended-group-broader-range-backtracking-heavy-warm-bytes",
                "module-search-named-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-warm-bytes",
                "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-bytes",
            ),
        ),
    ),
    "quantified-alternation-boundary": _combined_manifest_definition(
        fully_measured_expectation=_combined_fully_measured_manifest_expectation(
            coverage_group="quantified-alternation",
            representative_measured_workload_ids=(
                "module-compile-numbered-quantified-alternation-cold-bytes",
                "module-search-numbered-quantified-alternation-lower-bound-warm-bytes",
                "pattern-fullmatch-numbered-quantified-alternation-second-repetition-purged-bytes",
                "module-compile-named-quantified-alternation-warm-bytes",
                "module-search-named-quantified-alternation-second-repetition-warm-bytes",
                "pattern-fullmatch-named-quantified-alternation-lower-bound-purged-bytes",
                "module-compile-numbered-quantified-alternation-nested-branch-cold-bytes",
                "module-search-numbered-quantified-alternation-nested-branch-lower-bound-inner-branch-warm-bytes",
                "pattern-fullmatch-numbered-quantified-alternation-nested-branch-lower-bound-literal-branch-purged-bytes",
                "module-compile-named-quantified-alternation-nested-branch-warm-bytes",
                "module-search-named-quantified-alternation-nested-branch-lower-bound-literal-branch-warm-bytes",
                "pattern-fullmatch-named-quantified-alternation-nested-branch-second-repetition-mixed-purged-bytes",
                "module-search-numbered-quantified-alternation-branch-backref-cold-bytes",
                "module-compile-numbered-quantified-alternation-branch-backref-cold-bytes",
                "pattern-fullmatch-numbered-quantified-alternation-branch-backref-second-repetition-purged-bytes",
                "module-compile-named-quantified-alternation-branch-backref-warm-bytes",
                "module-search-named-quantified-alternation-branch-backref-lower-bound-c-branch-warm-bytes",
                "pattern-fullmatch-named-quantified-alternation-branch-backref-second-repetition-purged-bytes",
                "module-compile-numbered-quantified-alternation-broader-range-cold-bytes",
                "module-search-numbered-quantified-alternation-broader-range-third-repetition-cold-bytes",
                "pattern-fullmatch-numbered-quantified-alternation-broader-range-third-repetition-bcb-purged-bytes",
                "module-compile-named-quantified-alternation-broader-range-warm-bytes",
                "module-search-named-quantified-alternation-broader-range-third-repetition-bcc-warm-bytes",
                "pattern-fullmatch-named-quantified-alternation-broader-range-third-repetition-bbb-purged-bytes",
                "module-compile-numbered-quantified-alternation-open-ended-cold-bytes",
                "module-search-numbered-quantified-alternation-open-ended-lower-bound-b-warm-bytes",
                "pattern-fullmatch-numbered-quantified-alternation-open-ended-fourth-repetition-bcbc-purged-bytes",
                "module-compile-named-quantified-alternation-open-ended-warm-bytes",
                "module-search-named-quantified-alternation-open-ended-lower-bound-c-warm-bytes",
                "pattern-fullmatch-named-quantified-alternation-open-ended-fourth-repetition-bcbc-purged-bytes",
                "module-compile-numbered-quantified-alternation-conditional-cold-bytes",
                "module-search-numbered-quantified-alternation-conditional-lower-bound-b-warm-bytes",
                "pattern-fullmatch-numbered-quantified-alternation-conditional-second-repetition-mixed-purged-bytes",
                "module-compile-named-quantified-alternation-conditional-warm-bytes",
                "module-search-named-quantified-alternation-conditional-absent-warm-bytes",
                "pattern-fullmatch-named-quantified-alternation-conditional-second-repetition-c-purged-bytes",
                "module-compile-numbered-quantified-alternation-backtracking-heavy-cold-bytes",
                "module-search-numbered-quantified-alternation-backtracking-heavy-lower-bound-b-branch-warm-bytes",
                "pattern-fullmatch-numbered-quantified-alternation-backtracking-heavy-lower-bound-bc-branch-purged-bytes",
                "module-compile-named-quantified-alternation-backtracking-heavy-warm-bytes",
                "module-search-named-quantified-alternation-backtracking-heavy-lower-bound-bc-branch-warm-bytes",
                "pattern-fullmatch-named-quantified-alternation-backtracking-heavy-second-repetition-bc-then-b-purged-bytes",
            ),
            expected_measured_workload_count=84,
            expected_total_workload_count=84,
        ),
    ),
    "conditional-group-exists-boundary": _combined_manifest_definition(
        zero_gap_bytes_representative_subsets=(
            (
                "module-sub-template-numbered-conditional-group-exists-replacement-warm-bytes",
                "module-subn-template-numbered-conditional-group-exists-replacement-warm-bytes",
                "pattern-sub-template-numbered-conditional-group-exists-replacement-purged-bytes",
                "pattern-subn-template-numbered-conditional-group-exists-replacement-purged-bytes",
                "module-sub-template-named-conditional-group-exists-replacement-warm-bytes",
                "module-subn-template-named-conditional-group-exists-replacement-warm-bytes",
                "pattern-sub-template-named-conditional-group-exists-replacement-purged-bytes",
                "pattern-subn-template-named-conditional-group-exists-replacement-purged-bytes",
                "module-sub-template-numbered-conditional-group-exists-replacement-negative-count-warm-bytes",
                "module-subn-template-named-conditional-group-exists-replacement-negative-count-warm-bytes",
                "pattern-sub-template-numbered-conditional-group-exists-replacement-negative-count-purged-bytes",
                "pattern-subn-template-named-conditional-group-exists-replacement-negative-count-purged-bytes",
                "module-sub-callable-numbered-conditional-group-exists-replacement-negative-count-warm-bytes",
                "module-subn-callable-named-conditional-group-exists-replacement-negative-count-warm-bytes",
                "pattern-sub-callable-numbered-conditional-group-exists-replacement-negative-count-purged-bytes",
                "pattern-subn-callable-named-conditional-group-exists-replacement-negative-count-purged-bytes",
            ),
            (
                "module-sub-callable-numbered-conditional-group-exists-replacement-none-count-warm-bytes",
                "pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-purged-bytes",
                "module-sub-callable-named-conditional-group-exists-replacement-none-count-warm-bytes",
                "pattern-sub-callable-named-conditional-group-exists-replacement-none-count-purged-bytes",
                "module-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-warm-bytes",
                "pattern-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-purged-bytes",
                "module-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-warm-bytes",
                "pattern-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-purged-bytes",
                "module-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
                "module-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
                "pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
                "pattern-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
                "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-bytes",
                "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-bytes",
                "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-bytes",
                "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-bytes",
            ),
            (
                "module-sub-callable-numbered-nested-conditional-group-exists-replacement-warm-bytes",
                "module-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-warm-bytes",
                "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-purged-bytes",
                "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-purged-bytes",
                "module-sub-callable-named-nested-conditional-group-exists-replacement-warm-bytes",
                "module-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-warm-bytes",
                "pattern-sub-callable-named-nested-conditional-group-exists-replacement-purged-bytes",
                "pattern-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-purged-bytes",
                "module-sub-callable-numbered-nested-conditional-group-exists-replacement-no-match-warm-bytes",
                "module-subn-callable-numbered-nested-conditional-group-exists-replacement-no-match-warm-bytes",
                "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-no-match-purged-bytes",
                "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-no-match-purged-bytes",
                "module-sub-callable-named-nested-conditional-group-exists-replacement-no-match-warm-bytes",
                "module-subn-callable-named-nested-conditional-group-exists-replacement-no-match-warm-bytes",
                "pattern-sub-callable-named-nested-conditional-group-exists-replacement-no-match-purged-bytes",
                "pattern-subn-callable-named-nested-conditional-group-exists-replacement-no-match-purged-bytes",
                "module-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-warm-bytes",
                "module-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-warm-bytes",
                "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-purged-bytes",
                "pattern-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-purged-bytes",
                "module-sub-callable-numbered-nested-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
                "module-subn-callable-named-nested-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
                "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
                "pattern-subn-callable-named-nested-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
            ),
            (
                "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-warm-bytes",
                "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-absent-exception-warm-bytes",
                "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-purged-bytes",
                "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-absent-exception-purged-bytes",
                "module-sub-callable-named-quantified-conditional-group-exists-replacement-warm-bytes",
                "module-subn-callable-named-quantified-conditional-group-exists-replacement-absent-exception-warm-bytes",
                "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-purged-bytes",
                "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-absent-exception-purged-bytes",
                "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-none-count-warm-bytes",
                "module-subn-callable-named-quantified-conditional-group-exists-replacement-none-count-absent-exception-warm-bytes",
                "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-none-count-purged-bytes",
                "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-none-count-absent-exception-purged-bytes",
                "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-warm-bytes",
                "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-warm-bytes",
                "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-purged-bytes",
                "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-purged-bytes",
                "module-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-warm-bytes",
                "module-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-warm-bytes",
                "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-purged-bytes",
                "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-purged-bytes",
                "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-warm-bytes",
                "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-warm-bytes",
                "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-purged-bytes",
                "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-purged-bytes",
                "module-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-warm-bytes",
                "module-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-warm-bytes",
                "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-purged-bytes",
                "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-purged-bytes",
                "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-no-match-warm-bytes",
                "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-no-match-warm-bytes",
                "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-no-match-purged-bytes",
                "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-no-match-purged-bytes",
                "module-sub-callable-named-quantified-conditional-group-exists-replacement-no-match-warm-bytes",
                "module-subn-callable-named-quantified-conditional-group-exists-replacement-no-match-warm-bytes",
                "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-no-match-purged-bytes",
                "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-no-match-purged-bytes",
            ),
            (
                "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
                "module-subn-callable-numbered-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
                "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
                "pattern-subn-callable-numbered-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
                "module-sub-callable-named-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
                "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
                "pattern-sub-callable-named-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
                "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
                "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-bytes",
                "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-bytes",
                "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-bytes",
                "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-bytes",
                "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-bytes",
                "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-bytes",
                "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-bytes",
                "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-bytes",
            ),
        ),
    ),
    "regression-matrix": _combined_manifest_definition(
        exclude_from_combined_targets=True,
        representative_measured_workload_ids=(
            "regression-parser-bytes-backreference-purged",
        ),
    ),
})


def _combined_slice_expectation(
    *,
    manifest_id: str,
    slice_id: str,
    required_syntax_features: tuple[str, ...] = (),
    excluded_syntax_features: tuple[str, ...] = (),
    required_categories: tuple[str, ...] = (),
    excluded_categories: tuple[str, ...] = (),
    required_id_suffix: str | None = None,
    expected_workload_ids: tuple[str, ...],
    expected_patterns: set[str],
    expected_operations: set[str],
    expected_haystacks: set[str],
    required_row_categories: tuple[str, ...],
    expected_status: str = "measured",
) -> SourceTreeCombinedSliceExpectation:
    return SourceTreeCombinedSliceExpectation(
        manifest_id=manifest_id,
        slice_id=slice_id,
        required_syntax_features=tuple(
            str(feature) for feature in required_syntax_features
        ),
        excluded_syntax_features=tuple(
            str(feature) for feature in excluded_syntax_features
        ),
        required_categories=tuple(str(category) for category in required_categories),
        excluded_categories=tuple(str(category) for category in excluded_categories),
        required_id_suffix=required_id_suffix,
        expected_workload_ids=(
            expected_workload_ids
            if isinstance(expected_workload_ids, tuple)
            and all(
                isinstance(workload_id, str)
                for workload_id in expected_workload_ids
            )
            else tuple(str(workload_id) for workload_id in expected_workload_ids)
        ),
        expected_patterns=frozenset(str(pattern) for pattern in expected_patterns),
        expected_operations=frozenset(
            str(operation) for operation in expected_operations
        ),
        expected_haystacks=frozenset(
            str(haystack) for haystack in expected_haystacks
        ),
        required_row_categories=tuple(
            str(category) for category in required_row_categories
        ),
        expected_status=expected_status,
    )


def _source_tree_workload_ids_for_text_model(
    workload_stems: tuple[str, ...],
    *,
    text_model: str,
) -> tuple[str, ...]:
    suffix = "-bytes" if text_model == "bytes" else "-str"
    return tuple(f"{stem}{suffix}" for stem in workload_stems)


_SOURCE_TREE_CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_WORKLOAD_STEMS = (
    "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-warm",
    "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-absent-exception-warm",
    "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-purged",
    "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-absent-exception-purged",
    "module-sub-callable-named-quantified-conditional-group-exists-replacement-warm",
    "module-subn-callable-named-quantified-conditional-group-exists-replacement-absent-exception-warm",
    "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-purged",
    "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-absent-exception-purged",
    "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-none-count-warm",
    "module-subn-callable-named-quantified-conditional-group-exists-replacement-none-count-absent-exception-warm",
    "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-none-count-purged",
    "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-none-count-absent-exception-purged",
    "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-warm",
    "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-warm",
    "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-purged",
    "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-purged",
    "module-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-warm",
    "module-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-warm",
    "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-purged",
    "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-purged",
    "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-warm",
    "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-warm",
    "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-purged",
    "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-negative-count-no-match-purged",
    "module-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-warm",
    "module-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-warm",
    "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-purged",
    "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-negative-count-no-match-purged",
    "module-sub-callable-numbered-quantified-conditional-group-exists-replacement-no-match-warm",
    "module-subn-callable-numbered-quantified-conditional-group-exists-replacement-no-match-warm",
    "pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-no-match-purged",
    "pattern-subn-callable-numbered-quantified-conditional-group-exists-replacement-no-match-purged",
    "module-sub-callable-named-quantified-conditional-group-exists-replacement-no-match-warm",
    "module-subn-callable-named-quantified-conditional-group-exists-replacement-no-match-warm",
    "pattern-sub-callable-named-quantified-conditional-group-exists-replacement-no-match-purged",
    "pattern-subn-callable-named-quantified-conditional-group-exists-replacement-no-match-purged",
)

CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS = (
    _source_tree_workload_ids_for_text_model(
        _SOURCE_TREE_CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_WORKLOAD_STEMS,
        text_model="str",
    )
)
CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS = (
    _source_tree_workload_ids_for_text_model(
        _SOURCE_TREE_CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_WORKLOAD_STEMS,
        text_model="bytes",
    )
)

SOURCE_TREE_ROUTED_COLLECTION_REPLACEMENT_CONDITIONAL_CALLABLE_HELPER_NAMES = (
    "_conditional_group_exists_callable_str_slice_workloads",
    "_conditional_group_exists_callable_bytes_slice_workloads",
    "_conditional_group_exists_quantified_callable_str_workloads",
    "_conditional_group_exists_nested_callable_str_workloads",
    "_conditional_group_exists_nested_callable_bytes_workloads",
    "_conditional_group_exists_quantified_callable_bytes_workloads",
    "_conditional_group_exists_alternation_callable_bytes_workloads",
    "_split_workload_ids_by_text_model",
    "_selected_workload_ids",
    "_mirrored_bytes_workload_ids",
    "_conditional_group_exists_template_replacement_expectation",
    "_conditional_group_exists_callable_replacement_expectations",
    "_conditional_group_exists_alternation_callable_replacement_expectation",
    "_conditional_group_exists_nested_callable_replacement_expectation",
    "_conditional_group_exists_nested_callable_bytes_replacement_expectation",
    "_conditional_group_exists_quantified_callable_replacement_expectation",
    "_conditional_group_exists_quantified_callable_bytes_replacement_expectation",
)

SOURCE_TREE_ROUTED_COLLECTION_REPLACEMENT_WORKLOAD_ID_NAMES = (
    "CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS",
    "CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS",
    "CONDITIONAL_GROUP_EXISTS_TEMPLATE_ROUND_TRIP_WORKLOAD_IDS",
    "CONDITIONAL_GROUP_EXISTS_CALLABLE_BYTES_WORKLOAD_IDS",
    "CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS",
    "CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS",
    "CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_IDS",
    "CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS",
    "CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS",
    "CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS",
    "CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS",
    "CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS",
    "_is_collection_replacement_compiled_pattern_success_workload",
)

SOURCE_TREE_ROUTED_COLLECTION_REPLACEMENT_SIGNATURE_HELPER_NAMES = (
    "_conditional_group_exists_nested_callable_correctness_case_signature",
    "_conditional_group_exists_nested_callable_workload_signature",
    "_conditional_group_exists_quantified_callable_correctness_case_signature",
    "_conditional_group_exists_quantified_callable_workload_signature",
)

SOURCE_TREE_ROUTED_COLLECTION_REPLACEMENT_COMBINED_SLICE_OWNER_NAMES = (
    "SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS",
)


SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS = (
    _combined_slice_expectation(
        manifest_id="module-boundary",
        slice_id="anchored-module-compile-cluster",
        required_syntax_features=("module-compile", "literal-text"),
        excluded_syntax_features=("compiled-pattern-first-argument",),
        required_categories=("compile", "literal"),
        expected_workload_ids=(
            "module-compile-literal-cold",
            "module-compile-literal-warm",
            "module-compile-literal-purged",
        ),
        expected_patterns={r"^abc$"},
        expected_operations={"module.compile"},
        expected_haystacks=set(),
        required_row_categories=("compile", "literal"),
        expected_status="measured",
    ),
    _combined_slice_expectation(
        manifest_id="module-boundary",
        slice_id="compiled-pattern-module-compile-literal-success",
        required_syntax_features=(
            "module-compile",
            "literal-text",
            "compiled-pattern-first-argument",
        ),
        excluded_syntax_features=("keyword-flags",),
        required_categories=("compile", "literal", "compiled-pattern"),
        excluded_categories=("keyword", "flags"),
        expected_workload_ids=(
            "module-compile-literal-warm-str-compiled-pattern",
            "module-compile-literal-purged-bytes-compiled-pattern",
        ),
        expected_patterns={"abc"},
        expected_operations={"module.compile"},
        expected_haystacks=set(),
        required_row_categories=("compile", "literal", "compiled-pattern"),
        expected_status="measured",
    ),
    _combined_slice_expectation(
        manifest_id="module-boundary",
        slice_id="compiled-pattern-module-compile-named-group-success",
        required_syntax_features=(
            "module-compile",
            "grouping-forms",
            "named-groups",
            "compiled-pattern-first-argument",
        ),
        required_categories=("compile", "named-group", "compiled-pattern"),
        excluded_syntax_features=("keyword-flags",),
        excluded_categories=("keyword", "flags"),
        expected_workload_ids=(
            "module-compile-named-group-warm-str-compiled-pattern",
            "module-compile-named-group-purged-bytes-compiled-pattern",
        ),
        expected_patterns={"(?P<word>abc)"},
        expected_operations={"module.compile"},
        expected_haystacks=set(),
        required_row_categories=("compile", "named-group", "compiled-pattern"),
        expected_status="measured",
    ),
    _combined_slice_expectation(
        manifest_id="module-boundary",
        slice_id="compiled-pattern-module-compile-flags-int-zero-keyword-named-group",
        required_syntax_features=(
            "module-compile",
            "grouping-forms",
            "named-groups",
            "compiled-pattern-first-argument",
            "keyword-flags",
        ),
        required_categories=("compile", "named-group", "compiled-pattern", "keyword", "flags"),
        excluded_categories=("bool", "ignorecase", "exception"),
        expected_workload_ids=(
            "module-compile-flags-int-zero-warm-str-compiled-pattern-named-group",
            "module-compile-flags-int-zero-purged-bytes-compiled-pattern-named-group",
        ),
        expected_patterns={"(?P<word>abc)"},
        expected_operations={"module.compile"},
        expected_haystacks=set(),
        required_row_categories=(
            "compile",
            "named-group",
            "compiled-pattern",
            "keyword",
            "flags",
        ),
        expected_status="measured",
    ),
    _combined_slice_expectation(
        manifest_id="module-boundary",
        slice_id="compiled-pattern-module-compile-flags-bool-false-keyword-named-group",
        required_syntax_features=(
            "module-compile",
            "grouping-forms",
            "named-groups",
            "compiled-pattern-first-argument",
            "keyword-flags",
        ),
        required_categories=(
            "compile",
            "named-group",
            "compiled-pattern",
            "keyword",
            "flags",
            "bool",
        ),
        expected_workload_ids=(
            "module-compile-flags-bool-false-warm-str-compiled-pattern-named-group",
            "module-compile-flags-bool-false-purged-bytes-compiled-pattern-named-group",
        ),
        expected_patterns={"(?P<word>abc)"},
        expected_operations={"module.compile"},
        expected_haystacks=set(),
        required_row_categories=(
            "compile",
            "named-group",
            "compiled-pattern",
            "keyword",
            "flags",
            "bool",
        ),
        expected_status="measured",
    ),
    _combined_slice_expectation(
        manifest_id="module-boundary",
        slice_id="compiled-pattern-module-compile-flags-ignorecase-keyword-rejection-named-group",
        required_syntax_features=(
            "module-compile",
            "grouping-forms",
            "named-groups",
            "compiled-pattern-first-argument",
            "keyword-flags",
            "ignorecase-flag",
        ),
        required_categories=(
            "compile",
            "named-group",
            "compiled-pattern",
            "keyword",
            "flags",
            "ignorecase",
            "exception",
        ),
        expected_workload_ids=(
            "module-compile-flags-ignorecase-warm-str-compiled-pattern-named-group",
            "module-compile-flags-ignorecase-purged-bytes-compiled-pattern-named-group",
        ),
        expected_patterns={"(?P<word>abc)"},
        expected_operations={"module.compile"},
        expected_haystacks=set(),
        required_row_categories=(
            "compile",
            "named-group",
            "compiled-pattern",
            "keyword",
            "flags",
            "ignorecase",
            "exception",
        ),
        expected_status="measured",
    ),
    _combined_slice_expectation(
        manifest_id="module-boundary",
        slice_id="compiled-pattern-module-compile-flags-int-zero-keyword",
        required_syntax_features=(
            "module-compile",
            "literal-text",
            "compiled-pattern-first-argument",
            "keyword-flags",
        ),
        required_categories=("compile", "literal", "compiled-pattern", "keyword", "flags"),
        excluded_categories=("bool", "ignorecase", "exception"),
        expected_workload_ids=(
            "module-compile-flags-int-zero-warm-str-compiled-pattern",
            "module-compile-flags-int-zero-purged-bytes-compiled-pattern",
        ),
        expected_patterns={"abc"},
        expected_operations={"module.compile"},
        expected_haystacks=set(),
        required_row_categories=("compile", "literal", "compiled-pattern", "keyword", "flags"),
        expected_status="measured",
    ),
    _combined_slice_expectation(
        manifest_id="module-boundary",
        slice_id="compiled-pattern-module-compile-flags-bool-false-keyword",
        required_syntax_features=(
            "module-compile",
            "literal-text",
            "compiled-pattern-first-argument",
            "keyword-flags",
        ),
        required_categories=(
            "compile",
            "literal",
            "compiled-pattern",
            "keyword",
            "flags",
            "bool",
        ),
        expected_workload_ids=(
            "module-compile-flags-bool-false-warm-str-compiled-pattern",
            "module-compile-flags-bool-false-purged-bytes-compiled-pattern",
        ),
        expected_patterns={"abc"},
        expected_operations={"module.compile"},
        expected_haystacks=set(),
        required_row_categories=(
            "compile",
            "literal",
            "compiled-pattern",
            "keyword",
            "flags",
            "bool",
        ),
        expected_status="measured",
    ),
    _combined_slice_expectation(
        manifest_id="module-boundary",
        slice_id="compiled-pattern-module-compile-flags-ignorecase-keyword-rejection",
        required_syntax_features=(
            "module-compile",
            "literal-text",
            "compiled-pattern-first-argument",
            "keyword-flags",
            "ignorecase-flag",
        ),
        required_categories=(
            "compile",
            "literal",
            "compiled-pattern",
            "keyword",
            "flags",
            "ignorecase",
            "exception",
        ),
        expected_workload_ids=(
            "module-compile-flags-ignorecase-warm-str-compiled-pattern",
            "module-compile-flags-ignorecase-purged-bytes-compiled-pattern",
        ),
        expected_patterns={"abc"},
        expected_operations={"module.compile"},
        expected_haystacks=set(),
        required_row_categories=(
            "compile",
            "literal",
            "compiled-pattern",
            "keyword",
            "flags",
            "ignorecase",
            "exception",
        ),
        expected_status="measured",
    ),
    _combined_slice_expectation(
        manifest_id="branch-local-backreference-boundary",
        slice_id="broader-range-open-ended-conditional-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "conditionals",
            "nested-groups",
            "counted-repeats",
        ),
        required_categories=("open-ended-repeat", "broader-range"),
        expected_workload_ids=(
            "module-compile-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-cold-str",
            "module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-str",
            "pattern-fullmatch-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-mixed-branches-purged-str",
            "module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-warm-str",
            "module-search-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-warm-str",
            "pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-purged-str",
            "module-compile-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-cold-bytes",
            "module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-bytes",
            "pattern-fullmatch-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-mixed-branches-purged-bytes",
            "module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-warm-bytes",
            "module-search-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-warm-bytes",
            "pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-purged-bytes",
        ),
        expected_patterns={
            r"a((b|c){2,})\2(?(2)d|e)",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
        },
        expected_operations={"module.compile", "module.search", "pattern.fullmatch"},
        expected_haystacks={"zzabbbdzz", "abcbccd", "zzacccdzz", "abbbd"},
        required_row_categories=(
            "grouped",
            "nested-group",
            "alternation",
            "branch-local",
            "conditional",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-alternation-boundary",
        slice_id="quantified-nested-alternation",
        required_syntax_features=("alternation", "quantifiers"),
        excluded_syntax_features=("branch-local-backreferences",),
        expected_workload_ids=(
            "module-search-nested-group-quantified-alternation-cold-gap",
            "pattern-fullmatch-numbered-quantified-nested-group-alternation-repeated-mixed-purged-str",
            "module-search-named-quantified-nested-group-alternation-lower-bound-c-warm-str",
            "pattern-fullmatch-named-quantified-nested-group-alternation-repeated-mixed-purged-str",
        ),
        expected_patterns={
            r"a((b|c)+)d",
            r"a(?P<outer>(?P<inner>b|c)+)d",
        },
        expected_operations={"module.search", "pattern.fullmatch"},
        expected_haystacks={"zzabdzz", "acbbd", "zzacdzz", "abccd"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "quantified",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-alternation-boundary",
        slice_id="non-quantified-branch-local-backreference",
        required_syntax_features=("branch-local-backreferences",),
        excluded_syntax_features=("quantifiers",),
        expected_workload_ids=(
            "module-search-numbered-nested-group-branch-local-backreference-b-branch-warm-str",
            "module-compile-named-nested-group-branch-local-backreference-warm-str",
            "pattern-fullmatch-named-nested-group-branch-local-backreference-purged-gap",
        ),
        expected_patterns={
            r"a((b|c))\2d",
            r"a(?P<outer>(?P<inner>b|c))(?P=inner)d",
        },
        expected_operations={"module.compile", "module.search", "pattern.fullmatch"},
        expected_haystacks={"zzabbdzz", "accd"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "branch-local",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-alternation-boundary",
        slice_id="quantified-branch-local-backreference",
        required_syntax_features=("branch-local-backreferences", "quantifiers"),
        excluded_syntax_features=("counted-repeats",),
        expected_workload_ids=(
            "module-search-numbered-quantified-nested-group-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-search-numbered-quantified-nested-group-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-compile-named-quantified-nested-group-branch-local-backreference-warm-str",
            "module-compile-named-quantified-nested-group-branch-local-backreference-warm-bytes",
            "pattern-fullmatch-named-quantified-nested-group-branch-local-backreference-repeated-mixed-purged-str",
            "pattern-fullmatch-named-quantified-nested-group-branch-local-backreference-repeated-mixed-purged-bytes",
        ),
        expected_patterns={
            r"a((b|c)+)\2d",
            r"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
        },
        expected_operations={"module.compile", "module.search", "pattern.fullmatch"},
        expected_haystacks={"zzabbdzz", "abccd"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "branch-local",
            "quantified",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-alternation-boundary",
        slice_id="broader-range-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "counted-repeats",
            "ranged-repeats",
        ),
        expected_workload_ids=(
            "module-search-numbered-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-search-numbered-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-compile-named-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-warm-str",
            "module-compile-named-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-warm-bytes",
            "pattern-fullmatch-named-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-upper-bound-all-c-purged-str",
            "pattern-fullmatch-named-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-upper-bound-all-c-purged-bytes",
        ),
        expected_patterns={
            r"a((b|c){1,4})\2d",
            r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
        },
        expected_operations={"module.compile", "module.search", "pattern.fullmatch"},
        expected_haystacks={"zzabbdzz", "acccccd"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "branch-local",
            "quantified",
            "ranged-repeat",
            "counted-repeat",
            "broader-range",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-alternation-boundary",
        slice_id="broader-range-open-ended-branch-local-backreference",
        required_syntax_features=("branch-local-backreferences", "counted-repeats"),
        excluded_syntax_features=("ranged-repeats",),
        required_categories=("open-ended-repeat", "broader-range"),
        expected_workload_ids=(
            "module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-lower-bound-b-branch-warm-str",
            "module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-lower-bound-b-branch-warm-bytes",
            "module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-warm-str",
            "module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-warm-bytes",
            "pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-lower-bound-c-branch-purged-str",
            "pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-lower-bound-c-branch-purged-bytes",
        ),
        expected_patterns={
            r"a((b|c){2,})\2d",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        },
        expected_operations={"module.compile", "module.search", "pattern.fullmatch"},
        expected_haystacks={"zzabbbdzz", "acccd"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "branch-local",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="nested-group-bytes",
        required_syntax_features=("callable-replacement", "pattern-text-model"),
        excluded_syntax_features=(
            "alternation",
            "branch-local-backreferences",
            "quantifiers",
        ),
        expected_workload_ids=(
            "module-sub-callable-nested-group-numbered-warm-bytes",
            "module-subn-callable-nested-group-numbered-warm-bytes",
            "pattern-sub-callable-nested-group-numbered-purged-bytes",
            "pattern-subn-callable-nested-group-numbered-purged-bytes",
            "module-sub-callable-nested-group-named-warm-bytes",
            "module-subn-callable-nested-group-named-warm-bytes",
            "pattern-sub-callable-nested-group-named-purged-bytes",
            "pattern-subn-callable-nested-group-named-purged-bytes",
        ),
        expected_patterns={
            r"a((b))d",
            r"a(?P<outer>(?P<inner>b))d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abdabd"},
        required_row_categories=(
            "nested-group",
            "replacement",
            "callable",
            "bytes",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="nested-alternation",
        required_syntax_features=("alternation", "callable-replacement"),
        excluded_syntax_features=("branch-local-backreferences", "quantifiers"),
        expected_workload_ids=(
            "module-sub-callable-nested-group-alternation-cold-gap",
            "pattern-subn-callable-numbered-nested-group-alternation-c-branch-first-match-only-purged-str",
            "module-sub-callable-named-nested-group-alternation-c-branch-warm-str",
            "pattern-subn-callable-named-nested-group-alternation-b-branch-first-match-only-purged-str",
        ),
        expected_patterns={
            r"a((b|c))d",
            r"a(?P<outer>(?P<inner>b|c))d",
        },
        expected_operations={"module.sub", "pattern.subn"},
        expected_haystacks={"abdacd", "acdabd", "acd"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="quantified-nested-group",
        required_syntax_features=(
            "callable-replacement",
            "quantifiers",
        ),
        excluded_syntax_features=("alternation", "branch-local-backreferences"),
        expected_workload_ids=(
            "module-sub-callable-numbered-quantified-nested-group-lower-bound-warm-str",
            "module-subn-callable-numbered-quantified-nested-group-first-match-only-warm-str",
            "pattern-sub-callable-named-quantified-nested-group-repeated-outer-purged-str",
            "pattern-subn-callable-named-quantified-nested-group-purged-gap",
            "module-sub-callable-numbered-quantified-nested-group-lower-bound-warm-bytes",
            "module-subn-callable-numbered-quantified-nested-group-first-match-only-warm-bytes",
            "pattern-sub-callable-named-quantified-nested-group-repeated-outer-purged-bytes",
            "pattern-subn-callable-named-quantified-nested-group-first-match-only-purged-bytes",
        ),
        expected_patterns={
            r"a((bc)+)d",
            r"a(?P<outer>(?P<inner>bc)+)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"zzabcdzz", "zzabcbcdabcbcdzz", "zzabcbcdzz"},
        required_row_categories=(
            "nested-group",
            "replacement",
            "callable",
            "quantified",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="quantified-nested-alternation",
        required_syntax_features=("alternation", "callable-replacement", "quantifiers"),
        excluded_syntax_features=("branch-local-backreferences",),
        excluded_categories=("counted-repeat",),
        expected_workload_ids=(
            "module-sub-callable-numbered-quantified-nested-group-alternation-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-quantified-nested-group-alternation-c-branch-first-match-only-warm-str",
            "pattern-sub-callable-named-quantified-nested-group-alternation-repeated-mixed-purged-str",
            "pattern-subn-callable-named-quantified-nested-group-alternation-c-branch-first-match-only-purged-str",
            "module-sub-callable-numbered-quantified-nested-group-alternation-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-quantified-nested-group-alternation-c-branch-first-match-only-warm-bytes",
            "pattern-sub-callable-named-quantified-nested-group-alternation-repeated-mixed-purged-bytes",
            "pattern-subn-callable-named-quantified-nested-group-alternation-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns={
            r"a((b|c)+)d",
            r"a(?P<outer>(?P<inner>b|c)+)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"zzabdzz", "zzabccdacbbdzz", "zzabccdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "quantified",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="nested-broader-range-backtracking-heavy-callable-replacement",
        required_syntax_features=(
            "alternation",
            "callable-replacement",
            "quantifiers",
            "counted-repeats",
            "ranged-repeats",
        ),
        excluded_syntax_features=("branch-local-backreferences", "conditionals"),
        required_categories=("broader-range", "backtracking-heavy"),
        expected_workload_ids=(
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-str",
            "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-str",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-upper-bound-mixed-purged-str",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-str",
            "module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-bytes",
            "module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-bytes",
            "pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-upper-bound-mixed-purged-bytes",
            "pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-bytes",
        ),
        expected_patterns={
            r"a(((bc|b)c){1,4})d",
            r"a(?P<outer>(?:(?P<inner>bc|b)c){1,4})d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={
            "abcd",
            "abccdabcbccd",
            "zzabcbccbccbcdzz",
            "zzabccbcdabccdzz",
        },
        required_row_categories=(
            "grouped",
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "quantified",
            "ranged-repeat",
            "counted-repeat",
            "broader-range",
            "backtracking-heavy",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="nested-broader-range-open-ended-backtracking-heavy-callable-replacement",
        required_syntax_features=(
            "alternation",
            "callable-replacement",
            "quantifiers",
            "counted-repeats",
        ),
        excluded_syntax_features=(
            "branch-local-backreferences",
            "conditionals",
            "ranged-repeats",
        ),
        required_categories=("open-ended-repeat", "broader-range", "backtracking-heavy"),
        expected_workload_ids=(
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-str",
            "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-str",
            "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-fourth-repetition-short-only-purged-str",
            "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-str",
            "module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-bytes",
            "module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-bytes",
            "pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-fourth-repetition-short-only-purged-bytes",
            "pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-bytes",
        ),
        expected_patterns={
            r"a(((bc|b)c){2,})d",
            r"a(?P<outer>(?:(?P<inner>bc|b)c){2,})d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={
            "abcbcd",
            "abccbccdabcbcd",
            "zzabcbcbcbcdzz",
            "zzabcbcbcbcdabccbccdzz",
        },
        required_row_categories=(
            "grouped",
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
            "backtracking-heavy",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="branch-local-backreference",
        required_syntax_features=("branch-local-backreferences", "callable-replacement"),
        excluded_syntax_features=("quantifiers",),
        expected_workload_ids=(
            "module-sub-callable-numbered-nested-group-alternation-branch-local-backreference-b-branch-warm-str",
            "module-subn-callable-numbered-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str",
            "pattern-sub-callable-named-nested-group-alternation-branch-local-backreference-c-branch-purged-str",
            "pattern-subn-callable-named-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-str",
            "module-sub-callable-numbered-nested-group-alternation-branch-local-backreference-b-branch-warm-bytes",
            "module-subn-callable-numbered-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-bytes",
            "pattern-sub-callable-named-nested-group-alternation-branch-local-backreference-c-branch-purged-bytes",
            "pattern-subn-callable-named-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns={
            r"a((b|c))\2d",
            r"a(?P<outer>(?P<inner>b|c))(?P=inner)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbd", "abbdaccd", "accd", "accdabbd"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "branch-local",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="quantified-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "callable-replacement",
            "quantifiers",
        ),
        excluded_syntax_features=("counted-repeats", "ranged-repeats"),
        expected_workload_ids=(
            "module-sub-callable-numbered-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str",
            "pattern-sub-callable-named-quantified-nested-group-alternation-branch-local-backreference-mixed-branches-purged-str",
            "pattern-subn-callable-named-quantified-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-str",
            "module-sub-callable-numbered-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-bytes",
            "pattern-sub-callable-named-quantified-nested-group-alternation-branch-local-backreference-mixed-branches-purged-bytes",
            "pattern-subn-callable-named-quantified-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns={
            r"a((b|c)+)\2d",
            r"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbd", "abbbdaccd", "zzabccdzz", "zzaccdabbbdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "branch-local",
            "quantified",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="broader-range-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "callable-replacement",
            "quantifiers",
            "counted-repeats",
            "ranged-repeats",
        ),
        excluded_syntax_features=("conditionals",),
        expected_workload_ids=(
            "module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-mixed-branches-first-match-only-warm-str",
            "pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-str",
            "pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-str",
            "module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-mixed-branches-first-match-only-warm-bytes",
            "pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-bytes",
            "pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns={
            r"a((b|c){1,4})\2d",
            r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbd", "abcbccdabbd", "zzacccccdzz", "zzacccccdabbbdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "branch-local",
            "quantified",
            "ranged-repeat",
            "counted-repeat",
            "broader-range",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="broader-range-conditional-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "callable-replacement",
            "quantifiers",
            "counted-repeats",
            "ranged-repeats",
            "conditionals",
        ),
        expected_workload_ids=(
            "module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-first-match-only-b-branch-warm-str",
            "pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-all-c-purged-str",
            "pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-c-branch-first-match-only-purged-str",
            "module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-first-match-only-b-branch-warm-bytes",
            "pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-all-c-purged-bytes",
            "pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns={
            r"a((b|c){1,4})\2(?(2)d|e)",
            r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)(?(inner)d|e)",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbd", "abbbdaccd", "zzacccccdzz", "zzacccccdabbbdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "branch-local",
            "conditional",
            "group-exists",
            "quantified",
            "ranged-repeat",
            "counted-repeat",
            "broader-range",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="open-ended-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "callable-replacement",
            "quantifiers",
            "counted-repeats",
        ),
        excluded_syntax_features=("conditionals", "ranged-repeats"),
        excluded_categories=("broader-range",),
        expected_workload_ids=(
            "module-sub-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str",
            "pattern-sub-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-lower-bound-c-branch-purged-str",
            "pattern-subn-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-str",
        ),
        expected_patterns={
            r"a((b|c){1,})\2d",
            r"a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbd", "abbbdaccd", "zzaccdzz", "zzaccdabcbccdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "branch-local",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="broader-range-open-ended-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "callable-replacement",
            "quantifiers",
            "counted-repeats",
        ),
        excluded_syntax_features=("conditionals", "ranged-repeats"),
        required_categories=("broader-range",),
        expected_workload_ids=(
            "module-sub-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-str",
            "pattern-sub-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-str",
            "pattern-subn-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-str",
            "module-sub-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-bytes",
            "pattern-sub-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-bytes",
            "pattern-subn-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns={
            r"a((b|c){2,})\2d",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbbd", "abbbdabcbccd", "zzacccdzz", "zzacccdabcbccdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "branch-local",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-callable-replacement-boundary",
        slice_id="broader-range-open-ended-conditional-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "callable-replacement",
            "quantifiers",
            "counted-repeats",
            "conditionals",
        ),
        excluded_syntax_features=("ranged-repeats",),
        required_categories=("broader-range",),
        expected_workload_ids=(
            "module-sub-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-str",
            "module-subn-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-str",
            "pattern-sub-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-str",
            "pattern-subn-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-str",
            "module-sub-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-bytes",
            "pattern-sub-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-bytes",
            "pattern-subn-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns={
            r"a((b|c){2,})\2(?(2)d|e)",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbbd", "abbbdabcbccd", "zzacccdzz", "zzacccdabcbccdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "branch-local",
            "conditional",
            "group-exists",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-replacement-boundary",
        slice_id="quantified-nested-group",
        required_syntax_features=("quantifiers", "replacement-template"),
        excluded_syntax_features=("branch-local-backreferences",),
        expected_workload_ids=(
            "module-sub-template-numbered-quantified-nested-group-replacement-lower-bound-warm-str",
            "module-subn-template-numbered-quantified-nested-group-replacement-first-match-only-warm-str",
            "pattern-sub-template-named-quantified-nested-group-replacement-repeated-outer-purged-str",
            "pattern-subn-template-named-quantified-nested-group-replacement-purged-gap",
        ),
        expected_patterns={
            r"a((bc)+)d",
            r"a(?P<outer>(?P<inner>bc)+)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"zzabcdzz", "zzabcbcdabcbcdzz", "zzabcbcdzz"},
        required_row_categories=(
            "nested-group",
            "replacement",
            "template",
            "quantified",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-replacement-boundary",
        slice_id="broader-range-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "replacement-template",
            "quantifiers",
            "counted-repeats",
            "ranged-repeats",
        ),
        excluded_syntax_features=("conditionals",),
        required_categories=("broader-range",),
        expected_workload_ids=(
            "module-sub-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-subn-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str",
            "pattern-sub-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-str",
            "pattern-subn-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-str",
            "module-sub-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-subn-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-bytes",
            "pattern-sub-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-bytes",
            "pattern-subn-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns={
            r"a((b|c){1,4})\2d",
            r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbd", "abbbdaccd", "zzacccccdzz", "zzacccccdabbbdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "template",
            "branch-local",
            "quantified",
            "ranged-repeat",
            "counted-repeat",
            "broader-range",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-replacement-boundary",
        slice_id="open-ended-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "replacement-template",
            "quantifiers",
            "counted-repeats",
        ),
        excluded_syntax_features=("conditionals", "ranged-repeats"),
        excluded_categories=("broader-range",),
        expected_workload_ids=(
            "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str",
            "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str",
            "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-lower-bound-c-branch-purged-str",
            "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-str",
        ),
        expected_patterns={
            r"a((b|c){1,})\2d",
            r"a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbd", "abbbdaccd", "zzaccdzz", "zzaccdabcbccdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "template",
            "branch-local",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-replacement-boundary",
        slice_id="broader-range-open-ended-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "replacement-template",
            "quantifiers",
            "counted-repeats",
        ),
        excluded_syntax_features=("conditionals", "ranged-repeats"),
        required_categories=("broader-range",),
        expected_workload_ids=(
            "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-str",
            "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-str",
            "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-str",
            "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-str",
            "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-bytes",
            "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-bytes",
            "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-bytes",
            "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns={
            r"a((b|c){2,})\2d",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbbd", "abbbdabcbccd", "zzacccdzz", "zzacccdabcbccdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "template",
            "branch-local",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="nested-group-replacement-boundary",
        slice_id="broader-range-open-ended-conditional-branch-local-backreference",
        required_syntax_features=(
            "branch-local-backreferences",
            "replacement-template",
            "quantifiers",
            "counted-repeats",
            "conditionals",
        ),
        excluded_syntax_features=("ranged-repeats",),
        required_categories=("broader-range",),
        expected_workload_ids=(
            "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-str",
            "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-str",
            "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-str",
            "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-str",
            "module-sub-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-bytes",
            "module-subn-template-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-bytes",
            "pattern-sub-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-bytes",
            "pattern-subn-template-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-bytes",
        ),
        expected_patterns={
            r"a((b|c){2,})\2(?(2)d|e)",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"abbbd", "abbbdabcbccd", "zzacccdzz", "zzacccdabcbccdzz"},
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "template",
            "branch-local",
            "conditional",
            "group-exists",
            "quantified",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="open-ended-quantified-group-boundary",
        slice_id="broader-range-group-alternation",
        required_syntax_features=("module-search",),
        excluded_syntax_features=("conditionals", "named-groups"),
        required_categories=(
            "broader-range",
            "search",
            "module",
            "lower-bound",
            "bc-bc",
        ),
        excluded_categories=("backtracking-heavy",),
        expected_workload_ids=(
            "module-search-numbered-open-ended-group-broader-range-cold-gap",
            "module-search-numbered-open-ended-group-broader-range-lower-bound-bc-warm-bytes",
        ),
        expected_patterns={r"a(bc|de){2,}d"},
        expected_operations={"module.search"},
        expected_haystacks={"zzabcbcdzz"},
        required_row_categories=(
            "grouped",
            "alternation",
            "quantifier",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
            "search",
            "module",
            "lower-bound",
            "bc-bc",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="open-ended-quantified-group-boundary",
        slice_id="broader-range-group-conditional",
        required_syntax_features=("module-search", "conditionals"),
        excluded_syntax_features=("named-groups",),
        required_categories=(
            "broader-range",
            "conditional",
            "search",
            "module",
            "present",
            "second-repetition",
            "bc-branch",
        ),
        excluded_categories=("backtracking-heavy",),
        expected_workload_ids=(
            "module-search-numbered-open-ended-group-broader-range-conditional-warm-gap",
            "module-search-numbered-open-ended-group-broader-range-conditional-second-repetition-bc-warm-bytes",
        ),
        expected_patterns={r"a((bc|de){2,})?(?(1)d|e)"},
        expected_operations={"module.search"},
        expected_haystacks={"zzabcbcdzz"},
        required_row_categories=(
            "grouped",
            "alternation",
            "quantifier",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
            "conditional",
            "optional-group",
            "search",
            "module",
            "present",
            "second-repetition",
            "bc-branch",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="open-ended-quantified-group-boundary",
        slice_id="broader-range-group-backtracking-heavy",
        required_syntax_features=("pattern-fullmatch", "named-groups"),
        excluded_syntax_features=("conditionals",),
        required_categories=(
            "broader-range",
            "backtracking-heavy",
            "pattern",
            "fullmatch",
            "named-group",
            "fourth-repetition",
            "b-branch",
        ),
        expected_workload_ids=(
            "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-str",
            "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-bytes",
        ),
        expected_patterns={r"a(?P<word>(bc|b)c){2,}d"},
        expected_operations={"pattern.fullmatch"},
        expected_haystacks={"abcbcbcbcd"},
        required_row_categories=(
            "grouped",
            "alternation",
            "quantifier",
            "counted-repeat",
            "open-ended-repeat",
            "broader-range",
            "backtracking-heavy",
            "pattern",
            "fullmatch",
            "named-group",
            "fourth-repetition",
            "b-branch",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="grouped-alternation-callable-replacement-boundary",
        slice_id="former-gap-callable-replacement-rows",
        required_syntax_features=("callable-replacement",),
        required_id_suffix="gap",
        expected_workload_ids=(
            "module-sub-callable-nested-grouped-alternation-cold-gap",
            "pattern-subn-callable-named-nested-grouped-alternation-purged-gap",
        ),
        expected_patterns={
            r"a((b|c))d",
            r"a(?P<outer>(b|c))d",
        },
        expected_operations={"module.sub", "pattern.subn"},
        expected_haystacks={"abdacd", "acdabd"},
        required_row_categories=(
            "alternation",
            "replacement",
            "callable",
            "gap",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="minimal-template-replacement-rows",
        required_syntax_features=("conditionals", "replacement-template"),
        excluded_syntax_features=("quantifiers",),
        excluded_categories=(
            "alternation-heavy",
            "nested-group",
            "quantified",
            "unsupported",
            "callable",
        ),
        expected_workload_ids=(
            "module-sub-template-numbered-conditional-group-exists-replacement-warm-gap",
            "module-subn-template-numbered-conditional-group-exists-replacement-warm-str",
            "pattern-sub-template-numbered-conditional-group-exists-replacement-purged-str",
            "pattern-subn-template-numbered-conditional-group-exists-replacement-purged-str",
            "module-sub-template-numbered-conditional-group-exists-replacement-warm-bytes",
            "module-subn-template-numbered-conditional-group-exists-replacement-warm-bytes",
            "pattern-sub-template-numbered-conditional-group-exists-replacement-purged-bytes",
            "pattern-subn-template-numbered-conditional-group-exists-replacement-purged-bytes",
            "module-sub-template-named-conditional-group-exists-replacement-warm-str",
            "module-subn-template-named-conditional-group-exists-replacement-warm-str",
            "pattern-sub-template-named-conditional-group-exists-replacement-purged-str",
            "pattern-subn-template-named-conditional-group-exists-replacement-purged-str",
            "module-sub-template-named-conditional-group-exists-replacement-warm-bytes",
            "module-subn-template-named-conditional-group-exists-replacement-warm-bytes",
            "pattern-sub-template-named-conditional-group-exists-replacement-purged-bytes",
            "pattern-subn-template-named-conditional-group-exists-replacement-purged-bytes",
            "module-sub-template-numbered-conditional-group-exists-replacement-negative-count-warm-str",
            "module-subn-template-named-conditional-group-exists-replacement-negative-count-warm-str",
            "pattern-sub-template-numbered-conditional-group-exists-replacement-negative-count-purged-str",
            "pattern-subn-template-named-conditional-group-exists-replacement-negative-count-purged-str",
            "module-sub-template-numbered-conditional-group-exists-replacement-negative-count-warm-bytes",
            "module-subn-template-named-conditional-group-exists-replacement-negative-count-warm-bytes",
            "pattern-sub-template-numbered-conditional-group-exists-replacement-negative-count-purged-bytes",
            "pattern-subn-template-named-conditional-group-exists-replacement-negative-count-purged-bytes",
        ),
        expected_patterns={
            r"a(b)?c(?(1)d|e)",
            r"a(?P<word>b)?c(?(word)d|e)",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"zzabcdzz", "zzacezz", "abcdaceabcd"},
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "replacement",
            "template",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="minimal-callable-replacement-rows",
        required_syntax_features=("conditionals", "callable-replacement"),
        excluded_syntax_features=("quantifiers",),
        excluded_categories=(
            "alternation",
            "alternation-heavy",
            "exception",
            "nested-conditional",
            "nested-group",
            "quantified",
            "unsupported",
        ),
        expected_workload_ids=(
            "module-sub-callable-numbered-conditional-group-exists-replacement-warm-str",
            "module-sub-callable-numbered-conditional-group-exists-replacement-warm-bytes",
            "module-subn-callable-numbered-conditional-group-exists-replacement-first-match-only-warm-str",
            "module-subn-callable-numbered-conditional-group-exists-replacement-first-match-only-warm-bytes",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-purged-str",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-purged-bytes",
            "pattern-subn-callable-numbered-conditional-group-exists-replacement-first-match-only-purged-str",
            "pattern-subn-callable-numbered-conditional-group-exists-replacement-first-match-only-purged-bytes",
            "module-sub-callable-numbered-conditional-group-exists-replacement-negative-count-warm-str",
            "module-sub-callable-numbered-conditional-group-exists-replacement-negative-count-warm-bytes",
            "module-sub-callable-named-conditional-group-exists-replacement-warm-str",
            "module-sub-callable-named-conditional-group-exists-replacement-warm-bytes",
            "module-subn-callable-named-conditional-group-exists-replacement-first-match-only-warm-str",
            "module-subn-callable-named-conditional-group-exists-replacement-first-match-only-warm-bytes",
            "pattern-sub-callable-named-conditional-group-exists-replacement-purged-str",
            "pattern-sub-callable-named-conditional-group-exists-replacement-purged-bytes",
            "pattern-subn-callable-named-conditional-group-exists-replacement-purged-gap",
            "pattern-subn-callable-named-conditional-group-exists-replacement-purged-bytes",
            "module-subn-callable-named-conditional-group-exists-replacement-negative-count-warm-str",
            "module-subn-callable-named-conditional-group-exists-replacement-negative-count-warm-bytes",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-negative-count-purged-str",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-negative-count-purged-bytes",
            "pattern-subn-callable-named-conditional-group-exists-replacement-negative-count-purged-str",
            "pattern-subn-callable-named-conditional-group-exists-replacement-negative-count-purged-bytes",
        ),
        expected_patterns={
            r"a(b)?c(?(1)d|e)",
            r"a(?P<word>b)?c(?(word)d|e)",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"zzabcdzz", "zzabcdacezz", "abcdaceabcd"},
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "replacement",
            "callable",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="minimal-callable-replacement-exception-rows",
        required_syntax_features=("conditionals", "callable-replacement"),
        excluded_syntax_features=("quantifiers",),
        required_categories=("exception",),
        excluded_categories=(
            "alternation",
            "alternation-heavy",
            "nested-conditional",
            "nested-group",
            "none-count",
            "quantified",
            "unsupported",
        ),
        expected_workload_ids=(
            "module-subn-callable-numbered-conditional-group-exists-replacement-absent-exception-warm-str",
            "module-subn-callable-numbered-conditional-group-exists-replacement-absent-exception-warm-bytes",
            "pattern-subn-callable-numbered-conditional-group-exists-replacement-absent-exception-purged-str",
            "pattern-subn-callable-numbered-conditional-group-exists-replacement-absent-exception-purged-bytes",
            "module-subn-callable-named-conditional-group-exists-replacement-absent-exception-warm-str",
            "module-subn-callable-named-conditional-group-exists-replacement-absent-exception-warm-bytes",
            "pattern-subn-callable-named-conditional-group-exists-replacement-absent-exception-purged-str",
            "pattern-subn-callable-named-conditional-group-exists-replacement-absent-exception-purged-bytes",
        ),
        expected_patterns={
            r"a(b)?c(?(1)d|e)",
            r"a(?P<word>b)?c(?(word)d|e)",
        },
        expected_operations={"module.subn", "pattern.subn"},
        expected_haystacks={"zzacezz"},
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "replacement",
            "callable",
            "absent",
            "count",
            "exception",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="minimal-callable-replacement-none-count-exception-rows",
        required_syntax_features=("conditionals", "callable-replacement"),
        excluded_syntax_features=("quantifiers",),
        required_categories=("none-count", "exception"),
        excluded_categories=(
            "alternation",
            "alternation-heavy",
            "nested-conditional",
            "nested-group",
            "quantified",
            "unsupported",
        ),
        expected_workload_ids=(
            "module-sub-callable-numbered-conditional-group-exists-replacement-none-count-warm-str",
            "module-sub-callable-numbered-conditional-group-exists-replacement-none-count-warm-bytes",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-purged-str",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-purged-bytes",
            "module-sub-callable-named-conditional-group-exists-replacement-none-count-warm-str",
            "module-sub-callable-named-conditional-group-exists-replacement-none-count-warm-bytes",
            "pattern-sub-callable-named-conditional-group-exists-replacement-none-count-purged-str",
            "pattern-sub-callable-named-conditional-group-exists-replacement-none-count-purged-bytes",
            "module-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-warm-str",
            "module-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-warm-bytes",
            "pattern-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-purged-str",
            "pattern-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-purged-bytes",
            "module-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-warm-str",
            "module-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-warm-bytes",
            "pattern-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-purged-str",
            "pattern-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-purged-bytes",
            "module-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-warm-str",
            "module-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
            "module-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-warm-str",
            "module-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-purged-str",
            "pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
            "pattern-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-purged-str",
            "pattern-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
        ),
        expected_patterns={
            r"a(b)?c(?(1)d|e)",
            r"a(?P<word>b)?c(?(word)d|e)",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"zzabcdzz", "zzacezz", "abcdaceabcd"},
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "replacement",
            "callable",
            "count",
            "none-count",
            "exception",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="alternation-heavy-callable-replacement-rows",
        required_syntax_features=("conditionals", "alternation", "callable-replacement"),
        excluded_syntax_features=("quantifiers",),
        required_categories=("alternation-heavy", "replacement", "callable"),
        expected_workload_ids=(
            "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-warm-gap",
            "module-subn-callable-numbered-conditional-group-exists-alternation-heavy-replacement-warm-str",
            "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-purged-str",
            "pattern-subn-callable-numbered-conditional-group-exists-alternation-heavy-replacement-purged-str",
            "module-sub-callable-named-conditional-group-exists-alternation-heavy-replacement-warm-str",
            "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-warm-str",
            "pattern-sub-callable-named-conditional-group-exists-alternation-heavy-replacement-purged-str",
            "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-purged-str",
            "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
            "module-subn-callable-numbered-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
            "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
            "pattern-subn-callable-numbered-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
            "module-sub-callable-named-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
            "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-warm-bytes",
            "pattern-sub-callable-named-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
            "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-purged-bytes",
            "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-str",
            "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-str",
            "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-str",
            "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-str",
            "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-str",
            "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-str",
            "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-str",
            "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-str",
            "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-bytes",
            "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-bytes",
            "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-bytes",
            "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-bytes",
            "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-bytes",
            "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-bytes",
            "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-bytes",
            "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-bytes",
        ),
        expected_patterns={
            r"a(b)?c(?(1)(de|df)|(eg|eh))",
            r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={
            "zzabcdezz",
            "zzabcdfzz",
            "zzacegzz",
            "zzacehzz",
        },
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "alternation-heavy",
            "replacement",
            "callable",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="nested-callable-replacement-str-rows",
        required_syntax_features=("conditionals", "callable-replacement"),
        required_categories=("nested-conditional",),
        excluded_syntax_features=("quantifiers",),
        excluded_categories=(
            "alternation",
            "alternation-heavy",
            "bytes",
            "quantified",
            "unsupported",
        ),
        expected_workload_ids=(
            "module-sub-callable-numbered-nested-conditional-group-exists-replacement-warm-str",
            "module-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-warm-str",
            "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-purged-str",
            "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-purged-str",
            "module-sub-callable-named-nested-conditional-group-exists-replacement-warm-str",
            "module-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-warm-str",
            "pattern-sub-callable-named-nested-conditional-group-exists-replacement-purged-str",
            "pattern-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-purged-str",
            "module-sub-callable-numbered-nested-conditional-group-exists-replacement-no-match-warm-str",
            "module-subn-callable-numbered-nested-conditional-group-exists-replacement-no-match-warm-str",
            "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-no-match-purged-str",
            "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-no-match-purged-str",
            "module-sub-callable-named-nested-conditional-group-exists-replacement-no-match-warm-str",
            "module-subn-callable-named-nested-conditional-group-exists-replacement-no-match-warm-str",
            "pattern-sub-callable-named-nested-conditional-group-exists-replacement-no-match-purged-str",
            "pattern-subn-callable-named-nested-conditional-group-exists-replacement-no-match-purged-str",
            "module-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-warm-str",
            "module-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-warm-str",
            "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-purged-str",
            "pattern-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-purged-str",
            "module-sub-callable-numbered-nested-conditional-group-exists-replacement-none-count-negative-count-warm-str",
            "module-subn-callable-named-nested-conditional-group-exists-replacement-none-count-negative-count-warm-str",
            "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-none-count-negative-count-purged-str",
            "pattern-subn-callable-named-nested-conditional-group-exists-replacement-none-count-negative-count-purged-str",
        ),
        expected_patterns={
            r"a(b)?c(?(1)(?(1)d|e)|f)",
            r"a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"zzabcdzz", "zzabcezz", "zzacezz", "zzacfzz"},
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "nested-conditional",
            "replacement",
            "callable",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="nested-callable-replacement-bytes-rows",
        required_syntax_features=(
            "pattern-text-model",
            "conditionals",
            "callable-replacement",
        ),
        required_categories=("nested-conditional", "bytes"),
        excluded_syntax_features=("quantifiers",),
        excluded_categories=(
            "alternation",
            "alternation-heavy",
            "nested-group",
            "unsupported",
        ),
        expected_workload_ids=(
            "module-sub-callable-numbered-nested-conditional-group-exists-replacement-warm-bytes",
            "module-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-warm-bytes",
            "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-purged-bytes",
            "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-absent-exception-purged-bytes",
            "module-sub-callable-named-nested-conditional-group-exists-replacement-warm-bytes",
            "module-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-warm-bytes",
            "pattern-sub-callable-named-nested-conditional-group-exists-replacement-purged-bytes",
            "pattern-subn-callable-named-nested-conditional-group-exists-replacement-absent-exception-purged-bytes",
            "module-sub-callable-numbered-nested-conditional-group-exists-replacement-no-match-warm-bytes",
            "module-subn-callable-numbered-nested-conditional-group-exists-replacement-no-match-warm-bytes",
            "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-no-match-purged-bytes",
            "pattern-subn-callable-numbered-nested-conditional-group-exists-replacement-no-match-purged-bytes",
            "module-sub-callable-named-nested-conditional-group-exists-replacement-no-match-warm-bytes",
            "module-subn-callable-named-nested-conditional-group-exists-replacement-no-match-warm-bytes",
            "pattern-sub-callable-named-nested-conditional-group-exists-replacement-no-match-purged-bytes",
            "pattern-subn-callable-named-nested-conditional-group-exists-replacement-no-match-purged-bytes",
            "module-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-warm-bytes",
            "module-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-warm-bytes",
            "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-purged-bytes",
            "pattern-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-purged-bytes",
            "module-sub-callable-numbered-nested-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
            "module-subn-callable-named-nested-conditional-group-exists-replacement-none-count-negative-count-warm-bytes",
            "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
            "pattern-subn-callable-named-nested-conditional-group-exists-replacement-none-count-negative-count-purged-bytes",
        ),
        expected_patterns={
            r"a(b)?c(?(1)(?(1)d|e)|f)",
            r"a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"zzabcdzz", "zzabcezz", "zzacezz", "zzacfzz"},
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "nested-conditional",
            "replacement",
            "callable",
            "bytes",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="quantified-callable-replacement-str-rows",
        required_syntax_features=(
            "conditionals",
            "quantifiers",
            "callable-replacement",
        ),
        required_categories=("quantified",),
        excluded_categories=(
            "alternation",
            "alternation-heavy",
            "bytes",
            "nested-conditional",
            "nested-group",
            "unsupported",
        ),
        expected_workload_ids=CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS,
        expected_patterns={
            r"a(b)?c(?(1)d|e){2}",
            r"a(?P<word>b)?c(?(word)d|e){2}",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"zzabcddzz", "zzaceezz", "zzabcdezz", "zzacedzz"},
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "quantified",
            "replacement",
            "callable",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="quantified-callable-replacement-bytes-rows",
        required_syntax_features=(
            "pattern-text-model",
            "conditionals",
            "quantifiers",
            "callable-replacement",
        ),
        required_categories=("quantified", "bytes"),
        excluded_categories=(
            "alternation",
            "alternation-heavy",
            "nested-conditional",
            "nested-group",
            "unsupported",
        ),
        expected_workload_ids=CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS,
        expected_patterns={
            r"a(b)?c(?(1)d|e){2}",
            r"a(?P<word>b)?c(?(word)d|e){2}",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={"zzabcddzz", "zzaceezz", "zzabcdezz", "zzacedzz"},
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "quantified",
            "replacement",
            "callable",
            "bytes",
        ),
    ),
    _combined_slice_expectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="quantified-alternation-heavy-constant-replacement-rows",
        required_syntax_features=("conditionals", "alternation", "quantifiers"),
        required_categories=("alternation-heavy", "replacement", "quantified"),
        expected_workload_ids=(
            "module-sub-numbered-conditional-group-exists-quantified-alternation-heavy-replacement-warm-str",
            "module-subn-numbered-conditional-group-exists-quantified-alternation-heavy-replacement-warm-str",
            "pattern-sub-numbered-conditional-group-exists-quantified-alternation-heavy-replacement-purged-str",
            "pattern-subn-numbered-conditional-group-exists-quantified-alternation-heavy-replacement-purged-str",
            "module-sub-named-conditional-group-exists-quantified-alternation-heavy-replacement-warm-str",
            "module-subn-named-conditional-group-exists-quantified-alternation-heavy-replacement-warm-str",
            "pattern-sub-named-conditional-group-exists-quantified-alternation-heavy-replacement-purged-str",
            "pattern-subn-named-conditional-group-exists-quantified-alternation-heavy-replacement-purged-str",
        ),
        expected_patterns={
            r"a(b)?c(?(1)(de|df)|(eg|eh)){2}",
            r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}",
        },
        expected_operations={"module.sub", "module.subn", "pattern.sub", "pattern.subn"},
        expected_haystacks={
            "zzabcdedezz",
            "zzabcdfdfzz",
            "zzacegegzz",
            "zzacehehzz",
        },
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "alternation-heavy",
            "quantified",
            "replacement",
        ),
    ),
)

def relative_manifest_path(path: pathlib.Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def ordered_operations(workloads: list[Workload]) -> list[str]:
    operations: list[str] = []
    for workload in workloads:
        operation = workload.operation
        if operation not in operations:
            operations.append(operation)
    return operations


def source_tree_scorecard_case_ids() -> tuple[str, ...]:
    return tuple(SOURCE_TREE_SCORECARD_EXPECTATIONS)


def _append_unique_workload_ids(
    representative_ids: list[str],
    workload_ids: Iterable[str],
) -> None:
    for workload_id in workload_ids:
        normalized_workload_id = str(workload_id)
        if normalized_workload_id not in representative_ids:
            representative_ids.append(normalized_workload_id)


def _filter_manifest_workload_ids(
    workload_ids: tuple[str, ...] | None,
    *,
    selected_workload_ids: Iterable[str] | None = None,
) -> tuple[str, ...]:
    if workload_ids is None:
        return ()
    if selected_workload_ids is None or not workload_ids:
        return workload_ids

    selected_workload_id_set = {
        str(workload_id) for workload_id in selected_workload_ids
    }
    return tuple(
        workload_id
        for workload_id in workload_ids
        if workload_id in selected_workload_id_set
    )


def source_tree_combined_manifest_representative_measured_workload_ids(
    manifest_id: str,
) -> tuple[str, ...]:
    manifest_expectation = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.get(manifest_id)
    if manifest_expectation is None:
        raise AssertionError(
            f"unknown source-tree combined manifest expectation {manifest_id!r}"
        )

    explicit_workload_ids = manifest_expectation.representative_measured_workload_ids
    if explicit_workload_ids is not None:
        return explicit_workload_ids

    representative_ids: list[str] = []
    shape_expectation = manifest_expectation.shape_expectation
    if shape_expectation is not None:
        _append_unique_workload_ids(
            representative_ids,
            shape_expectation.representative_measured_workload_ids,
        )
    for expectation in SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS:
        if expectation.manifest_id != manifest_id:
            continue
        _append_unique_workload_ids(
            representative_ids,
            expectation.expected_workload_ids,
        )
    return tuple(representative_ids)


def source_tree_combined_fully_measured_manifest_expectation(
    manifest_id: str,
) -> SourceTreeCombinedFullyMeasuredManifestExpectation:
    manifest_expectation = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.get(manifest_id)
    if manifest_expectation is None:
        raise AssertionError(
            f"unknown source-tree combined manifest expectation {manifest_id!r}"
        )

    fully_measured_expectation = manifest_expectation.fully_measured_expectation
    if fully_measured_expectation is None:
        raise AssertionError(
            "source-tree combined manifest "
            f"{manifest_id!r} does not define a fully measured contract"
        )
    return fully_measured_expectation


def source_tree_combined_fully_measured_manifest_ids(
    coverage_group: str | None = None,
) -> tuple[str, ...]:
    return tuple(
        manifest_id
        for manifest_id, manifest_expectation in (
            SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.items()
        )
        if manifest_expectation.fully_measured_expectation is not None
        and (
            coverage_group is None
            or manifest_expectation.fully_measured_expectation.coverage_group
            == coverage_group
        )
    )


def _source_tree_manifest_known_gap_count(
    manifest_expectation: SourceTreeCombinedManifestExpectationDefinition,
    *,
    selected_workload_ids: Iterable[str] | None = None,
) -> int:
    return len(
        _filter_manifest_workload_ids(
            manifest_expectation.known_gap_workload_ids,
            selected_workload_ids=selected_workload_ids,
        )
    )


def _source_tree_manifest_representative_measured_workload_ids(
    manifest_expectation: SourceTreeCombinedManifestExpectationDefinition,
    *,
    selected_workload_ids: Iterable[str] | None = None,
) -> tuple[str, ...]:
    return _filter_manifest_workload_ids(
        manifest_expectation.representative_measured_workload_ids,
        selected_workload_ids=selected_workload_ids,
    )


def _source_tree_manifest_representative_known_gap_workload_ids(
    manifest_expectation: SourceTreeCombinedManifestExpectationDefinition,
    *,
    selected_workload_ids: Iterable[str] | None = None,
) -> tuple[str, ...]:
    return _filter_manifest_workload_ids(
        manifest_expectation.representative_known_gap_workload_ids,
        selected_workload_ids=selected_workload_ids,
    )


def _public_source_tree_manifest_expectation(
    manifest_id: str,
    *,
    selected_workload_ids: Iterable[str] | None = None,
) -> SourceTreeManifestExpectation:
    manifest_expectation = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.get(manifest_id)
    if manifest_expectation is None:
        raise AssertionError(
            f"unknown source-tree combined manifest expectation {manifest_id!r}"
        )
    return SourceTreeManifestExpectation(
        known_gap_count=_source_tree_manifest_known_gap_count(
            manifest_expectation,
            selected_workload_ids=selected_workload_ids,
        ),
        representative_measured_workload_ids=(
            _source_tree_manifest_representative_measured_workload_ids(
                manifest_expectation,
                selected_workload_ids=selected_workload_ids,
            )
        ),
        representative_known_gap_workload_ids=(
            _source_tree_manifest_representative_known_gap_workload_ids(
                manifest_expectation,
                selected_workload_ids=selected_workload_ids,
            )
        ),
    )


def _single_manifest_scorecard_fallback_expectation(
    manifest_id: str,
    *,
    case_definition: _SourceTreeScorecardDefinition,
    manifest_known_gap_counts: dict[str, int],
    selected_workload_ids: Iterable[str] | None = None,
) -> SourceTreeManifestExpectation:
    selected_workload_id_set = (
        {str(workload_id) for workload_id in selected_workload_ids}
        if selected_workload_ids is not None
        else None
    )

    def _filter_case_workload_ids(workload_ids: tuple[str, ...]) -> tuple[str, ...]:
        if selected_workload_id_set is None:
            return workload_ids
        return tuple(
            workload_id
            for workload_id in workload_ids
            if workload_id in selected_workload_id_set
        )

    return SourceTreeManifestExpectation(
        known_gap_count=manifest_known_gap_counts[manifest_id],
        representative_measured_workload_ids=_filter_case_workload_ids(
            case_definition.representative_measured_workload_ids
        ),
        representative_known_gap_workload_ids=_filter_case_workload_ids(
            case_definition.representative_known_gap_workload_ids
        ),
    )


def _source_tree_manifest_known_gap_counts(
    manifests: list[BenchmarkManifest],
    case_definition: _SourceTreeScorecardDefinition,
    *,
    selection_mode: str,
) -> dict[str, int]:
    known_gap_counts: dict[str, int] = {}
    for manifest in manifests:
        manifest_id = manifest.manifest_id
        manifest_expectation = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.get(manifest_id)
        if manifest_expectation is None:
            raise AssertionError(
                "missing known-gap expectation for source-tree scorecard manifest "
                f"{manifest_id!r}"
            )
        known_gap_counts[manifest_id] = _source_tree_manifest_known_gap_count(
            manifest_expectation,
            selected_workload_ids=_selected_source_tree_manifest_workload_ids(
                manifest,
                selection_mode=selection_mode,
            ),
        )
    return known_gap_counts


def _selected_source_tree_manifest_workload_ids(
    manifest: BenchmarkManifest,
    *,
    selection_mode: str,
) -> tuple[str, ...]:
    return tuple(
        workload.workload_id
        for workload in manifest.selected_workloads(selection_mode=selection_mode)
    )


def _flatten_manifest_workloads(manifests: list[BenchmarkManifest]) -> list[Workload]:
    return [workload for manifest in manifests for workload in manifest.workloads]


def _source_tree_benchmark_common_case_kwargs(
    *,
    manifests: list[BenchmarkManifest],
    workloads: list[Workload],
    selection_mode: str,
    manifest_known_gap_counts: dict[str, int] | None = None,
    expected_summary: dict[str, int] | None = None,
) -> dict[str, Any]:
    workload_payloads = [workload_to_payload(workload) for workload in workloads]
    return {
        "expected_adapter": (
            "rebar.module-surface"
            if any(workload.family == "module" for workload in workloads)
            else "rebar.compile"
        ),
        "expected_phase": determine_phase(workload_payloads),
        "expected_runner_version": determine_runner_version(workload_payloads),
        "expected_summary": (
            expected_summary
            if expected_summary is not None
            else expected_summary_for_manifests(
                manifests,
                selection_mode=selection_mode,
                manifest_known_gap_counts=manifest_known_gap_counts,
            )
        ),
        "manifests": manifests,
        "selection_mode": selection_mode,
    }


def source_tree_scorecard_case(case_id: str) -> SourceTreeScorecardCase:
    if case_id not in SOURCE_TREE_SCORECARD_EXPECTATIONS:
        raise AssertionError(f"unknown source-tree scorecard case {case_id!r}")

    case_definition = SOURCE_TREE_SCORECARD_EXPECTATIONS[case_id]
    manifest_ids = case_definition.manifest_ids
    manifest_records = manifest_records_by_id(published_benchmark_manifests())
    manifests: list[BenchmarkManifest] = []
    for manifest_id in manifest_ids:
        try:
            manifests.append(manifest_records[manifest_id])
        except KeyError as exc:
            raise AssertionError(
                f"unknown benchmark manifest id {manifest_id!r}"
            ) from exc
    selected_workloads = select_workloads(
        _flatten_manifest_workloads(manifests),
        smoke_only=case_definition.selection_mode == "smoke",
    )
    manifest_known_gap_counts = _source_tree_manifest_known_gap_counts(
        manifests,
        case_definition,
        selection_mode=case_definition.selection_mode,
    )
    manifest_expectations: dict[str, SourceTreeManifestExpectation] = {}
    for manifest in manifests:
        manifest_id = manifest.manifest_id
        selected_workload_ids = _selected_source_tree_manifest_workload_ids(
            manifest,
            selection_mode=case_definition.selection_mode,
        )
        manifest_expectations[manifest_id] = (
            _public_source_tree_manifest_expectation(
                manifest_id,
                selected_workload_ids=selected_workload_ids,
            )
            if manifest_id in SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS
            else _single_manifest_scorecard_fallback_expectation(
                manifest_id,
                case_definition=case_definition,
                manifest_known_gap_counts=manifest_known_gap_counts,
                selected_workload_ids=selected_workload_ids,
            )
        )
    representative_measured_workload_ids = (
        case_definition.representative_measured_workload_ids
    )
    representative_known_gap_workload_ids = (
        case_definition.representative_known_gap_workload_ids
    )
    if (
        len(manifest_ids) == 1
        and manifest_ids[0] in SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS
    ):
        manifest_expectation = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_ids[0]]
        if not representative_measured_workload_ids:
            representative_measured_workload_ids = (
                source_tree_combined_manifest_representative_measured_workload_ids(
                    manifest_ids[0]
                )
            )
        if not representative_known_gap_workload_ids:
            representative_known_gap_workload_ids = (
                _source_tree_manifest_representative_known_gap_workload_ids(
                    manifest_expectation
                )
            )
    common_case_kwargs = _source_tree_benchmark_common_case_kwargs(
        manifests=manifests,
        workloads=selected_workloads,
        selection_mode=case_definition.selection_mode,
        manifest_known_gap_counts=manifest_known_gap_counts,
    )
    return SourceTreeScorecardCase(
        **common_case_kwargs,
        case_id=case_id,
        manifest_expectations=manifest_expectations,
        representative_measured_workload_ids=representative_measured_workload_ids,
        representative_known_gap_workload_ids=representative_known_gap_workload_ids,
        expected_first_deferred=case_definition.expected_first_deferred,
        expected_workload_order=case_definition.expected_workload_order,
    )


def source_tree_combined_target_manifest_ids() -> tuple[str, ...]:
    target_manifest_ids: list[str] = []
    missing_expectations: list[str] = []
    for manifest in published_benchmark_manifests():
        manifest_id = manifest.manifest_id
        manifest_expectation = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.get(
            manifest_id
        )
        if manifest_expectation is None:
            missing_expectations.append(manifest_id)
            continue
        if manifest_expectation.exclude_from_combined_targets:
            continue
        target_manifest_ids.append(manifest_id)
    if missing_expectations:
        raise AssertionError(
            "source-tree combined manifest expectations drifted from the published full-suite selector: "
            f"missing {sorted(missing_expectations)}"
        )
    return tuple(target_manifest_ids)


def _selected_source_tree_manifests_for_target_manifest(
    target_manifest_id: str,
) -> list[BenchmarkManifest]:
    selected_manifests: list[BenchmarkManifest] = []
    published_manifests = published_benchmark_manifests()
    regression_manifest = next(
        (
            manifest
            for manifest in published_manifests
            if manifest.manifest_id == "regression-matrix"
        ),
        None,
    )
    for manifest in published_manifests:
        manifest_id = manifest.manifest_id
        if manifest_id == "regression-matrix":
            continue
        selected_manifests.append(manifest)
        if manifest_id == target_manifest_id:
            break
    else:
        raise AssertionError(
            f"target manifest {target_manifest_id!r} is not in the published full-suite selector"
        )
    if target_manifest_id != "module-boundary":
        if regression_manifest is None:
            raise AssertionError(
                "the published full-suite selector is missing the regression-matrix manifest"
            )
        selected_manifests.append(regression_manifest)
    return selected_manifests


def expected_summary_for_manifests(
    manifests: list[BenchmarkManifest],
    *,
    selection_mode: str,
    manifest_known_gap_counts: dict[str, int] | None = None,
) -> dict[str, int]:
    workloads: list[Workload] = []
    regression_workloads = 0
    selected_manifest_ids: list[str] = []
    for manifest in manifests:
        manifest_id = manifest.manifest_id
        selected_manifest_workloads = manifest.selected_workloads(
            selection_mode=selection_mode
        )
        if selected_manifest_workloads:
            selected_manifest_ids.append(manifest_id)
        if manifest_id == "regression-matrix":
            regression_workloads += len(selected_manifest_workloads)
        workloads.extend(selected_manifest_workloads)
    known_gap_counts = (
        manifest_known_gap_counts
        if manifest_known_gap_counts is not None
        else {
            manifest.manifest_id: _source_tree_manifest_known_gap_count(
                SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest.manifest_id],
                selected_workload_ids=_selected_source_tree_manifest_workload_ids(
                    manifest,
                    selection_mode=selection_mode,
                ),
            )
            for manifest in manifests
            if manifest.manifest_id in SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS
        }
    )
    known_gap_count = sum(
        known_gap_counts.get(manifest_id, 0) for manifest_id in selected_manifest_ids
    )
    return {
        "known_gap_count": known_gap_count,
        "measured_workloads": len(workloads) - known_gap_count,
        "module_workloads": sum(1 for workload in workloads if workload.family == "module"),
        "parser_workloads": sum(1 for workload in workloads if workload.family == "parser"),
        "regression_workloads": regression_workloads,
        "total_workloads": len(workloads),
    }


def representative_measured_workload_ids(
    scorecard: dict[str, Any],
    manifest: BenchmarkManifest,
    *,
    extra_workload_ids: tuple[str, ...] = (),
) -> list[str]:
    manifest_id = manifest.manifest_id
    representative_ids: list[str] = []
    manifest_expectation = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.get(manifest_id)
    if manifest_expectation is not None:
        _append_unique_workload_ids(
            representative_ids,
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            ),
        )
    _append_unique_workload_ids(representative_ids, extra_workload_ids)
    for operation in ordered_operations(manifest.workloads):
        for workload in scorecard["workloads"]:
            if workload["manifest_id"] != manifest_id:
                continue
            if workload["operation"] != operation or workload["status"] != "measured":
                continue
            workload_id = str(workload["id"])
            if workload_id not in representative_ids:
                representative_ids.append(workload_id)
            break
    return representative_ids


def source_tree_combined_case(target_manifest_id: str) -> SourceTreeCombinedCase:
    manifests = _selected_source_tree_manifests_for_target_manifest(target_manifest_id)
    workloads = _flatten_manifest_workloads(manifests)
    target_manifest = next(
        manifest for manifest in manifests if manifest.manifest_id == target_manifest_id
    )
    common_case_kwargs = _source_tree_benchmark_common_case_kwargs(
        manifests=manifests,
        workloads=workloads,
        selection_mode="full",
    )
    return SourceTreeCombinedCase(
        **common_case_kwargs,
        manifest_expectation=_public_source_tree_manifest_expectation(target_manifest_id),
        manifest_id=target_manifest_id,
        target_manifest=target_manifest,
    )


@cache
def source_tree_combined_manifest_shape_expectation(
    manifest_id: str,
) -> SourceTreeCombinedManifestShapeExpectation:
    manifest_expectation = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.get(manifest_id)
    if manifest_expectation is None:
        raise AssertionError(
            f"unknown source-tree combined manifest expectation {manifest_id!r}"
        )
    shape_expectation = manifest_expectation.shape_expectation
    if shape_expectation is None:
        raise AssertionError(
            "source-tree combined manifest "
            f"{manifest_id!r} does not define shared shape expectations"
        )
    return shape_expectation


def source_tree_combined_slice_manifest_ids() -> tuple[str, ...]:
    manifest_ids_with_expectations = {
        expectation.manifest_id for expectation in SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS
    }
    combined_target_ids = source_tree_combined_target_manifest_ids()
    missing_manifest_ids = manifest_ids_with_expectations - set(combined_target_ids)
    if missing_manifest_ids:
        raise AssertionError(
            "source-tree combined slice expectations reference manifest ids outside the "
            f"published combined selector: {sorted(missing_manifest_ids)}"
        )
    return tuple(
        manifest_id
        for manifest_id in combined_target_ids
        if manifest_id in manifest_ids_with_expectations
    )


def source_tree_combined_slice_derived_manifest_ids() -> tuple[str, ...]:
    return tuple(
        manifest_id
        for manifest_id in source_tree_combined_slice_manifest_ids()
        if SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
            manifest_id
        ].representative_measured_workload_ids
        is None
        and SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id].shape_expectation
        is None
    )


def source_tree_combined_slice_expectations(
    manifest_id: str,
) -> tuple[SourceTreeCombinedSliceExpectation, ...]:
    expectations = tuple(
        expectation
        for expectation in SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS
        if expectation.manifest_id == manifest_id
    )
    if not expectations:
        raise AssertionError(
            f"unknown source-tree combined slice expectation manifest {manifest_id!r}"
        )
    return expectations


@cache
def _conditional_group_exists_callable_str_slice_workloads() -> tuple[Workload, ...]:
    expected_workload_ids = tuple(
        workload_id
        for expectation in _conditional_group_exists_callable_replacement_expectations()
        for workload_id in expectation.expected_workload_ids
        if not workload_id.endswith("-bytes")
    )
    return benchmark_test_support.live_manifest_workloads(
        BENCHMARK_WORKLOADS_ROOT / "conditional_group_exists_boundary.py",
        expected_workload_ids,
    )


@cache
def _conditional_group_exists_callable_bytes_slice_workloads() -> tuple[Workload, ...]:
    expected_workload_ids = tuple(
        workload_id
        for expectation in _conditional_group_exists_callable_replacement_expectations()
        for workload_id in expectation.expected_workload_ids
        if workload_id.endswith("-bytes")
    )
    return benchmark_test_support.live_manifest_workloads(
        BENCHMARK_WORKLOADS_ROOT / "conditional_group_exists_boundary.py",
        expected_workload_ids,
    )


def _conditional_group_exists_quantified_callable_str_workloads() -> tuple[Workload, ...]:
    expectation = _conditional_group_exists_quantified_callable_replacement_expectation()
    return benchmark_test_support.live_manifest_workloads(
        BENCHMARK_WORKLOADS_ROOT / "conditional_group_exists_boundary.py",
        expectation.expected_workload_ids,
    )


def _conditional_group_exists_nested_callable_str_workloads() -> tuple[Workload, ...]:
    expectation = _conditional_group_exists_nested_callable_replacement_expectation()
    return benchmark_test_support.live_manifest_workloads(
        BENCHMARK_WORKLOADS_ROOT / "conditional_group_exists_boundary.py",
        expectation.expected_workload_ids,
    )


@cache
def _conditional_group_exists_nested_callable_bytes_workloads() -> tuple[Workload, ...]:
    expectation = _conditional_group_exists_nested_callable_bytes_replacement_expectation()
    return benchmark_test_support.live_manifest_workloads(
        BENCHMARK_WORKLOADS_ROOT / "conditional_group_exists_boundary.py",
        expectation.expected_workload_ids,
    )


@cache
def _conditional_group_exists_quantified_callable_bytes_workloads() -> tuple[Workload, ...]:
    expectation = (
        _conditional_group_exists_quantified_callable_bytes_replacement_expectation()
    )
    return benchmark_test_support.live_manifest_workloads(
        BENCHMARK_WORKLOADS_ROOT / "conditional_group_exists_boundary.py",
        expectation.expected_workload_ids,
    )


@cache
def _conditional_group_exists_alternation_callable_bytes_workloads() -> tuple[Workload, ...]:
    return benchmark_test_support.live_manifest_workloads(
        BENCHMARK_WORKLOADS_ROOT / "conditional_group_exists_boundary.py",
        collection_replacement_support.CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS,
    )


def _split_workload_ids_by_text_model(
    workload_ids: tuple[str, ...],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    return (
        tuple(
            workload_id
            for workload_id in workload_ids
            if not workload_id.endswith("-bytes")
        ),
        tuple(
            workload_id
            for workload_id in workload_ids
            if workload_id.endswith("-bytes")
        ),
    )


def _selected_workload_ids(
    workloads: Iterable[Workload],
    *,
    text_model: str,
    required_categories: tuple[str, ...],
    excluded_categories: tuple[str, ...] = (),
) -> tuple[str, ...]:
    return tuple(
        workload.workload_id
        for workload in workloads
        if workload.text_model == text_model
        and all(category in workload.categories for category in required_categories)
        and all(category not in workload.categories for category in excluded_categories)
    )


def _mirrored_bytes_workload_ids(str_workload_ids: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(
        f"{workload_id.removesuffix('-str')}-bytes" for workload_id in str_workload_ids
    )


def _conditional_group_exists_template_replacement_expectation(
) -> SourceTreeCombinedSliceExpectation:
    return next(
        expectation
        for expectation in source_tree_combined_slice_expectations(
            "conditional-group-exists-boundary"
        )
        if expectation.slice_id == "minimal-template-replacement-rows"
    )


def _conditional_group_exists_callable_replacement_expectations(
) -> tuple[SourceTreeCombinedSliceExpectation, ...]:
    expected_slice_ids = (
        "minimal-callable-replacement-rows",
        "minimal-callable-replacement-exception-rows",
        "minimal-callable-replacement-none-count-exception-rows",
        "alternation-heavy-callable-replacement-rows",
    )
    expectations = tuple(
        expectation
        for expectation in source_tree_combined_slice_expectations(
            "conditional-group-exists-boundary"
        )
        if expectation.slice_id in expected_slice_ids
    )
    actual_slice_ids = tuple(expectation.slice_id for expectation in expectations)
    if actual_slice_ids != expected_slice_ids:
        raise AssertionError(
            "conditional callable replacement slice expectations drifted: "
            f"expected {expected_slice_ids!r}, got {actual_slice_ids!r}"
        )
    return expectations


def _conditional_group_exists_alternation_callable_replacement_expectation(
) -> SourceTreeCombinedSliceExpectation:
    return next(
        expectation
        for expectation in source_tree_combined_slice_expectations(
            "conditional-group-exists-boundary"
        )
        if expectation.slice_id == "alternation-heavy-callable-replacement-rows"
    )


def _conditional_group_exists_nested_callable_replacement_expectation(
) -> SourceTreeCombinedSliceExpectation:
    return next(
        expectation
        for expectation in source_tree_combined_slice_expectations(
            "conditional-group-exists-boundary"
        )
        if expectation.slice_id == "nested-callable-replacement-str-rows"
    )


def _conditional_group_exists_nested_callable_bytes_replacement_expectation(
) -> SourceTreeCombinedSliceExpectation:
    return next(
        expectation
        for expectation in source_tree_combined_slice_expectations(
            "conditional-group-exists-boundary"
        )
        if expectation.slice_id == "nested-callable-replacement-bytes-rows"
    )


def _conditional_group_exists_quantified_callable_replacement_expectation(
) -> SourceTreeCombinedSliceExpectation:
    return next(
        expectation
        for expectation in source_tree_combined_slice_expectations(
            "conditional-group-exists-boundary"
        )
        if expectation.slice_id == "quantified-callable-replacement-str-rows"
    )


def _conditional_group_exists_quantified_callable_bytes_replacement_expectation(
) -> SourceTreeCombinedSliceExpectation:
    return next(
        expectation
        for expectation in source_tree_combined_slice_expectations(
            "conditional-group-exists-boundary"
        )
        if expectation.slice_id == "quantified-callable-replacement-bytes-rows"
    )


CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS = (
    collection_replacement_support.CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS
)
CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS = (
    collection_replacement_support.CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS
)
CONDITIONAL_GROUP_EXISTS_TEMPLATE_ROUND_TRIP_WORKLOAD_IDS = (
    collection_replacement_support.CONDITIONAL_GROUP_EXISTS_TEMPLATE_ROUND_TRIP_WORKLOAD_IDS
)
CONDITIONAL_GROUP_EXISTS_CALLABLE_BYTES_WORKLOAD_IDS = (
    collection_replacement_support.CONDITIONAL_GROUP_EXISTS_CALLABLE_BYTES_WORKLOAD_IDS
)
CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS = (
    collection_replacement_support.CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS
)
CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS = (
    collection_replacement_support.CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS
)
CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_IDS = (
    collection_replacement_support.CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_IDS
)
CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS = (
    collection_replacement_support.CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS
)
CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS = (
    collection_replacement_support.CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS
)
CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS = (
    collection_replacement_support.CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS
)


def _conditional_group_exists_nested_callable_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.manifest_id != "conditional-group-exists-callable-replacement-workflows":
        return None
    if "nested" not in case.categories:
        return None
    if any(category in case.categories for category in ("quantified", "alternation")):
        return None
    if case.operation not in {"module_call", "pattern_call"}:
        return None
    if case.helper not in {"sub", "subn"}:
        return None
    if case.kwargs or case.use_compiled_pattern:
        return None
    replacement_signature = callable_match_group_signature(
        case_replacement_argument(case)
    )
    if replacement_signature is None:
        return None
    count_index = 3 if case.operation == "module_call" else 2
    args = [case_text_argument(case)]
    if len(case.args) > count_index:
        args.append(case.args[count_index])
    operation_prefix = "module" if case.operation == "module_call" else "pattern"
    return (
        f"{operation_prefix}.{case.helper}",
        case_pattern(case),
        replacement_signature,
        benchmark_test_support.freeze_signature_value(args),
        "exception" in case.categories,
        "no-match" in case.categories,
        case.flags or 0,
        case.text_model or "str",
    )


def _conditional_group_exists_nested_callable_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    expected_workload_ids = (
        CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS
        + CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS
    )
    if workload.workload_id not in expected_workload_ids:
        raise AssertionError(
            "unexpected conditional nested callable workload "
            f"{workload.workload_id!r}"
        )
    replacement_signature = callable_match_group_signature(
        workload.replacement_payload()
    )
    if replacement_signature is None:
        raise AssertionError(
            "expected callable_match_group replacement for nested "
            f"conditional workload {workload.workload_id!r}"
        )
    args: list[object] = [workload.haystack_payload()]
    if workload.count != 0:
        args.append(workload.count_argument())
    return (
        workload.operation,
        workload.pattern_payload(),
        replacement_signature,
        benchmark_test_support.freeze_signature_value(args),
        workload.expected_exception is not None,
        "no-match" in workload.categories,
        workload.flags,
        workload.text_model,
    )


def _conditional_group_exists_quantified_callable_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.manifest_id != "conditional-group-exists-callable-replacement-workflows":
        return None
    if "quantified" not in case.categories:
        return None
    if any(category in case.categories for category in ("alternation", "nested")):
        return None
    if case.operation not in {"module_call", "pattern_call"}:
        return None
    if case.helper not in {"sub", "subn"}:
        return None
    if case.kwargs or case.use_compiled_pattern:
        return None
    replacement_signature = callable_match_group_signature(
        case_replacement_argument(case)
    )
    if replacement_signature is None:
        return None
    count_index = 3 if case.operation == "module_call" else 2
    args = [case_text_argument(case)]
    if len(case.args) > count_index:
        count = case.args[count_index]
        if count is None:
            pass
        elif type(count) is int:
            args.append(count)
        else:
            return None
    operation_prefix = "module" if case.operation == "module_call" else "pattern"
    return (
        f"{operation_prefix}.{case.helper}",
        case_pattern(case),
        replacement_signature,
        benchmark_test_support.freeze_signature_value(args),
        "exception" in case.categories,
        "no-match" in case.categories,
        case.flags or 0,
        case.text_model or "str",
    )


def _conditional_group_exists_quantified_callable_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    expected_workload_ids = (
        CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS
        + CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS
    )
    if workload.workload_id not in expected_workload_ids:
        raise AssertionError(
            "unexpected conditional quantified callable workload "
            f"{workload.workload_id!r}"
        )
    replacement_signature = callable_match_group_signature(
        workload.replacement_payload()
    )
    if replacement_signature is None:
        raise AssertionError(
            "expected callable_match_group replacement for quantified "
            f"conditional workload {workload.workload_id!r}"
        )
    args = [workload.haystack_payload()]
    if workload.count:
        args.append(workload.count_argument())
    return (
        workload.operation,
        workload.pattern_payload(),
        replacement_signature,
        benchmark_test_support.freeze_signature_value(args),
        workload.expected_exception is not None,
        "no-match" in workload.categories,
        workload.flags,
        workload.text_model,
    )


def _workload_matches_source_tree_combined_slice(
    workload: Workload,
    expectation: SourceTreeCombinedSliceExpectation,
) -> bool:
    workload_id = workload.workload_id
    required_id_suffix = expectation.required_id_suffix
    if required_id_suffix is not None and not workload_id.endswith(required_id_suffix):
        return False

    syntax_features = set(workload.syntax_features)
    categories = set(workload.categories)
    return (
        set(expectation.required_syntax_features).issubset(syntax_features)
        and syntax_features.isdisjoint(expectation.excluded_syntax_features)
        and set(expectation.required_categories).issubset(categories)
        and categories.isdisjoint(expectation.excluded_categories)
    )


def select_source_tree_combined_slice_rows(
    manifest: BenchmarkManifest,
    expectation: SourceTreeCombinedSliceExpectation,
) -> list[Workload]:
    return [
        workload
        for workload in manifest.workloads
        if _workload_matches_source_tree_combined_slice(workload, expectation)
    ]


def _compile_search_fullmatch_case_signature(
    case: Any,
    *,
    pattern: Callable[[], Any],
) -> tuple[Any, ...] | None:
    kwargs_signature = benchmark_test_support.freeze_signature_value(case.serialized_kwargs())
    flags = case.flags or 0
    text_model = case.text_model or "str"

    if case.operation == "compile":
        return ("module.compile", pattern(), (), kwargs_signature, flags, text_model)
    if case.operation == "module_call" and case.helper == "search":
        return (
            "module.search",
            None,
            benchmark_test_support.freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    if case.operation == "pattern_call" and case.helper == "fullmatch":
        return (
            "pattern.fullmatch",
            pattern(),
            benchmark_test_support.freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    return None


def _compile_search_fullmatch_workload_signature(
    workload: Any,
    *,
    pattern: Callable[[], Any],
    module_search_args: Callable[[], tuple[Any, ...]],
    pattern_fullmatch_args: Callable[[], tuple[Any, ...]],
    error_label: str,
) -> tuple[Any, ...]:
    if workload.operation == "module.compile":
        return (
            "module.compile",
            pattern(),
            (),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation == "module.search":
        return (
            "module.search",
            None,
            module_search_args(),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation == "pattern.fullmatch":
        return (
            "pattern.fullmatch",
            pattern(),
            pattern_fullmatch_args(),
            (),
            workload.flags,
            workload.text_model,
        )
    raise AssertionError(
        f"unexpected {error_label} workload operation {workload.operation!r}"
    )


def _optional_group_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or case.helper != "search":
        return None

    kwargs_signature = benchmark_test_support.freeze_signature_value(case.serialized_kwargs())
    flags = case.flags or 0
    text_model = case.text_model or "str"
    return (
        "module.search",
        None,
        benchmark_test_support.freeze_signature_value(case.serialized_args()),
        kwargs_signature,
        flags,
        text_model,
    )


def _optional_group_workload_signature(workload: Any) -> tuple[Any, ...]:
    if workload.operation != "module.search":
        raise AssertionError(
            "unexpected optional-group benchmark workload operation "
            f"{workload.operation!r}"
        )

    return (
        "module.search",
        None,
        benchmark_test_support.freeze_signature_value([workload.pattern, workload.haystack]),
        (),
        workload.flags,
        workload.text_model,
    )


def _is_optional_group_conditional_workload(workload: Any) -> bool:
    return workload.workload_id == _OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID


def _nested_group_correctness_case_signature(case: Any) -> tuple[Any, ...] | None:
    return _compile_search_fullmatch_case_signature(
        case,
        pattern=lambda: case.pattern,
    )


def _nested_group_workload_signature(workload: Any) -> tuple[Any, ...]:
    return _compile_search_fullmatch_workload_signature(
        workload,
        pattern=lambda: workload.pattern,
        module_search_args=lambda: (workload.pattern, workload.haystack),
        pattern_fullmatch_args=lambda: (workload.haystack,),
        error_label="nested-group benchmark",
    )


def _counted_repeat_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    return _compile_search_fullmatch_case_signature(
        case,
        pattern=lambda: case.pattern_payload(),
    )


def _counted_repeat_workload_signature(workload: Any) -> tuple[Any, ...]:
    return _compile_search_fullmatch_workload_signature(
        workload,
        pattern=lambda: workload.pattern_payload(),
        module_search_args=lambda: benchmark_test_support.freeze_signature_value(
            [
                workload.pattern_payload(),
                workload.haystack_payload(),
            ]
        ),
        pattern_fullmatch_args=lambda: benchmark_test_support.freeze_signature_value(
            [workload.haystack_payload()]
        ),
        error_label="counted-repeat benchmark",
    )


def _is_non_alternation_counted_repeat_workload(workload: Any) -> bool:
    return workload.operation in {
        "module.compile",
        "module.search",
        "pattern.fullmatch",
    } and "|" not in workload.pattern


def _grouped_alternation_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    kwargs_signature = benchmark_test_support.freeze_signature_value(case.serialized_kwargs())
    flags = case.flags or 0
    text_model = case.text_model or "str"

    if case.operation == "compile":
        return ("module.compile", case.pattern, (), kwargs_signature, flags, text_model)
    if case.operation == "module_call" and case.helper in {"search", "sub", "subn"}:
        return (
            f"module.{case.helper}",
            None,
            benchmark_test_support.freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    if case.operation == "pattern_call" and case.helper in {"fullmatch", "sub", "subn"}:
        return (
            f"pattern.{case.helper}",
            case.pattern,
            benchmark_test_support.freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    return None


def _grouped_alternation_workload_args(workload: Any) -> tuple[Any, ...]:
    if workload.operation == "module.compile":
        return ()
    if workload.operation == "module.search":
        return benchmark_test_support.freeze_signature_value([workload.pattern, workload.haystack])
    if workload.operation == "pattern.fullmatch":
        return benchmark_test_support.freeze_signature_value([workload.haystack])
    if workload.operation in {"module.sub", "module.subn"}:
        args = [workload.pattern, workload.replacement, workload.haystack]
        if workload.count:
            args.append(workload.count)
        return benchmark_test_support.freeze_signature_value(args)
    if workload.operation in {"pattern.sub", "pattern.subn"}:
        args = [workload.replacement, workload.haystack]
        if workload.count:
            args.append(workload.count)
        return benchmark_test_support.freeze_signature_value(args)
    raise AssertionError(
        f"unexpected grouped-alternation benchmark workload operation {workload.operation!r}"
    )


def _grouped_alternation_workload_signature(workload: Any) -> tuple[Any, ...]:
    if workload.operation == "module.compile":
        return (
            "module.compile",
            workload.pattern,
            (),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation in {"module.search", "module.sub", "module.subn"}:
        return (
            workload.operation,
            None,
            _grouped_alternation_workload_args(workload),
            (),
            workload.flags,
            workload.text_model,
        )
    if workload.operation in {"pattern.fullmatch", "pattern.sub", "pattern.subn"}:
        return (
            workload.operation,
            workload.pattern,
            _grouped_alternation_workload_args(workload),
            (),
            workload.flags,
            workload.text_model,
        )
    raise AssertionError(
        f"unexpected grouped-alternation benchmark workload operation {workload.operation!r}"
    )


def _grouped_alternation_replacement_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    kwargs_signature = benchmark_test_support.freeze_signature_value(case.serialized_kwargs())
    flags = case.flags or 0
    text_model = case.text_model or "str"

    if case.operation == "module_call" and case.helper in {"sub", "subn"}:
        return (
            f"module.{case.helper}",
            case.pattern,
            benchmark_test_support.freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    if case.operation == "pattern_call" and case.helper in {"sub", "subn"}:
        return (
            f"pattern.{case.helper}",
            case.pattern,
            benchmark_test_support.freeze_signature_value(case.serialized_args()),
            kwargs_signature,
            flags,
            text_model,
        )
    return None


_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS = (
    benchmark_test_support._CompiledPatternModuleCompileSuccessOwnerSpec(
        anchor_definition_name=(
            "module-workflow-compiled-pattern-module-compile-literal-success"
        ),
        allowed_patterns=(
            benchmark_test_support._COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS
        ),
        anchor_expectations=(
            (
                "module-compile-literal-warm-str-compiled-pattern",
                ("workflow-module-compile-str-compiled-pattern",),
            ),
            (
                "module-compile-literal-purged-bytes-compiled-pattern",
                ("workflow-module-compile-bytes-compiled-pattern",),
            ),
        ),
        expected_anchor_pairs=(
            (
                "module-compile-literal-warm-str-compiled-pattern-contract",
                "workflow-module-compile-str-compiled-pattern",
            ),
            (
                "module-compile-literal-purged-bytes-compiled-pattern-contract",
                "workflow-module-compile-bytes-compiled-pattern",
            ),
        ),
    ),
    benchmark_test_support._CompiledPatternModuleCompileSuccessOwnerSpec(
        anchor_definition_name=(
            "module-workflow-compiled-pattern-module-compile-named-group-success"
        ),
        allowed_patterns=(
            benchmark_test_support._COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS
        ),
        anchor_expectations=(
            (
                "module-compile-named-group-warm-str-compiled-pattern",
                ("workflow-module-compile-str-compiled-pattern-named-group",),
            ),
            (
                "module-compile-named-group-purged-bytes-compiled-pattern",
                ("workflow-module-compile-bytes-compiled-pattern-named-group",),
            ),
        ),
        expected_anchor_pairs=(
            (
                "module-compile-named-group-warm-str-compiled-pattern-contract",
                "workflow-module-compile-str-compiled-pattern-named-group",
            ),
            (
                "module-compile-named-group-purged-bytes-compiled-pattern-contract",
                "workflow-module-compile-bytes-compiled-pattern-named-group",
            ),
        ),
    ),
)
_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS = (
    benchmark_test_support._CompiledPatternModuleCompileKeywordOwnerSpec(
        case_id="int-zero",
        anchor_definition_name=(
            "module-workflow-compiled-pattern-module-compile-flags-int-zero-keyword"
        ),
        keyword_signature=(
            benchmark_test_support._COMPILED_PATTERN_MODULE_COMPILE_INT_ZERO_KEYWORD_SIGNATURE
        ),
        allowed_patterns=(
            benchmark_test_support._COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS
        ),
        anchor_expectations=(
            (
                "module-compile-flags-int-zero-warm-str-compiled-pattern",
                ("workflow-module-compile-flags-int-zero-str-compiled-pattern",),
            ),
            (
                "module-compile-flags-int-zero-purged-bytes-compiled-pattern",
                ("workflow-module-compile-flags-int-zero-bytes-compiled-pattern",),
            ),
        ),
        contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_keyword_contract.py"
        ),
        anchor_contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_keyword_anchor_contract.py"
        ),
        expected_anchor_pairs=(
            (
                "module-compile-flags-int-zero-warm-str-compiled-pattern-contract",
                "workflow-module-compile-flags-int-zero-str-compiled-pattern",
            ),
            (
                "module-compile-flags-int-zero-purged-bytes-compiled-pattern-contract",
                "workflow-module-compile-flags-int-zero-bytes-compiled-pattern",
            ),
        ),
    ),
    benchmark_test_support._CompiledPatternModuleCompileKeywordOwnerSpec(
        case_id="int-zero-named-group",
        anchor_definition_name=(
            "module-workflow-compiled-pattern-module-compile-flags-int-zero-"
            "keyword-named-group"
        ),
        keyword_signature=(
            benchmark_test_support._COMPILED_PATTERN_MODULE_COMPILE_INT_ZERO_KEYWORD_SIGNATURE
        ),
        allowed_patterns=(
            benchmark_test_support._COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS
        ),
        anchor_expectations=(
            (
                "module-compile-flags-int-zero-warm-str-compiled-pattern-named-group",
                (
                    "workflow-module-compile-flags-int-zero-str-compiled-pattern-"
                    "named-group",
                ),
            ),
            (
                "module-compile-flags-int-zero-purged-bytes-compiled-pattern-named-group",
                (
                    "workflow-module-compile-flags-int-zero-bytes-compiled-pattern-"
                    "named-group",
                ),
            ),
        ),
        contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_named_group_keyword_contract.py"
        ),
        anchor_contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_named_group_keyword_anchor_contract.py"
        ),
        expected_anchor_pairs=(
            (
                "module-compile-flags-int-zero-warm-str-compiled-pattern-named-group-contract",
                "workflow-module-compile-flags-int-zero-str-compiled-pattern-named-group",
            ),
            (
                "module-compile-flags-int-zero-purged-bytes-compiled-pattern-named-group-contract",
                "workflow-module-compile-flags-int-zero-bytes-compiled-pattern-named-group",
            ),
        ),
    ),
    benchmark_test_support._CompiledPatternModuleCompileKeywordOwnerSpec(
        case_id="bool-false",
        anchor_definition_name=(
            "module-workflow-compiled-pattern-module-compile-flags-bool-false-keyword"
        ),
        keyword_signature=(
            benchmark_test_support._COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_SIGNATURE
        ),
        allowed_patterns=(
            benchmark_test_support._COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS
        ),
        anchor_expectations=(
            (
                "module-compile-flags-bool-false-warm-str-compiled-pattern",
                ("workflow-module-compile-flags-bool-false-str-compiled-pattern",),
            ),
            (
                "module-compile-flags-bool-false-purged-bytes-compiled-pattern",
                ("workflow-module-compile-flags-bool-false-bytes-compiled-pattern",),
            ),
        ),
        contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_bool_false_keyword_contract.py"
        ),
        anchor_contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_bool_false_keyword_anchor_contract.py"
        ),
        expected_anchor_pairs=(
            (
                "module-compile-flags-bool-false-warm-str-compiled-pattern-contract",
                "workflow-module-compile-flags-bool-false-str-compiled-pattern",
            ),
            (
                "module-compile-flags-bool-false-purged-bytes-compiled-pattern-contract",
                "workflow-module-compile-flags-bool-false-bytes-compiled-pattern",
            ),
        ),
    ),
    benchmark_test_support._CompiledPatternModuleCompileKeywordOwnerSpec(
        case_id="bool-false-named-group",
        anchor_definition_name=(
            "module-workflow-compiled-pattern-module-compile-flags-bool-false-"
            "keyword-named-group"
        ),
        keyword_signature=(
            benchmark_test_support._COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_SIGNATURE
        ),
        allowed_patterns=(
            benchmark_test_support._COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS
        ),
        anchor_expectations=(
            (
                "module-compile-flags-bool-false-warm-str-compiled-pattern-named-group",
                (
                    "workflow-module-compile-flags-bool-false-str-compiled-pattern-"
                    "named-group",
                ),
            ),
            (
                "module-compile-flags-bool-false-purged-bytes-compiled-pattern-named-group",
                (
                    "workflow-module-compile-flags-bool-false-bytes-compiled-pattern-"
                    "named-group",
                ),
            ),
        ),
        contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_bool_false_named_group_keyword_contract.py"
        ),
        anchor_contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_bool_false_named_group_keyword_anchor_contract.py"
        ),
        expected_anchor_pairs=(
            (
                "module-compile-flags-bool-false-warm-str-compiled-pattern-named-group-contract",
                "workflow-module-compile-flags-bool-false-str-compiled-pattern-named-group",
            ),
            (
                "module-compile-flags-bool-false-purged-bytes-compiled-pattern-named-group-contract",
                "workflow-module-compile-flags-bool-false-bytes-compiled-pattern-named-group",
            ),
        ),
    ),
    benchmark_test_support._CompiledPatternModuleCompileKeywordOwnerSpec(
        case_id="ignorecase",
        anchor_definition_name=(
            "module-workflow-compiled-pattern-module-compile-flags-ignorecase-"
            "keyword-rejection"
        ),
        keyword_signature=(
            benchmark_test_support._COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_SIGNATURE
        ),
        allowed_patterns=(
            benchmark_test_support._COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS
        ),
        anchor_expectations=(
            (
                "module-compile-flags-ignorecase-warm-str-compiled-pattern",
                ("workflow-module-compile-flags-ignorecase-str-compiled-pattern",),
            ),
            (
                "module-compile-flags-ignorecase-purged-bytes-compiled-pattern",
                ("workflow-module-compile-flags-ignorecase-bytes-compiled-pattern",),
            ),
        ),
        contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_ignorecase_keyword_contract.py"
        ),
        anchor_contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_ignorecase_keyword_anchor_contract.py"
        ),
        expected_anchor_pairs=(
            (
                "module-compile-flags-ignorecase-warm-str-compiled-pattern-contract",
                "workflow-module-compile-flags-ignorecase-str-compiled-pattern",
            ),
            (
                "module-compile-flags-ignorecase-purged-bytes-compiled-pattern-contract",
                "workflow-module-compile-flags-ignorecase-bytes-compiled-pattern",
            ),
        ),
        expected_exception=(
            benchmark_test_support._COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION
        ),
    ),
    benchmark_test_support._CompiledPatternModuleCompileKeywordOwnerSpec(
        case_id="ignorecase-named-group",
        anchor_definition_name=(
            "module-workflow-compiled-pattern-module-compile-flags-ignorecase-"
            "keyword-rejection-named-group"
        ),
        keyword_signature=(
            benchmark_test_support._COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_SIGNATURE
        ),
        allowed_patterns=(
            benchmark_test_support._COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS
        ),
        anchor_expectations=(
            (
                "module-compile-flags-ignorecase-warm-str-compiled-pattern-named-group",
                (
                    "workflow-module-compile-flags-ignorecase-str-compiled-pattern-"
                    "named-group",
                ),
            ),
            (
                "module-compile-flags-ignorecase-purged-bytes-compiled-pattern-named-group",
                (
                    "workflow-module-compile-flags-ignorecase-bytes-compiled-pattern-"
                    "named-group",
                ),
            ),
        ),
        contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_ignorecase_named_group_keyword_contract.py"
        ),
        anchor_contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_ignorecase_named_group_keyword_anchor_contract.py"
        ),
        expected_anchor_pairs=(
            (
                "module-compile-flags-ignorecase-warm-str-compiled-pattern-named-group-contract",
                "workflow-module-compile-flags-ignorecase-str-compiled-pattern-named-group",
            ),
            (
                "module-compile-flags-ignorecase-purged-bytes-compiled-pattern-named-group-contract",
                "workflow-module-compile-flags-ignorecase-bytes-compiled-pattern-named-group",
            ),
        ),
        expected_exception=(
            benchmark_test_support._COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION
        ),
    ),
)
_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES = (
    benchmark_test_support.build_compiled_pattern_module_compile_contract_cases(
        manifest_path=benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,
        expected_build_calls_builder=benchmark_test_support.partial(
            benchmark_test_support.compiled_pattern_contract_expected_build_calls,
            label="module.compile contract",
        ),
        success_owner_specs=_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS,
        keyword_owner_specs=_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS,
    )
)
_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS = (
    benchmark_test_support.build_compiled_pattern_module_compile_contract_source_workload_params(
        _COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES
    )
)
_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES = (
    build_compiled_pattern_module_contract_anchor_lanes(
        contract_cases=_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES,
        published_case_ids_by_signature=(
            benchmark_test_support.published_case_ids_by_signature
        ),
    )
)
_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC = (
    benchmark_test_support.CompiledPatternModuleSuccessOwnerSpec(
        case_id="collection-replacement",
        manifest_path=benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
        include_workload_selectors=(
            benchmark_test_support._is_collection_replacement_compiled_pattern_success_workload,
        ),
        contract_manifest_id="collection-replacement-boundary",
        contract_filename=(
            "python_benchmark_compiled_pattern_collection_replacement_success_contract.py"
        ),
        note_surface="collection/replacement",
        expected_source_workload_ids=(
            "module-split-literal-warm-str-compiled-pattern",
            "module-findall-literal-purged-bytes-compiled-pattern",
            "module-finditer-literal-warm-str-compiled-pattern",
            "module-sub-literal-warm-str-compiled-pattern",
            "module-subn-literal-purged-bytes-compiled-pattern",
        ),
        preserved_payload_fields=("count", "maxsplit"),
        preserve_replacement_payload_typing=True,
    )
)
_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC = (
    benchmark_test_support.CompiledPatternModuleSuccessOwnerSpec(
        case_id="module-boundary",
        manifest_path=benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,
        include_workload_selectors=(
            benchmark_test_support._is_module_workflow_compiled_pattern_literal_success_workload,
            benchmark_test_support._is_module_workflow_compiled_pattern_bounded_wildcard_success_workload,
            benchmark_test_support._is_module_workflow_compiled_pattern_verbose_bytes_success_workload,
        ),
        contract_manifest_id="module-boundary",
        contract_filename=(
            "python_benchmark_compiled_pattern_module_boundary_success_contract.py"
        ),
        note_surface="module-boundary",
        expected_source_workload_ids=(
            "module-search-literal-warm-hit-str-compiled-pattern",
            "module-match-literal-warm-hit-str-compiled-pattern",
            "module-fullmatch-literal-purged-hit-bytes-compiled-pattern",
            "module-search-bounded-wildcard-ignorecase-warm-hit-str-compiled-pattern",
            "module-match-bounded-wildcard-warm-hit-str-compiled-pattern",
            "module-fullmatch-bounded-wildcard-purged-hit-str-compiled-pattern",
            "module-search-verbose-regression-warm-hit-bytes-compiled-pattern",
            "module-fullmatch-verbose-regression-purged-hit-bytes-compiled-pattern",
        ),
        preserved_payload_fields=("flags",),
        preserve_replacement_payload_typing=False,
    )
)
_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS = (
    _COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC,
    _COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC,
)
_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS = (
    tuple(
        pytest.param(
            owner_spec,
            source_workload,
            id=f"{owner_spec.case_id}-{source_workload.workload_id}",
        )
        for owner_spec in _COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS
        for source_workload in owner_spec.source_workloads()
    )
)
_is_module_workflow_compiled_pattern_literal_success_workload = (
    benchmark_test_support._is_module_workflow_compiled_pattern_literal_success_workload
)
_is_module_workflow_compiled_pattern_bounded_wildcard_success_workload = (
    benchmark_test_support._is_module_workflow_compiled_pattern_bounded_wildcard_success_workload
)
_is_module_workflow_compiled_pattern_verbose_bytes_success_workload = (
    benchmark_test_support._is_module_workflow_compiled_pattern_verbose_bytes_success_workload
)
_is_collection_replacement_compiled_pattern_success_workload = (
    benchmark_test_support._is_collection_replacement_compiled_pattern_success_workload
)
_assert_compiled_pattern_module_success_payload_round_trip = (
    benchmark_test_support._assert_compiled_pattern_module_success_payload_round_trip
)
def _is_collection_replacement_compiled_pattern_keyword_error_workload(
    workload: Any,
) -> bool:
    return (
        benchmark_test_support._is_collection_replacement_keyword_workload(workload)
        and workload.use_compiled_pattern
        and workload.operation in {"module.split", "module.sub", "module.subn"}
        and workload.expected_exception is not None
        and getattr(workload, "haystack_text_model", None) is None
    )


_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC = (
    benchmark_test_support._CompiledPatternModuleHelperKeywordContractSpec(
        contract_filename=(
            "python_benchmark_compiled_pattern_collection_replacement_keyword_contract.py"
        ),
        expected_source_workload_ids=(
            "module-split-maxsplit-keyword-purged-str-compiled-pattern",
            "module-split-maxsplit-indexlike-keyword-purged-bytes-compiled-pattern",
            "module-split-maxsplit-bool-keyword-purged-bytes-compiled-pattern",
            "module-sub-count-keyword-warm-str-compiled-pattern",
            "module-sub-count-indexlike-keyword-warm-bytes-compiled-pattern",
            "module-sub-count-bool-keyword-warm-str-compiled-pattern",
            "module-sub-count-bool-false-keyword-warm-str-compiled-pattern",
            "module-subn-count-keyword-purged-bytes-compiled-pattern",
            "module-subn-count-indexlike-keyword-purged-str-compiled-pattern",
            "module-subn-count-bool-keyword-purged-bytes-compiled-pattern",
            "module-subn-count-bool-true-keyword-purged-bytes-compiled-pattern",
        ),
        manifest_timed_samples=2,
        preserve_expected_exception=False,
        materializes_positional_keyword_field=False,
        notes=(
            "Ensures benchmark manifests keep compiled-pattern-first-argument "
            "collection/replacement keyword carriers unresolved until helper "
            "invocation.",
        ),
        precompile_anchor_ids=(
            "module-split-maxsplit-keyword-purged-str-compiled-pattern",
            "module-sub-count-keyword-warm-str-compiled-pattern",
            "module-subn-count-keyword-purged-bytes-compiled-pattern",
        ),
    )
)

_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC = (
    benchmark_test_support._CompiledPatternModuleHelperKeywordContractSpec(
        contract_filename=(
            "python_benchmark_compiled_pattern_collection_replacement_keyword_error_contract.py"
        ),
        expected_source_workload_ids=(
            "module-split-duplicate-maxsplit-keyword-purged-str-compiled-pattern",
            "module-split-unexpected-keyword-purged-bytes-compiled-pattern",
            "module-sub-duplicate-count-keyword-warm-str-compiled-pattern",
            "module-sub-unexpected-keyword-purged-str-compiled-pattern",
            "module-sub-unexpected-keyword-after-positional-count-purged-str-compiled-pattern",
            "module-sub-count-alias-keyword-purged-str-compiled-pattern",
            "module-subn-duplicate-count-keyword-warm-bytes-compiled-pattern",
            "module-subn-unexpected-keyword-purged-bytes-compiled-pattern",
            "module-subn-unexpected-keyword-after-positional-count-purged-bytes-compiled-pattern",
            "module-subn-count-alias-keyword-purged-bytes-compiled-pattern",
        ),
        manifest_timed_samples=1,
        preserve_expected_exception=True,
        materializes_positional_keyword_field=True,
    )
)

_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS = (
    benchmark_test_support.selected_manifest_workloads(
        benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
        include_workload=(
            benchmark_test_support._is_collection_replacement_compiled_pattern_module_helper_keyword_workload
        ),
    )
)
if (
    tuple(
        workload.workload_id
        for workload in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS
    )
    != _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC.expected_source_workload_ids
):
    raise AssertionError(
        "compiled-pattern module-helper keyword contract source workloads drifted "
        "from the live source workload surface"
    )

_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS = tuple(
    workload
    for workload in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS
    if workload.workload_id
    in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC.precompile_anchor_ids
)
if (
    tuple(
        workload.workload_id
        for workload in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS
    )
    != _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC.precompile_anchor_ids
):
    raise AssertionError(
        "compiled-pattern module-helper keyword precompile anchors drifted "
        "from the live source workload surface"
    )

_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS = (
    benchmark_test_support.selected_manifest_workloads(
        benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
        include_workload=(
            _is_collection_replacement_compiled_pattern_keyword_error_workload
        ),
    )
)
if (
    tuple(
        workload.workload_id
        for workload in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS
    )
    != _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC.expected_source_workload_ids
):
    raise AssertionError(
        "compiled-pattern module-helper keyword-error source workloads drifted "
        "from the live source workload surface"
    )

_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES = (
    benchmark_test_support._CompiledPatternModuleHelperKeywordContractSurface(
        case_id="success",
        spec=_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC,
        source_workloads_value=_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS,
        precompile_source_workloads_value=(
            _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS
        ),
    ),
    benchmark_test_support._CompiledPatternModuleHelperKeywordContractSurface(
        case_id="keyword-error",
        spec=_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC,
        source_workloads_value=(
            _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS
        ),
    ),
)

_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACE_PARAMS = tuple(
    pytest.param(surface, id=surface.case_id)
    for surface in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES
)

_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS = tuple(
    pytest.param(
        surface,
        source_workload,
        id=f"{surface.case_id}-{source_workload.workload_id}",
    )
    for surface in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES
    for source_workload in surface.source_workloads()
)

_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS = tuple(
    pytest.param(
        surface,
        source_workload,
        id=f"{surface.case_id}-{source_workload.workload_id}",
    )
    for surface in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES
    for source_workload in surface.precompile_source_workloads()
)
_assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call = (
    benchmark_test_support._assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call
)
compiled_pattern_contract_expected_build_calls = (
    benchmark_test_support.compiled_pattern_contract_expected_build_calls
)
_compiled_pattern_module_helper_route = (
    benchmark_test_support._compiled_pattern_module_helper_route
)

COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS = (
    _build_compiled_pattern_module_compile_standard_benchmark_definitions()
)
COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS = (
    benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
        name="module-workflow-compiled-pattern-literal-success",
        manifest_paths=(benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
            benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,
            {
                "module-search-literal-warm-hit-str-compiled-pattern": (
                    "workflow-module-search-str-compiled-pattern",
                ),
                "module-match-literal-warm-hit-str-compiled-pattern": (
                    "workflow-module-match-str-compiled-pattern",
                ),
                "module-fullmatch-literal-purged-hit-bytes-compiled-pattern": (
                    "workflow-module-fullmatch-bytes-compiled-pattern",
                ),
            },
        ),
        include_workload=(
            benchmark_test_support._is_module_workflow_compiled_pattern_literal_success_workload
        ),
        correctness_case_signature=(
            benchmark_test_support._module_workflow_compiled_pattern_correctness_case_signature
        ),
        workload_signature=(
            benchmark_test_support._module_workflow_compiled_pattern_workload_signature
        ),
        run_callback_result_parity=True,
    ),
    benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
        name="module-workflow-compiled-pattern-bounded-wildcard-success",
        manifest_paths=(benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
            benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,
            {
                "module-search-bounded-wildcard-ignorecase-warm-hit-str-compiled-pattern": (
                    "workflow-module-search-str-bounded-wildcard-ignorecase-compiled-pattern",
                ),
                "module-match-bounded-wildcard-warm-hit-str-compiled-pattern": (
                    "workflow-module-match-str-bounded-wildcard-compiled-pattern",
                ),
                "module-fullmatch-bounded-wildcard-purged-hit-str-compiled-pattern": (
                    "workflow-module-fullmatch-str-bounded-wildcard-compiled-pattern",
                ),
            },
        ),
        include_workload=(
            benchmark_test_support._is_module_workflow_compiled_pattern_bounded_wildcard_success_workload
        ),
        correctness_case_signature=(
            benchmark_test_support._module_workflow_compiled_pattern_correctness_case_signature
        ),
        workload_signature=(
            benchmark_test_support._module_workflow_compiled_pattern_workload_signature
        ),
        run_callback_result_parity=True,
    ),
    benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
        name="module-workflow-compiled-pattern-verbose-bytes-success",
        manifest_paths=(benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
            benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,
            {
                "module-search-verbose-regression-warm-hit-bytes-compiled-pattern": (
                    "workflow-module-search-bytes-verbose-regression-compiled-pattern",
                ),
                "module-fullmatch-verbose-regression-purged-hit-bytes-compiled-pattern": (
                    "workflow-module-fullmatch-bytes-verbose-regression-compiled-pattern",
                ),
            },
        ),
        include_workload=(
            benchmark_test_support._is_module_workflow_compiled_pattern_verbose_bytes_success_workload
        ),
        correctness_case_signature=(
            benchmark_test_support._module_workflow_compiled_pattern_correctness_case_signature
        ),
        workload_signature=(
            benchmark_test_support._module_workflow_compiled_pattern_workload_signature
        ),
        run_callback_result_parity=True,
    ),
    benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
        name="module-workflow-compiled-pattern-wrong-text-model",
        manifest_paths=(benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
            benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,
            {
                "module-search-on-bytes-string-warm-str-compiled-pattern": (
                    "workflow-module-search-str-compiled-pattern-on-bytes-string",
                ),
                "module-match-on-str-string-purged-bytes-compiled-pattern": (
                    "workflow-module-match-bytes-compiled-pattern-on-str-string",
                ),
                "module-fullmatch-on-bytes-string-warm-str-compiled-pattern": (
                    "workflow-module-fullmatch-str-compiled-pattern-on-bytes-string",
                ),
            },
        ),
        include_workload=_is_module_workflow_compiled_pattern_wrong_text_model_workload,
        correctness_case_signature=(
            benchmark_test_support._module_workflow_compiled_pattern_correctness_case_signature
        ),
        workload_signature=(
            benchmark_test_support._module_workflow_compiled_pattern_workload_signature
        ),
    ),
)


def live_compiled_pattern_module_success_surface_ids() -> tuple[str, ...]:
    return tuple(
        workload.workload_id
        for owner_spec in _COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS
        for workload in benchmark_test_support.selected_manifest_workloads(
            owner_spec.manifest_path,
            include_workload=(
                benchmark_test_support.include_live_compiled_pattern_module_success_workload
            ),
        )
    )


SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS = (
    _source_tree_standard_benchmark_definitions()
)
