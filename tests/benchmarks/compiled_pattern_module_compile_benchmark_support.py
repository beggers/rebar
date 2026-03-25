from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from functools import cache, partial
import pathlib
import re
from typing import Any

import pytest

from rebar_harness.benchmarks import (
    BENCHMARK_WORKLOADS_ROOT,
    Workload,
)
from tests.benchmarks.source_tree_contract_benchmark_support import (
    COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS,
    _SourceTreeContractBuilderSpec,
    _contract_source_workloads,
    compiled_pattern_contract_expected_build_calls,
)
from tests.benchmarks.benchmark_test_support import (
    StandardBenchmarkAnchorContractDefinition,
    _definition_anchor_expectations,
    _workload_case_pair_anchor_expectations,
    published_case_ids_by_signature,
)
from tests.python.fixture_parity_support import case_pattern

MODULE_BOUNDARY_MANIFEST_PATH = BENCHMARK_WORKLOADS_ROOT / "module_boundary.py"

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


def _compiled_pattern_module_compile_keyword_kwargs_signature(
    kwargs: dict[str, object],
) -> tuple[tuple[str, str, object], ...]:
    signature: list[tuple[str, str, object]] = []
    for name, value in sorted(kwargs.items()):
        if isinstance(value, bool):
            signature.append((name, "bool", value))
            continue
        if isinstance(value, re.RegexFlag) and int(value) == 0:
            signature.append((name, "noflag", 0))
            continue
        if isinstance(value, int):
            signature.append((name, "int", int(value)))
            continue
        signature.append((name, type(value).__name__, repr(value)))
    return tuple(signature)


def _module_workflow_compiled_pattern_compile_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or case.kwargs or not case.use_compiled_pattern:
        return None
    if case.helper != "compile" or case.args:
        return None
    case_text_model = case.text_model or "str"
    return (
        "module.compile",
        case_pattern(case),
        (),
        case.use_compiled_pattern,
        case.flags or 0,
        case_text_model,
    )


def _module_workflow_compiled_pattern_compile_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_module_workflow_compiled_pattern_compile_workload(workload):
        raise AssertionError(
            "unexpected module-workflow compiled-pattern module.compile workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        (),
        workload.use_compiled_pattern,
        workload.flags,
        workload.text_model,
    )


def _is_module_workflow_compiled_pattern_compile_workload(workload: Any) -> bool:
    return (
        not workload.kwargs
        and workload.use_compiled_pattern
        and workload.operation == "module.compile"
    )


def _is_module_workflow_compiled_pattern_compile_success_workload(
    workload: Any,
    *,
    allowed_patterns: tuple[str, ...],
) -> bool:
    return (
        _is_module_workflow_compiled_pattern_compile_workload(workload)
        and workload.expected_exception is None
        and workload.pattern in allowed_patterns
        and workload.flags == 0
    )


def _workload_matches_expected_exception(
    workload: Any,
    *,
    expected_exception: dict[str, str] | None,
) -> bool:
    if expected_exception is None:
        return workload.expected_exception is None
    return workload.expected_exception == expected_exception


