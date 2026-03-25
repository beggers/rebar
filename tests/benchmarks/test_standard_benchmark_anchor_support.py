from __future__ import annotations

import ast
from functools import partial
import pathlib
from typing import Any

import pytest

from rebar_harness.benchmarks import load_manifest
from tests.benchmarks.benchmark_test_support import (
    _synthetic_case,
    _synthetic_manifest_loader,
    _synthetic_workload,
    _synthetic_workload_is_included,
    _synthetic_workload_signature,
    anchor_support_cache_guard,
)
from tests.benchmarks import benchmark_test_support as benchmark_support
from tests.benchmarks import (
    collection_replacement_benchmark_anchor_support as collection_replacement_support,
)
from tests.benchmarks import compile_proxy_benchmark_support as compile_proxy_support
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
from tests.benchmarks import standard_benchmark_anchor_support as support
from tests.benchmarks.source_tree_benchmark_anchor_support import (
    assert_anchored_workload_case_result_parity,
    assert_benchmark_workload_matches_expected_result,
)
from tests.conftest import records_by_string_id

SOURCE_TREE_MANIFEST_PATH_CONSTANT_NAMES = (
    "MODULE_BOUNDARY_MANIFEST_PATH",
    "OPTIONAL_GROUP_MANIFEST_PATH",
    "NESTED_GROUP_MANIFEST_PATH",
    "EXACT_REPEAT_MANIFEST_PATH",
    "RANGED_REPEAT_MANIFEST_PATH",
    "GROUPED_ALTERNATION_MANIFEST_PATH",
    "GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH",
    "NESTED_GROUP_REPLACEMENT_MANIFEST_PATH",
    "OPEN_ENDED_MANIFEST_PATH",
)


def _synthetic_case_signature(case: Any) -> tuple[Any, ...] | None:
    return case.signature


def _allow_all_workloads(_: Any) -> bool:
    return True


def _definition_names(definitions: tuple[Any, ...]) -> tuple[str, ...]:
    return tuple(definition.name for definition in definitions)


def _build_standard_benchmark_definition_splice_names() -> tuple[str, ...]:
    import inspect

    parsed_support_source = ast.parse(inspect.getsource(support))
    builder = next(
        node
        for node in parsed_support_source.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "_build_standard_benchmark_definitions"
    )
    builder_return = next(
        node for node in builder.body if isinstance(node, ast.Return)
    )

    assert isinstance(builder_return.value, ast.Tuple)

    splice_names = []
    for element in builder_return.value.elts:
        assert isinstance(element, ast.Starred)
        assert isinstance(element.value, ast.Name)
        splice_names.append(element.value.id)

    return tuple(splice_names)


def _build_standard_benchmark_definition_imported_names(
    module_name: str,
) -> set[str]:
    import inspect

    parsed_support_source = ast.parse(inspect.getsource(support))
    builder = next(
        node
        for node in parsed_support_source.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "_build_standard_benchmark_definitions"
    )

    return {
        alias.name
        for node in builder.body
        if isinstance(node, ast.ImportFrom) and node.module == module_name
        for alias in node.names
    }


def _module_imported_names(module_name: str) -> set[str]:
    import inspect

    parsed_support_source = ast.parse(inspect.getsource(support))
    return {
        alias.name
        for node in parsed_support_source.body
        if isinstance(node, ast.ImportFrom) and node.module == module_name
        for alias in node.names
    }


