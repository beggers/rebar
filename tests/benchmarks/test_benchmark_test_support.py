from __future__ import annotations

import ast
from dataclasses import replace
from functools import cache
import importlib
import pathlib
import re
from types import SimpleNamespace

import pytest

from rebar_harness import benchmarks
from tests.benchmarks import benchmark_test_support as support
from tests.benchmarks import (
    collection_replacement_benchmark_anchor_support as collection_replacement_support,
)
from tests.benchmarks import source_tree_benchmark_anchor_support as anchor_support
from tests.benchmarks import (
    test_benchmark_publication_runtime_contracts as publication_runtime_contracts,
)
from tests.benchmarks.benchmark_test_support import (
    MODULE_BOUNDARY_MANIFEST_PATH,
    COMPILE_MATRIX_MANIFEST_PATH,
    CONDITIONAL_GROUP_EXISTS_BOUNDARY_MANIFEST_PATH,
    EXACT_REPEAT_MANIFEST_PATH,
    GROUPED_ALTERNATION_MANIFEST_PATH,
    GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,
    NESTED_GROUP_MANIFEST_PATH,
    NESTED_GROUP_CALLABLE_REPLACEMENT_BOUNDARY_MANIFEST_PATH,
    NESTED_GROUP_REPLACEMENT_MANIFEST_PATH,
    OPEN_ENDED_MANIFEST_PATH,
    OPTIONAL_GROUP_MANIFEST_PATH,
    RANGED_REPEAT_MANIFEST_PATH,
    REGRESSION_MATRIX_MANIFEST_PATH,
    RecordingBenchmarkCompiledPattern,
    RecordingBenchmarkModule,
    _module_pattern_case,
    _owner_definition_manifest_path_names,
    _parsed_module_ast,
    _synthetic_manifest_loader,
    _synthetic_workload,
    _synthetic_workload_is_included,
    _synthetic_workload_signature,
    anchor_support_cache_guard,
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
from tests.conftest import REPO_ROOT, records_by_string_id
from tests.python.fixture_parity_support import IndexLike


def _module_function_definition(module: object, function_name: str) -> ast.FunctionDef:
    return next(
        node
        for node in _parsed_module_ast(module).body
        if isinstance(node, ast.FunctionDef) and node.name == function_name
    )


def _module_class_definition(module: object, class_name: str) -> ast.ClassDef:
    return next(
        node
        for node in _parsed_module_ast(module).body
        if isinstance(node, ast.ClassDef) and node.name == class_name
    )


def _class_method_definition(
    class_definition: ast.ClassDef,
    method_name: str,
) -> ast.FunctionDef:
    return next(
        node
        for node in class_definition.body
        if isinstance(node, ast.FunctionDef) and node.name == method_name
    )


def _module_imported_names(module: object, imported_module: str) -> frozenset[str]:
    return frozenset(
        alias.name
        for node in _parsed_module_ast(module).body
        if isinstance(node, ast.ImportFrom) and node.module == imported_module
        for alias in node.names
    )


def _module_import_targets(module: object) -> frozenset[str]:
    return _ast_import_targets(_parsed_module_ast(module))


def _ast_import_targets(module_ast: ast.Module) -> frozenset[str]:
    targets: set[str] = set()

    for node in module_ast.body:
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            targets.add(node.module)
        elif isinstance(node, ast.Import):
            targets.update(alias.name for alias in node.names)

    return frozenset(targets)


def _top_level_benchmark_support_alias_pairs(
    module: object,
    attribute_names: frozenset[str],
) -> frozenset[tuple[str, str]]:
    alias_pairs: set[tuple[str, str]] = set()

    for node in _parsed_module_ast(module).body:
        if isinstance(node, ast.ImportFrom):
            if node.module != "tests.benchmarks.benchmark_test_support":
                continue
            alias_pairs.update(
                (alias.name, alias.asname)
                for alias in node.names
                if alias.name in attribute_names and alias.asname is not None
            )
            continue

        if isinstance(node, ast.Assign):
            targets = tuple(
                target.id for target in node.targets if isinstance(target, ast.Name)
            )
            value = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            targets = (node.target.id,)
            value = node.value
        else:
            continue

        if (
            isinstance(value, ast.Attribute)
            and isinstance(value.value, ast.Name)
            and value.value.id == "benchmark_test_support"
            and value.attr in attribute_names
        ):
            alias_pairs.update((value.attr, target_name) for target_name in targets)

    return frozenset(alias_pairs)


@cache
def _benchmark_support_import_targets_by_path(
) -> tuple[tuple[pathlib.Path, frozenset[str]], ...]:
    benchmark_root = REPO_ROOT / "tests" / "benchmarks"
    return tuple(
        (
            path.relative_to(REPO_ROOT),
            _ast_import_targets(
                ast.parse(
                    path.read_text(encoding="utf-8"),
                    filename=str(path),
                )
            ),
        )
        for path in sorted(benchmark_root.glob("*.py"))
    )


def _assert_deleted_benchmark_module_stays_absent(
    *,
    deleted_module_name: str,
    deleted_path: pathlib.Path,
) -> None:
    assert not deleted_path.exists()

    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(deleted_module_name)

    offending_paths = tuple(
        path
        for path, import_targets in _benchmark_support_import_targets_by_path()
        if deleted_module_name in import_targets
    )
    assert offending_paths == ()


def _compiled_pattern_module_helper_manifest_id(operation: str) -> str:
    if operation in {"module.search", "module.match", "module.fullmatch"}:
        return "module-boundary"
    return "collection-replacement-boundary"


def _module_assignment(module: object, name: str) -> ast.Assign:
    return next(
        node
        for node in _parsed_module_ast(module).body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == name
            for target in node.targets
        )
    )


def _assignment_target_name(assignment: ast.Assign) -> str:
    return next(
        target.id
        for target in assignment.targets
        if isinstance(target, ast.Name)
    )


def _inline_standard_definition_assignments(
    module: object,
) -> tuple[ast.Assign, ...]:
    return tuple(
        node
        for node in _parsed_module_ast(module).body
        if isinstance(node, ast.Assign)
        and _assignment_target_name(node).endswith("_STANDARD_BENCHMARK_DEFINITIONS")
        and isinstance(node.value, ast.Tuple)
        and all(isinstance(element, ast.Call) for element in node.value.elts)
    )


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
    source_tree_live_manifest_calls: list[tuple[pathlib.Path, tuple[str, ...]]] = []
    published_cases = {"case-1": object()}
    source_tree_workloads = (_synthetic_workload("source-tree-anchored", ("bytes",)),)

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

    def _live_manifest_workloads(
        manifest_path: pathlib.Path,
        workload_ids: tuple[str, ...],
    ) -> tuple[object, ...]:
        source_tree_live_manifest_calls.append((manifest_path, workload_ids))
        return source_tree_workloads

    monkeypatch.setattr(support, "load_manifest", _load_manifest)
    monkeypatch.setattr(
        support,
        "published_case_ids_by_signature",
        _published_case_ids_by_signature,
    )
    monkeypatch.setattr(support, "published_cases_by_id", _published_cases_by_id)
    monkeypatch.setattr(
        anchor_support,
        "live_manifest_workloads",
        _live_manifest_workloads,
    )

    support._clear_anchor_support_caches()

    assert support.live_manifest_workload(manifest_path, "anchored") is workloads[0]
    assert support.published_case_ids_by_signature(
        _synthetic_workload_signature
    ) == {("shared",): ("case-1",)}
    assert support.published_cases_by_id() is published_cases
    assert (
        anchor_support._conditional_group_exists_alternation_callable_bytes_workloads()
        == source_tree_workloads
    )
    assert manifest_load_calls == [manifest_path]
    assert published_case_id_calls == [_synthetic_workload_signature]
    assert published_cases_calls == ["called"]
    assert source_tree_live_manifest_calls == [
        (
            benchmarks.BENCHMARK_WORKLOADS_ROOT
            / "conditional_group_exists_boundary.py",
            anchor_support.CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS,
        )
    ]

    assert support.live_manifest_workload(manifest_path, "anchored") is workloads[0]
    assert support.published_case_ids_by_signature(
        _synthetic_workload_signature
    ) == {("shared",): ("case-1",)}
    assert support.published_cases_by_id() is published_cases
    assert (
        anchor_support._conditional_group_exists_alternation_callable_bytes_workloads()
        == source_tree_workloads
    )
    assert manifest_load_calls == [manifest_path]
    assert published_case_id_calls == [_synthetic_workload_signature]
    assert published_cases_calls == ["called"]
    assert source_tree_live_manifest_calls == [
        (
            benchmarks.BENCHMARK_WORKLOADS_ROOT
            / "conditional_group_exists_boundary.py",
            anchor_support.CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS,
        )
    ]

    support._clear_anchor_support_caches()

    assert support.live_manifest_workload(manifest_path, "anchored") is workloads[0]
    assert support.published_case_ids_by_signature(
        _synthetic_workload_signature
    ) == {("shared",): ("case-1",)}
    assert support.published_cases_by_id() is published_cases
    assert (
        anchor_support._conditional_group_exists_alternation_callable_bytes_workloads()
        == source_tree_workloads
    )
    assert manifest_load_calls == [manifest_path, manifest_path]
    assert published_case_id_calls == [
        _synthetic_workload_signature,
        _synthetic_workload_signature,
    ]
    assert published_cases_calls == ["called", "called"]
    assert source_tree_live_manifest_calls == [
        (
            benchmarks.BENCHMARK_WORKLOADS_ROOT
            / "conditional_group_exists_boundary.py",
            anchor_support.CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS,
        ),
        (
            benchmarks.BENCHMARK_WORKLOADS_ROOT
            / "conditional_group_exists_boundary.py",
            anchor_support.CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS,
        ),
    ]


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


