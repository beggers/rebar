from __future__ import annotations

from collections.abc import Callable, Iterable
from functools import lru_cache, partial
import pathlib
import re
import subprocess
import unittest
import warnings

from rebar_harness import correctness

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
TRACKED_REPORT_PATH = correctness.SCORECARD_REPORT.published_path
NUMBERED_BACKREFERENCE_FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "numbered_backreference_workflows.py"
)
NUMBERED_BACKREFERENCE_SUITE_ID = "match.numbered_backreference"
QUANTIFIED_ALTERNATION_BROADER_RANGE_FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "quantified_alternation_broader_range_workflows.py"
)
QUANTIFIED_ALTERNATION_BROADER_RANGE_SUITE_ID = (
    "match.quantified_alternation_broader_range"
)
QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / "quantified_nested_group_alternation_branch_local_backreference_workflows.py"
)
QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_SUITE_ID = (
    "match.quantified_nested_group_alternation_branch_local_backreference"
)
NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / (
        "nested_broader_range_open_ended_quantified_group_alternation_"
        "branch_local_backreference_conditional_workflows.py"
    )
)
NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_SUITE_ID = (
    "match.nested_broader_range_open_ended_quantified_group_alternation_"
    "branch_local_backreference_conditional"
)
NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CALLABLE_REPLACEMENT_FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
    / "fixtures"
    / (
        "nested_broader_range_open_ended_quantified_group_alternation_"
        "branch_local_backreference_callable_replacement_workflows.py"
    )
)
NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CALLABLE_REPLACEMENT_SUITE_ID = (
    "collection.replacement.nested_broader_range_open_ended_quantified_group_"
    "alternation_branch_local_backreference.callable"
)
TRACKED_REPORT_FRESHNESS_CASES = (
    (
        "numbered-backreference",
        NUMBERED_BACKREFERENCE_FIXTURE_PATH,
        NUMBERED_BACKREFERENCE_SUITE_ID,
    ),
    (
        "quantified-alternation-broader-range",
        QUANTIFIED_ALTERNATION_BROADER_RANGE_FIXTURE_PATH,
        QUANTIFIED_ALTERNATION_BROADER_RANGE_SUITE_ID,
    ),
    (
        "quantified-nested-group-alternation-branch-local-backreference",
        QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_FIXTURE_PATH,
        QUANTIFIED_NESTED_GROUP_ALTERNATION_BRANCH_LOCAL_BACKREFERENCE_SUITE_ID,
    ),
    (
        "nested-broader-range-open-ended-branch-local-backreference-conditional",
        NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_FIXTURE_PATH,
        NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CONDITIONAL_SUITE_ID,
    ),
    (
        "nested-broader-range-open-ended-branch-local-backreference-callable-replacement",
        NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CALLABLE_REPLACEMENT_FIXTURE_PATH,
        NESTED_BROADER_RANGE_OPEN_ENDED_BRANCH_LOCAL_BACKREFERENCE_CALLABLE_REPLACEMENT_SUITE_ID,
    ),
)

from rebar_harness.correctness import (
    CpythonReAdapter,
    RebarAdapter,
    evaluate_case,
    load_fixture_manifest,
)
from tests.conformance.correctness_expectations import (
    BRANCH_LOCAL_BACKREFERENCE_CORRECTNESS_SCORECARD_EXPECTATIONS,
    COMBINED_CORRECTNESS_MANIFEST_EXPECTATIONS,
    CONDITIONAL_ALTERNATION_CORRECTNESS_SCORECARD_EXPECTATIONS,
    CONDITIONAL_NESTED_QUANTIFIED_CORRECTNESS_SCORECARD_EXPECTATIONS,
    CONDITIONAL_REPLACEMENT_CORRECTNESS_SCORECARD_EXPECTATIONS,
    CorrectnessScorecardExpectation,
    NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_ALTERNATION_SCORECARD_EXPECTATIONS,
    OPEN_ENDED_QUANTIFIED_GROUP_SCORECARD_EXPECTATIONS,
    QUANTIFIED_ALTERNATION_CORRECTNESS_SCORECARD_EXPECTATIONS,
    WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_SCORECARD_EXPECTATIONS,
    correctness_scorecard_case,
    correctness_scorecard_target_manifest_ids,
    tracked_correctness_scorecard_suites,
)
from tests.harness_cli_test_support import run_harness_scorecard
from tests.report_assertions import (
    assert_correctness_case_record_matches,
    assert_correctness_fixture_contract,
    assert_correctness_layer_contract,
    assert_correctness_report_contract,
    assert_correctness_suite_case_accounting,
    assert_correctness_suite_contract,
    assert_correctness_suites_present,
    find_correctness_case_record,
    find_correctness_suite_record,
)