@pytest.mark.parametrize(
    ("module", "export_name", "builder_name"),
    (
        pytest.param(
            compile_proxy_support,
            "COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS",
            "_build_compile_proxy_standard_benchmark_definitions",
            id="compile-proxy",
        ),
        pytest.param(
            collection_replacement_support,
            "COLLECTION_REPLACEMENT_STANDARD_BENCHMARK_DEFINITIONS",
            "_collection_replacement_standard_benchmark_definitions",
            id="collection-replacement",
        ),
        pytest.param(
            pattern_boundary_support,
            "PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS",
            "_build_pattern_boundary_standard_benchmark_definitions",
            id="pattern-boundary",
        ),
        pytest.param(
            compiled_pattern_module_helper_support,
            "COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS",
            "_build_compiled_pattern_module_helper_standard_benchmark_definitions",
            id="compiled-pattern-module-helper",
        ),
        pytest.param(
            compiled_pattern_module_compile_support,
            "COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS",
            "_build_compiled_pattern_module_compile_standard_benchmark_definitions",
            id="compiled-pattern-module-compile",
        ),
        pytest.param(
            anchor_support,
            "MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS",
            "_module_workflow_keyword_standard_benchmark_definitions",
            id="source-tree-module-workflow-keyword",
        ),
        pytest.param(
            anchor_support,
            "SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS",
            "_source_tree_standard_benchmark_definitions",
            id="source-tree-standard",
        ),
    ),
)
def test_owner_standard_definition_exports_stay_lazy_and_cached(
    module: Any,
    export_name: str,
    builder_name: str,
) -> None:
    builder = getattr(module, builder_name)

    # Owner modules expose these tuples lazily through __getattr__ rather than
    # binding another top-level global.
    assert export_name not in vars(module)

    first_export = getattr(module, export_name)
    second_export = getattr(module, export_name)

    assert isinstance(first_export, tuple)
    assert first_export
    assert first_export is second_export
    assert first_export is builder()
    assert export_name not in vars(module)


@pytest.mark.parametrize(
    ("module", "missing_name"),
    (
        pytest.param(
            compile_proxy_support,
            "NOT_A_COMPILE_PROXY_OWNER_EXPORT",
            id="compile-proxy",
        ),
        pytest.param(
            collection_replacement_support,
            "NOT_A_COLLECTION_REPLACEMENT_OWNER_EXPORT",
            id="collection-replacement",
        ),
        pytest.param(
            pattern_boundary_support,
            "NOT_A_PATTERN_BOUNDARY_OWNER_EXPORT",
            id="pattern-boundary",
        ),
        pytest.param(
            compiled_pattern_module_helper_support,
            "NOT_A_COMPILED_PATTERN_MODULE_HELPER_OWNER_EXPORT",
            id="compiled-pattern-module-helper",
        ),
        pytest.param(
            compiled_pattern_module_compile_support,
            "NOT_A_COMPILED_PATTERN_MODULE_COMPILE_OWNER_EXPORT",
            id="compiled-pattern-module-compile",
        ),
        pytest.param(
            anchor_support,
            "NOT_A_SOURCE_TREE_OWNER_EXPORT",
            id="source-tree-module-workflow-keyword",
        ),
    ),
)
def test_owner_support_modules_reject_unknown_lazy_export_names(
    module: Any,
    missing_name: str,
) -> None:
    with pytest.raises(AttributeError) as exc_info:
        getattr(module, missing_name)

    assert str(exc_info.value) == (
        f"module {module.__name__!r} has no attribute {missing_name!r}"
    )


def test_standard_support_does_not_reexport_module_boundary_manifest_path() -> None:
    assert "MODULE_BOUNDARY_MANIFEST_PATH" not in vars(support)

    with pytest.raises(AttributeError) as exc_info:
        getattr(support, "MODULE_BOUNDARY_MANIFEST_PATH")

    assert str(exc_info.value) == (
        "module 'tests.benchmarks.standard_benchmark_anchor_support' has no "
        "attribute 'MODULE_BOUNDARY_MANIFEST_PATH'"
    )


def test_standard_builder_imports_generic_anchor_helpers_from_benchmark_test_support(
) -> None:
    imported_names = _module_imported_names(
        "tests.benchmarks.benchmark_test_support"
    )

    assert {
        "_definition_anchor_expectations",
        "_workload_case_pair_anchor_expectations",
        "_workload_case_pairs_case_ids",
        "_workload_case_pairs_workload_ids",
    }.issubset(imported_names)
    assert _module_imported_names(
        "tests.benchmarks.source_tree_benchmark_anchor_support"
    ) == {
        "anchored_workload_case_ids",
        "expected_anchored_workload_case_pairs",
        "published_case_ids_by_signature",
        "unanchored_workload_ids",
    }


