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
    _is_collection_replacement_pattern_wrong_text_model_workload,
    _is_collection_replacement_wrong_text_model_workload,
)
from tests.benchmarks.compiled_pattern_module_helper_benchmark_support import (
    _compiled_pattern_module_helper_route,
    _run_cpython_compiled_pattern_module_helper_workload,
)
from tests.benchmarks.compiled_pattern_contract_benchmark_support import (
    COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS,
)
from tests.benchmarks.source_tree_contract_benchmark_support import (
    _SourceTreeContractBuilderSpec,
    _contract_source_workloads,
)
from tests.benchmarks.wrong_text_model_benchmark_anchor_support import (
    _is_module_workflow_compiled_pattern_wrong_text_model_workload,
    _is_pattern_boundary_wrong_text_model_workload,
)

MODULE_BOUNDARY_MANIFEST_PATH = BENCHMARK_WORKLOADS_ROOT / "module_boundary.py"
PATTERN_BOUNDARY_MANIFEST_PATH = BENCHMARK_WORKLOADS_ROOT / "pattern_boundary.py"
COLLECTION_REPLACEMENT_MANIFEST_PATH = (
    BENCHMARK_WORKLOADS_ROOT / "collection_replacement_boundary.py"
)

_WRONG_TEXT_MODEL_PATTERN_CONTRACT_EXCLUDED_FIELDS = frozenset(
    {
        "manifest_id",
        "workload_id",
        "warmup_iterations",
        "sample_iterations",
        "timed_samples",
        "smoke",
    }
)

@dataclass(frozen=True, slots=True)
class WrongTextModelOwnerSpec:
    case_id: str
    manifest_path: pathlib.Path
    include_workload_selectors: tuple[Callable[[Any], bool], ...]
    contract_manifest_id: str
    contract_filename_stem: str
    expected_source_workload_ids: tuple[str, ...]
    use_compiled_pattern: bool
    timing_scope: str
    excluded_fields: frozenset[str]
    note_surface: str | None
    direct_pattern_route: str | None

    def contract_builder_spec(self) -> _SourceTreeContractBuilderSpec:
        notes: tuple[str, ...] = ()
        if self.note_surface is not None:
            notes = (
                "Ensures benchmark manifests keep the bounded "
                "compiled-pattern-first-argument wrong-text-model "
                f"{self.note_surface} rows unresolved until helper invocation.",
            )
        return _SourceTreeContractBuilderSpec(
            manifest_id=self.contract_manifest_id,
            excluded_fields=self.excluded_fields,
            timing_scope=self.timing_scope,
            notes=notes,
        )

    def source_workloads(self) -> tuple[Workload, ...]:
        return _contract_source_workloads(
            manifest_path=self.manifest_path,
            include_workload_selectors=self.include_workload_selectors,
            expected_source_workload_ids=self.expected_source_workload_ids,
            drift_message=(
                "wrong-text-model contract source workloads drifted from the "
                f"{self.case_id} owner-spec surface"
            ),
        )


_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_OWNER_SPEC = WrongTextModelOwnerSpec(
    case_id="pattern_helper_collection_replacement_wrong_text_model",
    manifest_path=COLLECTION_REPLACEMENT_MANIFEST_PATH,
    include_workload_selectors=(
        _is_collection_replacement_pattern_wrong_text_model_workload,
    ),
    contract_manifest_id="collection-replacement-boundary",
    contract_filename_stem="pattern_collection_replacement_wrong_text_model",
    expected_source_workload_ids=(
        "pattern-split-on-bytes-string-warm-str",
        "pattern-sub-on-bytes-string-warm-str",
        "pattern-subn-on-str-string-purged-bytes",
    ),
    use_compiled_pattern=False,
    timing_scope="pattern-helper-call",
    excluded_fields=_WRONG_TEXT_MODEL_PATTERN_CONTRACT_EXCLUDED_FIELDS,
    note_surface=None,
    direct_pattern_route="collection/replacement",
)

