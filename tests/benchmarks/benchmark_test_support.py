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


def _split_workload_ids_by_text_model(
    workload_ids: tuple[str, ...],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    return (
        tuple(
            workload_id
            for workload_id in workload_ids
            if not workload_id.endswith("-bytes")
        ),
        tuple(
            workload_id
            for workload_id in workload_ids
            if workload_id.endswith("-bytes")
        ),
    )


def _selected_workload_ids(
    workloads: Iterable[Any],
    *,
    text_model: str,
    required_categories: tuple[str, ...],
    excluded_categories: tuple[str, ...] = (),
) -> tuple[str, ...]:
    return tuple(
        workload.workload_id
        for workload in workloads
        if workload.text_model == text_model
        and all(category in workload.categories for category in required_categories)
        and all(category not in workload.categories for category in excluded_categories)
    )


def _mirrored_bytes_workload_ids(str_workload_ids: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(
        f"{workload_id.removesuffix('-str')}-bytes" for workload_id in str_workload_ids
    )


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


def assert_source_tree_benchmark_contract(
    testcase: Any,
    scorecard: dict[str, Any],
    summary: dict[str, Any],
    *,
    expected_phase: str,
    expected_runner_version: str,
    expected_adapter: str,
    expected_manifests: list[BenchmarkManifest],
    expected_manifest_paths: list[str],
    expected_selection_mode: str,
    tracked_report_path: pathlib.Path | None = None,
) -> None:
    expected_manifest_records = [
        _artifact_manifest_record(manifest_path, manifest)
        for manifest_path, manifest in zip(
            expected_manifest_paths,
            expected_manifests,
            strict=True,
        )
    ]

    _assert_benchmark_summary_consistent(testcase, scorecard, summary)
    testcase.assertEqual(scorecard["schema_version"], "1.0")
    testcase.assertEqual(scorecard["suite"], "benchmarks")
    testcase.assertEqual(scorecard["phase"], expected_phase)
    expected_baseline = {
        **build_cpython_baseline(version_family="3.12.x"),
        "re_module": "re",
    }
    for key, expected_value in expected_baseline.items():
        testcase.assertEqual(scorecard["baseline"][key], expected_value)
    testcase.assertEqual(scorecard["implementation"]["module_name"], "rebar")
    testcase.assertEqual(scorecard["implementation"]["adapter"], expected_adapter)
    testcase.assertEqual(
        scorecard["implementation"]["adapter_mode_requested"],
        "source-tree-shim",
    )
    testcase.assertEqual(
        scorecard["implementation"]["adapter_mode_resolved"],
        "source-tree-shim",
    )
    testcase.assertEqual(scorecard["implementation"]["build_mode"], "source-tree-shim")
    testcase.assertEqual(scorecard["implementation"]["timing_path"], "source-tree-shim")
    testcase.assertIsNone(scorecard["implementation"]["native_build_tool"])
    testcase.assertIsNone(scorecard["implementation"]["native_wheel"])
    testcase.assertIsInstance(scorecard["implementation"]["native_module_loaded"], bool)
    testcase.assertEqual(scorecard["implementation"]["native_module_name"], "rebar._rebar")
    if scorecard["implementation"]["native_module_loaded"]:
        testcase.assertEqual(scorecard["implementation"]["native_scaffold_status"], "scaffold-only")
        testcase.assertEqual(
            scorecard["implementation"]["native_target_cpython_series"],
            "3.12.x",
        )
    else:
        testcase.assertIsNone(scorecard["implementation"]["native_scaffold_status"])
        testcase.assertIsNone(
            scorecard["implementation"]["native_target_cpython_series"]
        )
    testcase.assertIn(
        "not requested",
        scorecard["implementation"]["native_unavailable_reason"],
    )
    testcase.assertEqual(scorecard["environment"]["runner_version"], expected_runner_version)
    testcase.assertEqual(
        scorecard["environment"]["execution_model"],
        "single-process in-process adapter comparison",
    )
    testcase.assertEqual(scorecard["artifacts"]["selection_mode"], expected_selection_mode)
    testcase.assertIsNone(scorecard["artifacts"]["raw_samples"])
    testcase.assertEqual(scorecard["artifacts"]["manifests"], expected_manifest_records)
    if len(expected_manifest_records) == 1:
        testcase.assertEqual(
            scorecard["artifacts"]["manifest"],
            expected_manifest_records[0]["manifest"],
        )
        testcase.assertEqual(
            scorecard["artifacts"]["manifest_id"],
            expected_manifest_records[0]["manifest_id"],
        )
        testcase.assertEqual(
            scorecard["artifacts"]["manifest_schema_version"],
            expected_manifest_records[0]["manifest_schema_version"],
        )
        testcase.assertEqual(
            scorecard["artifacts"]["workload_count"],
            expected_manifest_records[0]["workload_count"],
        )
        testcase.assertEqual(
            scorecard["artifacts"]["smoke_workload_ids"],
            expected_manifest_records[0]["smoke_workload_ids"],
        )
        testcase.assertEqual(
            scorecard["artifacts"]["spec_refs"],
            expected_manifest_records[0]["spec_refs"],
        )
    else:
        testcase.assertEqual(scorecard["artifacts"]["manifest"], None)
        testcase.assertEqual(scorecard["artifacts"]["manifest_id"], "combined-benchmark-suite")
        testcase.assertEqual(scorecard["artifacts"]["manifest_schema_version"], 1)
    if tracked_report_path is not None:
        testcase.assertTrue(tracked_report_path.is_file())


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


def _workload_case_pairs_workload_ids(
    workload_case_pairs: tuple[tuple[str, str], ...],
) -> tuple[str, ...]:
    return tuple(workload_id for workload_id, _ in workload_case_pairs)


def _workload_case_pairs_case_ids(
    workload_case_pairs: tuple[tuple[str, str], ...],
) -> tuple[str, ...]:
    return tuple(case_id for _, case_id in workload_case_pairs)


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
    alias_names = {
        alias.asname or alias.name
        for node in ast.walk(module_ast)
        if isinstance(node, ast.ImportFrom)
        and node.module == import_from_module
        for alias in node.names
        if alias.name == import_name
    } | {
        alias.asname or alias.name.rsplit(".", 1)[-1]
        for node in ast.walk(module_ast)
        if isinstance(node, ast.Import)
        for alias in node.names
        if alias.name == dotted_import_name
    }

    changed = True
    while changed:
        changed = False
        for node in ast.walk(module_ast):
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

    changed = True
    while changed:
        changed = False
        for node in ast.walk(module_ast):
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
                and value.value.id in module_alias_names
            ):
                aliased_attribute = value.attr
            elif isinstance(value, ast.Name):
                aliased_attribute = attribute_alias_targets.get(value.id)
                if aliased_attribute is None:
                    continue
            else:
                continue

            for target in targets:
                if attribute_alias_targets.get(target) != aliased_attribute:
                    attribute_alias_targets[target] = aliased_attribute
                    changed = True

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
        assert isinstance(assignment.value, ast.Attribute)
        assert isinstance(assignment.value.value, ast.Name)
        assert assignment.value.value.id in benchmark_test_support_alias_names
        assert assignment.value.attr == assignment_name
        assert getattr(caller_module, assignment_name) is getattr(
            shared_module,
            assignment_name,
        )


def assert_standard_inventory_reuses_owner_definitions(
    owner_definitions: tuple[StandardBenchmarkAnchorContractDefinition, ...],
    standard_definitions: tuple[StandardBenchmarkAnchorContractDefinition, ...],
    expected_definition_names: tuple[str, ...],
) -> None:
    assert isinstance(owner_definitions, tuple)
    assert tuple(definition.name for definition in owner_definitions) == (
        expected_definition_names
    )
    assert tuple(definition.name for definition in standard_definitions) == (
        expected_definition_names
    )
    assert standard_definitions == owner_definitions
    assert all(
        standard_definition is owner_definition
        for standard_definition, owner_definition in zip(
            standard_definitions, owner_definitions, strict=True
        )
    )


def select_standard_inventory_definitions(
    standard_definitions: Iterable[StandardBenchmarkAnchorContractDefinition],
    expected_definition_names: tuple[str, ...],
) -> tuple[StandardBenchmarkAnchorContractDefinition, ...]:
    definitions_by_name = {
        definition.name: definition
        for definition in standard_definitions
        if definition.name in expected_definition_names
    }
    assert tuple(definitions_by_name) == expected_definition_names
    return tuple(
        definitions_by_name[definition_name]
        for definition_name in expected_definition_names
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


def _collection_replacement_keyword_parameter_name(
    workload: Any,
) -> str | None:
    if workload.operation in {"module.split", "pattern.split"}:
        return "maxsplit"
    if workload.operation in {"module.sub", "module.subn", "pattern.sub", "pattern.subn"}:
        return "count"
    return None


def _collection_replacement_positional_keyword_field(
    workload: Any,
) -> str | None:
    if workload.operation.startswith("module."):
        expected_keyword_field = (
            benchmarks._expected_duplicate_module_helper_keyword_field(workload)
            or benchmarks._expected_positional_module_helper_keyword_field(workload)
        )
    elif workload.operation.startswith("pattern."):
        expected_keyword_field = (
            benchmarks._expected_pattern_helper_positional_keyword_field(workload)
        )
    else:
        expected_keyword_field = None
    if expected_keyword_field is None:
        return None
    keyword_parameter = _collection_replacement_keyword_parameter_name(workload)
    if expected_keyword_field != keyword_parameter:
        return None
    return expected_keyword_field


def _is_collection_replacement_keyword_workload(workload: Any) -> bool:
    keyword_parameter = _collection_replacement_keyword_parameter_name(workload)
    if keyword_parameter is None or not workload.kwargs:
        return False
    keyword_names = tuple(workload.kwargs)
    if len(keyword_names) != 1:
        return False
    if keyword_names[0] == keyword_parameter:
        return True
    if _collection_replacement_positional_keyword_field(workload) is not None:
        return True
    expected_exception = workload.expected_exception
    if expected_exception is None or expected_exception.get("type") != "TypeError":
        return False
    keyword_name = keyword_names[0]
    message_substring = expected_exception.get("message_substring")
    if not isinstance(message_substring, str):
        return False
    if f"unexpected keyword argument '{keyword_name}'" in message_substring:
        return True
    if workload.operation.startswith("pattern."):
        helper_name = workload.operation.removeprefix("pattern.")
        return (
            message_substring
            == f"'{keyword_name}' is an invalid keyword argument for {helper_name}()"
        )
    return False


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


def _is_module_workflow_compiled_pattern_wrong_text_model_workload(
    workload: Any,
) -> bool:
    return (
        not workload.kwargs
        and workload.use_compiled_pattern
        and workload.operation in _COMPILED_PATTERN_MODULE_HELPER_OPERATIONS
        and getattr(workload, "haystack_text_model", None) is not None
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


_COMPILED_PATTERN_MODULE_COMPILE_INT_ZERO_KEYWORD_SIGNATURE = (
    ("flags", "int", 0),
)
_COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_SIGNATURE = (
    ("flags", "bool", False),
)
_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_SIGNATURE = (
    ("flags", "int", int(re.IGNORECASE)),
)
_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS = ("abc",)
_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS = (
    "(?P<word>abc)",
)
_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION = {
    "type": "ValueError",
    "message_substring": "cannot process flags argument with a compiled pattern",
}


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


def _compiled_pattern_module_compile_keyword_signature(
    contract_case: CompiledPatternModuleCompileContractCase,
) -> tuple[tuple[str, str, object], ...]:
    if contract_case.keyword_signature is None:
        raise AssertionError(
            "missing compiled-pattern module.compile keyword signature for "
            f"{contract_case.case_id!r}"
        )
    return contract_case.keyword_signature


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
    contract_case: CompiledPatternModuleCompileContractCase,
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
    contract_case: CompiledPatternModuleCompileContractCase,
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


def _compiled_pattern_module_compile_keyword_correctness_case_signature(
    contract_case: CompiledPatternModuleCompileContractCase,
    case: Any,
) -> tuple[Any, ...] | None:
    return _module_workflow_compiled_pattern_compile_keyword_correctness_case_signature(
        case,
        keyword_signature=_compiled_pattern_module_compile_keyword_signature(
            contract_case
        ),
        allowed_patterns=contract_case.allowed_patterns,
    )


def _compiled_pattern_module_compile_keyword_workload_signature(
    contract_case: CompiledPatternModuleCompileContractCase,
    workload: Any,
) -> tuple[Any, ...]:
    return _module_workflow_compiled_pattern_compile_keyword_workload_signature(
        workload,
        keyword_label=contract_case.case_id,
        keyword_signature=_compiled_pattern_module_compile_keyword_signature(
            contract_case
        ),
        allowed_patterns=contract_case.allowed_patterns,
        expected_exception=contract_case.expected_exception,
    )


def _is_compiled_pattern_module_compile_keyword_workload(
    contract_case: CompiledPatternModuleCompileContractCase,
    workload: Any,
) -> bool:
    return _is_module_workflow_compiled_pattern_compile_keyword_workload(
        workload,
        keyword_signature=_compiled_pattern_module_compile_keyword_signature(
            contract_case
        ),
        allowed_patterns=contract_case.allowed_patterns,
        expected_exception=contract_case.expected_exception,
    )


def _run_cpython_compiled_pattern_module_compile_keyword_workload(
    contract_case: CompiledPatternModuleCompileContractCase,
    workload: Workload,
) -> object:
    del contract_case
    compiled_pattern = re.compile(workload.pattern_payload(), workload.flags)
    return re.compile(compiled_pattern, **workload.keyword_arguments())


def _compiled_pattern_module_compile_keyword_callback_flags(
    contract_case: CompiledPatternModuleCompileContractCase,
    source_workload: Workload,
) -> object:
    del contract_case
    return source_workload.keyword_arguments()["flags"]


def _compiled_pattern_module_compile_success_correctness_case_signature(
    contract_case: CompiledPatternModuleCompileContractCase,
    case: Any,
) -> tuple[Any, ...] | None:
    del contract_case
    return _module_workflow_compiled_pattern_compile_correctness_case_signature(case)


def _compiled_pattern_module_compile_success_workload_signature(
    contract_case: CompiledPatternModuleCompileContractCase,
    workload: Any,
) -> tuple[Any, ...]:
    del contract_case
    return _module_workflow_compiled_pattern_compile_workload_signature(workload)


def _is_compiled_pattern_module_compile_success_workload(
    contract_case: CompiledPatternModuleCompileContractCase,
    workload: Any,
) -> bool:
    del contract_case
    return _is_module_workflow_compiled_pattern_compile_workload(workload)


def _run_cpython_compiled_pattern_module_compile_success_workload(
    contract_case: CompiledPatternModuleCompileContractCase,
    workload: Workload,
) -> object:
    del contract_case
    compiled_pattern = re.compile(workload.pattern_payload(), workload.flags)
    return re.compile(compiled_pattern, workload.flags)


def _compiled_pattern_module_compile_success_callback_flags(
    contract_case: CompiledPatternModuleCompileContractCase,
    source_workload: Workload,
) -> object:
    del contract_case
    return source_workload.flags


@dataclass(frozen=True, slots=True)
class _CompiledPatternModuleCompileContractRoute:
    surface_label: str
    excluded_fields: frozenset[str]
    note: str
    correctness_case_signature_builder: Callable[
        [CompiledPatternModuleCompileContractCase, Any],
        tuple[Any, ...] | None,
    ]
    workload_signature_builder: Callable[
        [CompiledPatternModuleCompileContractCase, Any],
        tuple[Any, ...],
    ]
    include_workload_selector: Callable[
        [CompiledPatternModuleCompileContractCase, Any],
        bool,
    ]
    payload_round_trip_assertion: Callable[
        [CompiledPatternModuleCompileContractCase, Workload, dict[str, object], Workload],
        None,
    ]
    cpython_dispatch: Callable[
        [CompiledPatternModuleCompileContractCase, Workload],
        object,
    ]
    callback_flags_selector: Callable[
        [CompiledPatternModuleCompileContractCase, Workload],
        object,
    ]

    def drift_message(
        self,
        contract_case: CompiledPatternModuleCompileContractCase,
    ) -> str:
        return (
            f"compiled-pattern module.compile {self.surface_label} rows drifted from the "
            f"{contract_case.case_id} contract surface"
        )


@dataclass(frozen=True)
class CompiledPatternModuleCompileContractCase:
    route: _CompiledPatternModuleCompileContractRoute
    case_id: str
    manifest_path: pathlib.Path
    source_selectors: tuple[Callable[[Any], bool], ...]
    contract_filename: str
    anchor_contract_filename: str
    expected_anchor_pairs: tuple[tuple[str, str], ...]
    expected_build_calls_builder: Callable[[Workload], list[tuple[object, ...]]]
    keyword_signature: tuple[tuple[str, str, object], ...] | None = None
    allowed_patterns: tuple[str, ...] = ()
    expected_exception: dict[str, str] | None = None

    def expected_source_workload_ids(self) -> tuple[str, ...]:
        return tuple(
            workload_id.removesuffix("-contract")
            for workload_id, _case_id in self.expected_anchor_pairs
        )

    def source_workloads(self) -> tuple[Workload, ...]:
        return _contract_source_workloads(
            manifest_path=self.manifest_path,
            include_workload_selectors=self.source_selectors,
            expected_source_workload_ids=self.expected_source_workload_ids(),
            drift_message=self.route.drift_message(self),
        )

    def manifest_excluded_fields(self) -> frozenset[str]:
        return self.route.excluded_fields

    def note(self) -> str:
        return self.route.note

    def correctness_case_signature(self, case: Any) -> tuple[Any, ...] | None:
        return self.route.correctness_case_signature_builder(self, case)

    def workload_signature(self, workload: Any) -> tuple[Any, ...]:
        return self.route.workload_signature_builder(self, workload)

    def include_workload(self, workload: Any) -> bool:
        return self.route.include_workload_selector(self, workload)

    def assert_payload_round_trip(
        self,
        source_workload: Workload,
        payload: dict[str, object],
        round_tripped: Workload,
    ) -> None:
        self.route.payload_round_trip_assertion(
            self,
            source_workload,
            payload,
            round_tripped,
        )

    def run_cpython_workload(self, workload: Workload) -> object:
        return self.route.cpython_dispatch(self, workload)

    def callback_flags(self, source_workload: Workload) -> object:
        return self.route.callback_flags_selector(self, source_workload)

    def expected_anchor_case_ids(
        self,
        manifest_path: pathlib.Path,
    ) -> dict[tuple[str, str], tuple[str, ...]]:
        return _workload_case_pair_anchor_expectations(
            manifest_path,
            self.expected_anchor_pairs,
        )

    def expected_build_calls(
        self,
        source_workload: Workload,
    ) -> list[tuple[object, ...]]:
        return self.expected_build_calls_builder(source_workload)

    def contract_builder_spec(self) -> _SourceTreeContractBuilderSpec:
        return source_tree_support._SourceTreeContractBuilderSpec(
            manifest_id="module-boundary",
            excluded_fields=self.manifest_excluded_fields(),
            manifest_timed_samples=2,
            timing_scope="module-helper-call",
            notes=(self.note(),),
        )


_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_CONTRACT_ROUTE = (
    _CompiledPatternModuleCompileContractRoute(
        surface_label="success",
        excluded_fields=COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS,
        note=(
            "Ensures benchmark manifests keep the bounded compiled-pattern-first-argument "
            "module.compile rows unresolved until helper invocation."
        ),
        correctness_case_signature_builder=(
            _compiled_pattern_module_compile_success_correctness_case_signature
        ),
        workload_signature_builder=(
            _compiled_pattern_module_compile_success_workload_signature
        ),
        include_workload_selector=_is_compiled_pattern_module_compile_success_workload,
        payload_round_trip_assertion=(
            _assert_compiled_pattern_module_compile_success_payload_round_trip
        ),
        cpython_dispatch=_run_cpython_compiled_pattern_module_compile_success_workload,
        callback_flags_selector=(
            _compiled_pattern_module_compile_success_callback_flags
        ),
    )
)

_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CONTRACT_ROUTE = (
    _CompiledPatternModuleCompileContractRoute(
        surface_label="keyword",
        excluded_fields=(
            COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS
            | {"categories", "syntax_features"}
        ),
        note=(
            "Ensures benchmark manifests keep the bounded compiled-pattern-first-argument "
            "module.compile flags= keyword rows unresolved until helper invocation."
        ),
        correctness_case_signature_builder=(
            _compiled_pattern_module_compile_keyword_correctness_case_signature
        ),
        workload_signature_builder=(
            _compiled_pattern_module_compile_keyword_workload_signature
        ),
        include_workload_selector=_is_compiled_pattern_module_compile_keyword_workload,
        payload_round_trip_assertion=(
            _assert_compiled_pattern_module_compile_keyword_payload_round_trip
        ),
        cpython_dispatch=_run_cpython_compiled_pattern_module_compile_keyword_workload,
        callback_flags_selector=(
            _compiled_pattern_module_compile_keyword_callback_flags
        ),
    )
)


@dataclass(frozen=True)
class _CompiledPatternModuleContractAnchorLane:
    case_id: str
    contract_filename: str
    source_workloads: tuple[Workload, ...]
    contract_builder_spec: Callable[[], Any]
    expected_anchor_case_ids: Callable[
        [pathlib.Path],
        dict[tuple[str, str], tuple[str, ...]],
    ]
    anchor_case_ids: dict[tuple[Any, ...], tuple[str, ...]]
    workload_signature: Callable[[Any], tuple[Any, ...]]
    include_workload: Callable[[Any], bool]
    expected_anchor_pairs: tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class _CompiledPatternModuleCompileKeywordOwnerSpec:
    case_id: str
    anchor_definition_name: str
    keyword_signature: tuple[tuple[str, str, object], ...]
    allowed_patterns: tuple[str, ...]
    anchor_expectations: tuple[tuple[str, tuple[str, ...]], ...]
    contract_filename: str
    anchor_contract_filename: str
    expected_anchor_pairs: tuple[tuple[str, str], ...]
    expected_exception: dict[str, str] | None = None

    def correctness_case_signature(self, case: Any) -> tuple[Any, ...] | None:
        return _module_workflow_compiled_pattern_compile_keyword_correctness_case_signature(
            case,
            keyword_signature=self.keyword_signature,
            allowed_patterns=self.allowed_patterns,
        )

    def workload_signature(self, workload: Any) -> tuple[Any, ...]:
        return _module_workflow_compiled_pattern_compile_keyword_workload_signature(
            workload,
            keyword_label=self.case_id,
            keyword_signature=self.keyword_signature,
            allowed_patterns=self.allowed_patterns,
            expected_exception=self.expected_exception,
        )

    def includes_workload(self, workload: Any) -> bool:
        return _is_module_workflow_compiled_pattern_compile_keyword_workload(
            workload,
            keyword_signature=self.keyword_signature,
            allowed_patterns=self.allowed_patterns,
            expected_exception=self.expected_exception,
        )

    def expected_anchor_case_ids(self) -> dict[tuple[str, str], tuple[str, ...]]:
        return _definition_anchor_expectations(
            MODULE_BOUNDARY_MANIFEST_PATH,
            dict(self.anchor_expectations),
        )

    def expected_anchor_workload_ids(self) -> tuple[str, ...]:
        return tuple(workload_id for workload_id, _ in self.anchor_expectations)

    def anchor_definition(self) -> StandardBenchmarkAnchorContractDefinition:
        return StandardBenchmarkAnchorContractDefinition(
            name=self.anchor_definition_name,
            manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
            expected_anchor_case_ids=self.expected_anchor_case_ids(),
            include_workload=self.includes_workload,
            correctness_case_signature=self.correctness_case_signature,
            workload_signature=self.workload_signature,
            run_callback_result_parity=True,
        )

    def contract_case(self) -> CompiledPatternModuleCompileContractCase:
        return CompiledPatternModuleCompileContractCase(
            route=_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CONTRACT_ROUTE,
            case_id=self.case_id,
            manifest_path=MODULE_BOUNDARY_MANIFEST_PATH,
            source_selectors=(self.includes_workload,),
            keyword_signature=self.keyword_signature,
            allowed_patterns=self.allowed_patterns,
            contract_filename=self.contract_filename,
            anchor_contract_filename=self.anchor_contract_filename,
            expected_anchor_pairs=self.expected_anchor_pairs,
            expected_build_calls_builder=partial(
                compiled_pattern_contract_expected_build_calls,
                label="module.compile contract",
            ),
            expected_exception=self.expected_exception,
        )


@dataclass(frozen=True, slots=True)
class _CompiledPatternModuleCompileSuccessOwnerSpec:
    anchor_definition_name: str
    allowed_patterns: tuple[str, ...]
    anchor_expectations: tuple[tuple[str, tuple[str, ...]], ...]
    expected_anchor_pairs: tuple[tuple[str, str], ...]

    def correctness_case_signature(self, case: Any) -> tuple[Any, ...] | None:
        return _module_workflow_compiled_pattern_compile_correctness_case_signature(
            case
        )

    def workload_signature(self, workload: Any) -> tuple[Any, ...]:
        return _module_workflow_compiled_pattern_compile_workload_signature(workload)

    def includes_workload(self, workload: Any) -> bool:
        return _is_module_workflow_compiled_pattern_compile_success_workload(
            workload,
            allowed_patterns=self.allowed_patterns,
        )

    def expected_anchor_case_ids(self) -> dict[tuple[str, str], tuple[str, ...]]:
        return _definition_anchor_expectations(
            MODULE_BOUNDARY_MANIFEST_PATH,
            dict(self.anchor_expectations),
        )

    def expected_anchor_workload_ids(self) -> tuple[str, ...]:
        return tuple(workload_id for workload_id, _ in self.anchor_expectations)

    def anchor_definition(self) -> StandardBenchmarkAnchorContractDefinition:
        return StandardBenchmarkAnchorContractDefinition(
            name=self.anchor_definition_name,
            manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
            expected_anchor_case_ids=self.expected_anchor_case_ids(),
            include_workload=self.includes_workload,
            correctness_case_signature=self.correctness_case_signature,
            workload_signature=self.workload_signature,
            run_callback_result_parity=True,
        )


def build_compiled_pattern_module_compile_contract_cases(
    *,
    manifest_path: pathlib.Path,
    expected_build_calls_builder: Callable[[Workload], list[tuple[object, ...]]],
    success_owner_specs: Iterable[Any],
    keyword_owner_specs: Iterable[Any],
) -> tuple[CompiledPatternModuleCompileContractCase, ...]:
    success_owner_specs = tuple(success_owner_specs)
    keyword_owner_specs = tuple(keyword_owner_specs)
    keyword_case_groups = tuple(
        owner_spec.contract_case() for owner_spec in keyword_owner_specs
    )
    return (
        CompiledPatternModuleCompileContractCase(
            route=_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_CONTRACT_ROUTE,
            case_id="success",
            manifest_path=manifest_path,
            source_selectors=tuple(
                owner_spec.includes_workload for owner_spec in success_owner_specs
            ),
            contract_filename=(
                "python_benchmark_compiled_pattern_module_compile_contract.py"
            ),
            anchor_contract_filename=(
                "python_benchmark_compiled_pattern_module_compile_anchor_contract.py"
            ),
            expected_anchor_pairs=tuple(
                anchor_pair
                for owner_spec in success_owner_specs
                for anchor_pair in owner_spec.expected_anchor_pairs
            ),
            expected_build_calls_builder=expected_build_calls_builder,
        ),
        *keyword_case_groups,
    )


def build_compiled_pattern_module_compile_contract_source_workload_params(
    contract_cases: Iterable[CompiledPatternModuleCompileContractCase],
) -> tuple[Any, ...]:
    return tuple(
        pytest.param(
            contract_case,
            source_workload,
            id=f"{contract_case.case_id}-{source_workload.workload_id}",
        )
        for contract_case in contract_cases
        for source_workload in contract_case.source_workloads()
    )


def build_compiled_pattern_module_contract_anchor_lanes(
    *,
    contract_cases: Iterable[CompiledPatternModuleCompileContractCase],
    published_case_ids_by_signature: Callable[
        [Callable[[Any], tuple[Any, ...] | None]],
        dict[tuple[Any, ...], tuple[str, ...]],
    ],
) -> tuple[_CompiledPatternModuleContractAnchorLane, ...]:
    contract_cases = tuple(contract_cases)
    return tuple(
        _CompiledPatternModuleContractAnchorLane(
            case_id=contract_case.case_id,
            contract_filename=contract_case.anchor_contract_filename,
            source_workloads=source_workloads,
            contract_builder_spec=contract_case.contract_builder_spec,
            expected_anchor_case_ids=contract_case.expected_anchor_case_ids,
            anchor_case_ids=published_case_ids_by_signature(
                contract_case.correctness_case_signature
            ),
            workload_signature=contract_case.workload_signature,
            include_workload=contract_case.include_workload,
            expected_anchor_pairs=contract_case.expected_anchor_pairs,
        )
        for contract_case in contract_cases
        for source_workloads in (contract_case.source_workloads(),)
    )


_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS = (
    _CompiledPatternModuleCompileSuccessOwnerSpec(
        anchor_definition_name=(
            "module-workflow-compiled-pattern-module-compile-literal-success"
        ),
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS,
        anchor_expectations=(
            (
                "module-compile-literal-warm-str-compiled-pattern",
                ("workflow-module-compile-str-compiled-pattern",),
            ),
            (
                "module-compile-literal-purged-bytes-compiled-pattern",
                ("workflow-module-compile-bytes-compiled-pattern",),
            ),
        ),
        expected_anchor_pairs=(
            (
                "module-compile-literal-warm-str-compiled-pattern-contract",
                "workflow-module-compile-str-compiled-pattern",
            ),
            (
                "module-compile-literal-purged-bytes-compiled-pattern-contract",
                "workflow-module-compile-bytes-compiled-pattern",
            ),
        ),
    ),
    _CompiledPatternModuleCompileSuccessOwnerSpec(
        anchor_definition_name=(
            "module-workflow-compiled-pattern-module-compile-named-group-success"
        ),
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS,
        anchor_expectations=(
            (
                "module-compile-named-group-warm-str-compiled-pattern",
                ("workflow-module-compile-str-compiled-pattern-named-group",),
            ),
            (
                "module-compile-named-group-purged-bytes-compiled-pattern",
                ("workflow-module-compile-bytes-compiled-pattern-named-group",),
            ),
        ),
        expected_anchor_pairs=(
            (
                "module-compile-named-group-warm-str-compiled-pattern-contract",
                "workflow-module-compile-str-compiled-pattern-named-group",
            ),
            (
                "module-compile-named-group-purged-bytes-compiled-pattern-contract",
                "workflow-module-compile-bytes-compiled-pattern-named-group",
            ),
        ),
    ),
)

_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS = (
    _CompiledPatternModuleCompileKeywordOwnerSpec(
        case_id="int-zero",
        anchor_definition_name=(
            "module-workflow-compiled-pattern-module-compile-flags-int-zero-keyword"
        ),
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_INT_ZERO_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS,
        anchor_expectations=(
            (
                "module-compile-flags-int-zero-warm-str-compiled-pattern",
                ("workflow-module-compile-flags-int-zero-str-compiled-pattern",),
            ),
            (
                "module-compile-flags-int-zero-purged-bytes-compiled-pattern",
                ("workflow-module-compile-flags-int-zero-bytes-compiled-pattern",),
            ),
        ),
        contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_keyword_contract.py"
        ),
        anchor_contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_keyword_anchor_contract.py"
        ),
        expected_anchor_pairs=(
            (
                "module-compile-flags-int-zero-warm-str-compiled-pattern-contract",
                "workflow-module-compile-flags-int-zero-str-compiled-pattern",
            ),
            (
                "module-compile-flags-int-zero-purged-bytes-compiled-pattern-contract",
                "workflow-module-compile-flags-int-zero-bytes-compiled-pattern",
            ),
        ),
    ),
    _CompiledPatternModuleCompileKeywordOwnerSpec(
        case_id="int-zero-named-group",
        anchor_definition_name=(
            "module-workflow-compiled-pattern-module-compile-flags-int-zero-"
            "keyword-named-group"
        ),
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_INT_ZERO_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS,
        anchor_expectations=(
            (
                "module-compile-flags-int-zero-warm-str-compiled-pattern-named-group",
                (
                    "workflow-module-compile-flags-int-zero-str-compiled-pattern-"
                    "named-group",
                ),
            ),
            (
                "module-compile-flags-int-zero-purged-bytes-compiled-pattern-named-group",
                (
                    "workflow-module-compile-flags-int-zero-bytes-compiled-pattern-"
                    "named-group",
                ),
            ),
        ),
        contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_named_group_keyword_contract.py"
        ),
        anchor_contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_named_group_keyword_anchor_contract.py"
        ),
        expected_anchor_pairs=(
            (
                "module-compile-flags-int-zero-warm-str-compiled-pattern-named-group-contract",
                "workflow-module-compile-flags-int-zero-str-compiled-pattern-named-group",
            ),
            (
                "module-compile-flags-int-zero-purged-bytes-compiled-pattern-named-group-contract",
                "workflow-module-compile-flags-int-zero-bytes-compiled-pattern-named-group",
            ),
        ),
    ),
    _CompiledPatternModuleCompileKeywordOwnerSpec(
        case_id="bool-false",
        anchor_definition_name=(
            "module-workflow-compiled-pattern-module-compile-flags-bool-false-keyword"
        ),
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS,
        anchor_expectations=(
            (
                "module-compile-flags-bool-false-warm-str-compiled-pattern",
                ("workflow-module-compile-flags-bool-false-str-compiled-pattern",),
            ),
            (
                "module-compile-flags-bool-false-purged-bytes-compiled-pattern",
                ("workflow-module-compile-flags-bool-false-bytes-compiled-pattern",),
            ),
        ),
        contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_bool_false_keyword_contract.py"
        ),
        anchor_contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_bool_false_keyword_anchor_contract.py"
        ),
        expected_anchor_pairs=(
            (
                "module-compile-flags-bool-false-warm-str-compiled-pattern-contract",
                "workflow-module-compile-flags-bool-false-str-compiled-pattern",
            ),
            (
                "module-compile-flags-bool-false-purged-bytes-compiled-pattern-contract",
                "workflow-module-compile-flags-bool-false-bytes-compiled-pattern",
            ),
        ),
    ),
    _CompiledPatternModuleCompileKeywordOwnerSpec(
        case_id="bool-false-named-group",
        anchor_definition_name=(
            "module-workflow-compiled-pattern-module-compile-flags-bool-false-"
            "keyword-named-group"
        ),
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_BOOL_FALSE_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS,
        anchor_expectations=(
            (
                "module-compile-flags-bool-false-warm-str-compiled-pattern-named-group",
                (
                    "workflow-module-compile-flags-bool-false-str-compiled-pattern-"
                    "named-group",
                ),
            ),
            (
                "module-compile-flags-bool-false-purged-bytes-compiled-pattern-named-group",
                (
                    "workflow-module-compile-flags-bool-false-bytes-compiled-pattern-"
                    "named-group",
                ),
            ),
        ),
        contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_bool_false_named_group_keyword_contract.py"
        ),
        anchor_contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_bool_false_named_group_keyword_anchor_contract.py"
        ),
        expected_anchor_pairs=(
            (
                "module-compile-flags-bool-false-warm-str-compiled-pattern-named-group-contract",
                "workflow-module-compile-flags-bool-false-str-compiled-pattern-named-group",
            ),
            (
                "module-compile-flags-bool-false-purged-bytes-compiled-pattern-named-group-contract",
                "workflow-module-compile-flags-bool-false-bytes-compiled-pattern-named-group",
            ),
        ),
    ),
    _CompiledPatternModuleCompileKeywordOwnerSpec(
        case_id="ignorecase",
        anchor_definition_name=(
            "module-workflow-compiled-pattern-module-compile-flags-ignorecase-"
            "keyword-rejection"
        ),
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_LITERAL_KEYWORD_PATTERNS,
        anchor_expectations=(
            (
                "module-compile-flags-ignorecase-warm-str-compiled-pattern",
                ("workflow-module-compile-flags-ignorecase-str-compiled-pattern",),
            ),
            (
                "module-compile-flags-ignorecase-purged-bytes-compiled-pattern",
                ("workflow-module-compile-flags-ignorecase-bytes-compiled-pattern",),
            ),
        ),
        contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_ignorecase_keyword_contract.py"
        ),
        anchor_contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_ignorecase_keyword_anchor_contract.py"
        ),
        expected_anchor_pairs=(
            (
                "module-compile-flags-ignorecase-warm-str-compiled-pattern-contract",
                "workflow-module-compile-flags-ignorecase-str-compiled-pattern",
            ),
            (
                "module-compile-flags-ignorecase-purged-bytes-compiled-pattern-contract",
                "workflow-module-compile-flags-ignorecase-bytes-compiled-pattern",
            ),
        ),
        expected_exception=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION,
    ),
    _CompiledPatternModuleCompileKeywordOwnerSpec(
        case_id="ignorecase-named-group",
        anchor_definition_name=(
            "module-workflow-compiled-pattern-module-compile-flags-ignorecase-"
            "keyword-rejection-named-group"
        ),
        keyword_signature=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_KEYWORD_SIGNATURE,
        allowed_patterns=_COMPILED_PATTERN_MODULE_COMPILE_NAMED_GROUP_KEYWORD_PATTERNS,
        anchor_expectations=(
            (
                "module-compile-flags-ignorecase-warm-str-compiled-pattern-named-group",
                (
                    "workflow-module-compile-flags-ignorecase-str-compiled-pattern-"
                    "named-group",
                ),
            ),
            (
                "module-compile-flags-ignorecase-purged-bytes-compiled-pattern-named-group",
                (
                    "workflow-module-compile-flags-ignorecase-bytes-compiled-pattern-"
                    "named-group",
                ),
            ),
        ),
        contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_ignorecase_named_group_keyword_contract.py"
        ),
        anchor_contract_filename=(
            "python_benchmark_compiled_pattern_module_compile_ignorecase_named_group_keyword_anchor_contract.py"
        ),
        expected_anchor_pairs=(
            (
                "module-compile-flags-ignorecase-warm-str-compiled-pattern-named-group-contract",
                "workflow-module-compile-flags-ignorecase-str-compiled-pattern-named-group",
            ),
            (
                "module-compile-flags-ignorecase-purged-bytes-compiled-pattern-named-group-contract",
                "workflow-module-compile-flags-ignorecase-bytes-compiled-pattern-named-group",
            ),
        ),
        expected_exception=_COMPILED_PATTERN_MODULE_COMPILE_IGNORECASE_REJECTION,
    ),
)


