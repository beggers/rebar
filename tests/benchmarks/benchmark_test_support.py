from __future__ import annotations

import ast
from collections.abc import Callable, Iterable
from dataclasses import dataclass
import importlib
import inspect
import pathlib
import re
import sys
import textwrap
from functools import cache
from functools import partial
from types import SimpleNamespace
from typing import Any, Protocol
import unittest

import pytest

from rebar_harness import benchmarks
from rebar_harness.benchmarks import (
    BenchmarkManifest,
    Workload,
    load_manifest,
    workload_from_payload,
    workload_to_payload,
)
from rebar_harness.correctness import published_fixture_manifests
from rebar_harness.scorecard_io import build_cpython_baseline
from tests.conftest import REPO_ROOT, records_by_string_id
from tests.python.fixture_parity_support import (
    assert_match_result_parity,
    assert_pattern_parity,
    case_pattern,
    module_workflow_keyword_kwargs_signature,
    module_workflow_positional_args_signature,
)


class StandardBenchmarkAnchorContract(Protocol):
    manifest_paths: tuple[pathlib.Path, ...]
    expected_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]]
    correctness_case_signature: Callable[[Any], tuple[Any, ...] | None]
    workload_signature: Callable[[Any], tuple[Any, ...]]
    callback_anchor_workload_ids: frozenset[str]
    expected_legacy_workload_ids: frozenset[str]

    def includes_workload(self, workload: Any) -> bool: ...


@dataclass(frozen=True, slots=True)
class StandardBenchmarkAnchorContractDefinition:
    name: str
    manifest_paths: tuple[pathlib.Path, ...]
    expected_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]]
    include_workload: Callable[[Any], bool]
    correctness_case_signature: Callable[[Any], tuple[Any, ...] | None]
    workload_signature: Callable[[Any], tuple[Any, ...]]
    run_callback_result_parity: bool = False
    expected_excluded_workload_ids: frozenset[str] = frozenset()
    expected_legacy_workload_ids: frozenset[str] = frozenset()
    callback_anchor_workload_ids: frozenset[str] = frozenset()
    expected_special_unanchored_workload_ids: tuple[str, ...] = ()
    direct_parity_supplemental_cases: tuple[Any, ...] = ()
    run_special_unanchored_result_parity: bool = False

    def includes_workload(self, workload: Any) -> bool:
        return (
            workload.workload_id not in self.expected_excluded_workload_ids
            and workload.workload_id
            not in self.expected_special_unanchored_workload_ids
            and self.include_workload(workload)
        )


@dataclass(frozen=True, slots=True)
class _SourceTreeContractBuilderSpec:
    manifest_id: str
    excluded_fields: frozenset[str]
    manifest_timed_samples: int = 2
    timing_scope: str | None = None
    notes: tuple[str, ...] = ()


class RecordingBenchmarkCompiledPattern:
    def __init__(self, calls: list[tuple[object, ...]]) -> None:
        self._calls = calls

    def search(self, haystack: object, *args: object, **kwargs: object) -> object:
        self._calls.append(("pattern.search", haystack, args, kwargs))
        return "pattern-result"

    def match(self, haystack: object, *args: object, **kwargs: object) -> object:
        self._calls.append(("pattern.match", haystack, args, kwargs))
        return "pattern-result"

    def fullmatch(
        self,
        haystack: object,
        *args: object,
        **kwargs: object,
    ) -> object:
        self._calls.append(("pattern.fullmatch", haystack, args, kwargs))
        return "pattern-result"

    def split(self, haystack: object, *args: object, **kwargs: object) -> object:
        self._calls.append(("pattern.split", haystack, args, kwargs))
        return "pattern-result"

    def sub(
        self,
        repl: object,
        string: object,
        *args: object,
        **kwargs: object,
    ) -> object:
        self._calls.append(("pattern.sub", repl, string, args, kwargs))
        return "pattern-result"

    def subn(
        self,
        repl: object,
        string: object,
        *args: object,
        **kwargs: object,
    ) -> object:
        self._calls.append(("pattern.subn", repl, string, args, kwargs))
        return ("pattern-result", 0)


class RecordingBenchmarkModule:
    def __init__(
        self,
        *,
        helper_exception: Exception | None = None,
        compile_exception: Exception | None = None,
    ) -> None:
        self.calls: list[tuple[object, ...]] = []
        self._helper_exception = helper_exception
        self._compile_exception = compile_exception
        self.compiled_patterns: list[RecordingBenchmarkCompiledPattern] = []

    def _maybe_raise_helper_exception(self) -> None:
        if self._helper_exception is not None:
            raise self._helper_exception

    def purge(self) -> None:
        self.calls.append(("purge",))

    def compile(
        self,
        pattern: object,
        flags: int = 0,
    ) -> RecordingBenchmarkCompiledPattern:
        self.calls.append(("compile", pattern, flags))
        if isinstance(pattern, RecordingBenchmarkCompiledPattern):
            if self._compile_exception is not None:
                raise self._compile_exception
            return pattern
        compiled_pattern = RecordingBenchmarkCompiledPattern(self.calls)
        self.compiled_patterns.append(compiled_pattern)
        return compiled_pattern

    def search(
        self,
        pattern: object,
        haystack: object,
        flags: int = 0,
        **kwargs: object,
    ) -> object:
        self.calls.append(("module.search", pattern, haystack, flags, kwargs))
        self._maybe_raise_helper_exception()
        return "module-result"

    def match(
        self,
        pattern: object,
        haystack: object,
        flags: int = 0,
        **kwargs: object,
    ) -> object:
        self.calls.append(("module.match", pattern, haystack, flags, kwargs))
        self._maybe_raise_helper_exception()
        return "module-result"

    def fullmatch(
        self,
        pattern: object,
        haystack: object,
        flags: int = 0,
        **kwargs: object,
    ) -> object:
        self.calls.append(("module.fullmatch", pattern, haystack, flags, kwargs))
        self._maybe_raise_helper_exception()
        return "module-result"

    def split(
        self,
        pattern: object,
        haystack: object,
        *args: object,
        **kwargs: object,
    ) -> object:
        maxsplit = args[0] if args else 0
        flags = args[1] if len(args) > 1 else 0
        self.calls.append(("module.split", pattern, haystack, maxsplit, flags, kwargs))
        self._maybe_raise_helper_exception()
        return "module-result"

    def findall(
        self,
        pattern: object,
        haystack: object,
        flags: int = 0,
    ) -> object:
        self.calls.append(("module.findall", pattern, haystack, flags))
        self._maybe_raise_helper_exception()
        return "module-result"

    def finditer(
        self,
        pattern: object,
        haystack: object,
        flags: int = 0,
    ) -> object:
        self.calls.append(("module.finditer", pattern, haystack, flags))
        self._maybe_raise_helper_exception()
        return iter(["module-finditer-result"])

    def sub(
        self,
        pattern: object,
        repl: object,
        string: object,
        *args: object,
        **kwargs: object,
    ) -> object:
        count = args[0] if args else 0
        flags = args[1] if len(args) > 1 else 0
        self.calls.append(("module.sub", pattern, repl, string, count, flags, kwargs))
        self._maybe_raise_helper_exception()
        return "module-result"

    def subn(
        self,
        pattern: object,
        repl: object,
        string: object,
        *args: object,
        **kwargs: object,
    ) -> object:
        count = args[0] if args else 0
        flags = args[1] if len(args) > 1 else 0
        self.calls.append(("module.subn", pattern, repl, string, count, flags, kwargs))
        self._maybe_raise_helper_exception()
        return ("module-result", 0)


def _resolve_live_manifest_path(
    manifest_path: pathlib.Path | str,
) -> pathlib.Path:
    if isinstance(manifest_path, pathlib.Path):
        return manifest_path
    return benchmarks.BENCHMARK_WORKLOADS_ROOT / manifest_path


@cache
def manifest_workloads(
    manifest_path: pathlib.Path | str,
) -> tuple[benchmarks.Workload, ...]:
    return tuple(load_manifest(_resolve_live_manifest_path(manifest_path)).workloads)


def selected_manifest_workloads(
    manifest_path: pathlib.Path | str,
    *,
    include_workload: Any | None = None,
) -> tuple[benchmarks.Workload, ...]:
    workloads = manifest_workloads(manifest_path)
    if include_workload is None:
        return workloads
    return tuple(workload for workload in workloads if include_workload(workload))


@cache
def _live_manifest_workloads_by_id(
    manifest_path: pathlib.Path | str,
) -> dict[str, benchmarks.Workload]:
    return {
        workload.workload_id: workload
        for workload in manifest_workloads(manifest_path)
    }


def live_manifest_workload(
    manifest_path: pathlib.Path | str,
    workload_id: str,
) -> benchmarks.Workload:
    return _live_manifest_workloads_by_id(manifest_path)[workload_id]


def live_manifest_workloads(
    manifest_path: pathlib.Path | str,
    workload_ids: tuple[str, ...],
) -> tuple[benchmarks.Workload, ...]:
    workloads_by_id = _live_manifest_workloads_by_id(manifest_path)
    return tuple(workloads_by_id[workload_id] for workload_id in workload_ids)


