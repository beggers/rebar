from __future__ import annotations

from dataclasses import replace
from functools import cache
import inspect
import importlib
import pathlib
from types import SimpleNamespace

import pytest

from rebar_harness import benchmarks
from tests.benchmarks import benchmark_test_support as support
from tests.benchmarks import (
    collection_replacement_benchmark_anchor_support as collection_replacement_support,
)
from tests.benchmarks import (
    compiled_pattern_module_compile_benchmark_support as compiled_pattern_module_compile_support,
)
from tests.benchmarks import (
    compiled_pattern_module_helper_benchmark_support as compiled_pattern_module_helper_support,
)
from tests.benchmarks import (
    pattern_boundary_benchmark_anchor_support as pattern_boundary_support,
)
from tests.benchmarks import source_tree_benchmark_anchor_support as anchor_support
from tests.benchmarks.benchmark_test_support import (
    COMPILE_MATRIX_MANIFEST_PATH,
    REGRESSION_MATRIX_MANIFEST_PATH,
    _synthetic_manifest_loader,
    _synthetic_workload,
    _synthetic_workload_is_included,
    _synthetic_workload_signature,
    anchor_support_cache_guard,
    _build_compile_proxy_standard_benchmark_definitions,
    _assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call,
    _has_standard_benchmark_legacy_workloads,
    _has_standard_benchmark_special_unanchored_direct_parity_cases,
    _has_standard_benchmark_special_unanchored_workloads,
    _runs_standard_benchmark_callback_result_parity,
    compile_proxy_correctness_case_signature,
    compile_proxy_workload_signature,
    is_compile_proxy_workload,
    _expected_exception_instance,
    _record_numeric_materialization_fields,
    _write_test_manifest,
    synthetic_workload,
)
from tests.conftest import REPO_ROOT


def test_write_test_manifest_dedents_and_writes_utf8_text(tmp_path) -> None:
    manifest_path = _write_test_manifest(
        tmp_path,
        "sample_manifest.py",
        """\
            VALUE = "caf\u00e9"
        """,
    )

    assert manifest_path.read_text(encoding="utf-8") == 'VALUE = "caf\u00e9"\n'
    assert manifest_path.read_bytes() == 'VALUE = "caf\u00e9"\n'.encode("utf-8")


def test_expected_exception_instance_maps_supported_payloads() -> None:
    type_error = _expected_exception_instance(
        {
            "type": "TypeError",
            "message_substring": "type payload",
        }
    )
    value_error = _expected_exception_instance(
        {
            "type": "ValueError",
            "message_substring": "value payload",
        }
    )

    assert isinstance(type_error, TypeError)
    assert str(type_error) == "type payload"
    assert isinstance(value_error, ValueError)
    assert str(value_error) == "value payload"


def test_record_numeric_materialization_fields_collects_names_and_preserves_return_value(
    monkeypatch,
) -> None:
    original_materialize = benchmarks.materialize_numeric_workload_argument
    expected_value = original_materialize(
        {"type": "indexlike", "value": 7},
        field_name="kwargs.count",
    )
    observed_field_names = _record_numeric_materialization_fields(monkeypatch)

    observed_value = benchmarks.materialize_numeric_workload_argument(
        {"type": "indexlike", "value": 7},
        field_name="kwargs.count",
    )

    assert observed_field_names == ["kwargs.count"]
    assert type(observed_value) is type(expected_value)
    assert repr(observed_value) == repr(expected_value)
    assert observed_value.value == expected_value.value


def test_collection_replacement_keyword_kwargs_materialize_on_each_callback_call_success_path(
    monkeypatch,
) -> None:
    workload = synthetic_workload(
        manifest_id="collection-replacement-benchmark-support",
        workload_id="pattern-sub-count-indexlike-keyword-contract",
        operation="pattern.sub",
        pattern="abc",
        haystack="abcabcabc",
        replacement="x",
        kwargs={"count": {"type": "indexlike", "value": 2}},
        timing_scope="pattern-helper-call",
    )

    _assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call(
        monkeypatch,
        workload,
        expected_result="xxabc",
        expected_field_names=("kwargs.count",),
    )


