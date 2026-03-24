from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import pathlib
import re
from typing import Any

import pytest

from rebar_harness.benchmarks import (
    BENCHMARK_WORKLOADS_ROOT,
    Workload,
)
from tests.benchmarks.collection_replacement_benchmark_anchor_support import (
    _collection_replacement_wrong_text_model_haystack_index,
)
from tests.benchmarks.compiled_pattern_module_helper_benchmark_support import (
    _compiled_pattern_module_helper_route,
)
from tests.benchmarks.compiled_pattern_module_helper_keyword_benchmark_support import (
    _compiled_pattern_contract_expected_build_calls,
)
from tests.benchmarks.source_tree_benchmark_anchor_support import (
    freeze_signature_value,
)
from tests.benchmarks.source_tree_contract_benchmark_support import (
    _SourceTreeContractBuilderSpec,
    _contract_source_workloads,
)
from tests.python.fixture_parity_support import case_pattern

MODULE_BOUNDARY_MANIFEST_PATH = BENCHMARK_WORKLOADS_ROOT / "module_boundary.py"
COLLECTION_REPLACEMENT_MANIFEST_PATH = (
    BENCHMARK_WORKLOADS_ROOT / "collection_replacement_boundary.py"
)

_VERBOSE_REGRESSION_PATTERN = (
    r"^ (?P<key>[A-Z_]+) \s* = \s* (?:[A-Z]{2,4}+|\d{2,3}) $"
)
_VERBOSE_REGRESSION_FLAGS = int(re.VERBOSE | re.MULTILINE)


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
        freeze_signature_value(list(case.args)),
        case.use_compiled_pattern,
        case.flags or 0,
        case_text_model,
    )


def _collection_replacement_compiled_pattern_success_workload_args(
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
        "unexpected collection/replacement compiled-pattern success workload "
        f"operation {workload.operation!r}"
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
        freeze_signature_value(
            list(_collection_replacement_compiled_pattern_success_workload_args(workload))
        ),
        workload.use_compiled_pattern,
        workload.flags,
        workload.text_model,
    )


def _is_collection_replacement_compiled_pattern_success_workload(
    workload: Any,
) -> bool:
    return (
        getattr(workload, "haystack_text_model", None) is None
        and not workload.kwargs
        and workload.use_compiled_pattern
        and workload.operation
        in {
            "module.split",
            "module.findall",
            "module.finditer",
            "module.sub",
            "module.subn",
        }
        and workload.expected_exception is None
        and workload.pattern == "abc"
    )


def _module_workflow_compiled_pattern_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or case.kwargs or not case.use_compiled_pattern:
        return None
    if case.helper not in {"search", "match", "fullmatch"}:
        return None
    if not case.args:
        return None
    case_text_model = case.text_model or "str"
    return (
        f"module.{case.helper}",
        case_pattern(case),
        freeze_signature_value(list(case.args)),
        case.use_compiled_pattern,
        case.flags or 0,
        case_text_model,
    )


