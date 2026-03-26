from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from functools import cache, partial
import json
import pathlib
import re
from types import SimpleNamespace
import unittest

import pytest

from rebar_harness import benchmarks
from rebar_harness.benchmarks import (
    BenchmarkManifest,
    Workload,
    determine_phase,
    determine_runner_version,
    load_manifest,
    published_benchmark_manifests,
    workload_from_payload,
    workload_to_payload,
)
from tests.benchmarks import benchmark_test_support
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
    case_pattern,
    case_replacement_argument,
    case_text_argument,
    callable_match_group_signature,
    module_workflow_keyword_kwargs_signature,
    module_workflow_positional_args_signature,
)

_is_collection_replacement_compiled_pattern_success_workload = (
    benchmark_test_support._is_collection_replacement_compiled_pattern_success_workload
)
_is_collection_replacement_wrong_text_model_workload = (
    benchmark_test_support._is_collection_replacement_wrong_text_model_workload
)


def _assert_compiled_pattern_module_compile_contract_payload_round_trip_common(
    source_workload: Workload,
    payload: dict[str, object],
    round_tripped: Workload,
) -> None:
    expected_text_type = str if source_workload.text_model == "str" else bytes

    assert payload["use_compiled_pattern"] is True
    assert round_tripped.use_compiled_pattern is True
    assert payload["flags"] == source_workload.flags
    assert round_tripped.flags == source_workload.flags
    assert payload.get("expected_exception") == source_workload.expected_exception
    assert round_tripped.expected_exception == source_workload.expected_exception
    assert isinstance(round_tripped.pattern_payload(), expected_text_type)


def _assert_compiled_pattern_module_compile_success_payload_round_trip(
    contract_case: object,
    source_workload: Workload,
    payload: dict[str, object],
    round_tripped: Workload,
) -> None:
    del contract_case
    _assert_compiled_pattern_module_compile_contract_payload_round_trip_common(
        source_workload,
        payload,
        round_tripped,
    )
    assert payload.get("haystack_text_model") == source_workload.haystack_text_model
    assert round_tripped.haystack_text_model == source_workload.haystack_text_model


def _assert_compiled_pattern_module_compile_keyword_payload_round_trip(
    contract_case: object,
    source_workload: Workload,
    payload: dict[str, object],
    round_tripped: Workload,
) -> None:
    del contract_case
    _assert_compiled_pattern_module_compile_contract_payload_round_trip_common(
        source_workload,
        payload,
        round_tripped,
    )
    expected_keyword_value = source_workload.keyword_arguments()["flags"]

    assert payload["kwargs"] == source_workload.kwargs
    assert round_tripped.kwargs == source_workload.kwargs
    assert type(payload["kwargs"]["flags"]) is type(expected_keyword_value)
    assert type(round_tripped.kwargs["flags"]) is type(expected_keyword_value)
    assert payload.get("haystack_text_model") is None
    assert round_tripped.haystack_text_model is None


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


def compiled_pattern_contract_expected_build_calls(
    source_workload: Workload,
    *,
    label: str,
) -> list[tuple[object, ...]]:
    compile_call = ("compile", source_workload.pattern_payload(), source_workload.flags)
    if source_workload.cache_mode == "purged":
        return [compile_call, ("purge",)]
    if source_workload.cache_mode == "warm":
        return [compile_call]
    raise AssertionError(
        f"unexpected compiled-pattern {label} workload cache mode "
        f"{source_workload.cache_mode!r}"
    )


def _run_cpython_compiled_pattern_module_helper_workload(
    workload: Workload,
    *,
    collection_replacement_callback_flags: int,
) -> object:
    del collection_replacement_callback_flags

    compiled_pattern = re.compile(
        workload.pattern_payload(),
        workload.flags,
    )
    if workload.operation in benchmark_test_support._COMPILED_PATTERN_MODULE_HELPER_OPERATIONS:
        cpython_call_args = (workload.haystack_payload(), workload.flags)
        materialize_cpython_result = False
    elif workload.operation == "module.split":
        cpython_call_args = (
            workload.haystack_payload(),
            workload.maxsplit_argument(),
        )
        materialize_cpython_result = False
    elif workload.operation == "module.findall":
        cpython_call_args = (workload.haystack_payload(), workload.flags)
        materialize_cpython_result = False
    elif workload.operation == "module.finditer":
        cpython_call_args = (workload.haystack_payload(), workload.flags)
        materialize_cpython_result = True
    elif workload.operation == "module.sub":
        cpython_call_args = (
            workload.replacement_payload(),
            workload.haystack_payload(),
            workload.count_argument(),
        )
        materialize_cpython_result = False
    elif workload.operation == "module.subn":
        cpython_call_args = (
            workload.replacement_payload(),
            workload.haystack_payload(),
            workload.count_argument(),
        )
        materialize_cpython_result = False
    else:
        raise AssertionError(
            "unexpected compiled-pattern module helper workload operation "
            f"{workload.operation!r}"
        )
    helper = getattr(re, workload.operation.removeprefix("module."))
    result = helper(compiled_pattern, *cpython_call_args)
    if materialize_cpython_result:
        return list(result)
    return result


def _assert_wrong_text_model_payload_round_trip(
    source_workload: Workload,
    payload: dict[str, object],
    round_tripped: Workload,
) -> None:
    expected_text_type = str if source_workload.text_model == "str" else bytes
    expected_haystack_type = (
        str if source_workload.haystack_text_model == "str" else bytes
    )

    assert payload["use_compiled_pattern"] is True
    assert round_tripped.use_compiled_pattern is True
    assert payload["timing_scope"] == "module-helper-call"
    assert round_tripped.timing_scope == "module-helper-call"
    assert payload["haystack_text_model"] == source_workload.haystack_text_model
    assert round_tripped.haystack_text_model == source_workload.haystack_text_model
    assert payload["expected_exception"] == source_workload.expected_exception
    assert round_tripped.expected_exception == source_workload.expected_exception
    assert isinstance(round_tripped.pattern_payload(), expected_text_type)
    assert isinstance(round_tripped.haystack_payload(), expected_haystack_type)
    if source_workload.replacement is not None:
        assert isinstance(round_tripped.replacement_payload(), expected_text_type)


def _assert_compiled_pattern_module_success_payload_round_trip(
    source_workload: Workload,
    payload: dict[str, object],
    round_tripped: Workload,
    *,
    owner_spec: Any,
) -> None:
    expected_text_type = str if source_workload.text_model == "str" else bytes

    assert payload["use_compiled_pattern"] is True
    assert round_tripped.use_compiled_pattern is True
    assert payload.get("expected_exception") is None
    assert round_tripped.expected_exception is None
    assert payload.get("haystack_text_model") is None
    assert round_tripped.haystack_text_model is None
    assert isinstance(round_tripped.pattern_payload(), expected_text_type)
    assert isinstance(round_tripped.haystack_payload(), expected_text_type)
    for field_name in owner_spec.preserved_payload_fields:
        assert payload[field_name] == getattr(source_workload, field_name)
        assert getattr(round_tripped, field_name) == getattr(
            source_workload,
            field_name,
        )
    if (
        owner_spec.preserve_replacement_payload_typing
        and source_workload.replacement is not None
    ):
        assert isinstance(round_tripped.replacement_payload(), expected_text_type)


def _assert_compiled_pattern_success_rows_measured_in_combined_manifest(
    owner_spec: Any,
    *,
    include_workload: Callable[[Any], bool],
) -> None:
    testcase = benchmark_test_support.unittest.TestCase()
    manifest = benchmark_test_support.load_manifest(owner_spec.manifest_path)
    expected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in owner_spec.source_workloads()
        if include_workload(workload)
    )
    selected_measured_workload_ids = benchmark_test_support.manifest_workload_ids_matching(
        manifest,
        include_workload,
    )

    assert selected_measured_workload_ids == expected_measured_workload_ids

    _, scorecard = benchmark_test_support.run_harness_scorecard(
        "rebar_harness.benchmarks",
        ["--manifest", str(owner_spec.manifest_path)],
        report_name="benchmarks.json",
    )
    manifest_summary = scorecard["manifests"][owner_spec.contract_manifest_id]
    expected_workload_count = len(manifest.workloads)

    assert manifest_summary["known_gap_count"] == 0
    assert manifest_summary["measured_workloads"] == expected_workload_count
    assert manifest_summary["workload_count"] == expected_workload_count

    for workload_id in expected_measured_workload_ids:
        benchmark_test_support.assert_benchmark_workload_contract(
            testcase,
            benchmark_test_support.find_workload_record(scorecard, workload_id),
            manifest_id=owner_spec.contract_manifest_id,
            workload_document=benchmark_test_support.find_workload_document(
                manifest,
                workload_id,
            ),
            expected_status="measured",
        )


def include_live_compiled_pattern_module_success_workload(workload: Workload) -> bool:
    return (
        workload.use_compiled_pattern
        and workload.expected_exception is None
        and getattr(workload, "haystack_text_model", None) is None
        and workload.operation.startswith("module.")
        and workload.operation != "module.compile"
        and not workload.kwargs
    )

@dataclass(frozen=True, slots=True)
class _SourceTreeBenchmarkCommonCase:
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
        return tuple(
            workload.workload_id
            for workload in self.manifest_for_id(manifest_id).selected_workloads(
                selection_mode=self.selection_mode
            )
        )


@dataclass(frozen=True, slots=True)
class _SourceTreeManifestExpectation:
    known_gap_count: int
    representative_measured_workload_ids: tuple[str, ...] = ()
    representative_known_gap_workload_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class _SourceTreeDeferredExpectation:
    area: str
    follow_up: str


@dataclass(frozen=True, slots=True)
class _SourceTreeCombinedCase(_SourceTreeBenchmarkCommonCase):
    manifest_expectation: _SourceTreeManifestExpectation
    manifest_id: str
    target_manifest: BenchmarkManifest


@dataclass(frozen=True, slots=True)
class _SourceTreeCombinedPatternGroupExpectation:
    slice_id: str
    patterns: tuple[str, ...]
    minimum_rows: int
    required_operations: tuple[str, ...]
    required_categories: tuple[str, ...]
    search_haystacks: tuple[str, ...]
    search_haystack_substrings: tuple[str, ...]
    pattern_haystacks: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class _SourceTreeCombinedManifestShapeExpectation:
    representative_measured_workload_ids: tuple[str, ...]
    pattern_groups: tuple[_SourceTreeCombinedPatternGroupExpectation, ...] = ()


@dataclass(frozen=True, slots=True)
class _SourceTreeCombinedFullyMeasuredManifestExpectation:
    coverage_group: str
    representative_measured_workload_ids: tuple[str, ...]
    expected_measured_workload_count: int
    expected_total_workload_count: int | None = None


@dataclass(frozen=True, slots=True)
class _SourceTreeCombinedManifestExpectationDefinition:
    exclude_from_combined_targets: bool = False
    promote_zero_gap_representatives: bool = False
    known_gap_workload_ids: tuple[str, ...] | None = None
    representative_measured_workload_ids: tuple[str, ...] | None = None
    representative_known_gap_workload_ids: tuple[str, ...] | None = None
    fully_measured_expectation: _SourceTreeCombinedFullyMeasuredManifestExpectation | None = None
    shape_expectation: _SourceTreeCombinedManifestShapeExpectation | None = None
    zero_gap_bytes_representative_subsets: tuple[tuple[str, ...], ...] = ()


@dataclass(frozen=True, slots=True)
class _SourceTreeCombinedSliceExpectation:
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

def _combined_manifest_definition(
    *,
    exclude_from_combined_targets: bool = False,
    promote_zero_gap_representatives: bool = False,
    known_gap_workload_ids: tuple[str, ...] | None = None,
    representative_measured_workload_ids: tuple[str, ...] | None = None,
    representative_known_gap_workload_ids: tuple[str, ...] | None = None,
    fully_measured_expectation: _SourceTreeCombinedFullyMeasuredManifestExpectation
    | None = None,
    shape_expectation: _SourceTreeCombinedManifestShapeExpectation | None = None,
    zero_gap_bytes_representative_subsets: tuple[tuple[str, ...], ...] = (),
) -> _SourceTreeCombinedManifestExpectationDefinition:
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
    return _SourceTreeCombinedManifestExpectationDefinition(
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
) -> _SourceTreeCombinedFullyMeasuredManifestExpectation:
    return _SourceTreeCombinedFullyMeasuredManifestExpectation(
        coverage_group=coverage_group,
        representative_measured_workload_ids=tuple(
            str(workload_id) for workload_id in representative_measured_workload_ids
        ),
        expected_measured_workload_count=expected_measured_workload_count,
        expected_total_workload_count=expected_total_workload_count,
    )


@cache
def _published_benchmark_manifest_ids() -> frozenset[str]:
    return frozenset(
        manifest.manifest_id for manifest in published_benchmark_manifests()
    )


_PATTERN_BOUNDARY_STANDARD_DEFINITION_BLOCK = (
    benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
        name="pattern-window-positional-indexlike",
        manifest_paths=(benchmark_test_support.PATTERN_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
            benchmark_test_support.PATTERN_BOUNDARY_MANIFEST_PATH,
            {
                "pattern-search-pos-indexlike-positional-warm-str": (
                    "workflow-pattern-search-str-pos-indexlike-positional",
                ),
                "pattern-search-endpos-indexlike-positional-purged-bytes": (
                    "workflow-pattern-search-bytes-endpos-indexlike-positional",
                ),
                "pattern-match-window-indexlike-positional-purged-bytes": (
                    "workflow-pattern-match-bytes-window-indexlike-positional",
                ),
                "pattern-fullmatch-window-indexlike-positional-purged-bytes": (
                    "workflow-pattern-fullmatch-bytes-window-indexlike-positional",
                ),
                "pattern-findall-window-indexlike-positional-warm-str": (
                    "workflow-pattern-findall-str-window-indexlike-positional",
                ),
                "pattern-finditer-window-indexlike-positional-purged-bytes": (
                    "workflow-pattern-finditer-bytes-window-indexlike-positional",
                ),
            },
        ),
        include_workload=benchmark_test_support._is_pattern_window_positional_indexlike_workload,
        correctness_case_signature=(
            benchmark_test_support._pattern_window_positional_indexlike_correctness_case_signature
        ),
        workload_signature=(
            benchmark_test_support._pattern_window_positional_indexlike_workload_signature
        ),
        run_callback_result_parity=True,
    ),
    benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
        name="pattern-window-keyword",
        manifest_paths=(benchmark_test_support.PATTERN_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
            benchmark_test_support.PATTERN_BOUNDARY_MANIFEST_PATH,
            {
                "pattern-search-pos-keyword-warm-str": (
                    "workflow-pattern-search-str-pos-keyword",
                ),
                "pattern-search-bool-endpos-keyword-warm-str": (
                    "workflow-pattern-search-str-bool-endpos-keyword",
                ),
                "pattern-search-endpos-keyword-purged-bytes": (
                    "workflow-pattern-search-bytes-endpos-keyword",
                ),
                "pattern-search-pos-indexlike-keyword-warm-str": (
                    "workflow-pattern-search-str-pos-indexlike",
                ),
                "pattern-search-endpos-indexlike-keyword-purged-bytes": (
                    "workflow-pattern-search-bytes-endpos-indexlike",
                ),
                "pattern-match-pos-keyword-purged-str": (
                    "workflow-pattern-match-str-pos-keyword",
                ),
                "pattern-match-bool-pos-keyword-purged-str": (
                    "workflow-pattern-match-str-bool-pos-keyword",
                ),
                "pattern-match-window-indexlike-purged-bytes": (
                    "workflow-pattern-match-bytes-window-indexlike",
                ),
                "pattern-fullmatch-window-keyword-purged-bytes": (
                    "workflow-pattern-fullmatch-bytes-window-keyword",
                ),
                "pattern-fullmatch-window-indexlike-keyword-purged-bytes": (
                    "workflow-pattern-fullmatch-bytes-window-indexlike",
                ),
                "pattern-findall-window-keyword-warm-str": (
                    "workflow-pattern-findall-str-window-keyword",
                ),
                "pattern-findall-window-indexlike-keyword-warm-str": (
                    "workflow-pattern-findall-str-window-indexlike",
                ),
                "pattern-findall-bool-window-keyword-warm-str": (
                    "workflow-pattern-findall-str-bool-window-keyword",
                ),
                "pattern-finditer-window-keyword-purged-bytes": (
                    "workflow-pattern-finditer-bytes-window-keyword",
                ),
                "pattern-finditer-window-indexlike-purged-bytes": (
                    "workflow-pattern-finditer-bytes-window-indexlike",
                ),
                "pattern-finditer-bool-window-keyword-purged-bytes": (
                    "workflow-pattern-finditer-bytes-bool-window-keyword",
                ),
            },
        ),
        include_workload=benchmark_test_support._is_pattern_keyword_window_workload,
        correctness_case_signature=benchmark_test_support._pattern_keyword_window_correctness_case_signature,
        workload_signature=benchmark_test_support._pattern_keyword_window_workload_signature,
        run_callback_result_parity=True,
    ),
    benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
        name="pattern-boundary-bounded-wildcard",
        manifest_paths=(benchmark_test_support.PATTERN_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
            benchmark_test_support.PATTERN_BOUNDARY_MANIFEST_PATH,
            {
                "pattern-search-bounded-wildcard-ignorecase-warm-str": (
                    "workflow-pattern-search-str-bounded-wildcard-ignorecase",
                ),
                "pattern-match-bounded-wildcard-warm-str": (
                    "workflow-pattern-match-str-bounded-wildcard",
                ),
                "pattern-fullmatch-bounded-wildcard-purged-str": (
                    "workflow-pattern-fullmatch-str-bounded-wildcard",
                ),
                "pattern-findall-bounded-wildcard-warm-str": (
                    "workflow-pattern-findall-str-bounded-wildcard",
                ),
                "pattern-finditer-bounded-wildcard-purged-str": (
                    "workflow-pattern-finditer-str-bounded-wildcard",
                ),
                "pattern-search-bounded-wildcard-endpos-miss-purged-str": (
                    "workflow-pattern-search-str-bounded-wildcard-endpos-miss",
                ),
            },
        ),
        include_workload=benchmark_test_support._is_pattern_bounded_wildcard_workload,
        correctness_case_signature=benchmark_test_support._pattern_bounded_wildcard_correctness_case_signature,
        workload_signature=benchmark_test_support._pattern_bounded_wildcard_workload_signature,
        run_callback_result_parity=True,
    ),
    benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
        name="pattern-boundary-verbose-regression",
        manifest_paths=(benchmark_test_support.PATTERN_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
            benchmark_test_support.PATTERN_BOUNDARY_MANIFEST_PATH,
            {
                "pattern-search-verbose-regression-warm-str": (
                    "workflow-pattern-search-str-verbose-regression",
                ),
                "pattern-search-verbose-regression-digits-warm-str": (
                    "workflow-pattern-search-str-verbose-regression-digits",
                ),
                "pattern-search-verbose-regression-too-many-digits-purged-str": (
                    "workflow-pattern-search-str-verbose-regression-too-many-digits",
                ),
                "pattern-search-verbose-regression-warm-bytes": (
                    "workflow-pattern-search-bytes-verbose-regression",
                ),
                "pattern-search-verbose-regression-digits-warm-bytes": (
                    "workflow-pattern-search-bytes-verbose-regression-digits",
                ),
                "pattern-search-verbose-regression-too-many-digits-purged-bytes": (
                    "workflow-pattern-search-bytes-verbose-regression-too-many-digits",
                ),
                "pattern-fullmatch-verbose-regression-warm-str": (
                    "workflow-pattern-fullmatch-str-verbose-regression",
                ),
                "pattern-fullmatch-verbose-regression-alpha-warm-str": (
                    "workflow-pattern-fullmatch-str-verbose-regression-alpha",
                ),
                "pattern-fullmatch-verbose-regression-lowercase-key-purged-str": (
                    "workflow-pattern-fullmatch-str-verbose-regression-lowercase-key",
                ),
                "pattern-fullmatch-verbose-regression-warm-bytes": (
                    "workflow-pattern-fullmatch-bytes-verbose-regression",
                ),
                "pattern-fullmatch-verbose-regression-alpha-warm-bytes": (
                    "workflow-pattern-fullmatch-bytes-verbose-regression-alpha",
                ),
                "pattern-fullmatch-verbose-regression-lowercase-key-purged-bytes": (
                    "workflow-pattern-fullmatch-bytes-verbose-regression-lowercase-key",
                ),
            },
        ),
        include_workload=benchmark_test_support._is_pattern_verbose_regression_workload,
        correctness_case_signature=benchmark_test_support._pattern_verbose_regression_correctness_case_signature,
        workload_signature=benchmark_test_support._pattern_verbose_regression_workload_signature,
        run_callback_result_parity=True,
    ),
    benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
        name="pattern-boundary-wrong-text-model",
        manifest_paths=(benchmark_test_support.PATTERN_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
            benchmark_test_support.PATTERN_BOUNDARY_MANIFEST_PATH,
            {
                "pattern-search-on-bytes-string-warm-str": (
                    "workflow-pattern-search-str-pattern-on-bytes-string",
                ),
                "pattern-match-on-str-string-purged-bytes": (
                    "workflow-pattern-match-bytes-pattern-on-str-string",
                ),
                "pattern-fullmatch-on-bytes-string-warm-str": (
                    "workflow-pattern-fullmatch-str-pattern-on-bytes-string",
                ),
            },
        ),
        include_workload=benchmark_test_support._is_pattern_boundary_wrong_text_model_workload,
        correctness_case_signature=(
            benchmark_test_support._pattern_boundary_wrong_text_model_correctness_case_signature
        ),
        workload_signature=benchmark_test_support._pattern_boundary_wrong_text_model_workload_signature,
    ),
)


PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS = (
    _PATTERN_BOUNDARY_STANDARD_DEFINITION_BLOCK
)


def _compiled_pattern_module_helper_runtime_route(
    workload: Workload,
    *,
    collection_replacement_callback_flags: int,
) -> tuple[object, tuple[object, ...], tuple[object, ...], bool]:
    if workload.operation in benchmark_test_support._COMPILED_PATTERN_MODULE_HELPER_OPERATIONS:
        return (
            "module-result",
            (workload.operation, workload.haystack_payload(), 0, {}),
            (workload.haystack_payload(), workload.flags),
            False,
        )
    if workload.operation == "module.split":
        return (
            "module-result",
            (
                workload.operation,
                workload.haystack_payload(),
                workload.maxsplit_argument(),
                collection_replacement_callback_flags,
                {},
            ),
            (workload.haystack_payload(), workload.maxsplit_argument()),
            False,
        )
    if workload.operation == "module.findall":
        return (
            "module-result",
            (
                workload.operation,
                workload.haystack_payload(),
                collection_replacement_callback_flags,
            ),
            (workload.haystack_payload(), workload.flags),
            False,
        )
    if workload.operation == "module.finditer":
        return (
            ["module-finditer-result"],
            (
                workload.operation,
                workload.haystack_payload(),
                collection_replacement_callback_flags,
            ),
            (workload.haystack_payload(), workload.flags),
            True,
        )
    if workload.operation == "module.sub":
        return (
            "module-result",
            (
                workload.operation,
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count_argument(),
                collection_replacement_callback_flags,
                {},
            ),
            (
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count_argument(),
            ),
            False,
        )
    if workload.operation == "module.subn":
        return (
            ("module-result", 0),
            (
                workload.operation,
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count_argument(),
                collection_replacement_callback_flags,
                {},
            ),
            (
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count_argument(),
            ),
            False,
        )
    raise AssertionError(
        "unexpected compiled-pattern module helper workload operation "
        f"{workload.operation!r}"
    )


def _compiled_pattern_module_helper_route(
    workload: Workload,
    *,
    collection_replacement_callback_flags: int,
) -> tuple[object, tuple[object, ...], tuple[object, ...], bool]:
    return _compiled_pattern_module_helper_runtime_route(
        workload,
        collection_replacement_callback_flags=collection_replacement_callback_flags,
    )


_COMPILED_PATTERN_MODULE_HELPER_STANDARD_DEFINITION_BLOCK = (
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
        include_workload=benchmark_test_support._is_module_workflow_compiled_pattern_literal_success_workload,
        correctness_case_signature=(
            benchmark_test_support._module_workflow_compiled_pattern_success_correctness_case_signature
        ),
        workload_signature=benchmark_test_support._module_workflow_compiled_pattern_success_workload_signature,
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
            benchmark_test_support._module_workflow_compiled_pattern_success_correctness_case_signature
        ),
        workload_signature=benchmark_test_support._module_workflow_compiled_pattern_success_workload_signature,
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
        include_workload=benchmark_test_support._is_module_workflow_compiled_pattern_verbose_bytes_success_workload,
        correctness_case_signature=(
            benchmark_test_support._module_workflow_compiled_pattern_success_correctness_case_signature
        ),
        workload_signature=benchmark_test_support._module_workflow_compiled_pattern_success_workload_signature,
        run_callback_result_parity=True,
    ),
)


COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS = (
    _COMPILED_PATTERN_MODULE_HELPER_STANDARD_DEFINITION_BLOCK
)


@cache
def _source_tree_standard_benchmark_definitions() -> tuple[object, ...]:
    return (
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
            include_workload=(
                benchmark_test_support._is_module_workflow_compiled_pattern_wrong_text_model_workload
            ),
            correctness_case_signature=(
                benchmark_test_support._module_workflow_compiled_pattern_correctness_case_signature
            ),
            workload_signature=(
                benchmark_test_support._module_workflow_compiled_pattern_workload_signature
            ),
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="optional-group-conditional",
            manifest_paths=(benchmark_test_support.OPTIONAL_GROUP_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
                benchmark_test_support.OPTIONAL_GROUP_MANIFEST_PATH,
                {
                    benchmark_test_support._OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID: (
                        "optional-group-conditional-module-search-present-str",
                    ),
                },
            ),
            include_workload=benchmark_test_support._is_optional_group_conditional_workload,
            correctness_case_signature=benchmark_test_support._optional_group_correctness_case_signature,
            workload_signature=benchmark_test_support._optional_group_workload_signature,
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
            correctness_case_signature=benchmark_test_support._nested_group_correctness_case_signature,
            workload_signature=benchmark_test_support._nested_group_workload_signature,
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
            include_workload=benchmark_test_support._is_non_alternation_counted_repeat_workload,
            correctness_case_signature=benchmark_test_support._counted_repeat_correctness_case_signature,
            workload_signature=benchmark_test_support._counted_repeat_workload_signature,
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
            include_workload=benchmark_test_support._is_non_alternation_counted_repeat_workload,
            correctness_case_signature=benchmark_test_support._counted_repeat_correctness_case_signature,
            workload_signature=benchmark_test_support._counted_repeat_workload_signature,
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
            correctness_case_signature=benchmark_test_support._grouped_alternation_correctness_case_signature,
            workload_signature=benchmark_test_support._grouped_alternation_workload_signature,
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
            manifest_paths=(
                benchmark_test_support.GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,
            ),
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
                benchmark_test_support._grouped_alternation_replacement_correctness_case_signature
            ),
            workload_signature=benchmark_test_support._grouped_alternation_workload_signature,
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
                benchmark_test_support._grouped_alternation_replacement_correctness_case_signature
            ),
            workload_signature=benchmark_test_support._grouped_alternation_workload_signature,
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
            correctness_case_signature=benchmark_test_support._counted_repeat_correctness_case_signature,
            workload_signature=benchmark_test_support._counted_repeat_workload_signature,
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


SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS = (
    _source_tree_standard_benchmark_definitions()
)


_SOURCE_TREE_DEFAULT_COMBINED_MANIFEST_EXPECTATION = _combined_manifest_definition()


class _SourceTreeCombinedManifestExpectations(
    dict[str, _SourceTreeCombinedManifestExpectationDefinition]
):
    def _supports_fallback(self, manifest_id: object) -> bool:
        return (
            isinstance(manifest_id, str)
            and manifest_id in _published_benchmark_manifest_ids()
        )

    def __missing__(
        self,
        manifest_id: str,
    ) -> _SourceTreeCombinedManifestExpectationDefinition:
        if self._supports_fallback(manifest_id):
            return _SOURCE_TREE_DEFAULT_COMBINED_MANIFEST_EXPECTATION
        raise KeyError(manifest_id)

    def get(
        self,
        manifest_id: str,
        default: _SourceTreeCombinedManifestExpectationDefinition | None = None,
    ) -> _SourceTreeCombinedManifestExpectationDefinition | None:
        if self._supports_fallback(manifest_id):
            return self[manifest_id]
        return default

    def __contains__(self, manifest_id: object) -> bool:
        return super().__contains__(manifest_id) or self._supports_fallback(
            manifest_id
        )


_SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS = _SourceTreeCombinedManifestExpectations({
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
        shape_expectation=_SourceTreeCombinedManifestShapeExpectation(
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
        shape_expectation=_SourceTreeCombinedManifestShapeExpectation(
            representative_measured_workload_ids=(
                "module-search-numbered-wider-ranged-repeat-group-broader-range-cold-gap",
                "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-upper-bound-mixed-purged-str",
                "pattern-fullmatch-numbered-wider-ranged-repeat-group-open-ended-purged-gap",
                "module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-absent-warm-str",
                "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-fourth-repetition-mixed-purged-str",
            ),
            pattern_groups=(
                _SourceTreeCombinedPatternGroupExpectation(
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
                    search_haystack_substrings=(),
                    pattern_haystacks=(
                        "abcbccd",
                        "abcbccbccbcd",
                    ),
                ),
                _SourceTreeCombinedPatternGroupExpectation(
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
                    search_haystacks=(),
                    search_haystack_substrings=(
                        "abcd",
                        "aded",
                    ),
                    pattern_haystacks=(
                        "abcbcded",
                        "adedededed",
                    ),
                ),
                _SourceTreeCombinedPatternGroupExpectation(
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
                    search_haystack_substrings=(),
                    pattern_haystacks=(
                        "abcbcdede",
                        "adedededede",
                    ),
                ),
                _SourceTreeCombinedPatternGroupExpectation(
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
                    search_haystack_substrings=(),
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



SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS = (
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({r"^abc$"}),
        expected_operations=frozenset({"module.compile"}),
        expected_haystacks=frozenset(),
        required_row_categories=("compile", "literal"),
        expected_status="measured",
    ),
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({"abc"}),
        expected_operations=frozenset({"module.compile"}),
        expected_haystacks=frozenset(),
        required_row_categories=("compile", "literal", "compiled-pattern"),
        expected_status="measured",
    ),
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({"(?P<word>abc)"}),
        expected_operations=frozenset({"module.compile"}),
        expected_haystacks=frozenset(),
        required_row_categories=("compile", "named-group", "compiled-pattern"),
        expected_status="measured",
    ),
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({"(?P<word>abc)"}),
        expected_operations=frozenset({"module.compile"}),
        expected_haystacks=frozenset(),
        required_row_categories=(
            "compile",
            "named-group",
            "compiled-pattern",
            "keyword",
            "flags",
        ),
        expected_status="measured",
    ),
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({"(?P<word>abc)"}),
        expected_operations=frozenset({"module.compile"}),
        expected_haystacks=frozenset(),
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
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({"(?P<word>abc)"}),
        expected_operations=frozenset({"module.compile"}),
        expected_haystacks=frozenset(),
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
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({"abc"}),
        expected_operations=frozenset({"module.compile"}),
        expected_haystacks=frozenset(),
        required_row_categories=("compile", "literal", "compiled-pattern", "keyword", "flags"),
        expected_status="measured",
    ),
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({"abc"}),
        expected_operations=frozenset({"module.compile"}),
        expected_haystacks=frozenset(),
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
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({"abc"}),
        expected_operations=frozenset({"module.compile"}),
        expected_haystacks=frozenset(),
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
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({
            r"a((b|c){2,})\2(?(2)d|e)",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
        }),
        expected_operations=frozenset({"module.compile", "module.search", "pattern.fullmatch"}),
        expected_haystacks=frozenset({"zzabbbdzz", "abcbccd", "zzacccdzz", "abbbd"}),
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
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({
            r"a((b|c)+)d",
            r"a(?P<outer>(?P<inner>b|c)+)d",
        }),
        expected_operations=frozenset({"module.search", "pattern.fullmatch"}),
        expected_haystacks=frozenset({"zzabdzz", "acbbd", "zzacdzz", "abccd"}),
        required_row_categories=(
            "nested-group",
            "alternation",
            "quantified",
        ),
    ),
    _SourceTreeCombinedSliceExpectation(
        manifest_id="nested-group-alternation-boundary",
        slice_id="non-quantified-branch-local-backreference",
        required_syntax_features=("branch-local-backreferences",),
        excluded_syntax_features=("quantifiers",),
        expected_workload_ids=(
            "module-search-numbered-nested-group-branch-local-backreference-b-branch-warm-str",
            "module-compile-named-nested-group-branch-local-backreference-warm-str",
            "pattern-fullmatch-named-nested-group-branch-local-backreference-purged-gap",
        ),
        expected_patterns=frozenset({
            r"a((b|c))\2d",
            r"a(?P<outer>(?P<inner>b|c))(?P=inner)d",
        }),
        expected_operations=frozenset({"module.compile", "module.search", "pattern.fullmatch"}),
        expected_haystacks=frozenset({"zzabbdzz", "accd"}),
        required_row_categories=(
            "nested-group",
            "alternation",
            "branch-local",
        ),
    ),
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({
            r"a((b|c)+)\2d",
            r"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
        }),
        expected_operations=frozenset({"module.compile", "module.search", "pattern.fullmatch"}),
        expected_haystacks=frozenset({"zzabbdzz", "abccd"}),
        required_row_categories=(
            "nested-group",
            "alternation",
            "branch-local",
            "quantified",
        ),
    ),
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({
            r"a((b|c){1,4})\2d",
            r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
        }),
        expected_operations=frozenset({"module.compile", "module.search", "pattern.fullmatch"}),
        expected_haystacks=frozenset({"zzabbdzz", "acccccd"}),
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
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({
            r"a((b|c){2,})\2d",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        }),
        expected_operations=frozenset({"module.compile", "module.search", "pattern.fullmatch"}),
        expected_haystacks=frozenset({"zzabbbdzz", "acccd"}),
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
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({
            r"a((b))d",
            r"a(?P<outer>(?P<inner>b))d",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"abdabd"}),
        required_row_categories=(
            "nested-group",
            "replacement",
            "callable",
            "bytes",
        ),
    ),
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({
            r"a((b|c))d",
            r"a(?P<outer>(?P<inner>b|c))d",
        }),
        expected_operations=frozenset({"module.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"abdacd", "acdabd", "acd"}),
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
        ),
    ),
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({
            r"a((bc)+)d",
            r"a(?P<outer>(?P<inner>bc)+)d",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"zzabcdzz", "zzabcbcdabcbcdzz", "zzabcbcdzz"}),
        required_row_categories=(
            "nested-group",
            "replacement",
            "callable",
            "quantified",
        ),
    ),
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({
            r"a((b|c)+)d",
            r"a(?P<outer>(?P<inner>b|c)+)d",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"zzabdzz", "zzabccdacbbdzz", "zzabccdzz"}),
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "quantified",
        ),
    ),
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({
            r"a(((bc|b)c){1,4})d",
            r"a(?P<outer>(?:(?P<inner>bc|b)c){1,4})d",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({
            "abcd",
            "abccdabcbccd",
            "zzabcbccbccbcdzz",
            "zzabccbcdabccdzz",
        }),
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
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({
            r"a(((bc|b)c){2,})d",
            r"a(?P<outer>(?:(?P<inner>bc|b)c){2,})d",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({
            "abcbcd",
            "abccbccdabcbcd",
            "zzabcbcbcbcdzz",
            "zzabcbcbcbcdabccbccdzz",
        }),
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
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({
            r"a((b|c))\2d",
            r"a(?P<outer>(?P<inner>b|c))(?P=inner)d",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"abbd", "abbdaccd", "accd", "accdabbd"}),
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "branch-local",
        ),
    ),
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({
            r"a((b|c)+)\2d",
            r"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"abbd", "abbbdaccd", "zzabccdzz", "zzaccdabbbdzz"}),
        required_row_categories=(
            "nested-group",
            "alternation",
            "replacement",
            "callable",
            "branch-local",
            "quantified",
        ),
    ),
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({
            r"a((b|c){1,4})\2d",
            r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"abbd", "abcbccdabbd", "zzacccccdzz", "zzacccccdabbbdzz"}),
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
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({
            r"a((b|c){1,4})\2(?(2)d|e)",
            r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)(?(inner)d|e)",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"abbd", "abbbdaccd", "zzacccccdzz", "zzacccccdabbbdzz"}),
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
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({
            r"a((b|c){1,})\2d",
            r"a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"abbd", "abbbdaccd", "zzaccdzz", "zzaccdabcbccdzz"}),
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
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({
            r"a((b|c){2,})\2d",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"abbbd", "abbbdabcbccd", "zzacccdzz", "zzacccdabcbccdzz"}),
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
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({
            r"a((b|c){2,})\2(?(2)d|e)",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"abbbd", "abbbdabcbccd", "zzacccdzz", "zzacccdabcbccdzz"}),
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
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({
            r"a((bc)+)d",
            r"a(?P<outer>(?P<inner>bc)+)d",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"zzabcdzz", "zzabcbcdabcbcdzz", "zzabcbcdzz"}),
        required_row_categories=(
            "nested-group",
            "replacement",
            "template",
            "quantified",
        ),
    ),
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({
            r"a((b|c){1,4})\2d",
            r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"abbd", "abbbdaccd", "zzacccccdzz", "zzacccccdabbbdzz"}),
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
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({
            r"a((b|c){1,})\2d",
            r"a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"abbd", "abbbdaccd", "zzaccdzz", "zzaccdabcbccdzz"}),
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
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({
            r"a((b|c){2,})\2d",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"abbbd", "abbbdabcbccd", "zzacccdzz", "zzacccdabcbccdzz"}),
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
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({
            r"a((b|c){2,})\2(?(2)d|e)",
            r"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"abbbd", "abbbdabcbccd", "zzacccdzz", "zzacccdabcbccdzz"}),
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
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({r"a(bc|de){2,}d"}),
        expected_operations=frozenset({"module.search"}),
        expected_haystacks=frozenset({"zzabcbcdzz"}),
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
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({r"a((bc|de){2,})?(?(1)d|e)"}),
        expected_operations=frozenset({"module.search"}),
        expected_haystacks=frozenset({"zzabcbcdzz"}),
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
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({r"a(?P<word>(bc|b)c){2,}d"}),
        expected_operations=frozenset({"pattern.fullmatch"}),
        expected_haystacks=frozenset({"abcbcbcbcd"}),
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
    _SourceTreeCombinedSliceExpectation(
        manifest_id="grouped-alternation-callable-replacement-boundary",
        slice_id="former-gap-callable-replacement-rows",
        required_syntax_features=("callable-replacement",),
        required_id_suffix="gap",
        expected_workload_ids=(
            "module-sub-callable-nested-grouped-alternation-cold-gap",
            "pattern-subn-callable-named-nested-grouped-alternation-purged-gap",
        ),
        expected_patterns=frozenset({
            r"a((b|c))d",
            r"a(?P<outer>(b|c))d",
        }),
        expected_operations=frozenset({"module.sub", "pattern.subn"}),
        expected_haystacks=frozenset({"abdacd", "acdabd"}),
        required_row_categories=(
            "alternation",
            "replacement",
            "callable",
            "gap",
        ),
    ),
    _SourceTreeCombinedSliceExpectation(
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
        expected_patterns=frozenset({
            r"a(b)?c(?(1)(de|df)|(eg|eh)){2}",
            r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}",
        }),
        expected_operations=frozenset({"module.sub", "module.subn", "pattern.sub", "pattern.subn"}),
        expected_haystacks=frozenset({
            "zzabcdedezz",
            "zzabcdfdfzz",
            "zzacegegzz",
            "zzacehehzz",
        }),
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

_COLLECTION_REPLACEMENT_SPLIT_OPERATIONS = frozenset(
    {"module.split", "pattern.split"}
)
_COLLECTION_REPLACEMENT_SUBSTITUTE_OPERATIONS = frozenset(
    {"module.sub", "module.subn", "pattern.sub", "pattern.subn"}
)


def _collection_replacement_keyword_parameter_name(
    workload: Any,
) -> str | None:
    if workload.operation in {"module.split", "pattern.split"}:
        return "maxsplit"
    if workload.operation in {"module.sub", "module.subn", "pattern.sub", "pattern.subn"}:
        return "count"
    return None


def _collection_replacement_positional_keyword_field(
    workload: Any,
) -> str | None:
    if workload.operation.startswith("module."):
        expected_keyword_field = (
            benchmarks._expected_duplicate_module_helper_keyword_field(workload)
            or benchmarks._expected_positional_module_helper_keyword_field(workload)
        )
    elif workload.operation.startswith("pattern."):
        expected_keyword_field = (
            benchmarks._expected_pattern_helper_positional_keyword_field(workload)
        )
    else:
        expected_keyword_field = None
    if expected_keyword_field is None:
        return None
    keyword_parameter = _collection_replacement_keyword_parameter_name(workload)
    if expected_keyword_field != keyword_parameter:
        return None
    return expected_keyword_field


def _is_collection_replacement_keyword_workload(workload: Any) -> bool:
    keyword_parameter = _collection_replacement_keyword_parameter_name(workload)
    if keyword_parameter is None or not workload.kwargs:
        return False
    keyword_names = tuple(workload.kwargs)
    if len(keyword_names) != 1:
        return False
    if keyword_names[0] == keyword_parameter:
        return True
    if _collection_replacement_positional_keyword_field(workload) is not None:
        return True
    expected_exception = workload.expected_exception
    if expected_exception is None or expected_exception.get("type") != "TypeError":
        return False
    keyword_name = keyword_names[0]
    message_substring = expected_exception.get("message_substring")
    if not isinstance(message_substring, str):
        return False
    if f"unexpected keyword argument '{keyword_name}'" in message_substring:
        return True
    if workload.operation.startswith("pattern."):
        helper_name = workload.operation.removeprefix("pattern.")
        return (
            message_substring
            == f"'{keyword_name}' is an invalid keyword argument for {helper_name}()"
        )
    return False


def _assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call(
    monkeypatch: pytest.MonkeyPatch,
    workload: benchmarks.Workload,
    *,
    expected_result: object | None,
    expected_exception_message: str | None = None,
    expected_field_names: list[str] | tuple[str, ...],
) -> None:
    observed_field_names = benchmark_test_support._record_numeric_materialization_fields(
        monkeypatch
    )

    re.purge()
    try:
        callback = benchmarks.build_callable(re, "re", workload)
        assert observed_field_names == []

        if expected_exception_message is None:
            assert callback() == expected_result
            assert callback() == expected_result
        else:
            with pytest.raises(TypeError, match=re.escape(expected_exception_message)):
                callback()
            with pytest.raises(TypeError, match=re.escape(expected_exception_message)):
                callback()

        assert observed_field_names == list(expected_field_names) * 2
    finally:
        re.purge()


def _is_collection_replacement_compiled_pattern_module_helper_keyword_workload(
    workload: Any,
) -> bool:
    return (
        _is_collection_replacement_keyword_workload(workload)
        and workload.use_compiled_pattern
        and workload.operation in {"module.split", "module.sub", "module.subn"}
        and workload.expected_exception is None
        and getattr(workload, "haystack_text_model", None) is None
    )


def _is_collection_replacement_compiled_pattern_keyword_error_workload(
    workload: Any,
) -> bool:
    return (
        _is_collection_replacement_keyword_workload(workload)
        and workload.use_compiled_pattern
        and workload.operation in {"module.split", "module.sub", "module.subn"}
        and workload.expected_exception is not None
        and getattr(workload, "haystack_text_model", None) is None
    )


@dataclass(frozen=True, slots=True)
class _CompiledPatternModuleHelperKeywordContractSpec:
    contract_filename: str
    expected_source_workload_ids: tuple[str, ...]
    manifest_timed_samples: int
    preserve_expected_exception: bool
    materializes_positional_keyword_field: bool
    notes: tuple[str, ...] = ()
    precompile_anchor_ids: tuple[str, ...] = ()

    def expected_materialized_field_names(
        self,
        source_workload: benchmarks.Workload,
    ) -> tuple[str, ...]:
        if self.materializes_positional_keyword_field:
            field_names: list[str] = []
            positional_keyword_field = _collection_replacement_positional_keyword_field(
                source_workload
            )
            if positional_keyword_field is not None:
                field_names.append(positional_keyword_field)
            field_names.extend(f"kwargs.{name}" for name in source_workload.kwargs)
            return tuple(field_names)

        keyword_parameter = _collection_replacement_keyword_parameter_name(
            source_workload
        )
        if keyword_parameter is None:
            raise AssertionError(
                "unexpected compiled-pattern module helper keyword workload "
                f"{source_workload.workload_id!r}"
            )
        return (f"kwargs.{keyword_parameter}",)

    def contract_builder_spec(self) -> object:
        excluded_fields = (
            benchmark_test_support.COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_PAYLOAD_DROP_FIELDS
        )
        if not self.preserve_expected_exception:
            excluded_fields = excluded_fields | {"expected_exception"}
        return _SourceTreeContractBuilderSpec(
            manifest_id="collection-replacement-boundary",
            excluded_fields=excluded_fields,
            manifest_timed_samples=self.manifest_timed_samples,
            timing_scope="module-helper-call",
            notes=self.notes,
        )


@dataclass(frozen=True, slots=True)
class _CompiledPatternModuleHelperKeywordContractSurface:
    case_id: str
    spec: _CompiledPatternModuleHelperKeywordContractSpec
    source_workloads_value: tuple[benchmarks.Workload, ...]
    precompile_source_workloads_value: tuple[benchmarks.Workload, ...] | None = None

    def source_workloads(self) -> tuple[benchmarks.Workload, ...]:
        return self.source_workloads_value

    def precompile_source_workloads(self) -> tuple[benchmarks.Workload, ...]:
        return self.precompile_source_workloads_value or self.source_workloads_value

    def expected_build_calls(
        self,
        source_workload: benchmarks.Workload,
    ) -> list[tuple[object, ...]]:
        return compiled_pattern_contract_expected_build_calls(
            source_workload,
            label="module helper keyword",
        )

    def expected_callback_call(
        self,
        source_workload: benchmarks.Workload,
    ) -> tuple[object, ...]:
        if source_workload.operation == "module.split":
            return (
                source_workload.operation,
                source_workload.haystack_payload(),
                source_workload.maxsplit,
                source_workload.flags,
                source_workload.kwargs,
            )
        if source_workload.operation in {"module.sub", "module.subn"}:
            return (
                source_workload.operation,
                source_workload.replacement_payload(),
                source_workload.haystack_payload(),
                source_workload.count,
                source_workload.flags,
                source_workload.kwargs,
            )
        raise AssertionError(
            "unexpected compiled-pattern module helper keyword workload operation "
            f"{source_workload.operation!r}"
        )

    def expected_callback_result(self, source_workload: benchmarks.Workload) -> object:
        if source_workload.operation == "module.subn":
            return ("module-result", 0)
        return "module-result"

    def run_cpython_helper_workload(
        self,
        workload: benchmarks.Workload,
    ) -> object:
        compiled_pattern = re.compile(workload.pattern_payload(), workload.flags)
        helper_name = workload.operation.removeprefix("module.")
        helper = getattr(re, helper_name)
        kwargs = dict(workload.kwargs)
        positional_keyword_field = _collection_replacement_positional_keyword_field(
            workload
        )

        if workload.operation == "module.split":
            args: list[object] = [compiled_pattern, workload.haystack_payload()]
            if positional_keyword_field == "maxsplit":
                args.append(workload.maxsplit)
            return helper(*args, **kwargs)

        if workload.operation in {"module.sub", "module.subn"}:
            args = [
                compiled_pattern,
                workload.replacement_payload(),
                workload.haystack_payload(),
            ]
            if positional_keyword_field == "count":
                args.append(workload.count)
            return helper(*args, **kwargs)

        raise AssertionError(
            "unexpected compiled-pattern module helper keyword workload operation "
            f"{workload.operation!r}"
        )

    def assert_outcome(
        self,
        source_workload: benchmarks.Workload,
        workload: benchmarks.Workload,
        round_tripped: benchmarks.Workload,
    ) -> None:
        if self.case_id == "success":
            benchmark_test_support.assert_benchmark_workload_matches_expected_result(
                round_tripped,
                benchmark_test_support.run_benchmark_workload_with_cpython(
                    source_workload
                ),
            )
            return

        if self.case_id == "keyword-error":
            with pytest.raises(TypeError) as expected_error:
                self.run_cpython_helper_workload(workload)
            with pytest.raises(TypeError) as observed_error:
                benchmark_test_support.run_benchmark_workload_with_cpython(
                    round_tripped
                )
            assert str(observed_error.value) == str(expected_error.value)
            return

        raise AssertionError(
            "unexpected compiled-pattern module helper keyword contract surface "
            f"{self.case_id!r}"
        )

    def assert_payload_round_trip(
        self,
        source_workload: benchmarks.Workload,
        payload: dict[str, object],
        round_tripped: benchmarks.Workload,
    ) -> None:
        expected_text_type = str if source_workload.text_model == "str" else bytes
        expected_exception = (
            source_workload.expected_exception
            if self.spec.preserve_expected_exception
            else None
        )
        assert payload["use_compiled_pattern"] is True
        assert round_tripped.use_compiled_pattern is True
        assert payload["count"] == source_workload.count
        assert round_tripped.count == source_workload.count
        assert payload["maxsplit"] == source_workload.maxsplit
        assert round_tripped.maxsplit == source_workload.maxsplit
        assert payload["kwargs"] == source_workload.kwargs
        assert round_tripped.kwargs == source_workload.kwargs
        assert payload.get("expected_exception") == expected_exception
        assert round_tripped.expected_exception == expected_exception
        assert payload.get("haystack_text_model") is None
        assert round_tripped.haystack_text_model is None
        assert round_tripped.text_model == source_workload.text_model
        assert isinstance(round_tripped.pattern_payload(), expected_text_type)
        assert isinstance(round_tripped.haystack_payload(), expected_text_type)
        if source_workload.replacement is not None:
            assert isinstance(
                round_tripped.replacement_payload(),
                expected_text_type,
            )
        for name, value in source_workload.kwargs.items():
            if type(value) is bool:
                assert type(payload["kwargs"][name]) is bool
                assert type(round_tripped.kwargs[name]) is bool


_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC = (
    _CompiledPatternModuleHelperKeywordContractSpec(
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
    _CompiledPatternModuleHelperKeywordContractSpec(
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
            _is_collection_replacement_compiled_pattern_module_helper_keyword_workload
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
    _CompiledPatternModuleHelperKeywordContractSurface(
        case_id="success",
        spec=_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC,
        source_workloads_value=_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS,
        precompile_source_workloads_value=(
            _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS
        ),
    ),
    _CompiledPatternModuleHelperKeywordContractSurface(
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

_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC = _SourceTreeContractBuilderSpec(
    manifest_id="pattern-boundary",
    excluded_fields=frozenset(
        {
            "manifest_id",
            "workload_id",
            "warmup_iterations",
            "sample_iterations",
            "timed_samples",
            "smoke",
        }
    ),
    timing_scope="pattern-helper-call",
)

_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_SPECS = {
    "collection-replacement-boundary": _SourceTreeContractBuilderSpec(
        manifest_id="collection-replacement-boundary",
        excluded_fields=(
            benchmark_test_support.COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS
        ),
        timing_scope="module-helper-call",
        notes=(
            "Ensures benchmark manifests keep the bounded "
            "compiled-pattern-first-argument wrong-text-model "
            "collection/replacement rows unresolved until helper invocation.",
        ),
    ),
    "module-boundary": _SourceTreeContractBuilderSpec(
        manifest_id="module-boundary",
        excluded_fields=(
            benchmark_test_support.COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS
        ),
        timing_scope="module-helper-call",
        notes=(
            "Ensures benchmark manifests keep the bounded "
            "compiled-pattern-first-argument wrong-text-model "
            "module-boundary rows unresolved until helper invocation.",
        ),
    ),
}

_COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS = (
    "module-split-on-bytes-string-purged-str-compiled-pattern",
    "module-findall-on-str-string-purged-bytes-compiled-pattern",
    "module-finditer-on-bytes-string-warm-str-compiled-pattern",
    "module-sub-on-bytes-string-warm-str-compiled-pattern",
    "module-subn-on-str-string-purged-bytes-compiled-pattern",
)
_COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS = (
    "module-search-on-bytes-string-warm-str-compiled-pattern",
    "module-match-on-str-string-purged-bytes-compiled-pattern",
    "module-fullmatch-on-bytes-string-warm-str-compiled-pattern",
)


def _compiled_pattern_wrong_text_model_specs() -> tuple[dict[str, object], ...]:
    return (
        {
            "case_id": "compiled_pattern_module_helper_wrong_text_model",
            "manifest_path": "collection_replacement_boundary.py",
            "include_workload": _is_collection_replacement_wrong_text_model_workload,
            "contract_manifest_id": "collection-replacement-boundary",
            "contract_filename": (
                "python_benchmark_compiled_pattern_collection_replacement_wrong_text_model_contract.py"
            ),
            "expected_source_workload_ids": (
                _COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
            ),
        },
        {
            "case_id": "compiled_pattern_module_boundary_wrong_text_model",
            "manifest_path": "module_boundary.py",
            "include_workload": (
                benchmark_test_support._is_module_workflow_compiled_pattern_wrong_text_model_workload
            ),
            "contract_manifest_id": "module-boundary",
            "contract_filename": (
                "python_benchmark_compiled_pattern_module_boundary_wrong_text_model_contract.py"
            ),
            "expected_source_workload_ids": (
                _COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
            ),
        },
    )


def _compiled_pattern_wrong_text_model_source_workloads(
    spec: dict[str, object],
) -> tuple[Workload, ...]:
    return benchmark_test_support.selected_manifest_workloads(
        spec["manifest_path"],
        include_workload=spec["include_workload"],
    )


@dataclass(frozen=True, slots=True)
class CompiledPatternModuleSuccessOwnerSpec:
    case_id: str
    manifest_path: Any
    include_workload_selectors: tuple[Callable[[Any], bool], ...]
    contract_manifest_id: str
    contract_filename: str
    note_surface: str
    expected_source_workload_ids: tuple[str, ...]
    preserved_payload_fields: tuple[str, ...]
    preserve_replacement_payload_typing: bool

    def source_workloads(self) -> tuple[Workload, ...]:
        return benchmark_test_support._contract_source_workloads(
            manifest_path=self.manifest_path,
            include_workload_selectors=self.include_workload_selectors,
            expected_source_workload_ids=self.expected_source_workload_ids,
            drift_message=(
                "compiled-pattern module contract source workloads drifted from the "
                f"{self.case_id} owner-spec surface"
            ),
        )

    def expected_build_calls(
        self,
        source_workload: Workload,
    ) -> list[tuple[object, ...]]:
        return compiled_pattern_contract_expected_build_calls(
            source_workload,
            label=f"{self.case_id} success",
        )

    def expected_callback_result(self, source_workload: Workload) -> object:
        callback_result, _, _, _ = _compiled_pattern_module_helper_route(
            source_workload,
            collection_replacement_callback_flags=source_workload.flags,
        )
        return callback_result

    def expected_callback_call(
        self,
        source_workload: Workload,
    ) -> tuple[object, ...]:
        _, callback_call, _, _ = _compiled_pattern_module_helper_route(
            source_workload,
            collection_replacement_callback_flags=source_workload.flags,
        )
        return callback_call

    def contract_builder_spec(self) -> _SourceTreeContractBuilderSpec:
        return _SourceTreeContractBuilderSpec(
            manifest_id=self.contract_manifest_id,
            excluded_fields=(
                benchmark_test_support.COMPILED_PATTERN_MODULE_SUCCESS_CONTRACT_EXCLUDED_FIELDS
            ),
            timing_scope="module-helper-call",
            notes=(
                "Ensures benchmark manifests keep the bounded "
                "compiled-pattern-first-argument successful "
                f"{self.note_surface} rows unresolved until helper invocation.",
            ),
        )


_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC = (
    CompiledPatternModuleSuccessOwnerSpec(
        case_id="collection-replacement",
        manifest_path=benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
        include_workload_selectors=(
            _is_collection_replacement_compiled_pattern_success_workload,
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
    CompiledPatternModuleSuccessOwnerSpec(
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
_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS = tuple(
    pytest.param(
        owner_spec,
        source_workload,
        id=f"{owner_spec.case_id}-{source_workload.workload_id}",
    )
    for owner_spec in _COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS
    for source_workload in owner_spec.source_workloads()
)

_COMPILED_PATTERN_MODULE_COMPILE_INT_ZERO_KEYWORD_SIGNATURE = (
    ("flags", "int", 0),
)
_COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_SIGNATURE = (
    ("flags", "bool", False),
)
_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_SIGNATURE = (
    ("flags", "int", int(re.IGNORECASE)),
)
_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS = ("abc",)
_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS = (
    "(?P<word>abc)",
)
_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION = {
    "type": "ValueError",
    "message_substring": "cannot process flags argument with a compiled pattern",
}


@dataclass(frozen=True, slots=True)
class _CompiledPatternModuleCompileContractRoute:
    surface_label: str
    excluded_fields: frozenset[str]
    note: str
    correctness_case_signature_builder: Callable[
        ["CompiledPatternModuleCompileContractCase", Any],
        tuple[Any, ...] | None,
    ]
    workload_signature_builder: Callable[
        ["CompiledPatternModuleCompileContractCase", Any],
        tuple[Any, ...],
    ]
    include_workload_selector: Callable[
        ["CompiledPatternModuleCompileContractCase", Any],
        bool,
    ]
    payload_round_trip_assertion: Callable[
        ["CompiledPatternModuleCompileContractCase", Workload, dict[str, object], Workload],
        None,
    ]
    cpython_dispatch: Callable[
        ["CompiledPatternModuleCompileContractCase", Workload],
        object,
    ]
    callback_flags_selector: Callable[
        ["CompiledPatternModuleCompileContractCase", Workload],
        object,
    ]

    def drift_message(
        self,
        contract_case: "CompiledPatternModuleCompileContractCase",
    ) -> str:
        return (
            f"compiled-pattern module.compile {self.surface_label} rows drifted from the "
            f"{contract_case.case_id} contract surface"
        )


@dataclass(frozen=True)
class CompiledPatternModuleCompileContractCase:
    route: _CompiledPatternModuleCompileContractRoute
    case_id: str
    manifest_path: pathlib.Path
    source_selectors: tuple[Callable[[Any], bool], ...]
    contract_filename: str
    anchor_contract_filename: str
    expected_anchor_pairs: tuple[tuple[str, str], ...]
    expected_build_calls_builder: Callable[[Workload], list[tuple[object, ...]]]
    keyword_signature: tuple[tuple[str, str, object], ...] | None = None
    allowed_patterns: tuple[str, ...] = ()
    expected_exception: dict[str, str] | None = None

    def required_keyword_signature(self) -> tuple[tuple[str, str, object], ...]:
        if self.keyword_signature is None:
            raise AssertionError(
                "missing compiled-pattern module.compile keyword signature for "
                f"{self.case_id!r}"
            )
        return self.keyword_signature

    def expected_source_workload_ids(self) -> tuple[str, ...]:
        return tuple(
            workload_id.removesuffix("-contract")
            for workload_id, _case_id in self.expected_anchor_pairs
        )

    def source_workloads(self) -> tuple[Workload, ...]:
        return benchmark_test_support._contract_source_workloads(
            manifest_path=self.manifest_path,
            include_workload_selectors=self.source_selectors,
            expected_source_workload_ids=self.expected_source_workload_ids(),
            drift_message=self.route.drift_message(self),
        )

    def manifest_excluded_fields(self) -> frozenset[str]:
        return self.route.excluded_fields

    def note(self) -> str:
        return self.route.note

    def correctness_case_signature(self, case: Any) -> tuple[Any, ...] | None:
        return self.route.correctness_case_signature_builder(self, case)

    def workload_signature(self, workload: Any) -> tuple[Any, ...]:
        return self.route.workload_signature_builder(self, workload)

    def include_workload(self, workload: Any) -> bool:
        return self.route.include_workload_selector(self, workload)

    def assert_payload_round_trip(
        self,
        source_workload: Workload,
        payload: dict[str, object],
        round_tripped: Workload,
    ) -> None:
        self.route.payload_round_trip_assertion(
            self,
            source_workload,
            payload,
            round_tripped,
        )

    def run_cpython_workload(self, workload: Workload) -> object:
        return self.route.cpython_dispatch(self, workload)

    def callback_flags(self, source_workload: Workload) -> object:
        return self.route.callback_flags_selector(self, source_workload)

    def expected_anchor_case_ids(
        self,
        manifest_path: pathlib.Path,
    ) -> dict[tuple[str, str], tuple[str, ...]]:
        return benchmark_test_support._workload_case_pair_anchor_expectations(
            manifest_path,
            self.expected_anchor_pairs,
        )

    def expected_build_calls(
        self,
        source_workload: Workload,
    ) -> list[tuple[object, ...]]:
        return self.expected_build_calls_builder(source_workload)

    def contract_builder_spec(self) -> _SourceTreeContractBuilderSpec:
        return _SourceTreeContractBuilderSpec(
            manifest_id="module-boundary",
            excluded_fields=self.manifest_excluded_fields(),
            manifest_timed_samples=2,
            timing_scope="module-helper-call",
            notes=(self.note(),),
        )


_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_CONTRACT_ROUTE = (
    _CompiledPatternModuleCompileContractRoute(
        surface_label="success",
        excluded_fields=(
            benchmark_test_support.COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS
        ),
        note=(
            "Ensures benchmark manifests keep the bounded compiled-pattern-first-argument "
            "module.compile rows unresolved until helper invocation."
        ),
        correctness_case_signature_builder=(
            lambda _contract_case, case: benchmark_test_support._module_workflow_compiled_pattern_compile_correctness_case_signature(
                case
            )
        ),
        workload_signature_builder=(
            lambda _contract_case, workload: benchmark_test_support._module_workflow_compiled_pattern_compile_workload_signature(
                workload
            )
        ),
        include_workload_selector=(
            lambda _contract_case, workload: benchmark_test_support._is_module_workflow_compiled_pattern_compile_workload(
                workload
            )
        ),
        payload_round_trip_assertion=(
            _assert_compiled_pattern_module_compile_success_payload_round_trip
        ),
        cpython_dispatch=(
            lambda _contract_case, workload: re.compile(
                re.compile(workload.pattern_payload(), workload.flags),
                workload.flags,
            )
        ),
        callback_flags_selector=(lambda _contract_case, source_workload: source_workload.flags),
    )
)

_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CONTRACT_ROUTE = (
    _CompiledPatternModuleCompileContractRoute(
        surface_label="keyword",
        excluded_fields=(
            benchmark_test_support.COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS
            | {"categories", "syntax_features"}
        ),
        note=(
            "Ensures benchmark manifests keep the bounded compiled-pattern-first-argument "
            "module.compile flags= keyword rows unresolved until helper invocation."
        ),
        correctness_case_signature_builder=(
            lambda contract_case, case: benchmark_test_support._module_workflow_compiled_pattern_compile_keyword_correctness_case_signature(
                case,
                keyword_signature=contract_case.required_keyword_signature(),
                allowed_patterns=contract_case.allowed_patterns,
            )
        ),
        workload_signature_builder=(
            lambda contract_case, workload: benchmark_test_support._module_workflow_compiled_pattern_compile_keyword_workload_signature(
                workload,
                keyword_label=contract_case.case_id,
                keyword_signature=contract_case.required_keyword_signature(),
                allowed_patterns=contract_case.allowed_patterns,
                expected_exception=contract_case.expected_exception,
            )
        ),
        include_workload_selector=(
            lambda contract_case, workload: benchmark_test_support._is_module_workflow_compiled_pattern_compile_keyword_workload(
                workload,
                keyword_signature=contract_case.required_keyword_signature(),
                allowed_patterns=contract_case.allowed_patterns,
                expected_exception=contract_case.expected_exception,
            )
        ),
        payload_round_trip_assertion=(
            _assert_compiled_pattern_module_compile_keyword_payload_round_trip
        ),
        cpython_dispatch=(
            lambda _contract_case, workload: re.compile(
                re.compile(workload.pattern_payload(), workload.flags),
                **workload.keyword_arguments(),
            )
        ),
        callback_flags_selector=(
            lambda _contract_case, source_workload: source_workload.keyword_arguments()["flags"]
        ),
    )
)


@dataclass(frozen=True)
class _CompiledPatternModuleContractAnchorLane:
    case_id: str
    contract_filename: str
    source_workloads: tuple[Workload, ...]
    contract_builder_spec: Callable[[], Any]
    expected_anchor_case_ids: Callable[
        [pathlib.Path],
        dict[tuple[str, str], tuple[str, ...]],
    ]
    anchor_case_ids: dict[tuple[Any, ...], tuple[str, ...]]
    workload_signature: Callable[[Any], tuple[Any, ...]]
    include_workload: Callable[[Any], bool]
    expected_anchor_pairs: tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class _CompiledPatternModuleCompileKeywordOwnerSpec:
    case_id: str
    anchor_definition_name: str
    keyword_signature: tuple[tuple[str, str, object], ...]
    allowed_patterns: tuple[str, ...]
    anchor_expectations: tuple[tuple[str, tuple[str, ...]], ...]
    contract_filename: str
    anchor_contract_filename: str
    expected_anchor_pairs: tuple[tuple[str, str], ...]
    expected_exception: dict[str, str] | None = None

    def correctness_case_signature(self, case: Any) -> tuple[Any, ...] | None:
        return benchmark_test_support._module_workflow_compiled_pattern_compile_keyword_correctness_case_signature(
            case,
            keyword_signature=self.keyword_signature,
            allowed_patterns=self.allowed_patterns,
        )

    def workload_signature(self, workload: Any) -> tuple[Any, ...]:
        return benchmark_test_support._module_workflow_compiled_pattern_compile_keyword_workload_signature(
            workload,
            keyword_label=self.case_id,
            keyword_signature=self.keyword_signature,
            allowed_patterns=self.allowed_patterns,
            expected_exception=self.expected_exception,
        )

    def includes_workload(self, workload: Any) -> bool:
        return benchmark_test_support._is_module_workflow_compiled_pattern_compile_keyword_workload(
            workload,
            keyword_signature=self.keyword_signature,
            allowed_patterns=self.allowed_patterns,
            expected_exception=self.expected_exception,
        )

    def expected_anchor_case_ids(self) -> dict[tuple[str, str], tuple[str, ...]]:
        return benchmark_test_support._definition_anchor_expectations(
            benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,
            dict(self.anchor_expectations),
        )

    def expected_anchor_workload_ids(self) -> tuple[str, ...]:
        return tuple(workload_id for workload_id, _ in self.anchor_expectations)

    def anchor_definition(
        self,
    ) -> benchmark_test_support.StandardBenchmarkAnchorContractDefinition:
        return benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name=self.anchor_definition_name,
            manifest_paths=(benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,),
            expected_anchor_case_ids=self.expected_anchor_case_ids(),
            include_workload=self.includes_workload,
            correctness_case_signature=self.correctness_case_signature,
            workload_signature=self.workload_signature,
            run_callback_result_parity=True,
        )

    def contract_case(self) -> CompiledPatternModuleCompileContractCase:
        return CompiledPatternModuleCompileContractCase(
            route=_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CONTRACT_ROUTE,
            case_id=self.case_id,
            manifest_path=benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,
            source_selectors=(self.includes_workload,),
            keyword_signature=self.keyword_signature,
            allowed_patterns=self.allowed_patterns,
            contract_filename=self.contract_filename,
            anchor_contract_filename=self.anchor_contract_filename,
            expected_anchor_pairs=self.expected_anchor_pairs,
            expected_build_calls_builder=partial(
                compiled_pattern_contract_expected_build_calls,
                label="module.compile contract",
            ),
            expected_exception=self.expected_exception,
        )


@dataclass(frozen=True, slots=True)
class _CompiledPatternModuleCompileSuccessOwnerSpec:
    anchor_definition_name: str
    allowed_patterns: tuple[str, ...]
    anchor_expectations: tuple[tuple[str, tuple[str, ...]], ...]
    expected_anchor_pairs: tuple[tuple[str, str], ...]

    def correctness_case_signature(self, case: Any) -> tuple[Any, ...] | None:
        return benchmark_test_support._module_workflow_compiled_pattern_compile_correctness_case_signature(
            case
        )

    def workload_signature(self, workload: Any) -> tuple[Any, ...]:
        return benchmark_test_support._module_workflow_compiled_pattern_compile_workload_signature(
            workload
        )

    def includes_workload(self, workload: Any) -> bool:
        return benchmark_test_support._is_module_workflow_compiled_pattern_compile_success_workload(
            workload,
            allowed_patterns=self.allowed_patterns,
        )

    def expected_anchor_case_ids(self) -> dict[tuple[str, str], tuple[str, ...]]:
        return benchmark_test_support._definition_anchor_expectations(
            benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,
            dict(self.anchor_expectations),
        )

    def expected_anchor_workload_ids(self) -> tuple[str, ...]:
        return tuple(workload_id for workload_id, _ in self.anchor_expectations)

    def anchor_definition(
        self,
    ) -> benchmark_test_support.StandardBenchmarkAnchorContractDefinition:
        return benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name=self.anchor_definition_name,
            manifest_paths=(benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,),
            expected_anchor_case_ids=self.expected_anchor_case_ids(),
            include_workload=self.includes_workload,
            correctness_case_signature=self.correctness_case_signature,
            workload_signature=self.workload_signature,
            run_callback_result_parity=True,
        )


def build_compiled_pattern_module_compile_contract_cases(
    *,
    manifest_path: pathlib.Path,
    expected_build_calls_builder: Callable[[Workload], list[tuple[object, ...]]],
    success_owner_specs: Iterable[Any],
    keyword_owner_specs: Iterable[Any],
) -> tuple[CompiledPatternModuleCompileContractCase, ...]:
    success_owner_specs = tuple(success_owner_specs)
    keyword_owner_specs = tuple(keyword_owner_specs)
    keyword_case_groups = tuple(
        owner_spec.contract_case() for owner_spec in keyword_owner_specs
    )
    return (
        CompiledPatternModuleCompileContractCase(
            route=_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_CONTRACT_ROUTE,
            case_id="success",
            manifest_path=manifest_path,
            source_selectors=tuple(
                owner_spec.includes_workload for owner_spec in success_owner_specs
            ),
            contract_filename=(
                "python_benchmark_compiled_pattern_module_compile_contract.py"
            ),
            anchor_contract_filename=(
                "python_benchmark_compiled_pattern_module_compile_anchor_contract.py"
            ),
            expected_anchor_pairs=tuple(
                anchor_pair
                for owner_spec in success_owner_specs
                for anchor_pair in owner_spec.expected_anchor_pairs
            ),
            expected_build_calls_builder=expected_build_calls_builder,
        ),
        *keyword_case_groups,
    )


def build_compiled_pattern_module_compile_contract_source_workload_params(
    contract_cases: Iterable[CompiledPatternModuleCompileContractCase],
) -> tuple[Any, ...]:
    return tuple(
        pytest.param(
            contract_case,
            source_workload,
            id=f"{contract_case.case_id}-{source_workload.workload_id}",
        )
        for contract_case in contract_cases
        for source_workload in contract_case.source_workloads()
    )


def build_compiled_pattern_module_contract_anchor_lanes(
    *,
    contract_cases: Iterable[CompiledPatternModuleCompileContractCase],
    published_case_ids_by_signature: Callable[
        [Callable[[Any], tuple[Any, ...] | None]],
        dict[tuple[Any, ...], tuple[str, ...]],
    ],
) -> tuple[_CompiledPatternModuleContractAnchorLane, ...]:
    contract_cases = tuple(contract_cases)
    return tuple(
        _CompiledPatternModuleContractAnchorLane(
            case_id=contract_case.case_id,
            contract_filename=contract_case.anchor_contract_filename,
            source_workloads=source_workloads,
            contract_builder_spec=contract_case.contract_builder_spec,
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


@cache
def _compiled_pattern_module_compile_success_owner_specs(
) -> tuple[_CompiledPatternModuleCompileSuccessOwnerSpec, ...]:
    return (
        _CompiledPatternModuleCompileSuccessOwnerSpec(
            anchor_definition_name=(
                "module-workflow-compiled-pattern-module-compile-literal-success"
            ),
            allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS,
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
        _CompiledPatternModuleCompileSuccessOwnerSpec(
            anchor_definition_name=(
                "module-workflow-compiled-pattern-module-compile-named-group-success"
            ),
            allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS,
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


@cache
def _compiled_pattern_module_compile_keyword_owner_specs(
) -> tuple[_CompiledPatternModuleCompileKeywordOwnerSpec, ...]:
    return (
        _CompiledPatternModuleCompileKeywordOwnerSpec(
            case_id="int-zero",
            anchor_definition_name=(
                "module-workflow-compiled-pattern-module-compile-flags-int-zero-keyword"
            ),
            keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_INT_ZERO_KEYWORD_SIGNATURE,
            allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS,
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
        _CompiledPatternModuleCompileKeywordOwnerSpec(
            case_id="int-zero-named-group",
            anchor_definition_name=(
                "module-workflow-compiled-pattern-module-compile-flags-int-zero-"
                "keyword-named-group"
            ),
            keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_INT_ZERO_KEYWORD_SIGNATURE,
            allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS,
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
        _CompiledPatternModuleCompileKeywordOwnerSpec(
            case_id="bool-false",
            anchor_definition_name=(
                "module-workflow-compiled-pattern-module-compile-flags-bool-false-keyword"
            ),
            keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_SIGNATURE,
            allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS,
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
        _CompiledPatternModuleCompileKeywordOwnerSpec(
            case_id="bool-false-named-group",
            anchor_definition_name=(
                "module-workflow-compiled-pattern-module-compile-flags-bool-false-"
                "keyword-named-group"
            ),
            keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_SIGNATURE,
            allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS,
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
        _CompiledPatternModuleCompileKeywordOwnerSpec(
            case_id="ignorecase",
            anchor_definition_name=(
                "module-workflow-compiled-pattern-module-compile-flags-ignorecase-"
                "keyword-rejection"
            ),
            keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_SIGNATURE,
            allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS,
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
            expected_exception=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION,
        ),
        _CompiledPatternModuleCompileKeywordOwnerSpec(
            case_id="ignorecase-named-group",
            anchor_definition_name=(
                "module-workflow-compiled-pattern-module-compile-flags-ignorecase-"
                "keyword-rejection-named-group"
            ),
            keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_SIGNATURE,
            allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS,
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
            expected_exception=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION,
        ),
    )


_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS = (
    _compiled_pattern_module_compile_success_owner_specs()
)

_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS = (
    _compiled_pattern_module_compile_keyword_owner_specs()
)


COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS = tuple(
    owner_spec.anchor_definition()
    for owner_spec in (
        *_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS,
        *_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS,
    )
)

_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES = (
    build_compiled_pattern_module_compile_contract_cases(
        manifest_path=benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,
        expected_build_calls_builder=partial(
            compiled_pattern_contract_expected_build_calls,
            label="module.compile contract",
        ),
        success_owner_specs=_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS,
        keyword_owner_specs=_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS,
    )
)

_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS = (
    build_compiled_pattern_module_compile_contract_source_workload_params(
        _COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES
    )
)

_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES = (
    build_compiled_pattern_module_contract_anchor_lanes(
        contract_cases=_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES,
        published_case_ids_by_signature=benchmark_test_support.published_case_ids_by_signature,
    )
)


def _collection_replacement_pattern_collection_correctness_case_signature(
    case: Any,
    *,
    case_ids: tuple[str, ...],
    expected_operation: str,
) -> tuple[Any, ...] | None:
    if case.case_id not in case_ids:
        return None
    if (
        case.operation != "pattern_call"
        or case.kwargs
        or case.helper != expected_operation.removeprefix("pattern.")
    ):
        return None
    return (
        expected_operation,
        case_pattern(case),
        benchmark_test_support.freeze_signature_value(list(case.args)),
        (),
        case.flags or 0,
        case.text_model or "str",
    )


def _is_collection_replacement_pattern_collection_workload(
    workload: Any,
    *,
    workload_ids: tuple[str, ...],
    expected_operation: str,
    requires_window_bounds: bool,
) -> bool:
    return (
        workload.workload_id in workload_ids
        and workload.operation == expected_operation
        and workload.pattern == "abc"
        and workload.expected_exception is None
        and not workload.use_compiled_pattern
        and workload.text_model in {"str", "bytes"}
        and not workload.kwargs
        and (workload.pos is not None) is requires_window_bounds
        and (workload.endpos is not None) is requires_window_bounds
    )


def _collection_replacement_pattern_collection_workload_signature(
    workload: Any,
    *,
    workload_ids: tuple[str, ...],
    expected_operation: str,
    requires_window_bounds: bool,
) -> tuple[Any, ...]:
    if not _is_collection_replacement_pattern_collection_workload(
        workload,
        workload_ids=workload_ids,
        expected_operation=expected_operation,
        requires_window_bounds=requires_window_bounds,
    ):
        raise AssertionError(
            "unexpected collection/replacement bounded "
            f"{expected_operation} workload {workload.workload_id!r}"
        )
    if requires_window_bounds:
        args: list[object] = [workload.haystack_payload()]
        if workload.pos is not None or workload.endpos is not None:
            args.append(0 if workload.pos is None else workload.pos)
        if workload.endpos is not None:
            args.append(workload.endpos)
    else:
        args = [workload.haystack_payload()]
        if workload.maxsplit is not None and not (
            type(workload.maxsplit) is int and workload.maxsplit == 0
        ):
            args.append(workload.maxsplit_argument())
    return (
        expected_operation,
        workload.pattern_payload(),
        benchmark_test_support.freeze_signature_value(list(args)),
        (),
        workload.flags,
        workload.text_model,
    )


@dataclass(frozen=True, slots=True)
class _CollectionReplacementCombinedSliceExpectation:
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

_COLLECTION_REPLACEMENT_PATTERN_FINDALL_WORKLOAD_CASE_PAIRS = (
    ("pattern-findall-bounded-warm-str", "pattern-findall-str-bounded"),
    (
        "pattern-findall-bounded-no-match-warm-str",
        "pattern-findall-str-bounded-no-match",
    ),
    ("pattern-findall-bounded-purged-bytes", "pattern-findall-bytes-bounded"),
)
_COLLECTION_REPLACEMENT_PATTERN_FINDALL_WORKLOAD_IDS = tuple(
    workload_id
    for workload_id, _ in _COLLECTION_REPLACEMENT_PATTERN_FINDALL_WORKLOAD_CASE_PAIRS
)
_COLLECTION_REPLACEMENT_PATTERN_FINDALL_CASE_IDS = tuple(
    case_id
    for _, case_id in _COLLECTION_REPLACEMENT_PATTERN_FINDALL_WORKLOAD_CASE_PAIRS
)
_COLLECTION_REPLACEMENT_PATTERN_FINDITER_WORKLOAD_CASE_PAIRS = (
    ("pattern-finditer-bounded-warm-str", "pattern-finditer-str-bounded"),
    (
        "pattern-finditer-bounded-no-match-warm-str",
        "pattern-finditer-str-bounded-no-match",
    ),
    (
        "pattern-finditer-bounded-purged-bytes",
        "pattern-finditer-bytes-bounded",
    ),
)
_COLLECTION_REPLACEMENT_PATTERN_FINDITER_WORKLOAD_IDS = tuple(
    workload_id
    for workload_id, _ in _COLLECTION_REPLACEMENT_PATTERN_FINDITER_WORKLOAD_CASE_PAIRS
)
_COLLECTION_REPLACEMENT_PATTERN_FINDITER_CASE_IDS = tuple(
    case_id
    for _, case_id in _COLLECTION_REPLACEMENT_PATTERN_FINDITER_WORKLOAD_CASE_PAIRS
)
_COLLECTION_REPLACEMENT_PATTERN_SPLIT_WORKLOAD_CASE_PAIRS = (
    ("pattern-split-no-match-warm-str", "pattern-split-str-no-match"),
    ("pattern-split-repeated-warm-str", "pattern-split-str-repeated"),
    ("pattern-split-maxsplit-purged-bytes", "pattern-split-bytes-maxsplit"),
)
_COLLECTION_REPLACEMENT_PATTERN_SPLIT_WORKLOAD_IDS = tuple(
    workload_id
    for workload_id, _ in _COLLECTION_REPLACEMENT_PATTERN_SPLIT_WORKLOAD_CASE_PAIRS
)
_COLLECTION_REPLACEMENT_PATTERN_SPLIT_CASE_IDS = tuple(
    case_id
    for _, case_id in _COLLECTION_REPLACEMENT_PATTERN_SPLIT_WORKLOAD_CASE_PAIRS
)

_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS = (
    ("pattern-sub-no-match-warm-str", "pattern-sub-str-no-match"),
    ("pattern-sub-single-match-warm-str", "pattern-sub-str-single-match"),
    ("pattern-sub-repeated-warm-str", "pattern-sub-str-repeated"),
    ("pattern-sub-count-one-warm-str", "pattern-sub-str-count-one"),
    ("pattern-sub-negative-count-warm-str", "pattern-sub-str-negative-count"),
    ("pattern-sub-bytes-no-match-purged-bytes", "pattern-sub-bytes-no-match"),
    (
        "pattern-sub-bytes-single-match-purged-bytes",
        "pattern-sub-bytes-single-match",
    ),
    (
        "pattern-sub-bytes-repeated-purged-bytes",
        "pattern-sub-bytes-repeated",
    ),
    (
        "pattern-sub-bytes-count-one-purged-bytes",
        "pattern-sub-bytes-count-one",
    ),
    (
        "pattern-sub-bytes-negative-count-purged-bytes",
        "pattern-sub-bytes-negative-count",
    ),
    ("pattern-subn-count-warm-str", "pattern-subn-str-count"),
    ("pattern-subn-single-match-warm-str", "pattern-subn-str-single-match"),
    ("pattern-subn-repeated-warm-str", "pattern-subn-str-repeated"),
    ("pattern-subn-negative-count-warm-str", "pattern-subn-str-negative-count"),
    ("pattern-subn-no-match-warm-str", "pattern-subn-str-no-match"),
    ("pattern-subn-bytes-count-purged-bytes", "pattern-subn-bytes-count"),
    (
        "pattern-subn-bytes-single-match-purged-bytes",
        "pattern-subn-bytes-single-match",
    ),
    (
        "pattern-subn-bytes-repeated-purged-bytes",
        "pattern-subn-bytes-repeated",
    ),
    (
        "pattern-subn-bytes-negative-count-purged-bytes",
        "pattern-subn-bytes-negative-count",
    ),
    (
        "pattern-subn-bytes-no-match-purged-bytes",
        "pattern-subn-bytes-no-match",
    ),
)
_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_WORKLOAD_IDS = tuple(
    workload_id
    for workload_id, _ in _COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS
)
_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_CASE_IDS = tuple(
    case_id
    for _, case_id in _COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS
)
_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_OPERATIONS = (
    "pattern.sub",
    "pattern.subn",
)
_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_TEXT_MODELS = ("str", "bytes")
_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_EXPECTED_OPERATION = (
    "pattern_call"
)
_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_OPERATION_PREFIX = "pattern"
_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_ARGS_OFFSET = 0

_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS = (
    ("module-sub-str-no-match-purged-str", "module-sub-str-no-match"),
    ("module-sub-str-single-match-purged-str", "module-sub-str-single-match"),
    ("module-sub-str-repeated-purged-str", "module-sub-str-repeated"),
    ("module-sub-str-count-one-purged-str", "module-sub-str-count-one"),
    ("module-sub-str-negative-count-purged-str", "module-sub-str-negative-count"),
    ("module-subn-str-count-purged-str", "module-subn-str-count"),
    (
        "module-subn-str-single-match-purged-str",
        "module-subn-str-single-match",
    ),
    ("module-subn-str-repeated-purged-str", "module-subn-str-repeated"),
    (
        "module-subn-str-negative-count-purged-str",
        "module-subn-str-negative-count",
    ),
    ("module-subn-str-no-match-purged-str", "module-subn-str-no-match"),
    ("module-sub-bytes-no-match-purged-bytes", "module-sub-bytes-no-match"),
    (
        "module-sub-bytes-single-match-purged-bytes",
        "module-sub-bytes-single-match",
    ),
    ("module-sub-bytes-repeated-purged-bytes", "module-sub-bytes-repeated"),
    ("module-sub-bytes-count-one-purged-bytes", "module-sub-bytes-count-one"),
    ("module-subn-bytes-count-purged-bytes", "module-subn-bytes-count"),
    (
        "module-subn-bytes-single-match-purged-bytes",
        "module-subn-bytes-single-match",
    ),
    ("module-subn-bytes-repeated-purged-bytes", "module-subn-bytes-repeated"),
    ("module-subn-bytes-no-match-purged-bytes", "module-subn-bytes-no-match"),
)
_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_WORKLOAD_IDS = tuple(
    workload_id
    for workload_id, _ in _COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS
)
_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_CASE_IDS = tuple(
    case_id
    for _, case_id in _COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS
)
_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_OPERATIONS = (
    "module.sub",
    "module.subn",
)
_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_TEXT_MODELS = ("str", "bytes")
_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_EXPECTED_OPERATION = "module_call"
_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_OPERATION_PREFIX = "module"
_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_ARGS_OFFSET = 1
_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_ALLOWED_COUNTS = (-1, 0, 1)


def _collection_replacement_standard_benchmark_definitions() -> tuple[object, ...]:
    return (
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-module-positional-indexlike",
            manifest_paths=(benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
                benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
                {
                    "module-split-maxsplit-indexlike-positional-purged-bytes": (
                        "workflow-module-split-maxsplit-indexlike-positional-bytes",
                    ),
                    "module-sub-count-indexlike-positional-warm-str": (
                        "workflow-module-sub-count-indexlike-positional-str",
                    ),
                    "module-subn-count-indexlike-positional-purged-bytes": (
                        "workflow-module-subn-count-indexlike-positional-bytes",
                    ),
                    "pattern-split-maxsplit-indexlike-positional-warm-str": (
                        "workflow-pattern-split-str-maxsplit-indexlike-positional",
                    ),
                    "pattern-sub-count-indexlike-positional-purged-bytes": (
                        "workflow-pattern-sub-count-indexlike-positional-bytes",
                    ),
                    "pattern-subn-count-indexlike-positional-warm-str": (
                        "workflow-pattern-subn-count-indexlike-positional-str",
                    ),
                },
            ),
            include_workload=_is_collection_replacement_positional_indexlike_workload,
            correctness_case_signature=(
                _module_workflow_positional_indexlike_correctness_case_signature
            ),
            workload_signature=_collection_replacement_positional_indexlike_workload_signature,
            run_callback_result_parity=True,
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-keyword",
            manifest_paths=(benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
                benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
                {
                    "module-split-maxsplit-keyword-purged-bytes": (
                        "workflow-module-split-maxsplit-keyword-bytes",
                    ),
                    "module-split-maxsplit-bool-keyword-purged-bytes": (
                        "workflow-module-split-maxsplit-bool-false-bytes",
                    ),
                    "module-split-maxsplit-indexlike-keyword-purged-bytes": (
                        "workflow-module-split-maxsplit-indexlike-bytes",
                    ),
                    "module-split-maxsplit-keyword-purged-str-compiled-pattern": (
                        "workflow-module-split-maxsplit-keyword-str-compiled-pattern",
                    ),
                    "module-split-maxsplit-indexlike-keyword-purged-bytes-compiled-pattern": (
                        "workflow-module-split-maxsplit-indexlike-bytes-compiled-pattern",
                    ),
                    "module-split-maxsplit-bool-keyword-purged-bytes-compiled-pattern": (
                        "workflow-module-split-maxsplit-bool-false-bytes-compiled-pattern",
                    ),
                    "module-split-duplicate-maxsplit-keyword-purged-str": (
                        "workflow-module-split-duplicate-maxsplit-keyword",
                    ),
                    "module-split-unexpected-keyword-purged-str": (
                        "workflow-module-split-unexpected-keyword",
                    ),
                    "module-split-unexpected-keyword-purged-bytes": (
                        "workflow-module-split-unexpected-keyword-bytes",
                    ),
                    "module-split-duplicate-maxsplit-keyword-purged-str-compiled-pattern": (
                        "workflow-module-split-duplicate-maxsplit-keyword-str-compiled-pattern",
                    ),
                    "module-split-unexpected-keyword-purged-bytes-compiled-pattern": (
                        "workflow-module-split-unexpected-keyword-bytes-compiled-pattern",
                    ),
                    "module-sub-count-keyword-warm-str": (
                        "workflow-module-sub-count-keyword-str",
                    ),
                    "module-sub-count-bool-keyword-warm-str": (
                        "workflow-module-sub-count-bool-true-str",
                    ),
                    "module-sub-count-bool-false-keyword-warm-str": (
                        "workflow-module-sub-count-bool-false-str",
                    ),
                    "module-sub-count-indexlike-keyword-warm-str": (
                        "workflow-module-sub-count-indexlike-str",
                    ),
                    "module-sub-count-keyword-warm-str-compiled-pattern": (
                        "workflow-module-sub-count-keyword-str-compiled-pattern",
                    ),
                    "module-sub-count-indexlike-keyword-warm-bytes-compiled-pattern": (
                        "workflow-module-sub-count-indexlike-bytes-compiled-pattern",
                    ),
                    "module-sub-count-bool-keyword-warm-str-compiled-pattern": (
                        "workflow-module-sub-count-bool-true-str-compiled-pattern",
                    ),
                    "module-sub-count-bool-false-keyword-warm-str-compiled-pattern": (
                        "workflow-module-sub-count-bool-false-str-compiled-pattern",
                    ),
                    "module-sub-duplicate-count-keyword-warm-str": (
                        "workflow-module-sub-duplicate-count-keyword",
                    ),
                    "module-sub-unexpected-keyword-purged-str": (
                        "workflow-module-sub-unexpected-keyword",
                    ),
                    "module-sub-unexpected-keyword-after-positional-count-purged-str": (
                        "workflow-module-sub-unexpected-keyword-after-positional-count",
                    ),
                    "module-sub-count-alias-keyword-purged-str": (
                        "workflow-module-sub-count-alias-keyword",
                    ),
                    "module-sub-duplicate-count-keyword-warm-str-compiled-pattern": (
                        "workflow-module-sub-duplicate-count-keyword-str-compiled-pattern",
                    ),
                    "module-sub-unexpected-keyword-purged-str-compiled-pattern": (
                        "workflow-module-sub-unexpected-keyword-str-compiled-pattern",
                    ),
                    "module-sub-unexpected-keyword-after-positional-count-purged-str-compiled-pattern": (
                        "workflow-module-sub-unexpected-keyword-after-positional-count-str-compiled-pattern",
                    ),
                    "module-sub-count-alias-keyword-purged-str-compiled-pattern": (
                        "workflow-module-sub-count-alias-keyword-str-compiled-pattern",
                    ),
                    "module-subn-count-keyword-purged-bytes": (
                        "workflow-module-subn-count-keyword-bytes",
                    ),
                    "module-subn-count-bool-keyword-purged-bytes": (
                        "workflow-module-subn-count-bool-false-bytes",
                    ),
                    "module-subn-count-bool-true-keyword-purged-bytes": (
                        "workflow-module-subn-count-bool-true-bytes",
                    ),
                    "module-subn-count-indexlike-keyword-purged-bytes": (
                        "workflow-module-subn-count-indexlike-bytes",
                    ),
                    "module-subn-duplicate-count-keyword-warm-bytes": (
                        "workflow-module-subn-duplicate-count-keyword-bytes",
                    ),
                    "module-subn-unexpected-keyword-purged-bytes": (
                        "workflow-module-subn-unexpected-keyword-bytes",
                    ),
                    "module-subn-unexpected-keyword-after-positional-count-purged-bytes": (
                        "workflow-module-subn-unexpected-keyword-after-positional-count-bytes",
                    ),
                    "module-subn-count-alias-keyword-purged-bytes": (
                        "workflow-module-subn-count-alias-keyword-bytes",
                    ),
                    "module-subn-count-keyword-purged-bytes-compiled-pattern": (
                        "workflow-module-subn-count-keyword-bytes-compiled-pattern",
                    ),
                    "module-subn-count-indexlike-keyword-purged-str-compiled-pattern": (
                        "workflow-module-subn-count-indexlike-str-compiled-pattern",
                    ),
                    "module-subn-count-bool-keyword-purged-bytes-compiled-pattern": (
                        "workflow-module-subn-count-bool-false-bytes-compiled-pattern",
                    ),
                    "module-subn-count-bool-true-keyword-purged-bytes-compiled-pattern": (
                        "workflow-module-subn-count-bool-true-bytes-compiled-pattern",
                    ),
                    "module-subn-duplicate-count-keyword-warm-bytes-compiled-pattern": (
                        "workflow-module-subn-duplicate-count-keyword-bytes-compiled-pattern",
                    ),
                    "module-subn-unexpected-keyword-purged-bytes-compiled-pattern": (
                        "workflow-module-subn-unexpected-keyword-bytes-compiled-pattern",
                    ),
                    "module-subn-unexpected-keyword-after-positional-count-purged-bytes-compiled-pattern": (
                        "workflow-module-subn-unexpected-keyword-after-positional-count-bytes-compiled-pattern",
                    ),
                    "module-subn-count-alias-keyword-purged-bytes-compiled-pattern": (
                        "workflow-module-subn-count-alias-keyword-bytes-compiled-pattern",
                    ),
                    "pattern-split-maxsplit-keyword-warm-str": (
                        "workflow-pattern-split-str-maxsplit-keyword",
                    ),
                    "pattern-split-maxsplit-bool-keyword-warm-str": (
                        "workflow-pattern-split-str-maxsplit-bool-true",
                    ),
                    "pattern-split-maxsplit-indexlike-keyword-warm-str": (
                        "workflow-pattern-split-str-maxsplit-indexlike",
                    ),
                    "pattern-split-duplicate-maxsplit-keyword-warm-str": (
                        "workflow-pattern-split-duplicate-maxsplit-keyword-str",
                    ),
                    "pattern-split-unexpected-keyword-warm-bytes": (
                        "workflow-pattern-split-unexpected-keyword-bytes",
                    ),
                    "pattern-sub-count-keyword-purged-bytes": (
                        "workflow-pattern-sub-count-keyword-bytes",
                    ),
                    "pattern-sub-count-bool-keyword-purged-bytes": (
                        "workflow-pattern-sub-count-bool-false-bytes",
                    ),
                    "pattern-sub-count-bool-true-keyword-purged-bytes": (
                        "workflow-pattern-sub-count-bool-true-bytes",
                    ),
                    "pattern-sub-count-indexlike-keyword-purged-bytes": (
                        "workflow-pattern-sub-count-indexlike-bytes",
                    ),
                    "pattern-sub-duplicate-count-keyword-warm-str": (
                        "workflow-pattern-sub-duplicate-count-keyword-str",
                    ),
                    "pattern-sub-unexpected-keyword-warm-str": (
                        "workflow-pattern-sub-unexpected-keyword-str",
                    ),
                    "pattern-sub-unexpected-keyword-after-positional-count-warm-str": (
                        "workflow-pattern-sub-unexpected-keyword-after-positional-count-str",
                    ),
                    "pattern-sub-count-alias-keyword-warm-str": (
                        "workflow-pattern-sub-count-alias-keyword-str",
                    ),
                    "pattern-subn-count-keyword-warm-str": (
                        "workflow-pattern-subn-count-keyword-str",
                    ),
                    "pattern-subn-count-bool-keyword-warm-str": (
                        "workflow-pattern-subn-count-bool-true-str",
                    ),
                    "pattern-subn-count-bool-false-keyword-warm-str": (
                        "workflow-pattern-subn-count-bool-false-str",
                    ),
                    "pattern-subn-count-indexlike-keyword-warm-str": (
                        "workflow-pattern-subn-count-indexlike-str",
                    ),
                    "pattern-subn-duplicate-count-keyword-warm-bytes": (
                        "workflow-pattern-subn-duplicate-count-keyword-bytes",
                    ),
                    "pattern-subn-unexpected-keyword-warm-bytes": (
                        "workflow-pattern-subn-unexpected-keyword-bytes",
                    ),
                    "pattern-subn-unexpected-keyword-after-positional-count-warm-bytes": (
                        "workflow-pattern-subn-unexpected-keyword-after-positional-count-bytes",
                    ),
                    "pattern-subn-count-alias-keyword-warm-bytes": (
                        "workflow-pattern-subn-count-alias-keyword-bytes",
                    ),
                },
            ),
            include_workload=_is_collection_replacement_keyword_workload,
            correctness_case_signature=(
                _collection_replacement_keyword_correctness_case_signature
            ),
            workload_signature=_collection_replacement_keyword_workload_signature,
            run_callback_result_parity=True,
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-compiled-pattern-literal-success",
            manifest_paths=(benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
                benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
                {
                    "module-split-literal-warm-str-compiled-pattern": (
                        "workflow-module-split-str-compiled-pattern",
                    ),
                    "module-findall-literal-purged-bytes-compiled-pattern": (
                        "workflow-module-findall-bytes-compiled-pattern",
                    ),
                    "module-finditer-literal-warm-str-compiled-pattern": (
                        "workflow-module-finditer-str-compiled-pattern",
                    ),
                    "module-sub-literal-warm-str-compiled-pattern": (
                        "workflow-module-sub-str-compiled-pattern",
                    ),
                    "module-subn-literal-purged-bytes-compiled-pattern": (
                        "workflow-module-subn-bytes-compiled-pattern",
                    ),
                },
            ),
            include_workload=(
                _is_collection_replacement_compiled_pattern_success_workload
            ),
            correctness_case_signature=(
                _collection_replacement_compiled_pattern_success_correctness_case_signature
            ),
            workload_signature=(
                _collection_replacement_compiled_pattern_success_workload_signature
            ),
            run_callback_result_parity=True,
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-compiled-pattern-wrong-text-model",
            manifest_paths=(benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
                benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
                {
                    "module-split-on-bytes-string-purged-str-compiled-pattern": (
                        "workflow-module-split-str-compiled-pattern-on-bytes-string",
                    ),
                    "module-findall-on-str-string-purged-bytes-compiled-pattern": (
                        "workflow-module-findall-bytes-compiled-pattern-on-str-string",
                    ),
                    "module-finditer-on-bytes-string-warm-str-compiled-pattern": (
                        "workflow-module-finditer-str-compiled-pattern-on-bytes-string",
                    ),
                    "module-sub-on-bytes-string-warm-str-compiled-pattern": (
                        "workflow-module-sub-str-compiled-pattern-on-bytes-string",
                    ),
                    "module-subn-on-str-string-purged-bytes-compiled-pattern": (
                        "workflow-module-subn-bytes-compiled-pattern-on-str-string",
                    ),
                },
            ),
            include_workload=_is_collection_replacement_wrong_text_model_workload,
            correctness_case_signature=(
                _collection_replacement_wrong_text_model_correctness_case_signature
            ),
            workload_signature=_collection_replacement_wrong_text_model_workload_signature,
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="pattern-helper-collection-replacement-wrong-text-model",
            manifest_paths=(benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._definition_anchor_expectations(
                benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
                {
                    "pattern-split-on-bytes-string-warm-str": (
                        "workflow-pattern-split-str-pattern-on-bytes-string",
                    ),
                    "pattern-sub-on-bytes-string-warm-str": (
                        "workflow-pattern-sub-str-pattern-on-bytes-string",
                    ),
                    "pattern-subn-on-str-string-purged-bytes": (
                        "workflow-pattern-subn-bytes-pattern-on-str-string",
                    ),
                },
            ),
            include_workload=_is_collection_replacement_pattern_wrong_text_model_workload,
            correctness_case_signature=(
                _collection_replacement_pattern_wrong_text_model_correctness_case_signature
            ),
            workload_signature=(
                _collection_replacement_pattern_wrong_text_model_workload_signature
            ),
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-pattern-findall-bounded",
            manifest_paths=(benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._workload_case_pair_anchor_expectations(
                benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
                _COLLECTION_REPLACEMENT_PATTERN_FINDALL_WORKLOAD_CASE_PAIRS,
            ),
            include_workload=partial(
                _is_collection_replacement_pattern_collection_workload,
                workload_ids=_COLLECTION_REPLACEMENT_PATTERN_FINDALL_WORKLOAD_IDS,
                expected_operation="pattern.findall",
                requires_window_bounds=True,
            ),
            correctness_case_signature=partial(
                _collection_replacement_pattern_collection_correctness_case_signature,
                case_ids=_COLLECTION_REPLACEMENT_PATTERN_FINDALL_CASE_IDS,
                expected_operation="pattern.findall",
            ),
            workload_signature=partial(
                _collection_replacement_pattern_collection_workload_signature,
                workload_ids=_COLLECTION_REPLACEMENT_PATTERN_FINDALL_WORKLOAD_IDS,
                expected_operation="pattern.findall",
                requires_window_bounds=True,
            ),
            run_callback_result_parity=True,
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-pattern-finditer-bounded",
            manifest_paths=(benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._workload_case_pair_anchor_expectations(
                benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
                _COLLECTION_REPLACEMENT_PATTERN_FINDITER_WORKLOAD_CASE_PAIRS,
            ),
            include_workload=partial(
                _is_collection_replacement_pattern_collection_workload,
                workload_ids=_COLLECTION_REPLACEMENT_PATTERN_FINDITER_WORKLOAD_IDS,
                expected_operation="pattern.finditer",
                requires_window_bounds=True,
            ),
            correctness_case_signature=partial(
                _collection_replacement_pattern_collection_correctness_case_signature,
                case_ids=_COLLECTION_REPLACEMENT_PATTERN_FINDITER_CASE_IDS,
                expected_operation="pattern.finditer",
            ),
            workload_signature=partial(
                _collection_replacement_pattern_collection_workload_signature,
                workload_ids=_COLLECTION_REPLACEMENT_PATTERN_FINDITER_WORKLOAD_IDS,
                expected_operation="pattern.finditer",
                requires_window_bounds=True,
            ),
            run_callback_result_parity=True,
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-pattern-split",
            manifest_paths=(benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._workload_case_pair_anchor_expectations(
                benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
                _COLLECTION_REPLACEMENT_PATTERN_SPLIT_WORKLOAD_CASE_PAIRS,
            ),
            include_workload=partial(
                _is_collection_replacement_pattern_collection_workload,
                workload_ids=_COLLECTION_REPLACEMENT_PATTERN_SPLIT_WORKLOAD_IDS,
                expected_operation="pattern.split",
                requires_window_bounds=False,
            ),
            correctness_case_signature=partial(
                _collection_replacement_pattern_collection_correctness_case_signature,
                case_ids=_COLLECTION_REPLACEMENT_PATTERN_SPLIT_CASE_IDS,
                expected_operation="pattern.split",
            ),
            workload_signature=partial(
                _collection_replacement_pattern_collection_workload_signature,
                workload_ids=_COLLECTION_REPLACEMENT_PATTERN_SPLIT_WORKLOAD_IDS,
                expected_operation="pattern.split",
                requires_window_bounds=False,
            ),
            run_callback_result_parity=True,
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-module-literal-replacement",
            manifest_paths=(benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._workload_case_pair_anchor_expectations(
                benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
                _COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS,
            ),
            include_workload=partial(
                _is_collection_replacement_literal_replacement_workload,
                workload_ids=_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_WORKLOAD_IDS,
                operations=_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_OPERATIONS,
                text_models=_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_TEXT_MODELS,
                allowed_counts=_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_ALLOWED_COUNTS,
            ),
            correctness_case_signature=partial(
                _collection_replacement_literal_replacement_correctness_case_signature,
                case_ids=_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_CASE_IDS,
                expected_operation=(
                    _COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_EXPECTED_OPERATION
                ),
                operation_prefix=(
                    _COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_OPERATION_PREFIX
                ),
                args_offset=_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_ARGS_OFFSET,
            ),
            workload_signature=partial(
                _collection_replacement_literal_replacement_workload_signature,
                include_workload=partial(
                    _is_collection_replacement_literal_replacement_workload,
                    workload_ids=(
                        _COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_WORKLOAD_IDS
                    ),
                    operations=(
                        _COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_OPERATIONS
                    ),
                    text_models=(
                        _COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_TEXT_MODELS
                    ),
                    allowed_counts=(
                        _COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_ALLOWED_COUNTS
                    ),
                ),
                workload_kind="module",
            ),
            run_callback_result_parity=True,
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-pattern-literal-replacement",
            manifest_paths=(benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._workload_case_pair_anchor_expectations(
                benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
                _COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS,
            ),
            include_workload=partial(
                _is_collection_replacement_literal_replacement_workload,
                workload_ids=_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_WORKLOAD_IDS,
                operations=_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_OPERATIONS,
                text_models=_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_TEXT_MODELS,
            ),
            correctness_case_signature=partial(
                _collection_replacement_literal_replacement_correctness_case_signature,
                case_ids=_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_CASE_IDS,
                expected_operation=(
                    _COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_EXPECTED_OPERATION
                ),
                operation_prefix=(
                    _COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_OPERATION_PREFIX
                ),
                args_offset=(
                    _COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_ARGS_OFFSET
                ),
            ),
            workload_signature=partial(
                _collection_replacement_literal_replacement_workload_signature,
                include_workload=partial(
                    _is_collection_replacement_literal_replacement_workload,
                    workload_ids=(
                        _COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_WORKLOAD_IDS
                    ),
                    operations=(
                        _COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_OPERATIONS
                    ),
                    text_models=(
                        _COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_TEXT_MODELS
                    ),
                ),
                workload_kind="direct Pattern",
            ),
            run_callback_result_parity=True,
        ),
        benchmark_test_support.StandardBenchmarkAnchorContractDefinition(
            name="collection-replacement-grouped-callable-replacement",
            manifest_paths=(benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,),
            expected_anchor_case_ids=benchmark_test_support._workload_case_pair_anchor_expectations(
                benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
                _COLLECTION_REPLACEMENT_GROUPED_CALLABLE_WORKLOAD_CASE_PAIRS,
            ),
            include_workload=_is_collection_replacement_grouped_callable_workload,
            correctness_case_signature=(
                _collection_replacement_grouped_callable_correctness_case_signature
            ),
            workload_signature=_collection_replacement_grouped_callable_workload_signature,
            run_callback_result_parity=True,
        ),
    )


def _collection_replacement_literal_replacement_correctness_case_signature(
    case: Any,
    *,
    case_ids: tuple[str, ...] | None = None,
    expected_operation: str | None = None,
    operation_prefix: str | None = None,
    args_offset: int | None = None,
) -> tuple[Any, ...] | None:
    if expected_operation is None or operation_prefix is None or args_offset is None:
        raise AssertionError(
            "literal replacement correctness signatures require explicit "
            "operation metadata"
        )
    if case.manifest_id != "collection-replacement-workflows":
        return None
    if case_ids is not None and case.case_id not in case_ids:
        return None
    if case.operation != expected_operation or case.kwargs:
        return None
    if case.helper not in {"sub", "subn"}:
        return None
    if case.use_compiled_pattern:
        return None
    pattern = case_pattern(case)
    if pattern not in {"abc", b"abc"}:
        return None
    if len(case.args) <= args_offset:
        return None
    if case.args[args_offset] not in {"x", b"x"}:
        return None
    trailing_args = case.args[args_offset:]
    if len(trailing_args) not in {2, 3}:
        return None
    if len(trailing_args) == 3 and type(trailing_args[2]) is not int:
        return None
    return (
        f"{operation_prefix}.{case.helper}",
        pattern,
        benchmark_test_support.freeze_signature_value(list(trailing_args)),
        (),
        case.flags or 0,
        case.text_model or "str",
    )


def _collection_replacement_literal_replacement_workload_signature(
    workload: Any,
    *,
    include_workload: Callable[[Any], bool],
    workload_kind: str,
) -> tuple[Any, ...]:
    if not include_workload(workload):
        raise AssertionError(
            "unexpected collection/replacement "
            f"{workload_kind} literal replacement workload {workload.workload_id!r}"
        )
    args = [
        workload.replacement_payload(),
        workload.haystack_payload(),
    ]
    if workload.count:
        args.append(workload.count_argument())
    return (
        workload.operation,
        workload.pattern_payload(),
        benchmark_test_support.freeze_signature_value(args),
        (),
        workload.flags,
        workload.text_model,
    )
def _module_workflow_positional_indexlike_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.helper not in {"split", "sub", "subn"} or case.kwargs:
        return None
    if case.operation == "module_call":
        if case.use_compiled_pattern or not case.include_pattern_arg:
            return None
    elif case.operation != "pattern_call":
        return None
    if not any(hasattr(argument, "__index__") for argument in case.args):
        return None
    return (
        case.helper,
        case_pattern(case),
        module_workflow_positional_args_signature(case.args),
        case.text_model or "str",
    )


def _collection_replacement_positional_indexlike_workload_args(
    workload: Any,
) -> tuple[object, ...]:
    if workload.operation in {"module.split", "pattern.split"}:
        return (
            workload.haystack_payload(),
            workload.maxsplit,
        )
    if workload.operation in _COLLECTION_REPLACEMENT_SUBSTITUTE_OPERATIONS:
        return (
            workload.replacement_payload(),
            workload.haystack_payload(),
            workload.count,
        )
    raise AssertionError(
        "unexpected collection/replacement positional-indexlike workload operation "
        f"{workload.operation!r}"
    )


def _collection_replacement_positional_indexlike_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_collection_replacement_positional_indexlike_workload(workload):
        raise AssertionError(
            "unexpected collection/replacement positional-indexlike workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation.removeprefix("module.").removeprefix("pattern."),
        workload.pattern_payload(),
        module_workflow_positional_args_signature(
            _collection_replacement_positional_indexlike_workload_args(workload)
        ),
        workload.text_model,
    )


def _is_collection_replacement_positional_indexlike_workload(workload: Any) -> bool:
    keyword_parameter = _collection_replacement_keyword_parameter_name(workload)
    if keyword_parameter == "maxsplit":
        parameter_payload = workload.maxsplit
    elif keyword_parameter == "count":
        parameter_payload = workload.count
    else:
        parameter_payload = None
    return (
        not workload.kwargs
        and workload.expected_exception is None
        and benchmark_test_support._is_encoded_indexlike_payload(parameter_payload)
    )

def _collection_replacement_keyword_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if not case.kwargs:
        return None
    if case.helper not in {"split", "sub", "subn"}:
        return None
    use_compiled_pattern = False
    if case.operation == "module_call":
        use_compiled_pattern = case.use_compiled_pattern
    elif case.operation != "pattern_call":
        return None
    return (
        f"{'module' if case.operation == 'module_call' else 'pattern'}.{case.helper}",
        case_pattern(case),
        benchmark_test_support.freeze_signature_value(list(case.args)),
        module_workflow_keyword_kwargs_signature(case.kwargs),
        use_compiled_pattern,
        case.flags or 0,
        case.text_model or "str",
    )


def _collection_replacement_keyword_workload_args(
    workload: Any,
) -> tuple[object, ...]:
    positional_keyword_field = _collection_replacement_positional_keyword_field(
        workload
    )
    if workload.operation in {"module.split", "pattern.split"}:
        args: list[object] = [workload.haystack_payload()]
        if positional_keyword_field == "maxsplit":
            args.append(workload.maxsplit)
        return tuple(args)
    if workload.operation in _COLLECTION_REPLACEMENT_SUBSTITUTE_OPERATIONS:
        args: list[object] = [
            workload.replacement_payload(),
            workload.haystack_payload(),
        ]
        if positional_keyword_field == "count":
            args.append(workload.count)
        return tuple(args)
    raise AssertionError(
        "unexpected collection/replacement keyword workload operation "
        f"{workload.operation!r}"
    )


def _collection_replacement_keyword_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_collection_replacement_keyword_workload(workload):
        raise AssertionError(
            "unexpected collection/replacement keyword workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        benchmark_test_support.freeze_signature_value(
            list(_collection_replacement_keyword_workload_args(workload))
        ),
        module_workflow_keyword_kwargs_signature(workload.kwargs),
        workload.use_compiled_pattern,
        workload.flags,
        workload.text_model,
    )


def _collection_replacement_compiled_pattern_success_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or case.kwargs or not case.use_compiled_pattern:
        return None
    if case.helper not in {"split", "findall", "finditer", "sub", "subn"}:
        return None
    operation = f"module.{case.helper}"
    haystack_index = _collection_replacement_wrong_text_model_haystack_index(operation)
    if len(case.args) <= haystack_index:
        return None
    haystack = case.args[haystack_index]
    case_text_model = case.text_model or "str"
    if case_text_model == "str" and not isinstance(haystack, str):
        return None
    if case_text_model == "bytes" and not isinstance(haystack, bytes):
        return None
    return (
        operation,
        case_pattern(case),
        benchmark_test_support.freeze_signature_value(list(case.args)),
        case.use_compiled_pattern,
        case.flags or 0,
        case_text_model,
    )


def _collection_replacement_compiled_pattern_success_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_collection_replacement_compiled_pattern_success_workload(workload):
        raise AssertionError(
            "unexpected collection/replacement compiled-pattern success workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        benchmark_test_support.freeze_signature_value(
            list(_collection_replacement_wrong_text_model_workload_args(workload))
        ),
        workload.use_compiled_pattern,
        workload.flags,
        workload.text_model,
    )


def _pattern_helper_collection_replacement_keyword_error_workload(
    *,
    operation: str,
    haystack: str,
    kwargs_payload: dict[str, object],
    replacement: object,
    count: object,
    maxsplit: object,
    expected_exception: dict[str, str],
    text_model: str,
) -> benchmarks.Workload:
    return benchmarks.workload_from_payload(
        {
            "manifest_id": "python-benchmark-pattern-collection-replacement-keyword-contract",
            "workload_id": f"{operation}-keyword-error-materialization-contract",
            "bucket": operation.replace("pattern.", "pattern-"),
            "family": "module",
            "operation": operation,
            "pattern": "abc",
            "haystack": haystack,
            "replacement": replacement,
            "expected_exception": expected_exception,
            "flags": 0,
            "count": count,
            "maxsplit": maxsplit,
            "kwargs": kwargs_payload,
            "text_model": text_model,
            "cache_mode": "warm",
            "timing_scope": "pattern-helper-call",
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
            "notes": [],
            "categories": [],
            "syntax_features": [],
            "smoke": False,
        }
    )


_PATTERN_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS = (
    "pattern-split-duplicate-maxsplit-keyword-warm-str",
    "pattern-split-unexpected-keyword-warm-bytes",
    "pattern-sub-duplicate-count-keyword-warm-str",
    "pattern-sub-unexpected-keyword-warm-str",
    "pattern-sub-unexpected-keyword-after-positional-count-warm-str",
    "pattern-sub-count-alias-keyword-warm-str",
    "pattern-subn-duplicate-count-keyword-warm-bytes",
    "pattern-subn-unexpected-keyword-warm-bytes",
    "pattern-subn-unexpected-keyword-after-positional-count-warm-bytes",
    "pattern-subn-count-alias-keyword-warm-bytes",
)


def _is_collection_replacement_pattern_helper_keyword_error_workload(
    workload: Any,
) -> bool:
    return (
        _is_collection_replacement_keyword_workload(workload)
        and not workload.use_compiled_pattern
        and workload.operation in {"pattern.split", "pattern.sub", "pattern.subn"}
        and workload.expected_exception is not None
        and getattr(workload, "haystack_text_model", None) is None
        and workload.workload_id
        in _PATTERN_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS
    )


_PATTERN_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS = benchmark_test_support._contract_source_workloads(
    manifest_path=benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
    include_workload_selectors=(
        _is_collection_replacement_pattern_helper_keyword_error_workload,
    ),
    expected_source_workload_ids=(
        _PATTERN_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS
    ),
    drift_message=(
        "pattern helper collection/replacement keyword-error surface drifted "
        "from the live source workload surface"
    ),
)


_MODULE_HELPER_BOUNDARY_KEYWORD_ERROR_WORKLOAD_IDS = (
    "module-search-duplicate-flags-keyword-warm-str",
    "module-fullmatch-unexpected-keyword-purged-str",
)

_MODULE_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS = (
    "module-split-duplicate-maxsplit-keyword-purged-str",
    "module-split-unexpected-keyword-purged-str",
    "module-split-unexpected-keyword-purged-bytes",
    "module-sub-duplicate-count-keyword-warm-str",
    "module-sub-unexpected-keyword-purged-str",
    "module-sub-unexpected-keyword-after-positional-count-purged-str",
    "module-sub-count-alias-keyword-purged-str",
    "module-subn-unexpected-keyword-after-positional-count-purged-bytes",
    "module-subn-count-alias-keyword-purged-bytes",
)


def _is_collection_replacement_module_helper_keyword_error_workload(
    workload: Any,
) -> bool:
    return (
        _is_collection_replacement_keyword_workload(workload)
        and not workload.use_compiled_pattern
        and workload.operation in {"module.split", "module.sub", "module.subn"}
        and workload.expected_exception is not None
        and getattr(workload, "haystack_text_model", None) is None
        and workload.workload_id
        in _MODULE_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS
    )


_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS = benchmark_test_support._contract_source_workloads(
    manifest_path=benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,
    include_workload_selectors=(
        benchmark_test_support._is_module_workflow_keyword_error_workload,
    ),
    expected_source_workload_ids=_MODULE_HELPER_BOUNDARY_KEYWORD_ERROR_WORKLOAD_IDS,
    drift_message=(
        "module helper keyword-error surface drifted from the live source "
        "workload surface"
    ),
) + benchmark_test_support._contract_source_workloads(
    manifest_path=benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
    include_workload_selectors=(
        _is_collection_replacement_module_helper_keyword_error_workload,
    ),
    expected_source_workload_ids=(
        _MODULE_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS
    ),
    drift_message=(
        "module helper collection/replacement keyword-error surface drifted "
        "from the live source workload surface"
    ),
)


def _assert_keyword_error_workload_probe_measured(
    source_workload: Any,
    *,
    import_name: str,
    adapter_name: str,
) -> None:
    payload = benchmarks.workload_to_payload(source_workload)
    round_tripped = benchmarks.workload_from_payload(payload)

    assert payload["workload_id"] == source_workload.workload_id
    assert round_tripped.workload_id == source_workload.workload_id
    assert payload["expected_exception"] == source_workload.expected_exception
    assert round_tripped.expected_exception == source_workload.expected_exception
    assert payload["kwargs"] == source_workload.kwargs
    assert round_tripped.kwargs == source_workload.kwargs

    probe = benchmarks.run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name=import_name,
        adapter_name=adapter_name,
    )

    assert probe["status"] == "measured"
    assert probe["median_ns"] > 0


_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CONTRACT_EXCLUDED_FIELDS = frozenset(
    {
        "manifest_id",
        "workload_id",
        "warmup_iterations",
        "sample_iterations",
        "timed_samples",
        "smoke",
    }
)
_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS = (
    "pattern-split-on-bytes-string-warm-str",
    "pattern-sub-on-bytes-string-warm-str",
    "pattern-subn-on-str-string-purged-bytes",
)
_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CONTRACT_SPEC = (
    SimpleNamespace(
        manifest_id="collection-replacement-boundary",
        excluded_fields=_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_CONTRACT_EXCLUDED_FIELDS,
        manifest_timed_samples=2,
        timing_scope="pattern-helper-call",
        notes=(),
    )
)

def _collection_replacement_wrong_text_model_expected_callback_call(
    source_workload: Any,
) -> tuple[object, ...]:
    if source_workload.operation == "pattern.split":
        return (
            "pattern.split",
            source_workload.haystack_payload(),
            (source_workload.maxsplit_argument(),),
            {},
        )
    if source_workload.operation in {"pattern.sub", "pattern.subn"}:
        return (
            source_workload.operation,
            source_workload.replacement_payload(),
            source_workload.haystack_payload(),
            (source_workload.count_argument(),),
            {},
        )
    raise AssertionError(
        "unexpected direct Pattern collection/replacement wrong-text-model "
        f"workload operation {source_workload.operation!r}"
    )


def _collection_replacement_wrong_text_model_expected_callback_result(
    source_workload: Any,
) -> object:
    if source_workload.operation == "pattern.subn":
        return ("pattern-result", 0)
    if source_workload.operation in {"pattern.split", "pattern.sub"}:
        return "pattern-result"
    raise AssertionError(
        "unexpected direct Pattern collection/replacement wrong-text-model "
        f"workload operation {source_workload.operation!r}"
    )


def _run_cpython_collection_replacement_wrong_text_model_workload(
    workload: Any,
) -> object:
    compiled_pattern = re.compile(workload.pattern_payload(), workload.flags)
    helper_name = workload.operation.removeprefix("pattern.")
    if workload.operation == "pattern.split":
        return getattr(compiled_pattern, helper_name)(
            workload.haystack_payload(),
            workload.maxsplit_argument(),
        )
    if workload.operation in {"pattern.sub", "pattern.subn"}:
        return getattr(compiled_pattern, helper_name)(
            workload.replacement_payload(),
            workload.haystack_payload(),
            workload.count_argument(),
        )
    raise AssertionError(
        "unexpected direct Pattern collection/replacement wrong-text-model "
        f"workload operation {workload.operation!r}"
    )


def _collection_replacement_wrong_text_model_haystack_index(operation: str) -> int:
    if operation in {"module.split", "module.findall", "module.finditer"}:
        return 0
    if operation in {"module.sub", "module.subn"}:
        return 1
    raise AssertionError(
        "unexpected collection/replacement wrong-text-model workload operation "
        f"{operation!r}"
    )


def _collection_replacement_wrong_text_model_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or case.kwargs or not case.use_compiled_pattern:
        return None
    if case.helper not in {"split", "findall", "finditer", "sub", "subn"}:
        return None
    operation = f"module.{case.helper}"
    haystack_index = _collection_replacement_wrong_text_model_haystack_index(operation)
    if len(case.args) <= haystack_index:
        return None
    haystack = case.args[haystack_index]
    case_text_model = case.text_model or "str"
    if case_text_model == "str" and not isinstance(haystack, bytes):
        return None
    if case_text_model == "bytes" and not isinstance(haystack, str):
        return None
    return (
        operation,
        case_pattern(case),
        benchmark_test_support.freeze_signature_value(list(case.args)),
        case.use_compiled_pattern,
        case.flags or 0,
        case_text_model,
    )


def _collection_replacement_wrong_text_model_workload_args(
    workload: Any,
) -> tuple[object, ...]:
    if workload.operation == "module.split":
        return (
            workload.haystack_payload(),
            workload.maxsplit_argument(),
        )
    if workload.operation in {"module.findall", "module.finditer"}:
        return (workload.haystack_payload(),)
    if workload.operation in {"module.sub", "module.subn"}:
        return (
            workload.replacement_payload(),
            workload.haystack_payload(),
            workload.count_argument(),
        )
    raise AssertionError(
        "unexpected collection/replacement wrong-text-model workload operation "
        f"{workload.operation!r}"
    )


def _collection_replacement_wrong_text_model_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_collection_replacement_wrong_text_model_workload(workload):
        raise AssertionError(
            "unexpected collection/replacement wrong-text-model workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        benchmark_test_support.freeze_signature_value(
            list(_collection_replacement_wrong_text_model_workload_args(workload))
        ),
        workload.use_compiled_pattern,
        workload.flags,
        workload.text_model,
    )
def _pattern_collection_replacement_wrong_text_model_haystack_index(
    operation: str,
) -> int:
    if operation == "pattern.split":
        return 0
    if operation in {"pattern.sub", "pattern.subn"}:
        return 1
    raise AssertionError(
        "unexpected direct Pattern collection/replacement wrong-text-model "
        f"workload operation {operation!r}"
    )


def _collection_replacement_pattern_wrong_text_model_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "pattern_call" or case.kwargs:
        return None
    if case.helper not in {"split", "sub", "subn"}:
        return None
    operation = f"pattern.{case.helper}"
    haystack_index = _pattern_collection_replacement_wrong_text_model_haystack_index(
        operation
    )
    case_args = list(case.args)
    if len(case_args) <= haystack_index:
        return None
    haystack = case_args[haystack_index]
    case_text_model = case.text_model or "str"
    if case_text_model == "str" and not isinstance(haystack, bytes):
        return None
    if case_text_model == "bytes" and not isinstance(haystack, str):
        return None
    return (
        operation,
        case_pattern(case),
        benchmark_test_support.freeze_signature_value(case_args),
        (),
        case.flags or 0,
        case_text_model,
    )


def _collection_replacement_pattern_wrong_text_model_workload_args(
    workload: Any,
) -> tuple[object, ...]:
    if workload.operation == "pattern.split":
        args: list[object] = [workload.haystack_payload()]
        if workload.maxsplit:
            args.append(workload.maxsplit_argument())
        return tuple(args)
    if workload.operation in {"pattern.sub", "pattern.subn"}:
        args = [
            workload.replacement_payload(),
            workload.haystack_payload(),
        ]
        if workload.count:
            args.append(workload.count_argument())
        return tuple(args)
    raise AssertionError(
        "unexpected direct Pattern collection/replacement wrong-text-model "
        f"workload operation {workload.operation!r}"
    )


def _collection_replacement_pattern_wrong_text_model_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_collection_replacement_pattern_wrong_text_model_workload(workload):
        raise AssertionError(
            "unexpected direct Pattern collection/replacement wrong-text-model "
            f"workload {workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        benchmark_test_support.freeze_signature_value(
            list(
                _collection_replacement_pattern_wrong_text_model_workload_args(
                    workload
                )
            )
        ),
        (),
        workload.flags,
        workload.text_model,
    )


def _is_collection_replacement_pattern_wrong_text_model_workload(
    workload: Any,
) -> bool:
    return (
        getattr(workload, "haystack_text_model", None) is not None
        and not workload.kwargs
        and not workload.use_compiled_pattern
        and workload.operation in {"pattern.split", "pattern.sub", "pattern.subn"}
        and workload.expected_exception is not None
        and workload.expected_exception.get("type") == "TypeError"
    )


_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOADS = (
    benchmark_test_support._contract_source_workloads(
        manifest_path=benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
        include_workload_selectors=(
            _is_collection_replacement_pattern_wrong_text_model_workload,
        ),
        expected_source_workload_ids=(
            _COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
        ),
        drift_message=(
            "direct Pattern collection/replacement wrong-text-model surface "
            "drifted from the live source workload surface"
        ),
    )
)


def _is_collection_replacement_literal_replacement_workload(
    workload: Any,
    *,
    workload_ids: tuple[str, ...],
    operations: tuple[str, ...],
    text_models: tuple[str, ...],
    allowed_counts: tuple[int, ...] | None = None,
) -> bool:
    return (
        workload.workload_id in workload_ids
        and workload.operation in operations
        and workload.pattern == "abc"
        and workload.replacement == "x"
        and workload.expected_exception is None
        and not workload.use_compiled_pattern
        and workload.text_model in text_models
        and (allowed_counts is None or workload.count in allowed_counts)
        and workload.pos is None
        and workload.endpos is None
        and not workload.kwargs
    )


_COLLECTION_REPLACEMENT_GROUPED_CALLABLE_WORKLOAD_CASE_PAIRS = (
    ("module-sub-callable-grouped-warm-str", "module-sub-callable-grouped-str"),
    ("module-sub-callable-grouped-warm-bytes", "module-sub-callable-grouped-bytes"),
    (
        "pattern-subn-callable-named-grouped-warm-str",
        "pattern-subn-callable-named-grouped-str",
    ),
    (
        "pattern-subn-callable-named-grouped-purged-bytes",
        "pattern-subn-callable-named-grouped-bytes",
    ),
)


def _is_collection_replacement_grouped_callable_workload(workload: Any) -> bool:
    return (
        workload.workload_id
        in tuple(
            workload_id
            for workload_id, _ in _COLLECTION_REPLACEMENT_GROUPED_CALLABLE_WORKLOAD_CASE_PAIRS
        )
        and workload.operation in {"module.sub", "pattern.subn"}
        and workload.pattern in {
            "(abc)",
            b"(abc)",
            "(?P<word>abc)",
            b"(?P<word>abc)",
        }
        and workload.expected_exception is None
        and not workload.use_compiled_pattern
        and workload.text_model in {"str", "bytes"}
        and workload.pos is None
        and workload.endpos is None
        and not workload.kwargs
    )


def _collection_replacement_grouped_callable_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.case_id not in tuple(
        case_id
        for _, case_id in _COLLECTION_REPLACEMENT_GROUPED_CALLABLE_WORKLOAD_CASE_PAIRS
    ):
        return None
    if case.kwargs or case.use_compiled_pattern:
        return None
    if case.operation not in {"module_call", "pattern_call"}:
        return None
    if case.helper not in {"sub", "subn"}:
        return None
    replacement_signature = callable_match_group_signature(
        case_replacement_argument(case)
    )
    if replacement_signature is None:
        return None
    args = [case_text_argument(case)]
    if case.helper == "subn":
        count = case.args[-1]
        if type(count) is not int:
            return None
        args.append(count)
    operation_prefix = "module" if case.operation == "module_call" else "pattern"
    return (
        f"{operation_prefix}.{case.helper}",
        case_pattern(case),
        replacement_signature,
        benchmark_test_support.freeze_signature_value(args),
        (),
        case.flags or 0,
        case.text_model or "str",
    )


def _collection_replacement_grouped_callable_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_collection_replacement_grouped_callable_workload(workload):
        raise AssertionError(
            "unexpected collection/replacement grouped callable workload "
            f"{workload.workload_id!r}"
        )
    replacement_signature = callable_match_group_signature(
        workload.replacement_payload()
    )
    if replacement_signature is None:
        raise AssertionError(
            "expected callable_match_group replacement for grouped callable workload "
            f"{workload.workload_id!r}"
        )
    args = [workload.haystack_payload()]
    if workload.count:
        args.append(workload.count_argument())
    return (
        workload.operation,
        workload.pattern_payload(),
        replacement_signature,
        benchmark_test_support.freeze_signature_value(args),
        (),
        workload.flags,
        workload.text_model,
    )


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


def _workload_ids_for_text_model(
    workload_stems: tuple[str, ...],
    *,
    text_model: str,
) -> tuple[str, ...]:
    suffix = "-bytes" if text_model == "bytes" else "-str"
    return tuple(f"{stem}{suffix}" for stem in workload_stems)


CONDITIONAL_GROUP_EXISTS_CALLABLE_BYTES_WORKLOAD_IDS = (
    "module-sub-callable-numbered-conditional-group-exists-replacement-warm-bytes",
    "module-subn-callable-numbered-conditional-group-exists-replacement-first-match-only-warm-bytes",
    "pattern-sub-callable-numbered-conditional-group-exists-replacement-purged-bytes",
    "pattern-subn-callable-numbered-conditional-group-exists-replacement-first-match-only-purged-bytes",
    "module-sub-callable-named-conditional-group-exists-replacement-warm-bytes",
    "module-subn-callable-named-conditional-group-exists-replacement-first-match-only-warm-bytes",
    "pattern-sub-callable-named-conditional-group-exists-replacement-purged-bytes",
    "pattern-subn-callable-named-conditional-group-exists-replacement-purged-bytes",
    "module-subn-callable-numbered-conditional-group-exists-replacement-absent-exception-warm-bytes",
    "pattern-subn-callable-numbered-conditional-group-exists-replacement-absent-exception-purged-bytes",
    "module-subn-callable-named-conditional-group-exists-replacement-absent-exception-warm-bytes",
    "pattern-subn-callable-named-conditional-group-exists-replacement-absent-exception-purged-bytes",
)
CONDITIONAL_GROUP_EXISTS_CALLABLE_NEGATIVE_COUNT_STR_WORKLOAD_IDS = (
    "module-sub-callable-numbered-conditional-group-exists-replacement-negative-count-warm-str",
    "module-subn-callable-named-conditional-group-exists-replacement-negative-count-warm-str",
    "pattern-sub-callable-numbered-conditional-group-exists-replacement-negative-count-purged-str",
    "pattern-subn-callable-named-conditional-group-exists-replacement-negative-count-purged-str",
)
CONDITIONAL_GROUP_EXISTS_CALLABLE_NEGATIVE_COUNT_BYTES_WORKLOAD_IDS = (
    "module-sub-callable-numbered-conditional-group-exists-replacement-negative-count-warm-bytes",
    "module-subn-callable-named-conditional-group-exists-replacement-negative-count-warm-bytes",
    "pattern-sub-callable-numbered-conditional-group-exists-replacement-negative-count-purged-bytes",
    "pattern-subn-callable-named-conditional-group-exists-replacement-negative-count-purged-bytes",
)
_CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_STEMS = (
    "module-sub-callable-numbered-conditional-group-exists-replacement-none-count-warm",
    "pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-purged",
    "module-sub-callable-named-conditional-group-exists-replacement-none-count-warm",
    "pattern-sub-callable-named-conditional-group-exists-replacement-none-count-purged",
    "module-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-warm",
    "pattern-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-purged",
    "module-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-warm",
    "pattern-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-purged",
    "module-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-warm",
    "module-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-warm",
    "pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-purged",
    "pattern-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-purged",
    "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm",
    "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm",
    "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged",
    "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged",
)
CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS = _workload_ids_for_text_model(
    _CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_STEMS,
    text_model="str",
)
CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS = _workload_ids_for_text_model(
    _CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_STEMS,
    text_model="bytes",
)
CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_IDS = (
    CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS
    + CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS
)
CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_STR_WORKLOAD_IDS = (
    "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-warm-gap",
    "module-subn-callable-numbered-conditional-group-exists-alternation-heavy-replacement-warm-str",
    "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-purged-str",
    "pattern-subn-callable-numbered-conditional-group-exists-alternation-heavy-replacement-purged-str",
    "module-sub-callable-named-conditional-group-exists-alternation-heavy-replacement-warm-str",
    "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-warm-str",
    "pattern-sub-callable-named-conditional-group-exists-alternation-heavy-replacement-purged-str",
    "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-purged-str",
    "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-str",
    "module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-str",
    "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-warm-str",
    "module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-str",
    "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-str",
    "pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-str",
    "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-negative-count-purged-str",
    "pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-str",
)
CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS = (
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
)
CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS = (
    CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_STR_WORKLOAD_IDS[:8]
    + CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS[:8]
    + CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_STR_WORKLOAD_IDS[8:]
    + CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS[8:]
)
CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS = (
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
)
CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS = (
    "module-sub-template-numbered-conditional-group-exists-replacement-negative-count-warm-str",
    "module-subn-template-named-conditional-group-exists-replacement-negative-count-warm-str",
    "pattern-sub-template-numbered-conditional-group-exists-replacement-negative-count-purged-str",
    "pattern-subn-template-named-conditional-group-exists-replacement-negative-count-purged-str",
)
CONDITIONAL_GROUP_EXISTS_TEMPLATE_ROUND_TRIP_WORKLOAD_IDS = (
    CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS[:8]
    + CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS
    + CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS[8:]
)


CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS = (
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
)
CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS = (
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
)
CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_NEGATIVE_COUNT_BYTES_WORKLOAD_IDS = (
    "module-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-warm-bytes",
    "module-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-warm-bytes",
    "pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-negative-count-purged-bytes",
    "pattern-subn-callable-named-nested-conditional-group-exists-replacement-negative-count-purged-bytes",
)
_CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_WORKLOAD_STEMS = (
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
CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS = _workload_ids_for_text_model(
    _CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_WORKLOAD_STEMS,
    text_model="str",
)
CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS = _workload_ids_for_text_model(
    _CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_WORKLOAD_STEMS,
    text_model="bytes",
)

COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS = (
    _CollectionReplacementCombinedSliceExpectation(
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
        expected_patterns=frozenset(
            {
            r"a(b)?c(?(1)d|e)",
            r"a(?P<word>b)?c(?(word)d|e)",
            }
        ),
        expected_operations=frozenset(
            {"module.sub", "module.subn", "pattern.sub", "pattern.subn"}
        ),
        expected_haystacks=frozenset({"zzabcdzz", "zzacezz", "abcdaceabcd"}),
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "replacement",
            "template",
        ),
    ),
    _CollectionReplacementCombinedSliceExpectation(
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
        expected_patterns=frozenset(
            {
            r"a(b)?c(?(1)d|e)",
            r"a(?P<word>b)?c(?(word)d|e)",
            }
        ),
        expected_operations=frozenset(
            {"module.sub", "module.subn", "pattern.sub", "pattern.subn"}
        ),
        expected_haystacks=frozenset({"zzabcdzz", "zzabcdacezz", "abcdaceabcd"}),
        required_row_categories=(
            "grouped",
            "optional-group",
            "conditional",
            "group-exists",
            "replacement",
            "callable",
        ),
    ),
    _CollectionReplacementCombinedSliceExpectation(
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
        expected_patterns=frozenset(
            {
            r"a(b)?c(?(1)d|e)",
            r"a(?P<word>b)?c(?(word)d|e)",
            }
        ),
        expected_operations=frozenset({"module.subn", "pattern.subn"}),
        expected_haystacks=frozenset({"zzacezz"}),
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
    _CollectionReplacementCombinedSliceExpectation(
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
        expected_patterns=frozenset(
            {
            r"a(b)?c(?(1)d|e)",
            r"a(?P<word>b)?c(?(word)d|e)",
            }
        ),
        expected_operations=frozenset(
            {"module.sub", "module.subn", "pattern.sub", "pattern.subn"}
        ),
        expected_haystacks=frozenset({"zzabcdzz", "zzacezz", "abcdaceabcd"}),
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
    _CollectionReplacementCombinedSliceExpectation(
        manifest_id="conditional-group-exists-boundary",
        slice_id="alternation-heavy-callable-replacement-rows",
        required_syntax_features=("conditionals", "alternation", "callable-replacement"),
        excluded_syntax_features=("quantifiers",),
        required_categories=("alternation-heavy", "replacement", "callable"),
        expected_workload_ids=CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS,
        expected_patterns=frozenset(
            {
            r"a(b)?c(?(1)(de|df)|(eg|eh))",
            r"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))",
            }
        ),
        expected_operations=frozenset(
            {"module.sub", "module.subn", "pattern.sub", "pattern.subn"}
        ),
        expected_haystacks=frozenset(
            {"zzabcdezz", "zzabcdfzz", "zzacegzz", "zzacehzz"}
        ),
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
    _CollectionReplacementCombinedSliceExpectation(
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
        expected_workload_ids=CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS,
        expected_patterns=frozenset(
            {
            r"a(b)?c(?(1)(?(1)d|e)|f)",
            r"a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
            }
        ),
        expected_operations=frozenset(
            {"module.sub", "module.subn", "pattern.sub", "pattern.subn"}
        ),
        expected_haystacks=frozenset({"zzabcdzz", "zzabcezz", "zzacezz", "zzacfzz"}),
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
    _CollectionReplacementCombinedSliceExpectation(
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
        expected_workload_ids=CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS,
        expected_patterns=frozenset(
            {
            r"a(b)?c(?(1)(?(1)d|e)|f)",
            r"a(?P<word>b)?c(?(word)(?(word)d|e)|f)",
            }
        ),
        expected_operations=frozenset(
            {"module.sub", "module.subn", "pattern.sub", "pattern.subn"}
        ),
        expected_haystacks=frozenset({"zzabcdzz", "zzabcezz", "zzacezz", "zzacfzz"}),
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
    _CollectionReplacementCombinedSliceExpectation(
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
        expected_patterns=frozenset(
            {
            r"a(b)?c(?(1)d|e){2}",
            r"a(?P<word>b)?c(?(word)d|e){2}",
            }
        ),
        expected_operations=frozenset(
            {"module.sub", "module.subn", "pattern.sub", "pattern.subn"}
        ),
        expected_haystacks=frozenset({"zzabcddzz", "zzaceezz", "zzabcdezz", "zzacedzz"}),
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
    _CollectionReplacementCombinedSliceExpectation(
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
        expected_patterns=frozenset(
            {
            r"a(b)?c(?(1)d|e){2}",
            r"a(?P<word>b)?c(?(word)d|e){2}",
            }
        ),
        expected_operations=frozenset(
            {"module.sub", "module.subn", "pattern.sub", "pattern.subn"}
        ),
        expected_haystacks=frozenset({"zzabcddzz", "zzaceezz", "zzabcdezz", "zzacedzz"}),
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
)
_CONDITIONAL_GROUP_EXISTS_TEMPLATE_REPLACEMENT_EXPECTATION = next(
    expectation
    for expectation in COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS
    if expectation.slice_id == "minimal-template-replacement-rows"
)
_CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTED_SLICE_IDS = (
    "minimal-callable-replacement-rows",
    "minimal-callable-replacement-exception-rows",
    "minimal-callable-replacement-none-count-exception-rows",
    "alternation-heavy-callable-replacement-rows",
)
_CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTATIONS = tuple(
    expectation
    for expectation in COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS
    if expectation.slice_id
    in _CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTED_SLICE_IDS
)
_CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_ACTUAL_SLICE_IDS = tuple(
    expectation.slice_id
    for expectation in _CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTATIONS
)
if (
    _CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_ACTUAL_SLICE_IDS
    != _CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTED_SLICE_IDS
):
    raise AssertionError(
        "conditional callable replacement slice expectations drifted: "
        "expected "
        f"{_CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTED_SLICE_IDS!r}, got "
        f"{_CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_ACTUAL_SLICE_IDS!r}"
    )
_CONDITIONAL_GROUP_EXISTS_ALTERNATION_CALLABLE_REPLACEMENT_EXPECTATION = next(
    expectation
    for expectation in COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS
    if expectation.slice_id == "alternation-heavy-callable-replacement-rows"
)
_CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_REPLACEMENT_EXPECTATION = next(
    expectation
    for expectation in COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS
    if expectation.slice_id == "nested-callable-replacement-str-rows"
)
_CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_REPLACEMENT_EXPECTATION = next(
    expectation
    for expectation in COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS
    if expectation.slice_id == "nested-callable-replacement-bytes-rows"
)
_CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_REPLACEMENT_EXPECTATION = next(
    expectation
    for expectation in COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS
    if expectation.slice_id == "quantified-callable-replacement-str-rows"
)
_CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_REPLACEMENT_EXPECTATION = next(
    expectation
    for expectation in COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS
    if expectation.slice_id == "quantified-callable-replacement-bytes-rows"
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
COLLECTION_REPLACEMENT_STANDARD_BENCHMARK_DEFINITIONS = (
    _collection_replacement_standard_benchmark_definitions()
)

_SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS = (
    SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS
    + COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS
)


def ordered_operations(workloads: list[Workload]) -> list[str]:
    operations: list[str] = []
    for workload in workloads:
        operation = workload.operation
        if operation not in operations:
            operations.append(operation)
    return operations


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


def _source_tree_combined_manifest_representative_measured_workload_ids(
    manifest_id: str,
) -> tuple[str, ...]:
    manifest_expectation = _SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.get(manifest_id)
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
        for workload_id in shape_expectation.representative_measured_workload_ids:
            normalized_workload_id = str(workload_id)
            if normalized_workload_id not in representative_ids:
                representative_ids.append(normalized_workload_id)
    for expectation in _SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS:
        if expectation.manifest_id != manifest_id:
            continue
        for workload_id in expectation.expected_workload_ids:
            normalized_workload_id = str(workload_id)
            if normalized_workload_id not in representative_ids:
                representative_ids.append(normalized_workload_id)
    return tuple(representative_ids)


def _public_source_tree_manifest_expectation(
    manifest_id: str,
    *,
    selected_workload_ids: Iterable[str] | None = None,
) -> _SourceTreeManifestExpectation:
    manifest_expectation = _SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.get(manifest_id)
    if manifest_expectation is None:
        raise AssertionError(
            f"unknown source-tree combined manifest expectation {manifest_id!r}"
        )
    return _SourceTreeManifestExpectation(
        known_gap_count=len(
            _filter_manifest_workload_ids(
                manifest_expectation.known_gap_workload_ids,
                selected_workload_ids=selected_workload_ids,
            )
        ),
        representative_measured_workload_ids=_filter_manifest_workload_ids(
            manifest_expectation.representative_measured_workload_ids,
            selected_workload_ids=selected_workload_ids,
        ),
        representative_known_gap_workload_ids=_filter_manifest_workload_ids(
            manifest_expectation.representative_known_gap_workload_ids,
            selected_workload_ids=selected_workload_ids,
        ),
    )

def _source_tree_combined_target_manifest_ids() -> tuple[str, ...]:
    target_manifest_ids: list[str] = []
    missing_expectations: list[str] = []
    for manifest in published_benchmark_manifests():
        manifest_id = manifest.manifest_id
        manifest_expectation = _SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.get(
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


def _expected_summary_for_manifests(
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
            manifest.manifest_id: len(
                _filter_manifest_workload_ids(
                    _SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
                        manifest.manifest_id
                    ].known_gap_workload_ids,
                    selected_workload_ids=(
                        workload.workload_id
                        for workload in manifest.selected_workloads(
                            selection_mode=selection_mode
                        )
                    ),
                )
            )
            for manifest in manifests
            if manifest.manifest_id in _SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS
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


def _source_tree_combined_case(target_manifest_id: str) -> _SourceTreeCombinedCase:
    manifests: list[BenchmarkManifest] = []
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
        manifests.append(manifest)
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
        manifests.append(regression_manifest)
    workloads = [workload for manifest in manifests for workload in manifest.workloads]
    target_manifest = next(
        manifest for manifest in manifests if manifest.manifest_id == target_manifest_id
    )
    workload_payloads = [workload_to_payload(workload) for workload in workloads]
    return _SourceTreeCombinedCase(
        expected_adapter=(
            "rebar.module-surface"
            if any(workload.family == "module" for workload in workloads)
            else "rebar.compile"
        ),
        expected_phase=determine_phase(workload_payloads),
        expected_runner_version=determine_runner_version(workload_payloads),
        expected_summary=_expected_summary_for_manifests(
            manifests,
            selection_mode="full",
        ),
        manifests=manifests,
        selection_mode="full",
        manifest_expectation=_public_source_tree_manifest_expectation(target_manifest_id),
        manifest_id=target_manifest_id,
        target_manifest=target_manifest,
    )

def _workload_matches_source_tree_combined_slice(
    workload: Workload,
    expectation: _SourceTreeCombinedSliceExpectation,
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


def _select_source_tree_combined_slice_rows(
    manifest: BenchmarkManifest,
    expectation: _SourceTreeCombinedSliceExpectation,
) -> list[Workload]:
    return [
        workload
        for workload in manifest.workloads
        if _workload_matches_source_tree_combined_slice(workload, expectation)
    ]


def _assert_source_tree_benchmark_contract(
    testcase: object,
    scorecard: dict[str, object],
    summary: dict[str, object],
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
        benchmark_test_support._artifact_manifest_record(manifest_path, manifest)
        for manifest_path, manifest in zip(
            expected_manifest_paths,
            expected_manifests,
            strict=True,
        )
    ]

    benchmark_test_support._assert_benchmark_summary_consistent(
        testcase,
        scorecard,
        summary,
    )
    testcase.assertEqual(scorecard["schema_version"], "1.0")
    testcase.assertEqual(scorecard["suite"], "benchmarks")
    testcase.assertEqual(scorecard["phase"], expected_phase)
    expected_baseline = {
        **benchmark_test_support.build_cpython_baseline(version_family="3.12.x"),
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
        testcase.assertEqual(
            scorecard["implementation"]["native_scaffold_status"],
            "scaffold-only",
        )
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
    testcase.assertEqual(
        scorecard["environment"]["runner_version"],
        expected_runner_version,
    )
    testcase.assertEqual(
        scorecard["environment"]["execution_model"],
        "single-process in-process adapter comparison",
    )
    testcase.assertEqual(
        scorecard["artifacts"]["selection_mode"],
        expected_selection_mode,
    )
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


SourceTreeBenchmarkCommonCase = _SourceTreeBenchmarkCommonCase
SourceTreeManifestExpectation = _SourceTreeManifestExpectation
SourceTreeDeferredExpectation = _SourceTreeDeferredExpectation
SourceTreeCombinedCase = _SourceTreeCombinedCase
SourceTreeCombinedPatternGroupExpectation = _SourceTreeCombinedPatternGroupExpectation
SourceTreeCombinedManifestShapeExpectation = _SourceTreeCombinedManifestShapeExpectation
SourceTreeCombinedFullyMeasuredManifestExpectation = _SourceTreeCombinedFullyMeasuredManifestExpectation
SourceTreeCombinedManifestExpectationDefinition = (
    _SourceTreeCombinedManifestExpectationDefinition
)
SourceTreeCombinedSliceExpectation = _SourceTreeCombinedSliceExpectation
SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS = (
    _SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS
)
SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS = (
    _SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS
)
expected_summary_for_manifests = _expected_summary_for_manifests
source_tree_combined_manifest_representative_measured_workload_ids = (
    _source_tree_combined_manifest_representative_measured_workload_ids
)
source_tree_combined_target_manifest_ids = _source_tree_combined_target_manifest_ids
source_tree_combined_case = _source_tree_combined_case
select_source_tree_combined_slice_rows = _select_source_tree_combined_slice_rows
assert_source_tree_benchmark_contract = _assert_source_tree_benchmark_contract

TRACKED_REPORT_PATH = benchmarks.SCORECARD_REPORT.published_path

WIDER_RANGED_REPEAT_MANIFEST_ID = "wider-ranged-repeat-quantified-group-boundary"


def _workload_ids_for_declared_slice(
    workloads: tuple[Workload, ...],
    *,
    text_model: str | None = None,
    include_categories: tuple[str, ...] = (),
    exclude_categories: tuple[str, ...] = (),
) -> tuple[str, ...]:
    return tuple(
        workload.workload_id
        for workload in workloads
        if (text_model is None or workload.text_model == text_model)
        and all(category in workload.categories for category in include_categories)
        and all(category not in workload.categories for category in exclude_categories)
    )


@dataclass(frozen=True, slots=True)
class _SourceTreeSuiteScorecardDefinition:
    manifest_ids: tuple[str, ...]
    selection_mode: str = "full"
    representative_measured_workload_ids: tuple[str, ...] = ()
    representative_known_gap_workload_ids: tuple[str, ...] = ()
    expected_first_deferred: SourceTreeDeferredExpectation | None = None
    expected_workload_order: tuple[str, ...] | None = None


@dataclass(frozen=True, slots=True)
class _SourceTreeSuiteScorecardCase(SourceTreeBenchmarkCommonCase):
    case_id: str
    manifest_expectations: dict[str, SourceTreeManifestExpectation]
    representative_measured_workload_ids: tuple[str, ...]
    representative_known_gap_workload_ids: tuple[str, ...]
    expected_first_deferred: SourceTreeDeferredExpectation | None = None
    expected_workload_order: tuple[str, ...] | None = None


_SOURCE_TREE_SUITE_SCORECARD_DEFINITIONS = {
    "compile-matrix": _SourceTreeSuiteScorecardDefinition(
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
    "post-parser-workflows": _SourceTreeSuiteScorecardDefinition(
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
    ),
    "numbered-backreference-boundary": _SourceTreeSuiteScorecardDefinition(
        manifest_ids=("numbered-backreference-boundary",),
    ),
    "nested-group-boundary": _SourceTreeSuiteScorecardDefinition(
        manifest_ids=("nested-group-boundary",),
    ),
    "nested-group-replacement-boundary": _SourceTreeSuiteScorecardDefinition(
        manifest_ids=("nested-group-replacement-boundary",),
    ),
    "nested-group-callable-replacement-boundary": _SourceTreeSuiteScorecardDefinition(
        manifest_ids=("nested-group-callable-replacement-boundary",),
    ),
    "branch-local-backreference-boundary": _SourceTreeSuiteScorecardDefinition(
        manifest_ids=("branch-local-backreference-boundary",),
    ),
    "conditional-group-exists-boundary": _SourceTreeSuiteScorecardDefinition(
        manifest_ids=("conditional-group-exists-boundary",),
    ),
    "regression-pack-full": _SourceTreeSuiteScorecardDefinition(
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
    ),
    "regression-pack-smoke": _SourceTreeSuiteScorecardDefinition(
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
    ),
}


@cache
def _published_benchmark_manifest_records() -> dict[str, BenchmarkManifest]:
    return {manifest.manifest_id: manifest for manifest in published_benchmark_manifests()}


def _filter_selected_workload_ids(
    workload_ids: tuple[str, ...] | None,
    *,
    selected_workload_ids: tuple[str, ...],
) -> tuple[str, ...]:
    if not workload_ids:
        return ()
    selected_workload_id_set = set(selected_workload_ids)
    return tuple(
        workload_id
        for workload_id in workload_ids
        if workload_id in selected_workload_id_set
    )


def _source_tree_scorecard_manifest_expectation(
    manifest_id: str,
    *,
    selected_workload_ids: tuple[str, ...],
) -> SourceTreeManifestExpectation:
    manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
        manifest_id
    ]
    return SourceTreeManifestExpectation(
        known_gap_count=len(
            _filter_selected_workload_ids(
                manifest_definition.known_gap_workload_ids,
                selected_workload_ids=selected_workload_ids,
            )
        ),
        representative_measured_workload_ids=_filter_selected_workload_ids(
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            ),
            selected_workload_ids=selected_workload_ids,
        ),
        representative_known_gap_workload_ids=_filter_selected_workload_ids(
            manifest_definition.representative_known_gap_workload_ids,
            selected_workload_ids=selected_workload_ids,
        ),
    )


def _source_tree_suite_scorecard_case(
    case_id: str,
) -> _SourceTreeSuiteScorecardCase:
    case_definition = _SOURCE_TREE_SUITE_SCORECARD_DEFINITIONS.get(case_id)
    if case_definition is None:
        raise AssertionError(f"unknown source-tree suite scorecard case {case_id!r}")

    manifest_records = _published_benchmark_manifest_records()
    manifests = [manifest_records[manifest_id] for manifest_id in case_definition.manifest_ids]
    selected_workloads = tuple(
        workload
        for manifest in manifests
        for workload in manifest.selected_workloads(
            selection_mode=case_definition.selection_mode
        )
    )
    selected_workload_ids = tuple(
        workload.workload_id for workload in selected_workloads
    )
    manifest_expectations: dict[str, SourceTreeManifestExpectation] = {}
    manifest_known_gap_counts: dict[str, int] = {}
    for manifest in manifests:
        manifest_id = manifest.manifest_id
        manifest_expectation = _source_tree_scorecard_manifest_expectation(
            manifest_id,
            selected_workload_ids=tuple(
                workload.workload_id
                for workload in manifest.selected_workloads(
                    selection_mode=case_definition.selection_mode
                )
            ),
        )
        manifest_expectations[manifest_id] = manifest_expectation
        manifest_known_gap_counts[manifest_id] = manifest_expectation.known_gap_count

    representative_measured_workload_ids = _filter_selected_workload_ids(
        case_definition.representative_measured_workload_ids,
        selected_workload_ids=selected_workload_ids,
    )
    representative_known_gap_workload_ids = _filter_selected_workload_ids(
        case_definition.representative_known_gap_workload_ids,
        selected_workload_ids=selected_workload_ids,
    )
    if len(case_definition.manifest_ids) == 1:
        manifest_expectation = manifest_expectations[case_definition.manifest_ids[0]]
        if not representative_measured_workload_ids:
            representative_measured_workload_ids = (
                manifest_expectation.representative_measured_workload_ids
            )
        if not representative_known_gap_workload_ids:
            representative_known_gap_workload_ids = (
                manifest_expectation.representative_known_gap_workload_ids
            )

    workload_payloads = [workload_to_payload(workload) for workload in selected_workloads]
    return _SourceTreeSuiteScorecardCase(
        case_id=case_id,
        expected_adapter=(
            "rebar.module-surface"
            if any(workload.family == "module" for workload in selected_workloads)
            else "rebar.compile"
        ),
        expected_phase=determine_phase(workload_payloads),
        expected_runner_version=determine_runner_version(workload_payloads),
        expected_summary=expected_summary_for_manifests(
            manifests,
            selection_mode=case_definition.selection_mode,
            manifest_known_gap_counts=manifest_known_gap_counts,
        ),
        manifests=manifests,
        selection_mode=case_definition.selection_mode,
        manifest_expectations=manifest_expectations,
        representative_measured_workload_ids=representative_measured_workload_ids,
        representative_known_gap_workload_ids=representative_known_gap_workload_ids,
        expected_first_deferred=case_definition.expected_first_deferred,
        expected_workload_order=case_definition.expected_workload_order,
    )


class SourceTreeCombinedBoundaryBenchmarkSuiteTest(unittest.TestCase):
    maxDiff = None

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

    def test_collection_replacement_manifest_keeps_pattern_keyword_replacement_and_split_rows_measured(
        self,
    ) -> None:
        manifest_path = "collection_replacement_boundary.py"
        manifest_workload_count = len(
            benchmark_test_support.selected_manifest_workloads(manifest_path)
        )
        expected_measured_workload_ids = tuple(
            workload.workload_id
            for workload in benchmark_test_support.selected_manifest_workloads(
                manifest_path,
                include_workload=lambda workload: (
                    _is_collection_replacement_keyword_workload(
                        workload
                    )
                    and workload.operation.startswith("pattern.")
                ),
            )
        )

        self.assertEqual(
            expected_measured_workload_ids,
            (
                "pattern-split-maxsplit-keyword-warm-str",
                "pattern-split-maxsplit-bool-keyword-warm-str",
                "pattern-split-maxsplit-indexlike-keyword-warm-str",
                "pattern-split-duplicate-maxsplit-keyword-warm-str",
                "pattern-split-unexpected-keyword-warm-bytes",
                "pattern-sub-count-keyword-purged-bytes",
                "pattern-sub-count-bool-keyword-purged-bytes",
                "pattern-sub-count-bool-true-keyword-purged-bytes",
                "pattern-sub-count-indexlike-keyword-purged-bytes",
                "pattern-sub-duplicate-count-keyword-warm-str",
                "pattern-sub-unexpected-keyword-warm-str",
                "pattern-sub-unexpected-keyword-after-positional-count-warm-str",
                "pattern-sub-count-alias-keyword-warm-str",
                "pattern-subn-count-keyword-warm-str",
                "pattern-subn-count-bool-keyword-warm-str",
                "pattern-subn-count-bool-false-keyword-warm-str",
                "pattern-subn-count-indexlike-keyword-warm-str",
                "pattern-subn-duplicate-count-keyword-warm-bytes",
                "pattern-subn-unexpected-keyword-warm-bytes",
                "pattern-subn-unexpected-keyword-after-positional-count-warm-bytes",
                "pattern-subn-count-alias-keyword-warm-bytes",
            ),
        )
        benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
            manifest_path=manifest_path,
            manifest_id="collection-replacement-boundary",
            expected_measured_workload_ids=expected_measured_workload_ids,
            expected_measured_workload_count=manifest_workload_count,
            expected_total_workload_count=manifest_workload_count,
        )

    def test_collection_replacement_manifest_keeps_module_keyword_replacement_and_split_rows_measured(
        self,
    ) -> None:
        manifest_path = "collection_replacement_boundary.py"
        manifest_workload_count = len(
            benchmark_test_support.selected_manifest_workloads(manifest_path)
        )
        expected_measured_workload_ids = tuple(
            workload.workload_id
            for workload in benchmark_test_support.selected_manifest_workloads(
                manifest_path,
                include_workload=lambda workload: (
                    _is_collection_replacement_keyword_workload(
                        workload
                    )
                    and workload.operation.startswith("module.")
                ),
            )
        )

        self.assertEqual(
            expected_measured_workload_ids,
            (
                "module-split-maxsplit-keyword-purged-bytes",
                "module-split-maxsplit-bool-keyword-purged-bytes",
                "module-split-maxsplit-indexlike-keyword-purged-bytes",
                "module-split-maxsplit-keyword-purged-str-compiled-pattern",
                "module-split-maxsplit-indexlike-keyword-purged-bytes-compiled-pattern",
                "module-split-maxsplit-bool-keyword-purged-bytes-compiled-pattern",
                "module-split-duplicate-maxsplit-keyword-purged-str",
                "module-split-unexpected-keyword-purged-str",
                "module-split-unexpected-keyword-purged-bytes",
                "module-split-duplicate-maxsplit-keyword-purged-str-compiled-pattern",
                "module-split-unexpected-keyword-purged-bytes-compiled-pattern",
                "module-sub-count-keyword-warm-str",
                "module-sub-count-bool-keyword-warm-str",
                "module-sub-count-bool-false-keyword-warm-str",
                "module-sub-count-indexlike-keyword-warm-str",
                "module-sub-count-keyword-warm-str-compiled-pattern",
                "module-sub-count-indexlike-keyword-warm-bytes-compiled-pattern",
                "module-sub-count-bool-keyword-warm-str-compiled-pattern",
                "module-sub-count-bool-false-keyword-warm-str-compiled-pattern",
                "module-sub-duplicate-count-keyword-warm-str",
                "module-sub-unexpected-keyword-purged-str",
                "module-sub-unexpected-keyword-after-positional-count-purged-str",
                "module-sub-count-alias-keyword-purged-str",
                "module-sub-duplicate-count-keyword-warm-str-compiled-pattern",
                "module-sub-unexpected-keyword-purged-str-compiled-pattern",
                "module-sub-unexpected-keyword-after-positional-count-purged-str-compiled-pattern",
                "module-sub-count-alias-keyword-purged-str-compiled-pattern",
                "module-subn-count-keyword-purged-bytes",
                "module-subn-count-bool-keyword-purged-bytes",
                "module-subn-count-bool-true-keyword-purged-bytes",
                "module-subn-count-indexlike-keyword-purged-bytes",
                "module-subn-duplicate-count-keyword-warm-bytes",
                "module-subn-unexpected-keyword-purged-bytes",
                "module-subn-unexpected-keyword-after-positional-count-purged-bytes",
                "module-subn-count-alias-keyword-purged-bytes",
                "module-subn-count-keyword-purged-bytes-compiled-pattern",
                "module-subn-count-indexlike-keyword-purged-str-compiled-pattern",
                "module-subn-count-bool-keyword-purged-bytes-compiled-pattern",
                "module-subn-count-bool-true-keyword-purged-bytes-compiled-pattern",
                "module-subn-duplicate-count-keyword-warm-bytes-compiled-pattern",
                "module-subn-unexpected-keyword-purged-bytes-compiled-pattern",
                "module-subn-unexpected-keyword-after-positional-count-purged-bytes-compiled-pattern",
                "module-subn-count-alias-keyword-purged-bytes-compiled-pattern",
            ),
        )
        benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
            manifest_path=manifest_path,
            manifest_id="collection-replacement-boundary",
            expected_measured_workload_ids=expected_measured_workload_ids,
            expected_measured_workload_count=manifest_workload_count,
            expected_total_workload_count=manifest_workload_count,
        )

    def test_collection_replacement_manifest_keeps_positional_indexlike_module_and_pattern_rows_measured(
        self,
    ) -> None:
        manifest_path = "collection_replacement_boundary.py"
        manifest_workload_count = len(
            benchmark_test_support.selected_manifest_workloads(manifest_path)
        )
        expected_measured_workload_ids = tuple(
            workload.workload_id
            for workload in benchmark_test_support.selected_manifest_workloads(
                manifest_path,
                include_workload=_is_collection_replacement_positional_indexlike_workload,
            )
        )

        self.assertEqual(
            expected_measured_workload_ids,
            (
                "module-split-maxsplit-indexlike-positional-purged-bytes",
                "module-sub-count-indexlike-positional-warm-str",
                "module-subn-count-indexlike-positional-purged-bytes",
                "pattern-split-maxsplit-indexlike-positional-warm-str",
                "pattern-sub-count-indexlike-positional-purged-bytes",
                "pattern-subn-count-indexlike-positional-warm-str",
            ),
        )
        benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
            manifest_path=manifest_path,
            manifest_id="collection-replacement-boundary",
            expected_measured_workload_ids=expected_measured_workload_ids,
            expected_measured_workload_count=manifest_workload_count,
            expected_total_workload_count=manifest_workload_count,
        )

    def test_conditional_collection_replacement_slice_expectations_stay_in_sync_with_owner_workload_ids(
        self,
    ) -> None:
        callable_expectations = {
            expectation.slice_id: expectation.expected_workload_ids
            for expectation in (
                _CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTATIONS
            )
        }
        minimal_callable_workloads = benchmark_test_support.live_manifest_workloads(
            "conditional_group_exists_boundary.py",
            callable_expectations["minimal-callable-replacement-rows"]
            + callable_expectations["minimal-callable-replacement-exception-rows"],
        )
        callable_none_count_candidate_workloads = (
            benchmark_test_support.live_manifest_workloads(
                "conditional_group_exists_boundary.py",
                callable_expectations[
                    "minimal-callable-replacement-none-count-exception-rows"
                ]
                + callable_expectations["alternation-heavy-callable-replacement-rows"],
            )
        )
        alternation_workloads = benchmark_test_support.live_manifest_workloads(
            "conditional_group_exists_boundary.py",
            callable_expectations["alternation-heavy-callable-replacement-rows"],
        )
        template_workload_ids = (
            _CONDITIONAL_GROUP_EXISTS_TEMPLATE_REPLACEMENT_EXPECTATION.expected_workload_ids
        )
        template_workloads = benchmark_test_support.live_manifest_workloads(
            "conditional_group_exists_boundary.py",
            template_workload_ids,
        )
        callable_none_count_str_ids = _workload_ids_for_declared_slice(
            callable_none_count_candidate_workloads,
            text_model="str",
            include_categories=("none-count",),
        )
        callable_none_count_bytes_ids = _workload_ids_for_declared_slice(
            callable_none_count_candidate_workloads,
            text_model="bytes",
            include_categories=("none-count",),
        )

        observed_workload_ids_by_label = {
            "callable-bytes": _workload_ids_for_declared_slice(
                minimal_callable_workloads,
                text_model="bytes",
                exclude_categories=("negative-count",),
            ),
            "callable-negative-count-str": _workload_ids_for_declared_slice(
                minimal_callable_workloads,
                text_model="str",
                include_categories=("negative-count",),
            ),
            "callable-negative-count-bytes": _workload_ids_for_declared_slice(
                minimal_callable_workloads,
                text_model="bytes",
                include_categories=("negative-count",),
            ),
            "callable-none-count-all": (
                callable_none_count_str_ids + callable_none_count_bytes_ids
            ),
            "callable-none-count-str": callable_none_count_str_ids,
            "callable-none-count-bytes": callable_none_count_bytes_ids,
            "callable-alternation-all": _workload_ids_for_declared_slice(
                alternation_workloads,
                include_categories=("alternation-heavy",),
            ),
            "callable-alternation-str": _workload_ids_for_declared_slice(
                alternation_workloads,
                text_model="str",
                include_categories=("alternation-heavy",),
            ),
            "callable-alternation-bytes": _workload_ids_for_declared_slice(
                alternation_workloads,
                text_model="bytes",
                include_categories=("alternation-heavy",),
            ),
            "template-round-trip": tuple(
                workload.workload_id
                for workload in template_workloads
                if workload.text_model == "bytes"
                or "negative-count" in workload.categories
            ),
            "template-bytes": _workload_ids_for_declared_slice(
                template_workloads,
                text_model="bytes",
            ),
            "template-negative-count-str": _workload_ids_for_declared_slice(
                template_workloads,
                text_model="str",
                include_categories=("negative-count",),
            ),
            "nested-callable-str": (
                _CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_REPLACEMENT_EXPECTATION.expected_workload_ids
            ),
            "nested-callable-bytes": (
                _CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_REPLACEMENT_EXPECTATION.expected_workload_ids
            ),
            "quantified-callable-str": (
                _CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_REPLACEMENT_EXPECTATION.expected_workload_ids
            ),
            "quantified-callable-bytes": (
                _CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_REPLACEMENT_EXPECTATION.expected_workload_ids
            ),
        }
        expected_workload_ids_by_label = {
            "callable-bytes": (
                CONDITIONAL_GROUP_EXISTS_CALLABLE_BYTES_WORKLOAD_IDS
            ),
            "callable-negative-count-str": (
                CONDITIONAL_GROUP_EXISTS_CALLABLE_NEGATIVE_COUNT_STR_WORKLOAD_IDS
            ),
            "callable-negative-count-bytes": (
                CONDITIONAL_GROUP_EXISTS_CALLABLE_NEGATIVE_COUNT_BYTES_WORKLOAD_IDS
            ),
            "callable-none-count-all": (
                CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_IDS
            ),
            "callable-none-count-str": (
                CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS
            ),
            "callable-none-count-bytes": (
                CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS
            ),
            "callable-alternation-all": (
                CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS
            ),
            "callable-alternation-str": (
                CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_STR_WORKLOAD_IDS
            ),
            "callable-alternation-bytes": (
                CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS
            ),
            "template-round-trip": (
                CONDITIONAL_GROUP_EXISTS_TEMPLATE_ROUND_TRIP_WORKLOAD_IDS
            ),
            "template-bytes": (
                CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS
            ),
            "template-negative-count-str": (
                CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS
            ),
            "nested-callable-str": (
                CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS
            ),
            "nested-callable-bytes": (
                CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS
            ),
            "quantified-callable-str": (
                CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS
            ),
            "quantified-callable-bytes": (
                CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS
            ),
        }

        for label, expected_workload_ids in expected_workload_ids_by_label.items():
            with self.subTest(label=label):
                self.assertEqual(
                    observed_workload_ids_by_label[label], expected_workload_ids
                )

    def test_quantified_conditional_callable_combined_slice_expectations_stay_in_sync_with_owner_workload_ids(
        self,
    ) -> None:
        expectations_by_slice_id = {
            expectation.slice_id: expectation
            for expectation in (
                COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS
            )
        }

        self.assertEqual(
            expectations_by_slice_id[
                "quantified-callable-replacement-str-rows"
            ].expected_workload_ids,
            CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS,
        )
        self.assertEqual(
            expectations_by_slice_id[
                "quantified-callable-replacement-bytes-rows"
            ].expected_workload_ids,
            CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS,
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

        benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
            manifest_path=case.target_manifest.path,
            manifest_id="literal-flag-boundary",
            expected_measured_workload_ids=(
                "module-search-ignorecase-ascii-cold-gap",
                "pattern-search-ignorecase-ascii-warm-gap",
            ),
            expected_measured_workload_count=10,
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
                manifest_definition = (
                    SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
                        manifest_id
                    ]
                )
                self.assertIsNone(manifest_definition.known_gap_workload_ids)
                self.assertEqual(
                    manifest_definition.representative_known_gap_workload_ids or (),
                    (),
                )

                case = source_tree_combined_case(manifest_id)
                manifest_expectation = case.manifest_expectation
                self.assertEqual(manifest_expectation.known_gap_count, 0)
                self.assertEqual(
                    manifest_expectation.representative_known_gap_workload_ids,
                    (),
                )
                expected_workload_ids = (
                    manifest_definition.representative_measured_workload_ids
                )
                self.assertIsNotNone(expected_workload_ids)
                assert expected_workload_ids is not None
                self.assertEqual(
                    manifest_expectation.representative_measured_workload_ids,
                    expected_workload_ids,
                )

                benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
                    manifest_path=case.target_manifest.path,
                    manifest_id=manifest_id,
                    expected_measured_workload_ids=expected_workload_ids,
                    expected_measured_workload_count=len(
                        case.selected_workload_ids_for_manifest(manifest_id)
                    ),
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
            [str(manifest.path.relative_to(REPO_ROOT)) for manifest in case.manifests],
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
        for manifest_id, manifest_definition in (
            SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.items()
        ):
            fully_measured_expectation = manifest_definition.fully_measured_expectation
            if fully_measured_expectation is None:
                continue
            if fully_measured_expectation.coverage_group != "counted-repeat":
                continue
            expected_workload_ids = (
                fully_measured_expectation.representative_measured_workload_ids
            )
            expected_measured_workload_count = (
                fully_measured_expectation.expected_measured_workload_count
            )
            with self.subTest(manifest_id=manifest_id):
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

                benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
                    manifest_path=case.target_manifest.path,
                    manifest_id=manifest_id,
                    expected_measured_workload_ids=expected_workload_ids,
                    expected_measured_workload_count=expected_measured_workload_count,
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
                    manifest_definition = (
                        SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
                            manifest_id
                        ]
                    )
                    public_representatives = (
                        source_tree_combined_manifest_representative_measured_workload_ids(
                            manifest_id
                        )
                    )
                    case = source_tree_combined_case(manifest_id)
                    manifest_expectation = case.manifest_expectation
                    expected_measured_workload_count = len(
                        case.selected_workload_ids_for_manifest(manifest_id)
                    )
                    expected_total_workload_count = len(
                        case.target_manifest.workloads
                    )

                    self.assertIsNone(manifest_definition.known_gap_workload_ids)
                    self.assertIsNone(
                        manifest_definition.representative_known_gap_workload_ids
                    )
                    self.assertEqual(manifest_expectation.known_gap_count, 0)
                    self.assertEqual(
                        manifest_expectation.representative_known_gap_workload_ids,
                        (),
                    )
                    self.assertIn(
                        expected_workload_ids,
                        manifest_definition.zero_gap_bytes_representative_subsets,
                    )
                    self.assertEqual(
                        expected_measured_workload_count,
                        expected_total_workload_count,
                    )
                    for workload_id in expected_workload_ids:
                        with self.subTest(workload_id=workload_id):
                            self.assertIn(workload_id, public_representatives)
                            if (
                                manifest_definition.representative_measured_workload_ids
                                is not None
                            ):
                                self.assertIn(
                                    workload_id,
                                    manifest_definition.representative_measured_workload_ids,
                                )
                            if (
                                manifest_expectation.representative_measured_workload_ids
                            ):
                                self.assertIn(
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

        benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
            manifest_path=case.target_manifest.path,
            manifest_id=manifest_id,
            expected_measured_workload_ids=expected_workload_ids,
            expected_measured_workload_count=expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_conditional_group_exists_template_bytes_manifest_promotes_minimal_replacement_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        template_expectation = (
            _CONDITIONAL_GROUP_EXISTS_TEMPLATE_REPLACEMENT_EXPECTATION
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

        benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
            manifest_path=case.target_manifest.path,
            manifest_id=manifest_id,
            expected_measured_workload_ids=expected_workload_ids,
            expected_measured_workload_count=expected_workload_count,
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
                    benchmark_test_support.run_benchmark_workload_with_cpython(
                        workload
                    ),
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
                    benchmark_test_support.run_benchmark_workload_with_cpython(
                        round_tripped
                    ),
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
        benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
            manifest_path=case.target_manifest.path,
            manifest_id=manifest_id,
            expected_measured_workload_ids=expected_workload_ids,
            expected_measured_workload_count=expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_conditional_group_exists_callable_none_count_bytes_manifest_promotes_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        expected_workload_ids = (
            CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
            manifest_id
        ]
        case = source_tree_combined_case(manifest_id)
        manifest_expectation = case.manifest_expectation
        public_representatives = (
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            )
        )
        expected_workload_count = len(
            case.selected_workload_ids_for_manifest(manifest_id)
        )

        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_known_gap_workload_ids)
        self.assertEqual(manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self.assertIn(
            expected_workload_ids,
            manifest_definition.zero_gap_bytes_representative_subsets,
        )
        self.assertEqual(expected_workload_count, len(case.target_manifest.workloads))
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, public_representatives)
                if manifest_expectation.representative_measured_workload_ids:
                    self.assertIn(
                        workload_id,
                        manifest_expectation.representative_measured_workload_ids,
                    )

        benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
            manifest_path=case.target_manifest.path,
            manifest_id=manifest_id,
            expected_measured_workload_ids=expected_workload_ids,
            expected_measured_workload_count=expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_conditional_group_exists_nested_callable_str_manifest_promotes_replacement_and_exception_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        expectation = (
            _CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_REPLACEMENT_EXPECTATION
        )
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

        benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
            manifest_path=case.target_manifest.path,
            manifest_id=manifest_id,
            expected_measured_workload_ids=expected_workload_ids,
            expected_measured_workload_count=expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_conditional_group_exists_nested_callable_bytes_manifest_promotes_replacement_and_exception_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        expected_workload_ids = (
            CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
            manifest_id
        ]
        case = source_tree_combined_case(manifest_id)
        manifest_expectation = case.manifest_expectation
        public_representatives = (
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            )
        )
        expected_workload_count = len(
            case.selected_workload_ids_for_manifest(manifest_id)
        )

        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_known_gap_workload_ids)
        self.assertEqual(manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self.assertIn(
            expected_workload_ids,
            manifest_definition.zero_gap_bytes_representative_subsets,
        )
        self.assertEqual(expected_workload_count, len(case.target_manifest.workloads))
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, public_representatives)
                if manifest_expectation.representative_measured_workload_ids:
                    self.assertIn(
                        workload_id,
                        manifest_expectation.representative_measured_workload_ids,
                    )

        benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
            manifest_path=case.target_manifest.path,
            manifest_id=manifest_id,
            expected_measured_workload_ids=expected_workload_ids,
            expected_measured_workload_count=expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_conditional_group_exists_quantified_callable_str_manifest_promotes_replacement_and_exception_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        expectation = (
            _CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_REPLACEMENT_EXPECTATION
        )
        case = source_tree_combined_case(manifest_id)
        matched_rows = tuple(
            select_source_tree_combined_slice_rows(case.target_manifest, expectation)
        )
        expected_workload_ids = (
            CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS
        )
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

        benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
            manifest_path=case.target_manifest.path,
            manifest_id=manifest_id,
            expected_measured_workload_ids=expected_workload_ids,
            expected_measured_workload_count=expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_conditional_group_exists_quantified_callable_bytes_manifest_promotes_replacement_and_exception_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        expected_workload_ids = (
            CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS
        )
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
            manifest_id
        ]
        case = source_tree_combined_case(manifest_id)
        manifest_expectation = case.manifest_expectation
        public_representatives = (
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            )
        )
        expected_workload_count = len(
            case.selected_workload_ids_for_manifest(manifest_id)
        )

        self.assertIsNone(manifest_definition.known_gap_workload_ids)
        self.assertIsNone(manifest_definition.representative_known_gap_workload_ids)
        self.assertEqual(manifest_expectation.known_gap_count, 0)
        self.assertEqual(
            manifest_expectation.representative_known_gap_workload_ids,
            (),
        )
        self.assertIn(
            expected_workload_ids,
            manifest_definition.zero_gap_bytes_representative_subsets,
        )
        self.assertEqual(expected_workload_count, len(case.target_manifest.workloads))
        for workload_id in expected_workload_ids:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, public_representatives)
                if manifest_expectation.representative_measured_workload_ids:
                    self.assertIn(
                        workload_id,
                        manifest_expectation.representative_measured_workload_ids,
                    )

        benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
            manifest_path=case.target_manifest.path,
            manifest_id=manifest_id,
            expected_measured_workload_ids=expected_workload_ids,
            expected_measured_workload_count=expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_conditional_group_exists_nested_callable_str_workloads_round_trip_preserves_outcomes(
        self,
    ) -> None:
        source_workloads = benchmark_test_support.live_manifest_workloads(
            benchmarks.BENCHMARK_WORKLOADS_ROOT
            / "conditional_group_exists_boundary.py",
            CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS,
        )

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
                    benchmark_test_support.assert_benchmark_workload_matches_expected_result(
                        round_tripped,
                        benchmark_test_support.run_benchmark_workload_with_cpython(source_workload),
                    )
                    continue

                expected_exception = source_workload.expected_exception
                assert expected_exception is not None

                with pytest.raises(
                    TypeError,
                    match=re.escape(expected_exception["message_substring"]),
                ) as expected_error:
                    benchmark_test_support.run_benchmark_workload_with_cpython(source_workload)
                with pytest.raises(TypeError) as observed_error:
                    benchmark_test_support.run_benchmark_workload_with_cpython(round_tripped)
                self.assertEqual(
                    str(observed_error.value),
                    str(expected_error.value),
                )

    def test_conditional_group_exists_nested_callable_bytes_workloads_round_trip_preserves_outcomes(
        self,
    ) -> None:
        source_workloads = benchmark_test_support.live_manifest_workloads(
            benchmarks.BENCHMARK_WORKLOADS_ROOT
            / "conditional_group_exists_boundary.py",
            CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS,
        )

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
                    expected_result = benchmark_test_support.run_benchmark_workload_with_cpython(
                        source_workload
                    )
                    benchmark_test_support.assert_benchmark_workload_matches_expected_result(
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
                    benchmark_test_support.run_benchmark_workload_with_cpython(source_workload)
                with pytest.raises(TypeError) as observed_error:
                    benchmark_test_support.run_benchmark_workload_with_cpython(round_tripped)
                self.assertEqual(
                    str(observed_error.value),
                    str(expected_error.value),
                )

    def test_conditional_group_exists_nested_callable_workloads_anchor_to_unique_published_cases(
        self,
    ) -> None:
        workloads = (
            benchmark_test_support.live_manifest_workloads(
                benchmarks.BENCHMARK_WORKLOADS_ROOT
                / "conditional_group_exists_boundary.py",
                CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS,
            )
            + benchmark_test_support.live_manifest_workloads(
                benchmarks.BENCHMARK_WORKLOADS_ROOT
                / "conditional_group_exists_boundary.py",
                CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS,
            )
        )
        case_ids_by_signature = benchmark_test_support.published_case_ids_by_signature(
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
        source_workloads = benchmark_test_support.live_manifest_workloads(
            benchmarks.BENCHMARK_WORKLOADS_ROOT
            / "conditional_group_exists_boundary.py",
            CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS,
        )

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
                    benchmark_test_support.assert_benchmark_workload_matches_expected_result(
                        round_tripped,
                        benchmark_test_support.run_benchmark_workload_with_cpython(source_workload),
                    )
                    continue

                expected_exception = source_workload.expected_exception
                assert expected_exception is not None

                with pytest.raises(
                    TypeError,
                    match=re.escape(expected_exception["message_substring"]),
                ) as expected_error:
                    benchmark_test_support.run_benchmark_workload_with_cpython(source_workload)
                with pytest.raises(TypeError) as observed_error:
                    benchmark_test_support.run_benchmark_workload_with_cpython(round_tripped)
                self.assertEqual(
                    str(observed_error.value),
                    str(expected_error.value),
                )

    def test_conditional_group_exists_quantified_callable_bytes_workloads_round_trip_preserves_outcomes(
        self,
    ) -> None:
        source_workloads = benchmark_test_support.live_manifest_workloads(
            benchmarks.BENCHMARK_WORKLOADS_ROOT
            / "conditional_group_exists_boundary.py",
            CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS,
        )

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
                    benchmark_test_support.assert_benchmark_workload_matches_expected_result(
                        round_tripped,
                        benchmark_test_support.run_benchmark_workload_with_cpython(source_workload),
                    )
                    continue

                expected_exception = source_workload.expected_exception
                assert expected_exception is not None

                with pytest.raises(
                    TypeError,
                    match=re.escape(expected_exception["message_substring"]),
                ) as expected_error:
                    benchmark_test_support.run_benchmark_workload_with_cpython(source_workload)
                with pytest.raises(TypeError) as observed_error:
                    benchmark_test_support.run_benchmark_workload_with_cpython(round_tripped)
                self.assertEqual(
                    str(observed_error.value),
                    str(expected_error.value),
                )

    def test_conditional_group_exists_quantified_callable_workloads_anchor_to_unique_published_cases(
        self,
    ) -> None:
        workloads = (
            benchmark_test_support.live_manifest_workloads(
                benchmarks.BENCHMARK_WORKLOADS_ROOT
                / "conditional_group_exists_boundary.py",
                CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS,
            )
            + benchmark_test_support.live_manifest_workloads(
                benchmarks.BENCHMARK_WORKLOADS_ROOT
                / "conditional_group_exists_boundary.py",
                CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS,
            )
        )
        case_ids_by_signature = benchmark_test_support.published_case_ids_by_signature(
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
        source_workloads = benchmark_test_support.live_manifest_workloads(
            benchmarks.BENCHMARK_WORKLOADS_ROOT
            / "conditional_group_exists_boundary.py",
            tuple(
                workload_id
                for expectation in (
                    _CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTATIONS
                )
                for workload_id in expectation.expected_workload_ids
                if not workload_id.endswith("-bytes")
            ),
        )

        self.assertEqual(
            tuple(workload.workload_id for workload in source_workloads),
            tuple(
                workload_id
                for expectation in _CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTATIONS
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
                    benchmark_test_support.assert_benchmark_workload_matches_expected_result(
                        round_tripped,
                        benchmark_test_support.run_benchmark_workload_with_cpython(source_workload),
                    )
                    continue

                expected_exception = source_workload.expected_exception
                assert expected_exception is not None

                with pytest.raises(
                    TypeError,
                    match=re.escape(expected_exception["message_substring"]),
                ) as expected_error:
                    benchmark_test_support.run_benchmark_workload_with_cpython(source_workload)
                with pytest.raises(TypeError) as observed_error:
                    benchmark_test_support.run_benchmark_workload_with_cpython(round_tripped)
                self.assertEqual(
                    str(observed_error.value),
                    str(expected_error.value),
                )

    def test_conditional_group_exists_callable_bytes_slice_workloads_round_trip_preserves_outcomes(
        self,
    ) -> None:
        source_workloads = benchmark_test_support.live_manifest_workloads(
            benchmarks.BENCHMARK_WORKLOADS_ROOT
            / "conditional_group_exists_boundary.py",
            tuple(
                workload_id
                for expectation in (
                    _CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTATIONS
                )
                for workload_id in expectation.expected_workload_ids
                if workload_id.endswith("-bytes")
            ),
        )

        self.assertEqual(
            tuple(workload.workload_id for workload in source_workloads),
            tuple(
                workload_id
                for expectation in _CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTATIONS
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
                    benchmark_test_support.assert_benchmark_workload_matches_expected_result(
                        round_tripped,
                        benchmark_test_support.run_benchmark_workload_with_cpython(source_workload),
                    )
                    continue

                expected_exception = source_workload.expected_exception
                assert expected_exception is not None

                with pytest.raises(
                    TypeError,
                    match=re.escape(expected_exception["message_substring"]),
                ) as expected_error:
                    benchmark_test_support.run_benchmark_workload_with_cpython(source_workload)
                with pytest.raises(TypeError) as observed_error:
                    benchmark_test_support.run_benchmark_workload_with_cpython(round_tripped)
                self.assertEqual(
                    str(observed_error.value),
                    str(expected_error.value),
                )

    def test_conditional_group_exists_alternation_callable_bytes_workloads_round_trip_preserves_outcomes(
        self,
    ) -> None:
        for source_workload in benchmark_test_support.live_manifest_workloads(
            benchmarks.BENCHMARK_WORKLOADS_ROOT
            / "conditional_group_exists_boundary.py",
            CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS,
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
                    benchmark_test_support.assert_benchmark_workload_matches_expected_result(
                        round_tripped,
                        benchmark_test_support.run_benchmark_workload_with_cpython(source_workload),
                    )
                    continue

                expected_exception = source_workload.expected_exception
                assert expected_exception is not None

                with pytest.raises(
                    TypeError,
                    match=re.escape(expected_exception["message_substring"]),
                ) as expected_error:
                    benchmark_test_support.run_benchmark_workload_with_cpython(source_workload)
                with pytest.raises(TypeError) as observed_error:
                    benchmark_test_support.run_benchmark_workload_with_cpython(round_tripped)
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

        benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
            manifest_path=case.target_manifest.path,
            manifest_id=manifest_id,
            expected_measured_workload_ids=expected_workload_ids,
            expected_measured_workload_count=expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_quantified_alternation_manifest_promotes_bounded_branch_backref_conditional_nested_branch_broader_range_open_ended_and_backtracking_heavy_bytes_rows_to_measured(
        self,
    ) -> None:
        manifest_id = "quantified-alternation-boundary"
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]
        fully_measured_expectation = manifest_definition.fully_measured_expectation
        self.assertIsNotNone(fully_measured_expectation)
        assert fully_measured_expectation is not None
        expected_workload_ids = (
            fully_measured_expectation.representative_measured_workload_ids
        )
        expected_measured_workload_count = (
            fully_measured_expectation.expected_measured_workload_count
        )
        expected_total_workload_count = (
            fully_measured_expectation.expected_total_workload_count
        )
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

        benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
            manifest_path=case.target_manifest.path,
            manifest_id=manifest_id,
            expected_measured_workload_ids=expected_workload_ids,
            expected_measured_workload_count=expected_measured_workload_count,
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
        benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
            manifest_path=case.target_manifest.path,
            manifest_id=manifest_id,
            expected_measured_workload_ids=expected_workload_ids,
            expected_measured_workload_count=expected_workload_count,
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
        benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
            manifest_path=case.target_manifest.path,
            manifest_id=manifest_id,
            expected_measured_workload_ids=expected_workload_ids,
            expected_measured_workload_count=expected_workload_count,
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
        benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
            manifest_path=case.target_manifest.path,
            manifest_id=manifest_id,
            expected_measured_workload_ids=expected_workload_ids,
            expected_measured_workload_count=expected_workload_count,
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
        benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
            manifest_path=case.target_manifest.path,
            manifest_id=manifest_id,
            expected_measured_workload_ids=expected_workload_ids,
            expected_measured_workload_count=expected_workload_count,
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
        benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
            manifest_path=case.target_manifest.path,
            manifest_id=manifest_id,
            expected_measured_workload_ids=expected_workload_ids,
            expected_measured_workload_count=expected_workload_count,
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
        benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
            manifest_path=case.target_manifest.path,
            manifest_id=manifest_id,
            expected_measured_workload_ids=expected_workload_ids,
            expected_measured_workload_count=expected_workload_count,
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
        benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
            manifest_path=case.target_manifest.path,
            manifest_id=manifest_id,
            expected_measured_workload_ids=expected_workload_ids,
            expected_measured_workload_count=expected_workload_count,
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
        benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
            manifest_path=case.target_manifest.path,
            manifest_id=manifest_id,
            expected_measured_workload_ids=expected_workload_ids,
            expected_measured_workload_count=expected_workload_count,
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
    success_case = next(
        case
        for case in _COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES
        if case.case_id == "success"
    )
    bool_false_case = next(
        case
        for case in _COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES
        if case.case_id == "bool-false"
    )
    success_anchor_lane = next(
        lane
        for lane in _COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES
        if lane.case_id == success_case.case_id
    )
    bool_false_anchor_lane = next(
        lane
        for lane in _COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES
        if lane.case_id == bool_false_case.case_id
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
        benchmark_test_support.selected_manifest_workloads(benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH)
    )
    expected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in benchmark_test_support.selected_manifest_workloads(
            benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,
            include_workload=owner_spec.includes_workload,
        )
    )

    assert expected_measured_workload_ids == owner_spec.expected_anchor_workload_ids()
    benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
        manifest_path=benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH,
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
    contract_case = next(
        case
        for case in _COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES
        if case.case_id == anchor_lane.case_id
    )
    manifest = _source_tree_contract_manifest(
        anchor_lane.source_workloads,
        spec=contract_case.contract_builder_spec(),
    )
    manifest_path = benchmark_test_support._write_test_manifest(
        tmp_path,
        anchor_lane.contract_filename,
        f"MANIFEST = {manifest!r}\n",
    )
    expected_anchor_case_ids = anchor_lane.expected_anchor_case_ids(manifest_path)
    anchor_case_ids = anchor_lane.anchor_case_ids

    assert benchmark_test_support.anchored_workload_case_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=anchor_lane.workload_signature,
        include_workload=anchor_lane.include_workload,
    ) == expected_anchor_case_ids
    assert benchmark_test_support.unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=anchor_lane.workload_signature,
        include_workload=anchor_lane.include_workload,
    ) == ()
    assert tuple(
        (pair.workload_id, pair.case_id)
        for pair in benchmark_test_support.expected_anchored_workload_case_pairs(
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
    observed_field_names = benchmark_test_support._record_numeric_materialization_fields(monkeypatch)

    re.purge()
    try:
        callback = benchmarks.build_callable(re, "re", workload)
        assert observed_field_names == []

        if source_workload.expected_exception is None:
            observed_result = callback()
            assert observed_result.pattern == workload.pattern_payload()
        else:
            expected_exception = benchmark_test_support._expected_exception_instance(
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
        else benchmark_test_support._expected_exception_instance(source_workload.expected_exception)
    )
    module = benchmark_test_support.RecordingBenchmarkModule(compile_exception=compile_exception)
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
        benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
            manifest_path=case.target_manifest.path,
            manifest_id=manifest_id,
            expected_measured_workload_ids=expected_workload_ids,
            expected_measured_workload_count=expected_workload_count,
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
        benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
            manifest_path=case.target_manifest.path,
            manifest_id=manifest_id,
            expected_measured_workload_ids=expected_workload_ids,
            expected_measured_workload_count=expected_workload_count,
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
        benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
            manifest_path=case.target_manifest.path,
            manifest_id=manifest_id,
            expected_measured_workload_ids=expected_workload_ids,
            expected_measured_workload_count=expected_workload_count,
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
        benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
            manifest_path=case.target_manifest.path,
            manifest_id=manifest_id,
            expected_measured_workload_ids=expected_workload_ids,
            expected_measured_workload_count=expected_workload_count,
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
        benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
            manifest_path=case.target_manifest.path,
            manifest_id=manifest_id,
            expected_measured_workload_ids=expected_workload_ids,
            expected_measured_workload_count=expected_workload_count,
            expected_total_workload_count=expected_workload_count,
        )

    def test_shape_backed_manifests_keep_derived_representatives(self) -> None:
        manifest_definition = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
            "pattern-boundary"
        ]
        shape_expectation = manifest_definition.shape_expectation
        self.assertIsNotNone(shape_expectation)
        assert shape_expectation is not None
        self.assertIs(manifest_definition.shape_expectation, shape_expectation)
        self.assertEqual(
            source_tree_combined_manifest_representative_measured_workload_ids(
                "pattern-boundary"
            ),
            shape_expectation.representative_measured_workload_ids,
        )

    def test_regression_manifest_is_fully_measured_on_the_shared_surface(self) -> None:
        scorecard_case = _source_tree_suite_scorecard_case("regression-pack-full")
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

        benchmark_test_support.assert_manifest_workload_contracts(
            self,
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
        manifest_ids_with_slice_expectations = {
            expectation.manifest_id
            for expectation in SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS
        }
        combined_target_manifest_ids = (
            source_tree_combined_target_manifest_ids()
        )
        self.assertEqual(
            manifest_ids_with_slice_expectations - set(combined_target_manifest_ids),
            set(),
        )
        for manifest_id in (
            manifest_id
            for manifest_id in combined_target_manifest_ids
            if manifest_id in manifest_ids_with_slice_expectations
        ):
            with self.subTest(manifest_id=manifest_id):
                manifest = source_tree_combined_case(manifest_id).target_manifest
                for expectation in (
                    expectation
                    for expectation in SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS
                    if expectation.manifest_id == manifest_id
                ):
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
        manifest_ids_with_slice_expectations = {
            expectation.manifest_id
            for expectation in SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS
        }
        for manifest_id in (
            manifest_id
            for manifest_id in source_tree_combined_target_manifest_ids()
            if manifest_id in manifest_ids_with_slice_expectations
            if SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
                manifest_id
            ].representative_measured_workload_ids
            is None
            and SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
                manifest_id
            ].shape_expectation
            is None
        ):
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
                        for expectation in SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS
                        if expectation.manifest_id == manifest_id
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
                        str(manifest.path.relative_to(REPO_ROOT))
                        for manifest in case.manifests
                    ],
                    expected_selection_mode=case.selection_mode,
                    tracked_report_path=TRACKED_REPORT_PATH,
                )
                self.assertEqual(summary, case.expected_summary)

                manifest_id = case.manifest_id
                manifest_summary = scorecard["manifests"][manifest_id]
                manifest_record = benchmark_test_support.find_manifest_record(
                    scorecard,
                    manifest_id,
                )
                benchmark_test_support.assert_benchmark_manifest_contract(
                    self,
                    manifest_summary,
                    manifest_record,
                    manifest=case.target_manifest,
                    manifest_path=str(
                        case.target_manifest.path.relative_to(REPO_ROOT)
                    ),
                    known_gap_count=manifest_expectation.known_gap_count,
                    selection_mode=case.selection_mode,
                    selected_workload_ids=case.selected_workload_ids_for_manifest(
                        manifest_id
                    ),
                )

                representative_ids = list(
                    source_tree_combined_manifest_representative_measured_workload_ids(
                        manifest_id
                    )
                )
                for workload_id in (
                    manifest_expectation.representative_measured_workload_ids
                ):
                    if workload_id not in representative_ids:
                        representative_ids.append(workload_id)
                for operation in ordered_operations(
                    case.target_manifest.workloads
                ):
                    for workload in scorecard["workloads"]:
                        if workload["manifest_id"] != manifest_id:
                            continue
                        if (
                            workload["operation"] != operation
                            or workload["status"] != "measured"
                        ):
                            continue
                        workload_id = str(workload["id"])
                        if workload_id not in representative_ids:
                            representative_ids.append(workload_id)
                        break
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

                benchmark_test_support.assert_manifest_workload_contracts(
                    self,
                    case.target_manifest,
                    scorecard,
                    workload_expectations,
                )

    def test_selected_combined_source_tree_manifest_slices_stay_covered(self) -> None:
        manifest_ids_with_slice_expectations = {
            expectation.manifest_id
            for expectation in SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS
        }
        for manifest_id in (
            manifest_id
            for manifest_id in source_tree_combined_target_manifest_ids()
            if manifest_id in manifest_ids_with_slice_expectations
        ):
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

                for expectation in (
                    expectation
                    for expectation in SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS
                    if expectation.manifest_id == manifest_id
                ):
                    with self.subTest(slice_id=expectation.slice_id):
                        matched_rows = (
                            select_source_tree_combined_slice_rows(
                                case.target_manifest,
                                expectation,
                            )
                        )
                        self.assertEqual(
                            tuple(workload.workload_id for workload in matched_rows),
                            expectation.expected_workload_ids,
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
                            and workload["id"] in expectation.expected_workload_ids
                        ]
                        self.assertEqual(
                            {workload["id"] for workload in scorecard_rows},
                            set(expectation.expected_workload_ids),
                        )
                        benchmark_test_support.assert_manifest_workload_contracts(
                            self,
                            case.target_manifest,
                            scorecard,
                            (
                                (
                                    workload_id,
                                    expectation.expected_status,
                                )
                                for workload_id in expectation.expected_workload_ids
                            ),
                            subtest_label="workload_id",
                        )

    def test_wider_ranged_repeat_manifest_shape_stays_covered_in_combined_suite(
        self,
    ) -> None:
        case = source_tree_combined_case(WIDER_RANGED_REPEAT_MANIFEST_ID)
        shape_expectation = SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
            WIDER_RANGED_REPEAT_MANIFEST_ID
        ].shape_expectation
        self.assertIsNotNone(shape_expectation)
        assert shape_expectation is not None
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

        benchmark_test_support.assert_manifest_workload_contracts(
            self,
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
                manifest_rows = [
                    workload
                    for workload in case.target_manifest.workloads
                    if workload.pattern in pattern_group.patterns
                ]
                self.assertGreaterEqual(
                    len(manifest_rows),
                    pattern_group.minimum_rows,
                    f"expected benchmark rows for the {pattern_group.slice_id} slice",
                )
                for pattern in pattern_group.patterns:
                    pattern_rows = [
                        workload
                        for workload in manifest_rows
                        if workload.pattern == pattern
                    ]
                    self.assertGreaterEqual(
                        len(pattern_rows),
                        3,
                        f"expected compile/search/fullmatch coverage for {pattern!r}",
                    )
                    self.assertTrue(
                        set(pattern_group.required_operations).issubset(
                            {workload.operation for workload in pattern_rows}
                        )
                    )
                    for workload in pattern_rows:
                        with self.subTest(
                            pattern=pattern,
                            workload_id=workload.workload_id,
                        ):
                            for category in pattern_group.required_categories:
                                self.assertIn(category, workload.categories)
                manifest_search_haystacks = {
                    str(workload.haystack)
                    for workload in manifest_rows
                    if workload.operation == "module.search"
                }
                for haystack in pattern_group.search_haystacks:
                    self.assertIn(haystack, manifest_search_haystacks)
                for snippet in pattern_group.search_haystack_substrings:
                    self.assertTrue(
                        any(
                            snippet in haystack
                            for haystack in manifest_search_haystacks
                        ),
                        f"expected a module.search workload covering {snippet!r}",
                    )
                manifest_pattern_haystacks = {
                    str(workload.haystack)
                    for workload in manifest_rows
                    if workload.operation == "pattern.fullmatch"
                }
                for haystack in pattern_group.pattern_haystacks:
                    self.assertIn(haystack, manifest_pattern_haystacks)
                scorecard_rows = [
                    workload
                    for workload in scorecard["workloads"]
                    if workload["manifest_id"] == WIDER_RANGED_REPEAT_MANIFEST_ID
                    and workload["pattern"] in pattern_group.patterns
                ]
                self.assertEqual(
                    {workload["id"] for workload in scorecard_rows},
                    {workload.workload_id for workload in manifest_rows},
                )
                for workload in scorecard_rows:
                    with self.subTest(scorecard_workload_id=workload["id"]):
                        self.assertEqual(workload["status"], "measured")
                        self.assertEqual(
                            workload["implementation_timing"]["status"],
                            "measured",
                        )
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

    def test_raw_scorecard_case_definitions_use_direct_manifest_ids(self) -> None:
        for case_id, case_definition in _SOURCE_TREE_SUITE_SCORECARD_DEFINITIONS.items():
            with self.subTest(case_id=case_id):
                self.assertFalse(isinstance(case_definition, dict))
                self.assertFalse(hasattr(case_definition, "full_manifest_ids"))
                self.assertTrue(hasattr(case_definition, "manifest_ids"))
                self.assertGreaterEqual(len(case_definition.manifest_ids), 1)
                self.assertIn(case_definition.selection_mode, {"full", "smoke"})

    def test_full_scorecard_cases_derive_known_gap_counts_from_manifest_inventories(
        self,
    ) -> None:
        case = _source_tree_suite_scorecard_case("post-parser-workflows")
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
        case = _source_tree_suite_scorecard_case("post-parser-workflows")
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
        case = _source_tree_suite_scorecard_case("regression-pack-full")
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
        manifest_id = "numbered-backreference-boundary"
        scorecard_case = _source_tree_suite_scorecard_case(manifest_id)
        combined_case = source_tree_combined_case(manifest_id)

        self.assertEqual(
            scorecard_case.manifest_expectations[manifest_id].known_gap_count,
            0,
        )
        self.assertEqual(
            scorecard_case.representative_measured_workload_ids,
            combined_case.manifest_expectation.representative_measured_workload_ids,
        )
        self.assertEqual(scorecard_case.representative_known_gap_workload_ids, ())
        self.assertEqual(
            combined_case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )

    def test_nested_group_manifest_promotes_nested_pair_to_measured(self) -> None:
        manifest_id = "nested-group-boundary"
        scorecard_case = _source_tree_suite_scorecard_case(manifest_id)
        combined_case = source_tree_combined_case(manifest_id)

        self.assertEqual(
            scorecard_case.manifest_expectations[manifest_id].known_gap_count,
            0,
        )
        self.assertEqual(
            scorecard_case.representative_measured_workload_ids,
            combined_case.manifest_expectation.representative_measured_workload_ids,
        )
        self.assertEqual(scorecard_case.representative_known_gap_workload_ids, ())
        self.assertEqual(
            combined_case.manifest_expectation.representative_known_gap_workload_ids,
            (),
        )

    def test_case_builders_reuse_cached_source_tree_manifest_records(self) -> None:
        scorecard_case = _source_tree_suite_scorecard_case("post-parser-workflows")
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
        case = _source_tree_suite_scorecard_case("post-parser-workflows")

        self.assertEqual(
            [manifest.path.name for manifest in case.manifests],
            [
                "module_boundary.py",
                "collection_replacement_boundary.py",
                "literal_flag_boundary.py",
            ],
        )
        self.assertEqual(
            [str(manifest.path.relative_to(REPO_ROOT)) for manifest in case.manifests],
            [
                "benchmarks/workloads/module_boundary.py",
                "benchmarks/workloads/collection_replacement_boundary.py",
                "benchmarks/workloads/literal_flag_boundary.py",
            ],
        )

    def test_case_selection_helpers_derive_workload_ids_from_manifests(self) -> None:
        compile_matrix = _source_tree_suite_scorecard_case("compile-matrix")
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

        post_parser = _source_tree_suite_scorecard_case("post-parser-workflows")
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
                        with self.subTest(
                            manifest_id=manifest_id,
                            workload_id=workload_id,
                        ):
                            self.assertIn(workload_id, public_representatives)
                            if explicit_representatives:
                                self.assertIn(workload_id, explicit_representatives)

                    if not explicit_representatives:
                        self.assertEqual(explicit_representatives, ())

    def test_combined_cases_treat_counted_repeat_manifest_pair_as_fully_measured(
        self,
    ) -> None:
        for manifest_id, manifest_definition in (
            SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.items()
        ):
            fully_measured_expectation = manifest_definition.fully_measured_expectation
            if fully_measured_expectation is None:
                continue
            if fully_measured_expectation.coverage_group != "counted-repeat":
                continue
            expected_workload_ids = (
                fully_measured_expectation.representative_measured_workload_ids
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
        case = _source_tree_suite_scorecard_case("compile-matrix")
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
                case = _source_tree_suite_scorecard_case(case_id)
                self.assertEqual(
                    case.representative_measured_workload_ids,
                    tuple(
                        workload_id
                        for expectation in SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS
                        if expectation.manifest_id == case_id
                        for workload_id in expectation.expected_workload_ids
                    ),
                )

    def test_conditional_group_exists_callable_scorecards_keep_negative_count_follow_on_workloads_in_sync(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        expectations = (
            _CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTATIONS
        )
        case = _source_tree_suite_scorecard_case(manifest_id)
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
        representative_measured_workload_ids = (
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            )
        )
        representative_callable_workload_ids = tuple(
            workload_id
            for workload_id in representative_measured_workload_ids
            if workload_id in expected_callable_workload_ids
        )
        expected_str_workload_ids = tuple(
            workload_id
            for workload_id in expected_callable_workload_ids
            if not workload_id.endswith("-bytes")
        )
        expected_bytes_workload_ids = tuple(
            workload_id
            for workload_id in expected_callable_workload_ids
            if workload_id.endswith("-bytes")
        )
        representative_str_workload_ids = tuple(
            workload_id
            for workload_id in representative_callable_workload_ids
            if not workload_id.endswith("-bytes")
        )
        representative_bytes_workload_ids = tuple(
            workload_id
            for workload_id in representative_callable_workload_ids
            if workload_id.endswith("-bytes")
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
        expectations = (
            _CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTATIONS
        )
        case = _source_tree_suite_scorecard_case(manifest_id)
        manifest = case.manifest_for_id(manifest_id)
        expected_none_count_workload_ids = (
            CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_IDS
        )
        callable_slice_rows = tuple(
            workload
            for expectation in expectations
            for workload in select_source_tree_combined_slice_rows(manifest, expectation)
        )
        representative_measured_workload_ids = (
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            )
        )
        none_count_rows = tuple(
            workload
            for workload in callable_slice_rows
            if "none-count" in workload.categories
        )
        representative_none_count_workload_ids = tuple(
            workload_id
            for workload_id in representative_measured_workload_ids
            if workload_id in expected_none_count_workload_ids
        )
        representative_str_workload_ids = tuple(
            workload_id
            for workload_id in representative_none_count_workload_ids
            if not workload_id.endswith("-bytes")
        )
        representative_bytes_workload_ids = tuple(
            workload_id
            for workload_id in representative_none_count_workload_ids
            if workload_id.endswith("-bytes")
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
        case = _source_tree_suite_scorecard_case(manifest_id)
        manifest = case.manifest_for_id(manifest_id)
        representative_measured_workload_ids = (
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            )
        )
        str_expectation = (
            _CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_REPLACEMENT_EXPECTATION
        )
        bytes_expectation = (
            _CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_REPLACEMENT_EXPECTATION
        )
        str_rows = tuple(
            select_source_tree_combined_slice_rows(manifest, str_expectation)
        )
        bytes_rows = tuple(
            select_source_tree_combined_slice_rows(manifest, bytes_expectation)
        )
        representative_nested_workload_ids = tuple(
            workload_id
            for workload_id in representative_measured_workload_ids
            if workload_id
            in (
                CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS
                + CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS
            )
        )
        representative_str_workload_ids = tuple(
            workload_id
            for workload_id in representative_nested_workload_ids
            if not workload_id.endswith("-bytes")
        )
        representative_bytes_workload_ids = tuple(
            workload_id
            for workload_id in representative_nested_workload_ids
            if workload_id.endswith("-bytes")
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
        case = _source_tree_suite_scorecard_case(manifest_id)
        manifest = case.manifest_for_id(manifest_id)
        representative_measured_workload_ids = (
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            )
        )
        str_expectation = (
            _CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_REPLACEMENT_EXPECTATION
        )
        bytes_expectation = (
            _CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_REPLACEMENT_EXPECTATION
        )
        str_rows = tuple(
            select_source_tree_combined_slice_rows(manifest, str_expectation)
        )
        bytes_rows = tuple(
            select_source_tree_combined_slice_rows(manifest, bytes_expectation)
        )
        representative_quantified_workload_ids = tuple(
            workload_id
            for workload_id in representative_measured_workload_ids
            if workload_id
            in (
                CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS
                + CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS
            )
        )
        representative_str_workload_ids = tuple(
            workload_id
            for workload_id in representative_quantified_workload_ids
            if not workload_id.endswith("-bytes")
        )
        representative_bytes_workload_ids = tuple(
            workload_id
            for workload_id in representative_quantified_workload_ids
            if workload_id.endswith("-bytes")
        )
        manifest_negative_count_str_workload_ids = tuple(
            workload.workload_id
            for workload in str_rows
            if workload.text_model == "str"
            and "negative-count" in workload.categories
        )
        manifest_negative_count_bytes_workload_ids = tuple(
            workload.workload_id
            for workload in bytes_rows
            if workload.text_model == "bytes"
            and "negative-count" in workload.categories
        )
        manifest_negative_count_no_match_str_workload_ids = tuple(
            workload.workload_id
            for workload in str_rows
            if workload.text_model == "str"
            and "negative-count" in workload.categories
            and "no-match" in workload.categories
        )
        manifest_negative_count_no_match_bytes_workload_ids = tuple(
            workload.workload_id
            for workload in bytes_rows
            if workload.text_model == "bytes"
            and "negative-count" in workload.categories
            and "no-match" in workload.categories
        )
        manifest_none_count_str_workload_ids = tuple(
            workload.workload_id
            for workload in str_rows
            if workload.text_model == "str"
            and "none-count" in workload.categories
        )
        manifest_none_count_bytes_workload_ids = tuple(
            workload.workload_id
            for workload in bytes_rows
            if workload.text_model == "bytes"
            and "none-count" in workload.categories
        )
        manifest_plain_no_match_str_workload_ids = tuple(
            workload.workload_id
            for workload in str_rows
            if workload.text_model == "str"
            and "no-match" in workload.categories
            and "negative-count" not in workload.categories
        )
        manifest_plain_no_match_bytes_workload_ids = tuple(
            workload.workload_id
            for workload in bytes_rows
            if workload.text_model == "bytes"
            and "no-match" in workload.categories
            and "negative-count" not in workload.categories
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
            tuple(
                f"{workload_id.removesuffix('-str')}-bytes"
                for workload_id in manifest_negative_count_str_workload_ids
            ),
        )
        self.assertEqual(
            manifest_negative_count_no_match_bytes_workload_ids,
            tuple(
                f"{workload_id.removesuffix('-str')}-bytes"
                for workload_id in manifest_negative_count_no_match_str_workload_ids
            ),
        )
        self.assertEqual(
            manifest_none_count_bytes_workload_ids,
            tuple(
                f"{workload_id.removesuffix('-str')}-bytes"
                for workload_id in manifest_none_count_str_workload_ids
            ),
        )
        self.assertEqual(
            manifest_plain_no_match_bytes_workload_ids,
            tuple(
                f"{workload_id.removesuffix('-str')}-bytes"
                for workload_id in manifest_plain_no_match_str_workload_ids
            ),
        )
        self.assertEqual(
            representative_negative_count_str_workload_ids,
            manifest_negative_count_str_workload_ids,
        )
        self.assertEqual(
            representative_negative_count_bytes_workload_ids,
            tuple(
                f"{workload_id.removesuffix('-str')}-bytes"
                for workload_id in representative_negative_count_str_workload_ids
            ),
        )
        self.assertEqual(
            representative_negative_count_no_match_str_workload_ids,
            manifest_negative_count_no_match_str_workload_ids,
        )
        self.assertEqual(
            representative_negative_count_no_match_bytes_workload_ids,
            tuple(
                f"{workload_id.removesuffix('-str')}-bytes"
                for workload_id in representative_negative_count_no_match_str_workload_ids
            ),
        )
        self.assertEqual(
            representative_none_count_str_workload_ids,
            manifest_none_count_str_workload_ids,
        )
        self.assertEqual(
            representative_none_count_bytes_workload_ids,
            tuple(
                f"{workload_id.removesuffix('-str')}-bytes"
                for workload_id in representative_none_count_str_workload_ids
            ),
        )
        self.assertEqual(
            representative_plain_no_match_str_workload_ids,
            manifest_plain_no_match_str_workload_ids,
        )
        self.assertEqual(
            representative_plain_no_match_bytes_workload_ids,
            tuple(
                f"{workload_id.removesuffix('-str')}-bytes"
                for workload_id in representative_plain_no_match_str_workload_ids
            ),
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
            _CONDITIONAL_GROUP_EXISTS_ALTERNATION_CALLABLE_REPLACEMENT_EXPECTATION
        )
        case = _source_tree_suite_scorecard_case(manifest_id)
        manifest = case.manifest_for_id(manifest_id)
        representative_measured_workload_ids = (
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            )
        )
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
        self.assertEqual(case.representative_known_gap_workload_ids, ())
        for workload_id in CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, representative_measured_workload_ids)
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
            _CONDITIONAL_GROUP_EXISTS_TEMPLATE_REPLACEMENT_EXPECTATION
        )
        case = _source_tree_suite_scorecard_case(manifest_id)
        representative_measured_workload_ids = (
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            )
        )
        matched_rows = tuple(
            select_source_tree_combined_slice_rows(
                case.manifest_for_id(manifest_id),
                template_expectation,
            )
        )
        expected_workload_ids = template_expectation.expected_workload_ids

        self.assertEqual(case.representative_known_gap_workload_ids, ())
        self.assertEqual({workload.text_model for workload in matched_rows}, {"str", "bytes"})
        for workload_id in CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS:
            with self.subTest(workload_id=workload_id):
                self.assertIn(workload_id, representative_measured_workload_ids)
                self.assertNotIn(
                    workload_id,
                    case.representative_known_gap_workload_ids,
                )
        self.assertEqual(
            tuple(
                workload.workload_id
                for workload in matched_rows
                if workload.workload_id in representative_measured_workload_ids
            ),
            expected_workload_ids,
        )

    def test_conditional_group_exists_replacement_template_scorecards_keep_bytes_negative_count_follow_on_workloads_in_sync(
        self,
    ) -> None:
        manifest_id = "conditional-group-exists-boundary"
        template_expectation = (
            _CONDITIONAL_GROUP_EXISTS_TEMPLATE_REPLACEMENT_EXPECTATION
        )
        case = _source_tree_suite_scorecard_case(manifest_id)
        representative_measured_workload_ids = (
            source_tree_combined_manifest_representative_measured_workload_ids(
                manifest_id
            )
        )
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
            for workload_id in representative_measured_workload_ids
            if workload_id in template_expectation.expected_workload_ids
        )
        expected_str_workload_ids = tuple(
            workload_id
            for workload_id in template_expectation.expected_workload_ids
            if not workload_id.endswith("-bytes")
        )
        expected_bytes_workload_ids = tuple(
            workload_id
            for workload_id in template_expectation.expected_workload_ids
            if workload_id.endswith("-bytes")
        )
        representative_str_workload_ids = tuple(
            workload_id
            for workload_id in representative_template_workload_ids
            if not workload_id.endswith("-bytes")
        )
        representative_bytes_workload_ids = tuple(
            workload_id
            for workload_id in representative_template_workload_ids
            if workload_id.endswith("-bytes")
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
        case = _source_tree_suite_scorecard_case("nested-group-callable-replacement-boundary")
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
        case = _source_tree_suite_scorecard_case("nested-group-callable-replacement-boundary")
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
        case = _source_tree_suite_scorecard_case("nested-group-callable-replacement-boundary")
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
        case = _source_tree_suite_scorecard_case("nested-group-callable-replacement-boundary")
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
        case = _source_tree_suite_scorecard_case("nested-group-replacement-boundary")
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
        case = _source_tree_suite_scorecard_case("nested-group-replacement-boundary")
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
        case = _source_tree_suite_scorecard_case("nested-group-callable-replacement-boundary")
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
        case = _source_tree_suite_scorecard_case("nested-group-callable-replacement-boundary")
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
        case = _source_tree_suite_scorecard_case("nested-group-callable-replacement-boundary")
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
        case = _source_tree_suite_scorecard_case("nested-group-callable-replacement-boundary")
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
        case = _source_tree_suite_scorecard_case("nested-group-callable-replacement-boundary")
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
        case = _source_tree_suite_scorecard_case("nested-group-callable-replacement-boundary")
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
        case = _source_tree_suite_scorecard_case("nested-group-callable-replacement-boundary")
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
        case = _source_tree_suite_scorecard_case("nested-group-replacement-boundary")
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
        for case_id in _SOURCE_TREE_SUITE_SCORECARD_DEFINITIONS:
            with self.subTest(case_id=case_id):
                case = _source_tree_suite_scorecard_case(case_id)
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
                        str(manifest.path.relative_to(REPO_ROOT))
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

                for manifest_id, manifest_expectation in case.manifest_expectations.items():
                    manifest = case.manifest_for_id(manifest_id)
                    with self.subTest(manifest_id=manifest_id):
                        benchmark_test_support.assert_benchmark_manifest_contract(
                            self,
                            scorecard["manifests"][manifest_id],
                            benchmark_test_support.find_manifest_record(
                                scorecard,
                                manifest_id,
                            ),
                            manifest=manifest,
                            manifest_path=str(
                                manifest.path.relative_to(REPO_ROOT)
                            ),
                            known_gap_count=manifest_expectation.known_gap_count,
                            selection_mode=case.selection_mode,
                            selected_workload_ids=case.selected_workload_ids_for_manifest(
                                manifest_id
                            ),
                        )

                for expected_status, workload_ids in (
                    ("measured", case.representative_measured_workload_ids),
                    ("unimplemented", case.representative_known_gap_workload_ids),
                ):
                    for workload_id in workload_ids:
                        with self.subTest(
                            workload_id=workload_id,
                            expected_status=expected_status,
                        ):
                            workload_record = benchmark_test_support.find_workload_record(
                                scorecard,
                                workload_id,
                            )
                            manifest_id = workload_record["manifest_id"]
                            manifest = case.manifest_for_id(manifest_id)
                            benchmark_test_support.assert_benchmark_workload_contract(
                                self,
                                workload_record,
                                manifest_id=manifest_id,
                                workload_document=benchmark_test_support.find_workload_document(
                                    manifest,
                                    workload_id,
                                ),
                                expected_status=expected_status,
                            )


# Detached benchmark-anchor contract coverage from the former
# `test_standard_benchmark_correctness_anchor_contracts.py` lives below so this
# file is the single benchmark-owner suite.


@pytest.mark.parametrize(
    ("case_group", "source_workload"),
    tuple(
        pytest.param(case_group, source_workload, id=source_workload.workload_id)
        for case_group in _COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES
        for source_workload in case_group.source_workloads()
        if source_workload.expected_exception
    ),
)
def test_standard_benchmark_compiled_pattern_module_compile_validation_accepts_bounded_ignorecase_rejection_rows(
    tmp_path: pathlib.Path,
    case_group: object,
    source_workload: Workload,
) -> None:
    manifest = _source_tree_contract_manifest(
        (source_workload,),
        spec=case_group.contract_builder_spec(),
    )
    manifest_path = benchmark_test_support._write_test_manifest(
        tmp_path,
        "python_benchmark_compiled_pattern_module_compile_ignorecase_validation_contract.py",
        f"MANIFEST = {manifest!r}\n",
    )
    workload = load_manifest(manifest_path).workloads[0]
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    case_group.assert_payload_round_trip(
        source_workload,
        payload,
        round_tripped,
    )


@pytest.mark.parametrize(
    "contract_case",
    _COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES,
    ids=lambda contract_case: contract_case.case_id,
)
def test_standard_benchmark_compiled_pattern_module_compile_contract_rows_preserve_success_and_keyword_payload_round_trip_until_helper_invocation(
    tmp_path: pathlib.Path,
    contract_case: object,
) -> None:
    source_workloads = contract_case.source_workloads()
    manifest = _source_tree_contract_manifest(
        source_workloads,
        spec=contract_case.contract_builder_spec(),
    )
    manifest_path = benchmark_test_support._write_test_manifest(
        tmp_path,
        contract_case.contract_filename,
        f"MANIFEST = {manifest!r}\n",
    )
    workloads = load_manifest(manifest_path).workloads

    assert tuple(workload.workload_id for workload in source_workloads) == tuple(
        contract_case.expected_source_workload_ids()
    )
    assert tuple(workload.workload_id for workload in workloads) == tuple(
        workload_id for workload_id, _case_id in contract_case.expected_anchor_pairs
    )
    assert [workload.use_compiled_pattern for workload in workloads] == [
        True
    ] * len(source_workloads)
    assert [workload.haystack_text_model for workload in workloads] == [
        None
    ] * len(source_workloads)

    for source_workload, workload in zip(
        source_workloads,
        workloads,
        strict=True,
    ):
        payload = workload_to_payload(workload)
        round_tripped = workload_from_payload(payload)

        contract_case.assert_payload_round_trip(
            source_workload,
            payload,
            round_tripped,
        )
        if source_workload.expected_exception is None:
            benchmark_test_support.assert_benchmark_workload_matches_expected_result(
                round_tripped,
                contract_case.run_cpython_workload(workload),
            )
            continue

        expected_exception = benchmark_test_support._expected_exception_instance(
            source_workload.expected_exception
        )
        with pytest.raises(
            type(expected_exception),
            match=source_workload.expected_exception["message_substring"],
        ) as expected_error:
            contract_case.run_cpython_workload(workload)
        with pytest.raises(type(expected_error.value)) as observed_error:
            benchmark_test_support.run_benchmark_workload_with_cpython(round_tripped)
        assert str(observed_error.value) == str(expected_error.value)


def test_standard_benchmark_compiled_pattern_module_compile_keyword_payload_round_trip_preserves_keyword_signature_type(
    tmp_path: pathlib.Path,
) -> None:
    contract_case = next(
        case
        for case in _COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES
        if case.case_id == "bool-false"
    )
    source_workload = contract_case.source_workloads()[0]
    manifest = _source_tree_contract_manifest(
        (source_workload,),
        spec=contract_case.contract_builder_spec(),
    )
    manifest_path = benchmark_test_support._write_test_manifest(
        tmp_path,
        "python_benchmark_compiled_pattern_module_compile_keyword_type_contract.py",
        f"MANIFEST = {manifest!r}\n",
    )
    workload = load_manifest(manifest_path).workloads[0]
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    contract_case.assert_payload_round_trip(
        source_workload,
        payload,
        round_tripped,
    )

    assert source_workload.kwargs == {"flags": False}
    assert contract_case.keyword_signature == (("flags", "bool", False),)
    assert type(payload["kwargs"]["flags"]) is bool
    assert type(round_tripped.kwargs["flags"]) is bool


@pytest.mark.parametrize(
    "spec",
    tuple(
        pytest.param(spec, id=str(spec["case_id"]))
        for spec in _compiled_pattern_wrong_text_model_specs()
    ),
)
def test_standard_benchmark_compiled_pattern_wrong_text_model_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation(
    tmp_path: pathlib.Path,
    spec: dict[str, object],
) -> None:
    source_workloads = _compiled_pattern_wrong_text_model_source_workloads(
        spec
    )
    manifest = _source_tree_contract_manifest(
        source_workloads,
        spec=_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_SPECS[
            str(spec["contract_manifest_id"])
        ],
    )
    manifest_path = benchmark_test_support._write_test_manifest(
        tmp_path,
        str(spec["contract_filename"]),
        f"MANIFEST = {manifest!r}\n",
    )
    workloads = tuple(load_manifest(manifest_path).workloads)

    assert tuple(workload.workload_id for workload in source_workloads) == tuple(
        spec["expected_source_workload_ids"]
    )
    assert tuple(workload.workload_id for workload in workloads) == tuple(
        f"{workload_id}-contract" for workload_id in spec["expected_source_workload_ids"]
    )
    assert [workload.use_compiled_pattern for workload in workloads] == [True] * len(
        source_workloads
    )
    assert [workload.timing_scope for workload in workloads] == [
        "module-helper-call"
    ] * len(source_workloads)
    assert [workload.haystack_text_model for workload in workloads] == [
        workload.haystack_text_model for workload in source_workloads
    ]

    for source_workload, workload in zip(source_workloads, workloads, strict=True):
        payload = workload_to_payload(workload)
        round_tripped = workload_from_payload(payload)

        _assert_wrong_text_model_payload_round_trip(
            source_workload,
            payload,
            round_tripped,
        )

        with pytest.raises(TypeError) as expected_error:
            _run_cpython_compiled_pattern_module_helper_workload(
                workload,
                collection_replacement_callback_flags=0,
            )
        with pytest.raises(TypeError) as observed_error:
            benchmark_test_support.run_benchmark_workload_with_cpython(round_tripped)

        assert str(observed_error.value) == str(expected_error.value)


@pytest.mark.parametrize(
    "owner_spec",
    _COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS,
    ids=lambda owner_spec: owner_spec.case_id,
)
def test_standard_benchmark_compiled_pattern_module_success_contract_rows_preserve_live_source_selection_and_payload_round_trip_until_helper_invocation(
    tmp_path: pathlib.Path,
    owner_spec: object,
) -> None:
    source_workloads = owner_spec.source_workloads()
    manifest = _source_tree_contract_manifest(
        source_workloads,
        spec=owner_spec.contract_builder_spec(),
    )
    manifest_path = benchmark_test_support._write_test_manifest(
        tmp_path,
        owner_spec.contract_filename,
        f"MANIFEST = {manifest!r}\n",
    )
    workloads = load_manifest(manifest_path).workloads

    assert tuple(workload.workload_id for workload in source_workloads) == (
        owner_spec.expected_source_workload_ids
    )
    assert all(
        include_live_compiled_pattern_module_success_workload(
            workload
        )
        for workload in source_workloads
    )
    assert tuple(workload.workload_id for workload in workloads) == tuple(
        f"{workload.workload_id}-contract" for workload in source_workloads
    )
    assert [workload.use_compiled_pattern for workload in workloads] == [
        True
    ] * len(source_workloads)
    assert [workload.haystack_text_model for workload in workloads] == [
        None
    ] * len(source_workloads)

    for source_workload, workload in zip(source_workloads, workloads, strict=True):
        payload = workload_to_payload(workload)
        round_tripped = workload_from_payload(payload)

        _assert_compiled_pattern_module_success_payload_round_trip(
            source_workload,
            payload,
            round_tripped,
            owner_spec=owner_spec,
        )
        benchmark_test_support.assert_benchmark_workload_matches_expected_result(
            round_tripped,
            benchmark_test_support.run_benchmark_workload_with_cpython(round_tripped),
        )


@pytest.mark.parametrize(
    "contract_surface",
    _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACE_PARAMS,
    ids=lambda contract_surface: contract_surface.case_id,
)
def test_standard_benchmark_compiled_pattern_module_helper_keyword_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation(
    tmp_path: pathlib.Path,
    contract_surface: object,
) -> None:
    source_workloads = contract_surface.source_workloads()
    manifest = _source_tree_contract_manifest(
        source_workloads,
        spec=contract_surface.spec.contract_builder_spec(),
    )
    manifest_path = benchmark_test_support._write_test_manifest(
        tmp_path,
        contract_surface.spec.contract_filename,
        f"MANIFEST = {manifest!r}\n",
    )
    workloads = load_manifest(manifest_path).workloads

    assert tuple(workload.workload_id for workload in source_workloads) == (
        contract_surface.spec.expected_source_workload_ids
    )
    assert tuple(workload.workload_id for workload in workloads) == tuple(
        f"{workload.workload_id}-contract" for workload in source_workloads
    )
    assert [workload.use_compiled_pattern for workload in workloads] == [
        True
    ] * len(source_workloads)
    assert [workload.haystack_text_model for workload in workloads] == [
        None
    ] * len(source_workloads)

    for source_workload, workload in zip(
        source_workloads,
        workloads,
        strict=True,
    ):
        payload = workload_to_payload(workload)
        round_tripped = workload_from_payload(payload)

        contract_surface.assert_payload_round_trip(
            source_workload,
            payload,
            round_tripped,
        )
        contract_surface.assert_outcome(
            source_workload,
            workload,
            round_tripped,
        )


def test_compiled_pattern_module_helper_keyword_contract_rows_preserve_keyword_payload_types_field_names_and_bool_count_complements(
) -> None:
    success_surface = next(
        surface
        for surface in (
            _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES
        )
        if surface.case_id == "success"
    )
    keyword_error_surface = next(
        surface
        for surface in (
            _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES
        )
        if surface.case_id == "keyword-error"
    )

    success_source_workload = next(
        workload
        for workload in success_surface.source_workloads()
        if workload.workload_id
        == "module-sub-count-bool-false-keyword-warm-str-compiled-pattern"
    )
    success_workload = _source_tree_contract_workload(
        success_source_workload,
        spec=success_surface.spec.contract_builder_spec(),
    )
    success_payload = workload_to_payload(success_workload)
    success_round_tripped = workload_from_payload(success_payload)

    success_surface.assert_payload_round_trip(
        success_source_workload,
        success_payload,
        success_round_tripped,
    )
    assert success_payload.get("expected_exception") is None
    assert success_round_tripped.expected_exception is None
    assert type(success_payload["kwargs"]["count"]) is bool
    assert type(success_round_tripped.kwargs["count"]) is bool

    keyword_error_source_workload = next(
        workload
        for workload in keyword_error_surface.source_workloads()
        if workload.workload_id
        == "module-sub-unexpected-keyword-after-positional-count-purged-str-compiled-pattern"
    )
    keyword_error_workload = _source_tree_contract_workload(
        keyword_error_source_workload,
        spec=keyword_error_surface.spec.contract_builder_spec(),
    )
    keyword_error_payload = workload_to_payload(keyword_error_workload)
    keyword_error_round_tripped = workload_from_payload(keyword_error_payload)

    keyword_error_surface.assert_payload_round_trip(
        keyword_error_source_workload,
        keyword_error_payload,
        keyword_error_round_tripped,
    )
    assert (
        keyword_error_payload["expected_exception"]
        == keyword_error_source_workload.expected_exception
    )
    assert (
        keyword_error_round_tripped.expected_exception
        == keyword_error_source_workload.expected_exception
    )

    split_duplicate_workload = next(
        workload
        for workload in keyword_error_surface.source_workloads()
        if workload.workload_id
        == "module-split-duplicate-maxsplit-keyword-purged-str-compiled-pattern"
    )
    sub_keyword_workload = next(
        workload
        for workload in success_surface.source_workloads()
        if workload.workload_id == "module-sub-count-keyword-warm-str-compiled-pattern"
    )

    assert keyword_error_surface.spec.expected_materialized_field_names(
        split_duplicate_workload
    ) == ("maxsplit", "kwargs.maxsplit")
    assert success_surface.spec.expected_materialized_field_names(
        sub_keyword_workload
    ) == ("kwargs.count",)

    assert {
        (
            workload.workload_id,
            workload.operation,
            workload.text_model,
            workload.kwargs["count"],
            benchmark_test_support.run_benchmark_workload_with_cpython(workload),
        )
        for workload in (
            _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS
        )
        if workload.operation in {"module.sub", "module.subn"}
        and type(workload.kwargs.get("count")) is bool
    } == {
        (
            "module-sub-count-bool-keyword-warm-str-compiled-pattern",
            "module.sub",
            "str",
            True,
            "xabc",
        ),
        (
            "module-sub-count-bool-false-keyword-warm-str-compiled-pattern",
            "module.sub",
            "str",
            False,
            "xx",
        ),
        (
            "module-subn-count-bool-keyword-purged-bytes-compiled-pattern",
            "module.subn",
            "bytes",
            False,
            (b"xx", 2),
        ),
        (
            "module-subn-count-bool-true-keyword-purged-bytes-compiled-pattern",
            "module.subn",
            "bytes",
            True,
            (b"xabc", 1),
        ),
    }


def test_compiled_pattern_module_helper_keyword_contract_rows_preserve_cpython_outcomes_across_success_and_error_lanes(
) -> None:
    success_surface = next(
        surface
        for surface in (
            _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES
        )
        if surface.case_id == "success"
    )
    success_source_workload = next(
        workload
        for workload in success_surface.source_workloads()
        if workload.workload_id
        == "module-subn-count-keyword-purged-bytes-compiled-pattern"
    )
    success_workload = _source_tree_contract_workload(
        success_source_workload,
        spec=success_surface.spec.contract_builder_spec(),
    )
    success_payload = workload_to_payload(success_workload)
    success_round_tripped = workload_from_payload(success_payload)

    success_surface.assert_outcome(
        success_source_workload,
        success_workload,
        success_round_tripped,
    )
    assert success_surface.run_cpython_helper_workload(success_workload) == (
        b"xabc",
        1,
    )

    keyword_error_surface = next(
        surface
        for surface in (
            _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES
        )
        if surface.case_id == "keyword-error"
    )
    keyword_error_source_workload = next(
        workload
        for workload in keyword_error_surface.source_workloads()
        if workload.workload_id
        == "module-subn-count-alias-keyword-purged-bytes-compiled-pattern"
    )
    keyword_error_workload = _source_tree_contract_workload(
        keyword_error_source_workload,
        spec=keyword_error_surface.spec.contract_builder_spec(),
    )
    keyword_error_payload = workload_to_payload(keyword_error_workload)
    keyword_error_round_tripped = workload_from_payload(keyword_error_payload)

    keyword_error_surface.assert_outcome(
        keyword_error_source_workload,
        keyword_error_workload,
        keyword_error_round_tripped,
    )
    with pytest.raises(TypeError):
        benchmark_test_support.run_benchmark_workload_with_cpython(
            keyword_error_round_tripped
        )


@pytest.mark.parametrize(
    "source_workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in benchmark_test_support.selected_manifest_workloads(
            benchmarks.BENCHMARK_WORKLOADS_ROOT / "pattern_boundary.py",
            include_workload=benchmark_test_support._is_pattern_boundary_wrong_text_model_workload,
        )
    ),
)
def test_standard_benchmark_haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio(
    tmp_path: pathlib.Path,
    source_workload: Workload,
) -> None:
    manifest = _source_tree_contract_manifest(
        (source_workload,),
        spec=_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC,
    )
    manifest_path = benchmark_test_support._write_test_manifest(
        tmp_path,
        f"python_benchmark_{source_workload.workload_id}_haystack_text_model_contract.py",
        f"MANIFEST = {manifest!r}\n",
    )
    loaded_workload = load_manifest(manifest_path).workloads[0]
    payload = workload_to_payload(loaded_workload)
    round_tripped = workload_from_payload(payload)

    benchmark_test_support.assert_pattern_helper_wrong_text_model_payload_round_trip(
        source_workload,
        payload,
        round_tripped,
    )
    assert loaded_workload.workload_id == f"{source_workload.workload_id}-contract"


@pytest.mark.parametrize(
    ("owner_spec", "include_workload"),
    (
        pytest.param(
            _COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC,
            _is_collection_replacement_compiled_pattern_success_workload,
            id="collection-replacement-success",
        ),
        pytest.param(
            _COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC,
            benchmark_test_support._is_module_workflow_compiled_pattern_literal_success_workload,
            id="module-boundary-literal-success",
        ),
        pytest.param(
            _COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC,
            benchmark_test_support._is_module_workflow_compiled_pattern_bounded_wildcard_success_workload,
            id="module-boundary-bounded-wildcard-success",
        ),
        pytest.param(
            _COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC,
            benchmark_test_support._is_module_workflow_compiled_pattern_verbose_bytes_success_workload,
            id="module-boundary-verbose-bytes-success",
        ),
    ),
)
def test_compiled_pattern_module_helper_owner_specs_keep_zero_gap_rows_measured(
    owner_spec: object,
    include_workload: object,
) -> None:
    manifest_workload_count = len(benchmark_test_support.selected_manifest_workloads(owner_spec.manifest_path))
    manifest_id = owner_spec.source_workloads()[0].manifest_id
    expected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in benchmark_test_support.selected_manifest_workloads(
            owner_spec.manifest_path,
            include_workload=include_workload,
        )
    )

    benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
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
        for spec in _compiled_pattern_wrong_text_model_specs()
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
    for source_workload in _compiled_pattern_wrong_text_model_source_workloads(
        spec
    ):
        workload = _source_tree_contract_workload(
            source_workload,
            spec=_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_SPECS[
                str(spec["contract_manifest_id"])
            ],
        )
        payload = workload_to_payload(workload)
        round_tripped = workload_from_payload(payload)

        _assert_wrong_text_model_payload_round_trip(
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
        for spec in _compiled_pattern_wrong_text_model_specs()
    ),
)
def test_compiled_pattern_wrong_text_model_callbacks_preserve_precompile_contract(
    spec: dict[str, object],
) -> None:
    for source_workload in _compiled_pattern_wrong_text_model_source_workloads(
        spec
    ):
        expected_build_calls = compiled_pattern_contract_expected_build_calls(
            source_workload,
            label="wrong-text-model",
        )
        expected_callback_result, expected_callback_call, _, _ = (
            _compiled_pattern_module_helper_route(
                source_workload,
                collection_replacement_callback_flags=0,
            )
        )
        module = benchmark_test_support.RecordingBenchmarkModule()
        callback = benchmarks.build_callable(
            module,
            "re",
            _source_tree_contract_workload(
                source_workload,
                spec=_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_SPECS[
                    str(spec["contract_manifest_id"])
                ],
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
    _COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS,
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

    _assert_compiled_pattern_module_success_payload_round_trip(
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
    _COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS,
)
def test_compiled_pattern_module_success_callbacks_precompile_first_argument_before_timing(
    owner_spec: object,
    source_workload: Workload,
) -> None:
    expected_build_calls = owner_spec.expected_build_calls(source_workload)
    expected_callback_call = owner_spec.expected_callback_call(source_workload)
    module = benchmark_test_support.RecordingBenchmarkModule()
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
        for workload in benchmark_test_support.selected_manifest_workloads(
            benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
            include_workload=(
                _is_collection_replacement_compiled_pattern_keyword_error_workload
            ),
        )
    )
    expected_source_workload_ids = tuple(
        workload.workload_id
        for workload in (
            _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS
        )
    )
    manifest_workload_count = len(
        benchmark_test_support.selected_manifest_workloads(
            benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH
        )
    )

    assert expected_measured_workload_ids == expected_source_workload_ids
    benchmark_test_support.assert_zero_gap_manifest_workloads_measured(
        manifest_path=benchmark_test_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
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
            _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS
        )
    ),
)
def test_compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time(
    monkeypatch: pytest.MonkeyPatch,
    source_workload: Workload,
) -> None:
    workload = _source_tree_contract_workload(
        source_workload,
        spec=_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC.contract_builder_spec(),
    )
    _assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call(
        monkeypatch,
        workload,
        expected_result=benchmark_test_support.run_benchmark_workload_with_cpython(source_workload),
        expected_field_names=(
            _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC.expected_materialized_field_names(
                source_workload
            )
        ),
    )


@pytest.mark.parametrize(
    ("contract_surface", "source_workload"),
    _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS,
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
    _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS,
)
def test_compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing(
    contract_surface: object,
    source_workload: Workload,
) -> None:
    expected_build_calls = contract_surface.expected_build_calls(source_workload)
    expected_callback_call = contract_surface.expected_callback_call(source_workload)
    module = benchmark_test_support.RecordingBenchmarkModule()
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
            _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS
        )
    ),
)
def test_compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions(
    monkeypatch: pytest.MonkeyPatch,
    source_workload: Workload,
) -> None:
    contract_surface = next(
        surface
        for surface in (
            _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES
        )
        if surface.case_id == "keyword-error"
    )
    workload = _source_tree_contract_workload(
        source_workload,
        spec=_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC.contract_builder_spec(),
    )
    observed_field_names = benchmark_test_support._record_numeric_materialization_fields(monkeypatch)

    re.purge()
    try:
        callback = benchmarks.build_callable(re, "re", workload)
        assert observed_field_names == []

        with pytest.raises(TypeError) as expected_error:
            contract_surface.run_cpython_helper_workload(workload)
        with pytest.raises(TypeError) as observed_error:
            callback()

        assert observed_field_names == list(
            _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC.expected_materialized_field_names(
                source_workload
            )
        )
        assert str(observed_error.value) == str(expected_error.value)
    finally:
        re.purge()
