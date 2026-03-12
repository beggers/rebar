from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
MODULE_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "module_boundary.json"
COLLECTION_REPLACEMENT_MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "collection_replacement_boundary.json"
)
LITERAL_FLAG_MANIFEST_PATH = REPO_ROOT / "benchmarks" / "workloads" / "literal_flag_boundary.json"


class PostParserWorkflowBenchmarkSuiteTest(unittest.TestCase):
    def test_post_parser_workflows_publish_real_timings_and_keep_known_gaps_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = pathlib.Path(temp_dir) / "benchmarks.json"
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "rebar_harness.benchmarks",
                    "--manifest",
                    str(MODULE_MANIFEST_PATH),
                    "--manifest",
                    str(COLLECTION_REPLACEMENT_MANIFEST_PATH),
                    "--manifest",
                    str(LITERAL_FLAG_MANIFEST_PATH),
                    "--report",
                    str(report_path),
                ],
                check=True,
                cwd=REPO_ROOT,
                env={"PYTHONPATH": str(PYTHON_SOURCE)},
                capture_output=True,
                text=True,
            )

            scorecard = json.loads(report_path.read_text(encoding="utf-8"))

        measured_ids = {
            "module-search-grouped-literal-cold-hit",
            "module-findall-single-dot-warm-str",
            "module-sub-template-warm-str",
            "pattern-subn-grouped-template-warm-str",
            "module-search-inline-flag-warm-str-hit",
            "pattern-search-inline-flag-warm-str-hit",
            "module-search-locale-purged-bytes-hit",
            "pattern-search-locale-purged-bytes-hit",
        }
        for workload_id in measured_ids:
            with self.subTest(workload_id=workload_id):
                workload = next(
                    item for item in scorecard["workloads"] if item["id"] == workload_id
                )
                self.assertEqual(workload["status"], "measured")
                self.assertEqual(workload["implementation_timing"]["status"], "measured")
                self.assertGreater(workload["implementation_ns"], 0)

        ascii_gap_ids = {
            "module-search-ignorecase-ascii-cold-gap",
            "pattern-search-ignorecase-ascii-warm-gap",
        }
        for workload_id in ascii_gap_ids:
            with self.subTest(workload_id=workload_id):
                workload = next(
                    item for item in scorecard["workloads"] if item["id"] == workload_id
                )
                self.assertEqual(workload["status"], "unimplemented")
                self.assertEqual(workload["implementation_timing"]["status"], "unimplemented")
                self.assertIsNone(workload["implementation_ns"])


if __name__ == "__main__":
    unittest.main()