def _build_compiled_pattern_module_compile_standard_benchmark_definitions() -> tuple[
    StandardBenchmarkAnchorContractDefinition, ...
]:
    return tuple(
        owner_spec.anchor_definition()
        for owner_spec in (
            *_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS,
            *_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS,
        )
    )


COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS = (
    _build_compiled_pattern_module_compile_standard_benchmark_definitions()
)

_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES = (
    build_compiled_pattern_module_compile_contract_cases(
        manifest_path=MODULE_BOUNDARY_MANIFEST_PATH,
        expected_build_calls_builder=partial(
            compiled_pattern_contract_expected_build_calls,
            label="module.compile contract",
        ),
        success_owner_specs=_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS,
        keyword_owner_specs=_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS,
    )
)

_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS = (
    build_compiled_pattern_module_compile_contract_source_workload_params(
        _COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES
    )
)

_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES = (
    build_compiled_pattern_module_contract_anchor_lanes(
        contract_cases=_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES,
        published_case_ids_by_signature=published_case_ids_by_signature,
    )
)


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


def _assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call(
    monkeypatch: pytest.MonkeyPatch,
    workload: Workload,
    *,
    expected_result: object | None,
    expected_exception_message: str | None = None,
    expected_field_names: list[str] | tuple[str, ...],
) -> None:
    observed_field_names = _record_numeric_materialization_fields(monkeypatch)

    re.purge()
    try:
        callback = benchmarks.build_callable(re, "re", workload)
        assert observed_field_names == []

        if expected_exception_message is None:
            assert callback() == expected_result
            assert callback() == expected_result
        else:
            with pytest.raises(TypeError, match=re.escape(expected_exception_message)):
                callback()
            with pytest.raises(TypeError, match=re.escape(expected_exception_message)):
                callback()

        assert observed_field_names == list(expected_field_names) * 2
    finally:
        re.purge()


