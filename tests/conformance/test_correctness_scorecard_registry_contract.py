from __future__ import annotations

import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

from rebar_harness.correctness import published_fixture_manifests
from tests.conformance.correctness_expectations import (
    BRANCH_LOCAL_BACKREFERENCE_CORRECTNESS_SCORECARD_EXPECTATIONS,
    COMBINED_CORRECTNESS_MANIFEST_EXPECTATIONS,
    CONDITIONAL_ALTERNATION_CORRECTNESS_SCORECARD_EXPECTATIONS,
    CONDITIONAL_NESTED_QUANTIFIED_CORRECTNESS_SCORECARD_EXPECTATIONS,
    CONDITIONAL_REPLACEMENT_CORRECTNESS_SCORECARD_EXPECTATIONS,
    NESTED_BROADER_RANGE_WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_ALTERNATION_SCORECARD_EXPECTATIONS,
    OPEN_ENDED_QUANTIFIED_GROUP_SCORECARD_EXPECTATIONS,
    QUANTIFIED_ALTERNATION_CORRECTNESS_SCORECARD_EXPECTATIONS,
    WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_SCORECARD_EXPECTATIONS,
    correctness_scorecard_case,
    correctness_scorecard_target_manifest_ids,
    tracked_correctness_scorecard_suites,
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


class CorrectnessScorecardRegistryContractTest(unittest.TestCase):
    maxDiff = None

    def _assert_mixed_text_manifests_mirror_representative_bytes_rows(
        self,
        *,
        suite_id: str,
        expectation_table: object,
    ) -> None:
        manifests_by_id = {
            manifest.manifest_id: manifest for manifest in published_fixture_manifests()
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
        manifests = published_fixture_manifests()
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
        manifests = published_fixture_manifests()
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
                    manifest_expectation = suite.expectation_table[
                        target_manifest_id
                    ]
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