def test_compile_proxy_standard_definition_export_is_direct_global(
) -> None:
    first_export = getattr(support, "COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS")
    second_export = getattr(support, "COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS")

    assert first_export is second_export
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

    support_ast = _parsed_module_ast(support)
    definitions_assignment = next(
        node
        for node in support_ast.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name)
            and target.id == "STANDARD_BENCHMARK_DEFINITIONS"
            for target in node.targets
        )
    )

    assert isinstance(definitions_assignment.value, ast.Tuple)
    assert not any(
        isinstance(node, ast.FunctionDef)
        and node.name == "_build_standard_benchmark_definitions"
        for node in support_ast.body
    )
    assert any(
        isinstance(node, ast.comprehension)
        and isinstance(node.iter, ast.Name)
        and node.iter.id == "STANDARD_BENCHMARK_DEFINITIONS"
        for node in ast.walk(
            _module_function_definition(
                support,
                "_standard_benchmark_definition_params",
            )
        )
    )


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
            support.MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS,
            "collection-replacement-grouped-callable-replacement",
            "module-workflow-compiled-pattern-module-compile-literal-success",
            id="module-workflow-keyword-after-collection-replacement",
        ),
        pytest.param(
            support.COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS,
            "module-workflow-keyword-errors",
            "module-workflow-compiled-pattern-literal-success",
            id="compiled-pattern-module-compile-after-module-workflow-keyword",
        ),
        pytest.param(
            support.COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS,
            "module-workflow-compiled-pattern-module-compile-flags-ignorecase-keyword-rejection-named-group",
            "pattern-window-positional-indexlike",
            id="compiled-pattern-module-helper-after-module-compile",
        ),
        pytest.param(
            support.PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS,
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


def test_compiled_pattern_module_compile_standard_benchmark_definitions_are_support_owned_and_wrapper_free(
) -> None:
    expected_definitions = tuple(
        owner_spec.anchor_definition()
        for owner_spec in (
            *support._COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS,
            *support._COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS,
        )
    )

    first_export = getattr(
        support,
        "COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS",
    )
    second_export = getattr(
        support,
        "COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS",
    )

    assert first_export is second_export
    assert (
        support._build_compiled_pattern_module_compile_standard_benchmark_definitions()
        == first_export
    )
    assert first_export == expected_definitions
    assert first_export is not expected_definitions
    assert tuple(definition.name for definition in first_export) == (
        "module-workflow-compiled-pattern-module-compile-literal-success",
        "module-workflow-compiled-pattern-module-compile-named-group-success",
        "module-workflow-compiled-pattern-module-compile-flags-int-zero-keyword",
        "module-workflow-compiled-pattern-module-compile-flags-int-zero-keyword-named-group",
        "module-workflow-compiled-pattern-module-compile-flags-bool-false-keyword",
        "module-workflow-compiled-pattern-module-compile-flags-bool-false-keyword-named-group",
        "module-workflow-compiled-pattern-module-compile-flags-ignorecase-keyword-rejection",
        "module-workflow-compiled-pattern-module-compile-flags-ignorecase-keyword-rejection-named-group",
    )
    assert (
        vars(support)[
            "COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS"
        ]
        is first_export
    )

    definition_names, _ = support.top_level_module_definition_and_assignment_names(
        support
    )
    assert "_standard_benchmark_anchor_contract_definition" not in definition_names

    builder_definition = _module_function_definition(
        support,
        "_build_compiled_pattern_module_compile_standard_benchmark_definitions",
    )
    assert any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "owner_spec"
        and node.func.attr == "anchor_definition"
        for node in ast.walk(builder_definition)
    )
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_standard_benchmark_anchor_contract_definition"
        for node in ast.walk(builder_definition)
    )

    for class_name in (
        "_CompiledPatternModuleCompileSuccessOwnerSpec",
        "_CompiledPatternModuleCompileKeywordOwnerSpec",
    ):
        anchor_definition = _class_method_definition(
            _module_class_definition(
                support,
                class_name,
            ),
            "anchor_definition",
        )
        assert any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "StandardBenchmarkAnchorContractDefinition"
            for node in ast.walk(anchor_definition)
        )


def test_module_keyword_flags_workload_stays_pinned() -> None:
    workload = synthetic_workload(
        manifest_id="module-pattern-boundary",
        workload_id="module-search-flags-keyword",
        operation="module.search",
        haystack="zabc",
        kwargs={"flags": {"type": "indexlike", "value": 2}},
        flags=2,
    )
    case = _module_pattern_case(
        helper="search",
        operation="module_call",
        args=("zabc",),
        kwargs={"flags": IndexLike(2)},
        flags=2,
    )

    assert support._is_module_workflow_keyword_flags_workload(workload)
    assert support._module_workflow_keyword_workload_args(workload) == ("zabc",)
    assert support._module_workflow_keyword_workload_signature(workload) == (
        "module.search",
        "abc",
        ("zabc",),
        (("flags", "indexlike", 2),),
        2,
        "str",
    )
    assert support._module_workflow_keyword_correctness_case_signature(case) == (
        "module.search",
        "abc",
        ("zabc",),
        (("flags", "indexlike", 2),),
        2,
        "str",
    )


def test_module_keyword_error_workload_stays_pinned() -> None:
    workload = synthetic_workload(
        manifest_id="module-pattern-boundary",
        workload_id="module-search-duplicate-flags-keyword",
        operation="module.search",
        haystack="zabc",
        kwargs={"flags": {"type": "indexlike", "value": 4}},
        expected_exception={
            "type": "TypeError",
            "message_substring": "multiple values for argument 'flags'",
        },
        flags=4,
    )

    assert support._is_module_workflow_keyword_error_workload(workload)
    assert support._module_workflow_keyword_workload_args(workload) == ("zabc", 4)
    assert support._module_workflow_keyword_workload_signature(workload) == (
        "module.search",
        "abc",
        ("zabc", 4),
        (("flags", "indexlike", 4),),
        4,
        "str",
    )


def test_module_workflow_keyword_standard_definitions_export_stays_owned_by_support(
) -> None:
    owner_definitions = support.MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS
    definition_names = tuple(definition.name for definition in owner_definitions)
    standard_definitions = {
        definition.name: definition
        for definition in support.STANDARD_BENCHMARK_DEFINITIONS
        if definition.name in definition_names
    }

    assert definition_names == (
        "module-workflow-keyword-flags",
        "module-workflow-keyword-errors",
    )
    assert tuple(standard_definitions) == definition_names
    for definition in owner_definitions:
        assert standard_definitions[definition.name] is definition


