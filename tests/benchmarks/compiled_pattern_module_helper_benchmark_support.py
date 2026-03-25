from __future__ import annotations

from dataclasses import dataclass
from functools import cache
import re
from typing import Any

import pytest

from rebar_harness.benchmarks import BENCHMARK_WORKLOADS_ROOT
from rebar_harness.benchmarks import Workload
from tests.benchmarks.benchmark_test_support import (
    COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS,
    StandardBenchmarkAnchorContractDefinition,
    _SourceTreeContractBuilderSpec,
    _collection_replacement_keyword_parameter_name,
    _collection_replacement_positional_keyword_field,
    _compiled_pattern_module_helper_route,
    _is_module_workflow_compiled_pattern_bounded_wildcard_success_workload,
    _is_module_workflow_compiled_pattern_literal_success_workload,
    _is_module_workflow_compiled_pattern_verbose_bytes_success_workload,
    _module_workflow_compiled_pattern_correctness_case_signature,
    _module_workflow_compiled_pattern_workload_signature,
    _is_module_workflow_compiled_pattern_wrong_text_model_workload,
    assert_benchmark_workload_matches_expected_result,
    compiled_pattern_contract_expected_build_calls,
    _is_collection_replacement_keyword_workload,
    _is_collection_replacement_wrong_text_model_workload,
    run_benchmark_workload_with_cpython,
    selected_manifest_workloads,
)
COLLECTION_REPLACEMENT_MANIFEST_PATH = (
    BENCHMARK_WORKLOADS_ROOT / "collection_replacement_boundary.py"
)
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
            "include_workload": _is_module_workflow_compiled_pattern_wrong_text_model_workload,
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
    return selected_manifest_workloads(
        spec["manifest_path"],
        include_workload=spec["include_workload"],
    )


def _compiled_pattern_wrong_text_model_contract_spec(
    spec: dict[str, object],
) -> _SourceTreeContractBuilderSpec:
    notes: tuple[str, ...]
    if spec["contract_manifest_id"] == "collection-replacement-boundary":
        notes = (
            "Ensures benchmark manifests keep the bounded compiled-pattern-first-argument wrong-text-model collection/replacement rows unresolved until helper invocation.",
        )
    else:
        notes = (
            "Ensures benchmark manifests keep the bounded compiled-pattern-first-argument wrong-text-model module-boundary rows unresolved until helper invocation.",
        )
    return _SourceTreeContractBuilderSpec(
        manifest_id=spec["contract_manifest_id"],
        excluded_fields=COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS,
        timing_scope="module-helper-call",
        notes=notes,
    )


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