def test_collection_replacement_keyword_kwargs_materialize_on_each_callback_call_type_error_path(
    monkeypatch,
) -> None:
    workload = synthetic_workload(
        manifest_id="collection-replacement-benchmark-support",
        workload_id="pattern-split-duplicate-maxsplit-keyword-contract",
        operation="pattern.split",
        pattern="abc",
        haystack="abcabc",
        maxsplit=1,
        kwargs={"maxsplit": {"type": "indexlike", "value": 1}},
        expected_exception={
            "type": "TypeError",
            "message_substring": "split() takes at most 2 arguments (3 given)",
        },
        timing_scope="pattern-helper-call",
    )

    _assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call(
        monkeypatch,
        workload,
        expected_result=None,
        expected_exception_message="split() takes at most 2 arguments (3 given)",
        expected_field_names=("maxsplit", "kwargs.maxsplit"),
    )


def test_manifest_workloads_resolve_and_cache_manifest_loads(
    monkeypatch,
    anchor_support_cache_guard: None,
) -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")
    workloads = (
        _synthetic_workload("anchored", ("shared",)),
        _synthetic_workload("unanchored", ("missing",), include=False),
    )
    load_calls: list[pathlib.Path] = []

    def _load_manifest(path: pathlib.Path) -> SimpleNamespace:
        load_calls.append(path)
        return _synthetic_manifest_loader(path, workloads=workloads)

    monkeypatch.setattr(support, "load_manifest", _load_manifest)

    assert support.manifest_workloads(manifest_path) == workloads
    assert support.selected_manifest_workloads(
        manifest_path,
        include_workload=_synthetic_workload_is_included,
    ) == (workloads[0],)
    assert support.live_manifest_workload(manifest_path, "anchored") is workloads[0]
    assert support.live_manifest_workloads(
        manifest_path,
        ("anchored", "unanchored"),
    ) == workloads
    assert load_calls == [manifest_path]


def test_manifest_workloads_resolve_string_paths_from_workloads_root(
    monkeypatch,
    anchor_support_cache_guard: None,
) -> None:
    manifest_name = "synthetic_boundary.py"
    workloads = (_synthetic_workload("anchored", ("shared",)),)
    resolved_paths: list[pathlib.Path] = []

    def _load_manifest(path: pathlib.Path) -> SimpleNamespace:
        resolved_paths.append(path)
        return _synthetic_manifest_loader(path, workloads=workloads)

    monkeypatch.setattr(support, "load_manifest", _load_manifest)

    assert support.selected_manifest_workloads(manifest_name) == workloads
    assert resolved_paths == [
        benchmarks.BENCHMARK_WORKLOADS_ROOT / manifest_name,
    ]


def test_clear_anchor_support_caches_resets_shared_and_source_tree_cached_helpers(
    monkeypatch,
    anchor_support_cache_guard: None,
) -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")
    workloads = (_synthetic_workload("anchored", ("shared",)),)
    manifest_load_calls: list[pathlib.Path] = []
    published_case_id_calls: list[object] = []
    published_cases_calls: list[str] = []
    published_cases = {"case-1": object()}

    def _load_manifest(path: pathlib.Path) -> SimpleNamespace:
        manifest_load_calls.append(path)
        return _synthetic_manifest_loader(path, workloads=workloads)

    @cache
    def _published_case_ids_by_signature(
        case_signature: object,
    ) -> dict[tuple[str, ...], tuple[str, ...]]:
        published_case_id_calls.append(case_signature)
        return {("shared",): ("case-1",)}

    @cache
    def _published_cases_by_id() -> dict[str, object]:
        published_cases_calls.append("called")
        return published_cases

    monkeypatch.setattr(support, "load_manifest", _load_manifest)
    monkeypatch.setattr(
        support,
        "published_case_ids_by_signature",
        _published_case_ids_by_signature,
    )
    monkeypatch.setattr(support, "published_cases_by_id", _published_cases_by_id)

    assert support.live_manifest_workload(manifest_path, "anchored") is workloads[0]
    assert support.published_case_ids_by_signature(
        _synthetic_workload_signature
    ) == {("shared",): ("case-1",)}
    assert support.published_cases_by_id() is published_cases
    assert manifest_load_calls == [manifest_path]
    assert published_case_id_calls == [_synthetic_workload_signature]
    assert published_cases_calls == ["called"]

    assert support.live_manifest_workload(manifest_path, "anchored") is workloads[0]
    assert support.published_case_ids_by_signature(
        _synthetic_workload_signature
    ) == {("shared",): ("case-1",)}
    assert support.published_cases_by_id() is published_cases
    assert manifest_load_calls == [manifest_path]
    assert published_case_id_calls == [_synthetic_workload_signature]
    assert published_cases_calls == ["called"]

    support._clear_anchor_support_caches()

    assert support.live_manifest_workload(manifest_path, "anchored") is workloads[0]
    assert support.published_case_ids_by_signature(
        _synthetic_workload_signature
    ) == {("shared",): ("case-1",)}
    assert support.published_cases_by_id() is published_cases
    assert manifest_load_calls == [manifest_path, manifest_path]
    assert published_case_id_calls == [
        _synthetic_workload_signature,
        _synthetic_workload_signature,
    ]
    assert published_cases_calls == ["called", "called"]


