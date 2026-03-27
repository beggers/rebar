from __future__ import annotations

from collections.abc import Callable
from functools import cache
import json
import pathlib
import re
import shutil
import textwrap
from types import ModuleType
from typing import Any
from unittest import mock

import pytest

import rebar

from rebar_harness import benchmarks
from rebar_harness.benchmarks import (
    BENCHMARK_WORKLOADS_ROOT,
    BenchmarkManifest,
    PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR,
    Workload,
    load_manifest,
    published_benchmark_manifests,
    run_internal_workload_probe,
    select_benchmark_manifest_paths,
    workload_from_payload,
    workload_to_payload,
)


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
MATURIN = shutil.which("maturin")
_MISSING_MATURIN_REASON = (
    "built-native mode unavailable because no `maturin` executable was found on PATH"
)
_MISSING_MATURIN_PATTERN = "no `maturin` executable was found on PATH"
COMPILE_MATRIX_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "compile_matrix.py"
CONDITIONAL_GROUP_EXISTS_BOUNDARY_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "conditional_group_exists_boundary.py"
)
NESTED_GROUP_CALLABLE_REPLACEMENT_BOUNDARY_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "nested_group_callable_replacement_boundary.py"
)
_MISSING_GROUP_DEFAULT = object()


def duplicate_string_ids(items: tuple[str, ...] | list[str] | Any) -> tuple[str, ...]:
    counts: dict[str, int] = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    return tuple(sorted(item for item, count in counts.items() if count > 1))


def callable_match_group_signature(replacement: object) -> tuple[object, ...] | None:
    if not callable(replacement):
        return None
    kwdefaults = getattr(replacement, "__kwdefaults__", None)
    if not isinstance(kwdefaults, dict):
        return None
    return (
        getattr(replacement, "__qualname__", getattr(replacement, "__name__", None)),
        kwdefaults.get("_group_reference"),
        kwdefaults.get("_prefix"),
        kwdefaults.get("_suffix"),
    )


def assert_pattern_parity(
    backend_name: str,
    observed: object,
    expected: re.Pattern[str] | re.Pattern[bytes],
) -> None:
    if backend_name == "rebar":
        assert type(observed) is rebar.Pattern
    else:
        assert type(observed) is type(expected)

    assert observed.pattern == expected.pattern
    assert observed.flags == expected.flags
    assert observed.groups == expected.groups
    assert observed.groupindex == expected.groupindex


def _assert_match_parity(
    backend_name: str,
    observed: object,
    expected: re.Match[str] | re.Match[bytes],
    *,
    check_regs: bool = False,
) -> None:
    if backend_name == "rebar":
        assert type(observed) is rebar.Match
    else:
        assert type(observed) is type(expected)

    group_indexes = tuple(range(expected.re.groups + 1))
    mixed_group_references: list[tuple[object, ...]] = []
    if expected.re.groups >= 1:
        mixed_group_references.append((0, False, 1))

    group_names = tuple(expected.re.groupindex)
    if group_names:
        first_group_name = group_names[0]
        mixed_group_references.append((0, first_group_name))
        mixed_group_references.append((0, 1, first_group_name))

    assert observed.group(0) == expected.group(0)
    assert observed.group(*group_indexes) == expected.group(*group_indexes)
    for references in mixed_group_references:
        assert observed.group(*references) == expected.group(*references)
    for group_index in range(1, expected.re.groups + 1):
        assert observed.group(group_index) == expected.group(group_index)
        assert observed.span(group_index) == expected.span(group_index)
        assert observed.start(group_index) == expected.start(group_index)
        assert observed.end(group_index) == expected.end(group_index)

    assert observed.groups() == expected.groups()
    assert observed.groups(_MISSING_GROUP_DEFAULT) == expected.groups(
        _MISSING_GROUP_DEFAULT
    )
    assert observed.groupdict() == expected.groupdict()
    assert observed.groupdict(_MISSING_GROUP_DEFAULT) == expected.groupdict(
        _MISSING_GROUP_DEFAULT
    )
    assert observed.string == expected.string
    assert observed.pos == expected.pos
    assert observed.endpos == expected.endpos
    assert observed.span() == expected.span()
    assert observed.start() == expected.start()
    assert observed.end() == expected.end()
    assert observed.lastindex == expected.lastindex
    assert observed.lastgroup == expected.lastgroup
    if check_regs:
        assert hasattr(observed, "regs") == hasattr(expected, "regs")
        if hasattr(expected, "regs"):
            assert tuple(observed.regs) == tuple(expected.regs)
    assert_pattern_parity(backend_name, observed.re, expected.re)

    for group_name in expected.re.groupindex:
        assert observed.group(group_name) == expected.group(group_name)
        assert observed.span(group_name) == expected.span(group_name)
        assert observed.start(group_name) == expected.start(group_name)
        assert observed.end(group_name) == expected.end(group_name)


def assert_match_result_parity(
    backend_name: str,
    observed: object,
    expected: re.Match[str] | re.Match[bytes] | None,
    *,
    check_regs: bool = False,
) -> None:
    if expected is None:
        assert observed is None
        return

    assert observed is not None
    _assert_match_parity(
        backend_name,
        observed,
        expected,
        check_regs=check_regs,
    )


def _declared_string_constants_by_suffix(
    module: ModuleType,
    *,
    name_suffix: str,
) -> dict[str, str]:
    return {
        name: value
        for name, value in vars(module).items()
        if name.endswith(name_suffix) and isinstance(value, str)
    }


def _assert_declared_string_selector_registry_contract(
    module: ModuleType,
    *,
    name_suffix: str,
    selector_registry: dict[str, object],
) -> dict[str, str]:
    declared_selectors = _declared_string_constants_by_suffix(
        module,
        name_suffix=name_suffix,
    )

    assert declared_selectors
    assert len(declared_selectors) == len(set(declared_selectors.values()))
    assert set(declared_selectors.values()) == set(selector_registry)
    return declared_selectors


def _assert_published_selector_subset_paths_contract(
    published_full_suite_paths: tuple[pathlib.Path, ...],
    resolved_paths: tuple[pathlib.Path, ...],
    *,
    root_path: pathlib.Path,
    expected_filenames: tuple[str, ...] | None = None,
) -> None:
    assert resolved_paths
    assert len(resolved_paths) == len(set(resolved_paths))

    if expected_filenames is None:
        expected_ordered_subset = tuple(
            path for path in published_full_suite_paths if path in set(resolved_paths)
        )
    else:
        expected_filename_set = set(expected_filenames)
        assert len(expected_filenames) == len(expected_filename_set)
        expected_ordered_subset = tuple(
            path
            for path in published_full_suite_paths
            if path.name in expected_filename_set
        )
        assert tuple(path.name for path in expected_ordered_subset) == expected_filenames
        assert tuple(path.name for path in resolved_paths) == expected_filenames

    assert expected_ordered_subset
    assert len(expected_ordered_subset) == len(resolved_paths)
    assert resolved_paths == expected_ordered_subset

    for path in resolved_paths:
        assert path.is_relative_to(root_path)
        assert path.is_file()
        assert path.suffix == ".py"
        assert path in published_full_suite_paths


def _assert_published_manifest_helper_contract(
    published_loader: Callable[[], object],
    *,
    expected_paths: tuple[pathlib.Path, ...],
    expected_manifest_ids: tuple[str, ...] | None = None,
    observed_load_calls: list[tuple[pathlib.Path, ...]] | None = None,
) -> object:
    manifests = published_loader()

    assert published_loader() is manifests
    assert tuple(manifest.path for manifest in manifests) == expected_paths

    if expected_manifest_ids is not None:
        assert tuple(manifest.manifest_id for manifest in manifests) == expected_manifest_ids

    if observed_load_calls is not None:
        assert observed_load_calls == [expected_paths]

    return manifests


def _assert_published_manifest_helper_reload_contract(
    published_loader: Callable[[], object],
    *,
    clear_cache: Callable[[], None],
    expected_paths: tuple[pathlib.Path, ...],
    expected_manifest_ids: tuple[str, ...] | None = None,
    observed_load_calls: list[tuple[pathlib.Path, ...]] | None = None,
) -> object:
    clear_cache()
    try:
        return _assert_published_manifest_helper_contract(
            published_loader,
            expected_paths=expected_paths,
            expected_manifest_ids=expected_manifest_ids,
            observed_load_calls=observed_load_calls,
        )
    finally:
        clear_cache()