COLLECTION_REPLACEMENT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "collection_replacement_boundary.py"
)
_COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS = (
    "module-split-on-bytes-string-purged-str-compiled-pattern",
    "module-findall-on-str-string-purged-bytes-compiled-pattern",
    "module-finditer-on-bytes-string-warm-str-compiled-pattern",
    "module-sub-on-bytes-string-warm-str-compiled-pattern",
    "module-subn-on-str-string-purged-bytes-compiled-pattern",
)
_COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS = (
    "module-search-on-bytes-string-warm-str-compiled-pattern",
    "module-match-on-str-string-purged-bytes-compiled-pattern",
    "module-fullmatch-on-bytes-string-warm-str-compiled-pattern",
)
_COMPILED_PATTERN_MODULE_HELPER_OPERATIONS = frozenset(
    {"module.search", "module.match", "module.fullmatch"}
)
_VERBOSE_REGRESSION_PATTERN = (
    r"^ (?P<key>[A-Z_]+) \s* = \s* (?:[A-Z]{2,4}+|\d{2,3}) $"
)
_VERBOSE_REGRESSION_FLAGS = int(re.VERBOSE | re.MULTILINE)


def _compiled_pattern_wrong_text_model_specs() -> tuple[dict[str, object], ...]:
    return (
        {
            "case_id": "compiled_pattern_module_helper_wrong_text_model",
            "manifest_path": "collection_replacement_boundary.py",
            "include_workload": _is_collection_replacement_wrong_text_model_workload,
            "contract_manifest_id": "collection-replacement-boundary",
            "contract_filename": (
                "python_benchmark_compiled_pattern_collection_replacement_wrong_text_model_contract.py"
            ),
            "expected_source_workload_ids": (
                _COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
            ),
        },
        {
            "case_id": "compiled_pattern_module_boundary_wrong_text_model",
            "manifest_path": "module_boundary.py",
            "include_workload": (
                _is_module_workflow_compiled_pattern_wrong_text_model_workload
            ),
            "contract_manifest_id": "module-boundary",
            "contract_filename": (
                "python_benchmark_compiled_pattern_module_boundary_wrong_text_model_contract.py"
            ),
            "expected_source_workload_ids": (
                _COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS
            ),
        },
    )