def test_source_tree_contract_manifest_payload_drops_fields_and_injects_metadata(
) -> None:
    source_workload = synthetic_workload(
        manifest_id="source-manifest",
        workload_id="module-sub-count-keyword-warm-str",
        operation="module.sub",
        pattern="abc",
        haystack="abcabcabc",
        replacement="x",
        kwargs={"count": {"type": "indexlike", "value": 2}},
        timing_scope="pattern-helper-call",
        warmup_iterations=7,
        sample_iterations=8,
        timed_samples=9,
        notes=["source note"],
        categories=["synthetic-category"],
        syntax_features=["synthetic-syntax"],
        smoke=True,
    )
    source_payload = benchmarks.workload_to_payload(source_workload)
    spec = support._SourceTreeContractBuilderSpec(
        manifest_id="contract-manifest",
        excluded_fields=frozenset(
            {
                "manifest_id",
                "workload_id",
                "warmup_iterations",
                "sample_iterations",
                "timed_samples",
                "notes",
            }
        ),
        timing_scope="module-helper-call",
        notes=("keeps helper invocation unresolved",),
    )

    payload = support._source_tree_contract_manifest_payload(
        source_workload,
        spec=spec,
    )

    assert payload["id"] == "module-sub-count-keyword-warm-str-contract"
    assert payload["pattern"] == source_payload["pattern"]
    assert payload["haystack"] == source_payload["haystack"]
    assert payload["replacement"] == source_payload["replacement"]
    assert payload["kwargs"] == source_payload["kwargs"]
    assert payload["categories"] == ["synthetic-category"]
    assert payload["syntax_features"] == ["synthetic-syntax"]
    assert payload["smoke"] is True
    assert payload["timing_scope"] == "module-helper-call"
    assert payload["notes"] == ["keeps helper invocation unresolved"]
    for field_name in spec.excluded_fields - {"notes"}:
        assert field_name not in payload


def test_source_tree_contract_workload_reconstructs_contract_workload_with_defaults(
) -> None:
    source_workload = synthetic_workload(
        manifest_id="source-manifest",
        workload_id="module-subn-count-keyword-purged-str",
        operation="module.subn",
        pattern="abc",
        haystack="abcabcabc",
        replacement="x",
        kwargs={"count": {"type": "indexlike", "value": 2}},
        timing_scope="pattern-helper-call",
        warmup_iterations=4,
        sample_iterations=5,
        timed_samples=6,
        categories=["source-category"],
        syntax_features=["source-syntax"],
        smoke=True,
    )
    source_payload = benchmarks.workload_to_payload(source_workload)
    spec = support._SourceTreeContractBuilderSpec(
        manifest_id="contract-manifest",
        excluded_fields=frozenset(
            {
                "manifest_id",
                "workload_id",
                "warmup_iterations",
                "sample_iterations",
                "timed_samples",
                "notes",
            }
        ),
        timing_scope="module-helper-call",
        notes=("contract workload",),
    )

    workload = support._source_tree_contract_workload(source_workload, spec=spec)
    payload = benchmarks.workload_to_payload(workload)

    assert payload["manifest_id"] == "contract-manifest"
    assert payload["workload_id"] == "module-subn-count-keyword-purged-str-contract"
    assert payload["pattern"] == source_payload["pattern"]
    assert payload["haystack"] == source_payload["haystack"]
    assert payload["replacement"] == source_payload["replacement"]
    assert payload["kwargs"] == source_payload["kwargs"]
    assert payload["warmup_iterations"] == 1
    assert payload["sample_iterations"] == 1
    assert payload["timed_samples"] == 1
    assert payload["categories"] == []
    assert payload["syntax_features"] == []
    assert payload["smoke"] is False
    assert payload["timing_scope"] == "module-helper-call"
    assert payload["notes"] == ["contract workload"]