@cache
def _build_compiled_pattern_module_helper_standard_benchmark_definitions() -> tuple[
    object, ...
]:
    from tests.benchmarks.benchmark_test_support import (
        _definition_anchor_expectations,
        MODULE_BOUNDARY_MANIFEST_PATH,
    )

    return (
        StandardBenchmarkAnchorContractDefinition(
            name="module-workflow-compiled-pattern-literal-success",
            manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
            expected_anchor_case_ids=_definition_anchor_expectations(
                MODULE_BOUNDARY_MANIFEST_PATH,
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
            include_workload=_is_module_workflow_compiled_pattern_literal_success_workload,
            correctness_case_signature=(
                _module_workflow_compiled_pattern_correctness_case_signature
            ),
            workload_signature=_module_workflow_compiled_pattern_workload_signature,
            run_callback_result_parity=True,
        ),
        StandardBenchmarkAnchorContractDefinition(
            name="module-workflow-compiled-pattern-bounded-wildcard-success",
            manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
            expected_anchor_case_ids=_definition_anchor_expectations(
                MODULE_BOUNDARY_MANIFEST_PATH,
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
                _is_module_workflow_compiled_pattern_bounded_wildcard_success_workload
            ),
            correctness_case_signature=(
                _module_workflow_compiled_pattern_correctness_case_signature
            ),
            workload_signature=_module_workflow_compiled_pattern_workload_signature,
            run_callback_result_parity=True,
        ),
        StandardBenchmarkAnchorContractDefinition(
            name="module-workflow-compiled-pattern-verbose-bytes-success",
            manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
            expected_anchor_case_ids=_definition_anchor_expectations(
                MODULE_BOUNDARY_MANIFEST_PATH,
                {
                    "module-search-verbose-regression-warm-hit-bytes-compiled-pattern": (
                        "workflow-module-search-bytes-verbose-regression-compiled-pattern",
                    ),
                    "module-fullmatch-verbose-regression-purged-hit-bytes-compiled-pattern": (
                        "workflow-module-fullmatch-bytes-verbose-regression-compiled-pattern",
                    ),
                },
            ),
            include_workload=_is_module_workflow_compiled_pattern_verbose_bytes_success_workload,
            correctness_case_signature=(
                _module_workflow_compiled_pattern_correctness_case_signature
            ),
            workload_signature=_module_workflow_compiled_pattern_workload_signature,
            run_callback_result_parity=True,
        ),
        StandardBenchmarkAnchorContractDefinition(
            name="module-workflow-compiled-pattern-wrong-text-model",
            manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
            expected_anchor_case_ids=_definition_anchor_expectations(
                MODULE_BOUNDARY_MANIFEST_PATH,
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
                _module_workflow_compiled_pattern_correctness_case_signature
            ),
            workload_signature=_module_workflow_compiled_pattern_workload_signature,
        ),
    )


COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS = (
    _build_compiled_pattern_module_helper_standard_benchmark_definitions()
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


@dataclass(frozen=True, slots=True)
class _CompiledPatternModuleHelperKeywordContractSpec:
    contract_filename: str
    expected_source_workload_ids: tuple[str, ...]
    manifest_timed_samples: int
    preserve_expected_exception: bool
    materializes_positional_keyword_field: bool
    notes: tuple[str, ...] = ()
    precompile_anchor_ids: tuple[str, ...] = ()

    def contract_builder_spec(self) -> _SourceTreeContractBuilderSpec:
        excluded_fields = (
            _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_PAYLOAD_DROP_FIELDS
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

    def expected_materialized_field_names(
        self,
        source_workload: Workload,
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


@dataclass(frozen=True, slots=True)
class _CompiledPatternModuleHelperKeywordContractSurface:
    case_id: str
    spec: _CompiledPatternModuleHelperKeywordContractSpec
    source_workloads_value: tuple[Workload, ...]
    precompile_source_workloads_value: tuple[Workload, ...] | None = None

    def source_workloads(self) -> tuple[Workload, ...]:
        return self.source_workloads_value

    def precompile_source_workloads(self) -> tuple[Workload, ...]:
        return self.precompile_source_workloads_value or self.source_workloads_value

    def expected_build_calls(
        self,
        source_workload: Workload,
    ) -> list[tuple[object, ...]]:
        return compiled_pattern_contract_expected_build_calls(
            source_workload,
            label="module helper keyword",
        )

    def expected_callback_call(
        self,
        source_workload: Workload,
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

    def expected_callback_result(self, source_workload: Workload) -> object:
        if source_workload.operation == "module.subn":
            return ("module-result", 0)
        return "module-result"

    def run_cpython_helper_workload(
        self,
        workload: Workload,
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
        source_workload: Workload,
        workload: Workload,
        round_tripped: Workload,
    ) -> None:
        if self.case_id == "success":
            assert_benchmark_workload_matches_expected_result(
                round_tripped,
                run_benchmark_workload_with_cpython(source_workload),
            )
            return

        if self.case_id == "keyword-error":
            with pytest.raises(TypeError) as expected_error:
                self.run_cpython_helper_workload(workload)
            with pytest.raises(TypeError) as observed_error:
                run_benchmark_workload_with_cpython(round_tripped)
            assert str(observed_error.value) == str(expected_error.value)
            return

        raise AssertionError(
            "unexpected compiled-pattern module helper keyword contract surface "
            f"{self.case_id!r}"
        )

    def assert_payload_round_trip(
        self,
        source_workload: Workload,
        payload: dict[str, object],
        round_tripped: Workload,
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
        assert isinstance(round_tripped.pattern_payload(), expected_text_type)
        assert isinstance(round_tripped.haystack_payload(), expected_text_type)
        if source_workload.replacement is not None:
            assert isinstance(round_tripped.replacement_payload(), expected_text_type)
        for name, value in source_workload.kwargs.items():
            if type(value) is bool:
                assert type(payload["kwargs"][name]) is bool
                assert type(round_tripped.kwargs[name]) is bool


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
    selected_manifest_workloads(
        COLLECTION_REPLACEMENT_MANIFEST_PATH,
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
    selected_manifest_workloads(
        COLLECTION_REPLACEMENT_MANIFEST_PATH,
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
