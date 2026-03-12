from __future__ import annotations

import importlib.util
import json
import pathlib
import sys
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "rebar_ops.py"
CORRECTNESS_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.json"


def load_rebar_ops_module():
    spec = importlib.util.spec_from_file_location("rebar_ops_for_tests", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ReadmeReportingTest(unittest.TestCase):
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