_KNOWN_GAP_STATUSES = frozenset({"known-gap", "unimplemented"})


def _assert_benchmark_summary_consistent(
    testcase: Any,
    scorecard: dict[str, Any],
    summary: dict[str, Any],
) -> None:
    workloads = scorecard["workloads"]
    expected_summary = {
        key: scorecard["summary"][key]
        for key in (
            "known_gap_count",
            "measured_workloads",
            "module_workloads",
            "parser_workloads",
            "regression_workloads",
            "total_workloads",
        )
    }
    testcase.assertEqual(summary, expected_summary)
    testcase.assertEqual(summary["total_workloads"], len(workloads))
    testcase.assertEqual(
        summary["measured_workloads"] + summary["known_gap_count"],
        summary["total_workloads"],
    )
    testcase.assertEqual(
        summary["parser_workloads"],
        scorecard["families"]["parser"]["workload_count"],
    )
    testcase.assertEqual(
        summary["module_workloads"],
        scorecard["families"]["module"]["workload_count"],
    )
    testcase.assertEqual(
        summary["regression_workloads"],
        sum(1 for workload in workloads if workload["manifest_id"] == "regression-matrix"),
    )

    for cache_mode, expected_count in scorecard["summary"]["workloads_by_cache_mode"].items():
        testcase.assertEqual(
            expected_count,
            sum(1 for workload in workloads if workload["cache_mode"] == cache_mode),
        )

    if summary["measured_workloads"] > 0:
        testcase.assertIsInstance(scorecard["summary"]["baseline_median_ns"], int)
        testcase.assertGreater(scorecard["summary"]["baseline_median_ns"], 0)
        testcase.assertGreater(scorecard["summary"]["baseline_median_ops_per_second"], 0)
        testcase.assertIsInstance(scorecard["summary"]["implementation_median_ns"], int)
        testcase.assertGreater(scorecard["summary"]["implementation_median_ns"], 0)
        testcase.assertGreater(
            scorecard["summary"]["implementation_median_ops_per_second"],
            0,
        )

    for family_id, family_summary in scorecard["families"].items():
        family_workloads = [workload for workload in workloads if workload["family"] == family_id]
        testcase.assertEqual(family_summary["workload_count"], len(family_workloads))
        testcase.assertEqual(
            family_summary["known_gap_count"],
            sum(
                1
                for workload in family_workloads
                if workload["status"] in _KNOWN_GAP_STATUSES
            ),
        )
        for cache_mode, cache_summary in family_summary["cache_modes"].items():
            testcase.assertEqual(
                cache_summary["workload_count"],
                sum(
                    1
                    for workload in family_workloads
                    if workload["cache_mode"] == cache_mode
                ),
            )

    for cache_mode, cache_summary in scorecard["cache_modes"].items():
        cache_workloads = [workload for workload in workloads if workload["cache_mode"] == cache_mode]
        testcase.assertEqual(cache_summary["workload_count"], len(cache_workloads))
        testcase.assertEqual(
            cache_summary["known_gap_count"],
            sum(1 for workload in cache_workloads if workload["status"] in _KNOWN_GAP_STATUSES),
        )


def _artifact_manifest_record(
    manifest_path: str,
    manifest: BenchmarkManifest,
) -> dict[str, Any]:
    return {
        "manifest": manifest_path,
        "manifest_id": manifest.manifest_id,
        "manifest_schema_version": manifest.schema_version,
        "workload_count": len(manifest.workloads),
        "smoke_workload_ids": manifest.smoke_workload_ids(),
        "spec_refs": list(manifest.spec_refs),
    }


def assert_benchmark_manifest_contract(
    testcase: Any,
    manifest_summary: dict[str, Any],
    manifest_record: dict[str, Any],
    *,
    manifest: BenchmarkManifest,
    manifest_path: str,
    known_gap_count: int,
    selection_mode: str = "full",
    selected_workload_ids: tuple[str, ...] | None = None,
) -> None:
    workloads = list(manifest.workloads)
    selected_workloads = manifest.selected_workloads(
        selected_workload_ids=selected_workload_ids
    )
    smoke_ids = manifest.smoke_workload_ids()
    operations = sorted({workload.operation for workload in selected_workloads})
    families = sorted({workload.family for workload in selected_workloads})

    testcase.assertEqual(manifest_summary["workload_count"], len(workloads))
    testcase.assertEqual(manifest_summary["selected_workload_count"], len(selected_workloads))
    testcase.assertEqual(
        manifest_summary["measured_workloads"],
        len(selected_workloads) - known_gap_count,
    )
    testcase.assertEqual(manifest_summary["known_gap_count"], known_gap_count)
    testcase.assertEqual(
        manifest_summary["readiness"],
        "measured" if known_gap_count == 0 else "partial",
    )
    testcase.assertEqual(manifest_summary["selection_mode"], selection_mode)
    testcase.assertEqual(manifest_summary["available_smoke_workload_count"], len(smoke_ids))
    testcase.assertEqual(manifest_summary["smoke_workload_ids"], smoke_ids)
    testcase.assertEqual(manifest_summary["families"], families)
    testcase.assertEqual(manifest_summary["operations"], operations)
    testcase.assertEqual(manifest_summary["spec_refs"], manifest.spec_refs)
    if manifest.notes:
        testcase.assertEqual(manifest_summary["notes"], manifest.notes)

    testcase.assertEqual(manifest_record["manifest_id"], manifest.manifest_id)
    testcase.assertEqual(manifest_record["manifest"], manifest_path)
    testcase.assertEqual(manifest_record["smoke_workload_ids"], smoke_ids)


def find_manifest_record(scorecard: dict[str, Any], manifest_id: str) -> dict[str, Any]:
    for manifest_record in scorecard["artifacts"]["manifests"]:
        if str(manifest_record["manifest_id"]) == manifest_id:
            return manifest_record
    raise AssertionError(f"missing manifest record for {manifest_id!r}")


@cache
def published_case_ids_by_signature(
    case_signature: Callable[[Any], tuple[Any, ...] | None],
) -> dict[tuple[Any, ...], tuple[str, ...]]:
    case_ids_by_signature: dict[tuple[Any, ...], list[str]] = {}

    for case in published_cases_by_id().values():
        signature = case_signature(case)
        if signature is None:
            continue
        case_ids_by_signature.setdefault(signature, []).append(case.case_id)

    return {
        signature: tuple(sorted(case_ids))
        for signature, case_ids in case_ids_by_signature.items()
    }


@cache
def published_cases_by_id() -> dict[str, Any]:
    return records_by_string_id(
        (
            case
            for manifest in published_fixture_manifests()
            for case in manifest.cases
        ),
        id_attr="case_id",
        duplicate_error=lambda duplicate_ids: AssertionError(
            f"duplicate published correctness case id {duplicate_ids[0]!r}"
        ),
    )


def _clear_cached_functions(functions: Iterable[object]) -> None:
    for function in functions:
        cache_clear = getattr(function, "cache_clear", None)
        if callable(cache_clear):
            cache_clear()


def _clear_anchor_support_caches() -> None:
    _clear_cached_functions(
        (
            manifest_workloads,
            _live_manifest_workloads_by_id,
            _collection_replacement_anchor_support,
            published_case_ids_by_signature,
            published_cases_by_id,
            _parsed_module_ast,
        )
    )
    source_tree_support = sys.modules.get(
        "tests.benchmarks.source_tree_benchmark_anchor_support"
    )
    if source_tree_support is not None:
        _clear_cached_functions(vars(source_tree_support).values())
    collection_replacement_support = sys.modules.get(
        "tests.benchmarks.collection_replacement_benchmark_anchor_support"
    )
    if collection_replacement_support is not None:
        _clear_cached_functions(vars(collection_replacement_support).values())


@pytest.fixture
def anchor_support_cache_guard() -> None:
    _clear_anchor_support_caches()
    yield
    _clear_anchor_support_caches()


def _synthetic_manifest(
    *,
    cases: tuple[object, ...] = (),
    workloads: tuple[object, ...] = (),
) -> SimpleNamespace:
    return SimpleNamespace(cases=list(cases), workloads=list(workloads))


@cache
def _collection_replacement_anchor_support() -> object:
    return importlib.import_module(
        "tests.benchmarks.collection_replacement_benchmark_anchor_support"
    )


def _contract_source_workloads(
    *,
    manifest_path: pathlib.Path,
    include_workload_selectors: tuple[Callable[[Any], bool], ...],
    expected_source_workload_ids: tuple[str, ...],
    drift_message: str,
) -> tuple[Workload, ...]:
    source_workloads = tuple(
        workload
        for include_workload in include_workload_selectors
        for workload in selected_manifest_workloads(
            manifest_path,
            include_workload=include_workload,
        )
    )
    if (
        tuple(workload.workload_id for workload in source_workloads)
        != expected_source_workload_ids
    ):
        raise AssertionError(drift_message)
    return source_workloads


COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS = frozenset(
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

COMPILED_PATTERN_MODULE_SUCCESS_CONTRACT_EXCLUDED_FIELDS = (
    COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS
    | {
        "categories",
        "syntax_features",
        "expected_exception",
        "haystack_text_model",
    }
)

COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_PAYLOAD_DROP_FIELDS = frozenset(
    {
        "manifest_id",
        "workload_id",
        "warmup_iterations",
        "sample_iterations",
        "timed_samples",
        "notes",
        "smoke",
        "categories",
        "syntax_features",
        "haystack_text_model",
    }
)


def compiled_pattern_contract_expected_build_calls(
    source_workload: Workload,
    *,
    label: str,
) -> list[tuple[object, ...]]:
    compile_call = ("compile", source_workload.pattern_payload(), source_workload.flags)
    if source_workload.cache_mode == "purged":
        return [compile_call, ("purge",)]
    if source_workload.cache_mode == "warm":
        return [compile_call]
    raise AssertionError(
        f"unexpected compiled-pattern {label} workload cache mode "
        f"{source_workload.cache_mode!r}"
    )


def _synthetic_case(
    case_id: str,
    signature: tuple[Any, ...] | None,
) -> SimpleNamespace:
    return SimpleNamespace(case_id=case_id, signature=signature)


def _synthetic_workload(
    workload_id: str,
    signature: tuple[Any, ...],
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
    workloads: tuple[Any, ...],
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


def _synthetic_workload_signature(workload: Any) -> tuple[Any, ...]:
    return workload.signature


def _synthetic_workload_is_included(workload: Any) -> bool:
    return workload.include


def _definition_anchor_expectations(
    manifest_path: pathlib.Path,
    anchor_expectations: dict[str, tuple[str, ...]],
) -> dict[tuple[str, str], tuple[str, ...]]:
    return {
        (manifest_path.name, workload_id): case_ids
        for workload_id, case_ids in anchor_expectations.items()
    }


def _workload_case_pair_anchor_expectations(
    manifest_path: pathlib.Path,
    workload_case_pairs: tuple[tuple[str, str], ...],
) -> dict[tuple[str, str], tuple[str, ...]]:
    return _definition_anchor_expectations(
        manifest_path,
        {
            workload_id: (case_id,)
            for workload_id, case_id in workload_case_pairs
        },
    )


def freeze_signature_value(value: Any) -> Any:
    if isinstance(value, dict):
        return tuple(
            (str(key), freeze_signature_value(nested_value))
            for key, nested_value in sorted(value.items())
        )
    if isinstance(value, list):
        return tuple(freeze_signature_value(item) for item in value)
    return value


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
    alias_names = {
        alias.asname or alias.name
        for node in module_body
        if isinstance(node, ast.ImportFrom)
        and node.module == import_from_module
        for alias in node.names
        if alias.name == import_name
    } | {
        alias.asname or alias.name.rsplit(".", 1)[-1]
        for node in module_body
        if isinstance(node, ast.Import)
        for alias in node.names
        if alias.name == dotted_import_name
    }

    changed = True
    while changed:
        changed = False
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

            if not isinstance(value, ast.Name) or value.id not in alias_names:
                continue

            for target in targets:
                if target not in alias_names:
                    alias_names.add(target)
                    changed = True

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
        assert all(
            isinstance(manifest_path, ast.Name)
            for manifest_path in manifest_paths_keyword.value.elts
        )
        manifest_path_names.append(
            tuple(
                manifest_path.id
                for manifest_path in manifest_paths_keyword.value.elts
            )
        )

    return tuple(manifest_path_names)


def assert_pattern_helper_wrong_text_model_payload_round_trip(
    source_workload: Workload,
    payload: dict[str, object],
    round_tripped: Workload,
    *,
    expect_replacement_payload: bool = False,
) -> None:
    expected_text_type = str if source_workload.text_model == "str" else bytes
    expected_haystack_type = (
        str if source_workload.haystack_text_model == "str" else bytes
    )

    assert payload.get("use_compiled_pattern") is None
    assert round_tripped.use_compiled_pattern is False
    assert payload["timing_scope"] == "pattern-helper-call"
    assert round_tripped.timing_scope == "pattern-helper-call"
    assert payload["haystack_text_model"] == source_workload.haystack_text_model
    assert round_tripped.haystack_text_model == source_workload.haystack_text_model
    assert payload["expected_exception"] == source_workload.expected_exception
    assert round_tripped.expected_exception == source_workload.expected_exception
    assert isinstance(round_tripped.pattern_payload(), expected_text_type)
    assert isinstance(round_tripped.haystack_payload(), expected_haystack_type)
    if expect_replacement_payload:
        assert isinstance(round_tripped.replacement_payload(), expected_text_type)


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
    definition_names: Iterable[str] = (),
    assignment_names: Iterable[str] = (),
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
    local_function_names: Iterable[str] = (),
    local_assignment_names: Iterable[str] = (),
    support_alias_assignment_names: Iterable[str] = (),
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
    shared_module = sys.modules[__name__]
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
        assert getattr(caller_module, assignment_name) is getattr(
            shared_module,
            assignment_name,
        )


def compile_proxy_correctness_case_signature(
    case: Any,
) -> tuple[str, str | bytes, tuple[()], tuple[()], int, str] | None:
    if case.operation != "compile":
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
    workload: Any,
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


def is_compile_proxy_workload(workload: Any) -> bool:
    return workload.operation in {"compile", "module.compile"}


COMPILE_MATRIX_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "compile_matrix.py"
REGRESSION_MATRIX_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "regression_matrix.py"
)


COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS = (
    StandardBenchmarkAnchorContractDefinition(
        name="compile-proxy",
        manifest_paths=(
            COMPILE_MATRIX_MANIFEST_PATH,
            REGRESSION_MATRIX_MANIFEST_PATH,
        ),
        expected_anchor_case_ids=(
            _definition_anchor_expectations(
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
            | _definition_anchor_expectations(
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
        ),
        include_workload=is_compile_proxy_workload,
        correctness_case_signature=compile_proxy_correctness_case_signature,
        workload_signature=compile_proxy_workload_signature,
    ),
)

MODULE_BOUNDARY_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "module_boundary.py"
)
CONDITIONAL_GROUP_EXISTS_BOUNDARY_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "conditional_group_exists_boundary.py"
)
OPTIONAL_GROUP_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "optional_group_boundary.py"
)
NESTED_GROUP_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "nested_group_boundary.py"
)
EXACT_REPEAT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "exact_repeat_quantified_group_boundary.py"
)
RANGED_REPEAT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "ranged_repeat_quantified_group_boundary.py"
)
GROUPED_ALTERNATION_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_alternation_boundary.py"
)
GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "grouped_alternation_replacement_boundary.py"
)
NESTED_GROUP_REPLACEMENT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "nested_group_replacement_boundary.py"
)
NESTED_GROUP_CALLABLE_REPLACEMENT_BOUNDARY_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "nested_group_callable_replacement_boundary.py"
)
OPEN_ENDED_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "open_ended_quantified_group_boundary.py"
)


@dataclass(frozen=True, slots=True)
class AnchoredWorkloadCasePair:
    manifest_name: str
    workload_id: str
    case_id: str
    workload: Any
    case: Any


def _module_workflow_keyword_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or not case.kwargs:
        return None
    if case.use_compiled_pattern or case.helper not in {"search", "match", "fullmatch"}:
        return None
    return (
        f"module.{case.helper}",
        case_pattern(case),
        freeze_signature_value(list(case.args)),
        module_workflow_keyword_kwargs_signature(case.kwargs),
        case.flags or 0,
        case.text_model or "str",
    )


def _is_module_workflow_keyword_flags_workload(workload: Any) -> bool:
    keyword_names = tuple(workload.kwargs)
    return (
        workload.operation in {"module.search", "module.match", "module.fullmatch"}
        and bool(workload.kwargs)
        and len(keyword_names) == 1
        and keyword_names[0] == "flags"
        and workload.expected_exception is None
        and not workload.use_compiled_pattern
    )


def _is_module_workflow_keyword_error_workload(workload: Any) -> bool:
    keyword_names = tuple(workload.kwargs)
    expected_exception = workload.expected_exception
    if (
        workload.operation
        not in {"module.search", "module.match", "module.fullmatch"}
        or not workload.kwargs
        or len(keyword_names) != 1
        or expected_exception is None
        or expected_exception.get("type") != "TypeError"
        or workload.use_compiled_pattern
    ):
        return False
    message = expected_exception.get("message_substring", "")
    if keyword_names[0] == "flags":
        return "multiple values for argument" in message
    if keyword_names[0] == "missing":
        return "unexpected keyword argument" in message
    return False


def _is_encoded_indexlike_payload(value: object) -> bool:
    return (
        isinstance(value, dict)
        and value.get("type") == "indexlike"
        and isinstance(value.get("value"), int)
        and not isinstance(value.get("value"), bool)
    )