def test_benchmark_test_support_module_keyword_definition_references_owner_manifest_path_constant(
) -> None:
    assert _owner_definition_manifest_path_names(
        _module_assignment(
            support,
            "MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS",
        )
    ) == (
        ("MODULE_BOUNDARY_MANIFEST_PATH",),
        ("MODULE_BOUNDARY_MANIFEST_PATH",),
    )


def test_module_workflow_keyword_definition_exports_reuse_owner_manifest_path_constant(
) -> None:
    assert tuple(
        definition.manifest_paths[0]
        for definition in support.MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS
    ) == (
        MODULE_BOUNDARY_MANIFEST_PATH,
        MODULE_BOUNDARY_MANIFEST_PATH,
    )


def test_inline_standard_definition_exports_reuse_named_manifest_path_constants(
) -> None:
    assignment_nodes = _inline_standard_definition_assignments(support)
    assignment_names = {
        _assignment_target_name(assignment)
        for assignment in assignment_nodes
    }

    assert {
        "COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS",
        "MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS",
        "COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS",
        "PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS",
    }.issubset(assignment_names)

    for assignment in assignment_nodes:
        assignment_name = _assignment_target_name(assignment)
        manifest_path_name_groups = _owner_definition_manifest_path_names(assignment)
        assert all(
            manifest_path_names
            and all(
                manifest_path_name.endswith("_MANIFEST_PATH")
                for manifest_path_name in manifest_path_names
            )
            for manifest_path_names in manifest_path_name_groups
        )
        assert tuple(
            definition.manifest_paths
            for definition in getattr(support, assignment_name)
        ) == tuple(
            tuple(
                getattr(support, manifest_path_name)
                for manifest_path_name in manifest_path_names
            )
            for manifest_path_names in manifest_path_name_groups
        )


@pytest.mark.parametrize(
    ("module_name", "module_constant_name"),
    (
        pytest.param(
            "tests.benchmarks.source_tree_benchmark_anchor_support",
            "MODULE_BOUNDARY_MANIFEST_PATH",
            id="source-tree-support",
        ),
        pytest.param(
            "tests.benchmarks.test_source_tree_benchmark_anchor_support",
            "SHARED_MODULE_BOUNDARY_MANIFEST_PATH",
            id="source-tree-contract-suite",
        ),
        pytest.param(
            "tests.benchmarks.test_source_tree_combined_boundary_benchmarks",
            "COMPILED_PATTERN_MODULE_COMPILE_MANIFEST_PATH",
            id="source-tree-combined-suite",
        ),
    ),
)
def test_shared_module_boundary_manifest_path_consumers_reuse_support_constant_by_identity(
    module_name: str,
    module_constant_name: str,
) -> None:
    module = importlib.import_module(module_name)
    _, assignment_names = support.top_level_module_definition_and_assignment_names(
        module
    )

    assert "MODULE_BOUNDARY_MANIFEST_PATH" in _module_imported_names(
        module,
        "tests.benchmarks.benchmark_test_support",
    )
    assert module_constant_name not in assignment_names
    assert getattr(module, module_constant_name) is MODULE_BOUNDARY_MANIFEST_PATH


@pytest.mark.parametrize(
    "manifest_path_name",
    (
        "OPTIONAL_GROUP_MANIFEST_PATH",
        "NESTED_GROUP_MANIFEST_PATH",
        "EXACT_REPEAT_MANIFEST_PATH",
        "RANGED_REPEAT_MANIFEST_PATH",
        "GROUPED_ALTERNATION_MANIFEST_PATH",
        "GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH",
        "NESTED_GROUP_REPLACEMENT_MANIFEST_PATH",
        "OPEN_ENDED_MANIFEST_PATH",
    ),
)
def test_source_tree_manifest_path_consumers_reuse_support_constants_by_identity(
    manifest_path_name: str,
) -> None:
    _, assignment_names = support.top_level_module_definition_and_assignment_names(
        anchor_support
    )

    assert manifest_path_name in _module_imported_names(
        anchor_support,
        "tests.benchmarks.benchmark_test_support",
    )
    assert manifest_path_name not in assignment_names
    assert getattr(anchor_support, manifest_path_name) is getattr(
        support,
        manifest_path_name,
    )


def test_shared_source_tree_manifest_path_constants_point_to_current_workload_files() -> None:
    assert (
        OPTIONAL_GROUP_MANIFEST_PATH,
        NESTED_GROUP_MANIFEST_PATH,
        EXACT_REPEAT_MANIFEST_PATH,
        RANGED_REPEAT_MANIFEST_PATH,
        GROUPED_ALTERNATION_MANIFEST_PATH,
        GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,
        NESTED_GROUP_REPLACEMENT_MANIFEST_PATH,
        OPEN_ENDED_MANIFEST_PATH,
    ) == (
        REPO_ROOT / "benchmarks" / "workloads" / "optional_group_boundary.py",
        REPO_ROOT / "benchmarks" / "workloads" / "nested_group_boundary.py",
        REPO_ROOT
        / "benchmarks"
        / "workloads"
        / "exact_repeat_quantified_group_boundary.py",
        REPO_ROOT
        / "benchmarks"
        / "workloads"
        / "ranged_repeat_quantified_group_boundary.py",
        REPO_ROOT / "benchmarks" / "workloads" / "grouped_alternation_boundary.py",
        REPO_ROOT
        / "benchmarks"
        / "workloads"
        / "grouped_alternation_replacement_boundary.py",
        REPO_ROOT / "benchmarks" / "workloads" / "nested_group_replacement_boundary.py",
        REPO_ROOT
        / "benchmarks"
        / "workloads"
        / "open_ended_quantified_group_boundary.py",
    )


@pytest.mark.parametrize(
    "manifest_path_name",
    (
        "CONDITIONAL_GROUP_EXISTS_BOUNDARY_MANIFEST_PATH",
        "NESTED_GROUP_CALLABLE_REPLACEMENT_BOUNDARY_MANIFEST_PATH",
    ),
)
def test_publication_runtime_manifest_path_consumers_reuse_support_constants_by_identity(
    manifest_path_name: str,
) -> None:
    _, assignment_names = support.top_level_module_definition_and_assignment_names(
        publication_runtime_contracts
    )

    assert manifest_path_name in _module_imported_names(
        publication_runtime_contracts,
        "tests.benchmarks.benchmark_test_support",
    )
    assert manifest_path_name not in assignment_names
    assert getattr(publication_runtime_contracts, manifest_path_name) is getattr(
        support,
        manifest_path_name,
    )


def test_shared_publication_runtime_manifest_path_constants_point_to_current_workload_files(
) -> None:
    assert (
        CONDITIONAL_GROUP_EXISTS_BOUNDARY_MANIFEST_PATH,
        NESTED_GROUP_CALLABLE_REPLACEMENT_BOUNDARY_MANIFEST_PATH,
    ) == (
        REPO_ROOT / "benchmarks" / "workloads" / "conditional_group_exists_boundary.py",
        REPO_ROOT
        / "benchmarks"
        / "workloads"
        / "nested_group_callable_replacement_boundary.py",
    )


def test_benchmark_test_support_owns_shared_collection_replacement_classifier_helpers(
) -> None:
    definition_names, _ = support.top_level_module_definition_and_assignment_names(
        support
    )

    assert {
        "_is_encoded_indexlike_payload",
        "_collection_replacement_keyword_parameter_name",
        "_collection_replacement_positional_keyword_field",
        "_is_collection_replacement_keyword_workload",
        "_is_collection_replacement_wrong_text_model_workload",
    }.issubset(definition_names)


def test_non_owner_collection_replacement_benchmark_support_routes_shared_classifiers_through_support_alias(
) -> None:
    definition_names, assignment_names = (
        support.top_level_module_definition_and_assignment_names(
            collection_replacement_support
        )
    )

    assert any(
        isinstance(node, ast.ImportFrom)
        and node.module == "tests.benchmarks"
        and any(alias.name == "benchmark_test_support" for alias in node.names)
        for node in _parsed_module_ast(collection_replacement_support).body
    )
    assert {
        "_collection_replacement_keyword_parameter_name",
        "_collection_replacement_positional_keyword_field",
        "_is_collection_replacement_keyword_workload",
        "_is_collection_replacement_wrong_text_model_workload",
    }.isdisjoint(definition_names)
    assert {
        "_collection_replacement_keyword_parameter_name",
        "_collection_replacement_positional_keyword_field",
        "_is_collection_replacement_keyword_workload",
        "_is_collection_replacement_wrong_text_model_workload",
    }.isdisjoint(assignment_names)