def test_standard_benchmark_anchor_contract_definition_filters_excluded_workloads() -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")
    definition = support.StandardBenchmarkAnchorContractDefinition(
        name="synthetic",
        manifest_paths=(manifest_path,),
        expected_anchor_case_ids={},
        include_workload=_allow_all_workloads,
        correctness_case_signature=_synthetic_case_signature,
        workload_signature=_synthetic_workload_signature,
        expected_excluded_workload_ids=frozenset({"excluded"}),
        expected_special_unanchored_workload_ids=("special-unanchored",),
    )

    assert definition.includes_workload(_synthetic_workload("ordinary", ("shared",)))
    assert not definition.includes_workload(_synthetic_workload("excluded", ("shared",)))
    assert not definition.includes_workload(
        _synthetic_workload("special-unanchored", ("shared",))
    )

def test_expected_workload_ids_filter_to_manifest_name() -> None:
    first_manifest = pathlib.Path("first_boundary.py")
    second_manifest = pathlib.Path("second_boundary.py")
    definition = support.StandardBenchmarkAnchorContractDefinition(
        name="synthetic",
        manifest_paths=(first_manifest, second_manifest),
        expected_anchor_case_ids={
            ("first_boundary.py", "first-a"): ("case-1",),
            ("second_boundary.py", "second-a"): ("case-2",),
            ("first_boundary.py", "first-b"): ("case-3",),
        },
        correctness_case_signature=_synthetic_case_signature,
        workload_signature=_synthetic_workload_signature,
        include_workload=_synthetic_workload_is_included,
    )

    assert support._expected_workload_ids(definition, first_manifest) == (
        "first-a",
        "first-b",
    )
    assert support._expected_anchor_case_ids_for_manifest(definition, second_manifest) == {
        ("second_boundary.py", "second-a"): ("case-2",),
    }


def test_callback_and_legacy_anchor_subsets_select_expected_workloads() -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")
    definition = support.StandardBenchmarkAnchorContractDefinition(
        name="synthetic",
        manifest_paths=(manifest_path,),
        expected_anchor_case_ids={
            ("synthetic_boundary.py", "callback"): ("case-callback",),
            ("synthetic_boundary.py", "legacy"): ("case-legacy",),
            ("synthetic_boundary.py", "ordinary"): ("case-ordinary",),
        },
        correctness_case_signature=_synthetic_case_signature,
        workload_signature=_synthetic_workload_signature,
        include_workload=_synthetic_workload_is_included,
        callback_anchor_workload_ids=frozenset({"callback"}),
        expected_legacy_workload_ids=frozenset({"legacy"}),
    )

    assert support._expected_callback_anchor_case_ids(definition) == {
        ("synthetic_boundary.py", "callback"): ("case-callback",),
    }
    assert support._expected_legacy_anchor_case_ids(definition) == {
        ("synthetic_boundary.py", "legacy"): ("case-legacy",),
    }


def test_anchor_helpers_resolve_anchored_and_unanchored_workloads(
    monkeypatch: pytest.MonkeyPatch,
    anchor_support_cache_guard: None,
) -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")
    workloads = (
        _synthetic_workload("anchored", ("shared",)),
        _synthetic_workload("unanchored", ("missing",)),
        _synthetic_workload("excluded", ("shared",), include=False),
        _synthetic_workload("special-unanchored", ("missing",)),
    )
    definition = support.StandardBenchmarkAnchorContractDefinition(
        name="synthetic",
        manifest_paths=(manifest_path,),
        expected_anchor_case_ids={
            ("synthetic_boundary.py", "anchored"): ("case-1",),
        },
        correctness_case_signature=_synthetic_case_signature,
        workload_signature=_synthetic_workload_signature,
        include_workload=_synthetic_workload_is_included,
        expected_special_unanchored_workload_ids=("special-unanchored",),
    )

    monkeypatch.setattr(
        benchmark_support,
        "load_manifest",
        partial(_synthetic_manifest_loader, workloads=workloads),
    )
    monkeypatch.setattr(
        support,
        "published_case_ids_by_signature",
        lambda _: {("shared",): ("case-1",)},
    )

    assert support._anchored_case_ids(definition) == {
        ("synthetic_boundary.py", "anchored"): ("case-1",),
        ("synthetic_boundary.py", "unanchored"): (),
    }
    assert support._unanchored_case_ids(definition, manifest_path) == ("unanchored",)
    assert support._unanchored_case_ids(
        definition,
        manifest_path,
        include_special_unanchored=True,
    ) == (
        "unanchored",
        "special-unanchored",
    )