def _resolve_inventory_value(
    record: Any,
    accessor: str | Callable[[Any], Any],
) -> Any:
    if callable(accessor):
        return accessor(record)
    return getattr(record, accessor)


def _assert_published_manifest_inventory_contract(
    manifests: tuple[Any, ...],
    *,
    child_records: str | Callable[[Any], tuple[Any, ...]],
    child_id: str | Callable[[Any], str],
    extra_manifest_unique_fields: tuple[str | Callable[[Any], str], ...] = (),
    manifest_id: str | Callable[[Any], str] = "manifest_id",
    child_manifest_id: str | Callable[[Any], str] = "manifest_id",
) -> tuple[Any, ...]:
    assert manifests

    manifest_ids = tuple(
        _resolve_inventory_value(manifest, manifest_id)
        for manifest in manifests
    )
    assert duplicate_string_ids(manifest_ids) == ()

    for field in extra_manifest_unique_fields:
        assert duplicate_string_ids(
            _resolve_inventory_value(manifest, field) for manifest in manifests
        ) == ()

    child_entries = tuple(
        child
        for manifest in manifests
        for child in _resolve_inventory_value(manifest, child_records)
    )
    assert duplicate_string_ids(
        _resolve_inventory_value(child, child_id) for child in child_entries
    ) == ()

    manifest_ids_set = set(manifest_ids)
    child_counts_by_manifest = {
        current_manifest_id: 0 for current_manifest_id in manifest_ids
    }
    for child in child_entries:
        current_manifest_id = _resolve_inventory_value(child, child_manifest_id)
        assert current_manifest_id in manifest_ids_set
        child_counts_by_manifest[current_manifest_id] += 1

    for current_manifest_id in manifest_ids:
        assert child_counts_by_manifest[current_manifest_id] > 0

    return child_entries


def _resolve_manifest_path(manifest_path: pathlib.Path | str) -> pathlib.Path:
    if isinstance(manifest_path, pathlib.Path):
        return manifest_path
    return BENCHMARK_WORKLOADS_ROOT / manifest_path


@cache
def _manifest_workloads(manifest_path: pathlib.Path | str) -> tuple[Workload, ...]:
    return tuple(load_manifest(_resolve_manifest_path(manifest_path)).workloads)


def _live_manifest_workloads(
    manifest_path: pathlib.Path | str,
    workload_ids: tuple[str, ...],
) -> tuple[Workload, ...]:
    workloads_by_id = {
        workload.workload_id: workload
        for workload in _manifest_workloads(manifest_path)
    }
    return tuple(workloads_by_id[workload_id] for workload_id in workload_ids)


def _write_test_manifest(
    tmp_path: pathlib.Path,
    filename: str,
    source: str,
) -> pathlib.Path:
    path = tmp_path / filename
    path.write_text(textwrap.dedent(source), encoding="utf-8")
    return path


def _tracked_benchmark_manifest_paths() -> tuple[pathlib.Path, ...]:
    return tuple(sorted(BENCHMARK_WORKLOADS_ROOT.glob("*.py"), key=lambda path: path.name))


def _build_minimal_built_native_scorecard() -> dict[str, object]:
    return {
        "summary": {
            "total_workloads": 0,
            "parser_workloads": 0,
            "module_workloads": 0,
            "regression_workloads": 0,
            "measured_workloads": 0,
            "known_gap_count": 0,
        }
    }


def run_benchmark_workload_with_cpython(workload: Any) -> object:
    re.purge()
    try:
        callback = benchmarks.build_callable(re, "re", workload)
        return callback()
    finally:
        re.purge()


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


def _assert_built_native_runner_uses_optional_report_path(
    *,
    runner: Callable[..., dict[str, object]],
    expected_manifest_selector: str,
    expected_smoke_only: bool,
) -> None:
    expected_manifest_paths = select_benchmark_manifest_paths(expected_manifest_selector)
    scorecard = _build_minimal_built_native_scorecard()
    explicit_report_path = (
        REPO_ROOT / "reports" / "benchmarks" / "explicit-native-check.json"
    )

    with mock.patch.object(benchmarks, "run_benchmarks", return_value=scorecard) as mocked_run:
        returned = runner()

    assert returned is scorecard
    mocked_run.assert_called_once_with(
        manifest_paths=list(expected_manifest_paths),
        report_path=None,
        smoke_only=expected_smoke_only,
        adapter_mode=benchmarks.BUILT_NATIVE_MODE,
        allow_fallback=False,
    )

    with mock.patch.object(benchmarks, "run_benchmarks", return_value=scorecard) as mocked_run:
        returned = runner(report_path=explicit_report_path)

    assert returned is scorecard
    mocked_run.assert_called_once_with(
        manifest_paths=list(expected_manifest_paths),
        report_path=explicit_report_path,
        smoke_only=expected_smoke_only,
        adapter_mode=benchmarks.BUILT_NATIVE_MODE,
        allow_fallback=False,
    )


def _assert_built_native_cli_uses_optional_report_path(
    tmp_path: pathlib.Path,
    *,
    flag: str,
    runner_name: str,
    report_name: str,
) -> None:
    scorecard = _build_minimal_built_native_scorecard()

    with (
        mock.patch.object(benchmarks, runner_name, return_value=scorecard) as mocked_runner,
        mock.patch("builtins.print"),
    ):
        exit_code = benchmarks.main([flag])

    assert exit_code == 0
    mocked_runner.assert_called_once_with(report_path=None)

    report_path = tmp_path / report_name
    with (
        mock.patch.object(benchmarks, runner_name, return_value=scorecard) as mocked_runner,
        mock.patch("builtins.print"),
    ):
        exit_code = benchmarks.main([flag, "--report", str(report_path)])

    assert exit_code == 0
    mocked_runner.assert_called_once_with(report_path=report_path)


def _assert_built_native_mode_requires_real_built_runtime(
    report_path: pathlib.Path,
    *,
    runner: Callable[..., dict[str, object]],
) -> None:
    with mock.patch.object(
        benchmarks,
        "provision_built_native_runtime",
        return_value=(None, None, _MISSING_MATURIN_REASON),
    ):
        with pytest.raises(
            benchmarks.NativeBenchmarkProvisionError,
            match=_MISSING_MATURIN_PATTERN,
        ):
            runner(report_path=report_path)

    assert not report_path.exists()


def _assert_built_native_combined_scorecard_fields(
    scorecard: dict[str, object],
    *,
    expected_phase: str,
    expected_selection_mode: str,
    expected_manifest_count: int,
) -> None:
    implementation = scorecard["implementation"]
    environment = scorecard["environment"]
    artifacts = scorecard["artifacts"]

    assert scorecard["schema_version"] == "1.0"
    assert scorecard["phase"] == expected_phase
    assert implementation["module_name"] == "rebar"
    assert implementation["adapter_mode_requested"] == "built-native"
    assert implementation["adapter_mode_resolved"] == "built-native"
    assert implementation["build_mode"] == "built-native"
    assert implementation["timing_path"] == "built-native"
    assert implementation["native_module_loaded"] is True
    assert implementation["native_module_name"] == "rebar._rebar"
    assert implementation["native_build_tool"] == "maturin"
    assert str(implementation["native_wheel"]).startswith("rebar-")
    assert implementation["native_unavailable_reason"] is None
    assert (
        environment["execution_model"]
        == "single-interpreter subprocess workload probes against a built native wheel"
    )
    assert artifacts["manifest"] is None
    assert artifacts["manifest_id"] == "combined-benchmark-suite"
    assert artifacts["selection_mode"] == expected_selection_mode
    assert len(artifacts["manifests"]) == expected_manifest_count


