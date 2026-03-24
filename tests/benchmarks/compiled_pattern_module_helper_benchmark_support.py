from __future__ import annotations

import re

from rebar_harness.benchmarks import Workload

_COMPILED_PATTERN_MODULE_HELPER_OPERATIONS = frozenset(
    {"module.search", "module.match", "module.fullmatch"}
)


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
