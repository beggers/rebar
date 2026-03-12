from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "rebar_ops.py"
CORRECTNESS_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.json"
PARSER_FIXTURES_PATH = REPO_ROOT / "tests" / "conformance" / "fixtures" / "parser_matrix.json"
PYTHON_SOURCE = REPO_ROOT / "python"
EXPECTED_MANIFEST_IDS = [
    "parser-matrix",
    "public-api-surface",
    "match-behavior-smoke",
    "exported-symbol-surface",
    "pattern-object-surface",
    "module-workflow-surface",
    "collection-replacement-workflows",
    "literal-flag-workflows",
    "grouped-match-workflows",
    "named-group-workflows",
]


def load_rebar_ops_module():
    spec = importlib.util.spec_from_file_location("rebar_ops_for_tests", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ReadmeReportingTest(unittest.TestCase):
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

                CORRECTNESS_REPORT_PATH.write_text(
                    narrowed_report_path.read_text(encoding="utf-8"),
                    encoding="utf-8",
                )

                refreshed = rebar_ops.refresh_published_correctness_scorecard()
                self.assertIsInstance(refreshed, dict)

                repaired_payload = json.loads(CORRECTNESS_REPORT_PATH.read_text(encoding="utf-8"))
                self.assertEqual(repaired_payload["fixtures"]["manifest_count"], len(EXPECTED_MANIFEST_IDS))
                self.assertEqual(repaired_payload["fixtures"]["manifest_ids"], EXPECTED_MANIFEST_IDS)
                self.assertEqual(repaired_payload["summary"], refreshed["summary"])
        finally:
            CORRECTNESS_REPORT_PATH.write_text(original_payload, encoding="utf-8")

    def test_correctness_scorecard_uses_tracked_summary_shape(self) -> None:
        rebar_ops = load_rebar_ops_module()
        config = rebar_ops.load_config()
        payload = json.loads(CORRECTNESS_REPORT_PATH.read_text(encoding="utf-8"))
        summary = payload["summary"]

        expected_total = summary.get("cases_total", summary.get("total_cases"))
        expected_passed = summary.get("cases_passed", summary.get("passed_cases", summary.get("passed")))

        scorecard = rebar_ops.scorecard_from_config(
            config,
            "correctness_scorecard",
            "Correctness Scorecard",
            "reports/correctness/latest.json",
        )

        self.assertTrue(scorecard["available"])
        self.assertEqual(scorecard["cases_total"], expected_total)
        self.assertEqual(scorecard["cases_passed"], expected_passed)
        self.assertEqual(scorecard["candidate"], payload["baseline"]["target_module"])

        rendered = rebar_ops.render_readme_status(config)
        self.assertIn(f"| Published cases | `{expected_total}` |", rendered)
        self.assertIn(f"| Passing comparisons | `{expected_passed}` |", rendered)
        expected_unimplemented = summary.get(
            "cases_unimplemented",
            summary.get("unimplemented_cases", summary.get("unimplemented")),
        )
        self.assertIn(f"| Honest gaps (`unimplemented`) | `{expected_unimplemented}` |", rendered)


if __name__ == "__main__":
    unittest.main()
