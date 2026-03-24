from __future__ import annotations

import pytest

from rebar_harness.benchmarks import build_callable
from tests.benchmarks.benchmark_test_support import synthetic_workload
from tests.benchmarks.recording_benchmark_module_support import (
    RecordingBenchmarkCompiledPattern,
    RecordingBenchmarkModule,
)


def _module_search_cache_contract_workload(
    *,
    cache_mode: str,
    expected_exception: dict[str, str] | None = None,
):
    return synthetic_workload(
        manifest_id="python-benchmark-module-helper-cache-contract",
        workload_id=f"module-search-{cache_mode}-cache-contract",
        bucket="module-search",
        family="module",
        operation="module.search",
        pattern="abc",
        haystack="zabcabc",
        expected_exception=expected_exception,
        text_model="str",
        cache_mode=cache_mode,
        timing_scope="module-helper-call",
    )


def _pattern_search_cache_contract_workload(*, cache_mode: str):
    return synthetic_workload(
        manifest_id="python-benchmark-pattern-helper-cache-contract",
        workload_id=f"pattern-search-{cache_mode}-cache-contract",
        bucket="pattern-search",
        family="module",
        operation="pattern.search",
        pattern="abc",
        haystack="zabcabc",
        text_model="str",
        cache_mode=cache_mode,
        timing_scope="pattern-helper-call",
    )


def test_compile_only_support_records_compile_calls_and_reuses_compiled_patterns() -> None:
    module = RecordingBenchmarkModule()
    compiled_pattern = module.compile("abc", 0)

    assert module.calls == [("compile", "abc", 0)]
    assert len(module.compiled_patterns) == 1
    assert module.compiled_patterns[0] is compiled_pattern
    assert module.compile(compiled_pattern, 0) is compiled_pattern
    assert module.calls[-1] == ("compile", compiled_pattern, 0)


def test_helper_exception_support_records_helper_call_before_raising() -> None:
    module = RecordingBenchmarkModule(
        helper_exception=TypeError("unexpected keyword argument 'missing'"),
    )
    callback = build_callable(
        module,
        "re",
        synthetic_workload(
            manifest_id="module-boundary",
            workload_id="module-search-warm-str-compiled-pattern-support-contract",
            operation="module.search",
            pattern="abc",
            haystack="zabcabc",
            use_compiled_pattern=True,
        ),
    )

    assert module.calls == [("compile", "abc", 0)]
    with pytest.raises(TypeError, match="unexpected keyword argument 'missing'"):
        callback()
    assert module.calls[-1][0] == "module.search"


def test_direct_compiled_pattern_helper_support_records_pattern_calls() -> None:
    module = RecordingBenchmarkModule()
    callback = build_callable(
        module,
        "re",
        synthetic_workload(
            manifest_id="python-benchmark-recording-module-support",
            workload_id="pattern-search-warm-str-contract",
            operation="pattern.search",
            pattern="abc",
            haystack="zabcabc",
            timing_scope="pattern-helper-call",
        ),
    )

    assert module.calls == [("compile", "abc", 0)]
    compiled_pattern = module.compiled_patterns[0]
    assert isinstance(compiled_pattern, RecordingBenchmarkCompiledPattern)

    assert callback() == "pattern-result"
    assert module.calls[-1] == ("pattern.search", "zabcabc", (), {})


@pytest.mark.parametrize(
    ("cache_mode", "expected_build_calls", "expected_callback_calls"),
    (
        pytest.param(
            "cold",
            [],
            [
                ("purge",),
                ("module.search", "abc", "zabcabc", 0, {}),
            ],
            id="cold",
        ),
        pytest.param(
            "warm",
            [
                ("module.search", "abc", "zabcabc", 0, {}),
            ],
            [
                ("module.search", "abc", "zabcabc", 0, {}),
            ],
            id="warm",
        ),
        pytest.param(
            "purged",
            [],
            [
                ("purge",),
                ("module.search", "abc", "zabcabc", 0, {}),
                ("purge",),
            ],
            id="purged",
        ),
    ),
)
def test_module_helper_cache_modes_preserve_expected_purge_and_warmup_order(
    cache_mode: str,
    expected_build_calls: list[tuple[object, ...]],
    expected_callback_calls: list[tuple[object, ...]],
) -> None:
    module = RecordingBenchmarkModule()
    callback = build_callable(
        module,
        "re",
        _module_search_cache_contract_workload(cache_mode=cache_mode),
    )

    assert module.calls == expected_build_calls
    assert callback() == "module-result"
    assert module.calls == [*expected_build_calls, *expected_callback_calls]


def test_module_helper_warm_expected_exception_prewarms_compile_cache_without_invoking_helper(
) -> None:
    module = RecordingBenchmarkModule(
        helper_exception=TypeError("unexpected keyword argument 'missing'"),
    )
    callback = build_callable(
        module,
        "re",
        _module_search_cache_contract_workload(
            cache_mode="warm",
            expected_exception={
                "type": "TypeError",
                "message_substring": "unexpected keyword argument 'missing'",
            },
        ),
    )

    assert module.calls == [("compile", "abc", 0)]
    with pytest.raises(TypeError, match="unexpected keyword argument 'missing'"):
        callback()
    assert module.calls == [
        ("compile", "abc", 0),
        ("module.search", "abc", "zabcabc", 0, {}),
    ]


@pytest.mark.parametrize(
    ("cache_mode", "expected_build_calls", "expected_callback_calls"),
    (
        pytest.param(
            "cold",
            [],
            [
                ("purge",),
                ("compile", "abc", 0),
                ("pattern.search", "zabcabc", (), {}),
            ],
            id="cold",
        ),
        pytest.param(
            "warm",
            [
                ("compile", "abc", 0),
            ],
            [
                ("pattern.search", "zabcabc", (), {}),
            ],
            id="warm",
        ),
        pytest.param(
            "purged",
            [
                ("compile", "abc", 0),
                ("purge",),
            ],
            [
                ("pattern.search", "zabcabc", (), {}),
            ],
            id="purged",
        ),
    ),
)
def test_pattern_helper_cache_modes_preserve_expected_compile_and_purge_order(
    cache_mode: str,
    expected_build_calls: list[tuple[object, ...]],
    expected_callback_calls: list[tuple[object, ...]],
) -> None:
    module = RecordingBenchmarkModule()
    callback = build_callable(
        module,
        "re",
        _pattern_search_cache_contract_workload(cache_mode=cache_mode),
    )

    assert module.calls == expected_build_calls
    assert callback() == "pattern-result"
    assert module.calls == [*expected_build_calls, *expected_callback_calls]
