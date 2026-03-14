from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

from tests.conformance.scorecard_suite_support import (
    load_published_correctness_scorecard,
    write_published_correctness_scorecard,
)


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "rebar_ops.py"
CORRECTNESS_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.py"
LEGACY_CORRECTNESS_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.json"
BENCHMARK_REPORT_PATH = REPO_ROOT / "reports" / "benchmarks" / "latest.py"
LEGACY_BENCHMARK_REPORT_PATH = REPO_ROOT / "reports" / "benchmarks" / "latest.json"
PARSER_FIXTURES_PATH = REPO_ROOT / "tests" / "conformance" / "fixtures" / "parser_matrix.py"
PYTHON_SOURCE = REPO_ROOT / "python"


def load_rebar_ops_module():
    spec = importlib.util.spec_from_file_location("rebar_ops_for_tests", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ReadmeReportingTest(unittest.TestCase):
    def test_correctness_cli_rejects_legacy_tracked_json_path(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "rebar_harness.correctness",
                "--fixtures",
                str(PARSER_FIXTURES_PATH),
                "--report",
                str(LEGACY_CORRECTNESS_REPORT_PATH),
            ],
            check=False,
            cwd=REPO_ROOT,
            env={"PYTHONPATH": str(PYTHON_SOURCE)},
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("reports/correctness/latest.json is a retired legacy", result.stderr)
        self.assertIn("reports/correctness/latest.py", result.stderr)
        self.assertIn("non-tracked temporary .json path", result.stderr)
        self.assertFalse(LEGACY_CORRECTNESS_REPORT_PATH.exists())

    def test_benchmark_cli_rejects_legacy_tracked_json_path(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "rebar_harness.benchmarks",
                "--report",
                str(LEGACY_BENCHMARK_REPORT_PATH),
            ],
            check=False,
            cwd=REPO_ROOT,
            env={"PYTHONPATH": str(PYTHON_SOURCE)},
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("reports/benchmarks/latest.json is a retired legacy", result.stderr)
        self.assertIn("reports/benchmarks/latest.py", result.stderr)
        self.assertIn("non-tracked temporary .json path", result.stderr)
        self.assertFalse(LEGACY_BENCHMARK_REPORT_PATH.exists())

    def test_refresh_published_correctness_scorecard_deletes_legacy_json_sidecar(self) -> None:
        rebar_ops = load_rebar_ops_module()
        original_payload = CORRECTNESS_REPORT_PATH.read_text(encoding="utf-8")

        try:
            LEGACY_CORRECTNESS_REPORT_PATH.write_text(
                json.dumps({"legacy": True}, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            refreshed = rebar_ops.refresh_published_correctness_scorecard()

            self.assertIsInstance(refreshed, dict)
            self.assertFalse(LEGACY_CORRECTNESS_REPORT_PATH.exists())

            repaired_payload = load_published_correctness_scorecard()
            expected_manifest_ids = rebar_ops.expected_correctness_manifest_ids(
                rebar_ops.load_correctness_harness_module()
            )
            self.assertEqual(repaired_payload["fixtures"]["manifest_count"], len(expected_manifest_ids))
            self.assertEqual(repaired_payload["fixtures"]["manifest_ids"], expected_manifest_ids)
        finally:
            CORRECTNESS_REPORT_PATH.write_text(original_payload, encoding="utf-8")
            LEGACY_CORRECTNESS_REPORT_PATH.unlink(missing_ok=True)

    def test_refresh_published_correctness_scorecard_repairs_narrowed_report(self) -> None:
        rebar_ops = load_rebar_ops_module()
        original_payload = CORRECTNESS_REPORT_PATH.read_text(encoding="utf-8")

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                narrowed_report_path = pathlib.Path(temp_dir) / "parser-only.json"
                subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "rebar_harness.correctness",
                        "--fixtures",
                        str(PARSER_FIXTURES_PATH),
                        "--report",
                        str(narrowed_report_path),
                    ],
                    check=True,
                    cwd=REPO_ROOT,
                    env={"PYTHONPATH": str(PYTHON_SOURCE)},
                    capture_output=True,
                    text=True,
                )

                write_published_correctness_scorecard(
                    json.loads(narrowed_report_path.read_text(encoding="utf-8"))
                )

                refreshed = rebar_ops.refresh_published_correctness_scorecard()
                self.assertIsInstance(refreshed, dict)

                repaired_payload = load_published_correctness_scorecard()
                expected_manifest_ids = rebar_ops.expected_correctness_manifest_ids(
                    rebar_ops.load_correctness_harness_module()
                )
                self.assertEqual(
                    repaired_payload["fixtures"]["manifest_count"], len(expected_manifest_ids)
                )
                self.assertEqual(repaired_payload["fixtures"]["manifest_ids"], expected_manifest_ids)
                self.assertEqual(repaired_payload["summary"], refreshed["summary"])
        finally:
            CORRECTNESS_REPORT_PATH.write_text(original_payload, encoding="utf-8")

    def test_correctness_scorecard_uses_tracked_summary_shape(self) -> None:
        rebar_ops = load_rebar_ops_module()
        config = rebar_ops.load_config()
        payload = load_published_correctness_scorecard()
        summary = payload["summary"]

        expected_total = summary.get("cases_total", summary.get("total_cases"))
        expected_passed = summary.get("cases_passed", summary.get("passed_cases", summary.get("passed")))

        scorecard = rebar_ops.scorecard_from_config(
            config,
            "correctness_scorecard",
            "Correctness Scorecard",
            "reports/correctness/latest.py",
        )

        self.assertTrue(scorecard["available"])
        self.assertEqual(scorecard["cases_total"], expected_total)
        self.assertEqual(scorecard["cases_passed"], expected_passed)
        self.assertEqual(scorecard["candidate"], payload["baseline"]["target_module"])

        rendered = rebar_ops.render_readme_status(config)
        self.assertIn(f"| Published cases | `{expected_total}` |", rendered)
        self.assertIn(f"| Passing in published slice | `{expected_passed}` |", rendered)
        expected_unimplemented = summary.get(
            "cases_unimplemented",
            summary.get("unimplemented_cases", summary.get("unimplemented")),
        )
        self.assertIn(f"| Honest gaps (`unimplemented`) | `{expected_unimplemented}` |", rendered)
        self.assertIn("Overall delivery estimate:", rendered)
        self.assertIn("These correctness counts cover only the published slice.", rendered)
        self.assertIn("| Timing path | `source-tree-shim` |", rendered)
        self.assertIn("strict built-native smoke and full-suite modes remain available", rendered)
        self.assertIn("`--native-smoke`", rendered)
        self.assertIn("`--native-full`", rendered)
        self.assertIn("explicit `--report` path", rendered)
        self.assertNotIn("native_smoke.json", rendered)
        self.assertNotIn("native_full.json", rendered)

    def test_benchmark_scorecard_uses_tracked_summary_shape(self) -> None:
        rebar_ops = load_rebar_ops_module()
        config = rebar_ops.load_config()
        payload = rebar_ops.read_structured_dict(
            BENCHMARK_REPORT_PATH,
            default=None,
            label="benchmark scorecard",
        )

        self.assertIsInstance(payload, dict)
        summary = payload["summary"]
        implementation = payload["implementation"]

        scorecard = rebar_ops.scorecard_from_config(
            config,
            "benchmark_scorecard",
            "Benchmark Snapshot",
            "reports/benchmarks/latest.py",
        )

        self.assertTrue(scorecard["available"])
        self.assertEqual(scorecard["workload_count"], summary["total_workloads"])
        self.assertEqual(scorecard["measured_workloads"], summary["measured_workloads"])
        self.assertEqual(scorecard["known_gap_count"], summary["known_gap_count"])
        self.assertEqual(scorecard["candidate"], implementation["module_name"])

        rendered = rebar_ops.render_readme_status(config)
        self.assertIn(f"| Published workloads | `{summary['total_workloads']}` |", rendered)
        self.assertIn(
            f"| Workloads with real `rebar` timings | `{summary['measured_workloads']}` |",
            rendered,
        )
        self.assertIn("reports/benchmarks/latest.py", rendered)
        self.assertNotIn("reports/benchmarks/latest.json", rendered)


if __name__ == "__main__":
    unittest.main()