def _summary_contract_workload_payload(
    *,
    manifest_id: str,
    workload_id: str,
    family: str = "module",
    operation: str | None = None,
    cache_mode: str = "warm",
    smoke: bool = False,
) -> dict[str, object]:
    resolved_operation = operation
    if resolved_operation is None:
        resolved_operation = "compile" if family == "parser" else "module.search"

    return {
        "manifest_id": manifest_id,
        "workload_id": workload_id,
        "bucket": workload_id,
        "family": family,
        "operation": resolved_operation,
        "pattern": "abc",
        "haystack": None if resolved_operation == "compile" else "abc",
        "replacement": None,
        "expected_exception": None,
        "flags": 0,
        "use_compiled_pattern": False,
        "count": 0,
        "maxsplit": 0,
        "pos": None,
        "endpos": None,
        "kwargs": {},
        "text_model": "str",
        "haystack_text_model": None,
        "cache_mode": cache_mode,
        "timing_scope": (
            "compile-call"
            if resolved_operation == "compile"
            else "module-helper-call"
        ),
        "warmup_iterations": 1,
        "sample_iterations": 1,
        "timed_samples": 1,
        "notes": [],
        "categories": [],
        "syntax_features": [],
        "smoke": smoke,
    }


def _summary_contract_workload_record(
    *,
    manifest_id: str,
    workload_id: str,
    family: str = "module",
    operation: str | None = None,
    cache_mode: str = "warm",
    status: str = "measured",
    baseline_ns: int | None = 100,
    implementation_ns: int | None = 80,
    speedup_vs_cpython: float | None = 1.25,
) -> dict[str, Any]:
    payload = _summary_contract_workload_payload(
        manifest_id=manifest_id,
        workload_id=workload_id,
        family=family,
        operation=operation,
        cache_mode=cache_mode,
    )
    if status != "measured":
        baseline_ns = None
        implementation_ns = None
        speedup_vs_cpython = None
    return {
        "manifest_id": payload["manifest_id"],
        "workload_id": payload["workload_id"],
        "family": payload["family"],
        "operation": payload["operation"],
        "cache_mode": payload["cache_mode"],
        "status": status,
        "baseline_ns": baseline_ns,
        "implementation_ns": implementation_ns,
        "speedup_vs_cpython": speedup_vs_cpython,
    }


def _summary_contract_manifest(
    *,
    manifest_id: str,
    workload_ids: tuple[str, ...],
    family: str = "module",
    operation: str | None = None,
    smoke_workload_ids: tuple[str, ...] = (),
    spec_refs: tuple[str, ...] = (),
    notes: tuple[str, ...] = (),
) -> BenchmarkManifest:
    smoke_workload_id_set = set(smoke_workload_ids)
    workloads = [
        workload_from_payload(
            _summary_contract_workload_payload(
                manifest_id=manifest_id,
                workload_id=workload_id,
                family=family,
                operation=operation,
                smoke=workload_id in smoke_workload_id_set,
            )
        )
        for workload_id in workload_ids
    ]
    return BenchmarkManifest(
        path=pathlib.Path(f"{manifest_id}.py"),
        manifest_id=manifest_id,
        schema_version=benchmarks.MANIFEST_SCHEMA_VERSION,
        workloads=workloads,
        spec_refs=list(spec_refs),
        notes=list(notes),
    )


def test_build_family_summary_marks_partial_parser_family_and_keeps_parser_proxy_note() -> None:
    summary = benchmarks.build_family_summary(
        [
            _summary_contract_workload_record(
                manifest_id="compile-matrix",
                workload_id="parser-measured",
                family="parser",
                cache_mode="cold",
                baseline_ns=120,
                implementation_ns=90,
                speedup_vs_cpython=1.3333,
            ),
            _summary_contract_workload_record(
                manifest_id="compile-matrix",
                workload_id="parser-gap",
                family="parser",
                cache_mode="warm",
                status="known-gap",
            ),
            _summary_contract_workload_record(
                manifest_id="module-boundary",
                workload_id="module-measured",
                family="module",
                cache_mode="warm",
                baseline_ns=200,
                implementation_ns=180,
                speedup_vs_cpython=1.1111,
            ),
        ],
        "parser",
    )

    assert summary["workload_count"] == 2
    assert summary["known_gap_count"] == 1
    assert summary["readiness"] == "partial"
    assert summary["median_baseline_ns"] == 120
    assert summary["median_implementation_ns"] == 90
    assert summary["median_speedup_vs_cpython"] == 1.3333
    assert summary["cache_modes"]["cold"] == {
        "workload_count": 1,
        "known_gap_count": 0,
        "median_baseline_ns": 120,
        "median_implementation_ns": 90,
        "median_speedup_vs_cpython": 1.3333,
    }
    assert summary["cache_modes"]["warm"] == {
        "workload_count": 1,
        "known_gap_count": 1,
        "median_baseline_ns": None,
        "median_implementation_ns": None,
        "median_speedup_vs_cpython": None,
    }
    assert summary["cache_modes"]["purged"] == {
        "workload_count": 0,
        "known_gap_count": 0,
        "median_baseline_ns": None,
        "median_implementation_ns": None,
        "median_speedup_vs_cpython": None,
    }
    assert summary["notes"] == [
        "Phase 1 compile-path suite uses compile() as a parser proxy until a narrower benchmark hook exists."
    ]


def test_build_family_summary_marks_absent_module_family_and_keeps_deferred_note() -> None:
    summary = benchmarks.build_family_summary(
        [
            _summary_contract_workload_record(
                manifest_id="compile-matrix",
                workload_id="parser-measured",
                family="parser",
                cache_mode="cold",
            )
        ],
        "module",
    )

    assert summary["workload_count"] == 0
    assert summary["known_gap_count"] == 0
    assert summary["readiness"] == "absent"
    assert summary["median_baseline_ns"] is None
    assert summary["median_implementation_ns"] is None
    assert summary["median_speedup_vs_cpython"] is None
    assert summary["cache_modes"] == {
        "cold": {
            "workload_count": 0,
            "known_gap_count": 0,
            "median_baseline_ns": None,
            "median_implementation_ns": None,
            "median_speedup_vs_cpython": None,
        },
        "warm": {
            "workload_count": 0,
            "known_gap_count": 0,
            "median_baseline_ns": None,
            "median_implementation_ns": None,
            "median_speedup_vs_cpython": None,
        },
        "purged": {
            "workload_count": 0,
            "known_gap_count": 0,
            "median_baseline_ns": None,
            "median_implementation_ns": None,
            "median_speedup_vs_cpython": None,
        },
    }
    assert summary["notes"] == ["Module-boundary timings remain deferred to RBR-0015."]


def test_build_family_summary_marks_scaffold_only_module_family_when_every_row_is_a_gap() -> None:
    summary = benchmarks.build_family_summary(
        [
            _summary_contract_workload_record(
                manifest_id="module-boundary",
                workload_id="module-gap",
                family="module",
                cache_mode="warm",
                status="known-gap",
            )
        ],
        "module",
    )

    assert summary["workload_count"] == 1
    assert summary["known_gap_count"] == 1
    assert summary["readiness"] == "scaffold-only"
    assert summary["median_baseline_ns"] is None
    assert summary["median_implementation_ns"] is None
    assert summary["median_speedup_vs_cpython"] is None
    assert summary["cache_modes"]["warm"] == {
        "workload_count": 1,
        "known_gap_count": 1,
        "median_baseline_ns": None,
        "median_implementation_ns": None,
        "median_speedup_vs_cpython": None,
    }
    assert summary["notes"] == [
        "Phase 2 module-boundary timings use tiny import and helper-call workloads so the scorecard stays focused on public API overhead."
    ]


def test_build_manifest_summaries_marks_empty_module_boundary_selection_absent() -> None:
    manifest = _summary_contract_manifest(
        manifest_id="module-boundary",
        workload_ids=("module-boundary-workload",),
        family="module",
        spec_refs=("spec:module-boundary",),
    )

    summary = benchmarks.build_manifest_summaries(
        manifests=[manifest],
        workloads=[],
        selection_mode="focused",
    )["module-boundary"]

    assert summary["workload_count"] == 1
    assert summary["selected_workload_count"] == 0
    assert summary["measured_workloads"] == 0
    assert summary["known_gap_count"] == 0
    assert summary["readiness"] == "absent"
    assert summary["median_speedup_vs_cpython"] is None
    assert summary["families"] == []
    assert summary["operations"] == []
    assert summary["selection_mode"] == "focused"
    assert summary["smoke_workload_ids"] == []
    assert summary["available_smoke_workload_count"] == 0
    assert summary["spec_refs"] == ["spec:module-boundary"]
    assert summary["notes"] == [
        "Module-boundary workloads keep haystacks intentionally small so the timings emphasize public helper overhead."
    ]


