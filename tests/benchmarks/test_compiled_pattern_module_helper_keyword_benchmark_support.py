from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Any

import pytest

from rebar_harness.benchmarks import (
    BENCHMARK_WORKLOADS_ROOT,
    Workload,
    build_callable,
    load_manifest,
    run_internal_workload_probe,
    workload_from_payload,
    workload_to_payload,
)
from tests.benchmarks.benchmark_test_support import (
    _assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call,
    _record_numeric_materialization_fields,
    assert_zero_gap_manifest_workloads_measured,
    selected_manifest_workloads,
    _write_test_manifest,
)
from tests.benchmarks.collection_replacement_benchmark_anchor_support import (
    _collection_replacement_keyword_parameter_name,
    _collection_replacement_positional_keyword_field,
    _is_collection_replacement_keyword_workload,
)
from tests.benchmarks.recording_benchmark_module_support import (
    RecordingBenchmarkModule,
)
from tests.benchmarks.source_tree_benchmark_anchor_support import (
    assert_benchmark_workload_matches_expected_result,
    run_benchmark_workload_with_cpython,
)
from tests.benchmarks.source_tree_contract_benchmark_support import (
    _SourceTreeContractBuilderSpec,
    _source_tree_contract_manifest,
    _source_tree_contract_workload,
    compiled_pattern_contract_expected_build_calls,
)

COLLECTION_REPLACEMENT_MANIFEST_PATH = (
    BENCHMARK_WORKLOADS_ROOT / "collection_replacement_boundary.py"
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


def _contract_surface(case_id: str):
    return next(
        surface
        for surface in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES
        if surface.case_id == case_id
    )


def test_compiled_pattern_module_helper_keyword_source_workload_order_stays_pinned() -> None:
    success_surface = _contract_surface("success")
    keyword_error_surface = _contract_surface("keyword-error")

    assert tuple(
        workload.workload_id for workload in success_surface.source_workloads()
    ) == _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC.expected_source_workload_ids
    assert tuple(
        workload.workload_id for workload in keyword_error_surface.source_workloads()
    ) == _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC.expected_source_workload_ids


def test_collection_replacement_manifest_keeps_compiled_pattern_module_helper_keyword_error_rows_measured() -> None:
    expected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in selected_manifest_workloads(
            COLLECTION_REPLACEMENT_MANIFEST_PATH,
            include_workload=_is_collection_replacement_compiled_pattern_keyword_error_workload,
        )
    )
    expected_source_workload_ids = tuple(
        workload.workload_id
        for workload in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS
    )
    manifest_workload_count = len(
        selected_manifest_workloads(COLLECTION_REPLACEMENT_MANIFEST_PATH)
    )

    assert expected_measured_workload_ids == expected_source_workload_ids
    assert_zero_gap_manifest_workloads_measured(
        manifest_path=COLLECTION_REPLACEMENT_MANIFEST_PATH,
        manifest_id="collection-replacement-boundary",
        expected_measured_workload_ids=expected_measured_workload_ids,
        expected_measured_workload_count=manifest_workload_count,
        expected_total_workload_count=manifest_workload_count,
    )


def test_compiled_pattern_module_helper_keyword_success_payload_round_trip_preserves_bool_type() -> None:
    success_surface = _contract_surface("success")
    source_workload = next(
        workload
        for workload in success_surface.source_workloads()
        if workload.workload_id == "module-sub-count-bool-false-keyword-warm-str-compiled-pattern"
    )
    workload = _source_tree_contract_workload(
        source_workload,
        spec=success_surface.spec.contract_builder_spec(),
    )
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    success_surface.assert_payload_round_trip(
        source_workload,
        payload,
        round_tripped,
    )

    assert payload.get("expected_exception") is None
    assert round_tripped.expected_exception is None
    assert type(payload["kwargs"]["count"]) is bool
    assert type(round_tripped.kwargs["count"]) is bool


