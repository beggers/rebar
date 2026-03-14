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
SYSTEMATIC_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "systematic_feature_corpus.json"
)


class SystematicFeatureCorpusTest(unittest.TestCase):
    def test_fixture_is_checked_in_as_literal_cases(self) -> None:
        raw_manifest = json.loads(SYSTEMATIC_FIXTURES_PATH.read_text(encoding="utf-8"))

        self.assertEqual(raw_manifest["manifest_id"], "systematic-feature-corpus")
        self.assertNotIn("generator", raw_manifest)
        self.assertNotIn("feature_specs", raw_manifest)
        self.assertEqual(len(raw_manifest["cases"]), 18)

    def test_runner_executes_literal_systematic_feature_corpus(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = pathlib.Path(temp_dir) / "correctness.json"
            subprocess.run(
                ["cargo", "build", "-p", "rebar-cpython"],
                check=True,
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "rebar_harness.correctness",
                    "--fixtures",
                    str(SYSTEMATIC_FIXTURES_PATH),
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
            scorecard = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(scorecard["schema_version"], "1.0")
        self.assertEqual(scorecard["phase"], "phase3-match-behavior-pack")
        self.assertEqual(scorecard["baseline"]["python_implementation"], platform.python_implementation())
        self.assertEqual(scorecard["baseline"]["python_version"], platform.python_version())
        self.assertEqual(scorecard["baseline"]["python_version_family"], "3.12.x")
        self.assertEqual(
            scorecard["baseline"]["python_build"],
            {
                "name": platform.python_build()[0],
                "date": platform.python_build()[1],
            },
        )
        self.assertEqual(scorecard["baseline"]["python_compiler"], platform.python_compiler())
        self.assertEqual(scorecard["baseline"]["platform"], platform.platform())
        self.assertEqual(scorecard["baseline"]["executable"], sys.executable)
        self.assertEqual(scorecard["baseline"]["re_module"], "re")
        self.assertEqual(scorecard["summary"], summary)

        self.assertEqual(
            summary,
            {
                "executed_cases": 18,
                "failed_cases": 0,
                "passed_cases": 18,
                "skipped_cases": 0,
                "total_cases": 18,
                "unimplemented_cases": 0,
            },
        )
        self.assertEqual(scorecard["fixtures"]["manifest_id"], "systematic-feature-corpus")
        self.assertEqual(scorecard["fixtures"]["manifest_count"], 1)
        self.assertEqual(scorecard["fixtures"]["case_count"], 18)
        self.assertEqual(scorecard["fixtures"]["schema_version"], 1)
        self.assertEqual(len(scorecard["cases"]), 18)

        match_layer = scorecard["layers"]["match_behavior"]
        self.assertEqual(
            match_layer["summary"],
            {
                "executed_cases": 18,
                "failed_cases": 0,
                "passed_cases": 18,
                "skipped_cases": 0,
                "total_cases": 18,
                "unimplemented_cases": 0,
            },
        )
        self.assertEqual(match_layer["operations"], ["compile", "module_call", "pattern_call"])
        self.assertEqual(match_layer["text_models"], ["str"])

        suite_ids = [suite["id"] for suite in scorecard["suites"]]
        self.assertIn("match.systematic_feature_corpus", suite_ids)
        self.assertIn("match.systematic_feature_corpus.str", suite_ids)
        self.assertIn("match.systematic_feature_corpus.compile", suite_ids)
        self.assertIn("match.systematic_feature_corpus.module_call", suite_ids)
        self.assertIn("match.systematic_feature_corpus.pattern_call", suite_ids)

        cases_by_id = {case["id"]: case for case in scorecard["cases"]}

        optional_compile_case = cases_by_id[
            "systematic-optional-group-numbered-compile-metadata-str"
        ]
        self.assertEqual(optional_compile_case["comparison"], "pass")
        self.assertEqual(optional_compile_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(optional_compile_case["observations"]["cpython"]["result"]["groups"], 1)
        self.assertEqual(optional_compile_case["observations"]["rebar"]["outcome"], "success")
        self.assertEqual(
            optional_compile_case["observations"]["rebar"]["result"],
            optional_compile_case["observations"]["cpython"]["result"],
        )

        optional_absent_case = cases_by_id[
            "systematic-optional-group-named-module-search-absent-str"
        ]
        self.assertEqual(optional_absent_case["comparison"], "pass")
        self.assertEqual(optional_absent_case["helper"], "search")
        self.assertEqual(optional_absent_case["observations"]["cpython"]["result"]["group0"], "ad")
        self.assertEqual(optional_absent_case["observations"]["cpython"]["result"]["groups"], [None])
        self.assertEqual(
            optional_absent_case["observations"]["cpython"]["result"]["groupdict"],
            {"word": None},
        )
        self.assertEqual(
            optional_absent_case["observations"]["rebar"]["result"],
            optional_absent_case["observations"]["cpython"]["result"],
        )

        conditional_present_case = cases_by_id[
            "systematic-conditional-group-exists-empty-else-nested-numbered-module-search-present-str"
        ]
        self.assertEqual(conditional_present_case["comparison"], "pass")
        self.assertEqual(conditional_present_case["helper"], "search")
        self.assertEqual(
            conditional_present_case["observations"]["cpython"]["result"]["group0"],
            "abcd",
        )
        self.assertEqual(
            conditional_present_case["observations"]["cpython"]["result"]["groups"],
            ["b"],
        )
        self.assertEqual(
            conditional_present_case["observations"]["rebar"]["result"],
            conditional_present_case["observations"]["cpython"]["result"],
        )

        conditional_absent_case = cases_by_id[
            "systematic-conditional-group-exists-empty-else-nested-named-pattern-fullmatch-absent-str"
        ]
        self.assertEqual(conditional_absent_case["comparison"], "pass")
        self.assertEqual(conditional_absent_case["helper"], "fullmatch")
        self.assertEqual(
            conditional_absent_case["observations"]["cpython"]["result"]["group0"],
            "ac",
        )
        self.assertEqual(
            conditional_absent_case["observations"]["cpython"]["result"]["groupdict"],
            {"word": None},
        )
        self.assertEqual(
            conditional_absent_case["observations"]["rebar"]["result"],
            conditional_absent_case["observations"]["cpython"]["result"],
        )
