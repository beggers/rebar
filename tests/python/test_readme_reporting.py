from __future__ import annotations

import json
import unittest

from rebar_harness import benchmarks, correctness
from tests.harness_cli_test_support import (
    REPO_ROOT,
    load_rebar_ops_module,
    run_harness_cli,
    run_harness_scorecard,
)

PARSER_FIXTURES_PATH = REPO_ROOT / "tests" / "conformance" / "fixtures" / "parser_matrix.py"
CORRECTNESS_REPORT_PATH = correctness.SCORECARD_REPORT.published_path
LEGACY_CORRECTNESS_REPORT_PATH = correctness.SCORECARD_REPORT.legacy_path
BENCHMARK_REPORT_PATH = benchmarks.SCORECARD_REPORT.published_path
LEGACY_BENCHMARK_REPORT_PATH = benchmarks.SCORECARD_REPORT.legacy_path


def _load_correctness_scorecard(report_path):
    return correctness.SCORECARD_REPORT.load(report_path)


def _write_correctness_scorecard(scorecard, report_path) -> None:
    correctness.SCORECARD_REPORT.write(scorecard, report_path)


def _load_benchmark_scorecard(report_path):
    return benchmarks.SCORECARD_REPORT.load(report_path)


class ReadmeReportingTest(unittest.TestCase):
    def test_correctness_cli_rejects_legacy_tracked_json_path(self) -> None:
        result = run_harness_cli(
            "rebar_harness.correctness",
            [
                "--fixtures",
                str(PARSER_FIXTURES_PATH),
                "--report",
                str(LEGACY_CORRECTNESS_REPORT_PATH),
            ],
            check=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("reports/correctness/latest.json is a retired legacy", result.stderr)
        self.assertIn("reports/correctness/latest.py", result.stderr)
        self.assertIn("non-tracked temporary .json path", result.stderr)
        self.assertFalse(LEGACY_CORRECTNESS_REPORT_PATH.exists())

    def test_benchmark_cli_rejects_legacy_tracked_json_path(self) -> None:
        result = run_harness_cli(
            "rebar_harness.benchmarks",
            [
                "--report",
                str(LEGACY_BENCHMARK_REPORT_PATH),
            ],
            check=False,
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

            repaired_payload = _load_correctness_scorecard(CORRECTNESS_REPORT_PATH)
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
            _, narrowed_scorecard = run_harness_scorecard(
                "rebar_harness.correctness",
                [
                    "--fixtures",
                    str(PARSER_FIXTURES_PATH),
                ],
                report_name="parser-only.json",
            )

            _write_correctness_scorecard(narrowed_scorecard, CORRECTNESS_REPORT_PATH)

            refreshed = rebar_ops.refresh_published_correctness_scorecard()
            self.assertIsInstance(refreshed, dict)

            repaired_payload = _load_correctness_scorecard(CORRECTNESS_REPORT_PATH)
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
        payload = _load_correctness_scorecard(CORRECTNESS_REPORT_PATH)
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

    def test_benchmark_harness_loads_tracked_python_scorecard(self) -> None:
        payload = _load_benchmark_scorecard(BENCHMARK_REPORT_PATH)

        self.assertIsInstance(payload, dict)
        self.assertEqual(payload["suite"], "benchmarks")
        self.assertEqual(payload["implementation"]["module_name"], "rebar")


if __name__ == "__main__":
    unittest.main()
