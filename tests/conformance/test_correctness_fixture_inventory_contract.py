from __future__ import annotations

from collections import Counter
import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

from rebar_harness.correctness import (
    CORRECTNESS_FIXTURES_ROOT,
    DEFAULT_FIXTURE_PATHS,
    PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR,
    load_fixture_manifests,
    select_correctness_fixture_paths,
)


def _duplicates(counter: Counter[str]) -> list[str]:
    return sorted(item for item, count in counter.items() if count > 1)


def _tracked_fixture_paths() -> tuple[pathlib.Path, ...]:
    return tuple(sorted(CORRECTNESS_FIXTURES_ROOT.glob("*.py"), key=lambda path: path.name))


class CorrectnessFixtureInventoryContractTest(unittest.TestCase):
    def test_unknown_fixture_selector_raises_clear_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown correctness fixture selector"):
            select_correctness_fixture_paths("missing-selector")

    def test_published_full_suite_fixture_selector_is_unique_and_supported(self) -> None:
        published_fixture_paths = select_correctness_fixture_paths(
            PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR
        )
        tracked_fixture_paths = _tracked_fixture_paths()

        self.assertEqual(DEFAULT_FIXTURE_PATHS, published_fixture_paths)
        self.assertEqual(
            set(published_fixture_paths),
            set(tracked_fixture_paths),
            "published full-suite selector should cover every tracked correctness fixture",
        )
        self.assertEqual(len(published_fixture_paths), len(set(published_fixture_paths)))

        for path in published_fixture_paths:
            with self.subTest(path=str(path.relative_to(REPO_ROOT))):
                self.assertTrue(path.is_relative_to(CORRECTNESS_FIXTURES_ROOT))
                self.assertTrue(path.is_file())
                self.assertEqual(path.suffix, ".py")

    def test_published_full_suite_fixture_inventory_has_unique_manifest_suite_and_case_ids(
        self,
    ) -> None:
        published_fixture_paths = select_correctness_fixture_paths(
            PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR
        )
        manifests, cases = load_fixture_manifests(published_fixture_paths)

        self.assertEqual(
            [manifest.path for manifest in manifests],
            list(published_fixture_paths),
        )

        manifest_id_counts = Counter(manifest.manifest_id for manifest in manifests)
        self.assertEqual(
            _duplicates(manifest_id_counts),
            [],
            "default correctness fixtures must keep globally unique manifest ids",
        )

        suite_id_counts = Counter(manifest.suite_id for manifest in manifests)
        self.assertEqual(
            _duplicates(suite_id_counts),
            [],
            "default correctness fixtures must keep globally unique suite ids",
        )

        case_id_counts = Counter(case.case_id for case in cases)
        self.assertEqual(
            _duplicates(case_id_counts),
            [],
            "default correctness fixtures must keep globally unique case ids",
        )

        cases_by_manifest = Counter(case.manifest_id for case in cases)
        manifest_ids = {manifest.manifest_id for manifest in manifests}

        for manifest_id in manifest_ids:
            with self.subTest(manifest_id=manifest_id):
                self.assertGreater(
                    cases_by_manifest[manifest_id],
                    0,
                    "default correctness fixtures should contribute at least one case",
                )

        for case in cases:
            with self.subTest(case_id=case.case_id):
                self.assertIn(case.manifest_id, manifest_ids)


if __name__ == "__main__":
    unittest.main()
