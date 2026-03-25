from __future__ import annotations

import json
import pathlib
import re
from types import SimpleNamespace

import pytest

from rebar_harness.benchmarks import (
    Workload,
    build_callable,
    load_manifest,
    run_internal_workload_probe,
    workload_from_payload,
    workload_to_payload,
)
from tests.benchmarks.benchmark_test_support import (
    RecordingBenchmarkModule,
    STANDARD_BENCHMARK_DEFINITIONS,
    _assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call,
    _record_numeric_materialization_fields,
    _write_test_manifest,
    assert_benchmark_workload_matches_expected_result,
    assert_zero_gap_manifest_workloads_measured,
    top_level_module_definition_and_assignment_names,
    published_case_ids_by_signature,
    run_benchmark_workload_with_cpython,
    selected_manifest_workloads,
)
from tests.benchmarks import (
    compiled_pattern_module_helper_benchmark_support as compiled_pattern_module_helper_support,
)
from tests.benchmarks.benchmark_test_support import (
    compiled_pattern_contract_expected_build_calls,
    _source_tree_contract_manifest,
    _source_tree_contract_workload,
)
from tests.benchmarks.collection_replacement_benchmark_anchor_support import (
    _is_collection_replacement_compiled_pattern_success_workload,
)


def _compiled_pattern_module_helper_standard_definition(name: str) -> object:
    return next(
        definition
        for definition in (
            compiled_pattern_module_helper_support.COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS
        )
        if definition.name == name
    )


def _compiled_pattern_module_success_selector_candidate(
    **overrides,
) -> SimpleNamespace:
    payload = {
        "operation": "module.search",
        "use_compiled_pattern": False,
        "expected_exception": None,
        "haystack_text_model": None,
        "kwargs": {},
    }
    payload.update(overrides)
    return SimpleNamespace(**payload)


def _compiled_pattern_module_helper_keyword_contract_surface(case_id: str) -> object:
    return next(
        surface
        for surface in (
            compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES
        )
        if surface.case_id == case_id
    )


_COMPILED_PATTERN_MODULE_HELPER_STANDARD_DEFINITION_EXPECTATIONS = (
    pytest.param(
        "module-workflow-compiled-pattern-literal-success",
        (
            (
                "module-search-literal-warm-hit-str-compiled-pattern",
                ("workflow-module-search-str-compiled-pattern",),
            ),
            (
                "module-match-literal-warm-hit-str-compiled-pattern",
                ("workflow-module-match-str-compiled-pattern",),
            ),
            (
                "module-fullmatch-literal-purged-hit-bytes-compiled-pattern",
                ("workflow-module-fullmatch-bytes-compiled-pattern",),
            ),
        ),
        True,
        id="literal-success",
    ),
    pytest.param(
        "module-workflow-compiled-pattern-bounded-wildcard-success",
        (
            (
                "module-search-bounded-wildcard-ignorecase-warm-hit-str-compiled-pattern",
                ("workflow-module-search-str-bounded-wildcard-ignorecase-compiled-pattern",),
            ),
            (
                "module-match-bounded-wildcard-warm-hit-str-compiled-pattern",
                ("workflow-module-match-str-bounded-wildcard-compiled-pattern",),
            ),
            (
                "module-fullmatch-bounded-wildcard-purged-hit-str-compiled-pattern",
                ("workflow-module-fullmatch-str-bounded-wildcard-compiled-pattern",),
            ),
        ),
        True,
        id="bounded-wildcard-success",
    ),
    pytest.param(
        "module-workflow-compiled-pattern-verbose-bytes-success",
        (
            (
                "module-search-verbose-regression-warm-hit-bytes-compiled-pattern",
                ("workflow-module-search-bytes-verbose-regression-compiled-pattern",),
            ),
            (
                "module-fullmatch-verbose-regression-purged-hit-bytes-compiled-pattern",
                ("workflow-module-fullmatch-bytes-verbose-regression-compiled-pattern",),
            ),
        ),
        True,
        id="verbose-bytes-success",
    ),
    pytest.param(
        "module-workflow-compiled-pattern-wrong-text-model",
        (
            (
                "module-search-on-bytes-string-warm-str-compiled-pattern",
                ("workflow-module-search-str-compiled-pattern-on-bytes-string",),
            ),
            (
                "module-match-on-str-string-purged-bytes-compiled-pattern",
                ("workflow-module-match-bytes-compiled-pattern-on-str-string",),
            ),
            (
                "module-fullmatch-on-bytes-string-warm-str-compiled-pattern",
                ("workflow-module-fullmatch-str-compiled-pattern-on-bytes-string",),
            ),
        ),
        False,
        id="wrong-text-model",
    ),
)


