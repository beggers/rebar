from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
MANIFEST_PATH = (
    REPO_ROOT / "benchmarks" / "workloads" / "wider_ranged_repeat_quantified_group_boundary.json"
)


class WiderRangedRepeatQuantifiedGroupBoundaryBenchmarkSuiteTest(unittest.TestCase):
    def test_broader_range_and_nested_open_ended_grouped_alternation_rows_are_measured(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = pathlib.Path(temp_dir) / "benchmarks.json"
            subprocess.run(
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

            scorecard = json.loads(report_path.read_text(encoding="utf-8"))

        measured_ids = {
            "module-compile-numbered-wider-ranged-repeat-group-broader-range-cold-str",
            "module-search-numbered-wider-ranged-repeat-group-broader-range-cold-gap",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-third-repetition-mixed-purged-str",
            "module-compile-named-wider-ranged-repeat-group-broader-range-warm-str",
            "module-search-named-wider-ranged-repeat-group-broader-range-upper-bound-all-de-warm-str",
            "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-upper-bound-mixed-purged-str",
            "module-compile-numbered-wider-ranged-repeat-group-open-ended-cold-str",
            "module-search-numbered-wider-ranged-repeat-group-open-ended-lower-bound-bc-warm-str",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-open-ended-purged-gap",
            "module-compile-named-wider-ranged-repeat-group-open-ended-warm-str",
            "module-search-named-wider-ranged-repeat-group-open-ended-lower-bound-de-warm-str",
            "pattern-fullmatch-named-wider-ranged-repeat-group-open-ended-fourth-repetition-de-purged-str",
        }
        for workload_id in measured_ids:
            with self.subTest(workload_id=workload_id):
                workload = next(
                    item for item in scorecard["workloads"] if item["id"] == workload_id
                )
                self.assertEqual(workload["status"], "measured")
                self.assertEqual(workload["implementation_timing"]["status"], "measured")
                self.assertGreater(workload["implementation_ns"], 0)

        manifest_summary = scorecard["manifests"]["wider-ranged-repeat-quantified-group-boundary"]
        self.assertEqual(manifest_summary["known_gap_count"], 0)
        self.assertEqual(manifest_summary["measured_workloads"], 30)
        self.assertEqual(manifest_summary["workload_count"], 30)


if __name__ == "__main__":
    unittest.main()
