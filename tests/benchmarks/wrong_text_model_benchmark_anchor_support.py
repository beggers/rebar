from __future__ import annotations

from typing import Any

from tests.benchmarks.source_tree_benchmark_anchor_support import (
    freeze_signature_value,
)
from tests.python.fixture_parity_support import case_pattern

_COMPILED_PATTERN_MODULE_HELPER_OPERATIONS = frozenset(
    {"module.search", "module.match", "module.fullmatch"}
)
_PATTERN_BOUNDARY_OPERATIONS = frozenset(
    {"pattern.search", "pattern.match", "pattern.fullmatch"}
)


def _is_module_workflow_compiled_pattern_workload(workload: Any) -> bool:
    return (
        not workload.kwargs
        and workload.use_compiled_pattern
        and workload.operation in _COMPILED_PATTERN_MODULE_HELPER_OPERATIONS
    )


def _is_module_workflow_compiled_pattern_wrong_text_model_workload(
    workload: Any,
) -> bool:
    return (
        _is_module_workflow_compiled_pattern_workload(workload)
        and getattr(workload, "haystack_text_model", None) is not None
        and workload.expected_exception is not None
        and workload.expected_exception.get("type") == "TypeError"
    )


def _pattern_boundary_wrong_text_model_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "pattern_call" or case.kwargs:
        return None
    if case.helper not in {"search", "match", "fullmatch"}:
        return None
    case_args = list(case.args)
    if len(case_args) != 1:
        return None
    haystack = case_args[0]
    case_text_model = case.text_model or "str"
    if case_text_model == "str" and not isinstance(haystack, bytes):
        return None
    if case_text_model == "bytes" and not isinstance(haystack, str):
        return None
    return (
        f"pattern.{case.helper}",
        case_pattern(case),
        freeze_signature_value(case_args),
        (),
        case.flags or 0,
        case_text_model,
    )


def _pattern_boundary_wrong_text_model_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_pattern_boundary_wrong_text_model_workload(workload):
        raise AssertionError(
            "unexpected pattern-boundary wrong-text-model workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        freeze_signature_value([workload.haystack_payload()]),
        (),
        workload.flags,
        workload.text_model,
    )


def _is_pattern_boundary_wrong_text_model_workload(workload: Any) -> bool:
    return (
        getattr(workload, "haystack_text_model", None) is not None
        and not workload.use_compiled_pattern
        and workload.operation in _PATTERN_BOUNDARY_OPERATIONS
        and workload.pos is None
        and workload.endpos is None
        and not workload.kwargs
        and workload.expected_exception is not None
        and workload.expected_exception.get("type") == "TypeError"
    )