def test_compiled_pattern_wrong_text_model_owner_spec_surface_is_owner_module_owned_without_local_duplicates(
) -> None:
    import sys

    from tests.benchmarks import (
        compiled_pattern_module_helper_benchmark_support as support,
    )
    from tests.benchmarks.benchmark_test_support import (
        top_level_module_definition_and_assignment_names,
    )

    local_definition_names, local_assignment_names = (
        top_level_module_definition_and_assignment_names(sys.modules[__name__])
    )

    assert (
        compiled_pattern_module_helper_support._COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
        is support._COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
    )
    assert (
        compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
        is support._COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
    )
    assert (
        compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_specs
        is support._compiled_pattern_wrong_text_model_specs
    )
    assert (
        compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_source_workloads
        is support._compiled_pattern_wrong_text_model_source_workloads
    )
    assert (
        compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_contract_spec
        is support._compiled_pattern_wrong_text_model_contract_spec
    )
    assert (
        compiled_pattern_module_helper_support._assert_wrong_text_model_payload_round_trip
        is support._assert_wrong_text_model_payload_round_trip
    )
    assert {
        "_compiled_pattern_wrong_text_model_specs",
        "_compiled_pattern_wrong_text_model_source_workloads",
        "_compiled_pattern_wrong_text_model_contract_spec",
        "_assert_wrong_text_model_payload_round_trip",
    }.isdisjoint(local_definition_names)
    assert {
        "_COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS",
        "_COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS",
    }.isdisjoint(local_assignment_names)


def test_standard_inventory_reuses_owner_owned_compiled_pattern_module_helper_definitions(
) -> None:
    owner_definitions = (
        compiled_pattern_module_helper_support.COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS
    )
    definition_names = {
        "module-workflow-compiled-pattern-literal-success",
        "module-workflow-compiled-pattern-bounded-wildcard-success",
        "module-workflow-compiled-pattern-verbose-bytes-success",
        "module-workflow-compiled-pattern-wrong-text-model",
    }

    standard_definitions = tuple(
        definition
        for definition in STANDARD_BENCHMARK_DEFINITIONS
        if definition.name in definition_names
    )

    assert tuple(definition.name for definition in owner_definitions) == (
        "module-workflow-compiled-pattern-literal-success",
        "module-workflow-compiled-pattern-bounded-wildcard-success",
        "module-workflow-compiled-pattern-verbose-bytes-success",
        "module-workflow-compiled-pattern-wrong-text-model",
    )
    assert standard_definitions == owner_definitions
    assert all(
        standard_definition is owner_definition
        for standard_definition, owner_definition in zip(
            standard_definitions,
            owner_definitions,
            strict=True,
        )
    )


def test_compiled_pattern_module_helper_support_owns_success_owner_surface() -> None:
    import sys

    local_definition_names, local_assignment_names = (
        top_level_module_definition_and_assignment_names(sys.modules[__name__])
    )
    support_definition_names, support_assignment_names = (
        top_level_module_definition_and_assignment_names(
            compiled_pattern_module_helper_support
        )
    )

    assert not {
        "CompiledPatternModuleSuccessOwnerSpec",
        "_assert_compiled_pattern_module_success_payload_round_trip",
        "_assert_compiled_pattern_success_rows_measured_in_combined_manifest",
    } & local_definition_names
    assert {
        "CompiledPatternModuleSuccessOwnerSpec",
        "_assert_compiled_pattern_module_success_payload_round_trip",
        "_assert_compiled_pattern_success_rows_measured_in_combined_manifest",
        "include_live_compiled_pattern_module_success_workload",
        "live_compiled_pattern_module_success_surface_ids",
    }.issubset(support_definition_names)
    assert {
        "_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC",
        "_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC",
        "_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS",
        "_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS",
    }.issubset(support_assignment_names)
    assert {
        "_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC",
        "_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC",
        "_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS",
        "_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS",
    }.isdisjoint(local_assignment_names)
    assert (
        compiled_pattern_module_helper_support.CompiledPatternModuleSuccessOwnerSpec.contract_builder_spec.__name__
        == "contract_builder_spec"
    )
    assert (
        compiled_pattern_module_helper_support.CompiledPatternModuleSuccessOwnerSpec.source_workloads.__name__
        == "source_workloads"
    )
    assert (
        compiled_pattern_module_helper_support.CompiledPatternModuleSuccessOwnerSpec.expected_build_calls.__name__
        == "expected_build_calls"
    )
    assert (
        compiled_pattern_module_helper_support.CompiledPatternModuleSuccessOwnerSpec.expected_callback_result.__name__
        == "expected_callback_result"
    )
    assert (
        compiled_pattern_module_helper_support.CompiledPatternModuleSuccessOwnerSpec.expected_callback_call.__name__
        == "expected_callback_call"
    )