def test_build_manifest_summaries_marks_all_gap_regression_selection_scaffold_only() -> None:
    manifest = _summary_contract_manifest(
        manifest_id="regression-matrix",
        workload_ids=("regression-gap",),
        family="module",
        smoke_workload_ids=("regression-gap",),
        spec_refs=("spec:regression",),
    )

    summary = benchmarks.build_manifest_summaries(
        manifests=[manifest],
        workloads=[
            _summary_contract_workload_record(
                manifest_id="regression-matrix",
                workload_id="regression-gap",
                family="module",
                status="known-gap",
            )
        ],
        selection_mode="smoke",
    )["regression-matrix"]

    assert summary["workload_count"] == 1
    assert summary["selected_workload_count"] == 1
    assert summary["measured_workloads"] == 0
    assert summary["known_gap_count"] == 1
    assert summary["readiness"] == "scaffold-only"
    assert summary["median_speedup_vs_cpython"] is None
    assert summary["families"] == ["module"]
    assert summary["operations"] == ["module.search"]
    assert summary["selection_mode"] == "smoke"
    assert summary["smoke_workload_ids"] == ["regression-gap"]
    assert summary["available_smoke_workload_count"] == 1
    assert summary["spec_refs"] == ["spec:regression"]
    assert summary["notes"] == [
        "Regression/stability workloads track small, curated performance-cliff probes instead of broad engine-throughput claims."
    ]


def test_summary_contract_workload_payload_defaults_follow_family_shape() -> None:
    parser_payload = _summary_contract_workload_payload(
        manifest_id="compile-matrix",
        workload_id="parser-cold",
        family="parser",
        cache_mode="cold",
        smoke=True,
    )
    module_payload = _summary_contract_workload_payload(
        manifest_id="module-boundary",
        workload_id="module-fullmatch-warm",
        operation="module.fullmatch",
    )

    assert parser_payload == {
        "manifest_id": "compile-matrix",
        "workload_id": "parser-cold",
        "bucket": "parser-cold",
        "family": "parser",
        "operation": "compile",
        "pattern": "abc",
        "haystack": None,
        "replacement": None,
        "expected_exception": None,
        "flags": 0,
        "use_compiled_pattern": False,
        "count": 0,
        "maxsplit": 0,
        "pos": None,
        "endpos": None,
        "kwargs": {},
        "text_model": "str",
        "haystack_text_model": None,
        "cache_mode": "cold",
        "timing_scope": "compile-call",
        "warmup_iterations": 1,
        "sample_iterations": 1,
        "timed_samples": 1,
        "notes": [],
        "categories": [],
        "syntax_features": [],
        "smoke": True,
    }
    assert module_payload["operation"] == "module.fullmatch"
    assert module_payload["haystack"] == "abc"
    assert module_payload["timing_scope"] == "module-helper-call"
    assert module_payload["smoke"] is False


def test_summary_contract_workload_record_clears_timings_for_known_gaps() -> None:
    record = _summary_contract_workload_record(
        manifest_id="module-boundary",
        workload_id="module-gap",
        status="known-gap",
        baseline_ns=123,
        implementation_ns=45,
        speedup_vs_cpython=2.73,
    )

    assert record == {
        "manifest_id": "module-boundary",
        "workload_id": "module-gap",
        "family": "module",
        "operation": "module.search",
        "cache_mode": "warm",
        "status": "known-gap",
        "baseline_ns": None,
        "implementation_ns": None,
        "speedup_vs_cpython": None,
    }


def test_summary_contract_manifest_preserves_metadata_and_marks_smoke_workloads() -> None:
    manifest = _summary_contract_manifest(
        manifest_id="module-boundary",
        workload_ids=("search-cold", "search-smoke"),
        operation="module.match",
        smoke_workload_ids=("search-smoke",),
        spec_refs=("docs/spec-a.md",),
        notes=("owner helper manifest",),
    )

    assert manifest.manifest_id == "module-boundary"
    assert manifest.path == pathlib.Path("module-boundary.py")
    assert manifest.spec_refs == ["docs/spec-a.md"]
    assert manifest.notes == ["owner helper manifest"]
    assert [workload.workload_id for workload in manifest.workloads] == [
        "search-cold",
        "search-smoke",
    ]
    assert [workload.operation for workload in manifest.workloads] == [
        "module.match",
        "module.match",
    ]
    assert [workload.smoke for workload in manifest.workloads] == [False, True]


def _benchmark_manifest_selector_id(selector: str) -> str:
    return selector


def test_default_benchmark_manifest_selector_rejects_unknown_selector() -> None:
    with pytest.raises(ValueError, match="unknown benchmark manifest selector"):
        select_benchmark_manifest_paths("missing-selector")


def test_default_benchmark_published_full_suite_selector_covers_tracked_manifests() -> None:
    published_manifest_paths = select_benchmark_manifest_paths(
        PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR
    )
    tracked_manifest_paths = _tracked_benchmark_manifest_paths()

    assert set(published_manifest_paths) == set(tracked_manifest_paths)
    assert len(published_manifest_paths) == len(set(published_manifest_paths))

    for path in published_manifest_paths:
        assert path.is_relative_to(BENCHMARK_WORKLOADS_ROOT)
        assert path.is_file()
        assert path.suffix == ".py"