def test_expected_anchored_pairs_materialize_matching_workload_and_case_objects(
    monkeypatch: pytest.MonkeyPatch,
    anchor_support_cache_guard: None,
) -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")
    workload = _synthetic_workload("anchored", ("shared",))
    case = _synthetic_case("case-1", ("shared",))
    definition = support.StandardBenchmarkAnchorContractDefinition(
        name="synthetic",
        manifest_paths=(manifest_path,),
        expected_anchor_case_ids={
            ("synthetic_boundary.py", "anchored"): ("case-1",),
            ("other_boundary.py", "ignored"): ("case-2",),
        },
        correctness_case_signature=_synthetic_case_signature,
        workload_signature=_synthetic_workload_signature,
        include_workload=_synthetic_workload_is_included,
    )

    monkeypatch.setattr(
        benchmark_support,
        "load_manifest",
        partial(_synthetic_manifest_loader, workloads=(workload,)),
    )
    monkeypatch.setattr(
        anchor_support,
        "published_cases_by_id",
        partial(records_by_string_id, (case,), id_attr="case_id"),
    )

    anchored_pairs = support._expected_anchored_pairs(definition)

    assert len(anchored_pairs) == 1
    anchored_pair = anchored_pairs[0]
    assert anchored_pair.manifest_name == "synthetic_boundary.py"
    assert anchored_pair.workload_id == "anchored"
    assert anchored_pair.case_id == "case-1"
    assert anchored_pair.workload is workload
    assert anchored_pair.case is case


def test_standard_benchmark_definitions_are_support_owned_tuple_used_by_helper_paths() -> None:
    import inspect

    assert isinstance(support.STANDARD_BENCHMARK_DEFINITIONS, tuple)
    assert tuple(
        parameter.values[0]
        for parameter in support._standard_benchmark_definition_params(
            include_definition=lambda _: True
        )
    ) == support.STANDARD_BENCHMARK_DEFINITIONS

    support_source = inspect.getsource(support)
    assert "for definition in STANDARD_BENCHMARK_DEFINITIONS" in support_source
    assert "for definition in _standard_benchmark_definitions()" not in support_source
    assert _build_standard_benchmark_definition_splice_names() == (
        "COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS",
        "COLLECTION_REPLACEMENT_STANDARD_BENCHMARK_DEFINITIONS",
        "MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS",
        "COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS",
        "COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS",
        "PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS",
        "SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS",
    )


@pytest.mark.parametrize(
    ("owner_definitions", "preceding_definition_name", "following_definition_name"),
    (
        pytest.param(
            compile_proxy_support.COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS,
            None,
            "collection-replacement-module-positional-indexlike",
            id="compile-proxy-before-collection-replacement",
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
            anchor_support.SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS,
            "pattern-boundary-wrong-text-model",
            None,
            id="source-tree-standard-after-pattern-boundary",
        ),
    ),
)
def test_standard_inventory_keeps_source_tree_owner_blocks_at_expected_boundaries(
    owner_definitions: tuple[Any, ...],
    preceding_definition_name: str,
    following_definition_name: str | None,
) -> None:
    standard_definitions = support.STANDARD_BENCHMARK_DEFINITIONS
    standard_names = _definition_names(standard_definitions)
    owner_names = _definition_names(owner_definitions)

    first_owner_index = standard_names.index(owner_names[0])
    if preceding_definition_name is None:
        assert first_owner_index == 0
    else:
        assert standard_names[first_owner_index - 1] == preceding_definition_name

    standard_owner_slice = standard_definitions[
        first_owner_index : first_owner_index + len(owner_definitions)
    ]
    assert _definition_names(standard_owner_slice) == owner_names
    assert all(
        standard_definition is owner_definition
        for standard_definition, owner_definition in zip(
            standard_owner_slice, owner_definitions, strict=True
        )
    )
    next_index = first_owner_index + len(owner_definitions)
    if following_definition_name is None:
        assert next_index == len(standard_names)
    else:
        assert standard_names[next_index] == following_definition_name