def _is_collection_replacement_wrong_text_model_workload(workload: Any) -> bool:
    return (
        getattr(workload, "haystack_text_model", None) is not None
        and not workload.kwargs
        and workload.use_compiled_pattern
        and workload.operation
        in {
            "module.split",
            "module.findall",
            "module.finditer",
            "module.sub",
            "module.subn",
        }
        and workload.expected_exception is not None
        and workload.expected_exception.get("type") == "TypeError"
    )


def _module_workflow_keyword_workload_args(
    workload: Any,
) -> tuple[Any, ...]:
    if not (
        _is_module_workflow_keyword_flags_workload(workload)
        or _is_module_workflow_keyword_error_workload(workload)
    ):
        raise AssertionError(
            "unexpected module-workflow keyword workload "
            f"{workload.workload_id!r}"
        )
    args: list[object] = [workload.haystack_payload()]
    if (
        workload.operation == "module.search"
        and workload.expected_exception is not None
        and "flags" in workload.kwargs
    ):
        args.append(workload.flags)
    return tuple(args)


def _module_workflow_keyword_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not (
        _is_module_workflow_keyword_flags_workload(workload)
        or _is_module_workflow_keyword_error_workload(workload)
    ):
        raise AssertionError(
            "unexpected module-workflow keyword workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        freeze_signature_value(list(_module_workflow_keyword_workload_args(workload))),
        module_workflow_keyword_kwargs_signature(workload.kwargs),
        workload.flags,
        workload.text_model,
    )


MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS = (
    StandardBenchmarkAnchorContractDefinition(
        name="module-workflow-keyword-flags",
        manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            MODULE_BOUNDARY_MANIFEST_PATH,
            {
                "module-search-flags-keyword-warm-str": (
                    "workflow-module-search-flags-keyword-str",
                ),
                "module-match-flags-keyword-purged-bytes": (
                    "workflow-module-match-flags-keyword-bytes",
                ),
                "module-fullmatch-flags-keyword-warm-str": (
                    "workflow-module-fullmatch-flags-keyword-str",
                ),
            },
        ),
        include_workload=_is_module_workflow_keyword_flags_workload,
        correctness_case_signature=_module_workflow_keyword_correctness_case_signature,
        workload_signature=_module_workflow_keyword_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="module-workflow-keyword-errors",
        manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            MODULE_BOUNDARY_MANIFEST_PATH,
            {
                "module-search-duplicate-flags-keyword-warm-str": (
                    "workflow-module-search-duplicate-flags-keyword",
                ),
                "module-fullmatch-unexpected-keyword-purged-str": (
                    "workflow-module-fullmatch-unexpected-keyword",
                ),
            },
        ),
        include_workload=_is_module_workflow_keyword_error_workload,
        correctness_case_signature=_module_workflow_keyword_correctness_case_signature,
        workload_signature=_module_workflow_keyword_workload_signature,
    ),
)


def _compiled_pattern_module_compile_keyword_kwargs_signature(
    kwargs: dict[str, object],
) -> tuple[tuple[str, str, object], ...]:
    signature: list[tuple[str, str, object]] = []
    for name, value in sorted(kwargs.items()):
        if isinstance(value, bool):
            signature.append((name, "bool", value))
            continue
        if isinstance(value, re.RegexFlag) and int(value) == 0:
            signature.append((name, "noflag", 0))
            continue
        if isinstance(value, int):
            signature.append((name, "int", int(value)))
            continue
        signature.append((name, type(value).__name__, repr(value)))
    return tuple(signature)


def _module_workflow_compiled_pattern_compile_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or case.kwargs or not case.use_compiled_pattern:
        return None
    if case.helper != "compile" or case.args:
        return None
    case_text_model = case.text_model or "str"
    return (
        "module.compile",
        case_pattern(case),
        (),
        case.use_compiled_pattern,
        case.flags or 0,
        case_text_model,
    )


def _module_workflow_compiled_pattern_compile_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_module_workflow_compiled_pattern_compile_workload(workload):
        raise AssertionError(
            "unexpected module-workflow compiled-pattern module.compile workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        (),
        workload.use_compiled_pattern,
        workload.flags,
        workload.text_model,
    )


def _is_module_workflow_compiled_pattern_compile_workload(workload: Any) -> bool:
    return (
        not workload.kwargs
        and workload.use_compiled_pattern
        and workload.operation == "module.compile"
    )


def _is_module_workflow_compiled_pattern_compile_success_workload(
    workload: Any,
    *,
    allowed_patterns: tuple[str, ...],
) -> bool:
    return (
        _is_module_workflow_compiled_pattern_compile_workload(workload)
        and workload.expected_exception is None
        and workload.pattern in allowed_patterns
        and workload.flags == 0
    )


def _workload_matches_expected_exception(
    workload: Any,
    *,
    expected_exception: dict[str, str] | None,
) -> bool:
    if expected_exception is None:
        return workload.expected_exception is None
    return workload.expected_exception == expected_exception