EXPECTED_SUITE_TABLES = {
    "combined": COMBINED_CORRECTNESS_MANIFEST_EXPECTATIONS,
    "branch-local-backreference": BRANCH_LOCAL_BACKREFERENCE_CORRECTNESS_SCORECARD_EXPECTATIONS,
    "conditional-replacement": CONDITIONAL_REPLACEMENT_CORRECTNESS_SCORECARD_EXPECTATIONS,
    "conditional-alternation": CONDITIONAL_ALTERNATION_CORRECTNESS_SCORECARD_EXPECTATIONS,
    "conditional-nested-quantified": CONDITIONAL_NESTED_QUANTIFIED_CORRECTNESS_SCORECARD_EXPECTATIONS,
    "quantified-alternation": QUANTIFIED_ALTERNATION_CORRECTNESS_SCORECARD_EXPECTATIONS,
    "open-ended-quantified-group": OPEN_ENDED_QUANTIFIED_GROUP_SCORECARD_EXPECTATIONS,
    "wider-ranged-repeat-quantified-group": WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_SCORECARD_EXPECTATIONS,
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation": (
        NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_ALTERNATION_SCORECARD_EXPECTATIONS
    ),
}

MIXED_TEXT_MIRROR_EXPECTATION_TABLES = {
    "open-ended-quantified-group": OPEN_ENDED_QUANTIFIED_GROUP_SCORECARD_EXPECTATIONS,
    "quantified-alternation": QUANTIFIED_ALTERNATION_CORRECTNESS_SCORECARD_EXPECTATIONS,
    "wider-ranged-repeat-quantified-group": (
        WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_SCORECARD_EXPECTATIONS
    ),
}