@pytest.mark.parametrize(
    "owner_definitions",
    (
        pytest.param(
            compile_proxy_support.COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS,
            id="compile-proxy",
        ),
        pytest.param(
            collection_replacement_support.COLLECTION_REPLACEMENT_STANDARD_BENCHMARK_DEFINITIONS,
            id="collection-replacement",
        ),
        pytest.param(
            anchor_support.MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS,
            id="module-workflow-keyword",
        ),
        pytest.param(
            compiled_pattern_module_compile_support.COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS,
            id="compiled-pattern-module-compile",
        ),
        pytest.param(
            compiled_pattern_module_helper_support.COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS,
            id="compiled-pattern-module-helper",
        ),
        pytest.param(
            pattern_boundary_support.PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS,
            id="pattern-boundary",
        ),
        pytest.param(
            anchor_support.SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS,
            id="source-tree-standard",
        ),
    ),
)
def test_standard_inventory_splices_each_owner_tuple_once_and_contiguously(
    owner_definitions: tuple[Any, ...],
) -> None:
    standard_definitions = support.STANDARD_BENCHMARK_DEFINITIONS
    owner_names = _definition_names(owner_definitions)
    matching_indexes = tuple(
        index
        for index, definition in enumerate(standard_definitions)
        if definition.name in owner_names
    )

    assert len(matching_indexes) == len(owner_definitions)
    assert matching_indexes == tuple(
        range(matching_indexes[0], matching_indexes[0] + len(owner_definitions))
    )

    standard_owner_slice = tuple(
        standard_definitions[index] for index in matching_indexes
    )
    assert _definition_names(standard_owner_slice) == owner_names
    assert standard_owner_slice == owner_definitions
    assert all(
        standard_definition is owner_definition
        for standard_definition, owner_definition in zip(
            standard_owner_slice,
            owner_definitions,
            strict=True,
        )
    )


def test_standard_support_source_no_longer_inlines_collection_replacement_definitions(
) -> None:
    import inspect

    support_source = inspect.getsource(support)
    for definition_name in (
        "collection-replacement-module-positional-indexlike",
        "collection-replacement-keyword",
        "collection-replacement-compiled-pattern-literal-success",
        "collection-replacement-compiled-pattern-wrong-text-model",
        "pattern-helper-collection-replacement-wrong-text-model",
        "collection-replacement-pattern-findall-bounded",
        "collection-replacement-pattern-finditer-bounded",
        "collection-replacement-pattern-split",
        "collection-replacement-module-literal-replacement",
        "collection-replacement-pattern-literal-replacement",
        "collection-replacement-grouped-callable-replacement",
    ):
        assert f'name="{definition_name}"' not in support_source


def test_standard_support_source_no_longer_mentions_compile_proxy_helpers_or_inline_definition(
) -> None:
    import inspect

    support_source = inspect.getsource(support)

    assert "COMPILE_MATRIX_MANIFEST_PATH" not in support_source
    assert "REGRESSION_MATRIX_MANIFEST_PATH" not in support_source
    assert "compile_proxy_correctness_case_signature" not in support_source
    assert "compile_proxy_workload_signature" not in support_source
    assert "is_compile_proxy_workload" not in support_source
    assert 'name="compile-proxy"' not in support_source


def test_standard_support_source_no_longer_mentions_source_tree_manifest_path_constants(
) -> None:
    import inspect

    support_source = inspect.getsource(support)

    for constant_name in SOURCE_TREE_MANIFEST_PATH_CONSTANT_NAMES:
        assert constant_name not in support_source


def test_standard_support_imports_only_compile_proxy_owner_tuple() -> None:
    import inspect

    support_source = inspect.getsource(support)
    parsed_support_source = ast.parse(support_source)

    imported_names = {
        alias.name
        for node in ast.walk(parsed_support_source)
        if isinstance(node, ast.ImportFrom)
        and node.module == "tests.benchmarks.compile_proxy_benchmark_support"
        for alias in node.names
    }

    assert imported_names == {"COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS"}
    assert "*COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS," in support_source
    assert "_build_compile_proxy_standard_benchmark_definitions" not in support_source


def test_standard_inventory_reuses_owner_owned_compile_proxy_definition() -> None:
    owner_definitions = compile_proxy_support.COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS

    assert len(owner_definitions) == 1
    assert owner_definitions[0].name == "compile-proxy"
    assert support.STANDARD_BENCHMARK_DEFINITIONS[0] is owner_definitions[0]


