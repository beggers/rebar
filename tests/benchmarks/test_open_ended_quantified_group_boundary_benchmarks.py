from __future__ import annotations

import json
import pathlib
import platform
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "open_ended_quantified_group_boundary.json"
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "benchmarks" / "latest.json"


class OpenEndedQuantifiedGroupBoundaryBenchmarkSuiteTest(unittest.TestCase):
    def test_runner_regenerates_open_ended_group_boundary_scorecard(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        anchor_expectations = {
            "module-search-numbered-open-ended-group-broader-range-cold-gap": {
                "pattern": "a(bc|de){2,}d",
                "haystack": "zzabcbcdzz",
            },
            "module-search-numbered-open-ended-group-broader-range-conditional-warm-gap": {
                "pattern": "a((bc|de){2,})?(?(1)d|e)",
                "haystack": "zzabcbcdzz",
            },
            "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-str": {
                "pattern": "a(?P<word>(bc|b)c){2,}d",
                "haystack": "abcbcbcbcd",
            },
        }
        manifest_workloads = {item["id"]: item for item in manifest["workloads"]}
        for workload_id, expected in anchor_expectations.items():
            with self.subTest(anchor_workload_id=workload_id):
                workload = manifest_workloads[workload_id]
                self.assertEqual(workload["pattern"], expected["pattern"])
                self.assertEqual(workload["haystack"], expected["haystack"])

        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = pathlib.Path(temp_dir) / "benchmarks.json"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "rebar_harness.benchmarks",
                    "--manifest",
                    str(MANIFEST_PATH),
                    "--report",
                    str(report_path),
                ],
                check=True,
                cwd=REPO_ROOT,
                env={"PYTHONPATH": str(PYTHON_SOURCE)},
                capture_output=True,
                text=True,
            )

            summary = json.loads(result.stdout.strip())
            self.assertEqual(
                summary,
                {
                    "known_gap_count": 0,
                    "measured_workloads": 36,
                    "module_workloads": 36,
                    "parser_workloads": 0,
                    "regression_workloads": 0,
                    "total_workloads": 36,
                },
            )

            scorecard = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(scorecard["schema_version"], "1.0")
        self.assertEqual(scorecard["phase"], "phase2-module-boundary-suite")
        self.assertEqual(scorecard["baseline"]["python_implementation"], platform.python_implementation())
        self.assertEqual(scorecard["baseline"]["python_version"], platform.python_version())
        self.assertEqual(scorecard["implementation"]["module_name"], "rebar")
        self.assertEqual(scorecard["implementation"]["adapter"], "rebar.module-surface")
        self.assertEqual(scorecard["implementation"]["adapter_mode_requested"], "source-tree-shim")
        self.assertEqual(scorecard["implementation"]["adapter_mode_resolved"], "source-tree-shim")
        self.assertEqual(scorecard["implementation"]["build_mode"], "source-tree-shim")
        self.assertEqual(scorecard["implementation"]["timing_path"], "source-tree-shim")
        self.assertIsInstance(scorecard["implementation"]["native_module_loaded"], bool)
        self.assertIn("not requested", scorecard["implementation"]["native_unavailable_reason"])
        self.assertEqual(scorecard["summary"]["total_workloads"], 36)
        self.assertEqual(scorecard["summary"]["measured_workloads"], 36)
        self.assertEqual(scorecard["summary"]["known_gap_count"], 0)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["cold"], 7)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["warm"], 17)
        self.assertEqual(scorecard["summary"]["workloads_by_cache_mode"]["purged"], 12)
        self.assertEqual(scorecard["environment"]["runner_version"], "phase2")
        self.assertEqual(scorecard["families"]["module"]["workload_count"], 36)
        self.assertEqual(scorecard["families"]["module"]["known_gap_count"], 0)
        self.assertEqual(scorecard["families"]["module"]["readiness"], "measured")
        self.assertEqual(scorecard["artifacts"]["manifest"], "benchmarks/workloads/open_ended_quantified_group_boundary.json")
        self.assertEqual(scorecard["artifacts"]["manifest_id"], "open-ended-quantified-group-boundary")
        self.assertEqual(scorecard["artifacts"]["manifest_schema_version"], 1)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        manifest_summary = scorecard["manifests"]["open-ended-quantified-group-boundary"]
        self.assertEqual(manifest_summary["workload_count"], 36)
        self.assertEqual(manifest_summary["selected_workload_count"], 36)
        self.assertEqual(manifest_summary["measured_workloads"], 36)
        self.assertEqual(manifest_summary["known_gap_count"], 0)
        self.assertEqual(manifest_summary["readiness"], "measured")
        self.assertEqual(
            manifest_summary["operations"],
            ["module.compile", "module.search", "pattern.fullmatch"],
        )

        measured_ids = {
            "module-compile-numbered-open-ended-group-broader-range-cold-str",
            "module-search-numbered-open-ended-group-broader-range-cold-gap",
            "pattern-fullmatch-numbered-open-ended-group-broader-range-third-repetition-mixed-purged-str",
            "module-compile-named-open-ended-group-broader-range-warm-str",
            "module-search-named-open-ended-group-broader-range-lower-bound-de-warm-str",
            "pattern-fullmatch-named-open-ended-group-broader-range-third-repetition-de-purged-str",
            "module-compile-numbered-open-ended-group-broader-range-conditional-cold-str",
            "module-search-numbered-open-ended-group-broader-range-conditional-warm-gap",
            "pattern-fullmatch-numbered-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-str",
            "module-compile-named-open-ended-group-broader-range-conditional-warm-str",
            "module-search-named-open-ended-group-broader-range-conditional-fourth-repetition-de-warm-str",
            "pattern-fullmatch-named-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-str",
            "module-compile-numbered-open-ended-group-broader-range-backtracking-heavy-cold-str",
            "module-search-numbered-open-ended-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-str",
            "pattern-fullmatch-numbered-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-str",
            "module-compile-named-open-ended-group-broader-range-backtracking-heavy-warm-str",
            "module-search-named-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-warm-str",
            "pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-str",
        }
        for workload_id in measured_ids:
            with self.subTest(workload_id=workload_id):
                workload = next(item for item in scorecard["workloads"] if item["id"] == workload_id)
                self.assertEqual(workload["status"], "measured")
                self.assertEqual(workload["implementation_timing"]["status"], "measured")
                self.assertGreater(workload["baseline_ns"], 0)
                self.assertGreater(workload["implementation_ns"], 0)
                self.assertIsInstance(workload["speedup_vs_cpython"], float)

        gap_ids: set[str] = set()
        for workload_id in gap_ids:
            with self.subTest(gap_workload_id=workload_id):
                workload = next(item for item in scorecard["workloads"] if item["id"] == workload_id)
                self.assertEqual(workload["status"], "unimplemented")
                self.assertEqual(workload["implementation_timing"]["status"], "unimplemented")
                self.assertGreater(workload["baseline_ns"], 0)


if __name__ == "__main__":
    unittest.main()
