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


def _collection_replacement_pattern_split_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if workload.operation != "pattern.split":
        raise AssertionError(
            "unexpected collection/replacement pattern split workload operation "
            f"{workload.operation!r}"
        )
    if workload.expected_exception is not None or workload.use_compiled_pattern:
        raise AssertionError(
            "unexpected collection/replacement pattern split workload "
            f"{workload.workload_id!r}"
        )
    if workload.kwargs or workload.pos is not None or workload.endpos is not None:
        raise AssertionError(
            "unexpected collection/replacement pattern split workload shape "
            f"{workload.workload_id!r}"
        )

    args = [workload.haystack_payload()]
    if workload.maxsplit is not None and not (
        type(workload.maxsplit) is int and workload.maxsplit == 0
    ):
        args.append(workload.maxsplit_argument())
    return (
        workload.operation,
        workload.pattern_payload(),
        freeze_signature_value(args),
        (),
        workload.flags,
        workload.text_model,
    )


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
    return _collection_replacement_has_expected_unexpected_keyword_error(workload)


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
        freeze_signature_value(list(case.args)),
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
        freeze_signature_value(
            list(_collection_replacement_wrong_text_model_workload_args(workload))
        ),
        workload.use_compiled_pattern,
        workload.flags,
        workload.text_model,
    )


def _is_collection_replacement_wrong_text_model_workload(workload: Any) -> bool:
    return (
        getattr(workload, "haystack_text_model", None) is not None
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
        and workload.expected_exception is not None
        and workload.expected_exception.get("type") == "TypeError"
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
        freeze_signature_value(case_args),
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
        freeze_signature_value(
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
