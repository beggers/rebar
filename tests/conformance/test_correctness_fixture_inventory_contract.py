from __future__ import annotations

from collections import Counter
import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
FIXTURES_ROOT = REPO_ROOT / "tests" / "conformance" / "fixtures"

from rebar_harness.correctness import DEFAULT_FIXTURE_PATHS, load_fixture_manifests
from rebar_harness.correctness import (
    PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR,
    select_correctness_fixture_paths,
)


def _duplicates(counter: Counter[str]) -> list[str]:
    return sorted(item for item, count in counter.items() if count > 1)


class DefaultCorrectnessFixtureInventoryContractTest(unittest.TestCase):
    def test_published_full_suite_fixture_selector_is_unique_and_supported(self) -> None:
        published_fixture_paths = select_correctness_fixture_paths(
            PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR
        )

        self.assertEqual(DEFAULT_FIXTURE_PATHS, published_fixture_paths)
        self.assertEqual(len(published_fixture_paths), 104)
        self.assertEqual(len(published_fixture_paths), len(set(published_fixture_paths)))

        for path in published_fixture_paths:
            with self.subTest(path=str(path.relative_to(REPO_ROOT))):
                self.assertTrue(path.is_relative_to(FIXTURES_ROOT))
                self.assertTrue(path.is_file())
                self.assertEqual(path.suffix, ".py")

    def test_default_fixture_inventory_has_unique_manifest_case_and_suite_ids(self) -> None:
        published_fixture_paths = select_correctness_fixture_paths(
            PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR
        )
        manifests, cases = load_fixture_manifests(published_fixture_paths)

        self.assertEqual(
            [manifest.path for manifest in manifests],
            list(published_fixture_paths),
        )

        manifest_counts = Counter(manifest.manifest_id for manifest in manifests)
        self.assertEqual(
            _duplicates(manifest_counts),
            [],
            "default correctness manifests must keep globally unique manifest ids",
        )

        suite_counts = Counter(manifest.suite_id for manifest in manifests)
        self.assertEqual(
            _duplicates(suite_counts),
            [],
            "default correctness manifests must keep globally unique suite ids",
        )

        case_counts = Counter(case.case_id for case in cases)
        self.assertEqual(
            _duplicates(case_counts),
            [],
            "default correctness manifests must keep globally unique case ids",
        )

        cases_by_manifest = Counter(case.manifest_id for case in cases)
        manifest_ids = {manifest.manifest_id for manifest in manifests}
        for manifest in manifests:
            with self.subTest(manifest_id=manifest.manifest_id):
                self.assertGreater(
                    cases_by_manifest[manifest.manifest_id],
                    0,
                    "default correctness manifests should contribute at least one case",
                )

        for case in cases:
            with self.subTest(case_id=case.case_id, manifest_id=case.manifest_id):
                self.assertIn(case.manifest_id, manifest_ids)


if __name__ == "__main__":
    unittest.main()