def test_shared_collection_replacement_classifier_contract_tests_import_from_support(
) -> None:
    owner_suite = importlib.import_module(
        "tests.benchmarks.test_collection_replacement_benchmark_anchor_support"
    )
    combined_suite = importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )

    assert {
        "_collection_replacement_positional_keyword_field",
        "_is_collection_replacement_keyword_workload",
    }.issubset(
        _module_imported_names(
            owner_suite,
            "tests.benchmarks.benchmark_test_support",
        )
    )
    assert {
        "_is_collection_replacement_keyword_workload",
        "_is_collection_replacement_wrong_text_model_workload",
    }.issubset(
        _module_imported_names(
            combined_suite,
            "tests.benchmarks.benchmark_test_support",
        )
    )


def test_deleted_collection_replacement_keyword_contract_wrapper_stays_unimportable_and_unreferenced(
) -> None:
    _assert_deleted_benchmark_module_stays_absent(
        deleted_module_name=(
            "tests.benchmarks.test_collection_replacement_"
            + "keyword_contract_benchmark_support"
        ),
        deleted_path=(
            REPO_ROOT
            / "tests"
            / "benchmarks"
            / "test_collection_replacement_keyword_contract_benchmark_support.py"
        ),
    )


def test_benchmark_test_support_owns_pattern_boundary_surface() -> None:
    definition_names, assignment_names = (
        support.top_level_module_definition_and_assignment_names(support)
    )

    assert {
        "_pattern_boundary_wrong_text_model_source_workloads",
        "_pattern_boundary_wrong_text_model_expected_callback_call",
        "_run_cpython_pattern_boundary_wrong_text_model_workload",
        "_pattern_window_positional_indexlike_correctness_case_signature",
        "_pattern_window_positional_indexlike_workload_args",
        "_pattern_window_positional_indexlike_workload_signature",
        "_is_pattern_window_positional_indexlike_workload",
        "_pattern_keyword_window_correctness_case_signature",
        "_pattern_keyword_window_workload_signature",
        "_is_pattern_keyword_window_workload",
        "_pattern_bounded_wildcard_correctness_case_signature",
        "_pattern_bounded_wildcard_workload_signature",
        "_is_pattern_bounded_wildcard_workload",
        "_pattern_verbose_regression_correctness_case_signature",
        "_pattern_verbose_regression_workload_signature",
        "_is_pattern_verbose_regression_workload",
        "_pattern_boundary_wrong_text_model_correctness_case_signature",
        "_pattern_boundary_wrong_text_model_workload_signature",
        "_is_pattern_boundary_wrong_text_model_workload",
    }.issubset(definition_names)
    assert {
        "_PATTERN_BOUNDED_WILDCARD_WORKLOAD_IDS",
        "_PATTERN_VERBOSE_REGRESSION_PATTERN",
        "PATTERN_BOUNDARY_MANIFEST_PATH",
        "_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS",
        "_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC",
        "PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS",
    }.issubset(assignment_names)


def test_benchmark_test_support_defines_compiled_pattern_module_helper_owner_surface(
) -> None:
    definition_names, _ = support.top_level_module_definition_and_assignment_names(
        support
    )

    assert {
        "_compiled_pattern_module_helper_route",
        "_run_cpython_compiled_pattern_module_helper_workload",
        "_module_workflow_compiled_pattern_correctness_case_signature",
        "_module_workflow_compiled_pattern_workload_signature",
        "_is_module_workflow_compiled_pattern_wrong_text_model_workload",
        "_is_module_workflow_compiled_pattern_literal_success_workload",
        "_is_module_workflow_compiled_pattern_bounded_wildcard_success_workload",
        "_is_module_workflow_compiled_pattern_verbose_bytes_success_workload",
    }.issubset(definition_names)


def test_benchmark_test_support_owns_compiled_pattern_helper_surface(
) -> None:
    definition_names, assignment_names = (
        support.top_level_module_definition_and_assignment_names(support)
    )

    assert {
        "_compiled_pattern_module_helper_route",
        "_run_cpython_compiled_pattern_module_helper_workload",
        "_compiled_pattern_wrong_text_model_specs",
        "_compiled_pattern_wrong_text_model_source_workloads",
        "_compiled_pattern_wrong_text_model_contract_spec",
        "_assert_wrong_text_model_payload_round_trip",
        "_is_module_workflow_compiled_pattern_wrong_text_model_workload",
        "_module_workflow_compiled_pattern_correctness_case_signature",
        "_module_workflow_compiled_pattern_workload_signature",
        "_is_module_workflow_compiled_pattern_workload",
        "_is_module_workflow_compiled_pattern_literal_success_workload",
        "_is_module_workflow_compiled_pattern_bounded_wildcard_success_workload",
        "_is_module_workflow_compiled_pattern_verbose_bytes_success_workload",
        "CompiledPatternModuleSuccessOwnerSpec",
        "_assert_compiled_pattern_module_success_payload_round_trip",
        "_assert_compiled_pattern_success_rows_measured_in_combined_manifest",
        "include_live_compiled_pattern_module_success_workload",
        "live_compiled_pattern_module_success_surface_ids",
    }.issubset(definition_names)
    assert {
        "_COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS",
        "_COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS",
        "_COMPILED_PATTERN_MODULE_HELPER_OPERATIONS",
        "_VERBOSE_REGRESSION_PATTERN",
        "_VERBOSE_REGRESSION_FLAGS",
        "COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS",
        "_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC",
        "_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC",
        "_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS",
        "_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS",
    }.issubset(assignment_names)


def test_shared_compiled_pattern_helper_contract_tests_import_from_support() -> None:
    combined_suite = importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )

    assert {
        "_is_module_workflow_compiled_pattern_bounded_wildcard_success_workload",
        "_is_module_workflow_compiled_pattern_literal_success_workload",
        "_is_module_workflow_compiled_pattern_verbose_bytes_success_workload",
        "_module_workflow_compiled_pattern_correctness_case_signature",
        "_module_workflow_compiled_pattern_workload_signature",
        "_is_module_workflow_compiled_pattern_wrong_text_model_workload",
    }.issubset(
        _module_imported_names(
            combined_suite,
            "tests.benchmarks.benchmark_test_support",
        )
    )


@pytest.mark.parametrize(
    ("module_name", "expected_direct_names", "expected_owner_module_names"),
    (
        pytest.param(
            "tests.benchmarks.test_benchmark_manifest_validation",
            frozenset(
                {
                    "_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES",
                    "CompiledPatternModuleCompileContractCase",
                    "_source_tree_contract_manifest",
                    "_source_tree_contract_workload",
                }
            ),
            frozenset(
                {
                    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES",
                    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS",
                    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS",
                }
            ),
            id="benchmark-manifest-validation",
        ),
        pytest.param(
            "tests.benchmarks.test_source_tree_combined_boundary_benchmarks",
            frozenset(
                {
                    "_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES",
                    "_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS",
                    "_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS",
                    "_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES",
                    "_module_workflow_compiled_pattern_correctness_case_signature",
                    "_module_workflow_compiled_pattern_workload_signature",
                }
            ),
            frozenset(
                {
                    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES",
                    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS",
                    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS",
                    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS",
                }
            ),
            id="source-tree-combined",
        ),
    ),
)
def test_compiled_pattern_contract_consumer_suites_reuse_shared_support_without_local_duplicates(
    module_name: str,
    expected_direct_names: frozenset[str],
    expected_owner_module_names: frozenset[str],
) -> None:
    module = importlib.import_module(module_name)
    definition_names, assignment_names = (
        support.top_level_module_definition_and_assignment_names(module)
    )
    local_names = definition_names | assignment_names

    assert "tests.benchmarks.benchmark_test_support" in _module_import_targets(module)
    assert "tests.benchmarks" in _module_import_targets(module)
    assert expected_direct_names.issubset(
        _module_imported_names(module, "tests.benchmarks.benchmark_test_support")
    )
    assert "benchmark_test_support" in _module_imported_names(
        module,
        "tests.benchmarks",
    )

    for shared_name in expected_direct_names:
        assert getattr(module, shared_name) is getattr(support, shared_name)
        assert shared_name not in local_names

    assert not hasattr(module, "compiled_pattern_module_helper_support")
    assert getattr(module, "benchmark_test_support") is support
    for shared_name in expected_owner_module_names:
        assert getattr(module.benchmark_test_support, shared_name) is getattr(
            support,
            shared_name,
        )
        assert shared_name not in local_names


