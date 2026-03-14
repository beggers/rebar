from __future__ import annotations

from collections.abc import Callable, Iterable
import pathlib
import sys
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = REPO_ROOT / "python"
TRACKED_REPORT_PATH = REPO_ROOT / "reports" / "correctness" / "latest.py"
if str(PYTHON_SOURCE) not in sys.path:
    sys.path.append(str(PYTHON_SOURCE))

from rebar_harness.correctness import (
    CpythonReAdapter,
    RebarAdapter,
    evaluate_case,
    load_scorecard,
    write_scorecard,
)
from tests.conformance.correctness_expectations import (
    CorrectnessScorecardExpectation,
    build_rebar_extension,
    run_correctness_scorecard,
)
from tests.report_assertions import (
    assert_correctness_case_record_matches,
    assert_correctness_fixture_contract,
    assert_correctness_layer_contract,
    assert_correctness_report_contract,
    assert_correctness_suites_present,
    assert_correctness_suite_case_accounting,
    assert_correctness_suite_contract,
    find_correctness_case_record,
)


def load_published_correctness_scorecard() -> dict[str, object]:
    return load_scorecard(TRACKED_REPORT_PATH)


def write_published_correctness_scorecard(scorecard: dict[str, object]) -> None:
    write_scorecard(scorecard, TRACKED_REPORT_PATH)


def assert_correctness_scorecard_suite(
    testcase: unittest.TestCase,
    *,
    target_manifest_ids: Iterable[str],
    case_factory: Callable[[str], CorrectnessScorecardExpectation],
) -> None:
    build_rebar_extension()
    cpython_adapter = CpythonReAdapter()
    rebar_adapter = RebarAdapter()

    for target_manifest_id in target_manifest_ids:
        with testcase.subTest(manifest_id=target_manifest_id):
            case = case_factory(target_manifest_id)
            summary, scorecard = run_correctness_scorecard(case.fixture_paths)

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
            assert_correctness_layer_contract(
                testcase,
                scorecard,
                case.target_layer_id,
                expected_manifest_ids=case.target_layer_manifest_ids,
                expected_operations=case.target_layer_operations,
                expected_text_models=case.target_layer_text_models,
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
