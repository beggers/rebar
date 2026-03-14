from __future__ import annotations

import pathlib
import sys
import tempfile
import textwrap
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
TEMP_ROOT = REPO_ROOT / ".rebar" / "tmp"
if str(PYTHON_SOURCE) not in sys.path:
    sys.path.append(str(PYTHON_SOURCE))

from rebar_harness.correctness import (
    CpythonReAdapter,
    RebarAdapter,
    evaluate_case,
    load_fixture_manifest,
)
from tests.conformance.correctness_expectations import (
    build_rebar_extension,
    run_correctness_scorecard,
)
from tests.report_assertions import (
    assert_correctness_case_record_matches,
    assert_correctness_fixture_contract,
    assert_correctness_layer_contract,
    assert_correctness_report_contract,
    assert_correctness_suite_case_accounting,
    assert_correctness_suite_contract,
    find_correctness_case_record,
)


class CorrectnessHarnessQuantifiedNestedGroupCallableReplacementContractTest(
    unittest.TestCase
):
    maxDiff = None

    def _fixture_source(self) -> str:
        return """
        MANIFEST = {
            "schema_version": 1,
            "manifest_id": "quantified-nested-group-callable-workflow-contract",
            "layer": "module_workflow",
            "suite_id": "collection.replacement.quantified_nested_group.callable.contract",
            "defaults": {
                "text_model": "str",
            },
            "cases": [
                {
                    "id": "module-sub-callable-quantified-nested-group-numbered-lower-bound-str",
                    "operation": "module_call",
                    "family": "quantified_nested_group_numbered_outer_callable_workflow",
                    "helper": "sub",
                    "args": [
                        r"a((bc)+)d",
                        {
                            "type": "callable_match_group",
                            "group": 1,
                            "suffix": "x",
                        },
                        "zzabcdzz",
                    ],
                    "categories": ["workflow", "callable-replacement", "quantified", "nested-group", "module", "str"],
                    "notes": [
                        "Exercising the correctness CLI with a numbered quantified nested-group callable replacement fixture should preserve callable descriptors and report the same result payloads as the direct parity path."
                    ],
                },
                {
                    "id": "module-subn-callable-quantified-nested-group-numbered-first-match-only-str",
                    "operation": "module_call",
                    "family": "quantified_nested_group_numbered_inner_callable_count_workflow",
                    "helper": "subn",
                    "args": [
                        r"a((bc)+)d",
                        {
                            "type": "callable_match_group",
                            "group": 2,
                            "prefix": "<",
                            "suffix": ">",
                        },
                        "zzabcbcdabcbcdzz",
                        1,
                    ],
                    "categories": ["workflow", "callable-replacement", "quantified", "nested-group", "module", "str", "count"],
                    "notes": [
                        "The correctness runner should report counted numbered callable replacement results for the first quantified match without losing callable serialization."
                    ],
                },
                {
                    "id": "pattern-sub-callable-quantified-nested-group-named-repeated-outer-capture-str",
                    "operation": "pattern_call",
                    "family": "named_quantified_nested_group_outer_callable_workflow",
                    "pattern": r"a(?P<outer>(?P<inner>bc)+)d",
                    "helper": "sub",
                    "args": [
                        {
                            "type": "callable_match_group",
                            "group": "outer",
                            "suffix": "x",
                        },
                        "zzabcbcdzz",
                    ],
                    "categories": ["workflow", "callable-replacement", "quantified", "nested-group", "pattern", "str"],
                    "notes": [
                        "The correctness runner should preserve named quantified nested-group callable replacements when the compiled Pattern path expands the repeated outer capture."
                    ],
                },
                {
                    "id": "pattern-subn-callable-quantified-nested-group-named-constant-str",
                    "operation": "pattern_call",
                    "family": "named_quantified_nested_group_constant_callable_count_workflow",
                    "pattern": r"a(?P<outer>(?P<inner>bc)+)d",
                    "helper": "subn",
                    "args": [
                        {
                            "type": "callable_constant",
                            "value": "CONST",
                        },
                        "zzabcbcdabcbcdzz",
                        1,
                    ],
                    "categories": ["workflow", "callable-replacement", "quantified", "nested-group", "pattern", "str", "count"],
                    "notes": [
                        "Constant callable replacements should survive the correctness scorecard path with the same reported callable metadata as the loader contract."
                    ],
                },
            ],
        }
        """

    def _write_fixture(
        self,
        directory: pathlib.Path,
        filename: str,
        source: str,
    ) -> pathlib.Path:
        path = directory / filename
        path.write_text(textwrap.dedent(source), encoding="utf-8")
        return path

    def _run_scorecard(self):
        TEMP_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as temp_dir:
            fixture_path = self._write_fixture(
                pathlib.Path(temp_dir),
                "quantified_nested_group_callable_workflow_contract.py",
                self._fixture_source(),
            )
            relative_fixture_path = str(fixture_path.relative_to(REPO_ROOT))
            fixture_manifest, fixture_cases = load_fixture_manifest(fixture_path)

            build_rebar_extension()
            summary, scorecard = run_correctness_scorecard((fixture_path,))

        return fixture_manifest, fixture_cases, relative_fixture_path, summary, scorecard

    def test_runner_preserves_callable_metadata_for_python_backed_workflows(self) -> None:
        fixture_manifest, fixture_cases, relative_fixture_path, summary, scorecard = (
            self._run_scorecard()
        )
        assert_correctness_report_contract(
            self,
            scorecard,
            summary,
            expected_phase="phase3-module-workflow-pack",
        )
        self.assertEqual(summary["total_cases"], len(fixture_cases))
        assert_correctness_fixture_contract(
            self,
            scorecard,
            expected_manifest_ids=(fixture_manifest.manifest_id,),
            expected_paths=(relative_fixture_path,),
            expected_case_count=len(fixture_cases),
        )
        assert_correctness_layer_contract(
            self,
            scorecard,
            "module_workflow",
            expected_manifest_ids=(fixture_manifest.manifest_id,),
            expected_operations=tuple(sorted({case.operation for case in fixture_cases})),
            expected_text_models=tuple(sorted({case.text_model for case in fixture_cases})),
        )
        suite = assert_correctness_suite_contract(
            self,
            scorecard,
            fixture_manifest.suite_id,
            expected_manifest_ids=(fixture_manifest.manifest_id,),
            expected_families=tuple(sorted({case.family for case in fixture_cases})),
            expected_operations=tuple(sorted({case.operation for case in fixture_cases})),
            expected_text_models=tuple(sorted({case.text_model for case in fixture_cases})),
        )
        assert_correctness_suite_case_accounting(
            self,
            suite,
            expected_case_count=len(fixture_cases),
        )

        numbered_case_record = find_correctness_case_record(
            scorecard,
            "module-sub-callable-quantified-nested-group-numbered-lower-bound-str",
        )
        self.assertEqual(
            numbered_case_record["args"],
            [
                r"a((bc)+)d",
                {
                    "type": "callable",
                    "module": "rebar_harness.correctness",
                    "qualname": "callable_match_group",
                },
                "zzabcdzz",
            ],
        )
        constant_case_record = find_correctness_case_record(
            scorecard,
            "pattern-subn-callable-quantified-nested-group-named-constant-str",
        )
        self.assertEqual(
            constant_case_record["args"],
            [
                {
                    "type": "callable",
                    "module": "rebar_harness.correctness",
                    "qualname": "callable_constant",
                },
                "zzabcbcdabcbcdzz",
                1,
            ],
        )

        cpython_adapter = CpythonReAdapter()
        rebar_adapter = RebarAdapter()
        for fixture_case in fixture_cases:
            with self.subTest(case_id=fixture_case.case_id):
                expected_case = evaluate_case(
                    fixture_case,
                    cpython_adapter,
                    rebar_adapter,
                )
                assert_correctness_case_record_matches(
                    self,
                    find_correctness_case_record(scorecard, fixture_case.case_id),
                    expected_case,
                )

    def test_runner_exposes_quantified_nested_group_callable_replacement_gap(self) -> None:
        _, _, _, _, scorecard = self._run_scorecard()

        expected_results = {
            "module-sub-callable-quantified-nested-group-numbered-lower-bound-str": "zzbcxzz",
            "module-subn-callable-quantified-nested-group-numbered-first-match-only-str": [
                "zz<bc>abcbcdzz",
                1,
            ],
            "pattern-sub-callable-quantified-nested-group-named-repeated-outer-capture-str": "zzbcbcxzz",
            "pattern-subn-callable-quantified-nested-group-named-constant-str": [
                "zzCONSTabcbcdzz",
                1,
            ],
        }

        for case_id, expected_result in expected_results.items():
            with self.subTest(case_id=case_id):
                case_record = find_correctness_case_record(scorecard, case_id)
                self.assertEqual(case_record["comparison"], "unimplemented")
                self.assertEqual(
                    case_record["observations"]["cpython"]["outcome"],
                    "success",
                )
                self.assertEqual(
                    case_record["observations"]["cpython"]["result"],
                    expected_result,
                )
                self.assertEqual(
                    case_record["observations"]["rebar"]["outcome"],
                    "unimplemented",
                )
                self.assertIsNone(case_record["observations"]["rebar"]["result"])
                self.assertEqual(
                    case_record["observations"]["rebar"]["exception"]["type"],
                    "NotImplementedError",
                )


if __name__ == "__main__":
    unittest.main()