def test_compiled_pattern_module_success_owner_specs_match_live_nonkeyword_noncompile_success_surface_without_overlap(
) -> None:
    owner_surface_ids = tuple(
        source_workload.workload_id
        for owner_spec in (
            compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS
        )
        for source_workload in owner_spec.source_workloads()
    )
    expected_live_surface_ids = tuple(
        workload.workload_id
        for owner_spec in (
            compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS
        )
        for workload in selected_manifest_workloads(
            owner_spec.manifest_path,
            include_workload=(
                compiled_pattern_module_helper_support.include_live_compiled_pattern_module_success_workload
            ),
        )
    )

    assert tuple(sorted(owner_surface_ids)) == tuple(sorted(expected_live_surface_ids))
    assert expected_live_surface_ids == (
        compiled_pattern_module_helper_support.live_compiled_pattern_module_success_surface_ids()
    )
    assert len(owner_surface_ids) == len(set(owner_surface_ids))


@pytest.mark.parametrize(
    ("workload", "expected"),
    (
        pytest.param(
            _compiled_pattern_module_success_selector_candidate(
                use_compiled_pattern=True,
            ),
            True,
            id="module-boundary-direct-success",
        ),
        pytest.param(
            _compiled_pattern_module_success_selector_candidate(
                operation="module.sub",
                use_compiled_pattern=True,
            ),
            True,
            id="collection-replacement-direct-success",
        ),
        pytest.param(
            _compiled_pattern_module_success_selector_candidate(),
            False,
            id="rejects-non-compiled-pattern-workload",
        ),
        pytest.param(
            _compiled_pattern_module_success_selector_candidate(
                expected_exception={
                    "type": "TypeError",
                    "message_substring": "synthetic selector rejection",
                },
                use_compiled_pattern=True,
            ),
            False,
            id="rejects-exception-workload",
        ),
        pytest.param(
            _compiled_pattern_module_success_selector_candidate(
                operation="module.fullmatch",
                use_compiled_pattern=True,
                haystack_text_model="bytes",
            ),
            False,
            id="rejects-wrong-text-model-workload",
        ),
        pytest.param(
            _compiled_pattern_module_success_selector_candidate(
                operation="module.split",
                kwargs={"maxsplit": 1},
                use_compiled_pattern=True,
            ),
            False,
            id="rejects-keyword-workload",
        ),
        pytest.param(
            _compiled_pattern_module_success_selector_candidate(
                operation="module.compile",
                use_compiled_pattern=True,
            ),
            False,
            id="rejects-compile-workload",
        ),
        pytest.param(
            _compiled_pattern_module_success_selector_candidate(
                operation="pattern.search",
                use_compiled_pattern=True,
            ),
            False,
            id="rejects-non-module-operation",
        ),
    ),
)
def test_include_live_compiled_pattern_module_success_workload_accepts_only_direct_success_rows(
    workload,
    expected: bool,
) -> None:
    assert (
        compiled_pattern_module_helper_support.include_live_compiled_pattern_module_success_workload(
            workload
        )
        is expected
    )


@pytest.mark.parametrize(
    ("definition_name", "expected_workload_case_pairs", "expects_callback_parity"),
    _COMPILED_PATTERN_MODULE_HELPER_STANDARD_DEFINITION_EXPECTATIONS,
)
def test_compiled_pattern_module_helper_standard_definitions_select_expected_live_workloads_and_case_anchors(
    definition_name: str,
    expected_workload_case_pairs: tuple[tuple[str, tuple[str, ...]], ...],
    expects_callback_parity: bool,
) -> None:
    definition = _compiled_pattern_module_helper_standard_definition(definition_name)
    manifest_path = definition.manifest_paths[0]
    workloads = selected_manifest_workloads(
        manifest_path,
        include_workload=definition.includes_workload,
    )
    published_case_ids = published_case_ids_by_signature(
        definition.correctness_case_signature
    )

    assert definition.manifest_paths == (
        compiled_pattern_module_helper_support.MODULE_BOUNDARY_MANIFEST_PATH,
    )
    assert tuple(workload.workload_id for workload in workloads) == tuple(
        workload_id for workload_id, _ in expected_workload_case_pairs
    )
    assert all(workload.use_compiled_pattern for workload in workloads)
    assert all(workload.manifest_id == "module-boundary" for workload in workloads)
    assert tuple(
        (
            workload.workload_id,
            published_case_ids[definition.workload_signature(workload)],
        )
        for workload in workloads
    ) == expected_workload_case_pairs
    assert definition.expected_anchor_case_ids == {
        (manifest_path.name, workload_id): case_ids
        for workload_id, case_ids in expected_workload_case_pairs
    }
    assert definition.run_callback_result_parity is expects_callback_parity


@pytest.mark.parametrize(
    "spec",
    tuple(
        pytest.param(spec, id=str(spec["case_id"]))
        for spec in compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_specs()
    ),
)
def test_compiled_pattern_wrong_text_model_source_workloads_stay_exact_and_in_order(
    spec: dict[str, object],
) -> None:
    workloads = (
        compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_source_workloads(
            spec
        )
    )

    assert tuple(workload.workload_id for workload in workloads) == tuple(
        spec["expected_source_workload_ids"]
    )


