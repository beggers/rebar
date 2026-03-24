from __future__ import annotations

import pytest

from rebar_harness.benchmarks import (
    BENCHMARK_WORKLOADS_ROOT,
    load_manifest,
    workload_from_payload,
    workload_to_payload,
)
from tests.benchmarks import wrong_text_model_benchmark_owner_support as support


def _manifest_workload(manifest_name: str, workload_id: str):
    workloads = load_manifest(BENCHMARK_WORKLOADS_ROOT / manifest_name).workloads
    return next(workload for workload in workloads if workload.workload_id == workload_id)


@pytest.mark.parametrize(
    (
        "workload",
        "expected_build_calls",
        "expected_callback_call",
        "expected_callback_result",
        "message_substring",
    ),
    (
        pytest.param(
            _manifest_workload(
                "collection_replacement_boundary.py",
                "module-finditer-on-bytes-string-warm-str-compiled-pattern",
            ),
            [("compile", "abc", 0)],
            ("module.finditer", b"zabczz", 0),
            ["module-finditer-result"],
            "cannot use a string pattern on a bytes-like object",
            id="compiled-pattern-finditer-materialized-iterator",
        ),
        pytest.param(
            _manifest_workload(
                "module_boundary.py",
                "module-fullmatch-on-bytes-string-warm-str-compiled-pattern",
            ),
            [("compile", "abc", 0)],
            ("module.fullmatch", b"abc", 0, {}),
            "module-result",
            "cannot use a string pattern on a bytes-like object",
            id="compiled-pattern-fullmatch-scalar-result",
        ),
    ),
)
def test_compiled_pattern_wrong_text_model_helpers_cover_materialized_iterator_and_scalar_routes(
    workload,
    expected_build_calls,
    expected_callback_call,
    expected_callback_result,
    message_substring: str,
) -> None:
    assert support._wrong_text_model_expected_build_calls(
        workload,
        use_compiled_pattern=True,
        direct_pattern_route=None,
    ) == expected_build_calls
    assert support._wrong_text_model_expected_callback_call(
        workload,
        use_compiled_pattern=True,
        direct_pattern_route=None,
    ) == expected_callback_call
    assert support._wrong_text_model_expected_callback_result(
        workload,
        use_compiled_pattern=True,
        direct_pattern_route=None,
    ) == expected_callback_result

    with pytest.raises(TypeError, match=message_substring):
        support._run_cpython_wrong_text_model_workload(
            workload,
            use_compiled_pattern=True,
            direct_pattern_route=None,
        )


@pytest.mark.parametrize(
    (
        "workload",
        "direct_pattern_route",
        "expected_build_calls",
        "expected_callback_call",
        "expected_callback_result",
        "message_substring",
    ),
    (
        pytest.param(
            _manifest_workload(
                "collection_replacement_boundary.py",
                "pattern-subn-on-str-string-purged-bytes",
            ),
            "collection/replacement",
            [("compile", b"abc", 0), ("purge",)],
            ("pattern.subn", b"x", "zabczz", (0,), {}),
            ("pattern-result", 0),
            "cannot use a bytes pattern on a string-like object",
            id="direct-pattern-collection-replacement",
        ),
        pytest.param(
            _manifest_workload(
                "pattern_boundary.py",
                "pattern-search-on-bytes-string-warm-str",
            ),
            "pattern-boundary",
            [("compile", "abc", 0)],
            ("pattern.search", b"abc", (), {}),
            "pattern-result",
            "cannot use a string pattern on a bytes-like object",
            id="direct-pattern-boundary",
        ),
    ),
)
def test_direct_pattern_wrong_text_model_helpers_cover_collection_replacement_and_pattern_boundary_routes(
    workload,
    direct_pattern_route: str,
    expected_build_calls,
    expected_callback_call,
    expected_callback_result,
    message_substring: str,
) -> None:
    assert support._wrong_text_model_expected_build_calls(
        workload,
        use_compiled_pattern=False,
        direct_pattern_route=direct_pattern_route,
    ) == expected_build_calls
    assert support._wrong_text_model_expected_callback_call(
        workload,
        use_compiled_pattern=False,
        direct_pattern_route=direct_pattern_route,
    ) == expected_callback_call
    assert support._wrong_text_model_expected_callback_result(
        workload,
        use_compiled_pattern=False,
        direct_pattern_route=direct_pattern_route,
    ) == expected_callback_result

    with pytest.raises(TypeError, match=message_substring):
        support._run_cpython_wrong_text_model_workload(
            workload,
            use_compiled_pattern=False,
            direct_pattern_route=direct_pattern_route,
        )


@pytest.mark.parametrize(
    ("workload", "use_compiled_pattern", "timing_scope"),
    (
        pytest.param(
            _manifest_workload(
                "pattern_boundary.py",
                "pattern-search-on-bytes-string-warm-str",
            ),
            False,
            "pattern-helper-call",
            id="str-pattern-bytes-haystack",
        ),
        pytest.param(
            _manifest_workload(
                "collection_replacement_boundary.py",
                "module-subn-on-str-string-purged-bytes-compiled-pattern",
            ),
            True,
            "module-helper-call",
            id="bytes-pattern-str-haystack-with-replacement",
        ),
    ),
)
def test_assert_wrong_text_model_payload_round_trip_preserves_str_and_bytes_rows(
    workload,
    use_compiled_pattern: bool,
    timing_scope: str,
) -> None:
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    support._assert_wrong_text_model_payload_round_trip(
        workload,
        payload,
        round_tripped,
        use_compiled_pattern=use_compiled_pattern,
        timing_scope=timing_scope,
    )
