from __future__ import annotations

from collections import Counter
import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

from rebar_harness.benchmarks import (
    BENCHMARK_WORKLOADS_ROOT,
    BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR,
    COMPILE_SMOKE_PROVENANCE_MANIFEST_SELECTOR,
    PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR,
    load_manifest,
    load_manifests,
    select_benchmark_manifest_path,
    select_benchmark_manifest_paths,
)


def _duplicates(counter: Counter[str]) -> list[str]:
    return sorted(item for item, count in counter.items() if count > 1)


class DefaultBenchmarkManifestInventoryContractTest(unittest.TestCase):
    def test_unknown_manifest_selector_raises_clear_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown benchmark manifest selector"):
            select_benchmark_manifest_paths("missing-selector")

    def test_single_manifest_selector_helper_rejects_multi_manifest_selectors(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "benchmark manifest selector 'published-full-suite' does not resolve to exactly one path",
        ):
            select_benchmark_manifest_path(PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR)

    def test_published_full_suite_manifest_selector_is_unique_and_supported(self) -> None:
        published_manifest_paths = select_benchmark_manifest_paths(
            PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR
        )
        self.assertEqual(len(published_manifest_paths), len(set(published_manifest_paths)))

        for path in published_manifest_paths:
            with self.subTest(path=str(path.relative_to(REPO_ROOT))):
                self.assertTrue(path.is_relative_to(BENCHMARK_WORKLOADS_ROOT))
                self.assertTrue(path.is_file())
                self.assertEqual(path.suffix, ".py")

    def test_shared_manifest_selectors_keep_expected_inventory_shapes(self) -> None:
        published_manifest_paths = select_benchmark_manifest_paths(
            PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR
        )
        native_smoke_manifest_paths = select_benchmark_manifest_paths(
            BUILT_NATIVE_SMOKE_MANIFEST_SELECTOR
        )
        compile_smoke_manifest_path = select_benchmark_manifest_path(
            COMPILE_SMOKE_PROVENANCE_MANIFEST_SELECTOR
        )

        self.assertEqual(len(published_manifest_paths), 30)
        self.assertEqual(
            [path.name for path in native_smoke_manifest_paths],
            [
                "pattern_boundary.py",
                "collection_replacement_boundary.py",
                "literal_flag_boundary.py",
            ],
        )
        self.assertTrue(set(native_smoke_manifest_paths).issubset(set(published_manifest_paths)))
        self.assertEqual(compile_smoke_manifest_path.name, "compile_smoke.py")
        self.assertTrue(compile_smoke_manifest_path.is_relative_to(BENCHMARK_WORKLOADS_ROOT))
        self.assertNotIn(compile_smoke_manifest_path, published_manifest_paths)

    def test_published_full_suite_manifest_inventory_has_unique_manifest_and_workload_ids(
        self,
    ) -> None:
        published_manifest_paths = select_benchmark_manifest_paths(
            PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR
        )
        expected_manifest_ids = [
            str(load_manifest(path)[0]["manifest_id"]) for path in published_manifest_paths
        ]
        raw_manifests, workloads = load_manifests(list(published_manifest_paths))

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