@pytest.mark.parametrize(
    ("spec", "workload"),
    tuple(
        pytest.param(spec, workload, id=f"{spec['case_id']}-{workload.workload_id}")
        for spec in compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_specs()
        for workload in compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_source_workloads(
            spec
        )
    ),
)
def test_compiled_pattern_wrong_text_model_helpers_preserve_callback_and_runtime_contract(
    spec: dict[str, object],
    workload: Workload,
) -> None:
    expected_callback_result, expected_callback_call, _, _ = (
        compiled_pattern_module_helper_support._compiled_pattern_module_helper_route(
            workload,
            collection_replacement_callback_flags=0,
        )
    )

    assert compiled_pattern_contract_expected_build_calls(
        workload,
        label="wrong-text-model",
    ) == (
        [("compile", workload.pattern_payload(), workload.flags)]
        if workload.cache_mode == "warm"
        else [("compile", workload.pattern_payload(), workload.flags), ("purge",)]
    )
    assert (
        expected_callback_call
        == compiled_pattern_module_helper_support._compiled_pattern_module_helper_route(
            workload,
            collection_replacement_callback_flags=0,
        )[1]
    )
    assert (
        expected_callback_result
        == compiled_pattern_module_helper_support._compiled_pattern_module_helper_route(
            workload,
            collection_replacement_callback_flags=0,
        )[0]
    )

    with pytest.raises(TypeError) as observed_error:
        compiled_pattern_module_helper_support._run_cpython_compiled_pattern_module_helper_workload(
            workload,
            collection_replacement_callback_flags=0,
        )

    assert str(observed_error.value) == str(
        workload.expected_exception["message_substring"]
    )


@pytest.mark.parametrize(
    "spec",
    tuple(
        pytest.param(spec, id=str(spec["case_id"]))
        for spec in compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_specs()
    ),
)
def test_standard_benchmark_manifest_preserves_compiled_pattern_wrong_text_model_rows_until_helper_invocation(
    spec: dict[str, object],
    tmp_path: pathlib.Path,
) -> None:
    source_workloads = (
        compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_source_workloads(
            spec
        )
    )
    contract_spec = (
        compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_contract_spec(
            spec
        )
    )
    manifest = _source_tree_contract_manifest(
        source_workloads,
        spec=contract_spec,
    )
    manifest_path = _write_test_manifest(
        tmp_path,
        str(spec["contract_filename"]),
        f"MANIFEST = {manifest!r}\n",
    )
    workloads = tuple(load_manifest(manifest_path).workloads)

    assert tuple(workload.workload_id for workload in source_workloads) == tuple(
        spec["expected_source_workload_ids"]
    )
    assert tuple(workload.workload_id for workload in workloads) == tuple(
        f"{workload_id}-contract" for workload_id in spec["expected_source_workload_ids"]
    )
    assert [workload.use_compiled_pattern for workload in workloads] == [True] * len(
        source_workloads
    )
    assert [workload.timing_scope for workload in workloads] == [
        "module-helper-call"
    ] * len(source_workloads)
    assert [workload.haystack_text_model for workload in workloads] == [
        workload.haystack_text_model for workload in source_workloads
    ]

    for source_workload, workload in zip(source_workloads, workloads, strict=True):
        payload = workload_to_payload(workload)
        round_tripped = workload_from_payload(payload)

        compiled_pattern_module_helper_support._assert_wrong_text_model_payload_round_trip(
            source_workload,
            payload,
            round_tripped,
        )

        with pytest.raises(TypeError) as expected_error:
            compiled_pattern_module_helper_support._run_cpython_compiled_pattern_module_helper_workload(
                workload,
                collection_replacement_callback_flags=0,
            )
        with pytest.raises(TypeError) as observed_error:
            run_benchmark_workload_with_cpython(round_tripped)

        assert str(observed_error.value) == str(expected_error.value)


@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
@pytest.mark.parametrize(
    ("spec", "source_workload"),
    tuple(
        pytest.param(spec, workload, id=f"{spec['case_id']}-{workload.workload_id}")
        for spec in compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_specs()
        for workload in compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_source_workloads(
            spec
        )
    ),
)
def test_run_internal_workload_probe_measures_compiled_pattern_wrong_text_model_contract_workloads(
    spec: dict[str, object],
    source_workload: Workload,
    import_name: str,
    adapter_name: str,
) -> None:
    workload = _source_tree_contract_workload(
        source_workload,
        spec=compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_contract_spec(
            spec
        ),
    )
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    compiled_pattern_module_helper_support._assert_wrong_text_model_payload_round_trip(
        source_workload,
        payload,
        round_tripped,
    )

    probe = run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name=import_name,
        adapter_name=adapter_name,
    )

    assert probe["status"] == "measured"
    assert probe["median_ns"] > 0


