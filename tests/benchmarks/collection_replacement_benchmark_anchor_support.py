from __future__ import annotations

from typing import Any

from rebar_harness import benchmarks
from tests.benchmarks.source_tree_benchmark_anchor_support import (
    freeze_signature_value,
)
from tests.python.fixture_parity_support import (
    case_pattern,
    module_workflow_keyword_kwargs_signature,
    module_workflow_positional_args_signature,
)

_COLLECTION_REPLACEMENT_SPLIT_OPERATIONS = frozenset(
    {"module.split", "pattern.split"}
)
_COLLECTION_REPLACEMENT_SUBSTITUTE_OPERATIONS = frozenset(
    {"module.sub", "module.subn", "pattern.sub", "pattern.subn"}
)


def _is_encoded_indexlike_payload(value: object) -> bool:
    return (
        isinstance(value, dict)
        and value.get("type") == "indexlike"
        and isinstance(value.get("value"), int)
        and not isinstance(value.get("value"), bool)
    )


def _collection_replacement_keyword_parameter_name(
    workload: Any,
) -> str | None:
    if workload.operation in _COLLECTION_REPLACEMENT_SPLIT_OPERATIONS:
        return "maxsplit"
    if workload.operation in _COLLECTION_REPLACEMENT_SUBSTITUTE_OPERATIONS:
        return "count"
    return None


def _collection_replacement_has_expected_unexpected_keyword_error(
    workload: Any,
) -> bool:
    keyword_names = tuple(workload.kwargs)
    if len(keyword_names) != 1:
        return False
    keyword_name = keyword_names[0]
    expected_keyword_parameter = _collection_replacement_keyword_parameter_name(workload)
    if keyword_name == expected_keyword_parameter:
        return False
    expected_exception = workload.expected_exception
    if expected_exception is None or expected_exception.get("type") != "TypeError":
        return False
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
        and _is_encoded_indexlike_payload(parameter_payload)
    )


def _collection_replacement_expected_keyword_field(
    workload: Any,
) -> str | None:
    if workload.operation.startswith("module."):
        return (
            benchmarks._expected_duplicate_module_helper_keyword_field(workload)
            or benchmarks._expected_positional_module_helper_keyword_field(workload)
        )
    if workload.operation.startswith("pattern."):
        return benchmarks._expected_pattern_helper_positional_keyword_field(workload)
    return None


def _collection_replacement_positional_keyword_field(
    workload: Any,
) -> str | None:
    expected_keyword_field = _collection_replacement_expected_keyword_field(workload)
    if expected_keyword_field is None:
        return None
    keyword_parameter = _collection_replacement_keyword_parameter_name(workload)
    if expected_keyword_field != keyword_parameter:
        return None
    return expected_keyword_field


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
        freeze_signature_value(list(case.args)),
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
        freeze_signature_value(
            list(_collection_replacement_keyword_workload_args(workload))
        ),
        module_workflow_keyword_kwargs_signature(workload.kwargs),
        workload.use_compiled_pattern,
        workload.flags,
        workload.text_model,
    )


def _is_collection_replacement_keyword_workload(workload: Any) -> bool:
    keyword_parameter = _collection_replacement_keyword_parameter_name(workload)
    if keyword_parameter is None or not workload.kwargs:
        return False
    keyword_names = tuple(workload.kwargs)
    if len(keyword_names) != 1:
        return False
    if keyword_names[0] == keyword_parameter:
        return True
    if _collection_replacement_expected_keyword_field(workload) is not None:
        return True
    return _collection_replacement_has_expected_unexpected_keyword_error(workload)