@lru_cache(maxsize=1)
def _build_rebar_extension() -> None:
    subprocess.run(
        ["cargo", "build", "-p", "rebar-cpython"],
        check=True,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def assert_correctness_scorecard_suite(
    testcase: unittest.TestCase,
    *,
    target_manifest_ids: Iterable[str],
    case_factory: Callable[[str], CorrectnessScorecardExpectation],
) -> None:
    target_manifest_ids = tuple(target_manifest_ids)
    _build_rebar_extension()
    cpython_adapter = CpythonReAdapter()
    rebar_adapter = RebarAdapter()

    for target_manifest_id in target_manifest_ids:
        with testcase.subTest(manifest_id=target_manifest_id):
            case = case_factory(target_manifest_id)
            summary, scorecard = run_harness_scorecard(
                "rebar_harness.correctness",
                [
                    "--fixtures",
                    *(str(path) for path in case.fixture_paths),
                ],
                report_name="correctness.json",
            )

            assert_correctness_report_contract(
                testcase,
                scorecard,
                summary,
                expected_phase=case.expected_phase,
                tracked_report_path=TRACKED_REPORT_PATH,
            )
            assert_correctness_fixture_contract(
                testcase,
                scorecard,
                expected_manifest_ids=case.expected_fixture_manifest_ids,
                expected_paths=case.expected_fixture_paths,
                expected_case_count=case.expected_fixture_case_count,
            )
            testcase.assertEqual(
                [suite["id"] for suite in scorecard["suites"]],
                list(case.expected_cumulative_suite_ids),
            )
            testcase.assertEqual(
                tuple(scorecard["layers"]),
                tuple(
                    layer_expectation.layer_id
                    for layer_expectation in case.layer_expectations
                ),
            )
            for layer_expectation in case.layer_expectations:
                assert_correctness_layer_contract(
                    testcase,
                    scorecard,
                    layer_expectation.layer_id,
                    expected_manifest_ids=layer_expectation.expected_manifest_ids,
                    expected_operations=layer_expectation.expected_operations,
                    expected_text_models=layer_expectation.expected_text_models,
                )
            workflow_suite = assert_correctness_suite_contract(
                testcase,
                scorecard,
                case.target_suite_id,
                expected_manifest_ids=(case.target_manifest_id,),
                expected_families=case.target_suite_families,
                expected_operations=case.target_suite_operations,
                expected_text_models=case.target_suite_text_models,
            )
            assert_correctness_suite_case_accounting(
                testcase,
                workflow_suite,
                expected_case_count=case.target_manifest_case_count,
            )
            assert_correctness_suites_present(
                testcase,
                scorecard,
                case.expected_suite_ids[1:],
            )

            for fixture_case in case.representative_cases:
                with testcase.subTest(
                    manifest_id=target_manifest_id,
                    case_id=fixture_case.case_id,
                ):
                    expected_case = evaluate_case(
                        fixture_case,
                        cpython_adapter,
                        rebar_adapter,
                    )
                    assert_correctness_case_record_matches(
                        testcase,
                        find_correctness_case_record(scorecard, fixture_case.case_id),
                        expected_case,
                    )


def _fixture_manifest(
    *,
    filename: str,
    manifest_id: str,
    layer: str,
    suite_id: str,
) -> correctness.FixtureManifest:
    return correctness.FixtureManifest(
        path=REPO_ROOT / "tests" / "conformance" / "fixtures" / filename,
        manifest_id=manifest_id,
        layer=layer,
        suite_id=suite_id,
        schema_version=1,
        defaults={},
        cases=[],
    )


def _observation(
    adapter: str,
    operation: str,
    outcome: str,
    *,
    warnings: list[dict[str, str]] | None = None,
    result: object = None,
    exception: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "adapter": adapter,
        "operation": operation,
        "outcome": outcome,
        "warnings": [] if warnings is None else warnings,
        "result": result,
        "exception": exception,
    }


def _case_result(
    *,
    case_id: str,
    manifest_id: str,
    suite_id: str,
    layer: str,
    family: str,
    operation: str,
    comparison: str,
    text_model: str,
    cpython_observation: dict[str, object],
    rebar_observation: dict[str, object],
) -> dict[str, object]:
    return {
        "id": case_id,
        "manifest_id": manifest_id,
        "suite_id": suite_id,
        "layer": layer,
        "family": family,
        "operation": operation,
        "notes": [],
        "categories": [],
        "comparison": comparison,
        "comparison_notes": [],
        "text_model": text_model,
        "observations": {
            "cpython": cpython_observation,
            "rebar": rebar_observation,
        },
    }


PARSER_MANIFEST = _fixture_manifest(
    filename="parser_matrix.py",
    manifest_id="parser-matrix",
    layer="parser_acceptance_and_diagnostics",
    suite_id="parser.compile",
)
WORKFLOW_MANIFEST = _fixture_manifest(
    filename="module_workflow_surface.py",
    manifest_id="module-workflow-surface",
    layer="module_workflow",
    suite_id="workflow.synthetic",
)
MANIFESTS = (PARSER_MANIFEST, WORKFLOW_MANIFEST)
CASE_RESULTS = [
    _case_result(
        case_id="parser-str-pass",
        manifest_id=PARSER_MANIFEST.manifest_id,
        suite_id=PARSER_MANIFEST.suite_id,
        layer=PARSER_MANIFEST.layer,
        family="parser_literals",
        operation="compile",
        comparison="pass",
        text_model="str",
        cpython_observation=_observation(
            "cpython.re",
            "compile",
            "success",
            result={"pattern": "abc"},
        ),
        rebar_observation=_observation(
            "rebar",
            "compile",
            "success",
            result={"pattern": "abc"},
        ),
    ),
    _case_result(
        case_id="parser-bytes-fail",
        manifest_id=PARSER_MANIFEST.manifest_id,
        suite_id=PARSER_MANIFEST.suite_id,
        layer=PARSER_MANIFEST.layer,
        family="parser_diagnostics",
        operation="compile",
        comparison="fail",
        text_model="bytes",
        cpython_observation=_observation(
            "cpython.re",
            "compile",
            "success",
            warnings=[
                {
                    "category": "FutureWarning",
                    "message": "ambiguous nested set",
                }
            ],
            result={"pattern": "a[b]"},
        ),
        rebar_observation=_observation(
            "rebar",
            "compile",
            "exception",
            warnings=[
                {
                    "category": "RuntimeWarning",
                    "message": "native bridge mismatch",
                }
            ],
            exception={"type": "error", "message": "bad range"},
        ),
    ),
    _case_result(
        case_id="workflow-bytes-unimplemented",
        manifest_id=WORKFLOW_MANIFEST.manifest_id,
        suite_id=WORKFLOW_MANIFEST.suite_id,
        layer=WORKFLOW_MANIFEST.layer,
        family="workflow_search",
        operation="module_call",
        comparison="unimplemented",
        text_model="bytes",
        cpython_observation=_observation(
            "cpython.re",
            "module_call",
            "success",
            result={"matched": True},
        ),
        rebar_observation=_observation(
            "rebar",
            "module_call",
            "unimplemented",
            warnings=[
                {
                    "category": "DeprecationWarning",
                    "message": "temporary shim",
                }
            ],
            exception={"type": "NotImplementedError", "message": "todo"},
        ),
    ),
    _case_result(
        case_id="workflow-str-pass",
        manifest_id=WORKFLOW_MANIFEST.manifest_id,
        suite_id=WORKFLOW_MANIFEST.suite_id,
        layer=WORKFLOW_MANIFEST.layer,
        family="workflow_search",
        operation="pattern_call",
        comparison="pass",
        text_model="str",
        cpython_observation=_observation(
            "cpython.re",
            "pattern_call",
            "success",
            result={"matched": False},
        ),
        rebar_observation=_observation(
            "rebar",
            "pattern_call",
            "success",
            result={"matched": False},
        ),
    ),
]


class CorrectnessBuilderContractTest(unittest.TestCase):
    maxDiff = None

    def test_normalize_match_metadata_preserves_bytes_named_capture_shape(self) -> None:
        match = re.search(rb"(?P<outer>(ab)?)(?P<inner>c)", b"zabc")

        self.assertIsNotNone(match)
        self.assertEqual(
            correctness.normalize_match_metadata(match),
            {
                "matched": True,
                "group0": {"encoding": "latin-1", "value": "abc"},
                "groups": [
                    {"encoding": "latin-1", "value": "ab"},
                    {"encoding": "latin-1", "value": "ab"},
                    {"encoding": "latin-1", "value": "c"},
                ],
                "groupdict": {
                    "inner": {"encoding": "latin-1", "value": "c"},
                    "outer": {"encoding": "latin-1", "value": "ab"},
                },
                "lastgroup": "inner",
                "lastindex": 3,
                "pos": 0,
                "endpos": 4,
                "span": [1, 4],
                "string_type": "bytes",
                "named_groups": {
                    "inner": {"encoding": "latin-1", "value": "c"},
                    "outer": {"encoding": "latin-1", "value": "ab"},
                },
                "named_group_spans": {
                    "inner": [3, 4],
                    "outer": [1, 3],
                },
                "group1": {"encoding": "latin-1", "value": "ab"},
                "span1": [1, 3],
                "group_spans": [[1, 3], [1, 3], [3, 4]],
            },
        )

    def test_normalize_match_metadata_keeps_missing_optional_named_group_details(
        self,
    ) -> None:
        match = re.fullmatch(r"(?P<word>a)?b", "b")

        self.assertIsNotNone(match)
        self.assertEqual(
            correctness.normalize_match_metadata(match),
            {
                "matched": True,
                "group0": "b",
                "groups": [None],
                "groupdict": {"word": None},
                "lastgroup": None,
                "lastindex": None,
                "pos": 0,
                "endpos": 1,
                "span": [0, 1],
                "string_type": "str",
                "named_groups": {"word": None},
                "named_group_spans": {"word": [-1, -1]},
                "group1": None,
                "span1": [-1, -1],
                "group_spans": [[-1, -1]],
            },
        )

    def test_normalize_value_exhausts_iterators_and_normalizes_nested_bytes(
        self,
    ) -> None:
        iterator = iter([b"ab", {"x": (1, b"y")}])

        self.assertEqual(
            correctness._normalize_value(iterator),
            {
                "items": [
                    {"encoding": "latin-1", "value": "ab"},
                    {"x": [1, {"encoding": "latin-1", "value": "y"}]},
                ],
                "exhausted": True,
            },
        )
        self.assertIsNone(next(iterator, None))

    def test_normalize_warning_and_exception_payloads_preserve_diagnostic_details(
        self,
    ) -> None:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            warnings.warn("alpha", RuntimeWarning)
            warnings.warn("beta", FutureWarning)

        warning_payload = correctness.normalize_warning_records(caught)
        self.assertEqual(
            warning_payload,
            [
                {"category": "RuntimeWarning", "message": "alpha"},
                {"category": "FutureWarning", "message": "beta"},
            ],
        )

        with self.assertRaises(re.error) as raised:
            re.compile("(")

        exception_payload = correctness.normalize_exception(raised.exception)
        self.assertEqual(exception_payload["type"], "error")
        self.assertIn("missing )", exception_payload["message"])
        self.assertEqual(exception_payload["pos"], 0)
        self.assertEqual(exception_payload["lineno"], 1)
        self.assertEqual(exception_payload["colno"], 1)

    def test_compare_observations_prefers_unimplemented_result(self) -> None:
        comparison, mismatch_notes = correctness.compare_observations(
            {
                "outcome": "success",
                "warnings": [],
                "result": {"status": "ok"},
                "exception": None,
            },
            {
                "outcome": "unimplemented",
                "warnings": [{"category": "RuntimeWarning", "message": "alpha"}],
                "result": None,
                "exception": {"type": "NotImplementedError", "message": "todo"},
            },
        )

        self.assertEqual(comparison, "unimplemented")
        self.assertEqual(
            mismatch_notes,
            ["rebar adapter reports support as unimplemented"],
        )

    def test_compare_observations_reports_each_payload_mismatch_in_stable_order(
        self,
    ) -> None:
        comparison, mismatch_notes = correctness.compare_observations(
            {
                "outcome": "success",
                "warnings": [],
                "result": {"status": "ok"},
                "exception": None,
            },
            {
                "outcome": "exception",
                "warnings": [{"category": "RuntimeWarning", "message": "alpha"}],
                "result": {"status": "different"},
                "exception": {"type": "TypeError", "message": "boom"},
            },
        )

        self.assertEqual(comparison, "fail")
        self.assertEqual(
            mismatch_notes,
            [
                "outcome mismatch: success != exception",
                "warning payload mismatch",
                "result payload mismatch",
                "exception payload mismatch",
            ],
        )

    def test_build_observation_summary_counts_sorted_outcomes_warnings_and_exceptions(
        self,
    ) -> None:
        observations = [
            {"outcome": "success", "warnings": [], "exception": None},
            {
                "outcome": "exception",
                "warnings": [{"category": "RuntimeWarning", "message": "alpha"}],
                "exception": {"type": "TypeError", "message": "boom"},
            },
            {
                "outcome": "exception",
                "warnings": [{"category": "FutureWarning", "message": "beta"}],
                "exception": {"type": "error", "message": "bad"},
            },
            {
                "outcome": "unimplemented",
                "warnings": [{"category": "RuntimeWarning", "message": "gamma"}],
                "exception": None,
            },
        ]

        self.assertEqual(
            correctness.build_observation_summary(observations),
            {
                "outcomes": {
                    "exception": 2,
                    "success": 1,
                    "unimplemented": 1,
                },
                "warning_case_count": 3,
                "exception_case_count": 2,
                "warning_categories": {
                    "FutureWarning": 1,
                    "RuntimeWarning": 2,
                },
                "exception_types": {
                    "TypeError": 1,
                    "error": 1,
                },
            },
        )

    def test_build_scorecard_aggregates_correctness_summaries_and_suite_fanout(
        self,
    ) -> None:
        scorecard = correctness.build_scorecard(
            manifests=MANIFESTS,
            case_results=CASE_RESULTS,
        )

        self.assertEqual(scorecard["schema_version"], correctness.REPORT_SCHEMA_VERSION)
        self.assertEqual(scorecard["suite"], "correctness")
        self.assertEqual(scorecard["phase"], "phase3-module-workflow-pack")
        self.assertEqual(scorecard["generator"], "python -m rebar_harness.correctness")
        self.assertTrue(scorecard["generated_at"].endswith("Z"))

        self.assertEqual(
            scorecard["fixtures"],
            {
                "manifest_count": 2,
                "manifest_ids": ["parser-matrix", "module-workflow-surface"],
                "paths": [
                    "tests/conformance/fixtures/parser_matrix.py",
                    "tests/conformance/fixtures/module_workflow_surface.py",
                ],
                "case_count": 4,
            },
        )
        self.assertEqual(
            scorecard["summary"],
            {
                "total_cases": 4,
                "executed_cases": 4,
                "passed_cases": 2,
                "failed_cases": 1,
                "unimplemented_cases": 1,
                "skipped_cases": 0,
            },
        )
        self.assertEqual(
            scorecard["diagnostics"],
            {
                "by_adapter": {
                    "cpython": {
                        "outcomes": {"success": 4},
                        "warning_case_count": 1,
                        "exception_case_count": 0,
                        "warning_categories": {"FutureWarning": 1},
                        "exception_types": {},
                    },
                    "rebar": {
                        "outcomes": {
                            "exception": 1,
                            "success": 2,
                            "unimplemented": 1,
                        },
                        "warning_case_count": 2,
                        "exception_case_count": 2,
                        "warning_categories": {
                            "DeprecationWarning": 1,
                            "RuntimeWarning": 1,
                        },
                        "exception_types": {
                            "NotImplementedError": 1,
                            "error": 1,
                        },
                    },
                }
            },
        )

        self.assertEqual(
            scorecard["layers"],
            {
                "module_workflow": {
                    "manifest_ids": ["module-workflow-surface"],
                    "suite_ids": ["workflow.synthetic"],
                    "case_count": 2,
                    "families": ["workflow_search"],
                    "operations": ["module_call", "pattern_call"],
                    "text_models": ["bytes", "str"],
                    "summary": {
                        "total_cases": 2,
                        "executed_cases": 2,
                        "passed_cases": 1,
                        "failed_cases": 0,
                        "unimplemented_cases": 1,
                        "skipped_cases": 0,
                    },
                    "diagnostics": {
                        "by_adapter": {
                            "cpython": {
                                "outcomes": {"success": 2},
                                "warning_case_count": 0,
                                "exception_case_count": 0,
                                "warning_categories": {},
                                "exception_types": {},
                            },
                            "rebar": {
                                "outcomes": {"success": 1, "unimplemented": 1},
                                "warning_case_count": 1,
                                "exception_case_count": 1,
                                "warning_categories": {"DeprecationWarning": 1},
                                "exception_types": {"NotImplementedError": 1},
                            },
                        }
                    },
                },
                "parser_acceptance_and_diagnostics": {
                    "manifest_ids": ["parser-matrix"],
                    "suite_ids": ["parser.compile"],
                    "case_count": 2,
                    "families": ["parser_diagnostics", "parser_literals"],
                    "operations": ["compile"],
                    "text_models": ["bytes", "str"],
                    "summary": {
                        "total_cases": 2,
                        "executed_cases": 2,
                        "passed_cases": 1,
                        "failed_cases": 1,
                        "unimplemented_cases": 0,
                        "skipped_cases": 0,
                    },
                    "diagnostics": {
                        "by_adapter": {
                            "cpython": {
                                "outcomes": {"success": 2},
                                "warning_case_count": 1,
                                "exception_case_count": 0,
                                "warning_categories": {"FutureWarning": 1},
                                "exception_types": {},
                            },
                            "rebar": {
                                "outcomes": {"exception": 1, "success": 1},
                                "warning_case_count": 1,
                                "exception_case_count": 1,
                                "warning_categories": {"RuntimeWarning": 1},
                                "exception_types": {"error": 1},
                            },
                        }
                    },
                },
            },
        )

        self.assertEqual(
            [suite["id"] for suite in scorecard["suites"]],
            [
                "parser.compile",
                "parser.compile.bytes",
                "parser.compile.str",
                "workflow.synthetic",
                "workflow.synthetic.bytes",
                "workflow.synthetic.str",
                "workflow.synthetic.module_call",
                "workflow.synthetic.pattern_call",
            ],
        )
        self.assertEqual(
            scorecard["suites"][0],
            {
                "id": "parser.compile",
                "layer": "parser_acceptance_and_diagnostics",
                "manifest_ids": ["parser-matrix"],
                "case_count": 2,
                "families": ["parser_diagnostics", "parser_literals"],
                "operations": ["compile"],
                "text_models": ["bytes", "str"],
                "summary": {
                    "total_cases": 2,
                    "executed_cases": 2,
                    "passed_cases": 1,
                    "failed_cases": 1,
                    "unimplemented_cases": 0,
                    "skipped_cases": 0,
                },
                "diagnostics": scorecard["layers"][
                    "parser_acceptance_and_diagnostics"
                ]["diagnostics"],
            },
        )
        self.assertEqual(
            scorecard["suites"][-1],
            {
                "id": "workflow.synthetic.pattern_call",
                "layer": "module_workflow",
                "manifest_ids": ["module-workflow-surface"],
                "case_count": 1,
                "families": ["workflow_search"],
                "operations": ["pattern_call"],
                "text_models": ["str"],
                "summary": {
                    "total_cases": 1,
                    "executed_cases": 1,
                    "passed_cases": 1,
                    "failed_cases": 0,
                    "unimplemented_cases": 0,
                    "skipped_cases": 0,
                },
                "diagnostics": {
                    "by_adapter": {
                        "cpython": {
                            "outcomes": {"success": 1},
                            "warning_case_count": 0,
                            "exception_case_count": 0,
                            "warning_categories": {},
                            "exception_types": {},
                        },
                        "rebar": {
                            "outcomes": {"success": 1},
                            "warning_case_count": 0,
                            "exception_case_count": 0,
                            "warning_categories": {},
                            "exception_types": {},
                        },
                    }
                },
            },
        )

        self.assertEqual(
            scorecard["families"],
            [
                {
                    "id": "parser_diagnostics",
                    "case_count": 1,
                    "layers": ["parser_acceptance_and_diagnostics"],
                    "operations": ["compile"],
                    "text_models": ["bytes"],
                    "summary": {
                        "total_cases": 1,
                        "executed_cases": 1,
                        "passed_cases": 0,
                        "failed_cases": 1,
                        "unimplemented_cases": 0,
                        "skipped_cases": 0,
                    },
                },
                {
                    "id": "parser_literals",
                    "case_count": 1,
                    "layers": ["parser_acceptance_and_diagnostics"],
                    "operations": ["compile"],
                    "text_models": ["str"],
                    "summary": {
                        "total_cases": 1,
                        "executed_cases": 1,
                        "passed_cases": 1,
                        "failed_cases": 0,
                        "unimplemented_cases": 0,
                        "skipped_cases": 0,
                    },
                },
                {
                    "id": "workflow_search",
                    "case_count": 2,
                    "layers": ["module_workflow"],
                    "operations": ["module_call", "pattern_call"],
                    "text_models": ["bytes", "str"],
                    "summary": {
                        "total_cases": 2,
                        "executed_cases": 2,
                        "passed_cases": 1,
                        "failed_cases": 0,
                        "unimplemented_cases": 1,
                        "skipped_cases": 0,
                    },
                },
            ],
        )

    def test_build_fixture_summary_exposes_single_manifest_metadata_on_narrow_runs(
        self,
    ) -> None:
        summary = correctness.build_fixture_summary((WORKFLOW_MANIFEST,), CASE_RESULTS[2:])

        self.assertEqual(
            summary,
            {
                "manifest_count": 1,
                "manifest_ids": ["module-workflow-surface"],
                "paths": ["tests/conformance/fixtures/module_workflow_surface.py"],
                "case_count": 2,
                "path": "tests/conformance/fixtures/module_workflow_surface.py",
                "schema_version": 1,
                "manifest_id": "module-workflow-surface",
            },
        )


class CorrectnessScorecardSuitesTest(unittest.TestCase):
    maxDiff = None

    def _assert_tracked_report_keeps_manifest_fresh(
        self,
        fixture_path: pathlib.Path,
        suite_id: str,
    ) -> None:
        _build_rebar_extension()
        manifest_cases = load_fixture_manifest(fixture_path).cases
        _, expected_scorecard = run_harness_scorecard(
            "rebar_harness.correctness",
            [
                "--fixtures",
                str(fixture_path),
            ],
            report_name="correctness.json",
        )
        tracked_scorecard = correctness.SCORECARD_REPORT.load(TRACKED_REPORT_PATH)

        expected_suite = find_correctness_suite_record(expected_scorecard, suite_id)
        tracked_suite = find_correctness_suite_record(tracked_scorecard, suite_id)

        self.assertEqual(tracked_suite["manifest_ids"], expected_suite["manifest_ids"])
        self.assertEqual(tracked_suite["families"], expected_suite["families"])
        self.assertEqual(tracked_suite["operations"], expected_suite["operations"])
        self.assertEqual(tracked_suite["text_models"], expected_suite["text_models"])
        self.assertEqual(tracked_suite["case_count"], expected_suite["case_count"])
        self.assertEqual(tracked_suite["summary"], expected_suite["summary"])
        self.assertEqual(tracked_suite["diagnostics"], expected_suite["diagnostics"])

        for fixture_case in manifest_cases:
            with self.subTest(suite_id=suite_id, case_id=fixture_case.case_id):
                assert_correctness_case_record_matches(
                    self,
                    find_correctness_case_record(
                        tracked_scorecard, fixture_case.case_id
                    ),
                    find_correctness_case_record(expected_scorecard, fixture_case.case_id),
                )

    def test_runner_regenerates_correctness_scorecards(self) -> None:
        for suite in tracked_correctness_scorecard_suites():
            with self.subTest(suite_id=suite.suite_id):
                assert_correctness_scorecard_suite(
                    self,
                    target_manifest_ids=correctness_scorecard_target_manifest_ids(
                        suite.suite_id
                    ),
                    case_factory=partial(correctness_scorecard_case, suite.suite_id),
                )

    def test_tracked_report_keeps_sample_manifests_fresh(
        self,
    ) -> None:
        for label, fixture_path, suite_id in TRACKED_REPORT_FRESHNESS_CASES:
            with self.subTest(manifest=label):
                self._assert_tracked_report_keeps_manifest_fresh(
                    fixture_path,
                    suite_id,
                )


class CorrectnessScorecardRegistryContractTest(unittest.TestCase):
    maxDiff = None

    def _assert_mixed_text_manifests_mirror_representative_bytes_rows(
        self,
        *,
        suite_id: str,
        expectation_table: object,
    ) -> None:
        manifests_by_id = {
            manifest.manifest_id: manifest
            for manifest in correctness.published_fixture_manifests()
        }
        mixed_text_manifest_ids: list[str] = []

        for manifest_id, manifest_expectation in expectation_table.items():
            manifest = manifests_by_id[manifest_id]
            text_models = {case.text_model for case in manifest.cases}
            if text_models != {"bytes", "str"}:
                continue

            mixed_text_manifest_ids.append(manifest_id)
            with self.subTest(suite_id=suite_id, manifest_id=manifest_id):
                representative_case_ids = manifest_expectation.representative_case_ids
                representative_str_case_ids = tuple(
                    case_id
                    for case_id in representative_case_ids
                    if case_id.endswith("-str")
                )
                representative_bytes_case_ids = tuple(
                    case_id
                    for case_id in representative_case_ids
                    if case_id.endswith("-bytes")
                )

                self.assertNotEqual(representative_str_case_ids, ())
                self.assertEqual(
                    representative_bytes_case_ids,
                    tuple(
                        f"{case_id.removesuffix('-str')}-bytes"
                        for case_id in representative_str_case_ids
                    ),
                )

        self.assertNotEqual(
            mixed_text_manifest_ids,
            [],
            msg=f"{suite_id} should retain at least one mixed-text manifest",
        )

    def test_suite_registry_reuses_canonical_expectation_tables(self) -> None:
        suites_by_id = {
            suite.suite_id: suite for suite in tracked_correctness_scorecard_suites()
        }

        self.assertEqual(set(suites_by_id), set(EXPECTED_SUITE_TABLES))

        for suite_id, expectation_table in EXPECTED_SUITE_TABLES.items():
            with self.subTest(suite_id=suite_id):
                suite = suites_by_id[suite_id]
                self.assertIs(suite.expectation_table, expectation_table)
                manifest_id = next(iter(expectation_table))
                self.assertNotIsInstance(expectation_table[manifest_id], dict)

    def test_suite_registry_target_manifests_follow_default_fixture_order(self) -> None:
        manifests = correctness.published_fixture_manifests()
        suite_ids: list[str] = []

        for suite in tracked_correctness_scorecard_suites():
            with self.subTest(suite_id=suite.suite_id):
                suite_ids.append(suite.suite_id)
                expected_target_manifest_ids = tuple(
                    manifest.manifest_id
                    for manifest in manifests
                    if manifest.manifest_id in suite.expectation_table
                )
                self.assertEqual(
                    correctness_scorecard_target_manifest_ids(suite.suite_id),
                    expected_target_manifest_ids,
                )
                self.assertNotEqual(expected_target_manifest_ids, ())

        self.assertEqual(len(suite_ids), len(set(suite_ids)))

    def test_unknown_suite_id_raises_clear_error(self) -> None:
        with self.assertRaisesRegex(
            AssertionError,
            "unknown correctness scorecard suite 'missing-suite'; expected one of",
        ):
            correctness_scorecard_target_manifest_ids("missing-suite")

    def test_scorecard_case_rejects_manifests_outside_suite_expectations(self) -> None:
        target_manifest_id = correctness_scorecard_target_manifest_ids("combined")[0]
        self.assertNotIn(
            target_manifest_id,
            correctness_scorecard_target_manifest_ids("branch-local-backreference"),
        )

        with self.assertRaisesRegex(
            AssertionError,
            f"missing correctness expectation for '{target_manifest_id}'",
        ):
            correctness_scorecard_case("branch-local-backreference", target_manifest_id)

    def test_scorecard_cases_preserve_fixture_prefix_and_representative_case_order(
        self,
    ) -> None:
        manifests = correctness.published_fixture_manifests()
        fixture_manifest_ids = tuple(manifest.manifest_id for manifest in manifests)
        fixture_paths = tuple(
            str(manifest.path.relative_to(REPO_ROOT)) for manifest in manifests
        )

        for suite in tracked_correctness_scorecard_suites():
            for target_manifest_id in correctness_scorecard_target_manifest_ids(
                suite.suite_id
            ):
                with self.subTest(
                    suite_id=suite.suite_id,
                    manifest_id=target_manifest_id,
                ):
                    case = correctness_scorecard_case(suite.suite_id, target_manifest_id)
                    manifest_expectation = suite.expectation_table[target_manifest_id]
                    self.assertNotIsInstance(manifest_expectation, dict)
                    expected_representative_case_ids = (
                        manifest_expectation.representative_case_ids
                    )
                    target_index = fixture_manifest_ids.index(target_manifest_id)
                    expected_prefix_manifest_ids = fixture_manifest_ids[: target_index + 1]
                    expected_prefix_paths = fixture_paths[: target_index + 1]

                    self.assertEqual(case.target_manifest_id, target_manifest_id)
                    self.assertEqual(
                        case.expected_fixture_manifest_ids,
                        expected_prefix_manifest_ids,
                    )
                    self.assertEqual(case.expected_fixture_paths, expected_prefix_paths)
                    self.assertEqual(
                        tuple(
                            str(path.relative_to(REPO_ROOT)) for path in case.fixture_paths
                        ),
                        expected_prefix_paths,
                    )
                    self.assertEqual(
                        tuple(
                            fixture_case.case_id
                            for fixture_case in case.representative_cases
                        ),
                        expected_representative_case_ids,
                    )
                    self.assertEqual(
                        {fixture_case.manifest_id for fixture_case in case.representative_cases},
                        {target_manifest_id},
                    )

    def test_mixed_text_feature_scorecards_mirror_representative_bytes_rows(
        self,
    ) -> None:
        for suite_id, expectation_table in MIXED_TEXT_MIRROR_EXPECTATION_TABLES.items():
            self._assert_mixed_text_manifests_mirror_representative_bytes_rows(
                suite_id=suite_id,
                expectation_table=expectation_table,
            )


if __name__ == "__main__":
    unittest.main()
