from __future__ import annotations

import ast
from dataclasses import replace
from functools import cache
import importlib
import inspect
import pathlib
import re
import sys
from types import SimpleNamespace

import pytest

from rebar_harness import benchmarks
from tests.benchmarks import benchmark_test_support as support
from tests.benchmarks import (
    test_benchmark_publication_runtime_contracts as publication_runtime_contracts,
)
from tests.conftest import REPO_ROOT, records_by_string_id
from tests.python.fixture_parity_support import IndexLike

anchor_support = support
meta_support = sys.modules[__name__]
collection_replacement_support = importlib.import_module(
    "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
)


def _clear_cached_functions(functions: tuple[object, ...]) -> None:
    for function in functions:
        cache_clear = getattr(function, "cache_clear", None)
        if callable(cache_clear):
            cache_clear()


def _clear_local_meta_support_caches() -> None:
    _clear_cached_functions(
        (
            _parsed_module_ast,
            _benchmark_support_import_targets_by_path,
        )
    )


@pytest.fixture
def anchor_support_cache_guard() -> None:
    support._clear_anchor_support_caches()
    _clear_local_meta_support_caches()
    yield
    _clear_local_meta_support_caches()
    support._clear_anchor_support_caches()


@cache
def _parsed_module_ast(module: object) -> ast.Module:
    return ast.parse(inspect.getsource(module))


def _module_imported_names(module: object, imported_module: str) -> frozenset[str]:
    return frozenset(
        alias.name
        for node in _parsed_module_ast(module).body
        if isinstance(node, ast.ImportFrom) and node.module == imported_module
        for alias in node.names
    )


def _module_import_targets(module: object) -> frozenset[str]:
    return _ast_import_targets(_parsed_module_ast(module))


def _assert_exported_name_matches_owner(
    consumer_module: object,
    owner_module: object,
    name: str,
) -> None:
    consumer_value = getattr(consumer_module, name)
    owner_value = getattr(owner_module, name)

    if inspect.isroutine(consumer_value) or inspect.isclass(consumer_value):
        assert getattr(consumer_value, "__name__", None) == getattr(
            owner_value,
            "__name__",
            None,
        )
        assert getattr(consumer_value, "__module__", None) == getattr(
            owner_value,
            "__module__",
            None,
        )
        consumer_source = inspect.getsourcefile(consumer_value)
        owner_source = inspect.getsourcefile(owner_value)
        if consumer_source is not None or owner_source is not None:
            assert consumer_source is not None
            assert owner_source is not None
            assert pathlib.Path(consumer_source).resolve() == pathlib.Path(
                owner_source
            ).resolve()
        return

    assert consumer_value == owner_value


def _module_function_definition(module: object, function_name: str) -> ast.FunctionDef:
    return next(
        node
        for node in _parsed_module_ast(module).body
        if isinstance(node, ast.FunctionDef) and node.name == function_name
    )


def _module_assignment(module: object, name: str) -> ast.Assign | ast.AnnAssign:
    return next(
        node
        for node in _parsed_module_ast(module).body
        if (
            isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == name
                for target in node.targets
            )
        )
        or (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == name
        )
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


def _ast_import_targets(module_ast: ast.Module) -> frozenset[str]:
    targets: set[str] = set()

    for node in module_ast.body:
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            targets.add(node.module)
        elif isinstance(node, ast.Import):
            targets.update(alias.name for alias in node.names)

    return frozenset(targets)


def _module_alias_names(
    module_ast: ast.AST,
    *,
    import_from_module: str,
    import_name: str,
    dotted_import_name: str,
) -> frozenset[str]:
    module_body = getattr(module_ast, "body", ())
    alias_names: set[str] = set()

    for node in module_body:
        if isinstance(node, ast.ImportFrom) and node.module == import_from_module:
            alias_names.update(
                alias.asname or alias.name
                for alias in node.names
                if alias.name == import_name
            )
            continue

        if isinstance(node, ast.Import):
            alias_names.update(
                alias.asname or alias.name.rsplit(".", 1)[-1]
                for alias in node.names
                if alias.name == dotted_import_name
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

        if isinstance(value, ast.Name) and value.id in alias_names:
            alias_names.update(targets)
            continue

        for target in targets:
            alias_names.discard(target)

    return frozenset(alias_names)


def _top_level_import_from_alias_pairs(
    module_ast: ast.Module,
    *,
    module_name: str,
    imported_names: frozenset[str],
) -> frozenset[tuple[str, str | None]]:
    return frozenset(
        (alias.name, alias.asname)
        for node in module_ast.body
        if isinstance(node, ast.ImportFrom) and node.module == module_name
        for alias in node.names
        if alias.name in imported_names
    )


def _module_attribute_alias_targets(
    module_ast: ast.AST,
    *,
    module_alias_names: frozenset[str],
) -> dict[str, str]:
    attribute_alias_targets: dict[str, str] = {}
    module_body = getattr(module_ast, "body", ())

    for node in module_body:
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

        aliased_attribute: str | None = None
        if (
            isinstance(value, ast.Attribute)
            and isinstance(value.value, ast.Name)
            and value.value.id in module_alias_names
        ):
            aliased_attribute = value.attr
        elif isinstance(value, ast.Name):
            aliased_attribute = attribute_alias_targets.get(value.id)

        if aliased_attribute is None:
            for target in targets:
                attribute_alias_targets.pop(target, None)
            continue

        for target in targets:
            attribute_alias_targets[target] = aliased_attribute

    return attribute_alias_targets


def _owner_definition_manifest_path_names(
    owner_definition: ast.Assign | ast.Return,
) -> tuple[tuple[str, ...], ...]:
    def _manifest_path_name(node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "benchmark_test_support"
        ):
            return node.attr
        raise AssertionError("manifest path definitions must resolve through named support constants")

    value = owner_definition.value
    assert isinstance(value, ast.Tuple)

    manifest_path_names: list[tuple[str, ...]] = []
    for element in value.elts:
        assert isinstance(element, ast.Call)
        manifest_paths_keyword = next(
            keyword
            for keyword in element.keywords
            if keyword.arg == "manifest_paths"
        )
        assert isinstance(manifest_paths_keyword.value, ast.Tuple)
        manifest_path_names.append(
            tuple(
                _manifest_path_name(manifest_path)
                for manifest_path in manifest_paths_keyword.value.elts
            )
        )

    return tuple(manifest_path_names)


def top_level_module_definition_and_assignment_names(
    module: object,
) -> tuple[set[str], set[str]]:
    module_tree = _parsed_module_ast(module)
    definition_names = {
        node.name
        for node in module_tree.body
        if isinstance(node, (ast.AsyncFunctionDef, ast.ClassDef, ast.FunctionDef))
    }
    assignment_names = {
        node.target.id
        for node in module_tree.body
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    }
    assignment_names.update(
        target.id
        for node in module_tree.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    )
    return definition_names, assignment_names


def assert_owner_surface_module_owned_without_local_duplicates(
    caller_module: object,
    owner_module: object,
    *,
    definition_names: tuple[str, ...] = (),
    assignment_names: tuple[str, ...] = (),
    extra_owner_name: str | None = None,
    extra_owner_module: object | None = None,
) -> None:
    local_definition_names, local_assignment_names = (
        top_level_module_definition_and_assignment_names(caller_module)
    )
    local_names = local_definition_names | local_assignment_names
    expected_definition_names = set(definition_names)
    expected_assignment_names = set(assignment_names)

    for name in expected_definition_names | expected_assignment_names:
        assert hasattr(owner_module, name)

    assert expected_definition_names.isdisjoint(local_names)
    assert expected_assignment_names.isdisjoint(local_names)

    if extra_owner_name is None:
        assert extra_owner_module is None
        return

    assert extra_owner_module is not None
    assert hasattr(extra_owner_module, extra_owner_name)
    assert extra_owner_name not in local_names


def assert_mixed_owner_surface(
    caller_module: object,
    *,
    local_function_names: tuple[str, ...] = (),
    local_assignment_names: tuple[str, ...] = (),
    support_alias_assignment_names: tuple[str, ...] = (),
) -> None:
    module_ast = _parsed_module_ast(caller_module)
    parsed_function_names = {
        node.name
        for node in module_ast.body
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef))
    }
    _, parsed_assignment_names = (
        top_level_module_definition_and_assignment_names(caller_module)
    )
    expected_local_function_names = set(local_function_names)
    expected_local_assignment_names = set(local_assignment_names)
    expected_support_alias_assignment_names = set(support_alias_assignment_names)
    shared_module = support
    benchmark_test_support_alias_names = frozenset({"benchmark_test_support"}) | (
        _module_alias_names(
            module_ast,
            import_from_module="tests.benchmarks",
            import_name="benchmark_test_support",
            dotted_import_name="tests.benchmarks.benchmark_test_support",
        )
    )
    benchmark_test_support_attribute_alias_targets = _module_attribute_alias_targets(
        module_ast,
        module_alias_names=benchmark_test_support_alias_names,
    )

    assert expected_local_function_names.isdisjoint(expected_local_assignment_names)
    assert expected_local_function_names.isdisjoint(
        expected_support_alias_assignment_names
    )
    assert expected_local_assignment_names.isdisjoint(
        expected_support_alias_assignment_names
    )

    for function_name in expected_local_function_names:
        assert hasattr(caller_module, function_name)
        assert function_name in parsed_function_names
        assert function_name not in parsed_assignment_names
        assert not hasattr(shared_module, function_name)

    for assignment_name in expected_local_assignment_names:
        assert hasattr(caller_module, assignment_name)
        assert assignment_name in parsed_assignment_names
        assert assignment_name not in parsed_function_names
        assert not hasattr(shared_module, assignment_name)
        assert (
            benchmark_test_support_attribute_alias_targets.get(assignment_name) is None
        )

    for assignment_name in expected_support_alias_assignment_names:
        assert hasattr(caller_module, assignment_name)
        assert assignment_name in parsed_assignment_names
        assert assignment_name not in parsed_function_names
        assignment = _module_assignment(caller_module, assignment_name)
        assert assignment.value is not None
        assert isinstance(assignment.value, ast.Attribute)
        assert isinstance(assignment.value.value, ast.Name)
        assert assignment.value.value.id in benchmark_test_support_alias_names
        assert assignment.value.attr == assignment_name
        _assert_exported_name_matches_owner(
            caller_module,
            shared_module,
            assignment_name,
        )


def _synthetic_manifest(
    *,
    cases: tuple[object, ...] = (),
    workloads: tuple[object, ...] = (),
) -> SimpleNamespace:
    return SimpleNamespace(cases=list(cases), workloads=list(workloads))


def _synthetic_workload(
    workload_id: str,
    signature: tuple[object, ...],
    *,
    include: bool = True,
) -> SimpleNamespace:
    return SimpleNamespace(
        workload_id=workload_id,
        signature=signature,
        include=include,
    )


def _synthetic_manifest_loader(
    _: pathlib.Path,
    *,
    workloads: tuple[object, ...],
) -> SimpleNamespace:
    return _synthetic_manifest(workloads=workloads)


def _module_pattern_case(
    *,
    helper: str,
    operation: str,
    args: tuple[object, ...],
    case_id: str = "",
    kwargs: dict[str, object] | None = None,
    pattern: str = "abc",
    flags: int = 0,
    text_model: str | None = "str",
    use_compiled_pattern: bool = False,
) -> SimpleNamespace:
    pattern_value = pattern.encode() if text_model == "bytes" else pattern
    return SimpleNamespace(
        case_id=case_id,
        helper=helper,
        operation=operation,
        args=args,
        kwargs={} if kwargs is None else kwargs,
        pattern=pattern,
        flags=flags,
        text_model=text_model,
        use_compiled_pattern=use_compiled_pattern,
        pattern_payload=lambda: pattern_value,
        serialized_args=lambda: list(args),
    )


def _synthetic_workload_signature(workload: object) -> tuple[object, ...]:
    return workload.signature


def _synthetic_workload_is_included(workload: object) -> bool:
    return workload.include


def synthetic_workload(
    *,
    manifest_id: str,
    workload_id: str,
    operation: str,
    pattern: str = "abc",
    haystack: str | None = "abc",
    replacement: object | None = None,
    expected_exception: dict[str, str] | None = None,
    flags: int = 0,
    use_compiled_pattern: bool = False,
    count: object = 0,
    maxsplit: object = 0,
    kwargs: dict[str, object] | None = None,
    text_model: str = "str",
    haystack_text_model: str | None = None,
    pos: object | None = None,
    endpos: object | None = None,
    bucket: str | None = None,
    family: str = "module",
    cache_mode: str = "warm",
    timing_scope: str = "module-helper-call",
    warmup_iterations: int = 1,
    sample_iterations: int = 1,
    timed_samples: int = 1,
    notes: list[str] | None = None,
    categories: list[str] | None = None,
    syntax_features: list[str] | None = None,
    smoke: bool = False,
) -> benchmarks.Workload:
    payload: dict[str, object] = {
        "manifest_id": manifest_id,
        "workload_id": workload_id,
        "bucket": operation.replace(".", "-") if bucket is None else bucket,
        "family": family,
        "operation": operation,
        "pattern": pattern,
        "haystack": haystack,
        "replacement": replacement,
        "expected_exception": expected_exception,
        "flags": flags,
        "use_compiled_pattern": use_compiled_pattern,
        "count": count,
        "maxsplit": maxsplit,
        "text_model": text_model,
        "cache_mode": cache_mode,
        "timing_scope": timing_scope,
        "warmup_iterations": warmup_iterations,
        "sample_iterations": sample_iterations,
        "timed_samples": timed_samples,
        "notes": [] if notes is None else notes,
        "categories": [] if categories is None else categories,
        "syntax_features": [] if syntax_features is None else syntax_features,
        "smoke": smoke,
    }
    if kwargs is not None:
        payload["kwargs"] = kwargs
    if haystack_text_model is not None:
        payload["haystack_text_model"] = haystack_text_model
    if pos is not None:
        payload["pos"] = pos
    if endpos is not None:
        payload["endpos"] = endpos
    return benchmarks.workload_from_payload(payload)


def _assert_owner_module_routes_through_package_import(
    module: object,
    *,
    owner_module: str,
    package_module: str,
    expected_alias_pairs: frozenset[tuple[str, str | None]],
) -> None:
    assert package_module in _module_import_targets(module)
    assert owner_module not in _module_import_targets(module)
    assert _top_level_import_from_alias_pairs(
        _parsed_module_ast(module),
        module_name=package_module,
        imported_names=frozenset(name for name, _ in expected_alias_pairs),
    ) == expected_alias_pairs


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

    sys.modules.pop(deleted_module_name, None)
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


def compile_proxy_correctness_case_signature(
    case: object,
) -> tuple[str, str | bytes, tuple[()], tuple[()], int, str] | None:
    if getattr(case, "operation", None) != "compile":
        return None
    pattern = case.pattern_payload() if case.pattern is not None else case.args[0]
    assert isinstance(pattern, (str, bytes))
    return (
        "module.compile",
        pattern,
        (),
        (),
        case.flags or 0,
        case.text_model or "str",
    )


def compile_proxy_workload_signature(
    workload: object,
) -> tuple[str, str | bytes, tuple[()], tuple[()], int, str]:
    pattern = workload.pattern_payload()
    assert isinstance(pattern, (str, bytes))
    return (
        "module.compile",
        pattern,
        (),
        (),
        workload.flags,
        workload.text_model,
    )


def is_compile_proxy_workload(workload: object) -> bool:
    return workload.operation in {"compile", "module.compile"}


COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS = (
    collection_replacement_support.StandardBenchmarkAnchorContractDefinition(
        name="compile-proxy",
        manifest_paths=(
            support.COMPILE_MATRIX_MANIFEST_PATH,
            support.REGRESSION_MATRIX_MANIFEST_PATH,
        ),
        expected_anchor_case_ids={
            (support.COMPILE_MATRIX_MANIFEST_PATH.name, "compile-inline-locale-bytes-warm"): (
                "bytes-inline-locale-flag-success",
            ),
            (support.COMPILE_MATRIX_MANIFEST_PATH.name, "compile-lookbehind-cold"): (
                "str-fixed-width-lookbehind-success",
            ),
            (
                support.COMPILE_MATRIX_MANIFEST_PATH.name,
                "compile-character-class-ignorecase-warm",
            ): ("str-character-class-ignorecase-success",),
            (
                support.COMPILE_MATRIX_MANIFEST_PATH.name,
                "compile-possessive-quantifier-cold",
            ): ("str-possessive-quantifier-success",),
            (support.COMPILE_MATRIX_MANIFEST_PATH.name, "compile-atomic-group-purged"): (
                "str-atomic-group-success",
            ),
            (support.COMPILE_MATRIX_MANIFEST_PATH.name, "compile-parser-stress-cold"): (
                "str-parser-stress-compile-proxy-success",
            ),
            (
                support.REGRESSION_MATRIX_MANIFEST_PATH.name,
                "regression-parser-atomic-lookbehind-cold",
            ): ("str-parser-stress-compile-proxy-success",),
            (
                support.REGRESSION_MATRIX_MANIFEST_PATH.name,
                "regression-parser-bytes-backreference-purged",
            ): ("bytes-named-backreference-compile-proxy-success",),
            (
                support.REGRESSION_MATRIX_MANIFEST_PATH.name,
                "regression-module-compile-verbose-purged",
            ): ("workflow-compile-str-verbose-regression",),
            (
                support.REGRESSION_MATRIX_MANIFEST_PATH.name,
                "regression-module-compile-multiline-purged",
            ): ("workflow-compile-str-multiline-regression",),
            (
                support.REGRESSION_MATRIX_MANIFEST_PATH.name,
                "regression-module-compile-multiline-purged-bytes",
            ): ("workflow-compile-bytes-multiline-regression",),
            (
                support.REGRESSION_MATRIX_MANIFEST_PATH.name,
                "regression-module-compile-verbose-purged-bytes",
            ): ("workflow-compile-bytes-verbose-regression",),
        },
        include_workload=is_compile_proxy_workload,
        correctness_case_signature=compile_proxy_correctness_case_signature,
        workload_signature=compile_proxy_workload_signature,
    ),
)


def _explicit_standard_benchmark_definitions(
) -> tuple[collection_replacement_support.StandardBenchmarkAnchorContractDefinition, ...]:
    return (
        *COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS,
        *collection_replacement_support.COLLECTION_REPLACEMENT_STANDARD_BENCHMARK_DEFINITIONS,
        *collection_replacement_support.MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS,
        *collection_replacement_support.COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS,
        *collection_replacement_support.COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS,
        *collection_replacement_support.PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS,
        *collection_replacement_support.SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS,
    )


def test_write_test_manifest_dedents_and_writes_utf8_text(tmp_path) -> None:
    manifest_path = support._write_test_manifest(
        tmp_path,
        "sample_manifest.py",
        """\
            VALUE = "caf\u00e9"
        """,
    )

    assert manifest_path.read_text(encoding="utf-8") == 'VALUE = "caf\u00e9"\n'
    assert manifest_path.read_bytes() == 'VALUE = "caf\u00e9"\n'.encode("utf-8")