def test_source_tree_contract_manifest_uses_manifest_defaults_and_contract_ids() -> None:
    source_workloads = (
        synthetic_workload(
            manifest_id="source-manifest",
            workload_id="first-workload",
            operation="module.findall",
            pattern="abc",
            haystack="abcabc",
        ),
        synthetic_workload(
            manifest_id="source-manifest",
            workload_id="second-workload",
            operation="module.sub",
            pattern="abc",
            haystack="abcabc",
            replacement="x",
        ),
    )
    spec = support._SourceTreeContractBuilderSpec(
        manifest_id="contract-manifest",
        excluded_fields=frozenset({"manifest_id", "workload_id"}),
        manifest_timed_samples=7,
    )

    manifest = support._source_tree_contract_manifest(source_workloads, spec=spec)

    assert manifest["schema_version"] == 1
    assert manifest["manifest_id"] == "contract-manifest"
    assert manifest["defaults"] == {
        "warmup_iterations": 1,
        "sample_iterations": 1,
        "timed_samples": 7,
    }
    assert [workload["id"] for workload in manifest["workloads"]] == [
        "first-workload-contract",
        "second-workload-contract",
    ]


def test_compiled_pattern_contract_shared_excluded_fields_stay_pinned() -> None:
    assert support.COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS == frozenset(
        {
            "manifest_id",
            "workload_id",
            "warmup_iterations",
            "sample_iterations",
            "timed_samples",
            "notes",
            "smoke",
        }
    )


@pytest.mark.parametrize(
    ("workload", "expected_calls"),
    (
        pytest.param(
            support.live_manifest_workload(
                "module_boundary.py",
                "module-search-literal-warm-hit-str-compiled-pattern",
            ),
            [("compile", "abc", 0)],
            id="warm",
        ),
        pytest.param(
            support.live_manifest_workload(
                "module_boundary.py",
                "module-fullmatch-literal-purged-hit-bytes-compiled-pattern",
            ),
            [("compile", b"abc", 0), ("purge",)],
            id="purged",
        ),
    ),
)
def test_compiled_pattern_contract_expected_build_calls_cover_warm_and_purged_modes(
    workload,
    expected_calls,
) -> None:
    assert support.compiled_pattern_contract_expected_build_calls(
        workload,
        label="support test",
    ) == expected_calls


def test_compiled_pattern_contract_expected_build_calls_rejects_unknown_cache_mode() -> None:
    workload = support.live_manifest_workload(
        "module_boundary.py",
        "module-search-literal-warm-hit-str-compiled-pattern",
    )
    mutated_workload = replace(workload, cache_mode="cold")

    with pytest.raises(
        AssertionError,
        match="unexpected compiled-pattern support test workload cache mode 'cold'",
    ):
        support.compiled_pattern_contract_expected_build_calls(
            mutated_workload,
            label="support test",
        )


def test_contract_source_workloads_follow_selector_order_on_synthetic_manifest_rows(
    monkeypatch,
    anchor_support_cache_guard: None,
) -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")
    workloads = (
        _synthetic_workload("first", ("shared", "first")),
        _synthetic_workload("second", ("shared", "second")),
        _synthetic_workload("third", ("shared", "third")),
    )

    monkeypatch.setattr(
        support,
        "load_manifest",
        lambda path: _synthetic_manifest_loader(path, workloads=workloads),
    )

    source_workloads = support._contract_source_workloads(
        manifest_path=manifest_path,
        include_workload_selectors=(
            lambda workload: workload.workload_id in {"second", "third"},
            lambda workload: workload.workload_id == "first",
        ),
        expected_source_workload_ids=("second", "third", "first"),
        drift_message="synthetic workloads drifted",
    )

    assert tuple(workload.workload_id for workload in source_workloads) == (
        "second",
        "third",
        "first",
    )


