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
PARSER_FIXTURES_PATH = REPO_ROOT / "tests" / "conformance" / "fixtures" / "parser_matrix.json"
PUBLIC_API_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "public_api_surface.json"
)
MATCH_BEHAVIOR_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "match_behavior_smoke.json"
)
EXPORTED_SYMBOL_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "exported_symbol_surface.json"
)
PATTERN_OBJECT_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "pattern_object_surface.json"
)
MODULE_WORKFLOW_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "module_workflow_surface.json"
)
COLLECTION_REPLACEMENT_FIXTURES_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "collection_replacement_workflows.json"
)
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.json"


class CorrectnessHarnessCollectionReplacementWorkflowTest(unittest.TestCase):
    def test_runner_regenerates_combined_collection_replacement_scorecard(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = pathlib.Path(temp_dir) / "correctness.json"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "rebar_harness.correctness",
                    "--fixtures",
                    str(PARSER_FIXTURES_PATH),
                    str(PUBLIC_API_FIXTURES_PATH),
                    str(MATCH_BEHAVIOR_FIXTURES_PATH),
                    str(EXPORTED_SYMBOL_FIXTURES_PATH),
                    str(PATTERN_OBJECT_FIXTURES_PATH),
                    str(MODULE_WORKFLOW_FIXTURES_PATH),
                    str(COLLECTION_REPLACEMENT_FIXTURES_PATH),
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
                    "executed_cases": 69,
                    "failed_cases": 0,
                    "passed_cases": 52,
                    "skipped_cases": 0,
                    "total_cases": 69,
                    "unimplemented_cases": 17,
                },
            )

            scorecard = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(scorecard["schema_version"], "1.0")
        self.assertEqual(scorecard["phase"], "phase3-module-workflow-pack")
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
        self.assertEqual(scorecard["fixtures"]["manifest_count"], 7)
        self.assertEqual(
            scorecard["fixtures"]["manifest_ids"],
            [
                "parser-matrix",
                "public-api-surface",
                "match-behavior-smoke",
                "exported-symbol-surface",
                "pattern-object-surface",
                "module-workflow-surface",
                "collection-replacement-workflows",
            ],
        )
        self.assertEqual(len(scorecard["cases"]), 69)
        self.assertTrue(TRACKED_REPORT_PATH.is_file())

        workflow_layer = scorecard["layers"]["module_workflow"]
        self.assertEqual(workflow_layer["summary"]["total_cases"], 25)
        self.assertEqual(workflow_layer["summary"]["passed_cases"], 21)
        self.assertEqual(workflow_layer["summary"]["failed_cases"], 0)
        self.assertEqual(workflow_layer["summary"]["unimplemented_cases"], 4)
        self.assertEqual(
            workflow_layer["operations"],
            ["cache_workflow", "compile", "module_call", "pattern_call", "purge_workflow"],
        )
        self.assertEqual(workflow_layer["text_models"], ["bytes", "str"])
        self.assertEqual(
            workflow_layer["manifest_ids"],
            ["collection-replacement-workflows", "module-workflow-surface"],
        )

        suite_ids = [suite["id"] for suite in scorecard["suites"]]
        self.assertIn("collection.replacement.workflow", suite_ids)
        self.assertIn("collection.replacement.workflow.bytes", suite_ids)
        self.assertIn("collection.replacement.workflow.str", suite_ids)
        self.assertIn("collection.replacement.workflow.module_call", suite_ids)
        self.assertIn("collection.replacement.workflow.pattern_call", suite_ids)

        collection_suite = next(
            suite
            for suite in scorecard["suites"]
            if suite["id"] == "collection.replacement.workflow"
        )
        self.assertEqual(collection_suite["summary"]["total_cases"], 15)
        self.assertEqual(collection_suite["summary"]["passed_cases"], 11)
        self.assertEqual(collection_suite["summary"]["unimplemented_cases"], 4)
        self.assertEqual(
            collection_suite["families"],
            [
                "findall_workflow",
                "finditer_workflow",
                "replacement_workflow",
                "split_workflow",
                "unsupported_collection_workflow",
                "unsupported_replacement_workflow",
            ],
        )

        finditer_case = next(
            case for case in scorecard["cases"] if case["id"] == "module-finditer-str-repeated"
        )
        self.assertEqual(finditer_case["comparison"], "pass")
        self.assertEqual(finditer_case["helper"], "finditer")
        self.assertEqual(
            finditer_case["observations"]["rebar"]["result"],
            {
                "items": [
                    {
                        "endpos": 7,
                        "group0": "abc",
                        "groupdict": {},
                        "groups": [],
                        "lastgroup": None,
                        "lastindex": None,
                        "matched": True,
                        "pos": 0,
                        "span": [1, 4],
                        "string_type": "str",
                    },
                    {
                        "endpos": 7,
                        "group0": "abc",
                        "groupdict": {},
                        "groups": [],
                        "lastgroup": None,
                        "lastindex": None,
                        "matched": True,
                        "pos": 0,
                        "span": [4, 7],
                        "string_type": "str",
                    },
                ],
                "exhausted": True,
            },
        )
        self.assertEqual(
            finditer_case["observations"]["rebar"]["result"],
            finditer_case["observations"]["cpython"]["result"],
        )

        split_case = next(
            case for case in scorecard["cases"] if case["id"] == "pattern-split-bytes-maxsplit"
        )
        self.assertEqual(split_case["comparison"], "pass")
        self.assertEqual(split_case["helper"], "split")
        self.assertEqual(
            split_case["observations"]["rebar"]["result"],
            [
                {"encoding": "latin-1", "value": ""},
                {"encoding": "latin-1", "value": "zzabc"},
            ],
        )

        subn_case = next(case for case in scorecard["cases"] if case["id"] == "module-subn-bytes-count")
        self.assertEqual(subn_case["comparison"], "pass")
        self.assertEqual(
            subn_case["observations"]["rebar"]["result"],
            [
                {"encoding": "latin-1", "value": "xabc"},
                1,
            ],
        )

        template_case = next(case for case in scorecard["cases"] if case["id"] == "module-sub-template-str")
        self.assertEqual(template_case["comparison"], "unimplemented")
        self.assertEqual(template_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(template_case["observations"]["rebar"]["outcome"], "unimplemented")

        callable_case = next(case for case in scorecard["cases"] if case["id"] == "module-sub-callable-str")
        self.assertEqual(callable_case["comparison"], "unimplemented")
        self.assertEqual(callable_case["observations"]["cpython"]["outcome"], "success")
        self.assertEqual(callable_case["observations"]["rebar"]["outcome"], "unimplemented")
        self.assertEqual(callable_case["args"][1]["type"], "callable")
        self.assertEqual(callable_case["args"][1]["qualname"], "callable_constant")

        non_literal_case = next(
            case for case in scorecard["cases"] if case["id"] == "module-findall-nonliteral-str"
        )
        self.assertEqual(non_literal_case["comparison"], "unimplemented")
        self.assertEqual(non_literal_case["observations"]["cpython"]["result"], ["abc"])
        self.assertEqual(non_literal_case["observations"]["rebar"]["outcome"], "unimplemented")


if __name__ == "__main__":
    unittest.main()
