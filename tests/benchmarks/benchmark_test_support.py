from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
import importlib
import json
import pathlib
import re
import sys
import textwrap
from functools import cache
from functools import partial
from types import SimpleNamespace
from typing import Any
import unittest

from rebar_harness import benchmarks
from rebar_harness.benchmarks import (
    BENCHMARK_WORKLOADS_ROOT,
    BenchmarkManifest,
    Workload,
    determine_phase,
    determine_runner_version,
    load_manifest,
    published_benchmark_manifests,
    workload_from_payload,
    workload_to_payload,
)
from rebar_harness.correctness import published_fixture_manifests
from rebar_harness.scorecard_io import build_cpython_baseline
from tests.conftest import REPO_ROOT, records_by_string_id
from tests.python.fixture_parity_support import (
    BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    OPEN_ENDED_ALTERNATION_BYTES_CASES,
    OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    assert_match_result_parity,
    assert_pattern_parity,
    case_pattern,
    case_replacement_argument,
    case_text_argument,
    callable_match_group_signature,
    module_workflow_keyword_kwargs_signature,
    module_workflow_positional_args_signature,
)

benchmark_test_support = sys.modules[__name__]


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
            published_cases_by_id,
        )
    )
    _clear_cached_functions(vars(benchmark_test_support).values())
    combined_suite = sys.modules.get(
        "tests.benchmarks.test_source_tree_combined_boundary_benchmarks"
    )
    if combined_suite is not None:
        _clear_cached_functions(vars(combined_suite).values())


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

def freeze_signature_value(value: Any) -> Any:
    if isinstance(value, dict):
        return tuple(
            (str(key), freeze_signature_value(nested_value))
            for key, nested_value in sorted(value.items())
        )
    if isinstance(value, list):
        return tuple(freeze_signature_value(item) for item in value)
    return value


COMPILE_MATRIX_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "compile_matrix.py"
REGRESSION_MATRIX_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "regression_matrix.py"
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


COLLECTION_REPLACEMENT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "collection_replacement_boundary.py"
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


# RBR-1421: merged from the deleted source-tree benchmark support module.

import ast
import json
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from functools import cache
from functools import partial
import importlib
import pathlib
import re
from types import SimpleNamespace
from typing import Any

import pytest

from rebar_harness import benchmarks
from rebar_harness.benchmarks import (
    BENCHMARK_WORKLOADS_ROOT,
    BenchmarkManifest,
    Workload,
    determine_phase,
    determine_runner_version,
    published_benchmark_manifests,
    workload_from_payload,
    workload_to_payload,
)
from tests.python.fixture_parity_support import (
    BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    OPEN_ENDED_ALTERNATION_BYTES_CASES,
    OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES,
    OPEN_ENDED_CONDITIONAL_BYTES_CASES,
    case_pattern,
    case_replacement_argument,
    case_text_argument,
    callable_match_group_signature,
    module_workflow_keyword_kwargs_signature,
    module_workflow_positional_args_signature,
)