@pytest.mark.parametrize(
    ("module_name", "expected_owner_module_names"),
    (
        pytest.param(
            "tests.benchmarks.test_benchmark_manifest_validation",
            frozenset(
                {
                    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES",
                    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS",
                    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS",
                }
            ),
            id="benchmark-manifest-validation",
        ),
        pytest.param(
            "tests.benchmarks.test_source_tree_combined_boundary_benchmarks",
            frozenset(
                {
                    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES",
                    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS",
                    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS",
                    "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS",
                }
            ),
            id="source-tree-combined",
        ),
    ),
)
def test_compiled_pattern_contract_consumer_suites_do_not_alias_owner_module_surfaces(
    module_name: str,
    expected_owner_module_names: frozenset[str],
) -> None:
    module = importlib.import_module(module_name)

    assert (
        _top_level_benchmark_support_alias_pairs(
            module,
            expected_owner_module_names,
        )
        == frozenset()
    )


def test_benchmark_test_support_owns_compiled_pattern_module_success_surface(
) -> None:
    definition_names, assignment_names = (
        support.top_level_module_definition_and_assignment_names(support)
    )

    assert {
        "CompiledPatternModuleSuccessOwnerSpec",
        "_assert_compiled_pattern_module_success_payload_round_trip",
        "_assert_compiled_pattern_success_rows_measured_in_combined_manifest",
        "include_live_compiled_pattern_module_success_workload",
        "live_compiled_pattern_module_success_surface_ids",
    }.issubset(definition_names)
    assert {
        "_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC",
        "_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC",
        "_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS",
        "_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS",
    }.issubset(assignment_names)
    assert (
        support.CompiledPatternModuleSuccessOwnerSpec.contract_builder_spec.__name__
        == "contract_builder_spec"
    )
    assert (
        support.CompiledPatternModuleSuccessOwnerSpec.source_workloads.__name__
        == "source_workloads"
    )
    assert (
        support.CompiledPatternModuleSuccessOwnerSpec.expected_build_calls.__name__
        == "expected_build_calls"
    )
    assert (
        support.CompiledPatternModuleSuccessOwnerSpec.expected_callback_result.__name__
        == "expected_callback_result"
    )
    assert (
        support.CompiledPatternModuleSuccessOwnerSpec.expected_callback_call.__name__
        == "expected_callback_call"
    )


def test_deleted_compiled_pattern_module_helper_support_stays_unimportable_and_unreferenced(
) -> None:
    _assert_deleted_benchmark_module_stays_absent(
        deleted_module_name=".".join(
            (
                "tests",
                "benchmarks",
                "compiled"
                "_pattern"
                "_module"
                "_helper"
                "_benchmark"
                "_support",
            )
        ),
        deleted_path=(
            REPO_ROOT
            / "tests"
            / "benchmarks"
            / (
                "compiled"
                "_pattern"
                "_module"
                "_helper"
                "_benchmark"
                "_support.py"
            )
        ),
    )


def test_deleted_compiled_pattern_module_success_wrapper_stays_unimportable_and_unreferenced(
) -> None:
    _assert_deleted_benchmark_module_stays_absent(
        deleted_module_name=(
            "tests.benchmarks.compiled_pattern_module_success_benchmark_support"
        ),
        deleted_path=(
            REPO_ROOT
            / "tests"
            / "benchmarks"
            / "compiled_pattern_module_success_benchmark_support.py"
        ),
    )


def test_deleted_pattern_boundary_support_stays_unimportable_and_unreferenced() -> None:
    _assert_deleted_benchmark_module_stays_absent(
        deleted_module_name="tests.benchmarks.pattern_boundary_benchmark_anchor_support",
        deleted_path=(
            REPO_ROOT
            / "tests"
            / "benchmarks"
            / "pattern_boundary_benchmark_anchor_support.py"
        ),
    )


@pytest.mark.parametrize(
    ("module", "expected_imported_names"),
    (
        (
            collection_replacement_support,
            frozenset(
                {
                    "_SourceTreeContractBuilderSpec",
                    "_contract_source_workloads",
                }
            ),
        ),
    ),
)
def test_non_owner_benchmark_support_modules_import_shared_source_tree_contract_helpers_from_support(
    module: object,
    expected_imported_names: frozenset[str],
) -> None:
    assert expected_imported_names.issubset(
        _module_imported_names(module, "tests.benchmarks.benchmark_test_support")
    )


@pytest.mark.parametrize(
    ("module_name", "expected_imported_names"),
    (
        (
            "tests.benchmarks.test_benchmark_manifest_validation",
            frozenset(
                {
                    "_SourceTreeContractBuilderSpec",
                    "_source_tree_contract_manifest",
                }
            ),
        ),
        (
            "tests.benchmarks.test_collection_replacement_benchmark_anchor_support",
            frozenset(
                {
                    "_source_tree_contract_manifest",
                    "_source_tree_contract_workload",
                }
            ),
        ),
        (
            "tests.benchmarks.test_pattern_boundary_benchmark_anchor_support",
            frozenset(
                {
                    "_source_tree_contract_manifest",
                    "_source_tree_contract_workload",
                }
            ),
        ),
    ),
)
def test_source_tree_contract_helper_suites_import_from_support(
    module_name: str,
    expected_imported_names: frozenset[str],
) -> None:
    module = importlib.import_module(module_name)

    imported_names = _module_imported_names(
        module,
        "tests.benchmarks.benchmark_test_support",
    )

    assert expected_imported_names.issubset(imported_names)


def test_compiled_pattern_module_compile_wrapper_suite_is_deleted_and_unimportable(
) -> None:
    _assert_deleted_benchmark_module_stays_absent(
        deleted_module_name=".".join(
            (
                "tests",
                "benchmarks",
                "test"
                "_compiled"
                "_pattern"
                "_module"
                "_compile"
                "_benchmark"
                "_support",
            )
        ),
        deleted_path=(
            REPO_ROOT
            / "tests"
            / "benchmarks"
            / (
                "test"
                "_compiled"
                "_pattern"
                "_module"
                "_compile"
                "_benchmark"
                "_support.py"
            )
        ),
    )


def test_compiled_pattern_module_compile_support_layer_is_deleted_and_unimportable(
) -> None:
    _assert_deleted_benchmark_module_stays_absent(
        deleted_module_name=".".join(
            (
                "tests",
                "benchmarks",
                "compiled_pattern_module_compile_benchmark_support",
            )
        ),
        deleted_path=(
            REPO_ROOT
            / "tests"
            / "benchmarks"
            / "compiled_pattern_module_compile_benchmark_support.py"
        ),
    )


def test_compiled_pattern_module_helper_wrapper_suite_is_deleted_and_unimportable(
) -> None:
    _assert_deleted_benchmark_module_stays_absent(
        deleted_module_name=".".join(
            (
                "tests",
                "benchmarks",
                "test"
                "_compiled"
                "_pattern"
                "_module"
                "_helper"
                "_benchmark"
                "_support",
            )
        ),
        deleted_path=(
            REPO_ROOT
            / "tests"
            / "benchmarks"
            / (
                "test"
                "_compiled"
                "_pattern"
                "_module"
                "_helper"
                "_benchmark"
                "_support.py"
            )
        ),
    )