def test_standard_benchmark_manifest_selected_workloads_preserves_filters_and_order(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-selection-contract",
        "workloads": [
            {
                "id": "compile-literal-cold",
                "operation": "compile",
                "pattern": "abc",
            },
            {
                "id": "compile-smoke-flagged",
                "operation": "compile",
                "pattern": "def",
                "smoke": True,
            },
            {
                "id": "compile-smoke-categorized",
                "operation": "compile",
                "pattern": "ghi",
                "categories": ["smoke"],
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_selection_contract.py",
        manifest_source,
    )
    manifest = load_manifest(manifest_path)

    assert [workload.workload_id for workload in manifest.selected_workloads()] == [
        "compile-literal-cold",
        "compile-smoke-flagged",
        "compile-smoke-categorized",
    ]
    assert manifest.smoke_workload_ids() == [
        "compile-smoke-flagged",
        "compile-smoke-categorized",
    ]
    assert [
        workload.workload_id
        for workload in manifest.selected_workloads(
            selected_workload_ids=(
                "compile-smoke-categorized",
                "compile-literal-cold",
            )
        )
    ] == ["compile-smoke-categorized", "compile-literal-cold"]
    assert [
        workload.workload_id
        for workload in manifest.selected_workloads(
            selection_mode="smoke",
            selected_workload_ids=(
                "compile-smoke-categorized",
                "compile-literal-cold",
                "compile-smoke-flagged",
            ),
        )
    ] == ["compile-smoke-categorized", "compile-smoke-flagged"]

    with pytest.raises(
        AssertionError,
        match=(
            "missing workload definition 'missing-workload' in "
            "'python-benchmark-selection-contract'"
        ),
    ):
        manifest.selected_workloads(selected_workload_ids=("missing-workload",))

    with pytest.raises(
        AssertionError,
        match="unknown benchmark selection mode 'unknown'",
    ):
        manifest.selected_workloads(selection_mode="unknown")


def test_standard_benchmark_manifest_measures_expected_exception_workloads(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-exception-contract",
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 2,
            "text_model": "str",
            "cache_mode": "warm",
            "timing_scope": "module-helper-call",
        },
        "workloads": [
            {
                "id": "module-subn-callable-numbered-conditional-expected-exception-contract-str",
                "bucket": "module-subn",
                "family": "module",
                "operation": "module.subn",
                "pattern": r"a(b)?c(?(1)d|e)",
                "replacement": {
                    "type": "callable_match_group",
                    "group": 1,
                    "suffix": "x",
                },
                "expected_exception": {
                    "type": "TypeError",
                    "message_substring": "NoneType",
                },
                "haystack": "zzacezz",
                "count": 1,
                "categories": [
                    "replacement",
                    "callable",
                    "conditional",
                    "exception",
                    "str",
                ],
                "notes": [
                    "Ensures Python-backed benchmark manifests can measure expected callable replacement exceptions instead of failing the run."
                ],
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_exception_contract.py",
        manifest_source,
    )
    workloads = load_manifest(manifest_path).workloads

    workload = workloads[0]
    payload = workload_to_payload(workload)
    assert payload["expected_exception"] == {
        "type": "TypeError",
        "message_substring": "NoneType",
    }

    baseline_probe = run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name="re",
        adapter_name="cpython.re",
    )
    assert baseline_probe["status"] == "measured"
    assert baseline_probe["median_ns"] > 0

    implementation_probe = run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name="rebar",
        adapter_name="rebar",
    )
    assert implementation_probe["status"] == "measured"
    assert implementation_probe["median_ns"] > 0


@pytest.mark.parametrize(
    ("raised_exception", "expected_reason"),
    (
        pytest.param(
            ValueError("wrong exception"),
            (
                "AssertionError: workload "
                "'module-search-expected-exception-mismatch-contract' raised "
                "ValueError: wrong exception instead of the expected 'TypeError' "
                "exception"
            ),
            id="wrong-type",
        ),
        pytest.param(
            TypeError("wrong detail"),
            (
                "AssertionError: workload "
                "'module-search-expected-exception-mismatch-contract' raised "
                "TypeError: wrong detail instead of the expected 'TypeError' "
                "exception"
            ),
            id="wrong-message",
        ),
        pytest.param(
            None,
            (
                "AssertionError: workload "
                "'module-search-expected-exception-mismatch-contract' did not "
                "raise the expected 'TypeError' exception"
            ),
            id="missing-exception",
        ),
    ),
)
def test_run_internal_workload_probe_reports_expected_exception_mismatches_as_unavailable(
    monkeypatch,
    raised_exception: Exception | None,
    expected_reason: str,
) -> None:
    payload = {
        "manifest_id": "python-benchmark-expected-exception-mismatch-contract",
        "workload_id": "module-search-expected-exception-mismatch-contract",
        "bucket": "module-search",
        "family": "module",
        "operation": "module.search",
        "pattern": "abc",
        "haystack": "abc",
        "flags": 0,
        "count": 0,
        "maxsplit": 0,
        "expected_exception": {
            "type": "TypeError",
            "message_substring": "expected detail",
        },
        "text_model": "str",
        "cache_mode": "warm",
        "timing_scope": "module-helper-call",
        "warmup_iterations": 1,
        "sample_iterations": 1,
        "timed_samples": 1,
        "notes": [],
        "categories": [],
        "syntax_features": [],
        "smoke": False,
    }

    def fake_build_callable(module: Any, import_name: str, workload: Any) -> Any:
        del module, import_name, workload

        def callback() -> None:
            if raised_exception is not None:
                raise raised_exception
            return None

        return callback

    monkeypatch.setattr(benchmarks, "build_callable", fake_build_callable)

    probe = run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name="re",
        adapter_name="cpython.re",
    )

    assert probe == {
        "adapter": "cpython.re",
        "status": "unavailable",
        "reason": expected_reason,
    }


@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
def test_run_internal_workload_probe_reports_unsupported_operations_as_unavailable(
    tmp_path: pathlib.Path,
    import_name: str,
    adapter_name: str,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-unsupported-operation-contract",
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
        },
        "workloads": [
            {
                "id": "module-escape-unsupported-operation-contract",
                "bucket": "module-escape",
                "family": "module",
                "operation": "module.escape",
                "pattern": "abc",
                "haystack": "abcabc",
                "notes": [
                    "Ensures the internal benchmark probe reports unsupported workload operations as unavailable diagnostics instead of crashing."
                ],
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_unsupported_operation_contract.py",
        manifest_source,
    )
    (workload,) = load_manifest(manifest_path).workloads

    assert run_internal_workload_probe(
        workload_payload=json.dumps(workload_to_payload(workload), sort_keys=True),
        import_name=import_name,
        adapter_name=adapter_name,
    ) == {
        "adapter": adapter_name,
        "status": "unavailable",
        "reason": "ValueError: unsupported benchmark operation 'module.escape'",
    }


@cache
def _nested_group_callable_replacement_quantified_branch_local_backreference_bytes_workloads(
) -> tuple[Workload, ...]:
    return _live_manifest_workloads(
        NESTED_GROUP_CALLABLE_REPLACEMENT_BOUNDARY_MANIFEST_PATH,
        (
            "module-sub-callable-numbered-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-bytes",
            "module-subn-callable-numbered-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-bytes",
            "pattern-sub-callable-named-quantified-nested-group-alternation-branch-local-backreference-mixed-branches-purged-bytes",
            "pattern-subn-callable-named-quantified-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-bytes",
        ),
    )


_NESTED_GROUP_CALLABLE_REPLACEMENT_QUANTIFIED_BRANCH_LOCAL_BACKREFERENCE_BYTES_WORKLOAD_PARAMS = tuple(
    pytest.param(workload, id=workload.workload_id)
    for workload in (
        _nested_group_callable_replacement_quantified_branch_local_backreference_bytes_workloads()
    )
)


@pytest.mark.parametrize(
    "source_workload",
    _NESTED_GROUP_CALLABLE_REPLACEMENT_QUANTIFIED_BRANCH_LOCAL_BACKREFERENCE_BYTES_WORKLOAD_PARAMS,
)
def test_nested_group_callable_replacement_quantified_branch_local_backreference_bytes_workloads_round_trip_preserves_callback_results(
    source_workload: Workload,
) -> None:
    payload = workload_to_payload(source_workload)
    round_tripped = workload_from_payload(payload)

    assert payload["text_model"] == "bytes"
    assert round_tripped.text_model == "bytes"
    assert round_tripped.pattern_payload() == source_workload.pattern_payload()
    assert round_tripped.haystack_payload() == source_workload.haystack_payload()

    assert_benchmark_workload_matches_expected_result(
        round_tripped,
        run_benchmark_workload_with_cpython(source_workload),
    )


@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
@pytest.mark.parametrize(
    "source_workload",
    _NESTED_GROUP_CALLABLE_REPLACEMENT_QUANTIFIED_BRANCH_LOCAL_BACKREFERENCE_BYTES_WORKLOAD_PARAMS,
)
def test_run_internal_workload_probe_measures_nested_group_callable_replacement_quantified_branch_local_backreference_bytes_workloads(
    source_workload: Workload,
    import_name: str,
    adapter_name: str,
) -> None:
    payload = workload_to_payload(source_workload)
    round_tripped = workload_from_payload(payload)

    assert round_tripped.text_model == "bytes"
    probe = run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name=import_name,
        adapter_name=adapter_name,
    )

    assert probe["status"] == "measured"
    assert probe["median_ns"] > 0


@cache
def _conditional_group_exists_callable_negative_count_str_workloads() -> tuple[Workload, ...]:
    manifest = load_manifest(
        CONDITIONAL_GROUP_EXISTS_BOUNDARY_MANIFEST_PATH
    )
    workload_ids = tuple(
        workload.workload_id
        for workload in manifest.workloads
        if workload.count == -1
        and workload.text_model == "str"
        and workload.operation
        in {"module.sub", "module.subn", "pattern.sub", "pattern.subn"}
        and workload.expected_exception is None
        and workload.pattern in {
            r"a(b)?c(?(1)d|e)",
            r"a(?P<word>b)?c(?(word)d|e)",
        }
        and workload.replacement == {
            "type": "callable_match_group",
            "group": ("word" if "-named-" in workload.workload_id else 1),
            "suffix": "x",
        }
    )
    return _live_manifest_workloads(
        CONDITIONAL_GROUP_EXISTS_BOUNDARY_MANIFEST_PATH,
        workload_ids,
    )


