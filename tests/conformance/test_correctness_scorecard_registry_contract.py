from __future__ import annotations

import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

from rebar_harness.correctness import DEFAULT_FIXTURE_PATHS, load_fixture_manifest
from tests.conformance.correctness_expectations import (
    correctness_scorecard_case,
    correctness_scorecard_target_manifest_ids,
    tracked_correctness_scorecard_suites,
)


def _fixture_inventory() -> tuple[tuple[pathlib.Path, str], ...]:
    inventory = []
    for path in DEFAULT_FIXTURE_PATHS:
        manifest, _ = load_fixture_manifest(path)
        inventory.append((path, manifest.manifest_id))
    return tuple(inventory)


class CorrectnessScorecardRegistryContractTest(unittest.TestCase):
    maxDiff = None

    def test_suite_registry_target_manifests_follow_default_fixture_order(self) -> None:
        inventory = _fixture_inventory()
        suite_ids: list[str] = []

        for suite in tracked_correctness_scorecard_suites():
            with self.subTest(suite_id=suite.suite_id):
                suite_ids.append(suite.suite_id)
                expected_target_manifest_ids = tuple(
                    manifest_id
                    for _, manifest_id in inventory
                    if manifest_id in suite.expectation_table
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
        inventory = _fixture_inventory()
        fixture_manifest_ids = tuple(manifest_id for _, manifest_id in inventory)
        fixture_paths = tuple(str(path.relative_to(REPO_ROOT)) for path, _ in inventory)

        for suite in tracked_correctness_scorecard_suites():
            for target_manifest_id in correctness_scorecard_target_manifest_ids(
                suite.suite_id
            ):
                with self.subTest(
                    suite_id=suite.suite_id,
                    manifest_id=target_manifest_id,
                ):
                    case = correctness_scorecard_case(suite.suite_id, target_manifest_id)
                    expected_representative_case_ids = suite.expectation_table[
                        target_manifest_id
                    ]["representative_case_ids"]
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


if __name__ == "__main__":
    unittest.main()