@pytest.mark.parametrize(
    ("workload", "callback_flags", "expected_result", "expected_call", "expected_cpython_args", "materialize"),
    (
        (
            synthetic_workload(
                manifest_id=_compiled_pattern_module_helper_manifest_id(
                    "module.search"
                ),
                workload_id="module-search-success",
                operation="module.search",
                pattern="abc",
                haystack="zzabczz",
                flags=re.IGNORECASE,
                use_compiled_pattern=True,
            ),
            re.IGNORECASE,
            "module-result",
            ("module.search", "zzabczz", 0, {}),
            ("zzabczz", re.IGNORECASE),
            False,
        ),
        (
            synthetic_workload(
                manifest_id=_compiled_pattern_module_helper_manifest_id("module.subn"),
                workload_id="module-subn-success",
                operation="module.subn",
                pattern="abc",
                haystack="abcabc",
                replacement="x",
                count=1,
                flags=re.IGNORECASE,
                use_compiled_pattern=True,
            ),
            re.IGNORECASE,
            ("module-result", 0),
            ("module.subn", "x", "abcabc", 1, re.IGNORECASE, {}),
            ("x", "abcabc", 1),
            False,
        ),
        (
            synthetic_workload(
                manifest_id=_compiled_pattern_module_helper_manifest_id(
                    "module.finditer"
                ),
                workload_id="module-finditer-wrong-text-model",
                operation="module.finditer",
                pattern="abc",
                haystack="abcabc",
                text_model="bytes",
                haystack_text_model="str",
                use_compiled_pattern=True,
                expected_exception={
                    "type": "TypeError",
                    "message_substring": "cannot use a bytes pattern on a string-like object",
                },
            ),
            0,
            ["module-finditer-result"],
            ("module.finditer", "abcabc", 0),
            ("abcabc", 0),
            True,
        ),
        (
            synthetic_workload(
                manifest_id=_compiled_pattern_module_helper_manifest_id("module.split"),
                workload_id="module-split-success",
                operation="module.split",
                pattern="abc",
                haystack="abcabc",
                maxsplit=2,
                flags=re.MULTILINE,
                use_compiled_pattern=True,
            ),
            re.MULTILINE,
            "module-result",
            ("module.split", "abcabc", 2, re.MULTILINE, {}),
            ("abcabc", 2),
            False,
        ),
    ),
    ids=(
        "module-boundary-search",
        "collection-replacement-subn",
        "wrong-text-model-finditer",
        "collection-replacement-split",
    ),
)
def test_compiled_pattern_module_helper_route_preserves_expected_shapes(
    workload: object,
    callback_flags: int,
    expected_result: object,
    expected_call: tuple[object, ...],
    expected_cpython_args: tuple[object, ...],
    materialize: bool,
) -> None:
    route = support._compiled_pattern_module_helper_route(
        workload,
        collection_replacement_callback_flags=callback_flags,
    )
    callback_result, callback_call, cpython_call_args, materialize_cpython_result = route

    assert callback_result == expected_result
    assert callback_call == expected_call
    assert cpython_call_args == expected_cpython_args
    assert materialize_cpython_result is materialize


def test_run_cpython_compiled_pattern_module_helper_workload_materializes_finditer() -> None:
    workload = synthetic_workload(
        manifest_id=_compiled_pattern_module_helper_manifest_id("module.finditer"),
        workload_id="module-finditer-runtime",
        operation="module.finditer",
        pattern="abc",
        haystack="abcabc",
        use_compiled_pattern=True,
    )

    result = (
        support._run_cpython_compiled_pattern_module_helper_workload(
        workload,
        collection_replacement_callback_flags=0,
        )
    )

    assert isinstance(result, list)
    assert [match.group(0) for match in result] == ["abc", "abc"]


def test_run_cpython_compiled_pattern_module_helper_workload_preserves_scalar_result(
) -> None:
    workload = synthetic_workload(
        manifest_id=_compiled_pattern_module_helper_manifest_id("module.subn"),
        workload_id="module-subn-runtime",
        operation="module.subn",
        pattern="abc",
        haystack="abcabc",
        replacement="x",
        count=1,
        use_compiled_pattern=True,
    )

    result = (
        support._run_cpython_compiled_pattern_module_helper_workload(
        workload,
        collection_replacement_callback_flags=0,
        )
    )

    assert result == ("xabc", 1)


def test_compiled_pattern_module_helper_wrong_text_model_selector_accepts_bounded_trio(
) -> None:
    workload = synthetic_workload(
        manifest_id=_compiled_pattern_module_helper_manifest_id("module.search"),
        workload_id="module.search-wrong-text-model",
        operation="module.search",
        text_model="str",
        haystack_text_model="bytes",
        use_compiled_pattern=True,
        expected_exception={
            "type": "TypeError",
            "message_substring": "cannot use a string pattern on a bytes-like object",
        },
    )

    assert (
        support._is_module_workflow_compiled_pattern_wrong_text_model_workload(
            workload
        )
    )


def test_compiled_pattern_module_helper_wrong_text_model_selector_rejects_missing_guard_fields(
) -> None:
    wrong_pattern_argument = SimpleNamespace(
        workload_id="module-search-direct-pattern",
        operation="module.search",
        flags=0,
        text_model="str",
        haystack_text_model="bytes",
        use_compiled_pattern=False,
        expected_exception={
            "type": "TypeError",
            "message_substring": "cannot use a string pattern on a bytes-like object",
        },
        kwargs={},
    )
    missing_haystack_text_model = SimpleNamespace(
        workload_id="module-search-no-haystack-model",
        operation="module.search",
        flags=0,
        text_model="str",
        haystack_text_model=None,
        use_compiled_pattern=True,
        expected_exception={
            "type": "TypeError",
            "message_substring": "cannot use a string pattern on a bytes-like object",
        },
        kwargs={},
    )
    wrong_exception_type = SimpleNamespace(
        workload_id="module-search-value-error",
        operation="module.search",
        flags=0,
        text_model="str",
        haystack_text_model="bytes",
        use_compiled_pattern=True,
        expected_exception={
            "type": "ValueError",
            "message_substring": "wrong exception type",
        },
        kwargs={},
    )

    assert not (
        support._is_module_workflow_compiled_pattern_wrong_text_model_workload(
            wrong_pattern_argument
        )
    )
    assert not (
        support._is_module_workflow_compiled_pattern_wrong_text_model_workload(
            missing_haystack_text_model
        )
    )
    assert not (
        support._is_module_workflow_compiled_pattern_wrong_text_model_workload(
            wrong_exception_type
        )
    )


def test_module_workflow_compiled_pattern_success_selectors_accept_bounded_workloads(
) -> None:
    literal_workload = synthetic_workload(
        manifest_id=_compiled_pattern_module_helper_manifest_id("module.search"),
        workload_id="module-search-literal-compiled-pattern",
        operation="module.search",
        pattern="abc",
        haystack="zzabczz",
        use_compiled_pattern=True,
    )
    wildcard_workload = synthetic_workload(
        manifest_id=_compiled_pattern_module_helper_manifest_id("module.fullmatch"),
        workload_id="module-fullmatch-bounded-wildcard-compiled-pattern",
        operation="module.fullmatch",
        pattern="a.c",
        haystack="abc",
        text_model="bytes",
        use_compiled_pattern=True,
    )
    verbose_workload = synthetic_workload(
        manifest_id=_compiled_pattern_module_helper_manifest_id("module.search"),
        workload_id="module-search-verbose-bytes-compiled-pattern",
        operation="module.search",
        pattern=r"^ (?P<key>[A-Z_]+) \s* = \s* (?:[A-Z]{2,4}+|\d{2,3}) $",
        haystack="FOO = 123",
        text_model="bytes",
        flags=re.VERBOSE | re.MULTILINE,
        use_compiled_pattern=True,
    )

    assert (
        support._is_module_workflow_compiled_pattern_literal_success_workload(
            literal_workload
        )
    )
    assert (
        support._module_workflow_compiled_pattern_workload_signature(
            literal_workload
        )
        == ("module.search", "abc", ("zzabczz",), True, 0, "str")
    )

    assert (
        support._is_module_workflow_compiled_pattern_bounded_wildcard_success_workload(
            wildcard_workload
        )
    )
    assert (
        support._module_workflow_compiled_pattern_workload_signature(
            wildcard_workload
        )
        == ("module.fullmatch", b"a.c", (b"abc",), True, 0, "bytes")
    )

    assert (
        support._is_module_workflow_compiled_pattern_verbose_bytes_success_workload(
            verbose_workload
        )
    )
    assert (
        support._module_workflow_compiled_pattern_workload_signature(
            verbose_workload
        )
        == (
        "module.search",
        b"^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $",
        (b"FOO = 123",),
        True,
        re.VERBOSE | re.MULTILINE,
        "bytes",
        )
    )