def _compiled_pattern_wrong_text_model_source_workloads(
    spec: dict[str, object],
) -> tuple[Workload, ...]:
    return selected_manifest_workloads(
        spec["manifest_path"],
        include_workload=spec["include_workload"],
    )


def _compiled_pattern_module_helper_route(
    workload: Workload,
    *,
    collection_replacement_callback_flags: int,
) -> tuple[object, tuple[object, ...], tuple[object, ...], bool]:
    if workload.operation in _COMPILED_PATTERN_MODULE_HELPER_OPERATIONS:
        return (
            "module-result",
            (
                workload.operation,
                workload.haystack_payload(),
                0,
                {},
            ),
            (
                workload.haystack_payload(),
                workload.flags,
            ),
            False,
        )
    if workload.operation == "module.split":
        return (
            "module-result",
            (
                workload.operation,
                workload.haystack_payload(),
                workload.maxsplit_argument(),
                collection_replacement_callback_flags,
                {},
            ),
            (
                workload.haystack_payload(),
                workload.maxsplit_argument(),
            ),
            False,
        )
    if workload.operation == "module.findall":
        return (
            "module-result",
            (
                workload.operation,
                workload.haystack_payload(),
                collection_replacement_callback_flags,
            ),
            (
                workload.haystack_payload(),
                workload.flags,
            ),
            False,
        )
    if workload.operation == "module.finditer":
        return (
            ["module-finditer-result"],
            (
                workload.operation,
                workload.haystack_payload(),
                collection_replacement_callback_flags,
            ),
            (
                workload.haystack_payload(),
                workload.flags,
            ),
            True,
        )
    if workload.operation == "module.sub":
        return (
            "module-result",
            (
                workload.operation,
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count_argument(),
                collection_replacement_callback_flags,
                {},
            ),
            (
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count_argument(),
            ),
            False,
        )
    if workload.operation == "module.subn":
        return (
            ("module-result", 0),
            (
                workload.operation,
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count_argument(),
                collection_replacement_callback_flags,
                {},
            ),
            (
                workload.replacement_payload(),
                workload.haystack_payload(),
                workload.count_argument(),
            ),
            False,
        )
    raise AssertionError(
        "unexpected compiled-pattern module helper workload operation "
        f"{workload.operation!r}"
    )


