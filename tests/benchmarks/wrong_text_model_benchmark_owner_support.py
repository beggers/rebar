from __future__ import annotations

import re

from rebar_harness.benchmarks import Workload
from tests.benchmarks.compiled_pattern_module_helper_benchmark_support import (
    _compiled_pattern_module_helper_route,
    _run_cpython_compiled_pattern_module_helper_workload,
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