def _module_workflow_compiled_pattern_workload_args(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_module_workflow_compiled_pattern_workload(workload):
        raise AssertionError(
            "unexpected module-workflow compiled-pattern workload "
            f"{workload.workload_id!r}"
        )
    return (workload.haystack_payload(),)


def _module_workflow_compiled_pattern_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_module_workflow_compiled_pattern_workload(workload):
        raise AssertionError(
            "unexpected module-workflow compiled-pattern workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        freeze_signature_value(list(_module_workflow_compiled_pattern_workload_args(workload))),
        workload.use_compiled_pattern,
        workload.flags,
        workload.text_model,
    )


def _is_module_workflow_compiled_pattern_workload(workload: Any) -> bool:
    return (
        not workload.kwargs
        and workload.use_compiled_pattern
        and workload.operation in {"module.search", "module.match", "module.fullmatch"}
    )


def _is_module_workflow_compiled_pattern_literal_success_workload(
    workload: Any,
) -> bool:
    return (
        _is_module_workflow_compiled_pattern_workload(workload)
        and getattr(workload, "haystack_text_model", None) is None
        and workload.expected_exception is None
        and workload.pattern == "abc"
    )


def _is_module_workflow_compiled_pattern_bounded_wildcard_success_workload(
    workload: Any,
) -> bool:
    return (
        _is_module_workflow_compiled_pattern_workload(workload)
        and getattr(workload, "haystack_text_model", None) is None
        and workload.expected_exception is None
        and workload.pattern == "a.c"
        and workload.text_model in {"str", "bytes"}
    )


def _is_module_workflow_compiled_pattern_verbose_bytes_success_workload(
    workload: Any,
) -> bool:
    return (
        _is_module_workflow_compiled_pattern_workload(workload)
        and getattr(workload, "haystack_text_model", None) is None
        and workload.expected_exception is None
        and workload.pattern == _VERBOSE_REGRESSION_PATTERN
        and workload.flags == _VERBOSE_REGRESSION_FLAGS
        and workload.text_model == "bytes"
    )


_COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS = frozenset(
    {
        "manifest_id",
        "workload_id",
        "warmup_iterations",
        "sample_iterations",
        "timed_samples",
        "notes",
        "smoke",
    }
)
_COMPILED_PATTERN_MODULE_SUCCESS_CONTRACT_EXCLUDED_FIELDS = (
    _COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS
    | {
        "categories",
        "syntax_features",
        "expected_exception",
        "haystack_text_model",
    }
)


@dataclass(frozen=True, slots=True)
class CompiledPatternModuleSuccessOwnerSpec:
    case_id: str
    manifest_path: pathlib.Path
    include_workload_selectors: tuple[Callable[[Any], bool], ...]
    contract_manifest_id: str
    contract_filename: str
    note_surface: str
    expected_source_workload_ids: tuple[str, ...]
    preserved_payload_fields: tuple[str, ...]
    preserve_replacement_payload_typing: bool

    def contract_builder_spec(self) -> _SourceTreeContractBuilderSpec:
        return _SourceTreeContractBuilderSpec(
            manifest_id=self.contract_manifest_id,
            excluded_fields=_COMPILED_PATTERN_MODULE_SUCCESS_CONTRACT_EXCLUDED_FIELDS,
            timing_scope="module-helper-call",
            notes=(
                "Ensures benchmark manifests keep the bounded "
                "compiled-pattern-first-argument successful "
                f"{self.note_surface} rows unresolved until helper invocation.",
            ),
        )

    def source_workloads(self) -> tuple[Workload, ...]:
        return _contract_source_workloads(
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
        return _compiled_pattern_contract_expected_build_calls(
            source_workload,
            label=f"{self.case_id} success",
        )

    def expected_callback_result(self, source_workload: Workload) -> object:
        return _compiled_pattern_module_helper_route(
            source_workload,
            collection_replacement_callback_flags=source_workload.flags,
        ).callback_result

    def expected_callback_call(
        self,
        source_workload: Workload,
    ) -> tuple[object, ...]:
        return _compiled_pattern_module_helper_route(
            source_workload,
            collection_replacement_callback_flags=source_workload.flags,
        ).callback_call


_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC = (
    CompiledPatternModuleSuccessOwnerSpec(
        case_id="collection-replacement",
        manifest_path=COLLECTION_REPLACEMENT_MANIFEST_PATH,
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
        manifest_path=MODULE_BOUNDARY_MANIFEST_PATH,
        include_workload_selectors=(
            _is_module_workflow_compiled_pattern_literal_success_workload,
            _is_module_workflow_compiled_pattern_bounded_wildcard_success_workload,
            _is_module_workflow_compiled_pattern_verbose_bytes_success_workload,
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


def _assert_compiled_pattern_module_success_payload_round_trip(
    source_workload: Workload,
    payload: dict[str, object],
    round_tripped: Workload,
    *,
    owner_spec: CompiledPatternModuleSuccessOwnerSpec,
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


_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS = tuple(
    pytest.param(
        owner_spec,
        source_workload,
        id=f"{owner_spec.case_id}-{source_workload.workload_id}",
    )
    for owner_spec in _COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS
    for source_workload in owner_spec.source_workloads()
)