@cache
def _conditional_group_exists_callable_none_count_workloads() -> tuple[Workload, ...]:
    manifest = load_manifest(
        CONDITIONAL_GROUP_EXISTS_BOUNDARY_MANIFEST_PATH
    )
    workload_ids = tuple(
        workload.workload_id
        for workload in manifest.workloads
        if workload.count is None
        and workload.operation
        in {"module.sub", "module.subn", "pattern.sub", "pattern.subn"}
        and workload.expected_exception == {
            "type": "TypeError",
            "message_substring": "NoneType",
        }
    )
    return _live_manifest_workloads(
        CONDITIONAL_GROUP_EXISTS_BOUNDARY_MANIFEST_PATH,
        workload_ids,
    )


def _conditional_group_exists_callable_none_count_workloads_for_text_model(
    text_model: str,
) -> tuple[Workload, ...]:
    return tuple(
        workload
        for workload in _conditional_group_exists_callable_none_count_workloads()
        if workload.text_model == text_model
        and workload.replacement
        == {
            "type": "callable_match_group",
            "group": ("word" if "-named-" in workload.workload_id else 1),
            "suffix": "x",
        }
    )


def _conditional_group_exists_callable_none_count_workload_ids(
    text_model: str,
) -> tuple[str, ...]:
    return (
        f"module-sub-callable-numbered-conditional-group-exists-replacement-none-count-warm-{text_model}",
        f"pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-purged-{text_model}",
        f"module-sub-callable-named-conditional-group-exists-replacement-none-count-warm-{text_model}",
        f"pattern-sub-callable-named-conditional-group-exists-replacement-none-count-purged-{text_model}",
        f"module-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-warm-{text_model}",
        f"pattern-subn-callable-numbered-conditional-group-exists-replacement-none-count-absent-exception-purged-{text_model}",
        f"module-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-warm-{text_model}",
        f"pattern-subn-callable-named-conditional-group-exists-replacement-none-count-absent-exception-purged-{text_model}",
        f"module-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-warm-{text_model}",
        f"module-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-warm-{text_model}",
        f"pattern-sub-callable-numbered-conditional-group-exists-replacement-none-count-negative-count-purged-{text_model}",
        f"pattern-subn-callable-named-conditional-group-exists-replacement-none-count-negative-count-purged-{text_model}",
        f"module-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-{text_model}",
        f"module-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-warm-{text_model}",
        f"pattern-sub-callable-numbered-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-{text_model}",
        f"pattern-subn-callable-named-conditional-group-exists-alternation-heavy-replacement-none-count-negative-count-purged-{text_model}",
        f"module-sub-callable-numbered-nested-conditional-group-exists-replacement-none-count-negative-count-warm-{text_model}",
        f"module-subn-callable-named-nested-conditional-group-exists-replacement-none-count-negative-count-warm-{text_model}",
        f"pattern-sub-callable-numbered-nested-conditional-group-exists-replacement-none-count-negative-count-purged-{text_model}",
        f"pattern-subn-callable-named-nested-conditional-group-exists-replacement-none-count-negative-count-purged-{text_model}",
        f"module-sub-callable-numbered-quantified-conditional-group-exists-replacement-none-count-warm-{text_model}",
        f"module-subn-callable-named-quantified-conditional-group-exists-replacement-none-count-absent-exception-warm-{text_model}",
        f"pattern-sub-callable-numbered-quantified-conditional-group-exists-replacement-none-count-purged-{text_model}",
        f"pattern-subn-callable-named-quantified-conditional-group-exists-replacement-none-count-absent-exception-purged-{text_model}",
    )


_CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_PARAMS = tuple(
    pytest.param(workload, id=workload.workload_id)
    for workload in _conditional_group_exists_callable_none_count_workloads()
)


def test_conditional_group_exists_callable_negative_count_str_workloads_round_trip_preserves_suffix_only_callback_payloads(
) -> None:
    workloads = _conditional_group_exists_callable_negative_count_str_workloads()

    assert tuple(workload.workload_id for workload in workloads) == (
        "module-sub-callable-numbered-conditional-group-exists-replacement-negative-count-warm-str",
        "module-subn-callable-named-conditional-group-exists-replacement-negative-count-warm-str",
        "pattern-sub-callable-numbered-conditional-group-exists-replacement-negative-count-purged-str",
        "pattern-subn-callable-named-conditional-group-exists-replacement-negative-count-purged-str",
    )

    for workload in workloads:
        expected_replacement = {
            "type": "callable_match_group",
            "group": "word" if "-named-" in workload.workload_id else 1,
            "suffix": "x",
        }
        expected_result = (
            ("abcdaceabcd", 0)
            if "-subn-" in workload.workload_id
            else "abcdaceabcd"
        )

        payload = workload_to_payload(workload)
        round_tripped = workload_from_payload(payload)

        assert workload.text_model == "str"
        assert payload["text_model"] == "str"
        assert payload["replacement"] == expected_replacement
        assert payload["count"] == -1
        assert callable_match_group_signature(workload.replacement_payload()) == (
            "callable_match_group",
            expected_replacement["group"],
            "",
            "x",
        )
        assert (
            run_benchmark_workload_with_cpython(workload)
            == expected_result
        )

        assert round_tripped.text_model == "str"
        assert round_tripped.count == -1
        assert callable_match_group_signature(round_tripped.replacement_payload()) == (
            "callable_match_group",
            expected_replacement["group"],
            "",
            "x",
        )
        assert (
            run_benchmark_workload_with_cpython(round_tripped)
            == expected_result
        )


@pytest.mark.parametrize(
    ("text_model", "expected_prefix", "expected_suffix"),
    (
        pytest.param("str", "", "x", id="str"),
        pytest.param("bytes", b"", b"x", id="bytes"),
    ),
)
def test_conditional_group_exists_callable_none_count_workloads_round_trip_preserves_suffix_only_callback_payloads(
    text_model: str,
    expected_prefix: str | bytes,
    expected_suffix: str | bytes,
) -> None:
    workloads = _conditional_group_exists_callable_none_count_workloads_for_text_model(
        text_model
    )

    assert tuple(workload.workload_id for workload in workloads) == (
        _conditional_group_exists_callable_none_count_workload_ids(text_model)
    )

    for workload in workloads:
        expected_replacement = {
            "type": "callable_match_group",
            "group": "word" if "-named-" in workload.workload_id else 1,
            "suffix": "x",
        }

        payload = workload_to_payload(workload)
        round_tripped = workload_from_payload(payload)
        expected_exception = workload.expected_exception

        assert workload.text_model == text_model
        assert payload["text_model"] == text_model
        assert payload["replacement"] == expected_replacement
        assert payload["count"] is None
        assert workload.count is None
        assert callable_match_group_signature(workload.replacement_payload()) == (
            "callable_match_group",
            expected_replacement["group"],
            expected_prefix,
            expected_suffix,
        )

        assert round_tripped.text_model == text_model
        assert round_tripped.count is None
        assert callable_match_group_signature(round_tripped.replacement_payload()) == (
            "callable_match_group",
            expected_replacement["group"],
            expected_prefix,
            expected_suffix,
        )

        assert expected_exception is not None
        with pytest.raises(
            TypeError,
            match=re.escape(expected_exception["message_substring"]),
        ) as expected_error:
            run_benchmark_workload_with_cpython(workload)
        with pytest.raises(TypeError) as observed_error:
            run_benchmark_workload_with_cpython(round_tripped)
        assert str(observed_error.value) == str(expected_error.value)


def test_conditional_group_exists_callable_none_count_workload_slice_keeps_runtime_contract_span(
) -> None:
    workloads = _conditional_group_exists_callable_none_count_workloads()

    assert workloads
    assert {workload.operation for workload in workloads} == {
        "module.sub",
        "module.subn",
        "pattern.sub",
        "pattern.subn",
    }
    assert {workload.text_model for workload in workloads} == {"str", "bytes"}
    assert {workload.cache_mode for workload in workloads} == {"warm", "purged"}
    assert all(workload.count is None for workload in workloads)
    assert all(not workload.use_compiled_pattern for workload in workloads)
    assert all(
        workload.expected_exception
        == {
            "type": "TypeError",
            "message_substring": "NoneType",
        }
        for workload in workloads
    )


