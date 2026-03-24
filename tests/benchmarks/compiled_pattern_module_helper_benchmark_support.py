from __future__ import annotations

from dataclasses import dataclass
import re

from rebar_harness.benchmarks import Workload


@dataclass(frozen=True, slots=True)
class _CompiledPatternModuleHelperRoute:
    callback_result: object
    callback_call: tuple[object, ...]
    cpython_call_args: tuple[object, ...]
    materialize_cpython_result: bool = False


def _compiled_pattern_module_helper_route(
    workload: Workload,
    *,
    collection_replacement_callback_flags: int,
) -> _CompiledPatternModuleHelperRoute:
    if workload.operation in {
        "module.search",
        "module.match",
        "module.fullmatch",
    }:
        return _CompiledPatternModuleHelperRoute(
            callback_result="module-result",
            callback_call=(
                workload.operation,
                workload.haystack_payload(),
                0,
                {},
            ),
            cpython_call_args=(
                workload.haystack_payload(),
                workload.flags,
            ),
        )
    if workload.operation == "module.split":
        return _CompiledPatternModuleHelperRoute(
            callback_result="module-result",
            callback_call=(
                workload.operation,
                workload.haystack_payload(),
                workload.maxsplit_argument(),
                collection_replacement_callback_flags,
                {},
            ),
            cpython_call_args=(
                workload.haystack_payload(),
                workload.maxsplit_argument(),
            ),
        )
    if workload.operation == "module.findall":
        return _CompiledPatternModuleHelperRoute(
            callback_result="module-result",
            callback_call=(
                workload.operation,
                workload.haystack_payload(),
                collection_replacement_callback_flags,
            ),
            cpython_call_args=(
                workload.haystack_payload(),
                workload.flags,
            ),
        )
    if workload.operation == "module.finditer":
        return _CompiledPatternModuleHelperRoute(
            callback_result=["module-finditer-result"],
            callback_call=(
                workload.operation,
                workload.haystack_payload(),
                collection_replacement_callback_flags,
            ),
            cpython_call_args=(
                workload.haystack_payload(),
                workload.flags,
            ),
            materialize_cpython_result=True,
        )
    if workload.operation == "module.sub":
        return _CompiledPatternModuleHelperRoute(
            callback_result="module-result",
            callback_call=(
                workload.operation,
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count_argument(),
                collection_replacement_callback_flags,
                {},
            ),
            cpython_call_args=(
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count_argument(),
            ),
        )
    if workload.operation == "module.subn":
        return _CompiledPatternModuleHelperRoute(
            callback_result=("module-result", 0),
            callback_call=(
                workload.operation,
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count_argument(),
                collection_replacement_callback_flags,
                {},
            ),
            cpython_call_args=(
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count_argument(),
            ),
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
    route = _compiled_pattern_module_helper_route(
        workload,
        collection_replacement_callback_flags=collection_replacement_callback_flags,
    )
    helper = getattr(re, workload.operation.removeprefix("module."))
    result = helper(compiled_pattern, *route.cpython_call_args)
    if route.materialize_cpython_result:
        return list(result)
    return result