def test_standard_support_source_no_longer_inlines_pattern_boundary_definitions() -> None:
    import inspect

    support_source = inspect.getsource(support)
    for definition_name in (
        "pattern-window-positional-indexlike",
        "pattern-window-keyword",
        "pattern-boundary-bounded-wildcard",
        "pattern-boundary-verbose-regression",
        "pattern-boundary-wrong-text-model",
    ):
        assert f'name="{definition_name}"' not in support_source


def test_standard_support_source_no_longer_inlines_module_workflow_keyword_definitions(
) -> None:
    import inspect

    support_source = inspect.getsource(support)
    for definition_name in (
        "module-workflow-keyword-flags",
        "module-workflow-keyword-errors",
    ):
        assert f'name="{definition_name}"' not in support_source


def test_standard_support_source_no_longer_inlines_source_tree_standard_definitions(
) -> None:
    import inspect

    support_source = inspect.getsource(support)
    for definition_name in (
        "optional-group-conditional",
        "nested-group",
        "exact-repeat",
        "ranged-repeat",
        "grouped-alternation",
        "grouped-alternation-replacement",
        "nested-group-replacement",
        "open-ended-grouped-alternation",
    ):
        assert f'name="{definition_name}"' not in support_source


def test_standard_support_imports_only_pattern_boundary_owner_tuple() -> None:
    import inspect

    support_source = inspect.getsource(support)
    parsed_support_source = ast.parse(support_source)

    imported_names = {
        alias.name
        for node in ast.walk(parsed_support_source)
        if isinstance(node, ast.ImportFrom)
        and node.module == "tests.benchmarks.pattern_boundary_benchmark_anchor_support"
        for alias in node.names
    }

    assert imported_names == {"PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS"}


def test_standard_support_imports_and_splices_module_workflow_keyword_owner_tuple(
) -> None:
    import inspect

    support_source = inspect.getsource(support)
    imported_names = _build_standard_benchmark_definition_imported_names(
        "tests.benchmarks.source_tree_benchmark_anchor_support"
    )

    assert imported_names == {
        "MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS",
        "SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS",
    }
    assert "*MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS," in support_source


def test_standard_support_imports_only_compiled_pattern_module_compile_owner_tuple() -> None:
    import inspect

    support_source = inspect.getsource(support)
    parsed_support_source = ast.parse(support_source)

    imported_names = {
        alias.name
        for node in ast.walk(parsed_support_source)
        if isinstance(node, ast.ImportFrom)
        and node.module
        == "tests.benchmarks.compiled_pattern_module_compile_benchmark_support"
        for alias in node.names
    }

    assert imported_names == {
        "COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS"
    }
    assert (
        "*COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS,"
        in support_source
    )
    assert "_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS" not in support_source
    assert "_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS" not in support_source
    assert "owner_spec.anchor_definition(" not in support_source


def test_standard_support_imports_and_splices_source_tree_standard_owner_tuple() -> None:
    import inspect

    support_source = inspect.getsource(support)
    imported_names = _build_standard_benchmark_definition_imported_names(
        "tests.benchmarks.source_tree_benchmark_anchor_support"
    )

    assert imported_names == {
        "MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS",
        "SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS",
    }
    assert "*SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS," in support_source


def test_standard_support_source_no_longer_inlines_compiled_pattern_module_helper_definitions(
) -> None:
    import inspect

    support_source = inspect.getsource(support)
    for definition_name in (
        "module-workflow-compiled-pattern-literal-success",
        "module-workflow-compiled-pattern-bounded-wildcard-success",
        "module-workflow-compiled-pattern-verbose-bytes-success",
        "module-workflow-compiled-pattern-wrong-text-model",
    ):
        assert f'name="{definition_name}"' not in support_source


def test_standard_inventory_reuses_owner_owned_collection_replacement_definition_objects(
) -> None:
    owner_definitions = (
        collection_replacement_support.COLLECTION_REPLACEMENT_STANDARD_BENCHMARK_DEFINITIONS
    )
    standard_definitions = tuple(
        definition
        for definition in support.STANDARD_BENCHMARK_DEFINITIONS
        if definition.name.startswith("collection-replacement-")
        or definition.name == "pattern-helper-collection-replacement-wrong-text-model"
    )

    assert standard_definitions == owner_definitions