_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_OWNER_SPEC = WrongTextModelOwnerSpec(
    case_id="pattern_boundary_wrong_text_model",
    manifest_path=PATTERN_BOUNDARY_MANIFEST_PATH,
    include_workload_selectors=(
        _is_pattern_boundary_wrong_text_model_workload,
    ),
    contract_manifest_id="pattern-boundary",
    contract_filename_stem="pattern_boundary_wrong_text_model",
    expected_source_workload_ids=(
        "pattern-search-on-bytes-string-warm-str",
        "pattern-match-on-str-string-purged-bytes",
        "pattern-fullmatch-on-bytes-string-warm-str",
    ),
    use_compiled_pattern=False,
    timing_scope="pattern-helper-call",
    excluded_fields=_WRONG_TEXT_MODEL_PATTERN_CONTRACT_EXCLUDED_FIELDS,
    note_surface=None,
    direct_pattern_route="pattern-boundary",
)

_COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_OWNER_SPEC = (
    WrongTextModelOwnerSpec(
        case_id="compiled_pattern_module_helper_wrong_text_model",
        manifest_path=COLLECTION_REPLACEMENT_MANIFEST_PATH,
        include_workload_selectors=(
            _is_collection_replacement_wrong_text_model_workload,
        ),
        contract_manifest_id="collection-replacement-boundary",
        contract_filename_stem=(
            "compiled_pattern_collection_replacement_wrong_text_model"
        ),
        expected_source_workload_ids=(
            "module-split-on-bytes-string-purged-str-compiled-pattern",
            "module-findall-on-str-string-purged-bytes-compiled-pattern",
            "module-finditer-on-bytes-string-warm-str-compiled-pattern",
            "module-sub-on-bytes-string-warm-str-compiled-pattern",
            "module-subn-on-str-string-purged-bytes-compiled-pattern",
        ),
        use_compiled_pattern=True,
        timing_scope="module-helper-call",
        excluded_fields=COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS,
        note_surface="collection/replacement",
        direct_pattern_route=None,
    )
)

_COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_OWNER_SPEC = (
    WrongTextModelOwnerSpec(
        case_id="compiled_pattern_module_boundary_wrong_text_model",
        manifest_path=MODULE_BOUNDARY_MANIFEST_PATH,
        include_workload_selectors=(
            _is_module_workflow_compiled_pattern_wrong_text_model_workload,
        ),
        contract_manifest_id="module-boundary",
        contract_filename_stem="compiled_pattern_module_boundary_wrong_text_model",
        expected_source_workload_ids=(
            "module-search-on-bytes-string-warm-str-compiled-pattern",
            "module-match-on-str-string-purged-bytes-compiled-pattern",
            "module-fullmatch-on-bytes-string-warm-str-compiled-pattern",
        ),
        use_compiled_pattern=True,
        timing_scope="module-helper-call",
        excluded_fields=COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS,
        note_surface="module-boundary",
        direct_pattern_route=None,
    )
)

WRONG_TEXT_MODEL_OWNER_SPECS = (
    _PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_OWNER_SPEC,
    _PATTERN_BOUNDARY_WRONG_TEXT_MODEL_OWNER_SPEC,
    _COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_OWNER_SPEC,
    _COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_OWNER_SPEC,
)

_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_PARAMS = tuple(
    pytest.param(
        owner_spec,
        source_workload,
        id=f"{owner_spec.case_id}-{source_workload.workload_id}",
    )
    for owner_spec in WRONG_TEXT_MODEL_OWNER_SPECS
    for source_workload in owner_spec.source_workloads()
)


def _wrong_text_model_expected_callback_result(
    source_workload: Workload,
    *,
    use_compiled_pattern: bool,
    direct_pattern_route: str | None,
) -> object:
    if use_compiled_pattern:
        return _compiled_pattern_module_helper_route(
            source_workload,
            collection_replacement_callback_flags=0,
        ).callback_result

    route = _direct_pattern_route_label(direct_pattern_route)
    if route == "collection/replacement":
        if source_workload.operation == "pattern.subn":
            return ("pattern-result", 0)
        if source_workload.operation in {"pattern.split", "pattern.sub"}:
            return "pattern-result"
    elif route == "pattern-boundary" and source_workload.operation in {
        "pattern.search",
        "pattern.match",
        "pattern.fullmatch",
    }:
        return "pattern-result"
    raise AssertionError(
        "unexpected direct Pattern "
        f"{route} wrong-text-model workload operation "
        f"{source_workload.operation!r}"
    )