def test_module_workflow_compiled_pattern_success_selectors_reject_non_matching_rows(
) -> None:
    direct_pattern_workload = synthetic_workload(
        manifest_id=_compiled_pattern_module_helper_manifest_id("module.search"),
        workload_id="module-search-direct-pattern",
        operation="module.search",
        pattern="abc",
        haystack="zzabczz",
    )
    wrong_haystack_model = synthetic_workload(
        manifest_id=_compiled_pattern_module_helper_manifest_id("module.match"),
        workload_id="module-match-wrong-text-model",
        operation="module.match",
        pattern="abc",
        haystack="zzabczz",
        haystack_text_model="bytes",
        use_compiled_pattern=True,
        expected_exception={"type": "TypeError", "message_substring": "wrong type"},
    )

    assert not (
        support._is_module_workflow_compiled_pattern_literal_success_workload(
            direct_pattern_workload
        )
    )
    assert not (
        support._is_module_workflow_compiled_pattern_bounded_wildcard_success_workload(
            wrong_haystack_model
        )
    )


def test_module_workflow_compiled_pattern_correctness_case_signature_requires_compiled_module_call_shape(
) -> None:
    matching_case = _module_pattern_case(
        helper="search",
        operation="module_call",
        args=("zzabczz",),
        pattern="abc",
        use_compiled_pattern=True,
    )
    missing_args_case = _module_pattern_case(
        helper="search",
        operation="module_call",
        args=(),
        pattern="abc",
        use_compiled_pattern=True,
    )
    unsupported_helper_case = _module_pattern_case(
        helper="split",
        operation="module_call",
        args=("zzabczz",),
        pattern="abc",
        use_compiled_pattern=True,
    )

    assert (
        support._module_workflow_compiled_pattern_correctness_case_signature(
            matching_case
        )
        == ("module.search", "abc", ("zzabczz",), True, 0, "str")
    )
    assert (
        support._module_workflow_compiled_pattern_correctness_case_signature(
            missing_args_case
        )
        is None
    )
    assert (
        support._module_workflow_compiled_pattern_correctness_case_signature(
            unsupported_helper_case
        )
        is None
    )


def test_anchored_workload_case_helpers_classify_anchored_and_unanchored_workloads(
    monkeypatch: pytest.MonkeyPatch,
    anchor_support_cache_guard: None,
) -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")
    workloads = (
        _synthetic_workload("anchored", ("shared",)),
        _synthetic_workload("unanchored", ("missing",)),
        _synthetic_workload("excluded", ("shared",), include=False),
    )
    monkeypatch.setattr(
        support,
        "load_manifest",
        lambda path: _synthetic_manifest_loader(path, workloads=workloads),
    )

    anchor_case_ids = {("shared",): ("case-a", "case-b")}

    assert support.anchored_workload_case_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=_synthetic_workload_signature,
        include_workload=_synthetic_workload_is_included,
    ) == {
        ("synthetic_boundary.py", "anchored"): ("case-a", "case-b"),
        ("synthetic_boundary.py", "unanchored"): (),
    }
    assert support.unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=_synthetic_workload_signature,
        include_workload=_synthetic_workload_is_included,
    ) == ("unanchored",)


def test_expected_anchored_workload_case_pairs_return_matching_objects(
    monkeypatch: pytest.MonkeyPatch,
    anchor_support_cache_guard: None,
) -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")
    workload = _synthetic_workload("anchored", ("shared",))
    case = SimpleNamespace(case_id="case-1")
    monkeypatch.setattr(
        support,
        "load_manifest",
        lambda path: _synthetic_manifest_loader(path, workloads=(workload,)),
    )
    monkeypatch.setattr(
        support,
        "published_cases_by_id",
        lambda: records_by_string_id((case,), id_attr="case_id"),
    )

    anchored_pairs = support.expected_anchored_workload_case_pairs(
        manifest_path,
        expected_anchor_case_ids={
            ("synthetic_boundary.py", "anchored"): ("case-1",),
        },
    )

    assert len(anchored_pairs) == 1
    anchored_pair = anchored_pairs[0]
    assert anchored_pair.manifest_name == "synthetic_boundary.py"
    assert anchored_pair.workload_id == "anchored"
    assert anchored_pair.case_id == "case-1"
    assert anchored_pair.workload is workload
    assert anchored_pair.case is case


def test_expected_anchored_workload_case_pairs_rejects_manifest_name_drift(
    monkeypatch: pytest.MonkeyPatch,
    anchor_support_cache_guard: None,
) -> None:
    monkeypatch.setattr(
        support,
        "load_manifest",
        lambda path: _synthetic_manifest_loader(
            path,
            workloads=(_synthetic_workload("anchored", ("shared",)),),
        ),
    )
    monkeypatch.setattr(
        support,
        "published_cases_by_id",
        lambda: records_by_string_id(
            (SimpleNamespace(case_id="case-1"),),
            id_attr="case_id",
        ),
    )

    with pytest.raises(AssertionError, match="does not match"):
        support.expected_anchored_workload_case_pairs(
            pathlib.Path("synthetic_boundary.py"),
            expected_anchor_case_ids={
                ("other_boundary.py", "anchored"): ("case-1",),
            },
        )


def test_expected_anchored_workload_case_pairs_rejects_multiple_case_ids(
    monkeypatch: pytest.MonkeyPatch,
    anchor_support_cache_guard: None,
) -> None:
    monkeypatch.setattr(
        support,
        "load_manifest",
        lambda path: _synthetic_manifest_loader(
            path,
            workloads=(_synthetic_workload("anchored", ("shared",)),),
        ),
    )
    monkeypatch.setattr(
        support,
        "published_cases_by_id",
        lambda: records_by_string_id(
            (
                SimpleNamespace(case_id="case-1"),
                SimpleNamespace(case_id="case-2"),
            ),
            id_attr="case_id",
        ),
    )

    with pytest.raises(
        AssertionError,
        match="expected exactly one published correctness case",
    ):
        support.expected_anchored_workload_case_pairs(
            pathlib.Path("synthetic_boundary.py"),
            expected_anchor_case_ids={
                ("synthetic_boundary.py", "anchored"): ("case-1", "case-2"),
            },
        )


def test_expected_anchored_workload_case_pairs_rejects_missing_workload(
    monkeypatch: pytest.MonkeyPatch,
    anchor_support_cache_guard: None,
) -> None:
    monkeypatch.setattr(
        support,
        "load_manifest",
        lambda path: _synthetic_manifest_loader(
            path,
            workloads=(_synthetic_workload("anchored", ("shared",)),),
        ),
    )
    monkeypatch.setattr(
        support,
        "published_cases_by_id",
        lambda: records_by_string_id(
            (SimpleNamespace(case_id="case-1"),),
            id_attr="case_id",
        ),
    )

    with pytest.raises(
        AssertionError,
        match=r"expected anchored workload 'missing' to be in scope",
    ):
        support.expected_anchored_workload_case_pairs(
            pathlib.Path("synthetic_boundary.py"),
            expected_anchor_case_ids={
                ("synthetic_boundary.py", "missing"): ("case-1",),
            },
        )


def test_expected_anchored_workload_case_pairs_rejects_unpublished_case(
    monkeypatch: pytest.MonkeyPatch,
    anchor_support_cache_guard: None,
) -> None:
    monkeypatch.setattr(
        support,
        "load_manifest",
        lambda path: _synthetic_manifest_loader(
            path,
            workloads=(_synthetic_workload("anchored", ("shared",)),),
        ),
    )
    monkeypatch.setattr(
        support,
        "published_cases_by_id",
        lambda: records_by_string_id((), id_attr="case_id"),
    )

    with pytest.raises(
        AssertionError,
        match=r"expected anchored correctness case 'case-1' to be published",
    ):
        support.expected_anchored_workload_case_pairs(
            pathlib.Path("synthetic_boundary.py"),
            expected_anchor_case_ids={
                ("synthetic_boundary.py", "anchored"): ("case-1",),
            },
        )