@pytest.mark.parametrize(
    ("spec", "source_workload"),
    tuple(
        pytest.param(spec, workload, id=f"{spec['case_id']}-{workload.workload_id}")
        for spec in compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_specs()
        for workload in compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_source_workloads(
            spec
        )
    ),
)
def test_compiled_pattern_wrong_text_model_callbacks_preserve_precompile_contract(
    spec: dict[str, object],
    source_workload: Workload,
) -> None:
    expected_build_calls = compiled_pattern_contract_expected_build_calls(
        source_workload,
        label="wrong-text-model",
    )
    expected_callback_result, expected_callback_call, _, _ = (
        compiled_pattern_module_helper_support._compiled_pattern_module_helper_route(
            source_workload,
            collection_replacement_callback_flags=0,
        )
    )
    module = RecordingBenchmarkModule()
    callback = build_callable(
        module,
        "re",
        _source_tree_contract_workload(
            source_workload,
            spec=compiled_pattern_module_helper_support._compiled_pattern_wrong_text_model_contract_spec(
                spec
            ),
        ),
    )

    assert module.calls == expected_build_calls
    assert len(module.compiled_patterns) == 1
    assert callback() == expected_callback_result

    compiled_pattern = module.compiled_patterns[0]
    last_call = module.calls[-1]
    assert last_call[0] == expected_callback_call[0]
    assert last_call[1] is compiled_pattern
    assert last_call[2:] == expected_callback_call[1:]


@pytest.mark.parametrize(
    "owner_spec",
    compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS,
    ids=lambda owner_spec: owner_spec.case_id,
)
def test_standard_benchmark_manifest_preserves_compiled_pattern_module_success_rows_until_helper_invocation(
    tmp_path: pathlib.Path,
    owner_spec: compiled_pattern_module_helper_support.CompiledPatternModuleSuccessOwnerSpec,
) -> None:
    source_workloads = owner_spec.source_workloads()
    manifest = _source_tree_contract_manifest(
        source_workloads,
        spec=owner_spec.contract_builder_spec(),
    )

    manifest_path = _write_test_manifest(
        tmp_path,
        owner_spec.contract_filename,
        f"MANIFEST = {manifest!r}\n",
    )
    workloads = load_manifest(manifest_path).workloads

    assert tuple(workload.workload_id for workload in source_workloads) == (
        owner_spec.expected_source_workload_ids
    )
    assert tuple(workload.workload_id for workload in workloads) == tuple(
        f"{workload.workload_id}-contract" for workload in source_workloads
    )
    assert [workload.use_compiled_pattern for workload in workloads] == [
        True
    ] * len(source_workloads)
    assert [workload.haystack_text_model for workload in workloads] == [
        None
    ] * len(source_workloads)

    for source_workload, workload in zip(source_workloads, workloads, strict=True):
        payload = workload_to_payload(workload)
        round_tripped = workload_from_payload(payload)

        compiled_pattern_module_helper_support._assert_compiled_pattern_module_success_payload_round_trip(
            source_workload,
            payload,
            round_tripped,
            owner_spec=owner_spec,
        )
        assert_benchmark_workload_matches_expected_result(
            round_tripped,
            run_benchmark_workload_with_cpython(round_tripped),
        )


def test_collection_replacement_manifest_keeps_compiled_pattern_success_rows_measured(
) -> None:
    compiled_pattern_module_helper_support._assert_compiled_pattern_success_rows_measured_in_combined_manifest(
        compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC,
        include_workload=_is_collection_replacement_compiled_pattern_success_workload,
    )


def test_module_boundary_manifest_keeps_literal_compiled_pattern_success_rows_measured(
) -> None:
    compiled_pattern_module_helper_support._assert_compiled_pattern_success_rows_measured_in_combined_manifest(
        compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC,
        include_workload=(
            compiled_pattern_module_helper_support._is_module_workflow_compiled_pattern_literal_success_workload
        ),
    )


def test_module_boundary_manifest_keeps_bounded_wildcard_compiled_pattern_success_rows_measured(
) -> None:
    compiled_pattern_module_helper_support._assert_compiled_pattern_success_rows_measured_in_combined_manifest(
        compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC,
        include_workload=(
            compiled_pattern_module_helper_support._is_module_workflow_compiled_pattern_bounded_wildcard_success_workload
        ),
    )


def test_module_boundary_manifest_keeps_verbose_bytes_compiled_pattern_success_rows_measured(
) -> None:
    compiled_pattern_module_helper_support._assert_compiled_pattern_success_rows_measured_in_combined_manifest(
        compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC,
        include_workload=(
            compiled_pattern_module_helper_support._is_module_workflow_compiled_pattern_verbose_bytes_success_workload
        ),
    )


