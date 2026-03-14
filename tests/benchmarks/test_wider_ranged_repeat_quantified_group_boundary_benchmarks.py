from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
MANIFEST_ID = "wider-ranged-repeat-quantified-group-boundary"
TARGET_NESTED_BROADER_RANGE_PATTERNS = (
    "a((bc|de){1,4})d",
    "a(?P<outer>(bc|de){1,4})d",
)
TARGET_NESTED_BROADER_RANGE_CONDITIONAL_PATTERNS = (
    "a(((bc|de){1,4})d)?(?(1)e|f)",
    "a(?P<outer>((bc|de){1,4})d)?(?(outer)e|f)",
)
TARGET_NESTED_BROADER_RANGE_BACKTRACKING_HEAVY_PATTERNS = (
    "a(((bc|b)c){1,4})d",
    "a(?P<outer>((bc|b)c){1,4})d",
)

if str(PYTHON_SOURCE) not in sys.path:
    sys.path.append(str(PYTHON_SOURCE))

from rebar_harness.benchmarks import DEFAULT_MANIFEST_PATHS, load_manifest


def _manifest_path() -> pathlib.Path:
    for manifest_path in DEFAULT_MANIFEST_PATHS:
        manifest_document, _ = load_manifest(manifest_path)
        if manifest_document["manifest_id"] == MANIFEST_ID:
            return manifest_path
    raise AssertionError(f"benchmark manifest {MANIFEST_ID!r} not found in default path list")


MANIFEST_PATH = _manifest_path()