def test_assert_anchored_workload_case_result_parity_delegates_expected_values(
    monkeypatch: pytest.MonkeyPatch,
    anchor_support_cache_guard: None,
) -> None:
    workload = _synthetic_workload("anchored", ("shared",))
    pair = support.AnchoredWorkloadCasePair(
        manifest_name="synthetic_boundary.py",
        workload_id="anchored",
        case_id="case-1",
        workload=workload,
        case=SimpleNamespace(case_id="case-1"),
    )
    calls: list[tuple[object, object]] = []
    monkeypatch.setattr(
        support,
        "run_correctness_case_with_cpython",
        lambda case: f"expected:{case.case_id}",
    )
    monkeypatch.setattr(
        support,
        "assert_benchmark_workload_matches_expected_result",
        lambda workload, expected: calls.append((workload, expected)),
    )

    support.assert_anchored_workload_case_result_parity((pair,))

    assert calls == [(workload, "expected:case-1")]


def test_assert_anchored_workload_case_result_parity_accepts_matching_exceptions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workload = _synthetic_workload("anchored", ("shared",))
    pair = support.AnchoredWorkloadCasePair(
        manifest_name="synthetic_boundary.py",
        workload_id="anchored",
        case_id="case-1",
        workload=workload,
        case=SimpleNamespace(case_id="case-1"),
    )
    benchmark_calls: list[object] = []

    def _raise_expected(_: object) -> object:
        raise ValueError("shared boom")

    def _raise_observed(observed_workload: object) -> object:
        benchmark_calls.append(observed_workload)
        raise ValueError("shared boom")

    monkeypatch.setattr(support, "run_correctness_case_with_cpython", _raise_expected)
    monkeypatch.setattr(support, "run_benchmark_workload_with_cpython", _raise_observed)

    support.assert_anchored_workload_case_result_parity((pair,))

    assert benchmark_calls == [workload]


def test_assert_anchored_workload_case_result_parity_rejects_exception_message_drift(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workload = _synthetic_workload("anchored", ("shared",))
    pair = support.AnchoredWorkloadCasePair(
        manifest_name="synthetic_boundary.py",
        workload_id="anchored",
        case_id="case-1",
        workload=workload,
        case=SimpleNamespace(case_id="case-1"),
    )

    def _raise_expected(_: object) -> object:
        raise ValueError("expected boom")

    def _raise_observed(_: object) -> object:
        raise ValueError("observed boom")

    monkeypatch.setattr(support, "run_correctness_case_with_cpython", _raise_expected)
    monkeypatch.setattr(support, "run_benchmark_workload_with_cpython", _raise_observed)

    with pytest.raises(AssertionError):
        support.assert_anchored_workload_case_result_parity((pair,))


def test_standard_benchmark_definition_params_preserve_names_and_filters() -> None:
    def _assert_filtered_definition_params(
        predicate,
    ) -> tuple[support.StandardBenchmarkAnchorContractDefinition, ...]:
        params = support._standard_benchmark_definition_params(
            include_definition=predicate
        )
        expected_definitions = tuple(
            definition
            for definition in support.STANDARD_BENCHMARK_DEFINITIONS
            if predicate(definition)
        )

        assert tuple(parameter.values[0] for parameter in params) == expected_definitions
        assert tuple(parameter.id for parameter in params) == tuple(
            definition.name for definition in expected_definitions
        )

        return expected_definitions

    legacy_definitions = _assert_filtered_definition_params(
        _has_standard_benchmark_legacy_workloads
    )
    callback_definitions = _assert_filtered_definition_params(
        _runs_standard_benchmark_callback_result_parity
    )
    special_unanchored_definitions = _assert_filtered_definition_params(
        _has_standard_benchmark_special_unanchored_workloads
    )
    direct_parity_definitions = _assert_filtered_definition_params(
        _has_standard_benchmark_special_unanchored_direct_parity_cases
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
    assert "STANDARD_BENCHMARK_DEFINITIONS" in _module_imported_names(
        combined_suite,
        "tests.benchmarks.benchmark_test_support",
    )


def test_recording_benchmark_support_records_compile_calls_and_reuses_compiled_patterns(
) -> None:
    module = RecordingBenchmarkModule()
    compiled_pattern = module.compile("abc", 0)

    assert module.calls == [("compile", "abc", 0)]
    assert len(module.compiled_patterns) == 1
    assert module.compiled_patterns[0] is compiled_pattern
    assert module.compile(compiled_pattern, 0) is compiled_pattern
    assert module.calls[-1] == ("compile", compiled_pattern, 0)


def test_recording_benchmark_support_records_helper_call_before_raising() -> None:
    module = RecordingBenchmarkModule(
        helper_exception=TypeError("unexpected keyword argument 'missing'"),
    )
    callback = benchmarks.build_callable(
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


def test_recording_benchmark_support_records_pattern_helper_calls() -> None:
    module = RecordingBenchmarkModule()
    callback = benchmarks.build_callable(
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
            id="recording-module-cold",
        ),
        pytest.param(
            "warm",
            [
                ("module.search", "abc", "zabcabc", 0, {}),
            ],
            [
                ("module.search", "abc", "zabcabc", 0, {}),
            ],
            id="recording-module-warm",
        ),
        pytest.param(
            "purged",
            [],
            [
                ("purge",),
                ("module.search", "abc", "zabcabc", 0, {}),
                ("purge",),
            ],
            id="recording-module-purged",
        ),
    ),
)
def test_recording_benchmark_module_helper_cache_modes_preserve_expected_order(
    cache_mode: str,
    expected_build_calls: list[tuple[object, ...]],
    expected_callback_calls: list[tuple[object, ...]],
) -> None:
    module = RecordingBenchmarkModule()
    callback = benchmarks.build_callable(
        module,
        "re",
        synthetic_workload(
            manifest_id="python-benchmark-module-helper-cache-contract",
            workload_id=f"module-search-{cache_mode}-cache-contract",
            bucket="module-search",
            family="module",
            operation="module.search",
            pattern="abc",
            haystack="zabcabc",
            text_model="str",
            cache_mode=cache_mode,
            timing_scope="module-helper-call",
        ),
    )

    assert module.calls == expected_build_calls
    assert callback() == "module-result"
    assert module.calls == [*expected_build_calls, *expected_callback_calls]


def test_recording_benchmark_module_helper_warm_expected_exception_prewarms_compile_cache(
) -> None:
    module = RecordingBenchmarkModule(
        helper_exception=TypeError("unexpected keyword argument 'missing'"),
    )
    callback = benchmarks.build_callable(
        module,
        "re",
        synthetic_workload(
            manifest_id="python-benchmark-module-helper-cache-contract",
            workload_id="module-search-warm-cache-contract",
            bucket="module-search",
            family="module",
            operation="module.search",
            pattern="abc",
            haystack="zabcabc",
            expected_exception={
                "type": "TypeError",
                "message_substring": "unexpected keyword argument 'missing'",
            },
            text_model="str",
            cache_mode="warm",
            timing_scope="module-helper-call",
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
            id="recording-pattern-cold",
        ),
        pytest.param(
            "warm",
            [
                ("compile", "abc", 0),
            ],
            [
                ("pattern.search", "zabcabc", (), {}),
            ],
            id="recording-pattern-warm",
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
            id="recording-pattern-purged",
        ),
    ),
)
def test_recording_benchmark_pattern_helper_cache_modes_preserve_expected_order(
    cache_mode: str,
    expected_build_calls: list[tuple[object, ...]],
    expected_callback_calls: list[tuple[object, ...]],
) -> None:
    module = RecordingBenchmarkModule()
    callback = benchmarks.build_callable(
        module,
        "re",
        synthetic_workload(
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
        ),
    )

    assert module.calls == expected_build_calls
    assert callback() == "pattern-result"
    assert module.calls == [*expected_build_calls, *expected_callback_calls]
