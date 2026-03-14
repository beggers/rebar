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