def _module_workflow_compiled_pattern_compile_keyword_correctness_case_signature(
    case: Any,
    *,
    keyword_signature: tuple[tuple[str, str, object], ...],
    allowed_patterns: tuple[str, ...],
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or not case.use_compiled_pattern:
        return None
    if case.helper != "compile" or case.args:
        return None
    if (
        _compiled_pattern_module_compile_keyword_kwargs_signature(case.kwargs)
        != keyword_signature
    ):
        return None
    if case.pattern not in allowed_patterns:
        return None
    case_text_model = case.text_model or "str"
    return (
        "module.compile",
        case_pattern(case),
        (),
        keyword_signature,
        case.use_compiled_pattern,
        case.flags or 0,
        case_text_model,
    )


def _module_workflow_compiled_pattern_compile_keyword_workload_signature(
    workload: Any,
    *,
    keyword_label: str,
    keyword_signature: tuple[tuple[str, str, object], ...],
    allowed_patterns: tuple[str, ...],
    expected_exception: dict[str, str] | None = None,
) -> tuple[Any, ...]:
    if not _is_module_workflow_compiled_pattern_compile_keyword_workload(
        workload,
        keyword_signature=keyword_signature,
        allowed_patterns=allowed_patterns,
        expected_exception=expected_exception,
    ):
        raise AssertionError(
            "unexpected module-workflow compiled-pattern module.compile "
            f"{keyword_label} keyword workload {workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        (),
        keyword_signature,
        workload.use_compiled_pattern,
        workload.flags,
        workload.text_model,
    )


def _is_module_workflow_compiled_pattern_compile_keyword_workload(
    workload: Any,
    *,
    keyword_signature: tuple[tuple[str, str, object], ...],
    allowed_patterns: tuple[str, ...],
    expected_exception: dict[str, str] | None = None,
) -> bool:
    return (
        workload.use_compiled_pattern
        and workload.operation == "module.compile"
        and _workload_matches_expected_exception(
            workload,
            expected_exception=expected_exception,
        )
        and workload.pattern in allowed_patterns
        and workload.flags == 0
        and _compiled_pattern_module_compile_keyword_kwargs_signature(workload.kwargs)
        == keyword_signature
    )


def _compiled_pattern_module_compile_keyword_signature(
    contract_case: CompiledPatternModuleCompileContractCase,
) -> tuple[tuple[str, str, object], ...]:
    if contract_case.keyword_signature is None:
        raise AssertionError(
            "missing compiled-pattern module.compile keyword signature for "
            f"{contract_case.case_id!r}"
        )
    return contract_case.keyword_signature


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
    contract_case: CompiledPatternModuleCompileContractCase,
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
    contract_case: CompiledPatternModuleCompileContractCase,
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


def _compiled_pattern_module_compile_keyword_correctness_case_signature(
    contract_case: CompiledPatternModuleCompileContractCase,
    case: Any,
) -> tuple[Any, ...] | None:
    return _module_workflow_compiled_pattern_compile_keyword_correctness_case_signature(
        case,
        keyword_signature=_compiled_pattern_module_compile_keyword_signature(
            contract_case
        ),
        allowed_patterns=contract_case.allowed_patterns,
    )


def _compiled_pattern_module_compile_keyword_workload_signature(
    contract_case: CompiledPatternModuleCompileContractCase,
    workload: Any,
) -> tuple[Any, ...]:
    return _module_workflow_compiled_pattern_compile_keyword_workload_signature(
        workload,
        keyword_label=contract_case.case_id,
        keyword_signature=_compiled_pattern_module_compile_keyword_signature(
            contract_case
        ),
        allowed_patterns=contract_case.allowed_patterns,
        expected_exception=contract_case.expected_exception,
    )


def _is_compiled_pattern_module_compile_keyword_workload(
    contract_case: CompiledPatternModuleCompileContractCase,
    workload: Any,
) -> bool:
    return _is_module_workflow_compiled_pattern_compile_keyword_workload(
        workload,
        keyword_signature=_compiled_pattern_module_compile_keyword_signature(
            contract_case
        ),
        allowed_patterns=contract_case.allowed_patterns,
        expected_exception=contract_case.expected_exception,
    )


def _run_cpython_compiled_pattern_module_compile_keyword_workload(
    contract_case: CompiledPatternModuleCompileContractCase,
    workload: Workload,
) -> object:
    del contract_case
    compiled_pattern = re.compile(workload.pattern_payload(), workload.flags)
    return re.compile(compiled_pattern, **workload.keyword_arguments())


def _compiled_pattern_module_compile_keyword_callback_flags(
    contract_case: CompiledPatternModuleCompileContractCase,
    source_workload: Workload,
) -> object:
    del contract_case
    return source_workload.keyword_arguments()["flags"]


def _compiled_pattern_module_compile_success_correctness_case_signature(
    contract_case: CompiledPatternModuleCompileContractCase,
    case: Any,
) -> tuple[Any, ...] | None:
    del contract_case
    return _module_workflow_compiled_pattern_compile_correctness_case_signature(case)


def _compiled_pattern_module_compile_success_workload_signature(
    contract_case: CompiledPatternModuleCompileContractCase,
    workload: Any,
) -> tuple[Any, ...]:
    del contract_case
    return _module_workflow_compiled_pattern_compile_workload_signature(workload)


def _is_compiled_pattern_module_compile_success_workload(
    contract_case: CompiledPatternModuleCompileContractCase,
    workload: Any,
) -> bool:
    del contract_case
    return _is_module_workflow_compiled_pattern_compile_workload(workload)


def _run_cpython_compiled_pattern_module_compile_success_workload(
    contract_case: CompiledPatternModuleCompileContractCase,
    workload: Workload,
) -> object:
    del contract_case
    compiled_pattern = re.compile(workload.pattern_payload(), workload.flags)
    return re.compile(compiled_pattern, workload.flags)


def _compiled_pattern_module_compile_success_callback_flags(
    contract_case: CompiledPatternModuleCompileContractCase,
    source_workload: Workload,
) -> object:
    del contract_case
    return source_workload.flags


@dataclass(frozen=True, slots=True)
class _CompiledPatternModuleCompileContractRoute:
    surface_label: str
    excluded_fields: frozenset[str]
    note: str
    correctness_case_signature_builder: Callable[
        [CompiledPatternModuleCompileContractCase, Any],
        tuple[Any, ...] | None,
    ]
    workload_signature_builder: Callable[
        [CompiledPatternModuleCompileContractCase, Any],
        tuple[Any, ...],
    ]
    include_workload_selector: Callable[
        [CompiledPatternModuleCompileContractCase, Any],
        bool,
    ]
    payload_round_trip_assertion: Callable[
        [CompiledPatternModuleCompileContractCase, Workload, dict[str, object], Workload],
        None,
    ]
    cpython_dispatch: Callable[
        [CompiledPatternModuleCompileContractCase, Workload],
        object,
    ]
    callback_flags_selector: Callable[
        [CompiledPatternModuleCompileContractCase, Workload],
        object,
    ]

    def drift_message(
        self,
        contract_case: CompiledPatternModuleCompileContractCase,
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

    def contract_builder_spec(self) -> _SourceTreeContractBuilderSpec:
        return _SourceTreeContractBuilderSpec(
            manifest_id="module-boundary",
            excluded_fields=self.manifest_excluded_fields(),
            manifest_timed_samples=2,
            timing_scope="module-helper-call",
            notes=(self.note(),),
        )

    def expected_source_workload_ids(self) -> tuple[str, ...]:
        return tuple(
            workload_id.removesuffix("-contract")
            for workload_id, _case_id in self.expected_anchor_pairs
        )

    def source_workloads(self) -> tuple[Workload, ...]:
        return _contract_source_workloads(
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
        return _workload_case_pair_anchor_expectations(
            manifest_path,
            self.expected_anchor_pairs,
        )

    def expected_build_calls(
        self,
        source_workload: Workload,
    ) -> list[tuple[object, ...]]:
        return self.expected_build_calls_builder(source_workload)


_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_CONTRACT_ROUTE = (
    _CompiledPatternModuleCompileContractRoute(
        surface_label="success",
        excluded_fields=(
            COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS
        ),
        note=(
            "Ensures benchmark manifests keep the bounded compiled-pattern-first-argument "
            "module.compile rows unresolved until helper invocation."
        ),
        correctness_case_signature_builder=(
            _compiled_pattern_module_compile_success_correctness_case_signature
        ),
        workload_signature_builder=(
            _compiled_pattern_module_compile_success_workload_signature
        ),
        include_workload_selector=(
            _is_compiled_pattern_module_compile_success_workload
        ),
        payload_round_trip_assertion=(
            _assert_compiled_pattern_module_compile_success_payload_round_trip
        ),
        cpython_dispatch=(
            _run_cpython_compiled_pattern_module_compile_success_workload
        ),
        callback_flags_selector=(
            _compiled_pattern_module_compile_success_callback_flags
        ),
    )
)

_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CONTRACT_ROUTE = (
    _CompiledPatternModuleCompileContractRoute(
        surface_label="keyword",
        excluded_fields=(
            COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS
            | {"categories", "syntax_features"}
        ),
        note=(
            "Ensures benchmark manifests keep the bounded compiled-pattern-first-argument "
            "module.compile flags= keyword rows unresolved until helper invocation."
        ),
        correctness_case_signature_builder=(
            _compiled_pattern_module_compile_keyword_correctness_case_signature
        ),
        workload_signature_builder=(
            _compiled_pattern_module_compile_keyword_workload_signature
        ),
        include_workload_selector=(
            _is_compiled_pattern_module_compile_keyword_workload
        ),
        payload_round_trip_assertion=(
            _assert_compiled_pattern_module_compile_keyword_payload_round_trip
        ),
        cpython_dispatch=(
            _run_cpython_compiled_pattern_module_compile_keyword_workload
        ),
        callback_flags_selector=(
            _compiled_pattern_module_compile_keyword_callback_flags
        ),
    )
)


@dataclass(frozen=True)
class _CompiledPatternModuleContractAnchorLane:
    case_id: str
    contract_filename: str
    source_workloads: tuple[Workload, ...]
    contract_builder_spec: Callable[[], _SourceTreeContractBuilderSpec]
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
        return _module_workflow_compiled_pattern_compile_keyword_correctness_case_signature(
            case,
            keyword_signature=self.keyword_signature,
            allowed_patterns=self.allowed_patterns,
        )

    def workload_signature(self, workload: Any) -> tuple[Any, ...]:
        return _module_workflow_compiled_pattern_compile_keyword_workload_signature(
            workload,
            keyword_label=self.case_id,
            keyword_signature=self.keyword_signature,
            allowed_patterns=self.allowed_patterns,
            expected_exception=self.expected_exception,
        )

    def includes_workload(self, workload: Any) -> bool:
        return _is_module_workflow_compiled_pattern_compile_keyword_workload(
            workload,
            keyword_signature=self.keyword_signature,
            allowed_patterns=self.allowed_patterns,
            expected_exception=self.expected_exception,
        )

    def expected_anchor_case_ids(self) -> dict[tuple[str, str], tuple[str, ...]]:
        return _definition_anchor_expectations(
            MODULE_BOUNDARY_MANIFEST_PATH,
            dict(self.anchor_expectations),
        )

    def expected_anchor_workload_ids(self) -> tuple[str, ...]:
        return tuple(workload_id for workload_id, _ in self.anchor_expectations)

    def anchor_definition(self) -> StandardBenchmarkAnchorContractDefinition:
        return StandardBenchmarkAnchorContractDefinition(
            name=self.anchor_definition_name,
            manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
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
            manifest_path=MODULE_BOUNDARY_MANIFEST_PATH,
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
        return _module_workflow_compiled_pattern_compile_correctness_case_signature(
            case
        )

    def workload_signature(self, workload: Any) -> tuple[Any, ...]:
        return _module_workflow_compiled_pattern_compile_workload_signature(
            workload
        )

    def includes_workload(self, workload: Any) -> bool:
        return _is_module_workflow_compiled_pattern_compile_success_workload(
            workload,
            allowed_patterns=self.allowed_patterns,
        )

    def expected_anchor_case_ids(self) -> dict[tuple[str, str], tuple[str, ...]]:
        return _definition_anchor_expectations(
            MODULE_BOUNDARY_MANIFEST_PATH,
            dict(self.anchor_expectations),
        )

    def expected_anchor_workload_ids(self) -> tuple[str, ...]:
        return tuple(workload_id for workload_id, _ in self.anchor_expectations)

    def anchor_definition(self) -> StandardBenchmarkAnchorContractDefinition:
        return StandardBenchmarkAnchorContractDefinition(
            name=self.anchor_definition_name,
            manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
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
    return (
        *(
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
        ),
    )


_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS = (
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


_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS = (
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


@cache
def _build_compiled_pattern_module_compile_standard_benchmark_definitions() -> tuple[
    StandardBenchmarkAnchorContractDefinition, ...
]:
    return tuple(
        owner_spec.anchor_definition()
        for owner_spec in (
            *_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS,
            *_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS,
        )
    )


def __getattr__(name: str) -> Any:
    if name == "COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS":
        return _build_compiled_pattern_module_compile_standard_benchmark_definitions()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES = (
    build_compiled_pattern_module_compile_contract_cases(
        manifest_path=MODULE_BOUNDARY_MANIFEST_PATH,
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
        published_case_ids_by_signature=published_case_ids_by_signature,
    )
)