def _module_workflow_compiled_pattern_compile_keyword_correctness_case_signature(
    case: Any,
    *,
    keyword_signature: tuple[tuple[str, str, object], ...],
    allowed_patterns: tuple[str, ...],
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or not case.use_compiled_pattern:
        return None
    if case.helper != "compile" or case.args:
        return None
    if (
        _compiled_pattern_module_compile_keyword_kwargs_signature(case.kwargs)
        != keyword_signature
    ):
        return None
    if case.pattern not in allowed_patterns:
        return None
    case_text_model = case.text_model or "str"
    return (
        "module.compile",
        case_pattern(case),
        (),
        keyword_signature,
        case.use_compiled_pattern,
        case.flags or 0,
        case_text_model,
    )


def _module_workflow_compiled_pattern_compile_keyword_workload_signature(
    workload: Any,
    *,
    keyword_label: str,
    keyword_signature: tuple[tuple[str, str, object], ...],
    allowed_patterns: tuple[str, ...],
    expected_exception: dict[str, str] | None = None,
) -> tuple[Any, ...]:
    if not _is_module_workflow_compiled_pattern_compile_keyword_workload(
        workload,
        keyword_signature=keyword_signature,
        allowed_patterns=allowed_patterns,
        expected_exception=expected_exception,
    ):
        raise AssertionError(
            "unexpected module-workflow compiled-pattern module.compile "
            f"{keyword_label} keyword workload {workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        (),
        keyword_signature,
        workload.use_compiled_pattern,
        workload.flags,
        workload.text_model,
    )


def _is_module_workflow_compiled_pattern_compile_keyword_workload(
    workload: Any,
    *,
    keyword_signature: tuple[tuple[str, str, object], ...],
    allowed_patterns: tuple[str, ...],
    expected_exception: dict[str, str] | None = None,
) -> bool:
    return (
        workload.use_compiled_pattern
        and workload.operation == "module.compile"
        and _workload_matches_expected_exception(
            workload,
            expected_exception=expected_exception,
        )
        and workload.pattern in allowed_patterns
        and workload.flags == 0
        and _compiled_pattern_module_compile_keyword_kwargs_signature(workload.kwargs)
        == keyword_signature
    )


def _assert_compiled_pattern_module_compile_contract_payload_round_trip_common(
    source_workload: Workload,
    payload: dict[str, object],
    round_tripped: Workload,
) -> None:
    expected_text_type = str if source_workload.text_model == "str" else bytes

    assert payload["use_compiled_pattern"] is True
    assert round_tripped.use_compiled_pattern is True
    assert payload["flags"] == source_workload.flags
    assert round_tripped.flags == source_workload.flags
    assert payload.get("expected_exception") == source_workload.expected_exception
    assert round_tripped.expected_exception == source_workload.expected_exception
    assert isinstance(round_tripped.pattern_payload(), expected_text_type)


def _assert_compiled_pattern_module_compile_success_payload_round_trip(
    contract_case: Any,
    source_workload: Workload,
    payload: dict[str, object],
    round_tripped: Workload,
) -> None:
    del contract_case
    _assert_compiled_pattern_module_compile_contract_payload_round_trip_common(
        source_workload,
        payload,
        round_tripped,
    )
    assert payload.get("haystack_text_model") == source_workload.haystack_text_model
    assert round_tripped.haystack_text_model == source_workload.haystack_text_model


def _assert_compiled_pattern_module_compile_keyword_payload_round_trip(
    contract_case: Any,
    source_workload: Workload,
    payload: dict[str, object],
    round_tripped: Workload,
) -> None:
    del contract_case
    _assert_compiled_pattern_module_compile_contract_payload_round_trip_common(
        source_workload,
        payload,
        round_tripped,
    )
    expected_keyword_value = source_workload.keyword_arguments()["flags"]

    assert payload["kwargs"] == source_workload.kwargs
    assert round_tripped.kwargs == source_workload.kwargs
    assert type(payload["kwargs"]["flags"]) is type(expected_keyword_value)
    assert type(round_tripped.kwargs["flags"]) is type(expected_keyword_value)
    assert payload.get("haystack_text_model") is None
    assert round_tripped.haystack_text_model is None


def anchored_workload_case_ids(
    manifest_path: pathlib.Path,
    *,
    anchor_case_ids: dict[tuple[Any, ...], tuple[str, ...]],
    workload_signature: Callable[[Any], tuple[Any, ...]],
    include_workload: Callable[[Any], bool] | None = None,
) -> dict[tuple[str, str], tuple[str, ...]]:
    workloads = selected_manifest_workloads(
        manifest_path,
        include_workload=include_workload,
    )

    return {
        (manifest_path.name, workload.workload_id): anchor_case_ids.get(
            workload_signature(workload),
            (),
        )
        for workload in workloads
    }


def unanchored_workload_ids(
    manifest_path: pathlib.Path,
    *,
    anchor_case_ids: dict[tuple[Any, ...], tuple[str, ...]],
    workload_signature: Callable[[Any], tuple[Any, ...]],
    include_workload: Callable[[Any], bool] | None = None,
) -> tuple[str, ...]:
    workloads = selected_manifest_workloads(
        manifest_path,
        include_workload=include_workload,
    )

    return tuple(
        workload.workload_id
        for workload in workloads
        if workload_signature(workload) not in anchor_case_ids
    )


def expected_anchored_workload_case_pairs(
    manifest_path: pathlib.Path,
    *,
    expected_anchor_case_ids: dict[tuple[str, str], tuple[str, ...]],
    include_workload: Callable[[Any], bool] | None = None,
) -> tuple[AnchoredWorkloadCasePair, ...]:
    manifest_name = manifest_path.name
    workloads_by_id = records_by_string_id(
        selected_manifest_workloads(
            manifest_path,
            include_workload=include_workload,
        ),
        id_attr="workload_id",
    )
    published_cases = published_cases_by_id()
    anchored_pairs: list[AnchoredWorkloadCasePair] = []

    for (expected_manifest_name, workload_id), case_ids in expected_anchor_case_ids.items():
        if expected_manifest_name != manifest_name:
            raise AssertionError(
                f"expected anchored manifest {expected_manifest_name!r} "
                f"does not match {manifest_name!r}"
            )
        if len(case_ids) != 1:
            raise AssertionError(
                "expected exactly one published correctness case for "
                f"{(expected_manifest_name, workload_id)!r}, got {case_ids!r}"
            )

        case_id = case_ids[0]
        if workload_id not in workloads_by_id:
            raise AssertionError(
                f"expected anchored workload {workload_id!r} to be in scope for "
                f"{manifest_name!r}"
            )
        if case_id not in published_cases:
            raise AssertionError(
                f"expected anchored correctness case {case_id!r} to be published"
            )

        anchored_pairs.append(
            AnchoredWorkloadCasePair(
                manifest_name=manifest_name,
                workload_id=workload_id,
                case_id=case_id,
                workload=workloads_by_id[workload_id],
                case=published_cases[case_id],
            )
        )

    return tuple(anchored_pairs)


def run_benchmark_workload_with_cpython(workload: Any) -> object:
    re.purge()
    callback = benchmarks.build_callable(re, "re", workload)
    result = callback()
    re.purge()
    return result


def run_correctness_case_with_cpython(case: Any) -> object:
    if case.operation == "compile":
        return re.compile(case.pattern_payload(), case.flags or 0)

    if case.operation == "module_call":
        if case.helper is None:
            raise AssertionError(f"expected helper for {case.case_id!r}")
        compiled_pattern = None
        if case.use_compiled_pattern:
            compiled_pattern = re.compile(case.pattern_payload(), case.flags or 0)
        if not case.use_compiled_pattern and not case.include_pattern_arg:
            if case.pattern is None:
                return getattr(re, case.helper)(
                    *case.args,
                    **case.kwargs,
                )
            return getattr(re, case.helper)(
                case.pattern_payload(),
                *case.args,
                **case.kwargs,
            )
        return getattr(re, case.helper)(
            *case.module_call_args(compiled_pattern),
            **case.kwargs,
        )

    if case.operation == "pattern_call":
        if case.helper is None:
            raise AssertionError(f"expected helper for {case.case_id!r}")
        compiled = re.compile(case.pattern_payload(), case.flags or 0)
        return getattr(compiled, case.helper)(*case.args, **case.kwargs)

    raise AssertionError(f"unexpected correctness operation {case.operation!r}")


def assert_benchmark_workload_matches_expected_result(
    workload: Any,
    expected: object,
) -> None:
    observed = run_benchmark_workload_with_cpython(workload)

    if workload.operation == "module.compile":
        assert_pattern_parity("stdlib", observed, expected)
        return

    if workload.operation in {
        "module.search",
        "module.match",
        "module.fullmatch",
        "pattern.search",
        "pattern.match",
        "pattern.fullmatch",
    }:
        assert_match_result_parity(
            "stdlib",
            observed,
            expected,
            check_regs=True,
        )
        return

    if workload.operation in {
        "module.split",
        "module.findall",
        "pattern.findall",
        "module.sub",
        "module.subn",
        "pattern.split",
        "pattern.sub",
        "pattern.subn",
    }:
        assert observed == expected
        return

    if workload.operation in {"module.finditer", "pattern.finditer"}:
        assert isinstance(observed, list)
        expected_matches = list(expected)
        assert len(observed) == len(expected_matches)
        for observed_match, expected_match in zip(
            observed,
            expected_matches,
            strict=True,
        ):
            assert_match_result_parity(
                "stdlib",
                observed_match,
                expected_match,
                check_regs=True,
            )
        return

    raise AssertionError(
        "unexpected anchored benchmark workload operation "
        f"{workload.operation!r}"
    )


def assert_anchored_workload_case_result_parity(
    anchored_pairs: Iterable[AnchoredWorkloadCasePair],
) -> None:
    for anchored_pair in anchored_pairs:
        try:
            expected = run_correctness_case_with_cpython(anchored_pair.case)
        except Exception as expected_exc:
            with pytest.raises(type(expected_exc)) as observed_exc:
                run_benchmark_workload_with_cpython(anchored_pair.workload)
            assert str(observed_exc.value) == str(expected_exc)
            continue
        assert_benchmark_workload_matches_expected_result(
            anchored_pair.workload,
            expected,
        )


def manifest_workload_ids_matching(
    manifest: BenchmarkManifest,
    include_workload: Any,
    *,
    operation_prefix: str | None = None,
) -> tuple[str, ...]:
    return tuple(
        workload.workload_id
        for workload in manifest.workloads
        if include_workload(workload)
        and (
            operation_prefix is None
            or workload.operation.startswith(operation_prefix)
        )
    )


def find_workload_record(scorecard: dict[str, Any], workload_id: str) -> dict[str, Any]:
    for workload in scorecard["workloads"]:
        if str(workload["id"]) == workload_id:
            return workload
    raise AssertionError(f"missing workload record for {workload_id!r}")


def find_workload_document(
    manifest: BenchmarkManifest,
    workload_id: str,
) -> Workload:
    for workload in manifest.workloads:
        if workload.workload_id == workload_id:
            return workload
    raise AssertionError(
        f"missing workload definition {workload_id!r} in {manifest.manifest_id!r}"
    )


def assert_manifest_workload_contracts(
    testcase: Any,
    manifest: BenchmarkManifest,
    scorecard: dict[str, Any],
    workload_expectations: Iterable[tuple[str, str]],
    *,
    subtest_label: str | None = None,
) -> None:
    manifest_id = manifest.manifest_id
    for workload_id, expected_status in workload_expectations:
        if subtest_label is None:
            assert_benchmark_workload_contract(
                testcase,
                find_workload_record(scorecard, workload_id),
                manifest_id=manifest_id,
                workload_document=find_workload_document(manifest, workload_id),
                expected_status=expected_status,
            )
            continue

        with testcase.subTest(**{subtest_label: workload_id}):
            assert_benchmark_workload_contract(
                testcase,
                find_workload_record(scorecard, workload_id),
                manifest_id=manifest_id,
                workload_document=find_workload_document(manifest, workload_id),
                expected_status=expected_status,
            )


def assert_zero_gap_manifest_workloads_measured(
    *,
    manifest_path: pathlib.Path | str,
    manifest_id: str,
    expected_measured_workload_ids: tuple[str, ...],
    expected_measured_workload_count: int,
    expected_total_workload_count: int | None = None,
) -> None:
    from tests.conftest import run_harness_scorecard

    testcase = unittest.TestCase()
    manifest = load_manifest(_resolve_live_manifest_path(manifest_path))
    _, scorecard = run_harness_scorecard(
        "rebar_harness.benchmarks",
        ["--manifest", str(_resolve_live_manifest_path(manifest_path))],
        report_name="benchmarks.json",
    )
    manifest_summary = scorecard["manifests"][manifest_id]

    testcase.assertEqual(manifest_summary["known_gap_count"], 0)
    testcase.assertEqual(
        manifest_summary["measured_workloads"],
        expected_measured_workload_count,
    )
    if expected_total_workload_count is not None:
        testcase.assertEqual(
            manifest_summary["workload_count"],
            expected_total_workload_count,
        )

    subtest_label: str | None = None
    if expected_total_workload_count is not None:
        subtest_label = "measured_workload_id"
    elif len(expected_measured_workload_ids) > 1:
        subtest_label = "workload_id"

    assert_manifest_workload_contracts(
        testcase,
        manifest,
        scorecard,
        (
            (workload_id, "measured")
            for workload_id in expected_measured_workload_ids
        ),
        subtest_label=subtest_label,
    )


def assert_benchmark_workload_contract(
    testcase: Any,
    workload_record: dict[str, Any],
    *,
    manifest_id: str,
    workload_document: Workload,
    expected_status: str,
) -> None:
    workload_payload = workload_to_payload(workload_document)
    expected_syntax_features = workload_payload.get(
        "syntax_features",
        workload_payload.get("categories", []),
    )
    testcase.assertEqual(workload_record["manifest_id"], manifest_id)
    testcase.assertEqual(
        workload_record["family"],
        workload_payload.get("family", "parser"),
    )
    testcase.assertEqual(workload_record["operation"], workload_payload["operation"])
    testcase.assertEqual(workload_record["pattern"], workload_payload.get("pattern", ""))
    testcase.assertEqual(workload_record["haystack"], workload_payload.get("haystack"))
    testcase.assertEqual(
        workload_record["replacement"],
        workload_payload.get("replacement"),
    )
    testcase.assertEqual(workload_record["flags"], workload_payload.get("flags", 0))
    testcase.assertEqual(workload_record["count"], workload_payload.get("count", 0))
    testcase.assertEqual(
        workload_record["maxsplit"],
        workload_payload.get("maxsplit", 0),
    )
    testcase.assertEqual(
        workload_record.get("pos"),
        workload_payload.get("pos"),
    )
    testcase.assertEqual(
        workload_record.get("endpos"),
        workload_payload.get("endpos"),
    )
    testcase.assertEqual(
        workload_record.get("kwargs"),
        workload_payload.get("kwargs"),
    )
    testcase.assertEqual(
        workload_record["text_model"],
        workload_payload.get("text_model", "str"),
    )
    testcase.assertEqual(
        workload_record.get("haystack_text_model"),
        workload_payload.get("haystack_text_model"),
    )
    testcase.assertEqual(workload_record["cache_mode"], workload_payload["cache_mode"])
    testcase.assertEqual(
        workload_record["timing_scope"],
        workload_payload.get("timing_scope", "compile-path-proxy"),
    )
    testcase.assertEqual(workload_record["syntax_features"], expected_syntax_features)
    testcase.assertEqual(workload_record["status"], expected_status)
    testcase.assertEqual(
        workload_record["baseline_timing"]["status"],
        "measured",
    )
    testcase.assertGreater(workload_record["baseline_ns"], 0)
    testcase.assertGreater(workload_record["baseline_ops_per_second"], 0)
    testcase.assertEqual(
        workload_record["implementation_timing"]["status"],
        expected_status,
    )
    if expected_status == "measured":
        testcase.assertGreater(workload_record["implementation_ns"], 0)
        testcase.assertGreater(workload_record["implementation_ops_per_second"], 0)
        testcase.assertIsInstance(workload_record["speedup_vs_cpython"], float)
    else:
        testcase.assertIsNone(workload_record["implementation_ns"])
        testcase.assertIsNone(workload_record["implementation_ops_per_second"])
        testcase.assertIsNone(workload_record["speedup_vs_cpython"])


def _write_test_manifest(
    tmp_path: pathlib.Path,
    filename: str,
    source: str,
) -> pathlib.Path:
    path = tmp_path / filename
    path.write_text(textwrap.dedent(source), encoding="utf-8")
    return path


def synthetic_workload(
    *,
    manifest_id: str,
    workload_id: str,
    operation: str,
    pattern: str = "abc",
    haystack: str | None = "abc",
    replacement: Any | None = None,
    expected_exception: dict[str, str] | None = None,
    flags: int = 0,
    use_compiled_pattern: bool = False,
    count: Any = 0,
    maxsplit: Any = 0,
    kwargs: dict[str, Any] | None = None,
    text_model: str = "str",
    haystack_text_model: str | None = None,
    pos: Any | None = None,
    endpos: Any | None = None,
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
    payload: dict[str, Any] = {
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


def _expected_exception_instance(
    expected_exception: dict[str, str],
) -> Exception:
    exception_type = {
        "TypeError": TypeError,
        "ValueError": ValueError,
    }[expected_exception["type"]]
    return exception_type(expected_exception["message_substring"])


def _record_numeric_materialization_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> list[str]:
    observed_field_names: list[str] = []
    original_materialize = benchmarks.materialize_numeric_workload_argument

    def record_numeric_materialization(value: Any, *, field_name: str) -> Any:
        observed_field_names.append(field_name)
        return original_materialize(value, field_name=field_name)

    monkeypatch.setattr(
        benchmarks,
        "materialize_numeric_workload_argument",
        record_numeric_materialization,
    )
    return observed_field_names


COLLECTION_REPLACEMENT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "collection_replacement_boundary.py"
)

@dataclass(frozen=True, slots=True)
class _CompiledPatternModuleHelperKeywordContractSpec:
    contract_filename: str
    expected_source_workload_ids: tuple[str, ...]
    manifest_timed_samples: int
    preserve_expected_exception: bool
    materializes_positional_keyword_field: bool
    notes: tuple[str, ...] = ()
    precompile_anchor_ids: tuple[str, ...] = ()

    def expected_materialized_field_names(
        self,
        source_workload: Workload,
    ) -> tuple[str, ...]:
        collection_replacement_support = _collection_replacement_anchor_support()
        if self.materializes_positional_keyword_field:
            field_names: list[str] = []
            positional_keyword_field = (
                collection_replacement_support._collection_replacement_positional_keyword_field(
                    source_workload
                )
            )
            if positional_keyword_field is not None:
                field_names.append(positional_keyword_field)
            field_names.extend(f"kwargs.{name}" for name in source_workload.kwargs)
            return tuple(field_names)

        keyword_parameter = (
            collection_replacement_support._collection_replacement_keyword_parameter_name(
                source_workload
            )
        )
        if keyword_parameter is None:
            raise AssertionError(
                "unexpected compiled-pattern module helper keyword workload "
                f"{source_workload.workload_id!r}"
            )
        return (f"kwargs.{keyword_parameter}",)

    def contract_builder_spec(self) -> _SourceTreeContractBuilderSpec:
        excluded_fields = COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_PAYLOAD_DROP_FIELDS
        if not self.preserve_expected_exception:
            excluded_fields = excluded_fields | {"expected_exception"}
        return _SourceTreeContractBuilderSpec(
            manifest_id="collection-replacement-boundary",
            excluded_fields=excluded_fields,
            manifest_timed_samples=self.manifest_timed_samples,
            timing_scope="module-helper-call",
            notes=self.notes,
        )


@dataclass(frozen=True, slots=True)
class _CompiledPatternModuleHelperKeywordContractSurface:
    case_id: str
    spec: _CompiledPatternModuleHelperKeywordContractSpec
    source_workloads_value: tuple[Workload, ...]
    precompile_source_workloads_value: tuple[Workload, ...] | None = None

    def source_workloads(self) -> tuple[Workload, ...]:
        return self.source_workloads_value

    def precompile_source_workloads(self) -> tuple[Workload, ...]:
        return self.precompile_source_workloads_value or self.source_workloads_value

    def expected_build_calls(
        self,
        source_workload: Workload,
    ) -> list[tuple[object, ...]]:
        return compiled_pattern_contract_expected_build_calls(
            source_workload,
            label="module helper keyword",
        )

    def expected_callback_call(
        self,
        source_workload: Workload,
    ) -> tuple[object, ...]:
        if source_workload.operation == "module.split":
            return (
                source_workload.operation,
                source_workload.haystack_payload(),
                source_workload.maxsplit,
                source_workload.flags,
                source_workload.kwargs,
            )
        if source_workload.operation in {"module.sub", "module.subn"}:
            return (
                source_workload.operation,
                source_workload.replacement_payload(),
                source_workload.haystack_payload(),
                source_workload.count,
                source_workload.flags,
                source_workload.kwargs,
            )
        raise AssertionError(
            "unexpected compiled-pattern module helper keyword workload operation "
            f"{source_workload.operation!r}"
        )

    def expected_callback_result(self, source_workload: Workload) -> object:
        if source_workload.operation == "module.subn":
            return ("module-result", 0)
        return "module-result"

    def run_cpython_helper_workload(
        self,
        workload: Workload,
    ) -> object:
        collection_replacement_support = _collection_replacement_anchor_support()
        compiled_pattern = re.compile(workload.pattern_payload(), workload.flags)
        helper_name = workload.operation.removeprefix("module.")
        helper = getattr(re, helper_name)
        kwargs = dict(workload.kwargs)
        positional_keyword_field = (
            collection_replacement_support._collection_replacement_positional_keyword_field(
                workload
            )
        )

        if workload.operation == "module.split":
            args: list[object] = [compiled_pattern, workload.haystack_payload()]
            if positional_keyword_field == "maxsplit":
                args.append(workload.maxsplit)
            return helper(*args, **kwargs)

        if workload.operation in {"module.sub", "module.subn"}:
            args = [
                compiled_pattern,
                workload.replacement_payload(),
                workload.haystack_payload(),
            ]
            if positional_keyword_field == "count":
                args.append(workload.count)
            return helper(*args, **kwargs)

        raise AssertionError(
            "unexpected compiled-pattern module helper keyword workload operation "
            f"{workload.operation!r}"
        )

    def assert_outcome(
        self,
        source_workload: Workload,
        workload: Workload,
        round_tripped: Workload,
    ) -> None:
        if self.case_id == "success":
            assert_benchmark_workload_matches_expected_result(
                round_tripped,
                run_benchmark_workload_with_cpython(source_workload),
            )
            return

        if self.case_id == "keyword-error":
            with pytest.raises(TypeError) as expected_error:
                self.run_cpython_helper_workload(workload)
            with pytest.raises(TypeError) as observed_error:
                run_benchmark_workload_with_cpython(round_tripped)
            assert str(observed_error.value) == str(expected_error.value)
            return

        raise AssertionError(
            "unexpected compiled-pattern module helper keyword contract surface "
            f"{self.case_id!r}"
        )

    def assert_payload_round_trip(
        self,
        source_workload: Workload,
        payload: dict[str, object],
        round_tripped: Workload,
    ) -> None:
        expected_text_type = str if source_workload.text_model == "str" else bytes
        expected_exception = (
            source_workload.expected_exception
            if self.spec.preserve_expected_exception
            else None
        )

        assert payload["use_compiled_pattern"] is True
        assert round_tripped.use_compiled_pattern is True
        assert payload["count"] == source_workload.count
        assert round_tripped.count == source_workload.count
        assert payload["maxsplit"] == source_workload.maxsplit
        assert round_tripped.maxsplit == source_workload.maxsplit
        assert payload["kwargs"] == source_workload.kwargs
        assert round_tripped.kwargs == source_workload.kwargs
        assert payload.get("expected_exception") == expected_exception
        assert round_tripped.expected_exception == expected_exception
        assert payload.get("haystack_text_model") is None
        assert round_tripped.haystack_text_model is None
        assert isinstance(round_tripped.pattern_payload(), expected_text_type)
        assert isinstance(round_tripped.haystack_payload(), expected_text_type)
        if source_workload.replacement is not None:
            assert isinstance(round_tripped.replacement_payload(), expected_text_type)
        for name, value in source_workload.kwargs.items():
            if type(value) is bool:
                assert type(payload["kwargs"][name]) is bool
                assert type(round_tripped.kwargs[name]) is bool


_PATTERN_BOUNDED_WILDCARD_WORKLOAD_IDS = (
    "pattern-search-bounded-wildcard-ignorecase-warm-str",
    "pattern-match-bounded-wildcard-warm-str",
    "pattern-fullmatch-bounded-wildcard-purged-str",
    "pattern-findall-bounded-wildcard-warm-str",
    "pattern-finditer-bounded-wildcard-purged-str",
    "pattern-search-bounded-wildcard-endpos-miss-purged-str",
)

_PATTERN_BOUNDED_WILDCARD_CASE_IDS = (
    "workflow-pattern-search-str-bounded-wildcard-ignorecase",
    "workflow-pattern-match-str-bounded-wildcard",
    "workflow-pattern-fullmatch-str-bounded-wildcard",
    "workflow-pattern-findall-str-bounded-wildcard",
    "workflow-pattern-finditer-str-bounded-wildcard",
    "workflow-pattern-search-str-bounded-wildcard-endpos-miss",
)

_PATTERN_SEARCH_VERBOSE_REGRESSION_WORKLOAD_IDS = (
    "pattern-search-verbose-regression-warm-str",
    "pattern-search-verbose-regression-digits-warm-str",
    "pattern-search-verbose-regression-too-many-digits-purged-str",
    "pattern-search-verbose-regression-warm-bytes",
    "pattern-search-verbose-regression-digits-warm-bytes",
    "pattern-search-verbose-regression-too-many-digits-purged-bytes",
)

_PATTERN_FULLMATCH_VERBOSE_REGRESSION_WORKLOAD_IDS = (
    "pattern-fullmatch-verbose-regression-warm-str",
    "pattern-fullmatch-verbose-regression-alpha-warm-str",
    "pattern-fullmatch-verbose-regression-lowercase-key-purged-str",
    "pattern-fullmatch-verbose-regression-warm-bytes",
    "pattern-fullmatch-verbose-regression-alpha-warm-bytes",
    "pattern-fullmatch-verbose-regression-lowercase-key-purged-bytes",
)

_PATTERN_VERBOSE_REGRESSION_WORKLOAD_IDS = (
    *_PATTERN_SEARCH_VERBOSE_REGRESSION_WORKLOAD_IDS,
    *_PATTERN_FULLMATCH_VERBOSE_REGRESSION_WORKLOAD_IDS,
)

_PATTERN_SEARCH_VERBOSE_REGRESSION_CASE_IDS = (
    "workflow-pattern-search-str-verbose-regression",
    "workflow-pattern-search-str-verbose-regression-digits",
    "workflow-pattern-search-str-verbose-regression-too-many-digits",
    "workflow-pattern-search-bytes-verbose-regression",
    "workflow-pattern-search-bytes-verbose-regression-digits",
    "workflow-pattern-search-bytes-verbose-regression-too-many-digits",
)

_PATTERN_FULLMATCH_VERBOSE_REGRESSION_CASE_IDS = (
    "workflow-pattern-fullmatch-str-verbose-regression",
    "workflow-pattern-fullmatch-str-verbose-regression-alpha",
    "workflow-pattern-fullmatch-str-verbose-regression-lowercase-key",
    "workflow-pattern-fullmatch-bytes-verbose-regression",
    "workflow-pattern-fullmatch-bytes-verbose-regression-alpha",
    "workflow-pattern-fullmatch-bytes-verbose-regression-lowercase-key",
)

_PATTERN_VERBOSE_REGRESSION_CASE_IDS = (
    *_PATTERN_SEARCH_VERBOSE_REGRESSION_CASE_IDS,
    *_PATTERN_FULLMATCH_VERBOSE_REGRESSION_CASE_IDS,
)

_PATTERN_VERBOSE_REGRESSION_PATTERN = (
    "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $"
)
def _pattern_window_positional_indexlike_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "pattern_call" or case.kwargs:
        return None
    if case.helper not in {"search", "match", "fullmatch", "findall", "finditer"}:
        return None
    if not any(hasattr(argument, "__index__") for argument in case.args):
        return None
    return (
        case.helper,
        case_pattern(case),
        module_workflow_positional_args_signature(case.args),
        case.text_model or "str",
    )


def _pattern_window_positional_indexlike_workload_args(
    workload: Any,
) -> tuple[object, ...]:
    if workload.operation not in {
        "pattern.search",
        "pattern.match",
        "pattern.fullmatch",
        "pattern.findall",
        "pattern.finditer",
    }:
        raise AssertionError(
            "unexpected pattern positional-indexlike workload operation "
            f"{workload.operation!r}"
        )

    args: list[object] = [workload.haystack_payload()]
    if workload.pos is not None or workload.endpos is not None:
        args.append(0 if workload.pos is None else workload.pos)
    if workload.endpos is not None:
        args.append(workload.endpos)
    return tuple(args)


def _pattern_window_positional_indexlike_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_pattern_window_positional_indexlike_workload(workload):
        raise AssertionError(
            "unexpected pattern positional-indexlike workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation.removeprefix("pattern."),
        workload.pattern_payload(),
        module_workflow_positional_args_signature(
            _pattern_window_positional_indexlike_workload_args(workload)
        ),
        workload.text_model,
    )


def _is_pattern_window_positional_indexlike_workload(workload: Any) -> bool:
    categories = set(workload.categories)
    return (
        workload.operation in {
            "pattern.search",
            "pattern.match",
            "pattern.fullmatch",
            "pattern.findall",
            "pattern.finditer",
        }
        and workload.expected_exception is None
        and not workload.kwargs
        and {"positional-window", "indexlike"}.issubset(categories)
        and (
            _is_encoded_indexlike_payload(workload.pos)
            or _is_encoded_indexlike_payload(workload.endpos)
        )
    )


def _pattern_keyword_window_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "pattern_call" or not case.kwargs:
        return None
    if case.helper not in {"search", "match", "fullmatch", "findall", "finditer"}:
        return None
    return (
        f"pattern.{case.helper}",
        case_pattern(case),
        freeze_signature_value(list(case.args)),
        module_workflow_keyword_kwargs_signature(case.kwargs),
        case.flags or 0,
        case.text_model or "str",
    )


def _pattern_keyword_window_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_pattern_keyword_window_workload(workload):
        raise AssertionError(
            "unexpected pattern keyword-window workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        freeze_signature_value([workload.haystack_payload()]),
        module_workflow_keyword_kwargs_signature(workload.kwargs),
        workload.flags,
        workload.text_model,
    )


def _is_pattern_keyword_window_workload(workload: Any) -> bool:
    categories = set(workload.categories)
    return (
        workload.operation in {
            "pattern.search",
            "pattern.match",
            "pattern.fullmatch",
            "pattern.findall",
            "pattern.finditer",
        }
        and workload.expected_exception is None
        and workload.pos is None
        and workload.endpos is None
        and bool(workload.kwargs)
        and set(workload.kwargs).issubset({"pos", "endpos"})
        and "keyword" in categories
    )


def _pattern_bounded_wildcard_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.case_id not in _PATTERN_BOUNDED_WILDCARD_CASE_IDS:
        return None
    if case.operation != "pattern_call" or case.kwargs:
        return None
    if case.helper not in {"search", "match", "fullmatch", "findall", "finditer"}:
        return None
    return (
        f"pattern.{case.helper}",
        case_pattern(case),
        freeze_signature_value(case.serialized_args()),
        (),
        case.flags or 0,
        case.text_model or "str",
    )


def _pattern_bounded_wildcard_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_pattern_bounded_wildcard_workload(workload):
        raise AssertionError(
            "unexpected pattern bounded-wildcard workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        freeze_signature_value(
            list(_pattern_window_positional_indexlike_workload_args(workload))
        ),
        (),
        workload.flags,
        workload.text_model,
    )


def _is_pattern_bounded_wildcard_workload(workload: Any) -> bool:
    return (
        workload.workload_id in _PATTERN_BOUNDED_WILDCARD_WORKLOAD_IDS
        and workload.operation in {
            "pattern.search",
            "pattern.match",
            "pattern.fullmatch",
            "pattern.findall",
            "pattern.finditer",
        }
        and workload.pattern == "a.c"
        and workload.expected_exception is None
        and not workload.use_compiled_pattern
        and workload.text_model in {"str", "bytes"}
        and workload.pos is not None
        and workload.endpos is not None
        and not workload.kwargs
    )


def _pattern_verbose_regression_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.case_id not in _PATTERN_VERBOSE_REGRESSION_CASE_IDS:
        return None
    if (
        case.operation != "pattern_call"
        or case.kwargs
        or case.helper not in {"search", "fullmatch"}
    ):
        return None
    return (
        f"pattern.{case.helper}",
        case_pattern(case),
        freeze_signature_value(list(case.args)),
        (),
        case.flags or 0,
        case.text_model or "str",
    )


def _pattern_verbose_regression_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_pattern_verbose_regression_workload(workload):
        raise AssertionError(
            "unexpected pattern verbose-regression workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        freeze_signature_value([workload.haystack_payload()]),
        (),
        workload.flags,
        workload.text_model,
    )


def _is_pattern_verbose_regression_workload(workload: Any) -> bool:
    return (
        workload.workload_id in _PATTERN_VERBOSE_REGRESSION_WORKLOAD_IDS
        and workload.operation in {"pattern.search", "pattern.fullmatch"}
        and workload.pattern == _PATTERN_VERBOSE_REGRESSION_PATTERN
        and workload.expected_exception is None
        and not workload.use_compiled_pattern
        and workload.text_model in {"str", "bytes"}
        and workload.flags == 72
        and workload.pos is None
        and workload.endpos is None
        and not workload.kwargs
    )


def _anchored_case_ids(
    definition: StandardBenchmarkAnchorContract,
) -> dict[tuple[str, str], tuple[str, ...]]:
    anchored_case_ids: dict[tuple[str, str], tuple[str, ...]] = {}
    for manifest_path in definition.manifest_paths:
        anchored_case_ids.update(
            anchored_workload_case_ids(
                manifest_path,
                anchor_case_ids=published_case_ids_by_signature(
                    definition.correctness_case_signature
                ),
                workload_signature=definition.workload_signature,
                include_workload=definition.includes_workload,
            )
        )
    return anchored_case_ids


def _unanchored_case_ids(
    definition: StandardBenchmarkAnchorContract,
    manifest_path: pathlib.Path,
    *,
    include_special_unanchored: bool = False,
) -> tuple[str, ...]:
    return unanchored_workload_ids(
        manifest_path,
        anchor_case_ids=published_case_ids_by_signature(
            definition.correctness_case_signature
        ),
        workload_signature=definition.workload_signature,
        include_workload=(
            None if include_special_unanchored else definition.includes_workload
        ),
    )


def _manual_expected_result(workload: Any) -> object:
    pattern = workload.pattern_payload()
    re.purge()
    try:
        if workload.operation == "module.compile":
            pattern_argument = (
                re.compile(pattern, workload.flags)
                if workload.use_compiled_pattern
                else pattern
            )
            return re.compile(pattern_argument, workload.flags)
        if workload.operation == "module.search":
            return re.search(pattern, workload.haystack_payload(), workload.flags)
        if workload.operation == "pattern.search":
            compiled = re.compile(pattern, workload.flags)
            if workload.endpos is not None:
                return compiled.search(
                    workload.haystack_payload(),
                    workload.pos_argument(),
                    workload.endpos_argument(),
                )
            if workload.pos is not None:
                return compiled.search(
                    workload.haystack_payload(),
                    workload.pos_argument(),
                )
            return compiled.search(workload.haystack_payload())
        if workload.operation == "pattern.fullmatch":
            compiled = re.compile(pattern, workload.flags)
            if workload.endpos is not None:
                return compiled.fullmatch(
                    workload.haystack_payload(),
                    workload.pos_argument(),
                    workload.endpos_argument(),
                )
            if workload.pos is not None:
                return compiled.fullmatch(
                    workload.haystack_payload(),
                    workload.pos_argument(),
                )
            return compiled.fullmatch(workload.haystack_payload())
        if workload.operation == "pattern.findall":
            compiled = re.compile(pattern, workload.flags)
            if workload.endpos is not None:
                return compiled.findall(
                    workload.haystack_payload(),
                    workload.pos_argument(),
                    workload.endpos_argument(),
                )
            if workload.pos is not None:
                return compiled.findall(
                    workload.haystack_payload(),
                    workload.pos_argument(),
                )
            return compiled.findall(workload.haystack_payload())
        if workload.operation == "pattern.finditer":
            compiled = re.compile(pattern, workload.flags)
            if workload.endpos is not None:
                return list(
                    compiled.finditer(
                        workload.haystack_payload(),
                        workload.pos_argument(),
                        workload.endpos_argument(),
                    )
                )
            if workload.pos is not None:
                return list(
                    compiled.finditer(
                        workload.haystack_payload(),
                        workload.pos_argument(),
                    )
                )
            return list(compiled.finditer(workload.haystack_payload()))
        if workload.operation == "module.sub":
            return re.sub(
                pattern,
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count,
                workload.flags,
            )
        if workload.operation == "module.subn":
            return re.subn(
                pattern,
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count,
                workload.flags,
            )
        if workload.operation == "pattern.sub":
            compiled = re.compile(pattern, workload.flags)
            return compiled.sub(
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count,
            )
        if workload.operation == "pattern.subn":
            compiled = re.compile(pattern, workload.flags)
            return compiled.subn(
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count,
            )
    finally:
        re.purge()

    raise AssertionError(
        f"unexpected special-unanchored benchmark workload operation {workload.operation!r}"
    )


def _has_standard_benchmark_legacy_workloads(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> bool:
    return bool(definition.expected_legacy_workload_ids)


def _runs_standard_benchmark_callback_result_parity(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> bool:
    return definition.run_callback_result_parity


def _has_standard_benchmark_special_unanchored_workloads(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> bool:
    return bool(definition.expected_special_unanchored_workload_ids)


def _has_standard_benchmark_special_unanchored_direct_parity_cases(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> bool:
    return bool(
        definition.expected_special_unanchored_workload_ids
        and definition.direct_parity_supplemental_cases
    )


def _standard_benchmark_manifest_params(
    definitions: tuple[StandardBenchmarkAnchorContractDefinition, ...],
) -> tuple[Any, ...]:
    return tuple(
        pytest.param(
            definition,
            manifest_path,
            id=f"{definition.name}:{manifest_path.name}",
        )
        for definition in definitions
        for manifest_path in definition.manifest_paths
    )


def _standard_benchmark_definition_params(
    definitions: tuple[StandardBenchmarkAnchorContractDefinition, ...],
    *,
    include_definition: Callable[[StandardBenchmarkAnchorContractDefinition], bool],
) -> tuple[Any, ...]:
    return tuple(
        pytest.param(definition, id=definition.name)
        for definition in definitions
        if include_definition(definition)
    )


def _standard_benchmark_definition_id(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> str:
    return definition.name


def _standard_benchmark_special_unanchored_result_parity_params(
    definitions: tuple[StandardBenchmarkAnchorContractDefinition, ...],
) -> tuple[Any, ...]:
    return tuple(
        pytest.param(
            definition,
            workload_id,
            id=f"{definition.name}:{workload_id}",
        )
        for definition in definitions
        if definition.run_special_unanchored_result_parity
        for workload_id in definition.expected_special_unanchored_workload_ids
    )
