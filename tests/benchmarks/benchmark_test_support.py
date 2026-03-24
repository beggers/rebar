from __future__ import annotations

from functools import cache
import pathlib
import textwrap
from typing import Any

import pytest

from rebar_harness import benchmarks


def _resolve_live_manifest_path(
    manifest_path: pathlib.Path | str,
) -> pathlib.Path:
    if isinstance(manifest_path, pathlib.Path):
        return manifest_path
    return benchmarks.BENCHMARK_WORKLOADS_ROOT / manifest_path


@cache
def _live_manifest_workloads_by_id(
    manifest_path: pathlib.Path | str,
) -> dict[str, benchmarks.Workload]:
    return {
        workload.workload_id: workload
        for workload in benchmarks.load_manifest(
            _resolve_live_manifest_path(manifest_path)
        ).workloads
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