def _run_cpython_compiled_pattern_module_helper_workload(
    workload: Workload,
    *,
    collection_replacement_callback_flags: int,
) -> object:
    compiled_pattern = re.compile(
        workload.pattern_payload(),
        workload.flags,
    )
    _, _, cpython_call_args, materialize_cpython_result = (
        _compiled_pattern_module_helper_route(
            workload,
            collection_replacement_callback_flags=collection_replacement_callback_flags,
        )
    )
    helper = getattr(re, workload.operation.removeprefix("module."))
    result = helper(compiled_pattern, *cpython_call_args)
    if materialize_cpython_result:
        return list(result)
    return result


def _module_workflow_compiled_pattern_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "module_call" or case.kwargs or not case.use_compiled_pattern:
        return None
    if case.helper not in {"search", "match", "fullmatch"}:
        return None
    if not case.args:
        return None
    case_text_model = case.text_model or "str"
    return (
        f"module.{case.helper}",
        case_pattern(case),
        freeze_signature_value(list(case.args)),
        case.use_compiled_pattern,
        case.flags or 0,
        case_text_model,
    )


def _module_workflow_compiled_pattern_workload_args(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_module_workflow_compiled_pattern_workload(workload):
        raise AssertionError(
            "unexpected module-workflow compiled-pattern workload "
            f"{workload.workload_id!r}"
        )
    return (workload.haystack_payload(),)


def _module_workflow_compiled_pattern_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_module_workflow_compiled_pattern_workload(workload):
        raise AssertionError(
            "unexpected module-workflow compiled-pattern workload "
            f"{workload.workload_id!r}"
        )
    return (
        workload.operation,
        workload.pattern_payload(),
        freeze_signature_value(
            list(_module_workflow_compiled_pattern_workload_args(workload))
        ),
        workload.use_compiled_pattern,
        workload.flags,
        workload.text_model,
    )


def _is_module_workflow_compiled_pattern_workload(workload: Any) -> bool:
    return (
        not workload.kwargs
        and workload.use_compiled_pattern
        and workload.operation in _COMPILED_PATTERN_MODULE_HELPER_OPERATIONS
    )


def _is_module_workflow_compiled_pattern_literal_success_workload(
    workload: Any,
) -> bool:
    return (
        _is_module_workflow_compiled_pattern_workload(workload)
        and getattr(workload, "haystack_text_model", None) is None
        and workload.expected_exception is None
        and workload.pattern == "abc"
    )


def _is_module_workflow_compiled_pattern_bounded_wildcard_success_workload(
    workload: Any,
) -> bool:
    return (
        _is_module_workflow_compiled_pattern_workload(workload)
        and getattr(workload, "haystack_text_model", None) is None
        and workload.expected_exception is None
        and workload.pattern == "a.c"
        and workload.text_model in {"str", "bytes"}
    )


def _is_module_workflow_compiled_pattern_verbose_bytes_success_workload(
    workload: Any,
) -> bool:
    return (
        _is_module_workflow_compiled_pattern_workload(workload)
        and getattr(workload, "haystack_text_model", None) is None
        and workload.expected_exception is None
        and workload.pattern == _VERBOSE_REGRESSION_PATTERN
        and workload.flags == _VERBOSE_REGRESSION_FLAGS
        and workload.text_model == "bytes"
    )


def _assert_wrong_text_model_payload_round_trip(
    source_workload: Workload,
    payload: dict[str, object],
    round_tripped: Workload,
) -> None:
    expected_text_type = str if source_workload.text_model == "str" else bytes
    expected_haystack_type = (
        str if source_workload.haystack_text_model == "str" else bytes
    )

    assert payload["use_compiled_pattern"] is True
    assert round_tripped.use_compiled_pattern is True
    assert payload["timing_scope"] == "module-helper-call"
    assert round_tripped.timing_scope == "module-helper-call"
    assert payload["haystack_text_model"] == source_workload.haystack_text_model
    assert round_tripped.haystack_text_model == source_workload.haystack_text_model
    assert payload["expected_exception"] == source_workload.expected_exception
    assert round_tripped.expected_exception == source_workload.expected_exception
    assert isinstance(round_tripped.pattern_payload(), expected_text_type)
    assert isinstance(round_tripped.haystack_payload(), expected_haystack_type)
    if source_workload.replacement is not None:
        assert isinstance(round_tripped.replacement_payload(), expected_text_type)


def _is_collection_replacement_compiled_pattern_success_workload(
    workload: Any,
) -> bool:
    return (
        getattr(workload, "haystack_text_model", None) is None
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
        and workload.expected_exception is None
        and workload.pattern == "abc"
    )


@dataclass(frozen=True, slots=True)
class CompiledPatternModuleSuccessOwnerSpec:
    case_id: str
    manifest_path: Any
    include_workload_selectors: tuple[Callable[[Any], bool], ...]
    contract_manifest_id: str
    contract_filename: str
    note_surface: str
    expected_source_workload_ids: tuple[str, ...]
    preserved_payload_fields: tuple[str, ...]
    preserve_replacement_payload_typing: bool

    def source_workloads(self) -> tuple[Workload, ...]:
        return _contract_source_workloads(
            manifest_path=self.manifest_path,
            include_workload_selectors=self.include_workload_selectors,
            expected_source_workload_ids=self.expected_source_workload_ids,
            drift_message=(
                "compiled-pattern module contract source workloads drifted from the "
                f"{self.case_id} owner-spec surface"
            ),
        )

    def expected_build_calls(
        self,
        source_workload: Workload,
    ) -> list[tuple[object, ...]]:
        return compiled_pattern_contract_expected_build_calls(
            source_workload,
            label=f"{self.case_id} success",
        )

    def expected_callback_result(self, source_workload: Workload) -> object:
        callback_result, _, _, _ = _compiled_pattern_module_helper_route(
            source_workload,
            collection_replacement_callback_flags=source_workload.flags,
        )
        return callback_result

    def expected_callback_call(
        self,
        source_workload: Workload,
    ) -> tuple[object, ...]:
        _, callback_call, _, _ = _compiled_pattern_module_helper_route(
            source_workload,
            collection_replacement_callback_flags=source_workload.flags,
        )
        return callback_call

    def contract_builder_spec(self) -> _SourceTreeContractBuilderSpec:
        return source_tree_support._SourceTreeContractBuilderSpec(
            manifest_id=self.contract_manifest_id,
            excluded_fields=COMPILED_PATTERN_MODULE_SUCCESS_CONTRACT_EXCLUDED_FIELDS,
            timing_scope="module-helper-call",
            notes=(
                "Ensures benchmark manifests keep the bounded "
                "compiled-pattern-first-argument successful "
                f"{self.note_surface} rows unresolved until helper invocation.",
            ),
        )


def _assert_compiled_pattern_module_success_payload_round_trip(
    source_workload: Workload,
    payload: dict[str, object],
    round_tripped: Workload,
    *,
    owner_spec: CompiledPatternModuleSuccessOwnerSpec,
) -> None:
    expected_text_type = str if source_workload.text_model == "str" else bytes

    assert payload["use_compiled_pattern"] is True
    assert round_tripped.use_compiled_pattern is True
    assert payload.get("expected_exception") is None
    assert round_tripped.expected_exception is None
    assert payload.get("haystack_text_model") is None
    assert round_tripped.haystack_text_model is None
    assert isinstance(round_tripped.pattern_payload(), expected_text_type)
    assert isinstance(round_tripped.haystack_payload(), expected_text_type)
    for field_name in owner_spec.preserved_payload_fields:
        assert payload[field_name] == getattr(source_workload, field_name)
        assert getattr(round_tripped, field_name) == getattr(
            source_workload,
            field_name,
        )
    if (
        owner_spec.preserve_replacement_payload_typing
        and source_workload.replacement is not None
    ):
        assert isinstance(round_tripped.replacement_payload(), expected_text_type)


def _assert_compiled_pattern_success_rows_measured_in_combined_manifest(
    owner_spec: CompiledPatternModuleSuccessOwnerSpec,
    *,
    include_workload: Callable[[Any], bool],
) -> None:
    testcase = unittest.TestCase()
    manifest = load_manifest(owner_spec.manifest_path)
    expected_measured_workload_ids = tuple(
        workload.workload_id
        for workload in owner_spec.source_workloads()
        if include_workload(workload)
    )
    selected_measured_workload_ids = manifest_workload_ids_matching(
        manifest,
        include_workload,
    )

    assert selected_measured_workload_ids == expected_measured_workload_ids

    _, scorecard = run_harness_scorecard(
        "rebar_harness.benchmarks",
        ["--manifest", str(owner_spec.manifest_path)],
        report_name="benchmarks.json",
    )
    manifest_summary = scorecard["manifests"][owner_spec.contract_manifest_id]
    expected_workload_count = len(manifest.workloads)

    assert manifest_summary["known_gap_count"] == 0
    assert manifest_summary["measured_workloads"] == expected_workload_count
    assert manifest_summary["workload_count"] == expected_workload_count

    for workload_id in expected_measured_workload_ids:
        assert_benchmark_workload_contract(
            testcase,
            find_workload_record(scorecard, workload_id),
            manifest_id=owner_spec.contract_manifest_id,
            workload_document=find_workload_document(
                manifest,
                workload_id,
            ),
            expected_status="measured",
        )


def include_live_compiled_pattern_module_success_workload(workload: Workload) -> bool:
    return (
        workload.use_compiled_pattern
        and workload.expected_exception is None
        and getattr(workload, "haystack_text_model", None) is None
        and workload.operation.startswith("module.")
        and workload.operation != "module.compile"
        and not workload.kwargs
    )


_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC = (
    CompiledPatternModuleSuccessOwnerSpec(
        case_id="collection-replacement",
        manifest_path=COLLECTION_REPLACEMENT_MANIFEST_PATH,
        include_workload_selectors=(
            _is_collection_replacement_compiled_pattern_success_workload,
        ),
        contract_manifest_id="collection-replacement-boundary",
        contract_filename=(
            "python_benchmark_compiled_pattern_collection_replacement_success_contract.py"
        ),
        note_surface="collection/replacement",
        expected_source_workload_ids=(
            "module-split-literal-warm-str-compiled-pattern",
            "module-findall-literal-purged-bytes-compiled-pattern",
            "module-finditer-literal-warm-str-compiled-pattern",
            "module-sub-literal-warm-str-compiled-pattern",
            "module-subn-literal-purged-bytes-compiled-pattern",
        ),
        preserved_payload_fields=("count", "maxsplit"),
        preserve_replacement_payload_typing=True,
    )
)
_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC = (
    CompiledPatternModuleSuccessOwnerSpec(
        case_id="module-boundary",
        manifest_path=MODULE_BOUNDARY_MANIFEST_PATH,
        include_workload_selectors=(
            _is_module_workflow_compiled_pattern_literal_success_workload,
            _is_module_workflow_compiled_pattern_bounded_wildcard_success_workload,
            _is_module_workflow_compiled_pattern_verbose_bytes_success_workload,
        ),
        contract_manifest_id="module-boundary",
        contract_filename=(
            "python_benchmark_compiled_pattern_module_boundary_success_contract.py"
        ),
        note_surface="module-boundary",
        expected_source_workload_ids=(
            "module-search-literal-warm-hit-str-compiled-pattern",
            "module-match-literal-warm-hit-str-compiled-pattern",
            "module-fullmatch-literal-purged-hit-bytes-compiled-pattern",
            "module-search-bounded-wildcard-ignorecase-warm-hit-str-compiled-pattern",
            "module-match-bounded-wildcard-warm-hit-str-compiled-pattern",
            "module-fullmatch-bounded-wildcard-purged-hit-str-compiled-pattern",
            "module-search-verbose-regression-warm-hit-bytes-compiled-pattern",
            "module-fullmatch-verbose-regression-purged-hit-bytes-compiled-pattern",
        ),
        preserved_payload_fields=("flags",),
        preserve_replacement_payload_typing=False,
    )
)
_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS = (
    _COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC,
    _COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC,
)
_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS = (
    tuple(
        pytest.param(
            owner_spec,
            source_workload,
            id=f"{owner_spec.case_id}-{source_workload.workload_id}",
        )
        for owner_spec in _COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS
        for source_workload in owner_spec.source_workloads()
    )
)

COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS = (
    StandardBenchmarkAnchorContractDefinition(
        name="module-workflow-compiled-pattern-literal-success",
        manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            MODULE_BOUNDARY_MANIFEST_PATH,
            {
                "module-search-literal-warm-hit-str-compiled-pattern": (
                    "workflow-module-search-str-compiled-pattern",
                ),
                "module-match-literal-warm-hit-str-compiled-pattern": (
                    "workflow-module-match-str-compiled-pattern",
                ),
                "module-fullmatch-literal-purged-hit-bytes-compiled-pattern": (
                    "workflow-module-fullmatch-bytes-compiled-pattern",
                ),
            },
        ),
        include_workload=_is_module_workflow_compiled_pattern_literal_success_workload,
        correctness_case_signature=(
            _module_workflow_compiled_pattern_correctness_case_signature
        ),
        workload_signature=_module_workflow_compiled_pattern_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="module-workflow-compiled-pattern-bounded-wildcard-success",
        manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            MODULE_BOUNDARY_MANIFEST_PATH,
            {
                "module-search-bounded-wildcard-ignorecase-warm-hit-str-compiled-pattern": (
                    "workflow-module-search-str-bounded-wildcard-ignorecase-compiled-pattern",
                ),
                "module-match-bounded-wildcard-warm-hit-str-compiled-pattern": (
                    "workflow-module-match-str-bounded-wildcard-compiled-pattern",
                ),
                "module-fullmatch-bounded-wildcard-purged-hit-str-compiled-pattern": (
                    "workflow-module-fullmatch-str-bounded-wildcard-compiled-pattern",
                ),
            },
        ),
        include_workload=(
            _is_module_workflow_compiled_pattern_bounded_wildcard_success_workload
        ),
        correctness_case_signature=(
            _module_workflow_compiled_pattern_correctness_case_signature
        ),
        workload_signature=_module_workflow_compiled_pattern_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="module-workflow-compiled-pattern-verbose-bytes-success",
        manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            MODULE_BOUNDARY_MANIFEST_PATH,
            {
                "module-search-verbose-regression-warm-hit-bytes-compiled-pattern": (
                    "workflow-module-search-bytes-verbose-regression-compiled-pattern",
                ),
                "module-fullmatch-verbose-regression-purged-hit-bytes-compiled-pattern": (
                    "workflow-module-fullmatch-bytes-verbose-regression-compiled-pattern",
                ),
            },
        ),
        include_workload=_is_module_workflow_compiled_pattern_verbose_bytes_success_workload,
        correctness_case_signature=(
            _module_workflow_compiled_pattern_correctness_case_signature
        ),
        workload_signature=_module_workflow_compiled_pattern_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="module-workflow-compiled-pattern-wrong-text-model",
        manifest_paths=(MODULE_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            MODULE_BOUNDARY_MANIFEST_PATH,
            {
                "module-search-on-bytes-string-warm-str-compiled-pattern": (
                    "workflow-module-search-str-compiled-pattern-on-bytes-string",
                ),
                "module-match-on-str-string-purged-bytes-compiled-pattern": (
                    "workflow-module-match-bytes-compiled-pattern-on-str-string",
                ),
                "module-fullmatch-on-bytes-string-warm-str-compiled-pattern": (
                    "workflow-module-fullmatch-str-compiled-pattern-on-bytes-string",
                ),
            },
        ),
        include_workload=_is_module_workflow_compiled_pattern_wrong_text_model_workload,
        correctness_case_signature=(
            _module_workflow_compiled_pattern_correctness_case_signature
        ),
        workload_signature=_module_workflow_compiled_pattern_workload_signature,
    ),
)


