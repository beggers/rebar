from __future__ import annotations

import pathlib
import shutil
import sys
import tempfile
import unittest
from collections.abc import Callable
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