def test_standard_inventory_reuses_owner_owned_pattern_boundary_definition_objects(
) -> None:
    owner_definitions = (
        pattern_boundary_support.PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS
    )
    standard_definitions = tuple(
        definition
        for definition in support.STANDARD_BENCHMARK_DEFINITIONS
        if definition.name.startswith("pattern-window-")
        or definition.name.startswith("pattern-boundary-")
    )

    assert standard_definitions == owner_definitions


def test_standard_inventory_reuses_owner_owned_compiled_pattern_module_helper_definition_objects(
) -> None:
    definition_names = {
        "module-workflow-compiled-pattern-literal-success",
        "module-workflow-compiled-pattern-bounded-wildcard-success",
        "module-workflow-compiled-pattern-verbose-bytes-success",
        "module-workflow-compiled-pattern-wrong-text-model",
    }
    owner_definitions = (
        compiled_pattern_module_helper_support.COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS
    )
    standard_definitions = tuple(
        definition
        for definition in support.STANDARD_BENCHMARK_DEFINITIONS
        if definition.name in definition_names
    )

    assert standard_definitions == owner_definitions


def test_standard_inventory_reuses_owner_owned_compiled_pattern_module_compile_definition_objects(
) -> None:
    owner_definitions = (
        compiled_pattern_module_compile_support.COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS
    )
    definition_names = _definition_names(owner_definitions)
    standard_names = _definition_names(support.STANDARD_BENCHMARK_DEFINITIONS)
    first_owner_index = standard_names.index(definition_names[0])
    standard_definitions = support.STANDARD_BENCHMARK_DEFINITIONS[
        first_owner_index : first_owner_index + len(owner_definitions)
    ]

    assert _definition_names(standard_definitions) == definition_names
    assert standard_definitions == owner_definitions
    assert all(
        standard_definition is owner_definition
        for standard_definition, owner_definition in zip(
            standard_definitions,
            owner_definitions,
            strict=True,
        )
    )


def test_combined_suite_imports_support_owned_standard_benchmark_definitions() -> None:
    import importlib
    import inspect

    combined_suite = importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )

    assert (
        combined_suite.STANDARD_BENCHMARK_DEFINITIONS
        is support.STANDARD_BENCHMARK_DEFINITIONS
    )
    combined_source = inspect.getsource(combined_suite)
    assert "STANDARD_BENCHMARK_DEFINITIONS" in combined_source
    assert "_STANDARD_BENCHMARK_DEFINITIONS = (" not in combined_source


def test_support_module_no_longer_uses_combined_suite_proxy_path() -> None:
    import inspect

    support_source = inspect.getsource(support)
    assert "test_source_tree_combined_boundary_benchmarks as combined_suite" not in support_source
    assert "return combined_suite._STANDARD_BENCHMARK_DEFINITIONS" not in support_source
    assert "class _StandardBenchmarkDefinitionsProxy" not in support_source
    assert "STANDARD_BENCHMARK_DEFINITIONS = _StandardBenchmarkDefinitionsProxy()" not in support_source


@pytest.mark.parametrize(
    ("definition", "manifest_path"),
    support._standard_benchmark_manifest_params(),
)
def test_standard_benchmark_manifest_keeps_expected_workloads_in_scope(
    definition: support.StandardBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
) -> None:
    workloads = load_manifest(manifest_path).workloads
    assert {
        workload.workload_id
        for workload in workloads
        if workload.workload_id in definition.expected_excluded_workload_ids
    } == definition.expected_excluded_workload_ids
    assert {
        workload.workload_id
        for workload in workloads
        if workload.workload_id in definition.expected_legacy_workload_ids
    } == definition.expected_legacy_workload_ids
    assert tuple(
        workload.workload_id
        for workload in workloads
        if definition.includes_workload(workload)
    ) == support._expected_workload_ids(definition, manifest_path)


@pytest.mark.parametrize(
    ("definition", "manifest_path"),
    support._standard_benchmark_manifest_params(),
)
def test_standard_benchmark_workloads_stay_anchored_to_published_correctness_cases(
    definition: support.StandardBenchmarkAnchorContractDefinition,
    manifest_path: pathlib.Path,
) -> None:
    assert support._unanchored_case_ids(definition, manifest_path) == ()