def test_compiled_pattern_module_helper_keyword_error_payload_round_trip_preserves_expected_exception() -> None:
    keyword_error_surface = _contract_surface("keyword-error")
    source_workload = next(
        workload
        for workload in keyword_error_surface.source_workloads()
        if workload.workload_id
        == "module-sub-unexpected-keyword-after-positional-count-purged-str-compiled-pattern"
    )
    workload = _source_tree_contract_workload(
        source_workload,
        spec=keyword_error_surface.spec.contract_builder_spec(),
    )
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    keyword_error_surface.assert_payload_round_trip(
        source_workload,
        payload,
        round_tripped,
    )

    assert payload["expected_exception"] == source_workload.expected_exception
    assert round_tripped.expected_exception == source_workload.expected_exception


def test_compiled_pattern_module_helper_keyword_expected_materialized_field_names_cover_split_and_sub() -> None:
    success_surface = _contract_surface("success")
    keyword_error_surface = _contract_surface("keyword-error")

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


def test_compiled_pattern_module_helper_keyword_precompile_anchor_order_stays_pinned() -> None:
    assert tuple(
        workload.workload_id
        for workload in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS
    ) == _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC.precompile_anchor_ids


def test_compiled_pattern_module_helper_keyword_cpython_outcomes_cover_success_and_error_lanes() -> None:
    success_surface = _contract_surface("success")
    success_source_workload = next(
        workload
        for workload in success_surface.source_workloads()
        if workload.workload_id == "module-subn-count-keyword-purged-bytes-compiled-pattern"
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

    keyword_error_surface = _contract_surface("keyword-error")
    keyword_error_source_workload = next(
        workload
        for workload in keyword_error_surface.source_workloads()
        if workload.workload_id == "module-subn-count-alias-keyword-purged-bytes-compiled-pattern"
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
        run_benchmark_workload_with_cpython(keyword_error_round_tripped)


def test_compiled_pattern_module_helper_keyword_cases_cover_bool_count_complements() -> None:
    assert {
        (
            workload.workload_id,
            workload.operation,
            workload.text_model,
            workload.kwargs["count"],
            run_benchmark_workload_with_cpython(workload),
        )
        for workload in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS
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


@pytest.mark.parametrize(
    "contract_surface",
    _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACE_PARAMS,
)
def test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_keyword_contract_rows_until_helper_invocation(
    tmp_path,
    contract_surface,
) -> None:
    source_workloads = contract_surface.source_workloads()
    manifest = _source_tree_contract_manifest(
        source_workloads,
        spec=contract_surface.spec.contract_builder_spec(),
    )

    manifest_path = _write_test_manifest(
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


@pytest.mark.parametrize(
    "source_workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS
    ),
)
def test_compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time(
    monkeypatch,
    source_workload,
) -> None:
    workload = _source_tree_contract_workload(
        source_workload,
        spec=_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC.contract_builder_spec(),
    )
    _assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call(
        monkeypatch,
        workload,
        expected_result=run_benchmark_workload_with_cpython(source_workload),
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
    contract_surface,
    source_workload,
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

    probe = run_internal_workload_probe(
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
    contract_surface,
    source_workload,
) -> None:
    expected_build_calls = contract_surface.expected_build_calls(source_workload)
    expected_callback_call = contract_surface.expected_callback_call(source_workload)
    module = RecordingBenchmarkModule()
    callback = build_callable(
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
        for workload in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS
    ),
)
def test_compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions(
    monkeypatch,
    source_workload,
) -> None:
    contract_surface = next(
        surface
        for surface in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES
        if surface.case_id == "keyword-error"
    )
    workload = _source_tree_contract_workload(
        source_workload,
        spec=_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC.contract_builder_spec(),
    )
    observed_field_names = _record_numeric_materialization_fields(monkeypatch)

    re.purge()
    try:
        callback = build_callable(re, "re", workload)
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