def test_contract_source_workloads_detect_drift_on_synthetic_manifest_rows(
    monkeypatch,
    anchor_support_cache_guard: None,
) -> None:
    workloads = (
        _synthetic_workload("first", ("shared", "first")),
        _synthetic_workload("second", ("shared", "second")),
    )

    monkeypatch.setattr(
        support,
        "load_manifest",
        lambda path: _synthetic_manifest_loader(path, workloads=workloads),
    )

    with pytest.raises(AssertionError, match="synthetic workloads drifted"):
        support._contract_source_workloads(
            manifest_path=pathlib.Path("synthetic_boundary.py"),
            include_workload_selectors=(
                lambda workload: workload.workload_id == "first",
            ),
            expected_source_workload_ids=("second",),
            drift_message="synthetic workloads drifted",
        )


def _synthetic_case(
    *,
    operation: str,
    pattern: str | bytes | None,
    args: tuple[object, ...] = (),
    flags: int | None = None,
    text_model: str | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        operation=operation,
        pattern=pattern,
        args=args,
        flags=flags,
        text_model=text_model,
        pattern_payload=lambda: pattern,
    )


def test_compile_proxy_correctness_case_signature_uses_compile_shape() -> None:
    case = _synthetic_case(
        operation="compile",
        pattern=None,
        args=(b"literal",),
        flags=None,
        text_model=None,
    )

    assert compile_proxy_correctness_case_signature(case) == (
        "module.compile",
        b"literal",
        (),
        (),
        0,
        "str",
    )


def test_compile_proxy_workload_signature_uses_compile_shape() -> None:
    workload = synthetic_workload(
        manifest_id="compile-proxy-benchmark-support",
        workload_id="module-compile-literal",
        operation="module.compile",
        pattern="literal",
        flags=8,
        text_model="bytes",
    )

    assert compile_proxy_workload_signature(workload) == (
        "module.compile",
        b"literal",
        (),
        (),
        8,
        "bytes",
    )


def test_is_compile_proxy_workload_includes_compile_operations_only() -> None:
    assert is_compile_proxy_workload(
        synthetic_workload(
            manifest_id="compile-proxy-benchmark-support",
            workload_id="compile-literal",
            operation="compile",
            pattern="literal",
            flags=0,
            text_model="str",
        )
    )
    assert is_compile_proxy_workload(
        synthetic_workload(
            manifest_id="compile-proxy-benchmark-support",
            workload_id="module-compile-literal",
            operation="module.compile",
            pattern="literal",
            flags=0,
            text_model="str",
        )
    )
    assert not is_compile_proxy_workload(
        synthetic_workload(
            manifest_id="compile-proxy-benchmark-support",
            workload_id="module-search-literal",
            operation="module.search",
            pattern="literal",
            flags=0,
            text_model="str",
        )
    )


def test_compile_proxy_standard_definition_export_is_direct_global_cached_and_support_built(
) -> None:
    first_export = getattr(support, "COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS")
    second_export = getattr(support, "COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS")

    assert first_export is second_export
    assert first_export is _build_compile_proxy_standard_benchmark_definitions()
    assert len(first_export) == 1
    assert first_export[0].name == "compile-proxy"
    assert vars(support)["COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS"] is first_export


