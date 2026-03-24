from __future__ import annotations

from collections.abc import Callable
import pathlib
import re
import shutil
from unittest import mock

import pytest

from rebar_harness import benchmarks
from rebar_harness.benchmarks import (
    BENCHMARK_WORKLOADS_ROOT,
    PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR,
    published_benchmark_manifests,
    select_benchmark_manifest_paths,
)
from rebar_harness.scorecard_io import ordered_published_subset_filenames
from tests.benchmarks.benchmark_test_support import _write_test_manifest
from tests.conftest import (
    REPO_ROOT,
    assert_declared_string_selector_registry_contract,
    assert_published_manifest_inventory_contract,
    assert_published_manifest_helper_contract,
    assert_published_manifest_helper_reload_contract,
    assert_published_selector_subset_paths_contract,
)


COMPILE_MATRIX_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "compile_matrix.py"
MATURIN = shutil.which("maturin")
_MISSING_MATURIN_REASON = (
    "built-native mode unavailable because no `maturin` executable was found on PATH"
)
_MISSING_MATURIN_PATTERN = "no `maturin` executable was found on PATH"


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

    assert_published_selector_subset_paths_contract(
        published_manifest_paths,
        selected_paths,
        root_path=BENCHMARK_WORKLOADS_ROOT,
    )


def test_built_native_smoke_manifest_selector_keeps_membership_contract() -> None:
    selector = benchmarks.BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR
    expected_filenames = (
        benchmarks._NONDEFAULT_BENCHMARK_MANIFEST_SELECTOR_REQUESTED_FILENAMES[
            selector
        ]
    )
    assert benchmarks._BENCHMARK_MANIFEST_FILENAMES_BY_SELECTOR[selector] == expected_filenames

    assert_published_selector_subset_paths_contract(
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
        ordered_published_subset_filenames(
            benchmarks._BENCHMARK_MANIFEST_FILENAMES_BY_SELECTOR[
                PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR
            ],
            ("missing_boundary.py",),
            missing_filename_error_prefix=(
                benchmarks._PUBLISHED_BENCHMARK_MANIFEST_MISSING_ERROR_PREFIX
            ),
        )


def test_declared_benchmark_manifest_selectors_match_registry_keys() -> None:
    declared_selectors = assert_declared_string_selector_registry_contract(
        benchmarks,
        name_suffix="_MANIFEST_SELECTOR",
        selector_registry=benchmarks._BENCHMARK_MANIFEST_FILENAMES_BY_SELECTOR,
    )

    assert declared_selectors


def test_default_benchmark_published_manifest_helper_is_cached_and_preserves_selector_order() -> None:
    published_manifest_paths = select_benchmark_manifest_paths(
        PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR
    )

    assert_published_manifest_helper_contract(
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
    assert_published_manifest_helper_reload_contract(
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
    assert_published_manifest_inventory_contract(
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