def _wrong_text_model_expected_build_calls(
    source_workload: Workload,
    *,
    use_compiled_pattern: bool,
    direct_pattern_route: str | None,
) -> list[tuple[object, ...]]:
    compile_call = (
        "compile",
        source_workload.pattern_payload(),
        source_workload.flags,
    )
    if source_workload.cache_mode not in {"warm", "purged"}:
        if use_compiled_pattern:
            raise AssertionError(
                "unexpected compiled-pattern module helper wrong-text-model "
                f"workload cache mode {source_workload.cache_mode!r}"
            )
        route = _direct_pattern_route_label(direct_pattern_route)
        raise AssertionError(
            "unexpected direct Pattern "
            f"{route} wrong-text-model cache mode "
            f"{source_workload.cache_mode!r}"
        )
    if source_workload.cache_mode == "warm":
        return [compile_call]
    return [compile_call, ("purge",)]


def _wrong_text_model_expected_callback_call(
    source_workload: Workload,
    *,
    use_compiled_pattern: bool,
    direct_pattern_route: str | None,
) -> tuple[object, ...]:
    if use_compiled_pattern:
        return _compiled_pattern_module_helper_route(
            source_workload,
            collection_replacement_callback_flags=0,
        ).callback_call

    route = _direct_pattern_route_label(direct_pattern_route)
    if route == "collection/replacement":
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
    elif route == "pattern-boundary" and source_workload.operation in {
        "pattern.search",
        "pattern.match",
        "pattern.fullmatch",
    }:
        return (
            source_workload.operation,
            source_workload.haystack_payload(),
            (),
            {},
        )
    raise AssertionError(
        "unexpected direct Pattern "
        f"{route} wrong-text-model workload operation "
        f"{source_workload.operation!r}"
    )


def _run_cpython_wrong_text_model_workload(
    workload: Workload,
    *,
    use_compiled_pattern: bool,
    direct_pattern_route: str | None,
) -> object:
    if use_compiled_pattern:
        return _run_cpython_compiled_pattern_module_helper_workload(
            workload,
            collection_replacement_callback_flags=0,
        )

    route = _direct_pattern_route_label(direct_pattern_route)
    helper_name = workload.operation.removeprefix("pattern.")
    compiled_pattern = re.compile(workload.pattern_payload(), workload.flags)

    if route == "collection/replacement":
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
    elif route == "pattern-boundary" and workload.operation in {
        "pattern.search",
        "pattern.match",
        "pattern.fullmatch",
    }:
        return getattr(compiled_pattern, helper_name)(workload.haystack_payload())

    raise AssertionError(
        "unexpected direct Pattern "
        f"{route} wrong-text-model workload operation "
        f"{workload.operation!r}"
    )


def _assert_wrong_text_model_payload_round_trip(
    source_workload: Workload,
    payload: dict[str, object],
    round_tripped: Workload,
    *,
    use_compiled_pattern: bool,
    timing_scope: str,
) -> None:
    expected_text_type = str if source_workload.text_model == "str" else bytes
    expected_haystack_type = (
        str if source_workload.haystack_text_model == "str" else bytes
    )

    if use_compiled_pattern:
        assert payload["use_compiled_pattern"] is True
    else:
        assert payload.get("use_compiled_pattern") is None
    assert round_tripped.use_compiled_pattern is use_compiled_pattern
    assert payload["timing_scope"] == timing_scope
    assert round_tripped.timing_scope == timing_scope
    assert payload["haystack_text_model"] == source_workload.haystack_text_model
    assert round_tripped.haystack_text_model == source_workload.haystack_text_model
    assert payload["expected_exception"] == source_workload.expected_exception
    assert round_tripped.expected_exception == source_workload.expected_exception
    assert isinstance(round_tripped.pattern_payload(), expected_text_type)
    assert isinstance(round_tripped.haystack_payload(), expected_haystack_type)
    if source_workload.replacement is not None:
        assert isinstance(round_tripped.replacement_payload(), expected_text_type)


def _direct_pattern_route_label(direct_pattern_route: str | None) -> str:
    if direct_pattern_route is None:
        raise AssertionError("missing direct Pattern wrong-text-model route")
    return direct_pattern_route
