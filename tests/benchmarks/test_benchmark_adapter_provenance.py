from __future__ import annotations

import pathlib
import shutil
import sys
import tempfile
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
if str(PYTHON_SOURCE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SOURCE))

from rebar_harness import benchmarks


MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "compile_smoke.json"
MATURIN = shutil.which("maturin")


class BenchmarkAdapterProvenanceTest(unittest.TestCase):
    def test_native_mode_falls_back_to_source_shim_when_build_tooling_is_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = pathlib.Path(temp_dir) / "benchmarks.json"
            with mock.patch.object(
                benchmarks,
                "provision_built_native_runtime",
                return_value=(
                    None,
                    None,
                    "built-native mode unavailable because no `maturin` executable was found on PATH",
                ),
            ):
                scorecard = benchmarks.run_benchmarks(
                    manifest_paths=[MANIFEST_PATH],
                    report_path=report_path,
                    adapter_mode=benchmarks.BUILT_NATIVE_MODE,
                )

        implementation = scorecard["implementation"]
        self.assertEqual(implementation["adapter_mode_requested"], "built-native")
        self.assertEqual(implementation["adapter_mode_resolved"], "source-tree-shim")
        self.assertEqual(implementation["build_mode"], "source-tree-shim")
        self.assertEqual(implementation["timing_path"], "source-tree-shim")
        self.assertFalse(implementation["native_module_loaded"])
        self.assertIn("maturin", implementation["native_unavailable_reason"])
        self.assertIsNone(implementation["native_build_tool"])
        self.assertIsNone(implementation["native_wheel"])

    @unittest.skipUnless(
        MATURIN is not None,
        "built-native benchmark provenance smoke requires a maturin executable on PATH",
    )
    def test_native_mode_reports_built_native_provenance_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = pathlib.Path(temp_dir) / "benchmarks-native.json"
            scorecard = benchmarks.run_benchmarks(
                manifest_paths=[MANIFEST_PATH],
                report_path=report_path,
                adapter_mode=benchmarks.BUILT_NATIVE_MODE,
            )

        implementation = scorecard["implementation"]
        self.assertEqual(implementation["adapter_mode_requested"], "built-native")
        self.assertEqual(implementation["adapter_mode_resolved"], "built-native")
        self.assertEqual(implementation["build_mode"], "built-native")
        self.assertEqual(implementation["timing_path"], "built-native")
        self.assertTrue(implementation["native_module_loaded"])
        self.assertEqual(implementation["native_module_name"], "rebar._rebar")
        self.assertEqual(implementation["native_scaffold_status"], "scaffold-only")
        self.assertEqual(implementation["native_target_cpython_series"], "3.12.x")
        self.assertIsNone(implementation["native_unavailable_reason"])
        self.assertEqual(implementation["native_build_tool"], "maturin")
        self.assertTrue(str(implementation["native_wheel"]).startswith("rebar-"))
        self.assertEqual(
            scorecard["environment"]["execution_model"],
            "single-interpreter subprocess workload probes against a built native wheel",
        )


if __name__ == "__main__":
    unittest.main()