@pytest.mark.parametrize(
    "source_workload",
    _CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_PARAMS,
)
def test_conditional_group_exists_callable_none_count_workloads_round_trip_preserves_expected_exception_contract(
    source_workload: Workload,
) -> None:
    payload = workload_to_payload(source_workload)
    round_tripped = workload_from_payload(payload)
    expected_exception = source_workload.expected_exception

    assert expected_exception is not None
    assert payload["count"] is None
    assert payload["expected_exception"] == expected_exception
    assert round_tripped.count is None
    assert round_tripped.count_argument() is None
    assert round_tripped.expected_exception == expected_exception
    assert round_tripped.text_model == source_workload.text_model
    assert round_tripped.pattern_payload() == source_workload.pattern_payload()
    assert round_tripped.haystack_payload() == source_workload.haystack_payload()
    assert callable(round_tripped.replacement_payload())

    with pytest.raises(
        TypeError,
        match=re.escape(expected_exception["message_substring"]),
    ):
        run_benchmark_workload_with_cpython(round_tripped)


@pytest.mark.parametrize(
    ("import_name", "adapter_name"),
    (
        pytest.param("re", "cpython.re", id="cpython"),
        pytest.param("rebar", "rebar", id="rebar"),
    ),
)
@pytest.mark.parametrize(
    "source_workload",
    _CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_PARAMS,
)
def test_run_internal_workload_probe_measures_conditional_group_exists_callable_none_count_workloads(
    source_workload: Workload,
    import_name: str,
    adapter_name: str,
) -> None:
    payload = workload_to_payload(source_workload)

    assert payload["count"] is None
    probe = run_internal_workload_probe(
        workload_payload=json.dumps(payload, sort_keys=True),
        import_name=import_name,
        adapter_name=adapter_name,
    )

    assert probe["status"] == "measured"
    assert probe["adapter"] == adapter_name
    assert probe["median_ns"] > 0


@pytest.mark.parametrize(
    "selector",
    tuple(benchmarks._NONDEFAULT_BENCHMARK_MANIFEST_SELECTOR_REQUESTED_FILENAMES),
    ids=_benchmark_manifest_selector_id,
)
def test_shared_benchmark_manifest_selectors_resolve_published_subset_invariants(
    selector: str,
) -> None:
    published_manifest_paths = select_benchmark_manifest_paths(
        PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR
    )
    selected_paths = select_benchmark_manifest_paths(selector)

    _assert_published_selector_subset_paths_contract(
        published_manifest_paths,
        selected_paths,
        root_path=BENCHMARK_WORKLOADS_ROOT,
        expected_filenames=benchmarks._BENCHMARK_MANIFEST_FILENAMES_BY_SELECTOR[
            selector
        ],
    )


def test_built_native_smoke_manifest_selector_keeps_membership_contract() -> None:
    selector = benchmarks.BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR
    expected_filenames = (
        benchmarks._NONDEFAULT_BENCHMARK_MANIFEST_SELECTOR_REQUESTED_FILENAMES[
            selector
        ]
    )
    assert benchmarks._BENCHMARK_MANIFEST_FILENAMES_BY_SELECTOR[selector] == expected_filenames

    _assert_published_selector_subset_paths_contract(
        select_benchmark_manifest_paths(PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR),
        select_benchmark_manifest_paths(selector),
        root_path=BENCHMARK_WORKLOADS_ROOT,
        expected_filenames=expected_filenames,
    )


def test_benchmark_selector_subset_helper_keeps_benchmark_specific_missing_filename_error() -> None:
    with pytest.raises(
        ValueError,
        match=re.escape(
            "unknown published benchmark manifest filename(s): ['missing_boundary.py']"
        ),
    ):
        benchmarks._ordered_published_benchmark_manifest_filenames(
            ("missing_boundary.py",)
        )


def test_declared_benchmark_manifest_selectors_match_registry_keys() -> None:
    declared_selectors = _assert_declared_string_selector_registry_contract(
        benchmarks,
        name_suffix="_MANIFEST_SELECTOR",
        selector_registry=benchmarks._BENCHMARK_MANIFEST_FILENAMES_BY_SELECTOR,
    )

    assert declared_selectors


def test_declared_nondefault_benchmark_manifest_selectors_are_parametrized_once() -> None:
    declared_nondefault_selectors = tuple(
        sorted(
            selector
            for selector in _declared_string_constants_by_suffix(
                benchmarks,
                name_suffix="_MANIFEST_SELECTOR",
            ).values()
            if selector != PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR
        )
    )
    expected_selectors = tuple(
        sorted(benchmarks._NONDEFAULT_BENCHMARK_MANIFEST_SELECTOR_REQUESTED_FILENAMES)
    )

    assert PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR not in expected_selectors
    assert len(expected_selectors) == len(set(expected_selectors))
    assert expected_selectors == declared_nondefault_selectors


def test_default_benchmark_published_manifest_helper_is_cached_and_preserves_selector_order() -> None:
    published_manifest_paths = select_benchmark_manifest_paths(
        PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR
    )

    _assert_published_manifest_helper_contract(
        published_benchmark_manifests,
        expected_paths=published_manifest_paths,
    )


def test_published_benchmark_manifests_cache_clear_reloads_current_default_selector(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pathlib.Path,
) -> None:
    first_path = _write_test_manifest(
        tmp_path,
        "cached_benchmark_manifest_a.py",
        """
        MANIFEST = {
            "schema_version": 1,
            "manifest_id": "cached-benchmark-manifest-a",
            "workloads": [
                {
                    "id": "cached-benchmark-workload-a",
                    "operation": "module.search",
                    "pattern": "abc",
                    "haystack": "zabc",
                },
            ],
        }
        """,
    )
    second_path = _write_test_manifest(
        tmp_path,
        "cached_benchmark_manifest_b.py",
        """
        MANIFEST = {
            "schema_version": 1,
            "manifest_id": "cached-benchmark-manifest-b",
            "workloads": [
                {
                    "id": "cached-benchmark-workload-b",
                    "operation": "module.search",
                    "pattern": "def",
                    "haystack": "zdef",
                },
            ],
        }
        """,
    )
    requested_paths = (second_path, first_path)
    loader_calls: list[tuple[pathlib.Path, ...]] = []
    real_load_manifests = benchmarks.load_manifests

    def _recording_selector(selector: str) -> tuple[pathlib.Path, ...]:
        assert selector == PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR
        return requested_paths

    def _recording_loader(paths: list[pathlib.Path]) -> list[object]:
        loader_calls.append(tuple(paths))
        return real_load_manifests(paths)

    monkeypatch.setattr(benchmarks, "select_benchmark_manifest_paths", _recording_selector)
    monkeypatch.setattr(benchmarks, "load_manifests", _recording_loader)
    _assert_published_manifest_helper_reload_contract(
        published_benchmark_manifests,
        clear_cache=benchmarks.published_benchmark_manifests.cache_clear,
        expected_paths=requested_paths,
        expected_manifest_ids=(
            "cached-benchmark-manifest-b",
            "cached-benchmark-manifest-a",
        ),
        observed_load_calls=loader_calls,
    )


def test_default_benchmark_published_manifest_inventory_has_unique_manifest_and_workload_ids() -> None:
    manifests = published_benchmark_manifests()
    _assert_published_manifest_inventory_contract(
        manifests,
        child_records="workloads",
        child_id="workload_id",
    )


def test_built_native_smoke_runner_uses_explicit_report_paths_only() -> None:
    _assert_built_native_runner_uses_optional_report_path(
        runner=benchmarks.run_built_native_smoke_benchmarks,
        expected_manifest_selector=benchmarks.BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR,
        expected_smoke_only=True,
    )


def test_built_native_smoke_cli_uses_explicit_report_paths_only(
    tmp_path: pathlib.Path,
) -> None:
    _assert_built_native_cli_uses_optional_report_path(
        tmp_path,
        flag="--native-smoke",
        runner_name="run_built_native_smoke_benchmarks",
        report_name="benchmarks-native-smoke.json",
    )


def test_built_native_smoke_mode_requires_real_built_runtime(
    tmp_path: pathlib.Path,
) -> None:
    _assert_built_native_mode_requires_real_built_runtime(
        tmp_path / "benchmarks-native-smoke.json",
        runner=benchmarks.run_built_native_smoke_benchmarks,
    )


