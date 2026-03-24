from __future__ import annotations

import json
import pathlib

import pytest

from rebar_harness.benchmarks import (
    BENCHMARK_WORKLOADS_ROOT,
    build_callable,
    load_manifest,
    run_internal_workload_probe,
    workload_from_payload,
    workload_to_payload,
)
from tests.benchmarks import wrong_text_model_benchmark_owner_support as support
from tests.benchmarks import (
    test_source_tree_combined_boundary_benchmarks as combined,
)
from tests.benchmarks.source_tree_benchmark_anchor_support import (
    run_benchmark_workload_with_cpython,
)
from tests.benchmarks.source_tree_contract_benchmark_support import (
    _source_tree_contract_manifest,
    _source_tree_contract_workload,
)


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


@pytest.mark.parametrize(
    "owner_spec",
    tuple(
        pytest.param(
            owner_spec,
            id=owner_spec.case_id,
        )
        for owner_spec in support.WRONG_TEXT_MODEL_OWNER_SPECS
    ),
)
def test_standard_benchmark_manifest_preserves_wrong_text_model_rows_until_helper_invocation(
    owner_spec: support.WrongTextModelOwnerSpec,
    tmp_path: pathlib.Path,
) -> None:
    source_workloads = owner_spec.source_workloads()
    manifest = _source_tree_contract_manifest(
        source_workloads,
        spec=owner_spec.contract_builder_spec(),
    )
    manifest_path = combined._write_test_manifest(
        tmp_path,
        f"python_benchmark_{owner_spec.contract_filename_stem}_contract.py",
        f"MANIFEST = {manifest!r}\n",
    )
    workloads = load_manifest(manifest_path).workloads

    assert tuple(workload.workload_id for workload in source_workloads) == (
        owner_spec.expected_source_workload_ids
    )
    assert tuple(workload.workload_id for workload in workloads) == tuple(
        f"{workload_id}-contract"
        for workload_id in owner_spec.expected_source_workload_ids
    )
    assert [workload.use_compiled_pattern for workload in workloads] == [
        owner_spec.use_compiled_pattern
    ] * len(source_workloads)
    assert [workload.timing_scope for workload in workloads] == [
        owner_spec.timing_scope
    ] * len(source_workloads)
    assert [workload.haystack_text_model for workload in workloads] == [
        workload.haystack_text_model for workload in source_workloads
    ]

    for source_workload, workload in zip(
        source_workloads,
        workloads,
        strict=True,
    ):
        payload = workload_to_payload(workload)
        round_tripped = workload_from_payload(payload)

        support._assert_wrong_text_model_payload_round_trip(
            source_workload,
            payload,
            round_tripped,
            use_compiled_pattern=owner_spec.use_compiled_pattern,
            timing_scope=owner_spec.timing_scope,
        )

        with pytest.raises(TypeError) as expected_error:
            support._run_cpython_wrong_text_model_workload(
                workload,
                use_compiled_pattern=owner_spec.use_compiled_pattern,
                direct_pattern_route=owner_spec.direct_pattern_route,
            )
        with pytest.raises(TypeError) as observed_error:
            run_benchmark_workload_with_cpython(round_tripped)

        assert str(observed_error.value) == str(expected_error.value)


@pytest.mark.parametrize(
    ("owner_spec", "source_workload"),
    support._WRONG_TEXT_MODEL_SOURCE_WORKLOAD_PARAMS,
)
@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
def test_run_internal_workload_probe_measures_wrong_text_model_contract_workloads(
    owner_spec: support.WrongTextModelOwnerSpec,
    source_workload,
    import_name: str,
    adapter_name: str,
) -> None:
    workload = _source_tree_contract_workload(
        source_workload,
        spec=owner_spec.contract_builder_spec(),
    )
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    support._assert_wrong_text_model_payload_round_trip(
        source_workload,
        payload,
        round_tripped,
        use_compiled_pattern=owner_spec.use_compiled_pattern,
        timing_scope=owner_spec.timing_scope,
    )

    probe = run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name=import_name,
        adapter_name=adapter_name,
    )

    assert probe["status"] == "measured"
    assert probe["median_ns"] > 0


@pytest.mark.parametrize(
    ("owner_spec", "source_workload"),
    support._WRONG_TEXT_MODEL_SOURCE_WORKLOAD_PARAMS,
)
def test_wrong_text_model_callbacks_preserve_precompile_contract(
    owner_spec: support.WrongTextModelOwnerSpec,
    source_workload,
) -> None:
    expected_build_calls = support._wrong_text_model_expected_build_calls(
        source_workload,
        use_compiled_pattern=owner_spec.use_compiled_pattern,
        direct_pattern_route=owner_spec.direct_pattern_route,
    )
    expected_callback_call = support._wrong_text_model_expected_callback_call(
        source_workload,
        use_compiled_pattern=owner_spec.use_compiled_pattern,
        direct_pattern_route=owner_spec.direct_pattern_route,
    )
    module = combined._RecordingBenchmarkModule()
    callback = build_callable(
        module,
        "re",
        _source_tree_contract_workload(
            source_workload,
            spec=owner_spec.contract_builder_spec(),
        ),
    )

    assert module.calls == expected_build_calls
    assert len(module.compiled_patterns) == 1
    assert callback() == support._wrong_text_model_expected_callback_result(
        source_workload,
        use_compiled_pattern=owner_spec.use_compiled_pattern,
        direct_pattern_route=owner_spec.direct_pattern_route,
    )

    if owner_spec.use_compiled_pattern:
        compiled_pattern = module.compiled_patterns[0]
        last_call = module.calls[-1]
        assert last_call[0] == expected_callback_call[0]
        assert last_call[1] is compiled_pattern
        assert last_call[2:] == expected_callback_call[1:]
    else:
        assert module.calls[-1] == expected_callback_call
