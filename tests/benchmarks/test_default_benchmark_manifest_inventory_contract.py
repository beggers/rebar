from __future__ import annotations

from collections import Counter
import pathlib
import sys
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
WORKLOADS_ROOT = REPO_ROOT / "benchmarks" / "workloads"
PYTHON_SOURCE = REPO_ROOT / "python"
if str(PYTHON_SOURCE) not in sys.path:
    sys.path.append(str(PYTHON_SOURCE))

from rebar_harness.benchmarks import DEFAULT_MANIFEST_PATHS, load_manifest, load_manifests


def _duplicates(counter: Counter[str]) -> list[str]:
    return sorted(item for item, count in counter.items() if count > 1)


class DefaultBenchmarkManifestInventoryContractTest(unittest.TestCase):
    def test_default_manifest_paths_are_unique_and_supported(self) -> None:
        self.assertEqual(len(DEFAULT_MANIFEST_PATHS), len(set(DEFAULT_MANIFEST_PATHS)))

        for path in DEFAULT_MANIFEST_PATHS:
            with self.subTest(path=str(path.relative_to(REPO_ROOT))):
                self.assertTrue(path.is_relative_to(WORKLOADS_ROOT))
                self.assertTrue(path.is_file())
                self.assertEqual(path.suffix, ".py")

    def test_default_manifest_inventory_has_unique_manifest_and_workload_ids(
        self,
    ) -> None:
        expected_manifest_ids = [
            str(load_manifest(path)[0]["manifest_id"]) for path in DEFAULT_MANIFEST_PATHS
        ]
        raw_manifests, workloads = load_manifests(list(DEFAULT_MANIFEST_PATHS))

        self.assertEqual(
            [str(manifest["manifest_id"]) for manifest in raw_manifests],
            expected_manifest_ids,
        )

        manifest_counts = Counter(
            str(manifest["manifest_id"]) for manifest in raw_manifests
        )
        self.assertEqual(
            _duplicates(manifest_counts),
            [],
            "default benchmark manifests must keep globally unique manifest ids",
        )

        workload_counts = Counter(workload.workload_id for workload in workloads)
        self.assertEqual(
            _duplicates(workload_counts),
            [],
            "default benchmark manifests must keep globally unique workload ids",
        )

        workloads_by_manifest = Counter(workload.manifest_id for workload in workloads)
        manifest_ids = {str(manifest["manifest_id"]) for manifest in raw_manifests}
        for manifest_id in manifest_ids:
            with self.subTest(manifest_id=manifest_id):
                self.assertGreater(
                    workloads_by_manifest[manifest_id],
                    0,
                    "default benchmark manifests should contribute at least one workload",
                )

        for workload in workloads:
            with self.subTest(workload_id=workload.workload_id):
                self.assertIn(workload.manifest_id, manifest_ids)


if __name__ == "__main__":
    unittest.main()
