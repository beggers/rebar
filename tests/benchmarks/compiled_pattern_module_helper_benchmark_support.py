from __future__ import annotations

import re
from typing import Any

from rebar_harness.benchmarks import Workload
from tests.benchmarks.source_tree_benchmark_anchor_support import (
    freeze_signature_value,
)
from tests.python.fixture_parity_support import case_pattern

_COMPILED_PATTERN_MODULE_HELPER_OPERATIONS = frozenset(
    {"module.search", "module.match", "module.fullmatch"}
)
_VERBOSE_REGRESSION_PATTERN = (
    r"^ (?P<key>[A-Z_]+) \s* = \s* (?:[A-Z]{2,4}+|\d{2,3}) $"
)
_VERBOSE_REGRESSION_FLAGS = int(re.VERBOSE | re.MULTILINE)


def _compiled_pattern_module_helper_route(
    workload: Workload,
    *,
    collection_replacement_callback_flags: int,
) -> tuple[object, tuple[object, ...], tuple[object, ...], bool]:
    if workload.operation in {
        "module.search",
        "module.match",
        "module.fullmatch",
    }:
        return (
            "module-result",
            (
                workload.operation,
                workload.haystack_payload(),
                0,
                {},
            ),
            (
                workload.haystack_payload(),
                workload.flags,
            ),
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
            (
                workload.haystack_payload(),
                workload.maxsplit_argument(),
            ),
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
            (
                workload.haystack_payload(),
                workload.flags,
            ),
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
            (
                workload.haystack_payload(),
                workload.flags,
            ),
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


def _run_cpython_compiled_pattern_module_helper_workload(
    workload: Workload,
    *,
    collection_replacement_callback_flags: int,
) -> object:
    compiled_pattern = re.compile(
        workload.pattern_payload(),
        workload.flags,
    )
    _, _, cpython_call_args, materialize_cpython_result = (
        _compiled_pattern_module_helper_route(
            workload,
            collection_replacement_callback_flags=collection_replacement_callback_flags,
        )
    )
    helper = getattr(re, workload.operation.removeprefix("module."))
    result = helper(compiled_pattern, *cpython_call_args)
    if materialize_cpython_result:
        return list(result)
    return result


def _is_module_workflow_compiled_pattern_wrong_text_model_workload(
    workload: object,
) -> bool:
    return (
        not workload.kwargs
        and workload.use_compiled_pattern
        and workload.operation in _COMPILED_PATTERN_MODULE_HELPER_OPERATIONS
        and getattr(workload, "haystack_text_model", None) is not None
        and workload.expected_exception is not None
        and workload.expected_exception.get("type") == "TypeError"
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
        and workload.operation in _COMPILED_PATTERN_MODULE_HELPER_OPERATIONS
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