def test_compile_proxy_standard_definition_preserves_manifest_order_and_anchor_mapping(
) -> None:
    definition = support.COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS[0]

    assert COMPILE_MATRIX_MANIFEST_PATH == (
        REPO_ROOT / "benchmarks" / "workloads" / "compile_matrix.py"
    )
    assert REGRESSION_MATRIX_MANIFEST_PATH == (
        REPO_ROOT / "benchmarks" / "workloads" / "regression_matrix.py"
    )
    assert definition.manifest_paths == (
        COMPILE_MATRIX_MANIFEST_PATH,
        REGRESSION_MATRIX_MANIFEST_PATH,
    )
    assert definition.expected_anchor_case_ids == (
        support._definition_anchor_expectations(
            COMPILE_MATRIX_MANIFEST_PATH,
            {
                "compile-inline-locale-bytes-warm": (
                    "bytes-inline-locale-flag-success",
                ),
                "compile-lookbehind-cold": (
                    "str-fixed-width-lookbehind-success",
                ),
                "compile-character-class-ignorecase-warm": (
                    "str-character-class-ignorecase-success",
                ),
                "compile-possessive-quantifier-cold": (
                    "str-possessive-quantifier-success",
                ),
                "compile-atomic-group-purged": (
                    "str-atomic-group-success",
                ),
                "compile-parser-stress-cold": (
                    "str-parser-stress-compile-proxy-success",
                ),
            },
        )
        | support._definition_anchor_expectations(
            REGRESSION_MATRIX_MANIFEST_PATH,
            {
                "regression-parser-atomic-lookbehind-cold": (
                    "str-parser-stress-compile-proxy-success",
                ),
                "regression-parser-bytes-backreference-purged": (
                    "bytes-named-backreference-compile-proxy-success",
                ),
                "regression-module-compile-verbose-purged": (
                    "workflow-compile-str-verbose-regression",
                ),
                "regression-module-compile-multiline-purged": (
                    "workflow-compile-str-multiline-regression",
                ),
                "regression-module-compile-multiline-purged-bytes": (
                    "workflow-compile-bytes-multiline-regression",
                ),
                "regression-module-compile-verbose-purged-bytes": (
                    "workflow-compile-bytes-verbose-regression",
                ),
            },
        )
    )


def test_compile_proxy_standard_definition_reuses_compile_proxy_helper_functions() -> None:
    definition = support.COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS[0]

    assert definition.include_workload is support.is_compile_proxy_workload
    assert (
        definition.correctness_case_signature
        is support.compile_proxy_correctness_case_signature
    )
    assert definition.workload_signature is support.compile_proxy_workload_signature


def test_standard_benchmark_definitions_are_direct_support_owned_global_tuple() -> None:
    assert isinstance(support.STANDARD_BENCHMARK_DEFINITIONS, tuple)
    assert tuple(
        parameter.values[0]
        for parameter in support._standard_benchmark_definition_params(
            include_definition=lambda _: True
        )
    ) == support.STANDARD_BENCHMARK_DEFINITIONS

    support_source = inspect.getsource(support)
    assert "STANDARD_BENCHMARK_DEFINITIONS = (" in support_source
    assert "_build_standard_benchmark_definitions" not in support_source
    assert "for definition in STANDARD_BENCHMARK_DEFINITIONS" in support_source


@pytest.mark.parametrize(
    ("owner_definitions", "preceding_definition_name", "following_definition_name"),
    (
        pytest.param(
            support.COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS,
            None,
            "collection-replacement-module-positional-indexlike",
            id="compile-proxy-before-collection-replacement",
        ),
        pytest.param(
            collection_replacement_support.COLLECTION_REPLACEMENT_STANDARD_BENCHMARK_DEFINITIONS,
            "compile-proxy",
            "module-workflow-keyword-flags",
            id="collection-replacement-after-compile-proxy",
        ),
        pytest.param(
            anchor_support.MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS,
            "collection-replacement-grouped-callable-replacement",
            "module-workflow-compiled-pattern-module-compile-literal-success",
            id="module-workflow-keyword-after-collection-replacement",
        ),
        pytest.param(
            compiled_pattern_module_compile_support.COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS,
            "module-workflow-keyword-errors",
            "module-workflow-compiled-pattern-literal-success",
            id="compiled-pattern-module-compile-after-module-workflow-keyword",
        ),
        pytest.param(
            compiled_pattern_module_helper_support.COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS,
            "module-workflow-compiled-pattern-module-compile-flags-ignorecase-keyword-rejection-named-group",
            "pattern-window-positional-indexlike",
            id="compiled-pattern-module-helper-after-module-compile",
        ),
        pytest.param(
            pattern_boundary_support.PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS,
            "module-workflow-compiled-pattern-wrong-text-model",
            "optional-group-conditional",
            id="pattern-boundary-after-compiled-pattern-helper",
        ),
        pytest.param(
            anchor_support.SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS,
            "pattern-boundary-wrong-text-model",
            None,
            id="source-tree-standard-after-pattern-boundary",
        ),
    ),
)
def test_standard_benchmark_definitions_keep_owner_blocks_in_order(
    owner_definitions: tuple[object, ...],
    preceding_definition_name: str | None,
    following_definition_name: str | None,
) -> None:
    standard_definitions = support.STANDARD_BENCHMARK_DEFINITIONS
    standard_names = tuple(definition.name for definition in standard_definitions)
    owner_names = tuple(definition.name for definition in owner_definitions)

    first_owner_index = standard_names.index(owner_names[0])
    if preceding_definition_name is None:
        assert first_owner_index == 0
    else:
        assert standard_names[first_owner_index - 1] == preceding_definition_name

    standard_owner_slice = standard_definitions[
        first_owner_index : first_owner_index + len(owner_definitions)
    ]
    assert tuple(definition.name for definition in standard_owner_slice) == owner_names
    assert standard_owner_slice == owner_definitions
    assert all(
        standard_definition is owner_definition
        for standard_definition, owner_definition in zip(
            standard_owner_slice,
            owner_definitions,
            strict=True,
        )
    )

    next_index = first_owner_index + len(owner_definitions)
    if following_definition_name is None:
        assert next_index == len(standard_names)
    else:
        assert standard_names[next_index] == following_definition_name