class WiderRangedRepeatQuantifiedGroupBoundaryBenchmarkSuiteTest(unittest.TestCase):
    maxDiff = None

    def _run_scorecard(self) -> dict[str, object]:
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
            return json.loads(report_path.read_text(encoding="utf-8"))

    def test_broader_range_conditional_and_backtracking_rows_are_measured(self) -> None:
        manifest_document, _ = load_manifest(MANIFEST_PATH)
        scorecard = self._run_scorecard()

        measured_ids = {
            "module-compile-numbered-wider-ranged-repeat-group-broader-range-cold-str",
            "module-search-numbered-wider-ranged-repeat-group-broader-range-cold-gap",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-third-repetition-mixed-purged-str",
            "module-compile-named-wider-ranged-repeat-group-broader-range-warm-str",
            "module-search-named-wider-ranged-repeat-group-broader-range-upper-bound-all-de-warm-str",
            "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-upper-bound-mixed-purged-str",
            "module-compile-numbered-wider-ranged-repeat-group-broader-range-conditional-cold-str",
            "module-search-numbered-wider-ranged-repeat-group-broader-range-conditional-absent-warm-str",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-conditional-lower-bound-bc-purged-str",
            "module-compile-named-wider-ranged-repeat-group-broader-range-conditional-warm-str",
            "module-search-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-warm-str",
            "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-purged-str",
            "module-compile-numbered-wider-ranged-repeat-group-open-ended-cold-str",
            "module-search-numbered-wider-ranged-repeat-group-open-ended-lower-bound-bc-warm-str",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-open-ended-purged-gap",
            "module-compile-named-wider-ranged-repeat-group-open-ended-warm-str",
            "module-search-named-wider-ranged-repeat-group-open-ended-lower-bound-de-warm-str",
            "pattern-fullmatch-named-wider-ranged-repeat-group-open-ended-fourth-repetition-de-purged-str",
            "module-compile-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-cold-str",
            "module-search-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-str",
            "pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-second-repetition-b-then-bc-purged-str",
            "module-compile-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-warm-str",
            "module-search-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-lower-bound-bc-branch-warm-str",
            "pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-fourth-repetition-mixed-purged-str",
        }
        for workload_id in measured_ids:
            with self.subTest(workload_id=workload_id):
                workload = next(
                    item for item in scorecard["workloads"] if item["id"] == workload_id
                )
                self.assertEqual(workload["status"], "measured")
                self.assertEqual(workload["implementation_timing"]["status"], "measured")
                self.assertGreater(workload["implementation_ns"], 0)

        manifest_summary = scorecard["manifests"][MANIFEST_ID]
        self.assertEqual(manifest_summary["known_gap_count"], 0)
        self.assertEqual(
            manifest_summary["measured_workloads"],
            len(manifest_document["workloads"]),
        )
        self.assertEqual(
            manifest_summary["workload_count"],
            len(manifest_document["workloads"]),
        )

    def test_nested_broader_range_grouped_alternation_rows_are_present_and_measured(
        self,
    ) -> None:
        manifest_document, _ = load_manifest(MANIFEST_PATH)
        nested_manifest_rows = [
            workload
            for workload in manifest_document["workloads"]
            if workload.get("pattern") in TARGET_NESTED_BROADER_RANGE_PATTERNS
        ]

        self.assertGreaterEqual(
            len(nested_manifest_rows),
            6,
            "expected benchmark rows for the nested broader {1,4} grouped-alternation slice",
        )

        for pattern in TARGET_NESTED_BROADER_RANGE_PATTERNS:
            pattern_rows = [
                workload
                for workload in nested_manifest_rows
                if workload["pattern"] == pattern
            ]
            self.assertGreaterEqual(
                len(pattern_rows),
                3,
                f"expected compile/search/fullmatch coverage for {pattern!r}",
            )
            self.assertEqual(
                {workload["operation"] for workload in pattern_rows},
                {"module.compile", "module.search", "pattern.fullmatch"},
            )
            for workload in pattern_rows:
                with self.subTest(pattern=pattern, workload_id=workload["id"]):
                    self.assertIn("nested-group", workload["categories"])
                    self.assertIn("alternation", workload["categories"])
                    self.assertIn("ranged-repeat", workload["categories"])
                    self.assertIn("broader-range", workload["categories"])
                    self.assertIn("counted-repeat", workload["categories"])

        search_haystacks = [
            str(workload["haystack"])
            for workload in nested_manifest_rows
            if workload["operation"] == "module.search"
        ]
        for snippet in ("abcd", "aded"):
            self.assertTrue(
                any(snippet in haystack for haystack in search_haystacks),
                f"expected a module.search workload covering {snippet!r}",
            )

        pattern_haystacks = {
            str(workload["haystack"])
            for workload in nested_manifest_rows
            if workload["operation"] == "pattern.fullmatch"
        }
        self.assertIn("abcbcded", pattern_haystacks)
        self.assertIn("adedededed", pattern_haystacks)

        scorecard = self._run_scorecard()
        nested_scorecard_rows = [
            workload
            for workload in scorecard["workloads"]
            if workload["pattern"] in TARGET_NESTED_BROADER_RANGE_PATTERNS
        ]
        self.assertEqual(
            {workload["id"] for workload in nested_scorecard_rows},
            {workload["id"] for workload in nested_manifest_rows},
        )
        for workload in nested_scorecard_rows:
            with self.subTest(workload_id=workload["id"]):
                self.assertEqual(workload["status"], "measured")
                self.assertEqual(workload["implementation_timing"]["status"], "measured")
                self.assertGreater(workload["implementation_ns"], 0)

    def test_nested_broader_range_grouped_conditional_rows_are_present_and_measured(
        self,
    ) -> None:
        manifest_document, _ = load_manifest(MANIFEST_PATH)
        nested_manifest_rows = [
            workload
            for workload in manifest_document["workloads"]
            if workload.get("pattern") in TARGET_NESTED_BROADER_RANGE_CONDITIONAL_PATTERNS
        ]

        self.assertGreaterEqual(
            len(nested_manifest_rows),
            7,
            "expected benchmark rows for the nested broader {1,4} grouped-conditional slice",
        )

        for pattern in TARGET_NESTED_BROADER_RANGE_CONDITIONAL_PATTERNS:
            pattern_rows = [
                workload
                for workload in nested_manifest_rows
                if workload["pattern"] == pattern
            ]
            self.assertGreaterEqual(
                len(pattern_rows),
                3,
                f"expected compile/search/fullmatch coverage for {pattern!r}",
            )
            self.assertTrue(
                {"module.compile", "module.search", "pattern.fullmatch"}.issubset(
                    {workload["operation"] for workload in pattern_rows}
                )
            )
            for workload in pattern_rows:
                with self.subTest(pattern=pattern, workload_id=workload["id"]):
                    self.assertIn("nested-group", workload["categories"])
                    self.assertIn("alternation", workload["categories"])
                    self.assertIn("conditional", workload["categories"])
                    self.assertIn("optional-group", workload["categories"])
                    self.assertIn("ranged-repeat", workload["categories"])
                    self.assertIn("broader-range", workload["categories"])
                    self.assertIn("counted-repeat", workload["categories"])

        search_haystacks = {
            str(workload["haystack"])
            for workload in nested_manifest_rows
            if workload["operation"] == "module.search"
        }
        self.assertIn("zzafzz", search_haystacks)
        self.assertIn("zzabcdezz", search_haystacks)
        self.assertIn("zzadedezz", search_haystacks)

        pattern_haystacks = {
            str(workload["haystack"])
            for workload in nested_manifest_rows
            if workload["operation"] == "pattern.fullmatch"
        }
        self.assertIn("abcbcdede", pattern_haystacks)
        self.assertIn("adedededede", pattern_haystacks)

        scorecard = self._run_scorecard()
        nested_scorecard_rows = [
            workload
            for workload in scorecard["workloads"]
            if workload["pattern"] in TARGET_NESTED_BROADER_RANGE_CONDITIONAL_PATTERNS
        ]
        self.assertEqual(
            {workload["id"] for workload in nested_scorecard_rows},
            {workload["id"] for workload in nested_manifest_rows},
        )
        for workload in nested_scorecard_rows:
            with self.subTest(workload_id=workload["id"]):
                self.assertEqual(workload["status"], "measured")
                self.assertEqual(workload["implementation_timing"]["status"], "measured")
                self.assertGreater(workload["implementation_ns"], 0)

    def test_nested_broader_range_grouped_backtracking_heavy_rows_are_present_and_measured(
        self,
    ) -> None:
        manifest_document, _ = load_manifest(MANIFEST_PATH)
        nested_manifest_rows = [
            workload
            for workload in manifest_document["workloads"]
            if workload.get("pattern")
            in TARGET_NESTED_BROADER_RANGE_BACKTRACKING_HEAVY_PATTERNS
        ]

        self.assertGreaterEqual(
            len(nested_manifest_rows),
            7,
            "expected benchmark rows for the nested broader {1,4} grouped backtracking-heavy slice",
        )

        for pattern in TARGET_NESTED_BROADER_RANGE_BACKTRACKING_HEAVY_PATTERNS:
            pattern_rows = [
                workload
                for workload in nested_manifest_rows
                if workload["pattern"] == pattern
            ]
            self.assertGreaterEqual(
                len(pattern_rows),
                3,
                f"expected compile/search/fullmatch coverage for {pattern!r}",
            )
            self.assertTrue(
                {"module.compile", "module.search", "pattern.fullmatch"}.issubset(
                    {workload["operation"] for workload in pattern_rows}
                )
            )
            for workload in pattern_rows:
                with self.subTest(pattern=pattern, workload_id=workload["id"]):
                    self.assertIn("grouped", workload["categories"])
                    self.assertIn("nested-group", workload["categories"])
                    self.assertIn("alternation", workload["categories"])
                    self.assertIn("backtracking-heavy", workload["categories"])
                    self.assertIn("ranged-repeat", workload["categories"])
                    self.assertIn("broader-range", workload["categories"])
                    self.assertIn("counted-repeat", workload["categories"])

        search_haystacks = {
            str(workload["haystack"])
            for workload in nested_manifest_rows
            if workload["operation"] == "module.search"
        }
        self.assertIn("zzabcdzz", search_haystacks)
        self.assertIn("zzabccdzz", search_haystacks)

        pattern_haystacks = {
            str(workload["haystack"])
            for workload in nested_manifest_rows
            if workload["operation"] == "pattern.fullmatch"
        }
        self.assertIn("abcbccd", pattern_haystacks)
        self.assertIn("abccbcd", pattern_haystacks)
        self.assertIn("abcbccbccbcd", pattern_haystacks)

        scorecard = self._run_scorecard()
        nested_scorecard_rows = [
            workload
            for workload in scorecard["workloads"]
            if workload["pattern"]
            in TARGET_NESTED_BROADER_RANGE_BACKTRACKING_HEAVY_PATTERNS
        ]
        self.assertEqual(
            {workload["id"] for workload in nested_scorecard_rows},
            {workload["id"] for workload in nested_manifest_rows},
        )
        for workload in nested_scorecard_rows:
            with self.subTest(workload_id=workload["id"]):
                self.assertEqual(workload["status"], "measured")
                self.assertEqual(workload["implementation_timing"]["status"], "measured")
                self.assertGreater(workload["implementation_ns"], 0)


if __name__ == "__main__":
    unittest.main()