@pytest.mark.parametrize(
    ("owner_spec", "source_workload"),
    compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS,
)
@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
def test_run_internal_workload_probe_measures_compiled_pattern_module_success_contract_workloads(
    owner_spec: compiled_pattern_module_helper_support.CompiledPatternModuleSuccessOwnerSpec,
    source_workload: Workload,
    import_name: str,
    adapter_name: str,
) -> None:
    workload = _source_tree_contract_workload(
        source_workload,
        spec=owner_spec.contract_builder_spec(),
    )
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    compiled_pattern_module_helper_support._assert_compiled_pattern_module_success_payload_round_trip(
        source_workload,
        payload,
        round_tripped,
        owner_spec=owner_spec,
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
    compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS,
)
def test_compiled_pattern_module_success_callbacks_precompile_first_argument_before_timing(
    owner_spec: compiled_pattern_module_helper_support.CompiledPatternModuleSuccessOwnerSpec,
    source_workload: Workload,
) -> None:
    expected_build_calls = owner_spec.expected_build_calls(source_workload)
    expected_callback_call = owner_spec.expected_callback_call(source_workload)
    module = RecordingBenchmarkModule()
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
    assert callback() == owner_spec.expected_callback_result(source_workload)

    compiled_pattern = module.compiled_patterns[0]
    last_call = module.calls[-1]
    assert last_call[0] == expected_callback_call[0]
    assert last_call[1] is compiled_pattern
    assert last_call[2:] == expected_callback_call[1:]


def test_compiled_pattern_module_helper_keyword_contract_surface_is_support_owned_without_local_duplicates(
) -> None:
    import sys

    from tests.benchmarks import (
        compiled_pattern_module_helper_benchmark_support as support,
    )

    local_definition_names, local_assignment_names = (
        top_level_module_definition_and_assignment_names(sys.modules[__name__])
    )

    assert (
        compiled_pattern_module_helper_support.COLLECTION_REPLACEMENT_MANIFEST_PATH
        is support.COLLECTION_REPLACEMENT_MANIFEST_PATH
    )
    assert (
        compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC
        is support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC
    )
    assert (
        compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC
        is support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC
    )
    assert (
        compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS
        is support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS
    )
    assert (
        compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS
        is support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS
    )
    assert (
        compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS
        is support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS
    )
    assert (
        compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES
        is support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES
    )
    assert (
        compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACE_PARAMS
        is support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACE_PARAMS
    )
    assert (
        compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS
        is support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS
    )
    assert (
        compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS
        is support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS
    )
    assert (
        compiled_pattern_module_helper_support._is_collection_replacement_compiled_pattern_keyword_error_workload
        is support._is_collection_replacement_compiled_pattern_keyword_error_workload
    )
    assert {
        "_CompiledPatternModuleHelperKeywordContractSpec",
        "_CompiledPatternModuleHelperKeywordContractSurface",
    }.isdisjoint(local_definition_names)
    assert {
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACE_PARAMS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS",
    }.isdisjoint(local_assignment_names)


def test_compiled_pattern_module_helper_keyword_source_workload_order_stays_pinned() -> None:
    success_surface = _compiled_pattern_module_helper_keyword_contract_surface("success")
    keyword_error_surface = _compiled_pattern_module_helper_keyword_contract_surface(
        "keyword-error"
    )

    assert tuple(
        workload.workload_id for workload in success_surface.source_workloads()
    ) == (
        compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC.expected_source_workload_ids
    )
    assert tuple(
        workload.workload_id for workload in keyword_error_surface.source_workloads()
    ) == (
        compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC.expected_source_workload_ids
    )


def test_collection_replacement_manifest_keeps_compiled_pattern_module_helper_keyword_error_rows_measured(
) -> None:
    expected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in selected_manifest_workloads(
            compiled_pattern_module_helper_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
            include_workload=(
                compiled_pattern_module_helper_support._is_collection_replacement_compiled_pattern_keyword_error_workload
            ),
        )
    )
    expected_source_workload_ids = tuple(
        workload.workload_id
        for workload in (
            compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS
        )
    )
    manifest_workload_count = len(
        selected_manifest_workloads(
            compiled_pattern_module_helper_support.COLLECTION_REPLACEMENT_MANIFEST_PATH
        )
    )

    assert expected_measured_workload_ids == expected_source_workload_ids
    assert_zero_gap_manifest_workloads_measured(
        manifest_path=compiled_pattern_module_helper_support.COLLECTION_REPLACEMENT_MANIFEST_PATH,
        manifest_id="collection-replacement-boundary",
        expected_measured_workload_ids=expected_measured_workload_ids,
        expected_measured_workload_count=manifest_workload_count,
        expected_total_workload_count=manifest_workload_count,
    )


def test_compiled_pattern_module_helper_keyword_success_payload_round_trip_preserves_bool_type(
) -> None:
    success_surface = _compiled_pattern_module_helper_keyword_contract_surface("success")
    source_workload = next(
        workload
        for workload in success_surface.source_workloads()
        if workload.workload_id
        == "module-sub-count-bool-false-keyword-warm-str-compiled-pattern"
    )
    workload = _source_tree_contract_workload(
        source_workload,
        spec=success_surface.spec.contract_builder_spec(),
    )
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    success_surface.assert_payload_round_trip(
        source_workload,
        payload,
        round_tripped,
    )

    assert payload.get("expected_exception") is None
    assert round_tripped.expected_exception is None
    assert type(payload["kwargs"]["count"]) is bool
    assert type(round_tripped.kwargs["count"]) is bool