@pytest.mark.skipif(
    MATURIN is None,
    reason="built-native benchmark smoke requires a maturin executable on PATH",
)
def test_built_native_smoke_mode_writes_built_native_report(
    tmp_path: pathlib.Path,
) -> None:
    report_path = tmp_path / "benchmarks-native-smoke.json"
    scorecard = benchmarks.run_built_native_smoke_benchmarks(
        report_path=report_path,
    )
    assert report_path.is_file()
    _assert_built_native_combined_scorecard_fields(
        scorecard,
        expected_phase="phase2-module-boundary-suite",
        expected_selection_mode="smoke",
        expected_manifest_count=3,
    )
    assert scorecard["implementation"]["adapter"] == "rebar.module-surface"
    assert scorecard["summary"]["total_workloads"] == 6
    assert scorecard["summary"]["parser_workloads"] == 0
    assert scorecard["summary"]["module_workloads"] == 6
    assert scorecard["summary"]["regression_workloads"] == 0
    assert scorecard["summary"]["measured_workloads"] == 6
    assert scorecard["summary"]["known_gap_count"] == 0
    assert [workload["id"] for workload in scorecard["workloads"]] == [
        "pattern-search-literal-warm-hit",
        "pattern-fullmatch-bytes-purged-hit",
        "module-split-literal-warm-str",
        "pattern-subn-literal-purged-bytes",
        "module-search-inline-flag-warm-str-hit",
        "pattern-fullmatch-ignorecase-purged-bytes-hit",
    ]


def test_run_benchmarks_falls_back_to_source_shim_when_build_tooling_is_unavailable(
    tmp_path: pathlib.Path,
) -> None:
    report_path = tmp_path / "benchmarks.json"
    with mock.patch.object(
        benchmarks,
        "provision_built_native_runtime",
        return_value=(None, None, _MISSING_MATURIN_REASON),
    ):
        scorecard = benchmarks.run_benchmarks(
            manifest_paths=[COMPILE_MATRIX_MANIFEST_PATH],
            report_path=report_path,
            adapter_mode=benchmarks.BUILT_NATIVE_MODE,
        )

    implementation = scorecard["implementation"]
    assert implementation["adapter_mode_requested"] == "built-native"
    assert implementation["adapter_mode_resolved"] == "source-tree-shim"
    assert implementation["build_mode"] == "source-tree-shim"
    assert implementation["timing_path"] == "source-tree-shim"
    assert isinstance(implementation["native_module_loaded"], bool)
    assert "maturin" in implementation["native_unavailable_reason"]
    assert implementation["native_build_tool"] is None
    assert implementation["native_wheel"] is None


def test_run_benchmarks_rejects_smoke_only_selection_without_smoke_workloads(
    tmp_path: pathlib.Path,
) -> None:
    manifest_source = """
    MANIFEST = {
        "schema_version": 1,
        "manifest_id": "python-benchmark-no-smoke-selection-contract",
        "defaults": {
            "warmup_iterations": 1,
            "sample_iterations": 1,
            "timed_samples": 1,
        },
        "workloads": [
            {
                "id": "compile-nonsmoke-contract",
                "bucket": "compile",
                "family": "parser",
                "operation": "compile",
                "pattern": "abc",
                "notes": [
                    "Keeps the manifest valid while intentionally omitting any smoke-tagged workloads."
                ],
            },
        ],
    }
    """

    manifest_path = _write_test_manifest(
        tmp_path,
        "python_benchmark_no_smoke_selection_contract.py",
        manifest_source,
    )

    with pytest.raises(
        ValueError,
        match="no smoke-tagged workloads matched the selected benchmark manifests",
    ):
        benchmarks.run_benchmarks(
            manifest_paths=[manifest_path],
            report_path=None,
            smoke_only=True,
        )


@pytest.mark.skipif(
    MATURIN is None,
    reason="built-native benchmark provenance smoke requires a maturin executable on PATH",
)
def test_run_benchmarks_reports_built_native_provenance_when_available(
    tmp_path: pathlib.Path,
) -> None:
    scorecard = benchmarks.run_benchmarks(
        manifest_paths=[COMPILE_MATRIX_MANIFEST_PATH],
        report_path=tmp_path / "benchmarks-native.json",
        adapter_mode=benchmarks.BUILT_NATIVE_MODE,
    )

    implementation = scorecard["implementation"]
    assert implementation["adapter_mode_requested"] == "built-native"
    assert implementation["adapter_mode_resolved"] == "built-native"
    assert implementation["build_mode"] == "built-native"
    assert implementation["timing_path"] == "built-native"
    assert implementation["native_module_loaded"] is True
    assert implementation["native_module_name"] == "rebar._rebar"
    assert implementation["native_scaffold_status"] == "scaffold-only"
    assert implementation["native_target_cpython_series"] == "3.12.x"
    assert implementation["native_unavailable_reason"] is None
    assert implementation["native_build_tool"] == "maturin"
    assert str(implementation["native_wheel"]).startswith("rebar-")
    assert (
        scorecard["environment"]["execution_model"]
        == "single-interpreter subprocess workload probes against a built native wheel"
    )


def test_built_native_full_runner_uses_explicit_report_paths_only() -> None:
    _assert_built_native_runner_uses_optional_report_path(
        runner=benchmarks.run_built_native_full_benchmarks,
        expected_manifest_selector=benchmarks.PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR,
        expected_smoke_only=False,
    )


def test_built_native_full_cli_uses_explicit_report_paths_only(
    tmp_path: pathlib.Path,
) -> None:
    _assert_built_native_cli_uses_optional_report_path(
        tmp_path,
        flag="--native-full",
        runner_name="run_built_native_full_benchmarks",
        report_name="benchmarks-native-full.json",
    )


def test_built_native_full_mode_requires_real_built_runtime(
    tmp_path: pathlib.Path,
) -> None:
    _assert_built_native_mode_requires_real_built_runtime(
        tmp_path / "benchmarks-native-full.json",
        runner=benchmarks.run_built_native_full_benchmarks,
    )


@pytest.mark.skipif(
    MATURIN is None,
    reason="built-native full-suite benchmark requires a maturin executable on PATH",
)
def test_built_native_full_mode_writes_built_native_report_with_known_gaps(
    tmp_path: pathlib.Path,
) -> None:
    published_manifests = benchmarks.published_benchmark_manifests()
    selected_workloads = [
        workload
        for manifest in published_manifests
        for workload in manifest.workloads
    ]
    expected_total = len(selected_workloads)
    expected_parser = sum(1 for workload in selected_workloads if workload.family == "parser")
    expected_module = sum(1 for workload in selected_workloads if workload.family == "module")
    expected_regression = sum(
        1 for workload in selected_workloads if workload.manifest_id == "regression-matrix"
    )

    report_path = tmp_path / "benchmarks-native-full.json"
    scorecard = benchmarks.run_built_native_full_benchmarks(
        report_path=report_path,
    )
    assert report_path.is_file()
    _assert_built_native_combined_scorecard_fields(
        scorecard,
        expected_phase="phase3-regression-stability-suite",
        expected_selection_mode="full",
        expected_manifest_count=len(published_manifests),
    )
    assert scorecard["summary"]["total_workloads"] == expected_total
    assert scorecard["summary"]["parser_workloads"] == expected_parser
    assert scorecard["summary"]["module_workloads"] == expected_module
    assert scorecard["summary"]["regression_workloads"] == expected_regression

    unimplemented_workloads = [
        workload
        for workload in scorecard["workloads"]
        if workload["implementation_timing"]["status"] == "unimplemented"
    ]
    measured_workloads = [
        workload
        for workload in scorecard["workloads"]
        if workload["implementation_timing"]["status"] == "measured"
    ]
    assert len(unimplemented_workloads) > 0
    assert scorecard["summary"]["known_gap_count"] == len(unimplemented_workloads)
    assert scorecard["summary"]["measured_workloads"] == len(measured_workloads)
    assert len(measured_workloads) + len(unimplemented_workloads) == expected_total
