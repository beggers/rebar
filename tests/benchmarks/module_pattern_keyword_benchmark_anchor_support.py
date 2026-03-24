from __future__ import annotations

from typing import Any

from tests.benchmarks.collection_replacement_benchmark_anchor_support import (
    _is_encoded_indexlike_payload,
)
from tests.benchmarks.source_tree_benchmark_anchor_support import (
    freeze_signature_value,
)
from tests.python.fixture_parity_support import (
    case_pattern,
    module_workflow_keyword_kwargs_signature,
    module_workflow_positional_args_signature,
)


def _module_workflow_keyword_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or not case.kwargs:
        return None
    if case.use_compiled_pattern or case.helper not in {"search", "match", "fullmatch"}:
        return None
    return (
        f"module.{case.helper}",
        case_pattern(case),
        freeze_signature_value(list(case.args)),
        module_workflow_keyword_kwargs_signature(case.kwargs),
        case.flags or 0,
        case.text_model or "str",
    )


def _module_workflow_keyword_workload_args(
    workload: Any,
) -> tuple[Any, ...]:
    if not (
        _is_module_workflow_keyword_flags_workload(workload)
        or _is_module_workflow_keyword_error_workload(workload)
    ):
        raise AssertionError(
            "unexpected module-workflow keyword workload "
            f"{workload.workload_id!r}"
        )
    args: list[object] = [workload.haystack_payload()]
    if (
        workload.operation == "module.search"
        and workload.expected_exception is not None
        and "flags" in workload.kwargs
    ):
        args.append(workload.flags)
    return tuple(args)


def _module_workflow_keyword_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not (
        _is_module_workflow_keyword_flags_workload(workload)
        or _is_module_workflow_keyword_error_workload(workload)
    ):
        raise AssertionError(
            "unexpected module-workflow keyword workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        freeze_signature_value(list(_module_workflow_keyword_workload_args(workload))),
        module_workflow_keyword_kwargs_signature(workload.kwargs),
        workload.flags,
        workload.text_model,
    )


def _is_module_workflow_keyword_flags_workload(workload: Any) -> bool:
    keyword_names = tuple(workload.kwargs)
    return (
        workload.operation in {"module.search", "module.match", "module.fullmatch"}
        and bool(workload.kwargs)
        and len(keyword_names) == 1
        and keyword_names[0] == "flags"
        and workload.expected_exception is None
        and not workload.use_compiled_pattern
    )


def _is_module_workflow_keyword_error_workload(workload: Any) -> bool:
    keyword_names = tuple(workload.kwargs)
    expected_exception = workload.expected_exception
    if (
        workload.operation
        not in {"module.search", "module.match", "module.fullmatch"}
        or not workload.kwargs
        or len(keyword_names) != 1
        or expected_exception is None
        or expected_exception.get("type") != "TypeError"
        or workload.use_compiled_pattern
    ):
        return False
    message = expected_exception.get("message_substring", "")
    if keyword_names[0] == "flags":
        return "multiple values for argument" in message
    if keyword_names[0] == "missing":
        return "unexpected keyword argument" in message
    return False


def _pattern_window_positional_indexlike_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "pattern_call" or case.kwargs:
        return None
    if case.helper not in {"search", "match", "fullmatch", "findall", "finditer"}:
        return None
    if not any(hasattr(argument, "__index__") for argument in case.args):
        return None
    return (
        case.helper,
        case_pattern(case),
        module_workflow_positional_args_signature(case.args),
        case.text_model or "str",
    )


def _pattern_window_positional_indexlike_workload_args(
    workload: Any,
) -> tuple[object, ...]:
    if workload.operation not in {
        "pattern.search",
        "pattern.match",
        "pattern.fullmatch",
        "pattern.findall",
        "pattern.finditer",
    }:
        raise AssertionError(
            "unexpected pattern positional-indexlike workload operation "
            f"{workload.operation!r}"
        )

    args: list[object] = [workload.haystack_payload()]
    if workload.pos is not None or workload.endpos is not None:
        args.append(0 if workload.pos is None else workload.pos)
    if workload.endpos is not None:
        args.append(workload.endpos)
    return tuple(args)


def _pattern_window_positional_indexlike_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_pattern_window_positional_indexlike_workload(workload):
        raise AssertionError(
            "unexpected pattern positional-indexlike workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation.removeprefix("pattern."),
        workload.pattern_payload(),
        module_workflow_positional_args_signature(
            _pattern_window_positional_indexlike_workload_args(workload)
        ),
        workload.text_model,
    )


def _is_pattern_window_positional_indexlike_workload(workload: Any) -> bool:
    categories = set(workload.categories)
    return (
        workload.operation in {
            "pattern.search",
            "pattern.match",
            "pattern.fullmatch",
            "pattern.findall",
            "pattern.finditer",
        }
        and workload.expected_exception is None
        and not workload.kwargs
        and {"positional-window", "indexlike"}.issubset(categories)
        and (
            _is_encoded_indexlike_payload(workload.pos)
            or _is_encoded_indexlike_payload(workload.endpos)
        )
    )


def _pattern_keyword_window_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "pattern_call" or not case.kwargs:
        return None
    if case.helper not in {"search", "match", "fullmatch", "findall", "finditer"}:
        return None
    return (
        f"pattern.{case.helper}",
        case_pattern(case),
        freeze_signature_value(list(case.args)),
        module_workflow_keyword_kwargs_signature(case.kwargs),
        case.flags or 0,
        case.text_model or "str",
    )


def _pattern_keyword_window_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_pattern_keyword_window_workload(workload):
        raise AssertionError(
            "unexpected pattern keyword-window workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        freeze_signature_value([workload.haystack_payload()]),
        module_workflow_keyword_kwargs_signature(workload.kwargs),
        workload.flags,
        workload.text_model,
    )


def _is_pattern_keyword_window_workload(workload: Any) -> bool:
    categories = set(workload.categories)
    return (
        workload.operation in {
            "pattern.search",
            "pattern.match",
            "pattern.fullmatch",
            "pattern.findall",
            "pattern.finditer",
        }
        and workload.expected_exception is None
        and workload.pos is None
        and workload.endpos is None
        and bool(workload.kwargs)
        and set(workload.kwargs).issubset({"pos", "endpos"})
        and "keyword" in categories
    )
