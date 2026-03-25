from __future__ import annotations

import ast
from functools import cache
import inspect
import pathlib
import re
import textwrap
from types import SimpleNamespace
from typing import Any
import unittest

import pytest

from rebar_harness import benchmarks
from rebar_harness.benchmarks import (
    BenchmarkManifest,
    Workload,
    load_manifest,
    workload_to_payload,
)


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


def _clear_anchor_support_caches() -> None:
    from tests.benchmarks import source_tree_benchmark_anchor_support as anchor_support

    cached_functions = (
        manifest_workloads,
        _live_manifest_workloads_by_id,
        anchor_support.published_case_ids_by_signature,
        anchor_support.published_cases_by_id,
    )
    for cached_function in cached_functions:
        cache_clear = getattr(cached_function, "cache_clear", None)
        if cache_clear is not None:
            cache_clear()


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
    module_tree = ast.parse(inspect.getsource(module))
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

    for workload_id in expected_measured_workload_ids:
        assert_benchmark_workload_contract(
            testcase,
            find_workload_record(scorecard, workload_id),
            manifest_id=manifest_id,
            workload_document=find_workload_document(manifest, workload_id),
            expected_status="measured",
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
