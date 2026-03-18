from __future__ import annotations

from collections.abc import Callable, Iterable
from functools import lru_cache, partial
import pathlib
import subprocess
import unittest

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
