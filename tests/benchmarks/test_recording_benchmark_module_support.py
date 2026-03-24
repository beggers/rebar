from __future__ import annotations

import pytest

from rebar_harness.benchmarks import build_callable
from tests.benchmarks.benchmark_test_support import synthetic_workload
from tests.benchmarks.recording_benchmark_module_support import (
    RecordingBenchmarkCompiledPattern,
    RecordingBenchmarkModule,
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