def test_compiled_pattern_module_helper_keyword_error_payload_round_trip_preserves_expected_exception(
) -> None:
    keyword_error_surface = _compiled_pattern_module_helper_keyword_contract_surface(
        "keyword-error"
    )
    source_workload = next(
        workload
        for workload in keyword_error_surface.source_workloads()
        if workload.workload_id
        == "module-sub-unexpected-keyword-after-positional-count-purged-str-compiled-pattern"
    )
    workload = _source_tree_contract_workload(
        source_workload,
        spec=keyword_error_surface.spec.contract_builder_spec(),
    )
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    keyword_error_surface.assert_payload_round_trip(
        source_workload,
        payload,
        round_tripped,
    )

    assert payload["expected_exception"] == source_workload.expected_exception
    assert round_tripped.expected_exception == source_workload.expected_exception


def test_compiled_pattern_module_helper_keyword_expected_materialized_field_names_cover_split_and_sub(
) -> None:
    success_surface = _compiled_pattern_module_helper_keyword_contract_surface("success")
    keyword_error_surface = _compiled_pattern_module_helper_keyword_contract_surface(
        "keyword-error"
    )

    split_duplicate_workload = next(
        workload
        for workload in keyword_error_surface.source_workloads()
        if workload.workload_id
        == "module-split-duplicate-maxsplit-keyword-purged-str-compiled-pattern"
    )
    sub_keyword_workload = next(
        workload
        for workload in success_surface.source_workloads()
        if workload.workload_id == "module-sub-count-keyword-warm-str-compiled-pattern"
    )

    assert keyword_error_surface.spec.expected_materialized_field_names(
        split_duplicate_workload
    ) == ("maxsplit", "kwargs.maxsplit")
    assert success_surface.spec.expected_materialized_field_names(
        sub_keyword_workload
    ) == ("kwargs.count",)


def test_compiled_pattern_module_helper_keyword_precompile_anchor_order_stays_pinned(
) -> None:
    assert tuple(
        workload.workload_id
        for workload in (
            compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS
        )
    ) == (
        compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC.precompile_anchor_ids
    )


def test_compiled_pattern_module_helper_keyword_cpython_outcomes_cover_success_and_error_lanes(
) -> None:
    success_surface = _compiled_pattern_module_helper_keyword_contract_surface("success")
    success_source_workload = next(
        workload
        for workload in success_surface.source_workloads()
        if workload.workload_id
        == "module-subn-count-keyword-purged-bytes-compiled-pattern"
    )
    success_workload = _source_tree_contract_workload(
        success_source_workload,
        spec=success_surface.spec.contract_builder_spec(),
    )
    success_payload = workload_to_payload(success_workload)
    success_round_tripped = workload_from_payload(success_payload)

    success_surface.assert_outcome(
        success_source_workload,
        success_workload,
        success_round_tripped,
    )
    assert success_surface.run_cpython_helper_workload(success_workload) == (
        b"xabc",
        1,
    )

    keyword_error_surface = _compiled_pattern_module_helper_keyword_contract_surface(
        "keyword-error"
    )
    keyword_error_source_workload = next(
        workload
        for workload in keyword_error_surface.source_workloads()
        if workload.workload_id
        == "module-subn-count-alias-keyword-purged-bytes-compiled-pattern"
    )
    keyword_error_workload = _source_tree_contract_workload(
        keyword_error_source_workload,
        spec=keyword_error_surface.spec.contract_builder_spec(),
    )
    keyword_error_payload = workload_to_payload(keyword_error_workload)
    keyword_error_round_tripped = workload_from_payload(keyword_error_payload)

    keyword_error_surface.assert_outcome(
        keyword_error_source_workload,
        keyword_error_workload,
        keyword_error_round_tripped,
    )
    with pytest.raises(TypeError):
        run_benchmark_workload_with_cpython(keyword_error_round_tripped)


def test_compiled_pattern_module_helper_keyword_cases_cover_bool_count_complements() -> None:
    assert {
        (
            workload.workload_id,
            workload.operation,
            workload.text_model,
            workload.kwargs["count"],
            run_benchmark_workload_with_cpython(workload),
        )
        for workload in (
            compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS
        )
        if workload.operation in {"module.sub", "module.subn"}
        and type(workload.kwargs.get("count")) is bool
    } == {
        (
            "module-sub-count-bool-keyword-warm-str-compiled-pattern",
            "module.sub",
            "str",
            True,
            "xabc",
        ),
        (
            "module-sub-count-bool-false-keyword-warm-str-compiled-pattern",
            "module.sub",
            "str",
            False,
            "xx",
        ),
        (
            "module-subn-count-bool-keyword-purged-bytes-compiled-pattern",
            "module.subn",
            "bytes",
            False,
            (b"xx", 2),
        ),
        (
            "module-subn-count-bool-true-keyword-purged-bytes-compiled-pattern",
            "module.subn",
            "bytes",
            True,
            (b"xabc", 1),
        ),
    }