def test_standard_benchmark_definition_params_preserve_names_and_filters() -> None:
    legacy_definitions = tuple(
        parameter.values[0]
        for parameter in support._standard_benchmark_definition_params(
            include_definition=_has_standard_benchmark_legacy_workloads
        )
    )
    callback_definitions = tuple(
        parameter.values[0]
        for parameter in support._standard_benchmark_definition_params(
            include_definition=_runs_standard_benchmark_callback_result_parity
        )
    )
    special_unanchored_definitions = tuple(
        parameter.values[0]
        for parameter in support._standard_benchmark_definition_params(
            include_definition=_has_standard_benchmark_special_unanchored_workloads
        )
    )
    direct_parity_definitions = tuple(
        parameter.values[0]
        for parameter in support._standard_benchmark_definition_params(
            include_definition=(
                _has_standard_benchmark_special_unanchored_direct_parity_cases
            )
        )
    )

    assert all(definition.expected_legacy_workload_ids for definition in legacy_definitions)
    assert all(definition.run_callback_result_parity for definition in callback_definitions)
    assert all(
        definition.expected_special_unanchored_workload_ids
        for definition in special_unanchored_definitions
    )
    assert all(
        definition.expected_special_unanchored_workload_ids
        and definition.direct_parity_supplemental_cases
        for definition in direct_parity_definitions
    )
    assert tuple(
        support._standard_benchmark_definition_id(definition)
        for definition in support.STANDARD_BENCHMARK_DEFINITIONS
    ) == tuple(definition.name for definition in support.STANDARD_BENCHMARK_DEFINITIONS)


def test_standard_benchmark_manifest_params_preserve_definition_and_manifest_order() -> None:
    manifest_params = support._standard_benchmark_manifest_params()

    assert tuple(
        (parameter.values[0].name, parameter.values[1].name)
        for parameter in manifest_params
    ) == tuple(
        (definition.name, manifest_path.name)
        for definition in support.STANDARD_BENCHMARK_DEFINITIONS
        for manifest_path in definition.manifest_paths
    )


def test_standard_benchmark_special_unanchored_result_parity_params_preserve_order() -> None:
    params = support._standard_benchmark_special_unanchored_result_parity_params()

    assert tuple(
        (parameter.values[0].name, parameter.values[1])
        for parameter in params
    ) == tuple(
        (definition.name, workload_id)
        for definition in support.STANDARD_BENCHMARK_DEFINITIONS
        if definition.run_special_unanchored_result_parity
        for workload_id in definition.expected_special_unanchored_workload_ids
    )


def test_source_tree_combined_suite_imports_standard_benchmark_definitions_from_support(
) -> None:
    combined_suite = importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )

    assert (
        combined_suite.STANDARD_BENCHMARK_DEFINITIONS
        is support.STANDARD_BENCHMARK_DEFINITIONS
    )
    combined_source = inspect.getsource(combined_suite)
    assert "from tests.benchmarks.benchmark_test_support import (" in combined_source
