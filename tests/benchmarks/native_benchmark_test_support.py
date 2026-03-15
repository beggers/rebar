from __future__ import annotations

import os
import pathlib
import shutil
import sys
import tempfile
import unittest
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from unittest import mock


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))

from rebar_harness import benchmarks


MATURIN = shutil.which("maturin")
_MISSING_MATURIN_REASON = (
    "built-native mode unavailable because no `maturin` executable was found on PATH"
)
_MISSING_MATURIN_PATTERN = "no `maturin` executable was found on PATH"


@contextmanager
def built_native_runtime(
    testcase: unittest.TestCase,
) -> Iterator[tuple[pathlib.Path, dict[str, str]]]:
    provisioned, temp_dir, error = benchmarks.provision_built_native_runtime()
    testcase.assertIsNotNone(provisioned, error)
    testcase.assertIsNotNone(temp_dir, error)
    assert provisioned is not None
    assert temp_dir is not None

    # Keep the installed wheel ahead of the source tree so probe subprocesses
    # exercise the built native artifact instead of the checkout shim.
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        str(path) for path in (provisioned["install_root"], PYTHON_SOURCE)
    )

    try:
        yield pathlib.Path(sys.executable), env
    finally:
        temp_dir.cleanup()


def build_minimal_scorecard() -> dict[str, object]:
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


def assert_native_mode_requires_real_built_runtime(
    testcase: unittest.TestCase,
    *,
    runner: Callable[..., dict[str, object]],
    report_name: str,
) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        report_path = pathlib.Path(temp_dir) / report_name
        with mock.patch.object(
            benchmarks,
            "provision_built_native_runtime",
            return_value=(None, None, _MISSING_MATURIN_REASON),
        ):
            with testcase.assertRaisesRegex(
                benchmarks.NativeBenchmarkProvisionError,
                _MISSING_MATURIN_PATTERN,
            ):
                runner(report_path=report_path)

        testcase.assertFalse(report_path.exists())


def run_native_benchmark_with_report(
    testcase: unittest.TestCase,
    *,
    runner: Callable[..., dict[str, object]],
    report_name: str,
) -> dict[str, object]:
    with tempfile.TemporaryDirectory() as temp_dir:
        report_path = pathlib.Path(temp_dir) / report_name
        scorecard = runner(report_path=report_path)
        testcase.assertTrue(report_path.is_file())

    return scorecard


def assert_native_runner_uses_optional_report_path(
    testcase: unittest.TestCase,
    *,
    runner: Callable[..., dict[str, object]],
    expected_manifest_paths: tuple[pathlib.Path, ...],
    expected_smoke_only: bool,
) -> None:
    scorecard = build_minimal_scorecard()
    explicit_report_path = REPO_ROOT / "reports" / "benchmarks" / "explicit-native-check.json"

    with mock.patch.object(benchmarks, "run_benchmarks", return_value=scorecard) as mocked_run:
        returned = runner()

    testcase.assertIs(returned, scorecard)
    mocked_run.assert_called_once_with(
        manifest_paths=list(expected_manifest_paths),
        report_path=None,
        smoke_only=expected_smoke_only,
        adapter_mode=benchmarks.BUILT_NATIVE_MODE,
        allow_fallback=False,
    )

    with mock.patch.object(benchmarks, "run_benchmarks", return_value=scorecard) as mocked_run:
        returned = runner(report_path=explicit_report_path)

    testcase.assertIs(returned, scorecard)
    mocked_run.assert_called_once_with(
        manifest_paths=list(expected_manifest_paths),
        report_path=explicit_report_path,
        smoke_only=expected_smoke_only,
        adapter_mode=benchmarks.BUILT_NATIVE_MODE,
        allow_fallback=False,
    )


def assert_native_cli_uses_optional_report_path(
    testcase: unittest.TestCase,
    *,
    flag: str,
    runner_name: str,
    report_name: str,
) -> None:
    scorecard = build_minimal_scorecard()

    with (
        mock.patch.object(benchmarks, runner_name, return_value=scorecard) as mocked_runner,
        mock.patch("builtins.print"),
    ):
        exit_code = benchmarks.main([flag])

    testcase.assertEqual(exit_code, 0)
    mocked_runner.assert_called_once_with(report_path=None)

    with tempfile.TemporaryDirectory() as temp_dir:
        report_path = pathlib.Path(temp_dir) / report_name
        with (
            mock.patch.object(
                benchmarks, runner_name, return_value=scorecard
            ) as mocked_runner,
            mock.patch("builtins.print"),
        ):
            exit_code = benchmarks.main([flag, "--report", str(report_path)])

    testcase.assertEqual(exit_code, 0)
    mocked_runner.assert_called_once_with(report_path=report_path)


def assert_built_native_combined_scorecard_fields(
    testcase: unittest.TestCase,
    scorecard: dict[str, object],
    *,
    expected_phase: str,
    expected_selection_mode: str,
    expected_manifest_count: int,
) -> None:
    implementation = scorecard["implementation"]
    environment = scorecard["environment"]
    artifacts = scorecard["artifacts"]

    testcase.assertEqual(scorecard["schema_version"], "1.0")
    testcase.assertEqual(scorecard["phase"], expected_phase)
    testcase.assertEqual(implementation["module_name"], "rebar")
    testcase.assertEqual(implementation["adapter_mode_requested"], "built-native")
    testcase.assertEqual(implementation["adapter_mode_resolved"], "built-native")
    testcase.assertEqual(implementation["build_mode"], "built-native")
    testcase.assertEqual(implementation["timing_path"], "built-native")
    testcase.assertTrue(implementation["native_module_loaded"])
    testcase.assertEqual(implementation["native_module_name"], "rebar._rebar")
    testcase.assertEqual(implementation["native_build_tool"], "maturin")
    testcase.assertTrue(str(implementation["native_wheel"]).startswith("rebar-"))
    testcase.assertIsNone(implementation["native_unavailable_reason"])
    testcase.assertEqual(
        environment["execution_model"],
        "single-interpreter subprocess workload probes against a built native wheel",
    )
    testcase.assertEqual(artifacts["manifest"], None)
    testcase.assertEqual(artifacts["manifest_id"], "combined-benchmark-suite")
    testcase.assertEqual(artifacts["selection_mode"], expected_selection_mode)
    testcase.assertEqual(len(artifacts["manifests"]), expected_manifest_count)