def _is_collection_replacement_compiled_pattern_module_helper_keyword_workload(
    workload: Any,
) -> bool:
    return (
        _is_collection_replacement_keyword_workload(workload)
        and workload.use_compiled_pattern
        and workload.operation in {"module.split", "module.sub", "module.subn"}
        and workload.expected_exception is None
        and getattr(workload, "haystack_text_model", None) is None
    )


def _is_collection_replacement_compiled_pattern_keyword_error_workload(
    workload: Any,
) -> bool:
    return (
        _is_collection_replacement_keyword_workload(workload)
        and workload.use_compiled_pattern
        and workload.operation in {"module.split", "module.sub", "module.subn"}
        and workload.expected_exception is not None
        and getattr(workload, "haystack_text_model", None) is None
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
        if self.materializes_positional_keyword_field:
            field_names: list[str] = []
            positional_keyword_field = _collection_replacement_positional_keyword_field(
                source_workload
            )
            if positional_keyword_field is not None:
                field_names.append(positional_keyword_field)
            field_names.extend(f"kwargs.{name}" for name in source_workload.kwargs)
            return tuple(field_names)

        keyword_parameter = _collection_replacement_keyword_parameter_name(
            source_workload
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
        return source_tree_support._SourceTreeContractBuilderSpec(
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
        compiled_pattern = re.compile(workload.pattern_payload(), workload.flags)
        helper_name = workload.operation.removeprefix("module.")
        helper = getattr(re, helper_name)
        kwargs = dict(workload.kwargs)
        positional_keyword_field = _collection_replacement_positional_keyword_field(
            workload
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


_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC = (
    _CompiledPatternModuleHelperKeywordContractSpec(
        contract_filename=(
            "python_benchmark_compiled_pattern_collection_replacement_keyword_contract.py"
        ),
        expected_source_workload_ids=(
            "module-split-maxsplit-keyword-purged-str-compiled-pattern",
            "module-split-maxsplit-indexlike-keyword-purged-bytes-compiled-pattern",
            "module-split-maxsplit-bool-keyword-purged-bytes-compiled-pattern",
            "module-sub-count-keyword-warm-str-compiled-pattern",
            "module-sub-count-indexlike-keyword-warm-bytes-compiled-pattern",
            "module-sub-count-bool-keyword-warm-str-compiled-pattern",
            "module-sub-count-bool-false-keyword-warm-str-compiled-pattern",
            "module-subn-count-keyword-purged-bytes-compiled-pattern",
            "module-subn-count-indexlike-keyword-purged-str-compiled-pattern",
            "module-subn-count-bool-keyword-purged-bytes-compiled-pattern",
            "module-subn-count-bool-true-keyword-purged-bytes-compiled-pattern",
        ),
        manifest_timed_samples=2,
        preserve_expected_exception=False,
        materializes_positional_keyword_field=False,
        notes=(
            "Ensures benchmark manifests keep compiled-pattern-first-argument "
            "collection/replacement keyword carriers unresolved until helper "
            "invocation.",
        ),
        precompile_anchor_ids=(
            "module-split-maxsplit-keyword-purged-str-compiled-pattern",
            "module-sub-count-keyword-warm-str-compiled-pattern",
            "module-subn-count-keyword-purged-bytes-compiled-pattern",
        ),
    )
)

_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC = (
    _CompiledPatternModuleHelperKeywordContractSpec(
        contract_filename=(
            "python_benchmark_compiled_pattern_collection_replacement_keyword_error_contract.py"
        ),
        expected_source_workload_ids=(
            "module-split-duplicate-maxsplit-keyword-purged-str-compiled-pattern",
            "module-split-unexpected-keyword-purged-bytes-compiled-pattern",
            "module-sub-duplicate-count-keyword-warm-str-compiled-pattern",
            "module-sub-unexpected-keyword-purged-str-compiled-pattern",
            "module-sub-unexpected-keyword-after-positional-count-purged-str-compiled-pattern",
            "module-sub-count-alias-keyword-purged-str-compiled-pattern",
            "module-subn-duplicate-count-keyword-warm-bytes-compiled-pattern",
            "module-subn-unexpected-keyword-purged-bytes-compiled-pattern",
            "module-subn-unexpected-keyword-after-positional-count-purged-bytes-compiled-pattern",
            "module-subn-count-alias-keyword-purged-bytes-compiled-pattern",
        ),
        manifest_timed_samples=1,
        preserve_expected_exception=True,
        materializes_positional_keyword_field=True,
    )
)

_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS = (
    selected_manifest_workloads(
        COLLECTION_REPLACEMENT_MANIFEST_PATH,
        include_workload=(
            _is_collection_replacement_compiled_pattern_module_helper_keyword_workload
        ),
    )
)
if (
    tuple(
        workload.workload_id
        for workload in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS
    )
    != _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC.expected_source_workload_ids
):
    raise AssertionError(
        "compiled-pattern module-helper keyword contract source workloads drifted "
        "from the live source workload surface"
    )

_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS = tuple(
    workload
    for workload in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS
    if workload.workload_id
    in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC.precompile_anchor_ids
)
if (
    tuple(
        workload.workload_id
        for workload in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS
    )
    != _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC.precompile_anchor_ids
):
    raise AssertionError(
        "compiled-pattern module-helper keyword precompile anchors drifted "
        "from the live source workload surface"
    )

_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS = (
    selected_manifest_workloads(
        COLLECTION_REPLACEMENT_MANIFEST_PATH,
        include_workload=(
            _is_collection_replacement_compiled_pattern_keyword_error_workload
        ),
    )
)
if (
    tuple(
        workload.workload_id
        for workload in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS
    )
    != _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC.expected_source_workload_ids
):
    raise AssertionError(
        "compiled-pattern module-helper keyword-error source workloads drifted "
        "from the live source workload surface"
    )

_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES = (
    _CompiledPatternModuleHelperKeywordContractSurface(
        case_id="success",
        spec=_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC,
        source_workloads_value=_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS,
        precompile_source_workloads_value=(
            _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS
        ),
    ),
    _CompiledPatternModuleHelperKeywordContractSurface(
        case_id="keyword-error",
        spec=_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC,
        source_workloads_value=(
            _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS
        ),
    ),
)

_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACE_PARAMS = tuple(
    pytest.param(surface, id=surface.case_id)
    for surface in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES
)

_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS = tuple(
    pytest.param(
        surface,
        source_workload,
        id=f"{surface.case_id}-{source_workload.workload_id}",
    )
    for surface in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES
    for source_workload in surface.source_workloads()
)

_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS = tuple(
    pytest.param(
        surface,
        source_workload,
        id=f"{surface.case_id}-{source_workload.workload_id}",
    )
    for surface in _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES
    for source_workload in surface.precompile_source_workloads()
)


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
_PATTERN_BOUNDARY_OPERATIONS = frozenset(
    {"pattern.search", "pattern.match", "pattern.fullmatch"}
)
PATTERN_BOUNDARY_MANIFEST_PATH = benchmarks.BENCHMARK_WORKLOADS_ROOT / "pattern_boundary.py"
_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_EXCLUDED_FIELDS = frozenset(
    {
        "manifest_id",
        "workload_id",
        "warmup_iterations",
        "sample_iterations",
        "timed_samples",
        "smoke",
    }
)
_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS = (
    "pattern-search-on-bytes-string-warm-str",
    "pattern-match-on-str-string-purged-bytes",
    "pattern-fullmatch-on-bytes-string-warm-str",
)

def _pattern_boundary_wrong_text_model_source_workloads() -> tuple[Any, ...]:
    return _contract_source_workloads(
        manifest_path=PATTERN_BOUNDARY_MANIFEST_PATH,
        include_workload_selectors=(_is_pattern_boundary_wrong_text_model_workload,),
        expected_source_workload_ids=_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS,
        drift_message=(
            "direct Pattern pattern-boundary wrong-text-model surface drifted "
            "from the live source workload surface"
        ),
    )


def _pattern_boundary_wrong_text_model_expected_callback_call(
    source_workload: Any,
) -> tuple[object, ...]:
    if source_workload.operation in _PATTERN_BOUNDARY_OPERATIONS:
        return (
            source_workload.operation,
            source_workload.haystack_payload(),
            (),
            {},
        )
    raise AssertionError(
        "unexpected direct Pattern pattern-boundary wrong-text-model "
        f"workload operation {source_workload.operation!r}"
    )


def _run_cpython_pattern_boundary_wrong_text_model_workload(
    workload: Any,
) -> object:
    helper_name = workload.operation.removeprefix("pattern.")
    compiled_pattern = re.compile(workload.pattern_payload(), workload.flags)
    return getattr(compiled_pattern, helper_name)(workload.haystack_payload())


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


def _pattern_boundary_wrong_text_model_correctness_case_signature(
    case: Any,
) -> tuple[Any, ...] | None:
    if case.operation != "pattern_call" or case.kwargs:
        return None
    if case.helper not in {"search", "match", "fullmatch"}:
        return None
    case_args = list(case.args)
    if len(case_args) != 1:
        return None
    haystack = case_args[0]
    case_text_model = case.text_model or "str"
    if case_text_model == "str" and not isinstance(haystack, bytes):
        return None
    if case_text_model == "bytes" and not isinstance(haystack, str):
        return None
    return (
        f"pattern.{case.helper}",
        case_pattern(case),
        freeze_signature_value(case_args),
        (),
        case.flags or 0,
        case_text_model,
    )


def _pattern_boundary_wrong_text_model_workload_signature(
    workload: Any,
) -> tuple[Any, ...]:
    if not _is_pattern_boundary_wrong_text_model_workload(workload):
        raise AssertionError(
            "unexpected pattern-boundary wrong-text-model workload "
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


def _is_pattern_boundary_wrong_text_model_workload(workload: Any) -> bool:
    return (
        getattr(workload, "haystack_text_model", None) is not None
        and not workload.use_compiled_pattern
        and workload.operation in _PATTERN_BOUNDARY_OPERATIONS
        and workload.pos is None
        and workload.endpos is None
        and not workload.kwargs
        and workload.expected_exception is not None
        and workload.expected_exception.get("type") == "TypeError"
    )


PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITION_NAMES = (
    "pattern-window-positional-indexlike",
    "pattern-window-keyword",
    "pattern-boundary-bounded-wildcard",
    "pattern-boundary-verbose-regression",
    "pattern-boundary-wrong-text-model",
)


PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS = (
    StandardBenchmarkAnchorContractDefinition(
        name="pattern-window-positional-indexlike",
        manifest_paths=(PATTERN_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            PATTERN_BOUNDARY_MANIFEST_PATH,
            {
                "pattern-search-pos-indexlike-positional-warm-str": (
                    "workflow-pattern-search-str-pos-indexlike-positional",
                ),
                "pattern-search-endpos-indexlike-positional-purged-bytes": (
                    "workflow-pattern-search-bytes-endpos-indexlike-positional",
                ),
                "pattern-match-window-indexlike-positional-purged-bytes": (
                    "workflow-pattern-match-bytes-window-indexlike-positional",
                ),
                "pattern-fullmatch-window-indexlike-positional-purged-bytes": (
                    "workflow-pattern-fullmatch-bytes-window-indexlike-positional",
                ),
                "pattern-findall-window-indexlike-positional-warm-str": (
                    "workflow-pattern-findall-str-window-indexlike-positional",
                ),
                "pattern-finditer-window-indexlike-positional-purged-bytes": (
                    "workflow-pattern-finditer-bytes-window-indexlike-positional",
                ),
            },
        ),
        include_workload=_is_pattern_window_positional_indexlike_workload,
        correctness_case_signature=(
            _pattern_window_positional_indexlike_correctness_case_signature
        ),
        workload_signature=_pattern_window_positional_indexlike_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="pattern-window-keyword",
        manifest_paths=(PATTERN_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            PATTERN_BOUNDARY_MANIFEST_PATH,
            {
                "pattern-search-pos-keyword-warm-str": (
                    "workflow-pattern-search-str-pos-keyword",
                ),
                "pattern-search-bool-endpos-keyword-warm-str": (
                    "workflow-pattern-search-str-bool-endpos-keyword",
                ),
                "pattern-search-endpos-keyword-purged-bytes": (
                    "workflow-pattern-search-bytes-endpos-keyword",
                ),
                "pattern-search-pos-indexlike-keyword-warm-str": (
                    "workflow-pattern-search-str-pos-indexlike",
                ),
                "pattern-search-endpos-indexlike-keyword-purged-bytes": (
                    "workflow-pattern-search-bytes-endpos-indexlike",
                ),
                "pattern-match-pos-keyword-purged-str": (
                    "workflow-pattern-match-str-pos-keyword",
                ),
                "pattern-match-bool-pos-keyword-purged-str": (
                    "workflow-pattern-match-str-bool-pos-keyword",
                ),
                "pattern-match-window-indexlike-purged-bytes": (
                    "workflow-pattern-match-bytes-window-indexlike",
                ),
                "pattern-fullmatch-window-keyword-purged-bytes": (
                    "workflow-pattern-fullmatch-bytes-window-keyword",
                ),
                "pattern-fullmatch-window-indexlike-keyword-purged-bytes": (
                    "workflow-pattern-fullmatch-bytes-window-indexlike",
                ),
                "pattern-findall-window-keyword-warm-str": (
                    "workflow-pattern-findall-str-window-keyword",
                ),
                "pattern-findall-window-indexlike-keyword-warm-str": (
                    "workflow-pattern-findall-str-window-indexlike",
                ),
                "pattern-findall-bool-window-keyword-warm-str": (
                    "workflow-pattern-findall-str-bool-window-keyword",
                ),
                "pattern-finditer-window-keyword-purged-bytes": (
                    "workflow-pattern-finditer-bytes-window-keyword",
                ),
                "pattern-finditer-window-indexlike-purged-bytes": (
                    "workflow-pattern-finditer-bytes-window-indexlike",
                ),
                "pattern-finditer-bool-window-keyword-purged-bytes": (
                    "workflow-pattern-finditer-bytes-bool-window-keyword",
                ),
            },
        ),
        include_workload=_is_pattern_keyword_window_workload,
        correctness_case_signature=_pattern_keyword_window_correctness_case_signature,
        workload_signature=_pattern_keyword_window_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="pattern-boundary-bounded-wildcard",
        manifest_paths=(PATTERN_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            PATTERN_BOUNDARY_MANIFEST_PATH,
            {
                "pattern-search-bounded-wildcard-ignorecase-warm-str": (
                    "workflow-pattern-search-str-bounded-wildcard-ignorecase",
                ),
                "pattern-match-bounded-wildcard-warm-str": (
                    "workflow-pattern-match-str-bounded-wildcard",
                ),
                "pattern-fullmatch-bounded-wildcard-purged-str": (
                    "workflow-pattern-fullmatch-str-bounded-wildcard",
                ),
                "pattern-findall-bounded-wildcard-warm-str": (
                    "workflow-pattern-findall-str-bounded-wildcard",
                ),
                "pattern-finditer-bounded-wildcard-purged-str": (
                    "workflow-pattern-finditer-str-bounded-wildcard",
                ),
                "pattern-search-bounded-wildcard-endpos-miss-purged-str": (
                    "workflow-pattern-search-str-bounded-wildcard-endpos-miss",
                ),
            },
        ),
        include_workload=_is_pattern_bounded_wildcard_workload,
        correctness_case_signature=(
            _pattern_bounded_wildcard_correctness_case_signature
        ),
        workload_signature=_pattern_bounded_wildcard_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="pattern-boundary-verbose-regression",
        manifest_paths=(PATTERN_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            PATTERN_BOUNDARY_MANIFEST_PATH,
            {
                "pattern-search-verbose-regression-warm-str": (
                    "workflow-pattern-search-str-verbose-regression",
                ),
                "pattern-search-verbose-regression-digits-warm-str": (
                    "workflow-pattern-search-str-verbose-regression-digits",
                ),
                "pattern-search-verbose-regression-too-many-digits-purged-str": (
                    "workflow-pattern-search-str-verbose-regression-too-many-digits",
                ),
                "pattern-search-verbose-regression-warm-bytes": (
                    "workflow-pattern-search-bytes-verbose-regression",
                ),
                "pattern-search-verbose-regression-digits-warm-bytes": (
                    "workflow-pattern-search-bytes-verbose-regression-digits",
                ),
                "pattern-search-verbose-regression-too-many-digits-purged-bytes": (
                    "workflow-pattern-search-bytes-verbose-regression-too-many-digits",
                ),
                "pattern-fullmatch-verbose-regression-warm-str": (
                    "workflow-pattern-fullmatch-str-verbose-regression",
                ),
                "pattern-fullmatch-verbose-regression-alpha-warm-str": (
                    "workflow-pattern-fullmatch-str-verbose-regression-alpha",
                ),
                "pattern-fullmatch-verbose-regression-lowercase-key-purged-str": (
                    "workflow-pattern-fullmatch-str-verbose-regression-lowercase-key",
                ),
                "pattern-fullmatch-verbose-regression-warm-bytes": (
                    "workflow-pattern-fullmatch-bytes-verbose-regression",
                ),
                "pattern-fullmatch-verbose-regression-alpha-warm-bytes": (
                    "workflow-pattern-fullmatch-bytes-verbose-regression-alpha",
                ),
                "pattern-fullmatch-verbose-regression-lowercase-key-purged-bytes": (
                    "workflow-pattern-fullmatch-bytes-verbose-regression-lowercase-key",
                ),
            },
        ),
        include_workload=_is_pattern_verbose_regression_workload,
        correctness_case_signature=(
            _pattern_verbose_regression_correctness_case_signature
        ),
        workload_signature=_pattern_verbose_regression_workload_signature,
        run_callback_result_parity=True,
    ),
    StandardBenchmarkAnchorContractDefinition(
        name="pattern-boundary-wrong-text-model",
        manifest_paths=(PATTERN_BOUNDARY_MANIFEST_PATH,),
        expected_anchor_case_ids=_definition_anchor_expectations(
            PATTERN_BOUNDARY_MANIFEST_PATH,
            {
                "pattern-search-on-bytes-string-warm-str": (
                    "workflow-pattern-search-str-pattern-on-bytes-string",
                ),
                "pattern-match-on-str-string-purged-bytes": (
                    "workflow-pattern-match-bytes-pattern-on-str-string",
                ),
                "pattern-fullmatch-on-bytes-string-warm-str": (
                    "workflow-pattern-fullmatch-str-pattern-on-bytes-string",
                ),
            },
        ),
        include_workload=_is_pattern_boundary_wrong_text_model_workload,
        correctness_case_signature=(
            _pattern_boundary_wrong_text_model_correctness_case_signature
        ),
        workload_signature=_pattern_boundary_wrong_text_model_workload_signature,
    ),
)


from tests.benchmarks import (
    collection_replacement_benchmark_anchor_support as collection_replacement_support,
)
from tests.benchmarks import source_tree_benchmark_anchor_support as source_tree_support

_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_SPECS = {
    "collection-replacement-boundary": source_tree_support._SourceTreeContractBuilderSpec(
        manifest_id="collection-replacement-boundary",
        excluded_fields=COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS,
        timing_scope="module-helper-call",
        notes=(
            "Ensures benchmark manifests keep the bounded "
            "compiled-pattern-first-argument wrong-text-model "
            "collection/replacement rows unresolved until helper invocation.",
        ),
    ),
    "module-boundary": source_tree_support._SourceTreeContractBuilderSpec(
        manifest_id="module-boundary",
        excluded_fields=COMPILED_PATTERN_MODULE_CONTRACT_SHARED_EXCLUDED_FIELDS,
        timing_scope="module-helper-call",
        notes=(
            "Ensures benchmark manifests keep the bounded "
            "compiled-pattern-first-argument wrong-text-model "
            "module-boundary rows unresolved until helper invocation.",
        ),
    ),
}

_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC = (
    source_tree_support._SourceTreeContractBuilderSpec(
        manifest_id="pattern-boundary",
        excluded_fields=_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_EXCLUDED_FIELDS,
        timing_scope="pattern-helper-call",
    )
)

STANDARD_BENCHMARK_DEFINITIONS = (
    *COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS,
    *collection_replacement_support.COLLECTION_REPLACEMENT_STANDARD_BENCHMARK_DEFINITIONS,
    *MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS,
    *COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS,
    *COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS,
    *PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS,
    *source_tree_support.SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS,
)

BENCHMARK_MANIFEST_VALIDATION_RETIRED_OWNER_NAMES = frozenset(
    {
        "_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACE_PARAMS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_ANCHOR_SOURCE_WORKLOADS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS",
        "_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS",
        "_expected_exception_instance",
        "_is_collection_replacement_compiled_pattern_keyword_error_workload",
        "_is_pattern_boundary_wrong_text_model_workload",
        "_write_test_manifest",
        "CompiledPatternModuleCompileContractCase",
        "assert_benchmark_workload_matches_expected_result",
        "run_benchmark_workload_with_cpython",
        "assert_pattern_helper_wrong_text_model_payload_round_trip",
        "selected_manifest_workloads",
    }
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


def _standard_benchmark_manifest_params() -> tuple[Any, ...]:
    return tuple(
        pytest.param(
            definition,
            manifest_path,
            id=f"{definition.name}:{manifest_path.name}",
        )
        for definition in STANDARD_BENCHMARK_DEFINITIONS
        for manifest_path in definition.manifest_paths
    )


def _standard_benchmark_definition_params(
    *,
    include_definition: Callable[[StandardBenchmarkAnchorContractDefinition], bool],
) -> tuple[Any, ...]:
    return tuple(
        pytest.param(definition, id=definition.name)
        for definition in STANDARD_BENCHMARK_DEFINITIONS
        if include_definition(definition)
    )


def _standard_benchmark_definition_id(
    definition: StandardBenchmarkAnchorContractDefinition,
) -> str:
    return definition.name


def _standard_benchmark_special_unanchored_result_parity_params() -> tuple[Any, ...]:
    return tuple(
        pytest.param(
            definition,
            workload_id,
            id=f"{definition.name}:{workload_id}",
        )
        for definition in STANDARD_BENCHMARK_DEFINITIONS
        if definition.run_special_unanchored_result_parity
        for workload_id in definition.expected_special_unanchored_workload_ids
    )