@pytest.mark.parametrize(
    "definition",
    support.STANDARD_BENCHMARK_DEFINITIONS,
    ids=support._standard_benchmark_definition_id,
)
def test_standard_benchmark_workloads_stay_pinned_to_exact_case_ids(
    definition: support.StandardBenchmarkAnchorContractDefinition,
) -> None:
    assert support._anchored_case_ids(definition) == definition.expected_anchor_case_ids


@pytest.mark.parametrize(
    "definition",
    support._standard_benchmark_definition_params(
        include_definition=support._has_standard_benchmark_special_unanchored_workloads
    ),
)
def test_standard_benchmark_special_unanchored_workloads_stay_explicit(
    definition: support.StandardBenchmarkAnchorContractDefinition,
) -> None:
    assert tuple(
        workload_id
        for manifest_path in definition.manifest_paths
        for workload_id in support._unanchored_case_ids(
            definition,
            manifest_path,
            include_special_unanchored=True,
        )
    ) == definition.expected_special_unanchored_workload_ids


@pytest.mark.parametrize(
    "definition",
    support._standard_benchmark_definition_params(
        include_definition=(
            support._has_standard_benchmark_special_unanchored_direct_parity_cases
        )
    ),
)
def test_standard_benchmark_special_unanchored_bytes_workloads_stay_covered_by_direct_parity_cases(
    definition: support.StandardBenchmarkAnchorContractDefinition,
) -> None:
    workloads_by_id = support._definition_workloads_by_id(definition)
    direct_parity_case_ids = support._direct_parity_case_ids_by_signature(
        definition.direct_parity_supplemental_cases
    )
    uncovered_workload_ids: list[str] = []

    for workload_id in definition.expected_special_unanchored_workload_ids:
        workload = workloads_by_id[workload_id]
        if workload.text_model != "bytes":
            continue
        if workload.operation not in {"module.search", "pattern.fullmatch"}:
            raise AssertionError(
                "expected bytes special-unanchored workload to stay on a direct-parity "
                f"search/fullmatch path, got {workload.operation!r}"
            )

        signature = (
            workload.operation,
            workload.pattern_payload(),
            workload.haystack_payload(),
        )
        case_ids = direct_parity_case_ids.get(signature)
        if case_ids is None:
            uncovered_workload_ids.append(workload_id)
            continue

        assert len(case_ids) == 1

    assert uncovered_workload_ids == []


@pytest.mark.parametrize(
    "definition",
    support._standard_benchmark_definition_params(
        include_definition=support._has_standard_benchmark_legacy_workloads
    ),
)
def test_standard_benchmark_legacy_workloads_stay_pinned_to_expected_case_ids(
    definition: support.StandardBenchmarkAnchorContractDefinition,
) -> None:
    assert {
        key: case_ids
        for key, case_ids in support._anchored_case_ids(definition).items()
        if key[1] in definition.expected_legacy_workload_ids
    } == support._expected_legacy_anchor_case_ids(definition)


@pytest.mark.parametrize(
    "definition",
    support._standard_benchmark_definition_params(
        include_definition=support._runs_standard_benchmark_callback_result_parity
    ),
)
def test_standard_benchmark_workload_callbacks_match_anchor_case_results(
    definition: support.StandardBenchmarkAnchorContractDefinition,
) -> None:
    assert_anchored_workload_case_result_parity(
        support._expected_anchored_pairs(
            definition,
            expected_anchor_case_ids=support._expected_callback_anchor_case_ids(
                definition
            ),
        )
    )


@pytest.mark.parametrize(
    ("definition", "workload_id"),
    support._standard_benchmark_special_unanchored_result_parity_params(),
)
def test_standard_benchmark_special_unanchored_workloads_match_manual_cpython_dispatch(
    definition: support.StandardBenchmarkAnchorContractDefinition,
    workload_id: str,
) -> None:
    workload = support._definition_workloads_by_id(definition)[workload_id]
    assert_benchmark_workload_matches_expected_result(
        workload,
        support._manual_expected_result(workload),
    )