@pytest.mark.parametrize(
    "contract_surface",
    compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACE_PARAMS,
)
def test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_keyword_contract_rows_until_helper_invocation(
    tmp_path,
    contract_surface,
) -> None:
    source_workloads = contract_surface.source_workloads()
    manifest = _source_tree_contract_manifest(
        source_workloads,
        spec=contract_surface.spec.contract_builder_spec(),
    )

    manifest_path = _write_test_manifest(
        tmp_path,
        contract_surface.spec.contract_filename,
        f"MANIFEST = {manifest!r}\n",
    )
    workloads = load_manifest(manifest_path).workloads

    assert tuple(workload.workload_id for workload in source_workloads) == (
        contract_surface.spec.expected_source_workload_ids
    )
    assert tuple(workload.workload_id for workload in workloads) == tuple(
        f"{workload.workload_id}-contract" for workload in source_workloads
    )
    assert [workload.use_compiled_pattern for workload in workloads] == [
        True
    ] * len(source_workloads)
    assert [workload.haystack_text_model for workload in workloads] == [
        None
    ] * len(source_workloads)

    for source_workload, workload in zip(
        source_workloads,
        workloads,
        strict=True,
    ):
        payload = workload_to_payload(workload)
        round_tripped = workload_from_payload(payload)

        contract_surface.assert_payload_round_trip(
            source_workload,
            payload,
            round_tripped,
        )
        contract_surface.assert_outcome(
            source_workload,
            workload,
            round_tripped,
        )


@pytest.mark.parametrize(
    "source_workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in (
            compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS
        )
    ),
)
def test_compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time(
    monkeypatch,
    source_workload,
) -> None:
    workload = _source_tree_contract_workload(
        source_workload,
        spec=(
            compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC.contract_builder_spec()
        ),
    )
    _assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call(
        monkeypatch,
        workload,
        expected_result=run_benchmark_workload_with_cpython(source_workload),
        expected_field_names=(
            compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC.expected_materialized_field_names(
                source_workload
            )
        ),
    )


@pytest.mark.parametrize(
    ("contract_surface", "source_workload"),
    compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS,
)
@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
def test_run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_contract_workloads(
    contract_surface,
    source_workload,
    import_name: str,
    adapter_name: str,
) -> None:
    workload = _source_tree_contract_workload(
        source_workload,
        spec=contract_surface.spec.contract_builder_spec(),
    )
    payload = workload_to_payload(workload)
    round_tripped = workload_from_payload(payload)

    contract_surface.assert_payload_round_trip(
        source_workload,
        payload,
        round_tripped,
    )

    probe = run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name=import_name,
        adapter_name=adapter_name,
    )

    assert probe["status"] == "measured"
    assert probe["median_ns"] > 0


@pytest.mark.parametrize(
    ("contract_surface", "source_workload"),
    compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS,
)
def test_compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing(
    contract_surface,
    source_workload,
) -> None:
    expected_build_calls = contract_surface.expected_build_calls(source_workload)
    expected_callback_call = contract_surface.expected_callback_call(source_workload)
    module = RecordingBenchmarkModule()
    callback = build_callable(
        module,
        "re",
        _source_tree_contract_workload(
            source_workload,
            spec=contract_surface.spec.contract_builder_spec(),
        ),
    )

    assert module.calls == expected_build_calls
    assert len(module.compiled_patterns) == 1
    assert callback() == contract_surface.expected_callback_result(source_workload)

    compiled_pattern = module.compiled_patterns[0]
    last_call = module.calls[-1]
    assert last_call[0] == expected_callback_call[0]
    assert last_call[1] is compiled_pattern
    assert last_call[2:] == expected_callback_call[1:]


@pytest.mark.parametrize(
    "source_workload",
    tuple(
        pytest.param(workload, id=workload.workload_id)
        for workload in (
            compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS
        )
    ),
)
def test_compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions(
    monkeypatch,
    source_workload,
) -> None:
    contract_surface = _compiled_pattern_module_helper_keyword_contract_surface(
        "keyword-error"
    )
    workload = _source_tree_contract_workload(
        source_workload,
        spec=(
            compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC.contract_builder_spec()
        ),
    )
    observed_field_names = _record_numeric_materialization_fields(monkeypatch)

    re.purge()
    try:
        callback = build_callable(re, "re", workload)
        assert observed_field_names == []

        with pytest.raises(TypeError) as expected_error:
            contract_surface.run_cpython_helper_workload(workload)
        with pytest.raises(TypeError) as observed_error:
            callback()

        assert observed_field_names == list(
            compiled_pattern_module_helper_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC.expected_materialized_field_names(
                source_workload
            )
        )
        assert str(observed_error.value) == str(expected_error.value)
    finally:
        re.purge()
