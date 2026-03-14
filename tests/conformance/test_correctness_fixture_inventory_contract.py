from __future__ import annotations

from collections import Counter
import pathlib
import sys
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
FIXTURES_ROOT = REPO_ROOT / "tests" / "conformance" / "fixtures"
PYTHON_SOURCE = REPO_ROOT / "python"
if str(PYTHON_SOURCE) not in sys.path:
    sys.path.append(str(PYTHON_SOURCE))

from rebar_harness.correctness import DEFAULT_FIXTURE_PATHS, load_fixture_manifests


def _duplicates(counter: Counter[str]) -> list[str]:
    return sorted(item for item, count in counter.items() if count > 1)


class DefaultCorrectnessFixtureInventoryContractTest(unittest.TestCase):
    def test_default_fixture_paths_are_unique_and_supported(self) -> None:
        self.assertEqual(len(DEFAULT_FIXTURE_PATHS), len(set(DEFAULT_FIXTURE_PATHS)))

        for path in DEFAULT_FIXTURE_PATHS:
            with self.subTest(path=str(path.relative_to(REPO_ROOT))):
                self.assertTrue(path.is_relative_to(FIXTURES_ROOT))
                self.assertTrue(path.is_file())
                self.assertEqual(path.suffix, ".py")

    def test_default_fixture_inventory_has_unique_manifest_and_case_ids(self) -> None:
        manifests, cases = load_fixture_manifests(DEFAULT_FIXTURE_PATHS)

        self.assertEqual(
            [manifest.path for manifest in manifests],
            list(DEFAULT_FIXTURE_PATHS),
        )

        manifest_counts = Counter(manifest.manifest_id for manifest in manifests)
        self.assertEqual(
            _duplicates(manifest_counts),
            [],
            "default correctness manifests must keep globally unique manifest ids",
        )

        case_counts = Counter(case.case_id for case in cases)
        self.assertEqual(
            _duplicates(case_counts),
            [],
            "default correctness manifests must keep globally unique case ids",
        )

        manifest_ids = {manifest.manifest_id for manifest in manifests}
        for case in cases:
            with self.subTest(case_id=case.case_id):
                self.assertIn(case.manifest_id, manifest_ids)


if __name__ == "__main__":
    unittest.main()