def test_expected_exception_instance_maps_supported_payloads() -> None:
    type_error = collection_replacement_support._expected_exception_instance(
        {
            "type": "TypeError",
            "message_substring": "type payload",
        }
    )
    value_error = collection_replacement_support._expected_exception_instance(
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
    observed_field_names = collection_replacement_support._record_numeric_materialization_fields(
        monkeypatch
    )

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

    collection_replacement_support._assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call(
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

    collection_replacement_support._assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call(
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
    helper_workloads = (
        (
            tuple(
                workload_id
                for expectation in (
                    collection_replacement_support
                    ._CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTATIONS
                )
                for workload_id in expectation.expected_workload_ids
                if not workload_id.endswith("-bytes")
            ),
            (
                _synthetic_workload(
                    "conditional-callable-str-slice",
                    ("callable-str",),
                ),
            ),
        ),
        (
            tuple(
                workload_id
                for expectation in (
                    collection_replacement_support
                    ._CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTATIONS
                )
                for workload_id in expectation.expected_workload_ids
                if workload_id.endswith("-bytes")
            ),
            (
                _synthetic_workload(
                    "conditional-callable-bytes-slice",
                    ("callable-bytes",),
                ),
            ),
        ),
        (
            collection_replacement_support._CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_REPLACEMENT_EXPECTATION.expected_workload_ids,
            (
                _synthetic_workload(
                    "conditional-nested-callable-bytes",
                    ("nested-bytes",),
                ),
            ),
        ),
        (
            collection_replacement_support._CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_REPLACEMENT_EXPECTATION.expected_workload_ids,
            (
                _synthetic_workload(
                    "conditional-quantified-callable-bytes",
                    ("quantified-bytes",),
                ),
            ),
        ),
        (
            collection_replacement_support.CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS,
            (
                _synthetic_workload(
                    "conditional-alternation-callable-bytes",
                    ("alternation-bytes",),
                ),
            ),
        ),
    )
    expected_source_tree_calls = [
        (
            benchmarks.BENCHMARK_WORKLOADS_ROOT
            / "conditional_group_exists_boundary.py",
            workload_ids,
        )
        for workload_ids, _ in helper_workloads
    ]
    helper_workloads_by_expected_ids = {
        workload_ids: result for workload_ids, result in helper_workloads
    }

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
        return helper_workloads_by_expected_ids[workload_ids]

    monkeypatch.setattr(support, "load_manifest", _load_manifest)
    monkeypatch.setattr(
        collection_replacement_support,
        "published_case_ids_by_signature",
        _published_case_ids_by_signature,
    )
    monkeypatch.setattr(
        collection_replacement_support,
        "published_cases_by_id",
        _published_cases_by_id,
    )
    assert anchor_support.benchmark_test_support is support
    assert collection_replacement_support is not anchor_support
    assert collection_replacement_support.benchmark_test_support is support
    monkeypatch.setattr(support, "live_manifest_workloads", _live_manifest_workloads)

    support._clear_anchor_support_caches()

    assert support.live_manifest_workload(manifest_path, "anchored") is workloads[0]
    assert collection_replacement_support.published_case_ids_by_signature(
        _synthetic_workload_signature
    ) == {("shared",): ("case-1",)}
    assert collection_replacement_support.published_cases_by_id() is published_cases
    for workload_ids, expected_workloads in helper_workloads:
        assert (
            support.live_manifest_workloads(
                benchmarks.BENCHMARK_WORKLOADS_ROOT
                / "conditional_group_exists_boundary.py",
                workload_ids,
            )
            == expected_workloads
        ), workload_ids
    assert manifest_load_calls == [manifest_path]
    assert published_case_id_calls == [_synthetic_workload_signature]
    assert published_cases_calls == ["called"]
    assert source_tree_live_manifest_calls == expected_source_tree_calls

    assert support.live_manifest_workload(manifest_path, "anchored") is workloads[0]
    assert collection_replacement_support.published_case_ids_by_signature(
        _synthetic_workload_signature
    ) == {("shared",): ("case-1",)}
    assert collection_replacement_support.published_cases_by_id() is published_cases
    for workload_ids, expected_workloads in helper_workloads:
        assert (
            support.live_manifest_workloads(
                benchmarks.BENCHMARK_WORKLOADS_ROOT
                / "conditional_group_exists_boundary.py",
                workload_ids,
            )
            == expected_workloads
        ), workload_ids
    assert manifest_load_calls == [manifest_path]
    assert published_case_id_calls == [_synthetic_workload_signature]
    assert published_cases_calls == ["called"]
    assert source_tree_live_manifest_calls == (
        expected_source_tree_calls + expected_source_tree_calls
    )

    support._clear_anchor_support_caches()

    assert support.live_manifest_workload(manifest_path, "anchored") is workloads[0]
    assert collection_replacement_support.published_case_ids_by_signature(
        _synthetic_workload_signature
    ) == {("shared",): ("case-1",)}
    assert collection_replacement_support.published_cases_by_id() is published_cases
    for workload_ids, expected_workloads in helper_workloads:
        assert (
            support.live_manifest_workloads(
                benchmarks.BENCHMARK_WORKLOADS_ROOT
                / "conditional_group_exists_boundary.py",
                workload_ids,
            )
            == expected_workloads
        ), workload_ids
    assert manifest_load_calls == [manifest_path, manifest_path]
    assert published_case_id_calls == [
        _synthetic_workload_signature,
        _synthetic_workload_signature,
    ]
    assert published_cases_calls == ["called", "called"]
    assert source_tree_live_manifest_calls == (
        expected_source_tree_calls
        + expected_source_tree_calls
        + expected_source_tree_calls
    )


def test_clear_anchor_support_caches_clears_cacheable_objects_from_owner_modules(
    monkeypatch,
    anchor_support_cache_guard: None,
) -> None:
    class _CacheRecorder:
        def __init__(self) -> None:
            self.calls = 0

        def cache_clear(self) -> None:
            self.calls += 1

    combined_suite_cache = _CacheRecorder()

    monkeypatch.setitem(
        support.sys.modules,
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks",
        SimpleNamespace(
            cached_source_tree_helper=combined_suite_cache,
            uncached_helper=object(),
        ),
    )

    support._clear_anchor_support_caches()

    assert combined_suite_cache.calls == 1


def test_clear_anchor_support_caches_resets_shared_ast_import_helpers(
    monkeypatch,
    anchor_support_cache_guard: None,
) -> None:
    fake_module = object()
    source = ["from alpha import beta\n"]
    getsource_calls: list[object] = []

    def _getsource(module: object) -> str:
        getsource_calls.append(module)
        assert module is fake_module
        return source[0]

    monkeypatch.setattr(inspect, "getsource", _getsource)

    assert _module_imported_names(fake_module, "alpha") == frozenset({"beta"})
    assert _module_import_targets(fake_module) == frozenset({"alpha"})
    assert getsource_calls == [fake_module]

    source[0] = "from gamma import delta\n"

    assert _module_imported_names(fake_module, "gamma") == frozenset()
    assert _module_import_targets(fake_module) == frozenset({"alpha"})
    assert getsource_calls == [fake_module]

    _clear_local_meta_support_caches()

    assert _module_imported_names(fake_module, "gamma") == frozenset({"delta"})
    assert _module_import_targets(fake_module) == frozenset({"gamma"})
    assert getsource_calls == [fake_module, fake_module]

def test_source_tree_contract_manifest_workload_payload_drops_fields_and_injects_metadata(
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
    spec = collection_replacement_support._SourceTreeContractBuilderSpec(
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

    manifest = collection_replacement_support._source_tree_contract_manifest(
        (source_workload,),
        spec=spec,
    )
    payload = manifest["workloads"][0]

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
    assert not hasattr(support, "_source_tree_contract_manifest")
    assert hasattr(collection_replacement_support, "_source_tree_contract_manifest")


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
    spec = collection_replacement_support._SourceTreeContractBuilderSpec(
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

    workload = collection_replacement_support._source_tree_contract_workload(
        source_workload,
        spec=spec,
    )
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


def test_source_tree_contract_workload_preserves_source_timing_scope_but_drops_notes_without_builder_metadata(
) -> None:
    source_workload = synthetic_workload(
        manifest_id="source-manifest",
        workload_id="module-findall-cold-str",
        operation="module.findall",
        pattern="abc",
        haystack="abcabc",
        timing_scope="pattern-helper-call",
        notes=["source workload note"],
        categories=["source-category"],
        syntax_features=["source-syntax"],
        smoke=True,
    )
    spec = collection_replacement_support._SourceTreeContractBuilderSpec(
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
    )

    workload = collection_replacement_support._source_tree_contract_workload(
        source_workload,
        spec=spec,
    )
    payload = benchmarks.workload_to_payload(workload)

    assert payload["manifest_id"] == "contract-manifest"
    assert payload["workload_id"] == "module-findall-cold-str-contract"
    assert payload["warmup_iterations"] == 1
    assert payload["sample_iterations"] == 1
    assert payload["timed_samples"] == 1
    assert payload["categories"] == []
    assert payload["syntax_features"] == []
    assert payload["smoke"] is False
    assert payload["timing_scope"] == "pattern-helper-call"
    assert payload["notes"] == []


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
    spec = collection_replacement_support._SourceTreeContractBuilderSpec(
        manifest_id="contract-manifest",
        excluded_fields=frozenset({"manifest_id", "workload_id"}),
        manifest_timed_samples=7,
    )

    manifest = collection_replacement_support._source_tree_contract_manifest(
        source_workloads,
        spec=spec,
    )

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
    assert collection_replacement_support.compiled_pattern_contract_expected_build_calls(
        workload,
        label="source-tree test",
    ) == expected_calls


def test_compiled_pattern_contract_expected_build_calls_rejects_unknown_cache_mode() -> None:
    workload = support.live_manifest_workload(
        "module_boundary.py",
        "module-search-literal-warm-hit-str-compiled-pattern",
    )
    mutated_workload = replace(workload, cache_mode="cold")

    with pytest.raises(
        AssertionError,
        match="unexpected compiled-pattern source-tree test workload cache mode 'cold'",
    ):
        collection_replacement_support.compiled_pattern_contract_expected_build_calls(
            mutated_workload,
            label="source-tree test",
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

    source_workloads = collection_replacement_support._contract_source_workloads(
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
        collection_replacement_support._contract_source_workloads(
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


def test_support_module_does_not_export_compile_proxy_meta_only_surface(
) -> None:
    for name in (
        "compile_proxy_correctness_case_signature",
        "compile_proxy_workload_signature",
        "is_compile_proxy_workload",
        "COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS",
    ):
        assert not hasattr(support, name)


def test_compile_proxy_standard_definition_export_is_direct_global(
) -> None:
    first_export = getattr(meta_support, "COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS")
    second_export = getattr(meta_support, "COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS")

    assert first_export is second_export
    assert len(first_export) == 1
    assert first_export[0].name == "compile-proxy"
    assert vars(meta_support)["COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS"] is first_export


def test_compile_proxy_standard_definition_preserves_manifest_order_and_anchor_mapping(
) -> None:
    definition = COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS[0]

    assert support.COMPILE_MATRIX_MANIFEST_PATH == (
        REPO_ROOT / "benchmarks" / "workloads" / "compile_matrix.py"
    )
    assert support.REGRESSION_MATRIX_MANIFEST_PATH == (
        REPO_ROOT / "benchmarks" / "workloads" / "regression_matrix.py"
    )
    assert definition.manifest_paths == (
        support.COMPILE_MATRIX_MANIFEST_PATH,
        support.REGRESSION_MATRIX_MANIFEST_PATH,
    )
    assert definition.expected_anchor_case_ids == (
        collection_replacement_support._definition_anchor_expectations(
            support.COMPILE_MATRIX_MANIFEST_PATH,
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
        | collection_replacement_support._definition_anchor_expectations(
            support.REGRESSION_MATRIX_MANIFEST_PATH,
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
    definition = COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS[0]

    assert definition.include_workload is is_compile_proxy_workload
    assert (
        definition.correctness_case_signature
        is compile_proxy_correctness_case_signature
    )
    assert definition.workload_signature is compile_proxy_workload_signature


def test_standard_benchmark_param_helpers_require_explicit_definition_inventory() -> None:
    standard_definitions = _explicit_standard_benchmark_definitions()

    assert not hasattr(support, "STANDARD_BENCHMARK_DEFINITIONS")
    assert tuple(
        parameter.values[0]
        for parameter in collection_replacement_support._standard_benchmark_definition_params(
            standard_definitions,
            include_definition=lambda _: True
        )
    ) == standard_definitions

    support_ast = _parsed_module_ast(support)
    owner_ast = _parsed_module_ast(collection_replacement_support)
    assert not any(
        isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name)
            and target.id == "STANDARD_BENCHMARK_DEFINITIONS"
            for target in node.targets
        )
        for node in support_ast.body
    )
    assert not any(
        isinstance(node, ast.FunctionDef)
        and node.name == "_build_standard_benchmark_definitions"
        for node in support_ast.body
    )
    assert not any(
        isinstance(node, ast.FunctionDef)
        and node.name == "_standard_benchmark_definition_params"
        for node in support_ast.body
    )
    assert any(
        isinstance(node, ast.FunctionDef)
        and node.name == "_standard_benchmark_definition_params"
        for node in owner_ast.body
    )
    helper_definition = _module_function_definition(
        collection_replacement_support,
        "_standard_benchmark_definition_params",
    )
    assert tuple(argument.arg for argument in helper_definition.args.args) == (
        "definitions",
    )
    assert not any(
        isinstance(node, ast.Name)
        and node.id == "STANDARD_BENCHMARK_DEFINITIONS"
        for node in ast.walk(helper_definition)
    )


@pytest.mark.parametrize(
    ("owner_definitions", "preceding_definition_name", "following_definition_name"),
    (
        pytest.param(
            COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS,
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
            collection_replacement_support.MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS,
            "collection-replacement-grouped-callable-replacement",
            "module-workflow-compiled-pattern-module-compile-literal-success",
            id="module-workflow-keyword-after-collection-replacement",
        ),
        pytest.param(
            collection_replacement_support.COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS,
            "module-workflow-keyword-errors",
            "module-workflow-compiled-pattern-literal-success",
            id="compiled-pattern-module-compile-after-module-workflow-keyword",
        ),
        pytest.param(
            collection_replacement_support.COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS,
            "module-workflow-compiled-pattern-module-compile-flags-ignorecase-keyword-rejection-named-group",
            "pattern-window-positional-indexlike",
            id="compiled-pattern-module-helper-after-module-compile",
        ),
        pytest.param(
            collection_replacement_support.PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS,
            "module-workflow-compiled-pattern-verbose-bytes-success",
            "module-workflow-compiled-pattern-wrong-text-model",
            id="pattern-boundary-after-compiled-pattern-helper",
        ),
        pytest.param(
            collection_replacement_support.SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS,
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
    standard_definitions = _explicit_standard_benchmark_definitions()
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


def test_source_tree_combined_suite_owns_compiled_pattern_module_compile_standard_definitions(
) -> None:
    support_definition_names, support_assignment_names = (
        top_level_module_definition_and_assignment_names(support)
    )
    definition_names, assignment_names = (
        top_level_module_definition_and_assignment_names(
            collection_replacement_support
        )
    )
    source = (
        REPO_ROOT
        / "tests"
        / "benchmarks"
        / "test_source_tree_combined_boundary_benchmarks.py"
    ).read_text(encoding="utf-8")

    assert (
        "_build_compiled_pattern_module_compile_standard_benchmark_definitions"
        not in support_definition_names
    )
    assert "COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS" not in (
        support_definition_names | support_assignment_names
    )
    assert "COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS" in assignment_names
    assert (
        re.search(
            r"^COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS\s*=\s*tuple\(",
            source,
            re.MULTILINE,
        )
        is not None
    )


def test_source_tree_combined_suite_owns_compiled_pattern_module_compile_helper_surface(
) -> None:
    helper_names = {
        "_compiled_pattern_module_compile_keyword_kwargs_signature",
        "_module_workflow_compiled_pattern_compile_correctness_case_signature",
        "_module_workflow_compiled_pattern_compile_workload_signature",
        "_is_module_workflow_compiled_pattern_compile_workload",
        "_is_module_workflow_compiled_pattern_compile_success_workload",
        "_workload_matches_expected_exception",
        "_module_workflow_compiled_pattern_compile_keyword_correctness_case_signature",
        "_module_workflow_compiled_pattern_compile_keyword_workload_signature",
        "_is_module_workflow_compiled_pattern_compile_keyword_workload",
    }

    shared_definition_names, shared_assignment_names = (
        top_level_module_definition_and_assignment_names(support)
    )
    owner_definition_names, owner_assignment_names = (
        top_level_module_definition_and_assignment_names(collection_replacement_support)
    )
    shared_names = shared_definition_names | shared_assignment_names
    owner_names = owner_definition_names | owner_assignment_names

    assert helper_names.isdisjoint(shared_names)
    assert helper_names.issubset(owner_names)
    for helper_name in helper_names:
        assert not hasattr(support, helper_name)
        assert getattr(collection_replacement_support, helper_name).__module__ == (
            collection_replacement_support.__name__
        )


def test_source_tree_combined_suite_owns_compile_contract_round_trip_helper() -> None:
    source = (
        REPO_ROOT
        / "tests"
        / "benchmarks"
        / "test_source_tree_combined_boundary_benchmarks.py"
    ).read_text(encoding="utf-8")
    support_source = (
        REPO_ROOT / "tests" / "benchmarks" / "benchmark_test_support.py"
    ).read_text(encoding="utf-8")

    assert re.search(
        r"^def _assert_compiled_pattern_module_compile_contract_payload_round_trip_common\(",
        source,
        re.MULTILINE,
    )
    assert (
        re.search(
            r"^def _assert_compiled_pattern_module_compile_contract_payload_round_trip_common\(",
            support_source,
            re.MULTILINE,
        )
        is None
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

    assert collection_replacement_support._is_module_workflow_keyword_flags_workload(
        workload
    )
    assert collection_replacement_support._module_workflow_keyword_workload_args(
        workload
    ) == ("zabc",)
    assert collection_replacement_support._module_workflow_keyword_workload_signature(
        workload
    ) == (
        "module.search",
        "abc",
        ("zabc",),
        (("flags", "indexlike", 2),),
        2,
        "str",
    )
    assert collection_replacement_support._module_workflow_keyword_correctness_case_signature(
        case
    ) == (
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

    assert collection_replacement_support._is_module_workflow_keyword_error_workload(
        workload
    )
    assert collection_replacement_support._module_workflow_keyword_workload_args(
        workload
    ) == ("zabc", 4)
    assert collection_replacement_support._module_workflow_keyword_workload_signature(
        workload
    ) == (
        "module.search",
        "abc",
        ("zabc", 4),
        (("flags", "indexlike", 4),),
        4,
        "str",
    )


def test_module_workflow_keyword_standard_definitions_stay_owned_by_source_tree_suite(
) -> None:
    owner_definitions = (
        collection_replacement_support.MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS
    )
    definition_names = tuple(definition.name for definition in owner_definitions)
    standard_definitions_by_name = {
        definition.name: definition
        for definition in _explicit_standard_benchmark_definitions()
        if definition.name in definition_names
    }

    assert definition_names == (
        "module-workflow-keyword-flags",
        "module-workflow-keyword-errors",
    )
    assert tuple(standard_definitions_by_name) == definition_names
    assert tuple(
        standard_definitions_by_name[definition_name]
        for definition_name in definition_names
    ) == owner_definitions
    for definition in owner_definitions:
        assert standard_definitions_by_name[definition.name] is definition


def test_source_tree_module_keyword_definition_references_owner_manifest_path_constant(
) -> None:
    assert _owner_definition_manifest_path_names(
        _module_assignment(
            collection_replacement_support,
            "MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS",
        )
    ) == (
        ("MODULE_BOUNDARY_MANIFEST_PATH",),
        ("MODULE_BOUNDARY_MANIFEST_PATH",),
    )


def test_module_assignment_returns_top_level_annotated_assignment(
    monkeypatch,
) -> None:
    module_ast = ast.parse(
        """
ANNOTATED_ALIAS: object = benchmark_test_support.SHARED_ALIAS
"""
    )

    monkeypatch.setattr(
        meta_support,
        "_parsed_module_ast",
        lambda module: module_ast,
    )

    assignment = _module_assignment(
        SimpleNamespace(ANNOTATED_ALIAS=object()),
        "ANNOTATED_ALIAS",
    )

    assert isinstance(assignment, ast.AnnAssign)
    assert isinstance(assignment.target, ast.Name)
    assert assignment.target.id == "ANNOTATED_ALIAS"


def test_module_workflow_keyword_definition_exports_reuse_owner_manifest_path_constant(
) -> None:
    assert tuple(
        definition.manifest_paths[0]
        for definition in (
            collection_replacement_support.MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS
        )
    ) == (
        support.MODULE_BOUNDARY_MANIFEST_PATH,
        support.MODULE_BOUNDARY_MANIFEST_PATH,
    )


def test_inline_standard_definition_exports_reuse_named_manifest_path_constants(
) -> None:
    assignment_nodes = _inline_standard_definition_assignments(support)
    assert assignment_nodes == ()
    assert not hasattr(support, "COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS")


@pytest.mark.parametrize(
    ("module_name", "module_constant_name"),
    (
        pytest.param(
            "tests.benchmarks.test_source_tree_combined_boundary_benchmarks",
            None,
            id="source-tree-combined-suite",
        ),
    ),
)
def test_shared_module_boundary_manifest_path_consumers_reuse_support_constant_by_identity(
    module_name: str,
    module_constant_name: str | None,
) -> None:
    module = importlib.import_module(module_name)
    _assert_owner_module_routes_through_package_import(
        module,
        owner_module="tests.benchmarks.benchmark_test_support",
        package_module="tests.benchmarks",
        expected_alias_pairs=frozenset({("benchmark_test_support", None)}),
    )
    assert getattr(module, "benchmark_test_support") is support
    assert module.benchmark_test_support.MODULE_BOUNDARY_MANIFEST_PATH is support.MODULE_BOUNDARY_MANIFEST_PATH
    if module_constant_name is not None:
        _, assignment_names = top_level_module_definition_and_assignment_names(
            module
        )
        assert module_constant_name not in assignment_names


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
    assert getattr(anchor_support, manifest_path_name) is getattr(support, manifest_path_name)


def test_shared_source_tree_manifest_path_constants_point_to_current_workload_files() -> None:
    assert (
        support.OPTIONAL_GROUP_MANIFEST_PATH,
        support.NESTED_GROUP_MANIFEST_PATH,
        support.EXACT_REPEAT_MANIFEST_PATH,
        support.RANGED_REPEAT_MANIFEST_PATH,
        support.GROUPED_ALTERNATION_MANIFEST_PATH,
        support.GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH,
        support.NESTED_GROUP_REPLACEMENT_MANIFEST_PATH,
        support.OPEN_ENDED_MANIFEST_PATH,
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


def test_publication_runtime_contracts_route_shared_support_through_package_owner(
) -> None:
    definition_names, assignment_names = (
        top_level_module_definition_and_assignment_names(
            publication_runtime_contracts
        )
    )

    _assert_owner_module_routes_through_package_import(
        publication_runtime_contracts,
        owner_module="tests.benchmarks.benchmark_test_support",
        package_module="tests.benchmarks",
        expected_alias_pairs=frozenset({("benchmark_test_support", None)}),
    )
    assert publication_runtime_contracts.benchmark_test_support is support
    assert {
        "COMPILE_MATRIX_MANIFEST_PATH",
        "CONDITIONAL_GROUP_EXISTS_BOUNDARY_MANIFEST_PATH",
        "NESTED_GROUP_CALLABLE_REPLACEMENT_BOUNDARY_MANIFEST_PATH",
        "_write_test_manifest",
        "assert_benchmark_workload_matches_expected_result",
        "live_manifest_workloads",
        "run_benchmark_workload_with_cpython",
    }.isdisjoint(definition_names | assignment_names)
    for shared_name in (
        "COMPILE_MATRIX_MANIFEST_PATH",
        "CONDITIONAL_GROUP_EXISTS_BOUNDARY_MANIFEST_PATH",
        "NESTED_GROUP_CALLABLE_REPLACEMENT_BOUNDARY_MANIFEST_PATH",
        "_write_test_manifest",
        "assert_benchmark_workload_matches_expected_result",
        "live_manifest_workloads",
        "run_benchmark_workload_with_cpython",
    ):
        assert getattr(publication_runtime_contracts.benchmark_test_support, shared_name) is getattr(
            support,
            shared_name,
        )


def test_publication_runtime_contracts_keep_summary_contract_helpers_owner_local() -> None:
    definition_names, assignment_names = (
        top_level_module_definition_and_assignment_names(
            publication_runtime_contracts
        )
    )

    owner_local_names = {
        "_summary_contract_manifest",
        "_summary_contract_workload_payload",
        "_summary_contract_workload_record",
    }
    assert owner_local_names.issubset(definition_names | assignment_names)
    for owner_local_name in owner_local_names:
        assert not hasattr(support, owner_local_name)
        assert getattr(publication_runtime_contracts, owner_local_name).__module__ == (
            publication_runtime_contracts.__name__
        )


def test_shared_publication_runtime_manifest_path_constants_point_to_current_workload_files(
) -> None:
    assert (
        support.CONDITIONAL_GROUP_EXISTS_BOUNDARY_MANIFEST_PATH,
        support.NESTED_GROUP_CALLABLE_REPLACEMENT_BOUNDARY_MANIFEST_PATH,
    ) == (
        REPO_ROOT / "benchmarks" / "workloads" / "conditional_group_exists_boundary.py",
        REPO_ROOT
        / "benchmarks"
        / "workloads"
        / "nested_group_callable_replacement_boundary.py",
    )


def test_benchmark_test_support_owns_only_shared_collection_replacement_classifier_helpers(
) -> None:
    definition_names, _ = top_level_module_definition_and_assignment_names(
        support
    )

    assert {
        "_is_encoded_indexlike_payload",
        "_is_module_workflow_keyword_flags_workload",
        "_is_module_workflow_keyword_error_workload",
        "_module_workflow_keyword_workload_args",
        "_module_workflow_keyword_workload_signature",
        "_module_workflow_keyword_correctness_case_signature",
        "MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS",
        "_collection_replacement_keyword_parameter_name",
        "_collection_replacement_positional_keyword_field",
        "_is_collection_replacement_keyword_workload",
        "_assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call",
        "_is_collection_replacement_compiled_pattern_module_helper_keyword_workload",
        "_is_collection_replacement_compiled_pattern_keyword_error_workload",
    }.isdisjoint(definition_names)


def test_collection_replacement_benchmark_support_owns_keyword_classifier_helpers_and_routes_shared_ones_through_support_alias(
) -> None:
    definition_names, assignment_names = (
        top_level_module_definition_and_assignment_names(
            collection_replacement_support
        )
    )

    assert {
        "_is_encoded_indexlike_payload",
        "_is_module_workflow_keyword_flags_workload",
        "_is_module_workflow_keyword_error_workload",
        "_module_workflow_keyword_workload_args",
        "_module_workflow_keyword_workload_signature",
        "_module_workflow_keyword_correctness_case_signature",
        "_collection_replacement_keyword_parameter_name",
        "_collection_replacement_positional_keyword_field",
        "_is_collection_replacement_keyword_workload",
        "_assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call",
        "_is_collection_replacement_compiled_pattern_module_helper_keyword_workload",
        "_is_collection_replacement_compiled_pattern_keyword_error_workload",
    }.issubset(definition_names)
    assert "MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS" in assignment_names
    assert {
        "_collection_replacement_keyword_parameter_name",
        "_collection_replacement_positional_keyword_field",
        "_is_collection_replacement_keyword_workload",
        "_assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call",
        "_is_collection_replacement_compiled_pattern_module_helper_keyword_workload",
        "_is_collection_replacement_compiled_pattern_keyword_error_workload",
    }.isdisjoint(assignment_names)
    assert "_is_collection_replacement_wrong_text_model_workload" in definition_names
    assert "_is_collection_replacement_wrong_text_model_workload" not in assignment_names
    assert collection_replacement_support is not support
    assert collection_replacement_support.benchmark_test_support is support
    assert not hasattr(
        collection_replacement_support.benchmark_test_support,
        "_is_collection_replacement_wrong_text_model_workload",
    )


@pytest.mark.parametrize(
    ("module_name", "expected_helper_names"),
    (
        pytest.param(
            "tests.benchmarks.test_benchmark_test_support",
            frozenset(
                {
                    "_module_imported_names",
                    "_module_import_targets",
                    "_ast_import_targets",
                }
            ),
            id="benchmark-test-support-suite",
        ),
    ),
)
def test_benchmark_import_introspection_helpers_stay_owned_by_meta_suite(
    module_name: str,
    expected_helper_names: frozenset[str],
) -> None:
    module = importlib.import_module(module_name)
    definition_names, assignment_names = (
        top_level_module_definition_and_assignment_names(module)
    )
    module_ast = _parsed_module_ast(module)
    local_names = definition_names | assignment_names

    assert _top_level_import_from_alias_pairs(
        _parsed_module_ast(module),
        module_name="tests.benchmarks",
        imported_names=frozenset({"benchmark_test_support"}),
    ) == frozenset({("benchmark_test_support", "support")})
    assert not any(
        isinstance(node, ast.ImportFrom)
        and node.module == "tests.benchmarks.benchmark_test_support"
        and any(alias.name in expected_helper_names for alias in node.names)
        for node in module_ast.body
    )
    assert expected_helper_names.issubset(local_names)
    assert module.support is support
    for helper_name in expected_helper_names:
        helper = getattr(module, helper_name)
        assert helper.__module__ == module.__name__
        assert pathlib.Path(inspect.getsourcefile(helper)).resolve() == pathlib.Path(
            module.__file__
        ).resolve()
        assert not hasattr(module.support, helper_name)


def test_benchmark_support_suite_routes_shared_owner_imports_through_package_alias(
) -> None:
    module = importlib.import_module("tests.benchmarks.test_benchmark_test_support")
    definition_names, assignment_names = (
        top_level_module_definition_and_assignment_names(module)
    )

    _assert_owner_module_routes_through_package_import(
        module,
        owner_module="tests.benchmarks.benchmark_test_support",
        package_module="tests.benchmarks",
        expected_alias_pairs=frozenset({("benchmark_test_support", "support")}),
    )
    assert module.support is support
    assert {
        "MODULE_BOUNDARY_MANIFEST_PATH",
        "RecordingBenchmarkModule",
        "_write_test_manifest",
    }.isdisjoint(definition_names | assignment_names)
    assert "_parsed_module_ast" in definition_names
    assert "_synthetic_workload" in definition_names


def test_benchmark_support_suite_owns_local_synthetic_helper_surface() -> None:
    module = importlib.import_module("tests.benchmarks.test_benchmark_test_support")
    definition_names, assignment_names = (
        top_level_module_definition_and_assignment_names(module)
    )
    support_definition_names, support_assignment_names = (
        top_level_module_definition_and_assignment_names(support)
    )
    local_only_names = {
        "_synthetic_manifest",
        "_synthetic_workload",
        "_synthetic_manifest_loader",
        "_module_pattern_case",
        "_synthetic_workload_signature",
        "_synthetic_workload_is_included",
        "synthetic_workload",
        "_synthetic_case",
    }

    assert module.support is support
    assert local_only_names.issubset(definition_names | assignment_names)
    assert local_only_names.isdisjoint(
        support_definition_names | support_assignment_names
    )
    assert local_only_names.isdisjoint(dir(support))
    for helper_name in local_only_names:
        helper = getattr(module, helper_name)
        assert helper.__module__ == module.__name__
        assert pathlib.Path(inspect.getsourcefile(helper)).resolve() == pathlib.Path(
            module.__file__
        ).resolve()


@pytest.mark.parametrize(
    ("import_targets", "observed_alias_pairs", "expected_alias_pairs"),
    (
        pytest.param(
            frozenset(),
            frozenset(),
            frozenset({("benchmark_test_support", "support")}),
            id="missing-package-import",
        ),
        pytest.param(
            frozenset(
                {
                    "tests.benchmarks",
                    "tests.benchmarks.benchmark_test_support",
                }
            ),
            frozenset({("benchmark_test_support", "support")}),
            frozenset({("benchmark_test_support", "support")}),
            id="direct-owner-import",
        ),
        pytest.param(
            frozenset({"tests.benchmarks"}),
            frozenset({("benchmark_test_support", None)}),
            frozenset({("benchmark_test_support", "support")}),
            id="alias-drift",
        ),
    ),
)
def test_owner_module_package_import_helper_rejects_missing_package_alias_or_direct_owner_import(
    monkeypatch,
    import_targets: frozenset[str],
    observed_alias_pairs: frozenset[tuple[str, str | None]],
    expected_alias_pairs: frozenset[tuple[str, str | None]],
) -> None:
    current_module = importlib.import_module(__name__)

    monkeypatch.setattr(meta_support, "_module_import_targets", lambda _: import_targets)
    monkeypatch.setattr(
        meta_support,
        "_top_level_import_from_alias_pairs",
        lambda *args, **kwargs: observed_alias_pairs,
    )

    with pytest.raises(AssertionError):
        _assert_owner_module_routes_through_package_import(
            current_module,
            owner_module="tests.benchmarks.benchmark_test_support",
            package_module="tests.benchmarks",
            expected_alias_pairs=expected_alias_pairs,
        )


@pytest.mark.parametrize(
    (
        "local_definition_names",
        "local_assignment_names",
        "definition_names",
        "assignment_names",
    ),
    (
        pytest.param(
            frozenset(),
            frozenset({"owner_helper"}),
            ("owner_helper",),
            (),
            id="expected-definition-assigned-locally",
        ),
        pytest.param(
            frozenset({"OWNER_ASSIGNMENT"}),
            frozenset(),
            (),
            ("OWNER_ASSIGNMENT",),
            id="expected-assignment-defined-locally",
        ),
    ),
)
def test_owner_surface_module_owned_without_local_duplicates_rejects_cross_kind_local_duplicates(
    monkeypatch,
    local_definition_names: frozenset[str],
    local_assignment_names: frozenset[str],
    definition_names: tuple[str, ...],
    assignment_names: tuple[str, ...],
) -> None:
    caller_module = object()
    owner_module = SimpleNamespace(
        owner_helper=object(),
        OWNER_ASSIGNMENT=object(),
    )
    observed_modules: list[object] = []

    def _top_level_names(module: object) -> tuple[set[str], set[str]]:
        observed_modules.append(module)
        return set(local_definition_names), set(local_assignment_names)

    monkeypatch.setattr(
        meta_support,
        "top_level_module_definition_and_assignment_names",
        _top_level_names,
    )

    with pytest.raises(AssertionError):
        assert_owner_surface_module_owned_without_local_duplicates(
            caller_module,
            owner_module,
            definition_names=definition_names,
            assignment_names=assignment_names,
        )

    assert observed_modules == [caller_module]


def test_owner_surface_module_owned_without_local_duplicates_accepts_extra_owner_name_when_local_surface_is_clean(
    monkeypatch,
) -> None:
    caller_module = object()
    owner_module = SimpleNamespace(
        owner_helper=object(),
        OWNER_ASSIGNMENT=object(),
    )
    extra_owner_module = SimpleNamespace(EXTRA_OWNER_ASSIGNMENT=object())
    observed_modules: list[object] = []

    def _top_level_names(module: object) -> tuple[set[str], set[str]]:
        observed_modules.append(module)
        assert module is caller_module
        return set(), set()

    monkeypatch.setattr(
        meta_support,
        "top_level_module_definition_and_assignment_names",
        _top_level_names,
    )

    assert_owner_surface_module_owned_without_local_duplicates(
        caller_module,
        owner_module,
        definition_names=("owner_helper",),
        assignment_names=("OWNER_ASSIGNMENT",),
        extra_owner_name="EXTRA_OWNER_ASSIGNMENT",
        extra_owner_module=extra_owner_module,
    )

    assert observed_modules == [caller_module]


@pytest.mark.parametrize(
    ("local_definition_names", "local_assignment_names"),
    (
        pytest.param({"EXTRA_OWNER_ASSIGNMENT"}, set(), id="local-definition"),
        pytest.param(set(), {"EXTRA_OWNER_ASSIGNMENT"}, id="local-assignment"),
    ),
)
def test_owner_surface_module_owned_without_local_duplicates_rejects_extra_owner_name_when_defined_locally(
    monkeypatch,
    local_definition_names: set[str],
    local_assignment_names: set[str],
) -> None:
    caller_module = object()
    owner_module = SimpleNamespace(owner_helper=object())
    extra_owner_module = SimpleNamespace(EXTRA_OWNER_ASSIGNMENT=object())
    observed_modules: list[object] = []

    def _top_level_names(module: object) -> tuple[set[str], set[str]]:
        observed_modules.append(module)
        assert module is caller_module
        return set(local_definition_names), set(local_assignment_names)

    monkeypatch.setattr(
        meta_support,
        "top_level_module_definition_and_assignment_names",
        _top_level_names,
    )

    with pytest.raises(AssertionError):
        assert_owner_surface_module_owned_without_local_duplicates(
            caller_module,
            owner_module,
            definition_names=("owner_helper",),
            extra_owner_name="EXTRA_OWNER_ASSIGNMENT",
            extra_owner_module=extra_owner_module,
        )

    assert observed_modules == [caller_module]


def test_owner_surface_module_owned_without_local_duplicates_rejects_unpaired_extra_owner_arguments(
    monkeypatch,
) -> None:
    caller_module = object()
    owner_module = SimpleNamespace(owner_helper=object())
    extra_owner_module = SimpleNamespace(EXTRA_OWNER_ASSIGNMENT=object())

    monkeypatch.setattr(
        meta_support,
        "top_level_module_definition_and_assignment_names",
        lambda module: (set(), set()),
    )

    with pytest.raises(AssertionError):
        assert_owner_surface_module_owned_without_local_duplicates(
            caller_module,
            owner_module,
            extra_owner_module=extra_owner_module,
        )

    with pytest.raises(AssertionError):
        assert_owner_surface_module_owned_without_local_duplicates(
            caller_module,
            owner_module,
            extra_owner_name="EXTRA_OWNER_ASSIGNMENT",
        )


def test_assert_mixed_owner_surface_accepts_local_names_and_support_aliases(
    monkeypatch,
) -> None:
    shared_alias = object()

    def owner_helper() -> None:
        return None

    caller_module = SimpleNamespace(
        owner_helper=owner_helper,
        OWNER_ASSIGNMENT=object(),
        SHARED_ALIAS=shared_alias,
    )
    module_ast = ast.parse(
        """
def owner_helper():
    return None

OWNER_ASSIGNMENT = object()
SHARED_ALIAS = benchmark_test_support.SHARED_ALIAS
"""
    )

    monkeypatch.setattr(
        meta_support,
        "_parsed_module_ast",
        lambda module: module_ast,
    )
    monkeypatch.setattr(
        support,
        "SHARED_ALIAS",
        shared_alias,
        raising=False,
    )

    assert_mixed_owner_surface(
        caller_module,
        local_function_names=("owner_helper",),
        local_assignment_names=("OWNER_ASSIGNMENT",),
        support_alias_assignment_names=("SHARED_ALIAS",),
    )


def test_assert_mixed_owner_surface_rejects_overlapping_name_sets(
    monkeypatch,
) -> None:
    module_ast = ast.parse(
        """
def duplicated_name():
    return None
"""
    )

    monkeypatch.setattr(
        meta_support,
        "_parsed_module_ast",
        lambda module: module_ast,
    )

    with pytest.raises(AssertionError):
        assert_mixed_owner_surface(
            object(),
            local_function_names=("duplicated_name",),
            local_assignment_names=("duplicated_name",),
        )


def test_assert_mixed_owner_surface_rejects_local_assignment_that_aliases_benchmark_support(
    monkeypatch,
) -> None:
    shared_alias = object()
    caller_module = SimpleNamespace(OWNER_ASSIGNMENT=shared_alias)
    module_ast = ast.parse(
        """
OWNER_ASSIGNMENT = benchmark_test_support.SHARED_ALIAS
"""
    )

    monkeypatch.setattr(
        meta_support,
        "_parsed_module_ast",
        lambda module: module_ast,
    )
    monkeypatch.setattr(
        support,
        "SHARED_ALIAS",
        shared_alias,
        raising=False,
    )

    with pytest.raises(AssertionError):
        assert_mixed_owner_surface(
            caller_module,
            local_assignment_names=("OWNER_ASSIGNMENT",),
        )


@pytest.mark.parametrize(
    "module_source",
    (
        pytest.param(
            """
from tests.benchmarks import benchmark_test_support as shared_support
OWNER_ASSIGNMENT = shared_support.SHARED_ALIAS
""",
            id="module-alias",
        ),
        pytest.param(
            """
benchmark_support_alias = benchmark_test_support.SHARED_ALIAS
OWNER_ASSIGNMENT = benchmark_support_alias
""",
            id="assignment-alias-chain",
        ),
    ),
)
def test_assert_mixed_owner_surface_rejects_local_assignment_that_routes_through_benchmark_support_aliases(
    monkeypatch,
    module_source: str,
) -> None:
    shared_alias = object()
    caller_module = SimpleNamespace(OWNER_ASSIGNMENT=shared_alias)
    module_ast = ast.parse(module_source)

    monkeypatch.setattr(
        meta_support,
        "_parsed_module_ast",
        lambda module: module_ast,
    )
    monkeypatch.setattr(
        support,
        "SHARED_ALIAS",
        shared_alias,
        raising=False,
    )

    with pytest.raises(AssertionError):
        assert_mixed_owner_surface(
            caller_module,
            local_assignment_names=("OWNER_ASSIGNMENT",),
        )


def test_assert_mixed_owner_surface_accepts_support_alias_through_benchmark_support_module_alias(
    monkeypatch,
) -> None:
    shared_alias = object()
    caller_module = SimpleNamespace(SHARED_ALIAS=shared_alias)
    module_ast = ast.parse(
        """
from tests.benchmarks import benchmark_test_support as shared_support
SHARED_ALIAS = shared_support.SHARED_ALIAS
"""
    )

    monkeypatch.setattr(
        meta_support,
        "_parsed_module_ast",
        lambda module: module_ast,
    )
    monkeypatch.setattr(
        support,
        "SHARED_ALIAS",
        shared_alias,
        raising=False,
    )

    assert_mixed_owner_surface(
        caller_module,
        support_alias_assignment_names=("SHARED_ALIAS",),
    )


def test_assert_mixed_owner_surface_accepts_support_alias_with_annotated_assignment(
    monkeypatch,
) -> None:
    shared_alias = object()
    caller_module = SimpleNamespace(SHARED_ALIAS=shared_alias)
    module_ast = ast.parse(
        """
from tests.benchmarks import benchmark_test_support as shared_support
SHARED_ALIAS: object = shared_support.SHARED_ALIAS
"""
    )

    monkeypatch.setattr(
        meta_support,
        "_parsed_module_ast",
        lambda module: module_ast,
    )
    monkeypatch.setattr(
        support,
        "SHARED_ALIAS",
        shared_alias,
        raising=False,
    )

    assert_mixed_owner_surface(
        caller_module,
        support_alias_assignment_names=("SHARED_ALIAS",),
    )


def test_assert_mixed_owner_surface_accepts_local_assignment_after_module_alias_rebind(
    monkeypatch,
) -> None:
    caller_module = SimpleNamespace(OWNER_ASSIGNMENT=object())
    module_ast = ast.parse(
        """
from tests.benchmarks import benchmark_test_support as shared_support

shared_support = object()
OWNER_ASSIGNMENT = shared_support.SHARED_ALIAS
"""
    )

    monkeypatch.setattr(
        meta_support,
        "_parsed_module_ast",
        lambda module: module_ast,
    )

    assert_mixed_owner_surface(
        caller_module,
        local_assignment_names=("OWNER_ASSIGNMENT",),
    )


@pytest.mark.parametrize(
    "module_source",
    (
        pytest.param(
            """
from tests.benchmarks import benchmark_test_support as shared_support

shared_support = object()
SHARED_ALIAS = shared_support.SHARED_ALIAS
""",
            id="plain-rebind",
        ),
        pytest.param(
            """
from tests.benchmarks import benchmark_test_support as shared_support

shared_support: object = object()
SHARED_ALIAS = shared_support.SHARED_ALIAS
""",
            id="annotated-rebind",
        ),
    ),
)
def test_assert_mixed_owner_surface_rejects_support_alias_after_module_alias_rebind(
    monkeypatch,
    module_source: str,
) -> None:
    shared_alias = object()
    caller_module = SimpleNamespace(SHARED_ALIAS=shared_alias)
    module_ast = ast.parse(module_source)

    monkeypatch.setattr(
        meta_support,
        "_parsed_module_ast",
        lambda module: module_ast,
    )
    monkeypatch.setattr(
        support,
        "SHARED_ALIAS",
        shared_alias,
        raising=False,
    )

    with pytest.raises(AssertionError):
        assert_mixed_owner_surface(
            caller_module,
            support_alias_assignment_names=("SHARED_ALIAS",),
        )


@pytest.mark.parametrize(
    "module_source",
    (
        pytest.param(
            """
SHARED_ALIAS_SOURCE = benchmark_test_support.SHARED_ALIAS
SHARED_ALIAS = SHARED_ALIAS_SOURCE
""",
            id="plain-alias-chain",
        ),
        pytest.param(
            """
from tests.benchmarks import benchmark_test_support as shared_support

SHARED_ALIAS_SOURCE = shared_support.SHARED_ALIAS
SHARED_ALIAS: object = SHARED_ALIAS_SOURCE
""",
            id="annotated-alias-chain",
        ),
    ),
)
def test_assert_mixed_owner_surface_rejects_support_alias_through_top_level_alias_chain(
    monkeypatch,
    module_source: str,
) -> None:
    shared_alias = object()
    caller_module = SimpleNamespace(SHARED_ALIAS=shared_alias)
    module_ast = ast.parse(module_source)

    monkeypatch.setattr(
        meta_support,
        "_parsed_module_ast",
        lambda module: module_ast,
    )
    monkeypatch.setattr(
        support,
        "SHARED_ALIAS",
        shared_alias,
        raising=False,
    )

    with pytest.raises(AssertionError):
        assert_mixed_owner_surface(
            caller_module,
            support_alias_assignment_names=("SHARED_ALIAS",),
        )


def test_assert_mixed_owner_surface_rejects_support_alias_with_wrong_attribute_name(
    monkeypatch,
) -> None:
    shared_alias = object()
    caller_module = SimpleNamespace(SHARED_ALIAS=shared_alias)
    module_ast = ast.parse(
        """
SHARED_ALIAS = benchmark_test_support.OTHER_ALIAS
"""
    )

    monkeypatch.setattr(
        meta_support,
        "_parsed_module_ast",
        lambda module: module_ast,
    )
    monkeypatch.setattr(
        support,
        "SHARED_ALIAS",
        shared_alias,
        raising=False,
    )
    monkeypatch.setattr(
        support,
        "OTHER_ALIAS",
        shared_alias,
        raising=False,
    )

    with pytest.raises(AssertionError):
        assert_mixed_owner_surface(
            caller_module,
            support_alias_assignment_names=("SHARED_ALIAS",),
        )


def test_assert_mixed_owner_surface_rejects_local_annotated_assignment_that_aliases_benchmark_support(
    monkeypatch,
) -> None:
    shared_alias = object()
    caller_module = SimpleNamespace(OWNER_ASSIGNMENT=shared_alias)
    module_ast = ast.parse(
        """
from tests.benchmarks import benchmark_test_support as shared_support
OWNER_ASSIGNMENT: object = shared_support.SHARED_ALIAS
"""
    )

    monkeypatch.setattr(
        meta_support,
        "_parsed_module_ast",
        lambda module: module_ast,
    )
    monkeypatch.setattr(
        support,
        "SHARED_ALIAS",
        shared_alias,
        raising=False,
    )

    with pytest.raises(AssertionError):
        assert_mixed_owner_surface(
            caller_module,
            local_assignment_names=("OWNER_ASSIGNMENT",),
        )


def test_deleted_source_tree_support_modules_stay_unimportable_and_unreferenced() -> None:
    deleted_owner_module = ".".join(
        ("tests", "benchmarks", "source_tree" + "_benchmark_anchor_support")
    )
    deleted_owner_test_module = ".".join(
        ("tests", "benchmarks", "test_" + "source_tree" + "_benchmark_anchor_support")
    )
    _assert_deleted_benchmark_module_stays_absent(
        deleted_module_name=deleted_owner_module,
        deleted_path=(
            REPO_ROOT
            / "tests"
            / "benchmarks"
            / ("source_tree" + "_benchmark_anchor_support.py")
        ),
    )
    _assert_deleted_benchmark_module_stays_absent(
        deleted_module_name=deleted_owner_test_module,
        deleted_path=(
            REPO_ROOT
            / "tests"
            / "benchmarks"
            / ("test_" + "source_tree" + "_benchmark_anchor_support.py")
        ),
    )


def test_benchmark_test_support_no_longer_imports_deleted_source_tree_modules() -> None:
    import_targets = _module_import_targets(support)
    deleted_owner_module = ".".join(
        ("tests", "benchmarks", "source_tree" + "_benchmark_anchor_support")
    )
    deleted_owner_test_module = ".".join(
        ("tests", "benchmarks", "test_" + "source_tree" + "_benchmark_anchor_support")
    )

    assert deleted_owner_module not in import_targets
    assert deleted_owner_test_module not in import_targets


def test_deleted_collection_replacement_anchor_suite_stays_unimportable_and_unreferenced(
) -> None:
    _assert_deleted_benchmark_module_stays_absent(
        deleted_module_name=(
            "tests.benchmarks.test_collection_replacement_"
            "benchmark_anchor_support"
        ),
        deleted_path=(
            REPO_ROOT
            / "tests"
            / "benchmarks"
            / "test_collection_replacement_benchmark_anchor_support.py"
        ),
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


def test_deleted_collection_replacement_owner_module_stays_unimportable_and_unreferenced(
) -> None:
    _assert_deleted_benchmark_module_stays_absent(
        deleted_module_name="tests.benchmarks.collection_replacement_benchmark_anchor_support",
        deleted_path=(
            REPO_ROOT
            / "tests"
            / "benchmarks"
            / "collection_replacement_benchmark_anchor_support.py"
        ),
    )


def test_benchmark_test_support_owns_pattern_boundary_wrong_text_model_surface(
) -> None:
    support_definition_names, support_assignment_names = (
        top_level_module_definition_and_assignment_names(support)
    )
    collection_definition_names, collection_assignment_names = (
        top_level_module_definition_and_assignment_names(
            collection_replacement_support
        )
    )
    moved_owner_names = {
        "_pattern_boundary_wrong_text_model_source_workloads",
        "_pattern_boundary_wrong_text_model_expected_callback_call",
        "_pattern_boundary_wrong_text_model_correctness_case_signature",
        "_pattern_boundary_wrong_text_model_workload_signature",
        "_is_pattern_boundary_wrong_text_model_workload",
        "PATTERN_BOUNDARY_MANIFEST_PATH",
        "_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS",
    }

    assert moved_owner_names.isdisjoint(support_definition_names | support_assignment_names)
    assert moved_owner_names.isdisjoint(dir(support))
    assert {
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
        "_PATTERN_BOUNDED_WILDCARD_WORKLOAD_IDS",
        "_PATTERN_BOUNDED_WILDCARD_CASE_IDS",
        "_PATTERN_SEARCH_VERBOSE_REGRESSION_WORKLOAD_IDS",
        "_PATTERN_FULLMATCH_VERBOSE_REGRESSION_WORKLOAD_IDS",
        "_PATTERN_SEARCH_VERBOSE_REGRESSION_CASE_IDS",
        "_PATTERN_FULLMATCH_VERBOSE_REGRESSION_CASE_IDS",
        "_PATTERN_VERBOSE_REGRESSION_WORKLOAD_IDS",
        "_PATTERN_VERBOSE_REGRESSION_CASE_IDS",
        "_PATTERN_VERBOSE_REGRESSION_PATTERN",
    }.isdisjoint(support_definition_names | support_assignment_names)
    assert {
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
        "_PATTERN_BOUNDED_WILDCARD_WORKLOAD_IDS",
        "_PATTERN_BOUNDED_WILDCARD_CASE_IDS",
        "_PATTERN_SEARCH_VERBOSE_REGRESSION_WORKLOAD_IDS",
        "_PATTERN_FULLMATCH_VERBOSE_REGRESSION_WORKLOAD_IDS",
        "_PATTERN_SEARCH_VERBOSE_REGRESSION_CASE_IDS",
        "_PATTERN_FULLMATCH_VERBOSE_REGRESSION_CASE_IDS",
        "_PATTERN_VERBOSE_REGRESSION_WORKLOAD_IDS",
        "_PATTERN_VERBOSE_REGRESSION_CASE_IDS",
        "_PATTERN_VERBOSE_REGRESSION_PATTERN",
    }.issubset(collection_definition_names | collection_assignment_names)
    assert "_PATTERN_BOUNDARY_STANDARD_DEFINITION_BLOCK" not in (
        support_definition_names | support_assignment_names
    )
    assert "PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS" not in (
        support_definition_names | support_assignment_names
    )
    assert "_PATTERN_BOUNDARY_STANDARD_DEFINITION_BLOCK" in (
        collection_definition_names | collection_assignment_names
    )
    assert "PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS" in (
        collection_definition_names | collection_assignment_names
    )


def test_source_tree_combined_suite_owns_rehomed_pattern_boundary_wrong_text_model_surface_locally(
) -> None:
    module = importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )
    definition_names, assignment_names = (
        top_level_module_definition_and_assignment_names(module)
    )
    moved_owner_names = {
        "_pattern_boundary_wrong_text_model_source_workloads",
        "_pattern_boundary_wrong_text_model_expected_callback_call",
        "_pattern_boundary_wrong_text_model_correctness_case_signature",
        "_pattern_boundary_wrong_text_model_workload_signature",
        "_is_pattern_boundary_wrong_text_model_workload",
        "PATTERN_BOUNDARY_MANIFEST_PATH",
        "_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS",
    }

    assert moved_owner_names.issubset(definition_names | assignment_names)
    assert moved_owner_names.isdisjoint(dir(module.benchmark_test_support))


def test_source_tree_combined_suite_owns_benchmark_contract_helpers_locally() -> None:
    module = importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )
    definition_names, assignment_names = (
        top_level_module_definition_and_assignment_names(module)
    )
    moved_owner_names = {
        "_KNOWN_GAP_STATUSES",
        "_assert_benchmark_summary_consistent",
        "_artifact_manifest_record",
        "_expected_exception_instance",
        "_record_numeric_materialization_fields",
        "assert_benchmark_manifest_contract",
        "find_manifest_record",
        "manifest_workload_ids_matching",
        "run_correctness_case_with_cpython",
        "assert_pattern_helper_wrong_text_model_payload_round_trip",
    }

    assert moved_owner_names.issubset(definition_names | assignment_names)
    assert moved_owner_names.isdisjoint(dir(module.benchmark_test_support))


def test_source_tree_combined_suite_owns_workload_contract_helpers_locally() -> None:
    module = importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )
    definition_names, assignment_names = (
        top_level_module_definition_and_assignment_names(module)
    )
    moved_owner_names = {
        "published_cases_by_id",
        "_contract_source_workloads",
        "find_workload_record",
        "find_workload_document",
        "assert_manifest_workload_contracts",
        "assert_benchmark_workload_contract",
    }

    assert moved_owner_names.issubset(definition_names | assignment_names)
    assert moved_owner_names.isdisjoint(dir(module.benchmark_test_support))


class _RecordingSubTestContext:
    def __enter__(self) -> None:
        return None

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb,
    ) -> bool:
        return False


class _RecordingSubTestCase:
    __test__ = False

    def __init__(self) -> None:
        self.subtests: list[dict[str, object]] = []

    def subTest(self, **params):
        self.subtests.append(params)
        return _RecordingSubTestContext()


class _NoSubTestCase:
    __test__ = False

    def subTest(self, **params):
        del params
        raise AssertionError("subTest should not be used when subtest_label is omitted")


def test_assert_manifest_workload_contracts_delegates_without_subtests(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest = SimpleNamespace(manifest_id="synthetic-manifest")
    scorecard = {"synthetic": "scorecard"}
    testcase = _NoSubTestCase()
    record_by_id = {
        "first-workload": {"workload_id": "first-workload"},
        "second-workload": {"workload_id": "second-workload"},
    }
    document_by_id = {
        "first-workload": object(),
        "second-workload": object(),
    }
    workload_lookup_calls: list[str] = []
    document_lookup_calls: list[str] = []
    delegated_calls: list[tuple[object, dict[str, object], str, object, str]] = []

    def _find_workload_record(
        observed_scorecard: dict[str, object],
        workload_id: str,
    ) -> dict[str, object]:
        assert observed_scorecard is scorecard
        workload_lookup_calls.append(workload_id)
        return record_by_id[workload_id]

    def _find_workload_document(
        observed_manifest: object,
        workload_id: str,
    ) -> object:
        assert observed_manifest is manifest
        document_lookup_calls.append(workload_id)
        return document_by_id[workload_id]

    def _assert_benchmark_workload_contract(
        observed_testcase: object,
        workload_record: dict[str, object],
        *,
        manifest_id: str,
        workload_document: object,
        expected_status: str,
    ) -> None:
        delegated_calls.append(
            (
                observed_testcase,
                workload_record,
                manifest_id,
                workload_document,
                expected_status,
            )
        )

    monkeypatch.setattr(
        collection_replacement_support,
        "find_workload_record",
        _find_workload_record,
    )
    monkeypatch.setattr(
        collection_replacement_support,
        "find_workload_document",
        _find_workload_document,
    )
    monkeypatch.setattr(
        collection_replacement_support,
        "assert_benchmark_workload_contract",
        _assert_benchmark_workload_contract,
    )

    collection_replacement_support.assert_manifest_workload_contracts(
        testcase,
        manifest,
        scorecard,
        (
            ("first-workload", "measured"),
            ("second-workload", "known-gap"),
        ),
    )

    assert workload_lookup_calls == ["first-workload", "second-workload"]
    assert document_lookup_calls == ["first-workload", "second-workload"]
    assert delegated_calls == [
        (
            testcase,
            record_by_id["first-workload"],
            "synthetic-manifest",
            document_by_id["first-workload"],
            "measured",
        ),
        (
            testcase,
            record_by_id["second-workload"],
            "synthetic-manifest",
            document_by_id["second-workload"],
            "known-gap",
        ),
    ]


def test_assert_manifest_workload_contracts_wraps_each_expectation_in_named_subtests(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest = SimpleNamespace(manifest_id="synthetic-manifest")
    testcase = _RecordingSubTestCase()
    delegated_workload_ids: list[str] = []

    monkeypatch.setattr(
        collection_replacement_support,
        "find_workload_record",
        lambda scorecard, workload_id: {"workload_id": workload_id},
    )
    monkeypatch.setattr(
        collection_replacement_support,
        "find_workload_document",
        lambda benchmark_manifest, workload_id: workload_id,
    )
    monkeypatch.setattr(
        collection_replacement_support,
        "assert_benchmark_workload_contract",
        lambda observed_testcase, workload_record, **kwargs: delegated_workload_ids.append(
            workload_record["workload_id"]
        ),
    )

    collection_replacement_support.assert_manifest_workload_contracts(
        testcase,
        manifest,
        {"synthetic": "scorecard"},
        (
            ("first-workload", "measured"),
            ("second-workload", "known-gap"),
        ),
        subtest_label="workload_id",
    )

    assert testcase.subtests == [
        {"workload_id": "first-workload"},
        {"workload_id": "second-workload"},
    ]
    assert delegated_workload_ids == ["first-workload", "second-workload"]


@pytest.mark.parametrize(
    (
        "expected_measured_workload_ids",
        "expected_total_workload_count",
        "expected_subtest_label",
    ),
    (
        pytest.param(
            ("only-workload",),
            None,
            None,
            id="single-measured-workload-without-total-count",
        ),
        pytest.param(
            ("first-workload", "second-workload"),
            None,
            "workload_id",
            id="multiple-measured-workloads-without-total-count",
        ),
        pytest.param(
            ("first-workload", "second-workload"),
            2,
            "measured_workload_id",
            id="explicit-total-count",
        ),
    ),
)
def test_assert_zero_gap_manifest_workloads_measured_routes_through_shared_contract_helper(
    monkeypatch: pytest.MonkeyPatch,
    expected_measured_workload_ids: tuple[str, ...],
    expected_total_workload_count: int | None,
    expected_subtest_label: str | None,
) -> None:
    import tests.conftest as shared_conftest

    manifest_path = pathlib.Path("synthetic-boundary.py")
    resolved_manifest_path = pathlib.Path("/tmp/synthetic-boundary.py")
    manifest = SimpleNamespace(manifest_id="synthetic-boundary")
    captured_call: dict[str, object] = {}
    measured_workload_count = len(expected_measured_workload_ids)
    scorecard = {
        "manifests": {
            "synthetic-boundary": {
                "known_gap_count": 0,
                "measured_workloads": measured_workload_count,
                "workload_count": (
                    measured_workload_count
                    if expected_total_workload_count is None
                    else expected_total_workload_count
                ),
            }
        }
    }

    monkeypatch.setattr(
        support,
        "_resolve_live_manifest_path",
        lambda path: resolved_manifest_path,
    )
    monkeypatch.setattr(support, "load_manifest", lambda path: manifest)

    def _run_harness_scorecard(
        module_name: str,
        args: list[str],
        report_name: str,
    ) -> tuple[None, dict[str, object]]:
        captured_call.update(
            {
                "module_name": module_name,
                "args": args,
                "report_name": report_name,
            }
        )
        return (None, scorecard)

    def _assert_manifest_workload_contracts(
        testcase: object,
        observed_manifest: object,
        observed_scorecard: dict[str, object],
        workload_expectations,
        *,
        subtest_label: str | None = None,
    ) -> None:
        del testcase
        captured_call.update(
            {
                "observed_manifest": observed_manifest,
                "observed_scorecard": observed_scorecard,
                "workload_expectations": tuple(workload_expectations),
                "subtest_label": subtest_label,
            }
        )

    monkeypatch.setattr(
        shared_conftest,
        "run_harness_scorecard",
        _run_harness_scorecard,
    )
    monkeypatch.setattr(
        collection_replacement_support,
        "assert_manifest_workload_contracts",
        _assert_manifest_workload_contracts,
    )

    collection_replacement_support.assert_zero_gap_manifest_workloads_measured(
        manifest_path=manifest_path,
        manifest_id="synthetic-boundary",
        expected_measured_workload_ids=expected_measured_workload_ids,
        expected_measured_workload_count=measured_workload_count,
        expected_total_workload_count=expected_total_workload_count,
    )

    assert captured_call["module_name"] == "rebar_harness.benchmarks"
    assert captured_call["args"] == ["--manifest", str(resolved_manifest_path)]
    assert captured_call["report_name"] == "benchmarks.json"
    assert captured_call["observed_manifest"] is manifest
    assert captured_call["observed_scorecard"] is scorecard
    assert captured_call["workload_expectations"] == tuple(
        (workload_id, "measured")
        for workload_id in expected_measured_workload_ids
    )
    assert captured_call["subtest_label"] == expected_subtest_label


def test_benchmark_test_support_owns_compiled_pattern_helper_surface(
) -> None:
    support_definition_names, support_assignment_names = (
        top_level_module_definition_and_assignment_names(support)
    )
    collection_definition_names, collection_assignment_names = (
        top_level_module_definition_and_assignment_names(
            collection_replacement_support
        )
    )
    assert {
        "COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_PAYLOAD_DROP_FIELDS",
        "COMPILED_PATTERN_MODULE_SUCCESS_CONTRACT_EXCLUDED_FIELDS",
    }.issubset(support_assignment_names)
    removed_duplicate_names = {
        "_module_workflow_compiled_pattern_success_correctness_case_signature",
        "_module_workflow_compiled_pattern_success_workload_signature",
    }
    moved_owner_names = {
        "compiled_pattern_contract_expected_build_calls",
        "_run_cpython_compiled_pattern_module_helper_workload",
        "_assert_wrong_text_model_payload_round_trip",
        "_assert_compiled_pattern_module_success_payload_round_trip",
        "_assert_compiled_pattern_success_rows_measured_in_combined_manifest",
        "include_live_compiled_pattern_module_success_workload",
    }
    assert not hasattr(support, "_compiled_pattern_wrong_text_model_source_workloads")
    assert hasattr(collection_replacement_support, "_compiled_pattern_wrong_text_model_source_workloads")
    moved_selector_names = {
        "_COMPILED_PATTERN_MODULE_HELPER_OPERATIONS",
        "_VERBOSE_REGRESSION_PATTERN",
        "_VERBOSE_REGRESSION_FLAGS",
        "_is_module_workflow_compiled_pattern_workload",
        "_is_module_workflow_compiled_pattern_literal_success_workload",
        "_is_module_workflow_compiled_pattern_bounded_wildcard_success_workload",
        "_is_module_workflow_compiled_pattern_verbose_bytes_success_workload",
        "_is_collection_replacement_compiled_pattern_success_workload",
        "_is_module_workflow_compiled_pattern_wrong_text_model_workload",
        "_is_collection_replacement_wrong_text_model_workload",
        "_module_workflow_compiled_pattern_correctness_case_signature",
        "_module_workflow_compiled_pattern_workload_signature",
    }
    assert moved_selector_names.isdisjoint(
        support_definition_names | support_assignment_names
    )
    assert all(not hasattr(support, name) for name in moved_selector_names)
    assert moved_selector_names.issubset(
        collection_definition_names | collection_assignment_names
    )
    assert all(hasattr(collection_replacement_support, name) for name in moved_selector_names)
    assert removed_duplicate_names.isdisjoint(
        support_definition_names | support_assignment_names
    )
    assert all(not hasattr(support, name) for name in removed_duplicate_names)
    assert moved_owner_names.isdisjoint(support_definition_names | support_assignment_names)
    assert all(not hasattr(support, name) for name in moved_owner_names)
    assert moved_owner_names.issubset(
        collection_definition_names | collection_assignment_names
    )
    assert all(hasattr(collection_replacement_support, name) for name in moved_owner_names)
    assert "_compiled_pattern_module_helper_runtime_route" not in (
        support_definition_names | support_assignment_names
    )
    assert "_COMPILED_PATTERN_MODULE_HELPER_STANDARD_DEFINITION_BLOCK" not in (
        support_definition_names | support_assignment_names
    )
    assert "_compiled_pattern_module_helper_route" not in support_definition_names
    assert "COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS" not in (
        support_definition_names | support_assignment_names
    )
    assert "_compiled_pattern_module_helper_runtime_route" in (
        collection_definition_names | collection_assignment_names
    )
    assert "_COMPILED_PATTERN_MODULE_HELPER_STANDARD_DEFINITION_BLOCK" in (
        collection_definition_names | collection_assignment_names
    )
    assert "_compiled_pattern_module_helper_route" in collection_definition_names
    assert "COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS" in (
        collection_definition_names | collection_assignment_names
    )


def test_shared_compiled_pattern_helper_contract_tests_import_from_support() -> None:
    combined_suite = importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )

    assert _top_level_import_from_alias_pairs(
        _parsed_module_ast(combined_suite),
        module_name="tests.benchmarks",
        imported_names=frozenset({"benchmark_test_support"}),
    ) == frozenset({("benchmark_test_support", None)})
    assert "tests.benchmarks.benchmark_test_support" not in _module_import_targets(
        combined_suite
    )


def test_source_tree_combined_routing_helper_is_deleted_from_shared_support() -> None:
    definition_names, assignment_names = (
        top_level_module_definition_and_assignment_names(support)
    )

    assert "_assert_source_tree_combined_routes_owner_names_through_module_alias" not in (
        definition_names | assignment_names
    )
    assert not hasattr(
        support, "_assert_source_tree_combined_routes_owner_names_through_module_alias"
    )


def test_source_tree_combined_suite_deletes_proxy_boundary_symbols() -> None:
    module = importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )
    definition_names, assignment_names = (
        top_level_module_definition_and_assignment_names(module)
    )

    assert "_SourceTreeSupportProxy" not in definition_names
    assert "source_tree_support" not in assignment_names
    assert not hasattr(module, "_SourceTreeSupportProxy")
    assert not hasattr(module, "source_tree_support")


def test_source_tree_combined_suite_owns_rehomed_manifest_expectation_surface_locally(
) -> None:
    module = importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )
    definition_names, assignment_names = (
        top_level_module_definition_and_assignment_names(module)
    )
    private_owner_names = frozenset(
        {
            "_SourceTreeBenchmarkCommonCase",
            "_SourceTreeManifestExpectation",
            "_SourceTreeDeferredExpectation",
            "_SourceTreeCombinedCase",
            "_SourceTreeCombinedPatternGroupExpectation",
            "_SourceTreeCombinedManifestShapeExpectation",
            "_SourceTreeCombinedFullyMeasuredManifestExpectation",
            "_SourceTreeCombinedManifestExpectationDefinition",
            "_SourceTreeCombinedManifestExpectations",
            "_SourceTreeCombinedSliceExpectation",
            "_combined_manifest_definition",
            "_combined_fully_measured_manifest_expectation",
            "_published_benchmark_manifest_ids",
            "_SOURCE_TREE_DEFAULT_COMBINED_MANIFEST_EXPECTATION",
            "_SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS",
            "_SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS",
            "_filter_manifest_workload_ids",
            "_public_source_tree_manifest_expectation",
            "_source_tree_combined_manifest_representative_measured_workload_ids",
            "_source_tree_combined_target_manifest_ids",
            "_expected_summary_for_manifests",
            "_source_tree_combined_case",
            "_workload_matches_source_tree_combined_slice",
            "_select_source_tree_combined_slice_rows",
            "_assert_source_tree_benchmark_contract",
            "_OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID",
            "_compile_search_fullmatch_case_signature",
            "_compile_search_fullmatch_workload_signature",
            "_optional_group_correctness_case_signature",
            "_optional_group_workload_signature",
            "_is_optional_group_conditional_workload",
            "_nested_group_correctness_case_signature",
            "_nested_group_workload_signature",
            "_counted_repeat_correctness_case_signature",
            "_counted_repeat_workload_signature",
            "_is_non_alternation_counted_repeat_workload",
            "_grouped_alternation_correctness_case_signature",
            "_grouped_alternation_workload_args",
            "_grouped_alternation_workload_signature",
            "_grouped_alternation_replacement_correctness_case_signature",
        }
    )
    exported_owner_aliases = frozenset(
        {
            "SourceTreeBenchmarkCommonCase",
            "SourceTreeManifestExpectation",
            "SourceTreeDeferredExpectation",
            "SourceTreeCombinedCase",
            "SourceTreeCombinedPatternGroupExpectation",
            "SourceTreeCombinedManifestShapeExpectation",
            "SourceTreeCombinedFullyMeasuredManifestExpectation",
            "SourceTreeCombinedManifestExpectationDefinition",
            "SourceTreeCombinedSliceExpectation",
            "SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS",
            "SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS",
            "expected_summary_for_manifests",
            "source_tree_combined_manifest_representative_measured_workload_ids",
            "source_tree_combined_target_manifest_ids",
            "source_tree_combined_case",
            "select_source_tree_combined_slice_rows",
            "assert_source_tree_benchmark_contract",
        }
    )

    assert private_owner_names.isdisjoint(dir(support))
    assert private_owner_names.issubset(definition_names | assignment_names)
    assert exported_owner_aliases.issubset(definition_names | assignment_names)
    assert private_owner_names.isdisjoint(dir(module.benchmark_test_support))
    assert exported_owner_aliases.isdisjoint(dir(module.benchmark_test_support))
    assert hasattr(support, "freeze_signature_value")
    assert "freeze_signature_value" not in private_owner_names
    assert (
        module.SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS
        is module._SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS
    )
    assert (
        module.assert_source_tree_benchmark_contract
        is module._assert_source_tree_benchmark_contract
    )


@pytest.mark.parametrize(
    (
        "module_source",
        "import_name",
        "dotted_import_name",
        "expected_alias_names",
    ),
    (
        pytest.param(
            "\n".join(
                (
                    "import tests.benchmarks.benchmark_test_support as benchmark_support",
                    "",
                    "benchmark_support_alias = benchmark_support",
                    "benchmark_support_final: object = benchmark_support_alias",
                )
            ),
            "benchmark_test_support",
            "tests.benchmarks.benchmark_test_support",
            {
                "benchmark_support",
                "benchmark_support_alias",
                "benchmark_support_final",
            },
            id="benchmark-test-support-dotted-import",
        ),
        pytest.param(
            "\n".join(
                (
                    "import tests.benchmarks.benchmark_test_support as source_tree_support",
                    "",
                    "source_tree_support_alias = source_tree_support",
                    "source_tree_support_final: object = source_tree_support_alias",
                )
            ),
            "benchmark_test_support",
            "tests.benchmarks.benchmark_test_support",
            {
                "source_tree_support",
                "source_tree_support_alias",
                "source_tree_support_final",
            },
            id="source-tree-support-dotted-import",
        ),
    ),
)
def test_module_alias_names_follow_dotted_import_and_assignment_alias_chains(
    module_source: str,
    import_name: str,
    dotted_import_name: str,
    expected_alias_names: set[str],
) -> None:
    assert _module_alias_names(
        ast.parse(module_source),
        import_from_module="tests.benchmarks",
        import_name=import_name,
        dotted_import_name=dotted_import_name,
    ) == expected_alias_names


def test_module_alias_names_ignore_nested_scope_imports_and_assignments() -> None:
    module_ast = ast.parse(
        """
from tests.benchmarks import benchmark_test_support as shared_support

MODULE_ALIAS = shared_support

def helper():
    import tests.benchmarks.benchmark_test_support as nested_support

    nested_alias = shared_support
    nested_final = nested_support

class Holder:
    import tests.benchmarks.benchmark_test_support as class_support
    CLASS_ALIAS = shared_support
"""
    )

    assert _module_alias_names(
        module_ast,
        import_from_module="tests.benchmarks",
        import_name="benchmark_test_support",
        dotted_import_name="tests.benchmarks.benchmark_test_support",
    ) == {
        "shared_support",
        "MODULE_ALIAS",
    }


def test_module_alias_names_drop_shadowed_top_level_rebindings() -> None:
    module_ast = ast.parse(
        """
from tests.benchmarks import benchmark_test_support as shared_support

MODULE_ALIAS = shared_support
shared_support = object()
OWNER_ASSIGNMENT = shared_support.SHARED_ALIAS
FOLLOWER_ALIAS = MODULE_ALIAS
MODULE_ALIAS = None
FINAL_ALIAS = MODULE_ALIAS
"""
    )

    assert _module_alias_names(
        module_ast,
        import_from_module="tests.benchmarks",
        import_name="benchmark_test_support",
        dotted_import_name="tests.benchmarks.benchmark_test_support",
    ) == {
        "FOLLOWER_ALIAS",
    }


def test_module_attribute_alias_targets_drop_shadowed_top_level_rebindings() -> None:
    module_ast = ast.parse(
        """
from tests.benchmarks import benchmark_test_support as shared_support

OWNER_SURFACE = shared_support.SHARED_ALIAS
FOLLOWER_BEFORE_REBIND = OWNER_SURFACE
OWNER_SURFACE = None
FOLLOWER_AFTER_REBIND = OWNER_SURFACE
ANNOTATED_ALIAS: object = shared_support.OTHER_ALIAS
FINAL_FOLLOWER: object = ANNOTATED_ALIAS
"""
    )

    assert _module_attribute_alias_targets(
        module_ast,
        module_alias_names=frozenset({"shared_support"}),
    ) == {
        "FOLLOWER_BEFORE_REBIND": "SHARED_ALIAS",
        "ANNOTATED_ALIAS": "OTHER_ALIAS",
        "FINAL_FOLLOWER": "OTHER_ALIAS",
    }


def test_module_attribute_alias_targets_ignore_nested_scope_assignments() -> None:
    module_ast = ast.parse(
        """
from tests.benchmarks import benchmark_test_support

def helper():
    NESTED_ALIAS = benchmark_test_support.SHARED_ALIAS

class Holder:
    CLASS_ALIAS = benchmark_test_support.OTHER_ALIAS

MODULE_ALIAS = benchmark_test_support.MODULE_ALIAS
"""
    )

    assert _module_attribute_alias_targets(
        module_ast,
        module_alias_names=frozenset({"benchmark_test_support"}),
    ) == {
        "MODULE_ALIAS": "MODULE_ALIAS",
    }



def test_compiled_pattern_contract_consumer_suites_reuse_shared_support_without_local_duplicates(
) -> None:
    module = importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )
    definition_names, assignment_names = (
        top_level_module_definition_and_assignment_names(module)
    )
    local_names = definition_names | assignment_names

    _assert_owner_module_routes_through_package_import(
        module,
        owner_module="tests.benchmarks.benchmark_test_support",
        package_module="tests.benchmarks",
        expected_alias_pairs=frozenset({("benchmark_test_support", None)}),
    )
    assert getattr(module, "benchmark_test_support") is support
    owner_local_names = (
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACE_PARAMS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS",
        "_is_collection_replacement_compiled_pattern_keyword_error_workload",
    )
    assert all(name in local_names for name in owner_local_names)
    support_definition_names, support_assignment_names = (
        top_level_module_definition_and_assignment_names(support)
    )
    assert set(owner_local_names).isdisjoint(
        support_definition_names | support_assignment_names
    )


def test_source_tree_combined_suite_deletes_manifest_contract_wrapper_methods() -> None:
    module = importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )
    suite_definition = _module_class_definition(
        module,
        "SourceTreeCombinedBoundaryBenchmarkSuiteTest",
    )
    method_names = {
        node.name
        for node in suite_definition.body
        if isinstance(node, ast.FunctionDef)
    }

    assert {
        "_assert_manifest_workload_contracts",
        "_assert_zero_gap_manifest_workloads_measured",
    }.isdisjoint(method_names)


def test_class_method_definition_resolves_source_tree_combined_suite_test_method(
) -> None:
    module = importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )
    suite_definition = _module_class_definition(
        module,
        "SourceTreeCombinedBoundaryBenchmarkSuiteTest",
    )

    method_definition = _class_method_definition(
        suite_definition,
        "test_literal_flag_combined_case_preserves_expected_manifest_paths",
    )

    assert method_definition.name == (
        "test_literal_flag_combined_case_preserves_expected_manifest_paths"
    )
    assert [argument.arg for argument in method_definition.args.args] == ["self"]


def test_pattern_boundary_contract_helpers_use_local_pattern_case_builder() -> None:
    combined_module = importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )

    assert not hasattr(support, "_module_pattern_case")
    assert combined_module.benchmark_test_support is support
    assert _module_pattern_case(
        helper="search",
        operation="module_call",
        args=("abc",),
    )


def test_benchmark_manifest_validation_routes_owner_surfaces_through_package_imports(
) -> None:
    module = importlib.import_module("tests.benchmarks.test_benchmark_manifest_validation")
    definition_names, assignment_names = (
        top_level_module_definition_and_assignment_names(module)
    )
    shared_owner_names = frozenset(
        {
            "_write_test_manifest",
            "assert_benchmark_workload_matches_expected_result",
            "run_benchmark_workload_with_cpython",
            "selected_manifest_workloads",
        }
    )
    _assert_owner_module_routes_through_package_import(
        module,
        owner_module="tests.benchmarks.benchmark_test_support",
        package_module="tests.benchmarks",
        expected_alias_pairs=frozenset({("benchmark_test_support", None)}),
    )
    assert _top_level_import_from_alias_pairs(
        _parsed_module_ast(module),
        module_name="tests.benchmarks",
        imported_names=frozenset(),
    ) == frozenset()
    assert shared_owner_names.isdisjoint(definition_names | assignment_names)
    _assert_benchmark_test_support_aliases_absent(
        "tests.benchmarks.test_benchmark_manifest_validation",
        shared_owner_names,
    )


def test_rehomed_source_tree_contract_tests_stay_owned_by_combined_boundary_suite(
) -> None:
    generic_module = importlib.import_module(
        "tests.benchmarks.test_benchmark_manifest_validation"
    )
    owner_module = importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )
    rehomed_definition_names = frozenset(
        {
            "test_standard_benchmark_compiled_pattern_module_compile_contract_rows_preserve_success_and_keyword_payload_round_trip_until_helper_invocation",
            "test_standard_benchmark_compiled_pattern_wrong_text_model_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation",
            "test_standard_benchmark_compiled_pattern_module_success_contract_rows_preserve_live_source_selection_and_payload_round_trip_until_helper_invocation",
            "test_standard_benchmark_compiled_pattern_module_helper_keyword_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation",
            "test_standard_benchmark_haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio",
        }
    )

    generic_definition_names, generic_assignment_names = (
        top_level_module_definition_and_assignment_names(generic_module)
    )
    owner_definition_names, owner_assignment_names = (
        top_level_module_definition_and_assignment_names(owner_module)
    )

    assert rehomed_definition_names.isdisjoint(
        generic_definition_names | generic_assignment_names
    )
    assert rehomed_definition_names.issubset(
        owner_definition_names | owner_assignment_names
    )


def test_rehomed_collection_replacement_tests_stay_owned_by_combined_boundary_suite(
) -> None:
    combined_module = importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )
    combined_rehomed_names = frozenset(
        {
            "test_collection_replacement_manifest_keeps_pattern_keyword_replacement_and_split_rows_measured",
            "test_collection_replacement_manifest_keeps_module_keyword_replacement_and_split_rows_measured",
            "test_collection_replacement_manifest_keeps_positional_indexlike_module_and_pattern_rows_measured",
            "test_conditional_collection_replacement_slice_expectations_stay_in_sync_with_owner_workload_ids",
        }
    )

    combined_suite_names = frozenset(
        dir(combined_module.SourceTreeCombinedBoundaryBenchmarkSuiteTest)
    )

    assert combined_rehomed_names.issubset(combined_suite_names)


def test_collection_replacement_compiled_pattern_success_selector_stays_owned_by_combined_suite(
) -> None:
    owner_definition_names, _ = top_level_module_definition_and_assignment_names(
        anchor_support
    )
    consumer_definition_names, consumer_assignment_names = (
        top_level_module_definition_and_assignment_names(
            collection_replacement_support
        )
    )
    consumer_local_names = consumer_definition_names | consumer_assignment_names

    assert (
        "_is_collection_replacement_compiled_pattern_success_workload"
        not in owner_definition_names
    )
    assert not hasattr(anchor_support, "_is_collection_replacement_compiled_pattern_success_workload")
    assert not hasattr(support, "_is_collection_replacement_compiled_pattern_success_workload")
    assert "_is_collection_replacement_compiled_pattern_success_workload" in consumer_local_names

def _assert_benchmark_test_support_aliases_absent(
    module_name: str,
    forbidden_owner_names: frozenset[str],
) -> None:
    module = importlib.import_module(module_name)
    alias_pairs: set[tuple[str, str | None]] = set()
    for node in _parsed_module_ast(module).body:
        if isinstance(node, ast.ImportFrom):
            if node.module != "tests.benchmarks.benchmark_test_support":
                continue
            alias_pairs.update(
                (alias.name, alias.asname)
                for alias in node.names
                if alias.name in forbidden_owner_names and alias.asname is not None
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
            and value.attr in forbidden_owner_names
        ):
            alias_pairs.update((value.attr, target_name) for target_name in targets)

    assert alias_pairs == set()


def test_compiled_pattern_contract_consumer_suites_do_not_alias_owner_module_surfaces(
) -> None:
    _assert_benchmark_test_support_aliases_absent(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks",
        frozenset(
            {
                "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC",
                "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC",
                "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS",
                "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS",
                "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS",
                "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES",
                "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACE_PARAMS",
                "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS",
                "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS",
                "_is_collection_replacement_compiled_pattern_keyword_error_workload",
            }
        ),
    )


def test_collection_replacement_owner_surface_reaches_combined_suite_without_source_tree_workload_id_aliases(
) -> None:
    combined_suite = importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )
    definition_names, assignment_names = (
        top_level_module_definition_and_assignment_names(combined_suite)
    )
    local_names = definition_names | assignment_names
    moved_workload_id_names = frozenset(
        {
            "CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS",
            "CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS",
            "CONDITIONAL_GROUP_EXISTS_TEMPLATE_ROUND_TRIP_WORKLOAD_IDS",
            "CONDITIONAL_GROUP_EXISTS_CALLABLE_BYTES_WORKLOAD_IDS",
            "CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS",
            "CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS",
            "CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_IDS",
            "CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS",
            "CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS",
            "CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS",
            "CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS",
            "CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS",
        }
    )

    _assert_owner_module_routes_through_package_import(
        combined_suite,
        owner_module="tests.benchmarks.benchmark_test_support",
        package_module="tests.benchmarks",
        expected_alias_pairs=frozenset({("benchmark_test_support", None)}),
    )
    assert moved_workload_id_names.issubset(local_names)
    assert moved_workload_id_names.isdisjoint(dir(combined_suite.benchmark_test_support))
    for name in moved_workload_id_names:
        assert hasattr(collection_replacement_support, name)
        _assert_exported_name_matches_owner(
            combined_suite,
            collection_replacement_support,
            name,
        )


def test_source_tree_combined_suite_owns_compiled_pattern_module_success_surface(
) -> None:
    support_definition_names, support_assignment_names = (
        top_level_module_definition_and_assignment_names(support)
    )
    definition_names, assignment_names = (
        top_level_module_definition_and_assignment_names(
            collection_replacement_support
        )
    )
    assert "_is_collection_replacement_compiled_pattern_success_workload" not in (
        support_definition_names | support_assignment_names
    )
    assert {
        "_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC",
        "_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC",
        "_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS",
        "_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS",
    }.issubset(assignment_names)
    assert "CompiledPatternModuleSuccessOwnerSpec" not in (
        support_definition_names | support_assignment_names
    )
    assert hasattr(collection_replacement_support, "CompiledPatternModuleSuccessOwnerSpec")
    assert not hasattr(support, "CompiledPatternModuleSuccessOwnerSpec")
    assert hasattr(
        collection_replacement_support,
        "_assert_compiled_pattern_module_success_payload_round_trip",
    )
    assert hasattr(
        collection_replacement_support,
        "_assert_compiled_pattern_success_rows_measured_in_combined_manifest",
    )
    assert hasattr(
        collection_replacement_support,
        "include_live_compiled_pattern_module_success_workload",
    )
    assert not hasattr(support, "_assert_compiled_pattern_module_success_payload_round_trip")
    assert not hasattr(support, "_assert_compiled_pattern_success_rows_measured_in_combined_manifest")
    assert not hasattr(support, "include_live_compiled_pattern_module_success_workload")


def test_source_tree_combined_suite_owns_compiled_pattern_module_success_owner_specs(
) -> None:
    source = (
        REPO_ROOT
        / "tests"
        / "benchmarks"
        / "test_source_tree_combined_boundary_benchmarks.py"
    ).read_text(encoding="utf-8")
    support_source = (
        REPO_ROOT / "tests" / "benchmarks" / "benchmark_test_support.py"
    ).read_text(encoding="utf-8")

    assert re.search(
        r"^(_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC|"
        r"_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC|"
        r"_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS|"
        r"_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS)\b",
        source,
        re.MULTILINE,
    ) is not None
    assert re.search(
        r"^(_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC|"
        r"_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC|"
        r"_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS|"
        r"_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS)\b",
        support_source,
        re.MULTILINE,
    ) is None
    assert re.search(
        r"^(def compiled_pattern_contract_expected_build_calls|"
        r"def _run_cpython_compiled_pattern_module_helper_workload|"
        r"def _assert_wrong_text_model_payload_round_trip|"
        r"def _assert_compiled_pattern_module_success_payload_round_trip|"
        r"def _assert_compiled_pattern_success_rows_measured_in_combined_manifest|"
        r"def include_live_compiled_pattern_module_success_workload)\b",
        source,
        re.MULTILINE,
    ) is not None
    assert re.search(
        r"^(def compiled_pattern_contract_expected_build_calls|"
        r"def _run_cpython_compiled_pattern_module_helper_workload|"
        r"def _assert_wrong_text_model_payload_round_trip|"
        r"def _assert_compiled_pattern_module_success_payload_round_trip|"
        r"def _assert_compiled_pattern_success_rows_measured_in_combined_manifest|"
        r"def include_live_compiled_pattern_module_success_workload)\b",
        support_source,
        re.MULTILINE,
    ) is None


def test_source_tree_combined_suite_defines_compiled_pattern_module_compile_owner_surface(
) -> None:
    source = (
        REPO_ROOT
        / "tests"
        / "benchmarks"
        / "test_source_tree_combined_boundary_benchmarks.py"
    ).read_text(encoding="utf-8")
    support_source = (
        REPO_ROOT / "tests" / "benchmarks" / "benchmark_test_support.py"
    ).read_text(encoding="utf-8")

    assert re.search(
        r"^(class _CompiledPatternModuleCompileContractRoute|"
        r"class CompiledPatternModuleCompileContractCase|"
        r"class _CompiledPatternModuleContractAnchorLane|"
        r"class _CompiledPatternModuleCompileKeywordOwnerSpec|"
        r"class _CompiledPatternModuleCompileSuccessOwnerSpec|"
        r"def _compiled_pattern_module_compile_success_owner_specs|"
        r"def _compiled_pattern_module_compile_keyword_owner_specs|"
        r"def build_compiled_pattern_module_compile_contract_cases|"
        r"def build_compiled_pattern_module_compile_contract_source_workload_params|"
        r"def build_compiled_pattern_module_contract_anchor_lanes|"
        r"_COMPILED_PATTERN_MODULE_COMPILE_INT_ZERO_KEYWORD_SIGNATURE|"
        r"_COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_SIGNATURE|"
        r"_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_SIGNATURE|"
        r"_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS|"
        r"_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS|"
        r"_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION)\b",
        source,
        re.MULTILINE,
    ) is not None
    assert re.search(
        r"^(class _CompiledPatternModuleCompileContractRoute|"
        r"class CompiledPatternModuleCompileContractCase|"
        r"class _CompiledPatternModuleContractAnchorLane|"
        r"class _CompiledPatternModuleCompileKeywordOwnerSpec|"
        r"class _CompiledPatternModuleCompileSuccessOwnerSpec|"
        r"def _compiled_pattern_module_compile_success_owner_specs|"
        r"def _compiled_pattern_module_compile_keyword_owner_specs|"
        r"def build_compiled_pattern_module_compile_contract_cases|"
        r"def build_compiled_pattern_module_compile_contract_source_workload_params|"
        r"def build_compiled_pattern_module_contract_anchor_lanes|"
        r"_COMPILED_PATTERN_MODULE_COMPILE_INT_ZERO_KEYWORD_SIGNATURE|"
        r"_COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_SIGNATURE|"
        r"_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_SIGNATURE|"
        r"_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS|"
        r"_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS|"
        r"_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION)\b",
        support_source,
        re.MULTILINE,
    ) is None


def test_compiled_pattern_contract_builder_surface_uses_one_owned_route(
) -> None:
    source_tree_function_names = {
        node.name
        for node in _parsed_module_ast(collection_replacement_support).body
        if isinstance(node, ast.FunctionDef)
    }

    for wrapper_name, owner_type in (
        (
            "compiled_pattern_module_compile_contract_builder_spec",
            collection_replacement_support.CompiledPatternModuleCompileContractCase,
        ),
        (
            "compiled_pattern_module_success_contract_builder_spec",
            collection_replacement_support.CompiledPatternModuleSuccessOwnerSpec,
        ),
        (
            "compiled_pattern_module_helper_keyword_contract_builder_spec",
            collection_replacement_support._CompiledPatternModuleHelperKeywordContractSpec,
        ),
    ):
        owner_module = importlib.import_module(owner_type.__module__)
        class_definition = _module_class_definition(
            owner_module,
            owner_type.__name__,
        )
        class_method_names = {
            node.name
            for node in class_definition.body
            if isinstance(node, ast.FunctionDef)
        }
        owner_has_builder = hasattr(owner_type, "contract_builder_spec")
        source_tree_has_wrapper = hasattr(collection_replacement_support, wrapper_name)

        assert owner_has_builder
        assert "contract_builder_spec" in class_method_names
        assert not source_tree_has_wrapper
        assert wrapper_name not in source_tree_function_names


def test_source_tree_contract_builder_spec_constructor_sites_stay_owner_scoped() -> None:
    constructor_name = "_SourceTreeContractBuilderSpec"
    call_sites: list[tuple[str, ...]] = []

    for node in _parsed_module_ast(collection_replacement_support).body:
        if isinstance(node, ast.Assign):
            target_name = _assignment_target_name(node)
            if (
                isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == constructor_name
            ):
                call_sites.append(("assignment", target_name))
                continue
            if isinstance(node.value, ast.Dict):
                for key_node, value_node in zip(node.value.keys, node.value.values):
                    if (
                        isinstance(value_node, ast.Call)
                        and isinstance(value_node.func, ast.Name)
                        and value_node.func.id == constructor_name
                    ):
                        assert isinstance(key_node, ast.Constant)
                        call_sites.append(
                            (
                                "assignment-dict",
                                target_name,
                                str(key_node.value),
                            )
                        )
                continue
        if isinstance(node, ast.ClassDef):
            for class_node in node.body:
                if not isinstance(class_node, ast.FunctionDef):
                    continue
                if any(
                    isinstance(call_node.func, ast.Name)
                    and call_node.func.id == constructor_name
                    for call_node in ast.walk(class_node)
                    if isinstance(call_node, ast.Call)
                ):
                    call_sites.append(("method", node.name, class_node.name))

    assert frozenset(call_sites) == frozenset(
        {
            ("assignment", "_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC"),
            (
                "assignment-dict",
                "_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_SPECS",
                "collection-replacement-boundary",
            ),
            (
                "assignment-dict",
                "_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_SPECS",
                "module-boundary",
            ),
            (
                "method",
                "CompiledPatternModuleCompileContractCase",
                "contract_builder_spec",
            ),
            ("method", "CompiledPatternModuleSuccessOwnerSpec", "contract_builder_spec"),
            (
                "method",
                "_CompiledPatternModuleHelperKeywordContractSpec",
                "contract_builder_spec",
            ),
        }
    )
    assert not hasattr(support, "_SourceTreeContractBuilderSpec")


@pytest.mark.parametrize(
    ("owner",),
    tuple(
        pytest.param(owner, id=f"module-compile-{owner.case_id}")
        for owner in collection_replacement_support._COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES
    )
    + tuple(
        pytest.param(owner, id=f"module-success-{owner.case_id}")
        for owner in (
            collection_replacement_support._COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS
        )
    )
    + (
        pytest.param(
            collection_replacement_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC,
            id="module-helper-keyword-success",
        ),
        pytest.param(
            collection_replacement_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC,
            id="module-helper-keyword-error",
        ),
    ),
)
def test_compiled_pattern_contract_builder_owner_methods_return_live_specs(
    owner: object,
) -> None:
    owner_builder = getattr(owner, "contract_builder_spec", None)
    expected_manifest_timed_samples = getattr(owner, "manifest_timed_samples", 2)

    assert callable(owner_builder)
    built_spec = owner_builder()
    assert isinstance(
        built_spec,
        collection_replacement_support._SourceTreeContractBuilderSpec,
    )
    assert built_spec.manifest_timed_samples == expected_manifest_timed_samples
    assert built_spec.timing_scope == "module-helper-call"

def test_compiled_pattern_owner_builder_methods_return_shared_specs_directly() -> None:
    owner_spec = collection_replacement_support.CompiledPatternModuleSuccessOwnerSpec(
        case_id="synthetic-boundary",
        manifest_path=support.MODULE_BOUNDARY_MANIFEST_PATH,
        include_workload_selectors=(),
        contract_manifest_id="synthetic-boundary",
        contract_filename="synthetic_contract.py",
        note_surface="synthetic surface",
        expected_source_workload_ids=(),
        preserved_payload_fields=(),
        preserve_replacement_payload_typing=False,
    )
    built_spec = owner_spec.contract_builder_spec()

    assert built_spec == collection_replacement_support._SourceTreeContractBuilderSpec(
        manifest_id="synthetic-boundary",
        excluded_fields=(
            support.COMPILED_PATTERN_MODULE_SUCCESS_CONTRACT_EXCLUDED_FIELDS
        ),
        timing_scope="module-helper-call",
        notes=(
            "Ensures benchmark manifests keep the bounded "
            "compiled-pattern-first-argument successful "
            "synthetic surface rows unresolved until helper invocation.",
        ),
    )


def test_benchmark_test_support_drops_local_wrong_text_model_contract_builder() -> None:
    definition_names, _ = top_level_module_definition_and_assignment_names(
        support
    )

    assert "_compiled_pattern_wrong_text_model_contract_spec" not in definition_names
    assert not hasattr(support, "_compiled_pattern_wrong_text_model_contract_spec")


def test_collection_replacement_support_exports_compiled_pattern_module_helper_keyword_contract_surface(
) -> None:
    support_definition_names, support_assignment_names = (
        top_level_module_definition_and_assignment_names(support)
    )
    collection_definition_names, collection_assignment_names = (
        top_level_module_definition_and_assignment_names(
            collection_replacement_support
        )
    )
    moved_definition_names = {
        "_CompiledPatternModuleHelperKeywordContractSpec",
        "_CompiledPatternModuleHelperKeywordContractSurface",
    }
    assignment_only_names = {
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACE_PARAMS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS",
    }

    assert moved_definition_names.isdisjoint(
        support_definition_names | support_assignment_names
    )
    assert moved_definition_names <= collection_definition_names
    assert assignment_only_names <= collection_assignment_names
    assert assignment_only_names.isdisjoint(
        support_definition_names | support_assignment_names
    )
    assert not hasattr(support, "_is_collection_replacement_compiled_pattern_keyword_error_workload")
    assert not hasattr(anchor_support, "_is_collection_replacement_compiled_pattern_keyword_error_workload")
    assert hasattr(collection_replacement_support, "_is_collection_replacement_compiled_pattern_keyword_error_workload")
    for name in moved_definition_names:
        assert not hasattr(anchor_support, name)
        assert hasattr(collection_replacement_support, name)
    for name in assignment_only_names:
        assert not hasattr(support, name)
        assert not hasattr(anchor_support, name)
        assert hasattr(collection_replacement_support, name)


def test_benchmark_test_support_no_longer_exports_deleted_workload_id_selector_helpers(
) -> None:
    definition_names, _ = top_level_module_definition_and_assignment_names(
        support
    )
    deleted_names = frozenset(
        {
            "_split_workload_ids_by_text_model",
            "_selected_workload_ids",
            "_mirrored_bytes_workload_ids",
        }
    )

    assert deleted_names.isdisjoint(definition_names)
    for name in deleted_names:
        assert not hasattr(support, name)
        assert not hasattr(anchor_support, name)
        assert not hasattr(collection_replacement_support, name)


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


def test_deleted_pattern_boundary_owner_module_stays_unimportable_and_unreferenced(
) -> None:
    _assert_deleted_benchmark_module_stays_absent(
        deleted_module_name="tests.benchmarks.test_pattern_boundary_benchmark_anchor_support",
        deleted_path=(
            REPO_ROOT
            / "tests"
            / "benchmarks"
            / "test_pattern_boundary_benchmark_anchor_support.py"
        ),
    )


def test_deleted_benchmark_module_absence_helper_rejects_lingering_import_targets(
    monkeypatch,
    tmp_path,
) -> None:
    deleted_module_name = "tests.benchmarks.synthetic_deleted_support"
    deleted_path = tmp_path / "synthetic_deleted_support.py"
    original_import_module = importlib.import_module

    monkeypatch.setattr(
        importlib,
        "import_module",
        lambda module_name: (
            (_ for _ in ()).throw(ModuleNotFoundError(module_name))
            if module_name == deleted_module_name
            else original_import_module(module_name)
        ),
    )
    monkeypatch.setitem(
        globals(),
        "_benchmark_support_import_targets_by_path",
        lambda: (
            (
                pathlib.Path("tests/benchmarks/test_synthetic_owner.py"),
                frozenset({deleted_module_name}),
            ),
        ),
    )

    with pytest.raises(AssertionError):
        _assert_deleted_benchmark_module_stays_absent(
            deleted_module_name=deleted_module_name,
            deleted_path=deleted_path,
        )


def test_deleted_benchmark_module_absence_helper_ignores_stale_sys_modules_entry(
    monkeypatch,
    tmp_path,
) -> None:
    deleted_module_name = "tests.benchmarks.synthetic_deleted_support"
    deleted_path = tmp_path / "synthetic_deleted_support.py"

    monkeypatch.setitem(
        sys.modules,
        deleted_module_name,
        SimpleNamespace(__name__=deleted_module_name),
    )

    _assert_deleted_benchmark_module_stays_absent(
        deleted_module_name=deleted_module_name,
        deleted_path=deleted_path,
    )

    assert deleted_module_name not in sys.modules


def test_collection_replacement_support_reaches_source_tree_owner_surface_through_benchmark_test_support_alias(
) -> None:
    assert collection_replacement_support is not support
    assert collection_replacement_support.benchmark_test_support is support
    assert not hasattr(collection_replacement_support, "collection_replacement_support")


def test_compiled_pattern_module_compile_surviving_suites_import_shared_support_exports(
) -> None:
    module = importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )
    support_definition_names, support_assignment_names = (
        top_level_module_definition_and_assignment_names(support)
    )
    definition_names, assignment_names = (
        top_level_module_definition_and_assignment_names(module)
    )
    _assert_owner_module_routes_through_package_import(
        module,
        owner_module="tests.benchmarks.benchmark_test_support",
        package_module="tests.benchmarks",
        expected_alias_pairs=frozenset({("benchmark_test_support", None)}),
    )
    assert {
        "_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES",
        "_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS",
        "_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS",
        "_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS",
        "_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES",
        "COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS",
        "_assert_compiled_pattern_module_compile_success_payload_round_trip",
        "_assert_compiled_pattern_module_compile_keyword_payload_round_trip",
    }.issubset(definition_names | assignment_names)
    assert {
        "_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES",
        "_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS",
        "_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS",
        "_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS",
        "_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES",
        "COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS",
        "_assert_compiled_pattern_module_compile_success_payload_round_trip",
        "_assert_compiled_pattern_module_compile_keyword_payload_round_trip",
    }.isdisjoint(support_definition_names | support_assignment_names)


def test_compiled_pattern_module_helper_standard_owner_surface_surviving_suites_import_source_tree_exports(
) -> None:
    module = importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )
    support_definition_names, support_assignment_names = (
        top_level_module_definition_and_assignment_names(support)
    )
    definition_names, assignment_names = (
        top_level_module_definition_and_assignment_names(module)
    )
    local_owner_names = {
        "_compiled_pattern_module_compile_keyword_kwargs_signature",
        "_module_workflow_compiled_pattern_compile_correctness_case_signature",
        "_module_workflow_compiled_pattern_compile_workload_signature",
        "_is_module_workflow_compiled_pattern_compile_workload",
        "_is_module_workflow_compiled_pattern_compile_success_workload",
        "_workload_matches_expected_exception",
        "_module_workflow_compiled_pattern_compile_keyword_correctness_case_signature",
        "_module_workflow_compiled_pattern_compile_keyword_workload_signature",
        "_is_module_workflow_compiled_pattern_compile_keyword_workload",
        "compiled_pattern_contract_expected_build_calls",
        "_run_cpython_compiled_pattern_module_helper_workload",
        "_assert_wrong_text_model_payload_round_trip",
        "_assert_compiled_pattern_module_success_payload_round_trip",
        "_assert_compiled_pattern_success_rows_measured_in_combined_manifest",
        "include_live_compiled_pattern_module_success_workload",
        "_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_SPECS",
        "_compiled_pattern_wrong_text_model_source_workloads",
        "_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC",
        "_PATTERN_BOUNDARY_STANDARD_DEFINITION_BLOCK",
        "_compiled_pattern_module_helper_runtime_route",
        "_compiled_pattern_module_helper_route",
        "_COMPILED_PATTERN_MODULE_HELPER_STANDARD_DEFINITION_BLOCK",
        "COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS",
        "PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS",
        "_source_tree_standard_benchmark_definitions",
        "SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS",
    }

    _assert_owner_module_routes_through_package_import(
        module,
        owner_module="tests.benchmarks.benchmark_test_support",
        package_module="tests.benchmarks",
        expected_alias_pairs=frozenset({("benchmark_test_support", None)}),
    )
    assert local_owner_names.issubset(definition_names | assignment_names)
    assert local_owner_names.isdisjoint(support_definition_names | support_assignment_names)
    assert "_build_source_tree_standard_anchor_contract_definitions" not in (
        support_definition_names | support_assignment_names
    )


@pytest.mark.parametrize(
    ("module_name", "expected_imported_names", "expected_alias_pairs"),
    (
        (
            "tests.benchmarks.test_source_tree_combined_boundary_benchmarks",
            frozenset(
                {
                    "_source_tree_contract_manifest",
                    "_source_tree_contract_workload",
                    "_expected_exception_instance",
                    "_record_numeric_materialization_fields",
                    "assert_pattern_helper_wrong_text_model_payload_round_trip",
                    "compiled_pattern_contract_expected_build_calls",
                    "_run_cpython_compiled_pattern_module_helper_workload",
                    "_assert_wrong_text_model_payload_round_trip",
                    "_assert_compiled_pattern_module_success_payload_round_trip",
                    "_assert_compiled_pattern_success_rows_measured_in_combined_manifest",
                    "include_live_compiled_pattern_module_success_workload",
                }
            ),
            frozenset({("benchmark_test_support", None)}),
        ),
    ),
)
def test_source_tree_contract_helper_suites_import_shared_alias_but_define_local_helpers(
    module_name: str,
    expected_imported_names: frozenset[str],
    expected_alias_pairs: frozenset[tuple[str, str | None]],
) -> None:
    module = importlib.import_module(module_name)

    assert _top_level_import_from_alias_pairs(
        _parsed_module_ast(module),
        module_name="tests.benchmarks",
        imported_names=frozenset({"benchmark_test_support"}),
    ) == expected_alias_pairs
    assert expected_imported_names.issubset(dir(module))
    assert expected_imported_names.isdisjoint(dir(module.benchmark_test_support))
    assert "tests.benchmarks.benchmark_test_support" not in _module_import_targets(
        module
    )


def test_clear_anchor_support_caches_refreshes_published_manifest_id_fallbacks(
    monkeypatch,
    anchor_support_cache_guard: None,
) -> None:
    combined_suite = importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )
    initial_published_manifests = lambda: (
        SimpleNamespace(manifest_id="module-boundary"),
    )

    monkeypatch.setattr(
        support,
        "published_benchmark_manifests",
        initial_published_manifests,
    )
    monkeypatch.setattr(
        combined_suite,
        "published_benchmark_manifests",
        initial_published_manifests,
    )
    support._clear_anchor_support_caches()

    assert combined_suite._published_benchmark_manifest_ids() == frozenset(
        {"module-boundary"}
    )
    assert not hasattr(support, "SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS")
    assert (
        "synthetic-new-boundary"
        not in combined_suite.SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS
    )

    refreshed_published_manifests = lambda: (
        SimpleNamespace(manifest_id="synthetic-new-boundary"),
    )
    monkeypatch.setattr(
        support,
        "published_benchmark_manifests",
        refreshed_published_manifests,
    )
    monkeypatch.setattr(
        combined_suite,
        "published_benchmark_manifests",
        refreshed_published_manifests,
    )

    assert combined_suite._published_benchmark_manifest_ids() == frozenset(
        {"module-boundary"}
    )
    assert (
        "synthetic-new-boundary"
        not in combined_suite.SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS
    )

    support._clear_anchor_support_caches()

    assert combined_suite._published_benchmark_manifest_ids() == frozenset(
        {"synthetic-new-boundary"}
    )
    assert (
        "synthetic-new-boundary"
        in combined_suite.SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS
    )
    assert (
        combined_suite.SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[
            "synthetic-new-boundary"
        ]
        is combined_suite._SOURCE_TREE_DEFAULT_COMBINED_MANIFEST_EXPECTATION
    )


def test_source_tree_combined_manifest_expectations_get_preserves_fallback_contract(
    monkeypatch,
    anchor_support_cache_guard: None,
) -> None:
    combined_suite = importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )
    default_value = combined_suite._combined_manifest_definition(
        representative_measured_workload_ids=("custom-default",),
    )
    published_manifests = lambda: (
        SimpleNamespace(manifest_id="module-boundary"),
        SimpleNamespace(manifest_id="synthetic-fallback-boundary"),
    )

    monkeypatch.setattr(
        support,
        "published_benchmark_manifests",
        published_manifests,
    )
    monkeypatch.setattr(
        combined_suite,
        "published_benchmark_manifests",
        published_manifests,
    )
    support._clear_anchor_support_caches()

    expectations = combined_suite.SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS

    assert "synthetic-fallback-boundary" in expectations
    assert expectations.get("synthetic-fallback-boundary") is (
        combined_suite._SOURCE_TREE_DEFAULT_COMBINED_MANIFEST_EXPECTATION
    )
    assert expectations.get("synthetic-fallback-boundary", default_value) is (
        combined_suite._SOURCE_TREE_DEFAULT_COMBINED_MANIFEST_EXPECTATION
    )
    assert "synthetic-missing-boundary" not in expectations
    assert expectations.get("synthetic-missing-boundary") is None
    assert expectations.get("synthetic-missing-boundary", default_value) is default_value
    assert 7 not in expectations


def test_source_tree_combined_manifest_expectations_fallback_lookup_preserves_dict_shape(
    monkeypatch,
    anchor_support_cache_guard: None,
) -> None:
    combined_suite = importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )
    published_manifests = lambda: (
        SimpleNamespace(manifest_id="compile-matrix"),
        SimpleNamespace(manifest_id="synthetic-fallback-boundary"),
    )

    monkeypatch.setattr(
        support,
        "published_benchmark_manifests",
        published_manifests,
    )
    monkeypatch.setattr(
        combined_suite,
        "published_benchmark_manifests",
        published_manifests,
    )
    support._clear_anchor_support_caches()

    expectations = combined_suite.SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS
    explicit_keys_before_lookup = tuple(expectations.keys())
    explicit_length_before_lookup = len(expectations)

    assert expectations["compile-matrix"] is expectations.get("compile-matrix")
    assert expectations["synthetic-fallback-boundary"] is (
        combined_suite._SOURCE_TREE_DEFAULT_COMBINED_MANIFEST_EXPECTATION
    )
    assert expectations.get("synthetic-fallback-boundary") is (
        combined_suite._SOURCE_TREE_DEFAULT_COMBINED_MANIFEST_EXPECTATION
    )
    assert "synthetic-fallback-boundary" in expectations

    assert tuple(expectations.keys()) == explicit_keys_before_lookup
    assert len(expectations) == explicit_length_before_lookup
    assert "synthetic-fallback-boundary" not in expectations.keys()
    assert "synthetic-fallback-boundary" not in dict(expectations)
    assert tuple(expectations.items()) == tuple(dict(expectations).items())


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
                manifest_id=_compiled_pattern_module_helper_manifest_id(
                    "module.match"
                ),
                workload_id="module-match-success",
                operation="module.match",
                pattern="abc",
                haystack="abczz",
                flags=re.MULTILINE,
                use_compiled_pattern=True,
            ),
            re.MULTILINE,
            "module-result",
            ("module.match", "abczz", 0, {}),
            ("abczz", re.MULTILINE),
            False,
        ),
        (
            synthetic_workload(
                manifest_id=_compiled_pattern_module_helper_manifest_id(
                    "module.fullmatch"
                ),
                workload_id="module-fullmatch-success",
                operation="module.fullmatch",
                pattern="a.c",
                haystack="abc",
                text_model="bytes",
                flags=re.DOTALL,
                use_compiled_pattern=True,
            ),
            re.DOTALL,
            "module-result",
            ("module.fullmatch", b"abc", 0, {}),
            (b"abc", re.DOTALL),
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
                manifest_id=_compiled_pattern_module_helper_manifest_id("module.findall"),
                workload_id="module-findall-success",
                operation="module.findall",
                pattern="abc",
                haystack="abcabc",
                flags=re.IGNORECASE,
                use_compiled_pattern=True,
            ),
            re.IGNORECASE,
            "module-result",
            ("module.findall", "abcabc", re.IGNORECASE),
            ("abcabc", re.IGNORECASE),
            False,
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
        (
            synthetic_workload(
                manifest_id=_compiled_pattern_module_helper_manifest_id("module.sub"),
                workload_id="module-sub-success",
                operation="module.sub",
                pattern="abc",
                haystack="abcabc",
                replacement="x",
                count=1,
                flags=re.DOTALL,
                use_compiled_pattern=True,
            ),
            re.DOTALL,
            "module-result",
            ("module.sub", "x", "abcabc", 1, re.DOTALL, {}),
            ("x", "abcabc", 1),
            False,
        ),
    ),
    ids=(
        "module-boundary-search",
        "module-boundary-match",
        "module-boundary-fullmatch-bytes",
        "collection-replacement-subn",
        "wrong-text-model-finditer",
        "collection-replacement-findall",
        "collection-replacement-split",
        "collection-replacement-sub",
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
    route = collection_replacement_support._compiled_pattern_module_helper_route(
        workload,
        collection_replacement_callback_flags=callback_flags,
    )
    callback_result, callback_call, cpython_call_args, materialize_cpython_result = route

    assert callback_result == expected_result
    assert callback_call == expected_call
    assert cpython_call_args == expected_cpython_args
    assert materialize_cpython_result is materialize


@pytest.mark.parametrize(
    ("workload", "expected_result", "expected_match_group0"),
    (
        pytest.param(
            synthetic_workload(
                manifest_id=_compiled_pattern_module_helper_manifest_id("module.split"),
                workload_id="module-split-runtime",
                operation="module.split",
                pattern="abc",
                haystack="abcabc",
                maxsplit=1,
                use_compiled_pattern=True,
            ),
            ["", "abc"],
            None,
            id="split-preserves-list-result",
        ),
        pytest.param(
            synthetic_workload(
                manifest_id=_compiled_pattern_module_helper_manifest_id("module.search"),
                workload_id="module-search-runtime",
                operation="module.search",
                pattern="abc",
                haystack="zzabczz",
                use_compiled_pattern=True,
            ),
            None,
            "abc",
            id="search-preserves-match-result",
        ),
        pytest.param(
            synthetic_workload(
                manifest_id=_compiled_pattern_module_helper_manifest_id("module.match"),
                workload_id="module-match-runtime",
                operation="module.match",
                pattern="abc",
                haystack="abczz",
                use_compiled_pattern=True,
            ),
            None,
            "abc",
            id="match-preserves-match-result",
        ),
        pytest.param(
            synthetic_workload(
                manifest_id=_compiled_pattern_module_helper_manifest_id(
                    "module.fullmatch"
                ),
                workload_id="module-fullmatch-runtime",
                operation="module.fullmatch",
                pattern="a.c",
                haystack="abc",
                text_model="bytes",
                use_compiled_pattern=True,
            ),
            None,
            b"abc",
            id="fullmatch-preserves-bytes-match-result",
        ),
        pytest.param(
            synthetic_workload(
                manifest_id=_compiled_pattern_module_helper_manifest_id("module.finditer"),
                workload_id="module-finditer-runtime",
                operation="module.finditer",
                pattern="abc",
                haystack="abcabc",
                use_compiled_pattern=True,
            ),
            ["abc", "abc"],
            None,
            id="finditer-materializes-match-iterator",
        ),
        pytest.param(
            synthetic_workload(
                manifest_id=_compiled_pattern_module_helper_manifest_id("module.findall"),
                workload_id="module-findall-runtime",
                operation="module.findall",
                pattern="abc",
                haystack="abcabc",
                use_compiled_pattern=True,
            ),
            ["abc", "abc"],
            None,
            id="findall-preserves-list-result",
        ),
        pytest.param(
            synthetic_workload(
                manifest_id=_compiled_pattern_module_helper_manifest_id("module.sub"),
                workload_id="module-sub-runtime",
                operation="module.sub",
                pattern="abc",
                haystack="abcabc",
                replacement="x",
                count=1,
                use_compiled_pattern=True,
            ),
            "xabc",
            None,
            id="sub-preserves-string-result",
        ),
        pytest.param(
            synthetic_workload(
                manifest_id=_compiled_pattern_module_helper_manifest_id("module.subn"),
                workload_id="module-subn-runtime",
                operation="module.subn",
                pattern="abc",
                haystack="abcabc",
                replacement="x",
                count=1,
                use_compiled_pattern=True,
            ),
            ("xabc", 1),
            None,
            id="subn-preserves-tuple-result",
        ),
    ),
)
def test_run_cpython_compiled_pattern_module_helper_workload_preserves_expected_result_shapes(
    workload: object,
    expected_result: object,
    expected_match_group0: object | None,
) -> None:
    result = (
        collection_replacement_support._run_cpython_compiled_pattern_module_helper_workload(
            workload,
            collection_replacement_callback_flags=0,
        )
    )

    if expected_match_group0 is not None:
        assert isinstance(result, re.Match)
        assert result.group(0) == expected_match_group0
        assert result.string == workload.haystack_payload()
        assert result.re.pattern == workload.pattern_payload()
        return

    if workload.operation == "module.finditer":
        assert isinstance(result, list)
        assert [match.group(0) for match in result] == expected_result
        return

    if workload.operation == "module.split":
        assert isinstance(result, list)
        assert result == expected_result
        return

    assert result == expected_result


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

    assert collection_replacement_support._is_module_workflow_compiled_pattern_wrong_text_model_workload(
        workload
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
        collection_replacement_support._is_module_workflow_compiled_pattern_wrong_text_model_workload(
            wrong_pattern_argument
        )
    )
    assert not (
        collection_replacement_support._is_module_workflow_compiled_pattern_wrong_text_model_workload(
            missing_haystack_text_model
        )
    )
    assert not (
        collection_replacement_support._is_module_workflow_compiled_pattern_wrong_text_model_workload(
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
        collection_replacement_support._is_module_workflow_compiled_pattern_literal_success_workload(
            literal_workload
        )
    )
    assert (
        collection_replacement_support._module_workflow_compiled_pattern_workload_signature(
            literal_workload
        )
        == ("module.search", "abc", ("zzabczz",), True, 0, "str")
    )

    assert (
        collection_replacement_support._is_module_workflow_compiled_pattern_bounded_wildcard_success_workload(
            wildcard_workload
        )
    )
    assert (
        collection_replacement_support._module_workflow_compiled_pattern_workload_signature(
            wildcard_workload
        )
        == ("module.fullmatch", b"a.c", (b"abc",), True, 0, "bytes")
    )

    assert (
        collection_replacement_support._is_module_workflow_compiled_pattern_verbose_bytes_success_workload(
            verbose_workload
        )
    )
    assert (
        collection_replacement_support._module_workflow_compiled_pattern_workload_signature(
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
        collection_replacement_support._is_module_workflow_compiled_pattern_literal_success_workload(
            direct_pattern_workload
        )
    )
    assert not (
        collection_replacement_support._is_module_workflow_compiled_pattern_bounded_wildcard_success_workload(
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
        collection_replacement_support._module_workflow_compiled_pattern_correctness_case_signature(
            matching_case
        )
        == ("module.search", "abc", ("zzabczz",), True, 0, "str")
    )
    assert (
        collection_replacement_support._module_workflow_compiled_pattern_correctness_case_signature(
            missing_args_case
        )
        is None
    )
    assert (
        collection_replacement_support._module_workflow_compiled_pattern_correctness_case_signature(
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

    assert collection_replacement_support.anchored_workload_case_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=_synthetic_workload_signature,
        include_workload=_synthetic_workload_is_included,
    ) == {
        ("synthetic_boundary.py", "anchored"): ("case-a", "case-b"),
        ("synthetic_boundary.py", "unanchored"): (),
    }
    assert collection_replacement_support.unanchored_workload_ids(
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
        collection_replacement_support,
        "published_cases_by_id",
        lambda: records_by_string_id((case,), id_attr="case_id"),
    )

    anchored_pairs = collection_replacement_support.expected_anchored_workload_case_pairs(
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
        collection_replacement_support,
        "published_cases_by_id",
        lambda: records_by_string_id(
            (SimpleNamespace(case_id="case-1"),),
            id_attr="case_id",
        ),
    )

    with pytest.raises(AssertionError, match="does not match"):
        collection_replacement_support.expected_anchored_workload_case_pairs(
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
        collection_replacement_support,
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
        collection_replacement_support.expected_anchored_workload_case_pairs(
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
        collection_replacement_support,
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
        collection_replacement_support.expected_anchored_workload_case_pairs(
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
        collection_replacement_support,
        "published_cases_by_id",
        lambda: records_by_string_id((), id_attr="case_id"),
    )

    with pytest.raises(
        AssertionError,
        match=r"expected anchored correctness case 'case-1' to be published",
    ):
        collection_replacement_support.expected_anchored_workload_case_pairs(
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
        collection_replacement_support,
        "run_correctness_case_with_cpython",
        lambda case: f"expected:{case.case_id}",
    )
    monkeypatch.setattr(
        support,
        "assert_benchmark_workload_matches_expected_result",
        lambda workload, expected: calls.append((workload, expected)),
    )

    collection_replacement_support.assert_anchored_workload_case_result_parity((pair,))

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

    monkeypatch.setattr(
        collection_replacement_support,
        "run_correctness_case_with_cpython",
        _raise_expected,
    )
    monkeypatch.setattr(support, "run_benchmark_workload_with_cpython", _raise_observed)

    collection_replacement_support.assert_anchored_workload_case_result_parity((pair,))

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

    monkeypatch.setattr(
        collection_replacement_support,
        "run_correctness_case_with_cpython",
        _raise_expected,
    )
    monkeypatch.setattr(support, "run_benchmark_workload_with_cpython", _raise_observed)

    with pytest.raises(AssertionError):
        collection_replacement_support.assert_anchored_workload_case_result_parity((pair,))


def test_standard_benchmark_definition_params_preserve_names_and_filters() -> None:
    def _assert_filtered_definition_params(
        predicate,
    ) -> tuple[collection_replacement_support.StandardBenchmarkAnchorContractDefinition, ...]:
        standard_definitions = _explicit_standard_benchmark_definitions()
        params = collection_replacement_support._standard_benchmark_definition_params(
            standard_definitions,
            include_definition=predicate
        )
        expected_definitions = tuple(
            definition
            for definition in standard_definitions
            if predicate(definition)
        )

        assert tuple(parameter.values[0] for parameter in params) == expected_definitions
        assert tuple(parameter.id for parameter in params) == tuple(
            definition.name for definition in expected_definitions
        )

        return expected_definitions

    legacy_definitions = _assert_filtered_definition_params(
        collection_replacement_support._has_standard_benchmark_legacy_workloads
    )
    callback_definitions = _assert_filtered_definition_params(
        collection_replacement_support._runs_standard_benchmark_callback_result_parity
    )
    special_unanchored_definitions = _assert_filtered_definition_params(
        collection_replacement_support._has_standard_benchmark_special_unanchored_workloads
    )
    direct_parity_definitions = _assert_filtered_definition_params(
        collection_replacement_support._has_standard_benchmark_special_unanchored_direct_parity_cases
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
        collection_replacement_support._standard_benchmark_definition_id(definition)
        for definition in _explicit_standard_benchmark_definitions()
    ) == tuple(
        definition.name
        for definition in _explicit_standard_benchmark_definitions()
    )


def test_standard_benchmark_manifest_params_preserve_definition_and_manifest_order() -> None:
    standard_definitions = _explicit_standard_benchmark_definitions()
    manifest_params = collection_replacement_support._standard_benchmark_manifest_params(standard_definitions)

    assert tuple(
        (parameter.values[0].name, parameter.values[1].name)
        for parameter in manifest_params
    ) == tuple(
        (definition.name, manifest_path.name)
        for definition in standard_definitions
        for manifest_path in definition.manifest_paths
    )


def test_standard_benchmark_definition_includes_workload_filters_owner_scoped_rows(
) -> None:
    definition = collection_replacement_support.StandardBenchmarkAnchorContractDefinition(
        name="synthetic",
        manifest_paths=(pathlib.Path("synthetic_boundary.py"),),
        expected_anchor_case_ids={},
        include_workload=_synthetic_workload_is_included,
        correctness_case_signature=lambda case: case.signature,
        workload_signature=_synthetic_workload_signature,
        expected_excluded_workload_ids=frozenset({"excluded"}),
        expected_special_unanchored_workload_ids=("special",),
    )

    assert definition.includes_workload(
        _synthetic_workload("anchored", ("shared",))
    )
    assert not definition.includes_workload(
        _synthetic_workload("excluded", ("shared",))
    )
    assert not definition.includes_workload(
        _synthetic_workload("special", ("shared",))
    )
    assert not definition.includes_workload(
        _synthetic_workload("predicate-false", ("shared",), include=False)
    )


def test_anchor_workload_case_helpers_respect_standard_definition_scope_filter(
    monkeypatch: pytest.MonkeyPatch,
    anchor_support_cache_guard: None,
) -> None:
    manifest_path = pathlib.Path("synthetic_boundary.py")
    workloads = (
        _synthetic_workload("anchored", ("shared",)),
        _synthetic_workload("unanchored", ("missing",)),
        _synthetic_workload("excluded", ("shared",)),
        _synthetic_workload("special", ("shared",)),
        _synthetic_workload("predicate-false", ("missing",), include=False),
    )
    definition = collection_replacement_support.StandardBenchmarkAnchorContractDefinition(
        name="synthetic",
        manifest_paths=(manifest_path,),
        expected_anchor_case_ids={},
        include_workload=_synthetic_workload_is_included,
        correctness_case_signature=lambda case: case.signature,
        workload_signature=_synthetic_workload_signature,
        expected_excluded_workload_ids=frozenset({"excluded"}),
        expected_special_unanchored_workload_ids=("special",),
    )
    monkeypatch.setattr(
        support,
        "load_manifest",
        lambda path: _synthetic_manifest_loader(path, workloads=workloads),
    )

    anchor_case_ids = {("shared",): ("case-a",)}

    assert collection_replacement_support.anchored_workload_case_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=definition.workload_signature,
        include_workload=definition.includes_workload,
    ) == {
        ("synthetic_boundary.py", "anchored"): ("case-a",),
        ("synthetic_boundary.py", "unanchored"): (),
    }
    assert collection_replacement_support.unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=anchor_case_ids,
        workload_signature=definition.workload_signature,
        include_workload=definition.includes_workload,
    ) == ("unanchored",)


def test_standard_benchmark_special_unanchored_result_parity_params_preserve_order() -> None:
    standard_definitions = _explicit_standard_benchmark_definitions()
    params = collection_replacement_support._standard_benchmark_special_unanchored_result_parity_params(
        standard_definitions
    )

    assert tuple(
        (parameter.values[0].name, parameter.values[1])
        for parameter in params
    ) == tuple(
        (definition.name, workload_id)
        for definition in standard_definitions
        if definition.run_special_unanchored_result_parity
        for workload_id in definition.expected_special_unanchored_workload_ids
    )


def test_standard_benchmark_special_unanchored_workloads_stay_live_and_out_of_standard_scope(
    anchor_support_cache_guard: None,
) -> None:
    standard_definitions = _explicit_standard_benchmark_definitions()

    for definition in standard_definitions:
        if not definition.expected_special_unanchored_workload_ids:
            continue

        observed_live_workload_ids = tuple(
            workload.workload_id
            for manifest_path in definition.manifest_paths
            for workload in support.manifest_workloads(manifest_path)
            if workload.workload_id in definition.expected_special_unanchored_workload_ids
        )
        scoped_workload_ids = tuple(
            workload.workload_id
            for manifest_path in definition.manifest_paths
            for workload in support.selected_manifest_workloads(
                manifest_path,
                include_workload=definition.includes_workload,
            )
        )
        anchored_workload_ids = {
            workload_id
            for manifest_name, workload_id in definition.expected_anchor_case_ids
            if manifest_name in {manifest_path.name for manifest_path in definition.manifest_paths}
        }

        assert observed_live_workload_ids == definition.expected_special_unanchored_workload_ids
        assert not (
            anchored_workload_ids
            & set(definition.expected_special_unanchored_workload_ids)
        )
        assert not (
            set(scoped_workload_ids)
            & set(definition.expected_special_unanchored_workload_ids)
        )


def test_source_tree_combined_suite_does_not_expose_deleted_standard_benchmark_inventory(
) -> None:
    combined_suite = importlib.import_module(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )
    support_definition_names, support_assignment_names = (
        top_level_module_definition_and_assignment_names(support)
    )
    definition_names, assignment_names = (
        top_level_module_definition_and_assignment_names(combined_suite)
    )
    owner_only_names = {
        "StandardBenchmarkAnchorContractDefinition",
        "published_case_ids_by_signature",
        "anchored_workload_case_ids",
        "unanchored_workload_ids",
        "expected_anchored_workload_case_pairs",
        "assert_anchored_workload_case_result_parity",
        "assert_zero_gap_manifest_workloads_measured",
        "_standard_benchmark_definition_params",
        "_standard_benchmark_manifest_params",
        "_standard_benchmark_special_unanchored_result_parity_params",
    }

    assert "STANDARD_BENCHMARK_DEFINITIONS" not in (
        definition_names | assignment_names
    )
    assert not hasattr(combined_suite, "STANDARD_BENCHMARK_DEFINITIONS")
    assert combined_suite.benchmark_test_support is support
    assert not hasattr(combined_suite.benchmark_test_support, "STANDARD_BENCHMARK_DEFINITIONS")
    assert owner_only_names.isdisjoint(support_definition_names | support_assignment_names)
    assert owner_only_names.issubset(definition_names | assignment_names)


def test_recording_benchmark_support_records_compile_calls_and_reuses_compiled_patterns(
) -> None:
    module = support.RecordingBenchmarkModule()
    compiled_pattern = module.compile("abc", 0)

    assert module.calls == [("compile", "abc", 0)]
    assert len(module.compiled_patterns) == 1
    assert module.compiled_patterns[0] is compiled_pattern
    assert module.compile(compiled_pattern, 0) is compiled_pattern
    assert module.calls[-1] == ("compile", compiled_pattern, 0)


def test_recording_benchmark_support_records_helper_call_before_raising() -> None:
    module = support.RecordingBenchmarkModule(
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
    module = support.RecordingBenchmarkModule()
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
    assert isinstance(compiled_pattern, support.RecordingBenchmarkCompiledPattern)

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
    module = support.RecordingBenchmarkModule()
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
    module = support.RecordingBenchmarkModule(
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
    module = support.RecordingBenchmarkModule()
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
